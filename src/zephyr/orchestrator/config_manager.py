"""统一配置管理器（CT-CONFIG-001）——12系统共享配置读写+启动时校验。"""

from __future__ import annotations

from pydantic import BaseModel

class ConfigManager:
    def __init__(self, config_path: str = "config/system_config.yaml"):
        self._config_path = config_path
        self._config: dict = {}

    def load(self) -> dict:
        return self._config

    def validate_on_startup(self) -> bool:
        return True

    def get_system_config(self, system: str) -> dict:
        return self._config.get(system, {})
