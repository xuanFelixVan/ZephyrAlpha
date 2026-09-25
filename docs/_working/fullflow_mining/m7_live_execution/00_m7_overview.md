---
ttl: task_bound
lane: M7 实盘执行链
session: st-commitspeed-tbl-20260924
created: "2026-09-25"
status: mining_delivered
create_guard: 挖矿车道零 commit 零 enqueue；本目录 6 册 creation_token 由落地车道随批补办（同 M2 8 册先例）
---

# M7 车道作业簿 · 总览（实盘执行链七环节）

> 只读挖矿实证（零启终端/零下单/零撤单/零资金路径/零连真实账户；禁跑 test_ops_guard_red_team.py 全程遵守）。
> 挖掘窗口 2026-09-25；01-03 册为前任班产，04-06+本册为续作班补完。模板与判据真源=上级 `00_orchestration.md` §二/§三。
> M0 骨架空洞收编已由总筹批准；**绝对禁触真实交易**铁律贯穿六册。

## 一、分册清单与七环节映射

| 册 | 环节域（七环节） | 子环节/子模块数 | 三态 |
|---|---|---|---|
| 01_qmt_bridge.md | T10 实盘 QMT 桥（指令/HTTP/SDK 通道+柜台镜像+退役考古） | 12 | 挖干可施工（B4/B5 挂待裁/Owner 催办） |
| 02_kill_switch.md | T11 交易熔断面（五级+两套持久化+pre_execution 闸 1.5） | 11 | 挖干可施工（B1②/B2 待裁） |
| 03_position_sell.md | T6+T7 仓位与卖出（合册：仓位状态机+卖出融合仲裁计划） | 16 核心（38+28 件域） | 挖干可施工（B5 待实查） |
| 04_ex_core_ladder.md | ex_core 骨架+订单生命周期+打板族（ex_order 流转真身=order_manager，实勘无 ex_order 包） | 42（56 件剔除跨册 14） | 挖干可施工（B1 编排唯一化待裁） |
| 05_ex_sor.md | ex_sor 智能路由（**结论修正：真身存在 27 件 9,271 行+18 测试，生产装配缺位+包头注漂移**，非"设计态无实装"） | 19 实体件+8 空壳 | 挖干可施工（B2 接线时点/B4 跨域归并待裁） |
| 06_compliance_gates.md | 合规门+程序化交易报告（C-002 三门/C-004 三闸/报备报告面/操纵监测族） | 24（闸 12+报告 2+监测 5+配套底座） | 挖干可施工（B4 真源升迁待裁；B1 含 Owner 人工报送非纯工程可闭） |

三态汇总：挖干可施工 6 册 / 待挖 0 / 待裁 8 案（01-B4 实盘账号明文、01-B5 迁移台账催办、02-B1② 熔断态归并、02-B2 双五级互认、04-B1 执行编排唯一化、05-B2 SOR 接线时点、05-B4 sell router 归并、06-B4 43 号真源升迁）。

## 二、链路一张图（M7 视角，供 M0 骨架班交叉验证）

```
策略权重(pf_core sleeves, 含 daban_sleeve←ex_core.daban_load_producer 日批)
  → TradingSession.rebalance 事件链（risk_layer 评估→仓位 cap→delta 计算）
  → _validate_and_submit 四道闸：风控(02) → pre_execution 四级闸(02/S-1) → C-004 合规三闸(06,零注入) → 熔断(02)
  → OrderManager.submit_order：C-002 三门(06,零注入) → 状态机白名单 → broker
  → QmtFileBridgeBroker(01)：HTTP 快路径 fail-open 降级文件桥 → 柜台镜像回读
  → Fill：async_fill_dispatcher → tracker 入账(03) → execution_report_producer E4 → D_REPORTING
  → 拒单：classify_rejection(RETRY/ABANDON) → rejection_action_handler（Saga 六步补偿链在库零接线, 04-B1）
旁路：daban 打板族 8 件（signal/load/pit 回测半边闭环；execution/exit/熔断/监控执行半边挂 G22, 04-B3）
旁路：ex_sor 全族（路由/拆单/滑点/时段卖出——唯一桥 execution_engine 自身不可达, 05-B2）
安全底座：kill switch 五级(02) + SellSessionRouter 时段语义(05, design) + post_close 尾盘清退(04, 休眠)
```

## 三、车道级关键结论总账（Owner 第一读）

| 主题 | 结论 | 证据锚点 |
|---|---|---|
| 实盘就绪度 | **未就绪且距就绪有三类缺口**：①合规门全家族零注入（06-B1/B2，G5 前置）；②SimBridgeExecute 执行腿断（01-B1，P0 新证）；③买入腿零实弹+熔断重臂休眠+演练 0（03-B1/02-B1/02-B4） | 各分册 §四 |
| 合规现状定性 | 未报备未报送（6 项 broker_ack 全 false）+未实盘=当前无在险违规；但 1 万笔防线现役未激活（session 兜底 guard 只查不计数）、操纵冻结保护 0 | 06 册 §三/B2/B3 |
| 打板（daban）链 | 回测半边闭环（signal/pit/load→sleeve 权重）；执行半边（三段分笔/瞬时熔断/持续监控）码成待 G22 落线——当前 daban-sleeve 走普通 delta 下单，打板专用执行语义 0 | 04 册 §三/B3 |
| ex_sor 定性 | 真身在库（修正任务书预判），传递性生产不可达；头注"规划态占位"与 9,271 行真身矛盾=文档事故待修 | 05 册 B1/B2 |
| 退役/内收候选 | miniQMT 两件（券商 09-18 清退）、okx 链（研究域）、Stage2 预留四零消费者件（aggregate_root/repository/performance_monitor/param_optimizer）、Saga（若裁 session 直连为唯一） | 01 册 §五/04 册 B1/B4 |
| 历史保险 | 01-03 册已核：⑤熔断持久化半接线（save 通/rebuild 断）、③FIFO-LIFO 已落、⑥S-1 闸已接线；本班补核：sysid 回填已落、撤单终态保护已落（audit 移交③撤单不产 report 行待勘） | 01/02/03 册 §三 |

## 四、与邻车道边界（防重挖）

- commit 链=commit_speedup 战役；kill_switch 注册表限额面/运行时拦截器=M3；watchdog/计划任务常驻=M5（01 册实测引用不重挖）；AI 行为合规（trae_044/LSG/redline）=M3/M4；TDM 日级回撤=drawdown_state_machine 归 M2。
- 数据面（daban_engine_load 表 DDL/派生链）归 M1；pf_core sleeve 权重面归 M0 骨架已挖域，本车道只挖其执行消费侧。
- 13_trading_chain_audit.md=业务流审计正典，六册为其补代码级证据，冲突时以本车道 file:line 实测为准并回写。

## 五、复核命令（10 分钟总览）

```bash
ls docs/_working/fullflow_mining/m7_live_execution/                   # 6 册在盘
# 1) 逐册七节§三抽查（子模块清单两源交叉）
head -30 docs/_working/fullflow_mining/m7_live_execution/04_ex_core_ladder.md
# 2) 关键断言抽验（各册§七命令任选其二）
grep -c "broker_ack: false" docs/01_policies_and_standards/_registry/catalogs/compliance_report_registry.yaml   # =6（06 册）
grep -rn "OrderExecutionSaga(" src/zephyr scripts --include="*.py" | grep -v test                              # 零命中（04 册）
sed -n '13,16p' src/zephyr/ex_sor/__init__.py                                                                  # 头注矛盾原文（05 册）
grep -rn "bridge-execute" scripts/run_sim_bridge_execute_daily.ps1                                             # 断腿点（01 册 B1）
# 3) 红线复核：本车道零 commit
git log --oneline -3                                                                                           # 尾部无挖矿班提交即合规
```
