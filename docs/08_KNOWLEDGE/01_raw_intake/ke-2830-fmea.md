---
module_id: KE-2732
status: active
title: 十六、FMEA 故障模式分析
category: module_blueprint
ttl: permanent
---

# 十六、FMEA 故障模式分析

十六、FMEA 故障模式分析

> **定位**：预判系统"哪里最可能出错"→优先加固。
> **对标**：NASA FMEA + Google SRE Risk Analysis。

| ID | 故障模式 | 影响 | 检测方法 |
|------|------|------|------|
| F1 | 行情数据延迟>5s | 信号过期→错误交易 | 心跳超时检测 |
| F2 | 信号计算异常(WAL损坏) | 信号=噪声→随机交易 | 信号分布监控(§37) |
| F3 | 订单重复提交 | 错误加倍→损失×2 | 订单ID去重+幂等(§45) |
| F4 | 风控模块SQLite锁 | 止损不生效 | Health Panel(§0.0) |
| F5 | API 密钥过期 | 系统离线 | Secrets轮替日历(§69) |
| F6 | 喂入未来的数据(Look-ahead) | 回测虚高→实盘崩溃 | 逐日验证(§42.3) |
| F7 | 经纪商API 不可达 | 无法下单/撤单 | Heartbeat+Circuit Breaker |
| F8 | 灾难性遗忘(session断裂) | AI不知道过去决策 | §0分派表+SessionContinuity |

---
