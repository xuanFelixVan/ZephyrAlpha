---
module_id: "ALPHA-SIGNAL-DOMAIN-001"
title: "Alpha-Signal 因子域总蓝图 — L02 Alpha因子 → L03 信号生成 跨层集成"
doc_type: blueprint
status: Active
version: "0.1.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
tags: [alpha-signal-domain, l02, l03, alpha-factor, signal-generation, domain-integration]
created_by: human_plus_agent
date: "2026-05-06"
valid_from: "2026-05-06"
ttl: permanent
construction_progress: not_started
submodule_path: src/zephyr/
submodule_paths_scope: alpha-signal-domain
submodule_paths_extra:
  - src/zephyr/l02_alpha_factor/
  - src/zephyr/l03_signal_generation/
priority: P1
blueprint_level: domain
summary: "Alpha因子域（L02 + L03）Level 1 集成蓝图——定义 Alpha因子核心(MOD-AF-001)到信号生成核心(MOD-SIG-001)的数据流、接口契约、共享数据模型和施工门禁。本蓝图不重复 L02/L03 模块内部规范，只定义跨层集成协议。"
construction_progress: not_started
belongs_to: "SYS-MASTER-001"
ai_role_instruction: >
  你是 Alpha-Signal 因子域的 Level 1 集成蓝图。
  职责：(1) 定义 L02 Alpha因子 → L03 信号生成的完整数据流拓扑；
  (2) 定义跨层接口契约 AS-CT-*——AI agent 施工前 MUST 对照契约表；
  (3) 真源优先级：SYS-MASTER-001 §53~§57 > 本蓝图 > L02/L03 模块蓝图；
  (4) 跨层变更 MUST 先读本蓝图 §二契约表，所有接口改动 = registry 同步；
  (5) L02/L03 蓝图开工前 MUST L01 TaskCard 拆解通过 G0 门禁。
---

# Alpha-Signal 因子域总蓝图

## §一 跨层数据流拓扑

```
Market Data (L00) → Alpha Factor Core (L02)
  ├── 因子计算[technical/statistical/ML]
  ├── 因子清洗/去重[INF-005 code-dedup-engine]
  ├── 因子存储[INF-012 database: ALPHA_FACTORS table]
  └── ↓
Signal Generation Core (L03)
  ├── 信号合成[多因子→单信号]
  ├── 信号评估[IC/IR/Sharpe/shuffled test]
  ├── 信号发送[→ L04 Risk Management 风控门]
  └── 信号存档[IN-012 database: SIGNALS table]
```

## §二 跨层接口契约

| 契约ID | 方向 | 描述 | 状态 | CT引用 |
|---------|------|------|:---:|------|
| AS-CT-DATA-001 | L00→L02 | 市场数据→因子引擎（OHLCV/orderbook/tick） | Draft | — |
| AS-CT-FACTOR-001 | L02→L03 | 因子数据帧（MultiIndex DataFrame: (timestamp, asset)×factor） | Draft | — |
| AS-CT-FACTOR-002 | L02 internal | Code-Dedup-Engine→去重后的因子值（唯一source_key） | Draft | MOD-INF-005 |
| AS-CT-SIGNAL-001 | L03→L04 | 信号数据帧→风控引擎 | Draft | — |
| AS-CT-VMS-001 | L02+L03→VMS | 因子嵌入向量存储（8 collections: signal-embeddings） | Draft | MOD-INF-011 |

## §三 施工门禁

- L02/L03 蓝图开工前 MUST 通过 G0 TaskCard 拆解
- 因子→信号链路变更 MUST 通过 G6 蓝图合规门禁
- 新因子类型注册 MUST 更新 `wt_factor_universe.yaml`
- 所有因子计算 MUST 被 Telemetry(INF-015) instrument

## §四 故障模式

| FMEA ID | 故障 | 影响 | 缓解 |
|---------|------|------|------|
| AS-FMEA-001 | L02 crash mid-factor → stale因子入L03 | 错误信号触发交易 | Checkpoint + 增量因子刷新 |
| AS-FMEA-002 | L03 signal合成参数漂移 | 信号质量退化未发现 | Drift Detector(INF-023) 因子分布监控 |
| AS-FMEA-003 | Code-Dedup 误删唯一因子 | 因子缺失→信号失真 | Audit Trail(INF-020) 每因子 source_hash |


---

## 施工落盘确认（2026-05-07 审计）

| 维度 | 状态 |
|------|------|
| construction_progress | not_started（蓝图文档完成，L02/L03模块 blocked_by_infrastructure，跨层管道未施工） |
| 文档路径 | docs/03_modules/_alpha-signal-domain/blueprint.md (域集成文档) |
| 说明 | 架构/集成文档——定义跨模块契约与集成标准。底层C轨模块 blocked_by_infrastructure，代码施工待基建域就绪后启动 |
