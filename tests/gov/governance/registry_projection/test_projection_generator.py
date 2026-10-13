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
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from zephyr.governance.registry_projection.pg_source import ProjectionUnavailable
from zephyr.governance.registry_projection.projection_generator import run
from zephyr.governance.registry_projection.state import ProjectionState, load_state, save_state
from zephyr.shared.io.paths import REPO_ROOT

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


# ===========================================================================
# P0-2② 扩面：creation_tokens 双向一致性对账（st-maint7-20261014，统筹增补第 2 条）
# ===========================================================================
# 甲向复现对照＝PG 有行而盘上无（矿考二班 10-13 夜撞 4 次的滞后面）；
# 乙向复现对照＝盘上有行而 PG 无（死信放量班实证的历史直写遗留面，
#   真实样本 docs/_working/tdm_goal_structure_research_2026_10_13.md 在 PG 是 retired）。


def _snap_from(text: str):
    from zephyr.governance.registry_projection.model import snapshot_from_yaml

    return snapshot_from_yaml(text, registry_id="REG-CAPCAN-001", physical_path=REG_REL)


def test_token_diff_both_directions_empty_when_in_sync():
    """两面全等 ⇒ 零差集（尺在同步面上不误报）。"""
    from zephyr.governance.registry_projection.projection_generator import token_two_way_diff

    d = token_two_way_diff(_snap_from(REG_V1), REG_V1)
    assert d["comparable"] is True
    assert d["pg_only_n"] == 0 and d["disk_only_n"] == 0


def test_token_diff_direction_a_pg_has_row_disk_lacks():
    """甲向（滞后）：PG 快照有 b.md 行、盘上 YAML 只有 a.md ⇒ pg_only=1、disk_only=0。"""
    from zephyr.governance.registry_projection.projection_generator import token_two_way_diff

    s = _snap_from(REG_V2)  # PG 侧两条
    d = token_two_way_diff(s, REG_V1)  # 盘上一条
    assert d["comparable"] is True
    assert d["pg_only_n"] == 1 and d["disk_only_n"] == 0
    assert d["pg_only"] == ["file=b.md|token=tok-b"], d["pg_only"]


def test_token_diff_direction_b_disk_has_row_pg_lacks():
    """乙向（直写遗留）：盘上有 b.md 行而 PG 无 ⇒ disk_only=1，即"诚实 render 会少 1 条"那一面。"""
    from zephyr.governance.registry_projection.projection_generator import token_two_way_diff

    s = _snap_from(REG_V1)  # PG 侧一条
    d = token_two_way_diff(s, REG_V2)  # 盘上两条
    assert d["comparable"] is True
    assert d["disk_only_n"] == 1 and d["pg_only_n"] == 0
    assert d["disk_only"] == ["file=b.md|token=tok-b"], d["disk_only"]


def test_token_diff_never_reports_zero_when_unmeasurable():
    """不可比必须自报 comparable=False＋成因，禁把"量不了"报成"零差异"（在册假绿族）。"""
    from zephyr.governance.registry_projection.projection_generator import token_two_way_diff

    d_empty = token_two_way_diff(_snap_from(REG_V1), "   \n")
    assert d_empty["comparable"] is False and d_empty["reason"]

    d_broken = token_two_way_diff(_snap_from(REG_V1), "creation_tokens:\n  bad: [unclosed\n")
    assert d_broken["comparable"] is False
    assert "不可解析" in d_broken["reason"] or "空册" in d_broken["reason"], d_broken["reason"]

    other = _snap_from("schema_version: 1.1.0\nentries:\n- ruling_id: x\n")
    d_other = token_two_way_diff(other, REG_V1)
    assert d_other["comparable"] is False and "族" in d_other["reason"], d_other["reason"]


def test_render_warns_on_two_way_diff_and_still_writes(tmp_path, caplog):
    """告警是纯观测面：render 前把两向差集说出来，象限与写盘行为零变化。"""
    import logging

    snap_file = _setup(tmp_path, REG_V1)  # 盘上=PG 皆一条，先同步
    # 制造乙向：盘上多一条 PG 没有的直写遗留行
    target = tmp_path / REG_REL
    target.write_text(REG_V2, encoding="utf-8", newline="\n")
    with caplog.at_level(logging.WARNING, logger="zephyr.governance.registry_projection.projection_generator"):
        rep = run(tmp_path, mode="render", source=snap_file, registry_id="REG-CAPCAN-001", physical_path=REG_REL)
    assert rep.ok, rep.detail
    warns = [r.getMessage() for r in caplog.records if "双向一致性告警" in r.getMessage()]
    assert warns, "盘上有行而 PG 无（乙向）必须出声"
    assert "盘上有行而 PG 无/非 active=1 条" in warns[0], warns[0]
    # 写盘行为：诚实 render 按 PG 剔掉遗留行（PG wins 铁律不破）
    assert "b.md" not in target.read_text(encoding="utf-8")


def test_render_silent_when_projection_in_sync(tmp_path, caplog):
    """同步面不出声（防空洞告警刷屏，也证上一条的红不是恒真）。"""
    import logging

    snap_file = _setup(tmp_path, REG_V1)
    with caplog.at_level(logging.WARNING, logger="zephyr.governance.registry_projection.projection_generator"):
        rep = run(tmp_path, mode="render", source=snap_file, registry_id="REG-CAPCAN-001", physical_path=REG_REL)
    assert rep.ok, rep.detail
    assert not [r for r in caplog.records if "双向一致性告警" in r.getMessage()]


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


CLI_SCRIPT = REPO_ROOT / "scripts" / "governance" / "registry_projection" / "registry_projection_generator.py"


def test_cli_smoke_check_and_render_run_standalone(tmp_path):
    """CLI 独立可运行 smoke（2026-10-04 st-tdm-infrafix2）。

    病灶：子进程直跑 CLI 时 sys.path 无仓根，registry_ledger_ddl 裸导的仓根包
    schemas.* 被 site-packages 同名残缺命名空间包抢注 → ModuleNotFoundError。
    断言：--check 与 --render 子进程独立启动均正常退出且无 ModuleNotFoundError。
    """
    snap_file = _setup(tmp_path)
    for mode in ("--check", "--render"):
        proc = subprocess.run(
            [sys.executable, str(CLI_SCRIPT), mode, "--snapshot-file", snap_file, "--project-root", str(tmp_path)],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
        )
        assert "ModuleNotFoundError" not in (proc.stderr or ""), f"{mode} 启动断链: {proc.stderr[-500:]}"
        assert proc.returncode == 0, f"{mode} 退出码 {proc.returncode}: {proc.stdout[-500:]} {proc.stderr[-500:]}"
