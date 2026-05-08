---
module_id: KE-module_blu-4_______ide_mcp_________2026-0-000
title: 遗漏 #4 补充：三家 IDE MCP 兼容矩阵（基于 2026-04 主流版本实测）
category: module_blueprint
---

# 遗漏 #4 补充：三家 IDE MCP 兼容矩阵（基于 2026-04 主流版本实测）

遗漏 #4 补充：三家 IDE MCP 兼容矩阵（基于 2026-04 主流版本实测）
IDE_CAPABILITY_MATRIX: dict[IDEID, dict[IDEChannel, str]] = {
    IDEID.CURSOR: {
        IDEChannel.TOOLS:     "full",       # Cursor 主力通道，AI 主动调用
        IDEChannel.RESOURCES: "read_only",  # 可读但不主动订阅更新
        IDEChannel.PROMPTS:   "full",       # system prompt 注入
        IDEChannel.SAMPLING:  "experimental",
    },
    IDEID.TRAE: {
        IDEChannel.TOOLS:     "partial",    # 支持有限 tool schema
        IDEChannel.RESOURCES: "full",       # Trae 主力通道，强资源感知
        IDEChannel.PROMPTS:   "full",
        IDEChannel.SAMPLING:  "none",
    },
    IDEID.CLAUDE_DESKTOP: {
        IDEChannel.TOOLS:     "full",
        IDEChannel.RESOURCES: "full",
        IDEChannel.PROMPTS:   "full",       # Claude-Desktop 强 prompts
        IDEChannel.SAMPLING:  "full",
    },
    IDEID.GENERIC_MCP: {
        IDEChannel.TOOLS:     "unknown",
        IDEChannel.RESOURCES: "unknown",
        IDEChannel.PROMPTS:   "full",       # 最小公倍数兜底
        IDEChannel.SAMPLING:  "unknown",
    },
}
