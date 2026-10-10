---
ttl: task_bound
title: 引擎 GPU 化·T0 画像定靶 + T1 选型实测（st-gpux-20261011）
created: "2026-10-11"
sid: st-gpux-20261011
family_id: GPUFEED-CAMPAIGN
lane: LANE-GPUX
evidence_grade: A（全部数字为本机 RTX 3090 实测；探针件在 .runtime/tmp/st-gpux-20261011/，逐条带复核命令）
---

# T0 画像定靶 + T1 选型实测（st-gpux-20261011）

> 工单=总统统筹 2026-10-11 凌晨「引擎 GPU 化工单」（Owner 已批）。本班是 `00_gpufeed_report.md`（st-gpufeed-20261010）
> 的续班：那一班把均格 2.87s→1.707s（prefix 顺序化治本）并把仪表装上窗；本班负责"把 eval 计算核真正搬上卡"。
> 净零声明：本班**不新建计算件**——`gpu_core.py`（MOD-BT-233）原位扩面，实现的是
> `new_asset_gpu_cpu_checklist.md` §五 早已登记的 P2 候选「权重构造批化（combine 缓存未命中面）」，
> 不是平行新轮子。零新依赖（NVML 走 ctypes 直调驱动自带 `nvml.dll`）、零新门禁、零新注册表。

## 〇、TL;DR

1. **工单前提坐实**：今晚 38,956 格仪表（15 批，墙钟 18:38:36→00:22:10）分段求和 19,913.3s，
   其中 **eval 16,367.4s = 82.19%**、bt 16.10%、write 1.14%、fetch 0.57%。靶=eval 无疑。
   （开局我据单格首行读数 `bt_s=22.5s/tot 27.7s` 说过"回测核占 81%"——那是**每分片首格的数据装载预热伪影**，
   全量聚合后自我推翻，如实记此反转。）
2. **靶内的再切分**（38,502 格按 manifest 身份 join，15,489 eval-秒）：宇宙面 `all_a_ex_st` 独占
   **74.2%**（zz500 15.9%／hs300 9.9%）；combine 状态面 **命中路径 60.4%／未命中路径 39.6%**。
3. **Amdahl 硬账**：eval 占格耗时 82%，故 **eval 归零的上限只有 5.6x**；要 ≥3x 需 eval 自身降到
   ~0.09s/格（5.6x on eval），即**命中面与未命中面都必须上卡**，只搬一半到不了 3x。这条决定了施工范围，不是偏好。
4. **选型不再开放**：仓内 `#ARCH-TORCH-CPU-ONLY`（`architecture_issue_registry.yaml:9858`）+
   `requirements.txt:5-10` 钉 torch **CPU 版（明写 2.13.0+cpu）**，四问门 Q4 判 cuDF 不可用、
   **合法载体=CuPy**；本机 polars 1.41.2 无 `collect(backend=)` API（实测 TypeError）⇒ 三案对照表里
   两案出局有据。dtype 政策维持 FP64。**顺带一条环境漂移实锤**：本机 `import torch` 实测
   `2.13.0+cu126`（CUDA 构建），与在册钉的 `2.13.0+cpu` 差一个后缀——本班不据此改判、不据此用 torch，
   只登记（03 件 §四 呈批项 ④）。
5. **FP64 实测不打折**（这推掉了在册的一条推演）：CuPy FP64 在真实截面形状 (T=975, S=5217) 上
   `rank(pct) 0.690s→0.010s（65.8x）`、`equal 合成 0.385s→0.003s（144.5x）`、`定尺寸链 0.992s→0.041s（24.1x）`，
   连最小的 hs300（S=300）也有 7.0x。`verification_framework.md §一·补` 说"整卡搬 float64 会把 GPU 打回
   CPU 水平"并自认"系硬件规格推演，本机未做 GPU 实测"——**该前提对内存受限的截面算子不成立**，
   故无需申请放宽 FP64 红线，T2 容差面反而更宽裕。
6. **验收尺本身有假绿风险，已治本**：设备级 `utilization.gpu` 在**零算力负载**下实测 8-57% 摆动
   （桌面图形），而 6 分片大考期间设备均值只有 9.75%、341 枚采样里 **0.00% 达到 70%**。
   拿设备曲线单独当"≥70%"的尺＝分不清"引擎在喂卡"与"IDE 在画窗口"。本班在 `gpu_core` 加
   `nvml_process_util()`（逐进程 SM 归因，三阶段自测：CPU-only 进程不入计算表 / GPU 忙时本进程读数随负载升 /
   空闲回落），并让批内心跳并记归因三键。
7. **真缺陷两支（本班自犯，当班修＋当班留反例钉）**：①`bool(ndarray)` 让 6/8 考格记成 eval 阴性
   （算力面的坑变成判决，方向性错误）；②设备核在 drift_band 交接格提前做了 cap clip（换序=换数）。
   两支各有配对试件，其中一支把"曾炸过的表达式形态"写成 `pytest.raises(ValueError)` 反例钉。

## 一、T0 层 1：阶段耗时归因（今晚全部仪表）

口径：`data/strategy_intake/grid_2026101*/progress.jsonl` 逐行分段计时求和（仪表件=`00_gpufeed_report.md` §四）。
探针=`.runtime/tmp/st-gpux-20261011/profile_t0.py`＋`t0b_attribution.py`（只读，零生产写）。

| 阶段 | 求和秒 | 占比 | 均/格 | p50 | p95 |
|---|---|---|---|---|---|
| eval_s | 16,367.4 | **82.19%** | 0.420 | 0.102 | 1.053 |
| bt_s | 3,205.9 | 16.10% | 0.082 | 0.046 | 0.200 |
| write_s | 226.0 | 1.14% | 0.006 | 0.000 | 0.000 |
| fetch_s | 114.0 | 0.57% | 0.003 | 0.001 | 0.007 |
| 合计 | 19,913.3 | =5.53 CPU-h | — | — | — |

逐批（`n`＝该批 progress 行数）：

| 批 | n | tot | eval | bt | 备注 |
|---|---|---|---|---|---|
| grid_20261010-191646 | 200 | 2.870 | 2.740 | 0.117 | 上一班 T1 标定（改前基线） |
| grid_20261010-194108 | 200 | 1.707 | 1.584 | 0.112 | 上一班 T2-A 治本后 |
| grid_20261010-210008 | 1,000 | 0.540 | 0.475 | 0.060 | W1 考试提前窗 |
| grid_20261010-210933 | 10,080 | 0.092 | 0.058 | 0.026 | 子空间小宇宙 |
| grid_20261010-232435_s0..3of6 | 4×617 | ~0.97 | ~0.87 | ~0.09 | 探索 t1 |
| grid_20261010-233721_s0..5of6 | 6×4,167 | ~0.61 | ~0.49 | ~0.10 | 探索 p2（六路并发） |

宇宙/状态归因（join `manifest.csv` 的 `values_json`+`prefix_key`）：

| 面 | 格数 | eval 秒 | 占比 | 均/格 |
|---|---|---|---|---|
| all_a_ex_st | 9,479 | 11,496.7 | **74.2%** | 1.213 |
| zz500 | 14,560 | 2,465.3 | 15.9% | 0.169 |
| hs300 | 14,463 | 1,526.5 | 9.9% | 0.106 |
| — 其中 all_a 命中格 | 8,960 | 6,936.6 | 44.8% | 0.774 |
| — 其中 all_a 未命中格 | 519 | 4,560.1 | 29.4% | **8.786** |
| 命中路径合计 | 36,834 | 9,356.0 | **60.4%** | 0.254 |
| 未命中路径合计 | 1,668 | 6,132.0 | **39.6%** | 3.677 |

`backend` 字段与尺寸守卫对账：`gpu` 格 24,039=all_a+zz500、`cpu` 格 14,463=hs300，与
`scripts/backtest/translated/_c4_engine.py:532 _GPU_AUTO_MIN_CELLS = 500_000`（hs300 面板 975×300≈0.29M 不过闸）
逐位自洽——**即今天的"GPU"只覆盖 bt 张量面，eval 面一格没上卡**，这就是"CPU 引擎+GPU 点缀"的机制真身。

## 二、T0 层 2：eval 内部函数级占比（合成面板真形状 cProfile，零 CH）

探针=`t0c_eval_internal.py`，直调 `evaluate_recipe`（T=975, S=5217, F=8 因子）。

**命中路径 0.3585s/格 的构成**（cProfile tottime÷20 次）：

| 项 | s/格 | 占比 | 读法 |
|---|---|---|---|
| `numpy.ndarray.copy`（320 次/20 格=16 次/格） | 0.0856 | **24%** | 全面板物化拷贝是头号单项 |
| `pandas …_where_standard` | 0.0371 | 10% | `.where(mask)` |
| `pandas …_take_nd_ndarray` | 0.0222 | 6% | 行 gather（periodic） |
| `is_bool_dtype`（**417,460 次调用/20 格=20,873 次/格**） | 0.0162（cum 0.046） | 4.5%（cum 12.9%） | pandas dtype 派发税 |
| `putmask_without_repeat`（`base[base==0]=np.nan`） | 0.0171 | 4.8% | 逐格 setitem |
| `mul/truediv/rtruediv/le` 标量算子面 | 0.0406 | 11.3% | 逐格算术 |
| `astype` / `_isna_array` / `_get_values` | 0.0422 | 11.8% | 转换与掩码取数 |

结论：**命中路径的大头不是算术而是 pandas 机械**（拷贝+派发），这正是"设备一次成型 vs pandas 逐算子重做"
的形态差——也解释了为什么把同一段数学写成数组链能拿到 20x 以上。

**未命中路径（全格 `evaluate_recipe` 墙钟，秒）**：

| A1＼A2 | equal | ic_mean |
|---|---|---|
| raw | 1.972 | 15.379 |
| zscore | 3.335 | 16.812 |
| rank | 7.290 | 20.702 |
| industry_neutral | 3.198 | 16.387 |
| size_neutral | 6.088 | 19.521 |
| industsize_neutral | 7.621 | 20.284 |

命中路径按 C/D2 维：equal_weight 0.256 / inv_vol 0.316 / mkt_cap 0.314 / signal_strength 0.407 /
kelly_025 0.328；periodic 0.319 / drift_band 0.360。

单次 `algorithms.rank` 在 S=5217 上 = **0.641s**（cProfile 实帧），IC 族每因子要做 2 次秩
（其中 `fwd.rank(axis=1)` 与因子无关却在循环内重算＝在案的 L1 可 hoist 面，本班不动判据口径、只登记）。

## 三、T1 选型：三案对照 + 载体/形状/dtype 实测

载体合规性（四问门 Q4，真源=`new_asset_gpu_cpu_checklist.md §一`）：

| 案 | 本机在装 | 截面原语 FP64 实测 | 合规判定 |
|---|---|---|---|
| **CuPy 14.2.0** | ✓ | 见下表 7-145x | **选定**（checklist §一Q4 明文"载体=CuPy 或 numba.cuda"） |
| PyTorch 2.13.0+cu126 | ✓（与裁定冲突） | rank 0.0027s（更快） | **出局**：`#ARCH-TORCH-CPU-ONLY` 钉 CPU 版，翻转=Owner 门位；本机装了 cu126 属环境漂移，不得当作施工依据 |
| Polars-GPU 1.41.2 | ✓ | 无 API | **出局**：`collect(backend="gpu")` 实测 `TypeError: unexpected keyword argument 'backend'`；cuDF 另判"Windows 原生不可用" |

CuPy FP64 单价（T=975，探针 `eval_ops_axis1.py`，轴=axis=1 逐日截面，与被测代码同轴）：

| 原语 | 宇宙 | CPU(pandas/numpy) | GPU FP64 | 加速 |
|---|---|---|---|---|
| `rank(axis=1, pct=True)` | all_a 5217 | 0.6905 | 0.0105 | **65.8x** |
| `rank(axis=1)` 平均档 | all_a | 0.7469 | 0.0260 | 28.7x |
| 行 mean+std | all_a | 0.1592 | 0.0015 | 108x |
| `concat+groupby.mean`（F=8 合成） | all_a | 0.3848 | 0.0027 | **144.5x** |
| 定尺寸链（秩+掩码+归一+gather+clip） | all_a | 0.9918 | 0.0411 | 24.1x |
| 同上三原语 | zz500 1037 | 0.096/0.089/0.025/0.088/0.146 | 0.0025/0.0025/0.0001/0.0015/0.0070 | 38-180x |
| 同上三原语 | hs300 300 | 0.021/0.021/0.007/0.021/0.045 | 0.0021/0.0018/0.0002/0.0012/0.0064 | **7.0-31.3x** |
| H2D 975×5217 FP64（40.7MB） | — | — | 9.37ms | D2H 18.86ms |

**dtype 判定=FP64 全程，不上调任何容差**。依据：内存受限的截面原语 FP64 仍有 7-145x；
`§一·补` 担心的 1/64 只在 FLOP 密集面兑现（torch 侧对照：`svd(250×5000)` f64 0.136s vs f32 0.0155s，差 8.8x；
该组数字只作"1/64 是否兑现"的证据，不作载体选型证据，因 torch 非合规载体），而本班的 eval 面
**没有 FLOP 密集核**（lasso/pc1 明确留 CPU，见 §五交接点）。

**反向证据（GPU 不是万灵）**：把 `drift_band` 那种"逐日 python 循环 + 每步小张量"直接搬上卡，
实测 **0.2138s vs CPU 0.0158s＝慢 14 倍**，而同样的活融合成一次 kernel 是 0.0002s（kernel-launch 税 990x）。
这与 `p1_wiring_benchmark.md §二/§四` 在 bt 面量到的"hs300/zz500 GPU 反输 4-7x（串行闸循环 launch 税）"
是同一根因的第二次独立复现。**凡串行依赖面，先融合后上卡，否则禁上卡。**

## 四、验收尺（GPU 利用率）自身的取证与治本

| 读数 | 值 | 出处 |
|---|---|---|
| 大考期间设备级 util（6 分片心跳 341 枚，nvidia-smi 设备口径） | **均值 9.75%**，p95 19.0%，max 32%，**≥70% 者 0.00%** | `grid_20261010-*/heartbeat.jsonl` |
| 独立 10 分钟采样器 | 均值 17.58%，max 56%，≥70% 者 0.00%，**23:29 断流**（早于 p2 点火 23:37） | `.runtime/nightmine/gpu_util_long.log`（97 档，07:29→23:29） |
| **零算力负载下设备 util（桌面图形噪声底）** | 12 点采样 **8%→57%** 摆动，`nvidia-smi` 进程表内**全是 C+G 桌面进程、零 compute 进程** | 本班 03:26 实测 |

⇒ 设备曲线可被桌面图形推到数十个百分点，**单独作尺不可归因**。本班治本=逐进程 NVML 归因
（`gpu_core.nvml_process_util()`，ctypes 直调 `nvml.dll`，不新增依赖）；三阶段自测证明它能红：
CPU-only 子进程**不出现在计算进程表**、本进程 GPU 忙时读数随负载上升、停算后回落。
批内心跳并记 `gpu_self_sm_pct / gpu_self_in_compute / gpu_compute_pids_n` 三键（NVML 不可用时整键不出，
禁把"读不到"写成"没占用"）。

## 五、施工范围与 CPU 交接点（写死，越界即回原路并出声）

上卡面：A1 六模式全谱（raw/zscore/rank/industry_neutral/size_neutral/industsize_neutral，锚缺失时
与 factory 同降级 zscore+degraded）、A2 的 equal/orth_equal/ic_mean/ic_ir/halflife20/halflife60、
B+C 定尺寸七形态、periodic 调仓沿用、cap 硬 clip。
**留 CPU 面（=判据敏感或无收益，逐条给因）**：

| # | 面 | 位置 | 为何留 |
|---|---|---|---|
| 1 | drift_band 逐日 prev 串行 | `_apply_freq_trigger` | §三 实测慢 14 倍；融合是独立工程件 |
| 2 | lambda>0 的 ewm(alpha) 时间轴递推 | `_apply_cap_and_lambda` | 同族 IIR，未融合前禁上卡 |
| 3 | sklearn Lasso 滚动重训 | `_combine` lasso 支 | `selection="random"` 的确定性系 CPU 实现属性 |
| 4 | pc1 的 `np.linalg.eigh` | `_combine` pc1 支 | 特征序/符号约定另判 |
| 5 | IC 权重 rolling(60)/ewm/归一 | `_ic_weight_frame` | 对象是 (T,F)（F≤8）小矩阵，上卡无收益且造第二实现面——故 CPU/GPU 两条前缀路**共用同一函数**（本班把该段从 `_combine` 原位抽出，逐式同序） |
| 6 | 一切索引/列标签/reindex 语义 | 全程 | `gpu_core` 文件头 INVARIANTS 既有条款；面板进核前已 reindex 到考窗行 |
| 7 | X_sector / J_regime / X_stop / X_breaker 叠加族 | `evaluate_recipe` | `_cell_device_able` 判否=整格回原路 |

开关与漂移面控制：`--eval-backend cpu|gpu|auto`，**缺省 cpu=原 pandas 路逐字节零漂移**；
`summary.json` 的 `eval_gpu` 键仅在后端非 cpu 时出现（观测面，不进判据）；设备面任何异常
一律 `_instr_warn` 出声并降级 CPU，**绝不让算力面的坑变成阴性格**（§〇.7 的教训）。

> **本句已被 05:36 六路实测部分证伪并就地补修**（2026-10-11，详见 §六 D-F）：设备分支自己的
> 异常确实零阴性，但**上卡带来的主机侧资源足迹**（cupy 上下文 + 面板暂存）把 64GB RAM 顶到零后，
> MemoryError 落在本文件既有的 CPU 段记账口（`factory_grid_executor.py:2319` 那支 `except`），
> 于是 22 格被记成 `eval_fail:MemoryError` 阴性。"降级不杀格"只覆盖抛点一侧是不够的——
> 补齐=准入闸加主机腿（§六 D-F 修因①）+ eval 调用外套一次卸资源后重试（修因②）。

## 六、在册矛盾与缺陷登记（不自决，逐条给凭据）

| # | 类型 | 事实 | 处置 |
|---|---|---|---|
| D-A | **在册政策自相矛盾** | `new_asset_gpu_cpu_checklist.md §二.2`（Owner 令 2026-09-28）"FP64 红线绝对，禁 float32/TF32/FP16" vs `verification_framework.md §一·补`"GPU 重写必须走 FP32＋容差，FP64 仅争议格仲裁" | 本班按 FP64 施工（§三 实测支持），矛盾**不自裁**，提请两件的属主车道对齐或走裁定通道 |
| D-B | 文档↔代码漂移 | `p1_wiring_benchmark.md §四` 写 `_GPU_AUTO_MIN_CELLS=8e6`，代码=500_000（`_c4_engine.py:532`），且 `test_l2_gpu_landing.py` 的 INVARIANTS 已钉 5e5 | 代码与试件一致、战役文档陈旧——只登记，不改他人文档 |
| D-C | 悬空引用三处（同一件 `gpu_core.py`） | `[TESTS]` 指 `tests/backtest/test_gpu_core_parity.py`（真身=`tests/research/backtest/`）；`[CONSUMERS]` 指 `scripts/backtest/l2_bench_probe.py`（`git ls-files` 零命中=不存在）；docstring 验收出处指 `docs/_working/fullscore_night/06_gpu_compute/`（该子目录不存在，其父目录只有 02/03/10） | **定性已修正**（原写"盲区待查"，查出在案出处后改判）：后两处是 `c4c7960bb8d`（st-fullscore-20260930）commit message 明写的 defer 项——"l2_bench_probe.py+04_L2_landing_benchmark.md+deferred_claims.md 随 capability 册批跟车（staging 暂存，册被 datasop/w3h 在途）"，即**已知待跟车件未随册落地**，非无人知晓；`[TESTS]` 的目录名错则是本件自身笔误。本班只登记不改他人头部 |
| D-D | 资源互让面空转 | `config/search_space_prereg.yaml:106 vram.concurrency: 1`（注"单卡禁共存，与本地 LLM 21.6GB 硬顶互斥：exclusive_group=gpu_default"）而 `config/resource_profile_registry.yaml:1039-1046 manual_factory_grid_executor` 的 `exclusive_group: []`；今晚实跑 6 路并发＝靠临时看门狗让路（`yield_watchdog.py`，已随分片退役） | **处置已改判**（总统统筹 2026-10-11 05:3x 裁定③直接授权册面改：并发数按 NVML 实测入册＋executor 挂 exclusive_group，禁"册上写 1 实际跑 6"的漂移态继续）：本班已随袋把 vram 块补 `per_path_budget_mib: 2100`/`concurrency: 6`/`concurrency_basis`，executor 挂 `exclusive_group: [gpu_default]`，并在 `factory_grid_executor._dev_xp` 把预算变成**真准入闸**（只改 yaml 不接消费方＝又一个空转面） |
| D-E | 预存红 6 支（非本班） | `tests/research/backtest/test_l2_gpu_landing.py::test_executor_*` 6 支红，根因=`7961b3ec880`（2026-10-06）给执行器加了 `_load_mkt_cap_wide(...).reindex(...)` 而该试件的桩返回 None | 双证为预存：在**纯净 dev 字节**复跑同 6 支同样红（09 时点记录见本班终报），且本班两支改动对 dev 均纯新增。归执行器属主车道，不代修。6 支点名（06:0x 复跑逐支实录，便于按名对账）：`test_executor_engine_passthrough[cpu-cpu]`／`[gpu-gpu]`／`[auto-None]`、`test_executor_manifest_backend_degrade_columns`、`test_executor_gpu_wave_failclosed_rerun`、`test_executor_cpu_wave_negative_semantics` |
| D-F | **本班自犯缺陷（资源足迹顶零 RAM，判据面被污染）** | 05:36 六路×25,000 格上卡实测：s1/s2/s3/s5 四路跑完 4,167 格各负 8–12 支，其中 **22 支是 `eval/eval_fail:MemoryError`**（detail 实写 "Unable to allocate 37.4 MiB for an array with shape (970,5058) and data type float64" 等），s0/s4 两路更在 1,768/1,794 格处整波 MemoryError→按既定 fail-closed 整波重跑 CPU；同参纯 CPU 基线 p2（`grid_20261010-233721_s*of6`，25,000 格）eval 层阴性 **0 支**，其 39 支阴性全为 `backtest/backtest_fail:RuntimeError`（净值不足的真判决）。主机侧读数：单路 heartbeat.rss_mb 峰值 4,316–4,424MiB，六路合计≈26.4GB，05:52 实测 GlobalMemoryStatusEx 可用仅 23.7GB（总 63.9GB，另有夜矿/LLM/桌面在飞） | 定性=**算力面缺陷变成判决**（与本班 §〇.7 的 `bool(codes)` 案同族，只是抛点换到了未保护的 CPU 段）。两条腿都已补：①`_dev_xp` 准入闸加**主机腿**（册 `budget_caps.host_mem.per_path_peak_mib: 4600`，可用 RAM 不足即本路不上卡并计 `host_mem_refused`；水位读不到只计 `host_mem_unmeasured` 不拦路；读数口=在册唯一 `host_resource_governor.probe_system_watermark`，禁自造 ctypes/psutil 第二份探测）；②eval 调用外套 `_eval_cell_mem_retry`=首次 MemoryError 先卸设备面板缓存+置本批停卡旗+计 `memory_pressure`，**重试一次**，二次仍败照旧上抛既有记账口（真耗尽不禁静默）。配试件 2 支（`test_host_mem_admission_gate_refuses_and_agrees_with_registry` 四面钉＋`test_eval_memory_pressure_degrades_to_cpu_not_cell_death` 三面钉）。**残余不自掩**：只有 05:36 那一轮的 22 支已被记成阴性，历史产物不回填（only-add），改后需下一轮配对复跑证实 eval 阴性回落到基线同形（0 支）才算闭环 |
| D-G | **本班自犯计量盲区**（零计数被读成"跑过但没上卡"） | 06:32 一轮 `--eval-backend gpu` 的产物里 `summary.eval_gpu` 十项全零、`engine_degrade` 缺席，看着像"整批走 CPU 是准入闸决定的"；实为该子进程 **PYTHONPATH 未指车道 ⇒ `zephyr` 解析到主区旧字节**（在册同类教训：worktree 裸 python 导主区包=假绿），`from zephyr.backtest.gpu_core import nvml_device_memory` 抛 ImportError 被 `_dev_xp` 末尾宽 `except` 吞成降级，**只在 stderr 留一行**（`l3_gpu.log` 里 1,050 行同款）。发现路径=**旁证异常**（"GPU"侧 eval_s 0.445 与 CPU 侧 0.452 逐位同速），不是计量面 | 已随袋补：`_dev_xp` 两条静默出口各加计数器（`resolve_not_gpu` / `dev_attempt_failed`）+ 试件 `test_device_attempt_failure_is_never_silent_in_counters`（四相钉，计数器漏加即红）；纪律面新增硬规则自约束=**跑前先在同命令行断言 `zephyr.__file__` 落在车道**（本班 driver 已加，且今后任何"配对"必须先证明两侧的 `eval_gpu.cell_gpu>0` 与 argv 一致才允许进容差判定）。该轮产物**降级为 CPU-vs-CPU 对照**使用（见 02 件 级 3 与 03 件 §八），不得当 GPU 证据 |

 05:36 六路×25,000 格上卡实测：s1/s2/s3/s5 四路跑完 4,167 格各负 8–12 支，其中 **22 支是 `eval/eval_fail:MemoryError`**（detail 实写 "Unable to allocate 37.4 MiB for an array with shape (970,5058) and data type float64" 等），s0/s4 两路更在 1,768/1,794 格处整波 MemoryError→按既定 fail-closed 整波重跑 CPU；同参纯 CPU 基线 p2（`grid_20261010-233721_s*of6`，25,000 格）eval 层阴性 **0 支**，其 39 支阴性全为 `backtest/backtest_fail:RuntimeError`（净值不足的真判决）。主机侧读数：单路 heartbeat.rss_mb 峰值 4,316–4,424MiB，六路合计≈26.4GB，05:52 实测 GlobalMemoryStatusEx 可用仅 23.7GB（总 63.9GB，另有夜矿/LLM/桌面在飞） | 定性=**算力面缺陷变成判决**（与本班 §〇.7 的 `bool(codes)` 案同族，只是抛点换到了未保护的 CPU 段）。两条腿都已补：①`_dev_xp` 准入闸加**主机腿**（册 `budget_caps.host_mem.per_path_peak_mib: 4600`，可用 RAM 不足即本路不上卡并计 `host_mem_refused`；水位读不到只计 `host_mem_unmeasured` 不拦路；读数口=在册唯一 `host_resource_governor.probe_system_watermark`，禁自造 ctypes/psutil 第二份探测）；②eval 调用外套 `_eval_cell_mem_retry`=首次 MemoryError 先卸设备面板缓存+置本批停卡旗+计 `memory_pressure`，**重试一次**，二次仍败照旧上抛既有记账口（真耗尽不禁静默）。配试件 2 支（`test_host_mem_admission_gate_refuses_and_agrees_with_registry` 四面钉＋`test_eval_memory_pressure_degrades_to_cpu_not_cell_death` 三面钉）。**残余不自掩**：只有 05:36 那一轮的 22 支已被记成阴性，历史产物不回填（only-add），改后需下一轮配对复跑证实 eval 阴性回落到基线同形（0 支）才算闭环 |


## 七、复核命令（进程外可跑）

```bash
# T0 层1（阶段求和 + 心跳归因 + 采样器噪声）
python .runtime/tmp/st-gpux-20261011/profile_t0.py
python .runtime/tmp/st-gpux-20261011/t0b_attribution.py     # 宇宙/命中面 join
# T0 层2（eval 内函数级占比，合成面板零 CH）
python .runtime/tmp/st-gpux-20261011/t0c_eval_internal.py
# T1 单价（CuPy FP64 三宇宙 + 循环税 + H2D/D2H）与 NVML 归因自测
python .runtime/tmp/st-gpux-20261011/eval_ops_axis1.py
python .runtime/tmp/st-gpux-20261011/meter_validate.py
# 噪声底（判"设备 util 能否单独作尺"）
for i in $(seq 1 12); do nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader; sleep 2; done
# 试件（车道内跑，PYTHONPATH 必指车道 src，否则假绿）
PYTHONPATH=D:/ZephyrAlpha/.worktrees/st-gpux-20261011/src python -m pytest \
  tests/research/backtest/test_l2_gpu_landing.py tests/research/backtest/test_gpu_core_parity.py \
  tests/research/backtest/test_c4_engine_gpu_wiring.py -q
```
