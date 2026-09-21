---
ttl: task_bound
title: 深度审查报告——周期分析器（D13）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：周期分析器（D13）

- 状态: **已审**
- 级别: P1｜类型: 统计（日历效应事件研究+周年日窗口；辅助参考非交易信号）
- 基线 commit: 2fa92002c3
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/regime/regime_cycle_analyzer.py:182(RegimeCycleAnalyzer.analyze:415)`（518 行全文通读）
- 生产调用方: **查无（声明态孤儿）**——头栏 [CONSUMERS] 自认"无（MVP 阶段…接线属后续 WFA 验证达标后施工）"，MATURITY=design；孤儿为登记态非漂移
- 测试文件: `tests/regime/test_regime_cycle_analyzer.py`
- 变更热力: 4 次

## 1 对象快照

- 审查范围：两件套（日历效应三假设+周年日一假设）全链：trading_day_features/event_study/detect_swing_extremes/anniversary_windows/analyze 编排。排除项：扩展口（EXT-G/GEO/FFT/PRICE，MVP 未落码）；regime_cycle_registry.yaml 真源对账（cycle_id 映射已抽验）。
- 材料包缺项声明：日历效应在 A 股样本上的实际显著性结果（模块自身 evidence_table 输出）未取数据画像；registry v1.2.0 原文未回读。
- 测试覆盖概况：专项测试在册；upcoming 日历窗口结构空缺（F-A1）未见用例。
- 防滥用设计：is_advisory_only 恒 True、不显著窗口 confidence=0/neutral 下游禁消费——输出契约自觉。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | F-A1 **日历效应 upcoming 窗口结构性为空**：hit_days 在 `dates`（≤as_of 的收盘数据索引）上筛 [as_of, horizon_end]——未来日期不在索引内，故 month_end/month_start/post_holiday 的 upcoming 分支只可能命中 as_of 当日本身；"变盘窗口前降仓"所需的前瞻日历窗口在该路径产不出（周年日路径经 windows_df 未来偏移可产，日历路径不能）。active/upcoming 的 else 分支对日历窗口不可达 | regime_cycle_analyzer.py:453-463（dates 来源 :427/:514 截断） | P2 | as_of 取月中、horizon=10 跑 analyze，断言 upcoming 无日历窗口 |
| A | F-A2 事件研究统计合规：Welch t（不等方差）+Bonferroni 族=4 与假设数一致+min 8 事件双侧护栏+零方差/非有限 p 的 isfinite 兜底（p→1.0 不显著）——防御完整；**t 检验对日收益肥尾/自相关的近似性未校正**（p 值偏乐观的常规 caveat，Bonferroni 部分补偿） | :253-291 | P3 | 读 event_study 防御分支 |
| A | F-A3 显著高低点识别 PIT 正确：右窗未满不采信（:316-318 未确认极值丢弃——极值确认天然需后视数据，此处处理干净）；±20 日窗口+20% 幅度过滤+同类簇去重链式保留最极端——去重只与"最近保留点"比较的近似聚类（跨簇吞并未发生）可接受 | :294-358 | 已查无 | 构造双顶序列验证去重 |
| A | F-A4 周年日统计口径自洽：变盘=|日收益| 抬升（方向中性）+历史窗口 end≤as_of 参与统计（:394 PIT）+多极值窗口重叠以 mask 并集去重计一次——语义干净；但周年日效应本身文献基础薄（Gann 谱系民间方法，模块已在扩展口声明"证据强度不足不过度工程"的自觉） | :361-397,440-444 | P3 | — |
| A | F-A5 日历特征派生正确：月末/月初按 (year,month) 组内 rank 双向、节后=自然日间隔≥5（春节/国庆口径）——纯日历确定性派生，与"日历前视是确定性信息非泄漏"的 INVARIANT 自洽 | :217-250 | 已查无 | — |
| B | F-B1 输入契约 fail-closed：非 DataFrame/缺 close/≤as_of 观测 <60 抛 ZA-REGIME-0030（不静默降级——与本域其他对象"降级哲学"不同但符合统计模块 fail-closed 正解） | :501-518 | 已查无 | 短序列复现抛错 |
| C | F-C1 声明态孤儿+防滥用钉死：is_advisory_only 恒 True、下游禁消费不显著窗口——爆炸半径当前=0；接线风险在于"辅助参考"信号并入节流的传导系数未知（接线施工时应定义 confidence→节流映射） | 头栏 [CONSUMERS]:5; :181-198 | P3 | grep 调用方复核 |
| D | F-D1 cycle_id 映射锚定 registry（_CYCLE_ID_MAP: month_end/start/post_holiday→CYC-STAT-013、anniversary→CYC-TIME-004）——库↔代码锚点在位；registry 三假设同码的合并语义（三类共享同一 cycle_id 与证据条目）可读性一般但无漂移 | :108-115 | 已查无 | 对照 registry（抽验） |
| E | F-E1 静默失败面：全路径 fail-closed 或显著/不显著显式标注——本对象无 except 吞噬、无降级默认值，静默面干净；零随机源确定性成立（:8 INVARIANT） | 全文 | 已查无 | 双跑对拍 |
| E | F-E2 时序攻击面：anniversary mask 用窗口 end≤as_of——进行中窗口（start≤as_of≤end）的历史段不参与统计（保守，轻微样本损失非泄漏） | :391-397 | 已查无 | — |
| F | 见 §3 | — | — | — |

## 3 SOTA 对照

| # | 对照项 | 结论 | 来源 |
|---|---|---|---|
| 1 | 月末/月初效应（TOM） | **对等已有**——turn-of-the-month 效应自 Lakonishok & Smidt 1988（90 年道指证据）起跨市场复现；本项目月末/月初 ±2 交易日窗口与文献经典定义（约 -1~+3 日）同族，Welch+Bonferroni 的显著性自证符合日历异常检验的方法学正源（防 data-mining） | [Lakonishok & Smidt 1988, Are Seasonal Anomalies Real?, JSTOR 2962097](https://www.jstor.org/stable/2962097)（JSTOR，1988）；[Quantpedia: Turn-of-the-month in equity indexes](https://quantpedia.com/strategies/turn-of-the-month-in-equity-indexes)（Quantpedia，策略化口径） |
| 2 | 节后效应（长假） | **对等已有（A股语境）**——春节/国庆前后效应在 A 股实证文献常见（中文卖方金工独立矿脉，本次检索以英文源为主如实记；判"对等"基于效应类别存在性，非参数对齐） | 类别谱系见 [Emerald: TOM effect in emerging markets](https://www.emerald.com/mf/article/47/4/555/290750/Turn-of-the-month-effect-in-three-major-emerging)（Emerald，新兴市场日历效应族） |
| 3 | 周年日/时间对称窗口 | **驳回（作为统计效应）/保留（作为风险提示）**——高低点周年日的学术证据薄弱（Gann 时间周期谱系属民间方法）；本项目把它做成"波动抬升方向中性+显著性自证+不显著即禁消费"的风险提示而非方向信号——处置方式正确，保留其研究位不保留其方向语义 | Gann 时间分析谱系（公共域民间方法，无学术定源如实记）；模块扩展口自评 regime_cycle_analyzer.py:35-39 |

## 4 缺陷清单（按严重级）

- **F-A1（P2）日历 upcoming 窗口结构空缺**：现状=dates 截断使前瞻日历窗口产不出 → 证据=:453-463 与 dates 来源 → 影响=模块核心卖点"变盘窗口前瞻提示"只有周年日路径可用，日历路径退化成当日标记；爆炸半径=接线后的节流参考完整性 → 建议修法=日历窗口按 as_of+horizon 构造未来交易日历（或 pandas period 推断月末）生成前瞻窗口，统计仍只用 ≤as_of → 验证法=F-A1 复现命令。
- **F-A2（P3）肥尾/自相关 caveat**：接线前建议补 Newey-West 或块自助法稳健性（或文档声明近似性）→ 验证法=同数据双法对比 p 值。
- **F-C1（P3）接线时定义 confidence→节流映射**——常规队列。

## 5 挂起疑问

1. 三类日历假设在 A 股全样本上的实际显著性（evidence_table 真实输出）未取——若全部不显著则模块当前产出恒为空集（confidence=0），接线价值需先看数据。
2. registry v1.2.0 中 CYC-STAT-013 的"月末最后两个交易日"与代码 MONTH_EDGE_K=2 的一致性已抽验，registry 其余参数未逐条对账。

## 6 完备性自评

- 六轴全查：A（统计四问：Welch/Bonferroni/极值 PIT/周年口径+结构空缺发现）、B（纯输入无外部依赖+fail-closed）、C（声明态孤儿+防滥用契约）、D（registry 锚点）、E（静默面干净/确定性/时序保守）、F（3 条带来源，中文节后效应文献缺口如实记）。
- 长尾清单：①registry 全参数对账；②扩展口四族的证据强度评估未审（未落码）；③evidence_table 真实数据画像。
