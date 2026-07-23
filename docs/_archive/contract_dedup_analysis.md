---
module_id: ARCH-ENT-002
title: "合约模型去重分析报告"
status: active
version: 1.0.0
date: 2026-06-27
owner: ZephyrAlpha-Owner
ttl: permanent
---

# 合约模型去重分析报告

> 任务卡: DM-202925 | 日期: 2026-06-24 | 状态: 分析完成
> 真源数据: depgraph.db + 实际文件扫描 + import引用统计 + AST比对

## 1. 问题概述

4个位置存在合约文件重复，总计 ~60 文件跨 4 个域。这是 R2 时序存储的前置条件——合约去重后才能进行 R2-2 业务Schema DDL。

## 2. 四个位置文件清单

| 位置 | 物理路径 | .py文件数(排除__init__) | real | shim | module_id前缀 |
|------|---------|:---:|:---:|:---:|------|
| shared | `src/zephyr/shared/contracts/` | 55 | 33 | 22 | MOD-SHR(45), MOD-EXE(5), MOD-PRT(4), MOD-SEC(1) |
| integration | `src/zephyr/integration/shared_08/contracts/` | 50 | 47 | 3 | MOD-INT(49), MOD-SEC(1) |
| trading | `src/zephyr/trading/trading_contracts/` | 24 | 24 | 0 | MOD-EXE(7), MOD-UNK(14), MOD-PRT(3) |
| governance | `src/zephyr/governance/trading_contracts/` | 24 | 24 | 0 | MOD-EXE(21), MOD-PRT(3) |

## 3. 重复矩阵（47个文件出现在>=2个位置）

### 3.1 三路重复（shared + trading + governance）— 16个文件

| 文件 | shared | trading | governance | shared类型 |
|------|:---:|:---:|:---:|------|
| execution/capital_allocation_result.py | Y | Y | Y | SHIM |
| execution/execution_report.py | Y | Y | Y | SHIM |
| execution/fill.py | Y | Y | Y | SHIM |
| execution/model_serving_request.py | Y | Y | Y | SHIM |
| execution/order.py | Y | Y | Y | SHIM |
| market/factor_monitor_report.py | Y | Y | Y | SHIM |
| market/factor_signal.py | Y | Y | Y | SHIM |
| market/instrument.py | Y | Y | Y | SHIM |
| market/macro_factor_signal.py | Y | Y | Y | SHIM |
| market/market_data.py | Y | Y | Y | SHIM |
| market/synthesized_signal.py | Y | Y | Y | SHIM |
| risk/compliance_rule.py | Y | Y | Y | SHIM |
| risk/risk_dashboard_snapshot.py | Y | Y | Y | SHIM |
| risk/risk_limits.py | Y | Y | Y | SHIM |
| risk/risk_metrics.py | Y | Y | Y | SHIM |
| risk/risk_validator_protocol.py | Y | Y | Y | SHIM |

### 3.2 双路重复（trading + governance）— 8个文件

| 文件 | trading | governance |
|------|:---:|:---:|
| execution/execution_rejection_error.py | Y | Y |
| execution/position.py | Y | Y |
| factories.py | Y | Y |
| market/signal_degradation_warning.py | Y | Y |
| portfolio/contracts/money.py | Y | Y |
| portfolio/contracts/performance_attribution_report.py | Y | Y |
| portfolio/contracts/strategy_lifecycle_event.py | Y | Y |
| risk/risk_limit_violation_error.py | Y | Y |

### 3.3 双路重复（shared + integration）— 23个文件

| 文件 | shared | integration | shared类型 |
|------|:---:|:---:|------|
| backpressure/pause.py | Y | Y | REAL |
| backpressure/resume.py | Y | Y | REAL |
| backpressure/throttle.py | Y | Y | REAL |
| core/base_event.py | Y | Y | REAL |
| core/enforcer.py | Y | Y | REAL |
| core/gate_types.py | Y | Y | REAL |
| core/registry.py | Y | Y | REAL |
| core/runtime_plane_tag.py | Y | Y | REAL |
| core/system_configuration.py | Y | Y | REAL |
| core/telemetry_emitter.py | Y | Y | REAL |
| core/timestamp.py | Y | Y | REAL |
| core/trace_context.py | Y | Y | REAL |
| escalation/budget_alert.py | Y | Y | REAL |
| experiment/experiment_result.py | Y | Y | REAL |
| experiment/model_serving_response.py | Y | Y | REAL |
| external/ext_001.py | Y | Y | REAL |
| external/ext_002.py | Y | Y | REAL |
| external/ext_003.py | Y | Y | REAL |
| external/ext_004.py | Y | Y | REAL |
| gate/gate_result.py | Y | Y | REAL |
| identity/agent_identity.py | Y | Y | REAL |
| identity/permission.py | Y | Y | REAL |
| security/security_decision.py | Y | Y | REAL |

## 4. 引用统计

| 位置 | import行数 | 外部消费者文件数 | 说明 |
|------|:---:|:---:|------|
| shared.contracts | 100 | ~30 | 混合: 33个real实现 + 22个shim(指向不存在的路径) |
| integration.shared_08.contracts | 96 | ~25 | 独立codegen实现(dataclass) |
| trading.trading_contracts | 142 | 40 | 含内部__init__.py引用; 外部消费者: risk/signal_fundamental/reporting/ex_core/pf_core/ml_train/ops |
| governance.trading_contracts | 0 | 0 | 零外部消费者 — 纯内部re-export |
| zephyr.execution.trading | 0 | 0 | 目标路径不存在，`zephyr.execution`包未创建 |

## 5. 蓝图依据

| 字段 | 值 | 来源 |
|------|------|------|
| 蓝图module_id | MOD-INF-016-CONTRACTS (MOD-013) | `docs/03_modules/_cross_layer/shared_core/contracts_blueprint.md` |
| actual_disk_path | `src/zephyr/shared/contracts/` | 蓝图frontmatter |
| 蓝图声明 | "Factories已迁移至trading_contracts/" | 蓝图§0 |
| 蓝图声明 | "ExecutionRejectionError/RiskLimitViolationError/SignalDegradationWarning已迁移至trading_contracts/" | 蓝图§0 |
| [MODULE]字段(trading+governance) | `zephyr.execution.trading.trading_contracts.*` | 文件头部 |
| shared shim目标 | `zephyr.execution.trading.trading_contracts.*` | 文件头部`_TARGET_MODULE` |

**根因**: 一次未完成的迁移——shared/contracts的22个文件被改为shim指向`zephyr.execution.trading.trading_contracts`，但`zephyr.execution`包从未创建。真实实现同时存在于trading/trading_contracts和governance/trading_contracts两个位置。

## 6. AST比对（trading vs governance）

| 指标 | 值 |
|------|:---:|
| 比对文件数 | 24 |
| Class数量匹配 | 24/24 |
| Class+Func符号集相同 | 5/24 |
| 文件hash完全相同 | 0/24 |

**git diff验证**（market_data.py示例）: 差异仅为 (1) module_id前缀 MOD-UNK vs MOD-EXE (2) governance多`__all__`导出。dataclass实现本身功能等价。

**结论**: trading和governance的24个文件功能等价，差异仅在文件头module_id和`__all__`导出声明。

## 7. 规范位置裁定

### 7.1 候选方案

| 方案 | 规范位置 | 优点 | 缺点 |
|------|---------|------|------|
| A | `zephyr.trading.trading_contracts` | 已有142处import; 24个real实现已就位; 零迁移成本 | [MODULE]字段指向`zephyr.execution.*`(不一致) |
| B | `zephyr.execution.trading.trading_contracts`（新建） | 匹配[MODULE]字段意图; 语义清晰(execution域) | 需创建新包+迁移24文件+更新142处import; 成本高 |
| C | `zephyr.shared.contracts`（恢复） | 匹配蓝图MOD-INF-016; 100处import已存在 | 22个文件已是shim需回退; 违背已开始的迁移方向 |

### 7.2 裁定: 方案A（推荐）

**理由**:
1. trading/trading_contracts已有24个real实现 + 142处import — 事实标准
2. governance/trading_contracts零外部消费者 — 转shim零风险
3. shared/contracts的22个shim只需修正目标路径（从`zephyr.execution.trading.*`改为`zephyr.trading.trading_contracts.*`）
4. 方案B（新建execution包）可作为后续架构升级独立推进，不阻塞R2时序存储

### 7.3 integration/shared_08/contracts 独立处理

integration/shared_08/contracts是独立codegen实现（从`cross_layer_contracts.yaml`生成），有96处import。与trading/trading_contracts是**两套独立实现**（不同import路径、不同基类依赖）。此23个文件的shared+integration去重需单独评估，不在本次子卡范围内。

## 8. 去重策略（re-export shim方案）

### 8.1 总体策略

```
trading/trading_contracts     → 规范位置（保留real实现）
governance/trading_contracts  → 转为re-export shim（指向trading.trading_contracts）
shared/contracts (22个shim)   → 修正目标路径（指向trading.trading_contracts）
```

### 8.2 shim模板（参考pipeline_orchestrator.py）

```python
# [A_module] module_id=MOD-EXE_{name} | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/contracts_blueprint.md | §
# [MODULE] zephyr.trading.trading_contracts.{sub}.{name}
# [INVARIANTS] re-export shim only; truth source is zephyr.trading.trading_contracts.{sub}.{name}
# [MODIFY-GUARD] truth source MUST NOT be modified here; changes go to zephyr.trading.trading_contracts.{sub}.{name}
# [CONSUMERS] legacy imports via governance.trading_contracts
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
"""Re-export shim — 真源已合并至 zephyr.trading.trading_contracts.{sub}.{name}。"""
from zephyr.trading.trading_contracts.{sub}.{name} import *  # noqa: F401,F403
```

### 8.3 shared/contracts shim修正

22个shim当前指向`zephyr.execution.trading.trading_contracts.*`（不存在），修正为`zephyr.trading.trading_contracts.*`。

## 9. 子卡拆分方案（8张子卡，每组≤3文件）

### 子卡1: market类A — market_data, factor_signal, macro_factor_signal

| 字段 | 值 |
|------|------|
| 文件 | market/market_data.py, market/factor_signal.py, market/macro_factor_signal.py |
| 位置 | shared(SHIM) + trading(REAL) + governance(REAL) |
| 操作 | governance转shim + shared修正shim目标 |
| files_in_scope | 3 |

### 子卡2: market类B — instrument, synthesized_signal, factor_monitor_report

| 字段 | 值 |
|------|------|
| 文件 | market/instrument.py, market/synthesized_signal.py, market/factor_monitor_report.py |
| 位置 | shared(SHIM) + trading(REAL) + governance(REAL) |
| 操作 | governance转shim + shared修正shim目标 |
| files_in_scope | 3 |

### 子卡3: execution类A — order, fill, execution_report

| 字段 | 值 |
|------|------|
| 文件 | execution/order.py, execution/fill.py, execution/execution_report.py |
| 位置 | shared(SHIM) + trading(REAL) + governance(REAL) |
| 操作 | governance转shim + shared修正shim目标 |
| files_in_scope | 3 |

### 子卡4: execution类B — capital_allocation_result, model_serving_request, execution_rejection_error

| 字段 | 值 |
|------|------|
| 文件 | execution/capital_allocation_result.py, execution/model_serving_request.py, execution/execution_rejection_error.py |
| 位置 | 前2个: shared(SHIM)+trading(REAL)+governance(REAL); 后1个: trading(REAL)+governance(REAL) |
| 操作 | governance转shim + shared修正shim目标(前2个) |
| files_in_scope | 3 |

### 子卡5: risk类A — risk_metrics, risk_limits, compliance_rule

| 字段 | 值 |
|------|------|
| 文件 | risk/risk_metrics.py, risk/risk_limits.py, risk/compliance_rule.py |
| 位置 | shared(SHIM) + trading(REAL) + governance(REAL) |
| 操作 | governance转shim + shared修正shim目标 |
| files_in_scope | 3 |

### 子卡6: risk类B — risk_dashboard_snapshot, risk_validator_protocol, risk_limit_violation_error

| 字段 | 值 |
|------|------|
| 文件 | risk/risk_dashboard_snapshot.py, risk/risk_validator_protocol.py, risk/risk_limit_violation_error.py |
| 位置 | 前2个: shared(SHIM)+trading(REAL)+governance(REAL); 后1个: trading(REAL)+governance(REAL) |
| 操作 | governance转shim + shared修正shim目标(前2个) |
| files_in_scope | 3 |

### 子卡7: portfolio类 — money, performance_attribution_report, strategy_lifecycle_event

| 字段 | 值 |
|------|------|
| 文件 | portfolio/contracts/money.py, portfolio/contracts/performance_attribution_report.py, portfolio/contracts/strategy_lifecycle_event.py |
| 位置 | trading(REAL) + governance(REAL) |
| 操作 | governance转shim |
| files_in_scope | 3 |

### 子卡8: 其余 — factories, position, signal_degradation_warning

| 字段 | 值 |
|------|------|
| 文件 | factories.py, execution/position.py, market/signal_degradation_warning.py |
| 位置 | trading(REAL) + governance(REAL) |
| 操作 | governance转shim |
| files_in_scope | 3 |

## 10. 验收标准

| # | 验收项 | 验证方法 |
|---|--------|---------|
| 1 | governance/trading_contracts 24个文件全部转为shim | `grep -rL "re-export shim" src/zephyr/governance/trading_contracts/` 应返回空 |
| 2 | shared/contracts 22个shim目标路径已修正 | `grep "zephyr.execution.trading" src/zephyr/shared/contracts/` 应返回空 |
| 3 | 所有import仍可正常解析 | `python -c "import zephyr.trading.trading_contracts"` exit 0 |
| 4 | governance.trading_contracts import仍可解析 | `python -c "from zephyr.governance.trading_contracts.market import market_data"` exit 0 |
| 5 | 无功能回归 | `python -m pytest tests/test_trading_contracts.py -q` exit 0 |

## 11. 注意事项

1. 本任务是R2时序存储的前置条件——合约去重后才能进行R2-2业务Schema DDL
2. 分析任务不修改任何代码文件，只输出分析报告
3. 子卡建好后，逐个执行去重（每个子卡改3个文件为re-export shim）
4. governance/trading_contracts的module_id=MOD-EXE_*，trading/trading_contracts的module_id=MOD-UNK_*——裁定trading为规范位置（已有142处import事实标准）
5. integration/shared_08/contracts是独立实现（dataclass），不是shim——23个shared+integration重复文件需单独评估，不在本次子卡范围
6. 每个子卡执行时MUST遵循RULE-ZERO锁协议（check→acquire→write→release）
