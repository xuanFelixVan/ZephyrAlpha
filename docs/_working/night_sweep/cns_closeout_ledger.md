---
created: 2026-09-29
ttl: task_bound
session: st-nightsweep-sw14-20260929
---

# CNS 消化度终账（夜战 2026-09-29 · SW14 收口）

> 判据真源：`docs/_working/decision_map_campaign_20260924/14_consumption_census.md` §五（CNS-01~14 处方）
> ＋ SW10 案卷 `SW10_cns_chart_wiring.md`（第一批）＋本车道实测。
> 普查口径：census 单一 scope（`zephyr.governance.consumption.scan_scope_converged`，
> src/+scripts/+config/ 代码面计客、文档只作证据）——2026-09-29 全九族重跑
> （`data/runtime/consumption_census_ledger.json`，schema consumption_census/2）。
> 纪律：退役候选只登记禁删（净删=Owner 门位）；禁虚报。

## 一、CNS-02 消费活性听证重判（机账 schema v3 口径）

基数对照（族①技术指标 143 条全覆盖）：

| 口径 | active | zero | retired | 备注 |
|---|---|---|---|---|
| 14 号文基数（机账 /2 旧账） | 24→26 | 114→117 | —（stale 退役） | 扫描根错位（parents[3]=docs/）+文档计客 |
| **本班重跑（机账 /3，SW14）** | **27** | **115** | **1** | 与 census 族①逐位一致（27/115/1） |

- **机账 schema v3**（CNS-14）：`consumer_files` 分列 `code_refs`（扫描面代码消费者，计客）
  ＋`doc_refs`（文档提及，只作证据位）——IND-REV-001 七文件假阳性机械治本；
  扫描根病根（`registry_path.parents[3]`=docs/）修正为 resolve 后仓库根。
- **CHIPS 5 条诚实重判**（CNS-02-CHIPS）：IND-CHIPS-001~005 入册已在（st-zcloseout 批
  交叉验证），但旧账 CHIPS-001/002 的 "active" 系**文档提及假阳性**（consumer_files 全为
  _working/*.md）——v3 重判**五条全 zero（零代码消费）**，doc_mentions 留证据位。
  处置结论：`retire_candidate(零消费)` 登记待指标域核实，**禁删**；转绿路径=D21 获利盘
  消费接线（裁定#257④ 解挂后重跑幂等审计）。
- IND-REV-001：retired（裁定#233 在册）＋doc_refs 12 处证据位——假阳性样本口径闭环。

## 二、CNS 全 14 条消化对账（第一批 SW10 + 第二批 SW14）

| # | 处方 | 状态 | 证据/去向 |
|---|------|------|----------|
| CNS-01 | indicator_reader 接入 multifactor_synthesis | **BLOCKED**（在盘残袋） | TIF 包残缺（reader 通道缺）——SW10 §六；IC 取证件已建（eval_tech_indicator_ic.py 在 sw10 重放袋） |
| CNS-02 | 机账听证+CHIPS 补入 | **DONE-LANED**（本班收口） | 入册交叉验证（st-zcloseout）＋v3 诚实重判（§一）；zero=115 带处置结论（recommendation 字段逐条） |
| CNS-03 | block_trade_detail 消费方或退役 | **ADVANCED** | census ③族 alt_data_table active 15/zero 4；建消费方=新信号线（工量大）、退役=Owner 门位——双路均超本班权限，登记续派 |
| CNS-04 | 宏观族总裁决 | **OWNER-GATE** | census ⑤族 macro active 11/**zero 15**（即 MAC 族听证对象面）；cn_macro 重跑维持 zero（11 处文档提及不计客）——SW10 §二退役候选登记维持，净删待 Owner |
| CNS-05 | 基本面 ZERO 10 表标记 | **OWNER-GATE**（待令） | census ⑧族 fundamental_table zero=**10**（与处方数字吻合）；potential_consumers 增枝机制=ulib3b 提案 Owner 未批（CNS-14 后半同源）——待令后机械可打标 |
| CNS-06 | hk_kline/kline_hq_daily 归一裁定 | **ADVANCED** | 裁定项需 ruling_registry 通道（裁定#NNN 登记=Owner 门位前置），本班不代裁；census ③族台账佐证面已备 |
| CNS-07 | 情绪成分治理（C4/C6/C1 触发器） | **ADVANCED** | census ④族 emotion active 1/zero 5；C1 自动重考触发器与 SW4 考试判据车道同域（避让不代投），C4/C6=模型参数二评归 Wave 2 |
| CNS-08 | strategy alpha_sources 回填（17 空） | **DONE-LANED**（SW10） | 7 回填/10 无据留空（SW10 §三 known-gap）；values 在 sw10 重放袋（strategy_registry blob） |
| CNS-09 | factor belongs_to_strategies 0%→≥18% | **DONE-LANED**（SW10） | 32/175=18.29%；values 在 sw10 重放袋（factor_registry blob） |
| CNS-10 | ipo/index_adjustment 消费方 | **ADVANCED** | census ⑨族 calendar active 13/zero 8；上市天数过滤（BM-SEL-16）入 universe 链=明确处方，工量中——续派首批 |
| CNS-11 | auction_book 竞价强度因子接线 | **DONE-LANED**（本班） | 查询装配件 `src/zephyr/factor/auction_strength.py`（装配/查询路径，打分委托 youzi 引擎真源禁造新指标）＋IC 取证件 `scripts/backtest/eval_auction_strength_ic.py`（三件套齐：token/翻译/depgraph 15387770/15387771）；实弹 IC 证据：窗 2026-07-21→09-26，25 日中 15 有效日（≥30 截面），120,549 行打分/81,015 行有效，**IC=-0.0219 / ICIR=-0.266 / t=-1.03（5% 水平不显著）**——证据=docs/_working/night_sweep/sw14_auction_ic_evidence/（daily_ic.csv+summary.json 可复核）；factor_registry 注册条目（FCT-INTRADAY-025，alias BM-SEL-23-A-5，evidence 指 IC 证据位，status 维持 candidate 不晋级——短窗如实）编辑已备，随 B2 批落地（受 sw10-0002 袋 factor_registry blob 序约束，防快照回卷）；daban 决策链 T 日竞价喂入=声明接线点（策略侧盘中通道，非 T-1 负载批产字段，见模块头 CONSUMERS） |
| CNS-12 | 北向因子立项 | **ADVANCED** | 形状同 CNS-11（FCT+IC），但北向数据通道（DS-103 消费面）需先验证供数活性——续派 |
| CNS-13 | ashare_*/barra/data_eng 死亡证明批量评审 | **OWNER-GATE** | census ⑩族 table_residual zero=**61**（补集面全量在案）；批量退役=注册表净删=Owner 门位；zero_ref 清单即证据 |
| CNS-14 | 机账口径升级 schema v2 | **DONE-LANED**（本班） | v3 分列 code_refs/doc_refs（§一）；potential_consumers 增枝（ulib3b）=OWNER 未批维持待令 |

## 三、全族消化度快照（census 2026-09-29 重跑）

grand：**active 287 / zero 473 / retired 5**（765 实体）

| 族 | active | zero | retired | 对应 CNS |
|---|---|---|---|---|
| ① indicator | 27 | 115 | 1 | CNS-01/02/14 |
| ② candle_pattern | 0 | 0 | 2 | （裁定#233 退役面） |
| ③ alt_data_table | 15 | 4 | 0 | CNS-03/06/12 |
| ④ emotion_component | 1 | 5 | 0 | CNS-07 |
| ⑤ macro | 11 | 15 | 0 | CNS-04 |
| ⑥ factor | 48 | 126 | 1 | CNS-09/11/12 |
| ⑦ strategy | 31 | 129 | 1 | CNS-08 |
| ⑧ fundamental_table | 19 | 10 | 0 | CNS-05 |
| ⑨ calendar | 13 | 8 | 0 | CNS-10 |
| ⑩ table_residual | 122 | 61 | 0 | CNS-13 |

## 四、三数终账（最终回复口径）

- **已接线**：CNS-02、CNS-08、CNS-09、CNS-11、CNS-14 = **5 条**（＋SW10 的取证面 CNS-01-ICEVAL/G-A.3 图形面 2 件）；
- **登记让路/续派**：CNS-03/06/07/10/12 = **5 条**（处方明确、工量或权限超窗）；
- **无消费方退役候选（只登记禁删）**：CN-MACRO（SW10 §二维持）＋CHIPS 5 条＋族① zero 115＋
  族⑩ residual 61＋族⑤ macro zero 15 等——以 census 台账 recommendation 字段为准（禁物理删，
  净删=Owner 门位）。

## 五、口径变更披露（必读）

1. 机账 /2→/3：active 口径从"任意文件提及（含 docs/）"收紧为"census 扫描面代码消费"——
   24→26→**27** 的 active 数与 114→117→**115** 的 zero 数系**口径修正非漂移**；
   对照假阳性病根=旧实现扫描根错位（parents[3]=docs/）＋文档计客（IND-REV-001 同案）。
2. census 本体缺陷（本班发现，另案不代修）：`_scan_root_of` 默认 repo_root 推导差一级
   （`Path(__file__).parents[4]` 实取 src/）——生产默认参调用即抛"族登记册缺失"；
   本班薄壳/终账全显式传根绕开。修复归 census 属主车道。
3. 普查台账：`data/runtime/consumption_census_ledger.json`（本班全九族重跑产物）＋
   `data/runtime/indicator_usage_ledger.json`（机账 v3）——均 runtime 区，机生可重放。
