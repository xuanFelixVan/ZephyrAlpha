---
oid: C02
title: 多策略资金分配器（multi_strategy_capital_allocator MOD-PA-003）
status: 已审
reviewer: GLM-5.3-Flash/st-deeprev-20260918
baseline: 2fa92002c3
date: 2026-09-18
ttl: task_bound
---

# 深度审查报告：C02 MultiStrategyCapitalAllocator（GLM-5.3-Flash / 基线 2fa92002c3）

## 1 对象快照

- 入口：`src/zephyr/pf_alloc/core/multi_strategy_capital_allocator.py:156`（allocate:187）。
- 功能：容量截断+归一化（Σ=1.0）+MaxDD 全线缩减（factor 另交）+冷启动缩放+再平衡频率控制。
- 排除项：无（307 行全读）。
- 测试覆盖：tests/pf_alloc/test_multi_strategy_capital_allocator.py 18 passed（1.00s），无 NaN 用例。
- 生产接线：**零生产调用方**——全仓 grep 仅 `src/zephyr/signal_ashare/strategy_signal/signal_weight_adjuster.py:25` 的 docstring 查重分工提及。头注 [MATURITY] production、[CONSUMERS] MOD-PA-006/D-PF-CORE/D-POSITION 均无 import 证据（batched_position_builder 不 import 本件）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | **NaN signal_weight 全链穿透**：`NaN <= 0` 为 False 过校验；`min(NaN, cap)` 返 NaN；Σ=NaN；`NaN<=0` False 过零检查；权重全 NaN 输出 | multi_strategy_capital_allocator.py:296-299,234,238-240,257 | **P1** | 实测复现：`allocate([StrategyAllocationRequest('A',float('nan'),capacity=0.5),StrategyAllocationRequest('B',0.4)])` → weights={'A':nan,'B':nan}，零异常 |
| A | **NaN max_drawdown 静默跳闸**：`NaN > 0.15` False，`NaN < 0` False 过校验 → max_dd_triggered=False、factor=1.0——回撤闸 fail-open | :304-305,244 | **P1** | 实测：max_drawdown=float('nan') → triggered=False, factor=1.0 |
| A | NaN capacity 被正确拦截（链式比较 NaN 失败→raise），同函数内防御不一致 | :300-302 | P3（反差记录） | 实测已复现 raise |
| A | 数学四问：归一化/容量截断公式正确；冷启动 cap 语义=min(reduction, 0.50) 只约束缩放系数上限，MaxDD+冷启动叠加=0.15 位置远低于 cap（叠加语义偏激进但自洽）；空 requests/单策略/除零（total_raw<=0 raise）均有守 | :238-252 | 已查无 | 阅读+18 测试 |
| A.3 | 测试审查：18 用例覆盖正常/边界/频率控制，但零 NaN、零 Inf 用例——正是漏网处 | tests 文件全文 | P2（缺口） | grep nan 于测试文件=0 命中 |
| B | 输入追源：requests/MaxDD/cold_start 全由调用方注入，而调用方不存在——上游契约悬空 | 全仓 grep | P1（随孤儿） | grep 法见 §1 |
| C | 下游：AllocationResult.reduction_factor 语义="由调用方应用到总资金"（:258-259 注释）——**总仓位缩减双承载**，调用方忘乘则 MaxDD 减仓完全失效；当前无调用方故无实际危害，复活即踩雷 | :257-259,277 | P2 | 代码阅读（注释自认） |
| C | 频率拒绝返回空 allocations+total_weight=0.0（:220-228），调用方若把空当"清零"即全策略断粮——契约靠注释维持 | :218-228 | P2 | 代码阅读 |
| D | 兄弟对查（预算带双承载，特殊问句）：MOD-PA-003（Σ=1+外置 factor）vs MOD-PA-007 RegimeMetaAllocator（effective_budgets 内含 shrinkage，Σeff≤gs）——同一"资金分配"职责两套互斥口径并存；生产真源=PA-007（C01 装配使用），本件=旁置第二实现 | 本件 :257-259 vs regime_meta_allocator.py:326-328 | P1（合并建议） | 两文件对读 + C01 :1023-1029 证明生产用 PA-007 |
| E | 静默失败：NaN 两洞即静默失败点；频率拒绝也是静默（无告警钩子） | 同上 | 并入上 | 同上 |
| E | 重复触发：allocate 每次调用 _rebalance_count+1，同日第二次调用直接拒绝并返回空——若调用方在拒绝分支误用返回值（weights={}）会当"无策略"处理 | :229,218-228 | P3 | 单测模拟两次调用 |
| F | （见 §3） | | | |

## 3 SOTA 对照

- MaxDD 全线缩减 / 分数仓位控制：对等已有（家族）——回撤控制与 fractional Kelly（25-50% 共识）同族，业界以回撤触发减仓为常见风控形态。来源：[Wikipedia: Kelly criterion](https://en.wikipedia.org/wiki/Kelly_criterion)（2025 访问）、[PapersWithBacktest: Kelly Criterion for Position Sizing](https://paperswithbacktest.com/course/kelly-criterion-position-sizing)。
- 本件特有形态（factor 外置+Σ恒 1）无直接业界对照——该形态本身即缺陷面（见轴 C）。
- 深度学术对照（regime-switching + shrinkage 组合）检索受 429 限流**受阻**，如实记。

## 4 缺陷清单（按严重级）

1. **[P1] 孤儿死码 + 头注虚标**（checklist#8，同族案例 d9c5f4bb12）：零生产调用方，[MATURITY] production 与 [CONSUMERS] MOD-PA-006/D-PF-CORE/D-POSITION 无一真实。影响：维护税+复活即踩 NaN 洞。建议修法：登记退役/合并入 MOD-PA-007（规范预算净零：本件退役可对冲新规则），或改 MATURITY=experimental+修正 CONSUMERS。
   验证法：`grep -rn "MultiStrategyCapitalAllocator" src/ scripts/ --include="*.py" | grep -v test`。
2. **[P1] NaN 两洞（signal_weight 穿透 / max_drawdown 静默跳闸）**。建议修法：_validate 与 allocate 入口 `math.isfinite` 硬校验（capacity 同款）；max_drawdown 非有限→raise InvalidAllocationInputError。验证法：本报告 §2 A 行两条 python 单行复现，修复后应 raise。
3. **[P2] factor 外置双承载**：建议合并入 PA-007 口径或在本件内直接产出缩放后权重。验证法：评审 diff。
4. **[P2] 测试 NaN 盲区**：补两条 property 用例（NaN/Inf 输入必 raise）。
5. **[P3]**：NaN capacity 拦截与 signal_weight 放行的同函数防御不一致；频率拒绝返回值语义未类型化（建议返回 dataclass 而非空列表）。

## 5 挂起疑问

1. 本件是否为 MOD-PA-007 的前身/对照基准（git log 3db6f33c63 同批 9 模块基建）——退役裁定需 Owner 确认无规划中消费方。
2. signal_weight_adjuster docstring 的"查重分工"声明是否已随本件孤儿化而过期。

## 6 完备性自评

六轴全查。长尾：blueprint.md（docs/03_modules/_domain_portfolio_alloc/...）未取——退役裁定前建议补读；深度学术 SOTA 受限流受阻。
