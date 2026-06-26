---
module_id: KE-409
status: active
title: 5.2.3 顶级域层级关系
category: documentation
ttl: permanent
---

# 5.2.3 顶级域层级关系

5.2.3 顶级域层级关系

```
PS  ── meta/（元标准层，~10 文件，固定不增长）
 │
GOV ── governance/（全局治理层，~50 文件）
 │   ├── GOV-DOC  ── governance/document/
 │   ├── GOV-AI   ── governance/ai/
 │   ├── GOV-TASK ── governance/task/
 │   ├── GOV-SEC  ── governance/security/
 │   ├── GOV-CMP  ── governance/compliance/
 │   ├── GOV-ARCH ── governance/architecture/
 │   ├── GOV-DATA ── governance/data/
 │   └── GOV-MOD  ── governance/module/
 │
OPS ── operational/（全局操作层，~10 文件）
 │   ├── OPS-VC   ── operational/vibe_coding/
 │   ├── OPS-DEV  ── operational/devops/
 │   └── OPS-MIG  ── operational/migration/
 │
DOM ── domains/（层域治理，初始 4 层，按需扩展）
     ├── DOM-L00  ── domains/L00_data_source/
     ├── DOM-L02  ── domains/L02_alpha_factor/
     ├── DOM-L04  ── domains/L04_risk_management/
     └── DOM-L07  ── domains/L07_post_trade_analytics/
```
