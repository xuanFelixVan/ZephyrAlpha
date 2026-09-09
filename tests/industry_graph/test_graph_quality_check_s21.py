# -*- coding: utf-8 -*-
"""S21 流程连通性检查单测（三期项 6，2026-09-09）。
覆盖：上游→下游连通合规 / 断链违规 / supply 并集口径连通 / advisory 进度指标标志（不计违规）。"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ENGINE = REPO / "scripts" / "industry_graph" / "graph_quality_check.py"


def _load_engine():
    spec = importlib.util.spec_from_file_location("graph_quality_check", ENGINE)
    mod = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("graph_quality_check", mod)
    spec.loader.exec_module(mod)
    return mod


class _FakeCur:
    """按查询顺序吐出预置结果集的最小游标桩（_check_s21 依序执行 3 条 SELECT）。"""

    def __init__(self, chains, nodes, edges):
        self._results = [chains, nodes, edges]

    def execute(self, _sql):
        pass

    def fetchall(self):
        return self._results.pop(0)


def test_s21_connected_chain_passes():
    mod = _load_engine()
    chains = [("CH-1", "链A")]
    nodes = [("n-u", "CH-1", "上游"), ("n-m", "CH-1", "中游"), ("n-d", "CH-1", "下游")]
    edges = [("n-u", "n-m", "structure"), ("n-m", "n-d", "structure")]
    r = mod._check_s21(_FakeCur(chains, nodes, edges))
    assert r["id"] == "S21" and r["advisory"] is True
    assert r["violations"] == []
    assert r["checked_chains"] == 1


def test_s21_broken_chain_violates():
    mod = _load_engine()
    chains = [("CH-1", "断链")]
    nodes = [("n-u", "CH-1", "上游"), ("n-x", "CH-1", "中游"), ("n-d", "CH-1", "下游")]
    edges = [("n-u", "n-x", "structure")]  # 下游孤立
    r = mod._check_s21(_FakeCur(chains, nodes, edges))
    assert len(r["violations"]) == 1
    cid, desc = r["violations"][0]
    assert cid == "CH-1" and "断链" in desc and "结构占比" in desc


def test_s21_supply_edge_counts_as_path():
    mod = _load_engine()
    chains = [("CH-1", "供边链")]
    nodes = [("n-u", "CH-1", "上游"), ("n-d", "CH-1", "下游"), ("n-f", "CH-1", "中游")]
    # structure 缺失，仅 supply 边连通（Owner 口径：structure+supply 均计入连通路径）
    edges = [("n-u", "n-f", "supply"), ("n-f", "n-d", "supplies_to")]
    r = mod._check_s21(_FakeCur(chains, nodes, edges))
    assert r["violations"] == []


def test_s21_small_chain_skipped():
    mod = _load_engine()
    chains = [("CH-1", "小链")]
    nodes = [("n-u", "CH-1", "上游"), ("n-d", "CH-1", "下游")]  # 节点数 <3
    edges = []
    r = mod._check_s21(_FakeCur(chains, nodes, edges))
    assert r["violations"] == [] and r["checked_chains"] == 0
