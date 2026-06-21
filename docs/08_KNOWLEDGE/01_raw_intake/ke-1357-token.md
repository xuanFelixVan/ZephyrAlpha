---
module_id: KE-1268
title: 0.1 Token 预算
category: module_blueprint
---

# 0.1 Token 预算

0.1 Token 预算

| 阅读深度 | 读什么 | Token 消耗 | 适用场景 |
|:---:|------|:---:|------|
| 🔥 紧急 | `ai_role_instruction` + 拓扑图 + 合同总表 + 你系统的分派行 | ~500 | 新 AI session 冷启动 |
| 📋 标准 | 紧急 + 你负责系统的全部 CT-* 合同 | ~1500 | 开发跨系统功能 |
| 📚 完整 | 全文 | ~12000 | 架构审查 / 新系统接入 |

**新 AI session 默认从 🔥 紧急开始，按任务需求升级。**
