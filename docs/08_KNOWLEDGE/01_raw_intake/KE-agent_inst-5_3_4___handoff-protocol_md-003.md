---
module_id: KE-agent_inst-5_3_4___handoff-protocol_md-003
title: 5.3.4 与 handoff-protocol.md 的关系
category: agent_instruction
---

# 5.3.4 与 handoff-protocol.md 的关系

5.3.4 与 handoff-protocol.md 的关系

本 §5.3 是 `handoff-protocol.md` 的**自动化实现**——`handoff-protocol.md` 定义协议规范（8必填字段），`session_continuity.py` 提供自动执行的代码。两者互补非重复：
- `handoff-protocol.md` → 告诉 AI **"交接包里应该有什么"**
- `session_continuity.py` → 告诉 AI **"怎么自动生成交接包"**
- 本 §5.3 → 告诉 AI **"什么时候该调用它"**
