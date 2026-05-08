"""LSG 安全模式库（pattern library）。

可复用安全检测模式与签名：
- injection_patterns  — 注入攻击正则集
- jailbreak_patterns  — 越狱提示词模板
- pii_patterns        — PII 识别规则
- content_policy      — 话题边界控制策略
"""

__all__ = ['injection_patterns', 'secrets']
