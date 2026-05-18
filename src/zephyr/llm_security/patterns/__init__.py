# [BLUEPRINT] MOD-INF-014 | 03_modules/_cross_layer/llm-security/blueprint.md | §
"""LSG 安全模式库（pattern library）。

可复用安全检测模式与签名：
- injection_patterns  — 注入攻击正则集
- jailbreak_patterns  — 越狱提示词模板
- pii_patterns        — PII 识别规则
- content_policy      — 话题边界控制策略
"""

from zephyr.llm_security.patterns.injection_patterns import (
    scan_direct,
    scan_indirect,
    scan_jailbreak,
    scan_encoding_escape,
    scan_shell,
    scan_sql,
    scan_path_traversal,
    scan_semantic_attacks,
)
from zephyr.llm_security.patterns.secrets import scan_secrets

__all__ = [
    'injection_patterns', 'secrets',
    'scan_direct', 'scan_indirect', 'scan_jailbreak', 'scan_encoding_escape',
    'scan_shell', 'scan_sql', 'scan_path_traversal', 'scan_semantic_attacks',
    'scan_secrets',
]
