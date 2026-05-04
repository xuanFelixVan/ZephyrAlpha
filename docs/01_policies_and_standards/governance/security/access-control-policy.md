---
module_id: GOV-SEC-002
title: 访问控制策略
doc_type: policy
status: draft
version: "0.3.0"
layer: l01_infrastructure
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-04"
valid_from: "2026-05-01"
ttl: permanent
summary: "定义 ZephyrAlpha 系统中谁能访问什么资源的规则——角色定义、权限矩阵、最小权限原则、审批流程。"
tags: [security, governance, access-control]
rule_form: declarative
scope: global
stability: evolving
verifiability: manual
depends_on:
  - {target: PS-STD-001, at: "§2.5", why: "frontmatter字段唯一真源——策略文件的doc_type/rule_form一致性约束"}
ai_autonomy: human_gated
---

# 访问控制策略

> module_id: GOV-SEC-002 | version: 0.3.0 | status: draft | layer: L1

---

## 1. 目的与范围

本策略定义 ZephyrAlpha 系统中所有资源的访问控制规则。适用于：

- 代码仓库访问
- 服务器/容器访问
- 数据库访问
- API 接口访问
- 文档访问

---

## 2. 角色定义

| 角色 | 说明 | 典型权限 |
|------|------|---------|
| Owner | 项目所有者 | 全部权限 |
| Developer | 开发者 | 代码读写、测试执行、日志查看 |
| Operator | 运维人员 | 部署、监控、日志查看、配置修改 |
| Auditor | 审计人员 | 只读访问所有日志和配置 |
| AI-Agent | AI 代理 | 按任务卡授权的有限权限 |

---

## 3. 规则

### ACS-001：最小权限原则

| 编号 | 规则 | 违反后果 |
|------|------|---------|
| ACS-001 | 每个角色/用户/AI 只授予完成其任务所需的最小权限集 | 立即收回多余权限；安全审计 |

### ACS-002：禁止共享账号

| 编号 | 规则 | 违反后果 |
|------|------|---------|
| ACS-002 | 每个人/AI 必须使用独立账号，禁止共享凭证 | 冻结共享账号；重新分配 |

### ACS-003：AI 代理权限必须受控

| 编号 | 规则 | 违反后果 |
|------|------|---------|
| ACS-003 | AI 代理的权限必须在 [GOV-AI-001](../01_policies_and_standards/_registry/catalogs/ai-autonomy-authority-registry.md) 中明确注册，未注册的权限默认禁止 | AI 操作被拒绝；记录越权尝试 |

### ACS-004：权限审批流程

| 条件 | 规则 | 违反后果 |
|------|------|---------|
| 新增权限 | 必须由 Owner 审批，并记录审批理由 | 权限不生效 |
| 临时权限 | 必须设定过期时间，最长 7 天 | 过期后自动收回 |
| 权限变更 | 必须在 24 小时内更新权限矩阵 | 审计不通过 |

### ACS-005：权限周期性审查

| 编号 | 规则 | 违反后果 |
|------|------|---------|
| ACS-005 | 所有活跃权限每个季度必须复审一次，确认权限与当前职责匹配。不再需要的权限须在复审后 7 天内收回。复审结果记录于 `docs/09_audit/access-reviews/YYYY-MM.md` | 审计不通过 |

---

## 4. 权限矩阵

| 资源 | Owner | Developer | Operator | Auditor | AI-Agent |
|------|:-----:|:---------:|:--------:|:-------:|:--------:|
| 代码仓库 | 读写 | 读写 | 只读 | 只读 | 按任务卡 |
| 生产数据库 | 读写 | 只读 | 读写 | 只读 | 禁止 |
| 测试数据库 | 读写 | 读写 | 读写 | 只读 | 按任务卡 |
| 服务器 SSH | 允许 | 禁止 | 允许 | 禁止 | 禁止 |
| CI/CD 管线 | 读写 | 只读 | 读写 | 只读 | 禁止 |
| 安全日志 | 读写 | 只读 | 只读 | 只读 | 禁止 |
| 密钥管理 | 读写 | 禁止 | 只读 | 禁止 | 禁止 |

---

## 5. 验证方式

| 规则 | 验证方式 | 频率 |
|------|---------|------|
| ACS-001 | 检查是否有未经授权的访问记录 | 每次异常访问 |
| ACS-002 | 检查新用户是否仅分配了最小必要权限 | 每次分配 |
| ACS-003 | 检查 AI 代理权限是否在 GOV-AI-001 中注册 | 每次 AI 任务启动 |
| ACS-004 | 检查权限变更记录是否包含理由和期限 | 每次变更 |
| ACS-005 | 检查季度复审记录是否完成、过期权限是否已回收 | 每季度 |

---

## 6. 修订记录

| 日期 | 版本 | 修改内容 |
|------|------|---------|
| 2026-05-04 | 0.3.0 | 审计修复。ACS-005 审查记录路径更新：`docs/19_development_workspace/` → `docs/09_audit/`（对齐 directory-structure-standard.md v3.3.0——19_development_workspace 已删除）。 |
| 2026-04-30 | 0.1.0 | 初始版本 |
