---
module_id: KE-2329-------------placeholder-003
status: active
title: 6. 文件清单与落位（不留 placeholder）
category: module_blueprint
ttl: permanent
---

# 6. 文件清单与落位（不留 placeholder）

6. 文件清单与落位（不留 placeholder）

```

├── src/zephyr/
│   ├── vector-memory/                              # ⏳ experimental 新建
│   │   ├── __init__.py                             # 导出 get_vm() 工厂（按配置返回 InProcess 或 Remote 实现）
│   │   ├── protocol.py                             # VectorMemoryProtocol 抽象基类（§1.3）
│   │   ├── in_process.py                           # experimental 实现（ChromaDB SDK）
│   │   ├── remote.py                               # beta 实现占位（当前不开发）
│   │   ├── schemas.py                              # Pydantic schemas（§3.3）
│   │   ├── cascade.py                              # CascadeStrategy + CASCADE_SCENARIOS（§3.2）
│   │   ├── chunker.py                              # 递归字符分块
│   │   ├── embedder.py                             # BGE-M3 ONNX 封装
│   │   ├── chroma_adapter.py                       # ChromaDB 0.6 适配层
│   │   ├── collections.py                          # 4 个预定义 Collection 初始化
│   │   ├── routing.py                              # 路径 → Collection 路由规则（§7.3）
│   │   ├── bulk_bootstrap.py                       # bulk_bootstrap 断点续传
│   │   ├── sync.py                                 # sync_document git hook 入口
│   │   ├── rrf.py                                  # RRF 融合算法
│   │   └── config.py                               # VMConfig 加载
│   ├── config/
│   │   ├── embedding_model_registry.yaml           # ✅ 已存在
│   │   └── vector-memory.yaml                      # ⏳ 新建：runtime_root 引用 + ChromaDB 配置
│   └── clients/                                    # beta 启用时才建
│
├── vibe_config.yaml                                # ⏳ B-d 修订新增字段
│   # 新增字段：
│   #   runtime_root: ${ZEPHYR_RUNTIME_ROOT:-.runtime}   # 支持环境变量覆盖
│   #   models_root:  ${ZEPHYR_MODELS_ROOT:-.models}
│
├── .runtime/                                       # ⏳ 运行时数据根目录（加 .gitignore）
│   ├── chromadb/                                   # ← ChromaDB 持久化（按 Collection 分 persist_directory）
│   │   ├── decisions/
│   │   ├── code_context/
│   │   ├── task_history/
│   │   └── lessons/
│   ├── sqlite/                                     # 预留（Orchestrator 任务队列 / Session Log）
│   ├── logs/                                       # 预留（运行时日志）
│   ├── cache/                                      # 预留（TTL 缓存）
│   └── vector_memory_bootstrap.ckpt                # bulk_bootstrap 断点
│
├── .models/                                        # ⏳ 本地模型（加 .gitignore）
│   └── bge-m3/                                     # ONNX 模型文件 (~1.2GB)
│
├── tests/unit/vector-memory/                       # ⏳ experimental 新建
│   ├── test_chunker.py
│   ├── test_embedder.py
│   ├── test_chroma_adapter.py
│   ├── test_api_ingest.py
│   ├── test_api_sync.py
│   ├── test_api_search.py
│   ├── test_api_multi_search.py                    # 含 RRF 融合测试
│   ├── test_cascade.py                             # 4 种场景全覆盖
│   ├── test_bulk_bootstrap_resume.py
│   ├── test_cold_start.py                          # §10 冷启动 SLO 验证
│   └── test_degrade_paths.py                       # §9 DEGRADE-* 降级路径
│
└── .gitignore
