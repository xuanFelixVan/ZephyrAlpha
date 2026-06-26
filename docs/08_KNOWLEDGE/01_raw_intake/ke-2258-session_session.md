---
module_id: KE-2164---session--------session-005
status: active
title: 3.9.6 跨 Session 异常中断恢复（Session Crash Recovery Protocol）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 3.9.6 跨 Session 异常中断恢复（Session Crash Recovery Protocol）

3.9.6 跨 Session 异常中断恢复（Session Crash Recovery Protocol）

> **盲点#47**：当前 handoff 协议（§3.9.2）假设所有 session 都**正常结束**——`auto-handoff-log.py` 在 session 结束时优雅地生成 handoff package。但在 Windows 桌面环境下，IDE 崩溃、强制关机、蓝屏、终端 OOM kill 四种情况都会导致 session **异常中断**——handoff package 不生成、`next_session_hint` 不写入、下个 session 的 AI 不知道"上一个 session 任务做到哪了"。

```
正常结束流程：
  Session End → auto-handoff-log.py → handoff package 写入
  → next_session_hint 填充 → 下次 session AI 自动读取 → 继续施工

异常中断的情况：
  掉电/IDE崩溃/蓝屏 → 没有 handoff → 下次 session AI 空白启动
  → 不知道上周五下午做了什么 → 从头摸索 → 时间浪费
```

**恢复协议（三步自动诊断 + 一步 Owner 确认）**：

```
Session N+1 启动
    │
    ▼
┌──────────────────────────────────────────────────────┐
│ S1：中断检测（Crash Detector）                          │
│ ───────────────────────────────────────────          │
│ 检测信号：                                              │
│  · 上次 session log 存在但无对应 handoff package        │
│  · kb_state.db → session_handoff 表中 last_handoff    │
│    时间 < last_session_end 时间（缺口 > 0s）             │
│  · next_session_hint = NULL（未正常填写）                │
│                                                      │
│ 若检测到中断 → 进入 S2                                  │
│ 若无中断 → 正常加载 handoff package                     │
└──────────────────────────────────────────────────────┘
    │
    ▼ 检测到中断
┌──────────────────────────────────────────────────────┐
│ S2：中断前状态重建（State Reconstruction）               │
│ ───────────────────────────────────────────          │
│ 1. 读取最后一次完整 session log → 提取 action_blocks   │
│    → 识别最后成功完成的操作（OP-DONE）                   │
│ 2. 扫描 git status → staged/unstaged 变更              │
│    → 推断"正在进行中"的施工                             │
│ 3. 扫描 /tmp/ZephyrAlpha 临时文件 → 中间产物              │
│    → 恢复 AI 输出缓存（如未提交的生成代码）              │
│ 4. 生成 CrashRecoveryReport:                           │
│    · last_known_completed: "重构 KeCategory 枚举"      │
│    · in_progress_estimate: "正在补 §3.9 知识来源清单"    │
│    · dirty_files: ["schemas.py", "blueprint.md"]     │
│    · risk_level: LOW / MEDIUM / HIGH                  │
│                                                      │
│ 保存到 docs/19_development_workspace/session-logs/      │
│   crash-recovery-{session_id}.md                     │
└──────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────┐
│ S3：推送给新 Session AI + Owner                        │
│ ───────────────────────────────────────────          │
│ AI 入场后第一条消息：                                    │
│                                                     │
│ "检测到上次 Session (2026-04-30_session-047) 异常中断。  │
│  已重建中断前状态：                                       │
│  · 已完成：重构 KeCategory 枚举（schemas.py 已保存）       │
│  · 正在进行：补 §3.9 知识来源清单 (blueprint.md 有修改但未提交)│
│  · 风险级别：LOW（无数据丢失风险，未提交变更可恢复）        │
│                                                     │
│  请确认是否从此处继续？[Y/N/指定新起点]"                   │
└──────────────────────────────────────────────────────┘
```

**防丢失的最低健康心跳**：

为缩短"S2 状态重建"的窗口（减少推断依赖），追加一个**3 分钟健康
