---
ttl: task_bound
title: LANE-GPU① 计算热点普查（实测：单格耗时分解／可向量循环清单／内存足迹）
created: "2026-09-25"
sid: st-gpu-rewrite-mining-20260925
lane: LANE-GPU
family_id: GPU-REWRITE
evidence_grade: A（全部耗时数字为本机实测；无一项引自文档结论；文档结论仅作对照并逐条判真伪）
supersedes: docs/_working/gpu_rewrite/compute_inventory.md（同名义车道前一轮产物，其 §三 自认"未经 profiler 实测"——本轮以实测替换其估算；2026-09-26 双版合并：前一轮**"每格 7 次引擎 pass"构成＋"83% 的一半是重复而非算力（hoisting 3–7x）"两条量化口径**已按原文入档本文 §二·补并逐条标实测改判，证据不再只活在 git 历史里）
---

# LANE-GPU① 计算热点普查（实测）

> 一句话结论：**单格 92–95% 的时间在"涨跌停封板掩码重建"（Python 行级 dict/iat + ClickHouse 行物化），pandas 张量数学只占 2.8–3.6%；所谓"83% 在五档成本扫描"既不是单格口径、也不是在飞批次实际走的路径。**

## 零、复现口径（实测方法与边界）

| 项 | 值 |
|---|---|
| 被测件 | `scripts/backtest/factory_grid_executor.py` run_batch 单格路径 + `scripts/backtest/translated/_c4_engine.py` 真身函数 + `exam_cost_gate.run_cost_tier_scan`（**零重实现、零改动**） |
| 探针件 | `.runtime/tmp/lane_gpu/hotspot_profile.py`（importlib 载真身 + 内存 monkeypatch 计时，只读；产物 `.runtime/tmp/lane_gpu/hotspot_result*.json`） |
| 窗口 | 与在飞 T1 同窗：`--start 2019-01-04 --end 2025-09-09`（预热 200 日）→ 评估面板 1,622 交易日 × 5,646 列（含预热 1,757 行） |
| 格点 | 用 T1 同源抽样 `stratified_sample(expansion, 3700, seed=20260915, stratify_dims=("emotion_grey_band","market_state_F4"))`，按宇宙各取 1 格实测：hs300(504 列)/zz500(1,037 列)/all_a_ex_st(5,217 列) |
| 分解法 | ①`_load_seal_masks` 计时包装 + ②`_q` CH 往返计时（次数/秒/行数）+ ③`gate_limits=False` 对照（纯张量面）+ ④cProfile 全链一遍（**cProfile 有 2.2x 膨胀，只取函数占比不取绝对值**） |
| 环境 | 本机 20 逻辑核 / 64GB（实测时可用 22.9GB）/ RTX 3090 24GB（`nvidia-smi` 2026-09-25 util 6%、显存 1,823MiB/24,576MiB）/ pandas 2.3.3 / numpy 2.3.5 |
| 未做 | 不起 GPU 作业（T1 单卡独占）、不改引擎、不重启在跑进程 |

## 一、单格实测分解（本机，非估算）

### 1.1 分段耗时（秒/格）

| 宇宙（列数） | evaluate_recipe | run_backtest（pass1） | daily_net_returns（pass2） | 五档扫描 scan5 | 轻档扫描 scan2 | **现状单格合计**（eval+2 pass，无扫描） | 若开五档扫描 |
|---|---|---|---|---|---|---|---|
| hs300（504） | 0.702 | 2.276 | 2.219 | 11.148 | 4.098 | **5.197** | 16.345 |
| zz500（1,037） | 0.584 | 5.182 | 5.051 | 26.770 | 12.072 | **10.817** | 37.587 |
| all_a_ex_st（5,217） | 5.329 | 28.777 | 29.949 | 139.258 | 58.347 | **64.055** | 203.313 |

按 T1 实际抽样构成（实测 `picked_universe_counts`：hs300 1,254 / all_a_ex_st 1,236 / zz500 1,210）加权：

- **现状单格 ≈ 26.7s**（与 T0 实测 35.33s/格 同量级——差异=宇宙/配方方差，见 §四·更正2）；
- **若开五档扫描 ≈ 85.8s/格**，3,700 格 = 88h（远超 59h 窗）→ 这也是当前 T1 未开扫描的现实约束背景。

### 1.2 引擎 pass 内部去向（占单 pass 百分比，实测）

| 去向 | hs300 | zz500 | all_a_ex_st | 代码位置 |
|---|---|---|---|---|
| **掩码 Python 面**（7.2M 行 dict 推导 + 93.5 万次 `.iat` 写入 + 掩码 DataFrame 分配） | 1.648s（**74.3%**） | 3.819s（**75.6%**） | 23.428s（**78.2%**） | `_c4_engine.py:353`、`:354-355`、`:358-368` |
| **掩码 CH 面**（每 pass 2 次全窗查询：raw close + stk_limit） | 0.485s（21.9%） | 1.044s（20.7%） | 5.054s（16.9%） | `_c4_engine.py:341-349` |
| 闸内逐日行循环（prev 依赖） | 0.019s（0.9%） | 0.048s（0.9%） | 0.401s（1.3%） | `_c4_engine.py:385-395` |
| **纯 pandas 张量面**（reindex/ffill/pct_change/mul/sum/abs-diff） | 0.067s（**3.0%**） | 0.140s（**2.8%**） | 1.066s（**3.6%**） | `_c4_engine.py:415-420`、`:450-455` |
| 单 pass 合计 | 2.219s | 5.051s | 29.949s | — |

cProfile 全链（all_a，7 pass，膨胀口径）交叉印证：`_c4_engine.py:325 _load_seal_masks` **cumtime 457.7s / 480.0s = 95.4%**，其内 `{method 'get' of dict}` 1.479 亿次调用、`pandas .iat.__setitem__` 93.5 万次；CH 反序列化 `clickhouse_driver/result.py:45 get_result` cumtime 85.1s。**热点不在"表运算"，在"行物化+逐行判定"。**

## 二、可向量化／可 hoist 的循环清单（文件:行号 + 实测代价）

| # | 位置 | 形态 | 实测代价（all_a/单 pass） | 可改性 |
|---|---|---|---|---|
| L1-a | `_c4_engine.py:353` | `{(date6,sym6): close}` dict 推导，**7,227,934 行** | 独立实测 14.75s + RSS +1,206MB | 完全可改：CH 侧直接 join，或 pandas merge/pivot 向量化 |
| L1-b | `_c4_engine.py:358-368` | 逐行 `for d,s,up,dn in lim_rows` + 两次 `dict.get` + 命中后 `.iat[i,j]=True`（**935,165 次写入**） | 与 L1-a 合计 23.43s | 完全可改：向量化为"列对齐矩阵比较"（`close_raw >= limit_up*(1-tol)`） |
| L1-c | `_c4_engine.py:333,354-355` | 全尺寸 bool DataFrame 三份分配（empty + 两份 copy） | 分配 16.1MB/次，含在 L1-a/b 计时内 | 可改：位图/numpy bool 阵列 |
| L1-d | `_c4_engine.py:341-349` | 每 pass 2 次全窗 CH 查询（**同 (窗口,列集) 重复查**） | 5.054s | 可改：批级缓存（掩码只依赖窗口+列集） |
| L2-a | `_c4_engine.py:385-395` | 逐日 prev 依赖 numpy 行循环 | 0.401s（1.3%） | **不建议改**（收益 1.3%，串行依赖，风险>收益） |
| L2-b | `_c4_engine.py:415-420` 与 `:450-455` | 两函数体重叠（`run_backtest` 与 `daily_net_returns` 同式） | 执行器 `factory_grid_executor.py:777-778` 两连调=**白付 1 个 pass**（≈30s/all_a 格） | 完全可改（合并为一次计算两处消费） |
| L2-c | `exam_cost_gate.py:149` | 五档 = 对同 (weights,px) 调 `net_fn` 5 次 | 139.26s/all_a 格（其中 ≈132s 是掩码重建 5 遍） | 完全可改：档间唯一差异是标量 `cost = turnover×(2·2.5+10+2·slip)/1e4`（`_c4_engine.py:457`）→ 因子一次算、五档只算标量乘（实测五档标量乘 **<0.1ms**） |
| L3-a | `factory_grid_executor.py:579-597` | A1 标准化/A2 合成截面（combine_cache 未命中时） | 5.329s/all_a 格（L1 完成后**升为第一大项**） | 部分可批量化（前缀缓存已建，命中即免） |
| L3-b | `factory_grid_executor.py:244-248` | 因子宽表 rolling（批级，按宇宙缓存） | 全市场批级 1.7s（估）+ `:711` vol20 41.55s | 批级，已摊薄（见 §三） |

**关键判据：现状单格 7 个 pass（若有扫描）中，掩码重建被重复 7 次，而它只依赖 (窗口, 宇宙列集)——同宇宙 1,236 格可共享同一份掩码。**

## 二·补 重复计算结构的量化口径（前一轮 `compute_inventory.md` 矿脉证据并入，2026-09-26 双版合并）

> 并入理由：本文 §二 已按实测逐条列出重复项（L1-a…L2-c），但前一轮有**两条"结构性口径"在本文没有等价表述**——
> ①"**每格 7 次引擎 pass**"这个**总数及其构成**（本文合并前只有一句"7 个 pass（若有扫描）"，未给 7 从哪来）；
> ②"**83% 热点的一半其实是'重复'而非'算力'**"这个**结论**（本文 §四·更正1 判其分母口径不成立，但未记下前一轮结论本身）。
> 两条均属"证据不丢、口径可核"必并项：**入档前一轮原文与行号，并逐条标本文实测的改判，不隐晦也不覆写。**

### 口径① · "每格 7 次引擎 pass"的构成（前一轮 `compute_inventory.md:40` ＋ `rewrite_architecture.md:17-20`）

| 冗余类 | 前一轮原文（引，已落 HEAD commit 37aeecedcd） | pass 计数贡献 | 本文实测对应与判定 |
|---|---|---|---|
| **档位间重复** | "`run_cost_tier_scan` 每档全量重算 reindex/pct_change/涨跌停闸/gross/turnover，而档位间唯一差异是 `cost = turnover*(...+slip*2)/1e4` 一行标量乘（`_c4_engine.py:457`）"——五档各自全量重算 | **5**（全档口径；T1 轻档口径=2） | L2-c（`exam_cost_gate.py:149`）：all_a 单格 scan5=139.26s，其中 ≈132s 是**掩码重建被跑 5 遍**；实测五档标量乘 **<0.1ms** → **前一轮定性成立且被实测加强** |
| **函数间重复（两连调）** | "`factory_grid_executor.py:777-778` 又使每格 run_backtest+daily_net_returns 各跑一遍＝每格 7 次引擎 pass"；`rewrite_architecture.md:19`"两函数数学重叠 90%（net 序列两处同式 :423-424 vs :457-458）" | **+2** | L2-b：两函数体同式（`:415-420` vs `:450-455`）→ **白付 1 个 pass**（all_a ≈30s/格）→ 一致 |
| **涨跌停掩码重复构建（零缓存）** | "`apply_fillability_gate` 每次 pass 重查 CH 两次 + Python `iat` 逐行循环建掩码（`_c4_engine.py:341-368`，**无缓存**）……同一格 7 次 pass = **14 次 CH 往返 + 7 次全量行循环**，而掩码只依赖 (宇宙, 窗口)，格间可全批共享" | 每 pass ×(2 CH 往返＋1 全量行循环) | L1-a/L1-b/L1-d：实测掩码 Python 面占单 pass **74–78%**、CH 面 **17–22%**；cProfile `_load_seal_masks` cumtime **95.4%** → **前一轮"零缓存"判定成立，且实测把它的比重从"次要浪费"升为第一大靶** |
| **合计** | **每格 7 次引擎 pass**＝5（档位）＋1（run_backtest）＋1（daily_net_returns） | 7 | 本文 §二 末句同口径；**必须补的限定**：在飞 T1 实际未开 per-point 档位扫描（§四·更正2：prereg 无 `cost_gate_t1_tiers_bp` 键）→ **现网真实 pass 数=2，"7" 是"扫描全开"口径**，两数不可混用 |

### 口径② · "83% 热点的一半其实是重复而非算力"（前一轮 `compute_inventory.md:176`，普查结论第二条）

- 前一轮原文：**"83% 热点的一半其实是'重复'不是'算力'：每格 7 次引擎 pass 中，档位间/函数间可共享的部分占大头——L1 hoisting（不碰 GPU）先吃掉结构性浪费，GPU 只该吃剩下真正的算力账"**。
- 前一轮由此给的**非 GPU 提速线**：**纯代码整理（hoisting）即得 3–7 倍**（`rewrite_architecture.md:42`"预估 3-7x（35.33s→5-12s/格）"，并自设前置"施工前先跑一次 cProfile 定分位数"——本文 §一 即该前置的完成品）。
- 本文实测的两条改判（全留在案，不改写前一轮原文）：
  1. **"83%" 的分母口径不成立**（§四·更正1：131.9/(131.9+26.2)=83.4%，排除了 evaluate_recipe 与 pass2；完整单格口径下扫描开启=68.9%、未开=0%）；
  2. **"重复 vs 算力"的定性成立且被加强**，但重复的主体**不是"档位重算张量"而是"掩码重建的重复＋行物化"**（占单 pass 74–78%，纯张量面仅 2.8–3.6%）→
     故 hoisting 收益线从前一轮估算的 3–7x **上修为实测锚 8.6x（现状口径）／16.6x（扫描口径）**（③文 §一 L1 收益表）。
- **合并后净结论**：前一轮"先整理重复、再谈 GPU"的**顺序判断被实测完全证实**；其百分比与倍率数字属未实测估算，**以本文实测数为准**，前一轮原值在本节在案可查（不再需要去 git 历史里捞）。

## 三、内存足迹（实测）

| 对象 | 尺寸 | 实测出处 |
|---|---|---|
| 收盘价面板 `closes_all`（1,757×5,646 float64） | 75.7MB | 装载后 `values.nbytes` |
| 评估面板 `closes_eval`（1,622×5,646） | 69.9MB | 同上 |
| 权重宽表（单格，稠密 float64） | hs300 6.2MB / zz500 12.8MB / all_a 64.6MB | `weights.nbytes` |
| 权重稀疏度（非零占比） | hs300 76.1% / zz500 78.1% / all_a 47.9% | `(w!=0).mean()`——**注意：ffill 使"top-N 持仓"在时间轴摊成近稠密，稀疏化收益远小于前一轮假设** |
| 封板掩码两份（bool） | 16.1MB | 实测 |
| **掩码中间物：CH 行列表** | **+1,076MB**（7,227,934 个 tuple） | 实测 RSS 增量 |
| **掩码中间物：(date,sym)→close dict** | **+1,206MB** | 实测 RSS 增量 |
| 单次掩码构建总瞬时峰值 | ≈2.3GB（= 最终掩码的 **约 145 倍**） | 实测 RSS 3.03GB 终点 |
| 在飞 T1 进程 RSS | 4.46GB（1 核忙：`cpu_percent=93.2%`，39 线程） | psutil 2026-09-25 21:50 采样 |
| 批级数据面一次性成本 | load_px 6.40s + wide 3.44s + filter_st 6.44s + vol20 41.55s + mkt_cap 9.76s + industry 0.10s ≈ **68s** | 实测 → 摊到 3,700 格 = **0.018s/格（0.07%）** |
| 3090 显存可行性（算术，未起 GPU 作业） | 稠密 float32 批：3,700 格 all_a 面板 = 127GB（爆 18GB 配额）→ 每波 B≈500 格=17GB 边缘；**面板+掩码常驻仅 50MB** | 由实测面板尺寸推得（标注=推演非实测） |

## 四、对既有文档结论的实测判定（三条更正）

1. **"83% 花在五档成本扫描"——口径不成立。** 溯源=`docs/_working/e2e_integration/LEDGER.md:131`（数据装载 15.2/因子 1.2/单次回测 26.2/五档扫描 131.9）。其 131.9s 与我实测 all_a scan5=139.26s 吻合，说明那份 profiling 确实是 all_a 级窗口；但其 83% 的**分母只含"单次回测+五档扫描"**（131.9/(131.9+26.2)=83.4%），排除了 evaluate_recipe 与 pass2。按完整单格口径实测：**扫描开启时 scan5 占 68.9%**，扫描关闭时（见下条）**占 0%**。
2. **"单格 35.33s 中 83% 在扫描"与在飞批次路径不符。** 实测在飞 T1 命令行 `--stage t1`（PID 3584），而 `config/search_space_prereg.yaml:budget_caps` **无 `cost_gate_t1_tiers_bp` 键** → `_resolve_stage_cost_tiers()` 在字段缺省时直接返回 None（`factory_grid_executor.py:959-960`）→ **per-point 档位扫描根本未启用**；T0 产物 `data/strategy_intake/grid_20260924-080309/manifest.csv` 表头亦无 `cost_tier_sharpes_json/cost_adjusted_sharpe` 两列（实测核读）。故 35.33s 全部来自 eval+2 pass，与扫描无关。五档真扫描实际发生在 `scripts/backtest/t1_t2_handover.py:296-343` 的晋级集复验（以及 f06 考试/红蓝标定件）。
3. **"引擎串行天然只吃 ~10 核（全机 20）"——实测约 1 核。** `psutil.Process(3584).cpu_percent(interval=3)=93.2%`（=1.0 核），非 10 核。含义反转：**进程级并行的 headroom 比文档假设大得多**（受 RAM 约束，见⑤文），而"向量化吃满多核"的叙事不成立。

另需记录：前一轮同名义文档 `compute_inventory.md` 的 F1–F13 族清单（入口/行号/调用频率）经反查与实测**基本准确**，本轮继承其族划分口径，但把"83% 五档扫描/每格 7 pass"一类未经实测的推断全部替换为上表实测数；其"稀疏权重 ≤2GB"的显存判断被上表稀疏度实测**削弱**（all_a 权重非零占比 47.9%，稀疏表示收益有限）。

## 五、六向台账（每向：内部反查 + 全网搜索）

| 向 | 内部反查（动作→发现） | 全网搜索（动作→发现/查无） |
|---|---|---|
| ①上游 | 读 prereg/契约/引擎常量→热点输入仅 4 张 CH 表（`kline_daily_hfq`/`kline_daily`/`stk_limit`/`stock_indicator`）+行业锚；**掩码原料（raw close+limit）与净值原料（hfq close）来自不同表**，是重复查询的结构性根因 | 搜 "A股 涨跌停 不可成交 掩码 回测"：合格来源仅 arXiv:2507.07107（2025，A 股日线限价污染）+ qlib `exchange.py` 的 `limit_threshold`（见②文 §3）；中文结果全是 CSDN 聚合站→按闸1 弃用 |
| ②下游 | grep 消费方→`t1_t2_handover.py:296-343`（五档真扫描实际发生地）、`factory_grid_anova.py`、`f06_e4_wfa_exam.py`、`n_trial_ledger`、`condition_attribution.py`、`api_server.py`（只读 `three_high_candidates.csv`，不读 grid manifest）→ **改写单格语义会连坐 T2 晋级与成绩单成本门真实性线** | 搜 "backtesting engine profiling hotspot"（无 A 股向合格来源）→ 已查无同类公开普查件；判为内部矿 |
| ③算法/机制 | 反查既有加速件：T2c `combine_cache`/`slice_cache`（`factory_grid_executor.py:708-711`）、`_apply_freq_trigger` 向量化史（docstring :37-45）→ **仓内已有一次成功的"等价向量化"先例（记录 lasso 参数放宽=非逐位等价的先例）** | NVIDIA CCCL 确定性文（2026-03-05）+ CUDA FP 文档 v13.4（2026-09-13）+ Numba 交易模拟博客（2025-03-04，114x 几何=路径并行×时间串行）——三源合证"该改的是重复计算与逐行判定，不是把同一段 pandas 换成 GPU" |
| ④后端 | 实测（本文正文）+ 依赖盘点：`torch`=CPU 版（`requirements.txt:5-10` 裁定 ARCH-TORCH-CPU-ONLY）、`cupy` 未装、`cudf` 未装、`numba` 已装、`polars 1.41.2` 已装（20 线程）→ **L2 需要新依赖，无现成 GPU 载体可用** | 本机实测 Polars vs pandas 同形工作负载（1,622×1,200 面板，pct_change+rolling std）：pandas wide 0.35s / pandas long 1.0s / **polars lazy over 0.43s** → Polars 不是本热点的杠杆（实测否定，非文档印象） |
| ⑤前端 | 反查呈现面：grid manifest 零前端读端（`grep -rln "strategy_intake/grid" src/zephyr/frontend/` → **已查无**）；唯一相关=dashboard `api_server.py:2730` 的三高榜 | 搜参数 sweep 呈现惯例→登记为长尾矿（MLflow/W&B sweep 类，与本车道目标无关，不占预算） |
| ⑥数据字段 | 逐字段核对 `system.columns`（实测）：`kline_daily.close`／`stk_limit.limit_up`／`kline_daily_hfq.close`／`stock_indicator.total_mv`／`industry_class.industry_sw`／`index_constituent.valid_to`／`stock_basic.name` **7/7 present=1**；质量画像：`stk_limit` 共 9,226,503 行、`max(trade_date)=2026-09-24`（未断更）、`limit_up/limit_down IS NULL` 5,322 行=**0.058%**（→ 引擎 fail-open 分支的实际触发率，也是掩码语义的边界样本量） | 字段口径外部核：涨跌停价定义（交易所规则）已在②文 §6 记录来源；"可得性"无外部依赖 → 判"已查无（内部字段自证）" |

## 六、挖矿日志（本件）

| 轮 | 矿脉 | 判定 | 关键产出 |
|---|---|---|---|
| R1 | 单格耗时分解（内部实测） | signal | §一 全表 + 掩码占 74–78% 的新结论（推翻"表运算是热点"） |
| R2 | 循环/行号清单（内部实测+code reading） | signal | L1-a…L3-b 九项，含"可改/不建议改"分级 |
| R3 | 内存足迹与显存可行性（内部实测） | signal | 掩码中间物 2.3GB 峰值=最终掩码 145 倍；权重稀疏度假设被削弱 |
| R4 | 既有 83%/10核/35.33s 结论复核（内部核读+实测） | signal | 三条更正（§四），并定位 83% 的分母口径与出处行 |
| R5 | Polars 能否作零新依赖杠杆（本机实测+README） | signal（否定性） | polars 0.43s vs pandas 0.35s → 不入图，登记为"已测否定" |
| R6 | 外部热点普查同类方法论（全网） | noise（归因=方向本就无矿：公开界不做单格 profiler 公开） | 只入"分段计时+cProfile 交叉印证"方法自证，无新引文 |
| R7 | 中文 A 股回测性能普查来源（全网） | 受阻→改判 | CSDN/聚合站不可作引文；已换 arXiv/qlib 两条合格来源（②文） |
| 长尾 | 未挖 | — | 做T线 F4/F5 语料面的实测普查（本车道边界外，19 号文 A2 归属）；CH 服务端查询并发上限实测（禁干扰在飞 T1，未做） |

## 七、全项目计算族 GPU 适合度清单（继承前一轮普查＋本轮实测修正）

> 族清单本身经反查成立（入口/行号/调用频率准确），故**继承不重挖**；本轮只修正其未经实测的推断项（标 ▲）。评级口径：A=批量独立计算共享同一数据面板｜B=部分可向量化/GPU 化｜C=I-O/事件驱动/本已便宜。

| 族 | 入口（file:line） | 规模/耗时（实测或标注出处） | 评级 | 本轮修正 |
|---|---|---|---|---|
| F1 成本档扫描（考尺链） | `factory_grid_executor.py:797-818`→`exam_cost_gate.py:120-149`→`_c4_engine.py:439-458` | **实测 all_a 单格 scan5=139.26s / scan2=58.35s**；在飞 T1 **未启用**（§四·更正2） | A→**改判 B** | ▲靶不是"扫描本身"而是其重复调用掩码重建；L1 后成本≈7×张量 |
| F2 单格回测核 | `factory_grid_executor.py:777-778`（两连调） | 实测单 pass 2.22s/5.05s/29.95s（三宇宙） | A→**改判 B** | ▲张量面仅 2.8–3.6%，GPU 只搬核不动掩码=收益极小 |
| F3 配方求值（normalize/combine/sizing） | `factory_grid_executor.py:545-617`，缓存在 `:570-597` | 实测 0.58/0.70/**5.33s**（all_a 缓存未命中） | B→**升为 L1 后第一靶** | ▲前一轮"估 3-8s"命中 |
| F4 做T材料线 | `scripts/backtest/t0_material_line.py` | ≈23.3h CPU／语料 ≈282 万对/周期×5；分钟库 11.5 亿行（`decision_map_campaign/links/L05_t0/material_precapacity_report.md:23,94`） | A- | 未实测（本车道边界外，长尾登记） |
| F5 做T全量×状态匹配 | 规划中（17 号文 §三.1-2） | 未跑全量 | B+ | — |
| F6 P1 条件概率表 | `condition_package.py`（MIN_OBS=30） | 分钟级 | C | 保留为"不需要 GPU"对照样本 |
| F7 策略考试链（f06 E4 WFA＋成本门重考） | `scripts/backtest/f06_e4_wfa_exam.py`；`exam_cost_reexam.py` | 每 fold≈单格 pass | B | 吃 L1 外溢红利，不单独立项 |
| F8 整装引擎（IBT 链） | `src/zephyr/backtest/implementations/vectorized_engine.py`＋`core/matching_logic.py` | 410 策略首跑批 | B（**禁动**：口径真源，IBT-D01 未收口） | — |
| F9 Kronos 批推理打分 | `scripts/backtest/kronos_adapter.py` | 夜窗，GPU 峰值 7–8GB | 已 GPU（须与批测互斥窗） | — |
| F10 情绪打分 | `src/zephyr/signal_ashare/sentiment/` | 规则面可忽略 | C | — |
| F11 绩效/条件归因 | `scripts/backtest/condition_attribution.py`、`core/cost_attribution.py` | 秒-分钟级 | C | — |
| F12 Monte Carlo/Bootstrap | 现仅 `e2_stationary_bootstrap.py`；MC 未建 | n/a | A（未来） | ▲114x 系单源待验证（②文 §四.4），不得作承诺 |
| F13 WFA/CPCV 重采样 | `core/walk_forward.py`、`cpcv.py` | fold 串行 | B | 进程级并行即可受益（Phase 1） |

## 八、挖后自审闸（三态裁定）

- **主判据**：本普查直接消灭"Owner/总筹人工猜测热点"这一人工环节，并把 L1/L2 的施工靶从"pandas 换 GPU"纠正为"消除掩码重建的重复与行物化"——终局全貌里"性能诊断"必须是自动可复跑的能力，不是文档结论。
- **终局位置**：有（性能画像应成为常驻可复跑探针件，而非一次性手工脚本）。
- **裁定**：**施工**——但施工物不是本文档，而是把 `.runtime/tmp/lane_gpu/hotspot_profile.py` 的等价探针正式化（挂 `scripts/backtest/` 或测试位，带 ttl/creation_token/MOD 登记），使任何引擎改动的收益与回归可一键复测；施工顺序与工时见⑤文 Phase 2 前置。
- **反驳者一问（自我否证最强三条）**：①"实测只有 3 格样本，方差可能吞掉结论"→ 已如实标注宇宙各 1 格，且结论方向由 cProfile 函数级占比独立支持（95.4% cumtime），非单点噪声；②"合成基准与真库基准孰真"→ 本文全部为真库真身函数，无合成面板；③"把探针正式化=为自动化而自动化"→ 反驳：当前任何一次引擎提速决策都需人工重写探针（本轮即第二次），消灭的正是这种重复人工。
- **封矿线**：本普查矿脉（考尺链单格分解）已见底——剩余六向"已查无/受阻"见 R6/R7 与长尾清单，故**本件矿脉封矿**，后续挖掘移交⑤文 Phase 2 施工前的例行复测。
