# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.gov_drift.naming_magic_checker
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES]
# [CONSUMERS] src/zephyr/governance/behavioral_auditor/__init__.py; src/zephyr/gov_drift/_scanners.py; tests/audit/test_naming_magic_checker.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 命名约定检查不可跳过
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-SEC_naming_magic_checker | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Naming Magic Checker — 命名魔数与隐式约定检测 §6.27。


pattern_a.txt_b_logic: a.txt->b.py->c.yaml, 规定不匹配


lib_version_hardcode: import hashlib==2.0.1


file_pattern_convention: 某功能依赖特定文件命名模式(如*-service.py)


hidden_cycle: 生产代码 imports 测试夹具/配置


manual_inspection: 标注需要人工确认


对标 blueprint.md §6.27。"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path


@dataclass
class NamingMagicAlert:
    alert_id: str

    file_path: str

    line_no: int

    magic_type: str

    current_code: str

    description: str

    severity: str = "MAJOR"

    detected_at: datetime = field(default_factory=lambda: datetime.now(UTC))


_IMPLICIT_FILE_PATTERNS: list[tuple[str, str, str]] = [
    ("import.*models", "model files imported without explicit path", "import_models_convention"),
    ("import.*config", ".yaml config implicit load", "implicit_config_import"),
    ("open\\(.*\\.txt", "text file path hardcoded", "hardcoded_txt_path"),
]


_VERSION_HARDCODE_PATTERN: re.Pattern[str] = re.compile(r"(?:import|from)\s+(\w+)\s*==\s*[\d.]+")


_CYCLE_PATTERN: re.Pattern[str] = re.compile(r"(?:from|import)\s+tests\.|(?:from|import)\s+test_")


def scan_naming_magic(project_root: str) -> list[NamingMagicAlert]:
    alerts: list[NamingMagicAlert] = []

    py_files = [
        p
        for p in Path(project_root).rglob("*.py")
        if all(s not in str(p).lower() for s in (".git", "__pycache__", ".venv", "venv"))
    ]

    for pf in py_files:
        try:
            content = pf.read_text(encoding="utf-8")

        except Exception:
            continue

        for pattern, desc, magic_type in _IMPLICIT_FILE_PATTERNS:
            rx = re.compile(pattern)

            for match in rx.finditer(content):
                line_no = content[: match.start()].count("\n") + 1

                alerts.append(
                    NamingMagicAlert(
                        alert_id=(f"naming-magic-{magic_type}-{pf.stem}-L{line_no}"),
                        file_path=str(pf),
                        line_no=line_no,
                        magic_type=magic_type,
                        current_code=match.group(0)[:80],
                        description=desc,
                    )
                )

        for match in _VERSION_HARDCODE_PATTERN.finditer(content):
            line_no = content[: match.start()].count("\n") + 1

            alerts.append(
                NamingMagicAlert(
                    alert_id=(f"naming-magic-version-{pf.stem}-L{line_no}"),
                    file_path=str(pf),
                    line_no=line_no,
                    magic_type="version_hardcode",
                    current_code=match.group(0),
                    description=(f"Library version hardcoded in import: {match.group(0)}"),
                    severity="MINOR",
                )
            )

        for match in _CYCLE_PATTERN.finditer(content):
            line_no = content[: match.start()].count("\n") + 1

            alerts.append(
                NamingMagicAlert(
                    alert_id=(f"naming-magic-cycle-{pf.stem}-L{line_no}"),
                    file_path=str(pf),
                    line_no=line_no,
                    magic_type="hidden_cycle",
                    current_code=match.group(0),
                    description=(f"Production code imports test module: {match.group(0)}"),
                    severity="CRITICAL",
                )
            )

    return alerts
