---
module_id: VIEW-12-AUDIT-MATRIX
title: 12-Dimension Architecture Audit Matrix / 12 维架构评分矩阵
doc_type: audit_report
status: Active
version: 1.0.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: agent
valid_from: 2026-04-24
superseded_by: null
supersedes: null
truth_sources:
  - "[已归档-原模块候选池] vibe-coding-audit-merged.md §GLM 评分矩阵（§3243-3258）"
  - "[已归档-原模块候选池] vibe-coding-audit-merged.md §GLM 11 处薄弱点深度分析"
related_rationale: R70
related_open_questions: []
tags:
  - audit-matrix
  - architecture-scoring
  - phase-roadmap-tracking
  - quantitative-quality
priority: P1
summary: 定义 D1-D12 十二个架构维度的评分标准、当前评分基线、按 Phase 递进的目标评分。作为架构质量量化追踪的权威看板，由 validate_ssot.py 扩展的 score_architecture.py 按季度自动生成评分报告。
date: '2026-04-24'
ttl: permanent
---

# 12-Dimension Architecture Audit Matrix （被恢复）
# 12 维架构评分矩阵

***

## 0. 读者指南

| 章节 | 内容 | 主要读者 |
|------|------|----------|
| §1 | 12 维度的定义与权重 | 架构师 |
| §2 | 当前基线评分（2026-04-24）| 所有读者 |
| §3 | 按 Phase 递进的目标评分 | 项目经理 |
| §4 | 每维度的采集指标 | 开发者、运维 |
| §5 | 评分算法（0-10 分制）| 架构师 |
| §6 | 自动化评分接口 | 开发者 |
| §7 | 季度评审流程 | 用户 |

### 0.2 本文档不是

- ❌ 具体维度的实施路径 → 见各维度对应的 `0X-*-architecture.md`
- ❌ 6 大核心服务的详细架构 → 见 `../04_architecture_principles_decisions/application_principles.md`
- ❌ Phase 过渡门 → 见 `phase-transition-protocol.md`

***

## 1. 12 维度定义

### 1.1 维度清单

| 维度 | 名称 | 关注点 | 权重 | 对应架构文档 |
|:----:|------|-------|:----:|-------------|
| **D1** | 业务架构 | 业务能力完整性、需求覆盖 | 0.08 | `business_architecture.md` |
| **D2** | 信息架构 | 数据模型、元数据治理、schema 演化 | 0.08 | `information_principles.md` + `directory_registry.yaml` |
| **D3** | 应用架构 | 模块边界、服务拆分、职责清晰度 | 0.10 | `../04_architecture_principles_decisions/application_principles.md` |
| **D4** | 技术架构 | 技术栈成熟度、升级路径、零依赖原则 | 0.08 | `technology_architecture.md` + `technology_landscape.yaml` |
| **D5** | MCP 集成 | AI IDE 兼容性、MCP 协议通道覆盖 | 0.08 | `context-engine-interface.md §5` |
| **D6** | 安全架构 | 防御深度、OWASP LLM Top 10 覆盖、沙箱隔离 | 0.12 | `security_architecture.md` + `llm-security-gateway-interface.md` |
| **D7** | Agent 编排 | 任务生命周期、幻觉检测、状态机完整性 | 0.10 | `agent-orchestrator-interface.md` |
| **D8** | 反馈闭环 | 指标-异常-动作链路、可观测性 | 0.10 | `feedback-loop-engine-interface.md` |
| **D9** | 数据架构 | 存储一致性、备份/恢复、容灾 | 0.06 | `../04_architecture_principles_decisions/data_principles.md` + `architecture_model/data/data_entity_catalog.yaml` |
| **D10** | 运维架构 | SLI/SLO、可观测性三支柱、告警 | 0.08 | `operations_architecture.md` |
| **D11** | 安全运营 | Secret 防护、供应链安全、审计合规 | 0.06 | `security_architecture.md §6` |
| **D12** | 治理架构 | SSoT 一致性、KB 决策记录 覆盖、流程门禁 | 0.06 | `governance_architecture.md` |
| **合计** | — | — | **1.00** | — |

### 1.2 权重分配理由

| 权重档位 | 维度 | 理由 |
|---------|------|------|
| 0.12（最高）| D6 安全架构 | 个人量化 + LLM 编码的 P0 红线；GLM 当前评分 2.2/10 最薄弱 |
| 0.10 | D3 / D7 / D8 | 应用架构是业务层落地核心；Agent 编排 + 反馈闭环是 Vibe Coding 2.0 的独特性 |
| 0.08 | D1 / D2 / D4 / D5 / D10 | 企业架构传统四领域 + MCP + 运维，质量不可妥协但非 P0 |
| 0.06（最低）| D9 / D11 / D12 | 数据 / 安全运营 / 治理本身依赖上游维度，权重稍低避免双计 |

***

## 2. 当前基线评分（2026-04-24）

### 2.1 基线数据源

- GLM §评分矩阵（`vibe-coding-audit-merged.md` §3243-3258）
- Kimi §11 薄弱点深度分析
- Opus §最终裁定

### 2.2 基线评分表

| 维度 | 当前分 | 评估证据 | 主要缺口 |
|:----:|:------:|---------|---------|
| D1 业务架构 | **7.5** | 14 层量化架构冻结，业务流程完整 | 部分子域缺 HiL 门禁 |
| D2 信息架构 | **6.8** | 元数据层 L00 已定义 | schema 演化策略未落地 |
| D3 应用架构 | **5.2** | 6 大核心服务新定义 | experimental 未落地前为规范级 |
| D4 技术架构 | **7.0** | 17 项技术选型已定稿 | 升级阈值看板未自动化 |
| D5 MCP 集成 | **4.0** | IDE 能力矩阵已定义 | Cursor/Trae 实测未进行 |
| D6 安全架构 | **2.2** | LSG 接口规范完成 | L1-L4 四层防御全未落地；红队语料库为零 |
| D7 Agent 编排 | **4.0** | Orc 接口规范完成 | 状态机/幻觉检测/沙箱全未落地 |
| D8 反馈闭环 | **4.0** | FLE 接口规范完成 | 指标/异常/动作链路全未落地 |
| D9 数据架构 | **6.0** | ChromaDB + SQLite 选型明确 | 备份/恢复未落地 |
| D10 运维架构 | **2.8** | 架构文档骨架存在 | SLI/SLO 未定义；OpenTelemetry 未集成 |
| D11 安全运营 | **3.5** | git-secrets 选型已定 | 未集成到 pre-commit；供应链审计未跑 |
| D12 治理架构 | **5.5** | SSoT + KB 决策记录 体系有骨架 | SSoT Validator 未实现（scaffold 任务）|
| **加权合计** | **4.73** | — | 综合分 6 分 passing 线之下，需 2 整体提升（v1.2.0 GATE-SUM 校正：原报 4.49 为 GLM 舍入，精确值 4.732） |

### 2.3 综合分计算

```
综合分 = Σ (维度分 × 权重)
       = 7.5×0.08 + 6.8×0.08 + 5.2×0.10 + 7.0×0.08 + 4.0×0.08
       + 2.2×0.12 + 4.0×0.10 + 4.0×0.10 + 6.0×0.06 + 2.8×0.08
       + 3.5×0.06 + 5.5×0.06
       = 0.60 + 0.544 + 0.52 + 0.56 + 0.32
       + 0.264 + 0.40 + 0.40 + 0.36 + 0.224
       + 0.21 + 0.33
       = 4.732   （GLM §3258 报 4.49，小数差异因个别维度微调）
```

### 2.4 红线识别

| 维度 | 分数 | 红线判定 | 处置 |
|------|------|---------|------|
| **D6 安全架构** | 2.2 | ❗ P0 红线（< 3.0）| 2 必须升至 ≥ 6.0 |
| **D10 运维架构** | 2.8 | ❗ P0 红线（< 3.0）| 4 必须升至 ≥ 6.0 |
| D11 安全运营 | 3.5 | ⚠️ P1 警戒（< 4.0）| experimental 升至 ≥ 5.0 |
| D5 MCP 集成 | 4.0 | ⚠️ P1 警戒 | experimental 升至 ≥ 6.0 |
| D7 Agent 编排 | 4.0 | ⚠️ P1 警戒 | experimental 升至 ≥ 6.0 |
| D8 反馈闭环 | 4.0 | ⚠️ P1 警戒 | beta 升至 ≥ 6.0 |

***

## 3. 按 Phase 递进的目标评分

### 3.1 Phase 目标矩阵

| 维度 | 当前 | experimental 目标 | beta 目标 | beta 目标 | stable 目标 |
|:----:|:----:|:------------:|:------------:|:------------:|:------------:|
| D1  | 7.5 | 7.8  | 8.0  | 8.2  | 8.5 |
| D2  | 6.8 | 7.2  | 7.5  | 7.8  | 8.2 |
| D3  | 5.2 | 7.0  | 7.8  | 8.2  | 8.8 |
| D4  | 7.0 | 7.5  | 7.8  | 8.2  | 8.5 |
| D5  | 4.0 | 6.0  | 7.0  | 8.0  | 8.5 |
| D6  | 2.2 | 5.5  | 6.5  | 7.8  | 8.5 |
| D7  | 4.0 | 6.5  | 7.5  | 8.0  | 8.5 |
| D8  | 4.0 | 5.5  | 7.0  | 7.8  | 8.5 |
| D9  | 6.0 | 6.5  | 7.0  | 7.5  | 8.0 |
| D10 | 2.8 | 4.0  | 5.5  | 7.0  | 8.2 |
| D11 | 3.5 | 5.0  | 6.0  | 7.0  | 8.0 |
| D12 | 5.5 | 7.5  | 8.0  | 8.2  | 8.5 |
| **综合** | **4.73** | **6.39** | **7.17** | **7.87** | **8.44** |

### 3.2 每个 Phase 的增量重点

| Phase | 重点提升维度 | 关键动作 |
|-------|------------|---------|
| experimental | D3 / D6 / D7 / D12 | 6 大核心服务 InProcess* 落地 + LSG L1-L4 起步 + SSoT Validator 就位 |
| beta | D6 / D7 / D8 | 红队语料库 ≥ 150 条 + 幻觉检测规则完善 + FLE 13 项指标上线 |
| beta | D5 / D10 | Remote* 服务化 + OpenTelemetry 集成 |
| stable | D10 / D11 | 生产级可观测性 + 季度红队演练 + 供应链审计 |

### 3.3 里程碑门（最低合格线）

| 里程碑 | 综合分 ≥ | 关键单维度 ≥ |
|--------|:-------:|------------|
| experimental 退出门 | 6.0 | D6 ≥ 5.0, D12 ≥ 7.0 |
| beta 退出门 | 7.0 | D6 ≥ 6.0, D7 ≥ 7.0, D8 ≥ 6.5 |
| beta 退出门 | 7.5 | D5 ≥ 7.5, D10 ≥ 6.5 |
| stable 稳定态 | 8.0 | D6 ≥ 8.0, D10 ≥ 8.0 |

综合分 ≥ 6.0 是"可交付"的最低分；8.0 是"生产级"的参考分。

***

## 4. 每维度的采集指标

### 4.1 D1 业务架构

| 指标 | 采集方式 | 评分贡献 |
|------|---------|---------|
| 14 层覆盖度（有蓝图的层 / 14） | `grep layer src/zephyr/*/` | 0.3 |
| HiL 门禁覆盖率（有 HiL 的决策点 / 应有）| `grep HiL docs/02_ea/` | 0.3 |
| 业务用例完整性（有任务卡的业务流 / 已识别）| 任务卡统计 | 0.4 |

### 4.2 D2 信息架构

| 指标 | 采集方式 | 评分贡献 |
|------|---------|---------|
| L00 元数据 schema 定义完整性 | schema 字段数 / 期望字段数 | 0.4 |
| schema 演化 KB 决策记录 数量 | KB:decisions namespace 按 schema 标签 | 0.3 |
| 数据字典覆盖率 | 数据字典条目数 / 核心实体数 | 0.3 |

### 4.3 D3 应用架构

| 指标 | 采集方式 | 评分贡献 |
|------|---------|---------|
| 6 大核心服务 InProcess* 实现完整性 | `pytest tests/integration/services/` 通过率 | 0.5 |
| 服务间依赖 DAG 无循环 | `python scripts/governance/validate_dag.py` | 0.2 |
| Protocol 抽象基类覆盖率 | `grep Protocol src/zephyr/*/protocol.py` | 0.3 |

### 4.4 D4 技术架构

| 指标 | 采集方式 | 评分贡献 |
|------|---------|---------|
| 17 项技术选型落地率 | 安装 + import 验证 | 0.5 |
| 零外部服务依赖| `python -c "from zephyr import *"` 不联网 | 0.3 |
| 升级阈值看板自动化 | FLE 指标是否覆盖 `upgrade_watchboard` | 0.2 |

### 4.5 D5 MCP 集成

| 指标 | 采集方式 | 评分贡献 |
|------|---------|---------|
| IDE 能力矩阵覆盖率（已实测 IDE / 4 种）| 实测记录 | 0.5 |
| MCP 通道可用性（tools/resources/prompts/sampling）| 自动化测试 | 0.3 |
| 通道降级路径覆盖 | `DEGRADE-003` 触发测试 | 0.2 |

### 4.6 D6 安全架构

| 指标 | 采集方式 | 评分贡献 |
|------|---------|---------|
| LSG 四层防御完整性（L1-L4）| 单元测试通过率 | 0.3 |
| 红队语料库规模 + 绕过率 | 专项评估 | 0.3 |
| Agent Sandbox 隔离强度（Windows ACL 测试）| 越权测试 | 0.2 |
| OWASP LLM Top 10 覆盖率 | 对照表 | 0.2 |

### 4.7 D7 Agent 编排

| 指标 | 采集方式 | 评分贡献 |
|------|---------|---------|
| TaskState 状态机完整性（11 状态 + 转移）| 状态机测试覆盖 | 0.3 |
| 幻觉检测规则数量 + 漏检率 | 评估集测试 | 0.3 |
| 任务队列性能（入队延迟 P99）| 基准测试 | 0.2 |
| Sandbox 创建成功率 | 集成测试 | 0.2 |

### 4.8 D8 反馈闭环

| 指标 | 采集方式 | 评分贡献 |
|------|---------|---------|
| P0 指标覆盖率（已上报 / 13 项）| FLE 统计 | 0.3 |
| 异常检测规则完整性（EMA + 阈值）| 单元测试 | 0.3 |
| 动作 Protocol 适配器数量 | 代码统计 | 0.2 |
| TTL 自动回滚成功率 | 集成测试 | 0.2 |

### 4.9 D9 数据架构

| 指标 | 采集方式 | 评分贡献 |
|------|---------|---------|
| 备份自动化（ChromaDB + SQLite）| 定时任务存在性 | 0.4 |
| 恢复演练成功率 | 季度演练记录 | 0.3 |
| 跨服务数据一致性（VMS ↔ L00 schema）| 一致性扫描 | 0.3 |

### 4.10 D10 运维架构

| 指标 | 采集方式 | 评分贡献 |
|------|---------|---------|
| 5 项 SLI/SLO 定义完整性 | `operations_architecture.md` 内容 | 0.3 |
| OpenTelemetry 覆盖率 | traces/metrics/logs 三支柱 | 0.4 |
| 结构化日志规范合规率 | JSON lines 格式校验 | 0.3 |

### 4.11 D11 安全运营

| 指标 | 采集方式 | 评分贡献 |
|------|---------|---------|
| Secret 扫描集成到 pre-commit | `pre-commit-config.yaml` 检查 | 0.4 |
| 供应链审计频率（pip-audit）| CI/定时任务存在性 | 0.3 |
| 审计日志完整性 | `.runtime/logs/audit/` 存在性 | 0.3 |

### 4.12 D12 治理架构

| 指标 | 采集方式 | 评分贡献 |
|------|---------|---------|
| SSoT Validator 无 P0 违规 | `validate_ssot.py --all` | 0.4 |
| KB 决策记录 覆盖率（关键决策 / 已有 KB 决策记录）| `grep related_kb docs/` | 0.3 |
| Phase 过渡双门协议合规率 | `validate_phase_transition.py` | 0.3 |

***

## 5. 评分算法

### 5.1 单维度 0-10 分制

```
单维度分 = Σ (子指标值 × 子指标权重) × 10

其中子指标值 ∈ [0, 1]：
  - 布尔指标：通过 = 1.0，失败 = 0.0
  - 比例指标：实际 / 目标（上限 1.0）
  - 分级指标：按阈值映射（如 绕过率 <2% → 1.0, 2-5% → 0.7, 5-10% → 0.4, >10% → 0.0）
```

### 5.2 综合分

```
综合分 = Σ (单维度分 × 维度权重)
```

### 5.3 分档标准

| 综合分 | 等级 | 说明 |
|:-----:|------|------|
| ≥ 8.0 | A | 生产级 |
| 6.0-7.9 | B | 可交付（3 合格）|
| 4.0-5.9 | C | 开发中（1 过渡期）|
| < 4.0 | D | 不合格（必须整改）|

***

## 6. 自动化评分接口

### 6.1 核心脚本

```bash
# 季度全量评分
python scripts/governance/score_architecture.py --quarterly

# 单维度详评
python scripts/governance/score_architecture.py --dimension D6

# 对比历史（找趋势）
python scripts/governance/score_architecture.py --compare last_quarter

# 输出 dashboard（生成 markdown 看板）
python scripts/governance/score_architecture.py --dashboard > docs/19_development_workspace/architecture-score-dashboard.md
```

### 6.2 CLI 输出格式（JSON lines）

```json
{"ts": "2026-04-24", "dimension": "D6", "score": 2.2, "sub_indicators": {
  "lsg_four_layers": 0.0, "red_team_corpus": 0.0, "sandbox_strength": 0.3, "owasp_coverage": 0.4
}, "weighted_contribution": 0.264}

{"ts": "2026-04-24", "type": "composite", "score": 4.49, "grade": "C",
 "red_lines": ["D6", "D10"], "warnings": ["D11", "D5", "D7", "D8"]}
```

### 6.3 与 FLE 集成

`score_architecture.py` 产出的 JSON lines 同时写入 `.runtime/logs/scoring/<date>.jsonl`，被 FLE 采样为长周期指标（周/月粒度）。

---

## 7. 季度评审流程

### 7.1 频次

每季度最后一周执行一次评分。

### 7.2 流程

```
1. 运行 score_architecture.py --quarterly --dashboard
   → 产出 architecture-score-dashboard.md

2. 用户审阅 dashboard，识别：
   - 退步维度（环比下降 > 0.5 分）
   - 未达 Phase 目标的维度
   - 新增红线

3. 若存在 P0 红线（分数 < 3.0），立即进入"整改计划"：
   - 新建 KB 决策记录 分析根因
   - 排入下 Phase 任务卡
   - 下次评审检查是否恢复

4. 评审会议纪要归档到 docs/_working/architecture-score-reviews/YYYY-QN.md
```

### 7.3 一人团队的简化

虽然是一人团队，仍保留季度评审，理由：

- 强制自省：定期量化回顾，避免"感觉良好"盲区
- 进度锚点：Phase 计划的实际推进度可视化
- 决策证据：未来升级/重构决策有数据支持

### 7.4 一人开发场景的风险考量

> 来源：`architecture-audit-final-verdict-2026-04-21.md` §4（已融入本文件后删除）。该评估为 2026-04-21 时点快照（Claude Opus 外部审计），部分结论可能随时间推移和 Phase 推进而过期。以下为应永久关注的架构设计原则。

- **治理过重风险**：一人团队场景下，双轨目录结构 + 4 级注册表 + SSoT 校验 → 治理维护成本可能超过代码产出。设计原则：治理体量必须与交付能力成比例，宁缺毋滥。当维护某类治理产出的工时 > 直接写代码解决同样问题的工时，该治理产出应简化或废除。
- **架构文档维护成本**：6 层目录 + 14 个架构视图 + 24 条 KB 决策记录 + 29 个图 → 文档负债已逼近 AI 正常 session 管理上限。设计原则：新增文档需评估其 token 成本和维护频率，优先用结构化数据（YAML）替代自然语言（prose）。
- **AI 上下文约束**：同一 session 中 AI 无法同时加载所有架构文档。设计原则：每个文件必须满足 §0 零记忆重启标准——单文件自包含、不依赖"之前知道"的内容。

***

## 8. 开放问题

| OQ | 议题 | 何时闭合 |
|----|------|---------|
| OQ-AM-01 | 每维度子指标的权重是否需要随 Phase 微调 | beta |
| OQ-AM-02 | 是否需要加入"技术债"维度 D13 | beta |
| OQ-AM-03 | 社区标杆对比（如 Citadel / Jane Street 内部 EA 评分）| stable |

***

## 9. 修订记录

| 日期 | 版本 | 作者 | 说明 |
|------|------|------|------|
| 2026-04-24 | 1.0.0 | opus47_architect | 初版。基于 GLM 评分矩阵 + Kimi 11 处薄弱点分析 + Opus 最终裁定合成。12 维度 + 权重 + Phase 目标曲线 + 采集指标 + 自动化评分接口 + 季度流程。|
