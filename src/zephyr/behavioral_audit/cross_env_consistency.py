# [A_module] module_id=MOD-SEC_cross_env_consistency | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain-governance/drift-detector/blueprint.md
# [MODULE] zephyr.behavioral_audit.cross_env_consistency
# [INVARIANTS] Git-native漂移检测;自动对账;漂移预算
# [MODIFY-GUARD] docs/03_modules/_domain-governance/drift-detector/blueprint.md;src/zephyr/behavioral-auditor/__init__.py
# [CONSUMERS] MOD-INF-007;MOD-INF-021;MOD-INF-020
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/test_behavioral_auditor/

from __future__ import annotations
from enum import Enum

class ConsistencyDim(str, Enum):
    PYTHON = "Python3.11.9"
    DEPENDENCIES = "freeze.md5 hash"
    DATA_STRUCTURE = "parquet/pickle schema"
    MODEL_OUTPUT = "float ε<1e-9"

PYTHON_VERSION: str = "3.11.9"
MODEL_FLOAT_TOLERANCE: float = 1e-9
WIN_MIN_RAM_GB: int = 16
WIN_MAX_CPU_LOAD: float = 0.75

WIN11_RISKS: dict[str, str] = {
    "permissions": "UAC escalation blocked + firewall auto",
    "paths": "反斜杠→all refs consistent WSL+",
    "crlf": "gitattributes *.bat/proj eol=crlf",
    "memory": "Win ≥16GB load avg<75%",
    "process": "single python system_module=1",
}
