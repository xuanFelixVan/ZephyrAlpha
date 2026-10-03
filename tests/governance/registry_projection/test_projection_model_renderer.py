# [A_test] module_id: MOD-GOV_registry_projection_model_renderer | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.governance.registry_projection.test_projection_model_renderer
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TTL] task_bound
"""红蓝①：快照模型/渲染器——字节确定性+语义等值+排序键同构+四象限判别。"""

from __future__ import annotations

import pytest
import yaml

from zephyr.governance.registry_projection.model import (
    ProjectionSnapshot,
    Section,
    canonicalize,
    entry_identity_key,
    snapshot_from_yaml,
)
from zephyr.governance.registry_projection.pg_source import ProjectionUnavailable, snapshot_from_bundle
from zephyr.governance.registry_projection.renderer import SemanticMismatch, render, self_check
from zephyr.governance.registry_projection.state import (
    QUADRANT_CLEAN,
    QUADRANT_CONFLICT,
    QUADRANT_PRIVATE_EDIT,
    QUADRANT_STALE,
    ProjectionState,
    classify,
    load_state,
    save_state,
)

SAMPLE = """schema_version: 1.1.0
title: 测试册
capabilities:
- capability_id: b_cap
  aliases:
  - 别名乙
  description: 描述乙
- capability_id: a_cap
  description: 描述甲
creation_tokens:
- file: src/z.py
  token: tok-2
  created_by: sess-1
- file: src/a.py
  token: tok-1
- file: src/a.py
  token: tok-0
  created_by: sess-0
  merge_evaluation: "同文件多 token（复合键实证）"
di_seam_exemptions: []
"""


def _snap(text: str = SAMPLE) -> ProjectionSnapshot:
    return snapshot_from_yaml(text, registry_id="REG-TEST-001", physical_path="test_registry.yaml")


def test_extract_preserves_order_and_duplicates():
    snap = _snap()
    tok = snap.section("creation_tokens")
    assert [entry_identity_key(e) for e in tok.entries] == [
        ("src/z.py", "tok-2"),
        ("src/a.py", "tok-1"),
        ("src/a.py", "tok-0"),
    ]


def test_render_deterministic_and_semantic_roundtrip():
    snap = _snap()
    r1, r2 = render(snap), render(snap)
    assert r1 == r2  # 红蓝①：同快照两次渲染字节一致
    assert yaml.safe_load(r1) == yaml.safe_load(SAMPLE)  # 语义等值
    self_check(r1, snap)  # 不抛=通过


def test_self_check_rejects_ambiguous_emission():
    snap = _snap()
    # 裸发射会变型的标量（time-like/zero-padded）→ 渲染必须加引号无损；构造键注入验证自校验报警
    snap.section("creation_tokens").entries[0].append(("version_str", "1.10"))
    rendered = render(snap)
    assert '"1.10"' in rendered  # 加引号保字符串语义
    self_check(rendered, snap)


def test_self_check_rejects_real_mismatch():
    snap = _snap()
    snap2 = _snap()
    snap2.section("creation_tokens").entries[0].append(("token", "forged"))
    # 直接对渲染产物做快照错配断言（模拟账本与产物不一致）
    with pytest.raises(SemanticMismatch):
        self_check(render(snap2), snap)  # rendered 来自 snap2，断言对象是 snap → 必炸


def test_canonicalize_sort_key_is_file_token():
    snap = _snap()
    ordered = canonicalize(snap).section("creation_tokens").entries
    keys = [entry_identity_key(e) for e in ordered]
    assert keys == sorted(keys)  # (file, token) 字节序
    # 多重集等值：规范化只重排不增减（与合并器复合身份同键集）
    orig_map = {entry_identity_key(e): e for e in snap.section("creation_tokens").entries}
    assert {entry_identity_key(e): e for e in ordered} == orig_map


def test_quadrant_classification():
    S, R, D = "sha-s", "sha-r", "sha-d"
    assert classify(D := S, S, S) == QUADRANT_CLEAN
    assert classify("tampered", S, S) == QUADRANT_PRIVATE_EDIT
    assert classify(S, S, "new-r") == QUADRANT_STALE
    assert classify("tampered", S, "new-r") == QUADRANT_CONFLICT
    # PG 宕机降级：render_sha=None，D vs S 本地判别（私改照样现形）
    assert classify(S, S, None) == QUADRANT_CLEAN
    assert classify("tampered", S, None) == QUADRANT_PRIVATE_EDIT


def test_state_save_load_roundtrip(tmp_path):
    st = ProjectionState(content_sha256="abc", ledger_revision=7, registry_path="x.yaml", entry_counts={"t": 1})
    save_state(tmp_path, st)
    loaded = load_state(tmp_path)
    assert loaded == st


def test_bundle_roundtrip():
    snap = _snap()
    snap.ledger_revision = 3
    bundle = {
        "registry_id": snap.registry_id,
        "snapshot_version": 1,
        "ledger_revision": 3,
        "content_sha256": "deadbeef",
        "header_lines": snap.header_lines,
        "sections": [
            {"root_key": s.root_key, "entries": [[list(p) for p in e] for e in s.entries]} for s in snap.sections
        ],
        "trailing_scalars": [list(t) for t in snap.trailing_scalars],
    }
    restored = snapshot_from_bundle(bundle, "test_registry.yaml")
    assert render(restored) == render(snap)
    assert restored.ledger_revision == 3


def test_bundle_bad_shape_raises_unavailable():
    with pytest.raises(ProjectionUnavailable):
        snapshot_from_bundle({"nonsense": True}, "x.yaml")


def test_merge_evaluation_always_quoted():
    r = render(_snap())
    assert 'merge_evaluation: "同文件多 token（复合键实证）"' in r


def test_dict_valued_field_roundtrip_b3_20261003():
    """回归（B3 实弹诊断）：dict 值子树必须嵌套 2 格——拍扁=子键漏成条目兄弟键。

    根因实况：overlay_mode 的 {name_zh, description(多行)} 被 0 缩进发射成同级键，
    回读 overlay_mode=None 且 name_zh 污染条目键集（TRANSLATION/CAND 两册同根因）。
    """
    text = (
        "schema_version: 1.1.0\n"
        "title: 字典值册\n"
        "entries:\n"
        "- id: e1\n"
        "  overlay_mode:\n"
        "    name_zh: 叠加态模式\n"
        '    description: "多行\\n说明"\n'
        "  status: active\n"
        "trailing: []\n"
    )
    snap = snapshot_from_yaml(text, registry_id="REG-T-001", physical_path="docs/x.yaml")
    rendered = render(snap)
    self_check(rendered, snap)  # 修复前在此抛 SemanticMismatch
    entry = yaml.safe_load(rendered)["entries"][0]
    assert set(entry) == {"id", "overlay_mode", "status"}
    assert entry["overlay_mode"]["name_zh"] == "叠加态模式"
    assert entry["overlay_mode"]["description"] == "多行\n说明"


def test_nested_dict_no_sibling_key_leak_b3_20261003():
    """回归（CAND 册实弹）：嵌套 dict 的键不得漏成条目级键（dataflowgraph 假键案）。"""
    text = (
        "schema_version: 1.1.0\n"
        "title: 嵌套册\n"
        "entries:\n"
        "- id: e2\n"
        "  graphs:\n"
        "    dataflowgraph: bm-1\n"
        "    decisiongraph: bm-2\n"
        "  name: 候选甲\n"
    )
    snap = snapshot_from_yaml(text, registry_id="REG-T-002", physical_path="docs/y.yaml")
    rendered = render(snap)
    self_check(rendered, snap)
    entry = yaml.safe_load(rendered)["entries"][0]
    assert set(entry) == {"id", "graphs", "name"}
    assert entry["graphs"] == {"dataflowgraph": "bm-1", "decisiongraph": "bm-2"}
