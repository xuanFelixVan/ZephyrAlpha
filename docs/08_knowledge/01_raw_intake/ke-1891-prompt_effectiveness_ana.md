---
module_id: KE-1800
status: active
title: 2.221 Prompt Effectiveness Analytics - prompt_effectiveness_analytics.py (🆕 v0.2
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.221 Prompt Effectiveness Analytics - prompt_effectiveness_analytics.py (🆕 v0.2

2.221 Prompt Effectiveness Analytics - prompt_effectiveness_analytics.py (🆕 v0.20.0 - 盲点271 — Prompt模板到决策质量的全链路因果关系分析)

**致命问题**：PromptFactoryGovernance(v0.17.0)做Prompt的版本化+AB测试，但AB测试结果是aggregate-level的"新版vs旧版哪个分数高"。缺少的是**granular-level因果分析**：Prompt的哪个段落对诊断准确率贡献最大？哪个system message短语导致false-positive rate上升？在100%AI施工下，prompt就是code——缺少prompt-to-outcome的可解释性等同于缺少code profiling。
**对标**：Anthropic Prompt Caching Research + LangSmith Prompt Tracing + Datadog LLM Observability

```python
@dataclass
class PromptEffectivenessReport:
    prompt_id: str
    version: str
    total_uses: int
    avg_decision_quality: float
    false_positive_contribution: float  # 此prompt引起的FP占总FP的比例
    segment_impact: dict[str, float]  # {"introduction": 0.5, "context": 0.3, "instructions": 0.2}
    top_performing_sections: list[str]
    bottom_performing_sections: list[str]

class PromptEffectivenessAnalytics:
    ANALYSIS_WINDOW_USES: int = 100

    async def analyze_prompt_effectiveness(self,
                                             prompt_id: str) -> PromptEffectivenessReport:
        uses = await self._load_prompt_uses(prompt_id,
            limit=self.ANALYSIS_WINDOW_USES)
        if len(uses) < 30:
            return None  # 样本不足
        # 1. Aggregate: 此prompt的平均决策质量
        avg_quality = sum(u.decision_quality_score for u in uses) / len(uses)
        fp_ratio = sum(1 for u in uses if u.was_false_positive) / len(uses)
        total_fps = await self._total_fps_in_window(self.ANALYSIS_WINDOW_USES)
        fp_contribution = uses.count_false_positives / total_fps if total_fps > 0 else 0
        # 2. Segment-level causal attribution:
        #   将prompt按段落拆分→每段落embedding→与outcome做回归
        segment_impacts = await self._compute_segment_impact(uses)
        top_sections = sorted(segment_impacts.items(), key=lambda x: -x[1])[:2]
        bottom_sections = sorted(segment_impacts.items(), key=lambda x: x[1])[:2]
        report = PromptEffectivenessReport(
            prompt_id=prompt_id, version=self._current_version(prompt_id),
            total_uses=len(uses), avg_decision_quality=avg_quality,
            false_positive_contribution=fp_contribution,
            segment_impact=segment_impacts,
            top_performing_sections=[s[0] for s in top_sections],
            bottom_performing_sections=[s[0] for s in bottom_sections])
        if fp_contribution > 0.20:  # 单个prompt贡献>20%FP
            self.FLE.notify_owner("PROMPT_FP_HOTSPOT",
                f"Prompt {prompt_id} v{report.version} contributes "
                f"{fp_contribution:.0%} of all false positives. "
                f"Weak sections: {report.bottom_performing_sections}. "
                f"Recommend: targeted prompt section rewrite for bottom sections, "
                f"not full prompt replacement (minimizes regression risk for strong sections).")
        return report
```
