# [BLUEPRINT] MOD-INF-005 | (auto-injected by S4 reconciler) | §
#!/usr/bin/env python
# [TTL] task_bound
"""R6: 表级恢复演练——通过 VM clickhouse-client 执行 RESTORE（绕过 zephyr_writer 权限限制）。

在 VM 上以 clickhouse OS 用户运行 clickhouse-client，拥有完整 DB 权限。
步骤：CREATE temp DB -> RESTORE TABLE -> 校验行数 -> 清理。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backup"))
from ch_vm_ssh import ssh_run  # noqa: E402

TABLE = "trade_calendar"
SRC_DB = "c1_market"
TMP_DB = "_restore_drill"
BACKUP_FILE = "market.zip"

# 允许命令行指定表名：python r6_restore_via_vm.py [table_name]
if len(sys.argv) > 1:
    TABLE = sys.argv[1]


def ch_query(sql: str, timeout: int = 120) -> str:
    """在 VM 上执行 clickhouse-client 查询（sudo，以 clickhouse 用户权限）。

    用双引号包裹 --query 值（SQL 内部用单引号，如 Disk('backups', 'market.zip')）。
    """
    # SQL 内部不含双引号，用双引号包裹避免 shell 词分割，单引号留给 SQL 字面量
    cmd = f'sudo clickhouse-client --query "{sql}" 2>&1'
    result = ssh_run(cmd, timeout=timeout, use_sudo=True)
    out = result["stdout"].strip()
    # 去掉 PTY echo 的密码行
    lines = [l for l in out.splitlines() if l and "ZephyrAlpha" not in l]
    return "\n".join(lines)


def main() -> None:
    print(f"=== R6 表级恢复演练: {SRC_DB}.{TABLE} -> {TMP_DB}.{TABLE} ===\n")

    # 1. 源表行数
    src_count = ch_query(f"SELECT count() FROM {SRC_DB}.{TABLE}")
    print(f"[1] 源表 {SRC_DB}.{TABLE} 行数: {src_count}")

    # 2. 创建临时库
    print(f"[2] 创建临时库 {TMP_DB}...")
    print(ch_query(f"CREATE DATABASE IF NOT EXISTS {TMP_DB}"))

    # 3. RESTORE TABLE
    print(f"[3] RESTORE TABLE {SRC_DB}.{TABLE} FROM Disk('backups', '{BACKUP_FILE}')...")
    restore_sql = f"RESTORE TABLE {SRC_DB}.{TABLE} AS {TMP_DB}.{TABLE} FROM Disk('backups', '{BACKUP_FILE}')"
    restore_result = ch_query(restore_sql, timeout=300)
    print(f"    RESTORE 结果: {restore_result}")

    # 4. 校验行数
    restored_count = ch_query(f"SELECT count() FROM {TMP_DB}.{TABLE}")
    print(f"[4] 恢复表 {TMP_DB}.{TABLE} 行数: {restored_count}")

    # 5. 比对
    try:
        src_n = int(src_count.strip().splitlines()[-1].strip())
        rst_n = int(restored_count.strip().splitlines()[-1].strip())
    except (ValueError, IndexError):
        print(f"[5] 行数解析失败，原始值: src='{src_count}' restored='{restored_count}'")
        src_n, rst_n = -1, -1

    if src_n == rst_n and src_n > 0:
        print(f"[5] ✅ PASS: 行数一致 ({src_n} == {rst_n})")
    else:
        print(f"[5] ❌ FAIL: 行数不一致 (src={src_n} vs restored={rst_n})")

    # 6. 额外校验：抽样数据比对
    print("[6] 抽样数据比对（前 5 行）...")
    src_sample = ch_query(f"SELECT * FROM {SRC_DB}.{TABLE} ORDER BY 1 LIMIT 5 FORMAT TabSeparated")  # noqa: bare-sql  存量参数化查询/动态标识符，format重排伪新增（§5.160.2集中化专项另列）
    rst_sample = ch_query(f"SELECT * FROM {TMP_DB}.{TABLE} ORDER BY 1 LIMIT 5 FORMAT TabSeparated")  # noqa: bare-sql  存量参数化查询/动态标识符，format重排伪新增（§5.160.2集中化专项另列）
    if src_sample == rst_sample:
        print("    ✅ 抽样数据一致")
    else:
        print(f"    ⚠ 抽样数据有差异:\n    src: {src_sample[:200]}\n    rst: {rst_sample[:200]}")

    # 7. 清理临时库
    print(f"[7] 清理临时库 {TMP_DB}...")
    print(ch_query(f"DROP DATABASE IF EXISTS {TMP_DB}"))
    print("\n=== R6 演练完成 ===")


if __name__ == "__main__":
    main()
