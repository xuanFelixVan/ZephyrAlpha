---
module_id: KE-1939---sequence-guard--------005
status: active
title: 2.7 L4 — Sequence Guard 序列护栏（决策 D-018-09，**最关键的盲点补丁**）
category: module_blueprint
---

# 2.7 L4 — Sequence Guard 序列护栏（决策 D-018-09，**最关键的盲点补丁**）

2.7 L4 — Sequence Guard 序列护栏（决策 D-018-09，**最关键的盲点补丁**）

> **决策 D-018-09**：建立会话级操作序列追踪与阻断——单个操作可能合法，但多步组合可能构成攻击链。这是防御 Prompt Injection 和数据外泄的最后一公里。
>
> **决策依据**：D2 四层模型的第3层 Sequence Enforcement。安全研究表明：Agent 攻击不是单步的，而是通过合法操作组成的链条。如 `read_sensitive_data → send_email` 构成数据外泄。

```yaml
sequence_guard:
  # ─── 会话级序列追踪 ───
  tracking:
    scope: "per-session per-agent（每个 Agent 会话独立追踪）"
    window: "最近 20 次操作（滑动窗口）"
    storage: "内存内环形缓冲区（< 1KB per session）"

  # ─── 禁止序列规则 ───
  forbidden_sequences:
    # 数据外泄链
    - name: "prevent_data_exfiltration_via_email"
      sequence: [read_sensitive, send_email]
      reason: "读取敏感数据后发送邮件 = 数据外泄"
      action: BLOCKED

    - name: "prevent_data_exfiltration_via_http"
      sequence: [read_sensitive, http_post_external]
      reason: "读取敏感数据后对外 POST = 数据外泄"
      action: BLOCKED

    - name: "prevent_data_exfiltration_via_file"
      sequence: [read_sensitive, write_to_public_dir]
      reason: "读取敏感数据后写入公开目录 = 侧信道泄漏"
      action: BLOCKED

    # 权限提升链
    - name: "prevent_privilege_escalation"
      sequence: [read_rbac_config, write_rbac_config]
      reason: "读取权限配置后修改 = 提权"
      action: BLOCKED

    # 破坏链
    - name: "prevent_mass_destruction"
      sequence: [list_files, delete_multiple_permanent]
      reason: "扫描文件后批量删除永久文件 = 破坏"
      action: BLOCKED

    # 绕过链
    - name: "prevent_gate_circumvention"
      sequence: [modify_gate_config, bypass_gate_check]
      reason: "修改门禁配置后绕过检查 = 护栏拆除"
      action: BLOCKED

  # ─── 高风险序列（不阻断，但触发热熔断候选）───
  high_risk_sequences:
    - name: "suspicious_config_sweep"
      sequence: [read_multiple_configs, write_multiple_configs]
      reason: "大量读取配置后大量修改 = 可疑"
      action: "记录风险分数，累计触发 L0 Kill Switch"

    - name: "credentials_touch"
      sequence: [read_any, access_credential_store]
      reason: "任何读取后访问凭证库 = 高风险"
      action: "强制 L2 ABAC 重新验证 + 审计告警"

  # ─── 序列冲突解决方案 ───
  sequence_timeout: "同一序列在 300 秒内的两次操作才算序列命中（避免跨会话误报）"
  sequence_bypass: "Owner 可在 audit 中标记合法序列白名单（如正常的 read_config→write_config）"

  # ─── v0.4.0 跨Session关联检测 ───
  cross_session_correlation:
    description: "两个不同Session的Agent可能通过文件系统进行隐式协作来绕过单Session序列护栏"
    detection_rules:
      - name: "cross_session_data_exfiltration"
        condition: "Session-A Agent读取敏感数据 → (5分钟内) Session-B Agent执行网络请求"
        action: "两个Session同时标记为高风险 + 审计告警"
      - name: "cross_session_permission_escalation"
        condition: "Session-A Agent查询权限配置 → (5分钟内) Session-B Agent修改同一配置"
        action: "BLOCKED + 两个Agent同时标记为'疑似合谋'"
    storage: "共享的跨Session操作关联索引（SQLite memory table，保留最近60分钟）"

  # ─── v0.4.0 Agent间隐式通信检测 ───
  inter_agent_communication_detection:
    description: "Agent可以通过文件写入/读取进行隐式通信（Covert Channel）"
    patterns:
      - name: "file_system_covert_channel"
        condition: "Agent A写入非项目文件 → Agent B在1分钟内读取同一文件 → Agent B执行高危操作"
        action: "Agent B的操作降级为 auto_guard + 追溯Agent A的写入意图"
      - name: "shared_memory_covert_channel"
        condition: "两个不同IDE的Agent在同一临时目录高频交替读写"
        acti
