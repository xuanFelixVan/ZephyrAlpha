---
module_id: GOV-DOC-007
title: 文件删除/移动安全门禁
doc_type: policy
status: active
version: 1.1.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-01"
ttl: permanent
summary: "定义删除或移动任何文件前必须通过的安全检查，防止断链积累和知识丢失。"
tags: [file-operation, safety-gate, governance]
rule_form: declarative
scope: global
stability: stable
verifiability: manual
ai_autonomy: human_gated
---

# 文件删除/移动安全门禁

> **目的**：定义删除或移动任何文件前必须通过的安全检查，防止断链积累和知识丢失。
>
> **老树教训**：AI 工具执行"直接任务"（删除/移动文件）时，常遗漏"完整性副作用"（更新所有引用），导致断链在流水线操作后批量积累。

## 〇、目的与范围

### 〇.1 目的

确保任何文件的删除、移动、重命名操作都在安全门禁的控制下执行。防止 AI 在执行任务时因"直接完成任务目标"而忽略副作用（断链、知识丢失、锚点破坏）。

### 〇.2 本标准管理以下内容

| # | 内容 | 说明 |
|---|------|------|
| 1 | 删除文件的强制三问 | 是否锚点？是否有可提取价值？是否有其他文件引用？ |
| 2 | 删除文件的强制三步 | 找引用 → 清引用 → 断链验证 |
| 3 | 移动/重命名文件的强制两步 | git mv → 搜索旧路径引用 → 批量替换 |
| 4 | 不可触碰锚点文件清单 | 7 个文件在任何情况下不得删除 |
| 5 | 断链阈值 | 生产 ≤100 / 过渡期 ≤500 / >500 阻断 commit |
| 6 | 规划链接的写法规范 | 不存在的文件用 HTML 注释引用 |

### 〇.3 本标准**不**覆盖以下内容

| # | 排除项 | 以哪个文件为准 |
|---|--------|-------------|
| 1 | 文档生命周期状态判定（何时该废弃） | document-lifecycle-standard.md（GOV-DOC-006） |
| 2 | 文件的命名规范 | file-naming-standard.md（GOV-DOC-003） |
| 3 | 文件的存放路径 | file-path-standard.md（GOV-DOC-004） |
| 4 | 编码安全的检测与修复 | encoding-safety-standard.md（GOV-DOC-005） |
| 5 | commit message 格式规范 | PS-STD 或项目级规范 |

### 〇.4 专业对标

| 来源 | 对标内容 |
|------|---------|
| ITIL Change Control | 变更前必须评估影响+授权。本文的"删除前强制三问"即 ITIL 变更评估的文档化执行 |
| ISO 9001 §7.5.3.2 | 文件化信息的控制包括"分发、访问、检索和使用、存储和保存、变更控制、保留和处置"。本文 §二 覆盖处置步骤 |
| Google Engineering Practices | "每一笔 commit 应独立可审查，不应产生中间断裂状态"——本文 §二 的同一 commit 规则基于此 |
| K8s API Deprecation | "deprecated 资源在删除前必须确保无活跃引用"——本文 §一 的问题 3 对应 |

---

## 一、删除文件的强制三问

删除任何文件前，必须回答以下三个问题：

| 问题 | 回答 | 处置 |
|------|------|------|
| **是否在不可触碰锚点列表中？** | 是 | **停止，禁止删除** |
| **是否已提取知识/价值？** | 否且文件包含设计决策/策略/代码 | **必须先提取到知识库** |
| **是否有其他文件引用它？** | 是 | **必须先更新所有引用** |

### 不可触碰锚点文件（禁止删除）

```
docs/01_policies_and_standards/_registry/catalogs/document-metadata-index.yaml
docs/01_policies_and_standards/_registry/contracts/architecture-contract.yaml
docs/01_policies_and_standards/meta/rule-classification-and-arbitration-standard.md
docs/02_enterprise_architecture/target-architecture/architecture-model/_index.yaml
docs/02_enterprise_architecture/adr/index.md
AGENTS.md
.pre-commit-config.yaml
.roomodes
```

## 二、删除文件的强制三步

```bash
# 第一步：找到所有指向目标文件的引用
# PowerShell
Select-String -Path "docs/**/*.md" -Pattern "目标文件名" -Recurse

# 第二步：在同一 commit 内更新或移除所有引用
# （不允许分两次 commit：先删文件、后清引用）

# 第三步：删除后运行断链检测确认断链增量符合预期
python scripts/hooks/check_dead_links.py
```

## 三、移动/重命名文件的强制两步

```bash
# 第一步：git mv 后立即搜索旧路径的所有引用
git mv <旧路径> <新路径>
Select-String -Path "docs/**/*.md" -Pattern "旧文件名" -Recurse

# 第二步：批量替换旧路径为新路径，与 git mv 在同一 commit 提交
```

### 搬迁历史查询（强制）

移动文件前，必须先查询搬迁历史：

```bash
git log --follow --diff-filter=R --name-status --oneline -- "文件路径"
```

- 若搬迁次数 **≥ 2**：**停止**，报告给 Owner 确认后继续
- 搬迁 commit message 必须包含：`moved: old/path -> new/path | reason: 一句话原因`

## 四、断链阈值

| 状态 | 目标阈值 |
|------|---------|
| 正常生产 | ≤ 100 条 |
| 流水线重构过渡期 | ≤ 500 条（临时，需明确注释） |
| 超出 500 | pre-commit 直接阻断 commit |

## 五、规划链接的写法规范

尚不存在的文件若需要被引用，必须使用注释格式，禁止使用普通 Markdown 链接：

```markdown
<!-- PLANNED: ../03_modules/l01_infrastructure/<module>/construction-plan.md -->
```

普通 Markdown 链接 `[文字](不存在的路径)` 会被检测器计为断链，推高阈值，影响治理信号可信度。

## 六、禁止操作

| 禁止操作 | 原因 |
|---------|------|
| 删除锚点文件 | 治理系统崩溃风险 |
| 先删文件后清引用（分两次 commit） | 中间状态产生断链 |
| 使用 `--no-verify` 跳过 pre-commit 检查 | 绕过断链检测门禁 |
| 不查搬迁历史直接移动文件 | 可能产生第三次搬迁，追溯困难 |

## 七、与其他规则的关系

| 规则 | 与本标准的关系 |
|------|-------------|
| document-lifecycle-standard.md（GOV-DOC-006） | 生命周期决定文件何时进入废弃流程，废弃后才走到删除——本标准 §一 是废弃流程的最后一步门禁 |
| directory-structure-standard.md（GOV-DOC-002） | 不可触碰锚点文件的定义来源——锚点清单与 §5.1.2 锚点文件表一致 |
| encoding-safety-standard.md（GOV-DOC-005） | 损坏文件的修复（git checkout）可能触犯本标准的"强制三问" |
| document-control-policy.md（GOV-DOC-009） | 本标准实现 DOC-003（安全删除原则：删前必须清引用+不死文件） |

## 八、变更记录

| 日期 | 版本 | 修改内容 |
|------|------|---------|
| 2026-04-22 | 1.0.0 | 初始创建。定义删除强制三问+三步、移动强制两步、不可触碰锚点、断链阈值、规划链接写法。 |
| 2026-05-01 | 1.1.0 | 结构对齐。（1）新增 §〇 目的与范围（§〇.2 管理内容 + §〇.3 不覆盖内容 + §〇.4 专业对标）；（2）新增 §七 与其他规则的关系 + §八 变更记录。对齐 templates/policy-template.md 强制结构。 |
