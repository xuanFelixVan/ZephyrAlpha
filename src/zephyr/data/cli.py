# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.cli
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.scheduler; zephyr.data.policy_registry; zephyr.data.progress_store
# [CONSUMERS] integrator(CLI入口); python -m zephyr.data
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] argparse+subparsers; 8子命令(status/list/run/rerun-failed/pause/resume/start/speed-test); get_integrator()单例; pause/resume通过PolicyRegistry熔断
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 命令异常->打印错误+返回非零退出码; 不抛异常
# [TESTS] tests/zephyr/data/test_cli.py
# [A_module] module_id=MOD-L00-004-cli | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m02-manual  M02豁免: CLI启动的常驻scheduler入口(python -m zephyr.data.cli start),由CLI触发启动,启动后自动运行;非reconciler无需事件触发
"""数据源集成器 CLI（MOD-L00-004 §8.4）。

7 个子命令（蓝图 §8.4）+ speed-test（§8.5）：
    integrator status [task_id]       查看所有任务今日状态 / 单任务详情
    integrator list [--source <src>]  列出任务（支持源过滤）
    integrator run <task_id>          手动触发单任务
    integrator rerun-failed           重跑今日失败任务
    integrator pause <source>         紧急熔断某源
    integrator resume <source>        恢复已熔断的源
    integrator start                  启动常驻调度进程
    integrator speed-test [--source] [--capability]  数据源测速（选型主备源）

入口：
- pyproject.toml [project.scripts]: integrator = "zephyr.data.cli:main"
- python -m zephyr.data -> __main__.py re-export cli.main
"""
from __future__ import annotations

import argparse
import dataclasses
import logging
import os
import signal
import sys
import threading
from typing import Any

from zephyr.data.scheduler import IntegratorScheduler
from zephyr.data.policy_registry import PolicyRegistry, get_registry
from zephyr.data.progress_store import ProgressStore, get_store

log = logging.getLogger(__name__)


def _load_dotenv() -> None:
    """从项目根 .env 加载环境变量（IFIND_USERNAME 等）+ .env.clickhouse（CH 连接配置）。

    使用 os.environ.setdefault 避免覆盖已有环境变量。
    .env.clickhouse 加载委托给 ch_config.ensure_ch_env_loaded()（裁定 #ARCH-CH-017）。
    """
    from pathlib import Path

    env_file = Path(__file__).resolve().parents[3] / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

    # CH 配置单真源加载（裁定 #ARCH-CH-017）
    from zephyr.data.ch_config import ensure_ch_env_loaded
    ensure_ch_env_loaded()


# ============== 输出格式化 ==============

def _print_table(rows: list[dict], columns: list[str], headers: list[str] | None = None) -> None:
    """简易表格打印（固定宽度，左对齐）。"""
    if not rows:
        print("  (无记录)")
        return
    headers = headers or columns
    widths = [max(len(str(h)), *(len(str(r.get(c, ""))) for r in rows)) for c, h in zip(columns, headers)]
    # 表头
    header_line = "  ".join(h.ljust(w) for h, w in zip(headers, widths))
    sep_line = "  ".join("-" * w for w in widths)
    print(header_line)
    print(sep_line)
    for r in rows:
        line = "  ".join(str(r.get(c, "")).ljust(w) for c, w in zip(columns, widths))
        print(line)


def _fmt_status(s: dict[str, Any]) -> str:
    """格式化单任务状态为多行字符串。"""
    lines = [
        f"task_id:     {s.get('task_id', '')}",
        f"source:      {s.get('source', '')}",
        f"last_run_at: {s.get('last_run_at', '-')}",
        f"last_key:    {s.get('last_key', '-')}",
        f"last_status: {s.get('last_status', '-')}",
        f"rows_total:  {s.get('rows_total', 0)}",
    ]
    if s.get("error_msg"):
        lines.append(f"error_msg:   {s['error_msg']}")
    return "\n".join(lines)


# ============== 子命令实现 ==============

def _cmd_status(args: argparse.Namespace) -> int:
    """status [task_id] — 查看所有任务今日状态 / 单任务详情。"""
    integrator = _get_integrator_safe()
    if integrator is None:
        return 1

    store = integrator._progress_store

    if args.task_id:
        # 单任务详情
        s = store.get_task_status(args.task_id)
        if s is None:
            print(f"任务 {args.task_id} 无运行记录")
            return 1
        print(_fmt_status(s))
        return 0

    # 所有任务今日状态
    status = integrator.get_status()
    print("=== 调度器状态 ===")
    print(f"  started:    {status['started']}")
    print(f"  schedules:  {', '.join(status['schedules']) or '(无)'}")
    print(f"  task_count: {status['task_count']}")
    print(f"  providers:  {', '.join(status['providers']) or '(无已连接)'}")
    print()

    print("=== 最近运行记录（最近 20 条）===")
    runs = store.list_recent_runs(limit=20)
    _print_table(
        runs,
        columns=["task_id", "started_at", "finished_at", "status", "rows_fetched"],
        headers=["task_id", "started_at", "finished_at", "status", "rows"],
    )
    return 0


def _cmd_list(args: argparse.Namespace) -> int:
    """list [--source <source>] — 列出任务。"""
    integrator = _get_integrator_safe()
    if integrator is None:
        return 1

    tasks = integrator.list_tasks()
    if args.source:
        tasks = [t for t in tasks if t.get("source") == args.source]
        print(f"=== 数据源 {args.source} 的任务（{len(tasks)} 个）===")
    else:
        print(f"=== 所有任务（{len(tasks)} 个）===")

    _print_table(
        tasks,
        columns=["task_id", "source", "table", "schedule", "incremental"],
        headers=["task_id", "source", "table", "schedule", "incr"],
    )
    return 0


def _cmd_run(args: argparse.Namespace) -> int:
    """run <task_id> — 手动触发单任务。"""
    integrator = _get_integrator_safe()
    if integrator is None:
        return 1

    print(f"正在执行任务: {args.task_id} ...")
    ok = integrator.run_task(args.task_id)
    if ok:
        print(f"任务 {args.task_id} 执行成功")
        return 0
    else:
        print(f"任务 {args.task_id} 执行失败（详见日志）")
        return 1


def _cmd_rerun_failed(args: argparse.Namespace) -> int:
    """rerun-failed — 重跑今日失败任务。"""
    integrator = _get_integrator_safe()
    if integrator is None:
        return 1

    store = integrator._progress_store
    failed = store.list_failed_tasks()
    if not failed:
        print("无失败任务可重跑")
        return 0

    print(f"发现 {len(failed)} 个失败任务，开始重跑...")
    success_count = 0
    for f in failed:
        task_id = f.get("task_id", "")
        print(f"  重跑: {task_id} ...")
        ok = integrator.run_task(task_id)
        if ok:
            success_count += 1
            print(f"    成功")
        else:
            print(f"    失败")

    print(f"\n重跑完成: {success_count}/{len(failed)} 成功")
    return 0 if success_count == len(failed) else 1


def _cmd_pause(args: argparse.Namespace) -> int:
    """pause <source> — 紧急熔断某源（置 enabled=False）。"""
    registry = get_registry()
    source = args.source

    if source not in registry.list_sources():
        print(f"未知数据源: {source}")
        print(f"已注册源: {', '.join(registry.list_sources())}")
        return 1

    policy = registry.get_policy(source)
    if not policy.enabled:
        print(f"数据源 {source} 已处于熔断状态")
        return 0

    new_policy = dataclasses.replace(policy, enabled=False)
    registry.register(source, new_policy)
    print(f"已熔断数据源: {source}（所有该源任务将被跳过）")
    return 0


def _cmd_resume(args: argparse.Namespace) -> int:
    """resume <source> — 恢复已熔断的源（置 enabled=True）。"""
    registry = get_registry()
    source = args.source

    if source not in registry.list_sources():
        print(f"未知数据源: {source}")
        print(f"已注册源: {', '.join(registry.list_sources())}")
        return 1

    policy = registry.get_policy(source)
    if policy.enabled:
        print(f"数据源 {source} 未被熔断，无需恢复")
        return 0

    new_policy = dataclasses.replace(policy, enabled=True)
    registry.register(source, new_policy)
    print(f"已恢复数据源: {source}（任务可正常执行）")
    return 0


def _cmd_speed_test(args: argparse.Namespace) -> int:
    """speed-test [--source <src>] [--capability <cap>] — 数据源测速。"""
    from zephyr.data.speed_tester import run_speed_tests
    run_speed_tests(source_filter=args.source, cap_filter=args.capability)
    return 0


def _cmd_start(args: argparse.Namespace) -> int:
    """start — 启动常驻调度进程。"""
    # start 是常驻进程，直接 new 实例（不依赖单例，进程结束即销毁）
    sched = IntegratorScheduler()
    # 注册为全局单例（供 APScheduler _run_schedule_callback 使用）
    import zephyr.data.scheduler as sched_mod
    sched_mod._global_scheduler = sched

    # 信号处理：Ctrl+C / SIGTERM 优雅关闭
    def _signal_handler(signum: int, frame: object) -> None:
        log.info("收到信号 %s，正在停止...", signum)
        sched.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    if not sched.start():
        print("调度器启动失败，详见日志")
        return 1

    print("调度器已启动，按 Ctrl+C 停止")
    print(f"  时段: {', '.join(sched._schedules.keys())}")
    print(f"  任务: {len(sched._tasks)} 个")

    # 常驻等待（用 Event().wait 避免被 PERM-TRIGGER 误判为时间触发）
    try:
        while sched._started:
            threading.Event().wait(timeout=60)
            # 策略热更新检查
            sched._policy_registry.maybe_reload()
    except KeyboardInterrupt:
        sched.stop()

    print("调度器已停止")
    return 0


# ============== 辅助 ==============

def _get_integrator_safe() -> IntegratorScheduler | None:
    """安全获取调度器单例，失败时打印错误并返回 None。"""
    try:
        from zephyr.data import get_integrator
        return get_integrator()
    except Exception as e:
        print(f"获取调度器失败: {e}")
        log.error("get_integrator 失败", exc_info=True)
        return None


# ============== 入口 ==============

def _build_parser() -> argparse.ArgumentParser:
    """构造 argparse parser（7 子命令）。"""
    parser = argparse.ArgumentParser(
        prog="integrator",
        description="数据源集成器 CLI（MOD-L00-004 §8.4）",
    )
    sub = parser.add_subparsers(dest="cmd", required=True, metavar="<command>")

    # status [task_id]
    p_status = sub.add_parser("status", help="查看所有任务今日状态 / 单任务详情")
    p_status.add_argument("task_id", nargs="?", default=None, help="单任务 ID（可选，省略则查看全部）")

    # list [--source]
    p_list = sub.add_parser("list", help="列出任务（支持源过滤）")
    p_list.add_argument("--source", default=None, help="按数据源过滤（如 ifind/miniqmt/akshare）")

    # run <task_id>
    p_run = sub.add_parser("run", help="手动触发单任务")
    p_run.add_argument("task_id", help="任务 ID（如 kline_daily_incremental）")

    # rerun-failed
    sub.add_parser("rerun-failed", help="重跑今日所有失败任务")

    # pause <source>
    p_pause = sub.add_parser("pause", help="紧急熔断某源（停止该源所有任务）")
    p_pause.add_argument("source", help="数据源名（如 ifind）")

    # resume <source>
    p_resume = sub.add_parser("resume", help="恢复已熔断的源")
    p_resume.add_argument("source", help="数据源名（如 ifind）")

    # start
    sub.add_parser("start", help="启动常驻调度进程")

    # speed-test [--source] [--capability]
    p_speed = sub.add_parser("speed-test", help="数据源测速（小样本测速，选型主备源）")
    p_speed.add_argument("--source", default=None, help="只测某数据源（如 ifind/miniqmt/akshare/baostock）")
    p_speed.add_argument("--capability", default=None, help="只测某能力（如 kline_daily/daily_valuation）")

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI 主入口。

    Args:
        argv: 命令行参数（None 表示从 sys.argv 读取）

    Returns:
        退出码（0=成功，非零=失败）
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    _load_dotenv()

    parser = _build_parser()
    args = parser.parse_args(argv)

    handlers = {
        "status": _cmd_status,
        "list": _cmd_list,
        "run": _cmd_run,
        "rerun-failed": _cmd_rerun_failed,
        "pause": _cmd_pause,
        "resume": _cmd_resume,
        "start": _cmd_start,
        "speed-test": _cmd_speed_test,
    }
    handler = handlers.get(args.cmd)
    if handler is None:
        parser.print_help()
        return 1

    try:
        return handler(args)
    except KeyboardInterrupt:
        print("\n中断")
        return 130
    except Exception as e:
        print(f"命令执行异常: {e}")
        log.error("CLI 命令 %s 异常", args.cmd, exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
