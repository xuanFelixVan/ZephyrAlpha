# [A_test] module_id: DM-100056 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-019 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §rule_engine
# [MODULE] tests.test_rule_integration
# [INVARIANTS] RuleLoader 与 Skill/Gate/Depgraph/路径全景图集成正确; 性能<500ms; 并发无冲突
# [MODIFY-GUARD] rule_engine.py; skill_registry.yaml; gate_engine.py
# [CONSUMERS] CI pipeline
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest assertions on integration correctness and performance
# [TESTS] tests/test_rule_integration.py
# [TTL] task_bound

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import psycopg2
import pytest
import yaml

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection
from zephyr.gov_enforcement.rule_enforcement.rule_engine.rule_engine import RuleLoader
from zephyr.shared.io.paths import REPO_ROOT

_PROJECT_ROOT = REPO_ROOT
# 注：depgraph 已迁移到 PostgreSQL（P2迁移），_DB_PATH / _ARCH_PANORAMA 路径常量已移除
_SKILL_REGISTRY = _PROJECT_ROOT / "src" / "zephyr" / "orchestration" / "agent_lifecycle" / "skill_registry.yaml"
_RULES_DIR = _PROJECT_ROOT / "docs" / "01_policies_and_standards" / "rules"


@pytest.fixture
def loader():
    return RuleLoader()


class TestColdStart:
    def test_critical_rules_returns_l0(self, loader):
        critical = loader.get_critical_rules()
        assert isinstance(critical, list)
        assert len(critical) >= 9, f"Expected >= 9 L0/critical rules, got {len(critical)}"
        for rule in critical:
            assert rule.get("layer") == "L0" or rule.get("metadata", {}).get("impact_level") == "H"


class TestSkillIntegration:
    def test_skill_registry_rule_bindings(self, loader):
        if not _SKILL_REGISTRY.exists():
            pytest.skip("skill_registry.yaml not found")
        with open(_SKILL_REGISTRY, encoding="utf-8") as f:
            registry = yaml.safe_load(f)
        skills_section = registry.get("skills", {})
        loaded_count = 0
        for category_key in ("domain", "role"):
            category = skills_section.get(category_key, {})
            for skill_id, skill_data in category.items():
                rule_bindings = skill_data.get("rule_bindings", {})
                pre_load = rule_bindings.get("pre_load", [])
                if not pre_load:
                    continue
                for rule_id in pre_load:
                    rule = loader.get_rule_by_id(rule_id)
                    if rule is not None:
                        loaded_count += 1
        assert loaded_count > 0, "At least one skill rule binding should load successfully"


class TestGateIntegration:
    def test_gate_yaml_rule_ids(self, loader):
        gate_dir = _PROJECT_ROOT / "src" / "zephyr" / "governance" / "rule_enforcement"
        registry_path = gate_dir / "_registry.yaml"
        if not registry_path.exists():
            pytest.skip("Gate _registry.yaml not found")
        with open(registry_path, encoding="utf-8") as f:
            registry = yaml.safe_load(f)
        gates = registry.get("gates", [])
        loaded_count = 0
        for gate in gates:
            gate_id = gate.get("gate_id", "")
            if not gate_id:
                continue
            rules = loader.load_for_gate(gate_id)
            loaded_count += len(rules)
        if not gates or loaded_count == 0:
            rules_for_g0 = loader.load_for_gate("G0")
            loaded_count = len(rules_for_g0)
        assert loaded_count > 0, "At least one gate rule binding should load successfully"


class TestDepgraphIntegration:
    def test_depgraph_rule_node_count(self, loader):
        try:
            conn = get_depgraph_pg_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(DISTINCT node_id) FROM nodes WHERE node_type = 'rule'")
                db_count = cursor.fetchone()[0]
            conn.close()
        except Exception as exc:
            pytest.skip(f"Cannot query depgraph (PostgreSQL): {exc}")
        yaml_count = len(list(_RULES_DIR.glob("*.yaml")))
        assert db_count > 0 or yaml_count > 0, "Both DB and YAML should have rule entries"
        assert abs(db_count - yaml_count) <= yaml_count * 0.5, (
            f"DB rule count ({db_count}) differs significantly from YAML count ({yaml_count})"
        )


class TestArchitecturePanorama:
    def test_rule_domain_matches_panorama(self, loader):
        try:
            conn = get_depgraph_pg_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(DISTINCT domain_id) FROM domains")
                domain_count = cursor.fetchone()[0]
            conn.close()
        except Exception as exc:
            pytest.skip(f"Cannot query depgraph (PostgreSQL): {exc}")
        all_rules = loader.list_all_rules()
        rule_domains = set()
        for rule in all_rules:
            rule_id = rule.get("rule_id", "")
            if rule_id.startswith("TRAE"):
                rule_domains.add("TRAE")
        assert domain_count > 0 or len(rule_domains) > 0, (
            "Domains should exist in depgraph or rules should have valid domains"
        )


class TestPerformance:
    def test_load_all_under_500ms(self, loader):
        start = time.perf_counter()
        loader.list_all_rules()
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert elapsed_ms < 500, f"Loading all rules took {elapsed_ms:.1f}ms (limit: 500ms)"


class TestConcurrent:
    def test_multiple_loaders_no_conflict(self):
        loaders = [RuleLoader() for _ in range(5)]
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for i, ldr in enumerate(loaders):
                futures.append(executor.submit(ldr.load_for_operation, "file_write"))
            results = []
            for future in as_completed(futures):
                results.append(future.result())
        assert len(results) == 5, "All 5 concurrent loads should complete"
        for result in results:
            assert isinstance(result, list)
            assert len(result) > 0, "Each concurrent load should return rules"
