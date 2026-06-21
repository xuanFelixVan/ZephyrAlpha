---
module_id: KE-263
status: active
title: 3.2 总览表（按运行平面维度 — 反查视图）
category: documentation
---

# 3.2 总览表（按运行平面维度 — 反查视图）

3.2 总览表（按运行平面维度 — 反查视图）

> 按平面维度的反查视图同样收录于 [`runtime_planes.yaml`](architecture-model/cross-cutting/runtime_planes.yaml)（`planes.hot.modules[]` / `planes.warm.modules[]` / `planes.cold.modules[]`）。以下为可读摘要：

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
