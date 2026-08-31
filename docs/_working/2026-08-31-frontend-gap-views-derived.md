---
ttl: task_bound
---

> **派生物声明**：本文件由 `scripts/governance/d5_architecture/generators/generate_frontend_gap_views.py` 自动生成，**禁止手工修改**（手改会被下次派生覆盖）。真源=frontend_map.yaml + depgraph nodes 前端覆盖三字段。取代对象：两本手工缺口总账（2026-08-22 正向/反向账）——过渡期双跑对照，Owner 裁定后总账停手工维护。

# 前端缺口视图（派生活账） · 2026-09-01 00:32 中国标准时间

## A. 前端有 → 后端没有（16 项：frontend_map 功能点 backend_ref 空）

| 功能点 | 页面 | 名称 | 状态 |
|---|---|---|---|
| F-STOCKQ-COSTLINE | P-STOCKQ | 持仓成本线 | 已建 |
| F-STOCKQ-MARKS | P-STOCKQ | 量化买卖点标注 | 已建 |
| F-STOCKQ-TRADES | P-STOCKQ | 真实成交买卖点 | 已建 |
| F-STOCKQ-DRAW | P-STOCKQ | 画线工具 | 已建 |
| F-STOCKQ-INDICATORS | P-STOCKQ | 指标系统 | 已建 |
| F-STOCKQ-EVTROW | P-STOCKQ | 事件图标行 | 已建 |
| F-STOCKQ-TIMELINE | P-STOCKQ | 自定义时间轴 | 已建 |
| F-STOCKQ-CHIP | P-STOCKQ | 筹码峰分布 | 已建 |
| F-STOCKQ-WATCHLIST | P-STOCKQ | 自选列表 | 已建 |
| F-STOCKQ-INFO | P-STOCKQ | 右栏资料面板 | 已建 |
| F-OVW-LAYOUT | P-OVERVIEW | 布局管理 | 已建 |
| F-OVW-ICONBAR | P-OVERVIEW | 竖排图标栏 | 已建 |
| F-OVW-POS-A | P-OVERVIEW | A股持仓 | 已建 |
| F-OVW-POS-C | P-OVERVIEW | 币圈持仓 | 已建 |
| F-OVW-INDEX-CARDS | P-OVERVIEW | 指数卡片 | 已建 |
| F-OVW-TICKER | P-OVERVIEW | ticker-bar | 已建 |

## B. 后端有 → 前端没有（1 项：has_frontend=yes/planned 但 frontend_ref 空）

| 模块 | has_frontend | 说明 |
|---|---|---|
| MOD-SIG-110 | yes | 声明有前端但未挂功能点 |

## C. 悬空引用（0 项：frontend_ref 指向 frontend_map 不存在的功能点）

| 模块 | 悬空引用 |
|---|---|

## D. 对账异常（0 项：has_frontend=no 但未填理由）


## 统计

- frontend_map 功能点总数: 16
- depgraph 已声明前端覆盖模块数: 20
- A/B/C/D 四类缺口: 16 / 1 / 0 / 0
