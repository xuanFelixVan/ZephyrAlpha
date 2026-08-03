# [A_test] module_id: MOD-GOV_command_chain_length_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_command_chain_length_gate
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [INVARIANTS] 命令体积门控max=20不可修改;超限必须阻断
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/escalation-protocol/blueprint.md
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.Exception
# [TESTS] tests/test_command_chain_length_gate.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=stable | safety=M | ai_autonomy=ai_modifiable
# [TTL] task_bound


from zephyr.governance.context_governance.command_chain_length_gate import CommandChainGate


class TestCommandChainGateConstants:
    def test_max_length(self):
        assert CommandChainGate.MAX_LENGTH == 5000

    def test_max_commands(self):
        assert CommandChainGate.MAX_COMMANDS == 20


class TestCommandChainGateEvaluate:
    def test_empty_chain_passes(self):
        gate = CommandChainGate()
        ok, msg = gate.evaluate([])
        assert ok is True
        assert msg == "OK"

    def test_single_command_passes(self):
        gate = CommandChainGate()
        ok, msg = gate.evaluate(["ls -la"])
        assert ok is True
        assert msg == "OK"

    def test_max_commands_passes(self):
        gate = CommandChainGate()
        chain = ["cmd"] * 20
        ok, msg = gate.evaluate(chain)
        assert ok is True
        assert msg == "OK"

    def test_exceeds_max_commands_blocked(self):
        gate = CommandChainGate()
        chain = ["cmd"] * 21
        ok, msg = gate.evaluate(chain)
        assert ok is False
        assert "21" in msg
        assert "20" in msg

    def test_exceeds_max_length_blocked(self):
        gate = CommandChainGate()
        chain = ["x" * 5001]
        ok, msg = gate.evaluate(chain)
        assert ok is False
        assert "5001" in msg
        assert "5000" in msg

    def test_exactly_max_length_passes(self):
        gate = CommandChainGate()
        chain = ["x" * 5000]
        ok, msg = gate.evaluate(chain)
        assert ok is True
        assert msg == "OK"

    def test_both_limits_exceeded_reports_length_first(self):
        gate = CommandChainGate()
        chain = ["x" * 5001] * 21
        ok, msg = gate.evaluate(chain)
        assert ok is False

    def test_returns_tuple(self):
        gate = CommandChainGate()
        result = gate.evaluate(["cmd"])
        assert isinstance(result, tuple)
        assert len(result) == 2
