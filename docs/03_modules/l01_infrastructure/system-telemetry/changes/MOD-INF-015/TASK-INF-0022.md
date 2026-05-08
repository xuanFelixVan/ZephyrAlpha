---
task_id: "TASK-INF-0022"
source_blueprint: "MOD-INF-015"
source_section: "蓝图 §11 alerts 子系统——Burn Rate 告警 + 通知通道 + Postmortem + 合成监控 + 告警测试"

title: "实现 alerts 子系统：Multi-Window Burn Rate 告警引擎 + 通知通道 + SLO Postmortem + 合成监控 + 告警测试"
description: |
  1. Multi-Window Burn Rate 告警引擎：短窗(1h)>14.4x→P0 / 长窗(6h)>6x→P1 / 天窗(3d)>1x→P2
     Alert Pipeline：去重(5min同SLI) + 聚合(同模块→Incident) + 静默(维护窗口) + 路由(P0→Feishu@owner/P1→Feishu/P2→Dashboard)
  2. Error Budget 告警矩阵：LLM可用性99.5%/Gate95%/Pipeline90%
  3. 5 通知通道：Feishu Webhook/P0/P1 / Feishu日摘要 / Dashboard / MCP get_alerts() / Agent RBAC过滤
  4. SLO Postmortem：Burn Rate trigger→聚合相关traces+logs+metrics+annotations→Markdown草稿→Audit Trail→Feishu
  5. 合成监控：6 synth事务(taskcard.e2e/llm.health/ce.fetch/gate.ping/db.write_read/mcp.tool_invoke) + synthetic=true label
  6. 告警测试 4 模式：dry-run(历史回放)/inject(人工注入)/shadow(24h不发通知)/backtest(已知事件回放)
  7. Silent Alert 检测：每24h扫描从未触发的规则
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\alerts\\burn_rate.py"
    description: "Multi-Window Burn Rate 评估引擎"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\alerts\\pipeline.py"
    description: "Alert Pipeline——去重/聚合/静默/路由"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\alerts\\notifiers.py"
    description: "5 通知通道——Feishu/Dashboard/MCP/Agent RBAC"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\alerts\\postmortem.py"
    description: "SLO Postmortem——聚合+Markdown草稿+Audit Trail"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\alerts\\synthetic.py"
    description: "合成监控——6 事务 + synthetic label + SLI排除"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\alerts\\testing.py"
    description: "告警测试框架——dry-run/inject/shadow/backtest + Synthetic Injection"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l12_system_telemetry\\alerts\\**\\*.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"

applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\system-telemetry\\blueprint.md"
    reason: "§11——Burn Rate 引擎+Alert Pipeline+Error Budget矩阵+通知通道+Postmortem §11b——合成监控表+告警测试4模式+Silent Alert检测"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 15000
timeout_minutes: 60

acceptance_criteria:
  - "短窗>14.4x→P0 alert 触发"
  - "同SLI 5min内不重复"
  - "Feishu Webhook P0 卡片消息送达"
  - "SLO breach→Postmortem 草稿写入 Audit Trail"
  - "6 synth 事务全部可执行"
  - "synthetic=true label→排除 SLO 计算"
  - "alerter inject→端到端验证通过"
  - "Silent Alert>30天→P2提醒"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\alerts\burn_rate.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\alerts\pipeline.py
  3. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\alerts\notifiers.py
  4. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\alerts\postmortem.py
  5. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\alerts\synthetic.py
  6. 删除 D:\ZephyrAlpha\src\zephyr\l12_system_telemetry\alerts\testing.py

depends_on:
  - "TASK-INF-0001"
  - "TASK-INF-0012"
blocked_by: []
status: "created"

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

# TASK-INF-0022: alerts 子系统全套实现

## 目标
实现 Google SRE 风格 Multi-Window Burn Rate 告警引擎 + 5 通道通知 + Postmortem + 合成监控 + 告警测试。

## 执行步骤

### 读
- 蓝图 §11 + §11b：完整设计（Burn Rate/Error Budget/Postmortem/Synthetic/Alert Testing/Silent)

### 做
1. burn_rate.py：Multi-Window 评估
2. pipeline.py：Alert Pipeline 4 步
3. notifiers.py：5 通道
4. postmortem.py：聚合+草稿
5. synthetic.py：6 事务
6. testing.py：4 模式

### 检
```python
from zephyr.l12_system_telemetry.alerts.synthetic import SyntheticMonitor
```

## 验收标准
| # | 指标 | 目标 |
|---|------|------|
| 1 | burn_rate | multi-window |
| 2 | dedup | 5min |
| 3 | feishu | P0 card delivered |
| 4 | synth | 6 transactions |
| 5 | test | 4 modes available |
