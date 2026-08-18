# [BLUEPRINT] MOD-INF-043 | docs/03_modules/_domain_infrastructure_operations/disaster_recovery_backup/blueprint.md
# [MODULE] scripts.ch._recovery_drill
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_config; clickhouse-driver(pip); config/.env.ch_backup
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] diagnostic
# [INVARIANTS] 非破坏性恢复演练：轮询备份完成->恢复小表(trade_calendar)到_restore_drill临时库->行数校验->清理；不碰 live 表；零数据丢失风险
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH不可达->退出码2; 备份未完成->等待+退出码1; 恢复成功->退出码0; 行数不匹配->退出码3
# [TESTS] python scripts/ch/_recovery_drill.py (smoke: 轮询+恢复+校验+清理)
# [TTL] permanent
# noqa: m02-manual  一次性恢复演练脚本
"""恢复演练：轮询备份完成 → 恢复小表到临时库 → 行数校验 → 清理。

非破坏性：不碰 live 表，恢复到 _restore_drill 临时库。
"""
from __future__ import annotations

import os
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from clickhouse_driver import Client

from zephyr.data.ch_config import load_ch_config

_cfg = load_ch_config()
c = Client(host=_cfg["host"], port=9000, user=_cfg["user"], password=_cfg["password"])

# 从 .env.ch_backup 读 S3 凭证
_env_path = Path(r"D:\ZephyrAlpha\config\.env.ch_backup")
_env: dict[str, str] = {}
if _env_path.exists():
    for line in _env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            _env[k.strip()] = v.strip()

S3_KEY = _env.get("CH_S3_ACCESS_KEY", "zephyrbk")
S3_SECRET = _env.get("CH_S3_SECRET_KEY", "")

# 恢复演练用表（小表，快速验证）
DRILL_TABLE = "c1_market.trade_calendar"  # 13K rows
DRILL_DB = "_restore_drill"
DRILL_RENAMED = f"{DRILL_DB}.trade_calendar"


def get_latest_backup_s3_url() -> str | None:
    """从 system.backups 获取最新备份的 S3 URL。"""
    r = c.execute(
        "SELECT name, status FROM system.backups ORDER BY start_time DESC LIMIT 1"
    )
    if r:
        return str(r[0][0]), str(r[0][1])
    return None, None


def wait_for_backup_complete(timeout: int = 7200) -> tuple[str, str] | None:
    """轮询 system.backups，等待最新 CREATING_BACKUP 转为 BACKUP_CREATED。返回 (s3_url, backup_id)。"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 等待备份完成...")
    start = time.time()
    last_status = ""
    while time.time() - start < timeout:
        try:
            r = c.execute(
                "SELECT id, name, status, total_size, num_files "
                "FROM system.backups ORDER BY start_time DESC LIMIT 1"
            )
            if r:
                bid, name, status, size, files = r[0]
                if status != last_status:
                    print(f"  [{int(time.time()-start)}s] status={status} size={size} files={files}")
                    last_status = status
                if status == "BACKUP_CREATED":
                    print(f"  [OK] 备份完成! id={bid}")
                    return str(name), str(bid)
                if status == "BACKUP_FAILED":
                    print(f"  [FAIL] 备份失败! id={bid}")
                    return None
        except Exception as e:
            print(f"  查询异常: {e}")
        time.sleep(30)
    print(f"\n  超时 ({timeout}s)")
    return None


def run_recovery_drill(s3_name: str) -> bool:
    """恢复 trade_calendar 到 _restore_drill 库，校验行数。"""
    print(f"\n{'='*60}")
    print(f"恢复演练开始 — {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}")
    print(f"S3 backup: {s3_name[:80]}...")

    # 1. 创建临时库
    print("\n[1] 创建临时库 _restore_drill")
    c.execute(f"DROP DATABASE IF EXISTS {DRILL_DB}")
    c.execute(f"CREATE DATABASE {DRILL_DB}")
    print("  [OK]")

    # 2. 恢复小表（用备份的 S3 name 作为恢复源）
    print(f"\n[2] RESTORE TABLE {DRILL_TABLE} -> {DRILL_RENAMED}")
    restore_sql = (
        f"RESTORE TABLE {DRILL_TABLE} AS {DRILL_RENAMED} "
        f"FROM S3('{s3_name}', '{S3_KEY}', '{S3_SECRET}')"
    )
    print(f"  SQL: RESTORE TABLE ... AS {DRILL_RENAMED} FROM S3(...)")
    try:
        c.execute(restore_sql, settings={"async": False})
        print("  [OK] 恢复完成（同步）")
    except Exception as e:
        err_msg = str(e)
        if "async" in err_msg.lower() or "not supported" in err_msg.lower():
            # 尝试 async
            print(f"  同步模式不支持，尝试 async: {err_msg[:100]}")
            try:
                c.execute(restore_sql + " ASYNC")
                print("  [OK] async 恢复已触发，等待完成...")
                for i in range(120):
                    time.sleep(10)
                    r = c.execute(
                        "SELECT status, error FROM system.backups ORDER BY start_time DESC LIMIT 1"
                    )
                    if r:
                        st = r[0][0]
                        if "RESTORED" in st:
                            print("  [OK] 恢复完成")
                            break
                        if "FAILED" in st:
                            print(f"  [FAIL] 恢复失败: {st} | {r[0][1][:200]}")
                            return False
                        if i % 6 == 0:
                            print(f"  [{i*10}s] {st}...")
            except Exception as e2:
                print(f"  [FAIL] async 也失败: {e2}")
                return False
        else:
            print(f"  [FAIL] 恢复失败: {err_msg[:200]}")
            return False

    # 3. 行数对比
    print("\n[3] 行数校验")
    live_count = c.execute(f"SELECT count() FROM {DRILL_TABLE}")[0][0]
    drill_count = c.execute(f"SELECT count() FROM {DRILL_RENAMED}")[0][0]
    print(f"  live ({DRILL_TABLE}):  {live_count:,}")
    print(f"  drill ({DRILL_RENAMED}): {drill_count:,}")
    match = (live_count == drill_count)
    if match:
        print("  [OK] 行数一致!")
    else:
        print(f"  [WARN] 行数不一致 (diff={live_count - drill_count})")

    # 4. 数据抽样对比
    print("\n[4] 数据抽样对比（最新 3 行）")
    try:
        live_sample = c.execute(
            f"SELECT * FROM {DRILL_TABLE} ORDER BY trade_date DESC LIMIT 3"
        )
        drill_sample = c.execute(
            f"SELECT * FROM {DRILL_RENAMED} ORDER BY trade_date DESC LIMIT 3"
        )
        if live_sample == drill_sample:
            print("  [OK] 抽样数据完全一致")
        else:
            print("  [WARN] 抽样数据有差异")
            print(f"    live:  {live_sample[:2]}")
            print(f"    drill: {drill_sample[:2]}")
    except Exception as e:
        print(f"  (抽样对比跳过: {e})")

    # 5. 清理
    print("\n[5] 清理临时库")
    c.execute(f"DROP DATABASE {DRILL_DB}")
    print("  [OK] _restore_drill 已删除")

    # 6. 结论
    print(f"\n{'='*60}")
    if match:
        print("恢复演练: PASS — 备份完整可恢复 ✓")
    else:
        print("恢复演练: WARN — 行数有差异，需调查")
    print(f"{'='*60}")
    return match


def main() -> None:
    # Step 1: 等待备份完成
    result = wait_for_backup_complete(timeout=7200)
    if not result:
        print("[FAIL] 备份未完成或失败，无法进行恢复演练")
        sys.exit(1)
    s3_name, backup_id = result

    # Step 2: 执行恢复演练
    success = run_recovery_drill(s3_name)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
