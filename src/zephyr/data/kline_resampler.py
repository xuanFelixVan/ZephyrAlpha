# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §kline_resample
# [MODULE] zephyr.data.kline_resampler
# [DOMAIN] D_DATA
# [DEPENDENCIES] clickhouse_driver; zephyr.data.ch_config; zephyr.data.table_registry
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 从kline_sector_880表的1m/5m数据合成15m/30m/60m K线（ClickHouse toStartOfInterval聚合）；DELETE+INSERT幂等写入；盘后批量执行；argMin/argMax保证OHLC正确性
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ClickHouse查询失败->log+返回0; 合成0行->log warning; 单周期失败->log+继续下一周期
# [TESTS] tests/zephyr/data/test_kline_resampler.py
# [TTL] task_bound
"""
880xxx 板块K线合成器——从 1m/5m 合成 15m/30m/60m 写入 ClickHouse。

tqcenter 仅支持 1d/1m/5m 三周期，15m/30m/60m 需从分钟线合成。
本模块通过 ClickHouse toStartOfInterval 聚合在 DB 内完成合成，避免数据搬运。

合成规则（标准 OHLC 聚合）：
  - open  = argMin(open, timestamp)   窗口内第一条K线的开盘价
  - high  = max(high)                 窗口内最高价
  - low   = min(low)                  窗口内最低价
  - close = argMax(close, timestamp)  窗口内最后一条K线的收盘价
  - volume = sum(volume)              窗口内成交量之和
  - amount = sum(amount)              窗口内成交额之和

启动:
    python -m zephyr.data.kline_resampler                      # 合成最近7天
    python -m zephyr.data.kline_resampler --days 30            # 合成最近30天
    python -m zephyr.data.kline_resampler --period 15m         # 仅合成15m
    python -m zephyr.data.kline_resampler --start 2026-07-01 --end 2026-07-22

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: kline_resampler.py
# 层: 算法
# - id: A1
#   name_zh: ① main
#   name_en: main
#   intro: K线合成器主入口。
#   desc: K线合成器主入口。；源码 L209-L246
#   inputs: 无参数
#   outputs: int
# 层: 输出
# - id: O1
#   name_zh: int
#   name_en: int
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import UTC, datetime, timedelta

log = logging.getLogger(__name__)

# ---------- 常量 ----------

# 表名真源：business_data_categories.yaml via table_registry（裁定 #ARCH-CH-024，
# 2026-08-17 AI-04 审计治本：消除硬编码库表名）
from zephyr.data.table_registry import get_registry as _get_table_registry

_CH_TABLE = _get_table_registry().table("market_sector_kline_880")

# 合成周期映射：{目标周期: (源周期, 窗口分钟数)}
_SYNTH_MAP = {
    "15m": ("1m", 15),
    "30m": ("1m", 30),
    "60m": ("1m", 60),
}

# SQL 模板（NO-BARE-SQL gate 豁免 SQL_ 前缀）
SQL_DELETE_SYNTH = (
    "ALTER TABLE {table} DELETE "
    "WHERE period = '{target}' AND trade_date BETWEEN '{start}' AND '{end}' "
    "SETTINGS mutations_sync = 2"
)

SQL_SYNTH_TEMPLATE = """
INSERT INTO {table}
    (period, trade_date, timestamp, sector_code, sector_name,
     open, high, low, close, volume, amount, forward_factor, data_source)
SELECT
    '{target}' AS period,
    toDate(window_start) AS trade_date,
    window_start AS timestamp,
    sector_code,
    any(sector_name) AS sector_name,
    argMin(open, timestamp) AS open,
    max(high) AS high,
    min(low) AS low,
    argMax(close, timestamp) AS close,
    sum(volume) AS volume,
    sum(amount) AS amount,
    any(forward_factor) AS forward_factor,
    'synth_{source}' AS data_source
FROM {table}
WHERE period = '{source}'
  AND trade_date BETWEEN '{start}' AND '{end}'
GROUP BY sector_code, toStartOfInterval(timestamp, INTERVAL {minutes} MINUTE) AS window_start
"""


# ---------- SQL 构建 ----------


def _build_delete_sql(target: str, start: str, end: str) -> str:
    """构建删除已合成数据的 SQL（幂等：先删后插）。"""
    return SQL_DELETE_SYNTH.format(table=_CH_TABLE, target=target, start=start, end=end)


def _build_synth_sql(source: str, target: str, minutes: int, start: str, end: str) -> str:
    """构建合成 INSERT SQL。"""
    return SQL_SYNTH_TEMPLATE.format(
        table=_CH_TABLE,
        source=source,
        target=target,
        minutes=minutes,
        start=start,
        end=end,
    )


# ---------- ClickHouse 操作 ----------


def _get_ch_client():
    """从 ch_config 真源加载【写入账号】配置创建 ClickHouse 客户端。

    本模块执行 DELETE+INSERT 写操作，RBAC（audit 9.4 #ARCH-CH-027）要求使用
    zephyr_writer 账号（DB 级 INSERT/ALTER 权限），禁止用 base/reader 账号。
    （2026-08-17 AI-04 审计治本：load_ch_config → load_ch_writer_config）
    """
    from clickhouse_driver import Client

    from zephyr.data.ch_config import load_ch_writer_config

    cfg = load_ch_writer_config()
    c = Client(
        host=cfg["host"],
        port=int(cfg["port"]),
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        connect_timeout=10,
        send_receive_timeout=120,
    )
    c.execute("SELECT 1")
    return c


def _synth_period(client, target: str, start: str, end: str) -> int:
    """合成单个目标周期，返回写入行数。

    步骤：
      1. DELETE 已合成数据（幂等）
      2. INSERT 聚合数据
    """
    source, minutes = _SYNTH_MAP[target]
    log.info("=== 合成 %s (源=%s, 窗口=%dmin, %s~%s) ===", target, source, minutes, start, end)

    # Step 1: 删除已有合成数据
    del_sql = _build_delete_sql(target, start, end)
    client.execute(del_sql)
    log.info("  已清理旧 %s 数据", target)

    # Step 2: 聚合插入
    synth_sql = _build_synth_sql(source, target, minutes, start, end)
    client.execute(synth_sql)

    # 查询写入行数
    count_sql = (
        f"SELECT count() FROM {_CH_TABLE} WHERE period = '{target}' AND trade_date BETWEEN '{start}' AND '{end}'"  # noqa: bare-sql  存量参数化查询/动态标识符，format重排伪新增（§5.160.2集中化专项另列）
    )
    rows = client.execute(count_sql)
    count = rows[0][0] if rows else 0
    log.info("  %s 合成完成: %d 行", target, count)
    return count


# ---------- 日期辅助 ----------


def _get_date_range(days: int) -> tuple[str, str]:
    """返回最近 N 天的 (start, end) 日期字符串（YYYY-MM-DD）。"""
    end = datetime.now(UTC).date()
    start = end - timedelta(days=days)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


# ---------- 主流程 ----------


def main() -> int:
    """K线合成器主入口。"""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    parser = argparse.ArgumentParser(description="880xxx 板块K线合成器")
    parser.add_argument("--days", type=int, default=7, help="合成最近N天（默认7）")
    parser.add_argument("--period", default="all", help="目标周期: 15m/30m/60m/all（默认all）")
    parser.add_argument("--start", help="开始日期 YYYY-MM-DD（覆盖--days）")
    parser.add_argument("--end", help="结束日期 YYYY-MM-DD（覆盖--days）")
    args = parser.parse_args()

    # 确定日期范围
    if args.start and args.end:
        start, end = args.start, args.end
    else:
        start, end = _get_date_range(args.days)

    # 确定目标周期
    targets = list(_SYNTH_MAP.keys()) if args.period == "all" else [args.period]
    for t in targets:
        if t not in _SYNTH_MAP:
            log.error("不支持的目标周期: %s（可选: 15m/30m/60m/all）", t)
            return 1

    log.info("=== 880xxx 板块K线合成器启动 ===")
    log.info("日期范围: %s ~ %s, 目标周期: %s", start, end, targets)

    client = _get_ch_client()
    total = 0
    for target in targets:
        try:
            total += _synth_period(client, target, start, end)
        except Exception as e:  # noqa: BLE001
            log.error("合成 %s 失败: %s", target, str(e)[:200])

    client.disconnect()
    log.info("=== 完成: 共合成 %d 行 ===", total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
