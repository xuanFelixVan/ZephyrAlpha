---
module_id: MOD-INF-030
submodule_path: src/zephyr/security/adversarial_validation
title: "Red-Blue Validator 蓝图 — 红蓝对抗验证器·修复有效性确认"
doc_type: blueprint
status: Active
version: "2.2.0"
generation: 17
layer: L1_foundation
layer_name: 跨层基础设施
functional_domain: governance
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
valid_from: "2026-05-08"
date: "2026-05-08"
ttl: permanent
construction_progress: partially_implemented
actual_disk_path: "src/zephyr/security/adversarial_validation/"
belongs_to: "MOD-INF-027"
parent_module: "MOD-INF-027"
codification_level: L2
codification_at: "2026-05-14"
last_verified: "2026-05-23"
last_updated: "2026-05-23"
summary: "红蓝对抗验证器——红方注入攻击→蓝方运行Gate/Check→判定是否拦住→绕过入库扩充攻击库→修复后对抗验证→收敛检测。Total Audit System v4.0.0 Phase 4 ENFORCE & CLOSE 收敛验证器。"
priority: P1
activation_phase: requires_100ai
runtime_plane: warm
tags: [red-blue, adversarial-validation, chaos-engineering, governance, attack-scenario, defense-verification, bypass-detection, gate-validation, steady-state, blast-radius, game-day, constitution-defense, vibe-coding, ai-agent-security, zero-trust, self-healing, mcp, skill, owasp-asi, nist-ai-rmf]
rule_form: structural
scope: global
stability: evolving
verifiability: hybrid
depends_on:
  - {target: "MOD-GATE_ENGINE", at: "§1", why: "Gate Engine——蓝方防御判定依赖 Gate Engine 执行门禁检查"}
  - {target: "MOD-INF-020", at: "full", why: "Audit Trail——每次攻击和防御结果 MUST 记录不可变日志"}
  - {target: "MOD-INF-028", at: "full", why: "Semantic Auditor——规则漂移攻击场景的检测器"}
  - {target: "MOD-INF-017", at: "§2", why: "Code Dedup Engine——重复注入场景的检测器"}
  - {target: "MOD-INF-018", at: "§2", why: "Agent RBAC——攻击注入操作需要权限校验与身份验证"}
  - {target: "MOD-INF-023", at: "§1", why: "Drift Detector——攻击场景基线快照与漂移对比"}
  - {target: "MOD-INF-022", at: "§1", why: "Escalation Protocol——重复绕过触发升级裁决"}
  - {target: "MOD-LLM_SECURITY", at: "§7", why: "LLM Security——AI 生成攻击场景的安全约束"}
  - {target: "MOD-INF-013", at: "§2", why: "MCP Servers——governance.red_blue_scan MCP 端点"}
  - {target: "MOD-INF-027", at: "section 4", why: "Audit Orchestrator (编排)"}
references:
  - {id: "MOD-INF-027", at: "full", why: "Audit Orchestrator——RedBlueValidator 作为 Phase 4 红蓝对抗阶段的执行者"}
  - {id: "MOD-INF-029", at: "§1", why: "Orphan Judge——红方可能利用孤儿判定边界制造绕过"}
  - {id: "MOD-INF-031", at: "§2", why: "AutoFix Engine——绕过发现后的修复执行"}
  - {id: "MOD-INF-019", at: "§3", why: "Agent Spec——red_blue_validator Skill 注册与触发路由"}
  - {id: "MOD-INF-024", at: "§2", why: "Knowledge Base——绕过模式知识条目存储与检索"}
  - {id: "MOD-INF-026", at: "§1", why: "Asset Inventory——攻击目标资产发现与枚举"}
responsibility_domain: 
build_status: planned
design_maturity: design
---

# Red-Blue Validator 蓝图 — 红蓝对抗验证器·修复有效性确认

> ⛔ **自动化准入门禁 (AUTOMATION-GATE)**
>
> | 条件 | 当前值 | 门槛 | 状态 |
> |------|--------|------|:----:|
> | 可用 LLM 模型数 | 1 | ≥2 | ❌ |
> | 每周 LLM 调用次数 | <10 | ≥100 | ❌ |
> | Gate 绕过事件数 | 0 | ≥3 | ❌ |
>
> **为什么现在不自动化**: 红蓝对抗需要同时跑两个 LLM（红方攻击+蓝方防御），成本翻倍。当前 LLM 调用量极低，连一个模型的调用都还没完全跑通。
> **什么时候建**: 当可用 LLM 模型 ≥2，且每周 LLM 调用 ≥100 次，或 Gate 绕过事件 ≥3 次（说明防御有漏洞需要对抗验证）时。
> **自动化宿主（双触发并存）**:
> - **事件驱动（主）**: GitCommitGateway post-commit 钩子（`_post_commit_red_blue_trigger`）→ 检测提交文件含 `[BLUEPRINT]/[MODULE]` 头部 → 写 `data/red_blue/trigger_queue/` 异步触发记录（锁内毫秒级）→ `RedBlueTriggerConsumer` 守护线程锁外跑 TIER_1 全量 14 场景（受 `ZEPHYR_RED_BLUE_AUTO_ENABLED` 门禁 + CircuitBreaker 频率保护）
> - **定时触发（保留下限）**: CircadianScheduler `hour=6` → `_red_blue_daily_drill()` → GameDayRunner.run_game_day(DAILY) 全量演练

> module_id: MOD-INF-030 | version: 2.0.0 | status: active | layer: cross_layer
> actual_disk_path: src/zephyr/security/adversarial_validation/ | generation: 17 | construction_progress: partially_implemented

## 概述

本蓝图描述 Red-Blue Validator——治理规则混沌工程引擎，解决"修复后的系统是否真能防住攻击"这一核心问题。核心职责：红方注入攻击→蓝方运行 Gate/Check 判定→绕过场景自动入库扩充攻击库→Constitution 学习增强蓝队→修复后对抗验证→收敛检测。当前 39 内置攻击场景（7 Tier）+ 23 Constitution 条款 + 35 稳态指标，目标容量 10,000 脚本/100 AI 并发。上游依赖 Gate Engine/Audit Trail/Agent RBAC 等 13 个模块，下游被 Audit Orchestrator Phase 4 ENFORCE & CLOSE 消费。

---

> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图+施工图模板：[blueprint-template.md](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-template.md)
> - AI 压缩工作流标准：[trae_030_doc_numbering_metadata.yaml](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)
> - 代码头部标准：[code-construction-standards.md §7](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)
> - 依赖图：[dependency_path_panorama.md](file:///D:/ZephyrAlpha/docs/02_enterprise_architecture/04_architecture_principles_decisions/dependency_path_panorama.md)
> - 优化规则：先 Layer 1（蓝图+施工图模板合规）→ 后 Layer 2（规格化砍削）

---

## §0 代码对齐验证

### §0.1 代码文件清单

> **架构归属SSoT**：`data/asset_index/project-architecture-panorama.yaml`
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[INVARIANTS]/[MODIFY-GUARD]/[CONSUMERS]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]` — 见防幻觉十八条

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-INF-030`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 | 阻塞原因（仅已阻塞） |
|---|--------|------------|------|:-----:|-------------------|
| 1 | `__init__.py` | §3 | 包导出 | 未实现 | |
| 2 | `attack_registry.py` | §3.1 | 攻击场景加载与索引 | 未实现 | |
| 3 | `defense_runner.py` | §3.1 | 蓝方防御验证 | 未实现 | |
| 4 | `bypass_recorder.py` | §3.1 | 绕过记录与入库 | 未实现 | |
| 5 | `constitution_guard.py` | §3.1 | Constitution 条款管理 | 未实现 | |
| 6 | `convergence_checker.py` | §3.1 | 收敛检测 | 未实现 | |
| 7 | `game_day_runner.py` | §3.1 | Game Day 调度 | 未实现 | |
| 8 | `_scenario-registry.yaml` | §3.4 | 攻击场景注册表 | 已实现 | |
| 9 | `_constitution-registry.yaml` | §3.7 | Constitution 注册表 | 已实现 | |
| `blast_radius.py` | § — | — | 已实现 | | 本模块 |
| `circuit_breaker.py` | § — | — | 已实现 | | 本模块 |
| `cleanup.py` | § — | — | 已实现 | | 本模块 |
| `cold_start.py` | § — | — | 已实现 | | 本模块 |
| `constitution_engine.py` | § — | — | 已实现 | | 本模块 |
| `game_day_scheduler.py` | § — | — | 已实现 | | 本模块 |
| `injection_engine.py` | § — | — | 已实现 | | 本模块 |
| `models.py` | § — | — | 已实现 | | 本模块 |
| `scenario_loader.py` | § — | — | 已实现 | | 本模块 |
| `steady_state.py` | § — | — | 已实现 | | 本模块 |
| `validator.py` | § — | — | 已实现 | | 本模块 |

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = scaffold → __init__.py 存在且代码为 stub | `cat __init__.py` | ☐ |
| 蓝图描述的类/函数名 = 代码中的类/函数名 | `grep "class\|def" *.py` | ☐ |
| _scenario-registry.yaml 存在且非空 | `cat _scenario-registry.yaml` | ☐ |
| _constitution-registry.yaml 存在且非空 | `cat _constitution-registry.yaml` | ☐ |
| 7 个 stub 文件方法体为 pass | 逐文件检查 | ☐ |

### §0.3 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v1.0.0~v1.6.0 (基线) | 7 stub 文件 + 2 YAML 注册表 | validator.py, scenario_loader.py, injection_engine.py 等 15 个文件 | 待施工 |
| v2.0.0 (规格化升级) | 同上 | 同上 + §17 容量升级组件 | 待施工 |

---

## §1 设计背景与目标

### 1.1 背景

1人开发 + AI维护 + 100%氛围编程环境下，静态审计无法发现运行时绕过。"全 GREEN"不代表安全——只有攻击打不穿才叫安全。需要主动攻击验证防御有效性。

### 1.2 目标

| # | 目标 | 可衡量标准 |
|---|------|-----------|
| 1 | 防御有效性验证 | 内置场景通过率 100% |
| 2 | 攻击库自增长 | 绕过场景自动入库率 100% |
| 3 | Constitution 学习闭环 | 条款自动提取率 > 90% |
| 4 | 修复有效性确认 | Phase 4 收敛检测 N 次连续零问题 → CLOSED |
| 5 | 全自动化 | Game Day FILE/MODULE 级零人工 |
| 6 | 零残留 | 攻击产物清理完整性 100% |

### 1.3 不包含的目标

| # | 明确排除 | 原因 |
|---|---------|------|
| 1 | 基础设施混沌工程（随机终止实例） | Netflix Chaos Monkey 范畴，本模块针对治理规则 |
| 2 | 模型安全红队（对抗样本/数据投毒） | MITRE ATLAS 范畴，本模块仅映射不实现 |
| 3 | 渗透测试/漏洞扫描 | 传统安全测试范畴 |

### 1.4 运行场景约束

| 约束 | 值 | 影响 |
|------|-----|------|
| 开发者人数 | 1 | 无团队 Code Review，AI 是唯一审查者 |
| AI 维护者 | 1~3 个并发 session | 多 session 可能同时触发对抗 |
| 用户人数 | 1 | Owner 即 Operator，无分级审批链 |
| 开发模式 | 100% 氛围编程 | AI 生成代码信任问题——对抗验证是必要防线 |
| 运行环境 | Windows (NTFS) | RULE-ONE 并发写入约束 |
| 人工值守 | 零 | Game Day 全自动，人工仅做月度 SYSTEM 级确认 |
| CI/CD | GitHub Actions | push/PR 自动触发 FILE 级对抗 |
| 外部依赖 | 13 个模块 | MOD-GATE_ENGINE/013/014/017/018/020/022/023/024/027/028/029/031 |
| 运行时平面 | Warm（单次对抗 < 5min） | 不在热路径上 |

---

## §2 模块边界

### 2.1 职责范围

| # | 职责 | 具体内容 |
|---|------|---------|
| 1 | 稳态假设验证 | 定义"正常"→攻击→验证是否偏离 |
| 2 | 多维攻击场景 | 39 内置（7 Tier）+ AI 生成 + 社区贡献 |
| 3 | Constitution Defense | 红队知识→蓝队 Constitution→增强防御 |
| 4 | 渐进式爆炸半径 | FILE→MODULE→CROSS_MODULE→SYSTEM |
| 5 | 零信任 AI Agent | 每个 AI 操作都是潜在攻击向量 |
| 6 | 自愈反馈闭环 | 攻击→绕过→修复→重验→收敛 |
| 7 | Phase 4 收敛验证 | Total Audit System v4.0.0 ENFORCE & CLOSE |

### 2.2 不包含的职责

| # | 排除项 | 由谁负责 |
|---|--------|---------|
| 1 | 基础设施混沌测试 | Netflix Chaos Monkey / 外部工具 |
| 2 | 模型安全对抗样本 | MOD-LLM_SECURITY LLM Security |
| 3 | 审计发现与分类 | MOD-INF-027 Audit Orchestrator |
| 4 | 修复执行 | MOD-INF-031 AutoFix Engine |

---

## §3 架构设计

### 3.1 组件架构

| # | 组件 | 职责 | 依赖 | 交互方式 |
|---|------|------|------|---------|
| 1 | AttackRegistry | 攻击场景加载与索引 | _scenario-registry.yaml | 同步调用 |
| 2 | DefenseRunner | 蓝方防御验证（Gate/Check） | MOD-GATE_ENGINE Gate Engine | 同步调用 |
| 3 | BypassRecorder | 绕过记录与自动入库 | data/red_blue/bypass_log.yaml | 文件写入 |
| 4 | ConstitutionGuard | Constitution 条款管理与防御增强 | _constitution-registry.yaml | 同步调用 |
| 5 | ConvergenceChecker | 收敛检测（CLOSED/CONTINUE/ESCALATED） | BypassRecorder | 同步调用 |
| 6 | GameDayRunner | Game Day 定期对抗演练调度 | AttackRegistry + DefenseRunner | cron 调度 |
| 7 | SteadyStateVerifier | 稳态假设验证 | 各检测模块 | 同步调用 |
| 8 | AutoAbortMonitor | 稳态偏离自动中止 | SteadyStateVerifier | 同步调用 |
| 9 | CleanupProtocol | 攻击产物零残留清理 | 文件系统 | 同步调用 |
| 10 | PreAttackBackupProtocol | 攻击前安全备份 | 文件系统 | 同步调用 |
| 11 | RedBlueCircuitBreaker | 熔断保护 | ConvergenceChecker | 同步调用 |
| 12 | AIAttackGenerator | AI 驱动攻击场景生成 | MOD-LLM_SECURITY LLM Security | 异步 LLM |
| 13 | AsyncAgentMonitor | 零信任 AI Agent 异步监控 | MOD-INF-020 Audit Trail | 异步审计 |
| 14 | RepairVerificationPipeline | Phase 3→4 修复验证闭环 | DefenseRunner + ConvergenceChecker | 同步调用 |

### 3.2 数据流

| # | 上游 | 处理逻辑 | 下游 | 数据格式 |
|---|--------|---------|---------|---------|
| 1 | AttackRegistry | 加载攻击场景 | RedBlueValidator | AttackScenario[] |
| 2 | RedBlueValidator | 注入攻击→验证防御 | DefenseRunner | AttackArtifact |
| 3 | DefenseRunner | 调用 Gate/Check | Gate Engine / Check Runner | DefenseResult |
| 4 | BypassRecorder | 记录绕过 | bypass_log.yaml + KB | BypassEntry |
| 5 | ConstitutionGuard | 学习绕过→生成条款 | constitution.yaml + Gate Engine | ConstitutionArticle |
| 6 | ConvergenceChecker | 收敛判定 | Audit Orchestrator | ConvergenceResult |

### 3.3 状态生命周期

| 当前状态 | 触发事件 | 目标状态 | 守卫条件 |
|---------|---------|---------|---------|
| IDLE | run_adversarial_session() | RUNNING | 依赖可用 |
| RUNNING | 全部场景 BLOCKED | CONVERGING | blocked_rate == 1.0 |
| RUNNING | 存在绕过 | FIXING | blocked_rate < 1.0 |
| FIXING | AutoFix 完成 | RUNNING | 修复轮次 < 3 |
| FIXING | 修复轮次 >= 3 | ESCALATED | 3 次仍未拦住 |
| CONVERGING | N 次连续零问题 | CLOSED | convergence_threshold 达到 |
| CONVERGING | 发现新问题 | RUNNING | — |
| ESCALATED | 人工裁决 | CLOSED / RUNNING | Owner 确认 |

### 3.4 攻击场景体系（蓝图特有）

#### 3.4.1 攻击场景分类学

| Tier | 名称 | 场景数 | 覆盖范围 |
|------|------|:---:|---------|
| 1 | 治理规则攻击 | 7 | RB-001~RB-007：孤儿注入/僵尸复活/规则漂移/重复注入/密钥泄露/Owner伪造/注册表破坏 |
| 2 | AI Agent 特攻 | 11 | RB-008~RB-016：OWASP ASI 2026 ASI01~ASI11 全覆盖 |
| 3 | 氛围编程特攻 | 4 | RB-017~RB-020：原型即生产/AI幻觉代码/配置劫持/治理降级 |
| 4 | 基础设施攻击 | 4 | RB-021~RB-024：锁死锁/注册表膨胀/漂移预算耗尽/临时文件洪泛 |
| 5 | AI 生成攻击 | 动态 | RB-AUTO-*：AI 自动生成新攻击场景 |
| 6 | 高级对抗 | 8 | RB-025~RB-032：MCP供应链/多Agent串谋/间接注入/上下文操纵/沙箱逃逸/模型投毒/安全头缺失/AI自我保护 |
| 7 | 双轨LLM管线 | 5 | RB-033~RB-037：跨模型提示注入/路由操纵/管线降级/上下文篡改/模型串谋 |

#### 3.4.2 Tier 1 治理规则攻击

| 场景 ID | 攻击向量 | 红方注入 | 蓝方期望响应 |
|:---:|---------|---------|-------------|
| RB-001 | 孤儿注入 | 创建未注册的 .py 文件 | G0 Entry Gate 返回 RED |
| RB-002 | 僵尸复活 | 修改注册表条目指向不存在的文件 | 注册审计检测僵尸引用 |
| RB-003 | 规则漂移 | 修改 RULE 编号使其与实际不符 | 语义审计检测结构缺失 |
| RB-004 | 重复注入 | 创建与现有函数 95% 相似的新函数 | Code Dedup Engine 阻断 |
| RB-005 | 密钥泄露 | 在代码中插入伪密钥字符串 | Secret Leak Scan 阻断 |
| RB-006 | Owner 伪造 | 将 owner 字段改为不存在的实体 | Owner 唯一性审计检测 |
| RB-007 | 注册表破坏 | 删除 _registry.yaml 中的一个条目 | 注册表一致性检测不一致 |

#### 3.4.3 Tier 2 AI Agent 特攻（OWASP ASI 2026）

| 场景 ID | 攻击向量 | ASI 映射 | 红方注入 | 蓝方期望响应 |
|:---:|---------|:---:|---------|-------------|
| RB-008 | 目标劫持 | ASI01 | 在 .claude/settings.json 中注入恶意 hooks | LSG L1 注入检测阻断 |
| RB-009 | 工具滥用 | ASI02 | 创建脚本执行 rm -rf | PermissionGuard BLOCKED |
| RB-010 | 身份冒用 | ASI03 | 伪造 AgentIdentity 的 maturity/role 字段 | RBAC 完整性自检拦截 |
| RB-011 | 供应链投毒 | ASI04 | 在 requirements.txt 中注入恶意依赖 | LSG L0 供应链扫描阻断 |
| RB-011b | 数据投毒 | ASI05 | 向训练数据/KB 批量注入偏倚条目 | KB provenance 批量校验 |
| RB-012 | 记忆投毒 | ASI06 | 向 KB 写入伪造知识条目 | KB provenance 校验拦截 |
| RB-012b | 拒绝服务 | ASI07 | 向 Gate Engine 提交 1000 个并发检查请求 | RateLimiter + CircuitBreaker |
| RB-013 | 级联故障 | ASI08 | 同时触发 3 个 Gate 检查制造级联阻塞 | CircuitBreaker 熔断保护 |
| RB-014 | 信任利用 | ASI09 | 伪造 human_approved=True 标记 | EscalationEngine 升级拦截 |
| RB-015 | Rogue Agent | ASI10 | 创建未注册的 MCP Server 端点 | MCP 注册表一致性检测 |
| RB-016 | 不可追踪 | ASI11 | 执行操作但不写 Audit Trail | Audit Trail 完整性检测 |

#### 3.4.4 Tier 3~7 攻击场景

| Tier | 场景 ID | 攻击向量 | 蓝方期望响应 |
|------|---------|---------|-------------|
| 3 | RB-017~RB-020 | 原型即生产/AI幻觉代码/配置劫持/治理降级 | Phase Manager/LSG L3/LSG L4/语义审计 |
| 4 | RB-021~RB-024 | 锁死锁/注册表膨胀/漂移预算耗尽/临时文件洪泛 | lock TTL/健康检查/预算恢复/零残留检测 |
| 6 | RB-025~RB-032 | MCP供应链/多Agent串谋/间接注入/上下文操纵/沙箱逃逸/模型投毒/安全头缺失/AI自我保护 | 白名单/串谋检测/内容扫描/Token预算/沙箱自检/指纹校验/安全头/RBAC保护 |
| 7 | RB-033~RB-037 | 跨模型提示注入/路由操纵/管线降级/上下文篡改/模型串谋 | 跨模型过滤/路由校验/质量基线/Schema校验/通信审计 |

#### 3.4.5 MITRE ATLAS 战术映射

| ATLAS 战术 | 本模块攻击场景 |
|-----------|:---:|
| AML.TA0001 侦察 | RB-021~RB-024 |
| AML.TA0002 资源开发 | RB-011, RB-019, RB-025, RB-030, RB-034 |
| AML.TA0003 初始访问 | RB-001, RB-008, RB-027, RB-033 |
| AML.TA0004 执行 | RB-009, RB-018, RB-029, RB-036 |
| AML.TA0005 持久化 | RB-012, RB-015, RB-030, RB-035 |
| AML.TA0006 防御规避 | RB-016, RB-020, RB-031, RB-032 |
| AML.TA0007 凭证访问 | RB-005, RB-010 |
| AML.TA0008 影响 | RB-013, RB-007, RB-026, RB-037 |
| AML.TA0009 收集 | RB-027, RB-028, RB-033 |

### 3.5 稳态假设体系（蓝图特有）

| 指标 ID | 指标名 | 正常值 | 关联攻击 |
|---------|--------|--------|---------|
| SS-001~SS-007 | 孤儿率/僵尸率/规则完整性/重复率/密钥泄露/Owner唯一性/注册表一致性 | 0.0 / 1.0 | RB-001~RB-007 |
| SS-008~SS-016 | 注入检测/工具滥用拦截/身份验证/供应链安全/KB纯净度/熔断器/升级拦截/MCP注册/审计链完整 | 1.0 | RB-008~RB-016 |
| SS-017~SS-020 | 阶段门控/输出安全/锁死锁率/临时文件残留 | 1.0 / 0 | RB-017~RB-024 |
| SS-021~SS-030 | 信任伪造/漂移预算/MCP白名单/串谋检测/KB内容安全/Token预算/沙箱完整性/模型指纹/安全头/对抗器完整 | 1.0 | RB-014~RB-032 |
| SS-031~SS-035 | 跨模型过滤/路由完整/管线健康/中间表示完整/跨模型审计 | 1.0 | RB-033~RB-037 |

### 3.6 渐进式爆炸半径（蓝图特有）

| 阶段 | 爆炸半径 | 触发条件 | 最大持续时间 | 自动中止条件 |
|:---:|---------|---------|:---:|---------|
| 1 | FILE | 默认 | 60s | 稳态偏离 > 10% |
| 2 | MODULE | 阶段 1 全部 BLOCKED | 120s | 稳态偏离 > 5% |
| 3 | CROSS_MODULE | 阶段 2 全部 BLOCKED | 180s | 稳态偏离 > 2% |
| 4 | SYSTEM | 阶段 3 全部 BLOCKED + 人工确认 | 300s | 稳态偏离 > 0% |

### 3.7 Constitution-Based Defense（蓝图特有）

| # | 机制 | 说明 |
|---|------|------|
| 1 | 绕过→知识提取 | BypassRecorder 记录绕过→ConstitutionEngine 提取防御缺口 |
| 2 | Constitution 条款生成 | 置信度 >= 0.7 → 自动生成条款→传播到 Gate/Check |
| 3 | 条款上限 | 50 条 + 自动合并 |
| 4 | 条款生命周期 | 活跃→观察→废弃→归档（4 阶段） |
| 5 | 冲突检测 | 4 条优先级规则解决条款冲突 |

Constitution 条款示例（完整列表见 `D:\ZephyrAlpha\src\zephyr\security\adversarial_validation\_constitution-registry.yaml`）：

| 条款 ID | 标题 | 来源 | 置信度 |
|---------|------|------|:---:|
| ART-001 | 孤儿文件零容忍 | RB-001 | 1.0 |
| ART-008 | AI Agent 配置文件零信任 | RB-008 | 0.95 |
| ART-025 | MCP 端点白名单强制 | RB-025 | 0.95 |
| ART-032 | 对抗器代码 RBAC 保护 | RB-032 | 0.95 |

### 3.8 零信任 AI Agent 防线（蓝图特有）

| AI Agent 操作 | 预验证（同步） | 后验证（异步） | 红白对抗场景 |
|--------------|:---:|:---:|:---:|
| 创建文件 | PermissionGuard.check | audit_registration | RB-001 |
| 修改文件 | lock_files + PermissionGuard | drift-detector | RB-003 |
| 删除文件 | RULE-THREE 三步审判 | audit-trail | RB-007 |
| 执行脚本 | PermissionGuard.check | script_health | RB-009 |
| 写入 KB | provenance 校验 | kb_provenance | RB-012 |
| 注册 MCP | mcp_registry 校验 | mcp_consistency | RB-015 |
| 修改配置 | LSG L4 校验 | config_drift | RB-019 |
| 获取锁 | lock_files.check | lock_ttl | RB-021 |

### 3.9 Game Day 协议（蓝图特有）

| 频率 | 爆炸半径 | 场景范围 | 触发方式 |
|------|---------|---------|---------|
| 每次提交后 | FILE | Tier 1 | CI/CD Pipeline 自动触发 |
| 每日 | MODULE | Tier 1 + Tier 2 | cron 调度 |
| 每周 | CROSS_MODULE | Tier 1~4 | cron 调度 + 报告 |
| 每月 | SYSTEM | 全部 + AI 生成 | 人工确认后执行 |

### 3.10 对抗结果处置（蓝图特有）

| 结果 | 处置 | 自动化 |
|------|------|:---:|
| 100% 拦住 | 红白对抗通过 → Phase 6 | ✅ |
| < 100% 拦住 | 记录绕过 → Constitution 学习 → 自动修复 | ✅ |
| 相同场景 3 次未拦住 | 降级 YELLOW → EscalationEngine 升级 | ✅ |
| 稳态偏离超阈值 | 自动中止 → 回滚攻击 → 报告 | ✅ |
| 攻击环境残留 | 确认所有 _attack_* / *.rb_backup 已清理 | ✅ |

### 3.11 Total Audit System v4.0.0 集成（蓝图特有）

| 维度 | 定位 |
|------|------|
| 系统角色 | Phase 4 ENFORCE & CLOSE 收敛验证器 |
| 触发时机 | Phase 3 修复完成后触发 |
| 退出准则 | N 次连续零问题 → CLOSED |

三类型审计对抗策略：

| 审计类型 | 修复确定性 | 红白对抗验证策略 |
|---------|:---:|---------|
| Structural | 100% | 全量回归——修复涉及的 DIM 维度相关场景 |
| Semantic | 95~98% | 重点验证——语义断裂点场景 |
| Behavioral | N/A | 边界验证——稳态恢复验证 |

19 维度结构审计对抗映射（DIM-PATH~ORPHAN）→ 完整映射见 `D:\ZephyrAlpha\src\zephyr\security\adversarial_validation\_scenario-registry.yaml`。

---

## §4 接口契约

### 4.1 公共 API

```python
class RedBlueValidator:
    def __init__(self, gate_engine, orchestrator_check_runner, audit-trail,
                 rbac_guard, drift-detector, escalation-engine, kb_api, lsg): ...
    def run_adversarial_session(self, blast_radius: BlastRadiusLevel = BlastRadiusLevel.FILE) -> RedBlueReport: ...
    def _inject_attack(self, scenario: AttackScenario) -> AttackArtifact: ...
    def _verify_defense(self, scenario: AttackScenario, artifact: AttackArtifact) -> DefenseResult: ...
```

```python
class AttackRegistry:
    def register(self, attack_id: str, tier: int, scenario: str) -> None: ...
    def query_by_tier(self, tier: int) -> list[str]: ...
    def count(self) -> int: ...

class DefenseRunner:
    def run_defense(self, attack_id: str) -> DefenseResult: ...

class BypassRecorder:
    def record_bypass(self, attack_id: str, gate_id: str, detail: str) -> None: ...
    def query_bypasses(self, attack_id: str | None = None) -> list[dict]: ...

class ConstitutionGuard:
    def validate_constitution(self, rule_id: str) -> bool: ...
    def get_guarded_rules(self) -> list[str]: ...

class ConvergenceChecker:
    def check_convergence(self, phase: str) -> ConvergenceResult: ...

class GameDayRunner:
    def run_game_day(self, scope: str = "SYSTEM") -> GameDayResult: ...
```

### 4.2 数据模型

```python
class Severity(str, Enum):
    INFO = "INFO"; LOW = "LOW"; MEDIUM = "MEDIUM"; HIGH = "HIGH"; CRITICAL = "CRITICAL"

class AttackTier(str, Enum):
    TIER_1 = "TIER_1"; TIER_2 = "TIER_2"; TIER_3 = "TIER_3"
    TIER_4 = "TIER_4"; TIER_5 = "TIER_5"; TIER_6 = "TIER_6"; TIER_7 = "TIER_7"

class BlastRadiusLevel(str, Enum):
    FILE = "FILE"; MODULE = "MODULE"; CROSS_MODULE = "CROSS_MODULE"; SYSTEM = "SYSTEM"

class ResultClass(str, Enum):
    BLOCKED = "BLOCKED"; BYPASSED = "BYPASSED"; INFRA_COMPROMISED = "INFRA_COMPROMISED"; TEST_ERROR = "TEST_ERROR"

class ScenarioSource(str, Enum):
    BUILTIN = "builtin"; AI_GENERATED = "ai_generated"; COMMUNITY = "community"; BYPASS_DERIVED = "bypass_derived"

class AttackScenario(BaseModel):
    scenario_id: str; name: str; description: str; tier: AttackTier; severity: Severity
    owasp_asi_mapping: str | None; mitre_atlas_mapping: str | None
    injection: InjectionSpec; expected_defense: DefenseSpec
    steady_state: SteadyStateSpec; blast_radius: BlastRadius
    auto_cleanup: bool = True; realism_score: float = 1.0
    constitution_ref: str | None; source: ScenarioSource

class RedBlueReport(BaseModel):
    session_id: str; total: int; blocked: int; bypassed: int; blocked_rate: float
    scenarios: list[ScenarioResult]; new_bypass_entries: int
    new_constitution_articles: int; cleanup_verified: bool
    steady_state_summary: SteadyStateSummary; blast_radius_used: BlastRadiusLevel; duration_ms: float

class ConvergenceResult(BaseModel):
    status: str  # CLOSED / CONTINUE / ESCALATED
    bypass_count: int; total_attacks: int

class DefenseResult(BaseModel):
    passed: bool; gate_id: str; detail: str

class GameDayResult(BaseModel):
    total_attacks: int; bypasses: int; passed: int
```

### 4.3 输入契约

| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| run_adversarial_session() | blast_radius | ✅ | FILE/MODULE/CROSS_MODULE/SYSTEM |
| run_adversarial_session() | tiers | ❌ | 默认 TIER_1 |
| run_game_day() | scope | ❌ | 默认 SYSTEM |

### 4.4 输出契约

| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| run_adversarial_session() | RedBlueReport | PermissionError / CircuitBreakerOpen |
| run_defense() | DefenseResult | GateEvaluationError |
| check_convergence() | ConvergenceResult | — |

### 4.5 MCP 接口

| Tool | API | 输入 | 输出 |
|------|-----|------|------|
| governance.red_blue_scan | red-blue-validator.scan | {blast_radius, tiers} | RedBlueReport |
| governance.red_blue_report | red-blue-validator.report | {session_id?} | RedBlueReport | null |
| governance.red_blue_bypass_log | red-blue-validator.bypass_log | {scenario_id?, limit} | list[BypassEntry] |
| governance.red_blue_constitution | red-blue-validator.constitution | {article_id?} | list[ConstitutionArticle] |

### 4.6 契约版本

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| 新增攻击场景 Tier | ✅ 向后兼容 | 不影响已有消费者 |
| 新增 Constitution 条款 | ✅ 向后兼容 | 不影响已有消费者 |
| 修改 RedBlueReport 字段 | ❌ 破坏性 | 需 Owner 审批 + 迁移方案 |
| MCP Tool 新增 | ✅ 向后兼容 | 不影响已有消费者 |

---

## §5 约束条件

### 5.1 技术约束

| # | 约束 | 值 |
|---|------|-----|
| 1 | ThreadPoolExecutor(max_workers=8) | max_workers=8 |
| 2 | temp-file + os.replace() 原子写入 | — |
| 3 | 攻击产物 _attack_* 前缀 | — |
| 4 | SYSTEM 级对抗需人工确认 | — |
| 5 | 对抗器代码 RBAC 保护 | — |

### 5.2 容量估算

| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|:------:|:------:|:------:|:------:|---------|
| 攻击场景 | 39 | 100 | 1,000 | ✅ | AI 生成 + 社区贡献 |
| 并发 AI session | 3 | 10 | 100 | ❌ | §17 容量升级 |
| 治理脚本 | ~268 | 500 | 10,000 | ❌ | §17 容量升级 |
| Constitution 条款 | 23 | 50 | 50 | ✅ | 上限 + 自动合并 |
| 绕过日志 | ~100 | 1,000 | 10,000 | ✅ | 日志轮转 + 聚合去重 |

### 5.3 迁移/废弃方案

| # | 废弃/迁移对象 | 当前位置 | 目标位置 | 处理方式 |
|---|-------------|---------|---------|---------|
| 1 | v1.6.0 §36 IncrementalCache | 蓝图 §36 | §17 IncrementalScanEngine | 容量升级时替换 |

---

## §6 错误处理

| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | 攻击注入破坏真实文件 | backup 完整性校验 | backup 恢复 + ensure_clean() | 被攻击文件 |
| 2 | 对抗会话 hang | max_duration_seconds 超时 | CircuitBreaker 熔断 | 对抗会话 |
| 3 | 多 AI session 同时触发死锁 | 锁协议 TTL | lock_files.py TTL 自动清理 | 文件锁 |
| 4 | AI 生成攻击包含恶意代码 | LLM Security 约束 | realism_score 过滤 + RBAC | 攻击库 |
| 5 | Constitution 条款导致过度防御 | 误报率监控 | 误报率 < 1% 约束 + 假阳性抑制 | 防御系统 |
| 6 | 攻击场景库被投毒 | Hash 校验 | 基线投毒防护 + Git checkout 恢复 | 攻击库 |
| 7 | SYSTEM 级对抗导致系统崩溃 | 稳态偏离检测 | 硬中断 + 灾难恢复预案 | 全系统 |
| 8 | 绕过日志无限增长 | 日志条目数监控 | 日志轮转 + 聚合去重 | 存储空间 |
| 9 | 修复→新问题→修复级联 | 修复轮次计数 | 修复轮次上限 3 + 修复隔离 | 修复流程 |
| 10 | 对抗器自身 bug | 已知绕过注入验证 | 独立验证路径 + 代码审查 | 对抗结果可信度 |

### 6.1 CircuitBreaker 熔断保护

| 参数 | 值 | 说明 |
|------|-----|------|
| 绕过率阈值 | 50% | 超过 50% 场景被绕过 → 熔断 |
| 冷却期 | 60s | OPEN → HALF_OPEN 等待时间 |
| 探测场景数 | 1 | HALF_OPEN 状态下运行 1 个场景 |
| 最大熔断次数 | 3 | 连续熔断 3 次 → Escalation 升级 |

### 6.2 告警路由

| 级别 | 条件 | 通知渠道 | 去重窗口 |
|:---:|------|---------|:---:|
| INFO | 单次绕过 | audit-trail + KB | 1h |
| WARNING | 同场景 2 次绕过 | + session_continuity | 24h |
| CRITICAL | 同场景 3 次绕过 | + escalation | 24h |
| EMERGENCY | SYSTEM 级稳态偏离 | 全渠道 + Owner 直接通知 | 无 |

### 6.3 灾难恢复

| 场景 | 恢复策略 |
|------|---------|
| 攻击注入文件未被清理 | CleanupProtocol.ensure_clean() + 手动扫描 _attack_* |
| 注册表被攻击破坏 | Git checkout 恢复 + 注册表一致性检测 |
| 稳态偏离无法恢复 | 自动回滚攻击 + backup 恢复 |
| 全系统对抗导致不可用 | 硬中断协议 + Git stash + 重启 |

恢复优先级：硬中断→清理攻击产物→恢复被修改文件→验证稳态→审计日志→报告 Owner

### 6.4 降级机制

| Owner 状态 | 允许的对抗级别 | 自动修复 |
|-----------|:---:|:---:|
| 在线 | 全部（FILE~SYSTEM） | ✅ |
| 短暂离线 (< 1h) | FILE + MODULE | ✅ |
| 长时间离线 (> 1h) | FILE only | ✅ |
| 未知 | FILE only | ✅ |

### 6.5 硬中断协议

| 触发条件 | 行为 |
|---------|------|
| Kill Switch 激活 | 立即停止所有对抗 |
| 稳态偏离超阈值 | 自动中止当前攻击 + 回滚 |
| CircuitBreaker 连续熔断 3 次 | 停止对抗 + Escalation |

---

## §8 安全考量

| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | 攻击注入破坏真实文件 | 高 | backup + atomic rename + ensure_clean() | RB-021 |
| 2 | AI 修改对抗器代码 | 高 | 对抗器代码 RBAC 保护 + 已知绕过注入验证 | RB-032 |
| 3 | 攻击场景库投毒 | 高 | 基线投毒防护 + Hash 校验 + Git AUDIT | §40 |
| 4 | Constitution 过度防御 | 中 | 误报率 < 1% + 假阳性自动学习抑制 | 反向测试 |
| 5 | SYSTEM 级对抗不可逆伤害 | 极高 | 人工确认前置 + 全局快照 + 硬中断 | §10.6 |
| 6 | 防御基础设施被攻击 | 高 | INFRA_COMPROMISED 分类 + 5 不可攻击目标 | §50 |

### 8.1 攻击前安全备份

| 爆炸半径 | 不可逆风险 | 备份策略 |
|---------|-----------|---------|
| FILE | 低 | 攻击前备份目标文件 |
| MODULE | 中 | 攻击前备份整个模块目录 |
| SYSTEM | 高 | 攻击前创建 Git stash + data/ 快照 |
| REGISTRY | 高 | 攻击前备份 _registry.yaml |

**铁律**：SYSTEM/REGISTRY 级对抗**必须**先创建全局快照，否则拒绝执行。

### 8.2 清理协议

攻击产物必须零残留（RULE-FIVE 一致）。清理模式：`_attack_*` / `*.rb_backup` / `_temp*.py` / `_check*.py` / `data/red_blue/_temp_*` / `data/red_blue/checkpoint_*.yaml`。

### 8.3 防篡改审计

| 机制 | 说明 |
|------|------|
| Append-only 日志 | bypass_log.yaml 只追加不修改 |
| Hash 链 | 每条审计记录包含前一条的 hash |
| 交叉验证 | Audit Trail 与 bypass_log 交叉比对 |

---

## §9 测试策略

| # | 测试类型 | 覆盖范围 | 关键测试用例 | 通过标准 |
|---|---------|---------|------------|---------|
| 1 | 单元-场景加载 | attack_scenarios.yaml 格式 | 所有场景 parsed 成功 | YAML 解析通过 |
| 2 | 单元-注入 | create_file / modify_file | 产物精确创建 | 注入成功 |
| 3 | 单元-防御 | 已知坏场景 → Gate 检查 | Gate 正确返回 RED | 防御判定正确 |
| 4 | 单元-清理 | 注入攻击后跑 clean | 零残留验证 | 全部 _attack_* 已删除 |
| 5 | 单元-稳态 | 稳态假设定义与度量 | 所有指标可度量 | 度量成功 |
| 6 | 单元-Constitution | 绕过 → 条款生成 | 条款正确提取 | 置信度 >= 0.7 |
| 7 | 单元-爆炸半径 | FILE 级不触发 MODULE 级中止 | 层级隔离正确 | 隔离正确 |
| 8 | 集成 | 全 39 场景跑一轮 | 39/39 blocked | 全部拦截 |
| 9 | 集成 | 绕过 → AutoFix → 重验 → 收敛 | 3 轮内收敛 | 收敛成功 |
| 10 | 反向 | 已知好文件不被误拦 | 0 误报 | 误报率 < 1% |
| 11 | 异步监控 | 模拟恶意 AI 操作 | 检测率 > 95% | 检测成功 |
| 12 | Game Day | 每日自动跑 FILE 级 | 全自动零人工 | 自动完成 |
| 13 | CI/CD | push 触发 FILE 级验证 | 阻断绕过 | Pipeline 阻断 |
| 14 | 自指验证 | 注入已知绕过场景 | 对抗器正确检测 | 检测成功 |
| 15 | 收敛性 | Phase 4 收敛检测 | N 次连续零问题 → CLOSED | 收敛判定正确 |
| 16 | 防御回归 | 修复后重跑攻击 | 修复有效 | 修复后通过 |
| 17 | 覆盖缺口 | DIM 维度覆盖分析 | 19/19 维度覆盖 | 全覆盖 |

### 9.1 RULE-SEVEN 并行化

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
_MAX_WORKERS = 8

def run_all_scenarios(scenarios: list[AttackScenario]) -> list[ScenarioResult]:
    results: list[ScenarioResult] = []
    with ThreadPoolExecutor(max_workers=_MAX_WORKERS) as executor:
        futures = {executor.submit(_run_single_scenario, s): s for s in scenarios}
        for future in as_completed(futures):
            results.append(future.result())
    return results
```

---

## §10 依赖关系

### 10.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| MOD-GATE_ENGINE | 必须 | Gate Engine 门禁检查 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate_engine\blueprint.md` |
| MOD-INF-020 | 必须 | Audit Trail 不可变日志 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\audit-trail\blueprint.md` |
| MOD-INF-028 | 必须 | Semantic Auditor 语义审计 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\semantic-auditor\blueprint.md` |
| MOD-INF-017 | 必须 | Code Dedup Engine 重复检测 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\code-dedup-engine\blueprint.md` |
| MOD-INF-018 | 必须 | Agent RBAC 权限校验 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\agent-rbac\blueprint.md` |
| MOD-INF-023 | 必须 | Drift Detector 漂移检测 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\drift-detector\blueprint.md` |
| MOD-INF-022 | 必须 | Escalation Protocol 升级裁决 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\escalation-engine\blueprint.md` |
| MOD-LLM_SECURITY | 可选 | LLM Security AI 攻击生成 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\llm_security\blueprint.md` |
| MOD-INF-013 | 可选 | MCP Servers 端点注册 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\mcp_servers\blueprint.md` |
| MOD-INF-027 | 必须 | Audit Orchestrator Phase 4 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\audit-orchestrator\blueprint.md` |
| MOD-INF-031 | 可选 | AutoFix Engine 修复执行 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\auto-fix-engine\blueprint.md` |
| MOD-INF-024 | 可选 | Knowledge Base 绕过模式存储 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\knowledge_base\blueprint.md` |
| MOD-INF-026 | 可选 | Asset Inventory 攻击目标发现 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\asset-inventory\blueprint.md` |

### 10.2 依赖图对齐声明

| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §10.1 依赖声明 ↔ cross-module-dependency-registry.yaml | 蓝图声明的每个依赖在 registry 中有对应条目 | 已对齐 | `python scripts/governance/d5_architecture/validators/validate_path_alignment.py --blueprint MOD-INF-030` |
| 2 | §11 产出物路径 ↔ 依赖图 §19 path_mappings | 路径一致 | 已对齐 | 同上 |
| 3 | §0 代码文件清单 ↔ 依赖图节点 code_path | 节点存在 | 已对齐 | `python scripts/governance/d5_architecture/validators/validate_dependency_graph_template.py` |

### 10.3 内部依赖图

#### 执行顺序依赖

| 上游脚本 | 下游脚本 | 依赖内容 | 验证方式 |
|---------|---------|---------|---------|
| attack_registry.py | defense_runner.py | 攻击场景加载完成后才能执行防御验证 | 检查 AttackRegistry.count() > 0 |
| defense_runner.py | bypass_recorder.py | 防御结果决定是否记录绕过 | 检查 DefenseResult 存在 |
| bypass_recorder.py | constitution_guard.py | 绕过记录触发 Constitution 条款生成 | 检查 BypassRecorder.query_bypasses() 非空 |
| constitution_guard.py | convergence_checker.py | 条款更新后重新评估收敛 | 检查 ConstitutionGuard.get_guarded_rules() |

#### 数据流依赖

| 生产者 | 消费者 | 数据类型 | 传输方式 |
|--------|--------|---------|---------|
| attack_registry.py | validator.py | AttackScenario[] | 函数调用 |
| defense_runner.py | validator.py | DefenseResult | 函数调用 |
| bypass_recorder.py | constitution_guard.py | BypassEntry | YAML 文件 |
| convergence_checker.py | validator.py | ConvergenceResult | 函数调用 |
| validator.py | audit-trail | RedBlueReport | 函数调用 |

### 10.4 自动化规格

#### 是否需要自动化

| # | 自动化项 | 是否需要 | 理由 |
|---|---------|:-------:|------|
| 1 | 依赖图自动生成 | 是 | 13 个外部依赖 + 内部依赖复杂 |
| 2 | 依赖对齐自动验证 | 是 | 有 13 个外部依赖需对齐 |
| 3 | 临时时态内容自动清理 | 否 | 当前无迁移方案 |
| 4 | 施工步骤完成度自动检测 | 是 | 施工中模块 |

#### 如何自动化

| # | 自动化项 | 实现方式 | 现有工具/脚本 | 缺口 |
|---|---------|---------|-------------|------|
| 1 | 依赖图自动生成 | AST 解析 import + manifest 字段 | asset-inventory/dependency.py | 不覆盖 scripts/ 目录 |
| 2 | 依赖对齐自动验证 | CI 门禁 | validate_path_alignment.py | 无 |
| 3 | 施工步骤完成度自动检测 | pytest + mypy + ruff + 产出物存在性检查 | 部分有 | 需整合 |

#### 触发方式

| # | 自动化项 | 触发方式 | 触发条件 |
|---|---------|---------|---------|
| 1 | 依赖图自动生成 | CI pipeline | 文件变更时 |
| 2 | 依赖对齐自动验证 | CI 门禁 | PR 提交时 |
| 3 | 施工步骤完成度自动检测 | CI pipeline | 代码提交时 |

---

## §11 产出物存放目录

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\red_blue_validator\blueprint.md` | 本文件 |
| 业务代码 | `D:\ZephyrAlpha\src\zephyr\security\adversarial_validation\` | Python 源码 |
| 攻击场景注册表 | `D:\ZephyrAlpha\src\zephyr\security\adversarial_validation\_scenario-registry.yaml` | REG-RB-001 |
| Constitution 注册表 | `D:\ZephyrAlpha\src\zephyr\security\adversarial_validation\_constitution-registry.yaml` | REG-RB-002 |
| 攻击场景配置 | `D:\ZephyrAlpha\data\red_blue\attack_scenarios.yaml` | 39 场景配置 |
| 稳态指标配置 | `D:\ZephyrAlpha\data\red_blue\steady_state_metrics.yaml` | 35 指标配置 |
| Constitution 配置 | `D:\ZephyrAlpha\data\red_blue\constitution.yaml` | 23 条款配置 |
| Game Day 配置 | `D:\ZephyrAlpha\data\red_blue\game_day_protocol.yaml` | 调度配置 |
| 绕过日志 | `D:\ZephyrAlpha\data\red_blue\bypass_log.yaml` | 绕过记录 |
| 测试代码 | `D:\ZephyrAlpha\tests\red_blue\` | 测试用例 |

代码文件清单：

| # | 文件名 | 对应蓝图章节 | 职责 | 状态 |
|---|--------|------------|------|:---:|
| 1 | `__init__.py` | §3 | 包导出 + __all__ | 已存在（stub） |
| 2 | `attack_registry.py` | §3.1 | 攻击场景加载与索引 | 已存在（stub） |
| 3 | `defense_runner.py` | §3.1 | 蓝方防御验证 | 已存在（stub） |
| 4 | `bypass_recorder.py` | §3.1 | 绕过记录与入库 | 已存在（stub） |
| 5 | `constitution_guard.py` | §3.1 | Constitution 条款管理 | 已存在（stub） |
| 6 | `convergence_checker.py` | §3.1 | 收敛检测 | 已存在（stub） |
| 7 | `game_day_runner.py` | §3.1 | Game Day 调度 | 已存在（stub） |
| 8 | `validator.py` | §4.1 | RedBlueValidator 主类 | 待施工 |
| 9 | `scenario_loader.py` | §3.1 | 攻击场景加载器 | 待施工 |
| 10 | `injection_engine.py` | §3.1 | 攻击注入引擎 | 待施工 |
| 11 | `steady_state.py` | §3.5 | 稳态假设验证器 | 待施工 |
| 12 | `blast_radius.py` | §3.6 | 渐进式爆炸半径 | 待施工 |
| 13 | `cleanup.py` | §3.1 | 清理协议 | 待施工 |
| 14 | `constitution_engine.py` | §3.7 | Constitution Engine | 待施工 |
| 15 | `async_monitor.py` | §3.8 | 零信任 AI Agent 监控 | 待施工 |
| 16 | `ai_attack_generator.py` | §3.1 | AI 攻击场景生成器 | 待施工 |
| 17 | `game_day_scheduler.py` | §3.9 | Game Day 调度器 | 待施工 |
| 18 | `circuit_breaker.py` | §6.1 | CircuitBreaker 熔断器 | 待施工 |
| 19 | `cold_start.py` | §3.1 | 冷启动引导 | 待施工 |
| 20 | `mcp_endpoints.py` | §4.5 | MCP 端点注册 | 待施工 |
| 21 | `cli.py` | §4.5 | CLI 入口 | 待施工 |
|
| 22 | `__main__.py` | §3.1 |   main   | 已实现 | — | 22 | `models.py` | §4.2 | 数据模型 | 待施工 |

---

## §12 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| Audit Orchestrator | 新增接口 | Phase 4 ENFORCE & CLOSE | AuditOrchestrator 调用成功 |
| MCP Servers | 新增端点 | governance.red_blue_scan 等 4 端点 | MCP 端点注册成功 |
| Agent Skill | 新增注册 | red-blue-adversarial Skill | progressive_load 成功 |
| Knowledge Base | 事件订阅 | 绕过模式写入/检索 | kb.search 检索成功 |
| Escalation Protocol | 新增触发 | 3 次绕过升级 | EscalationEngine 触发 |
| Drift Detector | 配置注入 | 攻击基线快照 | drift_engine 记录成功 |
| Agent RBAC | 新增权限 | 攻击操作权限校验 | PermissionGuard 校验通过 |
| Contract Registry | 新增契约 | CT-RB-001~003 | 契约注册成功 |
| Feature Flag | 配置注入 | red_blue_validator 6 个开关 | flags.yaml 读取成功 |
| Capabilities | 新增声明 | CAP-RB-001 | 能力声明注册成功 |
| Skill CBAC | 新增映射 | red-blue-adversarial CBAC | CBAC 映射注册成功 |
| CI/CD Pipeline | 新增 workflow | GitHub Actions | push 触发验证 |
| Session Continuity | 状态保存 | 红白对抗状态 | session 状态恢复成功 |

### 12.1 域契约锚点

| 契约 ID | 本模块角色 | 对端模块 |
|---------|------------|----------|
| G-CT-001 | 消费方（攻击注入操作的 RBAC 权限校验） | MOD-INF-018 |
| G-CT-018 | 提供方（红白对抗结果写入审计链） | MOD-INF-020 |
| G-CT-022 | 消费方（重复绕过触发升级裁决） | MOD-INF-022 |
| G-CT-023 | 消费方（攻击场景基线快照） | MOD-INF-023 |
| G-CT-024 | 提供方（绕过模式写入知识库） | MOD-INF-024 |

---

## §13 需要更新的相关内容

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 模块 ID 注册表 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | MOD-INF-030 条目 | 模块注册 |
| 2 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | red_blue_validator 蓝图条目 | 蓝图注册 |
| 3 | 治理资产清单 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\document-metadata-index-registry.yaml` | MOD-INF-030 元数据 | 资产索引 |
| 4 | 依赖图 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\dependency_path_panorama.md` | 13 条依赖/引用 | 依赖注册 |
| 5 | Agent Skill 注册表 | `D:\ZephyrAlpha\src\zephyr\agent-spec\skill-registry.yaml` | red-blue-adversarial Skill | Skill 发现 |
| 6 | Gate 门禁注册表 | `D:\ZephyrAlpha\src\zephyr\gates\_registry.yaml` | RED-BLUE-GATE 门禁 | 门禁注册 |
| 7 | 脚本清单 | `D:\ZephyrAlpha\scripts\script-manifest.yaml` | red_blue_validator CLI 脚本 | 脚本注册 |
| 8 | 注册表总索引 | `D:\ZephyrAlpha\docs\registry_of_registries.yaml` | REG-RB-001 + REG-RB-002 | 注册表发现 |

---

## §14 已知风险与缓解

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|------|------|---------|------|
| 1 | 攻击注入破坏真实文件且清理失败 | 中 | 高 | backup + atomic rename + ensure_clean() | 风险 |
| 2 | 对抗会话 hang 导致系统不可用 | 中 | 高 | CircuitBreaker 熔断 + max_duration | 风险 |
| 3 | 多 AI session 同时触发对抗造成死锁 | 低 | 高 | 多 Agent 死锁防护 + 锁协议 | 风险 |
| 4 | AI 生成攻击场景包含真实恶意代码 | 中 | 高 | LLM Security + realism_score + RBAC | 风险 |
| 5 | Constitution 条款导致过度防御 | 中 | 中 | 误报率 < 1% + 假阳性自动学习 | 风险 |
| 6 | 攻击场景库被投毒 | 低 | 高 | 基线投毒防护 + 防篡改审计 | 风险 |
| 7 | Game Day SYSTEM 级导致系统崩溃 | 低 | 极高 | 人工确认 + 自动中止 + 灾难恢复 | 风险 |
| 8 | 绕过日志无限增长 | 中 | 低 | 告警疲劳管理 + 日志轮转 | 风险 |
| 9 | 对抗器自身存在 bug | 中 | 高 | 对抗器自指悖论——独立验证路径 | 风险 |
| 10 | Owner 长期离线导致升级无法裁决 | 中 | 中 | Owner 缺席降级策略 | 风险 |
| 11 | 稳态指标度量本身不准确 | 低 | 中 | 稳态指标交叉验证 + 告警可信度评分 | 风险 |
| 12 | 增量攻击场景与内置场景冲突 | 低 | 低 | 场景查重 + scaffold.py 冲突检测 | 风险 |
| 13 | 对抗消耗资源 | 中 | 低 | Warm 平面 < 5min + 资源预算控制 | 负面后果 |
| 14 | Constitution 条款膨胀 | 中 | 中 | 置信度阈值 0.7 + Owner 确认 + 上限 50 条自动合并 | 负面后果 |

---

## §16 施工指引

### AI 施工前检查清单

| # | 检查项 | 确认方式 | 状态 |
|---|--------|---------|:----:|
| 1 | 已读取本蓝图全部内容 | 逐节确认 | ☐ |
| 2 | 已读取必备链接中所有真源文件 | 逐个打开确认 | ☐ |
| 3 | PS-STD-001 编号规则已理解 | 能回答编号规则 | ☐ |
| 4 | GOV-DOC-002 防幻觉路径映射已理解 | 能回答文件该放哪 | ☐ |
| 5 | 每个施工步骤都对应明确的蓝图接口契约 | 逐步骤追溯 | ☐ |
| 6 | §0 代码对齐验证已填写且与实际代码一致 | 逐项核对 | ☐ |

### 16.1 施工策略

| 项目 | 内容 |
|------|------|
| 施工阶段数 | 4 个 Phase |
| 施工模式 | 扩展（从 stub 到完整实现） |
| 核心风险 | 攻击注入破坏真实文件 |
| 目标 generation | 17 — 本次施工将蓝图从规格化升级版升级到实现版 |

### 16.2 前置条件

| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | MOD-GATE_ENGINE Gate Engine 可用 | hard | ☐ | ☐ |
| 2 | MOD-INF-020 Audit Trail 可用 | hard | ☐ | ☐ |
| 3 | MOD-INF-018 Agent RBAC 可用 | hard | ☐ | ☐ |
| 4 | scaffold.py 可用 | hard | ✅ | ✅ |

### 16.3 实施步骤

#### 步骤 1：基础设施（Phase 0）

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 + §4.2 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\security\adversarial_validation\` |
| 验收标准 | 数据模型定义完整 + 攻击场景加载成功 |
| 验证命令 | `python -m pytest tests/red_blue/ -k "test_models or test_scenario_loader" -v` |
| G7 检查项 | 上游依赖全部列出？下游产出物路径精确？回滚方案可执行？ |

**创建文件清单**：

| module_id | 文件名 | doc_type | 完整绝对路径 |
|-----------|--------|----------|------------|
| MOD-INF-030 | models.py | code | `D:\ZephyrAlpha\src\zephyr\security\adversarial_validation\models.py` |
| MOD-INF-030 | scenario_loader.py | code | `D:\ZephyrAlpha\src\zephyr\security\adversarial_validation\scenario_loader.py` |
| MOD-INF-030 | injection_engine.py | code | `D:\ZephyrAlpha\src\zephyr\security\adversarial_validation\injection_engine.py` |

#### 步骤 2：核心引擎（Phase 1）

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\security\adversarial_validation\` |
| 验收标准 | 防御验证+绕过记录+稳态验证+清理+爆炸半径全部实现 |
| 验证命令 | `python -m pytest tests/red_blue/ -k "test_defense or test_bypass or test_steady or test_cleanup or test_blast" -v` |
| G7 检查项 | 同上 |

**修改文件清单**：

| 文件名 | 核心内容 | 必须包含 |
|--------|---------|---------|
| defense_runner.py | 实现 run_defense() 完整逻辑 | Gate 调用 + Check Runner 调用 + 结果判定 |
| bypass_recorder.py | 实现 record_bypass() + query_bypasses() | YAML 写入 + 去重 + 升级触发 |
| steady_state.py | 实现 verify_before/after_attack() | 35 指标度量 + 偏离判定 |
| cleanup.py | 实现 ensure_clean() + cleanup_artifact() | 零残留验证 + backup 恢复 |
| blast_radius.py | 实现 4 级过滤 + 自动中止 | 层级判定 + 阈值中止 |
| validator.py | 实现 RedBlueValidator 主类 | 完整对抗会话流程 |

#### 步骤 3：高级功能（Phase 2）

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 + §4.5 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\security\adversarial_validation\` |
| 验收标准 | Constitution + 零信任 + AI 生成 + Game Day + CircuitBreaker + 冷启动 + MCP + CLI + Skill |
| 验证命令 | `python -m pytest tests/red_blue/ -v` |
| G7 检查项 | 同上 |

#### 步骤 4：系统集成（Phase 3）

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §12 |
| 产出位置 | 多个集成点 |
| 验收标准 | 13 个集成点全部通过 |
| 验证命令 | `python -m pytest tests/red_blue/test_integration.py -v` |
| G7 检查项 | 同上 |

### 16.4 回滚方案

| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| 1 | 数据模型定义错误 | 删除 models.py + 恢复 __init__.py |
| 2 | 核心引擎实现错误 | git checkout 恢复 stub 文件 |
| 3 | 高级功能实现错误 | 删除新增文件 + 恢复 Phase 1 产出 |
| 4 | 集成失败 | 撤销集成注册 + 恢复独立运行 |

### 16.5 施工完成标准

| # | 产出物 | 存放完整绝对路径 | 是否存在 | 内容非空 | §0对齐 |
|---|--------|---------------|:---:|:---:|:---:|
| 1 | models.py | `D:\ZephyrAlpha\src\zephyr\security\adversarial_validation\models.py` | ☐ | ☐ | ☐ |
| 2 | validator.py | `D:\ZephyrAlpha\src\zephyr\security\adversarial_validation\validator.py` | ☐ | ☐ | ☐ |
| 3 | 全部 22 个代码文件 | `D:\ZephyrAlpha\src\zephyr\security\adversarial_validation\` | ☐ | ☐ | ☐ |
| 4 | 全部 12 个测试文件 | `D:\ZephyrAlpha\tests\red_blue\` | ☐ | ☐ | ☐ |

### 16.6 施工状态

| 字段 | 值 | 填写者 |
|------|-----|-------|
| construction_status | partially_implemented | 施工者 |
| verification_status | unverified | 审计者 |
| code_alignment_verified | no | 审计者 |

---

## §17 容量升级附录

> generation≥2 的蓝图 MUST 填写此附录。以下为 v2.0.0 容量升级方案（10,000 脚本 / 100 AI 并发）。

### §17.1 容量基线

| 资源 | 当前基线 | 测量方式 |
|------|---------|---------|
| 模块数 | 51 | module_registry.yaml |
| 治理脚本数 | ~268 | script-manifest.yaml |
| 并发 AI session | ~3 | 运行时监控 |
| 并发脚本执行 | 8 (session-local) | ThreadPoolExecutor |
| LLM Token 预算 | 1M~2M/月 | BudgetEnforcer |

### §17.2 缺口分析

| 缺口 ID | 当前瓶颈 | 升级方案 | 触发阈值 |
|---------|---------|---------|---------|
| GAP-001 | 无脚本注册表与索引 | ScriptRegistry + config/script_registry.yaml | 脚本 > 500 |
| GAP-002 | 无变更→脚本依赖图 | ScriptDependencyGraph + ChangeImpactAnalyzer | 模块 > 200 |
| GAP-003 | 无增量扫描引擎 | IncrementalScanEngine | 脚本 > 500 |
| GAP-004 | session-local ThreadPoolExecutor | 全局 ScriptExecutionPool | AI > 10 |
| GAP-005 | 无并发会话协调器 | SessionCoordinator | AI > 10 |
| GAP-006 | 无 GPU 资源调度 | GPUResourceScheduler | LLM 脚本 > 5 |
| GAP-007 | 无脚本超时与隔离 | Per-script timeout + kill | 脚本 > 1,000 |
| GAP-008 | 无优先级与背压 | 优先级队列 + 背压控制 | AI > 20 |
| GAP-009 | 无全量扫描模式 | FullScanOrchestrator + 分片 + checkpoint | 脚本 > 5,000 |
| GAP-010 | 无脚本拓扑排序 | ScriptTopologySorter + DAG | 脚本 > 1,000 |

### §17.3 升级版本矩阵

| 版本 | generation | 升级类型 | 核心变更 | 代码覆盖 |
|------|:---:|---------|---------|:---:|
| v1.0.0~v1.6.0 | 1~16 | 基线 | 39 攻击场景 + Constitution + Game Day + 全系统集成 | ⚠️ stub |
| v2.0.0 | 17 | 规格化升级 | 蓝图模板 v3.3 对齐 + 压缩工作流 | ⚠️ stub |

### 升级组件清单

| 组件名 | 对应缺口 | 代码文件 | 施工 Phase | 状态 |
|--------|---------|---------|----------|:---:|
| ScriptRegistry | GAP-001 | script_registry.py | Phase 4A | 待施工 |
| ScriptDependencyGraph | GAP-002 | dependency-graph.py | Phase 4C | 待施工 |
| IncrementalScanEngine | GAP-003 | incremental_scan.py | Phase 4D | 待施工 |
| ScriptExecutionPool | GAP-004 | execution_pool.py | Phase 4E | 待施工 |
| GPUResourceScheduler | GAP-006 | gpu_scheduler.py | Phase 4F | 待施工 |
| SessionCoordinator | GAP-005 | session_coordinator.py | Phase 4G | 待施工 |
| FullScanOrchestrator | GAP-009 | full_scan.py | Phase 4H | 待施工 |

### 升级施工路线图

| Phase | 任务 | 产出 | 预估工期 | 依赖 |
|:---:|------|------|:---:|------|
| 4A | 脚本注册表设计 + YAML 搭建 | ScriptRegistry 数据模型 | 2 天 | 无 |
| 4B | 现有 268 脚本迁移入库 | 268 条注册记录 | 1 天 | 4A |
| 4C | ScriptDependencyGraph 实现 | dependency-graph.py | 1.5 天 | 4B |
| 4D | IncrementalScanEngine 实现 | incremental_scan.py | 1 天 | 4C |
| 4E | ScriptExecutionPool（CPU + I/O 池） | execution_pool.py | 1.5 天 | 4B |
| 4F | GPUResourceScheduler + GPU Worker ×2 | gpu_scheduler.py | 1 天 | 4E |
| 4G | SessionCoordinator（去重 + 优先级 + 背压） | session_coordinator.py | 1.5 天 | 4D, 4E |
| 4H | FullScanOrchestrator（分片 + checkpoint） | full_scan.py | 1 天 | 4D |
| 4I | 核心重构：RedBlueValidator → SessionCoordinator | validator.py 门面模式 | 1 天 | 4G |
| 4J | 集成测试：100 AI 并发模拟 | 压力测试脚本 | 1 天 | 4I |
| 4K | 监控 + 告警 + SLO 升级 | §25 升级 | 0.5 天 | 4I |
| 4L | 蓝图同步 | 蓝图文档升级 | 0.5 天 | 4K |

### 升级风险

| 风险 | 概率 | 缓解 |
|------|:---:|------|
| 100 AI 去重窗口 2s 太短/太长 | 中 | 可配置 DEDUP_WINDOW_SECONDS |
| ScriptRegistry 10,000 条加载慢 | 低 | 一次性加载 + pickle cache |
| GPU VRAM 溢出 | 中 | can_accept() 预检查 + 拒绝超大任务 |
| ProcessPoolExecutor Windows 序列化开销 | 中 | I/O 密集型优先 ThreadPoolExecutor |

---

## §18 决策记录

| # | 决策 ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-RB-001 | 采用红白对抗而非纯静态审计 | A 对抗/B 静态 | A | 静态审计无法发现运行时绕过 | 2026-05-08 |
| 2 | D-RB-002 | 攻击场景分 7 Tier | A 分层/B 扁平 | A | 对标 Netflix Simian Army 分层 + OWASP ASI 分类 | 2026-05-08 |
| 3 | D-RB-003 | 引入 Constitution-Based Defense | A Constitution/B 手工补规则 | A | 对标 Microsoft BlueCodeAgent 红队知识驱动蓝队 | 2026-05-08 |
| 4 | D-RB-004 | 渐进式爆炸半径而非全量攻击 | A 渐进/B 全量 | A | 安全约束——从小范围开始 | 2026-05-08 |
| 5 | D-RB-005 | AI 生成攻击场景 | A AI 生成/B 手工 | A | 对标 PyRIT + ASTRA 时空探索 | 2026-05-08 |
| 6 | D-RB-006 | 稳态假设作为攻击前置条件 | A 有/B 无 | A | 对标 Google DiRT 稳态假设原则 | 2026-05-08 |
| 7 | D-RB-007 | 零信任 AI Agent 防线 | A 零信任/B 信任 | A | 对标 UK AISI + OWASP ASI 2026 | 2026-05-08 |
| 8 | D-RB-008 | Game Day 4 频度调度 | A 4频度/B 手动 | A | 对标 Google DiRT 定期演练 | 2026-05-08 |
| 9 | D-RB-009 | 绕过 3 次触发 Escalation | A 3次/B 2次/C 5次 | A | 3 次是重复模式的合理阈值 | 2026-05-08 |
| 10 | D-RB-010 | ThreadPoolExecutor 而非 multiprocessing | A Thread/B Process | A | RULE-SEVEN + I/O 密集型 | 2026-05-08 |
| 11 | D-RB-011 | temp-file + atomic rename 写入 | A 原子/B 直接 | A | RULE-ONE 并发写入安全 | 2026-05-08 |
| 12 | D-RB-012 | 攻击产物 _attack_* 前缀 | A 专用前缀/B 随机 | A | 与 RULE-FIVE _temp* 区分 | 2026-05-08 |
| 13 | D-RB-013 | CircuitBreaker 三态熔断 | A 三态/B 无熔断 | A | 对标 Audit Orchestrator §24 | 2026-05-08 |
| 14 | D-RB-014 | Phase 4 收敛检测取代简单阈值 | A 收敛/B 阈值 | A | Total Audit System v4.0.0 架构 | 2026-05-08 |
| 15 | D-RB-015 | 三类型审计对抗策略 | A 分类型/B 统一 | A | 不同审计类型修复确定性不同 | 2026-05-08 |
| 16 | D-RB-016 | construction_progress 修正为 scaffold | A scaffold/B partially_implemented | A | 代码实际为 stub（pass） | 2026-05-14 |

---

## ⚠️ Vibe Coding 蓝图编写铁律

> **时态属性**：本节属于**施工声明**——AI 进入蓝图修改/施工时必读。不可改为链接引用——AI 不会主动跳转链接读取，删掉 = 失去防漂移防线。本节永久保留在蓝图中。

| # | 铁律 | 违反后果 |
|---|------|---------|
| 1 | 所有路径必须是绝对路径（含盘符 D:\） | 文件创建到错误位置 |
| 2 | 必备链接不可省略 | AI 跳过不读，施工时缺少关键信息 |
| 3 | 蓝图必须是最终设计结果——不记录决策过程 | 蓝图过厚，关键信息被噪音淹没 |
| 4 | 产出物路径必须与 GOV-DOC-002 一致 | 路径幻觉 |
| 5 | 涉及文件范围必须明确列出 | 范围漂移 |
| 6 | 容量估算必须写 | 容量瓶颈 |
| 7 | 迁移/废弃方案必须写 | 断链或垃圾积累 |
| 8 | "待定"/"建议"/"按需"等模糊词禁止使用 | 执行漂移 |
| 9 | 蓝图必须自包含 | 信息缺失 |
| 10 | 删除文件必须遵守安全删除协议 | 永久丢失 |
| 11 | construction_progress 必须与代码实际状态一致 | 虚假进度 |
| 12 | actual_disk_path 必须与 §11 产出物路径一致 | 搜索失败 |
| 13 | 已实现代码不在蓝图中重复——§0.1 标记`已实现`的模块，蓝图只保留接口签名（§4），不复制实现代码 | AI 改蓝图忘改代码，或改代码忘改蓝图 |
| 14 | 临时时态内容执行完毕后从蓝图删除——迁移方案、升级执行计划等临时时态内容，一旦执行完毕即成为历史，从蓝图删除 | 蓝图膨胀，关键信息被历史噪音淹没 |
| 15 | 蓝图内容拆分判定——职责不同→拆分独立蓝图；职责相同→原地升级。判定标准见"蓝图拆分判定标准" | AI 不知道该读哪个蓝图，跨模块影响无法追踪 |

---

## 蓝图拆分判定标准

> 铁律 #15 的操作定义——当蓝图内容超过 ~800 行或包含多个独立职责域时，MUST 执行拆分判定。

### 判定流程

```
STEP 1: 识别职责域
  蓝图中的内容是否属于同一职责域？
  判定标准：该内容的服务对象、变更频率、依赖关系是否与蓝图主体一致？

STEP 2: 职责域判定
  ├ 职责相同（同一模块的升级/扩展）→ 原地升级
  │   条件：服务对象相同 + 变更频率同步 + 依赖关系重叠
  │   操作：在 §17 容量升级附录中增量记录
  │
  └ 职责不同（独立子系统/独立能力域）→ 拆分独立蓝图
      条件（满足任一即触发）：
      a) 有独立的 module_id 前缀（如 CAP-G vs CAP）
      b) 有独立的 Phase 路线图和交付节奏
      c) 有独立的依赖关系图（与蓝图主体的 depends_on 交集 <50%）
      d) 内容超过 100 行且与蓝图主体无直接数据流
      操作：创建子蓝图，本蓝图 §10 依赖关系引用子蓝图

STEP 3: 拆分后验证
  - 拆分出的蓝图 MUST 有独立 frontmatter + 概述 + §0~§18
  - 拆分出的蓝图 belongs_to = 本蓝图 module_id
  - 本蓝图 §10 依赖关系新增子蓝图引用
  - blueprint_registry.yaml 同步更新
```

### 判定示例

| 场景 | 判定 | 理由 |
|------|------|------|
| §17 容量升级组件（ScriptRegistry/ExecutionPool 等） | 原地升级 | 服务对象相同 + 变更频率同步 + 依赖关系重叠 |
| §3.4~3.11 蓝图特有攻击场景体系 | 原地升级 | Red-Blue Validator 核心职责，不可拆分 |

---

## ⚠️ 安全删除协议

> **时态属性**：本节属于**施工声明**——AI 施工涉及删除时必读。永久保留在蓝图中。

本蓝图不涉及文件废弃/迁移/删除。容量升级时（§17），旧 §36 IncrementalCache 将被 IncrementalScanEngine 替换，替换时走 RULE-THREE 三步审判。

### 删除铁律

| # | 铁律 | 原因 |
|---|------|------|
| 1 | 禁止蓝图阶段物理删除任何文件 | 蓝图只做决策，不做执行 |
| 2 | 迁移型删除必须逐条迁移、逐条验证 | 批量迁移容易遗漏 |
| 3 | 物理删除只能在 stable 搬入阶段执行 | deprecated 至少保持 1 个 Phase |
| 4 | 物理删除必须人类确认 | AI 不得自行决定删除文件 |

---

## 必备链接

> **时态属性**：本节属于**施工声明**——AI 进入蓝图时必读。不可改为链接引用——AI 不会主动跳转链接读取，删掉 = 失去上下文防线。永久保留在蓝图中。

| # | 文件 | module_id | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------------|----------|
| 1 | 元数据注册表 | PS-STD-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_043_meta_rule_metadata.yaml` | 编号规则、doc_type 词表 |
| 2 | 目录结构标准 | GOV-DOC-002 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 路径映射 |
| 3 | 治理方法论 | PS-STD-011 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_024_methodology_diagnosis.yaml` | MTH-012 + MTH-013 |
| 4 | 文件命名规范 | GOV-DOC-003 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 命名规则 |
| 5 | 模块 ID 注册表 | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 编号注册 |
| 6 | 架构总览 | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\00-overview.md` | 架构上下文 |
| 7 | 治理规则主注册表 | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\document-metadata-index-registry.yaml` | 现有规则索引 |
| 8 | AI 自治权限注册表 | GOV-AI-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\ai_autonomy_authority_registry.yaml` | AI 操作权限 |

---

## 项目中已有类似功能

| # | 已有模块/文件 | 完整绝对路径 | 功能重叠点 | 为什么不能复用 |
|---|-------------|------------|----------|-------------|
| 1 | Gate Engine | `D:\ZephyrAlpha\src\zephyr\gates\` | 门禁检查 | Gate Engine 是防御判定器，不是对抗验证器——缺少攻击注入/绕过记录/Constitution 学习 |
| 2 | Audit Orchestrator | `D:\ZephyrAlpha\src\zephyr\orchestrator\` | 审计管线 | Orchestrator 是管线编排，Red-Blue 是 Phase 4 收敛验证——职责不同 |

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | red_blue_validator 包 | `D:\ZephyrAlpha\src\zephyr\security\adversarial_validation\` | 业务代码 | 修改（stub→实现） |
| 2 | 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\red_blue_validator\blueprint.md` | 本文件 | 修改 |
| 3 | 测试目录 | `D:\ZephyrAlpha\tests\red_blue\` | 测试代码 | 新建 |
| 4 | 数据目录 | `D:\ZephyrAlpha\data\red_blue\` | 配置/日志 | 新建 |
| 5 | Skill 注册表 | `D:\ZephyrAlpha\src\zephyr\agent-spec\skill-registry.yaml` | Skill 注册 | 修改 |
| 6 | Gate 注册表 | `D:\ZephyrAlpha\src\zephyr\gates\_registry.yaml` | 门禁注册 | 修改 |
| 7 | 脚本清单 | `D:\ZephyrAlpha\scripts\script-manifest.yaml` | 脚本注册 | 修改 |
| 8 | Contract Registry | `D:\ZephyrAlpha\src\zephyr\orchestrator\contract_registry.py` | 契约注册 | 修改 |

---

## 治理信息

### SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| 红蓝对抗验证架构设计 | **本文档 §1-§10** | 已废弃的旧蓝图版本 |
| 施工步骤 | **本文档 §16** | 已废弃的旧施工图 |
| 接口契约 | **本文档 §4** | — |
| 代码文件清单与对齐状态 | **本文档 §0** | blueprint_registry.yaml（派生） |
| 容量升级方案 | **本文档 §17** | 独立升级文档（已废弃） |

**任何与本蓝图冲突的定义，以本蓝图为准。**

### 可观测性与遥测

| 指标名 | 类型 | 说明 |
|--------|------|------|
| red_blue_session_total | Counter | 对抗会话总数 |
| red_blue_scenario_blocked_total | Counter | 被拦截的场景数 |
| red_blue_scenario_bypassed_total | Counter | 被绕过的场景数 |
| red_blue_blocked_rate | Gauge | 当前拦截率 |
| red_blue_session_duration_ms | Histogram | 对抗会话耗时 |
| red_blue_bypass_log_entries | Gauge | 绕过日志条目数 |
| red_blue_constitution_articles | Gauge | Constitution 条款数 |
| red_blue_steady_state_deviations | Gauge | 稳态偏离数 |
| red_blue_circuit_breaker_state | Gauge | 熔断器状态 |

### SLO 定义

| SLO | 目标 | 告警阈值 |
|-----|------|---------|
| 对抗可用性 | 99.9% | < 99% |
| 拦截率（FILE 级） | 100% | < 100% |
| 对抗延迟（FILE 级） | P99 < 120s | P99 > 180s |
| 清理完整性 | 100% | False |
| 稳态偏离 | 0 | > 0 |

### 成功指标

| 指标 | 目标 | 度量方式 |
|------|------|---------|
| 内置场景通过率 | 100% | blocked_rate == 1.0 |
| 绕过场景自动入库率 | 100% | bypass_log 记录数 == 实际绕过数 |
| 攻击产物零残留 | 100% | cleanup_verified == True |
| 完整红白对抗时间（FILE 级） | < 2min | duration_ms |
| Constitution 条款自动提取率 | > 90% | 绕过→条款生成成功率 |
| 稳态假设覆盖率 | 100% | 每个场景都有稳态定义 |
| AI 生成场景现实性 | > 70% | realism_score >= 0.7 |
| Game Day 自动化率 | 100%（FILE/MODULE 级） | 零人工干预 |
| 异步监控检测率 | > 95% | 恶意操作检测率 |
| CI/CD 集成阻断率 | 100% | 绕过→Pipeline 阻断 |
| 注册表登记完整率 | 100% | 8/8 注册表已登记 |

### CLI 入口

```bash
python -m zephyr.red_blue_validator [OPTIONS]
  --blast-radius {FILE|MODULE|CROSS_MODULE|SYSTEM}   爆炸半径（默认 FILE）
  --tier {TIER_1|TIER_2|TIER_3|TIER_4|TIER_5|TIER_6|TIER_7|ALL}   攻击场景层级
  --scenario SCENARIO_ID                             运行指定场景
  --game-day {daily|weekly|monthly}                  Game Day 模式
  --report                                           输出最近报告
  --bypass-log [SCENARIO_ID]                         查询绕过日志
  --constitution [ARTICLE_ID]                        查询 Constitution 条款
  --warn-only                                        自测模式
  --json                                             JSON 输出
  --verbose                                          详细输出
```

### 冷启动策略

| 场景 | 条件 | 行为 |
|------|------|------|
| 全新安装 | data/red_blue/ 不存在 | 创建目录 + 写入默认配置 + 运行 FILE 级验证 |
| 空攻击库 | attack_scenarios.yaml 空 | 从内置 39 个场景恢复 |
| 空绕过日志 | bypass_log.yaml 不存在 | 创建空日志 |
| Constitution 为空 | constitution.yaml 空 | 从内置 23 条初始条款恢复 |
| 依赖缺失 | MOD-GATE_ENGINE/020 不可用 | 降级为"仅场景加载"模式 |

### 告警可信度评分

| 因子 | 权重 | 说明 |
|------|:---:|------|
| 场景来源 | 0.3 | BUILTIN=1.0, BYPASS_DERIVED=0.8, AI_GENERATED=0.6, COMMUNITY=0.5 |
| 稳态偏离幅度 | 0.25 | 偏离越大可信度越高 |
| 重复次数 | 0.25 | 重复越多可信度越高 |
| 防御配置变更 | 0.2 | 最近有防御变更→可信度降低 |

### 崩溃恢复与检查点

1. 检查 checkpoint 文件是否存在
2. 存在 → 加载 → 跳过已完成场景 → 从 pending 继续
3. 不存在 → 从头开始
4. 对抗完成后 → 清理 checkpoint 文件

### 攻守同体悖论与盲测模式

| 措施 | 说明 |
|------|------|
| 盲测模式 | 攻击场景不预先告知防御方——测试/真实标记 |
| 外部攻击库 | 社区贡献的攻击场景——独立于内置库 |
| AI 对抗 AI | L2 Local 生成攻击 → L3 API 验证防御 |
| 已知绕过注入 | 定期注入必然绕过场景验证对抗器正确性 |

### 认知负荷预算

| 维度 | 预算 |
|------|------|
| 月度对抗时间 | ~2.2h/月 |
| 硬上限 | 3h/月 |
| 人工干预 | 仅月度 SYSTEM 级确认 |

### 计算成本估算

| 项目 | 估算 |
|------|------|
| 月度场景执行 | ~980 场景/月 |
| LLM Token 消耗 | ~200K Token/月 |
| 月度成本 | $10-30/月 |

### EU AI Act 合规映射

| 风险级别 | 本模块对应 | 说明 |
|---------|-----------|------|
| 不可接受风险 | §8 安全考量 | 禁止 AI 自我保护攻击 |
| 高风险 | §3.4 攻击场景 + §3.7 Constitution | AI Agent 操作对抗验证 |
| 有限风险 | §3.9 Game Day | 定期对抗验证透明度 |
| 最小风险 | §25 可观测性 | 对抗结果可审计 |

### OWASP ASI 2026 完整映射

| ASI ID | 风险名称 | 攻击场景 | Constitution 条款 |
|--------|---------|:---:|:---:|
| ASI01 | 目标劫持 | RB-008 | ART-008 |
| ASI02 | 工具滥用 | RB-009 | ART-009 |
| ASI03 | 身份冒用 | RB-010 | ART-010 |
| ASI04 | 供应链投毒 | RB-011 | ART-011 |
| ASI05 | 数据投毒 | RB-011b | ART-011b |
| ASI06 | 记忆投毒 | RB-012 | ART-012 |
| ASI07 | 拒绝服务 | RB-012b | ART-012b |
| ASI08 | 级联故障 | RB-013 | ART-013 |
| ASI09 | 信任利用 | RB-014 | ART-014 |
| ASI10 | Rogue Agent | RB-015 | ART-015 |
| ASI11 | 不可追踪 | RB-016 | ART-016 |

### 注册登记清单

| # | 注册表 | 登记内容 | 状态 |
|---|--------|---------|:---:|
| 1 | module_registry.yaml | MOD-INF-030 条目 | ✅ |
| 2 | blueprint_registry.yaml | red_blue_validator 蓝图条目 | ✅ |
| 3 | cross-module-dependency-registry.yaml | 13 条依赖/引用 | ✅ |
| 4 | agent-spec/skill-registry.yaml | red-blue-adversarial Skill | ❌ 施工后登记 |
| 5 | gates/_registry.yaml | RED-BLUE-GATE 门禁 | ❌ 施工后登记 |
| 6 | script-manifest.yaml | red_blue_validator CLI 脚本 | ❌ 施工后登记 |
| 7 | red_blue_validator/__init__.py | __all__ 导出 | ❌ 施工后登记 |
| 8 | registry_of_registries.yaml | REG-RB-001 + REG-RB-002 | ✅ |

### 新增注册表

| 注册表 ID | 名称 | 路径 | 说明 |
|-----------|------|------|------|
| REG-RB-001 | 攻击场景注册表 | `D:\ZephyrAlpha\src\zephyr\security\adversarial_validation\_scenario-registry.yaml` | 39 攻击场景 |
| REG-RB-002 | Constitution 条款注册表 | `D:\ZephyrAlpha\src\zephyr\security\adversarial_validation\_constitution-registry.yaml` | 23 Constitution 条款 |

### 错误码目录

| 错误码 | 说明 | HTTP 状态 |
|--------|------|:---:|
| RB-ERR-001 | 攻击注入权限不足 | 403 |
| RB-ERR-002 | 文件被锁定无法注入 | 423 |
| RB-ERR-003 | 对抗会话超时 | 504 |
| RB-ERR-004 | CircuitBreaker 熔断中 | 503 |
| RB-ERR-005 | 稳态偏离超阈值 | 500 |
| RB-ERR-006 | 依赖模块不可用 | 503 |
| RB-ERR-007 | 攻击场景不存在 | 404 |
| RB-ERR-008 | Constitution 条款冲突 | 409 |
| RB-ERR-009 | 攻击产物清理失败 | 500 |
| RB-ERR-010 | 收敛检测失败 | 500 |

### 日志规范

| 级别 | 用途 |
|------|------|
| DEBUG | 攻击注入细节 |
| INFO | 对抗会话开始/结束 |
| WARNING | 绕过发现 |
| ERROR | 防御验证失败 |
| CRITICAL | 稳态偏离/系统不可用 |

### 数据保留策略

| 数据类型 | 保留期 | 清理方式 |
|---------|--------|---------|
| 对抗会话报告 | 90 天 | 自动清理 |
| 绕过日志 | 永久 | 聚合去重后保留 |
| Constitution 条款 | 永久 | 废弃→归档 |
| 检查点文件 | 对抗完成后立即清理 | 自动清理 |
| 攻击产物 | 对抗完成后立即清理 | 自动清理 |

### 优雅关机

| 信号 | 行为 |
|------|------|
| SIGINT | 停止接受新对抗 → 等待当前场景完成 → 清理 → 退出 |
| SIGTERM | 同 SIGINT |
| Kill Switch | 立即停止所有对抗 → 清理 → 退出 |

### 代码变更自动触发

| 变更路径 | 触发 Tier | 说明 |
|---------|:---:|------|
| src/zephyr/**/*.py | TIER_1 | Python 代码变更 |
| scripts/**/*.py | TIER_1 | 脚本变更 |
| src/zephyr/governance/rule_enforcement/** | TIER_1 + TIER_2 | Gate 变更触发 AI Agent 特攻 |
| .claude/settings.json | TIER_2 | AI Agent 配置变更 |
| _registry.yaml | TIER_1 | 注册表变更 |
| requirements.txt | TIER_2 | 依赖变更 |
