# [BLUEPRINT] MOD-METAQ-WO007-IOBINDLOADER | docs/_working/meta_question_answers/gaps/WORKORDER_MASTER.md#WO-007
# [MODULE] scripts.governance.meta_question.wo007.io_edge_binding_loader
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] PyYAML; data/registers/metaq_io_edge/io_edge_binding_register.yaml（件 2 产物）;
#                data/registers/metaq_io_edge/io_sector_two_level_map.yaml（件 1 产物）
# [CONSUMERS] CKG 行业对聚合施工批（PQ-0067 复考/后续传导先验装配）; wo007_reexam.py; 任何需要 io_edge→ig_node
#             挂接而不愿直改 ig_io_edge 的读方
# [STARTUP] import 即用（纯函数库，无常驻）
# [MATURITY] experimental
# [INVARIANTS] 只读：不写任何文件/库；不 import 数据库通道（旁挂册=自足产物，读方零 PG 依赖）；
#              默认返回全量=按结构先验使用；硬判定必须显式 only_hard_judge=True（豁免条款不可默认打开）；
#              文件按 mtime+size 缓存，重复调用不重复解析；未知 tier/参数→抛（禁静默返回空）。
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_generated
# [ERROR_CONTRACT] 册缺失/registry 字段不符/行缺键 → KeyError 或 RuntimeError 直抛并给路径；
#                  tier 非法值 → ValueError。
# [TESTS] wo007_reexam.py --self-check（行数=16,859 与件 2 header 对账 + 聚合抽样复算）
# [TTL] task_bound
"""io_edge_binding_loader — io_edge 旁挂册只读 loader API（WO-007 件 2 交付的一半）。

设计：旁挂=不改 ig_io_edge 原表，因此消费方必须经本 API 取挂接。提供

  load_io_sector_map()        件 1 部门两级映射册（153 行）
  load_io_edge_bindings(...)  件 2 逐边旁挂册（16,859 行，可按挂接档/置信/硬判定过滤）
  industry_pair_matrix(...)   把 io_edge 按标准行业码聚合成「行业→行业」传导矩阵（CKG 聚合消费形）
  register_meta() / exemption_policy()  册元信息与豁免条款（机读）

用法：
    python -m scripts.governance.meta_question.wo007.io_edge_binding_loader --self-check
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

_ROOT = Path(__file__).resolve().parents[4]
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

import yaml  # noqa: E402

REGISTER_DIR = _ROOT / "data/registers/metaq_io_edge"
BINDING_PATH = REGISTER_DIR / "io_edge_binding_register.yaml"
SECTOR_MAP_PATH = REGISTER_DIR / "io_sector_two_level_map.yaml"

TIERS = ("T1_node_identity", "T2_industry_proxy", "T3_mapping_complete")
_CACHE: dict = {}


def _read_yaml(path: Path, expect_registry: str) -> dict:
    if not path.exists():
        raise RuntimeError(f"册不存在：registry={expect_registry}（先跑对应生成器）")
    key = (str(path), path.stat().st_mtime_ns, path.stat().st_size)
    doc = _CACHE.get("_last")
    if not (doc and doc[0] == key):
        doc = (key, yaml.safe_load(path.read_text(encoding="utf-8")))
        _CACHE["_last"] = doc
    data = doc[1]
    if data.get("registry") != expect_registry:
        raise RuntimeError(f"registry={data.get('registry')!r}≠{expect_registry!r}（册类型不符）")
    return data


def load_io_sector_map(path: Path | None = None) -> dict:
    """件 1：153 部门两级映射册（含 mappings/stats/exemption_clause）。"""
    return _read_yaml(path or SECTOR_MAP_PATH, "io_sector_two_level_map")


def sector_map_by_code(path: Path | None = None) -> dict:
    return {m["io_sector_code"]: m for m in load_io_sector_map(path)["mappings"]}


def load_io_edge_bindings(
    path: Path | None = None,
    *,
    tier: str | None = None,
    only_node_linked: bool = False,
    only_hard_judge: bool = False,
    min_confidence: float | None = None,
    cross_industry_only: bool = False,
) -> list[dict]:
    """件 2：逐边旁挂册。

    默认返回全量 16,859 行=**按结构先验使用**；要把挂接当硬事实用，必须显式
    ``only_hard_judge=True``（只留 T1 且两端部门 confirm_status=auto_matched 的边）。
    """
    if tier is not None and tier not in TIERS:
        raise ValueError(f"未知 tier={tier!r}（可选 {TIERS}）")
    rows = _read_yaml(path or BINDING_PATH, "io_edge_binding_register")["bindings"]
    if tier:
        rows = [r for r in rows if r["tier"] == tier]
    if only_node_linked:
        rows = [r for r in rows if r["node_linked"]]
    if only_hard_judge:
        rows = [r for r in rows if r["hard_judge_allowed"]]
    if min_confidence is not None:
        rows = [r for r in rows if (r["conf"] or 0) >= min_confidence]
    if cross_industry_only:
        rows = [r for r in rows if r["cross_industry"]]
    return list(rows)


def industry_pair_matrix(
    bindings: Iterable[dict] | None = None,
    *,
    min_coefficient: float | None = None,
    include_same_industry: bool = False,
    require_sector_auto: bool = False,
) -> dict:
    """io_edge → 标准行业码（申万一级）对聚合矩阵（CKG supplies_to 聚合的同形对照侧）。

    返回 {"A->B": {n_edges, sum_coefficient, max_coefficient, sectors_from, sectors_to,
                   tiers, hard_judge_n}}，按行业码名（册内 l1_industry 原值）为键。
    """
    rows = load_io_edge_bindings() if bindings is None else list(bindings)
    if not include_same_industry:
        rows = [r for r in rows if r["cross_industry"]]
    if require_sector_auto:
        rows = [r for r in rows if r["sector_auto"]]
    if min_coefficient is not None:
        rows = [r for r in rows if (r["coef"] or 0) >= min_coefficient]
    agg: dict = {}
    for r in rows:
        k = (r["fi"], r["ti"])
        a = agg.setdefault(
            k,
            {
                "n_edges": 0,
                "sum_coefficient": 0.0,
                "max_coefficient": 0.0,
                "sectors_from": set(),
                "sectors_to": set(),
                "tiers": Counter(),
                "hard_judge_n": 0,
            },
        )
        a["n_edges"] += 1
        c = float(r["coef"] or 0.0)
        a["sum_coefficient"] += c
        a["max_coefficient"] = max(a["max_coefficient"], c)
        a["sectors_from"].add(r["fc"])
        a["sectors_to"].add(r["tc"])
        a["tiers"][r["tier"]] += 1
        a["hard_judge_n"] += 1 if r["hard_judge_allowed"] else 0
    out = {}
    for (f, t), a in sorted(agg.items()):
        out[f"{f}->{t}"] = {
            "n_edges": a["n_edges"],
            "sum_coefficient": round(a["sum_coefficient"], 6),
            "max_coefficient": round(a["max_coefficient"], 8),
            "sectors_from": sorted(a["sectors_from"]),
            "sectors_to": sorted(a["sectors_to"]),
            "tiers": dict(a["tiers"]),
            "hard_judge_n": a["hard_judge_n"],
        }
    return out


def register_meta(path: Path | None = None) -> dict:
    """册头（stats/threshold_verdict/untouched_proof/side_car_statement），不含逐边行。"""
    data = _read_yaml(path or BINDING_PATH, "io_edge_binding_register")
    return {k: v for k, v in data.items() if k != "bindings"}


def exemption_policy() -> dict:
    """两册豁免条款合并（机读；下游合规检查用）。"""
    b = _read_yaml(BINDING_PATH, "io_edge_binding_register")["exemption_clause"]
    s = _read_yaml(SECTOR_MAP_PATH, "io_sector_two_level_map")["exemption_clause"]
    return {
        "io_edge_binding_register": b,
        "io_sector_two_level_map": s,
        "consumer_rule": "任何进入阈值判定/边激活/因子打分/决策路由的 io_edge 挂接，必须来自 "
        "load_io_edge_bindings(only_hard_judge=True)；其余一律按结构先验（见件 3 "
        "ckg_structural_prior_tier.yaml 的 downstream_obligations）。",
    }


def _self_check() -> int:
    meta = register_meta()
    rows = load_io_edge_bindings()
    smap = load_io_sector_map()
    n = meta["stats"]["edges_total"]
    assert len(rows) == n == 16859, f"行数漂移 {len(rows)} vs {n}"
    assert len(smap["mappings"]) == smap["stats"]["sectors_total"] == 153, "部门册行数漂移"
    assert meta["untouched_proof"]["has_node_column"] is False, "原表出现 node 列=旁挂前提失效"
    assert meta["untouched_proof"]["row_count"] == n, "原表行数与册不一致"
    hard = load_io_edge_bindings(only_hard_judge=True)
    assert all(r["tier"] == "T1_node_identity" for r in hard), "硬判定档混入非 T1"
    t1 = load_io_edge_bindings(tier="T1_node_identity")
    m = industry_pair_matrix()
    print(
        json.dumps(
            {
                "bindings_rows": len(rows),
                "sectors_rows": len(smap["mappings"]),
                "t1_rows": len(t1),
                "hard_judge_rows": len(hard),
                "node_linked_rows": sum(1 for r in rows if r["node_linked"]),
                "industry_pairs_cross": len(m),
                "top_pairs_by_sum_coef": sorted(m.items(), key=lambda kv: -kv[1]["sum_coefficient"])[:5],
                "tiers": meta["stats"]["tier_counts"],
                "OK": True,
            },
            ensure_ascii=False,
            indent=1,
            default=str,
        )
    )
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="io_edge 旁挂册只读 loader（WO-007 件 2）")
    ap.add_argument("--self-check", action="store_true")
    ap.add_argument("--matrix", action="store_true", help="打印行业对聚合矩阵（前 30）")
    ap.add_argument("--min-coefficient", type=float, default=None)
    a = ap.parse_args()
    if a.self_check:
        return _self_check()
    if a.matrix:
        m = industry_pair_matrix(min_coefficient=a.min_coefficient)
        for k, v in sorted(m.items(), key=lambda kv: -kv[1]["sum_coefficient"])[:30]:
            print(f"{k}\tn_edges={v['n_edges']}\tsum_coef={v['sum_coefficient']:.4f}\thard={v['hard_judge_n']}")
        print("pairs:", len(m))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
