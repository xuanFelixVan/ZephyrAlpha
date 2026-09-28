# [BLUEPRINT] MOD-BT-171 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_weight_ssot_single_authority
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts.backtest.weight_ssot; scripts.backtest.auto_mount
# [CONSUMERS] R-M2-6 配比真源单头化验收面
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 测试隔离（tmp_path fixture，禁写生产路径/禁碰资金表）；红测必自证能红；
#   本文件只判"谁有权定配比"，不得改动任何权重数值或风险平价/再平衡判据；
#   资金面红线：零调用任何下单/调仓/撮合路径
# [MODIFY-GUARD] scripts/backtest/weight_ssot.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] WeightAuthorityError/RuntimeError=判权越权（非资金异常）
# [TESTS] 本文件
# [A_module] module_id=MOD-BT-171 | layer=test | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""R-M2-6 配比真源单头化红测：提名≠生效 + 同一权重两处写必被探出。

两枚主尺（任务书要求）：
  尺一「改提名不能改生效」→ test_nomination_claiming_effective_is_rejected 等 4 条；
  尺二「两处同时写同一权重可探出」（本案病根）→ test_two_writers_on_same_weight_*；
另附零漂移闸：auto_mount 降权后既有 allocation_request 契约键与权重数值逐位不变。
"""

from __future__ import annotations

import inspect
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import backtest.auto_mount as am  # noqa: E402
import backtest.weight_ssot as ws  # noqa: E402

# ---------- 夹具 ----------


def _rows():
    return [
        {"strategy_ref": "STR-A", "weight": 0.05, "stage": "proven", "signal_weight": 1.5, "capacity": 0.2},
        {"strategy_ref": "default-equity", "weight": 0.95, "stage": "frozen", "signal_weight": 0.0, "capacity": 0.0},
    ]


# ---------- 尺一：提名不能改生效 ----------


def test_auto_mount_is_registered_as_nomination_only():
    assert ws.binding_of("auto_mount") == ws.BINDING_NOMINATION
    assert ws.EFFECTIVE_AUTHORITY == "pf_alloc"
    assert ws.binding_of("pf_alloc") == ws.BINDING_EFFECTIVE


def test_unknown_producer_is_rejected_not_defaulted():
    """未登记作者禁默认放行（防"新脚本顺手写权重"混进生效面）。"""
    with pytest.raises(ws.WeightAuthorityError, match="未登记的权重作者"):
        ws.binding_of("some_new_script")


def test_nomination_rows_are_marked_and_numbers_untouched():
    out = ws.make_nomination(_rows(), produced_by="auto_mount")
    assert [r["binding"] for r in out] == ["nomination", "nomination"]
    assert all(r["effective"] is False and r["authority"] == "auto_mount" for r in out)
    # 零漂移：权重与既有契约键逐位原样（本次施工只加标记，不动数值/不删键）
    src = _rows()
    for a, b in zip(src, out, strict=True):  # 行数不等即红（防提名把行吞掉还自称零漂移）
        assert a["weight"] == b["weight"]
        assert set(a) <= set(b), f"既有契约键被吞: {set(a) - set(b)}"
        for k in a:
            assert a[k] == b[k]


def test_nomination_claiming_effective_is_rejected():
    """红测（提名面被拒）：auto_mount 的行一旦声明 effective → 必抛。"""
    rows = ws.make_nomination(_rows(), produced_by="auto_mount")
    rows[0]["binding"] = ws.BINDING_EFFECTIVE  # 伪造"我说的算"
    with pytest.raises(ws.WeightAuthorityError, match="提名越权改生效"):
        ws.assert_nomination_not_binding(rows)


def test_weight_row_without_binding_is_unattributable():
    """红测：没标权级的权重行=不可归因，禁默认生效（本案病根形态之一）。"""
    with pytest.raises(ws.WeightAuthorityError, match="不可归因"):
        ws.assert_nomination_not_binding(_rows())


def test_effective_side_admits_only_pf_alloc():
    ok = [{"strategy_ref": "STR-A", "weight": 0.3, "binding": ws.BINDING_EFFECTIVE, "authority": "pf_alloc"}]
    assert ws.assert_nomination_not_binding(ok) == ok


# ---------- 尺二：两处同时写同一权重=病根，必被探出 ----------


def test_two_writers_on_same_weight_are_detected():
    """病根判据（本案原始形态）：提名腿挤进生效字段与 pf_alloc 并写同一权重。"""
    intents = [
        {"producer": "auto_mount", "strategy_ref": "STR-A", "field": ws.EFFECTIVE_FIELD},
        {"producer": "pf_alloc", "strategy_ref": "STR-A", "field": ws.EFFECTIVE_FIELD},
    ]
    conflicts = ws.find_weight_writer_conflicts(intents)
    assert len(conflicts) == 1
    c = conflicts[0]
    assert c["writers"] == ["auto_mount", "pf_alloc"]
    assert c["field"] == ws.EFFECTIVE_FIELD
    assert c["nomination_overreach"] is True  # 提名越权进生效面
    assert c["multi_effective"] is False  # 只有一个合法生效者（另一只是越权提名）
    assert c["attributable"] is False  # 双写即不可归因，与数值是否相同无关
    with pytest.raises(ws.WeightAuthorityError, match="配比真源双头"):
        ws.assert_single_effective_writer(intents)


def test_two_effective_authors_on_same_weight_is_worst_case(monkeypatch):
    """最恶性形态：两个都自称生效（真·双头）→ multi_effective 必为真。"""
    monkeypatch.setitem(ws.WEIGHT_PRODUCERS, "auto_mount", ws.BINDING_EFFECTIVE)
    intents = [
        {"producer": "auto_mount", "strategy_ref": "STR-A", "field": ws.EFFECTIVE_FIELD},
        {"producer": "pf_alloc", "strategy_ref": "STR-A", "field": ws.EFFECTIVE_FIELD},
    ]
    c = ws.find_weight_writer_conflicts(intents)[0]
    assert c["multi_effective"] is True and c["effective_writers"] == ["auto_mount", "pf_alloc"]


def test_layered_writing_of_different_fields_is_not_a_conflict():
    """分层合法：提名写 PP-001 字段、生效写 alloc 表 → 不算双头（否则一刀切会误伤）。"""
    intents = [
        {"producer": "auto_mount", "strategy_ref": "STR-A", "field": ws.NOMINATION_FIELD},
        {"producer": "pf_alloc", "strategy_ref": "STR-A", "field": ws.EFFECTIVE_FIELD},
    ]
    assert ws.find_weight_writer_conflicts(intents) == []
    ws.assert_single_effective_writer(intents)  # 不抛=放行


def test_effective_path_must_stay_single_after_a_second_author_appears(monkeypatch):
    assert ws.effective_writers() == {"pf_alloc"}
    assert ws.assert_effective_path_single() is None  # 现状：单路，绿
    monkeypatch.setitem(ws.WEIGHT_PRODUCERS, "evil_alloc", ws.BINDING_EFFECTIVE)
    monkeypatch.setitem(ws.PRODUCER_FIELDS, "evil_alloc", ws.EFFECTIVE_FIELD)
    with pytest.raises(ws.WeightAuthorityError, match="生效配比路径不唯一"):
        ws.assert_effective_path_single()


def test_nomination_author_may_not_write_effective_field(monkeypatch):
    monkeypatch.setitem(ws.PRODUCER_FIELDS, "auto_mount", ws.EFFECTIVE_FIELD)
    with pytest.raises(ws.WeightAuthorityError, match="不得写生效字段"):
        ws.assert_producer_writes_nomination("auto_mount")


def test_discover_probe_finds_unregistered_second_head(tmp_path):
    """病根探针：不靠声明表，从源码里把一个野生的第二写手揪出来（file:line）。"""
    bad = tmp_path / "scripts" / "rogue_writer.py"
    bad.parent.mkdir(parents=True)
    bad.write_text(
        'X = 1\nline = f"  - {{strategy_ref: {sid}, weight: {w}}}"\n',
        encoding="utf-8",
    )
    out = ws.discover_weight_writers(tmp_path)
    assert out["unregistered_writer_sites"] == ["scripts/rogue_writer.py:2"]
    assert out["clean"] is False


def test_repo_census_reports_single_effective_path():
    """真仓实测：生效面只剩 pf_alloc 一条路，且无未登记写手（本车道验收面）。"""
    census = ws.authority_census(ROOT)
    assert census["single_effective_path"] is True
    assert census["effective_producers"] == ["pf_alloc"]
    assert census["conflicts"] == []
    assert "auto_mount" in census["producers_observed"]  # 提名腿仍在（只是不再是权威）
    disc = ws.discover_weight_writers(ROOT)
    assert disc["unregistered_writer_sites"] == [], f"野生权重写手：{disc['unregistered_writer_sites'][:5]}"


# ---------- 尺三（W6-H 补）：未登记作者禁隐身，野生写手必被抓 ----------

_ROGUE_LINE = 'line = f"  - {{strategy_ref: {sid}, weight: {w}}}"\n'


def _fake_repo(tmp_path: Path, *, rogue: bool = True, pf_alloc: bool = False) -> Path:
    """临时假仓：只造判据要看的两个目录（测试禁扫真仓写面，也禁写生产路径）。"""
    if rogue:
        rogue_dir = tmp_path / "scripts"
        rogue_dir.mkdir(parents=True, exist_ok=True)
        (rogue_dir / "rogue_writer.py").write_text("X = 1\n" + _ROGUE_LINE, encoding="utf-8")
    if pf_alloc:
        leg = tmp_path / "src" / "zephyr" / "pf_alloc" / "core"
        leg.mkdir(parents=True, exist_ok=True)
        (leg / "allocator.py").write_text(
            "def persist(rows):\n"
            "    for r in rows:\n"
            "        write_budget_daily(strategy_ref=r['strategy_ref'], target_weight=r['weight'])\n",
            encoding="utf-8",
        )
    return tmp_path


def test_classify_path_never_returns_none_anymore():
    """立身之本的第一颗钉：认不出人=判野生，**没有"返回 None 就不参与判定"这条路**。"""
    assert ws.classify_path("src/zephyr/pf_alloc/core/x.py") == "pf_alloc"
    assert ws.classify_path("scripts/backtest/auto_mount.py") == "auto_mount"
    assert ws.classify_path("tools/new_random_script.py") == ws.WILD_WRITER
    assert ws.is_wild_writer(ws.classify_path("whatever.py")) is True


def test_lone_wild_writer_is_a_conflict_not_a_non_event(tmp_path: Path):
    """红队 §三.4 修法核收：未登记作者的写手哪怕孤身一人也算冲突（禁默认放行）。"""
    repo = _fake_repo(tmp_path, rogue=True, pf_alloc=False)
    wild = ws.find_wild_weight_writers(repo)
    assert [h["file"] for h in wild] == ["scripts/rogue_writer.py"]
    assert all(h["producer"] == ws.WILD_WRITER and h["attributable"] is False for h in wild)

    conflicts = ws.find_weight_writer_conflicts(ws.wild_writer_intents(wild))
    assert len(conflicts) == 1, "「没人跟它抢」就放行的旧口径已废：孤身野生写手也算冲突"
    c = conflicts[0]
    assert c["wild_writers"] is True and c["attributable"] is False
    assert c["wild_writer_sites"] == ["scripts/rogue_writer.py:2"]
    with pytest.raises(ws.WeightAuthorityError, match="野生写手"):
        ws.assert_single_effective_writer(ws.wild_writer_intents(wild))


def test_census_surfaces_wild_writers_and_is_not_clean(tmp_path: Path):
    """census 面：野生写手进 conflicts + 单列 wild_writer_sites（可复核，不藏在日志里）。"""
    repo = _fake_repo(tmp_path, rogue=True, pf_alloc=True)
    census = ws.authority_census(repo)
    assert census["wild_writer_sites"] == ["scripts/rogue_writer.py:2"]
    assert census["conflicts"], "有野生写手而 conflicts 仍为空=这台尺又变装饰"
    assert census["unattributable"] is True and census["clean"] is False
    assert census["wild_scan_dirs"] == ["src", "scripts"], "扫描口径须在结论里自陈（禁装无死角）"


def test_self_alias_to_hide_now_surfaces_as_wild(tmp_path: Path, monkeypatch):
    """反向隐身（红队原话：改自己的路径键别名即可从 census 消失）→ 修后立即现形。"""
    repo = _fake_repo(tmp_path, rogue=False)
    mount = repo / "scripts" / "backtest"
    mount.mkdir(parents=True, exist_ok=True)
    (mount / "auto_mount.py").write_text(
        'def render(rows):\n    for r in rows:\n        out = f"{{strategy_ref: sid, weight: w}}"\n',
        encoding="utf-8",
    )
    assert ws.authority_census(repo)["wild_writer_sites"] == []  # 登记在册时：不判野生
    monkeypatch.setitem(ws.PRODUCER_PATH_KEYS, "auto_mount", ("scripts/backtest/alias_name.py",))
    census = ws.authority_census(repo)
    assert census["wild_writer_sites"] == ["scripts/backtest/auto_mount.py:3"], (
        "改别名把自己从名册抹掉后必须掉进野生面，而不是消失"
    )
    assert census["conflicts"] and census["clean"] is False


def test_unreadable_source_fails_closed_not_silently_skipped(tmp_path: Path):
    """INVARIANTS ④：未登记文件读不到=报错，不许当"这里没有写手"。"""
    repo = _fake_repo(tmp_path, rogue=False)
    victim = repo / "scripts" / "broken.py"
    victim.parent.mkdir(parents=True, exist_ok=True)
    victim.write_bytes(b"\xff\xfe\x00 non utf8 strategy_ref weight: 1\n")
    with pytest.raises(ws.WeightAuthorityError, match="读不到"):
        ws.find_wild_weight_writers(repo)


def test_real_repo_census_still_clean_after_wild_rule():
    """出厂自证：新口径下真仓没有野生写手（若有=本测试替 Owner 值班，禁放宽断言）。"""
    census = ws.authority_census(ROOT)
    assert census["wild_writer_sites"] == [], f"真仓野生写手：{census['wild_writer_sites'][:5]}"
    assert census["clean"] is True and census["conflicts"] == []


# ---------- auto_mount 侧接线与零漂移 ----------


def test_allocation_request_output_is_nomination_grade():
    old = [
        {"strategy_ref": "STR-A", "weight": am.NEW_SLEEVE_WEIGHT},
        {"strategy_ref": "default-equity", "weight": 1 - am.NEW_SLEEVE_WEIGHT},
    ]
    ev = {
        "STR-A": {
            "sr": 1.2,
            "vol": 0.02,
            "confidence": "verified",
            "states": ["expansion"],
            "selection": False,
            "source": "x.py",
            "retired": False,
        }
    }
    expected = am.sleeve_weights(old, ev)
    rows = am.allocation_request(old, ev)
    assert rows, "无行即测试失去判别力"
    for r in rows:
        assert r["binding"] == ws.BINDING_NOMINATION
        assert r["effective"] is False
        assert r["weight"] == pytest.approx(expected[r["strategy_ref"]], abs=1e-12)  # 零漂移
    assert abs(sum(r["weight"] for r in rows) - 1.0) < 1e-12  # Σ 闭合判据未动
    assert {r["stage"] for r in rows} == {"proven", "frozen"}  # 既有契约面未退化


def test_alloc_authority_guard_fails_closed(monkeypatch):
    """护栏必须有真调用者且能改变行为（防"装饰性护栏"复现）。"""
    assert am._weight_ssot() is ws, "auto_mount 用的必须是同一把尺（两份实例=patch 打不到=假绿源）"

    def boom(*_a, **_k):
        raise ws.WeightAuthorityError("模拟双头")

    monkeypatch.setattr(ws, "assert_effective_path_single", boom)
    with pytest.raises(ws.WeightAuthorityError, match="模拟双头"):
        am.alloc_authority_guard()


def test_guard_is_wired_before_the_map_write():
    src = inspect.getsource(am.main)
    assert "alloc_authority_guard(" in src, "写图路径未接权级闸=护栏是装饰"
    assert src.index("alloc_authority_guard(") < src.index("safe_write_text"), "闸必须在前，写在后（先判权再落图）"


def test_caliber_numbers_untouched_by_this_lane():
    """禁区自证：本车道未改任何配比数值/判据常量。"""
    assert am.NEW_SLEEVE_WEIGHT == 0.05
    assert am.WEIGHT_STEP_LIMIT == 0.25
    assert am.WEIGHT_GRID == 6
    import yaml

    tdm = yaml.safe_load((ROOT / "config" / "trading_decision_map.yaml").read_text(encoding="utf-8"))
    sleeves = tdm["portfolio_plan"]["sleeves"]
    assert abs(sum(float(s["weight"]) for s in sleeves) - 1.0) < 1e-9  # Σ=1 口径未动
    assert len(sleeves) == 16  # 未增删 sleeve（提名面降权不改挂图结果）
