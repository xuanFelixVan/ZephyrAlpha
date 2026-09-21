---
ttl: task_bound
title: 深度审查作业簿——可交易性预检
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：可交易性预检（P42）（GLM-5.3-Flash / 基线 2fa92002c3）

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（目标文件零漂移已核）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_ashare/tradability_preflight.py`
- TDM 节点: TDM-E-L3-10（stage）
- 备注: 阶段0对账补册对象（T08 缺口清册）；MOD-SIG-151，Owner 2026-09-16 裁定开工
- 生产调用方: **0（grep 全仓仅自命中；头注 [CONSUMERS] 为 TDM 节点语义声明非实际接线）**
- 测试文件: `tests/signal_ashare/test_tradability_preflight.py`（15 用例，本班次实跑 15/15 绿）

## 1 对象快照

277 行五查聚合专件：停牌/涨停（一字封死或意图价触板）/板块权限/资金一手/价格笼子（夹边建议价非拒单）。全 Decimal、fail-closed（prev_close/min_order_unit 缺失=DATA_MISSING 不可交易）、快照全注入零 DB。板块判定唯一真源=board_lot.classify_board；涨跌停比例表（主板 10/ST5、创科 20、北证 30）与 ST 分档齐全。笼子显式传 prev_close 基准价（X05 实盘路径恒 UNKNOWN 缺陷在此被正确规避=对照正例）。测试覆盖：五查分支+降级 detail。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | 数学①：涨停价 `round2(prev×(1+ratio))` ROUND_HALF_UP 与沪深交易所四舍五入至分口径一致（:116-117,133）；比例表主板 10%/ST5%、创科 20%、北证 30% 及 ST 分档（:68-73）与 A 股规则一致 | tradability_preflight.py:68-73,116-117,133 | 通过 | 手算 10 元主板涨停 11.00 |
| A 深度 | 边界②：prev_close 缺/非正→DATA_MISSING fail-closed（:130-131）；min_order_unit 缺→DATA_MISSING（:173-174）；一字判定 `open==high and low>=limit_up`（low≤涨停恒真故=等值判定）正确；意图价恰触板 `>=limit_up` 判不可买偏保守（reason 文案诚实"排队未必成交"） | :130-144,173-174 | 通过 | tests 已覆盖 |
| A 深度 | A 股口径③：**一字板判定要求 OHLC 三值齐备（:135-138 任一 None 即跳过一字判定）——快照只给 open/high 缺 low 时不判一字**（隐性三值齐契约未文档化）；意图价触板判定在 intended_price=None（池过滤默认路径）时跳过=默认路径只查一字不查触板（语义分层合理但未写明默认路径的检查强度） | :135-138,142 | P3 | 只给 open/high 观察 TERM 一字漏判 |
| B 上游 | checklist #6 断供：快照注入（instrument_master 口径自declared :4/:78——**两件均未接线，"口径对齐"当前为纸面互认**）；account 缺失→权限/资金查降级 detail 不阻断（:8 声明，下单层 L4-12 复检兜底声明在案）——降级链文档化良好 | :4,8,78,151-159 | 通过 | — |
| C 下游 | **孤儿裁定：生产零调用方**；下游=候选池日频过滤（L3-10→L3-08 上游语义）；爆炸半径=选股层预检缺位时下单层空转报错（:21-23 立项动机）；tradable=False 时 blocked 必非空的裁决不变量成立（:271-277 构造保证） | grep 证据 | P1(接线期) | `grep -rn "preflight_tradability" src/ --include=*.py` |
| D 旁系 | checklist #4 双承载：涨跌停比例在本件 `_LIMIT_RATIO_BY_BOARD`（:68-73）与 P33 的 9.5% 硬编码、P32 DDL 注释三处承载——**全仓涨跌幅规则无唯一真源**（本件最完整但未立真源地位）；与 price_cage/board_lot 为复用非复制（import 正确方向）；instrument_master 的 board→申报单位与本件 min_order_unit 消费=上下游契约（P32 的 star-ETF 200 股缺陷会经此放大为误判资金不足） | :68-73；cross-ref rpt_p32/rpt_p33 | P2(族级真源缺位) | grep 涨跌停承载点对照 |
| E 对抗 | 五问：①静默失败=无（fail-closed 全显式）②假阳性=降级 detail 路径（permission/lot_cash skip）在选股层放行、下单层复检兜底——若 L4-12 复检未接线则降级=裸放（**兜底声明依赖未接线层，接线前该降级是唯一防线**）③断供=DATA_MISSING 显式④重触发幂等⑤时序=N/A（当日快照） | :151-159,178-179 | P3 | 核 L4-12 复检件接线状态 |
| F 新鲜度 | 涨跌停/申报单位/价格笼子为交易所规则工程化（无学术对照面）；预检聚合器=工程常规=**对等已有（声明式）**；规则数值已按 2024-2026 现行 A 股口径核对通过 | 交易所规则对照（本报告 A 轴） | 通过 | — |

## 3 SOTA 对照

- 对等已有：五查聚合+fail-closed+降级链为交易前风控工程常规；涨跌停比例表与现行交易所规则一致。无立卡/驳回。

## 4 缺陷清单

1. P2（族级）：涨跌幅规则三处承载无唯一真源（本件 :68-73 最完整/P33 :469 硬编码 9.5%/P32 DDL 注释）——建议立真源裁定（本件为候选承载）并让 P33/P32 消费之；验证法=三文件对照 grep。
2. P1（接线期）：零生产调用方孤儿；permission/lot_cash 降级放行的下单层 L4-12 复检兜底同为待接线层——接线时须两件同步否则降级=裸放；验证法=§2 C 轴 grep+L4-12 路由核对。
3. P3：一字判定 OHLC 三值齐契约未文档化；默认路径（无意图价）检查强度=仅停牌+一字+数据缺失，未在 docstring 写明分层。

## 5 挂起疑问

- InstrumentSnapshot 由"instrument_master 口径产出"的产源件（盘前同步脚本）仍待接线（P32 同题）——上游产源与本件消费须同批接线。

## 6 完备性自评

六轴全查（F 声明式）。长尾：①意图数量 intended_qty>0 时 need=price×qty 未做整手对齐检查（零股卖出场景不在本件职责，买入零股申报=废单风险留接线核对）②15 测试无 OHLC 部分缺失 case③BSE 30% 比例的实证核对依赖交易所规则文本（本审查按现行规则核对通过）。

## 7 收口裁定（收口方填）
