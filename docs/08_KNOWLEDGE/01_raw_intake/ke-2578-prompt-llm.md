---
module_id: KE-2483-------------llm-003
status: active
title: 8.3 Prompt 模板（结构化——不留给 LLM 判断空间）
category: module_blueprint
---

# 8.3 Prompt 模板（结构化——不留给 LLM 判断空间）

8.3 Prompt 模板（结构化——不留给 LLM 判断空间）

```
你是 ZephyrAlpha 的文档修复助手。你需要将以下结构化修复数据，转换为一段可以直接替换到规则文档中的 Markdown 文本。

修复数据：
  - 问题类型: {issue.trigger_type}  # 只能是: file_disconnection | system_surpassed | structural_gap
  - 目标位置: {issue.rule_location}
  - 当前文本: {issue.current_text}
  - 修复指令: {issue.structured_fix_instruction}

约束：
  1. 输出 ONLY 替换后的 Markdown 段落——不加"修复后："、"建议："等前缀
  2. 不改变原文的语气、格式、编号
  3. 不引入任何原文中没有的实体（文件路径/Gate ID/模块 ID）
  4. 如果修复指令中有"删除"，输出空字符串 ""

输出：
```

---
