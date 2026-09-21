---
ttl: task_bound
title: 深度审查报告——指数Regime面板（D10）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：指数Regime面板（D10）

- 状态: **已审**
- 级别: P1｜类型: 观测面板（1 引擎 × 4 代理；不接交易）
- 基线 commit: 2fa92002c3
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/regime/index_regime_panel.py:269(compute_index_regime_panel:303)`（783 行全文通读，头/尾两段分别精读）
- 生产调用方: `src/zephyr/frontend/dashboard/components/warroom.py`（IDX-02 战情室四指数状态卡）；MATURITY=testing 如实
- 测试文件: `tests/regime/test_index_regime_panel.py`（20 测试）

## 1 对象快照

- 审查范围：面板编排/单卡计算/特征构建/强弱排序/背离警示/降级路径全文件。排除项：warroom.py 前端消费细节（P2 前端域）；M1-② distortion 生产者（market_sentiment_analyzer）。
- 材料包缺项声明：399106 断更后本面板 F4 实际运行数据画像未取；前端展示端对 degraded 卡的呈现未审。
- 测试覆盖概况：20 测试覆盖主流程与降级；F4 断更场景与 strength_score 极端值未见用例。
- 变更热力：3 次，低返工。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | F-A1 **F4 广度断供静默恒 0 且无补洞（与 D05 同概念两处承载已分叉）**：D05 `_load_breadth` 有 EQW_ALLA 补洞+dead 探测+日志（regime_feature_builder.py:577-635），本模块 `_build_proxy_features` 的 F4 KeyError→adv=dec=0→`ad_ratio(0,0)=0` 常量注入，且 `_load_index_kline` 在加载层就 fillna(0)（:442-443）——399106 自 2026-07-03 结构性断更后，本面板四卡 F4 全部恒 0（特征死）无 degraded 标记无日志；HMM 训练窗 F4 无方差还会使协方差退化（RobustScaler scale→0/NaN 风险） | index_regime_panel.py:607-615,442-443 ↔ regime_feature_builder.py:577-635 | P2 | 加载面板块数据跑面板，检查 F4 列方差=0 且无告警 |
| A | F-A2 strength_score 除零保护不足：`recent_return/(volatility+1e-6)`——20 日窗口横盘微涨时 vol→0，score→1e6 级巨值霸榜第一；ε=1e-6 对年化波动的量纲过小；展示层排序被单卡扭曲 | index_regime_panel.py:630-644 | P2 | 构造 20 日几乎恒定微涨序列跑 _compute_strength 观察 score 量级 |
| A | F-A3 PIT 审查通过：特征 shift(1)（:509）、训练窗 [as_of-5y, as_of] 用 shifted 数据、detect 窗口 trailing 60（:541）、scaler 只 fit 训练窗（:526）、强弱分用 ≤as_of 已实现（:557 声明"盘后事实"）——四道 PIT 全合规；as_of=kline 末日 ≤ 入参 trade_date（:493-498）防未来切片 | :493-558 | 已查无 | 逐行核对 |
| A | F-A4 降级链完备且语义正确：数据缺/样本缺/拟合败/detect 异常→单卡 degraded+degrade_reason+无信息先验 Σ=1；全缺→面板级 degraded；配置非法 fail-fast——分层降级设计好，hmm_degraded 单独标记（:533-538）可归因 | :460-477,487-555,354 | 已查无 | 空 index_df 跑面板看四卡降级 |
| A | F-A5 四代理各自 fit 锚定语义一致：anchor_labels 默认 True 生效于每卡 fit，同一锚定规则（vol 升序/斜率 argmin）跨代理可比——观测层消费 r1-r4 标签的前提成立（但 D02 式"标签语义跨系统解释"风险仍在面板展示文案层） | :532,535 | 已查无 | 两卡 fit 后 means_ 槽位有序 |
| B | F-B1 ch_client 注入点+TableRegistry 表名真源+NO-BARE-SQL 豁免常量（_SQL_ 前缀）——数据层设计合规；查询失败→None→全卡 degraded 不炸面板 | :394-444 | 已查无 | — |
| B | F-B2 F3 共享维度：available 过滤后不足两指数时 cross_asset_corr 返回 0 序列（market_features.py:102-104）而非 NaN——单指数可用时 F3=0 常量（中性假值）进训练（dropna 不剔除），与 F1 同族的"静默中性"轻症 | :599-605 ↔ market_features.py:101-104 | P3 | 仅 1 个共享指数在库时查 F3 列 |
| C | F-C1 消费方=warroom.py 前端展示（B-007 零风险声明）；输出契约 90 号§7 铁律（只出概率分布与排序禁点位/方向）在 docstring+INVARIANTS 双声明——观测层爆炸半径=展示误导（degraded 卡 dominant_regime="r1 无语义"已在 contract 注明） | 头栏 :5,8; :234-243 | 已查无 | — |
| D | F-D1 复用纪律好：6 特征函数+`RegimeFeatureBuilder._rolling_apply` 逐函数复用（公式零分叉裁定落地）；唯一越界=跨类调用私有方法 `_rolling_apply`（可提为模块级公共函数，风格 P3）；FEATURE_NAMES 列序同源 import | :96,595-596 | P3 | — |
| D | F-D2 F4 概念双承载（D05 vs 本模块）行为分叉=F1 的旁系面——合并建议：广度加载抽公共函数（含 EQW 补洞）供两处消费 | 同 F-A1 | P2(同 F-A1) | — |
| E | F-E1 静默失败面：F-A1（F4 恒 0 无声）+F-B2（F3 假中性）为仅有的静默点；其余降级全带 reason/日志——面板级"断线有人知道"依赖前端是否渲染 degrade_reason（未审） | :607-615 | P2(同 F-A1) | — |
| E | F-E2 幂等：纯计算无状态；同日重算结果一致（HMM n_init 固定 seed 链路继承 D01 确定性）；json 序列化 frozen dataclass 稳定 | :289-295 | 已查无 | 双跑对拍 |
| F | 见 §3 | — | — | — |

## 3 SOTA 对照

| # | 对照项 | 结论 | 来源 |
|---|---|---|---|
| 1 | 多资产 regime 面板（同引擎多标的） | **对等已有**——同一 HMM 框架跨指数复用+各自拟合是 regime 面板的常规形态（对照 rpt_d01 §3.1 HMM regime 文献族）；"1 引擎×4 配置非 4 模型"的降维裁定与工程惯例一致 | 交叉引用 rpt_d01 §3.1（QuantStart/QuantInsti） |
| 2 | 强弱排序=波动调整动量（return/vol 排序轮动） | **对等已有**——risk-adjusted momentum 排序是 relative strength 轮动文献标准做法；文献同时强调极端波动标的的动量脆弱性——支持本面板用 vol 调整而非裸收益 | [Faber 2010, Relative Strength Strategies for Investing](https://www.cambriainvestments.com/wp-content/uploads/2018/01/Relative-Strength-Strategies-for-Investing.pdf)（Cambria，2010）；[Alpha Architect: Enhancing Momentum](https://alphaarchitect.com/enhancing-the-performance-of-momentum-strategies/)（Alpha Architect，波动过滤实证） |
| 3 | 指数涨/广度跌的背离确认 | **对等已有**——advance/decline 与指数背离是 Dow 理论谱系的经典广度确认信号；本模块自算简版（涨且 dec>adv）+M1-② 注入双路合规 | [Quantpedia: Sector Momentum Rotational System](https://quantpedia.com/strategies/sector-momentum-rotational-system)（Quantpedia，轮动+确认语境）；广度背离为技术分析公共域谱系（Dow theory，无单一定源如实记） |

## 4 缺陷清单（按严重级）

- **F-A1/D2/E1（P2）F4 断供恒 0 无补洞**：现状=F4 静默恒 0（D05 已修同症）→ 证据=双模块锚点对照 → 影响=四卡 HMM 少一维有效特征且训练协方差退化风险，面板概率口径自 2026-07 起漂移无痕；爆炸半径=warroom 展示（观测层，无资金路径）→ 建议修法=抽 D05 的 `_load_breadth`（含 EQW 补洞）为公共加载函数，或至少复用其 dead 探测+告警 → 验证法=现库数据跑面板查 F4 方差。
- **F-A2（P2）strength_score 除零巨值**：建议 ε 提到 vol 分位数下限（如 250 日 vol 的 5% 分位）或 score=NaN 当 vol<阈值 → 验证法=横盘序列复现。
- **F-B2/D1（P3）**：F3 假中性、私有方法跨类调用——常规队列。

## 5 挂起疑问

1. warroom.py 对 degraded 卡与 F4 恒 0 的呈现方式（是否可见降级原因）——前端细节未审，若不可见则 F-A1 的展示风险升级。
2. 000688 科创50 数据始于 2019-07——5 年训练窗要到 2024-07 才满，此前窗口截断式训练（min_train_samples=100 放行）与满窗四卡的训练深度不一致——是否可接受归 Owner（观测层影响轻）。

## 6 完备性自评

- 六轴全查：A（特征/PIT/降级/锚定/强弱分逐项）、B（数据层注入+表真源+F3/F4 断供行为）、C（前端消费方+90号铁律契约）、D（复用纪律+F4 双承载分叉）、E（静默面/幂等）、F（3 条带来源）。
- 长尾清单：①warroom.py 消费细节；②M1-② distortion 生产者质量；③面板级缓存缺失（每次调用 4 次 HMM fit 的性能画像未测）。
