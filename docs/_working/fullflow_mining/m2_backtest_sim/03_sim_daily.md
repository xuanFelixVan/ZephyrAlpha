---
ttl: task_bound
volume: 03_sim_daily
session: st-commitspeed-tbl-20260924
---

# 03 · 模拟盘日链（plan-bridge/桥执行/账本/日刊/治理）

## 一、环节定义与边界
交易日自动化链条：日计划→模拟姿态翻译（plan-bridge）→盘中桥执行（bridge-execute，09:35/13:05 两火点）→E4 观察档重放（e4-replay）→日报告账（report/settle）→平台日刊与健康三检（journal）→月度治理（deviation/attribution/governance/promotion）。上游=丁线 judgment_daily_plan（只读）+QMT 沙箱桥；下游=sim 台账表族+Owner 月审。**红线：模拟盘四禁在岗，本车道零实跑。**

## 二、六向台账

| 向 | 内容（证据） |
|---|---|
| 上游输入 | judgment_daily_plan/judgment_intraday_market_state（丁域只读）；strategy_screen verdict=oos_tested+translated/c4_<hash>_*.py 翻译件；QMT 沙箱桥（HTTP 快路径中位 32ms，失败降级文件桥 fail-open） |
| 下游消费 | c1_backtest.sim_daily_report（判定台账）/sim_trade_log/sim_pocket_daily/sim_platform_journal；月度：sim_deviation_report/sim_attribution_report/sim_promotion_memo/promotion_combo_gate/league_*；pf_alloc SIM_DAILY 事件（07 册） |
| 自动化触发 | 计划任务 ZephyrAlpha_SimBridgeExecute（实测 State=Ready；09:35/13:05 Mon-Fri；run_sim_bridge_execute_daily.ps1 三防：is_trading_day fail-closed SKIP/XtItClient 存活检/PS5.1 stderr 经 cmd /c）；ZephyrAlpha_PaperSession（实测 Ready；13 号文标注"DISABLED→Ready 转换无登记记录"待实查）；ZephyrAlpha_PostSettlement（Ready） |
| 真源与注册表 | 蓝图 MOD-BT-222；schemas/categories/sim_pocket_daily+sim_trade_log（DDL-as-code）；钱包注册表 lifecycle==sim（registry_sim_entries）；qmt_environments.yaml（live account='' 空+blocks_live_trading=true） |
| 门禁与质量尺 | **四禁正典**：QMT_REAL_*/enable_real/ZEPHYR_ENV=live/LiveSimulationSwitcher.switch_to_live 全禁；**三道锁**：①pre_execution_checker.py:61-94,259-274 fail-closed 拒全部新单（C2 红已闭）②live_simulation_switcher.py:8,26-30 一次性令牌③qmt_file_bridge_integration.py:54,66 enable_real=False 默认；bridge-execute 幂等=signal_batch=plan-bridge-<day>+orders_sim.csv idem-key 同日重跑不双下单；R-H5E-1 盘前门（裁定#338-5）注入 |
| 当前运行状态 | **绿**（带两处观察）：健检三件在岗；freshness 病灶已治本（expected_fresh_date，09-15..21 十行假阳→时点感知 T-1 口径，日历降级 fail-closed 不放宽：sim_platform_journal.py:59-83）；孤儿钱包隔离 R5 清偿（STR-AUTO-001 型幽灵不再污染平台汇总） |

## 三、子模块清单（11 子环节）

| # | 子环节 | 入口 file:line | 状态 |
|---|---|---|---|
| 3.1 | plan-bridge：日计划姿态→模拟盘姿态，防御（stand_aside）=唯一可机械执行（=空仓）；其余动作如实记 unexecutable(action_not_order_mapped) 零伪造 | scripts/backtest/sim_daily_runner.py:31-35（头注契约） | 绿 |
| 3.2 | e4-replay：观察档重放出模拟单（方案C 收盘价成交；观察本金 100 万 flat；与注册表 sim_daily 平面分离不占分配链额度；首夜 --limit 控面） | sim_daily_runner.py:36-40 | 绿 |
| 3.3 | report/settle：平台汇总行+累积结算扫描（settle(D) 结算所有 report_date<D 未结算行，幂等可重入——错过的日子不丢账） | sim_daily_runner.py:41-44 | 绿 |
| 3.4 | bridge-execute：盘中桥执行（限价取活桥报价，stale quote→不下单；env="sim" ONLY，真账户=Owner 门位） | run_sim_bridge_execute_daily.ps1:17-27 + sim_daily_runner | 绿（安全三防在） |
| 3.5 | 计划任务接线 | scripts/register_sim_bridge_execute_task.ps1；实测 schtasks 4 任务 Ready | 绿（13 号文待实查项照录） |
| 3.6 | 方案C 账本（内置引擎 STR-VREV-025：上证跌≤-1.5%/-1.4%→次日 000852 全仓，持 19 交易日期强平；BUY 7.5bp/SELL 17.5bp 与回测同成本模型） | sim_paper_ledger.py:36-46（常量区） | 绿；C1 参数化多策略开户（--strategy-id/--from-registry）在 |
| 3.7 | 平台日刊+健康三检（新鲜度/账本心跳/越界持仓；QUOTA_WARNING=110 万=额度+10% 容差；收盘落库缓冲线 15:05） | sim_platform_journal.py:31-33,:59-83 | 绿（freshness R3 治本） |
| 3.8 | 月度偏离报告（模拟实跑 vs 同期回测四项对照：信号一致率/漏单率/成交价偏差/收益偏差含时机拆分；全过=sim_deviation 月度通过，任一不过=monthly_breach） | sim_deviation_report.py:17-21 | 绿 |
| 3.9 | 收益归因四段（策略分解/成本吃多少/基准超额 000852 主+000300 次/风险贡献） | sim_attribution_report.py:17-21 | 绿 |
| 3.10 | 治理建议器（连续 2 月 deviation 通过→sim→paper 建议；连续 2 月 breach→sim→decayed；oos_years_decay>=0.5 存疑；只出建议不改册，册变更=Owner 裁定） | sim_governance.py:22-31 | 绿 |
| 3.11 | QMT 桥执行器适配器（HTTP 桥快路径 POST /order→EXEC v16.4，实测中位 32ms≈miniqmt；失败自动降级文件桥；指令 CSV↔沙箱哑执行器 v14/v16 双向） | src/zephyr/ex_core/adapters/qmt_file_bridge_broker.py:17-30 | 绿 |

## 四、堵点与病灶
1. **校准分母为零（IBT-H02）**：sim_trade_log 切点前 0 行——回测↔实盘滑点偏差校准闭环零样本（11_integrated_backtest_audit.md §0⑧）。修法：bridge-execute 量产成交流水后回填标定（依赖 3.4 稳定跑，时间解法非代码解法）。**跨车道移交**。
2. ** PaperSession 任务状态转换无痕**（DISABLED→Ready 无登记记录，13_trading_chain_audit.md 待实查①）——文档矛盾=事故条款已登记。修法：任务启停一律留痕。XS。M5。
3. **订单语义映射面窄**（3.1 只有防御姿态可机械执行，其余 unexecutable）——平台铁律要求 Owner 批后扩，属**待裁**（扩哪些动作的映射顺序）。已入 pending_rulings。
4. registry 读失败时 registered_ids=None fail-open 保汇总不断（sim_platform_journal.py:92-95）——与"宁可假阳"精神相悖的局部放宽，有 BLE001 注记自证，属已知取舍非漏洞。
5. **撮合面**：回测撮合=zephyr/backtest/core/matching_engine.py+matching_logic.py（eval_exp_expectations 消费 MatchingConfig #233）；模拟撮合=方案C 收盘价口径（乐观偏差由偏离报告单列监督——sim_daily_runner INVARIANTS 自注）。两撮合口径差异被监督件覆盖，闭环成立。

## 五、提速与合并机会
- 3.8/3.9/3.10 三月度件+league 快照（02 册 2.6）四命令四处落点→合并"模拟盘月报编排器"（一命令四产物，落点统一 data/backtest_artifacts/sim_monthly/）。
- run_sim_bridge_execute_daily.ps1 的三防逻辑（交易日历/终端存活/stderr 陷阱）已在三处 ps1 重复（保活循环/日刊同款收盘时点常量 CLOSE_CHECK_BJ）——可提取共用 ps1 库。S。

## 六、自审闸三态
**挖干可施工**（11 子环节全部 file:line 实证；四禁/三道锁/幂等键引用 13 号文+代码双源交叉）。堵点 1/2 移交，3 待裁。

## 七、复核命令
```bash
sed -n '25,50p' scripts/backtest/sim_daily_runner.py
sed -n '1,30p' scripts/run_sim_bridge_execute_daily.ps1
powershell -NoProfile -Command "Get-ScheduledTask | ? TaskName -like 'ZephyrAlpha*Sim*' | select TaskName,State"
sed -n '59,83p' scripts/backtest/sim_platform_journal.py   # freshness 治本实证
grep -n "四禁正典" docs/_working/decision_map_campaign_20260924/13_trading_chain_audit.md
```
