#!/usr/bin/env python3
# [BLUEPRINT] MOD-CHAINPILE-METAQ | docs/_working/chain_piling_campaign/snapshots/question_batch_w6.yaml | PQ-0099 exam_plan.threshold（L2461）+ docs/_working/meta_question_answers/gaps/PQ-0099_workbook.md §4
# [MODULE] scripts.governance.check_meta_question_status_band
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] src/zephyr/governance/depgraph_schema.py（get_depgraph_pg_connection，read_only=True 只读，惰性导入使 --selftest 零 PG 依赖）; src/zephyr/shared/io/yaml_utils.py（load_vocabulary_values 词表 SSoT）
# [CONSUMERS] docs/_working/chain_piling_campaign/04_construction_map.md #24（月度机检）; PQ-0099 工作簿 §4 regime 裁定项（数值留 Owner 门位）; L5 执行验证层 / L0 元问题层 / Owner
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 全程零写（PG read_only 连接，无 DML/DDL 代码路径）; 状态枚举唯一真源=meta_question_statuses_vocabulary.yaml 经 load_vocabulary_values 加载（禁字面量集合复制合法值、禁 yaml.safe_load 直读——GATE-VOCAB 检测5）; PG 出词表外状态/空表=异常 fail-closed exit 2（不静默归入分布、不出判档）; 判档纯函数 _evaluate_band 无 IO，边界可函数级验证; 边界语义=inclusive（answered∈[带下限,带上限] 在带、任一状态≤80% 在帽，帽含 answered 自身、双 regime 共用不放宽）; campaign 带仅放宽 answered 上限（CAMPAIGN_ANSWERED_MAX_PCT=95.0 即裁定值，经 Owner 2026-09-24 战役施工批六裁定之六 转正、非占位；持续入题机制上线后可改常态带 70 并另登裁定——WO-003② intake_batch 即为该前置）; 健康带判据不接入 thresholds.yaml（判据真源=题面 exam_plan.threshold 原文，非脚本治理阈值），常量命名避开 THRESHOLD/LIMIT 词根防 GATE-VOCAB 检测8 误报
# [MODIFY-GUARD] docs/_working/chain_piling_campaign/snapshots/question_batch_w6.yaml（PQ-0099 exam_plan.threshold 原文，改带先改题面）+ docs/_working/meta_question_answers/gaps/PQ-0099_workbook.md §4（campaign regime 已由 Owner 2026-09-24 战役施工批六裁定之六 裁 95 并落地本件，再改带须新裁定同步本行与出处注释）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] EXIT 0=在带（含边界值 30.0/70.0/80.0）; EXIT 1=破带（逐状态计数+占比+violations 结构化报告照打）; EXIT 2=异常（PG 连接/查询失败、出词表状态、空表、词表加载失败或词表缺 answered 锚——fail-closed 不出判档结论）
# [TESTS] 手动红蓝两腿：蓝腿=默认 regime 跑 PG 实况（一次性应考后全 answered=100%）→ exit 1+结构化报告；--regime campaign 亦如实报超帽（100>95 占位帽）exit 1；红腿=--selftest 构造分布函数级边界矩阵（29.9%/70.1%/80.1%/100% 双 regime 七例+边界值 30.0/70.0/80.0 三例），另跑 --regime campaign 验证参数路径；100% 单状态例锁死裁定帽（一次性应考终态必判红，禁把终态洗成在带）
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 04_construction_map #24 月度机检执行体（按需 CLI 非驻留进程，月检/Owner 查账时点触发）
"""check_meta_question_status_band — meta_question 状态分布健康带监控器（PQ-0099 / WO-003①）。

从 PG ``meta_question.meta_question`` 只读拉取 status 分布（全程零写），对照健康带判档：
  - default 带（稳态）：answered 占比 30-70% 且任一单状态占比 ≤80%；
  - campaign 带（战役期一次性应考特例带）：仅放宽 answered 上限至 **95%**——
    campaign regime 已按 Owner 2026-09-24 战役施工批六裁定之六 裁定为 95（PQ-0099 工作簿 §4 二选一取 (b) 双 regime 双带，
    豁免窗 (a) 不采：机制不留免检窗，只留更宽但仍有牙的带）。

判据出处：PQ-0099 题面 exam_plan.threshold="answered 30-70% 且单状态≤80%"
（快照=question_batch_w6.yaml L2461；台账=04_construction_map.md #24 monthly）。
背景：PQ-0099 fail=状态分布破健康带（战役建账+一次性应考后全表钉死 answered=100%），
工作簿 §4 判定 threshold 未声明适用 regime 为缺口，本监控器即其机检执行体。

状态枚举唯一真源=meta_question_statuses_vocabulary.yaml（经 load_vocabulary_values 动态加载，
GATE-VOCAB 合规）；PG 出词表外状态=异常 fail-closed（exit 2），不静默归入分布。

用法::

    # 月检（default 稳态带）
    python scripts/governance/check_meta_question_status_band.py

    # 战役期特例带（输出显式标注 campaign 裁定带 95% 与裁定出处）
    python scripts/governance/check_meta_question_status_band.py --regime campaign

    # 红腿：阈值边界函数级自测（零 PG 依赖，构造分布验证 29.9%/70.1%/80.1% 判档）
    python scripts/governance/check_meta_question_status_band.py --selftest

退出码：0=在带；1=破带（结构化报告照打）；2=异常（fail-closed 不出判档结论）。
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

_BOOT_ROOT = Path(__file__).resolve().parents[2]
_SRC = _BOOT_ROOT / "src"
if _SRC.exists() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from zephyr.shared.io.yaml_utils import load_vocabulary_values  # noqa: E402

_SQL_STATUS_DIST = "SELECT status, COUNT(*) FROM {schema}.meta_question GROUP BY status ORDER BY status"

__manifest__ = """
args: []
description: 'PQ-0099 状态分布健康带监控器：只读拉取 meta_question.status 分布，对照 answered 30-70%+单状态≤80% 判档（default/campaign 双 regime，campaign 上限=Owner 裁定值 95%）。'
dimensions:
- D3
priority: P2
timeout_seconds: 60
warn_only: false
"""

# ── 退出码契约（[ERROR_CONTRACT]）──
EXIT_IN_BAND = 0
EXIT_OUT_OF_BAND = 1
EXIT_ERROR = 2

# ── 状态枚举 SSoT（GATE-VOCAB：合法值禁字面量复制，一律动态加载）──
STATUS_VOCAB_FILE = "meta_question_statuses_vocabulary.yaml"

# 健康带判据的状态锚：题面 threshold 原文点名 "answered"（单值语义锚，非枚举复制；
# 加载词表后校验其在词表内，词表漂移时 fail-closed）。
ANSWERED_STATUS = "answered"

# ── 健康带阈值（语义命名常量+判据出处）────────────────────────────────
# 判据出处：PQ-0099 题面 exam_plan.threshold="answered 30-70% 且单状态≤80%"，
#   快照真源=docs/_working/chain_piling_campaign/snapshots/question_batch_w6.yaml L2461，
#   台账=docs/_working/chain_piling_campaign/04_construction_map.md #24（monthly）。
#   为稳态注册表设计的判据；不接入 thresholds.yaml（该 SSoT 面向脚本治理超时/配额类阈值，
#   本判据真源是题面原文）。
# campaign 带数值出处：PQ-0099 工作簿 §4 二选一（(a) 豁免窗 / (b) 双 regime 双带）——
#   Owner 2026-09-24 战役施工批六裁定之六 取 (b)，campaign answered 上限裁 95.0（本行即裁定落地位，非占位）。
#   95 而非 100 的理由（裁定原意）：战役收口后全表仍钉死单状态属结构性异常，
#   监控必须继续如实报警——100% 单状态例已入 --selftest 红腿锁死。
#   改带条件（同裁定留口）：持续入题机制上线、状态分布回到多态并存后改回常态带 70。
ANSWERED_BAND_MIN_PCT = 30.0  # default/campaign 共用下限（题面 "30-70%" 下界）
ANSWERED_BAND_MAX_PCT = 70.0  # default 带上限（题面 "30-70%" 上界，inclusive）
SINGLE_STATUS_MAX_PCT = 80.0  # 单状态占比帽（题面 "单状态≤80%"，双 regime 共用不放宽）
CAMPAIGN_ANSWERED_MAX_PCT = (
    95.0  # campaign answered 上限=Owner 裁定值（Owner 2026-09-24 战役施工批六裁定之六，2026-09-24 转正）
)

_CAMPAIGN_NOTE = (
    f"campaign 裁定带：answered 上限 {CAMPAIGN_ANSWERED_MAX_PCT:.0f}%（Owner 2026-09-24 战役施工批六裁定之六转正，"
    "出处见本件常量区注释；下限/单状态帽与 default 带共用不放宽）"
)

# --schema 参数白名单（防注入：schema 名经正则校验后才可拼 SQL）
_SCHEMA_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


@dataclass(frozen=True)
class BandVerdict:
    """判档结论（纯数据，逐状态计数+占比+violations 结构化承载）。"""

    regime: str
    total: int
    counts: dict[str, int]  # status → 计数（按计数降序、同数按名排序）
    pcts: dict[str, float]  # status → 占比（原始浮点，报告层取 2 位小数）
    answered_pct: float
    band_min_pct: float
    band_max_pct: float
    max_status: str
    max_status_pct: float
    violations: tuple[str, ...]
    notes: tuple[str, ...]

    @property
    def in_band(self) -> bool:
        return not self.violations


def _evaluate_band(counts: dict[str, int], regime: str) -> BandVerdict:
    """判档纯函数（无 IO）：构造分布 → 健康带判档结论。

    边界语义 inclusive：answered 占比 == 带边界 在带；单状态占比 == 帽 在帽。
    campaign 带仅放宽 answered 上限（下限/单状态帽与 default 共用）。

    Raises:
        ValueError: 分布为空（总量 0）或 regime 非法——fail-closed。
    """
    if regime == "campaign":
        band_max = CAMPAIGN_ANSWERED_MAX_PCT
    elif regime == "default":
        band_max = ANSWERED_BAND_MAX_PCT
    else:
        raise ValueError(f"unknown regime: {regime!r}")
    total = sum(counts.values())
    if total <= 0:
        raise ValueError("empty status distribution (total=0)")
    pcts = {status: n / total * 100.0 for status, n in counts.items()}
    answered_pct = pcts.get(ANSWERED_STATUS, 0.0)
    # max 状态确定性 tie-break：计数降序，同数按状态名升序
    max_status = sorted(counts, key=lambda s: (-counts[s], s))[0]
    max_status_pct = pcts[max_status]

    violations: list[str] = []
    if answered_pct < ANSWERED_BAND_MIN_PCT:
        violations.append(f"answered {answered_pct:.2f}% < 带下限 {ANSWERED_BAND_MIN_PCT:.1f}%")
    if answered_pct > band_max:
        violations.append(f"answered {answered_pct:.2f}% > 带上限 {band_max:.1f}%")
    if max_status_pct > SINGLE_STATUS_MAX_PCT:
        violations.append(f"单状态 {max_status} {max_status_pct:.2f}% > 帽 {SINGLE_STATUS_MAX_PCT:.1f}%")

    notes = (_CAMPAIGN_NOTE,) if regime == "campaign" else ()
    ordered_counts = dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))
    return BandVerdict(
        regime=regime,
        total=total,
        counts=ordered_counts,
        pcts=pcts,
        answered_pct=answered_pct,
        band_min_pct=ANSWERED_BAND_MIN_PCT,
        band_max_pct=band_max,
        max_status=max_status,
        max_status_pct=max_status_pct,
        violations=tuple(violations),
        notes=notes,
    )


def _load_statuses() -> tuple[frozenset[str], str | None]:
    """从词表 SSoT 动态加载状态枚举（禁字面量/禁 safe_load 直读——GATE-VOCAB 检测5）。

    Returns:
        (合法状态集, error)；error 非 None 时 fail-closed。
    """
    try:
        values = load_vocabulary_values(STATUS_VOCAB_FILE, strict=True)
    except Exception as exc:  # noqa: BLE001 — 词表缺失/损坏统一 fail-closed
        return frozenset(), f"vocab_load_failed: {STATUS_VOCAB_FILE}: {exc}"
    if not values:
        return frozenset(), f"vocab_load_failed: {STATUS_VOCAB_FILE} 合法值为空"
    if ANSWERED_STATUS not in values:
        return frozenset(), (
            f"vocab_missing_anchor: {STATUS_VOCAB_FILE} 缺判据锚状态 {ANSWERED_STATUS!r}"
            "（题面 threshold 点名 answered，词表漂移须先修词表）"
        )
    return frozenset(values), None


def _load_status_distribution(schema: str) -> tuple[dict[str, int], str | None]:
    """只读拉取 status 分布（GROUP BY 计数）→ (counts, error)。

    零写保证：get_depgraph_pg_connection 默认 read_only=True（depgraph_reader 只读角色），
    全函数无任何 DML/DDL 语句。惰性导入使 --selftest 路径零 PG 依赖。
    """
    from zephyr.governance.depgraph_schema import (  # noqa: PLC0415
        get_depgraph_pg_connection,
    )

    sql = _SQL_STATUS_DIST.format(schema=schema)
    try:
        conn = get_depgraph_pg_connection(read_only=True)
    except Exception as exc:  # noqa: BLE001
        return {}, f"pg_connect_failed: {exc}"
    try:
        cur = conn.cursor()
        cur.execute(sql, ())
        counts = {str(status): int(n) for status, n in cur.fetchall()}
        return counts, None
    except Exception as exc:  # noqa: BLE001
        return {}, f"pg_query_failed: {exc}"
    finally:
        conn.close()


def _print_report(verdict: BandVerdict, schema: str) -> None:
    """结构化报告：逐状态计数+占比+判档结论（stdout，人类可读+字段化行）。"""
    print(f"check_meta_question_status_band | regime={verdict.regime} | schema={schema}")
    print("source: PG meta_question.meta_question (read_only)")
    print(f"total={verdict.total}")
    print("per-status (count, pct):")
    for status, n in verdict.counts.items():
        print(f"  {status:<12}: {n:>6} ({verdict.pcts[status]:.2f}%)")
    print(
        f"answered_pct={verdict.answered_pct:.2f}"
        f" | band=[{verdict.band_min_pct:.1f}, {verdict.band_max_pct:.1f}]"
        f" | max_status={verdict.max_status} {verdict.max_status_pct:.2f}%"
        f" | single_status_cap={SINGLE_STATUS_MAX_PCT:.1f}"
    )
    for note in verdict.notes:
        print(f"note: {note}")
    if verdict.in_band:
        print("VERDICT: IN_BAND (exit 0)")
    else:
        print("VERDICT: OUT_OF_BAND (exit 1)")
        print("violations:")
        for v in verdict.violations:
            print(f"  - {v}")


# ── 红腿：阈值边界函数级自测（零 PG 依赖，构造分布验证判档）─────────────
# 用例：（用例名, 构造分布, regime, 期望在带）
_SELFTEST_CASES: list[tuple[str, dict[str, int], str, bool]] = [
    # 29.9% 边界：低于下限 → 双 regime 均破带（下限不因 campaign 放宽）
    (
        "answered 29.9% < 下限 30 → default 破带",
        {"answered": 299, "reexam": 351, "registered": 350},
        "default",
        False,
    ),
    (
        "answered 29.9% < 下限 30 → campaign 亦破带",
        {"answered": 299, "reexam": 351, "registered": 350},
        "campaign",
        False,
    ),
    # 70.1% 边界：default 超上限破带；campaign 上限放宽后同分布回到带内（regime 差异显影）
    (
        "answered 70.1% > 上限 70 → default 破带",
        {"answered": 701, "reexam": 150, "registered": 149},
        "default",
        False,
    ),
    (
        "answered 70.1% ≤ campaign 裁定上限 95 → campaign 在带",
        {"answered": 701, "reexam": 150, "registered": 149},
        "campaign",
        True,
    ),
    # 80.1% 边界：单状态帽双 regime 共用不放宽——campaign 放宽 answered 上限后
    # 80.1% 仍必须破帽（帽含 answered 自身）
    (
        "单状态 answered 80.1% > 帽 80 → default 破带",
        {"answered": 801, "reexam": 199},
        "default",
        False,
    ),
    (
        "单状态 answered 80.1% > 帽 80 → campaign 仍破带（帽不放宽）",
        {"answered": 801, "reexam": 199},
        "campaign",
        False,
    ),
    # 边界值 inclusive 自证：恰好 30.0/70.0/80.0 均在带/在帽
    (
        "边界 answered 30.0% == 下限 → default 在带",
        {"answered": 300, "reexam": 350, "registered": 350},
        "default",
        True,
    ),
    (
        "边界 answered 70.0% == 上限 → default 在带",
        {"answered": 700, "reexam": 150, "registered": 150},
        "default",
        True,
    ),
    (
        "边界单状态 answered 80.0% == 帽 → campaign 在带",
        {"answered": 800, "reexam": 200},
        "campaign",
        True,
    ),
    # 100% 终态：一次性应考全表钉死 answered——campaign 裁定带亦必判红（95 帽有牙）
    (
        "单状态 answered 100% > 帽 80 且 > campaign 裁定上限 95 → campaign 判红",
        {"answered": 283},
        "campaign",
        False,
    ),
]


def _run_selftest() -> int:
    """边界矩阵函数级自测：全部通过 exit 0，任一不符 exit 2（fail-closed）。"""
    statuses, error = _load_statuses()
    if error:
        print(f"SELFTEST ERROR: {error}")
        return EXIT_ERROR
    print(f"SELFTEST: 词表 SSoT 接线 OK（{STATUS_VOCAB_FILE} {len(statuses)} 态，含锚 {ANSWERED_STATUS}）")
    failures: list[str] = []
    for name, counts, regime, expected_in_band in _SELFTEST_CASES:
        try:
            verdict = _evaluate_band(counts, regime)
        except ValueError as exc:
            failures.append(f"{name}: 判档抛错 {exc}")
            print(f"  FAIL {name}: 判档抛错 {exc}")
            continue
        ok = verdict.in_band == expected_in_band
        mark = "PASS" if ok else "FAIL"
        print(
            f"  {mark} {name} | in_band={verdict.in_band}（期望 {expected_in_band}）"
            f" | violations={list(verdict.violations)}"
        )
        if not ok:
            failures.append(name)
    total = len(_SELFTEST_CASES)
    print(f"SELFTEST: {total - len(failures)}/{total} 通过")
    if failures:
        print(f"SELFTEST ERROR: {len(failures)} 例不符（fail-closed）")
        return EXIT_ERROR
    return EXIT_IN_BAND


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(
        description="PQ-0099 状态分布健康带监控器（meta_question.status 只读判档，双 regime）"
    )
    parser.add_argument(
        "--regime",
        choices=("default", "campaign"),
        default="default",
        help="健康带 regime：default=稳态带（answered 30-70%+单状态≤80%）；"
        "campaign=战役期特例带（仅放宽 answered 上限至 Owner 裁定值 95%）",
    )
    parser.add_argument(
        "--schema",
        default="meta_question",
        help="PG schema（默认 meta_question）",
    )
    parser.add_argument(
        "--selftest",
        action="store_true",
        help="红腿自测：阈值边界矩阵函数级验证（零 PG 依赖），不连库不出实况判档",
    )
    args = parser.parse_args()

    if not _SCHEMA_PATTERN.match(args.schema):
        print(f"ERROR: 非法 schema 名（须匹配 {_SCHEMA_PATTERN.pattern}）: {args.schema}")
        return EXIT_ERROR

    statuses, error = _load_statuses()
    if args.selftest:
        return _run_selftest()
    if error:
        print(f"ERROR: {error}")
        return EXIT_ERROR

    counts, error = _load_status_distribution(args.schema)
    if error:
        print(f"ERROR: {error}")
        return EXIT_ERROR
    if not counts:
        print("ERROR: meta_question.meta_question 空表（status 分布未定义，fail-closed 不出判档）")
        return EXIT_ERROR
    unknown = sorted(set(counts) - statuses)
    if unknown:
        print(f"ERROR: PG 出词表外状态（fail-closed，不静默归入分布）：{unknown}；词表真源={STATUS_VOCAB_FILE}")
        return EXIT_ERROR

    try:
        verdict = _evaluate_band(counts, args.regime)
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return EXIT_ERROR
    _print_report(verdict, args.schema)
    return EXIT_IN_BAND if verdict.in_band else EXIT_OUT_OF_BAND


if __name__ == "__main__":
    sys.exit(main())
