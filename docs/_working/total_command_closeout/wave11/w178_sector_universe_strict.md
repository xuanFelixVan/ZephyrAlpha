---
ttl: task_bound
completes_when: "A/B/C/D/E 五段实测表齐 + 同目录 w178_universe_facts.yaml 落盘"
---

# W-178 板块宇宙 strict 复测案卷（wave11）

> **性质**：只读取证＋出案卷，**不裁真源、不自赋裁定号**。§E 是 `DRAFT_NOT_FROZEN` 草案，等 W-178 定案后由总包冻结。
> **机生表**：`docs/_working/total_command_closeout/wave11/w178_universe_facts.yaml`（57 个读数键，禁手改），
> 产出命令＝`python scripts/governance/wave11/w178_universe_facts_gen.py`（同目录生成器），
> 探针原始产物＝`wave11/probe/ch_probe_20260926T180553Z.jsonl`（最终批）＋同窗 `.sql` 清单。

## 0. 案卷头部四字段

- **turn_budget**：子代理轮预算 150；本卷骨架在第 9 次工具调用落盘（早于任何完整结论）；单块调研 ≤6 次；末段只落盘不新调研。实际用约 33 次工具调用。
- **verified（本机 strict 实测，全部走 W-180 合规通道）**：
  - 车道 Python 3.12.8；`PYTHONPATH=<lane>/src`（禁裸 python 导主区包）。
  - **读数批次**：通道① `scripts/governance/data_supply/ch_probe.py --file`（W-180.4 标准探针，内部 `ch_writer.query_strict`）
    逐行 ts 窗 `2026-09-26T18:05:50.567Z … 18:05:53.273Z`；通道② `ch_reader.query_rows()` 同批 `18:05:53Z … 18:05:56Z`。
    两通道 **57/57 一致**（`agree=true` 或 `agree_rows=true`），`failures=[]`，传输路径两次皆 **tcp**。
    本地墙钟＝2026-09-27 02:05（UTC+8）。
  - **CH 可达性＝可达**（TCP 9000 正常，无降级到 HTTP）。首探曾报红，见 §F.1。
- **assumed（旧册转述，未复测，不当现值用）**：`final_review_chartlib/ext_03_schedule_completeness_audit.md` §五 19:5x 读数（89,586 / 467 / 128 / 375 / 32,659 / 729 / 5,217）与 `10_wave_plan.md:181` 的"gap=262／滞后 21 天"；`tqcenter_provider.py:412` 注释"全族 594 只"；`du881_verdict/casefile.md:80` 的 132/134 拆解；`mainline_candidates.py:36` 的"469 板块/880001-880011"。**本卷只把 `sector_constituent` 旧数复测到逐条相同，把两处**语义**读错的地方纠正了（见 §A.2）。**
- **input_set_disjoint_with**：与 wave11 之外任何在途案卷无共享写入面；只读引用 `00_master_skeleton.md:238`（族 14 W-178 行）、`ext_03 §五/§七`、`config/search_space_prereg.yaml:44`（**未改一字**）、`config/flags.yaml`（未改）、`schemas/**`、`src/zephyr/**`、`scripts/**`。写入仅限 `wave11/`。
- **evidence_ref.cmd**：`bash: set -a; . /d/ZephyrAlpha/config/.env.clickhouse; set +a; PYTHONPATH=$PWD/src python scripts/governance/wave11/w178_universe_facts_gen.py`
  → 全量 SQL 原文/执行 SQL（FINAL 注入后）/耗时/行数/首行样本/时间戳逐条在 yaml `readings.<key>.channel_1|channel_2`；消费者反查＝`git grep -ln "<table>" -- '*.py'`（排除 test）。

---

## A. strict 复测现值

### A.1 逐表三列（读数 / 传输路径 / 时间戳）

| 对象 | strict 现值（通道①＝通道②） | 传输路径 | 时间戳 UTC（通道① / 通道②） |
|---|---|---|---|
| `sector_constituent` 880 段板块数 | **467** | tcp / tcp | 18:05:50.567 / 18:05:53 |
| `sector_constituent` 880 段成分行数 | **89,586** | tcp / tcp | 18:05:50.888 / 18:05:54 |
| `sector_constituent` 881 段板块数 | **128** | tcp / tcp | 18:05:50.911 / 18:05:54 |
| `sector_constituent` 881 段成分行数 | **5,538** | tcp / tcp | 18:05:50.917 / 18:05:54 |
| `sector_constituent` 全表板块数／行数 | 595 / 95,124 | tcp / tcp | 18:05:5x（键 `sc_all_boards`/`sc_all_rows`） |
| `kline_sector_880` distinct 板块数（全表） | **729** | tcp / tcp | 18:05:50.994 / 18:05:54 |
| ┗ 其中 880 前缀／881 前缀 | **601 / 128**（行数 602,204 / 158,814） | tcp / tcp | 键 `kl880_prefix`、`SET_kl880`、`SET_kl881` |
| `kline_sector_880` 行数 | 761,018 | tcp / tcp | 键 `kl880_rows` |
| `concept_board` 行数／distinct board_code | **375 / 375** | tcp / tcp | 18:05:51.363 / 18:05:54 |
| `concept_board_constituent` 行数／distinct board_code | **32,659 / 375** | tcp / tcp | 18:05:51.377 / 18:05:54 |
| `sector_list` 行数 | **5,217** | tcp / tcp | 18:05:51.430 / 18:05:54 |
| ┗ `sector_list` 语义实测：distinct `sector_name`=1（恒 **'沪深A股'**）、distinct `symbol_canonical`=5,217、SH 2,316＋SZ 2,901、`data_source`=miniqmt | ⇒ 它是 **A 股全池清单**，不是板块清单 | tcp / tcp | 键 `sl_sector_names`/`sl_symbols`/`sl_profile`/`sl_names` |
| 补齐通道面：`sector_constituent_snapshot` 行数／880 段板块数 | 570,744 / **467**（＝与基表同覆盖，`snapshot_adds=0`） | tcp / tcp | 键 `scsnap_rows`/`scsnap_880_boards` |
| 名册面：`sector_code_name_map` 行数／880 段板块数 | 729 / **601**（880 段板块名 100% 可解析） | tcp / tcp | 键 `name_map_rows`/`name_map_880_boards` |
| 第三张概念名册 `concept_sector` 行数 | 375（与 `concept_board` code 集 375/375 重合，与 880 段 0 重合） | tcp / tcp | 键 `concept_sector_rows`/`third_concept_roster` |

### A.2 与 ext_03 §五 旧数逐行 diff

| 对象 | 旧数（19:5x） | strict 现值 | 差 | 差异来源 |
|---|---|---|---|---|
| `sector_constituent` 880 段成分行数 | 89,586 | 89,586 | 0 | 无漂移（基表自 09-15 未更新，见 §B 新鲜度） |
| `sector_constituent` 880 段板块数 | 467 | 467 | 0 | 同上；旧册注"与 09-15 登记 469 差 2"＝在册口径差，非本次差 |
| `sector_constituent` 881 段板块数 | 128 | 128 | 0 | — |
| `concept_board` 行数 | 375 | 375 | 0 | 非空壳表得证（strict 计数＋375 个 distinct code） |
| `concept_board_constituent` 行数 | 32,659 | 32,659 | 0 | — |
| `kline_sector_880` distinct 板块数 | 729（旧册注："= 名册 729 ✅（**880 日K全覆盖**）"） | 729 | **0（但语义错）** | **本卷第一处更正**：729 不是 880 名册。实测 `kline_sector_880` 内 880 前缀 601＋881 前缀 128＝729（该表 2026-09-25 起按 `_get_kline880_universe()` 扩面收 881 段，见 `src/zephyr/data/implementations/tqcenter_provider.py:239-262`）。旧册"880 日K全覆盖 729"把混族总数当 880 单族名册 |
| `sector_list` 行数 | 5,217 | 5,217 | 0 | **第二处更正**：旧册把它列在"板块宇宙"表内，实测其 `sector_name` 恒为'沪深A股'、5,217 个 symbol ⇒ 它是**股票池清单**（A 股全池），不是板块清单 |
| **gap（有行情无成分映射的 880 板块）** | **262**（=729−467，`00_master_skeleton.md:238`／`10_wave_plan.md:181`／`ext_04:76` 同口径） | **134** | **−128** | 差异 **100% 由上行语义错误派生**：真尺＝601−467＝134（双探测互证，§B）。旧数把 881 段 128 只算进"880 缺口"。与 09-15 在册的 **132** 差 **2**＝同期漂移，非翻倍扩大 |

> 结论性事实（不裁真源）：**ext_03 §五 与 00 册 W-178 行的"gap 从 132 扩大到 262（近一倍）"不成立**；同一把尺子换成 strict 双探测后是 **132→134（+2 漂移）**。W-180 的"首位数字假象"病在这条上没有复发，复发的是**集合口径混族**，属新病种（建议归 W-180.3 污染面复测）。

---

## B. gap 现值与新鲜度滞后

- **尺**（严格集合差，非聚合相减）：`SET_kl880`（`kline_sector_880` 中 880 前缀 distinct sector_code，601） − `SET_sc880`（`sector_constituent` 880 段 distinct，467）。
- **现值＝134**。三探测互证：① SQL `NOT IN` 子查询＝**134**（tcp，18:05:51.456Z）；② python 集合差＝**134**；③ `agree=true`。成员全表（含空名）在 yaml `derived.gap_880_no_constituent.members_full`。
- **881 段 gap＝0**（`SET_kl881` 128 − `SET_sc881` 128；SQL 与集合差两法均 0）⇒ **881 行业名册对账闭合**，W-178 里"881 名册对账"一项在现值层面无缺口。
- **134 的成色**（与 `du881_verdict/casefile.md:80` 在册拆解对拍，独立复测）：`8803` 段 **61** ＋ `8804` 段 **71** ＋ `8808` 段 **2** ＝ **134**；这些码的 `kline_sector_880.sector_name` **全空**，`sector_constituent.sector_name` 880 段"可用中文名"板块数＝**0**（`sc880_named_boards`）。名册侧 `sector_code_name_map` 对 601 只 880 板块 100% 有名（含 8803/8804/8808）。
- **补齐通道实测增量＝0**：`sector_constituent_snapshot`（Phase 2 快照表）880 段 distinct 板块 **467**，与基表同集合，`SET_scsnap880 − SET_sc880 = 0` ⇒ **把快照表也算作成分源，gap 仍 134**（yaml `derived.gap_880_after_snapshot_union`）。
- **新鲜度滞后（业务表列，未走 `system.` 面）**：

| 表（判据面） | 业务日期列 | max | 滞后（对行情面 max(trade_date)=2026-09-24 / 对读表本地日 2026-09-27） |
|---|---|---|---|
| `sector_constituent` 880 段 | `max(update_date)`（同 `max(valid_from)`） | **2026-09-03** | **21 天 / 24 天** |
| `sector_constituent` 881 段 | `max(update_date)` | 2026-07-22 | 64 天 / 67 天 |
| `sector_constituent` 880 段 | `max(fetched_at)`／`max(ingest_ts)` | 2026-07-28 17:03Z／2026-09-03 11:39Z | 注：`max(valid_to)`＝**NULL**（全表无闭合切片⇒SCD-2 只有开段，当期真值式） |
| `sector_constituent_snapshot` | `max(snapshot_date)`／`min`／distinct 日数 | **2026-09-26 / 2026-09-14 / 6** | 新鲜（当日），但**只有 6 个快照日**⇒ 波 12 的 PIT 回溯深度不成立（见 §E 未决项） |
| `concept_board`／`concept_board_constituent` | `max(valid_from)`／`max(updated_at)` | 2026-09-24／2026-09-24 10:22Z | 0 天（与行情面同窗，**比 880 段基表新 21 天**） |
| `sector_list` | `max(trade_date)` | 2026-09-03 | 21 天 |
| `kline_sector_880` | `max(trade_date)`（`period` distinct=1，值 `1d`） | 2026-09-24 | 行情面基准 |

- **在册旧注核对**：`10_wave_plan.md:181` 写"`sector_constituent` 滞后 21 天在册"⇒ 与本次实测**同值**（21 天对行情面），未漂移；但 10 册同行"gap=262"须按本卷更正为 **134**。

---

## C. 两套并存口径对照（只给判定所需事实，不裁真源）

| 维度 | 口径一：`sector_constituent` 880 段（+881 段） | 口径二：`concept_board` + `concept_board_constituent` |
|---|---|---|
| 数据源列 | `data_source=tqcenter`（100%，467 板块／89,586 行） | `concept_board.data_source=akshare`；成分 `akshare_ths`（375 板块／32,659 行） |
| 板块码命名空间 | 通达信带后缀裸族 `880xxx.SH` / `881xxx.SH` | 6 位数字串 `'300008'` 型（THS/akshare 概念 ID） |
| 板块数 | 467（880 段）＋128（881 段）=595 | 375（`concept_sector` 名册与之 code 集 375/375 重合） |
| 成分行数 | 89,586（880 段） | 32,659 |
| 粒度 | 板块→股票多对多；**无日期切片**（`valid_to` 全 NULL），单板块均 191.8 只 | SCD-2（DDL-as-Code 声明 `valid_from/valid_to` 消幸存者偏差，`schemas/categories/market/market_concept_board*.py:19`），单板块均 87.1 只 |
| 成分股全集 | 6,179 只 distinct `stock_code` | 4,865 只 distinct `symbol_canonical` |
| 板块名可用度 | 880 段可用中文名板块数 **0**（名真源在 `sector_meta`／`sector_code_name_map`，本卷未测 `sector_meta`） | 375 个中文名全在列（样本：'5G'、'AI智能体'、'POE胶膜'…） |
| 新鲜度 | `max(update_date)` 2026-09-03（滞后 21 天） | `max(valid_from)` 2026-09-24（0 天滞后） |
| 消费者（`git grep -l '*.py'` 排除 test，文件数口径） | **23** 个文件：采集＝`tqcenter_provider.py:412`、`tdx_provider.py:296,336,353`、`sector_snapshot_collector.py:291`；信号/回测＝`signal_ashare/mainline_candidates.py`(SQL_SECTOR_CONSTITUENTS)、`position_sector_context.py:70`、`limit_up_reason_attribution.py:84`、`sector/sector_breadth|divergence|leader|siphon.py`、`sector_state_pipeline.py:25-26`、`sector_report_builder.py:134`、**`scripts/backtest/sector_prereg_exam_runner.py:48`（registry 表 `market_sector_constituent_880`）**；schema＝`market_sector_constituent.py` | **11** 个文件：采集＝`data/implementations/akshare_provider.py`；近数据＝`alt_data/concept_factor_mapper.py`、`data/backfill_checker.py`；面板＝`frontend/dashboard/api_server.py`；metaq 工棚＝`scripts/governance/meta_question/wo006/*`；schema＝`market_concept_board.py`、`market_concept_board_constituent.py` |
| `kline_sector_880`（行情面，729 码）消费者 | **21** 个文件（含 `sector_kline_downloader.py` 采集、`signal_ashare/sector/sector_momentum|rrg|divergence|volume_anomaly.py`、`sector_factor_manager.py`、`mainline_candidates.py:93,99`） | — |
| `sector_list`（5,217 只＝A 股池清单）消费者 | **10** 个文件（`miniqmt_provider.py:88,4461`、`catchup_guard.py:63`、`backfill_checker.py:329`、`source_health_check.py`、`sector_kline_downloader.py`） | — |

**若以某一套为跑批宇宙真源，另一套会漏/多哪些板块（集合差实测）**：

- **板块码层面完全不相交**：`SET_sc880 ∩ SET_cb = 0`；`only_in_sc880 = 467`、`only_in_concept_board = 375`；板块名层面同样不相交（`name_overlap = 0`，因 880 段名＝空/码回显）⇒ **两套口径没有任何可 join 的板块键**，只能按成分股集合对齐。
- **成分股层面近乎单向包含**：交集 **4,864**；`concept_board_constituent` 独有 **1 只**；`sector_constituent` 880 段独有 **1,315 只**；两口径并集股票池 **6,180 只**。
  ⇒ 事实：以 880 段为宇宙**不会漏掉**概念板股票（只漏 1 只），但**漏掉全部 375 个概念板块这个"分组维度"本身**；反之以 concept_board 为宇宙会**漏 1,315 只成分股归属**且完全丢掉 881 行业族与 880 指数族。
- **现行跑批引擎既不读口径一也不读口径二**（关键事实，供裁真源用）：`scripts/backtest/factory_grid_executor.py:167-178` 的 `G_universe`＝`{hs300, zz500, all_a_ex_st}`，成分快照真源＝`index_constituent`；行业维度词表＝`io_sector_sws_map.yaml` 的 `sws2021_l1`（同件 :115,189,223）。该文件**不在**上表 `sector_constituent`／`concept_board` 的消费者名单内 ⇒ 两套板块口径目前都**未接到 T1/共振矩阵的股票池与行业轴**上；已接的是"通达信 880/881 + 申万词表"两条腿中的前者→信号链（`sector_prereg_exam_runner.py`）与后者→factory 轴。

---

## D. 降级预案的事实面（"补不齐则降为观察轴"需要动的文件——只列，不动手）

在册先例写法（原文引用，`config/search_space_prereg.yaml` **本卷未改一字**）：

```yaml
# config/search_space_prereg.yaml :44（条件分层块内，:38 condition_stratification 之下）
      sector_layer: observational_only   # 板块腿 17 交易日禁入统计判据
```

同族在册表述（供写法对齐，非本卷新拟）：`docs/_working/e2e_integration/w3_w5_precheck_20260923.md:217` `observational_only:  # 禁入统计判据、禁当独立样本计 n`。

降级为观察轴**预计需动**的文件清单（列清单不动手；⚠ 标记＝本包硬禁改，须经 Owner 门位/正式通道）：

1. ⚠ `config/search_space_prereg.yaml`（在册先例位；冻结态改值＝flag 出厂翻转级，high tier）
2. 波 12 prereg 册（**尚未建册**；00 册 W-173/波 12 设计注"目标值在波 12 prereg 定"）——新建须走 CREATE-GUARD＋预注册纪律
3. ⚠ `config/flags.yaml`（若按 `du881_verdict/casefile.md:97` 处方走旗标隔离，如 `extra.include_industry_boards` 语义）
4. `docs/_working/total_command_closeout/00_master_skeleton.md:238`（W-178 行出口判据须按本卷现值改写：gap 134 非 262）
5. `docs/_working/total_command_closeout/10_wave_plan.md:181`（11.4 行"gap=262"更正）
6. `docs/01_policies_and_standards/_registry/…/ruling_registry.yaml`（若走"降级裁定"，RULE-RULING 须先登记且与留痕件同 commit 原子；**本卷不自赋裁定号**）
7. `scripts/backtest/sector_prereg_exam_runner.py:48` ＋ `schemas/categories/market/market_sector_constituent.py`（板块腿判据入口的 registry 消费位——观察轴要在此标"禁入统计判据/禁当独立样本计 n"）
8. `docs/_working/total_command_closeout/92_acceptance_rulers.md`（W-178 出口判据尺面须与降级口径一致，改判据须与 gate/册同批）
9. 若走"补齐"而非降级：`src/zephyr/data/implementations/tqcenter_provider.py` `_fetch_sector_constituent` 的宇宙源（在册两条处方见 `du881_verdict/casefile.md:97`——复用 `_get_kline880_universe()` 或新增旗标；**三处消费端各加同族旗标隔离，禁裸改 DISTINCT 查询**）

补齐可行性事实（非裁真源）：源端可补证据＝`sector_code_name_map` 对 134 码 100% 有名、`kline_sector_880` 对 134 码有行情（8803 段 61／8804 段 71／8808 段 2）；**在册成分源本身对这 134 码零覆盖**（基表与快照表各 467，快照无增量）⇒ "补齐"= 新增采集腿，非数据修复。

---

## E. 跑批宇宙声明草案 `DRAFT_NOT_FROZEN`

> 三轴（板块全集／股票池／图形信号族）。**只填已测事实＋标明未决**，等 W-178 定案由总包冻结；本件任何数值不得被引用为"已冻结宇宙"。

```
[universe v0-draft  DRAFT_NOT_FROZEN  measured_at=2026-09-26T18:05:5xZ(UTC)  channel=ch_probe+query_rows(tcp)]

轴 1 板块全集（三档并呈，不裁唯一真源）
  1a 行情可得档（kline_sector_880, period='1d', max(trade_date)=2026-09-24）
     880 前缀 601 ｜ 881 前缀 128 ｜ 合计 729；行数 761,018
     名册可解析：sector_code_name_map 729 行（880 段 601 全有名）
  1b 成分可得档（sector_constituent，update_date max=2026-09-03）
     880 段 467（成分 89,586 行，股票 6,179）｜881 段 128（5,538 行，与行情面 gap=0）
     缺口：880 段 134（8803:61 + 8804:71 + 8808:2）——有行情无成分
  1c 概念维度档（concept_board/constituent，valid_from max=2026-09-24，SCD-2）
     375 板块（akshare 命名空间）／32,659 成分行／4,865 只股票；与 1b 无共同板块键
  1d 现行 factory 档（与本包争的两套口径都不同）：sws2021_l1 行业词表（io_sector_sws_map.yaml）

轴 2 股票池
  2a factory G_universe 真源=index_constituent（hs300 / zz500 / all_a_ex_st）[在册未复测]
  2b 板块成分并集（strict）：6,180 只（sc880 6,179 ∪ concept 4,865；concept 独有 1）
  2c A 股全池清单（sector_list，miniqmt，max(trade_date)=2026-09-03）：5,217 只（SH 2,316/SZ 2,901）
     ⚠ 2c 与 2b 的**规模差＝963**（5,217 vs 6,180，两值皆 strict 实测，差为算术差）；
        两者**交集/包含关系未测**（未取逐码集合差）——"以 2c 作池会静默丢掉哪些成分归属"须补测后才能写进冻结件

轴 3 图形信号族（波 10 G-A..G-E）
  3a 板块腿统计可用度先例在册：sector_layer: observational_only（板块腿 17 交易日禁入统计判据）
  3b 板块日史深度：mainline_candidates.py:36 在册"自 2026-06 起采（~52 交易日）"，RRG 62 日常态降级 [在册未复测]
  3c 未决：134 缺口的图形腿（有 K 线无归属）与 375 概念板（无板块 K 线，只有成分股）
     能否进共振矩阵分母，取决于 W-178 定案——未定案前本轴禁冻结

冻结前置（本卷实测得出的硬事实）
  · gap 现值 134（不是 262）；补齐需新增采集腿，快照通道无增量
  · sector_constituent 880 段滞后 21 天（业务面），且 valid_to 全 NULL ⇒ 无历史切片可 PIT
  · 快照表仅 6 个快照日（2026-09-14 起）⇒ 若靠它补 PIT，深度=6 日
  · 两套口径无板块级 join 键 ⇒ 任何"合并宇宙"必须是股票级合并，且需声明去重律
```

---

## F. 通道缺陷与未取到清单（诚实面）

### F.1 车道 CH 配置缺失导致的**首探报红**（非 CH 不可达）

车道根无 `config/.env.clickhouse`（`ch_config.py:52` 以 `REPO_ROOT` 解析真源），首探 `--count c1_market.sector_list` 原文：

```
CH 配置文件不存在: <lane>\config\.env.clickhouse（CH 连接将失败）
clickhouse-driver TCP 连接失败 (:9000): CLICKHOUSE_HOST 未配置：os.environ 未设置且 ... 不含该键。
ClickHouse HTTP 连接失败 (:8123): [WinError 10061] 由于目标计算机积极拒绝，无法连接。
[RED] 探测失败（禁降级为无数据）: <count c1_market.sector_list where=''> -> ClickHouseQueryError
产物=<lane>\scripts\.runtime\tmp\ch_probe\ch_probe_20260926T175436Z.jsonl  共 1 次：ok=0 empty=0 fail=1
```

处置＝同 shell 内 source 主区 `.env.clickhouse` 注入 `os.environ`（`ch_config.ensure_ch_env_loaded()` 明写"已有 os.environ 不覆盖（允许环境变量显式 override）"），**未在主区/车道 config 写任何文件**，密钥未落卷。之后 57/57 读数 tcp 成功。

### F.2 W-180.4 探针新缺陷样本（建议登记，本卷未改探针一字）

`ch_probe.py` 对 `Date/DateTime/Decimal` 列的 `first_row_sample` 直接 `json.dumps` ⇒ `TypeError: Object of type date is not JSON serializable`，且崩溃发生在写出 JSONL/打印阶段，**一条脏值打挂整批 42 条探针**（本卷复现：rc=1，recs=0/42）。规避＝SQL 侧 `toString()` 包裹（已写进生成器注释）。这是"失败态伪装"家族的新病种：不是读成 0，而是**整批读数蒸发**。

### F.3 未取到 / 未测清单（禁推算，禁外推）

| 未取到项 | 状态 | 原因 |
|---|---|---|
| `sector_meta`（在册板块名真源）行数/覆盖 | **未测**（非失败） | 本包 SQL 清单未含；`mainline_candidates.py:36-40` 在册转述为 assumed |
| `sector_constituent` 880 段 `valid_from` 分布/历史深度 | 未测 | 只测 `max`；补测需按 code 分组的时点面 |
| `kline_sector_881` 独立表是否存在 | 已确证**无**（`system.tables` 面 sector/board/concept 共 19 表，无该件；881 行情在 `kline_sector_880` 内以 881 前缀存放） | 对象清单非新鲜度读数，允许 system. 面 |
| 963 只差集（2b−2c）逐码点名 | 未测 | 本包未取 `index_constituent`/`kline_daily` 股票全集 |
| Postgres / DatabaseService 侧任何面 | 未测 | 本包判据全在 CH 业务表；未跑通道③ |
| 09-15 登记的"132"与"469"原始件 | 未复核原件 | 只按 00/10/ext_03 册面转述（assumed） |

### F.4 复算命令（单条）

```bash
export PATH="/c/Users/fanzi/AppData/Local/Programs/Python/Python312:/c/Users/fanzi/AppData/Local/Programs/Python/Python312/Scripts:$PATH"
cd D:/ZephyrAlpha/.aidrafts/st-final-build-20260926
set -a; . /d/ZephyrAlpha/config/.env.clickhouse; set +a
PYTHONPATH=$PWD/src python scripts/governance/wave11/w178_universe_facts_gen.py
# 产物：wave11/w178_universe_facts.yaml + wave11/probe/ch_probe_*.jsonl + wave11/probe/probes_*.sql
# 期望：rc=0、failures=[]、derived.gap_880_no_constituent.agree=true（不一致即读数通道或库态已变，禁沿用本卷数值）
```

### F.5 纪律自证

未跑 `tests/governance/test_ops_guard_red_team.py`；零 git 写（无 commit/add/enqueue）；零 DDL/DML（全部 SELECT，探针本体只读）；零进程操作、零删除、零 CH VM/数据目录触碰；`docs/01_policies_and_standards/**` 与 `config/search_space_prereg.yaml`、`config/flags.yaml`、`exam_scale_cost_gate.yaml` 未改一字；写入仅 `wave11/` 三件（案卷＋机生表＋生成器）＋其 `probe/` 子目录。
