# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain-governance/code-dedup-engine/blueprint.md
# [MODULE] zephyr.governance.code_dedup.path_index_validator
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/path/test_path_index_validator.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_path_index_validator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""路径索引验证——验证 config 数据集相对路径表与实际文件系统同步."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class PathMismatch:
    indexed_path: str
    actual_status: str
    expected_exists: bool
    actual_exists: bool


@dataclass
class PathIndexValidator:
    root: Path = field(default_factory=lambda: Path.cwd())
    mismatches: list[PathMismatch] = field(default_factory=list)

    def validate(self, indexed_paths: list[str]) -> dict[str, Any]:
        self.mismatches.clear()
        for ip in indexed_paths:
            fp = self.root / ip
            exists = fp.exists()
            if not exists:
                self.mismatches.append(
                    PathMismatch(
                        indexed_path=ip,
                        actual_status="MISSING",
                        expected_exists=True,
                        actual_exists=False,
                    )
                )

        return {
            "total_checked": len(indexed_paths),
            "mismatches": len(self.mismatches),
            "clean": len(self.mismatches) == 0,
            "details": [{"path": m.indexed_path, "status": m.actual_status} for m in self.mismatches],
        }
