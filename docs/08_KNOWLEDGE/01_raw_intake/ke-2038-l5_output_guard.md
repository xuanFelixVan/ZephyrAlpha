---
module_id: KE-1947---output-guard----------003
status: active
title: 2.8 L5 — Output Guard 输出护栏（决策 D-018-10）
category: module_blueprint
---

# 2.8 L5 — Output Guard 输出护栏（决策 D-018-10）

2.8 L5 — Output Guard 输出护栏（决策 D-018-10）

> **决策 D-018-10**：Tool 执行后的输出也需要护栏——防止敏感数据泄漏到日志/Terminal/下游 Tool。
>
> **决策依据**：D2 四层模型的第4层——"Validate & sanitize after execution"。在 Agent 管道中，输出也是下一跳的输入。

```yaml
output_guardrails:
  # ─── 规则类型 ───
  rule_types:
    pii_redaction:
      description: "检测并脱敏输出中的个人身份信息"
      patterns:
        - type: "email"
          pattern: "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}"
          action: "redact → [EMAIL_REDACTED]"
        - type: "chinese_id"
          pattern: "\\d{17}[\\dXx]"
          action: "redact → [ID_REDACTED]"
        - type: "phone"
          pattern: "1[3-9]\\d{9}"
          action: "redact → [PHONE_REDACTED]"

    credential_detection:
      description: "检测输出中的凭证泄漏（复用 GateEngine secrets_detection 模式）"
      patterns:
        - "sk-[A-Za-z0-9]{32,}"
        - "-----BEGIN.*PRIVATE KEY-----"
        - "(?:api[_-]?key|apikey)\\s*[:=]\\s*['\"][A-Za-z0-9_\\-]{16,}['\"]"
      action: "redact → [CREDENTIAL_REDACTED] + P0 安全告警"

    size_truncation:
      description: "输出大小截断——防日志/终端轰炸"
      rules:
        - tool: "file_read"
          max_output_bytes: 51200  # 50KB
        - tool: "run_command"
          max_output_bytes: 102400  # 100KB
        - default:
          max_output_bytes: 65536  # 64KB 全局默认
      action: "truncate + 附加元数据 {truncated: true, original_size: N}"

    diff_summary:
      description: "文件变更时生成差异摘要——帮助 L6 行为异常检测"
      applies_to: ["file_write", "file_edit", "apply_patch"]
      output_format: "{lines_added: N, lines_removed: M, files_touched: K}"
```

---
