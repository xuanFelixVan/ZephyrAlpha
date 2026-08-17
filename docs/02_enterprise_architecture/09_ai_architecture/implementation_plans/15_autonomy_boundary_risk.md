---
ttl: permanent
doc_type: architecture_view
title: AI 自治边界与风险施工图
owner: ZephyrAlpha-Owner
language: zh
status: draft
version: "0.2.1"
date: 2026-08-17
topic: autonomy_boundary_risk
scope: 09_ai_architecture
---

# AI 自治边界与风险施工图

> 本文定位：AI 自治边界（ai_modifiable/human_gated/immutable + Agentic Drift 防护 + 自治熔断）和 Agent 风险治理（有界自治5级 + OWASP + Kill Switch + ARS 双轨）的施工。
> 与其他文件的分工：结构设计见 [00_index.md](00_index.md)，对标见 [01_external_benchmark_analysis.md](01_external_benchmark_analysis.md)。

---

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | AI 自治边界与风险 |
| 所属 | [00_index.md](00_index.md) §1 目标架构·横切层 |
| 依赖 | 61 号备忘（生命周期多 AI，`../../07_trading_decision_architecture/design_memos/61_lifecycle_multi_ai.md`，只读）+ 系统宪章约束六 |
| 优先级 | P0——AI 自治边界是所有 AI 能力的安全前提 |
| 状态 | draft（已填充 v0.2.1） |

---

## 2. 背景

### 2.1 项目处境

ZephyrAlpha 是个人 + 100% AI 生成代码的 A 股量化交易系统（miniQMT 通道，T+1，不能做空）。AI 层规划了自我进化层（画像→考试→护照、Context Engine、技能路由、自反 Agent、模块工厂）与执行层（治理/业务/算法/自我迭代 Agent）。当 AI 既是代码的唯一生产者、又逐步获得运行时行为能力时，"AI 能改什么、不能改什么、行为跑偏怎么发现、出事怎么停"就成为全部 AI 能力的安全前提——这正是本文档覆盖的横切层。

当前实现状态（实测，详见 §2.4）：

1. **三分类权限体系已有权威真源，但停在"登记层"**。`ai_autonomy_authority_registry.yaml`（GOV-AI-001 v1.4.0，active）已定义 Immutable Core / Human-Gated / AI-Modifiable 三层权限并覆盖全模块；`ai_autonomy_vocabulary.yaml`（PS-VOC-012）与 `ai_autonomy_level_planned_vocabulary.yaml`（PS-VOC-021）提供受控词表；源码文件头普遍带 `[AI_AUTONOMY]` 锚定。**缺的是运行时判定链路**：写操作发生前没有统一的 gate 去查注册表并拦截越权写入，三分类目前主要靠 AI 自律 + pre-commit 静态检查。
2. **自治治理组件已存在 6 个，但分散在 5 个域、语义未统一**。`autonomy_credit.py`（信任衰减，R87）、`autonomy_maturity.py`（成熟度阶梯，R86）、`autonomy_guard.py`（Owner 缺位分级自治）、`autonomy_regressor.py`（自治级别回归）、`autonomy_dashboard.py`（健康度降级，exit 35）、`autonomy_monitor.py`（自治监控）各自实现了 00_index §3.2「有界自治」的某个切片，但等级标尺三套并存（详见 §2.2 问题三）。
3. **Kill Switch 已有 5 套实现 + 1 个仿真器，但没有统一编排**。系统级（`security/access_control/kill_switch.py`，MOD-INF-018，human_gated）、交易级（`trading_kill_switch.py`，MOD-INF-016，五级）、回滚级（`infrastructure/rollback/kill_switch.py`，MOD-INF-021，L1/L2/L3 递进）、技能级（`skill_kill_switch.py`，MOD-INF-019）、容量保障级（`capacity_assurance/kill_switch.py`），外加 `kill_switch_sim.py` 仿真。各套独立触发、独立复位，缺"谁优先、谁兜底、多路径触发怎么收敛"的编排设计。
4. **漂移检测能力偏"代码/治理漂移"，Agent 行为漂移只有设计没有落地**。`gov_drift` 域已有 74 个 Python 模块（baseline_manager / drift_engine / cascade_detector / spiral_ews / reward_hacking_rebound_detector / silence_detector / tamper_proof_audit 等），但检测对象是仓库 artifact、治理规则、奖励黑客反弹；面向 Agent 操作链的意图漂移（Context Drift）只在 `agent_role_based_access_control` 蓝图（决策 D-018-21）中有设计，代码未施工。
5. **ARS 双轨结算仅有设计口径**。00_index §3.2 登记了「Fee+Principal 双轨防自利」，全仓检索未发现对应实现模块；检测侧可复用 `gov_drift/reward_hacking_rebound_detector.py`。
6. **依赖文档状态**：14_execution_layer.md、09_llm_security_integration.md、16_ai_security_ops.md 当前均为 v0.1.0 空骨架（2026-08-17 实测），本文按"如已填充"降级处理——接口假设记入 §6 开放问题 Q4，不等待不阻塞。
### 2.2 核心问题

**问题一：三分类如何落地为"每次写操作前的运行时判定"？**
注册表（GOV-AI-001）+ 文件头锚定（`[AI_AUTONOMY]`）+ 受控词表（PS-VOC-012）三件套解决了"权限信息在哪"，但没解决"谁在写入前强制执行"。AI 自律在多会话并发施工（08 号文场景）下不可靠——61 号备忘明确多 AI 协作=人调度多会话，每个会话的 AI 不一定知道全量权限约定。需要一条"写操作 → 查注册表 → 判定放行/拦截/升级人工"的代码路径。

**问题二：Agentic Drift（Agent 行为漂移）如何检测？**
00_index §3.1 定了四件套：双维度阈值 + Hard-Gate + 行为基线 + Agent Challenge。落地要回答：①行为基线用什么数据建（Agent 操作日志？工具调用序列？）；②双维度是哪两个维度（候选：置信度 × 意图偏差度）；③Hard-Gate 卡住哪些不可谈判动作；④Agent Challenge 以什么形式让 Agent 自证未漂移（开放问题 Q2）。现有 gov_drift 设施检测的是代码库漂移，不能直接回答"这个 Agent 的行为序列偏离了它的任务意图"。

**问题三：三套自治等级标尺并存，如何统一？**
实测发现三套语义不同的等级体系：

| 标尺 | 出处 | 等级 | 语义 |
|---|---|---|---|
| PS-VOC-021 词表 | `ai_autonomy_level_planned_vocabulary.yaml` | l0~l3（4 值） | 模块"规划期望"的自治等级（l0 无自治→l3 全权自主） |
| AutonomyMaturity | `feedback_loop/gates/autonomy_maturity.py` | L0~L4（5 级） | 运行时信任阶梯（OBSERVE/NOTIFY/SUGGEST/AUTO_MINOR/AUTO_FULL） |
| AutonomyGuard | `orchestrator/governance/autonomy_guard.py` | level1~3（3 级） | Owner 缺位时的运维动作白名单（健康检查→自动缓解→回滚） |

另有 `autonomy_regressor.py` 的 `autonomous/auto_guard/blocked` 三态（行为态，非等级）。00_index §3.2 的「有界自治 5 级：L0 人工→L1 建议→L2 低风险→L3 中风险」是第 4 种口径。不统一会导致：模块工厂（13 号文）给新模块定级时无所适从，Drift 检测的"降级"动作不知道降到哪一档。统一方案需人裁定（开放问题 Q3），本文只给候选映射。

**问题四：Kill Switch 如何触发、如何收敛、延迟是否够用？**
00_index §3.2 定了多路径：AI 自动(<1ms) / 人工一键(<100ms) / 定时熔断(<1ms) / 外部信号。两个现实问题：①"<1ms"在 Windows+Python 用户态做不到内核级响应（开放问题 Q1），需要软件级等效方案并实测延迟；②5 套 Kill Switch 并存，全局事故时该拉哪一个、拉错会不会只停了次要回路而主回路还在跑——需要两级编排（系统级总开关 + 域级分开关）。

### 2.3 约束条件

以 [system_charter.md §2 硬边界约束](../../04_architecture_principles_decisions/system_charter.md) 为唯一判定基准，与本文直接相关的：

| 约束 | 对本文设计的影响 |
|---|---|
| 约束一（1 人全栈+AI 协作，代码 100% AI 生成） | 人不可能逐行审查 AI 产出 → 三分类必须机器可判定，不能靠人盯 |
| 约束二（单机 PC：i7-12700KF / RTX 3090 / 64GB RAM / 30Mbps） | Drift 检测走日频/周频批量，不做实时全量语义检测；不引入集群级控制面 |
| 约束四（T+1、涨跌停、日频及以上根频率） | 交易侧 Kill Switch 的"<1ms"压力本就有限——Tick=3 秒，决策点拦截等效即可 |
| 约束五（单机部署无热备，RTO<5分钟） | Kill Switch 触发后恢复流程必须简单（文件标志位 + 人工复位），不要复杂状态机 |
| 约束六（AI 自治熔断：亏损超限/置信度低 → 降级"仅建议"模式） | 本文的自治降级链路（regressor/dashboard/credit）就是约束六的工程化 |
| 施工方式（多 AI 多会话并发） | 权限判定不能依赖单会话 AI 的上下文记忆，必须外置注册表 |

**关于"<1ms 自动触发"的可行性边界**：Windows 用户态 + Python 进程内检查的典型延迟为微秒级（同进程函数调用），但跨进程/跨会话信号（文件标志位轮询）在 Windows 上实测为 10ms~1s 量级。"AI 自动 <1ms"只能理解为**决策点内联拦截**（下单/写文件前的同步检查，等效 0 延迟），不能理解为"外部信号 1ms 内传遍全系统"。Phase 0 将做延迟实测并把结果写回本节。
### 2.4 已施工设施盘点

> 全部路径已于 2026-08-17 实测存在（LS/Grep/Read 验证）。"状态"指文件头 `[MATURITY]` 锚定或注册表 status。

**A. 权限真源与词表（登记层）**

| 类别 | 路径/位置 | 内容简述 | 状态 |
|---|---|---|---|
| 注册表 | `docs/01_policies_and_standards/_registry/catalogs/ai_autonomy_authority_registry.yaml` | GOV-AI-001 v1.4.0：全模块三层权限（Immutable Core / Human-Gated / AI-Modifiable）唯一真源 | active |
| 受控词表 | `docs/01_policies_and_standards/_registry/vocabularies/ai_autonomy_vocabulary.yaml` | PS-VOC-012：`ai_autonomy` 字段 3 个合法值（immutable_core/human_gated/ai_modifiable） | active |
| 受控词表 | `docs/01_policies_and_standards/_registry/vocabularies/ai_autonomy_level_planned_vocabulary.yaml` | PS-VOC-021：`ai_autonomy_level_planned` 4 个合法值（l0~l3） | active |
| 文件头锚定 | 全仓源码 `[AI_AUTONOMY]` 标记 | 每个模块文件头标注自治权限（如 `ai_modifiable`、`human_gated`） | production（随文件） |
| 校验脚本 | `scripts/governance/d5_architecture/validators/validate_autonomy_gate.py` | D5 架构层自治门校验器 | production |

**B. 自治治理组件（运行时，6 个）**

| 类别 | 路径/位置 | 内容简述 | 状态 |
|---|---|---|---|
| 信任衰减 | `src/zephyr/feedback_loop/gates/autonomy_credit.py` | AutonomyCredit：score=100 起步、decay_per_day=1.0，信任随时间衰减需重新赢得（盲点 R87） | production |
| 成熟度阶梯 | `src/zephyr/feedback_loop/gates/autonomy_maturity.py` | AutonomyMaturity：L0 OBSERVE→L4 AUTO_FULL 渐进信任模型（盲点 R86） | production |
| 缺位分级自治 | `src/zephyr/orchestrator/governance/autonomy_guard.py` | AutonomyGuard：Owner 离线时 level1/2/3 运维动作白名单（CT-AUTONOMY） | production |
| 自治回归器 | `src/zephyr/gov_drift/autonomy_regressor.py` | AutonomyRegressor：confidence<0.3 或 error>5 时 autonomous→auto_guard→blocked 逐级回归；不变量"回归触发器不可禁用" | production |
| 自治仪表盘 | `src/zephyr/governance/intelligence_governance/autonomy_dashboard.py` | health<0.3 持续 5 分钟 → autonomy_downgrade + exit 35 + Owner 通知（对标 Autopilot 接管） | production |
| 自治监控 | `src/zephyr/shared/maintenance/autonomy_monitor.py` | 自治状态监控（维护域） | production |
| 离线自治 | `src/zephyr/governance/resilience_governance/offline_autonomy.py`、`src/zephyr/infrastructure/a2a_protocol/offline_autonomy.py` | 离线场景的降级自治（两处实现） | production |

**C. Kill Switch（5 套 + 1 仿真）**

| 类别 | 路径/位置 | 内容简述 | 状态 |
|---|---|---|---|
| 系统级总开关 | `src/zephyr/security/access_control/kill_switch.py` | MOD-INF-018：NORMAL/TRIPPED/RESET_PENDING/COOLDOWN 四态；支持单 Agent 阻断+全局熔断；复位需 Owner 批准；safety=H、human_gated | production |
| 交易风险熔断 | `src/zephyr/trading/trading_contracts/risk/trading_kill_switch.py` | MOD-INF-016：五级（POSITION_LIMIT/DAILY_LOSS/CIRCUIT_BREAKER/SECOND_LEVEL/API_TIMEOUT）；日亏>3% AUM → 撤全部挂单+禁新单、冷却 86400s；human_gated | production |
| 回滚三级开关 | `src/zephyr/infrastructure/rollback/kill_switch.py` | MOD-INF-021：L1 Session Kill→L2 Skill Kill→L3 Global Kill 递进升级，L3 仅 token-gated | production |
| 技能熔断 | `src/zephyr/autonomy_core/skills/skill_kill_switch.py` | MOD-INF-019：Skill 失败 3 次熔断、冷却 300s、可 revive | production |
| 容量保障开关 | `src/zephyr/infrastructure/capacity_assurance/kill_switch.py` | 容量保障域熔断 | production |
| 熔断仿真器 | `src/zephyr/infrastructure/kill_switch_sim.py` | Kill Switch 行为仿真（测试/演练用） | production |

**D. 漂移检测（gov_drift 域，74 个 Python 模块，摘相关者）**

| 类别 | 路径/位置 | 内容简述 | 状态 |
|---|---|---|---|
| 基线管理 | `src/zephyr/gov_drift/baseline_manager.py` | 治理基线建立/更新（可复用为 Agent 行为基线地基） | production |
| 漂移引擎 | `src/zephyr/gov_drift/drift_engine.py`、`drift_detector.py`、`drift_models.py` | 仓库 artifact 漂移检测主链路 | production |
| 级联故障检测 | `src/zephyr/gov_drift/cascade_detector.py` | 级联故障（OWASP ASI05 对应能力） | production |
| 螺旋预警 | `src/zephyr/gov_drift/spiral_ews.py` | 恶化螺旋早期预警 | production |
| 奖励黑客反弹 | `src/zephyr/gov_drift/reward_hacking_rebound_detector.py` | 奖励黑客行为反弹检测（ARS 检测侧可复用） | production |
| 静默检测 | `src/zephyr/gov_drift/silence_detector.py` | 该报不报=异常的检测 | production |
| 防篡改审计 | `src/zephyr/gov_drift/tamper_proof_audit.py` | 审计链防篡改 | production |
| 值守运行时 | `src/zephyr/gov_drift/vigil_runtime.py` | 持续值守扫描运行时 | production |
| 基线投毒防护 | `src/zephyr/gov_drift/baseline_poisoning_guard.py` | 防行为基线被投毒 | production |

**E. 蓝图与设计（docs/03_modules，只读引用）**

| 类别 | 路径/位置 | 内容简述 | 状态 |
|---|---|---|---|
| RBAC 蓝图 | `docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md` | MOD-INF-018 域蓝图：L2 ABAC 意图绑定（drift_tolerance=0.3）、Context Drift 检测设计（决策 D-018-21：10 步操作链、类型熵>1.5、路径熵>2.0、DRIFT_WARNING→auto_guard、DRIFT_DETECTED→blocked+P0） | 设计完成 |
| 回滚系统蓝图 | `docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md` | MOD-INF-021：Kill Switch 三级递进设计依据 | 设计完成 |
| 升级协议蓝图 | `docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md` | MOD-INF-022：regressor/dashboard 的设计依据（渐进自治可逆性） | 设计完成 |

**F. 测试**

| 类别 | 路径/位置 | 内容简述 | 状态 |
|---|---|---|---|
| 自治边界专项 | `tests/autonomy/test_autonomy_{credit,dashboard,guard,maturity,monitor,regressor}.py` | 6 个专项测试文件 | production |
| Kill Switch RBAC | `tests/agent_rbac/test_kill_switch_agent_rbac.py` | 系统级 KillSwitch + RBAC 集成测试 | production |
| 回滚测试 | `tests/rollback/`（34 个测试文件） | 回滚域（含三级 Kill）测试目录 | production |
| 自治域大套件 | `tests/autonomy/`（共 71 个测试文件） | autonomy_core 全量测试 | production |

**G. 自治核心域（相邻设施，非本文施工对象）**

`src/zephyr/autonomy_core/` 共 113 个 Python 模块（其中 `skills/` 58 个），含 `skill_rbac_registry.py`（技能 RBAC 注册表）、`skill_guardrails.py`、`self_evolution_fidelity_gate.py`、`agent_observability.py` 等。本文复用其注册表与护栏，不改动它们（属 04/11/13 号文施工范围）。
---

## 3. 设计决策

### 3.1 三分类边界（ai_modifiable / human_gated / immutable）的 why

**为什么是三分类而不是两分类（可改/不可改）？**
两分类把全部流量挤向两端：要么 AI 放开改（风险不可控），要么人逐个批（1 人力根本批不过来——约束一）。human_gated 中间层承担的是"效率与安全的折中"：AI 完成 90% 的工作（分析、提议、生成 diff），人只做 10% 的点头动作。实测仓内现状也证明三层有必要——系统级 KillSwitch（safety=H）标 human_gated、交易熔断标 human_gated、大量 skills 标 ai_modifiable，真实分布就是三层。指令块第 6 轮之问"两分类是否足够"的答案：**不足够，三分类保留**。

**为什么真源必须是注册表（GOV-AI-001）而不是文件头或目录约定？**
该注册表的 provenance 记录了根因：前三轮审计在 8 份文档中各自标注权限，导致 25-30% 错误率——"没有横向汇总"是病根。因此决策：**注册表是唯一真源，文件头 `[AI_AUTONOMY]` 锚定是注册表的投影（便于 AI 读文件时即时感知），运行时 gate 判定以注册表为准**。三者关系是"真源→投影→执行"，禁止反向同步。这与 00_index §3.1「三分类：设计完成」的口径一致——设计已定稿，本文负责施工落地。

**落地链路的关键决策**：写操作前的判定必须外置（注册表查询），不能依赖会话内 AI 的自觉。施工方式（多 AI 多会话并发）决定了任何"我以为这个文件能改"的判断都不可靠；`agent_role_based_access_control` 蓝图已有同思路先例（derive_rbac_roles.py 从 GOV-AI-001 自动派生 RBAC 角色，"消除手动复制漂移"）——本文的运行时 gate 复用同一"注册表自动派生"模式。

**考虑过的替代方案**：

| 方案 | 取舍 | 结论 |
|---|---|---|
| 两分类（可改/不可改） | 简单但人工流量爆炸，约束一不满足 | 拒绝 |
| 基于目录路径的权限（如 config/ 一律 human_gated） | 实现简单，但权限是模块语义而非位置语义；仓内已有 `docs/03_modules/path_ownership_map.yaml` 管归属，权限另有一层 | 拒绝（路径归属≠权限分级，两者正交） |
| Git pre-commit 静态检查兜底 | 已有（gov_enforcement commit_gates），但只在提交时点生效，管不住工作区内 AI 写文件 | 保留为补充，不作为主链路 |

### 3.2 Agentic Drift 防护的 why（双维度阈值 + Hard-Gate + 行为基线 + Agent Challenge）

**为什么 Drift 是 P0 风险？**
Agent 在长操作链中的意图漂移是最隐蔽的越权形式——RBAC 蓝图决策 D-018-21 引用的企业研究表明"授权边界随操作链漂移"（从"修一个 Bug"渐变到"重构整个模块"）。2026 年 1 月 arXiv:2601.04170 进一步把 Agent Drift 形式化为三类（语义漂移/协作漂移/行为漂移）并提出 12 维 Agent Stability Index。对本项目，漂移的直接后果是：AI 在 ai_modifiable 文件上做着做着越界到 human_gated 文件，或交易策略代码在自我迭代中偏离原始意图——两者都触发资金风险。

**四件套各自解决什么（为什么缺一不可）**：

| 组件 | 解决的失效模式 | 本项目地基 |
|---|---|---|
| 双维度阈值 | 单维度（只看置信度或只看偏差）误报/漏报二选一；置信度 × 意图偏差度两个正交维度可把"低置信但守规矩"与"高置信但跑偏"分开处置 | `autonomy_regressor.py` 已用 confidence 单维；意图偏差度见下行 |
| Hard-Gate | 有些动作不可谈判（删 immutable_core 文件、改交易熔断参数、绕过 GitCommitGateway）——不管置信度多高都物理拦截 | `security/access_control/kill_switch.py` 的 human_gated 语义 + commit_gates 模式 |
| 行为基线 | "异常"需要参照系；没有基线，漂移检测只能靠拍脑袋阈值 | `gov_drift/baseline_manager.py` + `baseline_poisoning_guard.py`（防基线投毒） |
| Agent Challenge | 检测器判"像漂移"不等于真漂移；让 Agent 自证（复述原始任务意图并对齐当前动作）可把判定成本转移给被检测方，降低误报停工 | 无现成实现——实现方式待定（开放问题 Q2） |

**为什么是"日频/周频批量 + 关键操作实时 Hard-Gate"的混合，而不是全量实时？**
约束二（单机）+ 约束五（无热备）。全量实时语义检测（每步操作都算嵌入相似度）在单机 RTX 3090 上要跟交易/回测抢显存，不可行；且本项目 Agent 操作主要是施工期写代码（分钟级粒度），不是高频交易（Tick=3 秒已由交易熔断兜底）。RBAC 蓝图 L2 ABAC 已给出实时档的性能预算参考（L2 ABAC+TLB+Drift ≈0.25ms，针对操作链内联检查）——实时档只覆盖 Hard-Gate 与操作链内联漂移检查（drift_tolerance=0.3、10 步窗口、类型熵>1.5、路径熵>2.0），深度语义复核放批量档。

**考虑过的替代方案**（含 2026 前沿登记，不替换已定决策）：

| 方案 | 来源 | 取舍 | 结论 |
|---|---|---|---|
| Agent Stability Index（ASI）12 维复合指标 | arXiv:2601.04170（2026-01） | 维度全、可量化；但 12 维对单机单人过重，且多 Agent 协作维度本项目暂不适用（61 号备忘：不做 agent 编排） | 登记为前沿演进方向：批量档可借鉴其"语义/行为"二分与 episodic memory consolidation |
| Turn budget + 成本熔断（25 轮上限、会话级成本断路器） | MLflow 2026 生产监控指南（2026-06） | 简单有效防"规划死循环"；但面向运行时 Agent 会话，本项目施工期 AI 会话由人调度，轮次预算意义有限 | 登记为前沿演进方向：14 号文执行层 Agent 上线后引入 |
| OPA Rego / Cedar 策略内核（亚毫秒判定） | Microsoft Agent Governance Toolkit（2026-04） | 亚毫秒策略判定、形式化审计；但引入外部策略引擎+新语言，对 1 人维护是过重依赖 | 拒绝（约束一/二）：用 Python 内联检查达到等效"决策点拦截" |
| 纯统计阈值（无语义维度） | — | 实现最简，但"意图偏差"本质是语义问题，统计特征抓不住 | 拒绝 |

### 3.3 有界自治 5 级设计（L0 人工→L3 中风险）的 why

**为什么自治必须是阶梯而不是开关？**
00_index §3.2 定「有界自治 5 级：L0 人工 → L1 建议 → L2 低风险 → L3 中风险」。阶梯的 why 根植于约束一：代码 100% AI 生成，人对 AI 的信任只能**用证据逐段购买**，不能一次性授予——`autonomy_maturity.py`（R86）与 `autonomy_credit.py`（R87，score=100 起步、decay_per_day=1.0）已把"信任随时间衰减、需持续重新赢得"工程化。开关式自治（要么全人工要么全自动）在本项目等于永远全人工——没有 AI 能活到证明自己配得全自动的那天，自我进化层全部落空。等级序列的存在让"放权"本身变成可验证、可回退的施工对象：每一级的解锁条件（信任分阈值 + 连续无事故天数 + 人签）都是 gate，回退由 `autonomy_regressor.py`（confidence<0.3 或 error>5 → autonomous→auto_guard→blocked）机械执行。

**为什么 L3 是可操作上限、L4 档保留不启用？**
等级框架为 5 级刻度（L0~L4），本文施工范围只覆盖 L0~L3 可操作档，L4（高自治）保留不启用（§5 第 1 条）。依据：①约束五——单机无热备 RTO<5 分钟，L4 级"高风险动作自动执行"一旦出错，恢复成本超出 1 人运维能力；②13 号文同款裁定"Phase 2 保留人工审核，零审核=自杀"；③00_index §3.2 列举的等级语义止于 L3 中风险。

**指令块第 6 轮之问"3 级是否足够"的答案：不足够，5 级框架保留。** 3 级（人工/建议/自动）把"自动"压成一档，后果二选一：低风险动作（改 ai_modifiable 文档、跑已登记脚本）也被迫走人工 → 约束一人工流量爆炸；或中风险动作（改 human_gated 配置）混入自动档 → 风险敞口。L2/L3 拆分正是效率与安全的分界。且刻度成本≈零——PS-VOC-021 词表（l0~l3）已存在，无需新建基础设施。

**三套既有标尺的候选映射**（§2.2 问题三承诺，统一裁定待 Q3，本节只给候选不拍板）：

| 00_index 有界自治（可操作档） | PS-VOC-021 规划级 | AutonomyMaturity 运行时信任 | 语义对齐点 |
|---|---|---|---|
| L0 人工 | l0（无自治） | L0 OBSERVE | 只观察记录，不产动作 |
| L1 建议 | l1 | L1 NOTIFY / L2 SUGGEST | 产建议，人决策人执行 |
| L2 低风险 | l2 | L3 AUTO_MINOR | 低风险动作自动，留痕可回滚 |
| L3 中风险 | l3（全权自主→本项目封顶为中风险语义） | L4 AUTO_FULL（本项目不启用，L3 内仍带熔断兜底） | 中风险自动 + regressor 回归兜底 |

映射的两个已知张力（入 Q3）：①PS-VOC-021 的 l3 语义是"全权自主"，比 00_index L3"中风险"更激进，统一时需明确 l3 封顶语义；②AutonomyMaturity 是 5 档（L0~L4）而可操作档只有 4 档，L1 建议对应 NOTIFY+SUGGEST 两档还是单档需裁定。AutonomyGuard 的 level1~3 是正交维度（Owner 缺位时的运维动作白名单，非信任阶梯），不纳入映射、保持不变。

**与 14 号文的现况对齐**：14_execution_layer.md v0.2.0 已定四类 Agent 入口全部"手动触发 + human_gated 产出"起步——按本表即 L0/L1 档。这是正确的 Phase 0 姿态：所有 Agent 从 L0/L1 开始攒信任，升级走 §4 Phase 2 的逐级解锁验证。

### 3.4 Kill Switch 设计的 why（多路径触发 + 两级编排）

**为什么是多路径？**
00_index §3.2 定四条触发路径：AI 自动 / 人工一键 / 定时熔断 / 外部信号。多路径的 why 是停车维度的纵深防御——每条路径覆盖前一条的失效模式：AI 自动路径依赖检测器活着且正确（检测器本身可能被漂移绕过）；人工一键依赖人在场且知情（Owner 可能离线，`autonomy_guard.py` 处理的就是缺位场景）；定时熔断（冷却/额度耗尽自动触发）兜底"检测器与人都失效"；外部信号（券商端断连、监控告警）覆盖系统内视角盲区。单路径=把"停车"这一最后防线押在单一假设上。

**"<1ms"的工程语义**：按 §2.3 的可行性边界，"AI 自动 <1ms"落地为**决策点内联拦截**——下单/写文件/注册表变更前的同步检查，与被拦截动作同进程同线程，等效零附加延迟；不承诺"外部信号 1ms 传遍全系统"（Windows 文件标志位轮询实测 10ms~1s 量级，Phase 0 S0.4 实测后写回 §2.3）。约束四给了这个重新解读的底气：Tick=3 秒、miniQMT 10 笔/秒，决策点拦截的时间预算本就宽裕。

**两级编排的 why（§2.2 问题四"拉哪一个"的答案）**：
- **系统级总开关 = `security/access_control/kill_switch.py`（VR-009，MOD-INF-018）**。选它而不是新建总线式开关的依据：它已是四态状态机（NORMAL/TRIPPED/RESET_PENDING/COOLDOWN）+ 全局熔断与单 Agent 阻断双粒度 + 复位需 Owner 批准 + human_gated + 5 条件触发（Agent 越界/模型漂移 PSI/自治等级跳变/资源消耗/连续否决），语义最全且经 `tests/agent_rbac/test_kill_switch_agent_rbac.py` 集成测试验证。
- **域级分开关保留既有 4 套**（交易五级 / 回滚三级 / 技能熔断 / 容量保障），各自域内自治。不压平的理由：交易熔断的五级语义（POSITION_LIMIT→API_TIMEOUT）携带域知识（如"日亏>3% AUM→撤全部挂单+冷却 86400s"），压平成统一接口反而丢失语义。
- **收敛规则**（编排器的全部职责，只做路由不做重写）：①影响资金 → 先交易级、系统级兜底；②影响代码库/会话 → 系统级；③域内故障 → 域级先行，升级条件（域级触发后异常持续 / 跨域蔓延）→ 系统级；④全局事故只拉系统级总开关——避免"拉错开关只停次要回路、主回路还在跑"。

**考虑过的替代方案**：

| 方案 | 取舍 | 结论 |
|---|---|---|
| FPGA/内核级 Kill Switch（微秒硬断） | 延迟最极致；但 Windows 用户态无内核路径，且 Tick=3 秒下收益为零 | 拒绝（超约束二硬件边界） |
| 新建统一总线式 Kill Switch 替代 5 套 | 架构最"干净"；但重写 5 套 production 组件引入新故障面，违反"不重写已有能力"原则 | 拒绝（用编排器收敛，不重写） |
| 只留系统级一套 | 最简单；但域内故障直接全局熔断=误伤面过大（技能失败 3 次就停全系统） | 拒绝（域级吸收局部故障，系统级只做兜底） |

### 3.5 ARS 双轨设计的 why（Fee + Principal 双轨防自利）

**问题本质：自利行为的结算通道。**
Agent 若能通过自身动作直接影响自己的"收益结算"，优化目标就会从"让系统受益"滑向"让自己得分"（Goodhart 定律在 Agent 场景的投影）。ARS 双轨结算（候选登记 MOD-RISK-141，源设计「风险架构.md」§15.5）把结算物理拆成两轨：**Fee 轨**——Agent 的报酬/计分/信任积累，托管式、延迟结算、可追回；**Principal 轨**——本金/资产/权限本体，Agent 永不可触。双轨隔离后，Agent 的任何动作只能影响 Principal 的盈亏，Fee 由人（或人授权的审计流程）事后按审计记录结算——自利行为没有结算通道，动机在机制上被消除而非靠自觉。

**为什么是双轨而不是单轨+审计？**
单轨+审计是事后发现：自利行为发生时收益已结算、已再投入，追回成本随时间指数上升。双轨是事前机制：结算通道根本不存在，行为不发生。对 1 人项目，"不需要盯"比"盯得住"重要一个数量级（约束一）。

**本项目的双形态落地**：

| 形态 | Fee 轨 | Principal 轨 | 执行载体 | 状态 |
|---|---|---|---|---|
| 施工期（当前，AI 会话产出结算） | 会话产出被接受（commit 生效） | 代码库/文档库/注册表本体 | 61 号备忘 BM-RC-09 已裁定快轨/慢轨：白名单内+额度内+gate 全过 → 快轨自治结算；其余 → 慢轨人工审批，审批前不落分支。GitCommitGateway（GATE-COMMIT-GW 硬阻断裸 commit）即双轨的执行载体 | production |
| 运行期（执行层 Agent 上线后，远期） | Agent 信任分/计分（autonomy_credit 承载） | 资金账户与交易权限本体（交易决策侧 30 号文 firm 层风控管辖，本文不碰） | 仅有设计口径，实现排 Phase 2+（§4） | 设计完成，未施工 |

**检测侧配套**：`gov_drift/reward_hacking_rebound_detector.py` 复用为"Fee 轨被博弈"的检测器（奖励黑客行为反弹=Agent 找到计分规则的 exploit）；`silence_detector.py` 检测"该报不报"（隐藏亏损以保信任分）。检测是双轨的补充而非替代——机制防"能自利"，检测防"钻机制空子"。

**考虑过的替代方案**（含指令块第 6 轮之问"单轨是否足够"）：

| 方案 | 取舍 | 结论 |
|---|---|---|
| 单轨+审计 | 实现最简；但事后追回不可靠，约束一下盯不住 | 拒绝 |
| 完全无结算（Agent 无激励信号） | 无自利动机；但自我进化层（11/12/13 号文）以信任分/证据为优化目标，无信号=无进化 | 拒绝（Fee 轨保留激励，Principal 轨隔离风险） |
| 施工期也上 Fee/Principal 金融级托管 | 过度工程：施工期"本金"是代码库，Git 版本锁定+慢轨审批已等效托管 | 拒绝（施工期维持 61 号裁定形态） |

---

## 4. 施工计划

> depgraph L1 铁律：凡新建模块，第一步用 `scripts/governance/apply_depgraph.py --add-design-node` 登记设计态（status=planned），验证通过后最后一步 `--transition-design-maturity` 转正 production。禁止先施工后补登记。

### 4.1 Phase 0（P0）：运行时权限 gate + Kill Switch 两级编排 + 延迟实测

**步骤 S0.1：depgraph 设计态登记**
- 为两个新建模块登记设计态节点（status=planned）：①运行时三分类判定 gate（写操作前查 GOV-AI-001 注册表，判定放行/拦截/升级人工）；②Kill Switch 两级编排器（路由+收敛规则，不重写既有 5 套）。声明依赖：gate → `ai_autonomy_authority_registry.yaml` + PS-VOC-012 词表 + `derive_rbac_roles.py` 派生模式；编排器 → 5 套既有 Kill Switch + `kill_switch_sim.py`。
- 验收：apply_depgraph 查询可见 2 个 planned 节点且依赖边完整。
- 注：worktree 会话内只登记不流转，merge 回 dev 后随第一次重建自动转 production（与 14 号文 S0.1 同款分流纪律）。

**步骤 S0.2：运行时三分类 gate 施工（P0-1）**
- 判定链路：写操作（文件写入/注册表变更/配置修改）→ 查 GOV-AI-001 → ai_modifiable 放行 / human_gated 升级人工 / immutable_core 物理拦截。注册表查询失败或目标未登记时 fail-closed（默认按 human_gated 处理）。
- 复用 `derive_rbac_roles.py` 的"注册表自动派生"模式（消除手动复制漂移）；文件头 `[AI_AUTONOMY]` 锚定仅作投影提示，判定以注册表为准（§3.1 真源决策）。
- 与既有 commit_gates 的关系：commit_gates 管提交时点，本 gate 管工作区内写操作时点，两层互补不替代。
- 验收：①对 human_gated 样例文件的写操作被拦截并留痕（审计落盘）；②对 ai_modifiable 样例放行；③对 immutable_core 样例物理拦截；④注册表不可读时 fail-closed 生效；⑤既有 `validate_autonomy_gate.py` 静态校验不受影响（回归全绿）。

**步骤 S0.3：Kill Switch 两级编排器施工（P0-2）**
- 编排器只做两件事：①按 §3.4 收敛规则路由触发信号（哪条路径/哪个场景拉哪个开关）；②全局事故时统一拉系统级总开关。编排规则落盘为 yaml（人可审可改），5 套既有实现零改动。
- 验收：①用 `kill_switch_sim.py` 仿真三类事故（资金异常/代码库越权/域内故障），各拉到正确开关；②系统级 TRIPPED 时域级开关状态一致性检查通过；③复位仍需 Owner 批准（既有不变量不破）；④编排器自身故障时各开关保持独立可用（编排器是增强不是单点）。

**步骤 S0.4：Kill Switch 延迟实测（P0-3）**
- 实测两组延迟：①决策点内联拦截延迟（同进程同步检查，目标微秒级）；②跨会话文件标志位轮询延迟（Windows 实测，预期 10ms~1s 量级）。实测方法：最小计时脚本，1000 次采样取 P50/P95/P99。
- 验收：延迟数据写回 §2.3 可行性边界段落；若内联拦截 P95 超 1ms 则回头修订 §3.4 的"<1ms"工程语义并记 Q1 结论。

**步骤 S0.5：Phase 0 验证转正**
- S0.2~S0.4 验收全过后，merge 回 dev 实证核验 depgraph 节点 planned→production（worktree 分流路径）或 `--transition-design-maturity` 手动转正（主工作区路径）。

### 4.2 Phase 1（P1）：Agentic Drift 防护落地

**步骤 S1.1：Agent 行为基线建立**
- 复用 `gov_drift/baseline_manager.py` + 61 号备忘 BM-RC-04-F 口径：从 Git 提交历史/会话日志统计基线——操作频率（单会话 commit 次数/小时）、操作类型分布（文档/代码/注册表占比）、涉及模块分布。轻量实现（统计脚本量级，无独立监控服务）；基线投毒防护挂 `baseline_poisoning_guard.py`。
- 验收：对历史数据建基线；注入合成异常（单会话 commit 频率突增 10×、首次触碰从未涉及的 production 模块）能检出并告警。

**步骤 S1.2：操作链内联漂移检查（实时档）**
- 按 RBAC 蓝图决策 D-018-21 的参数落地：drift_tolerance=0.3、10 步操作链窗口、类型熵>1.5、路径熵>2.0；DRIFT_WARNING → 降级 auto_guard（`autonomy_regressor.py` 承载），DRIFT_DETECTED → blocked + P0 告警。内联检查挂在 S0.2 的 gate 链路上，性能预算对齐蓝图 L2 ABAC 参考值（≈0.25ms 量级）。
- 验收：构造渐变操作链样例（read→write→delete 类型漂移、src/→config/ 路径漂移）分别触发 WARNING 与 DETECTED；正常施工链不误报（抽样人审）。

**步骤 S1.3：深度语义复核（批量档，日频/周频）**
- 意图偏差度的语义维度（§3.2 双维度的第二维）走批量：日频/周频对会话操作链做嵌入相似度复核（当前动作 vs 原始任务意图），避开交易时段与 GPU 高峰（约束二）。产出漂移报告落盘，人审。
- 验收：周频跑批产出报告；误报率人审抽样评估后可接受（阈值人定，记 Q2 关联）。

### 4.3 Phase 2（P2，远期候选）：Agent Challenge + 有界自治逐级解锁 + ARS 运行期双轨

> 本 Phase 启动以 Q2/Q3 裁定为前提，属远期工程，不展开细排。

- Agent Challenge：实现形式待 Q2 裁定（候选：challenge 工单——要求被检测 Agent 复述原始任务意图并对当前动作链做对齐说明，人审或交叉会话复审）。
- 有界自治逐级解锁验证：L0/L1 → L2 → L3 每级解锁条件 = 信任分阈值（autonomy_credit）+ 连续无事故天数 + 人签；降级由 regressor 机械执行，升级永不自动。
- ARS 运行期 Fee/Principal 隔离：执行层 Agent 上线后启动；Principal 轨归交易决策侧 firm 层风控（30 号文），本文只做 Fee 轨（信任分/计分）与检测侧（reward_hacking_rebound_detector）对接。

### 4.4 与其他文档的接口

- **与 [14_execution_layer.md](14_execution_layer.md)（已填充 v0.2.0）**：四类 Agent 入口的自治边界标记 = 全部 L0/L1 起步（手动触发 + human_gated 产出），升级走 §4.3 逐级解锁。14 号文 Q5（执行层 Agent 自治等级划分待 15 号文对齐）的答复即此口径——本文 §3.3 候选映射表为其提供刻度。
- **与 [09_llm_security_integration.md](09_llm_security_integration.md)（已填充 v0.2.0）**：边界互补——LSG 守 LLM 请求/响应（检测+阻断+记录），本文 gate 守文件/注册表写入（权限判定）；09 号文 KILLSWITCH 三级响应触发时，本文系统级 Kill Switch（VR-009）是执行载体之一（09 号文 §4.6 已登记"KILLSWITCH 触发 → L5 全量熔断"口径）。
- **与 [16_ai_security_ops.md](16_ai_security_ops.md)（骨架 v0.1.0，接口假设）**：本文产出的风险事件（gate 拦截 / Drift 检出 / Kill Switch 触发）写审计链落盘，16 号文 Detect 环节消费——假设与 09 号文 §4.6 的"L6 事件 → 审计链 → 16 号文 Detect 消费"同一载体。假设入 §6 Q4，待 16 号文填充后核对。
- **与交易决策侧**：只读不改。61 号备忘 BM-RC-09（白名单+额度+快轨慢轨）是施工期双轨的已定裁定；30 号文 firm 层风控是 Principal 轨的资金侧管辖方；55 号告警通道未定型的 interim 载体（会话日志人工审查 + git_guard 审计输出）同样适用于本文告警。

---

## 5. 不做什么

1. **不启用 L4 及以上高自治档**——等级框架保留 5 级刻度但 L4 永不启用，可操作上限 L3（§3.3）；零审核全自动=自杀（13 号文同款裁定）。
2. **不做 FPGA/内核级 Kill Switch**——Windows 用户态无此路径，软件级决策点内联拦截在 Tick=3 秒场景下等效（§3.4 替代方案表）。
3. **不做实时全量语义 Drift 检测**——单机 RTX 3090 不与交易/回测抢显存（约束二）；实时档只做操作链内联检查，深度语义走日频/周频批量（§3.2）。
4. **不重写既有组件**——5 套 Kill Switch、gov_drift 74 模块、6 个自治治理组件一律复用；编排器只做路由收敛，gate 只做注册表判定（§3.4/§4）。
5. **不做 agent 编排系统**——61 号备忘已裁定；多 Agent = 人调度多会话 + 落盘交接，本文全部机制在此边界内。
6. **不做 ARS 运行期自动结算**——施工期维持 61 号快轨/慢轨裁定（不设自动化结算比例指标）；运行期 Fee/Principal 隔离排 Phase 2 远期（§4.3）。
7. **不做复杂的自治状态机**——Kill Switch 复位 = 文件标志位 + Owner 人工批准（约束五 RTO<5 分钟要求恢复流程简单）；信任分+成熟度阶梯既有组合已足够，不新建信誉系统。
8. **不做 OWASP ASI 自动化扫描**——61 号备忘 BM-RC-04-F 已定轻量替代：映射检查表随新会话认领人工过一遍；本文不另建扫描器。

---

## 6. 开放问题

| # | 问题 | 状态 | 说明 |
|---|------|------|------|
| Q1 | Kill Switch "<1ms" 语义与 Windows 实测 | 待实测 | 00_index §3.2 的"<1ms"在 Windows+Python 用户态的可达语义=决策点内联拦截（§2.3/§3.4）。Phase 0 S0.4 实测两组延迟后：①数据写回 §2.3；②若内联拦截 P95 超 1ms，需裁定是否修订 00_index 口径（00_index 只读，本文不改，修订走 00 号文流程） |
| Q2 | Agent Challenge 的实现形式 | 待裁定 | 检测器判"像漂移"后，Agent 以什么形式自证未漂移？候选：①challenge 工单（Agent 复述原始任务意图+当前动作链对齐说明，人审）；②交叉会话复审（另一 AI 会话做对齐判定，人兜底）。裁定后细化 §4.3 Phase 2 |
| Q3 | 三套自治等级标尺的统一方案 | 待裁定 | PS-VOC-021（l0~l3 规划级）/ AutonomyMaturity（L0~L4 运行时信任）/ 00_index 有界自治（L0~L3 可操作档+L4 保留）三套并存（§2.2 问题三）。候选映射见 §3.3，两个已知张力（l3"全权自主"vs L3"中风险"封顶语义；L1 对应 NOTIFY+SUGGEST 单档或双档）需人裁定；裁定结果需同步 00_index §3.2（只读，走 00 号文流程）与 13 号文模块工厂定级口径 |
| Q4 | 依赖文档接口假设核对 | 部分对齐，待 16 号文填充 | ①16_ai_security_ops.md 为 v0.1.0 骨架：本文假设"风险事件（gate 拦截/Drift 检出/Kill Switch 触发）→ 审计链落盘 → 16 号文 Detect 消费"（与 09 号文 §4.6 同载体），待 16 号文填充后核对；②14_execution_layer.md 已填充 v0.2.0：四类 Agent 全部 L0/L1 起步口径已对齐（本文 §3.3/§4.4，即 14 号文 Q5 的答复）；③09_llm_security_integration.md 已填充 v0.2.0：LSG 守请求响应 / 本文 gate 守文件写入的边界已对齐（§4.4） |

---

## 修订记录

| 日期 | 版本 | 变更 | 原因 |
|------|------|------|------|
| 2026-08-17 | 0.1.0 | 骨架建立 | 新建 |
| 2026-08-17 | 0.2.0 | §1 主题组信息 + §2 背景（项目处境/核心问题/约束/已施工设施盘点实测清单）+ §3.1 三分类边界 why + §3.2 Agentic Drift 防护 why | AI-FILL-15 首轮填充（会话中途中断，§3.3~§6 未竟） |
| 2026-08-17 | 0.2.1 | 续写补完：§3.3 有界自治 5 级（含三套标尺候选映射）/ §3.4 Kill Switch（多路径+两级编排）/ §3.5 ARS 双轨（双形态落地）；§4 施工计划（Phase 0 运行时 gate+编排器+延迟实测 / Phase 1 Drift 防护 / Phase 2 远期候选，含 depgraph L1 登记与转正）；§5 不做什么 8 条；§6 开放问题 Q1~Q4；新增修订记录节。红蓝对抗修正 2 处：§2.4 F 回滚测试路径为 `tests/rollback/`（34 文件，实测）；§2.1 依赖状态更新为当前值（14/09 号文已填充 v0.2.0，16 号文仍骨架） | AI-FILL-15 续写补完（指令块第 3/4/5/7 轮 + mop-up 纪律） |

---

*维护者：AI 架构协调者*