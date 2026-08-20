# [BLUEPRINT] MOD-GOV_ALGO_FLOW_TRANSLATION_SYNC | docs/03_modules/_cross_layer/gov_scripts/blueprint.md
# [MODULE] scripts.governance._shared.algo_flow_translation_sync
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance._shared.code_algorithm_extractor
# [CONSUMERS] algorithm_map_rollout（步骤⑥ 翻译真源同步）；后续 reconciler 可复用检测漂移
# [STARTUP] event_driven
# [MATURITY] production
# [INVARIANTS] 幂等（重复运行同结果）; 只回填空缺不覆盖人工curated字段; mtr algo_submodules 段整体派生重建; 指标注册表按 name_en 去重; 段级文本替换保人工段字节（B7 治本，禁整文件重序列化）; 运行即写审计日志
# [MODIFY-GUARD] 无
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 注册表 YAML 损坏→报错不部分写入
# [TESTS] tests/scripts/test_algo_flow_translation_sync.py
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

import os
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


# ── B7 治本（2026-08-19）：段级文本替换原语 ─────────────────────────────────
# 事故背景：原实现整文件 safe_load→safe_dump 重序列化——entries 等人工维护段落的
# 引号/空串写法/折行被 PyYAML 规范化，造成 195+/215- 纯格式漂移（两次未登记异动，
# drift watchdog 快照在案；同类事故先例=audit_registration.py:1265 OPS-A3
# "不再手动 yaml.dump——会丢弃头注释并重排格式"）。以下原语保人工段字节级原样。


def _replace_top_level_section(text: str, key: str, new_section: str) -> str:
    """替换 YAML 文本中某个顶段（``key:`` 起至下一顶段/EOF），其余字节原样保留。

    顶段判定：行首 ``key:`` 形态（``^[A-Za-z_]\\w*:``——顶段列表项 ``- `` 虽在行首
    但非 key 形态，不算新段）。段不存在时追加到文件尾。
    new_section 须为 ``yaml.safe_dump({key: value}, ...)`` 产物（自带 ``key:`` 头行）。
    """
    key_re = re.compile(r"^[A-Za-z_]\w*:")
    lines = text.splitlines(keepends=True)
    start: int | None = None
    for i, ln in enumerate(lines):
        if ln.startswith(f"{key}:"):
            start = i
            break
    if start is None:
        base = text if text.endswith("\n") else text + "\n"
        return base + new_section
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if key_re.match(lines[j]):
            end = j
            break
    return "".join(lines[:start]) + new_section + "".join(lines[end:])


def _yaml_scalar_inline(value: str) -> str:
    """单值 YAML 标量序列化（强制单行不折行，保人工段排版最小侵入）。"""
    dumped = yaml.safe_dump({"v": value}, allow_unicode=True, sort_keys=False, width=10**9)
    return dumped.split(":", 1)[1].strip()


def _validated_write(path: Path, new_text: str) -> None:
    """ERROR_CONTRACT 落地：写前 YAML 可解析校验，损坏→报错不部分写入。"""
    yaml.safe_load(new_text)  # 解析失败抛异常，不写文件
    path.write_text(new_text, encoding="utf-8", newline="\n")


def _fill_factor_fields_textual(text: str, fills: dict[tuple[str, str], str]) -> tuple[str, dict[str, int]]:
    """factor_registry 段级字段回填：定位 ``- factor_id:`` 块，就地替换/插入字段行。

    fills: {(factor_id, field): value}——调用方已判定"条目存在且字段为空"。
    返回 (新文本, {field: 实际回填数})。找不到条目/字段已有非空值（并发漂移）→ 跳过不计数。
    实现：块定位与改写分两遍，改写按块逆序进行（insert 不移位前序块索引）。
    """
    lines = text.splitlines(keepends=True)
    entry_re = re.compile(r'^\s*-\s*factor_id:\s*[\'"]?([^\'"\s]+)')
    starts = [(i, m.group(1)) for i, ln in enumerate(lines) if (m := entry_re.match(ln))]
    blocks = [
        (s, starts[idx + 1][0] if idx + 1 < len(starts) else len(lines), fid) for idx, (s, fid) in enumerate(starts)
    ]
    filled_by_field: dict[str, int] = {}
    for s, e, fid in reversed(blocks):
        for field in ("name_zh", "alpha_source"):
            value = fills.get((fid, field))
            if value is None:
                continue
            field_re = re.compile(rf"^(\s+){field}\s*:")
            for k in range(s + 1, e):
                m = field_re.match(lines[k])
                if m:
                    existing = lines[k].split(":", 1)[1].strip().strip("'\"")
                    if existing:  # 并发漂移：字段已被填——跳过不覆盖（只填空铁律）
                        break
                    lines[k] = f"{m.group(1)}{field}: {_yaml_scalar_inline(value)}\n"
                    filled_by_field[field] = filled_by_field.get(field, 0) + 1
                    break
            else:
                indent = re.match(r"^(\s*)", lines[s]).group(1) + "  "
                lines.insert(s + 1, f"{indent}{field}: {_yaml_scalar_inline(value)}\n")
                filled_by_field[field] = filled_by_field.get(field, 0) + 1
    return "".join(lines), filled_by_field


def _audit_run(results: dict) -> None:
    """运行即写审计日志（B7 治本：两次未登记运行无人知晓——操作者可追查）。"""
    import json
    from datetime import datetime, timezone

    audit_dir = REPO_ROOT / ".runtime" / "audit"
    audit_dir.mkdir(parents=True, exist_ok=True)
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "tool": "algo_flow_translation_sync",
        "session": os.environ.get("ZEPHYR_SESSION_ID", ""),
        "results": results,
    }
    with (audit_dir / "algo_flow_translation_sync_runs.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _harvest() -> dict:
    """重解析全部运营态模块的 ALGO_FLOW 标记，按层收集节点。"""
    import json

    mods = json.loads(_MODULES_JSON.read_text(encoding="utf-8"))
    features: list[dict] = []  # 特征层
    indicators: list[dict] = []  # 指标层
    algos: list[dict] = []  # 算法层
    for m in mods:
        s = extract_algorithm_from_code(REPO_ROOT / m["path"], module_id=m["module_id"])
        if s.algo_flow is None:
            continue
        for n in s.algo_flow.nodes:
            rec = {
                "module_id": m["module_id"],
                "module_path": s.source_path or m["path"],
                "node_id": n.id,
                "name_zh": n.name_zh,
                "name_en": n.name_en,
                "intro": n.intro,
                "formula": n.formula,
                "registry": n.registry,
            }
            if n.layer == "特征":
                features.append(rec)
            elif n.layer == "指标":
                indicators.append(rec)
            elif n.layer == "算法":
                algos.append(rec)
    return {"features": features, "indicators": indicators, "algos": algos}


def _sync_factor_registry(features: list[dict]) -> dict:
    """特征节点（有FCT条目）→ factor_registry 回填 name_zh/alpha_source（只填空）。

    B7 治本（2026-08-19）：原实现有回填即整文件 safe_dump——round-trip 实测
    346376→329517 字节不幂等，人工排版被规范化（MTR 同款漂移隐患）。改为段级
    文本回填（_fill_factor_fields_textual）：无回填零写入，有回填只动目标字段行。
    """
    text = _FACTOR_REGISTRY.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    factors = data.get("factors") or []
    by_id = {f.get("factor_id"): f for f in factors}
    fills: dict[tuple[str, str], str] = {}
    for feat in features:
        m = _FCT_RE.search(feat["registry"] or "")
        if not m:
            continue
        entry = by_id.get(m.group(1))
        if entry is None:
            continue
        if feat["name_zh"] and not (entry.get("name_zh") or "").strip():
            fills[(m.group(1), "name_zh")] = feat["name_zh"]
        if feat["intro"] and not (entry.get("alpha_source") or "").strip():
            fills[(m.group(1), "alpha_source")] = feat["intro"]
    filled_zh = filled_alpha = 0
    if fills:
        new_text, filled_by_field = _fill_factor_fields_textual(text, fills)
        filled_zh = filled_by_field.get("name_zh", 0)
        filled_alpha = filled_by_field.get("alpha_source", 0)
        if filled_zh or filled_alpha:
            _validated_write(_FACTOR_REGISTRY, new_text)
    return {
        "fct_matched": sum(1 for f in features if _FCT_RE.search(f["registry"] or "")),
        "filled_name_zh": filled_zh,
        "filled_alpha_source": filled_alpha,
    }


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
        entries.append(
            {
                "indicator_id": f"IND-ALGOMAP-{i:03d}",
                "name_zh": ind["name_zh"],
                "name_en": ind["name_en"] or ind["node_id"],
                "description": ind["intro"],
                "formula": ind["formula"],
                "table_status": ind["registry"],
                "source_module": ind["module_id"],
                "source_path": ind["module_path"],
            }
        )
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
        encoding="utf-8",
        newline="\n",
    )
    return {"indicators": len(entries)}


def _sync_mtr_algo_submodules(algos: list[dict]) -> dict:
    """算法子模块 → mtr algo_submodules 顶段（整体派生重建，幂等）。

    B7 治本（2026-08-19）：原实现整文件 safe_load→safe_dump 重序列化，entries 等
    人工段引号/空串/折行被 PyYAML 规范化（两次未登记漂移实证，drift watchdog 快照
    在案）。改为段级文本替换：entries/battle_map 等人工段字节级原样，仅
    algo_submodules 顶段（派生段）整体重写。写前 YAML 可解析校验（ERROR_CONTRACT）。
    """
    entries = []
    for a in algos:
        entries.append(
            {
                "module_path": a["module_path"],
                "module_id": a["module_id"],
                "node_id": a["node_id"],
                "name_zh": a["name_zh"],
                "name_en": a["name_en"],
                "plain_zh": a["intro"],
            }
        )
    new_section = yaml.safe_dump({"algo_submodules": entries}, allow_unicode=True, sort_keys=False, width=120)
    text = _MTR.read_text(encoding="utf-8")
    _validated_write(_MTR, _replace_top_level_section(text, "algo_submodules", new_section))
    return {"algo_submodules": len(entries)}


def main() -> None:
    print("[1/4] 重解析 416 模块 ALGO_FLOW 标记…")
    h = _harvest()
    print(f"      特征 {len(h['features'])} ｜ 指标 {len(h['indicators'])} ｜ 算法 {len(h['algos'])}")
    print("[2/4] 同步 factor_registry（只回填空缺）…")
    r_factor = _sync_factor_registry(h["features"])
    print("     ", r_factor)
    print("[3/4] 生成 technical_indicator_registry（去重种子）…")
    r_ti = _sync_technical_indicator_registry(h["indicators"])
    print("     ", r_ti)
    print("[4/4] 同步 module_translation_registry.algo_submodules（派生重建）…")
    r_mtr = _sync_mtr_algo_submodules(h["algos"])
    print("     ", r_mtr)
    _audit_run({"factor": r_factor, "ti": r_ti, "mtr": r_mtr})  # B7：运行即写审计日志
    print("[OK] 翻译真源同步完成")


if __name__ == "__main__":
    main()
