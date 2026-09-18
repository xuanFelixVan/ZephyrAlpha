---
ttl: task_bound
doc_type: report
title: 深度审查报告——F02 因子工厂阶段闸（FactorFactory）
owner: st-deeprev-20260918
reviewer_model: GLM-5.3-Flash
baseline_commit: 2fa92002c3
created: 2026-09-18
---

# 深度审查报告：F02 因子工厂阶段闸（GLM-5.3-Flash / 基线 2fa92002c3）

- 状态: **已审**
- 级别: P1｜类型: 引擎（9 阶段生命周期编排）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/factor/factor_factory.py:78(:160 StageGateVerdict, :191 FactorFactory)`
- 生产调用方: factor_production_pipeline.py（真实）、autonomy_core/agents/_g04_ops_check.py、governance/ops_governance/phase_manager.py、ml_train/core/model_version_registry.py、pf_core/core/strategy_factory.py（grep 实证≥1，非孤儿）
- 测试文件: tests/factor/test_factor_factory.py（存在）
- 变更热力: 2026 年 4 commits（低热，稳定）
- 材料包缺项: 运行时证据包缺（design 级，可接受）

## 1 对象快照

9 阶段工厂（candidate→hypothesis→generation→validation→registration→monitoring→iteration/deprecation→retirement），显式边表 _STAGE_EDGES，门禁三委托（IC/因果/回测），底层复用 MOD-L02-013 生命周期 FSM 逐站正向驱动。排除项：lifecycle_state_machine 本体（旁系依赖，已读关键转换）、registry 注入实现。测试存在，但未覆盖回炉全链生命周期断言（见 A-01 验证法）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | **回炉重验烧毁底层生命周期（复算实锤）**：ITERATION→VALIDATION 时 _drive_lifecycle(goal=BACKTEST) 从 PRODUCTION 只会沿 _LIFECYCLE_FORWARD 单向走到 RETIRED 死路（RETIRED 无出边→return 不达 goal 不报错）；复算：advance 全链到 MONITORING(lifecycle=production)→ITERATION→VALIDATION 后 lifecycle_state_of()=**"retired"** 而工厂 stage=validation；随后 VALIDATION→REGISTRATION 照常注册成功（:320-335 不查 lifecycle 状态）——退役态因子入库 | factor_factory.py:285-300, 129-137, 116-126; lifecycle_state_machine.py:21-85（转换表无 PRODUCTION→BACKTEST 回退边） | **P1** | 复算脚本（已实测）：submit→HYPOTHESIS→GENERATION→VALIDATION→REGISTRATION→MONITORING→ITERATION→VALIDATION，打印 lifecycle_state_of()=="retired" |
| A | **三重门禁默认全开**：ic/causal/backtest validator 缺省 lambda:True——装配批漏接=垃圾因子静默通过门禁入库；与 ERROR_CONTRACT"未装 mining_hook 抛错"的 fail-closed 风格相反 | factor_factory.py:218-220, 275-283 | P1 | 构造 FactorFactory() 无委托，advance 到 VALIDATION 观察直接 passed |
| B/C | registry 未装时 REGISTRATION 静默跳过注册但 verdict passed=True——"入库"阶段没入库；与 mining_hook 缺装抛 FactorFactoryError（:262-263）不对称 | factor_factory.py:326-335 vs 262-263 | P2 | registry=None 推进到 REGISTRATION，看 passed=True 且无注册副作用 |
| D | 文档口径漂移：header :36"验证一次通过不回炉" vs :312-318 ITERATION→VALIDATION 重跑三重门禁（合法回炉边 :38 已认可，但"仅一次"表述与实现冲突） | factor_factory.py:36-38, 312-318 | P3 | 对读两处 |
| A | ITERATION 目标 None（不动底层 :123）设计自洽；GRAYSCALE 站在 _LIFECYCLE_FORWARD 有但工厂永不指向——冗余无害 | factor_factory.py:116-137 | P3 | 读表 |
| E | _drive_lifecycle 中 fsm.transition 若底层加 guard（如终态禁转）将抛异常中断 advance，无捕获——当前 FSM 无 guard 故不触发，属潜在耦合 | factor_factory.py:298; lifecycle_state_machine.py:112 | P3 | 代码走查 |
| A.3 | 测试缺回炉场景断言（lifecycle_state_of 在 ITERATION→VALIDATION 后的期望值无覆盖）——P1-A01 正是从此缝隙漏过 | tests/factor/test_factor_factory.py（grep 无 iteration+lifecycle 断言） | P2 | grep 测试文件关键词 iteration |

## 3 SOTA 对照

- 因子全生命周期治理（立项→验证→生产→退役）与业界平台流程（WorldQuant BRAIN 平台 alpha 生命周期、qlib recorder 实验管理）——**受阻未搜**（本批检索预算用于数学核心；编排类对象）。docstring 自述查重裁定已排除与 ic_ir_calc/回测门禁的重复。
- 结论：受阻如实记；A-01 修复方向（回炉走显式回退边或双射映射校验）不依赖外部 SOTA。

## 4 缺陷清单（按严重级）

1. **P1 回炉烧毁生命周期**：现状=ITERATION→VALIDATION 后底层 FSM=retired 且后续注册照常；证据=:285-300 单向驱动+:129-137 死路+:320-335 注册不查 lifecycle；影响=回炉重验的因子以退役态注册，审计链（lifecycle_driven_to 未更新 :300）与真实状态永久背离，爆炸半径=因子治理账本可信度（决策系统性失真，不报错）。建议修法：_drive_lifecycle 对"goal 在当前态之前"显式抛错或走 FSM 合法回退边（BACKTEST→RESEARCH 在案）；REGISTRATION 前断言 lifecycle==PAPER。验证法：§2 A-01 复算脚本（已实锤）。
2. **P1 门禁默认全开**：缺省 lambda:True 使"三重门禁"退化为可选装饰。建议：缺省 None+advance 时 fail-closed 报"验证器未装配"。验证法：无委托构造推进观察。
3. **P2 registry 静默跳过**：REGISTRATION 无注册表时 verdict 应 failed 或构造期强制注入。验证法：§2 B/C 行。
4. **P2 测试缺回炉断言**；**P3** 文档口径漂移、GRAYSCALE 冗余、transition guard 耦合。

## 5 挂起疑问

- factor_production_pipeline.py 对 FactorFactory 的装配是否已接真实验证器（若已接，P1-2 降级为防御性缺陷）——待收口方沿装配批核实。

## 6 完备性自评

六轴全查（F 受阻记）。长尾：①mine() 并发重入未审（单线程假设）；②audit_sink 记录 schema 无 schema 校验（风格级）。

## 7 收口裁定（收口方填）
- 三态逐条:
- 修复 commit:
- 复检结论:
