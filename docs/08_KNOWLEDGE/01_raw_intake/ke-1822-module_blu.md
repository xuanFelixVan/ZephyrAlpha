---
module_id: KE-1731
status: active
title: 2.17 非文件操作升级规则
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.17 非文件操作升级规则

2.17 非文件操作升级规则

> **对标**：MMNTM Agent Attack Surface——操作不限于文件IO + 中国信通院行为护栏工具调用风险。

```yaml
non_file_operation_rules:
  # ===== 网络操作规则 =====
  - id: "ESC-NET-001"
    priority: 5
    condition: "Agent 发起外部网络请求（HTTP/HTTPS/web socket）"
    escalate_to: "auto_guard"
    guard_checks: ["url_safety_check", "volume_anomaly_detection"]
    reason: "防止数据外泄"

  - id: "ESC-NET-002"
    priority: 6
    condition: "Agent 向外部发送超过 1KB 的数据"
    escalate_to: "auto_guard + 自动截断"
    reason: "防止大块数据外泄"

  # ===== Git 操作规则 =====
  - id: "ESC-GIT-001"
    priority: 7
    condition: "执行 git push --force / git push --force-with-lease 到 main/master 分支"
    escalate_to: "blocked"
    reason: "不可逆远程操作"

  - id: "ESC-GIT-002"
    priority: 8
    condition: "执行 git push 到任意远程分支"
    escalate_to: "auto_guard"
    guard_checks: ["branch_protection_check"]

  # ===== CI/CD 操作规则 =====
  - id: "ESC-CI-001"
    priority: 9
    condition: "触发 CI/CD pipeline / GitHub Actions workflow"
    escalate_to: "auto_guard"
    guard_checks: ["pipeline_safety_check"]

  # ===== MCP 工具调用规则 =====
  - id: "ESC-MCP-001"
    priority: 10
    condition: "调用外部 MCP tool（非本项目定义的tool）"
    escalate_to: "auto_guard"
    guard_checks: ["tool_origin_verification", "capability_boundary_check"]

  - id: "ESC-MCP-002"
    priority: 11
    condition: "MCP tool 调用涉及文件系统写入（write_file/delete_file）"
    escalate_to: "已有文件规则覆盖——按对应 ESC-001~003 处理"

  # ===== 数据库操作规则 =====
  - id: "ESC-DB-001"
    priority: 12
    condition: "直接执行 SQL / 修改数据库记录"
    escalate_to: "auto_guard"
    guard_checks: ["sql_safety_analysis"]

  - id: "ESC-DB-002"
    priority: 13
    condition: "DROP TABLE / DELETE FROM（不筛选的删除）"
    escalate_to: "blocked"
    reason: "不可逆数据库操作"
```

---
