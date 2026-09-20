---
ttl: task_bound
title: W1d 层归属映射素材——判例表 + 目录口径表 + 全量归层草案表 + 争点清单
owner: ZephyrAlpha-Owner
session: st-vocabconsol-20260918
date: 2026-09-18
status: draft
---

# W1d 层归属映射素材

> 战役：模块三层/四层归属（W4a 目标真源 `docs/01_policies_and_standards/_registry/vocabularies/domain_layer_mapping.yaml`）。
> 本文=挖矿产物，只读调研，不改任何既有文件。映射草案四值：`governance / business / ai / infrastructure`。
> 归层原则（任务给定）：门禁/网关/审计/纠察/规则执行=governance；行情/因子/信号/回测/风控/组合/执行/前端/数据接入/报表=business；编排器/自主核心/反馈循环/ML 训练服务/知识/LLM 安全/自我进化=ai；进程守护/备份容灾/遥测/数据库服务/消息总线/环境运维=infrastructure；拿不准标 `?` 并写争点。
> 实查路径全部可复核。

---

## 0. 结论速览

- **草案表实测 79 行**（68 个 registry 去重 `D_*` 域 + 11 个 depgraph 在用但未进 registry 的域）。战役口径"约 84 域"= 68 + 上位施工包 A 组 16 入 values；本文独立挖到 11 个明确在用增量，其余 5 个差额（如连字符/全称别名 `D_PORTFOLIO_CORE`/`D_EXECUTION_CORE`/`D_RED_BLUE_VALIDATOR` 等）由上位 `00_workorder_施工包.md` A/B/C 差集清单定稿，本文不擅自补数（§9.5 静态清单禁手工维护）。
- **`?` 数：10**（registry 核心表 9 + 新增表 D_TEST 1；另有 4 个"soft"标 `business?`：D_REGIME/D_RESEARCH/D_DATA_ENG/D_DIGITAL_TWIN）。见 §3 与 §4。
- **最大争点**：vision 的 `governance/business/ai/infrastructure` 是**职责分层**，与既有 depgraph `domains.layer_id` 的 `L0_infrastructure / L1_foundation / L2_domain` 是**运行时栈分层**，两套口径**正交且字面冲突**（`L2_domain` ≠ `business`：绝大多数 governance 域也挂在 `L2_domain`）。新 `layer` 字段若不显式改名/加命名空间，会与既有 `layer_id` 同名混淆。详见 §4-C1。

---

## 1. 判例表——vision 文档已有的"归边"先例

真源：`docs/_working/ai_layer_vision/ai_layer_vision_and_roadmap_v1.md`（v2.0.3，Owner 2026-09-17 夜全批）。
三层定案（§0/定调1）：**治理层=不犯错 / 业务层=赚钱 / AI 层=进化**；"三层是职责分层不是运行时栈（AI 层横切一切）"。以下为可抽取为归边依据的全部判例：

| # | 判例（原文锚点） | 归边结论 | 对映射的意义 |
|---|-----------------|---------|-------------|
| P1 | 定调2"消化系统归 AI 层，找策略归业务层——AI 层建胃，业务层点菜" | 搜索-收集-清洗-对比-排产这套"胃"=**ai**；用胃产出策略=**business** | 收集/清洗/对比/排产类引擎归 ai；下游策略生产归 business |
| P2 | 定调2"业务层 E1 第六车道点'策略原料'，治理层点'治理新章法'，AI 层自己点'AI 工程进展'" | 三类客户各点各层：策略原料=business 消费、治理章法=governance 消费、AI 工程=ai 消费 | 层的"服务对象/消费方"可作辅助判层 |
| P3 | §0"治理层内含两种职能：控制（门禁=二线式实时拦）+独立保证（纠察/审计=三线式独立抽查），二者分离本身就是纪律" | 门禁/网关（控制）+纠察/审计（独立保证）统一归 **governance**（不拆到 ai） | 关键：纠察/审计不因"像自动化"落 ai，而锁定 governance |
| P4 | 定调7.5 排班表归属三段裁定 | 规则与裁决=**governance+Owner**；自动化运营=**ai 运营轴**；使用=两层客户自助登记 | 一张资源/排班资产被三段切开——层归属可"按字段/职能"拆，不必整域单一层（争点来源） |
| P5 | §二"AI 层不持自己的尺子（考纲/阈值/rubric 归治理层标准库，AI 层只有使用权+提案权）" | 规则/标准/门禁的"定义权"=governance；AI 仅使用/提案 | OBJ_R（规则/标准）本体归 governance，非 ai |
| P6 | §四 Owner 四类事 + "必须留人四底线"（支付/实名/转正拍板/明文密钥） | 资金/密钥/门位=**governance 门位**（high tier） | 实盘资金动作所在域按门位算 governance，业务链路算 business |
| P7 | §五"三层刹车：资源刹车（配额）→权限刹车（门位+密钥隔离）→时间刹车（revert+TTL+审计链）"；reaper 电闸=最后刹车 | 刹车/熔断/审计链=revenue governance；配额调度=ai 运营轴约束 | KillSwitch/审计/reaper 分别落 governance 与 infrastructure |
| P8 | §一 引擎轴 L1-L7 七段一常数 + 对象轴 OBJ_M/T/R/S | 感知/收集/清洗/对比/排产/切换/传承 = **ai** | 对应 D_FEEDBACK_LOOP / D_ORCHESTRATOR / D_AUTONOMY_CORE 等归 ai |
| P9 | §0 表 KPI：治理层=违规漏拦=0、业务层=整装策略收益、AI 层=进化速度 | 每层唯一 KPI 可作反查：收益导向=business，进化=ai，防错=governance | 归层的最终校验尺 |
| P10 | 附录 D"risk_tier_registry high 九域四门位/资金破坏性=high" | 资金/注册表净删/flag 翻转/production 流转=governance 门位 | 与宪法 §5 人机门位一致 |

**判层三把尺（从判例收敛）**：①服务对象（谁消费该域产出）②职能性质（防错=治理 / 赚钱=业务 / 进化=AI / 兜运行=基础设施）③KPI 归属（漏拦 / 收益 / 进化速度 / 可用性）。

---

## 2. 目录口径表——`docs/03_modules/` "目录=层"隐含口径

真源：`docs/03_modules/` 目录清单（`ls` 实查，2026-09-18）。既有目录命名已隐含一层"归组"，但**不是** vision 四值——它是"物理/职责混合"分组。以下给每个目录→四值建议归组（`?`=争点，理由见 §4）。

| 目录 | 建议四值 | 一句话依据 |
|------|---------|-----------|
| `_domain_governance` | governance | 生命周期/注册表治理 |
| `_domain_gov_audit` | governance | 审计追踪 |
| `_domain_gov_drift` | governance | 漂移检测=纠察（P3） |
| `_domain_gov_enforcement` | governance | 门禁/规则执行（P3） |
| `_domain_gov_rule` | governance | 规则治理（P5） |
| `_domain_compliance` | governance | 合规门禁（争点 C3） |
| `_domain_data_governance` | governance? | 数据治理→"治理"字面 vs 数据域，争点 C4 |
| `_domain_data_security` | governance? | 数据安全与契约，安全边界 vs 数据基建，争点 C5 |
| `_domain_governance`（重复见上） | — | — |
| `_domain_factor` | business | 因子 |
| `_domain_signal` | business | A股信号策略集（大量 pattern/sector 策略子目录） |
| `_domain_signal_quality` | business | 信号质量控制 |
| `_domain_fundamental_signal` | business | 基本面信号 |
| `_domain_mkt_data` | business | 行情数据 |
| `_domain_alt_data` | business | 另类数据接入 |
| `_domain_data` | business | 数据接入层（争点 C6：接入 vs 基建） |
| `_domain_data_eng` | business? | 数据工程 ETL 管道，接入(business) vs 基建(infra) 争点 C6 |
| `_domain_backtest` | business | 回测 |
| `_domain_simulation` | business | 仿真 |
| `_domain_execution_sim` | business | 执行仿真 |
| `_domain_digital_twin` | business? | 数字孪生/场景推演，业务镜像 vs 研究基建 争点 C7 |
| `_domain_execution_core` | business | 执行核心 |
| `_domain_ex_sor` | business | 执行路由 |
| `_domain_risk` | business | 风控 |
| `_domain_portfolio_core` | business | 组合核心 |
| `_domain_portfolio_alloc` | business | 组合分配 |
| `_domain_pf_alloc` | business | 组合分配（与 `_domain_portfolio_alloc` 同义并存，争点 C8 目录冗余） |
| `_domain_position` | business | 仓位管理 |
| `_domain_trading` | business | 交易运营 |
| `_domain_plan_engine` | business | 预案引擎（明日边界/盘前约束） |
| `_domain_regime` | business? | 市场状态检测（HMM），业务链路 vs ML(ai) 争点 C9 |
| `_domain_sell_decision` | business | 卖出决策 |
| `_domain_frontend` | business | 前端 |
| `_domain_reporting` | business | 报表 |
| `_domain_research` | business? | 研究域，找策略=business(P1) vs 知识进化=ai，争点 C10（且 note 记录归并 D_KNOWLEDGE 未终局） |
| `_domain_orchestrator` | ai | 代理编排器 |
| `_domain_autonomy_core` | ai | 自主核心（Skill/Agent 生命周期） |
| `_domain_autonomy_perm` | ai? | 自治保护/预算/升级，进化约束=ai vs 权限护栏=governance 争点 C11 |
| `_domain_feedback_loop` | ai | 反馈循环引擎（自我进化） |
| `_domain_fbl_detectors` | ai | 反馈检测器 |
| `_domain_intelligence` | ai | 上下文管理引擎 |
| `_domain_knowledge` | ai | 知识/向量记忆 |
| `_domain_machine_learning_train` | ai | ML 训练服务 |
| `_domain_ml_serve` | ai? | 推理服务，ML 训练服务=ai vs 生产在线服务=business 争点 C12 |
| `_domain_security_llm` | ai | LLM 安全（LSG） |
| `_domain_red_blue_validator` | ai? | 红蓝对抗=进化安全带(P3/§五) vs 独立保证纠察=governance 争点 C13 |
| `_domain_integration` | ai? | 管线路由/LLM 网关，进化管线=ai vs 消息基建=infra 争点 C14 |
| `_domain_infrastructure` | infrastructure | 跨层契约基础设施 |
| `_domain_infrastructure_operations` | infrastructure | 基础设施运维 |
| `_domain_infrastructure_runtime` | infrastructure? | 运行时集成，含 DB 持久化=infra vs 运行时编排=ai 争点 C15 |
| `_domain_contracts` | infrastructure | 共享契约 |
| `_domain_shared` | infrastructure | 共享服务（event bus/熔断/配置） |
| `_cross_layer` | infrastructure? | 跨层公共件（含 database/cd_pipeline/clone_guard 等混装），争点 C16（单目录跨多层） |
| `_master_blueprint` | governance | 全图总蓝本（元治理） |
| `_system_master` | governance | 系统总纲（元治理） |

> 目录口径**非权威**：`_cross_layer`、`_domain_signal` 等目录内文件实际声明多个不同 `D_*` 域（`_domain_signal` 实测声明 D_ASHARE_SIGNAL/D_FACTOR/D_BACKTEST/D_FRONTEND/D_ML_TRAIN/D_PORTFOLIO_CORE… 跨 business/ai），证明"目录=层"只是导航便利，**不可直接作为归层真源**（争点 C17）。

---

## 3. 全量归层草案表

### 3.1 68 个 registry 域（真源 `functional_domain_registry.yaml`，`grep -oP '^- domain:'` 实测 68 去重）

辅助字段：每条 registry 项有 `domain / subdomain / domain_name_zh / ssot_module / ssot_path / covers / aliases / stability / ai_autonomy`。可辅助归层的主要是 `domain_name_zh + covers`（职责语义）；`ai_autonomy`（immutable_core/human_gated/ai_modifiable）可作治理门位强弱旁证（immutable_core 多为 governance/安全）。`tier` 字段在 registry 头部为 `tier_1_governance`（整表级），非域级；`owner` 为表级 MOD-INF-037，**均不可域级辅助归层**。

| domain_id | 建议 layer | 归层依据（一句话） |
|-----------|-----------|------------------|
| D_GOV_ENFORCEMENT | governance | 门禁引擎/规则强制=二线实时拦（P3） |
| D_GOV_SCRIPTS | governance | 脚本治理/审计注册（P3） |
| D_GOV_DRIFT | governance | 漂移检测=三线独立纠察（P3） |
| D_GOVERNANCE | governance | 注册表/生命周期元治理 |
| D_GOV_AUDIT | governance | 审计追踪/审计链=独立保证（P3/附录C-4） |
| D_GOV_REPAIR | governance | 治理修复/回滚/Checkpoint（时间刹车 P7） |
| D_GOV_RULE | governance | 规则治理/规则注册表=标准定义权（P5） |
| D_GOV_DOCS | governance | 架构文档治理 |
| D_GOV_CODE_QUALITY | governance | 代码质量治理/提交门禁/去重 |
| D_GOV_OPS_RESILIENCE | governance | 运维/安全/弹性**治理**（名字带治理优先落 governance，注：底座弹性近 infra 争点 C18） |
| D_COMPLIANCE | governance | 合规校验/前置审批门禁（注：监管报告生成子项近 business 争点 C3） |
| D_AUDITTEST | governance | 审计测试套件（注：tests/ 与自家测试边界争点 C19） |
| D_FBL_VERIFICATION | ? | 反馈循环**门禁/安全门禁/验证器**→governance，但父域 feedback_loop 属 ai，边界争点 C20 |
| D_SECURITY | ? | RBAC/KillSwitch/不可变核心→governance，红蓝对抗/孤儿审判→ai 安全带（P3），跨层争点 C13/C21 |
| D_SECURITY_LLM | ai | LLM 安全/LSG 九层防御（原则明列 LLM 安全=ai） |
| D_AUTONOMY_CORE | ai | 自主核心/Skill 渐进披露/Agent 生命周期 |
| D_AUTONOMY_PERM | ? | 自治保护（预算/升级/委托）——进化约束=ai vs 权限护栏=governance 争点 C11 |
| D_INTELLIGENCE | ai | 上下文引擎（AI 层核心） |
| D_FEEDBACK_LOOP | ai | 反馈循环引擎/自我进化（定调3 七段闭环） |
| D_FBL_DETECTORS | ai | 反馈检测器（异常/漂移检测，FLE 分册） |
| D_FBL_DIAGNOSERS | ai | 反馈诊断器（根因诊断/模型健康监控） |
| D_OPS | ? | 遥测(telemetry=infra)+反馈循环(feedback=ai) 混域，双身份争点 C22 |
| D_ORCHESTRATOR | ai | 代理编排器/任务队列/幻觉检测 |
| D_ML_TRAIN | ai | ML 训练服务（模型能力考试/画像） |
| D_ML_SERVE | ? | 推理服务——ML 训练服务=ai vs 生产在线服务=business 争点 C12 |
| D_KNOWLEDGE | ai | 知识/向量记忆（记忆银行） |
| D_INTEGRATION | ? | 管线路由/M1-M11 双管线/LLM 网关——进化管线=ai vs 消息基建=infra 争点 C14 |
| D_INTEGRATION_GATEWAY | ? | MCP 11 服务端+Gateway——"网关"字面=governance 但实为工具服务基建/ai 争点 C23 |
| D_MKT_DATA | business | 行情数据接入 |
| D_FACTOR | business | 因子计算/因子库 |
| D_ASHARE_SIGNAL | business | A股特色信号 |
| D_FUNDAMENTAL_SIGNAL | business | 基本面信号 |
| D_SIGQC | business | 信号质量控制（业务链路质控，非纠察） |
| D_SIGLEGACY | business | 信号遗留设计态 |
| D_SIGNAL | business | 遗留图示用名（deprecated），随信号族归 business |
| D_BACKTEST | business | 回测 |
| D_RISK | business | 风控 |
| D_PF_CORE | business | 组合核心 |
| D_PF_ALLOC | business | 组合分配 |
| D_PORTFOLIO | business | 遗留图示用名（deprecated） |
| D_POSITION | business | 仓位管理 |
| D_EX_CORE | business | 执行核心 |
| D_EX_SOR | business | 执行路由 |
| D_EXECUTION | business | 遗留图示用名（deprecated） |
| D_ORDER | business | 遗留图示用名（deprecated） |
| D_TRADING | business | 交易运营 |
| D_PLAN | business | 预案引擎（明日边界/盘前约束） |
| D_REGIME | business? | 市场状态检测——业务覆盖层触发（倾向 business，HMM 近 ai 争点 C9） |
| D_SELL_DECISION | business | 卖出决策 |
| D_SIMULATION | business | 仿真/模拟撮合 |
| D_EXEC_SIM | business | 执行仿真 |
| D_DIGITAL_TWIN | business? | 数字孪生/场景推演——业务镜像（争点 C7） |
| D_CROSS_ASSET | business | 跨资产/套利策略 |
| D_FRONTEND | business | 前端 |
| D_DATA | business | 数据接入层 |
| D_ALT_DATA | business | 另类数据接入 |
| D_DATA_ENG | business? | 数据工程 ETL 管道（接入=business vs 基建=infra 争点 C6） |
| D_DATA_GOV | ? | 数据治理——"治理"字面 vs 数据域底座 争点 C4 |
| D_DATA_SEC | ? | 数据安全与契约（访问控制/加密）——安全边界=governance vs 数据基建 争点 C5 |
| D_REPORTING | business | 报表（投资/风险/合规报告生成分发） |
| D_RESEARCH | business? | 研究域/事件研究——找策略=business(P1) vs 知识进化=ai，且归并 D_KNOWLEDGE 未终局 争点 C10 |
| D_SHARED | infrastructure | 共享服务（event bus/熔断/配置/文件工具） |
| D_INFRASTRUCTURE | infrastructure | 跨层契约基础设施 |
| D_INFRA_OPS | infrastructure | 基础设施运维/容量/资产盘点 |
| D_INFRA_RUNTIME | infrastructure? | 运行时集成+DB 持久化（含"系统大脑"编排近 ai 争点 C15） |
| D_INFRA_A2A | infrastructure | A2A 通信=消息总线 |
| D_INFRA_RECOVERY | infrastructure | 回滚恢复/容灾 |
| D_INFRA_TELEMETRY | infrastructure | 可观测性/遥测 |

### 3.2 W1 新增在用域（depgraph/05_trading_domains.md 有节点但未进 registry 的 11 域）

真源：`docs/02/.../project_handbook/05_trading_domains.md` §3 域清单（AUTO，depgraph 同步）与 registry `comm` 差集实测。

| domain_id | 建议 layer | 归层依据 |
|-----------|-----------|---------|
| D_ARCH_SCRIPTS | governance | 架构治理脚本 |
| D_META_SCRIPTS | governance | 元治理脚本 |
| D_ARCH_GUARD | governance | 架构守护脚本 |
| D_COMPLIANCE_SCRIPTS | governance | 合规治理脚本 |
| D_DATA_SCRIPTS | governance | 数据治理脚本 |
| D_CODE_SCRIPTS | governance | 代码质量脚本 |
| D_SEC_SCRIPTS | governance | 安全治理脚本 |
| D_STRUCT_SCRIPTS | governance | 结构治理脚本 |
| D_ARCHIVE_SCRIPTS | governance | 已归档脚本（退役墓碑制，随脚本族 governance） |
| D_CONTRACTS | infrastructure | 共享契约 |
| D_TEST | ? | Test Domain（depgraph 0 节点，语义待定，争点 C24） |

> 战役口径"16 新增在用"与本文实测"11"的差额：`D_PORTFOLIO_CORE`/`D_EXECUTION_CORE`（target_layer_vocabulary 里作全称别名/deprecated）、`D_RED_BLUE_VALIDATOR`（`_domain_red_blue_validator` 目录存在但内部无独立 `D_*` 声明）、若干连字符历史 bug 值（`D-DATA`/`D-SIGNAL`/`D-FACTOR`/`D-RESEARCH`，词表已 deprecated）。**定稿集应以上位施工包 A 组为准**，本文不背数（宪法 §4 文档纪律：计数用字段勿写死散文）。

---

## 4. 争点清单（`?` 与需裁定的边界）

### 4.1 顶层争点（C1 最大争点）

- **C1（最大争点）·两套"层"口径正交冲突**：vision 四值 `governance/business/ai/infrastructure`（**职责分层**）vs 既有 depgraph `domains.layer_id` = `L0_infrastructure/L1_foundation/L2_domain`（**运行时栈分层**，见 05_trading_domains.md §3 全表 + panorama_registry.md "GAP-TBL-10 domains(layer_id)"）。二者**不是同一坐标**：`L2_domain` 里 governance 与 business 域混装（例：D_GOV_DOCS 与 D_FACTOR 同为 `L2_domain`）。**冲突处置**：新 `layer` 字段建议命名 `responsibility_layer`（或 `layer_vision`）与既有 `layer_id` 物理区隔；映射生成器**不得**从 `layer_id` 直接推导。二者可并存但必须各自有真源，禁互相覆写。
- **C2 ·整域单一层的假设不成立**：vision 排班表三段裁定（P4）与 `AI 不持尺子`（P5）证明同一"资产/域"的不同职能可分属多层。域→层是**多对一近似**，遇 governance（定义权）× ai（使用/提案权）复合域时须以"主职能/KPI"定层，其余以注释留痕。

### 4.2 逐域 `?` 争点

- **C3 D_COMPLIANCE**：门禁校验=governance；但"监管报告生成"子项=business reporting。整域倾向 governance，报告子项留痕。
- **C4 D_DATA_GOV / C5 D_DATA_SEC**：数据治理/数据安全名字带"治理/安全"，但 ssot 在数据底座（data_governance/data_security）。是"governance 的数据分支"还是"infrastructure 的数据域"？争点＝**治理词 vs 数据底座**。
- **C6 D_DATA_ENG**：ETL 管道——数据接入=business（原则）vs 数据基建=infra。
- **C7 D_DIGITAL_TWIN**：市场镜像/组合模拟=business vs 场景推演研究基建。
- **C8 `_domain_portfolio_alloc` 与 `_domain_pf_alloc` 目录冗余**：同一 D_PF_ALLOC 两套目录，先收目录再定层，否则映射生成器重复条目（呼应 W1b loader 重复键病灶）。
- **C9 D_REGIME**：业务覆盖层触发（CRISIS/RECOVERY）=business；HMM 推断近 ai/ML。倾向 business，注 ML 争点。
- **C10 D_RESEARCH**：registry note 亲记"归并 D_KNOWLEDGE vs 独立终局裁定留 Owner，现状两口径并存"。找策略=business(P1)，但研究资产/假设验证近 ai 知识。**未决，须裁定**。
- **C11 D_AUTONOMY_PERM**：预算/升级/委托护栏——进化约束=ai vs 权限门位=governance。
- **C12 D_ML_SERVE**：ML 训练服务=ai；但"在线生产推理服务"支撑赚钱链路=business。
- **C13 D_SECURITY / D_RED_BLUE（红蓝）**：RBAC/KillSwitch/不可变核心（ai_autonomy=immutable_core）=governance；红蓝对抗/孤儿审判/对抗验证=AI 进化安全带（P3/§五）。**同一域跨治理与 AI**，最大内部分裂域。
- **C14 D_INTEGRATION**：管线路由/LLM 网关=进化管线（ai）vs 消息中间件（infra）。
- **C15 D_INFRA_RUNTIME**：ssot covers 同时含"三层运行时编排/夜班队列/自动入职（系统大脑）"与"DB 持久化/连接池（infra）"。名字=infrastructure，但"运行时编排/冷启动/会话恢复"是 AI 层执行底座。
- **C16 `_cross_layer` 目录跨多层**：内含 database(infra)/cd_pipeline(governance)/clone_guard(governance)/large_language_model_security(ai) 等，目录无法整组归一层。
- **C17 目录≠域≠层**：`_domain_signal` 实测声明跨 business/ai 的多域，证明"目录=层"仅是导航便利，**不可作归层真源**；真源须回到 registry `covers` 语义。
- **C18 D_GOV_OPS_RESILIENCE**：底座（circuit_breaker/fault_tolerance/chaos）是 infra 韧性能力，但域定位是"治理"。词首 governance。
- **C19 D_AUDITTEST**：tests/ 目录。宪法测试隔离（§9.6）与 W1a/W5 豁免关联；归 governance（审计）还是排除于映射外（测试非运行层）？
- **C20 D_FBL_VERIFICATION**：与 D_FEEDBACK_LOOP 拆分——验证器/安全门禁是 governance（二线拦截）还是随 FLE 归 ai？父 ai、职能 governance。
- **C21 D_SECURITY 的 ai_autonomy=immutable_core 旁证**：immutable_core 强治理信号，倾向 governance 主导，红蓝子域单列。
- **C22 D_OPS 双身份**：covers 同时有 telemetry（infra）与 feedback-loop（ai），且 D_INFRA_TELEMETRY 独立存在→职责重叠，建议 D_OPS 收敛或拆分后再定层。
- **C23 D_INTEGRATION_GATEWAY**："网关"字面命中 governance 原则，但实为 11 个 MCP 工具服务=ai/infra 边界。
- **C24 D_TEST**：depgraph 0 节点、layer 标注"—"，是占位域还是映射外集合？

### 4.3 交叉核对结论（任务 4）

- **05_trading_domains.md**：已给全部 75 域的 `L0_infrastructure/L1_foundation/L2_domain`——**属运行时栈分层（C1），不作 governance/business/ai 归层先验**，但可作"底座 vs 领域"旁证（L0_infrastructure 集合与本表 infrastructure 高度重合：D_INFRA_RUNTIME/D_SHARED/D_INFRA_A2A/D_INFRA_RECOVERY/D_INFRASTRUCTURE/D_CONTRACTS；L1_foundation 混含 ai+business+governance；L2_domain 混含 business+governance）。
- **panorama_registry.md**：`domains(layer_id)` 字段=同上 L0/L1/L2 口径（GAP-TBL-10 记 50 域 2 行 layer_id 为 NULL）；决策流图 `decision_layers` L0-L6 是决策链分层，**亦非职责四层**。→ panorama 无现成"职责四层"口径可采，故 §3 草案以 registry `covers` 语义 + vision 判例（§1）为第一真源。
- **target_layer_vocabulary.yaml**：值注释已按"交易核心域/治理域/基础设施域/AI 智能域/安全域/集成域/测试域/信号域/共享域"分组——**是最接近的既有归组先例**（治理域 13 项、基础设施域含 D_FEEDBACK_LOOP/D_ORCHESTRATOR 被并列——注意此处已把 ai 性质的域塞进"基础设施"注释，是需纠正的历史噪声，勿照抄）。

---

## 5. 给 W4a 的可执行建议（不改文件，仅提示）

1. `domain_layer_mapping.yaml` 四值 enum：`governance/business/ai/infrastructure`（+ 允许 `"?"`/`unclassified` 承载争点，季度收敛）。
2. 字段命名避开既有 `layer_id`（C1）：建议 `responsibility_layer`。
3. 生成器输入=registry `covers`+`domain_name_zh`+§1 判例关键词，**禁从 `layer_id`/目录名直推**（C17）。
4. C13/C22 等跨层复合域先走裁定（RULE-RULING 登记 ruling_registry，同 commit 原子）再落映射。
5. §9.5 红线：域→层映射为静态清单，必须生成器产出，禁手工维护。
