# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.governance.commit_gates.id_uniqueness_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec); scripts.governance.d5_architecture.checkers.check_precommit_id_uniqueness (subprocess 调用，检测真源)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] fail-closed on exit 1 (violations); fail-open on exit 2 (script error)
# [MODIFY-GUARD] gate_id="ID-UNIQUENESS"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]；_CONFIG_REL/_CHECK_SCRIPT 路径
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] (True, msg)=通过；False=阻断（exit 1 violations）；exit 2 script error->(True, warn) fail-open
# [TESTS] tests/governance/commit_gates/test_id_uniqueness_gate.py
# [A_module] module_id=MOD-GOV-id_uniqueness_gate | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""id_uniqueness_gate.py — pre-commit hook ID 唯一性门禁（Phase 3 reconciler->gate 收敛）

从 make_precommit_id_uniqueness_reconciler（post-commit warn）升级为 pre-commit 阻断 gate。
--no-verify 绕不过 in-process gate，same-repo 重复 hook id 在 commit 前即被阻断。

治本动机：原 reconciler 是 post-commit 非阻断兜底（--no-verify 绕过 pre-commit hook），
违规已入 git 历史仅告警。本 gate 在 commit() 内嵌等效校验，阻断新引入的重复 id。

fail-open/fail-closed 约定：
- exit 0 = clean -> pass
- exit 1 = violations -> block (fail-closed)
- exit 2 = script error -> pass with warning (fail-open)
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__ = ["make_id_uniqueness_gate"]

_CONFIG_REL = ".pre-commit-config.yaml"
_CHECK_SCRIPT = "scripts/governance/d5_architecture/checkers/check_precommit_id_uniqueness.py"


def make_id_uniqueness_gate() -> GateSpec:
    """构造 pre-commit hook ID 唯一性门禁 GateSpec（fail-closed 阻断型）。

    Returns:
        GateSpec(gate_id="ID-UNIQUENESS", priority=86)。
        priority=86——在 FILE-COPY(85) 之后（文件级检查优先于配置检查）。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        project_root = gateway.project_root

        triggered = any(
            os.path.relpath(f, str(project_root)).replace("\\", "/") == _CONFIG_REL
            for f in files
            if os.path.isfile(f)
        )
        if not triggered:
            return True, "no .pre-commit-config.yaml in commit"

        result = subprocess.run(
            [sys.executable, _CHECK_SCRIPT, "--ci"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )

        if result.returncode == 0:
            return True, "pre-commit id uniqueness check passed"
        if result.returncode == 2:
            logger.warning(
                "id_uniqueness_gate: script error (exit=2): %s",
                result.stderr[-300:], exc_info=True,
            )
            return True, "id_uniqueness check script error (exit=2), fail-open"

        return False, (
            f"ID-UNIQUENESS: same-repo duplicate pre-commit hook IDs detected\n"
            f"{result.stdout[-500:]}"
        )

    return GateSpec(gate_id="ID-UNIQUENESS", check=_check, priority=86)
