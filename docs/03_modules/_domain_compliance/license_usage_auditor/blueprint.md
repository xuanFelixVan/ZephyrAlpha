---
module_id: MOD-CMP-008
title: "数据源授权合规审计器蓝图 — 授权条款登记/使用审计/违规处置"
doc_type: blueprint
status: Active
version: "0.1.11"
ttl: permanent
design_maturity: production
layer: L1_foundation
layer_name: compliance
functional_domain: compliance
responsibility_domain: 
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-15"
last_updated: "2026-08-15"
priority: P1
blueprint_level: module
---

# MOD-CMP-008 | License Usage Auditor 数据源授权合规审计器

> **域**: D_COMPLIANCE | **优先级**: P1 | **safety**: H | **ai_autonomy**: ai_modifiable
> **状态**: design | **版本**: 0.1.0 | **SSoT**: depgraph MOD-CMP-008 (node 9651493)

## 1. 模块定位

信息合规（BM-BUY-09）落地为**数据源授权条款合规**：登记（62 号 data_asset_registry compliance 段字段语义真源=43 号 §5.3）+ 使用审计（实际用途 ∈ permitted_use）+ 违规三级处置。内幕隔离墙/通信监控不建设（个人自有资金单人决策，§5.2 裁定）。

依据: `43_compliance_discipline.md` §5

## 2. 不变量 (INVARIANTS)

- 缺 compliance 段的源默认**仅 backtest 用途**（最保守假设），直至补登
- 授权过期 = L2 立即切断数据流（Fail-Closed）+ 告警
- 违规分级不降级：L1 超范围 / L2 过期 / L3 再分发
- legacy 形态（compliance 为自由文本）视同缺段

## 3. 错误契约 (ERROR_CONTRACT)

| 错误类 | error_code | 触发条件 |
|--------|-----------|---------|
| LicenseAuditError | ZA-CMP-0003 | 源未登记 / 登记表不可读（Fail-Closed） |

## 4. 依赖关系

| 方向 | 模块 | 契约/事件 | 说明 |
|------|------|---------|------|
| 依赖 | catalogs/data_asset_registry.yaml | REG-DATAFLOW-001 sources | 登记容器真源（62 号），本模块定 compliance 段字段语义 |
| 依赖 | zephyr.compliance.compliance_log | ComplianceLogger | 审计报告落 compliance_log |
| 消费 | 62 号治理流程 | audit(source_id, actual_uses) | 每 review_cycle_days 定期 + 新增数据消费模块触发 |

## 5. 核心逻辑

```
compliance 段（§5.3）：vendor/license_type/permitted_use/redistribution/
  derived_data_policy/expiry/terms_ref/registered_at/review_cycle_days(默认90)
audit(): L2 过期最优先 → L3 再分发 → L1 超范围（未知用途/未许可用途）
review_due(): registered_at + review_cycle_days ≤ today → 到期复核；缺段 → True
```

## 6. 接口

```python
LicenseUsageAuditor(registry_path=None, logger=None)
.load_source(source_id) -> SourceLicense
.audit(source_id, actual_uses: set[str], *, today=None) -> LicenseAuditReport
.review_due(source_id, *, today=None) -> bool
```

## 7. 设计决策

| 决策 | 理由 |
|------|------|
| 审计器与登记容器分离 | 62 号 REG-DATAFLOW-001 是容器与治理流程真源；本模块定字段语义与处置动作（43 号 §5.4） |
| 缺段保守默认 backtest-only | §5.3 降级裁定：授权不明的数据只能回测，不得上实盘 |
| 用途词表硬编码 5 值 | §5.3 permitted_use 枚举（backtest/live_trading/display/ml_training/redistribution），DDL-as-Code 例外 |

## 8. 测试计划

tests/compliance/test_license_usage_auditor.py — 11 用例：缺段保守/超范围 L1/过期 L2/再分发 L3/未知用途/未登记/表缺失/复核周期/落日志。

---

## 9. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status=generated）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 9.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| — | — | 本模块尚无已实现代码 |

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


