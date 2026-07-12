# [A_test] module_id: SRC-TST-0943 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_config
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.config
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_config.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.config import FLEConfig


class TestFLEConfigInstantiation:
    def test_creates_with_defaults(self):
        config = FLEConfig()
        assert config.enable_autonomous_actions is False
        assert config.max_concurrent_actions == 3
        assert config.autonomy_max_level == 0
        assert config.log_dir == "logs/fle/"
        assert config.otel_endpoint == "http://localhost:4317"
        assert config.kb_path == "data/fle/kb/"
        assert config.worm_path == "data/fle/worm/"

    def test_creates_with_custom_params(self):
        config = FLEConfig(
            enable_autonomous_actions=True,
            max_concurrent_actions=5,
            autonomy_max_level=2,
            log_dir="/custom/logs/",
        )
        assert config.enable_autonomous_actions is True
        assert config.max_concurrent_actions == 5
        assert config.autonomy_max_level == 2
        assert config.log_dir == "/custom/logs/"


class TestFLEConfigAttributes:
    def test_all_fields_accessible(self):
        config = FLEConfig()
        assert hasattr(config, "enable_autonomous_actions")
        assert hasattr(config, "log_dir")
        assert hasattr(config, "otel_endpoint")
        assert hasattr(config, "max_concurrent_actions")
        assert hasattr(config, "autonomy_max_level")
        assert hasattr(config, "kb_path")
        assert hasattr(config, "worm_path")

    def test_modification(self):
        config = FLEConfig()
        config.enable_autonomous_actions = True
        config.max_concurrent_actions = 10
        assert config.enable_autonomous_actions is True
        assert config.max_concurrent_actions == 10
