---
module_id: KE-1435
title: 12.4 回滚方案
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 12.4 回滚方案

12.4 回滚方案

| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| Phase 1 | 某模块集成失败 | 该模块降级为 skip（noop），其他模块继续 |
| Phase 2 | 迁移数据损坏 | 从 kb/ 旧 Collection 重新迁移；BridgeLayer 回退到仅读 kb/ |
| Phase 3 | 混合检索精度低于纯向量 | 切换为纯向量模式 + score threshold 收紧 |
| Phase 4 | HealthMonitor 错误清除了活跃数据 | 从 snapshot 恢复 |
