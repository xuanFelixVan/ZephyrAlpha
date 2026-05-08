---


task_id: TASK-MOD-INF-001-0002
module_id: MOD-INF-001
title: "架构决策实现：技术栈 DD-1 至 DD-16"
doc_type: task_card
status: done
priority: P0
layer: L01
layer_name: infrastructure
functional_domain: observability
owner: ZephyrAlpha-Owner
assignee: AI-GLM-5.1
created_by: AI-GLM-5.1
created_at: 2026-05-07T02:56:00+08:00
valid_from: 2026-05-07
ttl: permanent
belongs_to: MOD-INF-001
dependencies:
  - TASK-MOD-INF-001-0001
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\capacity-assurance\\blueprint.md"
  - "D:\\ZephyrAlpha\\config\\capacity\\capacity_slo.yaml"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\capacity_assurance\\tech_stack.py"
  - "D:\\ZephyrAlpha\\config\\capacity\\tech_stack_manifest.yaml"
acceptance_criteria:
  - "技术栈清单 YAML 文件包含全部 16 项 DD 决策的终选、理由、v2.0.0 变更标记"
  - "tech_stack.py 提供 TechStackValidator 类，启动时校验所有组件可用性"
  - "每个 DD 决策的终选技术与蓝图 §5.1 表格完全一致"
rollback_instructions:
  - "删除 src/zephyr/capacity_assurance/tech_stack.py"
  - "删除 config/capacity/tech_stack_manifest.yaml"
context_assembly_manifest:
  - source: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\capacity-assurance\\blueprint.md"
    sections: ["§5.1 终选技术栈"]
    purpose: "提取全部 16 项 DD 架构决策"
tags:
  - capacity-assurance
  - architecture-decisions
  - tech-stack
phase: phase_1_scaffold
estimated_effort_minutes: 30
ai_autonomy: AI-Modifiable
governance_layer: GOV-P1
runtime_plane: RP-3
source_blueprint: "MOD-INF-001"
source_section: "蓝图 §2 设计决策 DD-1~DD-16"
description: "架构决策实现：技术栈 DD-1 至 DD-16"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\capacity_assurance\\tech_stack.py"
  - "D:\\ZephyrAlpha\\config\\capacity\\tech_stack_manifest.yaml"
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
estimated_tokens: 9000
timeout_minutes: 30
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



# 架构决策实现：技术栈 DD-1 至 DD-16

## 1. 任务来源

从蓝图 §5.1 终选技术栈提取全部 16 项架构决策。

| # | DD 编号 | 组件 | 终选 | 理由 |
|---|---------|------|------|------|
| 1 | DD-1 | SLO 配置 | YAML + Pydantic v2 | 零依赖运行时校验，Schema 即文档 |
| 2 | DD-2 | 审计 Provenance 存储 | SQLite + hash 链 | 只追加 + 完整性校验，零运维 |
| 3 | DD-3 | 容量指标采样 | structlog + OpenTelemetry SDK | 业界标准 |
| 4 | DD-4 | AI 审计守卫规则 | YAML 规则集 + Pydantic 校验 | 规则可演化 |
| 5 | DD-5 | 治理闭环 | 自研 EMA + 阈值 + 持续时间 | 零依赖 |
| 6 | DD-6 | 类型校验 | mypy + import-linter | 本地 + CI 双保险 |
| 7 | DD-7 | 单元测试 | pytest + pytest-cov | 行业标准 |
| 8 | DD-8 | 静态扫描 | ruff + bandit | 取代 pylint |
| 9 | DD-9 | ContractBus 迁移 | 分三批 15+15+14 | 控制回归风险 |
| 10 | DD-10 | Error Budget 追踪 | SQLite + Pydantic v2 | 复用已有基础设施 |
| 11 | DD-11 | Token Budget | Token Bucket + 滑动窗口 | 社区标准算法 |
| 12 | DD-12 | Kill Switch | 环境变量 + 文件信号 | 零依赖，双通道 |
| 13 | DD-13 | Sandbox | 子进程 + 资源限制 | Python stdlib |
| 14 | DD-14 | Graceful Degradation | YAML 降级链 + 模型路由 | 声明式配置 |
| 15 | DD-15 | OTel 语义规范 | OpenTelemetry GenAI Semantic Conventions | 2025 行业标准 |
| 16 | DD-16 | 语义缓存 | ChromaDB 向量相似度 | 复用已有 VMS 基础设施 |

## 2. 施工内容

### 2.1 创建 `tech_stack_manifest.yaml`

在 `D:\ZephyrAlpha\config\capacity\tech_stack_manifest.yaml` 中，创建结构化清单，每条包含：
- `dd_id`: DD-1 至 DD-16
- `component`: 组件名称
- `final_choice`: 终选技术
- `rationale`: 选择理由
- `version_change`: v2.0.0 变更标记（是/否）
- `governance_layer`: 治理层级

### 2.2 创建 `tech_stack.py`

在 `D:\ZephyrAlpha\src\\zephyr\\shared\\tech_stack.py` 中实现 `TechStackValidator`：
- `validate()`: 启动时逐一校验 16 项组件的可用性
- `check_pydantic_v2()`: 确认 Pydantic v2 可用
- `check_sqlite()`: 确认 SQLite 可用
- `check_otel_sdk()`: 确认 OpenTelemetry SDK 可用
- `check_pytest()`: 确认 pytest 可用
- `check_chromadb()`: 确认 ChromaDB 可用
- `check_psutil()`: 确认 psutil 可用
- `report()`: 输出组件可用性报告

## 3. 验收标准

1. `tech_stack_manifest.yaml` 包含全部 16 项决策
2. `tech_stack.py` 中 `TechStackValidator.validate()` 在测试环境通过
3. 每个 DD 的终选技术与蓝图 §5.1 表格完全一致
4. Pydantic v2 Schema 校验 tech_stack_manifest.yaml 通过