---
module_id: KE-module_blu-8_8_skill_semantic_version_con-003
title: 8.8 Skill Semantic Version Contract & Breakage Detection
category: module_blueprint
---

# 8.8 Skill Semantic Version Contract & Breakage Detection

8.8 Skill Semantic Version Contract & Breakage Detection

```yaml
skill_semver_contract:
  description: "Skill 的语义版本不仅仅是数字——定义了在什么情况下构成 Breaking Change"

  version_semantics:
    MAJOR_breaking:
      description: "Skill 的 CRITICAL 规则变更或 Checklist 的核心逻辑改变"
      examples:
        - "旧: 使用同步数据库连接 / 新: 使用异步数据库连接"
        - "旧: YAML 配置格式 / 新: TOML 配置格式"
        - "旧: allowed-tools 包含 Write / 新: 移除 Write"
      consequence: "所有依赖此 Skill 的 Trigger 条目必须重新审查"

    MINOR_feature:
      description: "新增 Checklist 步骤、新增 L3 reference、新增领域模式"
      examples:
        - "新增: 部署前跑 ruff format 检查"
        - "新增: references/edge_cases.md"
      consequence: "自动生效——不需要人工审查"

    PATCH_fix:
      description: "修复指令措辞歧义、修复 L3 reference 路径、修正领域知识错误"
      examples:
        - "修正: '跑测试' → '跑 pytest --count=3 --shard=auto'"
        - "修正: 引用路径 './atm.md' → './references/atm_pattern.md'"
      consequence: "自动生效"

  breakage_detection:
    tool: "skill_breakage_checker.py——对比两个版本的 YAML diff → 自动分类 breakage 等级"
    integration: "CI pre-commit hook——如果检测到 MAJOR breaking change → 标记 pull request 为 'needs-human-review'"
```
