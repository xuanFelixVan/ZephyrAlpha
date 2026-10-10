---
ttl: task_bound
title: 引擎 GPU 化·T2 等价协议采用 + T3 影子阶梯实录 + T4 施工（st-gpux-20261011）
created: "2026-10-11"
sid: st-gpux-20261011
family_id: GPUFEED-CAMPAIGN
lane: LANE-GPUX
evidence_grade: A（阶梯数字来自真实面板双跑产物逐位对拍；试件面 45 绿 6 预存红）
---

# T2 协议采用 + T3 阶梯实录 + T4 施工（st-gpux-20261011）

> 前置件=`01_gpux_t0_profile.md`（定靶与选型实测）。本件记"怎么保证搬上卡之后还是同一套数"。

## 〇、T2 不新立法：真源已在册，本班只消费

工单 T2 要求"先立数值等价协议再动生产"。进场考古发现**协议早已立法**，本班不重裁、不加第二条线：

| 需要的东西 | 在册真源 | 本班用法 |
|---|---|---|
| 逐位/容差/排名三层判据 | `docs/_working/gpu_rewrite/verification_framework.md` §二 | 阶梯每一级按层1/层2 断言，层3（整批 Spearman/top50）留给放量级 |
| 容差冻结值 | 同件 §一·补 表（net 逐日相对 ≤1e-5 FP32／≤1e-8 FP64；sharpe 与 ann_return 各绝对 ≤0.005；max_drawdown 相对 ≤1e-4；期末净值 ≤2bp；离散量 100% 精确） | 对拍脚本逐列按该表判 PASS/FAIL，不放松一格 |
| FP64 红线 | `new_asset_gpu_cpu_checklist.md` §二.2（Owner 令 2026-09-28） | 全程 FP64；本班实测支持（见 01 件 §三），故不必申请改线 |
| parity 先例与阈 | `gpu_core.py` 文件头 INVARIANTS + `tests/research/backtest/test_gpu_core_parity.py` | 新核沿用同件同阈（1e-12），双段归约模式实测 1.477e-12 后单列为 1e-11 并在试件注释里写明测量值 |

一处**在册内部矛盾**不自决、已登记（01 件 §六 D-A）：checklist §二.2 "FP64 红线绝对、禁 float32"
与 verification_framework §一·补 "必须走 FP32＋容差"。本班的实测把这条矛盾**在本班作用面上消解**
（FP64 就够 3x 以上，无须碰 FP32），但两件文档仍未对齐，归其属主车道或裁定通道处理。

## 一、T4 施工面（三处，全部缺省关）

1. `src/zephyr/backtest/gpu_core.py`（MOD-BT-233 原位扩面，**+426/−0 纯新增**）
   * 新 eval 节：`normalize_rows`（raw/zscore/rank/industry_neutral/size_neutral）、`industsize_rows`、
     `_rank_rows`（升/降/pct 三形，平均档并列组走既有 scatter_add 机）、`_row_mean/_row_std`（ddof=1 skipna，
     复用既有 `_neumaier_nansum_axis1` 补偿和）、`_group_mean_rows`/`_demean_rows`、`_regress_out_rows`、
     `ic_pair_rows`、`weighted_combine`、`orth_equal_rows`、`norm_rows_div`、`sizing_weights`（七形态）、
     `periodic_hold_rows`、`cap_clip`、`eval_cell_gpu`。
   * 单码路径纪律：每个函数只写一份，`xp=numpy|cupy` 由后端决定（文件头 INVARIANTS 既有要求）。
   * 新 `nvml_process_util()`：逐进程 SM 归因（ctypes 直调 `nvml.dll`，零新依赖）——见 01 件 §四。
2. `scripts/backtest/factory_grid_executor.py`（+385/−52，删除面全部逐行对上账，见 §三）
   * 新 `--eval-backend cpu|gpu|auto`，**缺省 cpu=原路逐字节零漂移**；
   * 新 `_prefix_eval_gpu`（前缀面）与 `_cell_eval_gpu`（单格定尺寸链）＋ `_cell_device_able`（叠加族判否）；
   * 抽 `_ic_weight_frame`（从 `_combine` 原样搬出，CPU/GPU 两条前缀路共用——禁复制第二实现面）；
   * 抽 `_FREQ_STEPS`/`_LAMBDA_PEN` 为模块常量（原两处内联字典上提，内容逐字同）；
   * 心跳并记归因三键（NVML 不可用时整键不出）；`summary.json` 的 `eval_gpu` 键仅在后端非 cpu 时出现。
3. `tests/research/backtest/test_l2_gpu_landing.py`（+555/−0，就地追加 20 支试件函数
   （dev 12 支→本道 32 支；参数化展开后采集面 51 支用例，其中新增 37 支），不新建试件册）

## 二、T3 影子阶梯实录（真实面板，双后端同 seed 同格集）

### 级 1：8 格（`--smoke`，零账本零试次）

| 轮 | cpu 目录 | gpu 目录 | 结果 |
|---|---|---|---|
| 首跑（口径缺陷在位） | grid_20261011-032628 | grid_20261011-032734 | **6/8 格被记 eval 阴性**（`eval_fail:ValueError`，见 §四 D-1）⇒ 停手 |
| 二跑（修 D-1 后，旧口径未修） | grid_20261011-033035 | grid_20261011-033126 | 8/8 出格，但 sharpe 最大差 **4.9e-2**、ann_return **1.5e-2**（线 0.005）⇒ **层2 FAIL**，逐格定位到两支 `industsize_neutral`（见 §四 D-3） |
| 三跑（口径修好后） | grid_20261011-034622 | grid_20261011-034706 | **PASS**：见下表 |

级 1 终轮对拍（同 8 个 recipe_id 逐列）：

| 指标 | 最大绝对差 | 最大相对差 | 冻结线 | 判定 |
|---|---|---|---|---|
| sharpe | 0.000e+00 | 0.000e+00 | 绝对 ≤0.005 | **PASS** |
| ann_return | 0.000e+00 | 0.000e+00 | 绝对 ≤0.005 | **PASS** |
| max_drawdown | 0.000e+00 | 0.000e+00 | 相对 ≤1e-4 | **PASS** |
| avg_turnover | 0.000e+00 | 0.000e+00 | 离散量 100% 一致 | **PASS** |
| net_days | 0.000e+00 | 0.000e+00 | 离散量 100% 一致 | **PASS** |
| degraded_dimensions | — | — | 100% 一致 | PASS |
| manifest `backend` 逐格 | — | — | 两侧同判 | PASS |

分流计数（gpu 轮 summary）：`prefix_gpu=6, prefix_cpu_kept=2, cell_gpu=6, cell_host_continue=5, cell_cpu_kept=0`
——2 个前缀不可移植（lasso 族，按 §五 交接点回原路）、5 个格含串行步交回原函数，
**其余确实上了卡**，而五项指标仍逐位等＝设备面与主机面同数。墙钟 44s→34s（8 格含装载，量不出吞吐，故有级 2）。

### 级 2：200 格（`--exploration-ledger` 分账，不占考试试次）

配对跑（同 seed=20261011、同分层维、单分片、串行先后各一轮，分册写本班 tmp 不碰战役分册）：
cpu=`grid_20261011-034911`（430s）、gpu=`grid_20261011-035629`（177s）。

| 读数 | CPU 后端 | GPU 后端 | 比 |
|---|---|---|---|
| 出格 / eval 死亡 / bt 死亡 | 199 / **0** / 1 | 199 / **0** / 1 | 两侧同集（bt 那 1 格同因，非算力面） |
| combine miss | 104/200 | 104/200 | 同（同 seed 同格集） |
| eval_s 均值 | 1.896s | **0.534s** | **3.55x** |
| eval_s 中位 | 0.593s | **0.168s** | 3.53x |
| eval_s p95 | 9.122s | 2.768s | 3.30x |
| bt_s 均值 | 0.152s | 0.147s | ≈1（本班不动此面，符合预期） |
| 单格 tot_s 均值 | 2.053s | **0.695s** | **2.96x** |
| 循环段墙钟 | 408s | 136s | **3.00x** |
| 折算吞吐 | 1,763 格/时 | **5,305 格/时** | 3.01x |
| 设备 util（nvidia-smi，含图形噪声） | 均 18.8% max 36% | 均 21.5% max 31% | ≥70% 采样占比两侧皆 0% |
| **本进程归因 SM**（NVML 逐进程） | 8.0%（n=2） | 8.5%（n=2） | 单分片心跳 60s 一轮，136s 窗只 2 枚——采样密度不足，另设并发探针（级 2b） |
| `in_compute_table` 心跳占比 | 33% | **100%** | GPU 轮全程持有计算上下文 |

分流计数（GPU 轮）：`prefix_gpu=78, prefix_cpu_kept=26, cell_gpu=130, cell_host_continue=104, cell_cpu_kept=44`
——78 个前缀真上了卡、26 个（lasso/pc1 族）按交接点回原路；130 个格走了设备定尺寸链、其中 104 个
含串行步交回主机续跑；44 个格因叠加族/不等形整格留 CPU。**出数面与 CPU 后端逐项对齐**（见下表）。

199 格逐项（同 seed 同格集，join 后按冻结线判）：**sharpe / ann_return / avg_turnover / net_days 四项 PASS，
max_drawdown 一项 FAIL（1/199 格）**。三层判据合看：

| 层 | 判据 | 实测 | 判定 |
|---|---|---|---|
| 层1 离散量 | 调仓行集/持仓只数/门判定/degraded/backend/prefix 集 | avg_turnover 与 net_days 199 格逐位等；degraded 全等；backend 逐格同判；prefix_key 集合等 | **PASS** |
| 层2 浮点 | sharpe ≤0.005 绝对 | max **3.0e-3** | PASS |
| 层2 浮点 | ann_return ≤0.005 绝对 | max **1.2e-3** | PASS |
| 层2 浮点 | max_drawdown ≤1e-4 相对 | max **4.55e-4**（1 格越线） | **FAIL** |
| 层3 整批 | Spearman ≥0.999 / top-k 重合 ≥0.98 / 符号一致 100% | **ρ=1.000000**；top10/20/50 重合 **1.0000**；196/199 格 sharpe 逐位等 | **PASS** |

越线那格（`72d259adba3d`：all_a_ex_st × industry_neutral × halflife20 × signal_strength ×
monthly × **drift_band** × cap10 × lambda_15bp × **top10**）用**全精度 `net_returns.parquet`** 复核，
排除了"manifest 只存 4 位小数"的伪影可能：net 序列在 970 个交易日里有 **462 天不同**、
单日最大差 4.0e-3 ⇒ **这是离散持仓翻转，不是浮点尾差**——全市场 5217 只里只取 top10，
卡上归约序差（~1e-16）把近并列的两只拆到边界两侧，一天换一只票，年化就走到 1e-4 相对线之外。
199 格里此类"真实序列差异"共 **3 格**（另外两格分别 4 天与 399 天）。

⇒ 阶梯判定：**级1 PASS／级2 四项 PASS + 一项越线／级3 PASS**，**整批不判绿**。
按 §五 的纪律，处理方向不由本班自裁（放宽线=改判据面，须走属主/裁定；三条候选见 03 件 §残余）。

#### 命中/未命中两面的单价（同格集配对，直接读 progress.jsonl）

| 面 | CPU eval | GPU eval | CPU tot | GPU tot | tot 加速 |
|---|---|---|---|---|---|
| 单分片 200 格 · hit（95 格） | 0.251s | 0.127s | 0.333s | **0.184s** | **1.81x** |
| 单分片 200 格 · miss（104 格） | 3.399s | 0.906s | 3.636s | **1.165s** | **3.12x** |
| 6 分片 GPU · hit（2,164 格） | — | 0.334s | — | **0.487s** | 相对单分片**慢 2.6x** |
| 6 分片 GPU · miss（826 格） | — | 2.065s | — | 2.631s | 相对单分片慢 2.3x |


**关键读数：单分片喂不饱卡。** eval 搬上卡后单格里设备只占很小一段，卡大部分时间在等 CPU 侧
（bt/成本门五档/编排/装载）。所以 ≥70% 利用率不是"搬上卡就有"，而是**并发度与融合度**的函数——
本班据此加做级 2b 并发探针，并把"要到 70% 还差多少设备秒/格"算成数（见 03 件 §验收实测）。


## 三、删除面逐行账（投袋前自证，合"共享件动手前先取 dev 现字节为基"纪律）

`git diff --numstat dev` 终态（2026-10-11 03:5x 实测）：

```
385    52    scripts/backtest/factory_grid_executor.py
426     0    src/zephyr/backtest/gpu_core.py
555     0    tests/research/backtest/test_l2_gpu_landing.py
 13     3    tests/research/backtest/test_factory_grid_instruments.py
```

核件与试件件对 dev 均**纯新增零删除**。执行器 52 条删除不靠手数，用一条可复现判据分类：
**每条删除行 strip 后若在新增侧有同形对应＝搬移/缩进移位；无对应＝必须逐条点名替代形态。**

```bash
python -c "import subprocess;d=subprocess.run(['git','diff','dev','--','scripts/backtest/factory_grid_executor.py'],capture_output=True,text=True).stdout;\
de=[l[1:] for l in d.splitlines() if l.startswith('-') and not l.startswith('---')];ad={l[1:].strip() for l in d.splitlines() if l.startswith('+') and not l.startswith('+++')};\
lost=[x for x in de if x.strip() and x.strip() not in ad];print('deleted',len(de),'无对应',len(lost));[print('  >>',x.strip()[:110]) for x in lost]"
```

实测结果：**52 条中 40 条有同形对应**（IC 权重块 10 行整体搬入 `_ic_weight_frame`；CPU 前缀块 18 行
与 `_sizing`→trigger→cap 块 12 行整体缩进 +4 移入 `else:` / `if weights is None:` 分支，内容零改）。

**无对应的 12 条，逐条点名替代形态**（全是我本批为实现功能而改写的行，无一例外）：

| 删除行 | 替代形态 |
|---|---|
| `w = w.reindex(dates).fillna(1.0 / len(names))` | 同表达式加 `return`（函数体搬进 `_ic_weight_frame` 末行） |
| `lam_map = {"lambda_0": ...}` | 常量上提 `_LAMBDA_PEN: dict[str, float] = {...}`（内容逐字同） |
| `l = lam_map[lam] * 100.0` | `l = _LAMBDA_PEN[lam] * 100.0` |
| `step = {"daily": 1, ...}[freq]` | `step = _FREQ_STEPS[freq]`（常量上提，内容逐字同） |
| `combined, rank, a1_deg, a2_deg = hit` | `..., *dev_rest = hit`（兼容旧 4 元组条目，取第 5 位为设备对） |
| `_combine_cache_store(combine_cache, cache_key, (combined, rank, a1_deg, bool(deg2)))` | 经 `entry` 变量，CPU 前缀在 gpu 后端时追加第 5 位设备对 |
| `def _instr_gpu_sample() -> tuple[float | None, float | None]:` | 三元组签名（追加归因 dict） |
| 其 docstring 行 | 新 docstring（说明"读不到禁写成没占用"） |
| `return float(util_s), float(mem_s)` | `util, mem = float(...), float(...)` 后统一出口 |
| `return None, None` | `util, mem = None, None` + 归因 try 段 |
| `gpu_util, gpu_mem = _instr_gpu_sample()` | `gpu_util, gpu_mem, attrib = ...` |
| `global _EXPLORATION_LEDGER` | `global _EXPLORATION_LEDGER, _EVAL_BACKEND` |

⇒ **外来内容零删除**（本班入口即测过：四支目标件在车道基线与 dev 逐位同；dev 又在本班开工前
从 `ac7565169f` 前进到 `5e8cf5f9a3` 共 6 笔，无一触及这四支——`git diff --name-only ac7565169f..dev` 实测）。


## 四、本班挖到并当班修掉的缺陷（含自犯，逐条给凭据）

| # | 缺陷 | 症状（实测） | 修法 | 配对试件 |
|---|---|---|---|---|
| D-1 | `_prefix_eval_gpu` 里 `bool(codes)` 对多元素 ndarray 求真值 | 首跑 6/8 格记 `eval_fail:ValueError`＝**算力面的坑变成判决** | 改判 `codes is not None and ng > 0`；并把该调用包进 try，异常一律出声降级 CPU | `test_dev_col_codes_no_bool_on_array`（把曾炸的表达式写成 `pytest.raises(ValueError)` 反例钉）＋ `test_evaluate_recipe_device_failure_degrades_to_cpu_not_cell_death` |
| D-2 | `eval_cell_gpu` 在 drift_band 交接格**提前**做了 cap clip | 换序＝换数（factory 次序 sizing→trigger→cap） | 串行交接格只做到 sizing，trigger→cap 全序交回原函数；periodic 与 clip 幂等性另证 | `test_eval_cell_drift_band_leaves_trigger_and_cap_to_host`（含"续跑等价"断言） |
| D-3 | **industsize 控制板口径错**：我在宇宙列切片后做组内去均值，factory 是在**全市场列**去均值后再 reindex 到宇宙列 | 二跑 sharpe 4.9e-2／ann_return 1.5e-2 超冻结线，而 turnover/net_days 逐位等（集合面没动、权重幅度面被改）；定位=两支漂格全是 `industsize_neutral`，正格里无一含它 | 新 `industsize_rows(ctrl_dm)`，ctrl 由调用方在全市场列集上去均值后切列；`normalize_rows` 对该模式**显式拒收**（禁核内按自己拿到的列集猜口径） | `test_industsize_ctrl_demeaned_on_full_market_columns_not_universe_subset`（**双向断言**：全市场口径 ≤1e-12、子集口径必须 >1e-6，否则本支自认失去判别力）＋ `test_industsize_mode_rejected_by_normalize_rows` |
| D-4 | 我的第一版 NVML 自测判据写错（浮点错位读出的 denormal 通过了 `0<x<=100`），当场报了"尺可用:True" | 假绿——我自称可用而实际字段错位 | 改三阶段对照实测（CPU-only 不入计算表／本进程忙时读数升／停算回落），并在核里只消费 f0 且带 0-100 sane 守卫 | `nvml_process_util` 实测输出（01 件 §四） |
| D-5 | 我在主区（非车道）直接编辑了 `gpu_core.py` | 违 RULE-WORKTREE 隔离施工默认 | 改动整体搬进车道、主区还原为 HEAD 字节并 `git status` 复核为空 | — （流程自纠，非代码缺陷） |
| D-6 | 我写的双跑探针本身有两只坑：`combine_cache` 传了两遍（TypeError 被 run_batch 吞成阴性）、写文件用了 git-bash 路径 `/d/…`（Windows python 打不开） | 探针空跑，`Empty DataFrame` | 诊断改用**已有产物**（两次 grid 目录的 `net_returns.parquet` 逐格差）+ 合成面板口径钉，反而更硬 | —（如实记，不假装探针成功过） |
| D-7 | 我第一版 `_demean_rows` 用 `mu[:, codes]`，无锚列 codes=-1 会被 numpy 取模索引静默取到**最后一组** | 若未修，"无行业锚票"会拿到别的行业的组均值＝静默口径替换，且对拍未必能一眼看出 | 先剔除无锚列再 scatter/gather，回填整列 NaN（与 factory `reindex(columns=…)` 失配→NaN 同态） | `test_eval_industry_demean_unlabeled_column_failclosed` |

## 五、施工边界（判据面零动的具体含义）

本班没动过：任何阈值、任何门禁判定、任何抽样/分层逻辑、任何 manifest 列、任何试次记账语义。
上卡面与留 CPU 面的清单、以及每条"为什么留"的实测理由，全部写在 01 件 §五。
所有新增键（`summary.eval_gpu`、心跳归因三键）都是**只在非缺省后端或读数可用时出现**的观测面。

## 六、复核命令

```bash
cd D:/ZephyrAlpha/.worktrees/st-gpux-20261011
export PYTHONPATH=D:/ZephyrAlpha/.worktrees/st-gpux-20261011/src   # 必指车道，否则读主区旧码=假绿
python -m pytest tests/research/backtest/test_l2_gpu_landing.py tests/research/backtest/test_gpu_core_parity.py \
  tests/research/backtest/test_c4_engine_gpu_wiring.py -q          # 应 45 绿 + 同 6 支预存红
git diff --numstat dev -- scripts/backtest/factory_grid_executor.py src/zephyr/backtest/gpu_core.py \
  tests/research/backtest/test_l2_gpu_landing.py
# 级 1 阶梯（可重放；--smoke 不记账本）
python scripts/backtest/factory_grid_executor.py --smoke --seed 20261011 \
  --stratify-dims G_universe,A1_factor_normalize,B_top_n --eval-backend cpu
python scripts/backtest/factory_grid_executor.py --smoke --seed 20261011 \
  --stratify-dims G_universe,A1_factor_normalize,B_top_n --eval-backend gpu
# 预存红自证（纯净 dev 字节复跑同样红＝非本班引入；跑完务必还原）
git checkout dev -- src/zephyr/backtest/gpu_core.py tests/research/backtest/test_l2_gpu_landing.py
python -m pytest tests/research/backtest/test_l2_gpu_landing.py -q
```
