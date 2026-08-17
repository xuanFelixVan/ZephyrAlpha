# [A_test] module_id: MOD-GOV_conftest | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

# tests/conftest.py already adds src/ to sys.path.
# ARCH-034 P4: replaced manual importlib.util.spec_from_file_location loading
# (caused circular-import deadlocks via governance.audit_trail chain) with
# normal imports — test files import what they need directly.
#
# NOTE: sqlite_dumper mock removed (2026-08-17 audit fix) — sys.modules MagicMock
# injection at conftest scope pollutes the entire pytest process. Tests that need
# sqlite_dumper isolation should use monkeypatch/fixtures at test scope instead.
