---
module_id: KE-module_blu-2_212_decision_justification_q-000
title: 2.212 Decision Justification Quality - decision_explanation_quality.py (🆕 v0.20.
category: module_blueprint
---

# 2.212 Decision Justification Quality - decision_explanation_quality.py (🆕 v0.20.

2.212 Decision Justification Quality - decision_explanation_quality.py (🆕 v0.20.0 - 盲点262 — FLE解释自己决策的质量自评估)

**致命问题**：FLE每次NOTIFY_OWNER时都附带一段"为什么我做了这个决定"的解释文本。但FLE从未度量过这些解释的质量——Owner能理解吗？解释包含了太多技术细节吗？解释是否遗漏了关键上下文？在1人+AI维护下，FLE的解释质量直接影响Owner的triage效率和信任度。劣质解释→Owner花更多时间理解→认知负载增加→信任下降。
**对标**：Anthropic LLM Explanation Evaluator + Google PAIR Explainability Framework + Microsoft AI Explanation Quality Score

```python
@dataclass
class ExplanationQualityMetrics:
    decision_id: str
    readability_score: float          # Flesch-Kincaid: 30太学术, 80太幼稚, 50-60最佳
    jargon_density: float              # 技术术语占词比 >15%→警告
    context_completeness: float        # 是否引用了必要的上下文(系统状态+历史+影响)
    actionability_score: float         # Owner读完能否立即行动？0=模糊, 1=可直行
    owner_acknowledgment_time_sec: float  # Owner从收到到ACK的延迟(=间接质量指标)
    owner_override_rate: float          # 对此类解释的override率

class DecisionJustificationQuality:
    TARGET_READABILITY: tuple[float, float] = (45, 65)
    MAX_JARGON_DENSITY: float = 0.12
    POOR_QUALITY_ACK_LAG_SEC: float = 600  # Owner>10min未ACK→解释可能不清楚

    async def evaluate_explanation(self, decision: FLEDecision,
                                     explanation: str) -> ExplanationQualityMetrics:
        metrics = ExplanationQualityMetrics(
            decision_id=decision.id,
            readability_score=self._flesch_kincaid(explanation),
            jargon_density=self._compute_jargon_ratio(explanation),
            context_completeness=self._check_context_coverage(explanation, decision.context),
            actionability_score=self._score_actionability(explanation))
        # 综合性评分
        quality_score = (
            self._readability_penalty(metrics.readability_score) * 0.25
            + (1 - metrics.jargon_density / self.MAX_JARGON_DENSITY) * 0.25
            + metrics.context_completeness * 0.25
            + metrics.actionability_score * 0.25)
        # 低质量→累积→触发自动优化
        if quality_score < 0.60:
            self._record_poor_explanation(decision, metrics)
            recent_poor_rate = self._recent_explanation_quality_rate(days=7)
            if recent_poor_rate > 0.20:
                self.FLE.notify_owner("EXPLANATION_QUALITY_DEGRADED",
                    f"{recent_poor_rate:.0%} of recent FLE explanations are low quality. "
                    f"FLE will adjust explanation template: reduce jargon, add executive summary first. "
                    f"Check justification quality for: {self._top_poor_patterns(3)}")
                await self._auto_adjust_explanation_template()
        return metrics
```
