---
ttl: task_bound
---

> **派生物声明**：本文件由 `scripts/governance/d5_architecture/generators/generate_frontend_gap_views.py` 自动生成，**禁止手工修改**（手改会被下次派生覆盖）。真源=frontend_map.yaml + depgraph nodes 前端覆盖三字段。取代对象：两本手工缺口总账（2026-08-22 正向/反向账）——过渡期双跑对照，Owner 裁定后总账停手工维护。

# 前端缺口视图（派生活账） · 2026-09-07 01:33 中国标准时间

## A. 前端有 → 后端没有（0 项：frontend_map 功能点 backend_ref 空）

| 功能点 | 页面 | 名称 | 状态 |
|---|---|---|---|

## B. 后端有 → 前端没有（1 项：has_frontend=yes/planned 但 frontend_ref 空）

| 模块 | has_frontend | 说明 |
|---|---|---|
| MOD-SIG-110 | yes | 声明有前端但未挂功能点 |

## C. 悬空引用（0 项：frontend_ref 指向 frontend_map 不存在的功能点）

| 模块 | 悬空引用 |
|---|---|

## D. 对账异常（0 项：has_frontend=no 但未填理由）


## 统计

- frontend_map 功能点总数: 302
- depgraph 已声明前端覆盖模块数: 20
- A/B/C/D 四类缺口: 0 / 1 / 0 / 0
