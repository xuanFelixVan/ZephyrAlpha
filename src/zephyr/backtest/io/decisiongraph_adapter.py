# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md | §decisiongraph-adapter
# [MODULE] zephyr.backtest.io.decisiongraph_adapter
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.backtest.core.engine_base (BacktestResult); zephyr.governance.persistence.decisiongraph_schema (get_decisiongraph_pg_connection)
# [CONSUMERS] 回测管线（vectorized_engine / event_driven_engine 完成后调用）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] BacktestResult -> decision_node 映射单向（回测产出->决策流图节点）; evidence_hash 由 idempotency_key 派生
# [MODIFY-GUARD] CTR-P1-016 契约冻结（BacktestResult 15 字段）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] BacktestResultValidationError; DecisionGraphWriteError
# [TESTS] tests/test_backtest_decisiongraph_adapter.py
# [TTL] permanent
"""
BacktestResult -> decisiongraph 适配器（TRAE-061 Phase 5）

将 BacktestResult（CTR-P1-016，15 字段冻结契约）映射为 decisiongraph
decision_nodes 表的 INSERT 参数，建立回测->决策流图的关联。

映射规则:
  - layer_id: L5（学习层——回测是学习/优化活动）
  - node_type: signal（回测产出策略质量信号）
  - path: backtest/{strategy_id}/{idempotency_key}（唯一路径）
  - module_id: MOD-BT-001（回测引擎模块）
  - inputs: 回测输入参数（start_date/end_date/trades_count/benchmark_symbol）
  - outputs: 回测产出指标（annual_return/total_return/sharpe_ratio/max_drawdown/win_rate）
  - conditions: 过拟合标记（overfitting_flag）
  - facets: 元数据（schema_version/idempotency_key/timestamp/strategy_id）
  - evidence_hash: idempotency_key 的 SHA-256 哈希

数据流:
  BacktestResult(CTR-P1-016)
    -> backtest_result_to_decision_node() -> decision_node 参数 dict
    -> register_backtest_result_in_decisiongraph() -> 写入 PostgreSQL decision_nodes 表
    -> L5 学习层决策节点（供 L6 自评估层消费）
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Any

from zephyr.backtest.core.engine_base import BacktestResult

# decisiongraph 层归属（回测 = L5 学习层）
_BACKTEST_LAYER_ID = "L5"

# decisiongraph 节点类型（回测产出策略质量信号）
_BACKTEST_NODE_TYPE = "signal"

# 回测模块 ID（depgraph 关联键）
_BACKTEST_MODULE_ID = "MOD-BT-001"


def _compute_evidence_hash(idempotency_key: str) -> str:
    """由 idempotency_key 派生 evidence_hash（SHA-256 前 16 字符）。

    :param idempotency_key: 回测运行的幂等键
    :return: 16 字符十六进制哈希
    """
    return hashlib.sha256(idempotency_key.encode("utf-8")).hexdigest()[:16]


def _json_serializable(obj: Any) -> Any:
    """datetime -> ISO 字符串，用于 JSONB 序列化。"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def backtest_result_to_decision_node(result: BacktestResult) -> dict[str, Any]:
    """将 BacktestResult 映射为 decision_nodes INSERT 参数。

    纯映射函数，不写 DB。调用方可将返回的 dict 传给
    apply_decisiongraph.py --op add_design_node 或直接 INSERT。

    :param result: BacktestResult（CTR-P1-016，15 字段冻结契约）
    :return: decision_node 参数 dict，包含以下键:
        - layer_id: "L5"
        - node_type: "signal"
        - path: "backtest/{strategy_id}/{idempotency_key}"
        - module_id: "MOD-BT-001"
        - decision_name: "回测: {strategy_id}"
        - decision_name_en: "Backtest: {strategy_id}"
        - inputs: JSONB（start_date, end_date, trades_count, benchmark_symbol）
        - outputs: JSONB（annual_return, total_return, sharpe_ratio, max_drawdown, win_rate）
        - conditions: JSONB（overfitting_flag）
        - facets: JSONB（schema_version, idempotency_key, timestamp, strategy_id）
        - evidence_hash: SHA-256(idempotency_key)[:16]
    """
    path = f"backtest/{result.strategy_id}/{result.idempotency_key}"
    evidence_hash = _compute_evidence_hash(result.idempotency_key)

    inputs = {
        "start_date": result.start_date.isoformat(),
        "end_date": result.end_date.isoformat(),
        "trades_count": result.trades_count,
        "benchmark_symbol": result.benchmark_symbol,
    }

    outputs = {
        "annual_return": result.annual_return,
        "total_return": result.total_return,
        "sharpe_ratio": result.sharpe_ratio,
        "max_drawdown": result.max_drawdown,
        "win_rate": result.win_rate,
    }

    conditions = {
        "overfitting_flag": result.overfitting_flag,
    }

    facets = {
        "schema_version": result.schema_version,
        "idempotency_key": result.idempotency_key,
        "timestamp": result.timestamp.isoformat(),
        "strategy_id": result.strategy_id,
    }

    return {
        "layer_id": _BACKTEST_LAYER_ID,
        "node_type": _BACKTEST_NODE_TYPE,
        "path": path,
        "module_id": _BACKTEST_MODULE_ID,
        "decision_name": f"回测: {result.strategy_id}",
        "decision_name_en": f"Backtest: {result.strategy_id}",
        "inputs": json.dumps(inputs, ensure_ascii=False, default=_json_serializable),
        "outputs": json.dumps(outputs, ensure_ascii=False, default=_json_serializable),
        "conditions": json.dumps(conditions, ensure_ascii=False, default=_json_serializable),
        "facets": json.dumps(facets, ensure_ascii=False, default=_json_serializable),
        "evidence_hash": evidence_hash,
    }


def register_backtest_result_in_decisiongraph(result: BacktestResult) -> int:
    """将 BacktestResult 注册为 decisiongraph L5 学习层决策节点。

    便捷函数：映射 + 写入 PostgreSQL decision_nodes 表，返回 node_id。

    :param result: BacktestResult
    :return: 新创建的 decision_nodes.node_id
    :raises: psycopg2.IntegrityError（path 唯一冲突 / FK 违规）
    """
    from zephyr.governance.persistence.decisiongraph_schema import (
        get_decisiongraph_pg_connection,
    )

    node_params = backtest_result_to_decision_node(result)

    conn = get_decisiongraph_pg_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO decision_nodes (
                    layer_id, node_type, path, module_id,
                    decision_name, decision_name_en,
                    inputs, outputs, conditions, facets,
                    evidence_hash, build_status
                ) VALUES (
                    %(layer_id)s, %(node_type)s, %(path)s, %(module_id)s,
                    %(decision_name)s, %(decision_name_en)s,
                    %(inputs)s, %(outputs)s, %(conditions)s, %(facets)s,
                    %(evidence_hash)s, 'generated'
                )
                RETURNING node_id
                """,
                node_params,
            )
            row = cur.fetchone()
            conn.commit()
            return row[0] if row else -1
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


__all__ = [
    "backtest_result_to_decision_node",
    "register_backtest_result_in_decisiongraph",
]
