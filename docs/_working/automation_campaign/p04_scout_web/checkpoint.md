---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: ④全网战法矿工席·游标
---

# 游标

cursor: **本班（p04-08）按复牌交两枚新轴卡＝卡18 隔夜-日内时段分解拉锯动量（时段结构轴；A股符号与美股相反且一手证据互斥＝方向不代裁）＋卡19 已实现偏度三阶矩（高阶矩轴；skew/偏度 在 strategy_registry.yaml 存量 0 命中＝完全空白本体）；两卡去重闸本班逐词实跑通过（计数在册），正交闸本班缺席＝开班 commit_pct=87.14% 高水位＋个股多日滚动 panel 物化撞在册 CH 7.14GiB 墙（memory ch-memory-wall-panel-load-500）＋⑥席-10(89.66)/⑧B(94) 本窗全程零 CH 零闸同律；池面本班已实跑 pool-report=32 员/1472 共同日/PR=5.3328（与 06/07 班在册逐字同＝池已物化、闸可用，缺席只在候选不在池）；gate 命令写进两卡 orthogonal_gate_zh 待 ⑤ 物化 csv(date,sig) 后补跑。计产按轴＝2 条新轴，方向均待 ⑥ 带独立外部先验另立 card_id（遵 ⑨ 令不翻号不反挖）。**
last_run: 2026-10-15 20:1x（date 实测，落笔 20:11:56）
last_batch: 20261015-p04-08（会话 st-qoder-p04-1015-08）
notes: 下一班必读六条：
①两卡都是横截面选股因子（panel 档），其『市场级可闸代理』是本席构造出来的派生形（卡18=时段动量之差 overnight-intraday 拉锯差分；卡19=偏度截面离散度 p90-p10），不是命题原形——引用者禁跨面把市场级读数当选股证据，正交闸面与个股面两条腿不同分母。
②时段拆分硬依赖复权：kline_daily.adj_factor 系恒 1 死列（在册），卡18 隔夜 close_{t-1}→open_t 必须取 c1_market.kline_daily_hfq（本班 DESCRIBE 实测 17 列：trade_date/symbol/open/close/high/low/volume/amount/amplitude/pct_change/change/turnover/data_source/lineage_version/ingest_ts/exchange/symbol_canonical；min/max(trade_date)=1990-12-19/2026-10-15）；hfq 面引擎本班未实测，⑤ 定 FINAL 前先 get_table_engine_strict（kline_daily=ReplacingMergeTree 不自动迁移到 hfq）。hfq 表族有 _recalc 与 __preeng_backup_20261007 并生件，取数锁真源一张防重灌（在册 repolluting-incremental-leg）。
③方向互斥证据（本席为何两卡均不预注册方向）：卡18 Lou-Polk-Skouras 美股隔夜反转 vs 清华 2025 论文『A股隔夜负/日内正』vs CSDN 实测『A股隔夜动量正』三者打架；卡19 Amaya 美股负 vs VIP A股『偏度关系与美不同』。均他方读数非本席检验，须 ⑥ 带独立外部先验另立 card_id 定方向后开考，禁在本卡翻号。
④去重闸相邻面申报：intraday_close（open→close，FCT-INTRADAY-030 IC=-0.0182）是卡18 拆分式的『日内段』孪生腿（本卡取隔夜段累计）；偏度与池内波动成员同输入不同统计量（三阶矩 vs 二阶矩）。正交闸只对池 32 员负责，本席同族 unlanded 旧卡与上述相邻均归 ⑥/⑨ 并员评估，本席不自证清白。
⑤上一班在册条仍有效（本班未复测，勿重复申请）：Corwin-Schultz 日频恒零禁重烧同式；前瞻/滚动窗右端须把日历铺满勿被交易日历截零；YAML 自由文本一律块标量(>-)禁双引号单行、中文引用用「」；分数册口径现 104 行/80 distinct card_id（⑨席15班）；GitHub 未认证 403 风险；Semantic Scholar graph API 前班两次 429；kline_index 无 pct_change 列且 2026-07-02/03 close 逐位同＝前值复制桩；*_pct 分位列＝前视。
⑥高水位节拍：本班起批实测 commit_pct=87.14%⇒全程零 CH 探针、零 panel 物化、零正交闸（只跑读 CSV 的 pool-report 与 system.columns 元数据）；下一班若 reaper 报 commit 回落到安全窗，第一件事＝把卡18/卡19 的市场级代理 csv 物化出来补跑正交闸，再谈第三枚卡。主区 index 现存 10 枚自家 web_cards 的 staged-deletion（p10-10 第九单呈批 17 同族＝他席在途），本班未代复位，走队列正门不直连。

<!-- P10-1016-01-FORCE-CLOSEOUT -->
> **⑩线长席强制收班提醒（2026-10-16 01:5x 实测追加，指令面-only，未改任何判据）**
> 本席 `ledger.md` 里 `[BLOCKER]` 行数实测 **0**（同尺负对照＝⑤席 8 行／⑨席 13 行命中；本席 ledger 正文 151877 字节内连 `BLOCKER` 子串都零命中⇒不是谓词伪空，是真未收班）；10-16 00:53 班同读数＝**连续两班 0 行** ⇒ 依 SOP §3⑩ 工序 9 追记本提醒。
> 下班收班三件（缺一＝本班不算收班）＝①ledger.md 追加至少一行 `[BLOCKER] <YYYY-MM-DD>|<席+班号>|<工具缺陷|判据缺失|数据问题|流程问题|需Owner>|<一句话>|<file:line 或路径>|<要谁做什么>|<高|中|低>`（零问题必写 `[BLOCKER] <date>|<席+班号>|无`）；②提交只走 `python scripts/commit_queue.py` 上游的 `git_commit.py --session <sid> --files <自家清单> --enqueue`（禁裸 git commit／禁从主区 index 直连）；③release 自家 claim＋注销心跳＋台账记实耗分钟。
