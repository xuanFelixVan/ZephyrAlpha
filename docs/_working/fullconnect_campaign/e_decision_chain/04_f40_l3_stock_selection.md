---
ttl: task_bound
title: F40 L3 个股选择——全流通挖干案卷（矿道 L05）
session: zc-l05-20260927
creation_token: fc-f40-l3-stock-20260927
---

# F40 L3 个股选择——挖干案卷

> 一句话：全市场 5000+ 压缩到 10-20 只——Universe 剔除→九阶段主链→双池评分→负面否决→顺位→环境开关→策略专属链→候选池→分层维护→可交易预检→日内双通道→四维验证。节点组=TDM-E-L3+01..12 共 25 节点（今日 yaml:1394-2143 机数=25，与册一致）。总册 built｜P1｜T4；上游 F39，下游 F41。

## 一、六向台账（实证锚点）

| 向 | 内容（锚点） |
|---|---|
| ①上游输入 | F39 板块调节分+龙头定位（只两字段）；DS-150/082/181；L1 六段（L3-06 查表轴） |
| ②数据原料 | technical_indicator 3.5 亿行/stock_daily_basic 7.1M/dragon_tiger_seat 4.5 年/money_flow 六年/limit_up_pool（L04 SKEL W2-W5 册引）；daban_engine_load PIT 真读（max(trade_date)<T 最近事件日分区，2026-09-16 E2 接线，册引） |
| ③状态输出 | 最终候选池 10-20 只（否决只标记不剔除/去重确定序/三来源注入零 IO 37 单测，册引）+双池 5 分制+顺位分+Tier 归属——**纯内存/回测内存话无持久化**（M-41/D22） |
| ④下游消费 | F41 L4（带 sleeve 标签）；L3-09 持久池喂次日；L3-11-2 观察池喂盘中；现唯一实际消费面=回测 framework_composer（L04 SKEL §1 audit:102 册引） |
| ⑤自动化触发 | 盘后链经 dloop_post+sector_state 面板供数；盘前 L3-06/L3-10 开盘前收口；盘中 L3-11 竞价 9:26-9:28+涨速 9:30-10:30（册引）；**tasks.yaml 仅数据任务无决策日循环触发面（LK-04 本体缺位）**（L04 SKEL W2⑤） |
| ⑥缺口债 | L3-05 六顺位判据-码面差异；L3-12-3 筹码维 trial 挂起（裁定#257④）；L3-09 池成员持久化无 SSOT（M-41）；L3-08 depgraph 登记欠账；25 件验证全 untested |

## 二、子模块三级枚举（2026-09-27 实扫）

- 域 `src/zephyr/signal_fundamental/`：36 件 .py（实扫）。核心：selection_funnel.py（九阶段，MOD-SIG-086）、negative_veto.py（七清单含 high_accrual 裁定#231，MOD-SIG-137）、selection_confidence.py（MOD-SIG-141，event/daban/multifactor 三类置信分）。
- 域 `src/zephyr/signal_ashare/`（155 件）：fine_scoring_engine.py（MOD-SIG-048）、quant_short_term_strength_engine.py（MOD-SIG-034）、router/signal_conflict_resolver.py（MOD-SIG-010）、core/candidate_pool_aggregator.py（430 行纯函数核）、core/pool_tier_maintenance.py（MOD-SIG-139）、core/environment_switch.py（MOD-SIG-138，:40 六段×四开关 _SWITCH_TABLE）、tradability_preflight.py（MOD-SIG-151 五查，:55 BlockedReason）、screening/tiered_screening_filter.py（MOD-SIG-046）、mainline_candidates.py。
- sleeve 策略件：pf_core/strategies/{daban,multifactor,event_driven}_sleeve_strategy.py（册引）。
- 22 个 module_ref 全在盘零缺件（册引）；L3-05/L3-07 容器 module_ref=null（structural 正常）。

## 三、接线四态独立复核（2026-09-27）

| 件 | 四态判定 | 独立证据 |
|---|---|---|
| 选股主链互调 | **域内接线（回测面）** | selection_funnel 4/fine_scoring 6 消费方（audit:102，L04 SKEL 册引）；生产日循环零挂点 |
| environment_switch | **半接线（最近生产挂点）** | strategy_pipeline/daily_gate_snapshot.py:166 已采集六段×四开关"只采不断言"（L04 SKEL W2⑤；今日 grep absent 契约实锚同文件） |
| tradability_preflight | **纯库挂机** | 调用方=0（audit:18，L04 SKEL W5④ 双源） |
| daban_engine_load | **生产接线** | tasks.yaml:3422 盘后日批→internal_compute_provider→daban_load_producer（仓内唯一持久化先例） |
| 策略挂载 | **proposed 为主** | 8 sleeve 引用 6 个 confidence=proposed evidence=None，仅 STR-TSMALL/VAL verified（册引 f40 册 §六） |

**骨架勘误（登记待 D 线）**：
1. **L04 板块→个股传导缺口（同 F39 卷勘误 3，跨卷登记）**：F39 产出两字段到 F40 消费两字段之间的落库载体与生产触发面双缺（M-41+LK-04+G05 未激活三叠加）；处置=L04 SKEL C01/C02/C08 三工单，本卷登记联责。
2. f40 册 §一"TDM-E-L3 共 25 节点"与今日机数一致，无勘误；但总册 F40 行"signal_fundamental/selection_funnel.py、negative_veto.py 等"路径口径与 L3-02/03-04 挂载一致今日未逐点复核（维持册引）。

## 四、缺口清单（处置+优先级）

| # | 缺口 | 处置 | 级 |
|---|---|---|---|
| G40-1 | 候选池持久化载体缺（M-41/D22） | L04-C01 建表族 c1_market.stock_candidate_pool（DDL 对齐 sector_state 草案，RULE-SCHEMA-TZ 合规） | **P0** |
| G40-2 | L3 生产日循环挂点缺（LK-04） | L04-C02 盘后 internal 批串接+tradability_preflight 挂 premarket_workflow，复用 daban_engine_load_daily 模式零新调度器 | **P0** |
| G40-3 | G05 选股引擎 admission_gate 未激活（同 F39 堵点 3） | G05 施工批或临时由 candidate_pool_aggregator 承载+图注声明 | P1 |
| G40-4 | L3-05 六顺位判据-码面差异 | a) 码面补顺位分级（1 天，成本低优先）或 b) S4 改判据 | P1 |
| G40-5 | L3-12-3 筹码维 trial 挂起 | 流通股本数据工程立卡（M1 交界）或 S4 改四指标语义；解除须重跑回测（裁定#257④） | P2 |
| G40-6 | 25 件验证全 untested | sensor_monotonicity+exit_counterfactual 批量冻结 | P1 |
| G40-7 | L3-09 分层状态机"昨日 Tier"无落库 | 随 G40-1 同批（Tier 变更流入表族） | P1 |
| G40-8 | L3-08 depgraph 登记欠账 | generate/登记 MOD id，0.5 小时 | P2 |

## 五、自审闸三态

**挖干可施工**（实件零缺；两处判据-码面差异+两处登记欠账已列修法；两个 P0 均有现成工单真源引用不重立）。

### 待裁
- L3-05/L3-12-3 处置路径 a/b——D 裁定场景。
- G05 施工批归属（PR/工程交界）——待排期裁定。

## 六、复跑命令

```bash
sed -n '40,90p' src/zephyr/signal_ashare/core/environment_switch.py   # 六段×四开关
sed -n '55,130p' src/zephyr/signal_ashare/tradability_preflight.py    # 五查
grep -c "node_id: TDM-E-L3" config/trading_decision_map.yaml          # =25
grep -rln "tradability_preflight" src/zephyr --include="*.py" | grep -v __pycache__  # 调用方清点
grep -rn "daban_engine_load_daily" src/zephyr/data/config/tasks.yaml  # :3422 先例
```
