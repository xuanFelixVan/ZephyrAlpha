---
ttl: task_bound
completes_when: 战役收尾（99_final_delivery 落账）后随役归档 archive/2026-10
---

# [BLUEPRINT] | docs/_working/chief_fullchain_20261006/env_mining/env_09_sector_select.md |
<!-- [MODULE]  -->
<!-- [STABILITY] evolving -->
<!-- [SAFETY] L -->

# ENV-09 板块选择 挖矿作业簿（B1 批次，2026-10-06）

## §0 环节档案

- **真源锚**：config/trading_decision_map.yaml nodes[layer=L2]（30）；骨架=01_skeleton_environments.md §2-丙
- **职责一句话**：从大盘状态到个股候选之间的板块层中枢——强度综合/轮动追踪/水温放行/传导门槛/催化剂五路，决定"钱往哪堆板块走、放行多少信号"
- **节点代表（30，代表非穷举）**：L2 板块选择(structural)｜L2-01 板块强度综合｜L2-01-1 结构强度｜L2-01-2 动量排名｜L2-01-5 市场级调节注入｜L2-02-1 RRG 轮动序列｜L2-04 板块级市场状态｜L2-04-2 虹吸态识别｜L2-05 水温响应(pending_gate)｜L2-06 板块个股传导｜L2-06-1 三级放行门槛｜L2-06-2 龙头识别定位｜L2-08 板块生命周期｜L2-09 催化剂识别+事件图谱传导｜L2-10 同源补涨比价｜TDM-C-L2 赛道选择(not_built)
- **图面状态**：confidence proposed=25 / untested=5；activation postmarket17 为主（premarket5/intraday5/continuous3）；red_reason：L2/L2-01/L2-04 structural、L2-05 pending_gate、C-L2 not_built

## §1 六向台账

| 向 | 内部反查发现（带路径证据） | 外部 | 判定 |
|---|---|---|---|
| ①上游 | 图内 IN 12 边：L1-AGG/L1-S5→L2-05-1 水温档（总闸直喂）、L1→L2、L0-04→L2-06-1、L9-G1→L2-06、L9-V2→L2-05、L9-V3→L2-01、L1-S0-1→L2-09-1 事件图谱、F-C3-05 可靠度回喂 | RRG 轮动/生命周期为业界通用框架；水温档 S0-S4 放行比例为仓内自创口径 | signal |
| ②下游 | 图内 OUT 11 边：L2-06-3→L3 主链/L3-02 九阶段、L2-05-1→L3-06 环境开关、L2-06-2→L3-07-1 打板链、L2-09-2→L3-04 负面否决+L0-02 回喂、L2-03-1/L2-07-1→L4。grep 消费方：src/zephyr/signal_ashare/strategy_signal/signal_factory.py、screening/tiered_screening_filter.py、screening/selection_funnel_skeleton.py、strategy_pipeline/daily_gate_snapshot.py、signal_ashare/core/daily_condition_sensor.py | — | signal |
| ③算法机制 | 强度综合五子件（signal_ashare/core/sector_strength_aggregator.py+sector/ 下 analyzer/momentum/breadth/ranking_engine）；RRG（sector/sector_rrg.py）；轮动五分类+虹吸（sector_rotation_state.py/sector_siphon.py）；水温→放行比例（sentiment/sentiment_cycle.py+sector_gate.py 三件套）；传导三级门槛+龙头（sector_conduction.py/sector_leader.py）；回踩 ABC（sector_pullback.py）；催化剂事件链（screening/event_driven_screener.py+intelligence/news_chain_node_linker.py+chain_impact_resolver.py） | — | signal |
| ④后端代码 | 23 个去重 module_ref 全在盘（覆盖 24/30 节点，sector_analyzer/sector_conduction 一件多节点共用）；无码=族头 L2/L2-05/C-L2 等三处。**日循环实接线**：sector_pre_open/intraday_sector/sector_close_final 三槽挂 src/zephyr/data/sector_state_pipeline.py:164 与 signal_ashare/sector/sector_state_aggregator.py:497（config/trading_day_cycle_map.yaml:833/876/1917——他队图 13 只读借力）。tests/：tests/data/data/test_sector_state_pipeline.py；signal_ashare/sector/* 无专项单测目录（已查无） | — | 半实现 |
| ⑤前端呈现（只登记） | dashboard/web/features/tdm.js 图面板块节点；warroom.py 水温/状态读出 | — | signal（登记） |
| ⑥数据字段 | data_refs=DS-170/059/181/186/150/224/082/107/225（板块行情/板块资金流/概念族）；催化剂链吃 news_data+事件图谱 | — | signal |

## §2 挖干自评

- **三扫收敛?** 收敛。消费方轮发现日循环三槽实接是本轮最大增量（图 TDM 未画此接线，属图 13 域），此后归零。
- **未挖长尾**：(a) sector 23 个模块逐件单测覆盖矩阵（本批只证到目录级已查无）；(b) L2-09 催化剂链三件（screener/linker/resolver）的端到端联调证据；(c) L2-10 同源补涨与 supply_chain_momentum 的数据依赖表。
- **🌑不可得**：①水温档 S0-S4 的历史回放台账（sentiment_cycle 无留痕面证据）；②L2-05 pending_gate 等的具体闸门 id（图面只留记号，闸册归属待验证）。

## §3 挖后自审闸三态裁定

**挂起排期（整层）——图语义→代码施工令缺口（实现厚但激活薄）**

- 理由：23/30 有码是全图实现密度较高的语义层，但 confidence 全 proposed/untested、零 verified；真正进入日循环的只有 data 域 sector_state_pipeline 三槽（盘前/盘中/盘后），TDM 画的传导/水温/回踩/生命周期主干与该管线的关系未在代码闭合——L2-05 水温显式 pending_gate 等 ENV-08 状态激活。语义→施工令缺口成立，不硬施工。
- 施工令候选排序（解锁后）：水温放行比例接线（sector_gate×sentiment_cycle×L1-AGG）> 三级放行门槛与 L3-06 环境开关闭合 > 催化剂端到端联调。
- 解锁条件：ENV-08 state_matrix 激活（水温的上游语义就位）+ Owner 对板块层发施工令 + sector 专项单测补齐作为施工伴生义务。
- C-L2 币圈赛道=not_built 外域封存，本簿不收。

## §4 挖矿日志

| 轮 | 矿脉 | 判定 | 关键产出 |
|---|---|---|---|
| 1 | 图字段轮：30 节点 conf/act/red_reason 切片+五路机制分族 | signal | structural4/pending_gate1/not_built1 分型；postmarket 为主的激活面 |
| 2 | 代码轮：23 module_ref 存在性+sector 家族清单 | signal | 零失踪；已查无 sector 专项单测目录 |
| 3 | 接线轮：trading_day_cycle_map 反查 sector 挂槽 | signal | 三槽实接 sector_state_pipeline:164/sector_state_aggregator:497——TDM 与图 13 的跨图接线证据 |
