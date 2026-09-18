---
ttl: task_bound
doc_type: report
title: 深度审查报告——机构行为分析器（S11）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：机构行为分析器（S11）

- 状态: **已审**
- 级别: P0｜类型: 算法
- 基线 commit: 2fa92002c3（审查时 HEAD=0aba088b65，本对象源文件基线后零变更）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_ashare/institutional_behavior_analyzer.py:93`（InstitutionalBehaviorConfig）/ `:218`（analyze 主入口）
- 生产调用方: **分析器类零实例化**（grep `InstitutionalBehaviorAnalyzer(` src/scripts 零命中）；仅 `BehaviorPhase` 枚举被 capital_behavior_orchestrator.py:59 复用（prod）；short_term_stock_selector 头注声明"数据字段级消费无 import"（:4）
- 测试文件: tests/signal_ashare/test_institutional_behavior_analyzer.py（27 用例，已审）
- 备注: 本批 12 件中变更热力最高（7 commits）；header :7 MATURITY=production、:10 STABILITY=stable 与"类体零调用"现状不符

## 1 对象快照

- **范围**：`institutional_behavior_analyzer.py` 全文 680 行——五维度启发式：6 阶段识别（建仓→洗盘→试盘→再洗盘→拉升→出货）、洗盘 vs 出货、诱多检测、主力 vs 游资、分时特征 + 综合评分。
- **排除项**：capital_behavior_orchestrator（六阶段推演状态机实现处，D 轴引用）；intraday_t0 消费方（头注级）。
- **测试覆盖概况**：27 用例（五维度+降级+审计留痕）。信任度：**信任（盲区=空大单数据与阶段跳跃序列）**。
- **材料包缺项声明**：无运行时证据包（类体无生产实例化）；真实大单数据分布未画像。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | **大单数据缺省=洗盘/出货双向加分**：`large_order_net` 默认空列表 → `_large_order_direction` 返回 0.0 → 洗盘判定 `lo_dir >= 0` 拿满分 30/35、出货判定 `lo_dir <= 0` **同样拿满分 35**——缺数据不是中性而是**双加分**：阶段识别系统性偏向洗盘/出货、洗盘 vs 出货两翼同时抬高（score 门槛 50 更易跨过）。且空列表是 dataclass 默认值（调用方不填即触发） | institutional_behavior_analyzer.py:171（默认空）、:614-618（空→0.0）、:373-374（洗盘 ≥0 加分）、:413-414 与 :449（出货 ≤0 加分）、:441 | **P1** | 同一 量/价 输入两份，一份 `large_order_net=[1e6]`、一份缺省 → 对照 `_score_washing`/`_score_distributing` 差 30 分；27 测试无一使用空 large_order_net（grep 实证） |
| A | **INVARIANTS"6阶段状态机不可跳跃"在本件无实现**：`identify_behavior_phase` 无状态、逐窗口独立对 6 阶段打分取 max（:343），单日可直接判"拉升/出货"而无任何前序阶段约束；真正的六阶段推演状态机在隔壁 capital_behavior_orchestrator 实现（"推演不跳跃" :25-27）——本件头注契约虚假+状态机语义双承载（checklist#4） | institutional_behavior_analyzer.py:8（INVARIANTS）vs :305-347（无状态打分）；capital_behavior_orchestrator.py:25-27 | **P2** | 构造放量+大涨单窗口输入 → 直出"拉升"（无建仓史）；对照 orchestrator 的推演实现 |
| A | **overall_score 语义含混+文档漂移**：docstring"加权融合5维度"，实现 4 维（0.30+0.25+0.20+0.25=1.0，维度5 分时特征权重为 0）；无诱多时该项恒给 100×0.20=20 分保底——分数不是任何事件的概率， mixes 置信度与补偿分；INVARIANTS 未定义其语义 | institutional_behavior_analyzer.py:630-652 vs :203-208（"5维度分析"） | P2 | 空 input 变体对照 overall_score 分解 |
| A | `_recent_price_change_pct`=全窗口 (last-first)/first，并非"近期"——窗口语义完全由调用方注入决定（日线 60 日 vs 分时 30 分钟产生完全不同的"涨幅"），契约未文档化 | institutional_behavior_analyzer.py:608-612 | P3 | 同一股票不同窗口长度对照 price_change_pct |
| A | 主力/游资主导度非互斥（两者可同时 ≥0.6，先判主力）；STALEMATE 置信度硬编 50.0（无信息量伪造中值） | institutional_behavior_analyzer.py:528-535 | P3 | 构造双高输入对照 |
| A | bull_trap 峰值取 `prices.index(max)` 首个最大值（并列取早）；峰在首尾 → False（无反转空间，合理）；均平序列 peak_idx=0 → False（防误报 ✓） | institutional_behavior_analyzer.py:475-477 | —（已查无，正面） | 全平序列输入 |
| A | A 股口径正面：分时段 9:30-10/10-11:30/13-14/14-15 正确排除午休 11:30-13:00（:148-153）；大单阈值 50 万元可配置（:156）——口径正确 | institutional_behavior_analyzer.py:148-156、:558-575 | —（正面） | 午休时间戳不落入任何段 |
| A.3 | 测试盲区：无空 large_order_net 用例（P1 正中）、无阶段跳跃序列用例（P2-1）、无 overall_score 分解校验；27 用例对正常路径覆盖全 | tests/signal_ashare/test_institutional_behavior_analyzer.py | P2（随 P1 修复补测） | grep 无 `large_order_net=[]` 用例 |
| B | 输入契约：prices/volumes/timestamps 等长且 ≥2 fail（bool 校验→degraded+日志 ✓ 兑现 INVARIANTS"降级必须有日志"）；`market_sentiment_score` 输入字段**声明后从未被消费**（全文仅 :173 一处出现）——死输入误导装配方 | institutional_behavior_analyzer.py:173、:585-594 | P3 | 全文 grep market_sentiment_score 仅 1 处 |
| B | timestamps 时区未约定（naive datetime 假设本地盘口时刻）——跨时区注入会静默错段；隐式契约未文档化 | institutional_behavior_analyzer.py:561-565 | P3 | 注入 UTC 时间戳 → 分时特征全错段 |
| C | **孤儿裁定（生死分离态）**：分析器类零生产实例化（本件空转）；枚举被 orchestrator 复用（活）；short_term_stock_selector 字段级消费（无 import 弱耦合）。MATURITY=production/STABILITY=stable 标签与"类体零调用"不符——本批第 4 例标签漂移（S03/S05/S08 同族） | 全仓 grep；institutional_behavior_analyzer.py:7、:10 | P2 | grep `InstitutionalBehaviorAnalyzer(` 零命中 |
| C | 爆炸半径：若按字段级消费（short_term_selector 读同名产出字段），当前实现与消费方之间**无契约测试**（无 import 依赖=无编译期保障，checklist#9 幽灵引用温床） | institutional_behavior_analyzer.py:5、short_term_stock_selector.py:4 | P3 | 对照两处字段清单 |
| D | 兄弟盘点：capital_behavior_orchestrator（状态机真身）、capital_flow_pattern_analyzer（资金流形态）——三者构成 D-SIGNAL-21 族；本件与 orchestrator 的阶段判定口径无对账测试（同一股票两处阶段结论可分歧） | capital_behavior_orchestrator.py:25-27 | P3 | 同输入双跑对照阶段输出 |
| E | 静默失败面：P1 双加分为主；校验失败 degraded+日志 ✓；无墙钟（datetime 仅类型注解）；类无状态幂等——其余已查无 | institutional_behavior_analyzer.py:218-299 | P2（并入 P1） | — |
| F | 主力行为学 6 阶段（建仓/洗盘/试盘/再洗盘/拉升/出货） | **受阻**：检索限流；该体系为 A 股散户-主力博弈叙事的本土实践（无英文学术标准化模型），"理论依据：主力行为学/市场微观结构/行为金融学"（:33）为叙事性引用非可检源 | 本战役检索记录 2026-09-18 | 收口方如需可检索中文卖方"主力行为"专题研报 |

## 3 SOTA 对照

| 对照项 | 结论 | 来源 |
|---|---|---|
| 6 阶段主力行为状态机 | **受阻**（本土叙事体系，无标准化学术对照；检索限流） | 本战役检索记录 2026-09-18 |
| 量价分档启发式打分 | **对等已有（工程惯例级）**：阈值带状打分是规则引擎常规做法；全部阈值显式可配+来源声明（设计文档 §D-SIGNAL-21）符合可审计要求 | 本件 :35-36、:96-156 |
| 订单流不平衡（lo_strength=sum/Σabs ∈[-1,1]） | **对等已有**：与订单流不平衡（OFI）简化口径同构（席位级数据缺失下的近似） | 本件 :521（实现；学术 OFI 文献未检索，受阻附注） |

## 4 缺陷清单（按严重级排序）

1. **P1｜大单数据缺省双向加分（缺数据≠中性，缺数据=洗盘+出货同时+分）**
   - 现状：`large_order_net` 默认空 → lo_dir=0.0 同时满足洗盘 ≥0 与出货 ≤0 → 双向满加分；阶段识别系统性偏向洗盘/出货。
   - 证据：institutional_behavior_analyzer.py:171、:614-618、:373-374、:441、:449。
   - 影响与爆炸半径：装配方不注入大单数据（默认即空）→ 五维度中两维度带系统偏置 → current_phase/wash_distribute 判定偏移 → 字段级消费方（短线选股）带偏决策。
   - 建议修法：`_large_order_direction` 空数据返回 None；洗盘/出货的大单加分项在 None 时不加分（而非 0 值双真）；补空数据用例。
   - 验证法：同量价输入±空大单对照 `_score_washing` 分差（30 分）。
2. **P2｜INVARIANTS 声明的状态机不存在于本件**（真身在 orchestrator）：修头注（指向 orchestrator 或降级表述为"无状态单窗口识别"）；验证法=单窗口跳跃输入。
3. **P2｜overall_score 4/5 维度+保底 20 分语义含混**：文档对齐或重构评分；验证法=分数分解。
4. **P2｜生死分离孤儿态+标签漂移**：类体无实例化但 MATURITY=production/stable；接线或降级标注；验证法=grep。
5. **P3｜窗口语义未文档化/market_sentiment_score 死输入/时区未约定/STALEMATE 置信 50 硬编/两处阶段口径无对账**；验证法=§2 对应行。

## 5 挂起疑问

- 设计文档真源 `D:\临时工作区\依赖图-D-SIGNAL-信号域.md`（:36 引用）为盘外路径——仓库内不可达，阈值默认值的可追溯性断链（疑为迁移前遗留，需 Owner 确认归档位置）。
- short_term_stock_selector"字段级消费"的具体字段清单与产出方未对账（无契约测试）。
- 7 commits 变更热力的具体内容未逐条深挖（批内最高，建议收口方抽查是否有算法性返工）。

## 6 完备性自评

- 六轴全查：是（F 轴受阻如实记）。
- 长尾：①盘外设计文档追溯；②orchestrator 推演状态机本体审查（建议单列对象）；③真实大单数据画像。
- 变更热力：7 commits（批内最高）——创建+多次锚点/重构批；未逐条定性，登记中等热度。
- 测试审查结论：信任（27 用例覆盖面广；盲区=空大单/跳跃序列，恰为 P1/P2 所在）。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
