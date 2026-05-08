---
task_id: "TASK-INF-0007"
source_blueprint: "MOD-INF-015"
source_section: "蓝图 §2h Observability-as-Code 声明"

title: "实现 Observability-as-Code：config/ YAML SSoT 版本化 + CI/CD 集成约束"
description: |
  实现 Grafana 12 风格的 Observability-as-Code——所有可观测性配置与业务代码同仓 git 管理：
  1. 创建 4 个 config/ YAML SSoT 文件：metrics_schema.yaml / sli_registry.yaml / alert_rules.yaml / flags.yaml
  2. 创建 config/dashboards/ 目录 + Dashboard YAML
  3. CI/CD Pipeline 集成：yamllint → schema validate → diff → alert backtest → deploy → synth verify
  4. AI 施工约定：所有配置 MUST 在 config/ 目录，禁止 Grafana UI 手动编辑
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\config\\metrics_schema.yaml"
    description: "指标 Schema SSoT——所有 MetricSchema 定义"
  - path: "D:\\ZephyrAlpha\\config\\sli_registry.yaml"
    description: "SLI 定义注册表——Google SRE 格式 SLI 定义"
  - path: "D:\\ZephyrAlpha\\config\\alert_rules.yaml"
    description: "告警规则 SSoT——Multi-Window Burn Rate 规则"
  - path: "D:\\ZephyrAlpha\\config\\flags.yaml"
    description: "FeatureFlag 定义——含 telemetry.* 8 flags"
  - path: "D:\\ZephyrAlpha\\config\\dashboards\\"
    description: "Dashboard-as-Code——Grafana-compatible Dashboard YAML"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\config_loader.py"
    description: "配置加载器——从 config/ YAML 热加载 + CI/CD lint 验证"

allowed_touch:
  - "D:\\ZephyrAlpha\\config\\metrics_schema.yaml"
  - "D:\\ZephyrAlpha\\config\\sli_registry.yaml"
  - "D:\\ZephyrAlpha\\config\\alert_rules.yaml"
  - "D:\\ZephyrAlpha\\config\\flags.yaml"
  - "D:\\ZephyrAlpha\\config\\dashboards\\**"
  - "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\config_loader.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2——config schema validation"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径合规创建"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"
    reason: "§2h——版本化清单（5 类产出物）+ CI/CD 集成约束（6 步骤）+ AI 施工约定（4 条）"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 7000
timeout_minutes: 30

acceptance_criteria:
  - "4 个 config/ YAML SSoT 文件已创建（含最小有效内容）"
  - "config/dashboards/ 目录存在"
  - "config_loader.py 可从 YAML SSoT 加载配置"
  - "CI/CD lint 步骤 yamllint config/*.yaml 可执行"
  - "禁止 Grafana UI 手动编辑的运行时检查已实现"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\config\metrics_schema.yaml（如仅含模板内容）
  2. 删除 D:\ZephyrAlpha\config\sli_registry.yaml
  3. 删除 D:\ZephyrAlpha\config\alert_rules.yaml
  4. 从 D:\ZephyrAlpha\config\flags.yaml 移除 telemetry.* 段
  5. 删除 D:\ZephyrAlpha\config\dashboards\ 目录
  6. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\config_loader.py

depends_on:
  - "TASK-INF-0001"
blocked_by: []
status: "created"

tags_fn:
  - "observability"
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-015"

completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---

# TASK-INF-0007: 实现 Observability-as-Code

## 目标
将所有可观测性配置（dashboards/alerts/SLIs/schemas）与业务代码同仓 git 管理，通过 CI/CD 部署，实现 Grafana 12 Git Sync 范式。

## 触发条件
- TASK-INF-0001 通过

## 执行步骤

### 读
- 蓝图 §2h：版本化清单（5 产出物）、CI/CD Pipeline 步骤（6 步）、AI 施工约定（4 条）

### 做
1. 创建 4 个 config/ YAML SSoT 文件骨架
2. 创建 config/dashboards/ 目录
3. 实现 config_loader.py：YAML 加载 + schema 验证 + CI/CD lint

### 产
- 4 个 YAML SSoT + dashboards/ + config_loader.py

### 检
```bash
yamllint config/metrics_schema.yaml config/sli_registry.yaml config/alert_rules.yaml config/flags.yaml
```

## 验收标准
| # | 指标 | 目标 |
|---|------|------|
| 1 | files | 4 YAML SSoT + dashboards/ 目录就绪 |
| 2 | lint | yamllint 0 errors |
| 3 | build | config_loader.py 可加载全部 4 个 YAML |
