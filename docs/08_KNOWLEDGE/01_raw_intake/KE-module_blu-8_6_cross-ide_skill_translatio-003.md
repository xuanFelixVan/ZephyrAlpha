---
module_id: KE-module_blu-8_6_cross-ide_skill_translatio-003
title: 8.6 Cross-IDE Skill Translation Layer
category: module_blueprint
---

# 8.6 Cross-IDE Skill Translation Layer

8.6 Cross-IDE Skill Translation Layer

```yaml
cross_ide_translation:
  description: "同一 Skill 在不同 IDE 环境中的表现形式——AGENTS.md（通用）vs SKILL.md（原生）vs .cursor/rules（Cursor）vs .roomodes（RooCode）"

  ide_ecosystem_map:
    TRAE:
      format: "AGENTS.md（跨工具通用路由）"
      load_mechanism: "AGENTS.md 触发表 → 引导 AI 读取 SKILL.md"

    Cursor:
      format: ".cursor/rules/{skill_name}.mdc"
      load_mechanism: "Glob-based auto-load（`*.py → database-specialist.mdc`）"
      frontmatter_requirement: "Cursor 需要 `alwaysApply: true/false` frontmatter"
      mapping: "SKILL.md → .cursor/rules/ → glob pattern 配置 → auto-load on matching files"

    RooCode:
      format: ".roomodes（单一 YAML 文件定义所有 mode）"
      load_mechanism: "Custom Mode → 用户手动切换或 role_regex 自动匹配"
      mapping: "Role Skill → RooCode Custom Mode（architect → architect mode）"

    Claude_Code:
      format: "SKILL.md（agentskills.io 标准，原生支持）"
      load_mechanism: "Native Skill Loading——自动发现 + 用户 @-mention 唤醒"
      advantage: "最完整的 Progressive Disclosure 支持"

    Cline:
      format: ".clinerules/{topic}.md"
      load_mechanism: "Per-task rule files——手动指定或 auto-load 配置"

    Windsurf:
      format: ".windsurfrules（全局规则）"
      load_mechanism: "Cascade auto-load——基于上下文自动注入"

  translation_strategy:
    principle: "AGENTS.md as Single Source of Truth → derive IDE-specific files"
    tool: "skill_translator.py——读取 skill_registry.yaml + AGENTS.md → 生成各 IDE 格式"
    generation_rules:
      cursor: "每个 Domain Skill → 一个 .cursor/rules/ 文件 → glob 匹配该模块的代码文件"
      roocode: "3 个 Role Skills → 3 个 .roomodes mode 定义 + role_regex"
      claude: "直接使用 SKILL.md（无需翻译——Claude Code 原生支持 agentskills.io）"
```
