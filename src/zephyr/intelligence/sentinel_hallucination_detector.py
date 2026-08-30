# [BLUEPRINT] MOD-INF-050 | docs/03_modules/MOD-INF-050/
# [MODULE] zephyr.intelligence.sentinel_hallucination_detector
# [DOMAIN] D_INTELLIGENCE
# [DEPENDENCIES] zephyr.orchestrator.hallucination_detector
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 不另立重复检测引擎——检测语义全部委托 orchestrator CoVe 引擎；本层只做包装+审计留痕增强；审计链只追加不修改
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SentinelDetectorError(ZA-IT-0010)——claim 为空 fail-closed
# [TESTS] tests/intelligence/test_sentinel_hallucination_detector.py
# [A_module] module_id=MOD-INF-050 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
sentinel 幻觉检测器（MOD-INF-050）——intelligence 域哨兵封装。

 backlog 裁定：不另立重复引擎。检测语义 100% 委托
:mod:`zephyr.orchestrator.hallucination_detector` 的 CoVe 引擎
（触发矩阵/风险阈值/降级级联/预算门禁），本层只做两件增强：

1. **审计留痕**：每次 detect 追加一条 SentinelAuditRecord（claim 只存
   sha256 指纹不存原文），prev_hash 链式防篡改，verify_audit_chain() 可离线校验。
2. **观测统计**：stats() 汇总检测次数/幻觉命中/兜底分布，供哨兵看板消费。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: detector 参数
#   fields: 参数 detector（无注解）
#   code: sentinel_hallucination_detector.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① SentinelHallucinationDetector
#   name_en: SentinelHallucinationDetector
#   intro: CoVe 幻觉检测引擎的 intelligence 域哨兵封装（委托模式）。
#   desc: CoVe 幻觉检测引擎的 intelligence 域哨兵封装（委托模式）。；公共方法（定义序）: detector, detect, audit_trail, verify_audit_chain, stats；源码…
#   inputs: detector
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: SentinelHallucinationDetector
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Final

from zephyr.orchestrator.hallucination_detector import (
    HallucinationDetector,
    HallucinationResult,
    RiskLevel,
)

__all__: Final = [
    "SentinelAuditRecord",
    "SentinelDetectorError",
    "SentinelHallucinationDetector",
]

_GENESIS_HASH: Final[str] = "0" * 64


class SentinelDetectorError(Exception):
    """ZA-IT-0010: sentinel 幻觉检测入口校验失败。"""

    error_code = "ZA-IT-0010"


@dataclass(frozen=True)
class SentinelAuditRecord:
    """哨兵审计留痕（只追加；claim 仅存指纹，不落原文）。"""

    seq: int
    claim_hash: str
    is_hallucination: bool
    risk_level: str
    fallback_used: str | None
    prev_hash: str
    record_hash: str


def _record_hash(rec: SentinelAuditRecord) -> str:
    blob = json.dumps(
        {
            "seq": rec.seq,
            "claim_hash": rec.claim_hash,
            "is_hallucination": rec.is_hallucination,
            "risk_level": rec.risk_level,
            "fallback_used": rec.fallback_used,
            "prev_hash": rec.prev_hash,
        },
        sort_keys=True,
        ensure_ascii=False,
    )
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


class SentinelHallucinationDetector:
    """CoVe 幻觉检测引擎的 intelligence 域哨兵封装（委托模式）。"""

    def __init__(self, *, detector: HallucinationDetector | None = None) -> None:
        # 默认构造无 caller 的引擎：双模型不可达时自动走 keyword 规则兜底（fail-closed 可用）。
        self._detector = detector if detector is not None else HallucinationDetector()
        self._records: list[SentinelAuditRecord] = []

    @property
    def detector(self) -> HallucinationDetector:
        """被委托的 CoVe 引擎（只读）。"""
        return self._detector

    # ── 委托检测 ─────────────────────────────────────────────────────

    def detect(
        self,
        claim: str,
        *,
        risk_level: str | RiskLevel = RiskLevel.M,
        context: dict[str, Any] | None = None,
        handoff_approved: bool = False,
    ) -> HallucinationResult:
        """检测一次 claim（语义完全委托底层 CoVe 引擎），随后追加审计留痕。"""
        if not claim or not claim.strip():
            raise SentinelDetectorError("claim 不得为空")
        result = self._detector.detect(
            claim,
            context=context,
            risk_level=risk_level,
            handoff_approved=handoff_approved,
        )
        self._append_audit(result)
        return result

    # ── 审计链 ───────────────────────────────────────────────────────

    def audit_trail(self) -> list[SentinelAuditRecord]:
        return list(self._records)

    def verify_audit_chain(self) -> bool:
        prev = _GENESIS_HASH
        for rec in self._records:
            if rec.prev_hash != prev:
                return False
            if rec.record_hash != _record_hash(rec):
                return False
            prev = rec.record_hash
        return True

    # ── 统计 ─────────────────────────────────────────────────────────

    def stats(self) -> dict[str, Any]:
        fallbacks: dict[str, int] = {}
        for rec in self._records:
            key = rec.fallback_used or "cove"
            fallbacks[key] = fallbacks.get(key, 0) + 1
        return {
            "total_detects": len(self._records),
            "hallucination_count": sum(1 for r in self._records if r.is_hallucination),
            "audit_records": len(self._records),
            "fallback_distribution": fallbacks,
        }

    # ── 内部 ─────────────────────────────────────────────────────────

    def _append_audit(self, result: HallucinationResult) -> None:
        prev_hash = self._records[-1].record_hash if self._records else _GENESIS_HASH
        rec = SentinelAuditRecord(
            seq=len(self._records) + 1,
            claim_hash=HallucinationDetector.claim_hash(result.claim),
            is_hallucination=result.is_hallucination,
            risk_level=result.risk_level,
            fallback_used=result.fallback_used,
            prev_hash=prev_hash,
            record_hash="",
        )
        rec = SentinelAuditRecord(
            seq=rec.seq,
            claim_hash=rec.claim_hash,
            is_hallucination=rec.is_hallucination,
            risk_level=rec.risk_level,
            fallback_used=rec.fallback_used,
            prev_hash=rec.prev_hash,
            record_hash=_record_hash(rec),
        )
        self._records.append(rec)
