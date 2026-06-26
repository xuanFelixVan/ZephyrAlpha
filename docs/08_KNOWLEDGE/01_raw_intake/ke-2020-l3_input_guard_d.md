---
module_id: KE-1929---input-guard---------d-003
status: active
title: 2.6 L3 — Input Guard 参数护栏（决策 D-018-08）
category: module_blueprint
ttl: permanent
---

# 2.6 L3 — Input Guard 参数护栏（决策 D-018-08）

2.6 L3 — Input Guard 参数护栏（决策 D-018-08）

> **决策 D-018-08**：在 Tool 调用参数级别增加护栏——同一 Tool 的不同参数应有不同权限。操作对象路径白名单 + 参数值范围限制 + 危险模式检测。
>
> **决策依据**：D2 四层模型的第2层——"Validate arguments before execution"。权限颗粒度从 Tool 级细化到参数级。

```yaml
input_guardrails:
  # ─── 规则类型 ───
  rule_types:
    schema_validation:
      description: "参数类型/结构校验"
      example: |
        tool: "file_write"
        guardrails:
          input:
            - field: "file_path"
              not_matches: "src/zephyr/agent-rbac/"
            - field: "content"
              max_bytes: 1048576  # 1MB 上限

    range_constraint:
      description: "参数值范围限制"
      example: |
        tool: "run_command"
        guardrails:
          input:
            - field: "timeout"
              min: 1
              max: 300  # 最多 5 分钟
            - field: "cmd"
              maxLength: 2000

    pattern_detection:
      description: "危险模式检测——在参数进入 Tool 前拦截"
      example: |
        tool: "database_query"
        guardrails:
          input:
            - field: "query"
              not_contains: ["DROP TABLE", "DROP DATABASE", "TRUNCATE"]
              not_matches: "(?i)delete\\s+from\\s+users"
            - field: "query"
              maxLength: 4000

    path_scope:
      description: "操作对象路径白名单/黑名单"
      example: |
        tool: "file_delete"
        guardrails:
          input:
            - field: "path"
              not_matches: "docs/01_policies_and_standards/"
              not_matches: "src/zephyr/agent-rbac/"
              not_matches: "\\.git/"

    # ─── v0.4.0 新增规则类型 ───
    package_install_guard:
      description: "第三方包安装的白名单管控——pip/npm install 的包名必须在允许列表中"
      example: |
        tool: "run_command"
        guardrails:
          input:
            - field: "cmd"
              if_matches: "(pip|pip3|python -m pip)\\s+install"
              allowed_packages: ["pytest", "ruff", "black", "mypy", "libcst", "pyyaml"]
              blocked_packages: ["*"]  # 不在白名单的一律blocked
            - field: "cmd"
              if_matches: "npm\\s+install"
              allowed_packages: ["prettier", "eslint"]
              blocked_packages: ["*"]

    network_target_guard:
      description: "Agent工具调用的网络目标URL白名单/黑名单"
      example: |
        tool: "web_fetch"
        guardrails:
          input:
            - field: "url"
              allowed_domains: ["github.com", "pypi.org", "docs.python.org"]
              blocked_domains: ["pastebin.com", "termbin.com", "*.ngrok.io"]
        tool: "run_command"
        guardrails:
          input:
            - field: "cmd"
              if_matches: "(curl|wget|Invoke-WebRequest)"
              allowed_domains: ["github.com", "pypi.org"]

    env_variable_guard:
      description: "环境变量操作的保护——修改.env或set环境变量需要auto_guard起"
      example: |
        tool: "file_write"
        guardrails:
          input:
            - field: "file_path"
              if_matches: "\\.env"
              force_auto_guard: true  # 即使L1判为always_allow也升级为auto_guard

  # ─── L3 判定逻辑 ───
  enfor
