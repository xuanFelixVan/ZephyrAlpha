# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.gov_drift.config_consistency
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES]
# [CONSUMERS] src/zephyr/governance/behavioral_auditor/__init__.py; src/zephyr/governance/drift_detection/_core.py; src/zephyr/governance/drift_detection/_infrastructure.py; tests/config/test_config_consistency.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 配置一致性检查不可绕过
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-SEC_config_consistency | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Config Consistency Checker — 配置多源一致性 D-023-29 · §6.21。





module_id: MOD-INF-023


三源(.env / YAML / 硬编码defaults)提取所有配置键


三类告警: CONFIG_CONFLICT / MISSING_SECRET_WARNING / UNUSED_CONFIG


YAML为SSoT，auto_fix生成config_sync.yaml


对标 blueprint.md §6.21。"""

from __future__ import annotations

from typing import Final
import os
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path


@dataclass
class ConfigSource:
    source_type: str

    source_path: str

    entries: dict[str, str] = field(default_factory=dict)


@dataclass
class ConfigConflict:
    key: str

    sources: list[str]

    values: list[str]

    resolved_to: str | None = None


@dataclass
class ConfigAuditReport:
    conflicts: list[ConfigConflict] = field(default_factory=list)

    missing_secrets: list[str] = field(default_factory=list)

    unused_configs: list[str] = field(default_factory=list)

    total_keys: int = 0

    ssot_source: str = "YAML"

    report_time: datetime = field(default_factory=lambda: datetime.now(UTC))


YAML_CONFIG_PATTERN: Final[re.Pattern[str]] = re.compile(r"(\w+)\s*:\s*(.+?)(?:\n|$)")


ENV_CONFIG_PATTERN: Final[re.Pattern[str]] = re.compile(r"^(\w+)\s*=\s*(.+?)$", re.MULTILINE)


HARDCODED_DEFAULT_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"os\.(?:environ|getenv)\.get\(['\"](\w+)['\"]\s*,\s*['\"]([^'\"]+)['\"]"
)


HARDCODED_VAR_PATTERN: Final[re.Pattern[str]] = re.compile(r"(\w+)\s*=\s*(?:os\.environ\.get|os\.getenv)")


SECRET_KEY_INDICATORS: Final[set[str]] = {
    "secret",
    "password",
    "token",
    "api_key",
    "apikey",
    "private_key",
    "jwt_secret",
    "encryption_key",
    "auth_token",
}


def parse_yaml_config(filepath: str) -> ConfigSource:
    cs = ConfigSource(source_type="YAML", source_path=filepath)

    try:
        content = Path(filepath).read_text(encoding="utf-8")

    except Exception:
        return cs

    for match in YAML_CONFIG_PATTERN.finditer(content):
        key = match.group(1).strip()

        val = match.group(2).strip()

        if key and val and not key.startswith("#"):
            cs.entries[key] = val

    return cs


def parse_env_config(filepath: str) -> ConfigSource:
    cs = ConfigSource(source_type="ENV", source_path=filepath)

    try:
        content = Path(filepath).read_text(encoding="utf-8")

    except Exception:
        return cs

    for match in ENV_CONFIG_PATTERN.finditer(content):
        key = match.group(1).strip()

        val = match.group(2).strip()

        if key and val and not key.startswith("#"):
            cs.entries[key] = val

    return cs


def extract_hardcoded_defaults(
    src_root: str,
) -> ConfigSource:
    cs = ConfigSource(source_type="CODE_DEFAULTS", source_path=src_root)

    for py_file in Path(src_root).rglob("*.py"):
        try:
            content = py_file.read_text(encoding="utf-8")

        except Exception:
            continue

        for match in HARDCODED_DEFAULT_PATTERN.finditer(content):
            key = match.group(1)

            val = match.group(2)

            cs.entries[key] = val

    return cs


def detect_conflicts(
    yaml_source: ConfigSource,
    env_source: ConfigSource,
    code_source: ConfigSource,
) -> ConfigAuditReport:
    report = ConfigAuditReport()

    all_keys: set[str] = set()

    all_keys.update(yaml_source.entries.keys())

    all_keys.update(env_source.entries.keys())

    all_keys.update(code_source.entries.keys())

    report.total_keys = len(all_keys)

    for key in sorted(all_keys):
        vals: dict[str, str] = {}

        if key in yaml_source.entries:
            vals["YAML"] = yaml_source.entries[key]

        if key in env_source.entries:
            vals["ENV"] = env_source.entries[key]

        if key in code_source.entries:
            vals["CODE"] = code_source.entries[key]

        unique_vals = set(vals.values())

        if len(vals) >= 2 and len(unique_vals) > 1:
            report.conflicts.append(
                ConfigConflict(
                    key=key,
                    sources=list(vals.keys()),
                    values=list(vals.values()),
                    resolved_to=yaml_source.entries.get(key, list(vals.values())[0]),
                )
            )

        key_lower = key.lower()

        is_secret = any(ind in key_lower for ind in SECRET_KEY_INDICATORS)

        if is_secret and key not in env_source.entries:
            report.missing_secrets.append(key)

    yaml_keys = set(yaml_source.entries.keys())

    env_keys = set(env_source.entries.keys())

    code_keys = set(code_source.entries.keys())

    unused = (env_keys | code_keys) - yaml_keys

    report.unused_configs = sorted(list(unused))

    return report


def generate_config_sync(
    report: ConfigAuditReport,
    yaml_source: ConfigSource,
) -> str:
    """生成 config_sync.yaml 作为 SSoT 同步输出。"""

    lines: list[str] = [
        "# Auto-generated config_sync.yaml — SSoT reconciler output",
        f"# Generated: {report.report_time.isoformat()}",
        f"# Conflicts resolved: {len(report.conflicts)}",
        f"# Missing secrets: {len(report.missing_secrets)}",
        f"# Unused configs: {len(report.unused_configs)}",
        "",
    ]

    lines.append("# Resolved conflicts (YAML SSoT wins)")

    for conflict in report.conflicts:
        lines.append(f"# {conflict.key}: sources={conflict.sources} values={conflict.values}")

        lines.append(f"{conflict.key}: {conflict.resolved_to or ''}")

        lines.append("")

    if report.missing_secrets:
        lines.append("# MISSING_SECRET_WARNING — add these to .env")

        for secret_key in report.missing_secrets:
            lines.append(f"# {secret_key}: <TODO: populate from vault>")

        lines.append("")

    if report.unused_configs:
        lines.append("# UNUSED_CONFIG — present in .env/code but not in YAML SSoT")

        for ukey in report.unused_configs:
            lines.append(f"# unused: {ukey}")

    return "\n".join(lines)


def run_config_audit(project_root: str) -> dict[str, object]:
    """执行完整的多源配置审计。"""

    yaml_path = Path(project_root) / "config.yaml"

    env_path = Path(project_root) / ".env"

    src_root = os.path.join(project_root, "src")

    yaml_source = (
        parse_yaml_config(str(yaml_path))
        if yaml_path.exists()
        else ConfigSource(source_type="YAML", source_path=str(yaml_path))
    )

    env_source = (
        parse_env_config(str(env_path))
        if env_path.exists()
        else ConfigSource(source_type="ENV", source_path=str(env_path))
    )

    code_source = extract_hardcoded_defaults(src_root)

    report = detect_conflicts(yaml_source, env_source, code_source)

    return {
        "conflicts": [{"key": c.key, "sources": c.sources, "values": c.values} for c in report.conflicts],
        "missing_secrets": report.missing_secrets,
        "unused_configs": report.unused_configs,
        "total_keys": report.total_keys,
        "ssot_source": report.ssot_source,
    }
