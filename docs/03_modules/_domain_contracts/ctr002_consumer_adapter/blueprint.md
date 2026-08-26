---
module_id: MOD-CON-001
title: "CTR-002消费契约适配器蓝图 — schema版本协商+字段容忍+变更订阅"
doc_type: blueprint
status: Active
version: "0.1.1"
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
design_maturity: production
build_status: stable
---

# MOD-CON-001 CTR-002 Consumer Adapter — 消费契约适配器 蓝图

> **module_id**: MOD-CON-001 | **域**: D_CONTRACTS | **层**: L0 共享契约
> **优先级**: P1 | **成熟度**: design→testing | **对标能力**: D-SIGNAL-163 CTR-002消费契约适配器
> **SSoT**: depgraph MOD-CON-001 | **代码**: `src/zephyr/shared/contracts/ctr002_consumer_adapter.py`
> **设计真源**: A3数据架构 §17.12（B13-04308）；B2-05119 已裁定重复归并本件

## 0. 边界

- CTR-002 FactorSignal 契约定义归 `factor_signal.py`（codegen，SSoT=
  cross_layer_contracts.yaml），本模块不定义契约、只做消费侧**管理面**。
- MOD-SIG-087 factor_result_bridge 报告预留"CTR-002 适配器未建 provider 注入
  前瞻兼容（W-P1-16）"——本模块即该适配器；桥接器取数经本适配器落地后接线
  （留运行时装配批）。
- 生产侧强制验证归 MOD-CON-002（互补面，共用本模块持有的同一 Schema 源）。

## 1. 定位

信号消费方统一经适配器取数：schema 版本协商（major 不兼容即拒）+ 字段缺失/
新增容忍策略 + 契约变更事件订阅。纯内存判定，零存储 IO（provider 由消费方注入）。

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | 原始 payload（Mapping，含 schema_version） | CTR-002 字段 |
| 输入 | 订阅回调 callback(ContractChange) | 变更事件 |
| 输出 | AdaptationVerdict（accepted/signal/version_action/filled/absorbed/reason） | frozen |
| 输出 | BatchVerdict / ContractChange / audit_log | frozen |

## 3. 核心设计

### 3.1 同一 Schema 源（CTR002_SCHEMA）

自 CTR-002 FactorSignal 推导：current_version="1.0"、必填五字段
（as_of_date/factor_id/idempotency_key/raw_value/symbol）、可选默认值表、
取值域规则表（prob_range/non_empty_str/finite_number/semver_str/datetime_type）。
MOD-CON-002 生产侧验证器复用同一实例，规则源不另造、不漂移。

### 3.2 版本三态协商

- exact：incoming 命中 supported 版本。
- compatible：同 major（minor 增减容忍， additive 变更不炸消费方）。
- unsupported：major 不一致或版本串非法 → fail-closed 拒收（不抛异常、
  绝不静默按错版本解析）。

### 3.3 字段容忍

- 缺可选字段 → 补默认值（list/dict 每次构造独立实例，零共享可变态），
  filled_defaults 留痕。
- 缺必填字段 → 拒收，missing_fields 列明。
- 新增未知字段 → 收编 extra（与显式 extra 合并），absorbed_extras 留痕。

### 3.4 契约变更事件订阅

subscribe(callback) 登记；publish_contract_change(new_version, note) 版本只升
不降（降级/同版/非法 → Ctr002AdapterError），通知全体订阅者（单订阅异常
不阻断他人），audit_log 全量留痕，返回实际通知数。

## 4. 关键不变量 (INVARIANTS)

- major 不兼容即拒（fail-closed 不抛）。
- 缺必填 fail-closed；新增字段收编 extra 并留痕。
- 版本只升不降；订阅通知单点失败不阻断。
- 全部裁决 dataclass frozen。

## 5. 错误契约

- `Ctr002AdapterError`（占位 ZA-CON-UNREGISTERED-adapter）：配置/输入/版本非法。

## 6. 依赖

- `zephyr.shared.foundation.errors`；`zephyr.shared.contracts.factor_signal`
  （构造 FactorSignal，延迟导入）。

## 7. 测试

`tests/contracts/test_ctr002_consumer_adapter.py`（43 例）：Schema 源派生/
semver 解析/三态协商/字段容忍/批量适配/订阅发布/用法 Fail-Closed/frozen。

## 8. 遗留

- 运行时接线：factor_result_bridge provider 注入接本适配器（前瞻兼容声明落地）；
  真实 Redis/CH provider 装配留运行时装配批。
- 错误码正式登记（占位→ZA-CON 新前缀，需主代理裁定，见 P1W16 fragment）。

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-CON-001`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-CON-001` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-CON-001` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-CON-001 | MOD-CON-001 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | stable | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 9. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 9.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/shared/contracts/ctr002_consumer_adapter.py` | ✅ 已实现 | |

### 9.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/contracts/test_ctr002_consumer_adapter.py` | ✅ 已实现 | |

### 9.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §9（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
