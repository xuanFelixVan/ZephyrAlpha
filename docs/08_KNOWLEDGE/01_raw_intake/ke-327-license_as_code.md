---
module_id: KE-300
status: active
title: 原则 3：License-as-Code / 许可证即代码
category: documentation
ttl: permanent
---

# 原则 3：License-as-Code / 许可证即代码

原则 3：License-as-Code / 许可证即代码

> 所有依赖项的许可证必须通过 SBOM 自动扫描（L10 文件治理）。GPL/AGPL 项目进入代码库前必须经过 ARB 特批。

**许可证分类标准**：

| 许可证类型 | 是否允许自动引入 | 条件 |
|----------|:---:|------|
| MIT / Apache 2.0 / BSD | ✅ 允许 | 无额外条件 |
| MPL 2.0 / LGPL | ⚠️ 允许（需登记） | 仅限动态链接，不修改源码 |
| GPL / AGPL | ❌ 禁止自动引入 | 必须经 ARB 特批 + Owner 签字 |
| 无许可证（Unlicensed） | ❌ 禁止 | 等同于 All Rights Reserved |

---
