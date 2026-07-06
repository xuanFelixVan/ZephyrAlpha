# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.governance.drift_detection.test_fixture_checker
# [DOMAIN] D_BEHAVIORAL_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] src/zephyr/governance/behavioral_auditor/__init__.py; src/zephyr/governance/drift_detection/_scanners.py; tests/audit/test_test_fixture_checker.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 测试夹具检查不可跳过
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-SEC_test_fixture_checker | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Test Fixture Checker — 测试夹具漂移检测 D-023-28 · §6.20。





module_id: MOD-INF-023


fixture_schema_drift: 夹具硬编码数据结构 vs ORM/pydantic schema


mock_target_drift: mock.patch路径 vs 实际模块路径


expected_output_drift: assert expected_value来源


auto_fixable=false: 测试漂移最隐蔽——测试通过不代表系统正确


对标 blueprint.md §6.20。"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path


@dataclass
class FixtureDriftEvent:
    event_id: str

    fixture_file: str

    fixture_type: str

    target_module: str

    detected_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    description: str = ""

    severity: str = "MAJOR"


FIXTURE_DETECTORS: dict[str, object] = {}


def scan_fixture_schema_drift(
    test_root: str,
    src_root: str,
) -> list[FixtureDriftEvent]:
    """检查测试夹具中硬编码数据结构是否与 ORM/pydantic schema 一致。"""

    events: list[FixtureDriftEvent] = []

    test_path = Path(test_root)

    src_path = Path(src_root)

    fixture_patterns: list[tuple[str, re.Pattern[str]]] = [
        ("dict_fixture", re.compile(r"(\w+)\s*=\s*\{([^}]+)\}")),
        ("list_fixture", re.compile(r"(\w+)\s*=\s*\[([^\]]+)\]")),
        ("mock_patch", re.compile(r"(?:mock\.patch|patch)\(['\"]([^'\"]+)['\"]")),
    ]

    for py_file in test_path.rglob("test_*.py"):
        try:
            content = py_file.read_text(encoding="utf-8")

        except Exception:
            continue

        for fixture_type, pattern in fixture_patterns:
            for match in pattern.finditer(content):
                if fixture_type == "mock_patch":
                    mocked_path = match.group(1)

                    events.append(
                        FixtureDriftEvent(
                            event_id=f"fixture-mock-{py_file.stem}-{mocked_path.replace('.', '-')}",
                            fixture_file=str(py_file),
                            fixture_type="mock_target",
                            target_module=mocked_path,
                            description=(
                                f"Mock target '{mocked_path}' in "
                                f"{py_file.name} — verify path matches "
                                f"actual module path"
                            ),
                            severity="MINOR",
                        )
                    )

                elif fixture_type == "dict_fixture":
                    var_name = match.group(1)

                    dict_body = match.group(2)

                    field_count = len(re.findall(r"'(\w+)'\s*:", dict_body))

                    if field_count >= 3:
                        events.append(
                            FixtureDriftEvent(
                                event_id=f"fixture-dict-{py_file.stem}-{var_name}",
                                fixture_file=str(py_file),
                                fixture_type="dict_fixture",
                                target_module=var_name,
                                description=(
                                    f"Dict fixture '{var_name}' has "
                                    f"{field_count} fields — "
                                    f"verify against ORM/pydantic schema"
                                ),
                                severity="MAJOR",
                            )
                        )

    return events


def scan_mock_target_drift(
    test_root: str,
    src_root: str,
) -> list[FixtureDriftEvent]:
    """检查 mock.patch 路径是否匹配实际模块路径。"""

    events: list[FixtureDriftEvent] = []

    test_path = Path(test_root)

    src_path = Path(src_root)

    src_modules: set[str] = set()

    for py_file in src_path.rglob("*.py"):
        rel = py_file.relative_to(src_path)

        module_path = str(rel.with_suffix("")).replace(os.sep, ".")

        src_modules.add(module_path)

    for py_file in test_path.rglob("test_*.py"):
        try:
            content = py_file.read_text(encoding="utf-8")

        except Exception:
            continue

        mock_matches = re.findall(
            r"(?:mock\.patch|patch)\(['\"]([^'\"]+)['\"]",
            content,
        )

        for mocked in mock_matches:
            resolved = mocked.replace(".", os.sep)

            found = any(resolved in str(m) for m in src_modules)

            if not found and "." in mocked:
                events.append(
                    FixtureDriftEvent(
                        event_id=f"fixture-mock-orphan-{mocked.replace('.', '-')}",
                        fixture_file=str(py_file),
                        fixture_type="mock_target",
                        target_module=mocked,
                        description=(f"Mock target '{mocked}' not found in src/ modules"),
                        severity="MAJOR",
                    )
                )

    return events


def scan_expected_output_drift(
    test_root: str,
) -> list[FixtureDriftEvent]:
    """检查 assert 中的 expected_value 是否有明确来源标注。"""

    events: list[FixtureDriftEvent] = []

    test_path = Path(test_root)

    assert_pattern = re.compile(
        r"assert\s+\w+\s*(?:==|!=|in|not in|is|is not)\s+(.+?)(?:\n|#|$)",
        re.MULTILINE,
    )

    for py_file in test_path.rglob("test_*.py"):
        try:
            content = py_file.read_text(encoding="utf-8")

        except Exception:
            continue

        for match in assert_pattern.finditer(content):
            expected = match.group(1).strip()

            if not re.search(r"#\s*(?:from|source|expected|baseline)", content[match.start() : match.start() + 200]):
                if len(expected) < 50:
                    continue

                events.append(
                    FixtureDriftEvent(
                        event_id=(f"fixture-assert-{py_file.stem}-L{content[: match.start()].count(chr(10)) + 1}"),
                        fixture_file=str(py_file),
                        fixture_type="expected_output",
                        target_module=expected[:50],
                        description=(f"Assert expected value lacks source annotation in {py_file.name}"),
                        severity="INFO",
                    )
                )

    return events


def run_fixture_check(project_root: str) -> dict[str, object]:
    """运行完整的测试夹具漂移检查。"""

    test_root = os.path.join(project_root, "tests")

    src_root = os.path.join(project_root, "src")

    results: dict[str, object] = {
        "schema_drifts": [],
        "mock_drifts": [],
        "output_drifts": [],
        "summary": {},
    }

    schema_events = scan_fixture_schema_drift(test_root, src_root)

    mock_events = scan_mock_target_drift(test_root, src_root)

    output_events = scan_expected_output_drift(test_root)

    results["schema_drifts"] = [
        {
            "event_id": e.event_id,
            "file": e.fixture_file,
            "type": e.fixture_type,
            "description": e.description,
        }
        for e in schema_events
    ]

    results["mock_drifts"] = [
        {
            "event_id": e.event_id,
            "file": e.fixture_file,
            "target": e.target_module,
            "description": e.description,
        }
        for e in mock_events
    ]

    results["output_drifts"] = [
        {
            "event_id": e.event_id,
            "file": e.fixture_file,
            "severity": e.severity,
            "description": e.description,
        }
        for e in output_events
    ]

    results["summary"] = {
        "total": len(schema_events) + len(mock_events) + len(output_events),
        "schema_drifts": len(schema_events),
        "mock_drifts": len(mock_events),
        "output_drifts": len(output_events),
        "auto_fixable": False,
    }

    return results
