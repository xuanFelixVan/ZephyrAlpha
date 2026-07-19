---
module_id: MOD-GOV-debt-fix-queue
title: 债务修复队列（未跟踪维度验证发现的新待修项 + 遗留）
version: 0.1.0
layer: L2_domain
depends_on: [architecture_debt_registry]
tags: [fix-queue, architecture-debt]
ttl: task_bound
doc_type: audit_report
completes_when: 本队列全部清空且 architecture_debt_registry.md 全部维度状态行回写完成
---

# 修复队列（第102轮验证发现 + 施工遗留）

## A. 未跟踪维度验证（5.2-5.30，explore 报告）新发现待修项
1. 5.7 [CI] `.github/workflows/governance.yml:138,290,321` — 3 个 CI step 引用已迁移脚本旧路径 → 更新为 `d3_metadata/check_registry_consistency.py`、`d3_metadata/validate_tool_contracts_consistency.py`、`d11_compliance/ci_self_check.py`
2. 5.20 [日志] print 705 处 / getLogger 613 处 — 无收敛门禁；需定 SSoT 日志入口 + 是否加 gate（裁定：规模太大，先评估分布再定）
3. 5.21 [测试] tests skip 218 处 + importorskip 264 处（5.8 交叉） — skip 理由审计
4. 5.25 [复杂度] `orchestrator/contracts/contract_registry.py` 1087 行拆分；AutoRuntimeCore 48 方法（god_class_gate 只防新增）
5. 5.24 [性能] `gov_drift/correlation_engine.py:78-79` O(n²) 双重循环
6. 5.15 [SSoT] `integration/shared/events/dlq.py` vs `shared/events/dlq.py` 双副本归一
7. 5.27 [SSoT] 2 份 `session_lifecycle.py`（security/access_control/ vs gov_enforcement/behavioral_admission/）归一
8. 5.30 [构建] `Dockerfile:20` 移除 `-r requirements-dev.txt`（dev 依赖入生产镜像）；引入锁文件（裁定：锁文件用 uv/pip-tools？）
9. 5.29 [Git] 补 `.github/CODEOWNERS`
10. 5.3 [capability] 登记 5 个未注册 gate 的 capability（depgraph_freshness/git_call_budget/reconciler_health/rule_execution_pairing/undefined_name_gate）
11. 5.10 [orphan] 清理 M07=3（decision_registry.py/guard_layers.py/feedback_loop/subdir/test_file.py——先查是否真孤儿）
12. 5.13/5.9 [文档] AGENTS.md 叙述数字更新（53域→62、52gate→99、34词表→39、10MCP→12）

## A2. 未跟踪维度验证（5.43-5.113，explore 报告）STILL-VALID 残留
- `_base_server.py:387` JSON-RPC notification（无 id）仍回包 id:null
- `event_bus.py:114` event_id 秒级 strftime 可碰撞
- `work_orchestrator.py:93-94` load_dags `except Exception: continue` 无日志
- `dlq.py:78/268-276` error_traceback 原文入库无脱敏
- `timeout_guard.py:77` _handlers 只写不删
- `gov_drift/state_machine.py:70` _events 无淘汰
- `reconciliation_registry.py:5087` blueprint frontmatter write_text 非原子
- `ide_health_daemon.py:468-472` cleanup_stash subprocess.run 未查 returncode
- `alert_dispatcher.py:92` DispatchError 死异常类（全库无 raise）
- `process_pool.py:208-209` stop_zombie_scanner 不 join
- 67 处/36 文件 Enum == 而非 is
- `daemon_registry.py:86-87` ClassVar 可变 dict（有锁，低危）
- （`shared/__init__.py`/`trading/__init__.py` __all__ 已由本 session 5.93.3/5.93.4 处理，待 merge）

## A3. 未跟踪维度验证（5.115-5.177，explore 报告）STILL-VALID 残留
- 5.115：risk_limits.py:70-75 / provider_base.py:95 / quality_gate.py:96-101 / risk_validator.py:88-93（_registry 只写不读，Phase-B 骨架）
- 5.120：trading/verdict_engine.py:188（if-elif 分发，LOW）
- 5.128：src/zephyr/__init__.py:173-192（import 启动 2 daemon Timer——**裁定 RATIFY，auto_bootstrap 刻意设计**）
- 5.130：session_id 日志 11+ 处（低危，非认证令牌）
- 5.131：runtime_interceptor.py:179 `reset_allowance_for_request` 零调用点（缓解死代码，**接线 1 行即闭环，最可操作**）
- 5.132：reconciliation_registry.py:502/559/631/711/777/859/900/1540/1622（9 处裸 sqlite3.connect 绕过 get_db_connection SSoT）
- 5.141：deepseek_chat.py:57、llm_gateway.py:139、deepseek_v4_chat.py:80（DeepSeek URL default 字面量×3）
- 5.149/5.172：event_bus.py:102-105（get_instance() 单例无锁无双检，两维度同源）
- 5.161：event_store.py:122、atomic_transaction_manager.py:164（_now_iso 私有副本）
- 5.167：pipeline_base.py:95（pooled_std == 0 浮点精确比较）
- 5.170：session_worktree.py（37 处 print，stderr UX 部分刻意）、session_continuity.py（24 处）
- 5.177：cost_budget.py:134、meta_guard_latency_budget.py:47、rbac_bridge.py:48（check_ 函数非布尔返回）

## A4. 仪表盘指标漂移（2026-07-19 latest.json，其他 session 新增引入）
- M01=1：`scripts/governance/generators/generate_rule_ai_perception_index.py:6` [STARTUP] 'on_demand' 不在 startup_vocabulary.yaml（改合法值或登记词表）
- M03=3：`query_metrics.py:enabled()` 与 `ch_batch_size_gate.py` 的 `_is_exempt_file()`/`_build_parent_map()` 重复簇（收敛或 noqa: m03-duplicate 豁免）
- M04=8：8 个新 gate 未登记 capability（depgraph_freshness/git_call_budget/manual_only_permanent/reconciler_health/rule_execution_pairing/snapshot_drift/+2）——登记到 capability_canonical_file_registry.yaml
- M07=3：`feedback_loop/subdir/test_file.py`（16B junk `print("hello")`，RULE-THREE 删除）+ `security/access_control/decision_registry.py`、`guard_layers.py`（先查是否真孤儿）
- M17=65、M19=206、M20=4、M21=3（其他 session 新增指标，其负责域，评估后协同）
- 5.176 编号冲突（SQL注入 vs AI-11遗留同号）——文档修复

## B. 施工遗留（各 agent 报告）
- error_code_registry.yaml：ZA-IG-0015（B2 删 integration schema）+ ZA-TR-0002/0003（B14 money.py 收敛）悬空条目清理
- 5.34.7 reconciliation_registry.py 最后 1 处 governance.db 字面量（被 sess-27964-p0 持有，其已部分处理，补提）
- 5.34.7 范围外 governance.db 字面量：f5_shutdown_manager/rollback_verifier/rollback_drill/ke_tombstone/self_test/rule_watcher
- B4 agent 建议：config/.env.postgres.test 模板（裁定后决定是否创建）
- 5.150.2 AutoRuntimeCore God Class 拆分（待 auto_runtime_core.py 稳定后）
- 5.152 跨层依赖 10 边（B11 完成后启动）
- 5.176.4 测试 7 个 HEAD 预存失败（test_ttl_gate/test_directory_contract_gate skip-logic 夹具补 d1_structure——另一 session 区域，评估后处理）

## C. 已完成（worktree commits，sess-29344）
B3构建/B2收敛/B1词表/B9状态机/B6API限流/B4迁移容灾/dr_policy/B12ACID/B15depgraph/5.37审计/5.38+5.39/5.40幂等/5.62+5.71+5.80/B5环境/B14残留/B10异步锁/5.93.3/小项组合(5.176.4+5.42.4+5.97.6)/5.153.13/B11耦合/5.150试点/5.174-M5M6
