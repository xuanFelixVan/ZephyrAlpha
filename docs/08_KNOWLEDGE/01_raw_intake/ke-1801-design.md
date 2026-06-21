---
module_id: KE-1710-----------------------d-0-000
status: active
title: 2.14 确定性重放——审计日志→系统状态重建（决策 D-020-34）
category: module_blueprint
---

# 2.14 确定性重放——审计日志→系统状态重建（决策 D-020-34）

2.14 确定性重放——审计日志→系统状态重建（决策 D-020-34）

> **决策 D-020-34**（新增）：对标 Goldman trade reconstruction——审计日志的最高价值是支持"回到任意时刻，精确重建系统状态"。仅记录"谁做了什么"不够——必须记录操作前后的完整状态快照。关键文件操作记录 `sha256_before` → `sha256_after`，通过重放审计日志可验证重建状态的 SHA-256 是否与记录一致。

```yaml
deterministic_replay:
  design:
    principle: "sha256_before + sha256_after → 任何时间点状态可重建"
    coverage: "关键文件操作 100% 记录 sha256_before/after"

  replay_layers:
    L1_file_state: "通过 sha256_after 链→重建任意时刻文件内容哈希"
    L2_git_state: "通过 git commit SHA→重建代码仓库状态"
    L3_system_config: "通过配置变更事件→重建系统配置状态"

  validation:
    weekly_replay_test: "随机选取 3 个时间点，重放审计日志验证 SHA-256 一致性"
    on_demand: "zephyr audit replay --at '2026-05-03T14:00:00Z' → 输出该时刻的完整文件状态哈希映射"

  limitation:
    partial_coverage: "仅记录有审计事件的操作——未被审计覆盖的操作无法重建"
    external_dependencies: "MCP/API 调用结果无法从审计日志重建——需外部系统配合"
```

```python
class DeterministicReplayEngine:
    """从审计日志重建系统状态"""

    def replay_to(self, target_time: datetime) -> dict[str, str]:
        """重放审计日志至指定时间——返回 {file_path: sha256} 状态映射"""

    def verify_replay(self, target_time: datetime) -> ReplayVerification:
        """对比重放结果与实际 git 状态——返回一致性报告"""

class ReplayVerification(BaseModel):
    target_time: datetime
    files_in_audit: int
    files_in_git: int
    matched: int
    mismatched: list[ReplayMismatch]
    coverage_pct: float
```
