# [BLUEPRINT] MOD-L02-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""technical_indicators 基类/注册表/自动发现 单测（骨架先行 v0.1.0）。

测试内容（骨架契约——冻结接口，不测算法正确性）：
- TechnicalIndicatorMeta 数据类字段与默认值
- TechnicalIndicatorRegistry 注册/查询/列表/分类/列汇总/清空/重复检测
- TechnicalIndicatorBase.validate() / get_params() / 抽象 compute()
- autodiscover_technical_indicators() 自动发现 5 类指标模块
- DDL 列交叉校验：Registry 输出列 == schemas DDL 的 Nullable(Float64) 列

骨架先行纪律：compute() 抛 NotImplementedError 属预期，本测试不断言数值正确性，
仅断言接口契约（meta 字段、注册表行为、DDL 列一致）。
算法实现待后续逐类施工后，在各 category 测试文件中补充数值正确性用例。

设计文档：docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/16_technical_indicator_catalog.md
架构议题：#ARCH-DATA-TI-001
"""

from __future__ import annotations

import re

import pandas as pd
import pytest

# 导入 5 类指标模块触发注册（__init__ 不自动 autodiscover，需显式 import）
from zephyr.factor.technical_indicators import (  # noqa: F401 — 注册副作用
    momentum,
    reversal,
    trend,
    volatility,
    volume,
)
from zephyr.factor.technical_indicators.indicator_base import (
    TechnicalIndicatorBase,
    TechnicalIndicatorMeta,
    TechnicalIndicatorRegistry,
    autodiscover_technical_indicators,
)

# 5 类指标数量契约（catalog §2：趋势10/动量10/波动8/成交量7/反转5）
_EXPECTED_TOTAL = 40
# 全部输出列数契约（catalog §2.6：趋势18+动量15+波动13+成交量7+反转5 = 58）
_EXPECTED_COLUMN_TOTAL = 58


# ============== TechnicalIndicatorMeta ==============


class TestTechnicalIndicatorMeta:
    def test_required_fields(self):
        meta = TechnicalIndicatorMeta(
            indicator_id="test_meta",
            name="测试指标",
            category="trend",
            output_columns=["a"],
            input_columns=["close"],
        )
        assert meta.indicator_id == "test_meta"
        assert meta.name == "测试指标"
        assert meta.category == "trend"
        assert meta.output_columns == ["a"]
        assert meta.input_columns == ["close"]

    def test_defaults(self):
        meta = TechnicalIndicatorMeta(
            indicator_id="t",
            name="t",
            category="trend",
            output_columns=[],
            input_columns=[],
        )
        # 默认值契约
        assert meta.params == {}
        assert meta.version == "0.1.0"  # 骨架先行阶段默认 0.1.0
        assert meta.description == ""

    def test_params_isolated_between_instances(self):
        """每个 meta 实例的 params 应独立（mutable default 用 field(default_factory=dict)）。"""
        m1 = TechnicalIndicatorMeta(
            indicator_id="t1",
            name="t1",
            category="trend",
            output_columns=[],
            input_columns=[],
            params={"p": 1},
        )
        m2 = TechnicalIndicatorMeta(
            indicator_id="t2",
            name="t2",
            category="trend",
            output_columns=[],
            input_columns=[],
        )
        m1.params["p"] = 99
        assert m2.params == {}  # 不受 m1 修改影响


# ============== TechnicalIndicatorRegistry ==============


@pytest.fixture(autouse=False)
def _restore_registry():
    """保存并恢复全局注册表——供会修改 _registry 的测试使用，避免污染其他测试。"""
    saved = dict(TechnicalIndicatorRegistry._registry)
    yield
    TechnicalIndicatorRegistry._registry = saved


class TestRegistryMechanics:
    def test_get_existing(self):
        cls = TechnicalIndicatorRegistry.get("ma")
        assert cls.meta.indicator_id == "ma"

    def test_get_nonexistent_raises(self):
        with pytest.raises(KeyError, match="未在注册表中找到"):
            TechnicalIndicatorRegistry.get("__definitely_not_registered__")

    def test_list_all_count(self):
        metas = TechnicalIndicatorRegistry.list_all()
        assert len(metas) == _EXPECTED_TOTAL

    def test_list_by_category_counts(self):
        assert len(TechnicalIndicatorRegistry.list_by_category("trend")) == 10
        assert len(TechnicalIndicatorRegistry.list_by_category("momentum")) == 10
        assert len(TechnicalIndicatorRegistry.list_by_category("volatility")) == 8
        assert len(TechnicalIndicatorRegistry.list_by_category("volume")) == 7
        assert len(TechnicalIndicatorRegistry.list_by_category("reversal")) == 5

    def test_list_by_category_empty(self):
        assert TechnicalIndicatorRegistry.list_by_category("nonexistent") == []

    def test_list_output_columns_total(self):
        cols = TechnicalIndicatorRegistry.list_output_columns()
        assert len(cols) == _EXPECTED_COLUMN_TOTAL

    def test_list_output_columns_unique(self):
        """输出列名全局唯一——DDL 宽表无列名冲突。"""
        cols = TechnicalIndicatorRegistry.list_output_columns()
        assert len(cols) == len(set(cols)), f"输出列名重复: {[c for c in cols if cols.count(c) > 1]}"

    def test_register_duplicate_raises(self):
        """重复注册同一 indicator_id 应抛 ValueError。"""
        # ma 已由 trend 模块注册
        with pytest.raises(ValueError, match="已注册"):

            @TechnicalIndicatorRegistry.register
            class _DupMA(TechnicalIndicatorBase):
                meta = TechnicalIndicatorMeta(
                    indicator_id="ma",
                    name="dup",
                    category="trend",
                    output_columns=["x"],
                    input_columns=["close"],
                )

                def compute(self, data, **kwargs):
                    raise NotImplementedError

    def test_register_missing_meta_raises(self):
        """注册缺少 meta 属性的类应抛 AttributeError。"""

        class _NoMeta(TechnicalIndicatorBase):
            def compute(self, data, **kwargs):
                raise NotImplementedError

        with pytest.raises(AttributeError, match="缺少 meta 属性"):
            TechnicalIndicatorRegistry.register(_NoMeta)

    def test_register_and_clear_roundtrip(self, _restore_registry):
        """注册新指标→可查询→clear 后为空。"""

        @TechnicalIndicatorRegistry.register
        class _Temp(TechnicalIndicatorBase):
            meta = TechnicalIndicatorMeta(
                indicator_id="__temp_clear_test__",
                name="temp",
                category="trend",
                output_columns=["temp_col"],
                input_columns=["close"],
            )

            def compute(self, data, **kwargs):
                raise NotImplementedError

        assert TechnicalIndicatorRegistry.get("__temp_clear_test__").meta.name == "temp"
        TechnicalIndicatorRegistry.clear()
        assert len(TechnicalIndicatorRegistry.list_all()) == 0


# ============== TechnicalIndicatorBase ==============


class TestBaseClass:
    def test_validate_valid(self):
        """validate() 对含 input_columns 的非空数据返回 True。"""
        cls = TechnicalIndicatorRegistry.get("ma")
        df = pd.DataFrame({"close": [1.0, 2.0, 3.0]})
        assert cls().validate(df) is True

    def test_validate_empty(self):
        cls = TechnicalIndicatorRegistry.get("ma")
        assert cls().validate(pd.DataFrame()) is False

    def test_validate_none(self):
        cls = TechnicalIndicatorRegistry.get("ma")
        assert cls().validate(None) is False

    def test_validate_missing_column_raises(self):
        """validate() 缺少 input_columns 应抛 ValueError。"""
        cls = TechnicalIndicatorRegistry.get("ma")  # input_columns=["close"]
        df = pd.DataFrame({"open": [1.0]})  # 无 close
        with pytest.raises(ValueError, match="缺少列"):
            cls().validate(df)

    def test_get_params_default(self):
        cls = TechnicalIndicatorRegistry.get("ma")
        assert cls().get_params() == {"periods": [5, 10, 20, 60]}

    def test_get_params_override(self):
        cls = TechnicalIndicatorRegistry.get("ma")
        assert cls().get_params(periods=[20]) == {"periods": [20]}

    def test_repr(self):
        cls = TechnicalIndicatorRegistry.get("ma")
        r = repr(cls())
        assert "ma" in r and "trend" in r


# ============== autodiscover ==============


class TestAutodiscover:
    def test_autodiscover_idempotent(self, _restore_registry):
        """autodiscover 重复调用不报错（已注册模块再 import 是 no-op）。

        注：autodiscover 内部 import 已注册模块时 register() 会抛 ValueError，
        但 autodiscover 用 try/except 捕获并 warning，不阻断。此处仅验证不抛。
        """
        # 注册表当前已含全部 40 指标（模块级 import 已触发）
        before = len(TechnicalIndicatorRegistry.list_all())
        autodiscover_technical_indicators()  # 不应抛异常
        after = len(TechnicalIndicatorRegistry.list_all())
        # 数量不变（重复 import 不新增——autodiscover 吞掉 ValueError）
        assert after == before == _EXPECTED_TOTAL


# ============== DDL 列交叉校验 ==============


def _parse_ddl_indicator_columns() -> set[str]:
    """从 schemas DDL 解析所有 Nullable(Float64) 指标列名。

    真源：schemas/categories/market_technical_indicator.py MARKET_TECHNICAL_INDICATOR_DDL
    """
    from schemas.categories.market_technical_indicator import (
        MARKET_TECHNICAL_INDICATOR_DDL,
    )

    # 匹配 `    col_name   Nullable(Float64)  COMMENT '...'`
    return set(re.findall(r"^\s*(\w+)\s+Nullable\(Float64\)", MARKET_TECHNICAL_INDICATOR_DDL, re.MULTILINE))


class TestDDLColumnCrossCheck:
    def test_registry_columns_match_ddl(self):
        """Registry 输出列集合 == DDL Nullable(Float64) 列集合（双向一致）。"""
        ddl_cols = _parse_ddl_indicator_columns()
        registry_cols = set(TechnicalIndicatorRegistry.list_output_columns())
        assert registry_cols == ddl_cols, (
            f"Registry 与 DDL 列不一致。\n"
            f"  Registry 有 DDL 无: {registry_cols - ddl_cols}\n"
            f"  DDL 有 Registry 无: {ddl_cols - registry_cols}"
        )

    def test_ddl_column_count(self):
        """DDL 指标列总数 == 58（catalog §2.6 契约）。"""
        ddl_cols = _parse_ddl_indicator_columns()
        assert len(ddl_cols) == _EXPECTED_COLUMN_TOTAL
