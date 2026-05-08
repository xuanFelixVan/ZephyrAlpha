---
task_id: "TASK-INF-0130"
source_blueprint: "MOD-INF-006"
source_section: "蓝图 §13 盲点审计与路线图（48盲点 + 8大类 + 路线图 + 已解决 + 对标基准）"

title: "维护盲点审计与路线图——48盲点关闭审计 + 路线图更新 + 已解决确认"
description: |
  维护蓝图 §13 盲点审计与路线图完整部分。
  48 盲点全部 8 大类有登记——A(执行质量)/B(架构完整性)/C(1人+AI)/D(可观测性)/
  E(质量管理)/F(补偿事务)/G(运行时演化)/H(数据持久化-跨类别新增)。
  v0.6.0 归类（A-9项/B-7项/C-5项/D-5项/E-4项/F-3项/G-8项/H-4项）总计48。
  优先级路线图更新——v0.4.0/v0.5.0/v0.6.0/vNext 规划正确。
  v0.4.0 已解决 14 项确认结果准确。
  对标基准——41→48盲点（新增H+7个扩充分类）的审计一致性。
  蓝图编写铁律 (10条) 一致性验证——本蓝图违反情况确认。
  安全删除协议状态确认。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\models.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\lifecycle\\task_lifecycle_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\reliability\\**\\*.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\quality\\**\\*.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\adaptation\\**\\*.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\session\\**\\*.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\observability\\**\\*.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\impact\\**\\*.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\migrations.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\maintenance\\**\\*.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
    description: "§13 盲点审计——48盲点关闭状态 + 路线图 + 铁律验证 + 删除协议确认"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\core\\test_blindspot_coverage.py"
    description: "盲点关闭审计——48盲点 vs 代码实现覆盖率检查脚本"

allowed_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\tests\\unit\\core\\test_blindspot_coverage.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

applicable_rules:
  - module_id: "MOD-INF-006"
    section: "§13"
    reason: "48盲点 + 8大类 + 路线图 + 已解决——SSoT"
  - module_id: "PS-STD-001"
    section: "§7.8"
    reason: "ai_autonomy_level 五级枚举——与盲点对标"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
    reason: "§13 完整盲点审计内容——48盲点 + 8大类 + 路线图 + 铁律"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
  - "M7"
estimated_tokens: 20000
timeout_minutes: 90

acceptance_criteria:
  - "§13.2 48盲点分类正确——各类别计数：A9/B7/C5/D5/E4/F3/G8/H4"
  - "关闭状态一致——resolved/open/partial 与实际代码实现一致"
  - "§13.3 优先级路线图——v0.4.0/v0.5.0/v0.6.0/vNext 规划与蓝图版本对齐"
  - "§13.4 v0.4.0 已解决 14 项——每项的代码实现路径存在并可 import"
  - "§13.5 基准——41→48盲点增量追踪正确"
  - "蓝图编写铁律 (10条) ——本蓝图无违反"
  - "安全删除协议——MOD-INF-003/MOD-INF-004 标记 deprecated 状态"
  - "contract_version 可在 tool_contracts.yaml 中读取"

rollback_instructions: |
  1. 恢复 blueprint.md §13 部分
  2. 删除 test_blindspot_coverage.py

depends_on: ["TASK-INF-0102", "TASK-INF-0106", "TASK-INF-0111"]
blocked_by: []

status: "done"

tags_fn:
  - "infra"
  - "audit"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-006"

completed_gates: []
blocked_gates: {}

artifact_paths: []
audit_findings: []
ke_entries: []

ai_autonomy_level: "supervised"
autonomy_checklist: []
---

# 维护盲点审计与路线图——48盲点 + 铁律验证

## 目标

1. 48盲点关闭审计——正确归类
2. 优先级路线图更新
3. v0.4.0 已解决 14 项——代码实现验证
4. 蓝图编写铁律一致性验证
5. 安全删除协议确认

## 触发条件

- TASK-INF-0102/0106/0111 完成

## 执行步骤

### 读
- 蓝图 §13 完整内容

### 做
1. 盲点关闭审计——与实现的代码路径对照
2. 路线图更新——v0.6.0 完成 + vNext 规划
3. v0.4.0 已解决验证——14项对应代码可 import
4. 铁律一致性验证
5. 删除协议确认

### 产
- 更新 §13 + test_blindspot_coverage.py

### 检
```bash
python -m zephyr.tools.check_blindspots --blueprint MOD-INF-006
```

## 验收标准

| # | 指标 | 目标 |
|---|------|------|
| 1 | diff | 仅修改 §13 |
| 2 | coverage | 48盲点→代码100%映射 |
