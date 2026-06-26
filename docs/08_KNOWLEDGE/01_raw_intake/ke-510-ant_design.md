---
module_id: KE-459------ant-design-000
status: active
title: 6.3 组件库与 Ant Design 的关系
category: documentation
ttl: permanent
---

# 6.3 组件库与 Ant Design 的关系

6.3 组件库与 Ant Design 的关系

**铁律**：

- Ant Design v5 是**底座**（提供 Button / Form / Table 等原子）
- `ui-kit/primitives/` 是**封装层**（固定默认样式 / 国际化 / 错误处理 / 无障碍 ARIA）
- apps/ **不得直接 import Ant Design**，必须经 ui-kit

这一层封装将来支撑"切换底座到 Material UI 或 Radix"的可能性（方案 R，FE-P7 渐进升级的降级路线）。
