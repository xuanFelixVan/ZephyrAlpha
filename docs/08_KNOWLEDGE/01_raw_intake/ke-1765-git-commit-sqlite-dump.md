---
module_id: KE-1674---sqlite-dump---003
status: active
title: 2.1 Git Commit + SQLite Dump 双轨 Checkpoint（决策 D-021-01 + D-021-04）
category: module_blueprint
---

# 2.1 Git Commit + SQLite Dump 双轨 Checkpoint（决策 D-021-01 + D-021-04）

2.1 Git Commit + SQLite Dump 双轨 Checkpoint（决策 D-021-01 + D-021-04）

> **决策 D-021-01（修订）**：git commit 是文件层的天然 checkpoint。每次 AI 改代码 → git commit → pre-commit 检查，git commit 本身就是文件回滚点。回滚 = `git revert`。
>
> **决策 D-021-04（新增）**：git commit 不能覆盖 SQLite 数据。采用 **SQLite dump 双轨**：每次 git commit 前，自动 dump SQLite schema + data 到 `data/rollback/db_snapshots/{commit_sha}.jsonl`，纳入 git track。回滚时：`git revert` 恢复文件 + 从 JSONL 重建 SQLite。**废弃 `rollback_manager.py` 的 DB-only checkpoint 独立路径**。
>
> **决策依据**：工作流已经是 AI 改代码 → git commit → pre-commit 检查。额外独立 snapshot 机制是重复投资。git 是跨 IDE 统一的状态管理，天然支持回滚。对标 Claude Code git-based checkpointing。但 SQLite 数据不在 git 中，必须解决 B1/B3 冲突——dump JSONL 是零额外依赖的最小方案。
>
> **与已有代码的关系**：`rollback_manager.py`（207行）的 checkpoint() / rollback_to() / list_checkpoints() 方法保留但**降级为仅用于调试场景的手动 DB 快照**，不再作为自动回滚路径。新的 rollback 操作统一由 `rollback_executor.py` 执行，覆盖文件+DB 双轨。v0.5.0 新增 `rollback_state_machine.py` 管理部分失败恢复，`forward_fix_runner.py` 提供回滚的替代决策路径。v0.6.0 新增 `rollback_bootstrap.py` 解决回滚系统自举，`hallucination_guard.py` 防护 AI 幻觉攻击，`warm_standby.py` 实现温备热切。v0.7.0 新增 `prompt_injection_filter.py` 防护回滚链路中的注入攻击，`rollback_policy_engine.py` 实现声明式回滚规则。v0.8.0 新增 `audit_sidecar_daemon.py`（独立审计 Sidecar）/ `git_integrity_checker.py`（二进制完整性验证）/ `ntp_attestation.py`（外部时间证明）/ `rollback_forensic_snapshot.py`（取证副本隔离）/ `continuous_proof_chain.py`（持续完整性证明链）/ `toctou_double_check.py`（TOCTOU 双检）。v0.9.0 新增 `operator_heartbeat.py`（Owner心跳+死手开关）/ `tiered_autonomy_governor.py`（分级自治边界治理）/ `feature_flag_registry.py`（特性开关注册表）/ `model_version_contract.py`（LLM版本兼容性契约）/ `agent_confidence_scorer.py`（AI置信度量化）/ `error_budget_autonomy_gate.py`（错误预算自治门禁）/ `rollback_complexity_analyzer.py`（回滚系统自复杂度分析）/ `commit_quality_auditor.py`（commit message质量审计）/ `fail_mode_policy.py`（fail-open/fail-closed策略）/ `context_window_gc.py`（上下文窗口垃圾回收）。v0.10.0 新增 `agent_sandbox_bridge.py`（沙盒基础设施集成桥接——对接Docker Sandbox/Bubblewrap/Seatbelt/E2B）/ `rollback_system_self_defense.py`（回滚系统自我防护——检测AI篡改自身安全代码）/ `runbook_generator.py`（回滚后自动生成SRE Runbook）/ `knowngoodstate_ledger.py`（已验证正确状态收据账本）/ `rollback_target_staleness.py`（回滚目标陈旧度风险评估）/ `credential_rotation_trigger.py`（回滚后凭据自动轮替）/ `rollback_wal.py`（回滚预写日志——操作意图耐久化）/ `cross_agent_conflict_detector.py`（多Agent文件冲突检测）/ `intent_archiver.py`（原始操作意图存档器）/ `rollback_abuse_detector.py`（回滚系统武器化滥用检测）。

```yaml
checkpoint_strategy:
  mechanism:
    file_layer: "git commit = 天然 checkpoint"
    db_layer: "SQLite dump → JSONL → git track（决策 D-021-04）"
  no_extra_independent_snapshot: true
  benefit: "文件+DB 原子回滚 + 跨 IDE 统一 + 历史可追溯 + 零额外依赖"

  dump_pipeline:
    pre_commit_hook:
      - "dump_sqlite(schema + data) → data/rollback/db_snapshots/{commit_sha}.jsonl"
      - "git add data/rollback/db_snapshots/{commit_sha}.jsonl"
    on_rollback:
      - "git revert {commit_sha} → 恢复文件"
      - "从 data/rollback/db_snapshots/{target_commit_sha}.jsonl 重建 SQLite"
      - "G0 门禁验证 → 确认双轨一致性"

  rollback_methods:
    full_revert:
      command: "git revert {commit_sha}"
      description: "回滚单个 commit——安全，
