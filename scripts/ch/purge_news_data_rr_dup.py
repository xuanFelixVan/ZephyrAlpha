#!/usr/bin/env python
# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §4
# [MODULE] scripts.ch.purge_news_data_rr_dup
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_config; zephyr.shared.security.secrets; clickhouse-driver(lazy)
# [CONSUMERS] (治理 CLI，无模块消费者；产物=news_data research_report 物理去重)
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 一次性清扫（design_memos/67_news_data_dedup_design.md §2②）；幂等（集合现算，重跑已删查不到）；不丢数据（仅删"有新版本行"的 id 的老批行）；--dry-run 只报不写；破坏性执行需近 24h 备份；mutation 后台轮询
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH 不可达→exit 1；写入/mutation 失败→exit 2；无近 24h 备份→exit 3
# [TESTS] tests/scripts/test_ch_purge_news_data_rr_dup.py
# [TTL] permanent
"""purge_news_data_rr_dup.py — CAND-DAT-025：news_data 研报多版本冗余一次性清扫。

根因（67 号设计备忘 §1.2）：同一新闻新老两批 publish_time 时区语义漂移
（老批偏 8h，16:00 指纹），ORDER BY (news_id, publish_time) 键不同，
ReplacingMergeTree 永不折叠 → research_report 稳定 2.0x 冗余（290,433 行 / 146,519 id）。

两步（execute）：
  1. 老批单行 id（无新版本对照）按 +8h 修正重插（版本列 now64(3)，防直删丢数据）
  2. ALTER DELETE 删除"有新版本行"的 id 的老批行（mutation 轮询等待）

用法:
    python scripts/ch/purge_news_data_rr_dup.py --dry-run   # 对账输出，0 写入
    python scripts/ch/purge_news_data_rr_dup.py --execute   # 正式清扫（近 24h 备份前置）
    python scripts/ch/purge_news_data_rr_dup.py --execute --no-backup-check  # 跳过备份检查（不推荐）

依据: CAND-DAT-025（candidate_module_registry.yaml）；design_memos/67_news_data_dedup_design.md
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from datetime import datetime, timedelta

ROOT = __import__("pathlib").Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

from zephyr.data.ch_config import ensure_ch_env_loaded  # noqa: E402
from zephyr.shared.security.secrets import get_secret_or_default  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

_TBL = "c3_fundamental.news_data"
# 新老批 ingest_ts 分界（UTC）：2026-08-01 后为重写新批（publish_time 语义正确）
CUTOFF = "2026-08-01 00:00:00"

_MUTATION_POLL_S = 15
_MUTATION_TIMEOUT_S = 7200

# news_data 全列清单（system.columns 实测 29 列）——修正重插必须全列显式，
# 缺列会被 DEFAULT 覆盖造成字段级数据丢失
FIX_INSERT_COLUMNS: list[str] = [
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

_SINGLE_ROW_IDS = f"SELECT news_id FROM {_TBL} WHERE category = 'research_report' GROUP BY news_id HAVING count() = 1"


def sql_orphan_where() -> str:
    """老批单行谓词（待 +8h 修正重插的行）。"""
    return (
        f"category = 'research_report' AND ingest_ts < toDateTime('{CUTOFF}', 'UTC') AND news_id IN ({_SINGLE_ROW_IDS})"
    )


def sql_fix_orphan_insert() -> str:
    """老批单行修正重插：publish_time +8h（full_publish_time 默认值守卫），版本列取当前。"""
    select_exprs = []
    for col in FIX_INSERT_COLUMNS:
        if col == "publish_time":
            select_exprs.append("publish_time + INTERVAL 8 HOUR")
        elif col == "full_publish_time":
            select_exprs.append(
                "if(toUnixTimestamp(full_publish_time) > 86400, full_publish_time + INTERVAL 8 HOUR, full_publish_time)"
            )
        elif col == "ingest_ts":
            select_exprs.append("now64(3)")
        else:
            select_exprs.append(col)
    return (
        f"INSERT INTO {_TBL} ({', '.join(FIX_INSERT_COLUMNS)}) "
        f"SELECT {', '.join(select_exprs)} FROM {_TBL} WHERE {sql_orphan_where()} "
        "SETTINGS max_partitions_per_insert_block = 100000"  # 单行老批跨 2010-2026 全月分区（一次性修正，行数小）
    )


def sql_delete_old_rows() -> str:
    """删老留新：仅删"有新版本行"的 id 的老批行（子查询 HAVING 守卫防全老批 id 被删光）。

    内联子查询（非临时表）：writer 角色无 TRUNCATE/DROP 授权（2026-08-27 实证），
    且 IN 集在 mutation 启动时一次性物化，与同表后续删除无竞态。
    """
    return (
        f"ALTER TABLE {_TBL} DELETE "
        "WHERE category = 'research_report' "
        f"AND ingest_ts < toDateTime('{CUTOFF}', 'UTC') "
        f"AND news_id IN (SELECT news_id FROM {_TBL} WHERE category = 'research_report' "
        f"GROUP BY news_id HAVING count() > 1 "
        f"AND countIf(ingest_ts >= toDateTime('{CUTOFF}', 'UTC')) >= 1)"
    )


def sql_dry_counts() -> list[tuple[str, str]]:
    """对账四件套（dry-run/execute 前共用）。"""
    return [
        (
            "dup_ids",
            f"SELECT count() FROM (SELECT news_id FROM {_TBL} WHERE category = 'research_report' "
            f"GROUP BY news_id HAVING count() > 1 "
            f"AND countIf(ingest_ts >= toDateTime('{CUTOFF}', 'UTC')) >= 1)",
        ),
        (
            "delete_rows",
            f"SELECT count() FROM {_TBL} WHERE category = 'research_report' "
            f"AND ingest_ts < toDateTime('{CUTOFF}', 'UTC') "
            f"AND news_id IN (SELECT news_id FROM {_TBL} WHERE category = 'research_report' "
            f"GROUP BY news_id HAVING count() > 1 "
            f"AND countIf(ingest_ts >= toDateTime('{CUTOFF}', 'UTC')) >= 1)",
        ),
        ("orphan_fix_rows", f"SELECT count() FROM {_TBL} WHERE {sql_orphan_where()}"),
        (
            "stuck_old_only_ids",
            f"SELECT count() FROM (SELECT news_id FROM {_TBL} WHERE category = 'research_report' "
            f"GROUP BY news_id HAVING count() > 1 "
            f"AND countIf(ingest_ts >= toDateTime('{CUTOFF}', 'UTC')) = 0)",
        ),
    ]


def recent_backup_ok(state: dict, now: datetime) -> tuple[bool, str]:
    """近 24h 成功 CH 备份检查（破坏性操作前置防线）。

    真源=data/databases/backup_state.json（backup.ps1 管线维护，
    last_ch_backup_time 仅成功时推进）——system.backups 在本部署为空
    （备份走 VM 侧 SSH 链路，不登记 SQL BACKUP 记录，2026-08-27 实证）。
    """
    ts = state.get("last_ch_backup_time")
    if not ts or not state.get("last_ch_backup_verified"):
        return (False, "无成功 CH 备份记录（backup_state.json）")
    try:
        t = datetime.fromisoformat(str(ts))
    except ValueError:
        return (False, f"backup_state.json 时间戳无法解析: {ts!r}")
    if t.tzinfo is None:
        t = t.astimezone()  # naive 按本机时区（backup.ps1 实际写 +08:00，防御性兜底）
    if now - t > timedelta(hours=24):
        return (False, f"最近 CH 备份已超 24h（{ts}）")
    return (True, f"最近成功备份 {ts}（verified）")


def _load_backup_state() -> dict:
    path = ROOT / "data" / "databases" / "backup_state.json"
    if not path.exists():
        return {}
    import json

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def get_client():
    """clickhouse-driver TCP 客户端（配置真源 config/.env.clickhouse）。"""
    import clickhouse_driver  # noqa: PLC0415 — lazy

    ensure_ch_env_loaded()
    return clickhouse_driver.Client(
        host=get_secret_or_default("CLICKHOUSE_HOST", ""),
        port=int(get_secret_or_default("CLICKHOUSE_PORT", "9000")),
        user=get_secret_or_default("CLICKHOUSE_WRITER_USER") or get_secret_or_default("CLICKHOUSE_USER", "default"),
        password=get_secret_or_default("CLICKHOUSE_WRITER_PASSWORD")
        or get_secret_or_default("CLICKHOUSE_PASSWORD", ""),
        send_receive_timeout=_MUTATION_TIMEOUT_S,
    )


def report_counts(client) -> dict[str, int]:
    """对账输出（dry-run 与 execute 前置共用）。"""
    counts: dict[str, int] = {}
    for name, sql in sql_dry_counts():
        counts[name] = int(client.execute(sql)[0][0])
    log.info(
        "对账：双版本 id %d 个（待删老行 %d 行）；老批单行待修正 %d 行；全老批残留 id %d 个（不触碰）",
        counts["dup_ids"],
        counts["delete_rows"],
        counts["orphan_fix_rows"],
        counts["stuck_old_only_ids"],
    )
    return counts


def wait_mutations(client) -> None:
    """轮询 news_data mutation 完成。"""
    t0 = time.time()
    while True:
        pending = client.execute("SELECT count() FROM system.mutations WHERE table = 'news_data' AND is_done = 0")[0][0]
        if pending == 0:
            log.info("mutation 完成（%.0f 秒）", time.time() - t0)
            return
        if time.time() - t0 > _MUTATION_TIMEOUT_S:
            raise TimeoutError(f"mutation 超时未完成（pending={pending}）")
        log.info("等待 mutation 完成（pending=%d）...", pending)
        time.sleep(_MUTATION_POLL_S)


def execute_purge(client, counts: dict[str, int]) -> None:
    """正式清扫：修正重插 → 删老留新 → 自验证。

    计数契约：后台 merge 会实时改变单行/双行集合归属（同键物理重复被折叠），
    故成功判据用"谓词清零"而非"行数相等"（幂等且对 merge 竞态免疫）。
    """
    # ① 老批单行 +8h 修正重插
    if counts["orphan_fix_rows"] > 0:
        client.execute(sql_fix_orphan_insert())
        remaining = int(client.execute(f"SELECT count() FROM {_TBL} WHERE {sql_orphan_where()}")[0][0])
        if remaining != 0:
            raise RuntimeError(f"修正重插后仍有 {remaining} 行老批单行未处理")
        log.info("老批单行修正重插完成（%d 行，谓词已清零）", counts["orphan_fix_rows"])
    else:
        log.info("无老批单行待修正，跳过重插")

    # ② 删老留新（ALTER DELETE mutation，IN 集内联物化）
    n_ids = int(
        client.execute(
            f"SELECT count() FROM (SELECT news_id FROM {_TBL} WHERE category = 'research_report' "
            f"GROUP BY news_id HAVING count() > 1 "
            f"AND countIf(ingest_ts >= toDateTime('{CUTOFF}', 'UTC')) >= 1)"
        )[0][0]
    )
    log.info("删除目标 id 集 %d 个，提交 ALTER DELETE mutation...", n_ids)
    if n_ids > 0:
        client.execute(sql_delete_old_rows())
        wait_mutations(client)

    # ③ 自验证：删除目标清零 + 行数/唯一 id 对账
    stuck = int(
        client.execute(
            f"SELECT count() FROM {_TBL} WHERE category = 'research_report' "
            f"AND ingest_ts < toDateTime('{CUTOFF}', 'UTC') "
            f"AND news_id IN (SELECT news_id FROM {_TBL} WHERE category = 'research_report' "
            f"GROUP BY news_id HAVING count() > 1 "
            f"AND countIf(ingest_ts >= toDateTime('{CUTOFF}', 'UTC')) >= 1)"
        )[0][0]
    )
    if stuck != 0:
        raise RuntimeError(f"自验证失败：仍有 {stuck} 行待删老批行残留")
    rows, uniq = client.execute(f"SELECT count(), uniqExact(news_id) FROM {_TBL} WHERE category = 'research_report'")[0]
    log.info("自验证通过：research_report %d 行 / %d 唯一 id（残留差=全老批多行 id，见对账）", rows, uniq)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="news_data 研报多版本冗余一次性清扫（CAND-DAT-025）")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="只对账输出，0 写入")
    mode.add_argument("--execute", action="store_true", help="正式清扫（近 24h 备份前置）")
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

    counts = report_counts(client)
    if args.dry_run:
        log.info("dry-run 完成，0 写入")
        return

    if not args.no_backup_check:
        ok, msg = recent_backup_ok(_load_backup_state(), datetime.now().astimezone())
        log.info("备份检查：%s", msg)
        if not ok:
            log.error("近 24h 无成功 CH 备份，拒绝破坏性执行（--no-backup-check 跳过，不推荐）")
            sys.exit(3)

    try:
        execute_purge(client, counts)
    except Exception as exc:  # noqa: BLE001 — 失败现场保留于日志
        log.error("清扫失败: %s", exc)
        sys.exit(2)
    log.info("清扫完成")


if __name__ == "__main__":
    main()
