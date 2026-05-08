---
task_id: "TASK-MST-0010"
source_blueprint: "MOD-MASTER-001"
source_section: "蓝图 §十 集成测试契约——13条CT-*专属断言 + 4级CI门禁触发条件"

title: "实现集成测试契约框架——CT-* 专属断言 + CI门禁 GATE-IT-* 系列"
description: |
  实现 §十 定义的集成测试契约：为 13 条核心 CT-* 契约编写专属集成测试断言，
  并实现 4 级 CI 门禁(GATE-IT-SMOKE/GATE-IT-CORE/GATE-IT-CONTRACT/GATE-IT-HEALTH)。
  集成测试框架：(1)每条 CT-* 契约的 contract_test——验证契约输入输出 Schema 一致性；
  (2)Mock 消费者的期望声明——拉取 consumer expectation JSON 并验证 provider 满足；
  (3)GATE-IT-SMOKE: 最关键 3 条契约的冒烟测试（pre-commit触发）；
  (4)GATE-IT-CORE: 13 条核心契约全量测试（push to main 触发）；
  (5)GATE-IT-CONTRACT: CDC verification + Can-I-Deploy（deploy前触发）；
  (6)GATE-IT-HEALTH: 12 系统三态探针全量扫描（每日定时+deploy前触发）。

priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\contract_registry.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\gates\\integration_test_runner.py"
    description: "集成测试运行器——加载契约定义+运行断言+CI门禁集成"
  - path: "D:\\ZephyrAlpha\\tests\\contracts\\test_ct_orc_script_001.py"
    description: "CT-ORC-SCRIPT-001 集成测试——Task Blocking→Task创建"
  - path: "D:\\ZephyrAlpha\\tests\\contracts\\test_ct_orc_ce_001.py"
    description: "CT-ORC-CE-001 集成测试——Session Context请求"
  - path: "D:\\ZephyrAlpha\\tests\\contracts\\test_ct_script_kb_001.py"
    description: "CT-SCRIPT-KB-001 集成测试——Finding→KE入库"
  - path: "D:\\ZephyrAlpha\\tests\\contracts\\test_ct_fle_orc_001.py"
    description: "CT-FLE-ORC-001 集成测试——异常检测→调度调整"
  - path: "D:\\ZephyrAlpha\\tests\\contracts\\test_ct_ce_vms_001.py"
    description: "CT-CE-VMS-001 集成测试——Context→Vector Search"
  - path: "D:\\ZephyrAlpha\\tests\\contracts\\test_ct_pipe_orc_001.py"
    description: "CT-PIPE-ORC-001 集成测试——Task→Pipeline路由"
  - path: "D:\\ZephyrAlpha\\tests\\contracts\\test_ct_script_gate_001.py"
    description: "CT-SCRIPT-GATE-001 集成测试——Script Exit Code→Gate决策"
  - path: "D:\\ZephyrAlpha\\tests\\contracts\\test_ct_orc_vms_001.py"
    description: "CT-ORC-VMS-001 集成测试——Task Output→Vector Memory"
  - path: "D:\\ZephyrAlpha\\tests\\contracts\\test_ct_orc_gate_001.py"
    description: "CT-ORC-GATE-001 集成测试——Task Lifecycle Gate"
  - path: "D:\\ZephyrAlpha\\tests\\contracts\\test_ct_ce_lsg_001.py"
    description: "CT-CE-LSG-001 集成测试——Context Injection Safety"
  - path: "D:\\ZephyrAlpha\\tests\\contracts\\test_ct_kb_vms_001.py"
    description: "CT-KB-VMS-001 集成测试——KB→Vector"
  - path: "D:\\ZephyrAlpha\\tests\\contracts\\test_ct_fle_db_001.py"
    description: "CT-FLE-DB-001 集成测试——FLE Metrics→DB"
  - path: "D:\\ZephyrAlpha\\tests\\contracts\\test_ct_tele_fle_001.py"
    description: "CT-TELE-FLE-001 集成测试——Telemetry→FLE"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\gates\\integration_test_runner.py"
  - "D:\\ZephyrAlpha\\tests\\contracts\\**"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\contract_registry.py"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号格式"
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径架构合规创建"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
    reason: "§十——13条CT-*专属断言 + 4级CI门禁触发条件定义"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\contract_registry.py"
    reason: "契约注册表——集成测试需要加载契约定义来生成断言"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 30000
timeout_minutes: 120

acceptance_criteria:
  - "integration_test_runner.py 支持加载任意 CT-* 契约定义并自动生成测试断言"
  - "13 条核心 CT-* 契约每条至少 1 个集成测试文件（test_ct_*.py）"
  - "GATE-IT-SMOKE: 3条最关键契约的冒烟测试——pre-commit时运行"
  - "GATE-IT-CORE: 13条全量——push to main 触发"
  - "GATE-IT-CONTRACT: CDC verification——deploy前触发"
  - "GATE-IT-HEALTH: 12系统三态探针全量扫描"
  - "所有集成测试通过 Pydantic V2 Schema 验证"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\gates\integration_test_runner.py
  2. 删除 D:\ZephyrAlpha\tests\contracts\test_ct_*.py 全部新增文件
  3. 确认 contracts/ 目录下无残留文件

depends_on: ["TASK-MST-0004"]
blocked_by: []

status: "done"

tags_fn:
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-MASTER-001"

completed_gates: []
blocked_gates: {}

artifact_paths: []
audit_findings: []
ke_entries: []

ai_autonomy_level: "supervised"
autonomy_checklist: []
---
