---
ttl: task_bound
title: 深度审查作业簿——TWAP拆单器
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：TWAP拆单器（X06）

- 状态: **已审**
- 级别: P0｜类型: 算法
- 基线 commit: 2fa92002c3
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/ex_core/order_splitter.py:213`
- 生产调用方: **仅 ex_sor/core/sor_agent.py + 测试**（头注声称的 MOD-EX-062 execution_strategy_selector 经查**不 import 本模块**——幽灵消费方）；ex_sor 域本身零生产外接（见 X04 P2-5）→ 实际生产链为零
- 测试文件: tests/ex_core/test_order_splitter.py（19 passed，实测）
- 备注: 余数修正

## 1 对象快照

- **范围**：order_splitter.py 全文 297 行（SplitRequest 校验、最大余数法分配、_enforce_min_unit 让渡、TWAP/VWAP 两档、守恒断言）。
- **排除项**：board_lot 规则表内部（真源消费已核）、execution_strategy_selector 的算法选择逻辑（经查无 import 关系）、调度器（时间维度不在本模块）。
- **测试覆盖概况**：19 passed（1.86s）。覆盖守恒/整手对齐/零股尾量/让渡失败拒单/VWAP 缺曲线 Fail-Closed。**未覆盖**：SELL 悬殊权重下 0 量末片（恰为 P2-1，已实证复现）。
- **材料包缺项声明**：运行时证据包无；数据画像不适用；checklist 15 条已过——命中 #9 幽灵引用邻近（头注消费方不实）、#8 孤儿族。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | 最大余数法数学正确：units_total 按权重配额、floor 基量、余量按小数部分降序分发（并列取小序号，确定性）；rank % len 兜底；Σ==units_total 恒成立 | order_splitter.py:161-179 | 通过 | 随机权重/总量对拍 |
| A | **SELL 0 量末片边界**：悬殊权重+小总量时末片可为 0（已实证：SELL 200 股、2 片、profile=(0.9,0.1) → [200, 0]）——0 量 ChildSlice 进入 SplitPlan，下游若不滤则生成 0 量废单；BUY 侧因全片 enforce≥min_unit 不受影响 | order_splitter.py:273-282（无零量过滤）+ 实证复现 | P2 | 见验证命令：VWAP profile=(0.9,0.1) SELL 200 股 2 片 |
| A | BUY 总量前置校验正确：≥min_unit 且 (total-min_unit) 按 increment 对齐；科创板 min=200/inc=1 口径经 board_lot 真源（与 X04 硬编码 LOT_SIZE=100 形成对照——本模块口径正确） | order_splitter.py:247-256,227-229 | 通过 | 造 150/250 股用例（19 tests 含） |
| A | 让渡算法有界且保守：donor 让渡后仍须 ≥min_unit；卖出末片可作让渡方但不可低于 min_unit（合法零股情形未放宽——保守方向，可能拒掉合法拆分，可接受） | order_splitter.py:182-210 | P3(保守) | 读审 |
| A | 零委托量/越界片数 Fail-Closed✓（1..48）；VWAP 缺曲线/长度错/负权重/全零权重全 Fail-Closed 不静默降级✓ | order_splitter.py:120-130,133-154 | 通过 | test 复跑 |
| B | 上游契约：total_quantity 须"已是合法申报数量"靠调用方先过 board_lot.round_buy_qty（BUY 校验兜底✓，SELL 校验较松——odd_tail 提取对任意正数成立，无合法性断言，非对齐 SELL 总量被静默接受后尾量并入末片） | order_splitter.py:84-85,236-240 | P3 | SELL 150 股断言不报错尾片 50 |
| C | 消费方实证：全仓 import 仅 sor_agent（ex_sor 域内）+ 测试——**头注 [CONSUMERS] MOD-EX-062 为幽灵引用**（execution_strategy_selector.py 无 splitter/split_order 字样，grep 实证） | order_splitter.py:5 + grep | P2 | `grep -n "splitter" src/zephyr/ex_core/execution_strategy_selector.py`（零命中） |
| D | **旁系双实现口径对照（与 X04）**：order_splitter（board_lot 板块真源/min_unit+increment/48 片上界/无价格策略）vs algo_trading_engine（LOT_SIZE=100 硬编码/ADV+参与率约束/带价格策略）——同职责（TWAP/VWAP 拆单）两套实现，整手口径一处对一处错；接线时必须二选一或统一到底板真源 | order_splitter.py:227-229 vs algo_trading_engine.py:177,240 | P2 | 两模块同输入对比切片量 |
| E | 静默失败：守恒违反防御性断言✓；0 量片静默产出（P2-1 即静默缺陷本体） | order_splitter.py:265-270,273-282 | P2(同上) | 同上复现 |
| E | 假阳性：无——Fail-Closed 面完整（量/片数/权重/合法性全校验） | order_splitter.py:120-154 | 通过 | test 复跑 |
| E | 重复触发：纯函数无副作用✓ 同输入同输出（头注承诺+实测复现） | order_splitter.py:214 | 通过 | 同请求两次调用 diff |
| E | 时序：sequence 1-based 顺序语义✓；无时间逻辑（调度归下游）——无时序死角 | order_splitter.py:100-105 | 通过 | 读审 |
| F | 见 §3 | — | — | — |

## 3 SOTA 对照

1. **TWAP/VWAP 拆单**：对等已有。等量时间切片（TWAP）与历史量能剖面加权（VAP）为业界执行算法标准形态（Optimal Execution Algorithms: TWAP, VWAP & Market Impact，mbrenndoerfer.com，https://mbrenndoerfer.com/writing/execution-algorithms-optimal-trading-strategies ，2024-2025；AlgoTrader 执行算法文档，https://algotrader.ch/resources/execution-algorithms/ ；VWAP 调度最优性理论=arXiv 1901.02327，2019，https://arxiv.org/html/1901.02327v2 ——与 X04 检索同族复用）。本模块为静态剖面 Phase 1，形态对等。
2. **整手约束的整数划分**：对等已有（工程惯例）。最大余数法分配整数手数+末片承接尾量是处理不可分粒度的标准确定性方法（apportionment 方法论；无单一权威工程文献 URL，本条按"业界通行工程做法"对等定性，检索预算记部分复用 X04）。

## 4 缺陷清单

**P2-1 SELL 悬殊权重下 0 量末片静默进入 SplitPlan**
- 现状：末片（零股尾量承接片）无 ≥最小量过滤；odd_tail=0 且权重分配给末片 0 单位时产出 qty=0 的 ChildSlice。
- 证据：order_splitter.py:273-282（无零量过滤）；实证：SELL 600000.SH 200 股 2 片 VWAP profile=(0.9,0.1) → slices=[200,0]。
- 影响：下游调度器若不滤则生成 0 量委托（柜台 error 52 数量不合法，消耗申报计数与撤单率预算）；SplitPlan 契约未声明可能含 0 量片。爆炸半径=接线下游全部 VWAP 卖单。
- 建议修法：生成切片时过滤 qty=0 片（守恒不受影响），或 _enforce_min_unit 把 enforce_upto 扩展到末片的非零下限。
- 验证法：python -c 复现命令（见 §2 A 轴）；修复后同输入断言单切片或非零末片。

**P2-2 头注幽灵消费方+孤儿链（checklist#9 邻近）**
- 现状：[CONSUMERS] 声称 MOD-EX-062（execution_strategy_selector）消费，实际该文件零 import；唯一 import 方为 ex_sor/sor_agent（域内），而 ex_sor 域零生产外接。
- 证据：order_splitter.py:5 + grep 实证（execution_strategy_selector.py 无 splitter 字样）。
- 影响：模块文档口径失真；与 X02/X03/X04 构成执行域孤儿族第 4 例——拆单能力存在但生产链断裂。爆炸半径=架构口径。
- 建议修法：头注改真源（sor_agent）或在 selector 接线；与执行域孤儿族同批裁定。
- 验证法：grep 复核两文件。

**P3**：①让渡保守（末片合法零股未放宽，可能拒掉合法拆分方向）；②SELL 总量合法性无前置断言（非对齐总量静默尾量并入）；③48 片上界与 3 秒 Tick 口径绑定为注释级约定（:62）。

## 5 挂起疑问

1. sor_agent 消费链的实际成熟度（ex_sor 域内自洽但域外零接线）——与 X04 P2-5 同批裁定拆单能力归属（order_splitter vs algo_trading_engine 二选一）。
2. 下游调度器（若接线）是否已滤 0 量片——决定 P2-1 实际爆炸半径。

## 6 完备性自评

- 六轴全查：A（最大余数法/让渡/BUY 校验/零量边界四问全过+1 项实证发现）、B（总量契约两侧对称性）、C（消费方 grep 实证=幽灵引用）、D（与 X04 双实现口径对照）、E（五问：静默=0 量片、假阳性=无、断了没人知道=不适用、重复触发=纯函数、时序=无死角）、F（2 条对照，检索与 X04 同族复用如实记）。
- 长尾：①execution_strategy_selector 选算法逻辑本身未审（无 import 关系故排除）；②sor_agent 内部未审。

## 7 收口裁定（收口方填）
- 三态逐条：
- 修复 commit:
- 复检结论:
