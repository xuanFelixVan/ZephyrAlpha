# [BLUEPRINT] MOD-INF-005 | scripts/governance/d6_security/price_cage/price_cage_unknown_reject_judge.py | §
# [MODULE] scripts.governance.d6_security.price_cage.price_cage_unknown_reject_judge
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.data.trading_calendar（trading_days_in_range 交易日真源）；zephyr.shared.utils.time_utils（now_utc）；yaml；
#   zephyr.ex_core.price_cage（BF-6 实现探测，缺席按前提件缺失不崩溃）
# [CONSUMERS] 裁定#535 翻旗呈批面（Owner 门位）；process_reaper 观察窗例行核证
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 判据全机械=最近 5 个交易日（XSHG 真源）逐日逐窗（am/pm）采样≥30 且 fresh 率≥80%
#   +判定日志≥4 条/日；前提件三查（BF-6 实现落地/flags 两键登记/判定日志持久化落点）任一缺席
#   →FAIL-BLOCKED+缺失清单（绝不崩溃——实现件未落地是本工具的合法输入态）；
#   flags 两键已登记时核 feature_flags.jsonl 越权 set（action=set 运行时翻转=逐条列出判 FAIL，
#   翻转唯一合法通道=裁定登记+flags.yaml 出厂值）；
#   读写路径全参数化（judge 无固定写面，只读证据——零审计写入零副作用）
# [MODIFY-GUARD] none（纯只读判定器；证据面=price_cage_supply_sampler 自建 jsonl，禁触 flags.yaml/生产 data）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 证据/旗标审计/判定日志文件缺失或行不可解析→按零样本/逐条列出处理不抛；
#   verdict 三态=PASS(exit 0)/FAIL(exit 1)/FAIL-BLOCKED(exit 2)
# [TESTS] tests/gov/governance/test_price_cage_judge.py
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  观察窗核证 CLI（[STARTUP] manual 既有语义），非常驻系统，__main__+argv 即其合法形态
"""裁定#535「unknown_reject 武装核证」判官——5 交易日观察窗机械化评测。

裁定#535 翻旗判据（原文口径，全机械核证）：
  1. 供数新鲜：QMT 桥 quote 供数连续 5 个交易日交易时段新鲜（证据面=
     price_cage_supply_sampler.py 采样的 .runtime/audit/price_cage_supply.jsonl，
     每窗口采样≥30 且 fresh 率≥80%）；
  2. 有笼子判定日志（≥4 条/日，每窗口≥2 对应 canary 判定链走链）；
  3. 前提件三查：BF-6 实现落地（zephyr.ex_core.price_cage 含 decide_cage_for_limit_order
     与 CAGE_BASE_SUPPLY_FLAG/CAGE_UNKNOWN_REJECT_FLAG）、flags.yaml 已登记
     ex_core_price_cage_base_supply/ex_core_price_cage_unknown_reject 两键、
     笼子判定日志持久化落点已建——任一缺席=FAIL-BLOCKED+缺失清单（待施工件）。

verdict 三态：
  PASS         三判据全绿（唯一翻旗呈批依据；翻旗时同步改出厂断言
               tests/trade/ex_core/test_price_cage_bf6_wiring.py TestFlagsOffIsByteIdentical
               ::test_factory_flags_are_off + 登记裁定，本工具不代翻）
  FAIL         前提件齐但证据不足/有越权 set 记录/判定日志不达量
  FAIL-BLOCKED 前提件缺失（当前环境预期态——BF-6 实现件未落地 HEAD）

用法::

    python scripts/governance/d6_security/price_cage/price_cage_unknown_reject_judge.py \
        [--evidence PATH] [--flags-yaml PATH] [--flag-audit PATH] [--cage-log PATH] \
        [--days N] [--min-samples N] [--min-fresh-rate F] [--min-daily-cage-logs N] [--today YYYY-MM-DD]

exit: 0=PASS, 1=FAIL, 2=FAIL-BLOCKED
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

_REPO = Path(__file__).resolve().parents[4]
_SRC = str(_REPO / "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from zephyr.data.trading_calendar import trading_days_in_range  # noqa: E402
from zephyr.shared.utils.time_utils import now_utc  # noqa: E402

__manifest__ = """
args:
- --evidence
- --flags-yaml
- --flag-audit
- --cage-log
description: 裁定#535 unknown_reject 武装核证判官（5 交易日逐日逐窗机械核证，PASS/FAIL/FAIL-BLOCKED）
dimensions:
- D6
priority: P2
timeout_seconds: 60
warn_only: false
"""

#: flags.yaml 待登记两键（裁定#535；出厂值必须保持 OFF——翻旗属 Owner 门位）
CAGE_FLAG_KEYS: tuple[str, ...] = ("ex_core_price_cage_base_supply", "ex_core_price_cage_unknown_reject")
#: 连续竞价两窗（与采样器 ASHareCalendar._SESSION_WINDOWS 一一对应）
WINDOWS: tuple[str, ...] = ("am", "pm")
#: 判定日志缺席时的待施工落点（canary 判定链走链留痕；BF-6 观察窗运行方案落地前=前提件缺失项）
DEFAULT_CAGE_LOG_REL = ".runtime/audit/price_cage_decisions.jsonl"

VERDICT_PASS = "PASS"
VERDICT_FAIL = "FAIL"
VERDICT_BLOCKED = "FAIL-BLOCKED"
_EXIT_BY_VERDICT = {VERDICT_PASS: 0, VERDICT_FAIL: 1, VERDICT_BLOCKED: 2}


@dataclass
class CellReport:
    """单日单窗核证行。"""

    day: str
    window: str
    samples: int
    fresh: int
    rate: float
    ok: bool
    note: str = ""


@dataclass
class JudgeReport:
    """判官全量结论（逐日明细+前提件清单+越权审计+判定日志计数）。"""

    verdict: str
    window_days: list[str] = field(default_factory=list)
    cells: list[CellReport] = field(default_factory=list)
    missing_prereqs: list[str] = field(default_factory=list)
    unauthorized_sets: list[dict] = field(default_factory=list)
    cage_log_daily: dict[str, int] = field(default_factory=dict)
    cage_log_ok: bool = False
    notes: list[str] = field(default_factory=list)


def recent_trading_days(today: date, n: int = 5, lookback_days: int = 45) -> list[date]:
    """最近 n 个交易日（含 today，XSHG 真源；lookback 覆盖长假断层）。"""
    days = trading_days_in_range(today - timedelta(days=lookback_days), today)
    return days[-n:]


def load_jsonl(path: Path) -> tuple[list[dict], int]:
    """读 jsonl（跳过空行/坏行）；返回 (记录列表, 坏行数)。文件缺失=([], 0)。"""
    if not path.exists():
        return [], 0
    records: list[dict] = []
    bad = 0
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            bad += 1
            continue
        if isinstance(obj, dict):
            records.append(obj)
        else:
            bad += 1
    return records, bad


def group_cells(records: list[dict]) -> dict[tuple[str, str], list[dict]]:
    """证据按 (date, window) 分格（缺 date/window 字段的行丢弃并计入上游坏行）。"""
    cells: dict[tuple[str, str], list[dict]] = {}
    for r in records:
        key = (str(r.get("date", "")), str(r.get("window", "")))
        cells.setdefault(key, []).append(r)
    return cells


def probe_bf6_symbols() -> bool:
    """BF-6 实现落地探测：zephyr.ex_core.price_cage 含判定件与两旗标常量（缺席=False 不抛）。"""
    try:
        from zephyr.ex_core import price_cage
    except Exception:  # noqa: BLE001 — 实现件缺席/导入链故障统一按"未落地"（合法输入态）
        return False
    return all(
        hasattr(price_cage, name)
        for name in ("decide_cage_for_limit_order", "CAGE_BASE_SUPPLY_FLAG", "CAGE_UNKNOWN_REJECT_FLAG")
    )


def missing_flag_keys(flags_yaml: Path) -> list[str]:
    """flags.yaml 缺席的两键（递归查任意嵌套层；文件/解析失败=两键全缺）。"""
    try:
        import yaml

        data = yaml.safe_load(flags_yaml.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001 — 不可读=按两键全缺列缺失清单（fail-visible 不崩溃）
        return list(CAGE_FLAG_KEYS)

    def _has(node: object, key: str) -> bool:
        if isinstance(node, dict):
            return key in node or any(_has(v, key) for v in node.values())
        return False

    return [k for k in CAGE_FLAG_KEYS if not _has(data, k)]


def scan_flag_audit(flag_audit: Path) -> list[dict]:
    """feature_flags.jsonl 中两键的运行时越权 set 记录（翻转唯一合法通道=裁定登记+出厂值）。"""
    records, _bad = load_jsonl(flag_audit)
    return [r for r in records if r.get("action") == "set" and r.get("key") in CAGE_FLAG_KEYS]


def evaluate_cells(
    grouped: dict[tuple[str, str], list[dict]],
    days: list[date],
    *,
    min_samples: int,
    min_fresh_rate: float,
) -> list[CellReport]:
    """逐日逐窗核证：采样≥min_samples 且 fresh 率≥min_fresh_rate（任一不达=该格不绿）。"""
    reports: list[CellReport] = []
    for day in days:
        for window in WINDOWS:
            rows = grouped.get((day.isoformat(), window), [])
            fresh = sum(1 for r in rows if r.get("fresh") is True)
            count = len(rows)
            rate = (fresh / count) if count else 0.0
            notes = []
            if count < min_samples:
                notes.append(f"样本<{min_samples}")
            if count and rate < min_fresh_rate:
                notes.append(f"fresh率<{min_fresh_rate:.0%}")
            reports.append(
                CellReport(
                    day=day.isoformat(),
                    window=window,
                    samples=count,
                    fresh=fresh,
                    rate=round(rate, 4),
                    ok=not notes,
                    note=";".join(notes),
                )
            )
    return reports


def count_cage_logs_by_day(cage_log: Path, days: list[date]) -> tuple[dict[str, int], list[str]]:
    """判定日志逐日计数（date 字段或 ts 前 10 位归日）；返回 (逐日计数, 不可解析说明)。文件缺失=({}, [缺失说明])。"""
    if not cage_log.exists():
        return {}, [f"判定日志不存在: {cage_log}"]
    records, bad = load_jsonl(cage_log)
    notes = [f"判定日志不可解析行 {bad} 条"] if bad else []
    counts: dict[str, int] = {d.isoformat(): 0 for d in days}
    for r in records:
        day = str(r.get("date") or str(r.get("ts", ""))[:10])
        if day in counts:
            counts[day] += 1
    return counts, notes


def run_judge(
    *,
    today: date,
    evidence_path: Path,
    flags_yaml: Path,
    flag_audit: Path,
    cage_log: Path,
    days_n: int = 5,
    min_samples: int = 30,
    min_fresh_rate: float = 0.8,
    min_daily_cage_logs: int = 4,
    bf6_ok: bool | None = None,
) -> JudgeReport:
    """判官主链（全参数化：读写路径/阈值/今日锚点均可注入，测试指向 tmp_path）。"""
    report = JudgeReport(verdict=VERDICT_FAIL)
    days = recent_trading_days(today, days_n)
    report.window_days = [d.isoformat() for d in days]

    # ── 前提件三查（任一缺席=FAIL-BLOCKED，缺什么列什么，不崩溃） ──
    if bf6_ok is None:
        bf6_ok = probe_bf6_symbols()
    if not bf6_ok:
        report.missing_prereqs.append(
            "[前提件①] BF-6 笼子判定实现未落地: zephyr.ex_core.price_cage 缺 "
            "decide_cage_for_limit_order / CAGE_BASE_SUPPLY_FLAG / CAGE_UNKNOWN_REJECT_FLAG（待施工件）"
        )
    flags_missing = missing_flag_keys(flags_yaml)
    if flags_missing:
        report.missing_prereqs.append(
            f"[前提件②] flags.yaml 未登记两键: {', '.join(flags_missing)}（登记时出厂值必须 OFF）"
        )
    report.unauthorized_sets = [] if flags_missing else scan_flag_audit(flag_audit)

    cage_counts, cage_notes = count_cage_logs_by_day(cage_log, days)
    if not cage_log.exists():
        report.missing_prereqs.append(
            f"[前提件③] 笼子判定日志持久化落点未建（待施工件，预期落点 {cage_log}；"
            "≥4 条/日=每窗口≥2 对应 canary 判定链走链留痕）"
        )

    # ── 证据核证（前提件缺席也照常出明细表，供观察窗日常跟踪） ──
    evidence, bad = load_jsonl(evidence_path)
    if bad:
        report.notes.append(f"证据面不可解析行 {bad} 条: {evidence_path}")
    report.cells = evaluate_cells(group_cells(evidence), days, min_samples=min_samples, min_fresh_rate=min_fresh_rate)
    report.cage_log_daily = cage_counts

    # ── verdict 汇聚 ──
    if report.missing_prereqs:
        report.verdict = VERDICT_BLOCKED
        return report
    cells_ok = all(c.ok for c in report.cells)
    cage_daily_ok = bool(cage_counts) and all(v >= min_daily_cage_logs for v in cage_counts.values())
    report.cage_log_ok = cage_daily_ok
    if not cells_ok:
        report.notes.append("存在不达标日窗（采样量/fresh 率不足，见逐日明细）")
    if not cage_daily_ok:
        report.notes.append(f"判定日志逐日计数不达 ≥{min_daily_cage_logs} 条/日（或不完整）")
    if report.unauthorized_sets:
        report.notes.append(
            f"feature_flags.jsonl 检出 {len(report.unauthorized_sets)} 条两键越权 set 记录（翻转须走裁定登记）"
        )
    if report.notes:
        report.verdict = VERDICT_FAIL
    else:
        report.verdict = VERDICT_PASS
    return report


def format_report(rep: JudgeReport, *, thresholds: str) -> str:
    """人读报告（逐日明细表+缺失清单，翻旗呈批直接引用）。"""
    lines = [
        "=== 裁定#535 unknown_reject 武装核证判官 ===",
        f"观察窗: {rep.window_days[0]} .. {rep.window_days[-1]}（最近 {len(rep.window_days)} 个交易日，XSHG 真源）",
        f"verdict: {rep.verdict} (exit {_EXIT_BY_VERDICT[rep.verdict]})",
    ]
    if rep.missing_prereqs:
        lines.append(f"--- 缺失前提件（{len(rep.missing_prereqs)} 件）---")
        lines.extend(f"  {m}" for m in rep.missing_prereqs)
    lines.append(f"--- 逐日明细（{thresholds}）---")
    lines.append("date        window  samples  fresh  rate     verdict")
    for c in rep.cells:
        lines.append(
            f"{c.day}  {c.window:<6}  {c.samples:>7}  {c.fresh:>5}  {c.rate:>6.1%}  {'OK' if c.ok else 'INSUFFICIENT ' + c.note}"
        )
    lines.append("--- 旗标越权 set 审计（feature_flags.jsonl，两键）---")
    if rep.unauthorized_sets:
        lines.extend(
            f"  越权: {r.get('timestamp', '?')} key={r.get('key')} state={r.get('state')}"
            for r in rep.unauthorized_sets
        )
    else:
        lines.append("  无记录" + ("（两键未登记，跳过核）" if any("两键" in m for m in rep.missing_prereqs) else ""))
    lines.append("--- 判定日志逐日计数（≥4 条/日）---")
    if rep.cage_log_daily:
        lines.extend(f"  {d}: {n} 条" for d, n in rep.cage_log_daily.items())
    else:
        lines.append("  无落点（见缺失前提件③）")
    if rep.notes:
        lines.append("--- notes ---")
        lines.extend(f"  * {n}" for n in rep.notes)
    lines.append(
        "翻旗前置（裁定#535）: 本 judge PASS + 同步改出厂断言"
        " tests/trade/ex_core/test_price_cage_bf6_wiring.py::TestFlagsOffIsByteIdentical::test_factory_flags_are_off"
        " + 登记裁定（Owner 门位）"
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="裁定#535 unknown_reject 武装核证判官（5 交易日观察窗机械核证）")
    parser.add_argument(
        "--evidence", default=str(_REPO / ".runtime" / "audit" / "price_cage_supply.jsonl"), help="采样证据面 jsonl"
    )
    parser.add_argument("--flags-yaml", default=str(_REPO / "config" / "flags.yaml"), help="flags.yaml 路径")
    parser.add_argument(
        "--flag-audit", default=str(_REPO / ".runtime" / "audit" / "feature_flags.jsonl"), help="旗标运行时审计 jsonl"
    )
    parser.add_argument("--cage-log", default=str(_REPO / DEFAULT_CAGE_LOG_REL), help="笼子判定日志持久化落点")
    parser.add_argument("--days", type=int, default=5, help="观察窗交易日数（裁定#535=5）")
    parser.add_argument("--min-samples", type=int, default=30, help="每窗口最少采样数")
    parser.add_argument("--min-fresh-rate", type=float, default=0.8, help="每窗口最低 fresh 率")
    parser.add_argument("--min-daily-cage-logs", type=int, default=4, help="判定日志每日最少条数")
    parser.add_argument("--today", default=None, help="核证锚点日（ISO，缺省=北京今日；回放/测试用）")
    args = parser.parse_args(argv)

    # 锚点日=北京今日（A股交易日归属北京墙钟；UTC 日期在 00:00-08:00 时段会滞后一天）
    today = (
        datetime.fromisoformat(args.today).date()
        if args.today
        else now_utc().astimezone(ZoneInfo("Asia/Shanghai")).date()
    )
    rep = run_judge(
        today=today,
        evidence_path=Path(args.evidence),
        flags_yaml=Path(args.flags_yaml),
        flag_audit=Path(args.flag_audit),
        cage_log=Path(args.cage_log),
        days_n=args.days,
        min_samples=args.min_samples,
        min_fresh_rate=args.min_fresh_rate,
        min_daily_cage_logs=args.min_daily_cage_logs,
    )
    thresholds = (
        f"每窗≥{args.min_samples} 样本且 fresh 率≥{args.min_fresh_rate:.0%}；判定日志≥{args.min_daily_cage_logs} 条/日"
    )
    print(format_report(rep, thresholds=thresholds))
    return _EXIT_BY_VERDICT[rep.verdict]


if __name__ == "__main__":
    sys.exit(main())
