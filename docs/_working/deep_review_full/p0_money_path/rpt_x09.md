---
ttl: task_bound
title: 深度审查作业簿——打板执行+瞬时熔断
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：打板执行+瞬时熔断（X09）

- 状态: **已审**
- 级别: P0｜类型: 闸门
- 基线 commit: 2fa92002c3
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/ex_core/daban_execution.py:59 + daban_instant_circuit_breaker.py:40`
- 生产调用方: **两模块均零生产接线（文件头诚实声明"首批实盘接线前暂无"）**；ex_core/__init__.py:31-37 仅可发现性导出；daban_exit_decision/daban_monitors 注释级提及未 import
- 测试文件: tests/ex_core/test_daban_execution.py + test_daban_instant_circuit_breaker.py（合计 37 passed，实测）
- 备注: L4执行族15/15已验(裁定快签#28)

## 1 对象快照

- **范围**：daban_execution.py 全文 196 行（三段分笔/SaR 评估/时点决策/动态容量四约束）+ daban_instant_circuit_breaker.py 全文 74 行（封单崩塌/梯队断层/量化席位三触发器）。
- **排除项**：daban_* 家族其余模块（signal/exit/monitors/pit_safety/load_producer，8 测试文件在列但非本对象）；§3.4 13 静态约束链（文档真源）。
- **测试覆盖概况**：37 passed（3.73s）。覆盖三分笔/SaR 削减/时点三分支/四约束 binding/三触发器。**未覆盖**：空订单簿 full 链路、初始封单=0 边界、0 量批次产出。
- **材料包缺项声明**：运行时证据包无；数据画像不适用；checklist 15 条已过——命中 #8 孤儿（双模块，但文件头已诚实声明=非漂移）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | SaR 量纲自洽验证：sar=(q/depth)×(1+conc)×eta（eta=0.001/满深度消耗）——2% 阈值对应订单=5 档深度 20 倍触发削减；容量反演 sar_capacity=tol×depth/((1+conc)×eta) 与 sar 公式互逆✓ | daban_execution.py:79-85,173-178 | 通过 | 正反算对拍（q=sar_capacity 时 sar=tol） |
| A | **封单崩塌触发器边界**：seal_ratio=current/max(initial,1)；initial_seal=0（未封板/盘前）→ ratio=0 <0.7 → **SEAL_COLLAPSE 瞬时全卖**——对"持仓必须已封板"的打板 sleeve 语义下=炸板卖出合理，但模块无"持仓为已封板票"前置校验，被非打板场景复用即误清仓 | daban_instant_circuit_breaker.py:52-53 | P2 | initial=0/current=0 调 check 断言 INSTANT_SELL |
| A | fill_prob 基础项无判别力：base=min(seal_volume/(order_volume×10),1)——封单百万股 vs 买 1 万股 → 恒 1.0（头注自认"概率模型校准属 Phase 3"）；position_decay 0.85^n 启发式、distance_decay κ=0.2 未校准 | daban_execution.py:73-77 | P3(已声明) | 大封单小订单断言 prob=1 |
| A | 三段分笔 int() 截断产生 0 量批次：target=1 → FIRST=0/REFLUSH=0/RESERVE=1；且 SAR_TRIM 为伪批次标记（无 timing 字段）混入 plan 序列——下游 G22 执行层需甄别（未建） | daban_execution.py:96-116 | P3 | target=1 断言 0 量批次存在 |
| A | 时点决策 WAIT 分支不可达（设计内）：_estimate_seal_probability 下限 0.5 → seal_prob<50% 两分支永假——头注 spec 转写登记①逐字保留；**活体后果=决策永不观望，弱板也出 AMBUSH 限价单** | daban_execution.py:36-38,140-159 | P2 | seal_strength=0/volume_surge=0 断言仍 ≥0.5 |
| A | AMBUSH limit_price="涨停价-0.01" 占位字符串（登记②）：消费方必须解析，直传柜台即废单——G22 执行层未建，风险悬置 | daban_execution.py:144,39-40 | P3(已声明) | 读占位标记 |
| A | 动态容量四约束取 min 数学✓：空簿 depth=0→sar_capacity=0（Fail-Closed）、price≤0→nav=0（Fail-Closed）、各容量非负；order_book 契约松散（缺 "volume" 键即 KeyError 裸抛） | daban_execution.py:171-196 | P3 | 缺键调用复现 KeyError |
| B | 上游 live_data/echelon_status/quant_seat_ratio 无类型/域校验：quant_seat_ratio=1.5 → 触发（保守方向可接受）；echelon_status 任意字符串 → 不触发（安全方向）；无"负封单量"防御（current=-5 → ratio 负 <0.7 → 触发全卖——异常数据误触发） | daban_instant_circuit_breaker.py:48-74 | P2 | current_seal=-5 断言误触发 |
| C | 消费方清单：零生产调用（头注声明）；__init__ 导出仅可发现性；爆炸半径=接线后打板 sleeve 全部资金 | ex_core/__init__.py:31-37 | 记录 | grep 复核 |
| D | 旁系族内口径：daban_exit_decision/daban_monitors 注释引用本类但未 import（联动靠装配层）；KillSwitchLite（X01 消费）是账户级，本类 sleeve 级——层级清晰无双实现 | daban_exit_decision.py:84 + daban_monitors.py:21 | 通过 | grep import 关系 |
| E | 静默失败：三触发器纯函数无 try/except 吞没✓；但无日志无审计——INSTANT_SELL 决策产出后是否有痕取决于消费方（未建） | daban_instant_circuit_breaker.py:48-74 | P3 | 读审 |
| E | 假阳性/假阴性：触发器①封单崩塌对"已封板持仓"语义正确；但**无 T+1 约束感知**——当日新买持仓触发熔断卖出会被柜台拒（error 55），熔断信号空转需上层降级处理（模块无此意识） | daban_instant_circuit_breaker.py:53-59 | P3 | 读审（T+1 拒单路径在柜台/OM） |
| E | 重复触发/时序：纯函数无状态✓ 重放安全；无防抖设计——连续 tick 崩塌信号会重复产出 INSTANT_SELL，消费方需幂等（未建，登记接线注意项） | daban_instant_circuit_breaker.py:48 | P3 | 连续调用断言重复产出 |
| F | 见 §3 | — | — | — |

## 3 SOTA 对照

1. **Slippage-at-Risk 理论背书**：对等已有（文献真实存在）+**适配缺口**。SaR 框架真源=arXiv:2603.09164（O. Sepper/SepperLabs，2026-03，https://arxiv.org/abs/2603.09164 ；RePEc 镜像，https://ideas.repec.org/p/arx/papers/2603.09164.html ）——**原文语境是永续合约交易所的订单簿流动性**，本模块迁移到 A 股涨停封单场景（封单≠连续簿深度、涨停板流动性动力学不同），线性响应 eta 模型是启发式简化，适配有效性未经回测校准（模块自认 Phase 3）。
2. **封单崩塌/级联清仓时点**：立卡候选。liquidation cascade 文献背书（头注引 arXiv:2608.03616，本次检索预算未逐条核验其余 4 篇 arXiv 引用——SaR 为代表性核验，其余记部分受阻）；"三触发器先到先熔断"的 sleeve 级瞬时风控设计与账户级 Kill Switch 分层是合理架构，无业界直接对照物（打板为 A 股特有策略），建议接线前以历史封单数据回测触发器阈值（30%/70%）。

## 4 缺陷清单

**P2-1 瞬时熔断触发器无持仓语义前置校验（initial_seal=0/负值误触发）**
- 现状：seal_ratio=current/max(initial,1)，initial=0 或 current 为异常负值时 ratio≤0 恒 <0.7 → INSTANT_SELL 全卖；模块不校验"持仓为已封板票"。
- 证据：daban_instant_circuit_breaker.py:52-53。
- 影响：接线后被非封板持仓场景复用（或数据异常 tick）→ 误触发瞬时清仓；A股 T+1 下当日票卖出被拒还会产生拒单噪音。爆炸半径=打板 sleeve 全部持仓。
- 建议修法：check 入口加前置断言（initial_seal>0 才参与崩塌判定，否则返回 MONITOR+数据异常告警）。
- 验证法：initial_seal=0/current_seal=0 调 check 断言当前 INSTANT_SELL（复现）。

**P2-2 时点决策永不 WAIT（登记在案的设计取舍需活体化决策）**
- 现状：seal_prob 下限 0.5 使两条 WAIT 分支不可达——spec 忠实转写（登记①）但活体行为=弱板也出 AMBUSH 限价单。
- 证据：daban_execution.py:36-38（登记）、140-159（实现）。
- 影响：接线后无"观望"能力，弱封板标的持续挂埋伏单（成交即接弱板刀）。爆炸半径=打板 sleeve 时点决策。
- 建议修法：Phase 3 校准时重标概率下限（或 near_limit=False 时下探 0.3），保留 spec 分支结构。
- 验证法：seal_strength=0/volume_surge=0/near_limit=False 断言 prob=0.5→AMBUSH。

**P2-3 双模块孤儿（文件头已诚实声明——非漂移，接线前置件清单需含本报告 P2-1/P2-2）**（daban_execution.py:6 + daban_instant_circuit_breaker.py:6；验证法：grep）。
**P3**：①fill_prob/参数族未校准（:62-68 已声明 Phase 3）；②SAR_TRIM 伪批次+0 量批次混入 plan（:96-116）；③order_book/live_data 契约松散缺键裸抛（:83-84,175-176）；④AMBUSH 占位限价依赖未建的 G22 解析（:144）；⑤瞬时熔断无 T+1/防抖/审计留痕设计（消费方责任未登记成文）。

## 5 挂起疑问

1. 其余 4 篇 arXiv 引用（2607.28323/2608.02002/2608.00988/2608.03616）未逐条核验（检索预算所限，SaR 代表性核验通过）——收口方或后续轮次补核。
2. "L4执行族15/15已验(裁定快签#28)"的裁定真源未回查 ruling_registry（本报告未引用其内容，不影响上述发现）。
3. G22 执行层（消费本族的装配层）落地时间表——决定 P2-1/P2-2 修复排期。

## 6 完备性自评

- 六轴全查：A（SaR 量纲/触发器边界/概率模型/容量四约束/占位符五问全过）、B（输入契约松散面）、C（零消费方诚实声明核证）、D（族内层级清晰无双实现）、E（五问：静默=无吞没、假阳性=P2-1、断了没人知道=不适用（无运行）、重复触发=纯函数通过+防抖登记、时序=通过）、F（SaR 核验通过+适配缺口立卡+其余引用部分受阻如实记）。
- 长尾：①daban_* 家族其余 6 模块未审（signal/exit/monitors/pit_safety/load_producer/named_functions）；②arXiv 引用 4 篇未核；③打板策略文档 24_daban_strategy_detail §3.13/3.14 spec 与代码逐条对未做（头注登记①②已覆盖已知偏差点）。

## 7 收口裁定（收口方填）
- 三态逐条：
- 修复 commit:
- 复检结论:
