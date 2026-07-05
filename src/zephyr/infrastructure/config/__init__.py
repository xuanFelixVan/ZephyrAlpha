# [A_module] module_id=MOD-INF_config | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md

# [MODULE] zephyr.infrastructure.config

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]
# [TTL] permanent

# ---
# domain: infra_ops
# category: configuration
# status: active
# created: "2026-05-04"
# ---
"""
ZephyrAlpha — 基础设施 Infrastructure Layer — Configuration Management
模块: Configuration Management | ID: l01-config | Priority: P0
职责: 配置加载与环境管理；跨平面共享配置（risk_params.yaml 等），自身属 Warm
接口契约: CTR-P1-010 (producer)
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_LOGGER = logging.getLogger(__name__)

_LAST_LOADED_CONFIG_PATH: str | None = None

DEFAULT_CONFIG_FILENAMES: tuple[str, ...] = ("config/zephyr_app.yaml", "config/app.yaml")


@dataclass(frozen=True)
class AppConfig:
    """应用配置数据类。

    可从 YAML 文件加载，并由环境变量覆盖（见 ``load_config``）。
    """

    env: str = "dev"
    log_level: str = "INFO"
    data_source_priority: tuple[str, ...] = ("akshare", "tushare")

    def __post_init__(self) -> None:
        if isinstance(self.data_source_priority, list):
            object.__setattr__(self, "data_source_priority", tuple(self.data_source_priority))


def _deep_merge_lists(val: Any) -> tuple[str, ...] | Any:
    if isinstance(val, list):
        return tuple(str(x) for x in val)
    return val


def load_config(config_path: str | None = None, env_override: bool = True) -> AppConfig:
    """加载应用配置。

    解析顺序
    --------
    1. 显式 ``config_path``（存在且为文件）。
    2. 环境变量 ``ZEPHYR_APP_CONFIG_PATH``。
    3. CWD 下 ``config/zephyr_app.yaml``、``config/app.yaml``。
    未找到YAML时返回默认 ``AppConfig``，并仅在此时打 warning。

    ``env_override`` 为 True 时：可用 ``ZEPHYR_ENV``、``ZEPHYR_LOG_LEVEL`` 覆盖 YAML。
    """

    global _LAST_LOADED_CONFIG_PATH

    yaml_path: Path | None = None
    checked: list[str] = []

    if config_path:
        p = Path(config_path)
        checked.append(str(p.resolve()))
        if p.is_file():
            yaml_path = p

    if yaml_path is None:
        env_p = os.environ.get("ZEPHYR_APP_CONFIG_PATH", "").strip()
        if env_p:
            pe = Path(env_p)
            checked.append(str(pe.resolve()))
            if pe.is_file():
                yaml_path = pe

    if yaml_path is None:
        for name in DEFAULT_CONFIG_FILENAMES:
            p = Path(name)
            checked.append(str(p.resolve()))
            if p.is_file():
                yaml_path = p
                break

    if yaml_path is None:
        _LAST_LOADED_CONFIG_PATH = None
        _LOGGER.warning(
            "config.load_config: 未找到 YAML（已检查 %s），使用默认 AppConfig。",
            "; ".join(checked) if checked else "无候选路径",
        )
        return AppConfig()

    try:
        import yaml
    except ImportError as exc:  # pragma: no cover
        _LOGGER.error("config.load_config: 需要 PyYAML：%s", exc)
        return AppConfig()

    raw_text = yaml_path.read_text(encoding="utf-8")
    loaded = yaml.safe_load(raw_text) or {}
    if not isinstance(loaded, dict):
        _LOGGER.warning("config.load_config: YAML 根节点须为 mapping，回退默认 AppConfig。")
        return AppConfig()

    _LAST_LOADED_CONFIG_PATH = str(yaml_path.resolve())

    env = str(loaded.get("env", "dev"))
    log_level = str(loaded.get("log_level", "INFO"))
    dsp_any = loaded.get("data_source_priority", ["akshare", "tushare"])
    dsp = _deep_merge_lists(dsp_any)

    if env_override:
        if os.environ.get("ZEPHYR_ENV"):
            env = os.environ["ZEPHYR_ENV"].strip()
        if os.environ.get("ZEPHYR_LOG_LEVEL"):
            log_level = os.environ["ZEPHYR_LOG_LEVEL"].strip()

    if not isinstance(dsp, tuple):
        dsp = ("akshare", "tushare")

    return AppConfig(env=env, log_level=log_level, data_source_priority=dsp)


def reload_config(current: AppConfig | None = None, env_override: bool = True) -> AppConfig:
    """热重载：按上次成功加载的路径（或默认搜索链）重新构建 ``AppConfig``。

    ``current`` 参数保留以兼容旧调用方，当前未使用（避免在 frozen dataclass 上挂载路径）。
    """

    _ = current
    return load_config(config_path=_LAST_LOADED_CONFIG_PATH, env_override=env_override)


__all__ = [
    "AppConfig",
    "load_config",
    "reload_config",
]
