---
ttl: task_bound
title: GPU 重写挖矿②——业界 GPU 量化方案全景（2026-09 调研）
created: "2026-09-25"
sid: st-gpu-rewrite-mining-20260925
evidence_grade: A-（全部外部论断带仓库/文档 URL+许可证；许可证与活跃度经 GitHub API 2026-09-25 实核）
---

# ② 业界 GPU 量化方案全景

> 评级口径：**直接用**（引依赖进仓）/ **参考架构**（学其分层抽象，不引码）/ **仅借鉴思想**（读论文读 README）。
> 许可证/活跃度为 GitHub API 2026-09-25 实核值（license 字段+pushed_at）。

## 一、逐项调研

### 1. qlib（microsoft/qlib）——MIT，活跃（pushed 2026-09-22，48.8k stars）

- **是否已有 GPU 回测后端：没有。** GPU 加速只覆盖 ML 模型层（PyTorch 训练/推理）；回测面（Exchange 模拟+`NestedExecutor` 日内→日间双层执行，`qlib/backtest/executor.py`）是纯 CPU pandas 实现（出处：仓库源码路径 [qlib/backtest/executor.py](https://github.com/microsoft/qlib/blob/main/qlib/backtest/executor.py)；[官方 backtest 文档](https://qlib.readthedocs.io/en/v0.5.1/component/backtest.html) Order Executor/Exchange 分层；2026-09 调研无 GPU 回测后端的 issue/PR/release 证据）。
- **CPU/GPU 双实现抽象**：qlib 没做回测双实现；它的"GPU 化"靠把模型层交给 PyTorch，数据层交给自家 Arrow/parquet 面板，回测层保持 CPU——**这本身就是一个答案**：业界最主流的 AI 量化平台选择不为回测核做 GPU。
- **可复用性评级：参考架构**（workflow/数据面板/DSR 纪律值得学；回测核不可复用）。

### 2. hftbacktest（nkaz001/hftbacktest）——MIT，4.8k stars（pushed 2025-12-23）

- **GPU 部分覆盖什么：主线现状=没有 GPU。** 本班实证三连：①README 全文 271 行零 GPU/CUDA 字样（GitHub API raw 2026-09-25 抓取 grep 实证）；②官方文档 "Accelerated Backtesting" 教程页 233KB 全文零 GPU/CUDA 字样（curl 2026-09-25 抓取 grep 实证，[docs](https://hftbacktest.readthedocs.io/en/latest/)）；③PyPI v2.4.4 `requires_dist` 仅 `numba~=0.61`（CPU JIT），无 cuda 依赖（PyPI JSON API 实核）。v2.1.0 文档时代曾把"GPU multi-asset"列过 roadmap 方向（[v2.1.0 docs](https://hftbacktest.readthedocs.io/en/py-v2.1.0/index.html)），但截至 v2.4.4 未落主线。
- 它真正的强项：L2/L3 tick 级全订单簿重建+限价单排队位+延迟建模（[GitHub](https://github.com/nkaz001/hftbacktest)），Python(Numba JIT)+Rust 双实现。
- **可复用性评级：直接用**——但对象不是 GPU 重写，而是**未来 EXE-8 五档/tick 级回放**（L07 SKEL §5 已采其排队位/延迟建模语义做 ch_tick_replay 设计对表：`docs/_working/decision_map_campaign/links/L07_exec/SKEL.md:188`）。对 GPU 战役=仅借鉴思想（per-symbol 独立流的并行切法）。

### 3. vectorbt / vectorbt PRO

- **开源版**（polakowo/vectorbt，自定义许可证 NOASSERTION，9.2k stars，活跃）：Numba CPU JIT 加速，无 GPU（[vectorbt.dev](https://vectorbt.dev)）。
- **PRO 版**（闭源付费）：官方 Performance 页明示"custom jitter classes, such as those for vectorized NumPy or even **JAX with GPU support**"——GPU 路线=换 JIT 后端到 JAX，非原生 CuPy kernel（[vectorbt.pro/features/performance](https://vectorbt.pro/features/performance)，2026-09 抓取）。
- **可复用性评级：仅借鉴思想**（PRO 闭源不可采；开源版引擎语义与 A 股 T+1/涨跌停闸/五档成本门不匹配，移植成本高于自写薄核；其"jitter 抽象=同一语义多后端"的思路对 L2 设计有参考价值）。

### 4. Spectre（Heerozh/spectre）——**GPL-3.0**，826 stars，基本休眠（pushed 2025-04）

- PyTorch CUDA 的 GPU 因子引擎+组合回测（佣金/滑点/止损/再平衡全有），对 zipline 实测 33.9x（SMA）~77.7x（MACD+RSI+STOCHF rank 组合），RTX 3090（[GitHub README](https://github.com/Heerozh/spectre)，2026-09-25 抓取）。
- 三宗罪：**GPL-3.0 传染（禁采码）**；float32 精度设计；README 自认 look-ahead bias 风险需自带测试防；QuandlLoader 停更于 2018=项目半死。
- **可复用性评级：仅借鉴思想**（其"因子=全面板张量一次算完"与本项目 F3 同构，证明 3090 档 GPU 跑因子批量可行——这是对本项目最有用的基准数字）。

### 5. CuPy / cuDF / Polars GPU 在金融时序的成熟度

- **CuPy**（MIT）：NumPy drop-in，成熟稳定，与 Numba CUDA kernel 互操作官方支持（[CuPy interoperability docs](https://docs.cupy.dev/en/stable/user_guide/interoperability.html)）。**L2 的首选载体。评级：直接用。**
- **cuDF/cudf.pandas**（Apache-2.0，RAPIDS）：ETL/scan/sort/groupby 成熟（2025 实测口径：数值扫描类 ~30x，[johal.in 2025 benchmark]）；但**技术指标类滚动计算只有 ~2x（A6000）**（stockstats/TA benchmark 2025）——证明"GPU 不是免费午餐，rolling 窗口类收益平庸"。
- **Polars GPU engine**（`engine="gpu"`，RAPIDS 后端）：PyData London 2025 有专场（[cfp.pydata.org](https://cfp.pydata.org)），生产可用但**表达式覆盖有洞**（不支持的操作回落 CPU 或报错）。
- **评级：cuDF/Polars-GPU=直接用（数据装载/归因/做T线 ETL 侧），不进回测核。**

### 6. taichi / JAX / numba 在回测加速的实践对比

| 载体 | 金融回测实践 | 判定 |
|---|---|---|
| **numba(CPU+CUDA)**（BSD） | hftbacktest 全核 + NVIDIA 官方 MC 教程（见 §7）=**业界最主流回测 GPU 化路径** | 直接用（kernel 载体候选之一） |
| **JAX**（Apache-2.0） | RL 环境向量化成熟（PureJaxRL 系，33M steps/s 单 GPU 先例）；金融回测无成熟框架，但 `vmap` 批量=理论最优雅；vectorbt PRO 的 GPU jitter 即 JAX | 参考架构（L3 野心层理论载体；生态/调试成本高，3090 上无优势） |
| **taichi**（MIT） | **2024-2026 未找到任何成熟金融回测案例**（搜索实证：结果全为图形/物理仿真领域） | 不采（诚实缺证据） |

### 7. Academic/官方：GPU-accelerated backtesting 2024-2026

- **NVIDIA Developer Blog（2025-03-04）"GPU-Accelerate Algorithmic Trading Simulations by over 100x with Numba"**（Mark J. Bennett）：随机 MC 订单簿模拟 Numba CUDA 化，**H200 上 114x**；加速几何=**千级独立路径并行 × 时间步串行**；显存数组 (Nsims, Nt) 预批正态/均匀变体；host/device 同种子对拍验证（[developer.nvidia.com](https://developer.nvidia.com/blog/gpu-accelerate-algorithmic-trading-simulations-by-over-100x-with-numba)，全文抓取 2026-09-25）。**注意：此文不是 hftbacktest**（多篇二手转述张冠李戴，本班已核原文）。→ 对本项目 F12（未来 MC 族）=参考架构。
- **arXiv:2507.07107**（ML Enhanced Multi-Factor Quantitative Trading, 2025-07）：用 `torch.unfold` 把"滞后权重×收益−成本"整段向量化上 GPU，并明说为何弃 pandas NaN-传播路径（[arxiv.org/abs/2507.07107](https://arxiv.org/abs/2507.07107)）→ 与本项目 F1+F2 的数学同构，**借鉴思想：批量维=格点，时间维=unfold/shift**。
- 学术界 2024-2026 **没有出现"canonical GPU 回测框架"论文**——主流共识仍是：回测核留在 CPU，向量化+并行格点（Reddit r/algotrading 2024 性能讨论同口径）；GPU 出现在 MC/RL/因子计算侧。
- 新框架扫描：QuantPits（GPU 暴力组合回测，许可证未核实，[GitHub](https://github.com/DarkLink/QuantPits)）=只登记不采；nautilus_trader/backtesting.py/LEAN 均无 GPU 回测模块（2026-09 搜索实证）。

## 二、核心问题裁定：自研 vs 改造现成框架

**裁定：自研薄核（~数百行 CuPy/NumPy 数学），基座用现成库（CuPy/Torch/numba），不改造任何现成回测框架。** 理由五条：

1. **核太小**：考尺引擎的数学本体 = `_c4_engine.py:439-458` 二十行 pandas 式子。改造 qlib/vectorbt 要把 A 股冻结语义（T+1、涨跌停可成交闸 `_c4_engine.py:372-396`、PIT 宇宙 SCD-2 `:252-287`、五档成本门 `exam_cost_gate.py:152-221`）翻译进别人的抽象——移植成本远大于重写 20 行数学的 GPU 版。
2. **没有现成框架有 GPU 回测核**（qlib/vectorbt/hftbacktest/nautilus/LEAN 五家实证全 CPU）——"改造现成框架"改造不出 GPU，只能改造出又一个 CPU 引擎。
3. **GPU 的收益几何与本项目完全同构**：3,700 格独立 × 共享同一数据面板 × 每格内时间串行——这正是"批量维并行、时间维串行"的教科书 GPU 形状（NVIDIA MC 文的 114x 几何同款），CuPy/numba 自写即得，无需框架。
4. **验证纪律倒逼薄核**：等价性对拍要求 GPU 核与 CPU 真源逐段可对照（④文），框架黑盒会杀死对拍能力。
5. **许可证风险面**：唯一 GPU 回测现成件 Spectre=GPL-3.0（传染，禁采）；vectorbt PRO=闭源付费；开源 vectorbt 许可证非标（NOASSERTION）。自研薄核+MIT/BSD 基座库（CuPy MIT/numba BSD）许可证面干净。

## 三、来源清单

| 来源 | 类型 | 许可证 | URL |
|---|---|---|---|
| microsoft/qlib | 框架 | MIT | https://github.com/microsoft/qlib |
| qlib backtest 文档 | 文档 | — | https://qlib.readthedocs.io/en/v0.5.1/component/backtest.html |
| nkaz001/hftbacktest | 框架 | MIT | https://github.com/nkaz001/hftbacktest |
| hftbacktest Accelerated Backtesting 教程 | 文档 | — | https://hftbacktest.readthedocs.io/en/latest/ |
| polakowo/vectorbt（OS） | 框架 | 自定义（NOASSERTION） | https://github.com/polakowo/vectorbt |
| vectorbt PRO Performance | 商业文档 | 闭源付费 | https://vectorbt.pro/features/performance |
| Heerozh/spectre | 框架 | **GPL-3.0** | https://github.com/Heerozh/spectre |
| CuPy | 库 | MIT | https://docs.cupy.dev/en/stable/user_guide/interoperability.html |
| NVIDIA MC 教程 blog | 官方教程 | — | https://developer.nvidia.com/blog/gpu-accelerate-algorithmic-trading-simulations-by-over-100x-with-numba |
| arXiv:2507.07107 | 论文 | 开放获取 | https://arxiv.org/abs/2507.07107 |
| QuantPits | 框架 | 未核实 | https://github.com/DarkLink/QuantPits |
