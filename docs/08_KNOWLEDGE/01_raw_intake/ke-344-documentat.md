---
module_id: KE-344
status: active
title: 4.1 架构定位
category: documentation
---

# 4.1 架构定位

4.1 架构定位

- `infra_ops/` 层是传统可观测性代码归属（OpenTelemetry 导出）
- **Feedback Loop Engine (FLE)** 是 6 大核心服务的"自动化运维大脑"，所有服务指标→FLE→异常检测→动作分派
- 两者关系：OpenTelemetry 面向"人工看板 + 外部工具"；FLE 面向"系统内部自调节"
