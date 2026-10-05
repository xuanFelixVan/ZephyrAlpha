---
ttl: task_bound
---

# lane_pipe · reconciliation_differences（盘后三方对账差异链 / 做T对账）— 判定：不通 ❌（可观测性 + 真源方向分裂）

## 六向台账

### 1 做什么
盘后跑结算/持仓/成交三方对账（SettlementReconciler/PositionReconciler/DailyAuditor），把差异 append-only 落 `reconciliation_differences`，供对账审计/告警消费。是任务点名"做T矩阵单写者"病灶族的业务面入口之一。

### 2 依据
- 写入方在册：`src/zephyr/trading/recon_runner.py:22` "差异写 reconciliation_differences 表（**governance.db**，append-only）"；L117 `INSERT INTO reconciliation_differences`；L82/L447 db_path 默认走 `DB_PATH` SSoT（`data/databases/governance.db`，duckdb）。
- DDL 在册：`src/zephyr/reporting/reconciliation_schema.py:42`。
- 触发在册：计划任务 `ZephyrAlpha_PostSettlement`（周五 15:30），LastRun=2026-09-25 15:30。
- **同时存在同名 ClickHouse 表** `c1_market.reconciliation_differences`（ReplacingMergeTree，ORDER BY trade_date,recon_layer,trade_id,symbol,drift_type,detected_at）。
- `api_server.py:1484` 把 `reconciliation_differences` 映射为展示项"对账差异"（读点）。

### 3 改动点（候选，不改）
- 真源方向分裂：governance.db（写入端正源）vs c1_market（ClickHouse 同名表）——谁是消费读源未锁；违反 RULE-SSOT 单一真源。
- 若 dashboard 读 CH 表而 recon 写 governance.db，则"对账差异"页恒空（探针读空被当"无差异"，病灶 C）。

### 4 判据
① 单一真源明确；② 能从"差异表空"区分"对账干净" vs "对账从未跑成"（须有运行留痕/心跳，非仅行数）。

### 5 读数（实测·只读）
- CH `SELECT count() FROM c1_market.reconciliation_differences` → **0**。
- governance.db（duckdb read_only）`SELECT count(),max(detected_at) FROM reconciliation_differences` → **0 · None**。
- 两库同名表**皆空**；无法据行数判 recon 是否跑过。
- 关联证据弱：`c1_market.execution_report` 仅 **1 行 · 2026-09-18**（实盘/结算产出面近乎停摆，见 `lane_pipe_auto_runtime_trading.md`）。

### 6 风险
- "对账无差异"是强安全断言；当前**空即歧义**（clean vs never-ran 不可辨），若 recon 静默失败则资损/持仓漂移漏检。
- 真源双表 → 修数据可能只补一库、消费读另一库。

## 自审三态
- **PASS**：两库空由独立 SELECT 确证（CH + governance.db duckdb read_only）；写入方/DDL/读点/计划任务给到文件级锚点；未臆断"应有多少差异"。
- **FAIL（未做）**：未查 recon_runner 实际被谁调用、PostSettlement 脚本内是否真触发三方对账并写 governance.db（只读脚本可达，本轮按预算列下一步）。
- **待裁**：真源收敛（保留 governance.db 删/视图化 CH 同名表，或反之）属结构处置 + 注册表净删 = **Owner 门位**（宪法 §5.2），本轮不自裁，仅登记。

## 处方与复现命令（全部只读）
```
# 5.1 双库皆空确证
python -c "from zephyr.data import ch_writer as c; print('CH=',c.query('SELECT count() FROM c1_market.reconciliation_differences FORMAT TSV'))"
python -c "import duckdb;con=duckdb.connect('data/databases/governance.db',read_only=True);print('GDB=',con.execute('SELECT count(),max(detected_at) FROM reconciliation_differences').fetchone());con.close()"
# 5.2 消费读哪库
grep -rn "reconciliation_differences" src/zephyr/frontend/dashboard/api_server.py src/zephyr/reporting | head
# 5.3 触发链是否真跑
cat data/runtime/post_settlement_last_run.log 2>/dev/null | tail -20
grep -rn "recon_runner\|reconcile_diff\|write_reconciliation\|reconciliation_differences" scripts/run_post_settlement.py 2>/dev/null
```
处方（待授权）：① 定 reconciliation_differences 唯一真源并消歧（Owner 门位）；② 给 recon 落"运行心跳/最近成功时间"尺，令"空表=干净"可证；③ dashboard 读点对齐真源库。执行侧改动 + 实跑对账需授权并走 claim。
