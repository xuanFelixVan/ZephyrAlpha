---
module_id: KE-3248
title: 3.1 总览表（按业务层维度）
category: documentation
ttl: permanent
---

# 3.1 总览表（按业务层维度）

3.1 总览表（按业务层维度）

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
| | `
