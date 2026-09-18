# [BLUEPRINT] MOD-AUTO-L3-003 | docs/_working/fullflow_campaign/FLOWTHROUGH_ACCEPTANCE_SPEC.md | §1-§4
# [MODULE] tests.automation.test_flowthrough_verifier
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts/automation/flowthrough_verifier.py; pytest
# [CONSUMERS] pytest 套件（tests/automation）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 测试只读真源，禁写 data/ 业务目录；产物一律 tmp_path;
#   判定路径不得整体 mock——注入的只是"行数来源"这类外设数据通道
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 通道故障 → prove-red 用例 skip 并给出原因（不假绿）
# [TESTS] tests/automation/test_flowthrough_verifier.py
# [A_module] module_id=MOD-AUTO-L3-003 | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [PROVISIONAL] 暂编号：随主件重编
"""全流通验收仪测试：钉住"能红"与三态判据，防尺子退化成橡皮章。"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO / "scripts" / "automation" / "flowthrough_verifier.py"
spec = importlib.util.spec_from_file_location("flowthrough_verifier", MODULE_PATH)
fv = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules["flowthrough_verifier"] = fv
spec.loader.exec_module(fv)


def _ctx(**kw):
    base = {"limit_tables": 4, "limit_runs": 0, "use_db": False}
    base.update(kw)
    return fv.FlowthroughProbeContext(**base)


def _fake_counter(mapping, default: int = 0):
    def counter(table: str) -> int:
        return mapping.get(table, default)

    return counter


def test_feed_green_when_all_tables_have_rows() -> None:
    """①全表有货且无时间戳约束 → 绿。"""
    hit = fv.probe_feed(["c1_x.alpha", "c1_x.beta"], {}, _ctx(),
                        row_counter=_fake_counter({"c1_x.alpha": 10, "c1_x.beta": 3}))
    assert hit["verdict"] == "绿"
    assert "10行" in hit["evidence"]


def test_feed_red_when_upstream_empty() -> None:
    """①上游空表 = 断点，必须判红（禁把 0 行说成正常）。"""
    hit = fv.probe_feed(["c1_x.alpha"], {}, _ctx(), row_counter=_fake_counter({"c1_x.alpha": 0}))
    assert hit["verdict"] == "红"


def test_feed_distinguishes_broken_table_from_channel_failure() -> None:
    """表不可达=-1 判红；通道故障=-2 判不可测（防他会话坏件造假红）。"""
    broken = fv.probe_feed(["c1_x.ghost"], {}, _ctx(), row_counter=lambda _t: -1)
    down = fv.probe_feed(["c1_x.ghost"], {}, _ctx(), row_counter=lambda _t: -2)
    assert (broken["verdict"], broken["broken_hop"]) == ("红", ["c1_x.ghost"])
    assert down["verdict"] == "不可测" and down["broken_hop"] == []


def test_verdict_red_when_any_core_direction_empty() -> None:
    """三态：①~④ 任一空 → 红（规范 §2）。"""
    rec = {"sixway": {"①入口有料": {"verdict": "红"}, "②转化能跑": {"verdict": "绿"},
                      "③出口有货": {"verdict": "绿"}, "④下游能取": {"verdict": "绿"},
                      "⑤哨兵在岗": {"verdict": "绿"}, "⑥失败会响": {"verdict": "绿"}}}
    assert fv.suggest_verdict(rec) == "红"


def test_verdict_yellow_when_aux_directions_missing() -> None:
    """三态：核心四向绿、⑤⑥ 未证 → 黄（禁把黄说成绿）。"""
    rec = {"sixway": {"①入口有料": {"verdict": "绿"}, "②转化能跑": {"verdict": "绿"},
                      "③出口有货": {"verdict": "绿"}, "④下游能取": {"verdict": "绿"},
                      "⑤哨兵在岗": {"verdict": "不可测"}, "⑥失败会响": {"verdict": "黄"}}}
    assert fv.suggest_verdict(rec) == "黄"


def test_prove_red_names_the_broken_hop_without_mocks() -> None:
    """能红证明：注入假行数通道（不 mock 判定函数）→ 必须红且指名那一跳。"""
    tables = ["c1_x.alpha", "c1_x.beta"]
    good = fv.probe_feed(tables, {}, _ctx(),
                         row_counter=_fake_counter({"c1_x.alpha": 5, "c1_x.beta": 7}))
    poisoned = list(tables)
    poisoned[0] = fv._poisoned_table(tables[0])
    bad = fv.probe_feed(poisoned, {}, _ctx(),
                        row_counter=_fake_counter({"c1_x.beta": 7}, default=-1))
    assert good["verdict"] == "绿"
    assert bad["verdict"] == "红"
    assert bad["broken_hop"] == [f"c1_x.alpha{fv.FF_PROBE_POISON_SUFFIX}"]


@pytest.mark.skipif(not fv.ch_channel_alive(), reason="ClickHouse 证据通道不可用")
def test_prove_red_against_real_warehouse() -> None:
    """真仓红证：真实上游表改名 → 走真查询必须报红并指名。"""
    ctx = _ctx(use_db=True, limit_tables=2)
    clean = fv._clean_control_tables(ctx)
    if len(clean) < 2:
        pytest.skip("真源取不到 ≥2 张有货上游表")
    assert fv.probe_feed(clean, {}, ctx)["verdict"] in ("绿", "黄")
    hit = fv.prove_red_chain_hop(clean, ctx, broken_index=0)
    assert hit["verdict"] == "红"
    assert hit["named_broken_hop"] == [fv._poisoned_table(clean[0])]


def test_declarations_catch_lying_blueprint() -> None:
    """双向核对：声明的消费方实际不 import = 蓝图说谎候选（假闭环防线）。"""
    declared = [{"module": "src/zephyr/x/last_resort_watchdog.py", "declared": ["escalation"]}]
    actual = [{"consumer": "src/zephyr/other/reporting.py", "callee": "src/zephyr/x/last_resort_watchdog.py",
               "dep_type": "import_depends"}]
    out = fv.crosscheck_declarations(declared, actual)
    assert out["liar_count"] == 1
    assert out["blueprint_lying_candidates"][0]["declared_but_no_import"] == ["escalation"]
    assert out["unlisted_consumers"][0]["imported_by_unlisted"] == "src/zephyr/other/reporting.py"


def test_dynamic_registration_is_not_counted_as_orphan(tmp_path: Path) -> None:
    """BRK-009：注册表里出现的模块不判孤儿。"""
    reg = tmp_path / "agent_skill_registry.yaml"
    reg.write_text("entries:\n  - skill: my_special_skill_pack\n", encoding="utf-8")
    fv._REGISTRY_INDEX = {"my_special_skill_pack": {reg.name}}
    try:
        hits = fv.dynamic_registration_hits(["src/zephyr/autonomy_core/skills/my_special_skill_pack.py"])
    finally:
        fv._REGISTRY_INDEX = None
    assert hits and hits[0]["registered_in"] == [reg.name]
    assert fv.zero_in_dynamic(["src/zephyr/a.py"], hits) == [{"module": "src/zephyr/a.py"}]


def test_e2e_flags_upstream_full_downstream_zero(monkeypatch) -> None:
    """§3.1：上游有货、本环节产出 0 → 该跳判断点。"""
    rows = {"c1_x.alpha": 42, "c1_x.beta": 0, "c1_x.src": 5}
    monkeypatch.setattr(fv, "_row_count", lambda t: rows.get(t, -1))
    scans = {"FF-01": {"write_tables": ["c1_x.alpha"], "read_tables": ["c1_x.src"]},
             "FF-06": {"write_tables": ["c1_x.beta"], "read_tables": ["c1_x.alpha"]}}
    hop = fv._e2e_hop("FF-01", "FF-06", scans, _ctx())
    assert hop["shared_tables"] == ["c1_x.alpha"]
    assert hop["upstream_landed"] == {"c1_x.alpha": 42}
    assert hop["this_stage_produced"] == {"c1_x.beta": 0}
    assert hop["break"] is True


def test_crosscheck_flags_source_drift(tmp_path: Path, monkeypatch) -> None:
    """真源龄超阈值必须报"已过期"（禁缓存快照当真值）。"""
    meta = {"age_days": fv.FF_STALE_SOURCE_DAYS + 3, "missing": False}
    assert "已过期" in fv._source_age_warning(meta)
    assert "MISSING" in fv._source_age_warning({"age_days": 0, "missing": True})
    assert monkeypatch is not None


# ==========================================================================
# verifier2 接力批：R-024 两处漏检的治本证据（逐跳断言 + 论域声明 + ⑤⑥向补齐）
# ==========================================================================
def _hop(src: str, dst: str, handoff: tuple[str, ...], produced: tuple[str, ...] = (),
         kind: str = "declared") -> fv.FlowthroughHopSpec:
    return fv.FlowthroughHopSpec(src=src, dst=dst, kind=kind, handoff=handoff, produced=produced)


GOOD = {"c1_x.alpha": 100, "c1_x.beta": 50, "c1_x.gamma": 7, "c1_x.prod": 9}


def _counter(mapping: dict[str, int], default: int = fv.FF_ROWS_UNREACHABLE):
    return lambda t: mapping.get(t, default)


def test_hop_model_names_the_second_table_not_just_the_first() -> None:
    """变异证据①：断供藏在交接表清单的**第 2 张**——旧"取首表代表全跳"必然漏检。"""
    hop = _hop("FF-01", "FF-07", ("c1_x.alpha", "c1_x.beta"), ("c1_x.prod",))
    rows = dict(GOOD)
    rows["c1_x.beta"] = 0                      # 只有第 2 张断供
    ev = fv.measure_hop(hop, _counter(rows))
    assert ev["breaks"], "逐跳断言必须看见藏在后面的断供"
    assert {b["table"] for b in ev["breaks"]} == {"c1_x.beta"}
    assert ev["breaks"][0]["hop_id"] == "FF-01→FF-07"


def test_hop_model_treats_unreachable_as_break_not_ok() -> None:
    """变异证据②：旧 `is_break` 用 `read_rows == 0`，表消失(-1) 时判"不断"=漏检。"""
    hop = _hop("FF-03", "FF-04", ("c1_x.alpha",), ("c1_x.prod",))
    rows = {"c1_x.alpha": 100, "c1_x.prod": 9}   # c1_x.ghost 不在名册 → -1
    ev = fv.measure_hop(_hop("FF-03", "FF-04", ("c1_x.alpha", "c1_x.ghost"), ("c1_x.prod",)),
                        _counter(rows))
    assert fv.measure_hop(hop, _counter(rows))["breaks"] == []
    reasons = {b["reason"]: b["table"] for b in ev["breaks"]}
    assert reasons == {"upstream_table_absent": "c1_x.ghost"}


def test_injected_hop_is_named_and_no_other_hop_is_blamed() -> None:
    """A 族判据：注入一跳 → **新增**红跳集合恰好=那一跳（多了=误导归因，少了=漏检）。"""
    hops = [_hop("FF-01", "FF-02", ("c1_x.alpha",), ("c1_x.prod",)),
            _hop("FF-01", "FF-07", ("c1_x.alpha", "c1_x.beta"), ("c1_x.prod",), "transitive"),
            _hop("FF-12", "FF-02", ("c1_x.gamma",), ("c1_x.prod",))]
    counter = _counter(GOOD)
    baseline = {h.hop_id: fv.measure_hop(h, counter)["breaks"] for h in hops}
    poison = {"FF-01→FF-07|c1_x.beta": fv._poisoned_table("c1_x.beta")}
    after = fv.evaluate_hops(hops, counter, read_poison=poison)
    newly = set(after["broken_hops"]) - {k for k, v in baseline.items() if v}
    assert newly == {"FF-01→FF-07"}
    detail = [b for b in after["broken_detail"] if b["reason"] == "supply_cut_at_read"]
    assert detail and detail[0]["hop_id"] == "FF-01→FF-07" and "FF-07" in detail[0]["hop_id"]


def test_global_supply_cut_names_every_using_hop() -> None:
    """B 族判据：一张表供多跳时断供，用它的每一跳都得点名，不用它的不得被牵连。"""
    hops = [_hop("FF-01", "FF-02", ("c1_x.alpha",), ("c1_x.prod",)),
            _hop("FF-01", "FF-07", ("c1_x.alpha",), ("c1_x.prod",), "transitive"),
            _hop("FF-06", "FF-07", ("c1_x.beta",), ("c1_x.prod",))]
    counter = _counter(GOOD)
    poison = {f"{h.hop_id}|c1_x.alpha": fv._poisoned_table("c1_x.alpha")
              for h in hops if "c1_x.alpha" in h.handoff}
    after = fv.evaluate_hops(hops, counter, read_poison=poison)
    named = {b["hop_id"] for b in after["broken_detail"] if b["reason"] == "supply_cut_at_read"}
    assert named == {"FF-01→FF-02", "FF-01→FF-07"}


def test_enumerate_hops_derives_transitive_pair_from_skeleton() -> None:
    """跳清单机械推导：骨架声明 FF-01→FF-06、FF-06→FF-07 ⇒ 必须长出 FF-01→FF-07。"""
    catalog = {f"FF-{i:02d}": {"kind": "pipeline"} for i in (1, 6, 7)}
    scans = {k: {"read_tables": ["c1_x.alpha"], "write_tables": ["c1_x.alpha"]} for k in catalog}
    skel = {"FF-01": {"downstream": "FF-06"}, "FF-06": {"upstream": "FF-01", "downstream": "FF-07"},
            "FF-07": {"upstream": "FF-06"}}
    ids = {h.hop_id for h in fv.enumerate_hops(catalog, scans, skel)}
    assert {"FF-01→FF-06", "FF-06→FF-07", "FF-01→FF-07"} <= ids


def test_sentinel_allow_empty_whitelist_can_not_be_green() -> None:
    """⑤向：白名单里的表=该向自动失明，只配判黄并注"豁免中"（不许判绿）。"""
    armed = [{"table": "c1_x.alpha", "allow_empty": False}]
    blind = [{"table": "c1_x.beta", "allow_empty": True, "豁免中": True}]
    ran = {"ran": True, "breaches": 0, "failed": False}
    verdict, why = fv.sentinel_verdict(["c1_x.alpha", "c1_x.beta"], armed, blind, [], ran)
    assert verdict == "黄" and "豁免" in why
    assert fv.sentinel_verdict(["c1_x.alpha"], armed, [], [], ran)[0] == "绿"
    assert fv.sentinel_verdict(["c1_x.beta"], [], [], [], ran)[0] == "红"     # 全豁免无在岗=红
    assert fv.sentinel_verdict(["c1_x.alpha"], armed, blind, [], {"ran": True, "breaches": 3})[0] == "红"


def test_failclose_declares_static_mode_and_never_claims_injection() -> None:
    """⑥向：本轮只做只读静态推演，输出必须自证 dynamic_injection=False。"""
    verdict, why = fv.failclose_verdict(["a.py:3"], {"silent_except_pass": 1}, 2, 40)
    assert verdict == "红" and "静默" in why
    assert fv.failclose_verdict([], {}, 0, 40)[0] == "红"          # 零告警接线=失败无人知晓
    assert fv.failclose_verdict([], {"silent_except_pass": 1}, 3, 40)[0] == "黄"
    assert "静态" in fv.probe_failclose([Path(fv.__file__).parent]).get("mode", "")


def test_universe_guard_rejects_report_without_declaration() -> None:
    """R-024 硬约束的代码化：缺论域声明的报表必须抛错，不是"提醒一下"。"""
    with pytest.raises(fv.UniverseDeclarationError):
        fv.universe_guard("# 台账\n\n结论：本环节已打通\n")
    u = fv.universe_declaration({"G_depgraph_runtime": ({"D_A"}, {"missing": False}),
                                 "B_functional_domain_registry": ({"D_A", "D_ORDER"}, {})},
                                {"FF-01": {"kind": "supply"}}, "测试论域")
    text = "\n".join(fv.render_universe_lines(u))
    fv.universe_guard(text)
    assert "本结论论域" in text and "D_ORDER" in text          # 论域外有册无实体须逐条列出
    assert u["counts"]["在册无实体"] == 1


def test_row_count_separates_absent_from_unmeasurable(monkeypatch) -> None:
    """表不在名册=-1（断链，判红）；在名册但查不动=-2（不可测，禁判红也禁判绿）。"""
    monkeypatch.setattr(fv, "ch_channel_alive", lambda: True)
    monkeypatch.setattr(fv, "_ch_known_tables", lambda: {"c1_x.alpha"})
    monkeypatch.setattr(fv, "log_line", lambda _s: None)
    assert fv._row_count("c1_x.ghost") == fv.FF_ROWS_UNREACHABLE
    monkeypatch.setattr(fv, "_rows_from_parts", lambda _t: fv.FF_ROWS_UNMEASURABLE)
    assert fv._row_count("c1_x.alpha") == fv.FF_ROWS_UNMEASURABLE
    monkeypatch.setattr(fv, "_rows_from_parts", lambda _t: 4242)
    assert fv._row_count("c1_x.alpha") == 4242


def test_orphan_verdict_does_not_call_dynamically_loaded_module_orphan(monkeypatch) -> None:
    """D_AI_LAYER 型复核：有 importlib 证据/注册面命中的，禁报成孤儿（Z-aibase 正在施工）。"""
    monkeypatch.setattr(fv, "dynamic_registration_hits", lambda mods, cap=40: [])
    monkeypatch.setattr(fv, "_global_consumers", lambda _p: [])
    assert fv.orphan_verdict("src/zephyr/ai_layer/foo.py", "foo")[0] == "孤儿候选（需总包裁定）"
    monkeypatch.setattr(fv, "_dynamic_import_evidence", lambda _s: "src/x/loader.py 含 import_module")
    assert fv.orphan_verdict("src/zephyr/ai_layer/foo.py", "foo")[0] == "假阳性（importlib 动态加载）"
    monkeypatch.setattr(fv, "dynamic_registration_hits",
                        lambda mods, cap=40: [{"module": mods[0], "registered_in": ["r.yaml"]}])
    assert "假阳性" in fv.orphan_verdict("src/zephyr/ai_layer/foo.py", "foo")[0]


def test_universe_guard_payload_rejects_machine_ledger_without_universe(tmp_path) -> None:
    """R-024 论域禁令的**机读件**版本：04_sixway_machine_ledger.yaml 是下游按字段读的件，
    缺字段/伪空必须抛错——否则下游 .get(k, []) 会把"没扫到"读成"扫了且为零"。"""
    good = fv.universe_declaration({"G_depgraph_runtime": ({"D_A"}, {"missing": False}),
                                    "B_functional_domain_registry": ({"D_A", "D_ORDER"}, {})},
                                   {"FF-01": {"kind": "supply"}}, "测试论域")
    fv.universe_guard_payload(good)                      # 完整论域块必须放行
    for field in ("scope", "counts", "registered_without_entity", "residual_domains_no_flow_stage"):
        hole = dict(good)
        hole.pop(field)
        with pytest.raises(fv.UniverseDeclarationError):
            fv.universe_guard_payload(hole)              # 任一必备字段缺失都得拦，不是只查 scope
    blank = dict(good, scope="   ")
    with pytest.raises(fv.UniverseDeclarationError):
        fv.universe_guard_payload(blank)                 # 有键但空串=伪声明，同样拦
