---
ttl: task_bound
---
> ## 结案报告（2026-10-06 由 st-workingchief-20261006 核验）
> **总结论：已结案（机生派生快照，非待办载体；A/B/C/D 四类缺口 0/1/0/0，唯一缺口 MOD-SIG-110 归 frontend_map.yaml 真源治理）**
> **✅ 已完成（摘录）**
> - ①生成器活账落地并取代两本手工缺口总账；②四类对账口径 A-D 全部建成；③生成器 scripts/governance/d5_architecture/generators/generate_frontend_gap_views.py 在仓可复跑
> **⚠️ 未完成**
> - 无
> - （
> - M
> - O
> - D
> - -
> - S
> - I
> - G
> - -
> - 1
> - 1
> - 0
> -  
> - 挂
> - 接
> - 缺
> - 口
> - 的
> - 修
> - 复
> - 义
> - 务
> - 在
> - 真
> - 源
> - 侧
> - ，
> - 非
> - 本
> - 文
> - 件
> - ）
> **核验方式**：全文读+生成器存在性核验+与 2026-08-22 总账未结案章交叉对轴（两账不矛盾）
> **处置建议**：保留（机生件，可随时重派生）


> **派生物声明**：本文件由 `scripts/governance/d5_architecture/generators/generate_frontend_gap_views.py` 自动生成，**禁止手工修改**（手改会被下次派生覆盖）。真源=frontend_map.yaml + depgraph nodes 前端覆盖三字段。取代对象：两本手工缺口总账（2026-08-22 正向/反向账）——过渡期双跑对照，Owner 裁定后总账停手工维护。

# 前端缺口视图（派生活账） · 2026-09-17 10:25 中国标准时间

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

- frontend_map 功能点总数: 359
- depgraph 已声明前端覆盖模块数: 21
- A/B/C/D 四类缺口: 0 / 1 / 0 / 0
