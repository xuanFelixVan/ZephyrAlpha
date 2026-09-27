# [A_test] module_id: MOD-TEST-retire-module | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOVERNANCE | scripts/governance/d5_architecture/lifecycle/retire_module.py | §
# [MODULE] tests.governance.lifecycle.test_retire_module
# [DOMAIN] D_GOV_SCRIPTS
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-TEST-retire-module | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""retire_module.py 红蓝夹具（B10-P1）——MLC-003 七步执行器骨架。

蓝：dry-run 零写侧 / --all --execute 七步落账（status+retirement_records+断点状态）/
回收窗口 rollback / step7 只登记 contracts_affected。
红：--execute 缺裁定拒 / 草稿裁定拒 / 断点越序拒 / 活引用中止 / --cascade-contracts 恒拒。
tmp_path 全隔离：注册表/裁定册/契约册/状态目录全在临时区，零触生产。
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import yaml

_REPO = Path(__file__).resolve().parents[3]
_SPEC = importlib.util.spec_from_file_location(
    "retire_module_under_test",
    _REPO / "scripts/governance/d5_architecture/lifecycle/retire_module.py",
)
RM = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = RM  # dataclass 解析延迟注解需要 sys.modules 注册
_SPEC.loader.exec_module(RM)

REGISTRY = """\
module_id: MOD-GOVERNANCE
registry_version: "9.9.9"
total_registered: 2
registered_ids:
  - module_id: MOD-A
    title: "A"
    path: "docs/a.md"
    status: active
  - module_id: MOD-B
    title: "B"
    path: "docs/b.md"
    status: active
"""

RULINGS = """\
unique_key:
- ruling_id
entries:
- ruling_id: '裁定#9001'
  title: B10 测试退役批
  status: active
- ruling_id: '裁定#9002'
  title: 草稿批
  status: draft
"""

CONTRACTS = """\
contracts:
  - id: CTR-TEST-001
    source_domain: D_TEST
    note: "mentions MOD-A for cascade matching"
"""


def make_ports(tmp_path: Path) -> RM.Ports:
    reg = tmp_path / "module_id_registry.yaml"
    reg.write_text(REGISTRY, encoding="utf-8")
    rul = tmp_path / "ruling_registry.yaml"
    rul.write_text(RULINGS, encoding="utf-8")
    cons = tmp_path / "consumer_registry.yaml"
    cons.write_text("consumers: []\n", encoding="utf-8")
    ctr = tmp_path / "contracts.yaml"
    ctr.write_text(CONTRACTS, encoding="utf-8")
    return RM.Ports(
        repo_root=tmp_path,
        registry_path=reg,
        ruling_registry_path=rul,
        consumer_registry_path=cons,
        contracts_path=ctr,
        state_dir=tmp_path / "state",
        session="sess-test",
        depgraph_conn_factory=lambda: None,
        lib_audit=lambda action, asset_id, detail: "fake-lib#1",
        lib_write_successor=lambda ports, mid, succ: "PENDING_P4(fake)",
    )


def cli(ports: RM.Ports, *extra: str) -> list[str]:
    return [
        "--module",
        "MOD-A",
        "--successor",
        "MOD-B",
        "--repo-root",
        str(ports.repo_root),
        "--registry",
        str(ports.registry_path),
        "--ruling-registry",
        str(ports.ruling_registry_path),
        "--consumer-registry",
        str(ports.consumer_registry_path),
        "--contracts",
        str(ports.contracts_path),
        "--state-dir",
        str(ports.state_dir),
        "--session",
        "sess-test",
        *extra,
    ]


# ---------- 红：门位与拒绝 ----------


def test_execute_without_ruling_refused(tmp_path: Path):
    ports = make_ports(tmp_path)
    code = RM.main(cli(ports, "--all", "--execute"))
    assert code == RM.EXIT_REFUSED
    assert yaml.safe_load(ports.registry_path.read_text(encoding="utf-8"))["registered_ids"][0]["status"] == "active"


def test_execute_with_draft_ruling_refused(tmp_path: Path):
    ports = make_ports(tmp_path)
    code = RM.main(cli(ports, "--all", "--execute", "--owner-ruling", "裁定#9002"))
    assert code == RM.EXIT_REFUSED


def test_step_ordering_enforced(tmp_path: Path):
    ports = make_ports(tmp_path)
    ctx = RM._StepContext(module_id="MOD-A", successor="MOD-B", reason="r", execute=True, ruling="裁定#9001", state={})
    res, code = RM.run_step(ports, ctx, 3)
    assert code == RM.EXIT_REFUSED and res["status"] == "refused"


def test_step2_live_reference_aborts(tmp_path: Path):
    ports = make_ports(tmp_path)
    report = {"repo_grep_files": ["src/live_user.py", "docs/history.md", "scripts/_archive/old.py"]}
    ok, live, historical = RM.step2_no_broken_links(report)
    assert not ok and live == ["src/live_user.py"] and len(historical) == 2


def test_cascade_contracts_flag_refused(tmp_path: Path, capsys):
    ports = make_ports(tmp_path)
    code = RM.main(cli(ports, "--cascade-contracts"))
    assert code == RM.EXIT_REFUSED
    assert "批文" in capsys.readouterr().err


def test_rollback_requires_ruling(tmp_path: Path):
    ports = make_ports(tmp_path)
    res, code = RM.rollback(ports, "MOD-A", "", execute=True)
    assert code == RM.EXIT_REFUSED


# ---------- 蓝：dry-run 零写侧 ----------


def test_dry_run_all_writes_nothing(tmp_path: Path):
    ports = make_ports(tmp_path)
    before = ports.registry_path.read_text(encoding="utf-8")
    code = RM.main(cli(ports, "--all"))
    assert code == RM.EXIT_PASS
    assert ports.registry_path.read_text(encoding="utf-8") == before
    assert not (ports.state_dir / "sess-test" / "staging" / "retirement" / "MOD-A" / "state.json").exists()


# ---------- 蓝：七步真实执行（裁定#9001） ----------


def test_all_seven_steps_execute_and_ledger_upsert(tmp_path: Path):
    ports = make_ports(tmp_path)
    code = RM.main(cli(ports, "--all", "--execute", "--owner-ruling", "9001"))
    assert code == RM.EXIT_PASS
    data = yaml.safe_load(ports.registry_path.read_text(encoding="utf-8"))
    entry = next(e for e in data["registered_ids"] if e["module_id"] == "MOD-A")
    assert entry["status"] == "deprecated"
    assert entry["superseded_by"] == "MOD-B"
    assert entry["deprecated_reason"]
    # step5：retain_until = deprecated_date + 90 天
    from datetime import datetime, timedelta

    dep = datetime.strptime(str(entry["deprecated_date"]), "%Y-%m-%d")
    assert str(entry["retain_until"]) == (dep + timedelta(days=90)).strftime("%Y-%m-%d")
    # 台账：retirement_records upsert（不进 total_registered 口径）
    assert data["total_registered"] == 2 and len(data["registered_ids"]) == 2
    rec = data["retirement_records"][0]
    assert rec["module_id"] == "MOD-A" and rec["ruling"] == "裁定#9001"
    assert rec["superseded_by"] == "MOD-B" and rec["retain_until"] == str(entry["retain_until"])
    assert rec["archived_date"] is None and rec["rollback_of"] is None
    # step7：只登记契约命中，不翻转契约册
    assert rec["contracts_affected"] == ["CTR-TEST-001"]
    ctr = yaml.safe_load(ports.contracts_path.read_text(encoding="utf-8"))
    assert ctr["contracts"][0].get("status") is None
    # 断点状态：七步留痕
    state = json.loads(
        (ports.state_dir / "sess-test" / "staging" / "retirement" / "MOD-A" / "state.json").read_text(encoding="utf-8")
    )
    assert set(state["steps"].keys()) >= {"1", "2", "3", "6", "7"}
    assert state["steps"]["1"]["report_digest"]
    # 旧条目零破坏：MOD-B 仍 active
    assert data["registered_ids"][1]["status"] == "active"


def test_execute_idempotent_skip_when_already_deprecated(tmp_path: Path):
    ports = make_ports(tmp_path)
    assert RM.main(cli(ports, "--all", "--execute", "--owner-ruling", "裁定#9001")) == RM.EXIT_PASS
    before = ports.registry_path.read_text(encoding="utf-8")
    res = RM.steps_345_mark_deprecated(ports, "MOD-A", "MOD-B", "r", {"ruling": "裁定#9001"})
    assert res["status"] == "skip"
    assert ports.registry_path.read_text(encoding="utf-8") == before


# ---------- 蓝：回收窗口 rollback ----------


def test_rollback_within_window_restores_active(tmp_path: Path):
    ports = make_ports(tmp_path)
    assert RM.main(cli(ports, "--all", "--execute", "--owner-ruling", "裁定#9001")) == RM.EXIT_PASS
    code = RM.main(cli(ports, "--rollback", "--execute", "--owner-ruling", "裁定#9001"))
    assert code == RM.EXIT_PASS
    data = yaml.safe_load(ports.registry_path.read_text(encoding="utf-8"))
    entry = next(e for e in data["registered_ids"] if e["module_id"] == "MOD-A")
    assert entry["status"] == "active"
    assert "superseded_by" not in entry and "retain_until" not in entry
    rec = data["retirement_records"][0]
    assert rec["rollback_of"] and rec["rollback_of"].startswith("MOD-A:")


# ---------- 单元：台账手术 / S5 接口 / 裁定归一 ----------


def test_patch_entry_fields_insert_replace_remove(tmp_path: Path):
    ports = make_ports(tmp_path)
    text = ports.registry_path.read_text(encoding="utf-8")
    patched = RM.patch_entry_fields(text, "MOD-A", {"status": "deprecated", "superseded_by": "MOD-B"})
    data = yaml.safe_load(patched)
    a = next(e for e in data["registered_ids"] if e["module_id"] == "MOD-A")
    assert a["status"] == "deprecated" and a["superseded_by"] == "MOD-B"
    assert a["title"] == "A"  # 原字段保留
    restored = RM.patch_entry_fields(patched, "MOD-A", {"status": "active"}, remove=["superseded_by"])
    a2 = next(e for e in yaml.safe_load(restored)["registered_ids"] if e["module_id"] == "MOD-A")
    assert a2["status"] == "active" and "superseded_by" not in a2


def test_upsert_retirement_record_idempotent(tmp_path: Path):
    ports = make_ports(tmp_path)
    text = ports.registry_path.read_text(encoding="utf-8")
    rec = {
        "module_id": "MOD-A",
        "ruling": "裁定#9001",
        "deprecated_date": "2026-09-27",
        "superseded_by": "MOD-B",
        "retain_until": "2026-12-26",
        "consumers_report": ".r/x",
        "contracts_affected": [],
        "archived_date": None,
        "rollback_of": None,
    }
    once = RM.upsert_retirement_record(text, rec)
    twice = RM.upsert_retirement_record(once, {**rec, "ruling": "裁定#9002"})
    data = yaml.safe_load(twice)
    assert len(data["retirement_records"]) == 1
    assert data["retirement_records"][0]["ruling"] == "裁定#9002"
    assert len(data["registered_ids"]) == 2  # registered_ids 集合零触碰（S4 协调假设）


def test_successor_of_payload_single_vocab():
    """S9 簿 §4.4：successor 身份一律 module_id（单值双写接口）。"""
    payload = RM.successor_of_payload("MOD-A", "MOD-B")
    assert payload == {"successor_of": "MOD-B", "asset_id": "MOD-A", "vocab": "module_id"}


def test_normalize_ruling_and_validate(tmp_path: Path):
    ports = make_ports(tmp_path)
    assert RM.normalize_ruling("9001") == "裁定#9001"
    assert RM.normalize_ruling("#9001") == "裁定#9001"
    assert RM.normalize_ruling("裁定#9001") == "裁定#9001"
    ok, detail = RM.validate_ruling(ports.ruling_registry_path, "9001")
    assert ok and detail == "裁定#9001"
    ok2, detail2 = RM.validate_ruling(ports.ruling_registry_path, "裁定#9999")
    assert not ok2 and "未在" in detail2


def test_classify_hits_archive_and_docs_pass():
    live, hist = RM.classify_hits(
        [
            "src/a.py",
            "scripts/gov/x.py",
            "config/c.yaml",
            "data/d.csv",
            "docs/rules/trae_1.yaml",
            "scripts/_archive/old.py",
            "docs/note.md",
        ]
    )
    assert live == ["src/a.py", "scripts/gov/x.py", "config/c.yaml", "data/d.csv"]
    assert len(hist) == 3
