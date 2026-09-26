# [BLUEPRINT] MOD-METAQ-WO-A2LEGS-W2 | docs/_working/meta_question_answers/01_phase2_plan.md §数据施工需求清单(PQ-0013/0085/0040)
# [MODULE] scripts.governance.meta_question.wo_a2legs.backfill_sw_member_history
# [DOMAIN] D_DATA
# [DEPENDENCIES] tushare(index_classify/index_member, DS-TUSHARE 在册 2000 积分);
#                 zephyr.shared.security.secrets; zephyr.data.ch_writer (strict 写通道);
#                 zephyr.infrastructure.database_service (reader 复核); zephyr.shared.utils.time_utils
# [CONSUMERS] c1_market.sector_constituent_sw_history（新表：板块→个股 PIT 成分映射历史区间）
#             → PQ-0085 板块新高家数占比 / PQ-0013 板块合成强度 / PQ-0040 板块 CR5 聚合复考
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 写面三验证：必要性=现库 sector_constituent*/concept_board_constituent 仅 2026 单时点快照且
#              valid_from 无历史版本（闭卷窗 2021-01-04~2025-09-09 零成分可查）；
#              真实性=tushare 申万官方成分在/离任日期（实测 801010.SI 184 行含 80 条 is_new='N' 且
#              out_date 覆盖 2005-05-16~2026-07-01、in_date 最早 1993）；
#              可逆性=只建新表零触碰既有表，回滚=DROP 新表；
#              纯 INSERT 新增、禁 UPDATE/DELETE；分片幂等=按 index_code 断点续跑（已在库则 skip）；
#              限频自适应（权限/频控异常退避 15s 重试 3 次，仍失败记 skip 继续）；fail-visible 汇总非零退出。
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 单指数拉取失败→退避重试后记账 skip；写库失败→记账非零退出；末行 JSON 汇总。
# [TESTS] 无（数据施工脚本，验收=CH 探针复核 + 闭卷窗覆盖抽检）
# [A_module] module_id=MOD-METAQ-WO-A2LEGS-W2 | layer=script | stability=volatile | safety=M | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""申万板块→个股成分映射历史区间回填（tushare index_member，带 in_date/out_date PIT）。

用法：
    python scripts/governance/meta_question/wo_a2legs/backfill_sw_member_history.py [--levels L1,L2,L3]
                                                                    [--src SW2021] [--limit 0]
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import warnings
from datetime import date
from pathlib import Path

warnings.filterwarnings("ignore")
_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(_ROOT / "src"))

import tushare as ts  # noqa: E402

from zephyr.data import ch_writer  # noqa: E402
from zephyr.data.table_registry import TableRegistry  # noqa: E402
from zephyr.infrastructure.database_service import DatabaseService  # noqa: E402
from zephyr.shared.security.secrets import get_secret_or_default  # noqa: E402
from zephyr.shared.utils.time_utils import now_utc  # noqa: E402

#: 表名唯一真源 = TableRegistry 品类册（#ARCH-CH-024 Phase 5：禁硬编码全限定表名）
#: 本件目标表是在册成分表派生新表 → 注册表名 + 后缀拼接（求值文本与改前逐字一致）
_T_SECTOR_CONSTITUENT = TableRegistry().table("market_sector_constituent_880")
TBL = f"{_T_SECTOR_CONSTITUENT}_sw_history"
DDL = f"""
CREATE TABLE IF NOT EXISTS {TBL} (
    index_code    String               COMMENT '申万行业指数代码 801010.SI',
    index_name    String               COMMENT '行业名',
    level         LowCardinality(String) COMMENT '分类层级 L1/L2/L3',
    src_version   LowCardinality(String) COMMENT '分类版本 SW2021/SW2014（版本切换=口径分叉，必存）',
    con_code      String               COMMENT '成分股 ts_code',
    con_name      String               COMMENT '成分股名',
    in_date       Date                 COMMENT '进入该行业日期（PIT 区间起点）',
    out_date      Nullable(Date)       COMMENT '移出日期（NULL=至今有效）',
    is_new        LowCardinality(String) COMMENT 'Y=当前在册 N=历史在册（官方成分变更存证）',
    data_source   LowCardinality(String) COMMENT '渠道=tushare',
    fetched_at    DateTime64(3, 'UTC') COMMENT '本次抓取时刻',
    ingest_ts     DateTime64(3, 'UTC') COMMENT '入库时刻'
) ENGINE = ReplacingMergeTree(ingest_ts)
PARTITION BY src_version
ORDER BY (src_version, index_code, con_code, in_date)
COMMENT 'metaq WO-A2LEGS：申万板块→个股成分历史区间映射（闭卷窗 PIT 成分，真源=tushare index_member）'
"""
INSERT_COLS = [
    "index_code",
    "index_name",
    "level",
    "src_version",
    "con_code",
    "con_name",
    "in_date",
    "out_date",
    "is_new",
    "data_source",
    "fetched_at",
    "ingest_ts",
]

# NO-BARE-SQL：SQL 集中于此（§5.160.2）。{TBL}/INSERT_COLS 由模块常量注入；
# src_version 为运行期入参，用 %s 占位由调用方传入，禁把值写进常量。
_SQL_HAVE_INDEX_CODES = f"SELECT DISTINCT index_code FROM {TBL} WHERE src_version='%s'"
_SQL_INSERT_VALUES = f"INSERT INTO {TBL} ({', '.join(INSERT_COLS)}) VALUES"
_SQL_VERIFY = (
    f"SELECT count(), uniqExact(index_code), uniqExact(con_code), countIf(is_new='N'), "
    f"countIf(in_date <= '2025-09-09' AND (out_date IS NULL OR out_date >= '2021-01-04')) "
    f"FROM {TBL} FINAL WHERE src_version='%s'"
)


def _to_date(v) -> date | None:
    s = str(v).strip()
    if not s or s in ("NaT", "None", "nan"):
        return None
    s = s.replace("-", "")[:8]
    return date(int(s[:4]), int(s[4:6]), int(s[6:8]))


def _call(fn, *a, **kw):
    for attempt in range(3):
        try:
            return fn(*a, **kw)
        except Exception as exc:  # noqa: BLE001 — 限频/权限需区分重试
            msg = str(exc)
            if "每分钟" in msg or "频率超限" in msg or "限频" in msg or "最多访问" in msg:
                time.sleep(20)
                continue
            raise RuntimeError(msg[:200]) from exc
    raise RuntimeError("限频重试超限")


def _member_rows_for_code(pro, code, name, lvl, src, lvl_col, stats) -> list[list] | None:
    """单指数成分拉取（index_member 空→index_member_all 分层码兜底）→ 待插行集。

    两通道皆空返回 None（调用方记账 skip）；API 异常向上抛由调用方捕获记账；
    坏行（无 in_date / 无 con_code）按既定口径计入 skipped_index 不入行。
    """
    df = _call(pro.index_member, index_code=code, is_new="")
    src_api = "index_member"
    if df is None or len(df) == 0:
        # 非公开发布行业（index_classify.is_pub='0'）在 index_member 侧返回空，
        # 但 index_member_all 分层码口径有成分（2026-09-24 实测 850114.SI 4 行）→ 兜底
        df = _call(pro.index_member_all, **{lvl_col: code}, is_new="")
        src_api = "index_member_all"
    if df is None or len(df) == 0:
        return None
    now = now_utc()
    rows = []
    for _, r in df.iterrows():
        ind, outd = _to_date(r.get("in_date")), _to_date(r.get("out_date"))
        if ind is None:
            stats["skipped_index"] += 1
            continue
        con = str(r.get("con_code") or r.get("ts_code") or "")
        if not con:
            stats["skipped_index"] += 1
            continue
        rows.append(
            [
                code,
                name,
                lvl,
                src,
                con,
                str(r.get("name") or ""),
                ind,
                outd,
                str(r.get("is_new") or ""),
                f"tushare:{src_api}",
                now,
                now,
            ]
        )
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--levels", default="L1,L2,L3")
    ap.add_argument("--src", default="SW2021")
    ap.add_argument("--limit", type=int, default=0, help="仅取前 N 个指数（冒烟用）")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    tok = get_secret_or_default("TUSHARE_TOKEN")
    if not tok:
        raise SystemExit("TUSHARE_TOKEN 未配置")
    ts.set_token(tok)
    pro = ts.pro_api()
    client = ch_writer.get_client()
    reader = DatabaseService().get_clickhouse_conn(role="reader")
    client.execute(DDL)

    have = {str(r[0]) for r in reader.execute(_SQL_HAVE_INDEX_CODES % args.src)}
    stats = {"levels": {}, "rows_written": 0, "skipped_index": 0, "errors": []}
    for lvl in [x.strip() for x in args.levels.split(",") if x.strip()]:
        try:
            cls = _call(pro.index_classify, level=lvl, src=args.src)
        except Exception as exc:  # noqa: BLE001 — 版本/层级不可得如实登记不崩全批
            stats["levels"][lvl] = {"classified": 0, "error": str(exc)[:150]}
            continue
        names = dict(zip(cls.index_code.tolist(), cls.industry_name.tolist(), strict=True))
        stats["levels"][lvl] = {"classified": len(names)}
        codes = [c for c in names if c not in have]
        if args.limit:
            codes = codes[: args.limit]
        got = 0
        for code in codes:
            lvl_col = f"{lvl.lower()}_code"  # index_member_all 的分层码列名
            try:
                rows = _member_rows_for_code(pro, code, names.get(code, ""), lvl, args.src, lvl_col, stats)
            except Exception as exc:  # noqa: BLE001 — 单指数失败不阻断
                stats["errors"].append(f"{code}:{str(exc)[:120]}")
                continue
            if rows is None:
                stats["skipped_index"] += 1
                stats.setdefault("empty_codes", []).append(code)
                continue
            if args.dry_run:
                got += len(rows)
                continue
            if rows:
                client.execute(_SQL_INSERT_VALUES, rows, types_check=True)
                got += len(rows)
            time.sleep(0.32)
        stats["levels"][lvl]["rows_written"] = got
        stats["rows_written"] += got
    chk = reader.execute(
        f"SELECT count(), uniqExact(index_code), uniqExact(con_code), countIf(is_new='N'), "
        f"countIf(in_date <= '2025-09-09' AND (out_date IS NULL OR out_date >= '2021-01-04')) "
        f"FROM {TBL} FINAL WHERE src_version='{args.src}'"
    )[0]
    stats["verify"] = {
        "rows": chk[0],
        "indices": chk[1],
        "cons": chk[2],
        "historic_out_rows": chk[3],
        "rows_pit_useful": chk[4],
        "total_index_codes": len(have) + sum(v.get("classified", 0) for v in stats["levels"].values()),
    }
    print(json.dumps(stats, ensure_ascii=False, default=str)[:2000])
    if stats["errors"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
