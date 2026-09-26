---
ttl: task_bound
completes_when: "开源生态对标证据入仓且被引用处带案卷出处"
---

> 来源：外部终审交付目录原件 `dossier_github_ecosystem.md`（2026-09-26 终审会话定稿），本仓内改名只为避开非 ASCII 路径与编码门；正文逐字节未改。
> 原件 sha256：d64c33e839f360e4b9ff655c70371297e02938314c59ae695f456b757656776e
> 口径律：本目录是**终审修正层**；凡与 `02_field_corrections_and_new_cases.md` 冲突以 02 册为准，本目录只在其上打补丁与增波，不改写既有 27 册正文。

# GitHub/开源生态案卷：量化系统技术图形库终审证据

> 调研员：research-github（开源生态）｜日期：2026-09-26
> 性质：只出案卷，不出裁定。所有 URL 均为本次实际检索所得；检索不到的信息如实标注，禁止编造。
> Star 数为检索快照，不同来源（star-history / libhunt / Awesome 榜单）口径与时间不一，均已注明。

---

## §一 Python 技术分析库对比表

| 库名 | Star（快照） | 维护状态 | 指标/形态数 | 许可证 | URL |
|---|---|---|---|---|---|
| TA-Lib python 包装（ta-lib 0.6.x/0.7.x） | 未直接检索到 star 数 | 活跃（0.6.x 起原生支持 Polars、安装体验改善） | 158 指标，含 61 种 K 线形态 | BSD 系（原版 TA-Lib） | https://github.com/TA-Lib/ta-lib |
| pandas-ta | ~6k（2025-05 元数据，fork ~1k） | ⚠️ 风险：维护者 twopirllc 在 README 声明赞助不可持续，若 2026-07-01 前无足够资助将归档；PyPI 最新 0.4.71b0 | 150+ 指标与工具；K 线形态依赖 TA-Lib（装后 60+） | MIT | https://github.com/twopirllc/pandas-ta |
| ta（bukosabino/ta） | 5,228（libhunt 2026 榜单） | 低频维护 | 40+ 指标，无 K 线形态，无形态识别 | MIT | https://github.com/bukosabino/ta |
| tulipy | 377（TulipCharts 组织页）；上游 C 库 tulipindicators 944 | ❌ 仓库自标 "[NOT ACTIVELY MAINTAINED]"，最后更新 2021-07；上游 C 库最后更新 2024-02 | 100+ 指标（C 库），无 K 线形态 | LGPL-3.0 | https://github.com/TulipCharts/tulipy |
| finta | 未检索到独立仓库数据 | 未确认 | 仅在第三方基准文章（johal.in）中被提及跑分 | 未确认 | 未检索到可靠入口 |
| freqtrade/technical（配套库） | 未检索到 star 数 | 随 freqtrade 生态活跃 | TA-Lib/PyTi 等封装 + 自研指标：trendlines（2 种算法）、fibonacci_retracements、Ehlers laguerre、Consensus 等；提供 resample_to_interval / resampled_merge 多周期工具 | 与 freqtrade 一致 | https://github.com/freqtrade/technical |

关键证据：
- 社区对比（2025）：纯 Python 库中"K 线形态识别只有 TA-Lib 有"；TA-Lib 单指标 C 实现快 3-10x，pandas-ta 工作流（df.ta.sma()）更顺手；性能差距在百万行分钟级数据上显著。
- pandas-ta README（经镜像 nachogarrid0/pandas_ta 确认原文）关键句："current and past levels of support are unsustainable for maintaining and improving the library. Unless significant additional support is provided by July 1st, 2026, this widely used library will be archived."——**这是终审必须知悉的依赖风险**。
- ta 库评价（CSDN 对比文，2025）：API 简洁（add_all_ta_features 一键全指标），但"缺少复杂技术分析模式识别、不支持自定义指标组合、性能低 5-15x"。
- tulipy 上游 C 库 TulipCharts/tulipindicators（944 stars，LGPL-3.0，最后更新 2024-02）提供 100+ 指标，Python 绑定自 2019 年（0.4.0）未再发版，Windows wheel 停在 cp37。
- **本次检索未发现比 TA-Lib 61 形态更全的"单一 K 线形态库"**（无 100+ K 线形态的现代库直接证据）。更全的形态覆盖出现在"图表级几何形态"项目（§二），而非 K 线级。
- ta4py：本次检索未命中任何有效结果。

## §二 形态识别专用项目清单

| 项目 | 覆盖形态 | 备注 | URL |
|---|---|---|---|
| ChipaDevTeam/simple-chart-patterns-detection | 头肩（正/反）、多顶多底、双顶双底、三角形、楔形、通道、趋势线、支撑阻力、枢轴点 | pandas/numpy 脚本级，函数式 API（detect_head_shoulder(df, window=3)），MIT | https://github.com/ChipaDevTeam/simple-chart-patterns-detection |
| tysoncung/crypto-chart-patterns | 头肩/双顶底/上升下降对称三角/升降楔形/牛熊旗/三类通道/杯柄 | 局部极值 + 数学分析；**内置前向收益验证**（pattern validation）；多周期支持；面向币安数据但算法可移植；MIT | https://github.com/tysoncung/crypto-chart-patterns |
| choisangh/pattern-scanner-library | 头肩、三角、楔形等 | OO 设计：PatternRecognizer 可挂接任意 OHLCV，单形态类可分别调用 | https://github.com/choisangh/pattern-scanner-library |
| nashit8421/price-action-lib | 30+ K 线形态、15+ 图表形态（头肩/三角/楔形/旗）、BOS/ChoCh、Fair Value Gap、Order Block、pin bar/inside bar/fakey、缺口分类 | **一次 fetch_all() 产出 95+ 列**，专为"ML 就绪"的结构化输出设计，含多时间框架与支撑阻力汇合分析——与现有 215 列体系思路同构 | https://github.com/nashit8421/price-action-lib |
| djoffrey/HarmonicPatterns | 9 种谐波：ABCD、Gartley、Bat、Alt-Bat、Butterfly、Crab、Deep Crab、Shark、Cypher | ZigZag 过滤 + 斐波那契比例校验；支持"已完成+预测中"双扫描（预测 D 点目标）；依赖 TA-Lib；2026-06 仍在现代化维护（pyproject/uv） | https://github.com/djoffrey/HarmonicPatterns |
| pyharmonics（niall-oc） | 谐波 XABCD | 输出大 JSON（显著点+分组形态），社区有 GPT 集成实践（niall-oc/pyharmonics-gpt）；star 数未逐一确认 | https://github.com/niall-oc/pyharmonics |

补充：HKUDS/Vibe-Trading（33,994 stars，libhunt 2026）内置 harmonic skill（Gartley/Bat/Butterfly/Crab 的 PRZ 信号引擎，pyharmonics 后端）——说明谐波检测已进入主流 AI 交易框架的组件层。

## §三 缠论实现清单与评价

| 项目 | 要点 | URL |
|---|---|---|
| Vespa314/chan.py | **事实标准**。分型/笔/线段/中枢/一~三类买卖点完整实现；支持多级别联立计算、区间套；形态学买卖点 + 自定义策略动力学买卖点；背驰算法可配置；内置 ML 打分框架（XGB/LightGBM/MLP，提供训练/预测/读写接口即可上线）；内置回测与评估框架；多数据源（futu/akshare/baostock/tushare/本地离线）；matplotlib 全局绘制/逐步回放；可对接 Futu 交易引擎实盘 | https://github.com/Vespa314/chan.py |
| 164149043/chananalyzer | 基于 chan.py 二次开发的 A 股缠论系统：一/二/三类买卖点、全市场买卖点批量扫描、FastAPI Web 界面、多 AI 协作分析、SQLite 缓存、5 年日线 | https://github.com/164149043/chananalyzer |

算法思路（DeepWiki 架构文档 https://deepwiki.com/Vespa314/chan.py/1.1-system-architecture）：
- CChan 统一编排多级别 K 线迭代（lv_list 从高到低严格排序）→ CKLine_List 逐 K 处理：包含关系合并 → CBiList.update_bi() 成笔 → 特征序列（Eigen/EigenFX）线段划分 → cal_seg_and_zs() 中枢 → CBSPointList 形态学买卖点。
- 支持批量模式（init 一次消费）与实时/回放模式（step_load/trigger_load 逐 K 喂入）——**对盘中买卖点类信号的增量计算有直接参考价值**。

实测评价证据：
- chan.py 被二次开发为 A 股分析系统（chananalyzer）并加入 AI 协作，说明其数据结构可复用；社区镜像与多语言文档存在（repoportal 等）。
- 官方功能清单（README 检索快照）与现有系统缺口高度对口：分型/笔/线段/中枢/买卖点、"支持父级别计算（线段中枢、线段的分段、线段买卖点）"、多级别联立、区间套、背驰配置、ML 打分、回测评估、逐 K 回放。
- 二次开发实证（chananalyzer README）：在 chan.py 之上补齐了"全市场买卖点批量扫描、SQLite 缓存、FastAPI 看板、多 AI 协作建议"——说明裸 chan.py 缺少的是批量扫描与展示层，核心结构计算已完备。
- 未检索到对 chan.py 信号胜率的权威第三方评测；chan.py 的 star 数本次未直接获得（检索命中的是 DeepWiki/镜像/二开仓库）。

## §四 多周期框架的工程化方案

| 框架 | Star（快照） | 多周期机制 | URL |
|---|---|---|---|
| freqtrade | 51.1k~51.7k（2026-06 榜单） | ① `@informative('30m')` 装饰器：高周期指标计算后自动合并进低周期 DataFrame，生成 `rsi_30m`、`rsi_1h` 列，条件轴直接引用；② `informative_pairs()` 声明白名单对数据；③ 手工方案：`dp.get_pair_dataframe(tf)` + `pd.merge_asof(direction="backward")` **无前视对齐**；④ 配套库 technical：`resample_to_interval` / `resampled_merge` → `resample_240_rsi` 列模式 | https://github.com/freqtrade/freqtrade ；配套：https://github.com/freqtrade/technical |
| vectorbt | 8.0k~9.1k（2026 快照不一） | ① 全向量化：`vbt.Portfolio.from_signals(close, entries, exits)` 一次跑 N 组参数 × M 资产；② `Portfolio[(param1, param2)].stats()` 逐格子出 Sharpe/Expectancy/SQN，`total_return().vbt.heatmap()` 出参数热力图——**与"矩阵法算每个共振格子夏普率"直接同构**；③ 多周期：`vbt.resample_apply("4h", ...)` 将信号/指标重采样到高周期（文档警告：降采样有信号次序信息损失）；from_signals 会自动清洗 entries/exits | https://github.com/polakwo/vectorbt |
| qlib（microsoft） | 44.5k~48.8k（2026 多源不一） | ① 数据层：`freq=["day","1min"]` 多频率 handler；② 回测层：NestedExecutor——外层日线组合决策 + 内层 5min 执行（TWAP 拆单、SBB 选时棒），LevelInfrastructure 分层管理 trade_calendar；③ PIT provider 处理财报点时序；④ Alpha158/Alpha360 因子库与 RD-Agent 自动因子挖掘 | https://github.com/microsoft/qlib |
| backtrader | 22.1k~22.9k | 原生多 datafeed：最小周期数据必须最先 addata；`cerebro.resampledata(data, timeframe=...)` 生成高周期；大周期指标的最小周期会推迟策略 next() 触发；⚠️ 2026 评测普遍标记为"dormant/休眠" | https://github.com/mementum/backtrader ；文档：https://www.backtrader.com/docu/data-multitimeframe/data-multitimeframe/ |

工程化启示（证据综合）：freqtrade 的 `@informative` + merge_asof 模式 = "把高周期信号列贴到低周期行上"，最适合"15 分钟趋势线触碰 + 1 分钟两次不过前高"这种**跨周期条件与**；vectorbt 的参数矩阵 + 逐格子 stats = **共振矩阵统计**的开箱实现；qlib 的 NestedExecutor 是"日线决策+分钟执行"双层架构的参考实现。

各框架关键代码形态（检索所得原文摘录，供接线设计对照）：
- freqtrade：`@informative('30m') @informative('1h') def populate_indicators_inf(...)` 计算的高周期指标自动生成 `rsi_30m`、`rsi_1h` 列；社区策略 MultiTimeframeConfirmation 用 `self.dp.get_pair_dataframe(pair, timeframe="15m")` + `pd.merge_asof(..., direction="backward")` 手工合并（Freqle 策略库样例）。注意官方文档强调**基础周期必须取所有周期中最低的一个**。
- vectorbt：`fast_ma, slow_ma = vbt.MA.run_combs(close, window=np.arange(2,101), r=2)` → `pf = vbt.Portfolio.from_signals(...)` → `pf[(13,21)].stats` 输出 Sharpe 1.78/Sortino 2.81/SQN 1.96 等全指标——README 自述"4851 个窗口组合 5 秒内测完"，是共振矩阵法性能上限的直接证据。
- qlib：NestedExecutor 配置样例 = 外层 `time_per_step: "day"` + 内层 TWAPStrategy + `time_per_step: "5min"`（qlib/backtest/executor.py 310-499）。
- backtrader：官方多周期文档规则——最小周期数据最先 adddata，`cerebro.resampledata(data, timeframe=bt.TimeFrame.Weeks)`；文档演示了周线 SMA(10) 使 next() 推迟 50 根日线才触发的最小周期效应。

## §五 支撑阻力/趋势线开源方案

| 项目 | 方法 | 备注 | URL |
|---|---|---|---|
| trendln（GregoryMorse） | 极值点检测 4 法（NAIVE/NAIVECONSEC/NUMDIFF/NCUBED）+ 趋势线拟合 5 法：默认 METHOD_NSQUREDLOGN（2 点排序斜率），**METHOD_HOUGHPOINTS / METHOD_HOUGHLINES / METHOD_PROBHOUGH（Hough 变换，需 scikit-image）**；输出 (slope, intercept, SSR, slopeErr, areaAvg) 完整统计 | 2026-04 仍有现代化提交（支持新版 Python、OHLC 渲染）；配套论文级文章《Programmatic Identification of Support/Resistance Trend lines with Python》 | https://github.com/GregoryMorse/trendln |
| pytrendline（ednunezg） | 枢轴点穷举连线（O(N^3)），校验：最少点数、点到线距离、**是否穿越实体（breakout_tolerance 突破判定）**、枢轴要求；内置评分函数与 (slope,last_price) 2D 聚类去重；结果为可排序 pandas DataFrame | 明确定位日内小样本/离线分析；**突破检测（假突破陷阱的线侧证据）内置** | https://github.com/ednunezg/pytrendline |
| freqtrade/technical | trendlines 指标（2 种算法）、fibonacci_retracements（120 根滚动窗口内高低枢轴） | 与 freqtrade 生态配套 | https://github.com/freqtrade/technical |
| price-action-lib | 支撑阻力多方法 + 汇合（confluence）分析、near_support/near_resistance 布尔列 | 见 §二 | https://github.com/nashit8421/price-action-lib |
| simple-chart-patterns-detection | rolling 统计支撑阻力 + detect_trendline + find_pivots | 见 §二 | https://github.com/ChipaDevTeam/simple-chart-patterns-detection |

## §六 深度学习形态项目

| 项目/论文 | 方法 | 结果 | URL |
|---|---|---|---|
| pecu/Series2GAF（论文 Financial Innovation 2020） | K 线 OHLC/CULR 特征 → Gramian Angular Field 图像编码 → 2 层 CNN（16 kernels） | EUR/USD 分钟数据 2010-2018，8 种主要 K 线形态，平均准确率 90.7%（超 LSTM 基线）；class 0（无形态）误报偏多 | https://github.com/pecu/Series2GAF |
| Edreesrm/Enhancing-Market-Trend-Prediction-Using-Convolutional-Neural-Networks-（PMC11935771，2025） | **TA-Lib 61 形态定位窗口** + 20 均线定多空标签 → CNN 窗口分类（窗口 5~30，50% 重叠） | Forex 15min 数据；论文开源全部代码 | https://github.com/Edreesrm/Enhancing-Market-Trend-Prediction-Using-Convolutional-Neural-Networks- |
| LEarnX-Official/candelstickpatternrecognition | GBM 合成数据 → TA-Lib 形态标注 → mplfinance 出图（128x128）→ 2-conv CNN → Buy/Sell/Hold 推理 | 教学级端到端流水线，含杯柄/下降楔/牛旗/头肩/对称三角的"高级形态"图像类 | https://github.com/LEarnX-Official/candelstickpatternrecognition |
| mraselm/stock-chart-image-classifier | RGB K 线图 CNN 二分类（涨/跌），TF 2.13+ | 诚实基线：从零训练 46.4% → 调学习率后 **52.1%**——说明 K 线图直接 CNN 二分类接近随机 | https://github.com/mraselm/stock-chart-image-classifier |
| CharlesLoo/stock-pattern-recorginition | FR-CNN（Faster R-CNN）在 2D K 线图中检测头肩形态 | 150 张标注图 AP@0.5IOU=64%；数据增强到 8000 张后 74%；小样本过拟合问题显著 | https://github.com/CharlesLoo/stock-pattern-recorginition |

证据综合：深度学习路线在 K 线形态上的公开证据多为二元/少量类别分类，GAF 编码是其中最有论文支撑的表示法；直接图像 CNN 基线接近随机（52%）。未见"10+ 自研形态模块同等复杂度（缠论结构/庄股模拟/假突破）"的开源 DL 替代品。

对终审的具体含义：
- 若考虑 DL 通路，证据支持的形态是"规则库触发标签 + 窗口分类/打分"（Edreesrm 论文用 TA-Lib 61 形态定位窗口），而非端到端图像分类（mraselm 的 52% 是反证）。
- 小样本是硬约束：CharlesLoo 项目 150 张标注图即过拟合，需 8000 张增强图才到 AP 74%——A 股自研形态（庄股/假突破）标注成本需按此量级评估。
- GAF-CNN 的 90.7% 是 8 类主要形态 + EUR/USD 分钟数据的论文口径，迁移到 A 股全市场前需独立复测（论文本身注明 class 0 误报偏多，"可视为保守模型"）。

## §七 信号统计框架（信号触发→条件收益统计）

| 项目 | Star（快照） | 能力 | URL |
|---|---|---|---|
| alphalens（quantopian 原版） | 4,435 | 因子→分位数→前向收益（Returns/IC/Turnover/分组四大分析）；**create_event_study_tear_sheet（事件研究模板）**；❌ 2020 年后停更（最后 PyPI 0.4.0，Python 3.5 上限） | https://github.com/quantopian/alphalens |
| alphalens-reloaded（stefan-jansen） | 642 | 维护版：Python 3.10-3.13，2025-12 仍有推送，8 个 release；核心调用 `get_clean_factor_and_forward_returns(factor, prices, periods=(1,5,10), quantiles=5)`；⚠️ 已知陷阱：前向收益从 t 收盘起算，**t 收盘信号需自行 shift(1) 才对应 t+1 开盘成交**；无交易成本；累计收益口径默认重叠收益抬高 t 值 | https://github.com/stefan-jansen/alphalens-reloaded |
| vectorbt | 8.0k~9.1k | from_signals + `pf[params].stats()`（Sharpe/Expectancy/SQN/胜率一锅出）+ heatmap 参数扫描；`pf.trades.expectancy().groupby([...])` 分组统计——**网格搜索条件轴最直接的开箱实现** | https://github.com/polakwo/vectorbt |
| qlib | 44.5k~48.8k | 信号分层回测报告（分组累积收益/超额/IC 曲线），NestedExecutor 支持信号日频+执行分钟频 | https://github.com/microsoft/qlib |

未检索到独立成熟的"信号触发→条件收益"专用框架（signal lab 类）超出上述四者；alphalens 的事件研究 tear sheet + vectorbt 的分组 stats 是最接近的开源拼图。

alphalens-reloaded 关键机制摘录（供"信号→条件收益统计"实现参考）：
- IC 计算 = 按日 Spearman 秩相关（因子值 vs 前向收益），附带 IC 衰减（按 horizon）与 IC IR = mean(IC)/std(IC)。
- 分位收益 = mean_return_by_quantile + 分位累计收益 + 多空 factor_returns；换手 = quantile_turnover + factor_rank_autocorrelation（信号衰减代理）。
- 事件研究 = `create_event_returns_tear_sheet(factor_data, returns, avgretplot=(5,15))`：事件前后 (before, after) 窗口的平均累计收益 + 标准差条——**这就是"15 分钟趋势线触碰前 N 根到后 M 根的条件收益"统计的现成模板**。
- 前向收益陷阱（源码验证）：`returns.shift(-period)`，即信号日 t 的收益从 t 收盘起算；若信号来自 t 收盘，需 `factor.groupby(level=1).shift(1)` 才对应现实可成交的 t+1 开盘链路。
- 硬性输入要求：factor 必须是 (date, asset) 双层 MultiIndex 的 Series；prices 必须是"行=日期、列=资产"的宽表（方向相反是最高频报错原因）；prices 需比最后因子日多出 max(periods) 根。

## §八 选型建议倾向（仅列证据倾向，不出裁定）

1. **K 线形态基座**：本次未检索到形态数超过 TA-Lib 61 种的单一 K 线形态库；ta-lib 0.7.x wrapper（活跃、Polars 支持）仍是 K 线形态的事实标准。pandas-ta 功能互补（150+ 指标、numba），但存在明确的 2026-07 归档风险声明，**不宜作为新接线的核心依赖**。
2. **接线（信号→网格条件轴）**：vectorbt 的参数矩阵 + 逐格子 stats + heatmap 与"矩阵法算每个共振格子夏普率"方法学同构；alphalens-reloaded 的 event study tear sheet 是"信号触发→前后窗口累计收益"的参考实现（注意 shift(1) 前视陷阱与无成本口径）。
3. **多周期共振工程化**：freqtrade 的 `@informative`/merge_asof 模式（高周期列贴到低周期行，backward 对齐防前视）最贴合"15 分钟趋势线触碰 + 1 分钟两次不过前高"的跨周期条件组合；qlib NestedExecutor 是"日线决策+分钟执行"分层的参考；backtrader 多周期原生但项目已休眠，不宜新依赖。
4. **缠论**：Vespa314/chan.py 是唯一完整级开源实现（含回测+ML 打分框架+逐K回放），自研缠论模块的对照基准。
5. **趋势线/突破**：trendln（Hough 变换族，2026 仍在维护）+ pytrendline（穷举+breakout_tolerance 突破判定+评分去重）可直接支撑"趋势线触碰/假突破"条件的线侧实现。
6. **谐波/几何图表形态**：djoffrey/HarmonicPatterns（9 种、含预测 D 点）与 tysoncung/crypto-chart-patterns（含前向收益验证）质量较高但 star 规模小，适合按源码移植而非整体依赖。
7. **深度学习**：公开证据（52% 二分类基线、GAF-CNN 90.7% 少类别）不支持用 DL 整体替代规则形态库；仅 GAF 编码 + 8 类主要形态有论文级正证据。
8. **95+ 列先例**：nashit8421/price-action-lib 证明"单次调用输出 95+ 特征列（含形态/结构/支撑阻力）"的库设计在社区可行——与现有 215 列体系互为印证。

## §九 低把握/未覆盖项

- finta、ta4py：本次检索未获得可靠仓库信息（ta4py 未命中任何有效结果），不做评价。
- TA-Lib python 包装（TA-Lib/ta-lib）的 star 数未直接检索到；ta-lib 0.7.1 相对 0.6.x 的新特性清单未逐条核对官方 changelog。
- §二/§五 多数形态识别项目未逐一进入仓库页核实 star 数与最新 commit 日期（引用内容来自 README 检索快照）。
- "庄股形态模拟"类（吸筹/拉升/出货剧本）无对应开源实现检索结果；"假突破"仅有 pytrendline 的 breakout 判定与 price-action-lib 的 fakey 模式两个近似物，非完整陷阱检测框架。
- Star 数快照来源混杂（star-history 2026-09：qlib 48.3k；libhunt：vectorbt 9,132；itjob 2026-06：vectorbt 8.0k），存在统计时点与 fork 归并差异，终审引用时建议以 GitHub API 当日复核为准。
- vectorbt OSS 与 vectorbt PRO 的 resample API 有差异，本案卷引用的 vbt.resample_apply 部分示例来自 PRO 教程（qubitquants），迁移到 OSS 版需核对。
- 缠论 chan.py 的信号胜率/收益权威第三方评测未检索到；chananalyzer 为个人二次开发项目，工程质量未经终审级核查。
- 未覆盖：R 语言/非 Python 形态库；TradingView Pine 脚本生态的形态库（其许可不允许移植，未纳入）。

---

## 附录：检索日志（本案卷证据可追溯性）

| # | 主题 | 检索关键词（实际执行） | 主要命中来源 |
|---|---|---|---|
| 1 | pandas-ta 现状 | pandas-ta GitHub 维护状态 2025 stars indicators | PyPI 镜像（0.4.71b0、6k stars 元数据）、nachogarrid0 镜像（归档声明原文）、worldlink 指标趋势页 |
| 2 | TA-Lib 替代讨论 | TA-Lib python alternative 2024 2025 pandas-ta vs ta library comparison | CSDN/DevPress 对比文（158/150+/40+ 指标口径、性能 3-10x/5-15x）、ima.qq.com 对比页 |
| 3 | 图表形态检测 | chart pattern detection python github head and shoulders double top triangles | ChipaDevTeam、tysoncung、choisangh、nashit8421 四仓库 README |
| 4 | 缠论 | chan.py 缠论 python github Vespa314 分型 笔 线段 中枢 | repoportal 功能镜像、DeepWiki 架构页、164149043/chananalyzer |
| 5 | 多周期 a | freqtrade informative pairs multi timeframe strategy vectorbt resample | dev.to 教程、Bot Academy、Freqle 策略库、freqtrade/technical README |
| 6 | 多周期 b | qlib multi frequency / backtrader multiple timeframe data feeds | qlib CSDN 指南、DeepWiki Advanced Topics（NestedExecutor 源码行号）、backtrader 官方文档 |
| 7 | vectorbt | vectorbt from_signals resample multi timeframe grouping stats | vectorbt README（fork 镜像全文）、qubitquants PRO 教程（resample_apply） |
| 8 | 支撑阻力/趋势线 | support resistance detection python github trendline RANSAC Hough | GregoryMorse/trendln、ednunezg/pytrendline、GitCode 指南 |
| 9 | 深度学习 | candlestick pattern CNN deep learning github | LEarnX、mraselm、Series2GAF 论文（DOI 10.1186/s40854-020-00187-0）、PMC11935771、CharlesLoo |
| 10 | 信号统计 | alphalens signal analysis event study framework | DeepWiki alphalens 架构、alphalens-reloaded 分析（stefan-jansen 642★/2025-12）、ml4trading API 文档 |
| 11 | 谐波 | harmonic patterns python github Gartley Bat Butterfly | djoffrey/HarmonicPatterns、HKUDS/Vibe-Trading skill、pyharmonics |
| 12 | tulipy 等 | tulipy python github / ta4py finta | TulipCharts 组织页（"NOT ACTIVELY MAINTAINED"）、pythonfix（92-377 stars 口径）、PyPI 0.4.0 |
| 13 | star 数核对 | polakmarcel vectorbt stars / microsoft qlib stars | libhunt（vectorbt 9,132）、Awesome_AI4Finance（freqtrade 51.1k）、star-history（qlib 48.3k）、ghtrends（qlib 44,469@2026-06） |

*案卷完。检索方法：每主题 2-3 组不同关键词，WebSearch 实际执行于 2026-09-26。*
