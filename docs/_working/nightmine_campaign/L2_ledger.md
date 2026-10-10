---
ttl: task_bound
title: L2 挖矿车道台账（entry_flow/L3 个股层，26 节点）
created: "2026-10-10"
sid: st-nightmine-20261010
lane: L2
family_id: NIGHTMINE-CAMPAIGN
---

# L2 台账——TDM 个股层（L3）挖矿

工作根=工棚 `D:/ZephyrAlpha/.aidrafts/st-nightmine-20261010`。
名册真源=`docs/_working/nightmine_campaign/00_lane_roster.yaml`（lane=L2，26 节点）。
共用作业簿=`01_mining_brief.md`；方法论=`mining_sop_policy.md` v1.7.0（§2 六向/§3 结构枯竭/§5 四闸/§7.5 断言纪律）。

## 0. 环境真相与一次返工（如实记录，非降格理由）

- 本车道首轮挖掘（节点 dump + CH 探针 + 22 张卡 + 台账首稿）**未落盘**：工棚在 06:27:10 被重建
  （L3 骨架 26 件 mtime 全等于 06:27:10，campaign 目录 06:34 生成），首轮流件被连坐清除。
- 取证（三条独立通道，禁凭记忆）：
  1. `ls docs/03_modules/_domain_backtest/exam_cards/entry_flow/L3/ | wc -l` = **26**（仅骨架，无 `__NN_` 手工卡）；
  2. `find . -maxdepth 6 -name "L2_ledger.md" -o -name "l3_nodes.json" -o -name "*换手率分层*"` = **0 命中**；
  3. Write 工具落盘性探针：写 `L3/_write_probe.yaml` → Bash `ls` 实测存在（06:53）→ 探针删除，
     判定=**写通道正常，首轮系工棚重建时被抹**（非写工具故障）。
- 次轮（本文件）全程"写后即进程外核实"（`ls`/`wc -c` 复核），并**重新实测全部数据断言**，
  未沿用首轮任何未经复测的数字。
- 工棚 `.runtime` 是指向主仓 `.runtime` 的 junction（`D:\ZephyrAlpha\.runtime\...` 在 Read 白名单外），
  临时件读写一律走 shell；临时件目录=`.runtime/tmp/st-nightmine-20261010/`。

## 1. 实测数据面板（本车道唯一取数真源，全部为本轮命令实测）

探针脚本=`.runtime/tmp/st-nightmine-20261010/l2_ch_{cov,cov2..6,backend}.py`，
读库通道=`scripts/backtest/fexam/ch_data.py`（ch_query_df，禁裸 duckdb；TSV 位置列名 c1..cN）。
冻结窗（作业簿立法，禁改）：IS `2019-01-04..2023-12-31` / OOS `2024-01-01..2025-09-09`。

| 表（CH 全名） | 实测覆盖 | 窗内量（去重口径） | 本车道用途 |
|---|---|---|---|
| `c1_market.kline_daily`（不复权） | — | 单日 2019-06-05=3,622 符号 / 2023-06-05=5,200 / 2024-10-08=5,355 / 2025-06-05=5,438 | 涨停/炸板/一字板判定（价与涨跌停价同量纲） |
| `c1_market.kline_daily_hfq` | 1990-12-19..2026-09-30；全表 10,098,785 行/5,916 符号/8,736 日 | 窗内 5,583,635 行=5,583,635 唯一(symbol,日)，1,622 交易日，3,944 符号 | 前向收益目标面 + 量能 |
| `c1_market.stk_limit` | 2015-01-05..2026-10-09；9,254,772 行/5,831 符号/2,857 日 | 2023-06-05 单日 5,199 行=5,199 符号（PIT 无重复） | 涨跌停价/幅度、st_flag、board |
| `c1_market.technical_indicator` | 2019-01-02..2026-09-30；404,675,630 行/14,357 符号 | 窗内 134,772,727 行；**去重后 symbol-day** 2019=647,746 … 2024=910,208；`chips_winner`>0 覆盖≈symbol-day 的 97-100% | 单指标宽表（趋势/均线/MACD/RSI/ATR/OBV/MFI/chips_*/conc_*） |
| `c1_market.stock_daily_basic` | **2021-01-04**..2026-10-09；7,118,522 行/5,785 符号 | IS 段=3,492,273（2021-2023）/ OOS=2,200,180 | 市值/流通股本/换手率——**2019-01-04..2020-12-31 全缺** |
| `c1_market.stock_basic` | 2015-01-05..2026-10-09；9,047,409 行/5,785 符号 | 板块分布（全史 distinct 符号）：沪主板1,803/深主板1,604/**创业板1,409 仅自 2026-08-14**/科创板621（2019-07-22 起）/**北交所348 仅自 2026-09-15** | 采集宇宙在册唯一读取源——**窗内创业板/北交所零覆盖=本域头号口径雷** |
| `c1_market.money_flow` | **2021-01-04**..2026-10-09；5,993,328 行/5,782 符号 | 按年 symbol-day：2021=1,058,846/2022=1,146,266/2023=1,209,660/2024=1,233,202/2025(至09)=861,547 | 主力/大单净额占比——**IS 前段 2019-01-04..2020-12-31 缺** |
| `c1_market.dragon_tiger_seat` | **2022-01-04**..2026-10-09；622,365 行/5,998 符号/1,152 日 | 按年 symbol-day：2022=14,589/2023=12,908/2024=18,111/2025=16,352；seat_type 枚举=broker 562,116/institution 39,250/connect 20,999 | 席位定性——**IS 前段 2019-01-04..2021-12-31 缺** |
| `c1_market.suspend` | **2026-09-04..2026-09-23**，36 行/11 符号 | 冻结窗内 0 | 停牌旗标——**全窗缺**（需以日历缺口重建代理） |
| `c1_market.auction_snapshot` | **2026-06-01..2026-09-30**，288,909 行/6,590 符号/56 日 | 冻结窗内 0 | 竞价量价——全窗缺 |
| `c1_market.auction_book` | **2026-07-21..2026-09-30**，3,690,473 行/30 日 | 冻结窗内 0 | 竞价五档/笼子——全窗缺 |
| `c1_market.kline_5min` | trade_time **2021-09-01 09:35..2026-10-09 15:00**，296,122,159 行 | IS 段 2019-01-04..2021-08-31 缺 | 涨速/盘中量比 |
| `c1_market.limit_up_pool` | **2026-09-01..2026-10-09**，1,426 行/23 日 | 窗内 0 | 封单额/封板秒数/开板次数——**历史全缺，须由不复权行情推导** |
| `c1_market.limit_up_down` | **2026-07-20..2026-10-09**，5,397 行/54 日 | 窗内 0 | 同上 |
| `c1_market.daban_engine_load` | **2026-09-01..2026-09-28**，1,701 行/19 日 | 窗内 0 | 打板引擎 PIT 负载表——打板链卡按窗判 blocked |
| `c1_market.daban_board_event` | 2026-09-01..2026-10-09，1,767 行 | 窗内 0 | 板事件 |
| `c1_market.stock_candidate_pool` | **count()=0（空表，min/max 返回 1970-01-01）** | 窗内 0 | 候选池/盘前预检消费面——空表非查询静默败（同行 count 成功返回） |
| `c1_market.emotion_index` | 1991-06-10..2026-10-09，8,661 行 | 窗内 1,622 行（stage 全为 `close_final`，每日 1 行） | 环境开关档位序列 |
| `c1_market.kline_index` | 1990-12-19..2026-10-09，3,104,162 行 | 000001/399001 窗内各 242/243/242/242/242/242/168 日（2019..2025）→ 两市成交额可算 | 环境开关成交额轴 |
| `c1_market.kline_sector_880` | **2020-03-17**..2026-10-08，785,204 行/729 板块 | IS=289,365/OOS=288,254 | 板块强度/行业相对强度——2019 全年缺 |
| `c1_market.sector_constituent` | update_date **2026-07-22..2026-10-01**（6 个更新日），323,175 行 | 窗内 0 | 题材/板块归属历史缺 |
| `c1_market.concept_board_constituent` | valid_from **2026-08-10..2026-10-09**，37,891 行 | 窗内 0 | 题材纯正度历史缺 |
| `c1_market.index_constituent` | 2005-04-29..2026-09-30，705,916 行；窗内 80 个月末快照 | index_code 实测=`000300.SH`(949符号,2005起)/`000905.SH`(1,800)/`000906.SH`(2,013)/`000852.SH`(2,839)/`000985.SH`(仅2026) | 指数宇宙 PIT |
| `c3_fundamental.share_unlock` | unlock_date 2010-01-04..2027-09-29，30,264 行 | 窗内解禁事件 15,668 条/5,531 符号 | 负面否决第七检（解禁>5%）可考 |
| `c3_fundamental.shareholder_count` | end_date 1992-12-31..2026-09-30，514,690 行 | 按年 distinct 符号 2019=3,804…2024=5,485（季频） | 筹码集中度代理（户均持股）可考 |
| `c1_market.market_pattern_event` | anchor_trade_date **2021-09-01**..2026-09-30，28,587,647 行/5,715 符号 | IS 前段缺 | K线/反转形态事件（实测 pattern_id 头名=X-短线 2,335,308…CDLENGULFING 831,253） |
| `c3_fundamental.income_statement` / `cashflow_statement` | 存在（列实测含 net_profit_incl_minority / ocf_net / report_period / announce_date） | 无 balance_sheet 表（`%statement%` 枚举仅此二表） | Sloan 高应计只能取"净利−经营现金流"代理口径 |

**判据性实测样例（涨停/炸板/一字三口径均可由 `kline_daily`×`stk_limit` 重建）**：
- 封板家数：2023-06-05=74、2024-10-08=893（`close>=limit_up-0.011`）；
- 炸板家数：2023-06-05=23、2024-10-08=2,268（`high>=limit_up-0.011 AND close<limit_up-0.011`）；
- 一字板家数：2024-10-08=41/5,355（`open=high=low=close AND close>=limit_up-0.011`）。
- **量纲陷阱（新发现，已写进卡）**：`kline_daily_hfq` 是后复权价，与 `stk_limit.limit_up`（不复权价）
  直接比较会得 3,882/5,199 的荒谬"涨停家数"；涨停族判据必须走 `kline_daily`（不复权）。

## 2. 立法与口径决定（本车道，供考试车道接线）

1. **负向假说的门柱写法**：执行器 `calibration_exam.judge()` 对 `ic_mean`/`ic_ir` 做**带符号下限**比较
   （`ic < ic_mean_min` 即 fail），无 abs 语义。故否决类/买不进类假说一律**反向构造信号**
   （signal = −1× 风险分位），在 `signal_derivation` 写死取负，门柱保持正向地板，
   禁把 `ic_mean_min` 写成负数（=挪门柱）。
2. **宇宙口径写死**：`data_binding.signal_derivation` 必须显式声明宇宙重建方式
   （窗内 `stock_basic` 无创业板/北交所行 → 以 `kline_daily.exchange`+symbol 前缀重建主板/创业板/科创板集合，
   北交所整段不入窗；ST 判定用 `stk_limit.st_flag` 而非 `stock_basic.name`）。禁裸扩口径。
3. **停牌代理**：`c1_market.suspend` 窗内零行 → 停牌以"交易日历有日、该符号该日无行情行"重建，
   写进 `signal_derivation`，并在 `data_window_evidence` 记实测缺段。
4. **前向收益口径**：panel 卡 primary=`stock_fwd_ret_1`（T+1 开盘可成交→T+2 收盘，`kline_daily_hfq`），
   series 卡 primary=`next_day_index_return`（`kline_index` 000300 close）。禁 close-to-close 前视。
5. **去重**：一切 CH 面板读取按 `argMax(col, ingest_ts) GROUP BY symbol, trade_date` 或 `FINAL`；
   `technical_indicator` 原始行含多版本（2024 年 raw 29.8M 行 vs 去重 910K symbol-day），
   不去重=IC 被复制样本污染。

## 3. 逐节点六向台账（26 行）

①上游=TDM 节点全字段实读（`.runtime/tmp/.../l2_probe_out.txt`，26 节点逐 JSON 摘录）；
②下游=`grep -rl <node_id> src scripts config docs/01...`（排除 TDM 本体），数字=命中文件数；
③算法=族级外部引用（§6）+ 近亲卡对照；④后端=module_ref 件存在性 + 持久产物枚举；
⑤呈现=只登记；⑥数据=§1 实测面板。

| node_id | ①上游 | ②下游 | ③算法 | ④后端 | ⑤呈现 | ⑥数据 | 新卡 | 族 | mined_out? | blocked 原因 |
|---|---|---|---|---|---|---|---|---|---|---|
| TDM-C-L3 | 判据句=市值+流动性+7日动量+深度滑点（not_built） | 2（无 py 消费，仅图/册） | 币圈截面动量族外部引用未挖（长尾） | 无 module_ref（red_reason=not_built） | 登记：无前端挂载需求 | crypto_kline_daily 仅 2025-08-08 起 19,801 行 | 1 | calibration | 否 | 数据缺窗+未施工双缺 |
| TDM-E-L3 | 枢纽：5000+→10-20 压缩率 3000→10 业界参照 | 21（chip_engine/aggregator/snapshot 等） | 漏斗压缩族外部未挖（长尾） | 六 sleeve 挂载全 proposed、零 verified 产物 | 登记 | 池表实测零行（在册 empty_table 缺账） | 1 | ablation | 否 | 实现缺（逐段产物零落库） |
| TDM-E-L3-01 | 剔除六线：停牌/ST/退市/上市<60日/市值<30亿/成交<5000万 | 2 | 流动性与规模族：外部未挖（长尾） | instrument_master.py（MOD-DATA-069）存在 | 登记 | stock_basic 窗内创业板/北交所零行；stock_daily_basic 2021-01-04 起；kline_daily 全窗 | 3 | calibration×2+comparison | 否 | 市值线缺 2019-2020 |
| TDM-E-L3-02 | 九段主链，每段砍 50-70% | 4（pool_tier_maintenance 消费） | 漏斗分段族外部未挖（长尾） | selection_funnel.py（MOD-SIG-086）存在、零产物 | 登记 | 形态段依赖表 2021-09-01 起 | 1 | ablation | 否 | 实现缺+形态段缺 |
| TDM-E-L3-03 | 双池并行打分再合流过三维共振 | 3 | CYQ/涨停族可用，双池合流外部无对等文献（查无） | 无 module_ref（structural 组骨架） | 登记 | 代理分所需列全窗可用 | 1 | ablation | 否 | 无（preregistered） |
| TDM-E-L3-03-1 | 五分制：涨停基因/题材纯正度/龙头定位/情绪周期位置/分时强度 | 3 | 涨停族：Jiang&Li 2026 涨停行为经济学（内部 lookup 命中）+CNKI 2024 涨跌停信号传递 | fine_scoring_engine.py（MOD-SIG-048）存在 | 登记 | 涨停可重建（stk_limit×不复权）；题材归属窗内 0 行 | 2 | calibration×2 | 否 | 题材线缺窗；龙头/情绪/分时三判据未立卡（长尾） |
| TDM-E-L3-03-2 | 五分制：趋势/量能/相对强度/回踩质量/筹码 | 3 | 趋势与量能族外部引用未挖（长尾） | quant_short_term_strength_engine.py（MOD-SIG-034）存在 | 登记 | ma_*/volume 全窗；880 板块 2020-03-17 起；行业归属窗内不全 | 3 | calibration×3 | 否 | 相对强度缺段；回踩质量与筹码位两判据未立卡（长尾） |
| TDM-E-L3-03-3 | 三维共振（趋势/资金/形态）至少两维 | 3 | signal_conflict_resolver 内部先例（MOD-SIG-010） | 件存在、零产物 | 登记 | 资金 2021-01-04 起、形态 2021-09-01 起 | 1 | ablation | 否 | 两维缺 IS 前段 |
| TDM-E-L3-04 | 七检一票否决（暴雷/立案/减持/解禁/商誉/配股/高应计） | 4（negative_veto.py 自引） | Sloan 应计族外部未挖（长尾）；解禁族 2 源（§6） | negative_veto.py（MOD-SIG-137）存在、零产物 | 登记 | 解禁全窗 15,668 事件；减持/商誉/立案无 CH 表（文档面在册） | 3 | calibration×2+ablation | 否 | 三检无表属缺表非缺段；暴雷/配股两检未立卡（长尾） |
| TDM-E-L3-05 | 顺位：妖>龙>中军>核心>趋势>跟风 | 3 | 龙头/顺位族外部仅散户叙事（待验证，§6） | selection_confidence.py（MOD-SIG-141）存在 | 登记 | 连板高度可自建（实测封板 74/893 家） | 1 | calibration | 否 | 无（六档语义仅连板代理，余为长尾） |
| TDM-E-L3-06 | 六段×四开关查表（首板/短线/波段/收紧） | 5（environment_switch/sector_ecology_judge） | 情绪档位族归 L1 车道（边界登记不越界） | environment_switch.py（MOD-SIG-138）存在 | 登记 | emotion_index 窗内 1,622 行无缺日；两市成交额全窗 | 1 | calibration(series) | 否 | 无（其余三轴未立卡=长尾） |
| TDM-E-L3-07 | 三链并行、不共享中间结果 | 8（aggregator/auto_mount） | 多因子链族（§6 长尾：IC 加权外部引用未挖） | 三链件均存在、零候选产物 | 登记 | 池表零行；打板负载表仅 2026-09 | 1 | ablation | 否 | 实现缺（sleeve 产物不落库） |
| TDM-E-L3-07-1 | 五步漏斗：板块前3→涨停→剔烂板→封单质量→龙头定位 | 6 | 涨停族 3 源（§6） | daban_sleeve_strategy.py（MOD-L05-001）+ daban_engine_load 腿在册 | 登记 | 烂板可代理重建（炸板实测 23/2,268）；封单额窗内 0 行 | 2 | ablation×2 | 否 | 封单步缺窗；板块强度步与龙头步未立卡（长尾） |
| TDM-E-L3-07-2 | IC 衰减加权合成、前20+单行业≤4 | 5 | IC 加权族外部未挖（长尾） | multifactor_synthesis.py（MOD-L02-011）存在 | 登记 | 因子列全窗（去重后 0.65-0.91M symbol-day/年）；行业归属窗内不全 | 2 | ablation×2 | 否 | 中性约束缺归属；月度权重校准（C3-04）未立卡（长尾） |
| TDM-E-L3-07-3 | eventdriven 提前3日/topn 20日动量/default 网格；**verified 节点** | 5 | 动量族外部未挖（长尾） | event_driven_sleeve_strategy.py 存在 | 登记 | 动量全窗可算；calendar_event 仅 2021-08-20 起 | 1 | calibration | 否 | 不改既有 verified 结论；eventdriven 与 default-equity 两链未立卡（长尾） |
| TDM-E-L3-08 | 三来源合成+容量 10-20+否决只标记 | 7（aggregator/snapshot/preflight） | 组合容量族外部未挖（长尾） | candidate_pool_aggregator.py（MOD-SIG-142）+ candidate_pool_snapshot.py 写腿均存在 | 登记 | stock_candidate_pool 实测 0 行（在册缺账 id=stock_candidate_pool_empty_table_no_leg，status=open） | 1 | ablation | 否 | 注入源零注册致表空 |
| TDM-E-L3-09 | Tier1/2/3 升2日/降5日/剔10日状态机 | 4 | 池分层状态机族外部无对等（查无） | pool_tier_maintenance.py（MOD-SIG-139）存在；TDM 原文在册 M-41 欠账 | 登记 | tier_slot 列在但表 0 行 | 1 | calibration | 否 | 状态历史永不落库 |
| TDM-E-L3-10 | 五查：停牌/一字/笼子/权限/资金一手 | 4（tradability_preflight.py） | 可成交性族外部未挖（长尾） | tradability_preflight.py（MOD-SIG-151）+ 盘前腿已通电（2026-09-27 在册） | 登记 | 一字可判（实测 41/5,355）；suspend 窗内 0 行；盘口窗内 0 行 | 2 | calibration×2 | 否 | 停牌缺；笼子/权限/资金一手三查未立卡（长尾） |
| TDM-E-L3-11 | 日内双通道（竞价+涨速），与盘前互补 | 4（周期图生成器） | 日内动量族外部未挖（长尾） | 无 module_ref（structural） | 登记 | 5min 2021-09-01 起、竞价 2026 起 | 1 | ablation | 否 | 两通道双缺段 |
| TDM-E-L3-11-1 | 竞价量比>5+涨幅2-5%+大单主导；9:25 前不作依据 | 4 | 竞价族外部未挖（长尾） | auction_microstructure_analyzer.py（MOD-SIG-089）存在 | 登记 | auction_snapshot 仅 2026-06-01..09-30 | 1 | calibration | 否 | 全窗缺 |
| TDM-E-L3-11-2 | 5min 涨>2%+量比>3+非跟风；黄金窗 9:30-10:30；尾盘差 | 2 | 涨速族外部未挖（长尾） | intraday_volume_orderflow.py（MOD-SIG-093）存在 | 登记 | kline_5min 缺 2019-01-04..2021-08-31 | 1 | calibration | 否 | IS 前 2/3 缺；尾盘档单立为长尾 |
| TDM-E-L3-12 | 四维验证，至少三维正面 | 6 | 多维共振族外部未挖（长尾） | 无 module_ref；挂载 MOD-SIG-092/096/103/127 | 登记 | 四维中仅筹码维全窗可用 | 1 | ablation | 否 | 三维缺段 |
| TDM-E-L3-12-1 | 大单净额/成交额≥20%；DDE 连3日净流入；单日>50% 警惕对倒 | 2 | 资金流族 2 源（含"聪明钱陷阱"反例，§6） | capital_flow_pattern_analyzer.py（MOD-SIG-022）存在 | 登记 | money_flow 2021-01-04 起（缺 2019-01..2020-12） | 1 | calibration | 否 | 缺 IS 前段（三判据句已并卡） |
| TDM-E-L3-12-2 | 一线游资/机构专用/拉萨天团三风格定性 | 2 | 席位族 2 源（均为待验证级，§6） | seat_pattern_analyzer.py（MOD-SIG-056）存在 | 登记 | dragon_tiger_seat 2022-01-04 起；seat_type 无游资枚举（须 seat_name 白名单） | 1 | calibration | 否 | 缺 IS 前三年+白名单工程未做 |
| TDM-E-L3-12-3 | 获利盘>90%且集中=拉升期；<30% 高位换手=派发；单峰密集最干净 | 5 | CYQ 族 2 源+内部 lookup 3/3（§5/§6） | chip_distribution_engine.py（MOD-REGIME-005）2026-10-04 获利盘接线在册 | 登记 | chips_winner/conc_70/conc_90 去重后全窗覆盖≈100%；直方图面不存在 | 3 | calibration×3 | 否 | 单峰密集缺产物；conc_70/90 口径对照卡与 chips_avg_cost 成本均线族为长尾 |
| TDM-E-L3-12-4 | 缠论二/三买+W底头肩底+前高突破平台 | 2 | 缠论内部命中（中泰 2022 一类买点胜率 76.53%；同行评审缺，§5） | chanlun_structure.py（MOD-SIG-072）+6 挂载件存在、零产物 | 登记 | market_pattern_event 2021-09-01 起；无缠论表 | 2 | calibration×2 | 否 | 形态缺段+缠论缺产物；平台突破/前高判据未立卡（长尾） |

**六向结论口径**：26 节点全部完成六向各一轮留痕（无一向缺失）；
**mined_out 判定=0 个节点**——依 §3 结构判据（六向全"已查无/已入卡"且无未挖长尾）不成立，
长尾明列于 §7，禁以"已出一轮/卡数已多"降格封矿。

## 4. 新卡清单（39 张，目录=`docs/03_modules/_domain_backtest/exam_cards/entry_flow/L3/`）

可考（`status: preregistered`，15 张）：
`TDM-E-L3-01__calibration__02_成交额下限剔除` / `TDM-E-L3-01__comparison__04_宇宙口径完整性对照` /
`TDM-E-L3-03__ablation__02_双池代理合成` / `TDM-E-L3-03-1__calibration__02_涨停基因` /
`TDM-E-L3-03-2__calibration__02_均线多排` / `TDM-E-L3-03-2__calibration__03_温和放量` /
`TDM-E-L3-04__calibration__02_解禁否决` / `TDM-E-L3-05__calibration__02_连板顺位` /
`TDM-E-L3-06__calibration__02_地量档位开关` / `TDM-E-L3-07-1__ablation__02_烂板剔除步` /
`TDM-E-L3-07-2__ablation__02_IC加权对等权` / `TDM-E-L3-07-3__calibration__02_二十日动量排名` /
`TDM-E-L3-10__calibration__02_一字板不可成交` / `TDM-E-L3-12-3__calibration__02_获利盘占比` /
`TDM-E-L3-12-3__calibration__03_股东户数集中度`

blocked_on_data（18 张，全部写死缺段）：01/03 市值线、03-1/03 题材纯正度、03-2/04 行业相对强度、
03-3/02 三维共振、04/03 高应计、04/04 否决器整体、07-1/03 封单质量、07-2/03 行业中性、08/02 候选池容量、
10/03 停牌、11/02 日内双通道、11-1/02 竞价量比、11-2/02 涨速异动、12/02 四维共振、12-1/02 主力净额、
12-2/02 席位净买、12-4/02 K线形态、C-L3/02 加密动量流动性。

blocked_on_impl（6 张，注明缺什么）：E-L3/02 漏斗压缩、02/02 九阶段、07/02 三链并集、
09/02 Tier 状态机、12-3/04 单峰密集度、12-4/03 缠论结构。

机检面复核（`.runtime/tmp/st-nightmine-20261010/l2_validate.py`）：
`cards_new=39 nodes_covered=26 families={calibration:25, ablation:13, comparison:1} INVALID=0 nodes_uncovered=[]`；
逐卡校验项=顶层 19 字段齐备 / 无 `generated: true` / `signal_kind∈{panel,series}` /
`pillars_numeric` 五门柱齐 / 双窗为二元素列表 + regimes / `confidence_writeback` 与 node_id 精确匹配 /
`data_binding` 五子段非空且 `data_window_evidence` 含命令原文 / blocked 卡必带
`blocked_reason+missing_segment+unlock_condition`，preregistered 卡必不带。

## 5. 资产状态断言证据（§7.5 纪律，`python -m zephyr.library.lookup state "<关键词>"` 原文摘录）

- `筹码分布` → sources-with-hits **3/3**；馆面 `FILE:data/strategy_intake/normalized/2024年度精选策略1/77.【复现】筹码分布因子.txt`；
  git 面 `7963211f1ad [tilib-b10][WO-4] 批10 筹码族三件套正文批：+CYQ/SCR/CYC 3 指标/9 列（新建 chips.py MOD-L02-031…迭代衰减筹码分布+集中度+成本均线通达信口径，volume 手/股量纲实证÷100）`、
  `244c99c97fa 筹码分布性能断言负载flake收敛`、`f1a1eae6603 筹码分布引擎蓝图`；工棚面 `docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/rpt_d06.md（深度审查报告——筹码分布引擎 D06）`、
  `docs/_working/archive/2026-09/design_memos/10_regime_detector_spec.md L593 | 筹码单峰密集 | 筹码分布分析 | ✅ A 股特色 |`。
  → 结论修正：**"筹码分布未做"是错的**（CYQ 族与引擎在册且已接获利盘）；本车道断言仅限"筹码分布**直方图/峰数产物**未落库"（另附 `@impl` 枚举证据）。
- `减持` → sources-with-hits **2/3**；工棚面命中减持链叙述（`预披露 → 15 个交易日锁定期 → 窗口内集中竞价 90 日 ≤1%、大宗 ≤2% → 进展 → 完成`）
  与案例本叙述 → 断言精确化=**减持在文档/判据面在册，CH 无减持采集表**（`system.tables LIKE '%reduc%'/'%announce%'` 枚举 0 命中，`l2_ch_cov3.py`）。
- `商誉` → **2/3**；命中=财务安全维叙述（`资产负债率/流动比率/商誉占比/Altman Z | Piotroski 2000；国盛多因子 14`）与个别 fin 快照字段（`['商誉/净资产','0.00%']`）
  → 断言精确化=**商誉占比作为维度在册、无全宇宙商誉表**。
- `立案调查` → **2/3**；命中=TDM 原文 + `negative_veto.py（MOD-SIG-137）六项一票否决=业绩暴雷/立案调查/大股东减持/解禁>5%/商誉减值/配股圈钱 + 黑名单，INVARIANTS:8 命中任一即 vetoed`
  → 断言精确化=**实现在册、数据面无源**（故 04/04 卡为 blocked_on_data 而非未做）。
- `缠论` → **3/3**；命中=策略 intake 三件（2022/11、2023/50、2025/16 缠论工具笔线段）、深度审查 S07 报告、
  `L25: A股特有层有强证据：涨跌停板行为经济学（Jiang & Li 2026，149,589 次涨停事件 + 2020 创业板改革自然实验）与缠论券商级量化回测（中泰 2022：一类买点+大盘择时胜率 76.53%）存在；但缠论无同行评审文献`、
  `L48: ChanlunX 等 DLL 插件生态` → 断言精确化=**缠论判据文献在、本仓无逐日买点产物表**（12-4/03 卡）。
- `停牌` → **3/3**；命中=intake `0.回测提速十倍,过滤ST,退市,停牌,新股优化方法.txt`、`59 小市值轮动…剔除了停牌股`、
  矩阵册 `W5 ST/涨跌停/停牌过滤 | MINING | 未读：tradability_preflight.py 本体逐行 / stk_limit S16 三级解析链` → 断言精确化=**停牌过滤工程在册（三查件），缺的是 suspend 历史数据**（10/03 卡）。
- `一字板` → sources-with-hits 见 `.runtime/tmp/.../l2_lookup2.txt:171-203`（命中含执行层 19 问面与 W5  MINING 面）→ 本卡断言仅"一字可判数据源=不复权行情+stk_limit，实测可行"，无负存在断言。
- `一字板` → sources-with-hits **2/3**（snapshot 2026-10-10T07:37:29+08:00）；命中工棚面两处硬事实：
  1. `docs/_working/archive/2026-09/deep_review_full/p1_decision_chain/rpt_d06.md:29`＝**F-A1 缺陷在册（已实测）**：
     `high<=low`（一字涨跌停/零区间）时 `compute_daily_distribution` 返回**跨整个 250 日价格区间的均匀分布**而非该价位点质量，
     一字板日全部筹码被错误摊到全历史价格区间 → 直接影响本车道 12-3/02 获利盘卡的可读性，
     **已把该缺陷写入卡面 `pillars.known_defect_FA1`**（要求首跑按 一字日/非一字日 分组对照 IC，差异显著则禁直接回写 confidence）；
  2. `docs/_working/full-auto-chain/S11_assembled_backtest/nodes/limit_up_event_load_mining.md:78`＝一字板显式判定与 `eps=0.001` 触价口径在册（与本车道 0.011 容差的差异已记入长尾，须统一）。
- `竞价` → sources-with-hits **3/3**（snapshot 2026-10-10T07:39:50+08:00）；馆面命中 `data/strategy_intake/normalized/2022年度精选策略/96.集合竞价量比策略V1.txt`、
  `46.韶华研究之十二--还算可以的竞价研究.txt`、`4.集合竞价摸奖策略1.0-致敬2022.txt`（竞价量比题型内部先例在册）；
  事故面命中 `data/failures/20260716_auction_book_snapshot_033741.json`、`20260728_auction_book_snapshot_011553.json`、
  `20260803/20260804_integrity_check_c1_market.auction_snapshot_*.json`（**竞价采集有完整性失败史**，已写入 11-1/02 卡 evid）；
  边界登记：T3 系列 L-1 tick 级做T考卷（含竞价段新语义）已按**裁定#486** 出立项卡（commit `ad6b9d683d5`，五卡全 null 待批）
  → 本车道 11-1 卡不与该立项重复立考，只做窗口可考性判定；`价格笼子（主板 98%~102%）+ 9:20-9:25 禁撤单` 在册口径已列入 L3-10 长尾（三查未立卡）。
- `股票池分层` → 命中工棚面：`docs/_working/2026-09-11-tdm-morning-review-report.md:136`＝
  "L3-09 股票池分层｜施工清单 9.1 记'已非红'与实测不符（module_ref=null）——以地图真源为准，维持红，登记文档差异"、
  `2026-09-09-tdm-missing-modules-construction.md:129`＝"反查 pool/tier/分层（universe 管理可能已覆盖）｜反查命中→回填；落空→升 C"
  → 断言精确化=**09 环历史上确有 module_ref=null 期**（现已挂 pool_tier_maintenance.py/MOD-SIG-139），
    本车道 blocked_on_impl 的依据不是"件不存在"而是"池与 Tier 状态零落库（M-41 欠账 + 实测表 0 行）"。
- 说明：单次 `lookup state` 快照耗时约 2-3 分钟，本车道共 8 条（减持/商誉/立案调查/缠论/停牌/一字板/竞价/股票池分层）
  已全部跑完并逐条摘录，原始输出=`.runtime/tmp/st-nightmine-20261010/l2_lookup2.txt`（另 `l2_lookup_state.txt` 为首轮 10 关键词的超时残档，不作证据使用）。


**负存在断言降级记录（诚实优先）**：首轮流件曾把"筹码分布未做"写成断言——本轮正查后撤回，
改为"筹码分布直方图产物未落库"；同理"负面否决器未实现"撤回为"实现在册（MOD-SIG-137）但三检无数据源"。

## 6. 族级外部引用（③向，URL+发布方+年份；单源=待验证只登记不入图）

**涨停/连板族**（支撑 03-1/02、05/02、07-1/02、10/02 卡）：
- [市场微观结构视角下中国A股市场涨跌停板信号传递效应的实证研究](https://wap.cnki.net/touch/web/Dissertation/Article/10651-1013353274.nh.html)（CNKI 学位论文，2024）
- [Can price limits help when the price is falling?](https://www.sciencedirect.com/science/article/abs/pii/S1043951X08000680)（ScienceDirect，2009）
- [Do Daily Price Limits Stabilize Stock Markets?](https://cbk.bschool.cuhk.edu.hk/do-daily-price-limits-stabilize-the-markets/)（CUHK Business School CBK，2019）
- 内部强证据：Jiang & Li 2026 涨停行为经济学（149,589 次涨停事件 + 2020 创业板改革自然实验，经 `lookup state 缠论` 命中转述，**未获原文 URL=待验证**）
- A股适配闸：三源均确认涨跌停导致"磁吸效应/次日溢价"结构，与本车道 T+1 可成交口径一致；一字板不可成交处理为我方附加剔除（外部文献多以可成交假设计，直接照搬会前视）。

**CYQ 筹码族**（支撑 12-3/02、12-3/03 卡）：
- [筹码分布因子系统构建](https://bigquant.com/square/paper/5f3c2f13-367e-4be1-a0b7-e926acca54fd)（BigQuant，2025）
- [研报复现｜基于筹码分布的选股策略](https://zhuanlan.zhihu.com/p/707545244)（知乎专栏，2024）
- [CYQ指标](https://baike.baidu.com/item/CYQ%E6%8C%87%E6%A0%87/6324873)（百度百科，2026 版）——口径定义用，非收益证据
- A股适配闸：CYQ 用换手率衰减迭代（本仓 chips.py 同口径，WO-4 批 7963211f1ad 在册）；无流通股本时用衰减近似=本车道 12-3 卡可算，
  单峰密集全语义仍缺（12-3/04 卡 blocked_on_impl）。

**资金流族**（支撑 12-1/02、03-3/02 卡）：
- [聪明钱陷阱：主力尾盘买入后隔夜反而跌](https://www.joinquant.com/view/community/detail/70741)（JoinQuant 社区，2025）——与节点"单日大进大出警惕对倒"同向，构成反例证据（要求对倒档剔除）
- [资金流向因子挖掘实录：从主力净流入到行业轮动的全流程建模](https://m.blog.csdn.net/leisoo8097/article/details/163556400)（CSDN 博客，2026）——单源=待验证
- [主力资金净流入](https://baike.baidu.com/item/%E4%B8%BB%E5%8A%9B%E8%B5%84%E9%87%91%E5%87%80%E6%B5%81%E5%85%A5/658545)（百度百科，2026）——大/超大单口径定义
- 状态：资金流族收益预测的**同行评审级证据未获**（两源均为社区/百科）→ 12-1 卡的 ic_floor 门柱不放宽，负结果照收。

**席位族**（支撑 12-2/02 卡）：
- [机构与游资是A股市场两类截然不同的主力资金](https://xueqiu.com/1077174092/386262653)（雪球，2026）
- [第4章 龙虎榜的四大席位类型](https://m.toutiao.com/article/7662320547925983750/)（今日头条，2026）
- 状态：两源均为散户/投教叙事，**均不足以入图**（闸2 待验证）→ 12-2 卡的席位分类判据改为"seat_name 白名单工程需先落册"（写在 unlock 面）。

**解禁族**（支撑 04/02 卡）：
- [创业板限售股解禁对股票收益率影响的实证研究](https://max.book118.com/html/2025/0726/8040063030007115.shtm)（原创力文档转载学位论文 PDF，2025）——收费/转载墙，只登记题录（闸1）
- [中国股改限售股解禁的分析研究成果](https://www.daowen.com/lilun/1721997.html)（道文论文库，2026）——同上，题录级
- 状态：解禁族**方向有文献支撑但均为二手题录**，故 04/02 卡门柱不降、并加 `绝对线与分位双轨`。

**已查无（③向有效结论）**：双池合流（L3-03）与池分层状态机（L3-09）两题型在公开检索中**无对等文献**（A 股短线双池+Tier 状态机是本项目自造结构），
记 noise 并归因=查询词以中文战法叙事为主、来源贫矿（不降格为"挖不动"）。

## 7. 未挖长尾清单（明列，禁以候选多封矿）

1. ③向族级外部引用未做：**趋势/均线多排族、温和放量/量能族、IC 加权合成族、行业中性化族、组合容量族、可成交性/价格笼子族、竞价族、涨速族、Sloan 应计 A 股族、crypto 截面动量族**（10 族，各需 ≥2 源）。
2. 未立判据句（同节点仍有独立可判面）：
   - L3-01：上市<60 日剔除线单独卡、退市风险（valid_to/序列终止）剔除卡；
   - L3-03-1：龙头定位、情绪周期位置、分时强度（tick 永缺→blocked_on_data 卡未立）三判据；
   - L3-03-2：回踩质量（A/B 级）、筹码低位集中（五分制第五分）两判据；
   - L3-04：业绩暴雷（净利转负 PIT）、配股圈钱两检未立卡；
   - L3-05：妖/龙/中军/核心/趋势/跟风 六档语义的分档收益对照卡（本卡仅连板高度代理）；
   - L3-06：environment_switch 四开关的其余三轴（短线链停/波段/极端高潮反向收紧）；
   - L3-07-1：板块强度前 3 步、龙头定位步、板块内涨停股步（三步未各立消融卡）；
   - L3-07-2：月度权重校准频率（C3-04）对照卡；
   - L3-07-3：eventdriven 事件提前 3 日观察卡、default-equity 宽基 ETF 网格卡；
   - L3-10：价格笼子拒单率、科创板权限、资金不够一手 三查卡；
   - L3-11-2：尾盘偷袭板质量单独档卡；
   - L3-12-3：conc_70 vs conc_90 口径对照卡、chips_avg_cost 成本均线族卡；
   - L3-12-4：平台突破/前高位判据卡；
   - TDM-C-L3：赛道归属（无数据源）coverage 卡。
3. 族面缺：个股层的 **cost 族**（滑点/成交成本对候选池容量的侵蚀——与 L3-08/L3-10 强相关，可算不复权 amount+一字比例）与 **coverage 族**（各链 PIT 可得率日度监控）本轮零卡。
4. 复挖建议（交叉复挖 20%≈6 节点，供主车道派他车）：
   `TDM-E-L3-03-1`（涨停基因窗口敏感性 20/60/120 日三版）、`TDM-E-L3-04`（七检逐检边际，需先解三检数据源）、
   `TDM-E-L3-06`（四开关全轴，与 L1 车道正交对接）、`TDM-E-L3-07-2`（IC 加权族外部引用+权重频率）、
   `TDM-E-L3-12-3`（筹码三维口径互证，含 chips vs 户数 vs 直方图三方）、`TDM-E-L3-01`（宇宙口径与北交所/退市股处理终裁，涉 Owner 门）。

## 8. 车道收尾统计（MUST 面）

- 本车道节点总数：**26**（权威=`00_lane_roster.yaml` lane=L2）
- 已挖数（六向各一轮留痕）：**26**
- mined_out 节点数：**0**（结构判据未成立，长尾见 §7；禁降格）
- 新卡总数：**39**（目录=`docs/03_modules/_domain_backtest/exam_cards/entry_flow/L3/`）
- 族分布：calibration 25 / ablation 13 / comparison 1
- 状态分布：preregistered 15 / blocked_on_data 18 / blocked_on_impl 6
- blocked 名单与原因（18+6=24）：
  - 缺 `stock_daily_basic`（2019-01-04..2020-12-31）：01/03 市值线、04/03 高应计（分母）
  - 缺 `money_flow`（2019-01-04..2020-12-31）：12-1/02、03-3/02（资金维）、12/02
  - 缺 `dragon_tiger_seat`（2019-01-04..2021-12-31）：12-2/02、12/02
  - 缺 `market_pattern_event`（2019-01-04..2021-08-31）：12-4/02、03-3/02（形态维）、02/02（形态段）
  - 缺 `kline_5min`（2019-01-04..2021-08-31）：11-2/02、11/02
  - 缺竞价面（2019-01-04..2026-05-31/07-20）：11-1/02、11/02
  - 缺封单额（2019-01-04..2025-09-09 全段）：07-1/03
  - 缺板块/题材 PIT 归属（窗内 0 行）：03-1/03、03-2/04、07-2/03
  - 缺 `suspend` 历史（窗内 0 行）：10/03
  - 缺 `crypto_kline_daily`（起点 2025-08-08）：C-L3/02
  - 缺候选池数据（在册 `stock_candidate_pool_empty_table_no_leg`，status=open）：08/02、（连带）09/02、07/02、E-L3/02
  - 实现缺（引擎在、逐环节产物零落库）：E-L3/02、02/02、07/02、09/02、12-4/03、12-3/04
  - 数据永缺（缺表非缺段）：04/04（减持/商誉/立案三检无 CH 表）
- 交回主车道的一条硬事实：**涨停/炸板/一字三口径在冻结窗内可由 `kline_daily`（不复权）×`stk_limit` 重建**（实测封板 74/893、炸板 23/2,268、一字 41/5,355），
  但必须避开 `kline_daily_hfq` 量纲陷阱（同日误判 3,882 家涨停）；`limit_up_pool`/`limit_up_down` 历史不可依赖（仅 2026-07/09 起）。
- 禁区自证：零 git 写操作；未改 TDM/注册表/分数册；未跑生成器；未碰他人车道目录
  （`git status --short docs/.../entry_flow/L3/` 非 `??` 行数=0 → 26 张骨架件零改动）；临时件全部在 `.runtime/tmp/st-nightmine-20261010/`。

