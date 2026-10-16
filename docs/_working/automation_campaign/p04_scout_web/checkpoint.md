---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: ④全网战法矿工席·游标
---

# 游标

cursor: **本班（p04-02，会话 st-qoder-p04-1016-02，batch 20261016-p04-02）产两枚空白轴新卡＝卡20 期权隐含波动率期限结构斜率（波动率期限结构轴）＋卡21 龙虎榜机构席位净买入占比（资金面分户轴）；两卡正交闸本班**实跑并 pass**（0.1612 vs ti_ew_garman_klass_20_v1／0.1799 vs lu_count，池 32 员实存）＝把 1015-08 游标第⑥条「水位回落先补闸」当班结清，未留给下班；去重闸逐词实跑（strategy_registry.yaml 162 条：IV 期限结构簇全 0 命中且 basis 的 3 命中经逐行核＝全是字段名 card_state_frozen_basis 假阳性；龙虎榜 2 命中经逐行核＝均为 MOD-L05-001 复合卡成分项＝「独立本体空白、复合面相邻」）；两卡方向**均不预注册**（卡20 三源无符号、唯一带方向的 Yoon-Ruan-Zhang 2022 对象是 VIX 期货；卡21 三源互斥＝+1.7% 正向／V 字型／净卖出腿更强）。本班另排掉一枚鬼班（st-qoder-p04-1016-01 被运行面掐死，孤儿心跳 daemon pid 28048 仍在自跳，三证在册）并把其遗物定性＝两枚两融候选早已被闸判重（0.5535/0.5678）、三枚大宗 csv 只有 46 行的根因＝block_trade/dragon_tiger 主表跨度仅 2026-08-07 起。计产按轴＝2 条新轴。**
last_run: 2026-10-16 23:0x（date 实测，本班起批 21:30:09）
last_batch: 20261016-p04-02（会话 st-qoder-p04-1016-02）
notes: 下一班必读八条：
①**取号先查两处**：台账面 `grep -o "st-qoder-p04-1016-[0-9][0-9]"` 与 `.runtime/sessions/` 目录面可能给不同班号（本班即遇到：台账 0 命中 vs 会话目录已有 01）；本席并集+1 取 02，⑩ 的取号尺裁定尚未回。开工第一件事＝按在册三证法判前班死活（tasklist 父 daemon／idle_seconds 是否恰等于 tick 间隔／写域是否零产出），**勿只读心跳末行**——说谎心跳已在本席自家会话面第二次复现。
②**seat_type 是英文枚举**（broker／institution／connect，本班 GROUP BY 实测），情报里的「机构专用／陆股通／游资／私募新席位」无一一对应；按中文子串判定会产出**恒 0 序列**并让正交闸假 pass（本班首跑就踩，处方＝物化脚本必打 `zero_value_days` 这一行自检）。
③**跨度分水岭**＝c1_market.dragon_tiger_seat 自 2022-01-04 起 623,661 行可用；而主表 dragon_tiger（含 reason/net_buy）与 block_trade 仅自 2026-08-07 起（2,785／1,794 行）＝凡「上榜原因／金额分布／大宗折价」类构造现只有 46 个交易日，**别在本窗再烧第三次**（鬼班已烧过一次并留下 46 行 csv），先等 ① 席回补或改判本体源。
④**option_iv_surface 三面实测**：419,801 行／2019-01-02→2026-10-15；option_type 域＝put 197,562／call 197,428／**空串 24,811（必须过滤）**；underlying 头部＝510050.SH 154,709／510300.SH 111,937／510500.SH 55,217／588080.SH 44,998／588000.SH 42,627／159915.SZ 2,850／159922.SZ 2,605／159901.SZ 2,514；**quality_flag 恒 1＝无判别力禁当筛**；表内**无标的现价列**⇒ATM 只能按 |delta-0.5| 近似。
⑤**本班未产的第三轴＝股指期货基差/年化贴水**（材料已在册：中金研报转载页 200、集思录 471508/504383 200、NBER w13249 Green OA 200、MIT 仓 index-futures-basis 与 ETF-Futures-Basis-Arbitrage-Reproduction 2★/10-02）；本库 `kline_futures` 仅 8,298 行（2017-01-17→2026-10-12）＝**跨度薄**，动手前先做一次合约符号密度普查（IF/IH/IC/IM 是否齐全、有无主力连续拼接前视），别默认 CFFEX 四品种可用。
⑥**正交闸池面**＝`.runtime/tmp/p04_06_pool` 32 枚 csv 本班实测可用；本班闸命令模板＝`python scripts/backtest/fexam/signal_orthogonality.py gate --candidate .runtime/tmp/p04_1016_02/<x>.csv --pool .runtime/tmp/p04_06_pool --gate 0.3`。⚠ tmp 是 24h TTL 面，下班须先 ls 复核池与候选是否还在，禁按游标记忆断言存在。
⑦1015-08 在册条继续有效（本班未复测，勿重复申请）：Corwin-Schultz 日频恒零禁重烧同式；前瞻/滚动窗右端须铺满日历；YAML 自由文本一律块标量(>-)、中文引用用「」；分数册勿入袋（⑩ 第十三单通令）；kline_daily.adj_factor 恒 1 死列、卡18 须走 kline_daily_hfq；*_pct 分位列＝前视；kline_index 2026-07-02/03 close 逐位同＝前值复制桩。卡18/卡19 的方向仍待 ⑥，本席不翻号。
⑧本班袋＝q-20261016-st-qoder-p04-1016-02-000x（files＝两枚新卡＋ledger＋游标，**不含** capability_canonical_file_registry.yaml＝热册 status=MM 含他席在途，令牌走 PG 第三源）；1015-08 那只 dead 袋本班**未 requeue 未归档**，理由在册 §一（requeue 会把他席对两枚 1015 卡的 staged 删除洗进我方袋）；下班若见该 dead 袋仍在＝正常，等本班袋落地后再按 --content-level 销账。

<!-- P10-1016-01-FORCE-CLOSEOUT -->
> **⑩线长席强制收班提醒（2026-10-16 01:5x 实测追加，指令面-only，未改任何判据）**
> 本席 `ledger.md` 里 `[BLOCKER]` 行数实测 **0**（同尺负对照＝⑤席 8 行／⑨席 13 行命中；本席 ledger 正文 151877 字节内连 `BLOCKER` 子串都零命中⇒不是谓词伪空，是真未收班）；10-16 00:53 班同读数＝**连续两班 0 行** ⇒ 依 SOP §3⑩ 工序 9 追记本提醒。
> 下班收班三件（缺一＝本班不算收班）＝①ledger.md 追加至少一行 `[BLOCKER] <YYYY-MM-DD>|<席+班号>|<工具缺陷|判据缺失|数据问题|流程问题|需Owner>|<一句话>|<file:line 或路径>|<要谁做什么>|<高|中|低>`（零问题必写 `[BLOCKER] <date>|<席+班号>|无`）；②提交只走 `python scripts/commit_queue.py` 上游的 `git_commit.py --session <sid> --files <自家清单> --enqueue`（禁裸 git commit／禁从主区 index 直连）；③release 自家 claim＋注销心跳＋台账记实耗分钟。
