---
module_id: KE-module_blu-2_241_owner_causal_trace_query-000
title: 2.241 Owner Causal Trace Query Interface - owner_why_query_interface.py (🆕 v0.22
category: module_blueprint
---

# 2.241 Owner Causal Trace Query Interface - owner_why_query_interface.py (🆕 v0.22

2.241 Owner Causal Trace Query Interface - owner_why_query_interface.py (🆕 v0.22.0 - 盲点290 — Owner无法对FLE进行"为什么"的因果溯因查询)

**致命问题**：结构化通知协议(v0.21.0)解决了FLE→Owner的单向推送问题。但Owner需要反向能力：在任何时候对FLE发起"为什么"查询。例如："2026-03-15 14:32:00 你为什么要重启order_router?"——这个问题的答案需要从DETECT→DIAGNOSE→REPAIR→VERIFY的全链路证据中重建因果链。现有的decision_provenance和action_rationale存储了离散数据点，但无统一的、可遍历的因果图让Owner或审计者追溯。
**对标**：Datadog Notebooks + Jupyter Interactive Investigation + GitLens Blame/History + Google Cloud Asset Inventory + AWS Config Timeline

```python
@dataclass
class CausalTraceNode:
    decision_id: str
    timestamp: datetime
    node_type: str         # "TRIGGER"|"EVIDENCE"|"LLM_INFERENCE"|"ACTION"|"VERIFICATION"
    description: str       # 自然语言："Metric CPU_LOAD rose to 92% (p99=85%)"
    evidence_links: list[str]  # 链接到底层metric、log、config change
    llm_rationale: str | None  # LLM给出的推理文本
    parent_nodes: list[str]    # causal upstream nodes
    confidence: float

class OwnerWhyQueryInterface:
    async def answer_why_inquiry(self,
                                    query: WhyQuery) -> CausalTraceReport:
        """Handle query like: 'Why did FLE restart order_router on 2026-03-15 14:32?'"""
        # 1. Resolve: 找到匹配的decision
        decision = await self._resolve_decision_from_query(query)
        if not decision:
            return CausalTraceReport(found=False,
                message=f"No FLE decision found matching '{query.natural_language}' "
                        f"in timeframe {query.time_range}.")
        # 2. Build causal chain: 从trigger→evidence→diagnosis→repair→verification
        chain = []
        chain.append(CausalTraceNode(
            decision_id=decision.id,
            timestamp=decision.detection_time,
            node_type="TRIGGER",
            description=f"Anomaly detected: {decision.anomaly.metric_name} "
                        f"at {decision.anomaly.z_score:.1f}σ "
                        f"(value={decision.anomaly.value:.2f}, baseline={decision.anomaly.baseline:.2f})",
            evidence_links=[decision.anomaly.metric_dashboard_url],
            parent_nodes=[]))
        for inference in decision.llm_inferences:
            chain.append(CausalTraceNode(
                decision_id=decision.id,
                timestamp=inference.timestamp,
                node_type="LLM_INFERENCE",
                description=f"LLM stage {inference.stage}: {inference.input_context[:80]}...",
                llm_rationale=inference.output_text,
                evidence_links=inference.referenced_sources,
                parent_nodes=[c.decision_id for c in chain[-1:]]))
        chain.append(CausalTraceNode(
            decision_id=decision.id,
            timestamp=decision.action_time,
            node_type="ACTION",
            description=f"FLE executed: {decision.action_type} on {decision.target_system}. "
                        f"Rationale: {decision.rationale[:100]}",
            llm_rationale=decision.rationale,
            evidence_links=[decision.a
