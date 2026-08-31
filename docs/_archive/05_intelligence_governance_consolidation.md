---
ttl: permanent
---

> **归档注记（2026-08-31）**：自 09_ai_architecture/implementation_plans/ 归档（终审批 gp1closure_20260831——GP1 两项全部闭环且无 GP1 遗留项（2026-08-30 状态修正已自证），残余仅远期 Q4 退役裁定属开放裁定非施工项，审计链保留，原位索引已同步标注）。
>
> **文档元信息**（_working 临时区豁免规范：EXEMPT-ZONE-FM）：doc_type=architecture_view · title=intelligence_governance 包整合施工图 · owner=ZephyrAlpha-Owner · language=zh · status=active · version=0.2.3 · date=2026-08-30 · topic=intelligence_governance_consolidation · scope=09_ai_architecture

# intelligence_governance 包整合施工图

> ## 结案报告（2026-08-28 全量审查批，代码实证；2026-08-30 状态修正）
> **实际开发**：intelligence_governance 包整合定稿（Phase 0=文档定稿，零代码改动性质，active v0.2.2）；src/zephyr/governance/intelligence_governance/ 24 个功能模块实证在位（delegation_engine/model_router/agent_debate/self_benchmark 等与文内清单逐名一致）。
> **最终成果**：包文件级细节真源+GP1 入口修复施工图确立；GP1 两项均已闭环——①`__init__.py` 入口腐烂已修复（2026-08-18，AI-ADJ-001，commit 8efacc2c70：PEP 562 惰性外观，`__all__` 42 个真实符号，契约测试 tests/governance/test_intelligence_governance_facade.py，见 §3.1/§6 Q1）；②文件头 [TESTS]/[CONSUMERS] 漂移已纠偏（2026-08-30：delegation_manager/mvep_orchestrator/provider_failover 三文件 [TESTS] 改为实测存在的测试路径、[CONSUMERS] 按全仓 import 扫描置空、[MODIFY-GUARD] 连字符路径统一为实测存在的下划线版；Q3 已核实，见 §6）。
> **未做+原因**：无 GP1 遗留项；远期 Q4（退役裁定）/Q5（迁移裁定，已按 D4 关闭）见 §6。

> 本文定位：`src/zephyr/governance/intelligence_governance/` 24 个功能模块的整合方案——统一入口、职责边界、与 AI 层的关系。
> 与其他文件的分工：结构设计见 [00_index.md](00_index.md)，资产登记（链接级）见 [02_design_asset_inventory.md](02_design_asset_inventory.md) §1「智能治理包」行——本文档是该包的文件级细节真源，不复制 02 号文的登记表。

---

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | intelligence_governance 整合 |
| 所属 | [00_index.md](00_index.md) §1 目标架构·AI 执行层·治理 Agent |
| 依赖 | `src/zephyr/governance/intelligence_governance/` 现有 24 个功能模块 + `__init__.py`（共 25 个 .py，实测 2026-08-17） |
| 优先级 | P1——治理 Agent 的核心能力包 |
| 状态 | active（骨架填充完成 v0.2.0；v0.2.1 一致性回填——03/14 号文已填充，接口假设已核对） |

---

## 2. 背景

### 2.1 项目处境

`src/zephyr/governance/intelligence_governance/` 是治理域（D_GOVERNANCE）下的"智能治理"能力包，承载 AI 自我治理相关的决策原语。实测现状（2026-08-17，LS + 逐文件行数统计）：

- **规模**：24 个功能模块 + 1 个 `__init__.py`，合计 3,223 行（含 `__init__.py` 49 行）；最大 `self_benchmark.py` 446 行，最小 `ai_self_diagnosis.py` 27 行，多数模块 <300 行。
- **名义入口已存在但已腐烂**：`__init__.py` 声明 `__all__` 33 项，但**全文件无任何 import 语句**（Grep `^(import |from )` 零匹配）——16 个类/函数名（`AgentDebate`、`DriftConfig`、`KnowledgeIndex` 等）在包命名空间中并不存在；其中 `DriftConfig/DriftType/KnowledgeEntry/get_drift_config` 实测定义在**包外**（`src/zephyr/gov_drift/`、`src/zephyr/shared/schema/schemas.py`），属于历史漂移残留。`__all__` 同时漏列 5 个实存模块（`agent_debate`、`autonomy_dashboard`、`confidence_quantifier`、`continuous_trust`、`cross_agent_conflict_detector`）。
- **文件头声明与实测漂移**：①`delegation_manager.py`/`mvep_orchestrator.py`/`provider_failover.py` 头部 `[TESTS] tests/test_escalation_engine.py`——该文件实测不存在（`Test-Path` 返回 False），实测相关测试为 `tests/f_lifecycle/test_f5_red_team_extreme.py`（importorskip 引用 `delegation_engine`）；②上述 3 个文件头部 `[CONSUMERS]` 声明的消费方（`zephyr.governance.services.adapter`、`zephyr.orchestrator`、`zephyr.infrastructure.escalation`）在全仓 import 扫描中零匹配；③`[BLUEPRINT]` 路径存在 `_domain_autonomy_perm/escalation_protocol`（实测存在）与 `_domain-autonomy_perm/escalation-protocol`（实测不存在）两种写法混用。
- **消费方实测**（全仓 Grep `from zephyr.governance.intelligence_governance` / `import ... intelligence_governance`，2026-08-17）：包外 12 个消费文件，集中消费 10 个模块——`delegation_engine`（escalation、resilience_governance/f5_boot_integration）、`model_router`（trading/auto_runtime_core、financial_governance/budget_enforcement）、`provider_base`（data_governance 3 个 provider）、`aisg_sandbox`（security_governance/default_security_gateway）、`self_test`（ops_governance/phase_check_registry）、`self_benchmark`（gov_code_quality/code_dedup/cli）、`continuous_trust`（gov_audit/bridges/audit_trust_bridge）、`agent_debate`/`ai_self_diagnosis`/`multi_model_consensus`（经 `zephyr/governance/__init__.py` 懒加载段）。其余 14 个模块无实测消费方（多为 v0.x 升级协议引入的自验证/防护小模块，由冷启动流程间接驱动或待接线）。
- **AI 层定位**：[00_index.md](00_index.md) §1 目标架构中，AI 执行层「治理 Agent」职责为 gate 检查/规则——本包正是治理 Agent 的能力底座；00_index §5.2 目录树已将本文档列入（实测 2026-08-17）。

### 2.2 核心问题

- **Q1 是否需要统一入口？** 名义入口已存在（`__init__.py` + `__all__`），但"有入口、入口腐烂"比"无入口"更危险——`from ... import *` 会拉到不存在的名字，AI 协作者按 `__all__` 编码会产生幻觉引用。问题实质不是"要不要建入口"，而是"**入口修复到什么程度算够**"（与 [02_design_asset_inventory.md](02_design_asset_inventory.md) 开放问题 Q1 同源）。
- **Q2 与 D_ORCHESTRATOR 的边界在哪？** 包内 `delegation_engine`（自动委托）、`mvep_orchestrator`（MVEP 阶段门）、`multi_model_consensus`/`agent_debate`（多模型共识/辩论）名字上像"编排"，而 [61_lifecycle_multi_ai.md](../../07_trading_decision_architecture/design_memos/61_lifecycle_multi_ai.md) §2.3 已裁定"不做 agent 编排系统（多 AI 协作是人调度多会话，非 agent 自治）"。必须划清"治理决策原语"与"Agent 编排"的边界，否则包会越长越像被否决的编排系统。
- **Q3 声明漂移如何收口？** 文件头 `[TESTS]`/`[CONSUMERS]`/`[BLUEPRINT]` 三类声明与实测不符（§2.1），这些声明是 S4 reconciler / 提交门禁的输入，漂移会误导门禁与 AI 协作者。

### 2.3 约束条件

- **硬边界**（[system_charter.md](../../04_architecture_principles_decisions/system_charter.md) §2）：1 人全栈 + AI 协作者、单机 PC、个人资金双账户；整合方案必须让 1 人可维护——禁止引入需要专职维护的抽象层。
- **已裁定否定式边界**：[61_lifecycle_multi_ai.md](../../07_trading_decision_architecture/design_memos/61_lifecycle_multi_ai.md) §2.3——不做 agent 编排系统；多 AI 并发治理走 [66_commit_queue_serialization.md](../../07_trading_decision_architecture/design_memos/66_commit_queue_serialization.md)（提交串行化）而非运行时编排。
- **施工纪律**：本包 24 个模块全部 `[MATURITY] production` 且 12 个消费文件在线引用——任何重命名/移动/合并都会断裂生产引用，故整合以"文档 + 入口修复"为主，代码零移动。
- **文档规范**：frontmatter/修订记录/开放问题遵循 [01_design_memo_management_spec.md](../../07_trading_decision_architecture/design_memos/01_design_memo_management_spec.md) §4；整合类按"现状→问题→方案→迁移→不做"组织（§4.4）。
- **只读纪律**：本指令集只改本文档；[03_domain_boundary_definition.md](03_domain_boundary_definition.md)（v0.2.1 已填充）、[14_execution_layer.md](14_execution_layer.md)（v0.3.0 已填充）只读引用——v0.2.1 已完成接口假设核对（结论见 §4.4、§6 Q2/Q5/Q6）；03 号文全部裁定仍为「待裁定」（Owner 拍板前本文边界假设按"分析倾向"口径暂成立，若冲突以 03 号文裁定为准并升版修订）。

### 2.4 已施工设施盘点

**A. 包内 24 个功能模块职责矩阵**（实测：LS 列文件 + 逐文件非空行数（Measure-Object -Line 口径）+ docstring/类定义读取，2026-08-17）

| # | 文件 | 行数 | 当前职责（docstring 摘要） | 蓝图归属 | 实测消费方 | 状态 |
|---|------|------|---------------------------|----------|-----------|------|
| 1 | delegation_engine.py | 249 | MOD-INF-022 自动委托引擎：owner 缺席/过载时按负载均衡/专长匹配/轮询/优先队列策略委托 | escalation_protocol | escalation、resilience_governance | production |
| 2 | delegation_manager.py | 65 | 委托管理器：委托链深度≤3、四级安全约束不可降级 | escalation_protocol | 无（头部声明漂移） | production |
| 3 | mvep_orchestrator.py | 47 | MVEP Phase Gate：Phase 0→5 顺序不可逆的阶段门 | escalation_protocol | 无（头部声明漂移） | production |
| 4 | provider_failover.py | 45 | Provider 降级链：顺序不可逆、ALL_STOP 可触发 | escalation_protocol | 无（头部声明漂移） | production |
| 5 | model_router.py | 249 | MOD-INF-024 模型路由：TaskComplexity×ModelTier 映射 + cost 0.5/speed 0.35/quality 0.15 性能感知评分 | budget-enforcer | trading、financial_governance | production |
| 6 | model_provider_data.py | 56 | 模型 Provider 静态数据（zhipu/deepseek 等价格、模型键） | — | 无（被 model_router 同包引用） | production |
| 7 | provider_base.py | 97 | MOD-L00-001 行情 Provider 抽象基类（QuoteProviderBase/Meta） | _domain_data | data_governance ×3 | production |
| 8 | memory_provider.py | 292 | D_DATA 内存模拟数据源：合成 A 股 OHLCV（CTR-001），测试/离线用 | — | 无 | production |
| 9 | multi_model_consensus.py | 28 | 多模型共识协议枚举 + escalate_to_owner | _domain_governance | governance 根 __init__ | production |
| 10 | agent_debate.py | 109 | Agent 辩论：DebateVerdict/DebateRound/ModelResponse 模型 | _domain_governance | governance 根 __init__ | production |
| 11 | confidence_estimator.py | 34 | D-022-05 置信度评估：certainty×0.4+evidence×0.35+(1-risk)×0.25 三档 | — | 无 | production |
| 12 | confidence_quantifier.py | 110 | MOD-INF-021 §7 Phase 9 置信度量化：连续 5 次 <0.3→exit 37 降 tier | MOD-INF-021 | 无 | production |
| 13 | meta_confidence.py | 41 | D-022-10 元置信度：Agent 对自身判定置信度的自评+历史校准 | — | 无 | production |
| 14 | continuous_trust.py | 290 | MOD-INF-021 §6.15 持续信任账本：trust→tier 0/1/2 分级自主 | MOD-INF-021 | gov_audit | production |
| 15 | cross_agent_conflict_detector.py | 121 | MOD-INF-021 §7 Phase 10 多 Agent 并发冲突检测：同文件双写→仲裁串行化 | MOD-INF-021 | 无 | production |
| 16 | aisg_sandbox.py | 204 | AISG 沙箱验证（INV-015）：模拟危险指令验证拦截 + 审计日志 | — | security_governance | production |
| 17 | ai_self_diagnosis.py | 27 | 自诊断：AutoFixLayer L1/L2/L3 + 已知模式自动修复 | — | governance 根 __init__ | production |
| 18 | self_test.py | 205 | MOD-INF-022 升级协议自检：冷启动 STEP 4.8 / Phase Manager 门禁，exit 0/1/2 | escalation_protocol | ops_governance | production |
| 19 | self_benchmark.py | 446 | W3-7 自基准：5 组已知对自验证 + 引擎退化告警 + 原子写历史 | — | gov_code_quality | production |
| 20 | self_validator.py | 33 | 升级协议规则自验证：rule_id/level/patterns 完整性 | — | 无 | production |
| 21 | autonomy_dashboard.py | 305 | MOD-INF-021 §6.15 自治健康仪表：health<0.3 持续 5 分钟→降级+exit 35 | MOD-INF-021 | 无 | production |
| 22 | model_version_detector.py | 39 | 模型版本突变检测：版本变更→degraded auto_guard | — | 无 | production |
| 23 | subagent_hook_propagator.py | 37 | 子 Agent Hook 旁路防护 | — | 无 | production |
| 24 | cross_assistant_adapter.py | 45 | Trae/Cursor/Windsurf/Codex/Wedata 五 IDE 统一升级接口 | — | 无 | production |
| — | __init__.py | 49 | 包入口：仅 `__all__` 33 项声明，**无 import 语句（腐烂）** | MOD-GOV-intelligence_governance | — | draft（待修复） |

**B. 包外消费方矩阵**（全仓 import 扫描实测）

| 消费方 | 消费模块 | 消费方式 |
|--------|---------|---------|
| `zephyr/governance/__init__.py`（懒加载段） | agent_debate / ai_self_diagnosis / multi_model_consensus | 懒加载 |
| `governance/escalation/__init__.py` | delegation_engine | 顶层 import |
| `governance/resilience_governance/f5_boot_integration.py` | delegation_engine | 函数内 import ×2 |
| `governance/financial_governance/budget_enforcement.py` | model_router | 顶层 import |
| `governance/security_governance/default_security_gateway.py` | aisg_sandbox | 顶层 import |
| `governance/data_governance/{miniqmt,akshare,akshare_quote}_provider.py` | provider_base | 顶层 import ×3 |
| `governance/ops_governance/phase_check_registry.py` | self_test | 函数内 import |
| `trading/auto_runtime_core.py` | model_router | 顶层 import |
| `gov_code_quality/code_dedup/cli.py` | self_benchmark | 函数内 import |
| `gov_audit/bridges/audit_trust_bridge.py` | continuous_trust | 函数内 import |

**C. 配套测试**：`tests/f_lifecycle/test_f5_red_team_extreme.py`（红队极限测试，importorskip 引用 delegation_engine/escalation_api）；`tests/automation/test_auto_runtime_*.py`（patch init_escalation_protocol）。**注意**：文件头声明的 `tests/test_escalation_engine.py` 实测不存在。

**D. 关联蓝图与门禁设施**：`docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md`（实测存在，MOD-INF-022）；MOD-INF-021 / MOD-INF-024 / MOD-L00-001 / MOD-GOVERNANCE（文件头 [BLUEPRINT] 声明）；depgraph 设计态门禁 `src/zephyr/gov_enforcement/commit_gates/new_file_depgraph_gate.py`、`depgraph_pre_registration_gate.py`（实测存在）；文件锁 `scripts/lock_files.py`、提交网关 `scripts/git_commit.py`（实测存在）。

**E. 兄弟包上下文**：`src/zephyr/governance/` 下实测 30 个子目录（2026-08-18 复测；v0.2.0 实测时为 29，新增 1 个兄弟子目录，不影响本包边界）（a2a、escalation、ops_governance、data_governance、security_governance……），intelligence_governance 是其中之一；另有 5 个带连字符目录（agent-rbac、agent-spec、audit-trail、budget-enforcer、drift-detector）非合法 Python 包名，不在本整合范围。

---

## 3. 设计决策

### 3.1 决策一：统一入口 = 修复现有 `__init__.py`，不新建 facade

**决定**：保留单一 `__init__.py` 作为唯一公共入口，修复内容为——①`__all__` 与实存模块/类对齐（删掉漂移名 `DriftConfig/DriftType/KnowledgeEntry/KnowledgeIndex/get_drift_config/get_index`（前 4 项定义在包外、后 2 项全仓无类/def 定义），补列漏掉的 5 个模块）；②对 10 个有实测消费方的核心类做显式 re-export，其余保持"子模块路径导入"惯例；③入口内不写任何业务逻辑。

**裁定与施工状态（已裁定+已施工 2026-08-18）**：本方案已获裁定并完成施工（AI-ADJ-001，commit 8efacc2c70）——`__init__.py` 已修复为 PEP 562 惰性外观（`_SYMBOL_TO_MODULE` 映射 + `__getattr__` 按需 import，包级零 eager 子模块加载），`__all__` 42 个真实符号（剔除 6 个幻影名与双义 `DebateRound`——双义名包级不导出、子模块路径自取），新增契约测试 `tests/governance/test_intelligence_governance_facade.py` 4 项守住出口契约，28 个消费方测试文件 570 测试全绿。形式=修复为惰性外观，非新建 facade，与本文裁定一致。

**Why**：
- 名义入口已存在且被 S4 reconciler 自动注入注释管理——新建 facade 会变成第二入口，违反真源唯一，且 reconciler 可能覆盖手写 facade。
- 24 个模块总计仅 ~3,200 行、1 人维护——为 ~3,200 行代码再建一层 facade 抽象是典型过度工程（system_charter §2 约束一人力）。
- 12 个消费文件全部使用"子模块路径导入"（`from ...intelligence_governance.X import Y`），无一方依赖包级 re-export——说明包级入口的真实价值是**给 AI 协作者/文档读者看的"目录声明"**，不是运行时必需。修复 `__all__` 真实性即可满足该价值，成本最低。
- `__init__.py` 全量 re-export 会引入导入时副作用链（如 cross_agent_conflict_detector 依赖 subprocess 工具），懒加载式最小 re-export 避免拖慢 `import zephyr.governance`。

**考虑过的替代方案**：①新建 `facade.py` 统一门面——否决，双入口 + reconciler 冲突 + 过度抽象；②删除 `__init__.py` 的 `__all__` 回到纯命名空间包——否决，`__all__` 是 S4 reconciler 与文档读者的契约锚点，删了等于放弃入口；③全量 re-export 24 个模块全部公共类——否决，导入副作用 + 维护面扩大。

### 3.2 决策二：职责重划 = 文档级七组命名，零文件合并/拆分/退役

**决定**：本期不做任何文件的合并、拆分、移动、退役；只在本文档与入口注释中确立七组职责分组（Why 层边界），物理布局保持不变：

| 组 | 模块 | 组职责 |
|----|------|--------|
| G1 委托与升级协议 | delegation_engine / delegation_manager / mvep_orchestrator / provider_failover | owner 缺席时的自动委托 + MVEP 阶段门 + 降级链（MOD-INF-022） |
| G2 模型路由与供给 | model_router / model_provider_data / provider_base / memory_provider | LLM 路由评分 + Provider 抽象/数据/内存模拟源 |
| G3 置信与信任 | confidence_estimator / confidence_quantifier / meta_confidence / continuous_trust | 置信度三维评估→量化→元校准→信任账本（MOD-INF-021） |
| G4 多智能体协议 | multi_model_consensus / agent_debate / cross_agent_conflict_detector / subagent_hook_propagator | 共识/辩论/并发冲突/Hook 旁路防护（协议层，非编排） |
| G5 安全沙箱 | aisg_sandbox | AISG 拦截实测验证（INV-015） |
| G6 自验证与基准 | ai_self_diagnosis / self_test / self_benchmark / self_validator / autonomy_dashboard / model_version_detector | 自诊断/自检/自基准/规则自验证/自治仪表/版本突变检测 |
| G7 跨 IDE 适配 | cross_assistant_adapter | 五 IDE 统一升级接口 |

**Why**：①全部模块标 production 且有在线消费方，移动/重命名的断裂风险远大于"目录整洁"收益；②职责重叠实测很轻——唯一近似对是 `confidence_estimator`（34 行规则评估）vs `confidence_quantifier`（110 行流程量化，挂 exit 37），二者层次不同（G3 内互补），合并收益不抵修改成本；③1 人维护 24 个 <450 行的内聚模块，导航成本用"文档分组"即可解决，不需要物理重组。

**考虑过的替代方案**：①按七组物理拆分子目录——否决，断裂 12 个消费文件 import 路径；②合并 confidence 两文件——否决，层次不同且各有蓝图依据；③退役 14 个无实测消费方模块——否决，多数由冷启动/升级协议流程间接驱动（如 self_test 挂冷启动 STEP 4.8），"无静态 import"≠"无运行时消费"，退役裁定需逐个实测运行时调用链，列为开放问题 Q4。

### 3.3 决策三：与 D_ORCHESTRATOR 的边界裁定——治理决策原语 vs Agent 编排

**决定（边界假设，待 03 号文确认）**：
- **intelligence_governance 做"治理决策原语"**：在单个治理动作内部提供决策能力（委托谁、用哪个模型、置信度够不够、是否降级）——输入是治理事件，输出是决策/分级/告警，**不持有 Agent 生命周期，不调度 Agent 执行顺序**。
- **"编排"在本项目已被否定式裁定**：[61_lifecycle_multi_ai.md](../../07_trading_decision_architecture/design_memos/61_lifecycle_multi_ai.md) §2.3——多 AI 协作是"人调度多会话"，不做 agent 编排系统。因此 D_ORCHESTRATOR 的职责上限是**任务/阶段的确定性流转**（如 AutoRuntime 的 phase 流转），不是 Agent 自治编排。
- **包内 4 个"疑似编排"模块的归属澄清**：`mvep_orchestrator` 是 MVEP 阶段**门控**（判定 Phase 可否推进），不是编排器——名字带 orchestrator 但语义是 gate；`delegation_engine` 是"决策委托给谁"的路由，不执行被委托任务；`multi_model_consensus`/`agent_debate` 是协议与数据结构层，且 61 号备忘已暂缓"LLM 多 Agent 辩论"的运行时落地——本期保留为协议定义，不接运行时编排。

**Why**：边界不划清，本包会在"治理"名义下缓慢吸收编排职责，最终长成已被否决的系统；划清后，治理 Agent（00_index §1：gate 检查/规则）消费本包原语即可，编排需求一律导向"人调度多会话 + 提交串行化"的既定路线。

### 3.4 决策四：错位归属文件本期不动，只登记

`memory_provider.py`（D_DATA 内存数据源）与 `provider_base.py`（行情 Provider 抽象）从 docstring/蓝图看属数据域资产，`model_provider_data.py`/`model_router.py` 与 `intelligence/model_profiling/` 关系更近——但四者均有生产消费方（provider_base 被 data_governance 3 个 provider 继承，model_router 被 trading 引用）。**决定**：本期只登记错位事实（本节 + §6 Q5），不迁移；迁移与否牵涉数据域/画像域的归属裁定，属 03 号文域边界职责，本文档不越权。

### 3.5 替代方案汇总

| 方案 | 结论 | 否决/采纳理由 |
|------|------|--------------|
| 新建 facade.py | 否决 | 双入口、reconciler 冲突、过度抽象（§3.1） |
| 修复 __init__.py | **采纳** | 成本最低、满足"目录声明"真实价值（§3.1） |
| 物理拆七组子目录 | 否决 | 断裂生产 import（§3.2） |
| 文档级职责分组 | **采纳** | 零风险解决导航问题（§3.2） |
| 退役无消费方模块 | 暂缓 | 静态无 import ≠ 运行时无消费，待逐个实测（§6 Q4） |
| 错位文件迁移 | 暂缓 | 域归属裁定属 03 号文职责（§6 Q5） |
---

## 4. 施工计划

> 组织方式：现状→问题→方案→**迁移**→不做（01 号规范 §4.4 整合类）。本节为迁移/落地方案。
> **depgraph 说明**：本计划不新建任何模块文件（`__init__.py` 修复属既有文件修改，depgraph 条目 MOD-GOV-intelligence_governance 已登记（`__init__.py` 文件头 [A_module] 声明），故"新建模块先登记 depgraph 设计态"无适用对象；若未来执行 §6 Q4/Q5 的退役/迁移，届时第一步必须先做 depgraph 设计态登记（status=planned），验证通过后转 production——门禁设施 `new_file_depgraph_gate.py` / `depgraph_pre_registration_gate.py` 已在仓。

### 4.1 阶段总览

| 阶段 | 目标 | 代码改动 | 依赖 |
|------|------|---------|------|
| Phase 0 | 文档定稿 + 入口修复设计 | 零代码改动 | 无（本阶段即本文档） |
| Phase 1 | `__init__.py` 修复 + 文件头声明纠偏 | 仅 `__init__.py` + 3 个文件头注释 | Phase 0 + 用户裁定 Q1 |
| Phase 2 | 治理 Agent 接口对接 | 零本包代码改动（消费侧在 14 号文范围） | ~~14_execution_layer.md 填充完成~~ 已满足（v0.3.0）；文档级核对 v0.2.1 完成，入口级对接待 Phase 1 |
| 远期（P4） | Q4 退役裁定 / Q5 迁移裁定 | 待定 | 03 号文域边界 + depgraph 登记 |

### 4.2 Phase 0：文档与统一入口设计（本轮已完成）

1. ✅ 实测盘点 24 个模块职责矩阵与消费方矩阵（§2.4）。
2. ✅ 七组职责分组定稿（§3.2），作为入口注释与文档导航标准。
3. ✅ 入口修复设计定稿（§3.1）：`__all__` 对齐清单 = 24 个实存模块名 + 10 个核心类 re-export 候选（DelegationEngine、DelegationManager、ModelRouter、RoutingDecision、QuoteProviderBase、ContinuousTrust、SelfBenchmark、run_self_test、AgentDebate、escalate_to_owner——最终以 Phase 1 实施时逐文件核对的公共类为准）。
4. ✅ 边界裁定假设落盘（§3.3）+ 开放问题登记（§6）。
5. 验收：本文档通过红蓝对抗审查；02 号文 Q1 有明确回答（§3.1）。

### 4.3 Phase 1：入口修复与声明纠偏（待用户裁定 Q1 后施工）

1. 修改 `__init__.py`：按 §3.1 重写 `__all__` 与最小 re-export；保留 S4 reconciler 注释块结构。
2. 纠偏 3 个文件头：`delegation_manager.py`/`mvep_orchestrator.py`/`provider_failover.py` 的 `[TESTS]` 改为实测存在的测试路径或置空，`[CONSUMERS]` 按 §2.4-B 实测修正；统一 `[BLUEPRINT]` 路径写法为实测存在的 `_domain_autonomy_perm/escalation_protocol`。
3. 验证：`python -c "import zephyr.governance.intelligence_governance"` 通过；`from ... import *` 不拉取不存在名字；`run_self_test()` 退出码 0；12 个消费方文件 import 无回归（pytest 相关测试集抽跑）。
4. 验收标准：`__all__` 每项均可 `getattr` 命中；文件头声明与全仓扫描零漂移。
5. 提交走 GitCommitGateway（`scripts/git_commit.py`），禁止裸 commit。

### 4.4 Phase 2：治理 Agent 接口对接（文档级核对 v0.2.1 已完成）

[14_execution_layer.md](14_execution_layer.md) 已填充（v0.3.0，2026-08-18 核对）。文档级核对结论：

1. **接口形态核对——一致**：14 号文 §3.1 治理 Agent「处理=调用 intelligence_governance/ 治理能力包 + feedback_loop/gates/ 门闸组 + security/access_control/ guards」，即**薄入口直接组装本包**，与本文 §3.1 决策（修复现有入口、不建 facade）及现有 12 个消费方的子模块路径导入惯例一致，无设计冲突。
2. **14 号文降级路径的隐藏依赖（新发现，2026-08-18 已解除）**：14 号文 Phase 0 S0.2 注记"若 05 号文未定型，入口直接组装包级 `__all__` 导出"——本文 §2.1 实测当时 `__init__.py` 的 `__all__` 已腐烂（无 import、含幻觉名），该降级路径一度不可用；**2026-08-18 入口已修复为 PEP 562 惰性外观（§3.1 裁定+施工状态，commit 8efacc2c70），降级路径现已成为可用面**——"治理入口若先施工须用子模块路径导入"的临时口径同时作废（子模块路径导入仍是合法惯例，但不再是唯一选择）。见 §6 Q6。
3. **"治理 Agent → 本包"调用矩阵**（按 14 号文 §3.1/§3.3 职责映射，组号见 §3.2）：

   | 14 号文职责/场景 | 消费本包模块 | 组 |
   |---|---|---|
   | 治理 Agent·验证自检（"self_test.py / self_benchmark.py 自检"） | self_test / self_benchmark | G6 |
   | 治理 Agent·gate 检查与规则判定（调用治理能力包） | aisg_sandbox（沙箱验证，INV-015）/ confidence_estimator·confidence_quantifier·meta_confidence·continuous_trust（置信与信任分级） | G5 / G3 |
   | 治理 Agent·owner 缺席/过载时委托决策 | delegation_engine / delegation_manager（委托链≤3、安全约束不可降级） | G1 |
   | 治理 Agent·降级链/阶段门 | provider_failover / mvep_orchestrator | G1 |
   | 算法 Agent·模型选择（14 号文 §3.3 假设锚点，production） | model_router（+model_provider_data） | G2 |

4. **接口缺口**：未发现缺口——14 号文四类 Agent 中仅治理/算法两类消费本包，且所消费模块全部 production 在线；业务/自我迭代 Agent 不消费本包（14 号文 §3.2/§3.4），符合预期。
5. 验收（已满足）：治理 Agent 每个职责（gate 检查/规则/验证）均能映射到本包具体模块（上表）；剩余入口级对接（治理入口消费修复后的 `__all__` 出口）依赖 Phase 1 完成，随 Phase 1 验收一并回核。

### 4.5 验收标准汇总

- Phase 0：文档六节齐全、实测数字可复验（验证方式见 §2.4 各表注）。
- Phase 1：import 无回归 + `__all__` 零幻觉名 + 文件头零漂移声明。
- Phase 2：14 号文接口假设全部确认或转开放问题。

---

## 5. 不做什么

1. **不做大规模代码重构**：不合并、不拆分、不移动、不重命名任何模块文件；整合以文档 + 入口修复为主（§3.2）。
2. **不做 agent 编排系统**：[61_lifecycle_multi_ai.md](../../07_trading_decision_architecture/design_memos/61_lifecycle_multi_ai.md) §2.3 已裁定；本包多智能体协议模块（G4）保持协议层，不接运行时编排。
3. **不改 D_ORCHESTRATOR 及其他域代码**：只裁定边界假设（§3.3），不越权施工；错位文件迁移属 03 号文职责（§3.4）。
4. **不新建 facade/抽象层**：不为 ~3,200 行代码引入第二入口（§3.1，system_charter §2 一人维护约束）。
5. **不建集群化/分布式治理能力**：单机 PC 约束，无多节点治理、无分布式共识。
6. **不做运行时模块热插拔/插件市场**：远期愿景且超出当前硬件与人力边界。
7. **不替 02/03/14 号文更新状态**：02 号文 Q1 状态同步由 AI-FILL-02 裁定，本文档只提供回答（§3.1），真源唯一、禁止双向同步。

---

## 6. 开放问题

| # | 问题 | 状态 | 说明 |
|---|------|------|------|
| Q1 | intelligence_governance 包是否需要统一入口？ | **已裁定+已施工 2026-08-18** | §3.1：需要，形式 = 修复现有 `__init__.py` 而非新建 facade——已按裁定施工为 PEP 562 惰性外观（`__all__` 42 个真实符号，剔除 6 幻影名与双义 DebateRound），契约测试 `tests/governance/test_intelligence_governance_facade.py` 4 项，28 个消费方测试文件 570 测试全绿（AI-ADJ-001，commit 8efacc2c70）。与 [02_design_asset_inventory.md](02_design_asset_inventory.md) 开放问题 Q1 同源，02 号文状态同步属 AI-FILL-02 职责。 |
| Q2 | 与 D_ORCHESTRATOR 的关系？ | **已裁定 2026-08-18（按裁定 2 关闭）** | 03 号文 §3.3 D5 已裁定采纳倾向①：D_ORCHESTRATOR 维持域名不改，语义澄清为「任务/阶段的确定性流转 + Agent 生命周期基础设施（回滚/容错/健康/质量门/契约）」，明确「生命周期基础设施 ≠ Agent 自治编排」（61 号备忘 §2.3/§4.1/§5.1 冻结编排路线，§5.2 第三阶段重评口子保留）。本文 §3.3 边界假设（本包=治理决策原语，4 个疑似编排模块定性为门/路由/协议原语）与裁定同向，按裁定收口。 |
| Q3 | 文件头 `[TESTS]`/`[CONSUMERS]`/`[BLUEPRINT]` 漂移是否影响 S4 reconciler/提交门禁？ | **已核实（2026-08-30）：影响有限——无硬阻断，纠偏已施工** | 实证依据：①S4 reconciler（`reconciliation_registry.py` GATE-MODULE-ID-RECOMMEND，post-commit）只读文件头前 500 字符检测/注入 `[BLUEPRINT]`，不读 `[TESTS]`/`[CONSUMERS]`；②pre-commit `consumers_accuracy_gate.py`（CONSUMERS-ACCURACY，priority=116，warn-only）读 staged src/**.py 的 `[CONSUMERS]`，但 commit-time 只检 orphan/phantom（stale 留给 baseline-scan 脚本），且漂移声明 `zephyr.infrastructure.escalation` 经逐级缩短命中实存包 `zephyr.infrastructure`，连 phantom 警告亦不触发；③`tests_coverage_gate.py`（META-TESTS-COVERAGE，priority=99，硬阻断）读 `[TESTS]` 但 trigger 限 `src/zephyr/gov_enforcement/commit_gates/*.py`，本包文件不在扫描范围；④post-commit GATE-CONSUMERS-ACCURACY-BASELINE 全扫 `[CONSUMERS]` 仅 warn。结论：漂移污染 AI 协作者判断与 warn 级基线报告，但对这 3 个文件不构成提交阻断；2026-08-30 已完成纠偏（`[TESTS]` 改为实测路径 tests/infrastructure/test_delegation_manager.py、tests/governance/orchestrator/test_mvep_orchestrator.py、tests/governance/resilience/test_provider_failover.py；`[CONSUMERS]` 三文件均置空——全仓 import 扫描无实测消费方；`[MODIFY-GUARD]` 连字符路径统一为实测存在的 `_domain_autonomy_perm/escalation_protocol`），无需同步门禁预期。 |
| Q4 | 14 个无静态消费方模块是否存在运行时间接消费？可否退役任何模块？ | 待实测 | 需逐个追冷启动/升级协议调用链（如 self_test 挂冷启动 STEP 4.8）；裁定前一律保留（§3.2）。 |
| Q5 | memory_provider / provider_base（数据域特征）与 model_router / model_provider_data（画像域特征）是否迁移出本包？ | **已裁定 2026-08-18（按裁定 2 的 D4 关闭）** | 03 号文 §3.3 D4 已裁定采纳倾向①：intelligence_governance 整包维持 D_GOVERNANCE 归属+横切标签，不迁域不新建子域——包级不动则文件级迁出亦不执行，本期登记口径关闭（§3.4 登记事实保留）。 |
| Q6 | 治理 Agent 调用本包的接口形态（直接 import vs 经 governance services 适配层）？ | **已核对（2026-08-18 二次核对：降级路径可用）** | 核对结论（§4.4）：14 号文治理 Agent = 薄入口直接组装本包，与本文 §3.1 及现有 12 消费方惯例一致，无接口缺口。2026-08-18 更新：包级 `__all__` 已修复（AI-ADJ-001，commit 8efacc2c70），14 号文 S0.2 降级路径"组装包级 `__all__`"现已成为可用面；此前"治理入口若先施工须用子模块路径导入"的临时口径作废（子模块路径导入仍是合法惯例，但不再是唯一选择）。14 号文 Q6 与本问同源，已同步更新。 |
| Q7 | TTL-METADATA 门禁与本文档集 frontmatter 冲突：门禁 valid doc_type 列表不含 `implementation_plan` | **本文档已收口；目录级 doc_type 统一裁定待 Owner** | 本文档 doc_type 已修正为合法值 `architecture_view`，2026-08-17 Gateway 补提交成功（commit a65a8b8a）。目录级取值仍不统一（00=index、03/05=architecture_view、14=blueprint），14 号文 Q7 已登记该裁定需求，统一裁定后如需回填本文 doc_type 再升版。 |

---

## 修订记录

| 日期 | 版本 | 变更 | 原因 |
|------|------|------|------|
| 2026-08-17 | 0.1.0 | 骨架建立 | 新建 |
| 2026-08-17 | 0.2.0 | 骨架填充完成：§2 实测盘点 24 模块职责/消费方矩阵（修正"~20 文件"为实测 24 模块 3,223 行；发现 `__init__.py` 无 import、文件头三类声明漂移）；§3 四项决策（入口修复而非 facade、文档级七组分组零物理改动、D_ORCHESTRATOR 边界假设、错位文件只登记）；§4 Phase 0→2 + 远期；§5 七项不做；§6 开放问题扩至 Q1-Q6 | AI-FILL-05 填充：将"约 20 文件无统一入口"的模糊表述落实为可复验的实测现状与可施工方案；03/14 号文未填充，接口假设降级入开放问题；当日晚 Gateway 提交被 TTL-METADATA 门禁硬阻断（doc_type=implementation_plan 非法，见 Q7），按规则暂存待裁定 |
| 2026-08-18 | 0.2.1 | 一致性回填（依赖文档已填充，纯口径/状态更新，无设计变更）：①§2.3 只读纪律更新——03 号文 v0.2.1、14 号文 v0.3.0 均已填充，接口假设核对完成；②§4.1/§4.4 Phase 2 文档级核对落盘——接口形态一致（薄入口直接组装本包）、新增"治理 Agent→本包"调用矩阵、新发现 14 号文 S0.2 降级路径"组装包级 __all__"依赖本文 Phase 1（当前 __all__ 腐烂不可用）；③§6 状态更新——Q2（03 号文 D5 分析倾向同向，待 Owner 裁定）、Q5（03 号文 D4 倾向①降低迁移可能性）、Q6（已核对）、Q7（本文档 doc_type=architecture_view 合规，已于 2026-08-17 补提交 a65a8b8a 收口；目录级 doc_type 统一裁定移交 14 号文 Q7）；实测复核：25 个 .py、`__init__.py` 零 import、包外 12 消费文件、02 号文 Q1 同源、引用文档路径全部存在；④红蓝对抗复测修正 §2.4-E 一处漂移——governance 子目录 29→30（新增 1 个兄弟子目录，本包边界不变） | AI-FILL-05 第 5 轮一致性审查：03/14 号文填充完成后回核接口假设，消除"v0.1.0 空骨架"过期口径；红蓝对抗验证全部通过（import 扫描 17 行命中复核 12 消费文件清单与 §2.4-B 完全一致；3,223 行总数复测一致） |
| 2026-08-18 | 0.2.2 | Owner 裁定回填+施工事实登记：①§3.1/Q1 标「已裁定+已施工 2026-08-18」——`__init__.py` 已修复为 PEP 562 惰性外观（`__all__` 42 个真实符号，剔除 6 幻影名与双义 DebateRound），契约测试 `tests/governance/test_intelligence_governance_facade.py` 4 项，28 个消费方测试文件 570 测试全绿（AI-ADJ-001，commit 8efacc2c70），形式=修复为惰性外观非新建 facade，与裁定一致；②Q2 按裁定 2 关闭——03 号文 D5 裁定：D_ORCHESTRATOR=任务/阶段确定性流转+Agent 生命周期基础设施，≠Agent 自治编排；③Q5 按裁定 2 的 D4 关闭——整包维持 D_GOVERNANCE+横切标签，不迁域不新建子域，文件级迁出不执行；④Q6/§4.4 降级路径口径更新——包级 `__all__` 已修复可用，"须用子模块路径导入"临时口径作废（子模块路径导入仍是合法惯例但不再是唯一选择） | 裁定 1（包入口已修复）+ 裁定 2（D4/D5 域边界）；AI-ADJ-004 回填 |
| 2026-08-30 | 0.2.3 | GP1 收尾回写（纯文档+头注释纠偏，零业务代码改动）：①头部结案报告消除与 §3.1/§6 Q1 的自相矛盾——`__init__.py` 入口腐烂已于 2026-08-18 修复（AI-ADJ-001），"待 Q1 裁定"stale 表述作废；②§4.3 Phase 1 第 2 条文件头纠偏施工——delegation_manager/mvep_orchestrator/provider_failover 三文件 `[TESTS]` 改实测路径（tests/infrastructure/test_delegation_manager.py、tests/governance/orchestrator/test_mvep_orchestrator.py、tests/governance/resilience/test_provider_failover.py），`[CONSUMERS]` 按全仓 import 扫描置空（原声明 zephyr.governance.services.adapter/zephyr.orchestrator/zephyr.infrastructure.escalation 均非实测消费方），`[MODIFY-GUARD]` 连字符路径统一为实测存在的 `_domain_autonomy_perm/escalation_protocol`；③Q3 核实关闭——S4 reconciler 只读写 `[BLUEPRINT]`，CONSUMERS-ACCURACY gate warn-only 且 commit-time 不检 stale，META-TESTS-COVERAGE 不覆盖本包目录，漂移无硬阻断影响；④动态终验 tests/governance/test_intelligence_governance_facade.py 4 项全绿 | C2 收尾项：代码早已施工（2026-08-18），本轮回写文档/登记对齐实态 |

---

*维护者：AI 架构协调者*