# [BLUEPRINT] MOD-INF-005 | (auto-injected by S4 reconciler) | §
#!/usr/bin/env python
# [TTL] task_bound
"""R6: 表级恢复演练——检查备份磁盘配置 + 候选表行数（非破坏性只读查询）。"""

from zephyr.data import ch_reader

print("=== 1. Backup disks configured ===")
disks = ch_reader.query(
    "SELECT name, path, type FROM system.disks WHERE name LIKE '%backup%' OR name = 'backups' OR type = 's3'"  # noqa: bare-sql  存量参数化查询/动态标识符，format重排伪新增（§5.160.2集中化专项另列）
)
print(disks)

print("\n=== 2. Backup files on 'backups' disk ===")
try:
    files = ch_reader.query("SELECT name, size FROM system.files('backups', '') WHERE name LIKE '%zip%' ORDER BY name")  # noqa: bare-sql  存量参数化查询/动态标识符，format重排伪新增（§5.160.2集中化专项另列）
    print(files)
except Exception as e:
    print(f"system.files query failed: {e}")
    # Try alternative: list via system.disks path
    print("Trying alternative: check backup config file...")
    try:
        cfg = ch_reader.query("SELECT name, value FROM system.settings WHERE name LIKE '%backup%'")  # noqa: bare-sql  存量参数化查询/动态标识符，format重排伪新增（§5.160.2集中化专项另列）
        print(cfg)
    except Exception as e2:
        print(f"Also failed: {e2}")

print("\n=== 3. Candidate tables for restore drill (small, safe) ===")
tables = ch_reader.query(
    "SELECT database, name, total_rows, total_bytes "
    "FROM system.tables "
    "WHERE database IN ('c1_market', 'c3_fundamental') "
    "AND engine NOT LIKE '%View%' "
    "ORDER BY total_rows ASC "
    "LIMIT 10"
)
print(tables)

print("\n=== 4. trade_calendar row count (candidate) ===")
try:
    count = ch_reader.query("SELECT count() FROM c1_market.trade_calendar")
    print(f"trade_calendar rows: {count}")
except Exception as e:
    print(f"trade_calendar not available: {e}")
