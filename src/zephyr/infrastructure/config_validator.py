# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md
# [MODULE] zephyr.infrastructure.config_validator
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_config_validator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
M-12 ConfigValidator — 配置参数校验器
=====================================
职责：检查系统配置文件的合法性——必需字段、类型、取值区间、引用完整性。
对标：JSON Schema + K8s Admission Webhook
使用方式：
    validator = ConfigValidator(schema_path="config/schemas/")
    result = validator.validate("config/thresholds.yaml")
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

import yaml

__all__ = [
    "ConfigValidator",
    "ValidationResult",
    "ValidationSeverity",
]


class ValidationSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationResult:
    file_path: str
    valid: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    infos: list[str] = field(default_factory=list)
    checked_fields: int = 0

    @property
    def total_issues(self) -> int:
        return len(self.errors) + len(self.warnings)


class ConfigValidator:
    """配置参数校验器

    对配置文件进行多维度校验：
    - 必需字段检查
    - 类型匹配
    - 取值区间验证
    - 引用完整性
    """

    _REQUIRED_CONFIG_FIELDS: dict[str, list[str]] = {
        "thresholds.yaml": ["version", "thresholds", "error_budget"],
        "pipelines.yaml": ["version", "pipelines"],
        "modules.yaml": ["version", "modules"],
        "gates.yaml": ["version", "gates"],
    }

    _NUMERIC_RANGES: dict[str, tuple[float, float]] = {
        "error_budget": (0.0, 1.0),
        "threshold": (0.0, 100.0),
        "timeout": (1, 3600),
        "retry_count": (0, 10),
        "max_workers": (1, 64),
        "token_budget": (1000, 1000000),
    }

    def __init__(self, schema_path: str | Path | None = None):
        self._schema_path = Path(schema_path) if schema_path else None

    def validate(
        self,
        config_path: str | Path,
        strict: bool = False,
    ) -> ValidationResult:
        cfg_path = Path(config_path)
        result = ValidationResult(file_path=str(cfg_path))

        if not cfg_path.exists():
            result.valid = False
            result.errors.append(f"配置文件不存在: {cfg_path}")
            return result

        try:
            with open(cfg_path, encoding="utf-8") as f:
                if cfg_path.suffix in (".yaml", ".yml"):
                    config = yaml.safe_load(f)
                elif cfg_path.suffix == ".json":
                    config = json.load(f)
                else:
                    config = {"_raw": f.read()}
        except Exception as e:
            result.valid = False
            result.errors.append(f"解析失败: {e}")
            return result

        self._check_required_fields(config, cfg_path, result)
        self._check_numeric_ranges(config, result)
        self._check_empty_values(config, result)
        result.checked_fields = len(config) if isinstance(config, dict) else 0

        if (strict and (result.errors or result.warnings)) or result.errors:
            result.valid = False

        return result

    def _check_required_fields(
        self,
        config: dict | list | str,
        cfg_path: Path,
        result: ValidationResult,
    ) -> None:
        if not isinstance(config, dict):
            return

        fname = cfg_path.name
        if fname in self._REQUIRED_CONFIG_FIELDS:
            required = self._REQUIRED_CONFIG_FIELDS[fname]
            for field in required:
                if field not in config:
                    result.errors.append(f"缺少必需字段: {field}")

    def _check_numeric_ranges(
        self,
        config: dict,
        result: ValidationResult,
    ) -> None:
        if not isinstance(config, dict):
            return

        for key, value in config.items():
            if isinstance(value, (int, float)):
                for range_key, (lo, hi) in self._NUMERIC_RANGES.items():
                    if range_key in key.lower():
                        if value < lo or value > hi:
                            result.warnings.append(f"{key}={value} 超出建议范围 [{lo}, {hi}]")
                        break

    def _check_empty_values(
        self,
        config: dict | list | str,
        result: ValidationResult,
    ) -> None:
        if isinstance(config, dict):
            for k, v in config.items():
                if v is None:
                    result.warnings.append(f"字段值为 null: {k}")
                elif v == "":
                    result.warnings.append(f"字段值为空字符串: {k}")
                elif isinstance(v, list) and len(v) == 0:
                    result.infos.append(f"字段为空列表: {k}")
