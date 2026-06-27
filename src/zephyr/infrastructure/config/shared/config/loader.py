# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.shared.config.loader
# [DOMAIN] D-INFRA_RUNTIME
# [DEPENDENCIES] zephyr.integration.shared_08.foundation.errors
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SHR_loader | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""
loader.py —— 共享 YAML 配置加载与 Pydantic 校验（Phase 3 新增 | 盲点 #3/#15 修复）

痛点修复：infrastructure_runtime_integration/config.py 是 STUB，contracts/registry.py
有自己的 load_config。缺少统一的 Pydantic-validated 配置加载基座。

设计对标：
  - Pydantic V2 YAML model_validate
  - Spring Boot @ConfigurationProperties + @Validated
  - K8s ConfigMap validation

设计原则：
  - YAML → dict → Pydantic model 三段式加载
  - 支持多文件 merge（base.yaml + env/dev.yaml）
  - 错误信息精准到文件+行+字段

AI 施工约定：
  - 所有模块的配置加载 MUST 通过本模块
  - 用户直接编辑 YAML，本模块负责校验
  - 配置变更后 MUST 通过 Pydantic 模型校验

SSoT: MOD-INF-016 §2.12 shared-config
Version: 0.1.0
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, TypeVar

import yaml

from zephyr.integration.shared_08.foundation.errors import ConfigError

__all__ = [
    "ConfigLoadError",
    "load_yaml_config",
    "load_yaml_config_validated",
]

logger = logging.getLogger(__name__)

T = TypeVar("T")


class ConfigLoadError(ConfigError):
    """配置加载失败——文件不存在 / YAML 解析错误 / Schema 校验失败。"""


def load_yaml_config(filepath: Path | str) -> dict[str, Any]:
    """加载 YAML 配置文件为 dict。

    Args:
        filepath: 配置文件路径。

    Returns:
        解析后的配置字典。

    Raises:
        ConfigLoadError: 文件不存在或 YAML 解析失败。
    """
    filepath = Path(filepath)

    if not filepath.exists():
        raise ConfigLoadError(
            f"Config file not found: {filepath}",
            details={"filepath": str(filepath)},
        )

    try:
        raw = filepath.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ConfigLoadError(
            f"Config file encoding error: {filepath}",
            details={"filepath": str(filepath), "error": str(exc)},
        ) from exc

    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise ConfigLoadError(
            f"YAML parse error in {filepath}",
            details={
                "filepath": str(filepath),
                "error": str(exc),
            },
        ) from exc

    if data is None:
        return {}

    if not isinstance(data, dict):
        raise ConfigLoadError(
            f"Config file must contain a mapping, got {type(data).__name__}: {filepath}",
            details={"filepath": str(filepath), "type": type(data).__name__},
        )

    return data


def load_yaml_config_validated(
    filepath: Path | str,
    model_cls: type[T],
    *,
    merge_files: list[Path | str] | None = None,
) -> T:
    """加载 YAML 配置并校验为 Pydantic 模型。

    三段式加载：
      1. 可选加载 merge_files 并合并为 base dict
      2. 加载主文件并 merge 到 base（主文件优先）
      3. model_cls.model_validate(merged_dict)

    Args:
        filepath: 主配置文件路径。
        model_cls: 目标 Pydantic BaseModel 类型。
        merge_files: 可选的待合并文件列表（先加载，优先级低于主文件）。

    Returns:
        校验后的 Pydantic 模型实例。

    Raises:
        ConfigLoadError: YAML 加载失败或 Pydantic 校验失败。
    """
    merged: dict[str, Any] = {}

    if merge_files:
        for mf in merge_files:
            try:
                base = load_yaml_config(mf)
                merged.update(base)
                logger.debug("merged config from %s", mf)
            except ConfigLoadError as exc:
                logger.warning("skip unreadable merge file %s: %s", mf, exc)

    try:
        main_data = load_yaml_config(filepath)
    except ConfigLoadError:
        raise

    merged.update(main_data)

    try:
        instance = model_cls.model_validate(merged)
    except Exception as exc:
        raise ConfigLoadError(
            f"Config validation failed for {filepath} with model {model_cls.__name__}",
            details={
                "filepath": str(filepath),
                "model": model_cls.__name__,
                "error": str(exc),
            },
        ) from exc

    logger.debug("loaded + validated config from %s → %s", filepath, model_cls.__name__)
    return instance
