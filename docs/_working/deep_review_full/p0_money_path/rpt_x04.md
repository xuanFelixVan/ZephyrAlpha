---
ttl: task_bound
title: 深度审查作业簿——SOR算法执行引擎
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：SOR算法执行引擎（X04）

- 状态: **已审**
- 级别: P0｜类型: 管线
- 基线 commit: 2fa92002c3
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/ex_sor/core/algo_trading_engine.py:749`
- 生产调用方: 仅 `ex_core/execution_engine.py:65,346`（而该引擎本身零生产接线，见 X03 P1-2）——**实际生产调用链为零**
- 测试文件: tests/ex_sor/test_algo_trading_engine.py（71 passed，实测）
- 备注: TWAP/VWAP/冰山/POV/IS/ALT 六算法

## 1 对象快照

- **范围**：algo_trading_engine.py 全文 1011 行（AlgoType 注册表、6 策略切片生成、_distribute_evenly/_distribute_by_weights 守恒工具、generate_plan 校验链、AlgoParamOptimizer）。
- **排除项**：XS-04 execution_scheduler（时间调度，仅确认 import 关系）、market_context_provider（X03 已核接口）、RL 执行模块族。
- **测试覆盖概况**：71 passed（3.99s）。覆盖六算法切片/守恒/ADV 上限/参数校验/注册表。**未覆盖**：参与率红线强制、科创板最小申报单位、max_slice_count 耗尽后末片补余的语义。
- **材料包缺项声明**：运行时证据包无；数据画像不适用（ADV/volume_profile 为运行时输入）；checklist 15 条已过——命中 #7 A股口径（科创板整手）、#8 孤儿族（依赖 X03）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | 守恒工具数学验证：_distribute_evenly base 向下取整+余数补末片，Σ==total 成立；_distribute_by_weights 归一化+deficit 补最大权重片，Σ==total 成立（w_sum=0 回退均匀） | algo_trading_engine.py:394-426 | 通过 | 随机总量×n 片对拍求和 |
| A | **余数补末片可破坏 lot 对齐**：total 非 lot 对齐时（如 1050 股、lot=100、n=10）末片=150 股——主板买入非整手属废单；仅当上游 board_lot 已对齐时安全（隐含假设无断言） | algo_trading_engine.py:401-408 | P2 | 造 total=1050 调 _distribute_evenly 看末片 150 |
| A | **科创板最小申报单位口径错**：LOT_SIZE 硬编码 100（:177），AlgoParams.min_slice_quantity 默认=LOT_SIZE、AlgoParamOptimizer 用 LOT_SIZE——科创板买入最小 200 股，100 股切片全为废单；board_lot 真源（X01 消费的 ex_core.board_lot 板块差异化）未接入本模块 | algo_trading_engine.py:177,240,968-998 | P2 | 造 688xxx 订单走 optimizer→plan，切片含 100 股 |
| A | **参与率 §10.1 红线只估算不强制**：generate_plan 第 5 步算 est_participation "供监控"但不做 ≤5% Hard Block；POV/ICEBERG 末片补余后 max_slice 可远超窗口量×5%——INVARIANTS 声称"参与率≤5% 监管硬约束"与实现不符（文档 vs 代码漂移+监管约束失效） | algo_trading_engine.py:898-909 vs :8(头注) | P1 | 造 order=14%ADV、POV 低参与率参数，断言 est_participation>5% 仍出 plan |
| A | **ICEBERG 末片补余毁隐藏意图**：max_slice_count 耗尽后余量全补末片（:557-565）——10 万股单 display 1k×max 10 片 → 末片 91000 股，冰山变明单（暴露意图+参与率爆表） | algo_trading_engine.py:538-565 | P2 | 造 display=1k/max=10/总量 100k 断言末片 91k |
| A | IS 策略命名与实现差距：称 Almgren-Chriss 轨迹，实为 w_i∝exp(-λ t_i) 指数衰减启发式（无影响力模型/风险厌恶求解）——λ=0 退化为 TWAP✓、前置加载方向✓ | algo_trading_engine.py:645-684 | P3 | 读审+λ=0 对拍 TWAP |
| A | POV 窗口量估算数学：expected_window_vol=ADV×horizon/240/n——240 分钟交易日假设✓；未考虑午休（4 小时连续）、未按 volume_profile 加权（与 VWAP 口径不一致，同为时段法两处算法） | algo_trading_engine.py:590-592 | P3 | 读审 |
| A | generate_plan 校验链完备：参数重校验防绕过✓、ADV≤15% Hard Block✓、空切片拒✓、守恒双查（plan __post_init__ + generate_plan）✓ | algo_trading_engine.py:858-919,325-340 | 通过 | test 71 passed 含守恒 |
| B | 上游 MarketContext 契约：last_price/adv>0、profile 和≈1.0 强校验✓；bid/ask 可 None→_mid_price 退化 last_price（中间价=最新价，PASSIVE 挂单价格语义弱化）——上游错价直接进 reference_price，无价格笼子/涨跌停钳制 | algo_trading_engine.py:200-218,730-741 | P2 | 造 ask=涨停价×2 的 ctx 看 reference_price 出笼 |
| C | 消费方：唯一外部消费方=execution_engine（自身孤儿，X03 P1-2）；XS-04 scheduler 仅域内 import；**ex_sor 切片方案无任何生产路径到达交易所** | grep 实证 | 记录 | `grep -rn "from zephyr.ex_sor" src/ scripts/ --include=*.py` 排除域内 |
| D | 旁系：order_splitter.py（X06 TWAP 拆单器）与本模块 TWAP 功能同职责双实现——ex_core/ex_sor 两域各一套拆单（口径是否一致待 X06 对比）；VWAP/POV 时段法 vs POV 窗口法域内口径也不一致（见 A 轴） | ex_sor/core/algo_trading_engine.py vs ex_core/order_splitter.py | P2 | X06 报告交叉对比 |
| E | 静默失败：策略生成 0 切片→AlgoError✓（:881）；但 _distribute_by_weights 全零权重回退均匀是静默改语义（:417-418）仅可接受；守恒失败抛错不静默✓ | algo_trading_engine.py:417-418,881-896 | 通过 | 读审 |
| E | 假阳性过关：ADV 上限检查 `ctx.adv > 0` else fraction=1→必拒✓；但 adv 来自上游快照，**陈旧 ADV（停牌前）会让 15% 上限失真**——无 adv 时效校验（与 X01 价格陈旧同型） | algo_trading_engine.py:864-866 | P3 | 造 30 天前 adv 复现 |
| E | 重复触发：generate_plan 纯函数（无副作用）✓ 重放安全；重复调用仅重复计算，下单副作用在调用方（ExecutionEngine/X03） | algo_trading_engine.py:834-919 | 通过 | 读审 |
| E | 时序：created_at 由调用方注入✓；切片顺序=逻辑顺序、时间调度归 XS-04（本对象无时序死角） | algo_trading_engine.py:310-314 | 通过 | 读审 |
| F | 见 §3 | — | — | — |

## 3 SOTA 对照

1. **VWAP/POV 切片调度**：对等已有（方法论方向）。VWAP 按日内成交量分布调度、POV 按预期窗口量×参与率限速，与业界标准做法一致（Optimal VWAP execution under transient price impact，arXiv，2019，https://arxiv.org/html/1901.02327v2 ；VWAP Execution as an Optimal Strategy，SSRN/Gabrielsen 等，https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2487241 ；Optimal Execution Algorithms 综述，mbrenndoerfer.com，https://mbrenndoerfer.com/writing/execution-algorithms-optimal-trading-strategies ）。本对象为 Phase 1 静态剖面实现，方向对等、粒度较粗（4 时段/无动态更新）。
2. **Almgren-Chriss 框架**：对等已有（概念）/立卡候选（实现）。AC(2000) 影响力-时机风险权衡是 IS 算法真源；本对象仅指数衰减启发式未解 AC 最优轨迹（QuestDB AC 词条，https://questdb.com/glossary/optimal-execution-strategies-almgren-chriss-model/ ）。立卡：接入真 AC 求解或改名为"指数衰减启发式"以正名。
3. **参与率监管约束**：本仓 §10.1 自称对应证监会程序化交易规定（参与率上限）——本次未做中文监管原文检索对照（检索预算用于 1/2 条目），**监管口径对照记部分受阻**；建议收口方核《证券市场程序化交易管理规定》原文参与率条款与本仓 5% 阈值的一致性。

## 4 缺陷清单

**P1-1 参与率 §10.1 红线只估算不强制（INVARIANTS 与实现不符）**
- 现状：est_participation 仅记录；POV/ICEBERG/均匀分配的末片补余不受 5% 检查；无 Hard Block。
- 证据：algo_trading_engine.py:898-909（仅估算）vs :8（INVARIANTS 声称硬约束）；末片补余 :557-565,617-626。
- 影响：接线后可能生成单片参与率超监管红线的执行计划（程序化交易违规风险）。爆炸半径=经 ex_sor 的全部大单。
- 建议修法：generate_plan 末步加 `est_participation <= MAX_PARTICIPATION_RATE` 校验，超限拒或强制再拆。
- 验证法：单测造 order=14%ADV+POV 小参与率参数，断言当前仍出 plan（复现），修复后断言拒。

**P2-1 科创板最小申报单位口径错（LOT_SIZE=100 硬编码）**（:177,240,968-998；688 标的 100 股切片全废单；修法：min_slice_quantity 接入 board_lot 板块真源；验证法：688 订单走 optimizer 看 100 股切片）。
**P2-2 ICEBERG 末片补余毁隐藏意图**（:557-565；修法：超片数时拒单要求调大 max_slice_count 或分批 plan；验证法：display=1k/max=10/100k 总量复现末片 91k）。
**P2-3 余数补末片可出非整手切片**（:401-408；上游未对齐时主板买入废单；修法：末片 lot 对齐+余量二次分配或拒单；验证法：total=1050 复现末片 150）。
**P2-4 reference_price 无价格笼子/涨跌停钳制**（:730-741 + ctx 上游；异常 bid/ask 直接成参考价，依赖下游闸；修法：出参考价前过 X05 price_cage；验证法：构造超笼 ask 复现）。
**P2-5 ex_sor 域整体未接入生产（依赖 X03 P1-2 联动裁定）**（grep 实证唯一外部消费方为孤儿 ExecutionEngine；与 X02/X03 构成执行域孤儿族；修法：同批裁定接线或降级登记；验证法：grep 复核）。
**P3**：①IS 命名 AC 但实为指数衰减启发式（:645-684）；②POV 240 分钟连续假设忽略午休+与 VWAP 剖面口径不一致（:590-592）；③adv 无时效校验（:864-866）；④optimize 的 rate=min(5%, frac×2) 在 frac 极小时回退 5% 反向放大（:981-983，与 X03 P3-①同型）。

## 5 挂起疑问

1. §10.1 参与率 5% 与证监会程序化交易新规条款的原文对照未完成（检索预算所限）——收口方补核监管原文。
2. XS-04 execution_scheduler 是否有时间调度实现（本审仅确认 import 关系）——若后续接线 ex_sor 需先审 XS-04。
3. ex_core.board_lot 板块差异化真源与 LOT_SIZE 常量的合并方向（P2-1 修法依赖）。

## 6 完备性自评

- 六轴全查：A（守恒/lot 对齐/科创板/参与率/AC 命名/POV 假设六问）、B（MarketContext 契约+陈旧 adv）、C（消费方=孤儿链实证）、D（与 order_splitter 双实现登记+域内口径）、E（五问：静默=通过、假阳性=adv 时效、断了没人知道=不适用（无运行）、重复触发=纯函数通过、时序=通过）、F（2 条带 URL 对照+1 条部分受阻）。
- 长尾：①XS-04 时间调度内部未审；②RL 执行模块族（rl_exec_*）未审；③volume_profile 真实分布画像未取（无生产数据）。

## 7 收口裁定（收口方填）
- 三态逐条：
- 修复 commit:
- 复检结论:
