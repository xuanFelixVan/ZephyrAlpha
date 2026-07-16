# [BLUEPRINT] MOD-INF-005 | scripts/governance/d6_security/__init__.py | §
# [TTL] permanent
"""D6 安全漏洞 — 代码/配置/依赖安全风险审计。

检查项：
- 密钥泄露（API key / token / password 硬编码）
- 依赖漏洞扫描
- 敏感文件权限/加密状态
- SQL 注入 / XSS / 路径遍历风险点检测
"""

__all__ = [
    "check_protected_paths",
    "detect_anchor_file_deletion",
    "detect_git_dangerous",
    "detect_keywords_in_logs",
    "detect_permanent_file_deletion",
    "detect_secrets",
    "detect_shell_dangerous",
    "detect_shell_true",
    "detect_threading_lock",
    "detect_vague_terms",
    "run_adversarial_checks",
    "scan_runtime_log_secrets",
    "scan_secret_leak",
    "validate_gate_discipline",
]
