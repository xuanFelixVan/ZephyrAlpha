---
module_id: KE-659
status: active
title: Vendor Registry 配置片段
category: documentation
ttl: permanent
---

# Vendor Registry 配置片段

Vendor Registry 配置片段
brokers:
  - id: XXXX-securities
    name: "XXXX 证券"
    jurisdiction: cn_a_share
    asset_class: equity
    provider_rank: primary
    acquisition_method: sdk
    status: active
    fallback_brokers: [YYYY-securities]
  - id: YYYY-securities
    name: "YYYY 证券"
    jurisdiction: cn_a_share
    asset_class: equity
    provider_rank: secondary
    status: active
```

---
