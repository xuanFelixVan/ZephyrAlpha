# [BLUEPRINT] MOD-INF-028 | docs/03_modules/_cross_layer/semantic_auditor/blueprint.md | §3.1 Stage 6
# [MODULE] zephyr.governance.semantic_audit.llm_bridge
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.semantic_audit.models
# [CONSUMERS] self_healer; fix_prioritizer
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] LLM 只做文本润色不判断; 不可用时降级为 detect-only; Token 使用追踪
# [MODIFY-GUARD] 修改 prompt 必须同步 llm_bridge_prompt.yaml
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] LLM 不可用时返回 success=False, error="LLM_UNAVAILABLE"
# [TESTS] tests/semantic-auditor/test_llm_bridge.py
# [A_module] module_id=MOD-GOV_llm_bridge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""[BLUEPRINT] MOD-INF-028 — LLM 桥接 Stage 6

接收 RED 问题,生成修复文本。LLM 只润色不做判断。不可用时降级为模板生成。
"""

from __future__ import annotations

import logging
import re

from zephyr.governance.semantic_audit.models import LLMFixResult, TriggerResult

logger = logging.getLogger(__name__)

__all__ = [
    "LLMBridge",
]

_FIX_TEMPLATES: dict[str, str] = {
    "cross_doc_ref_broken": (
        "修复建议: 文件引用断裂 — {target_location}\n"
        "证据: {evidence}\n"
        "操作: 验证目标文件是否存在,若已移动则更新路径,若已删除则移除引用。"
    ),
    "dependson_chain_broken": (
        "修复建议: 依赖链断裂 — {target_location}\n"
        "证据: {evidence}\n"
        "操作: 检查 depends_on 声明,验证目标模块是否已重构,更新 at 章节号。"
    ),
    "default": ("修复建议: 语义断裂 — {target_location}\n证据: {evidence}\n操作: 人工审查是否需要修复。"),
}

_ESTIMATED_TOKENS_RE = re.compile(r"\S+")


class LLMBridge:
    def __init__(self, api_available: bool = False) -> None:
        self._available = api_available

    def generate_fix(self, trigger: TriggerResult) -> LLMFixResult:
        if not self._available:
            return self._template_fix(trigger)
        return self._llm_fix(trigger)

    def generate_fix_batch(self, triggers: list[TriggerResult]) -> list[LLMFixResult]:
        return [self.generate_fix(t) for t in triggers]

    def _template_fix(self, trigger: TriggerResult) -> LLMFixResult:
        template = _FIX_TEMPLATES.get(
            trigger.trigger_type,
            _FIX_TEMPLATES["default"],
        )
        fix_text = template.format(
            target_location=trigger.target_location,
            evidence=trigger.evidence,
        )
        token_used = len(_ESTIMATED_TOKENS_RE.findall(fix_text))
        logger.debug("模板生成修复文本: %s — %d tokens", trigger.target_location, token_used)
        return LLMFixResult(
            success=True,
            fix_text=fix_text,
            token_used=token_used,
            error="",
        )

    def _llm_fix(self, trigger: TriggerResult) -> LLMFixResult:
        prompt = self._build_prompt(trigger)
        try:
            response = self._call_llm(prompt)
            if response is None:
                return LLMFixResult(
                    success=False,
                    fix_text="",
                    token_used=len(_ESTIMATED_TOKENS_RE.findall(prompt)),
                    error="LLM_API_NO_RESPONSE",
                )
            return LLMFixResult(
                success=True,
                fix_text=response,
                token_used=len(_ESTIMATED_TOKENS_RE.findall(response)),
                error="",
            )
        except Exception as exc:
            logger.warning("LLM 调用失败, 降级到模板: %s", exc, exc_info=True)
            return self._template_fix(trigger)

    def _build_prompt(self, trigger: TriggerResult) -> str:
        # 修复 prompt 注入：对用户可控字段进行基本净化（去换行+截断）
        def _sanitize(text: str) -> str:
            return text.replace("\n", " ").replace("\r", " ")[:500]
        return (
            f"你是一个代码审计助手。以下是一个语义断裂问题的检测结果:\n"
            f"- 类型: {_sanitize(trigger.trigger_type)}\n"
            f"- 位置: {_sanitize(trigger.target_location)}\n"
            f"- 严重性: {trigger.severity.value}\n"
            f"- 确定性: {trigger.certainty}\n"
            f"- 证据: {_sanitize(trigger.evidence)}\n\n"
            f"请生成具体的修复文本。只需要输出修复内容,不要解释。"
        )

    def _call_llm(self, prompt: str) -> str | None:
        return None

    def is_available(self) -> bool:
        return self._available

    def set_available(self, value: bool) -> None:
        self._available = value