---
ttl: permanent
doc_type: policy
rule_form: standard
verifiability: manual
title: 研报/一致预期数据消费端设计 v1.0 与数据缺口档案（§8 预注册/§9 源快照语义定性）
---

# 研报/一致预期数据消费端设计（v1.0，2026-09-12）

> Owner 发起：先想清楚"这数据拿来干什么"，全网调研机构/社区/学术/开源，再出施工方案。
> 数据前提（已就绪）：`c3_fundamental.research_report`（146,633 行/4,695 只/2017-01 起，每行=一份研报：机构/东财评级/行业/publish_date/预测期 0-2 EPS+PE/PDF 直链，report_id=infoCode）+ `analyst_forecast`（官方一致预期快照 2026-07 起累积）+ `earnings_forecast`/`express_report`（业绩预告/快报 1998 起）。
> 项目侧咬合点已经探索代理逐行核实（证据=路径:行号，见 §4）。

---

## 1. 第一性原理：这批数据的本质

研报数据 = **"卖方分析师脑子里的预期"的时空记录**。它回答的不是"公司怎么样"（那是财报的事），而是"**市场认为公司会怎么样、这个认识正在怎么变**"。全部消费价值落在三条不变量 + 一条市场结构变量上：

| # | 不变量 | 数据投影 | 经典文献 |
|---|--------|---------|---------|
| ① | **预期动量**（预期自身怎么变） | 同股相邻研报 EPS 预测差（方向/幅度/上调占比） | Gleason & Lee 2003：修正后股价漂移，高创新性修正漂移更强 |
| ② | **预期差**（实际 vs 预期） | 业绩预告/快报实际值 vs 事前一致预期 | PEAD（Ball-Brown 1968）；华泰"预期调升"策略年化 22-27% |
| ③ | **预期分歧**（认知不均匀度） | 窗口内多机构预测标准差/极差 | Diether et al. 2002：高分歧→未来收益偏低 |
| ④ | **关注度**（谁在看、多少人看） | 研报数/机构数的异常变化 | Lee & So 2017：异常覆盖度预测收益 |
| ⑤ | **认知内容**（他们说了什么） | 研报文本（Phase 2，body 列已预留） | Lv 2025 AFA：LLM 文本 alpha 增量 R² 3%→10%+ |

**一句话**：这批数据给项目补上了基本面的"预期侧"——财报是滞后的锚，预期是领先的锚，**预期差是两锚之间的桥**。

## 2. 全网调研结论

### 2.1 机构实践（华泰金工系列 = A 股最完整公开方法论，公式可直接抄）

| 来源 | 框架 | 实证 | 我们可行性 |
|------|------|------|-----------|
| 华泰单因子测试之九（2018，19 因子） | 一致预期 EP/BP/EPS/ROE/净利润 + 同行业位序 + 季度环比 | 一致预期 EP 沪深300 RankIC 6.32%，长期稳定 | ✅ 全可造 |
| 华泰 AI 系列 54（遗传规划挖一致预期因子） | Alpha1~11 表达式公开；**变化率 ts_return 是最高频构件**；复合=预期×真实基本面（Alpha11=预期EP×EP 即超预期）；**除以预测标准差是标准改进法** | Alpha1-4（盈利变化族）相关 0.76-0.92 → 一族留 1-2 代表即可 | ✅ 公式直译 |
| 华泰基本面量化之二（2024-12，三因子合成） | **异常覆盖**（研报/作者/机构数对市值动量换手回归取残差，RankIC 2.34%）；**改进评级**（7/5/3/2/1/0 评分，2.26%）；**盈利修正**（修正幅度+上调占比，高创新性修正+剔除动量改进，3.99%，TOP 年化超额 9.55%）；合成 4.27%/10.55%，与 AI 量价相关性仅 0.03 | 2011-2024 月频 | ✅ 作者数缺→报告数+机构数双代理；"分析师技能筛选"需姓名维度（V2） |
| 华泰策略《预期调升》 | 业绩预告披露前后 10 天一致预期变化>0=超预期，行业+个股 | 年化 22-27% | ✅ 预告数据 1998 起 + consensus 时序 2017 起，完全支持 |

### 2.2 学术与最新算法（2024-2026）

- **Lv (2025, AFA)《Do Sell-side Analyst Reports Have Investment Value?》**：120 万份研报，LLM embedding+ML 预测 12 个月收益，增量 R² 从情绪词袋 3%→10%+；Shapley 归因：**前瞻性战略判断贡献最大**——Phase 2 文本管线路线图。
- **国内《让情绪"有结构"》（DeepSeek 研报摘要结构化情感）**：摘要按业务/战略/技术/财务/股东/政策六类拆解，四维量化（类别/倾向/顺序/篇幅）；"业绩超预期密度""盈利改善密度"最有效；综合因子年化超额 13.5%——LLM 选型可直接复制（DeepSeek）。
- 韩国卖方研报 LLM 对比（6 模型）：领域微调模型多空组合优于通用 GPT-4o——微调方向确认。

### 2.3 开源项目（借鉴模式，不整体引入）

| 项目 | 借鉴 | 不引入原因 |
|------|------|-----------|
| microsoft/qlib（44k★） | RD-Agent 循环（LLM 提因子假设→回测验证→迭代）= SOP-B 自动化方向 | 数据格式/回测语义不匹配自有栈 |
| FinGPT（20k★） | Phase 2 文本微调基座备选（LoRA <$300） | C4 再评估，先 DeepSeek API 起步更省 |
| TradingAgents（85k★） | 多 Agent 协作模式印证 intelligence 三 Agent 设计 | 模式已内化 |

**结论：没有现成 A 股一致预期因子开源库可搬——华泰公开公式 + 我们独有明细数据 = 自建，这正是价值所在。**

## 3. 模块设计（五个消费模块）

### M1 派生层 `consensus_daily`（一切消费的地基，可立即动工）

- **粒度**：(symbol, trade_date, horizon)，horizon∈{fy1, fy2}
- **字段**：eps_consensus（窗口均值）、eps_median、eps_std（分歧度）、eps_min/max、n_reports、n_orgs、rating_score_mean（买入7/增持5/中性3/减持2/卖出1 映射）、n_buy/n_add/n_neutral、last_report_date；窗宽 90 天可配
- **PIT 铁律**：只聚合 publish_date ≤ trade_date 的研报（publish_date 即可得=零 embargo）；无覆盖=NULL 不前向填充
- **实现**：夜间批（research_nightly 之后），DDL-as-Code 照 research_report 先例，ReplacingMergeTree
- **为什么必须有**：研报明细是事件流，因子回测要"每股每日矩阵"——华泰全部公式以此为输入

### M2 因子族（首批 6 个，逐个走 SOP-B）

| 因子 | 构造 | 依据 |
|------|------|------|
| EXP-01 一致预期 EP | eps_consensus_fy1 / price | 华泰 RankIC 6.32% |
| EXP-02 修正动量 | Δeps_consensus(1m/3m) ÷ eps_std | 华泰 AI54：ts_return 最高频构件；Gleason-Lee |
| EXP-03 修正广度 | 窗口内上调研报占比（fy1/fy2 双期） | 华泰初探 |
| EXP-04 异常覆盖 | n_reports/n_orgs 对市值+动量+换手回归取残差 | Lee-So 2017；华泰 2.34% |
| EXP-05 分歧度 | eps_std / \|eps_mean\| | Diether 2002（负向）；兼作 EXP-02 分母 |
| EXP-06 评级动量 | rating_score_mean 3m 变化 + 上调事件计数 | 华泰 7/5/3/2/1/0 评分制 |

### M3 超预期事件族（契约坑已挖好，填实体即可）★

探索代理实锤：`event_factor_matrix.py` 里 **EarningsFactorData（L288-312）已预留 consensus_eps/surprise_std/ear + consensus_before/consensus_after/open_next/close_event（has_triple）字段，`expectation_gap_with_revision_momentum`（L393-410）函数已存在，compute_event_score 降级链 triple→dual→single 已通**。施工=①EventRecord.class_ 加"财报超预期"枚举 ②EVENT_CLASS_WEIGHT/DECAY_EXIT_WINDOW 加权重与衰减窗 ③consensus_before/after 由 M1（深度）或 analyst_forecast 跨快照 diff（实时）供给 ④MarketEventStore.query 协议落存储。判定规则照华泰：预告/快报实际值 vs 事前 90 天 consensus（n=10 交易日窗口），次优信号=预告后 consensus 修正方向。

### M4 文本管线（Phase 2，建议等数值链路跑通）

PDF 下载（body 列已预留）→ PyMuPDF 解析 → LLM 结构化提取（DeepSeek 六类框架：业务/战略/技术/财务/股东/政策 × 倾向/篇幅/顺序）→ score_report_llm 因子。模型走 intelligence 域现成 local_llm_pool/api_llm_pool。

### M5 信号层挂接（SOP-C C5 解冻后激活）

- `signal_fundamental` 新增**预期下修否决**：照 negative_veto 模式（L46-111）——新建 expectation_facts frozen dataclass（consensus_revision_down_30d 比例、eps_below_consensus 等布尔/比值）+ 纯函数裁决器 + 注册进 selection_funnel；证据不足不否决
- `llm_fundamental_analysis` 的 FundamentalInputBundle（L72-81）：研报预期拼入 financial_report 文本槽或折进 quantitative_score（融合权重 0.6/0.4）

## 4. 与现有体系的咬合（探索代理逐行核实）

1. **SOP-B 七步**（sop_b_node_loop.md:30-100）：本设计 §2 调研=第①步"全网算法调研≥3候选"的产物；C2 每因子走 ④宽回测→⑤噪音剪枝→⑥窄回测（factor 对象映射 V1 验证层）→⑦归档三出口（decisiongraph_adapter 落 L5+evidence_hash）。
2. **预注册铁律**：C2 每个因子先登记 `backtest_backlog.yaml`（threshold_status=draft，批次决策点冻结后才跑；无注册条目的回测结果不予归档）。
3. **实验登记**：experiment_registry 的 factor_eval 类型在 schema 里已支持（无先例，EXP-FACTOR-EVAL-001 起），result_summary{sharpe,max_dd,ic}+过拟合六法字段。
4. **factor_registry**：10 类 10 族，预期条目为零；growth 族 common_types 设计态注记"预期增速上修（分析师一致预期变化）"（L194）= 种子。条目格式照 FCT-INTRADAY-015 块（factor_id/name_zh/factor_class/formula/params/inputs/outputs/frequency/lookback_period/universe/benchmark_id/neutralization/pit_policy/code_path/status/ic）。
5. **PIT 白名单扩表**：pit_query.py L192-202 `_FINANCIAL_PIT_TABLES` 加 research_report（period_col=None 照 repurchase 模式，时间锚=publish_date）；**注意 SQL 模板硬编码 announce_date 列名（L176,181）——需参数化时间锚列（小改）**。
6. **评估引擎现成**：multifactor_pit_backtest（注入式回调+5 层 PIT 断言）、layered_backtest（layered_returns/compute_layer_spread）= SOP-B ④⑤⑥ 的 L0 引擎，无需新建回测机器。

## 5. 分期施工

| 期 | 内容 | 依赖 | 量级 |
|----|------|------|------|
| **C1** | M1 派生表（DDL+回补+品类/DS 登记）+ pit_query 白名单参数化扩表 | 无（数据已在库），不占回测通道 | 1-2 天 |
| **C2** | 预期因子族 6 个：backlog 预注册 → 逐个 SOP-B ④⑤⑥ → EXP-FACTOR-EVAL 台账 | C1 + **回测通道空闲（排队在 P0 后）** | 每因子 0.5-1 天 |
| **C3** | M3 超预期事件填坑 | C1 + 财报日历 | 2-3 天 |
| **C4** | M4 PDF 文本 LLM 管线 | 建议等 P0 收口 + 数值链路出证 | 3-5 天 |
| **C5** | M5 信号融合（veto + bundle 扩字段） | SOP-C C5 解冻 | 1-2 天 |

## 6. Owner 决策点（拍板即开工）

| # | 决策 | 推荐 |
|---|------|------|
| D1 | 因子族注册方式：新增 `expectations` 族（growth 族 L194 注记转正）vs 并入 growth 族 | **新增族**（一次施工一个族，10→11 族，审计清晰） |
| D2 | C2 首批因子顺序 | **EXP-02 修正动量 → EXP-01 一致预期EP → EXP-04 异常覆盖 → EXP-05 分歧度 → EXP-06 评级**（修正动量文献最强+我们明细数据最独特） |
| D3 | pit_query SQL 模板参数化时间锚列（小改，必做） | 直接列入 C1 |
| D4 | C4 文本管线时机 | 等 P0 收口 + C2/C3 出证后启动 |
| D5 | 与 P0 主线的关系 | C1 并行（不占回测通道）；C2 起排队在 P0 之后 |

## 7. 出证与引用清单

- 机构：华泰单因子测试之九（2018）/华泰 AI 系列 54/华泰基本面量化之二（2024-12）/华泰策略《预期调升》（2020）
- 学术：Gleason & Lee 2003；Lee & So 2017；Jegadeesh et al. 2002；Diether et al. 2002；Engelberg et al. 2019；Ball & Brown 1968；Lv 2025 (arXiv 2411.13813 / 2502.20489, AFA 2025)；韩国卖方研报 LLM 对比（2025）
- 开源：microsoft/qlib（RD-Agent）；AI4Finance-Foundation/FinGPT；TradingAgents
- 项目内契约：event_factor_matrix.py L288-312/L393-410/L457-469；negative_veto.py L46-111；pit_query.py L176-202；factor_registry L194/L273-299；sop_b_node_loop.md:30-100；experiment_registry entry_schema

---

## 8. EXP 族预注册（2026-09-14，SOP-B 护栏③——跑前冻结禁挪）

> 依据=裁定 2026-09-14（Owner 授权夜班自裁，全天候协议）：C2 放行进回测通道。排队条款 D5 的原约束
> "回测通道空闲（排队在 P0 后）"已消失（P0-001/002 判 valid，P0-003 为壁钟积累型不占通道）；
> FQ 批同通道先例在案。研究判定与部署门位解耦：EXP 因子 can_deploy=False 直到 BT-P0-003 转正。

### 8.1 窗口与门槛（与 FCT-FQ/GR 同款，registry 头 2026-09-12 成文判据）

- IS（晋级窗）= 2019-01-01~2023-12-31 月末截面（60 月）；OOS = 2024-01-01~2026-09-11 稳定性复核。
  IS 从 2019 起的依据=数据核对电池实证：2017-2018 研报覆盖 1.5-1.8k 只显著稀薄（2022 后 2.3k+）。
- ④ IC 门槛：IS 截面 RankIC 均值 |IC|≥0.02 且 IC 序列 t 检验 p<0.05 且月度覆盖≥60%。
- ⑤ 剪枝：五分位单调性（分位秩相关≥0.6）；分状态条件 IC（c1_backtest.regime_state_anchored 四档，
  上游已 valid）；与 20td 价格动量秩相关≥0.85 → 挂 variant_of 或否决（华泰"剔动量改进"对照）。
- ⑥ 窄测：Top50 等权月频多头，成本五项读 MatchingConfig #233（零硬编码）；
  准入线=IS 超额 Sharpe≥0.5 且 OOS/IS≥0.7（FQ 同款）；过拟合门禁=OverfittingDetector+DSR。
- **滑点压力协议（本批新增，裁定 2026-09-14）**：⑥ 附 slippage_bps∈{土规20, 40, 80} 三档重跑；
  结论对 80bp 仍稳健 → P0-003 pending 不实质；仅 20bp 档达标 → 标 cost-fragile 自动降级。

### 8.2 预注册参数网格（禁越界）

- EXP-02：k_td∈{20, 60}×forecast_year∈{fy1}（主档 k=20，3m 为复核档）；disp_floor=1e-6。
- 试验计数进 n_trials（DSR 校正原料）：④ 每因子 ≤4 配置（k×fy 网格）+ ⑤ 四状态 + ⑥ 三滑点档。
- ⑥ 组合窗 2019-01~2026-08（月末→月末持有）；AUM/最小佣金/费率全读 MatchingConfig。

### 8.3 台账约定

- 逐因子 run 落 experiment_registry（EXP-FACTOR-EVAL-001 起，factor_eval 型开山）；
- evidence 写 factor_registry 条目（SOP-B ④⑤⑥⑦ 分段留痕，同 FQ 批格式）；
- 评估器=scripts/backtest/eval_exp_expectations.py（④⑤⑥ 单脚本链，JSON 出证）。

---

## 9. 【重大数据缺口档案】research_report 预测槽位=源站当前快照，历史区间无 PIT（2026-09-14）

> 发现路径：EXP-02 首跑 ④ IC 全 NaN → 探针实证 600519 因子值全史零方差（恒 0=无修正）→
> 直查源行：2018-07-16 研报（infoCode AP201807161166783168，东莞证券茅台中报点评）携带
> fy0=2026/eps=69.83 即今天的预测值。三路交叉验证定案。

### 9.1 定性

- 东财研报明细源的 fy0/fy1/fy2 槽位字段=**源站页面当前快照值**，非报告发布时点值。
  证据：① infoCode 证明报告本体是 2018 年，槽位却是 2026；② 2020 前发布研报 47,610 份中
  40,176 份槽位年=2026、7,434 份无预测（fy0=0），uniq(eps_fy0)=487≈当前全市场预测值集合；
  ③ 600519 全部 2213 交易日 × 3 预测年值恒定（uniq=1）。
- 传染面：consensus_daily（DS-229）678 万行 = "今天的预期回放到历史"——2017~2026-09 历史
  快照全部无效（未来函数）；pit_query 白名单 research_report 的 EPS 槽位消费同险。
- **未被既有核对发现的原因（方法论教训）**：五层电池 A-D 为结构检查不涉值语义；E 项 PIT 对账
  与 --check 均=同源对账（SQL 重算与表同饮一池污染水）——对账只能验"聚合逻辑"，验不了
  "源语义"。前会话"茅台抽查与东财一致"恰以污染源为真值。

### 9.2 仍然有效的部分

- publish_date 本身真实（研报清单、评级、机构、覆盖度计数不受影响）——EXP-03 修正广度的
  上调占比需 EPS 槽位历史值，同险；**关注度/覆盖度类因子（EXP-04 的 n_reports/n_orgs、
  评级分布计数）不受值污染**（计数是窗口内研报数，真实）。
- 前向积累：每日增量不重抓旧报告 → 新报告入行时的槽位值≈发布时值，2026-09 起 consensus
  前向积累 PIT 干净（近似成立）。
- analyst_forecast（同花顺一致预期官方快照，2026-07 起日度累积）= 干净 PIT 源，C3 超预期的
  consensus_before/after 本就设计走它（§M3 实时通道）。
- C4 PDF 文本管线 = 从研报原文提取"发布时点预测"的潜在历史修复路径（原文有真 as-of 值）。

### 9.3 处置（Owner 已裁 A，2026-09-14；标注批同日执行）

1. consensus_daily 历史行处置三选一 → **Owner 裁 A（保留+标注，非破坏）**：已执行
   data_asset_registry DS-228/DS-229 format_summary 补 ⚠PIT 价值限制（version→1.1.0）；
   pit_query.py research_report 白名单项加预测值列禁消费注释（锚列 publish_date 本身无恙）。
   本文档 ttl 同日 task_bound→permanent（§8 预注册+§9 档案已被 factor_registry/
   experiment_registry doc_ref 永久引用，不再适合作业件清扫口径）。
2. EXP 族评估（EXP-02 首跑已执行）：④ 出证=data-gap（非 noise 非 valid），FCT-EXP-002 保持
   candidate；IS 2019-2023 窗无有效数据——**改用前向积累+analyst_forecast 双源，积累期复核**
   （预估干净回测窗最早 2027-07，若 analyst_forecast 快照密度支持可提前）。
3. 后续批：D3 时间锚参数化（锚列无恙，低优）；历史区间修复候选=C4 PDF 原文提取
   （研报 PDF 是真历史原件，内含发布时点预测表）+全网源调研结论（2026-09-14 会话另附）。

### 9.4 EXP-02 首跑记录（run=eval_exp_expectations.py 2026-09-14，数据坍缩形态）

- ④ IS/OOS IC=NaN（因子零方差——快照回放使 eps 20 交易日零变化，全市场恒 0 修正）；
  覆盖 908/月（IS）/1262/月（OOS）真实；⑥ 窄测四档数值无意义（退化因子上构建，弃用）；
- n_trials=6；归档=EXP-FACTOR-EVAL-001；**本 run 教训价值=评估链路端到端贯通+暴露源污染**。
