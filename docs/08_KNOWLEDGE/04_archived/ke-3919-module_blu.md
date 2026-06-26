---
module_id: KE-3767
title: 1.2 核心职能（一句话 + 五支柱）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 1.2 核心职能（一句话 + 五支柱）

1.2 核心职能（一句话 + 五支柱）

**Audit Trail 是系统的黑匣子 + 免疫系统 + 公证处**——每个 AI 动作都有密码学完整性保证的审计记录。出了问题可以回溯到任意时刻的任意操作，找到根因。异常行为自动检测并告警。蓝图漂移实时对账。闭环反馈驱动规则演进。Agent 级签名保证不可否认性。

| 支柱 | 职责 | 对标 |
|------|------|------|
| **记录（Record）** | 不可变 append-only 审计日志——JSONL 唯一真源 | Goldman SecDB immutable log |
| **验证（Verify）** | 密码学完整性——哈希链 + HMAC 签名 + Merkle 树聚合 | Microsoft AGT Merkle-chain |
| **归因（Attribute）** | Agent 级不可否认性——Ed25519 Agent 签名 + 委托链验证 | Microsoft AGT Ed25519 / IATP |
| **检测（Detect）** | 异常行为签名 + 蓝图漂移检测 + 权限违规告警 + 间接操作 + 供应链风险 | ISACA 2025 / OWASP ASI-10 / NIST 2026 |
| **进化（Evolve）** | 三角闭环反馈——审计数据回写 Policy 驱动规则演进 + 反馈自审计 | Netflix 混沌反馈 / KBG-0010 D2-B |
