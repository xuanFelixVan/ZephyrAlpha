---
module_id: ARCH-ENT-003
title: "合约去重分析报告 — shared + integration 双路重复（23文件）"
status: active
version: 1.0.0
date: 2026-06-27
owner: ZephyrAlpha-Owner
ttl: permanent
---

# 合约去重分析报告 — shared + integration 双路重复（23文件）

> 任务卡: DM-202925-integration | 日期: 2026-06-24 | 状态: 分析完成
> 真源数据: AST比对 + 消费者统计 + 文件内容审查 + 蓝图对照
> 前置报告: [contract_dedup_analysis.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/contract_dedup_analysis.md)（trading vs governance 24文件去重）

## 1. 问题概述

DM-202925 已完成 trading/trading_contracts vs governance/trading_contracts 的24文件去重分析（拆分为8张子卡 DM-202926~DM-202933）。本报告评估剩余的23个 shared+integration 双路重复文件。

**两套独立实现**（非 shim vs real）：
- `src/zephyr/shared/contracts/` — 蓝图声明的规范位置，混合 real + shim
- `src/zephyr/integration/shared_08/contracts/` — codegen 产物（从 cross_layer_contracts.yaml 生成），混合 real + re-export shim

## 2. 两个位置对比

| 位置 | 物理路径 | 文件数 | module_id前缀 | import行数 | 实现类型 |
|------|---------|:---:|------|:---:|------|
| shared | `src/zephyr/shared/contracts/` | 33 real + 22 shim | MOD-SHR | 100行 | 部分real+部分shim(指向shared内部_types) |
| integration | `src/zephyr/integration/shared_08/contracts/` | 47 real + 3 shim | MOD-INT | 96行 | 独立codegen(dataclass) + 部分re-export shim |

## 3. AST比对结果（23文件）

### 3.1 汇总指标

| 指标 | 值 | 说明 |
|------|:---:|------|
| 总文件数 | 23 | — |
| Class符号集相同 | 16/23 | 7个文件Class定义不同 |
| Function符号集相同 | 17/23 | 6个文件Function定义不同 |
| Class方法集相同 | 21/23 | 2个文件方法差异 |
| Class字段集相同 | 19/23 | 4个文件字段差异 |
| 文件hash相同 | 0/23 | **零hash相同——两套独立实现** |

### 3.2 消费者统计

| 位置 | 外部消费者引用总数 | 混合消费者 |
|------|:---:|:---:|
| shared.contracts | 26 | 0 |
| integration.shared_08.contracts | 37 | 0 |

**关键发现**: **混合消费者=0** — 没有任何文件同时 import 两个位置。去重零风险（不会产生 import 冲突）。

### 3.3 integration额外依赖（30个unique imports）

| 依赖类型 | 示例 | 说明 |
|---------|------|------|
| dataclass相关 | `from dataclasses import dataclass/field` | codegen风格 |
| integration内部模块 | `from zephyr.integration.shared_08.contract_enforcer import ...` | re-export shim指向 |
| integration内部模块 | `from zephyr.integration.shared_08.contract_versions import ...` | re-export shim指向 |
| integration内部模块 | `from zephyr.integration.shared_08.timestamp_utils import ...` | re-export shim指向 |
| integration内部模块 | `from zephyr.integration.shared_08.agent_identity_impl import ...` | re-export shim指向 |
| integration内部模块 | `from zephyr.integration.backpressure_types import ...` | re-export shim指向 |
| integration内部trace_context | `from zephyr.integration.shared_08.contracts.core.trace_context import TraceContext` | 内部循环依赖 |

## 4. 23文件分类（按实现类型）

### 4.1 类型A：shared=real，integration=re-export shim（4文件）

| 文件 | shared大小 | int大小 | integration指向 |
|------|:---:|:---:|------|
| core/enforcer.py | 16011B | 1115B | `zephyr.integration.shared_08.contract_enforcer` |
| core/registry.py | 12070B | 1191B | `zephyr.integration.shared_08.contract_versions` |
| core/timestamp.py | 6158B | 916B | `zephyr.integration.shared_08.timestamp_utils` |
| identity/agent_identity.py | 5516B | 1297B | `zephyr.integration.shared_08.agent_identity_impl` |

**特征**: shared有完整real实现，integration只是re-export shim指向integration内部模块。

### 4.2 类型B：shared=re-export shim，integration=real（3文件）

| 文件 | shared大小 | int大小 | shared指向 | integration问题 |
|------|:---:|:---:|------|------|
| backpressure/pause.py | 393B | 1854B | `zephyr.shared.contracts.backpressure._types` | **字段重复bug** |
| backpressure/resume.py | 396B | 1771B | `zephyr.shared.contracts.backpressure._types` | **字段重复bug** |
| backpressure/throttle.py | 402B | 1829B | `zephyr.shared.contracts.backpressure._types` | **字段重复bug** |

**特征**: shared是re-export shim（指向shared内部`_types.py`），integration是real dataclass实现。

**严重bug**: integration版本的 `backpressure/pause.py` 中 `idempotency_key: str` 字段重复定义3次（codegen缺陷）。

### 4.3 类型C：双real，shared字段更完整（4文件）

| 文件 | shared字段 | int字段 | integration问题 |
|------|:---:|:---:|------|
| external/ext_001.py | 4字段 | 0字段 | **空类(`pass`)** |
| external/ext_002.py | 4字段 | 0字段 | **空类(`pass`)** |
| external/ext_003.py | 5字段 | 0字段 | **空类(`pass`)** |
| external/ext_004.py | 4字段 | 0字段 | **空类(`pass`)** |

**特征**: shared有完整字段定义，integration是空类（codegen未生成字段）。

### 4.4 类型D：双real，功能等价（12文件）

| 文件 | Class匹配 | Function匹配 | Method匹配 | Field匹配 |
|------|:---:|:---:|:---:|:---:|
| core/base_event.py | ✓ | ✗ | ✓ | ✓ |
| core/gate_types.py | ✓ | ✗ | ✓ | ✓ |
| core/runtime_plane_tag.py | ✓ | ✓ | ✗ | ✓ |
| core/system_configuration.py | ✓ | ✓ | ✓ | ✓ |
| core/telemetry_emitter.py | ✓ | ✓ | ✓ | ✓ |
| core/trace_context.py | ✓ | ✓ | ✓ | ✓ |
| escalation/budget_alert.py | ✓ | ✓ | ✓ | ✓ |
| experiment/experiment_result.py | ✓ | ✓ | ✓ | ✓ |
| experiment/model_serving_response.py | ✓ | ✓ | ✓ | ✓ |
| gate/gate_result.py | ✓ | ✗ | ✓ | ✓ |
| identity/permission.py | ✓ | ✓ | ✓ | ✓ |
| security/security_decision.py | ✓ | ✓ | ✓ | ✓ |

**特征**: 两边都是real实现，功能基本等价，差异在实现风格（shared用plain class，integration用@dataclass）。

## 5. 关键发现

### 5.1 integration版本质量问题

| 问题 | 影响文件 | 严重程度 |
|------|---------|:---:|
| 字段重复定义（`idempotency_key`重复3次） | backpressure/pause.py, resume.py, throttle.py | HIGH |
| 空类（`class X: pass`，无字段） | external/ext_001~004.py | HIGH |
| codegen与YAML不同步 | 上述7个文件 | MEDIUM |

### 5.2 蓝图依据

| 字段 | 值 | 来源 |
|------|------|------|
| 蓝图module_id | MOD-013 (MOD-INF-016-CONTRACTS) | `docs/03_modules/_cross_layer/shared_core/contracts_blueprint.md` |
| actual_disk_path | `src/zephyr/shared/contracts/` | 蓝图frontmatter |
| codegen真源 | `cross_layer_contracts.yaml` | `architecture_model/contracts/` |
| 蓝图声明 | "所有模型 MUST 继承 pydantic.BaseModel" | 蓝图§2 |
| 蓝图声明 | "所有模型 MUST 使用 frozen=True" | 蓝图§2 |

**矛盾点**: 蓝图声明规范位置是 `shared/contracts/`，但 integration 版本是 codegen 从 YAML 真源生成的。两者实现风格不同（shared部分用plain class，integration用@dataclass）。

### 5.3 混合消费者=0

**零混合消费者**意味着没有任何文件同时 import 两个位置。这是去重的最佳条件——去重不会产生任何 import 冲突。

## 6. 规范位置裁定

### 6.1 候选方案

| 方案 | 规范位置 | 优点 | 缺点 |
|------|---------|------|------|
| A | `shared/contracts/` | 蓝图声明; 4文件real实现更完整; external有字段; 无bug | 需修复backpressure的shim指向 |
| B | `integration/shared_08/contracts/` | codegen产物; 从YAML真源生成 | 有字段重复bug; external空类; 依赖integration内部模块链 |
| C | 保留两套 | 零迁移成本 | 违反SSoT; 维护成本翻倍 |

### 6.2 裁定：方案A — shared为规范位置

**理由**:

1. **蓝图声明**: MOD-INF-016 明确 `actual_disk_path: src/zephyr/shared/contracts/`
2. **实现质量**: shared版本质量更高
   - 4文件完整real实现（enforcer/registry/timestamp/agent_identity）
   - external/ext_001~004.py 有完整字段定义（integration是空类）
   - 无字段重复bug
3. **integration版本缺陷**:
   - backpressure 3文件有字段重复bug（`idempotency_key`重复3次）
   - external 4文件是空类（codegen未生成字段）
   - 依赖integration内部模块链（contract_enforcer/contract_versions/timestamp_utils/agent_identity_impl/backpressure_types）
4. **去重零风险**: 混合消费者=0，不会产生import冲突
5. **SSoT原则**: 蓝图是架构SSoT，蓝图声明shared为规范位置

### 6.3 integration内部模块处理

integration版本依赖以下integration内部模块（需一并处理）:

| integration内部模块 | 被谁re-export | 对应shared实现 |
|-------------------|---------------|---------------|
| `zephyr.integration.shared_08.contract_enforcer` | core/enforcer.py | `zephyr.shared.contracts.core.enforcer` |
| `zephyr.integration.shared_08.contract_versions` | core/registry.py | `zephyr.shared.contracts.core.registry` |
| `zephyr.integration.shared_08.timestamp_utils` | core/timestamp.py | `zephyr.shared.contracts.core.timestamp` |
| `zephyr.integration.shared_08.agent_identity_impl` | identity/agent_identity.py | `zephyr.shared.contracts.identity.agent_identity` |
| `zephyr.integration.backpressure_types` | backpressure/*.py | `zephyr.shared.contracts.backpressure._types` |

**处理策略**: integration内部模块本身不在本次23文件范围内，但去重后这些re-export shim的指向需更新为shared位置。

## 7. 去重策略

### 7.1 总体策略

```
shared/contracts/                    → 规范位置（保留real实现）
integration/shared_08/contracts/     → 转为re-export shim指向shared
```

### 7.2 按类型分策略

| 类型 | 文件数 | 策略 |
|------|:---:|------|
| A (shared=real, int=shim) | 4 | integration版本修改import指向shared（从integration内部模块改为shared） |
| B (shared=shim, int=real) | 3 | 保留shared的shim指向_types；integration转shim指向shared |
| C (双real, shared完整) | 4 | integration转shim指向shared（shared字段更完整） |
| D (双real, 功能等价) | 12 | integration转shim指向shared |

### 7.3 shim模板（integration版本转为指向shared）

```python
# [A_module] module_id=MOD-INT_{name} | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-{XXX} | docs/03_modules/_cross_layer/shared-core/contracts_blueprint.md
# [MODULE] zephyr.integration.shared_08.contracts.{sub}.{name}
# [INVARIANTS] re-export shim only; truth source is zephyr.shared.contracts.{sub}.{name}
# [MODIFY-GUARD] truth source MUST NOT be modified here; changes go to zephyr.shared.contracts.{sub}.{name}
# [CONSUMERS] legacy imports via integration.shared_08.contracts
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError if source module missing
# [TESTS] python -c "from zephyr.integration.shared_08.contracts.{sub}.{name} import {ClassName}"
"""Re-export shim — 真源已合并至 zephyr.shared.contracts.{sub}.{name}。"""
from zephyr.shared.contracts.{sub}.{name} import *  # noqa: F401,F403
```

## 8. 子卡拆分方案（8张子卡，每组≤3文件）

### 子卡1: backpressure修复+去重（3文件，类型B）

| 字段 | 值 |
|------|------|
| 文件 | backpressure/pause.py, backpressure/resume.py, backpressure/throttle.py |
| 位置 | shared=shim→_types, integration=real(有bug) |
| 操作 | integration转shim指向shared; 保留shared的shim指向_types |
| files_in_scope | 3 |

### 子卡2: core类型A integration转shim（3文件，类型A）

| 字段 | 值 |
|------|------|
| 文件 | core/enforcer.py, core/registry.py, core/timestamp.py |
| 位置 | shared=real, integration=shim→integration内部模块 |
| 操作 | integration版本修改import指向shared |
| files_in_scope | 3 |

### 子卡3: core类型D integration转shim A（3文件，类型D）

| 字段 | 值 |
|------|------|
| 文件 | core/base_event.py, core/gate_types.py, core/runtime_plane_tag.py |
| 位置 | 双real, 功能等价 |
| 操作 | integration转shim指向shared |
| files_in_scope | 3 |

### 子卡4: core类型D integration转shim B（3文件，类型D）

| 字段 | 值 |
|------|------|
| 文件 | core/system_configuration.py, core/telemetry_emitter.py, core/trace_context.py |
| 位置 | 双real, 功能等价 |
| 操作 | integration转shim指向shared |
| files_in_scope | 3 |

### 子卡5: external类型C integration转shim（3文件，类型C）

| 字段 | 值 |
|------|------|
| 文件 | external/ext_001.py, external/ext_002.py, external/ext_003.py |
| 位置 | shared=real(有字段), integration=空类(pass) |
| 操作 | integration转shim指向shared（shared字段更完整） |
| files_in_scope | 3 |

### 子卡6: identity类型A+C integration转shim（3文件，类型A+C）

| 字段 | 值 |
|------|------|
| 文件 | external/ext_004.py, gate/gate_result.py, identity/agent_identity.py |
| 位置 | ext_004: shared=real, int=空类; gate_result: 双real; agent_identity: shared=real, int=shim |
| 操作 | integration转shim指向shared |
| files_in_scope | 3 |

### 子卡7: identity+security+escalation integration转shim（3文件，类型D）

| 字段 | 值 |
|------|------|
| 文件 | identity/permission.py, security/security_decision.py, escalation/budget_alert.py |
| 位置 | 双real, 功能等价 |
| 操作 | integration转shim指向shared |
| files_in_scope | 3 |

### 子卡8: experiment integration转shim（2文件，类型D）

| 字段 | 值 |
|------|------|
| 文件 | experiment/experiment_result.py, experiment/model_serving_response.py |
| 位置 | 双real, 功能等价 |
| 操作 | integration转shim指向shared |
| files_in_scope | 2 |

## 9. 验收标准

| # | 验收项 | 验证方法 |
|---|--------|---------|
| 1 | integration 23个文件全部转为shim | `rg -L "re-export shim" src/zephyr/integration/shared_08/contracts/{23文件}` 应返回空 |
| 2 | integration shim全部指向shared | `rg "from zephyr.shared.contracts" src/zephyr/integration/shared_08/contracts/` 应匹配23文件 |
| 3 | 无integration内部模块依赖 | `rg "from zephyr.integration.shared_08.(contract_enforcer|contract_versions|timestamp_utils|agent_identity_impl)" src/zephyr/integration/shared_08/contracts/` 应返回空 |
| 4 | 所有import仍可正常解析 | `python -c "import zephyr.integration.shared_08.contracts"` exit 0 |
| 5 | shared import仍可解析 | `python -c "from zephyr.shared.contracts.core.base_event import BaseEvent"` exit 0 |
| 6 | 无功能回归 | `python -m pytest tests/ -q -k contract` exit 0 |

## 10. 注意事项

1. 本任务是R2时序存储的前置条件——合约去重后才能进行R2-2业务Schema DDL
2. **分析任务不修改任何代码文件**，只输出分析报告
3. 子卡建好后，逐个执行去重（每个子卡改≤3个文件为re-export shim）
4. **integration版本有bug**: backpressure 3文件字段重复定义，external 4文件是空类——去重时以shared版本为准
5. **integration内部模块**（contract_enforcer等）不在本次23文件范围内，但去重后这些模块的re-export shim指向需更新
6. 每个子卡执行时MUST遵循RULE-ZERO锁协议（check→acquire→write→release）
7. **蓝图MOD-INF-016声明**: shared为规范位置，本裁定与蓝图一致
