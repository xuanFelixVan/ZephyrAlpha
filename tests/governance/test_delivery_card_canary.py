"""红证 canary：VERIFIED 升态校验器必须能拒（也必须有正控能放行）。

喂给校验器的卡经 TaskRepository（官方仓储 API，临时库 tmp_path，pid 隔离）真实建出，
artifact_paths 指向不存在路径 → 必须 REJECT；指向 HEAD 实存件 → ELIGIBLE。
本测试不触碰生产 governance.db，不对任何既有卡做 transition。
"""

from __future__ import annotations

import importlib.util
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import pytest

_LANE = Path(__file__).resolve().parents[2]
_MAIN_REPO = Path("D:/ZephyrAlpha")


def _load_checker():
    spec = importlib.util.spec_from_file_location(
        "verified_promotion_check", _LANE / "scripts/governance/wave1a/verified_promotion_check.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _make_task(tmp_path: Path, artifacts: list[str], rb: bool):
    from zephyr.governance.persistence.task_repo import TaskRepository
    from zephyr.shared.schema.task_types import Task, TaskNamespace, TaskStatus

    seq = 9260999 if not rb else 9260998
    tid = f"OPS-{seq}"
    now = datetime.now(UTC)
    db = tmp_path / f"canary_{Path(__file__).stem}_{seq}.db"
    repo = TaskRepository(db_path=str(db), enable_gate=True)
    t = Task(
        task_id=tid,
        namespace=TaskNamespace.OPS,
        seq=seq,
        title="canary：artifact 指向不存在路径的卡（判据必须拒升 VERIFIED）",
        description="根因：无 HEAD 证据锚的自称完成不可信。治根：升 VERIFIED 前置三判据。"
        "施工步骤：本卡仅用于红证，不再施工。验收标准：校验器对缺锚卡必 REJECT、"
        "对有锚无 rb 卡 ELIGIBLE。",
        status=TaskStatus.COMPLETED,
        priority="P2",
        phase=1,
        execution_model="glm",
        files_in_scope=[str(tmp_path / "canary_note.md")],
        deliverables=[str(tmp_path / "canary_out.md")],
        acceptance=["校验器对缺锚卡必 REJECT"],
        source_blueprint="TEST",
        source_section="test_delivery_card_canary",
        safety_level="L",
        directive="CANARY-TEST",
        classification="internal",
        ai_autonomy_level="supervised",
        applicable_rules=[{"module_id": "GOV-TASK-001", "section": "v3.2.0", "reason": "建卡校验"}],
        allowed_touch=[str(tmp_path / "**")],
        artifact_paths=artifacts,
        session_id="canary-st-final-build",
        idempotent=True,
        requires_rb_check=rb,
        approval_required=False,
        tags=(["rb-required:canary"] if rb else []),
        rollback_instructions="本卡仅存活于 tmp_path 临时库文件中，不涉任何生产路径，测试结束随临时目录销毁，无需回滚。",
        created_at=now,
        updated_at=now,
    )
    repo.create(t, allow_direct_create=True, batch_id="wave1a-canary")
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    row = dict(
        con.execute(
            "SELECT task_id,status,artifact_paths,requires_rb_check,tags FROM tasks WHERE task_id=?", (tid,)
        ).fetchone()
    )
    con.close()
    return row


def test_reject_missing_artifact(tmp_path):
    chk = _load_checker()
    row = _make_task(tmp_path, [str(_MAIN_REPO / "definitely_not_exists_wave1a_canary.py")], rb=False)
    res = chk.check_card(row, _MAIN_REPO)
    assert res["verdict"] == "REJECT"
    assert any("判据②" in r for r in res["reasons"])


def test_reject_empty_artifact(tmp_path):
    chk = _load_checker()
    row = _make_task(tmp_path, [], rb=False)
    res = chk.check_card(row, _MAIN_REPO)
    assert res["verdict"] == "REJECT"
    assert any("判据①" in r for r in res["reasons"])


@pytest.mark.skipif(not (_MAIN_REPO / "pyproject.toml").exists(), reason="主仓不在场")
def test_positive_control_eligible(tmp_path):
    chk = _load_checker()
    row = _make_task(tmp_path, [str(_MAIN_REPO / "pyproject.toml")], rb=False)
    res = chk.check_card(row, _MAIN_REPO)
    assert res["verdict"] == "ELIGIBLE", res


@pytest.mark.skipif(not (_MAIN_REPO / "pyproject.toml").exists(), reason="主仓不在场")
def test_rb_anchor_required_when_flag_set(tmp_path):
    chk = _load_checker()
    row = _make_task(tmp_path, [str(_MAIN_REPO / "pyproject.toml")], rb=True)
    res = chk.check_card(row, _MAIN_REPO)
    assert res["verdict"] == "REJECT"
    assert any("判据③" in r for r in res["reasons"])
