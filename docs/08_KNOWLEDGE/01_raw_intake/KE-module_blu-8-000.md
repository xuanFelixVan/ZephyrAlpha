---
module_id: KE-module_blu-8-000
title: 8. 集成目标
category: module_blueprint
---

# 8. 集成目标

8. 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| Context Engine (MOD-INF-008) | CE→VMS 向量检索 | `context_assembler.py` → `InProcessVectorMemory.search()` | CE build 阶段成功检索 KE 条目 |
| Knowledge Base (MOD-KB-001) | KB→VMS 写入 | KE 入库时同步写入 `knowledge` Collection | KE 入库后 VMS 可检索 |
| Feedback Loop (MOD-INF-010) | FLE→VMS 双向 | 失败模式写入 `lessons`；检索质量反馈读出 | FLE detect 后 VMS 可检索失败模式；FLE 反馈提高检索精度 |
| Orchestrator (MOD-INF-006) | Orc→VMS 写入 | 任务决策写入 `decisions` | Orc 完成 task 后 VMS 可检索决策 |
| SessionManager | Session→VMS 写入 | session 结束时压缩摘要写入 `session_snapshots` | 新 session 冷启动检索到上一 session |
| Audit Trail (MOD-INF-020) | VMS 操作审计 | 每次 VMS 读写写入审计日志 | 审计日志包含 VMS 操作记录 + WriteTrace |

---
