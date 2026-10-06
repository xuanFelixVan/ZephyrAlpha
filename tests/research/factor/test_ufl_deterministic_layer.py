# [BLUEPRINT] MOD-L02-001 | docs/03_modules/_domain_factor/blueprint.md
# [MODULE] tests.factor.test_ufl_deterministic_layer
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] zephyr.factor.ufl_deterministic_layer
# [CONSUMERS] none
# [STARTUP] pytest
# [MATURITY] production
# [INVARIANTS] 纯内存标记/过滤/SQL 生成测试，不触库不触网；fail-closed 未标记=非确定性；追加式语义冲突标记报错
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=确定性标记/行级打标/视图 SQL/读侧过滤逻辑缺陷
# [TESTS] 本文件
# [TTL] permanent
"""UflDeterministicLayer 单元测试（CAND-FAC-011 / B10-01176，UFL确定性事实层 v8.1）。

覆盖（min_build_spec）：
- 因子级 is_deterministic 标记台账（未标记 fail-closed=非确定性；同值幂等；异值冲突报错，对齐 UFL 追加式事实语义）
- 输入集推导 classify_from_inputs（纯价量输入=确定性；含外部状态输入=非确定性）
- feature_store 行级打标（元数据层，不碰 DDL；原行不被修改；缺 factor_id 列报错）
- 确定性查询视图 SQL（确定性集合过滤；空集合→空视图；单引号转义防注入）
- 读侧过滤 filter_deterministic
"""

from __future__ import annotations

import pytest

from zephyr.factor.ufl_deterministic_layer import (
    UflDeterministicLayer,
    build_deterministic_view_sql,
    classify_from_inputs,
    filter_deterministic,
    tag_feature_rows,
)


def _rows() -> list[dict]:
    return [
        {"trade_date": "2026-08-25", "symbol": "sh.600000", "factor_id": "momentum_20d", "value": 0.12},
        {"trade_date": "2026-08-25", "symbol": "sh.600000", "factor_id": "news_sentiment", "value": 0.66},
        {"trade_date": "2026-08-25", "symbol": "sz.000001", "factor_id": "momentum_20d", "value": -0.03},
    ]


# ---------------------------------------------------------------- 标记台账


def test_unmarked_factor_is_not_deterministic_fail_closed() -> None:
    layer = UflDeterministicLayer()
    assert layer.is_deterministic("momentum_20d") is False
    assert layer.marking_of("momentum_20d") is None


def test_mark_and_query() -> None:
    layer = UflDeterministicLayer()
    layer.mark("momentum_20d", True, evidence="纯OHLCV派生")
    layer.mark("news_sentiment", False, evidence="依赖外部新闻语料")
    assert layer.is_deterministic("momentum_20d") is True
    assert layer.is_deterministic("news_sentiment") is False
    assert layer.marking_of("momentum_20d").evidence == "纯OHLCV派生"
    assert layer.deterministic_factor_ids() == frozenset({"momentum_20d"})


def test_mark_same_value_idempotent_conflict_raises() -> None:
    layer = UflDeterministicLayer()
    layer.mark("momentum_20d", True)
    layer.mark("momentum_20d", True)  # 同值幂等不抛
    with pytest.raises(ValueError, match="冲突"):
        layer.mark("momentum_20d", False)  # 异值=篡改，追加式语义拒绝


def test_mark_empty_factor_id_raises() -> None:
    layer = UflDeterministicLayer()
    with pytest.raises(ValueError):
        layer.mark("", True)


def test_init_with_markings_mapping() -> None:
    layer = UflDeterministicLayer(markings={"a": True, "b": False})
    assert layer.is_deterministic("a") is True
    assert layer.is_deterministic("b") is False


# ---------------------------------------------------------------- 输入集推导


def test_classify_pure_price_volume_inputs_deterministic() -> None:
    assert classify_from_inputs(["open", "high", "low", "close", "volume"]) is True
    assert classify_from_inputs(["close", "amount", "vwap"]) is True


def test_classify_external_inputs_not_deterministic() -> None:
    assert classify_from_inputs(["close", "news_sentiment"]) is False
    assert classify_from_inputs(["llm_score"]) is False


def test_classify_empty_inputs_not_deterministic() -> None:
    assert classify_from_inputs([]) is False


# ---------------------------------------------------------------- 行级打标


def test_tag_feature_rows_appends_flag_without_mutating() -> None:
    layer = UflDeterministicLayer(markings={"momentum_20d": True})
    rows = _rows()
    tagged = tag_feature_rows(rows, layer)
    assert tagged[0]["is_deterministic"] is True
    assert tagged[1]["is_deterministic"] is False  # 未标记 fail-closed
    assert "is_deterministic" not in rows[0]  # 原行不被修改
    assert tagged[0]["value"] == 0.12  # 原字段保留


def test_tag_feature_rows_missing_factor_id_raises() -> None:
    layer = UflDeterministicLayer()
    with pytest.raises(ValueError, match="factor_id"):
        tag_feature_rows([{"trade_date": "2026-08-25", "value": 1.0}], layer)


# ---------------------------------------------------------------- 确定性查询视图


def test_build_view_sql_filters_deterministic_set() -> None:
    layer = UflDeterministicLayer(markings={"momentum_20d": True, "rsi_14": True, "news_sentiment": False})
    sql = build_deterministic_view_sql("c1_market.factor_feature_value", layer)
    assert "CREATE OR REPLACE VIEW" in sql
    assert "c1_market.factor_feature_value" in sql
    assert "'momentum_20d'" in sql
    assert "'rsi_14'" in sql
    assert "news_sentiment" not in sql
    assert "factor_id IN" in sql


def test_build_view_sql_empty_registry_yields_empty_view() -> None:
    layer = UflDeterministicLayer()
    sql = build_deterministic_view_sql("c1_market.factor_feature_value", layer)
    assert "1=0" in sql  # 空集合→空视图（fail-closed：无标记即无确定性子集）


def test_build_view_sql_escapes_single_quote() -> None:
    layer = UflDeterministicLayer(markings={"weird'factor": True})
    sql = build_deterministic_view_sql("c1_market.factor_feature_value", layer)
    assert "'weird''factor'" in sql  # 单引号双写转义


def test_build_view_sql_rejects_bad_table_name() -> None:
    layer = UflDeterministicLayer(markings={"a": True})
    with pytest.raises(ValueError):
        build_deterministic_view_sql("bad table; DROP", layer)


def test_custom_view_name() -> None:
    layer = UflDeterministicLayer(markings={"a": True})
    sql = build_deterministic_view_sql("c1_market.factor_feature_value", layer, view_name="v_det")
    assert "v_det" in sql


# ---------------------------------------------------------------- 读侧过滤


def test_filter_deterministic_keeps_only_marked() -> None:
    layer = UflDeterministicLayer(markings={"momentum_20d": True})
    kept = filter_deterministic(_rows(), layer)
    assert len(kept) == 2
    assert all(r["factor_id"] == "momentum_20d" for r in kept)


def test_filter_deterministic_empty_registry_keeps_nothing() -> None:
    layer = UflDeterministicLayer()
    assert filter_deterministic(_rows(), layer) == []


# ---------------------------------------------------------------- 门面


def test_layer_facade_end_to_end() -> None:
    layer = UflDeterministicLayer()
    layer.mark("momentum_20d", True, evidence="纯价量")
    tagged = layer.tag_rows(_rows())
    assert [r["is_deterministic"] for r in tagged] == [True, False, True]
    kept = layer.filter_deterministic(_rows())
    assert len(kept) == 2
    sql = layer.deterministic_view_sql("c1_market.factor_feature_value")
    assert "momentum_20d" in sql
