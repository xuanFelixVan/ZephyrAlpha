---
ttl: task_bound
title: GPU 重写五册双版合并审计（A 版矿脉证据并入 B 版＋五件指针改真）
created: "2026-09-26"
session: st-qmine-20260925
lane: LANE-GPU（双版合并收口）
---

# GPU 重写五册双版合并审计

> 车道＝LANE-GPU 收口执行｜总筹＝st-qmine-20260925｜A 版真身＝已落 HEAD 的 commit `37aeecedcd`（五件 488 行）｜B 版＝盘上新写未落五件。
> 本件性质＝案卷（不是裁定）：只记"实测事实＋并入落位＋遗留点"，取代关系与门的放行由总筹与 LANE-LAND2 判定。

## 零、前提复核（grep 实测，两方自述都不采信）

合并前对 B 版五册逐词 grep（词频实测，非印象）：

| 复核项 | 总筹指称 | 合并前实测（B 版五册） | 判定 |
|---|---|---|---|
| `qlib` | 找不到 | `industry_gpu_landscape.md` 6 处（含 `exchange.py` 源码级取证）＋①③④各 1 处 | **指称不实**（在位，但"GPU 只覆盖 ML 层、回测面 Exchange 无 GPU"的**分层表述**缺） |
| `vectorbt` | 找不到 | `industry_gpu_landscape.md` 5 处 | **指称不实**（在位，但**开源版 stars／NOASSERTION 许可证／Numba CPU JIT** 三项缺） |
| `nautilus` | 找不到 | `industry_gpu_landscape.md` 2 处 | **指称不实**（在位且证据强于 A 版） |
| `hftbacktest` | 找不到 | `industry_gpu_landscape.md` 3 处 | **指称不实**（在位），但 A 版**三连细证（README 271 行 grep／教程页 233KB grep／PyPI v2.4.4 `requires_dist` 仅 numba）缺** |
| `LEAN` | 找不到 | **五册零命中** | **指称成立——真缺口** |
| `1/64` | 找不到 | 仅③文 1 处（第 95 行），④⑤文零命中 | **半成立**：红线在③文，但**容差线真源位（④文）没有**，读④文者不知"为何必须 FP32" |
| FP32／1e-5／1e-8／2bp | 找不到 | ④文 §二 层2 全组在位 | **指称不实**；唯 **ann_return 的 0.005 未单列**、**A 版 1,650 日预检窗口口径未记** → 已补 |
| "每格 7 次引擎 pass" | — | ①文只有"7 个 pass（若有扫描）"一句，**无 7 的构成**；"83% 的一半是重复"零命中 | **成立**——两条量化口径缺 |
| 18GB／单卡独占／`exclusive_group=gpu_default` | — | ①③⑤文在位（⑤文 §〇＋N5/N6＋R6） | **成立在位**，逐字核数值一致（18GB=`03_gpu_campaign.md:24`；峰值 7–8GB=wo_gpu02 工单件）→ **不重复堆叠** |

→ **本车道判定**：真缺口 6 项（LEAN／hftbacktest 三连证／vectorbt 三项元数据／④文缺硬件红线／①文缺两条口径／ann_return 容差单列）。
总筹指称的"五家全无""容差全无"两条**过判**，本件如实记双面，**不据此推翻 B 版五件的真源地位**（B 版仍是唯一真源，文件名与章节结构未动）。

## 一、五条必并落位总表（一条不许漏 → 已逐条打钩）

| # | 必并项 | 落位（B 版文件＋节，含合并后行号） | 状态 |
|---|---|---|---|
| 1 | A②文 逐家实证表（五家各带 URL／发布方／年份／stars／许可证）＋总结论一句话 | `industry_gpu_landscape.md` **§一「结论 A 补 · 五家现成框架逐家实证表」**（l.30 起，表 l.36-42，总结论 l.45） | ☑ |
| 2 | A④文 容差冻结值＋FP32 累积误差定量预检 | `verification_framework.md` **§一·补**（l.32 起，冻结值表 l.46-56，预检 l.58 起）＋**§二 层2 行内补 ann_return**（l.70） | ☑ |
| 3 | 硬件红线（1/64→FP32＋容差路线；18GB／单卡独占／与本地 LLM 互斥） | `verification_framework.md` **§一·补 前半**（l.36-44，就近择此件为真源位；③文 l.95、⑤文 §〇/N5/N6/R6 原有条同已核一致，未重复堆叠） | ☑ |
| 4 | A①文 两条量化口径（7 pass 构成；"83% 的一半是重复而非算力"→hoisting 3-7x） | `hotspot_census.md` **§二·补 重复计算结构的量化口径**（l.71 起：口径①表 l.78-86，口径② l.87-96） | ☑ |
| 5 | 五件指针：删 `doc_type: index`、留 `ttl: task_bound`；核 `superseded_by:` 是否名副其实，不具名者改"部分并入＋余下见 commit" | 五件指针全部改真（详见 §三）；附带清除 B 版五件的 `doc_type`（防 EXEMPT-ZONE-FM 打死整袋） | ☑ |

## 二、并入证据台账（A 版原文行号／引文片段 → B 版落位）

> **行号口径（重要）**：本表与所有 B 版新增节里出现的 `compute_inventory.md:NN`／`validation_framework.md:26` 等行号，
> **一律指 commit `37aeecedcd` 的 blob 行号**（盘面同名文件现已是 22-26 行的指针件，行号不可混用）。
> 取原文：`git show HEAD:docs/_working/gpu_rewrite/<文件>`。

### 并 1 · 逐家实证表 → industry_gpu_landscape.md §一「结论 A 补」

| A 版原文行号 | A 版引文片段（摘） | 并入后的落位 |
|---|---|---|
| `gpu_landscape.md:16-20` | "qlib（microsoft/qlib）——MIT，活跃（pushed 2026-09-22，48.8k stars）…GPU 加速只覆盖 **ML 模型层**；回测面（Exchange 模拟＋`NestedExecutor` 日内→日间双层执行）是纯 CPU pandas…业界最主流的 AI 量化平台**选择不为回测核做 GPU**" | 表第 1 行（URL×2：GitHub＋官方 backtest 文档 `qlib.readthedocs.io/en/v0.5.1/component/backtest.html`；两版 stars 并列 48.8k／48,844） |
| `:22-26` | "hftbacktest（nkaz001，MIT，4.8k stars，pushed 2025-12-23）…实证三连：①README 全文 **271 行零 GPU/CUDA 字样**；②官方 'Accelerated Backtesting' 教程页 **233KB** 全文零 GPU/CUDA；③PyPI **v2.4.4 `requires_dist` 仅 `numba~=0.61`**…真正的强项：**L2/L3 tick 级全订单簿重建＋限价单排队位＋延迟建模**" | 表第 2 行（三连细证逐字入格；docs URL 保留） |
| `:28-32` | "vectorbt 开源版（polakowo/vectorbt，**自定义许可证 NOASSERTION**，9.2k stars）：**Numba CPU JIT 加速，无 GPU**" | 表第 3 行（vectorbt.dev＋GitHub 双 URL；并注明 PRO 的 JAX 说已由 B 版 §四 更正1 降为待验证） |
| `:60` | "nautilus_trader/backtesting.py/**LEAN 均无 GPU 回测模块**（2026-09 搜索实证）" | 表第 4、5 行——**LEAN 行系本次新增（合并前五册零命中该词）**；nautilus 行注明 B 版 A2 取证更强（README 零 GPU/CUDA/RAPIDS＋官方 AI/ML out of scope） |
| `:64-70` | 裁定五条：理由2 "没有现成框架有 **GPU 回测核**（qlib/vectorbt/hftbacktest/nautilus/LEAN 五家实证全 CPU）——改造现成框架改造不出 GPU，只能改造出又一个 CPU 引擎"；理由5 许可证风险面（Spectre GPL-3.0 传染／vectorbt PRO 闭源付费／开源 vectorbt NOASSERTION／自研＋CuPy MIT＋numba BSD=干净） | 该节末"总结论（一句话）"＋许可证面依据段 |

**诚实标注（不硬造成全量）**：LEAN 一项 A 版仅给"无 GPU 回测模块"的搜索实证结论，**未记 URL／stars／许可证／年份**；B 版合并前整家缺失。本车道**不凭记忆补元数据**，在表内标"两版均未实取→待验证，属长尾复采义务"。

### 并 2 · 容差冻结值 → verification_framework.md §一·补（＋层2 行）

| A 版原文行号 | A 版引文片段 | 核账与落位 |
|---|---|---|
| `validation_framework.md:26` | "net 序列逐日相对容差 ≤**1e-5**（FP32 路径）／≤**1e-8**（FP64 路径）；**sharpe/ann_return 绝对差 ≤0.005**；max_drawdown 相对差 ≤1e-4；期末净值差 ≤**2bp**" | 冻结值表 7 行逐条核：net／mdd／2bp／离散量四项**B 版原已逐字一致**（未改一字）；**ann_return 的 0.005 系本次补入 §二 层2 判据格**（合并前该格只具名 sharpe） |
| `:26` 末 | "离散量精确一致：交易/持仓信号、持仓只数、调仓日集合、五档门 PASS/FAIL **必须 100% 一致**（signals/trades exact match, floats tolerance）" | B 版 §二 层2"离散量 100% 一致"格在位，值一致 |
| `:28` | "FP32 累积误差的定量预检（施工前跑一次）：**1,650 日 cumprod 的 FP32 vs FP64 期末净值差实测——若 >2bp，L2 精度策略升级为'关键累计段 FP64'，容差表随之重签**" | §一·补 末段整段入档；并记两版窗口口径差：A=1,650 交易日（`compute_inventory.md:37`），B①文实测=**1,622 评估日**（含预热 1,757 行）→ **预检按 1,622 跑，1,650 作历史口径存档**（差＝窗口切法，非结论冲突）；⑤文 N4 同一条已核一致 |
| `:27` | "此为**建议判据 (建议)**，Owner 可调" | B 版 §二 表头"(建议线，Owner 可调)"一致，且 B 版 R6 另记"全仓无引擎间浮点容差先例" |

### 并 3 · 硬件红线 → verification_framework.md §一·补 前半

| A 版原文行号 | A 版引文片段 | 落位 |
|---|---|---|
| `compute_inventory.md:14` | "**注意 3090 的 FP64 吞吐是 FP32 的 1/64——精度选型是 L2 设计的第一约束**" | §一·补 首条（并注：③文 l.95 原有同一条，保留不重复堆叠；证据等级＝硬件规格推演、本机未做 GPU 实测，③文 R6 已标待验证） |
| `rewrite_architecture.md:12` | "RTX 3090 24GB，**FP64 吞吐≈FP32 的 1/64**——'整卡搬 float64'会把 GPU 打回 CPU 水平" | 同上（"故必须走 FP32＋对拍容差路线"即 A 版口径） |
| `rewrite_architecture.md:50` | "默认 **FP32 计算＋FP64 CPU 对拍容差**…提供 FP64 fallback 开关（吞吐掉到 ~1/64，仅仲裁争议格时用）。禁 TF16/TF32" | §一·补＋B 版 §一 禁止项（禁 TF32/FP16 两侧一致） |
| `compute_inventory.md:14` 前半＋`roadmap.md:56` | "显存配额 **18GB**（`03_gpu_campaign.md:24`）"＋N6"all_a 波稀疏化后显存仍 >18GB 配额→缩批降波而非买卡" | ⑤文 §〇/N6 **本已在位**（逐字核一致），本件 §一·补 落一份并注明单卡独占（prereg `vram.concurrency: 1`）与**本地 LLM 硬顶互斥（`exclusive_group=gpu_default`，Kronos 夜窗 7–8GB 先例）** |

### 并 4 · 两条量化口径 → hotspot_census.md §二·补

| A 版原文行号 | A 版引文片段 | 落位与实测关系 |
|---|---|---|
| `compute_inventory.md:40` | "**结构性重复计算**：①每档全量重算 reindex/pct_change/涨跌停闸/gross/turnover，而档位间唯一差异是 `cost = turnover*(...+slip*2)/1e4` 一行标量乘；②`apply_fillability_gate` 每次 pass 重查 CH 两次＋Python `iat` 逐行循环建掩码（无缓存），`factory_grid_executor.py:777-778` 又使每格 run_backtest+daily_net_returns 各跑一遍＝**每格 7 次引擎 pass**" | 口径①表（四行：档位间 5／两连调 +2／掩码零缓存＝14 次 CH 往返＋7 次全量行循环／合计 7），逐行标 B 版实测对应项（L2-c／L2-b／L1-a·b·d）与**必须限定**："在飞 T1 未开 per-point 档位扫描→现网真实 pass=2，'7' 是扫描全开口径" |
| `rewrite_architecture.md:17-20` | "当前每格跑 **7 次引擎 pass**，其中结构性冗余占大头"（三处冗余分述） | 同上（引文片段入表"前一轮原文"列） |
| `compute_inventory.md:176` | "**83% 热点的一半其实是'重复'不是'算力'**：每格 7 次引擎 pass 中，档位间/函数间可共享的部分占大头——L1 hoisting（不碰 GPU）先吃掉结构性浪费，GPU 只该吃剩下真正的算力账" | 口径②（原文逐字入档＋两条实测改判：83% 分母口径不成立；"重复"定性成立且被加强，主体是掩码重建重复而非档位张量） |
| `rewrite_architecture.md:42` | "**预估 3-7x**（35.33s→5-12s/格）；施工前先跑一次 cProfile 定分位数" | 口径②（前一轮非 GPU 提速线 3-7x 原样入档；实测改判为 **8.6x（现状口径）／16.6x（扫描口径）**，并注明 A 版自设的 cProfile 前置已由①文完成） |

### 并 5 · 五件指针改真（详见 §三）

## 三、指针改真与门位防死（附）

**A. 五件指针逐件判定**（`doc_type: index` 全部删除、`ttl: task_bound` 保留、`superseded_by:` 逐件核过内容确在案）：

| 指针件 | 后继件 | 本车道判定 | 残留（若有，逐条点名＋commit 行号） |
|---|---|---|---|
| `compute_inventory.md` | `hotspot_census.md` | **全量并入**（F1–F13 族清单＋锚定事实表＋普查结论三句话＋两条量化口径＋硬件锚） | 无（"稀疏 ≤2GB"等被实测判否项在①文 §三/§四 记着判否理由） |
| `gpu_landscape.md` | `industry_gpu_landscape.md` | **部分并入**（五家实证表＋总结论＋来源清单已在案） | **3 条**：①cuDF 数值扫描 ~30x／rolling 仅 ~2x(A6000)；②Polars GPU 表达式覆盖有洞（PyData London 2025）；③JAX PureJaxRL 33M steps/s。→ 见 commit `37aeecedcd` 的 `gpu_landscape.md:43,44,52`（本车道不为其补证，指针已写明不得引本件为据） |
| `rewrite_architecture.md` | `rewrite_architecture_three_tiers.md` | **全量并入**（L1 改动面/数据流/bitwise 验证/1-2 天工时；L2 面板驻留与显存推演；L3 边界；Phase 序） | 无（两处改判"稀疏 ≤2GB 撤回""cuDF→CuPy 单选"＝有意改判，理由在③文） |
| `roadmap.md` | `migration_roadmap.md` | **全量并入**（Phase 序与回滚点、N1–N6 逐条对应、一页节奏、总闸"产出密度决定 GPU 命运"） | 无（②' 分片"2 进程 ~2x"→"2–4 进程内存决定"＝实测改判，在⑤文 Phase 1） |
| `validation_framework.md` | `verification_framework.md` | **全量并入**（三层判据、容差冻结值、边界格 7 类→E-1…E-10 超集、fail-closed 与 FP64 仲裁、框架自身止损线） | 无（两句二手依据 1e-8~1e-6"业界通行"与"cuFFT determinism"＝取证升级替换，已写明不冒充依据） |

**B. 附带防门死修正（超出必并清单，但属"让本袋真能落地"的最小动作，如实报备）**：
`EXEMPT-ZONE-FM`（`src/zephyr/gov_enforcement/commit_gates/exempt_zone_frontmatter_gate.py`，priority=87，**pre-commit 阻断型**）判据＝
豁免区（`docs/_working/` 等）文件若 **HEAD 不存在（新件）** 且 frontmatter 带**非空 `doc_type`** → 阻断。
按此判据：五件指针（HEAD 已存在）原 `doc_type: index` 属"历史违规跳过"，删之是规范要求而非放行需要；
但 **B 版五件全部是新件且带 `doc_type`（audit_report／blueprint／architecture_view）→ 必被该门打死**，本袋 10 件一个也落不了地。
故本车道把 **10 个 .md 的 `doc_type` 行一并清除**（只动 frontmatter 一行，正文零损失，LF 行尾保持；本件与 `lane_gpu.yaml` 同规矩不带 doc_type）。
**此为对前一轮指针里"后继件已按受控词表取值"一句的纠偏**：受控词表取值在正式区才对，豁免区反而禁止——该句已随指针改写删除。

**C. 十条关键事实覆盖表**（前 5 条＝必并项；后 5 条＝本车道自 A 版再抽的最硬论断）：

| # | A 版关键事实（行号） | B 版是否存活 |
|---|---|---|
| 1 | 五家现成框架回测核全 CPU，改造不出 GPU；自研薄核＋CuPy 正解（`gpu_landscape.md:67`＋`:64-70`） | **补入后存活**（②文 §一 结论 A 补；LEAN 此前整家缺失） |
| 2 | net 逐日 ≤1e-5（FP32）／≤1e-8（FP64）等容差冻结值（`validation_framework.md:26`） | **存活＋补入**（值 B 版本已在案；ann_return 0.005 本次补单列，§一·补 冻结表 7 行核账） |
| 3 | 3090 FP64=FP32 的 1/64→必须 FP32＋容差路线（`compute_inventory.md:14`＋`rewrite_architecture.md:12`） | **补入后存活**（④文 §一·补 落为容差线的"因"；③文原有同条保留） |
| 4 | 每格 7 次引擎 pass 的重复结构（`compute_inventory.md:40`） | **补入后存活**（①文 §二·补 口径①，含"真实 pass=2"限定） |
| 5 | 83% 热点的一半是重复而非算力→hoisting 3-7x（`compute_inventory.md:176`＋`rewrite_architecture.md:42`） | **补入后存活**（①文 §二·补 口径②，实测上修 8.6x/16.6x，原值在案） |
| 6 | Spectre＝GPL-3.0 传染禁采码＋float32 设计＋README 自认 look-ahead 需自带测试＋77.7x@RTX 3090（`gpu_landscape.md:34-38`） | **存活**（②文 §二 表行 1，硬件与年份口径更细） |
| 7 | arXiv:2507.07107（2025-07）：A 股日线限价不可成交价必须掩掉，否则滚动统计静默污染；`torch.unfold` 因子批算 51x（`:58`） | **存活**（②文 §三 表末行＋R4；并升为④文 E-1/E-2 的学术同题证据） |
| 8 | NVIDIA Developer Blog 2025-03-04（Mark J. Bennett）Numba CUDA MC **114x@H200**，几何＝千级路径并行×时间步串行；**且"此文不是 hftbacktest"**（`:57`） | **存活但降级**（②文 B4 一手源引用＋§四.4 因单源改判"量级参照、不得作承诺"＝有意降级非丢失；归属辨伪无需搬运，B4 已正确挂 NVIDIA） |
| 9 | "重写对象是**一个核**不是一堆系统"——`_c4_engine.py:439-458` 二十行数学（`compute_inventory.md:175`） | **存活（口径已更正）**（③文总纲扩为 `:325-458`＝掩码构建＋两函数体，实测证明掩码才是核的主体） |
| 10 | 整装引擎（IBT `vectorized_engine`＋`matching_logic`）＝口径真源，**IBT-D01 双口径未收口前禁动**（`compute_inventory.md:118`＋`rewrite_architecture.md:11`） | **存活**（③文 l.16 逐条："三层均不改"，IBT-D01 挂⑤文 Phase 5 前置） |

覆盖合计：必并 5 条全部落位（其中 3 条为补入、2 条为"已在案＋核账补细"）；自抽 5 条中 3 条原样存活、1 条存活但经单源降级、1 条存活且口径更正。A 版被删而未在案的仅剩 `gpu_landscape.md:43,44,52` 三句二手 benchmark（已在指针里点名为"部分并入"）。

## 四、纪律自证与总筹复核命令

**纪律**：只读分析＋写文档；零 `git add`／`git commit`／`git push`，未跑 `scripts/git_commit.py`／`commit_queue.py`（唯一落地出口＝LANE-LAND2）；
未跑测试、未起 GPU 作业（连 `torch.cuda.is_available()` 都未打，避免建 CUDA context 占显存）、未碰 PID 3584 与 `D:\zephyr_t1_backup\`；
未新建第六第七册（GPU 家族＝五件真源＋五件指针，内收）；未删 A 版任何内容（HEAD `37aeecedcd` 可全量取回）；
未伪造 Owner 署名或裁定号（正文一律以 commit 号／文件行号指代，无裸"裁定#数字"写法）；主区 index 未做 `git add -A`。

**改动面（11 件，全为文档）**：B 版五件新增节（①§二·补／②§一 结论 A 补／④§一·补＋层2 行）＋A 版五件指针改写（含 frontmatter）＋本件＋`landing/lane_gpu.yaml`；
其余文件零触碰。三件带 `supersedes:` 声明的后继件（①②④）已在该字段补记本次合并，使取代声明可核。

**总筹复核命令**（只读，逐条可跑）：

```
git show HEAD:docs/_working/gpu_rewrite/gpu_landscape.md | sed -n '16,33p;60,70p'   # 并 1 的 A 版原文
grep -n "LEAN\|271 行\|NOASSERTION" docs/_working/gpu_rewrite/industry_gpu_landscape.md
git show HEAD:docs/_working/gpu_rewrite/validation_framework.md | sed -n '26,28p'   # 并 2/3 的 A 版原文
grep -n "1/64\|ann_return\|18GB\|exclusive_group" docs/_working/gpu_rewrite/verification_framework.md
git show HEAD:docs/_working/gpu_rewrite/compute_inventory.md | sed -n '14p;40p;176p'
grep -n "每格 7 次引擎 pass\|重复'不是'算力\|3–7 倍" docs/_working/gpu_rewrite/hotspot_census.md
grep -rn "^doc_type" docs/_working/gpu_rewrite/    # 期望：无输出（10 件 doc_type 已清）
python -c "import sys; sys.path.insert(0,'src'); from zephyr.gov_enforcement.commit_gates.exempt_zone_frontmatter_gate import make_exempt_zone_frontmatter_gate"  # 门的真身（可选）
```

**待总筹／LANE-LAND2 定夺三件（本车道只登记不代裁）**：
①`gpu_landscape.md:43,44,52` 三句二手 benchmark 是否要复采一手源入图（否则永久停在 git 历史）；
②LEAN 一家的 stars／许可证／URL 复采（当前标待验证，是②文表内唯一空洞）；
③前一轮 `lane_gpu.yaml` 曾向总筹呈报的三件待裁（Phase 序／CuPy 新依赖出厂／①文三条口径是否回写 19 号文与 03 号文）本车道**未代改任何他道文档**，仍待裁。
