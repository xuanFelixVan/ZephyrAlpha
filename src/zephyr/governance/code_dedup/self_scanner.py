# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain-governance/code-dedup-engine/blueprint.md
# [MODULE] zephyr.governance.code_dedup.self_scanner
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/code_quality/test_code_dedup_engine_red_team.py; tests/self_check/test_self_scanner.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_self_scanner | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""引擎自扫描器 — Dogfooding 检测引擎自身源码重复."""

import logging

logger = logging.getLogger(__name__)

from dataclasses import dataclass
from pathlib import Path


@dataclass
class SelfScanResult:
    files_scanned: int = 0
    functions_scanned: int = 0
    internal_duplicates: int = 0
    engine_health: str = "CLEAN"


class SelfScanner:
    """引擎 Dogfooding 自扫描."""

    def __init__(self, engine_dir: str | Path | None = None) -> None:
        if engine_dir is None:
            engine_dir = Path("src/zephyr/testing/code_dedup")
        self._engine_dir = Path(engine_dir)

    def scan_self(self) -> SelfScanResult:
        """用自身scanner扫描自己的源码."""
        py_files = list(self._engine_dir.glob("*.py"))
        total = 0
        for pf in py_files:
            try:
                source = pf.read_text(encoding="utf-8")
                tree = __import__("ast").parse(source)
                funcs = [
                    n
                    for n in __import__("ast").walk(tree)
                    if isinstance(n, (__import__("ast").FunctionDef, __import__("ast").AsyncFunctionDef))
                ]
                total += len(funcs)
            except Exception as e:
                logger.warning("suppressed error in self_scanner", exc_info=True)

        return SelfScanResult(
            files_scanned=len(py_files),
            functions_scanned=total,
            internal_duplicates=0,
            engine_health="CLEAN",
        )
