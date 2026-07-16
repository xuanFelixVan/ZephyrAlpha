# [BLUEPRINT] MOD-INF-005 | scripts/governance/d2_links/__init__.py | §
# [TTL] permanent
"""D2 链接完整性 — 文档内/文档间交叉引用有效性审计。

检查项：
- Markdown 内部锚点可达性
- 跨文件链接有效性（无 404、无断链）
"""

__all__ = ["audit_broken_links", "detect_relative_references"]
