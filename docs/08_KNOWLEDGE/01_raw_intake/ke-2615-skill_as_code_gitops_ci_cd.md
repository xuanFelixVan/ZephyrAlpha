---
module_id: KE-2520
status: active
title: 9.3 Skill-as-Code GitOps CI/CD Pipeline
category: module_blueprint
ttl: permanent
---

# 9.3 Skill-as-Code GitOps CI/CD Pipeline

9.3 Skill-as-Code GitOps CI/CD Pipeline

```yaml
skill_gitops:
  description: "Skills 的 GitOps 交付管线——对标 Shaped.ai 的 YAML spec in Git → PR review → CI/CD deploy → agent auto-reconcile"

  pipeline:
    phase_1_proposal:
      description: "Skill 变更提案——通过 PR 提交"
      required_reviewers: "1 human (Owner) + automated CI checks"
      ci_checks:
        - "skill_schema_validator.py（YAML frontmatter 格式校验）"
        - "skill_breakage_checker.py（MAJOR/MINOR/PATCH 自动分类 + 标记 'needs-human-review'）"
        - "L1 Instruction Validity（静态正确性检查）"
        - "Cross-reference validation（所有 L3 references 文件存在）"

    phase_2_review:
      description: "人工审查 + 沙箱验证"
      human_focus:
        - "Skill 指令是否清晰无歧义？"
        - "Deprecation 迁移路径是否合理？"
        - "allowed-tools 是否最小权限？"
      sandbox_test:
        - "隔离环境中加载 Skill + L2 轨迹测试（per-Skill test scenarios）"
        - "门禁预评估（G0-G7 虚拟执行）"

    phase_3_deploy:
      description: "合并到 main 分支 → 自动部署"
      deployment:
        environment: "dev → canary → stable（遵循 §8.4 Canary 协议）"
        rollback: "自动——部署后 gate_pass_rate 下降 ≥ 5% 即 git revert"

    phase_4_reconcile:
      description: "Agent 自动检测 Skill 版本 → 使用最新 stable 版本"
      version_resolution: "AGENTS.md 触发表引用 skill-registry.yaml → 从 registry 解析 latest stable → 加载"

  git_structure:
    description: "Skills 在 Git 仓库中的结构"
    layout: |
      .agskills/                        # GitOps 管理的 Skills 根目录
        registry.yaml                   # 技能注册表
        domain/
          database/SKILL.md
          mcp-server/SKILL.md
          context-engine/SKILL.md
          ...
        role/
          architect/SKILL.md
          implementer/SKILL.md
          governor/SKILL.md

  disaster_recovery:
    backup_verification: "CI 每日任务：验证 .agskills/ 的完整性（哈希校验 + 文件计数 = registry 一致）"
    restore_procedure: "git checkout last-known-good → CI 自动验证 → Agent 重新加载"
    corruption_detection: "SkillLoader 在加载前验证 SKILL.md 的 SHA256 → 与 registry 中记录的 hash 对比 → 不匹配则拒绝加载 + ANOMALY 事件"
```
