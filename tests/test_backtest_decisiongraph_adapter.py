# [A_test] module_id: SRC-TST-9001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md | §decisiongraph-adapter
# [MODULE] zephyr.backtest.io.decisiongraph_adapter
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound
"""test_backtest_decisiongraph_adapter — BacktestResult→decisiongraph 适配器单元测试。

验证内容：
  - _compute_evidence_hash: SHA-256(idempotency_key)[:16] 正确性
  - backtest_result_to_decision_node: 15 字段 BacktestResult → decision_node 参数映射
  - register_backtest_result_in_decisiongraph: DB 写入（mock）
"""

import hashlib
import json
import sys
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, "src")

try:
    from zephyr.backtest.core.engine_base import BacktestResult
    from zephyr.backtest.io.decisiongraph_adapter import (
        _compute_evidence_hash,
        backtest_result_to_decision_node,
        register_backtest_result_in_decisiongraph,
    )

    _IMPORT_OK = True
    _IMPORT_REASON = ""
except Exception as e:  # pragma: no cover
    _IMPORT_OK = False
    _IMPORT_REASON = repr(e)

pytestmark = pytest.mark.skipif(not _IMPORT_OK, reason=_IMPORT_REASON)


def _make_result(**overrides) -> BacktestResult:
    """构造测试用 BacktestResult（15 字段）。"""
    defaults = dict(
        annual_return=0.15,
        end_date=datetime(2024, 12, 31, tzinfo=timezone.utc),
        idempotency_key="bt-2024-001",
        max_drawdown=-0.10,
        sharpe_ratio=1.2,
        start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
        strategy_id="momentum_v1",
        timestamp=datetime(2024, 12, 31, 23, 59, 59, tzinfo=timezone.utc),
        total_return=0.20,
        trades_count=50,
        win_rate=0.6,
    )
    defaults.update(overrides)
    return BacktestResult(**defaults)


class TestComputeEvidenceHash:
    """DEC-INV-005: evidence_hash 由 idempotency_key SHA-256 派生。"""

    def test_hash_length_is_16(self):
        assert len(_compute_evidence_hash("bt-2024-001")) == 16

    def test_hash_matches_sha256_first_16(self):
        key = "bt-2024-001"
        expected = hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]
        assert _compute_evidence_hash(key) == expected

    def test_hash_deterministic_same_input(self):
        assert _compute_evidence_hash("abc") == _compute_evidence_hash("abc")

    def test_hash_differs_for_different_input(self):
        assert _compute_evidence_hash("abc") != _compute_evidence_hash("abd")

    def test_hash_unicode_input(self):
        # 中文幂等键不应抛异常
        h = _compute_evidence_hash("回测-2024")
        assert len(h) == 16


class TestBacktestResultToDecisionNode:
    """BacktestResult → decision_node 参数映射正确性。"""

    def test_layer_id_is_L5(self):
        node = backtest_result_to_decision_node(_make_result())
        assert node["layer_id"] == "L5"

    def test_node_type_is_signal(self):
        node = backtest_result_to_decision_node(_make_result())
        assert node["node_type"] == "signal"

    def test_path_format(self):
        r = _make_result(strategy_id="momentum_v1", idempotency_key="bt-2024-001")
        node = backtest_result_to_decision_node(r)
        assert node["path"] == "backtest/momentum_v1/bt-2024-001"

    def test_module_id_is_MOD_BT_001(self):
        node = backtest_result_to_decision_node(_make_result())
        assert node["module_id"] == "MOD-BT-001"

    def test_evidence_hash_derived_from_idempotency_key(self):
        r = _make_result(idempotency_key="unique-key-123")
        node = backtest_result_to_decision_node(r)
        assert node["evidence_hash"] == _compute_evidence_hash("unique-key-123")

    def test_decision_name_contains_strategy_id(self):
        r = _make_result(strategy_id="my_strategy")
        node = backtest_result_to_decision_node(r)
        assert "my_strategy" in node["decision_name"]
        assert "my_strategy" in node["decision_name_en"]

    def test_inputs_contains_required_fields(self):
        node = backtest_result_to_decision_node(_make_result())
        inputs = json.loads(node["inputs"])
        assert "start_date" in inputs
        assert "end_date" in inputs
        assert inputs["trades_count"] == 50

    def test_outputs_contains_performance_metrics(self):
        node = backtest_result_to_decision_node(_make_result())
        outputs = json.loads(node["outputs"])
        assert outputs["annual_return"] == 0.15
        assert outputs["sharpe_ratio"] == 1.2
        assert outputs["max_drawdown"] == -0.10
        assert outputs["win_rate"] == 0.6

    def test_conditions_contains_overfitting_flag(self):
        node = backtest_result_to_decision_node(_make_result(overfitting_flag=True))
        conditions = json.loads(node["conditions"])
        assert conditions["overfitting_flag"] is True

    def test_facets_contains_metadata(self):
        r = _make_result()
        node = backtest_result_to_decision_node(r)
        facets = json.loads(node["facets"])
        assert facets["idempotency_key"] == r.idempotency_key
        assert facets["strategy_id"] == r.strategy_id
        assert facets["schema_version"] == r.schema_version

    def test_all_required_keys_present(self):
        node = backtest_result_to_decision_node(_make_result())
        required = {
            "layer_id", "node_type", "path", "module_id",
            "decision_name", "decision_name_en",
            "inputs", "outputs", "conditions", "facets",
            "evidence_hash",
        }
        assert required.issubset(set(node.keys()))

    def test_benchmark_symbol_none_in_inputs(self):
        node = backtest_result_to_decision_node(_make_result(benchmark_symbol=None))
        inputs = json.loads(node["inputs"])
        assert inputs["benchmark_symbol"] is None


class TestRegisterBacktestResult:
    """register_backtest_result_in_decisiongraph: DB 写入（mock）。"""

    def test_register_returns_node_id(self):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cur
        mock_cur.fetchone.return_value = (99999,)

        with patch(
            "zephyr.governance.persistence.decisiongraph_schema.get_decisiongraph_pg_connection",
            return_value=mock_conn,
        ):
            node_id = register_backtest_result_in_decisiongraph(_make_result())

        assert node_id == 99999
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

    def test_register_rollback_on_exception(self):
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cur
        mock_cur.execute.side_effect = Exception("DB error")

        with patch(
            "zephyr.governance.persistence.decisiongraph_schema.get_decisiongraph_pg_connection",
            return_value=mock_conn,
        ):
            with pytest.raises(Exception, match="DB error"):
                register_backtest_result_in_decisiongraph(_make_result())

        mock_conn.rollback.assert_called_once()
        mock_conn.close.assert_called_once()
