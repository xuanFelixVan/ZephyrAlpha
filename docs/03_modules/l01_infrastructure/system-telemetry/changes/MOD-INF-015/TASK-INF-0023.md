---
task_id: "TASK-INF-0023"
source_blueprint: "MOD-INF-015"
source_section: "蓝图 §12 schema 子系统——Schema Registry + 漂移检测 + SLO Coverage + CI/CD + SLI Registry + Schema Versioning"

title: "实现 schema 子系统：MetricSchema Registry + 蓝图漂移检测 + SLI Registry + Schema 版本化"
description: |
  1. MetricSchema Registry：MetricSchema + LabelDef Pydantic 模型 / YAML SSoT→代码生成 / 运行时校验 report()前 / rejection→DLQ
  2. 蓝图漂移检测：蓝图§16声称文件 vs 磁盘实际→drift_report(missing/extra/status_mismatch)→AI session冷启动提示
  3. SLO 采集覆盖检测：蓝图§4 SLI vs Schema Registry注册 vs metrics表24h活跃→orphan_slos/orphan_metrics→P2
  4. 告警规则漂移检测：蓝图§11 vs alert_rules.yaml→delta report
  5. CI/CD Pipeline 可观测性：构建/测试/部署健康 + AI专属(ai_generated_code_ratio/code_review_bypass_rate) + Annotations注入 + Post-Deployment Validation
  6. SLI 定义注册表（SliDefinition）：slis.yaml YAML SSoT + 自动生成告警规则 + 与 alert_rules.yaml 同步检测
  7. Schema 版本化（v{major}.{minor}）：兼容性矩阵（7 种变更类型+行为）+ alias 策略（2版本后废弃旧名）+ 蓝图版本漂移检测
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"

downstream_outputs:
  - path: "D:\ZephyrAlpha\src\zephyr\governance\agent_spec\registry.py"
    description: "Schema Registry——MetricSchema+LabelDef 模型 + YAML SSoT 加载 + 运行时校验"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\schema\\drift.py"
    description: "蓝图漂移检测——文件/SLO/告警规则 三层 drift check"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\schema\\cicd_observability.py"
    description: "CI/CD 可观测性——构建/测试/部署遥测 + Annotations + Post-Deploy Validation"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\schema\\sli_registry.py"
    description: "SLI 定义注册表——SliDefinition 模型 + YAML 加载 + 自动生成告警规则"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\schema\\versioning.py"
    description: "Schema 版本化——兼容性矩阵 + alias 引擎 + 蓝图版本 drift"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\schema\\**\\*.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"
    reason: "§12——Schema Registry + drift检测(3层) + SLO coverage + §12b——CI/CD 可观测性表+部署验证 + §12c——SLI Registry Schema+示例 + §12d——Schema 版本化(兼容性矩阵+alias)"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 15000
timeout_minutes: 60

acceptance_criteria:
  - "MetricSchema 数据类可用——name/type/unit/description/module_id/labels/slo_target/cardinality_limit/deprecated/replaced_by"
  - "运行时 report() 前 schema 校验——拒绝未注册指标→rejection log + DLQ"
  - "drift check→发现 missing_file→生成 drift_report"
  - "SLO drift：蓝图§4 所有 SLI→Schema Registry 注册+24h活跃数据"
  - "CI/CD Annotation 注入：build_start→end / deploy_start→end / rollback"
  - "Post-Deploy Validation：deploy后自动→合成监控+metrics对比→任一回归→FLE rollback"
  - "sli_registry.yaml→自动生成 alert_rules.yaml 条目"
  - "schema v{X+1}.0→兼容性检查不通过→MUST upgrade major version"
  - "alias 查询 llm_api_calls→自动 redirect→llm_calls_total"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\schema\registry.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\schema\drift.py
  3. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\schema\cicd_observability.py
  4. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\schema\sli_registry.py
  5. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\schema\versioning.py

depends_on:
  - "TASK-INF-0001"
  - "TASK-INF-0012"
blocked_by: []
status: "done"

tags_fn:
  - "observability"
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

# TASK-INF-0023: schema 子系统全套实现

## 目标
实现 Schema Registry + 三层漂移检测 + CI/CD 可观测性 + SLI Registry + Schema 版本化兼容。

## 执行步骤

### 读
- 蓝图 §12/§12b/§12c/§12d：完整 schema 子系统设计

### 做
1. registry.py：MetricSchema 模型 + YAML 加载 + runtime 校验
2. drift.py：三层 drift（文件/SLO/告警规则）
3. cicd_observability.py：CI/CD 遥测 + Post-Deploy Validation
4. sli_registry.py：SLI YAML SSoT + 自动生成
5. versioning.py：兼容性矩阵 + alias

### 检
```python
from zephyr.l12_system_telemetry.schema.registry import SchemaRegistry
```

## 验收标准
| # | 指标 | 目标 |
|---|------|------|
| 1 | schema | MetricSchema model |
| 2 | validate | rejection→DLQ |
| 3 | drift | 3-level check |
| 4 | cicd | 构建/测试/部署 telemetry |
| 5 | version | alias + compat matrix |
