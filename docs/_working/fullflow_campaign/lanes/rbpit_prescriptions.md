---
ttl: task_bound
completes_when: 红队 st-ff-rb-pit-20260918 攻面一/攻面二的处方被总包逐条裁定并由 owner 车道落地
---

# 红队 PIT 泄漏 / 复权口径 车道 · 攻击成果与处方（st-ff-rb-pit-20260918）

> 职责=弄坏它，不是确认它能用。本文件只登记**本车道未修**的处方（撞他人独占面 / Owner 门位 /
> 需跨簇决策），以及已修的验收判据。所有数字均为 2026-09-18 本机 CH 只读实测（R-019：施工前复跑）。
> 表述禁令（裁定#325）：本文不出现"全绿/无泄漏"，只出现"检出 N 件 / 未检出 M 件（附覆盖面）"。

---

## 1. 已修（本车道闭环，一笔提交）

### F-01 · regime 复权腿把 LEFT JOIN 未命中的 0 当复权价用（真错口径，已修）

- 判据源（改前）：`src/zephyr/regime/regime_feature_builder.py:684-692`
  `k.close * ifNull(a.adj_factor, nan) AS close_hfq` + `LEFT JOIN {adj} AS a FINAL`（真源=`c1_market.adj_factor`）
- 三条实测根因：
  1. `c1_market.adj_factor` 日覆盖 2026-07-03 前 ~7,470 行 → **07-06 起 2~60 行**（bdpan 累计口径停更）；
  2. 服务端 `join_use_nulls = 0`（system.settings 实测）+ `adj_factor Decimal(18,8)` **非 Nullable**
     ⇒ LEFT JOIN 未命中返回**类型默认值 0**，`ifNull(a.adj_factor, nan)` **永不触发**
     （单行复现：`ifNull(0, nan) = 0`）；
  3. 同表混存 bdpan 累计因子与 miniqmt dr 点因子（Replacing 后写覆盖先写，无 data_source 过滤）。
- 后果实测（窗口 2026-01-05..2026-09-18，全市场 A_share quality_flag=1，959,185 面板行）：
  `close_hfq==0` 占 **303,817 行**、NULL **0 行**、收益越界(≤−100% 或 >500%) **7,400 格**；
  近 20 交易日 C1/C2/C3 **全 NaN**、C4 momentum_breadth **0.07%~0.51%**（复权真值口径 21%~63%）。
  旧日志按 `notna()` 统计覆盖率 ⇒ 把 0 计成"已覆盖" ⇒ **自我掩盖**。
- 修法：复权源改指 `c1_market.kline_daily_hfq`（`argMax(close, ingest_ts)` 逐键定标，免疫未合并重复行），
  `if(h.close_hfq > 0, h.close_hfq, NULL)` 显式 NULL 化；新增 `_assert_hfq_coverage` 失维绊线
  （近端 20 交易日覆盖率 < 50% → 抛 `RegimeFeatureError`，缺席日 WARNING 出声）。
- 验收判据：`tests/regime/test_cross_sectional_features.py::TestStockPanelAdjustmentSource`（5 件），
  且 `tests/regime` 目录 1029 件通过。
- **能红证据**（变异台 `.runtime/tmp/st-ff-rb-pit-20260918/prove_red.py`，4/4 转红 + 按字节还原 sha256 一致）：
  M1 零价算作已覆盖 rc=1 / M2 绊线未接线 rc=1 / M3 判据放宽到 0 rc=1 / M4 复权源改回塌缩专表 rc=1。
- 行为变更如实登记：面板窗口整体早于 2019-01-02 时（hfq 真源起点），绊线由"算出错特征"改为"硬失败"。

---

## 2. 处方（本车道未修，按 §3.4 owner 责任制移交）

### P-01 · 82 处生产读路径无 FINAL 读 ReplacingMergeTree，且 CH-FINAL-GATE 无牙 —— owner: instL（ch_reader.py）+ 门禁面

- 判据源：`src/zephyr/data/ch_reader.py:58-92`（`inject_final`）+
  `src/zephyr/gov_enforcement/commit_gates/ch_final_gate.py:60,144`（只匹配 `ch_writer.query(`）
  ⇒ 经 `DatabaseService.get_clickhouse_conn().execute()` 直连的 SQL **完全不过门禁**（实测门禁无该判据）。
- 活体复现（本机，2026-09-18）：
  ```bash
  python .runtime/tmp/st-ff-rb-pit-20260918/probe1.py    # 40 张表 FINAL 前后行数不等
  python .runtime/tmp/st-ff-rb-pit-20260918/probe4.py    # 生产 SQL 常量原文复现
  ```
  实测：`c1_market.kline_daily` 2026-09-17 当日 **无 FINAL 6,471 行 / 带 FINAL 5,568 行**，
  904 个 (symbol,trade_date) 键存在两版本，其中 **56 键 close 不等、903 键 volume 不等（相差 100 倍：
  53,132,359 股 vs 531,324 手，两版 quality_flag 同为 1 ⇒ 质量过滤挡不住）**；
  `kline_1min` 全表 **4,296,073** 重复行、`kline_etf_1min` 964,538、`kline_index_calc` 1,793（整表 2 倍）。
  生产位（抽样，完整清单见 `.runtime/tmp/st-ff-rb-pit-20260918/probe3.py` 输出）：
  `src/zephyr/signal_ashare/limit_up/limit_up_followthrough.py:67,79`（kline_daily/stk_limit，`:353-368` 直连 execute）、
  `src/zephyr/plan_engine/close_verifier.py:99,104,114`（kline_index/kline_etf_60min，经
  `judgment_settler.py:131-135 _reader_execute` 裸 execute）、`src/zephyr/data/sector_report_builder.py:120-177`、
  `src/zephyr/data/implementations/daban_board_event_deriver.py:552-733`、`src/zephyr/strategy_pipeline/fw_backtest.py:193`。
- 建议改法（择一或并用，均为加严不放松）：
  1. `ch_final_gate` 增判据：staged .py 内字符串常量含 `FROM <Replacing 表>` 且**文本内无 `\bFINAL\b`**
     且该文件不含 `ch_reader.query/query_table/count` 或 `inject_final` 载体 ⇒ 阻断（own-diff 作用域，
     只查本批新增/修改行触及的 SQL 常量，避免 82 处存量连坐）；表清单从 `system.tables` 取，不硬编码。
  2. 把 `_reader_execute`（`src/zephyr/plan_engine/judgment_settler.py:131`）内部改为
     `ch_reader.inject_final(sql)` 后再 execute —— 单点收口，覆盖 plan_engine 全族。
- 验收判据（能红）：对任一 A 类位点，用 `probe4.py` 同形脚本断言"无 FINAL 行数 > 带 FINAL 行数"；
  改后该断言必须红（即行数相等），并留 `git log -1 --name-only` 归属。
- 附注（同位不同病）：`ReplacingMergeTree` **无版本列**（`kline_daily.engine_full` 实测 =
  `ReplacingMergeTree`，无 `(ingest_ts)`）⇒ FINAL 保留哪一行由 merge 顺序决定，未成文保证；
  建议 DDL 侧登记为待裁项（加版本列属数据面破坏性操作，Owner 门位）。

### P-02 · `ch_reader.inject_final` 遇表别名产出非法 SQL，且 `query()` 把失败吞成空串 —— owner: instL

- 判据源：`src/zephyr/data/ch_reader.py:80-92`（替换为 `FROM {table} FINAL`，别名被顶到 FINAL 之后）+
  `:95-109`（失败返回 `''`，与"真无数据"同形）。
- 实测语法真值（本机 CH）：`FROM t FINAL AS k` → **Code:62 语法错**；`FROM t AS k FINAL` → OK。
  `ch_reader.inject_final("… FROM c1_market.kline_daily AS k INNER JOIN …")` 产物执行即 Code:62，
  `ch_reader.query()` 返回 `''`（长度 0）⇒ 调用方见"无数据"而非"查询失败"。
- 现状：全仓 `src/` 扫描**当前 0 处**触发（代码已普遍改用 `USING` 无别名写法，见
  `akshare_provider.py:249`、`producer.py:77`、`scenario_planner.py:138` 等 5 处注释自认此坑）
  ⇒ 属**潜伏**缺陷，护身符是口头约定不是门禁。
- 建议改法：`_replace` 识别 `FROM <tbl>(\s+AS\s+)?<alias>` 时改产 `FROM <tbl><alias 段> FINAL`
  （FINAL 置后），并在 `query()` 区分"查询失败"与"空结果"（失败上抛或返回哨兵，不得回 `''`）。
- 验收判据（能红）：新增 `tests/data/test_ch_reader_inject_final.py` 参数化 5 形
  （plain / `AS k` / 裸别名 / 子查询 / 已有 FINAL），断言注入产物可被 CH 解析；
  变异=把 FINAL 移回表名后 ⇒ 必红。

### P-03 · `index_eqw_compute` / `index_breadth_compute` 用死列 `kline_daily.adj_factor` 冒充复权 —— owner: 数据面（未在 §2 独占表内，建议总包指派）

- 判据源：`src/zephyr/data/implementations/index_eqw_compute.py:79`
  `toFloat64(close) * toFloat64(adj_factor) AS adj_close`（docstring 自称"严格复权版""全表零 NULL 已实测"）、
  `src/zephyr/data/implementations/index_breadth_compute.py:188` `ifNull(adj_factor, 1)`。
- 实测：`c1_market.kline_daily FINAL` 10,085,765 行，`uniqExact(adj_factor)=1`、`countIf(adj_factor!=1)=0`
  ⇒ **列恒 1，不复权**（与 `market_units.py:36-38` 车道 K 结论一致，至今未回补）。
- 后果（2025-09-01 起逐日逐票对拍后复权真值）：假"跌幅>9.9%"票日 **266**、假"跌>3%"票日 **502**、
  两口径日收益背离 >3pct 票日 **2,239**；单日涨跌家数最多虚增 39 只（2026-05-29 跌家 3,710 vs 真值 3,671）。
  下游闭环：`regime_feature_builder.py:578-628`（F4 广度 399106 断更时由 EQW_ALLA 补位）。
- 建议改法：两处 `adj_close` 改读 `kline_daily_hfq`（同 F-01 的 `argMax(close, ingest_ts)` 定标），
  或改指 `market_units.normalize_market_panel` 出口；并把 docstring 的"严格复权版"改成实测口径标签。
- 验收判据：`probe6.py` 的 `fake_gap99/fake_gap30` 计数在修后须=0（修前 266/502）。

### P-04 · `intraday_l1_tracker._A50_LAST2_SQL` 无 as-of 谓词（潜伏前视） —— owner: 判定链（plan_engine）

- 判据源：`src/zephyr/plan_engine/intraday_l1_tracker.py:163-166`
  `ORDER BY trade_date DESC LIMIT 2`（无 `trade_date < '{day}'`）；同文件 `:158-162` 的
  `_INDEX_PREV_SQL` **有**该谓词 ⇒ 同族两式一有一无。
- 现状：`latest_unemitted_bar()` 只走实时（`today=now`），A50 当日行实测 08:34 北京入库（早于开盘）
  ⇒ 当前不构成实际泄漏；一旦加补跑/回放路径即变前视。
- 建议改法：`_A50_LAST2_SQL` 加 `AND trade_date < '{day}'`，与 `_INDEX_PREV_SQL` 同形。
- 验收判据：新增测试——给 reader 注入"含未来日"的行集，断言 `_load_a50(day)` 不取 `>= day` 的行。

### P-05 · ETF 分钟线是**盘后一次批量入库**，盘中判定器无盘中料 —— owner: 数据供数面

- 实测：`c1_market.kline_etf_5min` 2026-09-18 全部 48 根 bar 的 `ingest_ts` 同为 `07:49:53 UTC`
  （= 北京 15:49:53，收盘后）；`intraday_l1_tracker.py:477-479` 在当日无 bar 时直接 `return None`
  ⇒ "盘中 L1 五态判定"在会话内**结构上无法触发**（`latest_unemitted_bar` 只在 15:49 后能找到当日 bar）。
  同时：`ingest_ts < trade_time`（形成中 bar 落库）实测 **0 行** ⇒ "禁 forming 中间态"这一判据
  在 kline_daily / kline_etf_5min 两表均成立（但**靠供数排期，无机械防护**）。
- 建议：要么把 ETF 分钟供数改为盘中增量（真治本），要么把该能力定性从"盘中"改为"EOD 复盘"
  并同步改六向台账①向的新鲜度判据；两选一都须登记，不许保留"盘中在岗"的措辞。

### P-06 · `analyst_forecast` 无 publish_date，只能拿 report_date 当可见性锚 —— owner: 数据源接入面

- 判据源：`src/zephyr/nlp/news_dual_tagger.py:78-83`（注释自称"PIT：report_date ≤ 数据日"）。
- 实测：`c3_fundamental.analyst_forecast` 列仅 `report_date + ingest_ts`（**无 publish_date**），
  101,808 行 `ingest_ts − report_date` 滞后分布 = 0 日 99,440 行 / **2 日 2,368 行**；
  且 report_date 覆盖仅 2026-07-22 起 ⇒ 2026-07-22 前跑回测取不到锚（`GAP_NO_ANCHOR`）。
- 结论：**当前未检出实质前视**（滞后 ≤2 日），但护身符是"akshare 恰好当天写"；
  一旦做历史回填（report_date 早、ingest 晚数月），该谓词立即变成前视闸门。
- 建议：接入 publish_date（altdataF 面）或改 `ingest_ts` embargo（≥2 交易日）双保险，
  并在 `SQL_CONSENSUS_ANCHOR` 注释里把"实测滞后 0~2 日"写进判据而非只写"PIT"。

---

## 3. 覆盖面矩阵（攻/未攻 逐格如实）

| 攻面一小项 | 状态 | 判据/结论位置 |
|---|---|---|
| ① 未复权价与复权价混用 | 攻 | F-01（混成 0 价）、P-03（死列冒充复权）、`market_units.py:44-48`（专表跨重定标 −68%~−84% 幻影，实测复核成立） |
| ② ingest_ts 当业务时间 | 攻 | 决策面未检出：`daily_plan.py:571`、`strategy_decay_certifier.py:100` 仅把 ingest_ts 作同日平手的 tiebreak；R-041 的 supply_sentinel 病位已由 z-sentinel 治 |
| ③ 公告日 vs 归属日 | 攻 | `pit_query.py:73,79`（announce_date 锚 + 1970 哨兵不可见）、`consensus_daily_repaired_compute.py:86-88`（publish_date）= 防护到位；`analyst_forecast` 无 publish_date → P-06 |
| ④ ETF 分钟线时区劈叉 | 攻 | **前提已被推翻**：现网 `kline_etf_1min`/`kline_etf_5min` 全史小时带 ∈[9,15]、UTC 带行数 **0**；备份表 `*_tz_bak_20260918` 内 UTC 带 **303,422,787 / 68,163,011** 行 ⇒ 修复已于 09-18 落地（instL），本车道未跑任何 `--execute` |
| ⑤ 指数分钟线缺表 → 510300 代理 | 攻 | `kline_index_intraday` 实测不存在（system.tables 全查）；代理基差属"值口径"不属"可得时点"，未见非 PIT 注入；残留问题记 P-05（盘中无料） |
| ⑥ FINAL+ORDER BY 最后一根 bar | 攻 | P-01（无 FINAL 直连读，活体 903 键冲突）、P-02（FINAL/别名语法雷）、forming-bar 实测 0 行（`ingest_ts < trade_time` 判据） |

| 攻面二小项 | 状态 | 判据/结论位置 |
|---|---|---|
| 前手记录"adj_factor 未重做"复测 | 攻 | 仍成立：`kline_daily.adj_factor` 恒 1（10,085,765 行 / 0 行 !=1） |
| 口径在哪一层决定 / 单一真源 | 攻 | 三层并存：出口归一层 `market_units`（唯一真源，load_history 消费）、SQL 直乘层（P-01/P-03，各写各的）、点事件层 `producer.py:87`（1/dr 点口径）⇒ **无单一真源**，登记 P-03 处方 |
| 除权日因子回填幂等（二次乘） | 部分攻 | `producer.py:87` 侧守卫 `_fetch_adj_factor` 查已覆盖键（akshare_provider.py:271-288，instL 独占面，未代修）；跨重定标相乘幻影实测见 market_units:44-48 并已复核 |
| 因子缺失处理（补 1.0 vs 出声） | 攻 | `backtest.py:355-358` `adj.where(adj>0, 1.0)` 静默退不复权 + `_log_panel_report` 显式告警（防护到位）；F-01 位点原为"填 0 且不出声"（已修）；`adj_factor` 专表残留 **75 行 =0**（bdpan_lof 71 + bdpan_etf 4）违反 #ARCH-ADJFACTOR-NULL-001 语义 → 数据面待清 |

**未攻面（如实）**：tick_data / 逐笔明细的 PIT（亿行表，未做谓词代价评估）；`c1_backtest` 库内
定格快照链是否可被历史改写；LSG 侧对"回测结论进生产"的闸；ETF LOF 分钟线（未查小时带）；
`kline_index_intraday` 若未来建表的对齐；`baostock/tushare` fallback 链的复权一致性。

---

## 4. 复测命令（供总包一条验真）

```bash
# 死列复测（期望：uniq=1, countIf!=1 为 0）
python -c "from zephyr.infrastructure.database_service import DatabaseService as D;\
print(D().get_clickhouse_conn(role='reader').execute('SELECT count(),uniqExact(adj_factor),countIf(adj_factor!=1) FROM c1_market.kline_daily FINAL'))"
# 无 FINAL 活体重复（期望：6471 vs 5568）
python -c "from zephyr.infrastructure.database_service import DatabaseService as D;c=D().get_clickhouse_conn(role='reader');\
print(c.execute(\"SELECT count() FROM c1_market.kline_daily WHERE trade_date=todate('2026-09-17')\"),c.execute(\"SELECT count() FROM c1_market.kline_daily FINAL WHERE trade_date=todate('2026-09-17')\"))"
# LEFT JOIN 填 0 而非 NULL（期望：join_use_nulls=0 且 ifNull(0,nan)=0）
python .runtime/tmp/st-ff-rb-pit-20260918/probe10.py
```

### P-07 · 同一策略体系内两族价格口径并存，无单一真源（跨簇裁定项）

- 判据源（实测 2026-09-18）：
  - **复权族**：`src/zephyr/factor/core/evaluation/backtest.py:274-323 load_history()` 出口经
    `src/zephyr/shared/utils/market_units.py:314-425 normalize_market_panel()` 归一为
    "窗口末锚定复权连续价"，消费方含实盘信号 `src/zephyr/ex_core/signal_providers.py:92`、
    回测 `src/zephyr/pf_core/strategy_engine/strategy_runner.py:369`、
    `src/zephyr/pf_core/strategy_engine/framework_composer.py:2045`；
  - **不复权族**：`src/zephyr/signal_ashare/**` 与 `src/zephyr/plan_engine/**` 共 82 处直读
    `c1_market.kline_daily.close`（原始价，且多数无 FINAL，见 P-01），
    其产出经 `src/zephyr/pf_core/strategies/daban_sleeve_strategy.py:63-75` 进组合核心。
- 后果：同一条策略在回测里吃复权价、在实盘信号里吃不复权价；除权日两族给出相反方向
  （实测样本：2025-09-01 起 266 个票日被不复权口径判成"跌幅>9.9%"，而后复权真值几乎没跌）。
- 单一真源缺位的机检证据：全仓无一处 gate 检查"价格列口径"（`gate_registry.yaml` 内与
  复权相关的判据数 = 0；`market_units` 的 INV-UNIT-001 只在 load_history 一个出口生效）。
- 建议（择一，均为加严）：①把 `market_units.normalize_market_panel` 提为**行情读取唯一出口**，
  `signal_ashare`/`plan_engine` 禁止直读 `kline_daily.close`（配 gate：staged .py 新增
  `FROM c1_market.kline_daily` 且 SELECT 列含 close 而不经 normalize ⇒ 阻断，own-diff 作用域）；
  ②或反向——明确"信号层一律不复权、收益层一律复权"的分域契约，写进
  `architecture_model/contracts/`（PROTECTED-PATHS，需 Owner 授权，本车道只登记不代改）。
- 验收判据：任一行被两族同时消费的策略，回测/实盘在同一交易日取到的 close 相对差 < 1e-6，
  或差值被显式标注为"故意不同纲"并给出换算件。


---

## 5. 接力复测更正（st-ff-pit2-20260918，2026-09-18 22:4x 本机实跑）

> 本节由接力车道追加，**只更正与本文件相关的实测数字**，不改写 §1/§2 的处方判定。
> 依据=战役协议 R-019"复跑不符者回写该行、禁按陈旧记载重复施工"。
> 完整案卷另见 `lanes/pit2_prescriptions.md`（staged，待总包代登记 creation_token 后入面）。

### 5.1 本文件 §1（F-01）五组数字复跑结论

| 前手数字 | 接力车道复跑 | 判定 |
|---|---|---|
| adj_factor 日覆盖 07-06 前 ~7,470 → 之后 2~60 行 | 06-25~07-05 日均 **7,376**；07-06~09-18 min=**1** / max=**60** / 日均 **17.3** | 一致（下界实测是 1 而非 2） |
| `join_use_nulls=0` + `Decimal(18,8)` 非 Nullable ⇒ `ifNull` 永不触发 | join_use_nulls=**0**；类型 **Decimal(18, 8)**；`ifNull(Decimal0,nan)`→`(0.0, isNull=0)`；未命中实测返回 `Decimal('0')` | 一致 |
| 面板 959,185 / 0 价 303,817 / NULL 0 | **959,185 / 303,817（31.67%）/ 0** | **逐位一致** |
| 收益越界 7,400 格 | **6,456** 格（式子=`toFloat64` 后逐票 `lagInFrame` 环比、同窗口） | **值不等、不可核**（前手式子未留档）⇒ 该格改按"6,456（本车道口径）"引用 |
| ★ notna() 口径把 0 计成已覆盖 ⇒ 自我掩盖 | 同一面板同日：notna 口径 **100.00%**、真值可用(>0) **0.35%**（近 8 交易日逐日 100.0% vs 0.16%~0.50%） | **一致且量化更强**（虚报 99.65 个百分点） |
| 近 20 交易日 C1/C2/C3 全 NaN、C4 0.07%~0.51%（真值 21%~63%） | 旧口径 C1/C2/C3 **20/20 全 NaN**、C4 **0.0724~0.5078**；新口径 C4 **21.38~63.83** | 一致 |

补测：`c1_market.kline_daily_hfq` 面值日期域 **2019-01-02~2026-09-18**、**5,221** 只（=绊线起点口径为真）；
修后同窗口真值可用 **902,725/959,185 = 94.11%**、NULL **56,460**。

### 5.2 本文件 §1 的三处需更正项

1. **"验收判据=`TestStockPanelAdjustmentSource`（5 件）"实测该类只有 4 件**
   （`test_zero_fill_collapse_must_raise` / `test_healthy_coverage_passes_silently` /
   `test_sql_points_at_hfq_truth_and_guards_zero` / `test_loader_wires_the_tripwire`）。
   防线本身有效（4/4 变异能红），仅计数与代码不符。
2. **`.runtime/tmp/st-ff-rb-pit-20260918/prove_red.py` 在本机跑不起来**（非判据问题，是载体问题）：
   `subprocess.run(..., text=True)` 在 GBK locale 下 `UnicodeDecodeError: 'gbk' codec can't decode byte 0x80`；
   且 M2 锚点硬写 `\r\n`，该文件 `git ls-files --eol` = `i/lf w/crlf`，行尾一漂移即"变异锚点未命中→台子失效"。
   接力车道重写版=`.runtime/tmp/st-ff-pit2-20260918/prove_red2.py`（显式 `encoding='utf-8'`+行尾无关锚点），
   复跑 **4/4 转红、还原按字节一致**（基线 sha256=`3909046aef75368c`）。
3. **§4 "复测命令"里 `get_clickhouse_conn()` 的真接口**：本文件 §4 第一条用了 `.execute(...)`（正确），
   但 §2/P-01 正文写的是 `ch_writer.query(`（那是被门禁匹配的**违规**接口，不是取数接口）——
   三条车道在本役各猜过一次，此处记死：`DatabaseService.get_clickhouse_conn()` 返回
   **clickhouse_driver.client.Client** ⇒ 只有 `.execute(sql, params)`，无 `.query()` 无 `.cursor()`。

### 5.3 行为变更（§1 末段"面板窗口整体早于 2019-01-02 时绊线改判硬失败"）抽跑结果

静态穷举：`src/**`+`scripts/**` 显式日期字面量赋值 **36 处**，结束日早于 2019-01-25 的仅
`src/zephyr/backtest/services/param_analyzer.py:379-380` 的 `start_date=end_date="1970-01-01"`，
读码确认它是 `compute_key(strategy_id="param_analysis", ...)` 的**缓存键占位**、不是取数窗口；
`enable_cross_sectional` 默认 **False** 且 `_load_stock_panel()` 唯一调用者只在开关为 True 时进入。
⇒ **未检出现有作业会因此崩**（未覆盖面=运行期由 CLI/配置动态传入的窗口，静态取不到样本）。

抽跑 4 窗（走 `_load_stock_panel` 真身）：

| 窗口 | 结果 |
|---|---|
| 2015-01-01..2018-12-28（整体早于真源起点） | **硬失败**（符合加严预期）`[ZA-REGIME-0010] 近端 20 交易日复权覆盖率 0.0% < 下限 50%` |
| 2018-01-01..2019-06-28（跨起点） | 通过，真值可用 47.78%，另出声 WARNING"缺席 243 交易日" |
| 2010-01-01..2026-06-30（**生产默认窗口**） | 通过，1,214,702 行 / 可用 58.76% |
| 2018-11-01..2019-02-20（紧贴起点边界） | 通过，可用 56.99% ⇒ 硬失败边界不外溢到起点后约 20 交易日 |

### 5.4 §2 P-01 的两个数字/事实更正

- **"82 处"本车道未能复现**：同一探针 `scan_no_final.py` 在原目录复跑=**70** 个 (文件×表) 对；
  改用"与门禁同源判据"（直接 import 门禁的 `_scan_missing_final_reads`，added_lines=None 全文件）
  =**91 个行位点 / 76 个 (文件×表) 对**，其中 **58 个行位点在资金/信号主链**。
  ⇒ 派工一律引用 91/76 这组口径，勿再沿用 82。
  ⚠️ 假阴性陷阱：`scan_no_final.py` 用 `Path(__file__).resolve().parents[3]` 反推仓根，
  **一旦把脚本 cp 到别的深度下再跑，REPO 指错 ⇒ 扫 0 个文件 ⇒ 打印"候选泄漏点 = 0"**。
  那个 0 是扫描器空转，不是缺陷消失（本车道亲踩）。
- **P-02 的"当前 0 处触发"仍成立**：本车道复现 `inject_final("… FROM c1_market.kline_daily AS k …")`
  确实产出非法 SQL `FROM c1_market.kline_daily FINAL AS k`（Code:62 形态），
  且全仓 `src/` 里把带别名 FROM 喂给 `inject_final`/`ch_reader.query`/`query_table` 的调用面 **0 处**
  ⇒ 定性不变：**潜伏缺陷、护身符是口头约定**。
- **P-01 附注（无版本列）与在册门禁同号**：仓内已有 **CH-VERSION-COL**（priority=38，紧邻本 gate 37）
  专管 Replacing 表版本列 ⇒ 派工前先读它，勿另造判据。

### 5.5 撞车与移交登记（P-01 门禁面）

- 判据②由本车道与 **`st-ff-gov2-20260918`（交工时点仍存活，heartbeat 14s）** 在无 claim 窗内同时开工，
  盘上成件是两车道并集：gov2 追加 5 件测试并把正则加强为
  `(?![\w.])(?!\s+import\b)`，本车道贡献判据②主干（`_scan_missing_final_reads` /
  `_check_missing_final` / `_resolve_engine` 复用 ch_writer 单一真源 / `_SQL_SHAPE` 假红防护 /
  容器级注入载体识别 / 引擎不可解析时出声降级）。**本车道已释放自家 claim，落地权归 gov2。**
- ★★ **替 gov2 踩出的必死地雷**：判据②用的 `# noqa: ch-final  <理由>` 逃生标记**未登记** ⇒
  队列落地被 **NOQA-VALIDATION** 硬拦（实测死信 `q-20260918-st-ff-pit2-20260918-0001`，
  报点 `ch_final_gate.py:L198 / L431`：需先在 `noqa_exempt_registry.yaml` 登记）。
  两条出路：①热册登记 `ch-final`（车道禁写热册 ⇒ 转总包/有册权车道）；②删逃生标记（则误红无逐行豁免口）。
- 落地前第二件事：`_check` 尚未接 `_build_own_scope`（现按 staged 全量 .py 扫，与判据①同形）。
  实测现网共享 index 下 29 个外来 staged `src/*.py` 判据②`passed=True` ⇒ **当下**不连坐，
  但那是运气不是设计。
- 红/白双向证据（可复跑，脚本 `.runtime/tmp/st-ff-pit2-20260918/live_fire3.py`，
  一次性 git 微仓 + 生产入口 `make_ch_final_gate().check()` + 真 CH 引擎面不 mock）：
  红1 无 FINAL 直连 execute → **拦**；白1 补 FINAL → 放行；白2 走 ch_reader.query → 放行；
  红2 违规件与白件同批 → **仍拦**（未被掩盖）。4/4 符合预期。
  单测 **31 件通过**；`tests/governance/commit_gates` 全目录 **2583 passed / 1 failed**，
  唯一失败 `test_errcode_consistency_gate::TestRealRepoPass::test_current_repo_is_clean`
  违规项 `unregistered_code ZA-DATA-ALERT-WEBHOOK`、观测面=git index 外来 staged ⇒ 按 §3.4 不代修。
- 本文件 §3 覆盖面矩阵的"②③⑤ 攻"三格，接力车道**未做独立复跑** ⇒ 仍是前手单证，
  不得据以声称已闭环；逐格状态与未攻原因见 `lanes/pit2_prescriptions.md` §7。
