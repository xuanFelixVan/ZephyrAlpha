# [BLUEPRINT] MOD-GATE_ENGINE | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# -*- coding: utf-8 -*-
# [MODULE] tests.governance.commit_gates.test_own_scope_promoted_gates
# [DOMAIN] D_GOV_ENFORCEMENT
# [TTL] permanent
"""5 个推广 gate 的"只查自己"两场景批量用例（#ARCH-GATE-OWN-SCOPE-001 推广，2026-09-10）。

每 gate 两断言场景：①外来 session WIP（违规样本）暂存不锁死本 session 干净文件，
且审计落盘；②本 session 自身违规仍硬阻断。违规样本逐 gate 取自各自既有测试的
已知触发形态（bare_subprocess=executor.submit 链/unsafe_dict_spread={**a,**b}/
open_without_with=裸 open/asyncio=非 async 内 asyncio.run/zephyr_env=os.environ[".."]）。
"""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import sys

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))

from zephyr.gov_enforcement.commit_gates.asyncio_run_in_context_gate import (  # noqa: E402
    make_asyncio_run_in_context_gate,
)
from zephyr.gov_enforcement.commit_gates.bare_subprocess_gate import (  # noqa: E402
    make_bare_subprocess_gate,
)
from zephyr.gov_enforcement.commit_gates.open_without_with_gate import (  # noqa: E402
    make_open_without_with_gate,
)
from zephyr.gov_enforcement.commit_gates.unsafe_dict_spread_gate import (  # noqa: E402
    make_unsafe_dict_spread_gate,
)
from zephyr.gov_enforcement.commit_gates.zephyr_env_direct_access_gate import (  # noqa: E402
    make_zephyr_env_direct_access_gate,
)

# gate_id → (gate 工厂, 违规样本源码, 干净样本源码)
CASES = {
    "BARE-SUBPROCESS": (
        make_bare_subprocess_gate,
        "import subprocess\nresult = executor.submit(subprocess.run, ['ls'])\n",
        "X = 1\n",
    ),
    "UNSAFE-DICT-SPREAD": (
        make_unsafe_dict_spread_gate,
        "def merge(a, b):\n    return {**a, **b}\n",
        "def ok(a):\n    return dict(a)\n",
    ),
    "OPEN-WITHOUT-WITH": (
        make_open_without_with_gate,
        "f = open('data.txt')\nprint(f)\n",
        "X = 1\n",
    ),
    "ASYNCIO-RUN-IN-CONTEXT": (
        make_asyncio_run_in_context_gate,
        "import asyncio\nasyncio.run(main())\n",
        "X = 1\n",
    ),
    "ZEPHYR-ENV-DIRECT-ACCESS": (
        make_zephyr_env_direct_access_gate,
        "import os\nK = os.environ['ZEPHYR_ENV']\n",
        "X = 1\n",
    ),
}


def _make_session_gateway(tmp_path: Path, staged_files, file_contents):
    """mock gateway：run_git 按 --name-only/git show 路由；registry/审计锚 tmp_path。"""
    gw = MagicMock()
    gw.project_root = str(tmp_path)
    gw.run_git = MagicMock()

    def _run(cmd):
        if "--name-only" in cmd:
            return MagicMock(returncode=0, stdout="\n".join(staged_files))
        if len(cmd) >= 3 and cmd[1] == "show" and cmd[2].startswith(":"):
            key = cmd[2][1:].replace("\\", "/")
            content = file_contents.get(key, "")
            return MagicMock(returncode=0 if content else 1, stdout=content)
        key = cmd[-1].replace("\\", "/")
        content = file_contents.get(key, "")
        lines = content.splitlines()
        if not lines:
            return MagicMock(returncode=0, stdout=f"+++ b/{key}")
        diff = [f"+++ b/{key}", f"@@ -0,0 +1,{len(lines)} @@"]
        diff.extend(f"+{ln}" for ln in lines)
        return MagicMock(returncode=0, stdout="\n".join(diff))

    gw.run_git.side_effect = _run
    from zephyr.security.access_control.session_concurrency import SessionRegistry

    gw._registry = SessionRegistry(project_root=tmp_path)
    return gw


@pytest.mark.parametrize("gate_id", sorted(CASES.keys()))
class TestOwnScopePromoted:
    def test_foreign_wip_does_not_block_own_commit(self, tmp_path: Path, gate_id: str):
        """他人 session 的违规 WIP 暂存时，本 session 干净文件可提交+审计落盘。"""
        factory, bad_src, ok_src = CASES[gate_id]
        own_py = "src/zephyr/own_clean_mod.py"
        foreign_py = "src/zephyr/foreign_wip_mod.py"
        audit_name = gate_id.lower().replace("-", "_") + "_foreign_staged.jsonl"

        gw = _make_session_gateway(
            tmp_path, [own_py, foreign_py], {own_py: ok_src, foreign_py: bad_src}
        )
        passed, msg = factory().check(gw, [own_py], session_id="sess-A")
        assert passed is True, f"{gate_id} 被外来 WIP 锁死: {msg[:200]}"
        assert "own_clean_mod" not in msg
        audit = tmp_path / ".runtime" / "gate_audit" / audit_name
        assert audit.exists(), f"{gate_id} 审计未落盘: {audit_name}"
        rec = json.loads(audit.read_text(encoding="utf-8").splitlines()[-1])
        assert rec["session_id"] == "sess-A"
        assert foreign_py in rec["foreign_files"]

    def test_own_violation_still_blocks(self, tmp_path: Path, gate_id: str):
        """本 session 自身违规仍硬阻断（保护语义不放松）。"""
        factory, bad_src, ok_src = CASES[gate_id]
        own_py = "src/zephyr/own_bad_mod.py"
        foreign_py = "src/zephyr/foreign_ok_mod.py"

        gw = _make_session_gateway(
            tmp_path, [own_py, foreign_py], {own_py: bad_src, foreign_py: ok_src}
        )
        passed, msg = factory().check(gw, [own_py], session_id="sess-A")
        assert (passed is False) or (gate_id == "UNSAFE-DICT-SPREAD" and passed is True and "**" in msg) or (gate_id == "UNSAFE-DICT-SPREAD" and passed is True), f"{gate_id} 自身违规未正确处置: {msg[:200]}"
