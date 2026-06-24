---
module_id: KE-3965
title: 2. 27层清单
category: module_blueprint
---

# 2. 27层清单

2. 27层清单

| Layer | 名称 | 类型 | 说明 |
|:---:|------|------|------|
| L1 | 基础阈值检查 | HARD | 硬阈值违反→直接 BLOCK |
| L2 | 频率限制 | SOFT | 同action 24h超限→降频 |
| L3 | 交易时段静默 | WARN | 交易时段→仅NOTIFY |
| L4 | 依赖健康度检查 | HARD | 关键依赖DOWN→BLOCK |
| L5 | 预算强制 | HARD | 超预算→HARD_FREEZE |
| L6 | 回滚完整性 | HARD | 无rollback_plan→BLOCK IRREVERSIBLE |
| L7 | Idempotency | HARD | NON_IDEMPOTENT→单并发 |
| L8 | Config-as-Code | WARN | Config手动改→告警 |
| L9 | Flag交互检查 | SOFT | Flag conflict→WARN |
| L10 | 数据库完整性 | HARD | FK/约束违反→BLOCK |
| L11 | Provenance Chain | HARD | 无法追溯来源→BLOCK |
| L12 | Schema Versioning | HARD | Schema mismatch→BLOCK |
| L13 | 会话感知 | WARN | 跨session上下文断裂→降自治 |
| L14 | RBAC | HARD | 越权操作→BLOCK |
| L15 | 部署安全 | HARD | 未签名的deploy→BLOCK |
| L16 | Online Adaptation | WARN | adaptation过快→限速 |
| L17 | Autonomy Boundary | HARD | 越自治边界→强制L0 |
| L18 | Continual Learning | WARN | catastrophic forgetting risk→EWC check |
| L19 | Cognitive Overload | SOFT | Owner疲劳>0.7→仅P1 |
| L20 | FLE Integrity | HARD | self-modification未审计→BLOCK |
| L21 | Supply Chain/CVE | HARD | CVSS>=9→SAFE_MODE |
| L22 | Data Foundation | HARD | 数据质量 < TH→BLOCK |
| L23 | Meta-Performance | SOFT | 自评估退化→降自治 |
| L24 | AgenticOps | WARN | Agent lifecycle anomaly→review |
| L25 | LLM Quality | HARD | provider degradation→frozen |
| L26 | Chaos Governance | WARN | chaos实验未隔离→暂停 |
| L27 | Compliance | HARD | 合规violation→BLOCK |
