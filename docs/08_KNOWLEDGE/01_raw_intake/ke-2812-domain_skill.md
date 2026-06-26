---
module_id: KE-2715
status: active
title: 每个 Domain Skill 的标准目录结构
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 每个 Domain Skill 的标准目录结构

每个 Domain Skill 的标准目录结构
skills/domain/{module}/
  SKILL.md                # 主 Skill 文件（agentskills.io 标准）——L1 metadata + L2 body
  AGENT.md                # Factory Agent——记录"创建时问了哪 3 个问题"（参考用）
  references/             # L3——按需加载的深度参考资料
    patterns.md           # 领域代码模式
    common_bugs.md        # 常见 bug 清单 + 修复策略
    key_files.yaml        # 关键文件索引表
    gate_checklist.md     # 模块专属门禁检查清单
  scripts/                # 可选——Skill 专用的自动化脚本
    validate.sh           # Skill 自体验证脚本（指令是否完整？引用是否有效？）
