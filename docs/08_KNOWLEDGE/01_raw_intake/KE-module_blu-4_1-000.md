---
module_id: KE-module_blu-4_1-000
title: 4.1 查询接口
category: module_blueprint
---

# 4.1 查询接口

4.1 查询接口

```python
class AuditQuery:
    def by_task(self, task_id: str) -> TaskAuditSummary:
        """查询任务级摘要——快速浏览"""

    def by_task_details(self, task_id: str) -> list[FileAuditDetail]:
        """查询任务关联的文件级明细——问题定位"""

    def by_agent(self, agent_id: str, time_range: tuple[datetime, datetime]) -> list[TaskAuditSummary]:
        """查询某个 Agent 在某时段的所有操作"""

    def by_target(self, file_path: str) -> list[FileAuditDetail]:
        """查询某个文件被谁操作过——完整 lineage"""

    def by_permission_level(self, level: str, time_range: tuple[datetime, datetime]) -> list[TaskAuditSummary]:
        """查询某个权限级别的所有操作"""

    def by_anomaly(self, anomaly_type: str | None = None, min_score: float = 0.7) -> list[AuditEntryV1]:
        """查询异常事件——按类型/最小分数过滤"""

    def by_drift(self, severity: str | None = None) -> list[AuditEntryV1]:
        """查询蓝图漂移事件——按严重度过滤"""

    def by_cost(self, min_cost_usd: float = 0.0, time_range: tuple[datetime, datetime] | None = None) -> list[AuditEntryV1]:
        """按成本查询——FinOps 审计"""

    def trail_for_ai_context(self, session_id: str) -> str:
        """为 AI agent 生成当前 session 的审计摘要——Markdown 格式，AI 零推理可消费"""

    def rebuild_index(self) -> int:
        """从 JSONL 重建 SQLite 索引——返回重建记录数"""

    def verify_integrity(self, fast_mode: bool = True) -> IntegrityReport:
        """校验密码学完整性——fast_mode 仅校验 Merkle root，否则逐条校验"""

class IntegrityReport(BaseModel):
    is_valid: bool
    total_entries: int
    hash_chain_breaks: list[int]  # 断裂处的 JSONL 行号
    hmac_failures: list[int]
    merkle_mismatches: list[str]  # Merkle 批次 ID
    checked_at: datetime
```
