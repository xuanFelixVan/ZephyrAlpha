---
ttl: permanent
doc_type: architecture_view
title: 交易决策地图（Trading Decision Map）——决策内容索引层设计备忘
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.5.0"
date: 2026-09-04
topic: trading_decision_map
scope: 07_trading_decision_architecture
parent: "[讨论备忘录](../../../_working/2026-09-04-trading-decision-map-discussion.md)（D1-D6 裁定+27 项论断交叉验证报告）"
related_modules:
  - src/zephyr/trading/decision_map.py
  - config/trading_decision_map.yaml
  - docs/03_modules/_domain_trading/decision_map/blueprint.md
related_issues:
  - "#ARCH-TRADING-DECISION-MAP-001（待登记：V0 施工完成后补登）"
---

# 交易决策地图（Trading Decision Map）——决策内容索引层设计备忘

## 1. 背景

### 1.1 项目处境与核心问题

项目已有 6 类全景图（depgraph/dataflowgraph/decisiongraph/battle_map/frontend_map/路径树）回答"**系统怎么运转**"（工程视图），但缺一个总口子回答"**钱怎么赚**"（决策内容视图）——什么市场情况、在决策链哪个环节、用哪个策略/因子、靠哪些数据、由哪段代码实现。

Owner（主观交易员）的实盘决策是一条分层漏斗：**看大盘（下不下单）→ 看板块（开哪个板块）→ 看个股（选哪只票）→ 看买卖点（何时进出）**。现有 8 个策略（打板/默认多头/事件驱动/多因子/TopN动量/30秒冲高回落做T/盘口失衡反转做T/VWAP回归做T）各对应漏斗不同环节，但没有一张图把它们串起来。

### 1.2 行业验证锚点（详见讨论备忘录 §12，27 项论断 24 项验证通过）

- **漏斗=机构决策流程通用标准**：Fisher Investments 官网直接画成漏斗；宏利基金五段式（MVPS 资产配置→行业研究→股票选择→组合构建执行→评估风控）与 Owner 主观流程逐段对应
- **生命周期=机构交易管理通用标准**：Financial Edge 交易生命周期四段，"持续持仓与风险管理"为正式阶段
- **三流骨架=两者复合**：漏斗管决策（建仓流内部解剖）+ 生命周期管持仓（持仓/离场流）+ 风控横切
- **L1 大盘层=传感器阵列**：WSC regime 三支柱（趋势+广度+情绪）；A股情绪周期量化门槛体系（涨停数/炸板率/连板梯队）；养家心法"赚钱效应＞指数"
- **图谱单真源+多视图投影**：VESA 论文（arXiv 2410.22846）/ Nextspace 本体架构
- **状态→策略矩阵**：SignalPilot Strategy Selection by Regime；假设治理阶梯（quantoptimus 80 thesis→6 阶段管线→7 部署）

### 1.3 约束条件

- 真源唯一铁律：地图不得复制 battle_map/strategy_registry/factor_registry/data_asset_registry 的内容，只做**引用**
- 8 个策略的"策略所处环节"已由 StrategyMeta 透传（回测页在用），地图引用不重建
- 市场分片三层隔离铁律：A股/币圈同 schema 不同实例
- V0 不涉前端（Owner 2026-09-04 指令）：只做后端真源+加载/校验模块

## 2. 决策

### 2.1 定位（D1，Owner 拍板）

**独立新地图**——项目第 7 张地图性质的**决策内容索引层**：

| 层 | 真源（全部已存在） | 地图角色 |
|---|---|---|
| 环节 | 本地图 YAML（决策链骨架是新增内容） | 定义 |
| 策略 | strategy_registry.yaml（REG-STR-001，STR-*） | 引用 |
| 因子 | factor_registry.yaml（REG-FCT-001，FCT-*） | 引用 |
| 数据 | data_asset_registry.yaml（REG-DATAFLOW-001，DS-*） | 引用 |
| 模块 | depgraph（MOD-*）+ blueprint.md | 引用 |

地图自身**不复制任何内容**：环节骨架（决策链结构与规则）是本地图唯一新增的真源；其余四层全部按稳定标识符（STR-*/FCT-*/DS-*/MOD-*）引用，缺口检测=引用存在性校验。

### 2.2 骨架（D3，Owner 拍板）

**三流骨架，建仓流内嵌 Owner 漏斗**（机构通用用法实证）：

```
【建仓流 entry_flow】
  L1 大盘总闸（双通道→四路传感器阵列）→ L2 板块 → L3 个股 → L4 买卖点/执行
【持仓流 position_flow】
  P1 持仓体检 → P2 做T/加减仓（三个做T策略挂载点） → P3 加仓决策
【离场流 exit_flow】
  S1 卖出信号收集评分 → S2 离场执行
【风控横切 risk_cross】 暴跌/流动性危机可在任何流任何环节触发（非第四条流）
```

L1 结构（D4/D6，Owner 裁定+行业修正）：**四路同层级传感器阵列**——①大盘指数 ②市场内部结构（涨停/跌停/炸板/连板梯队=广度）③赚钱效应（昨日涨停溢价/晋级率=投机情绪）④波动率（可选）→ 汇聚「市场状态判定」→ 三输出（预算/机会窗口/状态标签）。指数↔情绪双向边、短线情绪领先。

### 2.3 存储与视图（§8.2 结论，行业验证）

**存储=图谱（节点+边），展示=投影**。漏斗、环节×状态矩阵、三流泳道都是同一张图的不同视图；新想法=加节点/边，不动骨架。

### 2.4 状态矩阵与置信度（D5，Owner 拍板）

环节×市场状态矩阵，每格标注置信度：`verified`（回测归因支撑）/ `proposed`（主观假设待验证）/ `untested`（未填）。骨架先行，血肉（格子内容）以 proposed 逐步添加。行业模板：thesis 库→分级验证管线（quantoptimus/quantest）。

### 2.5 双市场（Q3 倾向，结构先行）

同一套 schema 两棵市场实例子图（market: cn_a | crypto）。币圈 V0 为骨架空壳（L2 弱化为赛道层），内容随币圈策略库成长。

### 2.6 V0 范围（D2，Owner 拍板 + Owner 2026-09-04 指令）

**后端骨架，不涉前端**：

| 交付物 | 路径 | 内容 |
|---|---|---|
| YAML 真源 | `config/trading_decision_map.yaml` | 三流环节骨架+8 策略归位+L1 传感器+状态矩阵骨架（proposed 占位）+币圈空壳 |
| 加载/校验模块 | `src/zephyr/trading/decision_map.py` | dataclasses + load_decision_map() + validate_decision_map()（引用存在性校验→GapReport） |
| 单元测试 | `tests/trading/test_decision_map.py` | 加载/校验/缺口检测全路径 |

**V0 明确不做**：API 端点（V1）、前端视图（V1）、入 DB（V2，Q8 待定）、动态状态判别（V2）、ClickHouse/depgraph 实时缺口检查（V1）。

### 2.7 列轴定稿与灰度判定（v1.2.0，Owner 2026-09-05 裁定）

**列轴六段（Owner 实战 6 段+机构命名）**：`capitulation 恐慌投降（冰点）→ accumulation 吸筹修复（修复期·震荡筹码交换）→ ignition 点火启动 → expansion 发酵扩散 → euphoria 亢奋高潮 → distribution 派发退潮`。
命名=Wyckoff 阶段论+行为金融标准术语；**MarketTriage 六态 regime 仪表盘**（2026-03，366 资产实盘）同构验证——其原话"三四态模型错过过渡带，而过渡带正是钱被赚走和亏掉的地方"，修复期独立成段获机构实证支持。

**灰度判定（Owner 裁定"软分档非硬阈值"）**：三层架构，业界标准=CNN Fear & Greed 家族连续分位法——
1. 因子层：每因子 0-100 滚动分位得分（连续滑动，非二值化）
2. 合成层：得分×历史可靠度权重 → 总分/状态分布（如"高潮 0.55/发酵 0.30/修复 0.15"）
3. 分档层：六段隶属度锚点=社区公开阈值（涨停 60/120 家、炸板率 35%、晋级率 60%，隶属度 0.5 交叉点），过渡带内多段共享隶属度

**冲突仲裁三规则（L1-AGG，Q9 收口）**：
1. 多数表决基准（国泰海通涨停板情绪择时模型：因子阈值信号多数表决）
2. **历史可靠度加权**——四路传感器按各自历史判准率动态加权（C3 归因反馈闭环兼任传感器可靠度养成器，与 arXiv 2608.13108 historical-experience weighting 同构）
3. **冲突度=状态分布熵**：熵高→输出"分裂市"标记+自动降档（机构规则"降仓不选边"落地）+提示 Owner 人工接管（conformal 弃权思想，arXiv 2607.27143）

**算法可插拔分层**（列轴词汇固定，分类器进化不返工）：V1=规则打分器（雪球阈值+国泰海通表决）→ V1.5=分位打分合成（灵犀指数法）→ V2=GMM/Wasserstein HMM（arXiv 2603.04441，2026-02 最先进可解释 regime 模型）。

### 2.8 L1 预算带与灰度仓位（v1.2.1，Owner 2026-09-05 裁定）

**六段预算带**（机构方法+A股多源收敛，全 proposed）：

| 状态 | 总仓位带 | 动作语义 | 出处 |
|---|---|---|---|
| capitulation | 0-10% | 只试错新题材首板，不抄底 | 养家≤10% / 龙头战法版 0-2 层 |
| accumulation | 20-30% | 试错+建底仓，错了就砍 | 启动期 2-3 成（55188/东财多源一致） |
| ignition | 30-50% | 确认后加仓，干新主线 | 养家回暖 30-50% |
| expansion | 50-70%（verified 后 earned-position 上探 70-80%） | 重仓主升，分歧转一致加仓 | 发酵 5-7 成多源一致；东财"主升老手可满仓" |
| euphoria | ≤30% | 只卖不买、锁仓不新开 | 养家高潮≤30%（卖在一致） |
| distribution | 0% | 空仓，反弹诱多 | 全源一致"退潮空仓" |

**灰度仓位语义（Owner 裁定"仓位也是灰度"）**：预算带=区间包络非查表定值；带内实际仓位=状态分布加权连续插值（如分布"expansion 0.7/ignition 0.3"→仓位在 30-50% 带内向 50-70% 带方向插值）。机构依据：1uptick regime-adaptive framework——**过渡期（最大隶属度<60%）自动降仓 30-50%**；尾部预备金 10-15% 永不投出（tail-risk reserve）。

**二值切换 vs 分级的讨论结论**：全进全出（Risk-Off 100% 黄金式）机构存在且有实证，但边界磨耗（whipsaw）+A股跌停流动性风险（满仓隔夜退潮大阴线可能无法止损）使其仅在**分类器 verified 后**成立。设计取**earned-position 语义**：格子陡峭度=分类器置信度的函数，proposed 阶段保守分级，verified 后凭回测归因逐步放陡至二值。

**资金体量讨论结论**：风险承担以百分比计=资金无关（Owner 判断正确，Kelly 无账户大小变量）；可实现仓位受四通道影响——容量约束（**小资金打板容量无限=对机构的合法结构性优势，游资成长路径本质**）、生存数学（资金无关）、执行心理（随纪律退化）、负债端约束（机构专属）。故"单票≤6%"是大资金的容量公式，小资金 earned 单票集中合法；expansion 段高仓位由 verified 归因挣得。

**PP-001 权重校准管线**（不拍数字，机构标准）：等权起步→V1.5 逆波动率调整→V2 半 Kelly（f=0.25×f*，防高估）+HRP 聚类→拼装回测归因→C3 反馈逐月调权。现有主观先验权重保留为 proposed，由归因逐月替换（breakingalpha：等权 vs 科学分配风险调整差 15-40%/年）。

### 2.9 真源对齐裁定：B 方案（六段定稿）+ 已有资产引用（v1.2.2，Owner 2026-09-05 裁定）

**背景撞车**：v1.2.0 新造的情绪六段与项目已有资产撞车——Owner 全项目搜索指令暴露三套既有状态体系：
1. **D_REGIME 宏观 12 态系统【已实现】**：10 号设计备忘录（真源 D-SIGNAL-04），3×3 趋势×波动率网格→施工降维 **4 态 HMM（r1 低波震荡/r2 中波震荡/r3 牛市/r4 熊市）+3 overlay（CRISIS/RECOVERY/BREAKOUT）=7 维概率分布**（RegimeSnapshot frozen 契约），回测验证 runner 已建（backtest/regime_validation/）
2. **情绪周期 4+1 阶段**（冰点/反核/主升/疯狂/退潮）：10 号 spec §3.3，已含与 12 态的映射表，原文"情绪周期更细（1-2 周），12 态更粗（1-3 月），不同时间尺度不矛盾可共存"
3. **作战预案引擎**（D_PLAN/BM-PLAN-01-C）：当日微观推演（今天冲高回落怎么应对）

**时间粒度三层定位（Owner 粒度直觉获实证）**：段状态（周/日线，1-3 月）=12 态系统；情绪相位（1-2 周）=六段轴；当日预案=预案引擎（地图只挂引用）。

**A vs B 第一性原理裁定 → B**：判据="一个状态唯一对应一组动作"（列轴的目的）。五态的"反核"复合两组互斥动作（accumulation 建底仓不确认 20-30% vs ignition 确认加仓 30-50%）——违反一态一动作原则，灰度插值无法区分执行哪套；六段拆开后每段动作唯一。机构实证（MarketTriage 过渡带独立成段）+Owner 实战（六段带修复期）+灰度软分类化解多状态边界成本。**宏观 12 态轴零改动**（B 只定稿情绪相位轴词汇，10 号 spec §3.3 映射表增补六段列=增补非推翻）。

**六段↔五态映射**：冰点→capitulation / **反核→accumulation+ignition（拆分）** / 主升→expansion / 疯狂→euphoria / 退潮→distribution。

**已有资产引用挂载**：
- TDM-E-L1（总闸）+ TDM-E-L1-AGG：`module_ref: src/zephyr/regime/core/regime_detector.py`（D_REGIME，消费 RegimeSnapshot 7 维概率=宏观谨慎度，总闸不自算宏观态）
- 当日预案：作战预案引擎（D_PLAN）管辖，地图只挂引用
- AGG 双轴合成定稿：RegimeSnapshot 概率（谨慎度→预算带）× 情绪六段分布（机会→策略路由）× 仲裁三规则

**SOP 沉淀**：本轮撞车教训固化为《交易决策地图逐层讨论 SOP》（docs/01_policies_and_standards/sop/trading_decision_map_layering_sop.md）——已有资产清单先行+四路外部调研+上层完整性检查+枝干分级检查。

**传感器数据引用定稿**：S1 指数→DS-150（日K）；S2 内部结构→DS-082（涨跌停价，涨停/跌停/炸板统计地基）；S3 赚钱效应→DS-082+DS-107（新闻情绪窗）；S4 波动率→DS-150（VIX 表未登记=数据缺口）；AGG→DS-098（两融杠杆环境）。因子层缺口：情绪类因子在 REG-FCT-001 仅 family 级（sentiment），FCT-* 级条目未建——factor_refs 留空=缺口节点，补登后回填。

**矩阵格定稿（24 格，全 proposed）**：L1×6（预算细则待填）+ L4×6（daban 仅 ignition/expansion/euphoria）+ P2×6（三做T 仅 accumulation/expansion）+ C1×6（预算切分待填）。PP-001 sleeves activation_state 升级为多状态列表（daban 3 段/做T 2 段，校验器 R12 同步支持 str|tuple）。

### 2.10 E-L2 板块层血肉 v1.3（D19，Owner 2026-09-06 裁定）

**吸收 22 号 spec v1.9.7**（SOP Step 1 盘点后按"同等职责文档合并"政策吸收）：E-L2 展开为 **7 树枝 15 子节点**（v1.5 节点规范全字段：七要素+五联锚+activation/invalidation/ai_autonomy/fallback），全部 ai_autonomy=auto（信号生产节点）。

**树枝清单**：01 强度综合（结构强度 evaluate_strength/动量排名 ranking_engine/q3q5q20/资金流聚合/watch_score 注入）→ 02 轮动序列（RRG 四象限+单板块预警）→ 03 调整周期（扩散指标进度）→ 04 板块级状态（5 分类+虹吸态）→ 05 水温响应（**挂起**）→ 06 个股传导（三级门槛→龙头识别→强度加权）→ 07 回踩质量（A/B/C 判定）。

**模块锚定**：production=MOD-SIG-026（analyzer+sector_breadth+sector_momentum）/MOD-L00-004（ranking+快照）；planned=MOD-SIG-040（调整周期）；**8 个红节点**（RRG/5分类/虹吸/门槛/龙头/传导/水温×2/回踩）module_ref=null=缺口显性化。数据锚：DS-059 快照/DS-170 板块日K/DS-181 money_flow/DS-186 成分股/DS-188 元数据。策略锚：STR-DABAN-003（强度数量档）→01-1、STR-DABAN-002（资金三日规则）→01-4（R3 校验；回归锚从相等改子集断言——8 实盘策略全覆盖不锁相等）。

**三裁定**：①**双通道输出**：Top 候选池+强度分→TDM-E-L3（机器）+ 盘后板块轮动简报→Owner 注意力（人工，锚 BM-SEL-25-C-3）②**只标记不排期**：8 红节点=缺口语义，施工排期归 22 号自身，地图不越权催期 ③**水温接口挂起**：树枝05（05-1/05-2）待 L1 温度计时间周期定稿——Owner 指出三尺度错配（宏观 12 态=月级/情绪六段=周级/22 号水温 5 档=日级），回炉 L1 层先定大盘温度计时间周期，再回 E-L2 收口（§3.1⑪ 5 档响应菜单保留，判定权归 L1）。

### 2.11 大盘四层温度计架构（D20，Owner 2026-09-06 终裁）

**时间尺度错配的解决**（Owner 洞察 → 业界四路验证）：业界标准=多时间尺度级联架构（arXiv 2606.06190 三尺度 MS-GARCH/Jungletrade 级联/breakingalpha 分层过滤器/A股三级共振），**每层独立温度计+上层过滤下层**——修正 AI 原案"5 档=前两层合成读数"。

**四件套定稿**：月级 12 态（管能否持仓）/周级六段（管方向）/日级水温 5 档（管今天多激进，**新增独立温度计 L1-S5**）/盘中预案引擎（管应对动作）。22 号 5 档正位=日级条件层，非换算表。

**跨层合成两规则**：①**封顶不覆盖**——周级退潮→日级最高 RISK_OFF，月级危机同；日级如实报告，放行比例被上层压住 ②**对齐加成**——月+周+日三层同向→预算带取上限（业界三级共振），冲突→取下限+高层赢。

**日级传感器 S5（11 信号全上，Owner 裁定"先大而全跑数据、后数据裁噪"）**：A 组实战 8（涨停家数环比/连板梯队/炸板率>50%/跌停+核按钮/昨日涨停溢价≤-5%/红盘<1500/量能匹配诱多识别/板块联动混沌）+ B 组机构 3（宽度领先/对坏消息的反应/市值分层宽度）。数据与 S2/S3 同源（DS-082/059/150），消费"当日读数+环比骤变"。**裁噪预留**：同源指标重复计票（冗余即静默杀手）→ 灰度合成阶段相关性去重。5 档判定阈值=社区公开版（proposed），回测校准后升级。

**落盘**：YAML +S5 节点+2 边（S5→AGG feed/S5→05-1 feed）+AGG 四层注释+05-1 解挂（决策问题改为"日级主判+月/周封顶"）。

### 2.12 大盘域算法审计与裁噪纪律（D21+D22，Owner 2026-09-06 终裁）

**D21 裁噪三防弹衣**（"先大而全跑数据、后裁噪"原则 D20 的成立前提，学界标准流水线：Factor Zoo 全量收录→统计裁剪）：
1. **多重检验校正**——参数搜索后纯噪声挑最优，naive 显著性检验假发现率=100%（Deflated Sharpe 实证：1000 策略选最大可造出年化 Sharpe 1.63）；必须用 DSR/Harvey-Liu 校正（Harvey 2016 新时代门槛 t>3.0）
2. **样本外分离**——选信号与验信号不同数据（walk-forward）
3. **相关性去重**——同源信号重复计票（冗余即静默杀手）；裁剪工具本身不稳定（LASSO 连市场因子都会误杀，Feng/Giglio/Xiu 用双选择法补救）
适用范围：S5 日级 11 信号的裁噪、情绪因子 FCT-* 补登后的筛选、未来所有因子/信号入库-裁剪循环。

**D22 四层算法审计结论（全网 20+ 来源交叉核查）**：**三同款一增强，无需推翻**——
- **月级**：Gaussian HMM 同款；**4 态有文献直证**（Hamilton 1989 族；2态/3态/4态谱系中 Maheu 2012/Jiang 2015/Lewin 2022 实证 m=4 支配；BIC 对单状态基准选型=标准做法）；7 维概率输出=filtered 软分类主流（防未来函数）；静态转移概率用于月级=正确（MS-GARCH 论文：低频静态/高频 TVTP）；3 overlay=过渡态实践标配。**澄清**：实现为 4 态+3 overlay，"12 态"是设计期蓝图经 BIC 降维的产物。
- **周级**：percentile composite 逐字同构 CNN Fear&Greed 三步法（测量→自身历史归一化→加权合成→分档带）；**灵犀指数（A股版）10 底 7 顶实证**（冰点读数 10-37/顶部 45-88 区分度已验证）；我们的状态分布（灰度）较单一 0-100 更丰富=增强。
- **日级**：信号计数表决同构 itafx 7 信号检查表（7 中 5 对齐=建仓/<5→减仓 50%/反向 6-7→回避）；A 组信号=机构 internals 的 A股本土化。
- **盘中**：预案引擎=pre-market routine+trading plan 同构；执行算法 TWAP/VWAP/IS 已在 EXA 库（REG-EXA-001 六件）。
- **三个增强方向（非错误）**：①月级补宏观特征（信用利差/收益率曲线/中国 VIX）②日级中国 VIX 表登记（DS 缺口已标）③月级升级路径备选=Wasserstein HMM（哥大 2026，防状态漂移，Sharpe 2.18）。
- **差异合法性**：绝对周期压缩（机构 SAA 年级 vs 我们月级）由策略频率决定（宪章约束四：日频以上），层级结构/职责/节拍/跨层规则与机构全部同构；分形市场假说（FMH）=分层理论根基。

## 3. 考虑过的替代方案与拒绝理由

| 方案 | 拒绝理由 |
|---|---|
| 并入作战地图（环节上加决策规则字段） | 工程/决策双真相混杂导致作战地图臃肿；两图对齐 key 不同（step_id vs 决策链），硬并违背单一职责 |
| 纯漏斗四层骨架 | 装不下 3 个做T策略（持仓流）与卖出（离场流）；漏斗只是建仓流内部解剖 |
| 真源直接入 DB 三表（battle_map 同款） | V0 轻量优先（Owner 倾向 Q8）；YAML 有文件可审可 diff，等实盘调度器消费决策规则时再入 DB |
| 校验器直连 ClickHouse/depgraph 查实时存在性 | V0 引入 DB 依赖违反 MVP；V0 用三注册表 YAML 做存在性检查（离线可测），实时四态灯留 V1 |

## 4. 施工算法

> **✅ 已施工**（2026-09-04，V0 后端骨架；MOD-TRADING-015）：config/trading_decision_map.yaml（19 节点/19 边/矩阵骨架/双市场）+ src/zephyr/trading/decision_map.py（load/validate R1-R8，含 15 字段头+ALGO_FLOW）+ tests/trading/test_decision_map.py（19 用例，循环验收连续 2 轮 0 错误）+ docs/03_modules/_domain_trading/decision_map/blueprint.md。depgraph 设计态 node_id=11576295（planned）。

### 4.1 YAML schema（config/trading_decision_map.yaml）

```yaml
schema_version: '1.0'
map_id: TDMAP-001
nodes:                       # 决策链节点（环节/传感器/状态判定）
  - node_id: TDM-L1          # 命名 TDM-{FLOW}{LAYER} 或 TDM-{FLOW}-{NN}
    name_zh: 大盘总闸
    market: cn_a             # cn_a | crypto
    flow: entry_flow         # entry_flow | position_flow | exit_flow
    layer: L1                # 层内序（L1-L4 / P1-P3 / S1-S2 / X1 横切）
    node_type: gate          # gate | stage | sensor | aggregation | cross_cutting
    point: 盘前              # 盘前 | 盘中 | 盘后 | 持续（时点属性）
    decision_question: 今天下不下单/给多少仓位   # 决策问题一句话
    factor_refs: []          # 引用 REG-FCT-001 的 FCT-*
    data_refs: []            # 引用 REG-DATAFLOW-001 的 DS-*
    module_ref: null         # 引用 depgraph MOD-*（可空=缺口，V0 允许 null）
    strategy_mounts:         # 本环节挂载的策略
      - strategy_ref: STR-DABAN-001   # 引用 REG-STR-001
        confidence: proposed            # verified | proposed | untested
        evidence: null                  # verified 时必填（回测 run 标识）
edges:                       # 决策依赖边（有依赖的地图才能推理）
  - from_node: TDM-L1
    to_node: TDM-L2
    edge_type: sequence       # sequence | broadcast | feedback
state_matrix:                # 环节×市场状态（骨架，格子 proposed 占位）
  states: [强势, 震荡, 弱势]  # V0 列轴占位；情绪周期细化留血肉阶段
  cells:
    - node_id: TDM-L4
      state: 强势
      mounted: [STR-DABAN-001]
      confidence: proposed
markets: [cn_a, crypto]      # 同 schema 两实例
```

### 4.2 接口签名（src/zephyr/trading/decision_map.py）

```python
@dataclass(frozen=True)
class DecisionMapNode: ...     # node_id/name_zh/market/flow/layer/node_type/point/
                               # decision_question/factor_refs/data_refs/module_ref/strategy_mounts
@dataclass(frozen=True)
class StrategyMount: ...       # strategy_ref/confidence/evidence
@dataclass(frozen=True)
class DecisionMapEdge: ...     # from_node/to_node/edge_type
@dataclass(frozen=True)
class GapReportItem: ...       # level(error|warning)/code/node_id/detail
@dataclass(frozen=True)
class DecisionMap: ...         # nodes/edges/state_matrix/markets

def load_decision_map(path: Path) -> DecisionMap:
    """加载 YAML 真源 → 不可变 dataclass；schema 结构错误抛 DecisionMapSchemaError"""

def validate_decision_map(dm: DecisionMap, registry_dir: Path) -> tuple[bool, list[GapReportItem]]:
    """引用存在性校验（V0 全部离线 YAML）：
    R1 节点结构（必填/枚举：market/flow/layer/node_type/point）
    R2 边端点存在性 + edge_type 枚举
    R3 strategy_ref 存在性（strategy_registry.yaml entries[].strategy_id）
    R4 factor_refs 存在性（factor_registry.yaml entries[].factor_id）
    R5 data_refs 存在性（data_asset_registry.yaml datasets[].dataset_id）
    R6 strategy_mounts.confidence 枚举 + verified 必带 evidence
    R7 state_matrix.cells 引用环节存在性 + mounted 策略存在性
    R8 边无环（sequence 边成环=骨架错误）
    返回 (all_errors_zero, GapReport 列表)；module_ref=null 记 warning（V0 允许，缺口可视化输入）"""
```

### 4.3 状态机与启动方式

- **无运行时状态**：纯函数库（load→validate→report），无常驻进程、无事件订阅——启动方式 N/A（B 类新建功能，非 C 类常驻系统；A.1.4-1.6 声明 N/A）
- 消费方（V1 API 端点/前端）调用本模块，本模块不反向依赖任何运行时组件

### 4.4 测试算法（tests/trading/test_decision_map.py）

1. 正常加载：构造合法 YAML → load 成功 + 字段逐项断言
2. schema 错误：缺必填/非法枚举 → DecisionMapSchemaError
3. 引用缺口：strategy_ref 指向不存在的 STR-ID → GapReport error R3
4. module_ref 缺失 → warning（非 error）
5. 边成环 → error R8
6. verified 无 evidence → error R6
7. **真源自检**：加载仓库内真实 config/trading_decision_map.yaml → validate 全绿（防真源漂移的回归锚）

## 5. 演进方向（V1+，不在本备忘施工范围）

> **v1.1.0 升级（2026-09-05，Owner 终极定位拍板）**：地图终极定位=**整装仿真策略组合的蓝图**（追溯是手段不是目的）。三流→四流：新增**组合资金流 portfolio_flow**（TDM-F-C1 预算切分→C2 组合聚合→C3 绩效归因反馈，C3→L1-AGG feedback 闭环=系统自我进化的图上表达，Millennium pod 模型单体版）；新增**portfolio_plan 整装方案层**（PP-001：8 sleeve 权重全 proposed+聚合规则——拼装回测引擎直接消费，业界已验证多回测加权合成）。schema v1.0→v1.1；校验器 R12（sleeve 引用/权重和≤1/activation_state 在列轴/重复/plan 置信度）。**一份图谱三种用法**：改=填血肉（门禁守）、查=索引（稳定标识符）、跑=整装回测（方案层）。V1 排期重排：**整装拼装回测提前于前端视图**。

- V1：api_server 增加只读端点（GET /api/decision_map）→ 前端泳道图/矩阵视图；module_ref 缺口接 depgraph 实时校验；数据四态灯接 ClickHouse；**整装拼装回测（组合方案→多回测加权合成整装净值）**
- V2：情绪状态动态判别器接入矩阵列轴；真源迁移 DB（若实盘调度器消费）
