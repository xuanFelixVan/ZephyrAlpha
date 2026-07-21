# [A_test] module_id: MOD-GOV_domain_decay_config | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §
# [MODULE] tests.test_domain_decay_config
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_domain_decay_config.py -q
# [TTL] task_bound
from __future__ import annotations

from zephyr.autonomy_core.context.domain_decay_config import DomainDecay, DomainDecayConfig


class TestDomainDecay:
    def test_instantiation_with_all_fields(self):
        dd = DomainDecay(domain="TEST", halflife_days=45.0, ttl_days=135.0, decay_mode="exponential")
        assert dd.domain == "TEST"
        assert dd.halflife_days == 45.0
        assert dd.ttl_days == 135.0
        assert dd.decay_mode == "exponential"

    def test_instantiation_linear_mode(self):
        dd = DomainDecay(domain="LINEAR", halflife_days=30.0, ttl_days=60.0, decay_mode="linear")
        assert dd.decay_mode == "linear"

    def test_equality(self):
        a = DomainDecay(domain="X", halflife_days=10.0, ttl_days=20.0, decay_mode="exponential")
        b = DomainDecay(domain="X", halflife_days=10.0, ttl_days=20.0, decay_mode="exponential")
        assert a == b


class TestDomainDecayConfig:
    def test_instantiation(self):
        cfg = DomainDecayConfig()
        assert cfg is not None

    def test_get_returns_domain_decay(self):
        cfg = DomainDecayConfig()
        result = cfg.get("CODE_GEN")
        assert isinstance(result, DomainDecay)

    def test_get_code_gen_domain(self):
        cfg = DomainDecayConfig()
        result = cfg.get("CODE_GEN")
        assert result.domain == "CODE_GEN"
        assert result.halflife_days == 60
        assert result.ttl_days == 180
        assert result.decay_mode == "exponential"

    def test_get_ops_fix_domain(self):
        cfg = DomainDecayConfig()
        result = cfg.get("OPS_FIX")
        assert result.domain == "OPS_FIX"
        assert result.halflife_days == 90
        assert result.ttl_days == 270

    def test_get_security_domain(self):
        cfg = DomainDecayConfig()
        result = cfg.get("SECURITY")
        assert result.domain == "SECURITY"
        assert result.halflife_days == 30
        assert result.ttl_days == 90

    def test_get_unknown_domain_returns_default(self):
        cfg = DomainDecayConfig()
        result = cfg.get("UNKNOWN_DOMAIN")
        assert result.domain == "UNKNOWN_DOMAIN"
        assert result.halflife_days == 90
        assert result.ttl_days == 365
        assert result.decay_mode == "exponential"

    def test_get_empty_string_domain_returns_default(self):
        cfg = DomainDecayConfig()
        result = cfg.get("")
        assert result.domain == ""
        assert result.halflife_days == 90
        assert result.ttl_days == 365

    def test_get_preserves_domain_name_in_default(self):
        cfg = DomainDecayConfig()
        result = cfg.get("CUSTOM_XYZ")
        assert result.domain == "CUSTOM_XYZ"

    def test_get_security_has_shortest_halflife(self):
        cfg = DomainDecayConfig()
        sec = cfg.get("SECURITY")
        code = cfg.get("CODE_GEN")
        ops = cfg.get("OPS_FIX")
        assert sec.halflife_days < code.halflife_days
        assert sec.halflife_days < ops.halflife_days

    def test_get_all_known_domains_have_exponential_decay(self):
        cfg = DomainDecayConfig()
        for domain_name in ["CODE_GEN", "OPS_FIX", "SECURITY"]:
            result = cfg.get(domain_name)
            assert result.decay_mode == "exponential"
