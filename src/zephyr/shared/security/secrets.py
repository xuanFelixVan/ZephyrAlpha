# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.security.secrets
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] intelligence.model_profiling.deepseek_v4_chat, intelligence.model_profiling.capability_passport, infrastructure.pipeline.llm_gateway, infrastructure.asset_inventory.telemetry, integration.local_model.deepseek_chat, infrastructure.rollback.rollback_integration, governance.depgraph_schema, trading.feedback_loop.security.secret_rotation, security.llm_defense.llm_security.patterns.secrets(re-export)
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SEC_secrets | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

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

from typing import Final
import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "SECRET_INDICATOR_PATTERNS",
    "DotEnvSecretProvider",
    "EnvSecretProvider",
    "SecretProvider",
    "SecretsError",
    "configure_secret_rotation",
    "get_required_secret",
    "get_secret",
    "get_secret_or_default",
    "get_secret_from_file",
    "get_secret_from_file_or_default",
    "sanitize_secret",
]

logger = logging.getLogger(__name__)


# ============ Secret Rotation 集成（Phase 4 新增 | §5.17.14 修复） ============
# 痛点：secret_rotation 模块（trading/feedback_loop/security/）独立维护轮换
# 调度，但 SecretProvider 读取密钥时无感知——已过期密钥仍被正常读取，
# 轮换告警形同虚设。现通过 configure_secret_rotation() 注入 registry，
# 读取时前置 needs_rotation 检查（warn 不阻断）。
#
# 设计：避免循环依赖——shared/ 不 import trading/，registry 通过鸭子类型注入，
# TYPE_CHECKING 仅用于类型提示。

if TYPE_CHECKING:
    from zephyr.trading.feedback_loop.security.secret_rotation import SecretRotation

_rotation_registry: "SecretRotation | None" = None


def configure_secret_rotation(registry: "SecretRotation | None") -> None:
    """注入 SecretRotation registry（§5.17.14 修复）。

    注入后，所有 get_secret* 读取密钥时会前置检查 needs_rotation，
    过期则记录 WARNING 日志（不阻断读取）。

    Args:
        registry: SecretRotation 实例，或 None（关闭检查）。
    """
    global _rotation_registry
    _rotation_registry = registry
    if registry is not None:
        logger.info("SecretRotation registry injected: %d secrets tracked", len(registry.secrets))


def _check_rotation(key: str) -> None:
    """检查密钥是否需要轮换（warn 不阻断，§5.17.14）。

    Args:
        key: 密钥名。
    """
    if _rotation_registry is None:
        return
    entry = _rotation_registry.secrets.get(key)
    if entry is not None and entry.needs_rotation:
        logger.warning(
            "secret '%s' (service=%s) needs rotation: %.1f days since last rotation (interval=%d days)",
            key,
            entry.service_name,
            entry.days_since_rotation,
            entry.rotation_interval_days,
        )


class SecretsError(ZephyrBaseError):
    """Secrets 读取失败——key 不存在、backend 不可达、权限拒绝。"""
    error_code = "ZA-SH-0016"


SECRET_INDICATOR_PATTERNS: Final[tuple[str, ...]] = (
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


def _parse_env_file(path: Path) -> dict[str, str]:
    """解析 .env 文件，返回 KEY=VALUE 字典（去引号，跳注释/空行）。

    .env 文件解析唯一真源——DotEnvSecretProvider._load_env_file 和
    get_secret_from_file 共用，避免解析逻辑重复（§5.17.10 真源统一）。
    """
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]
            values[key] = value
    return values


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
        _check_rotation(key)
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

        self._values = _parse_env_file(self._env_file)

        self._loaded = True
        logger.info("loaded %d secrets from '%s'", len(self._values), self._env_file)

    async def get_secret(self, key: str) -> str:
        _check_rotation(key)
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


# ============ 同步便捷函数（脚本场景用） ============
# 痛点：SecretProvider 是 async 接口，对同步脚本（diagnose_*.py / 测试脚本）
# 包 asyncio.run() 太重。提供同步入口，直接读 os.environ——
# .env 文件已由 zephyr/__init__.py._load_dotenv() 在包导入时自动加载到
# os.environ，因此所有同步代码直接调用本节函数即可，无需重复解析 .env。
#
# AI 施工约定（同 SSoT §2.11）：脚本中读取 API key / token / password
# MUST 调用本节函数——禁止裸 os.getenv。


def get_secret(key: str) -> str:
    """同步读取 secret（从 os.environ）。

    .env 文件已由 zephyr 包导入时自动加载到 os.environ，
    因此同步代码直接调用本函数即可。

    Args:
        key: 环境变量名（如 "DEEPSEEK_API_KEY"）。

    Returns:
        Secret 值（明文）。

    Raises:
        SecretsError: 如果 key 未设置。
    """
    _check_rotation(key)
    value = os.environ.get(key)
    if value is None:
        raise SecretsError(
            f"secret '{key}' not found in environment variables",
            details={"key": key, "hint": f"请在 .env 文件或环境变量中设置 {key}"},
        )
    return value


def get_secret_or_default(key: str, default: str = "") -> str:
    """同步读取 secret，缺失时返回默认值（不抛异常）。

    Args:
        key: 环境变量名。
        default: 默认值。

    Returns:
        Secret 值或默认值。
    """
    _check_rotation(key)
    return os.environ.get(key, default)


def get_required_secret(key: str) -> str:
    """同步读取必需的 secret，缺失或空即 fail-fast。

    语义化便捷函数——用于脚本启动时校验必需的 API key。
    与 get_secret 的区别：空字符串同样视为缺失（业务语义，
    空 key 无法用于 API 调用）。

    Args:
        key: 环境变量名。

    Returns:
        Secret 值（明文，且非空）。

    Raises:
        SecretsError: 如果 key 未设置或为空字符串。
    """
    _check_rotation(key)
    value = os.environ.get(key)
    if not value:
        raise SecretsError(
            f"required secret '{key}' is not set",
            details={"key": key, "hint": f"请在 .env 文件中添加: {key}=你的密钥"},
        )
    return value


# ============ 文件级 secret 读取（Phase 3 新增 | §5.34.8 修复） ============
# 痛点：config/.env.postgres 等非默认位置的密钥文件无法通过 get_secret() 读取
# （get_secret 仅读 os.environ，而 .env.postgres 不在包导入时自动加载范围）。
# 提供文件级读取入口，优先级：os.environ > 指定文件 > 抛异常。


def get_secret_from_file(key: str, env_file: str | Path) -> str:
    """同步从指定 .env 文件读取 secret（不依赖 os.environ 默认加载）。

    用于读取非默认位置的密钥文件（如 config/.env.postgres）。
    优先级：os.environ（最高） > 指定文件 > 抛异常。

    Args:
        key: 环境变量名。
        env_file: .env 文件路径。

    Returns:
        Secret 值（明文）。

    Raises:
        SecretsError: 如果 key 不存在或文件不可达。
    """
    # 1. 先查 os.environ（允许环境变量覆盖文件）
    _check_rotation(key)
    value = os.environ.get(key)
    if value is not None:
        return value
    # 2. 解析指定文件
    env_path = Path(env_file)
    if not env_path.is_file():
        raise SecretsError(
            f"env file not found: {env_path}",
            details={"key": key, "env_file": str(env_path)},
        )
    values = _parse_env_file(env_path)
    if key not in values:
        raise SecretsError(
            f"secret '{key}' not found in {env_path}",
            details={"key": key, "env_file": str(env_path)},
        )
    return values[key]


def get_secret_from_file_or_default(key: str, env_file: str | Path, default: str = "") -> str:
    """同步从指定文件读取 secret，缺失返回默认值（不抛异常）。"""
    try:
        return get_secret_from_file(key, env_file)
    except SecretsError:
        return default
