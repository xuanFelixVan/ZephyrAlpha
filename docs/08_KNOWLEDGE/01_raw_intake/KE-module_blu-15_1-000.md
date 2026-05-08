---
module_id: KE-module_blu-15_1-000
title: 15.1 自举五阶（从最坏情况逐步恢复）
category: module_blueprint
---

# 15.1 自举五阶（从最坏情况逐步恢复）

15.1 自举五阶（从最坏情况逐步恢复）

```
Level 0: 裸盘状态（只有 Python + 源代码，无任何盘点产物）
  ├─ 触发: unified_asset_index.yaml 不存在
  ├─ 动作: run_full_scan() → 扫描六大目录 → raw_asset_scan.json
  └─ 产出: raw_asset_scan.json（纯扫描，无分类/无对账）
       ↓
Level 1: 原始清单状态（有扫描，无分类）
  ├─ 触发: raw_asset_scan.json 存在但 unified_asset_index.yaml 不存在
  ├─ 动作: run_classification(raw_scan) → 四维分类
  └─ 产出: classified_assets.json（已分类，未对账/未注册）
       ↓
Level 2: 分类状态（有分类，无对账）
  ├─ 触发: classified_assets.json 存在但 reconciliation 未跑
  ├─ 动作: run_reconciliation(classified_assets, 24 registries)
  └─ 产出: reconciliation_report.md + unified_asset_index.yaml
       ↓
Level 3: 完整状态（索引存在，健康评分可用）
  ├─ 触发: unified_asset_index.yaml 存在且健康评分 ≥ C
  ├─ 动作: 正常全量扫描 + 增量对账
  └─ 产出: 更新 unified_asset_index.yaml（增量式）
       ↓
Level 4: 元盘点状态（每一步都验证盘点系统自身的条目）
  └─ 触发: 每次索引更新
     验证: "src/zephyr/asset_inventory/" 下所有模块均在 active 列表中
     失败 → 标记 self_orphan_warning → 写入 reconciliation_report
```
