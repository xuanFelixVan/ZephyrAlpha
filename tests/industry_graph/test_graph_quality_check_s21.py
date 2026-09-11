# -*- coding: utf-8 -*-
"""S21 流程连通性 + S24 僵尸链检测单测（三期项 6；2026-09-10 S21 口径修正+S24 增补）。
覆盖：上游→下游连通合规 / 断链违规 / supply 并集口径连通 / 小链跳过 /
墓碑节点过滤（历史快照不计起讫）/ 僵尸链·锚点链跳过（S24 收口）/ S24 清单输出。"""
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
    """按查询顺序吐出预置结果集的最小游标桩（_check_s21/_check_s24 依序执行 3 条 SELECT）。"""

    def __init__(self, chains, nodes, edges):
        self._results = [chains, nodes, edges]

    def execute(self, _sql, _params=None):
        pass

    def fetchall(self):
        return self._results.pop(0)

    def fetchone(self):
        return (0,)   # 锚点落位计数查询恒 0（测试无行业聚合落位场景）


def test_s21_connected_chain_passes():
    mod = _load_engine()
    chains = [("CH-1", "链A")]
    nodes = [("n-u", "CH-1", "上游", "原料"), ("n-m", "CH-1", "中游", "制造"), ("n-d", "CH-1", "下游", "应用")]
    edges = [("n-u", "n-m", "structure"), ("n-m", "n-d", "structure")]
    r = mod._check_s21(_FakeCur(chains, nodes, edges))
    assert r["id"] == "S21" and r["advisory"] is True
    assert r["violations"] == []
    assert r["checked_chains"] == 1


def test_s21_broken_chain_violates():
    mod = _load_engine()
    chains = [("CH-1", "断链")]
    nodes = [("n-u", "CH-1", "上游", "原料"), ("n-x", "CH-1", "中游", "制造"), ("n-d", "CH-1", "下游", "应用")]
    edges = [("n-u", "n-x", "structure")]  # 下游孤立
    r = mod._check_s21(_FakeCur(chains, nodes, edges))
    assert len(r["violations"]) == 1
    cid, desc = r["violations"][0]
    assert cid == "CH-1" and "断链" in desc and "结构占比" in desc


def test_s21_supply_edge_counts_as_path():
    mod = _load_engine()
    chains = [("CH-1", "供边链")]
    nodes = [("n-u", "CH-1", "上游", "原料"), ("n-d", "CH-1", "下游", "应用"), ("n-f", "CH-1", "中游", "制造")]
    # structure 缺失，仅 supply 边连通（Owner 口径：structure+supply 均计入连通路径）
    edges = [("n-u", "n-f", "supply"), ("n-f", "n-d", "supplies_to")]
    r = mod._check_s21(_FakeCur(chains, nodes, edges))
    assert r["violations"] == []


def test_s21_small_chain_skipped():
    mod = _load_engine()
    chains = [("CH-1", "小链")]
    nodes = [("n-u", "CH-1", "上游", "原料"), ("n-d", "CH-1", "下游", "应用")]  # 实质节点数 <2
    edges = []
    r = mod._check_s21(_FakeCur(chains, nodes, edges))
    assert r["violations"] == [] and r["checked_chains"] == 0


def test_s21_tombstone_nodes_excluded():
    """墓碑节点（'（已并入'=历史合并快照）不计节点数与起讫集——S8 同口径（2026-09-10 修正）。"""
    mod = _load_engine()
    chains = [("CH-1", "光伏")]
    nodes = [
        ("n-a", "CH-1", "上游", "光伏"),
        ("n-t1", "CH-1", "上游", "光伏（已并入ND-abc-自ND-def）"),
        ("n-t2", "CH-1", "下游", "光伏（已并入ND-abc-自ND-123）"),
    ]
    edges = []
    r = mod._check_s21(_FakeCur(chains, nodes, edges))
    # 去墓碑后实质节点=1 → 僵尸链跳过（S24 收口），不产生伪断链
    assert r["violations"] == [] and r["checked_chains"] == 0


def test_s21_tombstone_repair_restores_check():
    """墓碑被规范节点替代后恢复审查：实质节点≥3 且上游无法连通下游墓碑→仍判违规。"""
    mod = _load_engine()
    chains = [("CH-1", "某链")]
    nodes = [
        ("n-u", "CH-1", "上游", "原料环节"),
        ("n-u2", "CH-1", "上游", "辅料环节"),
        ("n-m", "CH-1", "中游", "制造环节"),
        ("n-t", "CH-1", "下游", "某链（已并入ND-abc-自ND-123）"),
    ]
    edges = [("n-u", "n-m", "structure"), ("n-u2", "n-m", "structure")]
    r = mod._check_s21(_FakeCur(chains, nodes, edges))
    assert len(r["violations"]) == 1 and r["checked_chains"] == 1


def test_s21_anchor_chain_skipped():
    """行业锚点链（实质节点全=链名±'行业'/'行业聚合'）跳过——by-design 无产业链结构。"""
    mod = _load_engine()
    chains = [("CH-1", "白酒行业")]
    nodes = [
        ("n-a", "CH-1", "上游", "白酒行业"),
        ("n-b", "CH-1", "中游", "行业聚合"),
        ("n-c", "CH-1", "下游", "白酒行业行业"),
    ]
    edges = []
    r = mod._check_s21(_FakeCur(chains, nodes, edges))
    assert r["violations"] == [] and r["checked_chains"] == 0


def test_s24_zombie_chains_listed():
    """S24 僵尸链检测：实质节点≤1 / 实质节点名全等链名 → advisory 清单。"""
    mod = _load_engine()
    chains = [("CH-Z1", "光刻胶行业"), ("CH-Z2", "铝产业链2026年5月月报"), ("CH-OK", "健康链")]
    nodes = [
        ("z1-a", "CH-Z1", "中游", "光刻胶行业"),
        ("z1-b", "CH-Z1", "上游", "行业聚合"),
        ("z1-t", "CH-Z1", "下游", "光刻胶行业（已并入ND-x-自ND-y）"),
        ("z2-a", "CH-Z2", "上游", "铝产业链2026年5月月报"),
        ("z2-t1", "CH-Z2", "中游", "铝产业链2026年5月月报（已并入ND-x-自ND-y）"),
        ("z2-t2", "CH-Z2", "下游", "铝产业链2026年5月月报（已并入ND-x-自ND-z）"),
        ("ok-u", "CH-OK", "上游", "原料"),
        ("ok-d", "CH-OK", "下游", "应用"),
    ]
    edges = []
    r = mod._check_s24(_FakeCur(chains, nodes, edges))
    assert r["id"] == "S24" and r["advisory"] is True
    listed = {pk for pk, _ in r["violations"]}
    assert listed == {"CH-Z1", "CH-Z2"}


def test_s24_ignores_small_chains():
    """节点<3 的链不构成僵尸判定基数（S21 同口径）。"""
    mod = _load_engine()
    chains = [("CH-1", "小链")]
    nodes = [("n-a", "CH-1", "上游", "小链（已并入ND-x-自ND-y）"), ("n-b", "CH-1", "下游", "小链")]
    edges = []
    r = mod._check_s24(_FakeCur(chains, nodes, edges))
    assert r["violations"] == []
