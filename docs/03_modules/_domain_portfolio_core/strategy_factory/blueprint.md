---
blueprint_id: MOD-PF-009
module_name: strategy_factory
domain: D_PF_CORE
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: H
ai_autonomy: human_gated
version: "0.1.0"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
priority: P1
blueprint_level: module
domain_id: D_PF_CORE
path: src/zephyr/pf_core/core/strategy_factory.py
granularity: file
---

# MOD-PF-009 strategy_factory 蓝图（C-006 策略工厂）

> **module_id**: MOD-PF-009 | **域**: D_PF_CORE | **优先级**: P1
> **来源**: B1-00189（AUD-DRAFT-001-DIGEST P1 波 W-P1-21，CAND-PF004-002，§功能域模块·D-PORTFOLIO）
> 代码：`src/zephyr/pf_core/core/strategy_factory.py`

## 0. 定位

策略全生命周期工厂：10 阶段状态机 + 策略注册表 + 自动发现四通道
（GP/SR/LLM/FactorMAD）发现钩子，产出必经 C-003 三重门禁 + p-hacking 评估 +
人工裁决，**严禁全自动上线**。

查重分工（W-P1-21 铁律②+R2 裁定在案——P1W07 工厂三兄弟归并注
"StrategyFactory=C-006 归 W-P1-21 B1-00189"）：

| 既有件 | module_id | 职责 | 与本模块边界 |
|---|---|---|---|
| factor_factory | MOD-L02-001 | 因子 9 阶段工厂（FactorMAD 留 mining_hook） | 本件=策略族工厂，因子厂为其上游发现通道之一 |
| signal_factory | MOD-SIG-087 | 信号草稿→记录工厂（信号域） | 信号≠策略，不同域不重叠 |
| strategy_book | MOD-POS-020 | 持仓域策略账本（仓位口径） | 账本非生命周期工厂 |
| strategy_engine / strategies/ | MOD-PF-001 等 | 运行时策略执行面 | 执行≠工厂编排；本件不 import 执行面 |
| strategy_cpcv_matrix | MOD-BT-028 | C-003 离线 CPCV 打分 | 本件消费其门类**结论**（gate_verdict 注入），不跑回测 |

TSV 裁定原文（做 P1）："StrategyFactory:10阶段状态机+策略注册表+自动发现四通道
(GP/SR/LLM/FactorMAD),产出必经C-003三重门禁+p-hacking评估+人工裁决,严禁全自动上线"。

## 1. 规则（确定性，B-009 testing 封顶）

- **10 阶段**：DRAFT→HYPOTHESIS→GENERATION→VALIDATION→GATE_REVIEW→
  PHACKING_REVIEW→HUMAN_ADJUDICATION→REGISTRATION→MONITORING→RETIREMENT；
  任一评审阶段可 →REJECTED（终态）。
- **四通道发现**：DiscoveryChannel ∈ {GP, SR, LLM, FACTOR_MAD}；intake 必须声明
  通道；discovery_hook 只产 DRAFT 候选（钩子注入，本件不内建 GP/SR/LLM 实现）。
- **C-003 三重门禁**：进 GATE_REVIEW 须注入 gate_verdict（True/False+明细，
  真源=回测域三重门禁结论）；False → REJECTED。
- **p-hacking 评估**：进 HUMAN_ADJUDICATION 前须注入 dsr/pbo 指标；确定性判定
  `dsr > 0 且 pbo ≤ pbo_max`（默认 0.5）否则 REJECTED（口径对齐 MOD-SIM-024/
  MOD-REGIME-VAL 方法论栈，指标注入不 import）。
- **人工裁决**：approve 必须 approved_by 非空；严禁全自动——本件无任何
  auto-approve 路径，注册条目 status 恒 candidate（治理串行合并）。
- Fail-Closed：空 id/名称、非法迁移、缺门禁/p-hacking 证据、approved_by 空 →
  StrategyFactoryError。

## 2. 接口

- `StrategyStage`（10 阶段）/ `DiscoveryChannel` / `StrategyRecord`（frozen）
  / `StrategyRegistryEntry`（frozen，status 恒 candidate）
- `StrategyFactory(pbo_max=0.5, clock=None)`
  - `intake(name, channel, hypothesis="") -> StrategyRecord`
  - `advance(strategy_id, to_stage, note="") -> StrategyRecord`
  - `submit_gate_verdict(strategy_id, passed, detail="") -> StrategyRecord`
  - `submit_phacking_metrics(strategy_id, dsr, pbo) -> StrategyRecord`
  - `human_adjudicate(strategy_id, approved, approved_by, note="") -> StrategyRecord`
  - `register(strategy_id) -> StrategyRegistryEntry`
  - `retire(strategy_id, reason)` / `get(strategy_id)` / `list_strategies(stage=None)`

## 3. 不做什么

不跑回测（门禁结论注入）、不实现 GP/SR/LLM 生成器（发现钩子注入）、不做运行时
执行（MOD-PF-001 族）、不直改任何共享注册表。
