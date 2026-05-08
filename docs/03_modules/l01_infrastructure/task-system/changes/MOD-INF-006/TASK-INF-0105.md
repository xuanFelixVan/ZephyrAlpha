---
task_id: "TASK-INF-0105"
source_blueprint: "MOD-INF-006"
source_section: "蓝图 §11.3 步骤6 — 补齐 context_engine + M1-M11 确认"

title: "补齐 context_engine + 跑通 M1-M11 全链路测试"
description: |
  补齐 `D:\ZephyrAlpha\src\zephyr\core\context_engine.py` 中的上下文封装逻辑。
  上下文补丁格式规范——每块 [source]/[trigger]/[content]。
  上下文窗口限制 32k token——context_engine.build_context() 参数化+默认值。
  M1-M11 全链路模块拉通测试——端到端：Blueprint→Decomposer→MCP→task_repo→.md。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\models.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\blueprint_decomposer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\mcp\\task_manager_server.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\task_repo.py"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\pipeline\\pipeline-module-registry.yaml"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\core\\context_engine.py"
    description: "ContextEngine 类——上下文封装 + Token 限制"
  - path: "D:\\ZephyrAlpha\\tests\\integration\\test_pipeline_e2e.py"
    description: "M1-M11 全链路端到端集成测试"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\core\\context_engine.py"
  - "D:\\ZephyrAlpha\\tests\\integration\\test_pipeline_e2e.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\db\\**\\*.py"
  - "D:\\ZephyrAlpha\\docs\\**\\*.md"

applicable_rules:
  - module_id: "MOD-INF-006"
    section: "§3.1.3"
    reason: "PipelineOrchestrator API——上下文引擎是管线基础设施"
  - module_id: "PS-STD-006"
    section: "PDL-014"
    reason: "上下文窗口限制——32k token 上限"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"
    reason: "§3.1.3 PipelineOrchestrator + 上下文补丁格式定义"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
  - "M4"
  - "M5"
estimated_tokens: 15000
timeout_minutes: 45

acceptance_criteria:
  - "ContextEngine.build_context(task, files) 返回结构化上下文字典"
  - "上下文补丁格式：[source]/[trigger]/[content]"
  - "token 计数 ≤ context_window_limit（默认32768）"
  - "M1-M11 端到端测试通过——Blueprint→TaskCard→SQLite→.md 成功"

rollback_instructions: |
  1. 删除 `context_engine.py` 文件中新增的上下文补丁逻辑
  2. 删除新增的端到端集成测试文件
  3. 确认 M1-M11 回退到 v0.2.0 状态

depends_on: ["TASK-INF-0102", "TASK-INF-0103", "TASK-INF-0104"]
blocked_by: []

status: "done"

tags_fn:
  - "infra"
  - "pipeline"
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

# 补齐 context_engine + M1-M11 全链路

## 目标

1. 实现上下文引擎——将任务卡的上游文件内容按规范格式组装成 AI 可消费的上下文补丁
2. 全链路 M1-M11 拉通——验证所有管线模块在端到端场景下正确协同

## 触发条件

- TASK-INF-0102/0103/0104 全部完成
- task_repo 可用——create/get/transition 正常

## 执行步骤

### 读
- core/models.py TaskCard 模型——了解 context_window_limit 等字段
- task_repo.py ——数据层接口
- GOV-AI-002 决策树

### 做
1. 实现 ContextEngine 类：
   - `build_context(task, files)` → 返回 {upstream_content, rules, manifest}
   - 每个文件打包为 [source]/[trigger]/[content] 格式
   - token 计数 ≤ context_window_limit
2. 实现 M1-M11 全链路端到端测试：
   - M1: 蓝图读入
   - M2: 建立上下文
   - M3: 解析与拆解
   - M4: SQLite 入库
   - M5: 上下文封装
   - M6: 门禁对标
   - M7: 自动化审阅
   - M8: 报告与路由
   - M9: Gate Engine
   - M10: Thinking Engine
   - M11: Contract Engine
   - M12: Keystone Engine

### 产
- `context_engine.py`
- `test_pipeline_e2e.py`

### 检
```bash
pytest tests/integration/test_pipeline_e2e.py -v
```

## 验收标准

| # | 指标 | 目标 |
|---|------|------|
| 1 | build | context_engine import 无错误 |
| 2 | test | M1-M11 e2e 测试全部通过 |
| 3 | lint | 0 errors |

## 风险与缓解

| 风险 | 缓解 |
|------|------|
| 上下文超过 token 限制 | 实现摘要(TL;DR)机制——超出时截断并附加摘要 |
| M1-M11 测试环境依赖未就绪 | 测试前执行 pipeline-module-registry.yaml 健康检查 |
