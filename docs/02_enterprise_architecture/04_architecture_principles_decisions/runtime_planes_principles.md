---
module_id: VIEW-04PRINC-RUNTIME-PLANES
title: Architecture Principles — Runtime Planes (Orthogonal View) / 架构原则：运行平面正交视图
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
supersedes: VIEW-04BIS-RUNTIME-PLANES
related_rationale: []
related_open_questions:
- OQ-083
related_kb:
- KBG-0009
- KBG-0011
tags:
- runtime-planes-principles
- orthogonal-view
- hot-path
- warm-path
- cold-path
- sim-to-real
- latency-budget
- control-plane
- execution-plane
- citadel
- jane-street
- two-sigma
summary: 运行平面正交视图永恒原则文档。timeless 方法论——正交视图方法论（业务 What vs 运行 How/When 两把尺子）、Hot/Warm/Cold 三平面定义与 SLO、三平面归属判定流程、跨平面通信协议（6 方向 + 4 禁止规则）、shared/contracts/runtime_plane_tag.py 契约预留、Hot/Warm/Cold 差异化技术选型矩阵、Ultra-Hot 预留原则、T0-T4 激活触发器与只做/不做清单、与 09-GOV Runtime 层边界澄清（双标签语法）、Sim-to-Real Gap 保障三机制。派生数据（全域 × 三平面完整映射矩阵、按平面反查表、Tech Radar 当前状态）不在本文档，由 runtime_planes.yaml + technology_landscape.yaml 维护。
date: '2026-07-19'
ttl: permanent
---

# Architecture Principles — Runtime Planes (Orthogonal View)
# 架构原则：运行平面正交视图（Runtime Planes Principles）

---

## §1 定位 / Position

本文档是**运行平面正交视图的永恒指导原则**。

**ZephyrAlpha 2.0 第一个正交视图（Orthogonal View）**——与 TOGAF 10 视图体系平级但切片维度不同。本视图按**运行时延迟 / 技术栈 / 可中断性 / 部署拓扑**四维把 全域业务代码与前端、治理层重新切分为三个**运行平面（Runtime Planes）**：Hot Path / Warm Path / Cold Path。

**保留内容**：方法论、设计原则、不变约束——正交视图方法论、三平面定义与 SLO、归属判定流程、跨平面通信协议、契约预留、技术选型矩阵、激活触发器、与治理层边界澄清、Sim-to-Real 保障。

**不保留内容**（派生/动态数据，由各自自动化系统维护）：
- 全域 × 三平面完整映射矩阵 → `architecture_model/cross_cutting/runtime_planes.yaml`（派生统计见该 YAML 的 planes.hot/warm/cold.modules[]）
- 按平面维度反查表 → 同 YAML 的 `planes.hot.modules[]` / `planes.warm.modules[]` / `planes.cold.modules[]`
- Tech Radar 当前状态 → `architecture_model/technology/technology_landscape.yaml`

**与其他原则文档关系**：
- [application_principles.md](application_principles.md)：应用架构 全域业务 What（本视图定义 How/When）
- [technology_principles.md](technology_principles.md)：技术架构全局技术基线（本视图做平面维度下钻）
- [governance_principles.md](governance_principles.md)：治理三层 Policy/Factory/Runtime（与本视图三平面正交独立，详见 §9）
- 本文：运行平面正交视图（Hot/Warm/Cold 三平面 + 跨面协议 + Sim-to-Real 保障）

---

## §2 正交视图方法论 / Why Orthogonal

### 2.1 核心判断（永恒）

**业务分层（What）和运行平面（How/When）是两把正交的尺子**——用哪把尺子切代码取决于你想回答什么问题。强行把"延迟特征"塞进"业务本体"会造成双重漂移：

| 混为一层的后果（反例）| 正交切分的收益（本视图采纳）|
|---|---|
| 例如把 `hot_path/` 建成独立业务域 → D_EX_CORE `trade_execution/` 订单管理和 Hot Path 下单**同一业务概念被两域承担** → ACL 失效 / OCP 契约断裂 / 因子注册表跨域 | D_EX_CORE 仍完整承担"交易执行"业务本体，其中 `oms/` 子模块打 `@RuntimePlane.WARM_PATH` 标签、`sor/` 打 `@RuntimePlane.HOT_PATH` 标签 → 业务语义保持 + 运行特征独立标注 |
| 未来新增"Cold Path Backfill 专用域"时必须再加一域 → 域数无上限膨胀 | 新增平面仅在本视图技术选型 + 映射矩阵打补丁，全域业务不动 |
| AI 协作者找代码时必须同时记住"业务归属 + 延迟归属"两个维度在同一路径里 → 目录歧义 | AI 协作者按业务找代码（`src/zephyr/ex_core/sor/`）+ 按装饰器 / frontmatter 查运行平面，两把尺子各自清晰 |

### 2.2 业界证据（永恒对标）

| 机构 | 业务切分 | 运行平面切分 | 是否混合成一层 |
|---|---|---|---|
| **Citadel Securities** | 按 Asset Class + Strategy Family | Hot Path（FPGA / C++）/ Warm Path（Python research）分库 | ❌ 不混 |
| **Jane Street** | 按 Desk + Market | OCaml Hot Path / OCaml + Python Research 分 runtime | ❌ 不混 |
| **Two Sigma** | 按 Capability（Alpha / Risk / Execution）| C++ Hot / Python Warm / Spark Cold 分集群 | ❌ 不混 |
| **Jump Trading** | 按 Market + Instrument | Hardware-accelerated Hot / Software Warm 分机架 | ❌ 不混 |
| **Renaissance Medallion** | 按 Signal Family | Research（Warm）vs Production（Hot）分**组织** | ❌ 不混 |

**五家机构一致做法**：业务分层和运行平面是**两个独立的架构维度**，通过**标签 / 装饰器 / frontmatter / 独立 deployment manifest**做正交映射。**ZephyrAlpha 采纳同一做法**。

---

## §3 三平面定义（Hot / Warm / Cold）

### 3.1 三平面速查表（永恒框架）

| 平面 | 延迟上限 | 可中断性 | 调度模式 | 典型技术栈 | 典型业务 |
|---|---|---|---|---|---|
| **Hot Path** 🔥 | **< 10 ms**（目标 P99）| 🔴 **不可中断**（kernel-bypass + 预分配内存）| 事件驱动 / 固定轮询 | C++20 / Rust / DPDK / RDMA / FPGA / ZeroMQ / Aeron / LMAX Disruptor | 市场数据撮合 / 盘中 SOR 路由 / 高频做市 / 风控硬拦截 |
| **Warm Path** 🌡️ | **10 ms - 1 s**（目标 P95）| 🟡 **可抢占**（asyncio / 协程）| Async event loop / Task queue | Python >=3.11 / asyncio / FastAPI / Redis Streams / Kafka / NumPy / pandas | 因子计算 / 信号生成 / 组合再平衡 / OMS 状态机 / AI 推理 / API 响应 |
| **Cold Path** ❄️ | **> 1 s**（秒级到小时级）| 🟢 **完全可中断**（checkpointing）| 批调度 / 定时任务 / DAG | Spark / Dask / Ray / Airflow / Prefect / Parquet / DuckDB / Polars | 日终因子回测 / 月度归因 / 模型训练 / SBOM 扫描 / Scout Agent 夜间抓取 / 审计报表 |

### 3.2 三平面量化 SLO（永恒指标）

| 平面 | 延迟 SLO | 吞吐 SLO | 可用性 SLO | 故障影响域 |
|---|---|---|---|---|
| **Hot Path** | P50 < 1 ms / P99 < 10 ms | ≥ 100k msg/s | 99.99% | **资金直接损失**（订单错过 / 风控失守）|
| **Warm Path** | P50 < 50 ms / P95 < 1 s | ≥ 1k req/s | 99.9% | **决策质量下降**（信号延迟 / AI 响应慢）|
| **Cold Path** | Job 完成时间 < SLA 窗口 | 按数据量定 | 95%（允许重跑）| **分析报表延迟**（次日补救即可）|

### 3.3 跨平面规则（永恒铁律）

1. **Hot ⇄ Warm**：必须过 `shared/contracts/runtime_plane_tag.py` 定义的 IPC 协议（默认 Aeron / LMAX Disruptor），**禁止直接函数调用**
2. **Warm → Cold**：Parquet / Redis Streams 异步推送，**永远非阻塞**
3. **Cold → Warm**：模型 / 参数更新必须过**影子验证**（Champion-Challenger，D_SIMULATION 子模块负责）
4. **禁止 Cold → Hot 直接通信**：所有 Cold 输出必须先落 Warm 再经 Warm 验证后进 Hot

### 3.4 为什么是三平面（永恒结论）

| 切法 | 业界采纳度 | 优点 | 缺点 |
|---|---|---|---|
| 两平面（Hot + Cold）| 少数（早期 HFT）| 简单 | 忽略"异步决策 / AI 推理"中频场景 |
| **三平面（Hot / Warm / Cold）✅ 采纳** | **主流**（Citadel / Jane Street / Two Sigma / Jump / Renaissance）| 覆盖高 / 中 / 低三档延迟预算 | 对 < 100µs 超低延迟场景描述不够细 |
| 四平面（Ultra-Hot / Hot / Warm / Cold）| 少数（纯 FPGA 做市商）| 对超低延迟有独立预算 | 当前无 FPGA 预算 → 过度抽象 |

**结论**：三平面是业界共识最佳点（5/5 顶级机构采纳），ZephyrAlpha 采纳三平面 + 预留未来 Ultra-Hot 下钻能力（§7.4）。

---

## §4 三平面归属判定流程（永恒）

```
┌─────────────────────────────────────────────────────────────┐
│ 新增一个业务子模块时，按如下流程确定运行平面归属：                 │
│                                                              │
│ Q1: 这个模块的响应时间要求是否 < 10ms（P99）？                  │
│   ├── 是 → Q2                                                │
│   └── 否 → Q3                                                │
│                                                              │
│ Q2: 是否接入真实行情或真实委托？（T1 触发条件）                  │
│   ├── 是 → Hot Path ✅                                       │
│   └── 否 → Warm Path（暂不激活 Hot，T1 后再评估）              │
│                                                              │
│ Q3: 响应时间是否 > 1s 且可以批量化处理？                        │
│   ├── 是 → Cold Path ✅                                      │
│   └── 否 → Warm Path ✅（默认归属）                           │
└─────────────────────────────────────────────────────────────┘
```

> **注**：全域 × 三平面完整映射矩阵的真源是 `architecture_model/cross_cutting/runtime_planes.yaml`，不在本文档硬编码。AI / 开发者查询具体子模块归属请查该 YAML。

---

## §5 跨平面通信协议（永恒）

### 5.1 六组通信协议速查（永恒矩阵）

| 方向 | 协议 | 延迟预算 | 可靠性模型 | 典型实现 |
|---|---|---|---|---|
| **Hot ⇄ Hot**（同一 Hot 集群内部）| Shared Memory Ring Buffer / LMAX Disruptor / Aeron | < 10 µs | At-most-once（单副本）+ 硬件 HA | Aeron cluster / LMAX |
| **Hot ⇄ Warm** | Aeron IPC / ZeroMQ PUB-SUB / Shared Memory + polling | < 500 µs | At-least-once + idempotent consumer | Aeron + Python agrona binding |
| **Warm ⇄ Warm** | Redis Streams / Kafka / FastAPI HTTP + WebSocket | 10-100 ms | At-least-once + dedup | Redis Streams / Kafka + aiokafka |
| **Warm ⇄ Cold** | Parquet columnar files on object storage / Redis Streams with long TTL | 秒级（异步）| At-least-once + re-read | S3 / MinIO + pyarrow |
| **Cold → Warm**（模型 / 参数更新回灌）| Model Registry pull + Champion-Challenger shadow validation | 小时级 | Exactly-once（version-pinned）| MLflow / model_registry/ + D_SIMULATION shadow |
| **Cold ⇄ Cold** | Parquet + Airflow DAG | 分钟-小时 | Checkpointed retries | Airflow / Prefect |

### 5.2 禁止的跨平面通信（永恒铁律）

| 禁止 | 原因 |
|---|---|
| ❌ Cold → Hot 直接通信 | Cold 无延迟保证，直通会污染 Hot 路径 SLO；**必须经 Warm 中转 + shadow 验证** |
| ❌ Hot 同步调用 Warm Python | Python GIL + asyncio 延迟不可预测，Hot 等 Warm = Hot 降级成 Warm |
| ❌ Warm 同步阻塞等 Cold batch 完成 | Cold 秒级延迟，Warm 阻塞 = 上游 Warm 用户全部被拖垮 |
| ❌ 跨平面共享可变全局状态 | 三平面各自有独立进程 / 容器 / 物理机，共享状态必然竞态 |

---

## §6 契约预留：`shared/contracts/runtime_plane_tag.py`（永恒）

**职责**：定义运行平面枚举 + docstring 标注规范 + 跨平面契约基类的运行平面声明字段。

```python
# shared/contracts/runtime_plane_tag.py
from enum import Enum

class RuntimePlane(Enum):
    """
    运行平面标签 — 正交于 全域业务分层的执行维度标签。

    用法 1（模块级装饰器）：
        @runtime_plane(RuntimePlane.HOT_PATH)
        class SmartOrderRouter: ...

    用法 2（contract 基类字段）：
        class FactorBase:
            runtime_plane: ClassVar[RuntimePlane] = RuntimePlane.WARM_PATH

    用法 3（frontmatter 声明，对于纯文档 / YAML / Rego）：
        ---
        runtime_plane: warm_path
        ---
    """
    HOT_PATH = "hot_path"   # < 10ms P99, C++/Rust/kernel-bypass
    WARM_PATH = "warm_path" # 10ms-1s P95, Python asyncio
    COLD_PATH = "cold_path" # > 1s batch, Spark/Dask/Airflow

    # 预留未来子档
    ULTRA_HOT = "ultra_hot"  # < 100µs, FPGA (T-ULTRA 激活后启用)
```

**预留原则（永恒）**：
- enum 定义落盘但**不强制任何现有模块立即标注**（避免波动）
- Sprint 0+ 施工时强制**新增子模块必须标注**（OQ-083 关闭时已登记为"未来标注义务"）
- application_principles.md §4.1 `runtime_plane` 列作为**主真源**；装饰器 / frontmatter 作为**代码级辅助标注**

---

## §7 技术选型矩阵（三平面差异化）

### 7.1 选型矩阵（永恒框架）

| 维度 | Hot Path 🔥 | Warm Path 🌡️ | Cold Path ❄️ |
|---|---|---|---|
| **语言** | C++20 / Rust (stable) / C (kernel modules) | Python >=3.11 / Rust CPython extensions (热点函数) | Python / Scala (Spark) / SQL |
| **运行时** | 裸金属 / 物理机 / DPDK userspace | Linux VM / 容器（K8s Pod）| Spark cluster / Dask cluster / Airflow workers |
| **通信中间件** | Aeron / LMAX Disruptor / ZeroMQ (IPC) / RDMA | Redis Streams / Kafka / FastAPI HTTP / WebSocket | Parquet + S3 / MinIO / Airflow XCom |
| **存储** | Shared Memory Ring Buffer / mmap files | Redis / PostgreSQL / Parquet (hot/warm border) | Parquet (columnar) / DuckDB / S3 object storage |
| **并发模型** | Lock-free ring buffers / SPSC queue / LMAX-style | asyncio event loop / actor model (trio / anyio) | Spark DataFrame / Dask delayed / Ray |
| **GC** | 🚫 禁止（预分配 / arena allocator）| 🟡 Python 默认 GC（acceptable） | 🟢 无所谓 |
| **调度** | CPU 亲和 / NUMA 感知 / 大页内存 | Gunicorn workers + asyncio event loop | Airflow DAG / Prefect Flow / cron |
| **日志** | 零分配结构化日志（lock-free + post-process flush）| `structlog` + OpenTelemetry | 常规 logging，批量写 |
| **监控** | eBPF + 硬件计数器 + 零拷贝 trace | OpenTelemetry SDK + Prometheus exporter | Spark UI + Airflow UI + 基础 metric |
| **部署** | 独立物理机 + NIC bypass（目标 T1 后）| K8s 容器 + HPA | Spark cluster / Ray cluster + object storage |
| **测试** | 硬实时基准 (criterion.rs / google-benchmark) + 延迟直方图 | pytest-asyncio + hypothesis | Spark local mode + dbt test |

### 7.2 与 technology_principles.md 的关系（永恒）

technology_principles.md 定义**全局技术基线**（Python >=3.11，见 `pyproject.toml` / Redis / PostgreSQL / Parquet 等），本视图 §7 **在平面维度做下钻**——同一业务逻辑在不同平面可能选用不同技术栈（例：D_RISK 风控 Warm Path 用 Python async，Hot Path 用 Rust 重写并通过 Aeron 对接）。**本视图不替代 technology_principles，是补充正交切面**。

### 7.3 预留：Ultra-Hot 子档（未激活，永恒预留原则）

对于未来可能的超低延迟场景（< 100 µs，FPGA / 纯硬件做市），预留 `RuntimePlane.ULTRA_HOT` 枚举值但**当前不启用**。激活条件：

- **T-ULTRA**（未定义，估计 Sprint 20+）：团队规模 ≥ 5 人 + 自营资金 ≥ $10M + 明确低延迟套利策略 + FPGA 预算 ≥ $100k
- 未命中则 Ultra-Hot 永久不激活（99% 概率）

---

## §8 激活触发器（T0-T4 分档）

### 8.1 当前基线状态

**ZephyrAlpha 当前阶段**：
- 🟢 **Warm Path 100% 激活**（所有 全域业务代码默认跑在 Warm）
- 🔴 **Hot Path 未激活**（无真实行情 / 无真实委托）
- 🔴 **Cold Path 部分激活**（D_FACTOR 因子批量回算 / D_TRADING 归因 / D_ML_TRAIN 训练，当前小规模）

### 8.2 激活触发器全表（永恒框架）

| 触发器 | 档位 | 激活平面 | 激活的子模块 | 激活代价 |
|---|---|---|---|---|
| **T0 当前** | P0 | Warm only | 全域业务 default + 部分 Cold (D_FACTOR/D_TRADING/D_ML_TRAIN) | **已激活** |
| **T1 真实资金接入** | P1 | Hot 首次激活 | D_RISK `limits/stop_loss/monitor` + D_EX_CORE `sor/adapters_hot` + D_COMPLIANCE `ai_security/security_gateway` | 物理机 × 2 + Aeron cluster + C++/Rust 团队 |
| **T2 Cold Path 全量激活** | P2 | Cold 扩展 | D_FACTOR `pipeline` 全量 + D_PF_CORE `backtest` 长周期 + D_ML_TRAIN `training` GPU | Spark cluster 或 Dask cluster |
| **T3 Hot Path 扩展** | P2 | Hot 扩展 | + D_MKT_DATA `connectors_hot` + D_SIGLEGACY `signals_hot` + D_ML_TRAIN `serving_hot` | 增加物理机 + 低延迟行情订阅 |
| **T4 Ultra-Hot 激活** | P3 | Ultra-Hot | FPGA 做市策略专用子模块 | FPGA 硬件 + 专职工程师 |

### 8.3 激活 Hot Path 的"只做不做"清单（永恒铁律）

**激活 Hot Path 时必须做**：
1. ✅ 物理机就位 + NIC bypass 配置
2. ✅ Aeron / LMAX Disruptor 部署并压测通过（延迟直方图 P99 < 10ms）
3. ✅ C++/Rust 团队组建（或外部顾问）
4. ✅ Hot Path 子模块全部通过 criterion / google-benchmark 硬实时回归测试
5. ✅ 与 Warm Path 的契约冻结（`shared/contracts/` OCP）
6. ✅ 治理三层（Policy/Factory/Runtime）对 Hot 代码的额外 fitness functions 落地（特别是"不可有 GC / 不可有系统调用 / 不可有锁"）

**激活 Hot Path 时明确不做**：
1. ❌ 不把 Python 代码强行 JIT 化当 Hot Path——直接用 C++/Rust 重写
2. ❌ 不允许 Hot 直接访问 PostgreSQL / Redis Cluster（阻塞风险）
3. ❌ 不引入 Kubernetes 调度 Hot 进程（容器 overhead）
4. ❌ 不在 Hot Path 运行任何 AI 推理（除非 C++ 预编译模型 + < 1ms）

---

## §9 与 09-GOV Runtime 层的边界澄清（关键铁律）

### 9.1 同名不同义问题（永恒澄清）

**问题**：09-GOV 三层叫 Policy / Factory / **Runtime**，本视图三平面叫 Hot / Warm / **Cold**（没有叫 Runtime），但在交流中经常被误解为"Runtime 平面 = GOV Runtime 层"。**这是错误的**。

### 9.2 边界对照表（永恒）

| 维度 | 治理 Runtime 层（09-GOV）| 执行 Runtime Plane（本视图 Hot/Warm/Cold）|
|---|---|---|
| **切片维度** | 治理维度（谁管规则）| 执行维度（代码何时以什么延迟跑）|
| **切片方式** | 按"规则生命周期"切（定规则 Policy / 造工具 Factory / 执行拦截 Runtime）| 按"延迟预算 + 技术栈"切（Hot / Warm / Cold）|
| **所有平面都有 Runtime 吗？** | — | **是**。Hot Path 有 Runtime（C++ OPA 等价物）/ Warm Path 有 Runtime（Python 拦截）/ Cold Path 有 Runtime（Airflow hook 拦截）|
| **Policy 有平面归属吗？** | — | **无**（Policy 是规则文本，不执行）|
| **Factory 有平面归属吗？** | — | **有**——Factory 跑在 Cold Path（构建期 / 定时批调度）|
| **所有业务层都有治理三层吗？** | **是**（治理横切所有层）| 运行平面也是正交标签，但不是每层所有子模块都有 Hot 归属 |

### 9.3 复合命名规则（永恒——当二者联合引用时）

当需要联合描述"某代码的治理层 + 运行平面"时，使用**双标签语法**：

```
d_risk.limits.hard_cut.py  →  [GOV:Runtime] × [Plane:Hot]
d_factor.pipeline.batch.py   →  [GOV:Runtime] × [Plane:Cold]
scripts/governance/aisg/compile_desensitize_rules.py  →  [GOV:Factory] × [Plane:Cold]
docs/01_policies_and_standards/ai-security-gateway-policy.md  →  [GOV:Policy] × [Plane:—]
```

**格式**：`[GOV:<Policy|Factory|Runtime>] × [Plane:<Hot|Warm|Cold|—>]`

### 9.4 命名约束（永恒铁律）

| 命名 | 含义 | 避免 |
|---|---|---|
| ✅ **Runtime Plane** | 运行平面（执行维度）| 不要单独说 "Runtime" |
| ✅ **Governance Runtime Layer** | 治理 Runtime 层（治理维度）| 不要单独说 "Runtime" |
| ❌ **Runtime**（单独）| 歧义 | 在任何文档中禁止单独使用 "Runtime" 一词 |

---

## §10 Sim-to-Real Gap 保障（永恒三机制）

### 10.1 问题陈述

**Sim-to-Real Gap**：回测（Cold Path）表现好的策略，在实盘（Warm+Hot Path）表现差，核心差异源于：
- 撮合模型差异（回测假设 mid-price / 实盘有 queue position + adverse selection）
- 延迟差异（回测无延迟 / 实盘 P95 50ms 延迟改变 alpha 衰减）
- 市场冲击差异（回测线性 / 实盘非线性 depending on ADV%）
- 数据差异（回测 survivorship bias 风险 / 实盘 point-in-time）

### 10.2 三机制（永恒保障框架）

**机制一：跨平面契约统一**

`shared/contracts/` 承载以下**跨平面统一契约**（所有平面必须同契约）：

| 契约 | Cold Path 实现 | Warm Path 实现 | Hot Path 实现（T1 后）|
|---|---|---|---|
| `MarketImpactModel` | 真实成交历史回归系数 | 同 Cold 参数 | C++ 硬编码同参数 |
| `WeightPortfolio` | DataFrame-based | asyncio dataclass | C++ struct（同 schema）|
| `OrderBook` | Parquet snapshot | Redis in-memory | Shared Memory |
| `FillEvent` | Parquet record | Kafka message | Aeron message（同 schema）|
| `Timestamp` | pandas Timestamp (nanosecond) | datetime + tz | int64 nanosecond epoch |

**所有平面共享 `shared/contracts/` canonical schema**，不允许任何平面独立发明 schema。

**机制二：Champion-Challenger Shadow Validation**

D_SIMULATION `shadow/` 强制所有 Cold → Warm 模型更新先跑 **Shadow Trading**（Warm Path 并行运行新旧模型，无真实资金）≥ N 天后再晋级到 Hot Path。

**机制三：三平面共享 `risk/`**

风控 `shared/contracts/RiskConstraint` 在 Cold 回测 / Warm 实盘 / Hot 拦截三处必须**使用同一参数文件**（`config/risk_params.yaml`），避免三平面参数漂移。

---

## §11 视图边界 / Boundaries

### 11.1 本文档覆盖

- 正交视图方法论（业务 What vs 运行 How/When 两把尺子）（§2）
- Hot/Warm/Cold 三平面定义与 SLO（§3）
- 三平面归属判定流程（§4）
- 跨平面通信协议（6 方向 + 4 禁止规则）（§5）
- shared/contracts/runtime_plane_tag.py 契约预留（§6）
- Hot/Warm/Cold 差异化技术选型矩阵 + Ultra-Hot 预留（§7）
- T0-T4 激活触发器与只做/不做清单（§8）
- 与 09-GOV Runtime 层边界澄清（双标签语法）（§9）
- Sim-to-Real Gap 保障三机制（§10）

### 11.2 本文档不覆盖（由其他系统维护）

| 内容 | 真源 |
|------|------|
| 全域 × 三平面完整映射矩阵 | `architecture_model/cross_cutting/runtime_planes.yaml` |
| 按平面维度反查表 | 同 YAML 的 `planes.{hot,warm,cold}.modules[]` |
| Tech Radar 当前状态 | `architecture_model/technology/technology_landscape.yaml` |
| 三平面部署拓扑图 | `diagrams/runtime_planes_topology.mmd` |
| 全局技术基线（Python/Redis/PostgreSQL）| `technology_principles.md` |
| 全域业务分层（What）| `application_principles.md` |
| 治理三层（Policy/Factory/Runtime）| `governance_principles.md` |
| 前端平面归属（Hot-adjacent 概念）| `frontend_principles.md` |

### 11.3 与其他原则文档关系

- [application_principles.md](application_principles.md)：应用架构 全域业务 What（本视图定义 How/When）
- [technology_principles.md](technology_principles.md)：技术架构全局技术基线
- [governance_principles.md](governance_principles.md)：治理三层（与本视图三平面正交独立）
- [frontend_principles.md](frontend_principles.md)：前端架构原则（含 Hot-adjacent 概念）
- 本文：运行平面正交视图（Hot/Warm/Cold 三平面 + 跨面协议 + Sim-to-Real 保障）

---

> **文档维护原则**：本文档只包含永恒指导原则。任何随 全域演进、平面激活、技术栈升级变化的内容，均不应写入本文档——它们由 runtime_planes.yaml + technology_landscape.yaml 维护。
