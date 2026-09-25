---
ttl: task_bound
---

# M7-05 · ex_sor 智能执行路由（SOR）

> 挖矿班 st-commitspeed-tbl-20260924 ｜ 2026-09-25 ｜ 只读挖矿
> 任务书预判"若真身不存在则如实记设计态无实装"——实勘结论：**真身存在（27 件 9,271 行+18 测试件），但生产装配零接线=传递性不可达**；另有包头注自相矛盾一处（详见 B1）。本册按实情登记。

## 一、环节定义与边界
D_EX_SOR=智能订单路由域：通道选择/盘口流动性评估/拆单策略/算法执行（TWAP 族）/滑点反馈/卖出时段路由。上游=ex_core 订单意图（供料），下游=券商通道（消费，经 broker_api_connector）。与 ex_core 分工（sor_agent 蓝图 §0 铁律⑤）：optimal_order_router=路由算法件、sor_agent=Agent 实体编排、order_splitter（ex_core）=拆单纯函数委托不重建、llm_agent_router=LLM 模型路由零交集。

## 二、六向台账
| 向 | 内容与实证 |
|---|---|
| 上游输入 | ex_core.execution_engine 懒加载 AlgoTradingEngine+MarketContextProvider（`execution_engine.py:64-66,353-411` G7 AlgoType 映射）；sor_agent 接受 SorRequest（weights 和=1.0 Fail-Closed）； rl_exec_boundary BoundedAction（价格笼子/整手约束内夹取，消费 board_lot/price_cage 语义） |
| 下游消费 | broker_api_connector→券商通道（api/）；slippage_analyzer→divergence_attributor 口径复用（`simulation/divergence_attributor.py:22` 引证）；transaction_cost_optimizer/t0_cost_model→成本面；**生产侧零直接消费者**（见向"当前运行状态"） |
| 自动化触发 | **无**。execution_scheduler 有调度器类但零生产装配；rl_trainer 训练循环独立（测试面）；全族无计划任务/事件总线挂接（grep scripts/ 零命中） |
| 真源与注册表 | 蓝图=docs/03_modules/_domain_ex_sor/（sor_agent/sell_session_router/slippage_analyzer/execution_quality_scorer/transaction_cost_optimizer/rl_execution_training_env 六子目录+index.md）；架构登记=architecture_model D_EX_SOR (L2_domain)（`ex_sor/__init__.py:13` 自注）；路由裁定真源=90_methodology_open_questions.md §19 v2.0.0（`execution_route_policy.py:3-14` 全文引）；查重裁定=sor_agent.py:22-25（smart_order_router 全仓不存在） |
| 门禁与质量尺 | Level 0 纯规则禁 LLM 写入门控；SOR 不做风控（§6.1 归 EX-CORE）；decide 无 IO 无下单语义（纯决策可回放 replay_id 单调）；低流动性通道先行剔除；拆单委托不重建算法；滑点实际 vs 预估回写配对留痕（`sor_agent.py:16-19` INVARIANTS）；human_gated（AI_AUTONOMY 全族最高级） |
| 当前运行状态 | **红（生产不可达）/绿（代码+测试在库）**：18 测试件 tests/ex_sor/ 在册（本班禁实跑只数）；外部消费者 grep 全仓唯 ex_core.execution_engine 一桥（而 engine 自身零生产实例化，04 册 B2）→**传递性不可达**；头注 MATURITY=production 者 9 件指模块质量态非接线态 |

## 三、子模块清单（27 件全勘：core 11+services 5+api 2+根 2+包文件 7；ls+MATURITY+外部消费 grep 三源）
| 子模块 | 是什么 | 入口 file:line | 状态 |
|---|---|---|---|
| core/sor_agent | SOR Agent 实体（B11-02491 族卡模式）：通道选择+盘口评估两技能+滑点反馈循环+全决策回放 | core/sor_agent.py:30（SorAgent 类） | production；消费者=无（运行时装配批"待装配"自注 :8） |
| core/execution_route_policy | 路由策略（90 号 Phase1 项③）：默认限价单+打板专用路径（集合竞价/早盘涨停价申报+封成比≥5% 过滤）+防异常拆单（单笔>5 倍分钟均量→分 2-3 笔隔 3-5 秒） | core/execution_route_policy.py:3-14 | **testing**；与 04 册 B3 打板接线同源 |
| core/sell_session_router | 卖出时段通道分裂路由（MOD-XS-016）：竞价逃命/14:57 深市不可撤/14:30-14:45 跳水窗/做 T 收口，纯函数可回测 | core/sell_session_router.py:1-13 | **design**；与 03 册 sell_execution_planner 相邻未合流（见 B4） |
| core/algo_trading_engine | 算法执行引擎（TWAP/VWAP/POV/IS/ALT）——ex_core.execution_engine 的懒加载依赖 | core/algo_trading_engine.py | production；唯一被 ex_core 引用的族内件 |
| core/algo_execution_selector | 算法选择器（MOD-XS-011，与 execution_route_policy 的分工见其头注） | core/algo_execution_selector.py | production；消费者=无 |
| core/execution_scheduler | 执行调度器（SchedulerError 契约） | core/execution_scheduler.py | production；零装配 |
| core/optimal_order_router | 路由算法件（RoutingError 契约） | core/optimal_order_router.py | production；消费者=无 |
| core/broker_adapter_manager | 券商适配器管理 | core/broker_adapter_manager.py | production；消费者=无 |
| core/market_context_provider | 市场上下文 Protocol（ClickHouse/Redis 依赖隔离，execution_engine:64 注） | core/market_context_provider.py | production；经 engine 懒加载 |
| core/rl_exec_{boundary,contract,env} | RL 执行边界三件：动作夹取（BoundedAction）/契约/训练环境——研究域 | core/rl_exec_*.py | 在库；消费面=board_lot/price_cage 语义复用（头注互指）；训练回路测试面 |
| services/slippage_analyzer | 滑点分析（divergence_attributor 口径复用引证） | services/slippage_analyzer.py | production；口径被复用，本体零装配 |
| services/execution_quality_scorer | 执行质量评分 | services/execution_quality_scorer.py | production；零装配 |
| services/transaction_cost_optimizer | 交易成本优化（715 行族内最大件） | services/transaction_cost_optimizer.py | production；零装配 |
| services/t0_cost_model | T+0 成本模型 | services/t0_cost_model.py | **testing**；零装配 |
| services/rl_trainer/ | RL 训练器（td3） | services/rl_trainer/ | 研究域（测试 test_td3_trainer.py 在册） |
| api/broker_api_connector | 券商 API 连接器 | api/broker_api_connector.py | production；零装配 |
| api/api_rate_limiter | API 限频器 | api/api_rate_limiter.py | production；零装配 |
| risk_redline.py | **实盘红线分级引擎 v0**（YELLOW/RED/GRACE/HALT-RESPECT 按日动作）——MOD-AUTO-L6-001 暂编号，蓝图真源=docs/_working/automation/campaign/blueprints/risk_redline_blueprint.md | risk_redline.py:1-8 | **错位居所**：automation 域文件居于 ex_sor 根——见 B3 |
| models/ infrastructure/ _extensions/ | 空壳包（仅 __init__） | — | 占位 |

## 四、堵点与病灶
| # | 现象/根因/修法/工作量/归属 |
|---|---|
| B1 | **包头注与真身自相矛盾（文档矛盾=事故，宪法 §4.4）**：`ex_sor/__init__.py:13-16` 自注"规划态占位（planning stub）：尚未施工（无蓝图/无代码/无消费者）"，实勘 core/ 11 件 9,271 行+蓝图 6 子目录+18 测试件。修法=改写头注为实态（代码在库/装配缺位）；0.5h；可施工 |
| B2 | **全族生产不可达**：唯一桥 execution_engine 自身零生产实例化（04 册 B2 同根）——sor_agent 的 CONSUMERS 自注"运行时装配批"长期未兑现。修法二选一：①接线路径=execution_route_policy（90 号 Phase1 交付）→assemble 装配进 session 执行腿；②显式裁定"design-frozen 远期"并头注统一（与 04 册 B2 微结构族同批处置）。①1-2 天/②0.5 天；**待裁**（接时点与 Owner 排期） |
| B3 | risk_redline.py 错居 ex_sor 根（MOD-AUTO 编号+automation 蓝图真源）——域归属错位，按域检索必然漏。修法=git mv 至 automation 域或加导航注记双侧互指；0.5h（mv 需走 RENAME-DEPGRAPH-SYNC 链）+登记；可施工 |
| B4 | sell_session_router（design，时段路由）与 sell_execution_planner（03 册 production，执行计划）职责切面未声明：同为"什么时候怎么卖"，一在 ex_sor 一在 sell_decision。修法=蓝图层写分工声明（router=时段×通道×可撤性纯函数；planner=理由×数量×市价限价决策）或合流；0.5 天声明/1 天合流；**待裁**（跨域归并方向） |

## 五、提速与合并机会
- execution_route_policy 的打板专用路径与 04 册 daban_execution 是同一条腿的两半（路由决定走哪条、execution 决定怎么拆）——G22 接线时应一批装配，避免两次动 session 装配层。
- rl 三件+t0_cost_model+crypto rules 同属"研究域在盘"：建议统一打 research 标签集中登记（对齐总筹"研究域不编入生产流通挖矿"裁定），一次审计替代逐件追问。

## 六、自审闸三态
**挖干可施工（结论修正型）**：任务书"设计态无实装"预判不成立——实装在库且测试在册；真实状态=**代码完备+生产装配缺位+头注漂移**。B1/B3 直接可施工；B2 接线方向挂待裁；B4 跨域归并挂待裁。

## 七、复核命令（10 分钟）
```bash
find src/zephyr/ex_sor -name "*.py" | grep -v __pycache__ | xargs wc -l | tail -1   # 9,271 行对账
sed -n '13,16p' src/zephyr/ex_sor/__init__.py                          # B1 头注矛盾原文
grep -rn "ex_sor" src/zephyr scripts --include="*.py" | grep -v "src/zephyr.ex_sor\|test\|#" | grep import  # 唯一桥=execution_engine
sed -n '3,14p' src/zephyr/ex_sor/core/execution_route_policy.py        # 90 号 §19 路由裁定
ls tests/ex_sor/*.py | wc -l                                           # 18 测试件
head -8 src/zephyr/ex_sor/risk_redline.py                              # B3 错位居所证据
```
