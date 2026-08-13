# [BLUEPRINT] MOD-GOV_ALGO_FLOW_TRANSLATION_SYNC | docs/03_modules/_cross_layer/gov_scripts/blueprint.md
# [MODULE] scripts.governance._shared.algo_flow_translation_sync
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance._shared.code_algorithm_extractor
# [CONSUMERS] algorithm_map_rollout（步骤⑥ 翻译真源同步）；后续 reconciler 可复用检测漂移
# [STARTUP] event_driven
# [MATURITY] production
# [INVARIANTS] 幂等（重复运行同结果）; 只回填空缺不覆盖人工curated字段; mtr algo_submodules 段整体派生重建; 指标注册表按 name_en 去重
# [MODIFY-GUARD] 无
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 注册表 YAML 损坏→报错不部分写入
# [TESTS] 无（rollout 工具）
# [TTL] permanent
"""algo_flow_translation_sync.py — ALGO_FLOW 标记 → 翻译真源同步（§4.16.4，方案步骤⑥）。

把 416 个运营态模块 ALGO_FLOW 标记里的 name_zh/intro 同步进翻译真源：
  ① 特征/因子节点（有FCT条目）→ factor_registry.yaml 回填 name_zh + alpha_source（只填空，不覆盖）
  ② 技术指标节点 → 新建 technical_indicator_registry.yaml（待建注册表，按 name_en 去重，
     name_zh + description=intro + formula + 来源模块）
  ③ 算法子模块节点 → module_translation_registry.yaml 新增顶段 ``algo_submodules:``
     （整体派生重建，幂等；不动 entries 主段——entries 由 auto-extract 工具管辖）

使用方式：
    python scripts/governance/_shared/algo_flow_translation_sync.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

_THIS_FILE = Path(__file__).resolve()
_SHARED_DIR = str(_THIS_FILE.parent)
if _SHARED_DIR not in sys.path:
    sys.path.insert(0, _SHARED_DIR)

from code_algorithm_extractor import REPO_ROOT, extract_algorithm_from_code  # noqa: E402

_CATALOGS = REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs"
_FACTOR_REGISTRY = _CATALOGS / "factor_registry.yaml"
_MTR = _CATALOGS / "module_translation_registry.yaml"
_TI_REGISTRY = _CATALOGS / "technical_indicator_registry.yaml"
_MODULES_JSON = REPO_ROOT / ".trae" / "documents" / "_operational_modules.json"

_FCT_RE = re.compile(r"(FCT-[A-Z]+-\d+)")


def _harvest() -> dict:
    """重解析全部运营态模块的 ALGO_FLOW 标记，按层收集节点。"""
    import json

    mods = json.loads(_MODULES_JSON.read_text(encoding="utf-8"))
    features: list[dict] = []   # 特征层
    indicators: list[dict] = []  # 指标层
    algos: list[dict] = []      # 算法层
    for m in mods:
        s = extract_algorithm_from_code(REPO_ROOT / m["path"], module_id=m["module_id"])
        if s.algo_flow is None:
            continue
        for n in s.algo_flow.nodes:
            rec = {
                "module_id": m["module_id"],
                "module_path": s.source_path or m["path"],
                "node_id": n.id,
                "name_zh": n.name_zh, "name_en": n.name_en, "intro": n.intro,
                "formula": n.formula, "registry": n.registry,
            }
            if n.layer == "特征":
                features.append(rec)
            elif n.layer == "指标":
                indicators.append(rec)
            elif n.layer == "算法":
                algos.append(rec)
    return {"features": features, "indicators": indicators, "algos": algos}


def _fill_factor_entry(feat: dict, by_id: dict) -> tuple[int, int]:
    """单特征节点回填 factor_registry 条目（只填空不覆盖）。返回 (filled_zh, filled_alpha)。"""
    m = _FCT_RE.search(feat["registry"] or "")
    if not m:
        return 0, 0
    entry = by_id.get(m.group(1))
    if entry is None:
        return 0, 0
    filled_zh = filled_alpha = 0
    if feat["name_zh"] and not (entry.get("name_zh") or "").strip():
        entry["name_zh"] = feat["name_zh"]
        filled_zh = 1
    if feat["intro"] and not (entry.get("alpha_source") or "").strip():
        entry["alpha_source"] = feat["intro"]
        filled_alpha = 1
    return filled_zh, filled_alpha


def _sync_factor_registry(features: list[dict]) -> dict:
    """特征节点（有FCT条目）→ factor_registry 回填 name_zh/alpha_source（只填空）。"""
    data = yaml.safe_load(_FACTOR_REGISTRY.read_text(encoding="utf-8"))
    factors = data.get("factors") or []
    by_id = {f.get("factor_id"): f for f in factors}
    filled_zh = filled_alpha = 0
    for feat in features:
        dz, da = _fill_factor_entry(feat, by_id)
        filled_zh += dz
        filled_alpha += da
    if filled_zh or filled_alpha:
        _FACTOR_REGISTRY.write_text(
            yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=120),
            encoding="utf-8", newline="\n",
        )
    return {"fct_matched": sum(1 for f in features if _FCT_RE.search(f["registry"] or "")),
            "filled_name_zh": filled_zh, "filled_alpha_source": filled_alpha}


def _sync_technical_indicator_registry(indicators: list[dict]) -> dict:
    """指标节点 → technical_indicator_registry.yaml（待建注册表，按 name_en 去重）。

    保护（2026-08-13，AI-REG-IND-001）：REG-IND-001 已全新施工（62 号 §4.5，
    40 条目手工 SSoT），本函数检测到注册表已升级（registry_id 不再是种子版
    REG-TECHNICAL-INDICATOR-001）时跳过覆写，防止派生种子冲掉手工真源。
    翻译职能（name_zh/description）已由 REG-IND-001 正式条目吸收。
    """
    if _TI_REGISTRY.exists():
        existing = yaml.safe_load(_TI_REGISTRY.read_text(encoding="utf-8")) or {}
        if existing.get("registry_id") != "REG-TECHNICAL-INDICATOR-001":
            return {"skipped": f"注册表已升级为 {existing.get('registry_id')}（手工 SSoT），种子覆写跳过"}
    seen: dict[str, dict] = {}
    for ind in indicators:
        key = (ind["name_en"] or ind["node_id"]).strip().lower()
        if not key:
            continue
        if key not in seen:
            seen[key] = ind
    entries = []
    for i, (key, ind) in enumerate(sorted(seen.items()), 1):
        entries.append({
            "indicator_id": f"IND-ALGOMAP-{i:03d}",
            "name_zh": ind["name_zh"],
            "name_en": ind["name_en"] or ind["node_id"],
            "description": ind["intro"],
            "formula": ind["formula"],
            "table_status": ind["registry"],
            "source_module": ind["module_id"],
            "source_path": ind["module_path"],
        })
    doc = {
        "ttl": "permanent",
        "schema_version": "0.1.0",
        "registry_id": "REG-TECHNICAL-INDICATOR-001",
        "name": "技术指标注册表（算法地图同步种子版）",
        "description": (
            "技术指标 name_zh/description 真源（§4.16.4）。种子数据由 "
            "algo_flow_translation_sync.py 从 416 模块 ALGO_FLOW 标记派生（按 name_en 去重），"
            "后续扩充走正常登记流程。"
        ),
        "owner": "ZephyrAlpha-Owner",
        "tier": "business",
        "status": "active",
        "version": "0.1.0",
        "created": "2026-08-12",
        "last_updated": "2026-08-12",
        "unique_key": ["name_en"],
        "indicators": entries,
    }
    _TI_REGISTRY.write_text(
        yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=120),
        encoding="utf-8", newline="\n",
    )
    return {"indicators": len(entries)}


def _sync_mtr_algo_submodules(algos: list[dict]) -> dict:
    """算法子模块 → mtr 新增 algo_submodules 顶段（整体派生重建，幂等）。"""
    data = yaml.safe_load(_MTR.read_text(encoding="utf-8"))
    entries = []
    for a in algos:
        entries.append({
            "module_path": a["module_path"],
            "module_id": a["module_id"],
            "node_id": a["node_id"],
            "name_zh": a["name_zh"],
            "name_en": a["name_en"],
            "plain_zh": a["intro"],
        })
    data["algo_submodules"] = entries
    _MTR.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=120),
        encoding="utf-8", newline="\n",
    )
    return {"algo_submodules": len(entries)}


def main() -> None:
    print("[1/4] 重解析 416 模块 ALGO_FLOW 标记…")
    h = _harvest()
    print(f"      特征 {len(h['features'])} ｜ 指标 {len(h['indicators'])} ｜ 算法 {len(h['algos'])}")
    print("[2/4] 同步 factor_registry（只回填空缺）…")
    print("     ", _sync_factor_registry(h["features"]))
    print("[3/4] 生成 technical_indicator_registry（去重种子）…")
    print("     ", _sync_technical_indicator_registry(h["indicators"]))
    print("[4/4] 同步 module_translation_registry.algo_submodules（派生重建）…")
    print("     ", _sync_mtr_algo_submodules(h["algos"]))
    print("[OK] 翻译真源同步完成")


if __name__ == "__main__":
    main()
