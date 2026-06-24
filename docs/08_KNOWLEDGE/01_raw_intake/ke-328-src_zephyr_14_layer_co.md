---
module_id: KE-301---src-zephyr-----14-layer-co-001
status: active
title: 4. `src/zephyr/` — 14-layer code architecture / 14 层代码分层架构
category: documentation
---

# 4. `src/zephyr/` — 14-layer code architecture / 14 层代码分层架构

4. `src/zephyr/` — 14-layer code architecture / 14 层代码分层架构

> Dependency direction: upper layers depend on lower layers. Cross-layer direct calls are prohibited; shared contracts pass through `shared/`.
>
> 依赖方向：上层依赖下层，禁止跨层直接调用；跨层共享契约通过 `shared/` 传递。
