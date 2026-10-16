---
ttl: task_bound
doc_type: tdm_mining_note
parent_skeleton: docs/_working/mine_fullchain_20261015/00_skeleton.md
skeleton_row: TDM-E-L3
flow: entry_flow
node_count: 25
session: mine-fullchain-tdm-20261015
---

# S_TDM-E-L3 个股选择（25 节点）

## 1. 定义

一句话：在强板块里挑好股（PT-03）——从全市场 5000+ 压缩到 10-20 只精选，子环节含 Universe 剔除/九阶段主链/双池评分/负面否决/顺位排序/环境开关/策略专属链/候选池输出/池分层/可交易性预检/日内动态选股/多维验证。

展开：漏斗主链=九阶段逐级压缩（每阶段砍 50-70%，3000→10 参照），双池（短线 1-3 日/波段 5-20 日）5 分制并行再合流过三维共振体检，负面否决器一票否决（暴雷/立案/减持/解禁/商誉/配股/高应计），最终候选池带 sleeve 标签与顺位分喂 L4。骨架总纲写 26 节点、地图实读 25（漂移记录于 §4）。本环节是策略挂载最密的一段：11 个节点带 strategy_mounts（打板/多因子/事件驱动 sleeve 链）。

## 2. 六向台账

### 2.1 输入面（有证）
- 入边（外部 0 条直入父节点，全经子节点）：L2→L3、L2-06-3→L3-02、L2-05-1→L3-06、L2-06-2→L3-07-1、L2-09-2→L3-04（利空子集喂负面否决）。
- 数据面：instrument_master.py（MOD-DATA-069）供 Universe；macro/财务/一致预期经 L9 源线挂点面（45 节点归数据链段）。

### 2.2 输出面（有证）
- 出边 27 条：L3→L4、L3-10→L4（可交易性预检前置）、L3-08→TDM-F-C3-01（候选池直喂归因引擎——决策→归因回流接线在册）。
- 策略挂载 11 节点：STR-VREV-001 挂 X-FLOW 族、打板/多因子/事件 sleeve 链（L3-07-1/2/3）各带 strategy_ref（STR 粒度真源=strategy_registry.yaml REG-STR-001）。

### 2.3 SSOT 真源（有证）
- config/trading_decision_map.yaml#TDM-E-L3（line 2022）至 L3-12-4（line 3026），25 节点行号连读。
- 算法登记 algo_refs 值域 23 个（DAL-8STATE-FCST/DAL-AUCTION-MICRO/DAL-CHANLUN/DAL-CHIP-DISTRIB/DAL-PULLBACK-ABC 等）→REG-DAL-001（decision_algo_registry.yaml 32 条，ROOR line 910）。
- 行业锚：position_recipe_grid_schema.yaml#industry_anchor（sws2021_l1，A1 行业中性化求值 MUST 用此锚禁硬编码行业清单）。
- casebooks 挂 16 处；考试卡 68 张（entry_flow/L3/ 实读）。

### 2.4 代码模块（有证，20/25 节点 ref 实存）
- 主链件：signal_fundamental/selection_funnel.py（MOD-SIG-086）、negative_veto.py（MOD-SIG-137）、selection_confidence.py（MOD-SIG-141）、router/signal_conflict_resolver.py（MOD-SIG-010）。
- 双池件：signal_ashare/fine_scoring_engine.py（MOD-SIG-048）、quant_short_term_strength_engine.py（MOD-SIG-034）；汇总件 candidate_pool_aggregator.py/pool_tier_maintenance.py（MOD-SIG-142/139）；预检 tradability_preflight.py（MOD-SIG-151，2026-09-16 三查专件落地）。
- 无 ref 节点 5 个均为结构枢纽：TDM-E-L3（父）/L3-03（双池评分聚合）/L3-07（策略专属链）/L3-11（日内动态选股）/L3-12（多维验证）——子节点全有锚，INV-1 允许。

### 2.5 门禁约束（有证）
- 四门同前；X_sector 维传导后处理（A1/A2 后、B Top-N 前=TDM 层级隔离位"只调分不重排名"）在 grid schema 有机读口径。
- L3-06 环境开关查表件 environment_switch.py 六段查表——ALGO-NOTE-SYNC 锚定其与地图节点同步。

### 2.6 自动化触发（有证）
- 盘后段（01/02/03/04/05/07/08/09/12 系）+盘前（06/10）+盘中（11 系竞价 9:26-9:28 与涨速扫描）分档在册。
- 宿主：daily_decision_orchestrator（pipeline_events 事件挂点）+dloop 链；竞价选股依赖图13-D13-11 竞价高频采集供料（骨架 §2.4 行）。

## 3. 自审闸三态

| 向 | 态 | 打分依据 |
|---|---|---|
| 输入面 | pass | 板块五路喂入+Universe 数据面在册 |
| 输出面 | pass | 候选池→L4 与→C3-01 归因回流双边在册 |
| SSOT | pass | 25 节点行+DAL 值域+行业锚+casebooks 16 处 |
| 代码模块 | pass | 20/25 实存；5 个 null 均结构枢纽（子全有锚） |
| 门禁约束 | pass | 四门+层级隔离位机读口径 |
| 自动化触发 | pass | 盘后/盘前/盘中三档+竞价供料链 |

**总评：pass（6/6，附漂移注记）**。

## 4. 缺口与建议

1. 骨架总纲写 L3=26 节点、地图实读 25——随 L2 同批骨架对齐。
2. 双池评分（L3-03）与策略专属链（L3-07）等 5 个聚合/枢纽节点无实现锚——"合流体检"与"策略间不共享中间结果"两纪律目前只活在 algo_note 散文，建议给 L3-03-3 signal_conflict_resolver 挂父级聚合锚或出专用合流件。
3. L3-05 顺位排序声明"妖股>龙头>中军>核心资产>趋势股>跟风"顺位表未单独成册（散文在 algo_note）——顺位是资金分配顺序的真输入（L4-04 消费），建议升格为 YAML 参数册进 RULE-SSOT 判向（规则数据=YAML）。
