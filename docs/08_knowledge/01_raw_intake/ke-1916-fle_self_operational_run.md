---
module_id: KE-1825
status: active
title: 2.240 FLE Self-Operational Runbook Auto-Generation - fle_self_runbook_generator.
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.240 FLE Self-Operational Runbook Auto-Generation - fle_self_runbook_generator.

2.240 FLE Self-Operational Runbook Auto-Generation - fle_self_runbook_generator.py (🆕 v0.22.0 - 盲点289 — FLE发现的新修复模式未自动文档化为人类可执行的运维手册)

**致命问题**：在1人+AI维护的语境下，Owner不可能记住FLE发现的每一个新修复模式。当FLE学到"如果order_router的connection_pool_usage>80%且avg_latency>200ms→先重启workers→若无效→调整pool_size+50%"这个3步修复流程→这个发现只存在于FLE的KB中。但Owner需要知道这个修复逻辑来：理解FLE的行为、在FLE不可用时手动执行、审核FLE的修复是否合理。FLE应该自动从KB中的lesson条目生成结构化的、人类可读的运维runbook——就像PagerDuty的自动Runbook生成。
**对标**：Google SRE Runbook Automation + PagerDuty Automated Runbooks + GitLab Runbook Documentation + AWS Systems Manager Automation Documents

```python
@dataclass
class FLESelfGeneratedRunbook:
    runbook_id: str
    trigger_condition: str      # "WHEN order_router.connection_pool_usage > 80%"
    severity: str
    fle_repair_steps: list[str] # FLE采取的步骤（自然语言）
    human_manual_steps: list[str]  # Owner手动操作的步骤
    rollback_steps: list[str]   # 如果修复失败如何回滚
    estimated_mttr_min: float
    last_validated_at: datetime
    source_kb_entries: list[str]   # 这些知识来自哪些KB条目
    owner_review_status: str    # "PENDING_REVIEW"|"APPROVED"|"REJECTED"

class FLESelfRunbookGenerator:
    MIN_RUNBOOK_CONFIDENCE: int = 3  # 修复在≥3个不同anomaly上成功才生成runbook

    async def generate_runbook_from_knowledge(self,
                                                pattern_id: str) -> FLESelfGeneratedRunbook | None:
        kb_entries = await self.kb.query_by_pattern(pattern_id)
        repair_results = await self.repair_effectiveness_loop.get_results_for_pattern(pattern_id)
        successful_repairs = [r for r in repair_results if r.was_effective]
        if len(successful_repairs) < self.MIN_RUNBOOK_CONFIDENCE:
            return None  # 不够成熟，过早生成runbook可能误导
        # 从KB条目和repair记录中提取修复步骤
        steps = await self._extract_repair_steps(successful_repairs)
        human_steps = await self._translate_fle_steps_to_human(steps)
        rollback = await self._derive_rollback_steps(steps, successful_repairs)
        runbook = FLESelfGeneratedRunbook(
            runbook_id=f"RB-{pattern_id}-{datetime.now():%Y%m%d}",
            trigger_condition=self._build_trigger_condition(kb_entries),
            severity=kb_entries[0].severity,
            fle_repair_steps=steps,
            human_manual_steps=human_steps,
            rollback_steps=rollback,
            estimated_mttr_min=self._estimate_mttr(successful_repairs),
            last_validated_at=datetime.now(),
            source_kb_entries=[e.id for e in kb_entries],
            owner_review_status="PENDING_REVIEW")
        await self._persist_runbook(runbook)
        self.FLE.notify_owner("NEW_RUNBOOK_GENERATED",
            f"FLE auto-generated runbook '{runbook.runbook_id}' for pattern {pattern_id}. "
            f"Trigger: {runbook.trigger_condition}. "
            f"Steps: {len(steps)} FLE steps, {len(human_steps)} human steps. "
            f"Based on {len(successful_repairs)} successful repairs. "
            f"Review and approve: {self._runbook_review_url(runbook.runbook_id)}.")
        return runbook
`
