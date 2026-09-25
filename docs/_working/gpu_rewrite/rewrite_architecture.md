---
ttl: task_bound
title: GPU 重写挖矿③——重写架构方案（L1/L2/L3 三层设计）
created: "2026-09-25"
sid: st-gpu-rewrite-mining-20260925
family_id: GPU-REWRITE
---

# ③ 重写架构方案（方案③施工总图的前置设计）

> 前置共识：重写对象=考尺链（F1+F2+F3，①文），核=`scripts/backtest/translated/_c4_engine.py:399-458`；整装引擎（F8）不在本战役改动面（口径真源，IBT-D01 未收口前禁动，`docs/_working/decision_map_campaign/11_integrated_backtest_audit.md:152`）。
> 硬件约束（诚实前提）：RTX 3090 24GB，**FP64 吞吐≈FP32 的 1/64**——"整卡搬 float64"会把 GPU 打回 CPU 水平；精度策略见每层标注。

## L1 · 热点向量化+去重（不碰 GPU，3-7x）

### 核心洞察（本班新证，代码级）
当前每格跑 **7 次引擎 pass**，其中结构性冗余占大头：
1. **档位间冗余**：`run_cost_tier_scan` 每档全量重调 `daily_net_returns`（`exam_cost_gate.py:149`），但五档之间唯一差异是 `cost = turnover × (佣金2.5×2 + 印花10 + slip×2)/1e4` 一个标量（`_c4_engine.py:457`）——gross/turnover/涨跌停闸全是档位无关量，被重复算了 5 遍。
2. **函数间冗余**：`run_backtest`（:399-436）与 `daily_net_returns`（:439-458）数学重叠 90%（net 序列两处同式 :423-424 vs :457-458），执行器却两连调（`factory_grid_executor.py:777-778`）。
3. **掩码重建冗余**：`apply_fillability_gate` 每 pass 重查 CH 两次+Python `iat` 循环建掩码（`_c4_engine.py:341-368`，约 50 万行 lim_rows 逐行 dict 查找），**无任何缓存**——同一格 7 次 pass = 14 次 CH 往返 + 7 次全量循环，而掩码只依赖 (宇宙, 窗口)，格间可全批共享。

### 改动面（全部单文件内，零新模块）
| 文件 | 改动 |
|---|---|
| `_c4_engine.py` | 新增 `compute_backtest_factors(weights, px_close) -> (gross, turnover, w_gated)`；`run_backtest`/`daily_net_returns` 改为其消费方（缺省行为逐位零漂移）；`_load_seal_masks` 加 per-(窗口,列集) memo |
| `exam_cost_gate.py` | `run_cost_tier_scan` 改单遍：factors 一次算，五档只做标量乘得五条 net（判定函数零改动） |
| `factory_grid_executor.py` | :777-778 两连调合一；掩码批级共享；（可选）②' 分片：picked 切 N 段多进程，manifest 合并加 run_ts 段号 |

### 数据流（改后）
```
格点 recipe → evaluate_recipe（不变）
  → compute_backtest_factors（每格 1 次：掩码查缓存，gross/turnover 一遍）
  → run_backtest 统计量（复用 factors） + 五档 net = gross − turnover×const(bp_i)（五次 O(T) 标量乘）
```

### 验证策略
- **逐位等价**：L1 不改任何浮点运算顺序（hoisting 只挪位置不换算法）→ CPU 新旧实现对拍必须 **bitwise 相等**（net 序列逐位、sharpe/mdd 逐位）。容差=0，达不到即回退。
- 红蓝：T0 200 格新旧执行器全对拍（manifest 逐列 diff）。

### 工程量/加速比（诚实区间）
- 工程量：**1-2 天**（含对拍脚本；②' 分片另 +0.5 天）。
- 加速比：pass 数 7→2（估），掩码 CH 往返 14→2，Python 掩码循环 7→1 次。**预估 3-7x**（35.33s→5-12s/格）；下界假设=热点其实在 pandas 宽表运算本身，上界假设=CH 往返+循环占主导。**施工前先跑一次 cProfile 定分位数**（①文 §三 已立此前置）。

## L2 · 批量 GPU（格子批处理上 GPU，10-30x 叠加 L1 后总 30-100x）

### 设计要点
- **数据一次进显存**：per-宇宙面板（close T×S、seal 掩码 T×S、vol20/factors T×S）驻留显存，3,700 格共享——这是 GPU 收益的根源（①文 F1 评级 A 的含义）。
- **格间批量化**：`net = (w_shift × rets).sum(symbols)` 对 B 个格点一次 einsum（批量维=格点）。权重构造（rank/normalize/sizing）同批张量化——arXiv:2507.07107 的 `torch.unfold` 同款几何（②文 §7）。
- **稀疏权重是显存可行性的钥匙**：top-N sizing（top10/20/50，`factory_grid_executor.py:598-602`）使权重面板天然稀疏（300 列宇宙持仓 ≤50 只；all_a 5,000 列持仓 ≤50 只）。稠密存 3,700 格 all_a 面板 = 3,700×1,650×5,000×4B≈122GB 爆显存；**indices+values 稀疏表示 = ~100x 压缩 → ≤2GB**。按宇宙分波（hs300/zz500 波全量进，all_a 波 ~200 格/波）兜底。
- **精度策略（3090 的 FP64 陷阱）**：默认 **FP32 计算 + FP64 CPU 对拍容差**（净收益序列相对容差 1e-5，见④文；1,650 日复利累积 FP32 舍入 ~1e-6 量级，可承受）；提供 FP64 fallback 开关（吞吐掉到 ~1/64，仅仲裁争议格时用）。禁 TF16/TF32 加速路径（不确定性来源，④文禁令）。
- **涨跌停闸的 GPU 化**：`apply_fillability_gate` 逐日循环带 prev 依赖（:386-395）——GPU 上保持逐日循环（1,650 步 × 批内并行列，仍在毫秒级），**不强行 scan 化**（工程风险大于收益，如实标注）。

### 改动面（新模块 1 + 触点 2）
| 文件 | 性质 |
|---|---|
| `src/zephyr/backtest/implementations/gpu_panel_engine.py` | **新建**（登记 MOD 号+大白话简介+creation_token）：面板装载/批量权重构造/批量 net 核/FP32-64 开关；CuPy 或 Torch 单依赖 |
| `factory_grid_executor.py` | 加 `--engine gpu|cpu` 开关（缺省 cpu=零行为变化）；GPU 路径产物走同一 manifest schema |
| `exam_cost_gate.py` | 零改动（五档判定吃 net 序列，引擎无关——扫描/判定两面分离既有纪律 `exam_cost_gate.py:8`） |

### 数据流图
```
CH 一次拉取 → CPU 面板（per 宇宙） → to_device 一次
  → [GPU] 批量 evaluate（rank/sizing 稀疏化）→ 批量 factors（gross/turnover einsum）
  → 五档 net 批量标量乘 → 统计量批算（mean/std/cumprod）
  → 回传 CPU（manifest 行流式吐出）→ 判定/落盘（CPU，复用现有 gate）
```

### 验证策略
- ④文框架全量适用：同一格 CPU 真源 vs GPU 被测三层对拍（逐位不要求、统计量容差+排名层严格）。
- 每波格点抽 5% 做 CPU 复算对账（防批量索引错位类静默错）。

### 工程量/加速比（诚实区间）
- 工程量：**1.5-2.5 周**（核 3-5 天 + 批量权重构造 3-5 天 + 对拍修 3-5 天 + 缓冲）。
- 加速比：L1 后单格 ~5-12s → GPU 批摊后 **等效 0.3-1.5s/格**（3,700 格一波算完的墙钟摊薄，含数据装载分摊）。**总 30-100x vs 现状**。假设：批量维 ≥500 格时 GPU 利用率 >60%；all_a 波稀疏化生效；T1 轻档制叠加。若 rank/构造无法有效批量化（F3 评级 B 的风险落地），加速比退到 10-20x——如实区间。

## L3 · 全 GPU 回测核（事件逻辑也 GPU 化，最高野心）

### 范围与边界
- 把逐笔成本腿（matching_logic 逐笔 ADV tier、AC 冲击 η·p^β·σ）、tick 级回放（ch_tick_replay + hftbacktest 式排队位）也搬 GPU：per-symbol/per-trade 独立流并行（gather 化 tier 查表）。
- **不动判定位**：五档门/DSR/单调性判定永远留 CPU（判定是治理面不是算力面）。

### 现实约束（诚实）
- 改动面=整装引擎口径真源（F8），与 IBT-D01 双口径收口纠缠——**L3 的真前置是口径统一，不是 GPU**。
- tick 级 GPU 回放业界尚无现成件（hftbacktest 主线零 GPU，②文 §2）；等于自研 kernel 库，工程量月级。
- 19 号文既定纪律：**③ 等本轮成绩单产出密度再定，避免为饱和而饱和**（`19_gpu_plan:18` + F5 门位）。

### 工程量/收益
- 工程量：**1-3 个月**（含验证）；收益：对 F4/F5（做T分钟线 23.3h）端到端 3-10x、对 tick 回放 10x+（NVIDIA MC 几何外推，标注为外推非实测）；对日频网格的边际收益小（L2 已吃掉大头）。

## 落地顺序与依赖（推荐）

```
Phase 2: L1 向量化+去重（含②' 分片）     ← 零风险高确定性，先吃 3-7x
   ↓ 依赖：cProfile 实测热点 + 逐位对拍绿
Phase 3: 验证框架（④文）落地             ← 必须先于 L2 转正（红蓝纪律）
   ↓ 依赖：L1 的逐位对拍基建复用
Phase 4: L2 批量 GPU                      ← 只有 L1+① 不够时才启动（⑤文负决策条款）
   ↓ 依赖：验证框架绿 + 产出密度立项裁定（19号文 F5）
Phase 5: L3（条件触发）                   ← 前置=IBT-D01 口径收口 + 做T线成规模
```
