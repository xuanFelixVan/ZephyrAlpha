"""
Drift Detector AI 训练闭环 + 跨语言检测 — drift_training.py

module_id: MOD-INF-023 (SRC-0034)
漂移事件 → 训练模式提取 → Prompt 注入 → 效果追踪 → 跨语言漂移检测框架。
从 drift_engine.py 提取，对标 blueprint.md §6.12/§6.18。
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path

from .drift_models import DriftEvent, DriftState, ScanLevel, Severity

# ── §6.12 AI Training Loop ──────────────────────────────────


@dataclass
class DriftTrainingPattern:
    pattern_id: str
    detector_id: str
    frequency: int
    dimension: str
    commit_diff_pattern: str
    root_cause_summary: str
    first_seen: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_seen: datetime = field(default_factory=lambda: datetime.now(UTC))
    injected: bool = False
    effectiveness: float | None = None


@dataclass
class AITrainingLoopResult:
    detector_name: str = "ai_training_loop"
    patterns_extracted: int = 0
    patterns_injected: int = 0
    patterns_suppressed: int = 0


def extract_training_patterns(project_root: str, days: int = 30) -> list[DriftTrainingPattern]:
    patterns: list[DriftTrainingPattern] = []
    drift_data_dir = Path(project_root) / "data" / "drift"

    if not drift_data_dir.exists():
        return patterns

    threshold = datetime.now(UTC) - timedelta(days=days)
    dim_freq: dict[str, int] = {}
    dim_events: dict[str, list[dict[str, object]]] = {}

    for json_file in drift_data_dir.glob("*.json"):
        try:
            mtime = datetime.fromtimestamp(json_file.stat().st_mtime, tz=UTC)
            if mtime < threshold:
                continue
            data = json.loads(json_file.read_text(encoding="utf-8"))
            events_data = data if isinstance(data, list) else data.get("events", [])
            for evt in events_data:
                dim = str(evt.get("detector_id", "unknown"))
                dim_freq[dim] = dim_freq.get(dim, 0) + 1
                dim_events.setdefault(dim, []).append(evt)
        except Exception:
            continue

    for dim, freq in dim_freq.items():
        if freq >= 3 and dim in dim_events:
            events_sample = dim_events[dim][:10]
            descriptions = [str(e.get("description", "")) for e in events_sample]
            root_cause = descriptions[0][:200] if descriptions else "Pattern analysis pending"

            patterns.append(
                DriftTrainingPattern(
                    pattern_id=f"pattern-{dim}-{freq}",
                    detector_id=dim,
                    frequency=freq,
                    dimension=dim,
                    commit_diff_pattern="git diff analysis pending",
                    root_cause_summary=root_cause,
                )
            )

    return patterns


def inject_patterns_to_prompt(
    patterns: list[DriftTrainingPattern],
) -> str:
    lines: list[str] = ["## AI Error-Prone Patterns (from drift training loop)", ""]
    for p in patterns[:5]:
        lines.append(f"- **[{p.detector_id}]** freq={p.frequency}: " f"{p.root_cause_summary[:150]}")
    lines.append("")
    lines.append(f"> These {len(patterns)} patterns were extracted from " f"drift events. Avoid repeating them.")
    return "\n".join(lines)


def track_training_effectiveness(
    pattern: DriftTrainingPattern,
    post_injection_freq: int,
) -> float:
    if pattern.frequency == 0:
        return 0.0
    reduction = 1.0 - (post_injection_freq / pattern.frequency)
    return max(0.0, reduction)


def detect_ai_training_loop(project_root: str) -> list[DriftEvent]:
    events: list[DriftEvent] = []
    patterns = extract_training_patterns(project_root, days=30)

    if not patterns:
        return events

    for p in patterns:
        events.append(
            DriftEvent(
                event_id=f"drift-train-pattern-{p.pattern_id}",
                detector_id="ai_training_loop",
                severity=Severity.INFO,
                source_file="drift_training_loop",
                description=(f"AI error pattern [{p.detector_id}] " f"recurred {p.frequency} times in 30 days"),
                details=(
                    f"Root cause: {p.root_cause_summary[:200]}. "
                    f"Injected: {p.injected}, "
                    f"Effectiveness: {p.effectiveness or 'untracked'}"
                ),
                timestamp=datetime.now(UTC),
                state=DriftState.DETECTED,
                scan_level=ScanLevel.STANDARD,
                auto_fixable=False,
            )
        )

    injected_count = sum(1 for p in patterns if p.injected)
    if injected_count > 0:
        effective = [p for p in patterns if p.injected and p.effectiveness is not None and p.effectiveness > 0.5]
        for p in effective:
            events.append(
                DriftEvent(
                    event_id=f"drift-train-suppressed-{p.pattern_id}",
                    detector_id="ai_training_loop",
                    severity=Severity.INFO,
                    source_file="AGENTS.md",
                    description=(
                        f"Pattern {p.pattern_id} suppressed " f"by {p.effectiveness:.0%} after prompt injection"
                    ),
                    details="Candidate for permanent inclusion in AGENTS.md",
                    timestamp=datetime.now(UTC),
                    state=DriftState.DETECTED,
                    scan_level=ScanLevel.STANDARD,
                    auto_fixable=False,
                )
            )

    return events


# ── §6.18 Cross-Language Drift Detection ─────────────────────

LANGUAGE_AGNOSTIC_DIMENSIONS: list[str] = [
    "D5-YAML-DISK",
    "D5-DIRTY-GIT",
    "D5-EVOLUTION",
    "D5-SEMANTIC",
    "D5-SECURITY",
    "D5-DEPENDENCY",
    "D5-TEST-COV",
    "D5-CASCADE",
    "D5-DOC-COEVOL",
]

LANGUAGE_SPECIFIC_INTERFACES: dict[str, list[str]] = {
    "Python": ["parse_python_imports", "parse_python_public_api", "detect_python_dead_code"],
    "TypeScript": [],
    "Go": [],
    "Rust": [],
}


@dataclass
class CrossLanguageConfig:
    enabled_languages: list[str] = field(default_factory=lambda: ["Python"])
    agnostic_dimensions: list[str] = field(default_factory=LANGUAGE_AGNOSTIC_DIMENSIONS.copy)
    fallback_on_unsupported: bool = True


CROSS_LANG_CONFIG = CrossLanguageConfig()


def parse_python_imports(file_path: str) -> list[str]:
    imports: list[str] = []
    try:
        content = Path(file_path).read_text(encoding="utf-8")
    except Exception:
        return imports
    for match in re.finditer(
        r"^(?:from\s+([\w.]+)\s+import|import\s+([\w.]+))",
        content,
        re.MULTILINE,
    ):
        imp = match.group(1) or match.group(2)
        if imp:
            imports.append(imp)
    return imports


def parse_python_public_api(file_path: str) -> list[str]:
    apis: list[str] = []
    try:
        content = Path(file_path).read_text(encoding="utf-8")
    except Exception:
        return apis
    for match in re.finditer(
        r"^def\s+(\w[\w_]*)\s*\(",
        content,
        re.MULTILINE,
    ):
        name = match.group(1)
        if not name.startswith("_"):
            apis.append(name)
    return apis


def detect_python_dead_code(file_path: str) -> list[str]:
    dead: list[str] = []
    try:
        content = Path(file_path).read_text(encoding="utf-8")
    except Exception:
        return dead
    functions = re.findall(
        r"def\s+(\w[\w_]*)\s*\(([^)]*)\)",
        content,
    )
    for func_name, _func_args in functions:
        if func_name.startswith("_"):
            continue
        func_escaped = re.escape(func_name)
        calls = len(
            re.findall(
                rf"\b{func_escaped}\s*\(",
                content,
            )
        )
        definition_count = content.count(f"def {func_name}")
        if calls <= definition_count and definition_count == 1:
            dead.append(func_name)
    return dead


LANG_INTERFACE_IMPL: dict[str, object] = {
    "parse_python_imports": parse_python_imports,
    "parse_python_public_api": parse_python_public_api,
    "detect_python_dead_code": detect_python_dead_code,
}


def detect_cross_language_drift(project_root: str) -> list[DriftEvent]:
    events: list[DriftEvent] = []
    src_root = Path(project_root) / "src"

    if not src_root.exists():
        return events

    language_extensions: dict[str, list[str]] = {
        "Python": ["*.py"],
        "TypeScript": ["*.ts", "*.tsx"],
        "Go": ["*.go"],
        "Rust": ["*.rs"],
    }

    for lang in CROSS_LANG_CONFIG.enabled_languages:
        extensions = language_extensions.get(lang, [])
        if not extensions:
            continue

        lang_files: list[Path] = []
        for ext in extensions:
            lang_files.extend(src_root.rglob(ext))

        if not lang_files:
            continue

        events.append(
            DriftEvent(
                event_id=f"drift-crosslang-{lang.lower()}-coverage",
                detector_id="cross_language_drift",
                severity=Severity.INFO,
                source_file=str(src_root),
                description=(
                    f"Cross-language check: {lang} has "
                    f"{len(lang_files)} files, "
                    f"{len(CROSS_LANG_CONFIG.agnostic_dimensions)} "
                    f"agnostic dimensions"
                ),
                details=(f"Language-agnostic dims: " f"{CROSS_LANG_CONFIG.agnostic_dimensions}"),
                timestamp=datetime.now(UTC),
                state=DriftState.DETECTED,
                scan_level=ScanLevel.STANDARD,
                auto_fixable=False,
            )
        )

    return events
