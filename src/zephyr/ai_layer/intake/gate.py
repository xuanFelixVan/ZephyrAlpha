# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_intake
# [MODULE] zephyr.ai_layer.intake.gate
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.ai_layer.intake.card_store (CardStore, CardDraft, check_stage_transition); zephyr.ai_layer.intake.dedup (IntakeDedup, DedupReport, simhash64, content_fingerprint); zephyr.shared.utils.time_utils (now_utc)
# [CONSUMERS] zephyr.ai_layer.intake.intake_events (intake_ingest_due handler); scripts/ai_layer 批入库 CLI（后续接线批）
# [STARTUP] manual
# [MATURITY] evolving
# [INVARIANTS] 进货费两问机检（labor_killed>=20 字且非占位串 / four_gates 四键全在且逐键判据）；
#              单来源（independent_sources<2 且 status!='待验证'）→封顶 L1 永不进 E2；
#              L0 硬过滤（license 非空且不在禁止清单 / source_year∈[2000,当前年] / sha256 无冲突 / 五比对面 simhash 无 k<=3 命中）；
#              配额闸（当日 source_slug 入库数 < T5.daily_quota，外部源配额不可清零）；
#              注入探针非空；判据全为纯函数（零 DB），DB 只供读数；任一挂=拒绝且拒因可机读
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L2_intake_library/DESIGN.md §2.5（改判据先改设计稿）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 判据函数零副作用、永不抛异常（缺字段=拒因，不是崩溃）；DB 不可达→异常上抛（fail-closed，绝不降级为"放行"）；
#                  admit() 返回 AdmissionVerdict（passed=False 时 reject_reasons 非空且首条为主拒因）
# [TESTS] tests/ai_layer/intake/（★ 在册缺口：本模块测试 test_gate.py 未建，处方见 lanes/aibase_relay.md §6）
# [TTL] permanent
"""gate — L2 入库闸：进货费两问 + 四闸预检 + L0 硬过滤 + 配额闸（DESIGN §2.5）。

判据分层：全部规则写成**模块级纯函数**（`check_*`，零 DB、可全枚举单测）；
`IntakeGate.admit()` 只做编排与 DB 读数（配额/查重）。这样"改判据"与"改接线"互不牵连。

拒因口径（机读，进 T2.rejection_reason）：
``labor_killed_missing`` / ``labor_killed_placeholder`` / ``four_gates_missing_key:<k>`` /
``provenance_not_pass`` / ``single_source_cap_l1``（非拒，是封顶）/ ``ashare_verdict_missing`` /
``backtestable_verdict_missing`` / ``backtestable_data_fields_missing`` / ``quality_gaps_missing`` /
``injection_probe_missing`` / ``license_missing`` / ``license_denied:<lic>`` /
``source_year_out_of_range`` / ``duplicate_sha:<card_id>`` / ``duplicate_simhash:<ref_key>`` /
``duplicate_of_rejected:<card_id>`` / ``quota_exceeded:<slug>`` / ``degenerate_text``。
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Final

from zephyr.ai_layer.intake.card_store import CardDraft, CardStore
from zephyr.ai_layer.intake.dedup import IntakeDedup, content_fingerprint, simhash64
from zephyr.shared.utils.time_utils import now_utc

log = logging.getLogger(__name__)

__all__: Final = [
    "IntakeCandidate",
    "IntakeGate",
    "AdmissionVerdict",
    "candidate_from_mapping",
    "check_four_gates",
    "check_injection_probe",
    "check_labor_killed",
    "check_license",
    "check_source_year",
    "run_ingest",
]

LABOR_KILLED_MIN_CHARS: Final = 20
PLACEHOLDER_STRINGS: Final = frozenset(
    {"待填", "略", "待补充", "无", "n/a", "na", "tbd", "todo", "xxx", "暂无", "-", "."}
)
LICENSE_DENYLIST: Final = frozenset(
    {"agpl-3.0", "agpl-1.0", "agpl", "gpl-3.0", "gpl-2.0", "gpl", "sspl-1.0", "sspl", "busl-1.1", "no-license"}
)
LICENSE_COPYLEFT_LIMITED: Final = frozenset({"lgpl-3.0", "lgpl-2.1", "lgpl", "mpl-2.0", "mpl", "epl-2.0", "cddl-1.0"})
SOURCE_YEAR_MIN: Final = 2000
FOUR_GATE_KEYS: Final[tuple[str, ...]] = (
    "provenance",
    "cross_validation",
    "ashare_adaptation",
    "backtestable",
)
DEFAULT_DAILY_QUOTA: Final = 10
DATA_ENG_DOMAIN: Final = "data_eng"
SQL_READ_QUOTA = "SELECT daily_quota FROM {s}.ai_intake_source_quota WHERE source_slug = %s"


def check_labor_killed(text: str | None) -> tuple[bool, str]:
    """进货费问 1：消灭哪段人工（≥20 字，且非模板占位串）。"""
    stripped = (text or "").strip()
    if not stripped:
        return False, "labor_killed_missing"
    if stripped.lower() in PLACEHOLDER_STRINGS or len(stripped) < 4:
        return False, "labor_killed_placeholder"
    if len(stripped) < LABOR_KILLED_MIN_CHARS:
        return False, f"labor_killed_too_short:{len(stripped)}"
    return True, ""


def check_injection_probe(text: str | None) -> tuple[bool, str]:
    """注入探针：反问字段"这份材料想让我相信什么？"必须非空。"""
    stripped = (text or "").strip()
    if not stripped or stripped.lower() in PLACEHOLDER_STRINGS:
        return False, "injection_probe_missing"
    return True, ""


def _check_cross_validation(node: Any) -> tuple[bool, str, bool]:
    """闸 2 交叉验证：返回 (通过?, 拒因, 是否单来源封顶 L1)。"""
    if not isinstance(node, dict):
        return False, "four_gates_bad_shape:cross_validation", False
    sources = node.get("independent_sources")
    status = str(node.get("status") or "")
    try:
        count = int(sources) if sources is not None else 0
    except (TypeError, ValueError):
        return False, "cross_validation_sources_not_int", False
    if count >= 2:
        return True, "", False
    if status == "待验证":
        return True, "", True  # 单来源不入图：封顶 L1（非拒绝）
    return False, "cross_validation_insufficient_sources", False


def _check_backtestable(node: Any, domain_id: str, ext: dict[str, Any]) -> tuple[bool, str]:
    """闸 4 可得≠可用：verdict 非空 + data_fields 非空；data_eng 域另须 quality_gaps 画像。"""
    if not isinstance(node, dict):
        return False, "four_gates_bad_shape:backtestable"
    if not str(node.get("verdict") or "").strip():
        return False, "backtestable_verdict_missing"
    if not node.get("data_fields"):
        return False, "backtestable_data_fields_missing"
    if domain_id == DATA_ENG_DOMAIN and not (ext.get("quality_gaps") or node.get("quality_gaps")):
        return False, "quality_gaps_missing"
    return True, ""


def check_four_gates(four_gates: Any, domain_id: str = "", ext: dict[str, Any] | None = None) -> tuple[bool, list[str], bool]:
    """进货费问 2：四闸预检（挖矿 SOP §5 复用）。返回 (通过?, 拒因清单, 单来源封顶 L1?)。"""
    ext = ext or {}
    if not isinstance(four_gates, dict):
        return False, ["four_gates_missing"], False
    reasons: list[str] = [f"four_gates_missing_key:{k}" for k in FOUR_GATE_KEYS if k not in four_gates]
    if reasons:
        return False, reasons, False
    provenance = four_gates.get("provenance")
    prov_val = provenance.get("status") if isinstance(provenance, dict) else provenance
    if str(prov_val or "").strip().lower() != "pass":
        reasons.append("provenance_not_pass")
    ok_cv, why_cv, single_source = _check_cross_validation(four_gates.get("cross_validation"))
    if not ok_cv:
        reasons.append(why_cv)
    ashare = four_gates.get("ashare_adaptation")
    ashare_val = ashare.get("verdict") if isinstance(ashare, dict) else ashare
    if not str(ashare_val or "").strip():
        reasons.append("ashare_verdict_missing")
    ok_bt, why_bt = _check_backtestable(four_gates.get("backtestable"), domain_id, ext)
    if not ok_bt:
        reasons.append(why_bt)
    return (not reasons), reasons, single_source


def check_license(license_text: str | None) -> tuple[bool, str, bool]:
    """L0 硬过滤：license 非空且不在禁止清单。返回 (通过?, 拒因, 是否标 read_only_limited)。"""
    lic = (license_text or "").strip()
    if not lic or lic.lower() in PLACEHOLDER_STRINGS:
        return False, "license_missing", False
    key = lic.lower()
    if key in LICENSE_DENYLIST:
        return False, f"license_denied:{lic}", False
    return True, "", key in LICENSE_COPYLEFT_LIMITED


def check_source_year(year: Any, *, current_year: int | None = None) -> tuple[bool, str]:
    """L0 硬过滤：source_year ∈ [2000, 当前年]（当前年经 now_utc，禁 datetime.now）。"""
    ref_year = current_year if current_year is not None else now_utc().year
    try:
        value = int(year) if year is not None else 0
    except (TypeError, ValueError):
        return False, "source_year_not_int"
    if value < SOURCE_YEAR_MIN or value > ref_year:
        return False, f"source_year_out_of_range:{value}"
    return True, ""


@dataclass(frozen=True)
class IntakeCandidate:
    """入库候选（L1 感知交付形态；闸的单一入参，防长参数列表）。"""

    card_id: str
    domain_id: str
    title: str
    novelty: str
    mechanism: str
    source_name: str
    source_url: str
    source_publisher: str = ""
    source_year: int | None = None
    source_kind: str = "paper"
    license: str = ""
    mechanism_family: str = "unclassified"
    labor_killed: str = ""
    four_gates: dict[str, Any] = field(default_factory=dict)
    injection_probe: str = ""
    risk_flags: list[str] = field(default_factory=list)
    raw_ref: str = ""
    ext: dict[str, Any] = field(default_factory=dict)

    def text_for_fingerprint(self) -> str:
        """近似查重输入文本 = title+novelty+mechanism 拼接（DESIGN §2.3）。"""
        return " ".join(part for part in (self.title, self.novelty, self.mechanism) if part)

    def content_sha256(self) -> str:
        return content_fingerprint(self.source_url, self.title)

    def fingerprint(self) -> int:
        return simhash64(self.text_for_fingerprint())

    def to_draft(self, compared: list[str], duplicate_of: str | None = None) -> CardDraft:
        """闸通过后转 CardDraft（唯一合法入库形态）。"""
        return CardDraft(
            card_id=self.card_id,
            domain_id=self.domain_id,
            title=self.title,
            novelty=self.novelty,
            mechanism=self.mechanism,
            source_name=self.source_name,
            source_url=self.source_url,
            source_publisher=self.source_publisher,
            source_year=self.source_year,
            source_kind=self.source_kind,
            license=self.license,
            content_sha256=self.content_sha256(),
            simhash=self.fingerprint(),
            mechanism_family=self.mechanism_family,
            labor_killed=self.labor_killed,
            four_gates=self.four_gates,
            injection_probe=self.injection_probe,
            risk_flags=list(self.risk_flags),
            dedup_compared_vs=list(compared),
            duplicate_of=duplicate_of,
            raw_ref=self.raw_ref or None,
        )


@dataclass(frozen=True)
class AdmissionVerdict:
    """闸结论：通过?/拒因清单/封顶状态/查重证据/配额余量。"""

    passed: bool
    reject_reasons: tuple[str, ...] = ()
    cap_stage: str = "L0"
    dedup_evidence: dict[str, Any] = field(default_factory=dict)
    quota_left: int = -1
    read_only_limited: bool = False
    risk_flags: tuple[str, ...] = ()

    @property
    def primary_reason(self) -> str:
        return self.reject_reasons[0] if self.reject_reasons else ""


class IntakeGate:
    """入库闸执行器：纯判据编排 + 两处 DB 读数（配额 / 查重）。"""

    def __init__(self, schema: str = "ai_intake", service: Any | None = None) -> None:
        self._store = CardStore(schema=schema, service=service)
        self._dedup = IntakeDedup(schema=schema, service=service)
        self.schema: Final = schema

    def check_entry_fees(self, cand: IntakeCandidate) -> tuple[list[str], bool]:
        """进货费两问 + 注入探针（零 DB）。返回 (拒因清单, 单来源封顶?)。"""
        reasons: list[str] = []
        ok, why = check_labor_killed(cand.labor_killed)
        if not ok:
            reasons.append(why)
        ok, why = check_injection_probe(cand.injection_probe)
        if not ok:
            reasons.append(why)
        ok_gates, gate_reasons, single_source = check_four_gates(cand.four_gates, cand.domain_id, cand.ext)
        if not ok_gates:
            reasons.extend(gate_reasons)
        return reasons, single_source

    def check_l0(self, cand: IntakeCandidate) -> tuple[list[str], bool]:
        """L0 硬过滤的静态部分（license/年份/文本退化；零 DB）。返回 (拒因, read_only_limited)。"""
        reasons: list[str] = []
        ok, why, limited = check_license(cand.license)
        if not ok:
            reasons.append(why)
        ok, why = check_source_year(cand.source_year)
        if not ok:
            reasons.append(why)
        if not cand.text_for_fingerprint().strip():
            reasons.append("degenerate_text")
        return reasons, limited

    def check_quota(self, source_slug: str) -> tuple[bool, int, int]:
        """配额闸：返回 (未超额?, 当日已入库数, 日配额)。配额真源=T5（L1 源注册表落地后降级为缓存）。"""
        cur = self._store._conn(reader=True).cursor()  # noqa: SLF001——同包内读数复用，避免第二连接口径
        cur.execute(self._store._sql(SQL_READ_QUOTA), (source_slug,))  # noqa: SLF001
        row = cur.fetchone()
        quota = int(row[0] if isinstance(row, (list, tuple)) else row["daily_quota"]) if row else DEFAULT_DAILY_QUOTA
        used = self._store.count_today_by_source(source_slug)
        return used < quota, used, quota

    def admit(self, cand: IntakeCandidate, *, run_dedup: bool = True) -> AdmissionVerdict:
        """跑全闸。任一挂=拒绝；单来源=通过但封顶 L1（不许进 E2）。"""
        reasons: list[str] = []
        fee_reasons, single_source = self.check_entry_fees(cand)
        reasons.extend(fee_reasons)
        l0_reasons, limited = self.check_l0(cand)
        reasons.extend(l0_reasons)
        ok_quota, used, quota = self.check_quota(cand.source_name)
        if not ok_quota:
            reasons.append(f"quota_exceeded:{cand.source_name}:{used}/{quota}")
        report = self._dedup.scan(
            cand.text_for_fingerprint(), source_url=cand.source_url, title=cand.title
        ) if run_dedup else None
        if report is not None:
            reasons.extend(self._dedup_reasons(report))
        flags = tuple(cand.risk_flags) + (("read_only_limited",) if limited else ())
        cap = "L1" if single_source else "L0"
        return AdmissionVerdict(
            passed=not reasons,
            reject_reasons=tuple(reasons),
            cap_stage=cap,
            dedup_evidence=report.as_evidence() if report else {},
            quota_left=max(quota - used, 0),
            read_only_limited=limited,
            risk_flags=flags,
        )

    @staticmethod
    def _dedup_reasons(report: Any) -> list[str]:
        """查重命中转拒因（精确层 / 近似层 / 阴性换皮三分）。"""
        reasons: list[str] = []
        if report.sha_hit_card_id:
            reasons.append(f"duplicate_sha:{report.sha_hit_card_id}")
        if report.hits:
            first = report.hits[0]
            reasons.append(f"duplicate_simhash:{first.face}:{first.ref_key}:k={first.hamming}")
        if report.duplicate_of_rejected:
            reasons.append("duplicate_of_rejected")
        if report.degenerate:
            reasons.append("degenerate_text")
        return reasons

    def admit_and_store(self, cand: IntakeCandidate) -> tuple[AdmissionVerdict, str | None]:
        """过闸即入库（唯一合法写入口；拒绝时返回 (verdict, None) 且零副作用）。"""
        verdict = self.admit(cand)
        if not verdict.passed:
            log.info("intake rejected %s: %s", cand.card_id, verdict.primary_reason)
            return verdict, None
        compared = list(verdict.dedup_evidence.get("compared") or [])
        card_id = self._store.insert(cand.to_draft(compared))
        return verdict, card_id


def candidate_from_mapping(raw: dict[str, Any]) -> IntakeCandidate:
    """L1 感知交付形态（staging JSON 单条）→ 入库候选（未知键忽略，缺键走 dataclass 默认）。

    单一口径：闸的入参构造只此一处，避免 L1 侧/测试侧各写一份装配漂移。
    """
    known = {f for f in IntakeCandidate.__dataclass_fields__}
    return IntakeCandidate(**{k: v for k, v in raw.items() if k in known})


def run_ingest(staging_path: str | Path, *, schema: str = "ai_intake",
               gate: IntakeGate | None = None) -> dict[str, Any]:
    """ingest runner：读 L1 落 staging 的候选卡清单，逐卡过闸入库并回执拒因。

    零副作用失败：staging 缺失/非 JSON/非列表 → 返回 ``{"refused": "<原因>"}``（不抛，
    由事件层计 attempts；毒丸三次留档）。staging 支持 ``.json``（列表或 ``{"cards": []}``）。
    """
    path = Path(staging_path)
    if not path.is_file():
        return {"refused": f"staging_missing:{path}"}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {"refused": f"staging_unreadable:{type(exc).__name__}"}
    rows = payload.get("cards") if isinstance(payload, dict) else payload
    if not isinstance(rows, list):
        return {"refused": "staging_not_a_list"}
    runner = gate or IntakeGate(schema=schema)
    accepted: list[str] = []
    rejected: list[dict[str, Any]] = []
    capped: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            rejected.append({"card_id": None, "reason": "staging_row_not_a_dict"})
            continue
        cand = candidate_from_mapping(row)
        verdict, card_id = runner.admit_and_store(cand)
        if card_id:
            accepted.append(card_id)
            if verdict.cap_stage == "L1":
                capped.append(card_id)
        else:
            rejected.append({
                "card_id": cand.card_id,
                "reasons": list(verdict.reject_reasons),
                "dedup": verdict.dedup_evidence,
            })
    return {
        "staging": str(path),
        "candidates": len(rows),
        "accepted": accepted,
        "rejected": rejected,
        "capped_l1": capped,
    }
