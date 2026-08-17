# [BLUEPRINT] MOD-TEST-492 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_test] module_id: MOD-GOV_conftest | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

# NOTE (2026-08-17 audit fix): sys.modules stub injection removed.
# zephyr.governance.escalation is a real package with __init__.py — normal imports work.
# The old _ensure_pkg/_load_mod pattern loaded modules from WRONG paths (e.g.,
# governance/escalation_models.py instead of governance/escalation/escalation_models.py),
# creating incorrect sys.modules entries that could shadow real packages.
# tests/conftest.py already adds src/ to sys.path — no conftest needed here.
