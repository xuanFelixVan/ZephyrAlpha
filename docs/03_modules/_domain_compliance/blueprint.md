---
module_id: MOD-L10-001
submodule_path: src/zephyr/compliance
title: "Compliance Core 蓝图+施工图 — 合规引擎"
doc_type: blueprint
status: Active
version: "2.1.0"
layer: L1_foundation
layer_name: compliance
functional_domain: compliance
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-05"
valid_from: "2026-05-12"
ttl: permanent
construction_progress: partially_implemented
actual_disk_path: "src/zephyr/compliance/"
belongs_to: "MOD-MASTER_BLUEPRINT"
parent_module: ""
codification_level: L1
codification_at: "2026-05-14"
last_verified: "2026-05-15"
last_updated: "2026-05-15"
generation: 2
rule_form: structural
scope: module
stability: evolving
verifiability: manual
summary: "合规引擎——SecurityGateway+ComplianceEngine OCP扩展点+AISG Sandbox+ArtifactScanner。Phase B骨架已就位，核心抽象和实现已定义。"
tags: [compliance, l10, security-gateway, artifact-scanner]
priority: P0
runtime_plane: warm
ssot_yaml: "architecture_model/layers/l10_compliance.yaml"
references:
  - path: "D:\\ZephyrAlpha\\architecture_model\\layers\\l10_compliance.yaml"
    section: "全篇"
    why: "YAML SSoT"
  - path: "D:\\ZephyrAlpha\\docs\\02_enterprise_architecture\\04_architecture_principles_decisions\\dependency_path_panorama.md"
    section: "§5 模块归属表 + §2.7 线7 + §3.16 权限判定链"
    why: "全局依赖图对齐"
depends_on:
  - target: MOD-DATABASE
    at: "§10"
    why: "合规规则存储"
  - target: MOD-INF-020
    at: "§10"
    why: "审计决策写入"
  - target: MOD-INF-018
    at: "§10"
    why: "权限联动"
responsibility_domain: 
design_maturity: prototype
build_status: generated
---

> ⚠️ **业务层已开放，可施工** — D_COMPLIANCE 属于 C 轨 T2-deferred 层，当前阶段仅做设计审查和代码验证，不开放新功能施工。

> module_id: MOD-L10-001 | version: 2.1.0 | status: Active | layer: L1_foundation
> actual_disk_path: src/zephyr/compliance/ | generation: 2 | construction_progress: partially_implemented

# Compliance Core 蓝图+施工图 — 合规引擎

> **真源声明**：本蓝图是 ZephyrAlpha 合规引擎体系的唯一真源。

## 概述

本蓝图描述 ZephyrAlpha 合规引擎——它解决了 AI 指令执行的安全拦截与合规规则可扩展性问题。核心职责包括：SecurityGateway OCP 扩展点（L1/L2/L3 三层防御）、ComplianceEngine OCP 扩展点（合规规则管理）、AISG Sandbox（模式匹配测试器）、ArtifactScanner（S-01~S-06 多类别安全扫描）。当前规模 4 个核心组件 + 1 个实现类，目标容量支持安全网关 QPS 100/s、Artifact 扫描 500 文件/次。上游依赖 INF-012 Database（规则存储）、INF-020 Audit Trail（审计写入）、INF-018 Agent RBAC（权限联动），下游被 D_RISK Risk Management、D_EXECUTION_CORE Trade Execution 消费。

---

> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图+施工图模板：[blueprint-construction-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-construction-template.md)
> - AI 压缩工作流标准：[trae_030_doc_numbering_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)
> - 代码头部标准：[code-construction-standards.md §7](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)
> - 依赖图：[dependency_path_panorama.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/04_architecture_principles_decisions/dependency_path_panorama.md)
> - 优化规则：先 Layer 1（蓝图+施工图模板合规）→ 后 Layer 2（规格化砍削）

---

## §0 代码对齐验证

### §0.1 代码文件清单

<!-- AUTOGEN: source=depgraph.nodes, generator=extract_depgraph.py, reconciler=blueprint_frontmatter_reconciler.py -->
> **⚠️ 自动化提示**：文件清单真源在 PostgreSQL depgraph.nodes 表，本节手写内容可能过时。
> 查询最新文件清单：`python scripts/governance/extract_depgraph.py --modules MOD-L10-001`
> 以下手写内容保留职责描述（depgraph 无此信息），文件列表以 depgraph 为准。

> **架构归属SSoT**：见 AGENTS.md §7「代码规范」（depgraph SSoT 真源唯一指针）
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[DOMAIN]/[DEPENDENCIES]/[CONSUMERS]/[STARTUP]/[MATURITY]/[INVARIANTS]/[MODIFY-GUARD]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]/[TTL]` — 见防幻觉十八条

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-L10-001`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 | 阻塞原因 |
|---|--------|------------|------|:---:|--------|
| 1 | __init__.py | §3.1 | 包导出 | 已实现 | — |
| 2 | security_gateway_base.py | §3.1 | SecurityGateway抽象 + AuditAction + AuditDecision | 已实现 | — |
| 3 | compliance_manager.py | §3.1 | ComplianceManagerBase + ComplianceRule | 已实现 | — |
| 4 | aisg_sandbox.py | §3.1 | AISGSandbox模式匹配测试器 | 已实现 | — |
| 5 | artifact_scanner.py | §3.1 | ArtifactScanner + ArtifactFinding + ScanReport | 已实现 | — |
| 6 | default_security_gateway.py | §3.1 | DefaultSecurityGateway导出兼容层 | 已废弃 | — |
| 7 | implementations/__init__.py | §3.1 | 子包导出 | 已实现 | — |
| 8 | implementations/default_security_gateway.py | §3.1 | DefaultSecurityGateway实际实现 | 未实现（文件不存在） | — |

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = partially_implemented → 已实现章节的代码存在 | 按章节核对 | ☐ |
| 蓝图描述的类/函数名 = 代码中的类/函数名 | `grep "class\|def" *.py` | ☐ |
| artifact_scanner.py 存在于磁盘但未在 YAML SSoT 中注册 | `cat architecture_model/layers/l10_compliance.yaml` | ☐ |
| default_security_gateway.py 根目录与 implementations/ 重复 | `diff default_security_gateway.py implementations/default_security_gateway.py` | ☐ |

### §0.3 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v1.0.0 (基线) | SecurityGateway + ComplianceEngine + AISGSandbox + ArtifactScanner + DefaultSecurityGateway | — | — |
| v2.0.0 (模板v3.3重构) | 同 v1.0.0 + 章节重排+新增概述+标准锚点+AI施工前检查清单 | — | 结构重组，无功能变更 |

---

### §0.6 四图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从四图真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-L10-001`

#### 四图位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-L10-001` 的 19 个 file 节点 | prototype | `extract_depgraph.py --modules MOD-L10-001` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-L10-001 | MOD-L10-001 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | generated | generated | ✅ |
| file_count | 19 文件 | 8 文件（§0.1） | ❌ |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## §1 设计背景与目标

### 1.1 背景

AI 指令执行路径缺乏统一安全拦截机制——不同模块各自实现安全检查，导致：①安全策略不一致 ②新增安全规则需修改多个模块 ③审计追踪不完整。合规层（D_COMPLIANCE）作为系统权限判定链第④步（dependency_path_panorama §3.16），负责在 AI 指令执行前进行合规检查（CTR-P1-012），拦截不合规指令并生成审计决策。

### 1.2 目标范围

| # | 类型 | 内容 | 标准/原因 |
|---|:----:|------|----------|
| 1 | ✅ 包含 | AI安全网关 | SecurityGateway OCP扩展点可用 |
| 2 | ✅ 包含 | 合规规则引擎 | ComplianceEngine OCP扩展点可用 |
| 3 | ✅ 包含 | AISG沙箱测试 | AISGSandbox模式匹配可运行 |
| 4 | ✅ 包含 | Artifact安全扫描 | ArtifactScanner S-01~S-06检测类别可用 |
| 5 | ❌ 排除 | 数据存储引擎 | 基础设施 INF-012 Database 负责 |
| 6 | ❌ 排除 | 审计日志存储 | INF-020 Audit Trail 负责 |
| 7 | ❌ 排除 | 权限判定 | INF-018 Agent RBAC 负责 |

### 1.3 运行场景约束

| 约束 | 影响 |
|------|------|
| SecurityGateway 在 AI 指令执行路径上同步调用 | 拦截延迟直接影响指令执行延迟，必须 <100ms |
| ArtifactScanner 在 CI/CD Pipeline 中异步调用 | 扫描时间不影响构建流水线主路径 |
| AISG 模式匹配基于正则表达式 | 复杂模式可能导致误报，需可配置白名单 |
| ComplianceRule 数据类来自 shared/contracts/risk | 接口变更需同步 D_RISK/D_EXECUTION_CORE |
| D_COMPLIANCE 属于 C 轨线7 T2 | C轨占位已解除[ARCH-045 P0]，可施工 |

### 1.5 利益相关者映射

| 角色 | 关注点 | 参与阶段 | 约束 |
|------|--------|---------|------|
| Owner | 架构决策、破坏性变更审批 | 设计+施工 | 审批权限 |
| D_RISK Risk Management | CTR-P1-012 ComplianceRule 消费 | 集成 | 接口兼容 |
| D_EXECUTION_CORE Trade Execution | CTR-P1-012 ComplianceRule 消费 | 集成 | 接口兼容 |
| INF-020 Audit Trail | AuditDecision 写入 | 集成 | 审计格式兼容 |
| CI/CD Pipeline | ArtifactScanner 调用 | 运行 | 门禁配置 |

### 1.6 当前态/目标态差距

| 维度 | 当前态 | 目标态 | 差距 | 优先级 |
|------|--------|--------|------|:------:|
| 安全网关 | DefaultSecurityGateway 两套实现 | 统一到 implementations/ | 根目录版本需废弃 | P1 |
| YAML SSoT | artifact_scanner.py 未注册 | 全部代码文件注册 | 孤儿文件 | P1 |
| 合规规则 | ComplianceManagerBase 骨架 | CTR-P1-012 可被 D_RISK/D_EXECUTION_CORE 消费 | 规则评估逻辑未完善 | P2 |
| 可观测性 | 无监控指标 | §6.1 指标已埋点 | 未实现 | P2 |

### 1.7 典型场景

| 场景 | 触发 | 处理流程 | 输出 |
|------|------|---------|------|
| AI指令安全拦截 | AI指令执行请求 | SecurityGateway.pre_filter → security-scan → decide | AuditDecision(allow/deny/flag) |
| Artifact安全扫描 | CI/CD Pipeline触发 | ArtifactScanner.scan → S-01~S-06检测 | ScanReport |
| 合规规则评估 | D_RISK/D_EXECUTION_CORE请求合规检查 | ComplianceManagerBase.evaluate | ComplianceResult |

---

## §2 模块边界

### 2.1 职责边界

| # | 类型 | 职责 | 具体内容 | 负责方 |
|---|:----:|------|---------|--------|
| 1 | ✅ | AI安全网关 | SecurityGateway抽象 + DefaultSecurityGateway实现（L1 Prompt Injection + L2 危险代码 + L3 审计追踪） | D_COMPLIANCE |
| 2 | ✅ | 合规规则引擎 | ComplianceEngine抽象 + ComplianceManagerBase + ComplianceRule | D_COMPLIANCE |
| 3 | ✅ | AISG沙箱 | AISGSandbox模式匹配测试器 | D_COMPLIANCE |
| 4 | ✅ | Artifact扫描 | ArtifactScanner（S-01~S-06多类别安全扫描） | D_COMPLIANCE |
| 5 | ❌ | 数据持久化 | — | INF-012 Database |
| 6 | ❌ | 权限控制 | — | INF-018 Agent RBAC |
| 7 | ❌ | 审计日志写入 | — | INF-020 Audit Trail |

---

## §3 架构设计

### 3.1 组件架构

| # | 组件 | 职责 | 依赖 | 交互方式 |
|---|------|------|------|---------|
| 1 | SecurityGateway（抽象） | 定义安全网关OCP扩展点 | — | 同步调用 |
| 2 | DefaultSecurityGateway | L1/L2/L3三层防御实现 | SecurityGateway, INF-020 | 同步调用 |
| 3 | ComplianceEngine（抽象） | 定义合规规则OCP扩展点 | — | 同步调用 |
| 4 | ComplianceManagerBase | 合规规则管理基类 | ComplianceEngine, shared/contracts/risk | 同步调用 |
| 5 | AISGSandbox | 模式匹配测试器 | SecurityGateway | 同步调用 |
| 6 | ArtifactScanner | S-01~S-06多类别安全扫描 | — | 异步调用（CI/CD） |

### 3.2 数据流

| # | 上游 | 处理逻辑 | 下游 | 数据格式 |
|---|--------|---------|---------|---------|
| 1 | AI指令输入 | SecurityGateway三层拦截 | 指令执行器 / 拦截拒绝 | AuditDecision |
| 2 | ComplianceRule定义 | ComplianceManagerBase规则管理 | D_RISK/D_EXECUTION_CORE消费 | ComplianceRule |
| 3 | AI指令输入 | AISGSandbox模式匹配 | SecurityGateway | bool + 拦截原因 |
| 4 | Artifact文件 | ArtifactScanner多类别扫描 | ScanReport | ScanReport |

### 3.3 状态生命周期

本模块无状态机。所有组件为无状态函数式调用，每次请求独立处理。

---

## §4 接口契约

### 4.1 公共 API

| 类 | 方法 | 输入 | 输出 | 核心逻辑 |
|---|------|------|------|---------|
| SecurityGateway | `check(instruction)` | AI指令字符串 | AuditDecision | 抽象方法，子类实现拦截逻辑 |
| DefaultSecurityGateway | `check(instruction)` | AI指令字符串 | AuditDecision | L1 Prompt Injection → L2 危险代码 → L3 审计追踪 |
| ComplianceManagerBase | `evaluate(rule, context)` | ComplianceRule + 上下文 | ComplianceResult | 规则评估基类 |
| AISGSandbox | `test(instruction)` | AI指令字符串 | (bool, reason) | 模式匹配检测 |
| ArtifactScanner | `scan(artifact_path)` | Artifact路径 | ScanReport | S-01~S-06多类别扫描 |

### 4.2 数据模型

| 模型 | 字段 | 类型 | 说明 |
|------|------|------|------|
| AuditDecision | decision | str | allow/deny/escalate |
| AuditDecision | reason | str | 决策原因 |
| AuditDecision | layer | str | L1/L2/L3 |
| AuditAction | action_type | str | 动作类型 |
| AuditAction | timestamp | datetime | 时间戳 |
| ComplianceRule | rule_id | str | 规则ID |
| ComplianceRule | description | str | 规则描述 |
| ComplianceRule | severity | str | 严重级别 |
| ArtifactFinding | category | str | S-01~S-06 |
| ArtifactFinding | severity | str | 严重级别 |
| ArtifactFinding | description | str | 发现描述 |
| ScanReport | findings | list[ArtifactFinding] | 扫描结果列表 |
| ScanReport | scanned_path | str | 扫描路径 |

### 4.3 输入契约

| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| `SecurityGateway.check()` | `instruction` | ✅ | 非空字符串，≤10000字符 |
| `ComplianceManagerBase.evaluate()` | `rule` | ✅ | ComplianceRule实例 |
| `ComplianceManagerBase.evaluate()` | `context` | ✅ | dict，包含评估上下文 |
| `AISGSandbox.test()` | `instruction` | ✅ | 非空字符串 |
| `ArtifactScanner.scan()` | `artifact_path` | ✅ | 绝对路径，文件必须存在 |

### 4.4 输出契约

| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| `SecurityGateway.check()` | `AuditDecision`：decision=allow/deny/escalate | `SecurityGatewayError` |
| `ComplianceManagerBase.evaluate()` | `ComplianceResult`：合规/不合规 | `ComplianceEvaluationError` |
| `AISGSandbox.test()` | `(bool, reason)`：是否安全+原因 | `AISGSandboxError` |
| `ArtifactScanner.scan()` | `ScanReport`：扫描结果列表 | `ArtifactScanError` |

### 4.5 MCP 接口

本模块不暴露 MCP 接口。

### 4.6 契约版本

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| 新增检测类别（S-07+） | ✅ 向后兼容 | 不影响已有消费者 |
| 新增SecurityGateway实现 | ✅ 向后兼容 | OCP扩展点 |
| 删除/重命名ComplianceRule字段 | ❌ 破坏性 | 需Owner审批 + 通知D_RISK/D_EXECUTION_CORE |
| 修改AuditDecision结构 | ❌ 破坏性 | 需Owner审批 |

**变更通知**：破坏性变更→Owner审批+蓝图minor+1。兼容性变更→AI自主+patch+1。

---

## §5 约束条件

### 5.1 技术约束

| # | 约束 | 值 |
|---|------|------|
| 1 | SecurityGateway为OCP扩展点 | 新安全策略只加不改 |
| 2 | ComplianceEngine为OCP扩展点 | 新合规规则只加不改 |
| 3 | INV-015: AISG拦截门禁 | 任何跳过AISG的AI指令执行均违反此不变量 |
| 4 | ArtifactScanner独立于SecurityGateway | 可在CI/CD pipeline中独立使用 |

### 5.2 容量估算

| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|:------:|:------:|:------:|:------:|---------|
| 安全网关QPS | 10/s | 100/s | 1000/s | ✅ | 异步拦截队列 |
| Artifact扫描文件数 | 50/次 | 500/次 | 5000/次 | ✅ | ThreadPoolExecutor并行扫描 |
| ComplianceRule数量 | 10 | 100 | 1000 | ✅ | 规则索引优化 |
| AISG模式规则数 | 20 | 200 | 2000 | ✅ | 模式编译缓存 |

### 5.3 迁移/废弃方案

| # | 废弃/迁移对象 | 当前位置 | 目标位置 | 处理方式 | 引用更新方案 |
|---|-------------|---------|---------|---------|------------|
| 1 | default_security_gateway.py（根目录） | `D:\ZephyrAlpha\src\zephyr\compliance\default_security_gateway.py` | 删除 | 迁移+重定向→标记deprecated→Phase4物理删除 | Grep全项目import引用→更新为implementations/路径 |

### 5.4 非功能需求与服务水平

| 维度 | NFR指标 | NFR目标 | 测量方式 | SLI | SLO | Error Budget | 告警阈值 |
|------|--------|--------|---------|-----|-----|-------------|---------|
| 可用性 | SecurityGateway拦截成功率 | 99.9% | 监控日志 | 拦截成功/总请求数 | 99.9% | 每月允许失败≤43min | 失败率>0.5% |
| 延迟 | SecurityGateway同步拦截延迟 | <100ms | 计时埋点 | P99延迟 | <100ms | — | P99>150ms |
| 可维护性 | MTTR | <30min | 故障记录 | — | — | — | — |
| 可观测性 | 指标覆盖率 | 100% | 指标审计 | — | — | — | — |

### 5.7 禁止模式与导入约束

| # | 类型 | 禁止项 | 替代/允许项 | 原因 |
|---|:----:|--------|-----------|------|
| 1 | 编码模式 | 直接 `open(path, "w")` 写文件 | temp-file + `os.replace()` 原子写入 | RULE-ONE |
| 2 | 编码模式 | `for + subprocess.run()` 串行执行 | `ThreadPoolExecutor(max_workers=8)` | RULE-SEVEN |
| 3 | 编码模式 | `@dataclass` 用于数据模型 | `Pydantic V2 BaseModel` | KBG-0040 |
| 4 | 导入源 | `from zephyr.risk.*` 直接导入 | 通过 CTR-P1-012 契约交互 | 分层约束 |
| 5 | 导入源 | `from zephyr.ex_core.*` 直接导入 | 通过 CTR-P1-012 契约交互 | 分层约束 |

---

## §6 错误处理

| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | SecurityGateway拦截异常 | try/except捕获SecurityGatewayError | 降级为deny+审计记录 | AI指令执行中断 |
| 2 | ArtifactScanner扫描文件不存在 | FileNotFoundError | 返回空ScanReport+警告日志 | CI/CD门禁跳过该文件 |
| 3 | ComplianceRule执行异常 | try/except捕获ComplianceEvaluationError | 降级为不合规+审计记录 | 下游D_RISK/D_EXECUTION_CORE收到不合规结果 |
| 4 | AISG模式匹配超时 | 正则执行超时检测 | 降级为deny+审计记录 | AI指令被拦截 |
| 5 | 审计日志写入失败 | INF-020 Audit Trail返回错误 | 本地缓存+重试 | 审计记录延迟 |

### 6.1 可观测性规格

| 指标名 | 类型 | 采集方式 | 告警阈值 | 告警级别 |
|--------|------|---------|---------|---------|
| l10_security_gateway_requests_total | Counter | 自动埋点 | — | — |
| l10_security_gateway_blocked_total | Counter | 自动埋点 | 阻断率>10% | P2 |
| l10_security_gateway_latency_p99 | Histogram | 计时埋点 | >150ms | P1 |
| l10_artifact_scanner_scan_total | Counter | 自动埋点 | — | — |
| l10_artifact_scanner_findings_total | Counter | 自动埋点 | 高危发现>0 | P1 |
| compliance_evaluation_total | Counter | 自动埋点 | 不合规率>50% | P2 |

### 6.2 退化矩阵

| 组件 | 失败后可用功能 | 不可用功能 | 降级策略 | 恢复条件 |
|------|-------------|-----------|---------|---------|
| SecurityGateway | deny-all（安全优先） | 允许指令通过 | 降级为deny+审计记录 | 异常解除 |
| AISGSandbox | deny-all | 模式匹配检测 | 降级为deny+审计记录 | 正则引擎恢复 |
| ArtifactScanner | 跳过该文件扫描 | 完整安全扫描 | 返回空ScanReport+警告 | 文件路径恢复 |
| ComplianceEngine | 返回不合规 | 规则评估 | 降级为不合规+审计记录 | 规则引擎恢复 |

---

## §8 安全考量

| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | AI指令绕过AISG拦截（INV-015违反） | 高 | SecurityGateway强制调用链+审计追踪 | 单元测试验证无AISG跳过路径 |
| 2 | Prompt Injection攻击 | 高 | DefaultSecurityGateway L1层拦截 | 集成测试覆盖已知注入模式 |
| 3 | ArtifactScanner扫描绕过 | 中 | CI/CD门禁强制调用 | Pipeline配置验证 |
| 4 | 合规规则注入 | 中 | ComplianceRule类型校验+白名单 | 输入校验测试 |

---

## §9 测试策略

| # | 测试类型 | 覆盖范围 | 关键测试用例 | 通过标准 |
|---|---------|---------|------------|---------|
| 1 | 单元测试 | SecurityGateway + DefaultSecurityGateway | L1 Prompt Injection拦截、L2 危险代码拦截、L3 审计追踪 | 覆盖率≥80% |
| 2 | 单元测试 | ComplianceManagerBase + ComplianceRule | 规则评估、规则注册、规则查询 | 覆盖率≥80% |
| 3 | 单元测试 | AISGSandbox | 模式匹配命中、模式匹配未命中、白名单 | 覆盖率≥80% |
| 4 | 单元测试 | ArtifactScanner | S-01~S-06各类别扫描、空文件、大文件 | 覆盖率≥80% |
| 5 | 集成测试 | D_RISK Risk Management ← CTR-P1-012 | ComplianceRule可被D_RISK消费 | 端到端通过 |
| 6 | 集成测试 | D_EXECUTION_CORE Trade Execution ← CTR-P1-012 | ComplianceRule可被D_EXECUTION_CORE消费 | 端到端通过 |
| 7 | 集成测试 | INF-020 Audit Trail ← AuditDecision | 审计决策可追溯 | 端到端通过 |

---

## §10 依赖关系

### §10.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| INF-012 Database | 可选 | 合规规则存储 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\database\blueprint.md` |
| INF-020 Audit Trail | 必须 | 审计决策写入 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\audit-trail\blueprint.md` |
| INF-018 Agent RBAC | 可选 | 权限联动 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\agent-rbac\blueprint.md` |
| shared/contracts/risk | 必须 | ComplianceRule数据类 | — | `D:\ZephyrAlpha\src\zephyr\shared\contracts\risk.py` |

### §10.2 依赖图对齐声明

| 对齐项 | 对齐状态 | 说明 |
|--------|:---:|------|
| §10.1 依赖声明 ↔ dependency_path_panorama.md | 未对齐 | 待验证 |
| §10.1 依赖声明 ↔ cross_layer_contracts.yaml | 未对齐 | 待验证 |
| §10.1 依赖声明 ↔ 下游蓝图 §10 | 未对齐 | 待验证 |

### §10.3 内部依赖图

**执行顺序依赖**：

| 上游步骤 | 下游步骤 | 依赖关系 |
|---------|---------|---------|
| 无内部依赖 | — | — |

**数据流依赖**：

| 数据生产者 | 数据消费者 | 数据格式 |
|-----------|-----------|---------|
| 无内部依赖 | — | — |

### §10.4 自动化规格

| 项目 | 内容 |
|------|------|
| 是否需要自动化依赖检查 | 否 |
| 如何实现 | — |
| 触发方式 | — |

---

## §11 产出物存放目录

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_domain_compliance\blueprint.md` | 本文件（含设计和施工指引） |
| 业务代码 | `D:\ZephyrAlpha\src\zephyr\compliance\` | Python 源码 |
| 测试代码 | `D:\ZephyrAlpha\tests\compliance\` | 测试用例 |

| 产出物 | 绝对路径 |
|--------|---------|
| SecurityGateway + ComplianceEngine + AuditAction + AuditDecision | `D:\ZephyrAlpha\src\zephyr\compliance\security_gateway_base.py` |
| ComplianceManagerBase + ComplianceRule | `D:\ZephyrAlpha\src\zephyr\compliance\compliance_manager.py` |
| AISGSandbox | `D:\ZephyrAlpha\src\zephyr\compliance\aisg_sandbox.py` |
| ArtifactScanner + ArtifactFinding + ScanReport | `D:\ZephyrAlpha\src\zephyr\compliance\artifact_scanner.py` |
| DefaultSecurityGateway（导出兼容层） | `D:\ZephyrAlpha\src\zephyr\compliance\default_security_gateway.py` |
| DefaultSecurityGateway（实际实现） | `D:\ZephyrAlpha\src\zephyr\compliance\implementations\default_security_gateway.py` |
| 契约违反错误 | `D:\ZephyrAlpha\src\zephyr\shared\contracts\errors\contract_violation_error.py` | 契约违反异常（归属 MOD-INF-016） |

---

## §12 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| D_RISK Risk Management | 新增接口 | CTR-P1-012 ComplianceRule | 风险管理可消费合规规则 |
| D_EXECUTION_CORE Trade Execution | 新增接口 | CTR-P1-012 ComplianceRule | 交易执行可消费合规规则 |
| INF-020 Audit Trail | 修改现有接口 | AuditDecision写入 | 审计决策可追溯 |
| CI/CD Pipeline | 配置注入 | ArtifactScanner | 代码审查门禁可扫描artifact |
| 权限判定链（dependency_path_panorama §3.16） | ④ 合规检查 | CTR-P1-012 | 指令执行前合规拦截 |

---

## §13 需要更新的相关内容

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | blueprint_registry.yaml | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | construction_progress更新; name统一为compliance_core | 进度更新+命名统一(ARB-21) |
| 2 | l10_compliance.yaml | `D:\ZephyrAlpha\architecture_model\layers\l10_compliance.yaml` | 补充 artifact_scanner.py + implementations/ 子目录 | 消除孤儿文件 |

---

## §14 已知风险与缓解

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|------|------|------|---------|------|
| 1 | artifact_scanner.py未注册到YAML | 高 | 孤儿文件 | 需补充到SSoT YAML | 风险 |
| 2 | default_security_gateway.py根目录与implementations/重复 | 中 | 维护分裂 | 根目录版本应仅为导出兼容层 | 风险 |
| 3 | AISG模式匹配误报 | 中 | 合法操作被拦截 | 可配置白名单 + 审计追踪 | 风险 |
| 4 | 新安全策略需实现SecurityGateway | — | — | — | 负面后果 |
| 5 | 增加扫描延迟 | — | — | — | 负面后果 |
| 6 | 接口变更需Owner审批 | — | — | — | 负面后果 |

---

## §16 施工指引

### ⚠️ AI 施工前检查清单

| # | 检查项 | 确认方式 | 状态 |
|---|--------|---------|:----:|
| 1 | 已读取本蓝图全部内容（概述 + §1-§15 架构 + §0 对齐 + §16 施工指引） | 逐节确认 | ☐ |
| 2 | 已读取必备链接中所有真源文件 | 逐个打开确认 | ☐ |
| 3 | PS-STD-001 编号规则已理解 | 能回答"GOV-SEC-001是什么" | ☐ |
| 4 | GOV-DOC-002 防幻觉路径映射已理解 | 能回答"某类文件该放哪" | ☐ |
| 5 | 每个施工步骤都对应明确的蓝图接口契约（§4） | 逐步骤追溯 | ☐ |
| 6 | §0 代码对齐验证已填写且与实际代码一致 | 逐项核对 | ☐ |

### 16.1 施工策略

| 项目 | 内容 |
|------|------|
| 施工阶段数 | 2 个 Phase |
| 施工模式 | 扩展 |
| 核心风险 | AISG拦截准确性 |
| 目标 generation | 2 — 本次从 generation 1 升级到 generation 2（模板v3.3重构） |

### 16.2 前置条件

| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | SecurityGateway定义 | hard | 已实现 | ✅ |
| 2 | ComplianceEngine定义 | hard | 已实现 | ✅ |
| 3 | ArtifactScanner定义 | hard | 已实现 | ✅ |

### 16.3 实施步骤

#### 步骤 1：完善DefaultSecurityGateway三层防御

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\compliance\implementations\default_security_gateway.py` |
| 验收标准 | L1/L2/L3拦截可运行 |
| 验证命令 | `python -m pytest tests/compliance/test_default_security_gateway.py -v` |
| G7 检查项 | security_gateway_base.py已读取；产出物路径精确；回滚方案可执行 |

#### 步骤 2：注册ArtifactScanner到YAML SSoT

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §0.1 |
| 产出位置 | `D:\ZephyrAlpha\architecture_model\layers\l10_compliance.yaml` |
| 验收标准 | audit_registration.py CLEAN |
| 验证命令 | `python scripts/governance/d11_compliance/audit_registration.py` |
| G7 检查项 | artifact_scanner.py已读取；YAML路径精确；回滚方案可执行 |

#### 步骤 3：完善ComplianceManagerBase

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\compliance\compliance_manager.py` |
| 验收标准 | CTR-P1-012可被D_RISK/D_EXECUTION_CORE消费 |
| 验证命令 | `python -m pytest tests/compliance/test_compliance_manager.py -v` |
| G7 检查项 | compliance_manager.py已读取；产出物路径精确；回滚方案可执行 |

### 16.4 回滚方案

| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| 1 | DefaultSecurityGateway三层防御实现失败 | `git checkout -- src/zephyr/compliance/implementations/` |
| 2 | YAML注册导致格式错误 | `git checkout -- architecture_model/layers/l10_compliance.yaml` |
| 3 | ComplianceManagerBase修改导致接口断裂 | `git checkout -- src/zephyr/compliance/compliance_manager.py` |

### 16.5 施工完成标准

| # | 产出物 | 存放完整绝对路径 | 是否存在 | 内容非空 | §0对齐 |
|---|--------|---------------|:---:|:---:|:---:|
| 1 | DefaultSecurityGateway | `D:\ZephyrAlpha\src\zephyr\compliance\implementations\default_security_gateway.py` | ☐ | ☐ | ☐ |
| 2 | l10_compliance.yaml | `D:\ZephyrAlpha\architecture_model\layers\l10_compliance.yaml` | ☐ | ☐ | ☐ |
| 3 | ComplianceManagerBase | `D:\ZephyrAlpha\src\zephyr\compliance\compliance_manager.py` | ☐ | ☐ | ☐ |

- [ ] DefaultSecurityGateway import成功
- [ ] ArtifactScanner S-01~S-06检测类别可运行
- [ ] CTR-P1-012 ComplianceRule可被D_RISK/D_EXECUTION_CORE消费
- [ ] artifact_scanner.py注册到YAML SSoT
- [ ] audit_registration.py exit 0

### 16.6 施工状态

| 字段 | 值 | 填写者 |
|------|-----|-------|
| construction_status | not_started | 施工者 |
| verification_status | unverified | 审计者 |
| code_alignment_verified | no | 审计者 |

### 16.7 参考实现规格

| # | 规格名称 | 类型 | 规格内容 | 对应代码 |
|---|---------|------|---------|---------|
| 1 | DefaultSecurityGateway三层防御 | 算法 | L1: _L1_PATTERNS正则匹配→InputSanitizer净化→L2: _L2_PATTERNS正则匹配+AISGSandbox.scan_content→L3: 汇总findings+LSG扫描→生成AuditDecision | `src/zephyr/governance/implementations/default_security_gateway.py` |
| 2 | AuditDecision生成逻辑 | 算法 | errors存在或lsg_blocked→BLOCK; warnings存在或l1_clean=False→FLAG; 否则→ALLOW | `src/zephyr/governance/implementations/default_security_gateway.py` |

### 16.8 施工参考卡

| # | 类型 | 名称 | 用途/说明 | 参数/字段 | 输出/约束 |
|---|:----:|------|----------|----------|----------|
| 1 | 命令 | `python -m pytest tests/compliance/` | 运行D_COMPLIANCE全部测试 | `-v`: 详细输出; `-k`: 过滤 | exit 0=通过 |
| 2 | 命令 | `python scripts/governance/d11_compliance/audit_registration.py` | 检查孤儿文件 | — | exit 0=CLEAN |
| 3 | 配置 | `l10_compliance.yaml` → `components` | YAML SSoT组件注册 | 类型/路径 | 必须与§0.1一致 |

### 16.10 故障与操作手册

| # | 阶段 | 场景 | 触发条件 | 诊断/操作 | 恢复/产出 | 验证/回退 |
|---|:----:|------|---------|----------|----------|----------|
| 1 | 施工 | DefaultSecurityGateway导入失败 | import报错 | 检查security_gateway_base.py路径 | 修正import | pytest验证 |
| 2 | 运行 | SecurityGateway拦截异常 | deny-all降级 | 检查审计日志中异常记录 | 异常解除后自动恢复 | 检查l10_security_gateway_blocked_total |
| 3 | 运行 | ArtifactScanner扫描失败 | 文件不存在 | 检查artifact_path有效性 | 返回空ScanReport | 修正路径后重扫 |
| 4 | 运行 | 紧急旁路 | D_COMPLIANCE阻塞CI | 跳过+降级为deny-all | — | D_COMPLIANCE恢复后取消旁路 |

### 16.12 并发操作模型

本模块无并发操作。SecurityGateway为同步调用，ArtifactScanner为异步CI/CD调用，两者无共享状态。

---

## §17 容量升级附录

### §17.1 容量基线

| 资源 | 当前基线 | 测量方式 |
|------|---------|---------|
| SecurityGateway QPS | 10/s | 压测工具 |
| ArtifactScanner 单次扫描文件数 | 50 | 日志统计 |
| ComplianceRule 数量 | 10 | 数据库查询 |
| AISG 模式规则数 | 20 | 配置文件统计 |

### §17.2 缺口分析

| 缺口ID | 当前瓶颈 | 升级方案 | 触发阈值 |
|--------|---------|---------|---------|
| GAP-L10-001 | SecurityGateway同步拦截延迟 | 异步拦截队列 + 缓存 | QPS > 100/s |
| GAP-L10-002 | ArtifactScanner串行扫描 | ThreadPoolExecutor并行 | 单次扫描文件 > 500 |

### §17.3 升级版本矩阵

| 版本 | generation | 升级类型 | 核心变更 | 代码覆盖 |
|------|:---:|---------|---------|:---:|
| v1.0.0 | 1 | 基线 | SecurityGateway + ComplianceEngine + AISGSandbox + ArtifactScanner | ⚠️ |
| v2.0.0 | 2 | 模板v3.3重构 | 章节重排+新增概述+标准锚点+AI施工前检查清单 | ⚠️ |

### 缺口清单

| 缺口ID | 缺口描述 | 优先级 | 目标版本 | 状态 |
|--------|---------|:---:|---------|:---:|
| GAP-L10-001 | SecurityGateway同步拦截延迟 | P1 | v3.0.0 | 待施工 |
| GAP-L10-002 | ArtifactScanner串行扫描 | P2 | v3.0.0 | 待施工 |

### 升级组件清单

| 组件名 | 对应缺口 | 代码文件 | 施工Phase | 状态 |
|--------|---------|---------|----------|:---:|
| AsyncInterceptQueue | GAP-L10-001 | `D:\ZephyrAlpha\src\zephyr\compliance\async_intercept_queue.py` | Phase 2 | 待施工 |
| ParallelScanner | GAP-L10-002 | `D:\ZephyrAlpha\src\zephyr\compliance\parallel_scanner.py` | Phase 2 | 待施工 |

---

## §18 决策记录

| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-L10-04 | 模板v3.5升级 | 保持v3.3/按v3.5升级 | 按v3.5升级 | §0前移+§7/§15删除+§10拆分+铁律扩展 | 2026-05-15 |

---

## ⚠️ Vibe Coding 蓝图编写铁律

| # | 铁律 | 违反后果 |
|---|------|---------|
| 1 | 所有路径必须是绝对路径（含盘符 `D:\`） | 路径错误 |
| 2 | 必备链接不可省略 | 信息缺失 |
| 3 | 蓝图必须是最终设计结果 | 信息淹没 |
| 4 | 产出物路径必须与 GOV-DOC-002 一致 | 路径幻觉 |
| 5 | 涉及文件范围必须明确列出 | 范围漂移 |
| 6 | 容量估算必须写 | 容量瓶颈 |
| 7 | 迁移/废弃方案必须写 | 断链/垃圾 |
| 8 | 禁止"待定"/"建议"/"按需"等模糊词 | 执行漂移 |
| 9 | 蓝图必须自包含 | 信息缺失 |
| 10 | 删除文件必须遵守安全删除协议 | 永久丢失 |
| 11 | construction_progress 必须与代码实际状态一致 | 误导AI |
| 12 | actual_disk_path 必须与 §11 产出物路径一致 | 搜索/导入失败 |
| 13 | 已实现代码不在蓝图中重复——§0.1标记`已实现`的模块，蓝图只保留接口签名（§4），不复制实现代码 | 代码与蓝图漂移 |
| 14 | 临时时态内容执行完毕后从蓝图删除——迁移方案、升级执行计划等临时时态内容，一旦执行完毕即成为历史，从蓝图删除 | 蓝图膨胀 |
| 15 | 蓝图内容拆分判定——职责不同→拆分独立蓝图；职责相同→原地升级。判定标准见"蓝图拆分判定标准" | 职责混淆 |

---

## 蓝图拆分判定标准

### 判定流程

| 步骤 | 判定 | 结果 |
|------|------|------|
| 1 | 蓝图内是否存在职责不同的多个子系统？ | 是→步骤2；否→原地升级 |
| 2 | 各子系统是否有独立的上游/下游依赖？ | 是→拆分独立蓝图；否→原地升级 |
| 3 | 拆分后各蓝图是否仍能自包含？ | 是→执行拆分；否→原地升级 |

### 判定示例

| 场景 | 职责不同？ | 独立依赖？ | 判定 |
|------|:---:|:---:|------|
| 安全网关 + 合规引擎 | 否（同属合规层） | 否（共享INF-012/020） | 原地升级 |
| 安全网关 + 风险管理 | 是 | 是 | 拆分独立蓝图 |
| Artifact扫描 + 数据摄取 | 是 | 是 | 拆分独立蓝图 |

---

## ⚠️ 安全删除协议

### 蓝图中的删除决策清单

| # | 待删除/废弃文件 | 完整绝对路径 | 删除类型 | 接收文件 | 安全删除方案 |
|---|---------------|------------|---------|---------|------------|
| 1 | default_security_gateway.py（根目录导出兼容层） | `D:\ZephyrAlpha\src\zephyr\compliance\default_security_gateway.py` | 迁移型 | `D:\ZephyrAlpha\src\zephyr\compliance\implementations\default_security_gateway.py` | 确认所有import路径指向implementations/后→标记deprecated→Phase4物理删除 |

### 删除铁律

| # | 铁律 | 原因 |
|---|------|------|
| 1 | 禁止蓝图阶段物理删除任何文件 | 蓝图只做决策，不做执行 |
| 2 | 迁移型删除必须逐条迁移、逐条验证 | 批量迁移容易遗漏 |
| 3 | 物理删除只能在 stable 搬入阶段执行 | deprecated 至少保持1个Phase |
| 4 | 物理删除必须人类确认 | AI 不得自行决定删除文件 |
| 5 | "宁可慢，不可漏" | 没有git备份，删了就没了 |

---

## 必备链接

| # | 文件 | module_id | 版本 | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------|------------|----------|
| 1 | 元数据注册表 | PS-STD-001 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_043_meta_rule_metadata.yaml` | 编号规则、doc_type词表 |
| 2 | 目录结构标准 | GOV-DOC-002 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 路径映射、边界判据 |
| 3 | 治理方法论 | PS-STD-011 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_024_methodology_diagnosis.yaml` | MTH-012 + MTH-013 |
| 4 | 文件命名规范 | GOV-DOC-003 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 命名规则 |
| 5 | 模块 ID 注册表 | — | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 编号注册 |
| 6 | 架构总览 | — | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\00-overview.md` | 架构上下文 |
| 7 | 治理规则主注册表 | — | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\document-metadata-index-registry.yaml` | 现有规则索引 |
| 8 | AI 自治权限注册表 | GOV-AI-001 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\ai_autonomy_authority_registry.yaml` | AI 操作权限 |

---

## 项目中已有类似功能

无

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | security_gateway_base.py | `D:\ZephyrAlpha\src\zephyr\compliance\security_gateway_base.py` | 修改 | 完善SecurityGateway抽象 |
| 2 | compliance_manager.py | `D:\ZephyrAlpha\src\zephyr\compliance\compliance_manager.py` | 修改 | 完善ComplianceManagerBase |
| 3 | aisg_sandbox.py | `D:\ZephyrAlpha\src\zephyr\compliance\aisg_sandbox.py` | 读取 | AISG模式匹配 |
| 4 | artifact_scanner.py | `D:\ZephyrAlpha\src\zephyr\compliance\artifact_scanner.py` | 修改 | 注册到YAML SSoT |
| 5 | default_security_gateway.py（根目录） | `D:\ZephyrAlpha\src\zephyr\compliance\default_security_gateway.py` | 废弃 | 导出兼容层→迁移 |
| 6 | implementations/default_security_gateway.py | `D:\ZephyrAlpha\src\zephyr\compliance\implementations\default_security_gateway.py` | 修改 | 完善三层防御实现 |
| 7 | l10_compliance.yaml | `D:\ZephyrAlpha\architecture_model\layers\l10_compliance.yaml` | 修改 | 补充artifact_scanner注册 |
| 8 | blueprint_registry.yaml | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | 修改 | name统一为compliance_core |

---

## 治理信息

### SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| 合规层架构设计 | **本文档 §1-§10** | — |
| 合规层施工步骤 | **本文档 §16** | — |
| 合规层接口契约 | **本文档 §4** | — |
| 代码文件清单与对齐状态 | **本文档 §0** | blueprint_registry.yaml（派生） |
| 容量升级方案 | **本文档 §17** | — |

**任何与本蓝图冲突的定义，以本蓝图为准。**

### 消费者注册表

| Tier | 消费者 | 依赖内容 |
|------|--------|---------|
| 1 | D_RISK Risk Management | CTR-P1-012 ComplianceRule |
| 1 | D_EXECUTION_CORE Trade Execution | CTR-P1-012 ComplianceRule |
| 2 | INF-020 Audit Trail | AuditDecision |
| 2 | CI/CD Pipeline | ArtifactScanner |

### 变更同步规则

| 变更类型 | Tier 1（下游蓝图） | Tier 2（集成系统） |
|---------|------------------|------------------|
| 新增/修改接口契约 | 下游检查接口兼容性 | 检查集成点兼容性 |
| 修改施工步骤 | 下游更新产出物引用 | 更新配置文件 |
| 修改模块边界 | 下游更新依赖声明 | 更新集成路由 |
| 修改 construction_progress | 下游更新依赖状态 | 更新集成测试 |
| 新增容量升级组件（§17） | 下游评估影响 | 更新容量预算 |

### 修改条件

| 变更类型 | 审批要求 |
|---------|---------|
| SecurityGateway/ComplianceEngine接口变更 | 需 Owner 审批 + 通知所有消费者 |
| 模块边界修改（§2） | 需 Owner 审批 |
| construction_progress 变更 | 需 §0 对齐验证通过 |
| 施工步骤微调（命令、路径修正） | AI 可自主修改 |
| 非关键补充（风险缓解、后果描述） | AI 可自主修改 |
| 容量升级方案新增（§17） | 需 Owner 审批 |
| 实现类变更 | AI 可自主 |

---

## 术语表

| 术语 | 精确定义 | 易混淆术语 | 区别 |
|------|---------|-----------|------|
| SecurityGateway | AI安全网关OCP扩展点，定义三层防御抽象 | DefaultSecurityGateway | SecurityGateway=抽象接口；DefaultSecurityGateway=具体实现 |
| ComplianceEngine | 合规规则OCP扩展点，定义规则评估抽象 | ComplianceManagerBase | ComplianceEngine=抽象接口；ComplianceManagerBase=管理基类 |
| AISG | AI Safety Gate——模式匹配测试器 | SecurityGateway | AISG=模式匹配组件；SecurityGateway=完整安全网关 |
| AuditDecision | 安全网关审计决策（allow/flag/block） | ComplianceResult | AuditDecision=安全拦截决策；ComplianceResult=合规评估结果 |
| CTR-P1-012 | 跨层契约——ComplianceRule定义 | ComplianceRule | CTR-P1-012=契约ID；ComplianceRule=数据类 |
| OCP-004 | 开放封闭原则——SecurityGateway三层防御扩展点 | — | 新安全策略只加不改 |
| INV-015 | 不变量——AISG拦截门禁 | — | 任何跳过AISG的AI指令执行均违反此不变量 |

---

## 已知问题与盲点登记

| # | 问题 | 严重性 | 根因 | 解决方案 | 约束编号 | 状态 |
|---|------|:------:|------|---------|---------|:----:|
| 1 | artifact_scanner.py未注册到YAML SSoT | 高 | 初始创建时遗漏注册 | 步骤2：注册到l10_compliance.yaml | §5.1 #4 | 待解决 |
| 2 | default_security_gateway.py根目录与implementations/重复 | 中 | 迁移未完成 | 根目录标记deprecated→Phase4物理删除 | §5.3 #1 | 待解决 |
| 3 | DefaultSecurityGateway两套实现接口签名不一致 | 中 | 独立开发未同步 | 统一接口签名到implementations/版本 | §4.1 | 待解决 |
| 4 | 可观测性指标未实现（§6.1） | 中 | T2-deferred阶段未施工 | Phase 2实现 | §6.1 | 待解决 |

---

## 自检与闭合清单

| # | 阶段 | 检查项 | 确认方式 | 状态 |
|---|:----:|--------|---------|:----:|
| 1 | 设计 | §3 每个组件在 §4 有对应接口 | 逐组件核对 | ☐ |
| 2 | 设计 | §4 每个接口在 §16 有对应施工步骤 | 逐接口核对 | ☐ |
| 3 | 设计 | §5 每个约束在 §9 有对应测试 | 逐约束核对 | ☐ |
| 4 | 设计 | §0.1 每个代码文件在 §11 有对应产出物路径 | 逐文件核对 | ☐ |
| 5 | 设计 | §10 每个依赖在 cross-module-dependency-registry.yaml 有对应条目 | 逐依赖核对 | ☐ |
| 6 | 前 | 已读取蓝图全文（概述→§0→§1-§18→术语表→自检清单） | 逐节确认 | ☐ |
| 7 | 前 | 术语表中每个术语含义已理解 | 能回答"X和Y的区别是什么" | ☐ |
| 8 | 前 | 成熟度声明中 volatile/evolving 的部分已标记 | 知道哪些设计可改哪些不可改 | ☐ |
| 9 | 前 | 已知问题登记中未解决的问题已知晓 | 知道哪些坑不能踩 | ☐ |
| 10 | 中 | 每步施工后执行验证命令 | exit 0 才进下一步 | ☐ |
| 11 | 中 | 新代码文件头部十五字段完整 | 逐文件核对 | ☐ |
| 12 | 中 | 修改接口契约后检查 §18 决策记录 | 决策ID+依据已更新 | ☐ |
| 13 | 后 | §0 代码对齐验证已更新 | construction_progress 与实际一致 | ☐ |
| 14 | 后 | 临时时态内容已清理 | 迁移方案已执行→删除 | ☐ |

---

## 成熟度声明

| 设计维度 | 成熟度 | 信心 | 升级标准 | 说明 |
|---------|:------:|:---:|---------|------|
| 核心架构 | stable | 高 | 三层防御架构经集成测试验证 | OCP-004+INV-015已定义 |
| 接口契约 | evolving | 中 | CTR-P1-012被D_RISK/D_EXECUTION_CORE实际消费 | 当前仅骨架实现 |
| 数据模型 | evolving | 中 | AuditDecision/ComplianceRule字段稳定 | 两套DefaultSecurityGateway接口不一致 |
| 施工步骤 | evolving | 中 | 业务层开放后验证 | T2-deferred，步骤待验证 |

---

## 版本演进路线图

| 版本 | 核心变更 | 前置版本 | 施工状态 |
|------|---------|---------|:-------:|
| v1.0.0 | SecurityGateway+ComplianceEngine+AISGSandbox+ArtifactScanner基线 | — | 已完成 |
| v2.0.0 | 模板v3.3重构+章节重排 | v1.0.0 | 已完成 |
| v2.1.0 | 模板v4.1回填（SLO/可观测性/退化矩阵/术语表等） | v2.0.0 | 已完成 |
| v3.0.0 | 容量升级（AsyncInterceptQueue+ParallelScanner） | v2.1.0 | 待施工 |

---

## 变更记录

> 变更历史通过 Git log 追踪。
