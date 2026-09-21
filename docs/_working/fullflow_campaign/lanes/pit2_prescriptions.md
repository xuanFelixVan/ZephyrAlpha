---
ttl: task_bound
completes_when: 本文件 P-01 存量清单被总包逐条派工、且 §5 撞车移交项由 gov2 车道确认落地
---

# 红队 PIT 接力车道 st-ff-pit2-20260918 · 接手案卷与处方移交

> 接手自 `st-ff-rb-pit-20260918`（耗尽 150 轮阵亡、未交回报）。
> 前手案卷=`lanes/rbpit_prescriptions.md`（195 行）；前手探针已双份留档
> `.runtime/tmp/ff-recon/backup_pit/`（21 件）+ `G:/zephyr_cold/30_corpus/fullflow_harvest/pit_20260918/`。
> 本文所有数字均为 2026-09-18 **本车道本机实跑**（R-019 施工前复测），不继承前手数值。
> 表述禁令（#325）：本文不出现"全绿/无泄漏"，只出现"检出 N 件 / 未检出 M 件（附覆盖面）"。

---

## 1. ★ 两条派工前提被实测推翻（先记账，再谈施工）

| # | 任务书前提 | 实测 | 证据（一条命令可复） |
|---|---|---|---|
| 前提A | "`regime_feature_builder.py` 有 +74/−9 **未提交**，悬在工作树" | **已进 HEAD**：`ee0e0a2cef`（父=提交前基线），`git diff HEAD --numstat` 对该文件**空输出** | `git show --numstat ee0e0a2cef` |
| 前提B | "`ch_reader.py` 只匹配 ch_writer.query(  ⇒ 82 处直连读无牙，**先复跑确认 82**" | 判据②已在工作树被**两条车道同时实现**（本车道 + `st-ff-gov2-20260918`），且前手的 82 **不复现**（见 §3 两个口径均 70~91，无 82） | `git diff HEAD --numstat -- src/zephyr/data/ch_reader.py`（本车道未改） |

前提A 被推翻 ⇒ 本车道 T1 从"抢救落地"改判为"**独立复测 + 复跑能红**"（已全部完成，见 §2）。
前提B 被推翻 ⇒ 见 §5 撞车登记。

---

## 2. F-01 复测表（前手五组数字逐组复跑）

窗口 `2026-01-05..2026-09-18`，`c1_market.kline_daily FINAL` A_share quality_flag=1。
探针=`.runtime/tmp/st-ff-pit2-20260918/reverify_f01.py`（只读，输出 `reverify_f01.log`）。

| 前手数字 | 本车道复跑 | 判定 |
|---|---|---|
| adj_factor 日覆盖 07-06 前 ~7,470 → 之后 2~60 行 | 06-25~07-05 日均 **7,376**；07-06~09-18 **min=1 / max=60 / 日均 17.3** | **一致**（前手写"2~60"，实测下界是 1） |
| `join_use_nulls=0` + `adj_factor Decimal(18,8)` 非 Nullable ⇒ `ifNull(a.adj_factor,nan)` 永不触发 | join_use_nulls=**0**；类型 **Decimal(18, 8)**；`ifNull(Decimal0, nan)` → `(0.0, isNull=0)`；LEFT JOIN 未命中实测返回 `Decimal('0')` / isNull=**0** | **一致** |
| 面板 959,185 行 / close_hfq==0 **303,817** / NULL **0** / 收益越界 7,400 | 959,185 ✓ / 303,817 ✓（31.67%）/ NULL 0 ✓ / 越界 **6,456** | 前三项**逐位一致**；越界项**值不等**（本车道式子=`toFloat64` 后 lagInFrame 逐票环比、同窗口，未记前手式子 ⇒ 标"同数量级、不可核"） |
| ★ 旧日志按 `notna()` 统计覆盖率 ⇒ 把 0 计成已覆盖 ⇒ 自我掩盖 | 同一面板同一天：**notna 口径 = 100.00%**，**真值可用(>0) 口径 = 0.35%**（近 8 交易日逐日 100.0% vs 0.16%~0.50%） | **一致且量化更强**：指标虚报 99.65 个百分点 |
| 近 20 交易日 C1/C2/C3 全 NaN、C4 0.07%~0.51%（真值 21%~63%） | 旧口径：C1/C2/C3 **20/20 全 NaN**、C4 **0.0724~0.5078**；新口径（hfq 真值）：C4 **21.38~63.83**，C1 0.0159~0.0189、C2 0.2146~0.2319、C3 0.1970~0.2570 | **一致** |

补测（前手未记）：
- `c1_market.kline_daily_hfq` 日期域 **2019-01-02 ~ 2026-09-18**，标的 **5,221** 只 ⇒ 绊线的"2019-01-02 起点"口径为真。
- 修后同窗口：面板 959,185 行，真值可用 **902,725（94.11%）**，NULL **56,460**（NULL=真缺失，被 pct_change 剔除，不再冒充 0 价）。

### 2.1 能红复证（本车道自有红蓝台，不依赖前手脚本）

前手 `prove_red.py` **在本机跑不起来**：`subprocess.run(..., text=True)` 在 GBK locale 下
`UnicodeDecodeError: 'gbk' codec can't decode byte 0x80` ⇒ 红蓝台自身先失效（判据没问题，载体有问题）。
另其 M2 锚点硬写 `\r\n`，本仓工作区该文件是 CRLF 而 index 是 LF（`git ls-files --eol` = `i/lf w/crlf`），
行尾一漂移即"变异锚点未命中 → 台子失效"。本车道重写为 `prove_red2.py`
（显式 `encoding='utf-8', errors='replace'` + 锚点行尾无关）。

```
[baseline] sha256=3909046aef75368c  未变异 4 件：rc=0  4 passed
[M1 零价算作已覆盖] rc=1 → 红  还原按字节一致=True  2 failed, 2 passed
[M2 绊线未接线]     rc=1 → 红  还原按字节一致=True  1 failed, 3 passed
[M3 判据放宽到 0]   rc=1 → 红  还原按字节一致=True  2 failed, 2 passed
[M4 复权源改回塌缩专表] rc=1 → 红  还原按字节一致=True  1 failed, 3 passed
[结论] 变异台 4 条，无效 0 条；收尾 sha256=3909046aef75368c（与基线同）
```

### 2.2 测试面（本车道自跑，不继承前手数值）

- `tests/regime` 目录全套：**1029 passed in 45.36s**（与前手声称的 1029 同值，本车道重跑确认）。
- ⚠️ 前手案卷写"验收判据=`TestStockPanelAdjustmentSource`（**5 件**）"⇒ **实测该类只有 4 件**
  （`test_zero_fill_collapse_must_raise` / `test_healthy_coverage_passes_silently` /
  `test_sql_points_at_hfq_truth_and_guards_zero` / `test_loader_wires_the_tripwire`）。
  属 R-026 第 2 类"口径/计数与代码不符"，不影响防线有效性，但案卷数字须更正。
- 三件套状态：F-01 那笔 `ee0e0a2cef` **未新建任何文件**（2 件均为 M），
  故 creation_token / 翻译登记 / depgraph 新节点**均不适用**（非缺失，判据=
  `git show --name-status ee0e0a2cef` 只有两行 M）。

### 2.3 行为变更抽跑（早于 2019-01-02 的窗口由"算出错特征"改判"硬失败"）

静态穷举：`src/**` + `scripts/**` 里显式日期字面量赋值共 **36 处**，
其中结束日早于 2019-01-25 的只有 **1 处** = `src/zephyr/backtest/services/param_analyzer.py:379-380`
`start_date=end_date="1970-01-01"` ⇒ 读码确认它是**缓存键占位**（`compute_key(strategy_id="param_analysis", ...)`），
不是取数窗口 ⇒ **不构成会崩的作业**。
`RegimeFeatureBuilder(enable_cross_sectional=...)` 默认 **False**，且 `_load_stock_panel()`
的唯一调用者是 `_build_cross_sectional_features()`（仅在开关为 True 时进入）⇒ 绊线打不到未开横截面的既有作业。
全仓 `enable_cross_sectional=True` 的生产配置只出现在 `scripts/backtest/alg01_ab_redo.py`（B 臂）。

抽跑 4 窗（`probe_2019_window.py`，走 `_load_stock_panel` 真身，top_n 缩样以控成本）：

| 窗口 | 结果 | 备注 |
|---|---|---|
| W1 2015-01-01..2018-12-28（整体早于真源起点） | **硬失败**（符合预期） | `[ZA-REGIME-0010] 近端 20 交易日复权覆盖率 0.0% < 下限 50%` |
| W2 2018-01-01..2019-06-28（跨起点） | 通过 | 真值可用 47.78%，另出声 WARNING"缺席 243 交易日" |
| W3 2010-01-01..2026-06-30（**生产默认窗口**） | 通过 | 1,214,702 行 / 可用 58.76% / 11.6s |
| W4 2018-11-01..2019-02-20（紧贴起点边界） | 通过 | 可用 56.99% ⇒ 硬失败边界在起点后约 20 交易日内，不外溢 |

⇒ **结论：这是加严（#321 方向），且现网无既有回测作业因此当场崩**（穷举面=上述 36 处字面量赋值 +
`enable_cross_sectional` 调用面；未覆盖面=运行期由配置/CLI 传入的动态窗口，本车道未取到样本）。

---

## 3. P-01 存量清单（无 FINAL 直读 ReplacingMergeTree）

**口径先立清**（本役 R-026 第 2/3 型的常见来源就是"换了把尺子又报同一个数"）：

| 口径 | 数值 | 说明 |
|---|---|---|
| 前手案卷记 | **82** | 本车道**未能复现**（前手 `scan_no_final.py` 现跑=70 个"文件×表"对；两小时内工作树被多车道推进，差 12 不作归因猜测） |
| 前手探针 `scan_no_final.py` 复跑 | **70** 个 (文件×表) 对 | 去重键=(相对路径, 表名)，模块级容器计作 `:0` |
| ★ **与门禁同源判据**（`_scan_missing_final_reads` added_lines=None） | **91 个行位点 / 76 个 (文件×表) 对** | 本车道采用此口径交付（门禁将来拦的就是这批位点的新增行）；其中 **58 个行位点在资金/信号主链** |

⚠️ 复跑前手探针的一个**假阴性陷阱**（本车道差点中招）：`scan_no_final.py` 用
`REPO = Path(__file__).resolve().parents[3]` 反推仓根 ⇒ **一旦把脚本 cp 到 `.runtime/tmp/ff-recon/backup_pit/`
下再跑，REPO 变成 `D:/ZephyrAlpha/.runtime`，扫 0 个文件，输出"候选泄漏点 = 0"**。
"0"是扫描器空转，不是缺陷消失。正道=必须在原目录跑，或显式传仓根。

完整 91 位点清单：`.runtime/tmp/st-ff-pit2-20260918/inventory_no_final.log`（含表名、主链标记、
是否"直连 execute"面）。按文件汇总（前 10）：

```
10  src/zephyr/data/sector_report_builder.py
 8  src/zephyr/signal_ashare/sector/sector_divergence.py
 7  src/zephyr/data/implementations/akshare_provider.py
 6  src/zephyr/signal_ashare/sentiment/option_sentiment.py
 6  src/zephyr/signal_ashare/futures_basis_monitor.py
 5  src/zephyr/signal_ashare/mainline_candidates.py
 5  src/zephyr/signal_ashare/sector/sector_leader.py
 5  src/zephyr/data/implementations/daban_board_event_deriver.py
 4  src/zephyr/frontend/dashboard/api_server.py
 4  src/zephyr/signal_ashare/limit_up/limit_up_followthrough.py
```

**资金/信号主链上最该先修的（★，逐条给派工对象）**：

| 位点 | 表 | 为什么最要命 | 建议 owner |
|---|---|---|---|
| `signal_ashare/limit_up/limit_up_followthrough.py:62,69,80,87` | limit_up_down / **kline_daily**×2 / market_breadth_snapshot | 涨停跟随信号的进料；kline_daily 无 FINAL 实测同键两版 volume 相差 **100 倍**（53,132,359 股 vs 531,324 手），quality_flag 两版同为 1 ⇒ 质量过滤挡不住 | signal 道 |
| `signal_ashare/mainline_candidates.py:91,97,103,109,116` | kline_sector_880 / money_flow / sector_constituent / sector_meta / **kline_daily** | 主线候选池构成，直接进组合 | signal 道 |
| `signal_ashare/sector/sector_divergence.py:119..162`（8 处） | kline_sector_880 / sector_constituent / money_flow / **kline_daily**×2 / stk_limit / dragon_tiger_seat | 板块背离判定 | signal 道 |
| `signal_ashare/futures_basis_monitor.py:65..103`（6 处） | index_quote / futures_kline_qmt / kline_futures / kline_index / futures_position / calendar_event | 期现基差（攻面一⑤的实盘对偶） | signal 道 |
| `signal_ashare/sentiment/option_sentiment.py:82..117`（6 处） | option_iv_surface×3 / option_kline / option_greeks / calendar_event | 期权情绪面 | signal 道 |
| `plan_engine/close_verifier.py:99,104,114` | kline_index / kline_etf_60min | **收盘判定链**（经 `judgment_settler.py:131-135 _reader_execute` 裸 execute） | judgment 道 |
| `plan_engine/daily_plan.py:552,574,578`；`scenario_classifier.py:383` | kline_index / market_breadth_snapshot / trade_calendar | 日内计划与情景分类 | judgment 道 |
| `pf_alloc/allocation_inputs.py:301` | `c1_backtest.sim_pocket_daily` | **仓位分配输入**（资金破坏面，且读的是回测库） | alloc 道 |
| `strategy_pipeline/fw_backtest.py:193`、`pipeline_events.py:625` | index_constituent / kline_index | 回测与事件链 | sim 道 |
| `data/sector_report_builder.py`（10 处）、`data/implementations/daban_board_event_deriver.py`（5 处）、`data/implementations/akshare_provider.py`（7 处） | 多表 | 派生层：错数会**沉淀进下游表**（比读时错更难回滚） | instL（akshare_provider 是其独占面） |

⇒ **本车道未代修任何一条**（`ch_reader.py`/`akshare_provider.py` = instL 独占面，其余按 §3.4 owner 责任制）。

---

## 4. 处方分流表（前手 P-01…P-07 + 本车道新增）

| 处方 | owner | 本车道动作 | 状态 |
|---|---|---|---|
| **P-01** 门禁无牙（判据②缺失） | 门禁面（无独占册） | 判据②已在工作树实现并测通，**未落地**（§5 让路） | **移交** |
| **P-01 存量 82/70/91 处** | instL + signal + judgment + alloc + sim 各道 | 出清单（§3），**不代修** | **待总包派工** |
| **P-01 附注**：ReplacingMergeTree **无版本列**（`kline_daily.engine_full` 实测=`ReplacingMergeTree`，无 `(ingest_ts)`）⇒ FINAL 保留哪一行无成文保证 | 数据面 + Owner 门位 | 只登记（加版本列属数据面破坏性操作）；另有在册门禁 **CH-VERSION-COL**（priority=38）与本项同题，派工前先读它 | **只登记** |
| **P-02** `inject_final` 遇表别名产非法 SQL（`FROM t FINAL AS k` → Code:62）+ `query()` 把失败吞成 `''` | **instL**（`ch_reader.py` 独占） | 未动一行；复测确认前手"全仓当前 0 处触发"仍成立（判据②扫出的 91 位点里无一经 inject_final 带别名路径） | **只登记转报** |
| **P-03** `index_eqw_compute`/`index_breadth_compute` 用死列 `kline_daily.adj_factor` 冒充复权（列恒 1：10,085,765 行 / 0 行≠1） | 数据面（不在独占表内） | 本车道复测死列结论仍成立；未改（改它=动派生链，需与 P-01 存量修同批否则口径来回跳） | **待总包指派** |
| **P-04** `intraday_l1_tracker._A50_LAST2_SQL` 无 as-of 谓词（同族 `_INDEX_PREV_SQL` 有） | judgment 道 | 未动 | **只登记** |
| **P-05** ETF 分钟线盘后批量入库 ⇒ "盘中 L1"结构上无法触发 | 供数面 | 未动。**但本车道按任务书红线改用"修复后口径"复测**：`kline_etf_1min/5min` 现网 live 小时域 ∈[9,15]、UTC 带 **0 行** ⇒ BRK-036 确已闭合（R-052 事实链与本车道复测一致） | **只登记** |
| **P-06** `analyst_forecast` 无 publish_date，只能拿 report_date 当可见性锚 | 数据源接入面 | 未动 | **只登记** |
| **P-07** 同体系内两族价格口径并存、无单一真源 | **跨簇裁定** | 未动；选项②要改 `architecture_model/contracts/`（PROTECTED-PATHS） | **需裁定** |
| **新 P-08（本车道）** 门禁"判据②"与"表名来自 registry 变量"的 SQL 静态不可见 | 门禁面 | 已在 gate 源码注释里写明覆盖面；补法=要求 `get_registry().table()` 的返回值参与运行时断言（非静态门禁） | **只登记** |
| **新 P-09（本车道）** `tests/` 下**没有任何** CH-FINAL-GATE 测试 ⇒ "门禁无牙"两年不可见 | 门禁面 | 本车道新建 31 件测试（§6），已测通 | **随判据②一起移交** |

---

## 5. ★ 撞车登记（P-01 门禁面，两条车道同时施工）

- 进场时（≈22:0x）`.ailocks/registry.json` 只有 4 条 claim，**无 commit_gates 面** ⇒ 按任务书开工判据②。
- 22:32 编辑门禁文件时工具报"file changed since last read"，复查发现
  **`st-ff-gov2-20260918` 已对同一 `ch_final_gate.py` 与本测试文件取 claim**，
  并在测试文件 261-328 行**追加 5 件**（`(?![\w.])(?!\s+import\b)` 负向断言的边界用例——
  与本车道独立发现的同一假红源，他们修在正则、我修在加 `_SQL_SHAPE` 前置判据，**两套都在盘上且互不冲突**）。
- 本车道动作=**立即停手让路**：撤掉自己刚加、尚未接线的 `_build_own_scope`/`_audit_foreign_staged` import
  （留着会变未用导入，按 R-028 会打死他道提交通道），此后**未再改这两个文件一行**。
- 截至 22:39 两份 claim 已消失（`total locks=2`，均非本面），但
  **`ch_final_gate.py`（+225/−6）与 `test_ch_final_gate_no_final_reads.py`（untracked）仍未进 HEAD**
  ⇒ 正是本役反复出现的"修复字节长期悬在工作树"病（§8 可被整文件还原，本役已被抹过四次）。
  **本车道已把它们双份留档**：`.runtime/tmp/ff-recon/pit2_held/`（sha256
  `a79fe0b156d7c19a…` / `7adb9a847fab0320…`）+ `G:/zephyr_cold/30_corpus/fullflow_harvest/pit2_20260918/`。
- ★★ **本车道替 gov2 踩出的一颗必死地雷（务必先修再提交）**：判据②里的
  `# noqa: ch-final  <理由>` 逃生标记**未登记** ⇒ 队列落地被
  **NOQA-VALIDATION** 硬拦（本车道实测死信 `q-20260918-st-ff-pit2-20260918-0001`，
  报点 `ch_final_gate.py:L198 / L431` "未登记的 noqa 标记 'ch-final'（需先在
  `noqa_exempt_registry.yaml` 登记）"）。两条出路：
  ①在 `noqa_exempt_registry.yaml` 登记 `ch-final`（**热册，本车道无权写**，转总包或有册权车道）；
  ②删掉逃生标记（判据仍成立，但误红时无逐行豁免口，82/91 存量若被后续车道改动会硬顶）。
  本车道选①并移交——**不自行写热册、不与活体共作者抢落地面**。
- **给总包的派工建议**：判据②的落地权归**一条车道**（本车道倾向 gov2，他们已在面上并有 5 件额外测试），
  另一方转"存量清单派工"。落地前三件事必须做：
  ① 先解上面 NOQA-VALIDATION；
  ② 把 `_check` 接 `_build_own_scope`（外来 staged 违规=warn+审计，不阻断无辜提交人，宪法 §3.1）——
     实测现网共享 index 下 29 个外来 staged `src/*.py` 判据②passed=True，即**当下**不连坐，
     但这是运气不是设计（gov2 与本车道都未接线）；
  ③ 复跑 §6 实弹四门。

---

## 6. 判据②加严的红/白双向证据（落地后验收用）

**单测**：`tests/governance/commit_gates/test_ch_final_gate_no_final_reads.py`
→ 本车道 **26 件 + gov2 追加 5 件 = 31 件全过**（`31 passed in 1.83s`）。

**实弹（生产判定入口 `make_ch_final_gate().check()`、真 CH 引擎面、零共享写的一次性 git 微仓）**：

```
[红1 无 FINAL 直连 execute]        passed=False  ← 拦（detail 指到 bad_read.py:L3 与表名）
[白1 同一条 SQL 只补 FINAL]        passed=True
[白2 改走 ch_reader.query 注入]    passed=True
[红2 白件与违规件同批]             passed=False  ← 违规件未被白件掩盖
[结论] 4 门实弹，不符 0 门
```
脚本=`.runtime/tmp/st-ff-pit2-20260918/live_fire_gate2.py`（可重跑）。

**回归**：`tests/governance/commit_gates` 目录 **2583 passed / 1 failed**，
唯一失败=`test_errcode_consistency_gate.py::TestRealRepoPass::test_current_repo_is_clean`，
违规项=`unregistered_code ZA-DATA-ALERT-WEBHOOK`，观测面=**git index**（本车道当时未 staged 任何件）
⇒ 外来在途内容，按宪法 §3.4 不代修，仅登记。

---

## 7. 攻面覆盖矩阵（本车道显式交账）

### 攻面一 · PIT 六小项

| 小项 | 状态 | 判据/结论（本车道亲验 or 前手已验+本车道复测） |
|---|---|---|
| ① 未复权价与复权价混用 | **攻** | F-01 五组数字全复跑（§2）+ 4/4 变异能红（§2.1）+ 行为变更 4 窗抽跑（§2.3）；混用另一族见 P-03（死列恒 1，本车道复测成立） |
| ② `ingest_ts` 当业务时间 | **未攻（本车道）** | 前手已攻：决策面未检出（`daily_plan.py:571`、`strategy_decay_certifier.py:100` 仅同日 tiebreak）。本车道覆盖面=**0 项独立复跑** ⇒ 该格结论仍是前手单证 |
| ③ 公告日 vs 归属日 | **未攻（本车道）** | 前手已攻（`pit_query.py:73,79` 防护到位 + P-06 无 publish_date）。本车道未复跑 |
| ④ ETF 时区劈叉 | **攻（前提复核）** | 按任务书红线**用修复后口径复测**：`kline_etf_1min` 面值 `toHour(trade_time)` 小时带 **09:00~15:00**（326,110,294 行）、`kline_etf_5min` 同为 **09:00~15:00**（71,966,591 行）⇒ 未见 UTC 带（01~07）残留 ⇒ BRK-036 已闭合（R-052 链一致）；备份五表 `kline_etf_{1,5,15,30,60}min_tz_bak_20260918` **实测仍在库**。本车道**未跑任何 `--execute`、未动备份表** |
| ⑤ 指数分钟代理基差 | **未攻（本车道）** | 前手实测 `kline_index_intraday` 不存在（`system.tables` 全查）。本车道未复跑该查；但已在 §3 抓到同域新证：`futures_basis_monitor.py` 6 处期现基差读全部无 FINAL |
| ⑥ FINAL+ORDER BY 取末根 | **攻** | P-01 判据②实现+实弹四门；forming-bar 判据（`ingest_ts < trade_time`）沿用前手 0 行结论未复跑 |

### 攻面二 · 复权口径四小项

| 小项 | 状态 | 判据 |
|---|---|---|
| 口径决定层 | **攻** | 复权真源唯一可用面=`kline_daily_hfq`（2019-01-02 起 5,221 只，本车道亲测日期域）；`kline_daily.adj_factor` 死列恒 1（亲测） |
| 单一真源 | **未攻（本车道）** | 前手判"三层并存、无单一真源"（P-07）。本车道未独立取证，仅复跑其一条支撑事实（adj_factor 恒 1） |
| 回测↔实盘同口径 | **未攻** | **未检出（附覆盖面）**：本车道覆盖面=F-01 修后的 regime 腿 + §3 的 91 位点静态扫描；**未做**同一策略回测/实盘逐日 close 对拍（前手判据 ② 里那条"相对差 <1e-6"至今无人跑过）⇒ 不得据此说"同口径" |
| 因子缺失处理方式 | **攻** | 修前=填 0 且 notna 口径自我掩盖（亲测 100.00% vs 0.35%）；修后=显式 NULL + 失维绊线硬失败（W1 亲测抛 `ZA-REGIME-0010`）；`backtest.py:355-358` 的 `adj.where(adj>0, 1.0)` 静默退不复权 = 前手记，本车道未复跑 |

**本车道未攻面（如实，含原因）**：tick_data/逐笔明细 PIT（亿行表，未做谓词代价评估，怕压死宿主）；
`c1_backtest` 库内定格快照链可否被历史改写（未开库）；LSG 侧"回测结论进生产"的闸（不属本面）；
ETF **LOF** 分钟线小时带（未查）；`baostock/tushare` fallback 链的复权一致性（未查）；
运行期由 CLI/配置动态传入的回测窗口（静态穷举取不到样本，§2.3 已标为未覆盖面）。

---

## 8. 未做清单 + 原因

| 项 | 状态 | 原因 |
|---|---|---|
| T2 判据②落地（提交） | **未做** | 22:32 撞车 gov2 持 claim ⇒ 按任务书"在途就让路并登记"停手（§5） |
| `_check` 接 `_build_own_scope`（防外来连坐） | **未做** | 同上面面归 gov2；本车道只撤了自己未接线的 import，未续写 |
| P-02 / P-03 / P-04 / P-05 / P-06 / P-07 施工 | **未做（按纪律）** | owner 非本车道（instL / 数据面 / judgment / 供数 / 接入面 / 跨簇裁定） |
| 攻面一 ②③⑤、攻面二"单一真源""回测↔实盘同口径"独立复跑 | **未做** | 轮数预算优先给了 T1 复测与 P-01；已在 §7 逐格标"未攻/未检出+覆盖面" |
| 本车道提交 0 笔 | 见 §5 | 唯一可落地面被撞车占用；F-01 无需再落（已在 HEAD） |


---

## 9. 车道终态（交工时刻，逐条可核）

| 项 | 终态 | 机证 |
|---|---|---|
| T1 F-01 复测 | **已做**：五组数字复跑（4 组逐位一致 / 1 组值不等已标"不可核"）+ 自有红台 4/4 能红 + tests/regime 1029 件自跑 + 行为变更 4 窗抽跑 + 36 处日期字面量穷举 | `reverify_f01.log` / `prove_red2.py` 输出 / `tests_regime.log` / `probe_2019_window.py` 输出；回写已入 `lanes/rbpit_prescriptions.md` §5 |
| T1 落地 | **无需**（前提A 被推翻：已在 HEAD `ee0e0a2cef`） | `git show --numstat ee0e0a2cef` |
| T2 P-01 判据②（加严到 execute 直连面） | **代码+测试已在盘、本车道不落地**（撞车让路） | 本车道死信 `q-20260918-st-ff-pit2-20260918-0001`（NOQA-VALIDATION）；gov2 自投项 `q-20260918-st-ff-gov2-20260918-0002` 交工时 state=processing |
| T2 P-01 复跑 82 | **已做**：70（前手探针原目录）/ **91 行位点·76 对·58 主链**（与门禁同源判据） | `scan_no_final_rerun.log` / `inventory_no_final.log` |
| T2 存量代修 | **未做（按纪律）**：`ch_reader.py`/`akshare_provider.py`=instL 独占，其余按 owner 责任制 | §3 清单 |
| T2 其余处方 P-02…P-07 | **逐条分流完毕**（§4），只做只读复测（P-02 非法 SQL 复现 + 全仓 0 处触发；P-05/④ 用修复后口径复测小时带） | §4 / §7 |
| T3 攻面矩阵 | **已交**（§7，6+4 格逐格标 攻/未攻+原因） | §7 |
| 本车道提交 | **1 笔**：`lanes/rbpit_prescriptions.md` §5 回写（+291/−0 纯插入）经队列项 `q-20260918-st-ff-pit2-20260918-0002` 投递 | `python scripts/commit_queue.py status --session st-ff-pit2-20260918` |
| 本车道新 .md | `lanes/pit2_prescriptions.md` **只 staged 未提交**（缺 creation_token，车道禁写热册）⇒ 请总包代登记后入面 | `git status --porcelain` 显示 `AM` |
| claim 收尾 | 本车道 claim **已全部释放**（`mine remaining: []`）；gateway 正确拒绝本车道释放 gov2 持有的两个文件 | `.ailocks/registry.json` 的 `locks` 键 |
| 成品留档 | 前手探针 21 件 + 本车道脚本/日志 14 件 + 撞车面两文件（sha `a79fe0b1…` / `7adb9a84…`）三处留档 | `.runtime/tmp/ff-recon/backup_pit/`、`.runtime/tmp/ff-recon/pit2_held/`、`G:/zephyr_cold/30_corpus/fullflow_harvest/{pit_20260918,pit2_20260918}/` |

**两条待办（不属本车道权限，置顶给总包）**：
1. `noqa_exempt_registry.yaml` 登记 `ch-final` 标记 —— 否则任何含判据②的批都会 NOQA-VALIDATION 死信；
2. 判据②落地后把 `_check` 接 `_build_own_scope`（现按 staged 全量 .py 扫，与判据①同形，
   当下不连坐只是运气）。


---

## 10. ★★ 交工前最后的三件更正（覆盖 §5/§9 的相应段落，以此为准）

1. **判据②已落地，但不是本车道落的。**
   `st-ff-gov2-20260918` 以 **`f45e205fad`** 提交 `ch_final_gate.py` +
   `test_ch_final_gate_no_final_reads.py`（HEAD 实测含 `_scan_missing_final_reads` 2 处、
   测试文件 **31 件 `def test_`**）⇒ §5 "本车道贡献判据②主干"的字节**已进版本保护**，
   只是随 gov2 的批次入库（并含他们后续的治本：`FROM` 尾闸改回溯不可绕过形、
   import 子句辨伪、测试源加 ast 合法性自检、`_scan_missing_final_reads` 复杂度从 >15 降到 10）。
   本车道全程**未在那两个文件上赢过一次提交**，也**没有回退过 gov2 的任何字节**
   （机证：本车道 22:44 留档 sha `a79fe0b1…` ≠ 现盘 `e7f0ae2b…`，差异全部来自 gov2 的 22:56 编辑）。
2. ★ **前手案卷本身原本也不在 HEAD**（本役同病的第二例，且更危险）：
   `git cat-file -e HEAD:docs/_working/fullflow_campaign/lanes/rbpit_prescriptions.md`
   ⇒ **`NOT in HEAD（仅 staged）`**。也就是本车道 22:0x 被要求"先读的前手 195 行案卷"
   一直是**只 staged 未提交**状态，一次 reconciler/整文件还原就能把这役 PIT 面的全部处方案卷抹掉。
   前手 commit message 自述"注册表随批：本车道新 .md 的 creation_token 必须对本批工作树可见"，
   但 `git show --name-status ee0e0a2cef` 实测**只含 2 个代码文件**，.md 与注册表都没跟上
   ⇒ **"声称已随批"与"实际入面"必须逐笔 `git log -1 --name-only` 核，本役第二次因此返工**。
   本车道那 +291 行更正正压在这份未提交的案卷上。
3. **本车道提交结局**：
   - 队列项 `q-…-pit2-…-0001`（判据②两文件）→ **dead**，原因 NOQA-VALIDATION
     （`ch-final` 标记未在 `noqa_exempt_registry.yaml` 登记；实测 HEAD 与工作区该册均 0 命中）；
     **本车道未 requeue 该项**——同一文件集已由 gov2 落地，重投必成重复/连坐项。
   - 队列项 `q-…-pit2-…-0002`（案卷回写 1 件 .md）→ 首轮 **dead**，原因 CREATE-GUARD 报
     "无 creation_token: rbpit_prescriptions.md"，而同一时刻 `git show HEAD:<注册表>` 实测
     **该路径的 token 在册**（`pit-attestation-prescriptions-rbpit-prescriptions-20260918`，
     created_by=st-ff-rb-pit-20260918）⇒ 判据与在册事实矛盾，疑为**落地侧读到的注册表版本
     早于 token 入 HEAD 的时刻**（时序竞态），非本车道缺登记。已按正道
     `requeue` → `q-…-pit2-…-0003`（重建快照、排队尾），**结局以总包复查为准**。
   - 本车道新建 `lanes/pit2_prescriptions.md` 无任何 token（车道禁写热册）⇒ **只 staged 不提交**，
     请总包代登记 `creation_tokens` 后入面。

⇒ **给总包的两条待办不变**（§9 末尾），其中第 1 条现在**只是给未来判据的收尾**：
`ch-final` 这个 noqa 标记已随 `f45e205fad` 进入 HEAD 代码，但注册表里仍无该标记
⇒ **任何后续车道只要在新批里写 `# noqa: ch-final …` 都会 NOQA-VALIDATION 死信**，
这是已在 HEAD 的判据与注册表之间的一条未闭合缺口，需一次热册登记收口。
