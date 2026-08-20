# [BLUEPRINT] MOD-INF-046 | .trae/documents/runtime-tmp-test-residue-auto-cleanup.md | Part 1
# [MODULE] scripts.ops.cleanup_runtime_tmp_residue
# [DOMAIN] D_INFRA_OPS
# [DEPENDENCIES] zephyr.governance.audit.reconciliation_registry（共享判定函数 _should_remove_test_dir 等）
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] volatile
# [INVARIANTS] 一次性清理工具，默认 dry-run（只统计不删），--execute 才实清；判定真源复用 reconciliation_registry 共享函数（禁止内联实现形成双源漂移）；PID 存活+TTL 双判定防误删活跃测试
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=成功/dry-run 正常; exit 1=部分删除失败; exit 2=共享判定函数加载失败（fail-loud 拒绝降级）
# [TESTS]
# [TTL] task_bound
# noqa: m10-time-trigger  M10豁免: 本脚本是 oneoff 手动清理工具（--execute 显式触发），非 cron/Timer 自动调度；自动防复发由 GATE-RUNTIME-CLEANUP post-commit reconciler 事件驱动（trae_071 LAW-4）

"""cleanup_runtime_tmp_residue.py — 一次性清理 .runtime/tmp/ 下测试残留目录。

治本 #ARCH-TEST-RESIDUE-CLEANUP-001（2026-08-04）Part 1：

.runtime/tmp/ 下积压 10 万+ 文件，几乎全是测试框架残留目录：
  - pytest_<PID>/（tests/conftest.py:67 PID-unique basetemp，#ARCH-XDIST-WORKER-CRASH-001）
  - git_guard_test_*/（concurrency guard 测试残留）
  - tmp*/conc_mv_*/b1/g1/rb1_/fx1/rc1/p4-1b-test*/probe_test/xhs_ocr 等
  （覆盖前缀/精确名/TTL/防误删阈值的 authoritative 真源 =
   trae_071 §test_residue_reclaim，本脚本动态加载，禁止本地硬编码）

GATE-RUNTIME-CLEANUP reconciler 原用 os.rmdir 只删空目录，但 pytest_<PID>/ 内 fixture
子目录（test_conftest_py_exempted0/...）永远非空 → 永远删不掉。Part 2 已修 reconciler
升级为 shutil.rmtree + PID 存活 + TTL 双判定。本脚本是 Part 2 修复前的一次性存量清理。

判定真源唯一：复用 reconciliation_registry._should_remove_test_dir / _match_test_residue
（与 reconciler 共享同一真源，避免双源漂移）。

安全：
  - 默认 dry-run（只统计不删），--execute 才实清
  - PID 存活跳过（正在跑的测试不删）
  - mtime < 10min 跳过（防误删正在写入）
  - mtime < 2h 跳过（TTL 内保留，留窗口供近期测试复用）
  - 顶层平铺文件不动（commit_msg.txt 等活跃会话产物）
  - .gitkeep 跳过

用法：
  python scripts/ops/cleanup_runtime_tmp_residue.py            # dry-run（默认）
  python scripts/ops/cleanup_runtime_tmp_residue.py --execute  # 实清
"""

from __future__ import annotations

import argparse
import os
import shutil
import stat
import sys
import time
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_RUNTIME_TMP = _PROJECT_ROOT / ".runtime" / "tmp"


def _load_shared_predicates():
    """从 reconciliation_registry 加载共享判定函数 + config 加载器（判定真源唯一）。

    失败时 fail-loud 退出——清理脚本依赖与 reconciler 一致的判定逻辑 + YAML config，
    不可降级为内联实现（会形成双源漂移）。trae_071 §test_residue_reclaim.failure_handling:
    oneoff 脚本 config 不可达时 fail-loud 退出（手动工具必须有配置才能安全清理）。
    """
    src = _PROJECT_ROOT / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
    try:
        from zephyr.governance.audit.reconciliation_registry import (
            _load_test_residue_config,
            _match_test_residue,
            _should_remove_test_dir,
        )
    except ImportError as exc:
        print(
            f"[FATAL] 无法加载共享判定函数（reconciliation_registry）：{exc}\n"
            "清理脚本依赖与 reconciler 一致的判定逻辑，拒绝降级为内联实现。",
            file=sys.stderr,
        )
        sys.exit(2)
    # config 可达性 fail-loud 校验（trae_071 failure_handling）。
    # oneoff 手动工具必须有配置才能安全清理，config 不可达不降级。
    global _config_loader
    _config_loader = _load_test_residue_config
    if _load_test_residue_config() is None:
        print(
            "[FATAL] trae_071 test_residue_reclaim config 不可达，"
            "拒绝降级为内联实现（手动工具必须有配置才能安全清理）。",
            file=sys.stderr,
        )
        sys.exit(2)
    return _match_test_residue, _should_remove_test_dir


# 共享 config 加载器（_load_shared_predicates 注入；供 _categorize/_classify_keep_reason
# 动态读取 trae_071 YAML 真源，禁止本地硬编码前缀/阈值——trae_062 SSoT）。
_config_loader = None


def _count_files_in_tree(dirpath: str) -> int:
    """统计目录树内文件数（含子目录）。"""
    total = 0
    for _root, _dirs, files in os.walk(dirpath):
        total += len(files)
    return total


def _categorize(name: str) -> str:
    """把目录名归类用于统计展示（前缀/精确名真源 = trae_071 YAML，动态加载）。

    数据驱动：遍历 config.dir_prefixes 命中即归类，config.exact_names 命中返回原名，
    tmp_prefix 命中返回 "tmp*"。禁止本地硬编码前缀（trae_062 SSoT）。
    """
    cfg = _config_loader() if _config_loader is not None else None
    if cfg is None:
        return "other"
    if name in cfg["exact_names"]:
        return name
    for prefix in cfg["dir_prefixes"]:
        if name.startswith(prefix):
            # pytest_ 是 PID-unique basetemp，特例展示为 pytest_<PID>；其余展示 prefix*
            return "pytest_<PID>" if prefix == "pytest_" else f"{prefix}*"
    if name.startswith(cfg["tmp_prefix"]):
        return "tmp*"
    return "other"


def _classify_keep_reason(full: Path, now: float) -> str:
    """归类目录保留原因（活跃测试/TTL内/PID存活）。阈值真源 = trae_071 YAML。"""
    cfg = _config_loader() if _config_loader is not None else None
    if cfg is None:
        return "config不可达"
    try:
        age = now - os.path.getmtime(str(full))
    except OSError:
        age = 0.0
    fresh = cfg["fresh_protect_seconds"]
    ttl = cfg["ttl_seconds"]
    if age < fresh:
        return f"正在写入(<{int(fresh // 60)}min)"
    if age < ttl:
        return f"TTL内(<{int(ttl // 3600)}h)"
    return "PID存活"


def _parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(
        description="一次性清理 .runtime/tmp/ 下测试残留目录（pytest_*/git_guard_test_*/tmp* 等）"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--execute",
        action="store_true",
        help="实清（默认 dry-run 只统计不删）",
    )
    mode.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="只统计不删（默认）",
    )
    return parser.parse_args()


def _scan_entries(match_residue, should_remove, now: float):
    """扫描 .runtime/tmp/ 条目，分类收集删除候选。

    Returns:
        (will_delete, kept_reasons, category_counts, top_level_files)
    """
    will_delete: list[tuple[str, int, float]] = []
    kept_reasons: dict[str, int] = {}
    category_counts: dict[str, int] = {}
    top_level_files = 0

    try:
        entries = os.listdir(_RUNTIME_TMP)
    except OSError as exc:
        print(f"[FATAL] 无法列出 {_RUNTIME_TMP}: {exc}", file=sys.stderr)
        sys.exit(1)

    for name in entries:
        full = _RUNTIME_TMP / name
        if os.path.isfile(full):
            top_level_files += 1
            continue
        if not os.path.isdir(full) or name == ".gitkeep":
            continue
        if not match_residue(name):
            continue

        cat = _categorize(name)
        category_counts[cat] = category_counts.get(cat, 0) + 1

        if should_remove(full, now):
            try:
                mtime = os.path.getmtime(str(full))
            except OSError:
                mtime = 0.0
            fcount = _count_files_in_tree(str(full))
            will_delete.append((name, fcount, mtime))
        else:
            reason = _classify_keep_reason(full, now)
            kept_reasons[reason] = kept_reasons.get(reason, 0) + 1

    return will_delete, kept_reasons, category_counts, top_level_files


def _print_summary(will_delete, kept_reasons, category_counts, top_level_files, execute: bool):
    """打印 dry-run/execute 摘要。"""
    total_files = sum(fc for _n, fc, _m in will_delete)
    mode_label = "EXECUTE（实清）" if execute else "DRY-RUN（只统计）"
    print(f"== .runtime/tmp/ 测试残留清理 [{mode_label}] ==")
    print(f"扫描根: {_RUNTIME_TMP}")
    print(f"顶层平铺文件（不动）: {top_level_files}")
    print(f"测试残留目录总数: {sum(category_counts.values())}")
    print(f"将删除目录: {len(will_delete)} 个")
    print(f"将删除文件: {total_files} 个（含子目录）")
    print(f"保留目录（活跃）: {sum(kept_reasons.values())} 个")
    for reason, cnt in sorted(kept_reasons.items(), key=lambda x: -x[1]):
        print(f"  - {reason}: {cnt}")

    _print_category_breakdown(will_delete)
    _print_top_candidates(will_delete)

    if not execute:
        print("\n[DRY-RUN] 未删除任何文件。确认无误后用 --execute 实清。")


def _print_category_breakdown(will_delete):
    """打印按类型统计的删除分布。"""
    if not will_delete:
        return
    print("\n按类型统计（将删除）:")
    delete_cats: dict[str, int] = {}
    for name, _fc, _m in will_delete:
        c = _categorize(name)
        delete_cats[c] = delete_cats.get(c, 0) + 1
    for cat, cnt in sorted(delete_cats.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {cnt} 目录")


def _print_top_candidates(will_delete):
    """打印首批 20 个将删除目录。"""
    if not will_delete:
        return
    print("\n首批 20 个将删除目录（按文件数降序）:")
    from datetime import datetime

    for name, fc, mt in sorted(will_delete, key=lambda x: -x[1])[:20]:
        mt_str = datetime.fromtimestamp(mt).strftime("%Y-%m-%d %H:%M")
        print(f"  {name} ({fc} 文件, mtime {mt_str})")


def _on_rm_error(func, path, exc_info):  # noqa: ARG001
    """shutil.rmtree onerror：处理只读文件（git objects/.pyc 常见）。"""
    try:
        os.chmod(path, stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)
        func(path)
    except OSError:
        pass


def _execute_deletion(will_delete, match_residue) -> int:
    """执行实际删除，返回 exit code（0=成功, 1=部分失败）。"""
    deleted_dirs = 0
    deleted_files = 0
    errors = 0

    for name, fc, _m in will_delete:
        full = _RUNTIME_TMP / name
        try:
            shutil.rmtree(str(full), onerror=_on_rm_error)
        except OSError:
            pass
        if full.exists():
            errors += 1
        else:
            deleted_dirs += 1
            deleted_files += fc

    print(f"\n[EXECUTE] 已删除目录: {deleted_dirs}, 文件: {deleted_files}, 失败: {errors}")
    if errors:
        _print_remaining(match_residue)
    return 0 if errors == 0 else 1


def _print_remaining(match_residue):
    """列出剩余测试残留目录（删除失败 + 可能新产生的）。"""
    remaining = []
    for name in os.listdir(_RUNTIME_TMP):
        full = _RUNTIME_TMP / name
        if not full.is_dir() or name == ".gitkeep":
            continue
        if not match_residue(name):
            continue
        try:
            fc = _count_files_in_tree(str(full))
        except OSError:
            fc = -1
        remaining.append((name, fc))
    print(f"剩余测试残留目录: {len(remaining)} 个（含活跃保留 + 删除失败）:")
    for name, fc in sorted(remaining, key=lambda x: -(x[1] if x[1] > 0 else 0))[:20]:
        print(f"  {name} ({fc} 文件)")


def main() -> int:
    args = _parse_args()
    if not _RUNTIME_TMP.exists():
        print(f"[skip] {_RUNTIME_TMP} 不存在")
        return 0

    match_residue, should_remove = _load_shared_predicates()
    now = time.time()
    will_delete, kept_reasons, category_counts, top_level_files = _scan_entries(match_residue, should_remove, now)
    _print_summary(will_delete, kept_reasons, category_counts, top_level_files, args.execute)

    if not args.execute:
        return 0
    return _execute_deletion(will_delete, match_residue)


if __name__ == "__main__":
    raise SystemExit(main())
