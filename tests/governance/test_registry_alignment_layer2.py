# [BLUEPRINT] MOD-D5_ARCH_TOOLS | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# -*- coding: utf-8 -*-
"""注册表对齐第二层回归测试（全图全库对齐满贯施工 2026-09-11）。

锁定 registry_alignment.py（第二层唯一逻辑真源）的五个校验函数基线 + 两个
commit gate 的红蓝行为。基线红线（任一变红=对齐回退，禁止直接改断言放水——
先修数据，走 shared 校验函数定位违规清单）：
- 19 文件/21 段 1463 条目：id 唯一 + module_id MOD-* + depgraph 存在（fail-open）
- 字段字典 FK 悬空 = 0
- CAND 转正链幽灵锚 = 0
- 治理库双向悬空 = 0
- 产业链字典结构四边违规 = 0
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from zephyr.gov_enforcement.registry_alignment import (  # noqa: E402
    CATALOGS_DIR,
    REGISTRY_SPECS,
    RegistrySpec,
    check_candidate_promotion_chain,
    check_field_dictionary_fk,
    check_governance_bidirectional,
    check_industry_graph_field_dictionary,
    run_all_registry_validations,
    validate_registry_file,
)
from zephyr.gov_enforcement.commit_gates.business_registry_gate import (  # noqa: E402
    make_business_registry_gate,
)
from zephyr.gov_enforcement.commit_gates.industry_chain_map_gate import (  # noqa: E402
    make_industry_chain_map_gate,
)


# ── 基线绿测（数据回退即红）───────────────────────────────────────────


def test_specs_cover_21_sections():
    assert len(REGISTRY_SPECS) == 21
    files = {s.filename for s in REGISTRY_SPECS}
    assert len(files) == 19, f"满贯应为 19 文件，实际 {len(files)}"


def test_all_registries_pass_full_validation():
    fails, total = run_all_registry_validations(include_depgraph=True)
    assert not fails, f"注册表对齐基线回退 {len(fails)} 项:\n" + "\n".join(fails[:20])
    assert total >= 1460, f"条目总量异常收缩: {total}"


def test_field_dictionary_fk_closure():
    errors, _ = check_field_dictionary_fk()
    assert not errors, "字段字典 FK 悬空回退:\n" + "\n".join(errors[:20])


def test_candidate_promotion_chain_no_ghost_anchors():
    errors, _ = check_candidate_promotion_chain()
    assert not errors, "CAND 转正链幽灵锚点回退:\n" + "\n".join(errors[:20])


def test_governance_bidirectional_closure():
    errors, _ = check_governance_bidirectional()
    assert not errors, "治理库双向关联回退:\n" + "\n".join(errors[:20])


def test_industry_graph_field_dictionary_structure():
    errors, _ = check_industry_graph_field_dictionary()
    assert not errors, "产业链字段字典结构四边回退:\n" + "\n".join(errors[:20])


# ── validate_registry_file 红测（tmp 构造，不触真源）──────────────────


def _write_registry(tmp_path: Path, entries: list[dict]) -> tuple[Path, RegistrySpec]:
    path = tmp_path / "demo_registry.yaml"
    path.write_text(yaml.safe_dump({"demos": entries}, allow_unicode=True), encoding="utf-8")
    spec = RegistrySpec("demo_registry.yaml", "demos", "demo_id", "演示库")
    return path, spec


def test_validate_catches_duplicate_id(tmp_path: Path):
    path, spec = _write_registry(
        tmp_path,
        [
            {"demo_id": "DEMO-001", "module_id": "MOD-L02-001"},
            {"demo_id": "DEMO-001", "module_id": "MOD-L02-001"},
        ],
    )
    fails = validate_registry_file(path, spec)
    assert any("重复" in f for f in fails)


def test_validate_catches_missing_module_id(tmp_path: Path):
    path, spec = _write_registry(tmp_path, [{"demo_id": "DEMO-001"}])
    fails = validate_registry_file(path, spec)
    assert any("缺 module_id" in f for f in fails)


def test_validate_catches_bad_module_format(tmp_path: Path):
    path, spec = _write_registry(tmp_path, [{"demo_id": "DEMO-001", "module_id": "factor"}])
    fails = validate_registry_file(path, spec)
    assert any("非 MOD-* 格式" in f for f in fails)


def test_validate_clean_ok(tmp_path: Path):
    path, spec = _write_registry(tmp_path, [{"demo_id": "DEMO-001", "module_id": "MOD-L02-001"}])
    assert validate_registry_file(path, spec) == []


# ── gate 行为（触发/放行/红蓝）───────────────────────────────────────


def test_business_gate_non_registry_files_pass():
    gate = make_business_registry_gate()
    ok, msg = gate.check(None, files=["src/zephyr/foo.py"])
    assert ok and msg == ""


def test_business_gate_blocks_bad_entry(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """红测：staged 库文件含坏条目时阻断（monkeypatch catalogs 目录）。"""
    import zephyr.gov_enforcement.commit_gates.business_registry_gate as brg

    bad_dir = tmp_path / "catalogs"
    bad_dir.mkdir()
    (bad_dir / "universe_registry.yaml").write_text(
        yaml.safe_dump(
            {
                "universes": [
                    {"universe_id": "UNI-TEST-999", "module_id": "MOD-L02-001"},
                    {"universe_id": "UNI-TEST-999", "module_id": "MOD-L02-001"},
                ]
            },
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(brg, "_CATALOGS_DIR", bad_dir)
    gate = make_business_registry_gate()
    ok, msg = gate.check(None, files=["docs/01_policies_and_standards/_registry/catalogs/universe_registry.yaml"])
    assert ok is False
    assert "重复" in msg


def test_industry_gate_triggers_on_dictionary():
    gate = make_industry_chain_map_gate()
    ok, _ = gate.check(
        None,
        files=["docs/01_policies_and_standards/_registry/catalogs/industry_graph_field_dictionary.yaml"],
    )
    assert ok is True  # 基线干净 → 触发但通过


def test_industry_gate_ignores_unrelated_files():
    gate = make_industry_chain_map_gate()
    ok, msg = gate.check(None, files=["README.md"])
    assert ok and msg == ""


def test_industry_gate_blocks_bad_cluster_names(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """红测：簇名词表键格式/族名超长阻断。"""
    import zephyr.gov_enforcement.commit_gates.industry_chain_map_gate as icg

    bad_cfg = tmp_path / "config" / "chainmap_cluster_names.yaml"
    bad_cfg.parent.mkdir(exist_ok=True)
    bad_cfg.write_text(
        yaml.safe_dump({"X99": "超长族名测试超过六字", "C01": "ok"}, allow_unicode=True),
        encoding="utf-8",
    )
    monkeypatch.setattr(icg, "_REPO_ROOT", tmp_path)
    gate = make_industry_chain_map_gate()
    ok, msg = gate.check(None, files=["config/chainmap_cluster_names.yaml"])
    assert ok is False
    assert "C<N>" in msg and "超 6 字" in msg
