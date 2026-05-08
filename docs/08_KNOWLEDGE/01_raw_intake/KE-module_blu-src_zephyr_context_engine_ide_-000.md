---
module_id: KE-module_blu-src_zephyr_context_engine_ide_-000
title: src/zephyr/context_engine/ide_capabilities.py (experimental 产出)
category: module_blueprint
---

# src/zephyr/context_engine/ide_capabilities.py (experimental 产出)

src/zephyr/context_engine/ide_capabilities.py (experimental 产出)

from enum import Enum

class IDEChannel(str, Enum):
    TOOLS = "tools"
    RESOURCES = "resources"
    PROMPTS = "prompts"
    SAMPLING = "sampling"

class IDEID(str, Enum):
    CURSOR = "cursor"
    TRAE = "trae"
    CLAUDE_DESKTOP = "claude_desktop"
    GENERIC_MCP = "generic_mcp"
