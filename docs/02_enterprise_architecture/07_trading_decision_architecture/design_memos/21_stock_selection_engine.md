---
ttl: permanent
doc_type: architecture_view
title: 选股引擎架构
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.1.21"
date: 2026-08-15
topic: stock_selection_engine
scope: 07_trading_decision_architecture
---

> ## 结案报告（AI-NIGHT-001 复核 2026-08-19）
>
> **实际开发**：L0/L1/L2-C 三层生产实证——L0 数据接入（data/ 采集调度全链）、L1 因子工厂（factor/ 池管理 n_max=64 + 8 态生命周期 + IC 衰减监控 + 治理门禁）、L2-C 打板链 4 引擎（MOD-SIG-023/033/034/035 均 production）；层间契约的 SynthesizedSignal 已建（shared/contracts/synthesized_signal.py 实证），signal_synthesizer.py（MOD-L03-001）存在。
>
> **最终成果**：选股引擎架构定稿（active v1.1.21）——三层切分 + 四阶段漏斗 + SelectionResult 统一接口设计 + StrategyBook 对接契约 + BM-SEL-02-J/L 与 BM-SEL-16/17/18 五环节远期/定性登记。
>
> **未做事项及原因**：① SelectionResult 统一接口与 3 sleeve 实现未施工——无 SelectionResult 类实证（signal_ashare 仅有局部 StockSelectionResult），pf_core/strategies/ 空壳，与 20 号 sleeve 策略类同属"首批上线主链路"缺口，待 G08/G09/G10 定型；② 漏斗三层级（BM-SEL-16 分级指标过滤/17 初筛/18 精筛评分）模块未落码（grep 实证零命中，§3.6 已裁定为批处理语义的设计态）；③ confidence 算法（待裁定-5）、事件置信度阈值（待裁定-6）、6 维权重 IC 校准（待裁定-8）未施工——登记为 G08/G09/G10 细节讨论时校准；④ 信号工厂九子阶段 + 信号聚合器按 §3.3.1 裁定远期登记不施工（激活条件=信号冲突/口径漂移实例 ≥3 例，未触发）；⑤ LLM alpha 挖掘闭环（八框架）、Cross-Sectional LSTM、BM-SEL-12 Signature 分布特征为远期登记。

# 选股引擎架构

> 本备忘定义多策略并发架构（[30_multi_strategy_concurrency](30_multi_strategy_concurrency.md) Model A）下选股引擎的分层架构、双引擎融合定位、pipeline 标准接口与 StrategyBook 对接契约。
> 性质：永久态讨论记录，可随项目演进而修订。
> 管理规范见 [01_design_memo_management_spec.md](01_design_memo_management_spec.md)。
> 路线图定位见 [00_index_trading_decision](00_index_trading_decision.md) G05（L1·Alpha 选股层，P1）。
> 前置依赖：[20_first_batch_strategies](20_first_batch_strategies.md) v1.5.10（首批 3 策略定义已定稿）。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G05 选股引擎架构 |
| 所属 | 作战地图 05（[battle_map_05_stock_selection](../battle_map/battle_map_05_stock_selection.md)） |
| 依赖 | G04（策略定义，[20_first_batch_strategies](20_first_batch_strategies.md) v1.5.10 已定稿） |
| 对标 | WorldQuant Alpha 工厂分层 / qstobody 多引擎 / Medallion Architecture |
| 正交性 | ✅ 与 regime 正交（选股不读 regime 输出，[20 §1.4](20_first_batch_strategies.md)） |
| 优先级 | P1 |
| 状态 | ✅ 已定稿 v1.1.21 |

## 2. 背景

### 2.1 项目处境
- 个人 + 100% AI 开发的 A 股量化系统（miniQMT，T+1，不能做空）—— [20 §1.1](20_first_batch_strategies.md)
- 多策略并发架构已定稿为 Model A（独立账本 + firm 聚合 + regime 风险节流），首批 3 策略 = 打板 + 多因子 + 事件驱动（[20 §2](20_first_batch_strategies.md)）
- 三策略的 alpha 信号源链已不同程度施工（[20 §2.2-2.4 施工回填](20_first_batch_strategies.md)）：打板链 4 模块全 production/stable、因子工厂治理层全 production/stable、事件链仅数据底座
- 选股阶段作战地图（[battle_map_05](../battle_map/battle_map_05_stock_selection.md)）已有 BM-SEL-01~27 共 27 环节，分属 L0/L1/L2-C 三层，混合 production/design 态
- **缺口的 why**：30_multi_strategy_concurrency 锁了"组合层"why，20_first_batch_strategies 锁了"3 策略是什么"why，但"选股引擎如何分层、双引擎融合落在哪、pipeline 标准接口长什么样、如何对接 StrategyBook"的 why 层此前空白（骨架）

### 2.2 核心问题
1. 三策略的选股信号来自不同源（打板=盘中实时游资情绪、多因子=盘后横截面因子、事件驱动=离散事件），如何用**统一的分层架构**承载而非三套割裂管线？
2. 双引擎融合（BM-SEL-25）是跨策略层还是策略内部？定位不清会导致架构层次混乱
3. 选股 pipeline 的标准接口是什么？输入（信号/因子）→ 输出（target_portfolio）的契约如何定义才能让 3 个 sleeve 对接同一 StrategyBook？
4. 候选池从全市场如何收敛到可交易标的？生成→过滤→排序→输出的漏斗如何设计？

### 2.3 约束条件
- charter §3 约束四三维度解耦：选股（what）× 组合权重（how much）× 执行（how）独立优化——选股引擎**只产出 target_portfolio 候选与信号**，不越界到仓位与执行（[20 §1.4](20_first_batch_strategies.md)）
- charter §3 约束五少而精：个人系统分层不能过重，L0→L1→L2-C 三层须论证必要性（见 §5 过度工程审查）
- T+1 结算：选股信号盘后/盘中产出，次日开盘执行，pipeline 须容忍"信号产出→执行"跨日时滞
- A 股不能做空：选股只产多头候选，不产空头信号
- 与 regime 正交：选股不读 regime 输出，只收 budget 数字（[20 §1.4](20_first_batch_strategies.md)）

## 3. 决策：L0→L1→L2-C 三层选股引擎架构

### 3.1 分层总览

选股引擎按数据→因子→特色信号三层组织，对应作战地图 BM-SEL 环节的层归属：

| 层 | 职责 | 对应 BM-SEL 环节 | 施工态 | 输出 |
|---|---|---|---|---|
| **L0 数据接入层** | miniQMT Tick(3s) + 盘前定时，把行情/新闻/另类数据经事件总线写入分层时序存储（Redis 热+ClickHouse 温+Parquet 冷） | BM-SEL-01 等 | 🟦 production | 标准化行情/因子原料 |
| **L1 因子工厂层** | 盘前全量+盘中增量双模计算，产出因子池（设计容量≥150，运行≤64），叠加分布特征工程 | BM-SEL-02 等 | 🟦 production | 因子池 + FactorSignal |
| **L2-C A股特色信号层** | A 股特有的游资情绪/量化强度/双引擎融合/板块轮动/Survival 等特色信号（C=Characteristic/China） | BM-SEL-22~27 | 🟦 production（打板链）+ 🟧 design（板块/Survival 等） | SynthesizedSignal + 决策分类 |

> **层间数据流接口契约（v1.1.1 补，施工环节算法补全）**：三层之间通过标准接口契约解耦，每层只消费上层的标准化输出：
>
> | 接口 | 上游→下游 | 契约签名 | 触发条件 |
> |---|---|---|---|
> | L0→L1 | 数据接入→因子工厂 | `FactorMaterial(as_of_date, symbol, fields: dict)` 写入分层时序存储 | Tick 3s 实时 + 盘前定时批量 |
> | L1→L2-C | 因子工厂→A股特色信号 | `FactorSignal(symbol, factor_id, value, rank, ic_lag, timestamp)` 经事件总线发布 | 盘前全量 + 盘中增量（IC 衰减触发） |
> | L2-C→sleeve | A股特色信号→StrategyBook | `SynthesizedSignal(symbol, score, confidence, decision_class, metadata)` 写入 sleeve StrategyBook | sleeve 频率（打板盘中/多因子盘后/事件触发） |
>
> **降级链路触发判据**：L0 数据源断流（连续 3 个 Tick 缺失）→ L1 降级为硬编码均线规则；L1 因子层全失效（活跃因子 IC 均值 < 0.01 持续 5 日）→ L2-C 降级为仅游资情绪引擎（MOD-SIG-033 单引擎）；L2-C 双引擎融合失效 → 打板 sleeve 降级为仅短线评分卡（MOD-SIG-023）。降级是 sleeve 内部行为，不破坏 firm 层统一风险框架。

> **L2-C 板块轮动→SynthesizedSignal.score 映射（v1.1.16 补，跨文档算法交接完整性审查——链路 1 缺口修复）**：
>
> [22号](22_sector_rotation_spec.md) 板块轮动输出 RRG 四象限信号（Leading/Improving/Weakening/Lagging）+ 板块强度评分（0-100）+ 回踩质量 A/B/C，但 L2-C→sleeve 接口契约 `SynthesizedSignal(symbol, score, confidence, decision_class, metadata)` 中的 `score` 如何从 RRG 象限+强度分推导此前未形式化。现补全映射公式：
>
> ```
> # 板块轮动 sleeve 的 score 映射（G06 板块轮动激活后适用，当前 design 态）
> SECTOR_QUADRANT_BASE = {
>     "Leading":   0.8,   # 领先象限：板块相对强度上行+动量上行
>     "Improving": 0.6,   # 改善象限：板块相对强度下行+动量上行（触底回升）
>     "Weakening": 0.3,   # 减弱象限：板块相对强度上行+动量下行（见顶回落）
>     "Lagging":   0.1,   # 滞后象限：板块相对强度下行+动量下行
> }
> PULLBACK_QUALITY_BONUS = {"A": 0.15, "B": 0.05, "C": -0.05}  # 回踩质量加成
>
> score = clamp(SECTOR_QUADRANT_BASE[quadrant] + strength_score/100 * 0.2 + PULLBACK_QUALITY_BONUS[quality], 0.0, 1.0)
> # strength_score/100 * 0.2：板块强度分 0-100 归一化后乘 0.2 系数，使强度在象限基准上微调（±0.1）
> # 例：Leading(0.8) + 强度 80(0.16) + 回踩 A(0.15) = 1.11 → clamp → 1.0（满配）
> # 例：Improving(0.6) + 强度 50(0.10) + 回踩 B(0.05) = 0.75
> ```
>
> - **score 语义**：[0,1] 区间的板块轮动综合评分，Leading 象限+高强度+优质回踩 → score 接近 1.0（强买入信号），Lagging 象限+低强度+差回踩 → score 接近 0.1（弱信号/回避）。与打板 sleeve 的双引擎融合 score（6 类决策映射）和多因子 sleeve 的因子打分 score 在 SynthesizedSignal 中统一为 [0,1] 语义
> - **板块 overlay 降级影响**：[30号](30_multi_strategy_concurrency.md) §2.5.1 定义 `sector_overlay_active=False`（板块轮动 overlay 未激活）时，行业偏离约束从 ±15% 收紧为 ±10%。此时 L2-C 板块轮动 sleeve 不产出 SynthesizedSignal（板块轮动属 design 态，overlay 未激活=不参与选股打分），行业偏离由 firm 层 [32号](32_firm_risk_aggregator.md) §2.5.1 用 ±10% 硬约束兜底。板块轮动激活后（G06 定型+实盘校准），行业偏离放宽至 ±15%，L2-C 产出 SynthesizedSignal 喂入选股评分
> - **当前施工态**：板块轮动属 🟧 design（G06 待定型），上述映射公式为 **G06 定型时的施工参考**，参数（象限基准值/强度系数/回踩加成）待 G06 回测校准后最终确定

> **why 三层而非两层或四层**：L0/L1 是通用量化地基（数据→因子，任何市场都需），L2-C 是 A 股特色差异化层（游资打板/连板梯队/情绪周期是 A 股独有，海外 alpha 工厂无此层）。三层 = "通用地基 + 本土特色"的最低完整切分；两层（数据+信号）会让因子计算与特色信号混杂、归因不清；四层（再拆"组合信号层"）会与 StrategyBook/firm 层职责重叠（违反 charter 约束四）。实证支撑：Medallion Architecture 三层（Bronze/Silver/Gold）"splitting into 3 layers makes debugging fast"——三层是调试效率与切分清晰度的甜点（[lukastymo 2026-05](https://lukastymo.com/posts/029-software-engineer-value-investing-magic-formula/)）。**2026 前沿印证**：[国联民生金工 2026-07-16 AAAI/ICLR 综述](https://finance.sina.com.cn/wm/2026-07-16/doc-inihyyvy4515788.shtml)——AI 量化从"调用通用模型"转向"围绕金融约束重构模型"，三层正是其工程落地（L0 处理延迟/L1 处理非平稳性/L2-C 处理本土特色）；LLM 在线/离线边界见 §5.4。

### 3.2 决策①：双引擎融合定位 = 打板策略内部融合，非跨策略层

> 对齐 [00_index G05 讨论要点①](00_index_trading_decision.md) / [30 §7.3](30_multi_strategy_concurrency.md) / [20 §2.2](20_first_batch_strategies.md)

**裁定**：双引擎融合（BM-SEL-25，MOD-SIG-035 `dual_engine_fusion_decision_engine.py`）是**打板策略 sleeve 内部**的融合，**不是**跨策略层的统一融合器。

**why**：
- 双引擎 = 游资接力情绪引擎（MOD-SIG-033）+ 量化短线强度引擎（MOD-SIG-034），两者都是**短线/盘中**信号，服务打板 sleeve 的高换手场景
- 多因子 sleeve（盘后横截面因子）与事件驱动 sleeve（离散事件）的信号频率/持仓周期与双引擎不匹配——把双引擎抬到跨策略层会强行统一三种异构信号，违反 charter 约束五（禁止堆砌相似策略制造多策略假象的反面：禁止强行统一异构策略）
- 跨策略层的统一在 firm 层（MOD-POS-021 FirmRiskAggregator 求和+裁剪），不在选股层——选股层各 sleeve 独立产 alpha，firm 层做风险聚合（[30 §2.2/§4.2](30_multi_strategy_concurrency.md)）

**边界**：双引擎融合的输出（6 类决策：主升龙头/二进三/跟风/复苏/伪强/地天反包）作为打板 sleeve 的 alpha 信号喂给打板 StrategyBook，不喂给多因子/事件 sleeve。

### 3.3 决策②：L0→L1→L2-C 分层 = 通用地基 + A股特色

> 对齐 [00_index G05 讨论要点②](00_index_trading_decision.md) / [battle_map_05](../battle_map/battle_map_05_stock_selection.md) 层归属

**L0 数据接入层**（production）：
- 触发：每 3 秒 miniQMT Tick + 盘前定时
- 数据流：外部源（miniQMT/iFind/tushare/BaoStock）→ 事件总线 → 分层时序存储（Redis 热+ClickHouse 温+Parquet 冷）
- 事件契约：TickEvent / SignalEvent / DecisionEvent / ExecutionEvent / RiskEvent / SystemEvent 统一
- 降级：数据源断流→仅执行卖出指令（不新增仓位）

**L1 因子工厂层**（production）：
- 触发：盘前全量 + 盘中增量双模计算
- 因子治理：池容量 n_max=64（活跃 60+休眠 4）、入池 min_ic_to_enter=0.02、IC 末位淘汰、生命周期 8 状态机（[20 §2.3 施工回填](20_first_batch_strategies.md)）
- 分布特征工程：滞后项/交互项/滚动统计量/签名方法 Signature，喂密度预测模型
- 降级：因子层全失效→硬编码均线规则

> **L1 因子配比与衰减监控施工补全（v1.1.0 补，施工环节算法补全）**：
>
> **① 因子配比——人工为主 + 衍生为辅**：[私募札记 因子重本源 2026](http://m.toutiao.com/group/7669707690368565795/) 保守型量化投研框架实证——因子挖掘长期维持 **85%-90% 人工挖掘 + 10%-15% 衍生补充** 固定配比，人工因子逻辑清晰、行情失效时可快速定位归因；衍生因子执行月度复盘，收益衰减直接替换下线。因子权重分层：**75% 高频量价因子**（捕捉短期资金交易行为）+ **15% 基本面因子**（排雷规避基本面恶化）+ **10% 另类情绪因子**（辅助补充）。**对本项目 L1 的施工启示**：[20 §2.3](20_first_batch_strategies.md) "少而精 8-15 个因子"应进一步明确配比——建议人工因子为主（逻辑可解释、失效可归因），LLM/RL 衍生因子为辅（[20 §6 待定问题"LLM alpha 挖掘闭环"](20_first_batch_strategies.md) 产出的因子进衍生池，月度复盘替换），与 8 状态生命周期治理（research→...→retired）天然契合。[华泰证券金工 2026-08-02](https://m.hibor.com.cn/wap_detail.aspx?id=5dc71a9949bce52f3398c30caaf270dd) 机构级实证：**全频段融合因子**（量价+基本面+另类多频段融合）TOP 层年化超额 27.37%、5 日 RankIC 均值 11.2%，AI 中证 1000 指增年化超额 20.33%、IR 3.10——印证 L1 因子工厂层"全频段融合"是机构级 alpha 主源（非单一频段）。
>
> **② IC 衰减四参数监控框架**：当前 `ic_decay.py`（MOD-L02-004）已实现 IC 衰减曲线 + 半衰期计算，[CSDN 2026-07-11](https://blog.csdn.net/wencaitouzi/article/details/148829424) / [gs-quant IC 衰减曲线](https://blog.csdn.net/gitblog_00055/article/details/151774547) 给出完整四参数框架应作为 L1 衰减监控的标准指标：
> - **初始 IC 值**（IC at lag=1）：衡量因子短期预测能力
> - **半衰期**（IC 衰减至初始值 50% 所需天数，线性插值）：衡量因子持续性
> - **衰减斜率**（曲线平均下降速率）：衡量衰减速度
> - **长期 IC 均值**（如 60 日平均 IC）：衡量因子长期有效性
>
> 四参数联动判据：半衰期<10 天 → 缩短调仓周期（动态持仓周期 `min(half_life, 5)`，夏普 1.2→1.8 实证）；初始 IC>0.05 但长期 IC 均值<0.02 → 因子拥挤告警（[20 §2.3 microalphas](20_first_batch_strategies.md) arbitrage/crowding 机制）；衰减斜率突变（CUSUM >2σ）→ 进入观察态。此四参数框架是对 [20 §2.3](20_first_batch_strategies.md) 因子衰减监控的 L1 层落地细化。

> **盘中增量双模计算触发条件与 Signature 方法（v1.1.1 补，施工环节算法补全）**：
>
> **① 盘中增量双模计算触发条件**：当前 §3.3 只写"盘前全量 + 盘中增量双模计算"，未明确增量触发条件。触发判据：① 因子新鲜度衰减——因子 `current_ic < initial_ic * 0.7`（[CSDN 2026-07-11](https://blog.csdn.net/wencaitouzi/article/details/148829424) 新鲜度监控阈值）时触发盘中增量重算；② 价格冲击——标的日内涨幅 >3% 或成交量 >5 日均值 2 倍时触发该标的因子增量重算；③ 事件触发——事件源（[20 §2.4](20_first_batch_strategies.md) 事件源）发布事件时触发相关标的因子增量重算。增量计算只重算受影响标的（非全市场），算力节省 80%+。
>
> **② Signature 签名方法解释**：当前 §3.3 写"分布特征工程：滞后项/交互项/滚动统计量/签名方法 Signature，喂密度预测模型"但未解释 Signature 是什么。**Signature 方法** = 路径签名（Path Signature），源自粗路径理论（rough path theory）——将时间序列路径编码为不变量序列（签名变换），捕捉路径的几何特征（水平/面积/体积等），不依赖时间对齐。金融应用：将价格/成交量路径转为签名特征向量，喂密度预测模型（[91_density_prediction](91_density_prediction.md)）预测次日 8 态走势。优势：① 可变长路径编码为定长向量；② 捕捉高阶交互（传统滞后项只捕一阶）；③ 对时间扭曲鲁棒。工程实现参考 `signatory` 库（PyTorch 签名计算）。
>
> **③ 25 号多因子细节算法交叉引用**：[25_multifactor_strategy_detail](25_multifactor_strategy_detail.md) v1.9.0 已登记四项选项之外更好算法（IC 半衰期加权/GAN_GRU/Bayesian 变点/Bootstrap CI），与本备忘 §3.3 L1 因子工厂层的演进路径闭合——详见 [20 §2.3 25 号交叉引用](20_first_batch_strategies.md)。L1 因子工厂层的 production 基线（因子池 n_max=64 + 8 状态生命周期 + IC 衰减四参数监控）已施工，远期演进（Hubble AST 沙箱 + AlphaEvolve MAP Elites，见 [20 §2.4 LLM alpha 挖掘新框架](20_first_batch_strategies.md)）登记为 §6 待裁定-7。

> **④ 2026-08 LLM alpha 挖掘新框架（v1.1.4 补，选项之外更好算法——当前 §6 待裁定-7 仅引 Hubble/AlphaEvolve/XAlpha，缺 2026-08 新出的 AlphaMemo/FactorMiner/MAGE/AlphaAgent 四框架）**：
>
> **AlphaMemo SSPM（结构化搜索过程记忆）**（[arXiv 2606.20625, 2026-05-26](https://arxiv.org/pdf/2606.20625)）：不只记忆最终因子或完整轨迹，而是记录 **edit motif 级别**的可复用证据（哪些编辑模式在特定父因子上下文下有效/失败）；从 AST 差异提取 edit motifs；置信度门控残差记忆（在 search-ledger 先验之上）；**非对称否决控制**（高置信负模式可否决，正模式仅软提升）；CSI 500 和 S&P 500 验证。**对 L1 因子工厂的启示**：AlphaMemo 是 XAlpha 记忆层的精细化升级——XAlpha 的 A/B/C 三层分类（OHLCV 资格/机制家族/研究原型）是粗粒度记忆，AlphaMemo 的 edit motif 级记忆可复用"哪些因子编辑操作（如加滞后项/取对数/交互项）在何种上下文下有效"，比 XAlpha 更精细。与 [CogAlpha](https://arxiv.org/html/2511.18850v4) 多 agent 质量检查互补——AlphaMemo 提供"失败模式记忆"，CogAlpha 提供"质量校验"。
>
> **FactorMiner Ralph Loop（retrieve-generate-evaluate-distill）**（[ICLR 2026](https://openreview.net/pdf?id=TTsecyqrW3)）：Ralph Loop 范式 + 模块化 Skill 架构（封装 IC 筛选/相关性检查/去重/全验证为可执行工具）+ 结构化经验记忆（成功模式 + **禁区**——与现有库高互相关的因子家族）；**全局因子库视角**：候选因子如何补充现有库而非孤立优化。**对 L1 因子工厂的启示**：FactorMiner 的"禁区"概念与本项目 [factor_pool_manager.py](20_first_batch_strategies.md)（MOD-L02-018）IC 末位淘汰 + n_max=64 容量上限天然契合——新因子入池前检查与现有 64 因子的相关性，高相关的因子家族进"禁区"不入池。这是对当前 IC 末位淘汰的**入池前预防**（当前是入池后 IC 衰减才淘汰，FactorMiner 是入池前相关性检查拦截）。
>
> **MAGE（MAP-Elites for Alpha Generation）**（[GitHub 2026-04-30](https://github.com/joconno2/MAGE)）：MAP-Elites 质量-多样性进化算法应用于 Alpha 生成——2D 行为网格（turnover × market correlation），每格保留该行为 profile 下最优 alpha；RL 奖励含个体 alpha 质量+"synergy"项鼓励生成集多样性；AlphaGen 在 S&P 500 Sharpe 3.96，CSI300 0.76。**对 L1 因子工厂的启示**：MAGE 是 AlphaEvolve MAP Elites 的金融场景聚焦版——AlphaEvolve 的行为维度是通用 metric，MAGE 明确用 turnover × market correlation 两维（低换手×低相关=最优区）。与本项目 charter 约束五"少而精+差异性"对齐——MAGE 的 2D 网格可直接映射为因子的"换手率×相关性"筛选器。
>
> **AlphaAgent 三大正则化**（[arXiv 2502.16789, KDD 2025](https://arxiv.org/pdf/2502.16789)）：**(i) 原创性强化**（基于 AST 相似度对现有 alpha 库，抗 alpha decay）、**(ii) 假设-因子对齐**（LLM 评估市场假设与生成因子的语义一致性，防"幸运因子"）、**(iii) 复杂度控制**（AST 结构约束防过拟合）；CSI 500 和 S&P 500 四年验证抗 decay 能力。**对 L1 因子工厂的启示**：AlphaAgent 三大正则化是残差代数（[20 §2.4 arXiv 2608.07349](20_first_batch_strategies.md)）思路的工程化升级——残差代数在合成层保持表示身份，AlphaAgent 在生成层就约束原创性/对齐/复杂度。与 [Beyond Prompting](https://arxiv.org/html/2603.14288v1) 经济正则化"幸运因子"过滤器互补。
>
> **AlphaSAGE 结构感知因子生成**（[arXiv 2509.25055v3, 2026-05-19](https://arxiv.org/pdf/2509.25055v3)）：RGCN（Relational Graph Convolutional Network）结构编码器捕捉因子 AST 的数学结构 + GFlowNet 生成策略（从空 AST 逐步施加 action 生成完整因子）+ 多维度奖励函数（`reward = r_ic + 0.2·r_sa + 0.3·r_nov`，IC 收益 + 结构对齐 + 新颖性）。**对 L1 因子工厂的启示**：AlphaSAGE 是 MAGE 的结构感知升级——MAGE 用 turnover×correlation 2D 行为网格做多样性，AlphaSAGE 用 RGCN 做 **AST 结构嵌入**多样性。两者互补：FactorMiner 禁区当前基于 IC 相关性检查（数值相关），AlphaSAGE 的 RGCN 编码器可补**结构相关**检查（两个因子 IC 不同但 AST 结构相似=同一思路换皮，应进禁区）。与 [CogAlpha](https://arxiv.org/html/2511.18850v4) 多 agent 质量检查互补——AlphaSAGE 在生成层约束结构多样性，CogAlpha 在校验层约束代码质量。
>
> **结论**：§6 待裁定-7 LLM alpha 挖掘闭环的工程路径=八框架完整工具链（Hubble/AlphaEvolve/XAlpha/AlphaMemo/FactorMiner/MAGE/AlphaAgent/AlphaSAGE，逐框架分析与链接见上文④各块及 §8.5）。本项目远期演进应采 Hubble 架构为骨架（AST 沙箱确保可执行），FactorMiner 禁区机制接入 [factor_pool_manager.py](20_first_batch_strategies.md) 入池前相关性检查（IC 相关 + AlphaSAGE RGCN 结构相关双层），AlphaMemo edit motif 记忆接入因子治理层经验累积。详见 [20 §2.4 LLM alpha 挖掘新框架](20_first_batch_strategies.md)。
>
> **⑤ L1 深度学习 baseline 候选：Cross-Sectional LSTM（v1.1.6 补，施工环节算法补全——当前 §3.3 L1 因子工厂是"人工因子 + IC 评估 + 8 状态治理"纯线性框架，缺非线性深度学习预测 baseline 作为远期对照）**：[Cross-Sectional Heterogeneity LSTM arXiv 2608.05755 2026-08-07](https://arxiv.org/html/2608.05755v1)（Julius Döbelt）——在标准 LSTM 上加 **learnable sector embeddings**（捕获截面异质性，A 股行业轮动适配）+ 宏观金融协变量 + label smoothing/dropout/gradient clipping 正则。S&P 500 日频方向预测实证：超越 basic LSTM / Random Forest / buy-and-hold，预测信号由**短期反转因子 + 行业动量因子**驱动（与 A 股已知有效因子一致），可解释性通过潜空间可视化分析模型如何区分行业。**对 L1 因子工厂的启示**：当前 L1 是纯线性 IC 加权合成（[MOD-L03-001 signal_synthesizer](20_first_batch_strategies.md)），Cross-Sectional LSTM 可作 **Phase 3+ 非线性预测 baseline**——sector embedding 直接适配 A 股行业轮动（与 L2-C 板块轮动 G06 协同），短期反转+行业动量双因子结构与 [20 §2.3](20_first_batch_strategies.md) 因子族对齐。**过度工程审查**：LSTM 非线性预测属远期增强（当前 L1 production 线性框架已够 MVP），不纳入首批施工——登记为 §6 待裁定-9，G09 远期评估深度学习 baseline 接入 L1（须因子工厂治理层稳定运行 6+ 月后）。

**L2-C A股特色信号层**（混合 production/design）：
- **打板链**（🟦 production）：游资接力情绪（MOD-SIG-033，6 因子+情绪周期 4+1 阶段）→ 量化短线强度（MOD-SIG-034，6 维 A~E 评级）→ 双引擎融合（MOD-SIG-035，自适应权重+6 类决策）
- **板块轮动**（🟧 design）：3×3×3 立方体（量能=第 3 维）+ 日历修饰器 + 体制转换检测 + 回踩质量 A/B/C 等级（BM-SEL-08/09，G06）
- **Survival/密度预测**（🟧 design）：止盈止损时间预测、T+1 次日 8 态走势预测（远期，[91_density_prediction](91_density_prediction.md)）

**作战地图环节映射**

| BM 环节 | 环节名 | 本篇承载小节 | 状态 |
|---|---|---|---|
| BM-SEL-12 | 分布特征工程 | §3.3（L1 因子工厂层"分布特征工程：滞后项/交互项/滚动统计量/签名方法 Signature，喂密度预测模型" + v1.1.1 补② Signature 路径签名方法解释，signatory 库参考） | design待施工 |

### 3.3.1 信号工厂与信号聚合器（远期登记层，v1.1.19 新增——BM-SEL-02-J/L 闭合）

> 对齐 [battle_map_05](../battle_map/battle_map_05_stock_selection.md) BM-SEL-02-J（信号工厂子阶段流水线）/ BM-SEL-02-L（信号聚合器架构），均为 🟧 design 态（planned，D_SIGNAL 域）。本节只做**远期登记**（定位+裁定+契约），不施工。

**① BM-SEL-02-J 信号工厂子阶段流水线（design）**：
- **定位**：L1 因子工厂层→L2-C 特色信号层之间的**信号加工层**（作战地图层归属 L2-A 信号生成层）——消费因子值（BM-SEL-02）+ 市场状态（BM-SEL-03）+ 主力行为（BM-SEL-05），产出标准化信号（含方向/强度/置信度）喂下游投票/聚合。
- **裁定**：远期登记，**当前不施工**。理由：① 当前首批 3 sleeve 各自在 sleeve 内部完成"因子/信号→评分"加工（打板链 MOD-SIG-023/033/034/035 已 production 闭环、多因子 `multifactor_synthesis.py` 已 production），无独立信号加工层的现实需求——新增一层会与 §3.5 统一接口内部实现重叠，属 §4.2 已拒绝的"四层切分"变体；② 九子阶段（预处理→信号化→合成→过滤→增强→校准→投票→聚合→输出）的切分在多信号源真正并发前是仪式性分层（charter 约束五）。
- **契约（远期建设项登记）**：九子阶段流水线——`因子预处理 → 单因子信号化 → 多因子合成 → 信号过滤 → 信号增强 → 信号校准 → 信号投票 → 信号聚合 → 信号输出`；输入=FactorSignal（§3.1 L1→L2-C 接口），输出=标准化信号 `(symbol, direction, strength, confidence)`；降级=单子阶段失效→跳过该阶段输出未加工信号，流水线不中断。
- **重评条件（激活门槛）**：首批策略上线后出现**信号冲突/口径漂移实例 ≥3 例**（同一标的被多 sleeve 以不同口径产出冲突信号，归因确认缺统一加工层所致）→ 启动信号工厂层定型讨论。

**② BM-SEL-02-L 信号聚合器架构（design）**：
- **定位**：信号投票/加权（BM-SEL-02-K）之后的**组合级聚合出口**——把加权信号聚合为最终组合决策输入（标的清单+权重+触发条件），喂下游 BM-BUY-01 多情景对策与 BM-SEL-20 多策略交叉投票。
- **裁定**：远期登记，**当前不施工**。理由：① 当前跨 sleeve 的聚合裁决已在 firm 层（MOD-POS-021 FirmRiskAggregator 求和+裁剪，§3.2/§3.7）落地，选股层再设聚合器会与 firm 层职责重叠（§4.2 拒绝理由同构）；② 本登记**承接 [32_firm_risk_aggregator](32_firm_risk_aggregator.md) §2.7 既有声明**——"Kalman 信号融合 ❌ 远期：策略层信号融合归 G05 信号工厂，非 G13 职责"。32 号已把信号融合职责划给 G05，本篇作为 G05 真源备忘予以登记承接：若远期确需策略层信号融合，落在本节信号聚合器（G05），不落 firm 层（G13）。
- **契约（远期建设项登记）**：三段式——**多信号归一化**（异构信号统一 [0,1] 语义）→ **优先级仲裁**（风险信号 > 机会信号，硬约束优先）→ **组合级输出**（标的清单+权重建议+触发条件+时序）；消费=投票加权信号（BM-SEL-02-K）+ 风险约束（BM-RC-*）+ 仓位约束（BM-POS-*）；降级=聚合器失效→直通最近一次有效聚合结果（缓存）+ 告警。
- **重评条件**：与 BM-SEL-02-J 同一激活门槛（信号冲突/口径漂移 ≥3 例）；另加：firm 层求和+裁剪被实证无法处理信号级冲突（如两 sleeve 对同一标的方向相反且各持高置信）时重评。

### 3.4 决策③：量化强度评级 = 打板 sleeve 的量化引擎输入

> 对齐 [00_index G05 讨论要点③](00_index_trading_decision.md) / BM-SEL-24

**裁定**：量化短线强度评级（MOD-SIG-034 `quant_short_term_strength_engine.py`，production/stable）是**打板 sleeve 双引擎融合的量化引擎输入**，6 维 0-100 分（价格动量 20/行业强度 15/相对强度 20/资金 15/技术 20/风险 10）+ A~E 五级评级 + 6 类输出。

**why 独立评级而非直接用游资情绪**：游资情绪引擎（MOD-SIG-033）捕捉"人"的接力情绪，但对量化砸板（2026 年量化成游资最大对手盘，[20 §2.2 2026 市场语境](20_first_batch_strategies.md)）不敏感；量化强度评级用价格动量/资金/技术等客观维度补盲，两引擎融合权重由情绪周期阶段自适应（冰点时量化 70%、主升时游资 70%）——单一引擎都有盲区，融合是打板 alpha 的核心。

**边界**：量化强度评级**仅服务打板 sleeve**，多因子 sleeve 用横截面因子打分（不共用此评级），事件 sleeve 用事件冲击信号。三 sleeve 的"强度"概念各自定义，不在选股层强行统一。

> **6 维权重校准方法（v1.1.2 补，施工环节算法补全）**：当前 6 维权重（价格动量 20/行业强度 15/相对强度 20/资金 15/技术 20/风险 10）是经验设定，未说明校准方法。校准路径两条：
> - **路径 A·IC 加权**（与 [20 §2.3](20_first_batch_strategies.md) 因子工厂 IC 加权合成对齐）：将 6 维各视为子因子，计算各自滚动 60 日 RankIC，按 `weight_i = IC_i / Σ|IC_j|` 归一化为权重——IC 高的维度自动获得更高权重，IC 衰减的维度自动降权。优势：与因子工厂治理层（MOD-L02-018）的 IC 末位淘汰逻辑一致，校准自动化。
> - **路径 B·SHAP 归因**（机器学习反推）：用 LightGBM 训练"6 维→次日收益"模型，SHAP 值反推各维度贡献度作为权重。优势：捕捉非线性交互（IC 加权只捕线性），劣势：需离线训练+定期重训。
> - **重校准频率**：月度（与 §3.3 IC 衰减四参数半衰期监控对齐），CUSUM >2σ 触发即时重校准。
> - **MVP 优先**：首版用经验权重（当前 20/15/20/15/20/10）+ 路径 A（IC 加权）作为 Phase 2 演进，路径 B（SHAP）为远期。登记为 §6 待裁定-8。

### 3.5 决策④：选股 pipeline 标准接口

> 对齐 [00_index G05 讨论要点④](00_index_trading_decision.md)

**标准接口契约**（每个 sleeve 实现同一接口，差异化在内部）：

```
输入：SignalInput(as_of_date, universe, regime_budget)   # regime_budget=数字，非 regime 状态
处理：sleeve.select(SignalInput) → SelectionResult
输出：SelectionResult(target_portfolio: list[TargetPosition], signals: list[Signal], confidence: float, metadata: dict)
```

- **target_portfolio**：`list[TargetPosition(symbol, target_weight, signal_source, urgency)]`，urgency∈{immediate, next_open, gradual} 对应打板/多因子/事件的不同执行时序
- **signals**：原始信号留痕，供归因与 G07 相关性验证
- **confidence**：sleeve 自评置信度，喂 firm 层 PerformanceScore（[30 §2.2](30_multi_strategy_concurrency.md)）
- **metadata**：sleeve 私有信息（如打板的情绪周期阶段、多因子的因子贡献度、事件的冲击衰减阶段）

> **confidence 算法待裁定（v1.0.1 补）**：当前接口只定义 confidence∈[0,1] 的语义（sleeve 自评置信度），但**算法未定**。2026 前沿提供三条候选路径：① [AlphaSchema 2026-08-01](https://ubos.tech/alphaschema-exploring-the-space-of-trading-semantics-for-llm-based-alpha-mining/) surrogate model 预测 reward 的方差——surrogate learner 估计 schema 的预期 Sharpe，方差小=高 confidence；② [Janus-Q arXiv 2026-02](https://arxiv.org/html/2602.19919v2) 分层门控奖励建模——LLM 事件标签的 confidence 直接作为 gating 信号（错误解读如"否认收购"误读为利好是主要亏损源，[HF Trading Book 2026-06](https://hftradingbook.com/strategies/news-trading)）；③ 经验贝叶斯 shrinkage——sleeve 历史 hit rate × 当前信号强度 shrink 到先验均值。三条路径非互斥：打板 sleeve 可用②（情绪周期阶段 confidence）、多因子 sleeve 可用①（因子 surrogate variance）、事件 sleeve 可用②（LLM 事件 confidence gate）。具体算法登记为 §6 待裁定-5。
>
> **confidence 算法第四候选（v1.1.0 补，事件 sleeve 专属）**：[Vortex Capital 2026-05 PEAD Inversion](https://www.vortexcapitalgroup.com/post/the-mega-cap-pead-inversion-when-the-reaction-is-the-trade-and-when-it-is-the-trap)（[26 §2.4](26_event_driven_strategy_detail.md) 已详述）提供事件 sleeve confidence 的第四条路径——**极端反应 confidence 衰减**：事件日反应 |reaction|>3% 时，经典 PEAD 延续 confidence 应**衰减至接近 0**（因极端反应后 20 日中位 -5.58% 反转，非延续）；温和反应 |reaction|≤3% 时 confidence 维持正常 PEAD 延续水平。算法：`confidence = base_confidence * (1 if |reaction|<=0.03 else 0.1)`。这与候选②（LLM confidence gate）协同——LLM gate 防误读，PEAD Inversion gate 防极端反应追涨。四候选汇总：打板 sleeve ②（情绪周期阶段 confidence）、多因子 sleeve ①（因子 surrogate variance）、事件 sleeve ②+④（LLM gate + PEAD Inversion gate 双重门控）。

> **SignalInput 字段与 urgency↔convergence_window 映射（v1.1.1 补，施工环节算法补全）**：
>
> **SignalInput 详细字段**（当前 §3.5 只写 `SignalInput(as_of_date, universe, regime_budget)`，未展开）：
> ```
> SignalInput:
>   as_of_date: date              # 信号产出日
>   universe: list[symbol]        # 候选池（漏斗①生成后）
>   regime_budget: float          # regime 风险节流后的 budget 数字（非 regime 状态）
>   signals: list[Signal]         # L2-C 产出的原始信号（打板=双引擎融合6类决策/多因子=因子打分/事件=事件冲击）
>   metadata: dict                # sleeve 私有上下文（如打板情绪周期阶段、多因子因子贡献度、事件冲击衰减阶段）
> ```
>
> **urgency↔convergence_window 映射**（当前 §3.5 定义 urgency∈{immediate, next_open, gradual} 但未与 convergence_window 对齐）：
>
> | urgency | 含义 | convergence_window | sleeve | 执行时序 |
> |---|---|---|---|---|
> | immediate | 盘中立即 | 1-2 天 | 打板 | T 日盘中买入，T+1 卖出 |
> | next_open | 次日开盘 | 2-3 天 | 事件驱动 | T+1 开盘买入，2-3 天收敛 |
> | gradual | 逐步建仓 | 3-5 天 | 多因子 | T+1 起 3-5 天逐步建仓 |
>
> urgency 由 sleeve 根据信号强度与持仓周期自决，convergence_window 在 StrategyBook（[30 §2.2](30_multi_strategy_concurrency.md) MOD-POS-020）持有并触发 BudgetChangeHandler（MOD-POS-022）三级升级。

**why 统一接口**：3 sleeve 异构（信号源/频率/周期全不同，[20 §2.5 差异化矩阵](20_first_batch_strategies.md)），但须对接同一 firm 层（MOD-POS-021）——统一接口是 Model A"统一 firm 风险框架 + 差异化 sleeve"（[20 §1.4](20_first_batch_strategies.md)）的工程落地。差异化在接口实现内部，统一在接口签名。

### 3.6 决策⑤：候选池生成→过滤→排序→输出（漏斗模型）

> 对齐 [00_index G05 讨论要点⑤](00_index_trading_decision.md) / [battle_map_05 漏斗 L1→L2](../battle_map/battle_map_05_stock_selection.md)

**四阶段漏斗**（各 sleeve 按自身频率执行，打板盘中实时、多因子盘后日频、事件触发不定期）：

| 阶段 | 打板 sleeve | 多因子 sleeve | 事件 sleeve |
|---|---|---|---|
| **① 候选池生成** | 全市场涨停标的 + 连板梯队（L0 涨停数据） | 全市场沪深 A 股（L1 universe） | 事件触发标的动态生成（L0 新闻/公告） |
| **② 过滤** | 排除 ST/*ST/退市风险/流动性失效；流通市值 10-50 亿黄金区间（[20 §2.2](20_first_batch_strategies.md)） | 排除 ST/*ST/次新(<60天)/日均成交额低于阈值 | 排除 ST/流动性失效；事件置信度低于阈值过滤 |
| **③ 排序** | 双引擎融合评分（MOD-SIG-035，6 类决策优先级） | 横截面因子打分（IC 加权/正交化，G09） | 事件冲击评分 × 衰减曲线阶段（[20 §2.4](20_first_batch_strategies.md)） |
| **④ 输出** | target_portfolio（urgency=immediate/next_open，T+1 次日卖） | target_portfolio（urgency=gradual，3-5 天收敛） | target_portfolio（urgency=next_open，2-3 天收敛） |

**漏斗容量**（[battle_map_05](../battle_map/battle_map_05_stock_selection.md)）：全市场 ~5000 → L1 因子过滤 ~1200 → L2-C 精筛 300 → sleeve 排序输出 50 → firm 层裁剪后实仓（受 budget 约束）。

> **漏斗三层级 BM 环节映射（v1.1.19 补，BM-SEL-16/17/18 闭合——三环节由登记级升级为已覆盖）**：
>
> **① BM-SEL-16 分级指标过滤（design）——漏斗 L0/L1 入口（~7000→~1200）**：
> - **定位**：候选池入口的**排除型过滤器**（对应上文漏斗容量链"全市场→L1 因子过滤 ~1200"的上游段），只排除不评分，廉价规则先砍量。
> - **裁定**：四机制语义定型 + 执行频率裁定——**日线级选股用盘前批处理即可，作战地图 trigger 的"3 秒级 Tick"语义登记远期**（仅当打板 sleeve 需要盘中增量刷新候选池时启用 Tick 级过滤）。理由：四机制消费的都是日级/低频标记（涨跌停/停牌/ST、上市天数、AUM 分级、弃庄概率），盘前批量计算一次即可覆盖全日；3 秒 Tick 级过滤对多因子/事件 sleeve 无收益，对打板 sleeve 的盘中场景属增强非必需（打板候选池以涨停标的为入口，非全市场）。
> - **契约——四排除机制语义**：**物理排除**=涨跌停/停牌/ST/*ST 标记硬剔除（L0 标记）；**门禁排除**=次新上市 <30 天绝对排除（不参与任何评分）；**分级排除**=成交额/AUM 分级门槛（日均成交额 <500 万、AUM≤100 万级剔除，流动性失效保护）；**概率排除**=庄家弃庄概率 >95% 剔除（消费 BM-SEL-05 主力行为输出）。降级=过滤模块未就绪→仅排除涨跌停/停牌，其余放行。
> - **重评条件**：打板 sleeve 盘中增量候选池需求出现（首板盘中实时识别）→ 3 秒 Tick 级过滤语义激活重评。
>
> **② BM-SEL-17 初筛漏斗（design）——漏斗 L2 入口（~1200→~300）**：
> - **定位**：BM-SEL-16 输出之上的**五维初筛**（对应容量链"L2-C 精筛 300"的入口段），挂接现有 L1 ~5000→1200 容量链的下游收敛段。
> - **裁定**：五维构成定型——**技术**（均线/KDJ/MACD 形态，消费 BM-SEL-02）+ **量价**（量比 >1.5、换手率，L0 行情）+ **板块**（板块强度排名前 30%，L0）+ **主力**（C-011 主力阶段，BM-SEL-05）+ **状态**（C-021 市场状态，BM-SEL-03）。五维均为布尔/门槛式初筛（非评分），60 秒级 trigger 语义同样登记为批处理执行（盘前/盘后批量，盘中不滚动）。
> - **契约**：输入=BM-SEL-16 输出 ~1200 只，输出=~300 只进 BM-SEL-18；降级=初筛未就绪→直接全量进精筛（算力风险告警）。
> - **重评条件**：精筛（BM-SEL-18）实测算力或延迟不可承受时，重评初筛维度加严（量比/板块排名阈值收紧）。
>
> **③ BM-SEL-18 精筛评分（design）——漏斗评分出口（~300→~50）**：
> - **定位**：初筛输出之上的**六要素综合评分**（对应容量链"sleeve 排序输出 50"的上游评分段），Z-score 横截面标准化后降序取 Top ~50。
> - **裁定**：六要素构成定型——**基础评分**（价值 40%/动量 30%/质量 20%/情绪 10% 加权）+ **状态偏移**（C-021，±10% 修正，BM-SEL-03）+ **主力评分**（C-034/C-035，BM-SEL-05）+ **8 态修正**（C-014，BM-SEL-04）+ **拥挤度**（C-045，L4）+ **密度要素**（偏度/峰度/前瞻 VaR 扣分 15%，BM-SEL-13），六要素 Z-score 综合。**8 态要素现状说明**：[90_methodology_open_questions](90_methodology_open_questions.md) §7 已裁定 T+1 次日 8 态预测（BM-SEL-04）**暂缓建设**（52-53% 天花板未突破，远期窄目标重启条件已定义）——当前六要素中 8 态修正项**置 0 不参与**（等效五要素），待 90 号 §7 重评条件满足后恢复接入。
> - **契约**：输入=BM-SEL-17 输出 ~300 只 + 六要素数据源，输出=Z-score 排名 Top ~50 只喂 BM-SEL-19 事件驱动筛选/sleeve 排序；降级=精筛未就绪→等权综合评分。
> - **重评条件**：8 态预测按 90 号 §7 重启条件复活时，重评六要素权重（8 态修正项从置 0 恢复为有权重参与）。

**why 漏斗而非全量**：全量 5000 只逐个跑双引擎/因子打分算力不可行（打板盘中实时要求秒级），漏斗逐级收敛用廉价过滤（市值/流动性）先砍量，昂贵评分（双引擎/因子合成）只跑精筛后标的——这是 alpha 工厂的标准做法（[AlphaFoundry 2026](https://github.com/Rayhanpatel/MSML-602-Final-Project-alphafoundry-ff5-sp500)：Top-K 等权；[jjjojoj/stock-team 2026-03](https://github.com/jjjojoj/stock-team/blob/main/docs/architecture_v3.md)：候选池→硬筛→软筛→排序→前 20）。

> **事件 sleeve 过滤阶段置信度阈值待裁定（v1.0.1 补）**：漏斗"② 过滤"对事件 sleeve 写"事件置信度低于阈值过滤"，但阈值未定。2026 前沿提示：错误解读（如"否认收购"误读为利好）是事件驱动主要亏损源（[HF Trading Book 2026-06](https://hftradingbook.com/strategies/news-trading)），confidence gate 是防误读主要防线。初拟阈值=0.7（LLM 事件标签 confidence<0.7 过滤），但须 G10 事件驱动细节讨论时按事件类型差异化校准（业绩/并购/政策/突发的误读成本不同）。登记为 §6 待裁定-6。

> **漏斗③排序优先级算法（v1.1.2 补，施工环节算法补全）**：漏斗"③ 排序"对打板 sleeve 写"双引擎融合评分（MOD-SIG-035，6 类决策优先级）"但未展开优先级排序算法，此处补全：
>
> **打板 sleeve 6 类决策优先级**（[20 §2.2 施工回填](20_first_batch_strategies.md) MOD-SIG-035 `dual_engine_fusion_decision_engine.py` 6 类输出）：
>
> | 优先级 | 决策类 | 含义 | 排序权重 |
> |---|---|---|---|
> | P0 | 主升龙头 | 双引擎最强输出，情绪周期主升/疯狂态龙头 | 1.0 |
> | P1 | 二进三 | 连板梯队二进三晋级，情绪周期主升态 | 0.85 |
> | P2 | 跟风 | 板块跟风标的，情绪周期发酵态 | 0.65 |
> | P3 | 复苏 | 冰点/反核态复苏信号 | 0.50 |
> | P4 | 伪强 | 量化诱导假强势（须警惕量化砸板） | 0.30 |
> | P5 | 地天反包 | 地天板反包，极端反转 | 0.20 |
>
> **排序算法**：`final_score = fusion_score × priority_weight`，按 final_score 降序排列，受 budget 约束裁剪至 Top-N（打板 sleeve N≤10 受容量硬约束）。同类内按融合评分降序。**与连板/趋势切换协同**（[20 §2.2 v1.4.1 初拟算法](20_first_batch_strategies.md)）：连板模式下 P0-P1 优先级提升（连板接力信号权重 0.8），趋势模式下 P3-P4 优先级提升（趋势龙低吸+断板反包信号权重 0.8）。
>
> **多因子 sleeve 排序**：横截面因子打分降序（IC 加权/正交化，[25_multifactor_strategy_detail](25_multifactor_strategy_detail.md) G09），Top-N 受 budget 约束。
> **事件 sleeve 排序**：`final_score = event_impact_score × decay_phase_factor`，事件冲击评分 × 衰减曲线阶段因子（rising phase day 0-5 factor=1.0→decay phase day 6-15 factor=0.3），降序排列。PEAD Inversion 修正：极端反应（|ORJ|>3%）事件降权（[20 §2.4 ORJ 算法骨架](20_first_batch_strategies.md)）。

### 3.7 决策⑥：与 StrategyBook 对接契约

> 对齐 [00_index G05 讨论要点⑥](00_index_trading_decision.md) / [30 §2.2](30_multi_strategy_concurrency.md)

**对接契约**：选股引擎（sleeve）产出 `SelectionResult` → 写入对应 sleeve 的 StrategyBook（MOD-POS-020）→ StrategyBook 持有 target_portfolio + 粗仓位 → firm 层（MOD-POS-021）求和+裁剪 → BudgetChangeHandler（MOD-POS-022）三级升级收敛。

| 契约项 | 选股引擎职责 | StrategyBook 职责 | 边界 |
|---|---|---|---|
| target_portfolio | 产出（what） | 持有 + 粗仓位（how much 初拟） | 选股不越界到精仓位（Kelly 在 firm 层，[31_position_sizing](31_position_sizing.md)） |
| convergence_window | 不涉及 | 持有 + 按换手率设（打板 1-2/多因子 3-5/事件 2-3 天） | 选股产 urgency，收敛窗口在仓位层 |
| budget | 只收数字 | 持有 + 触发 rebalance | budget 来源在 RegimeMetaAllocator（G15，第二阶段） |
| PnL 归因 | 产出 signals 留痕 | 独立 PnL 归因 | sleeve 独立账本（[20 §4.1](20_first_batch_strategies.md)） |

**why sleeve 不持精仓位**：charter 约束四三维度解耦——选股（what）与仓位（how much）独立优化，sleeve 只产"买什么+粗权重"，精仓位（Kelly/risk parity）在 firm 层统一裁决（[31_position_sizing §1](31_position_sizing.md)）。若 sleeve 自持精仓位会与 firm 层冲突，破坏 Model A 统一风险框架。

## 4. 考虑过的替代方案

### 4.1 双引擎融合作为跨策略层统一融合器 —— 拒绝
- **拒绝理由**：游资/量化双引擎都是短线盘中信号，服务打板 sleeve。把双引擎抬到跨策略层会强行统一打板（盘中实时）、多因子（盘后日频）、事件（不定期）三种异构信号，违反 charter 约束五（[20 §1.4](20_first_batch_strategies.md)）。跨策略统一在 firm 层做风险聚合（求和+裁剪），不在选股层做信号融合
- **处置**：双引擎融合定位为打板 sleeve 内部（§3.2）

### 4.2 L0→L1→L2-C→L3 四层（拆"组合信号层"） —— 拒绝
- **拒绝理由**：L3"组合信号层"会与 StrategyBook（MOD-POS-020）/ FirmRiskAggregator（MOD-POS-021）职责重叠——组合层是 30_multi_strategy_concurrency 的领域，选股层不应越界（charter 约束四）。四层会模糊选股与组合的边界，归因不清
- **处置**：三层 L0→L1→L2-C（§3.1），组合信号在 firm 层

### 4.3 三 sleeve 共用单一选股 pipeline —— 拒绝
- **拒绝理由**：三 sleeve 信号源/频率/周期全不同（[20 §2.5](20_first_batch_strategies.md)），共用单一 pipeline 会丢失差异化。正确做法是统一**接口**（§3.5）+ 差异化**实现**（各 sleeve 内部漏斗不同，§3.6）
- **处置**：统一接口签名，差异化内部实现

### 4.4 全量逐个评分（不漏斗） —— 拒绝
- **拒绝理由**：全市场 5000 只逐个跑双引擎/因子打分，打板盘中实时算力不可行；多因子盘后全量虽可行但浪费算力。漏斗逐级收敛（廉价过滤先砍量，昂贵评分只跑精筛后）是 alpha 工厂标准做法
- **处置**：四阶段漏斗（§3.6）

## 5. 上限定义

### 5.1 架构上限
- 选股引擎 = L0→L1→L2-C 三层，不扩到四层（§4.2）
- 双引擎融合 = 打板 sleeve 内部，不抬到跨策略层（§3.2）
- 三 sleeve 各自实现 SelectionResult 接口，不强行统一内部实现（§3.5）

### 5.2 演进路径
- **第一阶段（当前）**：打板链全 production（L2-C 打板链闭环）、因子工厂治理层全 production（L1 闭环）、事件链仅数据底座（L0 news_collector design）。三 sleeve 载体（StrategyBook 实例化）均未注册，属 G08/G09/G10 细节
- **第二阶段**：补事件链 NLP 管道（[ARCH-NLP-PIPELINE-001](../../05_architecture_issue_registry/architecture_issue_registry.yaml)）→ 事件 sleeve 信号链闭环
- **第三阶段**：补板块轮动（G06）、Survival/密度预测（远期，[91_density_prediction](91_density_prediction.md)）→ L2-C 全闭环

### 5.3 为何这是上限
- 三层是"通用地基 + 本土特色"的最低完整切分，多于三层越界组合层（§4.2）
- 三 sleeve 覆盖高/低/中换手率 + 小/大/中容量 + 情绪/横截面/事件三类 alpha（[20 §4.3](20_first_batch_strategies.md)），选股引擎承载这三类已完整
- 个人系统算力/带宽有限，三层 + 三 sleeve 是少而精的平衡点（charter 约束五）

### 5.4 过度工程审查：L0→L1→L2-C 三层是否过重

> 对齐任务"过度工程审查：L0→L1→L2-C 三层是否对个人项目过重"

**审查结论：三层不过重，是必要切分而非过度工程。**

| 审查项 | 判断 | 理由 |
|---|---|---|
| L0/L1/L2-C 三层本身 | ✅ 不过重 | L0（数据）/L1（因子）是任何量化系统的通用地基，L2-C 是 A 股特色差异化层——三层是"通用+本土"最低切分，非仪式性分层。Medallion 三层架构实证"splitting into 3 layers makes debugging fast"（[lukastymo 2026-05](https://lukastymo.com/posts/029-software-engineer-value-investing-magic-formula/)） |
| 四阶段漏斗 | ✅ 不过重 | 候选池→过滤→排序→输出是 alpha 工厂标准（[jjjojoj 2026-03](https://github.com/jjjojoj/stock-team/blob/main/docs/architecture_v3.md)、[AlphaFoundry 2026](https://github.com/Rayhanpatel/MSML-602-Final-Project-alphafoundry-ff5-sp500)），每阶段有明确算力/质量目的，非冗余 |
| 双引擎融合 | ✅ 不过重 | 仅打板 sleeve 内部，非跨策略层（§3.2），不增加其他 sleeve 复杂度 |
| 统一接口 SelectionResult | ✅ 不过重 | 接口签名轻量（4 字段），差异化在内部，是 Model A 统一 firm 框架的必要对接契约 |
| 板块轮动 3×3×3 立方体 + Survival | ⚠️ 远期，暂不施工 | 属 L2-C design 态，P1 增强环节，激活条件未满足前不施工——已通过"演进路径分阶段"控制，不构成当前过重 |

**对比反例（过重才需警惕）**：若把双引擎融合抬到跨策略层（§4.1）、或拆 L3 组合信号层（§4.2）、或全量逐个评分（§4.4）——这些才是过度工程，均已拒绝。三层 + 漏斗 + 统一接口 = charter 约束五少而精下的必要复杂度。

> **过度工程审查补充·LLM 边界（v1.0.1 补）**：2026-08 LLM alpha 挖掘前沿（[AlphaSchema](https://ubos.tech/alphaschema-exploring-the-space-of-trading-semantics-for-llm-based-alpha-mining/)/[CogAlpha](https://arxiv.org/html/2511.18850v4)/[QuantaAlpha](https://arxiv.org/html/2602.07085v3)/[Beyond Prompting](https://arxiv.org/html/2603.14288v1)）密集突破，但 [TiMi ICLR 2026](https://arxiv.org/html/2602.07085v3) 与 [国联民生金工 2026-07-16 综述](https://finance.sina.com.cn/wm/2026-07-16/doc-inihyyvy4515788.shtml) 明确：LLM 适合**离线研发/因子生成/语义校验**，不进入**在线低延迟交易执行**。本选股引擎的复杂度边界由此清晰：① L0/L1/L2-C 三层 + 漏斗 + 统一接口是**在线选股层**（须秒级/盘后日频响应），**不引入 LLM 推理**；② LLM 驱动 alpha 挖掘闭环（生成→评估→治理→扩展）是**离线研发层**，产出固化因子/事件标签 schema 写入因子池与事件库，在线层只消费固化产物——这与 TiMi"离线策略研发 + 在线分钟级执行"分离模式完全一致。若把 LLM 推理塞进在线选股层（如盘中实时跑 LLM 事件分类），会引入不可控延迟与成本，是过度工程；离线研发层用 LLM 是必要演进方向（登记为 §6 待裁定-7）。结论：三层架构的"不过重"判定在 v1.0.1 得到 2026 前沿的进一步支撑——复杂度边界由"在线/离线分离"锁定。

## 6. 待裁定

> 以下项目暂不施工，非永久禁止。随项目演进重新裁定。

| 暂缓项 | 暂缓理由 | 重评条件 | 责任方 |
|---|---|---|---|
| 1. 事件链 NLP 管道接入 | 事件 sleeve 信号链未闭环（仅 news_collector 数据底座），NLP/事件分类/映射/衰减全链路待建 | [ARCH-NLP-PIPELINE-001](../../05_architecture_issue_registry/architecture_issue_registry.yaml) Phase 1 落地 | G10 |
| 2. 板块轮动 L2-C 全闭环 | 3×3×3 立方体 + 回踩质量 A/B/C 等级属 design 态，BM-SEL-08/09 proposed | G06 板块轮动 spec 定型 | G06 |
| 3. Survival/密度预测 | 止盈止损时间预测、T+1 次日 8 态属远期愿景 | 密度预测模型验证通过 | [91_density_prediction](91_density_prediction.md) |
| 4. 三 sleeve StrategyBook 实例化 | 打板/多因子/事件 sleeve 载体均未注册（当前仅 DefaultEquityStrategy） | G08/G09/G10 细节讨论定型 | G08/G09/G10 |
| 5. SelectionResult.confidence 算法（v1.0.1 新增） | 接口只定义 confidence∈[0,1] 语义，算法未定。2026 前沿三候选：① AlphaSchema surrogate variance ② Janus-Q LLM confidence gate ③ 经验贝叶斯 shrinkage。三 sleeve 可差异化（打板②/多因子①/事件②） | G08/G09/G10 细节讨论时按 sleeve 差异化选定 | G08/G09/G10 |
| 6. 事件 sleeve 过滤置信度阈值（v1.0.1 新增） | 漏斗"② 过滤"对事件 sleeve 写"置信度低于阈值过滤"，阈值未定。初拟 0.7，须按事件类型差异化（业绩/并购/政策/突发误读成本不同） | G10 事件驱动细节讨论时校准 | G10 |
| 7. LLM 驱动 alpha 挖掘闭环作为 L1 因子工厂远期演进（v1.0.1 新增，v1.1.4 更新，v1.1.6 补 AlphaSAGE） | 当前因子工厂是"人工定义因子 + IC 评估 + 8 状态生命周期治理"，远期可演进为"LLM 生成因子假设 + schema 引导搜索 + 经济正则化 + 多重检验 + 生命周期治理"闭环。须离线运行（TiMi 模式），不进入在线低延迟路径。2026-08 工程路径已清晰：Hubble（AST 沙箱）+ AlphaEvolve（MAP Elites）+ XAlpha（记忆/归因）+ AlphaMemo（edit motif 记忆）+ FactorMiner（禁区入池前预防）+ MAGE（turnover×correlation 2D 网格）+ AlphaAgent（三大正则化）+ AlphaSAGE（RGCN 结构感知 + GFlowNet 多样性生成）构成八框架完整工具链（详见 §3.3 ④） | G09 多因子细节讨论 + 因子工厂治理层 production 稳定运行 3-6 月后 | G09 远期 |
| 8. 6 维权重校准方法（v1.1.2 新增） | 当前 6 维权重（价格动量 20/行业强度 15/相对强度 20/资金 15/技术 20/风险 10）是经验设定，补两条校准路径——路径 A·IC 加权（6 维各视为子因子按 IC 归一化）+ 路径 B·SHAP 归因（LightGBM+SHAP 反推非线性贡献）+ 月度重校准 + CUSUM>2σ 即时重校准；MVP 用经验权重→IC 加权 Phase 2→SHAP 远期 | G08 打板细节讨论 | G08 |
| 9. L1 深度学习 baseline 候选 Cross-Sectional LSTM（v1.1.6 新增） | 当前 L1 是纯线性 IC 加权合成，缺非线性深度学习预测 baseline。Cross-Sectional LSTM（arXiv 2608.05755）加 learnable sector embeddings 捕获截面异质性，短期反转+行业动量双因子驱动，适配 A 股行业轮动。属 Phase 3+ 远期增强（当前 L1 production 线性框架已够 MVP），不纳入首批施工 | G09 多因子细节讨论 + 因子工厂治理层稳定运行 6+ 月后 | G09 远期 |
| 10. 信号工厂九子阶段流水线 + 信号聚合器（v1.1.19 新增，BM-SEL-02-J/L） | 远期登记层（§3.3.1）：当前 3 sleeve 内部各自完成信号加工、跨 sleeve 聚合在 firm 层落地，独立信号加工层/聚合器属四层切分变体（§4.2 已拒绝同构方案）；承接 32 号 §2.7"策略层信号融合归 G05 信号工厂，非 G13 职责"声明，本篇作为 G05 真源登记承接 | 首批策略上线后信号冲突/口径漂移实例 ≥3 例，或 firm 层求和+裁剪被实证无法处理信号级冲突 | G05 远期 |

## 7. 待定问题（讨论要点对齐）

> [00_index §3 G05 讨论要点](00_index_trading_decision.md) 6 项已全部闭合并落入 §3 决策：① 双引擎融合定位 → §3.2（打板 sleeve 内部融合，非跨策略层）；② L0→L1→L2-C 分层 → §3.1/§3.3（通用地基 + A 股特色三层最低切分）；③ 量化强度评级 → §3.4（打板 sleeve 量化引擎输入，6 维 A~E 评级）；④ 选股 pipeline 标准接口 → §3.5（SelectionResult 统一接口 + 差异化内部实现）；⑤ 候选池生成→过滤→排序→输出 → §3.6（四阶段漏斗，各 sleeve 按频率差异化）；⑥ 与 StrategyBook 对接契约 → §3.7（选股产 target_portfolio+粗仓位，精仓位在 firm 层）。

## 8. 引用

### 8.1 相关设计备忘
- [20_first_batch_strategies.md](20_first_batch_strategies.md) v1.5.10（G04 首批 3 策略定义，前置依赖，§2.2-2.4 施工回填为本备忘信号源依据）⚠️ v1.1.19 注记：20 号 git HEAD frontmatter 当前显示 v1.2.4（并发会话回退/重写中间态，2026-08-12），本引用维持 v1.5.10 待 20 号稳定后核对
- [30_multi_strategy_concurrency.md](30_multi_strategy_concurrency.md) v2.5.0（多策略并发架构总纲，§2.2 StrategyBook/firm 层、§7.3 双引擎融合定位）
- [31_position_sizing.md](31_position_sizing.md) v1.23.0（仓位算法 spec，§3.7 精仓位边界依据）
- [00_index_trading_decision.md](00_index_trading_decision.md) §3 G05（讨论要点来源）

### 8.2 相关作战地图
- [battle_map_05_stock_selection.md](../battle_map/battle_map_05_stock_selection.md)（选股阶段 27 环节，L0/L1/L2-C 层归属与施工态）
  - BM-SEL-01：L0 数据接入（production）
  - BM-SEL-02：L1 因子工厂（production）
  - BM-SEL-22~25：L2-C 打板链（production，MOD-SIG-023/033/034/035）
  - BM-SEL-08/09：L2-C 板块轮动（design，G06）
  - BM-SEL-27：L2-C 事件处理（design/proposed，G10）

### 8.3 depgraph 模块（引用稳定 path / blueprint_id）
| 模块 | blueprint_id | path | 层 | 本讨论关系 |
|---|---|---|---|---|
| ShortTermStockSelector | MOD-SIG-023 | `src/zephyr/signal_ashare/short_term_stock_selector.py` | L2-C | 打板短线评分卡 |
| YouziRelayEmotionEngine | MOD-SIG-033 | `src/zephyr/signal_ashare/youzi_relay_emotion_engine.py` | L2-C | 打板游资情绪引擎 |
| QuantShortTermStrengthEngine | MOD-SIG-034 | `src/zephyr/signal_ashare/quant_short_term_strength_engine.py` | L2-C | 打板量化强度评级 |
| DualEngineFusionDecisionEngine | MOD-SIG-035 | `src/zephyr/signal_ashare/dual_engine_fusion_decision_engine.py` | L2-C | 打板双引擎融合 |
| FactorPoolManager | MOD-L02-018 | `src/zephyr/factor/governance/factor_pool_manager.py` | L1 | 因子池容量管理（n_max=64） |
| LifecycleStateMachine | MOD-L02-013 | `src/zephyr/factor/governance/lifecycle_state_machine.py` | L1 | 因子生命周期 8 状态 |
| FactorGovernanceEngine | MOD-L02-017 | `src/zephyr/factor/governance/engine.py` | L1 | 因子治理引擎主入口 |
| SignalSynthesizer | MOD-L03-001 | `src/zephyr/signal_fundamental/synth/signal_synthesizer.py` | L1 | 多因子加权聚合 |
| NewsCollector | MOD-DATA-NEWS-001 | `src/zephyr/data/news_collector.py` | L0 | 事件链数据底座（design） |
| StrategyBook | MOD-POS-020 | `src/zephyr/position/core/strategy_book.py` | 组合层 | sleeve 载体（对接契约 §3.7） |
| FirmRiskAggregator | MOD-POS-021 | `src/zephyr/position/core/firm_risk_aggregator.py` | 组合层 | 统一风险框架（求和+裁剪） |

### 8.4 下游交接
- G06 板块轮动（`22_sector_rotation_spec`）：L2-C 板块轮动层定型
- G07 策略间相关性验证（`23_strategy_correlation_validation`）：§3.5 SelectionResult.signals 为相关性验证输入
- G08/G09/G10（`24-26`）：三 sleeve StrategyBook 实例化与信号消费接线
- G23 回测框架对接（`52_backtest_framework_docking`）：选股 pipeline 的回测验证

### 8.5 开源实证参考
- [lukastymo — Magic Formula + Medallion Architecture (2026-05)](https://lukastymo.com/posts/029-software-engineer-value-investing-magic-formula/)：Bronze/Silver/Gold 三层架构，"splitting into 3 layers makes debugging fast"。支撑 §3.1 三层切分与 §5.4 过度工程审查
- [jjjojoj/stock-team — 三层架构 (2026-03)](https://github.com/jjjojoj/stock-team/blob/main/docs/architecture_v3.md)：选股→预测→交易三层，候选池→硬筛→软筛→排序→前 20。支撑 §3.6 四阶段漏斗
- [AlphaFoundry — Factor-Based Quantitative Strategy Engine (2026)](https://github.com/Rayhanpatel/MSML-602-Final-Project-alphafoundry-ff5-sp500)：Fama-French 5 因子 + XGBoost Ranker，walk-forward 防泄漏，Top-K 等权。支撑 L1 因子工厂 + 漏斗 Top-K 输出
- [arXiv 2409.06289 — Automate Strategy Finding with LLM (2025-11)](https://arxiv.org/html/2409.06289v4)：Seed Alpha Factory + 多 agent 评估 + 权重优化，SSE50 53.17% 收益。支撑分层 alpha 工厂 + 多 agent 决策方向
- [dananalytics — Quant Signals Complement TA (2026-03)](https://dananalytics.com/en/quant-signals-complement-ta/)：TA 模式生成→量化回测过滤→执行三层框架，30+ 样本最小。支撑分层 pipeline + 统计判据
- [BraveOldMan — A-Share L2 Strong Stock Strategy (2026-06)](https://github.com/BraveOldMan/a-share-l2-strong-stock-strategy)：universe_filter.py + T+1 状态机回测，A 股 L2 强势股。支撑 L2-C A 股特色层 + T+1 约束适配
- [WorldQuant Alpha 工厂](https://github.com/Morwane/multi-strategy-alpha-book)：分层 alpha 工厂对标来源（[00_index G05 对标](00_index_trading_decision.md)）

**2026-08 LLM alpha 挖掘前沿与因子衰减诊断（v1.0.1 补，支撑 §3.1 三层切分 / §3.5 confidence 算法 / §5.4 LLM 边界 / §6 待裁定 5-7）**
- [国联民生金工 — 2026 AAAI/ICLR 前沿论文综述 (2026-07-16)](https://finance.sina.com.cn/wm/2026-07-16/doc-inihyyvy4515788.shtml)：AI 量化从"调用通用模型"转向"围绕金融约束重构模型"；TiMi 离线研发+在线执行分离；LLM 适合离线研发/因子生成/语义校验。§3.1 三层切分 2026 前沿印证 + §5.4 LLM 边界依据
- [AlphaSchema — LLM-Based Alpha Mining (2026-08-01)](https://ubos.tech/alphaschema-exploring-the-space-of-trading-semantics-for-llm-based-alpha-mining/)：五字段 schema（Event/Context/Qualities/Direction/Output）+ surrogate model + Acquisition 函数；20 因子 Sharpe 1.85（vs 手工 1.42、随机 1.05）；68% 评估分配到 top-10。§3.5 confidence 算法候选① + §6 待裁定-7 LLM alpha 挖掘闭环
- [CogAlpha — Cognitive Alpha Mining via LLM-Driven Code-Based Evolution (arXiv 2511.18850)](https://arxiv.org/html/2511.18850v4)：七层 agent 层级 + 多 agent 质量检查器（代码质量/修复/裁决/逻辑改进/数值稳定性/时间泄漏单测）+ 思维进化。§6 待裁定-7 多 agent 校验架构参考
- [QuantaAlpha — Evolutionary Framework for LLM-Driven Alpha Mining (arXiv 2602.07085, 2026-05)](https://arxiv.org/html/2602.07085v3)：假设生成→可控因子构造→因子评估→自进化；市场风格转换×因子语义对齐。§6 待裁定-7 因子工厂远期演进
- [Beyond Prompting — Autonomous Framework for Systematic Factor Investing via Agentic AI (arXiv 2603.14288, 2026-03)](https://arxiv.org/html/2603.14288v1)：Agentic AI 闭环（生成→评估→治理→扩展）+ 经济正则化"幸运因子"过滤器 + 多重检验调整。§6 待裁定-7 因子治理防 publication bias
- [microalphas — Factor Decay: Why Published Factor Premia Fade (2026-06-02)](https://microalphas.com/factor-decay/)：因子衰减三机制（arbitrage/crowding + data mining + structural change）；OOS decay vs post-publication decay 诊断；Harvey-Liu-Zhu t-stat 3.0。§3.3 L1 因子衰减监控 + §3.4 量化强度评级 why 补充
- [CSDN — Python量化：因子时效性评估 (2026-07-11)](https://blog.csdn.net/wencaitouzi/article/details/148829424)：IC 衰减曲线 + 半衰期 + 动态持仓周期（夏普 1.2→1.8）+ 混合频率因子组合 + 新鲜度监控阈值 0.7。§3.3 L1 因子衰减监控工程实现

**2026-08 LLM alpha 挖掘新框架五项（v1.1.4 补，v1.1.6 补 AlphaSAGE，支撑 §3.3 ④ LLM alpha 挖掘闭环远期演进）**
- [AlphaMemo — Structured Search-Process Memory (arXiv 2606.20625, 2026-05-26)](https://arxiv.org/pdf/2606.20625)：edit motif 级搜索过程记忆（从 AST 差异提取可复用编辑模式）+ 置信度门控残差记忆 + 非对称否决控制（高置信负模式否决/正模式软提升）；CSI 500 和 S&P 500 验证。§3.3 ④ XAlpha 记忆层精细化升级
- [FactorMiner — Self-Evolving Agent with Skills and Experience Memory (arXiv 2602.14670, ICLR 2026)](https://arxiv.org/pdf/2602.14670v1)：Ralph Loop（retrieve-generate-evaluate-distill）+ 模块化 Skill 架构 + 结构化经验记忆（成功模式+禁区——与现有库高互相关因子家族）+ 全局因子库视角；CSI500 top-40 IC 8.25%/ICIR 0.77；GitHub 2026-08-01 更新 ledger-backed 严格准入。§3.3 ④ 禁区入池前预防（与 factor_pool_manager.py IC 末位淘汰协同）
- [MAGE — MAP-Elites for Alpha Generation (GitHub, 2026-04-30)](https://github.com/joconno2/MAGE)：MAP-Elites 质量-多样性进化算法 + 2D 行为网格（turnover × market correlation）+ RL synergy 奖励；AlphaGen S&P 500 Sharpe 3.96/CSI300 0.76。§3.3 ④ AlphaEvolve 金融场景聚焦版（turnover×correlation 筛选器）
- [AlphaAgent — LLM-Driven Alpha Mining with Regularized Exploration (arXiv 2502.16789, KDD 2025)](https://arxiv.org/pdf/2502.16789)：三大正则化（AST 相似度原创性强化 + 假设-因子语义对齐 + 复杂度控制防过拟合）；CSI 500/S&P 500 四年抗 decay 验证。§3.3 ④ 残差代数工程化升级（生成层约束）
- [AlphaSAGE — Structure-Aware Alpha Generation (arXiv 2509.25055v3, 2026-05-19)](https://arxiv.org/pdf/2509.25055v3)：RGCN 结构编码器捕捉因子 AST 数学结构 + GFlowNet 生成策略 + 多维度奖励（IC+结构对齐+新颖性）。§3.3 ④ MAGE 结构感知升级（FactorMiner 禁区补 AST 结构相关检查）

**2026-08 L1 深度学习 baseline 候选（v1.1.6 补，支撑 §3.3 ⑤ Cross-Sectional LSTM 远期增强）**
- [Cross-Sectional Heterogeneity LSTM (arXiv 2608.05755, 2026-08-07)](https://arxiv.org/html/2608.05755v1)：learnable sector embeddings 捕获截面异质性 + 宏观金融协变量 + label smoothing/dropout/gradient clipping 正则；短期反转+行业动量双因子驱动；超越 basic LSTM/RF/buy-and-hold。§3.3 ⑤ L1 Phase 3+ 非线性预测 baseline（sector embedding 适配 A 股行业轮动）

## 9. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-09 | 0.1.0 | 骨架创建 | 施工图骨架先行：由 00_index G05 讨论要点占位，待讨论填空 |
| 2026-08-10 | 1.0.0 | 骨架→active 全填 | 逐项对齐 G05 讨论要点 6 项落入 §3 决策：①双引擎融合定位（打板 sleeve 内部，非跨策略层，§3.2）②L0→L1→L2-C 分层（通用地基+A股特色三层最低切分，§3.1/3.3）③量化强度评级（打板 sleeve 量化引擎输入，§3.4）④选股 pipeline 标准接口（SelectionResult 统一接口+差异化实现，§3.5）⑤候选池生成→过滤→排序→输出（四阶段漏斗，§3.6）⑥与 StrategyBook 对接契约（选股产 target_portfolio+粗仓位，精仓位在 firm 层，§3.7）；补 §2 背景/§4 替代方案 4 项/§5 上限+L0→L1→L2-C 过度工程审查（结论三层不过重）/§6 待裁定 4 项/§8 引用含 6 条 2026 实证；核对源码施工态：打板链 MOD-SIG-023/033/034/035 全 production、因子工厂 MOD-L02-017/018/013 全 production、事件链 MOD-DATA-NEWS-001 design；不破坏与 20/30/31 号交叉引用 |
| 2026-08-10 | 1.0.1 | 2026-08 最新算法实践补全 + 施工环节算法缺失审查 | ① §3.1 补"2026 前沿趋势印证"块：国联民生金工(2026-07-16) AAAI/ICLR 综述——AI 量化从"调用通用模型"转向"围绕金融约束重构模型"，分层架构是"金融约束重构"工程落地（L0 处理延迟/L1 处理非平稳性/L2-C 处理本土特色）；② §3.5 补"confidence 算法待裁定"块：接口只定义 confidence∈[0,1] 语义但算法未定，2026 前沿三候选（AlphaSchema surrogate variance / Janus-Q LLM confidence gate / 经验贝叶斯 shrinkage），三 sleeve 可差异化；③ §3.6 补"事件 sleeve 过滤置信度阈值待裁定"：初拟 0.7，须 G10 按事件类型差异化校准；④ §5.4 补"过度工程审查·LLM 边界"块：TiMi 离线研发+在线执行分离→三层架构是"在线选股层"不引入 LLM 推理，LLM alpha 挖掘闭环是"离线研发层"产出固化因子/事件标签 schema，复杂度边界由"在线/离线分离"锁定；⑤ §6 新增 3 项待裁定（item5 confidence 算法/item6 事件置信度阈值/item7 LLM alpha 挖掘闭环作为 L1 远期演进）；⑥ §8.5 补 7 条 2026-08 实证（国联民生金工综述+AlphaSchema+CogAlpha+QuantaAlpha+Beyond Prompting+microalphas+CSDN） |
| 2026-08-10 | 1.1.0 | L1 因子配比与 IC 衰减四参数监控 + confidence 第四候选 | ① §3.3 补"L1 因子配比与衰减监控施工补全"块：私募札记 85-90% 人工+10-15% 衍生配比+75%/15%/10% 权重分层+华泰全频段融合年化超额 27.37%；IC 衰减四参数框架（初始 IC/半衰期/衰减斜率/长期 IC 均值）+联动判据（半衰期<10 天缩短调仓/IC 拥挤告警/CUSUM 观察态）；② §3.5 补"confidence 算法第四候选"块：PEAD Inversion 极端反应 confidence 衰减（\|reaction\|>3% confidence 衰减至 0.1），事件 sleeve ②+④双重门控 |
| 2026-08-10 | 1.1.1 | 再次深度审查施工算法缺失 + 选项之外更好算法交叉引用 | ① §3.1 补"层间数据流接口契约"块：L0→L1→L2-C→sleeve 三接口签名（FactorMaterial/FactorSignal/SynthesizedSignal）+降级链路触发判据（Tick 缺失/IC 均值<0.01/双引擎失效）；② §3.3 补"盘中增量双模计算触发条件与 Signature 方法"块：增量触发三判据（新鲜度衰减 0.7/价格冲击 >3%/事件触发）+Signature 路径签名解释（粗路径理论+signatory 库）+25 号多因子细节算法交叉引用（IC 半衰期加权/GAN_GRU/Bayesian 变点/Bootstrap CI）；③ §3.5 补"SignalInput 字段与 urgency↔convergence_window 映射"块：SignalInput 5 字段展开+urgency（immediate/next_open/gradual）↔convergence_window（1-2/2-3/3-5 天）↔sleeve（打板/事件/多因子）三向映射表；④ 修复 v1.1.0 修订记录缺失 drift |
| 2026-08-10 | 1.1.2 | 施工环节算法补全：6 维权重校准方法 + 漏斗③排序优先级算法 | ① §3.4 补"6 维权重校准方法"块：当前 6 维权重（价格动量 20/行业强度 15/相对强度 20/资金 15/技术 20/风险 10）是经验设定，补两条校准路径——路径 A·IC 加权（将 6 维各视为子因子，按 weight_i=IC_i/Σ\|IC_j\| 归一化，与 20 §2.3 因子工厂 IC 加权合成对齐）+ 路径 B·SHAP 归因（LightGBM 训练"6 维→次日收益"模型，SHAP 值反推贡献度作为权重，捕非线性交互）+ 重校准频率（月度+CUSUM>2σ 触发即时）+ MVP 优先（经验权重→IC 加权 Phase 2→SHAP 远期），登记 §6 待裁定-8；② §3.6 补"漏斗③排序优先级算法"块：打板 sleeve 6 类决策优先级表（P0 主升龙头 1.0/P1 二进三 0.85/P2 跟风 0.65/P3 复苏 0.50/P4 伪强 0.30/P5 地天反包 0.20）+ 排序算法 final_score=fusion_score×priority_weight 降序+budget 约束裁剪 Top-N（N≤10）+ 连板/趋势切换协同（连板模式 P0-P1 提升权重 0.8/趋势模式 P3-P4 提升 0.8）+ 多因子 sleeve 横截面因子打分降序 + 事件 sleeve final_score=event_impact_score×decay_phase_factor（含 PEAD Inversion 极端反应降权） |
| 2026-08-10 | 1.1.3 | §1 状态版本漂移修复 + 修订记录补全 | §1 主题组信息状态 v1.0.0→v1.1.3（frontmatter 已为 1.1.3 但 §1 状态未同步，属 v1.1.1-v1.1.2 增量编辑累积漂移）；补 v1.1.2/v1.1.3 修订记录缺失 drift |
| 2026-08-10 | 1.1.4 | LLM alpha 挖掘新框架四项补全 + §1 状态同步 | ① §3.3 补"④ 2026-08 LLM alpha 挖掘新框架"块：AlphaMemo SSPM（edit motif 级搜索过程记忆+非对称否决，XAlpha 记忆层精细化升级）+ FactorMiner Ralph Loop（retrieve-generate-evaluate-distill+禁区入池前预防，与 factor_pool_manager.py IC 末位淘汰协同）+ MAGE（MAP-Elites 2D 行为网格 turnover×market correlation，AlphaEvolve 金融场景聚焦版）+ AlphaAgent 三大正则化（AST 相似度原创性+假设-因子对齐+复杂度控制，残差代数工程化升级）；七框架完整工具链=Hubble+AlphaEvolve+XAlpha+AlphaMemo+FactorMiner+MAGE+AlphaAgent；② §6 待裁定-7 更新：补充四新框架工程路径，远期演进采 Hubble 架构为骨架+FactorMiner 禁区接入入池前相关性检查+AlphaMemo edit motif 记忆接入因子治理层；③ §8.5 补 4 条 2026-08 LLM alpha 挖掘新框架实证（AlphaMemo arXiv 2606.20625+FactorMiner ICLR 2026+MAGE GitHub+AlphaAgent arXiv 2502.16789 KDD 2025）；④ §1 状态 v1.1.3→v1.1.4 同步 |
| 2026-08-10 | 1.1.5 | 版本号漂移修复（3 处交叉引用同步） | 修复 §8.1 相关设计备忘中 3 处版本号漂移：①20 号 v1.3.0→v1.4.5（首批 3 策略定义已升版）；②30 号 v1.4.0→v2.0.0（多策略并发架构已升版）；③31 号 v1.3.0→v1.12.0（仓位算法已升版）；同步修复 §1 前置依赖行 20 号 v1.3.0→v1.4.5 | 循环至零复查发现版本号漂移 |
| 2026-08-10 | 1.1.6 | 2026-08-08 最新研究补全 + 施工环节算法缺失补全（AlphaSAGE/Cross-Sectional LSTM） | ① §3.3 ④ 补"AlphaSAGE 结构感知因子生成"块：arXiv 2509.25055v3 RGCN 结构编码器+GFlowNet 生成策略+多维度奖励（IC+结构对齐+新颖性），MAGE 结构感知升级（FactorMiner 禁区补 AST 结构相关检查）；八框架完整工具链=Hubble+AlphaEvolve+XAlpha+AlphaMemo+FactorMiner+MAGE+AlphaAgent+AlphaSAGE；② §3.3 补"⑤ L1 深度学习 baseline 候选 Cross-Sectional LSTM"块：arXiv 2608.05755 learnable sector embeddings+短期反转+行业动量双因子，Phase 3+ 远期增强（过度工程审查：当前 L1 production 线性框架已够 MVP，不纳入首批施工）；③ §6 待裁定-7 更新补 AlphaSAGE（八框架）+ 新增 item8 6 维权重校准（修复 §3.4 §6 待裁定-8 引用 drift，原文本引用但 §6 表无对应行）+ 新增 item9 Cross-Sectional LSTM baseline；④ §8.5 补 AlphaSAGE+Cross-Sectional LSTM 2 条实证 + FactorMiner 引用补 arXiv 2602.14670 ID 与 CSI500 IC 8.25% 实证 + GitHub 8月1日更新；⑤ §1 状态 v1.1.4→v1.1.6 同步 |
| 2026-08-10 | 1.1.7 | 交叉引用版本同步（20 号 v1.4.5→v1.4.6） | 同步 3 处 20 号交叉引用版本号 v1.4.5→v1.4.6（§前置依赖/§1 主题组信息依赖行/§8.1 相关设计备忘），对齐 20 号 v1.4.6 新增 Diffusion Copulas 尾部依赖建模+earnings acceleration 动量/反转二象性两块内容 |
| 2026-08-10 | 1.1.8 | 交叉引用版本同步（20 号 v1.4.6→v1.5.0） | 同步 3 处 20 号交叉引用版本号 v1.4.6→v1.5.0（§前置依赖/§1 主题组信息依赖行/§8.1 相关设计备忘），对齐 20 号 v1.5.0 新增打板4项升级（5维诱多评分/梯队4类结构/盈亏分档+动态凯利除数/T+1参数订正）+多因子3项（Mittag-Leffler衰减/SUE+EAR双因子/t≥3.0门槛）+事件1项（Omori律三段衰减）+组合2项（Bayesian Kelly/Path Portfolio）共10项 2026-08-08 最新算法 |
| 2026-08-10 | 1.1.9 | 交叉引用版本同步（20 号 v1.5.0→v1.5.2，跨 v1.5.1 两版合并同步）+ 修复 §8.1 漂移 | 同步 3 处 20 号交叉引用版本号至 v1.5.2（§前置依赖 v1.5.1→v1.5.2 / §1 主题组信息依赖行 v1.5.1→v1.5.2 / §8.1 相关设计备忘 v1.5.0→v1.5.2 修复跨版漂移），对齐 20 号 v1.5.1（封成比指标/多因子sleeve仓位分配+退出调仓/EFS RMT去噪/事件sleeve仓位分配共5项）+ v1.5.2（封板率连板率模型/打板战法硬阈值/TSPS隔夜跳空建模/快数字慢语言分离/quantskills因子衰减Skill共5项）新增10项施工算法与2026-08最新算法 |
| 2026-08-10 | 1.1.10 | 交叉引用版本同步（20 号 v1.5.2→v1.5.3） | 同步 3 处 20 号交叉引用版本号 v1.5.2→v1.5.3（§前置依赖/§1 主题组信息依赖行/§8.1 相关设计备忘），对齐 20 号 v1.5.3 新增打板3项（板块联动五条退潮回避铁律/板块Z-score标准化封单占比/连板高度自适应差异化仓位）+多因子4项（因子合成算法/因子中性化分场景决策/换手率控制双目标优化/CFA算法市场假说）共7项施工算法与2026-08最新算法 |
| 2026-08-10 | 1.1.11 | 交叉引用版本同步（20 号 v1.5.3→v1.5.4） | 同步 3 处 20 号交叉引用版本号 v1.5.3→v1.5.4（§前置依赖/§1 主题组信息依赖行/§8.1 相关设计备忘），对齐 20 号 v1.5.4 新增事件驱动5项（异动雷达事件簇/PEAD.txt纯文本盈余惊喜/Qwen3两阶段事件去重/Beyond Sentiment 6维结构化抽取/神经自激点过程）共5项2026-08最新算法 |
| 2026-08-10 | 1.1.12 | 交叉引用版本同步（20 号 v1.5.4→v1.5.5） | 同步 3 处 20 号交叉引用版本号 v1.5.4→v1.5.5（§前置依赖/§1 主题组信息依赖行/§8.1 相关设计备忘），对齐 20 号 v1.5.5 新增打板3项（Tick 68维 CatBoost 破板预测模型/本地逐笔真实封单特征工程/EasyQMT 五步漏斗+灵敏撤单6模式）共3项2026-08最新算法+施工算法补全 |
| 2026-08-10 | 1.1.13 | 交叉引用版本同步（20 号 v1.5.5→v1.5.6） | 同步 3 处 20 号交叉引用版本号 v1.5.5→v1.5.6（§前置依赖/§1 主题组信息依赖行/§8.1 相关设计备忘），对齐 20 号 v1.5.6 新增组合层2项（HRP-μ/HRP-Σμ/CRISP 信号感知分层组合/双层动态风险预算模型）共2项2026-08最新算法+施工算法补全 |
| 2026-08-10 | 1.1.14 | 交叉引用版本同步（20 号 v1.5.6→v1.5.7） | 同步 3 处 20 号交叉引用版本号 v1.5.6→v1.5.7（§前置依赖/§1 主题组信息依赖行/§8.1 相关设计备忘），对齐 20 号 v1.5.7 打板sleeve实证校准数据（疯牛v2.0回测校准+2026量化绞杀游资市场结构数据，非新增待定问题仅校准现有项参数+强化市场语境） |
| 2026-08-10 | 1.1.15 | frontmatter 版本漂移修复 + 交叉引用同步（20 号 v1.5.7→v1.5.8） | ① 修复 20 号 frontmatter 版本漂移（body 含 §4.2 MINGLE ⑩块/§6 表/§6 intro 共76项/§9 修订记录均已为 v1.5.8，仅 frontmatter 漏更 v1.5.7→v1.5.8）；② 同步 3 处 20 号交叉引用版本号 v1.5.7→v1.5.8（§前置依赖/§1 主题组信息依赖行/§8.1 相关设计备忘），对齐 20 号 v1.5.8 组合层 MINGLE 因子暴露度图多样化（arXiv 2608.06618 升级 HRP-μ 图构造层，exposure-similarity graph 替代 correlation-based graph，相关性结构失效 stress regime 时图拓扑崩塌弱点修复） |
| 2026-08-10 | 1.1.17 | 交叉引用同步（20 号 v1.5.8→v1.5.9） | 同步 3 处 20 号交叉引用版本号 v1.5.8→v1.5.9（§前置依赖/§1 主题组信息依赖行/§8.1 相关设计备忘），对齐 20 号 v1.5.9 打板 sleeve 两项 2026 实证校准与因子交互警示——① 辛普森悖论因子交互警示（华安证券 2026-03-20，32615 首板样本，单变量有效→多因子逆转，须 v1.5.3 ① 因子合成施工时内建交互效应检验）；② 多维炸板率经验校准表（雪球 2026-02-25，板型×地位×情绪周期×流通盘四维查表校准现有炸板率项）；两项均为 2026-08-10 全网搜索三 agent 交叉验证的项目级新发现（MFCCA/Non-Gaussian Drawdown/arXiv:2507.07107/AlphaSchema 等均已在前轮整合）。注：v1.1.16 由并发会话添加（§3.1 板块轮动 score 映射公式链路 1 缺口修复），本版顺延 v1.1.17 避免版本冲突 |
| 2026-08-10 | 1.1.18 | 交叉引用同步（20 号 v1.5.9→v1.5.10）+ §8.1 版本漂移修复（30号 v2.0.0→v2.2.0、31号 v1.21.0→v1.22.0） | ① 同步 3 处 20 号交叉引用版本号 v1.5.9→v1.5.10（§前置依赖/§1 主题组信息依赖行/§8.1 相关设计备忘），对齐 20 号 v1.5.10 辛普森悖论防御施工流程形式化——§2.3 补"⑤ 辛普森悖论防御：因子合成交互效应检验施工流程"块（forward_stepwise_ic_test 前向逐步 IC 检验伪代码，v1.5.9 警示的施工落地，与 v1.5.0 ⑩ t≥3.0 正交补组合层假阳性防御，流水线顺序：去噪⑬→正交化⑦→交互效应检验⑤→IC加权合成①）；② §8.1 修复版本漂移：30号 v2.0.0→v2.2.0（30号 frontmatter 实际 v2.2.0，含 SentimentStageSignal 退潮加权+target_portfolio 权重口径声明）、31号 v1.21.0→v1.22.0（31号 frontmatter 实际 v1.22.0）；③ frontmatter v1.1.17→v1.1.18；④ 2026-08-10 第四十六轮审查：搜索 agent 确认 8月10日 arxiv q-fin 21条目无新增可整合算法，8月11日列表未发布 |
| 2026-08-10 | 1.1.16 | §3.1 补 L2-C 板块轮动→SynthesizedSignal.score 映射公式（跨文档算法交接完整性审查——链路 1 缺口修复） | 后台 agent 6 链路审查发现链路 1（22→21 板块轮动→选股）缺口：21号 §3.1 L2-C→sleeve 接口契约 `SynthesizedSignal(symbol, score, confidence, decision_class, metadata)` 中的 `score` 如何从 22号 RRG 四象限（Leading/Improving/Weakening/Lagging）+板块强度评分(0-100)+回踩质量(A/B/C)推导此前未形式化。本次补全映射公式 `score = clamp(SECTOR_QUADRANT_BASE[quadrant] + strength_score/100 * 0.2 + PULLBACK_QUALITY_BONUS[quality], 0.0, 1.0)` + 板块 overlay 降级影响说明（sector_overlay_active=False 时板块轮动不参与选股打分，行业偏离由 firm 层 ±10% 硬约束兜底）。参数待 G06 回测校准。缺口性质="接口契约未显式文档化"非"算法逻辑断裂"，严重性中等 |
| 2026-08-12 | 1.1.19 | **作战地图全覆盖补丁——闭合 BM-SEL-02-J / BM-SEL-02-L / BM-SEL-16 / BM-SEL-17 / BM-SEL-18（5 环节）**：① 新增 §3.3.1「信号工厂与信号聚合器（远期登记层）」——BM-SEL-02-J 信号工厂九子阶段流水线（预处理→信号化→合成→过滤→增强→校准→投票→聚合→输出）定位=L1→L2-C 之间信号加工层，裁定=远期登记不施工（激活条件=首批策略上线后信号冲突/口径漂移实例≥3 例）；BM-SEL-02-L 信号聚合器（归一化+优先级仲裁 风险>机会+组合级输出）裁定=远期登记不施工，承接 32 号 §2.7"策略层信号融合归 G05 信号工厂，非 G13 职责"既有声明（G05 本篇登记承接）；② §3.6 补「漏斗三层级 BM 环节映射」块——BM-SEL-16 分级指标过滤（物理/门禁/分级/概率四排除机制语义定型，日线级批处理执行、"3 秒级 Tick"语义登记远期）、BM-SEL-17 初筛漏斗（技术+量价+板块+主力+状态五维构成定型，挂接 L1 ~5000→1200 容量链）、BM-SEL-18 精筛评分（基础+偏移+主力+8态+拥挤+密度六要素 Z-score 综合定型，8 态要素按 90 号 §7 暂缓裁定现状置 0 不参与），三环节由登记级升级为已覆盖；③ §6 待裁定新增 item10（信号工厂+聚合器远期登记及重评条件）；④ 修复 frontmatter 漂移（frontmatter 已为 1.1.19 而 §1 状态仍为 v1.1.18，本版正文同步 v1.1.19） | 选股域作战地图 11 环节全覆盖施工（本篇承担 5 个），定位→裁定→契约→重评条件四要素逐环节显式映射 |
| 2026-08-12 | 1.1.20 | 作战地图环节映射补强——锚定 BM-SEL-12 分布特征工程（§3.3 末映射块：滞后项/交互项/滚动统计量/Signature 签名，design） | 语义已覆盖但正文未显式编号的环节锚定到承载小节，实现环节级可追溯；不改既有正文 |
| 2026-08-15 | 1.1.21 | 第二轮循环压缩：可压缩点收敛=0（AI-DC2-08）——① §3.1"why 三层"块尾 2026 前沿印证精简（LLM 在线/离线边界内容 §5.4 已载，留指针）；② §3.3④ 结论段八框架重复枚举去重（逐框架清单真源=上文④各块 + §8.5 + §6 待裁定-7）；③ §3.4 空锚点自链（#）清除；④ §7 已闭合 6 项讨论要点由 checkbox 清单压为一行映射（逐项指针保留）；⑤ §1 状态版本漂移修复（v1.1.19→v1.1.21 同步） | 裁定/待裁定 10 项/BM 锚点/外部链接零丢失 |
