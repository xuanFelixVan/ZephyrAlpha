---
ttl: task_bound
title: LANE-GPU③ 重写架构三层（L1 等价去重／L2 批量 GPU／L3 全 GPU 驻留）——按实测热点重定的替换点与回退路径
created: "2026-09-25"
sid: st-gpu-rewrite-mining-20260925
lane: LANE-GPU
family_id: GPU-REWRITE
evidence_grade: A-（替换点全部带 file:line；收益区间全部锚在①文实测数上；未经实测的推演项显式标"推演"）
supersedes: docs/_working/gpu_rewrite/rewrite_architecture.md（同名义前一轮产物；本轮按实测把 L1 的靶从"档位扫描向量化"改判为"掩码重建去重+缓存"，并新增 OS/载体约束与稀疏度修正）
---

# LANE-GPU③ 重写架构三层

> 改动面总纲：**重写对象只有一个核**——`scripts/backtest/translated/_c4_engine.py:325-458`（掩码构建＋两函数体），判定位（`exam_cost_gate` 三门、DSR、单调性）**三层都不许动**（判定是治理面不是算力面）。
> 整装引擎（`src/zephyr/backtest/implementations/vectorized_engine.py` + `core/matching_logic.py`）＝**口径真源，本战役三层均不改**（双口径收口 IBT-D01 未结前动它＝动口径，见 `docs/_working/decision_map_campaign_20260924/11_integrated_backtest_audit.md:152`）。

## 〇、实测前提（决定三层的靶，来自①文）

| 事实（实测） | 对架构的含义 |
|---|---|
| 单 pass 中掩码 Python 面 74–78%、掩码 CH 面 17–22%、纯张量面 **2.8–3.6%** | L1 的靶=消除掩码重建重复与行物化；**任何只做张量 GPU 化的 L2 最多只能碰到 3.6% 的成本** |
| 掩码只依赖 (窗口, 列集)，与配方无关；同宇宙 1,236 格可共享一份 | L1 的核心机制=**批级掩码缓存**（键=(start,end,cols 指纹)） |
| 掩码中间物瞬时 ≈2.3GB（最终掩码仅 16MB） | 顺带解决内存与 CH 压力（每格 2 次全窗查询 → 每批 2 次） |
| `run_backtest` 与 `daily_net_returns` 同式两连调（`factory_grid_executor.py:777-778`） | L1 白捡 1 个 pass（all_a 级 ≈30s/格） |
| 五档之间唯一差异是标量（`_c4_engine.py:457`），实测五档标量乘 <0.1ms | L1 后"开五档扫描"从 139s 降到 ~7×张量（≈7.5s），**使方案①/②'的成本顾虑失效** |
| 权重非零占比 all_a 47.9%（ffill 摊密） | **推翻"稀疏索引表示 100x 压缩"的前一轮假设**；L2 显存预算须按稠密算 |
| 宿主 Windows 原生，cuDF/Polars-GPU 不支持原生 Windows（②文 C3） | **L2 载体=CuPy（MIT，Windows 有二进制）或 numba.cuda（BSD，已装）**，不能选 cuDF |
| torch 在本仓钉为 CPU 版（`requirements.txt:5-10`） | 若选 PyTorch 作载体=翻转一条既有裁定钉 → 属 Owner 门位；故**默认 CuPy** |

## 一、L1 等价去重（零新依赖，pandas/numpy 级）

### 接口切分（新增 1 个纯函数核 + 1 个缓存，语义零漂移）

```
现在：run_backtest(w,px) ─┐
      daily_net_returns(w,px) ─┤→ 各自内部：ffill→pct_change→apply_fillability_gate(重建掩码)→gross/turnover→cost
      run_cost_tier_scan(×5)  ─┘
改为：factors = compute_backtest_factors(w, px, masks)   # 掩码由外部注入（可缓存）
      net(tier) = factors.gross - factors.turnover * K(tier)   # K 为档位标量（_c4_engine.py:457 同式）
      run_backtest/daily_net_returns → 退化为 factors 的两个消费方（签名保留，缺省行为逐位不变）
```

| 替换点（file:line） | 改法 | 现测代价 | 改后（推演，须实测复核） |
|---|---|---|---|
| `_c4_engine.py:325-369 _load_seal_masks` | ①CH 侧一次取回（按宇宙一次，不每 pass）；②dict/iat 双循环→**向量化**：把 (date,sym) 行集 pivot 成与 `index×columns` 对齐的两张矩阵后逐元素比较（`close_raw >= limit_up*(1-tol)`） | all_a 28.5s/pass（含 CH 5.05s） | 掩码构建每批 1 次；单格摊销≈0 |
| `_c4_engine.py:372-396 apply_fillability_gate` | 保留逐日 prev 循环（占 1.3%，不动）；入参改为"掩码由调用方注入" | 0.40s | 不变 |
| `_c4_engine.py:415-420 / 450-455` | 抽 `compute_backtest_factors`；两函数共用 | 每 pass 1.07s 张量 | 每格 1 次（档内只算标量） |
| `exam_cost_gate.py:120-149 run_cost_tier_scan` | 由"每档调 net_fn"改为"吃 factors 出五档"（**判定函数零改动**；`net_fn` 口径注入位保留给考试链老调用方） | 139.3s/all_a 格 | ≈7.5s（7×张量） |
| `factory_grid_executor.py:777-778` | 两连调合一 | 白付 1 pass ≈29.9s | 0 |
| `factory_grid_executor.py:706-711`（批级缓存区） | 新增 `seal_mask_cache[(start,end,cols_fp)]`，与既有 `slice_cache/combine_cache` 同批级生命周期 | — | 缓存命中即免 |

### 语义与一致性约束（必须写进实现的三条）

1. **缓存键完整性**：掩码依赖 (窗口, 宇宙列集, stk_limit/kline 数据版本)。跑批中 CH 为只追加（历史日不改）→ 键内加"本批冻结窗口"即可；**跨批复用必须带数据版本指纹**（否则日更后拿到旧掩码=静默语义漂移，属 E7 同族风险）。
2. **PIT 不放松**：向量化改写只允许改变"行物化方式"，不允许改变判定单位（原始价 vs hfq，`_c4_engine.py:328-331` 的 E7 追加 §3 实锤教训）与 fail-open 语义（NULL/缺行→False）。
3. **逐位等价是 L1 的验收门**：不改变浮点运算顺序（hoisting 只挪位置）→ ④文层1 要求 bitwise 全等，达不到即回退。

### L1 收益（按①文实测数算的区间，非承诺）

| 场景 | 现状/格 | L1 后/格 | 倍率 |
|---|---|---|---|
| 在飞口径（无扫描，加权） | 26.7s | ≈3.1s（eval 0.7–5.3 + 2×张量） | **≈8.6x** |
| 五档扫描全开（加权） | 85.8s | ≈5.2s | **≈16.6x** |
| 轻档两档（方案①，加权） | 30.0s* | ≈3.8s | ≈7.9x |

*轻档按 scan2 加权推得（hs300 4.10/zz500 12.07/all_a 58.35 + 现状）——L1 之后**方案①与②'的取舍会反转**：扫描成本不再构成产能约束（详见⑤文）。

### 回退路径

单 commit revert（改动集中在 `_c4_engine.py`/`exam_cost_gate.py`/`factory_grid_executor.py` 三文件）；保留 `gate_limits`/`net_fn` 老签名与老调用方（考试链 `f06_e4_wfa_exam.py`、`t1_t2_handover.py:296-343` 不改即可继续跑老路径）；缓存以"缺省关"上线，一次批测窗验证后再翻默认。

## 二、L2 批量 GPU（格点批并行；载体=CuPy，**非 cuDF**）

### 什么必须留在 CPU、什么进 GPU

| 面 | 归属 | 理由 |
|---|---|---|
| 判定（三门/DSR/单调性/换手帽） | CPU | 治理面，禁与算力同移（④文） |
| CH 读取＋宽表 pivot | CPU | ①文实测批级 68s=0.07%，无收益 |
| **封板掩码构建** | **CPU（向量化后）或 GPU 侧元素比较** | 掩码只依赖 (窗口,列集)→**每批一份，不构成 GPU 靶**；进 GPU 的动机是省 CPU 时间而非省重复 |
| 权重构造（normalize/rank/sizing/组合） | GPU（B 格一批） | L1 后它升为第一大项（all_a 5.33s/格，combine 缓存未命中时）——**这是 L2 的真靶** |
| 张量核（gross/turnover/五档 net） | GPU | 单独只值 3.6%（现状），但 L1 后占比升到 ~20%，且批并行后统计量（mean/std/cumprod）一并算 |

### 数据流

```
CPU: 批级一次性 → 面板(hfq close)+掩码两份(GPU 常驻) → cupy 一次性 to_device（≈50MB/宇宙）
GPU: B 个配方 → [normalize/rank/combine/sizing] → weights(B,T,S) → gated weights（逐日 prev 循环仍在 GPU kernel 内串行 T）
     → gross(B,T)/turnover(B,T) → 五档 net(B,5,T) → 统计量(B,5)
CPU: 回传 (B,5) 统计量 + net 序列（manifest 行流式落盘）→ 判定/门禁（零改动）
```

显存预算（按①文实测尺寸，稠密 float32 推演）：单宇宙面板+掩码 ≈50MB；weights 每格 T×S×4B（all_a=33.9MB）→ **B 上限受 18GB 配额约束≈500 格/波**（all_a 稠密）。前一轮"稀疏化到 ≤2GB"的假设已被稀疏度实测削弱（47.9% 非零），**不得据其立项**。

精度策略（3090 的 FP64=FP32 的 1/64 吞吐，推演自硬件规格）：默认 FP32 计算＋④文层2 容差对拍；保留 FP64 单格仲裁开关；**禁 TF32/FP16 路径**（不确定性叠加，④文禁令）。

### 替换点与新增件

| 位置 | 性质 |
|---|---|
| 新建 `src/zephyr/backtest/implementations/gpu_panel_engine.py` | 唯一新模块（须登记 MOD 号＋大白话简介 `add_module_translation.py`＋creation_token）；依赖 CuPy（新钉进 `requirements.txt`，属依赖变更=按⑤文门位表报批） |
| `factory_grid_executor.py:732-831` 单格循环 | 加 `--engine cpu|gpu` 开关（缺省 cpu=行为逐位不变）；GPU 路径按宇宙分波，产物走同一 manifest schema＋独立 run_ts 目录 |
| `exam_cost_gate.py` | 零改动（判定与扫描面分离既有纪律 `exam_cost_gate.py:8`） |

### 回退路径

`--engine cpu` 常开；GPU 波失败=整波作废重跑 CPU（manifest 同构，无半成品混入）；CuPy 依赖出问题=import 失败即 fail-closed 退回 CPU 并记 degraded（禁静默降级）。

### 收益（诚实区间，且**已按实测重估，低于前一轮**）

L1 后 all_a 格 ≈11.7s（eval 5.3 + 7×张量 7.5）→ L2 把张量与配方构造批并行：批摊后单格**推演 1–3s**（GPU 对 300–5,000 列元素级的收益按 Spectre 77.7x/cuDF 50x 带取保守下界，再扣 H2D/回传），即 **在 L1 之上再 4–10x**；总 8.6x(L1) × 4–10x ≈ **35–85x**（vs 现状，扫描开启口径）。风险：逐日 prev 依赖循环（`_c4_engine.py:385-395`）与 `rank(axis=1)`/`orth_equal` 批量化难度——若这两项打不开，收益退到 1.5–2x，即触发⑤文 N2/N3 停手线。

## 三、L3 全 GPU（数据面驻留；本战役内**默认不做**）

范围：把 CH→面板→掩码→权重→统计整链常驻 GPU（cuDF/WSL2 侧车或 GPU 原生列存），并把**做T分钟线语料面**（①文 F4 族：11.5 亿行、全量 ≈23.3h CPU，来源 `docs/_working/decision_map_campaign/links/L05_t0/material_precapacity_report.md:23`）与 tick 级回放并入。

真前置（不是 GPU，是口径与数据）：① IBT-D01 双引擎口径收口；②分钟/tick 数据可得性与质量画像（字段在≠可用）；③L2 稳定运行一整个批测周期。工程量按月级（含 kernel 库自研：hftbacktest 主线零 GPU，业界无现成件——②文结论 A）。收益对日频网格**边际很小**（L2 已吃掉张量面），对 F4 端到端 3–10x 属外推（**标注：外推非实测**）。

## 四、六向台账（本件）

| 向 | 内部反查 | 全网搜索 |
|---|---|---|
| ①上游 | 逐字段核 `_load_seal_masks` 输入（raw close+stk_limit）与 `run_backtest` 输入（hfq close）分表→**这就是"每 pass 两次全窗查询"的结构根因**；提出批级注入接口 | cuDF 官方页具名加速操作=joins/aggregations/sorting（②文 C1）→ 说明"掩码 join"这类工作业界确实放 GPU，但本项目已被 L1 缓存消解 |
| ②下游 | manifest/net_returns/负结果库消费方逐一核（①文②向）→ 三层都必须保持 manifest schema 与判定入参逐位不变 | 搜 "GPU backtest result determinism validation"→ 命中 CCCL/CUDA FP 文（②文 B1/B2）支撑④文分层对拍 |
| ③算法/机制 | 仓内既有等价向量化先例：T2c `_apply_freq_trigger` 向量化"与逐日循环逐位等价"＋lasso 参数放宽"非逐位等价"（docstring :37-45）→ **仓内已有"等价/非等价"两档先例，L1 只允许前者** | arXiv:2507.07107 的 `unfold` 批量几何＋Spectre 全面板因子= L2 权重构造批化的同构先例 |
| ④后端 | 三层替换点全部 file:line（本文各表）；新建模块登记义务（TRANSLATION-COVERAGE/creation_token）已写入 | 载体可行性=②文 C3/C4（cuDF Windows 不可用 / CuPy Windows 可用）＋本机 `find_spec` 实盘（torch CPU 钉、numba 在位） |
| ⑤前端 | 反查"引擎开关是否需要呈现"→ 仪表盘无 grid 读端（已查无）；GPU 波次/回退需在 summary 里留披露位（`summary.json` 增键，属产物自描述义务，非前端施工） | 外部呈现惯例登记长尾（②文⑤向） |
| ⑥数据字段 | L2/L3 需要的字段清单逐条对 ①文⑥向结果：全在（7/7）；新增要求=**宇宙列序指纹字段**（缓存键完整性），当前无 → 标 GAP 待落 | 外部字段口径：涨跌停价定义已由 qlib `limit_threshold`＋arXiv 双证 |

## 五、挖矿日志（本件）

| 轮 | 矿脉 | 判定 | 关键产出 |
|---|---|---|---|
| R1 | 仓内等价向量化先例（内部） | signal | "逐位等价可上、非等价须裁定"的分级成例（T2c/lasso）→ 写进 L1 约束 |
| R2 | 载体可行性（内部依赖盘点＋外部 OS 支持） | signal | **cuDF 出局、CuPy 首选**（Windows 原生硬约束，②文 C3/C4） |
| R3 | 稀疏权重假设复核（内部实测） | signal（否定性） | 47.9% 非零→稀疏化收益被推翻，显存预算改按稠密（前一轮 ≤2GB 结论不可用于立项） |
| R4 | L1 收益的实测算术（内部） | signal | 现状 8.6x / 扫描口径 16.6x——**高于 19 号文对②档"3-5 倍"的估计** |
| R5 | 掩码 GPU 化的必要性（外部 cuDF 具名操作 vs 内部缓存方案） | signal（判否） | 每批一份→重复已消，GPU 化掩码不作为 L2 目标（防为饱和而饱和） |
| R6 | 3090 FP64 吞吐比、cuDF-polars 限制清单 | 待验证 | 前者=硬件规格未在本机实测（禁 GPU 作业）；后者=官方文档页 404（②文 R6 已记受阻） |
| 长尾 | 未挖 | — | CuPy 与本项目 `numba`/`scikit-learn`（lasso/Gram-Schmidt 路径）共存冲突评估；WSL2 侧车方案与 HyperV CH VM 的资源竞争 |

## 六、挖后自审闸（三态裁定）

- **主判据**：三层设计把"要不要 GPU"从主观争论变成**可测门槛**（L1 之后剩余热点是否仍 >48h 墙钟），消灭的是"Owner/总筹人工拍板提速方案"这一环节。
- **终局位置**：L1 有且必须现在做；L2 有但时序在后（等 L1 实测数）；L3 在终局有位置（做T语料面＋tick 回放），但**层位高于本战役**，现做=在错误层位建中间件。
- **裁定**：**L1=施工**（改动面三文件、逐位对拍可验）；**L2=挂起排期**（解锁条件=L1 落地实测 + ⑤文 N1/N2/N4 三线全不命中 + Owner 批 CuPy 依赖）；**L3=挂起排期（前置=IBT-D01 口径收口）**，非封矿——终局要它，只是时序未到。
- **反驳者一问**：①"L1 只做去重是否辜负 GPU 立项？"→ 实测显示重复计算才是热点，GPU 化前先消除重复是任何性能工程的第一性步骤；②"三层并列写会不会诱导并行施工返工？"→ 已用⑤文的互斥/依赖与回滚点钉死顺序，且 L2/L3 都带停手条款；③"掩码缓存会不会引入跨批数据版本漂移？"→ 已在 §一·约束1 把"数据版本指纹"写成实现义务，④文层1 bitwise 对拍负责兜底。
