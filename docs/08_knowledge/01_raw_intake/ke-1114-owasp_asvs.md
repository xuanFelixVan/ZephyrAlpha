---
module_id: KE-1029
title: 8.1 OWASP ASVS 对标
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# 8.1 OWASP ASVS 对标

8.1 OWASP ASVS 对标

| ASVS 要求 | 本协议对应 | 覆盖 |
|-----------|-----------|------|
| V1 架构安全 | D5 架构一致性 + ARG 门禁 | ✅ |
| V2 认证 | D6 安全红线 | ✅ |
| V3 会话 | D12 AI 幻觉（Session 预算）| ✅ |
| V4 访问控制 | D5 AI 自治权限 ABS-05~10 | ✅ |
| V5 输入验证 | D6 shell=True/危险命令 | ✅ |
| V7 错误处理 | D7 静默降级 COND-44~15 | ✅ |
| V8 数据保护 | D6 日志敏感词 | ✅ |
| V10 恶意代码 | D6 全部 9 个 P0 安全脚本 | ✅ |
| V13 配置 | D1 配置完整性（11 层纵深）+ pre-commit | ✅ |
