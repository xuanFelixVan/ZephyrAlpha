---
module_id: KE-3879-----safety-level-000
title: 13.3 工具级 safety_level
category: module_blueprint
---

# 13.3 工具级 safety_level

13.3 工具级 safety_level

| Level | 含义 | 控制方式 |
|:---:|------|------|
| L | 低风险——无限制 | 直接执行 |
| M | 中风险——需确认 | 返回确认提示，Agent 再次调用 |
| H | 高风险——需 Owner 审批 | 返回审批请求，Agent 暂停等待 |
