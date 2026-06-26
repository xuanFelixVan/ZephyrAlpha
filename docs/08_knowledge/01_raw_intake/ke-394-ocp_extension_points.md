---
module_id: KE-358
status: active
title: 4.4 OCP Extension points / 扩展点设计
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 4.4 OCP Extension points / 扩展点设计

4.4 OCP Extension points / 扩展点设计

> 三个扩展点遵循 Open-Closed Principle。契约（基类 + 注册表）锁死，实现无限扩展。
> 完整接口签名 → `architecture_model/contracts/cross_layer_contracts.yaml`。

系统定义三个核心 OCP 扩展点：

| 扩展点 | 所属层 | 基类 | 注册表 | 用途 |
|:---|:---|:---|:---|:---|
| **因子扩展点** | L02 | `FactorBase` | `FactorRegistry` | 新增 Alpha 因子不修改引擎 |
| **策略扩展点** | L05 | `StrategyBase` | `StrategyRegistry` | 新增组合策略不修改调用方 |
| **券商扩展点** | L06 | `BrokerInterface` | Broker Vendor Registry | 新增券商适配器不修改订单流 |

新增因子/策略/券商适配器只需继承基类并注册，无需修改已有代码。
