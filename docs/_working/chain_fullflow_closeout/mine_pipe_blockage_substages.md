---
ttl: task_bound
---

# M3 · 九条不通链路五段子环节拆解 + 假绿灯全量普查 + str⊶date 共因定位

- 作业性质：全程只读（SELECT / 只读 SQLite / 纯函数内存复现 / 端口探针）；未施工、未 git 写、未重启任何服务。
- 母节点：全流通战役 · 九条"不通"业务链路的子环节拆解 + 全链路假绿灯普查。
- 分母来源：D 队广度普查 `business_pipeline_skeleton.md`（N=62 链路，通30/半通23/不通9）。
- 本日实测口径（取数命令见各节，勿以本文计数为死数）：
  - `tasks.yaml` 解析任务数 = 270（脚本读数，D 队口径 271，差 1 待对齐，见长尾）；
  - `task_runs` 总行数 188,867，有运行史任务 266；
  - 09-25 为中秋休市（`SELECT max(cal_date) FROM c1_market.trade_calendar WHERE is_open=1 AND cal_date<=today()` → **2026-09-24**，当分钟实测）。**凡以 09-25 缺席判"断更"者一律判为噪音**。

## 1. 五段子环节拆解表（触发 → 计算 → 落库 → 消费 → 自检）

判定图例：✅实测通过 / ❌实测断 / ⚠️带病 / ❓不可辨。

| # | 链路 | 触发 | 计算 | 落库 | 消费 | 自检 | 断段钉死 |
|---|------|------|------|------|------|------|----------|
| 1 | #19 realtime_snapshot | ✅调度器在跑（09-24 SUCCESS@07:40，fetched=5568） | ✅fetch 产 5568 行 | ❌CH 表 0 行（count 独立两查=0，本日复测 rows_nofinal=0）；`data/failures/*realtime_snapshot*` 反复降级 | ⚠️仪表盘读空帧 | ❌task_runs 记 SUCCESS=假绿灯 | **落库段**（INSERT 失败→本地降级→回灌未闭环；探针面 ch_writer 空串歧义叠加） |
| 2 | #28 news_sentiment_score | ✅NightlySentiment 计划任务 Ready（LastRun 09-25 22:30） | ⚠️夜间脚本现算 window（`run_nightly_sentiment.py:41 → zephyr.intelligence.nightly_sentiment_window`） | ❌score 表冻结 2025-09-09（774万行整年不推进，D 队 SELECT 实测）；window 表新鲜 09-24 | ❌api_server/sentiment.html/daily_gate_snapshot/prediction_log_writer 仍读 score 旧面 | ❌无新鲜度尺 | **落库+消费段共断**：打分换面到 window，score 成僵尸壳仍被读（换名残留，值级不可见） |
| 3 | #30 financial_derived | ✅nightly_financial 档在跑（09-24T23:26Z 有运行记录） | ❌FAILED `'<' not supported between 'str' and 'datetime.date'`（崩点见 §3） | ❌随计算断（表 30.6万行停在 report_period 2026-06-30/最新行日 09-02 双口径，见 census） | ⚠️估值因子读旧季 | ⚠️FAILED 有记录但无告警尺 | **计算段**（增量窗边界 str vs date 混比） |
| 4 | #34 consensus_daily | ✅research_nightly 档有运行（09-18T22:30Z） | ❌FAILED `'>' not supported between 'str' and 'datetime.date'`（崩点见 §3） | ❌主表停 09-14；旁表 `_repaired` 停 09-15，双面孔 | ⚠️下游读哪张未锁（known_gap value_cols_pit open） | ❌无"build 连崩 N 晚"尺 | **计算段**（同 §3 共因；end 边界先崩 `'>'`） |
| 5 | #47 reconciliation_differences | ⚠️PostSettlement LastRun 09-25 15:30（休市日照跑，但 recon_runner 是否被真触发未证） | ❓无法判（无运行心跳） | ❌CH 0 行 且 governance.db 0 行（双库皆空，D 队独立 SELECT） | ❌api_server 把 CH 表映射"对账差异"展示项——若读 CH 恒空 | ❌"空=干净 vs 空=没跑"不可辨 | **落库真源方向分裂 + 自检段缺心跳**（governance.db 写端 vs CH 同名表读端） |
| 6 | #48 AutoRuntime 实盘 | ❌manual 触发；TradingWatchdog State=Disabled | —（QMT 09-18 退役过渡） | ⚠️execution_report 仅 1 行·09-18 | — | ❌无进程存活尺接入业务告警 | **触发段**（无人值守断在 watchdog 注册即禁用——Owner 已判看门狗"不必保护"，勿重裁，只登记现状） |
| 7 | #53 Ollama 后端 | ❌无 next run（boot 型），进程不在 | ❌ | ❌ | ❌LSG 全下游 | ❌存活探测未入业务尺 | **触发/服务段**（当分钟复测见挖矿日志 R6） |
| 8 | #54 LSG→LLM | ✅网关代码在 | ❌依赖 #53 | — | ❌ | ❌ | **计算段外因**（与 #53 同根，合并处置） |
| 9 | #43 pattern_win_rate | ✅daily 档有运行（09-24T09:43Z） | ❌FAILED 退出码 1（透传，真因未定位——非本档 str⊶date 签名，见 §3 反例） | ⚠️表 4239 行非空但 updated_at 停摆 | ⚠️可考性门读陈旧胜率 | ❌无 updated_at 新鲜度尺 | **计算段**（exit 1 真栈未取，属执行+写越权，留长尾） |

复现命令（只读，全表通用）：
```
python .runtime/tmp/mine_dossiers_20260926/false_green_census.py   # 一键重跑普查（含本表所有 CH/SQLite 读数）
python -c "import sqlite3;c=sqlite3.connect('file:data/integrator_progress.db?mode=ro',uri=True);print(c.execute(\"SELECT started_at,status,rows_fetched,rows_written FROM task_runs WHERE task_id='realtime_snapshot_incremental' ORDER BY started_at DESC LIMIT 3\").fetchall())"
```

## 2. 假绿灯全量普查（摘要，全清单见 `mine_pipe_false_green_census.md`）

判据 = 「最近一次 task_runs 状态」×「目标表实测 count 与 max(date_col)」（CH 经 DatabaseService reader Client，抛错态单列 PROBE_INCONCLUSIVE，绝不并入 0 行）。

实测判定分布（270 任务全扫）：
- FALSE_GREEN（SUCCESS 但目标表 0 行）：**5** —— `realtime_snapshot_incremental`、`etf_benchmark_refresh`、`suspend_status_premarket/postclose/derive_weekend`×3（suspend 一表三腿全假绿）。
- NEVER_RUN（tasks.yaml 在册、task_runs 零记录）：**10**（含 global_*_daily×4 共用 kline_global、kline_5min_history_backfill、tick_backfill_weekly、factor_decay_monitor_weekly、ir_activity_record、irm_interactive_qa、kline_us_daily_qmt）。
- NO_TARGET_TABLE：4（3 个 qmt_placeholder 死腿 + trading_lifecycle_weekly 无表声明）。
- NOT_GREEN：25（FAILED 12 / STALE 13——STALE 全部为 reaper `>6h auto-reap` 签名，含 daily_valuation、technical_indicator_full_refresh、sector 分钟族 5 腿）。
- **不可分辨集合（"从没跑过 vs 跑过且无差异/无数据"同读数）**：4 —— `etf_benchmark_refresh`、`suspend_status_premarket/postclose/derive_weekend`。特征：SUCCESS + rows_fetched=0 + rows_written=0 + 表 0 行 → 与"合法 no-op（休市/无新差异）"读数完全同型，task_runs 面无法证伪"其实从没成功跑过"。
- 新得假绿家族信号：`restricted_shares` max 日期=**2035-10-29**（前瞻解禁数据混入 date_col max，新鲜度尺会被此值骗绿——画像入 §5 字段向）。

## 3. `'>' not supported between str and datetime.date` 共因定位

两崩点实文本：consensus `'>'@09-18T22:30Z；financial `'<'@09-24T23:26Z`（task_runs 原文，census.json 复现）。

定位（只读代码核对）：
- `internal_compute_provider.py:680` `_fetch_fund_consensus_daily` → `run_compute(start=infer_incremental_start(), end=payload.end)`；`consensus_daily_compute.py:155` `if hi_iso and td_iso > hi_iso`，其中 `td_iso` 为 str、`hi_iso = end or ""`——**若 payload.end 是 datetime.date，则 str > date 崩 `'>'`**。
- `internal_compute_provider.py:710` `_fetch_financial_derived` → `run_compute(symbols, start=payload.start, end=payload.end)`；`financial_derived_compute.py:397` `if start and row["announce_date"] < start`——`row["announce_date"]` 是 `a.isoformat()` str，**start 为 date 时崩 `'<'`**。

共同根因假设（H1）：`FetchPayload.start/end` 是 `datetime.date` 类型（待 provider_base 注解码上钉死），而两个 compute 核的行字段一律先转 ISO 字符串再参与增量窗边界比较；文档串均声称"start/end: iso str"，类型契约在 provider→compute 交接处无人执行。两链同崩于此交接缝，属**同一契约违规的两个实例**，非两个 bug。

证伪法（已执行/可复跑，见挖矿日志 R6）：
1. 纯函数内存复现：`build_consensus_rows(reports=[1条], trade_dates=[date], end=datetime.date(...))` → 若抛 TypeError 且消息逐字命中 task_runs 原文，H1 成立；不命中即证伪。
2. 读 `provider_base.FetchPayload` 字段注记（静态）。
3. 反例护栏：pattern_win_rate 的 FAILED 消息是"退出码 1（透传）"，不含 str/date 签名 → 不同根，勿打包同修。

全仓同类形状可疑站点（Grep 扫描，只登记不修）：`akshare_provider.py:5063 end = payload.end or datetime.date.today()`（payload.end 直入下游比较）、`consensus_daily_repaired_compute run_compute_repaired(start=payload.start, end=payload.end)`（同一形状第三个实例，尚未崩或因未挂夜间档）、`backfill_checker.py:990`（end 先 fromisoformat 再比，安全样板）。

## 4. 六向台账（M3 增量；每向=内部反查+全网搜索双动作）

| 向 | 内部反查发现 | 全网搜索发现（URL+发布方+年份） |
|----|-------------|--------------------------------|
| ① 需求/裁定 | 九条断链的消费方全部 grep 到文件级锚点（api_server/daily_gate_snapshot/sentiment.html/prediction_log_writer，见各 lane §2）；无一条"无人读的死链"可就地清理 | Monte Carlo 把 freshness 列为数据可观测五支柱之一并给出 SLO 化用法：[61 Data Observability Use Cases](https://www.montecarlodata.com/blog-data-observability-use-cases/)（Monte Carlo Data, 2023） |
| ② 下游消费 | realtime_snapshot 断链下游=dashboard 盘中帧（读到空）；news_sentiment_score 断链下游=门闸快照/预测日志（读一年前值，值级不可见）；reconciliation 断链下游=对账展示页恒空。三处均为"静默降级不报错"型放大 | 陈旧数据下游污染的公开论述：[Top 8 Data Quality Issues & 4 Ways to Fix Them](https://dagster.io/learn/data-quality-issues)（Dagster, 2026） |
| ③ 算法/机制 | 假绿灯判据在仓内已有半套（integrity_checker 有 last_date/lag 诊断列、foreign_market_coverage 有 `_is_fresh`）但都不消费 task_runs 状态位——"任务态×落库态"交叉尺全仓零实例（本普查为首例，脚本已产） | freshness-inspection 作为一等资产属性：[Dagster 数据新鲜度检查（译述）](https://blog.csdn.net/neweastsun/article/details/149103778)（CSDN 译文, 2025）；双门校验（运行态+数据态）先例：[Towards data quality management at LinkedIn](http://engineering.linkedin.com/blog/2022/towards-data-quality-management-at-linkedin)（LinkedIn Engineering, 2022）。关键结论"任务绿≠数据新鲜，须独立测 last-updated"两独立来源齐 |
| ④ 历史先例 | 病灶 C（ch_writer/query 空串歧义）D 队已在册；reaper 误杀长任务先例在册（memory: 孵收事故 09-25）——本普查 STALE 13 例全部为 reaper 签名，与已知先例同型不另案 | [AbsaOSS/pramen](https://github.com/AbsaOSS/pramen)（GitHub, 开源框架）——"resilient pipeline 须校验 each-run 实际落库而非退出码"的框架级先例 |
| ⑤ 数据字段（画像） | 逐表 DESC 实测：kline_daily_hfq 有 lineage_version，kline_weekly_hfq/kline_monthly_hfq 无（有 data_source/ingest_ts）——D 队病灶 D 复核成立；`restricted_shares` max=2035-10-29（前瞻解禁混入，新鲜度尺会误绿）；`l2_tick`/`suspend`/`etf_benchmark` date 列 ALL_NULL（schema 在、数据零，"schema 在≠数据可得"三例钉死）；`stock_valuation` 实测在 **c1_market**（骨架未标库名，c3_fundamental 下不存在此表——查库名时已核对） | 已查无（A 股休市日新鲜度容忍外部文献无直接对应，以本仓 trade_calendar 实读替代，见 §0 口径） |
| ⑥ 成本/风险 | 量尺：112 个 realtime_snapshot 降级件=落库断是**持续态**非偶发；两 build 崩合计停更 8~12 天且每晚继续崩（无人告警）；假绿灯 5+不可辨 4+NEVER_RUN 10=19 个采集位实际失效但账面绿 | [Data quality monitoring](https://learn.microsoft.com/en-us/azure/databricks/data-quality-monitoring/)（Microsoft Learn/Databricks, 2025）——监控 ROI 以"缺陷静默时长"计价先例 |

## 5. 挖矿日志表

| 轮 | 矿脉 | signal/noise+归因 | 产出 | 复现命令 |
|----|------|-------------------|------|----------|
| R1 | D 队案卷 9 本 | signal；分母口径全盘接收 | 拆解表底稿 | Read docs/_working/chain_fullflow_closeout/ |
| R2 | 崩点静态定位 | signal；两 compute 核边界比较入档 | §3 定位 | Grep internal_compute_provider.py `run_compute` |
| R3-R4 | 假绿灯普查脚本 | signal；CH 用抛错型 Client 分离"探测失败/0 行" | census.json/md（270 任务全扫） | `python .runtime/tmp/mine_dossiers_20260926/false_green_census.py` |
| R5 | 休市噪音 | **noise 拦截**：lane 文案称"09-25 周五交易日缺席=断"，当分钟实读 trade_calendar max open=09-24 → 09-25 中秋休市，该缺席判噪音（A 股适配闸过闸记录） | 口径修正入两份案卷 | `SELECT max(cal_date) FROM c1_market.trade_calendar WHERE is_open=1 AND cal_date<=today()` |
| R6 | H1 证伪实验 | signal 钉死：`FetchPayload.start/end` 注记实测 = `datetime.date`；`build_consensus_rows(..., end=date)` 纯函数内存复现，异常消息与 task_runs 原文**逐字同**：`'>' not supported between instances of 'str' and 'datetime.date'`；financial 同形 `'<'` 复现。同轮 Ollama 11434 当分钟探针=connect timeout（不通确证，未重启） | §3 升级为已证 | `python - <<EOF`（见 R6 命令存档 census 目录 runlog 段/脚本尾）|
| R7 | 登记核对 | signal×2：6 张空壳表在 `src/zephyr/data/config/known_data_gaps.yaml` grep 命中数=0（未在册确证）；weekly/monthly_hfq 缺列 system.columns 实测确证 | §8 门位登记 | `grep -c ipo_schedule src/zephyr/data/config/known_data_gaps.yaml` |
| R8 | score 表写面 | signal：`news_sentiment_score` 全仓**无排产写腿**——唯一写者是 `scripts/governance/meta_question/wo_a2legs/backfill_news_sentiment.py`（历史一次性回补，止于 2025-09-09）；夜间脚本只写 window 表。僵尸壳被消费实锤 | 拆解表 #28 断段改写 | `grep -rn news_sentiment_score scripts src --include=*.py` |
| R9 | 分母对齐 | **noise 记账**：tasks.yaml 解析=270 条，骨架宣称 271——差 1 属枚举口径（未逐条 diff），不改判定 | 长尾 L-1 | 普查脚本第 [1] 步打印 |

## 6. 防噪音四闸过闸记录（逐条）

- 闸1 实测性：全部断言带当轮命令+输出（task_runs 原文/CH SELECT/端口 connect/纯函数异常消息），无旧快照引用。
- 闸2 可复现：普查一键脚本、崩点复现片段、登记核对 grep 命令均入挖矿日志复现列。
- 闸3 A 股适配：09-25 休市判据用 trade_calendar 实读钉死（R5）；`restricted_shares` 前瞻 2035 值判为数据画像污染非断更（T+1 无涉）；新鲜度基准=09-24（最近交易日）非 09-26 自然日。
- 闸4 影响面：每条断链给出真实消费方 grep 锚点（无消费方的"断"不存在于本档）；Ollama 腿影响 LSG 全部下游如实记，但**不判"该重启"**（Owner 已定既成事实，勿顺手重启）。

## 7. 挖后自审闸（量尺=终局全貌：Owner 只做注册/申请/充值/策略转正审批）

三态裁定（施工 / 挂起排期+解锁条件 / 方案封矿）：

| # | 候选 | 裁定 | 理由/解锁条件 |
|---|------|------|---------------|
| C1 | 两 compute 核边界比较先 `_norm_date`（str/date 统一 ISO 再比），一处规整覆盖 consensus+financial+repaired 第三实例 | **施工** | 零 DDL、纯代码、H1 已逐字证伪闭环；修后以 report_period/trade_date 推进为验收 |
| C2 | task_runs `rows_written` 改记 CH INSERT 回执，降级/写败不再记 SUCCESS（治 5 例假绿灯的账面面） | **施工**（第二批，独立于根因） | 假绿灯普查已证"SUCCESS 计数=fetched 透传"；不修则一切落库尺永远被任务态遮蔽 |
| C3 | realtime_snapshot INSERT 失败根因（registry 表名解析 vs 写权限） | **挂起排期**；解锁=一次带插桩实写复现获授权（属写操作，越本档只读红线） | 112 件降级件证明态在恶化，先 C2 止血 |
| C4 | news_sentiment_score：消费点切 window 或 score 续写 | **挂起排期**；解锁=Owner 裁真源方向（涉退役=注册表净删门位） | 值级失真但行数大，禁以"频次低"轻判；两案皆需方向裁定 |
| C5 | market_pattern_win_rate `updated_at` 新鲜度尺 + exit-1 栈定位 | 尺=**施工**；栈定位=**挂起排期**（解锁=授权跑物化取栈） | 无 DDL；尺先行防"表非空但停摆"再吞一次 |
| C6 | recon 运行心跳（run_id+last_success_at 落 governance.db 元表，使"空=干净"可证） | **施工** | 只新增观测元数据，不动资金面；真源收敛另立 C8 |
| C7 | STALE 13 例长批腿入 process_reaper_keep 白名单核对 | **施工**（先核对再登记，防"该保护未登记"误杀循环） | 已知先例在册，属收口非新裁定 |
| C8 | reconciliation_differences 双库同名收敛 | **挂起排期**；解锁=Owner（删库/视图化属生产流转+注册表净删） | 宪法 §5.2 门位 |
| C9 | weekly/monthly_hfq 补 `lineage_version` 列 | **禁排施工，必走 Owner 门**（DDL）→ §8 登记 | 补列=改表结构；本档只登记 |
| C10 | NEVER_RUN 10 腿清理（4 global 腿有他腿供数 kline_global·09-25 新鲜） | **挂起排期**；解锁=逐腿确认"冗余注册 vs 应跑未跑"（需跑 `--list` 与 scheduler 装载日志比对） | 禁以"没跑=可删"直判 |
| C11 | ch_writer/ch_reader 失败态与空态分离（返回 None/抛错二相） | **施工** | 病灶 C 在册未修；普查脚本已示范抛错型通道可行 |
| C12 | LLM/Ollama 服务恢复 | **方案封矿（本战役内）**：Owner 既定"LLM 腿没人重启是既有事实"且判看门狗不必保护；矿脉在业务链不在运维，重复提案封 | 解锁=Owner 显令 |

反驳者一问（对 C2 高成本候选）："改 rows_written 语义会不会打崩下游按 fetched 计数做补洞的调用方？"——答：消费面先 grep `rows_written` 再动，普查已列出读取点清单入长尾 L-4，风险可控不推翻方向。

## 8. 待 Owner 门位登记项（只登记，零操作）

1. **DDL**：`kline_weekly_hfq` / `kline_monthly_hfq` 补 `lineage_version`（实测列缺失，daily_hfq 已有；同族独占版本不变量破口，旧行可覆新）。
2. **建腿 vs 退役**：空壳表 9 张当分钟复核 count=0 —— `ipo_schedule` / `msci_adjustment` / `stock_valuation`（真身=c1_market，骨架未标库）/ `stock_candidate_pool` / `market_index_meta` / `margin_target_adjustment`（以上 6 张经 grep 确证**未登记** `src/zephyr/data/config/known_data_gaps.yaml`）+ 已在册但同态的 `suspend` / `etf_benchmark`。
3. **真源收敛**：reconciliation_differences（governance.db 写 vs c1_market 同名表读）；consensus_daily 主表 vs `_repaired` 双面孔；news_sentiment_score vs window（C4）。
4. **服务处置**：Ollama 11434 当分钟 connect timeout、无 boot 后自动恢复义务——仅报事实，恢复=Owner 令（勿顺手重启）。
5. **已裁不重提请**：TradingWatchdog 注册即禁用=Owner 判"不必保护"在先，本档只记现状不提案。

## 9. 长尾矿脉清单 + 已查无记录

- L-1 tasks.yaml 270 vs 骨架 271：枚举口径差 1，逐条 diff 未做（已查无=差值不影响任何单条判定，但登记防漂移）。
- L-2 pattern_win_rate exit-1 真实栈（需授权执行）。
- L-3 recon_runner 调用链：`scripts/run_post_settlement.py` 是否真调三方对账未读到（文件未定位，glob 超时；下一步按 classify 后定点读）。
- L-4 `rows_written` 字段消费方全仓清单（C2 前置）。
- L-5 DEFERRED_PERSISTENCE 14 例/近 30h 的落表分布与回灌闭环（骨架 §5.6 遗题，本档未吞）。
- L-6 NEVER_RUN 10 腿的调度装载面核对（C10 前置）。
- L-7 etf_benchmark_refresh 表 date 列 ALL_NULL——列名与 date_col 声明是否错位待 DESC 定点核。
- 已查无：`news_sentiment_score` 排产写腿（scripts+src 双 grep 零命中排产面，仅回补脚本）；`known_data_gaps.yaml` 对 6 张新空壳的登记（grep 全零）；全仓"任务态×落库态"交叉假绿灯尺（普查脚本为首例实例，此前零存在）。
- 矿脉状态：母节点三条深度脉（五段拆解/假绿灯全量/共因定位）均已到可判定底；L-2/L-3/L-5 需授权或属他班矿口，非本档轮次上限性关停。
