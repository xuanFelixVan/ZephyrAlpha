# -*- coding: utf-8 -*-
# [BLUEPRINT] MOD-GOV-CONSUMPTIONCENSUS | tests/governance/test_consumption_census_redproof.py
# [TTL] permanent
"""消费面普查九族引擎 · 能红判据（R-5 律：红证不落盘＝没跑）。

沙盘＝tmp_path 合成仓库（禁写生产 data/ 与真登记册，宪法 §9.6）。
逐条对应任务书红证要求：
  R-A 造"上架无客"新件 ⇒ 必进孤岛清单且计数对
  R-B 给它一个真消费者 ⇒ 必从孤岛清单消失
  R-C `.md` 单独提及 ⇒ 不得计为消费者（IND-REV-001 假绿回归）
  R-D `stale` 态处置与声明一致（显式退役：产出侧永不再出现该态）
  R-E `consumer_files` 必须是真实清单（非计数）
  R-F 增量缓存与冷跑结果全等（成本控制不许改判据）
  R-G 单一 scope 常量口径谓词
  R-H 孤岛价值排序按显式公式（非拍脑袋）
  R-I 观察者自排：尺自己提到实体名不得算消费者（本次实测新发现）
  R-J 事件触发 reconciler：登记册变更才跑、新岛报警、回填即净、护栏注释在册
  R-K wiring_registry 机器视图：复用既有 wiring_status 词表 + --check rc 语义
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from zephyr.governance.consumption import consumption_census as cc
from zephyr.governance.indicator_usage_audit import run_indicator_usage_audit

CAT = "docs/01_policies_and_standards/_registry/catalogs"


# ── 合成仓库夹具 ────────────────────────────────────────────────────────────
def _w(root: Path, rel: str, text: str) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8", newline="\n")
    return p


def _synth_repo(root: Path, *, extra_indicator: str = "") -> Path:
    inds = [
        "  - indicator_id: IND-RED-001\n    name: red_proof\n    status: active\n"
        "    tier: 4\n    used_by_factors: [FCT-X-001]\n    code_path: src/zephyr/factor/tech.py\n",
        "  - indicator_id: IND-ORPHAN-001\n    name: orphan\n    status: active\n"
        "    tier: 2\n    code_path: src/zephyr/factor/orphan_impl.py\n",
    ]
    if extra_indicator:
        inds.append(extra_indicator)
    _w(root, f"{CAT}/technical_indicator_registry.yaml",
       "tier: 3\nindicators:\n" + "".join(inds) +
       "  - indicator_id: IND-REV-001\n    name: legacy_candle\n    status: deprecated\n")
    _w(root, f"{CAT}/macro_indicator_registry.yaml",
       "tier: 2\nindicators:\n  - indicator_id: MAC-CN-001\n    name: shibor\n"
       "    impact_assets: [A1, A2]\n")
    _w(root, f"{CAT}/data_asset_registry.yaml",
       "tier: 3\ndatasets:\n  - dataset_id: DS-901\n    entity_name: c3_fundamental.block_x_detail\n"
       "    consumed_by_jobs: [JOB-1]\n  - dataset_id: DS-902\n"
       "    entity_name: c1_market.weather_station_daily\n    consumed_by_jobs: []\n"
       "sources: []\njobs:\n  - job_id: JOB-7\n    source_code_ref: src/zephyr/alt_data/w.py\n"
       "    outputs: [DS-902]\n    module_id: MOD-ALT\n")
    _w(root, f"{CAT}/factor_registry.yaml",
       "tier: 3\nfactors:\n  - factor_id: FCT-RED-001\n    name: f1\n"
       "    belongs_to_strategies: [STR-A]\n")
    _w(root, f"{CAT}/strategy_registry.yaml",
       "tier: 2\nstrategies:\n  - strategy_id: STR-RED-001\n    name: s1\n    alpha_sources: [FCT-RED-001]\n")
    _w(root, f"{CAT}/event_calendar_registry.yaml",
       "tier: 1\nevent_types:\n  - event_type_id: EVT-RED-001\n    name: e1\n"
       "    used_by_strategies: [STR-RED-001]\n")
    # 族④ 真源锚（组件名由正则派生，禁手工清单）+ 族③ 生产者面
    _w(root, "src/zephyr/alt_data/emotion_index_builder.py",
       'comps = [_component_row("C1_limitup_temp", 1), _component_row("C2_promotion", 2)]\n'
       'c = _sub_component("C5_margin", 3)\n')
    _w(root, "src/zephyr/alt_data/w.py", 'TABLE = "c1_market.weather_station_daily"\n')
    return root


def _run(root: Path, *, out: Path | None = None, cache: Path | None = None,
         doc_mentions: bool = True, families=None) -> dict:
    return cc.run_consumption_census(
        families=families, repo_root=root, scan_root=root,
        output_path=out if out is not None else root / ".runtime/tmp/ledger.json",
        cache_path=cache, include_doc_mentions=doc_mentions, today="T1",
    )


def _entry(doc: dict, eid: str, family: str = "indicator") -> dict:
    for f in doc["families"]:
        if f["family_id"] == family:
            for e in f["entries"]:
                if e["entity_id"] == eid:
                    return e
    raise AssertionError(f"台账无条目 {family}/{eid}")


# ── R-A / R-B / R-C / R-D / R-E / R-I ───────────────────────────────────────
def test_new_island_appears_then_disappears_with_real_consumer(tmp_path):
    root = _synth_repo(tmp_path)
    doc = _run(root)["doc"]
    a = _entry(doc, "IND-ORPHAN-001")
    assert a["state"] == "zero" and a["consumer_count"] == 0
    assert isinstance(a["consumer_files"], list)        # R-E：清单非计数
    assert "IND-ORPHAN-001" in {i["entity_id"] for i in doc["islands"]}

    # 给它一个真消费者（src/ 的 .py）⇒ 必须从孤岛清单消失
    _w(root, "src/zephyr/factor/consumer_orphan.py", "v = IND_ORPHAN_001 * 2\n")
    doc2 = _run(root)["doc"]
    b = _entry(doc2, "IND-ORPHAN-001")
    assert b["state"] == "active"
    assert b["consumer_files"] == ["src/zephyr/factor/consumer_orphan.py"]   # R-E 精确清单
    assert "IND-ORPHAN-001" not in {i["entity_id"] for i in doc2["islands"]}


def test_markdown_only_mention_never_counts_as_consumer(tmp_path):
    """IND-REV-001 假绿回归：文档提一句 ≠ 有客。"""
    root = _synth_repo(tmp_path)
    _w(root, "docs/design/indicator_catalog.md", "IND-RED-001 与 candle_pattern 都值得研究。\n")
    doc = _run(root)["doc"]
    e = _entry(doc, "IND-RED-001")
    assert e["state"] == "zero"
    assert e["consumer_files"] == []
    assert "docs/design/indicator_catalog.md" in e["doc_mentions"]   # 只进证据位
    assert "IND-RED-001" in {i["entity_id"] for i in doc["islands"]}


def test_stale_state_is_retired_and_never_emitted(tmp_path):
    """R-D：stale 态显式退役——产出侧任何族都不得出现该态/该键。"""
    root = _synth_repo(tmp_path)
    doc = _run(root)["doc"]
    assert "stale" not in doc["counts"]
    for f in doc["families"]:
        assert "stale" not in f["counts"]
        for e in f["entries"]:
            assert e["state"] in {"active", "zero", "retired"}
    assert "retired" in doc["stale_state"]
    # 退役态确实可达（族② IND-REV-001 status=deprecated 且零消费者）
    assert _entry(doc, "IND-REV-001")["state"] == "retired"


def test_observer_self_reference_is_not_a_consumer(tmp_path):
    """R-I：尺自己（引擎/旧壳/生成器）提到实体名＝自我认证，必须自排。"""
    root = _synth_repo(tmp_path)
    _w(root, "src/zephyr/governance/consumption_census_note.py",
       "# IND-RED-001 与 candle_pattern 的判据说明\n")
    doc = _run(root)["doc"]
    assert _entry(doc, "IND-RED-001")["consumer_files"] == []


def test_legacy_shim_emits_real_consumer_lists_without_stale(tmp_path):
    """旧台账路径向后兼容：签名/输出路径不变，counts 不再有 stale 键。"""
    root = _synth_repo(tmp_path)
    _w(root, "src/zephyr/factor/tech.py", "x = IND_RED_001\n")
    reg = root / CAT / "technical_indicator_registry.yaml"
    out = root / ".runtime/tmp/ind_ledger.json"
    r = run_indicator_usage_audit(reg, scan_root=root, output_path=out, today="D1")
    assert "stale" not in r["counts"]                  # 态位退役：键不再广告
    assert set(r["counts"]) <= {"active", "zero", "retired"}
    doc = json.loads(out.read_text(encoding="utf-8"))
    assert doc["schema"] == "indicator_usage/2"
    by = {e["indicator_id"]: e for e in doc["entries"]}
    assert by["IND-RED-001"]["consumer_files"] == ["src/zephyr/factor/tech.py"]
    assert by["IND-ORPHAN-001"]["recommendation"].startswith("retire_candidate")


# ── R-F 增量缓存 ─────────────────────────────────────────────────────────────
def test_incremental_cache_matches_cold_run(tmp_path):
    cache = tmp_path / ".runtime/tmp/cache.json"
    cold = _run(_synth_repo(tmp_path), cache=None)["doc"]
    first = _run(tmp_path, cache=cache)["doc"]          # 建缓存
    warm = _run(tmp_path, cache=cache)["doc"]           # 命中缓存
    assert warm["families"] == cold["families"] == first["families"]
    assert warm["runtime"]["rescanned_files"] == 0
    assert cold["runtime"]["rescanned_files"] > 0
    # 改动一个文件 ⇒ 只重扫该文件
    _w(tmp_path, "src/zephyr/factor/late_consumer.py", "y = IND_ORPHAN_001\n")
    inc = _run(tmp_path, cache=cache)["doc"]
    assert inc["runtime"]["rescanned_files"] == 1
    assert _entry(inc, "IND-ORPHAN-001")["state"] == "active"


def test_cache_invalidates_when_entity_universe_changes(tmp_path):
    """R-F2（本道实测缺陷）：登记册新增实体后，旧缓存必须作废。

    否则新实体在缓存里"从未被扫过"→ 被判零命中＝假孤岛（上架无客清单被灌水）。
    """
    cache = tmp_path / ".runtime/tmp/cache.json"
    root = _synth_repo(tmp_path)
    _run(root, cache=cache)
    # 登记册加一条新指标，且它确有消费者（新 token 必须重扫才看得见）
    _w(root, f"{CAT}/technical_indicator_registry.yaml",
       (root / CAT / "technical_indicator_registry.yaml").read_text(encoding="utf-8")
       + "  - indicator_id: IND-NEW-001\n    name: new\n    status: active\n    tier: 3\n")
    _w(root, "src/zephyr/factor/uses_new.py", "q = IND_NEW_001\n")
    doc = _run(root, cache=cache)["doc"]
    e = _entry(doc, "IND-NEW-001")
    assert e["state"] == "active", "缓存未失效 ⇒ 新实体被误判孤岛（假上架无客）"
    assert e["consumer_files"] == ["src/zephyr/factor/uses_new.py"]
    # 缓存签名必须落册（可核对判据版本）
    # 缓存签名必须落册并与台账记录一致（台账只存前 12 位，便于人工核对判据版本）
    sig = json.loads(cache.read_text(encoding="utf-8")).get("signature")
    assert sig and sig.startswith(doc["runtime"]["token_signature"])


# ── R-G 单一 scope 谓词 ──────────────────────────────────────────────────────
@pytest.mark.parametrize("rel,expect", [
    ("src/zephyr/factor/x.py", True),          # 代码消费者
    ("scripts/backtest/run_eval.py", True),    # scripts 算消费者（§3.4 明判）
    ("config/trading_decision_map.yaml", True),  # config 算消费者
    ("docs/library/INDEX.md", False),          # docs/.md 永不算
    ("src/zephyr/notes.md", False),            # .md 即使在 src/ 也不算
    ("src/zephyr/frontend/dashboard/app_panel.py", False),   # display 层
    ("scripts/ch/apply_market_tables_ddl.py", False),         # infra 层（scope 外）
    ("src/zephyr/data/implementations/p.py", False),          # producer 层（scope 外）
])
def test_single_scope_constant_predicate(rel, expect):
    assert cc.CONSUMER_SCAN_SCOPE.counts_as_consumer(rel) is expect
    assert cc.scope_verdict(rel) is expect


def test_scope_is_a_single_named_constant():
    """口径只此一处：任何族配置不得自带 roots/suffixes 副本（防再分叉）。"""
    # 壬道收敛后 roots= 常量唯一宿主=scan_scope_converged（census 禁再派生口径值，
    # 见 consumption_census [INVARIANTS]）；本断言随迁至唯一真源文件（20260928 接管袋）。
    import zephyr.governance.consumption.scan_scope_converged as ssc

    src = Path(ssc.__file__).read_text(encoding="utf-8")
    assert src.count('roots=(') == 2   # 消费者面 + 文档证据面（后者仅 .md）
    assert 'roots=(' not in Path(cc.__file__).read_text(encoding="utf-8")
    for fam in cc.FAMILY_SPECS:
        assert not hasattr(fam, "roots")


# ── R-H 价值公式 ─────────────────────────────────────────────────────────────
def test_island_ranking_follows_explicit_formula(tmp_path):
    root = _synth_repo(tmp_path)
    _w(root, f"{CAT}/technical_indicator_registry.yaml",
       "tier: 3\nindicators:\n"
       "  - indicator_id: IND-HIGH-001\n    name: hi\n    status: active\n    tier: 5\n"
       "    used_by_factors: [F1, F2, F3]\n    code_path: src/zephyr/factor/h.py\n"
       "  - indicator_id: IND-BARE-001\n    name: lo\n    status: active\n    tier: 1\n",
       )
    doc = _run(root)["doc"]
    hi = _entry(doc, "IND-HIGH-001")
    lo = _entry(doc, "IND-BARE-001")
    assert hi["value_score"] > lo["value_score"]
    scores = [i["value_score"] for i in doc["islands"]]
    assert scores == sorted(scores, reverse=True)
    for i in doc["islands"]:
        assert i["proof_cmd"].startswith("grep -rn")
        assert i["suggested_wiring_target"]


# ── R-J 事件触发 reconciler ───────────────────────────────────────────────────
class _Host:
    def __init__(self, root: Path):
        self.project_root = root


def test_reconciler_is_event_triggered_and_alarms_on_new_island(tmp_path):
    # 单行 from-import 系刻意写法：ORPHAN-MODULE 用行级 grep 认 `from X import Y`，
    # 括号多行 import 匹配不到 → reconciler 被判孤儿（实证死信 q-…-0004 与
    # q-20260923-st-e2e-20260924-0001 同族）。
    from zephyr.governance.consumption.consumption_census_reconciler import make_consumption_census_reconciler, make_external_reconciler_spec  # noqa: I001,F401

    root = _synth_repo(tmp_path)
    (root / CAT).mkdir(parents=True, exist_ok=True)
    spec = make_external_reconciler_spec(_Host(root))
    assert spec.gate_id == "GATE-CONSUMPTION-CENSUS"
    assert spec.file_ops == frozenset({"read", "write"})   # T1① 声明制
    # 触发面＝登记册变更，无关文件不触发（禁 cron/Timer，宪法 §9.3）
    assert spec.trigger([str(root / CAT / "technical_indicator_registry.yaml")]) is True
    assert spec.trigger([str(root / "src/zephyr/unrelated_note.txt")]) is False

    res = spec.reconcile([str(root / CAT / "technical_indicator_registry.yaml")], "s1")
    assert res.action == "warn"                      # 新岛（IND-ORPHAN-001）必报警
    assert "IND-ORPHAN-001" in res.detail or "上架无客" in res.detail
    ledger = root / "data/runtime/consumption_census_ledger.json"
    assert ledger.exists()
    # 台账已在册 ⇒ 再跑无新岛=clean（自终止，不自环）
    res2 = spec.reconcile([str(root / CAT / "technical_indicator_registry.yaml")], "s2")
    assert res2.action == "clean"


def test_reconciler_guardrail_marker_present():
    """护栏：make_*_reconciler 的 def 上方 5 行内必有 # trae_060-reviewed: 结论。"""
    p = Path(cc.__file__).with_name("consumption_census_reconciler.py")
    lines = p.read_text(encoding="utf-8").splitlines()
    for i, ln in enumerate(lines):
        if re.match(r"def make_\w*reconciler", ln.strip()) or \
           re.match(r"def make_external_reconciler_spec", ln.strip()):
            window = "\n".join(lines[max(0, i - 6):i])
            assert "trae_060-reviewed:" in window, f"缺护栏注释: {ln}"


# ── R-K wiring_registry 机器视图 ─────────────────────────────────────────────
def test_generator_books_islands_with_existing_vocabulary(tmp_path, monkeypatch):
    import importlib.util

    root = _synth_repo(tmp_path)
    _w(root, f"{CAT}/wiring_registry.yaml",
       "version: '1.0.0'\nclasses: {pure_library: '纯库'}\nmodules:\n"
       "- candidate_id: CAND-1\n  name: n\n  path: src/zephyr/a.py\n"
       "  domain: D_ALT_DATA\n  wiring_class: pure_library\n  wiring_status: exempt\n")
    ledger = root / "data/runtime/consumption_census_ledger.json"
    _run(root, out=ledger)
    script = Path(cc.__file__).resolve().parents[2] / "scripts/governance/d3_metadata/generate_wiring_registry.py"
    if not script.exists():
        script = Path(__file__).resolve().parents[2] / "scripts/governance/d3_metadata/generate_wiring_registry.py"
    spec_ = importlib.util.spec_from_file_location("gen_wiring", script)
    mod = importlib.util.module_from_spec(spec_)
    spec_.loader.exec_module(mod)
    out = root / "out.yaml"
    rc = mod.main(["--repo-root", str(root), "--out", str(out), "--top", "5"])
    assert rc == 0
    import yaml

    view = yaml.safe_load(out.read_text(encoding="utf-8"))
    booked = view["consumption_islands"]
    assert booked and all(b["wiring_status"] in {"unwired", "wired", "exempt"} for b in booked)
    assert {"IND-ORPHAN-001", "IND-RED-001"} <= {b["entity_id"] for b in booked} or \
           any(b["entity_id"].startswith("IND-") for b in booked)
    assert view["generator"] == mod.GEN_PATH_COMMENT        # 假声明归真
    assert "modules" in view and view["modules"][0]["wiring_status"] == "exempt"  # 原样保留

    # --check：账面缺项＝漂移 rc=1；入账后 rc=0
    prod = root / CAT / "wiring_registry.yaml"
    assert mod.main(["--repo-root", str(root), "--registry", str(prod), "--check"]) == 1
    _w(root, f"{CAT}/wiring_registry.yaml", out.read_text(encoding="utf-8"))
    assert mod.main(["--repo-root", str(root), "--registry", str(prod), "--check"]) == 0

    # 入账后的孤岛补上一个真消费者 ⇒ 必离开 unwired 账面，并以既有词表 wired 记回填事件
    healed = "IND-ORPHAN-001"
    _w(root, "src/zephyr/factor/heal_orphan.py", f"z = {healed.replace('-', '_')}\n")
    _run(root, out=ledger)
    out2 = root / "out2.yaml"
    mod.main(["--repo-root", str(root), "--out", str(out2), "--top", "5"])
    view2 = yaml.safe_load(out2.read_text(encoding="utf-8"))
    assert healed not in {b["entity_id"] for b in view2["consumption_islands"]
                          if b["wiring_status"] == "unwired"}
    assert healed in {t["entity_id"] for t in view2["island_transitions"]}
    assert all(t["wiring_status"] == "wired" for t in view2["island_transitions"])
