---
module_id: MOD-INF-004
title: Vibe Coding 双管线 + 脚本系统 + M1-M11 模块蓝图（B4 · 3）
doc_type: blueprint
status: retired
version: 1.0.1
layer: L01
layer_name: infrastructure
functional_domain: infra
owner: ZephyrAlpha-Owner
classification: internal
language: zh
created_by: AI-GLM-5.1
valid_from: 2026-05-01
ttl: permanent
construction_progress: phase_0_completed
superseded_by: MOD-INF-006
completion_note: "scaffold 构建完成——双管线方案+M1-M11模块定义+脚本系统架构已落地。内容已于2026-05-02升级并入 MOD-INF-006 task-system。本蓝图记录已完成工作，永久保留，不可删除——有新需求应走蓝图升级流程重开(§八·铁律三)。"
priority: P0
tags:
  - vibe-coding
  - dual-pipelines
  - script-system
  - m1-m11-modules
  - infrastructure
  -
summary: ZephyrAlpha Vibe Coding 双管线（起草+审计）+ 脚本系统 + M1-M11 模块完整蓝图。覆盖 11 个 AI 基础设施模块的 3 渐进落地路径。Wave 0 终审落地：M2 SQLite-VSS  → ChromaDB ，M3 自研轻量 Orchestrator，M5 自研安全网关。
---

# Vibe Coding 双管线 + 脚本系统 + M1-M11 模块蓝图（B4 · 3）

> **真源声明**：本蓝图是 Vibe Coding 双管线 + 脚本系统 + 11 模块（M1-M11）的唯一真源。原始施工图文档 `construction-plan-vibe-coding-pipelines.md` 经历 Wave 0 三轮审计 + Claude-Opus-4.7 终审，本文档承载终审裁定后的最终方案。

---

## 1. 核心概念

Vibe Coding 基础设施是 ZephyrAlpha **所有 AI 辅助开发的"骨架"**——包括内容生产的双管线流程、脚本系统的质量保障、以及 11 个核心 AI 基础设施模块。

**三大子系统**：
- **双管线（Drafting + Auditing）**：A 区起草（Kimi→GLM→Qwen）→ 三轮审计 → B 区 Opus 终审
- **脚本系统（D1-D12）**：15 维度评分 + 缺口扫描 + 根因分析 + 学术验证 + 工业对标 + 幻觉检测
- **M1-M11 模块**：Context Engine / Vector Memory / Orchestrator / Feedback Engine / Auto Fixer / Security Gateway / Session Carryover / Drift Detector / Code Health / Knowledge Base / Kill Switch / Invariant Guard

---

## 2. 到需要做什么（回顾大盘 + 用户原意）

**Owner 指示**：
- "起草和审计物理分离（A/B 两区）"
- "每个蓝图必须走完整管线 + Opus 终审"
- 当前规模：1 Owner + 5 个 AI 服务（Trae CN / Cursor / Claude / Kimi / GLM / Qwen / Opus）

**设计原则**：
- 起草 + 审计物理分离（A/B 两区，G2 协议）
- 任何蓝图必须经过双管线 + Opus 终审（V-12 门禁强制）
- 自审计闸 + Provenance Chain（C5 知识沉淀器隔离闸）

---

## 3. 边界

### 3.1 覆盖

- Vibe Coding 内容生产侧的双管线（起草 + 审计）+ 脚本系统 + M1-M11
- 1 Owner + 5 AI 服务规模下的完整工作流

### 3.2 不覆盖（→ 去哪）

- 具体业务层（C 轨 L00-L13 业务模块）→ 各自模块蓝图
- 安全网关实现细节 → MOD-INF-001（capacity-assurance）
- 任务卡制度 → MOD-INF-003（task-card-kms）

---

## 4. 输入 / 基于此设计

| 输入 | 来源 |
|------|------|
| Owner 双管线指示 | A/B 物理分离 + Opus 终审 |
| Wave 0 终审裁决 | Claude-Opus-4.7（R-71~73, R-76）|
| 原始设计草案 | `19_development_workspace/drafts-and-audits/vibe-coding-infrastructure/` |

---

## 5. 架构决策

### 5.1 双管线工作流

**起草管线（A 区写作）**：

| Step | 模型 | 职责 | 工作量 |
|------|------|------|:--:|
| 1 | Kimi K2.6 | 发散：原意理解 + 方向展开 + 关键问题 + 风险盲点 + 调研需求 | 0.5-1h |
| 2 | GLM-5.1 | 调研：GitHub/论文/技术选型/行业实践/项目对齐 | 0.5-1h |
| 3 | Qwen-3.6-Plus | 起草：模块分解 + Phase 路线 + 技术选型 + 验收 + 争议标记 | 1-2h |

**审计管线（A 区审计）**：

| Round | 模型 | 职责 | 工作量 |
|-------|------|------|:--:|
| 1 | GLM-5.1 | 结构扫描：15 维度评分 + 缺口扫描 + AI 自治权限审计 | 0.5-1h |
| 2 | Kimi K2.6 | 发现深挖：盲区扫描 + 根因分析 + 架构方向 + 学术验证 | 0.5-1h |
| 3 | Qwen-3.6-Plus | 务实落地：选型最终化 + 路线图 + 配置规格 + 验收标准 | 1-2h |

**当前阶段裁定方式**（drafts-audits-arbitration-protocol.md 已于 2026-05-01 废除，多轮 AI 审计流水线已停止）：

| Step | 平台 | 职责 |
|------|------|------|
| 草案 | Cursor | 模块草案直接写入本目录，frontmatter 标注 `status: proposed` |
| 裁定 | Cursor | Owner 审查草案，拍板后 `status` → `accepted` |
| 落地 | Cursor | 同 commit 迁入正式源码路径 + 追加 R-XXX |

### 5.2 M1-M11 模块总表（Wave 0 终审选型）

| 模块 | 名称 | 关键技术 | Phase | 权限 |
|------|------|---------|:-----:|------|
| **M1** | Context Engine | NetworkX + Qwen2.5-3B + 三级回退 | experimental | Human-Gated |
| **M2** | Vector Memory | SQLite-VSS+FTS5 (P1) → ChromaDB (P2) | experimental 起步 | Human-Gated |
| **M2-P** | M2 Provenance | hash 链 + 只追加 SQLite | experimental | Immutable Core |
| **M3** | Orchestrator | dataclass+Pydantic (P1) → LangGraph (P2) | experimental | Human-Gated |
| **M4-A** | Feedback Engine | EMA + 阈值 + 持续时间 | experimental | Human-Gated |
| **M4-B** | Auto Fixer | sandbox ruff/mypy 修复 | experimental | Immutable Core |
| **M5** | Security Gateway | bandit + safety + regex + OWASP | experimental | Immutable Core |
| **M6** | Session Carryover | SQLite + TTL 7 天 + agent_role | experimental | Human-Gated |
| **M7** | Drift Detector | EMA-based 漂移检测 + YAML 阈值 | beta | AI-Modifiable |
| **M8** | Code Health | 评分算法 + YAML 阈值 | beta | AI-Modifiable |
| **M9** | Knowledge Base | M2 共享 collection + metadata.type | beta | AI-Modifiable |
| **M10** | Kill Switch | 熔断器 + Owner 恢复 | experimental | Immutable Core |
| **M11** | Invariant Guard | Pydantic v2 运行时校验 | experimental | Immutable Core |

### 5.3 脚本系统（D1-D12）

| 维度 | 名称 | Phase | 终选 |
|------|------|:---:|------|
| D1 | 缺口扫描 | experimental | meta_auditor.py 抽样 10% |
| D2 | 15 维度评分 | experimental | YAML 评分模板 + Pydantic |
| D3 | 根因分析 | experimental | 5-Why + 类比库 |
| D4 | 学术验证 | experimental | KB 向量检索 |
| D5 | 工业对标 | experimental | KE-业界标准库 |
| D12 | 幻觉检测 | experimental→2 | 阈值版 (P1) → LLM-as-Judge (P2) |

### 5.4 自审计闸（防 OWASP LLM-04 自我闭环）

```python
@isolation_guard
def knowledge_writer(content, source):
    assert source.audit_status in ('arbitrated',)
    assert source.owner_approved
    assert source.type != 'llm_output_direct'
    write_to_quarantine(content, source)
```

---

## 6. 架构视图

### 6.1 Phase 路线图

| Phase | 名称 | 人日 | 关键交付物 |
|-------|------|:--:|---------|
| **0** | 地基 | 4-6 | A/B 区目录骨架 / V-12 门禁 / 权限注册表 |
| **1a** | 核心安全闸 | 5-7 | M5 LSG / M10 Kill Switch / M11 Invariant Guard / M2 起步 |
| **1b** | 自动化能力 | 5-7 | M1 Context Engine / M3 Orchestrator / M4 Feedback + Auto Fixer / M6 Carryover / 脚本系统 D1-D12 |
| **2** | 升级完善 | 5-7 | M7 Drift / M8 Health / M9 KB / 触发条件评估 |
| **3** | 服务化 | 按需 | 远程化 Vector/Orchestrator/Context |

### 6.2 experimental 综合验收

| 维度 | 指标 | 目标 |
|------|------|------|
| 安全 | LSG fail-closed 率 | 100% |
| 安全 | OWASP LLM01-05 覆盖 | 100% |
| 安全 | 红队绕过率 | ≤5% |
| 性能 | M2 search() P99 | ≤200ms |
| 性能 | M1 build() P99 | ≤800ms |
| 性能 | M3 入队延迟 P99 | ≤100ms |
| AI | Token 消耗/任务 | ≤5K |
| AI | Provenance Chain 完整性 | 100% |
| 成本 | 免费模型占比 | ≥90% |
| 容量 | 启动时间 | <2s @ 97 模块 |

### 6.3 关键代码骨架

**M2 Vector Memory (experimental SQLite-VSS)**：
```python
class SQLiteVSSBackend:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self.conn.load_extension('vss0')
        # FTS5 + VSS 双索引
    def search(self, query, k=5): ...  # RRF 合并
```

**M3 自研 Orchestrator**：
```python
class LightweightOrchestrator:
    def __init__(self, db_path, sandbox_gate):
        self.queue = asyncio.Queue()
    async def submit(self, spec: TaskSpec): ...
    async def dispatch(self): ...
```

**M5 安全网关**：
```python
class LocalLLMSecurityGateway:
    def inspect(self, request: LLMRequest) -> InspectResult:
        # L1 输入分类 → L2 Prompt 隔离 → L3 Schema 验证 → L4 Pattern 巡检
        ...
```

---

## 7. 触发条件与扩展路径

| 条件 | 动作 |
|------|------|
| 向量记录 > 50K | M2 切 ChromaDB |
| 并发 Agent > 3 | M3 引入 LangGraph |
| OWASP LLM-04 命中 ≥3 次 | M5 引入 Guardrails |
| 模块 > 300 且 AI 错误率 > 10% | D12 幻觉检测升级 LLM-as-Judge |
| 并发 Agent > 20 或 P99 > 3s | beta 远程化 |
| Auto Fixer 修改含删除 | Reward Hacking 告警 |

---

## 8. 风险与缓解

| 风险 | 概率 | 缓解 |
|------|------|------|
| sqlite-vss Windows 编译失败 | 中 | 预编译 .dll；fallback FTS5+余弦近似 |
| 自研 Orchestrator 并发 >3 性能不足 | 低 | beta 触发提前 LangGraph |
| Auto Fixer 反向 reward hacking | 中 | sandbox + diff 必须含修改非删除 |
| 脚本系统自审计死循环 | 低 | 隔离闸 + 抽样率 10% 上限 |

---

## 9. 关键关联

| 关联文档 | 说明 |
|---------|------|
| `ai-autonomy-authority-registry.md` | 模块权限真源 |
| `capacity-assurance/blueprint.md` | B3 容量保障协同 |

## 10. 实际代码实现情况（Code Implementation Status）

> **本节记录蓝图对应的实际代码，证明 scaffold 构建确实完成——非纸面设计。**

| 代码文件 | 对应蓝图节 | 实现内容 |
|---------|:---:|------|
| `src/zephyr/pipeline/pipeline_orchestrator.py` | §4.3 双管线 | TaskCard 派发到 A区（M1-M5起草）/ B区（M6-M11审计） |
| `src/zephyr/pipeline/models.py` | §4.3 | Pipeline 路由结构定义（PipelineRoute / ExecutionMode） |
| `src/zephyr/l01_infrastructure/script_system/finding.py` | §5 脚本系统 | Finding 数据结构 + 严重度分级 |
| `src/zephyr/core/blueprint_decomposer.py` | §4.2 | 蓝图 → 任务分解逻辑 |
| `src/zephyr/context_engine/doc_compressor.py` | §4.4 | M1 输入文档压缩 |
| `scripts/governance/` (D1-D12) | §5 | 12 维度质量审计脚本全量落地 |

**实现判定**：scaffold 蓝图所述的双管线方案、脚本系统架构、M1-M11 模块定义均已落地——对应磁盘代码完整。

> **历史溯源**：原始施工图 Wave 0 终审产出（2026-04-27），三轮审计 GLM/Kimi/Qwen + Opus-4.7 裁决 5 条争议 + 兜底 V-11/V-12/V-13。2026-05-01 迁入 `03_modules/l01_infrastructure/vibe-coding-pipelines/blueprint.md`，内容保留，结构按蓝图模板重组。

---

## 11. 已实现代码完整路径索引

> **AGENTS.md §6.14 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> Vibe Coding双管线——scaffold构建完成，已升级为MOD-INF-006

### 11.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/pipeline/models.py` | ✅ 已实现 | |
| `src/zephyr/pipeline/pipeline_orchestrator.py` | ✅ 已实现 | |

### 11.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/unit/test_pipeline_orchestrator.py` | ✅ 已实现 | |

### 11.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §11（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
