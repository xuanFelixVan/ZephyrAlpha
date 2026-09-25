# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §standards_governance
# [MODULE] zephyr.governance.standards_governance.standard_checkup
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.standards_governance.rule_replay (P1-P4 预注册判据常量，SSOT 引用不复制);
#                zephyr.shared.utils.time_utils (now_utc/parse_iso); zephyr.shared.io.paths (REPO_ROOT)
# [CONSUMERS] CLI python -m zephyr.governance.standards_governance.standard_checkup checkup
#             [--stats PATH --window 30 --out DIR | --demo];
#             [CONSUMERS 附录] 挂 L1 内监慢周期=接线批（本班只交付 CLI+纯函数，不接线）;
#             运营启用前置=gate_execution_stats 积累满 30 天窗（2026-09-15 起积累中，当前人工点火）
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 对 DB/审计文件只读（DESIGN §②-G 工具禁写 DB），提案仅落参数指定目录
#              （默认 docs/_working/ai_layer_vision/OBJ_R_rules_standards/proposals/，测试传 tmp_path）;
#              fail-open 读（坏行跳过计数留痕）+ fail-closed 输入（stats 缺文件抛 CheckupError）;
#              误拦率 v0 代理=豁免（skipped）事件计数，豁免缺席返回空 dict+诚实注记（不虚构精度）;
#              自动化的是提案与证据不是裁决（形态保守铁律）——产出恒 status=draft;
#              判据/聚合为纯函数（as_of 可注入），now_utc 仅消费于 generated_at/proposal date/proposal_id
# [MODIFY-GUARD] docs/_working/ai_layer_vision/OBJ_R_rules_standards/DESIGN.md §④（设计真源，变更走 OBJ_R 流水线）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] stats 缺文件→CheckupError（fail-closed）；坏行 JSON→跳过+计数留痕（fail-open）；
#                  时间戳缺失/畸形→该行不进任何窗（不炸）；写提案缺 proposal_id→CheckupError 拒落盘；
#                  CLI 无候选=打印"零候选"退出码 0（零候选是正常态）；CLI 输入错误→REFUSED 退出码 2
# [TESTS] tests/governance/test_standard_checkup.py（坏行跳过+缺文件抛错/触发率已知值 10 提交 2 触发=20%/
#         两窗切分边界/退役四态+判据线边界/误拦代理诚实条款/proposal schema+两问/落盘回读/CLI --demo 与零候选）
# [TTL] permanent
"""standard_checkup — 月度标准体检：gate 触发率/误拦率统计器 + standards_proposal 生成器。

OBJ_R 标准与规则线施工项 S4（DESIGN §④，挂 L1 内监慢周期=接线批）。数据主燃料=
```.runtime/audit/gate_execution_stats.jsonl```（每行：timestamp/n_specs/failed[]/reused{}/ms{}/total_ms，
gate 触发定义=出现在 failed 列表，runs=窗口内审计行数）。可选补充源 gate_runs 表（PG）不强制——
DB 缺席时不炸。

体检口径（DESIGN §④）：
  连续两窗触发率 <1% → 退役候选（宪法 §4 对齐）；任一窗 >50% → 噪音候选（阈值过松）；
  误拦率 v0 代理=豁免（skipped）事件计数，豁免记录缺席返回空 dict+诚实注记（不虚构精度），
  事故驱动立案口径见 DESIGN §④。

产出：standards_proposal 草案 YAML（schema 全字段见 DESIGN §④），恒 status=draft——
自动化的是提案和证据，不是裁决；file 后进治理层标准库变更流程，Owner 裁决。
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Final

import yaml

from zephyr.governance.standards_governance.rule_replay import (
    P1_PASS_LEAK_ALLOWED,
    P2_NEW_BLOCK_RATE,
    P3_JACCARD_GLOBAL,
    P3_JACCARD_PER_GATE,
)
from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.utils.time_utils import now_utc, parse_iso

logger = logging.getLogger(__name__)

DEFAULT_STATS_PATH: Final = REPO_ROOT / ".runtime" / "audit" / "gate_execution_stats.jsonl"
DEFAULT_OUT_DIR: Final = REPO_ROOT / "docs" / "_working" / "ai_layer_vision" / "OBJ_R_rules_standards" / "proposals"
WINDOW_DAYS_DEFAULT: Final = 30
N_WINDOWS_DEFAULT: Final = 2
RETIRE_LINE: Final = 0.01  # 连续两窗触发率 <1% → 退役候选（DESIGN §④/宪法 §4）
NOISE_LINE: Final = 0.50  # 任一窗触发率 >50% → 噪音候选（阈值过松）
MIN_WINDOWS: Final = 2  # 有效窗不足此数 → insufficient 不判
STATUS_DRAFT: Final = "draft"
SKIP_EVENT_VALUE: Final = "skipped"
RULER_GATE_TRIGGER_RATE: Final = "gate_trigger_rate"  # 盘点表（DESIGN §③）行键的体检指标
FP_PROXY_NOTE: Final = "误拦率代理=豁免计数，事故驱动立案口径见 DESIGN §④"
OPERATION_PREREQ_NOTE: Final = (
    "运营启用前置=gate_execution_stats 积累满 30 天窗（2026-09-15 起积累中）；L1 内监慢周期接线=接线批，当前人工点火"
)
ZERO_CANDIDATE_MSG: Final = "零候选"
FILENAME_SAFE_RE: Final = re.compile(r"[^A-Za-z0-9._-]")


class CheckupError(RuntimeError):
    """体检输入错误（stats 缺文件/proposal 缺关键字段等 fail-closed 场景）。

    :param details: 敏感上下文（路径等）走 details 不进消息文本（5.99.20）。
    """

    def __init__(self, msg: str, *, details: dict[str, str] | None = None) -> None:
        super().__init__(msg)
        self.details: dict[str, str] = details or {}


# ────────────────────────── 读取（fail-open 读 + fail-closed 输入） ──────────────────────────


def _parse_line(line: str) -> dict[str, Any] | None:
    stripped = line.strip()
    if not stripped:
        return None
    try:
        row = json.loads(stripped)
    except json.JSONDecodeError:
        return None
    return row if isinstance(row, dict) else None


def _read_stats(path: Path) -> tuple[list[dict[str, Any]], int]:
    """读 jsonl → (记录, 坏行数)。缺文件 fail-closed 抛 CheckupError，坏行跳过计数留痕。"""
    if not path.exists():
        raise CheckupError("stats 文件不存在（fail-closed）", details={"path": str(path)})
    records: list[dict[str, Any]] = []
    bad = 0
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        row = _parse_line(line)
        if row is None:
            if line.strip():
                bad += 1
            continue
        records.append(row)
    if bad:
        logger.warning("load_stats 跳过坏行 %d 行（fail-open 留痕）: %s", bad, path)
    return records, bad


def load_stats(path: Path) -> list[dict[str, Any]]:
    """逐行 JSON 解析审计文件（fail-open：坏行跳过计数留痕；缺文件抛 CheckupError）。"""
    records, _ = _read_stats(path)
    return records


def _record_ts(record: dict[str, Any]) -> datetime | None:
    raw = record.get("timestamp")
    if not isinstance(raw, str) or not raw:
        return None
    try:
        return parse_iso(raw)
    except ValueError:
        return None


# ────────────────────────── 纯函数判据（as_of 可注入） ──────────────────────────


def _count_fires(records: list[dict[str, Any]]) -> tuple[dict[str, int], int]:
    """单窗聚合成 (gate_id→触发次数, runs)。触发定义=gate 出现在 failed 列表。"""
    fires: dict[str, int] = defaultdict(int)
    runs = 0
    for record in records:
        if _record_ts(record) is None:
            continue
        runs += 1
        failed = record.get("failed")
        if not isinstance(failed, list):
            continue
        for gate_id in failed:
            if isinstance(gate_id, str) and gate_id:
                fires[gate_id] += 1
    return dict(fires), runs


def _rates_of(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """窗内记录 → {gate_id: {fires, runs, rate}}（rate=fires/runs，窗空时 rate=0.0）。"""
    fires, runs = _count_fires(records)
    return {
        gate_id: {
            "fires": fire_count,
            "runs": runs,
            "rate": round(fire_count / runs, 6) if runs else 0.0,
        }
        for gate_id, fire_count in sorted(fires.items())
    }


def trigger_rates(
    records: list[dict[str, Any]],
    window_days: int = WINDOW_DAYS_DEFAULT,
    *,
    as_of: datetime | None = None,
) -> dict[str, dict[str, Any]]:
    """滚动窗口触发率聚合 {gate_id: {fires, runs, rate}}（纯函数，as_of 可注入）。

    runs=窗口内总提交次数（审计行数）；rate=fires/runs；只出现过 n_specs 计数、
    无 gate 清单的行不贡献 gate 键（诚实口径：不可见 gate 不虚构）。
    """
    end = as_of or now_utc()
    start = end - timedelta(days=window_days)
    in_window = [r for r in records if (ts := _record_ts(r)) is not None and start <= ts < end]
    return _rates_of(in_window)


def split_windows(
    records: list[dict[str, Any]],
    window_days: int = WINDOW_DAYS_DEFAULT,
    n_windows: int = N_WINDOWS_DEFAULT,
    *,
    as_of: datetime | None = None,
) -> list[list[dict[str, Any]]]:
    """按时间倒序切 n 个连续不重叠窗（index 0=最近窗；半开区间 [start, end)）。

    窗外（更老）与未来时间戳的记录丢弃；时间戳缺失/畸形的记录丢弃。
    """
    end = as_of or now_utc()
    buckets: list[list[dict[str, Any]]] = [[] for _ in range(n_windows)]
    span = timedelta(days=window_days)
    for record in records:
        ts = _record_ts(record)
        if ts is None:
            continue
        age = end - ts
        if age < timedelta(0):
            continue
        index = int(age // span)
        if index < n_windows:
            buckets[index].append(record)
    return buckets


def retire_candidates(
    window_rates: list[dict[str, Any]],
    *,
    retire_line: float = RETIRE_LINE,
    noise_line: float = NOISE_LINE,
    min_windows: int = MIN_WINDOWS,
) -> dict[str, Any]:
    """DESIGN §④ 口径四态判定（纯函数，逐窗报告可注入）。

    window_rates=逐窗报告列表（index 0=最近窗），每项 {"runs": int, "rates": {gate: {rate...}}}。
    判定规则：有效窗（runs>0）按序取最近 min_windows 个 evaluated；gate 在 evaluated 某 valid
    窗缺席=该窗触发率 0.0（跑了但没触发）；连续 evaluated 全部 <retire_line → 退役候选；
    任一 evaluated 窗 >noise_line → 噪音候选（噪音优先于退役）；有效窗不足 → 全部 insufficient
    （单窗不足不判）。gate 全集=全部窗 rates 键的并集（历史触发、近两窗归零 → 退役候选）。
    """
    valid = [w for w in window_rates if w.get("runs", 0) > 0]
    evaluated = valid[:min_windows]
    universe: set[str] = set()
    for window in window_rates:
        universe.update(window.get("rates", {}))
    base: dict[str, Any] = {
        "windows_evaluated": len(evaluated),
        "min_windows": min_windows,
        "retire": [],
        "noise": [],
        "normal": [],
        "insufficient": [],
        "evaluated_rates": {},
    }
    if len(evaluated) < min_windows:
        base["insufficient"] = sorted(universe)
        return base
    retire: list[str] = []
    noise: list[str] = []
    normal: list[str] = []
    evaluated_rates: dict[str, list[float]] = {}
    for gate_id in sorted(universe):
        rates = [float(window.get("rates", {}).get(gate_id, {}).get("rate", 0.0)) for window in evaluated]
        evaluated_rates[gate_id] = rates
        if any(rate > noise_line for rate in rates):
            noise.append(gate_id)
        elif all(rate < retire_line for rate in rates):
            retire.append(gate_id)
        else:
            normal.append(gate_id)
    base["retire"] = retire
    base["noise"] = noise
    base["normal"] = normal
    base["evaluated_rates"] = evaluated_rates
    return base


# ────────────────────────── 误拦率代理（诚实条款） ──────────────────────────


def extract_skip_events(records: list[dict[str, Any]]) -> list[dict[str, str]]:
    """从审计行提取豁免（skip_gates）事件：reused 字段值=skipped 的 gate。"""
    events: list[dict[str, str]] = []
    for record in records:
        reused = record.get("reused")
        if not isinstance(reused, dict):
            continue
        for gate_id, status in reused.items():
            if status == SKIP_EVENT_VALUE and isinstance(gate_id, str) and gate_id:
                events.append({"gate_id": gate_id, "timestamp": str(record.get("timestamp", ""))})
    return events


def false_positive_proxy(
    records: list[dict[str, Any]],
    exemption_records: list[dict[str, Any]] | None = None,
) -> dict[str, int]:
    """误拦率 v0 代理=豁免（skip）事件计数（DESIGN §④ 诚实条款）。

    显式 exemption_records 提供时只统计它；缺席时回退扫 records 内嵌 reused=skipped 事件；
    两处均无豁免记录 → 返回空 dict（不虚构精度），报告侧必携带 FP_PROXY_NOTE 注记。
    """
    source = exemption_records if exemption_records else extract_skip_events(records)
    counts: dict[str, int] = defaultdict(int)
    for event in source:
        gate_id = event.get("gate_id") if isinstance(event, dict) else None
        if isinstance(gate_id, str) and gate_id:
            counts[gate_id] += 1
    return dict(counts)


# ────────────────────────── standards_proposal 生成（DESIGN §④ schema） ──────────────────────────


def build_proposal(
    proposal_id: str,
    ruler_id: str,
    current_value: Any,
    source_path: str,
    evidence: Any,
    proposed_value: Any,
    *,
    impact_note: str = "",
) -> dict[str, Any]:
    """产出 standards_proposal 全字段草案（DESIGN §④ schema），恒 status=draft。

    重放判据预告=固定模板引用 P1-P4（常量 SSOT 引用自 rule_replay，重放前锁定）；
    预期影响两问（定调 #11：好在哪+消灭哪段人工）默认由 impact_note 填充，缺席=待补占位。
    """
    note = impact_note.strip()
    fallback = "待补（提案人立案时填写，定调 #11 两问）"
    return {
        "proposal_id": proposal_id,
        "date": now_utc().isoformat(),
        "ruler_id": ruler_id,
        "current_value": current_value,
        "source_path": source_path,
        "evidence": evidence,
        "proposed_value": proposed_value,
        "replay_criteria_preview": {
            "template": "OBJ_R DESIGN §2-E 预注册判据（重放前锁定，修标一票否决）",
            "P1_该拦放走": f"new_pass = {P1_PASS_LEAK_ALLOWED}（一票否决）",
            "P2_误拦不增": f"新增拦截率 <= {P2_NEW_BLOCK_RATE} 且逐案归因误拦 = 0",
            "P3_集合保持": f"全局 Jaccard >= {P3_JACCARD_GLOBAL} 且单 gate >= {P3_JACCARD_PER_GATE}",
            "P4_分层稳健": "层1（已知拦截）/层3（特殊形态）分别复检 P1-P3",
        },
        "expected_impact": {
            "q1_better_where": note or fallback,
            "q2_manual_eliminated": note or fallback,
        },
        "status": STATUS_DRAFT,
    }


def write_proposal(proposal: dict[str, Any], out_dir: Path) -> Path:
    """落盘 `<proposal_id>.yaml`（yaml.safe_dump sort_keys=False + allow_unicode）；目录不存在创建。"""
    proposal_id = str(proposal.get("proposal_id", "")).strip()
    if not proposal_id:
        raise CheckupError("proposal 缺 proposal_id，拒绝落盘（fail-closed）")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / (FILENAME_SAFE_RE.sub("-", proposal_id) + ".yaml")
    out_path.write_text(
        yaml.safe_dump(proposal, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return out_path


# ────────────────────────── 体检编排（读生产文件的唯一入口） ──────────────────────────


def _proposal_id(gate_id: str) -> str:
    return f"STD-PROP-{now_utc().strftime('%Y%m%d')}-{FILENAME_SAFE_RE.sub('-', gate_id)}"


def _emit_proposal(
    gate_id: str,
    kind: str,
    verdict: dict[str, Any],
    overall: dict[str, dict[str, Any]],
    source_path: str,
    window_days: int,
    out_dir: Path,
) -> str:
    action = "retire_candidate" if kind == "retire" else "noise_candidate"
    proposal = build_proposal(
        proposal_id=_proposal_id(gate_id),
        ruler_id=RULER_GATE_TRIGGER_RATE,
        current_value={
            "metric": "trigger_rate",
            "gate_id": gate_id,
            "window_days": window_days,
            "observed_window_rates": verdict["evaluated_rates"].get(gate_id, []),
            "overall_rate": overall.get(gate_id, {}).get("rate"),
        },
        source_path=source_path,
        evidence={
            "kind": kind,
            "windows_evaluated": verdict["windows_evaluated"],
            "min_windows": verdict["min_windows"],
            "judgement_lines": {"retire_line": RETIRE_LINE, "noise_line": NOISE_LINE},
            "note": FP_PROXY_NOTE if kind == "retire" else "",
        },
        proposed_value={"action": action, "gate_id": gate_id},
        impact_note="",
    )
    return str(write_proposal(proposal, out_dir))


def _checkup_core(
    records: list[dict[str, Any]],
    out_dir: Path,
    *,
    source_path: str,
    window_days: int = WINDOW_DAYS_DEFAULT,
    n_windows: int = N_WINDOWS_DEFAULT,
    bad_lines: int = 0,
) -> dict[str, Any]:
    """体检内核（纯记录输入；run_checkup/CLI --demo 共用）。多切一窗供历史全集参照。"""
    generated_at = now_utc().isoformat()
    windows = split_windows(records, window_days, n_windows + 1)
    window_reports = [{"runs": len(bucket), "rates": _rates_of(bucket)} for bucket in windows]
    verdict = retire_candidates(window_reports)
    overall = trigger_rates(records, window_days)
    fp_proxy = false_positive_proxy(records)
    proposals = [
        _emit_proposal(gate_id, kind, verdict, overall, source_path, window_days, out_dir)
        for kind in ("retire", "noise")
        for gate_id in verdict[kind]
    ]
    return {
        "generated_at": generated_at,
        "stats_path": str(source_path),
        "window_days": window_days,
        "n_windows": n_windows,
        "records_total": len(records),
        "bad_lines_skipped": bad_lines,
        "window_runs": [window["runs"] for window in window_reports],
        "overall_rates": overall,
        "candidates": verdict,
        "false_positive_proxy": fp_proxy,
        "false_positive_proxy_note": FP_PROXY_NOTE,
        "operation_prereq": OPERATION_PREREQ_NOTE,
        "proposals_written": proposals,
    }


def run_checkup(
    stats_path: Path,
    out_dir: Path,
    *,
    window_days: int = WINDOW_DAYS_DEFAULT,
    n_windows: int = N_WINDOWS_DEFAULT,
) -> dict[str, Any]:
    """对真实审计文件跑体检（只读 jsonl；提案落 out_dir）。缺 stats 文件抛 CheckupError。"""
    records, bad_lines = _read_stats(stats_path)
    return _checkup_core(
        records,
        out_dir,
        source_path=str(stats_path),
        window_days=window_days,
        n_windows=n_windows,
        bad_lines=bad_lines,
    )


# ────────────────────────── CLI ──────────────────────────


def _demo_records() -> list[dict[str, Any]]:
    """内置合成数据：DEMO-NOISE（噪音候选）/DEMO-NORMAL（正常）/DEMO-QUIET（近两窗归零退役候选）。"""
    now = now_utc()
    records: list[dict[str, Any]] = []
    for window in range(2):
        for i in range(20):
            ts = now - timedelta(days=1 + window * 30 + (i % 28), minutes=i)
            failed: list[str] = []
            if i < 12:
                failed.append("DEMO-NOISE")
            if i < 2:
                failed.append("DEMO-NORMAL")
            reused: dict[str, str] = {}
            if i % 10 == 0:
                reused["DEMO-SKIPPED"] = SKIP_EVENT_VALUE
            records.append(
                {
                    "timestamp": ts.isoformat(),
                    "n_specs": 100,
                    "failed": failed,
                    "reused": reused,
                    "ms": {},
                    "total_ms": 0.0,
                }
            )
    for i in range(10):  # 第 3 窗（evaluated 之外）：历史有触发、近两窗归零 → 退役候选
        ts = now - timedelta(days=62 + i)
        records.append(
            {
                "timestamp": ts.isoformat(),
                "n_specs": 100,
                "failed": ["DEMO-QUIET"],
                "reused": {},
                "ms": {},
                "total_ms": 0.0,
            }
        )
    return records


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m zephyr.governance.standards_governance.standard_checkup",
        description="月度标准体检——触发率/误拦率统计 + standards_proposal 草案生成（OBJ_R S4）",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_checkup = sub.add_parser("checkup", help="跑体检；退役/噪音候选各生成一份草案 YAML")
    p_checkup.add_argument(
        "--stats", default=str(DEFAULT_STATS_PATH), help="gate_execution_stats.jsonl 路径（只读；--demo 时忽略）"
    )
    p_checkup.add_argument("--window", type=int, default=WINDOW_DAYS_DEFAULT, help="滚动窗口天数（默认 30）")
    p_checkup.add_argument("--out", default=str(DEFAULT_OUT_DIR), help="提案输出目录")
    p_checkup.add_argument("--demo", action="store_true", help="内置合成数据跑通全链，不读生产文件")
    return parser


def _print_summary(report: dict[str, Any]) -> None:
    verdict = report["candidates"]
    if not verdict["retire"] and not verdict["noise"]:
        print(ZERO_CANDIDATE_MSG)
    for gate_id in verdict["retire"]:
        print(f"[退役候选] {gate_id} observed={verdict['evaluated_rates'].get(gate_id)}")
    for gate_id in verdict["noise"]:
        print(f"[噪音候选] {gate_id} observed={verdict['evaluated_rates'].get(gate_id)}")
    print(json.dumps(report, ensure_ascii=False, indent=2))


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    args = _build_parser().parse_args(argv)
    if args.cmd != "checkup":
        return 2
    out_dir = Path(args.out)
    try:
        if args.demo:
            report = _checkup_core(
                _demo_records(),
                out_dir,
                source_path="<demo:synthetic>",
                window_days=args.window,
            )
        else:
            report = run_checkup(Path(args.stats), out_dir, window_days=args.window)
    except CheckupError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    _print_summary(report)
    return 0


# noqa: m11-perm-manual-legitimate  M11豁免: 本模块=月度标准体检执行件，L1 内监慢周期接线批前由人工/按需点火（非 cron/非 daemon/非常驻服务）
if __name__ == "__main__":
    sys.exit(main())
