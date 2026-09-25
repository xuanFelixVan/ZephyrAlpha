---
ttl: task_bound
title: LANE-DU881 案卷 · 881xxx 行业族 DU-01/02 三判据复测 + 补史可得性 + 成分扩容 + P1 v1↔v2
created: 2026-09-26
sid: st-qmine-20260925
lane: LANE-DU881
status: 终态——复测三条定案；补史判据源侧不可得（死亡证明式台账）；P1 对比件已交；成分扩容出待写清单未写库（前提证伪+连带面待裁）
---

# LANE-DU881 案卷 · "账面已落、实判未达"纠偏实录

> 判据真源：`docs/_working/decision_map_campaign_20260924/17_quantified_acceptance.md` §五 DU-01/02 行。
> **阈值一条未改、未销口**；本卷只出实测事实与可得性台账，重裁权属总筹/Owner。
> 取证工具：`zephyr.infrastructure.database_service` reader 连接（`get_clickhouse_conn(role='reader')`，禁裸 duckdb/裸构造 Client）；
> 表名一律经 `TableRegistry`，禁硬编码全限定名。探针脚本：`.runtime/tmp/lane_du881/du881_probe{1..10}*.py`（零写库）。

## 一、三条复测（交接账面 vs 本车道实测）

| 判据（17 号文 §五原文） | 交接账面值 | 本车道 2026-09-26 实测值 | 判定 |
|---|---|---|---|
| ①板块数 469→**≥727**（行业族 260 全量） | v5 已落 728/729 | `c1_market.kline_sector_880`（period='1d'）**729 唯一码**；近 5 交易日（09-17…09-24）每日 **728 码满量**；`ingest_ts` 首采台账：2026-07-24 落 2 码、2026-09-11 落 467 码（=v1 宇宙 469）、**2026-09-24 一次落 260 码（881 段 128 + 8803/8804 段 132）** | **一致 → 判据①达成** |
| ②历史深度对齐 880 族（2020-03 起） | 881 起点 2021-08-02，差约 17 个月 | 881 族 **128 码**：**127 码起点=2021-08-02**（每码 1253 根），**1 码 881479.SH 起点=2026-06-29**；881 族 `trade_date < 2021-08-02` 行数 **实测 0**；全表 min=2020-03-17 | **一致（881 未达 2020-03）**；**但判据本身与现实互斥，见 §二·乙** |
| ③P1 重跑 v2 覆盖行业族并出对比报告 | v2 曾在队、无对比报告 | 盘上 `data/strategy_intake/conditional_tables/p1_sector_by_phase.csv` = **4,362 行 = 729 码 × 6 相位**（881 段 128 码 / **764 行**，exam_ok=True 全表 2,874 格、881 段 509 格；n<30 保留为不可考 1,488 行）；`sector_name` 列 **0 行有值**；git 该路径**全史仅 1 次提交 `6fb93ebf39`＝"P1 v2 条件概率表（729 板块…）"** | **半一致**：v2 **已跑且已入库**（账面"曾在队"过时）；**无 v1↔v2 对比报告=一致**；**"v1=469 板块版已在盘上"不成立**——v1 原件被原地覆盖且未归档，只能按宇宙重放法重建（§四） |

**判据②的实测细化（关键新证，交接与 L03-B1/B7 簿均未量化）**：所谓"对齐 880 族（2020-03 起）"在 880 族自身也不成立。全库 729 码按首根日期分布——

| 首根区间 | 880 族码数 | 881 族码数 |
|---|---|---|
| ≤2020-06 | **1**（880854.SH，2020-03-17） | 0 |
| 2020-07…2021-07 | 6 | 0 |
| **2021-08…2021-12** | **133** | **127** |
| 2022 | 368 | 0 |
| 2023…2024 | 75 | 0 |
| 2025+ | 18 | 1 |

年度在库码数（period='1d'，uniqExact）：2020 年全库仅 **2 码/219 行**；2021-04-01 当日全库 **4 码**有 K 线；2020-06-01 当日 **1 码**。
→ 结论：**881 族起点（2021-08-02）恰好落在 880 族主体的众数起点桶（2021-08…2021-12）**；"881 比 880 浅 17 个月"的正确表述是"881 与 880 族主体同窗起步，而 2020-03 这条线全库只有 1 个码达到"。
→ 若判据②读作"对齐 880 族主体"则 **已达成**；读作字面"2020-03 起"则 **两族同时不可达**。此歧义属判据面事实，不改阈值，交总筹重裁（本车道不销口）。

## 二、补史可得性台账（"能不能补 2020-03→2021-07"）

### 甲、逐通道最小探针实测（全部只读，零写）

| 通道 | 实测请求 | 实测返回 | 定性 |
|---|---|---|---|
| A **tqcenter**（在册唯一活腿，`TQCenterProvider`） | `get_sector_list()` | 587 项：880 段 459 / 881 段 128 / **8803/8804 段 0** | 宇宙面：8803/8804 从未进入源侧板块清单 |
| A 同上·深度 | `refresh_kline([881101,881121,880881,880301],'1d')` + `get_market_data(count=600)` | 各 600 根，最早 **2024-04-10**（880881 626 根→2024-02-27） | 请求窗生效 |
| A 同上 | `count=1400` | 881 两码 **1250 根，最早 2021-08-02**；880301 同 **1250 根→2021-08-02**；880881 **1430 根→2020-11-06** | 881 段撞顶 |
| A 同上 | `count=2600` | 881/880301 **仍 1250 根（2021-08-02）**；880881 **2259 根→2017-06-13** | **同一通道同一批调用，880 族可深到 2017、881/8803 段停在 2021-08-02** → 深度上限是**源侧起点**，不是请求参数、不是代码缺陷 |
| A 同上 | `count=4000` | 与 count=2600 **逐字节同**（6009 根解析行） | 上限已饱和，加大请求无增益 |
| B **tushare** `ths_daily` | `881101.TI` / `881477(?)`… 实为 881101/881147/881385 三码各一次（start=20200101 end=20210801）+ 全史一次 + 截面 `trade_date=20210401` 一次 | **6 次全报同一异常**：`Exception: 抱歉，您没有接口(ths_daily)访问权限，权限的具体详情访问：https://tushare.pro/document/1?doc_id=108` | **权限/积分面不可得**（非网络、非接口不存在） |
| B 同上 `ths_index` | `exchange=SSE,type=I` 与 `exchange=A,type=N` 各一次 | 同样"没有接口(ths_index)访问权限" | 连行业码清单都取不到 → 无法绕过 |
| C **akshare** `stock_board_industry_index_ths` | `stock_board_industry_name_ths()` | 90 板（全 881xxx 码），与在库 128 码交集 **仅 18** | 覆盖面先天不足（110 码无腿） |
| C 同上·深度 | `symbol=建筑材料/建筑装饰/其他电子/计算机设备, start_date=20150101` | 各 **2852 行，最早 2015-01-05**，缺口窗 2020-03-02…2021-08-01 **各 347 行可得** | 深度够，但—— |
| C 同上·**同值性检验（决定性）** | 同日收盘价对拍：akshare vs 在库 tqcenter | 881115 建筑材料 2024-03-15 **3681.419 vs 734.97**（差 4.0×）、2026-09-24 **5681.831 vs 1728.8**（2.3×）；881116 2026-09-24 4160.917 vs 874.59（3.8×）；881123 2026-09-24 **21225.272 vs 655.79（31.4×）**；881130 2026-09-24 3970.343 vs 555.0 | **不同指数序列（不同基期/不同编制），追加即序列断裂污染 → 判"不可用作补史源"** |
| D 库内他表 | `c1_market.kline_sector`（tdx 遗留表）按前缀分组 | 含 881 段 128 码，但最早 **2026-01-09…2026-03-17** | 无深史，不可用作源 |
| E mootdx | 未在本轮重复打（L03-B1 簿记 2026-09-10 起"免费协议栈系统性死亡"、mootdx ext 已死） | — | **登记为"未测"**，不据此下结论 |

### 乙、结论：DU-01 判据②在现生存通道下不可达（死亡证明式）

1. **881 族（及 8803/8804 段）历史深度上限 = 2021-08-02**，硬顶在**源侧服务器**：tqcenter 请求 600→4000 根实证 1250 根封顶，而同一次调用中 880 族指数可深到 2017-06-13。这不是窗参、不是批大小、不是代码路径缺陷。
2. tushare 同花顺日线通道 = **账号权限不可得**（错误原文已录，非推测）。
3. akshare 同花顺行业指数通道 = **深度够但序列不同值 + 只覆盖 18/128 码**，追加会污染既有 tqcenter 序列，属"看似可补、实为造假"路径，本车道拒绝执行。
4. **DU-01/DU-02 上限声明**：881 族诚实上限 = **2021-08-02 起 / 127 码（+881479.SH 自 2026-06-29）**；8803/8804 段同顶 2021-08-02。
5. **交总筹的重裁请求**（不代裁、不改文件）：判据②若维持字面"2020-03 起"，则**880 族主体（含全部 260 只行业族）永久不达，DU-01/02 无法销口**；若按现实改述为"对齐 880 族主体起点（2021-08-02）"，则**判据②即时达成**。二者取一必须显式落纸，禁悬置（17 号文 §五 DU-07 行"二选一禁悬置"同构纪律）。

## 三、成分表扩容（`sector_constituent`）

### 甲、真源与写入器定位（实测）

| 件 | 位置 | 实测事实 |
|---|---|---|
| 写入器 | `src/zephyr/data/implementations/tqcenter_provider.py::_fetch_sector_constituent`（L511-578），capability=`sector_constituent` | 宇宙取自 `_get_sector_list()`＝`get_sector_list()` 过滤 `startswith('880')` + `_MKT_INDEX_CODES` |
| 调度 | `src/zephyr/data/config/tasks.yaml:2388` `sector_constituent_refresh`（source=tqcenter，schedule=monthly_static，incremental=false） | 描述仍写"约 84,450 条"（盘上 FINAL 实测 95,124，账面漂移未修，非本车道判据） |
| 表 DDL 真源 | `schemas/categories/market/market_sector_constituent.py`（SCD-2：valid_from/valid_to） | valid_to 全 NULL（实测 236,836 行 0 非空）＝B7-G2 在册 |

### 乙、复测：881 族成分**已在表**（与交接表述不一致）

`c1_market.sector_constituent` FINAL：**95,124 行 / 595 板块 / 6,179 只票**，全部 `data_source='tqcenter'`。其中 **881 族 128 码全在**（5,538 成分行，`sector_name` 5,538/5,538 有名，如 `881002.SH 煤炭开采 000552.SZ`），**valid_from=2026-07-23 批次**（早于 09-24 的 K 线补采）。
→ L03-B7 簿"881 补采后成分表未扩容（595 vs 729）"的**归因不成立**：881 侧无缺口；`729 − 595 = 134` 真缺码 = **8803 段 61 + 8804 段 71 + 8808 段 2**（`880851.SH`/`880890.SH`），即 TDX 行业裸码族，与 `tasks.yaml:2429-2431` 在册说明"该族不在 sector_constituent；名单 SSoT=sector_code_bridge.TDX_INDUSTRY_BOARDS"互证。

### 丙、可采性实测 + 待写清单（零写库）

tqcenter `get_stock_list_in_sector` 对 134 缺码逐码实采（探针 `.runtime/tmp/lane_du881/du881_probe13_manifest.py`）：**132 码回成员，合计 8,473 个 (板块,股票) 候选对**（深市 4,380 / 沪市 3,546 / 北交所 547），**2 码空板**（880851.SH、880890.SH，源侧回空列表非异常）；**键级查重实测：8,473 对与表内既有键重叠 0 对**（按 (sector_code, stock_code) 逐键比对，非聚合计数）。
→ 待写清单已产出：`constituent_expansion_manifest.yaml`（本目录，`written_to_ch: false`）。

### 丁、为什么本车道**未**径行写库（连带面实测，非拖延）

`sector_constituent` 是**三处采集宇宙的唯一读取源**，扩 134 码会即时改动作为：
1. `_fetch_kline_sector`（tqcenter，写遗留表 `kline_sector`）`tqcenter_provider.py:419-422` 直查 `SELECT DISTINCT sector_code FROM sector_constituent` → 该表宇宙 594→728（且 `sector_divergence.py:51` 等下游把 880/881 当"异构族"处理）；
2. `tdx_provider._resolve_sector_symbols`（`tdx_provider.py:296-320`，头注明确断言"该表仅存 8800/8802/8805-8809 + 异构 881"）→ 1 分钟 K 线盘中任务会把 8803/8804 塞进**已死的 mootdx 腿**，与 `include_industry_boards` 旗标路径重复计数；
3. `sector_snapshot_incremental`（`tasks.yaml:2410`"轮询池从 sector_constituent 表动态获取"）→ 盘中轮询池 +134 码。
且"四坐标系（469/596/90/729）未裁"属 Owner 门位（L03-C04 在册）。**通宵多车道并发窗口径盲翻 = 制造回归**，故本车道交付到"待写清单 + 生成器改造点"，翻转与写入留待坐标系裁定与串行窗口。

### 戊、施工配方（给总筹一键执行）

改生成器不改产物：`_fetch_sector_constituent` 宇宙源 `_get_sector_list()` → 复用同文件既有 `_get_kline880_universe()`（729，含 TDX_INDUSTRY_BOARDS 在册常量），或按分钟K任务同款旗标语义新增 `extra.include_industry_boards`（默认 false，翻转即扩容）；三处消费端（丁表 1/2/3）各加同族旗标隔离，禁止裸改 DISTINCT 查询。
证尺（先红后绿）已就位的一半：`tests/zephyr/data/test_providers_stage3.py:576` 已在册"sector_constituent 已含 8803 码时不重复抓取"——说明该族**本就被预期在表内**，扩容后此测试口径需复核不回归。

## 四、P1 v1↔v2 对比报告（DU-01 判据③交付件）

### 甲、生成器转正 + 宇宙白名单

`.runtime/tmp/p1_conditional_tables.py`（一次性脚本，L03-B8-G3 在册债）→ **转正为 `scripts/backtest/p1_conditional_tables.py`**：计算核逐行等值（Wilson LB、MIN_OBS=30、dropna=False 组键保护、相位 PIT 语义全保留），新增三件能力：`--codes-file`（宇宙白名单）、`--out-dir`/`--cache`（重放不污染生产产物）、`diff` 子命令（v1↔v2 对比器）。
防护核查（按"谁调它＋能否改变行为"三查，不只看 SQL 在不在）：`librarian.py:158` 取字段用 `f.get("potential_consumers")`（缺省=None，非 `or []` 空数组兜底）→ 同一 None 传入 `librarian.py:172/217` 两处执行的 `ledger_schema.py:107 _SQL_UPSERT_ASSET` → `:125 potential_consumers = COALESCE(EXCLUDED.potential_consumers, lib_assets.potential_consumers)`：**缺省保留存量、显式空数组才清空**，调用链实到、能改变行为，防护在位（非装饰）。本车道 P1 重跑**零写库**（只读 CH + 写 CSV 产物），不触发该链。

### 乙、v1 宇宙按台账实证重建（非记忆、非 README 抄数）

v1 原件已被原地覆盖且**从未单独入库**（`git log --all -- data/strategy_intake/conditional_tables/` 全史仅 1 次提交＝v2）。
v1 宇宙改按 **`ingest_ts` 首采台账**机械派生：首采日 ≤2026-09-11 的 **469 码**（清单 `../../../../../../data/strategy_intake/du881_verdict_case/p1_v1_universe_469codes.txt`，本目录）→ 重放 T1 = **2,806 格**，与 README 记载的"469×6=2,806 格（可考 1,837/不可考 969）"**逐数吻合（2,806/1,837/969 三项全等）**＝v1 重放有效性的独立旁证。

### 丙、对照控制（防"重放器自己造假"）

转正后的生成器按**全宇宙**重放 → 与盘上/HEAD 的 v2 产物逐格对拍：**4,362 格全共同、0 格仅在一侧、n/raw_win_rate/wilson_lb/mean_bp 四列漂移 0**（`.runtime/tmp/lane_du881/p1_ctl_diff/s.json`）。→ 重放管线与产线同源，下述对比可信。

### 丁、v1↔v2 对比结论（四元组口径，n<30 全程禁并格）

| 项 | v1（469 码） | v2（729 码） | 变化 |
|---|---|---|---|
| T1 格子数 | 2,806 | 4,362 | **+1,556 新格**（881 族 764 + 8803/8804 族 792） |
| 可考格（n≥30） | 1,837 | 2,874 | **+1,037（+56.4%）**；新增中不可考 519 格按原格保留不并池 |
| 既有格子数值 | — | — | **2,806 格逐格零漂移**（四元组全等）→ 扩宇宙未扰动任何存量结论 |
| 881 族格子 | 0 | 764（128 码） | 可考 509 格，**median n=137、median 区间宽(raw−WilsonLB)=0.0812**；880 族主体同期 median n=113、宽 0.0918 → 行业族样本密度**不低于**存量主体 |
| T2 动量系数（宇宙敏感面，池化） | 5/6 相位 | v2 | 系数位移全部 \|Δ\|≤0.0015（expansion −0.0165→−0.0158、capitulation −0.0272→−0.0269、distribution −0.0237→−0.0241、euphoria −0.1037→−0.1049、accumulation −0.0184→−0.0169）→ **"高低切/负动量"读数对扩宇宙稳健，无一经 0 翻向** |
| T2 ignition | 0.6109（n=468） | 0.5664（n=727） | Δ=−0.0445，**唯一显著位移格**，但两侧均系 1 路由日样本（B8 实测"不可用级"）→ 只如实报位移，不作任何结论 |
| T3 转移矩阵/停留 | 市场级 | 不受宇宙影响 | 恒等（相位路由序列与板块宇宙无关） |

产物：`../../../../../../data/strategy_intake/du881_verdict_case/p1_v1v2_cell_diff.csv`（2,806 共同格四元组 A/B 并排 + `ci_width_lb`，本目录）、`p1_v1v2_summary.yaml`（分层计数/T2 对拍/新格族别，本目录）。
**区间宽口径声明**：本卷"区间宽"＝`raw_win_rate − wilson_lb`（Wilson 95% 单侧下界距离），非双侧 CI 全宽；两侧对比同口径。
**README 漂移未由本车道手改**（469→729、.txt→.csv 两处）：按"生成器重出 README、禁手改数字"纪律（L03-B8-G2 施工 P0 文档面），须由 README 生成器承接，本卷只出实测数与其差。

### 戊、证尺（能红：三处变异实跑全红）

`tests/backtest/test_p1_conditional_tables.py`（4 项，全 `tmp_path` 合成数据，零碰生产 data/、零连 CH）：
1. `test_whitelist_restricts_universe` — 宇宙白名单失效即红（变异 M1 把过滤改 no-op → **FAILED**，实测）；
2. `test_build_tables_respects_exam_floor` — n<30 必须留档且 `exam_ok=False`（禁静默剔除/禁并池）；
3. `test_diff_detects_cell_drift` — 对比器漏判漂移即红（变异 M2 让比较恒真 → **FAILED**，实测）；
4. `test_diff_counts_new_cells_only_in_b` — 新格不得混进"共同格子"冒充一致（变异 M3 令 only_b=0 → **FAILED**，实测）。
变异脚本：`.runtime/tmp/lane_du881/du881_red_proof_p1.py`（逐变异改写源文件→跑测试→**按字节还原并校验 sha256**；踩坑实录：首轮用 `write_text` 还原把源文件转成 CRLF 触发还原校验失败，改 `write_bytes` 后三变异全红+基线 4 passed）。


## 五、附带发现（本车道复测中撞到的，均非本车道判据，转记不代修）

1. **P1 六件产物在主区暂存区被标记为 staged deletion**：`git status --porcelain data/strategy_intake/conditional_tables/` → 6 行 `D `（README + 5 个 CSV，含已提交的 v2 主表 4,363 行）。HEAD 与盘上内容一致（4,363 行含表头），但**任何一次他队 `git commit` 落地都会把这六件从库中删除**（盘上转未跟踪）。本仓有"22 件消失案"先例 → 属**蒸发级风险**，即刻报总筹；本车道按纪律**不动别人的暂存条目**。
2. **`kline_sector_880` 存在未合并副本**：2026-09-22/23/24 每日 raw 1,006 行 vs FINAL 728 行（+278），全表 raw 761,860 vs FINAL 761,018（842 个 (trade_date,sector_code) 键两版本，`ingest_ts` 分别为 08:30:40Z 与 19:27:21Z 两次写入）。ReplacingMergeTree 语义下不算损坏，但**下游漏 `FINAL` 即重复计数**（`sector_leader.py` 头注已在册此坑）；交接与 L03-B1 簿"728 满量"是 uniqExact 口径、"761,018 行"是 FINAL 口径，两处口径不同源，建议统一写"FINAL 口径"。
3. **`sector_name` 在 `kline_sector_880` 为 0/761,860 填充（100% 空串）**，而主数据 `data/registers/metaq_sector_name/sector_code_name_registry.csv`（730 行）**行业族名称已 100% 齐**（industry_ths 128/128、industry_l1 61/61、industry_l2 71/71、region 32/32、concept_or_style 425/426）→ L03-B1-G1 的原料已备、只差一次回填，与本车道 P1 表的 sector_name 全空同因（不属 DU-01 三判据，转记）。
4. **P1 相位真源仍在他会话 worktree**：生成器 `.runtime/tmp/p1_conditional_tables.py` 的 `PHASE_CSV=.worktrees/st-t0-matrix-20260924/docs/_working/t0_matrix/six_phase_history_v1.csv`，该件 **不在 HEAD**（`git ls-files` 查无）→ 重算依赖一个可被清理的会话工作树，属排班债（L03-B8-G3 在册）。

## 六、复核命令与证据等级

| 结论 | 证据等级 | 复核命令（只读，可直接跑） |
|---|---|---|
| 判据①达成 729/日均 728 | 实测（CH reader 双连接交叉） | `python .runtime/tmp/lane_du881/du881_probe2.py`（§A/B/G） |
| 881 起点 2021-08-02、前段 0 行 | 实测 | `python .runtime/tmp/lane_du881/du881_probe10_depth.py`（末段 count()） |
| "880 族仅 1 码达 2020-03" | 实测 | 同上（首段年度表） |
| 881 成分已在表（128 码/5,538 行） | 实测 | `python .runtime/tmp/lane_du881/du881_probe2.py`（§G） |
| 缺 134 码=8803(61)+8804(71)+8808(2) | 实测 | 同上（§E）+ `python .runtime/tmp/lane_du881/du881_probe3.py`（§E 与 TDX_INDUSTRY_BOARDS 对拍） |
| tqcenter 881 深度硬顶 | 实测（四档 count 递增） | `python .runtime/tmp/lane_du881/du881_probe8_depth.py` |
| tushare ths_daily 无权限 | 实测（错误原文） | `python .runtime/tmp/lane_du881/du881_probe5_tushare.py` |
| akshare 序列不同值 | 实测（同日收盘价对拍 4 板 × 5 日） | `python .runtime/tmp/lane_du881/du881_probe9_akshare_admission.py` |
| P1 v2 已入库、无对比报告 | 实测（文件解析 + git 全史单提交） | `python .runtime/tmp/lane_du881/du881_probe4.py`（§C）+ `git log --oneline --all -- data/strategy_intake/conditional_tables/` |
| P1 六件被 staged 删除 | 实测 | `git status --porcelain data/strategy_intake/conditional_tables/` |
| v1 宇宙=469 码（首采台账派生）与 v1 重放 2,806/1,837/969 三数吻合 | 实测 | `python .runtime/tmp/lane_du881/du881_run_p1_compare.py`（前 2 行打印）+ 对照 README |
| 重放器与产线产物逐格等值（对照组） | 实测（四列零漂移） | `python -c "import json;print(json.load(open('.runtime/tmp/lane_du881/p1_ctl_diff/s.json',encoding='utf-8'))['cell_drift_by_column'])"` |
| 8803/8804 成分可采（132 板/8,473 对/键级重叠 0） | 实测（逐码请求，未写库） | `python .runtime/tmp/lane_du881/du881_probe13_manifest.py` |
| P1 证尺能红（M1/M2/M3 变异全红） | 实测（变异→测试→字节级还原校验） | `python .runtime/tmp/lane_du881/du881_red_proof_p1.py` |

## 七、终态与交付清单

| 判据/施工项 | 本车道终态 | 交付件 |
|---|---|---|
| DU-01① 板块数 ≥727 | **达成（既有，本车道复核确认）** | §一表（`du881_probe1/2`） |
| DU-01② 历史深度 2020-03 | **不可达（死亡证明式台账）** → 不销口，交总筹按现实重裁 | §二（probe5/8/9/11 台账；上限=2021-08-02） |
| DU-01③ P1 v2 + 对比报告 | **交付完成**：v2 已入库（既有）+ v1↔v2 对比件三份 + 生成器转正 + 4 项证尺（3 变异全红） | §四 + `../../../../../../data/strategy_intake/du881_verdict_case/p1_v1v2_cell_diff.csv`/`p1_v1v2_summary.yaml`/`../../../../../../data/strategy_intake/du881_verdict_case/p1_v1_universe_469codes.txt` + `scripts/backtest/p1_conditional_tables.py` + `tests/backtest/test_p1_conditional_tables.py` |
| L03-B7-G1 成分扩容 | **半态（如实标注）**：881 侧实测无缺口；134 缺码=8803/8804/8808 段，已出待写清单与生成器改造点，**未写库**（三处采集宇宙连带 + 坐标系待 Owner 裁） | §三 + `constituent_expansion_manifest.yaml`（`written_to_ch: false`） |
| 补采作业（事件驱动/批处理） | **未建**——判据②经实测为"源侧不可得"，建补采器＝给不可达目标造半成品；一次性深度探针已归档（probe8/11），复核只需重跑 | §二 |

## 八、剩余工作量与移交（不悬置，逐条给解锁条件）

1. **DU-01/02 销口**：唯一卡点＝判据②口径重裁（改述"对齐 880 族主体起点 2021-08-02"→②即时达成并可销口；或维持 2020-03→永久不可达并如实记"上限 2021-08-02"）。**须总筹/Owner 落纸，本车道不代裁。**
2. **成分扩容写库**：解锁＝坐标系裁定（L03-C04）+ 三消费端旗标隔离改造（§三·戊配方）。工作量实测锚定：132 板 8,473 对，写入一次约 132 次源请求（0.05s/码限速，<1 分钟）+ 复验。
3. **README 口径漂移**（469→729、.txt→.csv）：解锁＝README 生成器承接（禁手改），本卷已给全部实测数。
4. **sector_name 100% 空置**：主数据已 100% 齐（`sector_code_name_registry.csv` 730 行），差一次回填＋日更纳入（L03-B1-G1 在册，本车道未动）。
5. **蒸发风险即报**：P1 六件在主区暂存区被 staged 为删除（§五·1）——须总筹在下次落地前处置，否则判据③的交付物载体本身会被删。


> 载体注记：交付机读件按纪律用 `.yaml` 不用 `.json`——对比器 `diff` 子命令原生输出 JSON，入本目录的交付件已转 YAML 并补 frontmatter（`p1_v1v2_summary.yaml`，原 `p1_v1v2_summary.json` 已删）；`.runtime/tmp/lane_du881/p1_ctl_diff/s.json` 为对照控制组的临时中间件，留 .runtime 不入库。


> 路径迁移披露（st-ddup-20260925）：两件数据证据（.txt/.csv）因 DIRECTORY-CONTRACT（docs/_working 目录扩展名白名单）迁至 data/strategy_intake/du881_verdict_case/，内容零变更。
