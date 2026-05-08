---
task_id: TASK-MOD-INF-010-0005
module_id: MOD-INF-010
blueprint_ref: D:\ZephyrAlpha\docs\03_modules\_cross_layer\feedback-loop\blueprint.md
blueprint_sections: ["§2 子系统 v0.15.0（第13轮：External Forensic Auditor）", "§5 v0.15.0 New Files (18)", "§7 R203-R220", "§6 Phase48-51"]
status: pending
priority: P0
created_date: 2026-05-06
assigned_to: null
depends_on: ["TASK-MOD-INF-010-0004"]
blocked_by: []
blocks: ["TASK-MOD-INF-010-0006"]
estimated_effort_hours: 28
actual_effort_hours: null
tags: [v0.15.0, external-forensic, cryptographic-trust, SoD, deterministic-replay, 18-files]
upstream_files:
  - D:\ZephyrAlpha\docs\03_modules\_cross_layer\feedback-loop\blueprint.md
downstream_outputs:
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\forensic\external_verifier.py
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\forensic\crypto_bootstrap.py
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\forensic\architectural_sod.py
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\forensic\deterministic_replay.py
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\forensic\toctou_guard.py
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\gates\action_reversibility.py
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\resilience\resource_starvation_aware.py
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\detectors\gradual_poisoning_detector.py
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\security\remote_attestation.py
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\resilience\deadman_switch.py
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\forensic\sub_agent_collusion.py
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\verifiers\golden_test_external.py
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\security\metric_prompt_scanner.py
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\forensic\worm_write_integrity.py
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\diagnosers\llm_provider_integrity.py
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\forensic\self_modification_audit.py
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\detectors\infinite_loop_detector.py
  - D:\ZephyrAlpha\src\zephyr\feedback_loop\gates\scope_creep_monitor.py
acceptance_criteria:
  - AC-0005-01: 18 个文件全部创建，0 遗漏
  - AC-0005-02: external_verifier.py 独立于FLE的外部验证器启动并运行
  - AC-0005-03: crypto_bootstrap.py 实现 Genesis→Current 哈希链验证
  - AC-0005-04: deterministic_replay.py 实现 seed(timestamp)+temperature=0 锁定
  - AC-0005-05: deadman_switch.py 实现 60s heartbeat+3次丢失→自锁
  - AC-0005-06: R203-R220 缓解措施在对应文件中可追踪
rollback_instructions: |
  1. 删除本次创建的 18 个文件
  2. 回滚 §10 路径索引
context_assembly_manifest:
  required_contexts:
    - context_id: CTX-BLUEPRINT-v0.15.0
      source: D:\ZephyrAlpha\docs\03_modules\_cross_layer\feedback-loop\blueprint.md
      sections: ["§变更记录 v0.15.0"]
      description: 终极轮——外部取证专家视角的致命漏洞补丁
  assembly_notes: |
    v0.15.0 是第13轮——"谁审计审计者？"的元问题首次得到架构性回答。
    External Verifier + Cryptographic Bootstrap + Architectural SoD + Deterministic Replay
    + TOCTOU Guard + Remote Attestation + Deadman Switch 组成外部取证闭环。
---

# TASK-MOD-INF-010-0005: v0.15.0 External Forensic Auditor 轮

## 1. 任务目标

实现 v0.15.0 的 18 个外部取证子系统，覆盖 R203-R220。

## 2. 核心概念

这 18 个文件实现了 FLE 的"法证审计自治"——回答了"谁审计审计者？"：
- **外部独立验证** (external_verifier.py)
- **密码学信任根** (crypto_bootstrap.py)
- **SoD 职责分离** (architectural_sod.py)
- **确定性回放** (deterministic_replay.py)
- **远程证明** (remote_attestation.py)
- **Deadman Switch** (deadman_switch.py)

## 3. 验证方式
```bash
python scripts/governance/verify_module_coverage.py --module-id MOD-INF-010 --version v0.15.0
```
