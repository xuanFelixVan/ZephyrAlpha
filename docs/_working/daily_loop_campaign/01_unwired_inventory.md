---
ttl: task_bound
session: st-dloop-20260921
issue: DLOOP-V2-UNWIRED-INVENTORY
completes_when: A/B 类施工落地+C 类申请单呈批（Owner 扩面令 2026-09-21 12:5x）
---

# 01 全项目"未进编排器"清单（Owner 扩面挖矿总账）

> 挖矿=三路只读审计（新闻LLM链 / plan_engine 13 件 / 五层门+全仓）+ 对账总账 §1-§6。
> 口径：事件链=pipeline_events 9 棒（自动）；总扳手=daily_loop_master_switch 三段（手动圈）。

## A 类：立即施工（零新权限，挂总扳手段位）——本班落地
| # | 件 | 挂点 | 依据 |
|---|---|---|---|
| A1 | llm_premarket_analysis（MOD-PLAN-007，工序定义了无执行者） | 总扳手 premarket 段 | LLM 经 llm_runtime_gateway（LSG 必经）；llm_client=None→skipped_not_wired 内建 |
| A2 | intraday_sentiment_loop.run_once（MOD-DATA-063，单拍就绪没节拍） | 总扳手 intraday 段 | prediction_log sentiment_score 落库幂等；previous_board 跨拍态 v1=None+注记 |
| A3 | auction_hit_recorder（MOD-PLAN-015，10:00 时点判定） | 总扳手 intraday 段+事件链钩子 | 本地 10:00-10:30 闸+业务日记号；60min bar 无 10:00 棒（10:30/11:30/14:00/15:00），蹭 10:05 分钟批 |
| A4 | similar_day_evaluator（MOD-PLAN-016，只读统计） | 总扳手 postmarket 段 | 零写库零副作用 |
| A5 | scenario_attribution_stats（MOD-PLAN-009，纯统计） | 总扳手 postmarket 段 | 同上；W0 三维归因观察段 |

## B 类：事件链新增钩子（代码落地即生效于 DataScheduler 下次重启）——本班落地
| # | 件 | 挂点 | 依据 |
|---|---|---|---|
| B1 | daily_warroom_pipeline（MOD-PLAN-018，唯一未上链棒） | 事件链 Phase 2a 后 maybe_run_warroom_pipeline | 幂等=prediction_log UNIQUE；W0 20 日样本积累从此自动化 |
| B2 | auction_hit（同 A3） | 事件链 maybe_record_auction_hit（唤醒词 kline_etf_1min/5min+10:00-10:30 闸） | 10:05 分钟批=天然唤醒，尾窗 VWAP 不漏 |

## C 类：需新产出方/新阈值/写库面——设计稿已出（wiring_proposals_*.md），Owner 批后施工
| # | 件 | 缺什么 | 批点核心 |
|---|---|---|---|
| C1 | **L2 板块门日态产出方**（今晨拍板 degraded=D2:L2 根因：_collect_l2 是 stub，产出方从未存在） | 日态产出者或 water_temp 桥接 | 阈值 v2.1 待 G05 校准；桥接口径=拍板链新判定逻辑，禁代批 |
| C2 | recon_runner 15:40 对账 | tasks.yaml 任务行（0 行假通道）或 scheduler handler | tasks.yaml=Owner 门；QMT 不在线降级语义 |
| C3 | cohort_daily_ledger | CH 写入器+任务行 | 纯函数就绪零写库；tasks.yaml 禁碰 |
| C4 | plan_deviation_monitor（蓝图 T4 对接件） | Decimal 适配器+record_sink | AI_AUTONOMY=human_gated，自动挂=越权 |
| C5 | batch_boundary_runner | maybe 包装+候选清单真源（作战池） | 写库件 SAFETY=M |
| C6 | scenario_probability_model（W2 九格概率） | 双 provider 适配器（8态/密度层） | 三层全缺 fail-closed；与 next_day 双源口径需 Owner 标注 |

## D 类：封存（有据在册，不为接线而接线）
closing_session_decision（缺盘中推演+高低开概率生产者；执行域消费）／trading_analyst_agents+trading_debate（W4 LLM 席位消费面，GAP-F-44）／execution_deviation_attributor（计划+执行双断电）／thesis_survival（X 流离场域）／intraday_tomorrow_forecast（三消费点未接线，在册封存）／evidence_chain_decision（schema 层，随预案卡激活）／premarket_workflow_engine（与 021 近重复，禁平行实现）／premarket_workflow（conductor 不存在；归并设计随 C 类另批）／G07 情绪周期（30号§6.3，准确率评估挂起）／expectation 六因子（SOP-B 排队）／event_score（design）／social_sentiment_collector+sentiment_engine（装配批无装配者）／llm_market_interpreter+llm_fundamental_analysis（与 007 查重待裁，防三件重复烧 LLM）。

## E 类：核实=已在自动跑（Owner 问句的正面回答）
新闻采集 5 任务→news_data（快 event_driven+慢 news_slow 队列）→ regime 新闻特征（事件链 regime 棒间接消费，4600 日数据在喂）→ nightly_sentiment_window（08:20 定时，写 news_sentiment_window）→ 研报 C1.5（research_nightly→consensus_daily，e83f5926）→ sim 日件三连（事件链第7棒）→ 五层门 L1/L3/L4/L5 采集（编排器 S3 直读）→ dashboard warroom 今日决策面板（直读 decision_daily，无需新端点）→ paper_session 09:25（调度器外执行面，模拟盘保活）。

## F 类：特殊发现（记录在案）
- F1 kill_switch 跨进程缺口：编排器 L5 读本进程单例，paper_session 的 JsonStateStore 外部化熔断态读不到——建议 L5 改读落盘态（小改，随 C 类批）。
- F2 crypto 影子线：SIM_DAILY_WAKE_TASKS 不含 crypto 任务，crypto_kline 不唤醒 9 棒（设计内"只记账不进 TDM"）；进拍板需扩唤醒词+TDM crypto 段施工（远期单）。
- F3 新闻→盘前断点：news_sentiment_window→overnight_boundary_reviser 的 plan004_input 预留字段无消费（待统筹裁定）。

## 施工与测试时序（今日）
A/B 类代码 13:4x-14:3x 落地+单测 → 14:05/15:05 盘中采样照跑（A2 首拍实测）→ 16:30 数据落地事件链自动跑 9 棒（B1/B2 钩子待调度器下次重启生效，今日由总扳手兜）→ 17:30 总扳手 full 圈终测（全 A 类段实测）→ 红蓝+提交。
