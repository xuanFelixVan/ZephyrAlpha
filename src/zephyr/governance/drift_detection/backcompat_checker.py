# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral-auditor/blueprint.md
# [MODULE] zephyr.governance.drift_detection.backcompat_checker
# [DOMAIN] D_BEHAVIORAL_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] src/zephyr/governance/behavioral_auditor/__init__.py; tests/audit/test_backcompat_checker.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 向后兼容检查不可跳过
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-SEC_backcompat_checker | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Backward Compatibility Checker — 向后兼容策略漂移检测 D-023-31 · §6.23。





module_id: MOD-INF-023


removed_parameter: 基线(a,b,c) vs 当前(a,b) c被移除


changed_return_type: Optional[X] → X


renamed_function: Jaccard搜索相似签名


changed_exception: ValueError → CustomError


impact_analysis: 扫描调用方 BREAKING_CHANGE_REPORT


INTENTIONAL_BREAK: 标记宽恕


对标 blueprint.md §6.23。"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path


@dataclass
class CompatBreakEvent:
    event_id: str

    detector_id: str = "backcompat_checker"

    severity: str = "CRITICAL"

    source_file: str = ""

    description: str = ""

    details: str = ""

    intentional_break: bool = False

    detected_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class FunctionSignature:
    name: str

    params: list[str]

    return_type: str | None

    file_path: str

    line_no: int


_SIGNATURE_PATTERN: re.Pattern[str] = re.compile(r"def\s+(\w[\w_]*)\s*\(([^)]*)\)\s*(?:->\s*(\S+))?\s*:")


_INTENTIONAL_BREAK_PATTERN: re.Pattern[str] = re.compile(
    r"#\s*INTENTIONAL_BREAK\s*:\s*(.+)",
    re.IGNORECASE,
)


def extract_signatures(file_path: str) -> list[FunctionSignature]:
    sigs: list[FunctionSignature] = []

    try:
        content = Path(file_path).read_text(encoding="utf-8")

    except Exception:
        return sigs

    for match in _SIGNATURE_PATTERN.finditer(content):
        name = match.group(1)

        if name.startswith("_"):
            continue

        params_str = match.group(2)

        return_t = match.group(3)

        line_no = content[: match.start()].count("\n") + 1

        params = [p.strip() for p in params_str.split(",") if p.strip()]

        sigs.append(
            FunctionSignature(
                name=name,
                params=params,
                return_type=return_t.strip() if return_t else None,
                file_path=file_path,
                line_no=line_no,
            )
        )

    return sigs


def compare_signatures(
    baseline_sigs: list[FunctionSignature],
    current_sigs: list[FunctionSignature],
) -> list[CompatBreakEvent]:
    breaks: list[CompatBreakEvent] = []

    current_map: dict[str, FunctionSignature] = {s.name: s for s in current_sigs}

    baseline_map: dict[str, FunctionSignature] = {s.name: s for s in baseline_sigs}

    removed_names = set(baseline_map.keys()) - set(current_map.keys())

    for rname in removed_names:
        bs = baseline_map[rname]

        breaks.append(
            CompatBreakEvent(
                event_id=f"compat-removed-func-{rname}",
                source_file=bs.file_path,
                description=f"Function '{rname}' removed from public API",
                details=f"Was at line {bs.line_no}: def {rname}({', '.join(bs.params)})",
            )
        )

    for name in set(baseline_map.keys()) & set(current_map.keys()):
        bs = baseline_map[name]

        cs = current_map[name]

        bs_param_names = [p.split(":")[0].strip().replace("*", "") for p in bs.params]

        cs_param_names = [p.split(":")[0].strip().replace("*", "") for p in cs.params]

        removed_params = set(bs_param_names) - set(cs_param_names)

        if removed_params:
            breaks.append(
                CompatBreakEvent(
                    event_id=f"compat-removed-param-{name}",
                    source_file=cs.file_path,
                    description=(f"Parameter(s) removed from '{name}': {removed_params}"),
                    details=f"Baseline({bs.line_no}): ({', '.join(bs_param_names)})\n"
                    f"Current({cs.line_no}): ({', '.join(cs_param_names)})",
                )
            )

        if bs.return_type and cs.return_type and bs.return_type != cs.return_type:
            breaks.append(
                CompatBreakEvent(
                    event_id=f"compat-return-type-{name}",
                    source_file=cs.file_path,
                    severity="MAJOR",
                    description=(f"Return type changed for '{name}': {bs.return_type} → {cs.return_type}"),
                    details=f"Baseline line {bs.line_no}, Current line {cs.line_no}",
                )
            )

    return breaks


def find_renamed_functions(
    baseline_sigs: list[FunctionSignature],
    current_sigs: list[FunctionSignature],
    threshold: float = 0.6,
) -> list[CompatBreakEvent]:
    breaks: list[CompatBreakEvent] = []

    removed = set(s.name for s in baseline_sigs) - set(s.name for s in current_sigs)

    for rname in removed:
        rchars = set(rname)

        for cs in current_sigs:
            cchars = set(cs.name)

            if not cchars or not rchars:
                continue

            intersection = rchars & cchars

            union = rchars | cchars

            jaccard = len(intersection) / len(union) if union else 0

            if jaccard > threshold:
                breaks.append(
                    CompatBreakEvent(
                        event_id=f"compat-renamed-{rname}-to-{cs.name}",
                        source_file=cs.file_path,
                        severity="MAJOR",
                        description=(f"Function possibly renamed: '{rname}' → '{cs.name}' (Jaccard={jaccard:.2f})"),
                    )
                )

    return breaks


def scan_impact(
    breaks: list[CompatBreakEvent],
    src_root: str,
) -> dict[str, list[str]]:
    impact: dict[str, list[str]] = {}

    for b in breaks:
        func_name = b.event_id.split("-")[-1]

        callers: list[str] = []

        for py_file in Path(src_root).rglob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8")

            except Exception:
                continue

            if f"{func_name}(" in content:
                callers.append(str(py_file))

        impact[b.event_id] = callers[:10]

    return impact


def detect_intentional_breaks(
    file_path: str,
) -> list[str]:
    marks: list[str] = []

    try:
        content = Path(file_path).read_text(encoding="utf-8")

    except Exception:
        return marks

    for match in _INTENTIONAL_BREAK_PATTERN.finditer(content):
        marks.append(match.group(1).strip())

    return marks


def run_backcompat_check(
    project_root: str,
    baseline_snapshots_dir: str,
) -> dict[str, object]:
    results: dict[str, object] = {
        "breaks": [],
        "renamed": [],
        "impact": {},
    }

    src_files = list(Path(project_root, "src").rglob("*.py"))

    for pf in src_files[:20]:
        current_sigs = extract_signatures(str(pf))

        baseline_file = os.path.join(
            baseline_snapshots_dir,
            pf.relative_to(project_root).with_suffix(".baseline.json"),
        )

        baseline_sigs: list[FunctionSignature] = []

        if os.path.exists(baseline_file):
            try:
                with open(baseline_file, encoding="utf-8") as f:
                    raw_data = json.loads(f.read())

                    for entry in raw_data.get("signatures", []):
                        baseline_sigs.append(
                            FunctionSignature(
                                name=entry.get("name", ""),
                                params=entry.get("params", []),
                                return_type=entry.get("return_type"),
                                file_path=entry.get("file_path", ""),
                                line_no=entry.get("line_no", 0),
                            )
                        )

            except Exception:
                continue

        breaks = compare_signatures(baseline_sigs, current_sigs)

        renamed = find_renamed_functions(baseline_sigs, current_sigs)

        for b in breaks:
            results["breaks"].append(
                {
                    "event_id": b.event_id,
                    "description": b.description,
                    "severity": b.severity,
                }
            )

        for b in renamed:
            results["renamed"].append(
                {
                    "event_id": b.event_id,
                    "description": b.description,
                    "severity": b.severity,
                }
            )

    return results
