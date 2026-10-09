# [BLUEPRINT] MOD-DATSEC-001 | docs/03_modules/_domain_data_security/ai_masking_pipeline/blueprint.md | §F128 接点①
# [MODULE] zephyr.data_security.wiring.lsg_masking_front
# [DOMAIN] D_DATA_SEC
# [DEPENDENCIES] zephyr.data_security.ai_masking_pipeline；zephyr.security.llm_defense.llm_security.gateway（仅类型引用）；zephyr.data_security.wiring.audit_sink
# [CONSUMERS] LLM 调用面装配点（scan_input 必经 LSG 之前的统一脱敏前置——运行时按需装配）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 零侵入（不改 LSGSecurityGateway 一行——组合包装）；先脱敏后防御（脱敏产物再过 l1，
#   防"密文绕过检测"与"原文喂模型"两头）；未知/缺省 purpose→L1 原样放行（保持 LSG 现行为）；
#   L2+ 审计 before 只落摘要（长度/数字字符/标的/数值 token 计数）不落原文；逐次调用一条审计事件；
#   同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_data_security/ai_masking_pipeline/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] policies 为空抛 AiMaskingError（透传 MOD-DATSEC-001 契约）；扫描链异常透传 LSG 语义
# [TESTS] tests/data_security/test_wiring_lsg_masking_front.py
# [A_module] module_id=MOD-DATSEC-005 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
LSGMaskingFront — LSG l1 前置脱敏包装层（MOD-DATSEC-005，F128 接点①）。

F128 接线复活（st-menu-t1b2-20260930，Owner 2026-09-30 夜批 known-gap→接线复活）。
挖矿卡 docs/_working/night_sweep/b_audit/nb1_b2_f128_data_security_wiring.md
处方形态 a：gateway 外部组合包装（LSG 是门禁热区，零改一行，对齐最小变更）。

语义（先脱敏后防御）：
  purpose 解析（显式参 > metadata["masking_purpose"] > default_purpose）
  → 未知 purpose 回落 default（出厂=L1 原样放行，保持 LSG 现行为）
  → AiMaskingPipeline.mask_for_llm 分级脱敏（L2 序列统计摘要 / L3 金额标的泛化 /
    L4 仅统计摘要；策略表驱动，Fail-Closed 契约在管道层）
  → 脱敏产物才进 gateway.scan_input（l1 注入检测看的是脱敏后文本）
  → 逐次调用一条脱敏前后对比审计（L2+ before 红字化=只落摘要不落原文），
    统一经 JsonlAuditSink 落规则册声明路径（F128 缺口②）。

输出侧：scan_output 直通委托 gateway.scan_output——LSG L3 输出防御是输出侧本职；
L2-L4 分级脱敏为不可逆统计摘要，无"反查还原"语义；可逆件（FPE）还原仅存在于
数据出口白名单通道（见 data_exit_guard.reveal_payload）。

# [ALGO_FLOW] external: docs/03_modules/_domain_data_security/algo_flow/wiring__init__.yaml
"""

from __future__ import annotations

from typing import Any, Callable, Final, Mapping

from zephyr.data_security.ai_masking_pipeline import (
    AiMaskingError,
    AiMaskingPipeline,
    MaskingAuditRecord,
    MaskingLevel,
    MaskingPolicy,
)
from zephyr.data_security.wiring.audit_sink import DEFAULT_SINK_RELPATH, JsonlAuditSink

__all__: Final = ["LSGMaskingFront"]

#: L1 出厂策略（缺省 purpose/未知 purpose 落此——保持 LSG 现行为：原样放行）
_DEFAULT_POLICY_KEY: Final = "default"


def _summarize(text: str) -> str:
    """before 红字化摘要：只落长度与实体计数，不落原文（挖矿卡 L4 纪律推广到 L2+）。"""
    digits = sum(1 for ch in text if ch.isdigit())
    return f"[before已红字化] 字符数={len(text)} 数字字符数={digits}"


class LSGMaskingFront:
    """LSG l1 前置脱敏包装层（组合 gateway，零侵入）。"""

    def __init__(
        self,
        gateway: object,
        *,
        policies: Mapping[str, MaskingPolicy] | None = None,
        default_purpose: str = _DEFAULT_POLICY_KEY,
        audit_sink: Callable[[object], None] | None = None,
    ) -> None:
        if gateway is None:
            raise AiMaskingError("gateway 为空（LSGSecurityGateway 必填）")
        if not default_purpose:
            raise AiMaskingError("default_purpose 为空")
        table: dict[str, MaskingPolicy] = dict(policies) if policies else {}
        if not table:
            table[_DEFAULT_POLICY_KEY] = MaskingPolicy(level=MaskingLevel.L1)
        if default_purpose not in table:
            table[default_purpose] = MaskingPolicy(level=MaskingLevel.L1)
        self._gateway = gateway
        self._default_purpose = default_purpose
        self._pipeline = AiMaskingPipeline(policies=table, audit_sink=self._redacting_sink)
        self._audit_sink = audit_sink if audit_sink is not None else JsonlAuditSink(DEFAULT_SINK_RELPATH)
        self._levels: dict[str, MaskingLevel] = {k: v.level for k, v in table.items()}

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _redacting_sink(self, record: MaskingAuditRecord) -> None:
        """审计红字化中转：L2+ 的 before 换摘要（原文不落盘），L1 保留原文（放行即无变换）。"""
        if record.level is not MaskingLevel.L1:
            record = MaskingAuditRecord(
                purpose=record.purpose,
                level=record.level,
                before=_summarize(record.before),
                after=record.after,
                masked_at=record.masked_at,
                note=record.note,
            )
        self._audit_sink(record)

    def resolve_purpose(self, purpose: str | None, metadata: Mapping[str, Any] | None = None) -> str:
        """purpose 解析：显式参 > metadata["masking_purpose"] > default；未知→default（L1 现行为）。"""
        resolved = purpose or (metadata or {}).get("masking_purpose") or self._default_purpose
        resolved = str(resolved)
        return resolved if resolved in self._levels else self._default_purpose

    # ── 对外（与 LSGSecurityGateway 同形签名+purpose 扩展参） ─────────────

    async def scan_input(
        self,
        text: str,
        source: str = "direct_input",
        metadata: dict[str, Any] | None = None,
        mode: object = None,
        purpose: str | None = None,
    ) -> object:
        """先脱敏后防御：mask_for_llm → gateway.scan_input(脱敏产物)。"""
        from zephyr.security.llm_defense.llm_security.gateway import ScanMode  # noqa: PLC0415 延迟 import 防环

        resolved = self.resolve_purpose(purpose, metadata)
        masked = self._pipeline.mask_for_llm(resolved, text)
        kwargs: dict[str, Any] = {"source": source, "metadata": metadata}
        kwargs["mode"] = mode if mode is not None else ScanMode.INPUT_ONLY
        return await self._gateway.scan_input(masked, **kwargs)

    async def scan_output(
        self,
        text: str,
        source: str = "model_output",
        metadata: dict[str, Any] | None = None,
        mode: object = None,
    ) -> object:
        """输出侧直通委托（LSG L3 本职；分级脱敏不可逆，无反查还原语义）。"""
        from zephyr.security.llm_defense.llm_security.gateway import ScanMode  # noqa: PLC0415 延迟 import 防环

        kwargs: dict[str, Any] = {"source": source, "metadata": metadata}
        kwargs["mode"] = mode if mode is not None else ScanMode.OUTPUT_ONLY
        return await self._gateway.scan_output(text, **kwargs)

    # ── 查询面 ───────────────────────────────────────────────────────────

    def level_of(self, purpose: str) -> MaskingLevel:
        """用途级别查询（未知用途回落 default 的级别）。"""
        return self._levels.get(self.resolve_purpose(purpose), self._levels[self._default_purpose])

    @property
    def default_purpose(self) -> str:
        return self._default_purpose
