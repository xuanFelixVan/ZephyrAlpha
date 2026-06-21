---
module_id: KE-2319
status: active
title: 4.2 目录命名规则（MUST）
category: module_blueprint
---

# 4.2 目录命名规则（MUST）

4.2 目录命名规则（MUST）

| 目录类型 | 命名约定 | 示例 |
|------|---------|------|
| Level 0 总蓝图 | `_system-master/`（下划线前缀，表顶层）| `_system-master/` |
| Level 1 域蓝图 | `_domain-{layer-range}/`（下划线前缀 + domain + 层级范围，表跨层）| `_domain-l02-l03/` |
| Level 2 模块蓝图 | `l{NN}_{name}/`（层级编号 + 下划线 + 全小写 kebab-case 名称）| `infra_ops/` |
| 模块子目录 | `{module-name}/`（全小写 kebab-case，与 module_id 中 name 字段一致）| `task-system/` |
| 交付记录子目录 | `delivery/` | `delivery/` |

**规则**：
- Level 0 和 Level 1 的蓝图目录**以 `_` 下划线前缀**，与 Level 2 模块目录区分——方便 AI Agent 和人类快速定位金字塔高层
- Level 2 的模块目录**以层级编号 `l{NN}` 开头**，对齐 `module-registry.yaml` 的 `layer` 字段
- **所有目录名全小写、kebab-case**——禁止大写、中文、空格
