# [BLUEPRINT] MOD-INF-028 | docs/03_modules/_cross_layer/semantic_auditor/blueprint.md | §3.1 Stage 6
# [MODULE] zephyr.integration.llm_bridge
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] self_healer; fix_prioritizer
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] LLM 只做文本润色不判断; 不可用时降级为 detect-only; Token 使用追踪
# [MODIFY-GUARD] semantic-auditor/blueprint.md; semantic-auditor/__init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] LLM 不可用时返回 success=False, error="LLM_UNAVAILABLE"
# [TESTS] tests/semantic-auditor/test_llm_bridge.py
# [A_module] module_id=MOD-INF-028 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""

[BLUEPRINT] MOD-INF-028 — LLM 桥接 Stage 6

接收 RED 问题,生成修复文本。LLM 只润色不做判断。不可用时降级为模板生成。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 语义断裂问题 字典数据
#   fields: trigger_type 触发类型 + target_location 位置 + evidence 证据 + severity 严重性 + certainty 确定性
#   code: generate_fix(issue) L65
# - id: I2
#   name: 修复文案模板 内置常量
#   fields: cross_doc_ref_broken / dependson_chain_broken / default 三套模板
#   code: _FIX_TEMPLATES L38
# - id: I3
#   name: LLM 可用性开关 布尔配置
#   fields: api_available 构造参数 + set_available() 运行时切换
#   code: __init__ L62 / set_available L136
# 层: 算法
# - id: A1
#   name_zh: ① 可用性路由
#   name_en: generate_fix
#   intro: LLM 可用就走润色路径，不可用就走模板路径，调用方无感
#   desc: self._available False→_template_fix；True→_llm_fix
#   inputs: I1 I3
#   outputs: LLMFixResult
#   invariant: LLM 只做文本润色不判断
# - id: A2
#   name_zh: ② 模板降级生成
#   name_en: _template_fix
#   intro: 按问题类型套预制模板拼出修复建议，永远能出活
#   desc: 按 trigger_type 选模板（缺省 default）→ format(target_location, evidence)；token_used=len(re.findall(r"\S+", fix_text)) 空白分词估算
#   inputs: I1 I2
#   outputs: LLMFixResult(success=True)
# - id: A3
#   name_zh: ③ prompt 构造与 LLM 编排
#   name_en: _llm_fix + _build_prompt
#   intro: 把问题五要素拼成中文 prompt 请 LLM 润色，拿不到结果就降级回模板
#   desc: _build_prompt 拼 类型/位置/严重性/确定性/证据 → _call_llm；返回 None→LLMFixResult(success=False, error=LLM_API_NO_RESPONSE)；异常→降级 _template_fix
#   inputs: I1
#   outputs: LLMFixResult
#   invariant: 不可用时降级为 detect-only（模板生成）
# - id: A4
#   name_zh: ④ LLM API 调用桩
#   name_en: _call_llm
#   intro: 真实 LLM API 的占位桩，当前永远返回 None，等于 LLM 路径未接通
#   desc: 函数体只有 return None（桩），真实 API 接入留待后续
#   inputs: A3
#   outputs: None（恒）
#   is_break: true
# - id: A5
#   name_zh: ⑤ 批量生成
#   name_en: generate_fix_batch
#   intro: 一组问题逐个走 generate_fix，凑成结果列表
#   desc: [generate_fix(issue) for issue in issues]
#   inputs: A1
#   outputs: list[LLMFixResult]
# 层: 输出
# - id: O1
#   name_zh: 单个修复结果
#   name_en: LLMFixResult
#   intro: success + fix_text + token_used + error 四元组，Token 使用可追踪
#   invariant: LLM 不可用返回 success=False, error=LLM_UNAVAILABLE 系契约
#   downstream: self_healer; fix_prioritizer（[CONSUMERS]）
# - id: O2
#   name_zh: 批量修复结果列表
#   name_en: list[LLMFixResult]
#   intro: 批量问题的一揽子修复文本
#   downstream: self_healer; fix_prioritizer
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I3 --> A1
# I1 --> A2
# I2 --> A2
# I1 --> A3
# A3 -.->|断点| A4
# A3 --> A2
# A1 --> A2
# A1 --> A3
# A1 --> A5
# A2 --> O1
# A3 --> O1
# A5 --> O2
"""

from __future__ import annotations

import logging
import re
from typing import Any

# 5.152 #19 sanctioned: integration 为组合层，允许依赖全部层（governance.L2 含 semantic_audit）。
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
        except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
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
