---
ttl: task_bound
completes_when: 全流通战役 FF-01 数据缺口簇收口且总包复核签字
---

# datagap 车道 · 数据腐败坏行清单与处置（BRK-034 / BRK-035 / 新增发现）

> 车道 `st-ff-datagap-20260918`（总包 `st-fullflow-20260918`）｜2026-09-18 实测
> 判据：宁可缺一个数，不可有一个错数（R-014 同源）。处置序：**止血 → 清创 → 补数**。
> 本车道全程只读推演，**未执行任何 DELETE / TRUNCATE / ALTER / OPTIMIZE**
> （破坏性 DB 操作三步验证之"可逆性"未获备份支撑，且存量处置属 Owner/总包门位）。

## 0. 一句话结论（普查 vs 实测）

| 普查断点 | 普查记载 | 2026-09-18 本车道复跑实测 | 判语 |
|---|---|---|---|
| BRK-034 | 同键双行并存，下游读到不确定行 | 双行**已不存在**：pre-FINAL 8125 = FINAL 8125，按 (symbol,trade_date) 分组 count>1 命中 **0 组**，全字段 GROUP BY ALL HAVING count()>1 命中 **0**（RULE-DATA-OPS 禁聚合判重，已按全字段口径）；病灶已恶化为**计算列整表归零**：cape_5y / cape_5y_pct / pe_pct / pb_pct / erp / erp_pct / pb_mrq **NULL 8125/8125 = 100%**，覆盖 2010-01-01~2026-09-17 全史，000300 4062 行 + 000905 4063 行 | 普查表述**已失效**，真实缺陷**更严重** |
| BRK-035 | 243 组 ts_code 撞码静默污染，最难发现 | 库内**已无污染行**：pre-FINAL 30574 = FINAL 30574 = uniqExact(ts_code,trade_date) 30574；2026-06-30 快照 4065 行 / 4065 唯一 ts_code（撞码 0 组）。拦阻件在位：`northbound_hold_fetcher.py:154 _resolve_code_collisions`，调用点 `:232` | 普查**已失效**（台账 monitoring 是对的）；残余缺陷见 §3 |
| 新发现 N-1 | 普查无载 | `c1_market.daily_valuation` FINAL **259238 行**，`close!=0` / `amount!=0` / `turnover!=0` 命中 **0 行**（0.00%），全表跨 2026-08-01~2026-09-17；且 09-16/09-17 各仅 2000 行（又一次部分写入） | **错数据进闭环**，比缺数据危险，须裁 |
| 新发现 N-2 | 普查无载 | 同一表 `ps_ttm` 列写入的是 akshare 指标 **"市盈率(静)"**（`akshare_provider.py` 指标映射处自述"AKShare 无 PS，用静态PE替代"）；`data_source` 因 DDL DEFAULT 恒为 **local_valuation**，而真实写者是 akshare 百度估值链路 | 出处标注失真 + 列名与值不符 |

## 1. BRK-034 止血（已落地代码）

* 结构性根因：`c1_market.index_valuation_daily` 是
  `ENGINE = ReplacingMergeTree PARTITION BY toYYYYMM(trade_date) ORDER BY (symbol, trade_date)`，
  **无 version 列**。该表有两个写者：
  ①`akshare_provider._fetch_index_valuation_daily`（只采 pe_ttm/股息率，计算列一律置 None）；
  ②`internal_compute`（`index_valuation_compute.IndexValuationComputeProvider` 读库算
  CAPE/分位/ERP 后回写同表）。写者①在 `weekend_calibration` 档做**全史重灌**
  （`incremental=False → start=2010-01-01`）时把 8111 个键全部以 None 重插；
  无 version 列时后到版本胜出 → 计算列被整体抹除。
  ingest_ts 分布实证：`2026-09-13 单日 8111 行`（其余日各 2-4 行），与"表被全史重写一次"吻合。
* 治法（裁定 #288 `stock_indicator` 同款配方，provider 层，本车道独占面）：
  写前一次性读回同表既有非默认派生值（`_SQL_PRESERVED_VALUES`，带 FINAL、
  带"计算列非空"谓词、标的数 ≤200 时按 symbol 收窄），把值携带进新版本行的 None 槽位；
  本能力自采的非 None 值优先，不被库中旧值覆盖；探值读失败降级为不携带（不阻断采集）。
* 能红证据：注释掉携带调用 →
  `tests/zephyr/data/test_akshare_index_valuation.py::TestValuationCarryForward::test_full_refresh_carries_forward_computed_columns`
  红（`assert None == 31.05`）；恢复后该文件 11 passed，邻接回归
  `test_akshare_adj_factor_guard` + `test_a50_futures_daily` 18 passed、
  `test_capability_validator` + `test_data_scheduler` 87 passed。
  测试全程 monkeypatch `ch_reader.query`，禁触库禁写 `data/`。

## 2. BRK-034 清创与补数（交总包/Owner 决断）

* **清创不需要 DELETE**：现状不是"坏行混在好行里"，而是"全部行都缺派生列"。
  删行只会把唯一的 pe_ttm 真值也删掉 → 存量处置=重算回写，不是隔离删除。
* 补数（待执行，体积已估）：先 `python -m zephyr.data run index_valuation_daily_backfill`
  （akshare 主源，携带逻辑已在位，不会再抹计算列），
  随后**必须**跟一次 internal_compute 回写 CAPE/分位/ERP（任务片段见
  `lanes/datagap_tasks_yaml_fragment.yaml` 第 4 条）。
  体积：8125 行 / 2 symbol × 全史，CAPE 计算窗口 1250 交易日（约 5 年），分钟级；
  依赖 CPI 序列与 10Y 国债收益率（`_load_cpi_series` / `_load_bond_10y_series`）。
  注意 399006（创业板指）中证官网无此品种、接口恒空（provider 聚合模式注释已实证）。
* 机械核查（只读，本车道已跑）：

  ```sql
  SELECT data_source, count() AS n, countIf(cape_5y IS NOT NULL) AS has_cape,
         countIf(pe_pct IS NOT NULL) AS has_pepct, countIf(erp IS NOT NULL) AS has_erp
  FROM c1_market.index_valuation_daily FINAL GROUP BY data_source;
  -- 2026-09-18 实测：akshare_csindex 8125 / 0 / 0 / 0
  ```

* 回滚预案（**未执行**，仅登记可逆性）：本条无删除动作；
  回滚=revert provider 携带逻辑那一个 commit，携带读失败自动降级为旧行为，无残留状态。

## 3. BRK-035 残余缺陷（⑥失败会响未闭合）

* 数据面已干净（§0 实测），fetcher 的 code 自洽判别在位（组内恰好 1 行自洽 → 保留真主行、
  剔除入侵行；判别失效 → 整组剔除，宁缺毋错）。
* **未闭合项**：台账 `tushare_hk_hold_2026q2_code_collision.resolution_plan` 自述
  "若判别失效组数 >0 需告警复查规则"，实测 `northbound_hold_fetcher.py` 只返回
  `(df, _salvaged, _dropped)` 计数，调用点 `:232` **未消费该计数做任何门位/告警**
  → 撞码判别一旦失效会**静默整组丢数据**（丢的是真主行，表上看不出异常）。
  登记为治理需求（建议归 z-failopen 的 DLQ/告警面，与 BRK-054 同批）。
* 核查 SQL（只读）：

  ```sql
  SELECT trade_date, count() AS rows, uniqExact(ts_code) AS uniq_code,
         rows - uniq_code AS collision_rows
  FROM c1_market.northbound_hold_snapshot FINAL GROUP BY trade_date HAVING collision_rows > 0;
  -- 2026-09-18 实测：0 行输出（含 2026-06-30）
  ```

## 4. 新发现 N-1/N-2（daily_valuation）——需总包裁定，本车道只出止血与需求

* 止血已落地：行情腿携带（同 §1 机制，谓词 close/amount/volume/turnover 非零）
  + 宽窗重采幂等/断点续跑（跳过已到窗口最新事实日的标的），防"再花 11 小时又中断"。
* 待裁三选一（任一都涉及 schema 或新链路，非 provider 层能单独定）：
  A) 9 个行情腿列改 `Nullable`，让"无值"不再伪装成 0（DDL 变更，需 admin 角色 + DDL 真源同步）；
  B) 行情腿改由 `kline_daily` 同步行填（daily_valuation 本就是"行情+估值"复合表语义）；
  C) 明确该表只作估值表使用，把行情腿从表与 INSERT_COLUMNS 中摘除（注册表净删列=Owner 门位）。
  现况：`api_server.py:206` 已注明"daily_valuation 价格列全 0 不可用（2026-09-01 实测）"、
  `:265` "turnover 全 0 暂无真源→None"，消费侧已在规避，故不阻断他人。
* **判据落点**：0 是被写进闭环的**错数**（下游任何 amount/turnover 权重公式会得到 0 或除零）。
  台账 `daily_valuation_2026_09_10_missing` 已记"金融字段消费近期此表一律禁用"，
  但**禁用靠人自觉、无机械闸**——这正是 R-014 / BRK-054
  （`flags.schema_validation`: strict_mode=false + dlq_enabled=false + runtime drift 未实现）
  缺位能持续的直接后果：**不补 DLQ，本簇修完仍会复发**。

## 5. 破坏性 DB 操作三步验证记录（RULE-DATA-OPS）

| 步 | 结论 |
|---|---|
| 必要性 | 034/035 均**不需要删行**（034=重算，035=源头已拦阻）；N-1 是写侧口径问题，删行无意义 → 本车道零删除动作 |
| 真实性 | 每条判据都给了可复跑只读 SQL + 实测数字（§0/§2/§3）；判重按全字段 GROUP BY（禁聚合数，与 `scripts/governance/data_quality/check_tick_duplication.py` 同口径；该脚本本体是 tick_data 14 字段专用，故本表按其口径另写等价查询） |
| 可逆性 | 唯一落地变更=provider 携带逻辑（纯代码，revert 即回滚，无状态残留）；无备份 = 不执行任何删除，符合"无备份禁执行" |
