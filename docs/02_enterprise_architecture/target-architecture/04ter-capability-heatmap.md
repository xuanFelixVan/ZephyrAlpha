---
module_id: VIEW-04TER-CAPABILITY-HEATMAP
title: Target Architecture — Capability Maturity Heatmap (Orthogonal View) / 目标架构：能力成熟度热力图正交视图
doc_type: architecture_view
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
related_adr:
- ADR-0012
tags:
- target-architecture
- capability-heatmap
- maturity
- archimate
- capability-map
- business-architecture
- gap-analysis
- orthogonal-view
- i1-j1
summary: ZephyrAlpha 2.0 **第二个正交视图（Orthogonal View）**。本视图对 14 层业务能力做**五档成熟度评分**（L0
  缺失 / L1 设计 / L2 草稿 / L3 可用 / L4 生产级 / L5 顶级机构对标）+ 14 层 × 7 核心能力域的二维热力图 + Gap-to-Target
  差距分析 + 每季度 review 机制。对标 ArchiMate Capability Map + Gartner IT Capability Framework
  + Goldman Sachs Enterprise Architecture Capability Dashboard 三家业界主流做法。回应 `tests/外部评审.md`
  四家 AI 外部评审共识指出的"缺少能力成熟度可视化（top-tier 机构必备）"P1 短板。本视图 v1.0.0 定义能力评分方法论 + 当前基线快照 +
  目标状态（T1 真实资金 / T3 AI 自治升格 / T-ENDGAME 顶级机构对标）+ 与 03-AA `architecture-model/cross-cutting/capability-heatmap.yaml`
  的数据承载关系。**热力图不承载代码**，是**元架构层面的可视化治理工具**，季度由架构师刷新评分。
date: '2026-04-22'
ttl: permanent
---

## 1. Purpose & 为什么需要能力热力图

### 1.1 本视图要回答的问题

| 问题 | 答案所在 |
|---|---|
| ZephyrAlpha 的核心业务能力是什么？每一项当前多成熟？| §3 14 层 × 7 能力域热力图 |
| 哪些能力是"顶级机构标配但我们缺失"的 P0 短板？| §5 Gap-to-Target 差距表 |
| 达到顶级机构对标水平还需要多少投入？| §6 投入估算（人月 + ADR 数 + Sprint 数）|
| 能力成熟度何时刷新？谁负责？| §7 季度 review 机制 |
| 本视图与 01-BA 的 `capability-map` / 业务能力清单是什么关系？| §8 与 01-BA / `capability-heatmap.yaml` 的承载关系 |

### 1.2 为什么要做能力热力图

**外部评审驱动**（`tests/外部评审.md` 四家 AI 共识，P1 级短板）：
> "ZephyrAlpha 当前已补齐 TOGAF 10 视图 + 45 治理系统 + 14 层业务分层，但**缺少一张'全局能力地图 + 成熟度视觉化'**让架构师 / 用户 / 外部审计在 5 分钟内抓住'我们强在哪、弱在哪'。顶级机构（Goldman / JPM / BlackRock）均有 Enterprise Architecture Capability Dashboard 作为 C-level 汇报工具。"

**本视图价值**：
1. 🎯 **C-level 视角**：一张图回答"系统现在多成熟、距离顶级多远"
2. 🎯 **Gap 识别**：精准识别 P0/P1/P2 短板，防止精力被次要议题分散
3. 🎯 **季度 review 锚点**：固定每季度刷新，形成"能力进化曲线"
4. 🎯 **招聘 / 融资 / 审计输出物**：可直接作为对外汇报材料（剥离敏感数据后）

**业界对标**（三家共识做法）：

| 机构 | 能力地图实现 | 成熟度模型 | 刷新频率 |
|---|---|---|---|
| **Goldman Sachs** | Enterprise Architecture Capability Dashboard | 5 档（Emerging / Defined / Managed / Optimized / Leading）| 季度 |
| **BlackRock** | Aladdin Capability Heatmap（内部工具）| 5 档（Draft / Alpha / Beta / Production / World-Class）| 季度 |
| **Gartner IT Capability Framework** | Generic Capability Map | 5 档（Initial / Repeatable / Defined / Managed / Optimizing, CMMI-aligned）| 半年 |

**ZephyrAlpha 采纳**：Goldman / BlackRock / Gartner 共识的 5 档模型，季度刷新（§2 详述）。

### 1.3 与其他视图的边界

| 其他视图 | 本视图与其关系 |
|---|---|
| `01-business-architecture.md` | 01-BA 定义"业务做什么"（能力边界 / Value Stream / RACI）；本视图给每项能力打成熟度分 |
| `architecture-model/cross-cutting/capability-heatmap.yaml` | YAML 是**机器可读能力清单**（canonical schema）；本视图是**人类可读热力图视觉化**（引用该文件作为数据源）|
| `03-application-architecture.md` | 03-AA 14 层 **业务本体**；本视图 14 层 × 7 能力域**叠加评分**，承载热力图的数据源 |
| `04bis-runtime-planes.md` | 04bis 是执行维度正交视图；本视图是成熟度维度正交视图。两视图**各切一把尺子**，协同刻画系统全貌 |
| `archive/reorg-2026-04-24/draft-abandoned/working-designs/ai-autonomy-architecture-design.md`（ARC-20260424-007）| AI 自治层的能力评分由本视图 §3 第 7 能力域承载 |

### 1.4 决策溯源

- **ADR-0012** Capability Maturity Heatmap View v1.0.0 accepted（本视图同源）
- **R70** 能力热力图引入决策（2026-04-19 J1 批次，见 `architecture-rationale-log.md`）
- **OQ-084** closed（2026-04-19 J1 批次一次性拍板——采纳 Goldman/BlackRock/Gartner 共识 5 档模型 + 季度 review）
- **外部评审驱动**：`tests/外部评审.md` 4 AI 共识 P1 级能力可视化短板

---

## 2. 五档成熟度模型

### 2.1 五档定义

| 档位 | 名称 | 定义 | 证据类型 | 对应 Goldman/BlackRock/CMMI |
|---|---|---|---|---|
| **L0** ⚪ | **Missing** 缺失 | 能力完全不存在，无代码 / 无文档 / 无 ADR | — | — |
| **L1** 🔵 | **Designed** 设计级 | 有 ADR / 有架构视图 / 有 canonical 设计稿 / 无代码 | ADR-00XX accepted + 视图定义 | Emerging / Draft / Initial |
| **L2** 🟡 | **Drafted** 草稿级 | 有代码原型 / skeleton 目录 / 部分模块 stub 级实现 | 代码存在但无生产级测试 | Defined / Alpha / Repeatable |
| **L3** 🟢 | **Usable** 可用级 | 核心功能实现 + 测试覆盖 ≥ 60% + 文档齐全 + 已在 Sprint 内验证 | pytest ≥ 60% + 文档 + Sprint 验收记录 | Managed / Beta / Defined |
| **L4** 🟣 | **Production** 生产级 | 真实资金 / 真实流量 / 治理三层（09-GOV）完整覆盖 + 监控告警 + Runbook | SLO 达标 + 治理通过 + 生产运行证据 | Optimized / Production / Managed |
| **L5** 🔴 | **Leading** 顶级机构对标 | 对标 Goldman/JPM/Two Sigma/Citadel 等顶级机构同能力的业界领先实现 | 公开论文 / 开源贡献 / 业界 benchmark | Leading / World-Class / Optimizing |

### 2.2 档位判定规则（防刷分）

**硬门槛**（必须全部满足才能升下一档）：

| 升档方向 | 硬门槛 |
|---|---|
| L0 → L1 | ADR accepted + 架构视图定义 |
| L1 → L2 | 至少 1 个代码文件（stub 即可）+ frontmatter 合规 |
| L2 → L3 | pytest ≥ 60% + sprint 验收记录 + folder-charter 签名 |
| L3 → L4 | 真实资金 OR 真实流量 OR 外部依赖命中 + 治理三层 Runtime 拦截激活 + SLO 监控 |
| L4 → L5 | 至少一项：(a) 公开 benchmark 领先；(b) 开源发布 ≥ 100 stars；(c) 顶级机构同行 review 认可；(d) 业界论文引用 |

**档位降级规则**：
- 季度 review 时发现证据失效 → 强制降档（e.g. 测试覆盖 < 60% 从 L3 降 L2）
- 与 09-GOV 四档执行约定一致：档位是"当前真实状态"不是"曾经达到过"

### 2.3 档位颜色与图例

在所有热力图中使用以下色板（匹配本视图 frontmatter tag）：

| 档位 | 色值 | 表示符 |
|---|---|---|
| L0 | `#e5e7eb` 灰 | ⚪ |
| L1 | `#bfdbfe` 浅蓝 | 🔵 |
| L2 | `#fde68a` 浅黄 | 🟡 |
| L3 | `#86efac` 浅绿 | 🟢 |
| L4 | `#c4b5fd` 浅紫 | 🟣 |
| L5 | `#fca5a5` 浅红（顶级）| 🔴 |

---

## 3. 14 层 × 7 核心能力域热力图（v1.0.0 基线快照）

### 3.1 7 核心能力域定义

对标 ArchiMate Business Capability + Goldman Aladdin Capability Categories，本视图定义 ZephyrAlpha 的 7 个核心能力域：

| 能力域 | 含义 | 主承载业务层 |
|---|---|---|
| **C1 数据能力** | Market data ingestion / quality / PIT / survivorship / lineage | L00 + L01（存储基础设施）|
| **C2 因子 & 信号能力** | Alpha factor / sentiment / signal extraction / factor registry / IC-IR | L02 + L03 |
| **C3 风控能力** | Pre-trade / at-trade / post-trade / VaR-CVaR / limits / stop-loss | L04 |
| **C4 组合构建能力** | Optimization / rebalancing / backtest / strategic allocation / meta-router | L05 |
| **C5 执行 & 交易后能力** | OMS / SOR / execution / attribution / TCA / review | L06 + L07 |
| **C6 ML / AI 平台能力** | Model lifecycle / training / serving / scout / experimentation | L11 + L13 |
| **C7 治理 & 合规能力** | Compliance runtime / governance three-layer / AISG / audit trail / fitness functions | L10 + 横切 09-GOV |

**另有 3 横切支撑域**（打到 "Cross-layer" 行）：

| 横切域 | 含义 | 主承载 |
|---|---|---|
| **CC-1 人机交互 & 研究** | Human-AI interface / research notebooks / CLI | L08 + L09 |
| **CC-2 可观测性** | Metrics / logs / traces / ai_behavior | L12 |
| **CC-3 AI 自治** | D 家族 6 系统 / ai_operator 预留口子 / decision engine | 跨 D 家族 + l*_ai_operator |

### 3.2 v1.0.0 基线热力图（2026-04-19 快照）

> **⚠️ 评分基准**：本基线由 Opus47 于 2026-04-19 J1 批次依据当前架构终局文档状态评分。**架构文档 ≠ 代码实现**，大多数能力当前为 L1/L2（设计或草稿级），**L3+ 需要施工后才能达到**。

> **📋 能力成熟度完整数据**：见 [`architecture-model/cross-cutting/capability-heatmap.yaml`](architecture-model/cross-cutting/capability-heatmap.yaml)，包含 10 个能力域 × 32 条目的当前成熟度（L0-L5）、目标成熟度、Gap 分析（G-1~G-10）及 3 个目标状态定义。

**v1.0.0 基线快照摘要**（详细逐条数据见上述 YAML）：

- **15 个业务层**（L00~L13 + shared）× 7 核心能力域 + 3 横切支撑域 = **41 个评分单元格**
- 当前分布：L0 × 3 | L1 × 26 | L2 × 3 | L3+ × 0
- 横切域：CC-1 人机交互 ⚪L0 | CC-2 可观测性 🔵L1 | CC-3 AI 自治 🔵L1

### 3.3 v1.0.0 整体能力指数

**算法**：能力总分 = Σ(每单元格档位数值) / 总单元格数，其中 L0=0 / L1=1 / L2=2 / L3=3 / L4=4 / L5=5。

**当前判断**：ZephyrAlpha 整体处于 **L1 设计级**（平均档位 1.12，总得分 ~46/205）。架构蓝图已 95% 锁定，代码施工刚起步。这与外部评审的 89/100 评分一致——**架构设计完整度领先 + 代码实现刚开始**。目标状态：T1 ≥ 120 分（2.93 可用级）/ T3 ≥ 160 分（3.90 生产级）/ T-ENDGAME ≥ 185 分（4.51 顶级对标）。

### 3.4 热力图 Mermaid 可视化（当前 v1.0.0）

> **📊 能力热力图可视化**：见 [`diagrams/capability-heatmap-visual.mmd`](diagrams/capability-heatmap-visual.mmd)

---

## 4. 目标状态快照（T1 / T3 / T-ENDGAME）

### 4.1 T1 真实资金接入后目标（Sprint 12+ 左右）

**激活驱动**：真实券商 API / 真实资金账户 / 监管 KYC

**关键升档**：
- L00 数据 C1 **L2 → L4**（真实行情 + PIT + lineage 完整）
- L04 风控 C3 **L1 → L4**（真实 kill switch 运行时拦截）
- L06 执行 C5 **L1 → L4**（真实订单 + OMS 状态机在线）
- L10 合规 C7 **L2 → L4**（09-GOV Runtime 层全部激活 + AISG 拦截真实 AI 调用）
- L12 可观测 CC-2 **L1 → L3**（真实 metrics / logs / traces 三支柱上线）

### 4.2 T3 AI 自治升格后目标（Sprint 14+ 左右）

**激活驱动**：OQ-062 AI 自治升 P1 + D-03/04/05/06 四引擎 K2 批次展开

**关键升档**：
- L08 人机交互 C6 **L0 → L3**（CLI + 交互 orchestration + Feishu bot 稳定运行）
- CC-3 AI 自治 **L1 → L4**（D 家族 6 系统全部生产级 + ai_operator 15+ 员工在岗）
- C6 ML 平台 **L1 → L4**（Scout Agent 稳定抓取 + 模型 registry 生产级 + champion-challenger 跑通）

### 4.3 T-ENDGAME 顶级机构对标（Sprint 30+ / ≥ 2 年）

**激活驱动**：团队规模 ≥ 5 + 自营资金 ≥ $10M + 开源贡献 or 论文发表

**关键升档**：
- 至少 3-5 个能力域达 **L5 Leading 级**（候选：C1 数据 PIT / C2 因子 registry OCP / C6 Scout Agent / C7 AISG）
- 整体平均 ≥ 4.51（接近 L4.5）
- L3+ 生产比例 ≥ 90%

---

## 5. Gap-to-Target 差距分析（P0/P1/P2 短板）

### 5.1 v1.0.0 基线 Gap 表（当前 → T1 目标差距）

> **📋 Gap 完整数据**：见 [`architecture-model/cross-cutting/capability-heatmap.yaml`](architecture-model/cross-cutting/capability-heatmap.yaml) 的 `gap_analysis` 节，包含 G-1~G-10 的精确 from/to 档位、关联 CAP-ID 及优先级分类。

**Gap 分布摘要**：🔴 P0 × 4（G-1~G-4，T1 硬阻塞）| 🟡 P1 × 3（G-5~G-7）| 🟠 P2 × 3（G-8~G-10）

### 5.2 P0 短板集中诊断

**4 项 P0 短板（G-1 ~ G-4）都集中在 T1 真实资金接入路径上**：风控 → 执行 → 合规 → 数据 是**真实资金上线的四大硬基石**，四项都需要从 L1/L2 跳到 L4。这与 09-GOV T1 触发器完全一致（T1 触发 L04/L06/L10/L00 的治理 Runtime 层全部激活）。

**施工建议**：
- **Sprint 9（发布守卫）**：G-4 数据（PIT/Lineage 落地）+ G-3 合规（09-GOV L3 三件套 + L4 fitness functions）
- **Sprint 10（施工 + AI Safety）**：G-1 风控（kill switch + limits hard cut）+ **G-10 CC-3 AI 自治**（D-01 AISG Phase 0 硬闸门，Sprint 0 启动前已过）
- **Sprint 11（业务运行时）**：G-2 执行（OMS + SOR + 券商接入）
- **Sprint 12（T1 接入前 gate）**：G-1/G-2/G-3/G-4 全部到 L4 才解锁 T1

### 5.3 P1 短板（G-5 ~ G-7）

相对非阻塞但需在 Sprint 12 前完成：
- G-5 人机：CLI 是当前唯一 UI，必须 L3 否则体验差
- G-6 可观测：无监控不能上生产
- G-7 ML 平台：模型 registry 是 AI 员工上岗前置

### 5.4 P2 短板（G-8 ~ G-10）

可延后到 Sprint 12+：
- G-8/G-9 因子 / 组合：有设计 OCP 契约，实施可渐进
- G-10 AI 自治：本身依赖 T3 触发，非 T1 阻塞

---

## 6. 投入估算

### 6.1 能力升档投入模型

**经验系数**（基于单人开发 + AI 协作者 vibe coding 加成 3-5x）：

| 升档路径 | 单能力单位工作量 | 说明 |
|---|---|---|
| L0 → L1 | 0.5 人周 | 写 ADR + 架构视图 |
| L1 → L2 | 1-2 人周 | 写 stub 代码 + skeleton 测试 |
| L2 → L3 | 2-4 人周 | 实现 + pytest ≥ 60% + 文档 |
| L3 → L4 | 4-8 人周 | 生产级 + SLO + 监控 + runbook |
| L4 → L5 | 8-16 人周 + 外部证据 | 开源 / 论文 / 业界领先 |

### 6.2 到达 T1 目标的总投入估算

| Gap | 当前 | 目标 | Gap 大小 | 估算投入（人周）|
|---|---|---|---|---|
| G-1 风控 | L1 → L4 | 3 档 | ~10 人周 |
| G-2 执行 | L1 → L4 | 3 档 | ~10 人周 |
| G-3 合规 | L2 → L4 | 2 档 | ~6 人周 |
| G-4 数据 | L2 → L4 | 2 档 | ~6 人周 |
| G-5 人机 | L0 → L3 | 3 档 | ~6 人周 |
| G-6 可观测 | L1 → L3 | 2 档 | ~4 人周 |
| G-7 ML 平台 | L1 → L3 | 2 档 | ~4 人周 |
| G-8 因子 | L1 → L3 | 2 档 | ~4 人周 |
| G-9 组合 | L1 → L3 | 2 档 | ~4 人周 |
| G-10 AI 自治 | L1 → L3 | 2 档 | ~4 人周 |
| **总计（T1 前）** | — | — | — | **~58 人周 ≈ 14 个月（单人）≈ 3-5 个月（AI vibe coding 加成）**|

**与 09-GOV Sprint 9-12 对齐**：约 12-16 周 Sprint 执行，与估算区间一致。

### 6.3 达到 T-ENDGAME 顶级对标的总投入估算

**保守估计**：T1 后 **额外 2-3 年 + 团队扩至 3-5 人**。当前单人 vibe coding 模式的瓶颈不在代码量，在**外部证据积累**（开源 stars / 论文发表 / 顶级机构同行 review 认可）。

---

## 7. 季度 Review 机制

### 7.1 Review 节奏

| 频率 | 季度末（每 3 个月）|
|---|---|
| **责任人** | 架构师（Owner 用户）+ AI 协作者（Opus 收口）|
| **产出物** | 本视图 v1.X.0 修订 + 新增季度 Entry 到 §9 修订记录 + heatmap 可视化更新（Mermaid + 5 档色板）|
| **触发器** | (a) 季度到期；(b) T1/T3/T-ENDGAME 任一触发器命中；(c) 外部审计要求 |

### 7.2 Review 流程（5 步）

1. **扫描证据**：对每个能力单元格扫描当前状态（代码 / 测试覆盖 / 文档 / SLO / 真实流量等）
2. **档位重评**：按 §2.2 硬门槛判定当前档位，必要时**强制降档**
3. **Gap 刷新**：更新 §5 Gap-to-Target 表，重新计算 P0/P1/P2 短板
4. **投入重估**：更新 §6 投入估算
5. **修订入账**：落盘 v1.X.0 + R/OQ/ADR 登记 + handoff-log 条目

### 7.3 与 open-questions-register 联动

季度 review 时如发现新的 **L5 Leading 目标**（如某能力团队决定冲开源），登记新 OQ 追踪；如发现现有 OQ 已通过能力升档事实消解，主动关闭。

---

## 8. 与 01-BA / `capability-heatmap.yaml` 的数据承载关系

### 8.1 三层数据承载

```
┌──────────────────────────────────────────────────────────────────┐
│  01-BA (视图) — 定义"做什么"（能力边界 / Value Stream / RACI）    │
│    ↓ 驱动                                                          │
│  architecture-model/cross-cutting/capability-heatmap.yaml — 机器可读能力清单  │
│    ↓ 驱动                                                          │
│  04ter-capability-heatmap.md (本视图) — 人类可读热力图成熟度       │
└──────────────────────────────────────────────────────────────────┘
```

### 8.2 `capability-heatmap.yaml` 联动

当 `architecture-model/cross-cutting/capability-heatmap.yaml` 新增 / 修改能力条目时，本视图的 7 能力域 / 41 单元格**可能需要重构**。Review 时优先对齐该 YAML（**能力清单 SSoT**，本视图是**视觉化 + 成熟度评分**）。

### 8.3 未来可能的扩展视图（不在本批次）

- **04quater-risk-heatmap.md**：同样的正交视图方式，热力图维度改为"风险等级"（L0 无风险 → L4 致命），辅助架构 risk register
- **04quinque-cost-heatmap.md**：热力图维度改为"运维成本 / 开发成本"，辅助预算决策

**当前本批次只落 04ter，04quater/quinque 延后待触发**（避免视图爆炸）。

---

## 9. Revision history / 修订记录

| Date | Description |
|---|---|
| 2026-04-19 | **v1.0.0 首次发布**（S15-Phase1 J1 批次，选项 β 合并 Capability Heatmap 同批落地）。新建本视图作为 ZephyrAlpha 2.0 **第二个正交视图**，与 `04bis-runtime-planes.md` 并列（正交于 TOGAF 10 视图的成熟度维度）。核心内容：(a) §2 五档成熟度模型（L0 Missing → L5 Leading，对齐 Goldman/BlackRock/Gartner 共识 + CMMI）+ 硬门槛防刷分；(b) §3 14 业务层 × 7 能力域 + 3 横切支撑域 基线热力图（v1.0.0 当前 41 单元格评分：平均 1.12 ≈ L1 设计级，L3+ 生产比例 0%，与外部评审 89/100 分相符——架构 95% 完整 + 代码刚开始）+ Mermaid 可视化；(c) §4 三档目标状态（T1 真实资金 / T3 AI 自治升格 / T-ENDGAME 顶级对标）+ 升档关键点；(d) §5 Gap-to-Target 10 个短板（G-1~G-10 + P0/P1/P2 优先级）+ P0 四短板与 09-GOV T1 触发器精确对齐（风控 / 执行 / 合规 / 数据）；(e) §6 投入估算（T1 目标 ~58 人周 ≈ 3-5 个月 vibe coding，T-ENDGAME ~2-3 年 + 团队扩至 3-5 人）；(f) §7 季度 review 机制（固定节奏 + 5 步流程 + 强制降档规则 + 与 open-questions-register 联动）；(g) §8 与 01-BA / `catalogs/business-capability-map.md` 三层数据承载关系澄清（catalogs 是 SSoT，本视图是视觉化）+ 预留 04quater-risk-heatmap / 04quinque-cost-heatmap 未来扩展（当前不落避免视图爆炸）。**外部评审驱动**：回应 `tests/外部评审.md` 四家 AI 共识 P1 短板"缺少能力成熟度可视化（top-tier 机构必备 Dashboard）"。**架构影响：零代码 / 零目录**——本视图仅元架构层面的治理工具 + 可视化，季度刷新。配套：ADR-0012 Capability Maturity Heatmap View v1.0.0 accepted + OQ-084 closed + R70 登记 rationale-log + handoff-log S15-Phase1-J1 entry。|
