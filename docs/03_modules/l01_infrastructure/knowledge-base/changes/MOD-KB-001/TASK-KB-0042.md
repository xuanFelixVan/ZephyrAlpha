---
task_id: "TASK-KB-0042"
source_blueprint: "MOD-KB-001"
source_section: "§4.0 数据引擎物理布局——data/ 目录 + db_config.yaml + .gitignore 三级策略 + 12-Factor 环境变量"

title: "data/ 数据引擎目录与配置文件实现——db_config.yaml + .gitignore L1/L2/L3三级策略 + KB_DATA_DIR 环境变量驱动"
description: |
  实现蓝图 §4.0 定义的数据引擎独立于 Markdown 文档的物理布局：
  (1) 创建 `config/db_config.yaml`——`kb.data_root: ${KB_DATA_DIR:-data/}` + `kb.sqlite.db_path: ${KB_SQLITE_PATH:-data/sqlite/kb_state.db}` + `kb.chroma.persist_dir: ${KB_CHROMA_DIR:-data/chroma/}` + `kb.cache.reranker_model: ${KB_RERANKER_DIR:-data/cache/bge-reranker-v2-m3/}`——对标 12-Factor App §III Config，所有路径环境变量覆盖+默认 fallback；
  (2) `.gitignore` 三级策略实现——L1 追踪 `data/.gitkeep`（✅ Git）+ L2 `data/sqlite/kb_state.db`（⚠️ 可选 需Owner显式 `git add -f`）+ L3 `data/chroma/** data/cache/** 生产 *.db`（❌ Git 不入库）；
  (3) 验证 `data/sqlite/` `data/chroma/` `data/cache/` 三个物理目录存在（若不存在则 `mkdir -Force` 创建，并 `data/.gitkeep`）——且 Windows 环境下 相对路径自动→ abs path `CWD/data/` = `D:/ZephyrAlpha/data/`；
  (4) 三环境验证——开发Windows本地→`KB_DATA_DIR` 不设置=fallback `data/`；CI→若有CI env `KB_DATA_DIR`=目录；生产 Linux→`/mnt/ssd/zephyr_data/`。
  本操作确保 data/ 目录结构与环境变量+代码的边界清晰——代码不假设路径，环境变量不做硬编码。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
  - "D:\\ZephyrAlpha\\.gitignore"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\chromadb_init.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\config\\db_config.yaml"
    description: "新建——KB 数据库路径配置 YAML——${KB_DATA_DIR:-data/} 四条目 env variable + default"
  - path: "D:\\ZephyrAlpha\\.gitignore"
    description: "追加 §4.0 L1/L2/L3 三级 .gitignore 规则——data/.gitkeep ✅ data/chroma/ ❌ data/cache/  ❌"
  - path: "D:\\ZephyrAlpha\\data\\sqlite\\.gitkeep"
    description: "新建——保证 data/sqlite 目录在 Git 中可追踪"
  - path: "D:\\ZephyrAlpha\\data\\chroma\\.gitkeep"
    description: "新建"
  - path: "D:\\ZephyrAlpha\\data\\cache\\.gitkeep"
    description: "新建"

allowed_touch:
  - "D:\\ZephyrAlpha\\config\\db_config.yaml"
  - "D:\\ZephyrAlpha\\.gitignore"
  - "D:\\ZephyrAlpha\\data\\.gitkeep"
  - "D:\\ZephyrAlpha\\data\\sqlite\\.gitkeep"
  - "D:\\ZephyrAlpha\\data\\chroma\\.gitkeep"
  - "D:\\ZephyrAlpha\\data\\cache\\.gitkeep"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\**\\*.py"

applicable_rules:
  - module_id: "12-Factor App §III"
    section: "Config"
    reason: "环境变量驱动路径——不在代码中硬编码路径"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径合规"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
    reason: "§4.0 定义了完整 data/ 目录+db_config.yaml+.gitignore 三级策略"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 5000
timeout_minutes: 20

acceptance_criteria:
  - "config/db_config.yaml 存在——包含 kb.data_root/kb.sqlite.db_path/kb.chroma.persist_dir/kb.cache.reranker_model 四条"
  - "data/sqlite/chroma/cache 三个目录存在且各自包含 .gitkeep"
  - ".gitignore 追加 data/sqlite/*.db / data/chroma/** / data/cache/** （!保留 .gitkeep）"
  - "环境变量未设置时 chromadb_init.py 使用 db_config.yaml 的 default 路径启动——与硬编码相同"

rollback_instructions: |
  1. 删除 config/db_config.yaml
  2. git checkout -- .gitignore
  3. 删除 data/sqlite/.gitkeep data/chroma/.gitkeep data/cache/.gitkeep
  4. 若 data/ 根下创建了运行时文件→ restore from last-backup

depends_on: ["TASK-KB-0009"]
blocked_by: []
status: "created"
tags_fn:
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-KB-001"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---
