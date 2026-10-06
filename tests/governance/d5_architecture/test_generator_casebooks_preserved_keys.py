# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §casebooks-preserved-keys
# [MODULE] tests.governance.d5_architecture.test_generator_casebooks_preserved_keys
# [DOMAIN] D_GOV_SCRIPTS
# [TTL] permanent
# [DEPENDENCIES] pytest; yaml; pathlib;
#   scripts.governance.d5_architecture.generators._common（load_preserved_keys 单一真源）；
#   scripts.governance.d5_architecture.generators.generate_construction_workflow_map（图14）；
#   scripts.governance.d5_architecture.generators.generate_strategy_card_lifecycle_map（图15）
# [CONSUMERS] 两图生成器 casebooks 保留键机制（st-cbsurg-20261005 批）的回归证据面；
#   GOMAP _HUMAN_KEYS 机制（3d12a098）同族先例的图14/图15 接入证明
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 零真实仓库写入：两生成器 OUTPUT_PATH 一律 monkeypatch 到 tmp_path，
#   扫描面 root=真仓只读（禁写生产路径，宪法运维红线 6）；
#   规格两腿都钉——目标 yaml 带三键 → 重生成原样搬回值不变（重灌不吞人工值）；
#   目标 yaml 无三键 → 重生成不新增键（零输出变化，机生层零 diff）
# [MODIFY-GUARD] 改保留键集（_CASEBOOKS_KEYS）或装载语义（load_preserved_keys）必须同步本件
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=MOD-GOVERNANCE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
"""图14/图15 生成器 casebooks 保留键机制单元测试（st-cbsurg-20261005 批通管零内容）。

保留键规格（先例=GOMAP _HUMAN_KEYS 机制 3d12a098，装载单一真源=_common.load_preserved_keys）：
- 目标 yaml 带 casebooks/casebooks_note_zh/casebooks_legend_zh → 机生层全量重建时三键原样
  搬回（重灌不吞人工值）；
- 目标 yaml 无三键 → 重生成不新增键（零输出变化）——挂载值由人工批填，生成器禁伪造。

打桩法照 tests/test_generate_governance_map.py 的 _patch_head_tree 同族思路：不依赖 git 与
真实产出件，OUTPUT_PATH monkeypatch 到 tmp_path（本两件生成器的装载入口只有 OUTPUT_PATH，
无 HEAD 树依赖，无需额外打桩）。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "scripts" / "governance" / "d5_architecture" / "generators"))

import generate_construction_workflow_map as G14  # noqa: E402
import generate_strategy_card_lifecycle_map as G15  # noqa: E402
from d5_architecture.generators._common import load_preserved_keys  # noqa: E402

_MOUNTED = {
    "casebooks": [{"book_id": "CB-TEST-01", "mounts": ["D14-04", "D15-S6"]}],
    "casebooks_note_zh": "病历挂载注记（测试值，人工批填面）",
    "casebooks_legend_zh": "册码图例（测试值，人工批填面）",
}
_KEYS = ("casebooks", "casebooks_note_zh", "casebooks_legend_zh")


class TestLoadPreservedKeys:
    """装载单一真源的四边界（缺席/坏件/非对象/部分在册）。"""

    def test_missing_target_returns_empty(self, tmp_path):
        assert load_preserved_keys(tmp_path / "nope.yaml", _KEYS) == {}

    def test_broken_yaml_returns_empty(self, tmp_path):
        p = tmp_path / "bad.yaml"
        p.write_text("map_id: x\n  bad_indent: [1,2\n", encoding="utf-8")
        assert load_preserved_keys(p, _KEYS) == {}

    def test_non_object_top_returns_empty(self, tmp_path):
        p = tmp_path / "list.yaml"
        p.write_text("- a\n- b\n", encoding="utf-8")
        assert load_preserved_keys(p, _KEYS) == {}

    def test_only_registered_keys_copied_verbatim(self, tmp_path):
        p = tmp_path / "map.yaml"
        p.write_text(
            yaml.safe_dump({"casebooks": _MOUNTED["casebooks"], "casebooks_note_zh": "n", "unrelated": "x"}),
            encoding="utf-8",
        )
        got = load_preserved_keys(p, _KEYS)
        assert got == {"casebooks": _MOUNTED["casebooks"], "casebooks_note_zh": "n"}
        assert "unrelated" not in got and "casebooks_legend_zh" not in got


class TestFig14CasebooksPreservedKeys:
    """图14（construction_workflow_map）接入腿。"""

    def _build(self):
        return G14.build_document(as_of="2026-10-02T02:37:16+08:00", root=_REPO)

    def test_mounted_casebooks_survive_rebuild_verbatim(self, tmp_path, monkeypatch):
        out = tmp_path / "config" / "construction_workflow_map.yaml"
        monkeypatch.setattr(G14, "OUTPUT_PATH", out)
        doc1 = self._build()
        doc1["casebooks"] = _MOUNTED["casebooks"]
        doc1["casebooks_note_zh"] = _MOUNTED["casebooks_note_zh"]
        doc1["casebooks_legend_zh"] = _MOUNTED["casebooks_legend_zh"]
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(yaml.safe_dump(doc1, allow_unicode=True, sort_keys=False), encoding="utf-8")
        doc2 = self._build()
        assert doc2["casebooks"] == _MOUNTED["casebooks"]
        assert doc2["casebooks_note_zh"] == _MOUNTED["casebooks_note_zh"]
        assert doc2["casebooks_legend_zh"] == _MOUNTED["casebooks_legend_zh"]
        assert doc2["counts"] == doc1["counts"]  # 机生层仍全量重建，计数面零漂移

    def test_casebooks_absent_no_keys_emitted(self, tmp_path, monkeypatch):
        out = tmp_path / "config" / "construction_workflow_map.yaml"  # 不落盘=目标无三键
        monkeypatch.setattr(G14, "OUTPUT_PATH", out)
        doc = self._build()
        for k in _KEYS:
            assert k not in doc, f"目标 yaml 无 {k} 时生成器不得新增键（零输出变化）"


class TestFig15CasebooksPreservedKeys:
    """图15（strategy_card_lifecycle_map）接入腿。"""

    def _build(self):
        return G15.build_document(as_of="2026-09-26T00:00:00+08:00", root=_REPO)

    def test_mounted_casebooks_survive_rebuild_verbatim(self, tmp_path, monkeypatch):
        out = tmp_path / "config" / "strategy_card_lifecycle_map.yaml"
        monkeypatch.setattr(G15, "OUTPUT_PATH", out)
        doc1 = self._build()
        doc1["casebooks"] = _MOUNTED["casebooks"]
        doc1["casebooks_note_zh"] = _MOUNTED["casebooks_note_zh"]
        doc1["casebooks_legend_zh"] = _MOUNTED["casebooks_legend_zh"]
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(yaml.safe_dump(doc1, allow_unicode=True, sort_keys=False), encoding="utf-8")
        doc2 = self._build()
        assert doc2["casebooks"] == _MOUNTED["casebooks"]
        assert doc2["casebooks_note_zh"] == _MOUNTED["casebooks_note_zh"]
        assert doc2["casebooks_legend_zh"] == _MOUNTED["casebooks_legend_zh"]
        assert doc2["counts"] == doc1["counts"]  # 机生层仍全量重建，计数面零漂移

    def test_casebooks_absent_no_keys_emitted(self, tmp_path, monkeypatch):
        out = tmp_path / "config" / "strategy_card_lifecycle_map.yaml"  # 不落盘=目标无三键
        monkeypatch.setattr(G15, "OUTPUT_PATH", out)
        doc = self._build()
        for k in _KEYS:
            assert k not in doc, f"目标 yaml 无 {k} 时生成器不得新增键（零输出变化）"


if __name__ == "__main__":  # pragma: no cover  直跑=冒烟（pytest 才是正式入口）
    sys.exit(pytest.main([__file__, "-q"]))
