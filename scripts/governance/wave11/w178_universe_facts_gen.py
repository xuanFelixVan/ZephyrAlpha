#!/usr/bin/env python
# create-guard-not-dup: 死车道抢救件（字节代投非新能力），与canonical同名能力无职责重叠，逐词误报批量豁免（st-chief7-20260928 第12+轮实测均为关键词巧合命中）
# [TTL] task_bound
# [STARTUP] manual
#   （原值 on_demand： 施工队命令行调用（见案卷 §通道），无常驻调度——GATE-VOCAB 词表归正 manual）
# [MODULE] module_id=MOD-GOV-wave11-w178-facts-gen | layer=script | safety=L | ai_autonomy=ai_modifiable
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] stdlib(subprocess/json/re/datetime/pathlib/collections)；yaml；zephyr.data.ch_reader(严格通道)
# [CONSUMERS] docs/_working/total_command_closeout/wave11/w178_sector_universe_strict.md
# [MATURITY] draft
# [INVARIANTS] 只读 SELECT，禁一切 DDL/DML；每条读数双探测（ch_probe 标准探针 + query_rows）互证；
#              探测失败必记 outcome=fail 并保留失败原文，禁降级为 0/空表；输出机生禁手改
# [BLUEPRINT] MOD-DATA_SUPPLY | docs/03_modules/_domain_data/data_supply/blueprint.md | §w178_universe_facts
# [MODIFY-GUARD] 判据口径（宇宙定义/LIKE 前缀/双探测要求）变更须同步案卷 w178_sector_universe_strict.md 与 92 册尺，禁单独放宽
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 依赖失败必抛并点名，禁把异常吞成空值
# [TESTS] 案卷内附命令原文与实测读数，可复算
"""W-178 板块宇宙 strict 复测机生表生成器（产物=w178_universe_facts.yaml + probe JSONL）.

大白话：把"板块宇宙到底有多大、谁有行情没成分、两套口径差多少"一次测清楚，
并且每个数字都带上"我走的哪条传输通道、几点几分测的"，失败就红着写，不许写 0。

用法（车道内，必须先注入 CH 配置到 os.environ，禁写 config 文件）：
    export PATH="/c/Users/fanzi/AppData/Local/Programs/Python/Python312:...Scripts:$PATH"
    cd D:/ZephyrAlpha/.aidrafts/st-final-build-20260926
    set -a; . /d/ZephyrAlpha/config/.env.clickhouse; set +a
    PYTHONPATH=$PWD/src python scripts/governance/wave11/w178_universe_facts_gen.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from zephyr.shared.infra.process_pool import run_subprocess_hidden  # TRAE-067 无窗口统一入口

_HERE = Path(__file__).resolve().parent  # .../scripts/governance/wave11
_ROOT = _HERE.parents[2]  # 仓根（主区或本车道，随本件所在树走）
_DOC_DIR = _ROOT / "docs/_working/total_command_closeout/wave11"
assert (_ROOT / "scripts").is_dir(), f"仓根推断失手: {_ROOT}"
_PROBE = _ROOT / "scripts" / "governance" / "data_supply" / "ch_probe.py"
assert _PROBE.is_file(), f"标准探针不在位: {_PROBE}"
sys.path.insert(0, str(_ROOT / "src"))

import yaml  # noqa: E402

from zephyr.data import ch_reader, ch_writer  # noqa: E402

DB = "c1_market"
OUT_YAML = _DOC_DIR / "w178_universe_facts.yaml"
OUT_DIR = _ROOT / ".runtime/tmp/w178_probe"  # 跑批转录件＝非交付面（docs/_working 禁 .sql/.json，DCR-005/008）


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ── 只读 SQL 清单：kind=scalar(1x1) / onerow(1xN) / set(多行，取首列全集) / agg(多行聚合) ──
_SQL_QUERIES = [  # list[tuple[name, kind, sql]]
    # A. strict 现值
    (
        "sc_880_boards",
        "scalar",
        f"SELECT count(DISTINCT sector_code) FROM {DB}.sector_constituent WHERE sector_code LIKE '880%'",
    ),
    ("sc_880_rows", "scalar", f"SELECT count() FROM {DB}.sector_constituent WHERE sector_code LIKE '880%'"),
    (
        "sc_881_boards",
        "scalar",
        f"SELECT count(DISTINCT sector_code) FROM {DB}.sector_constituent WHERE sector_code LIKE '881%'",
    ),
    ("sc_881_rows", "scalar", f"SELECT count() FROM {DB}.sector_constituent WHERE sector_code LIKE '881%'"),
    ("sc_all_boards", "scalar", f"SELECT count(DISTINCT sector_code) FROM {DB}.sector_constituent"),
    ("sc_all_rows", "scalar", f"SELECT count() FROM {DB}.sector_constituent"),
    ("kl880_distinct_boards", "scalar", f"SELECT count(DISTINCT sector_code) FROM {DB}.kline_sector_880"),
    ("kl880_rows", "scalar", f"SELECT count() FROM {DB}.kline_sector_880"),
    ("cb_rows", "scalar", f"SELECT count() FROM {DB}.concept_board"),
    ("cb_boards", "scalar", f"SELECT count(DISTINCT board_code) FROM {DB}.concept_board"),
    ("cbc_rows", "scalar", f"SELECT count() FROM {DB}.concept_board_constituent"),
    ("cbc_boards", "scalar", f"SELECT count(DISTINCT board_code) FROM {DB}.concept_board_constituent"),
    ("sl_rows", "scalar", f"SELECT count() FROM {DB}.sector_list"),
    ("sl_sector_names", "scalar", f"SELECT count(DISTINCT sector_name) FROM {DB}.sector_list"),
    ("sl_symbols", "scalar", f"SELECT count(DISTINCT symbol_canonical) FROM {DB}.sector_list"),
    # B. gap 现值 + 新鲜度（业务表列，禁 system. 面）
    #    注：Date/DateTime/Decimal 一律 toString() 包裹——ch_probe 的 first_row_sample 走
    #    json.dumps，未转的 date 对象会把整批 42 条探针一起打挂（本机实测，已立案卷 §A.0b）。
    (
        "gap_sql_880",
        "scalar",
        "SELECT count() FROM (SELECT DISTINCT sector_code FROM "
        f"{DB}.kline_sector_880 WHERE sector_code LIKE '880%') WHERE sector_code NOT IN "
        f"(SELECT DISTINCT sector_code FROM {DB}.sector_constituent WHERE sector_code LIKE '880%')",
    ),
    (
        "gap_sql_881",
        "scalar",
        "SELECT count() FROM (SELECT DISTINCT sector_code FROM "
        f"{DB}.kline_sector_880 WHERE sector_code LIKE '881%') WHERE sector_code NOT IN "
        f"(SELECT DISTINCT sector_code FROM {DB}.sector_constituent WHERE sector_code LIKE '881%')",
    ),
    (
        "sc880_named_boards",
        "scalar",
        f"SELECT count(DISTINCT sector_code) FROM {DB}.sector_constituent "
        "WHERE sector_code LIKE '880%' AND sector_name <> '' AND sector_name NOT LIKE '880%'",
    ),
    ("sl_names", "set", f"SELECT DISTINCT sector_name FROM {DB}.sector_list ORDER BY sector_name"),
    (
        "sl_profile",
        "agg",
        f"SELECT exchange, data_source, count(DISTINCT symbol_canonical), count() FROM {DB}.sector_list GROUP BY exchange, data_source ORDER BY exchange, data_source",
    ),
    (
        "sc_880_fresh",
        "onerow",
        f"SELECT toString(max(update_date)), toString(max(valid_from)), toString(max(valid_to)), toString(max(fetched_at)), toString(max(ingest_ts)) FROM {DB}.sector_constituent WHERE sector_code LIKE '880%'",
    ),
    (
        "sc_881_fresh",
        "onerow",
        f"SELECT toString(max(update_date)), toString(max(valid_from)), toString(max(valid_to)) FROM {DB}.sector_constituent WHERE sector_code LIKE '881%'",
    ),
    (
        "kl880_fresh",
        "onerow",
        f"SELECT toString(max(trade_date)), count(DISTINCT period), any(period) FROM {DB}.kline_sector_880",
    ),
    (
        "cb_fresh",
        "onerow",
        f"SELECT toString(max(valid_from)), toString(max(valid_to)), toString(max(updated_at)) FROM {DB}.concept_board",
    ),
    (
        "cbc_fresh",
        "onerow",
        f"SELECT toString(max(valid_from)), toString(max(valid_to)), toString(max(updated_at)) FROM {DB}.concept_board_constituent",
    ),
    ("sl_fresh", "onerow", f"SELECT toString(max(trade_date)), toString(max(updated_at)) FROM {DB}.sector_list"),
    # C. 集合与粒度
    (
        "kl880_prefix",
        "agg",
        f"SELECT substring(sector_code,1,3) AS p, count(DISTINCT sector_code), count() FROM {DB}.kline_sector_880 GROUP BY p ORDER BY p",
    ),
    (
        "sc_prefix",
        "agg",
        f"SELECT substring(sector_code,1,3) AS p, count(DISTINCT sector_code), count() FROM {DB}.sector_constituent GROUP BY p ORDER BY p",
    ),
    (
        "sc_880_source",
        "agg",
        f"SELECT data_source, count(DISTINCT sector_code), count() FROM {DB}.sector_constituent WHERE sector_code LIKE '880%' GROUP BY data_source ORDER BY data_source",
    ),
    (
        "cb_source",
        "agg",
        f"SELECT data_source, count(DISTINCT board_code), count() FROM {DB}.concept_board GROUP BY data_source ORDER BY data_source",
    ),
    (
        "cbc_source",
        "agg",
        f"SELECT data_source, count(DISTINCT board_code), count() FROM {DB}.concept_board_constituent GROUP BY data_source ORDER BY data_source",
    ),
    (
        "sc_880_avg_size",
        "onerow",
        f"SELECT toString(avg(c)) FROM (SELECT count() AS c FROM {DB}.sector_constituent WHERE sector_code LIKE '880%' GROUP BY sector_code)",
    ),
    (
        "cbc_avg_size",
        "onerow",
        f"SELECT toString(avg(c)) FROM (SELECT count() AS c FROM {DB}.concept_board_constituent GROUP BY board_code)",
    ),
    (
        "sc_880_stock_universe",
        "scalar",
        f"SELECT count(DISTINCT stock_code) FROM {DB}.sector_constituent WHERE sector_code LIKE '880%'",
    ),
    ("cbc_stock_universe", "scalar", f"SELECT count(DISTINCT symbol_canonical) FROM {DB}.concept_board_constituent"),
    # 补齐通道面：Phase 2 快照表 / 名册映射表 / 第三张概念名册
    ("scsnap_rows", "scalar", f"SELECT count() FROM {DB}.sector_constituent_snapshot"),
    (
        "scsnap_880_boards",
        "scalar",
        f"SELECT count(DISTINCT sector_code) FROM {DB}.sector_constituent_snapshot WHERE sector_code LIKE '880%'",
    ),
    (
        "scsnap_fresh",
        "onerow",
        f"SELECT toString(max(snapshot_date)), toString(min(snapshot_date)), count(DISTINCT snapshot_date) FROM {DB}.sector_constituent_snapshot",
    ),
    ("name_map_rows", "scalar", f"SELECT count() FROM {DB}.sector_code_name_map"),
    (
        "name_map_880_boards",
        "scalar",
        f"SELECT count(DISTINCT sector_code) FROM {DB}.sector_code_name_map WHERE sector_code LIKE '880%'",
    ),
    (
        "name_map_fresh",
        "onerow",
        f"SELECT toString(max(ingest_ts)), toString(min(ingest_ts)) FROM {DB}.sector_code_name_map",
    ),
    ("concept_sector_rows", "scalar", f"SELECT count() FROM {DB}.concept_sector"),
    (
        "SET_scsnap880",
        "set",
        f"SELECT DISTINCT sector_code FROM {DB}.sector_constituent_snapshot WHERE sector_code LIKE '880%' ORDER BY sector_code",
    ),
    (
        "SET_namemap880",
        "set",
        f"SELECT DISTINCT sector_code FROM {DB}.sector_code_name_map WHERE sector_code LIKE '880%' ORDER BY sector_code",
    ),
    ("SET_concept_sector", "set", f"SELECT DISTINCT sector_code FROM {DB}.concept_sector ORDER BY sector_code"),
    # 集合成品（取首列全集，供 python 侧集合差＝第二探测）
    (
        "SET_kl880",
        "set",
        f"SELECT DISTINCT sector_code FROM {DB}.kline_sector_880 WHERE sector_code LIKE '880%' ORDER BY sector_code",
    ),
    (
        "SET_kl881",
        "set",
        f"SELECT DISTINCT sector_code FROM {DB}.kline_sector_880 WHERE sector_code LIKE '881%' ORDER BY sector_code",
    ),
    (
        "SET_sc880",
        "set",
        f"SELECT DISTINCT sector_code FROM {DB}.sector_constituent WHERE sector_code LIKE '880%' ORDER BY sector_code",
    ),
    (
        "SET_sc881",
        "set",
        f"SELECT DISTINCT sector_code FROM {DB}.sector_constituent WHERE sector_code LIKE '881%' ORDER BY sector_code",
    ),
    ("SET_cb", "set", f"SELECT DISTINCT board_code FROM {DB}.concept_board ORDER BY board_code"),
    ("SET_cbc", "set", f"SELECT DISTINCT board_code FROM {DB}.concept_board_constituent ORDER BY board_code"),
    (
        "SET_sc880_stocks",
        "set",
        f"SELECT DISTINCT stock_code FROM {DB}.sector_constituent WHERE sector_code LIKE '880%' ORDER BY stock_code",
    ),
    (
        "SET_cbc_stocks",
        "set",
        f"SELECT DISTINCT symbol_canonical FROM {DB}.concept_board_constituent ORDER BY symbol_canonical",
    ),
    (
        "NAME_sc880",
        "set",
        f"SELECT DISTINCT sector_name FROM {DB}.sector_constituent WHERE sector_code LIKE '880%' ORDER BY sector_name",
    ),
    ("NAME_cb", "set", f"SELECT DISTINCT board_name FROM {DB}.concept_board ORDER BY board_name"),
    # 板块对象名册（880 名含名，供差集点名）
    (
        "ROSTER_kl880",
        "set",
        f"SELECT DISTINCT concat(sector_code,'|',sector_name) FROM {DB}.kline_sector_880 WHERE sector_code LIKE '880%' ORDER BY sector_code",
    ),
    # 行情侧对象清单（判断 881 有无独立行情表，非新鲜度读数）
    (
        "TBL_sector",
        "set",
        "SELECT name FROM system.tables WHERE database = 'c1_market' AND (name LIKE '%sector%' OR name LIKE '%board%' OR name LIKE '%concept%') ORDER BY name",
    ),
]


def run_channel1(sqls: list[str]) -> tuple[list[dict], str]:
    """通道①＝W-180.4 标准探针 ch_probe.py --file（一次跑完，JSONL 落盘）。

    通道本身跑不起来＝红色事故，必须抛（禁静默降级成"只有单探测"的假双探测）。
    """
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    flist = OUT_DIR / f"probes_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.sql"
    flist.write_text("\n".join(sqls) + "\n", encoding="utf-8")
    p = run_subprocess_hidden(
        [sys.executable, str(_PROBE), "--file", str(flist), "--out-dir", str(OUT_DIR), "--timeout", "60"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    recs = [json.loads(ln) for ln in (p.stdout or "").splitlines() if ln.strip().startswith("{")]
    jsonl = ""
    for ln in (p.stderr or "").splitlines():
        if "产物=" in ln:
            jsonl = ln.split("产物=")[1].split(" 共")[0].strip()
    if len(recs) != len(sqls):
        raise RuntimeError(
            f"通道①探针未产出全量记录（{len(recs)}/{len(sqls)}），禁降级为单探测。"
            f" rc={p.returncode} probe={_PROBE} exe={sys.executable}\n"
            f"stderr_tail={(p.stderr or '')[-800:]}\nstdout_tail={(p.stdout or '')[-400:]}"
        )
    return recs, jsonl


def run_channel2(sql: str) -> tuple[list[tuple], str, str]:
    """通道②＝ch_reader.query_rows() 直读（失败必抛，不吞）。"""
    t0 = datetime.now(timezone.utc)
    rows = ch_reader.query_rows(sql, timeout=60)
    transport = ch_writer.last_transport() or "unknown"
    return rows, transport, t0.isoformat(timespec="seconds")


def main() -> int:
    sqls = [s for _, _, s in _SQL_QUERIES]
    c1, c1_jsonl = run_channel1(sqls)
    c1_by_sql = {r.get("sql_raw"): r for r in c1}

    out: dict = {
        "artifact": "w178_universe_facts.yaml",
        "generated_by": "scripts/governance/wave11/w178_universe_facts_gen.py",
        "command": "set -a; . /d/ZephyrAlpha/config/.env.clickhouse; set +a; "
        "PYTHONPATH=$PWD/src python scripts/governance/wave11/w178_universe_facts_gen.py",
        "generated_at_utc": _now(),
        "lane_python": f"{sys.version.split()[0]}",
        "channels": {
            "channel_1": "scripts/governance/data_supply/ch_probe.py --file (W-180.4 标准探针, query_strict)",
            "channel_1_jsonl": c1_jsonl,
            "channel_2": "zephyr.data.ch_reader.query_rows() 直读（同一传输层、另一调用点）",
            "config_note": "车道无 config/.env.clickhouse，读数侧以 os.environ override（ch_config 在册允许）",
            "read_only": "全部为 SELECT；未对 CH/PG 做任何写操作",
        },
        "readings": {},
        "sets": {},
        "derived": {},
        "failures": [],
    }

    c2_by_key: dict[str, list[tuple]] = {}
    for key, kind, sql in _SQL_QUERIES:
        r1 = c1_by_sql.get(sql, {})
        try:
            rows2, tp2, ts2 = run_channel2(sql)
        except ch_writer.ClickHouseQueryError as e:
            out["failures"].append(
                {
                    "key": key,
                    "channel": "query_rows",
                    "sql": sql,
                    "error": {"type": type(e).__name__, "attempts": [list(a) for a in e.attempts]},
                }
            )
            out["readings"][key] = {
                "kind": kind,
                "sql": sql,
                "value": "NOT_OBTAINED",
                "channel_1": {
                    "outcome": r1.get("outcome"),
                    "transport": r1.get("transport"),
                    "ts_utc": r1.get("ts_utc"),
                    "error": r1.get("error"),
                    "sql_executed": r1.get("sql_executed"),
                },
                "channel_2": "raise ClickHouseQueryError（见 failures）",
                "agree": None,
            }
            continue
        c2_by_key[key] = rows2
        if kind == "scalar":
            v2 = rows2[0][0] if rows2 else None
        elif kind == "onerow":
            v2 = [str(x) for x in rows2[0]] if rows2 else None
        elif kind == "agg":
            v2 = [[str(x) for x in r] for r in rows2]
        else:
            v2 = f"<{len(rows2)} rows>"
        out1_val = r1.get("first_row_sample")
        agree_val = None
        if kind in ("scalar", "onerow") and out1_val is not None and v2 is not None:
            want = [str(v2)] if kind == "scalar" else [str(x) for x in v2]
            agree_val = [str(x) for x in out1_val] == want
        agree_rows = (r1.get("rows") == len(rows2)) if r1.get("rows") is not None else None
        out["readings"][key] = {
            "kind": kind,
            "sql": sql,
            "value": int(v2) if (kind == "scalar" and isinstance(v2, int)) else v2,
            "channel_1": {
                "outcome": r1.get("outcome"),
                "rows_returned": r1.get("rows"),
                "transport": r1.get("transport"),
                "ts_utc": r1.get("ts_utc"),
                "first_row_sample": out1_val,
                "elapsed_ms": r1.get("elapsed_ms"),
                "sql_executed": r1.get("sql_executed"),
            },
            "channel_2": {"transport": tp2, "ts_utc": ts2, "rows_returned": len(rows2)},
            "agree": agree_val,
            "agree_rows": agree_rows,
        }
        if r1.get("outcome") == "fail":
            out["failures"].append({"key": key, "channel": "ch_probe", "sql": sql, "error": r1.get("error")})

    def sset(key: str) -> set[str]:
        return {str(r[0]) for r in c2_by_key.get(key, []) if r}

    S = {
        k: sset(k)
        for k in (
            "SET_kl880",
            "SET_sc880",
            "SET_sc881",
            "SET_cb",
            "SET_cbc",
            "SET_sc880_stocks",
            "SET_cbc_stocks",
            "NAME_sc880",
            "NAME_cb",
            "ROSTER_kl880",
            "SET_scsnap880",
            "SET_namemap880",
            "SET_concept_sector",
            "SET_kl881",
        )
    }
    out["sets"] = {k: {"size": len(v), "sample": sorted(v)[:80]} for k, v in S.items()}

    # 派生：gap（第二探测＝python 集合差）+ 两套口径集合差
    gap = S["SET_kl880"] - S["SET_sc880"]
    gap881 = S["SET_kl881"] - S["SET_sc881"]
    gap_after_snap = S["SET_kl880"] - (S["SET_sc880"] | S["SET_scsnap880"])
    name_by_code = {r.split("|")[0]: r.split("|")[1] for r in S["ROSTER_kl880"] if "|" in r}
    roster_gap = [f"{c}|{name_by_code.get(c, '')}" for c in sorted(gap)]
    out["derived"] = {
        "gap_880_no_constituent": {
            "value_sql_channel1": out["readings"]["gap_sql_880"]["value"],
            "value_python_setdiff": len(gap),
            "agree": out["readings"]["gap_sql_880"]["value"] == len(gap)
            if isinstance(out["readings"]["gap_sql_880"]["value"], int)
            else None,
            "members_full": roster_gap,
        },
        "gap_881_no_constituent": {
            "value_sql_channel1": out["readings"]["gap_sql_881"]["value"],
            "value_python_setdiff": len(gap881),
            "agree": out["readings"]["gap_sql_881"]["value"] == len(gap881)
            if isinstance(out["readings"]["gap_sql_881"]["value"], int)
            else None,
            "members_full": sorted(gap881),
        },
        "gap_880_prefix_split": {
            "definition": "gap 134 按 4 位前缀拆解（与 du881 案卷 §E '8803(61)+8804(71)+8808(2)' 对拍）",
            "split": dict(Counter(c[:4] for c in gap)),
            "total": len(gap),
            "ssot_note": "该族名单在册真源=zephyr/data/implementations/sector_code_bridge.py::TDX_INDUSTRY_BOARDS（本卷未导入核数）",
        },
        "gap_880_after_snapshot_union": {
            "definition": "SET_kl880 − (SET_sc880 ∪ SET_scsnap880)：把 Phase 2 快照表也算作成分源后剩余 gap",
            "value_python_setdiff": len(gap_after_snap),
            "snapshot_880_boards": len(S["SET_scsnap880"]),
            "snapshot_adds": len(S["SET_scsnap880"] - S["SET_sc880"]),
            "members_full": sorted(gap_after_snap),
        },
        "name_resolution_880": {
            "definition": "880 段板块名的可解析度（sector_code_name_map 是名册真源）",
            "kline_880_boards": len(S["SET_kl880"]),
            "namemap_880_boards": len(S["SET_namemap880"]),
            "kline_880_named_by_map": len(S["SET_kl880"] & S["SET_namemap880"]),
            "kline_880_unnamed": len(S["SET_kl880"] - S["SET_namemap880"]),
            "sc880_boards_with_usable_name_in_constituent": out["readings"]["sc880_named_boards"]["value"],
        },
        "third_concept_roster": {
            "concept_sector_boards": len(S["SET_concept_sector"]),
            "overlap_with_concept_board_code": len(S["SET_concept_sector"] & S["SET_cb"]),
            "overlap_with_sc880_code": len(S["SET_concept_sector"] & S["SET_sc880"]),
            "only_in_concept_sector": sorted(S["SET_concept_sector"] - S["SET_cb"])[:40],
        },
        "sc880_vs_concept_board": {
            "code_overlap": len(S["SET_sc880"] & S["SET_cb"]),
            "only_in_sc880": len(S["SET_sc880"] - S["SET_cb"]),
            "only_in_concept_board": len(S["SET_cb"] - S["SET_sc880"]),
            "name_overlap": len(S["NAME_sc880"] & S["NAME_cb"]),
            "only_name_in_sc880": sorted(S["NAME_sc880"] - S["NAME_cb"])[:40],
            "only_name_in_concept_board": sorted(S["NAME_cb"] - S["NAME_sc880"])[:40],
            "stock_overlap": len(S["SET_sc880_stocks"] & S["SET_cbc_stocks"]),
            "only_in_sc880_stocks": len(S["SET_sc880_stocks"] - S["SET_cbc_stocks"]),
            "only_in_concept_stocks": len(S["SET_cbc_stocks"] - S["SET_sc880_stocks"]),
        },
        "cb_vs_cbc": {
            "boards_in_cb_not_in_cbc": len(S["SET_cb"] - S["SET_cbc"]),
            "boards_in_cbc_not_in_cb": len(S["SET_cbc"] - S["SET_cb"]),
        },
        "universe_axis_candidates": {
            "boards_with_quote_880": len(S["SET_kl880"]),
            "boards_mapped_sc880": len(S["SET_sc880"]),
            "boards_mapped_concept": len(S["SET_cb"]),
            "stock_pool_sc880": len(S["SET_sc880_stocks"]),
            "stock_pool_concept": len(S["SET_cbc_stocks"]),
            "stock_pool_union_two_calibers": len(S["SET_sc880_stocks"] | S["SET_cbc_stocks"]),
            "note": "两套口径 board_code 命名空间不相交（tqcenter '880xxx.SH' vs akshare '300xxx'），"
            "只能按成分股集合对齐，不能按板块码/板块名对齐",
        },
        "sector_code_prefix_profile": {
            "kline_sector_880": out["readings"]["kl880_prefix"]["value"],
            "sector_constituent": out["readings"]["sc_prefix"]["value"],
        },
    }

    OUT_YAML.write_text(yaml.safe_dump(out, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")
    print(f"[GEN] {OUT_YAML}  failures={len(out['failures'])}")
    for k, v in out["readings"].items():
        print(f"{k:26s} {str(v['value'])[:70]:70s} agree={v['agree']} tp1={v['channel_1']['transport']}")
    print("derived:", json.dumps(out["derived"], ensure_ascii=False)[:1200])
    return 2 if out["failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
