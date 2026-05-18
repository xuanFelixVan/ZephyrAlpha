# [BLUEPRINT] MOD-INF-018 | 03_modules/l01_infrastructure/agent-rbac/blueprint.md | §

# [MODULE] zephyr.agent_rbac.build_sanitizer

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""构建净化器——检出构建脚本中可能注入恶意代码的模式."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class BuildSanitizeResult(BaseModel):
    script_path: str
    safe: bool = True
    risky_patterns: list[str] = []
    recommendation: str = ""


RISKY_BUILD_PATTERNS = [
    "curl ... | bash", "curl ... | sh", "wget ... -O - | sh",
    "pip install --no-deps", "pip install --break-system-packages",
    "npm install -g", "sudo npm", "sudo pip",
    "git clone ... && cd ... && make install",
    "chmod 777", "chmod -R 777",
    "rm -rf /", "rm -rf ~", "rm -rf .",
    'eval "$(' , "eval `",
    ".env", "export SECRET=", "export PASSWORD=",
]


class BuildSanitizer:
    def check(self, script_path: str, content: str) -> BuildSanitizeResult:
        risky = [p for p in RISKY_BUILD_PATTERNS if p.lower() in content.lower()]
        safe = len(risky) == 0
        return BuildSanitizeResult(
            script_path=script_path,
            safe=safe,
            risky_patterns=risky,
            recommendation="ok" if safe else f"review {len(risky)} risky patterns",
        )
