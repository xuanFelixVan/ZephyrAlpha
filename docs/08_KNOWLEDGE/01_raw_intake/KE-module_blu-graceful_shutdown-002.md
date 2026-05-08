---
module_id: KE-module_blu-graceful_shutdown-002
title: Graceful Shutdown 设计 🆕
category: module_blueprint
---

# Graceful Shutdown 设计 🆕

Graceful Shutdown 设计 🆕

> **B66 修复**——v0.8.0 新增。`shutdown()` 必须在系统停止前执行：flush 所有 ring buffer 中的 MetricPoint/LogEntry/Span → 写入 SQLite/JSONL → 关闭 DB 连接。不执行 flush = 缓冲区中的遥测数据静默丢失（系统"不可观测的最后一秒"）。

```
shutdown() 流程:
  1. 冻结入站: 停止接受新的 MetricPoint/Log/Span（返回 SHUTTING_DOWN 错误码）
  2. Flush metrics ring buffer → SQLite（超时 30s）
  3. Flush logs ring buffer → JSONL（超时 10s）
  4. Flush traces in-memory spans → JSONL（超时 10s）
  5. 等待所有正在进行的 write 操作完成（超时 5s）
  6. 关闭 SQLite 连接
  7. 关闭所有 JSONL file handles
  8. 从 LifecycleManager 注销
  9. 写入 shutdown audit event

  shutdown 超时策略:
    - 总超时 60s（不阻塞进程退出）
    - 强制退出前最后一次尝试: 将剩余 buffer 写入 emergency_shutdown.jsonl
    - 下次启动时自动加载 emergency_shutdown.jsonl → 正常路径处理
  
  应急丢失检测:
    启动时检测上次是否正常 shutdown（检查 shutdown audit event 是否存在）
    → 缺失 → P2 "上次关闭异常，可能有遥测数据丢失"
    → 自动评估丢失量: ring_buffer_size - successfully_flushed_on_shutdown
```
