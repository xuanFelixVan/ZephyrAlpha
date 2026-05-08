---
task_id: "TASK-INF-0214"
source_blueprint: "MOD-INF-020"
source_section: "蓝图 §3.2 文件组成——cli.py + §7 Phase scaffold 验收标准"

title: "实现 CLI 审计面板——zephyr audit query/trail/integrity/health/evidence"
description: |
  实现 `src/zephyr/audit_trail/cli.py` 中的 CLI 审计命令行面板。
  命令组 `zephyr audit`：
  - `query --task-id <id>` / `--agent <id>` / `--file <path>` / `--anomaly <type>` → 表格输出
  - `trail --session-id <id>` → 输出 AI 可消费的 Markdown 上下文摘要
  - `integrity [--fast|--full]` → 运行完整性校验，输出 IntegrityReport
  - `health` → 输出自监控健康指标摘要（10 项指标状态）
  - `evidence --task-id <id>` → 触发证据包导出（Phase beta 接入）
  - LOT 输出格式：彩色终端表格 + JSON 选项 `--output json`
  对标蓝图 §7 scaffold 验收标准 #4。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\cli.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\query.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\integrity.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\self_monitor.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\cli.py"
    description: "完整实现 CLI——5 命令组 + argparse + 彩色输出 + JSON 选项"
  - path: "D:\\ZephyrAlpha\\tests\\audit_trail\\test_cli.py"
    description: "CLI 集成测试——各命令端到端 + 输出格式验证"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\cli.py"
  - "D:\\ZephyrAlpha\\tests\\audit_trail\\test_cli.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"

applicable_rules:
  - module_id: "GOV-DOC-002"
    section: "§5.1.2"
    reason: "CLI 文件路径合规"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
    reason: "§3.2——cli.py 职责 + §7 scaffold 验收标准 #4"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 8000
timeout_minutes: 50

acceptance_criteria:
  - "zephyr audit query --task-id T-001 → 表格输出任务摘要"
  - "zephyr audit trail --session-id S-001 → Markdown 输出（含语义沙箱包裹）"
  - "zephyr audit integrity --fast → < 1s 返回结果"
  - "zephyr audit health → 展示 10 项指标状态（绿色PASS/红色FAIL）"
  - "--output json → 机器可读 JSON 输出"
  - "5/5 CLI 命令集成测试通过"

rollback_instructions: |
  1. 删除 cli.py 内容
  2. 删除 test_cli.py
  3. 移除 setup.py/pyproject.toml 中的 console_scripts 入口

depends_on:
  - "TASK-INF-0211"
  - "TASK-INF-0210"
  - "TASK-INF-0213"
blocked_by: []

status: "done"

tags_fn:
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-020"

completed_gates: []
blocked_gates: {}

artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
