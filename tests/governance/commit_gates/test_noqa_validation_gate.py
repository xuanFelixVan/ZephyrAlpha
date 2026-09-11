# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_noqa_validation_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [INVARIANTS] NOQA-VALIDATION gate 回归+own-scope 语义测试（#ARCH-GATE-OWN-SCOPE-001 第四批，#ARCH-310）
# [TTL] permanent
"""NOQA-VALIDATION gate 测试：未登记/无理由 noqa 阻断 + own-scope（只查自己）语义。"""

from __future__ import annotations

import os
import sys
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../src"))

from zephyr.gov_enforcement.commit_gates.noqa_validation_gate import (  # noqa: E402
    make_noqa_validation_gate,
)

_UNREGISTERED = "totally-fake-marker-xyz"


def _make_mock_gateway(staged_py: list[str], project_root: str) -> MagicMock:
    gw = MagicMock()
    gw.project_root = project_root

    def _run_git(cmd):
        result = MagicMock()
        if "--name-only" in cmd:
            result.returncode = 0
            result.stdout = "\n".join(staged_py)
            return result
        if "rev-parse" in cmd:
            result.returncode = 0
            result.stdout = project_root
            return result
        result.returncode = 0
        result.stdout = ""
        return result

    gw.run_git.side_effect = _run_git
    return gw


def _make_session_gateway(tmp_path, staged_py):
    for name, content in staged_py.items():
        (tmp_path / name).write_text(content, encoding="utf-8")
    gw = _make_mock_gateway(list(staged_py.keys()), str(tmp_path))
    from zephyr.security.access_control.session_concurrency import SessionRegistry

    gw._registry = SessionRegistry(project_root=tmp_path)
    return gw


class TestNoqaSemantics:
    def test_unregistered_marker_blocks(self, tmp_path):
        (tmp_path / "a.py").write_text(
            f"x = 1  # noqa: {_UNREGISTERED} 需要理由文本\n",
            encoding="utf-8",
        )
        gw = _make_session_gateway(tmp_path, {})
        # 直接构造 staged 清单（文件已写盘）
        gw2 = _make_mock_gateway(["a.py"], str(tmp_path))
        gw2._registry = gw._registry
        passed, detail = make_noqa_validation_gate().check(gw2, [])
        assert passed is False
        assert _UNREGISTERED in detail

    def test_no_violation_passes(self, tmp_path):
        (tmp_path / "clean.py").write_text("x = 1\n", encoding="utf-8")
        gw = _make_mock_gateway(["clean.py"], str(tmp_path))
        from zephyr.security.access_control.session_concurrency import SessionRegistry

        gw._registry = SessionRegistry(project_root=tmp_path)
        passed, detail = make_noqa_validation_gate().check(gw, [])
        assert passed is True


class TestOnlyOwnSessionScanned:
    """只查自己语义：外来 staged 未登记 noqa 不阻断本 session 提交（warn+审计）。"""

    def test_foreign_violation_does_not_block_own_commit(self, tmp_path):
        import json

        own_clean = "own_clean.py"
        foreign_bad = "foreign_bad.py"
        gw = _make_session_gateway(
            tmp_path,
            {
                own_clean: "x = 1\n",
                foreign_bad: f"y = 2  # noqa: {_UNREGISTERED} 外来会话的裸豁免文本\n",
            },
        )
        passed, detail = make_noqa_validation_gate().check(gw, [own_clean], session_id="sess-A")
        assert passed is True
        assert _UNREGISTERED not in detail
        audit = tmp_path / ".runtime" / "gate_audit" / "noqa_validation_foreign_staged.jsonl"
        assert audit.exists()
        rec = json.loads(audit.read_text(encoding="utf-8").splitlines()[-1])
        assert foreign_bad in rec["foreign_files"]

    def test_own_violation_still_blocks(self, tmp_path):
        own_bad = "own_bad.py"
        foreign_clean = "foreign_clean.py"
        gw = _make_session_gateway(
            tmp_path,
            {
                own_bad: f"z = 3  # noqa: {_UNREGISTERED} 本会话违规需阻断文本\n",
                foreign_clean: "w = 4\n",
            },
        )
        passed, detail = make_noqa_validation_gate().check(gw, [own_bad], session_id="sess-A")
        assert passed is False
        assert _UNREGISTERED in detail

    def test_no_session_degrades_to_full_scan(self, tmp_path):
        bad = "bad.py"
        gw = _make_session_gateway(tmp_path, {bad: f"q = 5  # noqa: {_UNREGISTERED} 无归属退化全量文本\n"})
        passed, detail = make_noqa_validation_gate().check(gw, [])
        assert passed is False
        assert _UNREGISTERED in detail
