# [BLUEPRINT] MOD-INF-034 | docs/03_modules/_cross_layer/model_profiler/blueprint.md | §3
# [MODULE] zephyr.intelligence.model_profiling.exam_judge
# [DOMAIN] D-INTELLIGENCE
# [DEPENDENCIES] zephyr.intelligence.model_profiling.__init__
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
# [TTL] task_bound

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
        """解析裁判输出的 JSON（含思维链清理）。

        步骤:
            1. 剥离思维链标签（think/thinking/reflection/Mattis 等成对/不成对标签）
            2. 正则提取首个 JSON 对象
            3. 容错 json.loads + 字段缺省填充 + 数值 clamp [0,1]
            4. 解析失败返回 JudgeResult(reasoning="parse_error: ...")，不抛异常
        """
        clean = raw
        # 1. 剥离成对思维链标签及其内容，再清残余孤立标签
        for tag in ("think", "thinking", "reflection", "reasoning", "Mattis"):
            clean = re.sub(
                rf"<{tag}[^>]*>.*?</{tag}>",
                "",
                clean,
                flags=re.IGNORECASE | re.DOTALL,
            )
            clean = re.sub(
                rf"</?{tag}[^>]*>",
                "",
                clean,
                flags=re.IGNORECASE,
            )

        # 2. 正则提取首个 JSON 对象
        match = re.search(r"\{[\s\S]*\}", clean)
        if not match:
            return JudgeResult(reasoning=f"parse_error: no JSON found in: {raw[:200]}")
        json_str = match.group(0)

        # 3. 容错 json.loads
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            return JudgeResult(reasoning=f"parse_error: {e}; raw={raw[:200]}")

        if not isinstance(data, dict):
            return JudgeResult(reasoning=f"parse_error: not a dict: {type(data)}")

        def _clamp(v: Any, default: float = 0.0) -> float:
            try:
                f = float(v)
            except (TypeError, ValueError):
                return default
            return max(0.0, min(1.0, f))

        return JudgeResult(
            correctness=_clamp(data.get("correctness")),
            completeness=_clamp(data.get("completeness")),
            depth=_clamp(data.get("depth")),
            hallucination_detected=bool(data.get("hallucination_detected", False)),
            overall=_clamp(data.get("overall")),
            reasoning=str(data.get("reasoning", "")),
        )


class DeterministicJudge:
    """P1-4: 确定性裁判 — 无 LLM judge_chat 时的 judge 轨回退。

    用关键词覆盖率 + 结构完整性 + 长度合理性 给出独立评分。
    比 rubric 严格 (penalize 缺失关键词), 比 LLM judge 简单 (无语义理解)。

    用途:
        - judge_chat=None 时, 避免 judge 轨完全缺失导致三轨退化为单轨
        - 提供独立的第二意见 (不直接复用 rubric 分)
        - 零成本 (无 API 调用)

    评分维度:
        - correctness: 关键词覆盖率 (expected_contains 命中率)
        - completeness: 结构完整性 (expected_structure_keys 存在率)
        - depth: 长度合理性 (50~10000 字为合理区间)
        - overall: 0.5*correctness + 0.3*completeness + 0.2*depth
    """

    # 长度合理性区间 (字符数)
    _MIN_LEN = 50
    _MAX_LEN = 10_000

    def __init__(self) -> None:
        pass  # 无状态, 纯函数式

    def judge(self, case: Any, candidate_answer: str) -> JudgeResult:
        """对候选答案进行确定性评分。

        Args:
            case: ExamTestCase，包含 expected_contains / expected_structure_keys
            candidate_answer: 被测模型的输出文本
        Returns:
            JudgeResult 多维评分 (reasoning 含诊断明细)
        """
        text = candidate_answer or ""
        text_lower = text.lower()

        # 1. 关键词覆盖率 (0-1)
        expected_contains = getattr(case, "expected_contains", []) or []
        if expected_contains:
            hits = sum(1 for kw in expected_contains if kw.lower() in text_lower)
            keyword_cov = hits / len(expected_contains)
        else:
            keyword_cov = 0.5  # 无关键词要求时给中性分

        # 2. 结构完整性 (0-1) — 检查 expected_structure_keys 是否在文本中出现
        expected_keys = getattr(case, "expected_structure_keys", []) or []
        if expected_keys:
            hits = sum(1 for k in expected_keys if k in text or k.lower() in text_lower)
            structure_score = hits / len(expected_keys)
        else:
            structure_score = 0.5  # 无结构要求时给中性分

        # 3. 长度合理性 (0-1)
        length = len(text)
        if length < self._MIN_LEN:
            # 太短: 0~50 字 → 0~0.5 线性
            length_score = (length / self._MIN_LEN) * 0.5
        elif length > self._MAX_LEN:
            # 太长: >10000 字 → 衰减但不归零
            length_score = max(0.5, 1.0 - (length - self._MAX_LEN) / 20_000)
        else:
            length_score = 1.0

        # 加权综合 (关键词 0.5 + 结构 0.3 + 长度 0.2)
        overall = 0.5 * keyword_cov + 0.3 * structure_score + 0.2 * length_score

        return JudgeResult(
            correctness=round(keyword_cov, 3),
            completeness=round(structure_score, 3),
            depth=round(length_score, 3),
            hallucination_detected=False,
            overall=round(overall, 3),
            reasoning=(
                f"deterministic: kw={keyword_cov:.2f} "
                f"struct={structure_score:.2f} len={length_score:.2f} "
                f"(len={length})"
            ),
        )
