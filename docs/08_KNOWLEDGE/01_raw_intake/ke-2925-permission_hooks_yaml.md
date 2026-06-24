---
module_id: KE-2825
status: active
title: permission_hooks.yaml — 钩子配置文件
category: module_blueprint
---

# permission_hooks.yaml — 钩子配置文件

permission_hooks.yaml — 钩子配置文件
hooks:
  # ─── Pre-Check Hooks ───
  pre_check:
    - id: "H01"
      name: "file_integrity_checksum"
      applies_to: ["file_write", "file_modify"]
      description: "写文件前记录修改前checksum——用于rollback还原"
      priority: 10
      timeout_ms: 5

    - id: "H02"
      name: "git_status_consistency"
      applies_to: ["file_delete", "file_modify"]
      description: "操作前确认git status无未跟踪变更——防止AI操作与git状态撕裂"
      priority: 20
      timeout_ms: 20

    - id: "H03"
      name: "dependency_version_lock"
      applies_to: ["file_write"]
      context: "target_file == 'pyproject.toml'"
      description: "修改pyproject.toml时检查依赖版本——防止AI意外升级破坏性版本"
      priority: 30
      timeout_ms: 10

  # ─── Post-Check Hooks ───
  post_check:
    - id: "H04"
      name: "downstream_module_notify"
      applies_to: ["permission_config_change"]
      description: "权限配置变更后通知所有依赖模块——§4 depends_on各模块的Gate Engine"
      priority: 50
      timeout_ms: 100

    - id: "H05"
      name: "sensitive_data_scan"
      applies_to: ["file_write", "file_create"]
      description: "文件写入后扫描是否包含PII/credential/API key——比L5更激进"
      priority: 60
      timeout_ms: 50

  # ─── On-Blocked Hooks ───
  on_blocked:
    - id: "H06"
      name: "auto_backup_before_block"
      applies_to: ["any_permission_blocked"]
      description: "越权被拦截时自动备份受影响文件——防止后续毁坏操作丢失恢复路径"
      priority: 100
      timeout_ms: 200

    - id: "H07"
      name: "owner_notification"
      applies_to: ["any_permission_blocked"]
      description: "越权拦截时通知Owner——飞书/钉钉/Slack"
      priority: 110
      timeout_ms: 500

  # ─── On-Kill-Switch Hooks ───
  on_kill_switch:
    - id: "H08"
      name: "system_snapshot_backup"
      applies_to: ["any_kill_switch"]
      description: "熔断时自动备份系统当前完整快照——git bundle + SQLite dump"
      priority: 200
      timeout_ms: 5000

    - id: "H09"
      name: "emergency_owner_alert"
      applies_to: ["any_kill_switch"]
      description: "熔断时紧急通知Owner——所有渠道同时推送（飞书+钉钉+SMS若配置）"
      priority: 210
      timeout_ms: 1000
```

---
