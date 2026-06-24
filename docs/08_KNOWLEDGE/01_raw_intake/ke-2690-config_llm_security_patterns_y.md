---
module_id: KE-2593
status: active
title: config/llm_security_patterns.yaml (experimental 产出)
category: module_blueprint
---

# config/llm_security_patterns.yaml (experimental 产出)

config/llm_security_patterns.yaml (experimental 产出)

pattern_profiles:
  default:
    dangerous_commands:
      - "rm -rf /"
      - "del /f /s /q"
      - "format [A-Za-z]:"
      - "shutdown\\s+"
      - "curl\\s+.*\\|\\s*(?:sh|bash|powershell)"
      - "wget\\s+.*\\|\\s*(?:sh|bash)"
      - "Invoke-Expression"
      - "IEX\\s*\\("
    external_urls:
      allow_hosts:
        - "github.com"
        - "pypi.org"
        - "huggingface.co"
      deny_all_others: true
    secret_hints:
      - "sk-[A-Za-z0-9]{32,}"              # OpenAI
      - "AKIA[0-9A-Z]{16}"                 # AWS Access Key
      - "ghp_[A-Za-z0-9]{36}"              # GitHub PAT
      - "xoxb-[A-Za-z0-9-]{50,}"           # Slack
      # 运行时补充：detect-secrets 规则集
    base64_payload_threshold_chars: 500    # 超 500 字符连续 base64 疑似 payload
```

---
