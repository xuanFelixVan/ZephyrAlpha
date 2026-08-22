# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md
# [MODULE] scripts.ch.apply_rbac
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_config; clickhouse-driver(pip)
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] RBAC-as-Code: CH 账号分级真源为本脚本; apply() 用 default(admin) 账号创建 zephyr_reader/zephyr_writer 并授权; verify() 用各账号实测权限; 幂等(CREATE USER IF NOT EXISTS + GRANT 可重复执行); 账号凭证真源为 config/.env.clickhouse
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH不可达->打印错误+退出码2; 权限验证失败->列出差异+退出码1; 全部匹配->退出码0
# [TESTS] scripts/ch/apply_rbac.py --verify (smoke test: 账号存在+权限正确+reader DROP被拒+writer可写)
# [TTL] permanent
"""ClickHouse RBAC 账号分级部署 + 验证脚本（audit 9.4 治本 #ARCH-CH-027）。

RBAC-as-Code 模式：
    - zephyr_reader: SELECT-only（database_service 查询用）
    - zephyr_writer: INSERT/SELECT/ALTER/CREATE/DROP/OPTIMIZE（ch_writer 写入用）
    - 账号凭证真源为 config/.env.clickhouse（CLICKHOUSE_READER/WRITEr_USER/PASSWORD）
    - 本脚本用 default(admin) 账号创建用户并授权，幂等可重复执行

治本背景（audit 9.4 #ARCH-CH-027，2026-07-23）：
    审查发现 CH 仅有 default 一个用户，读写未分离。本脚本实现 DB 级账号分级，
    确保 database_service 只读路径用 zephyr_reader（SELECT-only），
    ch_writer 写入路径用 zephyr_writer（INSERT/ALTER/CREATE/DROP/OPTIMIZE）。
    zephyr_writer 需 SELECT ON system.* 以支持 is_replacing_engine() 引擎查询。

用法::

    python scripts/ch/apply_rbac.py           # 创建用户 + 授权 + 验证
    python scripts/ch/apply_rbac.py --verify  # 仅验证

退出码：
    0 = 全部一致
    1 = 有不一致
    2 = ClickHouse 不可达
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from clickhouse_driver import Client

from zephyr.data.ch_config import load_ch_config, load_ch_reader_config, load_ch_writer_config

# ========== RBAC 定义 ==========

# default(admin) 账号配置——用于创建用户和授权
_ADMIN_CONFIG = load_ch_config()

# 管理员预建库清单（#256③ 路线B，2026-08-22）：zephyr_writer 无 CREATE DATABASE 权限
# （实证 Code 497），业务库一律由本脚本 admin 通道预建；apply 脚本建表前置改走
# ch_writer.ensure_database（存在即过，不再对 writer 发 CREATE DATABASE）。
_PRECREATE_DATABASES = ["c1_market", "c3_fundamental", "c0_meta"]

# zephyr_writer 权限：INSERT/SELECT/ALTER/CREATE/DROP/OPTIMIZE on 业务库 + SELECT on system/c0_meta
_WRITER_GRANTS = [
    "GRANT SELECT ON c1_market.* TO zephyr_writer",
    "GRANT INSERT ON c1_market.* TO zephyr_writer",
    "GRANT ALTER TABLE ON c1_market.* TO zephyr_writer",
    "GRANT CREATE TABLE ON c1_market.* TO zephyr_writer",
    "GRANT DROP TABLE ON c1_market.* TO zephyr_writer",
    "GRANT OPTIMIZE ON c1_market.* TO zephyr_writer",
    "GRANT SELECT ON c3_fundamental.* TO zephyr_writer",
    "GRANT INSERT ON c3_fundamental.* TO zephyr_writer",
    "GRANT ALTER TABLE ON c3_fundamental.* TO zephyr_writer",
    "GRANT CREATE TABLE ON c3_fundamental.* TO zephyr_writer",
    "GRANT DROP TABLE ON c3_fundamental.* TO zephyr_writer",
    "GRANT OPTIMIZE ON c3_fundamental.* TO zephyr_writer",
    "GRANT SELECT ON c0_meta.* TO zephyr_writer",
    "GRANT SELECT ON system.* TO zephyr_writer",
]

# zephyr_reader 权限：SELECT-only on 业务库 + system + c0_meta
_READER_GRANTS = [
    "GRANT SELECT ON c1_market.* TO zephyr_reader",
    "GRANT SELECT ON c3_fundamental.* TO zephyr_reader",
    "GRANT SELECT ON c0_meta.* TO zephyr_reader",
    "GRANT SELECT ON system.* TO zephyr_reader",
]


def _connect_admin() -> Client:
    """用 default(admin) 账号连接 CH。"""
    return Client(
        host=_ADMIN_CONFIG["host"],
        port=int(_ADMIN_CONFIG["port"]),
        user="default",
        password="",
        connect_timeout=5,
    )


def _connect_reader() -> Client:
    """用 zephyr_reader 账号连接 CH（验证只读权限）。"""
    cfg = load_ch_reader_config()
    return Client(
        host=cfg["host"],
        port=int(cfg["port"]),
        user=cfg["user"],
        password=cfg["password"],
        connect_timeout=5,
    )


def _connect_writer() -> Client:
    """用 zephyr_writer 账号连接 CH（验证写入权限）。"""
    cfg = load_ch_writer_config()
    return Client(
        host=cfg["host"],
        port=int(cfg["port"]),
        user=cfg["user"],
        password=cfg["password"],
        connect_timeout=5,
    )


def apply() -> bool:
    """创建用户 + 授权（幂等）。

    Returns:
        True 如果全部成功，False 如果有失败。
    """
    ok = True
    try:
        c = _connect_admin()
    except Exception as e:  # noqa: BLE001
        print(f"ERROR: 无法连接 CH (admin): {e}")
        return False

    # 1. 创建用户（幂等：CREATE USER IF NOT EXISTS）
    reader_cfg = load_ch_reader_config()
    writer_cfg = load_ch_writer_config()

    create_sqls = [
        f"CREATE USER IF NOT EXISTS zephyr_reader IDENTIFIED WITH plaintext_password BY '{reader_cfg['password']}'",
        f"CREATE USER IF NOT EXISTS zephyr_writer IDENTIFIED WITH plaintext_password BY '{writer_cfg['password']}'",
    ]
    for sql in create_sqls:
        try:
            c.execute(sql)
            print(f"  OK: {sql.split(' BY ')[0]}")
        except Exception as e:  # noqa: BLE001
            print(f"  FAIL: {sql} -> {e}")
            ok = False

    # 2. 管理员预建库（幂等：CREATE DATABASE IF NOT EXISTS，#256③ 路线B）
    print("\n--- Pre-creating databases (admin channel) ---")
    for db in _PRECREATE_DATABASES:
        try:
            c.execute(f"CREATE DATABASE IF NOT EXISTS {db}")
            print(f"  OK: {db}")
        except Exception as e:  # noqa: BLE001
            print(f"  FAIL: CREATE DATABASE {db} -> {e}")
            ok = False

    # 3. 授权（幂等：GRANT 可重复执行）
    print("\n--- Granting zephyr_writer permissions ---")
    for sql in _WRITER_GRANTS:
        try:
            c.execute(sql)
        except Exception as e:  # noqa: BLE001
            print(f"  FAIL: {sql} -> {e}")
            ok = False
    print(f"  {_WRITER_GRANTS.__len__()} grants applied to zephyr_writer")

    print("\n--- Granting zephyr_reader permissions ---")
    for sql in _READER_GRANTS:
        try:
            c.execute(sql)
        except Exception as e:  # noqa: BLE001
            print(f"  FAIL: {sql} -> {e}")
            ok = False
    print(f"  {_READER_GRANTS.__len__()} grants applied to zephyr_reader")

    c.disconnect()
    return ok


def verify() -> bool:
    """验证 RBAC 配置正确。

    检查项：
    1. zephyr_reader 和 zephyr_writer 用户存在
    2. zephyr_reader 可以 SELECT
    3. zephyr_reader DROP 被拒
    4. zephyr_writer 可以 CREATE/INSERT/DROP
    5. zephyr_writer 可以查询 system.data_skipping_indices
    6. zephyr_writer 可以查询 system.users

    Returns:
        True 如果全部通过，False 如果有失败。
    """
    ok = True
    try:
        c_admin = _connect_admin()
    except Exception as e:  # noqa: BLE001
        print(f"ERROR: 无法连接 CH (admin): {e}")
        return False

    # 1. 用户存在
    rows = c_admin.execute(
        "SELECT name FROM system.users "
        "WHERE name IN ('zephyr_reader','zephyr_writer') "
        "ORDER BY name FORMAT TabSeparated"
    )
    users = [r[0] for r in rows]
    _check("zephyr_reader exists", "zephyr_reader" in users, f"users={users}")
    _check("zephyr_writer exists", "zephyr_writer" in users, f"users={users}")
    if "zephyr_reader" not in users or "zephyr_writer" not in users:
        ok = False

    # 1b. 管理员预建库存在性（#256③ 路线B）
    rows = c_admin.execute("SELECT name FROM system.databases ORDER BY name FORMAT TabSeparated")
    dbs = [r[0] for r in rows]
    for db in _PRECREATE_DATABASES:
        _check(f"database {db} exists", db in dbs, f"dbs={dbs}")
        if db not in dbs:
            ok = False
    c_admin.disconnect()

    # 2-3. reader 权限验证
    try:
        c_r = _connect_reader()
        rows = c_r.execute("SELECT 1")
        _check("zephyr_reader SELECT", rows[0][0] == 1, "")
        if rows[0][0] != 1:
            ok = False

        # reader DROP 应被拒
        try:
            c_r.execute("DROP TABLE c1_market._rbac_verify_test")
            _check("zephyr_reader DROP denied", False, "DROP succeeded (should be denied)")
            ok = False
        except Exception:
            _check("zephyr_reader DROP denied", True, "")
        c_r.disconnect()
    except Exception as e:  # noqa: BLE001
        _check("zephyr_reader SELECT", False, str(e))
        ok = False

    # 4-6. writer 权限验证
    try:
        c_w = _connect_writer()

        # writer CREATE/INSERT/DROP
        c_w.execute("CREATE TABLE IF NOT EXISTS c1_market._rbac_verify_test (x UInt8) ENGINE=Memory")
        c_w.execute("INSERT INTO c1_market._rbac_verify_test VALUES (1)")
        c_w.execute("DROP TABLE c1_market._rbac_verify_test")
        _check("zephyr_writer CREATE/INSERT/DROP", True, "")
    except Exception as e:  # noqa: BLE001
        _check("zephyr_writer CREATE/INSERT/DROP", False, str(e))
        ok = False

    # 5. writer system.data_skipping_indices
    try:
        rows = c_w.execute(
            "SELECT count() FROM system.data_skipping_indices WHERE database='c1_market' AND table='tick_data'"
        )
        _check("zephyr_writer system.data_skipping_indices", rows[0][0] >= 0, f"count={rows[0][0]}")
    except Exception as e:  # noqa: BLE001
        _check("zephyr_writer system.data_skipping_indices", False, str(e))
        ok = False

    # 6. writer system.users
    try:
        rows = c_w.execute("SELECT count() FROM system.users WHERE name IN ('zephyr_reader','zephyr_writer')")
        _check("zephyr_writer system.users", rows[0][0] == 2, f"count={rows[0][0]}")
    except Exception as e:  # noqa: BLE001
        _check("zephyr_writer system.users", False, str(e))
        ok = False

    try:
        c_w.disconnect()
    except Exception:  # noqa: BLE001
        pass

    return ok


def _check(desc: str, condition: bool, detail: str) -> None:
    """打印验证结果。"""
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {desc}" + (f" — {detail}" if detail else ""))


def main() -> int:
    """主入口。"""
    verify_only = "--verify" in sys.argv

    if not verify_only:
        print("=" * 60)
        print("Applying RBAC (CREATE USER + GRANT)...")
        print("=" * 60)
        if not apply():
            print("\nERROR: apply 失败，请检查 CH 连接和 admin 权限")
            return 2

    print("\n" + "=" * 60)
    print("Verifying RBAC...")
    print("=" * 60)
    if verify():
        print("\n✅ 全部验证通过")
        return 0
    print("\n❌ 验证失败")
    return 1


if __name__ == "__main__":
    sys.exit(main())
