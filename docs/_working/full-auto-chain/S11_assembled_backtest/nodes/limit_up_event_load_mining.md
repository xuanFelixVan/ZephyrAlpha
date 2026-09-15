---
ttl: task_bound
title: T1-α 节点挖矿：打板/事件负载批产源（daban 四引擎 + 涨跌停/事件数据供给链）
session: st-qoder-t1a-20260915
date: 2026-09-15
parent: S11_assembled_backtest
---

# 挖矿节点 11：打板/事件负载批产源（T1A-1 的数据侧）

> 挖矿日期：2026-09-15 ｜ 会话：st-qoder-t1a-20260915 ｜ 唯源骨架：S11_assembled_backtest/nodes/
> 挖矿依据：decision_kernel_mining §5 子节点「打板/事件负载的日频批产源」；纵深延伸
> feature_pipeline_mining FPB-4（±9.5% 平阈值推导误判 20%/30% 板）与 FPB-1（399106 断更）
> 证据等级：数据结论全部经 ClickHouse 只读实证（ch_reader + TableRegistry 项目通道，
> ~19 个 SELECT-only 探针，零写库）；代码结论逐行核读，锚点 file:line

## 1. 头号发现 LUE-1（P0）：daban 四引擎日频负载零生产者——0.0945 权重的 sleeve 自出生即无输入

**证据锚点**：src/zephyr/pf_core/strategies/daban_sleeve_strategy.py:137-145（四键负载契约）；
src/zephyr/signal_ashare/screening/short_term_stock_selector.py:124-153（StockSelectionInput 17 字段）；
framework_plans.yaml fw-tdm-current（daban-sleeve 权重 0.0945）；decision_kernel_mining T1A-1。

**实证**：daban-sleeve 的 signals 契约要求每标的 `{"selector": {...}, "youzi": {...},
"quant": {...}, "fusion_context": {...}}` 四键 dict。全仓 grep（selector/youzi/quant/
fusion_context 组装器、daban 负载生产者、任务编排）证明：

| 负载键 | 契约字段（示例） | 日频批产器 |
|--------|------------------|------------|
| selector | StockSelectionInput 17 字段：连板高度/封单金额/开板次数/封板时间/催化强度… | **0** |
| youzi | YouziEmotionInput（游资情绪） | **0** |
| quant | QuantStrengthInput（量化强度） | **0** |
| fusion_context | FusionDecisionInput（连板数/主线/涨跌幅/风险分） | **0** |

StockSelectionInput 的 17 个字段里，`seal_time_minutes`/`catalyst_strength`/
`seal_order_amount` 等在现有日频表（kline_daily/stk_limit/limit_up_down）上**原理性不可产**——
封单代理唯一可信源是 miniqmt tick 尾盘买一档且 2026-07 起才可得
（daban_board_event_deriver.py:8 [INVARIANTS]）。与 decision_kernel_mining T1A-1 互为
镜像：策略侧证明该 sleeve 收恒量标量信号恒返回 `{}`（死成员），本节点补上数据侧根因——
**不是接线断了，是输入从未存在**。fw-tdm-current 给它配 0.0945 权重属名义配置。

**裁定建议**：批产器立项前置条件=先接通 LUE-3 的 daban_board_event 派生表；可产字段
（连板/开板/触价）从派生表映射，不可产字段显式置缺省并留痕（禁止拍默认值冒充）。
接线前建议 daban-sleeve 权重冻结或归零。

## 2. LUE-2（P0）：limit_up_down 表三重缺陷——无历史 + ~15% 非真封板行 + 周末幽灵分区

**证据锚点**：src/zephyr/data/config/tasks.yaml:1335-1345（incremental，intraday_realtime）、
tasks.yaml:2270-2279（full_refresh，"5年历史回补"）；c1_market.limit_up_down CH 实测。

**实证**（只读探针，2026-09-15 挖）：

| 维度 | 实测 |
|------|------|
| 历史覆盖 | 仅 2026-08-03→2026-09-15（42 日）；此前**零行**。full_refresh 登记的"5年历史回补"未履约 |
| 涨停行交叉验证 | 3248 行中：真封板（close==kline.close==limit_up）**2183（67.2%）**；炸板留痕 **257（7.9%）**——标涨停但 kline close 已落涨停价下方（中位破板深度 6.7%，最深 -9.2%）；两侧口径均不符 **228（7.0%）** |
| 周末幽灵行 | 5 对周末分区行数与前一交易日完全相等（63/63、54/54、82/82、39/39、40/40）——采集端无交易日守卫，把周五池复制进周六/周日分区 |

炸板行混入"涨停"口径会直接污染连板数/梯队高度/打板胜率统计（涨停日买入回测若信它，
实际收盘已破板）；周末幽灵行会让按 `trade_date` 取"最新分区"的下游读到假日期数据。

**裁定建议**：P0 三件套——①履约 5 年回补（源 akshare stock_zt_pool_em 支持历史按日拉取）；
②采集与派生两端加交易日历守卫；③表上派生 `is_sealed_at_close` 标记（close==limit_up 且
low<limit_up 区分炸板），炸板行移出涨停口径、单独成池。

## 3. LUE-3（P0）：daban_board_event / limit_up_pool 双零表——最 PIT 正确的批产件已建成未接线

**证据锚点**：src/zephyr/data/implementations/daban_board_event_deriver.py:8,35,46,67-72,769-783；
src/zephyr/data/config/tasks.yaml（grep limit_up_pool 无任务）。

**实证**：两张表均为 **0 行**，且均为"构建完成、测试齐全、零接线"：

| 表 | 设计完成度 | 断点 |
|----|-----------|------|
| c1_market.daban_board_event | 派生器自带 DDL（L46）；字段含 touched/is_one_word/open_board_count/seal_amount_proxy/consec_limit（L67-72）；规则口径经库内 stk_limit 重叠窗 **88445 样本 100% 验证**（L8）；CSV 中间层幂等（L769-783） | **全仓零 importer、tasks.yaml 零任务**——孤儿模块 |
| c1_market.limit_up_pool | DDL + 采集器 + 测试齐备（GAP-F-13） | tasks.yaml 无排程任务 |

讽刺的是：LUE-2 里 akshare 原始表的炸板/封单缺陷，恰恰是 daban_board_event 派生器
设计要治的病（触价判定 eps=0.001、逐行 limit_src 留痕、一字板显式判定）。批产链上
质量最高的环节被跳过了。

**裁定建议**：P0——按 deriver 自带 DDL 建表 + tasks.yaml 登记周末/盘后派生任务；
limit_up_pool 补排程。两者是 LUE-1 批产器与 FPB-4 修复的共同数据地基。

## 4. LUE-4（P1）：±9.5% 平阈值推导 fp=1099 全量化（fn=0）——stk_limit 真源坐实 FPB-4 修复路径；主板 ST 5%→10% 系真实规则变更非 bug

**证据锚点**：src/zephyr/data/implementations/akshare_provider.py:6600-6629；
c1_market.stk_limit / kline_daily CH 实测；feature_pipeline_mining FPB-4（姊妹发现）。

**实证**：

三口径同日对照（2026-09-15）：limit_up_down=51 ｜ 平阈值 close≥9.5%=43 ｜
精确 close≥stk_limit.limit_up=30-32——三口径互不相等，下游各信各的。

全窗混淆矩阵（2015-01-05→2026-09-15，平阈值 vs 精确 join）：**fp=1099，fn=0**：

| 板 | fp |
|----|----|
| 创业板（20%） | 505 |
| 科创板（20%） | 346 |
| 北交所（30%） | 129 |
| 沪主板 | 64 |
| 深主板 | 55 |

20%/30% 板合计 980/1099 = 89.2%，误判集中于非 10% 板（+9.5% 阈值对 20% 板既漏又误）。
stk_limit 本体全历史无断档（2015-01-05→2026-09-15，board/st_flag/limit_pct 列齐全），
**修复路径唯一且已被坐实：全部平阈值推导换 close≥stk_limit.limit_up 精确 join**。

**重要自纠（挖矿纪律留痕）**：挖矿中一度将 stk_limit 里主板 ST limit_pct 0.05→0.10 的
跳变疑为生成器 bug，逐行核读证实这是沪深交易所《交易规则（2026年修订）》
（2026-04-24 发布，**2026-07-06 施行**）的真实规则变更，`_MAIN_ST_10PCT_DATE`
（akshare_provider.py:6603-6605）按日期切片处理正确——**不立项**。真正的 P1 是下条
st_stock_list 源不稳。

## 5. LUE-5（P1）：st_stock_list 日度成员数 325↔206 逐日跳变——ST 链源不稳定

**证据锚点**：src/zephyr/data/config/tasks.yaml（st_stock_list_refresh，daily_capital 全量刷新）；
c1_market.st_stock_list CH 实测（2026-06~07 窗）。

**实证**：日度成员数在 ~206-214 与 ~325 之间隔日跳变。真实 ST 名单的日变动应为个位
（退市/摘帽节奏），百位级摆动指向源端口径漂移（全量拉取时偶发截断/去重失效），而非
市场事实。下游三处直接受害：回测 exclude_st、stk_limit 的 st_flag 推断（5%/10% 幅度
判定）、_load_st_snapshots 快照链（akshare_provider.py:6631-6634）。

**裁定建议**：P1——快照版本化留存 + 日变动阈值告警（单日 |Δ|>20 即可疑、拒绝落库），
回补时以"前值延续"兜底而非空集合。

## 6. LUE-6（P1）：STR-DABAN 注册表 23 条仅 3 条有 code_path——20 条设计空壳

**证据锚点**：docs/01_policies_and_standards/_registry/catalogs/strategy_registry.yaml（STR-DABAN 族）。

**实证**（行序解析）：STR-DABAN-001…023 共 23 条，code_path 已填 3 条：
020→src/zephyr/pf_core/orderbook_imbalance_strategy.py、022→c4_c72318f2da1c_bias_ql.py、
023→c4_fact_e831084c.py；其余 **20 条为 design-state 空壳**。空壳条目会被 intake/
激活累积流程当作可吸入对象（framework_plans 已见 STR-DABAN-023 进入 fw-tdm-current），
与 T1A-1 死成员问题同源：注册表把"愿景"计入了"产能"。

**裁定建议**：P1——批量清理空壳或限期（如 30 天）填 code_path，超期自动降级
design_draft 标记，禁止进入激活累积候选。

## 7. LUE-7（P2）：撮合侧无排队/一字板成交建模；tradability mask 孤儿

**证据锚点**：src/zephyr/backtest/core/matching_engine.py:177-182,185-190,196-208；
src/zephyr/backtest/implementations/vectorized_engine.py:195-260；
src/zephyr/ex_core/daban_pit_safety.py / daban_execution.py（CONSUMERS 注记）；
src/zephyr/factor/analysis/multifactor_tradability_mask.py。

**实证**：方向感知拒成（涨停买单拒成/跌停卖单拒成/清仓卖单跌停阻断）已落地并经
vectorized_engine 注入 StkLimitProvider 生效——但止步于"二值可成交"。打板语义里
真正的风险是**连续变量**：一字板（low≥limit_up−eps）日买盘排队几乎必不成交，回测侧
却按可成交价撮合；封单/排单位置、部分成交均无模型。ex_core 侧
daban_execution/daban_pit_safety 已实现排队位置成交概率、SaR、三段分笔，头部注记
"首批实盘接线前暂无"消费端——**实盘件建好了，回测没接**。另
multifactor_tradability_mask.build_tradability_mask（未停牌∧未涨停∧未跌停∧成交额阈值）
全仓零消费者，属孤儿件。

**裁定建议**：P2——回测撮合接 ex_core 成交概率模型（一字板=0 成交作下界）；
tradability mask 接线或明确退役，勿留双真源。

## 8. LUE-8（P2）：auto-mount self-heal NoneType 异常未解

**证据锚点**：docs/_working/pipeline-research/reports/intake-20260915-1859.md；
src/zephyr/strategy_pipeline/intake.py:351-353（self_heal 异常仅截断 160 字符入报告）。

**实证**：intake-20260915-1859 报告 mount error
`"'NoneType' object has no attribute 'close'"`，self_heal ops_n=0 未自愈；同报告幂等
skip 正常工作、写入门未破。指向 auto_mount 路径上资源句柄（连接/文件）关闭顺序问题。

**裁定建议**：P2——修 auto_mount 句柄生命周期（None 传播点加显式判空），self-heal
失败不应静默收敛为 ops_n=0。

## 9. LUE-9（P2）：事件负载燃料充沛但无日度 EventRecord 生产者、event_funnel 待接线

**证据锚点**：c1_market.news_data CH 实测（7,912,214 行，2010-01-02→2026-09-15 21:04）；
src/zephyr/intelligence/event_funnel.py（TYPE_CHECKING 导入，待接线）；
src/zephyr/pf_core/strategies/event_driven_sleeve_strategy.py（需 signals[symbol]["event"]
EventRecord 形 dict）。

**实证**：news_data 深度与活性俱佳（更新至挖矿日当日），但事件驱动 sleeve 所需的
EventRecord 负载与 daban 四引擎负载同样**零日频生产者**；event_funnel 漏斗件仅在
类型注解层被引用，未进任何编排。与 LUE-1 同构：燃料在库、灶台在库、无人开火。

**裁定建议**：P2——事件漏斗接线 + news→EventRecord 日度批产器立项（结构化抽取/
事件去重幂等键），与 daban 批产器同一批产框架下登记。

## 10. 正面清单

- **撮合方向感知拒成**：涨停买单拒成/跌停卖单拒成/清仓卖单跌停阻断三处齐全
  （matching_engine.py:177-182,185-190,196-208，2026-08-19 阶段2 红队修复落地），
  vectorized_engine 注入 StkLimitProvider 使限价真源生效——20%/30% 板不会误用 10%。
- **涨停价三级解析链真源健康**：stk_limit 全历史（2015-01-05→2026-09-15）无断档，
  FPB-4 修复可直接踩上去；kline 派生侧兜底链（stk_limit PIT 行→日期切片规则→板块
  前缀推断）逐级留痕。
- **主板 ST 5%→10% 规则变更处理正确**（akshare_provider.py:6603-6629）：日期切片 +
  docstring 引用交易所规则原文，PIT 纪律样板（本次挖矿实测排除一例假 P0）。
- **intake 写入路径双门 fail-closed**：KillSwitch（intake.py:268）+ 验收⑥ EVIDENCE
  文件门（intake.py:331-332）；重放幂等键=code_path（intake.py:288-291）；测试矩阵
  完备（test_intake.py:94 端到端重放幂等 / :178 code_path 幂等 / :121 EVIDENCE 门 /
  :108 KillSwitch 拦截）。
- **candidate_pool_aggregator 去重纪律**：完全重复 (symbol,sleeve) 对 fail-closed 抛错、
  跨 bundle 按优先级键去重、容量真源 10-20（candidate_pool_aggregator.py:15,89-90）。
- **factory_intake creation_token 集中登记**：auto_construct 经 batch_creation_tokens.py
  注册（factory_intake_pipeline.py:211），E2 预检 CH 不可达即 fail-closed。
- **涨停梯队双源并集自知降级**：limit_up_down ∪ stk_limit 触价收封（tol 0.005，
  sector_report_builder.py:49-50,197,440-466），单腿异常降级 unavailable 不炸整体。
- **daban_board_event_deriver 设计完备**：规则口径经 88445 样本 100% 验证、逐行
  limit_src 留痕、一字板/连板/开板次数/封单代理字段齐全、CSV 中间层幂等
  （daban_board_event_deriver.py:8,35,769-783）——只欠建表+排程（LUE-3）。
- **事件燃料活性**：news_data 792 万行、更新至挖矿日当日，批产器立项无数据障碍。
- **limit_up_down_incremental 通道设计合理**：akshare 涨停/跌停双池独立于 K 线通道，
  intraday_realtime 档位与全量回补任务分离（tasks.yaml:1335-1345）。

## 11. 修复优先级裁定建议

| 项 | 级别 | 动作 |
|----|------|------|
| LUE-3 双零表建表+排程 | P0 | daban_board_event 按 deriver 自带 DDL 建表 + tasks.yaml 派生任务；limit_up_pool 补排程（GAP-F-13 闭环）——LUE-1/LUE-4 的共同地基，建议最先做 |
| LUE-1 daban 四引擎批产器 | P0 | daban_board_event→StockSelectionInput 字段映射器；不可产字段显式缺省留痕；接线前 daban-sleeve 0.0945 权重冻结/归零 |
| LUE-2 limit_up_down 三重缺陷 | P0 | 履约 5 年回补；交易日历守卫杀周末幽灵；派生 is_sealed_at_close 区分炸板 |
| LUE-4 平阈值→stk_limit 精确 join | P1 | 与 FPB-4 同批修复；fp=1099/fn=0 实证背书 |
| LUE-5 st_stock_list 源稳定化 | P1 | 快照版本化 + 日变动阈值告警 + 前值延续兜底 |
| LUE-6 STR-DABAN 空壳清理 | P1 | 20 条限期填 code_path 或降级 design_draft |
| LUE-7 排队/一字板成交建模 | P2 | 回测接 ex_core 成交概率（一字板=0 成交下界）；tradability mask 接线或退役 |
| LUE-8 auto_mount self-heal 修复 | P2 | NoneType 句柄判空；self-heal 失败不得静默 |
| LUE-9 事件批产器立项 | P2 | news→EventRecord 日度批产 + event_funnel 接线，与 LUE-1 同框架 |
