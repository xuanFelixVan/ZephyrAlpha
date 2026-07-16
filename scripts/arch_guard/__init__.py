# [BLUEPRINT] MOD-INF-005 | scripts/arch_guard/__init__.py | §
# [TTL] permanent
"""Architecture Guard — 不变量自动强制执行基础设施

对标 Google Tricorder / Netflix Conformity Monkey / ArchUnit。
本目录下的所有脚本在 CI Pipeline 中按 manifest.yaml 注册表执行，
任何 exit(1) 的脚本都会阻塞 PR Merge。

设计原则：
  - 每个脚本对应 invariants.yaml 中的一条不变量
  - exit 0 = 不变量未被违反 / exit 1 = 违反
  - 桩文件（status: stub）不参与 CI 执行，只在开发时逐步填充
  - 禁止静默失败——所有违反必须有清晰的人类可读输出

与 invariants.yaml 的关系：
  invariants.yaml 中 fitness_function_path 字段指向本目录的具体脚本。
  本目录是 invariants 的"执行面"——invariants 是"设计面"。
"""

__all__ = [
    "check_acl_boundary",
    "check_cross_plane_communication",
    "check_fe_acl_boundary",
    "check_hot_path_purity",
    "check_scaffold_exit_gates",
    "check_schema_consistency",
    "fitness_functions",
    "import_linter",
    "run_all",
]
