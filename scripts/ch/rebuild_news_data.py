#!/usr/bin/env python
# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §4
# [MODULE] scripts.ch.rebuild_news_data
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_config; clickhouse-driver(lazy)
# [CONSUMERS] (治理 CLI，无模块消费者；产物=news_data 健康新表)
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 旧表 part 排序损坏（时区迁移原地改键列后遗症），merge/mutation 持续折叠吞数据——旧表只读封刀；重建=逐月 argMax 按键去重拷贝（GROUP BY (news_id, publish_time) 留 ingest_ts 最新行）；误伤批（ingest=2026-08-26 18:58:02.495 UTC 且 08:00:00 指纹）-8h 精确反演；断点续作（进度文件记已完成月份）；逐月对账不符即中止不换名；原子双 RENAME 换表；窗口期增量从旧表补捞
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH 不可达→exit 1；拷贝/对账失败→exit 2（不换名，可重跑）；无近 24h 备份→exit 3
# [TESTS] tests/scripts/test_ch_rebuild_news_data.py
# [TTL] permanent
"""rebuild_news_data.py — CAND-DAT-025 事故处置：news_data 换表重建。

背景（design_memos/67_news_data_dedup_design.md + 2026-08-28 事故链）：
    旧表 part 物理排序与排序键 (news_id, publish_time) 脱节（时区迁移 #ARCH-CH-022
    原地改键列后遗症），ReplacingMergeTree merge/mutation 在坏 part 上把不同键的行
    折叠丢弃（实证：202506 分区 409 键 OPTIMIZE 后剩 32 行；全新干净表引擎对照正常）。
    表持续萎缩（146,519→118,214 id，8 小时），必须换表重建。

步骤（execute）：
    1. CREATE news_data_rebuild（schema 克隆）
    2. 逐月 INSERT SELECT：误伤批 -8h 反演 + GROUP BY (news_id, fixed_pt) argMax 去重
    3. 逐月对账（源 DISTINCT 键数 == 目标行数），不符即中止（不换名可重跑）
    4. 原子双 RENAME（旧表→news_data_corrupt_20260828 保留观察，新表顶名）
    5. 窗口期增量补捞（旧表 ingest_ts > 重建起点的新行直插，引擎自然折叠）
    6. 终验：FINAL == 物理 == 键数（读路径痊愈判据）

用法:
    python scripts/ch/rebuild_news_data.py --dry-run    # 对账预览（月份/键数/误伤数），0 写入
    python scripts/ch/rebuild_news_data.py --execute    # 正式重建（近 24h 备份前置）

依据: CAND-DAT-025；design_memos/67_news_data_dedup_design.md
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

from zephyr.data.ch_config import load_ch_config  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

SRC_TABLE = "c3_fundamental.news_data"
REBUILD_TABLE = "c3_fundamental.news_data_rebuild"
CORRUPT_TABLE = "c3_fundamental.news_data_corrupt_20260828"

# 误伤批指纹：purge 修正重插的单次 INSERT（全行 ingest_ts 全等，2026-08-27 实证 min==max）
_MISCORRECT_BATCH_TS = "2026-08-26 18:58:02.495"

# news_data 全列清单（system.columns 实测 29 列）
ALL_COLUMNS: list[str] = [
    "news_id",
    "publish_time",
    "full_publish_time",
    "title",
    "content",
    "author",
    "keyword",
    "summary",
    "source",
    "source_url",
    "news_source_id",
    "recommend_sign",
    "is_accessory",
    "file_size",
    "related_symbol",
    "short_name",
    "security_type",
    "category",
    "region",
    "language",
    "sentiment_score",
    "sentiment_label",
    "related_symbols",
    "related_tags",
    "raw_data",
    "data_source",
    "crawl_time",
    "quality_flag",
    "ingest_ts",
]

PROGRESS_FILE = ROOT / ".runtime" / "rebuild_news_data_done.txt"

_MUTATION_POLL_S = 15
_MUTATION_TIMEOUT_S = 7200


def sql_create_rebuild() -> str:
    """schema 克隆（AS 复制引擎定义：ReplacingMergeTree(ingest_ts) 同分区同键）。"""
    return f"CREATE TABLE IF NOT EXISTS {REBUILD_TABLE} AS {SRC_TABLE}"


def sql_months() -> str:
    return f"SELECT DISTINCT toYYYYMM(publish_time) FROM {SRC_TABLE} ORDER BY 1"


def sql_copy_partition(month: int) -> str:
    """单月拷贝：误伤批 -8h 反演 + GROUP BY (news_id, fixed_pt) argMax 去重。

    反演只命中"误伤批且 08:00:00 指纹"的行（purge 修正重插误 +8h 的 1,400 行）；
    full_publish_time 同步反演（>86400 守卫与原变换严格互逆）；08:00-8h=当日 00:00，
    不跨月，源分区与目标分区一致。
    """
    select_exprs = []
    for col in ALL_COLUMNS:
        if col == "news_id":
            select_exprs.append("news_id")  # 分组键直出（不可包聚合）
        elif col == "publish_time":
            select_exprs.append("fixed_pt AS publish_time")
        elif col == "ingest_ts":
            select_exprs.append("max(ver_ts) AS ingest_ts")
        elif col == "full_publish_time":
            select_exprs.append(
                "argMax(if(full_publish_time > toDateTime64('1970-01-02 00:00:00', 3, 'UTC') AND is_misbatch = 1, "
                "full_publish_time - INTERVAL 8 HOUR, full_publish_time), ver_ts) AS full_publish_time"
            )
        else:
            select_exprs.append(f"argMax({col}, ver_ts) AS {col}")
    return (
        f"INSERT INTO {REBUILD_TABLE} ({', '.join(ALL_COLUMNS)}) "
        f"SELECT {', '.join(select_exprs)} FROM ("
        f"SELECT *, ingest_ts AS ver_ts, "
        f"if(ingest_ts = toDateTime64('{_MISCORRECT_BATCH_TS}', 3, 'UTC') "
        f"AND toHour(publish_time) = 8 AND toMinute(publish_time) = 0 AND toSecond(publish_time) = 0, "
        f"publish_time - INTERVAL 8 HOUR, publish_time) AS fixed_pt, "
        f"if(ingest_ts = toDateTime64('{_MISCORRECT_BATCH_TS}', 3, 'UTC') "
        f"AND toHour(publish_time) = 8 AND toMinute(publish_time) = 0 AND toSecond(publish_time) = 0, "
        f"1, 0) AS is_misbatch "
        f"FROM {SRC_TABLE} WHERE toYYYYMM(publish_time) = {month}"
        f") GROUP BY news_id, fixed_pt"
    )


def sql_verify_partition(month: int) -> tuple[str, str]:
    """（源 DISTINCT 键数, 目标行数）——相等才过。"""
    src = (
        f"SELECT count() FROM (SELECT DISTINCT news_id, "
        f"if(ingest_ts = toDateTime64('{_MISCORRECT_BATCH_TS}', 3, 'UTC') "
        f"AND toHour(publish_time) = 8 AND toMinute(publish_time) = 0 AND toSecond(publish_time) = 0, "
        f"publish_time - INTERVAL 8 HOUR, publish_time) AS fixed_pt "
        f"FROM {SRC_TABLE} WHERE toYYYYMM(publish_time) = {month})"
    )
    dst = f"SELECT count() FROM {REBUILD_TABLE} WHERE toYYYYMM(publish_time) = {month}"
    return src, dst


def sql_rename_swap() -> str:
    """原子双 RENAME（单语句多 rename = 原子交换）。"""
    return f"RENAME TABLE {SRC_TABLE} TO {CORRUPT_TABLE}, {REBUILD_TABLE} TO {SRC_TABLE}"


def sql_delta_backfill(since_utc: str) -> str:
    """窗口期增量补捞：换名后旧表（CORRUPT）里 ingest_ts>起点的新行直插新表（引擎自然折叠）。"""
    return (
        f"INSERT INTO {SRC_TABLE} ({', '.join(ALL_COLUMNS)}) "
        f"SELECT {', '.join(ALL_COLUMNS)} FROM {CORRUPT_TABLE} "
        f"WHERE ingest_ts > toDateTime64('{since_utc}', 3, 'UTC')"
    )


def sql_final_verify() -> str:
    return f"SELECT count(), uniqExact(news_id), uniqExact((news_id, publish_time)) FROM {SRC_TABLE}"


def get_client():
    """clickhouse-driver TCP 客户端（admin 档：RENAME/CREATE 需高授权，purge 实证 writer 不足）。"""
    import clickhouse_driver  # noqa: PLC0415 — lazy

    cfg = load_ch_config()
    return clickhouse_driver.Client(
        host=cfg["host"],
        port=cfg.get("port", 9000),
        user=cfg.get("user", "default"),
        password=cfg.get("password", ""),
        send_receive_timeout=_MUTATION_TIMEOUT_S,
    )


def _recent_backup_ok() -> tuple[bool, str]:
    """近 24h 成功 CH 备份（真源=backup_state.json，与 purge_news_data_rr_dup 同防线）。"""
    import json

    path = ROOT / "data" / "databases" / "backup_state.json"
    if not path.exists():
        return (False, "backup_state.json 不存在")
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return (False, "backup_state.json 无法解析")
    ts = state.get("last_ch_backup_time")
    if not ts or not state.get("last_ch_backup_verified"):
        return (False, "无成功 CH 备份记录")
    t = datetime.fromisoformat(str(ts))
    if t.tzinfo is None:
        t = t.astimezone()
    if datetime.now().astimezone() - t > timedelta(hours=24):
        return (False, f"最近 CH 备份已超 24h（{ts}）")
    return (True, f"最近成功备份 {ts}（verified）")


def load_done_months() -> set[int]:
    if not PROGRESS_FILE.exists():
        return set()
    return {int(x) for x in PROGRESS_FILE.read_text(encoding="utf-8").split() if x.strip().isdigit()}


def dry_run(client) -> None:
    months = [r[0] for r in client.execute(sql_months())]
    total_keys = 0
    mis = client.execute(
        f"SELECT count() FROM {SRC_TABLE} "
        f"WHERE ingest_ts = toDateTime64('{_MISCORRECT_BATCH_TS}', 3, 'UTC') "
        "AND toHour(publish_time) = 8 AND toMinute(publish_time) = 0 AND toSecond(publish_time) = 0"
    )[0][0]
    log.info("月份数 %d（%s ~ %s）；误伤批待反演 %d 行", len(months), months[0], months[-1], mis)
    for m in months:
        src_sql, _ = sql_verify_partition(m)
        n = int(client.execute(src_sql)[0][0])
        total_keys += n
        log.info("  %d: %d 键", m, n)
    log.info("总键数 %d（重建目标行数）", total_keys)


def execute_rebuild(client) -> None:
    t_start_utc = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    client.execute(sql_create_rebuild())
    log.info("重建表已建（起点 %s UTC）", t_start_utc)

    done = load_done_months()
    months = [r[0] for r in client.execute(sql_months())]
    for m in months:
        if m in done:
            log.info("%d 已完成，跳过", m)
            continue
        t0 = time.time()
        client.execute(sql_copy_partition(m))
        src_sql, dst_sql = sql_verify_partition(m)
        n_src = int(client.execute(src_sql)[0][0])
        n_dst = int(client.execute(dst_sql)[0][0])
        if n_src != n_dst:
            raise RuntimeError(f"{m} 对账不符：源 {n_src} 键 != 目标 {n_dst} 行（不换名，可重跑）")
        PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(PROGRESS_FILE, "a", encoding="utf-8") as f:
            f.write(f"{m}\n")
        log.info("%d 完成：%d 行（%.0f 秒）", m, n_dst, time.time() - t0)

    # 原子换名 + 增量补捞 + 终验
    log.info("逐月对账全过，原子换名...")
    client.execute(sql_rename_swap())
    delta = int(
        client.execute(
            f"SELECT count() FROM {CORRUPT_TABLE} WHERE ingest_ts > toDateTime64('{t_start_utc}', 3, 'UTC')"
        )[0][0]
    )
    if delta > 0:
        client.execute(sql_delta_backfill(t_start_utc))
        log.info("窗口期增量补捞 %d 行", delta)
    rows, ids, keys = client.execute(sql_final_verify())[0]
    log.info("终验：物理 %d 行 / %d id / %d 键", rows, ids, keys)
    fin = client.execute(
        f"SELECT count(), uniqExact(news_id) FROM {SRC_TABLE} FINAL WHERE category = 'research_report'"
    )[0]
    log.info("终验 FINAL(research_report)：%d 行 / %d id", fin[0], fin[1])
    rr = client.execute(
        f"SELECT count(), uniqExact(news_id), uniqExact((news_id, publish_time)) "
        f"FROM {SRC_TABLE} WHERE category = 'research_report'"
    )[0]
    if not (fin[0] == rr[0] == rr[2] and fin[1] == rr[1]):
        raise RuntimeError(f"FINAL 终验不符：FINAL {fin} vs 物理 {rr}（读路径未愈，旧表仍在，可回滚换名）")
    log.info("读路径痊愈确认：FINAL == 物理 == 键数")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="news_data 换表重建（CAND-DAT-025 事故处置）")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="对账预览，0 写入")
    mode.add_argument("--execute", action="store_true", help="正式重建（近 24h 备份前置）")
    parser.add_argument("--no-backup-check", action="store_true", help="跳过备份检查（不推荐）")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    try:
        client = get_client()
        client.execute("SELECT 1")
    except Exception as exc:  # noqa: BLE001 — CH 不可达 fail-closed
        log.error("ClickHouse 不可达: %s", exc)
        sys.exit(1)

    if args.dry_run:
        dry_run(client)
        return

    if not args.no_backup_check:
        ok, msg = _recent_backup_ok()
        log.info("备份检查：%s", msg)
        if not ok:
            log.error("近 24h 无成功 CH 备份，拒绝破坏性执行（--no-backup-check 跳过，不推荐）")
            sys.exit(3)

    try:
        execute_rebuild(client)
    except Exception as exc:  # noqa: BLE001 — 失败现场保留于日志
        log.error("重建失败: %s", exc)
        sys.exit(2)
    log.info("重建完成")


if __name__ == "__main__":
    main()
