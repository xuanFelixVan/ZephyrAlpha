# [BLUEPRINT] MOD-RESOURCE_OPTIMIZATION_ENGINE | docs/03_modules/_cross_layer/resource_optimization_engine/blueprint.md | §new-IDE
# [MODULE] scripts.ide_health_service
# [DOMAIN]
# [DEPENDENCIES]
# [CONSUMERS] .trae/rules/project_rules.md; .trae/rules/onboarding_detail.md; AGENTS.md; docs/01_policies_and_standards/rules/trae_053_automation_dual_track.yaml
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] --status优先PID文件检测(跨进程),回退registry(进程内);--start检查已在运行后写PID文件+atexit清理+阻塞;--start-background后台分离子进程非阻塞启动;stale PID文件自动清理
# [MODIFY-GUARD] MOD-RESOURCE_OPTIMIZATION_ENGINE §new-IDE
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 导入失败时打印明确错误信息并exit 1;--status守护进程未运行时exit 0并打印stopped
# [TESTS]
# [A_module] module_id=MOD-SCR_ide_health_service | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""IDE健康守护进程CLI包装器

包装 src/zephyr/trading/ide_health_daemon.py，提供 --status/--start CLI 接口。
守护进程本身在应用运行时通过 register_daemon() 自动注册启动，本脚本提供
命令行查询和手动启动入口（用于 session 冷启动序列 STEP 0）。

用法:
    python scripts/ide_health_service.py --status    # 查询守护进程状态
    python scripts/ide_health_service.py --start     # 注册并启动守护进程（阻塞）
"""

from __future__ import annotations

import argparse
import atexit
import logging
import os
import sys
import time
from pathlib import Path

# 确保项目根目录与 src/ 在 sys.path 中（src/ 用于 import zephyr.*）
# 一次性 bootstrap（REPO_ROOT 规则允许 scripts/ 一次性 sys.path bootstrap）
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_SRC_ROOT = _PROJECT_ROOT / "src"
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402

from zephyr.shared.infra.process_pool import is_pid_alive  # PID 存活检测真源唯一（红蓝对抗归一，曾三处分裂）

logger = logging.getLogger(__name__)

# PID 文件路径（跨进程状态持久化）
# daemon_registry 是进程内 ClassVar，--start/--status 是两个独立进程，
# 进程间内存隔离导致 --status 永远看不到 --start 注册的 daemon。
# PID 文件是跨进程状态检测的唯一可靠机制。
_PID_FILE = _PROJECT_ROOT / ".runtime" / "ide_health_daemon.pid"


def _write_pid_file() -> None:
    """原子写入当前进程 PID 到 PID 文件（RULE-ONE 原子写入模板）。"""
    _PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = f"{_PID_FILE}.{os.getpid()}.tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(str(os.getpid()))
        os.replace(tmp_path, _PID_FILE)
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        raise


def _read_pid_file() -> int | None:
    """读取 PID 文件，返回 PID 或 None（文件不存在/损坏）。"""
    if not _PID_FILE.exists():
        return None
    try:
        return int(_PID_FILE.read_text(encoding="utf-8").strip())
    except (ValueError, OSError):
        return None


def _remove_pid_file() -> None:
    """清理 PID 文件（atexit 钩子调用）。"""
    try:
        _PID_FILE.unlink(missing_ok=True)
    except OSError:
        pass


def _check_pid_status() -> dict[str, str] | None:
    """通过 PID 文件检测守护进程状态（跨进程）。

    返回 dict 表示检测到状态（running true/false），返回 None 表示无 PID 文件
    （回退到 registry 检查，用于 boot_hooks 进程内启动场景）。
    """
    pid = _read_pid_file()
    if pid is None:
        return None
    alive = is_pid_alive(pid)
    if not alive:
        # stale PID 文件：进程已死但文件残留 → 清理
        _remove_pid_file()
        return {"running": "false", "ghost_count": "0", "detail": f"stale PID {pid} 已清理"}
    # 进程存活时尝试获取 ghost_count
    ghost_count = "0"
    try:
        from zephyr.trading.ide_health_daemon import scan_ghost_windows

        ghost_count = str(len(scan_ghost_windows()))
    except Exception:
        pass
    return {"running": "true", "ghost_count": ghost_count, "detail": f"pid={pid} 存活"}


def _get_daemon_status() -> dict[str, str]:
    """查询守护进程状态。

    返回 {"running": "true|false", "ghost_count": "N", "detail": "..."}
    """
    try:
        # 5.154.1 修复: 使用公共 getter 而非导入 _daemon_instance 私有单例
        from zephyr.trading.ide_health_daemon import get_daemon_instance
        daemon = get_daemon_instance()
    except ImportError as e:
        return {"running": "false", "ghost_count": "0", "detail": f"导入失败: {e}"}

    if daemon is None:
        return {"running": "false", "ghost_count": "0", "detail": "守护进程未注册"}

    # 5.154.1 修复: 使用 is_running 公共属性而非 _running 私有字段
    running = daemon.is_running
    ghost_count = daemon.ghost_count
    return {
        "running": "true" if running else "false",
        "ghost_count": str(ghost_count),
        "detail": f"running={running}, ghost_count={ghost_count}",
    }


def _check_registry_status() -> dict[str, str]:
    """通过 daemon_registry 查询状态（如果可用）。"""
    try:
        from zephyr.shared.lifecycle.daemon_registry import registry

        is_running = registry.is_running("ide_health_daemon")
        return {
            "running": "true" if is_running else "false",
            "ghost_count": "0",
            "detail": f"registry.is_running={is_running}",
        }
    except Exception:
        # registry 不可用时回退到 _daemon_instance 检查
        return _get_daemon_status()


def cmd_status() -> int:
    """--status: 查询守护进程状态。优先 PID 文件(跨进程)，回退 registry(进程内)。"""
    status = _check_pid_status()
    if status is None:
        # 无 PID 文件 → 回退到 registry 检查(boot_hooks 进程内启动场景)
        status = _check_registry_status()
    running = status["running"]
    print(f"running={running}")
    print(f"ghost_count={status['ghost_count']}")
    print(f"detail={status['detail']}")
    return 0


def cmd_start() -> int:
    """--start: 注册并启动守护进程，然后阻塞保持运行。"""
    # 跨进程检测：是否已有守护进程在运行
    existing_pid = _read_pid_file()
    if existing_pid is not None and is_pid_alive(existing_pid):
        print(f"IdeHealthDaemon 已在运行 (pid={existing_pid})，无需重复启动")
        return 0
    # stale PID 文件清理（进程已死但文件残留）
    if existing_pid is not None:
        _remove_pid_file()

    try:
        from zephyr.trading.ide_health_daemon import register_daemon
    except ImportError as e:
        print(f"ERROR: 无法导入 ide_health_daemon: {e}", file=sys.stderr)
        return 1

    print("注册并启动 IdeHealthDaemon...")
    try:
        register_daemon()
    except Exception as e:
        print(f"ERROR: 启动失败: {e}", file=sys.stderr)
        return 1

    # 写入 PID 文件（跨进程状态持久化）+ 注册 atexit 清理
    try:
        _write_pid_file()
    except OSError as e:
        print(f"WARNING: PID 文件写入失败: {e}", file=sys.stderr)
    atexit.register(_remove_pid_file)

    print("IdeHealthDaemon 已启动（Ctrl+C 退出）")
    print("守护进程每 30s 扫描一次 TRAE 幽灵窗口并自动清理")

    # 阻塞保持守护进程运行
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n收到退出信号，停止守护进程...")
        return 0


def cmd_start_background() -> int:
    """--start-background: 后台启动守护进程（非阻塞，立即返回）。

    用 subprocess.Popen 启动分离的子进程运行 --start，主进程立即返回。
    适用于 AI 冷启动序列 STEP 0（避免阻塞后续步骤）。
    """
    # 检查是否已有守护进程在运行
    existing_pid = _read_pid_file()
    if existing_pid is not None and is_pid_alive(existing_pid):
        print(f"IdeHealthDaemon 已在运行 (pid={existing_pid})，无需重复启动")
        return 0
    if existing_pid is not None:
        _remove_pid_file()

    # 后台分离启动子进程运行 --start
    import subprocess

    creation_flags = 0
    if os.name == "nt":
        creation_flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW

    proc = subprocess.Popen(
        [sys.executable, str(Path(__file__).resolve()), "--start"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        creationflags=creation_flags,
        close_fds=True,
    )

    # 等待 PID 文件出现（最多 5 秒）
    for _ in range(50):
        time.sleep(0.1)
        pid = _read_pid_file()
        if pid is not None and is_pid_alive(pid):
            print(f"IdeHealthDaemon 后台启动成功 (pid={pid})")
            return 0

    # PID 文件未出现，检查子进程是否还活着
    if proc.poll() is None:
        print(f"WARNING: 守护进程子进程 (pid={proc.pid}) 已启动但 PID 文件未生成，请用 --status 检查")
        return 0
    print(f"ERROR: 守护进程子进程启动后立即退出 (code={proc.returncode})", file=sys.stderr)
    return 1


def main() -> None:
    """CLI 入口。"""
    parser = argparse.ArgumentParser(
        description="IDE健康守护进程CLI包装器（包装 src/zephyr/trading/ide_health_daemon.py）",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--status", action="store_true", help="查询守护进程状态")
    group.add_argument("--start", action="store_true", help="注册并启动守护进程（阻塞）")
    group.add_argument(
        "--start-background", action="store_true", help="后台启动守护进程（非阻塞，立即返回，AI冷启动用）"
    )

    args = parser.parse_args()

    if args.status:
        sys.exit(cmd_status())
    elif args.start:
        sys.exit(cmd_start())
    elif args.start_background:
        sys.exit(cmd_start_background())


if __name__ == "__main__":
    main()
