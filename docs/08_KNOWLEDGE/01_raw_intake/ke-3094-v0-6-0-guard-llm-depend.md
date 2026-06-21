---
module_id: KE-2993--------llm-depend-000
status: active
title: ── v0.6.0 Guard 升级路径：从 LLM-dependent → LLM-free 的渐进优化 ──
category: module_blueprint
---

# ── v0.6.0 Guard 升级路径：从 LLM-dependent → LLM-free 的渐进优化 ──

── v0.6.0 Guard 升级路径：从 LLM-dependent → LLM-free 的渐进优化 ──
guard_upgrade_path:
  description: "SUPERVISORAGENT (ICLR 2026) LLM-free 原则——在 scaffold 先用 LLM-based 验证逻辑正确性，stable 后逐步替换为 LLM-free 方案降本"
  phases:
    scaffold: "所有 guard 用 LLM-dependent 先验证逻辑——容忍 100% guard 开销"
    experimental: "format_check → regex-based LLM-free（最大降本点）"
    beta: "relevance_check → embedding similarity LLM-free（仅需一次 embedding 计算）"
    stable: "hallucination_check → 仅 10% 采样 + cached validation → LLM-free"
    self_calibrating: "> 80% guard 调用为 LLM-free | guard_efficiency ratio > 10:1"
```
