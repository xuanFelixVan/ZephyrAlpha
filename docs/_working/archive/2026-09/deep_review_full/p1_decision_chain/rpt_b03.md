---
ttl: task_bound
title: 深度审查作业簿——撮合引擎
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：撮合引擎（B03）

- 状态: **已审**
- 级别: P0｜类型: 内核（撮合价虚优=成绩造假源头的重点专项）
- 基线 commit: 2fa92002c3（对象文件基线/HEAD/工作区零漂移）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/backtest/core/matching_engine.py:152`（MatchingEngine 主体 :271 起）；共享数学真源 `matching_logic.py`（626 行）同批实读
- 生产调用方: vectorized_engine（日频 generate_fills，含 liquidity+limit_provider 注入）、event_driven_engine（tick 路径，**无 liquidity/limit_provider 注入**）、miniqmt_broker（MatchingLogic 实盘共享）
- 测试文件: tests/backtest/test_matching_engine.py（400 行）+test_matching_logic.py（540 行，golden 值/边界/部分成交/零流动性断言齐备，本批运行全绿）+test_cost_model_wiring.py
- 备注: 数学四问以 matching_logic 纯函数层为准

## 1 对象快照

- 范围：generate_fills 三入口、_build_target_orders（差额+清仓补全）、_limit_bounds 三级解析链、LiquidityGuard（参与率+A-C 冲击）、_clamp_buys_to_projected_cash、StkLimitProvider、MatchingLogic 三撮合函数+费率常量真源。
- 排除项：almgren_chriss_impact_model/cost_model_calibration 内部标定数据（只审接线与方向，不复核标定表数值——归 #23 H2 台账）。
- 材料包缺项声明：标定真值表未复核；运行时证据包未取。
- 变更热力：22 commits，末次 2026-09-16。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | **数学四问总评（撮合价模型）**：日频=合成1档盘口（ask1=bid1=当日 open 优先），成交基准非"当日收盘拍脑袋"而由上游 P0-1 滞后保证；滑点分层 2.34~7.24bp 按当日成交额落档、方向只严不松（matching_logic.py:91-99 方向纪律）；无流动性信息落全市场名义加权 3.79bp 不回退 1bp——"虚优=造假"主通道已被 #23 H2/P0-2 封堵 | matching_logic.py:69-116,515-555；matching_engine.py:360-408 | 通过（残余通道见下行） | test_buy_golden/test_sell_golden golden 值复核 |
| A | **残余虚优通道①：容量约束三条件与门**（liquidity_config 非 None + volumes 传入 + 非 tick_mode），任一缺失即旁路；vectorized 注入了 config，但 volumes 由数据有无决定（无 volume 列=无约束）。tick 路径（event_driven）构造 MatchingEngine 未传 liquidity_config——靠 5 档档位量自然约束，CH 1 档降级后=单档量约束（见 B07 联动） | matching_engine.py:625-633；vectorized_engine.py:196-199,283-289,328-335 | P2 | 无 volume 列跑日频回测 grep "P0-2 成交量上限" 零命中 |
| A | **残余虚优通道②：tick 模式不做涨跌停检查**（prev_close=None，注释称"Tick 内已含状态"），但 grep 实证 **TickSnapshot.stock_status 全仓零消费方**——封板保护完全依赖盘口自然为空；若数据源封板仍给 ask 价+量（部分源聚合快照如此），tick 模式会在涨停价照常成交 | matching_engine.py:485,601-604；grep stock_status src/zephyr/backtest/ 仅字段声明 | P2 | 构造 ask_price=涨停价的 TickSnapshot 调 generate_fills_with_tick 看是否成交 |
| A | **通道③：参与率越界/冲击报价失败按"无冲击成交"**（warning 不阻断不计数）——引擎 docstring 自认"成本被系统性低估"且 MUST 显式化，现状仅日志 | matching_engine.py:855-878 | P3 | 构造 order qty>volume×1 的订单看 warning 后成交价 |
| A | 涨跌停三级链数学核验：中点法 ref=(limit_up+limit_down)/2 恢复 prev_close 对 A 股 ±对称板成立（ST 5%/主板 10%/北交 30% 均对称）；复权缩放走 prev_close×(1±pct) 等价式推导正确（等比平移精确非近似）；ROUND_HALF_UP 与交易所取整一致；判据"误为不同纲"无害性论证成立 | matching_engine.py:1029-1094（docstring 数学推导） | 通过 | 低价股（2元）边界：0.01 取整噪声 0.5% >_LIMIT_REF_TOL 0.2% → 误判不同纲走等价式，数值仍正确（自洽） |
| A | 费用模型：佣金 max(万0.854×额,5元)+过户费万0.1双向+印花税万5卖出单边——与 2023-08 后 A 股法定一致；买入整手/卖出零股方向正确；BacktestFill.total_cost 滑点双计已修（AI-NIGHT-001） | matching_logic.py:557-581；portfolio.py:126-137 | 通过 | test_buy_large_order_commission_above_min |
| A.3 | 测试审查：matching_logic 测试含 golden 值/边界（equal ask/bid）/部分成交/零档跳过，强度高；matching_engine 测试 400 行覆盖涨跌停方向感知/清仓补全（本批运行全绿）；缺口=liquidity 三条件与门的正交组合测试、tick 模式涨停价成交测试（对应上两发现） | tests/backtest/test_matching_logic.py:104-399;test_matching_engine.py | P2 | 跑 `python -m pytest tests/backtest/test_matching_logic.py tests/backtest/test_matching_engine.py -q` |
| B | StkLimitProvider fail-open：provider 异常→warn+{}→规则兜底（无 ST 快照时主板 ST 按 10% 板误判，贴板可成交=虚优窄门）；st_stock_list 空结果降级记忆 `_degraded` 终身不重试 | matching_engine.py:984-1001,1264-1270 | P2 | mock ch_reader.query 抛错，看 ST 标的 5% 板判定 |
| B | SQL f-string 拼接 symbol/日期（内部受控输入，注入面低） | matching_engine.py:1188-1196,1207-1211 | P3 | 代码审读 |
| C | 消费方=两引擎+实盘 broker（MatchingLogic 共享）——回测改口径会同时改实盘预演行为（一致性设计本意，但也是爆炸半径：回测侧修 bug 若引入偏差直接入实盘链路） | matching_logic.py:19-23;matching_engine.py:5-6 | 亮点/警示 | grep MatchingLogic 消费方 |
| D | 费率常量单点真源（万0.854/万5/万0.1/5元地板，#233 裁定，BacktestConfig 同源引用零字面量复写）；涨跌停口径禁第四份声明与实现一致——已查无双真源复发 | matching_logic.py:62-76;vectorized_engine.py:138 | 已查无 | grep "0.0000854" src/ 应仅 matching_logic 一处 |
| E | _clamp_buys_to_projected_cash 投影口径与实际撮合同源 slippage_bps_for（防满仓误拒）✓；但投影不含冲击腿（冲击调价发生在 cap 之后的 books 上，sizing 仍用未冲击价）→ 高冲击满仓场景买单仍可能超支被 Portfolio 拒——有 H4-D 计数兜底，非静默 | matching_engine.py:657-720,643,631-634 | P3 | 满仓+低流动性标的手算投影 vs 实际成本 |
| E | tick 模式部分成交（filled=False 但 quantity>0）也应用（:653）——与限价单"完全成交才应用"分流正确 | matching_engine.py:646-655 | 通过 | test 部分成交用例 |
| A(亮点) | 涨跌停方向感知（涨停拒买不拒卖/跌停反之，2026-08-19 修）、清仓补全（2026-08-19 P0：滞留仓强制平仓） | matching_engine.py:236-267 | — | — |

## 3 SOTA 对照

- 撮合价模型（order book walk + 参与率上限 + 冲击调价）：**对等已有**——与 NautilusTrader 限价簿撮合/VectorBT 容量约束同构；A-C 冲击复用 execution_simulation 真源。（来源：NautilusTrader https://nautilustrader.io/ ，2026；Implementation Risk in Portfolio Backtesting, arXiv:2603.20319, 2026）
- 成本分层标定（ADV 五分位滑点+层标定冲击、两腿互斥 INV-COST-LEGS）：**对等已有（偏上）**——业界多为单一 slippage bps，双腿互斥可加+标定真源的做法接近机构级（对照 QuantInsti 交易成本综述面）；tick 模式价差腿已含于盘口再叠加 bps 滑点存在双计嫌疑（方向保守），建议在 INV-COST-LEGS 文本中澄清 tick 模式语义。（来源：Cross Validation in Finance 之外的成本面：QuantOpenSource 框架对比 waylandz.com, 2026）
- 涨跌停复权缩放不变式（中点恢复 ref + 等价收益空间式）：**立卡候选（反向输出）**——A 股特有约束的缩放不变处理在主流开源引擎（无 A 股原生支持）中无对应物，可沉淀为 A 股适配知识卡。

## 4 缺陷清单

1. **[P2] tick 模式涨跌停检查缺位 + stock_status 零消费**：封板保护仅靠盘口自然为空，数据源形态变化即破。建议修法：tick 模式至少消费 stock_status 停牌位 + 以 tick_data.prev_close（真实昨收，CH 侧当前伪造见 B07）做封板价比对。验证法：§2 轴A 通道②验证法。
2. **[P2] 流动性约束三条件与门，旁路显影弱**：建议修法：volumes 缺失时 warn 升级+计数进产物（对齐 H4-D 纪律）。验证法：§2 轴A 通道①。
3. **[P2] StkLimitProvider 双重 fail-open**（provider 异常→规则兜底；ST 快照空→非 ST 口径）：贴板 ST 股可被虚优成交。建议修法：降级事件计数+在 BacktestResult 产物附 provider 健康位。验证法：§2 轴B。
4. **[P3] 参与率越界/冲击失败"无冲击成交"仅日志**；sizing 投影不含冲击腿；SQL 拼接注入面。

## 5 挂起疑问

- tick 模式 5 档消化后再叠加 bps 滑点（matching_logic.py:498）：价差成分疑似双计（方向保守不造假，但成本口径与 INV-COST-LEGS"互斥可加"声明存在张力）——需 Owner 裁定语义。
- MatchingLogic 同改实盘链路：回测侧若按本报告修 tick 涨跌停检查，实盘 MiniQmtBroker 预演行为是否需同步评估（一致性设计使修复面扩大）。

## 6 完备性自评

六轴全查。长尾：①cost_model_calibration 标定表数值真伪（需实证数据）未复核；②test_cost_model_wiring.py 未逐断言；③almgren_chriss 模型内部数学（引用型，归 execution_simulation 域对象）；④miniqmt_broker 侧共享路径只核对引用不审实盘行为。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
