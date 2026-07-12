# [A_test] module_id: SRC-TST-1013 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_fle_config
# [INVARIANTS] FLEConfig defaults must remain stable
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from dataclasses import fields

from zephyr.feedback_loop.config import FLEConfig


class TestFLEConfigInstantiation:
    def test_default_values(self):
        cfg = FLEConfig()
        assert cfg.enable_autonomous_actions is False
        assert cfg.log_dir == "logs/fle/"
        assert cfg.otel_endpoint == "http://localhost:4317"
        assert cfg.max_concurrent_actions == 3
        assert cfg.autonomy_max_level == 0
        assert cfg.kb_path == "data/fle/kb/"
        assert cfg.worm_path == "data/fle/worm/"

    def test_custom_values(self):
        cfg = FLEConfig(
            enable_autonomous_actions=True,
            log_dir="/tmp/fle/",
            otel_endpoint="http://otel:4317",
            max_concurrent_actions=10,
            autonomy_max_level=2,
            kb_path="/data/kb/",
            worm_path="/data/worm/",
        )
        assert cfg.enable_autonomous_actions is True
        assert cfg.log_dir == "/tmp/fle/"
        assert cfg.otel_endpoint == "http://otel:4317"
        assert cfg.max_concurrent_actions == 10
        assert cfg.autonomy_max_level == 2
        assert cfg.kb_path == "/data/kb/"
        assert cfg.worm_path == "/data/worm/"

    def test_is_dataclass(self):
        field_names = {f.name for f in fields(FLEConfig)}
        expected = {
            "enable_autonomous_actions",
            "log_dir",
            "otel_endpoint",
            "max_concurrent_actions",
            "autonomy_max_level",
            "kb_path",
            "worm_path",
        }
        assert field_names == expected

    def test_partial_override(self):
        cfg = FLEConfig(enable_autonomous_actions=True)
        assert cfg.enable_autonomous_actions is True
        assert cfg.max_concurrent_actions == 3


class TestFLEConfigFieldTypes:
    def test_enable_autonomous_actions_bool(self):
        cfg = FLEConfig(enable_autonomous_actions=True)
        assert isinstance(cfg.enable_autonomous_actions, bool)

    def test_max_concurrent_actions_int(self):
        cfg = FLEConfig()
        assert isinstance(cfg.max_concurrent_actions, int)

    def test_autonomy_max_level_int(self):
        cfg = FLEConfig()
        assert isinstance(cfg.autonomy_max_level, int)

    def test_string_fields(self):
        cfg = FLEConfig()
        assert isinstance(cfg.log_dir, str)
        assert isinstance(cfg.otel_endpoint, str)
        assert isinstance(cfg.kb_path, str)
        assert isinstance(cfg.worm_path, str)


class TestFLEConfigBoundary:
    def test_zero_concurrent_actions(self):
        cfg = FLEConfig(max_concurrent_actions=0)
        assert cfg.max_concurrent_actions == 0

    def test_negative_autonomy_level(self):
        cfg = FLEConfig(autonomy_max_level=-1)
        assert cfg.autonomy_max_level == -1

    def test_empty_string_paths(self):
        cfg = FLEConfig(log_dir="", kb_path="", worm_path="")
        assert cfg.log_dir == ""
        assert cfg.kb_path == ""
        assert cfg.worm_path == ""

    def test_large_concurrent_actions(self):
        cfg = FLEConfig(max_concurrent_actions=10000)
        assert cfg.max_concurrent_actions == 10000
