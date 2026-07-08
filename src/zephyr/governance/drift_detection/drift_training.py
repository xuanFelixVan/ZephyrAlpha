# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.governance.drift_detection.drift_training
# [DOMAIN] D_BEHAVIORAL_AUDIT
# [DEPENDENCIES] zephyr.governance.drift_detection.drift_models
# [CONSUMERS] src/zephyr/governance/behavioral_auditor/__init__.py; src/zephyr/governance/drift_detection/_drift.py; tests/drift/test_drift_training.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 训练模式提取不可遗漏
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-SEC_drift_training | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Drift Detector AI 训练闭环 + 跨语言检测 — drift_training.py





module_id: MOD-INF-023 (SRC-0034)


漂移事件 -> 训练模式提取 -> Prompt 注入 -> 效果追踪 -> 跨语言漂移检测框架。


从 drift_engine.py 提取，对标 blueprint.md §6.12/§6.18。"""

from __future__ import annotations

from typing import Final
import json
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path

from .drift_models import DriftEvent, DriftState, ScanLevel, Severity

# ── §6.12 AI Training Loop ──────────────────────────────────


@dataclass
class DriftTrainingPattern:
    """AI 训练模式 — 从重复漂移事件中提取的可训练模式（§6.12）。





    Fields:


        pattern_id: 模式唯一标识。


        detector_id: 来源检测器 ID。


        frequency: 30 天内复发次数。


        dimension: 漂移维度。


        commit_diff_pattern: 关联的 commit diff 摘要。


        root_cause_summary: 根因摘要（≤200 字符）。


        first_seen: 首次出现时间。


        last_seen: 最近一次出现时间。


        injected: 是否已将模式注入 Prompt/AGENTS.md。


        effectiveness: 注入后的抑制效果（0.0~1.0），None 表示未追踪。


    """

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
    """AI 训练闭环结果（§6.12）。





    Fields:


        detector_name: 检测器标识。


        patterns_extracted: 提取的训练模式数。


        patterns_injected: 已注入 Prompt 的模式数。


        patterns_suppressed: 被有效抑制的模式数（effectiveness > 0.5）。


    """

    detector_name: str = "ai_training_loop"

    patterns_extracted: int = 0

    patterns_injected: int = 0

    patterns_suppressed: int = 0


def extract_training_patterns(project_root: str, days: int = 30) -> list[DriftTrainingPattern]:
    """从 ``data/drift/`` 目录中提取重复漂移事件作为训练模式。





    扫描 drift JSON 日志，对同一 detector_id 多次出现的事件


    聚合成 ``DriftTrainingPattern``，记录频次和根因摘要。





    Args:


        project_root: 项目根目录。


        days: 回溯天数，默认 30。





    Returns:


        list[DriftTrainingPattern]: 按频次降序排列的训练模式列表。


    """

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
    """将训练模式注入 Prompt — 生成 Markdown 格式的防御规则文本。





    选取频次最高的 5 个模式，生成 ``## AI Error-Prone Patterns`` 段落，


    可追加到 AGENTS.md 或系统 Prompt 中。





    Args:


        patterns: 待注入的训练模式列表（按频次排序）。





    Returns:


        str: Markdown 格式的防御规则文本。


    """

    lines: list[str] = ["## AI Error-Prone Patterns (from drift training loop)", ""]

    for p in patterns[:5]:
        lines.append(f"- **[{p.detector_id}]** freq={p.frequency}: {p.root_cause_summary[:150]}")

    lines.append("")

    lines.append(f"> These {len(patterns)} patterns were extracted from drift events. Avoid repeating them.")

    return "\n".join(lines)


def track_training_effectiveness(
    pattern: DriftTrainingPattern,
    post_injection_freq: int,
) -> float:
    """追踪训练效果 — 计算注入后的复发减少率。





    Args:


        pattern: 已注入的训练模式。


        post_injection_freq: 注入后的复发次数。





    Returns:


        float: 抑制率（0.0~1.0），``1 - post/pre`` 且下限为 0。


    """

    if pattern.frequency == 0:
        return 0.0

    reduction = 1.0 - (post_injection_freq / pattern.frequency)

    return max(0.0, reduction)


def detect_ai_training_loop(project_root: str) -> list[DriftEvent]:
    """检测 AI 训练闭环 — 周期性提取模式并评估注入效果。





    组合 ``extract_training_patterns`` + ``inject_patterns_to_prompt``


    + ``track_training_effectiveness``，将高复发模式标记为


    候选永久纳入 AGENTS.md。





    Args:


        project_root: 项目根目录。





    Returns:


        list[DriftEvent]: 每个复发模式及成功抑制的模式各对应一个事件。


    """

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
                description=(f"AI error pattern [{p.detector_id}] recurred {p.frequency} times in 30 days"),
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
                    description=(f"Pattern {p.pattern_id} suppressed by {p.effectiveness:.0%} after prompt injection"),
                    details="Candidate for permanent inclusion in AGENTS.md",
                    timestamp=datetime.now(UTC),
                    state=DriftState.DETECTED,
                    scan_level=ScanLevel.STANDARD,
                    auto_fixable=False,
                )
            )

    return events


# ── §6.18 Cross-Language Drift Detection ─────────────────────


LANGUAGE_AGNOSTIC_DIMENSIONS: Final[list[str]] = [
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


LANGUAGE_SPECIFIC_INTERFACES: Final[dict[str, list[str]]] = {
    "Python": ["parse_python_imports", "parse_python_public_api", "detect_python_dead_code"],
    "TypeScript": [],
    "Go": [],
    "Rust": [],
}


@dataclass
class CrossLanguageConfig:
    """跨语言漂移检测配置（§6.18）。





    Fields:


        enabled_languages: 启用的语言列表，默认 ``["Python"]``。


        agnostic_dimensions: 语言无关的漂移维度（D5-* 系列）。


        fallback_on_unsupported: 不支持的语言是否回退到通用检查。


    """

    enabled_languages: list[str] = field(default_factory=lambda: ["Python"])

    agnostic_dimensions: list[str] = field(default_factory=LANGUAGE_AGNOSTIC_DIMENSIONS.copy)

    fallback_on_unsupported: bool = True


CROSS_LANG_CONFIG: Final[CrossLanguageConfig] = CrossLanguageConfig()


def parse_python_imports(file_path: str) -> list[str]:
    """解析 Python 文件的 import 语句列表。





    Args:


        file_path: Python 源文件路径。





    Returns:


        list[str]: 所有 ``import X`` 和 ``from X import Y`` 中的模块名。


    """

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
    """解析 Python 文件的公开 API — 非下划线开头的顶层函数名。





    Args:


        file_path: Python 源文件路径。





    Returns:


        list[str]: 公开函数名列表。


    """

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
    """检测 Python 死代码 — 仅定义一次且仅调用一次的公开函数。





    对于每个非下划线开头的顶层函数，统计其调用次数。


    若调用次数 ≤ 定义次数（且只定义了一次），视为死代码。





    Args:


        file_path: Python 源文件路径。





    Returns:


        list[str]: 疑似死代码的函数名列表。


    """

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


LANG_INTERFACE_IMPL: Final[dict[str, object]] = {
    "parse_python_imports": parse_python_imports,
    "parse_python_public_api": parse_python_public_api,
    "detect_python_dead_code": detect_python_dead_code,
}


def detect_cross_language_drift(project_root: str) -> list[DriftEvent]:
    """检测跨语言漂移 — 按启用的语言枚举文件覆盖与维度对齐（§6.18）。





    对每种启用的语言统计源文件数量，与语言无关维度数对比，


    生成覆盖率事件。未来可扩展为语言特定检测器的路由。





    Args:


        project_root: 项目根目录。





    Returns:


        list[DriftEvent]: 每种语言对应一个 INFO 级别的覆盖事件。


    """

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
                details=(f"Language-agnostic dims: {CROSS_LANG_CONFIG.agnostic_dimensions}"),
                timestamp=datetime.now(UTC),
                state=DriftState.DETECTED,
                scan_level=ScanLevel.STANDARD,
                auto_fixable=False,
            )
        )

    return events
