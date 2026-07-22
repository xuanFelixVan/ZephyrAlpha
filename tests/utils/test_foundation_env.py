# [A_test] module_id: MOD-GOV_foundation_env | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §testing

# [MODULE] tests.test_foundation_env

# [INVARIANTS] Env枚举唯一;current_env缓存;ZEPHYR_ENV优先级最高

# [MODIFY-GUARD] env.py变更时同步更新

# [CONSUMERS] CI

# [STABILITY] stable

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 无

# [TESTS] pytest tests/test_foundation_env.py -q
# [TTL] task_bound

import pytest

from zephyr.shared.foundation import env as env_mod


@pytest.fixture(autouse=True)
def _reset_env_cache():
    env_mod._CURRENT_ENV = None
    yield
    env_mod._CURRENT_ENV = None


class TestEnvEnum:
    def test_members(self):
        assert env_mod.Env.DEV.value == "dev"
        assert env_mod.Env.STAGING.value == "staging"
        assert env_mod.Env.PROD.value == "production"
        assert env_mod.Env.TEST.value == "test"

    def test_is_str_enum(self):
        assert isinstance(env_mod.Env.DEV, str)


class TestCurrentEnv:
    def test_detects_pytest_as_test(self):
        result = env_mod.current_env()
        assert result == env_mod.Env.TEST

    def test_caches_result(self):
        first = env_mod.current_env()
        env_mod._CURRENT_ENV = env_mod.Env.PROD
        second = env_mod.current_env()
        assert second == env_mod.Env.PROD

    def test_zephyr_env_overrides(self, monkeypatch):
        env_mod._CURRENT_ENV = None
        monkeypatch.setenv("ZEPHYR_ENV", "production")
        result = env_mod.current_env()
        assert result == env_mod.Env.PROD

    def test_invalid_zephyr_env_falls_back(self, monkeypatch):
        env_mod._CURRENT_ENV = None
        monkeypatch.setenv("ZEPHYR_ENV", "invalid_value_xyz")
        result = env_mod.current_env()
        assert result == env_mod.Env.TEST


class TestIsFunctions:
    def test_is_test_under_pytest(self):
        assert env_mod.is_test() is True

    def test_is_dev_when_set(self):
        env_mod._CURRENT_ENV = env_mod.Env.DEV
        assert env_mod.is_dev() is True
        assert env_mod.is_prod() is False
        assert env_mod.is_staging() is False

    def test_is_prod_when_set(self):
        env_mod._CURRENT_ENV = env_mod.Env.PROD
        assert env_mod.is_prod() is True
        assert env_mod.is_dev() is False

    def test_is_staging_when_set(self):
        env_mod._CURRENT_ENV = env_mod.Env.STAGING
        assert env_mod.is_staging() is True

    def test_is_debug_dev(self):
        env_mod._CURRENT_ENV = env_mod.Env.DEV
        assert env_mod.is_debug() is True

    def test_is_debug_test(self):
        env_mod._CURRENT_ENV = env_mod.Env.TEST
        assert env_mod.is_debug() is True

    def test_is_not_debug_prod(self):
        env_mod._CURRENT_ENV = env_mod.Env.PROD
        assert env_mod.is_debug() is False
