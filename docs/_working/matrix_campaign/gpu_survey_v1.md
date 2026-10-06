---
campaign: matrix-20261006
lane: gpu-survey
status: draft（施工道按排行开工中）
ttl: task_bound
created: 2026-10-06
---

# gpu_survey_v1 — GPU 化可行性矩阵（调查道，2026-10-06）

> 口径：A=现成 cupy 模式可套（纯数值矩阵）｜B=可化但需算法改造（逐日/逐标的循环→面板分块向量）｜C=不值得（IO/分支/Decimal 精确性/顺序状态机）。工作量 S=小时/M=天/L=周+数值验证工程。
> 底座证据：`src/zephyr/backtest/gpu_core.py`（resolve_backend/ZEPHYR_COMPUTE_BACKEND/tensor_core/eval_prefix_equal_gpu/RawKernel fillability_gate_scan/fail-closed 降级台账）；`scripts/backtest/translated/_c4_engine.py`（P1 接线，0.53s/格）；`scripts/backtest/factory_grid_executor.py`（L2-C --engine 三态+manifest backend/degrade 列）。
> 继承并复判 `docs/_working/archive/2026-10/gpu_rewrite/hotspot_census.md` §七 F1–F13 族清单（实测件，本册不重挖其已封矿面）。

## 一、可行性矩阵总表

| # | 模块 | 现状态 | GPU化 | 工作量 | 风险面（对拍要求） | 热度证据 | 建议 |
|---|---|---|---|---|---|---|---|
| 1 | gpu_core + _c4_engine + factory_grid_executor | **已接 GPU** | 已接 | — | 逐位 parity 钉住 | 工厂网格考 T1/T2 主考场 | 唯一核，不再另起（L2-E 归一定案） |
| 2 | scripts/backtest/t0_material_line.py（run_model_m0 双重 for） | CPU 逐路径双循环 | **A-**（路径并行） | M-L | 路径级逐位对拍+语料双跑 | 普查 F4 实测 ≈23.3h CPU/语料 282 万对/周期 | 价值最大单点；立项后开，先 CPU numba 后 GPU |
| 3 | src/zephyr/data/implementations/internal_compute_provider.py + factor/technical_indicators/*（8 文件 6377 行） | CPU 单标的 Series 流水线，产 c1_market.technical_indicator **4.03 亿行** | **B**（面板批算；递推→RawKernel） | M-L | 1e-9 全列对拍（影子表双跑） | 夜跑 02:30 计划任务 tilib_dwm_shard_runner；指标册 143 列全量考 | 先探针分 CH IO vs 计算占比，再定 GPU 深度；CPU 面板化先吃大头 |
| 4 | backtest/core/walk_forward.py（whites_reality_check 1000 循环） | CPU 串行 bootstrap | **A** | S | 统计面 1e-9；同索引矩阵注入法对拍 | WFA 考试链 f06_e4_wfa_exam 每 fold 消费 | 今晚可开：纯函数核零接线 |
| 5 | regime_validation/e2_stationary_bootstrap.py（2000×） | CPU 串行 bootstrap | **A** | S | 同 #4 | regime 验证 C4 判定 | 与 #4 合并施工 |
| 6 | factor/analysis/correlation_block_bootstrap.py（2000×） | CPU numpy | **A** | S-M | 1e-9；PPW 块长留 CPU | pf_core/strategy_correlation_pipeline（上线门禁 G07） | 与 #4/#5 同族合并 |
| 7 | factor/wq_alpha_87.py（87 公式，MATURITY=design 未接线） | pandas 逐公式 | **A-B** | S-M | 1e-12（eval_prefix_equal_gpu 纪律） | 接线待装配批；接线后=因子批考批量面 | 先写核待接线 |
| 8 | factor/analysis/layered_backtest.py（逐日 qcut） | CPU 逐日循环 | **B** | S | 分箱边界逐位 | layered 验证管线族 | 小件顺手做 |
| 9 | factor/analysis/ic_ir_calc.py | 编排+面板 IC | **B** | M | 1e-9 | 暂无 import 消费方（AI-08）——低热 | 随 #7 接线一起，单独做空转 |
| 10 | backtest/implementations/vectorized_engine.py（逐日+Decimal 撮合） | production，Decimal 精确账本 | 拆开判：信号/市值重估 **B**；撮合+现金账本 **C（GPU 天敌）** | L | 交易引擎=双跑并行期+Owner 呈批换尺 | 普查 F8"口径真源禁动（IBT-D01 未收口）" | 全件禁动；未来只立 float64 镜像对拍通道呈批件 |
| 11 | cpcv/purged_kfold/strategy_cpcv_matrix | 小矩阵 | **C** | — | — | 预留 | 规模翻万倍再评 |
| 12 | metrics/cost_attribution | 秒级 | **C** | — | — | 每 run | 不做 |
| 13 | event_driven_engine/tick_replay 族 | 事件驱动 | **C** | — | — | — | 不做 |
| 14 | factor_production_pipeline/factor_factory | 编排件 | **C**（GPU 接点在 #3/#7 内部） | — | — | 盘前调度待接线 | 不动本体 |
| 15 | multifactor_pit_backtest | 注入式骨架+5 层 PIT 断言 | **C**（框架）；注入内部=B | — | — | 多因子 sleeve | 不动框架 |
| 16 | pf_core portfolio_optimizer 等 | 持仓小矩阵 | **C** | — | — | 盘中链 | 不做 |
| 17 | pf_alloc/core 12 件 | 小矩阵；BMA 有 bootstrap 面 | **C 为主**；BMA **B(轻)** | S | 1e-9 | allocator 影子考 | 仅 BMA 可选 |
| 18 | signal_ashare/* | 分支密集 | **C**；calibrator 可 pandas 化（非 GPU） | S(非GPU) | — | 盘中 3s 实时面 | 不做 GPU |
| 19 | kronos_adapter.py | **已 GPU**（夜窗 7-8GB 互斥窗） | 已接 | — | — | 夜窗批推理 | 共享 data_eng/gpu_resource_manager 配额 |
| 20 | ml_train/* | torch **CPU 钉死**（#ARCH-TORCH-CPU-ONLY Owner 裁定） | **C(禁)**＝Owner 门位翻转项 | L | 呈批 | 0 个 import torch 实证 | 只登记门位，禁动 |
| 21 | data/*（backfiller/scheduler/IO） | 分片+网络 IO | **C（GPU 无益）** | — | — | 全夜跑链 | 不做 |
| 22 | consensus_daily_compute/financial_derived_compute | pandas 三表/TTM 批 | **B(轻)** | S-M | 1e-9 | incremental 夜更 | 排后；先探针 |
| 23 | mcts_expression_search/lane_c_formula_miner | 搜索分支 | **C** | — | — | 挖矿车道 | 不做 |

**判定计数**：A=5（#2/#4/#5/#6/#7）｜B=6（#3/#8/#9/#10 信号面/#17-BMA/#22）｜C=12。

## 二、"已接 GPU 模式"复用指南

1. 后端开关走 gpu_core.resolve_backend（显式>env>auto；fail-closed 降级出声禁静默）。
2. 单一代码路径：xp = cupy/numpy 切换，语义一分叉即违宪。
3. FP64 红线：入口 _as_f64 收口禁 float32/TF32；索引/reindex 留 CPU pandas，核只吃对齐 (T,S)。
4. 串行依赖不拆：照抄 RawKernel"一 thread 一列、时间轴寄存器内推进"。
5. 归约精度：_neumaier_nansum_axis1/_zscore_rows（parity≤1e-12）；rank 用 _rank_desc_average。
6. 验收三件：parity 逐位钉 CPU 锚；l2_bench_probe 式提速探针（<1.5x 停手如实报）；资源登记接 data_eng/gpu_resource_manager（human_gated）。
7. 禁区：判定面（三门/DSR/单调性/PIT 断言）永不入核。

## 三、施工排行 Top5

| 排名 | 件 | 验收判据 |
|---|---|---|
| 1 | **bootstrap 统一族 GPU 核**（#4+#5+#6 合并 xp 纯函数核，不改原 API） | 同索引矩阵注入对拍 ≤1e-9；2000×T=1600 基准 CPU 秒级→GPU 目标 <0.5s |
| 2 | **dwm 技术指标链面板化**（去 iterrows+面板批算+递推 RawKernel） | 影子表全 143 列逐位/1e-9 双跑；探针先分 CH IO/计算/行物化占比 |
| 3 | **wq_alpha_87 表达式层**（五算子 xp 原型，87 公式迁移留接线） | 与 pandas 逐位/≤1e-12；前缀不变性测试继承 |
| 4 | **layered spread 批算** | spread 序列逐位（qcut rank method="first" 语义）；1622 日×5646 列基准 |
| 5 | **t0_material_line 路径并行**（numba CUDA→RawKernel） | 逐路径 fills/成本逐位；23.3h→<2h；材料门全绿 |

今晚即可开：#1（H 道）、#3+#4+#2探针（I 道）。#2 验收依赖夜窗影子表；#5 立项批后开。

## 四、盲点自查（12 条）

> **【I 道探针修正 2026-10-06】**：#2 的三段占比已实测（3 标的×全窗 25,160 行×142 指标）：**CH 读取 4.2% / 指标计算 38.3% / 行物化 57.5%**（_build_row 逐格 Python 52.9%+iterrows 4.6%）——非 IO 主导、是行物化主导。#2 打法改写：**第一收益点=_build_row 向量化（~53%，无需 GPU）**，GPU 深度降级为"表达式算子层"档。另：layered spread 核已出（逐位+6.7x，7.26s→1.08s，Kahan 补偿和是逐位关键）；wq87 五算子 14/14 ≤1e-12（CPU 提速诚实值 rolling 4.6x/corr 1.7x/rank 1.1x/shift 0.6x）。盲点 5 已闭环。

1. 无本机 profiler 复测——耗时证据继承 archive hotspot_census，实跑可能漂移。
2. cupy 本机可用性未验证（纪律禁触发 import）；09-25 普查"未装"vs 09-30 L2 落地，状态未复核。
3. 3826 py 未全集扫描：ml_train/alt_data/nlp 大域只抽查。
4. 热度=静态证据，无 runtime 频次日志。
5. #2 假设计算主导，CH 读写占比未实测——IO 主导则 GPU 收益缩水（探针前置）。
6. #7/#9 无 import 消费方，GPU 先行=产能等接线，装配批不落地即空转。
7. Decimal 撮合"不可 GPU"是形态判断；float64 镜像双轨方案未展开（Owner 呈批级，只登记）。
8. bootstrap 对拍受 RNG 约束：索引注入法本身未试跑验证。
9. CPCV 判 C 锚在当前规模；万策略×千折需重评。
10. 指标册 143 列考试读表不计算——算力面在 CH 侧回填链，勿误记热度。
11. eval_prefix_equal_gpu 只覆盖 equal 合成；IC 加权/正交/lasso 长尾合成留 CPU（未盘新面）。
12. 本道只读：本册由总包落盘，token 随收割批登记。
