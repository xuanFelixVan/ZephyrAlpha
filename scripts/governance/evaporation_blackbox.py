# [BLUEPRINT] MOD-GOV | docs/_working/decision_map_campaign/15_evaporation_cure_plan.md | 治本施工项 EV-01 行（取证依据=10 号文）
# [MODULE] scripts.governance.evaporation_blackbox
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance._shared.constants, scripts.governance._shared.encoding
# [CONSUMERS] schtasks ZephyrAlpha_EvaporationBlackbox（每 5 分钟）; Owner 手动 --restore 取证
# [STARTUP] scheduled_task
# [MATURITY] testing
# [INVARIANTS] 快照对 git 只读（write-tree 仅向对象库新增不可变对象，零 reset/clean/checkout/index 改写）；
#              追加式 JSONL fail-soft（任何 git 失败也写 error 记录，禁中断）；>50MB 轮转 .1 只留一代；
#              --restore 只打印人工恢复指引绝不自动执行（防二次事故）；
#              防御性快照非 reconciler，不违宪法 §9.3 事件触发律（15 号文 EV-01 行 Owner 批明示）。
# [MODIFY-GUARD] 快照字段清单增删须与 15 号文 EV-01 验收行对齐（index tree/untracked 计数/stash/reflog 尾巴）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] snapshot 模式永不因 git 失败非零退出（fail-soft 落 error 记录，exit 0；仅当 error 记录也写不进时 exit 2）；
#                  --restore 命中 exit 0 / 未命中或黑匣子缺失 exit 1
# [TESTS] none
# [A_module] module_id=EV-01 | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
#            （正式 MOD 编号由落地车道随批登记 depgraph 后回填）
# [TTL] permanent
"""evaporation_blackbox.py — 主仓蒸发黑匣子（行车记录仪，15 号文 EV-01）。

背景：2026-09-24 凌晨主区四起同族蒸发（untracked 全灭 + index 567→9），clean -fd 天然
零 reflog 痕迹，事后无法把凶手钉死到分钟（10 号文 §③）。本哨兵每 5 分钟向
.runtime/evaporation_blackbox/blackbox.jsonl 追加一行只读快照，把"静默"变"有声"，
下次蒸发即可二分定位到分钟级现场（15 号文 EV-01 验收行）。

每行 JSON（UTF-8）字段：
    ts            快照时刻（UTC ISO-8601 带时区）
    ts_local      本地时区可读时刻（10 号文时间线口径）
    head_sha      git rev-parse HEAD（全量 sha）
    branch        当前分支名
    index_tree    git write-tree 得到的 staged tree hash（经 subprocess 只读调用；
                  仅向 .git/objects 追加不可变对象，不改 index/工作区）
    untracked_count   git status --porcelain 中 "??" 行数
    modified_count    其余 porcelain 行数（tracked 侧改动/暂存）
    porcelain_total   porcelain 总行数（对账冗余字段）
    stash_list    git stash list 行数（stash 消失本身也是线索，10 号文 §⑤）
    stash_entries git stash list 原始行（抢救链证据）
    reflog_tail_1 git reflog -1 原始行（短哈希+主题）
    error         （仅异常时）字段级 git 失败原因；fail-soft 不断链

Usage:
    python scripts/governance/evaporation_blackbox.py                 # 快照一次（schtasks 载体）
    python scripts/governance/evaporation_blackbox.py --restore "2026-09-25 03:47"   # 打印当时状态清单+丢失窗口
    python scripts/governance/evaporation_blackbox.py --restore 2026-09-25T03:47:30  # 同上（ISO 亦可）
"""

from __future__ import annotations

# noqa: m11-perm-manual-legitimate  M11豁免: ZephyrAlpha_EvaporationBlackbox 计划任务每 5 分钟系统级调度触发，非人工手动常驻
import argparse
import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.encoding import ensure_utf8_stdout  # noqa: E402

# REPO_ROOT 真源=_shared.constants（re-export zephyr.shared.io.paths）。黑匣子必须在
# 主包自身损坏时仍能工作——这正是它的值班场景——故真源导入失败时降级为路径回溯推导，
# 并照常 fail-soft（本模块 INVARIANTS 优先于真源收敛约定的例外，已在此声明）。
try:
    from _shared.constants import REPO_ROOT  # noqa: E402
except Exception:  # pragma: no cover - 降级通道  # noqa: BLE001  黑匣子值班场景主包自身损坏仍须工作——INVARIANTS 已声明例外（降级路径回溯）
    REPO_ROOT = _SCRIPT_DIR.parents[2]

BLACKBOX_DIR: Path = REPO_ROOT / ".runtime" / "evaporation_blackbox"
BLACKBOX_FILE: Path = BLACKBOX_DIR / "blackbox.jsonl"
ROTATE_SUFFIX: str = ".1"
MAX_BYTES: int = 50 * 1024 * 1024  # 保留策略：>50MB 轮转，只留一代
try:
    from _shared.thresholds import get as _get_threshold  # noqa: E402  阈值SSoT(ARCH-036 P3-A5)
except ImportError:  # pragma: no cover - 降级通道（与 REPO_ROOT 降级同口径，值班场景真源不可达仍需工作）

    def _get_threshold(key: str, default=None):  # type: ignore[misc]
        return default


def _threshold_or(key: str, default: int) -> int:
    """阈值 SSoT fail-soft 读取：真源缺失/损坏一律回落默认（值班不可断，同 REPO_ROOT 降级先例）。"""
    try:
        return int(_get_threshold(key, default))
    except Exception:  # noqa: BLE001  真源损坏按默认值班——本件 INVARIANTS 已声明优先于真源收敛约定
        return default


GIT_TIMEOUT_SEC = _threshold_or("git_operations.evaporation_blackbox_git_timeout_seconds", 30)

# --restore 接受的时刻格式（均按本地时区解读；秒/时区缺省时向下兼容）
_RESTORE_TS_FORMATS: tuple[str, ...] = (
    "%Y-%m-%dT%H:%M:%S%z",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M",
    "%Y-%m-%d",
)


def _git(args: list[str]) -> subprocess.CompletedProcess[str]:
    """只读调用 git（-C 钉死主仓，免 cwd 依赖）。不 raise，由调用方判 returncode。"""
    return subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=GIT_TIMEOUT_SEC,
    )


def _git_ok(args: list[str]) -> str:
    """git 调用成功则回 stdout，失败抛 RuntimeError（由 _snapshot 字段级捕获）。"""
    proc = _git(args)
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip().splitlines()
        raise RuntimeError(f"git {' '.join(args)} rc={proc.returncode}: {detail[-1] if detail else 'no output'}")
    return (proc.stdout or "").strip()


def _snapshot() -> dict[str, Any]:
    """构建一行快照记录。任何单字段 git 失败都降级为该字段 error 说明，绝不中断。"""
    now = datetime.now(UTC)
    record: dict[str, Any] = {
        "ts": now.isoformat(timespec="milliseconds"),
        "ts_local": now.astimezone().isoformat(timespec="seconds"),
    }
    try:
        record["branch"] = _git_ok(["rev-parse", "--abbrev-ref", "HEAD"])
    except Exception as exc:  # noqa: BLE001  快照逐字段取证 fail-soft：单腿失败降级记 _error 字段，禁盲抛中断值班
        record["branch_error"] = str(exc)
    try:
        record["head_sha"] = _git_ok(["rev-parse", "HEAD"])
    except Exception as exc:  # noqa: BLE001  快照逐字段取证 fail-soft：单腿失败降级记 _error 字段，禁盲抛中断值班
        record["head_sha_error"] = str(exc)
    try:
        # write-tree：把当前 index 固化为 tree 对象（仅对象库追加，不可变、零工作区影响）。
        record["index_tree"] = _git_ok(["write-tree"])
    except Exception as exc:  # noqa: BLE001  快照逐字段取证 fail-soft：单腿失败降级记 _error 字段，禁盲抛中断值班
        record["index_tree_error"] = str(exc)
    try:
        lines = [ln for ln in _git_ok(["status", "--porcelain"]).splitlines() if ln.strip()]
        record["untracked_count"] = sum(1 for ln in lines if ln.startswith("??"))
        record["modified_count"] = len(lines) - record["untracked_count"]
        record["porcelain_total"] = len(lines)
    except Exception as exc:  # noqa: BLE001  快照逐字段取证 fail-soft：单腿失败降级记 _error 字段，禁盲抛中断值班
        record["untracked_count_error"] = str(exc)
    try:
        stash_lines = [ln for ln in _git_ok(["stash", "list"]).splitlines() if ln.strip()]
        record["stash_list"] = len(stash_lines)
        record["stash_entries"] = stash_lines
    except Exception as exc:  # noqa: BLE001  快照逐字段取证 fail-soft：单腿失败降级记 _error 字段，禁盲抛中断值班
        record["stash_list_error"] = str(exc)
    try:
        record["reflog_tail_1"] = _git_ok(["reflog", "-1"])
    except Exception as exc:  # noqa: BLE001  快照逐字段取证 fail-soft：单腿失败降级记 _error 字段，禁盲抛中断值班
        record["reflog_tail_1_error"] = str(exc)
    errors = {k: v for k, v in record.items() if k.endswith("_error")}
    if len(errors) >= 5:  # 全线失败（如 git 不可用/不是仓库）→ 顶层 error 记录
        record["error"] = f"snapshot fully degraded: {errors}"
    return record


def _rotate_if_needed() -> str | None:
    """保留策略：blackbox.jsonl >50MB 时轮转改名 .1（覆盖旧 .1，只留一代）。"""
    if not BLACKBOX_FILE.exists() or BLACKBOX_FILE.stat().st_size <= MAX_BYTES:
        return None
    rotated = BLACKBOX_FILE.with_name(BLACKBOX_FILE.name + ROTATE_SUFFIX)
    os.replace(BLACKBOX_FILE, rotated)  # os.replace 原子覆盖旧 .1
    return str(rotated)


def _append_record(record: dict[str, Any]) -> None:
    """向黑匣子追加一行 JSON（UTF-8、追加式、ensure_ascii=False 保可读）。"""
    BLACKBOX_DIR.mkdir(parents=True, exist_ok=True)
    rotated = _rotate_if_needed()
    with open(BLACKBOX_FILE, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    if rotated:
        print(f"[blackbox] rotated: {BLACKBOX_FILE.name} -> {Path(rotated).name} (>50MB, 留一代)")


def _load_records() -> list[dict[str, Any]]:
    """读回全部黑匣子行（坏行跳过，fail-soft）。"""
    if not BLACKBOX_FILE.exists():
        return []
    records: list[dict[str, Any]] = []
    with open(BLACKBOX_FILE, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records


def _parse_restore_ts(arg: str) -> datetime | None:
    """解析 --restore 时刻参数（本地时区口径；ISO 带时区则尊重其时区）。"""
    arg = arg.strip()
    for fmt in _RESTORE_TS_FORMATS:
        try:
            dt = datetime.strptime(arg, fmt)
            return dt if dt.tzinfo else dt.astimezone()
        except ValueError:
            continue
    try:  # 直接匹配黑匣子存储的 UTC ISO 字符串（含毫秒/时区）
        return datetime.fromisoformat(arg)
    except ValueError:
        return None


def _fmt_state(rec: dict[str, Any]) -> str:
    parts = [
        f"ts={rec.get('ts', '?')}",
        f"local={rec.get('ts_local', '?')}",
        f"branch={rec.get('branch', '?')}",
        f"head={str(rec.get('head_sha', '?'))[:12]}",
        f"index_tree={rec.get('index_tree', '?')}",
        f"untracked={rec.get('untracked_count', '?')}",
        f"modified={rec.get('modified_count', '?')}",
        f"stash={rec.get('stash_list', '?')}",
    ]
    return " ".join(parts)


def _pick_snapshot(
    records: list[dict[str, Any]], ts_arg: str, target: datetime
) -> tuple[int, dict[str, Any], dict[str, Any] | None]:
    """定位"当时"快照：精确命中（含毫秒串全等）优先，否则 target 之前最近一条。

    Returns:
        (idx, rec, prev)——idx 为命中行下标，prev 为上一快照（首行时 None）。
    """
    idx = next((i for i, r in enumerate(records) if r.get("ts") == ts_arg.strip()), None)
    if idx is None:
        candidates = [i for i, r in enumerate(records) if _rec_ts(r) is not None and _rec_ts(r) <= target]
        idx = candidates[-1] if candidates else 0
    rec = records[idx]
    prev = records[idx - 1] if idx > 0 else None
    return idx, rec, prev


def _print_state_section(rec: dict[str, Any], idx: int, total: int) -> None:
    """打印"当时状态清单"段（命中行全字段+stash+字段异常清单）。"""
    print("=" * 72)
    print(f"[blackbox] 当时状态清单（黑匣子第 {idx + 1}/{total} 行）")
    print("=" * 72)
    print(f"  {_fmt_state(rec)}")
    print(f"  reflog_tail_1 = {rec.get('reflog_tail_1', '?')}")
    for entry in rec.get("stash_entries", []):
        print(f"  stash: {entry}")
    for key in sorted(k for k in rec if k.endswith("_error")):
        print(f"  [字段异常] {key} = {rec[key]}")


def _print_diff_section(prev: dict[str, Any], rec: dict[str, Any]) -> None:
    """打印与上一快照的差分段（丢失窗口线索：计数 Δ/HEAD/tree 换代/疑似蒸发窗口）。"""
    print("-" * 72)
    print("[blackbox] 与上一快照差分（丢失窗口线索）")
    print(f"  上一条: {_fmt_state(prev)}")
    for field in ("untracked_count", "modified_count", "porcelain_total", "stash_list"):
        if isinstance(prev.get(field), int) and isinstance(rec.get(field), int):
            delta = rec[field] - prev[field]
            mark = "  <-- 疑似蒸发" if delta < 0 else ""
            print(f"  {field}: {prev[field]} -> {rec[field]} (Δ{delta}){mark}")
        if prev.get("head_sha") != rec.get("head_sha"):
            print(f"  head_sha: {str(prev.get('head_sha'))[:12]} -> {str(rec.get('head_sha'))[:12]}")
        if prev.get("index_tree") != rec.get("index_tree"):
            print(f"  index_tree: {prev.get('index_tree')} -> {rec.get('index_tree')}")
    if any(
        isinstance(prev.get(f), int) and isinstance(rec.get(f), int) and rec[f] < prev[f]
        for f in ("untracked_count", "modified_count", "stash_list")
    ):
        print(f"  >>> 疑似蒸发窗口: {prev.get('ts_local')} ~ {rec.get('ts_local')}（本地时间）")


def _print_restore_guidance(rec: dict[str, Any]) -> None:
    """打印人工恢复指引段（只打印不执行——防二次事故）。"""
    print("-" * 72)
    print("[blackbox] 人工恢复指引（以下命令仅供人工确认后手动执行，本脚本绝不自动执行）：")
    head_sha = str(rec.get("head_sha"))[:12]
    head_short = str(rec.get("head_sha"))[:10]
    tree = rec.get("index_tree")
    print(f"  1. 当时 HEAD 在 {head_sha}——`git reflog --date=iso | grep {head_short}` 核对去向；")
    print(f"  2. 当时暂存内容固化为 tree {tree}——`git ls-tree -r {tree} --name-only` 先查看，")
    print(f"     确需整体回置 index 时 `git read-tree {tree}`（会改写 index，务必人工确认）；")
    print("  3. untracked 内容本体不存于黑匣子（只记计数）——对照 .runtime/quarantine/ 漂移存证与 G:/backup 备份链；")
    print("  4. stash 数量对比当前 `git stash list`——stash 消失本身也是线索（10 号文 §⑤）。")


def _print_restore(ts_arg: str) -> int:
    """--restore：打印当时状态清单 + 与上一快照的差分（丢失窗口）+ 人工恢复指引。

    只打印、不执行任何恢复动作（防二次事故）。
    """
    records = _load_records()
    if not records:
        print(f"[blackbox] 黑匣子不存在或为空: {BLACKBOX_FILE}")
        return 1
    target = _parse_restore_ts(ts_arg)
    if target is None:
        print(f"[blackbox] 无法解析时刻参数: {ts_arg!r}（可用格式: 2026-09-25 03:47 / ISO8601）")
        return 1
    idx, rec, prev = _pick_snapshot(records, ts_arg, target)
    _print_state_section(rec, idx, len(records))
    if prev is not None:
        _print_diff_section(prev, rec)
    else:
        print("[blackbox] 本行即黑匣子首行，无上一快照可比。")
    _print_restore_guidance(rec)
    return 0


def _rec_ts(rec: dict[str, Any]) -> datetime | None:
    try:
        return datetime.fromisoformat(str(rec.get("ts")))
    except (TypeError, ValueError):
        return None


def main(argv: list[str] | None = None) -> int:
    ensure_utf8_stdout()
    parser = argparse.ArgumentParser(description="主仓蒸发黑匣子：只读快照 + 人工取证视图（15 号文 EV-01）")
    parser.add_argument(
        "--restore", metavar="TS", help="打印该时刻（含其前最近一次快照）的状态清单与丢失窗口，不自动恢复"
    )
    args = parser.parse_args(argv)

    if args.restore:
        return _print_restore(args.restore)

    try:
        record = _snapshot()
        _append_record(record)
    except Exception as exc:  # 连写记录都失败——仅此一处允许非零退出  # noqa: BLE001  写记录失败即值班失效——唯一允许非零退出的 FATAL 路径
        print(f"[blackbox] FATAL: 快照记录写入失败: {exc}", file=sys.stderr)
        return 2
    fields = (
        f"head={str(record.get('head_sha', '?'))[:12]}",
        f"tree={record.get('index_tree', '?')}",
        f"untracked={record.get('untracked_count', '?')}",
        f"modified={record.get('modified_count', '?')}",
        f"stash={record.get('stash_list', '?')}",
    )
    if "error" in record:
        print(f"[blackbox] {record['ts']} ERROR-RECORD {' '.join(fields)}")
    else:
        print(f"[blackbox] {record['ts']} ok {' '.join(fields)}")
    return 0


if __name__ == "__main__":  # noqa: m11-perm-manual-legitimate  ZephyrAlpha_EvaporationBlackbox 计划任务每 5 分钟系统级调度触发，非人工手动
    sys.exit(main())
