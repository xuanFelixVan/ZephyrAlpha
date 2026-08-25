---
module_id: MOD-CON-002
title: "CTR-002生产侧契约验证蓝图 — 字段完整性/取值域/PIT+违约阻断+错误契约"
doc_type: blueprint
status: Active
version: "0.1.0"
ttl: permanent
layer: L00_shared
layer_name: contracts
functional_domain: contracts
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-25"
last_updated: "2026-08-25"
priority: P1
blueprint_level: module
responsibility_domain: 
design_maturity: design
build_status: testing
---

# MOD-CON-002 CTR-002 Producer Validator — 生产侧契约验证 蓝图

> **module_id**: MOD-CON-002 | **域**: D_CONTRACTS | **层**: L0 共享契约
> **优先级**: P1 | **成熟度**: design→testing | **对标能力**: D-SIGNAL-158 二元结论补充（CTR-002生产侧契约验证）
> **SSoT**: depgraph MOD-CON-002 | **代码**: `src/zephyr/shared/contracts/ctr002_producer_validator.py`
> **设计真源**: D-SIGNAL §1.1（B2-05118）

## 0. 边界

- 与消费侧适配器（MOD-CON-001）**互补**：001=消费侧版本协商/字段容忍/变更
  订阅；本模块=生产侧出厂强制验证（字段完整性/取值域/时间戳 PIT）。
- **共用同一 Schema 源**：基础取值域规则直接复用 MOD-CON-001 的
  CTR002_SCHEMA.field_rules（同一实例），生产侧仅增补 PIT/整型域/其余必填
  非空——规则源不另造、不漂移。
- MOD-L02-001 ctr002_producer（converter）=信号构造（z-score/rank_pct/幂等键），
  本模块为其出厂闸口（挂接留运行时装配批）；不做因子计算。
- MOD-SIG-087 factor_result_bridge=消费桥接（版本三态+审计），与本模块同族
  分工：bridge 管消费、本模块管生产，互不重叠（同族衔接口径=同一 Schema 源）。

## 1. 定位

FactorSignal 出厂前强制验证：字段完整性/取值域/时间戳 PIT 校验；违约阻断
（strict 抛异常）或错误契约返回（collect 模式 ErrorContract，违约信号不出厂）；
验证指标入 telemetry（计数器 + metrics_hook 注入）。

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | FactorSignal 实例（单条/批量） | CTR-002 |
| 输入 | clock / metrics_hook 注入 | — |
| 输出 | ValidationReport（ok/violations/error_contract） | frozen |
| 输出 | ErrorContract（contract_id/producer_domain/violations/factor_id/symbol） | frozen |

## 3. 核心设计

### 3.1 规则体系

1. 基础取值域（同一 Schema 源 CTR002_SCHEMA.field_rules）：confidence/rank_pct
   ∈[0,1]；raw_value 有限数值；factor_id 非空；schema_version 合法 semver；
   as_of_date datetime 类型。
2. 生产侧增补：symbol/idempotency_key 非空；max_retries ≥0、timeout_ms ≥1 整数。
3. PIT 时间戳：as_of_date 不得晚于 clock() 当前时点（aware 归一本地 naive 比较）。

### 3.2 违约处置双模

- collect（默认）：返回 ValidationReport(ok=False, error_contract=...)，
  违约信号不出厂（调用方剔除）。
- strict：抛 ProducerValidationError（携 error_contract 结构化违约清单）——
  违约阻断。

### 3.3 验证指标

total_validated / total_violations 计数器；metrics_hook(name, value) 注入
（ctr002_producer.validated / ctr002_producer.violation），hook 异常不阻断验证。

## 4. 关键不变量 (INVARIANTS)

- 违约信号不出厂（collect 剔除 + 错误契约返回；strict 阻断）。
- Schema 源与 MOD-CON-001 同一实例（schema property 恒为 CTR002_SCHEMA）。
- PIT 校验 clock 注入可测；aware/naive 混合归一比较。
- metrics_hook 异常不阻断。

## 5. 错误契约

- `ProducerValidationError`（占位 ZA-CON-UNREGISTERED-producer）：strict 违约阻断，
  携 error_contract。

## 6. 依赖

- `zephyr.shared.contracts.ctr002_consumer_adapter`（CTR002_SCHEMA/parse_semver，
  同一 Schema 源）；`zephyr.shared.contracts.factor_signal`（isinstance 校验，
  延迟导入）；`zephyr.shared.foundation.errors`。

## 7. 测试

`tests/contracts/test_ctr002_producer_validator.py`（23 例）：取值域/PIT（clock
注入/aware 归一）/双模违约处置/指标与 hook 异常不阻断/同一 Schema 源身份断言/
frozen。

## 8. 遗留

- 运行时接线：ctr002_producer converter 出厂路径挂 validate(strict=?) 与
  telemetry 接线——留运行时装配批。
- 错误码正式登记（占位→ZA-CON 新前缀，需主代理裁定，见 P1W16 fragment）。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-CON-002`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-CON-002` 的 2 个 file 节点 | design | `extract_depgraph.py --modules MOD-CON-002` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-CON-002 | MOD-CON-002 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | testing | testing | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
