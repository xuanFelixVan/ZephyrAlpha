# [MODULE] tests.data.data.test_business_data_categories_unique
# [DOMAIN] D_DATA
# [TTL] task_bound

"""business_data_categories.yaml 同键防重门（Owner 批裁定「立项，机械去重+判重测试钉死」，st-t3b-dedup 2026-10-08）。

背景：HEAD 曾 338 条含 116 组完全重复 category_id（多批追加未判重）；2026-10-08 收敛后
本门钉死回归（TableRegistry.table() fail-closed 以 category_id 为唯一键，同键重复=注册表
最小一致性不变量）：
  - 真册只读断言 category_id 全集唯一；
  - tmp_path 注入面：重复 category_id 注入必被拦（红），合法唯一键必放行（绿）。
真册零写入（禁写生产路径）；判重器在本模块定义。
"""

from __future__ import annotations

import collections
from pathlib import Path

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[3]
_CATEGORIES_YAML = _REPO_ROOT / "docs" / "03_modules" / "_cross_layer" / "database" / "business_data_categories.yaml"


def find_duplicate_category_ids(entries: list[dict]) -> list[str]:
    """返回重复出现的 category_id（排序去重）；空列表=无重复（放行）。"""
    counts = collections.Counter(e.get("category_id") for e in entries)
    return sorted(cid for cid, n in counts.items() if cid is not None and n > 1)


def _load_real_categories() -> list[dict]:
    with open(_CATEGORIES_YAML, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data or []


# ── 绿：真册回归钉死 ─────────────────────────────────────────────────────
def test_real_registry_category_ids_unique():
    entries = _load_real_categories()
    assert entries, "business_data_categories.yaml 加载为空（文件缺失或结构漂移）"
    dups = find_duplicate_category_ids(entries)
    assert not dups, f"business_data_categories.yaml 出现重复 category_id（回归 116 组在案病）：{dups}"


# ── 红：重复注入必拦（tmp_path 隔离，零生产写入）────────────────────────
def test_injected_duplicate_category_id_is_caught(tmp_path):
    payload = [
        {"category_id": "dup_cat", "engine": "clickhouse", "database": "c0_meta", "table": "a"},
        {"category_id": "dup_cat", "engine": "clickhouse", "database": "c1_market", "table": "b"},
        {"category_id": "solo_cat", "engine": "clickhouse", "database": "c0_meta", "table": "c"},
    ]
    p = tmp_path / "categories_inject.yaml"
    p.write_text(yaml.safe_dump(payload, allow_unicode=True), encoding="utf-8")
    with open(p, encoding="utf-8") as f:
        entries = yaml.safe_load(f) or []
    assert find_duplicate_category_ids(entries) == ["dup_cat"], "重复 category_id 注入未被拦截"


# ── 绿：合法唯一键放行 ───────────────────────────────────────────────────
def test_injected_unique_keys_pass(tmp_path):
    payload = [
        {"category_id": f"ok_cat_{i}", "engine": "clickhouse", "database": "c0_meta", "table": f"t{i}"}
        for i in range(3)
    ]
    p = tmp_path / "categories_ok.yaml"
    p.write_text(yaml.safe_dump(payload, allow_unicode=True), encoding="utf-8")
    with open(p, encoding="utf-8") as f:
        entries = yaml.safe_load(f) or []
    assert find_duplicate_category_ids(entries) == []
