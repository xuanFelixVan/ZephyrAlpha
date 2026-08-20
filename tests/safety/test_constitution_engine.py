# [A_test] module_id: MOD-GOV_constitution_engine | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-030 | docs/03_modules/_cross_layer/red_blue_validator/blueprint.md | §4.1
# [MODULE] zephyr.security.adversarial_validation.constitution_engine
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] test_constitution_engine.py
# [TTL] task_bound

from datetime import UTC, datetime
from pathlib import Path

import pytest

constitution_mod = pytest.importorskip(
    "zephyr.security.adversarial_validation.constitution_engine",
    reason="constitution_engine not available",
)
ConstitutionEngine = constitution_mod.ConstitutionEngine
DuplicateArticleError = constitution_mod.DuplicateArticleError
RegistryWriteError = constitution_mod.RegistryWriteError

models_mod = pytest.importorskip(
    "zephyr.security.adversarial_validation.models",
    reason="models not available",
)
BypassEntry = models_mod.BypassEntry


@pytest.fixture
def temp_registry(tmp_path: Path) -> Path:
    """创建临时注册表文件用于测试。"""
    registry = tmp_path / "_constitution_registry.yaml"
    registry.write_text(
        "module_id: MOD-INF-005\n"
        "registry_version: '1.0.0'\n"
        "total_articles: 1\n"
        "last_updated: '2026-06-22'\n"
        "articles:\n"
        "  - article_id: CONST-001\n"
        "    name: 'Test Article'\n"
        "    derived_from: 'Test Source'\n"
        "    defense_action: 'test_gate.scan'\n"
        "    applicable_gates: ['G6']\n"
        "    status: active\n",
        encoding="utf-8",
    )
    return registry


@pytest.fixture
def engine(temp_registry: Path) -> ConstitutionEngine:
    """创建使用临时注册表的ConstitutionEngine实例。"""
    return ConstitutionEngine(registry_path=temp_registry)


class TestConstitutionEngineInit:
    def test_default_registry_path(self):
        """测试默认注册表路径指向正确的文件名（下划线）。"""
        from zephyr.security.adversarial_validation.constitution_engine import _REGISTRY_PATH

        assert _REGISTRY_PATH.name == "_constitution_registry.yaml"
        assert _REGISTRY_PATH.exists(), f"注册表文件不存在: {_REGISTRY_PATH}"

    def test_custom_registry_path(self, temp_registry: Path):
        engine = ConstitutionEngine(registry_path=temp_registry)
        assert engine.registry_path == temp_registry


class TestLearnFromBypass:
    def test_bypass_below_threshold_returns_none(self, engine: ConstitutionEngine):
        """count < 3 时不生成article。"""
        bypass = BypassEntry(
            entry_id="bp-001",
            scenario_id="scn-001",
            gate_id="test_gate",
            root_cause="injection attack",
            count=2,
        )
        result = engine.learn_from_bypass(bypass)
        assert result is None

    def test_bypass_at_threshold_generates_article(self, engine: ConstitutionEngine):
        """count >= 3 时生成article。"""
        bypass = BypassEntry(
            entry_id="bp-002",
            scenario_id="scn-002",
            gate_id="new_gate",
            root_cause="prompt injection bypass",
            count=3,
        )
        result = engine.learn_from_bypass(bypass)
        assert result is not None
        assert result.startswith("CONST-")

    def test_duplicate_bypass_returns_none(self, engine: ConstitutionEngine):
        """同一defense_action的bypass不重复生成article。

        _find_by_action查找defense_action字段，learn_from_bypass传入gate_id。
        当gate_id等于已存在的defense_action时，判定为重复。
        """
        bypass = BypassEntry(
            entry_id="bp-003",
            scenario_id="scn-003",
            gate_id="test_gate.scan",  # 等于注册表中已有的defense_action
            root_cause="injection attack",
            count=5,
        )
        result = engine.learn_from_bypass(bypass)
        assert result is None


class TestClassify:
    def test_classify_injection(self, engine: ConstitutionEngine):
        assert engine.classify("prompt injection attack") == "security_boundary"

    def test_classify_data(self, engine: ConstitutionEngine):
        assert engine.classify("data privacy breach") == "data_sovereignty"

    def test_classify_transaction(self, engine: ConstitutionEngine):
        assert engine.classify("atomic transaction failure") == "transaction_integrity"

    def test_classify_audit(self, engine: ConstitutionEngine):
        assert engine.classify("audit log tampering") == "audit_immutability"

    def test_classify_agent(self, engine: ConstitutionEngine):
        assert engine.classify("agent mcp tool abuse") == "agent_safety"

    def test_classify_knowledge(self, engine: ConstitutionEngine):
        assert engine.classify("kb knowledge provenance") == "knowledge_safety"

    def test_classify_default(self, engine: ConstitutionEngine):
        """未知关键词默认分类为security_boundary。"""
        assert engine.classify("unknown issue") == "security_boundary"


class TestNextArticleId:
    def test_next_id_with_existing(self, engine: ConstitutionEngine):
        """已有CONST-001时，下一个是CONST-002。"""
        next_id = engine.next_article_id()
        assert next_id == "CONST-002"

    def test_next_id_without_registry(self, tmp_path: Path):
        """注册表不存在时返回CONST-001。"""
        engine = ConstitutionEngine(registry_path=tmp_path / "nonexistent.yaml")
        next_id = engine.next_article_id()
        assert next_id == "CONST-001"


class TestFindByAction:
    def test_find_existing(self, engine: ConstitutionEngine):
        """查找已存在的defense_action。"""
        result = engine.find_by_action("test_gate.scan")
        assert result == "CONST-001"

    def test_find_nonexistent(self, engine: ConstitutionEngine):
        """查找不存在的defense_action返回None。"""
        result = engine.find_by_action("nonexistent.action")
        assert result is None


class TestAppendToRegistry:
    def test_append_creates_new_article(self, engine: ConstitutionEngine, temp_registry: Path):
        """追加新article到注册表。"""
        import yaml

        new_article = {
            "article_id": "CONST-002",
            "name": "Test Article 2",
            "derived_from": "Test",
            "defense_action": "new_gate.scan",
            "applicable_gates": ["G6"],
            "status": "active",
            "category": "security_boundary",
            "generated_from": "bp-test",
        }
        engine.append_to_registry(new_article)

        with open(temp_registry, encoding="utf-8") as f:
            raw = yaml.safe_load(f)
        assert len(raw["articles"]) == 2
        assert raw["articles"][1]["article_id"] == "CONST-002"
        assert raw["total_articles"] == 2

    def test_append_to_nonexistent_raises(self, tmp_path: Path):
        """注册表不存在时抛出RegistryWriteError。"""
        engine = ConstitutionEngine(registry_path=tmp_path / "nonexistent.yaml")
        with pytest.raises(RegistryWriteError):
            engine.append_to_registry({"article_id": "CONST-001"})


class TestRegistryIntegrity:
    def test_registry_file_exists(self):
        """验证实际注册表文件存在且可读。"""
        from zephyr.security.adversarial_validation.constitution_engine import _REGISTRY_PATH

        assert _REGISTRY_PATH.exists(), f"注册表文件不存在: {_REGISTRY_PATH}"

    def test_registry_has_articles(self):
        """验证注册表包含articles。"""
        import yaml

        from zephyr.security.adversarial_validation.constitution_engine import _REGISTRY_PATH

        with open(_REGISTRY_PATH, encoding="utf-8") as f:
            raw = yaml.safe_load(f)
        assert "articles" in raw
        assert len(raw["articles"]) > 0
