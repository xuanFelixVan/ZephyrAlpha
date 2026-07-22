---
module_id: VIEW-04PRINC-C4L3
title: C4-L3 域组件图（价值评估中）/ C4 Level 3 Component Diagrams (Pending Value Review)
doc_type: architecture_view
status: Active
version: 0.1.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
valid_from: 2026-07-22
superseded_by: null
supersedes: null
related_rationale: []
related_open_questions:
- OQ-063
tags:
- c4
- c4-l3
- component-diagram
- methodology
- pending-review
summary: 3 张 C4-L3 域组件图（D_MKT_DATA / D_EX_CORE / D_ML_TRAIN），由 target_architecture/diagrams/ 下独立 .mmd 转换为内嵌 mermaid，供价值评估。评估通过则保留为 C4-L3 单一真源；评估不通过则删除。
date: '2026-07-22'
ttl: permanent
---

# C4-L3 域组件图（价值评估中）
# C4 Level 3 Component Diagrams (Pending Value Review)

> ⚠️ **价值评估中 / Pending value review** — 本文档由 3 张独立 `.mmd`（`c4_l3_d_mkt_data` / `c4_l3_d_ex_core` / `c4_l3_d_ml_train`）转换为内嵌 mermaid，供挨个评估其架构价值。
>
> **背景**：原计划将 C4-L3 内嵌到各域文档（`02_domain_architecture_docs/`），但 `generate_domain_doc.py` 每次运行完全覆盖域文档（无保留机制），手动内容会被擦除，故改为独立成文。
>
> **评估后处置**：保留 → 本文档成为 C4-L3 单一真源（原 `.mmd` 删除）；删除 → 一并清理 `.mmd` 与本文档。原 `.mmd` 暂存于 `target_architecture/diagrams/`，评估期允许临时双份。

---

## 1. D-MKT_DATA 行情数据域组件图

> 行情数据域组件分解：Vendor 统一注册中心 + IDataSource 抽象 + Failover 策略 + connectors ACL 扩展区（iFinD/Tushare/AKShare 三段式）+ Autoload 引导 + 原始数据缓存。

> **重写时间**: 2026-06-26 (DM-200913 Phase4-B) ｜ **数据源**: depgraph ｜ **契约真源**: `architecture_model/contracts/cross_layer_contracts.yaml`
> **图例**: 🔒 = frozen (不可变契约) ｜ 🔓 = mutable (可变契约，状态机)
> **命名沿革**: v2.1.0 文件名由 `c4_l3_l00_data_source` 重命名为 `c4_l3_d_mkt_data`（14层前缀→域命名）

```mermaid
%%{init: {'theme': 'default'}}%%
C4Component
    title C4 Level 3 — D-MKT_DATA 行情数据域组件
    title (D-MKT_DATA 数据源域组件分解 / H5)

    Container_Boundary(d_mkt_data, "D-MKT_DATA 行情数据 / Market Data (depgraph派生)") {

        Component(vendor_registry, "Vendor Registry", "Python / vendor_registry.py", "Vendor 统一注册中心：按 asset_class/jurisdiction/data_domain 解析可用 Vendor，含优先级排序与健康状态上报<br/>Vendor Registry: register / resolve / healthcheck_all")

        Component(vendor_base, "IDataSource Base", "Python / vendor_base.py", "抽象接口锁定：fetch_bars / fetch_fundamentals / fetch_corp_actions / healthcheck<br/>所有 Vendor facade 必须实现")

        Component(failover_policy, "Failover Policy", "YAML / failover_policy.yaml", "故障转移策略配置：circuit_breaker 参数 / primary+fallbacks 链 / data_quality_degraded 标志")

        Boundary(connectors, "connectors/ ACL 扩展区") {
            Component(ifind_facade, "iFinD Facade", "Python / stock/cn_ifind/facade.py", "Primary vendor (L0 contractual SLA, ¥2000/mo)：实现 IDataSource，内含 retry + breaker + OTel span")

            Component(ifind_mapper, "iFinD Mapper", "Python / stock/cn_ifind/mapper.py", "外部 iFinD DTO → canonical schema 翻译：单位/时区/PIT 三字段补全")

            Component(ifind_raw, "iFinD Raw Client", "Python / stock/cn_ifind/raw_client.py", "原始 SDK 包装：网络重试、反序列化 Vendor 原生 DTO（不可被其他域 import）")

            Component(tushare_facade, "Tushare Pro Facade", "Python / stock/cn_tushare_pro/facade.py", "Fallback priority 1（UAT 激活后就绪）：同三段结构")

            Component(akshare_facade, "AKShare Facade", "Python / stock/cn_akshare/facade.py", "Fallback priority 2（免费备源）：同三段结构")
        }

        Component(loader, "Autoload Bootstrapper", "Python / __init__.py loader", "启动时遍历 connectors/ 子包，触发 VendorRegistry.register 装饰器")

        ComponentDb(cache, "Raw Data Cache", "DuckDB / Parquet", "按 asof_date 分区的 PIT 原始数据快照（可选缓存层）")
    }

    Container_Ext(shared_contracts, "D-SHARED/contracts/", "Python / canonical schema", "Instrument / Bar / Tick / CorporateAction / FundamentalSnapshot")

    Container_Ext(d_factor, "D-FACTOR 因子", "Python / D-FACTOR/", "因子消费侧（通过 IDataSource）")

    System_Ext(vendor_ext, "External Vendors", "iFinD / Tushare / AKShare / Polygon / ...")

    System_Ext(d_ops, "D-OPS 反馈循环", "OTel Collector / Prometheus", "metrics + traces 接收")

    Rel(d_factor, vendor_registry, "resolve(asset_class, jurisdiction, data_domain)", "解析可用 Vendor")
    Rel(vendor_registry, ifind_facade, "returns (primary)")
    Rel(vendor_registry, tushare_facade, "returns (fallback 1)")
    Rel(vendor_registry, akshare_facade, "returns (fallback 2)")
    Rel(vendor_registry, failover_policy, "reads policy")

    Rel(ifind_facade, ifind_mapper, "applies mapper", "canonical 翻译")
    Rel(ifind_mapper, ifind_raw, "calls raw_client", "Vendor 原生 DTO")
    Rel(ifind_mapper, shared_contracts, "outputs canonical", "Bar / Instrument / ...")
    Rel(ifind_raw, vendor_ext, "HTTPS / SDK", "REST / WebSocket")

    Rel(loader, vendor_registry, "bootstraps registration", "autodiscover on import")
    Rel(ifind_facade, failover_policy, "circuit breaker config")
    Rel(ifind_facade, cache, "read/write snapshot", "PIT 缓存")
    Rel(ifind_facade, d_ops, "emits trace + metric", "zephyr_vendor_hit / zephyr_vendor_failure")

    UpdateRelStyle(d_factor, vendor_registry, $offsetX="-40", $offsetY="-10")
```

---

## 2. D-EX_CORE 执行核心域组件图

> 执行核心域组件分解：IBroker 抽象契约 + OMS 订单生命周期 + Idempotency Guard（量化红线）+ SOR 智能路由 + Pre-Trade Risk Proxy + adapters 扩展区（Simulation/Real Broker）+ Fill Handler + Position Tracker。

> **重写时间**: 2026-06-26 (DM-200913 Phase4-B) ｜ **数据源**: depgraph ｜ **契约真源**: `architecture_model/contracts/cross_layer_contracts.yaml`
> **图例**: 🔒 = frozen (不可变契约) ｜ 🔓 = mutable (可变契约，状态机)
> **命名沿革**: v2.1.0 文件名由 `c4_l3_l06_trade_execution` 重命名为 `c4_l3_d_ex_core`（14层前缀→域命名）

```mermaid
%%{init: {'theme': 'default'}}%%
C4Component
    title C4 Level 3 — D-EX_CORE 执行核心域组件
    title (D-EX_CORE 执行域组件分解 / H5)

    Container_Boundary(d_ex_core, "D-EX_CORE 执行核心 / Trade Execution (depgraph派生)") {

        Component(broker_interface, "IBroker Interface", "Python / broker_interface.py", "🔒 BrokerInterface 抽象契约（锁死）：submit / cancel / query_status / stream_fills / get_positions")

        Component(oms, "OMS — Order Management", "Python / oms.py", "订单生命周期管理：pending → submitted → filled / cancelled；状态机 + audit hook")

        Component(idempotency_guard, "Idempotency Guard", "Python / idempotency.py", "**量化红线**：Idempotency Key 生成 + Redis SETNX 去重 + journal append-only 冷层（详见 §9 H10 / src-domain/idempotency-design.md）")

        Component(sor, "SOR — Smart Order Router", "Python / sor.py", "多 broker 路由决策：按 fee / 流动性 / 接入状态选 broker；接入 §8 failover")

        Component(pre_trade_risk_proxy, "Pre-Trade Risk Proxy", "Python / pre_trade_proxy.py", "风控代理（调用 D-RISK）：单订单阈值 + 组合级校验 ≤1s 延迟（SLO-3）")

        Boundary(adapters, "adapters/ Broker 扩展区") {
            Component(sim_adapter, "Simulation Adapter", "Python / adapters/simulation_adapter.py", "当前阶段默认：本地撮合模拟，实现 IBroker")

            Component(broker_xxx, "Real Broker Adapter", "Python / adapters/broker_{vendor}.py", "Post-Activation 激活：各家券商 SDK 实现 IBroker（Interactive Brokers / 华泰 / 中信 / ...）")
        }

        Component(fill_handler, "Fill Handler", "Python / fill_handler.py", "成交回报消费：写 audit journal（RPO=0）+ 更新 positions + 触发 D-TRADING")

        Component(position_tracker, "Position Tracker", "Python / positions.py", "实时持仓跟踪：内存缓存 + 定期持久化 + T+1 对账")
    }

    Container_Ext(d_pf_core, "D-PF_CORE 组合核心", "Python / D-PF_CORE/", "订单源：optimizer 输出目标仓位")

    Container_Ext(d_risk, "D-RISK 风控", "Python / D-RISK/", "pre-trade 实时风控决策")

    Container_Ext(d_trading, "D-TRADING 交易运营", "Python / D-TRADING/", "成交后归因 + 对账")

    Container_Ext(d_compliance, "D-COMPLIANCE 合规", "Python / D-COMPLIANCE/", "合规检查（辖区规则 / 自成交 / 洗售）")

    ContainerDb_Ext(audit_journal, "Audit Journal (L2 Log)", "JSONL append-only + Loki", "**零丢失约束**：每笔订单/成交/幂等 key 持久化（DR RPO=0）")

    ContainerDb_Ext(redis_idem, "Redis Idempotency Layer", "Redis SETNX + TTL", "Key 热层：交易日级去重窗口")

    System_Ext(broker_ext, "Broker API", "券商 API（实盘激活后）")

    Container_Ext(d_ops, "D-OPS 反馈循环", "OTel / Prometheus", "订单延迟 + 成交吞吐 + 幂等命中率")

    Rel(d_pf_core, oms, "submits target orders", "目标委托")
    Rel(oms, idempotency_guard, "check before send", "Key 生成 + SETNX")
    Rel(idempotency_guard, redis_idem, "SETNX + TTL", "交易日窗口")
    Rel(idempotency_guard, audit_journal, "append Key + decision", "append-only")

    Rel(oms, pre_trade_risk_proxy, "risk check", "<1s SLO-3")
    Rel(pre_trade_risk_proxy, d_risk, "delegates", "风控规则执行")
    Rel(pre_trade_risk_proxy, d_compliance, "delegates", "合规检查")

    Rel(oms, sor, "route decision", "选 broker")
    Rel(sor, sim_adapter, "when simulation", "模拟撮合")
    Rel(sor, broker_xxx, "when live", "Post-Activation")

    Rel(sim_adapter, broker_interface, "implements")
    Rel(broker_xxx, broker_interface, "implements")
    Rel(broker_xxx, broker_ext, "HTTPS / FIX", "submit + stream")

    Rel(broker_ext, fill_handler, "fills / status", "成交回报")
    Rel(sim_adapter, fill_handler, "simulated fills")
    Rel(fill_handler, audit_journal, "append fill", "RPO=0")
    Rel(fill_handler, position_tracker, "update positions")
    Rel(fill_handler, d_trading, "notifies", "归因入口")

    Rel(oms, d_ops, "emits", "zephyr_order_duration / zephyr_order_outcome")
    Rel(idempotency_guard, d_ops, "emits", "zephyr_idempotency_hit")
```

---

## 3. D-ML_TRAIN 训练域组件图

> 训练域组件分解：Feature Store + PIT Query Engine + Training Pipeline + Model Registry + Inference Engine + Drift Monitor + Shadow/Canary Mode + AI Operator 预留口子（OQ-063）。

> **重写时间**: 2026-06-26 (DM-200913 Phase4-B) ｜ **数据源**: depgraph ｜ **契约真源**: `architecture_model/contracts/cross_layer_contracts.yaml`
> **图例**: 🔒 = frozen (不可变契约) ｜ 🔓 = mutable (可变契约，状态机)
> **命名沿革**: v2.1.0 文件名由 `c4_l3_l11_ml_platform` 重命名为 `c4_l3_d_ml_train`（14层前缀→域命名）

```mermaid
%%{init: {'theme': 'default'}}%%
C4Component
    title C4 Level 3 — D-ML_TRAIN 训练域组件
    title (D-ML_TRAIN ML平台域组件分解 / H5)

    Container_Boundary(d_ml_train, "D-ML_TRAIN 训练 / ML Platform (depgraph派生)") {

        Component(feature_store, "Feature Store", "Python / feature_store/", "特征物化层：按 entity_id × asof_date PIT 对齐；写入供训练、读取供 inference")

        Component(pit_query, "PIT Query Engine", "Python / pit_query.py", "反 Survivorship 查询：强制带 asof_date + knowledge_date 双游标（05-DA §5 铁律）")

        Component(training_pipeline, "Training Pipeline", "Python / training/", "模型训练编排：数据集切分 + CV + metric 记录，输出 model artifact")

        Component(model_registry, "Model Registry", "Python / model_registry.py", "模型版本化 + lifecycle：draft/staging/prod/archived；每版绑定训练数据快照 id")

        Component(inference_engine, "Inference Engine", "Python / inference/", "生产推理：load by model_id + version + stage，emit metric 延迟/吞吐")

        Component(drift_monitor, "Drift Monitor", "Python / monitoring/drift.py", "feature drift / label drift / concept drift 三类监控；超阈值触发回滚或重训")

        Component(shadow_mode, "Shadow / Canary Mode", "Python / deployment/shadow.py", "新模型对比生产模型：影子跑不写下游 / 金丝雀 5-10% 流量")

        Boundary(ai_operator_slot, "ai_operator/ 预留口子（OQ-063 C-1）") {
            Component(ai_op_reserved, "AI Operator Slot", "Python / D-ML_TRAIN/_ai_operator/ (reserved)", "AI Operator 激活口子：OQ-063 P4 未来态，当前为空 skeleton")
        }
    }

    Container_Ext(d_factor, "D-FACTOR 因子", "Python / D-FACTOR/", "因子供 feature 来源")

    Container_Ext(d_mkt_data, "D-MKT_DATA 行情数据", "Python / D-MKT_DATA/", "原始数据 via IDataSource")

    Container_Ext(d_signal_pf, "D-SIGLEGACY/D-PF_CORE 信号&组合", "Python / D-SIGLEGACY + D-PF_CORE/", "下游推理消费者")

    Container_Ext(d_intelligence, "D-INTELLIGENCE 战略决策", "Python / D-INTELLIGENCE/", "A/B 实验与批跑研究")

    ContainerDb_Ext(artifact_storage, "Model Artifact Storage", "MLflow / 本地 + S3", "模型文件 + training dataset snapshot hash")

    ContainerDb_Ext(feature_storage, "Feature Storage", "Parquet / DuckDB", "按 entity × asof_date 分区")

    Container_Ext(d_ops, "D-OPS 反馈循环", "OTel + Prometheus", "训练/推理 metric + 漂移 metric")

    Rel(d_factor, feature_store, "writes factors as features", "feature ingest")
    Rel(d_mkt_data, feature_store, "writes raw features", "via pit_query")
    Rel(feature_store, feature_storage, "persists", "Parquet partition")
    Rel(feature_store, pit_query, "uses PIT semantics", "asof + knowledge")

    Rel(training_pipeline, feature_store, "reads training data", "PIT window")
    Rel(training_pipeline, model_registry, "registers artifact", "new version draft")
    Rel(model_registry, artifact_storage, "stores artifact", "versioned")

    Rel(inference_engine, model_registry, "loads model", "by stage")
    Rel(inference_engine, feature_store, "reads live features", "for scoring")
    Rel(inference_engine, d_signal_pf, "serves predictions", "signal input")

    Rel(drift_monitor, feature_store, "observes distribution")
    Rel(drift_monitor, inference_engine, "observes predictions")
    Rel(drift_monitor, d_ops, "emits drift metric", "zephyr_model_drift_score")

    Rel(shadow_mode, inference_engine, "duplicates traffic", "5-10% canary")
    Rel(d_intelligence, training_pipeline, "triggers experiments", "A/B job")

    Rel(ai_op_reserved, model_registry, "future: auto-promote/rollback", "OQ-063 P4")
```

---

## 说明 / Notes

- **来源 / Source**: 3 张 `.mmd`（`c4_l3_d_mkt_data` / `c4_l3_d_ex_core` / `c4_l3_d_ml_train`），原存于 `target_architecture/diagrams/`
- **转换规则**: 剥离文件级 `%%` 注释（重写时间/数据源/图例/契约真源/命名沿革）为 `>` 引用行；保留 `%%{init:...}%%` 主题指令与 `C4Component` 主体于 mermaid 代码块
- **评估要点 / Review Focus**:
  - 组件命名是否与实际代码（`src/zephyr/market_data/` / `src/zephyr/ex_core/` / `src/zephyr/ml_train/`）一致？
  - 是否描绘了尚未实现的理想化结构（如 SOR / Drift Monitor / AI Operator Slot）？
  - 作为 C4-L3 单一真源保留，还是因与代码脱节而删除？
- **关联 / Related**: `application_principles.md` §2.3/§2.4（C4 视图分层）已指向本文档
