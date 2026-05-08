---
task_id: "TASK-INF-0110"
source_blueprint: "MOD-INF-002"
source_section: "蓝图 §2.1-G 安全深度强化 B4-G01~G06 + §2.1-H 可观测性 B4-H01~H05 + §2.1-I API协议 B4-I01~I04 + §2.1-J 开发者体验 B4-J01~J06"
title: "盲点关闭——G.安全 B4-G01~G06 + H.可观测性 B4-H01~H05 + I.API协议 B4-I01~I04 + J.DevEx B4-J01~J06"
description: |
  关闭四类盲点共 21 项。
  G.安全（B4-G01~G06）：ModuleSandbox 进程隔离（§5.3 代码骨架——独立子进程+5次crash永久隔离）+
  AI-Generated Code Security Scanning（Semgrep 自动扫描）+
  Tamper-Proof Audit Log（Merkle Tree 哈希链防篡改）+
  Least Privilege Enforcement per Module（per-module IAM级权限）+
  Supply Chain Security（SBOM+CycloneDX+Dependabot CVE）+ Prompt Injection Guard。
  H.可观测性（B4-H01~H05）：Distributed Trace Visualization（Jaeger火焰图）+
  Error Budget Burn Rate Alerting（Google SRE 指标）+
  Capacity Forecasting（历史趋势→扩容预测）+
  Latency Heat Maps（per-module P50/P95/P99）+ Slow Query Detection（SQLite >100ms 标记）。
  I.API协议（B4-I01~I04）：Module API Versioning（SemVer+Major.Minor+废弃窗口）+
  Backward Compatibility Enforcement（CI自动检测破坏性变更）+
  WebSocket/gRPC Stream Management+ Module Discovery & Self-Description（§5.3 ModuleMetadata 代码骨架）。
  J.DevEx（B4-J01~J06）：One-Command Setup（git clone && ./tools/setup.sh）+
  Hot Reload（watchdog监控→自动reload）+ AI REPL/Chat Interface（终端内 /z 命令）+
  Self-Debugging Hooks（失败→自动收集上下文→AI自修复）+
  Codebase Familiarity Score（per-module f(最后修改,Owner次数,AI次数)）+
  Automated CHANGELOG from Git。
priority: "P2"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l01_infrastructure\\module_sandbox.py"
    description: "ModuleSandbox——§5.3代码骨架实现：独立子进程+crash计数+5次永久隔离+Owner通知"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\production\\module_metadata.py"
    description: "ModuleMetadata——§5.3代码骨架实现：自描述+注册+能力声明+AI信心标注"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\production\\code_familiarity.py"
    description: "CodebaseFamiliarityScore——per-module可视化熟悉度"
  - path: "D:\\ZephyrAlpha\\tools\\setup.sh"
    description: "一键启动脚本——自动创建venv+安装依赖+初始化SQLite+启动EventBus"
  - path: "D:\\ZephyrAlpha\\infra\\ci\\security_scan.sh"
    description: "Semgrep 安全扫描脚本——CI/CD 静态分析门消费"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l01_infrastructure\\module_sandbox.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\production\\module_metadata.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\production\\code_familiarity.py"
  - "D:\\ZephyrAlpha\\tools\\setup.sh"
  - "D:\\ZephyrAlpha\\infra\\ci\\security_scan.sh"
forbidden_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"
applicable_rules:
  - module_id: "MOD-INF-002"
    section: "§5.3 ModuleSandbox 代码骨架"
    reason: "spawn_module→restart_if_crashed→5次crash永久隔离+通知Owner"
  - module_id: "MOD-INF-002"
    section: "§5.3 ModuleMetadata 代码骨架"
    reason: "module_id/layer/capabilities/dependencies/api_version/ai_confidence/code_ownership"
  - module_id: "MOD-INF-002"
    section: "§6.6"
    reason: "6维开发者体验矩阵——一键启动/热重载/AI Chat/自调试/代码熟悉度/自动CHANGELOG"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
    reason: "§2.1-G安全/§2.1-H可观测/§2.1-I API/§2.1-J DevEx 盲点 + §5.3 ModuleSandbox/ModuleMetadata代码骨架 + §6.6 DevEx设计"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M2"
estimated_tokens: 25000
timeout_minutes: 60
acceptance_criteria:
  - "G. ModuleSandbox: AI模块独立子进程运行→crash不污染主进程（B4-G01）"
  - "G. ModuleSandbox: 连续crash≥5次→永久隔离+通知Owner（B4-G01）"
  - "G. Semgrep 集成到 CI 静态分析门——代码提交自动扫描（B4-G02）"
  - "H. Slow Query Detection: SQLite 查询 > 100ms→自动标记+建议索引（B4-H05）"
  - "I. ModuleMetadata: 新模块启动自动注册+能力声明——无需手动维护清单（B4-I04）"
  - "I. Backward Compatibility: CI 自动检测新版本是否破坏下游接口（B4-I02）"
  - "J. setup.sh: git clone && ./tools/setup.sh→全量本地环境就绪（B4-J01）"
  - "J. Hot Reload: watchdog 监控 src/zephyr/→受影响模块自动restart（B4-J02）"
rollback_instructions: |
  1. 删除 l01_infrastructure/module_sandbox.py
  2. 删除 shared/production/module_metadata.py / code_familiarity.py
  3. 删除 tools/setup.sh
  4. 删除 infra/ci/security_scan.sh
  5. 如新增目录为空→删除目录
depends_on: []
blocked_by: []
status: "created"
tags_fn:
  - "infra"
  - "security"
  - "observability"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "experimental"
tags_mo:
  - "MOD-INF-002"
  - "MOD-INF-016"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
