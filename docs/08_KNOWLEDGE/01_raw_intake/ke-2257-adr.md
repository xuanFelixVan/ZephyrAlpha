---
module_id: KE-2163---------------adr-006
status: active
title: 3.9.5 决策记录的三层模型（取代旧 ADR 体系）
category: module_blueprint
---

# 3.9.5 决策记录的三层模型（取代旧 ADR 体系）

3.9.5 决策记录的三层模型（取代旧 ADR 体系）

**背景**：ADR 体系已于 2026-04-27 裁定废弃（R72）。传统 ADR 假设"有人写 8 节模板 → 团队 Review → 永不过期"，但在 100% AI 开发的氛围编程下，这个假设不成立——决策在聊天中发生，不需要"有人写"。

**对标氛围编程社区**（8 个社区调研，2026-05）：

| 社区 | 做法 | 一行代码承载量 |
|------|------|:---:|
| Claude Code 官方 | CLAUDE.md `## Previous Decisions` — 每决策一行 | ≤1 行 |
| Steve Yegge (CHOP) | AI 在聊天中当场记录决策 → 追加到 CLAUDE.md | ≤1 行 |
| vertu.com (2026) | `decisions.log` — AI 自己写："I chose X over Y because..." | ≤1 行 |
| Cursor Rule Framework | `architecture.mdc` 自动更新内置决策 | ≤3 行 |
| 7/8 社区结论 | **不用传统 ADR。一句话决策贴进上下文文件。** | ≤200 字 |

**ZephyrAlpha 的三层决策记录模型**：

```
决策发生（聊天中）
      │
      ▼ AI 自动检测决策信号（关键字："决定了""选择一个""最终方案"）
      │
      ▼ 自动提取一句结论（≤200 字）
"选 ruff 不用 pylint：快 10-100x（Rust vs Python）+ pyproject.toml 原生集成"
      │
      ▼ 分流判定
 ┌──────────────────┬──────────────────────────┐
 │ L2：一行决策       │ L3：深度决策（KE）         │
 │ （绝大多数场景）     │ （需要对比表/冲突检测时）    │
 │                  │                          │
 │ 条件：            │ 条件：                    │
 │ · 无对比表需求      │ · 需要对比表/数据支撑       │
 │ · 未来不会反复争论   │ · 可能被后续 AI 重新论证     │
 │ · ≤200 字说得清    │ · 涉及架构不变核心          │
 │                  │                          │
 │ → AGENTS.md       │ → KE（A2）G1-G5 完整流程   │
 │   §10 历史决策      │   含对比表 + 结论 + 反模式   │
 │   每次决策追加一行   │   recall() 可语义检索      │
 └──────────────────┴──────────────────────────┘
```

**三层完整视图**：

| 层 | 载体 | 内容 | 粒度 | 示例 |
|:---:|------|------|------|------|
| L1 | AGENTS.md §5 Owner 画像（Track C） | Owner 反复表达的偏好/审美/决策启发式 | 30d TTL，弱信号 | "Owner 偏好短函数 ≤30 行" |
| L2 | AGENTS.md §10 历史决策 | 技术选型/工具对比的最终结论 | ≤200 字，一句话 | "选 SQLite 不用 PostgreSQL：零运维成本 > 并发需求" |
| L3 | KE（A2 architecture_decision） | 需要对比表/数据支撑的重大决策 | 5 段落 + 对比表 | KBG-0031 → KE-042（ChromaDB 选型） |

**旧 ADR 迁移方案**：

```
36 份旧 ADR (docs/02_enterprise_architecture/adr/)
      │
      ▼ 首次运行 adr_migrate.py（beta 单次执行）
      │
每份 ADR → 提取一句结论 + category + priority
      │
      ▼ 分流
 ┌──────────────────┬──────────────────────┐
 │ ≤200 字结论        │ 含对比表/多方案论证       │
 │ （大部分 ADR）      │ （如 KBG-0031 ChromaDB）│
 │                  │                      │
 │ → AGENTS.md §10   │ → KE（A2）            │
 │   原文件归档        │   G1-G5 完整流程        │
 │   docs/_archive/   │                       │
 │   old_adr/         │                       │
 └──────────────────┴──────────────────────┘
```

> **专业参考**：Claude Code 官方 CLAUDE.md 规范 §3 Historical Context——"每次重要决策后 AI 自动追加一行" / vertu.com 2026——"decisions.log：'I chose Library X because smaller bundle size'" / Cursor Rule Framework——"architecture.mdc auto-updated with decision logs"

---
