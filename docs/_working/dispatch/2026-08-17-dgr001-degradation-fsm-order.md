---
ttl: task_bound
---

施工会话 AI-DGR-001。任务：53 号 §3.8 降级/回退 5 态状态机代码落地（tracker 遗留 #101，#ARCH-QUANT-003 decided，Owner 2026-08-17 裁定派单，与四路并发文件级零交集实证——你域=governance/lifecycle_governance/ 新增模块+paper_live_transition.py 一行耦合+53 号 memo+新测试，禁碰四路施工面）。
worktree 已由统筹创建：D:\ZephyrAlpha\.worktrees\AI-DGR-001（分支 ai/AI-DGR-001/task-degradation-fsm，自 dev 776d4a2eaa 切出）。进入后 `. .\activate_env.ps1`。

背景：
- 真源裁定=#ARCH-QUANT-003（architecture_issue_registry.yaml L14178-14197，方案 C Owner 已批准）：降级维度唯一真源=53 号 §3.8 五态（NORMAL/THROTTLED/SOFT_HALT/HARD_HALT/UNWINDING），落地 evaluate_rollback/recover/safe_read_state，fail-closed+Hysteresis+≥30 笔样本地板；两机唯一耦合点=阶段晋级前置"当前降级姿态=NORMAL"。
- 设计伪代码=53 号 memo §3.8（[53_simulation_live_path.md](../../../docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/53_simulation_live_path.md) L544-696：五态表/迁移触发表/fail-closed vs fail-open 职责区分/Hysteresis/伪代码全量 L571-692）。
- 现状实证：53 号 L463 晋级条件已写明"当前降级姿态须为 NORMAL"但代码侧 paper_live_transition.py L31-37 回退逻辑未实现；QUANT-003 impact 指定落点 src/zephyr/governance/lifecycle_governance/rollback_state_machine.py（新建，与 paper_live_transition 同包）——注意 src/zephyr/infrastructure/rollback/rollback_state_machine.py 已存在但为**回滚步骤编排机**（RollbackStep/StepStatus），语义完全不同，仅同名巧合，你的新文件落 lifecycle_governance/ 包不冲突。

范围（两项，逐项真源引用）：
1. **rollback_state_machine.py 新建**（53 号 §3.8 伪代码 L571-692 逐行落地，QUANT-003 ②）：
   - RollbackState 五态枚举 + _AUTO_TRANSITIONS 单向迁移矩阵 + _HYSTERESIS（intraday_dd trip 0.01/recover 0.003；daily_loss 0.03/0.00；reject_rate 0.01/0.005）+ _MIN_SAMPLE_TRADES=30
   - evaluate_rollback(metrics, current, trade_count)：每 tick 评估，只向更保守态迁移，无自动恢复；P0 事件绕过样本地板
   - recover(current, target, rca_written, dual_approval, position_flat)：恢复须 RCA 已写+双人复核（缺一 PermissionError）；只能向更宽松态（反向 ValueError）；UNWINDING→NORMAL 须 position_flat=True
   - safe_read_state(persisted)：fail-closed——读取失败/无持久化默认 SOFT_HALT（kill switch 停错代价<不停代价，与 circuit breaker fail-open 职责区分，53 号 L567 裁定原文）
   - 状态持久化：复用 src/zephyr/shared/state_store.py JsonStateStore（#ARCH-QUANT-002 已 production，同包先例 default_risk_validator KillSwitch 状态）——REDIS-001 正在同文件加 Redis 后端但同接口零影响你的消费；你只读接口不碰实现
   - 新模块登记全链（硬约束）：creation_token+capability_canonical_file_registry.yaml+module_translation_registry.yaml（plain_zh："降级状态机"）+architecture_issue_registry.yaml 新 ARCH 条目（或复用 QUANT-003 更新 fix_phase）+blueprint 按 blueprint_construction_template.md
2. **两机耦合点 + 文档同步**（QUANT-003 ③）：
   - paper_live_transition.py 晋级前置条件接入"当前降级姿态=NORMAL"校验（L31-37 区附近，最小侵入——晋级路径加一行姿态读取+非 NORMAL 拒绝晋级；耦合点唯一，其余时间两机独立）
   - 53 号 memo §3.8 施工锚点更新（L795"待施工"→落地标注，版本升版；L22 结案报告"未做事项"同步删除该项描述）
   - 测试：tests/governance/（或 lifecycle_governance 对应测试目录）新建——五态迁移矩阵全路径/Hysteresis trip/recover 不对称/30 笔地板/P0 绕过/recover 权限三件套/fail-closed 读取畸形持久化/T+1 UNWINDING 仅 T-1 持仓语义（如涉持仓参数）红队用例

避让（四路并发施工面，零触碰）：
- AI-GOVA-001：gov_enforcement/rule_bridge/、治理脚本、regime/core/regime_detector.py、tests/governance/{data_layer,depgraph,rule_bridge} 及 test_sel_unreachable_5_linkage.py
- AI-LVL3-001：risk/core/ashare_systemic_risk_detector.py、risk_layer_orchestrator.py、ex_core/、37 号 memo
- AI-REDIS-001：shared/state_store.py 实现内部（你只读 JsonStateStore 公开接口）、tests/shared/
- AI-THD-001：governance/lifecycle_governance/post_live_verification.py（同目录不同文件实证零交集）、risk/core/drawdown_tracker.py 等 9 阈值模块、test_alert_threshold_consistency.py
- 特别避让：infrastructure/rollback/rollback_state_machine.py（同名不同语义，读都别改）

验收：①五态 FSM 全路径测试 2 轮全绿+paper_live_transition 既有套件零回归 ②红队实证（fail-closed 畸形持久化→SOFT_HALT/无 RCA 恢复 PermissionError/UNWINDING 仓位非零 ValueError/29 笔不触发+30 笔触发边界） ③新模块五登记链齐全（token/capability/translation/ARCH/blueprint） ④53 号 memo 版本升版+§3.8 落地标注 ⑤Step 1+Step 6（14 节版）双 PASS ⑥全走 GitCommitGateway（[GW:AI-DGR-001]）
完工反馈六要素：commit hash/Step 1/Step 6/测试轮次/改动清单/遗留项。worktree 保留待统筹统一 merge。
