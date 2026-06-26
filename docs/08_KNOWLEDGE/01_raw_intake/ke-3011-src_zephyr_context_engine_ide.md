---
module_id: KE-2911
status: active
title: src/zephyr/context-engine/ide_capabilities.py (experimental 产出)
category: module_blueprint
ttl: permanent
---

# src/zephyr/context-engine/ide_capabilities.py (experimental 产出)

src/zephyr/context-engine/ide_capabilities.py (experimental 产出)

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
