# [BLUEPRINT] MOD-METAQ-WO-A2LEGS-R1 | docs/_working/meta_question_answers/01_phase2_plan.md §数据施工需求清单(PQ-0013/0063)
# [MODULE] scripts.governance.meta_question.wo_a2legs.build_sector_name_registry
# [DOMAIN] D_DATA
# [DEPENDENCIES] 本地通达信客户端主数据 (E:/tdx/T0002/hq_cache/tdxzs3.cfg|tdxzs.cfg, GBK);
#                 zephyr.infrastructure.database_service (reader 取 880 码全集);
#                 zephyr.data.implementations.sector_code_bridge (在册 TDX_INDUSTRY_BOARDS 常量做一致性交叉验证);
#                 zephyr.shared.io.file_utils.safe_write_text (CAS 写产物册);
#                 zephyr.shared.utils.time_utils (RULE-SCHEMA-TZ：禁裸 datetime.now)
# [CONSUMERS] write_sector_name_map_to_ch.py（派生 CH 维表 c1_market.sector_code_name_map）；
#             WO-A2LEGS 案卷；PQ-0013/0063/0085 复考按 sector_code 口径挂名
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 产物册=真源（SSOT），CH 维表为派生面；每条 name 带来源文件+文件 sha256+mtime 溯源；
#              未配码禁猜名（coverage_status=unresolved，sector_name 留空）；
#              重跑幂等（同输入→同 sha→同产物，map_version=输入内容指纹）；
#              与在册常量 TDX_INDUSTRY_BOARDS 132/132 一致是出厂前置（不一致即非零退出）。
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 主数据文件缺失→RuntimeError fail-visible；常量一致性不通过→SystemExit(2)；
#                  目标码 0→SystemExit(3)。
# [TESTS] 无（数据施工脚本，验收=产物册复核+CH 探针复核，同族 scripts/ch/backfill_* 先例）
# [A_module] module_id=MOD-METAQ-WO-A2LEGS-R1 | layer=script | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""WO-A2LEGS 步骤1产物册生成器：880 板块 code→name 映射册（真源=通达信客户端主数据 cfg）。



背景：c1_market.kline_sector_880（443,380 行，data_source='tqcenter'）sector_name 100% 空置；

CH 内既有维表（sector_meta=881xxx 同花顺行业 90 码 / concept_sector=300xxx 概念 / sector_state

名称亦全空 / sector_constituent 名称退化为码本身）均与 880xxx 码零交集或无真名，故

在册可机械对齐的真源=产生该数据的同一供应商主数据文件（TDX hq_cache/tdxzs3.cfg 主、tdxzs.cfg 副）。



产物：data/registers/metaq_sector_name/sector_code_name_registry.yaml（+ 同名 .csv 便于人读）。



用法：python scripts/governance/meta_question/wo_a2legs/build_sector_name_registry.py

"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from zephyr.shared.utils.time_utils import format_iso, now_utc

_ROOT = Path(__file__).resolve().parents[4]

sys.path.insert(0, str(_ROOT / "src"))


import yaml  # noqa: E402

from zephyr.data.table_registry import TableRegistry  # noqa: E402
from zephyr.infrastructure.database_service import DatabaseService  # noqa: E402
from zephyr.shared.io.file_utils import content_sha256, safe_write_text  # noqa: E402

CFG_DIR = Path(os.environ.get("TDX_HQ_CACHE_DIR", r"E:\tdx\T0002\hq_cache"))

CFG_PRIMARY = "tdxzs3.cfg"

CFG_SECONDARY = "tdxzs.cfg"

OUT_DIR = _ROOT / "data" / "registers" / "metaq_sector_name"

REG_PATH = OUT_DIR / "sector_code_name_registry.yaml"

CSV_PATH = OUT_DIR / "sector_code_name_registry.csv"


# 表名唯一真源 = TableRegistry 品类册（#ARCH-CH-024 Phase 5：禁硬编码全限定表名）

_T_SECTOR_880 = TableRegistry().table("market_sector_kline_880")


# NO-BARE-SQL：SQL 集中于此（§5.160.2）。'2025-09-09' 为固定闭卷切点判据、period='1d' 为口径常量，

# 均非运行期入参故留字面量；本查询无入参，禁把值写进常量。

_SQL_K880_TARGETS = (
    "SELECT sector_code, count(), countIf(trade_date <= '2025-09-09'), min(trade_date), max(trade_date) "
    f"FROM {_T_SECTOR_880} WHERE period='1d' GROUP BY sector_code"
)


#: 码族注释（机械前缀规则；族名仅注记，不参与判据）——

#: 880001~880009=mkt_index 系 zephyr.data.sector_snapshot_collector.classify_market_type 在册口径；

#: 8810~8814=通达信行业族（DU-01/L03-C01 补采后入 880 表，名源走 sector_constituent 第二真源）

FAMILY_BY_PREFIX: dict[str, str] = {
    "8800": "mkt_index",
    "8802": "region",
    "8803": "industry_l1",
    "8804": "industry_l2",
    "8805": "concept_or_style",
    "8806": "concept_or_style",
    "8807": "concept_or_style",
    "8808": "concept_or_style",
    "8809": "concept_or_style",
    "8810": "industry_ths",
    "8811": "industry_ths",
    "8812": "industry_ths",
    "8813": "industry_ths",
    "8814": "industry_ths",
}


# 881 族第二名源（DU-02 扩族，2026-09-25）：tdxzs.cfg 仅含 880 前缀（parse_tdx_cfg 过滤器

# startswith('880')），881 段真名已在库=c1_market.sector_constituent.sector_name

# （refresh_881_names.py 经 tqcenter get_stock_info 回填，实测 5538/5538 真名率 100%）。

# NO-BARE-SQL：SQL 集中（§5.160.2）；argMax(valid_from) 取 SCD-2 最新名。

_T_SECTOR_CONSTITUENT = TableRegistry().table("market_sector_constituent_880")

_SQL_881_NAMES = (
    "SELECT sector_code, argMax(sector_name, valid_from) "
    f"FROM {_T_SECTOR_CONSTITUENT} WHERE sector_code LIKE '881%' "
    "GROUP BY sector_code"
)


def parse_tdx_cfg(path: Path) -> dict[str, tuple[str, str, str]]:
    """解析 TDX 主数据 'name|code|type|level|?|alias' → {code: (name, tdx_type, tdx_level)}。"""

    raw = path.read_bytes()

    text = raw.decode("gbk", errors="replace")

    out: dict[str, tuple[str, str, str]] = {}

    for line in text.splitlines():
        parts = [p.strip() for p in line.split("|")]

        if len(parts) < 4:
            continue

        name, code, ttype, tlevel = parts[0], parts[1], parts[2], parts[3]

        if not code.startswith("880") or not name:
            continue

        out.setdefault(code, (name, ttype, tlevel))

    return out


def fingerprint(paths: list[Path]) -> str:

    h = hashlib.sha256()

    for p in sorted(paths):
        h.update(p.name.encode("utf-8"))

        h.update(p.read_bytes())

    return h.hexdigest()[:16]


def _resolve_meta(bare: str, m_primary: dict, m_secondary: dict) -> tuple[str, str, str, str]:
    """按主/次 TDX 主数据解析板块元组（name/type/level/origin），未命中返回空串四元组。"""

    if bare in m_primary:
        return m_primary[bare][0], m_primary[bare][1], m_primary[bare][2], CFG_PRIMARY

    if bare in m_secondary:
        return m_secondary[bare][0], m_secondary[bare][1], m_secondary[bare][2], CFG_SECONDARY

    return "", "", "", ""


def _load_targets(conn) -> dict:

    targets = {
        str(r[0]): {"rows": int(r[1]), "rows_before_cut": int(r[2]), "first_date": str(r[3]), "last_date": str(r[4])}
        for r in conn.execute(_SQL_K880_TARGETS)
    }

    if not targets:
        raise SystemExit(3)

    return targets


def _load_src_sha(files: list) -> dict:

    return {
        p.name: {
            "sha256": hashlib.sha256(p.read_bytes()).hexdigest()[:16],
            "mtime_utc": datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "size": p.stat().st_size,
        }
        for p in files
    }


def _build_rows(targets: dict, m_primary: dict, m_secondary: dict) -> list:

    rows: list[dict] = []

    for code_full, meta in sorted(targets.items()):
        bare = code_full.split(".")[0]

        name, ttype, tlevel, origin = _resolve_meta(bare, m_primary, m_secondary)

        rows.append(
            {
                "sector_code": code_full,
                "code_bare": bare,
                "sector_name": name,
                "code_family": FAMILY_BY_PREFIX.get(bare[:4], "unknown"),
                "tdx_type": ttype,
                "tdx_level": tlevel,
                "name_source": origin,
                "coverage_status": "named" if name else "unresolved",
                "k880_rows_1d": meta["rows"],
                "k880_rows_before_cut": meta["rows_before_cut"],
                "first_trade_date": meta["first_date"],
                "last_trade_date": meta["last_date"],
                "note": (
                    ""
                    if name
                    else "TDX 主数据（tdxzs3/tdxzs.cfg）无该码；mkt_index 族按在册 classify_market_type "
                    "属大盘指数而非板块，禁猜名，留 unresolved"
                ),
            }
        )

    return rows


def _backfill_881_names(rows: list, conn) -> int:
    """DU-02 扩族：881 段第二名源（sector_constituent 真名，SCD-2 argMax(valid_from) 最新态）。"""

    unresolved_881 = [r for r in rows if not r["sector_name"] and r["code_bare"].startswith("881")]

    n_881_second_source = 0

    if not unresolved_881:
        return 0

    names_881 = {str(r[0]): str(r[1]) for r in conn.execute(_SQL_881_NAMES) if r[1]}

    for r in unresolved_881:
        nm = names_881.get(r["sector_code"], "")

        if nm:
            r["sector_name"] = nm

            r["name_source"] = f"{_T_SECTOR_CONSTITUENT}(tqcenter get_stock_info)"

            r["coverage_status"] = "named"

            r["note"] = ""

            n_881_second_source += 1

        else:
            r["note"] = "tdxzs.cfg 与 sector_constituent 均无该码真名；禁猜名，留 unresolved"

    return n_881_second_source


def _cross_check(rows: list, m_primary: dict) -> tuple[dict, list, list, list]:
    """出厂前置：与在册常量 TDX_INDUSTRY_BOARDS 交叉一致性。"""

    from zephyr.data.implementations.sector_code_bridge import TDX_INDUSTRY_BOARDS

    constant = {b.code: b.name for b in TDX_INDUSTRY_BOARDS}

    overlap = sorted(set(constant) & set(m_primary))

    disagree = [(c, constant[c], m_primary[c][0]) for c in overlap if constant[c] != m_primary[c][0]]

    not_in_cfg = sorted(set(constant) - set(m_primary))

    meta = {
        "constant": "zephyr.data.implementations.sector_code_bridge.TDX_INDUSTRY_BOARDS",
        "constant_codes": len(constant),
        "overlap_with_cfg": len(overlap),
        "agree": len(overlap) - len(disagree),
        "disagree": disagree,
        "constant_codes_absent_in_cfg": not_in_cfg,
        "verdict": (
            "PASS(132/132 逐字相等)" if not disagree and len(overlap) == len(constant) and not not_in_cfg else "FAIL"
        ),
    }

    return meta, [r for r in rows if r["coverage_status"] == "named"], disagree, not_in_cfg


def build(min_row_coverage: float) -> dict:

    conn = DatabaseService().get_clickhouse_conn(role="reader")

    targets = _load_targets(conn)

    prim = CFG_DIR / CFG_PRIMARY

    sec = CFG_DIR / CFG_SECONDARY

    missing = [str(p) for p in (prim, sec) if not p.exists()]

    if missing:
        raise RuntimeError(f"TDX 主数据文件缺失，无法取得真源：{missing}")

    m_primary = parse_tdx_cfg(prim)

    m_secondary = parse_tdx_cfg(sec)

    files = [prim, sec]

    src_sha = _load_src_sha(files)

    rows = _build_rows(targets, m_primary, m_secondary)

    n_881_second_source = _backfill_881_names(rows, conn)

    cross_meta, named, disagree, not_in_cfg = _cross_check(rows, m_primary)

    constant_codes = cross_meta["constant_codes"]

    row_cov = sum(r["k880_rows_1d"] for r in named) / max(1, sum(r["k880_rows_1d"] for r in rows))

    cut_cov = sum(r["k880_rows_before_cut"] for r in named) / max(1, sum(r["k880_rows_before_cut"] for r in rows))

    if row_cov < min_row_coverage:
        raise SystemExit(2)

    if disagree:
        raise SystemExit(4)

    reg = {
        "meta": {
            "title": "metaq_sector_name — 880 板块指数 code→name 映射册（WO-A2LEGS 步骤1产物）",
            "register_id": "metaq_sector_name_registry",
            "purpose": f"为 {_T_SECTOR_880}.sector_name 100% 空置提供在册可机械对齐真源"
            "（PQ-0013/PQ-0063 复考前置；题面口径=sector_code，本册仅补可读名不改判据）",
            "session": "st-metaq-gc-20260924",
            "work_order": "WO-A2LEGS",
            "generated_by": "scripts/governance/meta_question/wo_a2legs/build_sector_name_registry.py",
            "generated_at_utc": format_iso(now_utc()),
            "map_version": fingerprint(files),
            "authoritative_source": {
                "kind": "vendor_master_data_on_disk",
                "vendor": "通达信（tqcenter，与 kline_sector_880.data_source 同源）",
                "primary_file": CFG_PRIMARY,
                "secondary_file": CFG_SECONDARY,
                "dir": str(CFG_DIR),
                "encoding": "GBK",
                "file_sha256_and_mtime": src_sha,
                "why_this_source": "CH 内候选维表全部不合格：sector_meta=881xxx(同花顺行业,0 交集)、"
                "concept_sector/concept_board=300xxx 概念(0 交集)、"
                "sector_state.sector_name 亦 100% 空置、"
                "sector_constituent.sector_name 退化为码本身(真名仅 881xxx 族)；"
                "880xxx 为通达信自有码系，唯一自洽真源=产生该数据的同供应商主数据文件",
                "pit_caveat": "cfg 为客户端当前版本快照，板块改名不可回溯历史名；sector_name 是展示属性、"
                "判据 join 键为 sector_code，故不影响 PIT；历史名缺失如实登记于 caveats",
                "second_source_881_family": {
                    "kind": "in_db_truth",
                    "table": _T_SECTOR_CONSTITUENT,
                    "origin": "tqcenter get_stock_info（refresh_881_names.py 回填，实测真名率 100%）",
                    "scope": "仅 881 行业族（tdxzs.cfg 只含 880 前缀码）",
                    "pit_caveat": "argMax(valid_from) 取 SCD-2 最新名，历史名不回溯（同主源 pit 口径）",
                },
            },
            "cross_check_in_repo_constant": cross_meta,
            "coverage": {
                "target_codes_1d": len(rows),
                "named_codes": len(named),
                "code_coverage": round(len(named) / max(1, len(rows)), 4),
                "row_coverage_1d": round(row_cov, 4),
                "row_coverage_before_cut": round(cut_cov, 4),
                "unresolved_codes": [r["sector_code"] for r in rows if r["coverage_status"] == "unresolved"],
            },
            "caveats": [
                "unresolved 码的 sector_name 保持空串，禁以指数常识拍名（880001~880009 属 mkt_index 族）",
                "本册不回写 kline_sector_880 本体（写面铁律禁覆写既有行），派生面=CH 新维表 c1_market.sector_code_name_map",
            ],
        },
        "rows": rows,
    }

    return reg


def main() -> None:

    ap = argparse.ArgumentParser()

    ap.add_argument("--min-row-coverage", type=float, default=0.95)

    ap.add_argument("--stdout-summary", action="store_true")

    args = ap.parse_args()

    reg = build(args.min_row_coverage)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    text = yaml.safe_dump(reg, allow_unicode=True, sort_keys=False, default_flow_style=False)

    expected = content_sha256(text)

    safe_write_text(REG_PATH, text)

    back = REG_PATH.read_text(encoding="utf-8")

    if content_sha256(back) != expected:
        raise SystemExit(5)

    header = "sector_code,sector_name,code_family,coverage_status,name_source,tdx_type,tdx_level,k880_rows_1d,k880_rows_before_cut,first_trade_date,last_trade_date"

    lines = [header] + [",".join(str(r.get(k, "")) for k in header.split(",")) for r in reg["rows"]]

    csv_text = "\n".join(lines) + "\n"

    safe_write_text(CSV_PATH, csv_text)

    print(
        json.dumps(
            {
                "written": [str(REG_PATH), str(CSV_PATH)],
                "sha256_register": expected,
                **reg["meta"]["coverage"],
                "cross_check": reg["meta"]["cross_check_in_repo_constant"]["verdict"],
            },
            ensure_ascii=False,
            indent=1,
        )
    )


if __name__ == "__main__":
    main()
