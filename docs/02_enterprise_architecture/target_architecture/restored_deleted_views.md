---
module_id: VIEW-TA-RESTORED
title: 已删除图（被恢复）
doc_type: architecture_view
status: Active
version: 0.1.0
owner: ZephyrAlpha-Owner
valid_from: 2026-07-22
ttl: permanent
tags:
- architecture-view
- pending-review
- restored
---

# 已删除图（被恢复）

> ⚠️ **价值评估中** — 本文档由独立 `.mmd` 转换为内嵌 mermaid，供挨个评估其架构价值。

---

## frontend mfe topology

> Source: frontend_architecture.md §4.1

```mermaid
flowchart TB
    subgraph Host["platform/ (MF Host)"]
        Shell[App Shell<br/>Sidebar + Topbar + CommandPalette]
        Router[Global Router<br/>React Router v6]
        Auth[Auth Provider<br/>JWT + OIDC]
        Theme[Theme Provider<br/>Design Tokens]
        EventBus[Event Bus<br/>跨 App 事件总线]
    end

    subgraph Apps["apps/ (MF Remotes)"]
        A1[trading-terminal]
        A2[research-ide]
        A3[risk-dashboard]
        A4[monitoring-center]
        A5[...更多]
    end

    subgraph Packages["packages/ (Shared Chunks)"]
        P1[ui-kit]
        P2[chart-engine]
        P3[data-client]
        P4[auth]
        P5[shared-types]
    end

    Shell --> Router
    Router -.懒加载.-> A1
    Router -.懒加载.-> A2
    Router -.懒加载.-> A3
    Router -.懒加载.-> A4
    Router -.懒加载.-> A5

    A1 --> P1 & P2 & P3 & P4 & P5
    A2 --> P1 & P2 & P3 & P4 & P5
    A3 --> P1 & P2 & P3 & P4 & P5
    A4 --> P1 & P2 & P3 & P4 & P5

    Auth -.注入.-> A1 & A2 & A3 & A4 & A5
    Theme -.注入.-> A1 & A2 & A3 & A4 & A5
    EventBus -.发布订阅.-> A1 & A2 & A3 & A4 & A5
```

---

## frontend build pipeline

> Source: frontend_architecture.md §7.1

```mermaid
flowchart LR
    Dev[开发者] -->|pnpm changeset| Changeset
    Changeset --> CI{CI Pipeline}
    CI -->|pnpm install --frozen-lockfile| Install
    Install --> Lint[ESLint + Prettier + tsc]
    Lint --> Test[Vitest + Playwright]
    Test --> Build[Vite Build per App/Package]
    Build --> Sizecheck[Bundle Size Gate]
    Sizecheck --> Publish{Publish?}
    Publish -->|Package 变更| NPM[私有 NPM Registry<br/>Verdaccio or GitHub Packages]
    Publish -->|App 变更| CDN[Static CDN<br/>S3+CloudFront or Netlify]
    Publish -->|Platform 变更| CDN
```

---

## runtime planes topology

> Source: runtime_planes.md §2.3

```mermaid
%%{init: {'theme': 'default'}}%%
graph TB
    subgraph Hot["Hot Path 集群（专用物理机 / 裸金属 / 机架同城）"]
        HW["物理机 + 10GbE/25GbE + NIC bypass<br/>CPU 亲和性 + 大页内存<br/>无 GC / 无虚拟化 / 无容器"]
        HSW["C++ / Rust 进程 × N<br/>Ring Buffer / Aeron<br/>Disruptor / SPSC queue"]
        HW --> HSW
    end

    subgraph Warm["Warm Path 集群（容器 / K8s）"]
        WH["Linux VM / 容器 Pod<br/>Python >=3.11 + asyncio<br/>Gunicorn + Uvicorn workers"]
        WSW["FastAPI / Celery / Redis Streams<br/>策略信号 / OMS 状态机 / AI Agents"]
        WH --> WSW
    end

    subgraph Cold["Cold Path 集群（批调度 / 廉价存储）"]
        CH["Spark cluster / Dask cluster<br/>对象存储（S3 / MinIO）<br/>Parquet columnar"]
        CSW["Airflow DAG / Prefect Flow<br/>日终回测 / 归因 / 审计报表"]
        CH --> CSW
    end

    Hot -.->|"成交回报 Tick<br/>Aeron 低延迟订阅"| Warm
    Warm -.->|"订单指令 NewOrder<br/>同机架 IPC 或 Shared Memory"| Hot
    Warm -.->|"Parquet 落盘<br/>每日结束批量 flush"| Cold
    Cold -.->|"模型权重 / 因子参数<br/>次日启动时加载"| Warm
    Cold -.->|"训练好的模型<br/>灰度推送（Warm 先影子验证）"| Warm

    style Hot fill:#fef2f2,stroke:#dc2626,stroke-width:3px
    style Warm fill:#fef3c7,stroke:#d97706,stroke-width:2px
    style Cold fill:#dbeafe,stroke:#2563eb,stroke-width:2px
```

---

## governance activation gantt

> Source: governance_architecture.md §6.2

```mermaid
gantt
    title 治理架构激活时间表（方案 B Sprint 9/10/11/T4）
    dateFormat YYYY-MM-DD
    axisFormat %m/%d

    section Sprint 9（发布守卫）
    L3 三件套 ruff/mypy/bandit       :active, s9a, 2026-05-01, 2d
    L4 import-linter                  :s9b, after s9a, 1d
    L4 25 条 fitness functions        :s9c, after s9b, 2d
    A-14 kill switch + 量化红线        :s9d, after s9a, 2d

    section Sprint 10（施工 + AI Safety）
    L5 OCP 契约冻结                    :s10a, 2026-05-08, 2d
    AI Safety 三件套                    :s10b, after s10a, 3d
    A-10 audit_log 系统                :s10c, after s10a, 2d
    A-11 decision_provenance (F25)    :s10d, after s10c, 2d
    A-19 ADR 14 天 Gate (F23)         :s10e, after s10d, 1d

    section Sprint 11（业务运行时）
    L6 OPA Gatekeeper 部署             :s11a, 2026-05-18, 3d
    Rego 策略库起步                     :s11b, after s11a, 2d
    D2-B 反馈回写闭环                   :s11c, after s11b, 2d

    section T4 触发
    L7 SBOM 激活                       :milestone, crit, t4, 2026-07-01, 0d
```

---

## view dependencies

> Source: integration_architecture.md §8

```mermaid
graph TD
    BA["business_architecture.md\n业务能力 + 价值流"]
    IA["information_architecture.md\n信息资产组织"]
    AA["application_architecture.md\n应用模块 + 层次结构"]
    TA["technology_architecture.md\n技术栈 + 基础设施"]
    DA["data_architecture.md\n业务数据对象 + 血缘"]
    THIS["integration_architecture.md\n本视图：集成风格 + 拓扑 + 契约"]
    SEC["security_architecture.md\n安全域 + IAM + 密钥管理"]
    OPS["operations_architecture.md\n运维全景 + 流程 + 角色"]

    BA -->|业务流驱动集成意图| THIS
    AA -->|模块边界决定集成点| THIS
    DA -->|数据对象定义接口载荷| THIS
    TA -->|协议选型约束集成实现| THIS
    THIS -->|接口契约治理影响| SEC
    THIS -->|集成点运行状态纳入| OPS
```

---

## readme view dependency graph

> Source: README.md §4

```mermaid
graph TD
    OV["00-overview\n(Cross-layer 哲学)"]
    BA["01-business-architecture\n(BA 业务能力)"]
    IA["02-information-architecture\n(IA docs/抽屉治理)"]
    DA["05-data-architecture\n(DA 业务数据对象)"]
    AA["03-application-architecture\n(AA 应用分层)"]
    INTEG["07-integration-architecture\n(INTEG 集成拓扑·契约)"]
    TA["04-technology-architecture\n(TA 技术基础设施)"]
    SEC["06-security-architecture\n(SEC 安全域 skeleton)"]
    OPS["08-operations-architecture\n(OPS 运维全景 skeleton)"]
    GOV["09-governance-architecture\n(GOV 治理三层 Policy/Factory/Runtime)"]
    FE["10-frontend-architecture\n(FE 前端独立平台)"]
    RTP["04bis-runtime-planes\n🔷 正交视图 1\n(Hot/Warm/Cold 运行平面)"]
    CHM["04ter-capability-heatmap\n🔷 正交视图 2\n(能力成熟度热力图)"]

    OV --> BA
    BA --> IA
    BA --> DA
    IA --> AA
    DA -->|"数据实体 → AA 层处理"| AA
    AA -->|"模块边界 → 集成点"| INTEG
    DA -->|"数据载荷 → 接口契约"| INTEG
    AA --> TA
    DA -->|"存储选型"| TA
    INTEG -->|"外部接入点 → 安全域"| SEC
    INTEG -->|"集成健康状态 → 监控"| OPS
    TA --> OPS
    AA -->|"L08 api_gateway 是前后端唯一接触点"| FE
    INTEG -->|"API/WebSocket 契约"| FE
    FE -->|"前端也走 CDN/边缘部署"| OPS
    FE -->|"前端安全策略 (CSP/CORS/XSS)"| SEC
    GOV -->|"治理三层横切所有视图"| BA
    GOV -->|"治理三层横切所有视图"| IA
    GOV -->|"治理三层横切所有视图"| AA
    GOV -->|"治理三层横切所有视图"| FE
    GOV -->|"治理合规规则 → 安全执行"| SEC
    OPS -->|"运维审计 → 治理反馈回写"| GOV

    %% 正交视图横切关系（虚线表示正交标注叠加，不是依赖）
    RTP -.正交标注叠加.-> AA
    RTP -.正交标注叠加.-> FE
    RTP -.正交标注叠加.-> GOV
    RTP -.正交标注叠加.-> INTEG
    RTP -.正交标注叠加.-> TA
    CHM -.能力成熟度标注.-> BA
    CHM -.能力成熟度标注.-> AA
    CHM -.能力成熟度标注.-> DA
    CHM -.能力成熟度标注.-> GOV

    classDef orthogonal fill:#fef3c7,stroke:#f59e0b,stroke-width:3px,color:#78350f
    class RTP,CHM orthogonal
```
