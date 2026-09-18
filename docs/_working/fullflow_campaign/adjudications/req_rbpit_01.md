---
ttl: task_bound
completes_when: 总包对本文件四项申请逐条出裁定号（车道不自取号）
---

# 裁定申请书 req_rbpit_01 · 红队 PIT/复权 车道四项判不动或需授权项

车道 = `st-ff-rb-pit-20260918`（红蓝对抗车道，攻面=PIT 泄漏 + 复权口径）。
证据与处方正文见 `lanes/rbpit_prescriptions.md`（F-01 已修，P-01~P-07 未修）。
本文件只提**车道无权自行落地**的四项，按 §4 协议请总包取号裁定。

---

## A1 · `c1_market.kline_daily` 系 ReplacingMergeTree **无版本列**（申请：数据面 DDL 排期，Owner 门位）

- 实测：`system.tables.engine_full` 中 `c1_market.kline_daily` = `ReplacingMergeTree`
  （无 `(ingest_ts)` 参数），`kline_daily_hfq` 同；而 `c1_market.adj_factor` 是 `ReplacingMergeTree(ingest_ts)`。
- 为什么这是 PIT 问题而不是卫生问题：无版本列时 **FINAL 保留哪一行由 merge 顺序决定，规范上未定义**。
  现网已能观测到同键两行值不等：2026-09-17 有 904 键重复、56 键 close 不等、903 键 volume 相差 100 倍
  （Baostock 写股数 vs 主进料写手数），两版 `quality_flag` 都是 1 ⇒ 质量过滤挡不住，
  带 FINAL 的路径也只是"碰巧"留了后写的那版（实测 `002321` 留下的是 531,324 手）。
- 选项：甲=全系补版本列（`ALTER ... REPLACE` 重建，亿行级，需备份+回滚方案）；
  乙=只在读侧强制 `argMax(col, ingest_ts)` 定标（本车道 F-01 已按此写法落地，可作模板）；
  丙=先补 P-01 的 gate（禁止无 FINAL 直连读），把 DDL 排到战役后。
- **建议**：丙 + 乙并行（甲属资金/数据破坏性面，须 Owner 门位与备份方案，本车道未跑任何 `--execute`）。

## A2 · 价格口径分域契约（申请：`architecture_model/contracts/**` 属 PROTECTED-PATHS，需 Owner 授权）

- 现状实测：复权族出口 = `factor/core/evaluation/backtest.py load_history` →
  `shared/utils/market_units.normalize_market_panel`（窗口末锚定复权价）；
  不复权族 = `signal_ashare/**`、`plan_engine/**` 82 处直读 `kline_daily.close` 原始价；
  两族同时进 `pf_core`（`strategies/daban_sleeve_strategy.py:63-75` 与
  `strategy_engine/strategy_runner.py:369`）⇒ 同体系两口径，**无契约、无 gate**
  （`gate_registry.yaml` 内 "复权" 关键字命中 0 处）。
- 申请：授权在 `architecture_model/contracts/` 立一份"价格口径分域契约"，二选一定死：
  ①行情读取唯一出口 = `normalize_market_panel`（则 signal_ashare 须改造，工作量大）；
  ②信号层一律不复权、收益层一律复权（则须显式写清并给换算件）。
- 本车道立场：在契约落地前，**不替全仓选口径**，只把已实证的错口径位点（F-01 已修、P-03 处方）逐条钉住。

## A3 · CH-FINAL-GATE 扩容的作用域与存量 82 件处置（申请：门禁面决策）

- 判据源：`src/zephyr/gov_enforcement/commit_gates/ch_final_gate.py:60`（只匹配 `ch_writer.query(`）。
- 请裁：新增"直连 execute 读 Replacing 表且无 FINAL"判据时，
  ①是否只查本批新增行触及的 SQL 常量（own-diff，存量 82 件不连坐）；
  ②存量是否走 `lanes/rbpit_prescriptions.md` 的 owner 分配逐车道消化，还是登记为一次性豁免批。
- 规范预算声明：本申请是**并入既有 gate_id=CH-FINAL-GATE**（不新增 gate 条目，净零增长），
  合并掉的旧判据 = 无（只增维，不减）。
- 若总包同意，本车道可在下一批提交 gate 扩展 + 自家能红测试（含反向变异）。

## A4 · 盘中 L1 判定的"盘中"定性（申请：改判据还是改供数，二选一）

- 实测：`c1_market.kline_etf_5min` 2026-09-18 全天 48 根 bar 的 `ingest_ts` 同为北京 15:49:53
  （收盘后一次批量入库）；`plan_engine/intraday_l1_tracker.py:477-479` 当日无 bar 即 `return None`
  ⇒ 所谓"盘中五态判定"在会话内结构上无法触发。
- 请裁：甲=把 ETF 分钟供数改盘中增量（真治本，属数据面排期）；
  乙=把该能力从"盘中"改标"EOD 复盘"，并同步改六向台账①向新鲜度判据与前端措辞。
- 本车道不选：措辞降级 = 为降噪放宽判据（违裁定#273 精神），但供数改造超出本车道权限。

---

## 复测命令（一条验真）

```bash
python -c "from zephyr.infrastructure.database_service import DatabaseService as D;c=D().get_clickhouse_conn(role='reader');\
print('engine:',c.execute(\"SELECT engine_full FROM system.tables WHERE database='c1_market' AND name='kline_daily'\")[0][0][:60]);\
print('2026-09-17 无FINAL/FINAL 行数:',c.execute(\"SELECT count() FROM c1_market.kline_daily WHERE trade_date=toDate('2026-09-17')\"),c.execute(\"SELECT count() FROM c1_market.kline_daily FINAL WHERE trade_date=toDate('2026-09-17')\"))"
```
