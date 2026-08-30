# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.gov_drift.config_consistency
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES]
# [CONSUMERS] src/zephyr/gov_drift/_core.py ; src/zephyr/gov_drift/_infrastructure.py ; tests/config/test_config_consistency.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 配置一致性检查不可绕过
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-INF-023 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Config Consistency Checker — 配置多源一致性 D-023-29 · §6.21。


三源(.env / YAML / 硬编码defaults)提取所有配置键


三类告警: CONFIG_CONFLICT / MISSING_SECRET_WARNING / UNUSED_CONFIG


YAML为SSoT，auto_fix生成config_sync.yaml


对标 blueprint.md §6.21。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: filepath 参数
#   fields: 参数 filepath，类型注解 str
#   code: config_consistency.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: src_root 参数
#   fields: 参数 src_root，类型注解 str
#   code: config_consistency.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: yaml_source 参数
#   fields: 参数 yaml_source，类型注解 ConfigSource
#   code: config_consistency.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: env_source 参数
#   fields: 参数 env_source，类型注解 ConfigSource
#   code: config_consistency.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① parse_yaml_config
#   name_en: parse_yaml_config
#   intro: parse_yaml_config(filepath) 源码 L193-L210
#   desc: 源码 L193-L210
#   inputs: filepath
#   outputs: ConfigSource
# - id: A2
#   name_zh: ② parse_env_config
#   name_en: parse_env_config
#   intro: parse_env_config(filepath) 源码 L213-L230
#   desc: 源码 L213-L230
#   inputs: filepath
#   outputs: ConfigSource
# - id: A3
#   name_zh: ③ extract_hardcoded_defaults
#   name_en: extract_hardcoded_defaults
#   intro: extract_hardcoded_defaults(src_root) 源码 L233-L252
#   desc: 源码 L233-L252
#   inputs: src_root
#   outputs: ConfigSource
# - id: A4
#   name_zh: ④ detect_conflicts
#   name_en: detect_conflicts
#   intro: detect_conflicts(yaml_source, env_source, code_source) 源码 L…
#   desc: 源码 L255-L313
#   inputs: yaml_source env_source code_source
#   outputs: ConfigAuditReport
# - id: A5
#   name_zh: ⑤ generate_config_sync
#   name_en: generate_config_sync
#   intro: 生成 config_sync.yaml 作为 SSoT 同步输出。
#   desc: 生成 config_sync.yaml 作为 SSoT 同步输出。；源码 L316-L354
#   inputs: report yaml_source
#   outputs: str
# - id: A6
#   name_zh: ⑥ run_config_audit
#   name_en: run_config_audit
#   intro: 执行完整的多源配置审计。
#   desc: 执行完整的多源配置审计。；源码 L357-L388
#   inputs: project_root
#   outputs: dict[str, object]
#   （注：A6 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: ConfigSource
#   name_en: ConfigSource
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: src/zephyr/gov_drift/_core.py ; src/zephyr/gov_drift/_infrastructure.py ; tests…
# - id: O2
#   name_zh: ConfigAuditReport
#   name_en: ConfigAuditReport
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: src/zephyr/gov_drift/_core.py ; src/zephyr/gov_drift/_infrastructure.py ; tests…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> A6
# A6 --> O1
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Final


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

    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
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

    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
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

        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
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
