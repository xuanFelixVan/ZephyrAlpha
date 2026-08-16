---
ttl: task_bound
---

施工会话 AI-LVL3-001。任务：37 号流动性危机 Protocol LEVEL_3 生产接线（Owner 2026-08-17 裁定派单，P0 风控接线批遗留项，与 AI-RFIX-001 文件级零交集实证——你域=risk/core/ashare_systemic_risk_detector+ex_core 编排层接线点，禁碰 RFIX 施工面）。
worktree 已由统筹创建：D:\ZephyrAlpha\.worktrees\AI-LVL3-001（分支 ai/AI-LVL3-001/task-liquidity-level3-wiring，自 dev aaa570ea70 切出）。进入后 `. .\activate_env.ps1`。

背景：
- 37 号 memo L21 明示："LEVEL_3（最高级危机处置）生产接线未做——P0 风控接线批遗留，待后续批次"
- 现状：AshareSystemicRiskDetector（src/zephyr/risk/core/ashare_systemic_risk_detector.py）已 production——5 大信号扫描（含 LIQUIDITY_CRISIS）+三级警报递进（1 信号 LEVEL_1 停开仓/2 信号 LEVEL_2 降仓 30%/≥3 信号 LEVEL_3 清仓）+情绪断路器（≥0.85 强制 LEVEL_3）+build_escape_directive 逃生指令（仅 LEVEL_3 可产出，非 LEVEL_3 调用抛 InvalidSystemicRiskInputError）
- RWIRE/RRESIL 已落地：KillSwitch 状态落盘 Fail-Closed+LIQUIDATING 锁+execute_kill_switch_liquidation production 接线+risk_layer_orchestrator.py（MOD-L06-001）组合级风控编排
- **缺口**：LEVEL_3 检测→逃生指令→Kill Switch 执行的生产链路未接——detector.check() 在盘内链路无调用点，逃生指令无消费者

范围（先读真源再定施工面）：
1. 真源精读：37 号 memo（docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/37_liquidity_crisis_protocol.md）LEVEL_3 相关段（L84-85/L222-262 响应映射+逃生执行器+差异对齐/L342-399 降级机）+ 裁定书 docs/_working/reviews/2026-08-16-dual-review-adjudication.md §二
2. LEVEL_3 生产接线（按 RWIRE 先例接 risk_layer_orchestrator）：
   - detector.check() 调用点嵌入盘内风控评估链（risk_layer_orchestrator 编排层，与 VaR/ES/drawdown 同层）
   - LEVEL_3 SystemicRiskAlert → build_escape_directive → execute_kill_switch_liquidation 消费链接通
   - 降级机接线：LEVEL_3→LEVEL_2 冷却 30min+信号≤2 降级路径（37 号 §降级机表）
3. 红队实证（对齐 RWIRE 标准）：≥3 信号构造→LEVEL_3 真实触发→逃生指令产出→Kill Switch 真实置位清算全链（非 mock）；情绪断路器 0.85 强制升级实证；非 LEVEL_3 调用 build_escape_directive 抛错实证；冷却期降级实证
4. tracker #42 关联项甄别：37 号蓝图 §5 两项跨会话排期（①编排层接入 35 号 §3.13 调用方——与本项重叠的并入施工；②IPO 数据源接入——数据层不在本批，登记遗留）

避让：
- AI-RFIX-001 施工面 5 文件+4 测试+memo 31/36（risk/core/var_calculator.py+tail_risk_monitor.py / position/core/drawdown_controller.py / ex_core/order_manager.py / pf_alloc/core/regime_meta_allocator.py）——零触碰
- trading_session.py / risk_layer_orchestrator.py 已由 RWIRE-001 接线——你只加 LEVEL_3 接入点，不改既有接线逻辑
- fill_handler / PositionTracker / DefaultRiskValidator 已由 RRESIL-001 施工——只读不碰内部
- AI-GOVA-001（governance 域）/AI-REDIS-001（shared 域）并发施工中——各自域不碰

验收：①新增测试 2 轮全绿+既有 risk/ex_core 套件不回归 ②红队三向量实证（多信号 LEVEL_3 全链/情绪断路器/冷却降级）③Step 1+Step 6（14 节版）双 PASS ④全走 GitCommitGateway（[GW:AI-LVL3-001]）⑤37 号 memo 版本升版+接线完工标注（Step 7）
完工反馈六要素：commit hash/Step 1/Step 6/测试轮次/改动清单/遗留项。worktree 保留待统筹统一 merge。
