---
module_id: KE-1094
status: active
title: CBAC 自保规则
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# CBAC 自保规则

CBAC 自保规则

`capabilities.yaml` 中的 `write_config` 规则声明了 AI 对 config/ 的写权限：

```yaml
allow:
  - "config/compression/policy.yaml"    # 唯一允许 AI 修改的配置（Immutable Core 字段除外）
deny:
  - "config/capabilities.yaml"          # 自保：注册表不可改自身
  - "config/risk/**/*"                  # 风控配置不可改
  - "config/drift_thresholds.yaml"      # 漂移阈值不可改（experimentalf/1g 规划）
```

- `capabilities.yaml` 自身禁止被 AI 修改 → 防止权限旁路
- `trigger_router.yaml` 虽不在 `write_config` deny 列表中，但其 schema 被定义为 Human-Gated（ai_autonomy_authority_registry.yaml §2.9），实际修改须走 Owner 审批
