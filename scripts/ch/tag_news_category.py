#!/usr/bin/env python
# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §4
# [MODULE] scripts.ch.tag_news_category
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_config; zephyr.shared.security.secrets; clickhouse-driver(lazy); zephyr.data.news_taxonomy
# [CONSUMERS] (治理 CLI，无模块消费者；产物=news_data.category 四分化)
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 幂等（重复执行零效果：规则命中条件排除已标行）；news 兜底只扫 category='general' 不覆盖三类特标；--dry-run 只报表不写库；mutation 后台执行轮询等待
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ClickHouse 不可达→exit 1；mutation 失败→exit 2
# [TESTS] tests/scripts/test_ch_tag_news_category.py
# [TTL] permanent
"""tag_news_category.py — CAND-DAT-024：news_data category 存量刷标（四分治理）。

分类法（按源确定，无需模型）：
  announcement     公告（巨潮/cninfo 等法定披露源）
  research_report  研报（akshare_research_report）
  macro_data       宏观数据（akshare_economic_baidu 等纯数据条目源）
  news             媒体新闻（其余全部，兜底）

政策=内容旗标（跨源，不进 category）——regime _POLICY_KEYWORDS 线已覆盖。

用法:
    python scripts/ch/tag_news_category.py --dry-run   # 只报各类待标行数
    python scripts/ch/tag_news_category.py             # 执行刷标（轮询 mutation 完成）

依据: CAND-DAT-024（candidate_module_registry.yaml v1.1.3）
"""

from __future__ import annotations

import argparse
import logging
import sys
import time

ROOT = __import__("pathlib").Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

from zephyr.data.ch_config import ensure_ch_env_loaded  # noqa: E402
from zephyr.shared.security.secrets import get_secret_or_default  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

_TBL = "c3_fundamental.news_data"
_REGION_LANG = "region = 'CN' AND language = 'zh'"

from zephyr.data.news_taxonomy import (  # noqa: E402
    SOURCES_ANNOUNCEMENT,
    SOURCES_MACRO_DATA,
    SOURCES_RESEARCH_REPORT,
)


def _src_in(sources: frozenset[str]) -> str:
    """源集合 → SQL IN 子句（单元素转等号）。"""
    quoted = ", ".join(f"'{s}'" for s in sorted(sources))
    return f"source IN ({quoted})"


# 四分规则（顺序敏感：特标先行，news 兜底只扫 general；源名单真源=zephyr.data.news_taxonomy）
RULES: list[tuple[str, str]] = [
    ("research_report", f"{_src_in(SOURCES_RESEARCH_REPORT)} AND category != 'research_report' AND {_REGION_LANG}"),
    ("announcement", f"{_src_in(SOURCES_ANNOUNCEMENT)} AND category != 'announcement' AND {_REGION_LANG}"),
    ("macro_data", f"{_src_in(SOURCES_MACRO_DATA)} AND category != 'macro_data' AND {_REGION_LANG}"),
    ("news", f"category = 'general' AND {_REGION_LANG}"),
]

_MUTATION_POLL_S = 10
_MUTATION_TIMEOUT_S = 7200


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


def count_rule(client, where: str) -> int:
    """单规则待标行数。"""
    return int(client.execute(f"SELECT count() FROM {_TBL} WHERE {where}")[0][0])


def apply_rule(client, category: str, where: str) -> None:
    """执行单条 ALTER UPDATE 并轮询 mutation 完成。"""
    log.info("刷标 %s ...", category)
    client.execute(f"ALTER TABLE {_TBL} UPDATE category = '{category}' WHERE {where}")
    t0 = time.time()
    while True:
        pending = client.execute("SELECT count() FROM system.mutations WHERE table = 'news_data' AND is_done = 0")[0][0]
        if pending == 0:
            log.info("%s 完成（%.0f 秒）", category, time.time() - t0)
            return
        if time.time() - t0 > _MUTATION_TIMEOUT_S:
            raise TimeoutError(f"mutation 超时未完成（{category}，pending={pending}）")
        log.info("等待 mutation 完成（pending=%d）...", pending)
        time.sleep(_MUTATION_POLL_S)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="news_data category 存量刷标（CAND-DAT-024）")
    parser.add_argument("--dry-run", action="store_true", help="只报各类待标行数，不写库")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    try:
        client = get_client()
        client.execute("SELECT 1")
    except Exception as exc:  # noqa: BLE001 — CH 不可达 fail-closed
        log.error("ClickHouse 不可达: %s", exc)
        sys.exit(1)

    for category, where in RULES:
        n = count_rule(client, where)
        log.info("规则 %-15s 待标 %s 行", category, f"{n:,}")
        if args.dry_run or n == 0:
            continue
        try:
            apply_rule(client, category, where)
        except Exception as exc:  # noqa: BLE001 — mutation 失败 fail-visible
            log.error("刷标失败（%s）: %s", category, exc)
            sys.exit(2)

    log.info("=== 刷标后分布 ===")
    for cat, n in client.execute(
        f"SELECT category, count() FROM {_TBL} WHERE {_REGION_LANG} GROUP BY category ORDER BY count() DESC"
    ):
        log.info("%-15s %s", cat, f"{n:,}")


if __name__ == "__main__":
    main()
