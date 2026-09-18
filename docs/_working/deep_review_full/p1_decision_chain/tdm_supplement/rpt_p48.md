---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——价格锚定
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：价格锚定（P48）（GLM-5.3-Flash / 基线 2fa92002c3）

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（目标文件零漂移已核）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/ex_core/pricing_policy.py`
- TDM 节点: TDM-E-L4-03（stage）
- 备注: 阶段0对账补册对象（T08 缺口清册）；MOD-L06-001，40 号 §决策⑭ gap 9 施工
- 生产调用方: **0（精确 import grep 零命中——头注 [CONSUMERS] 声明的 trading_session/miniqmt_broker/open_order_resolver 三方均无 import；board_lot/price_cage 头注互认为声明文本。与 X02/X03/X05 同属 ex_core 执行链零接线族，但本件头注消费方为虚标（非"候选"诚实声明））**
- 测试文件: `tests/ex_core/test_pricing_policy.py`（22 用例，本班次实跑 22/22 绿）

## 1 对象快照

380 行五档挂单价决策器：被动档（己方最优价）/主动档 Make-or-Take（对手价）/涨停卖挂涨停/跌停买挂跌停/提 1tick 中间档；盘口回退链 last→prev_close→己方±tick 估算；Decimal 全程；与价格笼子解耦（调用方校验声明 :46-50）。设计 rationale 充分（为何被动档/为何不挂 mid，:35-44）。测试覆盖：五档+回退链+异常。排除项：price_cage 深审（X05 域已审）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | 数学①：五档映射表与 40 号 §2.15 决策⑭逐行一致（:24-33 对照 :93-97）；回退链有序降级全程 reason 留痕（审计友好成立）；ONE_TICK_INSIDE 买卖方向加减 tick 正确（:284-291） | pricing_policy.py:24-33,93-97,284-291 | 通过 | 对照规则表 |
| A 深度 | **取整口径②实锤：`_round_to_tick` 用 `quantize(PRICE_TICK)` 默认 ROUND_HALF_EVEN（银行家舍入）而 A 股申报价=四舍五入——本班次实测 prev_close=9.55 涨停估算 10.505 → 本件出 10.50，同仓 tradability_preflight（ROUND_HALF_UP 显式声明）出 10.51，差 1 tick**；触发点=涨停/跌停价估算退化路径（limit_up_price 缺失时）——挂单价≠交易所涨停价，"唯一可成交价位排队"语义破坏 | :149-151,228-235 | P2 | 本报告命令复跑：`PricingContext(prev_close=Decimal('9.55'))` LIMIT_UP_SELL→10.50 vs preflight 10.51 |
| A 深度 | 口径③：涨停估算 `_DEFAULT_LIMIT_UP_PCT=0.10` 对 20cm（创科）/30cm（北证）板块一刀切（:142-146 注释自declared"通用 10% 估算，调用方应优先传入精确涨停价"+真源指针 board_lot/miniqmt_broker）——**本件不消费 classify_board 真源**，20cm 票走退化路径时涨停价估低 10%；有 warning 留痕属声明式简化 | :142-146,228-235 | P3(接线期收紧) | STAR 票缺 limit_up_price 观察 ×1.1 估算 |
| B 上游 | checklist #6 断供：盘口快照全注入；全 None→PricingPolicyError 显式（:314,335）；limit 价缺省回退有 warning——断供链有痕 | :237-239,314,335 | 通过 | 全 None 上下文观察 raise |
| C 下游 | **孤儿裁定（虚标型）：零生产 import 且 [CONSUMERS] 三方虚标、[MATURITY]=production 失实**（checklist #8 最重形态——比"候选/待接线"诚实声明误导性强：接线路径图上本件显示已挂接）；爆炸半径=拆单算法（X04/X06）落地时挂单价最后一公里缺位 | grep 证据 | P1(接线期)+P3(标签失实) | `grep -rn "from zephyr.ex_core.pricing_policy import" src/ --include=*.py` |
| D 旁系 | checklist #4 双承载：涨跌停幅度表在 miniqmt_broker._BOARD_PRICE_LIMIT_PCT（:143 注释指认真源）与本件 _DEFAULT_10% 估算双承载——真源在 broker 件而本件不读（解耦声明，但 10% 兜底与真源表的偏离无一致性校验）；与 P42 tradability_preflight 的取整口径分歧（HALF_EVEN vs HALF_UP）=**同仓两套申报价取整惯例并存** | :142-146 vs tradability_preflight.py:116-117 | P2(同取整案) | 对照两文件取整 |
| E 对抗 | 五问：①静默失败=无（回退全 warning/raise）②假阳性=HALF_EVEN 涨停价差 1 tick（实锤）→ 涨停排队单挂错价③断供=盘口全 None raise④重触发幂等（纯函数）⑤时序=盘口快照时点由调用方负责（无 stale 检测——陈旧盘口挂单风险声明外） | :310-313 | P2(同②) | — |
| F 新鲜度 | Make-or-Take/被动档优先为小单执行标准打法（spread 成本经济学正确）；不挂 mid 的论证（A 股 0.01 tick 约束）正确；涨跌停排队单为 A 股特色（对照 X09 SaR 结论同源）；**对等已有（执行微观结构常规）** | 执行算法族结论（URL 见 rpt_p50 F 轴 TWAP/VWAP 检索） | 通过（同族复用） | — |

## 3 SOTA 对照

- 对等已有：被动档默认+主动兜底+涨跌停特殊档与执行算法文献及 A 股实务一致；无立卡/驳回。

## 4 缺陷清单

1. P2：**tick 取整 HALF_EVEN 与交易所四舍五入不一致**（实测 10.505→10.50，同仓 P42 为 10.51）——建议 `quantize(PRICE_TICK, rounding=ROUND_HALF_UP)` 对齐 P42 惯例；验证法=本报告 §2 A 轴命令。
2. P1（接线期）：零生产 import 孤儿+[CONSUMERS]/[MATURITY] 双虚标——建议接线（TWAP/VWAP 子单定价挂接点）或降级 testing+如实头注；验证法=§2 C 轴 grep。
3. P3：涨停估算 10% 一刀切不读 board 真源（20cm/30cm 退化路径估低）——接线时改用 classify_board 查表；盘口快照无 stale 时效检查。

## 5 挂起疑问

- PRICE_TICK 常量 0.01 对北交所/ETF（0.001 tick）是否适用——ETF/债券 tick 不同，本件按股票口径写死，接线扩展品种时须参数化（与 P42 min_order_unit 同族多品种适配债）。

## 6 完备性自评

六轴全查（F 同族复用 P50 检索）。长尾：①22 测试全用 10% 板案例（20cm/30cm 取整与估算路径零覆盖）②ONE_TICK_INSIDE 标注 Phase 1.5 候选未裁定启用③与 order_splitter（X06）切片价的集成契约未定义。

## 7 收口裁定（收口方填）
