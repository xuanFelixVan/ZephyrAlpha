# [A_test] module_id: MOD-GOV_conftest | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
import sys
from unittest.mock import MagicMock

# tests/conftest.py already adds src/ to sys.path.
# Mock sqlite_dumper for rollback_executor test isolation
# (avoids real SQLite operations during unit tests).
# ARCH-034 P4: replaced manual importlib.util.spec_from_file_location loading
# (caused circular-import deadlocks via governance.audit_trail chain) with
# normal imports — test files import what they need directly.
sys.modules.setdefault("zephyr.infrastructure.rollback.sqlite_dumper", MagicMock())
