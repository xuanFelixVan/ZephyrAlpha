# Knowledge Base 模块索引

> MOD-KB-001 | 施工#07 active

| 维度 | 详情 |
|------|------|
| 蓝图路径 | [blueprint.md](./blueprint.md) |
| 代码路径 | `src/zephyr/kb/` |
| KE存放路径 | `docs/08_knowledge/` |
| 施工Phase | Phase 3 — G3分析+分词已实现 |
| 架构YAML | `architecture-model/layers/b_kb.yaml` |
| MCP Server | `src/zephyr/mcp/knowledge_base_server.py` |
| 37字段Schema | `src/zephyr/shared/schemas.py` (KeEntry) |
| 核心入口 | `src/zephyr/kb/kb_repo.py` |

## 施工Phase状态

| Phase | 状态 | 描述 |
|-------|:---:|------|
| Phase 1 | ✅ | G1摄取 + 基础Schema |
| Phase 2 | ✅ | G2分拣 + embedding管道 |
| Phase 3 | 🔧 | G3分析 + MCP KB Server |
| Phase 4 | 📋 | G4激活 + 上下文串联 |
| Phase 5 | 📋 | G5提取 + 语义去重 |
