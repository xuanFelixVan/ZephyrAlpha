---
ttl: task_bound
completes_when: known_data_gaps 回写随甲线 WO-3 落地后转 archived
---

# TC-06 R1 结案回写卡——ETF 分钟族时区劈叉（已执行完毕，登记面三处收口）

> 结论：R1 不是"待 Owner 批的修复"，而是**已于 2026-09-18 07:22 执行完毕的事实**
> （执行提交 60ed3aa49c，本班 2026-09-21 重跑 `git merge-base --is-ancestor 60ed3aa49c HEAD`
> 验证 PASS）。执行班只回写了自己作业簿，三处登记面脱节至今。本卡=结案回写。

## 1. 执行终态（A 级证据，本班复核）

- 提交：60ed3aa49c「fix(data)+docs(tdchain): ETF 分钟族时区修复工具收编+五表修复终态」，
  4.12 亿误标行全部转正，备份五表 `*_tz_bak_20260918` 在库可逆。
- 对账真源：docs/_working/tdchain_mine/e1_tdata_infra/workbook.md（五表 remaining_utc=0
  记录）；修复件 scripts/ch/repair_etf_minute_tz_split.py 在 HEAD。
- RULE-DATA-OPS 三步验证在执行批已过（备份在库=可逆性证据）。

## 2. 三处登记面收口处置

| 登记面 | 脱节内容 | 本班处置 | 剩余动作与归属 |
|---|---|---|---|
| docs/_working/kimi_audit/experiments_ledger.md | biz5 行状态停「staged（--execute 等 Owner 门位）」 | **本班已回写**（文末追加修正案，历史行不改写） | 无 |
| src/zephyr/data/config/known_data_gaps.yaml | etf_minute_tz_split_pre_202607 条目仍 status=monitoring（写"等 Owner 批准"，实际已执行） | **不代改**——该文件在甲线（st-data-fix-20260921）写域 src/zephyr/data/** 内，按今夜避让令只登记不改 | 随甲线 WO-3 的 A15 批顺路改册（台账 A15 本就含「etf 时区已执行改 completed」） |
| 归档 biz5 工单停点声明 | 历史件停在 staged 等门位 | **不改写归档历史**（历史行不改写惯例）——本卡即结案凭证 | 无 |

## 3. 连库复测待办（不阻塞结案，列待办）

- 五表 remaining_utc=0 抽验、`*_tz_bak_20260918` 五表在库核验——需连 CH（经 DatabaseService
  只读），交数据线巡检窗顺路执行。

## 4. 判据与红线复核

- 备份表物理删除=Owner 门位，本班未动、也未排期（维持 Owner 挂单）。
- 本卡零状态变更（不改 known_data_gaps、不动 verdict 面），纯登记回写。
