# GPU 板块条件矩阵输入包（grid_gpu_sectorcond）

> 规格=深度案卷 §6（容量口径与义务定义）+ 考卡 v2 §2（frozen 输入）；回放面=
> replay_report.md（sector_state 425,787 行/985 日 close_final）。生成于 2026-09-24T08:35:26+08:00。

## provenance

- 源表：`c1_market.sector_state`（stage='close_final'，CH reader 只读）；日期骨架取
  `c1_market.kline_sector_880`（period='1d'，板数≥367 的 985 日，与回放窗一致）。
- **链 hash 前置断言**：生成前经冻结驱动 `freeze_baseline.py` 单一真源断言
  `kline_sector_880`/1d 链 sha256 = `710fe24490fbfe29dcbf90daf5f53904883add86782492bcd6cc6663f440ddd0`，与冻结常数及 `baseline_manifest_v0.json`
  逐位一致（MATCH，零漂移）。考卡 v2 §2：漂移即作废重做。
- sector_state 链现为 8d8f95ce879d…：由活值快照 011d4528… 经深窗回放演进而来，
  属 replay_report.md 登记的设计内变化（日期不相交方案），非 880 回补。

## 通道说明（全部稠密 .npy；行=板块、列=交易日升序，映射见 sector_index.json）

| 文件 | shape | dtype | 说明 |
|---|---|---|---|
| momentum_pct.npy | (469, 985) | float32 | sector_state.momentum_pct 原值；NaN=缺格/NULL（如实不插值：源内 NULL 2175 格 + 无 close_final 行缺格 36647 格） |
| rrg_quadrant.npy | (469, 985) | int8 | 象限编码 ''=0，'improving'=1，'lagging'=2，'leading'=3，'weakening'=4；0 同时覆盖源内空串（20398 格）与缺格（36647 格） |
| watch_score.npy | (469, 985) | float32 | **市场级标量**（实测每日截面 distinct=1，取值 {0.0, 0.03}）按板广播；缺格=NaN |
| is_holdout.npy | (985,) | bool | trade_date ≥ 2025-09-09 为 True（裁定#407 保密切点）；True=253 日 / False=732 日 |
| sector_index.json | — | — | sector_code→行号、日期→列号双向映射 + 板数/日数/生成参数/抽查对拍记录 |

已知缺口：末列 2026-09-23 活值仅 stage='pre_open' 行，close_final 过滤后全板缺格
（momentum=NaN、rrg=0、watch=NaN），如实呈现不借用 pre_open 值。

## 容量口径（防误读，案卷 §6 原义）

四通道合计约 4.2 MB，RTX 3090 24GB 显存占用 <0.05%——**整阵可常驻，
消费方无需分片加载**。59h（周五 12:00→周日 23:00）是**消费窗**而非施工窗：本包能否跑完取决于
消费方搜索空间（矩阵单元数 × 假设数），**不取决于本包体积**。本包义务=把贵算部分（动量分位原料/
RRG 象限/轮动标签/考试窗位图）预置交付，59h 预算全部留给搜索，不耗在预处理。

## NO_EDGE 警示（原文，随包必带）

> v1 S10 判 NO_EDGE：Q5−Q1=−0.2717%，t=−0.571，年度同号率 0.20——本包是同数据的条件化第二次提问，非独立发现

## 禁消费列声明

`strength`、`net_inflow_pct`、`capital_score` 三列**不在本包任何通道中**（考卡 v2 §2 frozen）：
前两者 42 日内 `constituent_count` 重复计数；`capital_score` 活表+回放面
425787/425787 全 NULL，该轴无活值，回放只能如实产 NULL，故不进包。

## 保密段声明

`trade_date ≥ 2025-09-09`（=考卡 v2 commit 冻结时点 −12 个月，裁定#407 滚动条款）
的数据**只供消费（考试），禁用于调参**（PB-08 + 裁定#407）。对应通道位图=is_holdout.npy。

## 自验记录

- 全部 .npy 载回断言 shape/dtype/NaN 计数与源查询一致（momentum shape；momentum dtype float32；momentum NaN == NULL(present)+absent；momentum finite == present-nulls 补集；rrg shape/dtype int8；rrg 零值 == ''行+缺格；rrg vocab 完备；watch shape/dtype float32；watch NaN == 缺格；watch 市场级（每日截面 distinct=1）；is_holdout dtype bool / shape；is_holdout True 数 == 切点后日数）。
- 抽查 3 个 (板,日) 格与 CH 单点查询逐位对拍 PASS：880001.SH@2022-09-01；880001.SH@2024-06-03；880001.SH@2026-09-22。
- 链 hash 前置断言 MATCH（见 provenance）。

规格真源：.runtime/sessions/st-statreplay-20260923/staging/sector_replay_depth_dossier_v0.md §6；docs/_working/sector_line/statreplay/sector_prereg_exam_cards_v2_frozen.md §2；docs/_working/sector_line/statreplay/replay_report.md
