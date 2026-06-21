---
module_id: KE-520------experimental-002
title: 8.1 数据分级（experimental 基线）
category: documentation
---

# 8.1 数据分级（experimental 基线）

8.1 数据分级（experimental 基线）

| 级别 | 数据类型 | 加密策略 |
|------|---------|---------|
| **L4 最高敏感** | API Key / 交易凭证 / 账户数据 | 传输 TLS 1.3；静止 OS Keychain 或加密卷 |
| **L3 高敏感** | 策略代码 / 参数 / 持仓 | 传输 HTTPS；静止 OS 权限 + .gitignore |
| **L2 中敏感** | 历史行情 / 因子值 | 传输 HTTPS；静止 文件系统权限 |
| **L1 低敏感** | 公开文档 / ADR / README | 无加密要求 |
