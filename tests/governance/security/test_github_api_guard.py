# [A_test] module_id: MOD-GOV_github_api_guard | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_github_api_guard
# [INVARIANTS] PR/Issue清洗不可跳过;注入标记必须移除
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/escalation-protocol/blueprint.md
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.Exception
# [TESTS] tests/test_github_api_guard.py
# [TTL] task_bound


from zephyr.governance.security_governance.github_api_guard import GitHubAPIGuard


class TestGitHubAPIGuardInstantiation:
    def test_instantiation(self):
        guard = GitHubAPIGuard()
        assert guard is not None

    def test_allowed_commands(self):
        guard = GitHubAPIGuard()
        assert "run_tests" in guard._allowed_commands
        assert "deploy_staging" in guard._allowed_commands

    def test_empty_audit_log(self):
        guard = GitHubAPIGuard()
        assert guard.get_audit_log() == []


class TestValidateCommand:
    def test_allowed_command(self):
        guard = GitHubAPIGuard()
        ok, msg = guard.validate_command("run_tests", "user1")
        assert ok is True
        assert msg == "OK"

    def test_denied_command(self):
        guard = GitHubAPIGuard()
        ok, msg = guard.validate_command("rm -rf /", "user1")
        assert ok is False
        assert "not allowed" in msg

    def test_injection_command_denied(self):
        guard = GitHubAPIGuard()
        ok, msg = guard.validate_command("; DROP TABLE tasks;", "attacker")
        assert ok is False

    def test_empty_command_denied(self):
        guard = GitHubAPIGuard()
        ok, msg = guard.validate_command("", "user1")
        assert ok is False

    def test_all_allowed_commands(self):
        guard = GitHubAPIGuard()
        for cmd in guard._allowed_commands:
            ok, msg = guard.validate_command(cmd, "user1")
            assert ok is True


class TestAuditLog:
    def test_audit_records_allowed(self):
        guard = GitHubAPIGuard()
        guard.validate_command("run_tests", "user1")
        log = guard.get_audit_log()
        assert len(log) == 1
        assert log[0]["result"] == "allowed"
        assert log[0]["user"] == "user1"

    def test_audit_records_denied(self):
        guard = GitHubAPIGuard()
        guard.validate_command("bad_cmd", "user2")
        log = guard.get_audit_log()
        assert len(log) == 1
        assert log[0]["result"] == "denied"
        assert log[0]["command"] == "bad_cmd"

    def test_audit_accumulates(self):
        guard = GitHubAPIGuard()
        guard.validate_command("run_tests", "user1")
        guard.validate_command("bad_cmd", "user2")
        log = guard.get_audit_log()
        assert len(log) == 2
