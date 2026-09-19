---
ttl: task_bound
completes_when: X-2 后半施工按本卡 merge 完成、验收红证与 RB 复核登记后，本卡归档
---

# X-2 前半：复权链修复预注册卡（方案，未施工）

- 会话: st-final3-20260919 ｜ 日期: 2026-09-19 ｜ 状态: **待【M】Max 复验，禁止直接施工**
- 依据: 终极令 X-2（原"归整改队"禁令由本战役承接解除）；本卡=施工前预注册，后半由另一代理按本卡施工
- 实测环境: Python 3.12.8，process_reaper 存活（last_run=2026-09-18 19:10:55）；DB 读取全走 `DatabaseService.get_clickhouse_conn()`，plain MergeTree 查询未用 FINAL
- 证据等级: 病根代码行=直接证据（本日实读）；DB 数字=直接实测（本日）；akshare 接口=本机实测（网络行为随时间可能变化，标注于 §5）

---

## 1. 病根证据（三处，全部本日实测）

### 1.1 回测读侧：表名错 + 复权列缺失（`src/zephyr/backtest/core/data_handler.py`）

注意：病灶文件实际位于 `src/zephyr/backtest/core/`（非 `src/zephyr/data/`）。

```python
# L335 (BacktestDataHandler.from_clickhouse 默认参)
table: str = "daily_kline",
# L380-385 SELECT 全文——只有 OHLCV+amount，无 adj_factor、无任何复权处理
query = (
    f"SELECT date, symbol, open, high, low, close, volume, amount "
    f"FROM {table} "
    f"WHERE symbol IN ({symbols_str}) "
    f"AND date >= %(start)s AND date <= %(end)s "
    f"ORDER BY date, symbol"
)
# L389: query = ch_reader.inject_final(query)   # #ARCH-CH-007 自动 FINAL
# L560 (MultiSourceDataHandler.__init__ 默认参)
table: str = "daily_kline",
```

- 库实测：`system.tables WHERE database='c1_market' AND name='daily_kline'` → **count=0，表不存在**。默认参调用必抛 `DataHandlerError("ClickHouse 查询失败")`；即使调用方显式传对表名，读出的也是**不复权原始价**。
- 真实表名：`c1_market.kline_daily`（`table_registry.py` L140 示例全限定名；akshare_provider L222 `_TBL_KLINE_DAILY = get_registry().table("market_kline_daily")`）。`daily_kline` 在仓库其他位置均为**调度批次名**（scheduler.py/catchup_guard.py），非表名——本病灶是回测库把批次名误用作表名。
- 调用面（本日全仓 grep）：`from_clickhouse`/`MultiSourceDataHandler` 在 src+tests 内仅 `tests/backtest/test_tick_replay_data_handler.py` 与 backtest 库自身引用；生产策略线（pf_core `translated_strategy_adapter.py`、`regime_feature_builder.py`）走 `kline_daily_hfq` 已复权表，**不在本病灶弹道内**——故修读侧默认值+取数是低爆炸半径动作。

### 1.2 写侧：kline_daily.adj_factor 恒 1 的两处硬编码

```python
# src/zephyr/data/implementations/tushare_provider.py L946（A股主源）
1,  # adj_factor：不复权（对齐 kline_daily 主口径）
# L964 docstring: 不复权 adj_factor=1、data_source='tushare'、quality_flag=1。

# src/zephyr/data/implementations/akshare_provider.py ~L9288（BJ 备源路径）
1,  # adj_factor：不复权
```

即：kline_daily 的**两个写者都硬编码 adj_factor=1**，该列从无真实生产者。库实测（§1.3）与 2026-08-19 #198 实证（"全表 9,659,286 行恒 1"，akshare_provider L237 注释）一致，行数增长到 10,086,669 后仍然恒 1。

### 1.3 库实测（2026-09-19，无 FINAL）

| 表 | 引擎 | 行数 | 日期范围 | 关键实测 |
|---|---|---|---|---|
| c1_market.kline_daily | ReplacingMergeTree | 10,086,669 | 1990-12-19..2026-09-18 | 5,912 symbols；**adj_factor 列存在**（Nullable(Decimal(18,8))），non1=0，NULL=0，min=max=1 → **恒 1 实锤** |
| c1_market.adj_factor | ReplacingMergeTree | 21,054,931 | 1990-12-19..2026-09-18 | 7,848 symbols；non1=18,200,675（86.45%）；按 data_source：bdpan 18,751,261（≤2026-07-03 停更）/bdpan_etf 1,417,324/bdpan_lof 840,650/local_adj 44,688/**miniqmt 1,004 行 980 symbols（2026-07-01..09-18，仅事件日）**/akshare 仅 4 行 |
| c1_market.kline_daily_hfq | ReplacingMergeTree | 8,406,666 | 2019-01-02..2026-09-18 | 5,221 symbols；后复权价已有 2019+ 覆盖 |

adj_factor 独立表的**口径分裂**（样本实测）：
- bdpan=**累计因子**：000001 @2026-06-30 = 139.008；
- miniqmt=**单次事件点因子（dr）**：601838 @2026-09-18 = 1.025349，603757 @2026-09-18 = 1.001509。
- 两种口径**不可直接混算**（#217 注释已明示；点因子=cum(t)/cum(t-1)）。

### 1.4 akshare 接口可得性（本机实测一次，2026-09-19）

| 接口 | 结果 |
|---|---|
| `ak.stock_zh_a_daily(adjust="hfq-factor")`（新浪） | **可用**。601838 返回 12 事件行（最新 2026-09-18 cum=1.5279682）；000001 返回 32 行（最新 2026-06-12 cum=150.7260） |
| `ak.stock_zh_a_daily(adjust="qfq")`（新浪） | **可用**（下方互证数据即出自它） |
| `ak.stock_zh_a_hist`（东财，qfq/hfq/不复权） | **本机网络级封锁**（RemoteDisconnected；与 akshare_provider L9374 注释"东财接口反爬（本机 2026-08-24 实证网络级封锁）"一致）→ 验收红证**不得依赖东财** |

**三源互证（601838，2026-09-18 除权事件）**：
- 新浪累计比：1.5279682/1.4902701 = **1.02530**
- miniqmt dr：**1.025349**（相对差 ≈4.8e-5，舍入级）
- 新浪 qfq/raw 收盘比（09-10..09-17）：**0.9753 ≈ 1/1.02530**；除权日 09-18 起 ratio=1.000000
→ 点因子↔累计因子↔前复权价比 三条换算链全部实测闭合，验收方法论成立。

**风险型实测**：000001 累计因子 bdpan=139.008（06-30）vs 新浪=150.726（06-12 后）**差 8.4%** → adj_factor 独立表的 bdpan 段历史口径未经验证/不可作真源（详见 §6 风险 R3）。

### 1.5 现有治理链（修复必须兼容，勿推倒）

- **#198**（2026-08-19）：stk_limit 弃 kline_daily.adj_factor 列（恒 1 已废弃语义），改读独立表。
- **方案D**（2026-09-09 Owner 立项，长城任务）：stk_limit 修正源改 `c3_fundamental.ex_dividend_event`（QMT get_divid_factors，全历史 dr 事件），SQL 取 1/dr 输出当日除权乘子（无事件日=1）。
- **#217**：`normalized_market_data_producer/producer.py` `_SQL_LOAD_KLINE` 已实现标准读侧范式：`kline_daily LEFT JOIN (SELECT symbol,trade_date,any(adj_factor) dr FROM c1_market.adj_factor WHERE data_source='miniqmt' …) USING(symbol,trade_date)`，`1/dr AS adj_factor`。
- **#209②**：akshare hfq fallback 写侧守卫——adj_factor 表 ReplacingMergeTree(ingest_ts)、ORDER BY(symbol,trade_date) 不含 data_source，**同键后写静默顶替**，故 akshare 累计口径写前查 miniqmt 已覆盖键跳过。
- **BRK-034/BRK-043**（2026-09-18，st-ff-datagap-20260918）：ReplacingMergeTree 无 version 列，**多写者同表时任一写者整窗重灌会把它不拥有的列写成默认值（NULL/0）并在合并仲裁中胜出**——这是"历史重写 vs append"决策的决定性约束。

---

## 2. 修复方案（推荐案）

### D0 读侧修复（backtest/core/data_handler.py，纯读侧零写入）

1. **表名修**：两处默认 `table: str = "daily_kline"`（L335/L560）→ 改走真源 `get_registry().table("market_kline_daily")`（即 c1_market.kline_daily）；保留入参覆盖能力。禁止裸写字符串字面量新默认值。
2. **adj_factor 取数**：SELECT 增补点乘子列，**沿用 #217 范式**（JOIN ex_dividend_event 为首选真源，见下），产出列名建议 `adj_factor`（当日除权乘子，无事件日=1）；`pd.DataFrame(columns=[...])` 列清单同步增补。连带核对 df 消费方（get_bar 等）按列名取值不受列序影响。
   - **真源选择**：A=`c1_market.adj_factor`（data_source='miniqmt' 点 dr）→ 仅覆盖 2026-07+ 事件，前复权全史不足；B=`c3_fundamental.ex_dividend_event`（方案D，QMT 官方 dr 全历史）→ 全史覆盖。**推荐 B 为主**（与 stk_limit 现行真源一致，单一事实源），A 作 2026-07+ 增量交叉验证源。
   - Decimal 坑沿用 #198 配方：`1 / toFloat64(dr)`，float 域除法（Decimal 域除法会 scale 越界 overflow）。
   - JOIN 写法沿用 USING 无别名形态（ch_reader.inject_final 在表名后注入 FINAL，"FROM t FINAL alias" 非法，#198 实测 USING 形态合法）。
3. **不改 OHLC 原值语义**：from_clickhouse 输出仍以原始价为主列、adj_factor 为附属列；复权价由消费方（或 handler 提供的 helper）用乘子**前向连乘**得到，避免本 commit 内隐式改变所有既有下游的数值行为。

### D1 回填策略：**否决全量重算，采纳"独立表真源 + 增量 + 读侧重算窗口"**

- **否决**：对 kline_daily 10.08M 行整窗重写 adj_factor 列。理由：(a) 违反生产表 append 纪律；(b) BRK-034 实证整窗重灌在 ReplacingMergeTree(ingest_ts) 仲裁下会把整行其他列（open…quality_flag 等"不拥有的列"）写成默认值并**胜出**——该风险已有真实事故（index_valuation_daily 2026-09-13 cape/pe_pct 全抹 NULL）；(c) kline_daily 写者众（tushare/miniqmt/akshare-BJ/…），加"全史复权回填写者"必然进入仲裁混战。
- **采纳**：
  1. kline_daily.adj_factor 列语义维持 #198"废弃、恒 1"现状，**不回填历史**；文档注释锚定本卡。
  2. 复权真源=事件体系：`c3_fundamental.ex_dividend_event`（全史 dr，方案D）+ `c1_market.adj_factor`（miniqmt 增量 dr，2026-07+）。两者已是持续生产状态，**无需新回填**。
  3. 读侧按查询窗口现算乘子（JOIN），历史"重算"永远即时、零物化。若未来确需物化（性能），走**新表**（如 c1_market.kline_daily_qfq 影子表，由单一写者全权拥有），从 kline_daily+hfq 生成——不在本 X-2 施工范围，登记为后续可选项。
  4. **增量约定**：今后任何向 kline_daily 写 adj_factor 的新写者，只允许 append 当日/增量行且 carry-forward 全列（BRK-034 配方），禁止整窗重灌。
- **hfq 路径并行可用**：2019+ 后复权价已有 `kline_daily_hfq`（5,221 symbols），回测若只需 2019+ 可直接用它做第二实现参照（不替代 D0）。

---

## 3. 验收红证方案（修后必做，抽样 N=20）

1. **抽样结构**（20 只）：10 只 2025-2026 有除权事件（须含 601838 类近期事件股、含 1 只 10 送 N 高送转）+ 5 只长期无事件股（乘子应恒 1）+ 5 只 2015 年前上市且历史多次除权的老股（覆盖 ex_dividend_event 深史段）。
2. **前复权价红证**：修后 from_clickhouse 输出乘子连乘所得前复权 close vs `ak.stock_zh_a_daily(adjust="qfq")`（新浪，唯一可用 qfq 源）逐日比对，除权事件 ±10 日窗口内 `|ratio-1| < 1e-3`（新浪价 2 位小数，误差预算 0.1%）；无事件股全窗口 ratio=1。
3. **事件日三源互证**：ex_dividend_event.dr vs miniqmt dr vs 新浪累计比（cum(t)/cum(t-1)），相对差 `< 5e-4`（本卡 §1.4 实测 601838 为 4.8e-5，余量充足）。
4. **红证反例（先于修复跑）**：修复前同抽样代码必须失败（表名不存在抛错）或复权比对 ratio 在事件日跳变 > 阈值——证明验收真能拦住病态，防"恒绿测试"。
5. **禁依赖**：东财 stock_zh_a_hist 本机封锁，验收脚本不得调用；新浪失败时验收阻塞（不降级放行），记录后改期。
6. 全部验收输出写 `tmp_path`/`.runtime/tmp/`，禁写 `data/` 生产路径（测试隔离红线）。

## 4. 回滚方案

- D0 为纯读侧（默认表名+SELECT 增列）单 commit：**revert 即回滚**，无数据副作用、无不可逆操作。
- 本卡方案不含任何 DDL/历史重写；若施工代理超范围触发了 kline_daily 历史改写：立即停手，按 RULE-DATA-OPS 三步验证申报 Owner，回滚依赖该写者的逆行补写（ReplacingMergeTree 无原地回退），并在事故台账登记——故 §2 D1 的否决项是硬边界。
- 回测消费方灰度：修复 merge 前先在单一回测入口验证 §3 抽样通过；异常时 flag 关闭新取数列（消费方按列名取，缺列=旧行为）。

## 5. RB 复核优先序（修后重算复核，X-2 后半施工完成即触发）

1. **塔形顶空头**（`src/zephyr/signal_ashare/strategy_signal/candlestick_scanner.py`）——形态对除权假跳空最敏感，最先复核；
2. **塔形底 / 双底**；
3. **R 幅度**；
4. **S8**；
5. **ETFT0 rv20**；
6. **F / MID 池**。
复核口径：修后复权链下重跑信号，对比修前输出差异清单；差异集中于除权日附近的为**预期修正**，远离除权日的差异须逐一归因。

## 6. 风险清单

| # | 风险 | 等级 | 对策 |
|---|---|---|---|
| R1 | 整窗重灌抹列（BRK-034）：任何"回填 kline_daily.adj_factor 历史"的实现都会在 ReplacingMergeTree 仲裁下毁掉整行其他列 | 高（事故级，已有先例） | §2 D1 硬否决全量重算；施工代理越线即停 |
| R2 | 口径混算：bdpan 累计 vs miniqmt/ex_dividend_event 点 dr 直接相乘/比较 | 高 | 点↔累计换算必须显式（cum(t)/cum(t-1)）；读侧 SQL 固定单一 data_source 过滤（#217 范式） |
| R3 | bdpan 历史不可信：000001 bdpan=139.008 vs 新浪=150.726 差 8.4%（本卡实测） | 中高 | bdpan 段仅作交叉验证素材，不作真源；真源=ex_dividend_event（全史）+miniqmt（增量） |
| R4 | ex_dividend_event 深史覆盖未独立验证（1990-2015 段） | 中 | 验收抽样含老股（§3.1）；若深史缺口，红证不通过即回滚并登记数据缺口，不得放行 |
| R5 | qfq 验收源单点依赖新浪（东财封锁） | 中 | 新浪失败=验收阻塞不降级；备选第二参照=kline_daily_hfq 内部一致性（非官方源，仅辅助） |
| R6 | from_clickhouse 列序/列数变化破坏既有消费方 | 中 | 按列名取值核对；全仓调用面当前仅 tests/backtest 一处（§1.1），施工时再 grep 一次防漂移 |
| R7 | Decimal 域 1/dr overflow（#198 已踩） | 低 | 沿用 toFloat64 配方 |
| R8 | FINAL 注入语法（JOIN 别名形态非法） | 低 | 沿用 USING 无别名形态（#198 CH 实测合法） |
| R9 | akshare hfq fallback（独立表 data_source='akshare' 仅 4 行）与 #209② 守卫的口径顶替风险复发 | 低 | 本方案不新增该路径写入；后续若启用 hfq fallback，守卫（L8894 起）必须保留 |

## 7. 施工边界（后半代理必读）

- 只动：`src/zephyr/backtest/core/data_handler.py`（表名默认值+SELECT 增列+列清单）+ 新增验收脚本（tests/ 或 .runtime/tmp，红证脚本随施工 commit 走 tests/ 豁免通道与否按 CREATE-GUARD 现行规则）。
- 禁碰：kline_daily/adj_factor/ex_dividend_event 任何写路径与 DDL；`apply_market_tables_ddl.py`；tasks.yaml；他会话在途件。
- 施工顺序：红证反例（修复前失败证据）→ D0 修改 → §3 红证 → §5 RB 优先序触发复核登记。
