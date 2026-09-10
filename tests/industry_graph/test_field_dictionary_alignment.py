# -*- coding: utf-8 -*-
"""字段字典四方对齐测试（Owner 2026-09-10 方案 A，alert_threshold_registry 先例同款）。

强制：YAML 字段字典 ↔ DDL 物理列 ↔ 工具词表 ↔ 引擎词表 四方一致——
词表漂移/字典漏字段/required 缺范例 任一发生 commit 红（治"同 commit 人肉同步"纪律）。
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DICT_PATH = REPO / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "industry_graph_field_dictionary.yaml"
DDL_PATH = REPO / "scripts" / "industry_graph" / "apply_industry_graph_ddl.py"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(name, mod)
    spec.loader.exec_module(mod)
    return mod


def _load_yaml() -> dict:
    import yaml

    return yaml.safe_load(DICT_PATH.read_text(encoding="utf-8"))


def _ddl_columns() -> dict[str, set[str]]:
    """从 DDL-as-Code 真源解析每表物理列（CREATE TABLE 列定义 + ALTER ADD COLUMN）。"""
    ddl = _load_module("apply_industry_graph_ddl", DDL_PATH)
    cols: dict[str, set[str]] = {}
    for stmt in ddl.DDL_STATEMENTS:
        s = " ".join(stmt.split())
        m = re.search(r"CREATE TABLE (IF NOT EXISTS )?(\w+)\s*\((.*)\)\s*$", s)
        if m:
            table = m.group(2)
            body = m.group(3)
            # 先剥离表级约束（UNIQUE(...)/PRIMARY KEY(...)/CHECK(...)），防括号内逗号碎片成假列名
            body = re.sub(r"\b(UNIQUE|PRIMARY KEY|FOREIGN KEY|CONSTRAINT|CHECK)\s*\([^)]*\)", "", body, flags=re.I)
            for line in body.split(","):
                line = line.strip()
                if not line or re.match(r"(PRIMARY KEY|UNIQUE|FOREIGN|CONSTRAINT)", line, re.I):
                    continue
                col = line.split()[0]
                cols.setdefault(table, set()).add(col)
            continue
        m = re.search(r"ALTER TABLE (\w+) ADD COLUMN IF NOT EXISTS (\w+)", s)
        if m:
            cols.setdefault(m.group(1), set()).add(m.group(2))
    return cols


def test_yaml_tables_cover_all_ddl_tables():
    d = _load_yaml()
    tables = set(d["tables"].keys())
    ddl_tables = {t for t in _ddl_columns() if t.startswith("ig_")}
    assert tables == ddl_tables, f"字典表集与 DDL 不一致: 仅YAML={tables - ddl_tables} 仅DDL={ddl_tables - tables}"


def test_yaml_fields_match_ddl_columns():
    d = _load_yaml()
    ddl_cols = _ddl_columns()
    for table, spec in d["tables"].items():
        yaml_fields = set(spec["fields"].keys())
        ddl_set = ddl_cols.get(table, set())
        assert yaml_fields == ddl_set, (
            f"{table} 字段与 DDL 不一致: 仅YAML={sorted(yaml_fields - ddl_set)} 仅DDL={sorted(ddl_set - yaml_fields)}"
        )


def test_vocab_matches_tool_and_engine_constants():
    """YAML vocab = 工具常量 = 引擎常量（词表单一真源的机械验证）。"""
    d = _load_yaml()
    v = d["vocab"]
    wi = _load_module("wi_for_align", REPO / "scripts" / "industry_graph" / "websearch_ingest.py")
    eng = _load_module("eng_for_align", REPO / "scripts" / "industry_graph" / "graph_quality_check.py")
    # 工具侧
    assert wi.TIERS == set(v["tiers"]["values"]) | set(v["tiers_legacy"]["values"])
    assert wi.TIERS_NEW == set(v["tiers"]["values"])
    assert set(wi.FUNCTION_ROLES) == set(v["function_roles"]["values"])
    assert set(wi.ROLES_STD) == set(v["roles_std"]["values"])
    assert wi.CATEGORIES == set(v["categories"]["values"])
    assert wi.CHAIN_STATUSES == set(v["chain_statuses"]["values"])
    assert wi.EDGE_TYPES_V2 == set(v["edge_types_v2"]["values"])
    assert wi.EQUITY_RELATIONS == set(v["equity_relations"]["values"])
    assert wi.EQUITY_VERIFICATION == set(v["equity_verification"]["values"])
    assert wi.DRILL_STATUSES_AI == set(v["drill_statuses_ai"]["values"])
    # 引擎侧
    assert set(eng.TIER_POSITION) == set(v["tiers"]["values"])
    assert set(eng.FUNCTION_ROLES) == set(v["function_roles"]["values"])
    assert set(eng.ROLES_STD) == set(v["roles_std"]["values"])
    assert set(eng.SW_CATEGORIES) == set(v["categories"]["values"])


def test_required_fields_have_good_bad_examples():
    """required=true 的字段必须配 good_example；bad_example 仅易错字段强制（有 bad_example 字段的 good 必在）。
    （Owner 2026-09-10 拍板"必填字段必须配例"；纯枚举/机械格式字段坏例无信息量，豁免 bad。）"""
    d = _load_yaml()
    missing_good = []
    for table, spec in d["tables"].items():
        for field, fdef in spec["fields"].items():
            if fdef.get("required") is not True:
                continue
            if not fdef.get("good_example"):
                missing_good.append(f"{table}.{field}")
            if fdef.get("bad_example") and not fdef.get("good_example"):
                missing_good.append(f"{table}.{field}(有bad无good)")
    assert not missing_good, f"required 字段缺 good_example: {missing_good}"


def test_validated_by_refs_exist_in_engine():
    """字段记录 validated_by 引用的 S 编号必须在引擎检查项中真实存在。"""
    d = _load_yaml()
    eng = _load_module("eng_for_align2", REPO / "scripts" / "industry_graph" / "graph_quality_check.py")
    engine_ids = {c["id"] for c in eng.CHECKS} | {"S11", "S19", "S21", "S24"}  # + Python 特例检查
    refs = set()
    for spec in d["tables"].values():
        for fdef in spec["fields"].values():
            refs.update(fdef.get("validated_by", []))
    dangling = sorted(refs - engine_ids)
    assert not dangling, f"validated_by 引用了引擎不存在的检查项: {dangling}"


def test_enum_refs_resolve_to_vocab():
    """字段 type=enum(vocab:xxx) 引用的词表键必须在 vocab 段存在。"""
    d = _load_yaml()
    for table, spec in d["tables"].items():
        for field, fdef in spec["fields"].items():
            t = str(fdef.get("type", ""))
            if t.startswith("enum(vocab:"):
                key = t[len("enum(vocab:") : -1]
                assert key in d["vocab"], f"{table}.{field} 引用词表 vocab:{key} 不存在"
