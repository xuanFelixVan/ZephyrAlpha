# [A_test] module_id: MOD-GOV_registry_projection_generator | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.governance.registry_projection.test_projection_generator
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TTL] task_bound
"""红蓝②：生成器端到端——幂等零写/私改自动纠正+留证/陈旧再生成/降级/gate 执法扩展。"""

from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from zephyr.governance.registry_projection.pg_source import ProjectionUnavailable
from zephyr.governance.registry_projection.projection_generator import run
from zephyr.governance.registry_projection.state import ProjectionState, load_state, save_state

REG_REL = "docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml"

REG_V1 = """schema_version: 1.1.0
title: 测试册
capabilities:
- capability_id: a_cap
  description: 描述甲
creation_tokens:
- file: a.md
  token: tok-a
  created_by: sess-1
di_seam_exemptions: []
"""

REG_V2 = REG_V1.replace("- file: a.md\n  token: tok-a", "- file: a.md\n  token: tok-a\n- file: b.md\n  token: tok-b")


def _snapshot_json(tmp_path, text: str, revision: int) -> str:
    from zephyr.governance.registry_projection.model import snapshot_from_yaml

    snap = snapshot_from_yaml(text, registry_id="REG-CAPCAN-001", physical_path=REG_REL)
    snap.ledger_revision = revision
    bundle = {
        "registry_id": snap.registry_id,
        "snapshot_version": revision,
        "ledger_revision": revision,
        "content_sha256": "",
        "header_lines": snap.header_lines,
        "sections": [
            {"root_key": s.root_key, "entries": [[list(p) for p in e] for e in s.entries]} for s in snap.sections
        ],
        "trailing_scalars": [list(t) for t in snap.trailing_scalars],
    }
    path = tmp_path / f"snap_{revision}.json"
    path.write_text(json.dumps({"physical_path": REG_REL, "bundle": bundle}, ensure_ascii=False), encoding="utf-8")
    return str(path)


def _setup(tmp_path, text: str = REG_V1):
    (tmp_path / REG_REL).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / REG_REL).write_text(text, encoding="utf-8", newline="\n")
    return _snapshot_json(tmp_path, text, 1)


def test_unmanaged_is_zero_behavior(tmp_path):
    snap_file = _setup(tmp_path)
    report = run(tmp_path, mode="check", source=snap_file)
    assert report.ok and report.quadrant == "unmanaged" and not report.wrote


def test_render_then_idempotent_zero_write(tmp_path):
    snap_file = _setup(tmp_path)
    r1 = run(tmp_path, mode="render", source=snap_file)
    assert r1.ok and r1.wrote
    assert load_state(tmp_path).content_sha256
    r2 = run(tmp_path, mode="render", source=snap_file)
    assert r2.ok and r2.quadrant == "clean" and not r2.wrote  # 幂等判据：第二次零写盘


def test_private_edit_auto_healed_with_evidence(tmp_path):
    snap_file = _setup(tmp_path)
    run(tmp_path, mode="render", source=snap_file)
    reg = tmp_path / REG_REL
    reg.write_text(reg.read_text(encoding="utf-8").replace("描述甲", "私改内容"), encoding="utf-8", newline="\n")
    report = run(tmp_path, mode="render", source=snap_file)
    assert report.ok and report.quadrant == "private_edit" and report.wrote
    assert report.evidence_path and "registry_drift_" in report.evidence_path  # 证据留档
    assert "私改内容" not in reg.read_text(encoding="utf-8")  # PG wins 自动纠正
    assert run(tmp_path, mode="render", source=snap_file).quadrant == "clean"  # 复检干净


def test_check_mode_reports_drift_without_write(tmp_path):
    snap_file = _setup(tmp_path)
    run(tmp_path, mode="render", source=snap_file)
    reg = tmp_path / REG_REL
    reg.write_text(reg.read_text(encoding="utf-8").replace("描述甲", "私改内容"), encoding="utf-8", newline="\n")
    report = run(tmp_path, mode="check", source=snap_file)
    assert not report.ok and report.quadrant == "private_edit" and not report.wrote


def test_stale_regenerated_silently(tmp_path):
    snap_file_v1 = _setup(tmp_path)
    run(tmp_path, mode="render", source=snap_file_v1)
    snap_file_v2 = _snapshot_json(tmp_path, REG_V2, 2)  # 账本前进 +1 token
    report = run(tmp_path, mode="render", source=snap_file_v2)
    assert report.ok and report.quadrant == "stale" and report.wrote
    assert report.detail["added"] == 1 and report.detail["removed"] == 0  # 身份增减量喂 registry_drift kind
    assert "tok-b" in (tmp_path / REG_REL).read_text(encoding="utf-8")


def test_pg_unreachable_degraded_never_blocks(tmp_path):
    snap_file = _setup(tmp_path)
    run(tmp_path, mode="render", source=snap_file)

    def dead_source(*_a, **_k):
        raise ProjectionUnavailable("PG 宕机")

    report = run(tmp_path, mode="check", source=dead_source)
    assert report.quadrant == "pg_unreachable" and not report.wrote  # 降级观察，零阻塞


def test_gate_blocks_tampered_projection_when_armed(tmp_path):
    from zephyr.gov_enforcement.commit_gates.registry_yaml_parse_gate import make_registry_yaml_parse_gate

    snap_file = _setup(tmp_path)
    run(tmp_path, mode="render", source=snap_file)  # 武装：状态文件落地
    reg = tmp_path / REG_REL
    tampered = reg.read_text(encoding="utf-8").replace("描述甲", "私改内容")
    reg.write_text(tampered, encoding="utf-8", newline="\n")
    gate = make_registry_yaml_parse_gate()
    gw = SimpleNamespace(project_root=str(tmp_path), _content=tampered)
    gw.run_git = lambda cmd: (
        SimpleNamespace(returncode=0, stdout=REG_REL)
        if cmd[:3] == ["git", "diff", "--cached"]
        else SimpleNamespace(returncode=0, stdout=tampered)
    )
    passed, msg = gate.check(gw, [], session_id="attacker")
    assert not passed and "投影" in msg


def test_gate_unarmed_passes(tmp_path):
    from zephyr.gov_enforcement.commit_gates.registry_yaml_parse_gate import make_registry_yaml_parse_gate

    _setup(tmp_path)  # 未武装：无状态文件
    gate = make_registry_yaml_parse_gate()
    gw = SimpleNamespace(project_root=str(tmp_path), _content=REG_V1)
    gw.run_git = lambda cmd: (
        SimpleNamespace(returncode=0, stdout=REG_REL)
        if cmd[:3] == ["git", "diff", "--cached"]
        else SimpleNamespace(returncode=0, stdout=REG_V1)
    )
    passed, msg = gate.check(gw, [], session_id="normal")
    assert passed
