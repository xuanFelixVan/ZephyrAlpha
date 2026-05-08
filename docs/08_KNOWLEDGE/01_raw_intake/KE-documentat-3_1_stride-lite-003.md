---
module_id: KE-documentat-3_1_stride-lite-003
title: 3.1 STRIDE-Lite 威胁分析
category: documentation
---

# 3.1 STRIDE-Lite 威胁分析

3.1 STRIDE-Lite 威胁分析

针对单人 AI 协作开发场景，使用 STRIDE 精简版（Spoofing / Tampering / Repudiation / Information Disclosure / DoS / Elevation）：

| 威胁类别 | 代表威胁 | 影响层 | 严重度 | 缓解措施 | 所在域 |
|---------|---------|-------|:------:|---------|-------|
| **T1 Spoofing** | LLM Provider 中间人攻击 / Broker 伪装响应 | D-EXT | 🔴 P0 | HTTPS + API Key Fingerprint 校验 | D-EXT |
| **T2 Tampering** | 数据源注入错误行情污染因子 | L00→L02 | 🔴 P0 | L00 ACL 质量门禁 + 数据签名验证 | D-EXT→D-INT |
| **T3 Repudiation** | AI 决策"不是我说的" / 无法追溯改动 | L08, L10 | 🟡 P1 | Session Log + Handoff Log (§9) | D-MGMT |
| **T4 Info Disclosure** | `.env` 泄漏 / API Key 误写 git | D-SECRET | 🔴 P0 | git-secrets + trufflehog + LSG Output Filter | D-SECRET |
| **T5 DoS** | LLM API 限流 / 连接池耗尽 | D-AI | 🟡 P1 | 限流 + 熔断 + 降级（规则基）| D-AI |
| **T6 Elevation** | Agent 越权写系统文件 / 逃逸沙箱 | D-AGT | 🔴 P0 | Windows ACL 只读挂载 + 白名单 | D-AGT |
