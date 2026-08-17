# [A_test] module_id: MOD-GOV_conftest | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-490 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.drift_detector.conftest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound

# NOTE (2026-08-17 audit fix): sys.modules stub injection removed.
# zephyr.gov_drift is a real package with __init__.py — normal imports work.
# The old _ensure_stub/_load pattern hijacked zephyr.* namespace at conftest
# scope, polluting the entire pytest process (zephyr/zephyr.shared/zephyr.shared.contracts
# stubs shadowed real packages for all subsequent tests).
# tests/conftest.py already adds src/ to sys.path — no conftest needed here.
