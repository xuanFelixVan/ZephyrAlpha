---
ttl: task_bound
completes_when: 总包对裁定#304 三方撞号完成 tombstone 治理并统一分配裁定号
title: 裁定申请书 req_tdchainJ_01——#304 三方撞号 tombstone 治理（实证交付）
lane: st-ff-tdchainJ-20260918
date: 2026-09-18
---

# req_tdchainJ_01 · 裁定#304 三方撞号 tombstone 治理

## 背景

`ruling_registry.yaml` 是永久产物，编号错一次即永久留痕。2026-09-17/18 并发风暴下裁定 #304 被三方
各自声称（本仓已实证系统性问题：09-17 #290-294 曾被五件他会话覆盖）。总包预裁=采纳治理，由总包
统一执行（统一分配裁定号 + tombstone 标记已撞号条目）；本申请书交付三方撞号实证，车道不取号、不动
注册表（总包独占写，COORDINATION_LEDGER §4）。

## 三方撞号实证（file:line 全带，2026-09-18 午后实测）

| 方 | 声称内容 | 载体与锚点 | 现状 |
|---|---|---|---|
| 甲 · regcal（Regime r4/r10 重校准） | `ruling_id: '裁定#304'` | dev 侧 `docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml:4120`；被 `src/zephyr/regime/core/regime_detector.py` 代码不变式引用 | **保留 #304**（2026-09-18 按代码绑定优先裁定，见乙方 renumber_note） |
| 乙 · 做T v2 战役砍 | 原取号 #304（批量登记 commit=01fbfad1，23 件 #304-#326） | 同册 `:3765` 现为 `裁定#331`，`:3766` renumber_note："原#304 与 Regime 重校准撞号（其被 regime_detector.py 代码不变式引用故保留 #304），2026-09-18 按代码绑定优先改号 #331"；`docs/_working/kimi_audit/owner_fast_sign_20260917.md` 表行 01 仍写"裁定#304" | 已改号 #331；**下游引用（owner_fast_sign 等）仍指旧号，需消歧** |
| 丙 · S-OWNER-002 切换器 verdict | "裁定#304 已原子登记"（登记 commit=fa5c8febaf） | 分支 `89dd33dd8a:docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml:3765` 自带一条 `裁定#304`；`docs/_working/factory/strategy_cards/e4_report_s_owner_002_regime_switcher.md:3`；交接包 `324cf187d7:docs/_working/factory/strategy_cards/e4_handoff_s_owner_002_merge.md:11,18-24` | **未入 dev**（模块留分支档，#310 不予放行案底）；分支侧 registry 副本与 dev 永久分叉 |

## 选项与建议（供总包裁定）

- A（建议）：tombstone 治理——在 dev 册 #304 条目追加 `collision_note`（甲为唯一正主；乙=#331 改号在案；
  丙=分支档声称，未入库，引用时须带 title 消歧），并对 owner_fast_sign 等下游旧引用加消歧注记；
  丙方分支如复活，其 #304 引用必须重新向总包取号。
- B：不治理，维持终局报告 §三 7 的"引用带 title 消歧"口头约定（风险：永久产物留三处矛盾记载，
  RULING-REFERENCE 门禁无法机械消歧）。

## 影响面

仅注册表注记与文档消歧，零代码行为变化；V-06/#316 已立法的编号唯一性治理属维护班，本案是其实证输入。

## 真源清单

- docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml（:3765-3766、:4120）
- docs/_working/kimi_audit/owner_fast_sign_20260917.md（行 01）
- docs/_working/tdchain_mine/final_delivery_report.md §三 7（commit bf65648609）
- git 分支 ai/st-sowner002-20260916/s-owner-002-regime-switcher（89dd33dd8a、fa5c8febaf）
