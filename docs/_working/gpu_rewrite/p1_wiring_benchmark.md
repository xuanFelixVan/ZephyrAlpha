---
ttl: task_bound
title: P1+L1 接线基准（gpu_core 快路径接线 + L1 hoist 实测——cpu/gpu/hoisted-cpu 逐格秒）
created: "2026-09-29"
sid: st-gpup1-20260929
family_id: GPU-REWRITE
lane: LANE-GPU-P1
supersedes: ""
evidence_grade: A（全部数字为本机 RTX 3090 实测；被测件=本批接线后引擎，探针=.runtime/tmp/st-gpup1-20260929/bench_p1.py）
---

# P1+L1 接线基准（st-gpup1-20260929）

## 〇、一句话结论

L1 hoist（批级 closes/rets 预热 + 成本门单趟三产物）实测 **1.78–2.39x**；GPU 快路径仅在
all_a 级面板（S=5217）反超（1.51x），hs300/zz500 尺寸受串行闸循环 kernel-launch 税拖累
反输 4–7x——故 auto 档加尺寸守卫（`_GPU_AUTO_MIN_CELLS=8e6`，实测赢面区下沿），
显式 `backend="gpu"` 无视守卫。CPU 逐位红线零触碰。

## 一、被测件与口径

- 引擎（本批接线后）：`scripts/backtest/translated/_c4_engine.py`（backend/pre_tensor
  透传 + `run_backtest_full_with_tiers` 单趟三产物）+ `scripts/backtest/factory_grid_executor.py`
  （批级 pre_tensor 共享 + 成本门场景单趟）；GPU 核=`src/zephyr/backtest/gpu_core.py`
  （P0 件，parity 11/11 绿真机）。
- 口径：`run_backtest_full`（或 tiers 场景对应入口）纯回测 pass 秒/格，**不含**
  evaluate_recipe/数据装载；N=6 格点均值；T=1622（与普查 T1 同窗）；合成面板
  （seed=20260929+S，leading/interior NaN+2% 合成封板掩码）； cupy 14.2.0 /
  CUDA 12.9 / RTX 3090 24GB / pandas 2.x / numpy 2.x / Python 3.12.8。
- 基线对照：T0 口径 35.33s/格 为「旧掩码逐行重建+eval+2 pass」全格点旧世界数字；
  本表为 st-ddup-20260925 去重改造后（掩码 LRU+向量化已落地）的单 pass 热路径口径，
  两者不可直接相除（hotspot_census.md §四·更正2 同因）。

## 二、实测结果（秒/格，6 格均值）

| 面板（T×S） | cpu（原路径） | hoisted-cpu（L1） | gpu | hoisted 加速 | gpu 加速 | tiers 两趟→单趟 |
|---|---|---|---|---|---|---|
| 1622×504（hs300 级） | 0.109 | 0.061 | 0.427 | **1.78x** | 0.25x（反输） | 0.114→0.059（**1.95x**） |
| 1622×1037（zz500 级） | 0.218 | 0.103 | 0.413 | **2.12x** | 0.53x（反输） | 0.274→0.115（**2.39x**） |
| 1622×5217（all_a 级） | 1.402 | 0.606 | 0.930 | **2.31x** | **1.51x** | 1.227→0.607（**2.02x**） |

GPU 单趟三产物（`run_backtest_full_with_tiers(backend="gpu")`）：hs300 0.355 /
zz500 0.437 / all_a 0.918 秒/格。

## 三、正确性证据

- **CPU 逐位**：新引擎 vs dev HEAD 原引擎（bitexact_proof.py 双模块同输入对拍）——
  `run_backtest_full` / hoisted / `daily_net_returns` / tiers 单趟三产物 / gate off /
  `run_backtest` 旧位置调用形 / px 多列 reindex / 索引错位回退，**8 面 3 格点全
  array_equal+stats 全等，PASS**；非法 backend=ValueError。
- **GPU parity**：vs CPU max rel diff = 8.1e-14（hs300）/ 2.5e-13（zz500）/
  6.1e-15（all_a），全 ≤1e-12 红线（FP64 全程）。
- **tiers 单趟三产物 vs 两连调**：五档 net 逐位 array_equal（hs300/zz500/all_a 全真）。
- **回归**：test_c4_batch_smoke + test_factory_grid_executor + test_exam_cost_gate +
  test_c4_limit_gate + test_c4_deflated_sharpe_runner + test_c4_auto_oos = **103 passed**
  （改前基线同集 0 fail；factory_guard 桩随 9 元组签名同步）。

## 四、auto 尺寸守卫（本批设计判定）

| 区 | 判定 | 依据 |
|---|---|---|
| T×S < 8e6（hs300/zz500 级） | auto→cpu-hoisted（最快路） | gpu 0.25–0.53x 反输：串行闸循环 1622 次 kernel-launch 税为主 |
| T×S ≥ 8e6（all_a 级） | auto→gpu | 实测 1.51x 赢面区 |
| 显式 backend="gpu" | 无视守卫恒走张量核 | 调用方自担（对照通道/大面板批跑） |
| 显式 backend="cpu" | 恒原 pandas 路径 | 零漂移红线 |

## 五、余量与下一步（供 L2 决策，本批不做）

1. GPU 侧最大税=串行闸循环（`_apply_gate_serial`，T 次小 kernel）——若 L2 将其
   GPU 融合或分段批处理，hs300/zz500 尺寸 GPU 有反超空间（普查 L2-a 判定仍成立：
   改动风险 vs 收益需另测）。
2. hoisted-cpu 剩余面=ffill/pct_change 之外的逐格张量（shift/mul/sum/abs）+掩码
   to_numpy 转换（SU/SD 逐格重复转换，约 1–3ms/格量级）。
3. 35.33s/格 旧世界基线的治本主力=已落地的掩码去重（74–95%）+本批 L1（残余 2x）
   ——全批次墙钟收益以 T1 重跑实测为准（本件 task_bound 不含批级跑批）。
