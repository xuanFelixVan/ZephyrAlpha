# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.security.secret_rotation
# [DOMAIN] D_OPS
# [DEPENDENCIES] zephyr.shared.security.secrets (SECRET_INDICATOR_PATTERNS, configure_secret_rotation)
# [CONSUMERS] zephyr.__init__._deferred_bootstrap (auto_configure)
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SEC_secret_rotation | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Secret Rotation — v0.14.0 R189

Blindspot: API keys/secrets never rotated; leaked credentials valid indefinitely.
Risk: R189 — Compromised secret grants permanent access; no automated rotation.

Mitigation: Secret lifecycle management with automated rotation scheduling.
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field


@dataclass
class SecretEntry:
    secret_id: str
    service_name: str
    last_rotated: float
    rotation_interval_days: int = 90
    current_hash: str = ""

    @property
    def days_since_rotation(self) -> float:
        return (time.time() - self.last_rotated) / 86400.0

    @property
    def needs_rotation(self) -> bool:
        return self.days_since_rotation > self.rotation_interval_days


@dataclass
class SecretRotation:
    secrets: dict[str, SecretEntry] = field(default_factory=dict)

    def register(self, secret_id: str, service_name: str, interval_days: int = 90) -> SecretEntry:
        entry = SecretEntry(
            secret_id=secret_id,
            service_name=service_name,
            last_rotated=time.time(),
            rotation_interval_days=interval_days,
        )
        self.secrets[secret_id] = entry
        return entry

    def rotate(self, secret_id: str) -> str:
        entry = self.secrets.get(secret_id)
        if entry is None:
            raise KeyError(f"Secret {secret_id} not registered")
        new_secret = secrets.token_hex(32)
        entry.current_hash = new_secret
        entry.last_rotated = time.time()
        return new_secret

    def pending_rotations(self) -> list[str]:
        return [sid for sid, e in self.secrets.items() if e.needs_rotation]


# ============ 自动接入 SecretProvider（§5.17.14 治本） ============
# 痛点：configure_secret_rotation 定义了但无调用者，_rotation_registry 永远 None，
# 轮换检查空转。本函数在应用启动时自动扫描 os.environ 中的密钥变量并注册，
# 然后注入到 SecretProvider——全自动，无需手工维护密钥列表。
#
# 设计：
#   - 扫描规则复用 SECRET_INDICATOR_PATTERNS（secrets.py 已有真源），不硬编码密钥列表
#   - 依赖方向正确：trading/ -> shared/（单向）
#   - 放在此模块（trading/）而非 secrets.py（shared/），避免 shared->trading 循环依赖


def auto_configure(interval_days: int = 90) -> int:
    """自动扫描 os.environ 中的密钥变量，注册到 SecretRotation 并注入 SecretProvider。

    扫描规则：变量名（大写）包含 SECRET_INDICATOR_PATTERNS 中的任意模式
    （KEY/TOKEN/SECRET/PASSWORD/PASSWD/PWD/CREDENTIAL）即视为密钥变量。

    在 zephyr/__init__.py 的 _deferred_bootstrap 中自动调用（后台线程，不阻塞冷启动）。
    .env 文件已在 _load_dotenv() 中加载到 os.environ，故扫描覆盖全部已配置密钥。

    Args:
        interval_days: 默认轮换间隔天数（90天）。

    Returns:
        注册的密钥数量。
    """
    import os

    from zephyr.shared.security.secrets import SECRET_INDICATOR_PATTERNS, configure_secret_rotation

    registry = SecretRotation()
    for key in os.environ:
        key_upper = key.upper()
        if any(pattern in key_upper for pattern in SECRET_INDICATOR_PATTERNS):
            registry.register(key, service_name=key, interval_days=interval_days)
    configure_secret_rotation(registry)
    return len(registry.secrets)
