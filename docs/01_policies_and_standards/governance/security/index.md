---
module_id: GOV-SEC-000
title: "安全治理目录索引"
doc_type: index
status: active
version: "1.0.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
ai_autonomy: human_gated
created_by: human_plus_agent
date: "2026-05-01"
valid_from: "2026-05-01"
ttl: permanent
summary: "governance/security/ 目录的导航索引。声明本目录的责任范围、文件清单及每文件的核心职责。新 AI session 进入本目录时，应首先读取本文件以建立全局认知。"
tags: [index, security, governance, navigation]
depends_on:
  - target: PS-STD-001
    at: "§5.8"
    why: "metadata-registry.md 定义 GOV-SEC 模块 ID 的分配规则"
---

# 安全治理目录索引

> **module_id**: GOV-SEC-000 | **version**: 1.0.0 | **status**: active

---

## §1 本目录的责任

`governance/security/` 是 ZephyrAlpha 的**安全治理中心**。这里管的是"保护系统免遭未授权访问、泄露和破坏"相关的全局安全规则。

**正向责任**（本目录管的事）：
1. 密钥和凭证的存储、轮换、撤销规则（禁止明文存储/日志/硬编码）
2. 访问控制——角色定义、权限矩阵、最小权限原则、审批流程
3. 安全事件响应——事件分级、响应步骤、通知机制、事后复盘

**负向责任**（本目录不管的事，去对应目录找）：
- 安全事件的操作步骤手册 → `operational/security/`
- AI 代理的自治权限定义 → `_registry/catalogs/ai-autonomy-authority-registry.md`（已从 governance/ai/ 迁出）
- 业务代码中的安全实现 → `src/zephyr/`
- 审计追踪和合规检查 → `governance/compliance/`

---

## §2 文件清单

| 文件 | module_id | 一句话职责 |
|------|-----------|-----------|
| [secret-management-policy.md](secret-management-policy.md) | GOV-SEC-001 | 定义密钥/凭证/Token 的存储、轮换、撤销全流程规则 |
| [access-control-policy.md](access-control-policy.md) | GOV-SEC-002 | 定义谁能访问什么——角色、权限矩阵、最小权限、审批流程 |
| [security-incident-response-policy.md](security-incident-response-policy.md) | GOV-SEC-003 | 安全事件分级、响应步骤、通知、复盘——P0 密钥泄露/P1 未授权/P2 高危操作（SIR-001~004） |

---

## §3 依赖关系速览

```
PS-STD-003 (行为边界)           ← 所有 SEC 文件共用：ABS-29~32 密钥禁止行为
    │
GOV-SEC-001 (secret-management) ← 被 GOV-SEC-003 引用：密钥泄露触发P0安全事件
    │
GOV-SEC-002 (access-control)    ← 被 GOV-SEC-003 引用：未授权访问触发安全事件
    │                              被 GOV-CMP-002 引用：审计日志访问权限
    │
GOV-AI-001 (autonomy-registry)  ← 被 GOV-SEC-002 引用：AI代理权限注册
    │                              被 GOV-SEC-003 引用：AI越权触发安全事件
    │
GOV-SEC-003 (incident-playbook) ← 汇总点：引用 SEC-001 + SEC-002 + AI-001 + PS-STD-003
```

跨域引用：
- `GOV-CMP-002 (audit-trail)` → `GOV-SEC-002 §2~§4`：审计日志访问受限需引用角色定义和权限矩阵

---

## §4 对 AI 的使用指引

每个新 AI session 进入本目录后，应按以下顺序建立认知：

1. **先读本文件**（你正在读的这个）——了解全貌
2. **再读 secret-management-policy.md**——理解"密钥怎么管"（SEC-001~005）
3. **再读 access-control-policy.md**——理解"谁能访问什么"（ACS-001~005）
4. **最后读 security-incident-response-policy.md**——理解"出事了怎么办"（SIR-001~004）

所有文件均标记 `ai_autonomy: human_gated` —— AI 可以读取和应用这些规则，但**不得单方面修改**。任何修改必须由 Owner 审批。

**安全事件分级速查**：
- P0（灾难）：密钥泄露 / 数据库对外暴露 / Kill Switch 触发
- P1（严重）：Azure Service Principal 泄露 / 第三方 API Key 泄露
- P2（重要）：写操作未留痕 / 高危命令未确认
- P3（一般）：非敏感数据泄露 / 读取类超额操作

---

## §5 已知技术债务

以下事项已明确识别但有意留置，待条件满足时处理。**AI 读取本域文件时应知晓这些待办项，但不得在未获 Owner 审批的情况下单方面补全。**

| # | 位置 | 事项 | 现状 | 触发条件 |
|---|------|------|------|---------|
| TD-SEC-01 | [secret-management-policy.md](secret-management-policy.md) SEC-004 | 轮换周期（90/180/365天）需经专业机构全面对标验证后写入正式依据 | 已标注 ⚠️待补充，附 NIST SP 800-63B / PCI DSS / AWS IAM 行业参考 | 全面对标 pass 启动时——执行：读取三个标准原文 → 确认适用条款 → 写入 SEC-004 依据列 → 移除 ⚠️标记 |

> **提醒**：本表为 AI 上下文提示——AI 读取本文件后即知晓此留置项的存在和触发条件，无需 Owner 记忆。当触发条件满足时（如下一阶段全面对标），AI 应主动将该事项纳入任务清单。
