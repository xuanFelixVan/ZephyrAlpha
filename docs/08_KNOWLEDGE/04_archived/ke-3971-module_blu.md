---
module_id: KE-3818
title: 11.4 回滚方案
category: module_blueprint
ttl: permanent
---

# 11.4 回滚方案

11.4 回滚方案

| 步骤 | 回滚 |
|------|------|
| 1（注册表） | 手动回退 YAML |
| 2（元注册表） | 手动回退——恢复 v0.2.0 迁移状态 |
| 3（models.py） | 恢复 v0.2.0 独立 TaskCard 模型 |
| 4（decomposer） | 恢复旧版——用 .md 为主的方式 |
| 5（MCP Server） | 恢复旧版 4 Tool |
| 6（context+M1-M11） | 此步骤与 v0.2.0 相同——回滚成本低 |
