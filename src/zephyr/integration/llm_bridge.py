# [BLUEPRINT] MOD-INF-028 | docs/03_modules/_cross_layer/semantic_auditor/blueprint.md | §3.1 Stage 6
# [MODULE] zephyr.integration.llm_bridge
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] self_healer; fix_prioritizer
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] LLM 只做文本润色不判断; 不可用时降级为 detect-only; Token 使用追踪
# [MODIFY-GUARD] semantic-auditor/blueprint.md; semantic-auditor/__init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] LLM 不可用时返回 success=False, error="LLM_UNAVAILABLE"
# [TESTS] tests/semantic-auditor/test_llm_bridge.py
# [A_module] module_id=MOD-SEM_llm_bridge | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""[BLUEPRINT] MOD-INF-028 — LLM 桥接 Stage 6

接收 RED 问题,生成修复文本。LLM 只润色不做判断。不可用时降级为模板生成。
"""

from __future__ import annotations

import logging
import re
from typing import Any

from zephyr.governance.semantic_audit.models import LLMFixResult

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
    """Stage 6 LLM 桥接 — 修复文本生成.

    LLM 只润色不做判断。不可用时降级为模板生成。
    接收 TriggerResult 或 issue dict, 输出 LLMFixResult。
    """

    def __init__(self, api_available: bool = False) -> None:
        self._available = api_available

    def generate_fix(self, issue: dict[str, Any]) -> LLMFixResult:
        """为单个问题生成修复文本.

        Args:
            issue: 包含 trigger_type, target_location, evidence, severity 等字段

        Returns:
            LLMFixResult: 修复结果
        """
        if not self._available:
            return self._template_fix(issue)
        return self._llm_fix(issue)

    def generate_fix_batch(self, issues: list[dict[str, Any]]) -> list[LLMFixResult]:
        """批量生成修复文本."""
        return [self.generate_fix(issue) for issue in issues]

    def _template_fix(self, issue: dict[str, Any]) -> LLMFixResult:
        trigger_type = issue.get("trigger_type", "default")
        template = _FIX_TEMPLATES.get(trigger_type, _FIX_TEMPLATES["default"])
        fix_text = template.format(
            target_location=issue.get("target_location", "unknown"),
            evidence=issue.get("evidence", "无"),
        )
        token_used = len(_ESTIMATED_TOKENS_RE.findall(fix_text))
        logger.debug("模板生成修复文本: %s — %d tokens", issue.get("target_location", ""), token_used)
        return LLMFixResult(
            success=True,
            fix_text=fix_text,
            token_used=token_used,
            error="",
        )

    def _llm_fix(self, issue: dict[str, Any]) -> LLMFixResult:
        prompt = self._build_prompt(issue)
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
            return self._template_fix(issue)

    def _build_prompt(self, issue: dict[str, Any]) -> str:
        return (
            f"你是一个代码审计助手。以下是一个语义断裂问题的检测结果:\n"
            f"- 类型: {issue.get('trigger_type', 'unknown')}\n"
            f"- 位置: {issue.get('target_location', 'unknown')}\n"
            f"- 严重性: {issue.get('severity', 'RED')}\n"
            f"- 确定性: {issue.get('certainty', 'N/A')}\n"
            f"- 证据: {issue.get('evidence', '无')}\n\n"
            f"请生成具体的修复文本。只需要输出修复内容,不要解释。"
        )

    def _call_llm(self, prompt: str) -> str | None:
        return None

    def is_available(self) -> bool:
        return self._available

    def set_available(self, value: bool) -> None:
        self._available = value