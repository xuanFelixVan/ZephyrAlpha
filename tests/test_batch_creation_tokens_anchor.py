# [MODULE] tests.test_batch_creation_tokens_anchor
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] pytest; yaml; scripts.governance.d3_metadata.batch_creation_tokens
# [CONSUMERS] batch_creation_tokens 语义完整性守卫（裁定#502 直写轨退役后）
# [INVARIANTS] 全部用例 monkeypatch 账本三步注入点（不碰生产 PG、不碰生产投影册）；
#   守卫的历史病根（锚点块劈裂吃邻条字段）在结构化 payload 通道下结构性不可能：
#   条目=字典整体过账本，无字符级插入位可劈
# [MODIFY-GUARD] 2026-10-09 st-regsolo-20261010 随裁定#502 直写轨退役同批重写：原"锚点整块
#   末尾插入"位守卫随直写路径退役；本件转守新不变量（payload 完整性+YAML 字节零变化+锚垫片）
# [TTL] permanent
"""batch_creation_tokens 语义完整性守卫（原锚点插入位守卫的退役后继任）。

历史病根（直写时代，2026-09-23 压测实弹）：插入点算到"锚点那一行"而非锚条目整块
末尾，新条劈进邻条字段块中间——邻条静默丢字段、新条静默冒领。裁定#502 退役直写轨
后该病根结构性不可能（条目=结构化 payload 整体登记进 PG 账本，不存在字符级插入位）；
本件改守三不变量：①block 往返字段零丢失（劈裂病根的语义等价面）②登记全程投影册
字节零变化（无写入位即无劈裂）③锚点兼容垫片恒等。
"""

from __future__ import annotations

from pathlib import Path

import pytest

import scripts.governance.d3_metadata.batch_creation_tokens as bct

_API_REG = "zephyr.governance.registry_ledger.api.register"
_PUBLISH = "zephyr.governance.registry_ledger.baseline.publish_snapshot"
_PROJ_RUN = "zephyr.governance.registry_projection.projection_generator.run"


class _Result:
    def __init__(self, code: str):
        self.code = code
        self.detail = {}


@pytest.fixture()
def lab(tmp_path: Path, monkeypatch):
    """tmp 投影册 + 账本三步注入点替身（不碰生产账本，也不走真 git）。"""
    reg = tmp_path / "capability_canonical_file_registry.yaml"
    reg.write_text(
        "creation_tokens:\n- file: docs/existing/neighbor.md\n  token: neighbor-token-20260923\n"
        '  created_by: st-neighbor\n  capability: anchor_cap\n  merge_evaluation: "邻居自己的净零自评"\n'
        "di_seam_exemptions:\n- module_path: fake.Thing\n  reason: test\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(bct, "_REGISTRY", reg)
    monkeypatch.setattr(bct, "_REPO", tmp_path)
    monkeypatch.setattr(_API_REG, lambda *a, **k: _Result("OK"))
    monkeypatch.setattr(
        _PUBLISH,
        lambda registry_id, **k: {"registry_id": registry_id, "noop": False, "snapshot_version": 1, "entry_count": 1},
    )

    class R:
        ok = True
        quadrant = "clean"
        wrote = False
        evidence_path = ""
        detail = {}

        def to_dict(self):
            return {}

    monkeypatch.setattr(_PROJ_RUN, lambda root, mode="check", **k: R())
    return reg


def test_block_roundtrip_keeps_every_field(lab):
    """不变量①：block 文本→payload 往返，逐字段完整（直写时代"吃字段"病根的语义面）。"""
    block = (
        "- file: docs/new/a.md\n  token: cap-a-a-20260923\n  created_by: st-a\n  capability: cap_a\n"
        '  merge_evaluation: "A 自评"\n'
        "- file: docs/new/b.md\n  token: cap-b-b-20260923\n  created_by: st-b\n  capability: cap_b\n"
        '  merge_evaluation: "B 自评"\n'
    )
    entries = bct._parse_block_entries(block)
    assert entries == [
        {
            "file": "docs/new/a.md",
            "token": "cap-a-a-20260923",
            "created_by": "st-a",
            "capability": "cap_a",
            "merge_evaluation": "A 自评",
        },
        {
            "file": "docs/new/b.md",
            "token": "cap-b-b-20260923",
            "created_by": "st-b",
            "capability": "cap_b",
            "merge_evaluation": "B 自评",
        },
    ]


def test_registration_never_mutates_projection_bytes(lab):
    """不变量②：登记全程投影册字节零变化——无字符级插入位，劈裂病根结构性不可能。"""
    before = lab.read_bytes()
    bct.insert_block(
        bct.build_block(["docs/new/stress.md"], "st-stress", "stress_cap", "20260923", merge_evaluation="新条自评"),
        "anchor_cap",
    )
    assert lab.read_bytes() == before
    # 邻条完整性在投影面不受登记影响（含 merge_evaluation 归属）
    import yaml

    data = yaml.safe_load(lab.read_text(encoding="utf-8"))
    neighbor = next(e for e in data["creation_tokens"] if e["file"] == "docs/existing/neighbor.md")
    assert neighbor["merge_evaluation"] == "邻居自己的净零自评"
    assert neighbor["capability"] == "anchor_cap"


def test_resolve_anchor_is_passthrough_shim(lab):
    """不变量③：锚点兼容垫片恒等返回（账本无插入锚语义）。"""
    assert bct.resolve_anchor("  capability: x\n", "wanted") == "wanted"
    assert bct.resolve_anchor("", "anything") == "anything"
