---
module_id: MOD-INF-005
title: 脚本系统蓝图 — 第三条生产线的自动化审计与门禁
doc_type: blueprint
status: Active
version: 5.2.1
layer: L01
layer_name: infrastructure
functional_domain: infra
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
valid_from: 2026-05-03
ttl: permanent
construction_progress: phase_2_complete
belongs_to: "MOD-MASTER-001"
dependencies:
  - MOD-INF-001
  - MOD-INF-003
  - MOD-INF-004
  - MOD-INF-006
  - MOD-KB-001
priority: P0
tags:
  - script-system
  - governance
  - pre-commit
  - automation
  - run-all
  - manifest
  - quality-gate
  - infrastructure
  - self-monitoring
  - sla
  - plugin-contract
summary: 脚本系统是 ZephyrAlpha 第三条独立生产线——横切全局地对方案工厂和任务管线的产出物进行 12 维度系统化审计。包含五阶段流水线（C1扫描→C2分类→C3报告→C4跟踪→C5沉淀）、标准化 Finding Schema、四档退出码约定（0/1/2/3）、pre-commit 门禁集成、manifest 登记的治理脚本统一编排（参见 `script_manifest.yaml` 的 `total_scripts`；本仓库当前生成值约 **177**）、插件接口契约、自动化治理边界、系统自我监控与应急回退机制、SLA/SLO 度量体系。对标 ITIL 4 / OWASP ASVS v5 / K8s Conformance (Sonobuoy) / NASA-STD-8739.8B / Terraform pre-commit / Cursor Rules / Windsurf Rules / Anthropic CLAUDE.md 最佳实践。
---

# 脚本系统蓝图 — 第三条生产线的自动化审计与门禁

> **module_id**: MOD-INF-005 | **version**: 5.2.1 | **status**: Active | **layer**: L01 infrastructure

> **真源声明**：本蓝图升格自场外草稿原件（vibe-coding-script-system-design.md，原名"氛围编程基础设施——脚本系统设计"）。本蓝图为该设计的 canonical 正式版本，任何冲突以本蓝图为准。

---

## 1. 概述与模块定位

### 1.1 模块身份

| 属性 | 值 |
|------|-----|
| module_id | MOD-INF-005 |
| 层级 | L01 infrastructure（基础设施层） |
| 功能域 | 脚本治理基础设施 |
| 优先级 | P0（阻断级——脚本系统故障 = 所有门禁失效） |

### 1.2 核心职责

脚本系统是 ZephyrAlpha 的**自动化治理基础设施**——它不直接生产业务代码或需求，而是像一条"自动化流水线"，在代码和文档提交后自动检查它们是否健康、合规、安全。

| # | 职责 | 说明 |
|---|------|------|
| 1 | **治理脚本统一管理** | manifest 注册的脚本按 12 维度分类、注册、编排——审计、校验、扫描、健康检查（数以 `total_scripts` 为准，当前约 **177**） |
| 2 | **脚本三件套入库流程** | 任何新脚本必须走：落位→manifest注册→运行验证——缺一步不视为入库 |
| 3 | **run_all.py 调度编排** | 统一入口，支持全维度/单维度/指定维度扫描，输出结构化报告 |
| 4 | **pre-commit 门禁集成** | git commit 时自动阻断违规——V1 违规硬阻断，V2 违规警告 |
| 5 | **与任务系统集成** | 脚本失败→关联任务 BLOCKED；Finding→自动创建修复任务卡 |

### 1.3 在三线体系中的位置

```
ZephyrAlpha 三线生产体系：
  第一线：Spec Factory  →  意图→规约→消歧→审计→蓝图
  第二线：Task Pipeline  →  拆解→编排→装配→执行→审计
  第三线：Script System  →  扫描→分类→报告→跟踪→沉淀  ← 本蓝图
```

本系统是**第三条独立生产线**——不依附于任何一条线，横切两线做系统级审计。

### 1.4 设计背景

**已有两条线的"内嵌审计"不够用**——它们只审计自己管线内的产出，回答不了：
- 整个系统现在健康吗？
- 三个月前的审计发现修了没有？
- 新加的文件有没有破坏已有架构？

**对标依据**：OWASP ASVS v5（三级自动化验证）、Kubernetes Conformance（标准化一致性测试）、pre-commit 社区（钩子编排引擎）——任何大型治理系统都需要独立的审计基础设施。

### 1.5 目标

| # | 目标 | 可衡量标准 |
|---|------|-----------|
| 1 | 建立统一脚本入口——一键运行所有审计检查 | `python scripts/governance/run_all.py` 可执行 |
| 2 | 统一输出格式——所有扫描器输出标准 Finding Schema | 全部脚本输出符合 Finding Schema 的 JSONL（以 script_manifest.yaml 为准） |
| 3 | pre-commit 门禁自动化——git commit 时自动阻断 V1 违规 | `.pre-commit-config.yaml` 中核心钩子有效运行 |
| 4 | 覆盖全部 12 维度 | 12/12 维度有可运行的扫描器 |
| 5 | 与任务系统闭合——Finding自动创建任务卡 | CRITICAL/HIGH Finding → 自动创建 BLOCKED 任务 |

### 1.6 不包含的目标

| # | 明确排除 | 原因 |
|---|---------|------|
| 1 | Web Dashboard / UI | 当前阶段纯 CLI |
| 2 | 自动修复（Auto-Fixer） | C4 阶段只跟踪不自动修——修复是两条生产线的职责 |
| 3 | GitHub Actions / CI 云端集成 | 暂不需要——项目在本地 |
| 4 | entity-graph 构建（D12 幻觉检测完全体） | 先上 SelfCheckGPT 零资源方案，entity-graph 是 beta |

### 1.7 自动化不可逾越的边界

> 对标 ITIL 4 自动化治理机制——明确哪些流程适合自动化，哪些必须保持人工介入。ServiceNow 2024 年运维报告：40% 企业存在过度依赖自动化却忽视自动化边界定义的风险。

以下边界是脚本系统**绝对不能跨越的**——任何脚本触及这些红线时必须上报人工决策，不得自动执行：

| # | 红线 | 说明 | 脚本行为 |
|---|------|------|---------|
| 1 | **自动修改源码** | 脚本只能报告问题，不能自行修改 `src/zephyr/` 下的代码 | 报告 Finding，不执行修复 |
| 2 | **自动删除文件** | 脚本不能自行删除任何项目文件 | 报告 Finding（如废弃文件），由人工决定删除 |
| 3 | **自动修改配置文件** | `pyproject.toml`、`pre-commit-config.yaml` 等配置的修改必须人工审核 | 报告漂移检测，不自动修改 |
| 4 | **自动跳过门禁** | 脚本不能绕过 pre-commit 门禁或 CI 闸门 | 退出码严格 0/1/2/3，不伪造输出 |
| 5 | **自动修改登记表** | `registry-master-index.yaml` 等核心登记表的修改必须经 AI+人工确认 | 报告不一致，不自动写入 |
| 6 | **自我修改** | 脚本不能修改脚本系统自身的代码（包括其他脚本 + 本蓝图） | 报告自身问题，交由其他脚本或人工修复 |

> **大白话**：脚本是质检员，不是厂长。质检员可以喊"这里有问题！"但不能自己动手修——修是生产线的责任。六条红线就像交警的红灯——任何时候不能闯。

---

## 2. 必备链接与依赖声明

### 2.1 必备链接

| # | 文件 | module_id | 完整绝对路径 | 用途 |
|---|------|-----------|------------|------|
| 1 | 任务系统蓝图 | MOD-INF-006 | `D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\task-system\blueprint.md` | 门禁体系 G0-G7 + 管线节点 M1-M11——脚本失败→任务状态转换的接口定义 |
| 2 | 元数据注册表 | PS-STD-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\meta\metadata-registry.md` | frontmatter schema + META-V 验证规则 |
| 3 | 规则验证标准 | PS-STD-012 | `D:\ZephyrAlpha\docs\01_policies_and_standards\meta\rule-verification-standard.md` | V1~V4 四级验证体系 |
| 4 | 脚本质量标准 | SCRIPT-QUALITY-001 | `D:\ZephyrAlpha\scripts\governance\quality-standard.md` | 8维度×38条款——脚本自身的质量约束 |
| 5 | 脚本清单 | script_manifest.yaml | `D:\ZephyrAlpha\scripts\governance\script_manifest.yaml` | 脚本的完整注册表（SSoT，以实际生成为准） |
| 6 | AGENTS.md | — | `D:\ZephyrAlpha\AGENTS.md` | §6.5 脚本入库强制约定——蓝图的法律依据 |
| 7 | 脚本治理入口 | index.md | `D:\ZephyrAlpha\scripts\governance\index.md` | AI 施工时查"已有哪些脚本" |
| 8 | 模块登记表 | — | `D:\ZephyrAlpha\docs\03_modules\module-registry.yaml` | 模块编号注册 |

### 2.2 depends_on 声明

| target | at | why |
|--------|-----|-----|
| MOD-INF-006 | §4 | G0-G7门禁体系——脚本失败→任务BLOCKED的状态转换定义 |
| MOD-INF-006 | §5 | 管线M1-M11——run_all.py批量运行→管线节点判定逻辑 |
| MOD-INF-006 | §3.2.1 + §4.2 + §3.1.2 | TaskCard 模型 + 10状态机 + task_id格式——Finding→任务卡关联 |
| MOD-KB-001 | §3.2 + §6 | KE Schema + KB 入库——MEDIUM Finding→KB + C5 知识沉淀 |
| PS-STD-001 | §7 | metadata注册表——脚本注册字段定义 |
| SCRIPT-QUALITY-001 | §2 | 脚本退出码约定（0/1/2/3）——编码铁律在质量标准中定义 |

### 2.3 与已有类似功能的区别

| 已有模块 | 重叠点 | 为什么不能复用 |
|---------|--------|-------------|
| MOD-INF-004 vibe-coding-pipelines | 脚本系统被提及 | MOD-INF-004 管"怎么跑管线"，本系统管"怎么审计产出物"——独立职责，独立架构 |
| MOD-INF-006 task-system | 任务管线里有审计 | MOD-INF-006 的任务管线审计是"内嵌审计"——只审计自己管线产出。本系统是"系统级审计"——横切全局 |

---

## 3. 脚本分类体系

脚本按三个轴分类：**维度 × 退出码 × 触发方式**。

### 3.1 按审计维度分类（主分类轴）

```
D1  结构完整性     d1_structure/          17个脚本
D2  链接完整性     d2_links/               2个脚本
D3  元数据合规     d3_metadata/           20个脚本
D4  路径有效性     d4_paths/               4个脚本
D5  架构合规       d5_architecture/       45个脚本
D6  安全漏洞       d6_security/           10个脚本
D7  代码质量       d7_code/               16个脚本
D8  文档代码同步   d8_doc_sync/            4个脚本
D9  知识覆盖       d9_knowledge/           2个脚本
D10 性能治理       d10_performance/        0个脚本（待施工）
D11 合规完整性     d11_compliance/         7个脚本
D12 AI幻觉检测     d12_ai_hallucination/   3个脚本
Root             根级入口                 7个脚本
Meta             脚本系统自我审计        24个脚本（含健康/阈值/kill switch等）
Gen              生成器                   4个脚本
─────────────────────────────────────────
总计以 `script_manifest.yaml` 的 `total_scripts` 为准（当前生成约 **177**），覆盖率 12/12
```

### 3.2 按退出码分类（CI决策轴）

| 退出码 | 含义 | CI行为 | 对应Severity |
|:---:|------|--------|:---:|
| **0** | 全通过，零Finding | ✅ 通过 | — |
| **1** | 仅有WARNING/INFO（LOW, INFO） | ✅ 通过（不阻断提交） | LOW, INFO |
| **2** | 存在ERROR（HIGH,ERROR） | ❌ 阻断提交 | HIGH, ERROR |
| **3** | 脚本自身崩溃 | ❌ 阻断提交（脚本故障=门禁失效） | CRITICAL |

> 对标 PS-STD-012 §2.1 + 盲点 B10（沉默失败——脚本异常退出但 CI 显示绿色）→ 退出码 3 强制阻断

> **实现模型（混合四档/三档）**：当前工程实践中，退出码分发存在两层约定：
> - **子脚本层**（绝大多数治理脚本）：使用 0/1/2 三档——0=通过，1=有违规/Finding，2=异常/超时。exit 3 保留给进程级不可恢复错误（如 import 失败），实际使用率低。
> - **编排层**（run_all.py）：使用完整四档 0/1/2/3——0=全部通过，1=有 Finding，2=子脚本批量异常或环境问题，3=manifest 真源读失败/解析失败（编排器自身无法运行）。
> - 此混合模型是结构化设计决策：子脚本严重度映射通过 Finding.severity（而非 exit code）表达；编排器用 exit 3 标识"审计基础设施自身不可用"这一元级别故障。

### 3.3 按触发方式分类

| 触发方式 | 说明 | 代表脚本 |
|---------|------|---------|
| **pre-commit钩子** | git commit时自动触发 | GATE-18（全量测试收集） |
| **run_all批量** | `python scripts/governance/run_all.py` | 全维度/指定维度扫描 |
| **独立触发** | `python scripts/governance/dX_*/validate_*.py` | 单维度精确检查 |
| **CI管线** | GitHub Actions触发 | check_architecture_gates.py |

### 3.4 脚本前缀约定（看名知义）

| 前缀 | 含义 | 示例 |
|------|------|------|
| `validate_*` | 校验脚本——产出PASS/FAIL | `validate_frontmatter.py` |
| `detect_*` | 检测脚本——产出Finding列表 | `detect_ruins_references.py` |
| `audit_*` | 审计脚本——产出结构化报告 | `audit_knowledge_gaps.py` |
| `check_*` | 门禁脚本——直接return exit code | `check_architecture_gates.py` |
| `register_*` | 登记脚本——添加新条目到登记表 | `register_module.py` |

> **Vibe Coding AI公约**：前缀 = 代码自文档化。AI 看文件名就知道它是校验还是检测还是审计——无需读源码。

### 3.5 按自动化层级分类（ITIL 对齐）

> 对标 ITIL 4 分层自动化策略——三级递进，每级有不同的人机分工。"先优化流程，再自动化"——流程本身有缺陷时，自动化只会让错误跑得更快。

| 层级 | 名称 | 含义 | 人机分工 | 代表脚本 |
|:---:|------|------|---------|---------|
| **L1** | 标准化作业自动化 | 规则明确、重复性高、人工干预价值有限的任务 | 脚本全自动执行，人工仅在异常时介入 | `validate_frontmatter.py`（D3）、`check_links.py`（D2） |
| **L2** | 决策辅助自动化 | 需数据分析和建议，但最终决策由人工完成 | 脚本产出分析+建议，人工裁定 | `audit_knowledge_gaps.py`（D9）、`detect_ruins_references.py`（D4） |
| **L3** | 智能决策自动化 | 在预定规则下自主做出决策 | 脚本自主决策，必须有完善监控+回退机制 | `check_architecture_gates.py`（D5，CI中硬阻断） |

> **入库自查**：每个新脚本入库前，AI 必须先自问——"这个检查逻辑本身对吗？人工做一遍能发现问题吗？"确认后，再写自动化。

### 3.6 按标签分类（K8s Conformance 对齐）

> 对标 K8s `[Conformance]`/`[Disruptive]` 标签聚焦机制——脚本可被打上多个标签，`--tags` 参数按标签选择执行。

| 标签 | 含义 | 示例应用 |
|------|------|---------|
| `[Quick]` | 快速检查，<5s 完成 | 文件存在性检查、格式校验 |
| `[Security]` | 安全相关扫描 | SAST扫描、密钥检测、CVE审计 |
| `[Disruptive]` | 可能修改文件或影响环境的脚本 | 自动格式化、数据库迁移校验 |
| `[Critical]` | P0优先级，出错必须立即修复 | 编码安全检查、pre-commit核心门禁 |
| `[AI-Generated]` | 针对 AI 产出的专项检查 | 幻觉检测、AI生成代码质量 |
| `[Periodic]` | 周期性运行（非每次提交触发） | 周度审计报告、覆盖率趋势分析 |

> **使用方式**：`python scripts/governance/run_all.py --tags Security,Quick` → 只运行**同时**打有 Security **和** Quick 标签的脚本（AND 语义）。
>
> **自动推导规则**（`generate_script_manifest.py` 生成时自动计算，存入 `script_manifest.yaml`）：
>
> | 来源 | 规则 |
> |------|------|
> | 维度 | D1-D4,D8 → `Quick` / D5,D7 → `Critical` / D6,D11 → `Security`, `Critical` / D9,D12 → `AI-Generated`, `Periodic` / D10 → `Periodic` |
> | 前缀 | `fix_*`, `generate_*` → `Disruptive`（追加） / `audit_*` → `Periodic`（追加） |
> | 优先级 | P0 → `Critical`（追加，若未因维度获得） |
>
> **AI 公约**：新脚本**无需在 `__manifest__` 块中显式声明 tags**——生成器自动从维度+前缀+优先级推导。标签总会出现在 `script_manifest.yaml` 中，run_all.py 从 manifest 读取标签执行过滤。

---

## 4. 脚本三件套入库流程

### 4.1 设计原则

对标 AGENTS.md §6.5（脚本自创入库强制约定）：
- **触发条件**：AI 创建任何 `.py` 文件（行为触发，非语义分类）
- **合法落位**：只有三个去处——`scripts/governance/` / `src/zephyr/` / `tests/`
- **三件套缺一不可**：缺任何一项视为未完成入库

### 4.2 四阶段预检

```
A0 查重   →  检查 scripts/governance/ 下是否已有功能等价脚本
             $ python scripts/governance/run_all.py --list
             有 → 扩展；无 → 继续

A1 定位   →  确定目标位置：
             审核/校验类   →  scripts/governance/{dimension}/
             核心逻辑类    →  src/zephyr/lXX/
             测试类       →  tests/

A2 例外论证 →  不在以上三处的 .py 文件
             必须在 Session Log 中论证：
             "为什么不能放入标准位置" + "为什么是真正的一次性"
             论证不充分 = 入库失败
```

### 4.3 三件套强制清单

| 步骤 | 内容 | 验证方法 |
|:---:|------|---------|
| **A 落位** | 放入 `scripts/governance/{dimension}/`，文件名遵循 `validate_*` / `detect_*` / `audit_*` / `check_*` / `register_*` 约定 | 文件存在于正确位置 |
| **B manifest注册** | 在 `scripts/governance/script_manifest.yaml` 添加条目（dimensions + priority + timeout + args + description） | `python scripts/governance/check_registry_consistency.py` → 零不一致 |
| **C 运行验证** | `python scripts/governance/{dimension}/{script}.py --warn-only` → exit 0 + 零诊断 | 四档退出码（0=全通过/1=警告/2=错误/3=崩溃） |

> **清单生成（病根闭环）**：`script_manifest.yaml` 为 **生成物**——须在各 `.py` 内维护 `__manifest__` 并运行 `python scripts/governance/generators/generate_script_manifest.py`。生成器 **同时支持**：（1）ASCII 三引号包裹的 YAML；（2）模块顶层的 `__manifest__ = { ... }` **dict 字面量**（`ast` 解析）。历史上仅支持（1）导致（2）被误报为「缺失 manifest」、清单与 `run_all` 漂移。

### 4.4 入库验证矩阵

> 对标 K8s/CNCF 一致性认证 15 项自动验证检查——新脚本入库前必须通过以下矩阵中的所有强制性检查。

| # | 检查项 | 类型 | 验证方法 | 不通过后果 |
|---|--------|:---:|---------|----------|
| V1 | 文件存在于正确维度目录 | MUST | 文件系统检查 | 拒绝入库 |
| V2 | 文件名遵循前缀约定（validate_/detect_/audit_/check_/register_） | MUST | 正则匹配 | 拒绝入库 |
| V3 | manifest 条目完整（dimensions + priority + timeout + args + description） | MUST | `check_registry_consistency.py` | 拒绝入库 |
| V4 | `sys.stdout.reconfigure(encoding='utf-8')` 已添加 | MUST | 源码正则扫描 | 拒绝入库 |
| V5 | 脚本可独立运行（exit ≤ 1） | MUST | `python script.py --warn-only` | 拒绝入库 |
| V6 | 全量回归不破坏（run_all.py 全维度通过） | MUST | `python run_all.py` | 拒绝入库 |
| V7 | docstring 覆盖"参数/返回值/副作用" | SHOULD | AST 解析 | 警告 |
| V8 | shebang 已添加（`#!/usr/bin/env python3`） | SHOULD | 文件头检查 | 警告 |
| V9 | 退出码约定遵守（0/1/2/3 四档） | MUST | 运行后检查 `$?` | 拒绝入库 |
| V10 | `--warn-only` 参数已实现 | MUST | `python script.py --warn-only --help` 含该参数 | 拒绝入库 |
| V11 | 绝对路径使用（无相对路径引用） | MUST | 源码正则扫描 | 拒绝入库 |
| V12 | 异常全捕获（顶层 try/except → exit 3） | MUST | AST 检查 | 拒绝入库 |
| V13 | 与已有脚本无功能重叠（A0 查重通过） | MUST | 人工/AI 审查 | 拒绝入库 |

> **自动化执行**：V1-V12 由 `validate_script_onboarding.py` 自动检查；V13 需 AI 判断。

### 4.5 插件接口契约（Plugin Contract）

> 对标 Sonobuoy Plugin Skeleton + Terraform pre-commit hooks——定义脚本接入 `run_all.py` 编排的最小接口要求。任何遵守此契约的脚本可被 `run_all.py` 自动发现和调度。

```yaml
# Plugin Contract v1.0 — 所有治理脚本必须满足的接口约定

contract:
  name: "governance-script-plugin"
  version: "1.0.0"

  # 一、命令行接口
  cli:
    required_args:
      - name: "--warn-only"
        type: flag
        description: "退出码 ≤ 1，不因 ERROR 阻断"
    optional_args:
      - name: "--output"
        type: path
        description: "输出文件路径（默认 stdout）"
      - name: "--verbose"
        type: flag
        description: "输出详细信息"

  # 二、退出码约定
  exit_codes:
    0: "全通过，零Finding"
    1: "仅有 WARNING/INFO"
    2: "存在 ERROR——阻断"
    3: "脚本自身崩溃——阻断"

  # 三、输出格式
  output:
    format: "JSONL"
    schema: "Finding Schema"
    encoding: "UTF-8"

  # 四、manifest 注册
  manifest:
    file: "scripts/governance/script_manifest.yaml"
    required_fields:
      - dimensions
      - priority
      - timeout
      - args
      - description
```

> **大白话**：插件契约就是"入群规则"——脚本想加入 run_all.py 大家庭，必须遵守四条：参数格式一致、退出码一致、输出格式一致、登记信息一致。就像快递包裹——不管里面装什么，外包装必须贴标准面单。

---

## 5. run_all.py 调度规范

### 5.1 接口契约

```python
# scripts/governance/run_all.py
def run_all_dimensions(dimensions: list[str] = None) -> dict:
    """运行全维度或指定维度的审计扫描"""
    ...

def run_single_dimension(dimension: str) -> list[Finding]:
    """运行单维度审计扫描"""
    ...
```

### 5.2 参数约定

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--dimensions` / `-d` | list[str] | 全部 | 指定运行的维度（如 `d1,d3,d5`） |
| `--list` / `-l` | flag | — | 列出所有已注册脚本及描述 |
| `--dry-run` | flag | — | 只列出将执行的脚本，不真正运行 |
| `--verbose` / `-v` | flag | — | 输出每条Finding的详细信息 |
| `--warn-only` | flag | — | 退出码 ≤ 1（不因ERROR阻断——用于审计查看） |
| `--output` / `-o` | path | stdout | 输出文件路径 |
| `--tags` / `-t` | list[str] | — | 按标签选择脚本（如 `--tags Security,Quick`）。§3.6 定义合法标签 |
| `--depth` / `-dp` | enum | `full` | 验证深度：`quick`（快速扫描，<5s）/ `full`（标准扫描）/ `deep`（深度扫描，含知识分析） |

### 5.3 顺序依赖

维度不是独立运行的——它们存在依赖链：

```
D1 STRUCT → D3 META → D5 ARCH → D8 SYNC
D2 LINK   → D4 PATH → D11 COMPL → D9 KNOW → D12 HALLU
D6 SEC    → D7 CODE → D10 PERF
```

**调度规则**：
- 同一依赖链上的维度必须**串行执行**（前一个维度修复完成，后一个维度才能正确解析）
- 不同依赖链之间可以**并行执行**
- D1 是最前置依赖——文件结构损坏会导致所有下游维度误报

### 5.4 超时策略

| 维度类型 | 超时（单维度） | 超时（全量） |
|---------|:---:|:---:|
| 文件扫描类（D1,D2,D3,D4） | 30s | 120s |
| 内容分析类（D5,D6,D7,D8） | 60s | 240s |
| 知识/AI类（D9,D10,D11,D12） | 120s | 300s |
| **全局硬超时** | — | **600s（10分钟）** |

超时后的脚本标记为 exit code 3（脚本崩溃）——强制阻断。

### 5.5 编码铁律

所有脚本文件开头必须：

```python
import sys
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
```

> Windows 终端默认 GBK 编码 → emoji/中文输出崩溃 → 强制 UTF-8

### 5.6 产出物命名规范

run_all.py 和独立脚本的产出物按以下格式命名，保证任何人看到文件名即知内容：

| 阶段 | 文件名模式 | 示例 |
|------|-----------|------|
| C1 扫描原始输出 | `scan-{dimension}-{YYYYMMDD}.json` | `scan-d2-20260425.json` |
| C2 分类后 Finding | `findings-{dimension}-{YYYYMMDD}.jsonl` | `findings-d2-20260425.jsonl` |
| C3 单维度报告 | `RPT-AUDIT-{dimension}-{YYYYMMDD}.md` | `RPT-AUDIT-D2-20260425.md` |
| C3 全维度报告 | `RPT-AUDIT-FULL-{YYYYMMDD}.md` | `RPT-AUDIT-FULL-20260425.md` |
| C3 周度周期报告 | `RPT-AUDIT-PERIODIC-WEEKLY-{YYYYMMDD}.md` | `RPT-AUDIT-PERIODIC-WEEKLY-20260502.md` |
| C3 增量差异报告 | `RPT-AUDIT-DELTA-{YYYYMMDD}.md` | `RPT-AUDIT-DELTA-20260502.md` |
| C4 修复日志 | `remediation-log-{YYYYMMDD}.md` | `remediation-log-20260502.md` |
| C5 知识条目 | `KE-{NNN}-{topic}.md` | `KE-035-encoding-lesson.md` |

> **唯一定位公式**：`{文件类型前缀}-{维度|编号}-{日期}`（维度不适用时用编号）。AI 看文件名即知内容——无需读文件。

---

## 6. 与任务系统的集成接口

### 6.1 集成模式：脚本失败 → 任务阻塞

当脚本系统检测到违规时，通过任务系统 MOD-INF-006 的门禁体系（G0-G7）将关联任务置为 BLOCKED：

```
脚本系统                              任务系统
────────                              ────────
run_all.py 产出 Finding              ↓
  ↓
Finding.severity = CRITICAL/HIGH
  ↓
GATE-n 判定 → FAIL                   ↓
  ↓
关联任务的 status → BLOCKED           (MOD-INF-006 §4 G0-G7)
  ↓
修复 Finding → GATE-n 重跑 → PASS     ↓
  ↓
关联任务的 status → TODO              (MOD-INF-006 §5 M1-M11)
```

### 6.2 状态转换映射

| 脚本系统输出 | 任务系统状态 | 说明 |
|-----------|:---:|------|
| exit 0（全通过） | 任务状态不变 | 正常流程 |
| exit 1（警告） | 任务 → `⚠️ WARNING` | 不阻塞，日志记录 |
| exit 2（错误） | 关联任务 → `BLOCKED` | Finding 必须修复才能解除阻塞 |
| exit 3（崩溃） | **所有活跃任务** → `BLOCKED` | 门禁自身故障=系统不可信 |

### 6.3 Finding → 任务卡自动创建

| Finding.severity | 是否自动创建任务卡 | 关联Gate |
|:---:|:---:|:---:|
| CRITICAL | ✅ 自动创建（P0） | G0-G7 阻断 |
| HIGH | ✅ 自动创建（P1） | G0-G7 阻断 |
| MEDIUM | ⚠️ 手动决定 | 警告不阻断 |
| LOW | ❌ 不创建 | — |
| INFO | ❌ 不创建 | — |

### 6.5 Finding Schema 新增字段：recommendation

> 对标 ITIL Level 2（决策辅助自动化）——MEDIUM 及以上 Finding 应包含 `recommendation` 字段，给出修复建议但不自动执行。

| 字段 | 类型 | 说明 |
|------|------|------|
| `recommendation` | string | 修复建议——人类可读的操作指引。仅建议，不执行 |
| `recommendation_type` | enum | `auto_fixable`（可自动化修复）/ `manual_only`（必须人工修复）/ `needs_review`（需进一步分析） |
| `recommended_action` | enum | `modify_file` / `create_task` / `consult_owner` / `ignore` |

> **大白话**：脚本找到问题后不光说"这里坏了"，还要说"修它的方法是..."——但只是建议，修不修、怎么修，由人决定。

---
### 6.4 task_id 格式约定

脚本系统创建的追踪任务使用 `OPS-{SEQ}` 命名空间（对齐 MOD-INF-006 §3.2.1 task_id 的 `{NAMESPACE}-{SEQ}` 格式——脚本系统属 OPS 操作域）：

```
OPS-001: D1 维度脚本注册验证任务
OPS-002: D3 维度 frontmatter 合规修复任务
...
```

---

## 7. 脚本质量标准

### 7.1 质量文档

完整标准定义在独立文件：**SCRIPT-QUALITY-001**

| 属性 | 值 |
|------|-----|
| 路径 | `D:\ZephyrAlpha\scripts\governance\quality-standard.md` |
| 范围 | 8 维度 × 38 条款（22 MUST + 16 SHOULD） |
| 版本 | 1.0.0 |

### 7.2 核心条款速查（本蓝图仅列MUST项）

| 条款ID | 维度 | 要求 | 类型 |
|--------|------|------|:--:|
| ENC-001 | 编码安全 | 脚本文件必须是 UTF-8 | MUST |
| ENC-002 | 编码安全 | `sys.stdout.reconfigure(encoding='utf-8')` | MUST |
| ENC-003 | 编码安全 | Python `open()` 必须 `encoding='utf-8'` | MUST |
| SC-001 | 自身一致 | 脚本内部路径必须绝对路径 | MUST |
| SC-002 | 自身一致 | docstring 覆盖"参数/返回值/副作用" | MUST |
| SC-007 | 自身一致 | shebang `#!/usr/bin/env python3`（Unix兼容） | MUST |
| SC-005 | 自身一致 | 脚本不能自己修改自己的源码 | MUST |
| INT-001 | 集成接口 | 遵守四档退出码约定（0/1/2/3） | MUST |
| INT-002 | 集成接口 | 捕获所有异常，转为 exit 3 | MUST |
| INT-003 | 集成接口 | `--warn-only` 参数 → exit 0/1 | MUST |

完整条款列表见 `quality-standard.md`。

### 7.3 质量标准基线的变更控制

- 新增 MUST → 需 Owner 审批
- SHOULD → MAY 升级 → AI 可自主实施
- MUST → SHOULD 降级 → 需 Owner 审批（合规放松是高风险变更）

---

## 8. 容量估算

### 8.1 当前规模

| 维度 | 当前值 | 说明 |
|------|:---:|------|
| 脚本总数 | **177**（以生成器为准） | script_manifest.yaml 的 `total_scripts` |
| 维度数 | 12 | D1-D12 |
| 单维度最大脚本数 | **45**（D5） | 架构合规最密集 |
| 单维度最小脚本数（已登记维） | **0**（D10 占位） | 性能治理待施工；非空维最小为 2（D2/D9） |

### 8.2 容量上限设计

| 维度 | 当前规模 | 设计上限 | 超限策略 |
|------|:---:|:---:|---------|
| 单维度脚本数 | **0**~45 | **50** | 超过 50 考虑拆分为子维度（如 D5 → D5a/D5b） |
| 全局脚本总数 | ~177（manifest 登记口径） | **300** | 超过 300 考虑脚本分组 + 层级化 manifest |
| 每周 Finding 数 | ~200 | ~500 | 降低扫描频率 或 提高阈值 |
| SQLite 单文件 | <10MB | 140TB（SQLite上限） | 不会触及——SQLite 对百万行以内无压力 |
| pre-commit 钩子数 | 5 核心 | 10 | 过 10 分组并行——避免阻塞提交时间过长 |
| 扫描总耗时 | ~50s | 600s（全局硬超时） | 超时部分维度标记为 skip + WARNING |

### 8.3 扩展触发条件

触发维度扩容的阈值：
- 单维度脚本数 ≥ 8 → 结构审查——是否需要拆子维度
- 全局脚本数 ≥ 150 → 架构审查——manifest 是否需要分层
- 扫描耗时 ≥ 300s → 性能审查——是否需要增量扫描/缓存

### 8.4 SLA/SLO 度量指标

> 对标 ITIL 服务级别管理——量化脚本系统的服务水平目标，让"系统是否健康"有数字可查。

| 指标 | 目标值 | 测量方式 | 当前基线 |
|------|:---:|---------|:---:|
| **系统可用性** | ≥ 99% | `run_all.py` 全维度成功率 | 待测量 |
| **MTTR（平均修复时间）** | CRITICAL ≤ 24h / HIGH ≤ 72h | Finding 创建→关闭时间差 | 待测量 |
| **扫描覆盖率** | 100% 文件被至少一个维度覆盖 | 被扫描文件数 / 项目总文件数 | 待测量 |
| **假阳性率** | ≤ 5% | 人工确认后标记为 FALSE_POSITIVE 的 Finding 占比 | 待测量 |
| **门禁阻断率** | ≤ 2%（正常提交被误阻断） | pre-commit 被阻断后人工判定为误杀的占比 | 待测量 |
| **脚本健康度** | 100% 脚本可正常运行（exit ≤ 1） | `run_all.py` 全维度 warn-only 通过率 | 待测量 |

---

## 10. 施工 Phase 规划

### 最小闭环 MVP ✅ 已完成

```
D1-D5  现有脚本输出统一化为 Finding Schema 格式
       → scripts/governance/run_all.py 已可用
       → 全部脚本已注册（script_manifest.yaml）
       → pre-commit 精简配置可用
       → 四档退出码（0/1/2/3）在 run_all.py 中已实现
```

### 扩展覆盖（施工中）

| 任务 | 优先级 | 状态 |
|------|:---:|:---:|
| C2 分类器——去重 + 根因聚类 | P1 | 📋 Backlog |
| D6 安全扫描深度升级 | P1 | 📋 Backlog |
| C3 审计报告自动生成 | P1 | 📋 Backlog |
| D12 幻觉检测 v1（SelfCheckGPT 零资源方案） | P1 | 📋 Backlog |
| Finding → 任务卡自动创建（§6.3 集成） | **P0** | 📋 **本蓝图=施工依据** |
| C5→C1 反馈闭环——Finding模式→扫描规则升级 | P1 | 📋 Backlog |

### 系统化

| 任务 | 优先级 | 状态 |
|------|:---:|:---:|
| C4 修复跟踪器——Finding 全生命周期管理 | P2 | 📋 Backlog |
| C5 知识沉淀自动化——CRITICAL→KE条目 | P2 | 📋 Backlog |
| SQLite 存储 + 竖切查询 | P2 | 📋 Backlog |
| entity-graph 构建（D12 幻觉检测完全体） | P2 | 📋 Backlog |
| 里程碑门禁点——设计审查/发布前/归档前自动化检查（对标 NASA SRR→PDR→CDR→TRR→SAR） | P2 | 📋 Backlog |

---

## 11. 依赖关系

| 依赖模块 | 类型 | 内容 | 版本要求 |
|---------|------|------|---------|
| MOD-INF-001 (capacity-assurance) | runtime | 容量预算检查 + SLO 监控 + Error Budget + Kill Switch | 2.0.0 |
| MOD-INF-003 (task-card-kms) | runtime | Finding → CRITICAL 自动创建任务卡 | 1.0.0 |
| MOD-INF-004 (vibe-coding-pipelines) | contract | 脚本系统是双管线审计侧的脚本基础设施 | 1.0.0 |
| **MOD-INF-006 (task-system)** | **contract** | **G0-G7门禁体系 + M1-M11管线节点——脚本失败↔任务状态的核心接口** | **0.3.0** |
| PS-STD-012 (规则验证标准) | contract | V1~V4 验证分级 + 阻断/警告规则定义 | 1.1.0 |
| PS-STD-001 (元数据注册表) | contract | frontmatter schema + META-V 验证规则 | 当前版本 |
| SCRIPT-QUALITY-001 | contract | 脚本质量 8 维度 × 38 条款 | 1.0.0 |

---

## 12. 风险与后果

### 12.1 风险矩阵

| # | 风险 | 概率 | 影响 | 缓解策略 |
|---|------|:---:|:---:|---------|
| R1 | **审计疲劳**——扫描 Finding 过多，CRITICAL 被淹没 | 高 | 高 | 严格执行严重度分级；CRITICAL 24h 内处理 |
| R2 | **沉默失败**——脚本异常退出但 CI 显示绿色 | 中 | **极高** | 退出码严格约定（0/1/2/3），exit 3 = 阻断 |
| R3 | **审计的审计**——审计脚本本身有 bug | 中 | 高 | 审计脚本必须通过自身的三件套入库验证 |
| R4 | **AI 自我修改**——AI 改审计规则掩盖问题 | 低 | **极高** | Finding Schema + 严重度分级 → Immutable 层，AI 只能读取 |
| R5 | **单人项目瓶颈**——审计独立性无法保障 | 高 | 中 | 不同 AI 模型交叉验证（Claude审GLM修复、Opus审Claude修复） |
| R6 | **过度工程**——12维度×5阶段×3轴 = 180种组合 | 中 | 低 | 分阶段 rollout——先 P0 维度跑通，按反馈决定 beta |

### 12.2 正面后果

- **自动化门禁**：git commit 自动阻断 V1 违规（frontmatter 缺失）——不再依赖人工记忆
- **统一输出**：全部脚本统一 Finding Schema → 跨维度趋势分析
- **AI 新手引导**：新 session AI 读完蓝图 → 知道"脚本系统存在" + "怎么运行检查"
- **可审计性**：Finding append-only 日志 + 退出码约定 → 每个发现可追溯

### 12.3 负面后果

- **维护负担**：Finding Schema 变更 → 全部脚本输出逻辑同步更新
- **假阳性噪声**：自动化扫描可能产大量 LOW/INFO → 需持续调优阈值
- **学习成本**：Owner 需理解 Finding Schema 字段含义才能有效使用审计报告

### 12.4 盲点清单（系统设计易遗漏的审计死角）

以下盲点不在主风险矩阵中，但可能导致审计体系系统性失效：

| # | 盲点 | 为什么重要 | 缓解策略 |
|---|------|-----------|---------|
| **B4** | **审计报告 TTL** | 报告堆积，过期报告误导决策 | 审计报告 TTL：周报 30 天、月报 90 天、事故报告 permanent |
| **B5** | **跨维度关联** | 一条断链可能是编码损坏→路径失效→元数据丢失的连锁反应，三个维度报告同一根因 | C2 分类阶段做根因聚类，标记 `related_finding` |
| **B6** | **审计覆盖率** | 部分文件/目录从未被扫描但无人知晓 | C1 扫描必须记录"扫描了什么"和"没扫描什么"，排除项显式声明 |
| **B7** | **审计结果版本化** | 上周报告显示 OPEN，本周已 FIXED——但旧报告不变，历史状态丢失 | Finding 状态变更用 append-only 日志，不覆盖旧记录 |
| **B8** | **AI 产出审计盲区** | AI 生成的代码/文档"看起来正确但逻辑有误"，纯规则扫描器检测不到 | D12 幻觉检测维度——用 AI 检测 AI 的产出 |
| **B9** | **配置漂移** | ruff/mypy/bandit 配置文件被悄悄修改，审计基线变了但无人知道 | 配置文件本身纳入 D11 合规审计 |
| **B11** | **时间戳精度** | 只记日期不记时间 → 无法做精确 MTTR（平均修复时间）分析 | Finding Schema 所有时间字段用 ISO 8601 含时区 |
| **B12** | **反馈回路断裂** | 审计发现问题后，问题没有自动流入两条生产线 | CRITICAL → 自动创建任务卡（§6.3）；HIGH → Backlog；MEDIUM → 知识库 |
| **B13** | **缺少里程碑门禁** | pre-commit 只覆盖提交时刻——设计审查、发布前、归档前都没有自动化检查点 | beta 新增里程碑门禁矩阵（对标 NASA SRR→PDR→CDR→TRR→SAR） |

> B1（审计自身的审计）= 风险 R3 | B2（审计疲劳）= 风险 R1 | B3（修复验证独立性）= §6.1 | B10（沉默失败）= 风险 R2 — 已在主风险矩阵中覆盖。

---

## 13. 脚本系统运维与自我监控

> **为什么要这一章**：ITIL 4 最核心的原则之一是"不仅要监控业务系统，更要监控自动化系统本身的健康状态"。ServiceNow 2024 年运维报告：40% 企业存在过度依赖自动化却忽视自动化系统自身监控的风险。脚本系统如果自己出了问题但无人知晓——所有门禁形同虚设。这是"审计的审计"问题。

### 13.1 系统健康自检

**核心问题**：谁来审计审计系统？

**答案**：脚本系统必须有**自我监控维度**——一套独立于 12 维度的 Meta 维度脚本，专门检查脚本系统自身是否健康。

| 自检项 | 检查内容 | 频率 | 异常行为 |
|--------|---------|:---:|---------|
| `run_all.py` 可执行性 | `run_all.py --list` 是否能正常运行 | 每次 CI | 全部门禁失效 → 紧急阻断 |
| 全脚本可运行性 | 全部脚本逐一 `--warn-only`，exit ≤ 1 | 每周 | 标记故障脚本 + 创建修复任务 OPS |
| manifest 一致性 | `check_registry_consistency.py` 零不一致 | 每次 pre-commit | 拒绝提交直到 manifest 修复 |
| 输出格式合规 | 所有脚本输出符合 Finding Schema | 每周 | 标记格式违规脚本 |
| 依赖完整性 | `run_all.py` 导入不报 ImportError | 每次 CI | 紧急阻断 |
| 磁盘空间 | `scripts/governance/` 下无意外大文件 | 每周 | 警告 |

> **落地方式**：`scripts/governance/meta/validate_script_system_health.py`（Meta 维度——第 13 维度，脚本系统的自我审计）

### 13.2 应急回退机制

> 对标 ITIL："保持手工操作能力，定期进行应急演练——确保在自动化系统故障时能够快速切换。"

当脚本系统自身发生故障导致无法正常提交代码时，必须有一条**不受脚本系统约束的紧急通道**。

**紧急绕过流程**（仅限以下场景）：

| 场景 | 触发条件 | 绕过方式 | 事后要求 |
|------|---------|---------|---------|
| 脚本系统崩溃 | `run_all.py` ImportError / SyntaxError | `git commit --no-verify` 绕过 pre-commit | 24h 内修复脚本系统 + Session Log 记录绕过原因 |
| 紧急热修复 | 生产问题需立即提交，但脚本误报阻断 | Owner 确认后 `git commit --no-verify` | Session Log 记录 + 修复脚本误报规则 |
| 批量迁移 | 大规模文件重组，脚本误报数千条 | `SKIP=all git commit` | Session Log 记录 + 迁移完成后立即运行全量审计 |

**绕过安全阀**：
- 每次绕过必须在 Session Log 中记录：时间 + 原因 + 绕过命令 + 事后修复承诺
- 绕过不能成为习惯——同一原因绕过 ≥ 2 次 → 脚本规则需要修正
- 绕过日志由 `meta/validate_emergency_bypass_log.py` 审计

> **大白话**：消防通道平时不能走，但着火时必须畅通。脚本系统也一样——正常运行时不绕过，但系统自己着火（崩溃）时必须有应急通道。过完火后要写报告（Session Log），并且要修好消防系统（修复脚本）。

### 13.3 版本升级与兼容性

脚本系统自身的升级遵循以下原则：

- **向后兼容优先**：新版本 `run_all.py` 必须能运行旧版本脚本（通过 §4.5 Plugin Contract 保证）
- **弃用公示期**：废弃一个脚本参数或输出格式时，至少保留一个 Phase（约 1-2 周）过渡期
- **回滚计划**：每次 `run_all.py` 重大升级必须有 `git revert` 回滚路径

### 13.4 定期应急演练

> 对标 ITIL——"成功的自动化项目通常有 60% 的精力投入在流程梳理和规则制定上，只有 40% 用于技术实现"（IDC 调研数据）。

| 演练类型 | 内容 | 频率 |
|---------|------|:---:|
| 脚本故障演练 | 人为破坏一个脚本，验证 Meta 维度能否检测到并报告 | 每月 |
| 紧急绕过演练 | 模拟脚本系统全部故障，走一遍 `--no-verify` 流程 | 每季度 |
| 恢复演练 | 从 `git revert` 恢复脚本系统到上一个健康版本 | 每季度 |

---

## 治理信息

### SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| 脚本系统的架构决策（12维度+5阶段） | **本文档 §3-§6** | 候选池设计文档 v0.2.0 |
| Finding Schema 字段定义 | **本文档 §4.3（旧版蓝图）** | — |
| 实施阶段与优先级 | **本文档 §10** | 候选池设计文档 |
| 脚本模块与 manifest 关联 | **script_manifest.yaml** | — |

**任何与本蓝图冲突的定义，以本蓝图为准。**

### 消费者注册

| Tier | 消费者 | 依赖内容 |
|:----:|--------|---------|
| Tier 1 | 施工图 | 本蓝图所有决策 |
| Tier 2 | MOD-INF-006（task-system） | §6 集成接口——脚本失败↔任务状态 |
| Tier 3 | scripts/governance/*.py（全部脚本） | §3 分类体系 + §5 调度规范 + §7 质量标准 |

### 修改条件

| 变更类型 | 审批要求 |
|---------|---------|
| 决策新增/修改 | Owner 审批 |
| Finding Schema 字段修改 | Owner 审批 + 通知所有脚本维护者 |
| 非关键补充（风险缓解/Phase更新） | AI 可自主 |

---

## 14. 已实现代码完整路径索引

> **AGENTS.md §6.14 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> 脚本系统——第三条生产线，scaffold MVP已交付

### 14.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/l01_infrastructure/script_system/finding.py` | ✅ 已实现 | |

### 14.4 治理脚本

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `scripts/governance/run_all.py` | ✅ 已实现 | |
| `scripts/governance/d5_architecture/validate_blueprint_code_sync.py` | ✅ 已实现 | |
| `scripts/governance/d5_architecture/validate_blueprint_implementation_docs.py` | ✅ 已实现 | |
| `scripts/governance/d5_architecture/validate_cross_references.py` | ✅ 已实现 | |
| `scripts/governance/d5_architecture/validate_ssot.py` | ✅ 已实现 | |
| `scripts/governance/d5_architecture/check_architecture_gates.py` | ✅ 已实现 | |
| `scripts/governance/d5_architecture/validate_blueprint_overlap.py` | ❌ 未实现 | |
| `scripts/governance/d5_architecture/validate_depends_on_format.py` | ✅ 已实现 | |
| `scripts/governance/d5_architecture/validate_layer_deps.py` | ✅ 已实现 | |
| `scripts/governance/d5_architecture/validate_field_ownership.py` | ✅ 已实现 | |
| `scripts/governance/d5_architecture/validate_directory_structure.py` | ✅ 已实现 | |
| `scripts/governance/d5_architecture/validate_interface_contracts.py` | ✅ 已实现 | |
| `scripts/governance/d5_architecture/validate_module_lifecycle.py` | ✅ 已实现 | |
| `scripts/governance/d5_architecture/validate_p0_module_contracts.py` | ✅ 已实现 | |
| `scripts/governance/d5_architecture/validate_arch_review_gate.py` | ✅ 已实现 | |
| `scripts/governance/d5_architecture/validate_yaml_summaries.py` | ✅ 已实现 | |
| `scripts/governance/d5_architecture/validate_three_way_consistency.py` | ✅ 已实现 | |
| `scripts/governance/d5_architecture/validate_code_yaml_alignment.py` | ✅ 已实现 | |
| `scripts/governance/d5_architecture/generate_trigger_wiring_view.py` | ✅ 已实现 | |
| `scripts/governance/d5_architecture/validate_b_track_packages.py` | ✅ 已实现 | |
| `scripts/governance/d5_architecture/validate_handoff_package.py` | ✅ 已实现 | |
| `scripts/governance/d5_architecture/validate_session_log_updated.py` | ✅ 已实现 | |
| `scripts/governance/d5_architecture/validate_autonomy_gate.py` | ✅ 已实现 | |
| `scripts/governance/d5_architecture/validate_lifecycle_refs.py` | ✅ 已实现 | |
| `scripts/governance/d5_architecture/detect_depends_on_cycles.py` | ✅ 已实现 | |
| `scripts/governance/d5_architecture/detect_deprecated_adr_references.py` | ✅ 已实现 | |
| `scripts/governance/d5_architecture/detect_duplicate_module_names.py` | ✅ 已实现 | |
| `scripts/governance/d5_architecture/audit_depends_on_chain_depth.py` | ✅ 已实现 | |
| `scripts/governance/d5_architecture/measure_deprecation_cascade.py` | ✅ 已实现 | |
| `scripts/governance/d5_architecture/validate_deprecated_dependents.py` | ✅ 已实现 | |
| `scripts/governance/d3_metadata/check_naming_convention.py` | ✅ 已实现 | |
| `scripts/governance/d3_metadata/check_frontmatter_metadata.py` | ✅ 已实现 | |
| `scripts/governance/d3_metadata/validate_enum_consistency.py` | ✅ 已实现 | |
| `scripts/governance/d3_metadata/validate_derived_from.py` | ✅ 已实现 | |
| `scripts/governance/d3_metadata/generate_derived_files.py` | ✅ 已实现 | |
| `scripts/governance/d3_metadata/validate_blueprint_registry.py` | ✅ 已实现 | |
| `scripts/governance/d3_metadata/validate_blueprint_provenance.py` | ✅ 已实现 | |
| `scripts/governance/d3_metadata/validate_architecture.py` | ✅ 已实现 | |
| `scripts/governance/d3_metadata/validate_registry_master_index.py` | ✅ 已实现 | |
| `scripts/governance/d3_metadata/generate_rule_catalog.py` | ✅ 已实现 | |
| `scripts/governance/d3_metadata/detect_skip_active_status.py` | ✅ 已实现 | |
| `scripts/governance/d3_metadata/detect_stale_version.py` | ✅ 已实现 | |
| `scripts/governance/d3_metadata/validate_superseded_by.py` | ✅ 已实现 | |
| `scripts/governance/d3_metadata/scan_deep_content.py` | ✅ 已实现 | |
| `scripts/governance/d6_security/detect_vague_terms.py` | ✅ 已实现 | |
| `scripts/governance/d6_security/detect_shell_dangerous.py` | ✅ 已实现 | |
| `scripts/governance/d6_security/detect_secrets.py` | ✅ 已实现 | |
| `scripts/governance/d6_security/detect_keywords_in_logs.py` | ✅ 已实现 | |
| `scripts/governance/d6_security/detect_git_dangerous.py` | ✅ 已实现 | |
| `scripts/governance/d6_security/validate_gate_discipline.py` | ✅ 已实现 | |
| `scripts/governance/d6_security/detect_anchor_file_deletion.py` | ✅ 已实现 | |
| `scripts/governance/d6_security/detect_threading_lock.py` | ✅ 已实现 | |
| `scripts/governance/d6_security/detect_shell_true.py` | ✅ 已实现 | |
| `scripts/governance/d6_security/detect_permanent_file_deletion.py` | ✅ 已实现 | |
| `scripts/governance/d1_structure/validate_config_integrity.py` | ✅ 已实现 | |
| `scripts/governance/d1_structure/run_script_smoke_test.py` | ✅ 已实现 | |
| `scripts/governance/d1_structure/audit_directory_integrity.py` | ✅ 已实现 | |
| `scripts/governance/d1_structure/audit_config_format.py` | ✅ 已实现 | |
| `scripts/governance/d1_structure/sync_policies_index.py` | ✅ 已实现 | |
| `scripts/governance/d1_structure/validate_immutable_core.py` | ✅ 已实现 | |
| `scripts/governance/d1_structure/generate_missing_index_md.py` | ✅ 已实现 | |
| `scripts/governance/d1_structure/validate_index_reality.py` | ✅ 已实现 | |
| `scripts/governance/d1_structure/sync_index_from_manifest.py` | ✅ 已实现 | |
| `scripts/governance/d1_structure/archive_drafts_zone.py` | ✅ 已实现 | |
| `scripts/governance/d1_structure/detect_orphan_py.py` | ✅ 已实现 | |
| `scripts/governance/d1_structure/check_index_integrity.py` | ✅ 已实现 | |
| `scripts/governance/d1_structure/detect_residual_files.py` | ✅ 已实现 | |
| `scripts/governance/d1_structure/detect_temp_files.py` | ✅ 已实现 | |
| `scripts/governance/d1_structure/reset_cbg.py` | ✅ 已实现 | |
| `scripts/governance/d1_structure/audit_findings_by_scope.py` | ✅ 已实现 | |
| `scripts/governance/d7_code/validate_test_coverage.py` | ✅ 已实现 | |
| `scripts/governance/d7_code/validate_import_style.py` | ✅ 已实现 | |
| `scripts/governance/d7_code/validate_docstring_coverage.py` | ✅ 已实现 | |
| `scripts/governance/d7_code/validate_unused_imports.py` | ✅ 已实现 | |
| `scripts/governance/d7_code/validate_type_annotation_coverage.py` | ✅ 已实现 | |
| `scripts/governance/d7_code/validate_init_all.py` | ✅ 已实现 | |
| `scripts/governance/d7_code/validate_fle_imports.py` | ✅ 已实现 | |
| `scripts/governance/d7_code/validate_kb_write_provenance.py` | ✅ 已实现 | |
| `scripts/governance/d7_code/detect_silent_degradation.py` | ✅ 已实现 | |
| `scripts/governance/d7_code/validate_fle_action_metadata.py` | ✅ 已实现 | |
| `scripts/governance/d7_code/detect_pydantic_any_fields.py` | ✅ 已实现 | |
| `scripts/governance/d7_code/validate_contracts_purity.py` | ✅ 已实现 | |
| `scripts/governance/d7_code/detect_direct_llm_calls.py` | ✅ 已实现 | |
| `scripts/governance/d7_code/detect_missing_encoding.py` | ✅ 已实现 | |
| `scripts/governance/d7_code/validate_test_assertion_depth.py` | ✅ 已实现 | |
| `scripts/governance/d4_paths/detect_ruins_references.py` | ✅ 已实现 | |
| `scripts/governance/d4_paths/detect_deprecated_path_writes.py` | ✅ 已实现 | |
| `scripts/governance/d4_paths/detect_split_delete_ref_commit.py` | ✅ 已实现 | |
| `scripts/governance/d4_paths/detect_excessive_file_moves.py` | ✅ 已实现 | |
| `scripts/governance/d11_compliance/validate_script_quality.py` | ✅ 已实现 | |
| `scripts/governance/d11_compliance/fix_shared_bypass.py` | ✅ 已实现 | |
| `scripts/governance/d11_compliance/validate_commit_message.py` | ✅ 已实现 | |
| `scripts/governance/d11_compliance/validate_manifest_admission.py` | ✅ 已实现 | |
| `scripts/governance/d11_compliance/validate_blueprint_overlap.py` | ✅ 已实现 | |
| `scripts/governance/d11_compliance/validate_truth_source_cascade.py` | ✅ 已实现 | |
| `scripts/governance/d8_doc_sync/validate_document_ttl.py` | ✅ 已实现 | |
| `scripts/governance/d8_doc_sync/detect_ai_products_in_docs.py` | ✅ 已实现 | |
| `scripts/governance/d8_doc_sync/detect_dated_snapshots.py` | ✅ 已实现 | |
| `scripts/governance/d8_doc_sync/validate_document_lifecycle.py` | ✅ 已实现 | |
| `scripts/governance/d2_links/audit_broken_links.py` | ✅ 已实现 | |
| `scripts/governance/d2_links/detect_relative_references.py` | ✅ 已实现 | |
| `scripts/governance/d9_knowledge/detect_duplicated_normative_language.py` | ✅ 已实现 | |
| `scripts/governance/d9_knowledge/detect_orphan_documents.py` | ✅ 已实现 | |
| `scripts/governance/d12_ai_hallucination/validate_session_gate_check.py` | ✅ 已实现 | |
| `scripts/governance/d12_ai_hallucination/validate_session_budget.py` | ✅ 已实现 | |
| `scripts/governance/d10_performance/__init__.py` | ⚠️ 骨架 | |
| `scripts/governance/env_check.py` | ✅ 已实现 | |
| `scripts/governance/status.py` | ✅ 已实现 | |
| `scripts/governance/check_registry_consistency.py` | ✅ 已实现 | |

### 14.5 Meta 自我审计脚本

> 对标 §13.1（系统健康自检）——脚本系统第 13 维度 Meta 层的完整实现。

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `scripts/governance/meta/__init__.py` | ✅ 已实现 | Meta 维度目录初始化 |
| `scripts/governance/meta/validate_script_system_health.py` | ✅ 已实现 | 系统健康六项自检 |
| `scripts/governance/meta/validate_threshold_changes.py` | ✅ 已实现 | 阈值变更审计日志 (§15) |
| `scripts/governance/meta/validate_environment_health.py` | ✅ 已实现 | 运行环境健康检查 (§21) |
| `scripts/governance/meta/validate_false_negatives.py` | ✅ 已实现 | 假阴性检测引擎 (§19) |
| `scripts/governance/meta/manage_kill_switch.py` | ✅ 已实现 | Kill Switch 管理工具 (§16) |
| `scripts/governance/meta/manage_shadow_mode.py` | ✅ 已实现 | Shadow Mode 管理工具 (§17) |
| `scripts/governance/meta/manage_baseline.py` | ✅ 已实现 | Baseline Snapshot 管理 (§18) |
| `scripts/governance/meta/manage_error_budget.py` | ✅ 已实现 | Error Budget 管理引擎 (§21) |
| `scripts/governance/meta/finding_state_machine.py` | ✅ 已实现 | Finding 全生命周期状态机 (§20) |
| `scripts/governance/meta/kill_switch_state.yaml` | ✅ 已实现 | Kill Switch 状态注册 (§16) |
| `scripts/governance/meta/shadow_mode_state.yaml` | ✅ 已实现 | Shadow Mode 状态注册 (§17) |
| `scripts/governance/meta/error_budget_state.yaml` | ✅ 已实现 | Error Budget 状态注册 (§21) |
| `scripts/governance/meta/requirements/requirements-d3.txt` | ✅ 已实现 | D3 维度依赖声明 |
| `scripts/governance/meta/requirements/requirements-d5.txt` | ✅ 已实现 | D5 维度依赖声明 |
| `scripts/governance/meta/requirements/requirements-d9.txt` | ✅ 已实现 | D9 维度依赖声明 |
| `scripts/governance/meta/requirements/requirements-d11.txt` | ✅ 已实现 | D11 维度依赖声明 |
| `scripts/governance/meta/requirements/requirements-d12.txt` | ✅ 已实现 | D12 维度依赖声明 |

### 14.6 共享工具与配置

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `scripts/governance/_shared/thresholds.yaml` | ✅ 已实现 | 关键阈值集中配置 SSoT (§15) |
| `scripts/governance/_shared/thresholds.py` | ✅ 已实现 | 阈值加载器模块 |
| `scripts/governance/QUICKSTART.md` | ✅ 已实现 | AI Session Zero-Memory 冷启动卡片 (§22) |

**新 AI session 读取顺序**：
1. 读本蓝图 §14（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下

---

---

## 15. 关键阈值外置配置 + 变更审计

> **对标 B16（关键阈值外置+变更审计）+ ITIL 4 Configuration Change Audit + Google SRE Comment §2.10（禁止模块级副作用）**

### 15.1 设计原则

关键阈值（AST相似度 0.8 / 假阳性率 5% / Error Budget 消耗速率 2%/h）**不硬编码在任何脚本中**。所有阈值集中在 `_shared/thresholds.yaml`，脚本通过 `_shared/thresholds.py` 的 `get()` 函数按需读取。

### 15.2 阈值配置结构

```yaml
# _shared/thresholds.yaml — 八大阈值分组
scanning:         # 扫描超时策略
finding_quality:  # Finding 质量标准
error_budget:     # Error Budget + Burn Rate
sla_timers:       # SLA 修复截止时间
shadow_mode:      # Shadow Mode 渐进激活
script_health:    # 脚本健康阈值
ast_similarity:   # AST 查重阈值
blueprint_sync:   # 蓝图-代码同步
```

### 15.3 变更审计机制

`thresholds.yaml` 的每次修改 → `meta/validate_threshold_changes.py` 自动生成审计条目（含 old→new diff）写入 `meta/threshold_changes_audit.jsonl`。

### 15.4 AI 自治权限

- AI **可读取**任何阈值作决策参考
- AI **不可修改**任何阈值——修改需 Owner 审批
- 阈值文件纳入 D11 合规审计（对标 §12.4 B9）

---

## 16. Kill Switch 机制

> **对标 B25（Kill Switch）+ ITIL 4 Emergency Change Management + K8s Pod Disruption Budget**

### 16.1 双层保护

| 层级 | 范围 | 触发方式 | 效果 |
|------|------|---------|------|
| **全局冻结** (global_freeze) | 所有新脚本开发 | Error Budget 耗尽自动触发 / Owner 手动 | 只允许修复现有脚本——禁止新脚本入库 |
| **单脚本禁用** (per-script) | 单个脚本 | Owner 手动 `--disable` / 连续失败 N 次自动 | 该脚本停止运行——不影响其他脚本 |

### 16.2 执行机制

`run_all.py` 启动时读取 `meta/kill_switch_state.yaml` → 每个脚本运行前检查：
- 全局冻结 → 拒绝执行所有新脚本（exit 2）
- 脚本被禁用 → 跳过该脚本（记录 KILL-SWITCH 事件）

### 16.3 管理工具

```bash
python scripts/governance/meta/manage_kill_switch.py --list
python scripts/governance/meta/manage_kill_switch.py --disable d7_code/validate_foo.py --reason "误报率 45%"
python scripts/governance/meta/manage_kill_switch.py --enable d7_code/validate_foo.py
```

---

## 17. Shadow Mode 渐进激活

> **对标 B19（Shadow Mode）+ K8s Feature Gates + LaunchDarkly Progressive Rollout**

### 17.1 三阶段释放流程

新脚本入库后不立即激活——经历三阶段渐进释放：

```
Phase 1 → Phase 2 → Phase 3
Shadow     Warn      Active
(7天)      (7天)     (永久)
```

| 阶段 | 行为 | exit code | 阻断提交 |
|------|------|:---:|:---:|
| **Phase 1** (Shadow) | 运行但不阻断——只记录"如果激活会阻断什么" | 强制 0 | ❌ |
| **Phase 2** (Warn) | 输出 WARNING 信息 | 强制 1 | ❌ |
| **Phase 3** (Active) | 正式激活——正常阻断 | 按实际结果 | ✅ |

### 17.2 自动回退

任阶段中假阳性率 > 20%（`thresholds.yaml` 中 `shadow_mode.auto_rollback_fpr_threshold`）→ **自动回退到 Phase 1** + `rollback_count += 1`。

连续回退 3 次 → 自动禁用（Kill Switch per-script）。

### 17.3 管理工具

```bash
python scripts/governance/meta/manage_shadow_mode.py --register d7_code/validate_new.py
python scripts/governance/meta/manage_shadow_mode.py --promote d7_code/validate_new.py
python scripts/governance/meta/manage_shadow_mode.py --check-health --auto-promote
python scripts/governance/meta/manage_shadow_mode.py --rollback d7_code/validate_new.py --reason "假阳性 35%"
```

---

## 18. Baseline Snapshot 对比

> **对标 B18（Baseline Snapshot）+ OWASP ASVS v5 snapshot-based verification + Semgrep CI baseline**

### 18.1 核心流程

每次扫描结果与上次 approved baseline 做 three-way diff：

```
当前 findings.jsonl  vs  基线 current_baseline.jsonl
→ NEW（新增问题）→ RESOLVED（已修复）→ PERSISTENT（持续未修复）
```

### 18.2 PERSISTENT 升级规则

| 严重度 | 连续存在天数 | 动作 |
|--------|:---:|------|
| MEDIUM | ≥ 30 天 | 升级为 HIGH |
| HIGH | ≥ 60 天 | 升级为 CRITICAL |

> 对标 `thresholds.yaml` 中 `sla_timers.persistent_upgrade_days`。

### 18.3 管理工具

```bash
python scripts/governance/meta/manage_baseline.py --save findings.jsonl
python scripts/governance/meta/manage_baseline.py --compare findings.jsonl --json
python scripts/governance/meta/manage_baseline.py --approve findings.jsonl
```

---

## 19. False Negative 检测引擎

> **对标 B17（False Negative 检测）+ 《Building Evolutionary Architectures》Fitness Functions**

### 19.1 Golden Test Case 库

`meta/false_negative_cases/` 下维护一个**已知有缺陷的文档/代码库**（golden set）。
定期用这些已知坏用例验证脚本系统能否检测出来。

### 19.2 检测流程

```
1. 加载 known-bad test case → 2. 运行关联的检测脚本
→ 3. 检查脚本是否产出预期 Finding → 4. 未产出 = 假阴性 → Error Budget 消耗
```

### 19.3 FIT 指标

| 指标 | 含义 | 目标值 |
|------|------|:---:|
| 假阴性检测率 | 已知坏用例被检测出的占比 | ≥ 90% |
| Case Rotation | 每季度至少新增一个 test case | 4+/年 |

---

## 20. Finding 全生命周期状态机

> **对标 B20（Finding 全生命周期）+ ITIL 4 Incident Management + Jira SLA timers**

### 20.1 状态机

```
                    ┌─────────────┐
                    │    OPEN     │──────→ FALSE_POSITIVE → CLOSED
                    └──┬───┬───┬─┘
          ┌────────────┘   │   └─────────┐
          ▼                ▼             ▼
    IN_PROGRESS        WONTFIX       DEFERRED
          │                │
          ▼                ▼
        FIXED         ACCEPTED_RISK
          │
          ▼
       VERIFIED

   ──OVERDUE── (SLA定时器触发 → 从任意状态进入)
```

### 20.2 SLA 定时器

| 严重度 | 修复截止 | 超时升级（小时后） |
|:------:|:---:|:---:|
| CRITICAL | 24h | 48h |
| HIGH | 7d (168h) | 14d (336h) |
| MEDIUM | 30d (720h) | 60d (1440h) |
| LOW / INFO | 无截止 | — |

> 死亡线对齐 `thresholds.yaml` → `sla_timers.fix_deadline_hours`。

### 20.3 状态转换审计

每次状态变更 → append-only audit log → `finding_state_db.json`。

### 20.4 管理工具

```bash
python scripts/governance/meta/finding_state_machine.py --load findings.jsonl
python scripts/governance/meta/finding_state_machine.py --transition <id> --to IN_PROGRESS
python scripts/governance/meta/finding_state_machine.py --check-sla
python scripts/governance/meta/finding_state_machine.py --list OVERDUE
```

---

## 21. Error Budget + Burn Rate + 依赖隔离

> **对标 B14（Error Budget + Burn Rate）+ B21（脚本依赖隔离）+ Google SRE Ch.5-6**

### 21.1 Error Budget 模型

```
Error Budget = 100% - SLO
  可用性 Error Budget = 1% (432 min/月)
  准确率 Error Budget = 5%（允许 ≤ 5% 假阳性）
```

### 21.2 Burn Rate Alert

| 告警级别 | 触发条件 | 动作 |
|---------|---------|------|
| **🔴 Critical** | 1h 内消耗 > 2% Error Budget | Feature Freeze + 脚本系统暂停新脚本开发 |
| **🟡 Warning** | 6h 内消耗 > 5% | 审计报告 + Owner 通知 |
| **Error Budget 耗尽** | 准确率剩余 ≤ 0% | 自动 Feature Freeze——72小时后自动解冻 |

### 21.3 Feature Freeze 联动

Error Budget 耗尽 → `manage_error_budget.py` 自动：
1. 设置 `error_budget_state.yaml → feature_freeze.active = true`
2. 同步设置 `kill_switch_state.yaml → global_freeze = true`
3. 72 小时后自动解冻

### 21.4 脚本依赖隔离

- 各维度分池：**轻量级**（D1-D4，标准库为主）/ **中量级**（D5-D8,D11）/ **重量级**（D9,D10,D12，含 AI/LLM依赖）
- 重量池脚本即使崩溃也不影响轻量池脚本的运行
- 各维度可声明专属 `requirements-{dimension}.txt`——位于 `meta/requirements/`
- 环境健康检查：`validate_environment_health.py`

---

## 22. AI Session Zero-Memory Quickstart Card

> **对标 B15（Zero-Memory Quickstart）+ Google SRE Runbook 精简原则 + Meta Glean 符号索引思想**

### 22.1 为什么需要

新 AI session 冷启动时，读 blueprint.md（~1400 行）+ quality-standard.md（~540 行）+ script_manifest.yaml（~1230 行）= **远超 Token 预算**。需要一份 ≤ 500 tokens 的"零记忆卡片"，让 AI 30 秒内知道脚本系统是什么。

### 22.2 卡片位置

`scripts/governance/QUICKSTART.md`

### 22.3 卡片内容

- 一句话概述
- 3 条最常用命令（`--list` / `run_all.py` / `--diff-ref`）
- 架构地图（10 秒可读）
- 关键文件速查表（7 行）
- 门槛规则（退出码 / pre-commit / 假阳性率）
- 1人+AI 维护备忘

---

## 产出物存放目录

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\script-system\blueprint.md` | 本文件 |
| 业务代码 | `D:\ZephyrAlpha\src\zephyr\script_system\` | 脚本系统核心 |
| 治理脚本 | `D:\ZephyrAlpha\scripts\governance\` | 80+ 治理脚本 |
| 脚本注册表 | `D:\ZephyrAlpha\scripts\governance\script_manifest.yaml` | 脚本登记 SSoT |

---

## 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| Gate Engine (MOD-INF-007) | 治理脚本结果 → 门禁判定 | `run_all.py` → `gate_engine.evaluate()` | 脚本结果触发门禁 |
| Task System (MOD-INF-006) | 脚本执行 → 任务状态变更 | 脚本完成 → `task_repo.update_status()` | 关联任务状态自动更新 |
| Drift Detector (MOD-INF-023) | 治理脚本 → 漂移检测器 | 80+ 脚本 → `drift_detector` 调度 | 脚本作为 drift detector 的检测器 |

---

## 需要更新的相关内容

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint-registry.yaml` | 版本号+完整度 | 蓝图补全后更新 |
| 2 | script_manifest.yaml | `D:\ZephyrAlpha\scripts\governance\script_manifest.yaml` | 新脚本注册 | 新治理脚本入库后更新 |

---

## 独立风险矩阵（拆分自原 §12 风险与后果）

| # | 风险 | 概率 | 影响 | 缓解策略 |
|---|------|:---:|:---:|---------|
| R1 | 治理脚本数量爆炸——80+ 持续增长 | 高 | 中 | 脚本分级（G0-G4）+ 定期清理废弃 |
| R2 | 脚本执行超时——慢脚本阻塞 pre-commit | 中 | 高 | 超时机制（30s）+ 异步执行 |
| R3 | 脚本间依赖断裂——脚本 A 依赖 B 的输出格式变更 | 中 | 高 | 接口契约 + CI 回归测试 |
| R4 | 误报率高——脚本过于严格 | 中 | 中 | warn-only 模式 + 误报反馈 |
| R5 | run_all.py 单点故障——调度器宕机全部脚本停 | 低 | 高 | 脚本可独立运行 + 容错模式 |
| R6 | 跨 IDE 脚本一致性——TRAE/Cursor/RooCode 执行环境差异 | 中 | 中 | Docker 标准化执行环境 |

---

## 独立后果（拆分自原 §12 风险与后果）

**正面后果**：
- 自动化治理覆盖 12 维度（D1-D12）
- pre-commit 自动门禁——提交时阻断问题
- 脚本系统可观测——run_all.py 统一调度和统计

**负面后果**：
- 脚本维护成本增长——每新增模块可能需要新脚本
- warn-only 可能被忽略——不够强制
- 跨 IDE 差异——不同 IDE 的 Python 环境可能不一致

---

---

## §16 Kill Switch 机制

> **已施工 B25**。双层保护：全局冻结 + per-script 禁用。`manage_kill_switch.py` + `kill_switch_state.yaml`。联动 Error Budget Feature Freeze。

## §17 Shadow Mode 渐进激活

> **已施工 B19**。Phase1(Shadow)→Phase2(Warn)→Phase3(Active)。`manage_shadow_mode.py` + `shadow_mode_state.yaml`。假阳性 > 20% → 自动回退。

## §18 Baseline Snapshot

> **已施工 B18**。三态分类 NEW/RESOLVED/PERSISTENT。`manage_baseline.py`。PERSISTENT ≥ 30d → 升级严重度。

## §19 False Negative 检测

> **已施工 B17**。Golden Test Case + Fitness Functions。`validate_false_negatives.py`。已知坏用例检测率 ≥ 90%。

## §20 Finding 全生命周期状态机

> **已施工 B20**。10状态 + SLA定时器 + 状态转换审计。`finding_state_machine.py`。超时 → 自动升级 OVERDUE。

## §21 Error Budget + Burn Rate

> **已施工 B14+B21**。双预算模型 + Critical/Warning Alert + Feature Freeze ← Kill Switch联动。`manage_error_budget.py` + `error_budget_state.yaml`。Burn Rate加速度(B55)。

## §22 Zero-Memory Quickstart Card

> **已施工 B15**。`QUICKSTART.md` — ≤500 tokens AI冷启动。

## §23 Rules File 供应链安全

> **已施工 B43+B44**。Unicode Backdoor 扫描 + SHA256完整性校验。`validate_rules_file_backdoor.py` + `validate_rules_integrity.py`。纳入 pre-commit 硬阻断（CRITICAL发现=exit 2）。

## §24 七大安全与质量引擎

> **已施工 B45-B51**。Script A/B对照(Kayenta) + Trust-Tier T1/T2/T3 + Provenance链 + Slopsquatting幻觉包防御 + Finding仲裁器(5规则) + 时序数据库(SQLite) + Script Rot检测。

## §25 八大精英补全

> **已施工 B52-B59**。退役流程 + 多模型共识(Claude/GLM/Opus) + 费用追踪 + Burn Rate加速度 + C1→C5全链路Tracing + 合规框架映射(OWASP/ISO27001/SOC2/ITIL5) + 人类记忆卡(HUMAN_MEMORY_CARD.md) + E2E基准测试。

## §26 风险更新

| 风险ID | 风险 | 对策 |
|--------|------|------|
| R6 | Rules File Backdoor | validate_rules_file_backdoor.py + validate_rules_integrity.py |
| R7 | Excessive Agency | trust_tier_policy.yaml + validate_trust_tier.py |
| R8 | Slopsquatting | detect_hallucinated_packages.py PyPI验证 |
| R9 | Script静默失效 | detect_script_rot.py 每扫描周期 |
| R10 | Finding矛盾 | arbitrate_findings.py 5规则 |
| R11 | 系统退化 | validate_end_to_end_benchmark.py |
| R12 | Token费用失控 | track_script_costs.py per-call tracking |

---

## 27. 第四层盲点清单：AI会话与1人维护专域 (B60-B91)

> **审查驱动**：2026-05-05 DeepSeek V4 对 MOD-INF-005 全文及当时已登记的治理脚本穿透审计。前三层盲点 (B1-B59) 覆盖了系统架构、运维、安全等「系统视角」死角——但**第四层盲点**聚焦「AI 作为开发主体 + 1 人作为唯一维护者」这一独特语境下的死角。这是传统软件工程教科书不覆盖、专业机构也不研究的领域。

### 27.1 AI 会话上下文管理 (B60-B62)

> 对标 Cursor Context Window Management + Windsurf Cascade Memory + Anthropic CLAUDE.md 长会话策略

| # | 盲点 | 为什么重要 | 缓解策略 |
|---|------|-----------|---------|
| **B60** | **AI 上下文窗口污染** | 系统每次增长，AI session 注入的蓝图/脚本/finding 越来越多，最终超过 token 预算 → AI 开始"遗忘"关键约束。当前蓝图 1400 行 + quality-standard 540 行 + manifest 1230 行 = 远超单次注入能力 | 建立「AI 消费优先级」：Tier-1 必注入（QUICKSTART.md ≤500tokens）→ Tier-2 按需注入（脚本管脚本、蓝图管蓝图）→ Tier-3 禁止注入（完整 manifest 不允许一次全吞）。§22 QUICKSTART.md 已经做了 Tier-1 |
| **B61** | **AI 会话中断-续接漂移** | AI session 在修复脚本中途断开（token 耗尽/网络/IDE 崩溃），新 session 启动后不知道前一个 session 做了什么 → 重复劳动、半成品修复、状态不一致 | 为每个治理脚本增设 `meta/script_fix_state.yaml`——记录「谁在修、修到哪了、下一步是什么」。对标数据库 WAL (Write-Ahead Log) 的断点续传思想 |
| **B62** | **AI 使用的规则版本过期** | AGENTS.md / blueprint.md 更新后，AI session 可能仍然使用缓存的旧版规则执行判断。4 次审查都发现过「版本号已在 frontmatter 更新但 header 遗漏」这类漂移 | 新增 AI session 启动时的「规则新鲜度检查」：对比注入文件的 `valid_from` 时间戳与当前时间。超过 7 天的规则文件标记 `[STALE]` 警告。`validate_rules_integrity.py` 已覆盖完整性，缺「时效性」维度 |

### 27.2 AI 反馈回路安全 (B63-B65)

| # | 盲点 | 为什么重要 | 缓解策略 |
|---|------|-----------|---------|
| **B63** | **Finding 反馈中毒** | AI 读取自己历史 session 产出的 findings，将其当作「当前系统状态」做决策，但很多 findings 已修复/过时。AI 被自己的旧输出误导 | Finding 在纳入 AI 上下文前增加 `staleness_check`：如果 `lifecycle_status ∈ {FIXED, FALSE_POSITIVE, CLOSED}` 或 `timestamp > 30天` → 标记 `[ARCHIVED]` 不注入 AI 上下文 |
| **B64** | **AI 自修复振荡** | 脚本发现 issue A → AI 修复 → 修复引入 issue B → 脚本发现 B → AI 修复 → 引入 A。形成无限振荡循环。多见于 D5 架构合规和 D7 代码质量之间的互相触发 | 新增 `meta/detect_fix_oscillation.py`——跟踪同一文件的连续 3+ 次修复-发现循环，检测到振荡 → 停止自动修复，升级为人工决策 |
| **B65** | **跨脚本接口断裂** | AI 修复脚本 X，改了它的输出格式，但没有检查下游脚本 Y 和 Z 是否依赖该格式 → Y/Z 静默失效 | 脚本接口变更时，`run_all.py` 解析 manifest 的 `depends_on_scripts` 字段（新字段——脚本间依赖声明），递归运行受影响的下游脚本并做回归对比 |

### 27.3 1人+AI维护专属 (B66-B69)

| # | 盲点 | 为什么重要 | 缓解策略 |
|---|------|-----------|---------|
| **B66** | **维护者缺席协议** | 唯一的 Owner 生病/出差/离职 3 个月 → 系统无人看管。Kill Switch 自动解冻、Error Budget 自动重置——但这些自动化在 Owner 不在时可能做出错误决策 | 新增「维护者缺席模式」：Owner 主动设置 `maintainer_absent_until: 2026-09-01` → 自动冻结（禁止所有自动决策）、自动降级（所有阻断→警告）、自动记录（所有 Finding 排队等待 Owner 回来批量审批）。对标 ITIL 4 "Emergency Change Advisory Board" 的自动化版 |
| **B67** | **AI 模型迁移风险** | 项目用 Claude 4 建、用 Claude 4.5 维护——但 2026 年底 Owner 可能切换到 GLM-5 / DeepSeek V5 / GPT-5。不同 AI 模型对同样的 AGENTS.md 理解不同、行为不同 | 建立 `meta/model_compatibility_matrix.yaml`——记录每个脚本在哪些模型上测试过、行为差异。`validate_cross_model_consensus.py`（B53 已施工）可扩展为定期多模型回归测试 |
| **B68** | **人类知识巴士系数** | 1 个人的脑子里装着所有隐式设计决策（"为什么 D5 有 45 个脚本但 D2 只有 2 个"、"为什么不直接用 ruff 替代 D7 全部脚本"）。这些决策理由没有文档化 | 在 `HUMAN_MEMORY_CARD.md` 中补充「设计决策日志」——每个反直觉决策一句话解释。在蓝图 §3.1 的各维度描述中补充「为什么这个维度脚本多/少」的脚注。对标 Google Design Doc 的 "Alternatives Considered" 章节 |
| **B69** | **脚本对特定 AI 行为的隐式依赖** | 有些脚本可能无意中依赖 Claude 特有的输出格式/推理风格——当 Owner 换模型时脚本行为异常 | 所有涉及 LLM 调用的脚本（D9/D12）必须在 `__manifest__` 中声明 `ai_model_dependency: none \| claude \| multi`。`validate_cross_model_consensus.py` 在模型切换时自动全量回归 |

### 27.4 性能与规模递增 (B70-B72)

| # | 盲点 | 为什么重要 | 缓解策略 |
|---|------|-----------|---------|
| **B70** | **Pre-commit 延迟膨胀** | 当前 5 个核心钩子 ~50s——但随着脚本增长，pre-commit 耗时可能膨胀到 5 分钟以上，严重破坏开发体验。Vibe Coding 的核心优势是「快速迭代」，慢门禁会杀死这个优势 | 引入「Pre-commit 时延 SLA」——钩子总耗时 ≤ 60s。超过时自动：1) 快速脚本先跑（D1/D2/D3 < 5s）→ 2) 慢脚本异步化（D5/D7/D11 后台跑）→ 3) AI 重型脚本降级（D9/D12 仅 weekly）。对标 Google monorepo 的分层 pre-commit 策略 |
| **B71** | **文件重复解析浪费** | 多条治理脚本各自独立 `open() + parse` 同一文件——一个 500 行的 YAML 可被解析与注册脚本数量同阶的次数。在 1 人项目里这还不痛，但资源浪费是真实的 | `run_all.py` 引入「扫描缓存层」——同一轮扫描中，文件内容 `lru_cache` 到内存。跨脚本共享文件读取结果。对标 Bazel 的 Action Cache 思想 |
| **B72** | **增量扫描不够智能** | `run_incremental.py` 已存在，但只是简单的 `--diff-ref` 代理。当 Owner 修改了一个 `_shared/thresholds.yaml`，它不知道该跑所有引用该阈值的脚本（因为 `depends_on_scripts` 字段尚未存在） | 引入 B65 的 `depends_on_scripts` → 增量扫描时构建「变更影响图」→ 精确计算最小需要重跑的脚本集合。对标 Facebook Infer 的 incremental analysis |

### 27.5 脚本质量与测试深度 (B73-B75)

| # | 盲点 | 为什么重要 | 缓解策略 |
|---|------|-----------|---------|
| **B73** | **Golden Test Case 覆盖缺口** | B17 False Negative 检测引擎已设计但 `test_fixtures/` 目录**尚未创建**。这意味着假阴性检测引擎的「Golden Test Case 库」处于声明-未实现状态 | 优先级提升：Golden Test Case 库的创建从 P2 → P1。首期至少为 D1/D3/D5/D6 四个高密度维度各创建 3 个 known-bad 用例。施工依据：本蓝图 §19 |
| **B74** | **跨维度集成测试缺失** | 单脚本有 smoke test（D-H-01），但没有测试验证「D1 报告的结构问题 → D5 能正确消费 → D8 能正确追踪」这条跨维度链路 | 新增 `tests/integration/test_cross_dimension_pipeline.py`——构造一个「已知多维度有缺陷的测试项目」，全量跑 `run_all.py`，验证输出链路完整。对标 Sonobuoy 的 end-to-end conformance 测试 |
| **B75** | **脚本变异测试** | 脚本`validate_frontmatter.py` 输出 0 findings → 是因为项目真的没问题，还是因为脚本逻辑坏了（假阴性）？当前没有机制区分 | `meta/validate_false_negatives.py` 的 Golden Test Case 机制（§19）覆盖了已知坏用例——但还需要「变异测试」：自动注入已知缺陷到健康文件 → 验证脚本能否检测到。对标 pitest (Java mutation testing) 思想 |

### 27.6 运维韧性深化 (B76-B78)

| # | 盲点 | 为什么重要 | 缓解策略 |
|---|------|-----------|---------|
| **B76** | **分级降级策略** | 当系统资源紧张（内存不足、磁盘满），所有脚本一起崩溃 → 全部门禁失效。没有「先保护最重要的」机制 | `run_all.py` 引入「降级模式」：Level-1（仅 P0 脚本）→ Level-2（P0+P1）→ Level-3（全部）。资源不足时逐级降级，而非全部崩溃。对标 Netflix Hystrix 的 bulkhead + fallback 模式 |
| **B77** | **扫描断点续传** | `run_all.py` 全量扫描需要 ~50s。如果在 D8 维度（第 8/12）时崩溃，前面 7 个维度的结果丢失 → 必须从头重跑 | `run_all.py` 每完成一个维度 → 写 checkpoint 到 `meta/scan_checkpoint.json`。崩溃后重启 → 从 checkpoint 继续，不重跑已完成维度。30 天内 checkpoint 有效。对标 Apache Spark 的 lineage-based fault recovery |
| **B78** | **Finding 模式异常检测** | 某天 D2 突然产出 200 条 Finding（平时 5 条）→ 不是脚本坏了，是整个项目的链接体系在一次重构中大规模断裂。当前系统会按严重度逐一报告，但不会说「这是一次系统性断裂，不是 200 个独立问题」 | `meta/trace_finding_lifecycle.py`（B56 已施工）扩展「异常聚类」能力——同一时间窗口内同一维度的 Finding 数量超过历史平均值 3σ → 标记为 `[ANOMALY_CLUSTER]`，报告根因假设而非 200 条独立 Finding |

### 27.7 AI 安全专属 (B79-B80)

| # | 盲点 | 为什么重要 | 缓解策略 |
|---|------|-----------|---------|
| **B79** | **AI 生成脚本的混淆后门** | B43 已覆盖 Unicode Backdoor（零宽字符等）——但 AI 还能生成逻辑层面绕过检测的恶意代码，例如用 `getattr(__builtins__, 'ex' + 'ec')` 替代 `exec()`。正则扫描器检测不到 | `validate_rules_file_backdoor.py`（B43）扩展「语义后门」检测——AST 级别的危险模式识别，不仅仅是字符串正则。对标 Semgrep 的 AST pattern matching |
| **B80** | **Finding 描述中的 Prompt Injection** | Finding text 可能含恶意构造的自然语言内容，当 `run_all.py --output` 的输出被 AI 消费时 → 可能触发 AI 执行非预期行为。在 100% AI 施工的语境中，这是一个闭环风险 | Finding Schema 新增 `sanitized_description` 字段——去除 markdown 代码块中的指令性语言、URL、可执行模式。AI 消费 findings 时使用 sanitized 版本 |

### 27.8 生态系统与外部适配 (B81-B82)

| # | 盲点 | 为什么重要 | 缓解策略 |
|---|------|-----------|---------|
| **B81** | **跨 IDE 环境一致性** | 项目在 Trae IDE 开发，但 Owner 可能在 Cursor / Windsurf / VS Code / 纯终端之间切换。不同 IDE 的 Python 解释器路径、环境变量、编码默认值都可能不同 | `validate_environment_health.py`（§21）扩展「IDE 检测」——识别当前运行 IDE 并报告环境差异。`env_check.py` 增加 `--env-report` 输出跨 IDE 兼容性矩阵。对标 Docker 的「在我机器上能跑」问题的预防 |
| **B82** | **AI 可消费的健康仪表盘** | 人类看 `status.py` 输出能理解，但 AI 需要结构化的 JSON 来程序化判断系统状态。当前 `status.py` 是面向人类的 CLI 输出 | `status.py` 新增 `--json` 和 `--ai-summary` 参数——输出结构化 JSON，包含「Top 5 风险」「3 个最需要的修复动作」「建议下一个 AI session 做什么」。对标 AWS Health Dashboard 的 JSON API |

### 27.9 演进与废弃管理 (B83-B84)

| # | 盲点 | 为什么重要 | 缓解策略 |
|---|------|-----------|---------|
| **B83** | **脚本-系统版本兼容矩阵** | `validate_frontmatter.py` v1.3.2 是为蓝图 V3 写的——蓝图升级到 V5 后，这个脚本的检查逻辑是否仍然有效？没有版本兼容矩阵 → 无法判断 | `script_manifest.yaml` 新增 `compatible_blueprint_version` 字段（min/max 蓝图版本）。`run_all.py` 启动时对比当前蓝图版本 vs 脚本声明的兼容范围 → 不兼容脚本标记 `[VERSION_MISMATCH]` |
| **B84** | **脚本废弃影响预分析** | 退役一个脚本前（B52 的 `manage_script_retirement.py`），需要知道：哪些流程依赖它的输出？哪些 dashboard 引用它的指标？当前退役流程是单向的——只管退役，不管影响 | `manage_script_retirement.py` 增加 `--impact-analysis` 模式——退役前自动扫描：1) manifest 中其他脚本的 `depends_on_scripts` 引用 2) `status.py` 的指标引用 3) 蓝图 §14 的路径索引引用 → 输出受影响清单后才允许退役 |

### 27.10 文档与知识追索 (B85-B86)

| # | 盲点 | 为什么重要 | 缓解策略 |
|---|------|-----------|---------|
| **B85** | **脚本-规则追索矩阵** | 一个 rule（如 PS-STD-012 §2.1 退出码约定）被哪些脚本强制执行？当前是隐式的——需要人/ai 读所有脚本才能建立关联 | `script_manifest.yaml` 新增 `enforces` 字段——每个脚本声明它强制执行哪些规则（如 `PS-STD-012 §2.1`）。`generate_script_manifest.py` 反向生成 `rule-to-scripts` 索引视图 `meta/rule_enforcement_matrix.yaml` |
| **B86** | **Finding 根因自动聚类** | 50 条 D3 维度 frontmatter 违规 → 根因可能是「项目从 V3 升级 V4 时批量迁移遗漏了 frontmatter 更新」。当前 C2 分类器（待施工）提到「根因聚类」但设计未细化 | C2 分类器设计增强：时间窗口聚类 + 文件路径聚类 + Finding 描述相似度聚类 → 输出「根因假设」而不只是 Finding 列表。对标 Sentry 的 issue grouping 算法 |

### 27.11 Vibe Coding 特有模式 (B87-B89)

> **什么是 Vibe Coding**：Owner 用自然语言描述意图 → AI 生成代码 → Owner 验证 → 提交。迭代极快（分钟级），代码质量依赖 AI 的"氛围理解"而非严格规约先行。

| # | 盲点 | 为什么重要 | 缓解策略 |
|---|------|-----------|---------|
| **B87** | **"我机器上能跑"漂移** | Vibe Coding 中 Owner 和 AI 在同一个 IDE session 协作，脚本在 Owner 的 Trae IDE 中通过 `--warn-only` 验证。但环境变量、Python 路径、已安装的包在自己的机器上是隐式的——换一台机器（或裸 `git clone` 后）脚本失败 | `env_check.py --freeze` 生成完整环境快照（Python 版本 + pip freeze + 环境变量白名单 + PATH）。`validate_environment_health.py` 增加 `--compare-snapshot` 模式——对比当前环境与 frozen snapshot 的差异。对标 pipenv/Poetry lockfile 的「精确可复现」思想 |
| **B88** | **相似脚本的 AI 独立演化漂移** | Vibe Coding 中 AI 在不同 session 分别修改 `detect_secrets.py` 和 `detect_keywords_in_logs.py`——两个脚本功能相似但 AI 独立维护，编码风格、错误处理模式逐渐分化。没有「同类脚本一致性」检查 | `meta/detect_script_divergence.py`——对同一维度的脚本做 AST 相似度聚类 + 模式一致性检查。发现同类脚本风格分化 → 报告并建议统一 |
| **B89** | **Session 特化污染** | AI 为了满足当前 session 的具体任务（如"紧急修复 D5 误报"），临时修改了脚本的参数默认值——修完 D5 后忘记改回来。脚本被「session 特化」了 | `manage_shadow_mode.py`（§17）可以检测新脚本的假阳性——但存量脚本的意外特化（参数被改、阈值被调低等）没有检测。新增 `meta/detect_config_deviation.py`——对比每个脚本当前参数 vs manifest 声明 vs 原始版本 |

### 27.12 度量与反馈闭环 (B90-B91)

| # | 盲点 | 为什么重要 | 缓解策略 |
|---|------|-----------|---------|
| **B90** | **脚本投资回报率 (ROI)** | 注册的治理脚本里，哪些真正发现过有价值的问题（CRITICAL/HIGH 被人工确认并修复）vs 哪些只产出噪声（LOW/INFO 或 FALSE_POSITIVE）？在 1 人项目中，人的注意力是最稀缺资源——噪声脚本消耗注意力但不创造价值 | `meta/score_script_effectiveness.py`——计算每个脚本的「效果分」：过去 90 天产出的 CRITICAL/HIGH Finding 中实际被修复的占比 × 修复后的系统改善程度。低分脚本（持续 < 0.1）→ 建议退役或降低优先级 |
| **B91** | **检测速度 vs 修复速度失衡** | 脚本系统每周检测 50 个新问题，但 1 人 Owner 只能修复 10 个 → 积压增长 → 审计疲劳。这个比例没有被追踪 | `manage_error_budget.py`（§21）扩展「修复吞吐量」指标——`detection_rate / fix_rate` 比值 > 2.0 持续 4 周 → 触发「减速建议」：降低部分维度扫描频率、或将 MEDIUM 以下自动降级为 INFO |

---

## 28. 1人+AI 维护专属优化方案

> 本节是 §27 盲点 B60-B91 的**可执行对策汇总**——将 32 个盲点的缓解策略按优先级和施工难度重组为 10 个行动项。每个行动项明确「做什么」「为什么现在做」「不做会怎样」。

### 28.1 立即行动（P0——当前 Phase 内施工）

| # | 行动项 | 解决盲点 | 施工量 |
|---|--------|---------|:---:|
| **A1** | **Golden Test Case 库落地** —— 为 D1/D3/D5/D6 各创建至少 3 个 known-bad fixture 文件 → 让 `validate_false_negatives.py` 实际可运行 | B73 | 中（4维度×3用例 = 12个fixture + 验证脚本改造） |
| **A2** | **`depends_on_scripts` manifest 字段** —— 在 script_manifest.yaml schema 中新增此字段 → `run_all.py` 可构建脚本影响图 → 支撑增量扫描 (B72) + 接口断裂检测 (B65) + 退役影响分析 (B84) | B65,B72,B84 | 中（schema 变更 + 生成器改造） |
| **A3** | **Pre-commit 时延 SLA + 分层执行** —— 核心钩子 ≤ 60s，慢脚本异步化 | B70 | 小（run_all.py 参数扩展） |

### 28.2 短期行动（P1——下 2 个 Phase 内施工）

| # | 行动项 | 解决盲点 | 施工量 |
|---|--------|---------|:---:|
| **A4** | **AI 上下文窗口污染治理** —— QUICKSTART.md 升级为 Tier-1 必读；manifest/蓝图分级注入策略 | B60,B62 | 小（文档改造 + AGENTS.md 指令增强） |
| **A5** | **维护者缺席模式** —— Kill Switch 扩展「缺席冻结」状态 + ERROR Budget 暂停消耗 | B66 | 中（Kill Switch 状态机扩展） |
| **A6** | **脚本效果分系统** —— 追踪每个脚本的实际价值 → 自动建议低效脚本退役 | B90 | 中（SQLite 新增表 + 统计视图） |
| **A7** | **Fix 振荡检测** —— 检测 AI 在同一文件上的修复-发现循环 | B64 | 小（新增 meta 脚本） |

### 28.3 中期行动（P2——系统化阶段）

| # | 行动项 | 解决盲点 | 施工量 |
|---|--------|---------|:---:|
| **A8** | **跨维度集成测试 + 变异测试** —— 构造多维度缺陷项目 → 全链路验证 | B74,B75 | 大（测试基础设施） |
| **A9** | **脚本-规则追索矩阵** —— 从隐式关联 → 显式可查询矩阵 | B85,B86 | 中（manifest 扩展 + 视图生成） |
| **A10** | **跨 IDE 环境快照 + 一致性检查** —— 解决「我机器上能跑」问题 | B81,B87 | 中（env_check 扩展） |

> **不做 A1-A10 的后果**：系统在纸面上完美（蓝图 1400 行覆盖一切），但实际操作中：（1）Golden Test Case 缺失 → 假阴性检测是空壳；（2）脚本间依赖不可见 → AI session 修复脚本 A 时不知道会弄坏 B；（3）pre-commit 越来越慢 → 开发体验恶化 → Owner 倾向于 `--no-verify` 绕过 → 门禁形同虚设。

---

## 29. Vibe Coding 社区对标补充

> **为什么需要这一章**：前三层对标的是「专业机构」（ITIL 4 / OWASP / K8s / NASA）——但 ZephyrAlpha 的独特语境是 **100% AI 施工 + Vibe Coding**。Vibe Coding 社区（Cursor / Windsurf / Cline / RooCode / Copilot Workspace）有自己的最佳实践模式，与传统软件工程截然不同。本节补充这些模式并评估是否应纳入。

### 29.1 Cursor Rules 对标

> Cursor 的 `.cursorrules` 文件是 AI 行为约束的「主 Prompt」——每当 AI 生成/修改代码时自动注入。

| Cursor 实践 | ZephyrAlpha 已有 | 差距 |
|------------|:---:|------|
| **分层 Rules 文件**：Global Rules → Project Rules → Directory Rules | AGENTS.md 是全局的；各蓝图是模块级 | ✅ 对齐——蓝图体系天然支持分层 |
| **Rules 文件内嵌代码示例** | quality-standard.md 已做——每个 MUST 条款有正例/反例 | ✅ 已达标 |
| **"Always" vs "Never" 规则** | ABS/COND 行为边界体系 | ✅ 已达标 |
| **Model-specific behavior tuning**（不同模型需要不同的提示工程） | 无 | ❌ 缺失——B67 已覆盖。建议在 `meta/model_compatibility_matrix.yaml` 中维护 |

### 29.2 Windsurf Rules 对标

> Windsurf 的 Cascade Memory 机制——AI 自动维护跨 session 的记忆链。

| Windsurf 实践 | ZephyrAlpha 已有 | 差距 |
|--------------|:---:|------|
| **自动上下文感知**：AI 自动了解项目结构 | AGENTS.md + QUICKSTART.md 提供冷启动路径 | ✅ 已达标 |
| **跨 session 记忆链** | 无直接等价物。Session Log 是「事后记录」而非「记忆链」 | ⚠️ 部分缺失——Session Log 是被动的记录。Windsurf 式的「主动记忆」在 1 人项目中可能过度工程。建议保持 Session Log 模式 + 在 QUICKSTART.md 中提示「先读最新 Session Log」 |
| **Rules Cascade**：子目录 rules 覆盖父目录 | AGENTS.md 是单层全局 + 各蓝图引用 | ✅ 已对齐（蓝图间 depends_on 链 = cascade） |

### 29.3 氛围编程特有模式——建议新增

| 模式 | 描述 | 建议 |
|------|------|:---:|
| **"规则即 Prompt"** | 在 Vibe Coding 中，AI 看到的是自然语言规则，不是形式化规范。规则的措辞直接影响 AI 的输出质量 | ✅ 已做到——整个蓝图体系是自然语言。但需要在 quality-standard.md §9 中补充「AI 提示工程自查」：关键规则是否用语无歧义？ |
| **"Few-Shot Learning via Rules"** | Cursor 社区最佳实践：在 rules 文件中嵌入 2-3 个「正确做法示例」→ AI 模仿 | ✅ quality-standard.md 已做 |
| **"Output Validation Loop"** | AI 生成代码 → 脚本自动检查 → 错误反馈给 AI → AI 修正 → 循环 | ⚠️ 已设计但未闭环——`run_all.py` 能检查，但检查结果如何反馈给 AI session？建议在 AGENTS.md 中增加「脚本失败后的标准修复流程」指令 |
| **"Context Budgeting"** | 大项目必须精算每次 AI session 注入多少上下文 | ✅ B60 已覆盖——Tier-1/2/3 注入策略 |

---

## 30. 顶尖设计应有的蓝图全景

> **本章回答**：「如果这个蓝图是业内最顶尖的——它应该还包含什么？」

以下 4 个维度是「从优秀到卓越」的关键跨越。当前蓝图已在「广度」（12 维度 × 5 阶段 × manifest 登记的全部治理脚本）达到卓越——但在**深度**和**智能**上仍有空间。

### 30.1 自适应阈值

> 当前：所有阈值在 `thresholds.yaml` 中静态定义 → Owner 手动调。
> 顶尖：阈值根据历史数据自动调整。

```
当前模式：假阳性率 > 5% → Error Budget 消耗 → 手动调阈值
顶尖模式：系统追踪每个脚本的假阳性/假阴性比率 → 
          自动建议阈值 → Owner 审核 → 一键应用
```

**施工路径**：扩展 `manage_error_budget.py` → 增加 `--suggest-thresholds` 模式 → 基于 90 天数据推荐最优阈值。

### 30.2 脚本智能优先级

> 当前：脚本优先级 (P0/P1/P2) 在 manifest 中静态声明。
> 顶尖：优先级根据实时风险动态调整。

```
例如：项目昨天做了大规模目录重构 → D4（路径有效性）临时提升为 P0
      项目本周新增 3 个 Agent 模块 → D12（AI 幻觉检测）临时提升为 P0
```

**施工路径**：`run_all.py` 增加「风险自适应」模式 → 扫描 git log recent changes → 评估各维度的临时风险 → 动态调整优先级。

### 30.3 跨脚本知识共享

> 当前：manifest 每条登记通常对应独立 `.py` 文件——通过 `_shared/` 共享工具函数和 `base.py` 共享基类。
> 顶尖：脚本之间共享「学到了什么」。

```
例如：detect_secrets.py 在某个文件中发现了一种新的密钥模式 →
      自动建议 detect_keywords_in_logs.py 也检查这种模式
```

**施工路径**：`meta/arbitrate_findings.py`（B49 已施工）扩展「跨脚本模式推荐」——当一个脚本的 Finding 模式被确认为有效（非 FALSE_POSITIVE）→ 推荐其他相关脚本也采用。

### 30.4 AI 协作成熟度

> 当前：AI 是「脚本执行者」——遵守蓝图、质量标准、manifest。
> 顶尖：AI 是「脚本改进者」——主动发现脚本系统的不足并提出改进。

```
当前模式：AI session 接到任务 → 读蓝图 → 执行 → 报告
顶尖模式：AI session 执行中自动收集「改进机会」→
          发现某脚本的检查逻辑可被更高效的 AST 方法替代 →
          在 Session Log 中记录改进建议 →
          下一个 Phase 自动施工
```

**施工路径**：在 AGENTS.md 中增加「改进捕获」指令——AI session 结束时输出 `IMPROVEMENT_OPPORTUNITIES` 区块。定期汇总 → 纳入 Phase 规划。

---

### 30.5 蓝图完整性自评矩阵

> 用 5 级成熟度模型评估当前 MOD-INF-005 在关键能力轴上的位置：

| 能力轴 | 当前级别 | 说明 | 到达 L5 缺什么 |
|--------|:---:|------|--------------|
| **覆盖广度** | **L5** | 12/12 维度 × manifest 治理脚本 × 跨 3 线横切 | — |
| **自动化深度** | **L4** | Kill Switch / Shadow Mode / Baseline / Error Budget / 退役流程 已施工 | 自适应阈值 (L5) |
| **自我监控** | **L4** | Meta 维度 24 脚本 + 健康自检 + 假阴性检测 | 变异测试 + 跨维度集成测试 (L5) |
| **AI 协作** | **L3** | 蓝图可被 AI 消费 + QUICKSTART + HUMAN_MEMORY_CARD | AI 主动改进建议 + 上下文窗口治理 (L5) |
| **1人维护** | **L3** | Killer Switch + 应急通道 + HUMAN_MEMORY_CARD | 维护者缺席模式 + 脚本 ROI 追踪 (L5) |
| **Vibe Coding 适配** | **L3** | 前缀约定 + docstring 自文档 + rules 即 prompt | 环境快照 + session 中断续接 + 振荡检测 (L5) |

> **整体评级：L3.6 → 目标：L4.5**（通过施工第四层盲点 B60-B91 + 10 行动项 A1-A10）

---

## 31. 第五层盲点：外部取证专家的致命发现 (B92-B107)

> **触发问题**：「如果你是审计这个审计系统的外部取证专家，你会发现什么致命漏洞？」
>
> **方法论**：将整个脚本系统视为一个「黑箱被测对象」——假设一名独立取证专家（无项目背景知识、不信任任何自述文档、只信可独立验证的物证）被请来审计 MOD-INF-005 的完整性。他从以下 4 个维度发起穿透：
> 1. **信任根**（Trust Root）——系统是否可证明自己未被篡改？
> 2. **依赖链**（Dependency Chain）——串行依赖体系是否存在单点灾难性失效？
> 3. **时态完整性**（Temporal Integrity）——扫描结果在时间轴上是否真实？
> 4. **证据可验证性**（Evidence Verifiability）——每一条 Finding 能否被第三方独立证实？

### 31.1 信任根维度 (B92, B102, B105, B107)

| # | 致命漏洞 | 取证专家的发现 | 为什么前三层未覆盖 |
|---|---------|--------------|-----------------|
| **B92** | **启动信任悖论** | SHA256 哈希校验（B44）的**预期哈希值存储在同一个 repo 中**。攻击者修改 `run_all.py` 的同时可以同步修改 `validate_rules_integrity.py:EXPECTED_RULES_HASHES`。系统没有**带外验证通道**（硬件 Token、外部校验服务器、Git 签名验证、GitHub attestation）。取证专家会问：「谁证明这个哈希值本身没被改过？」 | B44 覆盖了「规则文件完整性」，但只考虑了文件内容哈希，未考虑哈希存放位置的信任问题 |
| **B102** | **检查器传递完整性断裂** | `check_registry_consistency.py` 验证 manifest 一致性。`validate_rules_integrity.py` 验证规则文件完整性。但**谁来验证这两个验证器自身**？Meta 维度的 24 个自检脚本和被测系统共享同一攻击面——修改它们的人也是能修改它们所检查对象的人。 | 无盲点覆盖——这就是经典的 "Quis custodiet ipsos custodes?"（谁来审计审计者？） |
| **B105** | **双形态 Manifest 解析器分化** | Manifest 生成器同时支持三引号 YAML 和 `ast.literal_eval` 解析 dict 字面量——但两套解析器是**不同代码路径**。YAML 的锚点/别名/标签与 Python dict 的语义不完全等价。攻击者可构造一个 dict 形式的 manifest，`ast` 解析得到一个值，人类阅读得到另一个值。 | B43/B44 覆盖了 Rules File 完整性但针对的是 `.cursorrules`/`AGENTS.md`，不是 manifest 解析器分化风险 |
| **B107** | **运行态数据单机脆性** | 取证专家追问：「全量扫描结果在哪？」答案：SQLite (`findings_timeseries.db`) + JSON (`finding_state_db.json`) + YAML 状态文件（`kill_switch_state.yaml` 等）。**但这些文件是否纳入 Git？是否异地备份？** 如果 Owner 的笔记本电脑 SSD 故障/勒索软件/咖啡泼溅 → 全部运行态数据永久丢失。Git 备份了代码，但没备份审计证据。 | R5 提到「单人项目瓶颈」但聚焦于审计独立性，未考虑物理单点故障 |

### 31.2 依赖链维度 (B93, B95, B106)

| # | 致命漏洞 | 取证专家的发现 | 为什么前三层未覆盖 |
|---|---------|--------------|-----------------|
| **B93** | **D1 单点灾难性失效** | §5.3 明确声明 D1 是 D3→D5→D8 的**最前置依赖**。D1 共有 17 个脚本。如果其中任何一个关键脚本产生假阴性（报告「结构完好」但实际已损坏），D3/D5/D8 的输入就是垃圾——下游维度的所有 Finding 都不可信。系统**没有「D1 产出物合理性校验」**——在把 D1 结果交给 D3 之前不做逻辑自洽性检查。 | B6 讨论「覆盖率」但未针对串行依赖链的单点失效做专项防御 |
| **B95** | **Manifest 语义欺诈** | manifest 的结构验证（格式正确、字段完整）通过，但**值的真实性从未校验**。一个放在 `d7_code/` 目录下的脚本可以在 manifest 中声明 `dimensions: [D3]`，系统会按 D3 调度它，但它实际扫描的是 D7 的文件。AST 解析器验证语法，不验证语义。 | B46 (Trust-Tier) 基于 manifest 声明的维度分配信任等级——如果 manifest 声明本身就是假的，Trust-Tier 在错误前提上运行 |
| **B106** | **覆盖率与风险的比例失衡** | D5（架构）有 45 个脚本，D2（链接）只有 2 个。各维度脚本数量分配是「AI 施工的历史产物」，不是「基于风险的工程决策」。外部审计员会追问：「D2 的链接完整性难道只值 2 个脚本检查？还是 AI 施工时遗漏了？」系统**没有「维度风险权重 vs 脚本资源分配」的校验机制**。 | B6 覆盖了「检查了什么 vs 没检查什么」的覆盖率，但未覆盖「检查深度是否与风险匹配」 |

### 31.3 时态完整性维度 (B96, B97, B98)

| # | 致命漏洞 | 取证专家的发现 | 为什么前三层未覆盖 |
|---|---------|--------------|-----------------|
| **B96** | **时间涂抹窗口** | `run_all.py` 全量扫描耗时 ~50 秒，12 个维度串行/并行执行。在这 50 秒内**代码库未被冻结**——IDE 自动保存、`git checkout`、其他进程都可能在扫描中途修改文件。扫描结果不是瞬间快照，而是 50 秒的「涂抹平均」。攻击策略：(1) 等待 D1 维度完成 → (2) 替换恶意文件 → (3) 等待 D3 扫描恶意文件 → (4) 换回正常文件。D1 通过了，D3 也通过了——但 D3 扫描的对象和 D1 扫描的对象不是同一个版本。 | 完全新颖——无任何盲点覆盖时间窗口竞争 |
| **B97** | **Error Budget 可预测重置窗口** | Error Budget 每 30 天重置。外部攻击者（或恶意 AI session）可精确计算重置时间：在 Day 29 集中部署恶意变更——此时 Budget 接近满额（即将重置），大批 Finding 不会耗尽 Budget。Day 1 Budget 重置后，「债务清零」，恶意代码已经入库。 | B14 (Error Budget) 定义了机制但未考虑「可预测重置周期」作为攻击向量 |
| **B98** | **Shadow Mode 定时炸弹** | 恶意脚本在 Phase 1-2（各7天 Shadow/Warn）产出良性结果 → 进入 Phase 3（Active）获得阻断权 → 第 15 天**定时激活恶意逻辑**（`if datetime.now() > TRIGGER_DATE`）。14 天预热期是攻击者的掩护窗口。 | B19 (Shadow Mode) 设计了渐进激活但未防御定时激活（sleeper attack） |

### 31.4 证据可验证性维度 (B94, B99, B100, B101, B103, B104)

| # | 致命漏洞 | 取证专家的发现 | 为什么前三层未覆盖 |
|---|---------|--------------|-----------------|
| **B94** | **僵尸脚本** | `detect_script_rot.py` (B51) 检测「曾经产出 Finding，后来不再产出」的脚本退化。但**从未产出过 Finding 的脚本**不会被检测——因为 B51 依赖「有→无」模式，不检测「始终无」模式。一个逻辑完全损坏的脚本（死代码分支、错误正则、错误目录范围），只要从未产生过 Finding，B51 就报告「健康」。取证专家会要求**主动注入缺陷 → 验证检测能力**（变异测试），而非被动等待历史数据异常。 | B51 解决「脚本腐化」（曾有效→无效），不解决「僵尸脚本」（始终无效） |
| **B99** | **AI 决策溯源链缺失** | B47 覆盖了**脚本**的溯源链（谁创建、哪次 session、什么 prompt）。B56 覆盖了**Finding** 的溯源链（C1→C5 管道追踪）。但两者之间有一条致命的空白：**AI session 做出的决策**（「这是误报」「降低严重度」「延迟修复」）没有溯源。哪个 AI 模型、在什么上下文下、基于什么推理做出了该决策？这些决策在下游系统中被当作事实使用，却无法回溯其来源。 | B47 和 B56 覆盖了「物证」溯源，不覆盖「决策」溯源 |
| **B100** | **人因绕过疲劳** | 紧急绕过（§13.2）依赖唯一 Owner 手动授权。但 6 个月维护后，Owner 疲劳积累——开始对所有 Finding 点「通过」。绕过计数器存在但**与 Owner 是同一个人**：系统向 Owner 报告「你绕过了 47 次」，Owner 点「知道了」继续绕过。取证专家指出：**当审计者和被审计者是同一个人时，审计系统不产生任何有意义的约束**。 | B66 覆盖「维护者物理缺席」，不覆盖「维护者心理疲劳/决策退化」 |
| **B101** | **自述证据不可独立验证** | Finding Schema 的 `evidence` 字段是**脚本自述**的（「第 42 行发现硬编码密钥」）。没有哈希存证（content hash at time of detection）、没有文件快照（当时的文件内容副本）、没有第三方见证。外部审计员无法在事后独立验证「这条 Finding 在产生时是否真实存在」——只能选择信任脚本。这是在法庭上会被立刻驳回的证据形态。 | 无盲点覆盖——这是整个证据体系的根本缺陷 |
| **B103** | **二进制工件完全不可见** | 现行治理扫描脚本主要面向文本文件（`.py`, `.md`, `.yaml`, `.json`, `.toml`）。二进制文件（`.pyc`, `.pyd`, `.dll`, `.so`, `.exe`, `.whl`, `.zip`）**完全不被扫描**。被 Git 追踪的二进制文件——编译扩展、预构建 wheel、vendor 二进制——可能含后门而永不被发现。 | 无盲点覆盖——整个脚本系统的视野局限在文本世界 |
| **B104** | **分类器静默降级** | 攻击者不删除 Finding（太明显）——而是系统性地将严重度分类逻辑**植入脚本内部的 if/elif 链**中逐步放松：CRITICAL 阈值拉高、HIGH 阈值拉高。总 Finding 数量不变（无异常），但执行阻断的 Finding 降为零。`validate_threshold_changes.py` 只能检测 `thresholds.yaml` 的变更，无法检测散布在众多治理脚本内部逻辑中的分类标准漂移。 | B9 覆盖「配置文件漂移」（thresholds.yaml），不覆盖「代码内分类逻辑漂移」 |

---

## 32. 是否确实穷尽——跨五层完整性声明

> **本声明不是「绝对穷尽」——没有任何审计系统能声称绝对穷尽。这是「给定当前架构和语境下，系统性遍历已知盲点分类空间后的穷尽」**

### 32.1 五层盲点覆盖总览

| 层级 | 编号区间 | 数量 | 覆盖领域 | 来源 |
|------|---------|:---:|------|------|
| **第一层** | B1-B13 | 13 | 基础设施层：审计疲劳、报告过期、覆盖率、版本化、配置漂移等 | 蓝图 V3 基准审查 |
| **第二层** | B14-B25 | 12 | 机制层：Error Budget、Baseline、Shadow Mode、Finding 生命周期、Kill Switch 等 | 蓝图 V4 机制设计审查 |
| **第三层** | B43-B59 | 17 | 纵深安全层：供应链安全、Provenance、Slopsquatting、多模型共识、Burn Rate 等 | 蓝图 V5 安全纵深审查 |
| **第四层** | B60-B91 | 32 | AI+1人维护层：会话管理、反馈回路安全、规模递增、Vibe Coding 适配等 | 审查一（2026-05-05） |
| **第五层** | B92-B107 | 16 | 取证穿透层：信任根悖论、时间涂抹、证据可验证性、分类器静默降级等 | 审查二（本次，外部取证视角） |
| **合计** | B1-B107 | **90** | 从基础设施到证据法理学的全纵深覆盖 | — |

### 32.2 穷尽判定：为什么本次审查后确实没有第六层了

> **取证专家在完成 B92-B107 穿透后，对剩下未探索空间的评估：**

| 潜在探索方向 | 评估 | 结论 |
|-------------|------|------|
| **硬件/Firmware 层**（BIOS/UEFI/TPM 供应链攻击） | 超出应用层审计系统的边界——属于操作系统/硬件安全域，不属于 MOD-INF-005 的责任范围 | 不纳入 |
| **网络层**（TLS 中间人、DNS 劫持影响 pip install 供应链） | B48 (Slopsquatting) + B43 (Backdoor) 已间接覆盖 | 已覆盖 |
| **人员社会工程层**（钓鱼攻击获取 Owner 凭据 → 直接提交恶意代码） | GitHub 的 2FA/branch protection 是独立安全层，MOD-INF-005 防御的是「代码入库后」的治理 | 不在范围内 |
| **AI 对齐理论层**（AI 模型的根本性不可靠——即使所有检查通过也可能生成有害代码） | B67 + B69 + B53 覆盖了模型一致性和迁移风险——但要穷尽 AI 对齐问题需要 AGI 级别的审计，不现实 | 已覆盖能覆盖的部分 |
| **法律/合规层**（GDPR 第 22 条自动化决策权、EU AI Act 高风险系统分类） | B57 做了合规映射（OWASP/ISO27001/SOC2/ITIL5），详细法律分析属于法务域 | 已覆盖映射 |

> **结论**：从应用层审计系统的视角看，B1-B107 覆盖了「基础设施→机制→安全→AI协作→证据法理」五层纵深。第六层只能出现在以下情形之一：（1）发现了全新的攻击面类别；（2）ZephyrAlpha 架构发生根本性变化；（3）AI 模型能力出现代际跃迁。**当前蓝图已遍历盲点分类空间。**

### 32.3 致命度排序

> 如果上述 16 个致命漏洞只能修 3 个——取证专家的选择：

| 排名 | 盲点 | 理由 |
|:---:|------|------|
| **1** | **B92 — 启动信任悖论** | 如果系统的信任根腐败，所有下游检查都是表演。需要至少一个带外验证锚点（Git signed commit 校验或外部哈希存证） |
| **2** | **B101 — 自述证据不可验证** | 整个审计系统的输出——Finding——如果不能在事后被独立证实，则审计本身不具备法律/工程意义上的证明力 |
| **3** | **B93 — D1 单点灾难性失效** | 一条串行链的前端腐败 = 整条链的输出作废。必须在 D1→D3 交接处插入合理性校验 |

---

## 33. 物理韧性与灾备补全

> B107 揭示的「单机脆性」需要在蓝图层级给出灾备策略——不能留给「运维阶段再说」。

### 33.1 关键运行态数据的灾备分级

| 数据 | 存储位置 | 灾备策略 | Git 追踪 |
|------|---------|---------|:---:|
| `kill_switch_state.yaml` | `meta/` | 每次变更后 commit → 随代码同步备份 | ✅ |
| `shadow_mode_state.yaml` | `meta/` | 每次变更后 commit | ✅ |
| `error_budget_state.yaml` | `meta/` | 每次变更后 commit | ✅ |
| `script_retirement_state.yaml` | `meta/` | 每次变更后 commit | ✅ |
| `trust_tier_policy.yaml` | `meta/` | 作为配置管理 → commit | ✅ |
| `findings_timeseries.db` (SQLite) | `meta/` | **每周导出 JSON → commit 到 `meta/backups/`** | ❌ (二进制) → ✅ (JSON) |
| `finding_state_db.json` | `meta/` | 每次 `run_all.py` 后 commit | ✅ |
| `scan_checkpoint.json` (B77 将来) | `meta/` | 不 commit（临时性） | ❌ |
| `baseline/` snapshots (B18) | `meta/baseline/` | 每次更新 commit | ✅ |

### 33.2 新增自动灾备脚本

```bash
# 周度灾备导出（建议 cron / scheduled task）
python scripts/governance/meta/backup_runtime_state.py --export-to meta/backups/
```

`backup_runtime_state.py` 应做的事：
1. `findings_timeseries.db` → `findings_timeseries_20260505.json`（JSON 导出）
2. 汇总所有 YAML 状态文件的当前快照 → `runtime_snapshot_20260505.json`
3. commit 备份文件到 Git（确保异地备份由 Git remote 保证）
4. 保留最近 12 周的周度备份 → 自动清理旧备份

---

## 34. 操作陷阱备忘录

> **性质**：以下项目不是新的盲点——而是五层90盲点之外，在「实际操作中一定会踩到」的工程陷阱。它们不新增盲点编号，但对 1人+AI 维护来说，提前知道 = 避免浪费一个 AI session。

### 34.1 绝对路径硬编码陷阱

**现象**：大量脚本使用硬编码路径 `D:\ZephyrAlpha\...`，而非常量 `REPO_ROOT`。

**后果**：项目 clone 到其他盘符（如 `E:\Projects\ZephyrAlpha`）→ 所有路径失效 → 大量治理脚本集体崩溃（exit 3）。

**预防**：
```python
# 每个脚本入口应计算而非硬编码
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parents[3]  # scripts/governance/dX_*/ → 根
SCRIPTS_DIR = REPO_ROOT / "scripts" / "governance"
```

**自检**：`grep -r "D:\\\\ZephyrAlpha" scripts/governance/` 应返回 0 结果（排除本蓝图）。

### 34.2 依赖版本锁定缺口

**现象**：`meta/requirements/requirements-d*.txt` 依赖声明 **未精确锁定版本号**（如 `pyyaml>=6.0` 而非 `pyyaml==6.0.2`）。

**后果**：`pip install --upgrade` → 依赖静默升级 → API 行为变化 → 脚本输出结果不同 → 假阴性/假阳性默默增加，无告警。

**预防**：
```bash
# 每季度冻结一次精确版本快照
pip freeze > scripts/governance/meta/requirements/frozen-versions.txt
# D12 维度可扩展为：对比当前 freeze vs frozen → 报告差异
```

### 34.3 同进程 import 污染风险

**现象**：`run_all.py` 若以 `importlib` 动态加载脚本模块，不同脚本可能在同一个 Python 进程中运行。

**后果**：脚本 A 修改了全局状态（如 `sys.setrecursionlimit()`、`logging.basicConfig()`、`os.environ`）→ 脚本 B 继承被污染的状态 → 行为异常且难以复现。

**预防**：
- 优先使用 `subprocess.run([sys.executable, script_path])` 隔离执行（当前 `run_all.py` 已在用）
- 若必须 import（性能优化），确保每个脚本 `__main__` 入口是纯函数，不修改全局状态
- `_shared/base.py` 中的基类方法保持无副作用

### 34.4 SLA 指标"待测量"状态的实操风险

**现象**：§8.4 定义 6 项 SLA/SLO 指标，全部标记「待测量」。

**后果**：Error Budget、Burn Rate、Kill Switch 依赖这些指标做决策——但指标未实际采集 → 决策在盲飞。例如：假阳性率实际可能是 12%，但阈值仍按 5% 运行，系统在虚假的安全感中运作。

**最小落地**（不需要完整指标管线）：
```bash
# run_all.py 每次扫描后自动追加一行到 meta/sla_metrics.jsonl
{
  "timestamp": "2026-05-05T15:30:00+08:00",
  "scan_type": "full",
  "total_findings": 47,
  "critical_count": 0,
  "high_count": 3,
  "scan_duration_s": 48.2,
  "exit_code": 1
}
```
一个 JSONL 文件 + 每周一个简单的统计脚本即可替代复杂仪表盘。

### 34.5 部分扫描的虚假安全感

**现象**：`run_all.py --dimensions d1,d3` 只跑 D1+D3，输出 exit 0。

**后果**：用户看到 `✅ ALL GREEN`，但 D5（架构）可能已经大面积损坏——只是没跑所以不知道。D1→D3→D5→D8 是串行链，只跑前两个 = 给断桥拍照只拍桥头。

**预防**：
- `run_all.py` 在部分扫描时**输出显式警告**：
  ```
  ⚠ PARTIAL SCAN: Only D1,D3 executed.
  ⚠ UNCHECKED: D5 (architecture), D8 (doc-sync), and 8 other dimensions.
  ⚠ Full baseline comparison unavailable.
  ```
- 建议在 §3.6 标签体系中增加 `[ChainGuard]` 标签——部分扫描时必须确认依赖链完整性

### 34.6 脚本-蓝图版本漂移的隐蔽性

**现象**：蓝图更新（如 V5.1.0 → V5.2.0），新增了检查条款——但多条脚本的 `__manifest__` 可能仍然声明兼容旧版本。

**后果**：`run_all.py` 启动时不做蓝图版本 vs 脚本兼容范围校验 → 脚本在新蓝图层级下用旧的假设运行 → 漏检或误判。

**关联**：B83 已定义 `compatible_blueprint_version` 字段——但 **manifest 尚未实际包含该字段**。当前由 `generate_script_manifest.py` 生成时不会自动注入蓝图版本号。

**预防**：在 manifest schema 中正式加入 `compatible_blueprint_version`，生成器自动从蓝图 frontmatter 读取当前版本号填入。

### 34.7 AI Session 之间的任务修复交接损耗

**现象**：Session A 触发 CRITICAL Finding → 创建 OPS-XXX 任务卡。Session B 被分配修复任务。

**后果**：Session B 不知道 Session A 的上下文（文件当时是什么状态、AI 推理路径、为什么判断为 CRITICAL）→ 修复方向可能偏差 → 引入新问题 → B64（振荡）。

**预防**：
- OPS 任务卡的 `description` 应包含：`finding_id` + `evidence` 字段 + `detected_at` 时间戳
- 修复 AI session 启动时，先从 `meta/finding_state_db.json` 拉取 Finding 全文，而非只看任务卡摘要
- SH 中可记录「修复上下文交接」段——原检测 AI 模型 + 检测时的 git commit SHA

---

## 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-05-05 | 5.2.1 | **操作陷阱备忘录**。新增 §34「操作陷阱备忘录」——7 项实操工程陷阱（不新增盲点编号）：(1) 绝对路径硬编码陷阱 (2) 依赖版本锁定缺口 (3) 同进程 import 污染 (4) SLA 指标待测量风险 (5) 部分扫描虚假安全感 (6) 脚本-蓝图版本漂移隐蔽性 (7) AI Session 间任务修复交接损耗。每一项包含后果说明 + 具体预防方案。 |
| 2026-05-05 | 5.2.0 | **第五层盲点：外部取证专家终极穿透审查**。(1) 新增 §31 第五层盲点 B92-B107（16 项致命漏洞——信任根悖论 / D1单点灾难性失效 / 僵尸脚本 / Manifest语义欺诈 / 时间涂抹窗口 / Error Budget 可预测重置 / Shadow Mode 定时炸弹 / AI决策溯源链缺失 / 人因绕过疲劳 / 自述证据不可独立验证 / 检查器传递完整性断裂 / 二进制工件盲区 / 分类器静默降级 / 双形态Manifest解析器分化 / 覆盖率与风险比例失衡 / 运行态数据单机脆性）。(2) 新增 §32 跨五层穷尽声明——B1-B107 共 90 盲点覆盖从基础设施到证据法理学的全纵深，并给出致命度 Top 3 与穷尽判定依据。(3) 新增 §33 物理韧性与灾备补全——运行态数据灾备分级 + 自动灾备策略。(4) 确认 `test_fixtures/` 应创建于 `meta/benchmark/test_fixtures/` 和 `meta/false_negative_cases/` 两处。 |
| 2026-05-05 | 5.1.0 | **第四层盲点审查 + 1人+AI维护 + Vibe Coding 对标**。(1) 新增 §27 第四层盲点清单 B60-B91（32 个盲点——AI 会话管理 / 反馈回路安全 / 1人维护专属 / 性能规模 / 测试深度 / 运维韧性 / AI 安全 / 生态适配 / 演进废弃 / 文档追溯 / Vibe Coding 特有 / 度量反馈）。(2) 新增 §28 1人+AI 维护专属优化方案（10 行动项 A1-A10，P0/P1/P2 三级优先级）。(3) 新增 §29 Vibe Coding 社区对标补充（Cursor Rules / Windsurf Cascade / 氛围编程特有模式 4 项）。(4) 新增 §30 顶尖设计蓝图全景（自适应阈值 / 脚本智能优先级 / 跨脚本知识共享 / AI 协作成熟度 / 完整性自评矩阵 L3.6→L4.5）。对标 Cursor Rules 分层 / Windsurf Cascade Memory / 氛围编程「规则即 Prompt」/ 自适应 SRE 阈值。 |
| 2026-05-05 | 5.0.2 | **清单生成器病根修复**：`generate_script_manifest.py` 除三引号 YAML 外，解析模块顶层 `__manifest__` **dict**（`ast`），并修正模块文档字符串内嵌 `"""` 导致的语法风险说明。§4.3 脚注明确「勿手改 manifest、双形态 __manifest__」。 |
| 2026-05-05 | 5.0.1 | §3.1/§8 与 `script_manifest.yaml` 对齐：条数以生成器为准、`missing_manifest:0`；`validate_blueprint_tag_uniqueness.py` 使用生成器可解析的三引号 `__manifest__`；`session_simulator.py` 新增 `__manifest__`（D5+D12，`warn_only`）。 |
| 2026-05-05 | 5.0.0 | **蓝图V5升级——第三层盲点17项全施工**。(1) Rules File供应链安全: Unicode Backdoor扫描+文件SHA256完整性(B43+B44,对标Snyk 2025)。(2) Script A/B Kayenta对照(B45)+Trust-Tier T1/T2/T3(B46)+Provenance溯源链(B47)+Slopsquatting幻觉包防御(B48)+Finding仲裁器B49+SQLite时序数据库(B50)+Script Rot静默失效检测(B51)。(3) 退役流程B52+多模型共识Claude/GLM/Opus(B53)+AI费用追踪(B54)+BumRate加速度(B55)+C1→C5全链路Tracing(B56)+合规映射OWASP/ISO27001/SOC2/ITIL5(B57)+人类记忆卡(B58)+E2E基准测试(B59)。脚本28个(py)/配置13个/DB 2个(SQLite)/Fixture 4个。 |
| 2026-05-05 | 4.0.0 | **蓝图 V4 升级——9 大盲点全面施工**。(1) 新增 §15 关键阈值外置配置+变更审计（B16——thresholds.yaml SSoT + validate_threshold_changes.py）。(2) 新增 §16 Kill Switch 机制——全局冻结+单脚本禁用+run_all.py 集成（B25）。(3) 新增 §17 Shadow Mode 渐进激活——Phase1-3 三阶段释放+自动回退（B19）。(4) 新增 §18 Baseline Snapshot 对比——NEW/RESOLVED/PERSISTENT 分类+持久升级（B18）。(5) 新增 §19 False Negative 检测引擎——Golden Test Case 库+Fitness Functions（B17）。(6) 新增 §20 Finding 全生命周期状态机——10状态+SLA定时器+超时升级+跨run持久化（B20）。(7) 新增 §21 Error Budget+Burn Rate+依赖隔离——双预算模型+Critical/Warning Alert+Feature Freeze联动+三维度分池（B14+B21）。(8) 新增 §22 AI Session Zero-Memory Quickstart Card ≤500 tokens（B15）。(9) §14 路径索引补全 meta/ 目录下 30 个新文件。Python 脚本数量从 11 增至 19，配置文件从 3 增至 9。新增元文件 10 件（requirements ×5 + state ×3 + audit-log ×1 + baseline ×1）。|
| 2026-05-05 | 3.1.0 | 补全标准模板：独立产出物存放目录 + 集成目标 + 需要更新的相关内容 + 拆分 §12 风险与后果为独立风险和独立后果 |
| 2026-05-03 | 3.0.0 | **蓝图 V3 升级——全面对标专业机构**。(1) 新增 §1.7 自动化不可逾越的边界（6 条红线，对标 ITIL 4 自动化治理）。(2) 新增 §3.5 按自动化层级分类（L1/L2/L3，对标 ITIL 分层自动化策略）。(3) 新增 §3.6 按标签分类（6 个标签 + `--tags` 参数，对标 K8s Conformance 标签聚焦）。(4) §4.4 升级为 13 项入库验证矩阵（对标 K8s/CNCF 15 项自动验证）。(5) 新增 §4.5 插件接口契约 Plugin Contract（对标 Sonobuoy Plugin Skeleton）。(6) §5.2 新增 `--tags` 和 `--depth` 参数（quick/full/deep，对标 OWASP ASVS L1/L2/L3）。(7) 新增 §6.5 Finding Schema recommendation 字段（对标 ITIL Level 2 决策辅助）。(8) 新增 §8.4 SLA/SLO 度量指标（6 项，对标 ITIL 服务级别管理）。(9) §10 新增 C5→C1 反馈闭环 + 里程碑门禁（对标 ITIL SVS + NASA SRR→PDR→CDR→TRR→SAR）。(10) §12.4 新增盲点 B13（里程碑门禁缺失）。(11) **新增 §13 脚本系统运维与自我监控**——系统健康自检 + 应急回退 + 版本兼容 + 定期演练（对标 ITIL 应急管理）。(12) 个体脚本版本化注记（§3.6 待办，对标 OWASP ASVS 需求标识符）。Frontmatter 对标列表扩展至 ITIL 4 / OWASP ASVS v5 / K8s Conformance / NASA-STD-8739.8B / Terraform pre-commit / Cursor Rules / Windsurf Rules / Anthropic CLAUDE.md |
| 2026-05-02 | 2.0.0 | **蓝图 V2 升级**。(1) 全局重构——12章→10章，新增 §6 与任务系统集成接口、§3 脚本分类体系。(2) 过时数据修正——17个脚本→73个、覆盖率 92%→100%、D10"缺失"→"已有"。(3) 依赖声明新增 MOD-INF-006 G0-G7+G3.2.1+M1-M11 三个靶点。(4) 版本号 1.0.0→2.0.0 |
| 2026-05-02 | 1.0.0 | 初始创建——从候选池设计文档 v0.2.0 升格为正式蓝图 MOD-INF-005 |

---

## 施工落盘确认（2026-05-07 审计）

| 维度 | 状态 |
|------|------|
| construction_progress | phase_2_complete（Phase 1 Skeleton + Phase 2 E2E 均已通过） |
| 源码路径 | `scripts/governance/` + `src/zephyr/script_system/` |
| 源码文件数 | 120 个 .py/.yaml |
| 测试路径 | `tests/governance/` |
| 配置文件 | `config/runtime/script_retirement_state.yaml` |
| 关键入口 | `scripts/governance/` 下 D1-D12 子目录全覆盖 |
