---
ttl: task_bound
title: L06-子模块 上岗规则与配置矩阵填报（成绩单→state_matrix→路由，v1 稿已备待追认）挖干
created: 2026-09-25
sid: st-qmine-20260925
lane: L06_exam_alloc
status: SEALED-CORE（六向内部反查全填、③向外部双源；填格原料=GPU 成绩单在途属挂起非封矿）
skeleton_source: ../SKEL.md L06-E/L06-F；../../09_link_skeletons.md 环节6；判据 ../../17_quantified_acceptance.md §一
doc_role: L06 挖矿子模块 MINE（覆盖 SKEL L06-E 成绩单→上岗规则半边）
---

# 子模块 · 上岗规则与配置矩阵填报（onboarding_rules_matrix）

> 本块 = L06"上岗半边缺位"本体：GPU 成绩单（每格 cost_adjusted_sharpe+DSR）→"条件共振→选策略"规则 →
> `state_matrix` 填格。**任务令更新事实**：上岗规则 v1 立法稿已成文（19 号文 C3/F3，"L06-C01 稿已备"），
> 挂起条件=Owner 追认 + 成绩单出档（非 SKEL 旧判"未立法"，本块不重裁、只把立法稿现状实测清楚）。

## ① 职责一句话
把"每策略在什么条件下考得最好"的成绩单，经"当日天气=条件共振"折成**挂谁 / 给多少钱 / 走哪个因子面**的上岗决策，
落进 `state_matrix` 与路由常量——即"考试结果→选策略规则"的最后一公里。

## ② 现状实测（代码 file:line + 表/配置实测）

### 立法稿现状（唯一形态=设计稿，config 零落地）
- 真源件：`docs/_working/daily_loop_campaign/routing_table_v1_draft.md`（frontmatter `completes_when: Owner 批准映射口径并授权 config 落地`，:5；本稿仅设计不改 config，:10-11）。
  - §2 路由三级：Level0 六段状态（regime_snapshot dominant + TDM-E-L1 双轴仲裁）→ Level1 策略包路由（真源=`state_matrix.cells`，禁复制第二份，:37）→ Level2 配比（PP-001 sleeves + TDM-F-C1 预算带，:42-45）→ Level3 因子面（:46-48，TERMINATE#304 gate 禁翻案）。
  - §3 落地三步（**全部待 Owner 批**）：①映射常量入 `plan_engine`（代码批）②ignition/euphoria 拆分阈值+60% 硬顶+过渡带系数入 config（Owner 门位）③空格填格（Owner 资金分配门位，R41 封闭词表，:54-58）。
- 19 号文：C3 行（`19_gpu_plan_and_master_backlog.md:51`）="上岗规则 v1 Owner 追认→state_matrix 六空格填报，原料=GPU 成绩单，**L06-C01 稿已备**"；F3（:92）="上岗规则 v1 + 仲裁序 v1 追认，稿件+成绩单齐"；contextual bandit v2（:83）=v1 跑通一个日循环后（本块 = v1，非 v2）。

### state_matrix 六空格实测（`config/trading_decision_map.yaml`）
- 矩阵载体=各节点 `strategy_mounts` 字段（:60-865 绝大多数为 `[]`，仅 :300/:629/:717 非空）；六段↔七态注释（:33）"疯狂→euphoria / 退潮→distribution"。
- SKEL 实证口径（yaml:5556-5650，本块沿用不重数）：TDM-E-L1 三格 filled proposed（capitulation/accumulation/expansion）+ **三格空 pending-owner-adoption（ignition/euphoria/distribution）**；euphoria/distribution 备注明示"PP-001 无防御型 sleeve"、distribution 预算带 0% 禁新开仓（SKEL L06-E ②）。
- 生产触发面：**无程序化读端**——编排器 S4（PackageDecision 消费方）本体不存在=BT-P1-031（SKEL L06-E ③"消费链虚挂"）；现网读端仅 `daily_decision_orchestrator.py` 产 BUDGET_BANDS 仓位上限（:95-99,412-420），不消费 state_matrix 挂载格。

### 数据新鲜度
- 填格原料=GPU T1 3,700 格成绩单（`data/strategy_intake/grid_20260924-213246/`，跑批中，明晚完赛）；**成绩单未出=填格挂起的硬前置**（非规模问题）。
- 立法稿本身时戳=st-dloop-20260921（routing 稿 frontmatter :3），§4 已实证 PP-001 快照读通（16 sleeves Σ=1.0）+ 五态行已产（09-18 盘中 4 行）但**映射未落地**。

## ③ 六向台账（内部反查 + 全网搜索双动作）

| 向 | 内部反查发现 | 全网外部反查 |
|---|---|---|
| ①上游 | 成绩单口径（cost_adjusted_sharpe 主目标+毛夏普观察+DSR 门槛，17 §一）；解读纪律="考尺口径相对排名"，跨引擎绝对值翻译待 IBT-D01（同名格 sharpe 差>30% 列差异清单，17:24）；考试结果读出面=见 `../exam_result_writeback/MINE.md`（三态桶 pass/fail/insufficient） | 机构对照=regime-aware 动态资产配置（见 ③）；已查无"成绩单→上岗"直译范式（业界多以信号层/组合优化层落地，本仓走查表 v1，如实注） |
| ②下游 | 消费方：编排器 S4（不存在=虚挂，BT-P1-031）；`daily_decision_orchestrator.py`（现产预算带，不读挂载格）；pf_alloc 分配链；framework_composer activation（→ `resonance_friction_assembly` 块） | 待外部（并入 ③） |
| ③算法/机制 | 路由结构=Level0-3 查表（routing 稿 §2）；六段↔五态映射**全仓无定义**（§1 LK-16，五态→六段多对一保守收敛，亢奋→ignition 简化、euphoria 需 Owner 拍阈值，:20-31） | **≥2 源**：① arXiv 2406.09578 "Dynamic Asset Allocation with Asset-Specific Regime Switching"（arxiv.org/html/2406.09578v2，2024）——逐资产 regime 切换驱动配置=本块 Level0→Level2 同构；② López de Prado meta-labeling（腾讯云开发者社区 2020 "金融机器学习 10 大应用" cloud.tencent.com/developer/article/1731476 + waylandz.com/quant-book/Meta-Labeling方法）——二级模型只裁"下注方向/是否上岗"=本仓"条件共振→上岗"的机构原型（SKEL L06 §差异注：TDM 无独立上岗层，meta-labeling/pod 即其机构对照）。**A 股适配闸**：meta-labeling 原设连续可做空，A 股 T+1/涨跌停⇒上岗只裁"挂哪只已注册的合法策略"、不做方向对冲，适配通过（改造=路由到已合规 sleeve 非裸信号） |
| ④后端 | 立法稿落地三步全缺代码（§3 未做）；`plan_engine` `_STATE_LABEL_MAP` 常量落点建议存在但未写（:30-31）；D30 六空格 AI 禁自填（yaml 备注明文，SKEL L06-C02）；IBT-D01 对照表 / IBT-G01 成绩单上板桥无码 | 待外部反查（查表式路由 vs bandit 的工程实现，见标准件 `resonance_friction_assembly` 块 mabwiser） |
| ⑤前端 | 成绩单→上岗面板：`src/zephyr/frontend/dashboard/components/backtest_results.py` 现无 grid 成绩单源（SKEL L06-C09/IBT-G01）；上岗决策 PackageDecision 无 UI（编排器不存在） | 已查无：无"上岗矩阵格子"前端页；登记边界=呈现随 C09 上板桥，本块不越界施工 |
| ⑥数据字段 | `state_matrix` 词表 R41 封闭（pending-owner-adoption/by-design-empty/pending-evidence，缺键=DECISION-MAP gate 阻断，SKEL L06-E ②）；填格原料字段=成绩单 cost_adjusted_sharpe + 六段条件格；"字段在≠可得"：六空格结构位都在，缺的是**Owner 决策值 + 成绩单数值**双缺 | 待外部反查（配置矩阵/sleeve 配比字段口径，属本仓私有语义，业界无标准词表，记"已查无标准定义+查法：对比 Riskfolio sleeves/weights 口径"） |

## ④ 缺口清单（沿用编号 + 续编）

| 编号 | 缺口 | 册内可见性 | 状态/解锁条件 |
|---|---|---|---|
| **LK-10** | 上岗规则 v1：立法稿已成文（19 C3 "稿已备"），**待 Owner 追认 + config 落地** | SKEL L06-E ⑥（旧判"未立"→本块更新为"稿备待批"） | 挂起排期；解锁=Owner 门位批准 §3 三步 + 成绩单出档 |
| **D30** | state_matrix 三空格 pending-owner-adoption（ignition/euphoria/distribution） | SKEL L06-E/C02 | 挂起；解锁=Owner 资金分配门位 + 成绩单条件格可填 |
| **D31** | 预算带/过渡带数值 proposed→confirmed | SKEL L06-E ⑥ | 挂起；解锁=Owner 逐项批（60% 硬顶/过渡带系数） |
| **LK-16** | 六段↔五态映射全仓无定义 | routing §1 / SKEL L06-E ⑥ | 挂起→施工：映射常量入 plan_engine（§3 步①，Owner 批后） |
| **IBT-D01（P0）** | 成绩单口径对照表/声明（考尺平面 2.5/10/5bp ↔ 整装 matching_logic） | SKEL L06-E/C03 | 施工前置=成绩单落盘；判据 17 §一（sharpe 差>30% 列清单） |
| **IBT-G01** | 成绩单上板桥（BacktestResult 适配器，前端无 grid 源） | SKEL L06-E/H | 施工；前置=成绩单落盘 |

> 本块新增续编：无（六缺口全部沿用 SKEL/L06-C01~C03 在册号，未"册内未见"新立；如后续查得新面会标注）。

## ⑤ 自审闸三态裁定（mining_sop §6）

- **终局定位**：上岗=把"考试结论"变"可执行资金分配"的唯一咽喉，终局全貌里必自动化（Owner 仅批阈值/门位，其余机器填）。**不得封矿**。
- **裁定=挂起排期为主 + 部分施工**：
  - **挂起排期（解锁条件明确）**：LK-10/D30/D31 三门位均为 Owner 门位（AI 禁自填，宪法 §5 high 域）——解锁=Owner 追认 §3 三步 + GPU 成绩单出档（明晚完赛）。这不是"规模小"，是终局要的 Owner 决策 + 数据前置。
  - **可施工（不等门位）**：LK-16 映射常量入 plan_engine 属代码批（等长替换，走 review）；IBT-D01/IBT-G01 属数据桥接，成绩单落盘即可起手。
- **矿脉判读**：立法稿 + 六格现状 + 路由三级 + 六段↔五态空洞均实证到 file:line，本块六向内部见底；外部双源已锚定机构原型。**矿脉未枯但见底**——残余长尾=Owner 批后的 config 实际落地与 plan_engine 改动（属施工，非挖掘）。

## ⑥ 挖矿日志（mining_sop §7）

| 轮 | 矿脉 | 动作 | 判定 | 归因 |
|---|---|---|---|---|
| R1 | 立法稿 + 19 号文门位 + state_matrix 载体 | 读 routing_table_v1_draft 全文 + grep 19 号文 C3/F3 + grep trading_decision_map strategy_mounts/pending | **signal**（v1 稿备待批实锤、落地三步全待 Owner、消费链虚挂） | — |
| R2 | ③算法向外 + 六段↔五态映射 | grep framework_composer activation（→ 邻块）+ WebSearch meta-labeling/regime-switching（arXiv 2024 + LdP 两源） | **signal**（机构对照=meta-labeling 二级门 + asset-specific regime allocation；A 股适配闸过） | — |
| R3 | 前端面板 + config 落地现状 | grep backtest_results.py / plan_engine `_STATE_LABEL_MAP` | **查无**（面板无 grid 源、映射常量未写）——属"已落地=零"的负面结论，记档 | 归因=方向本就无物（config 零落地是立法稿的既定状态，非搜索不当） |

> 本块无 noise 轮。邻块边界：framework_composer activation / auto_mount R2SIX vs orchestrator 分叉 / 组合装配 E8 → `../resonance_friction_assembly/MINE.md`；成绩单搜索与预注册 → `../search_executor_prereg/MINE.md`。
