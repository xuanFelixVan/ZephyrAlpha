---
module_id: MOD-INF-005
submodule_path: src/zephyr/governance
title: 脚本系统蓝图 — 第三条生产线的自动化审计与门禁
doc_type: blueprint
status: Active
version: 5.5.0
layer: L0_infrastructure
layer_name: infrastructure
functional_domain: governance
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-03"
ttl: permanent
construction_progress: completed
actual_disk_path: "scripts/governance/"
belongs_to: "MOD-MASTER_BLUEPRINT"
dependencies:
  - MOD-INF-001
  - MOD-INF-003
  - MOD-INF-004
  - MOD-TASK_SYSTEM
  - MOD-KB-001
priority: P0
runtime_plane: hot
tags:
  - governance-automation
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
summary: 脚本系统——第三条独立生产线，12维度自动化审计与门禁，含增量扫描/缓存/去重/分布式执行架构。蓝图模板v3.5合规。
last_updated: "2026-05-15"
last_verified: "2026-05-15"
generation: 1
rule_form: structural
scope: global
stability: evolving
verifiability: hybrid
codification_level: L1
codification_at: "2026-05-13"
references: []
---

> actual_disk_path: src/zephyr/infrastructure/script_system/ + scripts/governance/ + scripts/governance/meta/ + scripts/governance/generators/ (12 .py files)
>
> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图模板 v3.5：[blueprint-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-template.md)
> - 压缩工作流标准：[trae_030_doc_numbering_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)
> - 代码头部标准：[code-construction-standards.md §7](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)
> - 优化规则：先 Layer 1（蓝图+施工图模板合规）→ 后 Layer 2（规格化砍削）

# Script System 蓝图 — 第三条生产线的自动化审计与门禁

脚本系统是 ZephyrAlpha 的自动化治理基础设施——12维度审计扫描、统一调度入口（run_all.py）、pre-commit门禁阻断、Finding全生命周期管理。横切两条生产线做系统级审计，不依附于任何一条线。当前177+治理脚本覆盖D1-D12全部维度，支持增量/全量/单维度扫描模式。

> **module_id**: MOD-INF-005 | **status**: Active | **layer**: L0_infrastructure

---

## §0 代码对齐验证

### §0.1 代码文件清单

> **架构归属SSoT**：`data/asset_index/project-architecture-panorama.yaml`
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[INVARIANTS]/[MODIFY-GUARD]/[CONSUMERS]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]` — 见防幻觉十八条

> 存在性受控词表：`未实现` / `已实现` / `已阻塞` / `已废弃`
> - `已实现`：代码已存在且通过验证 → 蓝图不再重复代码内容，接口签名见 §4
> - `已阻塞`：因外部依赖未就绪 → MUST 注明阻塞原因
> - `已废弃`：设计变更后不再需要 → MUST 在 §5.3 迁移方案中说明
> - 此列是当前事实（永久时态），不是施工进度追踪（临时时态）

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-INF-005`

| # | 文件路径 | 对应蓝图章节 | 职责 | 存在性 | 阻塞原因（仅已阻塞） |
|---|---------|------------|------|:-----:|-------------------|
| 1 | `src/zephyr/infrastructure/script_system/__init__.py` | §4 接口契约 | 包初始化 | 已实现 | — |
| 2 | `src/zephyr/infrastructure/script_system/finding.py` | §4 接口契约 | Finding Schema 数据模型 | 已实现 | — |
| 3 | `scripts/governance/run_all.py` | §5 调度规范 | 统一调度入口 | 已实现 | — |
| 4 | `scripts/governance/generators/generate_script_manifest.py` | §4 入库流程 | manifest 生成器 | 已实现 | — |
| 5 | `scripts/governance/meta/manage_kill_switch.py` | §16 Kill Switch | 全局冻结+单脚本禁用 | 已实现 | — |
| 6 | `scripts/governance/meta/manage_shadow_mode.py` | §17 Shadow Mode | 渐进激活管理 | 已实现 | — |
| 7 | `scripts/governance/meta/manage_baseline.py` | §18 Baseline | 快照对比管理 | 已实现 | — |
| 8 | `scripts/governance/meta/manage_error_budget.py` | §21 Error Budget | 双预算模型管理 | 已实现 | — |
| 9 | `scripts/governance/meta/validate_false_negatives.py` | §19 False Negative | 假阴性检测 | 已实现 | — |
| 10 | `scripts/governance/meta/finding_state_machine.py` | §20 Finding 状态机 | 全生命周期管理 | 已实现 | — |
| 11 | `scripts/governance/meta/validate_rules_file_backdoor.py` | §23 供应链安全 | Unicode 后门扫描 | 已实现 | — |
| 12 | `scripts/governance/meta/validate_rules_integrity.py` | §23 供应链安全 | SHA256 完整性校验 | 已实现 | — |
| 13 | `scripts/governance/architecture_health_dashboard.py` | §六 架构健康度 | 10项指标自动化检测基线（第0期，对标 architecture_debt_registry.md §六） | 已实现 | — |

### 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = completed → 代码文件清单100%存在 | `ls src/zephyr/infrastructure/script_system/` + `ls scripts/governance/` | ☐ |
| 蓝图描述的类/函数名 = 代码中的类/函数名 | `grep "class\|def" src/zephyr/infrastructure/script_system/finding.py` | ☐ |
| script-manifest.yaml 与蓝图 §3 维度分类一致 | `python scripts/governance/run_all.py --list` | ☐ |
| pre-commit hook 配置与蓝图 §5 一致 | `cat .pre-commit-config.yaml` | ☐ |

### 版本-代码映射

| 代码覆盖范围 | 缺失组件 | 缺失原因 |
|------------|---------|---------|
| finding.py + run_all.py + 120+ 治理脚本 + 配置文件 | validate_blueprint_overlap.py | 待施工 |

---

## ⚠️ 安全删除协议

本蓝图不涉及文件删除。蓝图描述的脚本系统为纯新增/扩展型模块，无废弃/迁移文件。

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | 脚本系统代码 | `D:\ZephyrAlpha\src\zephyr\infrastructure\script_system\` | 修改 | 蓝图描述的核心代码 |
| 2 | 治理脚本目录 | `D:\ZephyrAlpha\scripts\governance\` | 修改 | 审计脚本存放目录 |
| 3 | 脚本清单 | `D:\ZephyrAlpha\scripts\governance\script-manifest.yaml` | 修改 | 脚本注册表 |
| 4 | 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\governance-automation\blueprint.md` | 修改 | 本文件 |

---

## 1. 概述与模块定位 (§1 设计背景与目标)

### 1.1 模块身份

| 属性 | 值 |
|------|-----|
| module_id | MOD-INF-005 |
| 层级 | L0_infrastructure（基础设施层） |
| 功能域 | 脚本治理基础设施 |
| 优先级 | P0（阻断级——脚本系统故障 = 所有门禁失效） |

### 1.2 核心职责

| # | 职责 | 说明 |
|---|------|------|
| 1 | **治理脚本统一管理** | manifest 注册的脚本按 12 维度分类、注册、编排——审计、校验、扫描、健康检查（数以 `total_scripts` 为准，当前约 **177**） |
| 2 | **脚本三件套入库流程** | 任何新脚本必须走：落位→manifest注册→运行验证——缺一步不视为入库 |
| 3 | **run_all.py 调度编排** | 统一入口，支持全维度/单维度/指定维度扫描，输出结构化报告 |
| 4 | **pre-commit 门禁集成** | git commit 时自动阻断违规——V1 违规硬阻断，V2 违规警告 |
| 5 | **与任务系统集成** | 脚本失败→关联任务 BLOCKED；Finding→自动创建修复任务卡 |

> 脚本系统是自动化治理基础设施——不直接生产业务代码或需求，而是在代码和文档提交后自动检查合规性。横切两条生产线做系统级审计，不依附于任何一条线。

### 1.3 在三线体系中的位置

本系统是第三条独立生产线——不依附于任何一条线，横切两线做系统级审计。当/如果前两条线的内嵌审计不够用 → 则必须使用本系统做系统级横切审计。

### 1.4 设计背景 (§1.1 背景)

当/如果已有两条线的内嵌审计只审计自己管线内的产出 → 则必须建立独立脚本系统回答：系统整体健康？历史发现修了没？新文件是否破坏架构？

### 1.5 目标 (§1.2 目标)

| # | 目标 | 可衡量标准 |
|---|------|-----------|
| 1 | 建立统一脚本入口——一键运行所有审计检查 | `python scripts/governance/run_all.py` 可执行 |
| 2 | 统一输出格式——所有扫描器输出标准 Finding Schema | 全部脚本输出符合 Finding Schema 的 JSONL（以 script-manifest.yaml 为准） |
| 3 | pre-commit 门禁自动化——git commit 时自动阻断 V1 违规 | `.pre-commit-config.yaml` 中核心钩子有效运行 |
| 4 | 覆盖全部 12 维度 | 12/12 维度有可运行的扫描器 |
| 5 | 与任务系统闭合——Finding自动创建任务卡 | CRITICAL/HIGH Finding → 自动创建 BLOCKED 任务 |

### 1.6 不包含的目标 (§1.3 不包含的目标)

| # | 明确排除 | 原因 |
|---|---------|------|
| 1 | Web Dashboard / UI | 纯 CLI |
| 2 | 自动修复（Auto-Fixer） | C4 只跟踪不修复 |
| 3 | GitHub Actions / CI 云端集成 | 项目在本地 |
| 4 | entity-graph 构建（D12 完全体） | 先上 SelfCheckGPT 零资源方案 |

### 1.8 运行场景约束 (§1.4)

| 约束 | 影响 |
|------|------|
| Windows 单机环境（i7-12700KF / 64GB / RTX 3090） | 脚本系统设计为单机运行，不依赖分布式存储/计算 |
| CPU/RAM/磁盘 I/O 共享 | 治理脚本与开发环境共享资源，需控制并发度（ThreadPoolExecutor max_workers=8） |
| pre-commit 同步阻塞 | git commit 时 pre-commit hook 同步执行，脚本超时直接影响提交体验 |
| AI 并发 Session: 1~100 | §35/§36 并发架构，增量扫描模式支撑 100 并发 |

### 1.7 自动化不可逾越的边界

以下边界是脚本系统**绝对不能跨越的**——任何脚本触及这些红线时必须上报人工决策，不得自动执行：

| # | 红线 | 说明 | 脚本行为 |
|---|------|------|---------|
| 1 | **自动修改源码** | 脚本只能报告问题，不能自行修改 `src/zephyr/` 下的代码 | 报告 Finding，不执行修复 |
| 2 | **自动删除文件** | 脚本不能自行删除任何项目文件 | 报告 Finding（如废弃文件），由人工决定删除 |
| 3 | **自动修改配置文件** | `pyproject.toml`、`pre-commit-config.yaml` 等配置的修改必须人工审核 | 报告漂移检测，不自动修改 |
| 4 | **自动跳过门禁** | 脚本不能绕过 pre-commit 门禁或 CI 闸门 | 退出码严格 0/1/2/3，不伪造输出 |
| 5 | **自动修改登记表** | `registry-master-index.yaml` 等核心登记表的修改必须经 AI+人工确认 | 报告不一致，不自动写入 |
| 6 | **自我修改** | 脚本不能修改脚本系统自身的代码（包括其他脚本 + 本蓝图） | 报告自身问题，交由其他脚本或人工修复 |

---

## 2. 必备链接与依赖声明

### 2.1 必备链接

| # | 文件 | module_id | 完整绝对路径 | 用途 |
|---|------|-----------|------------|------|
| 1 | 任务系统蓝图 | MOD-TASK_SYSTEM | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\task_system\blueprint.md` | 门禁体系 G0-G7 + 管线节点 M1-M11——脚本失败→任务状态转换的接口定义 |
| 2 | 元数据注册表 | PS-STD-001 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_043_meta_rule_metadata.yaml` | frontmatter schema + META-V 验证规则 |
| 3 | 规则验证标准 | PS-STD-012 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_041_meta_rule_classification.yaml` | V1~V4 四级验证体系 |
| 4 | 脚本质量标准 | SCRIPT-QUALITY-001 | `D:\ZephyrAlpha\scripts\governance\quality-standard.md` | 8维度×38条款——脚本自身的质量约束 |
| 5 | 脚本清单 | script-manifest.yaml | `D:\ZephyrAlpha\scripts\governance\script-manifest.yaml` | 脚本的完整注册表（SSoT，以实际生成为准）——REG-SCRIPT-001 主清单 + REG-SCRIPT-002 Governance 子集 |
| 6 | AGENTS.md | — | `D:\ZephyrAlpha\AGENTS.md` | §6.5 脚本入库强制约定——蓝图的法律依据 |
| 7 | 脚本治理入口 | index.md | `D:\ZephyrAlpha\scripts\governance\index.md` | AI 施工时查"已有哪些脚本" |
| 8 | 模块登记表 | — | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | 模块编号注册 |
| 9 | 脚本质量标准 | REG-STD-003 / SCRIPT-QUALITY-001 | `D:\ZephyrAlpha\scripts\governance\quality-standard.md` | 8维度×38条款——脚本自身的质量约束（同 #4，双注册） |

### 2.2 depends_on 声明

| target | at | 用途 |
|--------|-----|------|
| MOD-TASK_SYSTEM | §4 | G0-G7门禁体系 |
| MOD-TASK_SYSTEM | §5 | 管线M1-M11 |
| MOD-TASK_SYSTEM | §3.2.1 + §4.2 + §3.1.2 | TaskCard + 10状态机 + task_id |
| MOD-KB-001 | §3.2 + §6 | KE Schema + KB入库 |
| PS-STD-001 | §7 | metadata注册表 |
| SCRIPT-QUALITY-001 | §2 | 退出码约定（0/1/2/3） |

### 2.3 与已有类似功能的区别

| 已有模块 | 重叠点 | 区别 |
|---------|--------|------|
| MOD-INF-004 vibe-coding-pipelines | 脚本系统被提及 | MOD-INF-004 管管线编排，本系统管审计产出物 |
| MOD-TASK_SYSTEM task_system | 任务管线里有审计 | MOD-TASK_SYSTEM 是内嵌审计，本系统是系统级横切审计 |

---

## §2 模块边界

### 2.1 职责范围 (§2.1)

| # | 职责 | 说明 |
|---|------|------|
| 1 | 治理脚本统一管理 | 12 维度分类、注册、编排 |
| 2 | 脚本三件套入库 | 落位→manifest注册→运行验证 |
| 3 | run_all.py 调度 | 全维度/单维度/增量/全量扫描 |
| 4 | pre-commit 门禁 | git commit 自动阻断 V1 违规 |
| 5 | 与任务系统集成 | Finding→任务卡自动创建 |
| 6 | 系统自我监控 | 健康自检+应急回退+Kill Switch+Shadow Mode+Error Budget |

### 2.2 不包含的职责 (§2.2)

| # | 排除项 | 由谁负责 |
|---|--------|---------|
| 1 | Web Dashboard / UI | 未来前端模块 |
| 2 | 自动修复（Auto-Fixer） | 两条生产线（Spec Factory / Task Pipeline） |
| 3 | GitHub Actions / CI 云端集成 | 未来 CI 模块 |
| 4 | 自动修改源码/配置/登记表 | 人工决策（§1.7 六条红线） |
| 5 | 自动删除文件 | 人工决策（§1.7 六条红线） |

---

## 3. 脚本分类体系 (§3 架构设计)

脚本按三个轴分类：**维度 × 退出码 × 触发方式**。

### 3.1 按审计维度分类（主分类轴）(§3.1 组件架构)

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
总计以 `script-manifest.yaml` 的 `total_scripts` 为准（当前生成约 **177**），覆盖率 12/12
```

### 3.2 按退出码分类（CI决策轴）

| 退出码 | 含义 | CI行为 | 对应Severity |
|:---:|------|--------|:---:|
| **0** | 全通过，零Finding | ✅ 通过 | — |
| **1** | 仅有WARNING/INFO（LOW, INFO） | ✅ 通过（不阻断提交） | LOW, INFO |
| **2** | 存在ERROR（HIGH,ERROR） | ❌ 阻断提交 | HIGH, ERROR |
| **3** | 脚本自身崩溃 | ❌ 阻断提交（脚本故障=门禁失效） | CRITICAL |

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

### 3.5 按自动化层级分类

| 层级 | 名称 | 含义 | 人机分工 | 代表脚本 |
|:---:|------|------|---------|---------|
| **L1** | 标准化作业自动化 | 规则明确、重复性高、人工干预价值有限的任务 | 脚本全自动执行，人工仅在异常时介入 | `validate_frontmatter.py`（D3）、`check_links.py`（D2） |
| **L2** | 决策辅助自动化 | 需数据分析和建议，但最终决策由人工完成 | 脚本产出分析+建议，人工裁定 | `audit_knowledge_gaps.py`（D9）、`detect_ruins_references.py`（D4） |
| **L3** | 智能决策自动化 | 在预定规则下自主做出决策 | 脚本自主决策，必须有完善监控+回退机制 | `check_architecture_gates.py`（D5，CI中硬阻断） |

### 3.6 按标签分类

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
> **自动推导规则**（`generate_script_manifest.py` 生成时自动计算，存入 `script-manifest.yaml`）：
>
> | 来源 | 规则 |
> |------|------|
> | 维度 | D1-D4,D8 → `Quick` / D5,D7 → `Critical` / D6,D11 → `Security`, `Critical` / D9,D12 → `AI-Generated`, `Periodic` / D10 → `Periodic` |
> | 前缀 | `fix_*`, `generate_*` → `Disruptive`（追加） / `audit_*` → `Periodic`（追加） |
> | 优先级 | P0 → `Critical`（追加，若未因维度获得） |
>
> **AI 公约**：新脚本**无需在 `__manifest__` 块中显式声明 tags**——生成器自动从维度+前缀+优先级推导。标签总会出现在 `script-manifest.yaml` 中，run_all.py 从 manifest 读取标签执行过滤。

---

### 3.7 数据流 (§3.2)

| # | 上游 | 处理逻辑 | 下游 | 数据格式 |
|---|--------|---------|---------|---------|
| 1 | git commit / 手动触发 | run_all.py 读取 manifest → 按维度调度脚本 | 各维度脚本 | manifest YAML |
| 2 | 各维度脚本 | 脚本执行扫描 → 产出 Finding JSONL | C2 分类阶段 | Finding JSONL |
| 3 | C2 分类 | 按 severity 分级 → 去重 | C3 报告 | Finding dict |
| 4 | C3 报告 | 生成结构化报告 + 退出码判定 | pre-commit / 人工 | exit code + report |
| 5 | C4 跟踪 | Finding → 任务卡自动创建 | MOD-TASK_SYSTEM 任务系统 | TaskCard |

### 3.8 状态生命周期 (§3.3)

| 当前状态 | 触发事件 | 目标状态 | 守卫条件 |
|---------|---------|---------|---------|
| IDLE | git commit / 手动触发 | SCANNING | manifest 可读 |
| SCANNING | 全部脚本完成 | REPORTING | 无脚本 exit=3 |
| SCANNING | 脚本 exit=3 | ERROR | 脚本自身崩溃 |
| REPORTING | 报告生成完成 | GATING | Finding 已分级 |
| GATING | exit=0/1 | PASSED | 无 V1 违规 |
| GATING | exit=2 | BLOCKED | 存在 V1 违规 |
| PASSED/BLOCKED | Finding 创建 | TRACKING | severity ≥ HIGH |
| TRACKING | 任务卡创建 | IDLE | 任务系统确认 |

---

### 3.9 ScriptImpactMap（脚本→文件依赖图谱）

增量扫描的核心组件——回答"改了这个文件，该跑哪些脚本？"。

**双层索引**:
- L1: 文件→脚本（正向索引，增量扫描核心查询）
- L2: 脚本→文件（逆向索引，缓存失效用）

**三种映射来源**:

| 来源 | 优先级 | 触发时机 |
|------|:---:|------|
| 声明式（`__manifest__` 的 `target_files`/`target_modules`） | 1 | 脚本注册时 |
| 模块归属（directory-registry.md） | 2 | 构建时 |
| 自动推导（ScriptTracer 监控 `open()`/`Path.read_*()` 调用） | 3 | 脚本执行后 |

**存储**: SQLite `impact_map` 表（WAL 模式），10,000脚本×200文件/脚本≈2M条边<50MB。

**增量扫描查询流程**:
```
git diff --name-only → changed_files
→ 模块归属推导 → ImpactMap.lookup(file_list) → affected_scripts
→ 按维度拓扑排序（§5.3 裁剪空维度）→ 缓存检查 → 去重检查 → 并行执行
```

### 3.10 ScriptResultCache（执行结果缓存）

避免 100 AI 并发下同一脚本的重复执行。

| 参数 | 值 |
|------|-----|
| 缓存键 | `sha256(script_path + script_content_hash + impacted_files_hash)` |
| 存储 | SQLite（与 governance.db 同 DB，分表） |
| TTL | Quick 脚本 120s / Content 脚本 600s / AI 脚本 1800s |
| 驱逐策略 | LRU，max_entries=50,000 |
| 失效触发 | TTL过期 / 关联文件变更(git diff) / 脚本代码变更 / `--no-cache` |

**缓存一致性协议**: git diff→changed_files → 对每个候选脚本计算 cache_key → hit→直接返回 / miss→入执行队列 → 执行完写入缓存。

预估缓存命中率: 100 AI 并发增量扫描下 ~75%（CPU 节省 75%）。

### 3.11 CrossSessionDeduplicator（跨 Session 去重）

100 AI 并发增量扫描下，同一脚本+同一 input_hash 只执行 1 次，后续 session 等待结果。

**两层模型**:
- L1 全局级: SQLite `execution_registry` 表，status=PENDING/RUNNING/DONE/STALE，等待超时 300s
- L2 Session 级: run_all.py 入队前去重集合

**与 ScriptResultCache 协作**: 先查缓存（hit→返回）→ miss→查去重器（RUNNING→等待 / 无→提交执行）。

### 3.12 Manifest 分层索引

10,000 条目下的 manifest 加载性能优化。

```
scripts/governance/
  script_index.yaml                       ← L0 索引（维度→脚本数，标签→脚本列表）
  manifest/
    d1_structuremanifest.yaml            ← per-dimension manifest
    ...
    metamanifest.yaml
  script-manifest.yaml                    ← 全量 SSoT（per-dimension manifest 派生）
```

**加载策略**: `--list`→只读 L0 index(<10ms) / `--dimensions d3,d5`→读 index+D3+D5 manifest(<100ms) / `--full`→全量 manifest(~5s，仅周检)。

**script-manifest.yaml 仍是全量 SSoT**——per-dimension manifest 由 `generate_script_manifest.py` 自动派生，不改 AI 的脚本注册流程。

## 4. 脚本三件套入库流程 (§4 接口契约)

### 4.1 设计原则 (§4.2 数据模型)

AGENTS.md §6.5（脚本自创入库强制约定）：
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
| **B manifest注册** | 在 `scripts/governance/script-manifest.yaml` 添加条目（dimensions + priority + timeout + args + description） | `python scripts/governance/check_registry_consistency.py` → 零不一致 |
| **C 运行验证** | `python scripts/governance/{dimension}/{script}.py --warn-only` → exit 0 + 零诊断 | 四档退出码（0=全通过/1=警告/2=错误/3=崩溃） |

> **清单生成（病根闭环）**：`script-manifest.yaml` 为 **生成物**——须在各 `.py` 内维护 `__manifest__` 并运行 `python scripts/governance/generators/generate_script_manifest.py`。生成器 **同时支持**：（1）ASCII 三引号包裹的 YAML；（2）模块顶层的 `__manifest__ = { ... }` **dict 字面量**（`ast` 解析）。历史上仅支持（1）导致（2）被误报为「缺失 manifest」、清单与 `run_all` 漂移。

### 4.4 入库验证矩阵

新脚本入库前必须通过以下矩阵中的所有强制性检查：

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

定义脚本接入 `run_all.py` 编排的最小接口要求。任何遵守此契约的脚本可被 `run_all.py` 自动发现和调度。

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
    file: "scripts/governance/script-manifest.yaml"
    required_fields:
      - dimensions
      - priority
      - timeout
      - args
      - description
```

---

### 4.6 公共 API (§4.1)

| API | 签名 | 说明 |
|-----|------|------|
| `run_all_dimensions()` | `(dimensions: list[str] = None) -> dict` | 统一调度入口 |
| `generate_manifest()` | `(scripts_dir: str) -> dict` | manifest 生成器 |
| `validate_script_entry()` | `(script_path: str) -> tuple[bool, str]` | 脚本入库验证 |
| `create_task_from_finding()` | `(finding: Finding) -> str` | Finding→任务卡 |

### 4.7 输入契约 (§4.3)

| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| `run_all_dimensions()` | `dimensions` | ❌ | None=全维度，否则维度ID列表 |
| `run_all_dimensions()` | `--tags` | ❌ | 标签过滤（AND 语义） |
| `run_all_dimensions()` | `--depth` | ❌ | quick/full/deep |
| `validate_script_entry()` | `script_path` | ✅ | 必须在 scripts/governance/ 下 |
| `validate_script_entry()` | `__manifest__` | ✅ | 脚本内必须包含 manifest 块 |

### 4.8 输出契约 (§4.4)

| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| `run_all_dimensions()` | `dict`：`{dimensions_run, total_findings, exit_code}` | exit=3（manifest 不可读） |
| `validate_script_entry()` | `(True, "OK")` | `(False, "reason")` |
| 各维度脚本 | Finding JSONL + exit 0/1 | exit 2（V1 违规）/ exit 3（脚本崩溃） |

### 4.9 MCP 接口 (§4.5)

本模块不暴露 MCP 接口。

### 4.10 契约版本 (§4.6)

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| Finding Schema 新增字段 | ✅ 向后兼容 | 不影响已有消费者 |
| 退出码语义变更 | ❌ 破坏性 | 需 Owner 审批 |
| 维度 ID 新增 | ✅ 向后兼容 | 不破坏已有逻辑 |
| manifest 格式变更 | ❌ 破坏性 | 需 Owner 审批 + 迁移方案 |

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

| 扫描模式 | 超时值 | 定义位置 |
|---------|:---:|------|
| 增量（默认） | 180s | `capacity_params.yaml` |
| 部分（批量） | 600s | `capacity_params.yaml` |
| 全量（可选） | 10800s（3h） | `capacity_params.yaml` |
| 紧急 | 不设超时 | `capacity_params.yaml` |
| 单脚本默认 | 120s | `capacity_params.yaml` |

| 维度类型 | 单维度超时 |
|---------|:---:|
| 文件扫描类（D1,D2,D3,D4） | 30s |
| 内容分析类（D5,D6,D7,D8） | 60s |
| 知识/AI类（D9,D10,D11,D12） | 120s |

超时值从 `capacity_params.yaml` 动态读取，不硬编码。超时后的脚本标记为 exit code 3——强制阻断。

### 5.5 编码铁律

所有脚本文件开头必须：

```python
import sys
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
```

### 5.6 产出物命名规范

run_all.py 和独立脚本的产出物按以下格式命名，保证任何人看到文件名即知内容：

| 阶段 | 文件名模式 | 示例 |
|------|-----------|------|
| C1 扫描原始输出 | `scan-{dimension}-{YYYYMMDD}-{session_id}.json` | `scan-d2-20260425-session_trae_01.json` |
| C2 分类后 Finding | `findings-{dimension}-{YYYYMMDD}-{session_id}.jsonl` | `findings-d2-20260425-session_trae_01.jsonl` |
| C3 单维度报告 | `RPT-AUDIT-{dimension}-{YYYYMMDD}.md` | `RPT-AUDIT-D2-20260425.md` |
| C3 全维度报告 | `RPT-AUDIT-FULL-{YYYYMMDD}.md` | `RPT-AUDIT-FULL-20260425.md` |
| C3 周度周期报告 | `RPT-AUDIT-PERIODIC-WEEKLY-{YYYYMMDD}.md` | `RPT-AUDIT-PERIODIC-WEEKLY-20260502.md` |
| C3 增量差异报告 | `RPT-AUDIT-DELTA-{YYYYMMDD}.md` | `RPT-AUDIT-DELTA-20260502.md` |
| C4 修复日志 | `remediation-log-{YYYYMMDD}.md` | `remediation-log-20260502.md` |
| C5 知识条目 | `KE-{NNN}-{topic}.md` | `KE-035-encoding-lesson.md` |

> **唯一定位公式**：`{文件类型前缀}-{维度|编号}-{日期}-{session_id}`（全量扫描无 session_id 时兼容旧格式）。


### 5.7 扫描模式切换架构

**模式优先级**:

| 触发源 | 条件 | 模式 |
|--------|------|------|
| git pre-commit hook | changed_files ≤ 50 | INCREMENTAL（默认，<1min） |
| git pre-commit hook | changed_files 50-100 | INCREMENTAL + debounce 500ms |
| git pre-commit hook | changed_files > 100 | PARTIAL（按模块分批，~5min） |
| 手动 `--diff-ref HEAD~1` | — | INCREMENTAL |
| 手动 `--full` | — | FULL_SCAN（仅周末/手动） |
| 手动 `--tags Critical` | — | INCREMENTAL（按标签+ImpactMap裁剪） |
| 手动无参数 | — | 提示确认全量扫描耗时 |
| cron `0 2 * * 0` | — | FULL_SCAN（周日凌晨） |

**run_all.py 新增入口参数**:

| 参数 | 说明 |
|------|------|
| `--diff-ref` | Git diff 参照点，触发增量扫描 |
| `--full` | 强制全量扫描 |
| `--session-id` | AI session ID，用于产出物命名隔离+CrossSessionDeduplicator |
| `--no-cache` | 禁用 ScriptResultCache（调试用） |

**增量拓扑按需裁剪**: 依赖链上只有 `affected_scripts > 0` 的维度才入队，空维度跳过但记录日志。跨链并行依然有效。

**pre-commit hook 配置**: 增量扫描为默认钩子（`governance-incremental`），全量扫描为手动触发钩子（`governance-full`，stages: [manual]）。

---

## 6. 与任务系统的集成接口

### 6.1 集成模式：脚本失败 → 任务阻塞

当脚本系统检测到违规时，通过任务系统 MOD-TASK_SYSTEM 的门禁体系（G0-G7）将关联任务置为 BLOCKED：

```
脚本系统                              任务系统
────────                              ────────
run_all.py 产出 Finding              ↓
  ↓
Finding.severity = CRITICAL/HIGH
  ↓
GATE-n 判定 → FAIL                   ↓
  ↓
关联任务的 status → BLOCKED           (MOD-TASK_SYSTEM §4 G0-G7)
  ↓
修复 Finding → GATE-n 重跑 → PASS     ↓
  ↓
关联任务的 status → TODO              (MOD-TASK_SYSTEM §5 M1-M11)
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

MEDIUM 及以上 Finding 应包含 `recommendation` 字段，给出修复建议但不自动执行。

| 字段 | 类型 | 说明 |
|------|------|------|
| `recommendation` | string | 修复建议——人类可读的操作指引。仅建议，不执行 |
| `recommendation_type` | enum | `auto_fixable`（可自动化修复）/ `manual_only`（必须人工修复）/ `needs_review`（需进一步分析） |
| `recommended_action` | enum | `modify_file` / `create_task` / `consult_owner` / `ignore` |

---
### 6.4 task_id 格式约定

脚本系统创建的追踪任务使用 `OPS-{SEQ}` 命名空间（对齐 MOD-TASK_SYSTEM §3.2.1 task_id 的 `{NAMESPACE}-{SEQ}` 格式——脚本系统属 OPS 操作域）：

```
OPS-001: D1 维度脚本注册验证任务
OPS-002: D3 维度 frontmatter 合规修复任务
...
```

---

## §6 错误处理

| 错误场景 | 检测方式 | 恢复策略 | 退出码 |
|---------|---------|---------|:---:|
| 脚本自身崩溃（ImportError/SyntaxError） | 顶层 try/except 捕获 | exit 3 强制阻断 + 创建修复任务 | 3 |
| manifest 不可读/解析失败 | run_all.py 启动时校验 | exit 3 编排器自身不可用 | 3 |
| 单脚本超时 | capacity_params.yaml 超时值 | 标记 exit 3 + 跳过 + 继续其他脚本 | 3 |
| SQLite 写入锁争抢 | busy_timeout 5s | WriteBatcher 批量合并（L级）/ 排队等待（S/M级） | — |
| Kill Switch 全局冻结 | run_all.py 启动时读取 kill-switch-state.yaml | 拒绝执行新脚本（exit 2） | 2 |
| 脚本误报阻断提交 | Owner 确认后 `git commit --no-verify` | 24h内修复脚本 + Session Log 记录绕过原因 | — |
| 脚本系统全部故障 | ImportError / SyntaxError | 紧急绕过 `--no-verify` + 事后修复 | — |
| D1 前置维度假阴性 | §19 False Negative 检测 | Golden Test Case 验证 + Error Budget 消耗 | — |

---

## 7. 脚本质量标准

### 7.1 质量文档

完整标准定义在独立文件：**SCRIPT-QUALITY-001**

| 属性 | 值 |
|------|-----|
| 路径 | `D:\ZephyrAlpha\scripts\governance\quality-standard.md` |
| 范围 | 8 维度 × 38 条款（22 MUST + 16 SHOULD） |

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

## §5 约束条件

### 5.1 技术约束 (§5.1)

> 蓝图只保留约束本身。"为什么这样约束"属于决策过程，记录在 §18 决策记录中。

| # | 约束 | 值 |
|---|------|-----|
| 1 | Python 版本 | 3.12+ |
| 2 | 运行环境 | Windows 单机 |
| 3 | 并行模型 | ThreadPoolExecutor（禁止串行 subprocess） |
| 4 | 写入模型 | 原子写入（temp-file + os.replace） |
| 5 | 数据模型 | Pydantic V2 BaseModel（禁止 @dataclass） |
| 6 | 编码约束 | 禁止 open(path, 'w') 无 encoding |

### 5.2 容量估算 (§5.2)

> 详见下方 `## 8. 容量估算` 章节。S/M/L/XL 四级规模-架构映射模型。

### 5.3 迁移 (§5.3)

> **时态属性**：迁移方案属于**临时时态**——执行完毕后即成为历史，不再属于蓝图。
> 压缩时判定：迁移方案已全部执行 → 从蓝图删除，归入变更记录。未执行 → 保留。

本蓝图不涉及迁移。

---

---

## §8 安全考量

| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | 脚本执行任意代码 | 高 | §1.7 六条红线——禁止自动修改/删除/跳过门禁 | `validate_gate_discipline.py` |
| 2 | pre-commit hook 被绕过 | 高 | 退出码严格 0/1/2/3，exit=3 强制阻断 | `check_architecture_gates.py` |
| 3 | Rules File 供应链投毒 | 高 | Unicode Backdoor 扫描 + SHA256 完整性校验 | `validate_rules_file_backdoor.py` + `validate_rules_integrity.py` |
| 4 | 密钥/凭证泄露 | 高 | `detect_secrets.py` 扫描 | D6 维度脚本 |
| 5 | 脚本自身崩溃导致门禁失效 | 高 | exit=3 强制阻断 + Kill Switch 全局冻结 | `manage_kill_switch.py` |

---

## §9 测试策略

| # | 测试类型 | 覆盖范围 | 关键测试用例 | 通过标准 |
|---|---------|---------|------------|---------|
| 1 | 单元测试 | Finding Schema / manifest 生成 / 入库验证 | Finding 序列化/反序列化、manifest 解析 | 覆盖率 ≥ 80% |
| 2 | 集成测试 | run_all.py → 脚本 → Finding → 任务系统 | 全维度扫描 E2E、pre-commit hook 触发 | 端到端通过 |
| 3 | 回归测试 | 脚本退出码 / Finding 格式 | 退出码 0/1/2/3 语义不变 | 退出码行为一致 |
| 4 | False Negative 测试 | Golden Test Case 库 | 已知坏用例检测率 | ≥ 90% |
| 5 | Shadow Mode 测试 | 新脚本渐进激活 | Phase1→Phase2→Phase3 | 假阳性 < 20% |

---

## 8. 容量估算

### 8.1 当前规模

| 维度 | 当前值 | 说明 |
|------|:---:|------|
| 蓝图数 | **51** | docs/03_modules/ 下 blueprint.md 文件数 |
| 脚本总数 | **268**（manifest 注册口径）/ **292**（磁盘 .py 文件数） | script-manifest.yaml 的 `total_scripts` |
| 脚本/蓝图比 | **5.25** | 268 ÷ 51 — 每个蓝图平均对应 5.25 个治理脚本 |
| 维度数 | 12 | D1-D12 |
| 单维度最大脚本数 | **45**（D5） | 架构合规最密集 |
| 单维度最小脚本数（已登记维） | **0**（D10 占位） | 性能治理待施工；非空维最小为 2（D2/D9） |

### 8.2 容量上限设计

> **换算依据**：当前 51 蓝图 → 268 脚本（5.25 脚本/蓝图）。1500 模块 × 5.25 ≈ **7,875 脚本**。
> 考虑到模块成熟后脚本密度可能下降（基础设施层脚本复用度高），取保守系数 0.8 → **6,300 脚本**；
> 考虑到 AI 并发场景下新增的专项检测脚本（D12 幻觉检测等），取扩张系数 1.3 → **10,200 脚本**。
> **设计上限取 10,000**，留 2x 安全裕度。

| 维度 | 当前规模 | 设计上限 | 超限策略 |
|------|:---:|:---:|---------|
| 全局蓝图/模块数 | 51 | **1,500** | 超过 1500 考虑子项目拆分 + 独立脚本系统实例 |
| 全局脚本总数 | 268（manifest 注册口径） | **10,000** | 超过 10000 考虑脚本分组 + 层级化 manifest + 分布式执行（§35） |
| 单维度脚本数 | 0~45 | **200** | 超过 200 拆分为子维度（如 D5 → D5a/D5b/D5c） |
| 每周 Finding 数 | ~200 | **5,000** | 超过 5000 触发 C2 根因聚类 + 降级扫描频率 |
| 并发 AI Worker | 1（当前） | **100** | 超过 100 需要分布式锁后端（Redis/etcd）+ Worker 生命周期管理（§35） |
| SQLite 单文件 | <10MB | 140TB（SQLite上限） | 不会触及——但超过 10,000 脚本后建议分片（ShardRouter 4→16 分片） |
| pre-commit 钩子数 | 5 核心 | 10 | 过 10 分组并行——避免阻塞提交时间过长 |
| 扫描总耗时（全量） | ~50s | **3,600s**（60 分钟） | 超时部分维度标记为 skip + WARNING；增量扫描作为默认模式 |
| ScanCache 条目数 | 500 | **10,000** | 1500 模块下文件数可能超过 50,000，LRU 缓存需相应扩容 |

### 8.3 扩展触发条件

触发维度扩容的阈值：
- 单维度脚本数 ≥ 8 → 结构审查——是否需要拆子维度
- 全局脚本数 ≥ 500 → 架构审查——manifest 是否需要分层 + 是否需要接入 BulkheadExecutor
- 全局脚本数 ≥ 2,000 → 架构审查——是否需要分布式执行（§35）
- 全局脚本数 ≥ 5,000 → 架构审查——ShardRouter 分片数是否需要从 4 扩展到 16+
- 扫描耗时 ≥ 300s → 性能审查——是否需要增量扫描/缓存
- 并发 AI Worker ≥ 10 → 并发审查——是否需要接入分布式锁后端

### 8.4 规模-架构映射模型

不同规模对应不同架构层级，避免小规模过度工程、大规模架构不足。

| 规模区间 | 脚本数 | AI Worker | 架构层级 | 关键组件 |
|---------|:---:|:---:|---------|---------|
| **S** (当前) | ≤500 | ≤8 | 单机单进程 | ThreadPoolExecutor + ProcessLock + SQLite 单文件 |
| **M** (过渡) | 500~2,000 | 8~20 | 单机多进程 | BulkheadExecutorV2 + ShardRouter(4) + SQLite WAL + 增量扫描默认 |
| **L** (目标) | 2,000~10,000 | 20~100 | 分布式 | 分布式任务队列(§35) + Redis/etcd 锁 + ShardRouter(16) + Worker 注册/心跳 |
| **XL** (远期) | >10,000 | >100 | 多集群 | 多实例脚本系统 + 跨实例 Finding 聚合 + 全局 Error Budget 协调 |

> S 规模（268 脚本），已预建 M/L 层级核心组件（BulkheadExecutorV2、ShardRouter、DistributedLock Protocol）。

### 8.5 硬件容量评估

> 基于开发机实际配置评估各规模层级的硬件可行性。

**开发机配置**：Intel i7-12700KF（12 核 20 线程）/ 64GB DDR4 / 1TB NVMe SSD + 1TB SATA SSD

| 规模层级 | 脚本数 | 并发 Worker | 内存需求 | CPU 占用 | 磁盘 I/O | 开发机能否支撑 |
|---------|:---:|:---:|---------|---------|---------|:---:|
| **S** (当前) | ≤500 | 8 | ~2GB（8 进程 × 256MB） | 8 线程 / 20 可用 = 40% | 低 | ✅ 轻松 |
| **M** (过渡) | 500~2,000 | 24 | ~6GB（24 进程 × 256MB） | 24 线程 / 20 可用 = 超线程调度 | 中 | ✅ 可以（需增量扫描默认） |
| **L** (目标) | 2,000~10,000 | 40~100 | ~25GB（100 进程 × 256MB） | 100 线程 / 20 可用 = 5x 超额订阅 | 高 | ⚠️ 增量模式可以，全量需分布式 |
| **XL** (远期) | >10,000 | >100 | >25GB | >5x 超额订阅 | 极高 | ❌ 需多机集群 |

**关键推算**：

| 场景 | 执行脚本数 | 并发数 | 预估耗时 | 开发机可行性 |
|------|:---:|:---:|:---:|:---:|
| 增量扫描（日常，改 3 个文件） | 15~30 | 8~24 | <1 分钟 | ✅ |
| 单维度扫描（CI 门禁） | ~833 | 24 | ~17 分钟 | ✅ |
| 全量扫描（周检，10K 脚本） | 10,000 | 24 | ~3.5 小时 | ⚠️ 可跑但慢，建议增量模式 |
| 100 AI Worker 并发增量扫描 | 100×15=1,500 | 100（需分布式） | 取决于调度 | ⚠️ 单机内存够（64GB），但 CPU 线程超额需分布式调度 |

**结论**：开发机（64GB / 20 线程 / NVMe）可支撑 **M 级（2,000 脚本 / 24 并发）** 全量运行；**L 级（10,000 脚本 / 100 并发）** 在增量扫描模式下可行，全量扫描需分布式执行（§35）。内存 64GB 是充足裕度——100 并发 × 256MB = 25GB，仅占 39%。瓶颈在 CPU 线程数（20 线程调度 100 并发进程），需通过 Bulkhead 四池隔离 + 优先级调度来避免 CPU 争抢。

### 8.6 SLA/SLO 度量指标

量化脚本系统的服务水平目标，让"系统是否健康"有数字可查。

| 指标 | 目标值 | 测量方式 | 当前基线 |
|------|:---:|---------|:---:|
| **系统可用性** | ≥ 99% | `run_all.py` 全维度成功率 | 待测量 |
| **MTTR（平均修复时间）** | CRITICAL ≤ 24h / HIGH ≤ 168h | Finding 创建→关闭时间差 | 待测量 |
| **扫描覆盖率** | 100% 文件被至少一个维度覆盖 | 被扫描文件数 / 项目总文件数 | 待测量 |
| **假阳性率** | ≤ 5% | 人工确认后标记为 FALSE_POSITIVE 的 Finding 占比 | 待测量 |
| **门禁阻断率** | ≤ 2%（正常提交被误阻断） | pre-commit 被阻断后人工判定为误杀的占比 | 待测量 |
| **脚本健康度** | 100% 脚本可正常运行（exit ≤ 1） | `run_all.py` 全维度 warn-only 通过率 | 待测量 |

---

## 10. 施工 Phase 规划 (§16 施工指引)

### 最小闭环 MVP ✅ 已完成

```
D1-D5  现有脚本输出统一化为 Finding Schema 格式
       → scripts/governance/run_all.py 已可用
       → 全部脚本已注册（script-manifest.yaml）
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
| 里程碑门禁点——设计审查/发布前/归档前自动化检查 | P2 | 📋 Backlog |

---

## §17 容量升级

### 17.1 容量基线

| 资源 | 当前基线 | 测量方式 |
|------|---------|---------|
| 模块数 | 51 | module_id_registry.yaml |
| 治理脚本数 | 366 | script-manifest.yaml total_scripts |
| AI 并发 Session | 1 | session 日志 |
| 单次全量扫描耗时 | ~50s | run_all.py 计时 |
| 并发执行线程数 | 6-24 | ThreadPoolExecutor max_workers |

### 17.2 缺口分析

| 缺口ID | 当前瓶颈 | 升级方案 | 触发阈值 |
|--------|---------|---------|---------|
| GAP-001 | 全量扫描默认，增量扫描缺失 | ScriptImpactMap + 增量扫描模式 | 脚本数 > 500 |
| GAP-002 | 无脚本结果缓存 | ScriptResultCache | 脚本数 > 500 |
| GAP-003 | 无跨 Session 去重 | CrossSessionDeduplicator | AI 并发 > 10 |
| GAP-004 | Manifest 单文件全量加载 | 分层索引 | 脚本数 > 1000 |
| GAP-005 | 全局硬超时 600s | 扫描模式感知超时 | 脚本数 > 500 |

### 17.3 升级版本矩阵

| 版本 | generation | 升级类型 | 核心变更 | 代码覆盖 |
|------|:---:|---------|---------|:---:|
| v5.4.0 | 1 | 基线 | 五阶段流水线 + 12维度审计 + pre-commit 门禁 | ✅ |
| v6.0.0 | 2 | 容量升级 | ScriptImpactMap + ScriptResultCache + CrossSessionDeduplicator + 增量扫描默认 | ⚠️ |

### 缺口清单

| 缺口ID | 缺口描述 | 优先级 | 目标版本 | 状态 |
|--------|---------|:---:|---------|:---:|
| GAP-001 | 增量扫描核心能力缺失 | P0 | v6.0.0 | 待施工 |
| GAP-002 | 脚本结果缓存缺失 | P0 | v6.0.0 | 待施工 |
| GAP-003 | 跨 Session 去重缺失 | P1 | v6.0.0 | 待施工 |
| GAP-004 | Manifest 分层索引缺失 | P1 | v6.0.0 | 待施工 |
| GAP-005 | 超时策略需按规模重定义 | P2 | v6.0.0 | 待施工 |

### 升级组件清单

| 组件名 | 对应缺口 | 代码文件 | 施工Phase | 状态 |
|--------|---------|---------|----------|:---:|
| ScriptImpactMap | GAP-001 | script_impact_map.py | Phase 1 | 待施工 |
| ScriptResultCache | GAP-002 | script_result_cache.py | Phase 1 | 待施工 |
| CrossSessionDeduplicator | GAP-003 | cross_session_dedup.py | Phase 2 | 待施工 |
| ManifestIndex | GAP-004 | manifest_index.py | Phase 2 | 待施工 |

---

## §10 依赖关系

### 10.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| MOD-INF-001 (capacity_assurance) | runtime | 容量预算检查 + SLO 监控 + Error Budget + Kill Switch | 2.0.0 | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\capacity_assurance\blueprint.md` |
| MOD-INF-003 (task-card-kms) | runtime | Finding → CRITICAL 自动创建任务卡 | 1.0.0 | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\task-card-kms\blueprint.md` |
| MOD-INF-004 (vibe-coding-pipelines) | contract | 脚本系统是双管线审计侧的脚本基础设施 | 1.0.0 | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\vibe-coding-pipelines\blueprint.md` |
| **MOD-TASK_SYSTEM (task_system)** | **contract** | **G0-G7门禁体系 + M1-M11管线节点** | **0.3.0** | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\task_system\blueprint.md` |
| PS-STD-012 (规则验证标准) | contract | V1~V4 验证分级 + 阻断/警告规则定义 | 1.1.0 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_041_meta_rule_classification.yaml` |
| PS-STD-001 (元数据注册表) | contract | frontmatter schema + META-V 验证规则 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_043_meta_rule_metadata.yaml` |
| SCRIPT-QUALITY-001 | contract | 脚本质量 8 维度 × 38 条款 | 1.0.0 | `D:\ZephyrAlpha\scripts\governance\quality-standard.md` |

### 10.2 依赖图对齐声明

> 蓝图 §10.1 声明的依赖 MUST 与全局依赖图一致。不一致 = 漂移。
> 全局依赖图 SSoT：[dependency_path_panorama.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/04_architecture_principles_decisions/dependency_path_panorama.md)
> 机器 SSoT：[cross-module-dependency-registry.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/cross-module-dependency-registry.yaml)

| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §10.1 依赖声明 ↔ cross-module-dependency-registry.yaml | 蓝图声明的每个依赖在 registry 中有对应条目 | 已对齐 | `python scripts/governance/d5_architecture/validators/validate_path_alignment.py --blueprint MOD-INF-005` |
| 2 | §11 产出物路径 ↔ 依赖图 §19 path_mappings | 路径一致 | 已对齐 | 同上 |
| 3 | §0 代码文件清单 ↔ 依赖图节点 code_path | 节点存在 | 已对齐 | `python scripts/governance/d5_architecture/validators/validate_dependency_graph_template.py` |

### 10.3 内部依赖图

> 全局依赖图只覆盖模块级，不覆盖脚本级。本节补充蓝图内部脚本/模块间的执行顺序和数据流依赖。

#### 执行顺序依赖

| 上游脚本 | 下游脚本 | 依赖内容 | 验证方式 |
|---------|---------|---------|---------|
| D1 维度脚本 | D3/D5/D8 维度脚本 | D1 结构完整性是 D3→D5→D8 的前置依赖 | D1 exit=0 后 D3 才能正确解析 |
| D2 维度脚本 | D4/D11/D9/D12 维度脚本 | D2 链接完整性是 D4→D11 的前置依赖 | D2 exit=0 后 D4 才能正确追踪 |
| D6 维度脚本 | D7 维度脚本 | D6 安全扫描结果影响 D7 代码质量判定 | D6 完成后 D7 才能做完整分析 |
| run_all.py | 所有维度脚本 | manifest 可读 + 调度编排 | `run_all.py --list` exit=0 |
| generate_script_manifest.py | run_all.py | manifest 生成是 run_all 调度的前提 | manifest 文件存在且非空 |

#### 数据流依赖

| 生产者 | 消费者 | 数据类型 | 传输方式 |
|--------|--------|---------|---------|
| 各维度脚本 | C2 分类阶段 | Finding JSONL | 文件写入 |
| C2 分类 | C3 报告 | Finding dict（去重后） | 函数调用 |
| C3 报告 | pre-commit / 人工 | exit code + report | 进程退出码 + stdout |
| C4 跟踪 | MOD-TASK_SYSTEM 任务系统 | TaskCard | 函数调用 |
| run_all.py | ScriptResultCache | 缓存条目 | SQLite |
| run_all.py | CrossSessionDeduplicator | 执行注册 | SQLite |

### 10.4 自动化规格

#### 是否需要自动化

| # | 自动化项 | 是否需要 | 理由 |
|---|---------|:-------:|------|
| 1 | 依赖图自动生成 | 是 | 脚本数>10，手动维护不可靠 |
| 2 | 依赖对齐自动验证 | 是 | 有外部依赖，需持续对齐 |
| 3 | 临时时态内容自动清理 | 否 | 当前无迁移方案 |
| 4 | 施工步骤完成度自动检测 | 否 | construction_progress=completed |

#### 如何自动化

| # | 自动化项 | 实现方式 | 现有工具/脚本 | 缺口 |
|---|---------|---------|-------------|------|
| 1 | 依赖图自动生成 | AST解析import + manifest字段 | generate_script_manifest.py | 不覆盖 scripts/ 间依赖 |
| 2 | 依赖对齐自动验证 | CI门禁 | validate_path_alignment.py | 无 |

#### 触发方式

| # | 自动化项 | 触发方式 | 触发条件 |
|---|---------|---------|---------|
| 1 | 依赖图自动生成 | CI pipeline | 文件变更时 |
| 2 | 依赖对齐自动验证 | CI门禁 | PR提交时 |

---

## 12. 风险与后果

### 12.1 风险矩阵

> 本节同时覆盖原 §15 后果——负面后果合并到本表"类型"列。正面后果与 §1 目标重复，不在此记录。

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|:---:|:---:|---------|------|
| R1 | **审计疲劳**——扫描 Finding 过多，CRITICAL 被淹没 | 高 | 高 | 严格执行严重度分级；CRITICAL 24h 内处理 | 风险 |
| R2 | **沉默失败**——脚本异常退出但 CI 显示绿色 | 中 | **极高** | 退出码严格约定（0/1/2/3），exit 3 = 阻断 | 风险 |
| R3 | **审计的审计**——审计脚本本身有 bug | 中 | 高 | 审计脚本必须通过自身的三件套入库验证 | 风险 |
| R4 | **AI 自我修改**——AI 改审计规则掩盖问题 | 低 | **极高** | Finding Schema + 严重度分级 → Immutable 层，AI 只能读取 | 风险 |
| R5 | **单人项目瓶颈**——审计独立性无法保障 | 高 | 中 | 不同 AI 模型交叉验证（Claude审GLM修复、Opus审Claude修复） | 风险 |
| R6 | **过度工程**——12维度×5阶段×3轴 = 180种组合 | 中 | 低 | 分阶段 rollout——先 P0 维度跑通，按反馈决定 beta | 风险 |
| R7 | **增量扫描漏检**——ImpactMap 自动推导不完整 | 中 | 高 | 三层推导（声明>模块归属>自动推导）+ 全量周检兜底 | 风险 |
| R8 | **缓存脏读**——ScriptResultCache 返回过期 result | 低 | 高 | 缓存键含 impacted_files_hash + TTL 硬过期兜底 | 风险 |
| R9 | **去重器死锁**——CrossSessionDeduplicator 极端并发活锁 | 低 | 高 | SQLite INSERT OR REPLACE 原子操作 + 300s 超时自动接管 | 风险 |
| R10 | **单机 CPU 过载**——100 session 增量扫描 CPU 接近极限 | 中 | 中 | 缓存+去重器降低执行量（命中率>85%）+ capacity_params 动态缩 pool + Kill Switch | 风险 |
| NC1 | **维护负担**——Finding Schema 变更 → 全部脚本输出逻辑同步更新 | 高 | 高 | Schema 变更需 Owner 审批 + 通知所有脚本维护者 | 负面后果 |
| NC2 | **假阳性噪声**——自动化扫描可能产大量 LOW/INFO | 中 | 中 | 需持续调优阈值；Shadow Mode 渐进激活 | 负面后果 |
| NC3 | **学习成本**——Owner 需理解 Finding Schema 字段含义 | 中 | 低 | quickstart.md + human-memory-card.md | 负面后果 |

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
| **B13** | **缺少里程碑门禁** | pre-commit 只覆盖提交时刻——设计审查、发布前、归档前都没有自动化检查点 | beta 新增里程碑门禁矩阵 |

> B1（审计自身的审计）= 风险 R3 | B2（审计疲劳）= 风险 R1 | B3（修复验证独立性）= §6.1 | B10（沉默失败）= 风险 R2 — 已在主风险矩阵中覆盖。

### 12.5 设计决策记录

> 本节同时覆盖原 §7 备选方案——"选项"列已包含备选方案信息。
> **时态属性**：决策记录属于**永久时态**——AI 修改设计时必读。

| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | DD-SCRIPT-001 | ImpactMap 映射来源优先级 | A:声明>B:模块归属>C:自动推导 | A>B>C | 声明精确但维护成本高；自动推导无维护成本但冷启动无数据；三层分工保证零漏检 | 2026-05-03 |
| 2 | DD-SCRIPT-002 | ScriptResultCache 存储 | A:SQLite / B:Redis / C:Memcached | A | 单机部署无需独立缓存服务；SQLite 读延迟<1ms；持久化不丢缓存；50K条目<50MB | 2026-05-03 |
| 3 | DD-SCRIPT-003 | 全量扫描保留策略 | A:保留降级手动 / B:完全移除 | A | 增量扫描依赖三层组件可能漏检；全量扫描是终极兜底；保留但不默认 | 2026-05-03 |
| 4 | DD-SCRIPT-004 | Manifest 分层方式 | A:生成物分层 / B:源数据分层 | A | script-manifest.yaml 仍是全量 SSoT；per-dimension manifest 自动派生；不改 AI 注册流程 | 2026-05-03 |
| 5 | DD-SCRIPT-005 | CI 执行环境 | A:本地Python脚本 / B:GitHub Actions云端 | A | 项目在本地；无需网络；零成本 | 2026-05-03 |
| 6 | DD-SCRIPT-006 | 规则表达方式 | A:Python脚本 / B:自定义DSL规则引擎 | A | Python 脚本已足够表达力；无学习成本；无额外维护负担 | 2026-05-03 |
| 7 | DD-SCRIPT-007 | 缓存后端 | A:SQLite / B:Redis | A | 单机场景 SQLite 足够；不引入外部依赖 | 2026-05-03 |
| 8 | DD-SCRIPT-008 | 并行模型 | A:ThreadPoolExecutor / B:多进程 | A | 脚本系统为 I/O 密集型；GIL 对 I/O 无影响；线程开销更小 | 2026-05-03 |

---

## 13. 脚本系统运维与自我监控

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


### 13.3 版本升级与兼容性

脚本系统自身的升级遵循以下原则：

- **向后兼容优先**：新版本 `run_all.py` 必须能运行旧版本脚本（通过 §4.5 Plugin Contract 保证）
- **弃用公示期**：废弃一个脚本参数或输出格式时，至少保留一个 Phase（约 1-2 周）过渡期
- **回滚计划**：每次 `run_all.py` 重大升级必须有 `git revert` 回滚路径

### 13.4 定期应急演练

| 演练类型 | 内容 | 频率 |
|---------|------|:---:|
| 脚本故障演练 | 人为破坏一个脚本，验证 Meta 维度能否检测到并报告 | 每月 |
| 紧急绕过演练 | 模拟脚本系统全部故障，走一遍 `--no-verify` 流程 | 每季度 |
| 恢复演练 | 从 `git revert` 恢复脚本系统到上一个健康版本 | 每季度 |

---

## ⚠️ Vibe Coding 蓝图编写铁律

> 以下铁律来自实战经验。违反任何一条都可能导致后续 AI 施工时出现幻觉、路径漂移、执行失败。
> **时态属性**：本节属于**施工声明**——AI 进入蓝图修改/施工时必读。不可改为链接引用。永久保留在蓝图中。

| # | 铁律 | 违反后果 |
|---|------|---------|
| 1 | **所有路径必须是绝对路径**（含盘符 `D:\`） | 文件创建到错误位置 |
| 2 | **必备链接不可省略**——即使与前序文档重复也必须完整列出 | AI 跳过不读，施工时缺少关键信息 |
| 3 | **蓝图必须是最终设计结果**——不记录决策过程、不保存未选方案 | 蓝图过厚，关键信息被噪音淹没 |
| 4 | **产出物路径必须与 GOV-DOC-002 一致** | 路径幻觉——文件放错位置 |
| 5 | **涉及文件范围必须明确列出** | 范围漂移——改了不该改的文件 |
| 6 | **容量估算必须写** | 容量瓶颈——上线后发现不够用 |
| 7 | **迁移/废弃方案必须写** | 断链——旧引用找不到文件；或垃圾积累 |
| 8 | **"待定"/"建议"/"按需"等模糊词禁止使用** | 执行漂移——AI 自行决定，可能选错 |
| 9 | **蓝图必须自包含**——关键信息不能只写"详见XX" | 信息缺失——AI 缺少关键上下文 |
| 10 | **删除文件必须遵守安全删除协议** | 永久丢失——无法恢复 |
| 11 | **construction_progress 必须与代码实际状态一致** | 重复造轮子或跳过施工 |
| 12 | **actual_disk_path 必须与 §11 产出物路径一致** | 搜索失败、导入错误 |
| 13 | **已实现代码不在蓝图中重复**——§0.1 标记`已实现`的模块，蓝图只保留接口签名（§4），不复制实现代码 | AI 改蓝图忘改代码，或改代码忘改蓝图 |
| 14 | **临时时态内容执行完毕后从蓝图删除**——迁移方案、升级执行计划等临时时态内容，一旦执行完毕即成为历史，从蓝图删除 | 蓝图膨胀，关键信息被历史噪音淹没 |
| 15 | **蓝图内容拆分判定**——职责不同→拆分独立蓝图；职责相同→原地升级。判定标准见"蓝图拆分判定标准" | AI 不知道该读哪个蓝图，跨模块影响无法追踪 |

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
      a) 有独立的 module_id 前缀
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

### 本蓝图拆分判定

本蓝图当前 ~2400 行，超过 ~800 行阈值。判定：

| 内容区块 | 行数 | 职责域 | 判定 | 理由 |
|---------|:---:|--------|------|------|
| §1-§9 核心设计 | ~800 | 脚本系统治理基础设施 | 原地保留 | 核心职责 |
| §10-§13 依赖/运维 | ~300 | 脚本系统运维 | 原地保留 | 服务对象相同 |
| §14-§25 已施工功能 | ~500 | 脚本系统纵深能力 | 原地保留 | 服务对象相同+依赖重叠 |
| §27-§28 盲点+行动项 | ~200 | 脚本系统演进 | 原地保留 | 服务对象相同 |
| §31-§34 取证/灾备/陷阱 | ~300 | 脚本系统安全纵深 | 原地保留 | 服务对象相同 |
| §35-§36 分布式架构 | ~300 | 脚本系统容量升级 | 原地保留 | §17 容量升级附录覆盖 |

**结论**：所有内容服务对象相同（脚本系统）、变更频率同步、依赖关系重叠 → **原地升级**，不拆分。超长原因是模块本身复杂度高（12维度×5阶段×90盲点），非职责混杂。

---

## 治理信息

### SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| 脚本系统的架构决策（12维度+5阶段） | **本文档 §3-§6** | 候选池设计文档 |
| Finding Schema 字段定义 | **本文档 §4.3（旧版蓝图）** | — |
| 实施阶段与优先级 | **本文档 §10** | 候选池设计文档 |
| 脚本模块与 manifest 关联 | **script-manifest.yaml** | — |

**任何与本蓝图冲突的定义，以本蓝图为准。**

### 消费者注册

| Tier | 消费者 | 依赖内容 |
|:----:|--------|---------|
| Tier 1 | 施工图 | 本蓝图所有决策 |
| Tier 2 | MOD-TASK_SYSTEM（task_system） | §6 集成接口——脚本失败↔任务状态 |
| Tier 3 | scripts/governance/*.py（全部脚本） | §3 分类体系 + §5 调度规范 + §7 质量标准 |

### 修改条件

| 变更类型 | 审批要求 |
|---------|---------|
| 决策新增/修改 | Owner 审批 |
| Finding Schema 字段修改 | Owner 审批 + 通知所有脚本维护者 |
| 非关键补充（风险缓解/Phase更新） | AI 可自主 |

### 漂移防护

| 修改本蓝图 | MUST 同步更新 |
|-----------|-------------|
| §4 接口契约变更 | script-manifest.yaml + 下游消费者 |
| §3 维度分类变更 | script-manifest.yaml + run_all.py |
| Finding Schema 字段变更 | finding.py + 所有输出 Finding 的脚本 |
| §5 调度规范变更 | run_all.py + pre-commit-config.yaml |
| §0 代码文件清单 | 代码文件 `[BLUEPRINT]` 字段 |
| frontmatter version | blueprint_registry.yaml |

### 负向责任

本蓝图**不涉及**以下领域：

| 领域 | 真源 |
|------|------|
| 任务卡字段定义 | MOD-TASK_SYSTEM（task_system blueprint） |
| 管线编排 | MOD-INF-004（vibe-coding-pipelines） |
| 门禁引擎 | MOD-GATE_ENGINE（gate_engine blueprint） |
| 代码命名/类型注解 | [code-construction-standards.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md) |
| 脚本质量 8 维度完整条款 | [quality-standard.md](file:///d:/ZephyrAlpha/scripts/governance/quality-standard.md) |

### 触发条件

| 关键词/场景 | 触发动作 |
|------------|---------|
| 脚本 / run_all / manifest / 治理脚本 | 加载本蓝图 |
| 新建 .py 文件需入库 | 读取 §4 三件套入库流程 |
| pre-commit 门禁配置 | 读取 §5 调度规范 |
| Finding / 审计发现 | 读取 §20 Finding 状态机 |

### 导航路径

```
registry_of_registries.yaml → blueprint_registry.yaml → MOD-INF-005 → 本蓝图
scripts/governance/quickstart.md → §22 Zero-Memory 冷启动卡片
```

---

## 14. 已实现代码完整路径索引

> **AGENTS.md §6.14 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> 脚本系统——第三条生产线，scaffold MVP已交付

### 14.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/infrastructure/script_system/finding.py` | ✅ 已实现 | |

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
| `scripts/governance/d5_architecture/validate_layer_deps.py` | ❌ 已删除（2026-07-09死代码清理） | |
| `scripts/governance/d5_architecture/validate_field_ownership.py` | ✅ 已实现 | |
| `scripts/governance/d5_architecture/validate_directory_structure.py` | ✅ 已实现 | |
| `scripts/governance/d5_architecture/validate_interface_contracts.py` | ✅ 已实现 | |
| `scripts/governance/d5_architecture/validate_module_lifecycle.py` | ✅ 已实现 | |
| `scripts/governance/d5_architecture/validate_p0_module_contracts.py` | ✅ 已实现 | |
| `scripts/governance/d5_architecture/validate_arch_review_gate.py` | ✅ 已实现 | |
| `scripts/governance/d5_architecture/validate_yaml_summaries.py` | ✅ 已实现 | |
| `scripts/governance/d5_architecture/validate_three_way_consistency.py` | ✅ 已实现 | |
| `scripts/governance/d5_architecture/validate_code_yaml_alignment.py` | ✅ 已实现 | |
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
| `scripts/governance/d5_architecture/classify_cross_package_imports.py` | ✅ 已实现 | DW-261 跨包引用分类引擎 |
| `scripts/governance/d5_architecture/refactor_god_init_lazy.py` | ✅ 已实现 | DW-241~250 God模块懒加载重构 |
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
| `scripts/governance/meta/kill-switch-state.yaml` | ✅ 已实现 | Kill Switch 状态注册 (§16) |
| `scripts/governance/meta/shadow-mode-state.yaml` | ✅ 已实现 | Shadow Mode 状态注册 (§17) |
| `scripts/governance/meta/error-budget-state.yaml` | ✅ 已实现 | Error Budget 状态注册 (§21) |
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
| `scripts/governance/quickstart.md` | ✅ 已实现 | AI Session Zero-Memory 冷启动卡片 (§22) |

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

> **B16（关键阈值外置+变更审计）**

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
- 阈值文件纳入 D11 合规审计（§12.4 B9）

---

## 16. Kill Switch 机制

> **B25（Kill Switch）**

### 16.1 双层保护

| 层级 | 范围 | 触发方式 | 效果 |
|------|------|---------|------|
| **全局冻结** (global_freeze) | 所有新脚本开发 | Error Budget 耗尽自动触发 / Owner 手动 | 只允许修复现有脚本——禁止新脚本入库 |
| **单脚本禁用** (per-script) | 单个脚本 | Owner 手动 `--disable` / 连续失败 N 次自动 | 该脚本停止运行——不影响其他脚本 |

### 16.2 执行机制

`run_all.py` 启动时读取 `meta/kill-switch-state.yaml` → 每个脚本运行前检查：
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

> **B19（Shadow Mode）**

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

> **B18（Baseline Snapshot）**

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

### 18.3 管理工具

```bash
python scripts/governance/meta/manage_baseline.py --save findings.jsonl
python scripts/governance/meta/manage_baseline.py --compare findings.jsonl --json
python scripts/governance/meta/manage_baseline.py --approve findings.jsonl
```

---

## 19. False Negative 检测引擎

> **B17（False Negative 检测）**

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

> **B20（Finding 全生命周期）**

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

每次状态变更 → append-only audit log → `finding-state-db.json`。

### 20.4 管理工具

```bash
python scripts/governance/meta/finding_state_machine.py --load findings.jsonl
python scripts/governance/meta/finding_state_machine.py --transition <id> --to IN_PROGRESS
python scripts/governance/meta/finding_state_machine.py --check-sla
python scripts/governance/meta/finding_state_machine.py --list OVERDUE
```

---

## 21. Error Budget + Burn Rate + 依赖隔离

> **B14（Error Budget + Burn Rate）+ B21（脚本依赖隔离）**

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
1. 设置 `error-budget-state.yaml → feature_freeze.active = true`
2. 同步设置 `kill-switch-state.yaml → global_freeze = true`
3. 72 小时后自动解冻

### 21.4 脚本依赖隔离

- 各维度分池：**轻量级**（D1-D4，标准库为主）/ **中量级**（D5-D8,D11）/ **重量级**（D9,D10,D12，含 AI/LLM依赖）
- 重量池脚本即使崩溃也不影响轻量池脚本的运行
- 各维度可声明专属 `requirements-{dimension}.txt`——位于 `meta/requirements/`
- 环境健康检查：`validate_environment_health.py`

---

## 22. AI Session Zero-Memory Quickstart Card

> **B15（Zero-Memory Quickstart）**

### 22.1 卡片位置

`scripts/governance/quickstart.md`

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
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\governance-automation\blueprint.md` | 本文件 |
| 业务代码 | `D:\ZephyrAlpha\src\zephyr\infrastructure\script_system\` | 脚本系统核心 |
| 治理脚本 | `D:\ZephyrAlpha\scripts\governance\` | 80+ 治理脚本 |
| 脚本注册表 | `D:\ZephyrAlpha\scripts\governance\script-manifest.yaml` | 脚本登记 SSoT（REG-SCRIPT-001 主清单 + REG-SCRIPT-002 Governance 子集） |

---

## 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| Gate Engine (MOD-GATE_ENGINE) | 治理脚本结果 → 门禁判定 | `run_all.py` → `gate_engine.evaluate()` | 脚本结果触发门禁 |
| Task System (MOD-TASK_SYSTEM) | 脚本执行 → 任务状态变更 | 脚本完成 → `task_repo.update_status()` | 关联任务状态自动更新 |
| Drift Detector (MOD-INF-023) | 治理脚本 → 漂移检测器 | 80+ 脚本 → `drift_detector` 调度 | 脚本作为 drift detector 的检测器 |

---

## 需要更新的相关内容

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | 版本号+完整度 | 蓝图补全后更新 |
| 2 | script-manifest.yaml | `D:\ZephyrAlpha\scripts\governance\script-manifest.yaml` | 新脚本注册 | 新治理脚本入库后更新 |

---

---

---

## §16 Kill Switch 机制

> **已施工 B25**。双层保护：全局冻结 + per-script 禁用。`manage_kill_switch.py` + `kill-switch-state.yaml`。联动 Error Budget Feature Freeze。

## §17 Shadow Mode 渐进激活

> **已施工 B19**。Phase1(Shadow)→Phase2(Warn)→Phase3(Active)。`manage_shadow_mode.py` + `shadow-mode-state.yaml`。假阳性 > 20% → 自动回退。

## §18 Baseline Snapshot

> **已施工 B18**。三态分类 NEW/RESOLVED/PERSISTENT。`manage_baseline.py`。PERSISTENT ≥ 30d → 升级严重度。

## §19 False Negative 检测

> **已施工 B17**。Golden Test Case + Fitness Functions。`validate_false_negatives.py`。已知坏用例检测率 ≥ 90%。

## §20 Finding 全生命周期状态机

> **已施工 B20**。10状态 + SLA定时器 + 状态转换审计。`finding_state_machine.py`。超时 → 自动升级 OVERDUE。

## §21 Error Budget + Burn Rate

> **已施工 B14+B21**。双预算模型 + Critical/Warning Alert + Feature Freeze ← Kill Switch联动。`manage_error_budget.py` + `error-budget-state.yaml`。Burn Rate加速度(B55)。

## §22 Zero-Memory Quickstart Card

> **已施工 B15**。`quickstart.md` — ≤500 tokens AI冷启动。

## §23 Rules File 供应链安全

> **已施工 B43+B44**。Unicode Backdoor 扫描 + SHA256完整性校验。`validate_rules_file_backdoor.py` + `validate_rules_integrity.py`。纳入 pre-commit 硬阻断（CRITICAL发现=exit 2）。

## §24 七大安全与质量引擎

> **已施工 B45-B51**。Script A/B对照(Kayenta) + Trust-Tier T1/T2/T3 + Provenance链 + Slopsquatting幻觉包防御 + Finding仲裁器(5规则) + 时序数据库(SQLite) + Script Rot检测。

## §25 八大精英补全

> **已施工 B52-B59**。退役流程 + 多模型共识(Claude/GLM/Opus) + 费用追踪 + Burn Rate加速度 + C1→C5全链路Tracing + 合规框架映射(OWASP/ISO27001/SOC2/ITIL5) + 人类记忆卡(human-memory-card.md) + E2E基准测试。

## §26 风险更新

| 风险ID | 风险 | 对策 |
|--------|------|------|
| R6 | Rules File Backdoor | validate_rules_file_backdoor.py + validate_rules_integrity.py |
| R7 | Excessive Agency | trust-tier-policy.yaml + validate_trust_tier.py |
| R8 | Slopsquatting | detect_hallucinated_packages.py PyPI验证 |
| R9 | Script静默失效 | detect_script_rot.py 每扫描周期 |
| R10 | Finding矛盾 | arbitrate_findings.py 5规则 |
| R11 | 系统退化 | validate_end_to_end_benchmark.py |
| R12 | Token费用失控 | track_script_costs.py per-call tracking |

---

## 27. 第四层盲点清单：AI会话与1人维护专域 (B60-B91)

### 27.1 AI 会话上下文管理 (B60-B62)

| # | 盲点 | 为什么重要 | 缓解策略 |
|---|------|-----------|---------|
| **B60** | **AI 上下文窗口污染** | 系统每次增长，AI session 注入的蓝图/脚本/finding 越来越多，最终超过 token 预算 → AI 开始"遗忘"关键约束。当前蓝图 1400 行 + quality-standard 540 行 + manifest 1230 行 = 远超单次注入能力 | 建立「AI 消费优先级」：Tier-1 必注入（quickstart.md ≤500tokens）→ Tier-2 按需注入（脚本管脚本、蓝图管蓝图）→ Tier-3 禁止注入（完整 manifest 不允许一次全吞）。§22 quickstart.md 已经做了 Tier-1 |
| **B61** | **AI 会话中断-续接漂移** | AI session 在修复脚本中途断开（token 耗尽/网络/IDE 崩溃），新 session 启动后不知道前一个 session 做了什么 → 重复劳动、半成品修复、状态不一致 | 为每个治理脚本增设 `meta/script_fix_state.yaml`——记录「谁在修、修到哪了、下一步是什么」（WAL 断点续传） |
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
| **B66** | **维护者缺席协议** | 唯一的 Owner 生病/出差/离职 3 个月 → 系统无人看管。Kill Switch 自动解冻、Error Budget 自动重置——但这些自动化在 Owner 不在时可能做出错误决策 | 新增「维护者缺席模式」：Owner 主动设置 `maintainer_absent_until: 2026-09-01` → 自动冻结（禁止所有自动决策）、自动降级（所有阻断→警告）、自动记录（所有 Finding 排队等待 Owner 回来批量审批）.
| **B67** | **AI 模型迁移风险** | 项目用 Claude 4 建、用 Claude 4.5 维护——但 2026 年底 Owner 可能切换到 GLM-5 / DeepSeek V5 / GPT-5。不同 AI 模型对同样的 AGENTS.md 理解不同、行为不同 | 建立 `meta/model-compatibility-matrix.yaml`——记录每个脚本在哪些模型上测试过、行为差异。`validate_cross_model_consensus.py`（B53 已施工）可扩展为定期多模型回归测试 |
| **B68** | **人类知识巴士系数** | 1 个人的脑子里装着所有隐式设计决策（"为什么 D5 有 45 个脚本但 D2 只有 2 个"、"为什么不直接用 ruff 替代 D7 全部脚本"）。这些决策理由没有文档化 | 在 `human-memory-card.md` 中补充「设计决策日志」——每个反直觉决策一句话解释。在蓝图 §3.1 的各维度描述中补充「为什么这个维度脚本多/少」的脚注.
| **B69** | **脚本对特定 AI 行为的隐式依赖** | 有些脚本可能无意中依赖 Claude 特有的输出格式/推理风格——当 Owner 换模型时脚本行为异常 | 所有涉及 LLM 调用的脚本（D9/D12）必须在 `__manifest__` 中声明 `ai_model_dependency: none \| claude \| multi`。`validate_cross_model_consensus.py` 在模型切换时自动全量回归 |

### 27.4 性能与规模递增 (B70-B72)

| # | 盲点 | 为什么重要 | 缓解策略 |
|---|------|-----------|---------|
| **B70** | **Pre-commit 延迟膨胀** | 当前 5 个核心钩子 ~50s——但随着脚本增长，pre-commit 耗时可能膨胀到 5 分钟以上，严重破坏开发体验。Vibe Coding 的核心优势是「快速迭代」，慢门禁会杀死这个优势 | 引入「Pre-commit 时延 SLA」——钩子总耗时 ≤ 60s。超过时自动：1) 快速脚本先跑（D1/D2/D3 < 5s）→ 2) 慢脚本异步化（D5/D7/D11 后台跑）→ 3) AI 重型脚本降级（D9/D12 仅 weekly）.
| **B71** | **文件重复解析浪费** | 多条治理脚本各自独立 `open() + parse` 同一文件——一个 500 行的 YAML 可被解析与注册脚本数量同阶的次数。在 1 人项目里这还不痛，但资源浪费是真实的 | `run_all.py` 引入「扫描缓存层」——同一轮扫描中，文件内容 `lru_cache` 到内存。跨脚本共享文件读取结果.
| **B72** | **增量扫描不够智能** | `run_incremental.py` 已存在，但只是简单的 `--diff-ref` 代理。当 Owner 修改了一个 `_shared/thresholds.yaml`，它不知道该跑所有引用该阈值的脚本（因为 `depends_on_scripts` 字段尚未存在） | 引入 B65 的 `depends_on_scripts` → 增量扫描时构建「变更影响图」→ 精确计算最小需要重跑的脚本集合.

### 27.5 脚本质量与测试深度 (B73-B75)

| # | 盲点 | 为什么重要 | 缓解策略 |
|---|------|-----------|---------|
| **B73** | **Golden Test Case 覆盖缺口** | B17 False Negative 检测引擎已设计但 `test_fixtures/` 目录**尚未创建**。这意味着假阴性检测引擎的「Golden Test Case 库」处于声明-未实现状态 | 优先级提升：Golden Test Case 库的创建从 P2 → P1。首期至少为 D1/D3/D5/D6 四个高密度维度各创建 3 个 known-bad 用例。施工依据：本蓝图 §19 |
| **B74** | **跨维度集成测试缺失** | 单脚本有 smoke test（D-H-01），但没有测试验证「D1 报告的结构问题 → D5 能正确消费 → D8 能正确追踪」这条跨维度链路 | 新增 `tests/integration/test_cross_dimension_pipeline.py`——构造一个「已知多维度有缺陷的测试项目」，全量跑 `run_all.py`，验证输出链路完整.
| **B75** | **脚本变异测试** | 脚本`validate_frontmatter.py` 输出 0 findings → 是因为项目真的没问题，还是因为脚本逻辑坏了（假阴性）？当前没有机制区分 | `meta/validate_false_negatives.py` 的 Golden Test Case 机制（§19）覆盖了已知坏用例——但还需要「变异测试」：自动注入已知缺陷到健康文件 → 验证脚本能否检测到.

### 27.6 运维韧性深化 (B76-B78)

| # | 盲点 | 为什么重要 | 缓解策略 |
|---|------|-----------|---------|
| **B76** | **分级降级策略** | 当系统资源紧张（内存不足、磁盘满），所有脚本一起崩溃 → 全部门禁失效。没有「先保护最重要的」机制 | `run_all.py` 引入「降级模式」：Level-1（仅 P0 脚本）→ Level-2（P0+P1）→ Level-3（全部）。资源不足时逐级降级，而非全部崩溃.
| **B77** | **扫描断点续传** | `run_all.py` 全量扫描需要 ~50s。如果在 D8 维度（第 8/12）时崩溃，前面 7 个维度的结果丢失 → 必须从头重跑 | `run_all.py` 每完成一个维度 → 写 checkpoint 到 `meta/scan_checkpoint.json`。崩溃后重启 → 从 checkpoint 继续，不重跑已完成维度。30 天内 checkpoint 有效.
| **B78** | **Finding 模式异常检测** | 某天 D2 突然产出 200 条 Finding（平时 5 条）→ 不是脚本坏了，是整个项目的链接体系在一次重构中大规模断裂。当前系统会按严重度逐一报告，但不会说「这是一次系统性断裂，不是 200 个独立问题」 | `meta/trace_finding_lifecycle.py`（B56 已施工）扩展「异常聚类」能力——同一时间窗口内同一维度的 Finding 数量超过历史平均值 3σ → 标记为 `[ANOMALY_CLUSTER]`，报告根因假设而非 200 条独立 Finding |

### 27.7 AI 安全专属 (B79-B80)

| # | 盲点 | 为什么重要 | 缓解策略 |
|---|------|-----------|---------|
| **B79** | **AI 生成脚本的混淆后门** | B43 已覆盖 Unicode Backdoor（零宽字符等）——但 AI 还能生成逻辑层面绕过检测的恶意代码，例如用 `getattr(__builtins__, 'ex' + 'ec')` 替代 `exec()`。正则扫描器检测不到 | `validate_rules_file_backdoor.py`（B43）扩展「语义后门」检测——AST 级别的危险模式识别，不仅仅是字符串正则.
| **B80** | **Finding 描述中的 Prompt Injection** | Finding text 可能含恶意构造的自然语言内容，当 `run_all.py --output` 的输出被 AI 消费时 → 可能触发 AI 执行非预期行为。在 100% AI 施工的语境中，这是一个闭环风险 | Finding Schema 新增 `sanitized_description` 字段——去除 markdown 代码块中的指令性语言、URL、可执行模式。AI 消费 findings 时使用 sanitized 版本 |

### 27.8 生态系统与外部适配 (B81-B82)

| # | 盲点 | 为什么重要 | 缓解策略 |
|---|------|-----------|---------|
| **B81** | **跨 IDE 环境一致性** | 项目在 Trae IDE 开发，但 Owner 可能在 Cursor / Windsurf / VS Code / 纯终端之间切换。不同 IDE 的 Python 解释器路径、环境变量、编码默认值都可能不同 | `validate_environment_health.py`（§21）扩展「IDE 检测」——识别当前运行 IDE 并报告环境差异。`env_check.py` 增加 `--env-report` 输出跨 IDE 兼容性矩阵.
| **B82** | **AI 可消费的健康仪表盘** | 人类看 `status.py` 输出能理解，但 AI 需要结构化的 JSON 来程序化判断系统状态。当前 `status.py` 是面向人类的 CLI 输出 | `status.py` 新增 `--json` 和 `--ai-summary` 参数——输出结构化 JSON，包含「Top 5 风险」「3 个最需要的修复动作」「建议下一个 AI session 做什么」.

### 27.9 演进与废弃管理 (B83-B84)

| # | 盲点 | 为什么重要 | 缓解策略 |
|---|------|-----------|---------|
| **B83** | **脚本-系统版本兼容矩阵** | 蓝图升级后脚本检查逻辑是否仍然有效？没有版本兼容矩阵 → 无法判断 | `script-manifest.yaml` 新增 `compatible_blueprint_version` 字段（min/max 蓝图版本）。`run_all.py` 启动时对比蓝图版本 vs 脚本声明兼容范围 → 不兼容标记 `[VERSION_MISMATCH]` |
| **B84** | **脚本废弃影响预分析** | 退役一个脚本前（B52 的 `manage_script_retirement.py`），需要知道：哪些流程依赖它的输出？哪些 dashboard 引用它的指标？当前退役流程是单向的——只管退役，不管影响 | `manage_script_retirement.py` 增加 `--impact-analysis` 模式——退役前自动扫描：1) manifest 中其他脚本的 `depends_on_scripts` 引用 2) `status.py` 的指标引用 3) 蓝图 §14 的路径索引引用 → 输出受影响清单后才允许退役 |

### 27.10 文档与知识追索 (B85-B86)

| # | 盲点 | 为什么重要 | 缓解策略 |
|---|------|-----------|---------|
| **B85** | **脚本-规则追索矩阵** | 一个 rule（如 PS-STD-012 §2.1 退出码约定）被哪些脚本强制执行？当前是隐式的——需要人/ai 读所有脚本才能建立关联 | `script-manifest.yaml` 新增 `enforces` 字段——每个脚本声明它强制执行哪些规则（如 `PS-STD-012 §2.1`）。`generate_script_manifest.py` 反向生成 `rule-to-scripts` 索引视图 `meta/rule_enforcement_matrix.yaml` |
| **B86** | **Finding 根因自动聚类** | 50 条 D3 维度 frontmatter 违规 → 根因可能是「项目从 V3 升级 V4 时批量迁移遗漏了 frontmatter 更新」。当前 C2 分类器（待施工）提到「根因聚类」但设计未细化 | C2 分类器设计增强：时间窗口聚类 + 文件路径聚类 + Finding 描述相似度聚类 → 输出「根因假设」而不只是 Finding 列表.

### 27.11 Vibe Coding 特有模式 (B87-B89)

> **什么是 Vibe Coding**：Owner 用自然语言描述意图 → AI 生成代码 → Owner 验证 → 提交。迭代极快（分钟级），代码质量依赖 AI 的"氛围理解"而非严格规约先行。

| # | 盲点 | 为什么重要 | 缓解策略 |
|---|------|-----------|---------|
| **B87** | **"我机器上能跑"漂移** | Vibe Coding 中 Owner 和 AI 在同一个 IDE session 协作，脚本在 Owner 的 Trae IDE 中通过 `--warn-only` 验证。但环境变量、Python 路径、已安装的包在自己的机器上是隐式的——换一台机器（或裸 `git clone` 后）脚本失败 | `env_check.py --freeze` 生成完整环境快照（Python 版本 + pip freeze + 环境变量白名单 + PATH）。`validate_environment_health.py` 增加 `--compare-snapshot` 模式——对比当前环境与 frozen snapshot 的差异.
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
| **A2** | **`depends_on_scripts` manifest 字段** —— 在 script-manifest.yaml schema 中新增此字段 → `run_all.py` 可构建脚本影响图 → 支撑增量扫描 (B72) + 接口断裂检测 (B65) + 退役影响分析 (B84) | B65,B72,B84 | 中（schema 变更 + 生成器改造） |
| **A3** | **Pre-commit 时延 SLA + 分层执行** —— 核心钩子 ≤ 60s，慢脚本异步化 | B70 | 小（run_all.py 参数扩展） |

### 28.2 短期行动（P1——下 2 个 Phase 内施工）

| # | 行动项 | 解决盲点 | 施工量 |
|---|--------|---------|:---:|
| **A4** | **AI 上下文窗口污染治理** —— quickstart.md 升级为 Tier-1 必读；manifest/蓝图分级注入策略 | B60,B62 | 小（文档改造 + AGENTS.md 指令增强） |
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
## 30. 蓝图完整性自评矩阵

| 能力轴 | 级别 | 说明 | 到 L5 缺什么 |
|--------|:---:|------|--------------|
| **覆盖广度** | **L5** | 12/12 维度 × manifest 治理脚本 × 跨 3 线横切 | — |
| **自动化深度** | **L4** | Kill Switch / Shadow Mode / Baseline / Error Budget / 退役流程 已施工 | 自适应阈值 (L5) |
| **自我监控** | **L4** | Meta 维度 24 脚本 + 健康自检 + 假阴性检测 | 变异测试 + 跨维度集成测试 (L5) |
| **AI 协作** | **L3** | 蓝图可被 AI 消费 + QUICKSTART + HUMAN_MEMORY_CARD | AI 主动改进建议 + 上下文窗口治理 (L5) |
| **1人维护** | **L3** | Kill Switch + 应急通道 + HUMAN_MEMORY_CARD | 维护者缺席模式 + 脚本 ROI 追踪 (L5) |
| **Vibe Coding 适配** | **L3** | 前缀约定 + docstring 自文档 + rules 即 prompt | 环境快照 + session 中断续接 + 振荡检测 (L5) |

> **整体评级：L3.6**（施工第四层盲点 B60-B91 + 10 行动项 A1-A10 后目标 L4.5）

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
| **B107** | **运行态数据单机脆性** | 取证专家追问：「全量扫描结果在哪？」答案：SQLite (`findings_timeseries.db`) + JSON (`finding-state-db.json`) + YAML 状态文件（`kill-switch-state.yaml` 等）。**但这些文件是否纳入 Git？是否异地备份？** 如果 Owner 的笔记本电脑 SSD 故障/勒索软件/咖啡泼溅 → 全部运行态数据永久丢失。Git 备份了代码，但没备份审计证据。 | R5 提到「单人项目瓶颈」但聚焦于审计独立性，未考虑物理单点故障 |

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

## 32. 五层盲点覆盖总览

| 层级 | 编号区间 | 数量 | 覆盖领域 |
|------|---------|:---:|------|
| **第一层** | B1-B13 | 13 | 基础设施层：审计疲劳、报告过期、覆盖率、版本化、配置漂移 |
| **第二层** | B14-B25 | 12 | 机制层：Error Budget、Baseline、Shadow Mode、Finding 生命周期、Kill Switch |
| **第三层** | B43-B59 | 17 | 纵深安全层：供应链安全、Provenance、Slopsquatting、多模型共识、Burn Rate |
| **第四层** | B60-B91 | 32 | AI+1人维护层：会话管理、反馈回路安全、规模递增、Vibe Coding 适配 |
| **第五层** | B92-B107 | 16 | 取证穿透层：信任根悖论、时间涂抹、证据可验证性、分类器静默降级 |
| **合计** | B1-B107 | **90** | 基础设施→机制→安全→AI协作→证据法理 全纵深 |

**致命度 Top 3**：B92（启动信任悖论）→ B101（自述证据不可验证）→ B93（D1 单点灾难性失效）

---

## 33. 物理韧性与灾备补全

> B107 揭示的「单机脆性」需要在蓝图层级给出灾备策略——不能留给「运维阶段再说」。

### 33.1 关键运行态数据的灾备分级

| 数据 | 存储位置 | 灾备策略 | Git 追踪 |
|------|---------|---------|:---:|
| `kill-switch-state.yaml` | `meta/` | 每次变更后 commit → 随代码同步备份 | ✅ |
| `shadow-mode-state.yaml` | `meta/` | 每次变更后 commit | ✅ |
| `error-budget-state.yaml` | `meta/` | 每次变更后 commit | ✅ |
| `script-retirement-state.yaml` | `meta/` | 每次变更后 commit | ✅ |
| `trust-tier-policy.yaml` | `meta/` | 作为配置管理 → commit | ✅ |
| `findings_timeseries.db` (SQLite) | `meta/` | **每周导出 JSON → commit 到 `meta/backups/`** | ❌ (二进制) → ✅ (JSON) |
| `finding-state-db.json` | `meta/` | 每次 `run_all.py` 后 commit | ✅ |
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

> 五层90盲点之外的工程陷阱——1人+AI 维护提前知道 = 避免浪费一个 AI session。

| # | 陷阱 | 后果 | 预防规则 |
|---|------|------|---------|
| 34.1 | 绝对路径硬编码 `D:\ZephyrAlpha\...` | clone 到其他盘符→脚本集体崩溃 | 当/如果脚本使用路径 → 则必须用 `REPO_ROOT = Path(__file__).resolve().parents[3]`。自检：`grep -r "D:\\\\ZephyrAlpha" scripts/governance/` 应返回 0 |
| 34.2 | 依赖版本未精确锁定（`pyyaml>=6.0`） | 静默升级→API 行为变化→假阴性/假阳性 | 当/如果声明依赖 → 则必须精确锁定版本号。每季度 `pip freeze > frozen-versions.txt` |
| 34.3 | 同进程 import 污染 | 脚本 A 修改全局状态→脚本 B 继承污染→行为异常 | 当/如果执行多脚本 → 则必须用 `subprocess.run([sys.executable, script_path])` 隔离。若必须 import → `__main__` 入口必须是纯函数 |
| 34.4 | SLA 指标"待测量" | Error Budget/Kill Switch 决策盲飞 | 当/如果 run_all.py 完成扫描 → 则必须追加一行到 `meta/sla_metrics.jsonl`（timestamp/scan_type/total_findings/scan_duration_s/exit_code） |
| 34.5 | 部分扫描的虚假安全感 | `--dimensions d1,d3` exit 0 但 D5 可能已损坏 | 当/如果执行部分扫描 → 则必须输出显式警告：`⚠ PARTIAL SCAN: Only D1,D3 executed. UNCHECKED: D5, D8, and 8 other dimensions.` |
| 34.6 | 脚本-蓝图版本漂移 | 脚本在新蓝图层级下用旧假设运行→漏检 | 当/如果生成 manifest → 则必须自动从蓝图 frontmatter 读取版本号填入 `compatible_blueprint_version` |
| 34.7 | AI Session 间任务修复交接损耗 | Session B 不知道 Session A 的上下文→修复偏差→振荡 | 当/如果创建修复任务 → 则必须包含 finding_id + evidence + detected_at。修复 AI 启动时先拉取 Finding 全文 |

---

## 35. 分布式执行架构
> 本章节定义 1500 模块 / 10,000 脚本 / 100 AI Worker 并发场景下的执行架构。
> 对齐 §8.4 规模-架构映射模型中的 L 级（2,000~10,000 脚本 / 20~100 Worker）。

### 35.1 设计原则

| # | 原则 | 说明 |
|---|------|------|
| 1 | **渐进式升级** | S→M→L 逐级演进，不跳级。当前 S 级组件（ThreadPoolExecutor、ProcessLock）在 M 级仍可用，L 级才需替换 |
| 2 | **接口不变** | `run_all.py` 的 CLI 接口（`--dimensions`、`--tags`、`--diff-ref` 等）在任何规模下保持一致——用户无感知切换 |
| 3 | **单机兼容** | 分布式组件在单机模式下可降级为本地实现——无 Redis 时自动 fallback 到 MemoryLock，无 Worker 注册时自动 fallback 到 ThreadPoolExecutor |
| 4 | **Finding Schema 不变** | 无论单机还是分布式，输出格式始终是 Finding Schema JSONL——下游消费者无需改动 |

### 35.2 Worker 生命周期管理

| 状态 | 转换条件 | 说明 |
|------|---------|------|
| REGISTERED | Worker 启动时向 Coordinator 注册 | 初始状态 |
| READY | REGISTERED + heartbeat 通过 | 可接收任务 |
| RUNNING | READY + 接收任务 | 执行脚本 |
| READY | RUNNING + 任务完成 | 回到可接收状态 |
| DEREGISTERED | heartbeat 超时 / 主动退出 | 从可用池移除 |

| 机制 | 说明 | 默认值 |
|------|------|--------|
| **注册** | Worker 启动时向 Coordinator 发送 `{worker_id, capabilities, max_concurrent}` | — |
| **心跳** | Worker 每 N 秒发送心跳；连续 M 次未收到 → 标记 DEREGISTERED | 间隔 10s / 超时 3 次 |
| **能力声明** | Worker 声明可执行的维度/标签/优先级 | `capabilities: {dimensions: [D1,D3], tags: [Quick], max_concurrent: 8}` |
| **优雅退出** | Worker 收到 SIGTERM → 完成当前任务 → DEREGISTERED → 退出 | 超时 30s 后强制 kill |
| **负载均衡** | Coordinator 按最少正在执行任务数分配 | — |

### 35.3 任务分发与调度

| 调度模式 | 触发条件 | 行为 |
|---------|---------|------|
| **维度亲和** | 默认 | 脚本按维度路由到声明了该维度能力的 Worker 池 |
| **优先级抢占** | P0 脚本到达 | P0 可抢占 P2 Worker 的执行槽 |
| **分片调度** | 单维度脚本数 > 200 | 按模块 ID 哈希分片到多个 Worker |
| **增量调度** | `--diff-ref` 模式 | 只调度与变更文件相关的维度 |

**任务包（Task Pack）字段**：task_id / dimension / scripts / timeout_seconds / priority / diff_ref / target_modules

### 35.4 分布式锁

| 锁层级 | 单机实现 | 分布式实现 | 适用场景 |
|--------|---------|-----------|---------|
| **L0 全局** | ProcessLock (PID 文件) | Redis SETNX + TTL | 防止同一维度被多个 Worker 同时扫描 |
| **L1 维度** | DimensionLock (threading.Lock) | Redis Hash + Field Lock | 同维度串行、不同维度并行 |
| **L2 文件** | FileLock (fcntl/msvcrt) | Redis Key-per-file | 同文件读写互斥 |

**降级策略**：Redis/etcd 不可用时 → 自动 fallback 到本地锁 → 功能降级为单机模式 → 告警通知 Owner。

### 35.5 故障恢复

| 故障场景 | 检测方式 | 恢复策略 |
|---------|---------|---------|
| **Worker 崩溃** | 心跳超时（3 次未收到） | 正在执行的任务标记为 FAILED → 重新入队 → 分配给其他 Worker |
| **Coordinator 崩溃** | Worker 心跳回复超时 | Worker 进入自治模式（本地执行已分配任务）→ 新 Coordinator 启动后重新注册 |
| **Redis/etcd 不可用** | 连接超时 + 重试 3 次 | 降级为单机锁 → 告警 → 人工介入 |
| **任务超时** | TieredTimeout（S0=10s, S1=60s, S2=180s, S3=120s） | kill 超时任务 → 标记 exit 3 → CircuitBreaker 计数 |
| **CircuitBreaker OPEN** | 连续失败 ≥ 阈值 | 该池暂停接收新任务 → 等待恢复窗口 → HALF_OPEN 探测 |

### 35.6 Finding 聚合

100 Worker 并发产出 Finding → 需要聚合为统一视图：

| 步骤 | 说明 |
|------|------|
| **1. 分片写入** | 每个 Worker 写入独立 JSONL 文件（按 `worker_id` 命名）——无文件锁竞争 |
| **2. 聚合** | Coordinator 在所有 Worker 完成后，按 `finding_id` 去重（同一内容哈希只保留一条） |
| **3. 排序** | 按 severity(CRITICAL→INFO) + dimension 排序 |
| **4. 入库** | 写入 `findings_YYYYMMDD.jsonl` + SQLite 时序表 |

### 35.7 技术选型约束

> 不在蓝图中锁定具体技术栈——但定义选型标准和候选方案。

| 组件 | 选型标准 | 候选方案 |
|------|---------|---------|
| **任务队列** | Python 原生支持 + 轻量级 + 支持 priority + 支持 result backend | Celery + Redis / Ray / Python multiprocessing.Queue（单机降级） |
| **分布式锁** | TTL 自动续期 + 防死锁 + Python async 兼容 | Redis (Redlock) / etcd / ZooKeeper / SQLite WAL（单机降级） |
| **Worker 通信** | 低延迟 + 支持广播 + 支持 request-reply | Redis Pub/Sub / ZeroMQ / HTTP long-polling |
| **状态存储** | ACID + JSONL 导出 + 支持 10,000 脚本规模 | SQLite WAL（单机/分片） / PostgreSQL（L 级远期） |

### 35.8 与现有组件的关系

| 现有组件 | §35 中的角色 | 变更 |
|---------|-------------|------|
| `_concurrency.py` BulkheadExecutorV2 | M 级核心执行器，L 级降级为 Worker 内部调度 | 参数化 Pool 配置（从 thresholds.yaml 读取） |
| `_concurrency.py` ShardRouter | L 级分片调度的基础——从 DB 路由升级为执行路由 | 分片数从 4 → 16+，路由目标从 SQLite 路径扩展为 Worker ID |
| `_concurrency.py` CircuitBreaker | Worker 级熔断——保护单个 Worker 不被故障脚本拖垮 | 不变 |
| `_concurrency.py` TokenBucket | Coordinator 级限流——保护全局资源 | refill_rate 和 burst_size 参数化（从 thresholds.yaml 读取） |
| `_concurrency.py` AdmissionController | Coordinator 级准入——P0 优先调度 | concurrency_limit 参数化 |
| `lock.py` DistributedLock Protocol | L 级分布式锁接口——已有 Protocol 定义 | 补充 Redis/etcd 实现 |
| `run_all.py` | 调度入口——CLI 接口不变 | 内部从 ThreadPoolExecutor 切换到 Coordinator 调度 |

---

## 36. L 规模升级施工方案（10,000 脚本 / 1,500 模块 / 100 AI 并发）

> 本章节是 §8.4 规模-架构映射模型中 **L 级**的具体施工方案——将 S 级硬编码参数升级为 L 级可配置参数，补齐 5 项关键缺口。
> **前置条件**：§35 分布式执行架构已定义框架，本章节是 §35 的落地施工清单。

### 36.1 缺口总览

| # | 缺口 | 严重性 | 现状 | 目标 | 对齐 §35 |
|---|------|:---:|------|------|:---:|
| G1 | L0 全局进程锁阻止多 AI 并行扫描 | 🔴 P0 | ProcessLock 全局互斥——同一时间只允许 1 个 run_all.py 实例 | per-session 锁——每个 AI session 独立扫描会话 | §35.4 |
| G2 | 四池 max_workers 硬编码，100 AI 下严重不足 | 🔴 P0 | quick=12 / content=6 / ai=4 / disruptive=2（总计 24 worker） | 从 thresholds.yaml 动态读取 + 按 AI Worker 数量自动缩放 | §35.8 |
| G3 | SQLite 单写锁 100 AI 写入争抢 | 🟠 P1 | ATM 锁串行化 + 5s busy_timeout——100 AI 排队等待 | 写入队列 + 批量合并 + 主库分片 | §35.4 |
| G4 | 缺少脚本执行历史表 | 🟠 P1 | 执行结果仅存 JSONL 文件——查询和聚合困难 | 新增 `script_executions` 表 + JSONL 双写 | §35.6 |
| G5 | ShardRouter 分片数硬编码为 4 | 🟡 P2 | 4 分片 × ~2,500 脚本/分片 = 锁竞争 | 从 thresholds.yaml 读取分片数（L 级默认 16） | §35.8 |

### 36.2 G1：L0 全局进程锁 → per-session 扫描会话锁

**问题**：`ProcessLock` 全局互斥——同一时间只允许 1 个 run_all.py 实例。100 AI 并发下 99 个被阻塞。

**方案**：将 L0 从"全局互斥"改为"扫描会话隔离"——每个 AI session 持有独立锁文件 `meta/scan_sessions/session_{agent_id}.lock`，不同 session 可并行扫描。

**新增类**：`ScanSessionLock`（`_concurrency.py`）——替代 ProcessLock，保留 ProcessLock 作为降级选项。

**LockManager 修改**：新增 `use_session_lock: bool = False` 参数，`True` 时使用 ScanSessionLock。

**run_all.py 入口**：根据 `thresholds.yaml` 中 `estimated_ai_workers > 8` 自动选择锁模式。

**阈值配置**：

```yaml
concurrency:
  lock:
    l0_mode: "session"
    l0_session_stale_seconds: 300
    l0_session_dir: "meta/scan_sessions"
    l0_global_fallback: true
```

**降级策略**：

| 条件 | 行为 |
|------|------|
| `estimated_ai_workers ≤ 8`（S 级） | ProcessLock 全局互斥——零风险 |
| `8 < estimated_ai_workers ≤ 20`（M 级） | ScanSessionLock——per-session 隔离 |
| `estimated_ai_workers > 20`（L 级） | ScanSessionLock + AdmissionController |
| 锁文件目录不可写 | 自动降级为 ProcessLock + 告警 |

**迁移步骤**：

| 步骤 | 操作 | 回滚 |
|:---:|------|------|
| 1 | 新增 `ScanSessionLock` 类（不删除 `ProcessLock`） | 删除新类 |
| 2 | `LockManager.__init__` 新增 `use_session_lock` 参数（默认 `False`） | 默认值保证兼容 |
| 3 | `run_all.py` 入口根据 `thresholds.yaml` 选择锁模式 | 配置默认 `global` |
| 4 | `thresholds.yaml` 新增 `lock.l0_mode` 配置项 | 删除配置项 |
| 5 | 测试：2 个并发 `run_all.py --agent-id test-01 / test-02` 同时运行 | — |

---

### 36.3 G2：四池 max_workers 参数化 + 自动缩放

**问题**：`POOL_CONFIGS` 硬编码四池 worker 数（quick=12/content=6/ai=4/disruptive=2，总计 24）。100 AI 并发需要 40~100 并发执行能力。

**方案**：`BulkheadExecutor` 池配置从 `thresholds.yaml` 动态读取，缩放公式：`pool_max_workers = base_workers × max(1, estimated_ai_workers / 8)`，上限 `max_workers_cap`。

**L 级（100 AI）推荐配置**：

| 池 | base | 缩放系数 (100/8=12.5) | cap | 最终值 |
|---|:---:|:---:|:---:|:---:|
| quick | 12 | ×12.5 | 40 | **40** |
| content_analysis | 8 | ×12.5 | 24 | **24** |
| ai_generated | 16 | ×12.5 | 20 | **20** |
| disruptive | 4 | ×12.5 | 8 | **8** |
| **总计** | 40 | — | 92 | **92** |

**代码改动**：`BulkheadExecutor.__init__` 新增 `auto_scale: bool = False` 参数 + `_load_pool_config()` 静态方法从 thresholds.yaml 读取。

**阈值配置**：

```yaml
concurrency:
  estimated_ai_workers: 1
  pool:
    quick: {max_workers: 12, max_workers_cap: 40}
    content_analysis: {max_workers: 8, max_workers_cap: 24}
    ai_generated: {max_workers: 16, max_workers_cap: 20}
    disruptive: {max_workers: 4, max_workers_cap: 8}
  auto_scale: {enabled: false, base_ai_workers: 8}
```

**迁移步骤**：

| 步骤 | 操作 | 回滚 |
|:---:|------|------|
| 1 | `BulkheadExecutor.__init__` 新增 `auto_scale` 参数（默认 `False`） | 默认值保证兼容 |
| 2 | 新增 `_load_pool_config()` 静态方法 | 删除方法 |
| 3 | `thresholds.yaml` 新增 `estimated_ai_workers` + `max_workers_cap` + `auto_scale` | 删除配置项 |
| 4 | `run_all.py` 入口根据规模启用 `auto_scale` | 配置默认 `false` |
| 5 | 压力测试：逐步增加 `estimated_ai_workers` 验证缩放行为 | — |

---

### 36.4 G3：SQLite 写入队列 + 批量合并 ⏸ 暂缓（待 L 级 5000+脚本）

> **⚠ 012B 裁定（2026-06-28）**：WriteBatcher 暂缓。当前 S 级 571 脚本无写争抢实证，
> L 级（5000+脚本）启动。depgraph 已迁 PG（MVCC 解决其写争抢），剩余 SQLite 争抢仅在 governance.db。

**问题**：SQLite WAL 模式只允许 1 个写事务。100 AI 同时写 events/gates/tasks 时，99 个排队等待 busy_timeout（5s）。

**方案**：引入 `WriteBatcher`——将多个 AI 的写入请求缓冲到内存队列，按时间窗口（100ms）或批量大小（50 条）合并为一次写事务。

**性能估算**：

| 场景 | 无 WriteBatcher | 有 WriteBatcher | 提升 |
|------|:---:|:---:|:---:|
| 100 AI 同时写 events | ~2s 排队 | ~100ms 批量提交 | 20x |
| 100 AI 同时 transition() | ~5s 排队 | ~200ms 批量提交 | 25x |

**新增文件**：`src/zephyr/data/persistence/write_batcher.py`——`WriteBatcher` 类，接口：`submit(table, row)` / `submit_many(table, rows)` / `flush()` / `start()` / `stop()`。

**集成点**：`task_repo.py` 的 `transition()` 和 `create()` 方法新增 `use_batcher: bool = False` 参数。

**阈值配置**：

```yaml
concurrency:
  write_batcher: {enabled: false, flush_interval_seconds: 0.1, flush_batch_size: 50, max_queue_size: 10000}
```

**降级策略**：`enabled=false`（S/M级）→ 直接写入零延迟 / `enabled=true`（L级）→ 批量写入100ms延迟换20x吞吐 / 队列满或线程崩溃 → 自动降级直接写入+告警。

**迁移步骤**：

| 步骤 | 操作 | 回滚 |
|:---:|------|------|
| 1 | 新增 `src/zephyr/data/persistence/write_batcher.py` | 删除文件 |
| 2 | `task_repo.py` 新增 `use_batcher` 参数（默认 `False`） | 默认值保证兼容 |
| 3 | `thresholds.yaml` 新增 `write_batcher` 配置组 | 删除配置项 |
| 4 | 测试：100 并发写入 events 表，对比有/无 WriteBatcher 的吞吐 | — |

---

### 36.5 G4：脚本执行历史表 ⏸ 暂缓（待 M-1 级 500+脚本，当前 571 已达）

> **⚠ 012B 裁定（2026-06-28）**：ScriptExecutionLogger 暂缓但近期可启动。
> 当前 571 脚本已达 M-1 下限 500，纯新增低风险（不影响现有表）。
> 启动条件：JSONL 查询痛点实证，或 audit_orchestrator 完成度提升至 20/33。

**问题**：当前脚本执行结果仅存 JSONL 文件，10,000 脚本 × 100 AI 的执行历史无法高效查询和聚合。

**方案**：新增 `script_executions` 表（v17 迁移），字段：execution_id / script_name / dimension / session_id / agent_id / scan_mode / pool_name / started_at / finished_at / duration_ms / exit_code / findings_count / is_failed / error_message / diff_ref / target_modules / checkpoint_id。4 个索引（dimension+started_at / session_id+started_at / script_name+started_at / agent_id+started_at）。

**容量估算**：~100,000 行/月 × ~500 字节/行 ≈ 50 MB/月。30 天热数据 + Parquet 归档。

**代码改动**：`sqlite_schema.py` 新增 v17 迁移 + `run_all.py` 的 `_execute_one_script` 完成后调用 `_record_execution` + `olap_engine.py` 新增 `archive_script_executions()` 归档方法。

**迁移步骤**：

| 步骤 | 操作 | 回滚 |
|:---:|------|------|
| 1 | `sqlite_schema.py` 新增 v17 迁移 | 删除迁移条目 |
| 2 | `run_all.py` 的 `_execute_one_script` 完成后调用 `_record_execution` | 删除调用 |
| 3 | `olap_engine.py` 新增 `archive_script_executions()` 归档方法 | 删除方法 |
| 4 | 测试：运行 `run_all.py` 后查询 `script_executions` 表验证记录 | — |

---

### 36.6 G5：ShardRouter 分片数参数化

**问题**：`ShardRouter` 的 `shard_count=4` 硬编码。1500 模块 / 10,000 脚本下每片 ~2,500 脚本，锁竞争严重。`thresholds.yaml` 已定义 `shard.count: 16` 但代码未读取。

**方案**：`ShardRouter.shard_count` 从 `thresholds.yaml` 读取，支持运行时调整。分片再平衡采用"新分片写入新路由，旧分片逐步迁移"策略。

**代码改动**：`ShardRouter.__init__` 新增 `_load_shard_count()` 静态方法从 thresholds.yaml 读取，保留硬编码默认值 4 作为 fallback。

**分片再平衡策略**（shard.count 从 4→16）：

| 步骤 | 操作 |
|:---:|------|
| 1 | 新写入按 `hash(module_id) % 16` 路由到新分片 |
| 2 | 后台线程逐步将旧 4 分片数据迁移到新 16 分片 |
| 3 | 迁移完成前，查询走 `UNION ALL` 旧分片 + 新分片 |
| 4 | 迁移完成后，旧分片标记为 `deprecated`，7 天后删除 |

**迁移步骤**：

| 步骤 | 操作 | 回滚 |
|:---:|------|------|
| 1 | `ShardRouter.__init__` 支持从 `thresholds.yaml` 读取 `shard_count` | 保留硬编码默认值 4 |
| 2 | 新增 `_load_shard_count()` 静态方法 | 删除方法 |
| 3 | 测试：修改 `thresholds.yaml` 中 `shard.count` 为 16，验证路由分布 | — |

---

### 36.7 整体施工顺序

```
Phase M-1（S→M 过渡，脚本数 500~2000）
  ├── G5: ShardRouter 参数化（风险最低，纯配置读取）
  ├── G2: 四池 max_workers 参数化（不改默认值，仅新增读取逻辑）
  └── G4: script_executions 表（纯新增，不影响现有表）

Phase M-2（M 级稳定，脚本数 2000~5000）
  ├── G1: ScanSessionLock（替代 ProcessLock，需充分测试并发安全）
  └── G3: WriteBatcher（新增模块，需性能基准测试）

Phase L-1（M→L 过渡，脚本数 5000~10000）
  ├── G2: auto_scale=true（启用自动缩放）
  ├── G3: write_batcher.enabled=true（启用批量写入）
  ├── G5: shard.count=16（扩展分片）
  └── 压力测试：100 AI 并发增量扫描端到端验证

Phase L-2（L 级稳定）
  ├── §35 分布式组件接入（Coordinator + Worker 注册/心跳）
  ├── 分布式锁后端（Redis/etcd）
  └── 全量扫描分布式执行
```

### 36.8 验收标准

| # | 验收项 | 通过条件 |
|---|--------|---------|
| 1 | 2 个 AI session 并行扫描 | 两者同时完成，无锁等待超时 |
| 2 | 100 AI 并发增量扫描 | 总耗时 < 2 分钟（增量 15~30 脚本/AI） |
| 3 | 四池自动缩放 | `estimated_ai_workers=100` 时总 worker 数 ≥ 80 |
| 4 | WriteBatcher 吞吐 | 100 并发写入 events 吞吐 ≥ 1000 条/秒 |
| 5 | script_executions 查询 | 按维度/agent/session 查询 < 50ms |
| 6 | ShardRouter 16 分片 | 1500 模块均匀分布，最大偏差 < 10% |
| 7 | 降级测试 | Redis 不可用时自动降级为单机模式，功能不丢失 |
| 8 | 向后兼容 | `thresholds.yaml` 未配置新项时，行为与 S 级完全一致 |

### 36.9 风险与缓解

| # | 风险 | 概率 | 影响 | 缓解 |
|---|------|:---:|:---:|------|
| R1 | ScanSessionLock 并发安全漏洞 | 中 | 高 | 保留 ProcessLock 作为降级选项 + 充分并发测试 |
| R2 | WriteBatcher 丢数据（进程崩溃时队列未刷盘） | 低 | 高 | `stop()` 时强制 flush + WAL 模式保证已提交数据不丢 |
| R3 | 自动缩放过度分配导致 OOM | 低 | 高 | `max_workers_cap` 硬上限 + 内存监控告警 |
| R4 | 分片再平衡期间查询不一致 | 中 | 中 | UNION ALL 双读 + 迁移完成前旧分片保留 |
| R5 | thresholds.yaml 配置错误导致系统不可用 | 中 | 高 | 配置校验 + 无效值 fallback 到硬编码默认值 |

---




## Consumers
- zephyr.governance_automation (internal)
