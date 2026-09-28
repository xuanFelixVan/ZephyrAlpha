# [BLUEPRINT] MOD-TEST_LANE_LEASES | scripts/governance/lane_leases.py | §租约模型与影子审计
# [TTL] permanent
# [MODULE] tests.governance.test_lane_leases
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.lane_leases；scripts.governance.lane_leases_gate
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] tmp_path 假册测租约登记+分配器+影子门（S5② v1）：claim 登记/同 sid 覆盖再 claim/他 sid 相交拒绝（含拆分 hint）/段边界感知（zephyr vs zephyr2 不相交、zephyr 与 zephyr/data 相交）/TTL 过期懒清除/心跳续期/release；suggest 分组（目录族域+hot-register 类+N 队 FCFS 贪心不相交+跨队 advisory）；gate 影子审计（no-lease/outside-lease/cross-lease-overlap 三类告警+干净面 rc=0+warn_only 永不阻断语义）；全部假册注入（--leases/函数参数），零生产路径写入
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [A_module] module_id=MOD-TEST_LANE_LEASES | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_lane_leases.py — 路径租约登记+分配器+影子审计门单元测试（S5② 动态车道 v1）

覆盖（全部 tmp_path 假册，零生产路径写入）：
- claim：登记成功；同 sid 再 claim 覆盖合并；他 sid 相交拒绝（rc=1+conflicts+hint）
- 段边界：src/zephyr 与 src/zephyr2 不相交；src/zephyr 与 src/zephyr/data 相交
- TTL：过期租约懒清除（新 sid 可抢同前缀）；heartbeat 续期；release；release 未登记 sid
- suggest：目录族域分组；hot-register 类聚合；N 队 FCFS 贪心不相交；跨队 advisory
- gate：no-lease / outside-lease / cross-lease-overlap 三类告警；干净面 rc=0；warn_only 标记
"""

from __future__ import annotations

import json
import sys
from datetime import timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "governance"))

import lane_leases as ll  # noqa: E402
import lane_leases_gate as llg  # noqa: E402

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _registry(tmp_path: Path) -> Path:
    return tmp_path / "lane_leases.json"


def _forge_lease(tmp_path: Path, sid: str, prefixes: list[str], ttl_offset_seconds: int) -> None:
    """直接写册追加单租约（ttl_offset<0=已过期）；绕过 claim 冲突判定以构造影子测试态。"""
    now = ll._now()
    p = _registry(tmp_path)
    reg, _ = ll.load_registry(p) if p.exists() else (ll._empty_registry(), False)
    reg.setdefault("leases", {})[sid] = {
        "sid": sid,
        "prefixes": prefixes,
        "acquired_at": ll._iso(now - timedelta(minutes=5)),
        "heartbeat_at": ll._iso(now),
        "expires_at": ll._iso(now + timedelta(seconds=ttl_offset_seconds)),
    }
    ll.save_registry(p, reg)


# ---------------------------------------------------------------------------
# claim / 冲突 / 段边界
# ---------------------------------------------------------------------------


def test_claim_ok_and_persisted(tmp_path):
    p = _registry(tmp_path)
    res = ll.op_claim(p, "sA", ["src/zephyr/governance", "docs/_working/camp1/"], 600)
    assert res["ok"] is True and res["rc"] == 0
    assert res["prefixes"] == ["docs/_working/camp1", "src/zephyr/governance"]  # 归一+去尾斜杠+排序
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["leases"]["sA"]["prefixes"] == res["prefixes"]
    assert data["leases"]["sA"]["expires_at"] > data["leases"]["sA"]["heartbeat_at"]


def test_claim_same_sid_reclaim_ok(tmp_path):
    p = _registry(tmp_path)
    assert ll.op_claim(p, "sA", ["src/zephyr/a"], 600)["ok"]
    res = ll.op_claim(p, "sA", ["src/zephyr/b", "src/zephyr/a"], 600)
    assert res["ok"] is True
    assert res["prefixes"] == ["src/zephyr/a", "src/zephyr/b"]


def test_claim_conflict_other_sid_rejected_with_hint(tmp_path):
    p = _registry(tmp_path)
    assert ll.op_claim(p, "sA", ["src/zephyr/governance"], 600)["ok"]
    res = ll.op_claim(p, "sB", ["src/zephyr/governance/data"], 600)
    assert res["ok"] is False and res["rc"] == 1
    assert res["conflicts"][0]["sid"] == "sA"
    assert res["conflicts"][0]["overlapping_requested"] == ["src/zephyr/governance/data"]
    assert "hint" in res
    # 拒绝后册未被污染（sB 未入册）
    data = json.loads(p.read_text(encoding="utf-8"))
    assert "sB" not in data["leases"]


def test_claim_segment_boundary_no_false_conflict(tmp_path):
    p = _registry(tmp_path)
    assert ll.op_claim(p, "sA", ["src/zephyr"], 600)["ok"]
    # src/zephyr2 与 src/zephyr 段边界不相交
    res = ll.op_claim(p, "sB", ["src/zephyr2"], 600)
    assert res["ok"] is True


def test_prefix_covers_semantics():
    assert ll.prefix_covers("src/zephyr", "src/zephyr/data/x.py")
    assert ll.prefix_covers("src/zephyr", "src/zephyr")
    assert not ll.prefix_covers("src/zephyr", "src/zephyr2/x.py")
    assert not ll.prefix_covers("src/zephyr", "src/zephyralia")
    assert ll.prefixes_overlap("a/b", "a/b/c")
    assert ll.prefixes_overlap("a/b/c", "a/b")
    assert not ll.prefixes_overlap("a/b", "a/bc")
    assert ll.prefix_covers(".\\docs\\_working\\", "docs/_working/camp/x.md")  # 反斜杠+尾斜杠归一


# ---------------------------------------------------------------------------
# TTL / heartbeat / release / status
# ---------------------------------------------------------------------------


def test_expired_lease_lazily_pruned_new_claim_ok(tmp_path):
    p = _registry(tmp_path)
    _forge_lease(tmp_path, "sOld", ["src/zephyr/gov"], ttl_offset_seconds=-1)
    res = ll.op_claim(p, "sNew", ["src/zephyr/gov"], 600)
    assert res["ok"] is True  # 过期租约不构成冲突
    data = json.loads(p.read_text(encoding="utf-8"))
    assert "sOld" not in data["leases"]


def test_status_live_vs_stale(tmp_path):
    p = _registry(tmp_path)
    ll.op_claim(p, "sAlive", ["a/b"], 600)  # 先 claim 再 forge：claim 的懒清除不会误删 sDead
    _forge_lease(tmp_path, "sDead", ["x/y"], ttl_offset_seconds=-10)
    st = ll.op_status(p)
    assert [l["sid"] for l in st["live"]] == ["sAlive"]
    assert [l["sid"] for l in st["stale"]] == ["sDead"]
    assert st["live"][0]["remaining_seconds"] > 0


def test_heartbeat_extends_ttl(tmp_path):
    p = _registry(tmp_path)
    ll.op_claim(p, "sA", ["a/b"], 1)  # 短 TTL 起登
    res = ll.op_heartbeat(p, "sA", 600)  # 心跳按 600s 续——增量远大于时钟抖动，判定确定
    assert res["ok"] is True
    after = json.loads(p.read_text(encoding="utf-8"))["leases"]["sA"]["expires_at"]
    hb = json.loads(p.read_text(encoding="utf-8"))["leases"]["sA"]["heartbeat_at"]
    assert ll.datetime_fromisoformat(after) - ll._now() > timedelta(seconds=590)
    assert ll.datetime_fromisoformat(hb) <= ll._now()
    assert ll.op_heartbeat(p, "ghost", 600)["ok"] is False


def test_release(tmp_path):
    p = _registry(tmp_path)
    ll.op_claim(p, "sA", ["a/b"], 600)
    res = ll.op_release(p, "sA")
    assert res["ok"] is True and res["released"] is True
    assert json.loads(p.read_text(encoding="utf-8"))["leases"] == {}
    assert ll.op_release(p, "sA")["released"] is False  # 幂等
    # 释放后他 sid 可抢同前缀
    assert ll.op_claim(p, "sB", ["a/b"], 600)["ok"]


# ---------------------------------------------------------------------------
# suggest 分组
# ---------------------------------------------------------------------------


def test_suggest_groups_by_domain_family():
    files = [
        "src/zephyr/governance/capability_lookup.py",
        "src/zephyr/gov_enforcement/gate.py",
        "tests/governance/test_x.py",
        "docs/_working/camp1/a.md",
        "scripts/governance/tool.py",
        "docs/01_policies_and_standards/_registry/catalogs/roor.yaml",
    ]
    res = ll.suggest_leases(files, 2)
    assert res["ok"] is True
    domains = {d for s in res["suggested"] for d in s["domains"]}
    assert "src/zephyr/governance" in domains
    assert "src/zephyr/gov_enforcement" in domains
    assert "tests/governance" in domains
    assert "docs/_working/camp1" in domains
    assert "scripts/governance" in domains
    assert "hot-register" in domains


def test_suggest_fcfs_disjoint_and_advisory_clean():
    files = [
        "src/zephyr/pkgA/1.py",
        "tests/tA/1.py",
        "src/zephyr/pkgB/2.py",
        "tests/tB/2.py",
    ]
    res = ll.suggest_leases(files, 2)
    t0, t1 = res["suggested"][0]["prefixes"], res["suggested"][1]["prefixes"]
    assert t0 and t1
    for a in t0:
        for b in t1:
            assert not ll.prefixes_overlap(a, b)
    assert res["overlap_advisories"] == []
    # FCFS：首文件域归 t0
    assert "src/zephyr/pkgA" in res["suggested"][0]["domains"]


def test_suggest_hot_register_class_uses_registry_roots():
    files = [
        "docs/01_policies_and_standards/_registry/catalogs/a.yaml",
        "docs/03_modules/_registry/b.yaml",
    ]
    res = ll.suggest_leases(files, 2)
    hot = [s for s in res["suggested"] if "hot-register" in s["domains"]]
    assert len(hot) == 1  # 同类聚一队
    assert "docs/01_policies_and_standards/_registry" in hot[0]["prefixes"]
    assert "docs/03_modules/_registry" in hot[0]["prefixes"]


def test_suggest_overlap_advisory_reported_not_rejected():
    # 根级直文件域（前缀=其父目录）与子目录域可构造相交——影子纪律=advisory 不拒
    files = ["src/zephyr/__init__.py", "src/zephyr/pkgA/x.py"]
    res = ll.suggest_leases(files, 2)
    assert res["rc"] == 0
    if res["overlap_advisories"]:
        assert {"team_a", "team_b", "a", "b"} <= set(res["overlap_advisories"][0])


def test_read_file_list_csv_and_file(tmp_path):
    assert ll.read_file_list("a.py, b.py ,c.py") == ["a.py", "b.py", "c.py"]
    f = tmp_path / "list.txt"
    f.write_text("x.py\ny.py,z.py\n", encoding="utf-8")
    assert ll.read_file_list(str(f)) == ["x.py", "y.py", "z.py"]


# ---------------------------------------------------------------------------
# 影子审计门（WARN-only）
# ---------------------------------------------------------------------------


def test_gate_no_lease_warns_all_files(tmp_path):
    payload = llg.audit_files(_registry(tmp_path), "sX", ["src/zephyr/a.py"])
    assert payload["rc"] == 2 and payload["warn_only"] is True
    assert payload["findings"][0]["type"] == "no-lease"
    assert "永不阻断" in payload["note"]


def test_gate_outside_lease_warns(tmp_path):
    p = _registry(tmp_path)
    ll.op_claim(p, "sA", ["src/zephyr/gov"], 600)
    payload = llg.audit_files(p, "sA", ["src/zephyr/gov/x.py", "tests/y.py"])
    types = [f["type"] for f in payload["findings"]]
    assert "no-lease" not in types
    assert "outside-lease" in types
    outside = [f for f in payload["findings"] if f["type"] == "outside-lease"]
    assert outside[0]["file"] == "tests/y.py"
    assert payload["rc"] == 2


def test_gate_clean_inside_lease_rc0(tmp_path):
    p = _registry(tmp_path)
    ll.op_claim(p, "sA", ["src/zephyr/gov"], 600)
    payload = llg.audit_files(p, "sA", ["src/zephyr/gov/x.py", "src/zephyr/gov/sub/y.py"])
    assert payload["findings"] == [] and payload["rc"] == 0


def test_gate_cross_lease_overlap_warns_both_sids(tmp_path):
    # claim 会拒绝相交登记（正是设计）——影子测试态须直接 forge 两本相交活租约
    _forge_lease(tmp_path, "sA", ["shared/pkg"], 600)
    _forge_lease(tmp_path, "sB", ["shared/pkg/sub"], 600)
    payload = llg.audit_files(_registry(tmp_path), "sA", ["shared/pkg/sub/f.py"])
    cross = [f for f in payload["findings"] if f["type"] == "cross-lease-overlap"]
    assert len(cross) == 1
    assert cross[0]["covering_sids"] == ["sA", "sB"]
    assert payload["rc"] == 2


def test_gate_expired_own_lease_counts_as_no_lease(tmp_path):
    _forge_lease(tmp_path, "sOld", ["a/b"], ttl_offset_seconds=-1)
    payload = llg.audit_files(_registry(tmp_path), "sOld", ["a/b/f.py"])
    assert payload["findings"][0]["type"] == "no-lease"


def test_gate_main_exit_codes_and_json(tmp_path, capsys, monkeypatch):
    # main(argv) 直接驱动：--leases 注入假册（零生产写入）
    monkeypatch.setattr(ll, "REPO_ROOT", tmp_path)  # 防御：即便默认路径被触发也落 tmp
    p = _registry(tmp_path)
    rc = llg.main(["--session", "sA", "--files", "a/b/f.py", "--leases", str(p), "--json"])
    out = json.loads(capsys.readouterr().out)
    assert rc == 2 and out["findings"][0]["type"] == "no-lease"
    ll.op_claim(p, "sA", ["a/b"], 600)
    rc = llg.main(["--session", "sA", "--files", "a/b/f.py", "--leases", str(p)])
    assert rc == 0
    assert "CLEAN" in capsys.readouterr().out


def test_claim_main_positional_form(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(ll, "REPO_ROOT", tmp_path)
    rc = ll.main(["claim", "sA", "src/zephyr/gov", "--leases", str(_registry(tmp_path)), "--json"])
    out = json.loads(capsys.readouterr().out)
    assert rc == 0 and out["ok"] is True


def test_claim_main_conflict_rc1(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(ll, "REPO_ROOT", tmp_path)
    p = _registry(tmp_path)
    ll.op_claim(p, "sA", ["src/zephyr/gov"], 600)
    rc = ll.main(["claim", "sB", "src/zephyr/gov", "--leases", str(p)])
    assert rc == 1
    assert "FAIL" in capsys.readouterr().out
