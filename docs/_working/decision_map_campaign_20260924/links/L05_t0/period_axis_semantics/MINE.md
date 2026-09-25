---
ttl: task_bound
title: L05 做T · 多周期买卖点轴语义矿（{1,5,15,30,60}min 分桶口径与 120min 边界）
created: "2026-09-26"
sid: st-qmine-20260925
lane: L05 个股做T（深挖车道，只读挖掘+写文档）
family_id: L05-T0-PERIOD-AXIS
executes: SKEL.md §5 D1 / §7 L05-C03 的缺口面
inputs:
  - docs/_working/decision_map_campaign_20260924/17_quantified_acceptance.md §三.1（周期集/5,853 只/容量预检先行）
  - docs/_working/decision_map_campaign_20260924/links/L05_t0/t0_state_match_readme.md §3.1/§3.3
  - docs/_working/decision_map_campaign_20260924/links/L05_t0/SKEL.md §5 D1
---

# 多周期买卖点轴语义矿 · MINE

## ① 职责一句话

把"周期"从一个人手敲的命令行参数升级成**有唯一语义、有可交易性下限、与生产数据面同源可核对**的条件轴：定义 {1,5,15,30,60}min 各自的 bar 语义、格内可比性与 120min 的边界理由，保证矩阵里"60min 格"这句话在三年后还能被同一口径复算。

## ② 现状实测（文件:行号 / 字段 / 生产触发面 / 新鲜度）

**口径实现面（研究）**

- `scripts/backtest/t0_material_line.py:64` — `ALLOWED_PERIODS = (1, 5, 15, 30, 60)`，同行注释即"120min 不做（Owner 明令）"，是**唯一**的 120min 拒入真源（常量，非文档承诺）。
- `scripts/backtest/t0_material_line.py:63` — `MIN_BARS_BY_PERIOD = {1:200, 5:40, 15:14, 30:7, 60:4}`，注释口径="≥83% 标准日 session 桶数"。实测校验：40/240×5=… 逐档核对 {200/240, 40/48, 14/16, 7/8, 4/4} → 1/5/15/30min 档为 83.3%/83.3%/87.5%/87.5%，**60min 档 4/4=100%**（不是 83%），即 60min 轴要求"满日"，缺任一桶即整票-日被弃 → 60min 格样本天然被"完整交易日"筛选，与其它四档**不同底**（详见缺口 L05-PA-G01）。
- `scripts/backtest/t0_material_line.py:89-110` — `resample_period()`：日内 bar **序数**分桶（每 P 根合一根），`open=chunk 首根`、`close/volume=末根/求和`、`trade_time=桶内末根时刻`；`period==1` 直返原生。**无 session 日历参与**（不按钟点对齐）。
- `scripts/backtest/t0_rule_engine.py:494-497` — 周期入参白名单硬拦（越集=SystemExit）；`:362-364` 产物按 `<rule>_<P>min.parquet` 命名；`:372-375` 逐档 `min_bars` 淘汰；`:323-325` R04 的 `or_bars_by_period` 把"开盘区间"折算成各周期根数。
- `scripts/backtest/t0_state_match_matrix.py:233-234` — `period` 是全交叉矩阵六键之一（`rule/period/phase/sector_family/mcap_q/news_axis`）；`:84-89` 周期从**文件名正则**回读（`_([0-9]+)min.parquet`）。

**生产数据面对照（关键新发现）**

- 仓内**已存在第二套 bar 合成语义**：`src/zephyr/data/kline_resampler.py:11,103`（ClickHouse `toStartOfInterval` **钟面对齐**聚合，1m/5m→15m/30m/60m，MATURITY=production）——但其真源对象是 **880xxx 板块指数 K 线**（`:17-20` 模块自述），不是个股。个股侧另有 `src/zephyr/data/implementations/ch_tick_kline.py:19,78,185`（tick→`kline_1min`/`kline_5min`，`minutes` 参数化，5min 为**原生表**）。
  → 结论：**同一动词（合成 15/30/60min）在仓内有"钟面对齐"与"序数分桶"两套语义**，分别服务板块面与研究面；个股 5min 存在原生表 `c1_market.kline_5min`，而研究面 5min 由 1min 序数桶派生 —— **双源未做过一致性对账**（L05-PA-G02）。
- 生产触发面（本轴有无自动运行）：**无**。全仓反查 `t0_rule_engine|t0_state_match|t0_rule_pairs|t0_rule_manifest`（*.py/*.yaml/*.json）命中仅 5 件：两引擎 + 两测试 + `scripts/script-manifest.yaml`，`src/` 零命中；无 `pipeline_events` 挂点、无周期轴产物消费代码 → 周期轴目前是**纯研究脚本轴**，与 SKEL §0.1"研究面已闭环、消费面零接线"一致（本向为二次实证，不重复登记 LK-05）。
- 新鲜度承袭（本车道不跑批、不碰 LANE-T0 产物）：`data/backtest_artifacts/t0_rule_engine/` 对本车道实测=空目录（2026-09-26 列举，0 文件），全量批在 LANE-T0 在途；分钟库=2021-09→2026-09（SKEL §2 A2，14.83 亿行/5,853 只），研究窗止 2025-09-09（`t0_material_line.py:60-61` 常量化 + `enforce_closed_book` :338 硬拦）。

## ③ 六向台账（每向：内部反查 + 全网搜索双动作）

**①上游（还有什么信息该喂进来）**
- 内部反查：`t0_material_line.py:66-72` 取数 SQL 只取 `open,high,low,close,volume`——**无 `amount`（成交额）**。个股分钟表在仓内是否有 amount 列未实测（本车道未查，见 L05-PA-G03）；若缺，则"各周期成交额/ADV 参与率"类过滤（A1 块量能闸门"单笔≤对手一档 50%、日参与≤1-5% ADV"，SKEL §2 A1 ③）在分钟面**无法原生计算**，只能用 volume×价近似。
- 全网搜索：日内高频研究的"成本可剥削性"必须与信号持续性同表报告——Seeck《Intraday Momentum in Spot FX and Currency Futures: Signal Persistence, the JPY Amplification Mechanism, and the Cost Barrier to Retail Exploitability》, SSRN 工作稿, 2026, https://doi.org/10.2139/ssrn.7008318（发布方=SSRN；单源，状态=**待验证**，只登记不入图）。

**②下游（输出还该喂给谁）**
- 内部反查：唯一现生消费者=匹配矩阵（`t0_state_match_matrix.py:242-255` 逐 (phase,period) 计 n 并出 D2 主视图 `t0_state_match_phase_period_<tag>.csv`）。潜在第二消费者=实盘执行/信号采集侧的周期对齐（`zephyr.data.implementations.qmt_bridge_provider.py:96` 只有 `1min/5min` 两周期可直取，15/30/60 需自合成）→ **研究结论若要落地，落地方拿到的 15/30/60min bar 语义与研究语义不同源**（L05-PA-G02 的下游后果）。
- 全网搜索：已查无（查法=Crossref 以"intraday bar frequency / time bar vs volume bar alignment"检索，命中的是电价与外汇 15 分钟建模：Kiesel & Paraschiv《Econometric Analysis of 15-Minute Intraday Electricity Prices》SSRN 2671379, 2015, https://doi.org/10.2139/ssrn.2671379 ——对象是电价非 A 股个股，**A 股适配闸不过**（无涨跌停/无 T+1/市场结构不同），只作"分钟频率分桶须显式声明时间戳约定"的一般性旁证，不作方法引文）。

**③算法/机制（业界学界最新怎么做）**
- 内部反查：capability_lookup 式符号反查=`resample|_resample|toStartOfInterval|freq="5min"` 全域 grep（`src/`+`scripts/`），命中 12 件（含 `internal_compute_provider.py:29` 的 9 周期枚举含 120min、`tdx_provider.py:334` 的通达信周期码表、`crypto.py:49` 的 `_KNOWN_FREQS`）→ 事实=**"周期"在仓内至少三套编码并存**（分钟数 int / "1min" 字符串 / 通达信数字码 0,1,2,3,7,9），研究轴用的是第四套（裸 int {1,5,15,30,60}）。
- 全网搜索：本向未挖到可直接替换"序数分桶"的公开标准实现（查法=Crossref `query=minute bar aggregation clock aligned vs volume bars stock intraday`，rows=6，无命中 A 股场景条目）。**结论=已查无（按查法记档），不因此判口径错**——序数分桶是 Owner 明令的实现选择（120min 不做的立法面）。

**④后端（代码侧缺什么）**
- 内部反查：`resample_period` 无"桶 → 钟点区间"映射产物 ⇒ 一个有停牌/缺 bar 的交易日里，序数桶与钟点错开，**同 (symbol, trade_date, period, bucket_index) 在不同票之间不对应同一钟点**。日内波动率按钟点强季节（开盘/收盘 U 型），桶时刻漂移=跨票混季节。引擎无 per-day 桶数分布诊断产物（`t0_rule_engine.py:460` 仅出 n_pairs 统计）。
- 全网搜索：与③同查法，无额外条目（记"已查无"）。
- 测试面：`tests/backtest/test_t0_material_line.py`（SKEL/文件头 TESTS 声明含"重采样分桶"例）为构造数据纯函数测试，**不覆盖真实缺 bar 日**。

**⑤前端（只登记不施工）**
- 内部反查：`t0_state_match_phase_period_<tag>.csv` 与矩阵 CSV 是周期轴唯一呈现面；仪表盘（`src/zephyr/frontend/dashboard/api_server.py`）零消费（grep `t0_state_match` 无前端命中）。
- 全网搜索：已查无（查法=未做，判为无外部呈现惯例可考——周期×相位矩阵是项目内部读法；此向按 SOP §8"内部轮就够"处理，不硬造引文）。

**⑥数据字段（要什么/有吗/质量）**
- 内部反查：`c1_market.kline_1min` 消费列=8（`_BARS_SQL`）；`trade_time` 类型/时区面属 RULE-SCHEMA-TZ 辖区，研究面按日内序数操作 ⇒ 对时区**不敏感**（这是序数分桶的一个真优点，值得写进注释而非只靠实现）。**质量画像未做**：①零成交分钟 bar 是否入库 ②缺 bar 日占比按周期分布 ③`kline_5min` 原生表 vs 派生 5min 的一致性 —— 三项全部未实测（本车道禁跑批，仅登记为 L05-PA-G03 取数面）。
- 全网搜索：字段口径"bar 时间戳=区间起始还是区间结束"是行业需显式声明项（上引 Kiesel & Paraschiv 2015 同族约定问题）；A 股适配闸：本项目取"区间结束"（`trade_time=chunk 末根`），与 tushare/通达信惯例一致性**未核**（L05-PA-G04）。

## ④ 缺口清单（本矿新登，编号 L05 段内续）

| 编号 | 缺口 | 证据锚 | 性质 |
|---|---|---|---|
| L05-PA-G01 | 60min 档 `min_bars=4` 实为"满日"筛（100% 桶数），与其余四档 83-87.5% **不同样本底**，跨周期格可比性未声明 | `t0_material_line.py:63` 算术实测 | 口径披露缺口（**禁改判据**，只须在矩阵 meta 与 README 加"逐周期样本底"披露） |
| L05-PA-G02 | 个股 5/15/30/60min 双源未对账：原生 `kline_5min`（`ch_tick_kline.py:19`）与 1min 序数派生、以及板块面 `toStartOfInterval` 钟面对齐（`kline_resampler.py:103`）三套语义并存，无一致性件 | 上述行号 | DU-xx（同动词异语义，非克隆；须登记语义边界或做对账件） |
| L05-PA-G03 | 分钟面质量画像三项缺失：零成交 bar 是否入库 / 缺 bar 日分布 / `amount` 列有无（→ 量能闸门能否分钟原生可算） | 本件 §③①⑥ 实测记"未查" | 闸4"字段在≠数据可得"典型项（取数面，非判据面） |
| L05-PA-G04 | bar 时间戳约定（区间末 vs 区间首）与外部数据源惯例一致性未核 | `resample_period` 桶时刻=末根 | 口径登记项 |
| L05-PA-G05 | 周期编码四套并存（int / "Nmin" / 通达信码 / 秒），无中央周期词表 | `internal_compute_provider.py:29`、`tdx_provider.py:334`、`crypto.py:49`、`t0_material_line.py:64` | LK-xx 治理面（终局要统一，现不阻断） |
| L05-PA-G06 | 120min 的"不做"目前只有常量+注释，无**书面边界理由件**（Owner 明令的机理=日内时长 240min，120min 只有 2 桶 → n 门槛下无信息；此推断未落任何文档） | 全仓 grep "120min" 仅上述两处拒入 | CNS-xx（口径注释级补充，禁扩周期集） |

## ⑤ 自审闸三态裁定

**裁定=施工（限定小面）+ 部分挂起排期。**

- 判"施工"的理由（终局全貌尺）：本轴的缺口全部是**披露/对账/画像件**，不新增判据、不动阈值——L05-PA-G01/L05-PA-G04/L05-PA-G06 三份披露各 ≤30 行文档或 meta 字段，能消灭"后人重读代码猜口径"的人工环节；L05-PA-G02 的双源对账件是**一次性可自动化的机器核对**，终局里做T 若上产，研究/生产 bar 语义不一致=静默错单源，属必须消灭的人工核账。
- 判"挂起排期"的：L05-PA-G03（取数画像）解锁条件=LANE-T0 全量批交付后有余量 CPU 窗口，且须走只读探针（禁本车道跑）；L05-PA-G05（周期中央词表）解锁条件=数据集成器侧统一词表立项，与本轴合并处理，禁在本矿单开。
- **不封矿**：矿脉未枯竭——六向中④⑥两向仍是富矿（bar 语义对账、质量画像），已明确长尾=①零成交 bar 占比实测 ②缺 bar 日按周期分布 ③`kline_5min` 对账 ④120min 边界理由的 Owner 追认。
- 反驳者一问（富矿候选 L05-PA-G02 立卡前）：(a) 对账件可能永远只有个位数差异 → 但差异方向不可知，且分钟库 24 亿级行、跨源差异会污染所有周期格；(b) 序数桶是 Owner 明令、"改口径"越权 → 本缺口只核对**不断言谁错**；(c) 现有矩阵已能自证样本量 → 样本量证明"有多少格"，不证明"格里的 bar 是同一种 bar"。三理由不足以驳回，维持施工候选。

## ⑥ 挖矿日志

| 轮 | 矿脉 | 动作 | 判定 | 关键产出 |
|---|---|---|---|---|
| R1 | 周期常量与分桶实现 | 内部 grep+读码 `t0_material_line.py:63-110` / `t0_rule_engine.py:323-375,494-497` | signal | 120min 唯一真源=常量拒入；60min 档底与其它档不同（L05-PA-G01） |
| R2 | 生产数据面对照 | 内部 grep `resample|toStartOfInterval` 全域 12 件 | signal | 仓内两套 bar 合成语义 + 个股 5min 原生表存在（L05-PA-G02） |
| R3 | 矩阵侧周期消费面 | 读 `t0_state_match_matrix.py:66-89,233-255` | signal | 周期从文件名正则回读；全交叉六键含 period |
| R4 | 生产触发面 | grep `t0_rule_engine|t0_state_match|t0_rule_pairs` 全仓（py/yaml/json） | signal（阴性即结论） | src/ 零命中、无事件挂点=纯研究轴 |
| R5 | 外部：多周期/分桶语义 | Crossref API 两轮检索（intraday momentum minute bars；bar aggregation alignment） | signal+noise 混合 | 2 条 SSRN 题录（单源=待验证）；电价条目 A 股适配闸驳回；"分桶对齐标准实现"=已查无 |
| R6 | 外部：WFE/闭卷判据族 | 留给 `state_match_downstream_surface` 矿 | 移长尾（非封矿） | 见该件 |
| R7 | 前端呈现向 | 内部 grep 仪表盘 | 已查无 | 记录查法，不硬造外部引文 |

> 本矿未做（禁越界声明）：未跑任何批算/未查真库（除目录列举）/未读 LANE-T0 在途产物/未改任何判据与阈值。
