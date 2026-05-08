---


task_id: TASK-MOD-INF-001-0010
module_id: MOD-INF-001
title: "风险缓解实现：R1 至 R8 全量风险项"
doc_type: task_card
status: done
priority: P0
layer: L01
layer_name: infrastructure
functional_domain: observability
owner: ZephyrAlpha-Owner
assignee: AI-GLM-5.1
created_by: AI-GLM-5.1
created_at: 2026-05-07T03:00:30+08:00
valid_from: 2026-05-07
ttl: permanent
belongs_to: MOD-INF-001
dependencies:
  - TASK-MOD-INF-001-0005
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\capacity-assurance\\blueprint.md"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\capacity_assurance\\risk_mitigation.py"
  - "D:\\ZephyrAlpha\\config\\capacity\\risk_register.yaml"
acceptance_criteria:
  - "risk_register.yaml 包含全部 8 项风险 + 多轮审计新增风险的完整记录"
  - "risk_mitigation.py 中每条风险有对应的 MitigationHandler 实现"
  - "R1 SQLite WAL 模式 + WAL checkpoint + backup checkpoint 已实现"
  - "R2 跨模块死锁检测：超时 + 重试 + 指数退避"
  - "R3 容量瓶颈告警链路依赖 fire-and-forget 保证不阻塞主链路"
  - "R4~R8 + 多轮审计新增风险均有缓解代码"
rollback_instructions:
  - "风险缓解模块独立，删除不影响核心功能"
  - "每条缓解 handler 可独立禁用"
context_assembly_manifest:
  - source: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\capacity-assurance\\blueprint.md"
    sections: ["§14 风险与缓解 L677-689（R1-R8）", "§20 #14~#16 风险扩展", "§22 #26, #38 风险扩展", "§23 #49 风险补充", "§24 #65~#67 风险扩展"]
    purpose: "提取全部风险项及其缓解策略"
tags:
  - capacity-assurance
  - risk-mitigation
  - R1-to-R8
phase: phase_1_scaffold
estimated_effort_minutes: 120
ai_autonomy: AI-Modifiable
governance_layer: GOV-P1
runtime_plane: RP-3
source_blueprint: "MOD-INF-001"
source_section: "蓝图 §14 Risk Registry R1~R16"
description: "风险缓解实现：R1 至 R8 全量风险项"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\capacity_assurance\\risk_mitigation.py"
  - "D:\\ZephyrAlpha\\config\\capacity\\risk_register.yaml"
forbidden_touch:
  - "D:\ZephyrAlpha\docs\01_policies_and_standards\**\*.md"
  - "D:\ZephyrAlpha\src\zephyr\shared\schemas.py"
applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号格式 TASK-{DOMAIN}-{NNNN}"
  - module_id: "PS-STD-011"
  - module_id: "ADR-0040"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 36000
timeout_minutes: 120
depends_on:
  - TASK-MOD-INF-001-0005
blocked_by: []
tags_fn: ["infra"]
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo: ["MOD-INF-001"]
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []


---



# 风险缓解实现：R1 至 R8 全量风险项

## 1. 任务来源

从蓝图 §14 核心风险 R1-R8 + 多轮审计扩展风险提取。

**基线 8 项风险：**

| 风险ID | 内容 | 等级 | 缓解策略 |
|--------|------|------|---------|
| R1 | SQLite 并发写入瓶颈 | 高 | WAL 模式 + WAL checkpoint + backup checkpoint + 写缓冲队列 |
| R2 | 跨模块死锁 | 高 | 超时机制 (30s) + 重试 (3次) + 指数退避 (1s/2s/4s) + 有序锁获取 |
| R3 | 容量瓶颈告警链路阻塞上游 | 高 | fire-and-forget 异步 + thread_pool + 队列上限保护 |
| R4 | Pydantic Schema 版本漂移 | 中 | 版本锁定 + ContractBus 双向校验 + schema_version 字段 |
| R5 | Token 预估严重失准 | 中 | 多模型校准 + 滚动窗口修正 + 实际/预估比率监控 |
| R6 | Kill Switch 误触发 | 中 | 多条件 AND 判定 + 脉冲过滤 (持续 > 30s) + 手动覆盖 |
| R7 | Sandbox 逃逸 | 低 | 资源限制硬边界 + 超时强制 kill + 能力审计 |
| R8 | AI 审计守卫绕过 | 极低 | 只追加表 + hash 链 + 定期完整性校验 |

## 2. 施工内容

### 2.1 创建 risk_register.yaml

创建 `D:\ZephyrAlpha\config\capacity\risk_register.yaml`，结构化记录全部风险，每条含：
- `risk_id`, `severity`, `description`, `mitigation`, `status`, `owner`, `last_review`

### 2.2 R1 缓解：WAL 模式 + 写缓冲

在 `risk_mitigation.py` 中实现：
- `enable_wal_mode(db_path)`: 执行 `PRAGMA journal_mode=WAL`
- `perform_wal_checkpoint(db_path)`: 定期 WAL checkpoint
- `backup_checkpoint(db_path, backup_path)`: 备份前强制执行 checkpoint
- 与 `MetricsWriteBuffer` 集成

### 2.3 R2 缓解：跨模块死锁检测

在 `risk_mitigation.py` 中实现 `DeadlockDetector`：
- `acquire_with_timeout(lock, timeout=30)`: 超时锁获取
- `retry_with_backoff(func, max_retries=3, base_delay=1.0)`: 指数退避重试
- `ordered_lock_acquisition(locks)`: 按模块 ID 排序获取锁

### 2.4 R3 缓解：告警链路隔离

在 `risk_mitigation.py` 中实现 `AlertLinkIsolator`：
- `fire_and_forget(alert_func, *args, **kwargs)`: 异步告警发送
- `ThreadPoolExecutor(max_workers=2)` + `queue.Queue(maxsize=100)`

### 2.5 R4-R8 缓解

在 `risk_mitigation.py` 中实现对应的 MitigationHandler：
- R4: `SchemaVersionGuard`: 双向版本校验
- R5: `TokenCalibration`: 滚动窗口校准
- R6: `KillSwitchSafeguard`: 脉冲过滤 + 多条件非AND
- R7: `SandboxHardener`: 资源硬边界
- R8: `ProvenanceIntegrityChecker`: hash 链定期校验

### 2.6 多轮审计扩展风险

在 `risk_register.yaml` 和 `risk_mitigation.py` 中补充：
- 盲点 #14 → R9: hash 链校验性能退化（大文件 hash 计算随 Provenance 增长而退化）
- 盲点 #15 → R10: Token 预估模型白盒包裹风险（AI 构造特殊 input 格式导致预估失败）
- 盲点 #16 → R11: Kill Switch 双通道竞态（环境变量 + 文件信号并写竞态）
- 盲点 #26 → R12: 累计 Error Budget 消耗不变式破坏（Δ=累计-Σ分窗口，|Δ|>1% 未被检测）
- 盲点 #38 → R13: SLO 配置泄露到应用日志（敏感阈值信息通过 structlog 泄露）
- 盲点 #49 → R14: 多 Batch 迁移中 ContractBus 崩溃恢复失败（部分契约已迁移、部分未迁移的中间态）
- 盲点 #65 → R15: wchar_t 路径匹配失败（Windows Unicode 路径与 ASCII 路径不一致）
- 盲点 #66 → R16: ChromaDB 线程池泄漏（长期运行后线程数持续增长）

## 3. 验收标准

1. `risk_register.yaml` 通过 Pydantic v2 Schema 校验
2. R1 WAL 模式 + checkpoint 可正确执行
3. R2 死锁检测在模拟死锁场景下触发超时
4. R3 告警链路在主链路阻塞时不丢告警
5. 所有 16 项风险条目（R1~R8 基线 + R9~R16 扩展）在 risk_mitigation.py 中有对应 handler