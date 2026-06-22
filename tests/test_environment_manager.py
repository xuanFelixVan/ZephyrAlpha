# [A_test] module_id: SRC-TST-0842 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain-infra_ops/agent-rbac/blueprint.md
# [MODULE] tests.test_environment_manager
# [INVARIANTS] must test all public classes and methods of environment_manager
# [MODIFY-GUARD] environment_manager.py changes require sync
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/test_environment_manager.py

from zephyr.security.access_control.environment_manager import (
    ENVIRONMENTS,
    EnvConfig,
    Environment,
    get_env,
    switch_env,
)


class TestEnvironment:
    def test_enum_values(self):
        assert Environment.DEV.value == "DEV"
        assert Environment.STAGE.value == "STAGE"
        assert Environment.UAT.value == "UAT"
        assert Environment.PAPER.value == "PAPER"
        assert Environment.LIVE.value == "LIVE"

    def test_enum_count(self):
        assert len(Environment) == 5

    def test_str_inheritance(self):
        assert isinstance(Environment.DEV, str)


class TestEnvConfig:
    def test_instantiation(self):
        cfg = EnvConfig(name=Environment.DEV, host="localhost", env_file=".env")
        assert cfg.name == Environment.DEV
        assert cfg.host == "localhost"
        assert cfg.env_file == ".env"
        assert cfg.env_vars == {}
        assert cfg.db_conn == ""
        assert cfg.broker_conn == ""

    def test_custom_values(self):
        cfg = EnvConfig(
            name=Environment.LIVE,
            host="prod.example.com",
            env_file=".env.prod",
            env_vars={"KEY": "VAL"},
            db_conn="pg://live",
            broker_conn="live://gw",
        )
        assert cfg.env_vars == {"KEY": "VAL"}
        assert cfg.db_conn == "pg://live"


class TestEnvironments:
    def test_all_environments_present(self):
        for env in Environment:
            assert env in ENVIRONMENTS

    def test_dev_config(self):
        dev = ENVIRONMENTS[Environment.DEV]
        assert dev.host == "127.0.0.1"
        assert dev.env_file == ".env.dev"
        assert "LOG_LEVEL" in dev.env_vars

    def test_live_config(self):
        live = ENVIRONMENTS[Environment.LIVE]
        assert live.env_vars.get("LOG_LEVEL") == "WARNING"
        assert live.env_vars.get("API_MODE") == "production"

    def test_paper_config(self):
        paper = ENVIRONMENTS[Environment.PAPER]
        assert paper.env_vars.get("API_MODE") == "paper"


class TestGetEnv:
    def test_get_dev(self):
        cfg = get_env(Environment.DEV)
        assert cfg is not None
        assert cfg.name == Environment.DEV

    def test_get_live(self):
        cfg = get_env(Environment.LIVE)
        assert cfg is not None
        assert cfg.name == Environment.LIVE

    def test_get_all(self):
        for env in Environment:
            cfg = get_env(env)
            assert cfg is not None
            assert cfg.name == env


class TestSwitchEnv:
    def test_switch_to_stage(self):
        result = switch_env(Environment.DEV, Environment.STAGE)
        assert result is not None
        assert result.name == Environment.STAGE

    def test_switch_to_live(self):
        result = switch_env(Environment.DEV, Environment.LIVE)
        assert result is not None
        assert result.name == Environment.LIVE

    def test_switch_to_paper(self):
        result = switch_env(Environment.STAGE, Environment.PAPER)
        assert result is not None
        assert result.name == Environment.PAPER
