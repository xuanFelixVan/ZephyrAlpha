---
module_id: KE-2827----------001
status: active
title: permission_modes.yaml — 新增文件（横切面D 模式管理）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# permission_modes.yaml — 新增文件（横切面D 模式管理）

permission_modes.yaml — 新增文件（横切面D 模式管理）
permission_modes:
  # ─── 五种权限模式（对标 Claude Code）───
  modes:
    default:
      description: "默认——读自动放行，写auto_guard，删除blocked。日常开发起点"
      l1_behavior: "always_allow(读) + auto_guard(写) + blocked(删)"
      mid_session_toggle: "Shift+Tab 切换"
      ide_indicator: "DEFAULT"

    accept_edits:
      description: "接受编辑——文件修改自动放行，Shell/Bash命令仍需确认"
      l1_behavior: "always_allow(读+写文件) + auto_guard(Shell) + blocked(删)"
      mid_session_toggle: "Shift+Tab 切换"
      ide_indicator: "ACCEPT-EDITS"

    plan:
      description: "规划模式——仅只读操作。禁止一切写/删/Shell。用于代码审查和架构探索"
      l1_behavior: "always_allow(只读) + blocked(写/删/Shell)"
      mid_session_toggle: "Shift+Tab 切换"
      ide_indicator: "PLAN"

    auto:
      description: "自动模式——AI分类器实时判断：这个操作安全吗？安全就放行，不安全就拦"
      l1_behavior: "AI分类器动态判定（对标 Claude Code auto模式）"
      classifier: "DeepSeek轻量级安全分类器（< 50ms）"
      mid_session_toggle: "Shift+Tab 切换"
      ide_indicator: "AUTO"
      # ⚠️ 注意：bypassPermissions 模式在本地开发中不可用——必须沙箱+无网络

    emergency:
      description: "紧急模式——使用D-018-18紧急覆盖令牌临时越权。不是Shift+Tab可选的模式"
      trigger: "Owner签发紧急覆盖令牌 + 确认"
      max_duration_minutes: 5
      ide_indicator: "⚠️ EMERGENCY"

  # ─── 多Profile管理（对标 Codex CLI）───
  profiles:
    active_profile: "default"
    available:
      default:
        mode: "default"
        sandbox: "workspace_write"
        network: "blocked"
        model: "deepseek"

      ci_automation:
        mode: "accept_edits"
        sandbox: "workspace_write"
        network: "github.com,pypi.org"
        model: "deepseek"

      exploration:
        mode: "plan"
        sandbox: "read_only"
        network: "blocked"
        model: "claude"  # 用Claude做架构分析

    profile_switching:
      cli: "zephyr profile set <name>"
      mid_session: "/profile <name>"
      auto_activate: "根据当前Task类型自动切换profile"

  # ─── Mid-Session Toggle（对标 Claude Code Shift+Tab 和 Codex CLI /permissions）───
  mid_session_control:
    commands:
      - "/mode"          # 显示/切换当前权限模式
      - "/permissions"   # 显示当前权限信封详情
      - "/profile"       # 切换配置profile
      - "/audit"         # 显示最近操作决策审计
    keyboard_shortcut: "Shift+Tab（循环切换 default→acceptEdits→plan→auto）"
```

```python
