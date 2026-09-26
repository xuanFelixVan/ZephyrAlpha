# [BLUEPRINT] MOD-METAQ-WO-A2LEGS-P2 | docs/_working/meta_question_answers/01_phase2_plan.md §数据施工需求清单(PQ-0013/0063)
# [MODULE] scripts.governance.meta_question.wo_a2legs.probe_tdx_cfg_coverage
# [DOMAIN] D_DATA
# [DEPENDENCIES] 本地通达信客户端主数据文件 (E:/tdx/T0002/hq_cache/*.cfg); zephyr.infrastructure.database_service (reader)
# [CONSUMERS] scripts/governance/meta_question/wo_a2legs/build_sector_name_registry.py
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 只读取证零写；GBK 解码 fail-visible；覆盖率如实报不修饰。
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 文件缺失/解码失败→记账继续其他文件并汇总非零退出码。
# [TESTS] 无（一次性取证脚本，同族 scripts/ch/backfill_* 先例）
# [A_module] module_id=MOD-METAQ-WO-A2LEGS-P2 | layer=script | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""WO-A2LEGS probe 02：TDX 客户端主数据 cfg 对 880 码的 code→name 覆盖率取证。"""

from __future__ import annotations

import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "src"))

from zephyr.data.table_registry import TableRegistry  # noqa: E402
from zephyr.infrastructure.database_service import DatabaseService  # noqa: E402

HQ = r"E:\tdx\T0002\hq_cache"
FILES = ["tdxzs3.cfg", "tdxzs.cfg", "tdxhy.cfg"]

# 表名唯一真源 = TableRegistry 品类册（#ARCH-CH-024 Phase 5：禁硬编码全限定表名）
_T_SECTOR_880 = TableRegistry().table("market_sector_kline_880")

# NO-BARE-SQL：SQL 集中于此（§5.160.2）。
_SQL_SECTOR_CODES880 = f"SELECT DISTINCT sector_code FROM {_T_SECTOR_880}"


def parse_cfg(path: str) -> dict[str, str]:
    """tdxzs/tdxzs3: 'name|code|type|level|?|alias' ；tdxhy: 行业归属另格式（探测用）。"""
    with open(path, "rb") as fh:
        raw = fh.read()
    text = raw.decode("gbk", errors="replace")
    out: dict[str, str] = {}
    for line in text.splitlines():
        parts = line.split("|")
        if len(parts) < 2:
            continue
        code = parts[1].strip()
        name = parts[0].strip()
        if len(parts) > 5 and parts[5].strip() and parts[5].strip() not in ("0", "1"):
            name = name if name else parts[5].strip()
        if code and name:
            out.setdefault(code, name)
    return out


def main() -> None:
    conn = DatabaseService().get_clickhouse_conn(role="reader")
    codes880 = sorted(str(r[0]).split(".")[0] for r in conn.execute(_SQL_SECTOR_CODES880))
    uniq = sorted(set(codes880))
    report: dict = {"target_codes": len(uniq), "target_sample": uniq[:8]}
    union: dict[str, tuple[str, str]] = {}
    for fn in FILES:
        p = os.path.join(HQ, fn)
        if not os.path.exists(p):
            report[fn] = {"error": "file_missing"}
            continue
        m = parse_cfg(p)
        tdx = {k: v for k, v in m.items() if k.startswith("880")}
        hit = [c for c in uniq if c in tdx]
        report[fn] = {
            "lines_total": len(m),
            "codes_880": len(tdx),
            "hit_of_target": len(hit),
            "coverage": round(len(hit) / max(1, len(uniq)), 4),
            "sha256": hashlib.sha256(open(p, "rb").read()).hexdigest()[:16],
            "mtime": os.path.getmtime(p),
            "sample": [[k, tdx[k]] for k in sorted(tdx)[:6]],
        }
        for k, v in tdx.items():
            union.setdefault(k, (v, fn))
    miss = [c for c in uniq if c not in union]
    report["UNION"] = {
        "codes_880": len(union),
        "hit_of_target": len(uniq) - len(miss),
        "coverage": round((len(uniq) - len(miss)) / max(1, len(uniq)), 4),
        "miss_count": len(miss),
        "miss_sample": miss[:40],
    }
    # 按家族看缺口
    fam: dict[str, list[str]] = {}
    for c in miss:
        fam.setdefault(c[:4], []).append(c)
    report["miss_by_family"] = {k: len(v) for k, v in sorted(fam.items())}
    print(json.dumps(report, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main()
