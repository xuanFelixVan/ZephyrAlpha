# [BLUEPRINT] MOD-INF-005 | scripts/governance/d6_security/__init__.py | §
"""D6 安全漏洞 — 代码/配置/依赖安全风险审计。

检查项：
- 密钥泄露（API key / token / password 硬编码）
- 依赖漏洞扫描
- 敏感文件权限/加密状态
- SQL 注入 / XSS / 路径遍历风险点检测
"""
