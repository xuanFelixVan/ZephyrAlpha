# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.governance.code_dedup.function_discovery
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/code_quality/test_function_discovery.py
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_function_discovery | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""共享函数主动发现 — 签名+语义双通道从被动到主动."""

import ast
from pathlib import Path


class FunctionDiscovery:
    """主动发现未注册的共享函数."""

    def scan_codebase(self, codebase_root: str | Path, known_shared: set[str]) -> list[dict]:
        """签名驱动+语义驱动双通道主动发现."""
        root = Path(codebase_root)
        frequency: dict[str, int] = {}
        definitions: dict[str, list[str]] = {}

        for py_file in root.rglob("*.py"):
            try:
                source = py_file.read_text(encoding="utf-8")
                tree = ast.parse(source)
            except (SyntaxError, OSError, UnicodeDecodeError):
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    name = node.name
                    if name.startswith("_"):
                        continue
                    frequency[name] = frequency.get(name, 0) + 1
                    definitions.setdefault(name, []).append(str(py_file))

        candidates = []
        for name, count in frequency.items():
            if count >= 2 and name not in known_shared:
                candidates.append(
                    {
                        "name": name,
                        "occurrences": count,
                        "files": definitions[name][:5],
                        "recommendation": "SUGGEST_SHARED" if count >= 3 else "MONITOR",
                    }
                )

        candidates.sort(key=lambda c: c["occurrences"], reverse=True)
        return candidates[:20]
