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
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

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
            log_level = os.environ["ZEPHYR_LOG_LEVEL"].strip().upper()
            _VALID_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
            if log_level not in _VALID_LEVELS:
                _LOGGER.warning(
                    "config.load_config: ZEPHYR_LOG_LEVEL=%s 无效，回退到 %s",
                    log_level, loaded.get("log_level", "INFO"),
                )
                log_level = str(loaded.get("log_level", "INFO")).upper()

    if not isinstance(dsp, tuple):
        dsp = ("akshare", "tushare")

    return AppConfig(env=env, log_level=log_level, data_source_priority=dsp)


def reload_config(current: AppConfig | None = None, env_override: bool = True) -> AppConfig:
    """热重载：按上次成功加载的路径（或默认搜索链）重新构建 ``AppConfig``。

    ``current`` 参数保留以兼容旧调用方，当前未使用（避免在 frozen dataclass 上挂载路径）。

    注意：本函数返回新实例但不通知持有旧引用的消费者。需要通知请用
    :meth:`ConfigHolder.reload`，它会调用本函数并广播给所有订阅者。
    """

    _ = current
    return load_config(config_path=_LAST_LOADED_CONFIG_PATH, env_override=env_override)


class ConfigHolder:
    """配置中心持有者 — 解决 reload_config 后消费者持有旧引用的问题。

    5.54.3 修复：AppConfig 是 frozen dataclass，reload_config 返回全新实例，
    持有旧引用的消费者（``self._config = load_config()``）无法感知变更，导致
    系统内配置不一致。ConfigHolder 维护单一当前实例 + 订阅者列表，reload 时
    广播通知所有订阅者刷新本地缓存。

    用法：
        # 消费者（启动时订阅，回调中刷新本地引用）
        ConfigHolder.subscribe(self._on_config_reload)
        cfg = ConfigHolder.get()

        # 热重载（通知所有订阅者）
        ConfigHolder.reload()
    """

    _instance: AppConfig | None = None
    _listeners: list[Callable[[AppConfig | None, AppConfig], None]] = []
    _lock = threading.Lock()

    @classmethod
    def get(cls) -> AppConfig:
        """返回当前配置实例，首次调用时自动加载。"""
        with cls._lock:
            if cls._instance is None:
                cls._instance = load_config()
            return cls._instance

    @classmethod
    def set(cls, config: AppConfig) -> None:
        """设置当前配置实例并通知订阅者（old, new）。"""
        with cls._lock:
            old = cls._instance
            cls._instance = config
            listeners = list(cls._listeners)
        cls._notify(old, config, listeners)

    @classmethod
    def subscribe(
        cls, callback: Callable[[AppConfig | None, AppConfig], None]
    ) -> None:
        """订阅配置重载事件。``callback(old, new)`` 在 set/reload 时被调用。

        回调异常被捕获并记录日志，不阻断其他订阅者。
        """
        with cls._lock:
            cls._listeners.append(callback)

    @classmethod
    def reload(cls, env_override: bool = True) -> AppConfig:
        """热重载配置并通知订阅者。返回新实例。

        内部调用 :func:`reload_config` 重建实例，再经 :meth:`set` 广播通知。
        """
        new = reload_config(current=cls._instance, env_override=env_override)
        cls.set(new)
        return new

    @classmethod
    def _notify(
        cls,
        old: AppConfig | None,
        new: AppConfig,
        listeners: list[Callable[[AppConfig | None, AppConfig], None]],
    ) -> None:
        for cb in listeners:
            try:
                cb(old, new)
            except Exception:
                _LOGGER.exception("ConfigHolder listener failed: %r", cb)

    @classmethod
    def _reset(cls) -> None:
        """测试辅助：重置持有者状态（实例 + 订阅者）。"""
        with cls._lock:
            cls._instance = None
            cls._listeners.clear()


__all__ = [
    "AppConfig",
    "ConfigHolder",
    "load_config",
    "reload_config",
]
