---
classification: confidential
date: '2026-05-02'
doc_type: index
generated: '2026-05-02'
layer: l00_data_source
merged_from: README.md + index.md
module_id: DOM-L00-000
status: active
title: L00 数据源层域层入口
---

# L00 — 数据源层（Data Source）

> 负责所有外部数据源的连接、认证、数据接入和格式标准化。本域是 ZephyrAlpha 的数据入口——所有下游域层的原始数据均经由此层流入。

## 责任声明（Single Responsibility）

本目录只存放：**L00 数据接入层 — 数据源连接/清洗规则/Connector 治理与操作**。

## 管什么（In Scope）

- 外部数据源连接管理（行情 API、交易 API、另类数据）
- 连接认证与安全（密钥轮换、IP 白名单、超时与断线重连）
- 数据格式标准化（将各异构数据源统一为内部 Schema）

## 不管什么（Out of Scope）

- 数据质量校验 → `../../governance/data/data-quality-policy.md`
- 数据存储与保留策略 → `../../governance/data/data-retention-policy.md`
- 数据血缘追踪 → `../../governance/data/data-lineage-policy.md`

## 依赖关系

| 方向 | 域层 | 关系 | 传输内容 |
|------|------|------|---------|
| 上游 | 外部数据供应商 | 输入 | 行情快照、逐笔成交、另类数据 |
| 下游 | L02 因子层 | 输出 | 标准化行情/交易数据 |
| 下游 | L04 风控层 | 输出 | 持仓/保证金/账户数据 |
| 下游 | L07 盘后分析 | 输出 | 交易日志/成交记录 |

## 本域文件

| 文件 | 类型 | 说明 |
|------|------|------|
| [governance/data-source-connection-policy.md](governance/data-source-connection-policy.md) | 治理规则 | 数据源连接必须满足的认证、超时、断线重连与准入条件 |
| [operational/connector-onboarding-runbook.md](operational/connector-onboarding-runbook.md) | 操作手册 | 接入新数据源的完整操作步骤、验证清单与回滚方案 |

## 引用的跨域规则

- [secret-management-policy.md](../../governance/security/secret-management-policy.md) — API 密钥管理
- [audit-trail-policy.md](../../governance/compliance/audit-trail-policy.md) — 审计追踪


## 排除规则（不应放入本目录的内容）

- ❌ 全局规则 → `01_policies_and_standards/governance/`

## 父级目录

- 父级：[domains](../../domains/index.md)
