---
module_id: KE-module_blu-session-000
title: 追加到 session 运行时
category: module_blueprint
---

# 追加到 session 运行时

追加到 session 运行时
def heartbeat():
    """
    每 3 分钟写入一次 (仅 1 行 JSON，≈ 200 字节)：
    {
      "session_id": "2026-05-02_session-047",
      "last_heartbeat": "2026-05-02T16:00:00+08:00",
      "active_op": "Writing §3.9.6",
      "dirty_files": ["blueprint.md"]
    }
    → 写入 docs/19_development_workspace/session-logs/.heartbeat
    → 正常结束时删除此文件
    → 若残留 → 新 session 启动时 S2 直接读取 → 0 推断、100% 精确
    """
    ...
```

> **对标**：Visual Studio Code 的 "Restore Project State"（窗口崩溃后自动打开上次文件和光标位置）/ JetBrains IDE 的 "Local History"（未保存文件的变更日志）/ PostgreSQL WAL (Write-Ahead Log)——预写日志确保崩溃后能回放到最后一个已提交状态。三者都是同一思想：**crash is inevitable; the cost of recovery depends on how much state was persisted before the crash**。
> **大白话**：电脑蓝屏了、VSCode崩了、甚至踢了电源线——这些在1人开发中稀松平常。当前蓝图假设 session 总是优雅结束——但现实是蓝屏那一刻，handoff package 根本没生成。下周一你打开电脑、启动 AI，"它"完全不记得上周五做了什么。这个协议就是让 AI 在每次启动时先问一句："上次是不是崩了？我把你做到哪了重新找出来了——你确认一下咱们继续？"

---
