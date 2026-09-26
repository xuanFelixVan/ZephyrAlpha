---
ttl: task_bound
---

# lane_pipe · realtime_snapshot（全市场实时快照灌入链）— 判定：不通 ❌

## 六向台账

### 1 做什么（本链职责）
盘中每 5 分钟拉全市场 A 股快照（akshare `stock_zh_a_spot_em`，#ARCH-IFIND-FAILOVER 接管 iFind 实时行情），落 `c1_market.realtime_snapshot`，供仪表盘/盘中决策读"最新一帧全市场"。

### 2 依据（在册证据）
- 任务在册：`src/zephyr/data/config/tasks.yaml:1044` `realtime_snapshot_incremental`，schedule=`intraday_realtime`（交易日 9-15 时每 5 分钟），capability=`realtime_snapshot`，`incr=True`。
- provider 在册：`src/zephyr/data/implementations/akshare_provider.py:5816 _fetch_realtime_snapshot`，L5817 文档串"写入 c1_market.realtime_snapshot"；L129 `_TBL_REALTIME_SNAPSHOT = get_registry().table("market_realtime_snapshot")`。
- 表在册且有正确 schema/分区：`CREATE TABLE c1_market.realtime_snapshot (snapshot_time DateTime64(3,'Asia/Shanghai'), symbol, open/high/low/close Decimal, volume, amount, data_source, ingest_ts DEFAULT now(), exchange MATERIALIZED …)`（DDL 实测无 TTL 子句）。

### 3 改动点（候选，本轮不改）
- 落库层：`ch_writer.write_tsv` / `http_insert` 对 realtime_snapshot 的 INSERT 反复失败并落 `data/failures/*_realtime_snapshot_incremental_*.json`（降级路径 #ARCH-CH-013），但 `task_runs` 仍记 SUCCESS（fetch 段计数即判成）。
- 待定位：为何降级件未回灌（local_replay 回灌腿是否覆盖本表）。
- 待定位：`market_realtime_snapshot`(registry key) 与 `c1_market.realtime_snapshot`(tasks 目标) 是否同表（若 registry 解析到别的库/表名→写到别处，本表恒空）。

### 4 判据（什么算通）
`count(*) FROM c1_market.realtime_snapshot > 0` 且 `max(snapshot_time)` 落在最近一个交易时段；且 `data/failures/*realtime_snapshot*` 不再新增。

### 5 读数（实测·只读）
- `SELECT count() FROM c1_market.realtime_snapshot` → **0**（两次独立查询均 0）。
- `task_runs` 最近一次（2026-09-24T07:40:06Z）status=**SUCCESS**，rows_fetched=**5568**，rows_written=**5568**，error=None — 但表 0 行（"写成功"与"落库 0 行"矛盾）。
- 09-25（周五交易日）**无该任务运行记录**（intraday_realtime 档应跑，缺席）。
- `data/failures/` 命中大量本任务失败件（20260722 / 20260803(多条) / 20260824 / 20260825 / 20260918 …）。
- ch_writer.query 失败即返 ""（L483），调用方按空判"无数据"→ 探针失败被读成空表（病灶 C）。

### 6 风险
- 盘中"最新一帧全市场"消费方读到空 → 静默降级，可能误判"无行情"。
- 任务 SUCCESS 掩盖落库失败 = 监控盲区（其它表可能同病，见骨架 §5.6 DEFERRED_PERSISTENCE 未归因）。

## 自审三态
- **PASS**：表 count 由 SELECT 独立两查确证=0；任务态/失败件/DDL/代码位置均给到绝对锚点。
- **FAIL（本轮未做）**：未实跑 `run realtime_snapshot_incremental` 复现写失败（属写操作，越只读红线）。
- **待裁**：根因是"registry 键→表名解析错位"还是"CH INSERT 权限/降级未回灌"——需一次带插桩的落地复现（要授权，且改前须 claim）。

## 处方与复现命令（全部只读）
```
# 5.1 落库真值（应 >0，实测 0）
python -c "from zephyr.data import ch_writer as c; print('rows=',c.query('SELECT count() FROM c1_market.realtime_snapshot FORMAT TSV'))"
# 5.2 任务态自相矛盾：SUCCESS 但表空
python -c "import sqlite3;c=sqlite3.connect('file:data/integrator_progress.db?mode=ro',uri=True);print(c.execute(\"SELECT started_at,status,rows_fetched,rows_written,error_msg FROM task_runs WHERE task_id='realtime_snapshot_incremental' ORDER BY started_at DESC LIMIT 5\").fetchall())"
# 5.3 降级失败件证据
ls data/failures/ | grep -c realtime_snapshot
# 5.4 registry 键→表名解析核对（判是否写错面）
python -c "from zephyr.data.table_registry import get_registry; print(get_registry().table('market_realtime_snapshot'))"
```
处方（待授权，勿自裁）：① 修 `task_runs` 判定——`rows_written` 应取 CH 实际 INSERT 回执而非 fetch 计数，写失败/降级须记 FAILED 或 DEFERRED_PERSISTENCE；② 确认回灌腿覆盖本表；③ 若 5.4 解析非 `c1_market.realtime_snapshot`，纠正 registry 映射（改表名须触发 depgraph，见宪法 §9.10）。
