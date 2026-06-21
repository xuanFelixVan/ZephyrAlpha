---
module_id: KE-1511
title: 14.1 自动触发矩阵（什么时候盘点——不需要人决定）
category: module_blueprint
---

# 14.1 自动触发矩阵（什么时候盘点——不需要人决定）

14.1 自动触发矩阵（什么时候盘点——不需要人决定）

| 触发条件 | 触发机制 | 盘点动作 | 频率 |
|---------|---------|---------|:--:|
| **AI 创建新文件** | scaffold.py 钩子 | 自动写 `unified_asset_index.yaml` 新增条目 | 实时 |
| **定时触发** | Pipeline cron / Task Scheduler | 全量扫描 + 对账 + Dashboard 更新 | 1 次/小时 |
| **Git commit 后** | pre-commit / post-commit hook | 增量扫描（只扫变更文件） + 快速对账 | 每次 commit |
| **Phase Manager 检查** | Phase 1 gate_asset_inventory | 健康评分检查 → < C 则阻断阶段推进 | 每次 Phase 检查 |
| **Session 结束时** | SessionContinuity.generate_and_save() | 上报当前资产摘要到 handoffs 表 | 每次 session 关闭 |
| **Session 开始时** | 冷启动序列 STEP 4.5 | 读最新 unified-asset-index.yaml → 恢复资产认知 | 每次新 session |
| **Owner 手动查询** | CLI: `python scripts/governance/generators/generate_asset_index.py --dashboard` | 按需生成最新 Dashboard | 按需 |
