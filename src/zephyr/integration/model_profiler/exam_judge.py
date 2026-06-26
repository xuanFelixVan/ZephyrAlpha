# [BLUEPRINT] MOD-INF-034 | docs/03_modules/_cross_layer/model-profiler/blueprint.md
# [MODULE] zephyr.integration.model_profiler.exam_judge
# [DOMAIN] D-INTEGRATION
# [DEPENDENCIES] zephyr.integration.model_profiler.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]

"""
ExamJudge --- LLM-as-judge 评分器

对开放式题（architecture_design/audit/hallucination_detect/OLYMPIAD题）用强模型
作为裁判，按多维 rubric 打分。裁判模型与被测模型不同（防自评偏差）。

v3.0.5 新增：阶段三极限深度测试的核心评分机制之一。
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from typing import Any

_log = logging.getLogger(__name__)


@dataclass
class JudgeResult:
    """LLM裁判评分结果。"""
    correctness: float = 0.0       # 事实正确性 0-1
    completeness: float = 0.0     # 要点覆盖完整性 0-1
    depth: float = 0.0            # 推理深度 0-1
    hallucination_detected: bool = False  # 是否检测到幻觉
    overall: float = 0.0          # 综合分 0-1
    reasoning: str = ""           # 裁判理由


JUDGE_SYSTEM_PROMPT = """You are an expert judge evaluating AI model responses.
Evaluate the candidate answer against the reference answer and rubric.

Be strict but fair. Reward depth, penalize hallucination.

Output JSON:
{
  "correctness": 0.0-1.0,
  "completeness": 0.0-1.0,
  "depth": 0.0-1.0,
  "hallucination_detected": true/false,
  "overall": 0.0-1.0,
  "reasoning": "brief explanation"
}
"""


class ExamJudge:
    """LLM-as-judge：用强模型对开放式题评分。

    用法:
        judge_chat = DeepSeekV4Chat(model="deepseek-v4-pro-thinking")
        judge = ExamJudge(judge_chat)
        result = judge.judge(case, candidate_answer)
        # result.overall = 0.85

    设计要点:
        - 裁判模型与被测模型不同（防自评偏差）
        - 多维评分：correctness/completeness/depth/hallucination/overall
        - 裁判 prompt 包含 rubric + 参考答案 + 候选答案
        - 仅对 OLYMPIAD 题和开放式题启用（控制成本）
    """

    def __init__(self, judge_chat: Any) -> None:
        self._chat = judge_chat

    def judge(self, case: Any, candidate_answer: str) -> JudgeResult:
        """对候选答案进行多维评分。

        Args:
            case: ExamTestCase，包含 prompt 和期望答案
            candidate_answer: 被测模型的输出文本
        Returns:
            JudgeResult 多维评分
        """
        reference = self._build_reference(case)
        judge_prompt = (
            f"Question:\n{case.prompt}\n\n"
            f"Reference Answer:\n{reference}\n\n"
            f"Candidate Answer:\n{candidate_answer}\n\n"
            "Evaluate the candidate answer. Be strict but fair."
        )

        try:
            raw = self._chat.ask(
                judge_prompt,
                system=JUDGE_SYSTEM_PROMPT,
                temperature=0.0,
            )
            return self._parse_judge_json(raw)
        except Exception as e:
            _log.warning("ExamJudge: judge failed: %s", e)
            return JudgeResult(reasoning=f"judge_error: {e}")

    def _build_reference(self, case: Any) -> str:
        """从 ExamTestCase 构建参考答案。"""
        parts = []
        if case.expected_contains:
            parts.append(f"Key concepts expected: {', '.join(case.expected_contains)}")
        if getattr(case, "expected_conclusion", ""):
            parts.append(f"Expected conclusion: {case.expected_conclusion}")
        if case.expected_structure_keys:
            parts.append(f"Required structure: {', '.join(case.expected_structure_keys)}")
        return "\n".join(parts) if parts else "N/A"

    def _parse_judge_json(self, raw: str) -> JudgeResult:
        """解析裁判输出的 JSON（含思维链清理）。"""
        clean = raw
        for tag in<tool_call>Write<arg_key>file_path</arg_key><arg_value>D:\ZephyrAlpha\src\z