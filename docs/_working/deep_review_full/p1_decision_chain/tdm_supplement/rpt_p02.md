---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——计划生成（已审）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：计划生成（P02）— GLM-5.3-Flash / st-deeprev-20260918

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（目标文件基线后零漂移）
- 审查者: GLM-5.3-Flash/st-deeprev-20260918
- 入口锚点: `src/zephyr/plan_engine/daily_trade_plan.py`
- TDM 节点: TDM-E-L0-01
- 生产调用方: **生产代码零调用方**（孤儿，见 C-1）
- 测试文件: tests/plan_engine/test_daily_trade_plan.py（实跑通过）

## 1 对象快照
MOD-PLAN-011 全文件（411 行）：结构化今日交易计划纯函数生成器（拟买上限截断+整手折算 / 拟卖止盈+破下沿减仓条件规则）。排除项：SHIFT_STANCE 真源（scenario_planner.py:96，本件只读消费）。测试实跑通过（合批 100 passed）。

## 2 六轴审查日志表
| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | 上限数学 `min(max_add×scale, firm 8%)` 正确；`_floor_lot` 浮点下取整 epsilon 边界：数学值恰 300 股可浮点表出 299.99999999999994→折 200 股（保守方向少买一手） | :112-116,283；实测 `_floor_lot(299.99999999999994,100)=200` | P3 | `python -c "from zephyr.plan_engine.daily_trade_plan import _floor_lot; print(_floor_lot(299.99999999999994,100))"` |
| A 深度 | resolve_stance 银行家舍入不对称：round(0.25×2)/2=0.0 而 round(0.75×2)/2=1.0，final_shift 离格（非 0.5 倍数）时档位漂移；且 stance 取 entry.stance 而 scale 取 SHIFT_STANCE[snapped][1]（两源拼接，离格时可能错配） | :257-265 | P3 | 造 final_shift=0.25 的 ScenarioPlan 看 (stance,scale) |
| A A股 | 整手 100 正确；卖出条件规则不涉 T+1 违规；买入价=box_lower 无涨跌停/停牌复核（计划文本，执行层责任，notes 未提示停牌候选） | :77-80,280-303 | P3 | 造 boundary.box_lower 超涨跌停价的候选看输出 |
| B 上游 | boundary 无 box_lower<box_upper 复核：P04 若产出反转箱体（amplitude<0，见 rpt_p04 A-2），本件按 buy=box_lower、必出=box_upper 生成荒谬计划不报错——上游坏→静默坏计划 | :279-283,324-343 | P2 | 造 amplitude=-0.05 的 TomorrowBoundary 喂 generate_daily_trade_plan |
| C 下游 | **孤儿**：`grep -rln "generate_daily_trade_plan" src/ scripts/` 仅本文件；GAP-F-09 声称前端消费，但 live.html:293-297 "今日交易计划"卡为硬编码 mock 数据（600519/601318 静态行），不消费本件输出 | grep 实证；live.html:291-297 | **P2** | grep + 查看 live.html 卡片数据源 |
| D 旁系 | firm 8% 硬顶双承载（本件 ：279 与 FirmRiskAggregator 30号§2.2）——层级有序（先截断后封顶）非漂移；SHIFT_STANCE 同源复用一致（scenario_planner.py:96 键型 float 与 snapped 匹配） | :277-279 | P3 | 核对 SHIFT_STANCE 键集合={-1.0,-0.5,0.0,0.5,1.0} |
| E 对抗 | 纯函数幂等；不足一手/零股跳过有 notes 留痕（好）；无静默吞异常路径 | :281-285,316-317,345-346 | 已查无 | 重复调用比对输出 |
| F 新鲜度 | 受阻/不适用：规则模板 DSL 无外部算法对照对象（非统计/学习算法） | — | — | — |

## 3 SOTA 对照
不适用（参数化中文模板生成器，无统计/学习算法主张）。

## 4 缺陷清单
1. **P2 孤儿+假消费**：生产零调用，前端"今日交易计划"卡为 mock 静态数据，GAP-F-09 消费链未兑现。建议：接线 api_server 或在 GAP 总账标注未兑现。验证法：grep + live.html:293。
2. P2 上游反转箱体静默传导（见轴 B，与 rpt_p04 A-2 同源，修 P04 或本件加 box 序断言均可）。
3. P3 浮点下取整 epsilon（保守方向，低危）。
4. P3 resolve_stance 离格漂移/两源拼接。

## 5 挂起疑问
- position_scale 由调用方注入且文档警告"勿重复施加"（:365-367）——无机制防线，接线时需评审调用方。

## 6 完备性自评
六轴全查。长尾：SHIFT_STANCE 全表与 §9.5/§9.6 设计文档逐行比对未做（只核对键型）；前端卡 mock 数据的来源无更多线索。
