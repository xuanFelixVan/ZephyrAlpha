# [MODULE] tests.ai_layer.perceive.test_veins
# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_perceive
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
"""施工项 3 验收机检面：地图节点全量派生/再生幂等/增删改语义（墓碑粘滞）/TDM 域辅助轴。

生成器为 scripts 自包含件（conftest 同款 importlib 装载先例）；产物写 tmp_path，零生产路径。
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import yaml

REPO = Path(__file__).resolve().parents[3]
GEN_SCRIPT = REPO / "scripts" / "ai_layer" / "gen_search_veins.py"


def _load_gen() -> ModuleType:
    spec = importlib.util.spec_from_file_location("gen_search_veins_under_test", GEN_SCRIPT)
    assert spec and spec.loader, f"无法装载生成器: {GEN_SCRIPT}"
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _write_map(path: Path, node_ids: list[str]) -> Path:
    nodes = [
        {
            "node_id": nid,
            "name_zh": f"节点{nid}",
            "stage": "E6",
            "node_type": "stage",
            "decision_question": f"{nid} 的决策问题？\n第二行也要折叠",
            "algo_note_zh": "注记第一句\n注记第二句",
            "module_ref": "MOD-X",
        }
        for nid in node_ids
    ]
    path.write_text(
        yaml.safe_dump({"schema_version": "0.2", "nodes": nodes}, allow_unicode=True),
        encoding="utf-8",
    )
    return path


def _write_domains(path: Path) -> Path:
    path.write_text(
        yaml.safe_dump(
            {
                "entries": [
                    {"domain": "D_B", "domain_name_zh": "乙域", "subdomain": "s"},
                    {"domain": "D_A", "domain_name_zh": "甲域", "subdomain": "s"},
                    {"domain": "D_A", "domain_name_zh": "甲域", "subdomain": "t"},
                ]
            },
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    return path


def test_derive_map_veins_full_and_fields(tmp_path: Path) -> None:
    """验收原文：地图节点全量派生（真实地图 16 节点）；vein_id/vein_family/关键词种子逐字段对。"""
    gen = _load_gen()
    map_raw = yaml.safe_load(gen.DEFAULT_MAP_PATH.read_text(encoding="utf-8"))
    node_count = len(map_raw["nodes"])
    veins = gen.derive_map_veins(map_raw)
    assert len(veins) == node_count == 16
    by_id = {v["vein_id"]: v for v in veins}
    e6 = by_id["VEIN-FAC-E6"]
    assert e6["vein_family"] == "E6"
    assert e6["keyword_seed"].startswith("入库的策略还活着吗")
    assert "\n" not in e6["keyword_seed"] and "\n" not in e6["note_excerpt"]
    assert e6["derived_from"] == "strategy_production_map#FAC-E6"
    assert e6["priority"] == 1.0 and e6["status"] == "active"
    e1a = by_id["VEIN-FAC-E1A"]
    assert e1a["vein_family"] == "E1"  # lane 节点族=stage（E1）


def test_card_veins_derivation_and_filter(tmp_path: Path) -> None:
    """段卡清单派生（L*/OBJ_* 有 DESIGN.md 才派生；V* 挖矿报告不派生）。"""
    gen = _load_gen()
    l2 = tmp_path / "L2_intake_library"
    l2.mkdir()
    (l2 / "DESIGN.md").write_text(
        "---\ntitle: L2 收集段——原材料库 真源设计稿 v1\nstatus: design_v1\n---\n# 正文",
        encoding="utf-8",
    )
    v2 = tmp_path / "V2_evolution_loop"
    v2.mkdir()
    (v2 / "DESIGN.md").write_text("---\ntitle: 挖矿报告\n---\n", encoding="utf-8")
    orphan = tmp_path / "L9_ghost"  # 段卡目录缺 DESIGN.md → 跳过
    orphan.mkdir()
    veins = gen.derive_card_veins(tmp_path)
    assert len(veins) == 1
    assert veins[0]["vein_id"] == "VEIN-AI-L2"
    assert veins[0]["vein_family"] == "ai_layer"
    assert "原材料库" in veins[0]["keyword_seed"]


def test_regeneration_idempotent_bytes(tmp_path: Path) -> None:
    """验收原文：再生幂等——同输入两次落盘逐字节一致（产物零墙钟时间戳）。"""
    gen = _load_gen()
    out = tmp_path / "veins.yaml"
    first = gen.build_artifact(out_path=out)
    gen.write_artifact(first, out)
    snapshot = out.read_bytes()
    second = gen.build_artifact(out_path=out)  # 读回自身做墓碑源
    gen.write_artifact(second, out)
    assert out.read_bytes() == snapshot
    assert first["total_veins"] == second["total_veins"]
    assert first["veins"] == second["veins"]


def test_node_removal_archives_tombstone_and_sticky(tmp_path: Path) -> None:
    """验收原文（§2.5.3）：节点退役→矿脉标 archived 墓碑不删除；且粘滞（再生不自动复活）。"""
    gen = _load_gen()
    map_path = _write_map(tmp_path / "map.yaml", ["FAC-X1", "FAC-X2"])
    domains = _write_domains(tmp_path / "domains.yaml")
    out = tmp_path / "veins.yaml"
    artifact = gen.build_artifact(
        map_path=map_path, cards_root=tmp_path / "no_cards", domains_path=domains, out_path=out
    )
    assert {v["vein_id"] for v in artifact["veins"]} == {"VEIN-FAC-X1", "VEIN-FAC-X2"}
    gen.write_artifact(artifact, out)
    # 退役 FAC-X2
    _write_map(map_path, ["FAC-X1"])
    after = gen.build_artifact(
        map_path=map_path, cards_root=tmp_path / "no_cards", domains_path=domains, out_path=out
    )
    by_id = {v["vein_id"]: v for v in after["veins"]}
    assert by_id["VEIN-FAC-X2"]["status"] == "archived"
    assert by_id["VEIN-FAC-X2"]["tombstone_reason"] == "absent_from_skeleton"
    assert by_id["VEIN-FAC-X1"]["status"] == "active"
    gen.write_artifact(after, out)
    # 粘滞：节点仍缺席，再生保持 archived 且逐字节稳定
    again = gen.build_artifact(
        map_path=map_path, cards_root=tmp_path / "no_cards", domains_path=domains, out_path=out
    )
    gen.write_artifact(again, out)
    assert again["veins"] == after["veins"]


def test_domain_axis_is_index_not_veins(tmp_path: Path) -> None:
    """TDM 域落辅助轴索引（63 域独立矿脉=噪音，偏离留痕）：domain_axis 去重排序，veins 不含域行。"""
    gen = _load_gen()
    map_path = _write_map(tmp_path / "map.yaml", ["FAC-Y1"])
    domains = _write_domains(tmp_path / "domains.yaml")
    artifact = gen.build_artifact(
        map_path=map_path, cards_root=tmp_path / "no_cards", domains_path=domains,
        out_path=tmp_path / "veins.yaml",
    )
    assert artifact["domain_axis"] == [
        {"domain": "D_A", "name_zh": "甲域"},
        {"domain": "D_B", "name_zh": "乙域"},
    ]
    assert all(not v["vein_id"].startswith("VEIN-D_") for v in artifact["veins"])


def test_cli_dry_run_writes_nothing(tmp_path: Path) -> None:
    gen = _load_gen()
    out = tmp_path / "should_not_exist.yaml"
    rc = gen.main(["--map", str(gen.DEFAULT_MAP_PATH), "--domains", str(gen.DEFAULT_DOMAINS_PATH),
                   "--cards-root", str(tmp_path / "no_cards"), "--out", str(out), "--dry-run"])
    assert rc == 0
    assert not out.exists()


def test_cli_full_run_real_inputs_to_tmp(tmp_path: Path) -> None:
    """真实地图+域注册表全量试跑（产物落 tmp_path，零生产路径写入）。"""
    gen = _load_gen()
    out = tmp_path / "veins.yaml"
    rc = gen.main([
        "--map", str(gen.DEFAULT_MAP_PATH),
        "--domains", str(gen.DEFAULT_DOMAINS_PATH),
        "--cards-root", str(gen.DEFAULT_CARDS_ROOT),
        "--out", str(out),
    ])
    assert rc == 0
    artifact = yaml.safe_load(out.read_text(encoding="utf-8"))
    assert artifact["total_veins"] >= 16  # 16 地图矿脉 + 段卡矿脉
    assert artifact["active_veins"] == artifact["total_veins"]
    assert len(artifact["domain_axis"]) >= 50  # 63 域去重后
