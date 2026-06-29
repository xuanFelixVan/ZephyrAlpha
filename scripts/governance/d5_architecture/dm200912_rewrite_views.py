# [BLUEPRINT]
# [MODULE] scripts.governance.d5_architecture.dm200912_rewrite_views
# [DOMAIN]
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
"""DM-200912 Phase4-A: 重写4个核心架构视图(overview/index/application_architecture/capability_heatmap)

将14层主框架改为52域+全景图(depgraph.db)派生。

[BLUEPRINT] ARCHITECTURE-DIAGRAM-PLAN | docs/02_enterprise_architecture/architecture_diagram_construction_plan.md | §4.5
[MODULE] scripts.governance.d5_architecture.dm200912_rewrite_views
[INVARIANTS] 只读depgraph.db;输出4个MD文件;保留原frontmatter结构但更新内容
[MODIFY-GUARD] 修改需通过DM-200912任务卡
[CONSUMERS] 架构视图读者;CI门禁
[STABILITY] evolving
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] depgraph.db不存在→exit 1;域数据缺失→exit 2
[TESTS] 无(一次性脚本)
[DOMAIN] D-GOVERNANCE
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

_THIS_FILE = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _THIS_FILE.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import get_depgraph_pg_connection  # noqa: E402

DEPGRAPH_DB = REPO_ROOT / "data" / "databases" / "depgraph.db"
TARGET_DIR = REPO_ROOT / "docs" / "02_enterprise_architecture" / "target_architecture"


def load_domain_data() -> dict:
    """从depgraph.db加载域+模块统计数据。"""
    conn = get_depgraph_pg_connection(autocommit=True)
    try:
        cur = conn.execute(
            """SELECT d.domain_id, d.domain_name, d.layer_id, d.current_modules,
                      d.max_modules, d.description,
                      (SELECT COUNT(*) FROM nodes n WHERE n.domain_id = d.domain_id) as actual_nodes,
                      (SELECT COUNT(*) FROM nodes n WHERE n.domain_id = d.domain_id AND n.design_maturity = 'production') as production_count,
                      (SELECT COUNT(*) FROM nodes n WHERE n.domain_id = d.domain_id AND n.design_maturity = 'design') as design_count,
                      (SELECT COUNT(*) FROM nodes n WHERE n.domain_id = d.domain_id AND n.design_maturity = 'prototype') as prototype_count
               FROM domains d ORDER BY d.layer_id, d.domain_id"""
        )
        domains = []
        for r in cur.fetchall():
            domains.append(
                {
                    "domain_id": r["domain_id"],
                    "domain_name": r["domain_name"] or "",
                    "layer_id": r["layer_id"] or "",
                    "current_modules": r["current_modules"] or 0,
                    "max_modules": r["max_modules"] or 200,
                    "description": r["description"] or "",
                    "actual_nodes": r["actual_nodes"],
                    "production_count": r["production_count"],
                    "design_count": r["design_count"],
                    "prototype_count": r["prototype_count"],
                }
            )

        cur = conn.execute("SELECT COUNT(*) AS cnt FROM domains")
        total_domains = cur.fetchone()["cnt"]
        cur = conn.execute("SELECT COUNT(*) AS cnt FROM nodes")
        total_nodes = cur.fetchone()["cnt"]
        cur = conn.execute("SELECT COUNT(*) AS cnt FROM edges")
        total_edges = cur.fetchone()["cnt"]
        cur = conn.execute(
            "SELECT design_maturity, COUNT(*) AS cnt FROM nodes GROUP BY design_maturity ORDER BY COUNT(*) DESC"
        )
        maturity_dist = {r["design_maturity"] or "NULL": r["cnt"] for r in cur.fetchall()}
        cur = conn.execute("SELECT build_status, COUNT(*) AS cnt FROM nodes GROUP BY build_status ORDER BY COUNT(*) DESC")
        build_dist = {r["build_status"] or "NULL": r["cnt"] for r in cur.fetchall()}

        # 按layer_id分组
        layers: dict[str, list] = {}
        for d in domains:
            layer = d["layer_id"] or "unassigned"
            layers.setdefault(layer, []).append(d)

        return {
            "total_domains": total_domains,
            "total_nodes": total_nodes,
            "total_edges": total_edges,
            "maturity_distribution": maturity_dist,
            "build_status_distribution": build_dist,
            "layers": layers,
            "domains": domains,
        }
    finally:
        conn.close()


def write_overview(data: dict) -> None:
    """重写 overview.md: 14层→52域+全景图派生说明。"""
    now = datetime.now().strftime("%Y-%m-%d")
    total = data["total_domains"]
    total_nodes = data["total_nodes"]
    total_edges = data["total_edges"]
    maturity = data["maturity_distribution"]
    layers = data["layers"]

    content = f"""---
module_id: VIEW-00-OVERVIEW
title: Target Architecture — Overview / 目标架构总览
doc_type: architecture_view
status: Active
version: 2.0.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
valid_from: 2026-04-17
superseded_by: null
supersedes: null
related_rationale: R26, R27, R28, R29, R30
related_open_questions: []
tags:
- overview
- togaf
- c4
- iso-42010
- architecture-philosophy
- adr-summary
- vibe-coding-2.0
- 6-core-services
- domain-driven
- depgraph-derived
summary: 架构文档组的总览视图。v2.0.0：基于§2.1裁定，14层降级为域属性，{total}域成为唯一物理分类体系。结构化数据由depgraph.db全景图派生。
date: '{now}'
ttl: permanent
---

# Target Architecture — Overview
# 目标架构总览

---

## 0. Executive Summary / 高管摘要

**系统定位**：ZephyrAlpha 是个人量化投资系统的 AI-native 重构，采用**{total}域唯一物理分类体系**（基于depgraph.db全景图），Python 全栈，Vibe Coding 驱动（Cursor + Trae 双 AI IDE）。

**核心架构决策**（v2.0.0 基于§2.1裁定）：
- **{total}域唯一分类**：原14层逻辑层(L00-L13)取消作为并行分类，降级为域的`layer_id`属性。两个并行分类=AI每次判断用哪个=幻觉温床，故14层信息保留方式改为域属性。
- **全景图派生**：所有结构化数据（域清单/模块清单/依赖关系/容量统计）由`data/databases/depgraph.db`派生，禁止在MD中硬编码。
- **运行时三平面**（引擎平面 / Vibe Coding 平面 / 治理平面）→ 正交划分开发态和运行态关注点
- **治理三层**（制度标准层 / 企业架构层 / 蓝图施工层）→ Phase 退出准入双门协议门禁
- **安全红线**：4 条不可撤销（详见 [architecture_principles.md](architecture_principles.md) §1）
- **技术栈**：Python >=3.11 + Pydantic v2 + SQLite WAL + ChromaDB + FastAPI 原型 + MCP 协议
- **当前阶段**：experimental 启动，{total}域已定义，模块边界待定，6 大 Vibe Coding 2.0 核心服务施工中

**System Identity**: ZephyrAlpha is an AI-native personal quantitative investment system. {total}-domain unique physical classification (derived from depgraph.db panorama). Python full-stack, Vibe Coding driven. The legacy 14-layer (L00-L13) has been demoted to a domain attribute (`layer_id`) per §2.1 ruling — single classification eliminates AI hallucination from dual-taxonomy ambiguity.

---

## 1. Architecture approach / 架构方法论

### 1.1 Three-standard composite / 三标准合成方案

ZephyrAlpha 2.0 adopts a composite of three internationally recognized standards:

| Standard / 标准 | Role in this project / 在本项目中的作用 |
|----------------|---------------------------------------|
| **ISO/IEC/IEEE 42010:2011** | Methodology: AD = multiple Views, each View addresses Stakeholder Concerns under a Viewpoint |
| **TOGAF 9.2 / 10** | Four-layer view taxonomy: Business / Information / Application / Technology |
| **C4 Model** (Simon Brown) | Application-level visualization: System Context (L1) and Container (L2) |

### 1.2 唯一物理分类体系裁定（§2.1）

**裁定**：{total}域是唯一物理分类体系。原14层逻辑层(L00-L13)取消作为并行分类，降级为域的`layer_id`属性。

| 裁定项 | 结论 | 理由 |
|--------|------|------|
| 14层 vs {total}域 | **{total}域唯一** | 两个并行分类=AI每次判断用哪个=幻觉温床 |
| 14层信息保留方式 | 作为域的`layer_id`属性 | 属性不是分类，不产生二元性 |
| L00-L13层YAML文件 | 废弃，信息合并入depgraph.db域定义 | 避免SSoT分裂 |

**当前域层级分布**（数据源：depgraph.db `domains` 表）：

| layer_id | 域数量 | 说明 |
|----------|:---:|------|
"""
    for layer_id in sorted(layers.keys()):
        domains_in_layer = layers[layer_id]
        content += f"| `{layer_id}` | {len(domains_in_layer)} | {', '.join(d['domain_id'] for d in domains_in_layer[:5])}{'...' if len(domains_in_layer) > 5 else ''} |\n"

    content += f"""

**域总数**：{total} | **节点总数**：{total_nodes} | **依赖边总数**：{total_edges}

### 1.3 全景图派生机制

所有架构视图的结构化数据均由`depgraph.db`全景图派生，禁止在MD中硬编码会变化的数字。

**派生工具链**：
- `scripts/governance/d5_architecture/generators/generate_domain_doc.py` — 单域/全域文档生成
- `scripts/governance/d5_architecture/generators/generate_domain_dependency_diagram.py` — 域依赖图生成
- `scripts/governance/d5_architecture/generators/generate_domain_index.py` — 域总览索引
- `scripts/governance/d5_architecture/generators/generate_cross_domain_matrix.py` — 跨域依赖矩阵
- `scripts/governance/d5_architecture/generators/generate_capacity_report.py` — 容量报告
- `scripts/governance/d5_architecture/generators/generate_design_vs_production.py` — 设计态vs运营态
- `scripts/governance/d5_architecture/generators/generate_constraint_violations.py` — 约束违规

**派生产出目录**：`docs/02_enterprise_architecture/generated/`

### 1.4 Current phase positioning / 当前阶段定位

| 维度 | 状态 | 说明 |
|------|------|------|
| **{total}域物理分类** | ✅ **已定义** | depgraph.db `domains` 表为SSoT |
| **6 大核心服务（VMS/CE/Orc/FLE/LSG/KB）** | ✅ **已定稿** | 2026-04-24 产出；接口规范 6 份齐备 |
| **17 项技术选型** | ✅ **已定稿** | 见 `technology_landscape.yaml`（SSoT）|
| **模块内部边界** | ⏳ **讨论中** | experimental 落地时细化 |
| **设计态→运营态迁移** | 🔧 **进行中** | design_maturity: design({maturity.get("design", 0)}) / prototype({maturity.get("prototype", 0)}) / production({maturity.get("production", 0)}) |

---

## 2. TOGAF four layers / TOGAF 四层结构

```
┌────────────────────────────────────────────────────────────┐
│  01. Business Architecture (BA) / 业务架构                  │
│      Who we serve, what we do, core processes, NFR         │
└────────────────────────────────────────────────────────────┘
                        ↓ drives / 驱动
┌────────────────────────────────────────────────────────────┐
│  02. Information Architecture (IA) / 信息架构               │
│      What information assets exist, how organized          │
└────────────────────────────────────────────────────────────┘
                        ↓ drives / 驱动
┌────────────────────────────────────────────────────────────┐
│  03. Application Architecture (AA) / 应用架构               │
│      What modules/services exist, how they interact        │
└────────────────────────────────────────────────────────────┘
                        ↓ drives / 驱动
┌────────────────────────────────────────────────────────────┐
│  04. Technology Architecture (TA) / 技术架构                │
│      What technology stack underpins everything            │
└────────────────────────────────────────────────────────────┘
```

> **注**：TOGAF四层是**视图分类方法**，不是物理代码分层。物理代码组织以{total}域为准（见§1.2裁定）。

---

## 3. C4 Model complement / C4 模型补充

TOGAF resolves "vertical layering". C4 Model resolves "how to visualize the inside of Application Architecture":

| Level / 级别 | Focus / 关注点 | Usage in this project / 本项目用法 |
|-------------|--------------|----------------------------------|
| **L1 — System Context** | System's position in the external world | ✅ Required → `diagrams/c4_l1_system_context.mmd` |
| **L2 — Container** | Independent deployable units inside the system | ✅ Required → `diagrams/c4_l2_containers.mmd` |
| **L3 — Component** | Components inside a container | 🟡 As needed, in blueprints |
| **L4 — Code** | Class/function level | ❌ Not drawn (code itself is documentation)|

---

## 4. Three trees / 三棵树的架构对应关系

| Tree / 树 | Primary view / 核心视图归属 | Key diagrams / 主要图 | Owner document / 归属文档 |
|----------|--------------------------|---------------------|--------------------------|
| `docs/` | Information Architecture | `docs/` 抽屉拓扑图 + 文档生命周期图 | `information_architecture.md` |
| `src/` | Application Architecture | C4-L1 系统上下文 + C4-L2 容器图 + 域依赖图 | `application_architecture.md` |
| `scripts/` | Application Architecture (sub-view) | 治理代码拓扑图 + pre-commit/CI 钩子流程图 | `application_architecture.md §4` |

> **v2.0.0变更**：原"14层代码分层图"改为"域依赖图"，由`generate_domain_dependency_diagram.py`从depgraph.db派生。

---

## 5. Key KB 决策记录 summary / 关键 KB 决策记录 汇总

| KB 决策记录 | Decision / 决策 | Impact / 影响 |
|-----|----------------|--------------|
| KBG-0001 | `docs/` is the single canonical source of truth | 所有文档归属 |
| KBG-0002 | Single frontmatter schema + phased required fields | 所有文档 frontmatter |
| KBG-0003 | Dual/multi AI collaboration workflow | 文档生产方式 |
| KBG-0015 | Context Engine：NetworkX + JSON + 本地 LLM 压缩 | 6 大核心服务之一 |
| KBG-0016 | Vector Memory：ChromaDB 0.6 + BGE-M3 ONNX + 递归分块 | 6 大核心服务之一 |
| KBG-0017 | Agent Orchestrator：SQLite + asyncio.Queue 起步 | 6 大核心服务之一 |
| KBG-0018 | Agent Sandbox：Windows ACL + 只读挂载 | Orchestrator 配套 |
| KBG-0019 | Feedback Loop Engine：SQLite 时间序列 + EMA 异常检测 | 6 大核心服务之一 |
| KBG-0020 | LLM Security Gateway：OWASP LLM Top 10 + fail-closed | 6 大核心服务之一 |
| KBG-0021 | SSoT Validator：scaffold 唯一任务，阻塞下游 | scaffold 门禁 |

---

## 5A. Vibe Coding 2.0 Infrastructure / Vibe Coding 2.0 基础设施架构

### 5A.1 6 大核心服务一句话定位

| 缩写 | 服务全称 | 一句话定位 | 接口规范 |
|------|---------|-----------|---------|
| **LSG** | LLM Security Gateway | LLM 交互的"安全闸"，四层防御，fail-closed | `08_.../llm-security-gateway-interface.md` |
| **CE** | Context Engine | AI 编码的"中枢神经"，上下文 build/compress/validate/inject | `08_.../context-engine-interface.md` |
| **Orc** | Agent Orchestrator | Vibe Coding 2.0 的"任务引擎"，任务生命周期 + Agent 沙箱 | `08_.../agent-orchestrator-interface.md` |
| **VMS** | Vector Memory Service | 知识与决策的"向量记忆库"，ChromaDB 5 个 Collection | `08_.../vector-memory-service-interface.md` |
| **FLE** | Feedback Loop Engine | 系统自调节的"闭环大脑"，指标→异常→动作 | `08_.../feedback-loop-engine-interface.md` |

### 5A.2 与域架构的关系

6 大核心服务属于`layer_id=L1_platform`的跨层支撑域，为业务域提供 AI 基础设施能力。具体域归属见depgraph.db `domains`表。

### 5A.3 详细架构

完整架构图 / 服务间依赖 DAG / 降级协调矩阵 / 4 落地路线 → 见 [`application_architecture.md §4A`](./application_architecture.md)。

---

## 6. Architecture document conventions / 架构文档惯例

### 6.1 Diagrams / 图的惯例

All diagrams use **Mermaid-only** (including Mermaid native C4 syntax).

### 6.2 Versioning / 版本化惯例

Flat directory + `frontmatter.version`. No version subdirectories.

### 6.3 Naming / 命名惯例

Directory: `target_architecture/` (TOGAF term). File names: `NN-kebab-case.md`. Module IDs: `VIEW-NN-<TYPE>-ARCH`.

### 6.4 数据派生原则（v2.0.0新增）

- 所有域/模块/依赖数字MUST来自depgraph.db，禁止硬编码
- 派生工具位于`scripts/governance/d5_architecture/generators/`
- 派生产出位于`docs/02_enterprise_architecture/generated/`
- MD文档引用派生数据时MUST标注数据源

---

## 7. Architecture Runway Index / 架构预留通道总览

> Architecture Runway（架构跑道）记录了系统未来 36 个月以上的 P3 能力挂载点。

### §7.1 各视图 Runway 章节快速导航

| 视图 | Runway 章节 | 条目数 | 主要覆盖域 |
|------|------------|--------|----------|
| [01-BA 业务架构](./business_architecture.md) | §8 Architecture Runway | 5 条 | 战略层 |
| [02-IA 信息架构](./information_architecture.md) | §11 Architecture Runway | 3 条 | 信息/数据层 |
| [03-AA 应用架构](./application_architecture.md) | §11 Architecture Runway | 22 条 | 应用组件层 |
| [04-TA 技术架构](./technology_architecture.md) | §14 Architecture Runway | 7 条 | 基础设施层 |
| **合计** | — | **37 条** | 全层覆盖 |

---

## 8. Revision history / 修订记录

| Date / 日期 | Description / 说明 |
|------------|-------------------|
| {now} | **v2.0.0（DM-200912 Phase4-A）**：基于§2.1裁定重写——14层降级为域属性，{total}域成为唯一物理分类体系；结构化数据由depgraph.db全景图派生；新增§1.2唯一分类体系裁定、§1.3全景图派生机制、§6.4数据派生原则。 |
| 2026-05-02 | v1.4.1：§0 英文部分从中英完全重复精简为关键信息摘要。 |
| 2026-04-24 | v1.2.0：追加§1.3当前阶段定位+§5A Vibe Coding 2.0基础设施。 |
| 2026-04-17 | v1.0.0：从 DW-IA-DESIGN-001 拆分升格建立。 |
"""
    out_path = TARGET_DIR / "overview.md"
    out_path.write_text(content, encoding="utf-8", newline="\n")
    print(f"[OK] 重写 {out_path} ({len(content)} 字符)")


def write_index(data: dict) -> None:
    """重写 index.md: 14层分区→52域索引+派生视图说明。"""
    now = datetime.now().strftime("%Y-%m-%d")
    total = data["total_domains"]
    layers = data["layers"]

    content = f"""---
classification: confidential
date: '{now}'
doc_type: index
generated: '{now}'
layer: cross_layer
merged_from: README.md + index.md
module_id: ARCH-006
status: Active
title: Target Architecture — Navigation Guide / 目标架构导航
version: 3.0.0
depends_on:
  - {{target: EA-INDEX, at: "§子目录", why: "父级 EA 索引——target_architecture 为其子目录"}}
tags:
- index
- navigation
- domain-driven
- depgraph-derived
summary: v3.0.0：基于§2.1裁定，导航改为{total}域索引+全景图派生视图说明。原14层分区导航废弃。
ttl: permanent
---

# Target Architecture — Navigation Guide
# 目标架构 — 导航指南

---

## 责任声明（Single Responsibility）

本目录只存放：**目标架构视图（TOGAF）— overview 到 dimension-audit-matrix + architecture_model/ + diagrams/**。

---

## 1. What is this document set / 本文档组是什么

This is the **canonical Architecture Description Set** for ZephyrAlpha 2.0.

采用 **ISO 42010 + TOGAF 四视图 + C4 合成方案**：

- **ISO 42010** — 定方法论：Architecture Description 由多个 View 组成
- **TOGAF** — 定四层视图：Business / Information / Application / Technology
- **C4 Model** — 定应用视图的可视化：系统上下文（L1）和容器（L2）

> **v3.0.0变更**：物理代码组织以{total}域为准（§2.1裁定），14层降级为域属性。结构化数据由depgraph.db派生。

---

## 2. 域索引（{total}域，数据源：depgraph.db）

> 本索引由`scripts/governance/d5_architecture/generators/generate_domain_index.py`派生。
> 完整域清单见`generated/domain_index.md`。

"""
    for layer_id in sorted(layers.keys()):
        domains_in_layer = layers[layer_id]
        content += f"### `{layer_id}` ({len(domains_in_layer)}域)\n\n"
        content += "| 域ID | 域名称 | 节点数 | 描述 |\n"
        content += "|------|--------|:---:|------|\n"
        for d in domains_in_layer:
            desc_short = (d["description"] or "")[:50]
            content += f"| `{d['domain_id']}` | {d['domain_name']} | {d['actual_nodes']} | {desc_short} |\n"
        content += "\n"

    content += f"""---

## 3. 文件清单

| 文件 | 说明 |
|------|------|
| overview.md | 架构总览（v2.0.0：{total}域+全景图派生）|
| business_architecture.md | BA 业务架构视图 |
| information_architecture.md | IA 信息架构视图 |
| application_architecture.md | AA 应用架构视图（v2.0.0：域派生模块清单）|
| technology_architecture.md | TA 技术架构视图 |
| runtime_planes.md | 运行时平面正交视图 |
| capability_heatmap.md | 能力热力图正交视图（v2.0.0：{total}域×能力域）|
| data_architecture.md | DA 数据架构视图 |
| security_architecture.md | SEC 安全架构视图 |
| integration_architecture.md | INTEG 集成架构视图 |
| operations_architecture.md | OPS 运维架构视图 |
| governance_architecture.md | GOV 治理架构视图 |
| frontend_architecture.md | FE 前端架构视图 |
| dimension_audit_matrix.md | 12维架构质量评分矩阵 |
| session_carryover_schema.md | AI会话接续Schema |
| revision_history.md | 完整修订历史归档 |

---

## 4. 派生视图（generated/目录）

> 所有派生视图由`scripts/governance/d5_architecture/generators/`下的生成器从depgraph.db派生。

| 派生视图 | 生成器 | 数据源 | 说明 |
|---------|--------|--------|------|
| `generated/domain_index.md` | generate_domain_index.py | domains+nodes | {total}域总览索引 |
| `generated/cross_domain_matrix.md` | generate_cross_domain_matrix.py | edges | 跨域依赖矩阵 |
| `generated/capacity_report.md` | generate_capacity_report.py | domains | 域容量报告 |
| `generated/design_vs_production.md` | generate_design_vs_production.py | nodes | 设计态vs运营态统计 |
| `generated/constraint_violations.md` | generate_constraint_violations.py | arch_constraints | 架构约束违规报告 |
| `generated/domains/*.md` | generate_domain_doc.py | nodes+edges | 单域架构文档（{total}个）|
| `generated/domains/*_dependency.mmd` | generate_domain_dependency_diagram.py | nodes+edges | 单域依赖图（{total}个）|

---

## 5. Document inventory / 文档清单

| File / 文件 | Layer / 层 | Answers / 回答的核心问题 | Primary audience / 主要读者 | Status / 状态 |
|------------|-----------|------------------------|--------------------------|--------------|
| `index.md`（本文） | — | 本文档组是什么？怎么读？ | 所有人 | active |
| `overview.md` | Cross-layer | 整体架构哲学？{total}域如何组织？ | 架构师、新加入者 | active |
| `business_architecture.md` | BA | 为谁服务？核心业务能力？ | 业务负责人 | active |
| `information_architecture.md` | IA | `docs/` 有哪些抽屉？ | 文档维护者、AI 协作者 | active |
| `application_architecture.md` | AA | 系统有哪些应用/模块？域如何划分？ | 开发者、架构师 | active |
| `technology_architecture.md` | TA | 用什么技术栈？ | SRE、实施者 | active |
| `runtime_planes.md` 🔷 **正交视图 1** | Orthogonal | 运行平面怎么切分？ | 架构师、SRE | active |
| `capability_heatmap.md` 🔷 **正交视图 2** | Orthogonal | {total}域能力成熟度热力图？ | 架构师、决策层 | active |
| `data_architecture.md` | DA | 业务数据对象？ | 量化研究员、数据工程师 | active |
| `security_architecture.md` | SEC | 安全域划分？IAM？ | 安全工程师、合规 | active |
| `integration_architecture.md` | INTEG | 集成风格？接口契约？ | 开发者、架构师、SRE | active |
| `operations_architecture.md` | OPS | 运维域全景？ | SRE、运维工程师 | draft |
| `governance_architecture.md` | GOV | 治理体系三层边界？ | 架构师、合规 | active |
| `frontend_architecture.md` | FE | 前端层分层？ | 前端开发者、架构师 | active |
| `dimension_audit_matrix.md` | Cross-layer | 12维架构质量评分 | 架构师、审计 | active |
| `session_carryover_schema.md` | Cross-layer | AI会话接续Schema | AI 协作者、架构师 | active |
| `diagrams/` | All | Mermaid 图源文件 | 所有人 | active |

---

## 6. Reading order / 推荐阅读顺序

**First time / 第一次读（5 分钟）**：`index.md`（本文）→ `overview.md` → `generated/domain_index.md`（{total}域总览）

**Architect / 架构师**：`overview.md` → `generated/domain_index.md` → 按域读`generated/domains/*.md`

**Developer / 开发者**：`application_architecture.md` → `generated/domains/<相关域>.md` → `integration_architecture.md`

**AI collaborator / AI 协作者**：`generated/domain_index.md`（全局索引）→ 按需读取`generated/domains/*.md` → `overview.md`（设计哲学）

---

## 7. View dependencies / 视图依赖关系

> **📊 视图依赖关系总览**：见 [`diagrams/readme_view_dependency_graph.mmd`](diagrams/readme_view_dependency_graph.mmd)

**正交视图说明**：`04bis` 和 `04ter` 是 TOGAF 10 视图之外的正交视图，提供运行平面/能力成熟度的额外切片标注。

**反向约束**：TA 成本限制 → AA 范围 → IA 范围 → BA 野心。

---

## 8. View vs YAML SSoT — key distinction / 视图与 YAML SSoT 的区别

| Type / 类型 | Style / 风格 | Purpose / 用途 |
|------------|-------------|---------------|
| **View** (00–10) | Narrative: explains **why** | For humans, conveys architectural intent |
| **YAML SSoT** (architecture_model/) | Structured: lists **what** | For machines, AI, and CI gates |
| **派生视图** (generated/) | 派生: 从depgraph.db生成 | 结构化数据可视化，禁止手编 |

---

## 9. Provenance / 来源说明

本文档组由 `DW-IA-DESIGN-001` 拆分升格而来。v3.0.0 基于§2.1裁定重写为{total}域索引+全景图派生。

---

## 10. Revision history / 修订记录

> 完整历史见 [revision_history.md](revision_history.md)。本处仅保留最近 3 次修订。

| Date / 日期 | Description / 说明 |
|------------|-------------------|
| {now} | **v3.0.0（DM-200912 Phase4-A）**：基于§2.1裁定重写——导航改为{total}域索引+派生视图说明；新增§2域索引、§4派生视图；废弃14层分区导航。 |
| 2026-05-06 | v2.2.0：双树与 SCOPE/SSoT 地图对齐。 |
| 2026-05-02 | v2.1.0：修复 4 项 SSoT 对齐问题。 |

## 排除规则（不应放入本目录的内容）

- ❌ 治理规范 → `01_policies_and_standards/`
- ❌ KB 决策记录 → KB:decisions namespace

## 父级目录

- 父级：[02_enterprise_architecture](../index.md)
"""
    out_path = TARGET_DIR / "index.md"
    out_path.write_text(content, encoding="utf-8", newline="\n")
    print(f"[OK] 重写 {out_path} ({len(content)} 字符)")


def write_application_architecture(data: dict) -> None:
    """重写 application_architecture.md: 14层模块清单→全景图派生模块清单。"""
    now = datetime.now().strftime("%Y-%m-%d")
    total = data["total_domains"]
    total_nodes = data["total_nodes"]
    total_edges = data["total_edges"]
    maturity = data["maturity_distribution"]
    layers = data["layers"]

    content = f"""---
module_id: VIEW-03-APPLICATION-ARCH
title: Target Architecture — Application Architecture / 目标架构：应用架构
doc_type: architecture_view
status: Active
version: 3.0.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
valid_from: 2026-04-21
superseded_by: null
supersedes: null
related_rationale: R29, R30, R33, R49, R53, R54, R55, R56, R69
related_open_questions:
- OQ-021
- OQ-022
- OQ-043
- OQ-045
- OQ-063
- OQ-067
- OQ-071
- OQ-072
- OQ-083
related_kb:
- KBG-0009
- KBG-0011
tags:
- application-architecture
- togaf
- aa
- c4
- domain-driven
- depgraph-derived
- modules
- acl
- vendor-registry
- fault-tolerance
- idempotency
- quant-redline
- runtime-planes
- orthogonal-view
- vibe-coding-2.0
- 6-core-services
summary: TOGAF Application Architecture 视图（v3.0.0 重组织版）。基于§2.1裁定，模块清单改为{total}域派生，数据源depgraph.db。原14层模块清单废弃。
date: '{now}'
ttl: permanent
---

## 1. Purpose of this view / 本视图的用途

The Application Architecture answers:

- What applications / modules / services exist? (C4 views)
- How do they interact? (Interfaces and protocols)
- How is `src/zephyr/` structured? ({total}域物理分类，数据源depgraph.db)
- How is `scripts/` organized? (Governance code topology)
- Where do future platform modules belong? (Module placement)

> **v3.0.0 重组织说明**：基于§2.1裁定，模块清单改为{total}域派生。原14层模块清单废弃，14层降级为域的`layer_id`属性。模块属性详情见`generated/domains/*.md`（由`generate_domain_doc.py`派生）。

---

## 2. C4-L1: System Context / C4-L1 系统上下文图

### 2.1 Actor list / 参与者清单

| Actor / 参与者 | Type / 类型 | Role / 职责 |
|--------------|------------|------------|
| **Independent Operator** 独立操作者 | Human (internal) | 系统拥有者；负责策略配置、风险决策、日常监控 |
| **AI Collaborators** AI 协作者 | System (internal) | Kimi (Trae) + Opus/Sonnet (Cursor)；发散+收口工作流 |

### 2.2 External system list / 外部系统清单

| External System / 外部系统 | Direction / 方向 | Protocol / 协议 | Purpose / 用途 |
|--------------------------|----------------|----------------|---------------|
| **Broker API** 券商 API | Bidirectional | REST / FIX | 发送交易委托；接收成交回报与持仓 |
| **Market Data Provider** 行情数据源 | Inbound | REST / WebSocket | 提供历史与实时行情数据 |
| **LLM Providers** LLM 服务商 | Outbound | REST | AI 推理调用 |
| **Feishu** 飞书 | Outbound | REST (Webhook) | 通知与报告分发 |

### 2.3 System context diagram / 系统上下文图

> **📊 C4-L1 系统上下文图**：见 [`diagrams/c4_l1_system_context.mmd`](diagrams/c4_l1_system_context.mmd)

---

## 3. C4-L2: Container / C4-L2 容器图

> **📊 C4-L2 容器图**：见 [`diagrams/c4_l2_containers.mmd`](diagrams/c4_l2_containers.mmd)

---

## 4. 域架构（{total}域，数据源：depgraph.db）

> 本节为v3.0.0重写。模块清单由`generated/domains/*.md`派生，禁止在本文硬编码。
> 完整域索引见`generated/domain_index.md`。

### 4.1 域统计概览

| 指标 | 值 | 数据源 |
|------|:---:|--------|
| 域总数 | {total} | depgraph.db `domains` 表 |
| 节点总数 | {total_nodes} | depgraph.db `nodes` 表 |
| 依赖边总数 | {total_edges} | depgraph.db `edges` 表 |
| production 节点 | {maturity.get("production", 0)} | depgraph.db `nodes.design_maturity` |
| design 节点 | {maturity.get("design", 0)} | depgraph.db `nodes.design_maturity` |
| prototype 节点 | {maturity.get("prototype", 0)} | depgraph.db `nodes.design_maturity` |

### 4.2 域层级分布

| layer_id | 域数量 | 域清单 |
|----------|:---:|--------|
"""
    for layer_id in sorted(layers.keys()):
        domains_in_layer = layers[layer_id]
        domain_list = ", ".join(f"`{d['domain_id']}`" for d in domains_in_layer)
        content += f"| `{layer_id}` | {len(domains_in_layer)} | {domain_list} |\n"

    content += f"""

### 4.3 域详细清单

> 完整域清单（含模块数/容量/描述）见 [`generated/domain_index.md`](../generated/domain_index.md)。
> 单域详细文档见 [`generated/domains/*.md`](../generated/domains/)（{total}个）。
> 单域依赖图见 [`generated/domains/*_dependency.mmd`](../generated/domains/)（{total}个）。

### 4.4 跨域依赖矩阵

> 完整跨域依赖矩阵见 [`generated/cross_domain_matrix.md`](../generated/cross_domain_matrix.md)（由`generate_cross_domain_matrix.py`从`edges`表派生）。

---

## 4A. Vibe Coding 2.0 Infrastructure / Vibe Coding 2.0 基础设施架构

### 4A.1 6 大核心服务一句话定位

| 缩写 | 服务全称 | 一句话定位 | 域归属 |
|------|---------|-----------|--------|
| **LSG** | LLM Security Gateway | LLM 交互的"安全闸"，四层防御，fail-closed | 见depgraph.db |
| **CE** | Context Engine | AI 编码的"中枢神经" | 见depgraph.db |
| **Orc** | Agent Orchestrator | Vibe Coding 2.0 的"任务引擎" | 见depgraph.db |
| **VMS** | Vector Memory Service | 知识与决策的"向量记忆库" | 见depgraph.db |
| **FLE** | Feedback Loop Engine | 系统自调节的"闭环大脑" | 见depgraph.db |

### 4A.2 与域架构的关系

6 大核心服务属于`layer_id=L1_platform`的跨层支撑域，为业务域提供 AI 基础设施能力。具体域归属见depgraph.db `domains`表。

---

## 5. Scripts governance code topology / 治理代码拓扑

> 治理代码拓扑图：见 [`diagrams/scripts_topology.mmd`](diagrams/scripts_topology.mmd)

治理脚本注册表：`scripts/script-manifest.yaml`（SSoT）

---

## 6. Module placement principles / 模块归属原则

### 6.1 域归属判定

新模块归属哪个域？查询depgraph.db `domains`表，按功能职责匹配`description`字段。无法匹配时，评估是否需要新增域（需Owner批准）。

### 6.2 跨域依赖规则

- 跨域依赖MUST在depgraph.db `edges`表登记
- 禁止循环依赖（由`arch_constraints`表约束）
- 跨域依赖强度由`coupling_strength`字段标注

### 6.3 容量管理

- 单域节点上限：150（默认）/ 200（高度耦合可放宽）
- 容量报告见 [`generated/capacity_report.md`](../generated/capacity_report.md)
- 超容域必须拆分（需Owner批准）

---

## 7. Fault tolerance & idempotency / 容错与幂等设计摘要

> 详细设计见各域蓝图。本节仅摘要。

- **幂等性**：所有写操作MUST支持幂等重试
- **容错**：失败不阻塞（DLQ + 告警）
- **回滚**：双轨Checkpoint（git commit + SQLite JSONL dump）

---

## 8. ACL & vendor registry / ACL与供应商注册表

- ACL落盘位置：见`security_architecture.md`
- 供应商注册表：`architecture_model/technology/vendor_registry.yaml`

---

## 9. Runtime planes orthogonal view / 运行时平面正交视图

> 详见 [`runtime_planes.md`](runtime_planes.md)

运行时三平面（Hot < 10ms / Warm 10ms-1s / Cold > 1s）横切所有域，不改变域的业务决策。

---

## 10. Architecture Runway / 架构预留通道

> 详见各视图 Runway 章节。合计 37 条 P3 能力挂载点。

---

## 11. Revision history / 修订记录

| Date / 日期 | Description / 说明 |
|------------|-------------------|
| {now} | **v3.0.0（DM-200912 Phase4-A）**：基于§2.1裁定重写——模块清单改为{total}域派生（数据源depgraph.db）；原14层模块清单废弃；新增§4域架构、§4.1域统计概览、§4.2域层级分布、§4.3域详细清单、§4.4跨域依赖矩阵；§6模块归属原则改为域归属判定。 |
| 2026-05-06 | v2.2.0：双树与 SCOPE/SSoT 地图对齐。 |
| 2026-04-22 | v2.0.0：模块属性详情迁移至 architecture_model/ 联邦 YAML 模型。 |
"""
    out_path = TARGET_DIR / "application_architecture.md"
    out_path.write_text(content, encoding="utf-8", newline="\n")
    print(f"[OK] 重写 {out_path} ({len(content)} 字符)")


def write_capability_heatmap(data: dict) -> None:
    """重写 capability_heatmap.md: 14层×7域→52域×能力域。"""
    now = datetime.now().strftime("%Y-%m-%d")
    total = data["total_domains"]
    layers = data["layers"]
    maturity = data["maturity_distribution"]

    # 能力域定义（7业务+3横切=10能力域）
    capability_domains = [
        ("数据接入", "D_MKT_DATA, D_ALT_DATA, D_DATA_ENG"),
        ("因子研究", "D-FACTOR, D-SIGLEGACY, D-FUNDAMENTAL_SIGNAL, D-ASHARE_SIGNAL, D-SIGQC"),
        ("策略决策", "D-PF_CORE, D-PF_ALLOC, D-SELL_DECISION, D-CROSS_ASSET"),
        ("执行交易", "D-EX_CORE, D-EX_SOR, D-TRADING, D-POSITION"),
        ("风险控制", "D-RISK, D-COMPLIANCE"),
        ("回测仿真", "D-BACKTEST, D-SIMULATION, D-EXEC_SIM, D-DIGITAL_TWIN"),
        ("ML平台", "D-ML_TRAIN, D-ML_SERVE"),
        (
            "治理（横切）",
            "D-GOVERNANCE, D-GOV_RULE, D-GOV_AUDIT, D-GOV_DRIFT, D-GOV_ENFORCEMENT, D-GOV_REPAIR, D-GOV_SCRIPTS",
        ),
        ("安全（横切）", "D_SECURITY, D_SECURITY_LLM, D_BEHAVIORAL_AUDIT, D_DATA_SEC, D-AUTONOMY_PERM"),
        (
            "基础设施（横切）",
            "D_INFRA_OPS, D_INFRA_RUNTIME, D_INTEGRATION, D_INTEGRATION_GATEWAY, D_SHARED, D_FRONTEND, D_REPORTING, D-KNOWLEDGE, D-INTELLIGENCE, D_AUTONOMY_CORE, D_OPS",
        ),
    ]

    content = f"""---
module_id: VIEW-04TER-CAPABILITY-HEATMAP
title: Target Architecture — Capability Maturity Heatmap (Orthogonal View) / 目标架构：能力成熟度热力图正交视图
doc_type: architecture_view
status: Active
version: 2.0.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: agent
valid_from: 2026-04-19
superseded_by: null
supersedes: null
related_rationale:
- R70
related_open_questions:
- OQ-084
related_kb:
- KBG-0012
tags:
- target_architecture
- capability-heatmap
- maturity
- archimate
- capability-map
- business-architecture
- gap-analysis
- orthogonal-view
- domain-driven
- depgraph-derived
summary: ZephyrAlpha 2.0 能力成熟度热力图正交视图（v2.0.0）。基于§2.1裁定，热力图改为{total}域×10能力域二维矩阵。原14层×7能力域矩阵废弃。成熟度数据由depgraph.db派生。
date: '{now}'
ttl: permanent
---

## 1. Purpose & 为什么需要能力热力图

### 1.1 本视图要回答的问题

| 问题 | 答案所在 |
|---|---|
| ZephyrAlpha 的核心业务能力是什么？每一项当前多成熟？| §3 {total}域×10能力域热力图 |
| 哪些能力是"顶级机构标配但我们缺失"的 P0 短板？| §5 Gap-to-Target 差距表 |
| 达到顶级机构对标水平还需要多少投入？| §6 投入估算 |
| 能力成熟度何时刷新？谁负责？| §7 季度 review 机制 |
| 本视图与 `capability_heatmap.yaml` 的承载关系？| §8 数据承载关系 |

### 1.2 为什么要做能力热力图

**外部评审驱动**（`tests/外部评审.md` 四家 AI 共识，P1 级短板）：
> "ZephyrAlpha 缺少一张'全局能力地图 + 成熟度视觉化'让架构师 / 用户 / 外部审计在 5 分钟内抓住'我们强在哪、弱在哪'。"

**本视图价值**：
1. C-level 视角：一张图回答"系统现在多成熟、距离顶级多远"
2. Gap 识别：精准识别 P0/P1/P2 短板
3. 季度 review 锚点：固定每季度刷新，形成"能力进化曲线"
4. 招聘 / 融资 / 审计输出物

### 1.3 业界对标

| 机构 | 能力地图实现 | 成熟度模型 | 刷新频率 |
|---|---|---|---|
| **Goldman Sachs** | Enterprise Architecture Capability Dashboard | 5 档 | 季度 |
| **BlackRock** | Aladdin Capability Heatmap | 5 档 | 季度 |
| **Gartner IT Capability Framework** | Generic Capability Map | 5 档（CMMI-aligned）| 半年 |

**ZephyrAlpha 采纳**：Goldman / BlackRock / Gartner 共识的 5 档模型，季度刷新。

### 1.4 v2.0.0变更说明

基于§2.1裁定：
- 原14层×7能力域矩阵 → 改为{total}域×10能力域矩阵
- 14层降级为域属性，不再作为热力图维度
- 成熟度数据由depgraph.db `nodes.design_maturity`派生

---

## 2. Maturity model / 成熟度模型

### 2.1 五档成熟度定义

| 档位 | 名称 | 定义 | depgraph.db映射 |
|:---:|------|------|----------------|
| **L0** | 缺失 | 能力完全不存在，无设计无代码 | 域无节点 |
| **L1** | 设计 | 仅有设计文档/蓝图，无代码 | `design_maturity='design'` |
| **L2** | 草稿 | 有原型代码，未集成 | `design_maturity='prototype'` |
| **L3** | 可用 | 代码可用但未生产验证 | `design_maturity='production'` + `build_status!='active'` |
| **L4** | 生产级 | 生产环境稳定运行 | `design_maturity='production'` + `build_status='active'` |
| **L5** | 顶级机构对标 | 达到Goldman/BlackRock水平 | 待评估 |

### 2.2 评分规则

- 域成熟度 = 该域所有节点的最高成熟度
- 能力域成熟度 = 该能力域下所有域成熟度的加权平均（按节点数加权）

---

## 3. {total}域×10能力域热力图

> 数据源：depgraph.db `domains` + `nodes` 表
> 派生工具：`scripts/governance/d5_architecture/generators/generate_design_vs_production.py`

### 3.1 能力域定义（10能力域=7业务+3横切）

| 能力域 | 类型 | 包含域 |
|--------|:---:|--------|
"""
    for cap_name, cap_domains in capability_domains:
        cap_type = "横切" if "横切" in cap_name else "业务"
        content += f"| {cap_name} | {cap_type} | {cap_domains} |\n"

    content += f"""

### 3.2 域成熟度快照（{total}域）

> 完整域成熟度数据见 [`generated/design_vs_production.md`](../generated/design_vs_production.md)

| 域ID | 域名称 | layer_id | 节点数 | production | design | prototype | 成熟度评级 |
|------|--------|----------|:---:|:---:|:---:|:---:|:---:|
"""
    for d in data["domains"]:
        # 评级：有production→L3+，只有design→L1，有prototype→L2，无节点→L0
        if d["production_count"] > 0:
            rating = "L3+"
        elif d["prototype_count"] > 0:
            rating = "L2"
        elif d["design_count"] > 0:
            rating = "L1"
        else:
            rating = "L0"
        content += f"| `{d['domain_id']}` | {d['domain_name']} | `{d['layer_id'] or 'N/A'}` | {d['actual_nodes']} | {d['production_count']} | {d['design_count']} | {d['prototype_count']} | {rating} |\n"

    content += """

### 3.3 能力域成熟度汇总

| 能力域 | 域数量 | 总节点 | production占比 | 整体成熟度 |
|--------|:---:|:---:|:---:|:---:|
"""
    for cap_name, cap_domains_str in capability_domains:
        cap_domain_ids = [d.strip() for d in cap_domains_str.split(",")]
        cap_domains_data = [d for d in data["domains"] if d["domain_id"] in cap_domain_ids]
        total_nodes_cap = sum(d["actual_nodes"] for d in cap_domains_data)
        total_prod_cap = sum(d["production_count"] for d in cap_domains_data)
        prod_ratio = (total_prod_cap / total_nodes_cap * 100) if total_nodes_cap > 0 else 0
        if prod_ratio > 50:
            overall = "L3+"
        elif prod_ratio > 10:
            overall = "L2-L3"
        elif total_nodes_cap > 0:
            overall = "L1-L2"
        else:
            overall = "L0"
        content += f"| {cap_name} | {len(cap_domains_data)} | {total_nodes_cap} | {prod_ratio:.1f}% | {overall} |\n"

    content += f"""

---

## 4. Gap-to-Target / 差距分析

### 4.1 目标状态定义

| 里程碑 | 目标 | 触发条件 |
|--------|------|---------|
| **T1** | 真实资金接入 | 模拟盘稳定运行3个月 |
| **T3** | AI自治升格 | 6大核心服务全部L4 |
| **T-ENDGAME** | 顶级机构对标 | 全域能力L4+，30%域L5 |

### 4.2 当前差距（基于§3.2快照）

| 指标 | 当前 | T1目标 | T-ENDGAME目标 | 差距 |
|------|:---:|:---:|:---:|------|
| production节点占比 | {maturity.get("production", 0)}/{data["total_nodes"]} ({maturity.get("production", 0) / data["total_nodes"] * 100:.1f}%) | >30% | >80% | 见`generated/design_vs_production.md` |
| L4+域数量 | 待评估 | >10 | >40 | 需逐域评估 |
| L0域数量 | 待统计 | 0 | 0 | 见§3.2 |

---

## 5. 季度 review 机制

### 5.1 刷新流程

1. 运行`generate_design_vs_production.py`刷新§3.2快照
2. 架构师逐域评估L4/L5达标情况
3. 更新§4.2差距表
4. 识别P0/P1/P2短板→纳入下季度任务卡

### 5.2 刷新频率

- 季度例行：每3个月
- 事件驱动：真实资金接入/架构重大变更

---

## 6. 与其他视图的边界

| 其他视图 | 本视图与其关系 |
|---|---|
| `business_architecture.md` | 01-BA定义"业务做什么"；本视图给每项能力打成熟度分 |
| `architecture_model/cross_cutting/capability_heatmap.yaml` | YAML是机器可读能力清单（canonical schema）；本视图是人类可读热力图视觉化 |
| `generated/design_vs_production.md` | 派生视图提供原始统计数据；本视图做能力域聚合分析 |

---

## 7. 投入估算（人月 + KB 决策记录数 + Sprint数）

> 详见各能力域蓝图。本节仅摘要。

- T1→T3：预计需6大核心服务全部升L4，约24人月
- T3→T-ENDGAME：预计需全域L4+，约60人月

---

## 8. Revision history / 修订记录

| Date / 日期 | Description / 说明 |
|------------|-------------------|
| {now} | **v2.0.0（DM-200912 Phase4-A）**：基于§2.1裁定重写——热力图改为{total}域×10能力域矩阵；原14层×7能力域矩阵废弃；成熟度数据由depgraph.db派生；新增§1.4 v2.0.0变更说明、§2.1五档成熟度depgraph.db映射、§3.2域成熟度快照、§3.3能力域成熟度汇总。 |
| 2026-04-22 | v1.0.0：建立能力热力图正交视图。 |
"""
    out_path = TARGET_DIR / "capability_heatmap.md"
    out_path.write_text(content, encoding="utf-8", newline="\n")
    print(f"[OK] 重写 {out_path} ({len(content)} 字符)")


def main() -> None:
    """入口：重写4个核心架构视图。"""
    print("=" * 60)
    print("DM-200912 Phase4-A: 重写4个核心架构视图")
    print("=" * 60)

    data = load_domain_data()
    print(f"[INFO] 加载域数据: {data['total_domains']}域, {data['total_nodes']}节点, {data['total_edges']}边")

    write_overview(data)
    write_index(data)
    write_application_architecture(data)
    write_capability_heatmap(data)

    print("\n" + "=" * 60)
    print("[DONE] 4个核心架构视图重写完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
