---
module_id: KE-1633
title: 2. 四大黄金信号
category: module_blueprint
---

# 2. 四大黄金信号

2. 四大黄金信号

对标 Google SRE 4 Golden Signals：

| 信号 | 维度 | 采集来源 | 阈值示例 |
|------|------|---------|---------|
| **Latency**（延迟） | LLM API 响应时间 / 脚本执行时长 / Pipeline 端到端耗时 | MCP servers / subprocess tracker | P95 > 30s → FLE 告警 |
| **Errors**（错误） | LLM 调用失败 / Gate 拒止 / 校验不通过 | Gate Engine / CE / Script System | 错误率 > 5% → FLE 自动降级 |
| **Traffic**（流量） | LLM 调用总量 / 任务卡生成速率 / API 请求 QPS | Pipeline / LSG / MCP | LLM QPS > 100 → Token Budget 预警 |
| **Saturation**（饱和度） | Context Engine Token 填充率 / VMS Collection 占用 / DB 连接池 | CE / VMS / Database | CE 填充 > 90% → 自动截断旧 Session |

---
