---
ttl: task_bound
title: LANE-GPU② 业界 GPU 回测／向量化方案全景（全网实查，含对前一轮结论的更正）
created: "2026-09-25"
sid: st-gpu-rewrite-mining-20260925
lane: LANE-GPU
family_id: GPU-REWRITE
evidence_grade: A-（外部论断逐条带 URL+发布方+年份+访问日期；未复核项一律标"待验证"不入图；搜索受阻如实记"受阻"）
supersedes: docs/_working/gpu_rewrite/gpu_landscape.md（同名义前一轮产物；本轮新增 4 条结论级来源并更正其 2 条未能复核的引文；2026-09-26 双版合并：前一轮**逐家实证表**（含 LEAN 与 URL/stars/许可证/hftbacktest 三连细证）已补入本文 §一「结论 A 补」，取代关系自此为实）
---

# LANE-GPU② 业界 GPU 回测／向量化方案全景

> 采集日期：2026-09-25（所有"访问即核"均标此日期；GitHub 元数据经 api.github.com 实取）。
> 评级口径：**直接用**（可引依赖进仓）／**参考架构**（学分层抽象不引码）／**仅借鉴思想**／**不采**（含许可证否决）。

## 一、决定路线的三条主结论（每条 ≥2 独立来源）

### 结论 A：主流开源回测/交易框架**没有 GPU 回测核**——回测核留 CPU 是业界现状而非疏忽

| # | 来源 | 证据 |
|---|---|---|
| A1 | [microsoft/qlib](https://github.com/microsoft/qlib)（MIT，48,844 stars，pushed 2026-09-22，GitHub API 2026-09-25）＋其回测撮合层源码 [qlib/backtest/exchange.py](https://github.com/microsoft/qlib/blob/main/qlib/backtest/exchange.py)（抓取 2026-09-25） | 该文件"无 GPU、CUDA 或加速数组库出现在 import 或逻辑中，运行在标准 Python + NumPy + Pandas，纯 CPU 执行"；A 股约束以 `limit_threshold`（float 或 (涨停,跌停) 元组）建模 |
| A2 | [nautilus_trader README](https://github.com/nautechsystems/nautilus_trader)（**LGPL-3.0**，29,385 stars，pushed 2026-09-25，GitHub API 实取）＋README 全文核（2026-09-25） | README 全文 **零** "GPU/CUDA/RAPIDS" 字样；并明示 "built-in AI/ML tooling are out of scope to maintain focus on the core engine" |
| A3 | [VectorBT® PRO — Performance 页](https://vectorbt.pro/features/performance/)（商业闭源，访问 2026-09-25） | 页面上具名的计算后端只有 "NumPy, Numba, and native Rust backends"，**本窗口未能复核到任何 GPU/JAX/CuPy 字样**（详见 §四 更正1） |
| A4 | [polakowo/vectorbt（开源版）](https://github.com/polakowo/vectorbt)（许可证 NOASSERTION，9,180 stars，pushed 2026-09-17）＋[hftbacktest](https://github.com/nkaz001/hftbacktest)（MIT，4,777 stars，pushed 2025-12-23） | 开源 vectorbt 以 Numba CPU JIT 为加速路径；hftbacktest 以 Numba/Rust 为加速路径，其"加速回测"文档亦未见 GPU 后端 |

→ **对本项目的含义**：想"改造现成框架上 GPU"改造不出 GPU；自研薄核是唯一路径（与③文裁定一致）。

### 结论 A 补 · 五家现成框架逐家实证表（前一轮 `gpu_landscape.md` 矿脉证据并入，2026-09-26 双版合并）

> 并入理由：挖矿 SOP 的来源可溯闸要求**每家的 URL／发布方／年份／stars／许可证一项不丢**——丢了本件就退化成"凭记忆断言业界做法"。
> 上表 A1–A4 是本轮真查重采口径，下表是前一轮（已落 HEAD commit 37aeecedcd）独立取证口径；两版各自成证，
> 数字冲突处逐行标注（不取平均、不改写任一方）。

| 家 | 仓库／发布方 | 许可证 | stars | 活跃度（访问／pushed） | GPU 覆盖到哪一层（该版实证） | URL |
|---|---|---|---|---|---|---|
| **qlib** | microsoft/qlib | **MIT** | 48.8k（前一轮四舍五入口径）／本文 A1 实取 48,844 | pushed **2026-09-22**，GitHub API 2026-09-25 | **回测面无 GPU**：GPU 只覆盖 **ML 模型层**（PyTorch 训练/推理）；回测面＝`Exchange` 模拟＋`NestedExecutor` 日内→日间双层执行，纯 CPU pandas（`qlib/backtest/executor.py`）。前一轮原话："业界最主流的 AI 量化平台**选择不为回测核做 GPU**——这本身就是一个答案" | https://github.com/microsoft/qlib ＋ [官方 backtest 文档](https://qlib.readthedocs.io/en/v0.5.1/component/backtest.html)（Order Executor/Exchange 分层） |
| **hftbacktest** | nkaz001/hftbacktest | **MIT** | 4.8k／本文 A4 实取 4,777 | pushed **2025-12-23** | **主线现状零 GPU**，前一轮实证三连（本表补齐本文 A4 的粗表述）：①**README 全文 271 行零 GPU/CUDA 字样**（GitHub API raw 2026-09-25 抓取 grep）；②官方 "Accelerated Backtesting" 教程页 **233KB 全文零 GPU/CUDA 字样**（curl 同日抓取 grep）；③**PyPI v2.4.4 `requires_dist` 仅 `numba~=0.61`（CPU JIT），无 cuda 依赖**（PyPI JSON API 实核）。v2.1.0 文档时代曾把 "GPU multi-asset" 列进 roadmap 方向，截至 v2.4.4 **未落主线**。**它真正的强项＝L2/L3 tick 级全订单簿重建＋限价单排队位＋延迟建模**（Python Numba JIT＋Rust 双实现） | https://github.com/nkaz001/hftbacktest ＋ [docs](https://hftbacktest.readthedocs.io/en/latest/) |
| **vectorbt**（开源版） | polakowo/vectorbt | **自定义许可证（GitHub API license 字段＝NOASSERTION）** | 9.2k／本文 A4 实取 9,180 | pushed **2026-09-17**，活跃 | **无 GPU**：加速路径＝**Numba CPU JIT**（前一轮原话"Numba CPU JIT 加速，无 GPU"）。PRO 版（闭源付费）的"GPU 路线＝JAX jitter"一说本文 §四 更正1 已复核失败降为待验证，两版一致不据此立项 | https://vectorbt.dev ＋ https://github.com/polakowo/vectorbt |
| **nautilus_trader** | nautechsystems/nautilus_trader | **LGPL-3.0** | 29,385（本文 A2 实取） | pushed **2026-09-25** | **无 GPU 回测模块**（前一轮 2026-09 搜索实证；本文 A2 取证更强：README 全文零 GPU/CUDA/RAPIDS 字样＋官方明示 AI/ML tooling out of scope） | https://github.com/nautechsystems/nautilus_trader |
| **LEAN** | QuantConnect/Lean | **两版均未实取许可证／stars／pushed → 标"待验证"，禁凭记忆补**（本车道禁 GPU 作业亦禁联网重采之外，此项属长尾复采义务，已登记） | 待验证 | 待验证 | **无 GPU 回测模块**（前一轮 `gpu_landscape.md` §一.7 与 nautilus／backtesting.py 同批搜索实证结论） | 前一轮来源清单未列 LEAN URL → 本表不补 URL（缺证即标缺证） |

**五家合并后的总结论（一句话，前一轮口径原样保留）**：
**五家现成框架（qlib／hftbacktest／vectorbt／nautilus／LEAN）的回测核全是 CPU——改造它们改造不出 GPU，只能改造出又一个 CPU 引擎；自研薄核（数百行 CuPy/NumPy 数学）＋ CuPy 批量是正解，且许可证面干净。**
许可证面依据（前一轮 §二 理由五条之五，逐字存档于 git 历史 commit 37aeecedcd 的 `gpu_landscape.md:64-70`）：唯一带 GPU 回测的现成件 Spectre＝**GPL-3.0 传染（禁采码）**、vectorbt PRO＝**闭源付费**、开源 vectorbt＝**非标许可证（NOASSERTION）**；自研薄核的基座库 CuPy＝MIT、numba＝BSD-2-Clause → 干净。
LEAN 一家是本次合并的**唯一真缺口**（本文合并前五册零命中该词），其余四家前一轮的细粒度实证（README 行数 grep／PyPI `requires_dist`／backtest 文档 URL／stars 与许可证）此前散落在被改成指针的旧文里，现已入本件真源。

### 结论 B：GPU/CPU 对拍**不追求逐位等价**是数值计算的公开事实，但"离散量必须精确一致"与"跨实现比较要预判差异"是同一批文献的另一半

| # | 来源 | 证据（原文引） |
|---|---|---|
| B1 | [CUDA Documentation: Floating Point and IEEE 754 Arithmetic](https://docs.nvidia.com/cuda/floating-point/)（NVIDIA，v13.4，页面标注 last updated 2026-09-13） | "The order in which operations are executed affects the accuracy of the result."；并行归约改变加法分组 "the change rearranges parentheses in the long string of additions."；**"Take this into account when doing comparisons between implementations."** 与 **"Differences are not automatically evidence that the result computed by the GPU is wrong."** |
| B2 | [Controlling Floating-Point Determinism in NVIDIA CCCL](https://developer.nvidia.com/blog/controlling-floating-point-determinism-in-nvidia-cccl/)（NVIDIA Developer Blog，作者 Nader Al Awar、Srinivas Yadav Singanaboina，**2026-03-05**） | 确定性定义="multiple runs with the same input data produce the same bitwise result"；CCCL 提供三档确定性层级，最高档用"Reproducible Floating-point Accumulator"（按指数分箱固定加法序）可保证**跨 GPU** 逐位一致；**未对 CPU 等价或旧版本兼容作任何承诺** |
| B3 | [PyTorch Reproducibility（randomness）notes](https://docs.pytorch.org/docs/stable/notes/randomness.html)（PyTorch 官方文档，访问 2026-09-25） | "results may not be reproducible between CPU and GPU executions, even when using identical seeds." |
| B4 | [GPU-Accelerate Algorithmic Trading Simulations by over 100x with Numba](https://developer.nvidia.com/blog/gpu-accelerate-algorithmic-trading-simulations-by-over-100x-with-numba/)（NVIDIA Developer Blog，Mark J. Bennett，**2025-03-04**） | 其验证做法=把 device 数组 copy_to_host 后**按索引断言精确相等**（`assert(norm_variates_d.copy_to_host()[0,10]==norm_variates[0,10])`）——即"离散/输入侧精确一致 + 统计侧另验"的工程范式 |

→ **对本项目的含义**：④文的"层1 逐位（CPU 改造）／层2 容差（GPU）／层3 排名严格"三段制有公开依据；**禁止**用"GPU 天然不等价"作免验理由（B1 明说差异不是错误证据，因此必须由容差线+排名线自己说话）。

### 结论 C：数据面 GPU（cuDF/pandas-on-GPU/Polars-GPU）收益带 = 个位数到数十倍，且**本机 OS 是硬约束**

| # | 来源 | 证据 |
|---|---|---|
| C1 | [NVIDIA cuDF 官方页](https://developer.nvidia.com/cudf)（访问 2026-09-25） | 官方口径："Accelerate Pandas by up to 50x"、"Run Polars GPU Engine for up to 10x Speed Up"、"Run Apache Spark Workloads 5x Faster"；受加速操作具名 = "I/O and SQL operations—like joins, aggregations, sorting, and shuffles" |
| C2 | [Portfolio optimization 9X faster with RAPIDS](https://www.pyquantnews.com/the-pyquant-newsletter/portfolio-optimization-9x-faster-with-rapids)（PyQuant News，作者 Jason Strimpel，**2025-02-08**） | "we'll see a 9X performance speed up over pandas on CPUs"、"~9X faster with cuDF-pandas"——对象是均值-方差优化的收益计算/协方差/矩阵求逆 |
| C3 | [RAPIDS 安装文档](https://docs.rapids.ai/install)（重定向至 [docs.nvidia.com/datascience/install/](https://docs.nvidia.com/datascience/install/)，Stable 26.08，访问 2026-09-25） | 支持面="Linux distributions with glibc>=2.28" 或 "Windows 11 using a WSL2 specific install"；**原生 Windows 部署不被支持** |
| C4 | [CuPy 安装文档](https://docs.cupy.dev/en/stable/install.html)（访问 2026-09-25） | 二进制安装覆盖 **Linux 与 Windows**，CUDA 12.0–13.2、Python 3.10–3.14；**未声明与 NumPy 完全 API 平权**（"is based on NumPy 2.3 and SciPy 1.16, and has been tested against the following versions"） |
| C5 | [pola-rs/polars README](https://github.com/pola-rs/polars)（MIT，39,858 stars，pushed 2026-09-25） | "GPU support: optionally accelerate queries on NVIDIA GPUs"（其 GPU 引擎后端即 cuDF，受 C3 同一 OS 约束） |

→ **对本项目的含义（决定性）**：宿主=Windows 原生（本项目仓库与在飞 T1 均跑在 Windows，ClickHouse 在 HyperV VM），故 **cuDF/Polars-GPU 不在"零改环境"可选集内**，L2 载体只能是 Windows 原生可装的 **CuPy（MIT）** 或已装但当前为 CPU 版的 PyTorch（换 CUDA 构建）／numba.cuda（BSD，已装）。

## 二、逐项卡片（含许可证与成熟度，全部 GitHub API 2026-09-25 实核）

| 件 | 许可证/stars/pushed | 与本项目关系 | 评级 |
|---|---|---|---|
| [Heerozh/spectre](https://github.com/Heerozh/spectre) | **GPL-3.0** / 826 / 2025-04-15（休眠） | PyTorch+CUDA 因子引擎＋组合回测；README 实测口径：Quandl 5 年 3,196 标的 3,637,344 bar，i9-7900X + RTX 3090/2080 Ti，vs zipline.pipeline **最高 77.7x**（多指标 rank 组合）；自述"normally using float32 for GPU performance"并警告全 bar 一次算=**look-ahead bias 风险需自带测试** | 仅借鉴思想（**GPL 传染=禁采码**；float32 与本项目对拍纪律冲突；数据源 QuandlLoader 停更） |
| [microsoft/qlib](https://github.com/microsoft/qlib) | MIT / 48,844 / 2026-09-22 | A 股友好（`limit_threshold`、T+1 式撮合语义在 exchange 层）；回测核 CPU | 参考架构（其数据面板/工作流/成本与换手约束建模方式对③文掩码语义对拍有用） |
| [nkaz001/hftbacktest](https://github.com/nkaz001/hftbacktest) | MIT / 4,777 / 2025-12-23 | L2/L3 订单簿重放＋排队位＋延迟建模，Numba/Rust CPU | 直接用（但对象=未来 tick 回放语义对表，非本战役 GPU 重写；本仓 L07 SKEL §5 已采其语义） |
| [rapidsai/cudf](https://github.com/rapidsai/cudf) | Apache-2.0 / 9,763 / 2026-09-25（极活跃） | 数据面 GPU 首库；**Windows 原生不可用** | 参考架构（若未来经 WSL2/Linux 侧车，可承接"掩码构建=join/比较"的 GPU 化） |
| [cupy/cupy](https://github.com/cupy/cupy) | MIT / 12,343 / 2026-09-23 | NumPy 直译 GPU，Windows 有二进制 | **直接用（L2 首选载体）** |
| [numba/numba](https://github.com/numba/numba) | BSD-2-Clause / 11,160 / 2026-09-24（本仓已装） | `@cuda.jit` 核 + CPU 同源语义；NVIDIA 交易模拟文（B4）即用此路径 | 直接用（kernel 载体候选，**未在本机实跑 GPU——T1 单卡独占**） |
| [pola-rs/polars](https://github.com/pola-rs/polars) | MIT / 39,858 / 2026-09-25（本仓已装 1.41.2，20 线程） | 本机实测对同形面板工作负载**不优于 pandas**（0.43s vs 0.35s，见①文 R5） | 不采（作为本热点的解法被实测否定） |
| [nautilus_trader](https://github.com/nautechsystems/nautilus_trader) | **LGPL-3.0** / 29,385 / 2026-09-25 | 事件驱动生产引擎，零 GPU | 参考架构（口径真源候选，非加速候选） |
| [DarkLink/QuantPits](https://github.com/DarkLink/QuantPits) | NOASSERTION / **17 stars** / 2026-09-12 | API 实取描述="An advanced, production-ready quantitative trading system built on top of Micros…"（**并非"GPU 暴力组合回测"**） | 待验证→仅登记边界（前一轮描述有误，见 §四 更正2） |

**JAX / taichi 两向（前一轮有断言，本窗口证据不足）**：JAX 作为回测 GPU 后端的**一手来源**本窗口未取到合格引文（vectorbt PRO 页面复核失败＝§四 更正1）；taichi 的金融回测案例前一轮称"搜索实证结果全为图形/物理仿真"，本轮未重复检索 → 两条均降级为**待验证**，不入图、不作为裁定依据。

## 三、A 股适配闸（逐条检验，非笼统"可移植"）

| 外部件/做法 | T+1 | 涨跌停/不可成交 | 散户主导（无做市商连续报价） | 检验结论 |
|---|---|---|---|---|
| qlib `exchange.py` 撮合 | 以 `deal_price`+收盘口径近似日间成交 | **有**：`limit_threshold` 判不可交易（源码核） | 无排队位（与本项目考尺一致） | **可直接对齐**：与本项目 `_c4_engine.apply_fillability_gate` 同一类控制，可作对拍语义参考 |
| hftbacktest | 不适用（其假设可日内回转） | 排队位模型不含 A 股"封单不可成交"语义 | 不适用（其面向做市/连续报价） | **需改造**：仅借 per-symbol 独立流并行切法与 tick 回放语义（L07 已登记） |
| Spectre 因子面板 | 面板式持仓日频=天然 T+1 兼容 | 无内建涨跌停闸（靠使用者自备 mask） | 兼容（top-N 截面组合） | **需改造**：本项目掩码语义必须自持（E7 引擎洞修复已在真源：`_c4_engine.py:326-369`） |
| cuDF/Polars-GPU 数据面 | 与语义无关（ETL 层） | 与语义无关 | 与语义无关 | **可即用**（若 OS 允许），但按①文实测，本项目数据面仅占单格 0.07%，**不是杠杆** |
| arXiv:2507.07107（A 股多因子，2025） | 截面日频=兼容 | **核心贡献即"日线限价不可成交收盘价必须在使用前掩掉"**，否则滚动统计静默污染（其结论：mask 是表现差异的主导因子） | 明确针对中国 A 股散户市场结构 | **同题文献**：直接支撑④文"掩码边界条件"作为一等验证对象；其 GPU 化=213 因子 PyTorch `unfold` 批算，报 **51x vs pandas** |

## 四、对前一轮结论的更正（诚实记录，防后人按旧引文施工）

1. **"vectorbt PRO 的 GPU 路线=换 JIT 后端到 JAX"** —— 本轮直取 [Performance 页](https://vectorbt.pro/features/performance/)（2026-09-25）只看到 NumPy/Numba/Rust 三后端，检索具名短语亦未命中官方页 → **改判：待验证（不入图）**。影响：③文 L2 载体推荐不再引用 vectorbt PRO 作为"JAX 回测可行"的背书。
2. **"QuantPits = GPU 暴力组合回测"** —— GitHub API 实取描述无 GPU 字样、17 stars、许可证 NOASSERTION → **改判：仅登记边界，不采**。
3. **受阻记录（不编造替代引用）**：①[blogs.nvidia.cn 宽邦科技 RAPIDS 案例](https://blogs.nvidia.cn/blog/kuanbang-technology-accelerating-ai-with-nvidia-rapids/) 取回 404（原搜索快照命中、正式链接失效）→ 商业 A 股 GPU 实践这一脉**本窗口受阻**，只留 PyQuant News（C2）与 cuDF 官方页（C1）；②`rapidsai/cudf` releases 页经代理取回 403；③Polars 官方 GPU 用户指南页 `docs.pola.rs/user-guide/gpu/` 404（README 表述已足够，标单源→待验证其"限制清单"细节）；④中文 A 股回测性能/掩码文章全部落在 CSDN/聚合站与营销号，按闸1 一律不采。
4. **单源结论登记**：NVIDIA B4 的 "114x（一个月时间跨度，H200）"与"路径并行×时间串行几何"目前**只有 1 个一手来源** → 状态=待验证，只可作"量级参照"，不可作收益承诺依据（⑤文 N4/Phase 4 立项线已按此约束写）。

## 五、六向台账（本件）

| 向 | 内部反查 | 全网搜索 |
|---|---|---|
| ①上游 | 反查本项目喂入面（CH 四表+行业锚）→ 业界同类"面板+约束表"装载方式（qlib 数据层/Arctic 类）只作对照 | 搜 "market data lake GPU columnar backtesting data loading"→ 合格来源仅 cuDF 官方页的 joins/aggregations 具名项（C1）；余为聚合站→查无 |
| ②下游 | 反查本仓 GPU 战役文档族真源：`03_gpu_campaign.md`（现行跑批+守望）、`19_gpu_plan`（三档）、`fullflow_mining/m2_backtest_sim/04_gpu_matrix.md`（六向环节图）→ 本文只补"外部方案全景"一维，**不另立清单**（内收：与 `gpu_landscape.md` 合并为本文） | 搜 "GPU 回测 商业机构实践 2025"→ PyQuant News（C2）+ cuDF 官方（C1）+ 404 一条（受阻） |
| ③算法/机制 | `capability_lookup` 语义=Grep 仓内已装依赖：torch(CPU 版钉)/numba/polars 在位，cupy/cudf/jax 不在位 | 主结论 A/B/C 全部外部（见 §一），关键结论各 ≥2 独立来源 |
| ④后端 | `requirements.txt:5-10`（torch CPU-only 裁定钉）+ `find_spec` 实盘核 → L2 需新依赖且需重签 torch 构建或引入 CuPy | GitHub API 元数据 + 官方 install 页（C3/C4/C5）实核许可证/活跃度/OS 支持 |
| ⑤前端 | 反查"业界如何呈现 GPU 迁移收益"→ 本项目 grid 无前端读端（①文⑤向已查无），仅登记 MLflow/W&B sweep 惯例为长尾矿 | 搜 sweep 结果呈现（未深挖，判为邻域有归属：仪表盘属前端车道）→ 只登记边界不越界 |
| ⑥数据字段 | ①文⑥向已逐字段核对（7/7 present + NULL 0.058%）→ 外部字段口径仅需"涨跌停价定义"，由 arXiv（A 股同题）+ qlib 参数名交叉印证 | 搜 "limit_threshold A股 涨跌停 定义"（qlib 源码 + arXiv 两条合格） |

## 六、挖矿日志（本件）

| 轮 | 矿脉 | 判定 | 关键产出 |
|---|---|---|---|
| R1 | 开源框架是否已有 GPU 回测核 | signal | 结论 A（4 来源）＋qlib exchange.py 的 `limit_threshold` 实源码核 |
| R2 | GPU/CPU 数值等价与确定性公开口径 | signal | 结论 B（4 来源，含 2026-03-05 CCCL 新文与 v13.4 CUDA FP 文档） |
| R3 | 数据面 GPU 收益带与 OS 可行域 | signal | 结论 C（cuDF/PyQuant 9x；RAPIDS 不支持原生 Windows；CuPy 支持 Windows） |
| R4 | A 股特有约束的外部同题文献 | signal | arXiv:2507.07107（2025）51x + 不可成交掩码为主因——**本轮最有价值单条** |
| R5 | 前一轮引文复核（vectorbt PRO JAX / QuantPits） | signal（否定性） | §四 更正1/2：一条降"待验证"、一条改判"不采" |
| R6 | 商业机构 A 股 GPU 实践 | 受阻 | NVIDIA 中文博客 404 + cudf releases 403 → 如实记录，不用聚合站凑数 |
| R7 | JAX/taichi 作为回测载体 | 待验证 | 本窗口未取到一手合格来源 → 不入图（前一轮断言降级） |
| 长尾 | 未挖 | — | ①NVIDIA 之外（AMD ROCm）GPU 回测生态；②RAPIDS 在 WSL2 下与本项目 ClickHouse(HyperV VM) 共存可行性实测（涉 GPU 作业，T1 独占期内禁做）；③Spectre 之外 GPL 因子库扫描 |

## 七、挖后自审闸（三态裁定）

- **主判据**：本文消灭的人工环节="凭印象断言业界怎么做"（本轮即抓出前一轮 2 条不可复核引文＋1 条描述有误）；终局全貌里"外部方案情报"必须是带访问日期、可复跑、可证伪的台账，而非一次性叙述。
- **终局位置**：有（本文与 `research_notes/` 类外部情报册同族，后续并入时按内收原则合流）。
- **裁定**：**挂起排期**——挖矿本身已完成到"矿脉枯竭 + 长尾清单"状态，但本文唯一需要"再挖"的两条长尾（ROCm 生态、WSL2+RAPIDS 共存）**都要求起 GPU/系统作业**，解锁条件=在飞 T1/T2 完赛且 Owner 批 GPU 空窗；在此之前不投入。
- **反驳者一问**：①"业界没人做 GPU 回测核，是否说明本矿方向错？"→ 不对，本项目热点已被①文重定义为"重复掩码重建 + 单核串行"，GPU 只在 L1 之后按⑤文 N 线判定；②"外部结论这么多，是不是过度调研？"→ 三条主结论各 ≥2 来源且都直接改变设计决策（OS 约束、对拍口径、自研 vs 改造），非装饰性引用；③"51x/114x 能否当承诺？"→ 已显式标注为量级参照＋单源待验证。
- **封矿线**：本矿（业界全景）在"不起 GPU 作业"边界内已见底；剩余长尾登记在 R 表，不视为枯竭之外的未挖项。
