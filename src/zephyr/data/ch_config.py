# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.ch_config
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.shared.security.secrets; zephyr.shared.io.paths
# [CONSUMERS] zephyr.data.ch_writer; zephyr.data.scheduler; zephyr.data.cli; zephyr.infrastructure.database_service
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] CH 连接配置唯一真源为 config/.env.clickhouse; 禁止任何入口硬编码 IP 默认值; ensure_ch_env_loaded 幂等; load_ch_config 读不到配置抛 CHConfigError(fail-closed)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ensure_ch_env_loaded 文件不存在->log warning+不抛; load_ch_config 配置缺失->抛 CHConfigError
# [TESTS] tests/zephyr/data/test_ch_config.py
# [A_module] module_id=MOD-GOV-ch_config | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""ClickHouse 连接配置单真源加载器（裁定 #ARCH-CH-017 / #ARCH-CH-019）。

背景：
    Hyper-V 迁移前，ch_writer.py 用 `os.environ.get("CLICKHOUSE_HOST", "172.24.30.100")`
    硬编码默认值，database_service.py 用 `"localhost"` 默认值，两者不一致且都不主动
    加载 config/.env.clickhouse。scheduler.main() / cli._load_dotenv() 也不加载该文件。
    当前能工作纯属硬编码默认值巧合等于 .env.clickhouse 的值，CH 再迁移一次就会暴露。

治本原则（裁定 #ARCH-CH-017）：
    - config/.env.clickhouse 是 CH 连接配置的唯一真源
    - 所有 CH 连接入口必须主动读取该文件，禁止用硬编码 IP 作为默认值
    - 启动入口必须显式加载 .env.clickhouse 到 os.environ
    - 读不到配置 fail-closed（抛异常），而非静默用 localhost/172.24.30.100

公共接口：
    - ensure_ch_env_loaded(): 将 .env.clickhouse 加载到 os.environ（幂等）
    - load_ch_config(): 返回 CH 连接配置字典，读不到抛 CHConfigError
"""

from __future__ import annotations

import logging
import os
import threading
from pathlib import Path

from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.security.secrets import get_service_secret

log = logging.getLogger(__name__)

# CH 连接配置文件路径（唯一真源）
_CH_ENV_PATH: Path = REPO_ROOT / "config" / ".env.clickhouse"

# 必须存在的配置键
_REQUIRED_KEYS = (
    "CLICKHOUSE_HOST",
    "CLICKHOUSE_PORT",
    "CLICKHOUSE_HTTP_PORT",
    "CLICKHOUSE_USER",
    "CLICKHOUSE_PASSWORD",
    "CLICKHOUSE_DATABASE",
)

# 幂等加载标志（避免重复解析文件）
_loaded: bool = False
_load_lock = threading.Lock()


class CHConfigError(RuntimeError):
    """CH 配置缺失或不可读时抛出（fail-closed，禁止静默用默认值）。"""


def ensure_ch_env_loaded() -> None:
    """将 config/.env.clickhouse 加载到 os.environ（幂等）。

    优先级：已有 os.environ 不覆盖（允许环境变量显式 override）。
    文件不存在时 log warning 但不抛异常（开发环境友好），
    后续 load_ch_config() 会因配置缺失抛 CHConfigError。

    幂等：模块级 _loaded 标志保证只解析一次文件。
    """
    global _loaded
    if _loaded:
        return
    with _load_lock:
        if _loaded:
            return
        if not _CH_ENV_PATH.is_file():
            log.warning("CH 配置文件不存在: %s（CH 连接将失败）", _CH_ENV_PATH)
            _loaded = True
            return
        try:
            for line in _CH_ENV_PATH.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                # 不覆盖已有环境变量（允许显式 override）
                os.environ.setdefault(k, v)
            log.info("CH 配置已加载: %s", _CH_ENV_PATH)
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            log.error("CH 配置加载失败 %s: %s", _CH_ENV_PATH, e)
        finally:
            _loaded = True


def load_ch_config() -> dict[str, str]:
    """返回 CH 连接配置字典。

    优先级：os.environ > config/.env.clickhouse > 抛 CHConfigError。
    禁止任何默认 IP 值（裁定 #ARCH-CH-017）。

    Returns:
        包含 host/port/http_port/user/password/database 的字典。

    Raises:
        CHConfigError: 如果 CLICKHOUSE_HOST 配置缺失（fail-closed）。
    """
    ensure_ch_env_loaded()
    # host 是必须的，缺失则 fail-closed（禁止默认 localhost/172.24.30.100）
    host = get_service_secret("CLICKHOUSE_HOST", "clickhouse", required=False)
    if not host:
        raise CHConfigError(
            f"CLICKHOUSE_HOST 未配置：os.environ 未设置且 {_CH_ENV_PATH} 不含该键。"
            f"请创建 config/.env.clickhouse 并填写 CLICKHOUSE_HOST=<Hyper-V VM IP>。"
        )
    return {
        "host": host,
        "port": get_service_secret("CLICKHOUSE_PORT", "clickhouse", required=False) or "9000",
        "http_port": get_service_secret("CLICKHOUSE_HTTP_PORT", "clickhouse", required=False) or "8123",
        "user": get_service_secret("CLICKHOUSE_USER", "clickhouse", required=False) or "default",
        "password": get_service_secret("CLICKHOUSE_PASSWORD", "clickhouse", required=False) or "",
        "database": get_service_secret("CLICKHOUSE_DATABASE", "clickhouse", required=False) or "c1_market",
    }


def get_ch_env_path() -> Path:
    """返回 CH 配置文件路径（供测试/诊断使用）。"""
    return _CH_ENV_PATH


def load_ch_reader_config() -> dict[str, str]:
    """返回 CH 只读账号配置（audit 9.4 RBAC 治本 #ARCH-CH-027）。

    优先使用 CLICKHOUSE_READER_USER/PASSWORD，未配置时回退到 CLICKHOUSE_USER/PASSWORD。
    用于 database_service.get_clickhouse_conn() 等只读查询场景，
    确保应用层只读连接使用 DB 级 SELECT-only 账号。

    Returns:
        包含 host/port/http_port/user/password/database 的字典。
    """
    base = load_ch_config()
    reader_user = get_service_secret("CLICKHOUSE_READER_USER", "clickhouse", required=False) or base["user"]
    reader_password = get_service_secret("CLICKHOUSE_READER_PASSWORD", "clickhouse", required=False) or base["password"]
    return {**base, "user": reader_user, "password": reader_password}


def load_ch_writer_config() -> dict[str, str]:
    """返回 CH 写入账号配置（audit 9.4 RBAC 治本 #ARCH-CH-027）。

    优先使用 CLICKHOUSE_WRITER_USER/PASSWORD，未配置时回退到 CLICKHOUSE_USER/PASSWORD。
    用于 ch_writer 的 TCP/HTTP 写入路径，确保写入操作使用 DB 级 INSERT/ALTER 账号。

    Returns:
        包含 host/port/http_port/user/password/database 的字典。
    """
    base = load_ch_config()
    writer_user = get_service_secret("CLICKHOUSE_WRITER_USER", "clickhouse", required=False) or base["user"]
    writer_password = get_service_secret("CLICKHOUSE_WRITER_PASSWORD", "clickhouse", required=False) or base["password"]
    return {**base, "user": writer_user, "password": writer_password}
