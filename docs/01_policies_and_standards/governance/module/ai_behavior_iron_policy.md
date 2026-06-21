---
module_id: GOV-MOD-002
title: AI模型行为铁律
doc_type: policy
status: active
version: "1.0.0"
layer: L01
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-02"
valid_from: "2026-05-02"
ttl: permanent
summary: "定义 AI 模型在任何操作中必须遵守�?10 条行为铁律，违反任何一条都可能导致架构污染或数据损坏。v1.0.0 升格：已�?6 个活跃文件量产级消费（GOV-MOD-001/003/004/005 + GOV-AI-001 + module-index），实质已达 active 成熟度。draft→active 升格�?2026-05-02 审计驱动�?
tags: [ai, governance, behavior, iron-rules, protected-paths]
rule_form: declarative
scope: global
stability: evolving
verifiability: manual
depends_on:
  - {target: PS-STD-001, at: "§2.5", why: "frontmatter字段唯一真源——策略文件的doc_type/rule_form一致性约�?}
  - {target: PS-STD-003, at: "§3", why: "行为边界标准ABS——AI行为铁律的宪法级约束基准"}
ai_autonomy: human_gated
---

# AI模型行为铁律

> module_id: GOV-MOD-002 | version: 1.0.0 | status: active | layer: L1

---

## 1. 目的与范�?

本策略定�?AI 模型�?ZephyrAlpha 项目中任何操作都必须遵守的行为铁律。违反任何一条都可能导致架构污染�?

适用于：所�?AI 模型的全部操作（不限于模块注入）�?

**铁律**：MUST 遵守本策略全部铁律——无铁律 = 编码损坏 + 上下文溢出 + SSoT 矛盾 + 断链累积。

**�?GOV-MOD-005 的分�?*：本策略管辖 AI 模型�?*行为准则**；GOV-MOD-005 管辖模块注入�?*技术检�?*。模块注入前必须同时满足本策略的行为铁律�?GOV-MOD-005 的注入检查�?

安全操作基线的补充规则参�?governance/security/ 下安全策略文件；架构污染的架构级治理约束参见 governance/architecture/ 下架构治理规则�?

## 2. SSoT 声明

本文档是 ZephyrAlpha 系统�?**AI 模型行为铁律**的唯一真源（SSoT）�?

**本文档定义了**�?
- 11 �?AI 行为铁律（IRN-001~011）——涵盖编码扫描、Session 预算、SSoT 唯一、断链清零、Phase Gate、能力边界、终局锁定、先读后写、双工具互斥、受保护路径、零残留原则
- 违规严重程度分级与处置方式（P0/P1/P2�?
- �?GOV-MOD-005 的职责分�?

**本文档与以下文件互补**（非取代关系）：
- GOV-MOD-005：模块注入技术检查——INJ-007 �?IRN-001 派生，注入级编码检�?
- GOV-SEC-001：安全操作基�?
- GOV-ARCH-001：架构污染防护的架构级约�?

**若其他文件中出现与本策略冲突�?AI 行为约束，以本文档为准�?*

## 3. 受控枚举定义

本文档定义了 **11 条铁�?*（IRN-001~011）作为受控枚举。每�?IRN 是全局唯一标识符，被以下治理文件引用：

| 枚举�?| 被引用于 | 引用方式 |
|--------|---------|---------|
| IRN-001 | GOV-MOD-005 | INJ-007 `derived_from: IRN-001` |
| IRN-010 | GOV-MOD-005, GOV-ARCH-001 | INJ-008 `derived_from: IRN-010`，受保护路径列表 |

**受控约束**：新增或删除铁律编号必须�?KB 决策记录流程（见 §13 修改条件），确保所有消费者同步更新映射�?

## 4. 消费者注册表

以下文件直接依赖本文档——铁律变更时必须同步更新�?

| 消费�?| 文件 | Tier | 依赖内容 |
|--------|------|:---:|---------|
| GOV-MOD-005 | module-injection-rules.yaml | 1 | INJ-007 �?IRN-001 派生（先读后写验证），INJ-008 �?IRN-010 派生（受保护路径检查） |
| GOV-MOD-001 | module-admission-policy.md | 1 | §7 准入否决条件——准入前置校验在操作层面落地 IRN 行为约束�?1 module_id 唯一�?IRN-003 SSoT 派生�?2 依赖完整性由 IRN-004 断链清零派生�?|
| GOV-ARCH-001 | governance/architecture/ | 2 | IRN-010 提供的受保护路径列表被架构模型消�?|

## 5. 铁律细则

### IRN-001：编码扫描（铁律1�?

所�?YAML/Markdown 文件写入后，必须运行编码扫描确认文件�?UTF-8 编码�?

- 验证方法：`python scripts/hooks/check_encoding.py`
- 违反后果：阿拉伯文乱码，双重编码损坏

### IRN-002：Session 预算（铁�?�?

- **规则**：每�?Session 内新创建文件不超�?8 个，新建目录不超�?3 个。同一文件反复修改请在已有文件中完成�?
- **例外**：Phase Gate 期间预算翻�?

- 验证方法：Session Log 审计
- 违反后果：上下文溢出，后期操作质量下�?

### IRN-003：SSoT 唯一（铁�?�?

每个架构事实有且仅有一份权威来源。其他文件只能引用，不能重复定义�?

- 验证方法：`check_ssot_conflicts.py`
- 违反后果：SSoT 矛盾，AI 按错误版本塞�?

### IRN-004：断链清零（铁律4�?

删除或移动文件后，必须在同一 commit 中更新所有引用，禁止分两�?commit�?

- 验证方法：`check_dead_links.py`
- 违反后果：断链累积，治理信号失真

### IRN-005：Phase Gate（铁�?�?

scaffold（治理基础设施）未完成前，禁止进入 beta（施工）�?beta（编码）�?

- 验证方法：Phase Gate 检�?
- 违反后果：技术债务爆发，地基不�?
- **落日条款**：本铁律�?scaffold 验收通过后自动失效。scaffold 结束时由 Owner 声明铁律5退役，届时更新本文件移除本条�?

### IRN-006：模型能力边界（铁律6�?

每个 AI 模型必须在其能力契约定义的边界内操作，禁止越权�?

- 验证方法：`model-capability-contract.yaml` 白名单校�?
- 违反后果：越权操作导致治理混�?

### IRN-007：架构终局锁定（铁�?�?

架构模型锁定后，任何变更必须�?Emergency Change Board 流程，禁止直接修改�?

- 验证方法：`architecture-endgame-locked` 声明检�?
- 违反后果：架构漂移，终局锁定失效

### IRN-008：先读后写（铁律8�?

修改任何文件前，必须�?Read 该文件的当前内容。禁止凭记忆或推测直接写入�?

- 验证方法：Session Log 审计（自动化脚本待开发——当前为规格占位）。check 每个 Write 前是否有对应�?Read 记录
- 违反后果：AI 凭过时记忆覆盖文件，导致内容回退或错�?

### IRN-009：双工具互斥（铁�?�?

禁止�?Cursor �?Trae 中同时打开同一文件编辑。同一时间只允许一�?IDE 操作同一文件�?

- 验证方法：流程纪律为主（Windows 下无统一�?IDE 文件锁机制），技术锁为辅
- 违反后果：两�?IDE 互相覆盖写入，文件内容损坏不可恢�?

### IRN-010：受保护路径不可写（铁律10�?

以下路径禁止 AI 直接写入、删除或重命名：

| 路径 | 保护级别 |
|------|:---:|
| `.git/` | 只读——禁止任何操�?|
| `AGENTS.md` | 重大修改�?Owner 审批（小修需�?session log 记录�?|
| `docs/01_policies_and_standards/meta/` 下所�?`.md` | 重大修改�?Owner 审批 |
| `docs/02_enterprise_architecture/target-architecture/architecture-model/` | 重大修改�?Owner 审批 |

- 验证方法：写入前检查目标路径是否在受保护清单中（`check_protected_paths.py`——规格占位）
- 违反后果：关键文件被覆盖 �?架构不可恢复

### IRN-011：零残留原则（铁�?1�?


**定义**：项目的磁盘状态必须始终保�?刚刚施工完成"的整洁度——没有任何文件、代码行、注释是为已完成�?phase 的中间过程服务的�?

**核心规则**�?

| 规则编号 | 规则 | 检测方�?|
|---------|------|---------|
| ZR-001 | **临时文件即删**：`_temp*`、`_check*`、`_phase_*`、`_test_*` 等前缀的临时文件，phase 完成后立即物理删除——不�?测试时的脚手�? | `detect_temp_files.py` |
| ZR-002 | **被替代即�?*：任何文件（文档/代码/配置）的内容被新版本完全替代后，原文件物理删除——不�?superseded 副本 | `detect_ruins_references.py`（路径残留）+ 人工判断 |
| ZR-003 | **孤儿即查**：零入边引用的文件（除锚�?蓝图/Session Log）标记为候选删除——AI 在每 phase 结束时主动报�?| `detect_orphan_py.py` + `detect_orphan_documents.py` |
| ZR-004 | **废墟禁引**：禁止在任何文件中引用已删除/废弃的路径——所有引用必须指向当前存在的文件�?KB namespace | `detect_ruins_references.py` |
| ZR-005 | **残留学债零容忍**：Session Log �?`decisions` 字段记录的清理决定，必须在下一�?session 开始前核对执行状态——未执行的清理项 = P1 违规 | Session Log 自检 |
| ZR-006 | **文件生命周期闭环**：新建文�?�?`status: draft` �?`status: active`。废弃路径必须与 GOV-DOC-006 对齐：`deprecated` 仅作为过渡期状态（须填 `superseded_by`、TTL、归档或删除）；**禁止**长期囤积无用�?deprecated 文档——过渡期满后 MUST 删除或归档�?*例外**：Session Log / rationale-log（TTL: permanent）不走废弃滞留路�?| `document-lifecycle-standard.md` |
| ZR-007 | **新文件准入门�?*：创建任何新文件前，AI 必须先回答三个问题——① 这个文件的内容是否已存在？② 这个文件在下一�?phase 是否仍有价值？�?这个文件是否可以被已存在的文件通过引用覆盖�?| 行为纪律——每�?Write 前自检 |
| ZR-008 | **Session 终了自净（Boy Scout Rule�?*：每�?Session 结束时，AI MUST 至少执行 `detect_temp_files.py` + `detect_orphan_py.py`。发现的临时文件/垃圾文件 �?自动删除；孤儿文�?�?主动报告。对标：vibe coding 社区第一铁律—�?Always leave the codebase cleaner than you found it" | Session 结束时强制自检 |
| ZR-009 | **代码级残留自检（AI Artifact Hygiene�?*：AI 生成的代�?MUST NOT 含有——① 幻觉 import（import 了不存在的包/模块）；�?空壳 stub 函数（`def foo(): pass` / `raise NotImplementedError`）；�?被注释掉的死代码块；�?`console.log`/`print()` 调试残留。对标：`vibe-check`（BZPRCHNY）的 20 �?AI 代码气味检测规�?| `detect_residual_files.py`（ORPHAN_SHELL/STALE_IMPORT�?+ 人工审查 |

**不可删除的例�?*�?
- 锚点文件（GOV-DOC-007 定义）：`AGENTS.md`、`.trae/rules/project_rules.md`、`docs/01_policies_and_standards/_registry/` �?
- Session Log（TTL: permanent�?
- architecture-rationale-log.md（appendix-only 推导链）
- 蓝图文件（`docs/03_modules/**/blueprint.md`�?
- KB 中的结构化决策（`namespace=decisions`�?

**AI 可直接执行的自检**�?
- `detect_residual_files.py` �?检测残留文�?
- `detect_temp_files.py` �?检测临时文�?
- `detect_ruins_references.py` �?检测废墟路径引�?
- `detect_orphan_py.py` �?检测孤�?Python 文件
- `detect_orphan_documents.py` �?检测孤立文�?
- `check_dead_links.py` �?检测断�?

**违反后果**：临时文件堆�?�?上下文噪音（下一�?AI session 加载时干扰决策质量）�?架构模型与实际文件状态偏�?�?SSoT 污染

### 铁律�?ABS 映射�?

以下显式映射每条铁律�?PS-STD-003 行为边界标准中的 ABS 条目，供 Vibe Coding AI 在无上下�?session 中直接定位宪法级边界�?

| 铁律 | 直接映射�?ABS | ABS 摘要 | 映射关系 |
|------|-------------|---------|---------|
| IRN-001（编码扫描） | ABS-23, ABS-24 | PowerShell echo �?md 禁止 / Python 编码声明 | 铁律�?ABS 的程序化执行——check_encoding.py 验证 |
| IRN-002（Session 预算�?| ABS-12（相关） | 不知道能力边界操作文�?| 间接相关——预算超�?= 越过能力边界。无直接 ABS，铁律是操作层约�?|
| IRN-003（SSoT 唯一�?| ABS-19, ABS-20 | 非权威文件中修改字段 / 重复定义字段 | 铁律�?ABS 的泛化——不仅字段，所有架构事实均唯一 |
| IRN-004（断链清零） | ABS-15 | 先删文件后清引用（分两次 commit�?| 直接对应——同一 commit 完成删除+引用更新 |
| IRN-005（Phase Gate�?| ABS-11 | 不知道当�?Phase 开始工�?| 延伸关系——ABS-11 要求"先确�?Phase"，铁律补�?确认后不跳过 Gate" |
| IRN-006（模型能力边界） | ABS-12 | 不知道能力边界操作文�?| 直接对应——铁律要求能力合约白名单校验 |
| IRN-007（架构终局锁定�?| ABS-01, ABS-05 | 修改 immutable_core / AI 执行 P0 变更 | 延伸关系——终局锁定后的架构模型视为 immutable_core |
| IRN-008（先读后写） | ABS-52 | 未读取文件当前版本就修改 | 直接对应——社区第一安全准则，铁律是操作化落�?|
| IRN-009（双工具互斥�?| ABS-25 | 两个编辑器同时打开同一文件 | 直接对应——铁律禁止并发编�?|
| IRN-010（受保护路径不可写） | ABS-09, ABS-44, ABS-08 | 修改 AGENTS.md / 引用废弃路径 / 修改 Cursor rules | 直接对应——铁律将多个 ABS 合并为统一的受保护路径清单 |
| IRN-011（零残留原则�?| ABS-15, ABS-44 | 断链累积 / 引用废墟目录 | 延伸关系——铁律抽象了"清理"原则并定义了可编程执行点（ZR-001~007�?|

## 6. 违反铁律的处�?

### 按严重程度分级处�?

| 严重�?| 涉及铁律 | 处置方式 |
|:---:|---------|---------|
| P0 �?| 铁律 1, 8, 10, 11 | **立即中止操作**，记�?Session Log，通知 Owner——违反后果不可逆（编码泄露、文件覆盖、关键路径删除、残留堆积） |
| P1 �?| 铁律 2-4, 9 | **警告+自纠**——AI 必须立即重新执行操作并遵守铁律；连续 3 次不遵守 �?升级�?P0 |
| P2 �?| 铁律 5-7 | **记录违规**，在 Session Log 中说明原因，Owner 裁决 |

### 响应矩阵

| **动作** | **关联铁律** | **处置** | **说明** |
|----------|-------------|--------|--------|
| **有覆盖文件写�?* | 受保护路径（IRN-010�?| **拒绝** | 若覆盖的�?*规则或不可变文件** �?P0；若覆盖的是**临时或测试文�?* �?不阻�?|
| **废弃文件清理** | 零残留原则（IRN-011�?| **主动执行** | �?phase 结束时自动扫描临时文�?孤立文件/废墟路径；若**残留未清�?* �?P0 |

## 7. �?GOV-MOD-005 的分�?

本策略（行为铁律）与 GOV-MOD-005（模块注入技术检查）的分工：

| 维度 | 本策略（GOV-MOD-002�?| GOV-MOD-005 |
|------|----------------------|-------------|
| 管辖范围 | AI 模型全部操作 | 模块注入操作 |
| 规则性质 | 行为准则（声明式�?| 技术检查（可自动化验证�?|
| 规则数量 | 11 �?| 8 �?|
| 执行时机 | 所有操�?| 注入�?|

模块注入前必�?*同时满足**�?
1. 本策略的 11 条行为铁律（AI 行为合规�?
2. GOV-MOD-005 �?8 条注入检查（技术合规）

原铁�?（ID唯一性）、铁�?（契约先行）、铁�?（依赖可解析+依赖方向）已归入 GOV-MOD-005 �?INJ-001/003/002/008，本策略不再重复定义�?

## 8. 标准间引用规�?

### normative（必须遵守——修改这些引用源时本文档也须同步更新�?

| 引用目标 | 引用位置 | 依赖内容 |
|---------|---------|---------|
| PS-STD-001 §2.5 | frontmatter depends_on | doc_type/rule_form 一致性约束——policy 文件的元数据合法�?|
| PS-STD-003 §3 | §1~§2 全部 IRN | ABS 级别禁止行为的宪法级约束基准——铁律违反处置的最高依�?|

### informative（仅供参考——变更时须评估影响但不强制同步）

| 引用目标 | 引用位置 | 用�?|
|---------|---------|------|
| GOV-MOD-005 §2 | §4 分工�?| 注入检查规则与行为铁律的互补关�?|
| governance/security/ | §1 范围 | 安全操作基线的领域规�?|
| governance/architecture/ | §1 范围 | 架构治理的领域规�?|

## 9. AI 可消费性声�?


**AI 可直接执行的自检**�?
- IRN-001（编码扫描）�?运行 `check_encoding.py`——每次写入后执行
- IRN-002（Session 预算）→ 检查当�?Session Log 中已处理模块�?�?5
- IRN-003（SSoT 唯一）→ `check_ssot_conflicts.py`
- IRN-004（断链清零）�?`check_dead_links.py`
- IRN-008（先读后写）�?行为纪律：每�?Write 前确认已�?Read 记录
- IRN-010（受保护路径）→ 写入前对照受保护清单
- IRN-011（零残留）→ Phase 结束时全量扫描临�?孤立/废墟文件；清理所�?`_temp*`、`_check*`、`_phase_*` 文件

**依赖人类裁决的规�?*�?
- IRN-005（Phase Gate）：Owner 声明 scaffold 验收通过后本铁律退�?
- IRN-006（模型能力边界）：`model-capability-contract.yaml` 白名单由 Owner 维护
- IRN-007（终局锁定）：Emergency Change Board �?Owner 主持
- IRN-009（双工具互斥）：流程纪律，技术锁为辅

**受保护路径清�?*（�? IRN-010）：`.git/`、`AGENTS.md`、含 `_DO_NOT_USE_` 前缀的废弃路径、`meta/` �?.md、`architecture-model/`——这些路�?AI 不可直接写�?

**最小必读路�?*（全�?AI session）：
1. §1 目的与范�?�?知道铁律适用边界
2. §2 SSoT 声明 �?知道本文档权威边�?
3. §5 铁律细则 �?逐条可自检的规�?
4. §6 违反处置 �?知道违规后果
5. §7 �?GOV-MOD-005 分工 �?知道与其他治理文件的边界
6. §5 铁律→ABS映射�?�?知道每条铁律在宪法中�?ABS 条目位置
7. §10 消费者通知机制 �?知道变更后如何通知受影响的消费�?

**Token 预算**：本文档�?2200 字（�?frontmatter），单次读取 �?3000 tokens�?

## 10. 变更同步规则

本策�?`stability: evolving`——铁律编号和内容会随 Phase 边界演变。以下矩阵定义变更类型与消费者同步要求：

| 变更类型 | 影响范围 | 同步动作 | 时机 |
|---------|---------|---------|------|
| 新增/删除铁律（IRN 编号变更�?| GOV-MOD-005（Tier 1�?| 更新 INJ-007/INJ-008 �?`derived_from` 字段 | �?commit |
| 修改铁律内容措辞 | 全部消费�?| 通知 + 评估是否语义变更 | 判断：语义变更→�?commit；文字微调→24h �?|
| P0/P1/P2 严重度分级调�?| GOV-MOD-001（Tier 1�?| 更新 §7 否决条件中的严重度映�?| �?commit |
| 修改 §7 �?GOV-MOD-005 分工边界 | GOV-MOD-005（Tier 1�?| 协商边界 + 双文件同�?update | �?branch，同 PR |
| frontmatter 仅变�?| �?| 不需同步 | �?|

### 消费者通知机制

上述表中"通知"动作的标准化执行方式�?

| 通知方式 | 触发条件 | 内容要求 | 格式 |
|---------|---------|---------|------|
| **Session Log 条目** | 所有变更（必须�?| 变更类型、受影响消费者清单、实际影响范围（无影响声�?有影响说明）、同步完成状�?| `[日期] [变更类型] [受影响消费者列表] [同步状�? DONE/PENDING]` |
| **ADR 创建** | L2 及以上变更、语义变�?| 变更原因、影响评估（Impact Assessment �?ISO 42001 §8 框架）、迁移路�?| 遵循 ADR 模板 |
| **module-id-registry.json 更新** | 涉及 `status`/`layer`/`depends_on` 字段变更 | 同步相关字段�?| JSON patch |

**执行顺序**：变更前创建 Session Log 占位条目 �?执行变更 �?变更完成后更�?Session Log �?DONE 状态�?

## 11. 修改条件

本策�?`ai_autonomy: human_gated`——铁律本身不可被 AI 修改，但解释和补充说明有分级权限�?

| 级别 | 变更范围 | 审批�?| 要求 |
|:---:|---------|--------|------|
| L0 | 错别字、措辞优化、格式调�?| AI 自批 | Session Log 记录 |
| L1 | 增加铁律�?为什么举�? | AI 可建议，Owner 确认 | Session Log 提案 �?Owner 24h 内确�?|
| L2 | 新增铁律 / 修改已有铁律内容 | Owner 审批 | 必须创建 KB 决策记录 |
| L3 | 删除铁律 / 严重度重新分�?| Owner 审批 | 必须创建 KB 决策记录 + 所�?Tier 1 消费者同�?|
| �?| 受保护路径列表（IRN-010 附录�?| Owner 唯一 | 此列表变更影响所有文件写保护，仅 Owner 可操�?|

## 12. 废弃流程

若本策略被更全面�?AI 行为治理框架取代�?

1. **搜索影响**：对全部 Tier 1/2 消费者执行搜�?`IRN-001|IRN-002|...|IRN-010`——确认所有引用都有迁移路�?
2. **通知�?*�?0 天提前通知全部消费者（Session Log + ADR�?
3. **废弃标记**：`status: deprecated`，`superseded_by` 指向替代文件
4. **过渡�?*：至�?90 天——期间新旧铁律并轨运行，消费者逐步切换映射
5. **归档**：过渡期满、全部引用已迁移 �?`status: archived`

## 13. 异常豁免机制

**默认**：铁律不可豁免——IRN-001~010 对所�?AI 行为同等级约束�?

**例外通道**：Owner 可在以下场景通过 ADR 签发豁免�?
- **灾难恢复**：系统故障需绕过某个铁律才能恢复（如 IRN-008 先读后写的验证脚本本身损坏）
- **Phase 边界**：Phase 转换期间，可临时豁免 IRN-002 Session 预算上限

**豁免规则**�?
- 每份豁免必须指定：豁免的铁律编号、豁免范围（文件/模块）、有效截止日�?
- 豁免到期自动回退——不自动续期
- 所有豁免记录在 module-id-registry.json �?`exemptions` 字段�?

## 14. 审查周期

本策略应在以下时机进行审查�?

| 触发条件 | 审查内容 |
|---------|---------|
| 每次 Phase 边界 | 10 条铁律是否仍覆盖当前架构的全部风险面 |
| �?AI 行为模式发现 | 是否需要新增铁�?|
| GOV-MOD-005 INJ 规则变更 | 铁律→INJ 派生映射是否需要更新（§3 受控枚举表） |
| 最低频率：�?6 个月 | 全量审查——即使无触发事件 |

## 15. 完整性自检清单

创建或重大修改本策略时，逐项勾选：

- [ ] §1 目的与范围：明确覆盖所�?Vibe Coding AI 行为
- [ ] §2 SSoT 声明：互补关系覆�?GOV-MOD-005 / GOV-MOD-001
- [ ] §3 受控枚举�?0 条铁律编号完整，引用的下游映射正�?
- [ ] §4 消费者注册表：全�?Tier 1/2 消费者已列出
- [ ] §5 铁律细则：每条有编号+规则+为什�?违反后果——含铁律→ABS映射表（映射到具�?ABS 条目+摘要+关系描述）完整且正确
- [ ] §6 违反处置：P0/P1/P2 分级正确，特别确�?P0 是否覆盖 IRN-008/010
- [ ] §7 分工：与 GOV-MOD-005 边界明确——无重复职责
- [ ] §8 标准间引用：normative �?informative 分类正确
- [ ] §10 变更同步规则：每种变更类型有明确的同步动作和时机——含消费者通知机制�? 层通知体系：Session Log/ADR/registry）已定义
- [ ] §13 异常豁免：豁免范�?截止日期+回退机制完整

