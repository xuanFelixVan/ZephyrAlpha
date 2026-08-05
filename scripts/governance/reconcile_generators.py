# [BLUEPRINT] MOD-GOV_SCRIPTS | docs/02_enterprise_architecture/04_architecture_principles_decisions/panorama/generator_auto_trigger_pilot.md
# [MODULE] scripts.governance.reconcile_generators
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] docs/01_policies_and_standards/_registry/catalogs/generator_registry.yaml (只读真源); scripts.governance.d5_architecture.generators.generate_battle_map_diagram (regenerate); 全部 generate_*.py (subprocess 回退)
# [CONSUMERS] apply_battle_map.py / apply_depgraph.py / apply_dataflowgraph.py / apply_decisiongraph.py (reconcile); src/zephyr/trading/boot_hooks.py (reconcile_stale)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 只读 generator_registry.yaml；生成失败不抛异常返回 failed dict（生成是派生不阻断真源写入，§2.3）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 生成器失败→返回{"status":"failed"}不阻断调用方；注册表缺失→返回{"status":"error"}跳过
# [TESTS] tests/governance/test_reconcile_generators.py
# [A_module] module_id=MOD-GOV_SCRIPTS | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] generator_auto_trigger_pilot.md
"""
reconcile_generators.py — 生成器自动触发统一编排器

职责：作为 apply_*.py（DB 真源变更实时触发）和 boot_hooks（YAML 真源变更启动时触发）
的统一入口，按 generator_registry.yaml 注册表调度对应生成器重生成。

设计（§3.1 能现成不创造·注册表驱动）：
  - 新增生成器自动化只需在 generator_registry.yaml 加一条，无需改编排器代码
  - 双路径调用：entry_function 存在→in-process importlib（快）；否则→subprocess 回退（隔离）
  - 生成失败降级返回 failed dict，不阻断真源写入（§2.3 派生关系）

双路径调用（§3.1 能现成不创造）：
  - 路径1·in-process：注册表声明 entry_function（如 battle_map 的 regenerate）→ importlib
    动态加载并调用，返回 dict。快（无进程启动开销），但生成器崩溃可能影响编排器。
  - 路径2·subprocess 回退：注册表无 entry_function → `python -m <module_path>` 子进程
    调用 main()，按退出码判定成功/失败（0/1=ok，2+=failed）。隔离（崩溃不影响编排器），
    免改造 23 个 main()-only 生成器。代价：进程启动+重新 import 开销（~2s/生成器）。

两个入口：
  - reconcile(source): apply 写完 DB 后按 trigger_source 精确匹配调用（实时）
  - reconcile_stale(): boot_hooks 启动时按 mtime 对比扫描全部生成器（YAML 变更兜底）
"""
from __future__ import annotations

__manifest__ = """
args: []
description: 生成器自动触发统一编排器——apply_*.py 写 DB 后调 reconcile(source) 实时触发，boot_hooks 启动时调 reconcile_stale() mtime 对比兜底。注册表驱动（generator_registry.yaml），双路径调用（in-process + subprocess 回退）。
dimensions:
- D5
priority: P2
timeout_seconds: 300
warn_only: false
"""

import importlib
import concurrent.futures
import logging
import os
import subprocess
import sys
import time
from pathlib import Path

_LOGGER = logging.getLogger(__name__)

# subprocess 回退超时（秒/生成器）——治理生成器最重的是 generate_domain_doc
# （批量写 20+ 域文档），实测 <60s；300s 留足余量防慢机环境误杀。
_SUBPROCESS_TIMEOUT = 300

# 并行重生成 worker 数（治本缺口#2：depgraph_db 串行 19 个 subprocess ~50s → 并行 ~13s）。
# 安全前提（已从 generator_registry.yaml 验证）：同一 trigger_source 的生成器
# output_globs 互斥（无文件写冲突）、input_sources 均为 db: 前缀（无生成器间读取依赖）。
# 可由 ZEPHYR_REGENERATE_WORKERS 环境变量覆盖（批量环境可调高，弱机可调低）。
_MAX_WORKERS = max(1, int(os.environ.get("ZEPHYR_REGENERATE_WORKERS", "4")))

# 退出码语义（_shared/constants.py）：0=PASS, 1=FINDINGS（生成成功但有告警）, 2=ERROR
# 生成器视角：0/1 均表示产物已生成（ok），2+ 表示未生成或失败。
_OK_RETURNCODES = {0, 1}

# 后台子进程 nursery——持有 Popen 引用避免 GC 触发 "subprocess still running"
# ResourceWarning（fire-and-forget spawn 后函数立即返回，Popen 对象无引用即被 GC，
# 此时子进程仍在运行→Popen.__del__ 发警告）。进程退出后由 _prune_detached() 清理，
# 列表不会无限增长（每次 reconcile_async 调用先 prune）。
_DETACHED_PROCS: list = []

# 仓库根（编排器在 scripts/governance/，parents[2]=repo root）
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# 生成器注册表真源（TRAE-062 规则数据真源=YAML，只读）
_REGISTRY_YAML = (
    _REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry"
    / "catalogs" / "generator_registry.yaml"
)

# ─────────────────────────────────────────────────────────────────────────────
# 跨进程串行锁（治本 #ARCH-REGEN-CONCURRENCY-001，2026-08-05 CPU 爆炸事故）
# ─────────────────────────────────────────────────────────────────────────────
# 病根（第一性原理）：
#   reconcile_async（--source 路径）无任何并发控制。post-commit worker 内
#   auto-commit 走 sync 路径同步递归重跑 32 reconciler，每个 apply_depgraph-
#   calling reconciler fire reconcile_async → N× 编排器并发；每个编排器又并行跑
#   19 生成器含 blueprint_panorama --all（300s 超时）。N 份并发抢同 DB + 同
#   blueprint.md → 互相拖慢全部超时 → CPU 99% 正反馈放大。
#   实测 2026-08-05 20:29-20:31：2 分钟 spawn 12 个编排器，每跑满 300s。
#
# 治本：
#   reconcile()/reconcile_stale() 入口加跨进程锁，drop-not-queue（生成器幂等，
#   在跑的那份已覆盖最新状态，丢弃不丢数据）。单全局键串行所有重生成——
#   跨 source 的生成器共享产物（panorama_registry / blueprint.md 被 depgraph_db
#   / dataflowgraph_db / decisiongraph_db 多源触发），全局串行同时消除跨源写冲突。
#
# 机制：
#   原子独占创建（O_CREAT|O_EXCL）消除 check-then-write TOCTOU（现有
#   post_commit_regen_yaml 的 TTL lockfile 用 write_text 非原子，AI 突发提交下
#   被穿透）。PID+TTL 兜底僵尸回收：持有者进程死亡或锁龄>阈值 → 抢占。
#   零依赖跨平台（scripts/ 不耦合 src/zephyr，故 _is_pid_alive 本地实现）。
#
# 二元判定（呼应规则二元化元规则）：_acquire_regen_lock → (acquired: bool, info)。
# 并发安全铁律：生成器幂等 ≠ 并发安全；重生成入口 MUST 经此锁（详见 AGENTS.md）。
# ─────────────────────────────────────────────────────────────────────────────
_LOCK_DIR = _REPO_ROOT / ".runtime" / "locks"
_REGEN_LOCK_NAME = "regenerate_global.lock"  # 单全局键：串行所有重生成（跨 source 防产物写冲突）
_REGEN_LOCK_TTL = 1800  # 僵尸兜底回收阈值（持有者崩溃未释放时，30min 后可抢占）


def _is_pid_alive_local(pid: int) -> bool:
    """跨进程 PID 存活探测（scripts/ 不耦合 zephyr，本地实现，对标 process_pool.is_pid_alive）。"""
    if pid <= 0:
        return False
    try:
        if sys.platform == "win32":
            import ctypes  # type: ignore[import-not-found]
            kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
            if not handle:
                return False
            kernel32.CloseHandle(handle)
            return True
        else:
            os.kill(pid, 0)
            return True
    except OSError:
        return False
    except Exception:  # noqa: BLE001 — 探活失败保守视为存活（避免误抢活跃锁）
        return True


def _acquire_regen_lock() -> tuple[bool, str]:
    """非阻塞尝试获取重生成全局串行锁（drop-not-queue）。

    Returns:
        (acquired, info) — acquired=True 时调用方 MUST 在 finally 中调
        _release_regen_lock()。acquired=False 表示已有重生成在跑，调用方应丢弃。
    """
    try:
        _LOCK_DIR.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass  # 目录已存在或创建失败——后者 _open 会再报
    lock_path = _LOCK_DIR / _REGEN_LOCK_NAME

    def _write_owner() -> bool:
        fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        try:
            os.write(fd, f"{os.getpid()}\n".encode("utf-8"))
        finally:
            os.close(fd)
        return True

    # 1. 原子独占创建
    try:
        _write_owner()
        return True, f"acquired pid={os.getpid()}"
    except FileExistsError:
        pass
    except OSError as e:
        _LOGGER.warning("regen lock: open 失败（降级为无锁执行）: %s", e)
        return True, f"no_lock ({e})"  # fail-open：锁不可用不阻断派生重生成

    # 2. 锁存在——判僵尸（PID 死亡 or 锁龄> TTL）→ 抢占
    holder_pid = 0
    try:
        content = lock_path.read_text(encoding="utf-8").strip()
        holder_pid = int(content.split()[0]) if content else 0
    except (OSError, ValueError):
        holder_pid = 0
    stale = False
    if holder_pid and not _is_pid_alive_local(holder_pid):
        stale = True
        reason = f"pid {holder_pid} dead"
    else:
        try:
            age = time.time() - lock_path.stat().st_mtime
            if age > _REGEN_LOCK_TTL:
                stale = True
                reason = f"age {int(age)}s > TTL {_REGEN_LOCK_TTL}s"
        except OSError:
            stale = True
            reason = "stat failed"
    if not stale:
        return False, f"held by pid={holder_pid}"
    _LOGGER.info("regen lock: 抢占僵尸锁（%s）", reason)
    try:
        lock_path.unlink()
    except OSError:
        pass
    # 3. 抢占（O_EXCL 再创；极小竞态窗口可接受——最坏双持短暂，生成器幂等不损坏数据）
    try:
        _write_owner()
        return True, f"stolen from pid={holder_pid}"
    except FileExistsError:
        return False, "race lost on steal"


def _release_regen_lock() -> None:
    """释放重生成锁（仅删除文件；O_EXCL 保证下持有者独占，删除安全）。"""
    try:
        (_LOCK_DIR / _REGEN_LOCK_NAME).unlink()
    except OSError:
        pass


def _load_registry() -> dict:
    """加载 generator_registry.yaml（只读真源）。

    Returns:
        {"generators": [{name, module_path, entry_function, trigger_sources, ...}]}
        文件缺失/解析失败返回空 dict（调用方降级跳过）。
    """
    try:
        import yaml  # type: ignore[import-untyped]
        if not _REGISTRY_YAML.exists():
            _LOGGER.warning("generator_registry.yaml 不存在: %s", _REGISTRY_YAML)
            return {"generators": []}
        data = yaml.safe_load(_REGISTRY_YAML.read_text(encoding="utf-8")) or {}
        return data if isinstance(data, dict) else {"generators": []}
    except Exception as e:  # noqa: BLE001
        _LOGGER.error("加载 generator_registry.yaml 失败: %s", e, exc_info=True)
        return {"generators": []}


def _invoke_subprocess(entry: dict) -> dict:
    """子进程调用生成器（main()-only 生成器回退路径，§3.1 能现成不创造）。

    运行 ``python <repo>/<module_path>.py``（直接执行脚本文件，非 ``-m``），按退出码
    判定成功/失败。退出码 0/1 = ok（1=FINDINGS，产物已生成但有告警），2+ = failed。

    为什么用直接脚本而非 ``python -m``：生成器用 ``from _common import ...`` 等
    同目录相对导入（如 generate_domain_index.py L35），``-m`` 不把脚本目录加入
    sys.path 导致 ModuleNotFoundError；直接执行脚本则 sys.path[0]=脚本目录，兼容。

    生成器崩溃/超时不抛异常，返回 failed dict（§2.3 派生不阻断真源）。
    """
    name = entry.get("name", "<unknown>")
    module_path = entry["module_path"]
    # module_path (dots) → 文件路径 (slashes + .py)
    script_path = _REPO_ROOT / (module_path.replace(".", "/") + ".py")
    # 可选 CLI 参数（注册表 args 字段，如 domain_doc 需 --all）
    extra_args: list[str] = list(entry.get("args", []))
    t0 = time.monotonic()
    try:
        proc = subprocess.run(  # noqa: S603 — 受控 script_path（注册表真源）
            [sys.executable, str(script_path), *extra_args],
            cwd=str(_REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=_SUBPROCESS_TIMEOUT,
        )
        elapsed = round((time.monotonic() - t0) * 1000, 1)
        if proc.returncode in _OK_RETURNCODES:
            # exit 1 可能是 EXIT_FINDINGS（正常·产物已生成）或未捕获异常（崩溃）。
            # 通过 stderr 是否含 "Traceback" 区分：有 Traceback = 崩溃 = failed。
            stderr = proc.stderr or ""
            if proc.returncode == 1 and "Traceback" in stderr:
                return {
                    "status": "failed",
                    "generator": name,
                    "error": f"crash (exit 1 + Traceback): {stderr[-400:]}",
                    "elapsed_ms": elapsed,
                }
            return {
                "status": "ok",
                "generator": name,
                "returncode": proc.returncode,
                "elapsed_ms": elapsed,
                "stdout_tail": (proc.stdout or "")[-400:],
            }
        return {
            "status": "failed",
            "generator": name,
            "error": f"exit {proc.returncode}: {(proc.stderr or '')[-400:]}",
            "elapsed_ms": elapsed,
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "failed",
            "generator": name,
            "error": f"timeout ({_SUBPROCESS_TIMEOUT}s)",
            "elapsed_ms": round((time.monotonic() - t0) * 1000, 1),
        }
    except Exception as e:  # noqa: BLE001 — 生成失败不阻断调用方
        return {
            "status": "failed",
            "generator": name,
            "error": f"{type(e).__name__}: {e}",
            "elapsed_ms": round((time.monotonic() - t0) * 1000, 1),
        }


def _invoke_generator(entry: dict) -> dict:
    """调用生成器（双路径：in-process 优先，subprocess 回退）。

    路径1·in-process：注册表声明 entry_function 且模块中存在该可调用 → importlib
    动态加载并调用（无参，返回 dict）。快，但生成器崩溃可能影响编排器内存。
    路径2·subprocess 回退：无 entry_function 或模块中不存在 → _invoke_subprocess。

    生成失败不抛异常，返回 {"status": "failed", ...}（§2.3 派生不阻断真源）。
    """
    name = entry.get("name", "<unknown>")
    entry_fn_name = entry.get("entry_function")
    t0 = time.monotonic()

    # 路径1：in-process（entry_function 存在且可调用）
    if entry_fn_name:
        try:
            module_path = entry["module_path"]
            mod = importlib.import_module(module_path)
            fn = getattr(mod, entry_fn_name, None)
            if callable(fn):
                result = fn()
                if not isinstance(result, dict):
                    result = {"status": "ok", "generator": name, "raw": result}
                result.setdefault("generator", name)
                result.setdefault("status", "ok")
                result["elapsed_ms"] = round((time.monotonic() - t0) * 1000, 1)
                result["invoke_mode"] = "in_process"
                return result
            # entry_function 声明了但模块中没有 → 落 subprocess 回退
            _LOGGER.debug(
                "entry_function '%s' not found in %s, falling back to subprocess",
                entry_fn_name, module_path,
            )
        except Exception as e:  # noqa: BLE001 — 生成失败不阻断调用方
            return {
                "status": "failed",
                "generator": name,
                "error": f"in_process: {type(e).__name__}: {e}",
                "elapsed_ms": round((time.monotonic() - t0) * 1000, 1),
            }

    # 路径2：subprocess 回退
    result = _invoke_subprocess(entry)
    result["invoke_mode"] = "subprocess"
    return result


def _invoke_parallel(entries: list[dict]) -> list[dict]:
    """并行调用多个生成器（治本缺口#2：串行 N 个 subprocess → 并行）。

    安全前提（已从 generator_registry.yaml 验证）：
      - 同一 trigger_source 的生成器 output_globs 互斥（无文件写冲突）
      - input_sources 均为 db: 前缀（无生成器间读取依赖，各读各的 DB 表）
    单个生成器失败不影响其他（_invoke_generator 内部捕获异常返回 failed dict）。
    结果顺序与 entries 一致（确定性报告，便于日志解读）。

    实测：depgraph_db 19 生成器串行 ~50s → 4 worker 并行 ~13s。
    """
    if not entries:
        return []
    results: list[dict | None] = [None] * len(entries)

    def _run(idx: int, entry: dict) -> None:
        try:
            results[idx] = _invoke_generator(entry)
        except Exception as e:  # noqa: BLE001 — _invoke_generator 已捕获，此处双保险
            name = entry.get("name", "<unknown>")
            results[idx] = {
                "status": "failed",
                "generator": name,
                "error": f"{type(e).__name__}: {e}",
            }

    with concurrent.futures.ThreadPoolExecutor(max_workers=_MAX_WORKERS) as ex:
        futures = [ex.submit(_run, i, e) for i, e in enumerate(entries)]
        for fut in concurrent.futures.as_completed(futures):
            fut.result()  # _run 内已捕获异常，此处仅确认完成
    # 防御性填充（理论不会发生）
    for i, r in enumerate(results):
        if r is None:
            results[i] = {
                "status": "failed",
                "generator": entries[i].get("name", "?"),
                "error": "no result (unknown)",
            }
    return results


def reconcile(source: str) -> dict:
    """按触发源精确匹配，并行调用对应生成器重生成（apply_*.py 写完 DB 后调用）。

    Args:
        source: 触发源标识（如 "battle_map_db"），匹配注册表 trigger_sources

    Returns:
        {"source": source, "regenerated": [result, ...], "total": N}
        并发去重命中时返回 {"source", "status":"skipped_dup", "held_by", ...}。
    """
    # #ARCH-REGEN-CONCURRENCY-001 治本：跨进程串行锁，drop-not-queue。
    acquired, info = _acquire_regen_lock()
    if not acquired:
        _LOGGER.warning("reconcile('%s'): 跳过——已有重生成在跑（%s）", source, info)
        return {
            "source": source,
            "status": "skipped_dup",
            "held_by": info,
            "regenerated": [],
            "total": 0,
        }
    try:
        registry = _load_registry()
        matched = [
            e for e in registry.get("generators", [])
            if source in e.get("trigger_sources", [])
        ]
        results = _invoke_parallel(matched)
        return {
            "source": source,
            "regenerated": results,
            "total": len(results),
        }
    finally:
        _release_regen_lock()


def _prune_detached() -> None:
    """清理已退出的后台子进程引用（避免 _DETACHED_PROCS 无限增长）。

    poll() 返回 None 表示进程仍在运行→保留；返回退出码表示已退出→移除。
    幂等，每次 reconcile_async 调用前先 prune。
    """
    global _DETACHED_PROCS
    _DETACHED_PROCS = [p for p in _DETACHED_PROCS if p.poll() is None]


def reconcile_async(source: str) -> dict:
    """异步触发重生成——spawn detached subprocess，不阻塞调用方（apply finally 块用）。

    apply_*.py 写完 DB 后调用本函数，立即返回。生成器在后台子进程中运行，
    日志写入 .runtime/logs/regenerate_<source>_<timestamp>.log 供事后查看。

    设计权衡（§3.2 事件驱动·非阻塞）：
      - 同步 reconcile(source) 会阻塞 apply 脚本（depgraph 19 生成器 ~50s，
        blueprint_panorama --all ~145s），UX 不可接受。
      - 异步 spawn 后 apply 立即返回，生成器后台跑。
      - 失败不丢失：日志文件捕获全部输出；boot_hooks 启动时 reconcile_stale()
        兜底重跑任何遗漏的生成器（生成器幂等，重复运行无副作用）。

    Returns:
        {"source": source, "pid": int, "log_file": str, "status": "spawned"}
    """
    import time as _time

    log_dir = _REPO_ROOT / ".runtime" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = _time.strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"regenerate_{source}_{timestamp}.log"

    orchestrator_script = _REPO_ROOT / "scripts" / "governance" / "reconcile_generators.py"

    creationflags = 0
    if sys.platform == "win32":
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

    try:
        log_handle = open(log_file, "w", encoding="utf-8")
        proc = subprocess.Popen(  # noqa: S603 — 受控 orchestrator_script
            [sys.executable, str(orchestrator_script), "--source", source],
            cwd=str(_REPO_ROOT),
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            creationflags=creationflags,
        )
        # 父进程关闭自己的 log_handle 副本——子进程已在 Popen 返回前 dup/继承该
        # 句柄，父进程副本若不关闭会泄漏（ResourceWarning: unclosed file）。
        log_handle.close()
        # 持有 Popen 引用避免 GC 触发 "subprocess still running" 警告；
        # _prune_detached() 在进程退出后清理本列表。
        _prune_detached()
        _DETACHED_PROCS.append(proc)
        return {
            "source": source,
            "pid": proc.pid,
            "log_file": str(log_file),
            "status": "spawned",
        }
    except Exception as e:  # noqa: BLE001
        return {
            "source": source,
            "status": "spawn_failed",
            "error": f"{type(e).__name__}: {e}",
        }


def _is_stale(entry: dict) -> tuple[bool, str]:
    """检测生成器是否需要重生成（YAML 输入比产物新 或 无产物）。

    db: 前缀的 input_sources 跳过（由 apply 实时触发，不参与 stale 扫描）。
    只对比 yaml: 前缀的文件 mtime vs output_globs 匹配文件最早 mtime。

    Returns:
        (is_stale, reason)
    """
    # 收集 yaml 输入源文件（去掉 #段名）
    yaml_files: list[Path] = []
    for src in entry.get("input_sources", []):
        if src.startswith("yaml:"):
            path_str = src.split(":", 1)[1].split("#")[0]
            f = _REPO_ROOT / path_str
            if f.exists():
                yaml_files.append(f)
    if not yaml_files:
        return False, "no_yaml_sources"  # 无 yaml 源，stale 扫描跳过

    input_mtime = max(f.stat().st_mtime for f in yaml_files)

    # 收集产物文件
    output_files: list[Path] = []
    for glob_str in entry.get("output_globs", []):
        output_files.extend(_REPO_ROOT.glob(glob_str))
    if not output_files:
        return True, "no_outputs"  # 无产物，需生成

    output_mtime = min(f.stat().st_mtime for f in output_files)
    if input_mtime > output_mtime:
        return True, "input_newer_than_output"
    return False, "output_up_to_date"


def reconcile_stale() -> dict:
    """扫描全部生成器，YAML 输入比产物新则并行重生成（boot_hooks 启动时调用）。

    两阶段：①stale 判定（mtime 对比，纯文件 stat，快，串行）→ ②stale 生成器并行重生成
    （治本缺口#2：原串行 N 个 subprocess，启动时若多生成器 stale 会阻塞 ~N×2s）。

    Returns:
        {"regenerated": [result,...], "skipped": [name,...], "total_scanned": N}
        并发去重命中时返回 {"status":"skipped_dup", "held_by", ...}。
    """
    # #ARCH-REGEN-CONCURRENCY-001 治本：跨进程串行锁，drop-not-queue。
    acquired, info = _acquire_regen_lock()
    if not acquired:
        _LOGGER.warning("reconcile_stale: 跳过——已有重生成在跑（%s）", info)
        return {
            "status": "skipped_dup",
            "held_by": info,
            "regenerated": [],
            "skipped": [],
            "total_scanned": 0,
        }
    try:
        registry = _load_registry()
        # 阶段1：stale 判定（串行，快——仅文件 mtime stat）
        stale_entries: list[tuple[dict, str]] = []  # (entry, reason)
        skipped: list[str] = []
        for entry in registry.get("generators", []):
            name = entry.get("name", "<unknown>")
            is_stale, reason = _is_stale(entry)
            if is_stale:
                stale_entries.append((entry, reason))
            else:
                skipped.append(name)
                _LOGGER.debug("reconcile_stale: %s skipped (reason=%s)", name, reason)

        # 阶段2：并行重生成 stale 生成器（慢——subprocess spawn）
        raw_results = _invoke_parallel([e for e, _ in stale_entries])
        regenerated: list[dict] = []
        for r, (entry, reason) in zip(raw_results, stale_entries):
            name = entry.get("name", "<unknown>")
            r["stale_reason"] = reason
            regenerated.append(r)
            if r.get("status") == "ok":
                _LOGGER.info("reconcile_stale: %s regenerated (reason=%s)", name, reason)
            else:
                _LOGGER.warning(
                    "reconcile_stale: %s FAILED (reason=%s): %s",
                    name, reason, r.get("error"),
                )
        return {
            "regenerated": regenerated,
            "skipped": skipped,
            "total_scanned": len(regenerated) + len(skipped),
        }
    finally:
        _release_regen_lock()


def _fmt_result(r: dict) -> str:
    """格式化单个生成器结果（兼容 in_process / subprocess 两种返回格式）。"""
    status = r.get("status", "?")
    name = r.get("generator", "?")
    mode = r.get("invoke_mode", "?")
    elapsed = r.get("elapsed_ms", "?")
    if status == "ok":
        # in_process 有 outputs 列表；subprocess 有 returncode
        if "outputs" in r:
            detail = f"{len(r['outputs'])} 文件"
        else:
            detail = f"exit {r.get('returncode', '?')}"
        return f"  ✅ {name} [{mode}]: {detail} ({elapsed}ms)"
    return f"  ❌ {name} [{mode}]: {r.get('error', '?')}"


def main() -> int:
    """CLI 入口（手动测试用，正常由 apply/boot_hooks 自动调用）."""
    import argparse
    parser = argparse.ArgumentParser(description="生成器自动触发编排器")
    parser.add_argument("--source", help="按触发源重生成（如 depgraph_db）")
    parser.add_argument("--stale", action="store_true", help="扫描 mtime 重生成过时产物")
    parser.add_argument("--list", action="store_true", help="列出注册表中的全部生成器")
    args = parser.parse_args()

    if args.list:
        registry = _load_registry()
        gens = registry.get("generators", [])
        print(f"generator_registry.yaml: {len(gens)} 生成器")
        for g in gens:
            triggers = ", ".join(g.get("trigger_sources", []))
            entry = g.get("entry_function", "(subprocess)")
            print(f"  {g.get('name', '?'):<30} triggers=[{triggers}]  entry={entry}")
        return 0

    if args.source:
        result = reconcile(args.source)
        print(f"reconcile('{args.source}'): {result['total']} 生成器")
        for r in result["regenerated"]:
            print(_fmt_result(r))
        ok = sum(1 for r in result["regenerated"] if r.get("status") == "ok")
        fail = result["total"] - ok
        if fail:
            print(f"  汇总: {ok} 成功, {fail} 失败")
        return 0 if fail == 0 else 1
    elif args.stale:
        result = reconcile_stale()
        print(f"reconcile_stale: 扫描 {result['total_scanned']} 生成器")
        for r in result["regenerated"]:
            name = r.get("generator", "?")
            reason = r.get("stale_reason", "?")
            status = r.get("status", "?")
            print(f"  🔄 {name}: {reason} → {status} ({r.get('elapsed_ms', '?')}ms)")
        for name in result["skipped"]:
            print(f"  ⏭ {name}: 已最新")
        return 0
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
