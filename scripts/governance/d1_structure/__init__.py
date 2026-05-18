# [BLUEPRINT] MOD-INF-005 | scripts/governance/d1_structure/__init__.py | §
"""D1 结构完整性 — 项目目录/文件结构合规性审计。

检查项：
- 不可变核心（immutable_core）完整性
- config/ YAML 格式/注释/边界校验
- 目录结构完整性（index.md 与磁盘对齐）
- 临时文件/孤立 .py / 残留文件检测
- 脚本冒烟测试（全量 --warn-only 运行）
"""
