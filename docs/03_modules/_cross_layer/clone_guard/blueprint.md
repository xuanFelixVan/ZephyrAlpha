---
module_id: MOD-CLONE_GUARD
submodule_path: src/zephyr/clone_guard
title: "CloneGuard 蓝图 — 多引擎代码克隆检测集成防御体系（治 AI 重复造轮子病根）"
doc_type: blueprint
template_for: blueprint
status: Draft
version: "0.1.4"
layer: L1_foundation
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-08-06"
valid_from: "2026-08-06"
ttl: permanent
actual_disk_path: "src/zephyr/clone_guard/"
belongs_to: "MOD-MASTER_BLUEPRINT"
parent_module: "MOD-MASTER_BLUEPRINT"
last_updated: "2026-08-08"
last_verified: "2026-08-06"
generation: 1
functional_domain: governance
rule_form: structural
scope: global
stability: evolving
verifiability: hybrid
codification_level: L1
summary: "6开源引擎(Echo-Guard+reDUP+ast-grep+mcrit+Vendetect+relate)并发集成的四层防御纵深(L0源头预防+L1提交拦截+L2周期审计+L3跨边界审计)，治本100%AI开发场景下的重复造轮子病根，升级CAPABILITY-OVERLAP门禁为强制合并去重"
tags: [clone_guard, code-clone-detection, echo-guard, redup, ast-grep, mcrit, vendetect, relate, dry, ai-rot, pre-commit, mcp, semantic-similarity, codesage, tree-sitter, minhash, type1-clone, type2-clone, type3-clone, type4-clone, force-merge, dedup, governance, capability-overlap, defense-in-depth]
priority: P1
runtime_plane: cold
depends_on:
  - {target: "MOD-GATE_ENGINE", at: "§0", why: "GitCommitGateway 唯一提交入口——CloneGuard L1 通过升级 CAPABILITY-OVERLAP 门禁接入"}
  - {target: "MOD-GATE_ENGINE", at: "§0", why: "pre-commit 门禁注册机制——复用 commit_gate_registry"}
  - {target: "MOD-MASTER_BLUEPRINT", at: "§11", why: "AGENTS.md §11 治理条款——CloneGuard 行为规范写入"}
  - {target: "architecture_issue_registry.yaml", at: "#ARCH-GOV-BUDGET-001", why: "I-GOV-3 等量退役约束——升级现有门禁不新增"}
  - {target: "architecture_issue_registry.yaml", at: "#ARCH-FORCE-MERGE-DEDUP-001", why: "强制合并去重裁决条目（待登记）"}
references:
  - {path: "d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint_construction_template.md", section: "REQUIRED_SECTIONS", why: "蓝图模板 v3.5 合规基准"}
  - {path: "https://github.com/jwizenfeld04/Echo-Guard", section: "README", why: "Echo-Guard v0.4.1 主检测引擎——AST哈希+CodeSAGE嵌入+MCP+DRY严重性"}
  - {path: "https://github.com/semcod/redup", section: "README", why: "reDUP v0.4.46 深度分析引擎——六层检测+重构规划+影响评分+跨项目比较"}
  - {path: "https://ast-grep.github.io/", section: "docs", why: "ast-grep 规则引擎——tree-sitter YAML 结构化模式匹配/重写"}
  - {path: "https://github.com/danielplohmann/mcrit", section: "README", why: "mcrit MinHash 代码关系工具包——大规模索引底座"}
  - {path: "https://github.com/trailofbits/vendetect", section: "README", why: "Vendetect 跨仓库 vendored 代码检测——合规审计"}
  - {path: "https://github.com/The-Billy-Company/relate", section: "README", why: "relate 基于压缩的相似度搜索——无模型快速预筛加速器"}
  - {path: "https://arxiv.org/html/2603.15004v1", section: "full", why: "TriFusion-LLM 多模态融合+LLM仲裁——技术储备(Type-4 F1=0.996)"}
  - {path: "d:/ZephyrAlpha/src/zephyr/gov_enforcement/commit_gates/arch_reference_gate.py", section: "§0.1", why: "门禁实现参考——GateSpec/priority/fail-closed 模式"}
ssot_claims:
  - {claim: "代码克隆检测引擎编排策略SSoT", scope: "module"}
  - {claim: "AI重复造轮子四层防御纵深SSoT", scope: "module"}
  - {claim: "克隆严重性到门禁阻断映射SSoT", scope: "module"}
  - {claim: "clone_guard.yml 统一配置SSoT", scope: "module"}
responsibility_domain: 
design_maturity: production
build_status: generated
---

# CloneGuard 蓝图 — 多引擎代码克隆检测集成防御体系

## 概述
<!-- temporal_type: permanent -->

本蓝图描述 CloneGuard——ZephyrAlpha 的代码克隆检测集成防御体系。它解决**100% AI 开发场景下的"重复造轮子"病根**：AI agent（Claude Code 等）为已在代码库中解决过的任务反复生成新代码，导致功能重叠的"AI Rot"（AI 腐烂）持续累积。

**治本思路**：不自研检测算法，而是将 6 个 2026 年最前沿的开源克隆检测引擎并发集成，通过统一编排层形成"四层防御纵深"，覆盖 AI 造轮子的全部 4 个发生时机（写代码前 / 提交时 / 累积期 / 跨边界）。核心约束遵循 #ARCH-GOV-BUDGET-001 的 I-GOV-3（治理预算等量退役）：**升级现有 CAPABILITY-OVERLAP 门禁，不新增门禁**。

> module_id: MOD-CLONE_GUARD | version: 0.1.4 | status: Draft | layer: cross_layer
> actual_disk_path: src/zephyr/clone_guard/ | generation: 1 | construction_progress: not_started
> **病根定位**：100% AI 开发 → AI 无"记忆" → 为已解决任务重复生成 → 功能重叠代码累积 → 维护成本指数增长 + bug 传播风险
> **治本原则**：用现成开源引擎 + 自研仅编排层（~1500行）+ 升级不新增门禁（守 I-GOV-3）

---

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-CLONE_GUARD`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-CLONE_GUARD` 的 24 个 file 节点 | production | `extract_depgraph.py --modules MOD-CLONE_GUARD` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Draft | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-CLONE_GUARD | MOD-CLONE_GUARD | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | generated | generated | ✅ |
| file_count | 24 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## §1 病根分析与治本逻辑
<!-- temporal_type: permanent -->

### §1.1 病根：AI 造轮子的 4 个时机

| 时机 | 病根表现 | 后果 | 单工具盲区 |
|---|---|---|---|
| ① 写代码前 | AI 不查重就生成新函数 | 重复从源头产生 | 无 MCP 的工具堵不住 |
| ② 提交时 | pre-commit 只查语法不查语义 | 语义重复漏检 | 仅 AST 哈希的工具漏 Type-3/4 |
| ③ 累积期 | 重复代码慢慢堆积 | "AI Rot" 技术债 | 仅增量的工具看不到全貌 |
| ④ 跨边界 | 抄外部仓库 / 跨项目重复 | 合规风险 + 跨域耦合 | 单仓库工具完全看不见 |

### §1.2 治本逻辑：四层防御纵深

每层堵一个时机，缺一不可。单一引擎最多覆盖 2 层，必须组合：

```
L0 源头预防 ──┐
              ├─ 堵时机①（AI 写代码前查重）
L1 提交拦截 ──┤
              ├─ 堵时机②（pre-commit 硬阻断）
L2 周期审计 ──┤
              ├─ 堵时机③（全量发现累积债）
L3 跨边界审计 ┘
              └─ 堵时机④（跨仓库/跨项目）
```

### §1.3 与 #ARCH-GOV-BUDGET-001 的关系

本方案是 #ARCH-GOV-BUDGET-001 裁定的"强制合并去重"方向的技术落地：
- **I-GOV-3 等量退役**：升级现有 CAPABILITY-OVERLAP 门禁，不新增门禁
- **I-GOV-2 reconciler 无写权**：L2 审计结果通过 reconciler 以 `warn` 模式提醒，不自动 commit
- **I-GOV-1 派生产物离库**：审计报告属派生产物，不入 git（由生成器按需生成）

---

## §2 工具选型与分工定案
<!-- temporal_type: permanent -->

### §2.1 选型过程

全网调研 2026-08-06 时点 GitHub 开源项目 + 前沿学术论文，候选池 15+ 工具，按"AI生成代码支持 / Python支持 / pre-commit集成 / MCP集成 / 语义克隆(Type-4)能力 / 许可证"六维筛选，最终定案 6 引擎。**PyChase 不纳入**（其 AST+MinHash 功能被 Echo-Guard+mcrit 完全覆盖，纳入违反 I-GOV-3）。

### §2.2 六引擎分工矩阵（去冗余）

| 引擎 | 许可证 | 版本 | 不可替代的职责 | 防御层 | 克隆类型覆盖 |
|---|---|---|---|---|---|
| **Echo-Guard** | MIT | v0.4.1 | 主检测：AST哈希 + CodeSAGE嵌入 + MCP + DRY严重性 + pre-commit快速路径 | L0+L1+L2 | T1/T2/T3/T4 |
| **ast-grep** | MIT | latest | 规则引擎：YAML 自定义结构化模式（业务规则） | L1 | T1/T2（规则化） |
| **reDUP** | Apache-2.0 | v0.4.46 | 深度分析：六层全量 + 重构规划 + 影响评分 + 跨项目比较 + `--changed-only`增量 | L1+L2+L3 | T1/T2/T3/T4 |
| **mcrit** | ~~MIT~~ GPL-3.0 | latest | ⚠️**已废弃（领域错位）**——原假设"MinHash 源码索引底座"实为二进制/恶意软件逆向相似度工具（Fraunhofer FKIE），非源码克隆检测；需 C++编译器+MongoDB | ~~L2（底座）~~ | 不适用 |
| **Vendetect** | AGPL-3.0 | latest | 跨仓库审计：检测外部代码拷贝（合规）；CLI 勘误——位置参数 `vendetect TEST_REPO SOURCE_REPO`（非 `compare --local/--remote`） | L3 | T1/T2/T3 |
| **relate** | MIT (datasketch) | latest | ✅**Path B 落地**——真实 relate 是 Zig 二进制（无预编译资产），改用 datasketch（MinHash LSH）进程内替代；标识符归一化使 Type-2 克隆可检测；k-gram shingle 对语句重排敏感，T3 仅部分覆盖；无 CLI/无模型/纯 Python | L2+L3（加速器） | T1/T2（+T3 partial） |

> **⚠️ 引擎核实勘误（2026-08-06，#ARCH-FORCE-MERGE-DEDUP-001）**：上表 mcrit/relate 的原蓝图假设经 PyPI+GitHub 源码核实**与事实不符**，reDUP/Vendetect 的 CLI/输出格式假设亦有偏差。逐引擎裁定：mcrit **废弃**（领域错位，适配器降级为占位）；relate **Path B 落地**（真实工具是 Zig 二进制无预编译资产，Path A 不可行；改用 datasketch MinHash LSH 进程内替代，标识符归一化使 Type-2 克隆可检测，35 测试全绿）；Vendetect **采纳并修 CLI**（位置参数 + CSV 输出）；reDUP **条件采纳并修解析器**（`groups/fragments` 结构，安装延后因 ~35 包足迹）。完整分析过程+裁定+施工方案见 `.trae/documents/clone-guard-engine-verification-ruling.md`（IDE scratchpad，非 git 真源）。**验证后集成纪律**：引擎适配器必须针对已捕获的真实 CLI 样本+输出 schema（提交为 `tests/fixtures/<engine>_sample.*`）编写，禁止基于假设实现。

### §2.3 功能去冗余原则

- **嵌入模型**：只用 CodeSAGE（Echo-Guard），关闭 reDUP 的 sentence-transformers
- **索引底座**：~~mcrit~~（已废弃）→ relate 压缩相似度 / reDUP 承担预筛底座角色，不重复建 reDUP/PyChase 的 LSH
- **跨项目比较**：reDUP compare（内部多模块）+ Vendetect（外部仓库）+ relate（快速预筛）
- **MCP**：统一 wrapper 聚合，不暴露各引擎原生 MCP（避免 AI 困惑）

### §2.4 前沿学术算法储备（不直接用，调参参考）

| 算法 | 来源 | 核心贡献 | 储备用途 |
|---|---|---|---|
| TriFusion-LLM | arXiv 2603.15004 (2026-03) | 启发式先验+AST+CodeBERT 三模态融合 + LLM仲裁(仅0.2%样本) | Type-4 调参，Macro-F1 0.875 |
| CodeT5+110M | arXiv 2510.15480 (2025-10) | 76 LLM 评估，CodeT5+ 商业数据集最佳 | 嵌入模型升级路径 |
| CloneLens v2.3 | 2026 奇点大会 | CodeBERT微调+CFG/DFG联合+对比学习孪生网络 | F1 0.86 基准 |
| SemClone | 2026 奇点大会 | AST Flow Encoding+语义对比学习+DCST | 准确率 91.7% |

---

## §3 四层防御纵深架构
<!-- temporal_type: permanent -->

### §3.1 架构总览

```
┌─────────────────────────────────────────────────────────────────────┐
│  统一编排层 (Zephyr CloneGuard Orchestrator)                         │
│  src/zephyr/clone_guard/orchestrator.py                              │
│  统一CLI: zephyr-clone-guard <scan|check|audit|compare|index>        │
│  配置: clone_guard.yml (统一阈值/忽略/严重性)                          │
│  结果聚合器: 多引擎结果去重+合并+统一格式(JSON/SARIF/Markdown)         │
└───────┬─────────────┬─────────────┬─────────────┬───────────────────┘
        │             │             │             │
   ┌────▼────┐   ┌────▼────┐   ┌────▼────┐   ┌───▼─────┐
   │ L0 源头  │   │ L1 提交时│   │ L2 周期  │   │ L3 跨边界│
   │ 预防     │   │ 拦截     │   │ 深度审计 │   │ 审计     │
   │(写前查重)│   │(pre-commit)│ │(CI/定时) │   │(按需/合规)│
   └─────────┘   └─────────┘   └─────────┘   └─────────┘
```

### §3.2 Layer 0 — 源头预防（AI 写代码前查重）

**目标**：在 AI agent 生成新函数前拦截，治本第一道关。

**数据流**：
```
AI Agent (Claude Code)
   │ 写新函数前
   ▼
MCP tool: clone_guard_check_before_write(函数签名+函数体)
   │
   ▼ 并发查询
┌──────────────┬──────────────┬──────────────┐
│ Echo-Guard   │ mcrit 索引   │ relate 预筛  │
│ (AST哈希     │ (MinHash     │ (压缩相似    │
│  快速查重)   │  全库查重)   │  候选集)     │
└──────┬───────┴──────┬───────┴──────┬───────┘
       │              │              │
       └──────────────┴──────────────┘
                      │
                      ▼
            命中 → 返回已存在函数位置 + "复用而非新建"建议
            未命中 → 放行
```

**统一 MCP 工具集**（封装各引擎，对 AI 暴露单一接口）：

| MCP 工具 | 内部调度 | 用途 |
|---|---|---|
| `check_before_write` | Echo-Guard + mcrit 并发 | AI 写新函数前查重 |
| `suggest_refactor` | reDUP 重构规划器 | 给出合并/抽取建议 |
| `search_functions` | mcrit + relate | 按语义搜已有函数 |
| `resolve_finding` | Echo-Guard acknowledged | 标记合理重复 |
| `recheck_file` | Echo-Guard + ast-grep | 文件修改后复查 |

### §3.3 Layer 1 — 提交时拦截（pre-commit 硬阻断）

**目标**：增量、快速、零误报。只查本次 commit 改动的文件。

**并发执行策略**（3 引擎并行，任一硬阻断则失败）：
```
git commit → GitCommitGateway → CAPABILITY-OVERLAP 门禁(升级)
   │
   ▼
CloneGuard check 模式 (输入: staged files, 超时: 30s, fail-closed)
   │ 并发 (asyncio.gather)
   ├─▶ Echo-Guard check FILES     [AST哈希 T1/2]  ~200ms
   │     fail_on: extract (3+副本=硬阻断)
   ├─▶ ast-grep scan --files      [业务规则]       ~100ms
   │     规则: clone_guard/rules/*.yml
   └─▶ reDUP --changed-only       [语义 T3/4]     ~2s
         --base-ref HEAD --min-sim 0.85 --max-groups 0
   │
   ▼ 结果聚合器
   ├─ 任一 extract 级命中 → 硬阻断 + 返回已存在位置
   ├─ review 级命中 → 警告（记入债，不阻断）
   └─ 全部通过 → 放行
```

### §3.4 Layer 2 — 周期深度审计（CI / 定时任务）

**目标**：全量语义分析，发现增量检测漏掉的累积债，给出重构优先级。

```
CloneGuard audit 模式 (每日CI/手动, 输入: 整个仓库)
   │
   │ 阶段1: 索引构建 (并发)
   ├─▶ mcrit build-index         [MinHash 全库索引]   建底座
   ├─▶ Echo-Guard index --full   [CodeSAGE 嵌入库]    建底座
   └─▶ relate (datasketch) index  [MinHash LSH 指纹库]   建底座（进程内惰性构建）
   │
   │ 阶段2: 全量扫描 (并发, 依赖阶段1)
   ├─▶ Echo-Guard scan           [T1/2/3/4 全检测]    主报告
   ├─▶ reDUP scan --semantic     [六层 + 影响评分]     补充报告
   └─▶ ast-grep scan             [业务规则全量]        规则报告
   │
   │ 阶段3: 结果聚合 + 优先级排序
   ▼
统一报告: clone_guard_audit_<date>.json (派生产物,不入git)
   - findings[]: 去重合并后的发现列表
   - refactoring_plan[]: 按影响评分排序的重构计划
   - health_score: A-F 代码库健康分
   - debt_trend: 与上次审计对比的债务趋势
   │
   ▼
写入 depgraph → 标记重复模块为 "refactor_candidate"
触发 reconciler → warn 模式提醒（守 I-GOV-2, 不自动 commit）
```

### §3.5 Layer 3 — 跨边界审计（按需/合规）

**目标**：检测跨仓库、跨项目的重复，合规审计。

```
CloneGuard compare 模式
   ├─ 跨项目(内部多模块): reDUP compare ./src/zephyr/data ./src/zephyr/signal
   ├─ 跨仓库(外部抄袭): Vendetect compare --local . --remote <github-url>
   └─ 快速预筛(大规模): relate (datasketch) search <query> --top-k <N>
```

---

## §4 统一编排层设计
<!-- temporal_type: permanent -->

### §4.1 模块结构（Adapter 模式，关注分离）

```
src/zephyr/clone_guard/
├── __init__.py
├── orchestrator.py          # 统一调度入口 (scan/check/audit/compare)
├── config.py                # clone_guard.yml 加载与校验
├── engines/                 # 引擎适配器 (Adapter 模式, 统一接口)
│   ├── __init__.py
│   ├── echo_guard_adapter.py
│   ├── ast_grep_adapter.py
│   ├── redup_adapter.py
│   ├── mcrit_adapter.py
│   ├── vendetect_adapter.py
│   └── relate_adapter.py
├── aggregator.py            # 多引擎结果去重+合并+统一格式
├── severity.py              # 严重性映射 (extract/review/...)
├── scoring.py               # 影响评分公式
├── mcp_server.py            # 统一 MCP Server (封装各引擎)
├── reporters/
│   ├── __init__.py
│   ├── json_reporter.py
│   ├── sarif_reporter.py    # CI 标准
│   └── markdown_reporter.py
└── rules/                   # ast-grep YAML 规则
    ├── no-duplicate-try-except.yml
    ├── no-duplicate-logger-setup.yml
    └── ...
```

### §4.2 统一 Finding 数据结构

```python
from dataclasses import dataclass

@dataclass
class Location:
    file_path: str
    line_start: int
    line_end: int
    function_name: str | None

@dataclass
class Finding:
    finding_id: str          # 跨引擎唯一ID (哈希)
    severity: str            # extract / review / cross_service / cross_language
    clone_type: str          # T1 / T2 / T3 / T4
    engines: list[str]       # 哪些引擎命中（交叉验证）
    locations: list[Location]# 所有副本位置
    similarity: float        # 0.0-1.0
    saved_lines: int         # 合并后可节省行数
    priority_score: float    # 综合影响评分
    acknowledged: bool       # 是否白名单
    refactoring_hint: str    # reDUP 给的合并建议
```

### §4.3 引擎适配器统一接口

```python
from abc import ABC, abstractmethod

class CloneEngineAdapter(ABC):
    """所有引擎适配器的统一接口。引擎升级/替换不影响编排层。"""

    @abstractmethod
    async def detect(self, files: list[str], config: "EngineConfig") -> list[Finding]:
        """检测给定文件的克隆。返回统一 Finding 列表。"""

    @abstractmethod
    async def index(self, corpus: list[str], config: "EngineConfig") -> None:
        """构建索引底座（L2 用）。"""

    @abstractmethod
    def health_check(self) -> bool:
        """引擎是否可用（二进制/模型是否安装）。"""
```

---

## §5 并发执行与降级策略
<!-- temporal_type: permanent -->

### §5.1 并发调度核心逻辑

```python
async def check(staged_files: list[str]) -> CheckResult:
    """pre-commit 快速路径，3 引擎并发。"""
    timeout = config.pre_commit.timeout_sec

    tasks = []
    if config.pre_commit.engines.echo_guard.enabled:
        tasks.append(_with_timeout(echo_guard.detect(staged_files), timeout))
    if config.pre_commit.engines.ast_grep.enabled:
        tasks.append(_with_timeout(ast_grep.detect(staged_files), timeout))
    if config.pre_commit.engines.redup.enabled:
        tasks.append(_with_timeout(redup.detect(staged_files), timeout))

    results = await asyncio.gather(*tasks, return_exceptions=True)
    findings = aggregator.merge(results, staged_files)

    if any(f.severity == "extract" for f in findings):
        return CheckResult(passed=False, findings=findings)
    return CheckResult(passed=True, findings=findings)
```

### §5.2 降级策略

| 故障场景 | 降级行为 | 理由 |
|---|---|---|
| 单引擎超时/崩溃 | 标记 degraded，其他引擎结果照常用 | 不因单点故障全盘崩溃 |
| 全部超时 | fail-closed 阻断（守项目铁律） | 环境异常必须阻断 |
| CodeSAGE 模型缺失 | L1 不加载模型仍可跑（AST哈希层），L2 跳过嵌入 | L1 零依赖兜底 |
| mcrit 索引未建 | Echo-Guard 内置索引兜底 | 不强依赖底座 |

---

## §6 统一配置方案
<!-- temporal_type: permanent -->

### §6.1 clone_guard.yml（一份配置管所有引擎）

```yaml
# clone_guard.yml — Zephyr CloneGuard 统一配置
version: 1
project_root: .
languages: [python]          # 主语言
ignore:
  - tests/
  - docs/
  - .runtime/
  - "**/_generated/"

# ─── Layer 0: MCP 源头预防 ───
mcp:
  enabled: true
  check_before_write: true   # AI 写函数前强制查重
  model: codesage-small      # 嵌入模型(只装一个,避免冗余)

# ─── Layer 1: pre-commit 拦截 ───
pre_commit:
  timeout_sec: 30
  fail_open: false           # 超时硬阻断(fail-closed,守铁律)
  engines:
    echo_guard:
      enabled: true
      fail_on: extract       # 3+副本硬阻断
      fast_path: true
    ast_grep:
      enabled: true
      rules_dir: clone_guard/rules/
    redup:
      enabled: true
      mode: changed-only
      min_sim: 0.85
      max_groups: 0          # 任一语义重复即阻断

# ─── Layer 2: 周期审计 ───
audit:
  schedule: "0 2 * * *"      # 每日 02:00
  engines:
    mcrit: {enabled: true}
    echo_guard: {enabled: true, full_scan: true}
    redup: {enabled: true, semantic: true, refactor_plan: true}
  output: docs/_working/clone_guard_audit/  # 派生产物,不入git

# ─── Layer 3: 跨边界 ───
compare:
  redup_cross_project: true
  vendetect_cross_repo: false  # 按需手动触发
  relate_prescreen: true

# ─── 严重性映射(统一) ───
severity:
  extract: block              # 3+副本,硬阻断
  review: warn                # 2副本,警告
  cross_service: warn
  cross_language: warn
  acknowledged: skip          # 已确认的合理重复

# ─── 已确认的合理重复(白名单) ───
acknowledged:
  - "src/zephyr/gov_enforcement/commit_gates/_reference_helpers.py::*"
```

**acknowledged 白名单管理规范**（echo-guard CLI + MCP 工具）

白名单条目经 `echo-guard acknowledge` CLI 写入 echo-guard.yml 的 `acknowledged:` 段，标记为 `acknowledged` 严重性（最低，不阻断 CI）。两条调用路径：

- **CLI**：`echo-guard acknowledge <finding_id> --verdict intentional|dismissed --note "<理由>"`
  - `intentional`：保留两份副本（函数变化时重新浮现，非永久豁免）
  - `dismissed`：标记为非重复（永久豁免）
  - `finding_id` 来自 `echo-guard scan --output json`；`--note` **强制必填**——留痕防 AI 滥用白名单消除告警
- **MCP 工具**：`clone_guard.resolve_finding`（`safety_level=M`，写操作需确认）封装上述 CLI，供 AI agent 经 MCP 调用。输入 `finding_id`/`verdict`/`note`，handler 做 schema + 非空校验后调 [`EchoGuardAdapter.acknowledge()`](file:///d:/ZephyrAlpha/src/zephyr/clone_guard/engines/echo_guard_adapter.py)，失败降级返回 `acknowledged=False + degraded=True`，永不抛异常（守 ERROR_CONTRACT）。

副作用与边界：

- **注释丢失警示**：echo-guard CLI 用 PyYAML（safe_load/dump）重写整个 echo-guard.yml，**丢弃所有手工注释**并改引号风格。治本：项目层 [`EchoGuardAdapter._acknowledge_via_roundtrip()`](file:///d:/ZephyrAlpha/src/zephyr/clone_guard/engines/echo_guard_adapter.py) 用 ruamel.yaml round-trip 接管 acknowledged 段写入（保留注释），见 #ARCH-ECHO-GUARD-YML-COMMENT-LOSS。
- **持久化**：acknowledge 仅改工作区 echo-guard.yml，**需经 GitCommitGateway 提交**才持久化；未提交的白名单变更会被 post-commit reconciler restore-to-HEAD 恢复（echo-guard.yml 同 src/ 跟踪文件 restore 约定）。
- **使用边界**：仅对经审慎确认的合理克隆（归档文件间、有意保留的双实现、接口适配层）调用；禁止用于"消除当前不想处理的告警"——属治理逃逸。

### §6.2 ast-grep 业务规则示例

`clone_guard/rules/no-duplicate-try-except.yml`：
```yaml
id: no-duplicate-try-except-wrapper
language: Python
severity: warning
message: 重复的 try-except 包装模式,建议抽取为装饰器或上下文管理器
rule:
  pattern: |
    try:
        $$$BODY
    except Exception as $E:
        logger.error($MSG)
        raise
constraints:
  E: { regex: "^(e|err|exc)$" }
```

---

## §7 严重性映射与门禁集成
<!-- temporal_type: permanent -->

### §7.1 DRY 严重性到门禁阻断映射

| 严重性 | 含义 | 门禁行为 | 对应"强制合并去重"语义 |
|---|---|---|---|
| `extract` | 3+副本，或同文件多重复 | **硬阻断**（commit 失败） | "必须合并" |
| `review` | 2副本 | 警告（记入债，不阻断） | "尽量精简" |
| `cross_service` | 跨服务重复 | 警告 | 跨域合并建议 |
| `cross_language` | 跨语言重复 | 警告 | 跨语言合并建议 |
| `acknowledged` | 已确认合理重复 | 跳过 | 白名单豁免 |

### §7.2 影响评分公式

```
priority_score =
    reDUP.saved_lines × reDUP.similarity     # 收益
  + echo_guard.copy_count × 10               # DRY 违规程度
  - ast_grep.is_business_logic ? 50 : 0      # 业务逻辑加权
  × (1 - acknowledged_ratio)                 # 已确认的打折
```

### §7.3 与现有治理基础设施集成

| 现有设施 | 集成方式 | 守的约束 |
|---|---|---|
| `GitCommitGateway` | 注册升级后的 CAPABILITY-OVERLAP 门禁 | 唯一提交入口 |
| `CAPABILITY-OVERLAP` 门禁 | **升级不新增**，内部调用 CloneGuard check | I-GOV-3 等量退役 |
| `depgraph` | audit 结果写入，标记 `refactor_candidate` | 复用现有依赖图 |
| `reconciler` | warn 模式提醒重复债（不自动 commit） | I-GOV-2 无写权 |
| MCP 基础设施 | 注册 `clone_guard` MCP server | 复用现有注册机制 |
| `architecture_issue_registry.yaml` | 登记 #ARCH-FORCE-MERGE-DEDUP-001 | 铁律#6 引用登记 |

---

## §8 实施阶段（MVP → 完整版）
<!-- temporal_type: permanent -->

### §8.1 Phase A — MVP（2 天，堵 80% 病根）

**只装 Echo-Guard，接入现有门禁**：
1. `pip install "echo-guard[languages,mcp]" onnxscript`  ← onnxscript 非echo-guard声明依赖，torch 2.13+ dynamo ONNX导出器必需，缺则Tier 2静默降级为Tier 1-only
2. `echo-guard setup`（生成 echo-guard.yml）
3. 升级 `CAPABILITY-OVERLAP` 门禁，内部调 `echo-guard check FILES`
4. 注册 MCP：`echo-guard add-mcp`
5. 验证：故意造重复函数，确认被拦截

**收益**：L0（源头预防）+ L1（提交拦截）立即可用，覆盖最常见 AI 造轮子场景。

**交付物**：
- `src/zephyr/clone_guard/engines/echo_guard_adapter.py`
- `src/zephyr/clone_guard/orchestrator.py`（MVP 版，仅调度 Echo-Guard）
- 升级后的 CAPABILITY-OVERLAP 门禁
- `clone_guard.yml`（MVP 版）

### §8.2 Phase B — 深度审计（3 天，发现累积债）

**加 reDUP + ast-grep**：
1. `pip install redup[ast,semantic,lsh] ast-grep`
2. 实现 `redup_adapter.py` + `ast_grep_adapter.py`
3. 写 3-5 条核心 ast-grep 业务规则
4. 实现 `aggregator.py` 结果聚合
5. 配置每日 CI audit 任务

**收益**：L2（周期审计）可用，发现增量漏掉的累积重复，给出重构优先级。

### §8.3 Phase C — 跨边界 + 索引底座（2 天，全链路）

**加 mcrit + Vendetect + relate**：
1. mcrit 建全库 MinHash 索引底座
2. relate 做快速预筛加速器
3. Vendetect 配置跨仓库审计（按需触发）
4. 实现统一 MCP Server，封装各引擎

**收益**：L3（跨边界）可用，四层防御纵深完整。

### §8.4 Phase D — 治理收尾（1 天）

1. 在 `architecture_issue_registry.yaml` 登记 #ARCH-FORCE-MERGE-DEDUP-001
2. 更新 AGENTS.md，写入 CloneGuard 使用规范
3. 配置 `acknowledged` 白名单（合理重复）
4. 全量审计基线，写入 depgraph

**总工期**：8 天（Phase A-D 串行）；Phase A 后即可投产，B/C/D 渐进增强。

---

## §9 验证指标与治本效果
<!-- temporal_type: permanent -->

### §9.1 治本指标

| 病根指标 | 现状 | 目标 | 验证方式 |
|---|---|---|---|
| AI 写函数前查重率 | 0% | 100%（MCP 强制） | MCP 调用日志 |
| 提交时重复拦截率 | 仅 CAPABILITY-OVERLAP 标签匹配 | 语义级 T1-T4 全覆盖 | 故意造重复测试 |
| 累积重复债可见性 | 不可见 | 每日报告 + 趋势 | audit 报告对比 |
| 跨项目重复发现 | 0 | 周期性发现 | compare 报告 |
| 误伤合理重复 | - | 白名单豁免 | acknowledged 列表 |

### §9.2 克隆类型覆盖验证矩阵

| 克隆类型 | 定义 | 检测引擎 | 验证用例 |
|---|---|---|---|
| Type-1 | 完全相同(仅空格/注释不同) | Echo-Guard AST哈希 | 复制函数改缩进 |
| Type-2 | 语法相同(变量名/字面量不同) | Echo-Guard AST哈希 | 复制函数改变量名 |
| Type-3 | 近似克隆(语句增删改) | Echo-Guard CodeSAGE（sim≥0.94阈值；中度改写0.80-0.93不检出） | 复制函数加验证逻辑 |
| Type-4 | 语义克隆(功能相同实现不同) | 嵌入模型根本局限·不可检出（实测冒泡vs归并sim=0.30；reDUP已裁定不装） | 快排 vs 归并排序 |

---

## §10 风险与对策
<!-- temporal_type: permanent -->

| 风险 | 对策 |
|---|---|
| 多引擎结果冲突(A说重复B说不重复) | 聚合器"多数表决 + 严重性就高" |
| pre-commit 延迟过高 | L1 只用快速引擎(AST哈希+规则)，语义层放 L2 |
| CodeSAGE 模型大(200MB) | L1 不加载模型，只 L2 加载；模型缓存 |
| 引擎升级破坏兼容 | Adapter 模式隔离，单引擎升级不影响整体 |
| AI 绕过 MCP 直接写文件 | L1 pre-commit 兜底，两层都不能少 |
| Vendetect AGPL-3.0 传染 | 仅作为独立工具按需调用，不链接进 src/ |
| 治理预算超限 | 升级 CAPABILITY-OVERLAP 不新增门禁(守 I-GOV-3) |

---

## §11 依赖与注册表登记清单
<!-- temporal_type: permanent -->

### §11.1 新增文件登记清单（提交时必须完成）

| 文件 | 注册表 | 登记内容 |
|---|---|---|
| `docs/03_modules/_cross_layer/clone_guard/blueprint.md` | depgraph | 设计态节点 design_maturity=design |
| 同上 | capability_canonical_file_registry.yaml | creation_token |
| 同上 | module_translation_registry.yaml | plain_zh 翻译条目 |
| `src/zephyr/clone_guard/*.py`（Phase A 起） | depgraph + 两个 registry | 同上 |

### §11.2 ARCH 引用登记

- **#ARCH-GOV-BUDGET-001**：已登记（I-GOV-3 等量退役依据）
- **#ARCH-FORCE-MERGE-DEDUP-001**：**待登记**（强制合并去重裁决条目，Phase D）

### §11.3 外部依赖

```
# Phase A
pip install "echo-guard[languages,mcp]" onnxscript   # onnxscript: torch 2.13+ ONNX导出必需，echo-guard 0.4.1未声明(缺则Tier 2静默降级)

# Phase B
pip install redup[ast,semantic,lsh] ast-grep

# Phase C
pip install mcrit relate
# Vendetect 独立安装(AGPL隔离): git clone https://github.com/trailofbits/vendetect
```

---

## §12 后续演进方向
<!-- temporal_type: permanent -->

1. **CodeT5+ 嵌入升级**：当 CodeSAGE 在 Type-4 召回不足时，按 arXiv 2510.15480 切换 CodeT5+110M
2. **TriFusion LLM 仲裁**：对高不确定性样本(0.2%)调 LLM 仲裁，提升 Type-4 F1 至 0.99+
3. **depgraph 自动合并建议**：audit 结果写入 depgraph 后，reconciler 生成合并 PR 草案（仍守 I-GOV-2，warn 不 commit）
4. **跨语言扩展**：当项目引入 JS/TS 前端时，启用 Echo-Guard 跨语言匹配

---

## §13 决策记录
<!-- temporal_type: permanent -->

- **2026-08-06**：蓝图 v0.1.0 创建。全网调研 15+ 工具，定案 6 引擎并发集成 + 四层防御纵深。遵循 I-GOV-3 升级 CAPABILITY-OVERLAP 不新增门禁。MVP(Phase A) 仅用 Echo-Guard，2 天投产堵 80% 病根。

---

## 1. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 1.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/clone_guard/__init__.py` | ✅ 已实现 | |
| `src/zephyr/clone_guard/engines/__init__.py` | ✅ 已实现 | |

### 1.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/clone_guard/__init__.py` | ⚠️ 骨架 | |
| `tests/clone_guard/test_aggregator.py` | ✅ 已实现 | |
| `tests/clone_guard/test_ast_grep_adapter.py` | ✅ 已实现 | |
| `tests/clone_guard/test_config.py` | ✅ 已实现 | |
| `tests/clone_guard/test_echo_guard_adapter.py` | ✅ 已实现 | |
| `tests/clone_guard/test_mcp_server.py` | ✅ 已实现 | |
| `tests/clone_guard/test_mcrit_adapter.py` | ✅ 已实现 | |
| `tests/clone_guard/test_orchestrator.py` | ✅ 已实现 | |
| `tests/clone_guard/test_redup_adapter.py` | ✅ 已实现 | |
| `tests/clone_guard/test_relate_adapter.py` | ✅ 已实现 | |
| `tests/clone_guard/test_vendetect_adapter.py` | ✅ 已实现 | |

### 1.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §1（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下


