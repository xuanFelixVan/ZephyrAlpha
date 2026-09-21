---
oid: C03
title: 持仓裁决中心（position_adjudication_center MOD-POS-024）
status: 已审
reviewer: GLM-5.3-Flash/st-deeprev-20260918
baseline: 2fa92002c3
date: 2026-09-18
ttl: task_bound
---

# 深度审查报告：C03 PositionAdjudicationCenter（GLM-5.3-Flash / 基线 2fa92002c3）

## 1 对象快照

- 入口：`src/zephyr/position/core/position_adjudication_center.py:192`（adjudicate:240 / verify_bypass:276）。
- 架构：纯编排件——四层判定全委托注入 callable（生产装配=allocation_orchestrator.build_adjudication_center:527），本件只管顺序/收敛/令牌/Fail-Closed。
- 排除项：四层判定实现本体归 C01 报告（其口径问题在 C01 记）。
- 测试覆盖：tests/position/test_position_adjudication_center.py 12 passed（1.44s），含 Fail-Closed/幂等/旁路断言。
- 生产接线：唯一消费者=C01 装配体；verify_bypass 零调用。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | 数学四问：min(四层 adjusted) 收敛——四层各自从同一 intended 单调缩减，min-of-parallel ≡ sequential-min，数学等价；intended_weight NaN 被 __post_init__ 拒（`not 0<=NaN<=1`=True→raise）；LayerVerdict 越界值经 __post_init__ raise→被 _call_layer 收敛为拒绝，双保险 | position_adjudication_center.py:118-119,161-165,217-238,264 | 已查无 | 12 测试+NaN 单行验证 `AdjudicationRequest(...,intended_weight=float('nan'))` 应 raise |
| A.3 | 测试审查：denial/fail-closed/idempotent/bypass 全覆盖，断言强（exact token/final_weight==0）；缺 NaN 输入与跨实例令牌用例 | tests:66-175 清单 | P3（缺口） | grep nan=0 于测试文件 |
| B | 输入追源：四层 callable 由装配体注入，本件对层返回值做类型+域校验（:230-237 契约违反→拒绝）——上游错→本对象 fail-closed，合格；request.context 键语义无 schema（"键值由层解释"自认）——隐式契约未文档化 | :99,230-237 | P3 | 代码阅读 |
| C | 下游：**verify_bypass 零生产调用**——"下单链令牌校验接线"（头注 :8）不存在；旁路阻断不变量当前无执行点 | grep verify_bypass 全仓（除本体/test）零命中 | **P2** | grep 命令 |
| C | 令牌载体进程内存态（_issued dict）——跨进程/重启后合法历史令牌在任意新中心实例 verify_bypass 必判 bypass（:282-284 issued=None→True）；接线下单链前必须解决令牌持久化，否则全部合法单被误拦或（若消费方规避）闸被绕过 | :215,276-285 | **P2** | 两个中心实例同请求各发令牌互验→互判 bypass |
| D | 幂等口径：fingerprint 含 context（:126-137），而生产 context 含 run_id（orchestrator:1134-1136）→"同请求幂等"仅轮内成立，跨轮同决策新令牌——与头注"同请求幂等不重复签发"的广义读法有差，当前无害（每轮新建中心） | :123-140 + allocation_orchestrator.py:1134 | P3 | 两轮同决策指纹对比 |
| D | default=str 序列化：context 值不可 JSON 时按 repr 指纹——不同对象同 repr 可碰撞（低概率，接受面） | :136 | P3 | 造同 repr 两 context |
| E | 静默失败面：层异常→拒绝+exc_info 日志（:221-229）——fail-closed 正确但**层 bug 会整链静默清仓**（表现为全 symbols allowed=False），爆炸半径=该策略全标的；建议装配层对"层异常率"设告警阈值 | :217-229 + orchestrator:1156-1168 | P2 | 注入抛错层→观察 verdict 全拒且仅 log |
| E | 重放攻击面：同 fingerprint 重复 adjudicate 返回首份裁决（:245-246）——若首份在事实变化（如 freeze 翻转）前签发，后续同指纹请求拿到陈旧裁决；当前每轮新建中心+每 (sid,sym) 单次调用，不触发；长生命周期复用即踩 | :244-246 | P3 | 同中心两次 adjudicate 夹状态翻转 |
| F | （见 §3） | | | |

## 3 SOTA 对照

- 本件为纯编排逻辑（顺序+min 收敛+令牌+Fail-Closed），无统计算法内核——**无单点 SOTA 对照必要**，如实记"不适用"；其 fail-closed 编排纪律与仓内 MOD-BT-001 strategy_validation_pipeline 同族自证（:25-26）。
- 家族对照（引用轴 F 已有检索）：pre-trade compliance 的令牌化审批链在业界为执行网关常见形态；检索受 429 限流，未能取得 2024-2025 直接文献，**受阻**如实记。

## 4 缺陷清单（按严重级）

1. **[P2] verify_bypass 未接线+令牌无持久化**。现状：零生产调用方；_issued 进程内存。影响：旁路阻断不变量（头注 :8）名义存在、无执行点；接线时若不解决持久化，重启后合法令牌全部误判 bypass（或被迫绕过校验）。建议修法：下单链接线时同步设计令牌落库（adjudication_id 已有唯一性，入 crisis_gate_log 式留痕表即可）。验证法：本报告 §2 C 行两法。
2. **[P2] 层异常静默清仓面**：建议装配体（C01）对 allowed=False 聚合率>阈值时升级告警。验证法：注入抛错层观察。
3. **[P3]** 幂等口径表述收窄（"同 context 幂等"）；context 无 schema；default=str 碰撞面；测试 NaN 缺口。

## 5 挂起疑问

1. 下单链（40_execution_broker/订单执行）规划中的令牌校验落点在哪——本报告 P2-1 的修法依赖该答案，建议 Owner 在接线立项时一并裁定令牌持久化载体。
2. fingerprint 是否应纳入 action 之外的仓位语境（现含 context 全量，实践上已含）——纯口径问题。

## 6 完备性自评

六轴全查。长尾：blueprint.md 未取；四层实现深审在 rpt_c01（本件职责边界内已查无重大缺陷——编排件本体干净，主要风险全在接线缺口）。
