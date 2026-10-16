"""tdm_goal_blocks 注入器/探针测试（Q5，裁定#516）。

测试隔离纪律（宪法 §9.6）：全部 tmp_path fixture，禁写生产 config/。"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "governance"))

import tdm_goal_blocks as tgb  # noqa: E402

MINI_TDM = """\
schema_version: "1.2"
map_id: mini
nodes:
- node_id: TDM-E-L1
  name_zh: 大盘总闸
  confidence: verified
- node_id: TDM-E-L9-A01
  name_zh: 源线A
  confidence: proposed
- node_id: TDM-E-L9-V2
  name_zh: 快照V2
  confidence: untested
- node_id: TDM-C-L1
  name_zh: 币圈
  confidence: proposed
edges: []
state_matrix: {}
"""


@pytest.fixture()
def mini_repo(tmp_path, monkeypatch):
    cfg = tmp_path / "config" / "trading_decision_map.yaml"
    cfg.parent.mkdir(parents=True)
    cfg.write_text(MINI_TDM, encoding="utf-8")
    monkeypatch.setattr(tgb, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(tgb, "TDM_PATH", cfg)
    return cfg


def _load_nodes(cfg: Path) -> dict[str, dict]:
    d = yaml.safe_load(cfg.read_text(encoding="utf-8"))
    return {n["node_id"]: n for n in d["nodes"]}


def test_family_mapping_covers_all_and_core_151():
    """分母口径机械可导出：186 节点全映射；core=151（30 源线+4 币圈+AGG 剔除）。"""
    text = (
        Path(__file__).resolve().parents[4].joinpath("config", "trading_decision_map.yaml").read_text(encoding="utf-8")
    )
    d = yaml.safe_load(text)
    assert len(d["nodes"]) == 186
    core = [
        n
        for n in d["nodes"]
        if not (
            tgb.RE_SRC_LINE.match(n["node_id"]) or tgb.RE_CRYPTO.match(n["node_id"]) or n["node_id"] == tgb.AGG_NODE
        )
    ]
    assert len(core) == 151
    for n in d["nodes"]:
        fam, status = tgb._family_for(n["node_id"])
        assert fam in tgb.FAMILY_TABLE, n["node_id"]
        assert status in ("active", "suspended", "suspended_reference"), n["node_id"]


def test_goal_block_fields_complete():
    lines = tgb._goal_block_lines("TDM-E-L9-G1", 3)
    txt = "\n".join(lines)
    for f in ("goal_statement", "output_contract", "exam_ref", "campaign_ref", "status"):
        assert f in txt
    assert "（3 张）" in txt


def test_suspended_marking():
    src = "\n".join(tgb._goal_block_lines("TDM-E-L9-B01", 0))
    assert "suspension_basis" in src and "B 档" in src
    crypto = "\n".join(tgb._goal_block_lines("TDM-C-L1", 0))
    assert "suspension_basis" in crypto and "币圈" in crypto


def test_inject_surgical_roundtrip(mini_repo):
    """注入→解析守恒→幂等重跑零增量→外科剥旧。"""
    before = _load_nodes(mini_repo)
    assert tgb.inject(dry_run=False) == 0
    after = _load_nodes(mini_repo)
    assert len(after) == len(before) == 4
    assert after["TDM-E-L1"]["goal"]["family"] == "F01_大盘两态"
    assert after["TDM-E-L9-A01"]["goal"]["status"] == "suspended_reference"
    assert after["TDM-E-L9-V2"]["goal"]["status"] == "suspended"
    assert after["TDM-C-L1"]["goal"]["status"] == "suspended"
    # 手写字段守恒
    assert after["TDM-E-L1"]["confidence"] == "verified"
    # 幂等：重跑后行数不增
    once = mini_repo.read_text(encoding="utf-8").count("\n")
    assert tgb.inject(dry_run=False) == 0
    twice = mini_repo.read_text(encoding="utf-8").count("\n")
    assert once == twice


def test_block_span_stops_at_top_key(mini_repo):
    """末节点块不得吞并 edges: 顶级段。"""
    spans = tgb._block_spans(mini_repo.read_text(encoding="utf-8"))
    assert [s[0] for s in spans] == ["TDM-E-L1", "TDM-E-L9-A01", "TDM-E-L9-V2", "TDM-C-L1"]
    assert "edges:" in mini_repo.read_text(encoding="utf-8")
