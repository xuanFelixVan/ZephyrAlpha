---
module_id: KE-2592
status: active
title: config/db_config.yaml
category: module_blueprint
ttl: permanent
---

# config/db_config.yaml

config/db_config.yaml
kb:
  data_root: ${KB_DATA_DIR:-data/}             # 根目录——环境变量覆盖，默认 data/
  sqlite:
    db_path: ${KB_SQLITE_PATH:-data/sqlite/kb_state.db}
  chroma:
    persist_dir: ${KB_CHROMA_DIR:-data/chroma/}
  cache:
    reranker_model: ${KB_RERANKER_DIR:-data/cache/bge-reranker-v2-m3/}
```

**磁盘布局**：

```

├── data/                          # 所有运行时数据根目录（不入 Git 的生产数据）
│   ├── .gitkeep                   # 空目录占位——确保 Git 追踪 data/ 的存在
│   ├── sqlite/                    # SQLite 数据库引擎文件
│   │   └── kb_state.db            #   knowledge_entries + kb_rules + state_log
│   ├── chroma/                    # ChromaDB 持久化目录（向量 + 全文本索引）
│   │   ├── chroma.sqlite3         #   Chroma 自动生成——元数据 (Sysdb + WAL + Metadata)
│   │   ├── index/                 #   Chroma 自动生成——HNSW 向量索引 binary
│   │   └── {collection_uuids}/    #   Chroma 自动生成——每 Collection 独立 Segment
│   └── cache/                     # 推理缓存（模型权重）
│       └── bge-reranker-v2-m3/    #   Reranker 模型 (~1.2GB, beta 下载)
│
├── docs/
│   └── 08_knowledge/              # Markdown KE 文件（图书馆——§4.2）
│
├── .gitignore                     # 数据库文件的 Git 策略 ↓
└── config/
    └── db_config.yaml             # 数据库路径配置（环境变量 + 默认值）
```

**`.gitignore` 三级策略**：

| 级别 | 内容 | Git 追踪？ | 理由 |
|:---:|------|:---:|------|
| L1 | `data/.gitkeep`、SQL migration schema 文件 | ✅ | 保证目录结构一致 + 数据库版本可重建 |
| L2 | `data/sqlite/kb_state.db`（开发环境种子数据） | ⚠️ 可选 | 方便新 AI session 快速启动——需 Owner 显式 `git add -f` |
| L3 | `data/chroma/**`、生产 `*.db`、`data/cache/**` | ❌ | 二进制大文件 + 可从 Markdown KE 重建（`embedding_migrate.py reindex`） |

```gitignore
