# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_heritage
# [MODULE] zephyr.ai_layer.heritage.closure_check
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.ai_layer.heritage.policy (load_policy——kind/理由枚举真源);
#                zephyr.ai_layer.heritage.store (HeritageStore 只读——签名匹配数据源)
# [CONSUMERS] 工单流关单链（P2 落地时挂进关单链，工单 kind ∈ incident_fix/defect_fix/redblu_finding）;
#             zephyr.ai_layer.heritage.heritage_events (closure_payload_to_actions 回执预检);
#             月度体检窗（对账代行，工单流落地前由月度对账双保险，DESIGN §2.9 位次裁定）
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] 位次裁定：传承登记是关单四闸全过之后的产出检查，不是第五道放行闸（四闸管质量登记管沉淀）;
#              判据全部纯函数（回执校验/签名匹配/对账对齐零 DB，DB 行由调用方注入）;
#              关单回执 heritage_ref | no_new_pattern 二选一，理由枚举三选一（known_pattern/
#              mechanical_debt/dup_of），词表真源=config/heritage_policy.yaml closure 节;
#              签名匹配只读 V2 缺陷面：signature 先按正则解释（编译失败退化子串匹配），命中带配方派工;
#              gate 立案走 OBJ_R 四步流水线（本稿只出规则不立 gate，DESIGN §2.9）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L7_heredity/DESIGN.md §2.9（关单登记机检规则真源）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 回执缺登记面→(False, 拒因)（告警由调用方发，本模块不发火）；畸形 no_new_pattern→拒因
#                  bad_no_new_pattern；signature 正则坏→退化子串匹配不炸（fail-open 逐条）
# [TESTS] tests/ai_layer/heritage/test_heritage_closure_check.py（合法三理由+heritage_ref 全过/
#         缺登记样本被拦/签名匹配带出配方/对账器违例清单）
# [TTL] permanent
"""closure_check — 关单强制传承登记机检（对接主文档 §三 关单四闸）。

设计真源：``docs/_working/ai_layer_vision/L7_heredity/DESIGN.md`` §2.9。

规则：工单 kind ∈ {incident_fix, defect_fix, redblu_finding} 的关单回执必须携带
``heritage_ref: <entry_id>``（新建/命中缺陷模式）**或** ``no_new_pattern`` 声明，声明理由
枚举三选一：``known_pattern: <entry_id>`` / ``mechanical_debt`` / ``dup_of: <case_id>``。
缺两者=关单回执校验失败→告警+工单重开（告警与重开由工单流侧执行，本模块出机读裁定）。

读路径（先于写路径存在）：派工前机检匹配 V2 缺陷签名，命中即把 recipe 附进工单
（主文档 §3.5"命中带配方派工"的落地）。工单流 P2 落地前由月度体检对账代行。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Final

from zephyr.ai_layer.heritage.policy import HeritagePolicy, load_policy
from zephyr.shared.utils.time_utils import now_utc

__all__: Final = [
    "HeritageSignatureMatch",
    "check_signature_match",
    "reconcile_closed_orders",
    "validate_receipt",
]

ENTRY_ID_RE: Final = re.compile(r"^HT-[0-9]{8}-[0-9]{3}$")
CASE_ID_RE: Final = re.compile(r"^CASE-[0-9]{4,}-[0-9A-Za-z-]+$")


@lru_cache(maxsize=1)
def _cached_policy() -> HeritagePolicy:
    """closure 词表缓存（config/heritage_policy.yaml 装载一次；修订走 OBJ_R 重启生效）。"""
    return load_policy()


@dataclass(frozen=True)
class HeritageSignatureMatch:
    """签名匹配命中（派工配方附带的供给端）。"""

    entry_id: str
    pattern_norm: str
    signature: str
    recipe: str


def _receipt_heritage_ref(receipt: dict[str, Any]) -> str:
    """回执 heritage_ref 字段（str/dict 两态兼容）。"""
    ref = receipt.get("heritage_ref")
    if isinstance(ref, dict):
        return str(ref.get("entry_id") or "")
    return str(ref or "").strip()


def _receipt_no_new_pattern(receipt: dict[str, Any]) -> tuple[str, str]:
    """回执 no_new_pattern 字段 → (reason, ref)；缺席=("", "")。"""
    raw = receipt.get("no_new_pattern")
    if isinstance(raw, dict):
        return str(raw.get("reason") or "").strip(), str(raw.get("ref") or "").strip()
    text = str(raw or "").strip()
    if not text:
        return "", ""
    if ":" in text:
        reason, _, ref = text.partition(":")
        return reason.strip(), ref.strip()
    return text, ""


def validate_receipt(kind: str, receipt: dict[str, Any]) -> tuple[bool, str]:
    """§2.9 关单回执机检（纯函数）。返回 (通过?, 拒因/通过码)。

    kind 不在强制清单=不在射程直接通过（closure_kind_not_in_scope）；
    heritage_ref 形态必须 HT-*；no_new_pattern 理由枚举三选一，known_pattern 带HT-*、
    dup_of 带 CASE-*；两者并存判畸形单选违规。
    """
    policy = _cached_policy()
    if kind not in policy.closure.kinds_requiring_heritage:
        return True, "closure_kind_not_in_scope"
    heritage_ref = _receipt_heritage_ref(receipt)
    reason, reason_ref = _receipt_no_new_pattern(receipt)
    if heritage_ref and reason:
        return False, "both_heritage_ref_and_no_new_pattern"
    if heritage_ref:
        if not ENTRY_ID_RE.match(heritage_ref):
            return False, f"bad_heritage_ref:{heritage_ref}"
        return True, "heritage_ref"
    if reason or raw_present(receipt):
        if reason not in policy.closure.no_new_pattern_reasons:
            return False, f"bad_no_new_pattern_reason:{reason}"
        if reason == "known_pattern" and not ENTRY_ID_RE.match(reason_ref):
            return False, f"bad_known_pattern_ref:{reason_ref}"
        if reason == "dup_of" and not CASE_ID_RE.match(reason_ref):
            return False, f"bad_dup_of_ref:{reason_ref}"
        return True, f"no_new_pattern:{reason}"
    return False, "missing_heritage_registration"


def raw_present(receipt: dict[str, Any]) -> bool:
    """no_new_pattern 键是否在回执中（含显式空串=声明存在但畸形）。"""
    return "no_new_pattern" in receipt


def check_signature_match(
    symptoms: str, defect_rows: list[dict[str, Any]]
) -> list[HeritageSignatureMatch]:
    """派工前签名匹配（读路径，纯函数）：symptoms 文本 vs V2 缺陷 signature 面。

    signature 先按正则解释（re.IGNORECASE；编译失败/纯文本退化子串匹配），
    命中按 occurrence_count 降序返回（高频坑优先）。
    """
    text = str(symptoms or "")
    if not text.strip():
        return []
    matches: list[HeritageSignatureMatch] = []
    for row in defect_rows:
        signature = str(row.get("signature") or "")
        if not signature.strip():
            continue
        if _signature_hits(signature, text):
            matches.append(
                HeritageSignatureMatch(
                    entry_id=str(row.get("entry_id") or ""),
                    pattern_norm=str(row.get("pattern_norm") or ""),
                    signature=signature,
                    recipe=str(row.get("recipe") or ""),
                )
            )
    matches.sort(key=lambda m: int(row_count(defect_rows, m.entry_id)), reverse=True)
    return matches


def row_count(defect_rows: list[dict[str, Any]], entry_id: str) -> int:
    """取指定条目的 occurrence_count（缺失按 0）。"""
    for row in defect_rows:
        if str(row.get("entry_id") or "") == entry_id:
            try:
                return int(row.get("occurrence_count") or 0)
            except (TypeError, ValueError):
                return 0
    return 0


def _signature_hits(signature: str, text: str) -> bool:
    """单条签名命中判定：正则优先，坏正则/纯文本退化子串（fail-open 逐条，不炸整面）。"""
    try:
        return re.search(signature, text, re.IGNORECASE) is not None
    except re.error:
        return signature.lower() in text.lower()


@dataclass(frozen=True)
class ClosureViolation:
    """月度对账违例（关单回执缺传承登记面）。"""

    work_order_id: str
    kind: str
    why: str


def reconcile_closed_orders(receipts: list[dict[str, Any]]) -> list[ClosureViolation]:
    """月度对账器（纯函数，工单流 P2 落地前的双保险代行）：违例清单交告警面。"""
    violations: list[ClosureViolation] = []
    for receipt in receipts:
        kind = str(receipt.get("kind") or "")
        ok, why = validate_receipt(kind, receipt)
        if not ok:
            violations.append(
                ClosureViolation(
                    work_order_id=str(receipt.get("work_order_id") or ""),
                    kind=kind,
                    why=why,
                )
            )
    return violations


def alert_message(violations: list[ClosureViolation]) -> str:
    """违例 → 一行告警文案（调用方投 Alerter；零违例返回空串）。"""
    if not violations:
        return ""
    heads = ", ".join(f"{v.work_order_id}({v.why})" for v in violations[:3])
    return f"关单传承登记对账违例 {len(violations)} 例: {heads}"


def due_month(*, as_of: Any = None) -> str:
    """对账归属月（YYYY-MM，now_utc 派生；as_of 可注入）。"""
    stamp = as_of or now_utc()
    return stamp.strftime("%Y-%m")
