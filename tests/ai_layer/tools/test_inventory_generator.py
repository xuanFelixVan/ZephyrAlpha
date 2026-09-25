"""test_inventory_generator — C1 五源聚合/删除闸拒产出/幂等双跑/坏卡留痕/词表 total 护栏。

测试隔离：全部输入=tmp_path 构造，零生产路径写入（capability_cards/mcp.json 只读真源
另有一条只读断言，不写）。
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from zephyr.ai_layer.tools import (
    DELETE_CLASSES,
    KINDS,
    ORGANS,
    SAFETY_LEVELS,
    STAT_SOURCES,
    STATUSES,
)
from zephyr.ai_layer.tools.inventory_generator import (
    DELETE_CLASS_BY_TOKEN,
    DELETION_TOKENS,
    MUTATION_TOKENS,
    OBSERVE_TOKENS,
    InventoryError,
    _collect_scripts,
    _render_report,
    _script_family,
    build_inventory,
    content_sha256,
    generate,
)

# ---------------------------------------------------------------------------
# 词表护栏（生成器自有知识 total 映射；package 词表与 DESIGN §2.1 同源）
# ---------------------------------------------------------------------------

def test_deletion_token_class_map_is_total() -> None:
    assert set(DELETION_TOKENS) == set(DELETE_CLASS_BY_TOKEN)
    assert all(c in DELETE_CLASSES for c in DELETE_CLASS_BY_TOKEN.values())


def test_package_vocab() -> None:
    assert ORGANS == ("hand", "eye", "foot")
    assert "manual_v0" in STAT_SOURCES          # 计量缺口兜底词（DESIGN §1⑥）
    assert {"script", "skill", "mcp_server", "builtin", "card"} <= set(KINDS)
    assert isinstance(SAFETY_LEVELS, tuple) and len(SAFETY_LEVELS) >= 3 and {"L", "M", "H"} <= set(SAFETY_LEVELS)
    assert set(STATUSES) == {"active", "trial", "tombstone"}


@pytest.mark.parametrize(
    ("stem", "family"),
    [
        ("cleanup_tmp", "删除"),
        ("purge_old", "删除"),
        ("battle_map_coverage_audit", "观测"),   # 子串误伤回归：battle 不含整词 ttl
        ("run_post_settlement", "执行"),          # settlement 不含整词 ttl
        ("generate_manifest", "修改"),
        ("check_depgraph", "观测"),
        ("git_commit", "执行"),
    ],
)
def test_script_family_token_matching(stem: str, family: str) -> None:
    assert _script_family(stem) == family


# ---------------------------------------------------------------------------
# 五源聚合（tmp_path 构造）
# ---------------------------------------------------------------------------

def _make_world(tmp_path: Path) -> dict[str, Path]:
    cards = tmp_path / "capability_cards"
    cards.mkdir()
    (cards / "skill_dom_tst_001.yaml").write_text(
        yaml.safe_dump({
            "module_id": "MOD-X", "capability_id": "skill-dom-tst-001",
            "name": "Skill: test", "status": "ACTIVE",
        }, allow_unicode=True), encoding="utf-8")
    (cards / "broken.yaml").write_text("key: [unclosed\n", encoding="utf-8")
    (cards / "not_a_card.yaml").write_text("foo: bar\n", encoding="utf-8")

    mcp = tmp_path / "mcp.json"
    mcp.write_text(json.dumps({"servers": {
        "task_manager": {"tool_count": 6, "safety_level": ["L", "M", "H"],
                          "transport": "FastMCP"},
        "vector_memory": {"tool_count": 2, "safety_level": ["L", "M"]},
    }}), encoding="utf-8")

    contracts = tmp_path / "tool_contracts.yaml"
    contracts.write_text(yaml.safe_dump({
        "task_manager": {"server_id": "task_manager", "stability": "stable"},
        "vector-memory": {"server_id": "vector-memory", "stability": "beta"},  # 连字符拼写同件
        "resource_optimization": {"server_id": "resource_optimization"},       # 仅契约=设计预留
    }, allow_unicode=True), encoding="utf-8")

    scripts = tmp_path / "scripts"
    scripts.mkdir()
    for name in ("git_commit.py", "cleanup_tmp.py", "check_thing.py"):
        (scripts / name).write_text("# entry\n", encoding="utf-8")
    return {"cards": cards, "mcp": mcp, "contracts": contracts, "scripts": scripts}


def test_five_sources_aggregated(tmp_path: Path) -> None:
    w = _make_world(tmp_path)
    skills = tmp_path / "cache" / "plugins" / "p1" / "0.4.2" / "skills" / "alpha"
    skills.mkdir(parents=True)
    (skills / "SKILL.md").write_text("# s\n", encoding="utf-8")
    newer = tmp_path / "cache" / "plugins" / "p1" / "0.5.1" / "skills" / "alpha"
    newer.mkdir(parents=True)
    (newer / "SKILL.md").write_text("# s\n", encoding="utf-8")

    doc = build_inventory(
        cards_dir=w["cards"], mcp_path=w["mcp"], contracts_path=w["contracts"],
        scripts_dir=w["scripts"], skill_roots=(tmp_path / "cache",),
    )
    ids = [t["tool_id"] for t in doc["tools"]]
    assert len(ids) == len(set(ids))                      # 幂等去重
    assert "card:skill-dom-tst-001" in ids                # S1 卡索引
    assert "mcp:task_manager" in ids                      # S2
    assert "mcp:vector_memory" in ids                     # S3 归一同件（连字符/下划线）
    assert "mcp:resource_optimization" in ids             # 仅契约=trial
    doc_by_id = {t["tool_id"]: t for t in doc["tools"]}
    assert doc_by_id["mcp:vector_memory"]["status"] == "active"          # mcp.json 优先
    assert doc_by_id["mcp:vector_memory"]["meta"].get("contract_spelling") == "vector-memory"
    assert doc_by_id["mcp:resource_optimization"]["status"] == "trial"   # 设计预留
    assert doc_by_id["mcp:task_manager"]["safety_level"] == "H"          # 申报档位保守取高
    assert "skill:p1:alpha" in ids                        # S4 多版本取新一
    assert ids.count("skill:p1:alpha") == 1
    assert "script:cleanup_tmp" in ids                    # S5
    assert doc_by_id["script:cleanup_tmp"]["delete_class"] == "ttl_only"
    assert doc_by_id["script:cleanup_tmp"]["safety_level"] == "H"
    assert "builtin:WebSearch" in ids                     # S4 附录内建
    # 坏卡/非卡 fail-open 留痕
    warns = "\n".join(doc["extraction_warnings"])
    assert "bad_card_yaml:broken.yaml" in warns and "not_a_card:not_a_card.yaml" in warns
    # 运营态字段恒 null（真源=DB，不虚构计量）
    for t in doc["tools"]:
        assert t["usage_30d"] is None and t["stat_source"] is None
    # 哈希锁自洽
    assert content_sha256(doc) == doc["content_sha256"]


def test_missing_source_fails_closed(tmp_path: Path) -> None:
    w = _make_world(tmp_path)
    with pytest.raises(InventoryError, match="mcp.json 不存在"):
        build_inventory(cards_dir=w["cards"], mcp_path=tmp_path / "nope.json",
                        contracts_path=w["contracts"], scripts_dir=w["scripts"],
                        skill_roots=(tmp_path / "cache",))


def test_deletion_gate_rejects_unmapped(tmp_path: Path) -> None:
    """登记闸（DESIGN §6.1 接口点1）：删除判词命中但判级缺失=拒产出（fail-closed）。"""
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "explode_cache.py").write_text("# x\n", encoding="utf-8")
    with pytest.raises(InventoryError, match="explode_cache"):
        _collect_scripts(scripts, extra_deletion_tokens=("explode",))


def test_deletion_gate_ambiguous_class_rejected(tmp_path: Path) -> None:
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "retire_and_purge.py").write_text("# x\n", encoding="utf-8")  # tombstone+owner_gated
    with pytest.raises(InventoryError, match="ambiguous_delete_class"):
        _collect_scripts(scripts)


# ---------------------------------------------------------------------------
# 幂等与落盘
# ---------------------------------------------------------------------------

def test_idempotent_double_run(tmp_path: Path) -> None:
    w = _make_world(tmp_path)
    kwargs = dict(cards_dir=w["cards"], mcp_path=w["mcp"], contracts_path=w["contracts"],
                  scripts_dir=w["scripts"], skill_roots=(tmp_path / "cache",))
    doc1 = build_inventory(**kwargs)
    doc2 = build_inventory(**kwargs)
    assert doc1["content_sha256"] == doc2["content_sha256"]


def test_generate_writes_yaml_and_report(tmp_path: Path) -> None:
    """generate 落盘：YAML 可解析+报告内容一致（generated_at 时间戳行除外）零生产路径写入。"""
    out = tmp_path / "out" / "tool_inventory.yaml"
    report = tmp_path / "out" / "report.md"
    doc = generate(out_path=out, report_path=report)
    loaded = yaml.safe_load(out.read_text(encoding="utf-8"))
    assert loaded["total_tools"] == doc["total_tools"]
    assert loaded["content_sha256"] == doc["content_sha256"]
    text = report.read_text(encoding="utf-8")
    strip_ts = lambda s: "\n".join(l for l in s.splitlines() if not l.startswith("generated_at"))
    assert strip_ts(_render_report(doc)) == strip_ts(text)
    assert "content_sha256" in text and "snapshot" in text


def test_repo_real_sources_readonly_snapshot() -> None:
    """只读真源快照断言：卡源非空+删除族（若在档）必带 delete_class（不写盘）。"""
    doc = build_inventory()
    assert doc["source_counts"]["capability_cards"] >= 1
    assert doc["source_counts"]["mcp_servers"] >= 1
    for t in doc["tools"]:
        if t["family"] == "删除":
            assert t["delete_class"] in DELETE_CLASSES
        assert t["organ"] in ORGANS or t["organ"] is None
