# [BLUEPRINT] MOD-INF-005 | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §性能观测
# [MODULE] scripts.governance.commit_perf_report
# [DOMAIN] D_GOV_CODE_QUALITY
# [TTL] permanent
"""提交性能与并发健康周报（GOV 治理-效率关联指标体系，2026-09-13 并发调查批 P1 落地）。

数据真源：
- git log（近 N 小时提交构成：正式/reconciler 收编/派生收敛/integrity 后注册）
- .runtime/audit/hook_tracked_drift.jsonl（gate 窗口竞态事件）
- .runtime/audit/worktree_drift_watchdog.jsonl（派生漂移）

输出指标（docs/_working/2026-09-13-concurrency-commit-perf-study.md §2.5）：
- 正式提交占比（健康阈值 ≥70%）
- 机器伴生比（≤30%）
- 竞态窗口事件数/日（≤4/日 为绿，>4 黄，>50 红）
- watchdog 漂移条数

判定（B2 2026-09-16）：judge_dimensions 四维度判级 + aggregate_verdict 与门聚合
（任一红→红，任一黄→黄）。病根：旧公式只看正式占比/机器伴生比，竞态 211/日
时总体判定仍输出"绿"。

用法：python scripts/governance/commit_perf_report.py [--hours 24]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
DRIFT_JSONL = _REPO / ".runtime/audit/hook_tracked_drift.jsonl"
WATCHDOG_JSONL = _REPO / ".runtime/audit/worktree_drift_watchdog.jsonl"


def _classify_log_line(subject: str) -> str:
    """_classify_log_line implementation."""
    if subject.startswith("chore(reconciler)"):
        return "机器伴生:reconciler 收编"
    if subject.startswith("chore(integrity)"):
        return "机器伴生:integrity 后注册"
    if subject.startswith("chore(derived)"):
        return "机器伴生:派生缓存收敛"
    return "正式提交"


def commit_mix(hours: int) -> tuple[Counter, int]:
    """commit_mix implementation."""
    since = (datetime.now(timezone.utc) - timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%S")
    r = subprocess.run(
        ["git", "log", f"--since={since}", "--format=%s"],
        capture_output=True, text=True, encoding="utf-8", errors="ignore",
        cwd=str(_REPO),
    )
    mix: Counter = Counter()
    subjects = [s for s in r.stdout.splitlines() if s.strip()]
    for s in subjects:
        mix[_classify_log_line(s)] += 1
    return mix, len(subjects)


def drift_events(hours: int, path: Path | None = None) -> int:
    """统计竞态窗口事件数（近 hours 小时）。

    path=None 走生产真源 DRIFT_JSONL；显式传 path 供测试 tmp_path 隔离。
    """
    p = DRIFT_JSONL if path is None else path
    if not p.exists():
        return 0
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    n = 0
    for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
        try:
            ev = json.loads(line)
            ts = datetime.fromisoformat(ev["timestamp"])
            if ts >= cutoff:
                n += 1
        except Exception:  # noqa: BLE001 — 单行坏数据跳过
            continue
    return n


def watchdog_rows() -> int:
    """watchdog_rows implementation."""
    if not WATCHDOG_JSONL.exists():
        return 0
    return sum(1 for _ in WATCHDOG_JSONL.open(encoding="utf-8", errors="ignore"))


def block_events(hours: int, path: Path | None = None) -> list[dict]:
    """堵点溯源事件（commit_block_events.jsonl——阈值化记录，仅异常才写）。

    溯源链路（2026-09-13 极限红蓝对抗 D5）：异常发生 → jsonl 留痕（session/门禁/
    文件数/耗时）→ 本报表聚合 → 按图索骥修复 → 红蓝验证。
    两类事件：commit_blocked（gate 链阻断，含 gate_chain_ms 白跑耗时）+
    commit_slow（成功但全程墙钟超 60s 阈值，含 total_ms——慢而未阻的堵点画像）。

    path=None 走生产真源；显式传 path 供测试 tmp_path 隔离。
    """
    p = _REPO / ".runtime" / "audit" / "commit_block_events.jsonl" if path is None else path
    if not p.exists():
        return []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    rows: list[dict] = []
    for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
        try:
            ev = json.loads(line)
            if datetime.fromisoformat(ev["timestamp"]) >= cutoff:
                rows.append(ev)
        except Exception:  # noqa: BLE001 — 单行坏数据跳过
            continue
    return rows


def _per_day(n: int | float, hours: int) -> float:
    """窗口计数折算为日均（<24h 按 1 日计，防小窗放大误判）。

    B2 病根场景：48h 窗口 211 事件若直接对标 ≤4/日 阈值会漏判——必须先折算
    105.5/日 再判级。
    """
    days = hours / 24 if hours >= 24 else 1.0
    return n / days


def judge_dimensions(
    formal_ratio: float,
    machine_ratio: float,
    race_per_day: float,
    blocks_per_day: float,
) -> list[tuple[str, str, str]]:
    """四维度判级，返回 [(维度名, 判级, 阈值说明)]。

    - 正式占比 ≥70 绿（否则黄）
    - 机器伴生 ≤30 绿（否则黄）
    - 竞态 ≤4 绿 / >4 黄 / >50 红
    - 堵点 ≤100 绿（否则黄）
    """
    rows: list[tuple[str, str, str]] = [
        ("正式提交占比", "绿" if formal_ratio >= 70 else "黄", f"≥70% 绿（当前 {formal_ratio}%）"),
        ("机器伴生比", "绿" if machine_ratio <= 30 else "黄", f"≤30% 绿（当前 {machine_ratio}%）"),
    ]
    if race_per_day > 50:
        race_verdict = "红"
    elif race_per_day > 4:
        race_verdict = "黄"
    else:
        race_verdict = "绿"
    rows.append(("竞态窗口", race_verdict, f"≤4/日 绿·>4 黄·>50 红（当前 {race_per_day}/日）"))
    rows.append(("堵点事件", "绿" if blocks_per_day <= 100 else "黄", f"≤100/日 绿（当前 {blocks_per_day}/日）"))
    return rows


def aggregate_verdict(rows: list[tuple[str, str, str]]) -> str:
    """与门聚合：任一红→红；任一黄→黄；全绿→绿。"""
    values = [v for _, v, _ in rows]
    if "红" in values:
        return "红"
    if "黄" in values:
        return "黄"
    return "绿"


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="提交性能与并发健康报表")
    parser.add_argument("--hours", type=int, default=24, help="统计窗口（小时）")
    args = parser.parse_args()

    mix, total = commit_mix(args.hours)
    formal = mix.get("正式提交", 0)
    machine = total - formal
    formal_ratio = formal * 100 // total if total else 0
    machine_ratio = machine * 100 // total if total else 0
    drift_n = drift_events(args.hours)
    wd = watchdog_rows()
    race_per_day = _per_day(drift_n, args.hours)

    print(f"=== 提交性能与并发健康报表（近 {args.hours}h）===")
    print(f"总提交: {total}")
    for k, v in mix.most_common():
        print(f"  {k}: {v}")
    print(f"正式提交占比: {formal_ratio}%  (健康阈值 ≥70%)")
    print(f"机器伴生比:   {machine_ratio}%  (健康阈值 ≤30%)")
    print(f"竞态窗口事件: {drift_n}（{race_per_day}/日，阈值 ≤4 绿·>4 黄·>50 红）")
    print(f"watchdog 漂移: {wd} 条（累计）")

    # 堵点溯源（D5）：阻断事件 TOP 门禁聚合
    events = block_events(args.hours)
    blocks = [ev for ev in events if ev.get("event") == "commit_blocked"]
    slows = [ev for ev in events if ev.get("event") == "commit_slow"]
    if blocks:
        print(f"\n堵点事件（gate 链阻断）: {len(blocks)} 次")
        gate_counter: Counter = Counter(ev.get("gate_id", "?") for ev in blocks)
        for gate_id, n in gate_counter.most_common(5):
            wastes = [ev.get("gate_chain_ms", 0) for ev in blocks if ev.get("gate_id") == gate_id]
            print(f"  {gate_id}: {n} 次（门禁链耗时 P50={sorted(wastes)[len(wastes)//2]/1000:.0f}s 累计白跑 {sum(wastes)/1000:.0f}s）")
    else:
        print("\n堵点事件（gate 链阻断）: 0 次")
    if slows:
        totals = sorted(ev.get("total_ms", 0) for ev in slows)
        print(f"慢提交（成功但超 60s 阈值）: {len(slows)} 次（P50={totals[len(totals)//2]/1000:.0f}s 最长 {totals[-1]/1000:.0f}s）")
        for ev in slows[-5:]:  # 最近 5 笔
            print(f"  [{ev.get('timestamp','')[:19]}] {ev.get('session_id','?')} {ev.get('files_count',0)} 文件 {ev.get('total_ms',0)/1000:.0f}s")

    # B2 四维判级 + 与门聚合（病根：竞态 211/日时旧公式只看占比仍输出"绿"）
    blocks_per_day = _per_day(len(blocks), args.hours)
    rows = judge_dimensions(formal_ratio, machine_ratio, race_per_day, blocks_per_day)
    print("判定（逐维度）:")
    for _name, _v, _note in rows:
        print(f"  {_name}: {_v}（{_note}）")
    verdict = aggregate_verdict(rows)
    print("总体判定:", verdict)
    if verdict != "绿":
        print("  （竞速伴生偏高——优先排查高频小提交与生成器窗口并发；竞态红=并发窗口治理优先级最高）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
