---
ttl: task_bound
title: GPU 重写挖矿①——全项目计算热点普查
created: "2026-09-25"
sid: st-gpu-rewrite-mining-20260925
family_id: GPU-REWRITE
evidence_grade: A-（全部仓内论断带路径行号；耗时数字带实测出处；未实测项明确标"估算"）
---

# ① 全项目计算热点普查（GPU 适合度分级）

> 使命：写任何 GPU 代码之前，先回答"项目到底有多少计算需要 GPU"。
> 评级口径：**A=批量独立计算共享同一数据面板（完美 GPU）｜B=部分可向量化/GPU 化｜C=I-O 或事件驱动或本已便宜（不适合 GPU）**。
> 硬件锚：RTX 3090 24GB（nvidia-smi 2026-09-25 实测：util 4%、显存 2.0/24.5GB）；显存配额 18GB（`docs/_working/decision_map_campaign/03_gpu_campaign.md:24`）。**注意 3090 的 FP64 吞吐是 FP32 的 1/64——精度选型是 L2 设计的第一约束**（详见③文）。

## 零、锚定事实（全部带出处）

| 事实 | 数值 | 出处 |
|---|---|---|
| 现役网格引擎 | CPU pandas 串行，一格一算 | `docs/_working/decision_map_campaign_20260924/19_gpu_plan_and_master_backlog.md:9` |
| 单格耗时 | 35.33s（T1 实测口径） | 同上 :15 |
| 热点占比 | 83% 耗时在五档成本扫描 | 同上 :9 |
| GPU 现状 | 仅当内存仓（1.8GB/利用率 1-7%） | 同上 :9 |
| 在跑批次 | T1 3,700 格（grid_20260924-213246）+ 完赛后 T2 900 格 | `docs/_working/decision_map_campaign/03_gpu_campaign.md:12-15` |
| 方案①两轮制 | T1 轻档 [0,5]bp 粗筛→T2 全档 [0,5,10,20,40]bp 终审 | `03_gpu_campaign.md:31` + `exam_cost_gate.py:100-117` |
| 方案②/③预算 | ②热点向量化 3-5x（1-2 天）；③GPU 重写 10x+（大工程，等产出密度） | `19_gpu_plan:16-18` |

---

## 一、计算族清单（13 族）

### F1 · 五档成本扫描（考尺链）——**本项目最大热点，GPU 适合度 A**

| 项 | 内容 |
|---|---|
| 入口 | `scripts/backtest/factory_grid_executor.py:797-818` → `run_cost_tier_scan`（`src/zephyr/backtest/regime_validation/exam_cost_gate.py:120-149`）→ `daily_net_returns`（`scripts/backtest/translated/_c4_engine.py:439-458`） |
| 数据规模 | 权重/收盘宽表 G 维度三档：hs300≈300 列、zz500≈500 列、all_a_ex_st≈5,000 列 ×≈1,650 交易日（`factory_grid_executor.py:154` 宇宙定义） |
| 当前耗时 | 每格五档 ≈29.3s（=35.33s×83%，`19_gpu_plan:9`）≈ **6s/档** |
| 调用频率 | 每格 5 次（全档）或 2 次（T1 轻档，方案①）× 3,700+900 格 |
| 当前瓶颈 | **结构性重复计算**：①每档全量重算 reindex/pct_change/涨跌停闸/gross/turnover，而档位间唯一差异是 `cost = turnover*(...+slip*2)/1e4` 一行标量乘（`_c4_engine.py:457`）；②`apply_fillability_gate` 每次 pass 重查 CH 两次 + Python `iat` 逐行循环建掩码（`_c4_engine.py:341-368`，无缓存，`factory_grid_executor.py:777-778` 又使每格 run_backtest+daily_net_returns 各跑一遍=**每格 7 次引擎 pass**）；③串行一格一算只吃 ~10 核（`19_gpu_plan:9`） |
| GPU 适合度 | **A**（格子间独立、共享同一数据面板；档位扫描 hoisting 后天然成批） |

### F2 · 单格回测核（考尺 run_backtest/daily_net_returns 本体）

| 项 | 内容 |
|---|---|
| 入口 | `factory_grid_executor.py:777-778`（两连调，语义重叠——run_backtest 的净收益序列就是 daily_net_returns 的返回值，`_c4_engine.py:424` vs `:458` 同式） |
| 数据规模 | 同 F1 |
| 当前耗时 | ≈6s/格（=35.33−29.3 中的引擎 pass 部分；另有 evaluate_recipe 见 F3） |
| 调用频率 | 每格 2 次（冗余 1 次） |
| 当前瓶颈 | CPU pandas + 涨跌停掩码重复构建（同 F1②） |
| GPU 适合度 | **A**（`(w.shift(1)*rets).sum(axis=1)` 与 turnover/cost 全是张量运算，`_c4_engine.py:419-424`——二十行数学，GPU 化薄核即可） |

### F3 · 策略网格求值（normalize/combine/sizing）

| 项 | 内容 |
|---|---|
| 入口 | `evaluate_recipe`（`factory_grid_executor.py:545-617`）；因子 `compute_v1_factors`（:242）；缓存已建：combine_cache T2c 前缀复用（:559-597）、slice_cache（:709） |
| 数据规模 | 同 F1 宽表 × 每格因子归一化/合成/rank/sizing |
| 当前耗时 | 含在 35.33s/格内（非 83% 热点，估算 3-8s/格量级） |
| 调用频率 | 每格（前缀命中时 combined/rank 复用） |
| 当前瓶颈 | pandas `rank(axis=1)`/rolling 在 5,000 列宽表上的 CPU 单线程 |
| GPU 适合度 | **B**（rank/sizing 可批量化但前缀缓存已削大半；优先级低于 F1/F2） |

### F4 · 做T材料线全算（t0_material_line，多周期做T语料）

| 项 | 内容 |
|---|---|
| 入口 | `scripts/backtest/t0_material_line.py`（头注 :1-45：M0 成交模型+周期重采样） |
| 数据规模 | 研究段分钟库 **1,147,018,314 行**；symbol-day **4,759,448** 个；5,410 只 × 975 日；语料 **≈282 万对/周期** × 5 周期（`docs/_working/decision_map_campaign/links/L05_t0/material_precapacity_report.md:23,94,§一`） |
| 当前耗时 | 全量 ≈**23.3h CPU**（抽样 20 只实测外推，同上 :23；A2 项同口径 `19_gpu_plan:29`） |
| 调用频率 | 每规则集一次（预注册卡冻结后重跑=另卡） |
| 当前瓶颈 | 逐 symbol 逐日 Python 循环（配对 build_pairs 逐日判断）；CH 分钟数据读取 I-O 占比可观 |
| GPU 适合度 | **A-**（symbol-day 间完全独立=天然并行；但 11.5 亿行 CH 读取是前置 I-O，GPU 只省算不省读；净收益=算法侧 10x+、端到端 3-10x 估算） |

### F5 · 做T全量×状态匹配引擎（相位×周期矩阵，L05-C04 语料消费面）

| 项 | 内容 |
|---|---|
| 入口 | 规划中（`17_quantified_acceptance.md:32` §三.1-2：周期集 {1,5,15,30,60}×5,853 只×两年，超 48h CPU 预算即强制分层） |
| 数据规模 | F4 语料 × 7 相位 × 5 周期格 |
| 当前耗时 | 未跑全量（容量预检 23.3h 为语料面；匹配矩阵另计） |
| 调用频率 | 每规则集/每相位轴重算一次 |
| 当前瓶颈 | 同 F4 + 状态匹配 join |
| GPU 适合度 | **B+**（继承 F4 并行性；分位数/Wilson 下界是批统计，GPU 顺手） |

### F6 · P1 三张条件概率表

| 项 | 内容 |
|---|---|
| 入口 | `docs/_working/decision_map_campaign/04_p1_conditional_tables.md`（板块 ~580-880 × 六段相位；condition_package.py:49 MIN_OBS=30） |
| 数据规模 | ≈1,600 交易日 × 880 板块——**一次计算批，量级极小** |
| 当前耗时 | 分钟级（groupby 统计，未测） |
| 调用频率 | 一次性 + 相位序列更新后重估 |
| 当前瓶颈 | 无（本已便宜） |
| GPU 适合度 | **C**（不需要 GPU——列此为"防 GPU 过度症"对照样本） |

### F7 · 策略考试链（f06 E4 WFA + 成本门重考）

| 项 | 内容 |
|---|---|
| 入口 | `scripts/backtest/f06_e4_wfa_exam.py`（fold 循环 :128/:156/:424）；`exam_cost_reexam.py`；`exam_cost_gate.py` |
| 数据规模 | 存活池 × fold 数（每 fold 一遍引擎 pass） |
| 当前耗时 | 每 fold ≈ 单格引擎 pass（估秒级×fold 数） |
| 调用频率 | 每批考试一次（weekly/按批） |
| 当前瓶颈 | 引擎 pass 串行（同 F2 核） |
| GPU 适合度 | **B**（吃 L1/L2 改造外溢红利即可，不单独立项） |

### F8 · 整装引擎批测（IBT 链，vectorized_engine+matching_logic+标定成本）

| 项 | 内容 |
|---|---|
| 入口 | `scripts/backtest/ibt/ibt_runner.py`（PIT 宇宙闸 :322）→ `src/zephyr/backtest/implementations/vectorized_engine.py`（production，1,001 行）+ `core/matching_logic.py`（626 行，佣金万0.854+5元地板+印花+过户，:131 逐笔透传 liquidity_tier）+ `core/cost_model_calibration.py`（ADV 分层+AC 冲击） |
| 数据规模 | 首跑批 410 策略（`11_integrated_backtest_audit.md:85` W_OOS 410/410） |
| 当前耗时 | 未公布单策略口径；逐笔成本解析=per-trade Python 逻辑 |
| 调用频率 | 每批首跑/复验一次 |
| 当前瓶颈 | 逐笔成本腿（ADV 分层查表）+事件循环 |
| GPU 适合度 | **B**（ADV tier 查表可 gather 化；但本引擎是**整装口径真源**，动它=动口径真源，GPU 化收益/风险比低于考尺链；双引擎分裂 IBT-D01 待对表——`11_integrated_backtest_audit.md:152`） |

### F9 · Kronos 批量推理打分（GPU-02 工单，已在产）

| 项 | 内容 |
|---|---|
| 入口 | `scripts/backtest/kronos_adapter.py`（MOD-BT-195，504 行）+ finetune 链（GPU 峰值 ~7G 实证，`docs/_working/automation/20260917_wo_gpu02_kronos_batch_scoring.md:11`） |
| 数据规模 | 全市场 ~5,000 标的 × 日线窗 |
| 当前耗时 | 夜窗批（工单验收线：单夜跑完、GPU 峰值≤8G） |
| 调用频率 | 每日/每周夜窗（cron 00:30） |
| 当前瓶颈 | PyTorch 推理本身=GPU 原生，不属本战役重写对象 |
| GPU 适合度 | **已 GPU**（登记在案防重复立项；与回测 GPU 共享 24GB 显存时须互斥窗——`wo_gpu02` §2.3 注册表互斥先例） |

### F10 · 情绪打分批量（LLM 化候选）

| 项 | 内容 |
|---|---|
| 入口 | 规则面现产：`src/zephyr/signal_ashare/sentiment/`（六件，规则打分，便宜）；LLM 面候选：`wo_gpu01_night_mining_ollama` + `docs/_working/emotion_line/`（gpu_emotion_condition_matrix_v1） |
| 数据规模 | 新闻/情绪行级；Ollama 本地推理=GPU 但属生成不是回测 |
| 当前耗时 | 规则面可忽略；LLM 面未立项 |
| 当前瓶颈 | I-O+模型推理 |
| GPU 适合度 | **C**（对本战役而言：不同 GPU 画像——显存长驻推理 vs 短批计算；互斥调度即可，不进重写范围） |

### F11 · 绩效/条件归因

| 项 | 内容 |
|---|---|
| 入口 | `scripts/backtest/condition_attribution.py`（只读 join+分层统计，头注 INVARIANTS"只读归因零重跑"）；`src/zephyr/backtest/core/cost_attribution.py`（闭式归因，723 行） |
| 数据规模 | net_returns 宽表（T×格数）× 条件包 |
| 当前耗时 | 秒-分钟级 |
| 调用频率 | 每批成绩单判读一次 |
| 当前瓶颈 | 无 |
| GPU 适合度 | **C** |

### F12 · Monte Carlo / Bootstrap（未来族）

| 项 | 内容 |
|---|---|
| 入口 | 现状只有 stationary bootstrap（`src/zephyr/backtest/regime_validation/e2_stationary_bootstrap.py`）；MC 引擎未建（PBO/CSCV 用确定性重排 `core/cpcv.py`+`purged_kfold.py`） |
| 数据规模 | 未来：千-万路径 × T 步 |
| 当前耗时 | n/a |
| 当前瓶颈 | n/a |
| GPU 适合度 | **A（未来）**——业界实证：Numba CUDA 路径并行×时间串行的 2D 几何，H200 上 114x（NVIDIA Developer Blog 2025-03-04，见②文 §五） |

### F13 · Walk-Forward/CPCV/White's RC 重采样

| 项 | 内容 |
|---|---|
| 入口 | `src/zephyr/backtest/core/walk_forward.py`（三模式+RC bootstrap，:28-33）、`cpcv.py`、`strategy_cpcv_matrix.py` |
| 数据规模 | fold 数 × 引擎 pass |
| 当前瓶颈 | fold 循环串行、每 fold 引擎 pass（同 F2 核） |
| GPU 适合度 | **B**（fold 间并行=进程级即可；核 GPU 化后自动受益） |

---

## 二、普查结论（三句话）

1. **需要 GPU 的计算高度集中**：F1+F2（考尺网格链）占已规划算力的绝对大头，且两者共用同一块 20 行数学核（`_c4_engine.py:439-458`）——重写对象是一个核，不是一堆系统。
2. **83% 热点的一半其实是"重复"不是"算力"**：每格 7 次引擎 pass 中，档位间/函数间可共享的部分占大头——L1 hoisting（不碰 GPU）先吃掉结构性浪费，GPU 只该吃剩下真正的算力账（详见③文 L1 节）。
3. **F4/F5（做T线）是第二大 GPU 候选**，但被 CH 读速卡脖子；F6/F10/F11 是"不需要 GPU"的对照样本，防为饱和而饱和（`19_gpu_plan:18` 原话）。

## 三、证据强度声明

- 实测口径：35.33s/83%/23.3h/282万对/11.5亿行 全部来自上文标注的仓内文档（B+ 级以上）。
- 估算口径：F3/F7 的"估秒级"未经 profiler 实测——L1 施工第一步应先跑一次 cProfile 热点确认（列⑥roadmap Phase 2 前置）。
