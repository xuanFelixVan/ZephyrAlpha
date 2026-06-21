# [A_module] module_id=MOD-SEC_secrets | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md

# [MODULE] zephyr.integration.shared_08.security.secrets

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
secrets.py —— Secrets 管理抽象（Phase 7 新增 | 盲点 B12 修复）

痛点修复：API key / token / 数据库密码散落在环境变量中——
  1. AI 在 10 个模块里写 10 种 os.getenv("SOME_KEY") → 不可审计
  2. 没有统一的 SecretProvider 接口——无法切换 secrets backend
  3. 没有 sanitization——AI 可能把 API key 打进日志

设计对标：
  - HashiCorp Vault（集中式 secrets management）
  - K8s Secrets（注入 env / volume）
  - 12-Factor App §III（Config stored in environment variables）
  - Stripe Restricted API Keys（最小权限原则）

设计原则：
  - SecretProvider 只是一个 async 读接口——不关心后端是 env / vault / AWS Parameter Store
  - 所有 secret 值在日志中必须 sanitize（显示为 "***REDACTED*** (len=N)"）
  - 零依赖第三方库——默认实现仅使用 os.environ

AI 施工约定：
  - 任何 API key / token / password MUST 通过 SecretProvider 读取——禁止裸 os.getenv
  - 新增 secrets backend 时 MUST 实现 SecretProvider 接口
  - 禁止在任何日志 / print / 错误消息中输出 secret 值

SSoT: MOD-INF-016 §2.11 shared-secrets
Version: 0.1.0
"""

from __future__ import annotations


import logging
import os
from pathlib import Path
from typing import Protocol, runtime_checkable

from zephyr.integration.shared_08.foundation.errors import ZephyrBaseError

__all__ = [
    "SecretsError",
    "SecretProvider",
    "EnvSecretProvider",
    "DotEnvSecretProvider",
    "sanitize_secret",
    "SECRET_INDICATOR_PATTERNS",
]

logger = logging.getLogger(__name__)


class SecretsError(ZephyrBaseError):
    """Secrets 读取失败——key 不存在、backend 不可达、权限拒绝。"""


SECRET_INDICATOR_PATTERNS: tuple[str, ...] = (
    "KEY",
    "TOKEN",
    "SECRET",
    "PASSWORD",
    "PASSWD",
    "PWD",
    "CREDENTIAL",
)


def sanitize_secret(name: str, value: str) -> str:
    """安全脱敏——仅暴露长度，绝不暴露原始值。

    Args:
        name: Secret 名称（用于日志上下文）。
        value: Secret 原始值。

    Returns:
        脱敏字符串——例 "***REDACTED*** (len=32)"
    """
    return f"***REDACTED*** (len={len(value)})"


@runtime_checkable
class SecretProvider(Protocol):
    """Secret 读取接口——async + 无依赖。

    任何 secrets backend（env / vault / AWS Parameter Store / K8s Secrets）
    只需实现 get_secret() 即可替换。

    Usage::

        provider = EnvSecretProvider()
        api_key = await provider.get_secret("DEEPSEEK_API_KEY")
    """

    async def get_secret(self, key: str) -> str:
        """读取一个 secret。

        Args:
            key: Secret 名称（如 "DEEPSEEK_API_KEY"）。

        Returns:
            Secret 值（明文）。

        Raises:
            SecretsError: 如果 key 不存在或 backend 不可达。
        """
        ...

    async def get_secret_or_default(self, key: str, default: str = "") -> str:
        """读取 secret，失败时返回默认值（不抛异常）。

        Args:
            key: Secret 名称。
            default: 默认值。

        Returns:
            Secret 值或默认值。
        """
        ...


class EnvSecretProvider:
    """从 os.environ 读取 secrets——默认实现。

    Usage::

        provider = EnvSecretProvider()
        key = await provider.get_secret("OPENAI_API_KEY")
    """

    async def get_secret(self, key: str) -> str:
        value = os.environ.get(key)
        if value is None:
            raise SecretsError(
                f"secret '{key}' not found in environment variables",
                details={"key": key},
            )
        logger.debug("secret '%s' loaded: %s", key, sanitize_secret(key, value))
        return value

    async def get_secret_or_default(self, key: str, default: str = "") -> str:
        try:
            return await self.get_secret(key)
        except SecretsError:
            logger.debug("secret '%s' not found, using default", key)
            return default


class DotEnvSecretProvider:
    """从 .env 文件读取 secrets——本地开发用。

    优先级：环境变量（最高） > .env 文件 > default

    Usage::

        provider = DotEnvSecretProvider(".env")
        key = await provider.get_secret("DATABASE_URL")
    """

    def __init__(self, env_file: str | Path = ".env") -> None:
        self._env_file = Path(env_file)
        self._values: dict[str, str] = {}
        self._loaded = False

    def _load_env_file(self) -> None:
        if self._loaded:
            return
        if not self._env_file.is_file():
            logger.info("env file '%s' not found, skipping", self._env_file)
            self._loaded = True
            return

        with open(self._env_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip()
                if value.startswith('"') and value.endswith('"') or value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                self._values[key] = value

        self._loaded = True
        logger.info("loaded %d secrets from '%s'", len(self._values), self._env_file)

    async def get_secret(self, key: str) -> str:
        self._load_env_file()

        env_value = os.environ.get(key)
        if env_value is not None:
            logger.debug("secret '%s' loaded from env (overrides .env)", key)
            return env_value

        value = self._values.get(key)
        if value is None:
            raise SecretsError(
                f"secret '{key}' not found in env or '{self._env_file}'",
                details={"key": key, "env_file": str(self._env_file)},
            )
        logger.debug("secret '%s' loaded from '%s': %s", key, self._env_file, sanitize_secret(key, value))
        return value

    async def get_secret_or_default(self, key: str, default: str = "") -> str:
        try:
            return await self.get_secret(key)
        except SecretsError:
            logger.debug("secret '%s' not found, using default", key)
            return default
