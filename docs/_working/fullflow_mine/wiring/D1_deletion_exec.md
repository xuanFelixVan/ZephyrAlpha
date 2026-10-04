---
ttl: task_bound
title: "已批净删执行报告"
owner: st-datasop-20260930
language: zh
status: active
version: "1.0.0"
date: 2026-10-04
---

# D1 净删执行报告（批 A/B/C/D/E，EXEC-D1）

依据：Owner 2026-10-04 口头裁定批准净删（0-1/0-2/0-4 三批）。每删一表三步验证：必要性=裁定已批｜真实性=删前行数终核+全仓引用复查｜可逆性=DDL/全库备份先行留档。写库走正门 `load_ch_writer_config`（写账号）。

## 批 A：CH 备份/隔离表 9 张 DROP（c1_market）——完成

| 表 | 删前行数 | 判定 |
|---|---:|---|
| kline_daily_hfq_legacy_20260924 | 8,426,036 | DROP |
| kline_daily_hfq_preversion_20260925 | 10,079,242 | DROP |
| kline_daily_hfq_quarantine_20260925 | 10,475 | DROP |
| kline_daily_hfq_recalc | 100,054 | DROP |
| kline_weekly_hfq_legacy_20260924 | 2,127,400 | DROP |
| kline_weekly_hfq_legacy_r1_20260924 | 1,856,391 | DROP |
| kline_monthly_hfq_legacy_20260924 | 502,496 | DROP |
| kline_monthly_hfq_legacy_r1_20260924 | 524,474 | DROP |
| _tmp_mat_test | 0 | DROP |

- DDL 全量存档（删前 SHOW CREATE）：`docs/_working/fullflow_mine/wiring/D1_ddl_backup_20261004.md`
- 引用复查：9 表在全仓 src/scripts/config/docs01 零活跃引用；`kline_daily_hfq_recalc` 唯一命中 = `scripts/governance/meta_question/wo004/recalc_hfq.py` 文档串历史提及（WO004 换名工艺记录，非消费者），未改动。
- `index_valuation_daily_quar_20260920`：删前复查已 ABSENT（他方先删），跳过。
- 执行：`DROP TABLE c1_market.<t> SYNC` 逐表执行，post-verify `SHOW TABLES` 零残留。
- 提交：f42711a88b（CREATE-GUARD token 先行）→ 20d9fd9acc（DDL 存档 + 批 A 留痕）。

## 批 B：governance.db 空表 3 张 DROP——完成

- audit_trail(0 行)、costs(0 行)、report_archive(0 行) 全部 DROP，post-verify 三表缺席、余 43 表完好。
- 可逆性：写前全库备份 `.runtime/tmp/governance.db.bak_20261004`（228,577,280 字节）；三表 DDL 存档追加至 D1_ddl_backup_20261004.md 批 B 节。
- 引用复查：costs 全仓零命中；audit_trail 命中均为同名 Python 包（zephyr.compliance.audit_trail）非 DB 表；report_archive 命中 = reconciliation_schema.py 的 DDL 常量（模块自述"落库执行归后续持久化批次"，无执行方调用）+ JsonlArchiveSink（真源为 data/reports/report_archive.jsonl 文件，非 DB 表）。attribution_result_store.py 仅建/消费 attribution_results 表（不在删除清单）。
- 提交：c3c4079f（governance.db 本身 gitignore 不入库，DDL 追加件为载体）。

## 批 C：空目录 3 个 rmdir——完成

- data/fills、data/gate_cache、data/scans 删前 ls 确认全空，已删除。git 不追踪空目录，零 tracked 变更（随批 B 宣告）。

## 批 D：hk_kline 判定——不删（缺口分支）

浅层三判据全过，但行级覆盖有实质缺口，按指令"覆盖有缺口→不删，登记缺口数据留档"执行：

| 维度 | hk_kline | kline_hk_daily | 判定 |
|---|---|---|---|
| 代码覆盖 | 193 canonical 标的 | 193/193 全含（5702 原始 symbol） | 通过 |
| 最新日期 | 2026-09-15 | 2026-09-30 | 通过 |
| 字段集 | 13 列 | 全含 + name 列 | 通过 |
| 行级 (canonical,trade_date) 对拍 | 6,107 对 | **3,774 对无对应** | **缺口** |

- 结构性证据：143/193 标的于 2026-09-15 在 kline_hk_daily 缺席；抽样 00003/00004/00005 在 kline_hk_daily 仅 5-6 行（08-21~09-16 零散）对 hk_kline 全窗密集日 K——qmt 源对小市值港股覆盖稀疏，hk_kline（miniqmt 源）3,774 对日 K 为库内唯一副本，删则永久灭失。
- 处置：①表保留 ②tasks.yaml 双任务（hk_kline_incremental / hk_kline_full_refresh）维持不动，删除分支未触发 ③缺口登记 `src/zephyr/data/config/known_data_gaps.yaml` 新增条目 `hk_kline_row_level_coverage_gap`（status: accepted，含复检 SQL 指针）。
- 提交：1acfd6c3b6 为并发会话 st-tdm-chief 提交（本批 commit 首跑与其竞速，网关误报其 hash；实际本批重跑落定）→ c97aa68406（本批正式落地，post-verify 26 insertions 含缺口条目）。

## 批 E：登记收尾——核对后零改动

- `data_asset_registry.yaml` 无本批 9 张被删表条目（grep 零命中）→ 按指令跳过 retired 标注；hk_kline 条目（DS-132, status: active）对应表保留，维持 active。
- ROOR/骨架计数未动（净删批后由维护流统一重算）。

## 偏差与异常留痕

1. DDL 备份原指令 `.sql` 名：DIRECTORY-CONTRACT 门禁（docs/_working 仅许 md/csv/yaml/html）阻断，改存同名 `.md`，DDL 内容零改动。
2. 首个 hk_kline 判定提交与 st-tdm-chief-20261004 并发竞速：网关报"OK committed hash=1acfd6c3"实为该时点 HEAD（他会话提交），本批变更仍在暂存区；重跑落定 c97aa68406。已按"提交后核实 git log"铁律捕获。
3. 会话注册中途过期触发 SESSION-REQUIRED：按门禁指路 session_worktree_start 重注册（WORKSPACE_DRIFT_BLOCKED→allow_workspace_drift 逃生，主区 1442 残留=他会话合法 WIP 确认不触碰）；allow_overlap 逃生通道因 24h 计满 5 次被 TRAE-079 限频，未再使用。
4. 批 D 提交吸收披露：known_data_gaps.yaml 工作区预存 st-tclose-b1retire-20261004 的 verification_20261004 注记（异 hunk 完整独立变更，Owner 批 B1 三退役收口），随批带入并在 commit message 披露，post-verify 逐行核对。
5. 本文件与 D1_ddl_backup_20261004.md 的 creation_token 均经 batch_creation_tokens.py 登记（capability=d1_net_deletion，含 merge_evaluation）。

## 提交索引（本会话 D1 净删批）

| commit | 内容 |
|---|---|
| f42711a88b | 批 A 前置 token 先行（capability_canonical_file_registry +1） |
| 20d9fd9acc | 批 A：CH 9 表 DROP 留痕 + DDL 存档 |
| c3c4079f | 批 B+C：governance 3 表 DROP + 3 空目录 rmdir |
| c97aa68406 | 批 D：hk_kline 判不删 + 缺口登记（批 E 零改动） |
