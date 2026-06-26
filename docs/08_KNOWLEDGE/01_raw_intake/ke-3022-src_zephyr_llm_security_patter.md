---
module_id: KE-2922
status: active
title: src/zephyr/llm-security/patterns/secrets.py
category: module_blueprint
ttl: permanent
---

# src/zephyr/llm-security/patterns/secrets.py

src/zephyr/llm-security/patterns/secrets.py

SECRET_PATTERNS: list[tuple[str, str, str]] = [
    # (名称, 正则模式, 脱敏策略: BLOCK | MASK | FLAG)
    # AI API Keys
    ("OpenAI API Key", r"sk-[a-zA-Z0-9]{32,}", "BLOCK"),
    ("Anthropic API Key", r"sk-ant-[a-zA-Z0-9]{32,}", "BLOCK"),
    ("AWS Access Key", r"AKIA[0-9A-Z]{16}", "BLOCK"),
    ("AWS Secret Key", r"(?i)aws[_\-]?secret[_\-]?access[_\-]?key[\s=:]+['\"]?[a-zA-Z0-9/+=]{40}", "BLOCK"),
    ("GitHub Token", r"ghp_[a-zA-Z0-9]{36}", "BLOCK"),
    ("GitHub Pat", r"github_pat_[a-zA-Z0-9_]{36,}", "BLOCK"),
    ("Google API Key", r"AIza[0-9A-Za-z\-_]{35}", "BLOCK"),
    ("Private Key", r"-----BEGIN\s+(RSA\s+|OPENSSH\s+|EC\s+)?PRIVATE\s+KEY-----", "BLOCK"),
    ("JWT Token", r"eyJ[a-zA-Z0-9\-_]{10,}\.[a-zA-Z0-9\-_]{10,}\.[a-zA-Z0-9\-_]{10,}", "BLOCK"),
    # PII
    ("手机号(中国)", r"1[3-9]\d{9}", "MASK"),
    ("身份证号(中国)", r"[1-9]\d{5}(19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]", "MASK"),
    ("邮箱", r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "MASK"),
    ("IP地址", r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "MASK"),
    # 内部敏感关键词
    ("策略参数", r"(最大仓位|止损线|风控阈值)", "FLAG"),
    ("内部API地址", r"https?://(internal|admin|api-internal)\.[a-zA-Z0-9.-]+", "FLAG"),
]
