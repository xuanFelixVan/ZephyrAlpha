---
ttl: task_bound
title: S02 因子/形态发现挖矿文档
session: st-fullauto-20260915
date: 2026-09-15
---
# S02 因子/形态发现

> 挖矿定位：公式轨（lane C）+智能体轨（lane C2）已周窗自动实弹；图形/另类道=人工班次=全链无人值守的最大人工残留。挖矿重点=三轨道自动化缺口+业界 SOTA 对照。

## 1 现状盘点（自动化状态+file:line 证据）

### 1.1 公式轨（lane C，gplearn）——✅ 周窗自动实弹
- `scripts/backtest/lane_c_formula_miner.py:23-35`（MOD-BT-155）：gplearn 遗传规划 MVP，正式档 pop1000×50；流程=E0 问闸（heavy 档，:358 "E0 闸拒：重算力须收盘后/休市日"）→ 白名单算子集（`config/factor_mining_whitelist.yaml`，fail-closed 交集）→ 面板（kline_daily_hfq 特征 ≤T+前向 5 日收益 y+technical_indicator 日频基座=REG-IND-001）→ 增量 IC fitness（对基座残差 rank IC）→ 出生证卸 `data/strategy_intake/lane_c_candidates.csv` → E2 预审消费。
- 调度：`scripts/run_factory_lane_c.ps1` 四连（mine → factory_intake_pipeline run --with-lane-b --limit-precheck 15 → construct → hypothesis_translator translate --seeds 5），日志 `.runtime/logs/factory_lane_c.log`；计划任务 `ZephyrAlpha_FactoryLaneC` 周六 10:00（`scripts/register_factory_lane_c_task.ps1:34-39`）；同日 14:00 `ZephyrAlpha_C4Exam`（register_c4_exam_task.ps1:16 排序注释：Sat 10:00 FactoryLaneC → Sat 14:00 C4Exam）。
- **实弹候选**：lane_c_candidates.csv 10 条，头名 `CAND-32e5c7444cc0 abs(ret_5d)` incr_ic 0.057134（E1C-20260914-064126，gplearn pop=50 gen=4 烟测批）。
- 双调度器并存事实：lane C/C4 走 **Windows 计划任务**，数据侧走 APScheduler tasks.yaml（tasks.yaml 内 grep 零 factory/lane_c 条目）——两条调度体系未统一。

### 1.2 智能体轨（lane C2，LLM 产 DSL）——✅ 已实弹
- `scripts/backtest/lane_c2_agentic_miner.py`（:25-42 实读）：种子=E2 台账已过审假说（反哺闭环）→ OllamaChat（默认 qwen3:8b，消融 deepseek-r1:8b）按种子产 DSL 表达式（三正则写进 prompt：对齐三段自述/原创声明/长度上限）→ DSL AST 校验（白名单算子+已知特征，fail-closed）→ 面板求值 → 增量 IC 验收（MIN_INCR_IC=0.0，描述性）+ AST 原创性门（节点多重集 Jaccard ≤0.8 vs gplearn 存货与已收候选）→ 卸 `data/strategy_intake/lane_c2_candidates.csv` → E2 预审。
- **实弹候选**：lane_c2_candidates.csv 8 条，头名 `CAND-22a96c4c7758 ts_zscore_20(ret_5d)` incr_ic 0.087049（E1C2-20260915-020015，AST 原创性 0.50<0.8）。
- 赛马：P2 计分板=factory_intake_pipeline race 子命令（同一考试自动可比）。

### 1.3 图形态道——❌ 人工班次（最大人工残留）
- 库已建：`docs/01_policies_and_standards/_registry/catalogs/chart_pattern_registry.yaml`（REG-PAT-001，schema v2.2，8 大类；v2.13.0 十四轮全网 SOTA 调研扩充：candlestick 77+chart_pattern 62+缠论/Elliott/威科夫等；条目级 code_symbol/code_fingerprint 双向索引）。
- 缺自动化识别器：条目靠 AI 班次人工开批 quantized（algorithm_status: code_path 非空→quantized，否则 pending_backtest）。

### 1.4 指标扩库道——❌ 班次驱动
- `src/zephyr/factor/technical_indicators/`：trend/momentum/volatility/volume/cycle/reversal/statistics 七族模块（线索口径 98 处注册；__init__ 聚合注册）。扩库靠班次，无自动提案机制。

### 1.5 另类数据道——❌ 未接线
- 方案已挖透：`docs/_working/alt_data_consumption_plan.md`（F1-F22+ 因子位，含 F22 情绪调节动量外证；消费排期 C-3=10 月中 F1-F3 千股千评+F13 人气榜）；`src/zephyr/regime/` 整包已存在作 regime 输出接线目标——**数据表和消费方案齐，落库管线未通**。

### 1.6 建而未接线（休眠矿）
- `src/zephyr/research/factor_mining_pipeline.py`、`src/zephyr/research/factor_vote_mining.py`：存在；仓内引用仅 `src/zephyr/factor/factor_factory.py:30` 注释（"本件只留 mining_hook 扩展点，委托不实现"）——**零运行时调用**。

## 2 六向挖矿日志表

| 向 | 内部发现 | 外部发现(URL+年份) | 判定 |
|---|---------|-------------------|------|
| ①上游 | 种子上游=E2 台账已过审假说反哺 lane C2（闭环已通）；算子上游=白名单 yaml（fail-closed）；基座上游=REG-IND-001 指标库 | — | signal |
| ②下游 | 出生证 CSV→E2 预审（factory_intake_pipeline --with-lane-b）→C3 construct→翻译，四连自动；候选>20 必停挖转施工（SOP §8） | — | signal |
| ③算法/机制 | lane C=gplearn；lane C2=LLM+AST 正则化（与 AlphaAgent 思路暗合） | ①RD-Agent(Q) 多代理因子-模型联合优化，2X 年化/70% 少因子（https://arxiv.org/html/2505.15155v2 ，Microsoft Research+HKUST，2025）；②LLM alpha mining 综述（https://jzus.zju.edu.cn/iparticle.php?doi=10.1631/FITEE.2500386 ，FITEE 浙大期刊，2025）；③Alpha-GPT 人机交互挖矿（https://arxiv.org/html/2308.00016v2 ，arXiv，2023）；④AlphaAgent LLM 代码进化挖矿（https://www.alphaxiv.org/abs/2511.18850v3 ，2025；另 https://arxiv.org/html/2502.16789v2 ，2025）；⑤GP+LLM 语义剪枝（https://www.mdpi.com/2076-3417/16/12/6231 ，MDPI Applied Sciences，2026） | signal |
| ④后端 | research/ 两模块休眠（factor_factory.py:30 hook 预留）；AlphaGen RL 轨在设计稿立项另批未启动（lane_c_formula_miner.py:30 注释） | AlphaGen：RL 产协同 alpha 集合，KDD 2023（https://github.com/ICT-FinD-Lab/alphagen ，ICT 中科院，2023；论文 https://arxiv.org/abs/2306.12964 ）；alpha-gfn GFlowNet 路线（https://github.com/nshen7/alpha-gfn ，2023）；Alpha2=RL+MCTS 逻辑公式 alpha（https://arxiv.org/html/2406.16505v1 ，2024） | signal |
| ⑤前端 | 候选只落 CSV，无前端可视化（登记不施工，属 S13 前端班） | — | signal（登记） |
| ⑥数据字段 | 面板=kline_daily_hfq+technical_indicator 日频；另类字段方案 F1-F22 已立卡（alt_data_consumption_plan.md）未落库 | Alpha158 基准=A 股 CSI300/500 设计（https://github.com/microsoft/qlib/blob/main/examples/benchmarks/README.md ，Microsoft，2025 在维）；Alpha101 经典 101 公式因子（https://www.researchgate.net/publication/289587760_101_Formulaic_Alphas ，WorldQuant，2015）；AlphaBench=LLM 挖矿基准 CSI300（https://www.cs.cityu.edu.hk/~cliu644/HomePage/doc/AlphaBench/AlphaBench_PDF.pdf ，香港城市大学，2025） | signal |

外部搜索 4 轮全 signal，无受阻轮；连续 noise 轮=0，未触发封矿，时间盒封批（长尾见 §6）。

## 3 业界与开源对照（四闸过滤后）

| 业界方案 | 对照本仓 | 四闸结论 |
|---------|---------|---------|
| RD-Agent(Q)（研究/开发双代理循环：假设→因子代码→回测→迭代，Qlib 底座） | lane C2 已是"LLM 产 DSL→AST 校验→增量 IC→E2/E4 终审"的单环；缺**因子-模型联合优化**与自动迭代改进环 | A 股适配✅（Qlib 即 A 股设计）；可回测✅。**方向性印证本仓路线**；联合优化环=挂起排期（等 E4 批考首跑出真实反馈信号后再立） |
| AlphaGen（RL 直接优化 alpha **集合**协同收益，天然去共线） | lane C gplearn 逐条产公式→靠 E2/E4 后置去重 | 开源（GitHub，MIT 系）。**立卡：AlphaGen RL 轨**（原设计稿已预留"立项另批"），解锁条件=lane C/C2 候选积压出现共线冗余实证 |
| AlphaAgent/Alpha-GPT（LLM 代码进化+正则化/人机交互） | lane C2 的 AST 原创性门+机制自述三正则=同思路自制实现 | 已对等，无施工 |
| Alpha158/Alpha101 基准集 | REG-IND-001 自建指标基座（七族） | **立卡：以 Alpha158/101 做横评基准集**（校准自建基座覆盖率），一次性脚本探路即可，挂起 |
| GP+LLM 语义剪枝（MDPI 2026） | lane C 全量 GP 搜索 | 可选加速项，挂起（等算力墙实测出现再立） |

## 4 堵点与欠账清单

1. **图形态道无自动识别器**（最大人工残留）：chart_pattern_registry.yaml 数百条目 pending_backtest，靠 AI 班次人工开批——违反终局全貌（中间一切人工参与都要消灭）。
2. **另类数据道未接线**：F1-F22 因子位方案齐、regime 消费端齐，缺落库管线（Owner 只需注册账号/API 的数据源如千股千评/人气榜，正是北极星一头）。
3. **指标扩库班次驱动**：无自动提案-评审-注册闭环。
4. **research/ 休眠模块**：factor_mining_pipeline.py/factor_vote_mining.py 零接线，占维护面不产价值。
5. **双调度体系并存**：lane C/C4=Windows 计划任务、数据=APScheduler，无统一可观测（日志散落 .runtime/logs/）。
6. **候选验收线偏松**：lane C2 MIN_INCR_IC=0.0（描述性证据，终审推给 E2/E4）——次名 incr_ic 0.0052 亦入库，E2 预审压力后移。

## 5 施工项建议

**本班施工（若施工班接单，按优先序）**：
- **N1 图形态道自动化第一批**：新建 `scripts/factor/pattern_auto_quantifier.py`（消费 chart_pattern_registry.yaml 中 algorithm_status=pending_backtest 且识别规则可代码化的 candlestick 77 条先行——TA-Lib 61 函数有现成映射）；产出追加出生证 CSV（复用 lane_c 出生证 schema，birth_channel="P"）；验收=≥60 条 candlestick 完成量化+win_rate 表可查+零人工介入连跑 3 个交易日。
- **N2 lane C2 验收线收紧**：`lane_c2_agentic_miner.py` MIN_INCR_IC 由 0.0 提为 0.01（或 IC 显著性 t 检验 n≥1000）；验收=次名 0.0052 类候选不再入库，E2 预审积压下降。

**挂起排期（写明解锁条件）**：
- H1 AlphaGen RL 轨立项（解锁：lane C/C2 候选共线冗余实证，或 gplearn 搜索收益连续两批 <1 条入选）；
- H2 另类数据落库管线 F1-F3+F13（解锁：Owner 完成 S00 账号注册+10 月中 C-3 排期到点；方案真源=alt_data_consumption_plan.md）；
- H3 research/ 休眠模块处置（解锁：挖后自审闸裁定——factor_factory mining_hook 若终局不用则方案封矿删除）；
- H4 因子-模型联合优化环（RD-Agent(Q) 式；解锁：E4 批考首跑产出真实战绩反馈）；
- H5 Alpha158/101 横评基准（一次性脚本，解锁：REG-IND-001 扩库争议出现时）；
- H6 调度体系统一（解锁：Windows 计划任务出现失联事故）。

## 6 封矿结论

- 内部 6 向+外部 4 轮全 signal，无 noise 轮——**矿脉未枯，时间盒封批**。
- 长尾矿脉登记（未挖，非封矿）：①缠论/Elliott 类主观形态的量化可行性专项（registry 已有 v2.2 refinements 字段承载）；②LLM 挖矿的 prompt 进化策略（FITEE 综述分类学可作提纲）；③factors 赛马计分板的前端呈现（S13 边界）。
- 方案封矿：无（本环节全部发现终局有位置）。
