---


task_id: TASK-MOD-INF-001-0004
module_id: MOD-INF-001
title: "ContractBus 三批迁移：DD-9 实现"
doc_type: task_card
status: done
priority: P0
layer: L01
layer_name: infrastructure
functional_domain: observability
owner: ZephyrAlpha-Owner
assignee: AI-GLM-5.1
created_by: AI-GLM-5.1
created_at: 2026-05-07T02:57:30+08:00
valid_from: 2026-05-07
ttl: permanent
belongs_to: MOD-INF-001
dependencies:
  - TASK-MOD-INF-001-0001
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\capacity-assurance\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\document\\directory-structure-standard.md"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\contracts\\capacity_assurance\\__init__.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\contracts\\capacity_assurance\\contract_bus.py"
acceptance_criteria:
  - "ContractBus 44 条契约分三批完成迁移：Batch1 15条、Batch2 15条、Batch3 14条"
  - "每批迁移后 YAML Schema 校验通过，无回归"
  - "contract_bus.py 加载全部 44 条契约的 Pydantic Schema"
rollback_instructions:
  - "git checkout -- src/zephyr/contracts/capacity_assurance/"
  - "每批迁移失败时可逐批回滚到上一批稳定版本"
context_assembly_manifest:
  - source: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\capacity-assurance\\blueprint.md"
    sections: ["§5.3 ContractBus 分三批迁移", "DD-9"]
    purpose: "提取 44 条契约的分批方案和每条契约的细节"
  - source: "D:\\ZephyrAlpha\\src\\zephyr\\contracts\\contract_bus.py"
tags:
  - capacity-assurance
  - contractbus
  - migration
  - DD-9
phase: phase_1_scaffold
estimated_effort_minutes: 120
ai_autonomy: AI-Modifiable
governance_layer: GOV-P1
runtime_plane: RP-3
source_blueprint: "MOD-INF-001"
source_section: "蓝图 §4 ContractBus 3批次44合约"
description: "ContractBus 三批迁移：DD-9 实现"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\contracts\\capacity_assurance\\__init__.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\contracts\\capacity_assurance\\contract_bus.py"
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
  - TASK-MOD-INF-001-0001
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



# ContractBus 三批迁移：DD-9 实现

## 1. 任务来源

从蓝图 §5.3 DD-9 提取 ContractBus 三批迁移方案。

**三批划分（共 44 条契约）：**

| 批次 | 契约数 | 重点 | 风险等级 |
|------|--------|------|---------|
| Batch 1 | 15 条 | 基础设施层：SLO 定义、Error Budget、Token Budget、Kill Switch | 中 |
| Batch 2 | 15 条 | 治理层：AI 审计守卫、Provenance、Sandbox、Graceful Degradation | 中 |
| Batch 3 | 14 条 | 集成层：跨模块 OTel/W3C、CT-1~4、语义缓存、健康评分 | 中 |

## 2. 施工内容

### 2.1 Batch 1 — 基础设施层（15 条）

创建 `D:\ZephyrAlpha\src\zephyr\contracts\capacity_assurance\batch1_infra.py`：
- CT-SLO-001: capacity_slo.yaml Schema 定义
- CT-SLO-002: SLO measurement window 定义
- CT-EB-001: Error Budget 计算公式
- CT-EB-002: Burn Rate 阈值契约
- CT-EB-003: 五级响应动作契约
- CT-TB-001: Token Budget 四级定义
- CT-TB-002: Pre-flight 预估接口
- CT-KS-001: Kill Switch 信号格式
- CT-KS-002: 熔断状态切换契约
- CT-SB-001: Sandbox 子进程隔离规范
- CT-GD-001: 降级链 YAML Schema
- CT-GD-002: 模型路由接口
- CT-GD-003: 输出截断策略
- CT-SC-001: 语义缓存键格式
- CT-SC-002: ChromaDB 向量存储契约

### 2.2 Batch 2 — 治理层（15 条）

创建 `D:\ZephyrAlpha\src\zephyr\contracts\capacity_assurance\batch2_governance.py`：
- CT-PR-001: ai_provenance 表写入契约
- CT-PR-002: hash 链校验算法契约
- CT-PR-003: Provenance 查询接口
- CT-AG-001: AI 审计守卫规则引擎输入/输出
- CT-AG-002: 审计结果格式
- CT-VL-001: TechStackValidator 校验结果格式
- CT-VL-002: mypy 配置契约
- CT-VL-003: ruff 规则集契约
- CT-VL-004: bandit 规则集契约
- CT-GV-001: 治理闭环 EMA 参数
- CT-GV-002: 阈值/持续时间契约
- CT-SB-002: Sandbox 资源限制规范
- CT-SB-003: Sandbox 超时策略
- CT-MB-001: MetricsWriteBuffer 批量写入规格
- CT-CH-001: capacity_metrics_hourly 聚合策略

### 2.3 Batch 3 — 集成层（14 条）

创建 `D:\ZephyrAlpha\src\zephyr\contracts\capacity_assurance\batch3_integration.py`：
- CT-OT-001: OTel Span 格式（含 gen_ai.* 属性）
- CT-OT-002: W3C TraceContext 传播接口
- CT-HS-001: ZephyrHealthScore 输出格式
- CT-CT1: 与 predict-router 的容量告警联动接口
- CT-CT2: 与 market-data-ingestor 的熔断传播接口
- CT-CT3: 与 task-system 的 Token 扣减接口
- CT-CT4: 与 iguana-rebalancer 的账户熔断接口
- CT-GD-004: 双向模型切换逻辑
- CT-CR-001: change_rate_limiter 渐进式切换
- CT-AI-001: AI 行为预测维度 SLI 插桩
- CT-FB-001: 预警→修复闭环 Playbook 格式
- CT-DR-001: DR 备份与恢复契约
- CT-CP-001: 容量预测模型输入/输出
- CT-SM-001: Sandbox 策略生命周期管理

## 3. 验收标准

1. 44 条契约全部以 Pydantic v2 BaseModel 定义
2. 每批迁移后 `pytest tests/contracts/capacity_assurance/` 全绿
3. ContractBus 加载全部 44 条契约无报错
4. 每批验收通过后方可启动下一批