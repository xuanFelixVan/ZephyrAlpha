---
doc_type: policy
ttl: permanent
title: 全自动研究生产线运营 SOP（九口出料·挖考判晋反馈闭环）
status: active
version: 1.0.0
date: '2026-10-14'
owner: ZephyrAlpha-Owner
---

# 全自动研究生产线运营 SOP

> **一句话定位**：从找数据到出成绩的整条业务线自动化流水线的岗位运营标准——13 个岗位各自的目标/输入口/输出口/工作流程/保底绩效/自检制。
> **机构对标命名**：Research Pipeline / Alpha Production Line（WorldQuant Alpha 平台流水线）/ Research-to-Production（MLOps 连续训练 CT）。本仓叫**全自动研究生产线**。
> **分工矩阵**（防双真源）：挖矿方法论=`mining_sop/`（六向/封矿核验）｜考试回测方法论=`backtest_system_sop/`（四卷+exam_policy）｜数据生命周期=`data_ops_sop/`｜班底编制与切碎机制=`automation_sop/automation_crew_policy.md`｜**本册只写"生产线岗位怎么运转"：输入输出口、流程、绩效、自检**。
> **净零声明**：本册收拢讨论册（docs/_working/cmd_ledger/automation_plan_discussion.md）与四域施工战报中的口头流程成文；不新增 gate/规则/注册表；handoff 新路径仅限 docs/_working/automation_campaign/ 下（ttl 面由 frontmatter 自带）。
> **总原则**：只有考试口径的成绩算数（引擎直跑数字仅参考）；先冻结判据后跑数（裁定#518）；fail 不得升级 verified；负结果如实入册也是成绩。

## 1. 主干传送带总图

正向主流：**①数据源 → ②③挖矿 → ⑤实现 → ⑥制卡冻结 → ⑦考工 → ⑧判卷 → ⑪晋级/成绩**
数据回流线：任何环缺数 → ①数据源席（全网找→建设→修复）→ 就位解锁；穷尽免费渠道才准断供登记（**必须附找过哪些渠道的证据链，没证据的登记监督员打回**）
成绩回流线：⑧判卷出分 → ⑨成绩分析师归因 → 三联反馈单（挖矿方向单/算法修改单/Owner 呈批件）→ 回流上游 → 复考再考（**优化后再考必须走对照卡 A/B**）
监督线：⑪监督员巡全线水位/断线/指令质量（可改指令面，禁碰判据门柱）
出料九口：见 §2——一条传送带，九个出料口，按卡族路由。

既有机器层三件（对话席不重复其工作，只消费其产出）：`scripts/tasks/run/run_night_mining.ps1`（Task Scheduler 23:00 Sun-Thu，lane_b/lane_c3 候选）｜`scripts/tasks/run/run_c4_exam.ps1`（夜间考试批）｜`scripts/tasks/run/run_f06_grid.ps1`（周六 08:00-22:30 参数网格窗）。

## 2. 九类成绩出料口映射（哪些已入线、并行度）

| # | 成绩类别 | 出料通道（考试口） | 上游喂料 | 入线状态 |
|---|---|---|---|---|
| 1 | 组合参数网格 | F06 周六窗（机器） | 参数空间 prereg（config/search_space_prereg.yaml f06_grid_v2） | ✅在跑 |
| 2 | 注册册策略 | strategy 考试口 | 策略挖矿+④战法全网矿工 | ✅可并行 |
| 3 | 指标考试批 | indicator 考试口 | TASC 指标挖矿 | ✅可并行 |
| 4 | 因子重考 | factor 考试口 | 因子挖矿（八段） | ✅可并行 |
| 5 | 分配器影子考 | allocator 考试口 | 分配器实现 | ✅可并行 |
| 6 | 防守机制对照（ATR 型） | **对照卡** | 环节假设+对照卡制作 | ⛔阻塞：对照执行器缺位（OD-1） |
| 7 | 引擎直跑数字 | （参考值，不入成绩正册） | — | 不入线 |
| 8 | 负结果 | 各口 fail 如实入册 | 全部 | ✅纪律面 |
| 9 | 环节考试卡 | 校准/消融/影子/对照四族 | 六向挖矿（186 节点 7 车道） | ✅主战场 |

并行度：2/3/4/5/9 五口同时开（考试通道互不抢）；1 口周六独占；6 口等 OD-1 立项。挖满一个矿脉→轮转下一个（§6）。

## 3. 岗位卡（13 席，每卡八段+真源挂点）

通用规则（适用于全部岗位）：开工冷启动三步；改前 claim 毕后 release；提交唯一正门 git_commit.py --enqueue；**完工自检两轮，连续两轮零问题该批产出才算交付**（第二轮才发现问题=第一轮漏检记缺陷行）；sid=`st-qoder-<岗>-<MMDD>-<NN>`。

### ⓪ 派单员
- **目标**：全线不断料、不堆积、不重复挖。
- **工作内容**：读全线水位与各车道台账，产出当日任务单；查重是硬职责。
- **输入口**：`docs/_working/automation_campaign/pulse/queue_depths.md`（水位，自己维护）；`docs/_working/nightmine_campaign/00_lane_roster.yaml`（186 节点 7 车道）；`docs/_working/nightmine_campaign/L1..L7_ledger.md`（已挖/mined_out 名单）；`docs/03_modules/_domain_backtest/exam_cards/`（卡池状态）。
- **输出口**：`docs/_working/automation_campaign/dispatch/daily_dispatch.md`（每席：对象+数量+优先级+出料口方向）。
- **工作流程**：1 读水位与卡池统计 2 读各车道台账未挖名单 3 查重（对照已挖名单/mined_out/现有卡，逐条核对）4 按瓶颈定配额（哪个环断料加派哪个）5 写任务单 6 标注出料口 7 自检两轮 8 交付。
- **保底绩效**：每日一单；覆盖全部在岗席；查重核对率 100%（漏查重=缺陷行）。
- **自检要点**：任务单每条都有"未挖过"的台账反证。
- **总包**：无需子代理。

### ① 数据源席
- **目标**：数据就位率最大化；断供=穷尽免费渠道后的最后登记，不是逃避登记。
- **工作内容**：全网搜源→评估→建设→修复→（实在找不到才）断供登记。缺数从最源头负责。
- **输入口**：`src/zephyr/data/config/known_data_gaps.yaml`（断供/缺数登记册）；`docs/_working/automation_campaign/feedback/to_owner.md` 中的缺数申请；源线谱 `docs/_working/chain_piling_campaign/02_source_line_registry.md`（29 线现状）。
- **输出口**：源线谱新增行（新源线 memo）；known_data_gaps.yaml 条目翻转（就位/断供+`searched_channels` 证据字段）；回补执行记录。
- **工作流程**：1 读断供表与缺数申请 2 逐项全网搜索（官方免费 API/开放数据/GitHub 数据集/数据商目录，**每项≥3 渠道**，WebSearch 留链接）3 评估（成本/合规/PIT/许可证；花钱采购→出呈批件禁自购）4 可建设→走 `data_ops_sop/data_source_onboarding_sop.md`（报批→建表→接入→接通验收三查）5 坏数据→`data_ops_sop/data_ops_policy.md` 修复流程 6 免费渠道穷尽→断供登记（附渠道清单+失败原因）7 解锁对应卡（翻 known_data_gaps status）8 台账留痕 9 自检两轮。
- **保底绩效**：每班处理≥3 个缺数项；每项≥3 渠道搜索留痕；断供登记 100% 带证据链。
- **自检要点**：每个"断供"结论都能回答"找过哪三处、为什么不行"。
- **真源挂点**：data_source_onboarding_sop（全生命周期）+ mining_sop（全网调研法）。
- **总包**：按缺数项并行搜索（读席并发不限，写登记串行 CAS）。

### ②③ 挖矿席（两席按车道分片）
- **目标**：六向候选持续产出且绝不重复挖。
- **工作内容**：按车道对 186 节点做六向挖（①上游②下游③算法④后端⑤呈现⑥数据），听⑨的方向单调整重心。
- **输入口**：daily_dispatch.md；`docs/_working/nightmine_campaign/01_mining_brief.md`（六向法）；本车道 `L*_ledger.md`（已挖名单+mined_out）；`docs/_working/automation_campaign/feedback/to_miners.md`（方向单）。
- **输出口**：候选→`data/strategy_intake/lane_<x>_candidates.csv`；empty 卡骨架→`docs/03_modules/_domain_backtest/exam_cards/<族目录>/`（schema 照抄样例卡）；台账行追加。
- **工作流程**：1 领车道 2 读台账排除已挖/mined_out 3 读方向单调整重心 4 逐节点六向挖 5 产候选入台账 6 登记 empty 卡骨架（门柱字段全 null，status=empty）7 台账追加 8 自检两轮。
- **保底绩效**：每席每班≥5 个新候选或≥10 张 empty 卡骨架；mined_out 名单核对率 100%。
- **自检要点**：抽 3 条产出反向核对台账确认未挖过。
- **真源挂点**：mining_sop_policy（六向/防噪音四闸/封矿核验）。
- **总包**：按节点并行（读并发不限；写台账/卡串行 CAS）。

### ④ 战法全网矿工
- **目标**：外部战法持续进卡（喂 2/9 口）。
- **输入口**：`backtest_system_sop/sop_c_strategy_library_intake.md` §9（渠道清单+合规铁律）；`docs/01_policies_and_standards/_registry/catalogs/strategy_registry.yaml`（存量去重）。
- **输出口**：战法卡（原文链接/许可证/逻辑描述/伪代码/数据源映射五必备）→`data/strategy_intake/` 战法卡区+候选行。
- **工作流程**：渠道轮转扫描→许可证闸→存量去重闸→写战法卡→登记台账→自检两轮。
- **保底绩效**：每班扫≥5 个渠道/仓库；产≥2 张战法卡。
- **真源挂点**：sop_c 全漏斗（外部代码禁直接复制，只学思想走 C3 重实现）。
- **总包**：按渠道并行。

### ⑤ 实现工
- **目标**：未实现卡清零+按反馈单优化算法。
- **输入口**：exam_cards 中 blocked(未实现)卡；`docs/_working/automation_campaign/feedback/to_impl.md`（算法修改单）；战法卡伪代码。
- **输出口**：码面+测试绿（tmp_path 隔离）→卡翻转 unblocked→移交⑥；修改单落地记录。
- **工作流程**：1 领单 2 读卡需求/修改单 3 模板化实现（真源=construction_sop 15 步）4 测试绿 5 翻卡状态 6 台账 7 自检两轮。
- **保底绩效**：每班≥1 张卡实现或≥1 张修改单落地；测试必须绿。
- **总包**：卡间并行（写域=各自模块不互斥）。

### ⑥ 制卡员（prereg 员）
- **目标**：empty→preregistered；先冻结后跑。
- **输入口**：exam_cards 中 empty 卡；在册冻结值（各域判据册/裁定#518 冻结口径）；呈批回执。
- **输出口**：preregistered 卡（pillars_numeric/window/buckets/data_binding 齐）；语义参数缺→`docs/_working/nightmine_campaign/05_owner_decisions.yaml` 追加呈批项（**一个数不编**）。
- **工作流程**：1 领 empty 卡 2 查在册冻结值（逐字沿用原册，禁自拟）3 有→填门柱 4 缺语义参数→呈批件 5 填齐翻 status=preregistered 6 台账 7 自检两轮（两轮都核对：门柱字段非空且与冻结值逐字一致）。
- **保底绩效**：每班≥5 张或当班领用卡 100% 处置完（含呈批登记）。
- **真源挂点**：backtest_system_sop/exam_policy（E4 口径）。
- **总包**：按卡并行。

### ⑦ 考工（两席，吞吐核心）
- **目标**：成绩产量——每日出分。
- **输入口**：exam_cards 中 preregistered 队列。
- **输出口**：`docs/03_modules/_domain_backtest/exam_scores_v1.yaml` 追加行（**only-add**）；卡 status→examined。
- **工作流程**：1 领卡（按卡族路由考试通道：run_fexam.py 的 factor/strategy/indicator/allocator 子命令或 calibration_exam.py --card）2 核对门柱已冻结 3 跑（CH 窗 01:00-04:00 避让）4 分数入库 5 翻状态 6 失败写堵点册即停 7 自检两轮（核对 only-add 与门柱一致）。
- **保底绩效**：每席每班≥8 张出分，或跑满 4 小时（数量+时长双口径，以先到者计）。
- **总包**：并发≤2（CPU 核限制），两席按卡族分工互不抢卡。
- **真源挂点**：backtest_system_sop/exam_policy+run_fexam.py MOD-BT-FEXAM。

### ⑧ 判卷复核员
- **目标**：成绩真实可信，负结果纪律落地。
- **输入口**：当日 exam_scores_v1.yaml 增量行。
- **输出口**：成绩日报（cmd_ledger 晨报附）+可疑复核单→`docs/_working/automation_campaign/feedback/`。
- **工作流程**：逐行核对门柱一票否决→负结果如实入册核对→IS/OOS 符号观察记录→可疑列复核单→交⑨。
- **保底绩效**：当日增量 100% 复核。

### ⑨ 成绩分析师（闭环之魂）
- **目标**：每条 fail 都变成改进动作，反馈回流。
- **输入口**：成绩日报+fail 行+家族共线性历史（exam_scores 既有 fail 簇）。
- **输出口**：三联单 `docs/_working/automation_campaign/feedback/to_miners.md`（方向单）/`to_impl.md`（修改单）/`to_owner.md`（判据呈批）+复考排程。
- **工作流程**：1 读当日 fail 2 逐条归因四分诊：信号真无效（OOS 翻转）/实现或数据问题/判据问题/需对照验证 3 真无效→方向单（该家族收敛建议或 mined_out 申报建议）4 实现数据→修改单/缺数单给①⑤ 5 判据→呈批件 6 需对照→对照卡制作申请（挂 OD-1，**优化闭环的再考必须 A/B 对照**）7 复考排程 8 自检两轮。
- **保底绩效**：fail 行 100% 分诊；每班≥1 条结构性观察（家族级规律，如共线性簇）。
- **总包**：按家族并行分析（读）。

### ⑩ 晋级/整装员
- **目标**：pass 变 verified 并挂图。
- **输入口**：pass 行+exam_policy 晋级纪律。
- **输出口**：verified 升级行+TDM 挂接（trading_decision_map_sop S1-S9）+promote 建议（模拟盘）。
- **工作流程**：领 pass→核红线（fail 永不升级；W5 confidence 回写待 OD-8 开闸）→挂 TDM→整装回测建议（backtest sop_a）→台账→自检两轮。
- **保底绩效**：pass 行 100% 处置（当前 pass=0，先干存量接线：大盘腿 shadow 转正式等）。

### ⑪ 监督员
- **目标**：全线不断线——水位平衡、断线自愈、指令质量。
- **输入口**：各席四件套 `docs/_working/automation_campaign/<岗>/checkpoint.md`；queue_depths.md；机器层日志（.runtime/logs/night_mining.log、f06_grid.log）。
- **输出口**：queue_depths.md 更新；**指令面修订**（各席 instruction/checkpoint，仅限四件套）；断线处置记录。
- **工作流程**：1 巡水位（上堆积/下饥饿→查因→调配额报⓪）2 巡断线（游标停跳/日志停更→修复重启或修指令）3 巡交接格式（下游收不上→修上游 instruction）4 断供登记无证据→打回① 5 权限红线：**只可改指令面，禁碰判据门柱与冻结值** 6 每班≥2 轮 7 自检两轮。
- **保底绩效**：每班 2 轮全环巡检；断线当班内响应。

### ⑫ 记账员
- **目标**：日清日结可审计。
- **输入口**：全部台账+分数册。
- **输出口**：晨报（`docs/_working/cmd_ledger/`，08:45 前）+05_owner_decisions.yaml 汇总核对+成绩分布周记。
- **工作流程**：汇总各席台账→晨报（真哈希/成绩增量/水位/呈批件清单）→挖干判定跟进（mined_out 复挖核验状态）→自检两轮。
- **保底绩效**：日清；晨报不隔夜。

## 4. 两条回流线详则

- **数据回流**：缺数申请唯一入口=①席；①席全网找（每项≥3 渠道留痕）→建设/修复→解锁；穷尽才断供登记（证据链强制，⑪抽查打回权）。采购类永远呈批，禁自购。
- **成绩回流**：⑧→⑨→三联单；复考纪律=新鲜窗月度+三取二裁定（exam_policy）；mined_out 自报必须邻车道 20% 抽样复挖核验方可封矿（mining_sop v1.8.0）。

## 5. 矿脉轮转制

lane_roster 7 车道+RX_A/RX_B 复挖道；某车道挖满（mined_out 申报+复挖核验通过）→⓪派单员把②③席产能切到下一车道；九口并行度按 §2；单车道单节点六向挖尽=节点级挖满，卡 empty→preregistered 转化率是轮转前置读数。

## 6. 附录A：对标顶尖机构盲点自查（2026-10-14 首轮）

| 环节 | 顶尖实践 | 本线现状 | 缺口判定 |
|---|---|---|---|
| Idea→生产状态机 | WorldQuant BRAIN：idea→simulation→OS→submission 全状态机 | 卡 status 机 empty→preregistered→examined | ✅等价 |
| 多样性去重 | WQ self/prod-correlation 闸 | C5 聚类+秩相关合并闸 | ✅等价；**环节层家族共线性聚类待建**（⑨席职责） |
| Champion/Challenger | 在产策略挑战者对照 | 模拟盘 promote_paper | ⚠️缺口：晋级后在产监控台账未成文（⑩席扩展项） |
| 连续训练 CT | MLOps CI/CT/CD | 本传送带即 CT | ✅ |
| 数据血缘/版本 | feature store+版本化 | PIT 快照+源线谱+断供证据链 | ✅ |
| 漂移监控 | production drift | 新鲜窗月度复考 | ✅ |
| 实验可复现 | run registry | backtest sop_d 档案命名 | ✅ |
| 算力预算 | 利用率治理 | GPU 采样器（峰值 44%） | ✅算力富余，缺的是执行器吞吐 |
| 质量红线 | fail 不上线 | test_no_upgrade_without_oos 实测生效 | ✅ |
| A/B 对照纪律 | champion/challenger A/B | 对照卡族 182 张**无执行器**（OD-1） | ⛔最大缺口：不立项则优化闭环空转 |
| 流水线 SLA | pipeline 健康看板 | queue_depths 水位表（⑪席） | 🆕本册新增 |
| 岗位 SLA/绩效 | 运营 KPI | 保底绩效+双轮自检 | 🆕本册新增 |

## 7. 附录B：待 Owner 呈批（拍一个解锁一片）

| 项 | 解锁 |
|---|---|
| OD-1 对照/消融执行器立项 | 98 张卡可考+优化闭环 A/B 转起来 |
| OD-④⑨ 数据断供派单/当班补 | 52 张 blocked 主要部分 |
| 情绪三判据命题与阈值 | 情绪腿接入 P3-R2 四腿端到端 |
| OD-⑤ F06 批预算/撞窗 | 周六网格产能 |
| OD-⑧ W5 confidence 补跑 | 晋级闸开测 |
| OD-②③⑥⑦⑩ 其余 | 见 05_owner_decisions.yaml |
| 采购三件（分析师预期/分钟流/L2） | 资金线与对应 blocked 卡 |
