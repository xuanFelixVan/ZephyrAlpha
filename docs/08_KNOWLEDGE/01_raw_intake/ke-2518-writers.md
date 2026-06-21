---
module_id: KE-2423----writers-000
title: 7.1 上游 Writers
category: module_blueprint
---

# 7.1 上游 Writers

7.1 上游 Writers

| 写入方 | 触发 | 目标 Collection | 调用方式 |
|--------|------|----------------|---------|
| git post-commit hook | 每次 commit 的 `.md`/`.py`/`.yaml` | 按 §7.3 路由 | `await vm.sync_document(path, event)` |
| Agent Orchestrator | 任务完成时 | `task_history` | `await vm.ingest(doc)` |
| Session Log writer | 会话结束时 | `lessons` | `await vm.ingest(doc)` |
| Manual CLI（`scripts/vm_ingest.py`） | 首次 bootstrap / 手动导入 | 按 CLI 参数 | `await vm.bulk_bootstrap(docs)` |
