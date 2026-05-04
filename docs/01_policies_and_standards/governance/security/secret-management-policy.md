---
module_id: GOV-SEC-001
title: 密钥管理策略
doc_type: policy
status: draft
version: "0.2.0"
layer: l01_infrastructure
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-01"
valid_from: "2026-05-01"
ttl: permanent
summary: "定义 ZephyrAlpha 系统中所有密钥、凭证、Token 的存储、轮换、撤销规则。"
tags: [security, governance, secret]
rule_form: declarative
scope: global
stability: evolving
verifiability: manual
depends_on:
  - {target: PS-STD-003, at: "§3~§4", why: "密钥管理行为边界——ABS-29~ABS-32禁止明文存储、日志记录、硬编码密钥"}
ai_autonomy: human_gated
---

# 密钥管理策略

> module_id: GOV-SEC-001 | version: 0.2.0 | status: draft | layer: L1

---

## 1. 目的与范围

本策略定义 ZephyrAlpha 量化交易系统中所有密钥、凭证、Token 的管理规则。适用于：

- API 密钥（交易所、数据源、第三方服务）
- 数据库凭证
- SSH 密钥
- JWT/Session Token
- 加密密钥

不适用于：人类用户的登录密码（由访问控制策略 [GOV-SEC-002](../01_policies_and_standards/governance/security/access-control-policy.md) 管理）。

---

## 2. 规则

### SEC-001：禁止明文存储密钥

| 编号 | 规则 | 违反后果 |
|------|------|---------|
| SEC-001 | 所有密钥、凭证、Token 禁止以明文形式存储在代码、配置文件、文档或日志中 | 立即轮换泄露的密钥；事件复盘；标记为 P0 安全事件 |

**明文存储的定义**：
- 硬编码在 Python/JSON/YAML 文件中
- 写入 .md 文档
- 输出到日志文件
- 提交到 git 仓库

### SEC-002：密钥必须通过环境变量或密钥管理服务注入

| 编号 | 规则 | 违反后果 |
|------|------|---------|
| SEC-002 | 所有密钥必须通过环境变量（`.env`）或密钥管理服务（如 HashiCorp Vault、AWS Secrets Manager）注入，不得在代码中直接引用 | 代码审查不通过；CI 构建失败 |

**注入方式优先级**：

| 优先级 | 方式 | 适用场景 |
|:------:|------|---------|
| 1 | 密钥管理服务 | 生产环境 |
| 2 | 环境变量（`.env` 文件） | 开发环境 |
| 3 | 系统环境变量 | CI/CD 环境 |

### SEC-003：`.env` 文件必须在 `.gitignore` 中

| 编号 | 规则 | 违反后果 |
|------|------|---------|
| SEC-003 | `.env` 文件必须在 `.gitignore` 中排除，禁止提交到版本控制 | 立即从 git 历史中清除；轮换所有泄露密钥 |

### SEC-004：密钥轮换周期

| 条件 | 规则 | 违反后果 |
|------|------|---------|
| 生产环境 API 密钥 | 每 90 天轮换一次 | 安全审计不通过 |
| 数据库凭证 | 每 180 天轮换一次 | 安全审计不通过 |
| 开发环境密钥 | 每 365 天轮换一次 | 提醒但不阻塞 |
| 密钥疑似泄露 | 立即轮换，不受周期限制 | 不轮换视为 P0 事件 |

> ⚠️ **待补充**：轮换周期 90/180/365 天为工程经验值。行业参考：NIST SP 800-63B 推荐 ≤ 180 天 / PCI DSS 要求 ≤ 90 天 / AWS IAM 最佳实践 90 天。待后续全面对标时验证并写入依据。

### SEC-005：密钥撤销

| 条件 | 规则 | 违反后果 |
|------|------|---------|
| 人员离职 | 24小时内撤销其所有密钥访问权限 | 未撤销视为 P1 事件 |
| 服务下线 | 7天内撤销该服务的所有密钥 | 未撤销视为 P2 事件 |
| 密钥泄露确认 | 立即撤销 | 不撤销视为 P0 事件 |

### SEC-006：密钥强度标准

| 条件 | 规则 | 违反后果 |
|------|------|---------|
| API 密钥 / Access Token | 长度 ≥ 256 bit（32 字节），使用 CSPRNG（密码学安全伪随机数生成器）生成 | 密钥不合规；阻断使用；需重新生成 |
| 数据库密码 | 长度 ≥ 16 字符，含大写字母 + 小写字母 + 数字 + 特殊字符 | 密码不合规 |
| JWT 签名密钥 | RSA ≥ 2048 bit 或 HMAC-SHA256（对称密钥 ≥ 256 bit） | 签名强度不足 |
| 加密密钥 | AES-256-GCM 或等效算法 | 加密强度不足 |

---

## 3. 密钥泄露响应

当密钥泄露被确认时，按以下顺序执行：

1. **立即撤销**泄露的密钥
2. **生成新密钥**并注入环境
3. **搜索**泄露密钥出现过的所有文件，确认无残留
4. **通知**所有使用该密钥的服务更新配置（含 [GOV-SEC-002](../01_policies_and_standards/governance/security/access-control-policy.md) 管理的权限范围）
5. **记录**泄露事件（时间、范围、原因）
6. **复盘**并在 7 天内提交改进方案（P0 复盘标准见 [GOV-SEC-003](../01_policies_and_standards/governance/security/security-incident-response-policy.md)）

---

## 4. 验证方式

| 规则 | 验证方式 | 频率 |
|------|---------|------|
| SEC-001 | 扫描代码库和配置文件中是否存在明文密钥 | 每次提交（pre-commit） |
| SEC-002 | 检查环境变量中是否包含硬编码密钥 | 每次部署 |
| SEC-003 | 检查密钥管理服务的审计日志 | 每周 |
| SEC-004 | 检查密钥创建时间与当前时间差值 | 每周 |
| SEC-005 | 检查离职人员的密钥是否仍活跃 | 每月 |
| SEC-006 | 检查活跃密钥的算法和长度是否满足强度标准 | 每月 |

---

## 5. 例外

| 例外条件 | 审批者 | 说明 |
|---------|--------|------|
| 第三方服务不支持密钥轮换 | 安全负责人 | 需记录替代缓解措施 |
| 开发环境临时测试密钥 | 开发者自行管理 | 必须在 24 小时内删除 |

---

## 6. 修订记录

| 日期 | 版本 | 修改内容 |
|------|------|---------|
| 2026-05-01 | 0.2.0 | #17 审批修复。(1) ABS/COND → SEC-（SEC-001~SEC-006）。(2) SEC-004 轮换周期补充行业参考。(3) SEC-006 新增密钥强度标准——API密钥≥256bit/CSPRNG，数据库密码≥16字符，JWT RSA≥2048bit或HMAC-SHA256，加密AES-256-GCM。(4) §4 验证表：补齐SEC-006验证行（每月检查密钥算法/长度）。(5) `depends_on: PS-STD-003, ai_autonomy: human_gated`。(6) `date` → 2026-05-01。 |
| 2026-04-30 | 0.1.0 | 初始版本 |
