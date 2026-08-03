# [A_test] module_id: SRC-TST-0260 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_account_isolator
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_account_isolator.py -q
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.resilience_governance.account_isolator import AccountIsolator


class TestAccountIsolatorInit:
    def test_fresh_instance_has_no_bindings(self):
        iso = AccountIsolator()
        assert iso.get_policy("nonexistent") == "default_blocked"

    def test_isolate_account_returns_false_for_unknown(self):
        iso = AccountIsolator()
        assert iso.isolate_account("unknown") is False


class TestAccountIsolatorBind:
    def test_bind_and_get_policy(self):
        iso = AccountIsolator()
        iso.bind("acct-1", "policy-strict")
        assert iso.get_policy("acct-1") == "policy-strict"

    def test_bind_multiple_accounts(self):
        iso = AccountIsolator()
        iso.bind("acct-a", "policy-alpha")
        iso.bind("acct-b", "policy-beta")
        assert iso.get_policy("acct-a") == "policy-alpha"
        assert iso.get_policy("acct-b") == "policy-beta"

    def test_bind_overwrites_existing_policy(self):
        iso = AccountIsolator()
        iso.bind("acct-1", "policy-old")
        iso.bind("acct-1", "policy-new")
        assert iso.get_policy("acct-1") == "policy-new"

    def test_unbound_account_returns_default_blocked(self):
        iso = AccountIsolator()
        iso.bind("acct-1", "policy-x")
        assert iso.get_policy("acct-2") == "default_blocked"


class TestAccountIsolatorIsolate:
    def test_isolate_bound_account(self):
        iso = AccountIsolator()
        iso.bind("acct-1", "policy-strict")
        assert iso.isolate_account("acct-1") is True

    def test_isolate_unbound_account(self):
        iso = AccountIsolator()
        assert iso.isolate_account("acct-missing") is False

    def test_isolate_after_overwrite(self):
        iso = AccountIsolator()
        iso.bind("acct-1", "policy-a")
        iso.bind("acct-1", "policy-b")
        assert iso.isolate_account("acct-1") is True


class TestAccountIsolatorBoundary:
    def test_empty_string_account_id(self):
        iso = AccountIsolator()
        iso.bind("", "policy-empty")
        assert iso.get_policy("") == "policy-empty"
        assert iso.isolate_account("") is True

    def test_unicode_account_id(self):
        iso = AccountIsolator()
        iso.bind("账户-α", "策略-严格")
        assert iso.get_policy("账户-α") == "策略-严格"

    def test_very_long_account_id(self):
        long_id = "a" * 10000
        iso = AccountIsolator()
        iso.bind(long_id, "policy-long")
        assert iso.get_policy(long_id) == "policy-long"

    def test_special_characters_in_policy(self):
        iso = AccountIsolator()
        iso.bind("acct-1", "policy: <strict> & 'fast'")
        assert iso.get_policy("acct-1") == "policy: <strict> & 'fast'"

    def test_many_bindings(self):
        iso = AccountIsolator()
        for i in range(500):
            iso.bind(f"acct-{i}", f"policy-{i}")
        for i in range(500):
            assert iso.get_policy(f"acct-{i}") == f"policy-{i}"
        assert iso.get_policy("acct-999") == "default_blocked"
