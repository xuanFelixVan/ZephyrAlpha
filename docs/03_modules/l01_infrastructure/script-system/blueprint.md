---
module_id: MOD-INF-005
title: 脚本系统蓝图 — 第三条生产线的自动化审计与门禁
doc_type: blueprint
status: approved
version: 3.0.1
layer: L01
layer_name: infrastructure
functional_domain: infra
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
valid_from: 2026-05-03
ttl: permanent
construction_progress: phase_1_partial
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
summary: 脚本系统是 ZephyrAlpha 第三条独立生产线——横切全局地对方案工厂和任务管线的产出物进行 12 维度系统化审计。包含五阶段流水线（C1扫描→C2分类→C3报告→C4跟踪→C5沉淀）、标准化 Finding Schema、四档退出码约定（0/1/2/3）、pre-commit 门禁集成、73 个治理脚本的统一编排、插件接口契约、自动化治理边界、系统自我监控与应急回退机制、SLA/SLO 度量体系。对标 ITIL 4 / OWASP ASVS v5 / K8s Conformance (Sonobuoy) / NASA-STD-8739.8B / Terraform pre-commit / Cursor Rules / Windsurf Rules / Anthropic CLAUDE.md 最佳实践。
---

# 脚本系统蓝图 — 第三条生产线的自动化审计与门禁

> **module_id**: MOD-INF-005 | **version**: 3.0.0 | **status**: approved | **layer**: L01 infrastructure

> **真源声明**：本蓝图升格自 `D:\ZephyrAlpha\模块候选池\开发流程\氛围编程基础设施\vibe-coding-script-system-design.md`（原名"氛围编程基础设施——脚本系统设计"，version 0.2.0，147KB）。本蓝图为该设计的 canonical 正式版本，任何冲突以本蓝图为准。

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
| 1 | **治理脚本统一管理** | 73 个脚本按 12 维度分类、注册、编排——审计、校验、扫描、健康检查 |
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
| 2 | 统一输出格式——所有扫描器输出标准 Finding Schema | 73 个脚本全部输出符合 Finding Schema 的 JSONL |
| 3 | pre-commit 门禁自动化——git commit 时自动阻断 V1 违规 | `.pre-commit-config.yaml` 中核心钩子有效运行 |
| 4 | 覆盖全部 12 维度 | 12/12 维度有可运行的扫描器 |
| 5 | 与任务系统闭合——Finding自动创建任务卡 | CRITICAL/HIGH Finding → 自动创建 BLOCKED 任务 |

### 1.6 不包含的目标

| # | 明确排除 | 原因 |
|---|---------|------|
| 1 | Web Dashboard / UI | 当前阶段纯 CLI |
| 2 | 自动修复（Auto-Fixer） | C4 阶段只跟踪不自动修——修复是两条生产线的职责 |
| 3 | GitHub Actions / CI 云端集成 | 暂不需要——项目在本地 |
| 4 | entity-graph 构建（D12 幻觉检测完全体） | 先上 SelfCheckGPT 零资源方案，entity-graph 是 Phase 2 |

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
| 5 | 脚本清单 | script_manifest.yaml | `D:\ZephyrAlpha\scripts\governance\script_manifest.yaml` | 73个脚本的完整注册表（SSoT） |
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
D1  结构完整性     d1_structure/       4个脚本
D2  链接完整性     d2_links/           4个脚本
D3  元数据合规     d3_metadata/        5个脚本
D4  路径有效性     d4_paths/           4个脚本
D5  架构合规       d5_architecture/    4个脚本
D6  安全漏洞       d6_security/        2个脚本
D7  代码质量       d7_code/            6个脚本
D8  文档代码同步   d8_doc_code_sync/   4个脚本
D9  知识覆盖       d9_knowledge/       2个脚本
D10 知识覆盖扩展   d10_knowledge/      3个脚本
D11 合规完整性     d11_compliance/     6个脚本
D12 AI幻觉检测     d12_ai_hallucination/ 1个脚本
Root             根级入口              4个脚本
Root-level       scripts/              2个脚本
─────────────────────────────────────────
总计 73 个脚本（截至 2026-05-02），覆盖率 12/12
```

### 3.2 按退出码分类（CI决策轴）

| 退出码 | 含义 | CI行为 | 对应Severity |
|:---:|------|--------|:---:|
| **0** | 全通过，零Finding | ✅ 通过 | — |
| **1** | 仅有WARNING/INFO（LOW, INFO） | ✅ 通过（不阻断提交） | LOW, INFO |
| **2** | 存在ERROR（HIGH,ERROR） | ❌ 阻断提交 | HIGH, ERROR |
| **3** | 脚本自身崩溃 | ❌ 阻断提交（脚本故障=门禁失效） | CRITICAL |

> 对标 PS-STD-012 §2.1 + 盲点 B10（沉默失败——脚本异常退出但 CI 显示绿色）→ 退出码 3 强制阻断

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

> **使用方式**：`python scripts/governance/run_all.py --tags Security,Quick` → 只运行打有 Security 或 Quick 标签的脚本。

> **待办**：`script_manifest.yaml` 中为每个脚本新增 `version` 字段——对标 OWASP ASVS 每个需求有唯一标识符+版本追溯。当前由 git history 隐式追踪，显式版本号利于 AI 判断脚本是否过期。

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
| 脚本总数 | **73** | script_manifest.yaml 注册数 |
| 维度数 | 12 | D1-D12 |
| 单维度最大脚本数 | 6（D7/D11） | 代码质量和合规完整性最密集 |
| 单维度最小脚本数 | 1（D12） | AI幻觉检测——种子维度 |

### 8.2 容量上限设计

| 维度 | 当前规模 | 设计上限 | 超限策略 |
|------|:---:|:---:|---------|
| 单维度脚本数 | 2~6 | **10** | 超过 10 考虑拆分为子维度（如 D7 → D7a/D7b） |
| 全局脚本总数 | 73 | **200** | 超过 200 考虑脚本分组 + 层级化 manifest |
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

## 9. 迁移与废弃方案

### 9.1 旧树脚本处理

| 对象 | 位置 | 处理方式 |
|------|------|---------|
| `_DO_NOT_USE_old_tree/` 下脚本 | `D:\ZephyrAlpha\_DO_NOT_USE_old_tree\scripts\` | **不做迁移**。旧树已归档——禁止使用 |
| 旧版 AGENTS.md | `D:\ZephyrAlpha\_DO_NOT_USE_old_tree\AGENTS.md` | 含 18 章完整版，92 处路径已失效。不作为规则来源 |

### 9.2 候选池设计文档处理

| 文件 | 路径 | 处理方式 |
|------|------|---------|
| vibe-coding-script-system-design.md | `D:\ZephyrAlpha\模块候选池\开发流程\氛围编程基础设施\` | **保留作为历史参考**。包含 Kimi K2.6 + GLM-5.1 完整调研数据。不做物理删除。冲突以本蓝图为准 |
| 01-脚本系统架构.md | `D:\ZephyrAlpha\模块候选池\开发流程\脚本任务知识库架构\` | 该文件是任务系统选型+路线文档——脚本系统专属内容已提取至本蓝图。候选池内保留原始链接 |

### 9.3 废弃的脚本路径（已在代码中更新）

原 `audit_factory/` → 现 `script_system/`（2026-05-02 重命名）：所有引用已同步更新。

---

## 10. 施工 Phase 规划

### Phase 0 — 最小闭环 MVP ✅ 已完成

```
D1-D5  现有脚本输出统一化为 Finding Schema 格式
       → scripts/governance/run_all.py 已可用
       → 73个脚本全部注册（script_manifest.yaml）
       → pre-commit 精简配置可用
       → 四档退出码（0/1/2/3）在 run_all.py 中已实现
```

### Phase 1 — 扩展覆盖（施工中）

| 任务 | 优先级 | 状态 |
|------|:---:|:---:|
| C2 分类器——去重 + 根因聚类 | P1 | 📋 Backlog |
| D6 安全扫描深度升级 | P1 | 📋 Backlog |
| C3 审计报告自动生成 | P1 | 📋 Backlog |
| D12 幻觉检测 v1（SelfCheckGPT 零资源方案） | P1 | 📋 Backlog |
| Finding → 任务卡自动创建（§6.3 集成） | **P0** | 📋 **本蓝图=施工依据** |
| C5→C1 反馈闭环——Finding模式→扫描规则升级 | P1 | 📋 Backlog |

### Phase 2 — 系统化

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
| R6 | **过度工程**——12维度×5阶段×3轴 = 180种组合 | 中 | 低 | 分阶段 rollout——先 P0 维度跑通，按反馈决定 Phase 2 |

### 12.2 正面后果

- **自动化门禁**：git commit 自动阻断 V1 违规（frontmatter 缺失）——不再依赖人工记忆
- **统一输出**：73 个脚本统一 Finding Schema → 跨维度趋势分析
- **AI 新手引导**：新 session AI 读完蓝图 → 知道"脚本系统存在" + "怎么运行检查"
- **可审计性**：Finding append-only 日志 + 退出码约定 → 每个发现可追溯

### 12.3 负面后果

- **维护负担**：Finding Schema 变更 → 73 个脚本输出逻辑同步更新
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
| **B13** | **缺少里程碑门禁** | pre-commit 只覆盖提交时刻——设计审查、发布前、归档前都没有自动化检查点 | Phase 2 新增里程碑门禁矩阵（对标 NASA SRR→PDR→CDR→TRR→SAR） |

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
| 全脚本可运行性 | 73 个脚本逐一 `--warn-only`，exit ≤ 1 | 每周 | 标记故障脚本 + 创建修复任务 OPS |
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
| Tier 3 | scripts/governance/*.py（73个脚本） | §3 分类体系 + §5 调度规范 + §7 质量标准 |

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
> 脚本系统——第三条生产线，Phase 0 MVP已交付

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
| `scripts/governance/d3_metadata/deep_content_scanner.py` | ✅ 已实现 | |
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
| `scripts/governance/d1_structure/drafts_zone_archiver.py` | ✅ 已实现 | |
| `scripts/governance/d1_structure/detect_orphan_py.py` | ✅ 已实现 | |
| `scripts/governance/d1_structure/check_index_integrity.py` | ✅ 已实现 | |
| `scripts/governance/d1_structure/detect_residual_files.py` | ✅ 已实现 | |
| `scripts/governance/d1_structure/detect_temp_files.py` | ✅ 已实现 | |
| `scripts/governance/d1_structure/cbg_reset.py` | ✅ 已实现 | |
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

### 14.5 路径索引使用指南

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

## 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-05-03 | 3.0.0 | **蓝图 V3 升级——全面对标专业机构**。(1) 新增 §1.7 自动化不可逾越的边界（6 条红线，对标 ITIL 4 自动化治理）。(2) 新增 §3.5 按自动化层级分类（L1/L2/L3，对标 ITIL 分层自动化策略）。(3) 新增 §3.6 按标签分类（6 个标签 + `--tags` 参数，对标 K8s Conformance 标签聚焦）。(4) §4.4 升级为 13 项入库验证矩阵（对标 K8s/CNCF 15 项自动验证）。(5) 新增 §4.5 插件接口契约 Plugin Contract（对标 Sonobuoy Plugin Skeleton）。(6) §5.2 新增 `--tags` 和 `--depth` 参数（quick/full/deep，对标 OWASP ASVS L1/L2/L3）。(7) 新增 §6.5 Finding Schema recommendation 字段（对标 ITIL Level 2 决策辅助）。(8) 新增 §8.4 SLA/SLO 度量指标（6 项，对标 ITIL 服务级别管理）。(9) §10 新增 C5→C1 反馈闭环 + 里程碑门禁（对标 ITIL SVS + NASA SRR→PDR→CDR→TRR→SAR）。(10) §12.4 新增盲点 B13（里程碑门禁缺失）。(11) **新增 §13 脚本系统运维与自我监控**——系统健康自检 + 应急回退 + 版本兼容 + 定期演练（对标 ITIL 应急管理）。(12) 个体脚本版本化注记（§3.6 待办，对标 OWASP ASVS 需求标识符）。Frontmatter 对标列表扩展至 ITIL 4 / OWASP ASVS v5 / K8s Conformance / NASA-STD-8739.8B / Terraform pre-commit / Cursor Rules / Windsurf Rules / Anthropic CLAUDE.md |
| 2026-05-02 | 2.0.0 | **蓝图 V2 升级**。(1) 全局重构——12章→10章，新增 §6 与任务系统集成接口、§3 脚本分类体系。(2) 过时数据修正——17个脚本→73个、覆盖率 92%→100%、D10"缺失"→"已有"。(3) 依赖声明新增 MOD-INF-006 G0-G7+G3.2.1+M1-M11 三个靶点。(4) 版本号 1.0.0→2.0.0 |
| 2026-05-02 | 1.0.0 | 初始创建——从候选池设计文档 v0.2.0 升格为正式蓝图 MOD-INF-005 |
