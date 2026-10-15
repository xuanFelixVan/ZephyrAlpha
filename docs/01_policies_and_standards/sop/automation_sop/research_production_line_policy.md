---
doc_type: policy
ttl: permanent
title: 全自动研究生产线运营 SOP（九口出料·挖考判晋反馈闭环）
status: active
version: 1.6.1
date: '2026-10-15'
owner: ZephyrAlpha-Owner
---

# 全自动研究生产线运营 SOP

> **一句话定位**：从找数据到出成绩的整条业务线自动化流水线的岗位运营标准——岗位各自的目标/输入口/输出口/工作流程/保底绩效/自检制。
> **机构对标命名**：Research Pipeline / Alpha Production Line（WorldQuant Alpha 平台流水线）/ Research-to-Production（MLOps 连续训练 CT）。本仓叫**全自动研究生产线**。
> **分工矩阵**（防双真源）：挖矿方法论=`mining_sop/`（六向/封矿核验）｜考试回测方法论=`backtest_system_sop/`（四卷+exam_policy）｜数据生命周期=`data_ops_sop/`｜班底编制与切碎机制=`automation_sop/automation_crew_policy.md`｜**本册只写"生产线岗位怎么运转"：输入输出口、流程、绩效、自检**。
> **净零声明**：本册收拢讨论册（docs/_working/cmd_ledger/automation_plan_discussion.md）与四域施工战报中的口头流程成文；不新增 gate/规则/注册表；handoff 新路径仅限 docs/_working/automation_campaign/ 下。
> **总原则**：只有考试口径的成绩算数（引擎直跑数字仅参考）；先冻结判据后跑数（裁定#518）；fail 不得升级 verified；负结果如实入册也是成绩。
> **v1.1.0 变更**：岗位从 13 收敛为 **10 席最小编制**（推导判据=技能类型/写域/职责分离/吞吐量四条，见 §3 头注）；新增 §4 自我迭代回路节；改良检索并入④席、对照配对并入⑥席、判卷+归因+晋级合并为⑨成绩官、派单+监督+迭代审计+记账合并为⑩线长席。横向扩席规则见 §3 尾。

## 1. 主干传送带总图

正向主流：**①数据源（找源评估）→ ②数据建设（建表回补）→ ③④挖矿（库内六向/全网战法）→ ⑤实现 → ⑥制卡冻结 → ⑦⑧考工 → ⑨成绩官（判卷→归因→晋级）**
数据回流线：任何环缺数 → ①（全网找≥3 渠道留痕）→ 就位给②建设 → 卡解锁；穷尽免费渠道才准断供登记（**必须附证据链，线长席抽查打回**）
成绩回流线：⑨归因 → 三联反馈单（挖矿方向单→③④／算法修改单→⑤／判据呈批→Owner）→ 复考再考（**优化后再考必须走⑥制作的对照卡 A/B**）
监督线：⑩线长席巡全线水位/断线/指令质量/迭代纪律（可改指令面，禁碰判据门柱）
出料九口：见 §2——一条传送带，九个出料口，按卡族路由。
终环：**⑪整装回测席**——每夜一次整装回测（真实成本+护栏口径），晨报直答「能不能赚钱/下浮率多少」；发现问题→⑨归因→修改单→⑤施工→⑥对照卡→⑦⑧环节考→verified→进装配→次夜整装复测。这是自我迭代的最高层闭环。

既有机器层三件（对话席不重复其工作，只消费其产出）：`scripts/tasks/run/run_night_mining.ps1`（Task Scheduler 23:00 Sun-Thu）｜`scripts/tasks/run/run_c4_exam.ps1`（夜间考试批）｜`scripts/tasks/run/run_f06_grid.ps1`（周六参数网格窗）。

## 2. 九类成绩出料口映射（哪些已入线、并行度）

| # | 成绩类别 | 出料通道（考试口） | 上游喂料 | 入线状态 |
|---|---|---|---|---|
| 1 | 组合参数网格 | F06 周六窗（机器） | 参数空间 prereg（config/search_space_prereg.yaml f06_grid_v2） | ✅在跑 |
| 2 | 注册册策略 | strategy 考试口 | 策略挖矿+④战法全网矿工 | ✅可并行 |
| 3 | 指标考试批 | indicator 考试口 | TASC 指标挖矿 | ✅可并行 |
| 4 | 因子重考 | factor 考试口 | 因子挖矿（八段） | ✅可并行 |
| 5 | 分配器影子考 | allocator 考试口 | 分配器实现 | ✅可并行 |
| 6 | 防守机制对照（ATR 型） | **对照卡** | 环节假设+⑥席配对 | 🔧OD-1 已批，执行器施工中 |
| 7 | 引擎直跑数字 | （参考值，不入成绩正册） | — | 不入线 |
| 8 | 负结果 | 各口 fail 如实入册 | 全部 | ✅纪律面 |
| 9 | 环节考试卡 | 校准/消融/影子/对照四族 | 六向挖矿（186 节点 7 车道） | ✅主战场 |

> 路径注（2026-10-14）：第 3/4/5/6/8 类成绩册已随 _working 清理归档至 `docs/_archive/_working_20261014/fexam/`；第 3/4/5/6/8 类成绩册已二次迁 `docs/04_research_records/backtest/scores/2026/`（30 本在册，归档区无研究资产残留）；第 9 类卡册仍住 `docs/03_modules/_domain_backtest/exam_cards/`（不变），分数册同 04；原 **分数册已物理迁 `docs/04_research_records/backtest/scores/<YYYY>/`（裁定#536，原 03 行作废）**。九类归属：1/2/3/4/5/6/8/9 八类由本线喂料，第 7 类（引擎直跑）不入线仅参考。

并行度：2/3/4/5/9 五口同时开（考试通道互不抢）；1 口周六独占；6 口随 OD-1 执行器交付转正。挖满一个矿脉→轮转下一个（§5）。

## 3. 岗位卡（10 席最小编制）

> **岗位数推导判据**（Owner 2026-10-14 定调：按实际流程给最少岗位）：一条流水线工序只有在（a）技能类型不同（b）写域不同（c）职责必须分离——冻结与运行分离/判卷独立于考工/审计独立于生产（d）吞吐量不足需横向扩席——四种情况下才设独立岗位。据此收敛为 10 席；横向扩席只允许扩⑦⑧考工与③④挖矿（吞吐型），判断席（⑥⑨⑩）永不拆分。
> **v1.1.1 变更（E2E 实测修正，2026-10-14）**：数据绑定口径修正（528/531 卡用 lineage 字段）；empty 骨架卡现实（转正须具名子题卡，呈批件计入⑥席保底）；同族门柱多口径并存→呈批不擅挑；考工 panel 卡走 run_card API（CLI --target-csv 砍单列缺陷，修复前 panel 禁走 CLI）；裁定#518 定位=「先冻结后跑」方法先例非数值源；新增并发环境警戒（归档/清理必须先查 .ailocks）。
> **v1.2.0 变更（2026-10-14 晚）**：新增⑪整装回测席（每夜一次，晨报直答「能不能赚钱/下浮率」）与整装→归因→施工→对照复测最高层闭环（§4）；考工 GPU 优先+安静窗纪律（§3⑦⑧）；班车时刻表（§3-B）与楼栋制进度图（§3-C）；§2 成绩册归档路径对齐（分数册新地址待 Owner 下发后全局替换）。
> **v1.2.1 变更（2026-10-15）**：新增 §3-D 研究态排班表（现行，24 小时不停）与 §3-E 实盘态排班表（达标后切换）+切换闸门协议；机器层计划任务真相核实落册（2026-10-15 实测：NightMining/F06Grid 已 /enable 启用、TTLRejudgeDaily/C4Exam 就绪、reaper=运行时钩子非计划任务）。
> **v1.6.0 变更（2026-10-15）**：§2 路径注二次核验（30 本成绩册入 04/backtest/scores/2026，归档区无残留）；GPU 接线升⑤席 P0 首件（考试执行器未接 GPU=一直没转根因）；§8 命名词表真源指针 domain_naming_rules.yaml。
> **v1.3.0 变更（2026-10-15，TDM 挖矿并入令并入）**：车道台账/名册等战役资产已归档至 `docs/_archive/_working_20261014/nightmine_campaign/`（③席输入口路径同步）；产卡唯一出口=`scripts/backtest/generate_exam_card_skeleton.py` only-add 通道；念想引擎双轨=本地引擎走 GPU 机会档（登记+让路，§3-F）或 LSG qwen provider（GPU 纪律同理）；枯竭判据对齐 mining_sop **v1.9.1**（六向全查无新卡+无未挖长尾+挖后自审闸 §6，双噪音封矿）；现状锚定：186 节点全有卡 531 张、mined_out=0、六向在半山腰；边界=docs/04_research_records/ 基建中，挖矿产物任务期暂留 _working 面、落成后统一迁移，**禁两线同写一区**；挖矿不停，唯一叫停权=Owner。

通用规则（适用于全部岗位）：开工冷启动三步（PATH 修 Python312→lock_files cleanup→process_reaper --status）；改前 claim 毕后 release；**班中 claim 过期（TTL 30 分、失败重试后 5 分）→重新 acquire 即可（文件未变则无冲突），CAS 拒写非事故勿进堵点**；提交唯一正门 git_commit.py --enqueue；**完工自检两轮，连续两轮零问题该批产出才算交付**（第二轮才发现问题=第一轮漏检记缺陷行）；四件套=`docs/_working/automation_campaign/<岗>/`{instruction.md 恒定指令, scope.md 输入清单, checkpoint.md 游标, ledger.md 台账}；sid=`st-qoder-<岗>-<MMDD>-<NN>`。

### ① 数据源席
- **目标**：数据就位率最大化；断供=穷尽免费渠道后的最后登记，不是逃避登记。
- **工作内容**：全网搜源→评估→（转②建设）→坏数据修复转办→断供登记。缺数从最源头负责。
- **输入口**：`src/zephyr/data/config/known_data_gaps.yaml`（断供/缺数登记册）；`docs/_working/automation_campaign/feedback/to_datasource.md`（缺数申请）；源线谱 `docs/04_research_records/data/chain_piling_campaign/02_source_line_registry.md`（2026-10-15 迁 04）。
- **输出口**：源线谱新增行（新源线 memo）；known_data_gaps.yaml 条目更新（附 `searched_channels` 证据字段）；就位 memo→②席建设单；采购呈批件。
- **工作流程**：1 读断供表与缺数申请 2 逐项全网搜索（官方免费 API/开放数据/GitHub 数据集/数据商目录，**每项≥3 渠道**，WebSearch 留链接）3 评估五门（成本/合规/PIT/许可证/**续供**——后续能否持续获取：采集通道+更新频率+自动化程度+断供风险四问，只进历史不续供的源标注「一次性历史档案」禁作常设信号源准入，历史回补另案；花钱采购→出呈批件禁自购）4 可免费建设→写建设单转②席 5 坏数据→转②席走 data_ops_policy 修复 6 免费渠道穷尽→断供登记（附渠道清单+失败原因）7 台账留痕 8 自检两轮。
- **保底绩效**：每班处理≥3 个缺数项；每项≥3 渠道搜索留痕；断供登记 100% 带证据链。
- **自检要点**：每个"断供"结论都能回答"找过哪三处、为什么不行"。
- **真源挂点**：data_source_onboarding_sop＋mining_sop（全网调研法）。
- **总包**：按缺数项并行搜索（读席并发不限，写登记串行 CAS）。

### ② 数据建设席
- **目标**：把①席找到的源变成可考数据；存量回补清零。
- **工作内容**：建表/接入/调度/回补/坏数据修复，全走数据族 SOP；不找源（那是①的事）。
- **输入口**：①席建设单；`src/zephyr/data/config/known_data_gaps.yaml`（pending 回补项）；`data_ops_sop/data_source_onboarding_sop.md`＋`data_ops_policy.md`。
- **输出口**：建表/接入/回补完成+接通验收三查记录；known_data_gaps 条目翻转 completed；解锁卡清单→`docs/_working/automation_campaign/feedback/unblocked.md`。
- **工作流程**：1 领建设单 2 走 onboarding（报批→建表→接入→调度→验收三查）3 回补类走 data_ops_policy（幂等回补+FINAL 逐位验证）4 翻登记册状态 5 写解锁清单（哪些卡的 data_binding 由此满足）6 台账 7 自检两轮。
- **保底绩效**：每班≥1 项建设或回补落地；验收三查 100% 留痕。
- **总包**：按项目并行（写域=各自表/册）。

### ③ 库内挖矿席
- **目标**：六向候选持续产出且绝不重复挖。
- **工作内容**：按车道对 186 节点六向挖（①上游②下游③算法④后端⑤呈现⑥数据），听⑨方向单调整重心。
- **输入口**：`docs/_working/automation_campaign/dispatch/daily_dispatch.md`；`docs/04_research_records/mining/ledgers/nightmine_20261010/01_mining_brief.md`（六向法）；同目录 `00_lane_roster.yaml`＋`L0d..L7_ledger.md`（已挖/mined_out，八本台账；2026-10-15 起资产住 04 区）；`docs/_working/automation_campaign/feedback/to_miners.md`。边界：04_research_records/ 基建中，产物暂留 _working 任务面，禁两线同写一区。
- **输出口**：候选→`data/strategy_intake/lane_<x>_candidates.csv`；具名子题卡（含假设描述，**按 TDM 图节点定义生成——真源=config/trading_decision_map.yaml，有据可依非自拟**；裸骨架不可考不产）→一律经 `scripts/backtest/generate_exam_card_skeleton.py` only-add 通道进 `docs/03_modules/_domain_backtest/exam_cards/`；念想引擎双轨=本地引擎走 GPU 机会档（登记+让路，§3-F）或 LSG qwen provider；台账行追加。
- **工作流程**：1 领车道 2 读台账排除已挖/mined_out 3 读方向单调重心 4 逐节点六向挖 5 候选入台账 6 empty 卡骨架（门柱 null，status=empty）7 台账追加 8 自检两轮（抽 3 条反向核对未挖过）；枯竭判定书（mined_out 申报+六向查证+交叉复挖结论，逐节点一册）→`docs/04_research_records/mining/exhaustion/<YYYY>/`（裁定#536）。
- **保底绩效**：每班≥5 新候选或≥10 张 empty 卡骨架；mined_out 名单核对率 100%。
- **真源挂点**：mining_sop_policy（六向/防噪音四闸/封矿核验）。
- **总包**：按节点并行（读并发不限；写串行 CAS）。

### ④ 全网战法矿工席
- **目标**：外部战法与 SOTA 算法持续进线（喂 2/9 口+给⑤供改良弹药）。
- **工作内容**：常规渠道轮转扫战法；**收到⑨方向单时定向检索 SOTA**（论文/GitHub/开源实现）出改良情报卡。
- **输入口**：`backtest_system_sop/sop_c_strategy_library_intake.md` §9（渠道+合规）；`docs/01_policies_and_standards/_registry/catalogs/strategy_registry.yaml`（去重）；`docs/_working/automation_campaign/feedback/to_miners.md`（定向检索单）。
- **输出口**：战法卡（原文链接/许可证/逻辑描述/伪代码/数据源映射五必备）→`data/strategy_intake/`；改良情报卡→`docs/_working/automation_campaign/feedback/to_impl.md` 附依据。
- **工作流程**：1 渠道轮转扫（或按定向单）2 许可证闸 3 存量去重闸 4 战法卡/改良情报卡 5 登记 6 自检两轮。
- **保底绩效**：每班扫≥5 渠道/仓库；产≥2 张战法卡；定向单 100% 响应。
- **真源挂点**：sop_c（外部代码禁直接复制，只学思想走 C3 重实现）。
- **总包**：按渠道并行。

### ⑤ 实现席
- **目标**：未实现卡清零+按修改单优化算法。
- **输入口**：exam_cards 中 blocked(未实现)卡；`docs/_working/automation_campaign/feedback/to_impl.md`（修改单+④改良情报）；战法卡伪代码。
- **输出口**：码面+测试绿（tmp_path 隔离）→卡翻转 unblocked→移交⑥；修改单落地记录。
- **工作流程**：1 领单 2 读需求/修改单 3 模板化实现（真源=construction_sop 15 步）4 测试绿 5 翻卡状态 6 台账 7 自检两轮。
- **保底绩效**：每班≥1 张卡实现或≥1 张修改单落地；测试必须绿。
- **总包**：卡间并行（写域=各自模块）。

### ⑥ 制卡席
- **目标**：empty→preregistered；先冻结后跑；每次优化都有 A/B。
- **工作内容**：填门柱判据（只抄在册冻结值）；**对照配对卡制作**（champion/challenger 单变量）。
- **输入口**：exam_cards 中 empty 卡（现存 empty 多为 /01 裸骨架卡——转正须③④席先产具名子题卡）；在册冻结值真源=同族已冻结卡本体+各域判据册（裁定#518=「先冻结后跑」方法先例，非数值源）；⑨席对照申请单。同族门柱多口径并存（如实测 S2 族标准/事件研究两套五键并存）→不擅自挑，一律呈批。**裸骨架卡（/01 无具名子题）一律退回③席按 TDM 图节点定义补具名子题（真源在图上，有据可依不属自拟），禁呈批 Owner；仅当节点定义本身无考题语义才上升呈批。**
- **输出口**：preregistered 卡（pillars_numeric/window/buckets 齐，数据绑定按卡面 lineage 字段承载——531 卡中 528 张用 lineage，`data_binding` 仅 3 张，口径以 lineage 为准）；对照卡对（原版=champion，改良=challenger，**只改一个变量**）；语义参数缺→`docs/_working/nightmine_campaign/05_owner_decisions.yaml` 呈批（**一个数不编**）。
- **工作流程**：1 领 empty 卡/对照申请 2 查在册冻结值（逐字沿用）3 有→填门柱 4 缺→呈批件 5 对照申请→配对制卡（clone 原卡改单变量）6 翻 status 7 自检两轮（两轮都核对：门柱非空且与冻结值逐字一致；对照卡 diff 恰一个变量）。
- **保底绩效**：每班≥5 张或当班领用卡 100% 处置完（含呈批件；骨架卡时代呈批件计入保底）。
- **真源挂点**：backtest_system_sop/exam_policy。
- **总包**：按卡并行。

### ⑦⑧ 考工 A/B（吞吐核心，可横向扩 C/D…）
- **目标**：成绩产量——每日出分。
- **输入口**：exam_cards 中 preregistered 队列（两席按卡族分工互不抢卡）。
- **输出口**：`docs/04_research_records/backtest/scores/<YYYY>/exam_scores_v1.yaml` 追加行（**only-add**；已物理迁此，裁定#536）；卡 status→examined。
- **工作流程**：1 领卡 2 核对门柱已冻结 3 选通道：series 卡走 CLI（calibration_exam.py --card/--signal-csv/--target-csv，实测约 2 分/卡）；panel 卡走 run_card API（CLI --target-csv 有砍单列缺陷，修复前 panel 禁走 CLI）；数据按卡绑定口径自物化（执行器不自助取数）；单卡>15min 即 kill 记 finding；**GPU 优先**：ic 类走 scripts/backtest/fexam/gpu_ic/gpu_rank_ic.py（3090+torch cu126 实测可用），启用前必过 parity_test 对拍、且须安静窗（VRAM 独占纪律：smoke_gpu 预检不过=改日，白天桌面进程占 GPU 硬闯禁止）；白天零星卡 CPU 兜底，不与主线抢 CPU。4 跑（CH 窗 01:00-04:00 避让）5 分数入库 6 翻状态 7 失败写堵点册即停 8 自检两轮（only-add 与门柱一致）。
- **保底绩效**：每席每班≥8 张出分，或跑满 4 小时（双口径先到者计）。
- **真源挂点**：exam_policy＋run_fexam.py（MOD-BT-FEXAM）。
- **总包**：并发≤2（CPU 核限制）。

### ⑨ 成绩官
- **目标**：成绩真实可信，且每条 fail 都变成改进动作。
- **工作内容**：判卷复核（独立于考工）→归因四分诊→三联反馈单→晋级处置→迭代史记账。
- **输入口**：当日 exam_scores_v1.yaml 增量行+家族共线性历史+晋级纪律（exam_policy）。
- **输出口**：成绩日报（cmd_ledger 晨报附）；三联单 `feedback/{to_miners,to_impl,to_datasource}.md`；对照申请单→⑥；复考排程；pass 行→verified 升级+TDM 挂接（fail 永不升级）；迭代史行 `docs/_working/automation_campaign/iteration_history.md`。
- **工作流程**：1 逐行判卷（门柱一票否决机械核对）2 负结果如实入册核对 3 IS/OOS 符号观察 4 归因四分诊：信号真无效→方向单（家族收敛或 mined_out 建议）／实现数据问题→修改单或缺数单／判据问题→呈批／需对照验证→对照申请单给⑥ 5 pass→核红线→升级+挂图 6 迭代史记账 7 自检两轮。
- **保底绩效**：当日增量 100% 判卷；fail 行 100% 分诊；每班≥1 条结构性观察（家族级）。
- **总包**：按家族并行分析（读）。

### ⑩ 线长席
- **目标**：全线不断料不堆积不断线不自我欺骗。
- **工作内容**：派单（查重+配额）+监督（水位/断线/指令质量）+**迭代纪律审计**（防过拟合）+晨报记账。
- **输入口**：各席四件套 checkpoint；全线台账；exam_cards 状态统计；`docs/_working/automation_campaign/iteration_history.md`。
- **输出口**：`docs/_working/automation_campaign/dispatch/daily_dispatch.md`；`docs/_working/automation_campaign/pulse/queue_depths.md`；指令面修订（仅四件套 instruction/checkpoint）；迭代预算处置单；晨报（cmd_ledger，08:45 前）。
- **工作流程**：1 读全线水位与卡池统计 2 查重（逐条对照已挖名单/mined_out/现有卡）3 定各席当日配额（瓶颈环加派）4 写任务单 5 巡断线（游标停跳/日志停更→修复或修指令）6 巡交接格式（下游收不上→修上游 instruction）7 **迭代纪律审计**：每对象迭代轮次记账；同 holdout 被迭代消费超限→处置（强制 fresh holdout 呈批或封存）；判据改动嫌疑=挪门柱→呈批 8 断供登记无证据→打回① 9 晨报 10 自检两轮。
- **保底绩效**：每日一单；每班≥2 轮全环巡检；迭代审计每周全量 1 轮；晨报不隔夜。
- **权限红线**：只可改指令面（四件套），禁碰判据门柱与冻结值与分数册。

### ⑪ 整装回测席
- **目标**：每夜一次整装回测，晨报直答两问——「现在这套能不能赚钱？下浮率多少？」
- **工作内容**：装配状态盘点→触发/核对整装回测（backtest sop_a 全图编排，真实成本+护栏口径）→出分判读→问题清单分流。
- **输入口**：装配状态册（config/strategy_production_map.yaml）＋verified 晋级件（exam_scores/registry）＋`backtest_system_sop/` 四卷。
- **输出口**：整装成绩台账 `docs/_working/automation_campaign/p11_assembler/ledger.md`；问题清单（环节/数据/结构三类）→⑨归因→三联单；晨报整装结论段。
- **工作流程**：1 冷启动 2 读装配状态（在产模块/challenger 待入）3 触发或核对整装回测 runner 4 出分判读（通过判据/下浮率/对比昨夜）5 成绩台账 6 问题清单分类转⑨ 7 晨报附结论 8 自检两轮。
- **保底绩效**：每晚 1 次；晨报必含「能不能赚钱+下浮率」直答；问题清单 100% 分流。
- **频率**：每夜 21:30（收盘数据落库后、23:00 夜挖前）；机器层跑数、本席判读记账。
- **铁律**：新施工模块必须先经环节考试 verified 才准进装配——施工完成的模块经⑨晋级后自动入次夜整装清单，闭环到此闭合。

## 3-A 横向扩席规则

只扩吞吐席：考工（⑦⑧→C/D/E…按 preregistered 积压>50 张时每 50 张加一席）、挖矿（③④按下游断料频率）；判断席（⑥制卡/⑨成绩官/⑩线长）永不拆分——拆分即破坏冻结/运行分离与判卷独立性。

## 4. 两条回流线 + 自我迭代回路

- **数据回流**：缺数唯一入口=①席（全网找≥3 渠道留痕）→②建设→解锁；穷尽才断供登记（证据链强制，⑩抽查打回）。采购类永远呈批。
- **成绩回流**：⑨判卷→归因→三联单；复考纪律=新鲜窗月度+三取二裁定（exam_policy）；mined_out 自报须邻车道 20% 抽样复挖核验方可封矿（mining_sop **v1.9.1**：枯竭=六向全查无新卡＋无未挖长尾＋挖后自审闸 §6，双噪音封矿）。现状锚定 2026-10-15：186 节点全覆盖有卡（531 张），mined_out=0，六向挖掘在半山腰；挖矿继续不停，唯一叫停权=Owner。
- **自我迭代回路（主循环）**：⑦⑧出成绩 → ⑨判卷归因（fail 四分诊）→ 改良三路：信号真无效→③④换方向挖（家族收敛/mined_out）｜可优化→④定向检索 SOTA 出改良情报→⑤落地→**⑥配对对照卡（只改一个变量）**→⑦⑧对照复考→⑨判卷→提升才晋级、持平/退化即封存改良并记账｜缺数据→①②供数→复考。全程⑩迭代纪律审计护航：迭代预算（同对象超限强制 fresh holdout 呈批或封存）、OOS 复用审计、门柱不可动（判据改动=挪门柱，只能呈批）。
- **迭代纪律判据**（防"迭代式过拟合"）：同一对象对同一 holdout 的有效迭代消费≤3 轮/月；第 4 轮起必须换未消费样本段（呈批）或封存；迭代史不记账的复考成绩判无效。

## 5. 矿脉轮转制

lane_roster 7 车道+RX_A/RX_B 复挖道；某车道挖满（mined_out 申报+复挖核验通过）→⑩线长把③席产能切到下一车道；单节点六向挖尽=节点级挖满；empty→preregistered 转化率是轮转前置读数。

## 6. 附录A：对标顶尖机构盲点自查（2026-10-14，v1.1 更新）

| 环节 | 顶尖实践 | 本线现状 | 缺口判定 |
|---|---|---|---|
| Idea→生产状态机 | WorldQuant BRAIN 全状态机 | 卡 status 机 empty→preregistered→examined | ✅等价 |
| 多样性去重 | WQ self/prod-correlation 闸 | C5 聚类+秩相关合并闸 | ✅；环节层家族共线性聚类=⑨席结构性观察职责 |
| Champion/Challenger | 挑战者对照 | ⑥席配对对照卡+模拟盘 promote | ✅（执行器随 OD-1 交付转正） |
| 连续训练 CT | MLOps CI/CT/CD | 本传送带即 CT | ✅ |
| 数据血缘/版本 | feature store+版本化 | PIT 快照+源线谱+断供证据链 | ✅ |
| 漂移监控 | production drift | 新鲜窗月度复考 | ✅ |
| 实验可复现 | run registry | backtest sop_d | ✅ |
| 算力预算 | 利用率治理 | GPU 采样器（峰值 44%，富余） | ✅瓶颈在执行器吞吐与断供 |
| 质量红线 | fail 不上线 | test_no_upgrade_without_oos | ✅ |
| A/B 对照纪律 | champion/challenger A/B | ⑥席配对+执行器（OD-1 已批施工） | ✅落地中 |
| **迭代预算/防迭代式过拟合** | holdout 纪律/Deflated Sharpe | 🆕v1.1 新增：⑩席迭代纪律审计+§4 判据 | ✅新增 |
| 流水线 SLA | pipeline 健康看板 | queue_depths 水位表 | ✅新增 |
| 岗位 SLA/绩效 | 运营 KPI | 保底绩效+双轮自检 | ✅新增 |

## 7. 附录B：Owner 呈批面（2026-10-14 状态）

| 项 | 状态 | 解锁 |
|---|---|---|
| OD-1 对照/消融执行器立项 | ✅已批，施工排期中 | 98 张卡可考+优化闭环 A/B 心脏 |
| 数据断供派单 | ✅已批（免费渠道优先） | 52 张 blocked 主要部分 |
| 情绪三判据 | ✅原则同意；⑥席出命题与阈值提案后终签 | 情绪腿接入 P3-R2 |
| 采购三件（分析师预期/分钟流/L2） | 待批 | 资金线与对应 blocked 卡 |
| OD-②③⑤⑥⑦⑩ | 见 05_owner_decisions.yaml | 各对应项 |
| 并发环境警戒（E2E 实测） | 转办治理线+⑩线长席：实测他会话无 claim 整树归档 automation_campaign/、staged 删 13 张冻结卡——任何归档/清理必须先查 .ailocks；⑩席首班职责=按本册 v1.1.1 重建/同步全部四件套 |


## 3-B 班车时刻表（Qoder 自动化发车节奏）

设计法则：**班车间隔≈班次时长×1.3~1.5**（上一班快结束下一班才到，误差几分钟）；各岗错峰偏移防撞车；每张卡带防重入条款（检测到同岗上游班次仍持有游标/claim→本班立即短报退出）；平均并发≈Σ(时长/间隔)≈6.4，峰值≤9，留余量给 Owner 与机器层。

| 岗 | 班时长(估) | 班车间隔 | 每日首班偏移 |
|---|---|---|---|
| ⑩线长 | ~15 分 | 30 分 | :00 |
| ⑥制卡 | ~20 分 | 40 分 | :05 |
| ⑨成绩官 | ~20 分 | 40 分 | :10 |
| ①数据源 | ~20 分 | 40 分 | :15 |
| ③库内挖矿 | ~30 分 | 45 分 | :20 |
| ④战法矿工 | ~30 分 | 45 分 | :30 |
| ⑦考工A | ~45 分 | 60 分 | :35 |
| ⑧考工B | ~45 分 | 60 分 | :45 |
| ②数据建设 | ~40 分 | 60 分 | :50 |
| ⑤实现 | ~60 分 | 75 分 | :55 |
| ⑪整装回测 | 机器跑+~30 分判读 | 每日 1 班 | 21:30 固定 |

校准机制：每班在台账记实际耗时分钟数，⑩线长每日按实测调表（连续 3 天偏差>30% 即改间隔）。

## 3-C 楼栋制进度图（防重复/可扫读）

三层结构：**楼**=车道/家族/域（coverage_map 一行一楼，恒定≤几百行）→**户**=节点/卡（分户台账）→**证据**=台账行（追加式）。
- `docs/_working/automation_campaign/pulse/coverage_map.md` 由**生成器**从各台账重算产出（⑤席首批施工单；静态清单禁手工维护铁律适用）：每楼一行`[楼号|状态:封楼/在挖/未开|已做/剩余计数|游标指针]`；封楼=mined_out 申报+邻道 20% 复挖核验通过。
- 岗位读取纪律：**先读楼图→只进未封楼→楼内查户级台账→绝不全量扫描**——几万条明细 AI 永不直读，靠楼图收敛视野；写入进分户台账，楼图只由生成器重算。
## 3-D 研究态排班表（现行，24 小时不停）

研究态=当前生效态：生产线 24 小时不停，昼夜同节奏，研究班车与机器层并行。要点：

- **①班车层（Qoder 10 席，昼夜同节奏）**：按 §3-B 时刻表 24h 发车——班车间隔=班时长×1.3~1.5（上一班快结束下一班才到），各岗错峰偏移防撞车；每张卡带**防重入条款**（检测到同岗上游班次仍持有游标/claim→本班立即短报退出，不排队等待）。
- **②机器层计划任务（2026-10-15 实测核实）**：

| 任务 | 时刻 | 状态（2026-10-15 实测） |
|---|---|---|
| ZephyrAlpha_NightMining | 每晚 23:00，Sun-Thu | ✅已启用（曾被禁用，已 /enable 恢复） |
| ZephyrAlpha_F06Grid | 周六 08:00 | ✅已启用（曾被禁用，已 /enable 恢复） |
| ZephyrAlpha_TTLRejudgeDaily | 每日 18:05 | 就绪 |
| ZephyrAlpha_C4Exam | 夜间考试批 | 就绪（下次 10-17 14:00，时刻待核） |
| process_reaper | — | 运行时钩子常开（非计划任务，不占 schtasks 位） |

- **③CH 维护窗禁入**：01:00-04:00 ClickHouse 维护窗，重活禁入（考工/回补/整装等重计算一律避让，§3⑦⑧同款纪律）。
- **④GPU 两档制**：小考试（单卡 ic 类）白天空闲显存≥8GB 即放行；大网格/F06 大件只在**夜间安静窗独占** VRAM 跑（白天桌面进程占卡硬闯禁止，smoke 预检不过=改日）。
- **⑤整装回测（⑪席）每夜 21:30**：收盘数据落库后、23:00 夜挖前，机器跑数+⑪席判读记账，晨报直答「能不能赚钱/下浮率」。

## 3-E 实盘态排班表（达标后切换）

实盘态=切换闸门通过且 Owner 下令后的生效态：白天让路交易，研究整体挪夜间，**研究不停止**。

| 时段 | 用途 | 纪律 |
|---|---|---|
| 08:00-09:15 | 盘前数据校验+风控快照 | 交易日必做；数据异常即报 Owner |
| 09:15-15:00 | **交易保护区**（交易日） | GPU/CPU 优先实时信号计算；生产线白天班**降速=只读研究+写单，禁跑算力**（挖矿/考工/网格白天面全停） |
| 15:30-19:30 | 盘后落库+复权校验+⑨成绩官主班绩效归因 | 盘后数据落地后才准恢复写算 |
| 21:30 | 整装回测（⑪席保留） | 与研究态同款 |
| 23:00-06:00 | 深夜研究窗全速 | 挖矿/F06/GPU 大件**整体挪夜间**；重载班车（③④⑤⑦⑧）挂夜间跑 |
| 01:00-04:00 | CH 维护窗 | 照避，重活禁入 |

**切换协议（研究态→实盘态）**：
- 切换闸门=**整装口径 Sharpe≥2 及格（可切模拟盘态）/≥4 优秀（可小资金实盘）**；
- 须**连续 10 个交易日滚动达标**（防单夜运气）；⑩线长席晨报持续报「距闸门差多少」；
- 触发=Owner 一句「切实盘排班」→ 未来 AI 读本节执行换挡：白天班车降速（只读研究+写单不跑算力）、交易保护区生效、runner 挂夜间。


## 3-F GPU 三档制与任务登记册（2026-10-15，Owner 定调：CPU 满载 GPU 闲置，机会档吃空闲）

| 档 | 谁在用 | 规矩 |
|---|---|---|
| 独占窗 | F06 网格/整装大跑/其他大件 | 跑前 `gpu_watchman.py acquire <task> --exclusive`，跑完 release；独占期间机会档必须让路 |
| 机会档 | 点子生成/小规模 rank-IC 等小件 | 空闲判据=空闲显存≥8GB 且 利用率<10% 且 登记册无独占任务；忙即让路 checkpoint（生成任务单条粒度，代价≈0） |
| 禁入 | 无登记裸占 | 任何 GPU 使用先登记后使用；违规=⑩线长席处置 |

基建：`scripts/gpu/gpu_watchman.py`（detect/acquire/release/status，登记册=`.runtime/gpu_registry/registry.jsonl`）。历史包袱修正：Ollama 非禁物，禁的是**无让路能力**——引擎已改 keep_alive=0+接看门人。

## 3-G 正交挖矿制（裁定#535 同源，2026-10-15）

**病根**：15 员池实际仅 4.4 个独立信号（FACT×5 corr=1.000 拷贝、RSRS×2 变体 0.97、2 员纯买入持有）——合成无分散增益，HOLDOUT 退化为买入持有。
**新目标**：挖矿产出按"与现有独立信号的正交性"计量，不按数量。三件套：
1. **正交准入闸**：新候选入台账前对独立信号库做 spearman 预检，`|corr|≤0.3` 才收（工具=scripts/backtest/fexam/signal_orthogonality.py gate 子命令）；不过闸记"重复"，喂 mined_out 判据。
2. **独立信号清单**：⑨成绩官每日维护（pool-report 子命令产出相关矩阵+参与率），存 `docs/_working/automation_campaign/pulse/independent_signals.md`——③④席与点子引擎 prompt 的必读"占领区摘要"。
3. **正交方向单**：⑨除 fail 分诊外每日给出空白轴地图（波动率/流动性/资金面/另类数据等未被占轴），③④优先去无人占的轴挖。

### 8-A 机器层四闹钟产物存放表（与 10 岗同规范，2026-10-15 补全）

| 闹钟 | 产物 | 存放处 | 层 |
|---|---|---|---|
| NightMining 夜挖 | lane_b/lane_c3 候选种子 CSV | data/strategy_intake/lane_b,c3_candidates.csv | 过程层（进货台账，只增） |
| NightMining 夜挖 | 运行日志 | .runtime/logs/night_mining.log | 非资产（随清理） |
| F06Grid 网格窗 | 窗产物（manifest.csv/summary.json/网格工件） | data/strategy_intake/grid_*/＋data/backtest_artifacts/ | 过程层（可重建，归档可清） |
| F06Grid 网格窗 | 幸存者台账 | data/strategy_intake/f06_survivors.csv | 结论层（进货侧，only-add） |
| F06Grid 网格窗 | 收窗总结（叙事终稿） | docs/04_research_records/backtest/campaigns/f06_<窗日期>/ | 叙事层（promote 三步） |
| TTLRejudgeDaily | 触发/执行日志 | .runtime/logs/ | 非资产；复考成绩一律走⑦⑧⑨通道入分数册，禁旁路 |
| C4Exam 考试夜批 | 增量分数行 | docs/04_research_records/backtest/scores/<YYYY>/（经 only-add 通道） | 结论层 |
| C4Exam/TTL | 运行日志 | .runtime/logs/ | 非资产 |

### 8-A-2 治理裁定记录制度（2026-10-15 Owner 采认）

**分片登记+⑩聚合，不建共写集中册**（共写面=双侧皆改死袋头号件面教训）：各席每班在自己 ledger.md 追加 `[BLOCKER] 日期|席+班号|类型|证据锚点|要谁做什么|严重度` 行，**零问题也须写 `[BLOCKER] 无`**（沉默≠没问题）；⑩每班扫各席 [BLOCKER] 汇总进晨报（全量+严重度列，粒度不收窄）；每周一⑩将上周全集定稿 promote 至 `docs/04_research_records/governance/adjudication/<周册>/`（promote 三步）。修复方就地翻状态必须附修复证据（commit 哈希或文件路径）。历史统一入口（99_owner_gate.md 等）已在归档区，不复活。

机器层通用规矩：产出的数字/文件=**原料**，只有经⑨成绩官判卷入分数册的才算成绩；叙事终稿进 04 走 promote 三步；日志永远 .runtime 非资产；四闹钟 runner 脚本头部的产物路径注记由⑤席/维护班下一班对齐本表（脚本行为不变，只补注释）。


## 8. 研究态资产存放规范 v2 对齐（裁定#536，2026-10-15 生效；制度页=automation_sop/research_asset_storage_spec.md 禁另造副本）

四层分流：结论层→分数册（04/backtest/scores/）｜数值层→CH c1_backtest.*｜过程层→run_archive+n_trial_ledger（可重建）｜叙事层→04 区各栏。
**Owner 判定总则（2026-10-15）**：①用完即删的→_working（ttl 任务期，如派单/水位快照/班间交接/游标）；②永久需要存放的→04。**04 准入资格=可复验**：所存必须是研究数据与研究结果，且内容足以支持恢复与复验（SQL/参数/file:line 锚点/相关性证据随件，只存结论不留证据链=不合格）。班台账类活文档任务期住 _working，收官定稿携全量证据链 promote 进 04。
本线资产落点（v2 对照）：运行面（派单/反馈/水位/四件套/班间交接）=docs/_working/automation_campaign/ 不变（带 ttl+游标，**禁入 04**）｜分数册=04/backtest/scores/<YYYY>/ only-add｜挖矿台账收官终稿 promote→04/mining/ledgers/<campaign_id>/｜**矿脉枯竭判定书**（mined_out 申报+六向查证+交叉复挖结论）→04/mining/exhaustion/<YYYY>/ 逐节点一册｜战役总报→04/backtest/campaigns/<id>/ 或 cross_domain/<id>/｜复盘案卷→04/backtest/postmortems/<YYYY>/｜耗尽预注册卡存档→04/backtest/prereg_archive/<YYYY>/｜新考试卡=03 卡册不变（生成器 only-add）。
四规矩：命名 `YYYYMMDD_<域码>_<类型码>_<slug>_v<N>`（域码 bt/mining/data/gov；类型码 score/exam/report/postmortem/card/ledger；ASCII ≤60；词表真源=docs/01_policies_and_standards/_registry/catalogs/domain_naming_rules.yaml）｜表头九必填（doc_type/ttl:permanent/schema_version/created/sid/family_id/domain/title_zh/status）｜叶子夹 120 硬顶 100 预警｜写完新件跑 scripts/governance/generate_research_index.py（机生禁手改）。
**promote 三步**：ttl task_bound→permanent＋落 04 对应栏＋跑索引生成器。

## 9. 新信号挖掘线作战规程（条件轴复核班交接，2026-10-15；十方向=③④席**持久作业菜单**（楼图子册=docs/_working/automation_campaign/pulse/mining_directions.md，逐楼状态+游标轮转，封矿即切楼——非一次性任务书；技术细节参考=桌面 condaxis_tmp/mining_lanes/new_signal_mission_brief.md））

**使命**：挖有预测力的新 alpha，过在册考试入池，把整装 HOLDOUT 净 Sharpe 从 −0.569 拉过 0 冲 ≥2。旧池 15 员已判死（有效独立信号仅 4.4，毛 −0.425）。
**七门槛（禁自拟数值）**：①相关性门与 15 员日净敞口 |corr|≤0.3（基准=condaxis_tmp/corr_15members.csv）②毛 Sharpe 新鲜样本>0 底线/≥0.5 推荐入库线 ③净 Sharpe（含 dampen）C 门>0、冲刺≥2 ④换手≤8x（Σ|Δw|/2×244，exam_scale_cost_gate.yaml E7 门）⑤独立预测≥60 笔或信号天数≥120 日 ⑥样本≥120 观测/事件≥30 次（裁定#532 同源）⑦MaxDD 如实记录暂不设门。量化结论：单信号毛 0.5~1.0×3~5 个独立信号即可达标。
**十方向（P0=盘口微结构族：39.5 亿行 tick_data+1.3 亿行 tick_depth_5，盘口因子消费量=0，完全未开发）**：盘口（OBI/5 档压力/WMP 偏离/大单流向/spread）｜财务基本面｜估值｜动量反转（残差动量优先）｜波动率｜流动性 Amihud｜资金流（sector_fund_flow）｜另类（两融/股东户数/解禁/大宗/龙虎榜）｜市场状态｜情绪重建（emotion_index C1/C2/C5/C6 缺失重建即是新信号）。
**七步流程**：W_IS（2019-04..2023-12）开发初筛→W_OOS 复验（只淘汰不录取，与池选择窗重叠）→相关性门→预注册冻结（先冻结后跑）→**HOLDOUT 单次烧毁**（每配置唯一一次，烧完禁改参重跑）→合成验证（旧池非冗余成员+dampen tau60）→滚动前哨（W_POSTD+新样本，唯一无污染窗）。
**资源路径**：引擎=scripts/backtest/ibt/ibt_runner.py（四窗定义+15 员 MEMBERS+build_panels/run_engine）｜成员样板=scripts/backtest/translated/c4_fact_4f749668.py 等 15 个｜dampen 参考实现=桌面 condaxis_tmp/turnover_pilot.py｜成本门=scripts/backtest/ibt/exam_cost_gate.py+config/exam_scale_cost_gate.yaml｜行情=zephyr.factor.core.evaluation.backtest.load_history｜CH=zephyr.data.ch_reader（**判据读数用 query_rows()，禁 query() 串 TSV、禁 count() 假 0**；库 c1_market@172.24.30.100:8123）。
**纪律**：严禁 HOLDOUT/OOS 调参后宣称成绩（自证窗教训=虚高 1.63 Sharpe）｜判据全沿用上表禁放宽｜临时件放桌面 condaxis_tmp 自建子夹、**禁写 docs/_working**（TTL 归档中）｜禁 git commit（总包统一提交）｜如实报告，缺一项视为未完成；每候选必报：定义/数据源/与 15 员相关性/三窗毛净 Sharpe/换手/独立观测数。
**岗位接线**：③④席按十方向开挖（P0 盘口）｜⑤实现席产信号代码｜⑥制卡席预注册冻结｜⑦⑧考工出分｜⑨成绩官判卷+维护独立信号清单（§3-G）｜过门者回传总包做合成与终局验证。
