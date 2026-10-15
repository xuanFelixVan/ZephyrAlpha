---
doc_type: audit_report
ttl: permanent
schema_version: '1.0'
created: '2026-10-15'
sid: 'st-autoplan-20261015'
family_id: 'WORKING-REF-SWEEP'
domain: 'governance'
title_zh: '_working 归档波全仓断链普查：2490 处断链/902 目标，五批次修复方案'
status: final
lineage:
  run_id: 'working_ref_sweep_20261015'
  source_book: 'C:/Users/fanzi/Desktop/ZephyrAlpha_condaxis_tmp/working_ref_sweep/broken_refs.md（3189 行全量明细）+ sweep_summary.json + broken_records.json'
---

# _working 归档波断链普查定稿（P1 工单的普查交付）

> 背景：_working TTL 归档波移走大批文件后，全仓代码/配置中指向 `docs/_working/` 的引用成为断链。
> 已实证修复 3 处（card_binding/test_card_binding/exit_simulator）；本普查为全量清点。

## 总量

扫描 5527 文件（scripts/src/config × .py/.yaml/.ps1）｜引用行 2529｜引用 2553 次｜**断链 2490 次/去重目标 902**（功能行 1791+注释行 699）｜活链 63（47 处 _working 根目录引用合法）。

## 五批次修复方案

| 批次 | 规模 | 处置 |
|---|---|---|
| 1 | 440 次/168 目标 | 改指永久区 04（目标已逐一核验盘面在）——机械改指 |
| 2 | 1813 次/583 目标 | 改指 `docs/_archive/_working_cleared/`（实际归档落点）——机械改指 |
| 3 | 39 次/26 目标 | 同名模糊命中，需人工逐条判定 |
| 4 | 196 次/123 目标 | 目标彻底消失（疑 TTL 永久删除，典型：同花顺资料/、根级 dated 战役报告 10+）——**需 Owner 定夺** |
| 5 | 2 处 | 动态模板（前缀仍活），保留 |

## 断链 top（功能行集中度）

1. config/strategy_card_lifecycle_map.yaml 474 处 2. config/data_supply_chain_map.yaml 268 3. config/trading_day_cycle_map.yaml 154 4. config/trading_decision_map.yaml 110 5. config/dev_delivery_map.yaml 75 6. config/construction_workflow_map.yaml 42+resource_profile_registry.yaml 34 7. map_build skeleton 群 ~250 8. script-manifest.yaml 47

**修复口径铁律**：65% 断链集中在 7 个 config/*_map.yaml 架构图——它们是 **d5 生成器产物**（generate_trading_day_cycle_map.py 等），修复=**修生成器内路径后重跑生成器**，禁手改 yam；script-manifest.yaml 同理。

## 盘面事实修正（重要）

`docs/_archive/_working_20261014/` **物理不存在**（该名 manifest 自述"在途暂存待归档袋落地"）；实际归档落点=`docs/_archive/_working_cleared/`（142 项）。wave1 永久区 `docs/04_research_records/` 已承载迁移成果。**任何引用 `_working_20261014` 的现行指针均需按本事实复核。**
