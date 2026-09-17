---
ttl: task_bound
title: ENV1 清洁执行计划（原稿只设计不执行；现状态=已按计划执行完毕）
owner: ZephyrAlpha-Owner
session: st-cleanexam-20260918/A
date: 2026-09-18
status: executed_by_gc_20260918
---

# ENV1 执行计划（设计稿）

> **授权链**：ruling #清洁执行（2026-09-18，active）附条件批准 → 本计划=条件核验+操作细化。原稿（status: designed_not_executed）未执行任何一步；**现状态=总包（tdchain 清扫/施工会话）已按本计划执行完毕，见下方执行状态注**。
> **执行清单来源**：`verdict_tables.csv`（10 表）+`verdict_files.csv`（125 件 tmp）。**bak 一律不在清单**（判决=保留）。

> **执行状态注（2026-09-18 再生时补记）**：总包已按本计划完成施工——10 表 DROP + 125 件 tmp 清除均落地（A 线再生时只读复核：`system.tables` 10 表命中=0、三处 tmp 复扫=0、`integrator_progress.db.bak_20260909b/_c` 在位，保留判决维持）。本文件因 tdchain 清扫会话误删 untracked 产物，由 st-cleanexam-20260918/A 自上下文与 `.runtime/tmp` 底档原样再生，判决与计划内容不变。

## 环 1 复核（执行日重验，任一不过即中止）

1. 宪法冷启动：Python 3.12 PATH 修正 + `python scripts/lock_files.py cleanup` + `python -m zephyr.trading.process_reaper --status`（计划任务不存在=禁执行）。
2. 10 表行数复核：逐表 `SELECT count() FROM c1_market.\`<表>\``——**必须全为 0**；非 0 表从清单剔除并回写判决。
3. tmp 增量重扫：同口径 find 三处（catalogs 含 _archive / config / data）——清单以**执行日实扫交集**为准（基线 125 件 ∩ 当日存在），新残留走同一判决脚本再验后并入。
4. `data/runtime/tmp_protocol_head.md`、bak×3 在排除清单，任何脚本不得触碰。

## 环 2 冻结清单

1. DROP 白名单（10，精确全名）：`kline_15min_tzbak2_20260914`、`kline_15min_tzbak_20260914`、`kline_1min_tzbak2_20260914`、`kline_30min_tzbak2_20260914`、`kline_30min_tzbak_20260914`、`kline_5min_tzbak3_20260914`、`kline_5min_tzbak4_20260914`、`kline_60min_tzbak2_20260914`、`kline_60min_tzbak_20260914`、`crypto_kline_daily_bak_okxshell`（全在 c1_market）。
2. rm 白名单：125 个精确路径（verdict_files.csv 判决=可删行），**按全名匹配删除，禁通配符/禁按模式批删**（防误删执行瞬间新写 tmp）。
3. 冻结件落 `.runtime/sessions/<sid>/staging/env1_frozen_manifest.json`（路径+size+mtime+md5 快照）。

## 环 3 执行（顺序固定）

1. **先回滚件后删除**：
   - CH：逐表 `SHOW CREATE TABLE c1_market.\`<表>\`` 存 `staging/env1_rollback_ddl.sql`（今日已试捕获 10/10，模板见 `.runtime/tmp/env1_rollback_ddl.sql`，执行日重捕为准）。
   - tmp：125 件 tar 至 `staging/env1_tmp_archive_202609XX.tar.gz`（约 22 MB）。
2. DROP：逐表单条执行（空表无需 mutations sync）；每条后即时回查 `EXISTS system.tables`。
3. rm：python 按 manifest 精确路径删除，**守卫= mtime < 10 分钟的件跳过留档**（防在途写），守卫剔除件记入报告。
4. 全程零 git add/commit（全部件均 `.gitignore:146 *.tmp` 或 untracked，追踪树零接触）。

## 环 4 验证

1. CH：`system.tables WHERE name IN (10 表)` 返回 0 行；主表抽查（kline_1min/kline_5min/crypto_kline_daily count 量级不变）。
2. 文件：三处复扫 tmp 期望=0（或仅守卫剔除件）；`git status --porcelain` 与执行前基线一致（零新增差异）。
3. 冒烟（只读）：`python -c "from zephyr.data.metrics import get_metrics; get_metrics().flush()"` 成功重写 `data/metrics.prom`；仪表盘可启动（`app_panel.py` 导入级冒烟）。

## 环 5 回写

1. `python scripts/ch/_data_inventory.py`（manual 只读盘点）重跑，将 `docs/02_enterprise_architecture/05_dataflow_architecture/data_inventory.md` 中 10 表行移除/标记已退役（该文档为机生清单的落稿，禁手工只改数字）。
2. 本战役 00_master_ledger 与本簿 status 收口；CREATE-GUARD/新文件登记义务一并办理。
3. 长尾 L1-L4 登记入 pending_items（见 00_env_mining.md §6）。

## 回滚方案

| 对象 | 回滚 |
|---|---|
| 10 空表 | 重放 `env1_rollback_ddl.sql`（0 行表，结构级回滚=零数据损失） |
| 125 tmp | 解 tar 归位（md5 与冻结 manifest 核对） |
| 误删守卫外新 tmp | 由正本写者下次成功写自愈（tmp 本非真源） |
| bak | 未入清单，无需回滚 |

## 中止条件

reaper 计划任务缺失；环 1 任一 count()>0；冻结 manifest 与实盘 md5 不符；执行中出现新会话对同批文件的活跃 claim——任一触发即整体中止留档。
