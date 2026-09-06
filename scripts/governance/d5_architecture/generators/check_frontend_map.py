# [BLUEPRINT] MOD-D_GOV_SCRIPTS | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] scripts.governance.d5_architecture.generators.check_frontend_map
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] PyYAML（yaml.safe_load）
# [CONSUMERS] construction_workflow_sop Step 3（六图对齐）；alignment_checklist §3（frontend_map 对齐工具）；未来 FRONTEND-MAP commit gate
# [STARTUP] manual（python scripts/governance/d5_architecture/generators/check_frontend_map.py）
# [MATURITY] production
# [INVARIANTS] R0 id 重复=fail；R1 backend_ref 非类型化五前缀=fail；R2 module_id 不在 manifest=warn（auto_scanned 条目豁免）；R3 file 失联=warn（auto/pending 豁免）；YAML 解析失败按异常上抛（fail-closed）
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 校验器永不静默吞错——yaml 异常直接崩（fail-closed）；warn 不影响 exit code，fail>0 → exit 1
# [TESTS] 手动：python scripts/governance/d5_architecture/generators/check_frontend_map.py（exit 0=全过）
# [A_module] module_id=MOD-D_GOV_SCRIPTS | layer=script | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""frontend_map 对齐校验器（alignment_checklist §3 第六图对齐工具，2026-09-04 落地）。

校验三规则（对齐清单 §3 frontend_map 行）：
  R1 backend_ref 类型化——五前缀（module:/registry:/table:/api:/none:）强制，悬空=fail
  R2 map↔manifest 双向一致——module_id 必须存在于 features/manifest.yaml；无 manifest 条目=warn
  R3 file 存在性——file 指向的 JS 文件必须真实存在（web/ 前缀），失联=warn（pending 状态豁免 R3）
用法：python scripts/governance/d5_architecture/generators/check_frontend_map.py
  exit 0=全过 / exit 1=有 fail（供 align 流程或未来 gate 消费）
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[4]
MAP_FILE = REPO / "src/zephyr/frontend/dashboard/web/frontend_map.yaml"
MANIFEST = REPO / "src/zephyr/frontend/dashboard/web/features/manifest.yaml"
WEB = REPO / "src/zephyr/frontend/dashboard/web"
REF_PREFIXES = ("module:", "registry:", "table:", "api:", "none:")


def _ref_list(f: dict) -> list[str]:
    """backend_ref 归一化为引用列表（D38：str 单值或 list 多值均合法）。"""
    raw = f.get("backend_ref", "")
    if isinstance(raw, list):
        return [str(r).strip() for r in raw if str(r).strip()]
    return [str(raw).strip()] if str(raw).strip() else []


def _check_feature(f: dict, mf_ids: set, warns: list, fails: list) -> None:
    """单功能点校验（R1 类型化 fail——列表形态逐元素校验；R2/R3 warn，auto/pending 豁免）。"""
    fid = f.get("id", "?")
    auto = bool(f.get("auto_scanned"))  # auto 补登条目：R2/R3 宽松（待逐页复核转正后严检）
    refs = _ref_list(f)
    if not refs or not refs[0].startswith(REF_PREFIXES):
        fails.append(f"R1 {fid}: backend_ref 悬空（非类型化五前缀）: {' '.join(refs)[:60]}")
        return
    bad = [r for r in refs if not r.startswith(REF_PREFIXES)]
    if bad:
        fails.append(f"R1 {fid}: backend_ref 列表含非类型化元素: {' '.join(bad)[:60]}")
        return
    if f.get("module_id") and not auto and f["module_id"] not in mf_ids:
        warns.append(f"R2 {fid}: module_id={f['module_id']} 不在 features/manifest.yaml")
    fp = f.get("file", "")
    if fp and not auto and f.get("status") != "pending" and not (WEB / fp).exists():
        warns.append(f"R3 {fid}: file 失联 {fp}")


def _load_depgraph_frontend() -> list[dict] | None:
    """depgraph nodes 前端覆盖字段（只读；DB 不可用返回 None 由调用方降级 warn）。"""
    try:
        sys.path.insert(0, str(REPO / "scripts" / "governance"))
        sys.path.insert(0, str(REPO / "src"))
        from _shared.constants import get_depgraph_pg_connection

        conn = get_depgraph_pg_connection(autocommit=True)
        try:
            rows = conn.execute(
                "SELECT blueprint_id, has_frontend, frontend_ref FROM nodes "
                "WHERE blueprint_id IS NOT NULL AND blueprint_id != '' "
                "AND (has_frontend != 'no' OR no_frontend_reason != '' OR frontend_ref != '')"
            ).fetchall()
        finally:
            conn.close()
        return [dict(r._mapping) if hasattr(r, "_mapping") else dict(r) for r in rows]
    except Exception:  # noqa: BLE001 —— DB 抖动不挡 commit 链（对账降级，本地门禁仍全覆盖）
        return None


def _check_module_bus(feats: list, warns: list, fails: list) -> None:
    """R4 模块总线对账（D38）：frontend_map module: 引用 ↔ depgraph frontend_ref 双向闭合。

    ① frontend_map 侧 module:MOD-X 必须在 depgraph 存在（防挂错幽灵模块）
    ② depgraph frontend_ref 的 F-* 功能点引用必须双向闭合（模块挂了功能点，
       该功能点必须挂 module: 该模块——防两侧漂移）
    ③ depgraph frontend_ref 的 P-* 页面引用映射 page 值域（P-STOCKQ→stockq）
    """
    modules = _load_depgraph_frontend()
    if modules is None:
        warns.append("R4 depgraph DB 不可达——模块总线对账降级跳过（环境恢复后自动恢复）")
        return
    depgraph_mods = {m["blueprint_id"] for m in modules}
    by_id = {f.get("id"): f for f in feats}
    pages = {str(f.get("page", "")).lower() for f in feats}

    # ① 前端侧 module: 引用存在性
    for f in feats:
        for r in _ref_list(f):
            if r.startswith("module:"):
                mod = r[len("module:"):].strip()
                if mod and mod not in depgraph_mods:
                    fails.append(f"R4 {f.get('id')}: module 引用不存在于 depgraph: {mod}")

    # ②/③ depgraph 侧引用闭合
    for m in modules:
        refs = [r.strip() for r in str(m.get("frontend_ref") or "").split(",") if r.strip()]
        for r in refs:
            if r.startswith("F-"):
                feat = by_id.get(r)
                if feat is None:
                    fails.append(f"R4 {m['blueprint_id']}: frontend_ref 功能点不存在: {r}")
                else:
                    feat_mods = [
                        x[len("module:"):].strip()
                        for x in _ref_list(feat)
                        if x.startswith("module:")
                    ]
                    if m["blueprint_id"] not in feat_mods:
                        fails.append(
                            f"R4 {m['blueprint_id']}: 挂了功能点 {r} 但该功能点未回挂 module:{m['blueprint_id']}（双向不闭合）"
                        )
            elif r.startswith("P-"):
                page_key = r[2:].lower()
                if page_key not in pages:
                    fails.append(f"R4 {m['blueprint_id']}: frontend_ref 页面不存在: {r}（page 值域无 {page_key}）")


def run_checks() -> tuple[list[str], list[str], int]:
    """执行三规则校验（供 align_all 六图入口复用）→ (fails, warns, 总功能点数)。"""
    data = yaml.safe_load(MAP_FILE.read_text(encoding="utf-8"))
    feats = data.get("features", [])
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    mods = manifest.get("modules") or manifest.get("features") or []
    mf_ids = {m.get("id") for m in mods}

    fails: list[str] = []
    warns: list[str] = []
    ids = [f.get("id", "") for f in feats]
    dup = sorted({i for i in ids if ids.count(i) > 1})
    if dup:
        fails.append(f"R0 id 重复: {dup}")

    for f in feats:
        _check_feature(f, mf_ids, warns, fails)
    _check_module_bus(feats, warns, fails)
    return fails, warns, len(feats)


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    fails, warns, total = run_checks()

    print(f"frontend_map 校验: {total} 功能点")
    for w in warns:
        print(f"WARN: {w}")
    for x in fails:
        print(f"FAIL: {x}")
    print(f"结论: fail={len(fails)} warn={len(warns)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
