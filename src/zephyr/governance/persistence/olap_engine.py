# 代理模块：将 zephyr.governance.persistence.olap_engine 重定向到 zephyr.governance.olap_engine
from zephyr.governance.olap_engine import (
    OLAPEngine,
    OLAPEngineError,
)

__all__ = ["OLAPEngine", "OLAPEngineError"]
