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
# [TESTS] tests/test_reconcile_generators.py (规划中)
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

import importlib
import logging
import subprocess
import sys
import time
from pathlib import Path

_LOGGER = logging.getLogger(__name__)

# subprocess 回退超时（秒/生成器）——治理生成器最重的是 generate_domain_doc
# （批量写 20+ 域文档），实测 <60s；300s 留足余量防慢机环境误杀。
_SUBPROCESS_TIMEOUT = 300

# 退出码语义（_shared/constants.py）：0=PASS, 1=FINDINGS（生成成功但有告警）, 2=ERROR
# 生成器视角：0/1 均表示产物已生成（ok），2+ 表示未生成或失败。
_OK_RETURNCODES = {0, 1}

# 仓库根（编排器在 scripts/governance/，parents[2]=repo root）
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# 生成器注册表真源（TRAE-062 规则数据真源=YAML，只读）
_REGISTRY_YAML = (
    _REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry"
    / "catalogs" / "generator_registry.yaml"
)


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


def reconcile(source: str) -> dict:
    """按触发源精确匹配，调用对应生成器重生成（apply_*.py 写完 DB 后调用）。

    Args:
        source: 触发源标识（如 "battle_map_db"），匹配注册表 trigger_sources

    Returns:
        {"source": source, "regenerated": [result, ...], "total": N}
    """
    registry = _load_registry()
    results: list[dict] = []
    for entry in registry.get("generators", []):
        if source in entry.get("trigger_sources", []):
            results.append(_invoke_generator(entry))
    return {
        "source": source,
        "regenerated": results,
        "total": len(results),
    }


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
        # 不 close log_handle——子进程继承它；Popen 会在子进程退出时自动关闭
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
    """扫描全部生成器，YAML 输入比产物新则重生成（boot_hooks 启动时调用）。

    Returns:
        {"regenerated": [result,...], "skipped": [name,...], "total_scanned": N}
    """
    registry = _load_registry()
    regenerated: list[dict] = []
    skipped: list[str] = []
    for entry in registry.get("generators", []):
        name = entry.get("name", "<unknown>")
        is_stale, reason = _is_stale(entry)
        if is_stale:
            result = _invoke_generator(entry)
            result["stale_reason"] = reason
            regenerated.append(result)
            _LOGGER.info("reconcile_stale: %s regenerated (reason=%s)", name, reason)
        else:
            skipped.append(name)
            _LOGGER.debug("reconcile_stale: %s skipped (reason=%s)", name, reason)
    return {
        "regenerated": regenerated,
        "skipped": skipped,
        "total_scanned": len(regenerated) + len(skipped),
    }


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
