---
module_id: KE-329
status: active
title: 4.2 Breaking Change 处理流程
category: documentation
ttl: permanent
---

# 4.2 Breaking Change 处理流程

4.2 Breaking Change 处理流程

```
发现需要 Breaking Change
    ↓
在 `architecture_model/contracts/cross_layer_contracts.yaml` 中标记 old_version → deprecated
    ↓
新建 new_version 接口，与旧版本共存一个 MINOR 周期（≥1 sprint）
    ↓
所有消费方完成迁移确认（checklist 见 `architecture_model/contracts/cross_layer_contracts.yaml`）
    ↓
废弃旧版本，更新 MAJOR 版本号
    ↓
在 architecture-rationale-log.md 登记理由
```

**单人开发阶段的简化原则**：当消费方仅为本项目内部模块时，Breaking Change 可以在同一 commit 中同步修改所有消费方，无需双版本共存；但必须在 commit message 中注明 "BREAKING: [契约名] v[old] → v[new]"。
