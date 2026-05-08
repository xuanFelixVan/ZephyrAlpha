---
module_id: KE-module_blu-7_____________placeholder-003
title: 7. 文件清单与落位（不留 placeholder）
category: module_blueprint
---

# 7. 文件清单与落位（不留 placeholder）

7. 文件清单与落位（不留 placeholder）

```

├── src/zephyr/
│   ├── llm_security/                               # ⏳ experimental 新建
│   │   ├── __init__.py                             # 导出 get_lsg()
│   │   ├── protocol.py                             # LLMSecurityGatewayProtocol
│   │   ├── in_process.py                           # experimental 实现
│   │   ├── remote.py                               # beta+ 占位
│   │   ├── schemas.py                              # InputPayload / OutputPayload / Verdict ...
│   │   ├── layers/
│   │   │   ├── l1_classifier.py                    # InputClassifier + HOSTILE_PATTERNS
│   │   │   ├── l2_isolator.py                      # System Prompt 隔离格式
│   │   │   ├── l3_schema_validator.py              # Pydantic 注册 + 校验
│   │   │   └── l4_pattern_inspector.py             # 命令/URL/secret/base64
│   │   ├── secret_scanner.py                       # detect-secrets 封装
│   │   ├── strictness_manager.py                   # bump/ttl/回滚
│   │   ├── audit_log.py                            # 结构化审计日志
│   │   ├── registry.py                             # schema 注册中心
│   │   └── config.py
│   └── config/
│       ├── llm_security.yaml                       # 主配置
│       └── llm_security_patterns.yaml              # 可热加载规则库
│
├── .runtime/
│   ├── llm_security/
│   │   ├── strictness_state.json                   # 动态严格度快照
│   │   └── quarantine/                             # 被隔离 correlation_id 的内容存档
│   └── logs/
│       ├── lsg_audit.log                           # 所有 validate_* 决策（必留档，SIEM 友好）
│       ├── lsg_degrade.log
│       └── lsg_bypass_evidence.log                 # bypass 证据链（红队复盘）
│
├── tests/unit/llm_security/
│   ├── test_l1_classifier.py
│   ├── test_l2_isolator.py
│   ├── test_l3_schema_validation.py
│   ├── test_l4_pattern_inspector.py
│   ├── test_secret_scanner.py
│   ├── test_strictness_manager.py
│   ├── test_cold_start.py
│   └── test_fail_closed_behavior.py                # 关键：降级测试
├── tests/redteam/llm_security/                     # ⏳ 红队用例（独立目录）
│   ├── injection_corpus/                           # 对抗样本集
│   ├── test_prompt_injection.py
│   ├── test_secret_leak.py
│   ├── test_bypass_attempts.py
│   └── test_owasp_alignment.py                     # OWASP Top 10 验证
│
├── .pre-commit-config.yaml                         # 追加 git-secrets / detect-secrets / pip-audit hooks
└── .gitignore                                      # 已追加 .runtime/ + .models/（注意 quarantine/ 入 git 时被 .gitignore 排除）
```

---
