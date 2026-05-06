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
summary: "定义 AI 模型在任何操作中必须遵守的 10 条行为铁律，违反任何一条都可能导致架构污染或数据损坏。v1.0.0 升格：已被 6 个活跃文件量产级消费（GOV-MOD-001/003/004/005 + GOV-AI-001 + module-index），实质已达 active 成熟度。draft→active 升格由 2026-05-02 审计驱动。"
tags: [ai, governance, behavior, iron-rules, protected-paths]
rule_form: declarative
scope: global
stability: evolving
verifiability: manual
depends_on:
  - {target: PS-STD-001, at: "§2.5", why: "frontmatter字段唯一真源——策略文件的doc_type/rule_form一致性约束"}
  - {target: PS-STD-003, at: "§3", why: "行为边界标准ABS——AI行为铁律的宪法级约束基准"}
ai_autonomy: human_gated
---

# AI模型行为铁律

> module_id: GOV-MOD-002 | version: 1.0.0 | status: active | layer: L1

---

## 1. 目的与范围

本策略定义 AI 模型在 ZephyrAlpha 项目中任何操作都必须遵守的行为铁律。违反任何一条都可能导致架构污染。

适用于：所有 AI 模型的全部操作（不限于模块注入）。

本策略源自老树教训：老树中没有明确的铁律，AI 模型自由发挥，导致编码损坏、上下文溢出、SSoT 矛盾、断链累积等一系列问题。

**与 GOV-MOD-005 的分工**：本策略管辖 AI 模型的**行为准则**；GOV-MOD-005 管辖模块注入的**技术检查**。模块注入前必须同时满足本策略的行为铁律和 GOV-MOD-005 的注入检查。

安全操作基线的补充规则参见 governance/security/ 下安全策略文件；架构污染的架构级治理约束参见 governance/architecture/ 下架构治理规则。

## 2. SSoT 声明

本文档是 ZephyrAlpha 系统中 **AI 模型行为铁律**的唯一真源（SSoT）。

**本文档定义了**：
- 11 条 AI 行为铁律（IRN-001~011）——涵盖编码扫描、Session 预算、SSoT 唯一、断链清零、Phase Gate、能力边界、终局锁定、先读后写、双工具互斥、受保护路径、零残留原则
- 违规严重程度分级与处置方式（P0/P1/P2）
- 与 GOV-MOD-005 的职责分工

**本文档与以下文件互补**（非取代关系）：
- GOV-MOD-005：模块注入技术检查——INJ-007 从 IRN-001 派生，注入级编码检查
- GOV-SEC-001：安全操作基线
- GOV-ARCH-001：架构污染防护的架构级约束

**若其他文件中出现与本策略冲突的 AI 行为约束，以本文档为准。**

## 3. 受控枚举定义

本文档定义了 **11 条铁律**（IRN-001~011）作为受控枚举。每条 IRN 是全局唯一标识符，被以下治理文件引用：

| 枚举项 | 被引用于 | 引用方式 |
|--------|---------|---------|
| IRN-001 | GOV-MOD-005 | INJ-007 `derived_from: IRN-001` |
| IRN-010 | GOV-MOD-005, GOV-ARCH-001 | INJ-008 `derived_from: IRN-010`，受保护路径列表 |

**受控约束**：新增或删除铁律编号必须走 ADR 流程（见 §13 修改条件），确保所有消费者同步更新映射。

## 4. 消费者注册表

以下文件直接依赖本文档——铁律变更时必须同步更新：

| 消费者 | 文件 | Tier | 依赖内容 |
|--------|------|:---:|---------|
| GOV-MOD-005 | module-injection-rules.yaml | 1 | INJ-007 从 IRN-001 派生（先读后写验证），INJ-008 从 IRN-010 派生（受保护路径检查） |
| GOV-MOD-001 | module-admission-policy.md | 1 | §7 准入否决条件——准入前置校验在操作层面落地 IRN 行为约束（#1 module_id 唯一由 IRN-003 SSoT 派生，#2 依赖完整性由 IRN-004 断链清零派生） |
| GOV-ARCH-001 | governance/architecture/ | 2 | IRN-010 提供的受保护路径列表被架构模型消费 |

## 5. 铁律细则

### IRN-001：编码扫描（铁律1）

所有 YAML/Markdown 文件写入后，必须运行编码扫描确认文件为 UTF-8 编码。

- 验证方法：`python scripts/hooks/check_encoding.py`
- 违反后果：阿拉伯文乱码，双重编码损坏

### IRN-002：Session 预算（铁律2）

- **规则**：每个 Session 内新创建文件不超过 8 个，新建目录不超过 3 个。同一文件反复修改请在已有文件中完成。
- **例外**：Phase Gate 期间预算翻倍

- 验证方法：Session Log 审计
- 违反后果：上下文溢出，后期操作质量下降

### IRN-003：SSoT 唯一（铁律3）

每个架构事实有且仅有一份权威来源。其他文件只能引用，不能重复定义。

- 验证方法：`check_ssot_conflicts.py`
- 违反后果：SSoT 矛盾，AI 按错误版本塞入

### IRN-004：断链清零（铁律4）

删除或移动文件后，必须在同一 commit 中更新所有引用，禁止分两次 commit。

- 验证方法：`check_dead_links.py`
- 违反后果：断链累积，治理信号失真

### IRN-005：Phase Gate（铁律5）

scaffold（治理基础设施）未完成前，禁止进入 beta（施工）或 beta（编码）。

- 验证方法：Phase Gate 检查
- 违反后果：技术债务爆发，地基不稳
- **落日条款**：本铁律在 scaffold 验收通过后自动失效。scaffold 结束时由 Owner 声明铁律5退役，届时更新本文件移除本条。

### IRN-006：模型能力边界（铁律6）

每个 AI 模型必须在其能力契约定义的边界内操作，禁止越权。

- 验证方法：`model-capability-contract.yaml` 白名单校验
- 违反后果：越权操作导致治理混乱

### IRN-007：架构终局锁定（铁律7）

架构模型锁定后，任何变更必须走 Emergency Change Board 流程，禁止直接修改。

- 验证方法：`architecture-endgame-locked` 声明检查
- 违反后果：架构漂移，终局锁定失效

### IRN-008：先读后写（铁律8）

修改任何文件前，必须先 Read 该文件的当前内容。禁止凭记忆或推测直接写入。

- 验证方法：Session Log 审计（自动化脚本待开发——当前为规格占位）。check 每个 Write 前是否有对应的 Read 记录
- 违反后果：AI 凭过时记忆覆盖文件，导致内容回退或错乱

### IRN-009：双工具互斥（铁律9）

禁止在 Cursor 和 Trae 中同时打开同一文件编辑。同一时间只允许一个 IDE 操作同一文件。

- 验证方法：流程纪律为主（Windows 下无统一跨 IDE 文件锁机制），技术锁为辅
- 违反后果：两个 IDE 互相覆盖写入，文件内容损坏不可恢复

### IRN-010：受保护路径不可写（铁律10）

以下路径禁止 AI 直接写入、删除或重命名：

| 路径 | 保护级别 |
|------|:---:|
| `.git/` | 只读——禁止任何操作 |
| `AGENTS.md` | 重大修改须 Owner 审批（小修需在 session log 记录） |
| `_DO_NOT_USE_old_tree/` | 只读——禁止任何操作 |
| `docs/01_policies_and_standards/meta/` 下所有 `.md` | 重大修改须 Owner 审批 |
| `docs/02_enterprise_architecture/target-architecture/architecture-model/` | 重大修改须 Owner 审批 |

- 验证方法：写入前检查目标路径是否在受保护清单中（`check_protected_paths.py`——规格占位）
- 违反后果：关键文件被覆盖 → 架构不可恢复

### IRN-011：零残留原则（铁律11）

> **对标**：Google Dead Code Elimination Policy · vi2 "文件即债务"原则 · Toyota Production System（Muda——消除浪费） · Extreme Programming YAGNI（You Aren't Gonna Need It）

**定义**：项目的磁盘状态必须始终保持"刚刚施工完成"的整洁度——没有任何文件、代码行、注释是为已完成的 phase 的中间过程服务的。

**核心规则**：

| 规则编号 | 规则 | 检测方式 |
|---------|------|---------|
| ZR-001 | **临时文件即删**：`_temp*`、`_check*`、`_phase_*`、`_test_*` 等前缀的临时文件，phase 完成后立即物理删除——不留"测试时的脚手架" | `detect_temp_files.py` |
| ZR-002 | **被替代即删**：任何文件（文档/代码/配置）的内容被新版本完全替代后，原文件物理删除——不留 superseded 副本 | `detect_ruins_references.py`（路径残留）+ 人工判断 |
| ZR-003 | **孤儿即查**：零入边引用的文件（除锚点/蓝图/Session Log）标记为候选删除——AI 在每 phase 结束时主动报告 | `detect_orphan_py.py` + `detect_orphan_documents.py` |
| ZR-004 | **废墟禁引**：禁止在任何文件中引用已删除/废弃的路径——所有引用必须指向当前存在的文件或 KB namespace | `detect_ruins_references.py` |
| ZR-005 | **残留学债零容忍**：Session Log 中 `decisions` 字段记录的清理决定，必须在下一次 session 开始前核对执行状态——未执行的清理项 = P1 违规 | Session Log 自检 |
| ZR-006 | **文件生命周期闭环**：新建文件 → `status: draft` → `status: active`。废弃路径必须与 GOV-DOC-006 对齐：`deprecated` 仅作为过渡期状态（须填 `superseded_by`、TTL、归档或删除）；**禁止**长期囤积无用的 deprecated 文档——过渡期满后 MUST 删除或归档。**例外**：Session Log / rationale-log（TTL: permanent）不走废弃滞留路径 | `document-lifecycle-standard.md` |
| ZR-007 | **新文件准入门禁**：创建任何新文件前，AI 必须先回答三个问题——① 这个文件的内容是否已存在？② 这个文件在下一个 phase 是否仍有价值？③ 这个文件是否可以被已存在的文件通过引用覆盖？ | 行为纪律——每次 Write 前自检 |
| ZR-008 | **Session 终了自净（Boy Scout Rule）**：每次 Session 结束时，AI MUST 至少执行 `detect_temp_files.py` + `detect_orphan_py.py`。发现的临时文件/垃圾文件 → 自动删除；孤儿文件 → 主动报告。对标：vibe coding 社区第一铁律——"Always leave the codebase cleaner than you found it" | Session 结束时强制自检 |
| ZR-009 | **代码级残留自检（AI Artifact Hygiene）**：AI 生成的代码 MUST NOT 含有——① 幻觉 import（import 了不存在的包/模块）；② 空壳 stub 函数（`def foo(): pass` / `raise NotImplementedError`）；③ 被注释掉的死代码块；④ `console.log`/`print()` 调试残留。对标：`vibe-check`（BZPRCHNY）的 20 条 AI 代码气味检测规则 | `detect_residual_files.py`（ORPHAN_SHELL/STALE_IMPORT） + 人工审查 |

**不可删除的例外**：
- 锚点文件（GOV-DOC-007 定义）：`AGENTS.md`、`.trae/rules/project_rules.md`、`docs/01_policies_and_standards/_registry/` 等
- Session Log（TTL: permanent）
- architecture-rationale-log.md（appendix-only 推导链）
- 蓝图文件（`docs/03_modules/**/blueprint.md`）
- KB 中的结构化决策（`namespace=decisions`）

**AI 可直接执行的自检**：
- `detect_residual_files.py` — 检测残留文件
- `detect_temp_files.py` — 检测临时文件
- `detect_ruins_references.py` — 检测废墟路径引用
- `detect_orphan_py.py` — 检测孤立 Python 文件
- `detect_orphan_documents.py` — 检测孤立文档
- `check_dead_links.py` — 检测断链

**违反后果**：临时文件堆积 → 上下文噪音（下一个 AI session 加载时干扰决策质量）→ 架构模型与实际文件状态偏移 → SSoT 污染

**专业对标矩阵**：

| 来源 | 对标内容 |
|------|---------|
| Google SWE | "Dead code is a liability, not an asset"——每个无用文件都会在未来被误读、误改 |
| Toyota Production System | Muda（無駄）——消除不产生价值的浪费。在软件中：每个不承载决策的文件都是 Muda |
| XP / YAGNI | "You Aren't Gonna Need It"——不要为未来的你写代码。已完成的 phase 的脚手架就是不需要的 |
| vi2 Framework | "文件即债务"——每个非代码文件都在为当下的施工便利付出未来的维护成本 |
| ITIL Change Control | 变更后必须验证"所有中间产物已清理"——对标准确映射到 ZR-001/002 |
| ISO 42001 §8 | AI system impact assessment——AI 清理文件前必须评估对系统的影响（对标 §6.8 删除前两步预检） |

**氛围编程社区对标矩阵**：

| 来源 | 对标内容 |
|------|---------|
| VIBEcoder Code Cleanup | AI 生成代码后必须专项清理冗余/无用片段——研究表明 AI 代码中 15-30% 为冗余（对标 ZR-009） |
| `vibe-check`（BZPRCHNY） | 针对 AI 代码的 20 条规则：幻觉 import、废弃 API、空函数、死代码、console.log 残留——社区首个 AI 代码质量 linter（对标 ZR-009） |
| ULAM Labs Vibe Cleanup | 5 大"需要清理"的信号：代码重复、文件结构混乱、AI 意大利面条代码、功能瘫痪、不一致模式（对标 ZR-001/003/006） |
| 42coffeecups Vibe Cleanup | 4 支柱清理策略：Linting + Refactoring + Formatting + Testing——"AI 生成代码优化的是正确性，不是可维护性"（对标 ZR-008/009） |
| Boy Scout Rule（社区共识） | "Always leave the campground cleaner than you found it"——应用到 AI：每次 session 结束时项目必须比开始时更干净（对标 ZR-008） |
| Koder.ai Vibe Coding Practice | "Remove dead code, rename confusing variables, add TODOs where you knowingly cut corners"——5 分钟清理检查清单（对标 ZR-007/008） |
| Questera Vibe Coding Tips | "Monitor and Clean Up Redundant Code"——定期审查 AI 生成代码中的冗余片段，调度重构（对标 ZR-003/006） |
| Marvik Cursor Rules Pattern | "Do not create new functions, files, or imports that don't exist" + "Keep changes minimal and focused"——通过 prompt 约束预防残留（对标 ZR-007） |

### 铁律与 ABS 映射表

以下显式映射每条铁律到 PS-STD-003 行为边界标准中的 ABS 条目，供 Vibe Coding AI 在无上下文 session 中直接定位宪法级边界：

| 铁律 | 直接映射的 ABS | ABS 摘要 | 映射关系 |
|------|-------------|---------|---------|
| IRN-001（编码扫描） | ABS-23, ABS-24 | PowerShell echo 写 md 禁止 / Python 编码声明 | 铁律是 ABS 的程序化执行——check_encoding.py 验证 |
| IRN-002（Session 预算） | ABS-12（相关） | 不知道能力边界操作文件 | 间接相关——预算超标 = 越过能力边界。无直接 ABS，铁律是操作层约束 |
| IRN-003（SSoT 唯一） | ABS-19, ABS-20 | 非权威文件中修改字段 / 重复定义字段 | 铁律是 ABS 的泛化——不仅字段，所有架构事实均唯一 |
| IRN-004（断链清零） | ABS-15 | 先删文件后清引用（分两次 commit） | 直接对应——同一 commit 完成删除+引用更新 |
| IRN-005（Phase Gate） | ABS-11 | 不知道当前 Phase 开始工作 | 延伸关系——ABS-11 要求"先确认 Phase"，铁律补充"确认后不跳过 Gate" |
| IRN-006（模型能力边界） | ABS-12 | 不知道能力边界操作文件 | 直接对应——铁律要求能力合约白名单校验 |
| IRN-007（架构终局锁定） | ABS-01, ABS-05 | 修改 immutable_core / AI 执行 P0 变更 | 延伸关系——终局锁定后的架构模型视为 immutable_core |
| IRN-008（先读后写） | ABS-52 | 未读取文件当前版本就修改 | 直接对应——社区第一安全准则，铁律是操作化落地 |
| IRN-009（双工具互斥） | ABS-25 | 两个编辑器同时打开同一文件 | 直接对应——铁律禁止并发编辑 |
| IRN-010（受保护路径不可写） | ABS-09, ABS-44, ABS-08 | 修改 AGENTS.md / 使用旧树文件 / 修改 Cursor rules | 直接对应——铁律将多个 ABS 合并为统一的受保护路径清单 |
| IRN-011（零残留原则） | ABS-15, ABS-44 | 断链累积 / 引用废墟目录 | 延伸关系——铁律抽象了"清理"原则并定义了可编程执行点（ZR-001~007） |

## 6. 违反铁律的处置

### 按严重程度分级处置

| 严重度 | 涉及铁律 | 处置方式 |
|:---:|---------|---------|
| P0 级 | 铁律 1, 8, 10, 11 | **立即中止操作**，记录 Session Log，通知 Owner——违反后果不可逆（编码泄露、文件覆盖、关键路径删除、残留堆积） |
| P1 级 | 铁律 2-4, 9 | **警告+自纠**——AI 必须立即重新执行操作并遵守铁律；连续 3 次不遵守 → 升级为 P0 |
| P2 级 | 铁律 5-7 | **记录违规**，在 Session Log 中说明原因，Owner 裁决 |

### 响应矩阵

| **动作** | **关联铁律** | **处置** | **说明** |
|----------|-------------|--------|--------|
| **有覆盖文件写入** | 受保护路径（IRN-010） | **拒绝** | 若覆盖的是**规则或不可变文件** → P0；若覆盖的是**临时或测试文件** → 不阻拦 |
| **废弃文件清理** | 零残留原则（IRN-011） | **主动执行** | 每 phase 结束时自动扫描临时文件/孤立文件/废墟路径；若**残留未清理** → P0 |

## 7. 与 GOV-MOD-005 的分工

本策略（行为铁律）与 GOV-MOD-005（模块注入技术检查）的分工：

| 维度 | 本策略（GOV-MOD-002） | GOV-MOD-005 |
|------|----------------------|-------------|
| 管辖范围 | AI 模型全部操作 | 模块注入操作 |
| 规则性质 | 行为准则（声明式） | 技术检查（可自动化验证） |
| 规则数量 | 11 条 | 8 条 |
| 执行时机 | 所有操作 | 注入前 |

模块注入前必须**同时满足**：
1. 本策略的 11 条行为铁律（AI 行为合规）
2. GOV-MOD-005 的 8 条注入检查（技术合规）

原铁律2（ID唯一性）、铁律3（契约先行）、铁律4（依赖可解析+依赖方向）已归入 GOV-MOD-005 的 INJ-001/003/002/008，本策略不再重复定义。

## 8. 标准间引用规范

### normative（必须遵守——修改这些引用源时本文档也须同步更新）

| 引用目标 | 引用位置 | 依赖内容 |
|---------|---------|---------|
| PS-STD-001 §2.5 | frontmatter depends_on | doc_type/rule_form 一致性约束——policy 文件的元数据合法值 |
| PS-STD-003 §3 | §1~§2 全部 IRN | ABS 级别禁止行为的宪法级约束基准——铁律违反处置的最高依据 |

### informative（仅供参考——变更时须评估影响但不强制同步）

| 引用目标 | 引用位置 | 用途 |
|---------|---------|------|
| GOV-MOD-005 §2 | §4 分工表 | 注入检查规则与行为铁律的互补关系 |
| governance/security/ | §1 范围 | 安全操作基线的领域规则 |
| governance/architecture/ | §1 范围 | 架构治理的领域规则 |

## 9. AI 可消费性声明

> 对标 Anthropic CLAUDE.md——直接向 AI 说明如何解析和执行本文档。

**AI 可直接执行的自检**：
- IRN-001（编码扫描）→ 运行 `check_encoding.py`——每次写入后执行
- IRN-002（Session 预算）→ 检查当前 Session Log 中已处理模块数 ≤ 5
- IRN-003（SSoT 唯一）→ `check_ssot_conflicts.py`
- IRN-004（断链清零）→ `check_dead_links.py`
- IRN-008（先读后写）→ 行为纪律：每次 Write 前确认已有 Read 记录
- IRN-010（受保护路径）→ 写入前对照受保护清单
- IRN-011（零残留）→ Phase 结束时全量扫描临时/孤立/废墟文件；清理所有 `_temp*`、`_check*`、`_phase_*` 文件

**依赖人类裁决的规则**：
- IRN-005（Phase Gate）：Owner 声明 scaffold 验收通过后本铁律退役
- IRN-006（模型能力边界）：`model-capability-contract.yaml` 白名单由 Owner 维护
- IRN-007（终局锁定）：Emergency Change Board 由 Owner 主持
- IRN-009（双工具互斥）：流程纪律，技术锁为辅

**受保护路径清单**（§5 IRN-010）：`.git/`、`AGENTS.md`、`_DO_NOT_USE_old_tree/`、`meta/` 下 .md、`architecture-model/`——这些路径 AI 不可直接写。

**最小必读路径**（全新 AI session）：
1. §1 目的与范围 → 知道铁律适用边界
2. §2 SSoT 声明 → 知道本文档权威边界
3. §5 铁律细则 → 逐条可自检的规则
4. §6 违反处置 → 知道违规后果
5. §7 与 GOV-MOD-005 分工 → 知道与其他治理文件的边界
6. §5 铁律→ABS映射表 → 知道每条铁律在宪法中的 ABS 条目位置
7. §10 消费者通知机制 → 知道变更后如何通知受影响的消费者

**Token 预算**：本文档约 2200 字（含 frontmatter），单次读取 ≤ 3000 tokens。

## 10. 变更同步规则

本策略 `stability: evolving`——铁律编号和内容会随 Phase 边界演变。以下矩阵定义变更类型与消费者同步要求：

| 变更类型 | 影响范围 | 同步动作 | 时机 |
|---------|---------|---------|------|
| 新增/删除铁律（IRN 编号变更） | GOV-MOD-005（Tier 1） | 更新 INJ-007/INJ-008 的 `derived_from` 字段 | 同 commit |
| 修改铁律内容措辞 | 全部消费者 | 通知 + 评估是否语义变更 | 判断：语义变更→同 commit；文字微调→24h 内 |
| P0/P1/P2 严重度分级调整 | GOV-MOD-001（Tier 1） | 更新 §7 否决条件中的严重度映射 | 同 commit |
| 修改 §7 与 GOV-MOD-005 分工边界 | GOV-MOD-005（Tier 1） | 协商边界 + 双文件同步 update | 同 branch，同 PR |
| frontmatter 仅变更 | 无 | 不需同步 | — |

### 消费者通知机制

上述表中"通知"动作的标准化执行方式：

| 通知方式 | 触发条件 | 内容要求 | 格式 |
|---------|---------|---------|------|
| **Session Log 条目** | 所有变更（必须） | 变更类型、受影响消费者清单、实际影响范围（无影响声明/有影响说明）、同步完成状态 | `[日期] [变更类型] [受影响消费者列表] [同步状态: DONE/PENDING]` |
| **ADR 创建** | L2 及以上变更、语义变更 | 变更原因、影响评估（Impact Assessment 按 ISO 42001 §8 框架）、迁移路径 | 遵循 ADR 模板 |
| **module-id-registry.json 更新** | 涉及 `status`/`layer`/`depends_on` 字段变更 | 同步相关字段值 | JSON patch |

**执行顺序**：变更前创建 Session Log 占位条目 → 执行变更 → 变更完成后更新 Session Log 为 DONE 状态。

## 11. 修改条件

本策略 `ai_autonomy: human_gated`——铁律本身不可被 AI 修改，但解释和补充说明有分级权限：

| 级别 | 变更范围 | 审批方 | 要求 |
|:---:|---------|--------|------|
| L0 | 错别字、措辞优化、格式调整 | AI 自批 | Session Log 记录 |
| L1 | 增加铁律的"为什么举例" | AI 可建议，Owner 确认 | Session Log 提案 → Owner 24h 内确认 |
| L2 | 新增铁律 / 修改已有铁律内容 | Owner 审批 | 必须创建 ADR |
| L3 | 删除铁律 / 严重度重新分级 | Owner 审批 | 必须创建 ADR + 所有 Tier 1 消费者同步 |
| — | 受保护路径列表（IRN-010 附录） | Owner 唯一 | 此列表变更影响所有文件写保护，仅 Owner 可操作 |

## 12. 废弃流程

若本策略被更全面的 AI 行为治理框架取代：

1. **搜索影响**：对全部 Tier 1/2 消费者执行搜索 `IRN-001|IRN-002|...|IRN-010`——确认所有引用都有迁移路径
2. **通知期**：30 天提前通知全部消费者（Session Log + ADR）
3. **废弃标记**：`status: deprecated`，`superseded_by` 指向替代文件
4. **过渡期**：至少 90 天——期间新旧铁律并轨运行，消费者逐步切换映射
5. **归档**：过渡期满、全部引用已迁移 → `status: archived`

## 13. 异常豁免机制

**默认**：铁律不可豁免——IRN-001~010 对所有 AI 行为同等级约束。

**例外通道**：Owner 可在以下场景通过 ADR 签发豁免：
- **灾难恢复**：系统故障需绕过某个铁律才能恢复（如 IRN-008 先读后写的验证脚本本身损坏）
- **Phase 边界**：Phase 转换期间，可临时豁免 IRN-002 Session 预算上限

**豁免规则**：
- 每份豁免必须指定：豁免的铁律编号、豁免范围（文件/模块）、有效截止日期
- 豁免到期自动回退——不自动续期
- 所有豁免记录在 module-id-registry.json 的 `exemptions` 字段中

## 14. 审查周期

对标 ISO 11179 §6.2 定期审查要求，本策略应在以下时机进行审查：

| 触发条件 | 审查内容 |
|---------|---------|
| 每次 Phase 边界 | 10 条铁律是否仍覆盖当前架构的全部风险面 |
| 新 AI 行为模式发现 | 是否需要新增铁律 |
| GOV-MOD-005 INJ 规则变更 | 铁律→INJ 派生映射是否需要更新（§3 受控枚举表） |
| 最低频率：每 6 个月 | 全量审查——即使无触发事件 |

## 15. 完整性自检清单

创建或重大修改本策略时，逐项勾选：

- [ ] §1 目的与范围：明确覆盖所有 Vibe Coding AI 行为
- [ ] §2 SSoT 声明：互补关系覆盖 GOV-MOD-005 / GOV-MOD-001
- [ ] §3 受控枚举：10 条铁律编号完整，引用的下游映射正确
- [ ] §4 消费者注册表：全部 Tier 1/2 消费者已列出
- [ ] §5 铁律细则：每条有编号+规则+为什么+违反后果——含铁律→ABS映射表（映射到具体 ABS 条目+摘要+关系描述）完整且正确
- [ ] §6 违反处置：P0/P1/P2 分级正确，特别确认 P0 是否覆盖 IRN-008/010
- [ ] §7 分工：与 GOV-MOD-005 边界明确——无重复职责
- [ ] §8 标准间引用：normative 和 informative 分类正确
- [ ] §10 变更同步规则：每种变更类型有明确的同步动作和时机——含消费者通知机制（3 层通知体系：Session Log/ADR/registry）已定义
- [ ] §13 异常豁免：豁免范围+截止日期+回退机制完整

## 16. 变更记录

| 日期 | 版本 | 变更说明 |
|------|------|---------|
| 2026-05-01 | 0.7.3 | P2 描述精确化：§4 Tier 1 GOV-MOD-001 消费者描述从模糊的"直接调用 IRN 规则"改为具体的 IRN→准入规则派生映射（#1 module_id 唯一←IRN-003，#2 依赖完整性←IRN-004） |
| 2026-05-01 | 0.7.2 | P2 补齐：(1) IRN→ABS 显式映射表（10 行 × 4 列）；(2) §10.1 消费者通知机制——三层通知体系（Session Log/ADR/registry）+ 执行顺序；所有 4 个关联文件同步添加通知机制交叉引用 |
| 2026-05-01 | 0.7.1 | 交叉引用漂移修复：informative refs 表中 §4→§7 / §2→§5 + 受保护路径清单 §3→§5——Round 10 插入 §3/§4 后未同步的 body ref |
| 2026-05-01 | 0.7.0 | 对齐 PS-STD-002 §3.2.4（行为规则型条件性章节）：新增 §3 受控枚举定义（10条铁律作为枚举） + §4 消费者注册表（Tier 1/2 含 GOV-MOD-005/001/ARCH-001/AI-005） + §10 变更同步规则 + §11 修改条件（L0~L3 分级） + §12 废弃流程 + §13 异常豁免机制（灾难恢复/Phase边界豁免通道） + §14 审查周期（ISO 11179） + §15 完整性自检清单。修正 C4（P0 严重度扩展至 IRN-008/010——覆盖不可逆后果） + C5（governance/security/→GOV-SEC-001 等相对引用→module_id） + C6（IRN-002 硬编码 5→8/2→3，添加 GOV-AI-005 交叉引用）。全文章节重编号 §3→§16。 |
| 2026-05-01 | 0.6.2 | Common Core 对齐 PS-STD-002 §3.2.1：新增 §2 SSoT声明 + §6 标准间引用规范（normative/informative）+ §7 AI可消费性声明 + 全文章节重编号（§2~§5 → §3~§8） |
| 2026-05-01 | 0.6.1 | 深颗粒审计修复：§4 规则数量硬编码 7→8 + 铁律4映射补全 INJ-002/008（依赖可解析+依赖方向分离） + 标题「模块注入6铁律」→「模块注入技术检查」 |
| 2026-05-01 | 0.6.0 | 元规则对齐审计：frontmatter 添加 valid_from + 字段排序对齐 PS-STD-001 §2.3 + layer cross_layer→L1 + depends_on 移除 GOV-SEC-001/GOV-ARCH-001/GOV-AI-005 同级引用对齐链深=1层死规则（PS-STD-001 §2.1） |
| 2026-05-01 | 0.5.0 | 第三轮补缺：IRN-008/009 验证方法标注（脚本占位/Windows限制）+ IRN-010 受保护路径不可写 + 规则数 9→10 |
| 2026-05-01 | 0.4.0 | 补齐 G3/G4/G11/G12 细颗粒审查缺漏：新增铁律8（先读后写）+ 铁律9（双工具互斥）+ IRN-005 落日条款 + depends_on 补齐 GOV-AI-005 |
| 2026-05-01 | 0.3.0 | #24 审批修复：frontmatter 补齐 depends_on 结构化 + ai_autonomy: human_gated |
| 2026-04-30 | 0.1.0 | 初始版本（原名 pre-model-onboarding-10-rules.md） |
