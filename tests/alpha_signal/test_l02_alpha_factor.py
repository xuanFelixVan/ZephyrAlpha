# [A_test] module_id: MOD-GOV_l02_alpha_factor | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md | §test
# [MODULE] zephyr.l02_alpha_factor
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_l02_alpha_factor.py
# [TTL] task_bound

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

factor_base = pytest.importorskip("zephyr.factor.factor_base")

FactorBase = factor_base.FactorBase
FactorMeta = factor_base.FactorMeta
FactorRegistry = factor_base.FactorRegistry


@pytest.fixture(autouse=True)
def clear_registry():
    FactorRegistry.clear()
    yield
    FactorRegistry.clear()


class TestFactorMeta:
    def test_create_required_fields(self):
        meta = FactorMeta(
            factor_id="test_factor",
            name="Test Factor",
            domain="technical",
        )
        assert meta.factor_id == "test_factor"
        assert meta.name == "Test Factor"
        assert meta.domain == "technical"
        assert meta.version == "1.0.0"
        assert meta.description == ""
        assert meta.dependencies == []
        assert meta.tags == []

    def test_create_with_all_fields(self):
        meta = FactorMeta(
            factor_id="momentum_20d",
            name="20日动量因子",
            domain="technical",
            version="2.0.0",
            description="20-day momentum",
            dependencies=["returns_1d"],
            tags=["short-term", "price-action"],
        )
        assert meta.version == "2.0.0"
        assert len(meta.dependencies) == 1
        assert len(meta.tags) == 2

    def test_mutable_defaults(self):
        meta1 = FactorMeta(factor_id="a", name="A", domain="tech")
        meta2 = FactorMeta(factor_id="b", name="B", domain="tech")
        meta1.dependencies.append("x")
        assert len(meta2.dependencies) == 0


class TestFactorBase:
    def test_cannot_instantiate_abc(self):
        with pytest.raises(TypeError):
            FactorBase()

    def test_concrete_subclass_compute(self):
        class TestFactor(FactorBase):
            meta = FactorMeta(factor_id="test_compute", name="Test", domain="technical")

            def compute(self, data, **kwargs):
                return data["close"].pct_change(20)

        factor = TestFactor()
        dates = pd.date_range("2026-01-01", periods=30)
        df = pd.DataFrame({"close": np.random.randn(30).cumsum() + 100}, index=dates)
        result = factor.compute(df)
        assert isinstance(result, pd.Series)
        assert len(result) == 30

    def test_validate_default(self):
        class TestFactor(FactorBase):
            meta = FactorMeta(factor_id="test_validate", name="Test", domain="technical")

            def compute(self, data, **kwargs):
                return data["close"]

        factor = TestFactor()
        df = pd.DataFrame({"close": [1, 2, 3]})
        assert factor.validate(df) is True

    def test_validate_none(self):
        class TestFactor(FactorBase):
            meta = FactorMeta(factor_id="test_none", name="Test", domain="technical")

            def compute(self, data, **kwargs):
                return data["close"]

        factor = TestFactor()
        assert factor.validate(None) is False

    def test_validate_empty(self):
        class TestFactor(FactorBase):
            meta = FactorMeta(factor_id="test_empty", name="Test", domain="technical")

            def compute(self, data, **kwargs):
                return data["close"]

        factor = TestFactor()
        assert factor.validate(pd.DataFrame()) is False

    def test_repr(self):
        class TestFactor(FactorBase):
            meta = FactorMeta(factor_id="test_repr", name="Test", domain="technical")

            def compute(self, data, **kwargs):
                return data["close"]

        factor = TestFactor()
        r = repr(factor)
        assert "test_repr" in r
        assert "1.0.0" in r

    def test_custom_validate(self):
        class StrictFactor(FactorBase):
            meta = FactorMeta(factor_id="strict_factor", name="Strict", domain="technical")

            def compute(self, data, **kwargs):
                return data["close"]

            def validate(self, data):
                if data is None or data.empty:
                    return False
                return "close" in data.columns and "volume" in data.columns

        factor = StrictFactor()
        df_ok = pd.DataFrame({"close": [1], "volume": [100]})
        df_bad = pd.DataFrame({"close": [1]})
        assert factor.validate(df_ok) is True
        assert factor.validate(df_bad) is False


class TestFactorRegistry:
    def test_register_and_get(self):
        @FactorRegistry.register
        class RegisteredFactor(FactorBase):
            meta = FactorMeta(factor_id="reg_test", name="Reg Test", domain="technical")

            def compute(self, data, **kwargs):
                return data["close"]

        cls = FactorRegistry.get("reg_test")
        assert cls is RegisteredFactor

    def test_register_duplicate_raises(self):
        @FactorRegistry.register
        class DupFactor(FactorBase):
            meta = FactorMeta(factor_id="dup_test", name="Dup", domain="technical")

            def compute(self, data, **kwargs):
                return data["close"]

        with pytest.raises(ValueError, match="已注册"):

            @FactorRegistry.register
            class DupFactor2(FactorBase):
                meta = FactorMeta(factor_id="dup_test", name="Dup2", domain="technical")

                def compute(self, data, **kwargs):
                    return data["close"]

    def test_register_missing_meta_raises(self):
        with pytest.raises(AttributeError, match="缺少 meta"):

            @FactorRegistry.register
            class NoMetaFactor(FactorBase):
                def compute(self, data, **kwargs):
                    return data["close"]

    def test_get_nonexistent_raises(self):
        with pytest.raises(KeyError, match="未在注册表中找到"):
            FactorRegistry.get("nonexistent_factor")

    def test_list_all(self):
        @FactorRegistry.register
        class ListFactor1(FactorBase):
            meta = FactorMeta(factor_id="list_1", name="L1", domain="technical")

            def compute(self, data, **kwargs):
                return data["close"]

        @FactorRegistry.register
        class ListFactor2(FactorBase):
            meta = FactorMeta(factor_id="list_2", name="L2", domain="fundamental")

            def compute(self, data, **kwargs):
                return data["close"]

        all_metas = FactorRegistry.list_all()
        ids = [m.factor_id for m in all_metas]
        assert "list_1" in ids
        assert "list_2" in ids

    def test_list_by_domain(self):
        @FactorRegistry.register
        class DomainFactor1(FactorBase):
            meta = FactorMeta(factor_id="dom_1", name="D1", domain="technical")

            def compute(self, data, **kwargs):
                return data["close"]

        @FactorRegistry.register
        class DomainFactor2(FactorBase):
            meta = FactorMeta(factor_id="dom_2", name="D2", domain="fundamental")

            def compute(self, data, **kwargs):
                return data["close"]

        tech = FactorRegistry.list_by_domain("technical")
        fund = FactorRegistry.list_by_domain("fundamental")
        tech_ids = [m.factor_id for m in tech]
        fund_ids = [m.factor_id for m in fund]
        assert "dom_1" in tech_ids
        assert "dom_2" in fund_ids
        assert "dom_2" not in tech_ids

    def test_clear(self):
        @FactorRegistry.register
        class ClearFactor(FactorBase):
            meta = FactorMeta(factor_id="clear_me", name="Clear", domain="technical")

            def compute(self, data, **kwargs):
                return data["close"]

        FactorRegistry.clear()
        with pytest.raises(KeyError):
            FactorRegistry.get("clear_me")

    def test_len(self):
        assert len(FactorRegistry._registry) == 0

        @FactorRegistry.register
        class LenFactor(FactorBase):
            meta = FactorMeta(factor_id="len_test", name="Len", domain="technical")

            def compute(self, data, **kwargs):
                return data["close"]

        assert len(FactorRegistry._registry) == 1
