---
ttl: task_bound
doc_type: report
title: 深度审查报告——生命周期FSM（T04）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：生命周期FSM（T04）

- 状态: **已审**
- 级别: P1｜类型: 晋升闸（越级晋升防护）
- 基线 commit: 2fa92002c3（工作树 bf65648609；本文件自基线零变更，锚点双有效）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/strategy_pipeline/lifecycle_fsm.py:112(build_strategy_fsm)/:75(SimPromotionGuard)/:87(OwnerTokenGuard)`
- 生产调用方: intake.py:317（candidate→sim）；promotion_advisory.py:634（sim→production 执行器）；base=zephyr/shared/lifecycle/state_machine.py（376 行，RLock+history+reset）
- 测试文件: tests/strategy_pipeline/test_lifecycle_fsm.py（8 用例）
- 材料包缺项: 无（对象小而封闭）；secrets 键 ZEPHYR_OWNER_APPROVAL_TOKEN 实际配置态未探测（不应由审查者读取）

## 1 对象快照

- 范围：5 态 7 边 FSM 定义+两 guard+构建工厂；连带审 base StateMachine 的 transition/reset/guard 异常语义（生命线依赖）。排除：promotion_advisory 的注册表手术写（T06 对象）。
- 状态图：candidate→sim(guard 三条件)/shelved；shelved→candidate/retired；sim→production(Owner token)/shelved；production→retired(Owner token)；retired=terminal。
- 测试覆盖概况：8 用例覆盖自动晋升/搁置回补/直连拒绝/token 门/三条件/无 context fail-closed/退役门/搁置退役——关键路径齐；**实例重建/hydration 语义无测**。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | **FSM 实例无持久化，真源双承载**：`build_strategy_fsm(sid)` 每次新建实例恒从 candidate 出发（lifecycle_fsm.py:112-135）；系统真实状态=注册表 lifecycle_status 字段。FSM 内存态与注册表态无同步机制——防跃迁只约束"从正确初态出发的单次调用"，不约束实例重建 | lifecycle_fsm.py:112-135; promotion_advisory.py:199-200（真源读侧） | **P2** | 两次 build_strategy_fsm("X") 各自 current_state 均为 candidate，互不知晓 |
| A | **base `reset(initial)` 无条件置任意态+清 history**：任何持实例者 `fsm.reset("production")` 即绕过全部 guard/边约束——越级晋升防护的强度完全落在调用量级外围（注册表 CAS+Owner token），FSM 本体是规则编码器非防线 | zephyr/shared/lifecycle/state_machine.py:262-268 | **P2** | fsm.reset(PRODUCTION); assert fsm.current_state=="production" |
| A | SimPromotionGuard 只复核调用方自报布尔（dual/bhfdr/no_decay 三字段，:78-84），不复核任何证据——预授权三条件的证据链在调用方（intake:313-318），API 面上任何代码可自造全 True context 得 sim；A 方案设计文档已声明此边界，纵深缺口如实登记 | lifecycle_fsm.py:78-84; intake.py:310-318 | P2（设计已知） | 直接 transition(SIM, 全True ctx) 观察通过 |
| A | OwnerTokenGuard 实现正确：sha256 双侧+hmac.compare_digest 常量时间（:106-109）；未配置 secret=fail-closed 拒绝+warning（:101-105）；空串/非串 token 拒绝（:98-100）——"非空即真"已废 | lifecycle_fsm.py:97-109 | 已查无（正面） | tests: test_sim_to_production_requires_owner_token |
| A | 跃迁完备性：candidate→production 无直连边（直跳=InvalidTransitionError，tests:61 实证）；retired terminal 无出边；**production 无降档边**（衰减只能退役且不可复活）；**sim→candidate 缺失**，降级须 sim→shelved→candidate 两跳——shelved→candidate 语义注释为"家族替身回补"，与"衰减降档回补"复用同一边，语义未来分叉处 | lifecycle_fsm.py:123-131, :29 | P3 | 读 transitions 表画图核对 |
| A | guard 抛异常路径：check 返回 False→TransitionGuardError（base:227-232）；check 自身 raise→原样穿出（未捕）——调用方 intake promote_to_sim 全捕折布尔（intake.py:173-174），fail 方向一致 | state_machine.py:223-232 | 已查无 | — |
| A.3 | 8 用例断言直跳拒绝/token 缺失拒绝/无 context fail-closed——guard 负路径覆盖到位；fresh-instance hydration 无测（与发现 1 同根） | test_lifecycle_fsm.py:50-115 | P3 | 无 reset/hydration 用例 |
| B | 上游=两个调用方的 context 构造（intake 三条件来源已审；promotion_advisory token 来源待 T06 细审）；secrets 键读取经 zephyr.shared.security.secrets（RULE-SECRETS 合规入口，非裸 getenv） | lifecycle_fsm.py:53, :101 | 已查无 | — |
| C | 下游消费=注册表 lifecycle_status→TDM R12/面板/晋升链；FSM 无直接写副作用（写全部在外围 registry_writer/手术更新）——爆炸半径由写侧闸决定，本件纯逻辑 | lifecycle_fsm.py 全文 | 已查无 | — |
| D | 兄弟实现：因子版 8 态 10 转换 FSM（docstring :23 自述"复用因子版模式"）——同族两套生命周期 FSM（因子/策略），转移表独立维护，口径漂移面登记 | lifecycle_fsm.py:23 | P3 | grep factor lifecycle fsm 定义 |
| E | 并发：base RLock per-instance（state_machine.py:184）——**跨进程/跨会话无互斥**：两会话各自建实例对同一 sid 判 sim 晋升，内存层各自成立，真源冲突由注册表 CAS 兜底（intake 路径 append CAS 已核；手术更新 CAS 归 T06）；竞态窗口="FSM 判过→持久化成功"之间 | state_machine.py:184, :224 | P3 | 双进程并发晋升对账注册表唯一性 |
| E | 重入/重放：同态重转=InvalidTransitionError；重放幂等由注册表键（code_path/sid）承载非 FSM——职责分界清晰 | state_machine.py:223-228 | 已查无 | — |
| E | Owner token 为单一静态密钥：无轮换/无 per-decision nonce/**成功路径无审计日志**（仅失败 warning :103）——用 token 晋升了谁、何时，FSM 层零留痕（依赖外围写侧审计） | lifecycle_fsm.py:97-109 | P3 | grep 成功路径 logger |

## 3 SOTA 对照

1. **状态机治理模式（对等已有）**：带 guard 的显式状态机+terminal 态+人类审批门是工作流引擎标准做法（guard 语义与 UML state machine guard 一致——Object Management Group《UML 2.5.1》规范，OMG，2017，https://www.omg.org/spec/UML/2.5.1）；令牌比对用 sha256+hmac.compare_digest 防时间侧信道= secrets 处理标准做法（OWASP Cheat Sheet 系列，OWASP Foundation，https://cheatsheetseries.owasp.org/）。
2. **晋升流水线（对等已有）**：candidate→paper→production 渐进上线为量化/MLOps 部署成法（QuantStart 部署系列，https://www.quantstart.com/articles/）；本仓在 paper 前再加 FDR 统计门+衰减门，属超额治理。
3. 结论：**对等已有**，无立卡项。

## 4 缺陷清单

1. **[P2] FSM 内存态与注册表真源双承载、实例可任意 reset**——现状：build 恒从 candidate 起（lifecycle_fsm.py:112-135）+base reset 无 guard 置任意态（state_machine.py:262-268）；影响：FSM 的防跃迁语义是"调用点纪律"而非机械防线，越级防护实重担在注册表 CAS+OwnerTokenGuard+写后复核（该三层在位，见 T02/T06）；建议：①文档明示"FSM=规则编码器，防线的真源=注册表+token"；②加 `hydrate(sid, lifecycle_status)` 工厂从真源初化，杜绝手拼初态；验证法：reset 复演+两实例互不知晓演示。
2. **[P2] SimPromotionGuard 证据自报制**——现状：三布尔由调用方构造（:78-84）；影响：绕过 intake 直接驱动 FSM 可得 sim（需代码动作，非运行时漏洞；sim=纸面故非资金险）；建议：guard 收 evidence 引用（台账批号）并留审计字段；验证法：全 True context 直调复演。
3. **[P3] production 无降档边+retired 终态不可逆**——现状：衰减的 production 策略唯一出路=退役（:123-131）；影响：无"降回 sim 观察"中间态，治理粒度粗；建议：Owner 裁定是否需要 production→sim 降档边（带 token 门）；验证法：读转移表。
4. **[P3] token 成功使用零审计**（:97-109）——建议：成功路径 log.info 留 sid+目标态（勿记 token 本体）；验证法：grep logger 调用。
5. **[P3] shelved→candidate 语义双载**（:29 回补 vs 降级回补复用）——建议：注释分流或拆边；验证法：读 docstring。
6. **[P3] 与因子版 FSM 双实现漂移面**（:23）——建议：两转移表对账入 align 清单；验证法：grep 因子 FSM 定义对比。

## 5 挂起疑问

1. ZEPHYR_OWNER_APPROVAL_TOKEN 的配置态/轮换周期归 Owner 秘钥管理——FSM 层只能确认"未配置=全拒"，实际是否配置审查者不探测（材料包缺项声明）。
2. production 策略若发现统计失效（decay/翻案），Owner 是否需要"停用但保留态"的第五态（suspended）？现设计只能退役。
3. intake promote_to_sim 捕获一切异常折布尔（intake.py:173-174）——TransitionGuardError 与意外 TypeError 不可分，是否需要区分日志？

## 6 完备性自评

- 六轴全查：是。A（转移表逐边核对+guard 密码学实现复核+reset 边界）、B（context 两来源+secrets 入口）、C（无写副作用/写侧闸分工）、D（因子版兄弟）、E（并发/重入/重放/token 审计五问）。
- 长尾：①base StateMachine 其余方法（history/can_transition）未逐行；②因子版 FSM 本体未审（同族对象建议另列）；③secrets.py 读取链信任 RULE-SECRETS 门禁未复验。

## 7 收口裁定（收口方填）
- 三态逐条:
- 修复 commit:
- 复检结论:
