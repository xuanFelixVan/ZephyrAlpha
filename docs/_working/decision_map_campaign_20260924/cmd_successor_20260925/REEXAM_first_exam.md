---
ttl: task_bound
---

# REEXAM 首考收口案卷（续跑车道，2026-09-25 夜）

> 本卷=LANE-REEXAM 撞 150 轮上限身亡后的**续跑收尾**，不重做地基。
> 地基三件（盘上、未落 HEAD）：`scripts/backtest/reexam_cpcv_harness.py`、
> `tests/backtest/test_reexam_cpcv_harness.py`、`docs/_working/reexam_strategy_lane/pre_registration_card.md`。
> 判据真源零改动：阈值引 17 号文 §一 + `config/exam_scale_cost_gate.yaml`（frozen）+ 预注册卡
> 内嵌 `reexam_prereg_params_v1`（sha256 锁）。DSR 分母口径见 `src/zephyr/backtest/core/n_trial_ledger.py`
> （该件正由 LANE-PIT 修"t0 族试验数不入分母"，本车道**未碰**，只引用其现况）。
> 闭卷纪律：切点 2025-09-09 之后数据未用于判档/定档/调参（窗口在卡内冻结为 2019-01-04..2025-09-09）。

## 0. 在跑批实况（2026-09-25 22:27 实测）

- 进程 PID 34232 存活（21:58:59 起，未被误杀；`reexam_cpcv_harness` 子串在 `data/runtime/process_reaper_keep.txt`）。
- **交接材料口径与盘上 cmdline 不符**（实测取盘上）：
  `python scripts/backtest/reexam_cpcv_harness.py --batch p1_translated_jq_outpool --limit 30`
  ——批名无 `_pool`、无 `--batch 30`（`--batch` 只接一个值，30 走的是 `--limit`）。
- 池实测（`resolve_pool(None, 10**6, 0)`，只读探针）：可执行子集 **32 格**
  （translated 85 件 ∩ (出局 321 ∪ ibt POOL 17) → 去撞名后 32 唯一 candidate_id）。
  在跑批取 `sel[0:30]` → **本批 30 格，池内还剩 2 格**（offset 30..31）。
- 断点续跑机制（读码+实测确认，**无 `--resume` 旗**）：
  产物根 `docs/_working/reexam_strategy_lane/runs/<batch>/`；
  `state.yaml` 每格完成即写（逐格断点），`report.yaml`/`cells.csv`/`negatives.csv` **只在批末一次写**；
  续跑=同批名 + `--offset` 切片，命中 `state.yaml` 的 candidate_id 即跳过重算。
- 进度：22:10 第 1 格、22:19 第 3 格、22:27 仍 3 格（机器争用，T1 GPU 车道 PID 3584 + 十余条并行车道在抢 RAM/CPU）。
  单格实测耗时区间 **5–12 min** → 30 格 ETA **2026-09-26 01:30–04:00**（按当前争用强度外推）。
- 已跑 3 格原始观察（**非判据结果**：族卷未成，haircut/DSR/PBO 皆批末才算）：

  | candidate_id | 材料 | days | 冻结口径 Sharpe（仅观察） |
  |---|---|---|---|
  | JQ-21af8c66c15e-small_cap | 足 | 1622 | 0.279 |
  | JQ-25028ae0c266-high_div5y | 足 | 1622 | −0.248 |
  | JQ-29eb91dbaf60-crash_dodge | 足 | 1622 | 0.206 |

- 续跑命令（若 34232 中途身亡，**禁杀、禁改判据**，直接同批名续跑）：
  `python scripts/backtest/reexam_cpcv_harness.py --batch p1_translated_jq_outpool --offset 0 --limit 30`
  余下 2 格另开批（**禁与已完批共用批名续跑**，见 §3 缺陷 2 修后语义）：
  `python scripts/backtest/reexam_cpcv_harness.py --batch p2_translated_jq_outpool_tail --offset 30 --limit 2`

## 1. 实测条数对账（本车道自己数，不采信文档背数）

| 口径 | 文档所写 | 本车道实测 | 判读 |
|---|---|---|---|
| 在册 candidate | 19 号文 D2"在册 139 candidate 先考" | `docs/01_policies_and_standards/_registry/catalogs/strategy_registry.yaml`：161 = **19 active + 139 candidate + 3 deprecated** | **吻合**，19 号文无需改 |
| 139 可考性 | 19 号文暗含"先考在册" | candidate 条目 `code_path` 非空 **0/139**、`distilled_to_code` True **0/139**（active 19/19 齐备） | **在册 candidate 当前不可直接考试**，首考只能用外部代理批（预注册卡 §十既定） |
| 聚宽出局池 | 19 号文 D2"聚宽 322" | `data/strategy_intake/c4_deferrals.csv` 机读记录 **321**（文本 322 行含表头），md5 全唯一 321 | 文档口径系**行数非记录数**，差 1；建议 19 号文改注"321 记录/322 行" |
| 可执行子集 | 预注册卡"仅 13 条（85 c4 件 ∩ 出局 md5）" | 按 **md5 去重=13**、按 **可执行件=17**（同 md5 多变体件 value55/value_improved 等）；加上 ibt POOL 侧 15 件 → harness 实际可选 **32 格** | 卡的"13"是 md5 口径，与 harness 的 candidate_id 口径不同源；**两口径都真**，卷内已并列披露 |
| 潘潘并入宿主 | 交接材料"潘潘 159 条" | strategy 册含 alias **46 条/66 串**、factor 册 **106 条/202 串**（合计 152 条目/268 串）；doc_ref/正文含"吸收"合计 **76 条**（14+62）；两册直接提及"潘潘"字面 **0 条** | **无任何机读枚举等于 159** → 判"159"为散文口径，不可作为分批分母；沿用预注册卡 §附录 A 语义（重考=宿主条目分状态复验，非逐条复活），文档口径已改判 |
| DB 侧复核 | 任务书"走 DatabaseService 只读数在册条数" | `get_db_service().get_governance_conn(read_only=True)`：治理库 45 表，**无 strategy/factor 注册表镜像**（registr/strategy/candidate 零命中） | 注册数据真源=YAML（RULE-SSOT 规则侧），DB 无镜像可读；本卷条数以 YAML 实测为准，DB 探针结果如实附注（非缺陷，口径澄清） |

## 2. 首考三态结果

**未到终点，未考完。** 截至 2026-09-25 22:28：已跑 **3/30 格**，批内剩 27 格，池内另剩 2 格；
ETA 见 §0。族级三件套（haircut Sharpe / DSR / PBO-CSCV）与三态判档（REVIVAL_CANDIDATE /
RETAIN_RETIRED / INSUFFICIENT_MATERIAL）由 harness 在**批末一次性**产
`runs/p1_translated_jq_outpool/{report.yaml,cells.csv,negatives.csv}`，本夜若批不成，
**禁把"跑了 3 格"写成"考完 3 格"**；三态计数此刻=0/0/0（无一批报告，无 negatives 面落盘）。

判据落点（供批成后核）：逐格须同时过 成本门（frozen 五档 + 换手 ≤8x）+ haircut Sharpe>0 +
DSR≥0.95 + 族 PBO≤0.50，任一不过判 RETAIN_RETIRED 并入 `negatives.csv`（batch_id/candidate_id/
scope/failed_criterion/measured/window/caliber/generated_at 八列契约）；材料不足判
INSUFFICIENT_MATERIAL，**禁混入判负、禁进 negatives**。

## 3. harness 实测缺陷与两处小修（结构未动）

接手夜实测（非推测）撞出两处会让首考**出假卷**的缺陷，均做最小修 + 各配能红的尺：

**缺陷 1（批末崩溃）：族外格无判档键 → 整批报告在数小时算力后 KeyError。**
`run_batch` 家族分支里 `if cid not in ids: continue`，材料不足/零信号/执行错误格永不写 `verdict`，
而 `_write` 用 `c["verdict"]` 计数 → 批末崩。首考 30 格只要含 1 个零信号件即触发，算力全废。
- 修：族外格也走 `adjudicate()`（其内部对 `material_insufficient` 恒返
  INSUFFICIENT_MATERIAL，语义与预注册卡"材料不足≠判负"一致），再 `continue`。
- 红证：`tests/backtest/test_reexam_cpcv_harness.py::test_off_book_cells_still_get_verdict`
  —— 修前件（快照 `.runtime/tmp/reexam_harness_prepatch_snapshot.py`）跑出
  `KeyError: 'verdict'`（实测第 395 行），修后绿；并断言零信号格 verdict=INSUFFICIENT_MATERIAL 且不进 negatives。

**缺陷 2（断点续跑残卷假考）：resume 只回标量行，不回净收益序列与成本档。**
`if cid in done: rows.append(done[cid]); continue` —— `series[cid]`/`costs[cid]` 未重建 →
已跑格被静默逐出族卷：`n_trials_in_book` 只剩新算格，PBO/三件套在**残卷**上算，且复原行
`cost_passed=None` 必判 cost_gate 失败。预注册卡 §七写明的续跑纪律（"重跑自动跳过"）正好走这条，
首考一旦中途身亡并按文档续跑就会出假卷。
- 修（最小、加性）：每格完成后把净收益序列落 `runs/<batch>/ret_<candidate_id>.csv`（CSV，DCR-006 允许面），
  成本档结果以 `_cost` 键并入 `state.yaml` 行；resume 时必需件齐→复原入卷（计 `resume_restored`），
  材料不足格照终态复原，必需件缺（旧格式 state）→**重算**（计 `resume_recomputed`），绝不残卷计入。
  `report.yaml` 的 `pool` 节新增 `resume_restored` / `resume_recomputed` 两披露位。
- 红证：`::test_resume_restores_family_material` —— 修前快照断言 `'_cost' in state.done[0]` 直接红；
  修后：首格不重算（restored=1/recomputed=0）、族卷 `n_trials_in_book==3`、复原格带 haircut/DSR。
- 注意：在跑的 PID 34232 载的是**修前码**（进程内存），其 state.yaml 无 `_cost`/无 ret 件；
  若它身亡，续跑会把已跑格**重算**（慢但对，禁为省时而容忍残卷）。

测试同步：`tests/backtest/test_reexam_cpcv_harness.py` 全量 22 条在修后 **22 passed**（显式带路径跑，
未跑全仓套件），tmp_path 隔离，零写生产 `data/`。红证开关 `REEXAM_HARNESS_PATH`（默认=生产件，CI 行为零变）。

**加项 3（分批落盘，非缺陷修是事故处方）**：本 harness 判据件只在批末一次写 `report.yaml`——
30 格 ≈3.5 h 的算力暴露在一次命上（收割器"incubation_expired 处决长批、末尾才写=击杀即全损"
在 2026-09-25 已有实录）。故每格完成后额外刷新 `runs/<batch>/progress.yaml`
（cells_done / cells_selected / material_in_book / resume_restored / resume_recomputed / updated_at_utc，
**明写"进度件非判据"**，禁与 report.yaml 混读）。尺：`test_resume_restores_family_material`
内新增 `prog["cells_done"]==1 and prog["cells_selected"]==1` 断言（修前无该件→FileNotFound 即红）。

## 4. 与既有考尺件的分工与内收声明（谁也不替代谁，但共享件已内收）

| 件 | 考核对象 | 判据轴 | 与本 harness 的关系 |
|---|---|---|---|
| `scripts/audit/cost_trio_exam.py` | **已产材料** `data/backtest_artifacts/bt-*.json` 的配对样本（≥30 土规） | 三件套复算（成本真源 CST-T0-001，做T 31.2bp rt） | 不产回测、不做 CPCV 族卷 → **不替代**；T0 条件化考试仍在消费 |
| `scripts/backtest/exam_cost_reexam.py` | E4 存活池逐条**成本单轴**重考（五档单调性+全成本档存活+换手 8x），含 4440 照妖镜验收 | 成本门 | 同一 `exam_cost_gate` 冻结件被 harness **共享调用**（未复制判据）；照妖镜验收用途独有 → **保留，不退** |
| `scripts/backtest/f06_e4_wfa_exam.py` | 单配方滚动 WFA 正考（IS→WFA→OOS 三线 + 过拟合三维 + RB-STATS-01 充分性闸） | 单策略纵向稳定性 | 折切分口径≠CPCV 族卷口径，对象亦异 → **不替代** |
| `scripts/backtest/reexam_cpcv_harness.py`（本袋） | 退役/在册**族卷级**同卷同纪重考：CPCV C(6,2)=15 折逐格 + 族 PBO | 多重检验三件套 + 成本门 + 证据地板 | 数学零新造：切分委托 `zephyr.backtest.core.cpcv.generate_cpcv_splits`、DSR/haircut 委托 MOD-SIM-024 `deflated_sharpe_calculator`、成本门委托 `exam_cost_gate`、N 分母委托 `n_trial_ledger` |

净零账（全资产净零口径）：本车道**新增文件 0**（只改 harness + 其测试 + 案卷 + 车道清单追加），
未新增规则/gate/脚本/配置册，无退役替代声明。

## 5. 剩余工作量（交接给下一手或落地车道）

1. 等批成 → 读 `runs/p1_translated_jq_outpool/report.yaml` 填 §2 三态计数，逐格 n/成本档/
   haircut/DSR/PBO 全列出；负结果确认已入 `negatives.csv`。
2. 池内剩 2 格 → 按 §0 的 `p2_translated_jq_outpool_tail` 另开批（2 格族卷统计力不足，
   须如实披露"族 PBO 在 n=2 上不可信"，禁并入首考冒充 30 格卷）。
3. 在册 139 candidate 的**蒸馏缺口**：0/139 有 code_path → 须走 hypothesis_translator/SOP-C 翻译轨
   产 `build()` 契约件，才有"在册先考"的真首考（19 号文 D2 前半句目前不可执行）。
4. DSR 分母口径依赖：LANE-PIT 修 t0 族试验数入分母后，本批 `n_trials_ledger_cumulative` 须重读账本
   复核（不改判据阈值，只改分母读数）。
5. 落地前置义务（总筹在 `landing/lane_reexam.yaml` note 已写）：harness 需 CREATE-GUARD creation_token
   + `add_module_translation.py` 大白话简介登记；碰实现代码须同批同步 TDM algo_note_zh/algo_flow；
   本袋=研究面回测件，禁与文档袋混装。本车道**未提交任何东西**（严禁裸 commit/队列/cron）。
