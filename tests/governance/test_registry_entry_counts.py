# [TESTS-FOR] scripts/governance/d3_metadata/check_registry_consistency.py（CR-007 entry_count 对账+回填）
# [MODULE] tests.governance.test_registry_entry_counts
# [DOMAIN] D_GOV_SCRIPTS
# [INVARIANTS] 四类判定不漏不错；五种口径数数精确；回填仅动 STALE 行（保注释/补口径/不动既有口径行）；clean 零改动
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即回填手术 bug 证据
# [TESTS] self
# [TTL] permanent
"""CR-007 · ROOR entry_count 实测对账与回填的单元测试。

覆盖：MATCH/STALE/MANUAL/UNSPECIFIED 判定、yaml_sum/yaml_dict_len 口径、
行级手术回填（保注释、补 counting_rule、不动既有 counting_rule）。
CR-001~006 规则引擎由 CI 端到端覆盖（真实 ROOR 全绿即回归哨兵），此处不重复。
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = _REPO_ROOT / "scripts" / "governance" / "d3_metadata" / "check_registry_consistency.py"


def _load_module():
    if str(_SCRIPT.parent) not in sys.path:
        sys.path.insert(0, str(_SCRIPT.parent))
    spec = importlib.util.spec_from_file_location("crc_under_test", _SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def crc():
    return _load_module()


ROOR_TMPL = """version: "1.0"
tiers:
  - tier: 1
    registries:
      - registry_id: REG-T1
        physical_path: {reg1}
        entry_count: {t1_count}
      - registry_id: REG-T2
        physical_path: {reg1}
        entry_count: {t2_count}
      - registry_id: REG-T5
        physical_path: {reg1}
        entry_count: 2  # 尾注释保留验证
        counting_rule: 既有口径行不得改写
      - registry_id: REG-T3
        physical_path: whatever
        entry_count: 7
      - registry_id: REG-T4
        physical_path: whatever
        entry_count: 9
"""


def _setup(tmp_path: Path) -> tuple[Path, Path]:
    reg1 = tmp_path / "reg1.yaml"
    reg1.write_text(
        "items:\n  - a\n  - b\n  - c\nsum_a:\n  - 1\nsum_b:\n  - 2\n  - 3\nsystems:\n  k1: {}\n  k2: {}\n",
        encoding="utf-8",
    )
    roor = tmp_path / "roor.yaml"
    roor.write_text(ROOR_TMPL.format(reg1=str(reg1).replace("\\", "/"), t1_count=3, t2_count=2), encoding="utf-8")
    return roor, reg1


def test_verify_verdicts(crc, tmp_path, monkeypatch):
    """MATCH/STALE/MANUAL/UNSPECIFIED 四类判定+yaml_sum/dict_len 口径。"""
    roor, _ = _setup(tmp_path)
    reg1 = str(tmp_path / "reg1.yaml").replace("\\", "/")
    monkeypatch.setattr(
        crc,
        "ENTRY_SPECS",
        {
            "REG-T1": ("yaml_list", "items", "items 数组条目数"),
            "REG-T2": ("yaml_list", "items", "items 数组条目数"),
            "REG-T5": ("yaml_sum", "sum_a+sum_b", "求和口径"),  # yaml_sum：1+2=3
        },
    )
    monkeypatch.setattr(crc, "ENTRY_MANUAL", {"REG-T3": "语义口径（测试）"})
    rows = crc.verify_entry_counts(roor)
    by_rid = {r["rid"]: r for r in rows}
    assert by_rid["REG-T1"]["verdict"] == "MATCH"  # entry_count=3 == len(items)=3
    assert by_rid["REG-T2"]["verdict"] == "STALE"  # entry_count=2 != 3
    assert by_rid["REG-T3"]["verdict"] == "MANUAL"
    assert by_rid["REG-T4"]["verdict"] == "UNSPECIFIED"
    assert by_rid["REG-T5"]["verdict"] == "STALE"  # yaml_sum 口径：sum_a(1)+sum_b(2)=3 != 2
    assert set(by_rid) == {"REG-T1", "REG-T2", "REG-T3", "REG-T4", "REG-T5"}


def test_actual_count_kinds(crc, tmp_path):
    """yaml_field / yaml_dict_len / yaml_sum / glob 四种口径数数。"""
    reg = tmp_path / "reg1.yaml"
    reg.write_text("total: 42\nsystems:\n  a: {}\n  b: {}\n", encoding="utf-8")
    p = str(reg).replace("\\", "/")
    assert crc._actual_entry_count(("yaml_field", "total", ""), p) == 42
    assert crc._actual_entry_count(("yaml_dict_len", "systems", ""), p) == 2
    assert crc._actual_entry_count(("yaml_list", "missing_key", ""), p) is None
    d = tmp_path / "cards"
    d.mkdir()
    (d / "skill_a.yaml").write_text("x: 1", encoding="utf-8")
    (d / "skill_b.yaml").write_text("x: 1", encoding="utf-8")
    (d / "other.txt").write_text("x", encoding="utf-8")
    assert crc._actual_entry_count(("glob", "skill_*.yaml", ""), str(d)) == 2
    assert crc._actual_entry_count(("yaml_list", "items", ""), str(tmp_path / "nope.yaml")) is None


def test_apply_updates_surgical(crc, tmp_path, monkeypatch):
    """回填只动 STALE 行数字；缺 counting_rule 补插、既有 counting_rule 不改写；注释保留。"""
    roor, _ = _setup(tmp_path)
    monkeypatch.setattr(
        crc,
        "ENTRY_SPECS",
        {
            "REG-T1": ("yaml_list", "items", "items 数组条目数"),
            "REG-T2": ("yaml_list", "items", "items 数组条目数"),
            "REG-T5": ("yaml_list", "items", "items 数组条目数"),
        },
    )
    monkeypatch.setattr(crc, "ENTRY_MANUAL", {"REG-T3": "语义口径", "REG-T4": "语义口径"})
    rows = crc.verify_entry_counts(roor)
    updates = crc.apply_roor_entry_count_updates(rows, roor)
    assert updates == ["REG-T2: 2 -> 3（补 counting_rule）", "REG-T5: 2 -> 3"]

    text = roor.read_text(encoding="utf-8")
    # T2：修数+按口径补插 counting_rule（插在 entry_count 行后）
    assert "entry_count: 3\n        counting_rule: items 数组条目数" in text
    # T5：修数但既有 counting_rule 保留原样、不补插；尾注释保留
    assert "counting_rule: 既有口径行不得改写" in text
    assert "entry_count: 3  # 尾注释保留验证" in text
    assert text.count("items 数组条目数") == 1
    # T1 原样（MATCH 不回填、不补口径）
    assert "REG-T1" in text
    # 回填后复验无 STALE（T3/T4 manual 不算问题）
    rows2 = crc.verify_entry_counts(roor)
    assert all(r["verdict"] != "STALE" for r in rows2)


def test_apply_updates_noop_when_clean(crc, tmp_path, monkeypatch):
    """全 MATCH 时回填零改动。"""
    roor, _ = _setup(tmp_path)
    roor.write_text(ROOR_TMPL.format(reg1=str(tmp_path / "reg1.yaml").replace("\\", "/"), t1_count=3, t2_count=3), encoding="utf-8")
    monkeypatch.setattr(
        crc,
        "ENTRY_SPECS",
        {"REG-T1": ("yaml_list", "items", "items 数组条目数"), "REG-T2": ("yaml_list", "items", "items 数组条目数")},
    )
    monkeypatch.setattr(crc, "ENTRY_MANUAL", {"REG-T3": "语义口径", "REG-T4": "语义口径"})
    before = roor.read_text(encoding="utf-8")
    rows = crc.verify_entry_counts(roor)
    assert crc.apply_roor_entry_count_updates(rows, roor) == []
    assert roor.read_text(encoding="utf-8") == before
