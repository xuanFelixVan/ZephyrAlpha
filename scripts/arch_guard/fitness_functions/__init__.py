# [BLUEPRINT] MOD-INF-005 | scripts/arch_guard/fitness_functions/__init__.py | §
"""Architecture Guard — 不变量适应度函数集

每个文件对应 invariants.yaml 中的一条不变量。
执行方式：python scripts/arch_guard/fitness_functions/<name>.py
exit 0 = 不变量未被违反，exit 1 = 违反。

桩文件（_manifest.yaml 中 status=stub）可作为模板扩展。
"""
