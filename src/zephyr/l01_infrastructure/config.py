# ---
# layer: l01_infrastructure
# category: configuration
# status: stub
# created: "2026-05-04"
# ---
"""
ZephyrAlpha — L01 Infrastructure Layer — Configuration Management
模块: Configuration Management | ID: l01-config | Priority: P0
职责: 配置加载与环境管理；跨平面共享配置（risk_params.yaml 等），自身属 Warm
接口契约: CTR-P1-010 (producer)
"""

from dataclasses import dataclass

@dataclass(frozen=True)
class AppConfig:
    """应用配置数据类。

    支持从 YAML 文件加载 + 环境变量覆盖 + 热重载。
    """

    env: str = "dev"
    log_level: str = "INFO"
    data_source_priority: list = None

    def __post_init__(self):
        object.__setattr__(self, "data_source_priority", self.data_source_priority or ["akshare", "tushare"])

def load_config(config_path: str | None = None, env_override: bool = True) -> AppConfig:
    """[STUB — Phase 2 实现] 加载应用配置。"""
    raise NotImplementedError("load_config: STUB — Phase 2 实现")

def reload_config(current: AppConfig) -> AppConfig:
    """[STUB — Phase 2 实现] 热重载配置。"""
    raise NotImplementedError("reload_config: STUB — Phase 2 实现")
