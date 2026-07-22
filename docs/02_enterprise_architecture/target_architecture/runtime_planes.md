---
module_id: VIEW-04BIS-RUNTIME-PLANES
title: Target Architecture — Runtime Planes (Orthogonal View) / 目标架构：运行平面正交视图
doc_type: architecture_view
status: Active
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
- R69
related_open_questions:
- OQ-083
related_kb:
- KBG-0009
- KBG-0011
tags:
- target-architecture
- runtime-planes
- hot-path
- warm-path
- cold-path
- orthogonal-view
- sim-to-real
- latency-budget
- control-plane
- execution-plane
- citadel
- jane-street
- two-sigma
- i1-j1
summary: ZephyrAlpha 2.0 **第一个正交视图（Orthogonal View）**，与 TOGAF 10 视图体系平级但切片维度不同。本视图按**运行时延迟
  / 技术栈 / 可中断性 / 部署拓扑**四维把 14 层业务代码（L00-L13 + shared）与前端、治理层重新切分为三个**运行平面（Runtime
  Planes）**：Hot Path（<10ms，kernel-bypass + C++/Rust）/ Warm Path（10ms-1s，Python async）/
  Cold Path（>1s batch，Spark/Dask）。对标 Citadel Securities / Jane Street / Two Sigma
  / Jump Trading / Renaissance 五家顶级机构在**控制面 vs 执行面物理切分**上的一致做法——业务分层（What 做什么）与运行平面（How
  何时以什么延迟执行）是两把正交尺子，**不能混为一层**（否则 14 层业务本体被延迟特征污染，ACL/OCP/因子注册表契约全部断裂）。本视图与 09-GOV
  Policy/Factory/Runtime 三层**边界互补不重叠**：09-GOV 治"谁管什么规矩"（治理维），本视图治"什么代码何时跑在什么硬件上"（执行维）。当前
  ZephyrAlpha 处于 Warm Path only 阶段（Hot Path / Cold Path 均为未激活），本视图定义终局拓扑 + 三档激活触发器
  + 跨面通信协议 + `shared/contracts/runtime_plane_tag.py` 契约预留，为 Sim-to-Real Gap 问题和未来低延迟交易铺路，当前零代码影响。
date: '2026-04-22'
ttl: permanent
---

## 1. Purpose & 为什么需要正交视图

### 1.1 本视图要回答的问题

| 问题 | 答案所在 |
|---|---|
| 控制面（研究 / 决策 / 报表）和执行面（下单 / 成交 / 撮合反馈）在物理上如何分离？| §2 三平面定义 |
| 14 层业务代码每一层 / 每个子模块属哪个运行平面？| §3 14 层 × 三平面映射矩阵 |
| Hot Path / Warm Path / Cold Path 何时激活？激活条件是什么？| §6 激活触发器（P0-P3）|
| 三个平面之间如何通信？契约是什么？| §4 跨面协议（Ring Buffer / Redis Streams / Parquet）|
| Hot Path 用什么技术栈？Warm Path 用什么？Cold Path 用什么？| §5 技术选型矩阵 |
| 与 09-GOV Policy/Factory/Runtime 三层是什么关系？| §7 与 09-GOV 边界澄清 |
| Sim-to-Real Gap 如何通过运行平面统一契约来消解？| §8 Sim-to-Real 保障 |

### 1.2 为什么要做成"正交视图"而不是 14 层业务之外再加一层

**核心判断**：业务分层（What）和运行平面（How/When）是**两把正交的尺子**，用哪把尺子切代码取决于你想回答什么问题。强行把"延迟特征"塞进"业务本体"会造成双重漂移：

| 混为一层的后果（反例）| 正交切分的收益（本视图采纳）|
|---|---|
| 例如把 `l14_hot_path/` 建成独立业务层 → L06 `trade_execution/` 订单管理和 L14 Hot Path 下单**同一业务概念被两层承担** → ACL 失效 / OCP 契约断裂 / 因子注册表跨层 | L06 仍完整承担"交易执行"业务本体，其中 `oms/` 子模块被打 `@RuntimePlane.WARM_PATH` 标签、`sor/` 打 `@RuntimePlane.HOT_PATH` 标签 → 业务语义保持 + 运行特征独立标注 |
| 未来新增"Cold Path Backfill 专用层"时必须再加一层 → 层数无上限膨胀 | 新增平面仅在本视图 §5 技术选型 + §3 映射矩阵打补丁，14 层业务不动 |
| AI 协作者找代码时必须同时记住"业务归属 + 延迟归属"两个维度在同一路径里 → 目录歧义 | AI 协作者按业务找代码（`src/zephyr/ex_core/sor/`）+ 按装饰器 / frontmatter 查运行平面，两把尺子各自清晰 |

**业界证据**：

| 机构 | 业务切分 | 运行平面切分 | 是否混合成一层 |
|---|---|---|---|
| **Citadel Securities** | 按 Asset Class + Strategy Family | Hot Path（FPGA / C++）/ Warm Path（Python research）分库 | ❌ 不混 |
| **Jane Street** | 按 Desk + Market | OCaml Hot Path / OCaml + Python Research 分 runtime | ❌ 不混 |
| **Two Sigma** | 按 Capability（Alpha / Risk / Execution）| C++ Hot / Python Warm / Spark Cold 分集群 | ❌ 不混 |
| **Jump Trading** | 按 Market + Instrument | Hardware-accelerated Hot / Software Warm 分机架 | ❌ 不混 |
| **Renaissance Medallion** | 按 Signal Family | Research（Warm）vs Production（Hot）分**组织** | ❌ 不混 |

**五家机构的一致做法**：业务分层和运行平面是**两个独立的架构维度**，通过**标签 / 装饰器 / frontmatter / 独立 deployment manifest** 做正交映射。**ZephyrAlpha 本视图采纳同一做法**。

### 1.3 与其他视图的边界

| 其他视图 | 本视图与其关系 |
|---|---|
| `application_architecture.md` | 03-AA 定义"14 层业务 What"；本视图定义"每个子模块的运行平面 How/When"；本视图 v1.0.0 在 03-AA §4.1 子模块表中**新增 `runtime_plane` 列**（J1 批次 C 任务同步） |
| `technology_architecture.md` | 04-TA 定义"全局技术选型"；本视图定义"按平面差异化技术选型"；§5 技术矩阵是 04-TA §3 的下钻 |
| `governance_architecture.md` | 09-GOV 治理三层 Policy/Factory/Runtime 是**治理维度**（谁管什么规矩）；本视图三平面是**执行维度**（代码何时以什么延迟跑在什么硬件）。二者**名字都叫 "Runtime" 但意义完全不同**——§7 专门澄清。|
| `frontend_architecture.md` | 10-FE 定义前端独立平台；本视图 §3.4 给前端子层打运行平面标签（React SPA Warm / WebSocket stream Hot-adjacent / SSR 报表 Cold）|
| `architecture_model/technology/technology_landscape.yaml` | Tech Radar 风格的技术清单；本视图选型依赖其 Adopt/Trial/Hold 状态（§5 引用）|

### 1.4 决策溯源

- **KBG-0009 v1.1.0** src/ 14 层业务分层 accepted（R31/R32/OQ-073）——业务本体锚点
- **KBG-0011** Runtime Planes Orthogonal View v1.0.0 accepted（本视图同源）
- **R69** 正交视图 vs 分层方法论决策（2026-04-19 J1 批次，见 `architecture-rationale-log.md`）
- **OQ-083** closed（2026-04-19 J1 批次一次性拍板——采纳方案 B 正交视图）
- **外部评审驱动**：`tests/外部评审.md` 四家 AI 外部评审共识指出"缺少控制面 / 执行面物理切分定义"是 top-tier 量化机构架构的 P0 短板

---

## 2. 三平面定义（Hot / Warm / Cold）

### 2.1 三平面速查表

| 平面 | 延迟上限 | 可中断性 | 调度模式 | 典型技术栈 | 典型业务 |
|---|---|---|---|---|---|
| **Hot Path** 🔥 | **< 10 ms**（目标 P99）| 🔴 **不可中断**（kernel-bypass + 预分配内存）| 事件驱动 / 固定轮询 | C++20 / Rust / DPDK / RDMA / FPGA / ZeroMQ / Aeron / LMAX Disruptor | 市场数据撮合 / 盘中 SOR 路由 / 高频做市 / 风控硬拦截 |
| **Warm Path** 🌡️ | **10 ms - 1 s**（目标 P95）| 🟡 **可抢占**（asyncio / 协程）| Async event loop / Task queue | Python >=3.11（基线见 `pyproject.toml`）/ asyncio / FastAPI / Redis Streams / Kafka / NumPy / pandas | 因子计算 / 信号生成 / 组合再平衡 / OMS 状态机 / AI 推理 / API 响应 |
| **Cold Path** ❄️ | **> 1 s**（秒级到小时级）| 🟢 **完全可中断**（checkpointing）| 批调度 / 定时任务 / DAG | Spark / Dask / Ray / Airflow / Prefect / Parquet / DuckDB / Polars | 日终因子回测 / 月度归因 / 模型训练 / SBOM 扫描 / Scout Agent 夜间抓取 / 审计报表 |

### 2.2 三平面的量化指标（SLO）

| 平面 | 延迟 SLO | 吞吐 SLO | 可用性 SLO | 故障影响域 |
|---|---|---|---|---|
| **Hot Path** | P50 < 1 ms / P99 < 10 ms | ≥ 100k msg/s | 99.99% | **资金直接损失**（订单错过 / 风控失守）|
| **Warm Path** | P50 < 50 ms / P95 < 1 s | ≥ 1k req/s | 99.9% | **决策质量下降**（信号延迟 / AI 响应慢）|
| **Cold Path** | Job 完成时间 < SLA 窗口 | 按数据量定 | 95%（允许重跑）| **分析报表延迟**（次日补救即可）|

### 2.3 三平面的部署拓扑

> **📊 三平面部署拓扑图**：见 [`diagrams/runtime_planes_topology.mmd`](diagrams/runtime_planes_topology.mmd)

**关键跨平面规则**：
1. **Hot ⇄ Warm**：必须过 `shared/contracts/runtime_plane_tag.py` 定义的 IPC 协议（默认 Aeron / LMAX Disruptor），**禁止直接函数调用**
2. **Warm → Cold**：Parquet / Redis Streams 异步推送，**永远非阻塞**
3. **Cold → Warm**：模型 / 参数更新必须过**影子验证**（Champion-Challenger，L13 子模块负责）
4. **禁止 Cold → Hot 直接通信**：所有 Cold 输出必须先落 Warm 再经 Warm 验证后进 Hot

### 2.4 为什么是三平面而不是两平面或四平面

| 切法 | 业界采纳度 | 优点 | 缺点 |
|---|---|---|---|
| 两平面（Hot + Cold）| 少数（早期 HFT）| 简单 | 忽略"异步决策 / AI 推理"这类中频场景，被迫挤进 Hot 或 Cold 都不合适 |
| **三平面（Hot / Warm / Cold）✅ 采纳** | **主流**（Citadel / Jane Street / Two Sigma / Jump / Renaissance）| 覆盖高 / 中 / 低三档延迟预算，匹配量化系统三类实时性需求 | 对 < 100µs 超低延迟场景描述不够细（可未来增补 "Ultra-Hot" 子档）|
| 四平面（Ultra-Hot / Hot / Warm / Cold）| 少数（纯 FPGA 做市商如 Jump HF desk）| 对超低延迟有独立预算 | 当前 ZephyrAlpha 无 FPGA 预算 → 过度抽象 |

**结论**：**三平面是业界共识最佳点**（5/5 家顶级机构采纳），ZephyrAlpha 采纳三平面 + 预留未来 "Ultra-Hot" 下钻能力（§5.4）。

---

## 3. 14 层业务 × 三平面完整映射矩阵

### 3.1 总览表（按业务层维度）

> **SSoT 声明**：运行平面归属的 **Single Source of Truth** 是 [`architecture_model/cross-cutting/runtime_planes.yaml`](architecture_model/cross-cutting/runtime_planes.yaml)（Hot 7 模块 / Warm 39 模块 / Cold 24 模块 + 6 条跨面通信规则）。下表从该 YAML **只读派生**，如有冲突以 YAML 为准。

| 业务层 | 子模块 | Hot 🔥 | Warm 🌡️ | Cold ❄️ | 备注 |
|--------|--------|:------:|:-------:|:------:|------|
| **shared** | `contracts/runtime_plane_tag.py` | ✅ | — | — | 枚举定义，所有平面共用契约 |
| **shared** | `contracts/*.py`（其余） | — | ✅ | — | 跨层公共契约 |
| **L00 Data Source** | `connectors/*.py`（默认） | — | ✅ | — | 当前默认数据接入 |
| | `connectors/*_hot.py` | ⏳T3 | — | — | T3 激活后低延迟行情 |
| | `normalizers/` | — | ✅ | — | 数据标准化 |
| | `cache/` | — | ✅ | — | 数据缓存 |
| | `storage/` | — | — | ✅ | 数据持久化落盘 |
| | `quality/` | — | — | ✅ | 批量数据质量校验 |
| **L01 Infrastructure** | `config/` | — | ✅ | — | 配置管理（跨平面共享，自身属 Warm） |
| | `logging/` | — | ✅ | — | 日志基础设施 |
| | `exceptions/` | — | ✅ | — | 异常框架 |
| | `runtime/` | — | ✅ | — | 基础运行时 |
| **L02 Alpha Factor** | `factors/`（在线增量） | — | ✅ | — | 因子在线增量计算 |
| | `factors/`（批量回算） | — | — | ✅ | 因子批量回算 |
| | `evaluation/`（实时 IC） | — | ✅ | — | 实时信息系数 |
| | `pipeline/`（全量计算） | — | — | ✅ | 因子批量全量计算 |
| | `registry/` | — | — | ✅ | 因子注册表持久化 |
| **L03 Signal Generation** | `signals/`（默认） | — | ✅ | — | 默认信号输出 |
| | `signals/*_hot.py` | ⏳T3 | — | — | T3 激活后低延迟信号 |
| | `sentiment/` | — | ✅ | — | 情绪分析（实时） |
| | `sentiment/`（历史批量） | — | — | ✅ | 情绪历史批量分析 |
| | `predictions/` | — | ✅ | — | AI 推理信号 |
| **L04 Risk Management** | `limits/` | ✅T1 | — | — | pre-trade hard check（T1 激活） |
| | `stop_loss/` | ✅T1 | — | — | 毫秒级 kill switch（T1 激活） |
| | `monitor/` | ✅T1 | ✅ | — | Hot: real-time hard monitor / Warm: 默认监控 |
| | `metrics/` | — | ✅ | ✅ | Warm: VaR/CVaR 计算 / Cold: 日终+月度回测 |
| **L05 Portfolio Construction** | `optimization/` | — | ✅ | — | 组合优化 |
| | `rebalancing/` | — | ✅ | — | 再平衡 |
| | `meta_router/` | — | ✅ | — | 策略元路由 |
| | `strategic/`（决策） | — | ✅ | — | 战略决策 |
| | `strategic/`（历史回溯） | — | — | ✅ | 战略历史分析 |
| | `backtest/` | — | — | ✅ | 策略回测 |
| | `performance/` | — | — | ✅ | 绩效分析 |
| **L06 Trade Execution** | `sor/` | ✅T1 | — | — | Smart Order Routing（T1 激活） |
| | `adapters/*_hot.py` | ✅T1 | — | — | 券商直连（T1 激活） |
| | `oms/` | — | ✅ | — | 订单状态机 |
| | `pre_trade/` | — | ✅ | — | 交易前检查 |
| | `adapters/`（默认） | — | ✅ | — | 默认券商适配器 |
| **L07 Post-Trade Analytics** | `review/`（实时 TCA） | — | ✅ | — | 实时交易成本分析 |
| | `attribution/` | — | — | ✅ | 日终绩效归因 |
| | `reports/` | — | — | ✅ | 月度报表生成 |
| **L08 Human-AI Interface** | `cli/` | — | ✅ | — | 命令行接口 |
| | `orchestration/` | — | ✅ | — | AI 编排 |
| | `notifications/` | — | ✅ | — | 消息通知 |
| **L09 Research & Innovation** | `notebooks/` | — | ✅ | — | 研究笔记本（交互式） |
| | `prototypes/` | — | ✅ | — | 原型实验 |
| | `experiments/` | — | — | ✅ | 批量实验沙盒 |
| **L10 Governance & Compliance** | `ai_security/security_gateway` | ✅ | — | — | AISG security_gateway（Hot-adjacent，< 50ms） |
| | `ai_security/`（其余 5 模块） | — | ✅ | — | AISG 其余模块 |
| | `validators/` | — | ✅ | — | 合规校验器 |
| | `rules/` | — | ✅ | — | 规则引擎 |
| | `policy_engine/` | — | ✅ | — | 策略执行引擎 |
| | `audit_trail/` | — | — | ✅ | 审计追踪归档 |
| | `policies/`（SBOM 扫描） | — | — | ✅ | 供应链 SBOM 扫描 |
| **L11 ML Platform** | `serving/`（默认 Python） | — | ✅ | — | 模型推理默认（Warm） |
| | `serving/*_hot.py` | ⏳T3 | — | — | T3 激活后低延迟推理 |
| | `model_registry/`（读） | — | ✅ | — | 模型注册表只读 |
| | `model_registry/`（写） | — | — | ✅ | 模型注册表写入 |
| | `training/` | — | — | ✅ | 模型训练 |
| | `evaluation/` | — | — | ✅ | 模型评估 |
| | `scout/` | — | — | ✅ | Scout Agent 批量任务 |
| **L12 System Telemetry** | `metrics/`（标准采集） | — | ✅ | — | 指标采集 |
| | `metrics/*_hot.py` | ⏳T3 | — | — | T3 激活后低延迟指标 |
| | `logs/` | — | ✅ | — | 日志管道 |
| | `traces/` | — | ✅ | — | 分布式追踪 |
| | `traces/`（长期归档） | — | — | ✅ | 追踪数据归档 |
| | `ai_behavior/` | — | ✅ | — | AI 行为监控 |
| | `ai_behavior/`（回溯分析） | — | — | ✅ | AI 行为历史回溯 |
| **L13 Experiment Pipeline** | `shadow/` | — | ✅ | — | 影子交易运行时 |
| | `champion_challenger/` | — | ✅ | — | 冠军挑战者评分 |
| | `promotion_gate/` | — | ✅ | — | 晋级门禁 |
| | `ab_testing/` | — | — | ✅ | A/B 测试结果聚合 |
| **Governance（09-GOV）** | `scripts/governance/`（Factory） | — | — | ✅ | 治理 Factory 层（构建期批调度） |
| | Scout Agent（D-02 cron） | — | — | ✅ | D-02 Scout Agent 每日抓取 |
| **Frontend（10-FE）** | `apps/reports-center/`（SSR） | — | — | ✅ | 前端 SSR 报表 |
| | `tools/codegen/` | — | — | ✅ | 构建期代码生成 |
| | 其余前端子层 | — | ✅ | — | 默认 Warm（React SPA + WebSocket） |

> **图例**：✅ = 当前归属 | ✅T1 = T1 触发器激活后归属 | ⏳T3 = T3 触发器激活后新增 | — = 不归属此平面

**统计**：Hot Path 7 模块（+ T3 扩展 4 模块）| Warm Path 39 模块 | Cold Path 24 模块 = **共 70 个子模块归属条目**，覆盖全部 14 层 + shared + Governance + Frontend。

### 3.2 总览表（按运行平面维度 — 反查视图）

> 按平面维度的反查视图同样收录于 [`runtime_planes.yaml`](architecture_model/cross-cutting/runtime_planes.yaml)（`planes.hot.modules[]` / `planes.warm.modules[]` / `planes.cold.modules[]`）。以下为可读摘要：

**🔥 Hot Path（7 模块，当前未激活，T1 首次激活）**

| 层 | 子模块 | 激活时机 | 说明 |
|----|--------|---------|------|
| shared | `contracts/runtime_plane_tag.py` | 当前 | 枚举定义，所有平面共用 |
| L04 | `limits/` | T1 | pre-trade hard check |
| L04 | `stop_loss/` | T1 | 毫秒级 kill switch |
| L04 | `monitor/` | T1 | real-time hard monitor |
| L06 | `sor/` | T1 | Smart Order Routing |
| L06 | `adapters/*_hot.py` | T1 | 券商直连 |
| L10 | `ai_security/security_gateway` | T1 | AISG 安全网关（Hot-adjacent，< 50ms） |

T3 扩展（Hot Path 扩展触发后新增）：`l00-connectors-hot` / `l03-signals-hot` / `l11-serving-hot` / `l12-metrics-hot`

**🌡️ Warm Path（39 模块，当前全量激活）**

覆盖层：L00（3）/ L01（4）/ L02（2）/ L03（3）/ L04（2）/ L05（4）/ L06（3）/ L07（1）/ L08（3）/ L09（2）/ L10（4）/ L11（2）/ L12（4）/ L13（3）/ shared（1）+ Frontend 默认

**❄️ Cold Path（24 模块，当前部分激活）**

覆盖层：L00（2）/ L02（3）/ L03（1）/ L04（1）/ L05（3）/ L07（2）/ L09（1）/ L10（2）/ L11（4）/ L12（2）/ L13（1）/ Governance（2）/ Frontend（2）

### 3.3 三平面归属判定流程（AI / 开发者自助）

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

### 3.4 前端（10-FE）三平面归属（同步批次）

> 前端子层的平面归属数据见 [`runtime_planes.yaml`](architecture_model/cross-cutting/runtime_planes.yaml) 中 `planes.cold.modules[]` 的 `fe-ssr-reports` / `fe-codegen` 条目（其余前端子层默认 Warm）。

详见 J1 批次 E 任务同步更新 `frontend_architecture.md`。

### 3.5 治理层（09-GOV）三平面归属（同步批次）

**澄清**：09-GOV 的 Policy/Factory/Runtime 是治理维度三层，本视图的 Hot/Warm/Cold 是执行维度三平面，二者正交。

> 09-GOV 治理系统的平面归属数据见 [`runtime_planes.yaml`](architecture_model/cross-cutting/runtime_planes.yaml) 中 `planes.cold.modules[]` 的 `gov-factory` / `gov-scout-d02` 条目。**要点**：Policy 层无运行平面（纯文档）；Factory 层归 Cold（构建期批调度）；Runtime 层 A/B/C 归 Warm 主 + Hot 部分（kill switch / pre-trade hard check）；D-01 AISG `security_gateway` 子模块 Hot-adjacent（< 50ms）；D-02 Scout 归 Cold。

详见 J1 批次 D 任务同步更新 `governance_architecture.md` v1.1.0 → v1.2.0。

---

## 4. 跨平面通信协议

### 4.1 三组通信协议速查

| 方向 | 协议 | 延迟预算 | 可靠性模型 | 典型实现 |
|---|---|---|---|---|
| **Hot ⇄ Hot**（同一 Hot 集群内部）| Shared Memory Ring Buffer / LMAX Disruptor / Aeron | < 10 µs | At-most-once（单副本）+ 硬件 HA | Aeron cluster / LMAX |
| **Hot ⇄ Warm** | Aeron IPC / ZeroMQ PUB-SUB / Shared Memory + polling | < 500 µs | At-least-once + idempotent consumer | Aeron + Python agrona binding |
| **Warm ⇄ Warm** | Redis Streams / Kafka / FastAPI HTTP + WebSocket | 10-100 ms | At-least-once + dedup | Redis Streams / Kafka + aiokafka |
| **Warm ⇄ Cold** | Parquet columnar files on object storage / Redis Streams with long TTL | 秒级（异步）| At-least-once + re-read | S3 / MinIO + pyarrow |
| **Cold → Warm**（模型 / 参数更新回灌）| Model Registry pull + Champion-Challenger shadow validation | 小时级 | Exactly-once（version-pinned）| MLflow / model_registry/ + L13 shadow |
| **Cold ⇄ Cold** | Parquet + Airflow DAG | 分钟-小时 | Checkpointed retries | Airflow / Prefect |

### 4.2 禁止的跨平面通信

| 禁止 | 原因 |
|---|---|
| ❌ Cold → Hot 直接通信 | Cold 无延迟保证，直通会污染 Hot 路径 SLO；**必须经 Warm 中转 + shadow 验证** |
| ❌ Hot 同步调用 Warm Python | Python GIL + asyncio 延迟不可预测，Hot 等 Warm = Hot 降级成 Warm |
| ❌ Warm 同步阻塞等 Cold batch 完成 | Cold 秒级延迟，Warm 阻塞 = 上游 Warm 用户全部被拖垮 |
| ❌ 跨平面共享可变全局状态 | 三平面各自有独立进程 / 容器 / 物理机，共享状态必然竞态 |

### 4.3 契约预留：`shared/contracts/runtime_plane_tag.py`

**职责**：定义运行平面枚举 + docstring 标注规范 + 跨平面契约基类的运行平面声明字段。**本批次仅预留契约，不实施**（本 J1 批次 G 任务同步创建契约文件，详见 §9）。

```python
# shared/contracts/runtime_plane_tag.py (v1.0.0 contract-only, J1 批次 G 落盘) （被恢复）
from enum import Enum

class RuntimePlane(Enum):
    """
    运行平面标签 — 正交于 14 层业务分层的执行维度标签。

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

**预留原则**：
- enum 定义落盘但**不强制任何现有模块立即标注**（避免波动）
- Sprint 0+ 施工时强制**新增子模块必须标注**（OQ-083 关闭时已登记为"未来标注义务"）
- 03-AA §4.1 `runtime_plane` 列作为**主真源**；装饰器 / frontmatter 作为**代码级辅助标注**（J1 批次 C 落盘）

---

## 5. 技术选型矩阵（三平面差异化）

### 5.1 选型矩阵

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

### 5.2 对标 Tech Radar 状态（基于 `architecture_model/technology/technology_landscape.yaml`）

| 技术栈 | Radar 状态 | 激活时机 |
|---|---|---|
| Aeron / LMAX Disruptor | **Trial**（T1 激活后 Adopt）| T1 真实资金 |
| Rust CPython extensions（Warm 热点替换）| **Assess** | T5 性能瓶颈命中 |
| FPGA | **Hold**（ZephyrAlpha 当前不考虑）| T-ULTRA（未定义，≥Sprint 20+）|
| asyncio + FastAPI + Redis Streams | **Adopt**（当前 Warm 主栈）| 当前 |
| Spark / Dask / Airflow | **Adopt**（当前 Cold 主栈）| 当前（施工 Sprint 9 激活 Cold）|

### 5.3 与 04-TA 技术架构的关系

04-TA § 定义**全局技术基线**（Python >=3.11，见 `pyproject.toml` / Redis / PostgreSQL / Parquet 等），本视图 §5 **在平面维度做下钻**——同一业务逻辑在不同平面可能选用不同技术栈（例：L04 风控 Warm Path 用 Python async，Hot Path 用 Rust 重写并通过 Aeron 对接）。**4bis 不替代 04-TA，是补充正交切面**。

### 5.4 预留：Ultra-Hot 子档（未激活）

对于未来可能的超低延迟场景（< 100 µs，FPGA / 纯硬件做市），预留 `RuntimePlane.ULTRA_HOT` 枚举值但**当前不启用**。激活条件：
- **T-ULTRA**（未定义，估计 Sprint 20+）：团队规模 ≥ 5 人 + 自营资金 ≥ $10M + 明确低延迟套利策略 + FPGA 预算 ≥ $100k
- 未命中则 Ultra-Hot 永久不激活（99% 概率）

---

## 6. 激活触发器（P0-P3 分档）

### 6.1 当前基线状态

**ZephyrAlpha 当前阶段（2026-04-19）**：
- 🟢 **Warm Path 100% 激活**（所有 14 层业务代码默认跑在 Warm）
- 🔴 **Hot Path 未激活**（无真实行情 / 无真实委托）
- 🔴 **Cold Path 部分激活**（L02 回测 / L07 归因 / L11 训练，当前 Sprint 9 前小规模）

### 6.2 激活触发器全表

| 触发器 | 档位 | 激活平面 | 激活的子模块 | 激活代价 |
|---|---|---|---|---|
| **T0 当前** | P0 | Warm only | 14 层业务 default + 部分 Cold (L02/L07/L11) | **已激活** |
| **T1 真实资金接入** | P1 | Hot 首次激活 | L04 `limits/stop_loss/monitor` + L06 `sor/adapters_hot` + L10 `ai_security/security_gateway` | 物理机 × 2 + Aeron cluster + C++/Rust 团队 |
| **T2 Cold Path 全量激活** | P2 | Cold 扩展 | L02 `pipeline` 全量 + L05 `backtest` 长周期 + L11 `training` GPU | Spark cluster 或 Dask cluster |
| **T3 Hot Path 扩展** | P2 | Hot 扩展 | + L00 `connectors_hot` + L03 `signals_hot` + L11 `serving_hot` | 增加物理机 + 低延迟行情订阅 |
| **T4 Ultra-Hot 激活** | P3 | Ultra-Hot | FPGA 做市策略专用子模块 | FPGA 硬件 + 专职工程师 |

### 6.3 激活的"只做不做"清单

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

## 7. 与 09-GOV Runtime 层的边界澄清（关键！）

### 7.1 同名不同义

**问题**：09-GOV 三层叫 Policy / Factory / **Runtime**，本视图三平面叫 Hot / Warm / **Cold**（没有叫 Runtime），但在交流中经常被误解为"Runtime 平面 = GOV Runtime 层"。**这是错误的**。

### 7.2 边界对照表

| 维度 | 09-GOV Runtime 层 | 本视图三平面 |
|---|---|---|
| **切片维度** | 治理维度（谁管规则）| 执行维度（代码何时以什么延迟跑）|
| **切片方式** | 按"规则生命周期"切（定规则 Policy / 造工具 Factory / 执行拦截 Runtime）| 按"延迟预算 + 技术栈"切（Hot / Warm / Cold）|
| **所有平面都有 Runtime 吗？** | — | **是**。Hot Path 有 Runtime（C++ OPA 等价物）/ Warm Path 有 Runtime（Python 拦截）/ Cold Path 有 Runtime（Airflow hook 拦截）|
| **Policy 有平面归属吗？** | — | **无**（Policy 是规则文本，不执行）|
| **Factory 有平面归属吗？** | — | **有**——Factory 跑在 Cold Path（构建期 / 定时批调度）|
| **所有业务层都有治理三层吗？** | **是**（治理横切所有层）| 运行平面也是正交标签，但不是每层所有子模块都有 Hot 归属 |

### 7.3 复合命名规则（当二者联合引用时）

当需要联合描述"某代码的治理层 + 运行平面"时，使用**双标签语法**：

```
L04.limits.hard_cut.py  →  [GOV:Runtime] × [Plane:Hot]
L02.pipeline.batch.py   →  [GOV:Runtime] × [Plane:Cold]
scripts/governance/aisg/compile_desensitize_rules.py  →  [GOV:Factory] × [Plane:Cold]
docs/01_policies_and_standards/ai-security-gateway-policy.md  →  [GOV:Policy] × [Plane:—]
```

**格式**：`[GOV:<Policy|Factory|Runtime>] × [Plane:<Hot|Warm|Cold|—>]`

### 7.4 避免混淆的命名约束

**本视图采用的命名约束**（防止与 09-GOV 混淆）：

| 命名 | 含义 | 避免 |
|---|---|---|
| ✅ **Runtime Plane** | 运行平面（执行维度）| 不要单独说 "Runtime" |
| ✅ **Governance Runtime Layer** | 治理 Runtime 层（治理维度）| 不要单独说 "Runtime" |
| ❌ **Runtime**（单独）| 歧义 | 在任何文档中禁止单独使用 "Runtime" 一词 |

---

## 8. Sim-to-Real Gap 保障

### 8.1 问题陈述

**Sim-to-Real Gap**：回测（Cold Path）表现好的策略，在实盘（Warm+Hot Path）表现差，核心差异源于：
- 撮合模型差异（回测假设 mid-price / 实盘有 queue position + adverse selection）
- 延迟差异（回测无延迟 / 实盘 P95 50ms 延迟改变 alpha 衰减）
- 市场冲击差异（回测线性 / 实盘非线性 depending on ADV%）
- 数据差异（回测 survivorship bias 风险 / 实盘 point-in-time）

### 8.2 本视图的保障机制

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

L13 `experiment_pipeline/shadow/` 强制所有 Cold → Warm 模型更新先跑 **Shadow Trading**（Warm Path 并行运行新旧模型，无真实资金）≥ N 天后再晋级到 Hot Path。

**机制三：三平面共享 `risk/`**

风控 `shared/contracts/RiskConstraint` 在 Cold 回测 / Warm 实盘 / Hot 拦截三处必须**使用同一参数文件**（`config/risk_params.yaml`），避免三平面参数漂移。

### 8.3 当前缺口（延后处理）

- 📋 **撮合模型 sim-to-real 对账器**（对比 L05 `backtest/` 撮合与 L06 `sor/` 实际成交）——Sprint 12+
- 📋 **延迟注入器**（Cold 回测时注入 P95 50ms 延迟模拟 Warm 实盘）——Sprint 12+
- 📋 **Adversarial selection 模型**（回测撮合模型引入 queue position）——T1 后 Sprint 14+

上述缺口作为施工阶段 Sprint 12+ 的具体任务，当前本视图只定义契约层保障，实施细节延后。

---

## 9. Revision history / 修订记录

| Date | Description |
|---|---|
| 2026-04-19 | **v1.0.0 首次发布**（S15-experimental J1 批次落地）。新建本视图作为 ZephyrAlpha 2.0 **第一个正交视图（Orthogonal View）**，与 TOGAF 10 视图切片维度正交（业务分层 What vs 运行平面 How/When）。核心内容：(a) §2 三平面定义（Hot < 10ms / Warm 10ms-1s / Cold > 1s）+ 延迟/吞吐/可用性 SLO + 部署拓扑 Mermaid；(b) §3 14 业务层 × 三平面完整映射矩阵（含 shared + L00-L13）+ 前端 + 治理层同步归属；(c) §4 跨平面通信协议（Aeron/Redis Streams/Parquet 三档）+ 禁止直通 Cold→Hot 铁律 + `shared/contracts/runtime_plane_tag.py` 契约预留；(d) §5 技术选型矩阵（C++/Rust Hot / Python asyncio Warm / Spark Dask Cold）+ 与 `technology-landscape.md` Tech Radar 对应 + Ultra-Hot 子档预留；(e) §6 激活触发器 T0-T4 分档（当前 Warm-only → T1 真实资金首激活 Hot → T2/T3 扩展 → T4 Ultra-Hot 永不激活 99%）；(f) §7 **与 09-GOV Runtime 层边界铁律澄清**（同名不同义：09-GOV Runtime 是治理维度 / 本视图 Runtime Plane 是执行维度，强制双标签语法 `[GOV:X] × [Plane:Y]`）；(g) §8 Sim-to-Real Gap 保障机制（跨平面契约统一 + Champion-Challenger Shadow + 共享风控参数）+ 3 条 Sprint 12+ 缺口延后。**对标五家业界共识**：Citadel Securities / Jane Street / Two Sigma / Jump Trading / Renaissance Medallion 均采用业务分层与运行平面正交切分，**无任何一家把延迟特征塞进业务分层**。**架构影响：零代码 / 零目录**——本视图仅定义终局拓扑 + 契约预留，14 层业务本体不变、03-AA §4.1 仅新增 `runtime_plane` 列（由 J1 批次 C 同步）、09-GOV §4.5 D 家族增加 Runtime Plane 归属标注（由 J1 批次 D 同步）。配套：KBG-0011 Runtime Planes Orthogonal View v1.0.0 accepted + OQ-083 closed + R69 登记 rationale-log + handoff-log S15-J1 entry。|
