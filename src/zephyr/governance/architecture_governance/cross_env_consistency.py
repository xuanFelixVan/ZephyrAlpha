# [BLUEPRINT] SRC-013 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.architecture_governance.cross_env_consistency
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.architecture_governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_cross_env_consistency | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from typing import Final
from enum import Enum


class ConsistencyDim(str, Enum):
    PYTHON = "Python3.11.9"
    DEPENDENCIES = "freeze.md5 hash"
    DATA_STRUCTURE = "parquet/pickle schema"
    MODEL_OUTPUT = "float ε<1e-9"


PYTHON_VERSION: Final[str] = "3.11.9"
MODEL_FLOAT_TOLERANCE: Final[float] = 1e-9
WIN_MIN_RAM_GB: Final[int] = 16
WIN_MAX_CPU_LOAD: Final[float] = 0.75

WIN11_RISKS: Final[dict[str, str]] = {
    "permissions": "UAC escalation blocked + firewall auto",
    "paths": "反斜杠→all refs consistent WSL+",
    "crlf": "gitattributes *.bat/proj eol=crlf",
    "memory": "Win ≥16GB load avg<75%",
    "process": "single python system_module=1",
}
