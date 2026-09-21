---
ttl: task_bound
completes_when: 七条裁定项全部由总包/Owner 处置完毕（登记即本车道闭环）
title: tdchain 收尾车道（st-ff-tdchainJ-20260918）转总包裁定清单——七项登记
session: st-ff-tdchainJ-20260918
date: 2026-09-18
parent: docs/_working/tdchain_mine/a0_master_ledger.md
---

# pending_for_max —— tdchainJ 车道登记（只登记不判；总包预裁项按预裁结论落档）

> 真源约定：每条带真源路径；车道侧证据实测于 2026-09-18 午后（HEAD=36c9ca4db2）。

## ① N-5 共享区纠缠脏树"恢复 or 废弃" —— 已由总包裁定 R-001 关闭

- 结论：无标的，已自愈（stash 面=空、staged 删除面=0、claim=0）。本车道复核实测与 R-001 一致：
  `git stash list`=空、`.git/MERGE_HEAD` 不存在。
- 真源：docs/_working/fullflow_campaign/COORDINATION_LEDGER.md §6 已裁 R-001。
- 状态：**关闭**（无需任何后续动作）。

## ② cp3 param-object 三处改造 —— 总包预裁：不主动重构，待 NO-LONG-PARAM-LIST 门禁触发时随批做

- 三处（死信 q-20260918-st-tdchain-20260917-0012 dead_reason 实测原文）：
  - `src/zephyr/strategy_factory/owner_regime_switcher/engine.py:132` `_execute_day`（12 参 > 7）
  - `src/zephyr/strategy_factory/owner_regime_switcher/engine.py:167` `run_leg`（10 参 > 7）
  - `src/zephyr/strategy_factory/owner_regime_switcher/exam.py:137` `_run_window`（10 参 > 7）
- 代码现状：分支 `ai/st-sowner002-20260916/s-owner-002-regime-switcher`（案底 commit=`89dd33dd8a`，
  实测存在且未入 dev——`git merge-base --is-ancestor 89dd33dd8a HEAD`=否，属预期）。
- 预裁理由（总包）：①三处当前无缺陷记录，主动重构=为假设收益支付真实风险；②门禁阈值 7，超限时门禁
  会在下次改动时自动逼出重构，同批收进带域前缀 dataclass 是最低成本时机；③重构未入库代码=白做。
- 六道闸实录真源：docs/_working/tdchain_mine/final_delivery_report.md §三 1'（commit bf65648609）。
- 状态：**登记为"待门禁触发时随批做"，不单独立项**（本车道闭环）。

## ③ 裁定#304 三方撞号 tombstone 治理 —— 总包预裁：采纳，由总包统一执行

- 三方撞号实证（本车道取证，全文见申请书）：
  - 甲方 regcal：dev 侧 `docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml:4120`
    `ruling_id: '裁定#304'` = Regime r4/r10 重校准（因被 `src/zephyr/regime/core/regime_detector.py`
    代码不变式引用，按代码绑定优先**保留 #304**）。
  - 乙方 做T v2 砍：同册 `:3765` `裁定#331` + `:3766` renumber_note"原#304 与 Regime 重校准撞号，
    2026-09-18 按代码绑定优先改号 #331"（原批量登记 commit=01fbfad1，
    docs/_working/kimi_audit/owner_fast_sign_20260917.md 表行 01 仍写"裁定#304"）。
  - 丙方 切换器 verdict：分支 `89dd33dd8a:ruling_registry.yaml:3765` 自带一条 `裁定#304`（切换器出证
    verdict），另 `docs/_working/factory/strategy_cards/e4_report_s_owner_002_regime_switcher.md:3`
    与交接包 `324cf187d7:docs/_working/factory/strategy_cards/e4_handoff_s_owner_002_merge.md:11,19`
    均声称"裁定#304 已原子登记"（登记 commit=fa5c8febaf，未入 dev，留分支档）。
- 申请书：docs/_working/fullflow_campaign/adjudications/req_tdchainJ_01.md（tombstone 由总包执行；
  裁定号一律总包分配，本车道不取号）。
- 状态：**实证交付完毕，待总包执行 tombstone**。

## ④ #306 红队条款① family_registry 立案 —— 总包预裁：立案

- 真源注记：`config/standards.yaml:60` reexam_evidence"①族注册表=治理层立案挂单"。
- 立案书（生成器落点/条目来源/计数字段三要素齐）：
  docs/_working/fullflow_campaign/adjudications/req_tdchainJ_02.md。
- 约束：宪法 §9.5 静态清单禁手工维护 → family_registry 必须是生成器产物；待总包批+分配裁定号。
- 状态：**立案书已交，待总包批**。

## ⑤ ETF 备份五表 `*_tz_bak_20260918` 物理删除时机 —— Owner 门位（登记不催）

- 本车道只读实测（DatabaseService，2026-09-18 午后）五备份表在库：
  kline_etf_1min_tz_bak=326,301,055 行 / 5min=71,856,186 / 15min=24,331,141 / 30min=11,939,337 /
  60min=5,962,194；五正表 `--verify` remaining_utc=0（repair_etf_minute_tz_split.py 只读通道，
  归 instL 独占，本车道未跑 dry-run/execute，`--execute`=Owner 门位禁跑）。
- 净删=Owner 门位，已列 COORDINATION_LEDGER §7（注册表/数据净删）。
- 状态：**登记即闭环，不催**。

## ⑥ `kline_index_intraday` 新表立项 —— 总包预裁：立项，由 residG 车道执行

- 缺表实测：`system.tables` 查 `c1_market.kline_index_intraday` = 0 件（本车道午后实测）。
- 现行代理：`src/zephyr/plan_engine/intraday_l1_tracker.py:405-409`
  proxy_notes.index_intraday = "pending_minute_source(etf_510300_proxy)"。
- DDL 规格（字段/引擎/排序键/分区，对齐 kline_etf_15min 房规）：
  docs/_working/fullflow_campaign/lanes/tdchainJ_kline_index_intraday_spec.md。
- 申请书：docs/_working/fullflow_campaign/adjudications/req_tdchainJ_03.md（转 residG：
  `scripts/ch/apply_market_tables_ddl.py` 归其独占，COORDINATION_LEDGER §2）。
- 状态：**规格+申请书交付完毕，待总包转交 residG**。

## ⑦ 板块分钟三天 15/30/60m 合成翻案与否 —— 总包预裁：维持原裁定（跳过），不翻案

- 原裁定真源：docs/_working/tdchain_mine/e1_tdata_infra/workbook.md（三问停止判据：无独立消费方+
  1m 原料系合成近似+无现成工具且存量 15m 桶时间戳发散存疑）；
  docs/_working/tdchain_mine/final_delivery_report.md §三 2。
- 预裁理由（总包）：翻案需新证据非新意愿；分钟合成 PIT 可复现性风险高（forming bar 中间态本仓明确禁）；
  当前无业务需求方在等。**若未来有明确消费需求方，再按新证据重议。**
- 状态：**维持跳过，登记即闭环**。
