---
module_id: KE-1414
title: 12. 修订记录
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 12. 修订记录

12. 修订记录

| 日期 | 版本 | 说明 |
|------|:-:|------|
| 2026-04-24 | 1.0.0 | 初版（B-a-1 首稿）。基于 Kimi §7.5.2 + Qwen 选型 #4-6。 |
| 2026-04-24 | 1.1.0 | 用户反馈吸收一轮：库化优先 + `.runtime/chromadb/` 锁定 + Collection + multi_search + bulk_bootstrap + update cascade 三场景 + 前置条件/文件清单/P0 测试章节 + 瘦身 "缺口→原因→解法" 三段式。 |
| 2026-04-24 | 1.2.0 | 用户反馈吸收二轮（定稿为 5 份接口的共享模板）：① §1.3 引入 `VectorMemoryProtocol` 抽象基类 + `InProcessVectorMemory` / `RemoteVectorMemory` 双实现；② 所有 API 改为 `async`，锁用 `asyncio.Lock` + `filelock`（严禁 `threading.Lock`）；③ 新增 `sync_document(file_path, event)` 增量同步 API（git hook 主入口）；④ CASCADE 新增 merge 场景（第 4 种）+ `CASCADE_SCENARIOS` 完整表；⑤ multi_search 默认 `merge_strategy="rrf"`（Cormack 2009），weighted 降为高级选项；⑥ §0 新增"本文档不是"；⑦ §9 补 **DEGRADE-001** P0 级降级条款 + 调用方强制契约 + 降级日志；⑧ §10 新增冷启动 SLO（总冷启动 ≤ 10s）；⑨ §11 补 merge / 冷启动 / 降级路径 P0 测试；⑩ `vibe_config.yaml::runtime_root` 支持环境变量覆盖。 |
