# [A_test] module_id: SRC-TST-1872 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
from zephyr.feedback_loop.config import FLEConfig


class TestFLEConfig:
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
            max_concurrent_actions=5,
            autonomy_max_level=2,
            kb_path="/data/kb/",
            worm_path="/data/worm/",
        )
        assert cfg.enable_autonomous_actions is True
        assert cfg.log_dir == "/tmp/fle/"
        assert cfg.otel_endpoint == "http://otel:4317"
        assert cfg.max_concurrent_actions == 5
        assert cfg.autonomy_max_level == 2
        assert cfg.kb_path == "/data/kb/"
        assert cfg.worm_path == "/data/worm/"

    def test_is_dataclass(self):
        cfg = FLEConfig()
        assert hasattr(cfg, "__dataclass_fields__")

    def test_immutability_of_defaults(self):
        cfg1 = FLEConfig()
        cfg2 = FLEConfig()
        cfg1.enable_autonomous_actions = True
        assert cfg2.enable_autonomous_actions is False
