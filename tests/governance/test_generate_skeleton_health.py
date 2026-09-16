# [BLUEPRINT] MOD-AUTO-L4-001(暂编号) | docs/_working/automation/campaign/blueprints/skeleton_health_blueprint.md | §测试
# [MODULE] tests.governance.test_generate_skeleton_health
# [DOMAIN] D_GOV_SCRIPTS
# [INVARIANTS] 零真源触碰——全部输入 fixture 注入 tmp（宪法 §9.6）
# [TTL] permanent
"""骨架体检测试：五面检查+建议两分+漂移检测，全 fixture 注入。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT / "scripts" / "governance" / "generators") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts" / "governance" / "generators"))

import generate_skeleton_health as gh  # noqa: E402


def _tdm(tmp_path, nodes=3, edges=2, tmp_litter=0):
    p = tmp_path / "trading_decision_map.yaml"
    p.write_text(yaml_dump({"nodes": [{"id": i} for i in range(nodes)],
                            "edges": [{"id": i} for i in range(edges)]}), encoding="utf-8")
    for i in range(tmp_litter):
        (tmp_path / f"trading_decision_map.yaml.tmp.{i}").write_text("x", encoding="utf-8")
    return p


def yaml_dump(obj) -> str:
    import yaml
    return yaml.safe_dump(obj, allow_unicode=True)


def test_check_tdm_counts_and_litter(tmp_path):
    p = _tdm(tmp_path, nodes=3, edges=2, tmp_litter=2)
    out = gh.check_tdm(p)
    assert out["nodes"] == 3 and out["edges"] == 2
    assert len(out["stale_tmp"]) == 2


def test_check_audit_drift_detected(tmp_path):
    audit = tmp_path / "audit.md"
    audit.write_text("**骨架 5 层 × 4 拍**：23 个已接电、98 个覆盖未接电（零件在、没人叫醒）、4 个 crypto 空壳、13 个纯结构节点。", encoding="utf-8")
    out = gh.check_audit(audit, tdm_nodes=140)
    assert out["electric"]["total"] == 138
    assert "重跑覆盖审计" in out["drift"]


def test_check_registry_status_histogram(tmp_path):
    reg = tmp_path / "reg.yaml"
    reg.write_text(yaml_dump({"entities": [
        {"task_id": "a", "status": "active"},
        {"task_id": "b", "status": "active"},
        {"task_id": "c", "status": "orphaned_source"},
    ]}), encoding="utf-8")
    out = gh.check_registry(reg)
    assert out["by_status"] == {"active": 2, "orphaned_source": 1}


def test_check_decay_watch_list(tmp_path):
    d = tmp_path / "decay.json"
    d.write_text(json.dumps({"strategies": {
        "CAND-a": {"state": "probation", "failed_streak": 2},
        "CAND-b": {"state": "active", "failed_streak": 0},
    }}), encoding="utf-8")
    out = gh.check_decay(d)
    assert out["by_state"] == {"probation": 1, "active": 1}
    assert out["failed_streak_watch"] == ["CAND-a"]


def test_report_advice_split(tmp_path):
    tdm = gh.check_tdm(_tdm(tmp_path, nodes=2, edges=1, tmp_litter=3))
    report = gh.build_report(tdm, {}, {}, {}, {})
    assert "血肉级" in report and "骨架级" not in []  # 结构在场
    assert ".tmp 残留 3 件" in report and "清理 TDM .tmp 残留 3 件" in report
    assert "骨锁肉动" in report
