---
ttl: task_bound
title: L4 对比段——通用对比器真源设计稿 v1
owner: ZephyrAlpha-Owner
session: st-ailayer-20260917
date: 2026-09-17
status: design_v1
---

# L4 对比段真源设计稿：通用对比器（考卷统一、裁定统一、独立性机检）

> **本文性质**：骨架卡挖干产出=可直接施工的设计真源。上承骨架卡（README.md）、主文档定调
> 六/七/八/11/12（ai_layer_vision_and_roadmap_v1.md §0.5）、V2 报告 DGM objective hacking
> 反面实证。**核心裁定 D-L4-01：L4 不自建考尺，做"协议层+登记层"**——考尺全部复用既有/在建
> 件（C4 双窗/OBJ_R 重放器/OBJ_M 三把尺/OBJ_T 基准集），L4 供给五样公共品：统一考场矩阵、
> 公平性对齐、判据预注册登记、显著性分级判据、too-good 三查与独立性机检。施工另走
> construction_workflow_policy。**硬边界自守**：本轮只写 L4_compare/ 目录内文件，零代码。

---

## 1. 六向寻路台账表

| # | 向 | 内部反查命中（真源路径） | 外部补盲 | 判定 |
|---|-----|------------------------|---------|------|
| ① | 上游（谁喂 L4） | `L2_intake_library/DESIGN.md` 事件表（`intake_clean_due`→L3，L3 完成回写 spec_ref+stage=E2 前态）；`L3_cleaning/README.md`（输出=规格卡→L4）；库外对象直入（OBJ_M M1 情报卡→M3 考试、OBJ_R 标准提案、L5 施工件回归） | — | signal |
| ② | 下游（谁吃 L4） | L2 事件表已预留 L4 位：`intake_scored_due`（回填 elite_score/verdict win|draw|loss）+`intake_reject_due`（退阴性）+`intake_e2_handoff`（L2→L5 唯一产线出口）；`L5_schedule_gate/README.md`（输入=L4 胜者带证据包→工单）；`L7_heredity/README.md`（输入=判据档案） | — | signal |
| ③ | 算法机制（怎么判优） | 策略级：`scripts/backtest/c4_batch_screen.py`（IS 冻结窗 2020-01-01..2023-12-31/OOS `--start --end`/DSR 批内折减委托 `src/zephyr/backtest/regime_validation/c4_deflated_sharpe_runner.py`）+`src/zephyr/strategy_pipeline/screen_source.py` fetch_bothwin；因子级：`src/zephyr/factor/analysis/bhy_fdr.py`（BHY FDR q=10%+ICIR≥0.5 硬门禁现行真源）；规则级：`OBJ_R_rules_standards/DESIGN.md` §② 重放器（Jaccard 主判据+P1-P4）；模型级：`OBJ_M_models/DESIGN.md` §4 三把尺（McNemar/Wilcoxon/单价口径）；护栏栈：`src/zephyr/backtest/core/overfitting_adjudicator.py` 三检验器（WFO 衰减/DSR/参数扰动，现未接门禁=可复用件） | 泄漏分类学：Kapoor & Narayanan "Leakage and the Reproducibility Crisis in ML-based Science"，Patterns 2023，八类泄漏分类+329 篇受影响论文（pubmed.ncbi.nlm.nih.gov/37720327 / arxiv.org/abs/2207.07048，EX-R2 第 4 次重试成功） | signal |
| ④ | 后端（落哪个仓/什么件） | 判据常量→`config/`（新建 comparison_policy.yaml，对标 alert_threshold_registry.yaml REG-ATH-001+threshold_loader 外置化母版）；实验卡→PG 同实例**独立 schema `ai_compare`** 新表（与 L2 ai_intake schema 隔离，产线禁读界不破；经 `src/zephyr/infrastructure/database_service.py`，禁裸连接）；run 档案先例=`data/backtest_artifacts/runs/`（22 个 SCR-C4 档案）；gate 触发数据=`.runtime/audit/gate_execution_stats.jsonl` | — | signal |
| ⑤ | 前端（裁定呈现） | 复刻 S13 promotion 先例（`src/zephyr/frontend/dashboard/web/features/promotion/promotion.js`+api_server 只读路由）：裁定卡=只读 API+JS 渲染，Owner 只读（登记不施工，归 L5/L6 呈现件） | — | signal（登记不施工） |
| ⑥ | 数据字段（记什么） | 任务书 schema v0 附录 A（definition_of_done 预注册/acceptance.reviewer 异会话异档/pre_rulings）；附录 C #5 验收判据自改=根约束禁区；OBJ_M M2 exam_suite_version 必记字段（防题库污染）；L2 卡 elite_score/elite_rank/elite_status 回填位已留；`config/resource_profile_registry.yaml`（排班 v1 互斥组/E0 算力档词表） | — | signal |

**受阻记录**：EX-R1（specification gaming 谱系核验）429×4（60-130s 间隔重试）未取到实时结果——DeepMind "Specification gaming: the flip side of AI ingenuity"（Krakovna 系）为通行引文，本稿仅作查钻营 checklist 思想锚点不引具体条目，**URL 补核挂单进 C6 验收标准，未编引文**。

---

## 2. 真源设计

### 2.1 考场矩阵（每类对象的对比方案+现状基准读取路径）

| 对象类 | 考场（怎么比） | 制式要点 | 现状基准从哪读（真实路径） |
|--------|---------------|---------|--------------------------|
| **模块** | 基准任务集=tests 全绿+gate 链全绿+depgraph/全景对齐；涉策略路径的模块加挂 C4 双窗实测 | 考卷=现行 tests 套件+受影响域测试（禁"自家考卷自家出"：任务书 definition_of_done 预注册受影响域清单）；机械二元判定（§2.4 Tier C） | 候选 vs 现行版本：`tests/`、`docs/03_modules/**/blueprint.md`、ALGO_FLOW 全景（candidate_module_registry.yaml）、`alignment_checklist.md`（align_all.py 单入口，对齐键=module_id/step_id）、gate_registry.yaml |
| **算法选型** | **锦标赛制式（D-L4-02）**：候选全员同批入 C4 双窗批考=IS 窗初赛（84 件规模已验证）→OOS 窗复赛（双窗齐才 emit）→DSR 批内折减→BHY FDR 多重校正→bothwin 终裁。多候选同批（N≥5）时按 IS 排名取前 K 进 OOS（省算力，K 进常数文件）；轮次=2 轮固定，不加赛 | 裁决流程：单件 IS 成绩→批内 DSR 折减（试验数膨胀）→同批 p 值族 BHY 校正（q 进常数文件）→双窗 bothwin（IS>0∧各 OOS 段>0∧decay<0.5）→出口裁决列（S06-G3 方案对齐）；Kronos 基线=每批机器对手盘必比 | `data/backtest_artifacts/runs/` SCR-C4 档案+strategy_screen 台账（`src/zephyr/strategy_pipeline/screen_source.py` fetch_bothwin）；现行冠军=台账 bothwin 现役集；基线=Kronos 输出（基线轨在档） |
| **门禁参数** | **OBJ_R 历史重放器复用，不重建**：新阈值 vs 现行常量对历史提交集重放（内存 stub gateway，first-parent diff 纯函数对照），判据=P1-P4（放走=0/误拦≤2%/Jaccard≥0.98·0.95） | L4 只做两件增补：①重放前把 P1-P4 判据冻进 experiment 卡（预注册时序机检）；②重放结果回填统一裁定卡 | 现行阈值=各 gate 模块常量（_MAX_COMPLEXITY=15/_HARD_LIMIT=120 等）+`in_process_gate_registry.yaml`；触发数据=`.runtime/audit/gate_execution_stats.jsonl`+gate_runs 表；判据真源=OBJ_R_rules_standards/DESIGN.md §②-E |
| **模型** | **OBJ_M 三把尺引用，不重建**：①MCE 能力考试（127 题五轴九维）②同任务双跑（五层×20 分层抽样，McNemar/Wilcoxon）③成本审计（时段加权单价） | 考纲细化/通过判据全按 OBJ_M DESIGN §4 原文执行（含 API 只跑 Quick/Standard、裁判异厂异档）；L4 增补=experiment 卡登记+too-good 三查挂接（基准记忆防备=变体题冒烟重考） | 现状基准=model_registry champion+护照（passport_version/exam_suite_version，`src/zephyr/intelligence/model_profiling/exam_test_cases.py` 考题真源）+`config/model_routing_policy.yaml` 现行轨+`config/model_pricing.yaml` 牌价 |
| **工具** | **OBJ_T 基准任务集引用，不重建**（OBJ_T 卡待深挖，L4 先锁制式）：同基准任务集版本双跑（同工具族新 vs 老），判成功率/速度/成本；小样本按 Tier B 诚实条款（未决不硬判） | 工具-模型配对实验借用 OBJ_M dual_run 执行器（OBJ_M §7 已预留）；删除类工具专项红线走 OBJ_S | 现状=capability_cards（data/capability_cards/ 33 件工具卡）+工具坑集（OBJ_T 待建，建后挂本行）；基准任务集真源=OBJ_T 目录（建成后此处引用） |
| **成本线/降档规则** | 历史重放（OBJ_R 重放器同构，换数据底表）：新降档规则对近 30 天 usage_records 重放算总成本/性能档命中，对比现行规则 | 数据只读（usage_records=SQLite governance.db 经 `src/zephyr/infrastructure/cost_tracker.py`）；判据=总成本降幅≥门槛 且 关键任务档位零降级 | `config/budget_policy.yaml` 现行五级阈值+degradation 阈值族；用量底表=usage_records |
| 骨架级/排班表自身 | **不进自动判据**（定调 #9：骨架级=AI 提案+Owner 前端一键确认；先他指后自指） | L4 只产证据包（利弊对照表），裁决权在 Owner 门位 | risk_tier_registry.yaml（域→tier→human_gate） |

**考场边界声明（红蓝 R1，L4/L5 双稿同款）**：策略候选的考场止于 L4 证据包产出；转正/流转归
业务层 S12-S14 与 Owner 拍板，AI 层不设第二转正门；交易算法专域不在 AI 层自动流转范围
——本表"算法选型"行的 verdict 只是证据，不构成任何策略上线/转正动作。

### 2.2 公平性规则（防"新候选吃更好资源"的假胜）

三轴对齐+三条防假胜，全部进 experiment 卡作**机检字段**，对齐器（施工项 C5）检查不等即**拒考**（fail-closed）：

| 轴 | 对齐机制 | 机检字段 |
|----|---------|---------|
| 同算力档 | challenger 与 champion 的考卷消耗同 compute_class（E0 闸词表）；同互斥组窗口（resource_profile_registry）；API/子代理消耗同配额池预算（定调 #10 进化也要配额） | compute_class_challenger == champion；quota_ref |
| 同数据窗 | 策略=同 IS 冻结窗+同 OOS 窗（window_for 真源）；规则=同历史提交集同分层种子；模型=同任务池同 seed 同层；工具=同基准任务集版本号 | window_spec / seed / task_suite_version 逐项相等 |
| 同时间预算 | 同墙钟上限+同 timeout+任务书 budget.timebox 同档；成本口径统一（时段加权：谷时×0.5、免费窗×0，OBJ_M §4.3 同款） | wall_clock_cap / cost_accounting_version |

防假胜三条：

1. **champion 必须同场重考**：禁引 champion 历史成绩跨考纲对比——只有考卷版本（exam_suite_version / 基准任务集版本 / 重放提交集快照）完全相同才允许引用历史成绩，否则同场重跑（OBJ_M M2 exam_suite_version 必记字段的全仓推广）。
2. **新资源通道同等开放**：考期恰逢免费窗/新算力上线时，challenger 用了 champion 也必须可用；对齐器检查 resource delta 非零=记录并降级为"带星胜"（win*，L5 排产降优先级）。
3. **同批同判据**：锦标赛同批候选共用同一份 frozen 判据卡，禁逐候选微调门槛（改判据=新 experiment 全批重考）。

### 2.3 判据预注册登记形态（目标常数的落地，对接任务书 definition_of_done）

双层结构（D-L4-03）：

- **常量层（尺子，治理层资产）**：`config/comparison_policy.yaml`（新建）——显著性 α、效应量门槛、锦标赛 K、too-good 触发线、公平性词表、阴性拒绝理由受控词表。改动走 OBJ_R 四步流水线（AI 提案→治理立案→Owner 修标→重考历史），**AI 层不持尺**。
- **实例层（考卷，一场一张卡）**：PG 同实例独立 schema `ai_compare` 新表 `ai_compare.ai_comparison_experiment`（**与 L2 ai_intake schema 隔离，产线禁读界不破**；经 DatabaseService，TIMESTAMPTZ）：`experiment_id(EX-<yyyymmdd>-<slug>) / 对象三方(challenger_ref, champion_ref, venue_ref) / criteria_yaml(canonical 文本) / criteria_hash(sha256) / status(frozen→running→verdict→archived) / 公平性字段组 / verdict / evidence_ref / evaluator_session / contractor_session / created_at / frozen_at`。

锁定机制（三道）：

1. **时序锁**：考卷先于开工——experiment 卡 status=frozen 且 criteria_hash 写入任务书（task_order 的 definition_of_done 锚点增补 `criteria_ref: <experiment_id>#<hash>`），L5 工单生成器机检 hash 缺失/不匹配=不许派工（附录 A"缺字段不许派工"同款）。
2. **不可变锁**：frozen 后 criteria_yaml/criteria_hash 字段 UPDATE 拒绝+审计告警（status 流转与 verdict 字段除外）；变更判据=新 experiment_id（OBJ_M C5 freeze_rule 同款；附录 C #5 验收判据自改=根约束禁区）。
3. **哈希锁**：执行器开考前重算 criteria_yaml 哈希比对，不匹配=拒绝执行（防 DB 外篡改）。

### 2.4 显著性门槛：工厂 FDR/DSR 思想的适用性分析（分级判据）

**适用性裁定（D-L4-04）**：FDR/DSR 能不能上，取决于"对象能不能算分布"——逐类分析后分三档+一个确定性对照档，禁跨档硬套统计：

| 档 | 对象 | 判据（复用什么） | 理由 |
|----|------|----------------|------|
| **A 分布充分** | 算法/策略（收益时间序列）、因子（IC 序列）、模型双跑（大 N 成对样本） | 策略：DSR 折减+OOS decay+bothwin（C4 现行）；因子：BHY FDR q=10%+ICIR≥0.5（bhy_fdr.py 现行真源）；模型双跑：McNemar（二元）/Wilcoxon（连续）p<0.05+效应量（OBJ_M §4.2 现行门槛：胜=+5pp 显著，成本主张=−20% 且非劣） | 有分布有样本，多重检验纪律必需（锦标赛=选择偏差天然温床，DSR 折试验数膨胀+FDR 校正恰是对症） |
| **B 有限样本** | 工具基准（5-10 题）、模型双跑层内可判件<10、任何 N<30 场景 | 效应量门槛+置信区间全宽报告+**未决诚实条款**（判不了记"未决"不硬判，OBJ_M 同款）；多重比较仍做但结论只降不升 | 样本撑不起 p 值，硬算=伪精确；诚实条款防"凑显著" |
| **B' 确定性对照** | 门禁参数重放、成本线重放 | 非统计推断：Jaccard 集合判据+P1-P4（OBJ_R）/成本差值判据——同输入必同输出，报精确差值不报 p 值 | 重放是纯函数对照，套统计=范畴错误 |
| **C 机械二元** | 模块（tests+gates） | 全绿/非绿，无推断 | 二元机检无分布概念 |

**锦标赛专属纪律**：同批 N 候选选优后报告冠军成绩，必须过 BHY 校正（q 值进常量层）——DSR 思想（"选过之后再报告，显著性就要折减"）对锦标赛是强制的，不是可选项。

### 2.5 too-good 三查流程化（好到反常与坏到反常同一条 anomalous 路线）

**触发线（量化定义，初值进常量层预注册，Owner 点头前为自裁建议值）**：

| # | 对象 | 触发线 |
|---|------|--------|
| G1 | 算法/策略 | OOS 优于 IS（oos_years_decay<0）；或 OOS 夏普超 IS+3σ；或成绩超同批分布均值+3σ；或 DSR≥0.99 |
| G2 | 模型 | 成功率≥champion+20pp；或幻觉率=0；或实测单价降幅≥50% 且成功率非劣 |
| G3 | 工具 | 基准任务集 100% 全对且任务集含已知陷阱题 |
| G4 | 门禁/成本重放 | delta 全零完美（Jaccard=1.0 且零 new_block 零 new_pass）——stub 失真嫌疑优先于庆祝 |
| G5 | 通用 | 连续≥3 场"恰好压线胜"（判定值与门槛差<ε，ε 进常量层）——钻营预警 |

**三查步骤**（每查有 checklist 骨架，结论三值：found/cleared/inconclusive）：

1. **查泄漏 leakage**：对照 Kapoor & Narayanan 八类分类学逐项过——时序窗重叠/预处理泄漏（全量归一化后再切窗）/重叠加窗/非独立样本；模型类加考题污染（考题或变体出现在候选的清洗语料/训练材料——MCE RISK-3.4 同源风险）；机检=考卷 sha256 vs 候选接触记录比对。
2. **查隐性风险 hidden_risk**：收益分布尾部（偏度/最大回撤/tail ratio）——"稳定小赚+尾部爆仓"卖保险形态；参数扰动敏感性（overfitting_adjudicator 检验器③可复用，现未接线正好此处消费）；容量/滑点/手续费假设敏感性；模型类加胜例定性抽检（胜例同质化=只会一种题）。
3. **查运气/钻营 luck_or_gaming**：多重比较复算（同批候选数与 BHY 校正后 q 值——赢在没校正前=运气）；种子/窗口敏感性（换 3 种子+滚动窗重跑，排序不稳=过拟合考纲）；近亲繁殖检查（候选与考卷同源同作者，L2 simhash+L7 先验）；基准记忆（模型类=变体题冒烟重考）；specification gaming 自问一句（业界思想锚，EX-R1 受阻待补核）："候选是不是在优化考卷而不是优化目标？"

**三出口**（裁定写进 experiment 卡，全部留痕）：

| 出口 | 动作 | 权限 |
|------|------|------|
| E1 改考场重跑 | 换考卷版本/换种子/换数据窗重考（新 experiment_id）；三查发现可修复泄漏时唯一出路 | 出卷权=评估者会话+治理层考纲；施工会话无权改考 |
| E2 接受但加监控 | 进 L6 观察期加严：观察期顶格 3 个月+提前回切线收紧两档+月度体检强制项（监控指标清单写进 experiment 卡随行） | 评估者裁定，L6 消费 |
| E3 驳回 | verdict='rejected_too_good'+归因枚举三选一（leakage/hidden_risk/luck_or_gaming）→阴性库；同 simhash 换皮被 L2 闸 5 拦 | 评估者裁定 |

### 2.6 评估者独立性：施工会话无权出考卷/改考卷的机检点

DGM 教训（V2-R5）的机制化落地，七道机检（前五道进执行器，后两道进治理流程）：

1. **会话互斥**：experiment 卡 contractor_session（提案/清洗/施工方）≠evaluator_session（出卷+裁定方），执行器机检相同=拒考；L4 裁定卡由 evaluator_session 签发。
2. **异档异厂**：模型裁判档位 premium 且与被测异厂（OBJ_M RISK-3.2 复用）；复核会话异会话异档（主文档 §3.2 验收三级协议复用）。
3. **时序锁**：criteria_frozen_at < 任务书派发时间 < 首个施工 commit 时间（三时间戳机检，倒挂=拒绝）。
4. **不可变锁**：frozen 后判据字段 UPDATE 拒绝+审计（§2.3）；施工会话 commit 触达考卷文件/experiment 卡判据字段=gate 阻断（对接附录 C #5；新 gate 立案归 OBJ_R 流水线，见待 Owner-2）。
5. **路径分离**：考卷真源（基准任务集/重放抽样集/考题/判据常量）在治理层路径（config/+data/ 基准目录），候选实现禁写考卷路径；考卷文件 sha256 开考前登记、考后复核。
6. **出卷权归属**：考纲/考卷常量=治理层资产，AI 层只有使用权+提案权（README §1.6 归属裁定；运动员不持尺）。
7. **翻案通道**：被拒方申诉=新 experiment（新考场/新判据常量走 OBJ_R），禁改旧卡——旧裁定只增不改，翻案走 ruling_registry 登记。

---

## 3. 接线图（四契约+两增补边）

| 对端 | 契约 | 方向 | 载荷 |
|------|------|------|------|
| **L3（规格卡输入）** | L3 完成回写 spec_ref（L2 库 stage=E2 前态）后，**增补事件 `intake_exam_due`**：L2 emit、L4 领考。该边在 L2 设计稿事件表中未列（其表止于 clean_due/handoff），需 L2 侧实施时对齐（待 Owner-3） | L2/L3→L4 | {card_id, spec_ref, domain_id, mechanism_family, four_gates} |
| **L5（胜者输出→排产）** | 双路：①库内对象走 L2 既有 `intake_e2_handoff`（payload 增补 evidence_ref=experiment_id 一字段，R2 已经 L2 稿同批落地）；②库外对象（模型/工具/门禁/模块）=experiment 卡 verdict='win' 即门闸输入，L5 工单生成器读 criteria_ref+evidence pack 套任务书 schema（definition_of_done 锚 criteria_ref） | L4→L5 | verdict + evidence_pack {experiment_id, criteria_hash, 判据结果, significance, too_good 结论, 公平性核验} |
| **L2（败者→阴性库）** | 原样对齐 L2 已定义两事件：败者/平局 `intake_reject_due` {card_id, stage:'L4', rejection_reason(受控词表), evidence_ref}；出分回填 `intake_scored_due` {card_id, verdict:'win'|'draw'|'loss', score, evidence_ref}（触发 L2 保优 benched 机制） | L4→L2 | 如 payload。**平局裁定（D-L4-05）**：平局=维持现状，rejection_reason='tie_no_gain' 入阴性视图，但带**可重考条件**（考纲版本变更/数据窗滚动进新数据/公平性参数变化时 L4 重开考），与败者永久阴性不同 |
| **L7（判据档案回写）** | **增补事件 `comparison_archived_due`**：experiment 卡 archived 时 emit，L7 判据档案收"当时为什么算它赢"；反向=L4 领考前调 L7 只读服务 comparison_prior_query(simhash/mechanism_family)→历史裁定列表，同候选已考直接引用旧裁定防重复考古 | L4↔L7 | {experiment_id, criteria_yaml, verdict, 归因, too_good 出口} / 查询→{历史 experiment 列表} |
| **目标常数段** | 判据常量真源=config/comparison_policy.yaml=目标常数段的落地件之一；改动走 OBJ_R 四步+Owner 门（§2.3） | L4←常数 | α/门槛/触发线/K/受控词表 |
| **OBJ_M/T/R（考尺供方）** | 考场适配器薄封装调用（不重建）：各家出证据包，L4 出统一裁定卡 | L4→调用 | 各家 schema 见 §2.1 现状基准列 |

---

## 4. 施工项清单（全部为设计交付，施工另派工，本轮零代码）

| # | 项 | 文件（新增/修改） | 验收标准 |
|---|-----|------------------|---------|
| C1 | 判据常量文件 | `config/comparison_policy.yaml`（新增，带治理锚定头） | 全部常数齐（α/效应量门槛/K/触发线 G1-G5/ε/受控词表）；Owner 点头记录；改动走 OBJ_R 流水线 |
| C2 | 实验卡库表 | PG 同实例独立 schema `ai_compare` 新表 `ai_comparison_experiment`+DDL 登记器（挂 L2 的 apply_ai_intake_ddl.py 同模式；与 L2 ai_intake schema 隔离，产线禁读界不破） | 全经 DatabaseService（禁裸连接）；TIMESTAMPTZ；frozen 后判据字段 UPDATE 拒绝有测试；append-only verdict |
| C3 | 对比执行器 | `src/zephyr/ai_layer/comparator/`（新增模块：领考/哈希校验/公平性机检/裁定卡产出） | 会话互斥+时序锁+哈希锁三检有测试；新模块登记 add_module_translation+CREATE-GUARD+RULE-DEPGRAPH |
| C4 | 考场适配器×4 | 同目录 venue_c4.py / venue_replay.py / venue_dual_run.py / venue_tool_bench.py（薄封装） | 各适配器零复制考尺逻辑（只转调既有件）；调不到考尺=fail-closed 拒考 |
| C5 | 公平性对齐器 | comparator 内 fairness.py | 三轴+防假胜三条全机检；不等=拒考且留 reason；"带星胜"降级路径有测试 |
| C6 | too-good 三查执行器 | comparator 内 too_good.py（触发线检测+三查 checklist+三出口流转） | G1-G5 触发线可配置读常量层；三查结论三值枚举；E1/E2/E3 流转留痕；specification gaming 引文补核完成（EX-R1 挂单在此销账） |
| C7 | 独立性 gate 立案 | （归 OBJ_R 流水线，非本卡施工）判据文件保护 gate+任务书 criteria_ref 机检 | 提案进治理层标准库；gate 上线前过 OBJ_R 历史重放 |
| C8 | L7 回写接线 | `comparison_archived_due` 事件+comparison_prior_query 只读服务（对齐 L2 events.py 模式） | 事件触发零定时器；先验查询只读；L7 卡实施时消费 |

依赖序：C1→C2→C3→(C4/C5/C6 并行)→C8；C7 独立走 OBJ_R。全部走 worktree 隔离+网关提交+改前 claim；测试禁写生产路径（tmp_path fixture）。

---

## 5. 挖矿日志表+自审闸三态裁定

### 5.1 挖矿日志

| 轮次 | 矿脉 | 判定 | 关键产出 |
|------|------|------|---------|
| IN-R1 | 上/下游段卡与 L2 事件契约 | signal | L2 DESIGN 事件表已预留 intake_scored_due/intake_reject_due/intake_e2_handoff+elite 回填位——L4 契约半数现成 |
| IN-R2 | 策略考场现状（S06 挖矿文档） | signal | C4 双窗编排已落地（IS defer-emit+OOS auto）/DSR 记录级/bothwin 在 S07/overfitting_adjudicator 三检验器在库未接线=三查②可复用件 |
| IN-R3 | 统计判据现行真源 | signal | bhy_fdr.py（BHY q=10%+ICIR≥0.5 硬门禁，#2 因子 IC 双轨裁定）；c4_deflated_sharpe_runner（DSR SSOT） |
| IN-R4 | 姊妹设计稿（OBJ_R/OBJ_M） | signal | 重放器 P1-P4+Jaccard 主判据/三把尺+exam_suite_version+freeze_rule——L4 两类考场零重建 |
| IN-R5 | 任务书 schema 与根约束 | signal | 附录 A definition_of_done 预注册+acceptance 异会话异档；附录 C #5 判据自改=禁区——预注册登记的对接锚全齐 |
| IN-R6 | 既有失败先例 | signal | DSR None 不阻断教训（S06 §1.1）→L4 判据器 fail-closed 反向设计；考纲版本漂移（OBJ_M RISK-3.4）→同场重考铁律 |
| EX-R1 | specification gaming 谱系 | **受阻** | 429×4（60-130s 间隔）未取实时结果；仅作三查③思想锚不引条目，补核挂单 C6。受阻≠查无，未编引文 |
| EX-R2 | 泄漏分类学 | signal | Kapoor & Narayanan（Patterns 2023，arXiv 2207.07048，八类泄漏/329 篇受影响）——三查① checklist 骨架（第 4 次重试成功，纪律内） |
| REUSE | V0-R2/R3+V2-R1/R5 | signal（在档复用） | AlphaEvolve evaluators/DGM objective hacking/champion-challenger——同源两处消费，交叉验证闸满足 |

### 5.2 自审闸三态裁定

**裁定=施工**（本设计稿定稿+README 状态翻转）。理由：①L4 是咽喉段（骨架卡自评优先级仅次于 L2），且契约半数已被 L2/OBJ_R/OBJ_M 预留到位，本稿是把预留接成协议——不是新发明；②过度工程检查：零代码、两件"重建"诱惑（通用考尺/自建统计器）均被 D-L4-01/D-L4-04 否决为薄封装+复用；③无套娃：判据常量归治理层，L4 自身升级也走 OBJ_R；④两问自答——好在哪=把"判优"从无协议变成预注册+公平性+独立性机检的统一协议（现状：策略级有 C4 但模块/门禁/模型/工具各说各话，无统一裁定卡）；消灭哪段人工=人工圈合格者（S06 终局视角同款）/人工判"新比旧好"/人工查反常成绩。反省：触发线初值（3σ/+20pp/50%/ε）是**设计定值非实测标定**，全部收进常量层预注册，首轮实考数据回来后按 OBJ_R 流水线提案修订——不在本轮拍死。

### 5.3 待 Owner（4 项）

1. **判据常量初值点头**：config/comparison_policy.yaml 全部常数（触发线 G1-G5/α/效应量门槛/锦标赛 K）——尺子归 Owner 修标。
2. **独立性 gate 立案准许**：判据文件保护 gate+任务书 criteria_ref 机检=治理层 gate 资产变更，提案经 OBJ_R 四步立案（C7）。
3. **两条增补边的跨稿对齐确认**：`intake_exam_due`（L2→L4）与 `intake_e2_handoff` payload 增 evidence_ref——R2 更新：后者已经 L2 稿同批补入 payload；且 L2 侧同名回执事件已改名 `intake_exam_receipt` 拆分，本项仅余派考边 `intake_exam_due` 的跨稿确认。
4. **creation_token 补登**：本班硬边界"禁登记 token"，DESIGN.md 的 creation_token 由主会话/Owner 补登（OBJ_R 稿同款先例）。

---

## 修订记录

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-09-17 | design_v1 | 初稿：六向台账（8 signal/1 受阻）+考场矩阵七行+公平性三轴+判据双层预注册+显著性四档+too-good 三查流程化+独立性七道机检+六契约接线+8 施工项+4 待 Owner |

---

## 红蓝 R1 修复记录（2026-09-17，修复组 2）

- **B9（新表落"ai_intake 同实例"未指 schema，违 L2 §2.1 产线禁读界）**：实验卡表改落 PG 同实例**独立 schema `ai_compare`**（表=`ai_compare.ai_comparison_experiment`），三处同步（§1 台账④行、§2.3 实例层、C2 施工项），均加"与 L2 ai_intake schema 隔离，产线禁读界不破"；仍同 PG 实例、全经 DatabaseService、禁裸连接。
- **第 7 项（跨稿边界声明，L4+L5 同款）**：§2.1 表后新增"考场边界声明"——策略候选的考场止于 L4 证据包产出；转正/流转归业务层 S12-S14 与 Owner 拍板，AI 层不设第二转正门；交易算法专域不在 AI 层自动流转范围。
- 连带核查：experiment 卡字段与 status 流转零变更；L5/L7 契约不受影响；DDL 登记器沿用 L2 母版模式，仅建表语句挂 `ai_compare` schema。

## 红蓝 R2 修复记录（2026-09-17，红队 R2 发现）

- **R2（同名事件冲突拆分+节锚漂移）**：L2 侧回执事件改名 `intake_exam_receipt`（payload 删未定义的 intake_id），本稿 §3 `intake_exam_due`（L2→L4 派考）**保留原名不变**——同名冲突消解，两事件方向/载荷不再交叠；§2.6 第 2 道机检锚的过时节号（v2.0 节号漂移）改指"主文档 §3.2 验收三级协议"，grep 零残留。连带核记：§3 L5 行与待 Owner-3 的 evidence_ref 增补已经 L2 稿 R2 同批落地，挂单仅余派考边跨稿确认。
