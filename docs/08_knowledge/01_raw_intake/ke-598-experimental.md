---
module_id: KE-538
title: 8A.3 降级矩阵
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 8A.3 降级矩阵

8A.3 降级矩阵

| 服务 | 降级条件 | 降级行为 | 恢复条件 |
|------|---------|---------|---------|
| LSG | **不降级**（fail-closed）| N/A（异常即拒绝调用）| N/A |
| CE | LLM 压缩失败 | 规则基截断 + degraded=True | Qwen2.5-3B 服务恢复 |
| CE | VMS 检索失败 | 降级到 grep/rg 文件检索 | VMS 恢复 |
| VMS | ChromaDB 损坏/首次启动 | `search()` 返回空 + degraded=True | bulk_bootstrap 完成 |
| Orc | SQLite 锁争用 | 任务延迟执行 + 告警 | 锁释放 |
| Orc | Agent 沙箱逃逸 | 立即 kill + IR-SEC-002 | 人工审查 |
| FLE | SQLite 容量满 | 归档旧数据 + 暂停异常检测 | 容量恢复 |
