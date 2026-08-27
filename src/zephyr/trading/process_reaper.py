# [BLUEPRINT] MOD-RESOURCE_OPTIMIZATION_ENGINE | docs/03_modules/_cross_layer/resource_optimization_engine/blueprint.md | §new-IDE
# [MODULE] zephyr.trading.process_reaper
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.shared.io.paths; zephyr.shared.infra.process_pool(run_subprocess_hidden); psutil(可选)
# [CONSUMERS] scripts/register_process_reaper_task.ps1; Windows Task Scheduler(ZephyrAlpha_ProcessReaper)
# [STARTUP] scheduled_task
# [MATURITY] production
# [INVARIANTS] 白名单命中永不杀; Trae后代进程永不杀; kill操作必须日志记录; dry-run零副作用; one-shot执行完即退出无常驻
# [MODIFY-GUARD] MOD-RESOURCE_OPTIMIZATION_ENGINE §new-IDE
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] psutil不可用时仅执行幽灵窗口扫描并告警; kill对已退出PID不报错; keep文件损坏时忽略该行
# [TESTS] tests/zephyr/trading/test_process_reaper.py
# [A_module] module_id=MOD-RESOURCE_OPTIMIZATION_ENGINE | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""process_reaper.py — 项目残留进程清理器（无状态 one-shot，Task Scheduler 托管）
=====================================================================

治本背景（2026-08-28 裁定）：
- 旧 ide_health_daemon「常驻守护 + AI 冷启动自觉拉起」模式违反 boot_autostart_architecture.md
  C1（永久系统全自动）/C3（Task Scheduler 唯一入口），实证失效（守护死亡后 stale PID 残留、
  AI 会话不执行冷启动协定，系统长期裸奔）。
- track_task_process 登记机制全项目零调用者（死代码）——肇事进程恰恰是最不会自觉登记的。
- zombie_scanner 写好但从未接线，且 >1h 即杀的粗暴阈值会误杀 scheduler 等永久服务。

第一性原理设计：
1. 不依赖创建者自觉清理（AI 会话会异常死亡）——由 OS（Task Scheduler）每 10 分钟触发。
2. 不做常驻进程（守护进程自身也是残留风险源，递归问题）——one-shot：scan→判定→kill→exit。
   模式先例：scripts/deadman_switch.ps1（#ARCH-BOOT-002 E）。
3. 「什么是垃圾」靠外部可观测量：父进程死活（孤儿）、年龄、资源占用、cmdline 特征。
4. 白名单优于黑名单：合法永久进程是小而稳定的可枚举集合，宁宽勿窄（fail-safe：
   本进程故障退化为「不清理」，绝不退化为「误杀」）。
5. 个案长任务（如用户指定保留的批处理）走外部 keep 文件，不污染默认白名单。

判定矩阵（按序命中即定）：
0. 自身及祖先链                    -> skip（自保）
1. 白名单 cmdline 正则命中         -> skip（永久服务）
2. 父链含 Trae CN 进程             -> skip（IDE 子进程：jedi/MCP 等，IDE 负责回收）
3. DANGEROUS：mem>10GB 或 子进程>50 -> kill（资源失控，不论年龄）
4. cmdline 含 .runtime/ 路径 + 孤儿 -> kill（临时目录脚本无长命权利，sweep_runner 族精准命中）
5. 孤儿 + age>2h                   -> kill（创建者已死且超龄）
6. 孤儿 + 30min<age<=2h            -> report（观察，下轮再判）
7. 非孤儿 + age>6h + CPU<0.5%      -> kill（长命但空转，zombie_scanner 阈值修正版）
8. 非孤儿 + age>1h + CPU<0.1%      -> report
9. 其余                            -> skip

同时兼任（从 ide_health_daemon 迁移的治理能力）：
- Trae 幽灵窗口扫描清理（复用 scan_ghost_windows/kill_ghost_windows，零修改）
- drift 指标：git stash>5 自动清理（cleanup_stash.py）、worktree 变更>50 告警记录

CLI：
    python -m zephyr.trading.process_reaper            # 执行清理（Task Scheduler 调用方式）
    python -m zephyr.trading.process_reaper --dry-run  # 只报告不杀（验证用）
    python -m zephyr.trading.process_reaper --status   # 读上次运行状态
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from zephyr.shared.io.paths import REPO_ROOT

try:
    import psutil
except ImportError:  # psutil 不可用时 python 进程扫描降级关闭，幽灵窗口扫描仍可执行
    psutil = None

logger = logging.getLogger(__name__)

# ============== 路径与文件 ==============
_STATUS_DIR = REPO_ROOT / ".runtime" / "process_reaper"
_STATUS_FILE = _STATUS_DIR / "last_run.json"
_KILL_LOG = REPO_ROOT / "data" / "runtime" / "reaper_kill.log"
# 个案保留清单：每行一个 cmdline 子串（非正则），命中即保护。
# 用途：用户/AI 指定保留的长批任务（如 run_sentiment_batch），不污染默认白名单。
_KEEP_FILE = REPO_ROOT / "data" / "runtime" / "process_reaper_keep.txt"

# ============== 阈值 ==============
_DANGEROUS_MEM_GB = 10.0
_DANGEROUS_CHILDREN = 50
_ORPHAN_KILL_AGE_S = 2 * 3600  # 孤儿超龄 2h 杀
_ORPHAN_REPORT_AGE_S = 1800  # 孤儿 30min~2h 报告
_IDLE_KILL_AGE_S = 6 * 3600  # 非孤儿长命空转：age>6h 且 CPU<0.5% 杀
_IDLE_KILL_CPU_MAX = 0.5
_IDLE_REPORT_AGE_S = 3600  # 非孤儿 age>1h 且 CPU<0.1% 报告
_IDLE_REPORT_CPU_MAX = 0.1
_KILL_CHILD_RECURSIVE = True  # kill 时级联杀子进程树（sweep 族连根拔，防残留再繁殖）

# ============== 默认白名单（永久服务 cmdline 正则，命中永不杀）==============
# 来源：boot_autostart_architecture.md 永久服务清单 + 当前生产实证常驻服务。
# 原则：宁宽勿窄；个案保留走 _KEEP_FILE，不加在这里。
_DEFAULT_WHITELIST: tuple[str, ...] = (
    r"zephyr\.data\.scheduler",  # 数据调度器（boot 永久服务）
    r"zephyr\.data\.tick_subscriber",  # tick 订阅（boot 永久服务）
    r"worktree_drift_watchdog",  # 漂移看门狗（boot 永久服务）
    r"write_audit_daemon",  # 写审计守护
    r"ch_health_probe",  # CH 健康探针（boot 永久服务）
    r"panel[.\w]*[\\/ ]+serve|panel\.exe\"? serve| serve src[\\/]zephyr[\\/]frontend",  # 前端 dashboard
    r"http\.server 8010",  # 原型预览服务
    r"process_reaper",  # 自保（含注册脚本路径）
    r"run-jedi-language-server|jedilsp",  # Trae Python 语言服务（双保险，正常也被 Trae 后代规则覆盖）
)
_TRAE_PROCESS_NAME_PREFIX = "trae cn"  # psutil name 小写前缀比较（实际为 "Trae CN.exe"）
_RUNTIME_PATH_MARKER = re.compile(r"\.runtime[\\/]", re.IGNORECASE)


@dataclass
class ProcVerdict:
    """单个进程的判定结果。"""

    pid: int
    action: str  # "kill" | "report" | "skip"
    reason: str
    cmdline: str = ""
    age_s: float = 0.0
    mem_mb: float = 0.0
    cpu_pct: float = 0.0
    children: int = 0
    orphan: bool = False
    killed: bool = False


@dataclass
class ReapReport:
    """一轮清理的报告。"""

    timestamp: str = ""
    dry_run: bool = False
    scanned: int = 0
    whitelist_hits: int = 0
    trae_descendant_hits: int = 0
    killed: list[dict[str, Any]] = field(default_factory=list)
    reported: list[dict[str, Any]] = field(default_factory=list)
    ghosts: dict[str, int] = field(default_factory=lambda: {"scanned": 0, "killed": 0})
    drift: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


# ============== 白名单 ==============


def _load_keep_patterns() -> list[str]:
    """读取个案保留清单（data/runtime/process_reaper_keep.txt，每行一个 cmdline 子串）。"""
    patterns: list[str] = []
    try:
        if _KEEP_FILE.exists():
            for line in _KEEP_FILE.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.append(line)
    except OSError as e:
        logger.warning("keep 文件读取失败（忽略，按无个案保留处理）: %s", e)
    return patterns


def _is_whitelisted(cmdline: str, whitelist_res: list[re.Pattern], keep_subs: list[str]) -> str | None:
    """命中白名单返回命中描述，未命中返回 None。"""
    for rx in whitelist_res:
        if rx.search(cmdline):
            return f"whitelist:{rx.pattern[:40]}"
    for sub in keep_subs:
        if sub in cmdline:
            return f"keep_file:{sub[:40]}"
    return None


# ============== 进程枚举与判定（纯函数，可测试）==============


def classify_process(
    *,
    pid: int,
    cmdline: str,
    age_s: float,
    mem_mb: float,
    cpu_pct: float,
    children: int,
    orphan: bool,
    is_self_ancestor: bool,
    is_trae_descendant: bool,
    whitelist_hit: str | None,
) -> ProcVerdict:
    """判定矩阵纯函数实现。输入均为外部可观测量，不依赖 psutil，便于单测。"""
    v = ProcVerdict(
        pid=pid,
        action="skip",
        reason="",
        cmdline=cmdline,
        age_s=age_s,
        mem_mb=mem_mb,
        cpu_pct=cpu_pct,
        children=children,
        orphan=orphan,
    )
    if is_self_ancestor:
        v.reason = "self_or_ancestor"
        return v
    if whitelist_hit:
        v.reason = whitelist_hit
        return v
    if is_trae_descendant:
        v.reason = "trae_descendant"
        return v
    # DANGEROUS：资源失控，不论年龄
    if mem_mb > _DANGEROUS_MEM_GB * 1024 or children > _DANGEROUS_CHILDREN:
        v.action = "kill"
        v.reason = f"dangerous:mem={mem_mb:.0f}MB,children={children}"
        return v
    # .runtime/ 临时目录脚本 + 孤儿：立即杀（sweep_runner 族精准命中）
    if orphan and _RUNTIME_PATH_MARKER.search(cmdline):
        v.action = "kill"
        v.reason = f"runtime_dir_orphan:age={age_s / 60:.0f}min"
        return v
    # 孤儿分级
    if orphan:
        if age_s > _ORPHAN_KILL_AGE_S:
            v.action = "kill"
            v.reason = f"orphan_aged:age={age_s / 3600:.1f}h"
        elif age_s > _ORPHAN_REPORT_AGE_S:
            v.action = "report"
            v.reason = f"orphan_watch:age={age_s / 60:.0f}min"
        else:
            v.reason = f"orphan_young:age={age_s / 60:.0f}min"
        return v
    # 非孤儿长命空转
    if age_s > _IDLE_KILL_AGE_S and cpu_pct < _IDLE_KILL_CPU_MAX:
        v.action = "kill"
        v.reason = f"idle_aged:age={age_s / 3600:.1f}h,cpu={cpu_pct:.2f}%"
        return v
    if age_s > _IDLE_REPORT_AGE_S and cpu_pct < _IDLE_REPORT_CPU_MAX:
        v.action = "report"
        v.reason = f"idle_watch:age={age_s / 3600:.1f}h,cpu={cpu_pct:.2f}%"
        return v
    v.reason = "normal"
    return v


def _build_trae_descendant_set(procs: dict[int, dict]) -> set[int]:
    """构建 Trae CN 后代 PID 集合（沿 ppid 链向上，任一祖先是 Trae CN 即命中）。

    父链断裂（父 PID 不在进程表）时停止——该进程同时会被判为孤儿，走孤儿规则。
    """
    trae_pids = {
        pid for pid, info in procs.items() if info.get("name", "").lower().startswith(_TRAE_PROCESS_NAME_PREFIX)
    }
    if not trae_pids:
        return set()
    descendants: set[int] = set()
    for pid in procs:
        if pid in trae_pids:
            continue
        cur = procs[pid].get("ppid")
        depth = 0
        while cur and cur in procs and depth < 32:
            if cur in trae_pids:
                descendants.add(pid)
                break
            cur = procs[cur].get("ppid")
            depth += 1
    return descendants


def _scan_project_python_processes(project_root: str) -> tuple[dict[int, dict], dict[int, dict]]:
    """枚举全部进程，返回 (项目 python 进程表, 全进程表)。

    项目进程判定（继承 zombie_scanner 语义）：cmdline 或 cwd 任一包含项目根路径。
    """
    all_procs: dict[int, dict] = {}
    project_py: dict[int, dict] = {}
    for proc in psutil.process_iter(["pid", "name", "cmdline", "ppid", "create_time"]):
        try:
            info = proc.info
            pid = info.get("pid")
            if pid is None:
                continue
            cmdline_list = info.get("cmdline") or []
            cmdline = " ".join(cmdline_list) if isinstance(cmdline_list, list) else str(cmdline_list)
            all_procs[pid] = {
                "name": info.get("name") or "",
                "ppid": info.get("ppid"),
                "cmdline": cmdline,
                "create_time": info.get("create_time") or 0.0,
            }
            name = (info.get("name") or "").lower()
            if "python" not in name or not cmdline:
                continue
            # cwd 获取可能 AccessDenied，尽力而为
            cwd = ""
            try:
                cwd = proc.cwd() or ""
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
            if project_root in cmdline or project_root in cwd:
                project_py[pid] = all_procs[pid]
                project_py[pid]["cwd"] = cwd
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return project_py, all_procs


def _collect_metrics(project_py: dict[int, dict]) -> None:
    """就地填充 mem/cpu/children（cpu_percent 用短间隔采样取瞬时值）。"""
    for pid, info in project_py.items():
        try:
            proc = psutil.Process(pid)
            info["mem_mb"] = proc.memory_info().rss / (1024 * 1024)
            info["cpu_pct"] = proc.cpu_percent(interval=0.1)
            try:
                info["children"] = len(proc.children())
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                info["children"] = 0
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            info["dead"] = True


def _is_self_ancestor(pid: int, all_procs: dict[int, dict]) -> bool:
    """pid 是否为当前 reaper 进程自身或祖先链成员（防自杀）。"""
    me = os.getpid()
    if pid == me:
        return True
    cur = all_procs.get(me, {}).get("ppid")
    depth = 0
    while cur and depth < 32:
        if cur == pid:
            return True
        cur = all_procs.get(cur, {}).get("ppid")
        depth += 1
    return False


# ============== kill ==============


def _log_kill(pid: int, reason: str, dry_run: bool) -> None:
    try:
        _KILL_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(_KILL_LOG, "a", encoding="utf-8") as f:
            tag = "DRY-RUN" if dry_run else "KILLED"
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {tag} PID={pid} reason={reason}\n")
    except OSError as e:
        logger.warning("kill 日志写入失败: %s", e)


def _kill_pid_tree(pid: int) -> bool:
    """terminate → 等 3s → kill 升级；级联杀子进程树（先子后父）。"""
    try:
        proc = psutil.Process(pid)
    except psutil.NoSuchProcess:
        return True  # 已退出视为成功（幂等）
    targets: list[Any] = []
    if _KILL_CHILD_RECURSIVE:
        try:
            targets.extend(proc.children(recursive=True))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    targets.append(proc)
    for t in targets:
        try:
            t.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    gone, alive = psutil.wait_procs(targets, timeout=3)
    for t in alive:
        try:
            t.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    try:
        proc.wait(timeout=2)
        return True
    except psutil.TimeoutExpired:
        return False
    except psutil.NoSuchProcess:
        return True


# ============== Trae 幽灵窗口扫描（2026-08-28 从 ide_health_daemon 迁入并修复）==============
# 迁移说明：旧 ide_health_daemon._get_trae_processes 用精确匹配 psutil name=="Trae CN"，
# 但 psutil 实际返回 "Trae CN.exe"——原实现静默失效（永远扫描为空）。迁入后统一为
# startswith 前缀匹配（与 reaper Trae 后代判定同一真源）。
# 幽灵窗口语义：MainWindowHandle=0 且其 window-config UUID 无对应可见窗口的 TRAE 进程树，
# 多为 IDE 崩溃/异常关闭后的残留渲染进程，发现即 force kill。


def _get_trae_processes() -> list[dict[str, Any]]:
    """枚举全部 Trae CN 进程（psutil name 前缀匹配，修复原精确匹配静默失效 bug）。"""
    procs: list[dict[str, Any]] = []
    if psutil is None:
        return procs
    for p in psutil.process_iter(["pid", "name"]):
        try:
            info = p.info
            if (info.get("name") or "").lower().startswith(_TRAE_PROCESS_NAME_PREFIX):
                procs.append({"pid": info["pid"], "name": info["name"]})
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return procs


def _get_window_configs_from_cmdlines(pids: list[int]) -> dict[str, set[int]]:
    """WMI 查询每个 TRAE 进程命令行，提取 vscode-window-config UUID。

    返回 {window_config_uuid: {pid, ...}}。
    """
    from zephyr.shared.infra.process_pool import run_subprocess_hidden

    windows: dict[str, set[int]] = {}
    for pid in pids:
        try:
            result = run_subprocess_hidden(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    f'(Get-WmiObject Win32_Process -Filter "ProcessId={pid}").CommandLine',
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            match = re.search(r"vscode-window-config=vscode:([a-f0-9-]+)", result.stdout)
            if match:
                windows.setdefault(match.group(1), set()).add(pid)
        except Exception:  # noqa: BLE001 — 单进程查询失败不影响整体扫描
            continue
    return windows


def _get_visible_window_configs() -> set[str]:
    """获取 MainWindowTitle 非空（可见）的 TRAE 窗口对应的 window-config UUID 集合。"""
    from zephyr.shared.infra.process_pool import run_subprocess_hidden

    visible: set[str] = set()
    try:
        result = run_subprocess_hidden(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "Get-Process -Name 'Trae CN' -ErrorAction SilentlyContinue | "
                "Where-Object { $_.MainWindowTitle -ne '' } | "
                "ForEach-Object { "
                '  try { (Get-WmiObject Win32_Process -Filter \\"ProcessId=$($_.Id)\\").CommandLine } catch {} '
                "}",
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )
        for match in re.finditer(r"vscode-window-config=vscode:([a-f0-9-]+)", result.stdout):
            visible.add(match.group(1))
    except Exception as e:  # noqa: BLE001 — 可见窗口查询失败时退化为全部按幽灵处理（保守不杀：由 handle==0 二次过滤）
        logger.warning("可见 TRAE 窗口查询失败: %s", e)
    return visible


def _get_mainwindow_handle_map() -> dict[int, int]:
    """返回 {pid: MainWindowHandle}，仅含 TRAE 进程。"""
    from zephyr.shared.infra.process_pool import run_subprocess_hidden

    handle_map: dict[int, int] = {}
    try:
        result = run_subprocess_hidden(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "Get-Process -Name 'Trae CN' -ErrorAction SilentlyContinue | "
                "Select-Object Id, MainWindowHandle | "
                "ForEach-Object { '{0}:{1}' -f $_.Id, $_.MainWindowHandle }",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        for line in result.stdout.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            parts = line.split(":", 1)
            if len(parts) == 2:
                try:
                    handle_map[int(parts[0])] = int(parts[1])
                except ValueError:
                    continue
    except Exception as e:  # noqa: BLE001
        logger.warning("MainWindowHandle 查询失败: %s", e)
    return handle_map


def scan_ghost_windows() -> list[dict[str, Any]]:
    """扫描所有 TRAE 幽灵窗口（MainWindowHandle=0 且无对应可见窗口的 window-config）。

    零副作用（只读）。返回 [{config_id, pids, pid_count}]。
    消费方：process_reaper 周期清理；resource_optimization snapshot 指标采集。
    """
    procs = _get_trae_processes()
    if not procs:
        return []

    all_pids = [p["pid"] for p in procs]
    windows = _get_window_configs_from_cmdlines(all_pids)
    visible = _get_visible_window_configs()
    handle_map = _get_mainwindow_handle_map()

    ghosts: list[dict[str, Any]] = []
    for config_id, pids in windows.items():
        if config_id in visible:
            continue
        ghost_pids = [pid for pid in pids if pid in handle_map and handle_map[pid] == 0]
        if ghost_pids:
            ghosts.append(
                {
                    "config_id": config_id,
                    "pids": sorted(ghost_pids),
                    "pid_count": len(ghost_pids),
                }
            )
    return ghosts


def kill_ghost_windows(ghosts: list[dict[str, Any]] | None = None) -> list[int]:
    """Force kill 幽灵窗口进程树。不传 ghosts 时自动扫描。返回被 kill 的 PID 列表。"""
    import signal as _signal

    if ghosts is None:
        ghosts = scan_ghost_windows()

    killed: list[int] = []
    for ghost in ghosts:
        for pid in ghost["pids"]:
            try:
                os.kill(pid, _signal.SIGTERM)
                killed.append(pid)
                logger.info("killed ghost PID %d (config=%s)", pid, ghost["config_id"])
            except OSError:
                try:
                    psutil.Process(pid).terminate()
                    killed.append(pid)
                    logger.info("psutil-terminated ghost PID %d", pid)
                except Exception:  # noqa: BLE001
                    logger.warning("failed to kill ghost PID %d", pid, exc_info=True)
    return killed


def _reap_ghost_windows(dry_run: bool) -> dict[str, int]:
    result = {"scanned": 0, "killed": 0}
    try:
        ghosts = scan_ghost_windows()
        result["scanned"] = len(ghosts)
        if ghosts and not dry_run:
            killed = kill_ghost_windows(ghosts)
            result["killed"] = len(killed)
            for pid in killed:
                _log_kill(pid, "trae_ghost_window", dry_run=False)
        elif ghosts:
            logger.info("[dry-run] 检测到 %d 个幽灵窗口，不执行 kill", len(ghosts))
    except Exception as e:  # noqa: BLE001 — 幽灵窗口扫描失败不阻断 python 进程清理主流程
        logger.warning("幽灵窗口扫描异常（跳过）: %s", e)
    return result


# ============== drift 指标（从 ide_health_daemon 迁移）==============


def _collect_drift_metrics(dry_run: bool) -> dict[str, Any]:
    """git stash>5 自动清理 + worktree 变更>50 告警记录。"""
    from zephyr.shared.infra.process_pool import run_subprocess_hidden

    metrics: dict[str, Any] = {"stash_count": None, "worktree_changes": None}
    try:
        r = run_subprocess_hidden(
            ["git", "stash", "list"], capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=30
        )
        if r.returncode == 0:
            metrics["stash_count"] = len([l for l in r.stdout.splitlines() if l.strip()])
    except Exception as e:  # noqa: BLE001 — drift 采集失败不阻断主流程
        logger.warning("git stash list 失败: %s", e)
    try:
        r = run_subprocess_hidden(
            ["git", "status", "--porcelain"], capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=60
        )
        if r.returncode == 0:
            metrics["worktree_changes"] = len([l for l in r.stdout.splitlines() if l.strip()])
    except Exception as e:  # noqa: BLE001
        logger.warning("git status 失败: %s", e)

    if metrics["stash_count"] is not None and metrics["stash_count"] > 5:
        if dry_run:
            logger.info("[dry-run] stash=%d > 5，跳过自动清理", metrics["stash_count"])
        else:
            logger.warning("stash=%d > 5，自动清理（保留最新3）", metrics["stash_count"])
            try:
                run_subprocess_hidden(
                    [sys.executable, "scripts/governance/cleanup_stash.py", "--cleanup"],
                    cwd=str(REPO_ROOT),
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
            except Exception as e:  # noqa: BLE001
                logger.warning("stash 自动清理失败: %s", e)
    if metrics["worktree_changes"] is not None and metrics["worktree_changes"] > 50:
        logger.warning("worktree_changes=%d > 50（并行 session 漂移风险）", metrics["worktree_changes"])
    return metrics


# ============== 状态落盘 ==============


def _write_status(report: ReapReport) -> None:
    try:
        _STATUS_DIR.mkdir(parents=True, exist_ok=True)
        tmp = _STATUS_DIR / f"last_run.{os.getpid()}.tmp"
        tmp.write_text(
            json.dumps(report.__dict__, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
        )
        os.replace(tmp, _STATUS_FILE)
    except OSError as e:
        logger.warning("状态落盘失败: %s", e)


# ============== 主流程 ==============


def reap(dry_run: bool = False) -> ReapReport:
    """执行一轮清理。one-shot：scan→判定→kill→落盘→返回，调用方随即退出。"""
    report = ReapReport(timestamp=time.strftime("%Y-%m-%d %H:%M:%S"), dry_run=dry_run)
    project_root = str(REPO_ROOT)

    # 1) python 进程清理（psutil 不可用时降级关闭，fail-safe 方向=不清理）
    if psutil is None:
        report.errors.append("psutil unavailable: python process scan disabled")
        logger.error("psutil 不可用，python 进程扫描降级关闭（仅执行幽灵窗口扫描）")
    else:
        whitelist_res = [re.compile(p, re.IGNORECASE) for p in _DEFAULT_WHITELIST]
        keep_subs = _load_keep_patterns()
        project_py, all_procs = _scan_project_python_processes(project_root)
        _collect_metrics(project_py)
        trae_descendants = _build_trae_descendant_set(all_procs)
        live_pids = set(all_procs.keys())

        for pid, info in project_py.items():
            if info.get("dead"):
                continue
            report.scanned += 1
            cmdline = info.get("cmdline", "")
            ppid = info.get("ppid")
            orphan = ppid not in live_pids
            whitelist_hit = _is_whitelisted(cmdline, whitelist_res, keep_subs)
            if whitelist_hit:
                report.whitelist_hits += 1
            if pid in trae_descendants:
                report.trae_descendant_hits += 1
            verdict = classify_process(
                pid=pid,
                cmdline=cmdline,
                age_s=time.time() - info.get("create_time", time.time()),
                mem_mb=info.get("mem_mb", 0.0),
                cpu_pct=info.get("cpu_pct", 0.0),
                children=info.get("children", 0),
                orphan=orphan,
                is_self_ancestor=_is_self_ancestor(pid, all_procs),
                is_trae_descendant=pid in trae_descendants,
                whitelist_hit=whitelist_hit,
            )
            if verdict.action == "kill":
                if dry_run:
                    verdict.killed = False
                    _log_kill(pid, verdict.reason, dry_run=True)
                else:
                    verdict.killed = _kill_pid_tree(pid)
                    _log_kill(pid, verdict.reason + ("" if verdict.killed else " [FAILED]"), dry_run=False)
                report.killed.append(
                    {
                        "pid": pid,
                        "reason": verdict.reason,
                        "cmdline": cmdline[:120],
                        "age_h": round(verdict.age_s / 3600, 2),
                        "killed": verdict.killed,
                    }
                )
                logger.warning(
                    "%s PID=%d reason=%s cmd=%s",
                    "[dry-run] would kill" if dry_run else "killed",
                    pid,
                    verdict.reason,
                    cmdline[:100],
                )
            elif verdict.action == "report":
                report.reported.append(
                    {
                        "pid": pid,
                        "reason": verdict.reason,
                        "cmdline": cmdline[:120],
                        "age_h": round(verdict.age_s / 3600, 2),
                    }
                )
                logger.info("watch PID=%d reason=%s", pid, verdict.reason)

    # 2) Trae 幽灵窗口
    report.ghosts = _reap_ghost_windows(dry_run)

    # 3) drift 指标
    report.drift = _collect_drift_metrics(dry_run)

    _write_status(report)
    return report


def _print_status() -> int:
    if not _STATUS_FILE.exists():
        print("never_run=true（无状态文件，等待 Task Scheduler 首次触发）")
        return 0
    try:
        data = json.loads(_STATUS_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(f"status_file_corrupt={e}")
        return 1
    print(f"last_run={data.get('timestamp')}")
    print(f"dry_run={data.get('dry_run')}")
    print(f"scanned={data.get('scanned')} whitelist_hits={data.get('whitelist_hits')} trae_hits={data.get('trae_descendant_hits')}")
    print(f"killed={len(data.get('killed', []))} reported={len(data.get('reported', []))}")
    print(f"ghosts={data.get('ghosts')}")
    print(f"drift={data.get('drift')}")
    if data.get("errors"):
        print(f"errors={data.get('errors')}")
    return 0


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(REPO_ROOT / "tmp" / "process_reaper.log", encoding="utf-8"),
        ],
    )
    parser = argparse.ArgumentParser(description="项目残留进程清理器（one-shot，Task Scheduler 托管）")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--dry-run", action="store_true", help="只报告不杀（验证用）")
    group.add_argument("--status", action="store_true", help="读取上次运行状态")
    args = parser.parse_args()

    if args.status:
        sys.exit(_print_status())

    report = reap(dry_run=args.dry_run)
    print(
        json.dumps(
            {
                "scanned": report.scanned,
                "killed": len(report.killed),
                "reported": len(report.reported),
                "whitelist_hits": report.whitelist_hits,
                "trae_hits": report.trae_descendant_hits,
                "ghosts": report.ghosts,
                "dry_run": report.dry_run,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
