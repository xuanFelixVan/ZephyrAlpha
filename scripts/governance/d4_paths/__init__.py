# [BLUEPRINT] MOD-INF-005 | scripts/governance/d4_paths/__init__.py | §
# [TTL] permanent
"""D4 路径有效性 — 文件系统中路径引用/落位合规性审计。

检查项：
- 绝对路径引用可达性
- 废弃路径引用检测（ruins detection）
- 蓝图路径来源校验（provenance validation）
- 废弃级联影响度量
"""

__all__ = [
    "detect_deprecated_path_writes",
    "detect_excessive_file_moves",
    "detect_ruins_references",
    "detect_split_delete_ref_commit",
]
