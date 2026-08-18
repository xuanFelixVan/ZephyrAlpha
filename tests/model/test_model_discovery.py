# [A_test] module_id: MOD-GOV_model_discovery | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-034 | docs/03_modules/_cross_layer/model_profiler/blueprint.md | §3
# [MODULE] tests.test_model_discovery
# [INVARIANTS] DiscoveredModel数据模型;ModelDiscovery构造;DEFAULT_OLLAMA_URL
# [MODIFY-GUARD] src/zephyr/pipeline/model-profiler/model_discovery.py
# [CONSUMERS] MOD-INF-034
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.AssertionError
# [TESTS] tests/test_model_discovery.py
# [TTL] task_bound

import pytest

from zephyr.intelligence.model_profiling.model_discovery import (
    DiscoveredModel,
    ModelDiscovery,
)

# 治本：DEFAULT_OLLAMA_URL 已下沉到 zephyr.shared.foundation.constants（§5.160.9 SSoT），
# model_discovery.py 仅在函数内 lazy-import，非模块级符号。从真源 constants 导入。
from zephyr.shared.foundation.constants import DEFAULT_OLLAMA_URL


class TestDiscoveredModelConstruction:
    def test_all_fields_populated(self):
        model = DiscoveredModel(
            name="qwen3:8b",
            source="ollama",
            provider="qwen3",
            size_bytes=4_900_000_000,
            parameter_size="8B",
            quantization_level="Q4_K_M",
            family="qwen3",
            available=True,
            metadata={"digest": "abc123"},
        )
        assert model.name == "qwen3:8b"
        assert model.source == "ollama"
        assert model.provider == "qwen3"
        assert model.size_bytes == 4_900_000_000
        assert model.parameter_size == "8B"
        assert model.quantization_level == "Q4_K_M"
        assert model.family == "qwen3"
        assert model.available is True
        assert model.metadata == {"digest": "abc123"}

    def test_required_fields_only(self):
        model = DiscoveredModel(name="test-model", source="remote_api")
        assert model.name == "test-model"
        assert model.source == "remote_api"


class TestDiscoveredModelSizeGb:
    def test_size_gb_with_bytes(self):
        model = DiscoveredModel(name="m", source="s", size_bytes=1_073_741_824)
        assert model.size_gb == pytest.approx(1.0, abs=0.01)

    def test_size_gb_with_zero_bytes(self):
        model = DiscoveredModel(name="m", source="s", size_bytes=0)
        assert model.size_gb == 0.0

    def test_size_gb_large_model(self):
        model = DiscoveredModel(name="m", source="s", size_bytes=19_327_352_832)
        assert model.size_gb == pytest.approx(18.0, abs=0.1)


class TestDiscoveredModelDefaults:
    def test_provider_default(self):
        model = DiscoveredModel(name="m", source="s")
        assert model.provider == ""

    def test_size_bytes_default(self):
        model = DiscoveredModel(name="m", source="s")
        assert model.size_bytes == 0

    def test_parameter_size_default(self):
        model = DiscoveredModel(name="m", source="s")
        assert model.parameter_size == ""

    def test_quantization_level_default(self):
        model = DiscoveredModel(name="m", source="s")
        assert model.quantization_level == ""

    def test_family_default(self):
        model = DiscoveredModel(name="m", source="s")
        assert model.family == ""

    def test_available_default(self):
        model = DiscoveredModel(name="m", source="s")
        assert model.available is True

    def test_metadata_default(self):
        model = DiscoveredModel(name="m", source="s")
        assert model.metadata == {}

    def test_metadata_independent_per_instance(self):
        a = DiscoveredModel(name="a", source="s")
        b = DiscoveredModel(name="b", source="s")
        a.metadata["key"] = "val"
        assert "key" not in b.metadata


class TestModelDiscoveryConstruction:
    def test_default_url(self):
        discovery = ModelDiscovery()
        assert discovery.url == DEFAULT_OLLAMA_URL

    def test_custom_url(self):
        discovery = ModelDiscovery(ollama_url="http://custom:9999")
        assert discovery.url == "http://custom:9999"

    def test_url_trailing_slash_stripped(self):
        discovery = ModelDiscovery(ollama_url="http://localhost:11434/")
        assert discovery.url == "http://localhost:11434"

    def test_default_timeout(self):
        discovery = ModelDiscovery()
        assert discovery.timeout == 15.0

    def test_custom_timeout(self):
        discovery = ModelDiscovery(timeout_s=30.0)
        assert discovery.timeout == 30.0


class TestDefaultOllamaUrl:
    def test_value(self):
        assert DEFAULT_OLLAMA_URL == "http://localhost:11434"

    def test_is_string(self):
        assert isinstance(DEFAULT_OLLAMA_URL, str)


class TestModelDiscoveryDiscoverOllama:
    def test_returns_list_on_failure(self):
        discovery = ModelDiscovery(ollama_url="http://nonexistent:99999", timeout_s=1.0)
        result = discovery.discover_ollama()
        assert isinstance(result, list)
        assert len(result) == 0


class TestModelDiscoveryOllamaAvailable:
    def test_returns_false_on_failure(self):
        discovery = ModelDiscovery(ollama_url="http://nonexistent:99999", timeout_s=1.0)
        assert discovery.ollama_available() is False
