---
module_id: VIEW-04PRINC-OPERATIONS
title: Architecture Principles — Operations / 架构原则：运维
doc_type: architecture_view
status: Active
version: 1.0.1
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
valid_from: 2026-07-19
superseded_by: null
supersedes: VIEW-08-OPERATIONS-ARCH
related_rationale: []
related_open_questions: []
tags:
- operations-principles
- togaf
- sre
- runbook
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
summary: 运维架构永恒原则文档。timeless 方法论——8 运维域定义（D1 部署/D2 监控/D3 备份/D4 灾备/D5 变更/D6 事件/D7 容量/D8 成本）、experimental SLI/SLO 基线（9 项指标阈值 + 告警动作）、指标采集拓扑（FLE 三段管道）、5 大核心服务运维治理（生命周期 DAG 序 + 健康检查合约 + 降级矩阵 + 日常巡检）、8 条 Activation Triggers（真实资金/非 localhost/磁盘 80%/第二人/7x24/月费 ¥5000/合规审查/生产因子）。派生数据（各域当前状态、Runbook Catalog 占位清单）不在本文档，由 ops 域实际激活后维护。
date: '2026-07-19'
ttl: permanent
---

# Architecture Principles — Operations
# 架构原则：运维（Operations Principles）

---

## §1 定位 / Position

本文档是**运维架构的永恒指导原则**。

**保留内容**：方法论、设计原则、不变约束——8 运维域定义、SLI/SLO 基线、指标采集拓扑、5 大核心服务运维治理、Activation Triggers。

**不保留内容**（派生/动态数据，由 ops 域激活后维护）：
- 各域"当前状态"描述 → 实际部署演进后由 ops 域文档维护
- Runbook Catalog 占位清单 → `docs/_working/runbooks/`（待创建）建立后维护
- 容量规划数字 / DR 演练计划 → 实际激活后维护

**与其他原则文档关系**：
- [technology_principles.md](technology_principles.md)：技术架构全局基线（04-TA §6 部署图 How vs 本视图 What，互补不替代）
- [governance_principles.md](governance_principles.md)：治理三层（变更管理 D5 与治理 Runtime 层部分重叠）
- [runtime_planes_principles.md](runtime_planes_principles.md)：运行平面（监控指标按平面差异化采样）
- [application_principles.md](application_principles.md)：5 大核心服务（Vibe Coding 2.0）业务架构
- 本文：运维架构原则（8 域框架 + SLI/SLO + 5 大服务运维治理）

---

## §2 8 运维域定义 / Operations Domains

**永恒框架**：本视图覆盖 8 个运维域。

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

### 2.1 与 technology_principles.md §6 的边界（永恒澄清）

| 视图 | 回答 | 类比 |
|------|------|------|
| `technology_principles.md` 部署相关章节 | **物理节点 How**：用了什么容器、什么机器、什么网络拓扑，如何部署 | 建筑的"施工图" |
| **本文档（operations_principles.md）** | **生命周期 What**：什么时候做什么运维操作、谁负责、流程是什么 | 建筑的"物业管理手册" |

两者**互补不替代**：technology_principles 告诉你"部署长什么样"，本文档告诉你"部署之后如何维护"。

---

## §3 D2 — Monitoring & Observability / 监控与可观测性域

### 3.1 架构定位（永恒）

- `D_INFRA_OPS` 域是传统可观测性代码归属（OpenTelemetry 导出）
- **Feedback Loop Engine (FLE)** 是 5 大核心服务的"自动化运维大脑"，所有服务指标→FLE→异常检测→动作分派
- 两者关系：OpenTelemetry 面向"人工看板 + 外部工具"；FLE 面向"系统内部自调节"

### 3.2 experimental SLI/SLO 基线（永恒阈值表，P0 必采）

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

**SLO 来源**（永恒约束）：每项 SLO 都有 `technology_landscape.yaml upgrade_watchboard` 中对应的升级阈值。

### 3.3 指标采集拓扑（永恒数据流）

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

**导出通道**（永恒）：

- `D_INFRA_OPS` 定期从 FLE 导出到本地文件（JSON Lines）
- beta 启用 OpenTelemetry Collector → Prometheus/Grafana 标准栈

---

## §4 5 Core Services — Runtime Operations / 5 大核心服务运维治理

> 本节专项描述 5 大核心服务（LSG/CE/Orc/VMS/FLE）的 experimental 运维流程，是 §2 的 8 大运维域在"AI 基础设施"上的具化。

### 4.1 服务生命周期（永恒启动/停止 DAG 序）

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

### 4.2 健康检查合约（永恒接口规范）

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

**巡检频率**（永恒）：experimental 由 FLE 每 60 秒轮询一次，异常立即进入 detect_anomaly 流程。

### 4.3 降级矩阵（永恒策略表）

| 服务 | 降级条件 | 降级行为 | 恢复条件 |
|------|---------|---------|---------|
| LSG | **不降级**（fail-closed）| N/A（异常即拒绝调用）| N/A |
| CE | LLM 压缩失败 | 规则基截断 + degraded=True | Qwen2.5-3B 服务恢复 |
| CE | VMS 检索失败 | 降级到 grep/rg 文件检索 | VMS 恢复 |
| VMS | ChromaDB 损坏/首次启动 | `search()` 返回空 + degraded=True | bulk_bootstrap 完成 |
| Orc | SQLite 锁争用 | 任务延迟执行 + 告警 | 锁释放 |
| Orc | Agent 沙箱逃逸 | 立即 kill + IR-SEC-002 | 人工审查 |
| FLE | SQLite 容量满 | 归档旧数据 + 暂停异常检测 | 容量恢复 |

### 4.4 配置热更新原则（永恒约束）

**experimental 约束**：配置文件修改需要重启服务（无热更新）。

**beta 目标**：LSG 策略表 + Orc 白名单 + FLE 阈值支持热更新，减少 AI 协作中断。

### 4.5 日常巡检清单（experimental P0，永恒建议清单）

建议每日一次：

- [ ] FLE anomaly 累计 < 5 条（否则启动调查）
- [ ] LSG fail-closed 触发 < 10 次（否则检查策略表）
- [ ] Orc SQLite audit.db 大小 < 100MB（超阈值归档）
- [ ] VMS ChromaDB 持久化大小 < 500MB（TECH-04 upgrade_watchboard）
- [ ] `.runtime/logs/session/` 30 天内无新 incident 文件

---

## §5 Activation Triggers / 激活触发条件（永恒框架）

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

## §6 视图边界 / Boundaries

### 6.1 本文档覆盖

- 8 运维域定义（D1-D8）（§2）
- 与 technology_principles 部署章节的边界澄清（§2.1）
- experimental SLI/SLO 基线（9 项指标阈值 + 告警动作）+ 指标采集拓扑（§3）
- 5 大核心服务运维治理（生命周期 DAG 序 + 健康检查合约 + 降级矩阵 + 巡检清单）（§4）
- 8 条 Activation Triggers（§5）

### 6.2 本文档不覆盖（由其他系统维护）

| 内容 | 真源 |
|------|------|
| 各域"当前状态"描述 | ops 域实际部署演进后由 ops 域文档维护 |
| Runbook Catalog 占位清单 | `docs/_working/runbooks/`（待创建）建立后维护 |
| 容量规划数字 / DR 演练计划 | 实际激活后维护 |
| 物理节点 How（部署图）| `technology_principles.md` 部署相关章节 |
| 变更管理审批流程细节 | `governance_principles.md`（治理 Runtime 层）|
| 监控指标按平面差异化采样 | `runtime_planes_principles.md` |
| 5 大核心服务业务架构 | `application_principles.md` |
| 安全事件响应流程 | `security_principles.md` |

### 6.3 与其他原则文档关系

- [technology_principles.md](technology_principles.md)：技术架构全局基线（部署 How vs 本视图 What）
- [governance_principles.md](governance_principles.md)：治理三层（D5 变更管理与治理 Runtime 层部分重叠）
- [runtime_planes_principles.md](runtime_planes_principles.md)：运行平面（监控指标按平面差异化）
- [application_principles.md](application_principles.md)：5 大核心服务业务架构
- [security_principles.md](security_principles.md)：安全事件响应流程
- 本文：运维架构原则（8 域 + SLI/SLO + 5 大服务运维治理）

---

> **文档维护原则**：本文档只包含永恒指导原则。任何随部署环境演进、Runbook 实际建立、容量与成本变化的内容，均不应写入本文档——它们由 ops 域实际激活后的实现文档维护。
