---
module_id: KE-4177
title: 6.5 关键决策建议
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 6.5 关键决策建议

6.5 关键决策建议

| 决策 ID | 建议 | 与现状对比 |
|---------|------|-----------|
| 数据模型 | **git-native + SQLite dump 双轨**：git revert 回滚文件 + 从 JSONL dump 恢复 SQLite。废弃 `rollback_manager.py` 的 DB-only checkpoint 作为独立回滚路径 | 现状：两个独立模型互不知晓 |
| Pre-commit 失败 | **discard changes**（`git checkout -- {files}`），不是 revert。蓝图需新增 discard 流程 | 现状：蓝图只说 revert，代码中有冲突 |
| Auto-rollback 治理 | 按失败信号分类（hard/soft/transient）+ loop detector 防震荡 + agent cooldown 隔离 | 现状：统一 revert，无治理 |
| Partial Rollback | 必须支持 file-glob 级别的选择性回滚——氛围编程的核心体验 | 现状：仅 full revert |
