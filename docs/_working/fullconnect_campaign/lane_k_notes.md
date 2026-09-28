---
ttl: task_bound
title: K 线施工台账（zc-lane-k-20260927）——F60 减仓编排/F61 重启重臂/PostSettlement 注册脚本形态
session: zc-lane-k-20260927
create_guard: creation_token 待 capability 册锁（st-final-build-20260926 册先行袋）释放后随批补办（M2/P 线先例）
---

# K 线台账（zc-lane-k-20260927，2026-09-27）

## K1 F60 回撤减仓编排接线（liquidation_guard 209 行零消费 → 仲裁点消费）

- 影响面判定：接线点=RiskLayerOrchestrator._engage_kill_switch（单一仲裁点），生产装配唯一点=start_paper_session.assemble_risk_layer（INVARIANTS"仅连 QMT 模拟账户"）=paper/sim 面；改动纯加预检/告警（只减撤单、零新增发单），未触实盘资金路径，无 99 登记项。
- 改动：risk_layer_orchestrator 接 drawdown_liquidation_guard 双函数——①check_cancel_rate 撤单前预检（新增 order_stats_provider 进料，≥15% blocked → scope 降级 position 撤单腿跳过=§3.5.1 小额挂单留自然到期；≥12% warning 放行留痕；provider 缺失/失效=fail-open 既有行为零变化）；②check_liquidation_timeout 清算后券商实时持仓复点（残余非空超 30s → CRITICAL 告警人工介入，不自动强平）；RiskLayerConfig 新增 liquidation_timeout_seconds=30.0。
- 生产进料：start_paper_session._order_stats_provider=OrderManager.declaration_guard（CancelRateGuard total_cancels/total_resolved）；guard 缺省 (0,0)→"无委托无约束"不阻断。
- 测试：TestLiquidationGuardWiring 6 例（blocked 降级/warning 放行/超时告警假钟/provider 缺失 fail-open/provider 抛错 fail-open/零委托无约束）全绿；Windows monotonic 粒度粗（相邻读数差 0.0）→ 超时例用编排器命名空间假钟 +60s 确定性触发。

## K2 F61 KillSwitch 重启失忆窗（rebuild 零生产调用 → TradingSession.start 一行接入+拒单演练）

- 影响面判定：rebuild 纯加闸不加放（store INVARIANTS），只重臂不解除，零实盘路径；影子文件读写全程 tmp 隔离（测试），生产路径只读不写。
- 改动：trading_session.start() 在 connect 前调 kill_switch_state_store.rebuild_from_disk()；重臂非空 → CRITICAL KILL_SWITCH_REBUILD_AT_START 留痕。
- 拒单演练（F61 缺口 4，G5 前置）：新件 tests/trading/test_kill_switch_rejection_drill.py 5 例——绿链（假校验器触发 DAILY_LOSS→HALT 拒单→落盘影子→内存失忆模拟重启→rebuild 重臂→拒单维持→rebuild 幂等复跑）/红态（无影子不重臂不拒单；损坏影子零重臂 fail-safe）/start 接线实证（start 后 active_switches==[DAILY_LOSS]）。
- 坑：isolate fixture 前置 tks.reset 会经落盘钩子建出影子文件污染红态断言——前置改直翻内存旗标。

## K3 PostSettlement 注册脚本坏形态活雷（bc76efe3bf 重注册即复断）

- 实勘定案：HEAD a0446129e3 已纯回植 8f0e5feba9 修复块（conhost --headless + cmd /c 真重定向），F82 卷判"已修复"正确，F76 卷缺口 2 系时序差（复测早于回植落地）。脚本现形态 65 行逐行核过：无残留坏点，未来重注册安全。
- 增量：脚本零改动（禁 schtasks 写遵守，重注册=Owner 门未触碰）；新件 tests/trading/test_register_post_settlement_task_form.py 7 例静态形态断言防复发——活雷断言（python 直挂 -Execute 形态出现即红）/conhost+cmd /c 真重定向/in-place Set 不 unregister/工作日 15:30/IgnoreNew+超时杀/纯 ASCII。红态证明：断言组对 bc76efe3bf 坏 blob 实测全数翻红（地雷探测器有判别力）。
- 病根追记：bc76efe3bf 是 lookup 提交连坐吸收他会话回退（AGENTS §2.5 暂存区吸收事故实例），本测试即该横断病的长期探测器。

## 门禁与登记

- capability_lookup 审计：熔断 2/回撤 3/计划任务 1 命中（session_id=zc-lane-k-20260927）。
- 锁：4 文件 acquire（orchestrator/trading_session/start_paper_session/test_risk_layer_orchestrator）；毕后 release。
- 本台账 token 待补：capability 册被 st-final-build-20260926 [册先行袋] 活锁持有，acquire 失败——不空转不硬闯，code+tests 先行落地，本台账 token 随册锁释放后补办。
- 测试读数：相关 10 套件 254 passed（ex_core 3+trading 4+scripts 1+risk 2），零 fail 零 skip 新增；ruff I001+format 治理后复跑 114 passed。

## 落地战况（2026-09-27 07:3x-08:0x， Landing 未遂三次全录）

- 直连尝试（5 文件窄清单）：preflight 三项=WORKTREE（--allow-non-worktree 可解）+COMMIT-SCOPE（--allow-multi-domain 留痕）+FOLDER-CAPACITY-HARD-LIMIT（scripts/ 122>120 硬拦 start_paper_session.py，gate 无旗、挪子目录非本车道职权→接线件缓办）；改 5 件清单后过 preflight，锁内被 MUTABLE-CONST-WITHOUT-FINAL（own_scope=false 全仓登记 gate）阻断——违规件=st-fms-chief-20260927 在飞 staged read_side/*（他会话在途违规不代修）。
- 队列三连：q-0001/q-0002 dead=cascade_stale"head_reader 缺失无法重校验"（serializer 基建缺件，自动进堵点本归维护班）；q-0003 dead=prestage 拒绝（快照吸入 gitignore 外来件）+GATE-PRECOMMIT-RUN。队列全局当日 828 dead/731 done=基建重度降级窗口，与他车道死袋替补先例（9a6dd64d05/c5a6f3d238）同型。
- 工作区就绪态：5 件代码/测试（ruff 治理毕）+start_paper_session.py 进料接线+本台账，全部就绪待落地；建议基建恢复或 st-fms staged 面清空后，首选拉直连 5+1 文件窄清单重试。
- Ruff 治理附记：I001 两处修复；format 三件（trading_session 665 行为 HEAD 既有漂移随批自洽，非他会话在飞内容）。

