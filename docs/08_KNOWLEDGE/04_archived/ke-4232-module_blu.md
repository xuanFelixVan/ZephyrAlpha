---
module_id: KE-4073
title: 决策追溯矩阵（38条全覆盖）
category: module_blueprint
ttl: permanent
---

# 决策追溯矩阵（38条全覆盖）

决策追溯矩阵（38条全覆盖）

| 决策ID | 标题 | 对应 task_id | 实现文件 |
|--------|------|-------------|---------|
| D-021-01 | git-native回滚模式 | 0201,0203 | rollback_executor.py |
| D-021-02 | SQLite dump格式 | 0201 | sqlite_dumper.py |
| D-021-03 | checkpoint策略 | 0201 | rollback-checkpoint-strategy.yaml |
| D-021-04 | 双轨协作 | 0201,0202 | executor+dumper |
| D-021-05 | 失败信号三分类 | 0205 | auto_rollback_trigger.py |
| D-021-06 | revert vs discard | 0202 | executor.discard_changes |
| D-021-07 | partial revert | 0206 | executor.partial_revert |
| D-021-08 | rollback lock | 0208 | rollback_lock.py |
| D-021-09 | forward-fix优先 | 0208,0222 | forward_fix_runner.py |
| D-021-10 | 非跟踪文件保护 | 0209 | secret_rotation_aware.py |
| D-021-11 | 回滚模拟 | 0210 | rollback_simulator.py |
| D-021-12 | G0门禁 | 0204 | rollback_verifier.py |
| D-021-13 | hard reset token gating | 0212 | executor.hard_reset |
| D-021-14 | BREAK_GLASS | 0216 | executor.cancel_pending_rollback |
| D-021-15 | exit code传播 | 0217 | contract.py |
| D-021-16 | gpgt签名链 | 0241 | executor |
| D-021-17 | GDPR遗忘权 | 0252 | right_to_be_forgotten.py |
| D-021-18 | Prompt Injection | 0253 | rollback_integration.py |
| D-021-19 | PSQL连接池 | 0254 | rollback_integration.py |
| D-021-20 | 嵌套环境 | 0255 | rollback_integration.py |
| D-021-21 | MCP不可逆 | 0256 | rollback_integration.py |
| D-021-22 | 取证基础设施 | 0264 | forensic.py |
| D-021-23 | 反向预言 | 0260 | rollback_integration.py |
| D-021-24 | 青野检查点密度 | 0261 | rollback_integration.py |
| D-021-25 | AI自主感知 | 0262 | autonomy_dashboard.py |
| D-021-26 | 持续信任评估 | 0263 | continuous_trust.py |
| D-021-27 | NTP时间证明 | 0246,0264 | temporal_context_adapter.py+forensic.py |
| D-021-28 | git hash存证 | 0264 | forensic.py |
| D-021-29 | Bit Rot检测 | 0264 | forensic.py |
| D-021-30 | kill-9截断/Non-repudiation | 0265 | forensic.py |
| D-021-31 | Owner缺席L3/L1 | 0266 | owner_absent.py |
| D-021-32 | Feature Flag分离 | 0266 | forensic.py |
| D-021-33 | 跨平台Shell | 0243 | cross_platform_shell.py |
| D-021-34 | venv同步 | 0244 | venv_sync.py |
| D-021-35 | env热重载 | 0245 | env_watcher.py |
| D-021-36 | Merkle外部验证 | 0250 | external_merkle_proof.py |
| D-021-37 | Submodule同步 | 0251 | submodule_sync.py |
| D-021-38 | S3快照防过期 | 0249 | s3_snapshot_lifecycle.py |
