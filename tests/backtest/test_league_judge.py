# [BLUEPRINT] MOD-AUTO-L11-JUDGE | docs/_working/fullflow_mining/03_promotion_ab/02_ab_league.md | 堵点2/3 测试
# [MODULE] tests.backtest.test_league_judge
# [DOMAIN] D_BACKTEST
# [INVARIANTS] 零 CH/网络触碰（query_fn 全 mock）; 全部 IO 走 tmp_path fixture（宪法测试隔离铁律，
#   禁写生产路径）; 判据三态/v2 尺对账/族守门/ρ 闸/空场诚实逐条钉值
# [TTL] permanent
"""league_judge 测试——判据三态/v2 尺对账/BHY 族守门/ρ 闸/空场诚实/登记与判定书落档。"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
for _p in (str(REPO_ROOT / "scripts" / "backtest"), str(REPO_ROOT / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import league_judge as lj  # noqa: E402
import league_registry as lr  # noqa: E402

# --------------------------------------------------------------------------- fixtures


def _standards(v2_status: str = "frozen", switch_status: str = "draft", rho: float = 0.7) -> dict:
    return {
        "standards": [
            {
                "std_id": "STD-SIM-ACCESS-002",
                "status": v2_status,
                "frozen_at": "2026-09-18" if v2_status == "frozen" else None,
                "thresholds": {"dsr_min": 0.5, "combo_corr_max": 0.7},
            },
            {
                "std_id": "STD-SWITCH-001",
                "status": switch_status,
                "thresholds": {
                    "pair_decision_engine": "msprt",
                    "league_family_scope": "league_batch",
                    "correlation_gate_rho": rho,
                },
            },
        ]
    }


def _write_standards(tmp_path: Path, data: dict) -> Path:
    p = tmp_path / "standards.yaml"
    p.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    return p


def _registry_data(members_a: list | None = None, members_b: list | None = None) -> dict:
    return {
        "schema_version": "0.1.0",
        "title": "A/B 联赛注册表（测试）",
        "review_policy": {"window_months": 6, "judge": "combo"},
        "groups": [
            {
                "group_id": "A",
                "status": "champion",
                "joined_date": "2026-09-21",
                "members": members_a or [],
                "archive_path": "",
                "review_window": {"start": "2026-09-21", "months": 6, "due": "2027-03-21"},
            },
            {
                "group_id": "B",
                "status": "challenger",
                "joined_date": "2026-09-21",
                "members": members_b or [],
                "archive_path": "",
                "review_window": {"start": "2026-09-21", "months": 6, "due": "2027-03-21"},
            },
        ],
    }


def _write_registry(tmp_path: Path, data: dict) -> Path:
    p = tmp_path / "league_registry.yaml"
    p.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    return p


def _equity_tsv(dates: list[str], equities: list[float]) -> str:
    return "\n".join(f"{d}\t{e}" for d, e in zip(dates, equities, strict=True))


def _dates(n: int, start_day: int = 1) -> list[str]:
    return [f"2026-09-{i:02d}" for i in range(start_day, start_day + n)]


# --------------------------------------------------------------------------- 尺解析


def test_resolve_rulers_requires_frozen_v2(tmp_path):
    p = _write_standards(tmp_path, _standards(v2_status="draft"))
    with pytest.raises(ValueError, match="非 frozen"):
        lj.resolve_rulers(lj.load_standards(p))
    # 尺缺失同拒（fail-closed）
    p2 = _write_standards(tmp_path, {"standards": [{"std_id": "STD-SWITCH-001", "status": "frozen", "thresholds": {}}]})
    with pytest.raises(ValueError, match="尺缺失"):
        lj.resolve_rulers(lj.load_standards(p2))


def test_resolve_rulers_draft_switch_noted(tmp_path):
    p = _write_standards(tmp_path, _standards(switch_status="draft", rho=0.65))
    r = lj.resolve_rulers(lj.load_standards(p))
    assert r["draft_ruler"] is True
    assert r["rho_max"] == pytest.approx(0.65)  # 阈值动态读尺（禁硬编码漂移）
    assert "draft" in r["ruler_note"]


# --------------------------------------------------------------------------- 判据三态


def _mock_query(series: dict[str, list[tuple[str, float]]]):
    def q(_sql: str):
        for sid, rows in series.items():
            if f"strategy_id = '{sid}'" in _sql:
                return _equity_tsv([d for d, _ in rows], [e for _, e in rows])
        return ""

    return q


def test_verdict_promote(tmp_path):
    # challenger 日均显著跑赢 champion → msprt 晋升 + BHY 拒绝 → promote
    n = 60
    dates = _dates(n)
    champ = [(d, 100.0 * (1.0001**i)) for i, d in enumerate(dates)]
    chall = [(d, 100.0 * (1.0100**i)) for i, d in enumerate(dates)]
    rulers = lj.resolve_rulers(lj.load_standards(_write_standards(tmp_path, _standards())))
    out = lj.judge_pair("CHAMPA", "CHALLB", rulers, query_fn=_mock_query({"CHAMPA": champ, "CHALLB": chall}))
    assert out["msprt_decision"] == "promote"
    assert out["verdict"] == "promote"
    assert out["n_samples"] == n - 1
    assert out["mean_delta"] > 0
    guarded = lj.apply_family_guard([out], rulers)
    assert guarded[0]["bhy_rejected"] is True  # 单对族 p=min(1,1/M) 极小 → BHY 拒绝


def test_verdict_eliminate(tmp_path):
    n = 60
    dates = _dates(n)
    champ = [(d, 100.0 * (1.0100**i)) for i, d in enumerate(dates)]
    chall = [(d, 100.0 * (0.9900**i)) for i, d in enumerate(dates)]
    rulers = lj.resolve_rulers(lj.load_standards(_write_standards(tmp_path, _standards())))
    out = lj.judge_pair("CHAMPA", "CHALLB", rulers, query_fn=_mock_query({"CHAMPA": champ, "CHALLB": chall}))
    assert out["msprt_decision"] == "eliminate"
    assert out["verdict"] == "eliminate"
    assert out["mean_delta"] < 0


def test_verdict_observe_insufficient_samples(tmp_path):
    n = 20  # < 30 配对样本=终局最小样本门
    dates = _dates(n)
    champ = [(d, 100.0 * (1.0100**i)) for i, d in enumerate(dates)]
    chall = [(d, 100.0 * (1.0200**i)) for i, d in enumerate(dates)]
    rulers = lj.resolve_rulers(lj.load_standards(_write_standards(tmp_path, _standards())))
    out = lj.judge_pair("CHAMPA", "CHALLB", rulers, query_fn=_mock_query({"CHAMPA": champ, "CHALLB": chall}))
    assert out["verdict"] == "observe"  # 观察延续（不足终局）
    assert "insufficient_samples" in out["evidence_gaps"]
    assert out["p_value"] is None


def test_verdict_observe_weak_edge(tmp_path):
    # 弱差edge：+2%/-1% 交替（x̄=+0.5%，σ=1.5%）满 30+ 样本，M 处 (1/α, α) 之间 → 观察延续
    n = 40
    champ_dates = _dates(n)
    champ = [(d, 100.0) for d in champ_dates]  # champion 净值平盘（日收益=0）
    chall = [(None, 100.0)]
    eq = 100.0
    for i in range(n - 1):
        r = 0.02 if i % 2 == 0 else -0.01
        eq *= 1.0 + r
        chall.append((None, eq))
    chall = [(champ_dates[i + 1], e) for i, (_, e) in enumerate(chall[1:])]
    rulers = lj.resolve_rulers(lj.load_standards(_write_standards(tmp_path, _standards())))
    out = lj.judge_pair("CHAMPA", "CHALLB", rulers, query_fn=_mock_query({"CHAMPA": champ, "CHALLB": chall}))
    assert out["msprt_decision"] == "observe"
    assert out["verdict"] == "observe"


def test_ch_unreachable_degrades_not_fabricates(tmp_path):
    def broken_q(_sql: str):
        raise RuntimeError("CH TCP down")

    rulers = lj.resolve_rulers(lj.load_standards(_write_standards(tmp_path, _standards())))
    out = lj.judge_pair("CHAMPA", "CHALLB", rulers, query_fn=broken_q)
    assert out["skipped"] is True
    assert out["verdict"] == "observe"
    assert "ch_unreachable" in out["evidence_gaps"]  # 断供=如实降级，禁编造成绩


# --------------------------------------------------------------------------- 族守门+ρ 闸


def test_family_guard_downgrades_uncorroborated_promotion(tmp_path):
    rulers = lj.resolve_rulers(lj.load_standards(_write_standards(tmp_path, _standards())))
    # 两对均 msprt promote 但 p 大（族内无一致强证据）→ BHY 不拒绝 → 降级观察
    pairs = [
        {"champion": "A1", "challenger": "B1", "p_value": 0.30, "msprt_decision": "promote", "verdict": "promote"},
        {"champion": "A1", "challenger": "B2", "p_value": 0.45, "msprt_decision": "promote", "verdict": "promote"},
    ]
    out = lj.apply_family_guard(pairs, rulers)
    assert all(r["verdict"] == "observe" for r in out)
    assert all(r["bhy_rejected"] is False for r in out)
    # 强证据对保留晋升：p=1e-6 单对族 → 拒绝
    strong = [
        {"champion": "A1", "challenger": "B1", "p_value": 1e-6, "msprt_decision": "promote", "verdict": "promote"}
    ]
    out2 = lj.apply_family_guard(strong, rulers)
    assert out2[0]["verdict"] == "promote"
    assert out2[0]["bhy_rejected"] is True


def test_correlation_merge_caps_promotion(tmp_path):
    # 挑战者与 champion 收益完全同构（共享波动+常数差 → ρ=1.0>阈值）→ 合并算一档：晋升封顶观察
    n = 60
    champ_dates = _dates(n)
    champ, chall = [(champ_dates[0], 100.0)], [(champ_dates[0], 100.0)]
    ce, he = 100.0, 100.0
    for i in range(n - 1):
        alt = 0.005 if i % 2 == 0 else -0.005  # 共享波动（同符号同幅）
        ce *= 1.0 + (0.0001 + alt)
        he *= 1.0 + (0.0100 + alt)
        champ.append((champ_dates[i + 1], ce))
        chall.append((champ_dates[i + 1], he))
    rulers = lj.resolve_rulers(lj.load_standards(_write_standards(tmp_path, _standards(rho=0.5))))
    out = lj.judge_pair("CHAMPA", "CHALLB", rulers, query_fn=_mock_query({"CHAMPA": champ, "CHALLB": chall}))
    assert out["correlation_merged"] is True
    assert out["rho"] is not None and out["rho"] > 0.99
    assert out["msprt_decision"] == "promote"
    assert out["verdict"] == "observe"  # 晋升被封顶（淘汰不受闸保护向）
    assert any("correlation_merge" in x for x in out.get("notes", []))


# --------------------------------------------------------------------------- 整场判定+空场诚实


def test_run_judgment_empty_field_honest(tmp_path):
    reg = _write_registry(tmp_path, _registry_data())  # 双组零成员
    j = lj.run_judgment(reg, _write_standards(tmp_path, _standards()), query_fn=lambda _s: "")
    assert j["empty_field"] is True
    assert j["pairs"] == []
    assert j["verdicts"] == {}
    assert j["suggestions"] == []
    assert "空场" in j["note"]
    md = lj.render_markdown(j)
    assert "空场" in md


def test_run_judgment_champion_without_challenger_is_empty(tmp_path):
    # 首位参赛者已入 A 组、B 组仍空 → 零对局=空场诚实（不判不编）
    reg = _write_registry(tmp_path, _registry_data(members_a=["STR-E-TIMING-001"]))
    j = lj.run_judgment(reg, _write_standards(tmp_path, _standards()), query_fn=lambda _s: "")
    assert j["champions"] == ["STR-E-TIMING-001"]
    assert j["empty_field"] is True


def test_run_judgment_pair_flow_and_ruler_echo(tmp_path):
    n = 60
    dates = _dates(n)
    champ = [(d, 100.0 * (1.0001**i)) for i, d in enumerate(dates)]
    chall = [(d, 100.0 * (1.0100**i)) for i, d in enumerate(dates)]
    reg = _write_registry(tmp_path, _registry_data(members_a=["CHAMPA"], members_b=["CHALLB"]))
    std = _write_standards(tmp_path, _standards(rho=0.65))
    j = lj.run_judgment(reg, std, query_fn=_mock_query({"CHAMPA": champ, "CHALLB": chall}))
    assert j["empty_field"] is False
    assert j["rulers"]["correlation_gate_rho"] == pytest.approx(0.65)  # v2 尺/切换尺动态对账
    assert j["rulers"]["access_std_id"] == "STD-SIM-ACCESS-002"
    assert j["rulers"]["access_status"] == "frozen"
    assert j["verdicts"] == {"CHAMPA|CHALLB": "promote"}
    assert len(j["suggestions"]) == 1
    assert "Owner" in j["suggestions"][0]["note"]  # 建议≠决定
    md = lj.render_markdown(j)
    assert "promote" in md and "draft" in md  # 判定书带 draft 尺注记


def test_run_judgment_registry_schema_violation(tmp_path):
    bad = _registry_data()
    bad["groups"][0].pop("review_window")
    reg = _write_registry(tmp_path, bad)
    with pytest.raises(ValueError, match="schema"):
        lj.run_judgment(reg, _write_standards(tmp_path, _standards()), query_fn=lambda _s: "")


# --------------------------------------------------------------------------- 判定书落档


def test_land_judgment_monthly_idempotent(tmp_path):
    reg = _write_registry(tmp_path, _registry_data())
    j = lj.run_judgment(reg, _write_standards(tmp_path, _standards()), query_fn=lambda _s: "")
    out_dir = tmp_path / "judgments"
    p1 = lj.land_judgment(j, out_dir, stamp="2026-09")
    p2 = lj.land_judgment(j, out_dir, stamp="2026-09")
    assert Path(p1[".md"]) == Path(p2[".md"])  # 月度幂等覆盖
    assert json.loads(Path(p1[".json"]).read_text(encoding="utf-8"))["empty_field"] is True
    assert Path(p1[".md"]).read_text(encoding="utf-8").startswith("# A/B 联赛判定书")


# --------------------------------------------------------------------------- 首位参赛者


def _strategy_registry(entries: list) -> dict:
    return {"strategies": entries}


def test_pick_first_sim_contestant(tmp_path):
    p = tmp_path / "strategy_registry.yaml"
    p.write_text(
        yaml.safe_dump(
            _strategy_registry(
                [
                    {"strategy_id": "STR-CAND-001", "lifecycle_status": "candidate", "status": "active"},
                    {"strategy_id": "STR-E-TIMING-001", "lifecycle_status": "sim", "status": "active"},
                    {"strategy_id": "STR-OLD-999", "lifecycle_status": "sim", "status": "retired"},
                ]
            ),
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    assert lj.pick_first_sim_contestant(p) == "STR-E-TIMING-001"  # 注册表序首个 sim+active


def test_pick_first_sim_contestant_empty_honest(tmp_path):
    p = tmp_path / "strategy_registry.yaml"
    p.write_text(
        yaml.safe_dump(
            _strategy_registry(
                [
                    {"strategy_id": "STR-CAND-001", "lifecycle_status": "candidate", "status": "active"},
                ]
            ),
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    assert lj.pick_first_sim_contestant(p) is None  # sim 现役为空=诚实 None（禁编造）


def test_register_member_cas_and_idempotent(tmp_path):
    reg = _write_registry(tmp_path, _registry_data())
    g = lr.register_member("A", "STR-E-TIMING-001", path=reg)
    assert g["members"] == ["STR-E-TIMING-001"]
    # 写后回读核实（文件真实落盘）
    assert lr.get_group(lr.load_registry(reg), "A")["members"] == ["STR-E-TIMING-001"]
    # 幂等：重复入组不重写
    g2 = lr.register_member("A", "STR-E-TIMING-001", path=reg)
    assert g2["members"] == ["STR-E-TIMING-001"]
    # 空清单引用挂载回归（st-c9-f73 实录 bug：`or []` 重建列表 append 落空）
    g3 = lr.register_member("B", "STR-CHALL-001", path=reg)
    assert g3["members"] == ["STR-CHALL-001"]
    assert lr.get_group(lr.load_registry(reg), "B")["members"] == ["STR-CHALL-001"]
    # schema 仍绿
    assert lr.validate_registry(lr.load_registry(reg)) == []


# --------------------------------------------------------------------------- 事件契约接线


def test_optional_due_kind_registered():
    # 注：解释器启动时 usercustomize 预导入主仓 zephyr 模块（worktree 内 import 不可见
    # 本侧未合并修改，st-c9-f73 实测）——接线断言走 worktree 本地文件源码面（零导入）。
    src = (REPO_ROOT / "src" / "zephyr" / "strategy_pipeline" / "pipeline_events.py").read_text(encoding="utf-8")
    # ① 派发表登记（kind → 执行体模块+函数，run_optional_due 契约）
    assert '"league_judge_due": ("scripts.backtest.league_judge", "run_league_judge_due")' in src
    # ② 月度档发射（禁 cron 语义=事件唤醒点 marker 评估）
    assert '("league_judge", "league_judge_due")' in src
    # ③ 消费 marker 触指（失败不触=跨唤醒重评）
    assert 'kind == "league_judge_due"' in src


def test_run_league_judge_due_contract(tmp_path, monkeypatch):
    j = {"empty_field": True, "verdicts": {}, "note": "空场"}
    landed = {".md": str(tmp_path / "j.md"), ".json": str(tmp_path / "j.json")}
    monkeypatch.setattr(lj, "run_judgment", lambda *a, **k: j)
    monkeypatch.setattr(lj, "land_judgment", lambda jj, out_dir=None, stamp=None: landed)
    out = lj.run_league_judge_due({"id": "evt-1"})
    assert out["ok"] is True
    assert out["empty_field"] is True
    assert out["landed"] == landed


def test_script_default_paths_are_file_anchored():
    # 回归钉（st-c9-f73 事故）：默认路径锚定 __file__ 位置，禁 env 注入依赖
    root = Path(lj.__file__).resolve().parents[2]
    assert root / "config" / "league_registry.yaml" == lj.LEAGUE_REGISTRY_PATH
    assert root / "config" / "standards.yaml" == lj.STANDARDS_PATH
