# [BLUEPRINT] MOD-BT-199 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.strategy_pipeline.test_promotion_advisory
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.strategy_pipeline.promotion_advisory
# [CONSUMERS] MOD-BT-199 循环验收（S12 C4）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 测试隔离零生产 IO（证据树/注册表/建议目录全 tmp_path 注入）；token 全程假值注入
#   （禁读真实密钥）；alerter 一律 fake（禁真 webhook/真 failure 文件）
# [MODIFY-GUARD] src/zephyr/strategy_pipeline/promotion_advisory.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红
# [TESTS] 本文件
# [A_module] module_id=MOD-BT-199 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""转正建议包测试（S12 C4）：三路证据合流/幂等/decide 全流程/token 三态/已决拒绝/alerter 降级。"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zephyr.strategy_pipeline import promotion_advisory as pa  # noqa: E402

TOKEN = "test-owner-token-abc123"  # 假值注入——测试禁读真实密钥


# ---------- 夹具：tmp 证据树 + 模块常量重定向 ----------
@pytest.fixture(autouse=True)
def alerter_calls(monkeypatch):
    """全文件 alerter 假件（autouse）：decide/建议推送回执零真通道零真 failure 文件。"""
    import zephyr.data.alerter as al

    calls: list[dict] = []

    def notify(self, task_id, error, level="ERROR", source=None, extra=None):
        calls.append({"task_id": task_id, "error": error, "level": level})
        return True

    monkeypatch.setattr(al.Alerter, "notify", notify)
    return calls


def _cand(n: str) -> str:
    """屏侧候选 id（衰减台账与 fdr_keep 都按它建行）。"""
    return f"CAND-0000000000{n}"


def _src_file(n: str) -> str:
    """翻译件路径（注册表 code_path ↔ strategy_screen source_file 联查锚）。"""
    return f"scripts/backtest/translated/c4_0000000000{n}_test.py"


def _bothwin_item(n: str) -> dict:
    """fetch_bothwin 产物行形状（§8 双窗及格集成员）。"""
    return {"key": f"{_cand(n)}@{_src_file(n).rsplit('/', 1)[-1]}",
            "strategy_id": _cand(n), "source_file": _src_file(n),
            "is_sharpe": 1.1, "segments": [{"batch": "OOS-2024", "sharpe": 0.8, "decay": 0.1}]}


def _preauth(n: str = "1", *, dual: bool = True, fdr: bool = True, decay: str = "certified") -> dict:
    """SIM 预授权三条件实据注入位（PA-1）；dual/fdr=False 或 decay=None/越线=该路证据拆掉。"""
    fdr_keys = {_bothwin_item(n)["key"]} if fdr else set()
    states = {_cand(n): decay} if decay else {}
    return {
        "bothwin_items": [_bothwin_item(n)] if dual else [],
        "fdr_keys": fdr_keys,
        "decay_states": states,
    }


def _intake_report(dir_: Path, name: str, keep: list[str]) -> None:
    dir_.mkdir(parents=True, exist_ok=True)
    (dir_ / name).write_text(
        yaml.safe_dump({"fdr_keep": keep}, allow_unicode=True), encoding="utf-8")


def _decay_ledger(path: Path, states: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"schema": "strategy_decay/2", "updated_at": "2026-09-17",
                                "strategies": {k: {"state": v} for k, v in states.items()}}),
                    encoding="utf-8")


def _reg_entries(states: dict[str, str]) -> str:
    """真册同形条目（两空格缩进+双引号标量，registry_writer 渲染约定）。

    PA-1：条目须带 code_path/aliases——三条件实据的注册表锚点，缺锚点即"证据缺位=不通过"。
    """
    out = []
    for sid, state in states.items():
        n = sid[-1]
        out.append(
            f'  - strategy_id: "{sid}"\n'
            f'    name_zh: "测试策略 {sid}"\n'
            f'    aliases: ["{_cand(n)}"]\n'
            f'    code_path: "{_src_file(n)}"\n'
            f'    lifecycle_status: "{state}"\n'
            "    updated_at: 2026-09-01\n"
        )
    return "".join(out)


def _write_reg(path: Path, states: dict[str, str]) -> None:
    path.write_text("strategies:\n" + _reg_entries(states), encoding="utf-8")


@pytest.fixture()
def tree(tmp_path, monkeypatch):
    """tmp 证据树：runs/fw-auto/sim-memos/advisories/registry 全在 tmp_path，零生产 IO。"""
    runs = tmp_path / "runs"
    fw = tmp_path / "fw-auto"
    memo = tmp_path / "sim-memos"
    adv = tmp_path / "advisories"
    for d in (runs, fw, memo, adv):
        d.mkdir(parents=True)
    reg = tmp_path / "strategy_registry.yaml"
    _write_reg(reg, {f"STR-SIM-00{i}": "sim" for i in (1, 2, 3, 4, 5)})
    monkeypatch.setattr(pa, "RUNS_DIR", runs)
    monkeypatch.setattr(pa, "FW_DIR", fw)
    monkeypatch.setattr(pa, "MEMO_DIR", memo)
    monkeypatch.setattr(pa, "ADVISORY_DIR", adv)
    monkeypatch.setattr(pa, "REGISTRY", reg)
    # PA-1 两路只读证据源也钉到 tmp（禁读真 intake 批报告/真衰减台账）
    monkeypatch.setattr(pa, "INTAKE_REPORT_DIR", tmp_path / "intake-reports")
    monkeypatch.setattr(pa, "DECAY_LEDGER", tmp_path / "strategy_decay_ledger.json")
    return {"runs": runs, "fw": fw, "memo": memo, "adv": adv, "reg": reg,
            "intake": tmp_path / "intake-reports", "ledger": tmp_path / "strategy_decay_ledger.json"}


def _gov_run(runs: Path, run_id: str, recs: list[dict]) -> None:
    d = runs / run_id / "04_wide"
    d.mkdir(parents=True)
    (d / "sim_governance_advice.json").write_text(
        json.dumps({"recommendations": recs}, ensure_ascii=False), encoding="utf-8")


def _dev_run(runs: Path, run_id: str, rows: list[dict]) -> None:
    d = runs / run_id / "04_wide"
    d.mkdir(parents=True)
    (d / "deviation_report.json").write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")


def _fw_evidence(fw: Path) -> None:
    (fw / "latest.json").write_text(json.dumps({
        "run": {"run_id": "bt-fw-test0001",
                "core_metrics": {"sharpe_ratio": 0.47, "max_drawdown": 0.11,
                                 "total_return": 0.107},
                "panel_reconciliation": {"within_tolerance": True}},
    }, ensure_ascii=False), encoding="utf-8")


def _seed_promote_tree(tree: dict) -> None:
    """STR-SIM-001: governance promote_paper（2 月 pass 判定史）；STR-SIM-002: demote 兜底；
    STR-SIM-003: 2 月 pass 无治理建议→promote 兜底；STR-SIM-005: 无建议→hold 不产包。"""
    _gov_run(tree["runs"], "SCR-SIMGOV-20260915-010101", [
        {"strategy_id": "STR-SIM-001", "recommendation": "promote_paper", "why": "连续 2 月月度通过"},
        {"strategy_id": "STR-SIM-005", "recommendation": None, "why": "中性"},
    ])
    _dev_run(tree["runs"], "SCR-DEV-20260901-000001", [
        {"strategy_id": "STR-SIM-001", "month": "2026-07", "ok": True},
        {"strategy_id": "STR-SIM-001", "month": "2026-08", "ok": True},
        {"strategy_id": "STR-SIM-003", "month": "2026-07", "ok": True},
        {"strategy_id": "STR-SIM-003", "month": "2026-08", "ok": True},
        {"strategy_id": "STR-SIM-002", "month": "2026-07", "ok": False},
        {"strategy_id": "STR-SIM-002", "month": "2026-08", "ok": False},
    ])
    # 同月重跑（(sid,month) 去重取最新 run）+ 跨 run 分裂行
    _dev_run(tree["runs"], "SCR-DEV-20260915-000002", [
        {"strategy_id": "STR-SIM-003", "month": "2026-08", "ok": True},
        {"strategy_id": "STR-SIM-001", "month": "2026-09", "ok": True},
    ])
    _fw_evidence(tree["fw"])
    (tree["memo"] / "sim-memo-202609.json").write_text("{}", encoding="utf-8")


def _fake_alerter(monkeypatch, calls: list | None = None) -> None:
    import zephyr.data.alerter as al

    def notify(self, task_id, error, level="ERROR", source=None, extra=None):
        if calls is not None:
            calls.append({"task_id": task_id, "level": level})
        return True

    monkeypatch.setattr(al.Alerter, "notify", notify)


_TODAY = pa.now_utc().strftime("%Y%m%d")  # 本地与 UTC 可能跨日——advisory_id 日期必须同源


class TestBuildAdvisories:
    def test_three_evidence_merge_and_fields(self, tree):
        _seed_promote_tree(tree)
        out = pa.build_advisories()
        by_sid = {a["strategy_id"]: a for a in out}
        # promote（治理建议直映）+ demote（判定史兜底）+ promote（兜底）；hold 不产包
        assert set(by_sid) == {"STR-SIM-001", "STR-SIM-002", "STR-SIM-003"}
        a1 = by_sid["STR-SIM-001"]
        assert a1["advisory_id"] == f"ADV-{_TODAY}-STR-SIM-001"
        assert a1["recommendation"] == "promote"
        assert a1["lifecycle_now"] == "sim"
        ev = a1["evidence"]
        assert ev["sim_pass_months"] == 3 and ev["sim_breach_months"] == 0
        assert ev["fw_backtest"] == {"run_id": "bt-fw-test0001", "sharpe": 0.47,
                                     "max_dd": 0.11, "total_return": 0.107, "panel_ok": True}
        assert ev["governance_action"] == "promote_paper"
        assert ev["memo_ref"].endswith("sim-memo-202609.json")
        assert "generated_at" in a1 and "T" in a1["generated_at"]
        # 落盘契约：ADV-<yyyymmdd>-<STR-ID>.json
        f = tree["adv"] / f"{a1['advisory_id']}.json"
        assert f.is_file() and json.loads(f.read_text(encoding="utf-8"))["advisory_id"] == a1["advisory_id"]
        assert by_sid["STR-SIM-002"]["recommendation"] == "demote"
        assert by_sid["STR-SIM-003"]["recommendation"] == "promote"
        assert by_sid["STR-SIM-003"]["evidence"]["governance_action"] is None

    def test_idempotent_same_day_no_file_pileup(self, tree):
        _seed_promote_tree(tree)
        first = pa.build_advisories()
        again = pa.build_advisories()
        files = sorted(tree["adv"].glob("ADV-*.json"))
        assert len(files) == len(first) == len(again) == 3  # 覆盖不堆叠

    def test_hold_strategy_no_package(self, tree):
        _gov_run(tree["runs"], "SCR-SIMGOV-20260915-010101",
                 [{"strategy_id": "STR-SIM-005", "recommendation": None, "why": "中性"}])
        assert pa.build_advisories() == []
        assert list(tree["adv"].glob("ADV-*.json")) == []

    def test_missing_evidence_sources_degrade(self, tree):
        """三路证据全缺：不抛、零包（兜底 hold 不产包）。"""
        assert pa.build_advisories() == []


class TestRunPromotionAdvisoryDue:
    def test_pushes_promote_only_via_alerter(self, tree, monkeypatch):
        _seed_promote_tree(tree)
        calls: list[dict] = []
        _fake_alerter(monkeypatch, calls)
        out = pa.run_promotion_advisory_due({"id": "E1"})
        assert out["event_id"] == "E1" and out["built"] == 3
        assert len(out["pushed"]) == 2  # 两个 promote（demote 不推）
        assert all(c["task_id"].startswith("promotion_advisory-ADV-") for c in calls)
        assert all(c["level"] == "ERROR" for c in calls)

    def test_alerter_down_degrades_no_raise(self, tree, monkeypatch):
        _seed_promote_tree(tree)
        import zephyr.data.alerter as al

        def boom(self, *a, **k):
            raise RuntimeError("webhook down")

        monkeypatch.setattr(al.Alerter, "notify", boom)
        out = pa.run_promotion_advisory_due({"id": "E2"})  # 不抛=降级成立
        assert out["built"] == 3 and out["pushed"] == []
        assert len(list(tree["adv"].glob("ADV-*.json"))) == 3  # 包仍在盘上


class TestDecide:
    def _adv(self, tree, sid="STR-SIM-001", rec="promote") -> str:
        adv = {"advisory_id": f"ADV-{_TODAY}-{sid}", "strategy_id": sid,
               "lifecycle_now": "sim",
               "evidence": {"sim_pass_months": 2, "sim_breach_months": 0,
                            "fw_backtest": None, "governance_action": None,
                            "memo_ref": None},
               "recommendation": rec, "generated_at": "2026-09-15T00:00:00+00:00"}
        (tree["adv"] / f"{adv['advisory_id']}.json").write_text(
            json.dumps(adv, ensure_ascii=False), encoding="utf-8")
        return adv["advisory_id"]

    def test_full_flow_server_token_approve(self, tree, monkeypatch):
        monkeypatch.setenv("ZEPHYR_OWNER_APPROVAL_TOKEN", TOKEN)
        calls: list[dict] = []
        _fake_alerter(monkeypatch, calls)
        aid = self._adv(tree)
        out = pa.decide(aid, "approve", token=None, via="frontend",  # token=None=服务端自取
                        advisory_dir=tree["adv"], registry_path=tree["reg"],
                        sim_evidence=_preauth("1"))  # PA-1：candidate→sim 三条件实据
        assert out["ok"] is True and out["decision"] == "approve"
        assert out["fsm"] == {"from": "sim", "to": "production"}
        assert out["sim_preauthorization"]["mode"] == "evidence"
        assert out["registry"]["lifecycle_status"] == "production"
        # 注册表真变 + 他条目零触碰
        reg = yaml.safe_load(tree["reg"].read_text(encoding="utf-8"))
        lc = {s["strategy_id"]: s["lifecycle_status"] for s in reg["strategies"]}
        assert lc["STR-SIM-001"] == "production" and lc["STR-SIM-002"] == "sim"
        # 台账：token 指纹留痕，明文绝不落盘
        ledger = json.loads((tree["adv"] / f"{aid}.decision.json").read_text(encoding="utf-8"))
        assert ledger["token_fingerprint"] == hashlib.sha256(TOKEN.encode()).hexdigest()[:12]
        assert ledger["via"] == "frontend" and ledger["decision"] == "approve"
        assert TOKEN not in json.dumps(ledger)
        assert calls and calls[0]["task_id"] == f"promotion_decision-{aid}"

    def test_explicit_token_correct_and_wrong(self, tree, monkeypatch):
        monkeypatch.setenv("ZEPHYR_OWNER_APPROVAL_TOKEN", TOKEN)
        aid = self._adv(tree)
        bad = pa.decide(aid, "approve", token="wrong-token",
                        advisory_dir=tree["adv"], registry_path=tree["reg"])
        assert bad == {"ok": False, "advisory_id": aid, "reason": "invalid_token"}
        assert not (tree["adv"] / f"{aid}.decision.json").exists()  # 拒门不落台账
        good = pa.decide(aid, "approve", token=TOKEN,
                         advisory_dir=tree["adv"], registry_path=tree["reg"],
                         sim_evidence=_preauth("1"))
        assert good["ok"] is True and good["fsm"]["to"] == "production"

    def test_token_unconfigured_fail_closed(self, tree, monkeypatch):
        monkeypatch.delenv("ZEPHYR_OWNER_APPROVAL_TOKEN", raising=False)
        aid = self._adv(tree)
        for tok in (None, "any-nonempty-token"):
            out = pa.decide(aid, "approve", token=tok,
                            advisory_dir=tree["adv"], registry_path=tree["reg"])
            assert out["ok"] is False and out["reason"] == "owner_token_not_configured"
        assert not (tree["adv"] / f"{aid}.decision.json").exists()
        reg = yaml.safe_load(tree["reg"].read_text(encoding="utf-8"))
        assert reg["strategies"][0]["lifecycle_status"] == "sim"  # 注册表零触碰

    def test_already_decided_rejects(self, tree, monkeypatch):
        monkeypatch.setenv("ZEPHYR_OWNER_APPROVAL_TOKEN", TOKEN)
        aid = self._adv(tree)
        first = pa.decide(aid, "approve", advisory_dir=tree["adv"], registry_path=tree["reg"],
                          sim_evidence=_preauth("1"))
        assert first["ok"] is True
        again = pa.decide(aid, "approve", advisory_dir=tree["adv"], registry_path=tree["reg"])
        assert again["ok"] is False and again["reason"] == "already_decided"
        # 幂等复核：注册表仍 production，未被二次流转
        reg = yaml.safe_load(tree["reg"].read_text(encoding="utf-8"))
        assert reg["strategies"][0]["lifecycle_status"] == "production"

    def test_reject_records_ledger_no_transition(self, tree, monkeypatch):
        monkeypatch.setenv("ZEPHYR_OWNER_APPROVAL_TOKEN", TOKEN)
        aid = self._adv(tree)
        out = pa.decide(aid, "reject", advisory_dir=tree["adv"], registry_path=tree["reg"])
        assert out["ok"] is True and out["fsm"] is None and out["registry"] is None
        reg = yaml.safe_load(tree["reg"].read_text(encoding="utf-8"))
        assert reg["strategies"][0]["lifecycle_status"] == "sim"

    def test_demote_approve_flows_to_shelved(self, tree, monkeypatch):
        """PA-1 反向不变量：降档是风险收敛动作，零晋升证据也必须放行（不被预授权反向卡住）。"""
        monkeypatch.setenv("ZEPHYR_OWNER_APPROVAL_TOKEN", TOKEN)
        aid = self._adv(tree, sid="STR-SIM-002", rec="demote")
        out = pa.decide(aid, "approve", advisory_dir=tree["adv"], registry_path=tree["reg"])
        assert out["ok"] is True and out["fsm"] == {"from": "candidate", "to": "shelved"}
        assert out["sim_preauthorization"]["mode"] == "not_required"
        assert out["registry"]["lifecycle_status"] == "shelved"

    def test_invalid_inputs(self, tree, monkeypatch):
        monkeypatch.setenv("ZEPHYR_OWNER_APPROVAL_TOKEN", TOKEN)
        with pytest.raises(ValueError):
            pa.decide("ADV-X", "maybe", advisory_dir=tree["adv"])
        with pytest.raises(FileNotFoundError):
            pa.decide(f"ADV-{_TODAY}-STR-NOPE-999", "approve",
                      advisory_dir=tree["adv"], registry_path=tree["reg"])
        # lifecycle 已非观察态（candidate）→ 拒绝且不落台账
        _write_reg(tree["reg"], {"STR-SIM-001": "sim", "STR-SIM-002": "sim",
                                 "STR-SIM-004": "candidate"})
        aid = self._adv(tree, sid="STR-SIM-004")
        out = pa.decide(aid, "approve", advisory_dir=tree["adv"], registry_path=tree["reg"])
        assert out["ok"] is False and out["reason"] == "invalid_lifecycle"
        assert not (tree["adv"] / f"{aid}.decision.json").exists()


class TestListAdvisories:
    def test_lists_with_decision_status(self, tree, alerter_calls):
        _seed_promote_tree(tree)
        pa.build_advisories()
        assert len(pa.list_advisories(tree["adv"])) == 3
        assert all("decision" not in a for a in pa.list_advisories(tree["adv"]))
        monkey_token = pytest.MonkeyPatch()
        try:
            monkey_token.setenv("ZEPHYR_OWNER_APPROVAL_TOKEN", TOKEN)
            row0 = pa.list_advisories(tree["adv"])[0]
            aid = row0["advisory_id"]
            # PA-1：promote 拍板须带三条件实据（缺证据=fail-closed 拒绝），demote 不需要
            out = pa.decide(aid, "approve", advisory_dir=tree["adv"],
                            registry_path=tree["reg"],
                            sim_evidence=_preauth(row0["strategy_id"][-1]))
            assert out["ok"] is True, out
        finally:
            monkey_token.undo()
        rows = {a["advisory_id"]: a for a in pa.list_advisories(tree["adv"])}
        assert rows[aid]["decision"]["decision"] == "approve"
        # 台账只带指纹不带明文（token_fingerprint 键=指纹，明文值绝不出现在台账 JSON）
        ledger_json = json.dumps(rows[aid]["decision"])
        assert rows[aid]["decision"]["token_fingerprint"] == hashlib.sha256(
            TOKEN.encode()).hexdigest()[:12]
        assert TOKEN not in ledger_json


def test_decide_rejected_when_kill_switch_active(tmp_path, monkeypatch):
    """红蓝：总闸激活时拍板必须拒（fail-closed），且不落台账。"""
    import json

    import zephyr.strategy_pipeline.promotion_advisory as pa

    adv_dir = tmp_path / "advisories"
    adv_dir.mkdir()
    (adv_dir / "ADV-TEST-KS.json").write_text(json.dumps({
        "advisory_id": "ADV-TEST-KS", "strategy_id": "STR-X", "recommendation": "promote",
    }, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setenv("ZEPHYR_OWNER_APPROVAL_TOKEN", "tok-ks")
    monkeypatch.setattr(pa, "_kill_switch_clear", lambda: (False, "manual"))
    r = pa.decide("ADV-TEST-KS", "approve", token="tok-ks", advisory_dir=adv_dir)
    assert r["ok"] is False and "kill_switch" in r["reason"]
    assert not (adv_dir / "ADV-TEST-KS.decision.json").exists()
