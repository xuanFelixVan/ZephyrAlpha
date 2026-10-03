# [BLUEPRINT] MOD-TRADING-015 | docs/03_modules/_domain_trading/decision_map/blueprint.md | §coverage ledger
# [MODULE] scripts.generate_map_coverage_ledger
# [DOMAIN] D_TRADING
# [DEPENDENCIES] stdlib(argparse/pathlib/re/sys); yaml; zephyr.shared.io.file_utils(safe_write_text); zephyr.infrastructure.database_service(DatabaseService); scripts.governance._shared.terminology_loader(get_category_map)
# [CONSUMERS] docs/_working/tdm_mount/B_coverage_ledger_v1.md + B_coverage_ledger_v1.yaml（机生产物，总筹对审输入）；config/trading_decision_map.yaml（挂载侧只读真源）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 双向对账唯一机生通道（禁手改产物）——人口侧=23交易相关域蓝图 frontmatter module_id 全集（施工单 st-tdm-mount-flash-20261003 任务A 后口径）；挂载侧=config/trading_decision_map.yaml 的 module_id 集 + module_ref 代码路径集（路径经 depgraph nodes 按包名折算所属模块）；三分类=已挂 mounted / 未挂孤儿红 unmounted_orphan / 跨域挂载 cross_domain_mount（挂载侧 id 的 depgraph 域 ∉ 23域人口域集=伸手进交易流程）；计数一律写字段禁散文；无匹配真源的挂载侧 id 进 mounted_unresolved 附录（不编造）；图/册不可达 fail-closed 退出码 1；输出经 safe_write_text 原子写；确定性输出（禁 datetime.now/time.time——M46 幂等口径，代之以 --anchor 显式传入锚标签）
# [MODIFY-GUARD] gate_id="MAP-COVERAGE-LEDGER-GENERATOR"；产物仅 docs/_working/tdm_mount/ 前缀
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 输入缺失（图不可达/册缺失/解析失败）exit 1 带定位；--check 校验模式零写盘；永不半写（safe_write_text 原子）
# [TESTS] tests/governance/test_generate_map_coverage_ledger.py
# [A_module] module_id=MOD-TRADING-015 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: AI 会话按需调用的 permanent CLI runner（TDM 覆盖账本机生器，总筹对审/挂图前对账时显式触发，非 cron/非 daemon）
"""generate_map_coverage_ledger — TDM 血肉挂载覆盖账本机生器（施工单任务B，2026-10-03）。

病根：docs/_working/map_census/00_panorama_map_census_v1.md 的人口/挂载普查为手工维护
（静态清单禁手工维护铁律），快照化即漂移；本生成器为活体真源替代（净零申报已随
creation_token merge_evaluation 登记，原册保留为历史快照）。

三分类语义（总筹对审口径）::

    mounted            已挂   ——人口 module_id ∈ TDM 挂载面（module_id 集 ∪ module_ref 折算模块集）
    unmounted_orphan   未挂孤儿 ——人口 module_id ∉ 挂载面（红区，任务C 初挂草案的输入全集）
    cross_domain_mount 跨域挂载 ——挂载面 id 的属域 ∉ 23 域人口域集（外域模块伸手进交易流程）

用法::

    python scripts/generate_map_coverage_ledger.py                 # 生成 md+yaml
    python scripts/generate_map_coverage_ledger.py --check         # 只校验可解析，零写盘
    python scripts/generate_map_coverage_ledger.py --anchor <sha>  # 产物头锚标签（缺省 depgraph 缓存 saved_at）
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

_REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO / "src"))

from zephyr.shared.io.file_utils import content_sha256, safe_write_text  # noqa: E402

TDM_MAP_REL = "config/trading_decision_map.yaml"
LEDGER_DIR = Path("docs/_working/tdm_mount")
LEDGER_MD = LEDGER_DIR / "B_coverage_ledger_v1.md"
LEDGER_YAML = LEDGER_DIR / "B_coverage_ledger_v1.yaml"
CENSUS_PREDECESSOR = "docs/_working/map_census/00_panorama_map_census_v1.md"

# 施工单 st-tdm-mount-flash-20261003 任务B 圈定的 23 个交易相关域（核心12+宽口径11）
DOMAIN_DIRS = (
    "signal",
    "risk",
    "position",
    "trading",
    "sell_decision",
    "execution_core",
    "regime",
    "factor",
    "portfolio_core",
    "portfolio_alloc",
    "plan_engine",
    "autonomy_core",
    "backtest",
    "simulation",
    "fundamental_signal",
    "signal_quality",
    "ex_sor",
    "mkt_data",
    "execution_sim",
    "digital_twin",
    "pf_alloc",
    "ml_serve",
    "machine_learning_train",
)
MODULES_ROOT = Path("docs/03_modules")

_RE_FM = re.compile(r"^---\n(.*?)\n---", re.S)
_RE_MID = re.compile(r"^module_id:\s*(\S+)\s*$", re.M)
_RE_BID = re.compile(r"^blueprint_id:\s*(\S+)\s*$", re.M)
_RE_DOM = re.compile(r"^domain:\s*(\S+)\s*$", re.M)

_LABEL_CATEGORY = "tdm_coverage_status"
_LABEL_KEYS = ("mounted", "unmounted_orphan", "cross_domain_mount")


def load_labels() -> dict[str, str]:
    """固定标签经术语册 loader 读取（SSoT；缺条目降级英文键，禁硬编码中文字典）。"""
    labels: dict[str, str] = {k: k for k in _LABEL_KEYS}
    try:
        sys.path.insert(0, str(_REPO / "scripts" / "governance"))
        from _shared.terminology_loader import get_category_map  # noqa: PLC0415

        zh = get_category_map(_LABEL_CATEGORY)
        for k in _LABEL_KEYS:
            if zh.get(k):
                labels[k] = f"{zh[k]}({k})"
    except Exception:  # noqa: BLE001 — 术语册缺失降级英文键（fail-open 仅展示面）
        pass
    return labels


def scan_population() -> tuple[list[dict], list[dict]]:
    """人口侧：23 域蓝图 frontmatter。返回 (with_id, without_id)。"""
    with_id: list[dict] = []
    without_id: list[dict] = []
    for d in DOMAIN_DIRS:
        dird = MODULES_ROOT / f"_domain_{d}"
        if not dird.exists():
            raise FileNotFoundError(f"人口域目录缺失: {dird.as_posix()}")
        for p in sorted(dird.rglob("blueprint.md")):
            fm_m = _RE_FM.match(p.read_text(encoding="utf-8"))
            fm = fm_m.group(1) if fm_m else ""
            mid = _RE_MID.search(fm)
            bid = _RE_BID.search(fm)
            dom = _RE_DOM.search(fm)
            entry = {
                "blueprint": p.as_posix(),
                "domain_dir": f"_domain_{d}",
                "blueprint_domain": dom.group(1) if dom else "",
                "blueprint_id": bid.group(1) if bid else "",
            }
            if mid:
                entry["module_id"] = mid.group(1)
                with_id.append(entry)
            else:
                without_id.append(entry)
    return with_id, without_id


def load_map_nodes() -> list[dict]:
    path = _REPO / TDM_MAP_REL
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    nodes = data.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        raise ValueError(f"{TDM_MAP_REL} 无 nodes 列表")
    return nodes


# SQL 集中化（§5.160.2）：depgraph 只读查询模块级常量
_SQL_NODE_PATH_MAP = (
    "SELECT path, blueprint_id FROM nodes "
    "WHERE path LIKE 'src/zephyr%' AND blueprint_id IS NOT NULL AND blueprint_id <> ''"
)
_SQL_BID_DOMAIN = (
    "SELECT blueprint_id, MIN(domain_id) AS dom FROM nodes "
    "WHERE blueprint_id IS NOT NULL AND blueprint_id <> '' AND domain_id IS NOT NULL AND domain_id <> '' "
    "GROUP BY blueprint_id"
)


def make_depgraph_resolver() -> tuple[dict[str, str], dict[str, str], dict[str, str], str]:
    """depgraph PG 解析器：path→module_id、包名→module_id、module_id→domain_id。

    返回 (path_map, pkg_map, bid_domain, anchor)；PG 不可达抛异常（fail-closed）。
    """
    from zephyr.infrastructure.database_service import DatabaseService  # noqa: PLC0415

    ds = DatabaseService()
    conn = ds.get_depgraph_conn(read_only=True)
    cur = conn.cursor()
    cur.execute(_SQL_NODE_PATH_MAP)
    path_map: dict[str, str] = {}
    pkg_map: dict[str, str] = {}
    for r in cur.fetchall():
        path, bid = r["path"], r["blueprint_id"]
        path_map.setdefault(path, bid)
        parts = path.split("/")
        if len(parts) >= 3:
            pkg_map.setdefault(parts[2], bid)
    cur.execute(_SQL_BID_DOMAIN)
    bid_domain = {r["blueprint_id"]: (r["dom"] or "") for r in cur.fetchall()}
    conn.close()
    anchor = ""
    cache = _REPO / ".runtime" / "depgraph_scan_cache.json"
    if cache.exists():
        try:
            anchor = str(json.loads(cache.read_text(encoding="utf-8")).get("saved_at", ""))
        except Exception:  # noqa: BLE001 — 锚标签仅展示面
            anchor = ""
    return path_map, pkg_map, bid_domain, anchor


def fold_ref(ref: str, path_map: dict[str, str], pkg_map: dict[str, str]) -> str | None:
    """module_ref 代码路径折算所属模块：精确路径 → 包名前缀，两级折算。"""
    ref_n = ref.replace("\\", "/").strip()
    if ref_n in path_map:
        return path_map[ref_n]
    parts = ref_n.split("/")
    if len(parts) >= 3 and parts[0] == "src" and parts[1] == "zephyr":
        return pkg_map.get(parts[2])
    return None


def build_ledger(
    population: list[dict],
    tdm_module_ids: set[str],
    ref_modules: set[str],
    ref_unresolved: list[str],
    module_domain: dict[str, str],
    trading_domains: set[str],
    ref_total_unique: int = 0,
    ref_folded_total: int = 0,
) -> dict:
    """纯分类核（测试注入面）：三分类 + 附录 + 计数字段。

    ref_total_unique=挂载侧 module_ref 去重总数；ref_folded_total=其中成功折算的
    ref 条数（多条 ref 可折算到同一模块，故与 ref_modules 势不相等）。
    """
    mounted_union = tdm_module_ids | ref_modules
    pop_ids = {p["module_id"] for p in population}
    mounted = sorted(pop_ids & mounted_union)
    unmounted_orphan = sorted(pop_ids - mounted_union)
    cross_domain = sorted(
        mid
        for mid in mounted_union - pop_ids
        if module_domain.get(mid, "") and module_domain[mid] not in trading_domains
    )
    mounted_unresolved = sorted(mid for mid in mounted_union - pop_ids if not module_domain.get(mid, ""))
    return {
        "counts": {
            "population_with_id": len(population),
            "population_unique_module_ids": len(pop_ids),
            "population_duplicate_ids": len(population) - len(pop_ids),
            "mounted": len(mounted),
            "unmounted_orphan": len(unmounted_orphan),
            "cross_domain_mount": len(cross_domain),
            "mounted_unresolved": len(mounted_unresolved),
            "tdm_module_id_unique": len(tdm_module_ids),
            "tdm_module_ref_unique": ref_total_unique or (len(ref_modules) + len(ref_unresolved)),
            "ref_folded_to_module": ref_folded_total or len(ref_modules),
            "ref_folded_unique_modules": len(ref_modules),
            "ref_unresolved": len(ref_unresolved),
            "trading_domains": len(trading_domains),
        },
        "mounted": mounted,
        "unmounted_orphan": unmounted_orphan,
        "cross_domain_mount": cross_domain,
        "mounted_unresolved": mounted_unresolved,
        "ref_unresolved": sorted(ref_unresolved),
    }


def render_markdown(
    ledger: dict, population: list[dict], without_id: list[dict], labels: dict[str, str], anchor: str
) -> str:
    c = ledger["counts"]
    lines = [
        "---",
        "ttl: task_bound",
        "completes_when: 总筹对审消费且 TDM 挂载裁决落地后本件转归档参考",
        'title: "任务B·TDM 覆盖账本 v1（机生）"',
        "owner: st-tdm-mount-flash-20261003",
        "generation: machine_generated",
        "generator: scripts/generate_map_coverage_ledger.py",
        f'anchor: "{anchor}"',
        "---",
        "",
        "# TDM 覆盖账本 v1（双向对账，机生）",
        "",
        f"> 人口侧=23 交易相关域蓝图 module_id 全集；挂载侧=config/trading_decision_map.yaml "
        f"module_id 集 + module_ref 折算模块集。净零申报：替代 {CENSUS_PREDECESSOR} 手工普查段（原册保留历史快照）。",
        "",
        "## 计数（字段，勿散文引用）",
        "",
    ]
    for k, v in c.items():
        lines.append(f"- {k}: {v}")
    sections = [
        ("mounted", "已挂（人口∩挂载面）", "module_id"),
        ("unmounted_orphan", "未挂孤儿（人口−挂载面，红区=任务C 输入全集）", "module_id"),
        ("cross_domain_mount", "跨域挂载（挂载面外域 id=伸手进交易流程）", "module_id | depgraph 域"),
        ("mounted_unresolved", "挂载面无主 id（depgraph 无域记录，不判域不编造）", "module_id"),
    ]
    for key, title, cols in sections:
        lines += ["", f"## {labels.get(key, key)}｜{title}（{len(ledger[key])} 行）", ""]
        lines.append(f"| # | {cols} |")
        lines.append("|---|---|")
        for i, item in enumerate(sorted(ledger[key]), 1):
            if key == "cross_domain_mount":
                lines.append(f"| {i} | {item} | {ledger['_dom'].get(item, '')} |")
            else:
                lines.append(f"| {i} | {item} |")
    lines += ["", f"## module_ref 未折算清单（{c['ref_unresolved']} 条，depgraph 无精确路径且包名无节点）", ""]
    for r in ledger["ref_unresolved"]:
        lines.append(f"- {r}")
    lines += ["", f"## 人口缺 ID 蓝图（{len(without_id)} 个，=任务A 未匹配清单同源）", ""]
    for p in without_id:
        lines.append(
            f"- {p['blueprint']}（blueprint_id={p['blueprint_id'] or '-'}，域={p['blueprint_domain'] or '-'}）"
        )
    lines.append("")
    return "\n".join(lines)


def render_yaml(ledger: dict, without_id: list[dict], anchor: str) -> str:
    doc = {
        "schema_version": "1.0.0",
        "ledger_id": "TDM-COVERAGE-LEDGER",
        "ttl": "task_bound",
        "generation": "machine_generated",
        "generator": "scripts/generate_map_coverage_ledger.py",
        "anchor": anchor,
        "predecessor": CENSUS_PREDECESSOR,
        "counts": ledger["counts"],
        "mounted": ledger["mounted"],
        "unmounted_orphan": ledger["unmounted_orphan"],
        "cross_domain_mount": ledger["cross_domain_mount"],
        "mounted_unresolved": ledger["mounted_unresolved"],
        "ref_unresolved": ledger["ref_unresolved"],
        "population_missing_id": [p["blueprint"] for p in without_id],
    }
    return yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=120)


def main() -> int:
    parser = argparse.ArgumentParser(description="TDM 覆盖账本机生器（双向对账三分类）")
    parser.add_argument("--check", action="store_true", help="只校验输入可解析，零写盘")
    parser.add_argument("--anchor", default="", help="产物锚标签（缺省=depgraph 扫描缓存 saved_at）")
    args = parser.parse_args()

    population, without_id = scan_population()
    nodes = load_map_nodes()
    tdm_module_ids = {str(n["module_id"]) for n in nodes if n.get("module_id")}
    refs = {str(n["module_ref"]).replace("\\", "/") for n in nodes if n.get("module_ref")}
    path_map, pkg_map, bid_domain, cache_anchor = make_depgraph_resolver()
    ref_modules: set[str] = set()
    ref_unresolved: list[str] = []
    ref_folded_total = 0
    for r in sorted(refs):
        folded = fold_ref(r, path_map, pkg_map)
        if folded:
            ref_modules.add(folded)
            ref_folded_total += 1
        else:
            ref_unresolved.append(r)
    module_domain = dict(bid_domain)
    for p in population:
        module_domain.setdefault(p["module_id"], p["blueprint_domain"])
    trading_domains = {p["blueprint_domain"] for p in population + without_id if p["blueprint_domain"]}

    ledger = build_ledger(
        population,
        tdm_module_ids,
        ref_modules,
        ref_unresolved,
        module_domain,
        trading_domains,
        ref_total_unique=len(refs),
        ref_folded_total=ref_folded_total,
    )
    ledger["_dom"] = module_domain
    anchor = args.anchor or cache_anchor
    labels = load_labels()

    md = render_markdown(ledger, population, without_id, labels, anchor)
    yml = render_yaml(ledger, without_id, anchor)
    if args.check:
        print(json.dumps(ledger["counts"], ensure_ascii=False))
        return 0
    md_path = _REPO / LEDGER_MD
    yml_path = _REPO / LEDGER_YAML
    for path, content in ((md_path, md), (yml_path, yml)):
        base = content_sha256(path.read_text(encoding="utf-8")) if path.exists() else None
        safe_write_text(path, content, expected_base_sha256=base, repo_root=str(_REPO))
    print(
        json.dumps({"written": [LEDGER_MD.as_posix(), LEDGER_YAML.as_posix()], **ledger["counts"]}, ensure_ascii=False)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
