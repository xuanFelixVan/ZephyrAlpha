---
module_id: KE-3895
title: 盲点覆盖矩阵（130条全覆盖）
category: module_blueprint
ttl: permanent
---

# 盲点覆盖矩阵（130条全覆盖）

盲点覆盖矩阵（130条全覆盖）

| 盲点范围 | 数量 | 代表性 task_id | 实现 |
|---------|:---:|---------------|------|
| B1-B10 核心流程盲点 | 10 | 0200-0203 | 骨架+executor |
| B11-B20 数据模型盲点 | 10 | 0201,0218,0219 | dumper+state_machine |
| B21-B30 安全盲点 | 10 | 0204,0233-0235 | verifier+guard+detector+scanner |
| B31-B40 回滚深度盲点 | 10 | 0205-0214 | trigger+loop+cooldown+lock+simulator |
| B41-B50 基础设施盲点 | 10 | 0215-0221 | cli+kill_switch+forward_fix |
| B51-B60 审计盲点 | 10 | 0223-0231 | context+nexus+llm+differential |
| B61-B70 跨平台盲点 | 10 | 0232-0245 | bootstrap+hallucination+cross_platform+venv+env |
| B71-B80 扩展盲点 | 10 | 0246-0252 | temporal+acl+timeout+s3+merkle+submodule+gdpr |
| B81-B90 安全深度盲点 | 10 | 0253-0259 | injection+psql+nested+irreversible+throttle+audit+binary |
| B91-B100 治理盲点 | 10 | 0260-0263 | prophecy+density+autonomy+trust |
| B101-B110 取证盲点 | 10 | 0264-0265 | forensic Part 1+2 |
| B111-B120 极端场景盲点 | 10 | 0266 | forensic Part 3+owner_absent |
| B121-B130 剩余盲点 | 10 | 0267-0268 | governance+adversarial |
