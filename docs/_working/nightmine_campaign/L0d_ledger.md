---
ttl: task_bound
title: L0d 广度序列推导解锁件台账（过夜总令）
created: "2026-10-10"
sid: st-nightmine-20261010-L0d
family_id: NIGHTMINE-CAMPAIGN
---

# L0d 数据解锁件施工台账 — TDM 广度面 7 序列推导（2019-01-04..2025-09-09）

session: st-nightmine-20261010 ｜ lane: L0d（广度序列推导）｜ 全程 CH **只读**，零 git 写，零表写

## M0 口径选定（实测留痕，非凭记忆）

### 价格面板 = `c1_market.kline_daily`（**不复权**，与涨跌停价同源）✅
实测证据（同 symbol/day 与 hfq 表面比对，600519）：

| trade_date | kline_daily.close（raw） | kline_daily_hfq.close | pct_change |
|---|---|---|---|
| 2019-06-20 | 975 | 7031.7 | 4.61 |
| 2024-06-18 | 1521.5 | 11955.3384 | -1.29 |

⇒ `kline_daily.close` 是原始成交价，`kline_daily_hfq` 是后复权。**判定：用 kline_daily**。
涨跌停价是原始价语义，混复权价=造漂亮假数据（本战役明令禁止）。
`kline_daily.adj_factor` 实测恒=1（不可用于还原），故不作二次除权修正，
昨收/涨跌幅直取在册 `pct_change` 列（交易所公布口径，已含除权修正）。

### 涨跌停价 = `c1_market.stk_limit`（库内官方价，直给 limit_up/limit_down/st_flag）
冻结窗（2019-01-04..2025-09-09）内实测：7,589,103 行 ｜ distinct trade_date=**1,622**（=日历全集）
｜ `limit_up IS NULL` 5,082（0.067%）｜ `st_flag=1` 231,806 ｜ 北交所 230,751 行 / 278 标的。
全表范围 2015-01-05..2026-10-09 / 9,254,772 行 ⇒ **冻结窗全覆盖，无需 tushare 拉取**。

### kline_daily × stk_limit JOIN 缺口（年×缺 limit 行数，实测）
2019:206 ｜ 2020:606 ｜ 2021:502 ｜ 2022:358 ｜ 2023:245 ｜ 2024:92 ｜ 2025:69
⇒ 合计 2,078 行（≤0.027%），走**在册规则推导链兜底**
`daban_board_event_deriver.rule_limit_price`（Decimal ROUND_HALF_UP 到分；主板 10%/ST 5%
（ST→10% 生效 2026-07-06 在冻结窗外，2019-2025 全程 ST=5%）/科创创业 20%/北证 30%）。

### 触板/封板判定 eps = **0.001**（复用在册 `LIMIT_EPS`，不另起）
- 触涨停 touched：`high >= limit_up - eps`；收盘封板 sealed：`close >= limit_up - eps`
- 一字 one_word：`low >= limit_up - eps`
- 触跌停：`low <= limit_down + eps`；封跌停：`close <= limit_down + eps`

### 官方对拍源
`c1_market.limit_up_down` **仅 data_source='akshare'**：实测 2026-08-03..2026-10-09，
涨停 44 distinct days / 3,624 行，跌停 40 days / 622 行。
⚠ 表内另有 `data_source='derived_stk_limit'`（2026-07-20..07-31）=**同款推导，非独立官方真源**，
已剔出对拍基准。⇒ 重叠窗=**2026-08-03..2026-10-09**（≥2026-07-20 判据满足）。

### 交易日历独立真源
`c1_market.trade_calendar`（exchange='SSE', is_open=1）：冻结窗期望交易日
= `uniqExact(cal_date)` 直查 = **1,622**（先前 1,624−1 手算推定已废：01-02 与 01-03 均在窗外）。
stk_limit distinct=1,622 ⇒ **零缺日**。重叠窗三方齐（日历 44 / kline 44 / stk_limit 44）。

## M0b 三条自我纠错（诚实留痕，不掩盖）

1. **`stk_limit.board` 存中文标签**（沪主板/深主板/创业板/科创板/北交所），**不是**在册
   `board_of()` 的英文枚举。首探 `board='bj'` 得 0 行 → 差点误判"北证窗口零覆盖"。
   那是**我探针口径错**，非数据缺失；按前缀复核 92 开头在 stk_limit 窗口内 229,638 行 / 275 标的 /
   1,379 交易日（days<1,622 纯属北交所 2021-11-15 才开板）。
   ⚠ 后续 board 判定一律走前缀（复用在册 `board_of`），**禁按该中文字符串筛**。
2. **`position(haystack, needle)` 实参顺序写反** ⇒ 首轮 ST 探测恒 0。改 `name LIKE '%ST%'` 复核得 M0c。
3. **诊断查询只 JOIN symbol 忘 JOIN 日期** ⇒ 一标的匹配 5 个交易日、行数虚增×5，
   一度误判"官方池 08-24 有 282 行重复"（真实 96）。已纠正，结论未受影响。

## M0c 自校验门的实质口径叉（决定判据成败）

`limit_up_down` 官方池（akshare，4,246 行，1,584 唯一 name）**实测 ST 名称行数 = 0**
⇒ **AKShare 涨停池在本库不含 ST 股**。而推导源 stk_limit 窗口内 `st_flag=1` 有 231,806 行
⇒ 推导家数天然含 ST；且重叠窗 2026-08-03 起 ST 幅度已=10%（与主板同幅），含 ST 版必然高于官方池。
⇒ **处置：含 ST / 剔 ST 两版同时跑对拍**，主序列保留含 ST（真实市场事件，剔除=家数虚低），
逐日 ST 家数一并入册供卡侧按需重算。**禁只挑好看的那版**。

## M0d 其它 universe 规则实测

- **重复键**：`kline_daily` 窗口内 (trade_date,symbol) 重复键 **656** 个（ReplacingMergeTree 未收敛）
  ⇒ 必须 `argMax(col, ingest_ts) GROUP BY (trade_date,symbol)` 取最新入库版，不去重=家数虚高；
  `stk_limit` 重复键 **0** 个（仍防御性同法处理）。
- **板块构成**（窗口内行数）：60xx 2,625,500 / 00xx 2,376,263 / 30xx 1,776,153 / 68xx 582,892 /
  92xx 229,913 / 83xx 1,116 ⇒ kline_daily 是纯股票面板（ETF/转债/指数各独立表），无 `period` 列。
- **停牌**：`volume=0` 25,417 行 ⇒ 显式剔除（含净广度）。
- **列可用性**：`pct_change` NULL=0、`high/close` NULL=0 ⇒ net_breadth 直接用 pct_change。
- **标的维表** `c1_market.stock_list`：5,930 行 / 5,930 唯一 symbol，`list_date` /
  `delist_date`（1970-01-01 哨兵=未退市）/ `list_status`（上市 5,564、退市 366）
  ⇒ 用于剔上市前、退市后、非在册标的。窗口内新股（首现日∈窗）2,076 个。

## M1 七条序列口径（index=trade_date，列名=value）

| # | series | 定义 |
|---|---|---|
| 1 | limit_up_count | 收盘封涨停家数（含一字、**含 ST**、含规则兜底补齐） |
| 2 | limit_down_count | 收盘封跌停家数（含 ST） |
| 3 | blast_ratio | (touched_up − sealed_up) / touched_up |
| 4 | seal_ratio | sealed_up / touched_up（=1−blast_ratio，同源互证） |
| 5 | max_streak_height | 当日连板最高高度（日历索引 gaps-and-islands 链） |
| 6 | streak_distribution | **长表** trade_date,bucket,value；bucket ∈ {first_board, second_board, third_plus_board, second_plus_board}（覆盖判据要求的"2 板家数 / 3 板及以上家数"） |
| 7 | net_breadth | 上涨家数 − 下跌家数（pct_change>0 / <0，剔停牌 volume=0） |

**新股无涨跌幅限制日的显式处理**（判据硬要求）=「涨跌停价 binding 检验」：
limit_up 非空但 `high > limit_up+0.02` 或 `low < limit_down−0.02` ⇒ 当日发布的涨跌停价未被市场
遵守 = 无有效涨跌幅限制（覆盖科创 2019-07-22 起 / 创业板 2020-08-24 起 / 北证 2021-11-15 起
首 5 日、主板全面注册制 2023-02-20 起首 5 日），该类 symbol-day 从涨停/跌停/炸板/连板剔除，
**仍计入净广度**（真实涨跌）。limit_up IS NULL 同样剔除。实测重叠窗每日仅 0~2 行非 binding。

计算全部 **ClickHouse 服务端聚合**（countIf + 窗口函数），一次性拉到 2026-10-09，
同一段代码兼产冻结窗 CSV 与重叠窗对拍，**零逐日 python 循环**。

## M2 重叠窗自校验 —— 核心发现：**基准侧被污染，不是推导错**

朴素全 44 天对拍：推导收盘封板家数 vs 官方池 = **系统性偏差 −24%，mean|rel| 22%**，
按判据该判"口径不通"停手。但逐日拆开，偏差全部由特定日贡献：

| 官方池当日快照数 `uniqExact(ingest_ts)` | 天数 | 推导 vs 官方 系统性偏差 | mean\|rel\| |
|---|---|---|---|
| **=1（盘后单次采集）** | 13 | **+1.9%** | **6.1%** |
| **>1（盘中多次快照）** | 31 | −24.4% | 21.9% |

根因（实测非猜测）：`limit_up_down` 按 `(trade_date,symbol)` 唯一键写入，采集器**一天跑多次盘中
快照**（实测 2026-08-18 有 16 个 ingest_ts、08-11 有 11 个，另有 03:15/01:30 UTC=北京 11:15/09:30
等盘中时刻）。故当日行数 = **各盘中快照标的集合的并集**，既非收盘封板亦非全日触板 ⇒ 必然大于
收盘封板家数。

反证链（行级取证，2026-08-24 官方 96 只）：46 只与我的收盘封板一致；13 只盘中触板、收盘炸板；
剩余 37 只 kline 全日 high 从未触及涨停价——且这 37 只的官方 `close` **恰等于当日 pre_close**
（000628：官方 close=45.35，我的 08-24 涨停价 49.89=round(45.35×1.1) ⇒ 官方那行是**前一日**收盘
数据串在 08-24 标签下）。⇒ 官方表还存在**日内标签串位**，进一步不可作收盘态基准。

**干净基准日（单快照 + 日线完整 + 官方家数≥10）逐日（含 ST / 剔 ST vs 官方）**：
08-03 83/76 vs 75 ｜ 08-04 141/139 vs 138 ｜ 08-05 104/103 vs 103 ｜ 08-06 83/79 vs 79 ｜
08-07 75/75 vs 74 ｜ 08-10 103/99 vs 99 ｜ 08-26 56/52 vs 52 ｜ 08-27 78/77 vs 77 ｜
09-17 50/47 vs 47 ｜ 09-18 79/78 vs 78 ｜ 09-28 35/33 vs 33 ｜ 09-29 56/56 vs 57
⇒ **剔 ST 后逐日几乎精确命中（±1~2 只）**；含 ST 高出部分≈当日 ST 涨停家数。

第二个基准缺陷：`kline_daily` 在 **2026-10-08/09 入库不全**（可判样本 ~2,957 vs 常态 ~5,545，
缺约一半；官方那两日 43/107 只 vs 推导 30/51）⇒ 已从对拍剔除，**不影响交付窗**（止 2025-09-09）。

**判据结论：按干净基准日口径过门**（含 ST 偏差 +1.9%、mean|rel| 6.1%，均 <10% 阈值）。
朴素全窗 −24% 是基准污染产物，两套数字同时入报告，不藏。

## M3 七条序列落盘（全绿）

产出目录 `docs/_working/nightmine_campaign/series/`，UTF-8 + **LF 行尾（实测 CRLF=0）**，
index=trade_date：

| 文件 | 行数 | 覆盖 | 缺日 | 值域 |
|---|---|---|---|---|
| limit_up_count.csv | **1,622** | 2019-01-04..2025-09-09 | **0** | 12..878（均 73.5） |
| limit_down_count.csv | 1,622 | 同上 | 0 | 0..3,188 |
| blast_ratio.csv | 1,622 | 同上 | 0 | 0.123..0.768 |
| seal_ratio.csv | 1,622 | 同上 | 0 | 0.232..0.877 |
| max_streak_height.csv | 1,622 | 同上 | 0 | 2..25 |
| streak_distribution.csv | 6,488（长表 1,622×4 桶） | 同上 | 0 | first/second/third_plus/second_plus_board |
| net_breadth.csv | 1,622 | 同上 | 0 | −5,178..+5,327 |

年×行数：2019 242 / 2020 243 / 2021 243 / 2022 242 / 2023 242 / 2024 242 / 2025 168
⇒ 合计 1,622 = 期望交易日数，**逐序列零缺日**。
universe 完整性（对**当年**中位数，A 股总数自然增长已吸收）：
2019 3,609 → 2025 5,390，偏薄日 **0** 个（首轮用全局中位数误报 554 个已纠）。
规则兜底链：冻结窗内 6,919 个 symbol-day 无 stk_limit 行，`rule_limit_price` 补出
**142 个封涨停**（涉 118 个交易日），已计入 limit_up_count 并逐日入册。

## M3b 外部公开事件回验（不依赖在册官方池，独立取证）

| 日期 | 公开事实 | 我的序列 |
|---|---|---|
| 2020-02-03 | 疫情后首日约 3,000+ 只跌停 | limit_down **3,188** |
| 2024-02-05 | 微盘股流动性危机见底 | limit_down **1,442** |
| 2024-02-08 | 汇金增持企稳、涨停暴增 | limit_up **552** |
| 2024-09-30 | 924 行情国庆前末日 | limit_up **878**、net_breadth **+5,327** |
| 2024-10-08 | 高开巨震炸板潮 | limit_up 827、**炸板率 0.684** |
| 2025-04-07 | 对等关税黑色星期一 | limit_down **3,018**、net_breadth −5,178 |
| 2020-06-08 | **万泰生物 603392**（IPO 2020-04-29）25 个一字连板收官 | max_streak **25** |

连板链复现了 2020 年三只著名次新股妖股（万泰生物 25、斯达半导 603290 22、立昂微
605358 22），且段内逐日 high=close=limit_up、累计 9.86 倍 ⇒ 连板口径成立。

## M4 机读报告已落盘

`docs/_working/nightmine_campaign/02_breadth_derivation_report.yaml`
字段齐：selected_tables / limit_price_source / eps / universe_rules（含 ST、新股无涨跌幅、
北证、停牌、退市、上市前、一字板逐条）/ per_series（含逐日 ST 家数与缺日清单）/
overlap_selfcheck（含基准污染取证、干净日清单、剔除日原因、逐日误差）/
universe_completeness_frozen_window / external_event_sanity_check / caliber_risk（8 条）/
reproduce_command。

重跑：`python D:/ZephyrAlpha/.runtime/tmp/st-nightmine-20261010/derive_breadth_series.py`
（`BREADTH_REFRESH=1` 强制重取 CH；缺省命中 `.runtime/tmp/.../breadth_diag/cache_*.json`）

## 残余风险（要点，全量见报告 caliber_risk 8 条）

1. **干净基准日仅 12 天**，且全在 2026-08/09，与冻结窗相隔约 10 个月 ⇒ 冻结窗正确性靠
   口径自证 + 外部公开事件回验，非同期官方池直验（官方池 2026-07-20 才有数据，在册断供成立）。
2. **seal_ratio 与 blast_ratio 恒等互补**（max|1−seal−blast|=1.1e-16）⇒ 两张卡信息完全冗余，
   卡侧须合并或改定义，否则同一信号考两遍。
3. **连板高度对"含 IPO 首日"的市场习惯口径低 1**（binding 检验剔除 IPO 无涨跌幅日）。
4. 北交所 2021-11-15 开板 ⇒ 冻结窗前段无北证样本，绝对家数存在结构性阶跃。
5. 主序列**含 ST**而官方池剔 ST（差值≈当日 ST 家数，逐日已给）。
6. `kline_daily` 2026-10-08/09 入库仅约半数 ⇒ 只影响对拍末两日，不影响交付窗。
7. binding 检验是经验判据：若 stk_limit 某行 limit_up 录错会被误判非 binding 而漏计。
8. 停牌日断连板链符合语义，但 kline 缺行同样断链 ⇒ 连板数可能偏低。

## 进度

- [x] M0 口径选定
- [x] M0b/M0c/M0d 自我纠错 + 基准口径叉 + universe 实测
- [x] M1 服务端 SQL 推导跑通
- [x] M2 重叠窗自校验（基准污染取证；**判据 GATE=PASS**）
- [x] M3 7 条 CSV 落盘（1,622/1,622 全覆盖，零缺日）+ M3b 外部事件回验
- [x] M4 02_breadth_derivation_report.yaml

**全程只读**：零 `c1_market.*` 写入、零 git 写、未碰注册表/TDM/卡册/分数册。

