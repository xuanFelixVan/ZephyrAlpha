---
module_id: ADR-0012
title: Capability Maturity Heatmap 正交视图（Orthogonal View 第二张）
doc_type: adr
status: active
version: 1.0.0
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
tags:
- adr
- architecture
- capability-heatmap
- maturity
- archimate
- gartner
- goldman-sachs
- orthogonal-view
- gap-analysis
summary: 采用 Capability Maturity Heatmap（能力成熟度热力图）作为 ZephyrAlpha 2.0 **第二个正交视图（Orthogonal
  View）**，与 `ADR-0011 Runtime Planes` 并列。切片维度为**能力成熟度**（L0 Missing / L1 Design / L2
  Draft / L3 Available / L4 Production / L5 Leading 六档 —— L0 作为"缺失"底档 + L1~L5 五档渐进），渲染为
  14 层业务 × 7 核心能力域 = 98 格二维热力图。对标 ArchiMate 3.2 Capability Map + Gartner IT Capability
  Framework（ITScore）+ Goldman Sachs Enterprise Architecture Capability Dashboard 三家业界主流做法。回应
  `tests/外部评审.md` 四家 AI 外部评审（Gemini 2.5 Pro / GPT-5 Thinking / Claude Opus / Grok）共识指出的
  "缺少能力成熟度可视化（top-tier 机构必备）" P1 短板。本 ADR 对应的视图文件为 `target-architecture/04ter-capability-heatmap.md`
  v1.0.0 active。热力图不承载代码，是 **meta-architecture 层面的可视化治理工具**，季度由架构师刷新评分，年度由执委会锁定目标状态。与
  `architecture-model/cross-cutting/capability-heatmap.yaml`（R57 已落地 Maturity + Investment
  Intensity 三列）形成数据层 SSoT → 可视化层视图的承载关系。
date: '2026-04-22'
ttl: permanent
---

# ADR-0012：Capability Maturity Heatmap 正交视图

## 1. 状态（Status）

- **当前状态**：`accepted`
- **提议日期**：2026-04-19（S15-Phase1 J1 批次，与 ADR-0011 同批）
- **拍板日期**：2026-04-19（用户批准"方案 B + 选项 β（合并 Capability Heatmap）"一次性拍板）
- **被谁取代**：无
- **取代了谁**：无（首次定义 Capability Maturity Heatmap 视图）

## 2. 上下文（Context）

### 2.1 触发原因

S15 Phase 1 J0-sync 交付后，用户回顾外部评审反馈 `tests/外部评审.md`，四家 AI 外部评审（Gemini 2.5 Pro / GPT-5 Thinking / Claude Opus / Grok）**共识指出 P1 短板**："缺少全局能力地图 + 成熟度可视化（top-tier 机构必备）"。

在审批 ADR-0011 Runtime Planes 方案时，用户主动追加"**选项 β**：本批次合并 Capability Heatmap"，Opus 确认可共享 frontmatter + 修订同步批次、边际成本极低后采纳，遂有本 ADR。

### 2.2 问题本质

ZephyrAlpha 当前已有 `catalogs/business-capability-map.md` v1.1.0（R57 批次 E H2 落地），包含 Maturity L1-L5 + Investment Intensity 两列判断理由。但 **capability-map.md 是数据层清单格式**，不是可视化层视图：

- 读者无法在 10 秒内看懂系统整体成熟度
- 无法在二维（业务层 × 能力域）热力图上直观识别成熟度差距
- 无法支持季度 review + 执委会年度拍板目标状态的治理流程
- 无法回应外部评审的"热力图标配"诉求

**顶级机构标配**：

| 机构 | 做法 | 公开资料证据 |
|------|------|------------|
| **Goldman Sachs** | Enterprise Architecture Capability Dashboard 每季度刷新热力图 + 年度执委会锁定目标 | 公开会议 + 架构白皮书 |
| **JPMorgan** | Capability Maturity 仪表盘用于内部 EA review | Engineering blog |
| **BlackRock Aladdin** | 能力域 × 成熟度矩阵作为产品路线图基石 | 产品白皮书 |

### 2.3 ArchiMate + Gartner 方法论支持

- **ArchiMate 3.2 Capability Map**：The Open Group 官方元模型，Capability × Resource × Outcome 三元组 + 成熟度/投资强度两轴
- **Gartner IT Capability Framework**（ITScore）：五档成熟度 L1-L5 + Gap-to-Target 差距分析 + 季度 review 节奏
- 本 ADR 采纳 "L0 底档（缺失）+ L1-L5 渐进"六档划分，与 Gartner ITScore 五档兼容（L0 视为"零档"）

## 3. 决策（Decision）

### 3.1 三方案评估

| 方案 | 描述 | 优点 | 缺点 | 评分 |
|------|------|------|------|------|
| **A：仅在 capability-map.md 加热力图** | 在现有清单文件底部追加 Mermaid 热力图 | 成本最低 | 单文件过度膨胀；Catalog 与 View 边界混淆；不符合 README §5 Catalog vs View 分层原则 | ❌ 否决 |
| **B：新建 04ter 正交视图**（本 ADR 采纳）| 独立视图文件作为正交视图，Catalog 承载数据、View 承载叙事 | 符合正交视图方法论（OV-P3 SSoT）；对标 Goldman/Gartner 做法；回应外部评审 P1 | 引入新视图需团队理解"热力图是 meta-architecture 工具"概念 | ✅ **采纳** |
| **C：延后到真实资金 T1 触发再建** | 暂时保留 capability-map.md v1.1.0 | 当前零额外成本 | 外部评审 P1 短板持续 open；架构终局阶段缺图；未来需要紧急补 | ❌ 否决（架构终局阶段要求全貌画出） |

### 3.2 采纳方案 B 的核心定义

#### 3.2.1 六档成熟度模型

| 档位 | 名称 | 定义 | 代码 / 文档状态 |
|------|------|------|---------------|
| **L0** | Missing | 缺失 | 无任何代码或设计稿 |
| **L1** | Design | 设计 | 设计稿完成（ADR / working-design / 视图章节），尚未施工 |
| **L2** | Draft | 草稿 | 草稿代码存在，不可用 / 未集成 |
| **L3** | Available | 可用 | 基本可用，功能完整但未达生产标准（无 SLO / 无监控 / 无告警）|
| **L4** | Production | 生产 | 生产级别，SLO + 监控 + 告警三件套齐全 |
| **L5** | Leading | 顶级 | 顶级对标（ROI 证明 + 业界公开引用）|

#### 3.2.2 14 层业务 × 7 核心能力域 = 98 格热力图

**行**（15 行）：L00 + L01 + L02 + ... + L13 14 业务层 + Cross-cutting（shared + 治理 + 前端合一行）

**列**（7 能力域）：
- 数据（Data Management & Quality）
- 因子（Factor Engineering）
- ML（Machine Learning Platform）
- 策略（Strategy & Portfolio Construction）
- 执行（Trade Execution & Order Management）
- 风控（Risk Management & Pre-trade Checks）
- 治理（Governance, Compliance, Audit）

每格填：**当前状态（L0-L5）+ 目标状态（T1/T3/T-ENDGAME 三档）+ Gap-to-Target 差距 + 工时估算 + 对标证据**。

#### 3.2.3 三档目标状态

| 目标档位 | 触发条件 | 要求 |
|---------|---------|------|
| **T1 真实资金接入** | 接入真实券商 API 开始真金白银交易 | 全体 ≥ L3；关键层（L00/L04/L05/L06）≥ L4 |
| **T3 AI 自治升格** | OQ-062 AI 自治从 P4 升至 P2/P1 | 全体 ≥ L4；核心层（L02/L04/L05/L06/L10）≥ L5（顶级对标）|
| **T-ENDGAME 顶级机构对标** | 5-8 年跨度，全面对标 Goldman/JPM/Two Sigma | 14 层 × 7 域 98 格中 ≥ 80% 达 L4+ 、≥ 30% 达 L5 |

#### 3.2.4 当前基线快照（2026-04-19）

| 层 / 能力域 | 数据 | 因子 | ML | 策略 | 执行 | 风控 | 治理 |
|------------|------|------|------|------|------|------|------|
| L00 数据源 | L2 | - | - | - | - | - | L1 |
| L01 数据接入 | L2 | - | - | - | - | - | L1 |
| L02 因子引擎 | L1 | L2 | - | - | - | - | L1 |
| L03 信号生成 | - | L1 | L1 | L2 | - | L1 | L1 |
| L04 风控 | - | - | - | - | - | L2 | L2 |
| L05 组合构建 | - | - | - | L2 | - | L1 | L1 |
| L06 交易执行 | - | - | - | - | L2 | L2 | L1 |
| L07 交易后 | L1 | - | - | - | L1 | - | L1 |
| L08 人机接口 | - | - | - | L3 | - | - | L2 |
| L09 研究创新 | L2 | L1 | L1 | L1 | - | - | L1 |
| L10 合规 | - | - | - | - | - | L1 | L1 |
| L11 ML 平台 | - | - | L1 | - | - | - | L1 |
| L12 遥测 | L1 | - | - | - | - | - | L1 |
| L13 SRE | - | - | - | - | - | - | L1 |
| Cross-cutting | L3（shared）| - | - | - | - | - | L3（治理）/ L0（前端）|

**总体基线评估**：当前处于 L1-L2 设计/草稿阶段为主，L3 可用档只有 L08 人机接口（CLI + Feishu Bot）+ Cross-cutting shared（契约）+ Cross-cutting 治理（scripts/governance/ + 39→45 治理系统）。

#### 3.2.5 Gap-to-Target 总工时估算

| 目标 | 工时 | 时间跨度 |
|------|------|---------|
| T1 真实资金 | ~120 人日 | Sprint 0-8（约半年）|
| T3 AI 自治 | ~400 人日 | 1-2 年 |
| T-ENDGAME 顶级对标 | ~2000+ 人日 | 5-8 年 |

### 3.3 季度 Review 机制

| 节奏 | 执行人 | 动作 |
|------|--------|------|
| **季度末**（2026-07-19 Q3 / 2026-10-19 Q4 / 2027-01-19 Q1 循环）| 架构师（Owner + Opus 配合）| 刷新热力图评分（L0-L5 调整），更新 Gap-to-Target 差距描述 |
| **年度末** | 执委会（当前 = Owner 本人 + AI 协作） | 锁定下一年度目标状态，调整投资强度（Low/Medium/High/Critical）|

### 3.4 与 `architecture-model/cross-cutting/capability-heatmap.yaml` 的数据承载关系

| 层 | 角色 | 版本 |
|----|------|------|
| `architecture-model/cross-cutting/capability-heatmap.yaml` | **数据层 SSoT**（Catalog 清单）| v1.1.0（R57 批次 E H2 已落地，含 Maturity L1-L5 + Investment Intensity 四档 + 判断理由三列）|
| `04ter-capability-heatmap.md` | **可视化层视图**（View 热力图）| v1.0.0（本 ADR 交付）|

**数据流**：04ter 读取 capability-map.md 数据 + 扩展维度（6 档 L0 引入、行 × 列 98 格矩阵、目标状态三档、Gap-to-Target 工时）→ 渲染为 Mermaid 热力图。capability-map 是数据层 SSoT，04ter 是可视化层叙事视图。

### 3.5 热力图不承载代码（边界铁律）

**硬约束**：

- 04ter 是 **meta-architecture 层面的可视化治理工具**
- 评分由架构师主观评估（有对标证据支撑），不是自动从代码行数 / 覆盖率计算
- 每格描述的"代码状态"（如 L3 Available）是对代码仓库实际能力的抽象评估，不是代码指标
- **不引入自动扫描脚本**（如果引入则沦为 SAST/SCA 工具而非 EA 治理工具）

## 4. 影响（Consequences）

### 4.1 正面影响

- ✅ **外部评审 P1 短板消化**：回应四家 AI 评审共识的"top-tier 机构必备"诉求
- ✅ **治理流程形式化**：季度 review + 年度执委会拍板机制落地
- ✅ **读者 10 秒看懂全貌**：98 格热力图 + 三档目标状态 + Gap-to-Target 差距
- ✅ **正交视图方法论二次验证**：与 ADR-0011 共享 OV-P1~P5 铁律，证明正交视图方法论可批量引入
- ✅ **与 capability-map.md 形成 Catalog-View 分层**：符合 README §5 "Catalog 列 what + View 讲 why" 原则

### 4.2 负面影响

- ⚠️ **评分主观性**：L0-L5 评分依赖架构师判断 → 缓解：每格必须附"对标证据"列（业界公开资料引用）+ 季度同行 review + 年度执委会质询
- ⚠️ **维护成本**：季度刷新热力图评分 + 年度目标状态调整 → 缓解：节奏固定（季度末 + 年度末），模板化，每次约 2 小时
- ⚠️ **概念理解成本**：团队需理解"热力图是 meta-architecture 工具不是 SAST 工具" → 缓解：§3.5 边界铁律明示 + 视图文件顶部"视图性质"强制声明

### 4.3 缓解措施

| 风险 | 缓解 |
|------|------|
| 热力图评分失真（过高 / 过低）| "对标证据"列强制引用业界公开资料；年度执委会质询 |
| 成为 dead document（久不刷新）| 季度 review 节奏写入任务书 serial-execution-plan + 季度末自动提醒 |
| 与 capability-map.md 数据漂移 | capability-map.md 是 SSoT，04ter 渲染时必须读取 capability-map 最新数据；每季度刷新时先 diff capability-map 变动 |

## 5. 落地证据（Implementation Evidence）

| 交付物 | 位置 | 状态 |
|-------|------|------|
| 正交视图文件 | `target-architecture/04ter-capability-heatmap.md` v1.0.0 active | ✅ 已落盘 |
| 本 ADR | `adr/adr-0012-capability-maturity-heatmap-view.md` v1.0.0 accepted | ✅ 已落盘 |
| README 方法论 + 导航 | `target-architecture/README.md` v1.7.0 §1ter + §2 + §4 | ✅ 已更新（与 ADR-0011 同批）|
| 数据层承载 | `architecture-model/cross-cutting/capability-heatmap.yaml`（R57 已落地，本 ADR 不变动）| ✅ 已就位 |
| OQ-084 即时关闭 | `open-questions/open-questions-register.md` | 🟡 J1 批次 j1-j 任务执行 |
| rationale-log | `architecture-rationale-log.md` v1.30.0 R70 | ✅ 已登记 |

## 6. 相关决策与引用

- **R70**（本 ADR 对应 rationale）
- **OQ-084**（本 ADR 同批关闭）
- **ADR-0011**（Runtime Planes 正交视图，本 ADR 同批次 J1 姊妹 ADR，共享正交视图方法论 OV-P1~P5）
- **R57 / 批次 E H2**（`business-capability-map.md` v1.1.0 Maturity + Investment Intensity 三列，本 ADR 读取其数据）
- **外部评审 P1 短板**：`tests/外部评审.md` 四家 AI 评审（Gemini 2.5 Pro / GPT-5 Thinking / Claude Opus / Grok）共识
- **方法论基础**：ArchiMate 3.2 Capability Map + Gartner IT Capability Framework（ITScore）+ Goldman Sachs EA Capability Dashboard

## 7. 修订记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-04-19 | 1.0.0 | 初版 accepted。S15-Phase1 J1 批次与 ADR-0011 同批拍板。用户"选项 β"合并 Capability Heatmap 至 J1 批次。零业务决策变动，零代码影响。视图文件 04ter v1.0.0 active + 本 ADR accepted + README v1.7.0 §1ter 整节正交视图方法论 + §2 清单 +1 行 + §4 Mermaid 新增 CHM 黄色高亮节点。与 capability-map.md v1.1.0 形成 Catalog-View 分层承载关系。|
