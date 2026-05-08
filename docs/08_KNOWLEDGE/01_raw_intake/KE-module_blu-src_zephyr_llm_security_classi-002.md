---
module_id: KE-module_blu-src_zephyr_llm_security_classi-002
title: src/zephyr/llm_security/classifier.py
category: module_blueprint
---

# src/zephyr/llm_security/classifier.py

src/zephyr/llm_security/classifier.py

from enum import Enum

class InputTrustLevel(str, Enum):
    TRUSTED      = "trusted"       # 来自本地 config / ADR / 白名单源
    SEMI_TRUSTED = "semi_trusted"  # 来自项目代码 / 任务卡
    UNTRUSTED    = "untrusted"     # 来自外部文档 / 网页 / 邮件 / 工具返回
    HOSTILE      = "hostile"       # 检测到明显注入模式

INPUT_SOURCE_ROUTING = {
    "system_config":      InputTrustLevel.TRUSTED,
    "task_card":          InputTrustLevel.SEMI_TRUSTED,
    "code_file":          InputTrustLevel.SEMI_TRUSTED,
    "vms_retrieval":      InputTrustLevel.SEMI_TRUSTED,
    "external_url":       InputTrustLevel.UNTRUSTED,
    "email":              InputTrustLevel.UNTRUSTED,
    "mcp_tool_return":    InputTrustLevel.UNTRUSTED,
    "user_chat":          InputTrustLevel.SEMI_TRUSTED,
    "unknown":            InputTrustLevel.UNTRUSTED,   # 默认最严
}
