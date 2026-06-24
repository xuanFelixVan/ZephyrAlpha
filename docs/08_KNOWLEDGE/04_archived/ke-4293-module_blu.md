---
module_id: KE-4134
title: 5.1 前置组件（必须先完成）
category: module_blueprint
---

# 5.1 前置组件（必须先完成）

5.1 前置组件（必须先完成）

| 前置项 | 状态 | 所在任务 |
|-------|:----:|---------|
| `src/zephyr/config/embedding_model_registry.yaml` | ✅ 已存在 | - |
| `src/zephyr/vector-memory/` 包创建 | ⏳ 待建 | experimental T-1-XX |
| BGE-M3 ONNX 模型下载到 `.models/bge-m3/` | ⏳ 待建 | experimental T-1-XX |
| `.runtime/` 目录规范写入 `trae_028_doc_structure_naming.yaml` | ⏳ 待修订 | B-d 阶段（B3/B4） |
| `.gitignore` 追加 `.runtime/` + `.models/` | ⏳ 待追加 | experimental T-1-XX 首步 |
| `vibe_config.yaml::runtime_root` 字段定义 | ⏳ 待修订 | B-d 阶段（B3） |
| KBG-0016 批准 | ⏳ pending | B-e 阶段 |
