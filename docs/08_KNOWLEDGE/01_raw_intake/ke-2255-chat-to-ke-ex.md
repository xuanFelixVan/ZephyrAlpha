---
module_id: KE-2161------------chat-to-ke-ex-004
status: active
title: 3.9.3 聊天记录→知识提取器（Chat-to-KE Extractor）
category: module_blueprint
---

# 3.9.3 聊天记录→知识提取器（Chat-to-KE Extractor）

3.9.3 聊天记录→知识提取器（Chat-to-KE Extractor）

**问题**：聊天（如本 session 的对话）是最大量、最高频的知识入口——一条 2000 行的聊天记录包含 15-30 个可提取的知识片段，但也混有大量上下文垃圾（"嗯""好的""继续"）。需要**自动拆分 + 自动分类 + 噪音过滤**。

**对标**：[vibe-coding-mcp](https://github.com/MUSE-CODE-SPACE/vibe-coding-mcp)（MUSE-CODE-SPACE，2025-12，v2.12.1）——提供 `muse_collect_code_context`（对话收集）+ `muse_summarize_design_decisions`（决策提取）+ `muse_auto_tag`（自动分类）+ `muse_create_session_log`（归档 Markdown）。Vasilopoulos session tracing："every session perpetually captured + auto-extracted"。

**三段式提取器架构**：

```
聊天记录（原始 Markdown）
    │
    ▼
┌──────────────────────────────────────────────────────┐
│ S1：语义分段器（Semantic Chunker）                      │
│ ───────────────────────────────────────────          │
│ 按话题转换切分——不按固定行数、不按固定时间               │
│                                                      │
│ 信号1：Markdown H2/H3 标题 ──→ 自然段落边界             │
│ 信号2：相邻段向量余弦相似度 < 0.3 ──→ 话题转换点         │
│ 信号3：总结/决策关键词 ("结论""所以""决定了""最终")       │
│                                                      │
│ 单条 2000 行 chat → 15-30 个"对话片段"（segment）       │
└──────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────┐
│ S2：三元判定器（Tri-Categorizer）                       │
│ ───────────────────────────────────────────          │
│ 每个 segment 判定为三类之一                             │
│                                                      │
│ 🟢 知识信号（declaration / decision / rule）           │
│    · 含 "决定了" / "CSS原则" / "规则" / "数据"           │
│    · 含对比表 / 专业参考 / 追问到底根因                   │
│    · Owner 明确说 "把这个加进去" / "按这个来"             │
│                                                      │
│ 🟡 上下文垃圾（banter / 重复 / 死路）                   │
│    · ≤50 tokens 的短响应                                │
│    · 和上一条向量余弦相似度 > 0.9（重复）                 │
│    · 纯提问（还没得到答案）→ 等答案出来再判定             │
│                                                      │
│ 🔵 半信号（refinement / 追问 / 澄清）                    │
│    · "还有一个问题" "继续说" "细化一下"                   │
│    · 合并到关联的 🟢 片段（作为补充 material）            │
│    · 如果 3 轮后还没关联到 🟢 → 丢弃                     │
└──────────────────────────────────────────────────────┘
    │
    ▼
🟢 知识信号 → G1 Ingest → G2 Triage → HIGH→KE / MID→KO
🟡 上下文垃圾 → 丢弃（不入库，留在 Session Log 原位置）
🔵 半信号 → 合并（追加到关联 🟢 片段的 body 末尾）
```

**噪音控制的四道硬门槛**：

| # | 机制 | 门槛值 | 作用 |
|:--:|------|--------|------|
| N-01 | 单片段最低长度 | ≥ 100 tokens | 过滤"好的""继续"等空响应 |
| N-02 | 知识信号评分 | G2 Triage ≥ 0.6 | 半信号自动过滤 |
| N-03 | 同 session 内去重 | 向量余弦相似度 > 0.9 → 合并 | 同一结论重复说只产 1 条 KE |
| N-04 | 日入库上限 | ≤ 30 条新 KO/天 | 防止密集讨论淹没知识库 |

**自动触发时机**：

| 触发事件 | 触发方式 | 提取范围 |
|---------|---------|---------|
| Session 结束（IDE 关闭 / 显式 `end session`） | post-commit hook → `auto-handoff-log.py` | 本 session 全部聊天 → 提取 🟢 片段 → G1 |
| 聊天中 Owner 说"把这个记下来" | 实时触发器 → 当前上下文 5 轮对话 → 直接 KE | Owner 手动标定片段 → 跳 KO → 直达 KE |
| 日终 22:00（如当天有聊天但未提取） | APScheduler cron → `extract_daily_chat.py` | 当天全部未提取片段 → 批量 G1 |

> **核心原则**：聊天是原料——不能全存（噪音太多）、不能全删（知识会丢）。必须拆→判→存。对标 vibe-coding
