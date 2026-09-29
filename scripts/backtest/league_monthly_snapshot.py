# [BLUEPRINT] MOD-AUTO-L11-SNAPSHOT | docs/_working/fullflow_mining/03_promotion_ab/02_ab_league.md | 第1节
# [MODULE] scripts.backtest.league_monthly_snapshot
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_reader; scripts.backtest.league_registry; zephyr.shared.io.file_utils
# [CONSUMERS] Owner 终审门（6 个月终审的历史留档证据）; 交接/晨报（月度对比引用）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 只留档不判胜负——快照只组装对比表，任何冠军/淘汰判定都归 6 个月终审（Owner 门）;
#   快照表组装=纯函数（parse/summary/render 直喷可测）;
#   CH 不可达→组段落降级记缺口（不硬造成绩）;
#   测试零 CH 触碰（CH 函数全 monkeypatch）
# [MODIFY-GUARD] none（只写 data/backtest_artifacts/league/snapshot-YYYYMM.md 新月度文件）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 注册表缺失→FileNotFoundError 上抛; CH 断供→快照记缺口不抛
# [TESTS] tests/backtest/test_league_archive.py（TestParsePocketTsv/TestMemberSummary/TestRenderSnapshot 类）
# [A_module] module_id=MOD-AUTO-L11-SNAPSHOT | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""league_monthly_snapshot — A/B 联赛月度对比快照（TC-11 件1，裁定#392 批）。

sim_pocket_daily 按组拉成员 equity 序列 → 组内对比表 → data/backtest_artifacts/league/
snapshot-YYYYMM.md。只留档不判胜负：月度快照是终审的历史证据链，冠军/淘汰判定一次性归
首组满窗后的 6 个月终审（promotion_combo_gate+Owner 门，见 league_registry.review_policy）。

用法（仓库根，Python 3.12）：
    python scripts/backtest/league_monthly_snapshot.py                 # 当月快照
    python scripts/backtest/league_monthly_snapshot.py --month 2026-09 # 指定月
    python scripts/backtest/league_monthly_snapshot.py --dry-run       # 只打印不落盘
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
for _p in (str(_PROJECT_ROOT), str(_PROJECT_ROOT / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from zephyr.shared.io.file_utils import content_sha256, safe_write_text  # noqa: E402
from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402  SSOT
from zephyr.shared.utils.time_utils import now_utc, now_utc_str  # noqa: E402

# noqa: m11-perm-manual-legitimate  M11豁免: 联赛月度留档的按需快照工具（月度手动/排班触发），非自动触发常驻

SNAPSHOT_DIR = REPO_ROOT / "data" / "backtest_artifacts" / "league"
POCKET_TABLE = "c1_backtest.sim_pocket_daily"
# §5.160.2 SQL 集中化：成员月度 equity 序列只读查询模板（POCKET_TABLE/where 运行时注入）
_SQL_MEMBER_EQUITY_TS = "SELECT trade_date, equity FROM {POCKET_TABLE} WHERE {where} ORDER BY trade_date ASC"


def parse_pocket_tsv(tsv: str) -> list[dict]:
    """ch_reader TSV（trade_date/equity 行）→ [{"trade_date", "equity"}]；空/坏行/表头行跳过（纯函数）。

    ch_reader.query 实测返回无表头 TSV；兼容带表头形态（表头第二列非数值自然被跳过）。
    """
    out: list[dict] = []
    for ln in (tsv or "").strip().splitlines():
        if not ln.strip():
            continue
        parts = ln.split("\t")
        if len(parts) < 2:
            continue
        try:
            out.append({"trade_date": parts[0].strip(), "equity": float(parts[1])})
        except ValueError:
            continue  # 表头行或坏行
    return out


def max_drawdown(equities: list[float]) -> float | None:
    """区间最大回撤（<2 点=None；纯函数，与 promotion_combo_gate 同口径）。"""
    if len(equities) < 2:
        return None
    peak = equities[0]
    worst = 0.0
    for v in equities:
        peak = max(peak, v)
        if peak > 0:
            worst = max(worst, (peak - v) / peak)
    return worst


def member_summary(rows: list[dict]) -> dict:
    """单成员月度汇总（纯函数）：首末权益+月收益+最大回撤+交易日数；空行=空汇总。"""
    if not rows:
        return {"days": 0, "start_equity": None, "end_equity": None, "monthly_return": None, "max_drawdown": None}
    eq = [r["equity"] for r in rows]
    start, end = eq[0], eq[-1]
    ret = (end - start) / start if start else None
    return {
        "days": len(eq),
        "start_equity": start,
        "end_equity": end,
        "monthly_return": ret,
        "max_drawdown": max_drawdown(eq),
    }


def _esc(s: str) -> str:
    """SQL 字面量防御性净化（registry 来源仍不拼裸引号）。"""
    return str(s).replace("'", "").replace("\\", "")


def fetch_member_rows(strategy_id: str, month: str) -> list[dict] | None:
    """拉单成员当月 equity 序列；CH 不可达→None（区别于空月=[]）。"""
    try:
        from zephyr.data.ch_reader import query  # noqa: PLC0415

        where = f"strategy_id = '{_esc(strategy_id)}' AND toStartOfMonth(trade_date) = toDate('{month}-01')"
        # 真源列名=equity（DESCRIBE 实核；表内另有 initial_capital/cash/position_value）
        tsv = query(_SQL_MEMBER_EQUITY_TS.format(POCKET_TABLE=POCKET_TABLE, where=where))
    except Exception:  # noqa: BLE001 — CH 断连/模块缺失统一降级
        return None
    if tsv is None:
        return None
    return parse_pocket_tsv(tsv)


def render_group_section(group: dict, month: str, summaries: dict[str, dict | None]) -> str:
    """组段落渲染（纯函数）。summaries：member→summary dict；CH 断供成员=None。"""
    gid = group.get("group_id")
    lines = [f"## 组 {gid}（{group.get('name_zh') or ''}｜status={group.get('status')}）", ""]
    members = group.get("members") or []
    if not members:
        lines.append("- 组内暂无成员入组（league_registry.yaml members 待回填）。")
        lines.append("")
        return "\n".join(lines)
    lines += [
        "| 成员 | 交易日数 | 期初权益 | 期末权益 | 月收益 | 最大回撤 |",
        "|------|---------|---------|---------|--------|----------|",
    ]
    for sid in members:
        s = summaries.get(str(sid))
        if s is None:
            lines.append(f"| {sid} | CH 缺口 | - | - | - | - |")
        elif s["days"] == 0:
            lines.append(f"| {sid} | 0 | - | - | - | - |")
        else:
            ret = f"{s['monthly_return']:.4%}" if s["monthly_return"] is not None else "-"
            dd = f"{s['max_drawdown']:.4%}" if s["max_drawdown"] is not None else "-"
            lines.append(f"| {sid} | {s['days']} | {s['start_equity']:.2f} | {s['end_equity']:.2f} | {ret} | {dd} |")
    lines.append("")
    return "\n".join(lines)


def render_snapshot(data: dict, groups: list[dict], month: str) -> str:
    """整篇快照渲染（纯函数）。data：group_id→{member: summary|None}。"""
    lines = [
        f"# A/B 联赛月度快照 {month}",
        "",
        f"- 生成: {now_utc_str()}（机生禁手改）",
        "- 口径: sim_pocket_daily 成员 equity 序列；**只留档不判胜负**——"
        "冠军/淘汰判定一次性归 6 个月终审（league_registry.review_policy）。",
        f"- 组数: {len(groups)}",
        "",
    ]
    for g in groups:
        lines.append(render_group_section(g, month, (data.get(str(g.get("group_id"))) or {})))
    return "\n".join(lines)


def snapshot_path(month: str, snapshot_dir: Path | str = SNAPSHOT_DIR) -> Path:
    """快照落盘路径 snapshot-YYYYMM.md（纯函数）。"""
    return Path(snapshot_dir) / f"snapshot-{month.replace('-', '')}.md"


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    ap = argparse.ArgumentParser(description="A/B 联赛月度对比快照（只留档不判胜负）")
    ap.add_argument("--month", type=str, default=None, help="YYYY-MM（缺省当月）")
    ap.add_argument("--registry", type=str, default=None)
    ap.add_argument("--snapshot-dir", type=str, default=None)
    ap.add_argument("--dry-run", action="store_true", help="只打印不落盘")
    args = ap.parse_args()

    from league_registry import load_registry  # noqa: PLC0415

    reg_path = Path(args.registry) if args.registry else None
    registry = load_registry(reg_path) if reg_path else load_registry()
    groups = registry.get("groups") or []
    month = args.month or now_utc().strftime("%Y-%m")

    data: dict[str, dict[str, dict | None]] = {}
    for g in groups:
        gid = str(g.get("group_id"))
        data[gid] = {}
        for sid in g.get("members") or []:
            rows = fetch_member_rows(str(sid), month)
            data[gid][str(sid)] = None if rows is None else member_summary(rows)

    report = render_snapshot(data, groups, month)
    if args.dry_run:
        print(report)
        return 0
    out = snapshot_path(month, Path(args.snapshot_dir) if args.snapshot_dir else SNAPSHOT_DIR)
    out.parent.mkdir(parents=True, exist_ok=True)
    expected = content_sha256(out.read_text(encoding="utf-8")) if out.exists() else None
    safe_write_text(out, report, expected_base_sha256=expected)
    print(f"ok snapshot={out} groups={len(groups)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
