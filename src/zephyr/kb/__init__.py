"""
ZephyrAlpha 知识库子包
======================

职责：知识生命周期管理——从文档/代码中摄取结构化和非结构化知识，
经分析、提取、验证后激活，供 AI Agent 查询与决策使用。

子模块：
  - activate.py            知识激活（暂存 → 正式索引）
  - analyze.py             语义分析 + 关系抽取
  - batch_ingest.py        批量知识摄入
  - chromadb_init.py       ChromaDB 向量数据库初始化
  - embedding_migrate.py   嵌入向量迁移
  - extract.py             结构化/非结构化知识提取
  - graph_validator.py     知识图谱校验
  - ingest.py              单条知识摄入
  - kb_repo.py             知识库 CRUD 仓库
  - triage.py              知识分诊（优先级排序）
  - unified_memory_api.py  统一内存 API

架构归属：B-track 独立能力，Phase 1 过渡期独立子包（不影响 C-track）。
Phase 3 计划整合入 vector_memory/ (VMS)。

注意：本包当前 bounded_context: false——直接暴露所有模块供
orchestrator/ + l12/ 消费，不设受限边界。
"""
from __future__ import annotations
