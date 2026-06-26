---
module_id: KE-004
status: active
title: 5.1 Vibe Coding AI 的认知特征
category: agent_instruction
ttl: permanent
---

# 5.1 Vibe Coding AI 的认知特征

5.1 Vibe Coding AI 的认知特征

本项目 **100% 采用 Vibe Coding AI** 进行开发。Vibe Coding AI 的核心特征是**上下文记忆极短**——类似于一个不断快速入职又离职的员工：每次新 session 来临，AI 对它不在这段上下文窗口中的一切毫无记忆。

这意味着项目中的所有文件、路径、规则、代码、命名，必须满足一个**零记忆重启标准**（Zero-Memory Restart Standard）：任何一个全新的 AI session，仅凭读取当前项目文件，就能在无外部提示的情况下准确理解项目结构并开始正确施工。

- **原则 1：二元化**（Binary-Safe）——没有"大概"、"应该"。每个定义是精确的枚举值或条件。受控词表必须完整列出合法值，不存在"等等"或"类似"
- **原则 2：责任唯一**（Single Responsibility）——同一概念只在一个文件中定义。禁止"A 文件说 X=3，B 文件说 X=5"
- **原则 3：路径不可漂移**（Path-Drift-Immune）——所有文件引用用绝对路径。禁止"在上级目录中"或"和 X 同级"的相对描述
- **原则 4：引用链不断裂**（Reference Chain Anti-Fragile）——`depends_on` 构成有向无环图。禁止"此文件已废弃，请参见 Y"的占位跳转
- **通俗解释**：AI 每次进来都是"新员工"。每个文件必须做到——读完这个文件，就像读完了整个项目。没有需要"之前知道"的东西。
- **会话交接约定**（Session Handoff）：AI session 结束时应在 Session Log 中留下交接工单——"刚做了什么 + 为什么这样做 + 下一步该做什么"。下一个 AI session 的入职顺序：读本文件 → 读最新 Session Log → 按其中"必读文件"清单继续。
