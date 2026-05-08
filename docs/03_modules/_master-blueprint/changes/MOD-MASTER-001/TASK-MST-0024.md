---
task_id: "TASK-MST-0024"
source_blueprint: "MOD-MASTER-001"
source_section: "蓝图 §二十五 性能基准与回归预防——CT-BENCH-001"

title: "实现跨系统性能基准与回归预防——CT-BENCH-001 每次 PR 自动跑 benchmark"
description: |
  实现 §二十五 CT-BENCH-001 的性能基准与回归预防：
  6 条 CT-* 的 benchmark targets——CT-ORC-CE-001(p95<3000ms+10%退化阈值)/
  CT-CE-VMS-001(p99<500ms+15%)/CT-ORC-VMS-001(p99<1000ms+10%)/
  CT-ORC-GATE-001(p99<50ms+20%)/CT-SCRIPT-GATE-001(p95<30000ms+15%)/CT-CE-LSG-001(p99<100ms+10%)。
  CI 集成: GATE-BENCH-1——每次 PR 触及 CT-* 契约相关代码→自动跑对应 benchmark→退化>threshold→CI FAIL。
  Baseline management: 存储 .audit_cache/benchmarks/baseline_{CT_ID}.json → CI PASS 后自动更新(最近7天 p95 median)。
  Emergency override: GATE-BENCH-1 失败可 override → 需 Owner 审批 + record override reason → audit_log。

priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\gates\\bench_runner.py"
    description: "性能基准运行器——CT-BENCH-001——6条CT-* benchmark+baseline管理+CI集成"
  - path: "D:\\ZephyrAlpha\\tests\\benchmarks\\test_ce_context_build.py"
    description: "CT-ORC-CE-001 性能基准——context build p95<3000ms"
  - path: "D:\\ZephyrAlpha\\tests\\benchmarks\\test_vms_search.py"
    description: "CT-CE-VMS-001 性能基准——VMS search p99<500ms"
  - path: "D:\\ZephyrAlpha\\tests\\benchmarks\\test_orc_vms_write.py"
    description: "CT-ORC-VMS-001 性能基准——Orc VMS write p99<1000ms"
  - path: "D:\\ZephyrAlpha\\tests\\benchmarks\\test_gate_latency.py"
    description: "CT-ORC-GATE-001 性能基准——Gate check p99<50ms"
  - path: "D:\\ZephyrAlpha\\tests\\benchmarks\\test_pre_commit_gate.py"
    description: "CT-SCRIPT-GATE-001 性能基准——pre-commit duration p95<30000ms"
  - path: "D:\\ZephyrAlpha\\tests\\benchmarks\\test_lsg_latency.py"
    description: "CT-CE-LSG-001 性能基准——LSG check p99<100ms"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\gates\\bench_runner.py"
  - "D:\\ZephyrAlpha\\tests\\benchmarks\\**"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

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
    reason: "§二十五——CT-BENCH-001 6条bench targets+baseline management+GATE-BENCH-1"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M5"
estimated_tokens: 20000
timeout_minutes: 90

acceptance_criteria:
  - "bench_runner.py 自动加载6条CT-*的 baseline 并比较 p95/p99 degration < threshold"
  - "GATE-BENCH-1: 每次PR触及CT-*代码→自动跑bench → regression>threshold→CI FAIL+输出退化详情"
  - "baseline 自动更新: CI PASS后 → 使用最近7天p95 median作为新baseline → .audit_cache/benchmarks/"
  - "baseline 30天未更新 → CI WARN(环境漂移告警)"
  - "emergency override: Owner审批 → record override reason → audit_log"
  - "6个 benchmark test 文件全部实现(CE context/VMS search/Orc VMS write/Gate/Pre-commit/LSG)"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\gates\bench_runner.py
  2. 删除 D:\ZephyrAlpha\tests\benchmarks\test_*.py 全部新增文件
  3. 如有baseline → 删除 .audit_cache/benchmarks/baseline_*.json

depends_on: []
blocked_by: []

status: "created"

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
