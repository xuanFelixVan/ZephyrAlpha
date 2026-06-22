# [A_test] module_id: SRC-TST-0529 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain-governance/code-dedup-engine/blueprint.md | §
# [MODULE] tests.test_code_analyzer_runner
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
from zephyr.governance.code_analyzer_runner import (
    CodeAnalyzerRunner,
)


class TestCodeAnalyzerRunner:
    def test_instantiation(self):
        runner = CodeAnalyzerRunner()
        assert runner is not None

    def test_run_returns_list(self):
        runner = CodeAnalyzerRunner()
        result = runner.run()
        assert isinstance(result, list)

    def test_summary_returns_dict(self):
        runner = CodeAnalyzerRunner()
        runner.run()
        result = runner.summary()
        assert isinstance(result, dict)
