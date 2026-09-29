# [TESTS-FOR] scripts/governance/d3_metadata/check_registry_consistency.py（CR-007 口径派生 / CR-007c summary 标量 / CR-008 域册 ssot↔covers）
# [MODULE] tests.governance.test_registry_derivation_canary
# [DOMAIN] D_GOV_SCRIPTS
# [INVARIANTS] 每把新尺都带反事实红证：删一条目/改一个数⇒尺必红；喂一致数据⇒尺必绿；回填复跑零 diff
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即派生尺失效（计数退回手写）的证据
# [TESTS] self
# [TTL] task_bound
"""W-52/W-53 派生计数尺的 Canary（红证）。

三把尺各自「人为破坏 ⇒ 必红」「一致数据 ⇒ 必绿」：
  1. CR-007 口径派生（ROOR 本条 counting_rule 即口径真源，ENTRY_SPECS 降级为覆写）；
  2. CR-007c ROOR summary 派生标量对账；
  3. CR-008 功能域册 ssot_path ↔ covers 对账。
全部只读 tmp_path，不碰生产 docs/ 与 data/。
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
import yaml

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = _REPO_ROOT / "scripts" / "governance" / "d3_metadata" / "check_registry_consistency.py"


def _load_crc():
    if str(_SCRIPT.parent) not in sys.path:
        sys.path.insert(0, str(_SCRIPT.parent))
    spec = importlib.util.spec_from_file_location("crc_canary", _SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def crc():
    return _load_crc()


@pytest.fixture(scope="module")
def rec():
    sys.path.insert(0, str(_REPO_ROOT / "scripts" / "governance"))
    from _shared import registry_entry_count as mod  # noqa: PLC0415

    return mod


def _write(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


def _roor_text(reg1: Path, declared: int) -> str:
    return (
        "tiers:\n"
        "  - tier: 0\n"
        "    registries:\n"
        "      - registry_id: REG-CANARY-001\n"
        f"        physical_path: {reg1.as_posix()}\n"
        f"        entry_count: {declared}\n"
        "        counting_rule: vocabularies 数组条目数\n"
        "        status: active\n"
    )


def _vocab_text(n: int) -> str:
    items = "\n".join(f"  - vocabulary_id: VOC-{i:03d}" for i in range(n))
    return f"registry_id: REG-CANARY-001\nvocabularies:\n{items}\n"


# ── 尺 1：CR-007 口径派生（不再依赖手工 ENTRY_SPECS）──────────────────────


def test_cr007_derives_from_counting_rule_green(crc, tmp_path, monkeypatch):
    """一致数据⇒绿：ENTRY_SPECS 空表也能由 ROOR 自述 counting_rule 数出真值。"""
    reg1 = _write(tmp_path / "reg1.yaml", _vocab_text(5))
    roor = _write(tmp_path / "roor.yaml", _roor_text(reg1, 5))
    monkeypatch.setattr(crc, "ENTRY_SPECS", {})
    monkeypatch.setattr(crc, "ENTRY_MANUAL", {})
    rows = crc.verify_entry_counts(roor)
    assert [r["verdict"] for r in rows] == ["MATCH"]


def test_cr007_red_when_one_entry_deleted(crc, tmp_path, monkeypatch):
    """红证：真源册删一条词表 ⇒ 在册 entry_count 立刻判 STALE（旧行为是 UNSPECIFIED 静默）。"""
    reg1 = _write(tmp_path / "reg1.yaml", _vocab_text(5))
    roor = _write(tmp_path / "roor.yaml", _roor_text(reg1, 5))
    monkeypatch.setattr(crc, "ENTRY_SPECS", {})
    monkeypatch.setattr(crc, "ENTRY_MANUAL", {})
    _write(reg1, _vocab_text(4))  # 人为删一行
    row = crc.verify_entry_counts(roor)[0]
    assert row["verdict"] == "STALE"
    assert (row["expected"], row["actual"]) == (5, 4)


def test_cr007_red_when_declared_number_tampered(crc, tmp_path, monkeypatch):
    """红证：在册数字被手改一个数 ⇒ 必红（派生值不随散文走）。"""
    reg1 = _write(tmp_path / "reg1.yaml", _vocab_text(7))
    roor = _write(tmp_path / "roor.yaml", _roor_text(reg1, 29))
    monkeypatch.setattr(crc, "ENTRY_SPECS", {})
    monkeypatch.setattr(crc, "ENTRY_MANUAL", {})
    assert crc.verify_entry_counts(roor)[0]["verdict"] == "STALE"


def test_cr007_backfill_idempotent(crc, tmp_path, monkeypatch):
    """幂等：回填后复跑零 diff（第二次 apply 返回空、文本字节不变）。"""
    reg1 = _write(tmp_path / "reg1.yaml", _vocab_text(6))
    roor = _write(tmp_path / "roor.yaml", _roor_text(reg1, 29))
    monkeypatch.setattr(crc, "ENTRY_SPECS", {})
    monkeypatch.setattr(crc, "ENTRY_MANUAL", {})
    first = crc.apply_roor_entry_count_updates(crc.verify_entry_counts(roor), roor)
    assert first == ["REG-CANARY-001: 29 -> 6"]
    after_first = roor.read_text(encoding="utf-8")
    assert all(r["verdict"] == "MATCH" for r in crc.verify_entry_counts(roor))
    assert crc.apply_roor_entry_count_updates(crc.verify_entry_counts(roor), roor) == []
    assert roor.read_text(encoding="utf-8") == after_first


# ── 尺 2：CR-007c ROOR summary 派生标量 ────────────────────────────────────


def _summary_roor(reg1: Path, total: int) -> str:
    entries = [
        {"registry_id": f"REG-CANARY-{i:03d}", "status": "active", "physical_path": reg1.as_posix()}
        for i in range(total)
    ]
    return yaml.safe_dump(
        {
            "tiers": [{"tier": 0, "registries": entries}],
            "summary": {
                "total_tiers": 1,
                "total_registries": total,
                "by_tier": {"tier_0": total},
                "by_status": {"active": total},
                "by_medium": {"ok": total},
                "broken": 0,
                "entries_carrying_tier_field": {},
            },
        },
        allow_unicode=True,
        sort_keys=False,
    )


def test_summary_green_when_consistent(crc, tmp_path):
    """一致数据⇒绿：summary 七个派生字段全 MATCH。"""
    reg1 = _write(tmp_path / "reg1.yaml", _vocab_text(1))
    roor = _write(tmp_path / "roor.yaml", _summary_roor(reg1, 2))
    assert {r["verdict"] for r in crc.verify_roor_summary(roor)} == {"MATCH"}


def test_summary_red_when_one_entry_deleted(crc, tmp_path):
    """红证：tiers 里删一条目 ⇒ total_registries/by_tier/by_status/by_medium 四标量同红。"""
    reg1 = _write(tmp_path / "reg1.yaml", _vocab_text(1))
    roor = _write(tmp_path / "roor.yaml", _summary_roor(reg1, 3))
    data = yaml.safe_load(roor.read_text(encoding="utf-8"))
    data["tiers"][0]["registries"].pop()  # 人为删一行条目，summary 不跟着改
    roor.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8", newline="\n")
    bad = {r["field"]: r for r in crc.verify_roor_summary(roor) if r["verdict"] != "MATCH"}
    assert {"total_registries", "by_tier", "by_status", "by_medium"} <= set(bad)
    assert bad["total_registries"]["expected"] == 3 and bad["total_registries"]["actual"] == 2


def test_summary_computation_is_stable(crc, tmp_path):
    """再生器幂等：同一册连算两次结果全等（写盘再复跑零 diff 的前半段证明）。"""
    reg1 = _write(tmp_path / "reg1.yaml", _vocab_text(1))
    roor = _write(tmp_path / "roor.yaml", _summary_roor(reg1, 2))
    data = yaml.safe_load(roor.read_text(encoding="utf-8"))
    assert crc.compute_roor_summary(data) == crc.compute_roor_summary(data)


# ── 尺 3：CR-008 功能域册 ssot_path ↔ covers ──────────────────────────────

_DOM_TMPL = """entries:
  - domain: D_CANARY
    subdomain: sd
    covers:
      - "编排({sym})"
    ssot_path: {path}
"""


def test_domain_ssot_green(crc, tmp_path):
    """一致数据⇒绿：真源存在且 covers 符号在其中可寻。"""
    src = _write(tmp_path / "mod.py", "class CanaryController:\n    pass\n")
    reg = _write(tmp_path / "domain.yaml", _DOM_TMPL.format(sym="CanaryController", path=src.as_posix()))
    assert crc.verify_domain_ssot(reg, check_covers=True) == []


def test_domain_ssot_red_when_path_missing(crc, tmp_path):
    """红证：真源路径不存在（改名/删库的等价态）⇒ PATH_MISSING。"""
    ghost = (tmp_path / "renamed_away" / "mod.py").as_posix()
    reg = _write(tmp_path / "domain.yaml", _DOM_TMPL.format(sym="CanaryController", path=ghost))
    rows = crc.verify_domain_ssot(reg)
    assert [r["verdict"] for r in rows] == ["PATH_MISSING"]


def test_domain_ssot_red_when_covered_symbol_moved(crc, tmp_path):
    """红证：covers 说它管 CanaryController，源码里类被改名 ⇒ COVERS_UNFOUND。"""
    src = _write(tmp_path / "mod.py", "class CanaryControllerV2:\n    pass\n")
    reg = _write(tmp_path / "domain.yaml", _DOM_TMPL.format(sym="CanaryController", path=src.as_posix()))
    rows = crc.verify_domain_ssot(reg, check_covers=True)
    assert [r["verdict"] for r in rows] == ["COVERS_UNFOUND"]
    assert "CanaryController" in rows[0]["detail"]


def test_domain_ssot_red_on_placeholder_path(crc, tmp_path):
    """红证：ssot_path 写成括注说明（非路径）⇒ PATH_UNDECLARED，不许当'没这条'混过。"""
    reg = _write(tmp_path / "domain.yaml", _DOM_TMPL.format(sym="CanaryController", path="(depgraph 里为空)"))
    assert [r["verdict"] for r in crc.verify_domain_ssot(reg)] == ["PATH_UNDECLARED"]


def test_domain_ssot_does_not_cry_wolf_on_prose_tokens(crc, tmp_path):
    """尺不许自哭狼：covers 里的散文层级标签（L1 Trae/L2 Local）不是类名，不得报红。"""
    src = _write(tmp_path / "mod.py", "class RuntimeCore:\n    pass\n")
    text = _DOM_TMPL.format(sym="RuntimeCore", path=src.as_posix()).replace(
        "编排(RuntimeCore)", "三层运行时编排(L1 Trae/L2 Local/L3 API)\n      - 编排(RuntimeCore)"
    )
    reg = _write(tmp_path / "domain.yaml", text)
    assert crc.verify_domain_ssot(reg, check_covers=True) == []
    # 而真正的符号失配仍必须红（同一括号语法，只是类名不存在）
    reg2 = _write(tmp_path / "domain2.yaml", _DOM_TMPL.format(sym="RenamedAway", path=src.as_posix()))
    assert [r["verdict"] for r in crc.verify_domain_ssot(reg2, check_covers=True)] == ["COVERS_UNFOUND"]


# ── 尺 1b：_shared.registry_entry_count 口径文本解析（生成器共用真源）──────


@pytest.mark.parametrize(
    ("rule", "expected"),
    [
        ("vocabularies 数组条目数", ("yaml_list", "vocabularies")),
        ("entries 条目数（含 deprecated 全量）", ("yaml_list", "entries")),
        ("detectors.existing + detectors.new 条目数合计", ("yaml_sum", "detectors.existing+detectors.new")),
        ("systems 子系统数", ("yaml_dict_len", "systems")),
        ("meta_question 主表行数（快照头部 row_count 字段）", None),
        ("", None),
    ],
)
def test_parse_counting_rule(rec, rule, expected):
    """口径文本只认显式声明；解析不出就返回 None（禁"最长 list"启发式）。"""
    assert rec.parse_counting_rule(rule) == expected


def test_master_index_count_follows_declared_key(rec, tmp_path):
    """绿证+红证：主索引计数改由声明口径派生——册内自述或 ROOR 带来的口径都认；删一条即少一个。"""
    data = yaml.safe_load(_vocab_text(5))
    in_file = yaml.safe_load(_vocab_text(5) + "counting_rule: vocabularies 数组条目数\n")
    stem = (tmp_path / "state_vocabulary_registry.yaml").stem
    assert rec.count_primary_registry_entries(in_file, stem) == 5  # 册内自述
    assert rec.count_primary_registry_entries(data, stem, "vocabularies 数组条目数") == 5  # ROOR 传入
    assert rec.count_primary_registry_entries(yaml.safe_load(_vocab_text(4)), stem, "vocabularies 数组条目数") == 4
    assert rec.primary_count_entry_key(in_file, stem) == "vocabularies"
    # 无声明的册不受影响（仍走既有手工键白名单）
    assert rec.count_primary_registry_entries({"entries": [1, 2]}, "whatever") == 2
    # 口径键面不符 ⇒ 不虚报（返回 0 让对账侧报 UNSPECIFIED，而不是猜一个数）
    bogus = yaml.safe_load(_vocab_text(5) + "counting_rule: nosuchkey 数组条目数\n")
    assert rec.count_primary_registry_entries(bogus, stem) == 0
