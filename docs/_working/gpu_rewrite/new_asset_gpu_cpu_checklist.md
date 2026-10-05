---
ttl: task_bound
title: GPU/CPU 新建计算资产判定清单（Owner 令：任何 AI 建计算件前必跑的四问门）
created: "2026-09-28"
sid: st-gpu-conv-20260928
lane: LANE-GPU
family_id: GPU-REWRITE
evidence_grade: B（判定流程=Owner 指令落地；锚点数据=A 级实测，出处见 §四；P0 先例=已落地过闸代码）
---

# GPU/CPU 新建计算资产判定清单（建前必跑）

> Owner 指令（2026-09-28）：**此后任何 AI 在本仓新建计算类资产（脚本/模块/内核）之前，必须先跑本清单并把四问答案写进该资产的头注/PR 描述**。未过本清单的新建计算件，评审即打回。
> 本件是流程卡，不是教程；实测依据见 §四，P0 落地先例见 §五。

## 一、四问判定（全答完才许动手）

| # | 问题 | 判据与取证方式 | 不满足时 |
|---|------|--------------|---------|
| Q1 | **热路径占比 >10%？** | 先 profile 后动手（cProfile/分段计时均可，禁"感觉慢"）。占比=该计算占其宿主工作负载墙钟的比例。仓内实测真源=`docs/_working/gpu_rewrite/hotspot_census.md`（掩码面 74-78%、张量面 2.8-3.6%、五档扫描口径 68.9%） | 占比 <10% = **禁新建 GPU 件**（先做 hoisting/去重/缓存——L1 先例：纯代码整理 8.6x，零新依赖） |
| Q2 | **规则形状数组？** | 输入可写成 (T,S)/(B,T,S) 等稠密规则阵列；无键值查找、无变长分支、无串行状态链（若主体是逐行 dict/iat 行物化，先向量化——那是 CPU 活，census §二 L1-a/b） | 不规则/行物化为主 = CPU（先向量化） |
| Q3 | **可批量化？** | 存在独立批（多格/多策略/多 fold）共享同一数据面板；批并行几何成立（census §三：面板+掩码常驻仅 50MB，批波显存预算按稠密算——权重稀疏假设已被 47.9% 非零实测推翻） | 单发串行 = CPU |
| Q4 | **依赖库 GPU 版存在且 Windows 原生可用？** | cuDF **不可用**（不支持原生 Windows，实测判否）；载体=CuPy（`pip install cupy-cuda12x`，本机 3090/驱动 610.88）或 numba.cuda。torch 在本仓钉 CPU 版（requirements.txt:5-10，ARCH-TORCH-CPU-ONLY，翻转=Owner 门位） | 无合规载体 = CPU（登记到 P1/P2 候选清单） |

**判定规则**：Q1-Q4 全真 → **GPU 候选**（进入 §二验收判据）；任一为否 → **CPU**（把不满足项写进资产头注，防止后人重问重挖）。

## 二、验收判据（GPU 件过闸门槛，缺一不收）

1. **parity test 必备**：CPU 路径与既有引擎/真源函数**逐位一致**（`np.array_equal`）；GPU 路径对 CPU **相对差 ≤1e-12**（先例：`tests/backtest/test_gpu_core_parity.py`）。
2. **FP64 红线绝对**：scoring 路径全程 float64，禁 float32/TF32/FP16（3090 FP64=1/64 吞吐是买确定性，不是买速度）。
3. **CPU fallback 永久保留**：`import guard` + 后端开关（先例 env=`ZEPHYR_COMPUTE_BACKEND=gpu|cpu|auto`，缺省 auto）；GPU 失败=fail-closed 降级 CPU **并出声**（degrade 台账/logger，禁静默降级、禁半成品混入）。
4. **语义零漂移**：判定面（成本三门/DSR/单调性/门禁）永不随算力迁移；公共 API 只加不改；manifest/产物 schema 逐位不变。
5. **索引/IO 留 CPU**：CH 读取、reindex 对齐、行物化不上 GPU（census §三：批级数据面 68s=0.07%，无收益）。

## 三、登记义务（与 §二同批）

- 新 .py：14 字段头注 + `add_module_translation.py` 大白话简介 + creation token（tests/ 豁免 token）。
- 新依赖（如 CuPy 进 requirements.txt）= 依赖变更，按门位表报批（rewrite_architecture_three_tiers.md §二）。
- 施工前 `apply_depgraph.py --add-design-node` 登记（宪法 RULE-DEPGRAPH）。

## 四、本仓实测锚点（引用勿背数，更新以真源为准）

| 锚点 | 值 | 真源 |
|------|-----|------|
| GPU | RTX 3090 24GB（driver 610.88，nvidia-smi 2026-09-25/28 在位） | census §零 |
| 单格耗时 | 35.33s/格（T0 实测）；census 加权现状 ≈26.7s/格 | T0 manifest / census §一 |
| T1 全程 | ≈40h CPU（3,700 格，未开档位扫描） | Owner 指令 2026-09-28 |
| 掩码面占比 | 单 pass 74-78%（L1 去重前）；cProfile `_load_seal_masks` 95.4% | census §一 |
| L1 收益锚 | 8.6x（现状口径）/16.6x（扫描口径） | census §二·补 |
| L2 收益推演 | L1 之上再 4-10x（张量+权重构造批并行） | three_tiers §二（推演项，落地须实测复核） |
| 显存预算 | 面板+掩码 ≈50MB/宇宙；all_a weights 33.9MB/格 → B≈500 格/波 | census §三 / three_tiers §二 |

## 五、P0 落地先例（本清单的活样本，2026-09-28）

- `src/zephyr/backtest/gpu_core.py`：考试引擎张量核（`_c4_engine._backtest_core`+`_net_line`）的 CuPy 薄核——import guard/HAS_GPU、env 三态后端开关、xp 单一代码路径（numpy|cupy）、FP64 收口、串行闸循环原样保留（census L2-a 判定不改）、CPU 逐位对拍 + GPU 1e-12 对拍。
- `tests/backtest/test_gpu_core_parity.py`：全合成 seeded 数据（CH 停机夜可跑）；引擎真身 `_backtest_core`/`net_returns_by_tiers` 逐位参照（掩码 monkeypatch 注入，零 CH）。
- 后续接线（P1/P2 候选）：权重构造批化（combine 缓存未命中面）、WFA/CPCV fold 批并行、掩码构建 GPU 元素比较——均须重跑 §一四问（时点变了，结论可能变）。
