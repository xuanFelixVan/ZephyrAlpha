---
module_id: KE-1044
status: active
title: 5.5 `03_modules/_cross_layer/` — 跨层模块
category: governance
---

# 5.5 `03_modules/_cross_layer/` — 跨层模块

5.5 `03_modules/_cross_layer/` — 跨层模块

**用途**：核心职责横跨 ≥2 个 C 轨层业务边界、任一单一层无法完整描述其接口的模块。

**内部结构**（方案A——按关联层分组）：
```
_cross_layer/
├── L02-L03/          # 因子→信号跨层
├── L04-L05/          # 风控→组合跨层
├── L03-L04-L05/      # 多跨层
└── index.md          # 模块清单 + 迁移计划
```

> **方案B（备选）**：扁平结构，模块直放在 `_cross_layer/` 下。方案A更适合 1500 模块场景（扁平跨层目录会过大）。

**准入规则**：
- ✅ 模块 `layer` frontmatter 值为 `cross_layer`
- ✅ 核心职责横跨 ≥2 个 C 轨层
- ❌ 可归属单一 C 轨层的模块（→ `l<NN>_*/`）
- ❌ 纯 B 轨平台能力（→ `infra_ops/` 或 `_b_track_interfaces/`）

**迁移清单**：8 个现有模块已声明 `layer: cross_layer`，物理仍居 `infra_ops/` 下（详见 `_cross_layer/index.md`），计划由 Phase 5 迁移。
