---
module_id: KE-module_blu-14_3_shared-003
title: 14.3 Shared 层准入边界规则
category: module_blueprint
---

# 14.3 Shared 层准入边界规则

14.3 Shared 层准入边界规则

> 为防止 shared/ 膨胀为垃圾场，新增模块进入 shared/ 必须同时满足：
> 1. 被 ≥2 个 L01 模块消费（或预期会被消费）
> 2. 不绑定任何特定业务域
> 3. 接口粒度 ≤ Protocol/dataclass/Enum（不包含重量级实现）

---
