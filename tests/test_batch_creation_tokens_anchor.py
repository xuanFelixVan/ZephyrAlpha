# [MODULE] tests.test_batch_creation_tokens_anchor
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] pytest; yaml; scripts.governance.d3_metadata.batch_creation_tokens
# [CONSUMERS] batch_creation_tokens 锚点插入位置守卫
# [INVARIANTS] 全部用例构造于 tmp 副本 registry（monkeypatch _REGISTRY，不碰生产）
# [TTL] permanent
"""batch_creation_tokens 锚点插入位置守卫（2026-09-23 压测实弹治本）。

缺陷：插入点算到"锚点那一行"而非"锚点条目整块"末尾，新条目被劈进邻条字段块中间，
YAML 把邻条 merge_evaluation 划归新条——邻条静默丢字段、新条静默冒领。
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

import scripts.governance.d3_metadata.batch_creation_tokens as bct

_REG_BODY = """creation_tokens:
- file: docs/existing/neighbor.md
  token: neighbor-token-20260923
  created_by: st-neighbor
  capability: anchor_cap
  merge_evaluation: "邻居自己的净零自评"
- file: docs/existing/tail.md
  token: tail-token-20260923
  created_by: st-tail
  capability: tail_cap
di_seam_exemptions:
- module_path: fake.Thing
  reason: test
"""


@pytest.fixture()
def lab(tmp_path: Path, monkeypatch):
    """tmp 副本 registry + 假 git 扫描（不碰生产账本，也不走真 git）。"""
    reg = tmp_path / "capability_canonical_file_registry.yaml"
    reg.write_text(_REG_BODY, encoding="utf-8")
    monkeypatch.setattr(bct, "_REGISTRY", reg)
    monkeypatch.setattr(bct, "_REPO", tmp_path)
    monkeypatch.setattr(bct, "_git_output", lambda *a: [])
    return reg


def _by_file(data: dict) -> dict[str, dict]:
    return {e["file"]: e for e in data["creation_tokens"]}


def test_neighbor_field_not_stolen_by_new_entry(lab):
    """用例1：锚点条目带 merge_evaluation，插新条后字段仍归邻条，新条不得冒领。"""
    reg = lab
    block = bct.build_block(["docs/new/stress.md"], "st-stress", "stress_cap", "20260923")
    bct.insert_block(block, "anchor_cap")

    data = yaml.safe_load(reg.read_text(encoding="utf-8"))
    by = _by_file(data)

    assert by["docs/existing/neighbor.md"]["merge_evaluation"] == "邻居自己的净零自评"
    assert "merge_evaluation" not in by["docs/new/stress.md"]
    assert by["docs/new/stress.md"]["capability"] == "stress_cap"
    assert by["docs/new/stress.md"]["created_by"] == "st-stress"
    # 邻条其它字段与段外死区不受牵连
    assert by["docs/existing/neighbor.md"]["token"] == "neighbor-token-20260923"
    assert len(data["di_seam_exemptions"]) == 1
    # 位置直证：新条整体落在邻条字段块之后
    text = reg.read_text(encoding="utf-8")
    assert text.index("邻居自己的净零自评") < text.index("- file: docs/new/stress.md")


def test_consecutive_inserts_keep_their_own_fields(lab):
    """用例2：同批连续插两条（各带自评），互不吃字段、两者字段各自完整。"""
    reg = lab
    bct.insert_block(
        bct.build_block(["docs/new/a.md"], "st-a", "cap_a", "20260923", merge_evaluation="A 自评"),
        "anchor_cap",
    )
    bct.insert_block(
        bct.build_block(["docs/new/b.md"], "st-b", "cap_b", "20260923", merge_evaluation="B 自评"),
        "anchor_cap",
    )

    data = yaml.safe_load(reg.read_text(encoding="utf-8"))
    by = _by_file(data)

    assert by["docs/new/a.md"]["merge_evaluation"] == "A 自评"
    assert by["docs/new/b.md"]["merge_evaluation"] == "B 自评"
    assert by["docs/existing/neighbor.md"]["merge_evaluation"] == "邻居自己的净零自评"
    for f, cap, owner in (
        ("docs/new/a.md", "cap_a", "st-a"),
        ("docs/new/b.md", "cap_b", "st-b"),
    ):
        assert by[f]["capability"] == cap and by[f]["created_by"] == owner
        assert set(by[f]) == {"file", "token", "created_by", "capability", "merge_evaluation"}
    assert len(data["creation_tokens"]) == 4
