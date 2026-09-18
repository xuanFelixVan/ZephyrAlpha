---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——策略相关性闸（W04）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：策略相关性闸 StrategyCorrelationGate（GLM-5.3-Flash / 基线 2fa92002c3）

- 状态: **已审**
- 级别: P1｜类型: 闸门
- 基线 commit: 2fa92002c3（实测 HEAD=b93d923b95 为其后代）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/pf_alloc/core/strategy_correlation_gate.py:220`
- 生产调用方: **名义挂接、零实际调用**——pf_core/core/performance_attribution_engine.py:57,264,275 仅注入赋值，全文件无 `_correlation_gate` 调用点
- 测试文件: tests/pf_alloc/test_strategy_correlation_gate.py（22 测试，随批实跑通过）
- 备注: 头注宣称消费方 MOD-PA-003/MOD-PA-005/D-PF-CORE 均无实际 import 调用

## 1 对象快照

- 范围：`strategy_correlation_gate.py` 全 449 行：pair 指标校验 → 四维阈值判定（相关性/因子重叠/股票池×行业/尾部相关）→ 最严重裁决聚合 → PA-E03 事件广播。纯判定无副作用。
- 排除项：相关性矩阵/因子重叠的**计算**（line 33 明示归数据层）——本件只消费现成指标。
- 测试覆盖概况：22 测试全绿；覆盖四维规则/持久化降级/监听器；**无 NaN 拒收测试、无空列表语义测试**。
- 材料包缺项声明：运行时证据包与数据画像未取；Python 3.12.8。
- checklist 前置过检：#6 变体（输入断供→门禁放行）命中（见 A1/C 轴）；#8 变体（名义接线）命中；其余查无。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| C 下游 | **孤儿裁定：名义挂接成立**。唯一 import 方 performance_attribution_engine.py:275 存入 `self._correlation_gate` 后**全文件零调用**（grep `_correlation_gate.` 仅赋值行）；且该引擎以 None 缺省构造（performance_attribution_degradation.py:124 也未传 gate）。门禁在产链中**从未拦截过任何东西** | performance_attribution_engine.py:57,264,275 | P1 | `grep -n "_correlation_gate" src/zephyr/pf_core/core/performance_attribution_engine.py` → 仅 3 行（import/签名/赋值） |
| A 深度 | **空输入 → PASS（门禁 fail-open）**：`pairs=[]` → worst([])=PASS（line 84-88,275），pairs_checked=0 无任何告警。上游指标断供/配对生成故障返回空列表时，闸门静默放行——对"防同质化上线"的闸门，无数据=应显式失败而非通过。checklist #6 问句"断供时报错还是恒 0"在本件的答案是"恒通过" | strategy_correlation_gate.py:249-296 | P1 | `StrategyCorrelationGate().check([])` → passed==True 且无异常 |
| A 深度 | **全 None 维度 → 盲闸通过**：所有指标 None 的 pair 全维度跳过（line 158-159,334-409），结果 PASS 且无"实际检查了 0 个维度"的披露（只有 pairs_checked 计数） | line 158-159 | P2 | 全 None pair → result.violations==[] 且 passed |
| A 深度 | **HARD_REJECT 可被持续天数降级为 WARN**：corr=0.99 + correlation_sustained_days=1 → WARN（可上线），line 413-422 对 REJECT/HARD_REJECT 一视同仁降级。#20 持久化条件防单日噪声的初衷合理，但最严档被元数据降级的政策后果（新观测即放行高危对）未见单独声明 | line 413-422,124-126 | P2 | corr=0.99/days=1 → verdict==WARN |
| A 深度(边界·查无) | NaN/越界 fail-closed：NaN 不满足 [-1,1]/[0,1] → InvalidCorrelationInputError（line 305-326）；自相关对拒收（line 306-307）；配置关系校验（reject<hard_reject 等，line 140-145）。**NaN 不能穿透本件** | line 304-326 | — | correlation=nan → raise |
| A 深度 | `abs(correlation)` 把强负相关（-0.95）判 HARD_REJECT：对线性分散化负相关本是利好，同质化门禁按"非独立性"从严——文档化取舍（头注 line 8），偏保守可接受，登记语义备注 | line 333-335 | P3 | corr=-0.95 → HARD_REJECT |
| A.3 测试 | 主路径+降级路径覆盖可；NaN 拒收与空列表语义（P1）无测试钉住 | tests/.../test_strategy_correlation_gate.py | P3 | grep 测试文件无 nan/空列表断言 |
| B 上游 | **上游估计契约未文档化**：窗口长度/样本量/PIT 口径全部在"数据层"（line 33）却无契约文件——相关性估计样本不足（如 20 日窗口 r 噪声大）会直接变成 REJECT/WARN 判决，门禁质量完全受未契约化输入摆布 | line 32-33 | P2 | 蓝图/头注无估计窗口声明 |
| C 下游 | 事件监听器异常被吞（error log，line 443-448，5.135 治标既定设计）；result.passed/rejected 语义清晰。当前零实际消费=爆炸半径 0；接线后=策略上线决策面 | line 443-448 | — | 注入 raise listener → log 不抛 |
| D 旁系 | pf_core/core/constraint_solver.py:4 注释"MOD-PA-004 策略级门禁由上层调用"——**上层并不调用**（与本审查 C 轴互证），注释承诺失实；与 90 号滚动相关性剔除规则的口径统一仅在 correlation 维度（line 124-126），factor/tail 无持久化条件——口径不对称但属 #20 明示范围 | constraint_solver.py:4 | P3 | grep constraint_solver 引用 |
| E 对抗 | 无状态判定（除 listeners 列表）：幂等、重复触发安全、无时序依赖（查无）；listeners 并发订阅无锁（单线程前提） | 全文件 | — | 同输入两次 check 比对 |

## 3 SOTA 对照

- 阈值式同质化门禁（相关性/重叠度/尾部相关多维聚合取最严重）属规则工程实践，无单一权威方法。战役检索预算 2 次已耗于 W02（BMA）与 W05（risk parity），**本件未独立检索——如实记"受阻（预算受限未查证）"**。接线时建议对照：策略容量/拥挤度文献的拥挤度指标（crowding）与尾部的 EVT 依赖度量（本件 tail_correlation 入参语义）。

## 4 缺陷清单

1. **[P1] 名义挂接、零实际调用**：现状=唯一持有方从不调用（证据 §2 C 轴）。影响："策略相关性门禁在运行"是治理错觉；同质化策略上线无闸。建议：接线裁决——接入策略生命周期（MOD-PA-005）或 C01 screen_panel；短期至少修正头注 CONSUMERS 声明。验证法：§2 grep。
2. **[P1] 空输入 PASS（fail-open）**：现状=空列表/配对生成失败静默通过。影响：接线后数据断供=门禁失效且无声。建议：`pairs` 为空时显式抛错或返回 FAIL_CLOSED 态（与宪法 fail-closed 基调一致），"0 对"若是合法态（单策略）由调用方显式传标志。验证法：§2 实测。
3. **[P2] 全 None 维度盲过**：建议 result 增加 dimensions_checked 计数并全 0 时告警/拒绝。验证法：§2 实测。
4. **[P2] HARD_REJECT 可降级 WARN**：建议最严档不适用持久化降级（或 days 门槛分档）。验证法：§2 实测。
5. **[P2] 上游估计契约未文档化**：建议蓝图补"估计窗口≥N、PIT、复权口径"契约。验证法：文档 grep。
6. **[P3] 负相关从严语义/重复 pair 不去重（A,B)+(B,A) 双计/constraint_solver 注释失实/测试缺口**：随接线批清理。

## 5 挂起疑问

- 若"相关性门禁只在策略上线评审人工触发"是既定用法（无自动接线计划），发现 1 应降级为文档失实 P2——需 Owner 裁定本件的目标运行形态（自动闸 vs 评审工具）。

## 6 完备性自评

- 六轴全查：A（四问+边界实测）/B/C/D/E 全查；F 受阻已记；查无项=NaN 穿透、时序竞态、重复触发副作用。
- 长尾：tail_correlation 的 EVT 估计质量与 same_direction 元数据的判定来源（谁标 same_direction）未追——入参语义文档化后再审。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
