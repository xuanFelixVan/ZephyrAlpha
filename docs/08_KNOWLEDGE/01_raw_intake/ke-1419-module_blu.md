---
module_id: KE-1329
title: 1.4 责任边界（不管什么——去哪找）
category: module_blueprint
---

# 1.4 责任边界（不管什么——去哪找）

1.4 责任边界（不管什么——去哪找）

| 不管的内容 | 正确位置 |
|-----------|---------|
| 任务系统的 TaskCard 状态机和任务生命周期 | MOD-INF-006（任务系统蓝图） |
| 上下文引擎的 Token 预算追踪和注入策略 | `context_engine/` 模块（ADR-0015） |
| VMS（Vector Memory Service）的 `InProcessVectorMemory` | `src/zephyr/vector-memory/`（beta 目标，当前空包） |
| Session Log 的结构和交接协议 | `_registry/schemas/session-log-schema.yaml` |
| 蓝图的结构注册和治理 | 各模块 `blueprint.md`（本蓝图只管理知识库自身的蓝图） |
| **脚本系统的 12 维度审计结果**（MEDIUM Finding → KB 入库） | **MOD-INF-005 §6.3 + §6.6**（脚本系统蓝图——C4→G1 数据流） |
| **脚本系统的审计执行**（C1-C5 流水线运行逻辑） | **MOD-INF-005**（脚本系统蓝图——KB 只消费审计结果，不执行审计） |
