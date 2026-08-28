#!/usr/bin/env python
# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §4
# [MODULE] scripts.ch.rebuild_news_data_tz2
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_config; clickhouse-driver(lazy)
# [CONSUMERS] (治理 CLI，无模块消费者；产物=news_data 时区语义健康新表)
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 16:00:00 指纹行（纯日期被按 UTC 解释存库，偏早 8h）publish_time +8h 修正——回测前视偏差治本（CAND-DAT-026）；指纹谓词只依赖本行字段（DAT-025 教训#2 安全形态）；跨月行由引擎按 fixed_pt 值归分区（月末 22.1 万行实证）；断点续作（按源分区进度文件）；全表对账（源按 fixed_pt 归月 vs 目标按 publish_time 归月）不符即中止不换名；原子双 RENAME；窗口期增量补捞
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH 不可达→exit 1；拷贝/对账失败→exit 2（不换名，可重跑）；无近 24h 备份→exit 3
# [TESTS] tests/scripts/test_ch_rebuild_news_data_tz2.py
# [TTL] permanent
"""rebuild_news_data_tz2.py — CAND-DAT-026：news_data publish_time 8h 偏移换表修正（时区防线二期）。

背景（67 号设计备忘 §4 + §8）：
    news 类别 98.4%、announcement 类别 100% 的 publish_time 偏早 8 小时（16:00:00 指纹：
    北京日期 D 被按 UTC 解释存为 D-1 16:00）。回测按库内时间会在 D-1 收盘后"看到"D 日
    信息——前视偏差，look_ahead_bias_detector 无法检出。DAT-025 已把表换出健康 parts，
    本轨修数据语义。

步骤（execute）：
    1. CREATE news_data_tz2（schema 克隆）
    2. 按源分区逐月 INSERT SELECT：16:00 指纹行 publish_time+8h（fixed_pt），
       GROUP BY (news_id, fixed_pt) argMax 去重；full_publish_time 不动（非纯日期语义，已实证）
    3. 全表对账：源按 toYYYYMM(fixed_pt) 归月 vs 目标按 toYYYYMM(publish_time) 归月
    4. 原子双 RENAME（旧表→news_data_pre_tz2_20260828 保留观察，新表顶名）
    5. 窗口期增量补捞 + 终验（FINAL==物理==键数；16:00 指纹=0）

用法:
    python scripts/ch/rebuild_news_data_tz2.py --dry-run    # 对账预览（指纹/跨月规模），0 写入
    python scripts/ch/rebuild_news_data_tz2.py --execute    # 正式重建（近 24h 备份前置）

依据: CAND-DAT-026（candidate_module_registry.yaml）；design_memos/67_news_data_dedup_design.md
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
REBUILD_TABLE = "c3_fundamental.news_data_tz2"
OLD_TABLE = "c3_fundamental.news_data_pre_tz2_20260828"

# 16:00:00 指纹谓词（纯日期被按 UTC 解释存库的 8h 偏移特征；只依赖本行字段）
_FINGERPRINT = (
    "toHour(publish_time) = 16 AND toMinute(publish_time) = 0 AND toSecond(publish_time) = 0"
)

ALL_COLUMNS: list[str] = [
    "news_id", "publish_time", "full_publish_time", "title", "content", "author",
    "keyword", "summary", "source", "source_url", "news_source_id", "recommend_sign",
    "is_accessory", "file_size", "related_symbol", "short_name", "security_type",
    "category", "region", "language", "sentiment_score", "sentiment_label",
    "related_symbols", "related_tags", "raw_data", "data_source", "crawl_time",
    "quality_flag", "ingest_ts",
]

PROGRESS_FILE = ROOT / ".runtime" / "rebuild_news_data_tz2_done.txt"

_MUTATION_TIMEOUT_S = 7200


def sql_create_rebuild() -> str:
    return f"CREATE TABLE IF NOT EXISTS {REBUILD_TABLE} AS {SRC_TABLE}"


def sql_months() -> str:
    return f"SELECT DISTINCT toYYYYMM(publish_time) FROM {SRC_TABLE} ORDER BY 1"


def _fixed_pt_expr() -> str:
    return f"if({_FINGERPRINT}, publish_time + INTERVAL 8 HOUR, publish_time) AS fixed_pt"


def sql_copy_partition(month: int) -> str:
    """按源分区拷贝：指纹行 +8h（fixed_pt），GROUP BY 键去重；full_publish_time 不动。"""
    select_exprs = []
    for col in ALL_COLUMNS:
        if col == "news_id":
            select_exprs.append("news_id")
        elif col == "publish_time":
            select_exprs.append("fixed_pt AS publish_time")
        elif col == "ingest_ts":
            select_exprs.append("max(ver_ts) AS ingest_ts")
        else:
            select_exprs.append(f"argMax({col}, ver_ts) AS {col}")
    return (
        f"INSERT INTO {REBUILD_TABLE} ({', '.join(ALL_COLUMNS)}) "
        f"SELECT {', '.join(select_exprs)} FROM ("
        f"SELECT *, ingest_ts AS ver_ts, {_fixed_pt_expr()} "
        f"FROM {SRC_TABLE} WHERE toYYYYMM(publish_time) = {month}"
        f") GROUP BY news_id, fixed_pt"
    )


def sql_verify_months() -> tuple[str, str]:
    """（源按 fixed_pt 归月键数, 目标按 publish_time 归月行数）——逐月相等才过。

    源侧必须 DISTINCT（同键物理重复行不去重会每月虚多 1-2 行，2026-08-28 实证）；
    目标侧必须按键 uniqExact（跨 INSERT 同键两行：邻月 fixed 撞键，如 id 在 6-30 16:00
    与 7-01 00:00 并存，fixed 后同键分属两次拷贝，引擎 merge 才折叠——语义无害但行数虚高）。"""
    src = (
        f"SELECT toYYYYMM(fixed_pt) AS m, count() FROM ("
        f"SELECT DISTINCT news_id, {_fixed_pt_expr()} FROM {SRC_TABLE}"
        f") GROUP BY m ORDER BY m"
    )
    dst = (
        f"SELECT toYYYYMM(publish_time) AS m, uniqExact((news_id, publish_time)) "
        f"FROM {REBUILD_TABLE} GROUP BY m ORDER BY m"
    )
    return src, dst


def sql_rename_swap() -> str:
    return (
        f"RENAME TABLE {SRC_TABLE} TO {OLD_TABLE}, "
        f"{REBUILD_TABLE} TO {SRC_TABLE}"
    )


def sql_delta_backfill(since_utc: str) -> str:
    return (
        f"INSERT INTO {SRC_TABLE} ({', '.join(ALL_COLUMNS)}) "
        f"SELECT {', '.join(ALL_COLUMNS)} FROM {OLD_TABLE} "
        f"WHERE ingest_ts > toDateTime64('{since_utc}', 3, 'UTC')"
    )


def sql_final_verify() -> str:
    return f"SELECT count(), uniqExact(news_id), uniqExact((news_id, publish_time)) FROM {SRC_TABLE}"


def get_client():
    """clickhouse-driver TCP 客户端（admin 档：RENAME/CREATE 需高授权，DAT-025 实证 writer 不足）。"""
    import clickhouse_driver  # noqa: PLC0415 — lazy

    cfg = load_ch_config()
    return clickhouse_driver.Client(
        host=cfg["host"], port=cfg.get("port", 9000),
        user=cfg.get("user", "default"), password=cfg.get("password", ""),
        send_receive_timeout=_MUTATION_TIMEOUT_S,
    )


def _recent_backup_ok() -> tuple[bool, str]:
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
    fp = int(client.execute(f"SELECT count() FROM {SRC_TABLE} WHERE {_FINGERPRINT}")[0][0])
    cross = int(client.execute(
        f"SELECT count() FROM {SRC_TABLE} WHERE {_FINGERPRINT} "
        "AND toMonth(publish_time + INTERVAL 8 HOUR) != toMonth(publish_time)"
    )[0][0])
    months = [r[0] for r in client.execute(sql_months())]
    log.info("指纹行 %d（其中跨月 %d）；月份数 %d（%s~%s）", fp, cross, len(months), months[0], months[-1])


def execute_rebuild(client) -> None:
    t_start_utc = datetime.now(tz=None).utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
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
        n = int(client.execute(
            f"SELECT count() FROM {REBUILD_TABLE} WHERE toYYYYMM(publish_time) = {m}"
        )[0][0])
        PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(PROGRESS_FILE, "a", encoding="utf-8") as f:
            f.write(f"{m}\n")
        log.info("%d 完成：本月落表 %d 行（含邻月跨入行；%.0f 秒）", m, n, time.time() - t0)

    # 全表对账（跨月敏感：源按 fixed_pt 归月 vs 目标按 publish_time 归月）
    src_sql, dst_sql = sql_verify_months()
    src_map = {int(r[0]): int(r[1]) for r in client.execute(src_sql)}
    dst_map = {int(r[0]): int(r[1]) for r in client.execute(dst_sql)}
    if src_map != dst_map:
        diff = {m: (src_map.get(m), dst_map.get(m)) for m in set(src_map) | set(dst_map)
                if src_map.get(m) != dst_map.get(m)}
        raise RuntimeError(f"全表对账不符（不换名，可重跑）: {diff}")
    log.info("全表对账通过（%d 月，总 %d 行）", len(dst_map), sum(dst_map.values()))

    log.info("原子换名...")
    client.execute(sql_rename_swap())
    delta = int(client.execute(
        f"SELECT count() FROM {OLD_TABLE} WHERE ingest_ts > toDateTime64('{t_start_utc}', 3, 'UTC')"
    )[0][0])
    if delta > 0:
        client.execute(sql_delta_backfill(t_start_utc))
        log.info("窗口期增量补捞 %d 行", delta)

    rows, ids, keys = client.execute(sql_final_verify())[0]
    log.info("终验：物理 %d 行 / %d id / %d 键", rows, ids, keys)
    fin = client.execute(f"SELECT count() FROM {SRC_TABLE} FINAL")[0][0]
    if fin != keys or ids != keys:
        raise RuntimeError(
            f"终验不符：FINAL {fin} vs 键 {keys} vs id {ids}（跨 INSERT 同键重复应被 FINAL 折叠；旧表仍在，可回滚换名）"
        )
    fp_left = int(client.execute(f"SELECT count() FROM {SRC_TABLE} WHERE {_FINGERPRINT}")[0][0])
    if fp_left != 0:
        raise RuntimeError(f"16:00 指纹残留 {fp_left} 行（应=0）")
    log.info("终验通过：FINAL==键数==id 数；16:00 指纹=0（物理 %d 行含 %d 行跨 INSERT 同键重复，merge 后自然折叠）",
             rows, rows - keys)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="news_data publish_time 8h 偏移换表修正（CAND-DAT-026）")
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
