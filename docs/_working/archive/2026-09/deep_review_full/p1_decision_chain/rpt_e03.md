---
ttl: task_bound
title: 深度审查报告——止损策略（E03）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：止损策略（E03）

- 状态: **已审**
- 级别: P1｜类型: 卖出族止损（#309 MVP 三件套之"ATR+移动止损"）
- 基线 commit: 2fa92002c3（工作树 bf65648609；本文件自基线零变更，锚点双有效）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- **裁定#309 约束声明**：卖出族整族挂起（ruling_registry.yaml:3833-3839）；本件属 MVP 三件套"维持生产"档——但 grep 实证生产调用方为零（见接线现状），"维持生产"实为名义态，修复仍受裁定流程约束。
- 入口锚点: `src/zephyr/sell_decision/core/stop_loss_strategy.py:121(validate_position_snapshot)/:148(compute_stop_loss)/:205(check_time_stop)`
- 接线现状（grep 实证）：包外零导入——引用仅包内（take_profit_strategy.py:48、stop_hunting_protector）+测试；与 E01/E02 同族结构性空转。
- 测试文件: tests/sell_decision/test_stop_loss_strategy.py
- 材料包缺项: 无

## 1 对象快照

- 范围：Chandelier Exit 止损计算（亏损区 N=10/M=3.0、盈利区 N=22/M=2.0、策略类型 M±0.5、ATR 缺失降级固定%）+ ATR 自适应时间止损（5 天 1×ATR）。输入校验共用件 validate_position_snapshot。
- 测试覆盖概况：专测在位；ATR 缺失降级锚点缺陷（见 §4-1）预计无专测。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | **ATR 缺失降级锚在 entry_price 而非最高收盘——盈利期止损线悬崖下移**：Chandelier 主路=Highest_Close(N)−M×ATR（随盈利上移）；降级路=entry×(1−4%/8%)（:182-191）。浮盈 50% 的持仓 ATR 断供时，止损从"最高收盘−2×ATR"（远高于入场）瞬间跌到入场价下方——全部浮盈裸奔且只留 debug 级日志（:186-190）。降级应为"锚点同构降级"（如 highest_close×(1−pct)）而非回到入场锚 | stop_loss_strategy.py:182-191 vs :202 | **P1** | 构造 entry=10/current=15/ATR=None/phase=PROFIT → 止损=9.2（<入场价），对比 ATR 在位时的止损线 |
| A | 降级固定%不看 phase：亏损/盈利两相同用 entry 锚（:183-185 只按 strategy_type 选 4%/8%）——与主路"phase 定参数"的结构不对称，同根缺陷 | stop_loss_strategy.py:182-191 | P2（并入缺陷 1） | 同上 |
| A | Chandelier 用 Highest_Close 而非业界常见的 Highest_High——收盘锚更钝（噪声小、触发晚），属可辩护变体但与"Chandelier Exit"教义名的差异未在 docstring 声明 | stop_loss_strategy.py:156, :202 | P3 | 读 docstring 对照 |
| A | 时间止损语义："净有利移动<1×ATR 且 ≥5 交易日"→FORCE_EXIT_EVALUATION（:232-248）——用净涨跌近似"未向有利方向移动"，忽略路径（先涨 3×ATR 再回吐到 <1×ATR 仍触发，合理；震荡净零也触发，符合意图）；ATR 缺失降级 1% 阈值锚 entry（:236）——此处锚 entry 语义正确（衡量的是相对入场的移动） | stop_loss_strategy.py:232-248 | 已查无（正面） | — |
| A | M 调整边界：均值回归盈利相 M=2.0−0.5=1.5、亏损相 3.0−0.5=2.5；趋势 3.5/2.5——均>0 无穿仓负止损风险；ATR 极大时止损线可为负（无 max(0) 钳制）——负价止损=永不触发，语义上无害但应显式 | stop_loss_strategy.py:131-141, :202 | P3 | ATR>highest_close/M 构造 |
| A.3 | 专测在位；降级路径断言预计只验"返回 entry×(1−pct)"（把缺陷 1 的行为固化为预期）——测试正确性存疑点：绿≠对（defect checklist #3 同族） | tests/sell_decision/test_stop_loss_strategy.py | P2 | 读降级用例断言 |
| B | 输入校验 fail-closed 齐（symbol/prices/fn/phase/holding_days，:121-129, :176-179, :229-230）；highest_close_fn 返回值零校验（回调返回 0/负→止损 0/负）——上游断供行为未防御 | stop_loss_strategy.py:176-177, :202 | P3 | mock fn 返回 0 |
| C | 下游：包内 take_profit/stop_hunting_protector；生产包外零调用——爆炸半径当前为零；接电后缺陷 1 直接作用于真仓止损线 | grep 实证 | P1（接电后，族级挂起中） | 同族验证法 |
| D | 与 risk 域 default_stop_loss_engine 并存"分层防御"（:33-34 头注声明）——两套止损真源分工有声明；42 号 memo §7 待定问题登记在案——双实现漂移面已自觉，未见对账机制 | stop_loss_strategy.py:33-34 | P3 | grep default_stop_loss_engine 对照 |
| E | 重入/重放：静态方法零状态；日志级别——降级 debug（:186）、时间止损 info（:241）：降级是资金相关状态切换却比时间止损更安静，日志分级失当 | stop_loss_strategy.py:186, :241 | P3 | 读日志分级 |
| E | A 股口径：固定%降级参数引 eastmoney 2026-07（4%/8% 短中长线）有出处；跌停日止损触发后能否成交归执行面（同族前置项）；T+1 不影响止损价计算本身 | stop_loss_strategy.py:77-79 | 已查无 | — |

## 3 SOTA 对照

1. **Chandelier Exit / ATR 移动止损（对等已有）**：ATR 自适应止损为实证充分的主流做法——Quantified Strategies《ATR Bands Strategy》33 年回测（实践验证，2024，https://www.quantifiedstrategies.com/）；ATR trailing stop（Chandelier 式）工程口径广泛（PyQuantLab/TrendShift 指南，2024-2025）。本件参数（10/3.0、22/2.0）在业界常用 22/3.0 邻域，MVP 值有 42 号 memo 背书。
2. **ATR 断供降级（驳回现状）**：业界降级路径应保持"锚点结构等价"（volatility-scaled sizing 的 inverse-ATR 文献口径：停距变→仓位反变，mental-momentum.ai《Dynamic Position Sizing Across Volatility and Risk Regimes》，2024，https://arongroups.co/forex-articles/dynamic-position-sizing/）——本件降级切换锚点结构（highest_close→entry）属偏离，判"立卡即改"（见缺陷 1）。
3. 结论：主算法对等已有；降级路径立卡即改。

## 4 缺陷清单

1. **[P1] ATR 缺失降级锚点错位（盈利期止损悬崖下移到入场价下方）**
   - 现状：降级止损=entry×(1−4%/8%)（:182-191），与主路 Highest_Close 锚结构断裂；浮盈越深，降级造成的止损线下移越狠。
   - 证据：:182-191 vs :202；触发剧本：ATR 数据断供日（checklist #6 数据源静默死亡）恰逢持仓浮盈→止损线从锁利位跳回入场下方，只留 debug 日志。
   - 影响：接电后=风险收敛件在最需要时失效（不报错只亏）；当前族挂起+零调用，实际爆炸半径为零。
   - 建议修法：降级改为 `highest_close_fn(N_eff) × (1 − pct)`（盈利相 N 取 22，亏损相 10 或 1）；日志升 WARNING；验证法：§2 首行构造复演。
2. **[P2] 降级不区分 phase**（并入缺陷 1 修法）——证据 ：183-185。
3. **[P2] 降级行为可能被测试固化为预期**——验证法：读 tests 断言；修缺陷 1 时同步改测试。
4. **[P3] highest_close_fn 返回值零校验**（:202）——建议：结果 ≤0 时 raise 或钳 0.01；验证法：mock 返回 0。
5. **[P3] 降级日志 debug 级**（:186）——建议 WARNING+计数进证据；验证法：日志级别断言。
6. **[P3] 与 risk 域 default_stop_loss_engine 双实现无对账机制**（:33-34）——验证法：两模块参数 diff。
7. **[P3] Highest_Close vs Highest_High 教义差异未声明**（:156）——文档级。

## 5 挂起疑问

1. 缺陷 1 修法方向（highest_close 锚 vs 维持 entry 锚+仓位联动缩量）需 Owner 裁定——后者把风险预算恒定化，改动面大。
2. 本件在裁定#309 中"MVP 维持生产"与"生产零调用"的矛盾——是名义维持还是应入退役清点？收口时一并对账。
3. strategy_type=SHORT_TERM 之外全部吃 8% 长线降级——类型枚举与 fallback 映射是否完备？

## 6 完备性自评

- 六轴全查：是（小对象全量逐行+两算法四问）。长尾：①SellPositionSnapshot 定义（E05 对象）；②stop_hunting_protector 消费方式（族内兄弟）；③42 号 memo §7 待定问题全文未追。

## 7 收口裁定（收口方填）
- 三态逐条:
- 修复 commit:
- 复检结论:
