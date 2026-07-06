# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.policy_registry
# [DOMAIN] D_DATA
# [DEPENDENCIES]
# [CONSUMERS] zephyr.data.scheduler, zephyr.data.provider_base
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 策略 yaml 是真源，DEFAULT_POLICIES 是 fallback；maybe_reload 热更新
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] get_policy 未知源返回默认策略，不抛异常
# [TESTS] tests/zephyr/data/test_policy_registry.py
# [A_module] module_id=MOD-L00-004-policy_registry | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""per-source 调用策略注册表（MOD-L00-004 §5）。

每个数据源有自己的限流/重试/反爬/登录刷新策略，集中管理、yaml 热更新。

策略参数来源：data_source_operation_manual.md（MOD-L00-002）中每个数据源的限流/防爬/登录方式描述，
已固化为 config/policies.yaml（见蓝图 §5.2 跨源策略矩阵）。

核心组件：
- SourcePolicy：单数据源策略（RPM/并发/重试/退避/反爬/登录刷新）
- PolicyRegistry：策略注册表，从 yaml 加载，支持热更新
"""
from __future__ import annotations

import logging
import os
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

log = logging.getLogger(__name__)


# ============== 策略数据类 ==============

@dataclass
class SourcePolicy:
    """单数据源调用策略。

    Attributes:
        rpm: 每分钟最大请求数（0=不限或配额制，如 iFind）
        concurrency: 最大并发数（1=串行）
        min_interval_sec: 两次调用最小间隔秒数（RPM 的补充，默认 60/rpm）
        max_retries: 最大重试次数（0=不重试）
        backoff: 退避模式 "exponential"/"fixed"/"jittered"
        initial_wait_sec: 首次重试等待秒数
        retry_on: 重试触发的错误码/异常名列表（如 ["-201","TimeoutError","ConnectionError"]）
        use_proxy: 是否走代理
        proxy: 代理地址（如 "http://127.0.0.1:7890"）
        disconnect_vpn: 是否须断开 VPN（AKShare 爬国内网站，VPN 导致海外 IP 被拒）
        user_agent: 自定义 User-Agent
        respect_robots_txt: 是否遵守 robots.txt
        session_ttl_sec: 登录会话有效期秒数（0=永久，超时自动重登）
        relogin_on_auth_error: 401/登录失效时是否自动重登
        extra: 数据源专属配置（如 iFind 月度配额监控）
    """
    rpm: int = 0
    concurrency: int = 1
    min_interval_sec: float = 0.0
    max_retries: int = 3
    backoff: str = "exponential"
    initial_wait_sec: float = 2.0
    retry_on: list = field(default_factory=list)
    use_proxy: bool = False
    proxy: Optional[str] = None
    disconnect_vpn: bool = False
    user_agent: Optional[str] = None
    respect_robots_txt: bool = True
    session_ttl_sec: int = 0
    relogin_on_auth_error: bool = False
    enabled: bool = True  # 熔断开关：CLI pause <source> 置 False，resume 置 True
    extra: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, d: dict) -> "SourcePolicy":
        """从字典构造（yaml 加载后）。忽略未知字段。"""
        known = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in d.items() if k in known})


# ============== 默认策略（跨源矩阵 §5.2） ==============

# 这些默认值对应蓝图 §5.2 跨源策略矩阵，可作为 policies.yaml 缺失时的兜底
DEFAULT_POLICIES: dict[str, dict] = {
    "ifind": {
        "rpm": 0, "concurrency": 1, "max_retries": 3, "backoff": "exponential",
        "initial_wait_sec": 2.0, "retry_on": ["-201", "TimeoutError", "ConnectionError"],
        "session_ttl_sec": 86400, "relogin_on_auth_error": True,
        "extra": {"monthly_quota_alert": True, "quota_error_codes": ["-4318", "-4309"]},
    },
    "miniqmt": {
        "rpm": 0, "concurrency": 1, "max_retries": 3, "backoff": "fixed",
        "initial_wait_sec": 1.0, "retry_on": ["TimeoutError", "ConnectionError"],
        "session_ttl_sec": 0, "relogin_on_auth_error": True,
        "extra": {"requires_process": "XtMiniQmt.exe"},
    },
    "akshare": {
        "rpm": 60, "concurrency": 4, "max_retries": 5, "backoff": "jittered",
        "initial_wait_sec": 2.0, "retry_on": ["HTTPError", "JSONDecodeError", "ConnectionError"],
        "disconnect_vpn": True,
        "extra": {"dongfang_caizhang_skip_after": 3},
    },
    "baostock": {
        "rpm": 60, "concurrency": 8, "max_retries": 3, "backoff": "fixed",
        "initial_wait_sec": 2.0, "retry_on": ["TimeoutError", "ConnectionError", "BaoStockError"],
        "session_ttl_sec": 3600, "relogin_on_auth_error": True,
        "extra": {"thread_local_login": True, "data_lag_days": 7},
    },
    "tushare": {
        "rpm": 200, "concurrency": 2, "max_retries": 3, "backoff": "exponential",
        "initial_wait_sec": 1.0, "retry_on": ["TPMaxQueryLimitError", "ConnectionError"],
        "session_ttl_sec": 0, "relogin_on_auth_error": False,
        "extra": {"points_alert_threshold": 2000},
    },
    "tickflow": {
        "rpm": 60, "concurrency": 2, "max_retries": 3, "backoff": "jittered",
        "initial_wait_sec": 1.0, "retry_on": ["HTTPError", "ConnectionError"],
    },
    "tdx": {
        "rpm": 0, "concurrency": 1, "max_retries": 3, "backoff": "fixed",
        "initial_wait_sec": 0.5, "retry_on": ["ConnectionError", "TimeoutError"],
        "extra": {"bestip": True},
    },
    "rss": {
        "rpm": 0, "concurrency": 1, "max_retries": 3, "backoff": "exponential",
        "initial_wait_sec": 5.0, "retry_on": ["SSLError", "ConnectionError", "HTTPError"],
        "respect_robots_txt": True,
    },
}


# ============== 策略注册表 ==============

class PolicyRegistry:
    """策略注册表：从 yaml 加载 per-source 策略，支持热更新。

    用法：
        registry = PolicyRegistry()
        registry.load_yaml("config/policies.yaml")  # 可选，覆盖默认
        policy = registry.get_policy("ifind")
    """

    def __init__(self):
        self._policies: dict[str, SourcePolicy] = {}
        self._lock = threading.RLock()
        self._last_reload: float = 0.0
        self._yaml_path: Optional[Path] = None
        self._yaml_mtime: float = 0.0
        # 加载默认策略
        self._load_defaults()

    def _load_defaults(self) -> None:
        """加载 DEFAULT_POLICIES。"""
        with self._lock:
            for src, d in DEFAULT_POLICIES.items():
                self._policies[src] = SourcePolicy.from_dict(d)

    def load_yaml(self, path: str | Path) -> None:
        """从 yaml 加载策略，覆盖默认值。

        yaml 格式见蓝图 §9.2 config/policies.yaml。
        """
        import yaml
        p = Path(path)
        if not p.exists():
            log.warning(f"策略 yaml 不存在，使用默认策略: {p}")
            return
        self._yaml_path = p
        with open(p, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        with self._lock:
            for src, d in data.items():
                if isinstance(d, dict):
                    self._policies[src] = SourcePolicy.from_dict(d)
        self._yaml_mtime = p.stat().st_mtime
        self._last_reload = time.time()
        log.info(f"已加载策略 yaml: {p}（{len(data)} 个数据源）")

    def maybe_reload(self, force: bool = False) -> bool:
        """检查 yaml 是否变更，变更则重载。返回是否重载。

        调度器可每 60 秒调用一次实现热更新。
        """
        if not self._yaml_path:
            return False
        try:
            mtime = self._yaml_path.stat().st_mtime
        except OSError:
            return False
        if force or mtime != self._yaml_mtime:
            self.load_yaml(self._yaml_path)
            return True
        return False

    def get_policy(self, source: str) -> SourcePolicy:
        """获取某数据源的策略。未注册的返回默认保守策略。"""
        with self._lock:
            if source in self._policies:
                return self._policies[source]
            log.warning(f"数据源 '{source}' 无注册策略，使用保守默认")
            return SourcePolicy()  # 全默认值（rpm=0, retries=3, ...）

    def register(self, source: str, policy: SourcePolicy) -> None:
        """编程式注册/覆盖策略（测试用）。"""
        with self._lock:
            self._policies[source] = policy

    def list_sources(self) -> list[str]:
        """列出所有已注册数据源。"""
        with self._lock:
            return sorted(self._policies.keys())

    @property
    def last_reload_at(self) -> float:
        return self._last_reload


# ============== 模块级单例 ==============

_registry: Optional[PolicyRegistry] = None
_registry_lock = threading.Lock()


def get_registry() -> PolicyRegistry:
    """获取全局 PolicyRegistry 单例。首次调用时尝试加载 config/policies.yaml。"""
    global _registry
    if _registry is None:
        with _registry_lock:
            if _registry is None:
                _registry = PolicyRegistry()
                # 尝试加载默认路径
                yaml_path = Path(__file__).parent / "config" / "policies.yaml"
                if yaml_path.exists():
                    _registry.load_yaml(yaml_path)
    return _registry
