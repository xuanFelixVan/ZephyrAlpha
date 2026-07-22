---
module_id: VIEW-08-OPERATIONS-ARCH
title: Target Architecture — Operations Architecture
doc_type: architecture_view
status: Draft
version: 0.2.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
valid_from: 2026-04-19
superseded_by: null
supersedes: null
related_rationale: R39
related_open_questions: []
tags:
- operations-architecture
- togaf
- sre
- runbook
- deployment
- monitoring
- backup
- disaster-recovery
- capacity
- cost
- skeleton
- 5-core-services-ops
- sli-slo
- opentelemetry
- feedback-loop-consumer
summary: TOGAF Operations Architecture 视图（骨架版）。描述系统运维全景（8 个运维域的生命周期、流程与角色），与 04-TA
  §6 的边界为：04-TA §6 = 部署图（物理节点 how），本视图 = 运维全景（生命周期+流程+角色 what）。Runbook Catalog 占位清单见
  §9，§10 列出激活触发条件。
date: '2026-04-22'
ttl: permanent
---

# Target Architecture — Operations Architecture （被恢复）
# 目标架构：运维架构（骨架）

> ⚠️ **本视图当前状态为 `skeleton`。**
>
> 运维架构的详细内容（Runbook 规程、容量规划数字、DR 演练计划等）在当前单人开发、无生产环境、无真实资金的阶段尚无落地条件。
>
> 本骨架的作用：
> 1. **占位存档**——确保 TOGAF 8 视图体系完整，8 个运维域的结构不缺席
> 2. **边界声明**——与 `technology_architecture.md §6` 的职责边界清晰
> 3. **Runbook 目录树**——§9 预置 Runbook 清单框架，后续按域补齐
> 4. **激活门控**——§10 明确"何种条件达到时必须补齐"
>
> 在激活条件触发前，**禁止向本视图添加实质性 Runbook 内容**（防止过度设计）。

---

## §1 Purpose & 与 04-TA §6 的边界 / Purpose & Boundary

### 1.1 本视图回答的问题

Operations Architecture（运维架构视图）回答：

- 系统的**运维域**如何划分（部署、监控、备份、灾备、变更、事件、容量、成本）？
- 每个运维域的**生命周期流程**是什么（谁做什么、什么时候做）？
- **角色与职责**如何分配（单人阶段 = 架构师 = 运维员 = 数据工程师）？
- **Runbook** 清单（操作手册目录）是什么？

### 1.2 与 04-TA §6 的边界

| 视图 | 回答 | 类比 |
|------|------|------|
| `technology_architecture.md §6` | **物理节点 How**：用了什么容器、什么机器、什么网络拓扑，如何部署 | 建筑的"施工图" |
| **本视图（operations_architecture.md）** | **生命周期 What**：什么时候做什么运维操作、谁负责、流程是什么 | 建筑的"物业管理手册" |

两者**互补不替代**：04-TA §6 告诉你"部署长什么样"，本视图告诉你"部署之后如何维护"。

---

## §2 Operations Domains / 运维域

本视图覆盖 8 个运维域：

| 域 | 英文名 | 核心职责 |
|----|--------|---------|
| D1 | **Deployment** | 发布流程、版本管理、回滚策略 |
| D2 | **Monitoring & Observability** | 指标采集、日志聚合、链路追踪、告警 |
| D3 | **Backup & Data Recovery** | 数据备份策略、恢复程序、验证周期 |
| D4 | **Disaster Recovery & BCP** | 灾难恢复目标（RTO/RPO）、业务连续性计划 |
| D5 | **Change Management** | 变更审批流程、变更窗口、变更后验证 |
| D6 | **Incident Management** | 事件响应流程、告警分级、复盘（Post-Mortem）|
| D7 | **Capacity Planning** | 资源用量预测、扩容触发条件、成本预算 |
| D8 | **Cost Management** | 运营成本监控、LLM Token 费用、数据订阅成本 |

---

## §3 D1 — Deployment / 部署域

**职责**：管理软件版本从开发到生产的全生命周期发布流程。

当前状态：
- 单人本地开发环境（localhost），无 CI/CD Pipeline
- 代码通过 git 管理，部署 = `git pull` + 手动启动脚本
- 版本号遵循项目 CHANGELOG 约定

> 🚧 **占位**：CI/CD Pipeline（GitHub Actions / 本地 Makefile）、蓝绿部署 / 金丝雀发布策略、版本回滚 Runbook 待激活后设计。
>
> **关联**：`technology_architecture.md §6`（部署图）

---

## §4 D2 — Monitoring & Observability / 监控与可观测性域

**职责**：采集系统运行指标、日志、链路追踪，建立告警体系。

### 4.1 架构定位

- `infra_ops/` 层是传统可观测性代码归属（OpenTelemetry 导出）
- **Feedback Loop Engine (FLE)** 是 6 大核心服务的"自动化运维大脑"，所有服务指标→FLE→异常检测→动作分派
- 两者关系：OpenTelemetry 面向"人工看板 + 外部工具"；FLE 面向"系统内部自调节"

### 4.2 experimental SLI/SLO 基线（P0 必采）

| 服务 | SLI 指标 | SLO 阈值 | 告警动作 |
|------|---------|:--------:|---------|
| Context Engine | `build()` 延迟 P99 | < 500ms | FLE → CE 降级规则基 |
| Vector Memory | `search()` 延迟 P99 | < 200ms（稳态）| FLE → 检查 ChromaDB 健康 |
| Vector Memory | `bulk_bootstrap` 冷启动 | < 60s/200 文档 | FLE → 容量检查 |
| Agent Orchestrator | 任务 P99 排队时延 | < 5s | FLE → 并发阈值告警 |
| Agent Orchestrator | 幻觉检测漏检率 | < 10% | TECH-09 升级触发 |
| Feedback Loop | 异常检测延迟 | < 30s | 自监控自告警 |
| LSG | 误拦率 | < 2% | 红队评估触发 |
| LSG | 漏拦率 | < 5% | TECH-16 升级触发 |
| LSG | fail-closed 触发频率 | < 0.1%/天 | 人工介入 |

**SLO 来源**：每项 SLO 都有 `technology_landscape.yaml upgrade_watchboard` 中对应的升级阈值。

### 4.3 指标采集拓扑

```
各服务 (VMS/CE/Orc/FLE/LSG)
        │ metrics.emit()
        ▼
┌────────────────────────┐
│   FLE collect_metric() │ ──→ SQLite .runtime/sqlite/feedback.db
└───────┬────────────────┘     （数据量 > 100 万/天 触发 TECH-13 升级 InfluxDB）
        │
        ▼
┌────────────────────────┐
│   detect_anomaly()     │ EMA + 滑动窗口
└───────┬────────────────┘
        │
        ▼
┌────────────────────────────────────┐
│   dispatch_action() via Protocol   │
│   [ CE.降级 / Orc.限流 / 人工告警 ]│
└────────────────────────────────────┘
```

**导出通道**：

- `infra_ops/` 定期从 FLE 导出到本地文件（JSON Lines）
- beta 启用 OpenTelemetry Collector → Prometheus/Grafana 标准栈

> 🚧 **beta 扩展**：Grafana Dashboard 模板、On-Call 流程、Alertmanager 规则集待 beta 补齐（本文档届时升级为 v1.0.0 active）。

---

## §5 D3 — Backup & Data Recovery / 备份与数据恢复域

**职责**：保障数据可恢复性，制定备份策略与验证周期。

当前状态：
- 历史行情数据（Parquet / HDF5）存放本地磁盘，无自动备份
- 代码库通过 Git 分布式版本控制实现源码备份（推送至远程 origin）
- 关键配置与密钥：本地 `.env`，无跨设备备份

> 🚧 **占位**：3-2-1 备份策略（3 份数据 / 2 种介质 / 1 份异地）、备份验证 Runbook、恢复时间目标（RTO < ? 小时）待激活后定义。

---

## §6 D4 — Disaster Recovery & BCP / 灾难恢复与业务连续性域

**职责**：定义 RTO / RPO 目标，制定业务连续性计划（BCP）。

当前状态：
- 无真实资金，灾难影响仅限研究数据丢失风险
- RTO / RPO 尚未量化（见 `business_architecture.md §5` NFR 待完善）
- BCP 场景：硬盘故障 / 主机失联 / 外部 API 断供

> 🚧 **占位**：RTO / RPO 量化目标（接入真实资金后必须）、故障切换（Failover）流程、DR 演练计划（年度）待激活后补齐。

---

## §7 D5 — Change Management / 变更管理域

**职责**：管理系统变更的审批、执行与验证流程，防止未授权变更。

当前状态：
- 所有变更通过 git commit 记录，commit message 遵循 Conventional Commits
- 重大架构决策通过 `architecture-rationale-log.md` 登记（R 系列）
- AI 辅助变更：`encoding-tool-guard.mdc` + `doc-governance.mdc` 规则约束 agent 操作范围

> 🚧 **占位**：正式变更审批流程（CAB）、变更窗口定义（生产禁止在行情时段变更）、变更后验证清单（Runbook RB-D5-01）待激活后补齐。

---

## §8 D6 — Incident Management / 事件管理域

**职责**：定义告警分级、响应流程、升级路径与事后复盘。

当前状态：
- 单人系统，无正式 On-Call 机制
- 事件记录通过 `handoff-log.md` 手工追踪
- 飞书（EI-004）用于非正式通知

> 🚧 **占位**：P0/P1/P2/P3 告警分级定义、事件响应流程（Detection → Triage → Mitigate → Resolve → Post-Mortem）、Post-Mortem 模板（Runbook RB-D6-01）待激活后补齐。
>
> **参考**：安全类事件响应流程已在 [`security_architecture.md §11`](./security_architecture.md) experimental 启动，本域 D6 在非安全运维事件上做增量补齐。

---

## §8A 6 Core Services — Runtime Operations / 6 大核心服务运维治理

> 新增于 v0.2.0（2026-04-24）。本节专项描述 6 大核心服务（LSG/CE/Orc/VMS/FLE/KB）的 experimental 运维流程，是 §3-§8 的 8 大运维域在"AI 基础设施"上的具化。

### 8A.1 服务生命周期（experimental 单机单进程）

```
系统启动 (python -m zephyr.orchestrator.bootstrap)  # 未来实现点，LPC 双轨下由 Orchestrator 启动 DAG
   │
   ▼
1. 加载 vibe_config.yaml
   │
   ▼
2. 按依赖顺序启动（DAG 序）：
      LSG  →  VMS  →  CE  →  Orc  →  FLE
      （每个服务 health check 通过才启动下一个）
   │
   ▼
3. FLE 订阅全部服务的 metrics channel
   │
   ▼
4. 服务 Ready → Agent 可消费

系统停止 (Ctrl+C / SIGTERM)
   │
   ▼
反向停止顺序：FLE → Orc → CE → VMS → LSG
   （每个服务完成 in-flight 任务后退出）
```

### 8A.2 健康检查合约（所有服务必须实现）

每个服务必须暴露标准化 health check 接口（详见各自 interface 规范 §8）：

```python
class ServiceHealthProtocol(Protocol):
    def health(self) -> dict:
        return {
            "status": "healthy" | "degraded" | "unhealthy",
            "version": "x.y.z",
            "uptime_seconds": int,
            "last_error": str | None,
            "dependencies": {...},  # 上游服务状态
        }
```

**巡检频率**：experimental 由 FLE 每 60 秒轮询一次，异常立即进入 detect_anomaly 流程。

### 8A.3 降级矩阵

| 服务 | 降级条件 | 降级行为 | 恢复条件 |
|------|---------|---------|---------|
| LSG | **不降级**（fail-closed）| N/A（异常即拒绝调用）| N/A |
| CE | LLM 压缩失败 | 规则基截断 + degraded=True | Qwen2.5-3B 服务恢复 |
| CE | VMS 检索失败 | 降级到 grep/rg 文件检索 | VMS 恢复 |
| VMS | ChromaDB 损坏/首次启动 | `search()` 返回空 + degraded=True | bulk_bootstrap 完成 |
| Orc | SQLite 锁争用 | 任务延迟执行 + 告警 | 锁释放 |
| Orc | Agent 沙箱逃逸 | 立即 kill + IR-SEC-002 | 人工审查 |
| FLE | SQLite 容量满 | 归档旧数据 + 暂停异常检测 | 容量恢复 |

### 8A.4 配置热更新

**experimental 约束**：配置文件修改需要重启服务（无热更新）。

**beta 目标**：LSG 策略表 + Orc 白名单 + FLE 阈值支持热更新，减少 AI 协作中断。

### 8A.5 日常巡检清单（experimental P0）

建议每日一次：

- [ ] FLE anomaly 累计 < 5 条（否则启动调查）
- [ ] LSG fail-closed 触发 < 10 次（否则检查策略表）
- [ ] Orc SQLite audit.db 大小 < 100MB（超阈值归档）
- [ ] VMS ChromaDB 持久化大小 < 500MB（TECH-04 upgrade_watchboard）
- [ ] `.runtime/logs/session/` 30 天内无新 incident 文件

---

## §9 Runbook Catalog / 操作手册目录

> **本节为占位目录清单。** Runbook 文件将在各运维域激活时独立建档，统一存放于 `docs/_working/runbooks/`（待创建）。

| ID | 域 | Runbook 名称 | 触发场景 | 状态 |
|----|---|--------------|---------|------|
| RB-D1-01 | 部署 | 标准发布 Runbook | 每次版本发布 | 🔲 待建 |
| RB-D1-02 | 部署 | 紧急回滚 Runbook | 发布后出现严重缺陷 | 🔲 待建 |
| RB-D2-01 | 监控 | 告警响应标准流程 | P0 告警触发 | 🔲 待建 |
| RB-D2-02 | 监控 | 监控巡检清单 | 每周日常巡检 | 🔲 待建 |
| RB-D3-01 | 备份 | 数据备份验证 Runbook | 每月备份验证 | 🔲 待建 |
| RB-D3-02 | 备份 | 数据恢复演练 Runbook | 每季度 DR 演练 | 🔲 待建 |
| RB-D4-01 | 灾备 | 主机故障切换 Runbook | 主机不可用 | 🔲 待建 |
| RB-D5-01 | 变更 | 变更后验证清单 | 每次变更发布后 | 🔲 待建 |
| RB-D6-01 | 事件 | Post-Mortem 模板 | 每次 P0/P1 事件后 | 🔲 待建 |
| RB-D7-01 | 容量 | 资源用量月度报告 | 每月容量复盘 | 🔲 待建 |
| RB-D8-01 | 成本 | LLM Token 费用报告 | 每月成本复盘 | 🔲 待建 |
| RB-SVC-01 | 6大核心服务 | 冷启动 Runbook（依赖 DAG 序）| 系统重启 | 🔲 experimental P0 |
| RB-SVC-02 | 6大核心服务 | VMS ChromaDB 重建 Runbook | 持久化损坏 | 🔲 experimental P0 |
| RB-SVC-03 | 6大核心服务 | LSG 策略表更新 Runbook | 红队发现新攻击模式 | 🔲 experimental P0 |
| RB-SVC-04 | 6大核心服务 | FLE SQLite 归档 Runbook | 数据量 > 100MB | 🔲 experimental P1 |
| RB-SVC-05 | 6大核心服务 | Agent Sandbox 逃逸响应 | 沙箱违规告警 | 🔲 experimental P0（→ IR-SEC-002）|

---

## §10 Activation Triggers / 激活触发条件

以下任何一个条件满足时，**对应运维域从 `skeleton` 升级并补齐实质 Runbook 内容**：

1. **接入真实券商 API 并有真实资金**（D1/D4/D6 三域立刻必须）：真实资金风险不允许无 Runbook 操作，发布流程 / 灾备 / 事件响应必须正式化
2. **部署至非 localhost 环境**（D1/D2 触发）：非本地部署需要正式的 CI/CD 流程和监控 Dashboard，手动操作不再可接受
3. **数据量超过本地磁盘 80% 阈值**（D3/D7 触发）：备份策略和容量规划进入紧迫状态
4. **引入第二个协作成员**（D5/D6 触发）：多人协作必须有变更审批流程和正式事件响应，防止"互相改坏"
5. **系统 7×24 小时运行需求**（D2/D4/D6 全触发）：单次会话模式 → 守护进程模式，监控 / 灾备 / On-Call 全部必须
6. **LLM/数据订阅月费超过 ¥5,000**（D8 触发）：成本管理从"感性控制"进入"定量监控"，需要成本告警与预算机制
7. **监管合规审查**（D5/D6 全触发）：变更管理与事件响应记录是合规审查的必查项，Runbook 必须存在且可查阅
8. **因子回测投入生产使用（非研究）**（D2/D3 触发）：生产级因子数据的可靠性依赖监控与备份，研究阶段的手动管理不再适用

---

## Revision History / 修订记录

| Date / 日期 | Description / 说明 |
|------------|-------------------|
| 2026-04-19 | v0.1.0：初版骨架建立（S14-G4，批次 A）。§1 Purpose + 与 04-TA §6 边界说明；§2 八运维域总表；§3-§8 六域占位（3-5 行现状 + 占位标记）；§9 Runbook Catalog 11 条占位清单；§10 Activation Triggers 8 条触发条件。R39 登记理由。 |
| 2026-04-24 | v0.2.0：B-d-5 增量加固。§4 D2 Monitoring 实质化：experimental SLI/SLO 基线 9 项（含 SLO 阈值+告警动作）+ 指标采集拓扑（FLE 为中枢）；新增 §8A "6 大核心服务运维治理"（生命周期 DAG 序 + health check 合约 + 降级矩阵 + 日常巡检清单）；§9 Runbook Catalog 新增 5 条服务类 Runbook（RB-SVC-01~05）；§8 D6 补充与 06-security §11 对齐链接。文档保留 skeleton 身份，待 beta 升级为 active。 |
