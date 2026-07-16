# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/checkers/check_blueprint_template_compliance.py | §
# [MODULE] scripts.governance.d5_architecture.checkers.check_blueprint_template_compliance
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.checkers.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""
[BLUEPRINT] GOV-DOC-011 | d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml
[MODULE] scripts.governance.d5_architecture.checkers.check_blueprint_template_compliance
[INVARIANTS] 蓝图模板合规检查不可绕过;52项检查全覆盖
[MODIFY-GUARD] blueprint-construction-template.md REQUIRED_SECTIONS;check_blueprint_compliance.py
[CONSUMERS] pre_write_gate.py;g6-blueprint-compliance.yaml;AI施工者
[STABILITY] stable
[SAFETY] M
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] ComplianceError;BlueprintFormatError
[TESTS] tests/governance/test_blueprint_compliance.py
"""

from __future__ import annotations

__manifest__ = """
args: []
description: '[BLUEPRINT] GOV-DOC-011 | d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml'
dimensions:
- D5
priority: P2
timeout_seconds: 60
warn_only: false
"""


import logging
import subprocess
import sys
from pathlib import Path
from _shared.constants import REPO_ROOT

_PROJECT_ROOT = REPO_ROOT
_COMPLIANCE_SCRIPT = _PROJECT_ROOT / "scripts" / "governance" / "check_blueprint_compliance.py"

logger = logging.getLogger(__name__)


def check_blueprint(blueprint_path: str, warn_only: bool = False) -> int:
    if not _COMPLIANCE_SCRIPT.exists():
        logger.error("合规脚本不存在: %s", _COMPLIANCE_SCRIPT)
        return 2
    cmd = [sys.executable, str(_COMPLIANCE_SCRIPT), blueprint_path]
    if warn_only:
        cmd.append("--warn-only")
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
        cwd=str(_PROJECT_ROOT),
    )
    if result.stdout:
        print(result.stdout)
    return result.returncode


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="蓝图模板合规检查（委托到 check_blueprint_compliance.py）")
    parser.add_argument("blueprint", nargs="+", help="蓝图文件路径")
    parser.add_argument("--warn-only", action="store_true", help="仅警告，不阻断")
    args = parser.parse_args()

    total_exit = 0
    for bp in args.blueprint:
        exit_code = check_blueprint(bp, args.warn_only)
        if exit_code != 0:
            total_exit = 1

    return total_exit


if __name__ == "__main__":
    sys.exit(main())
