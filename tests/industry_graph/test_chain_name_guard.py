# -*- coding: utf-8 -*-
"""链名写入拦截红蓝测试（Owner 2026-09-10："以后不想再看见'中国节水装备行业发展现状'这种内容"）。

实锤事故：三个真实穿透案例（扩词前全部能写入库）——本测试固化防回归。
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TOOL = REPO / "scripts" / "industry_graph" / "websearch_ingest.py"


def _load_tool():
    spec = importlib.util.spec_from_file_location("websearch_ingest_guard", TOOL)
    mod = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("websearch_ingest_guard", mod)
    spec.loader.exec_module(mod)
    return mod


def _chain_recs(name: str):
    return [{
        "type": "chain", "name": name, "category": "综合", "version_year": 2026,
        "market": "cn", "source": "websearch", "source_doc": "查询词|https://example.com/a|2026-09-10",
    }]


def test_owner_reported_names_rejected():
    """Owner 点名的穿透案例必须被写入校验拒绝。"""
    mod = _load_tool()
    for name in ("中国节水装备行业发展现状", "环氧丙烷产业链供需格局", "聚氨酯材料市场和应用"):
        errs = mod._validate_records(_chain_recs(name), None)
        assert errs, f"穿透回归！'{name}' 未被拦截"


def test_overlong_name_rejected():
    """链名 >12 字拒绝（SOP §4.7.1，2026-09-10 起工具硬校验）。"""
    mod = _load_tool()
    errs = mod._validate_records(_chain_recs("新型高性能稀土永磁材料产业链全景"), None)
    assert any("超长" in e for e in errs)


def test_legitimate_names_pass():
    """规范链名（分类学三段法）不被误伤。"""
    mod = _load_tool()
    for name in ("碳化硅产业链", "全球半导体制造产业链", "食品加工制造行业", "模拟芯片产业链"):
        errs = mod._validate_records(_chain_recs(name), None)
        name_errs = [e for e in errs if "标题腔" in e or "超长" in e]
        assert not name_errs, f"规范名被误拦: '{name}' -> {name_errs}"
