# [BLUEPRINT] MOD-LIB-007 | docs/03_modules/_domain_library/blueprint.md | §7
# [MODULE] zephyr.library.ruling_precedent
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.io.paths (REPO_ROOT)；zephyr.governance.capability_lookup.write_lookup_audit_log（--session 审计，懒加载）
# [CONSUMERS] zephyr.library.lookup（ruling: 检索面委托）；裁定路由政策 §2.2 E2 前置（docs/01_policies_and_standards/sop/governance_sop/adjudication_routing_policy.md）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 只读（ruling_registry.yaml 零改写；写侧真源=PG 账本 REG-RULING-001 意图 API，本模块不碰）；归类=派生视图机械规则（条目显式 route_class/d_class 字段优先=政策 §6.1 登记即归类前向兼容；缺省走 D1-D8 关键词面，元组序即优先级序=处置语义优先于过程语义，首命中为主类，全命中集+证据词随行展示）；存量条目禁事后批处理回填（政策 §6.1）；关键词面只增不删，删改序须测试随改；退出码契约同图书馆总口（0=有结果/普查，1=无结果）
# [MODIFY-GUARD] gate_id 不适用
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 裁定册缺失/YAML 解析失败=SystemExit 非零不产半结果；查询零命中 rc=1 附 E2 新类提示；--session 审计失败 fail-open 不阻断查询
# [TESTS] tests/ai/library/test_ruling_precedent.py
# [A_module] module_id=MOD-LIB-007 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""ruling_precedent.py — 裁定先例机检薄 CLI（MOD-LIB-007，裁定路由政策 v2 E2 强制前置）。

政策锚（adjudication_routing_policy.md §2.2 E2）：裁新项必先机检 ruling_registry
同类先例并引用裁定号；零先例=判"新类"→触发路由表丰富流程。本模块=该机检的执行面：
按八类路由（D1-D8）归类检索裁定册，建在图书馆检索面上（``python -m zephyr.library.lookup
ruling:D3 <词>`` 同达，零新检索系统）。

八类口径真源=裁定路由政策 §3（识别问句），本模块只读投影：

    D1 生死处置   D2 通道门禁   D3 标准阈值   D4 方向路线
    D5 资源优先级 D6 事故冲突   D7 数据口径   D8 例外豁免

归类是派生视图机械规则（零注册表写、零新字段）：条目显式 ``route_class``/``d_class``
字段优先（政策 §6.1 登记即归类的读侧前向兼容）；缺省走关键词面按优先级序取首命中为
主类。命中证据（关键词+显式标记）随行展示，供 E2 引用留痕与 Owner 抽查复核。

Usage::

    python -m zephyr.library.ruling_precedent                     # 八类普查（未归类=路由缺口信号）
    python -m zephyr.library.ruling_precedent 退役 --class D1     # E2 同类先例机检
    python -m zephyr.library.ruling_precedent 裁定#489            # 单条定位（含归类证据）
    python -m zephyr.library.ruling_precedent --class D3 --status active --limit 50
    python -m zephyr.library.lookup ruling:D3 退役                # 图书馆总口等达形式
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any, Final

from zephyr.shared.io.paths import REPO_ROOT

# noqa: m11-perm-manual-legitimate  M11豁免: 裁定先例机检查询 CLI（python -m zephyr.library.ruling_precedent / lookup ruling: 面）人工按需调用是设计形态，非常驻系统（先例=lookup.py 同款标记）

__all__ = ["classify_ruling", "load_rulings", "main", "query_face", "search"]  # noqa: n114-final  n114-final豁免: __all__是Python导出约定，非可变常量，无需Final标注（先例=lookup.py L48 同款）

_REGISTRY_CAPABILITY_ID: Final[str] = "ruling_registry"


def _resolve_registry_path() -> Path:
    """SSoT 路径经 capability_canonical_file_registry 反查（VOCAB-CHAIN 合规，禁硬编码）。

    capability_id=``ruling_registry`` 的 canonical_file 即裁定册路径；反查无命中=
    fail-closed SystemExit（与 ERROR_CONTRACT 一致，禁退化为猜测路径）。
    """
    from zephyr.governance.capability_lookup import CapabilityLookup  # noqa: PLC0415 — 懒加载

    for hit in CapabilityLookup().find(_REGISTRY_CAPABILITY_ID):
        cid = hit.get("capability_id") if isinstance(hit, dict) else getattr(hit, "capability_id", None)
        cf = hit.get("canonical_file") if isinstance(hit, dict) else getattr(hit, "canonical_file", None)
        if cid == _REGISTRY_CAPABILITY_ID and cf:
            return REPO_ROOT / str(cf)
    raise SystemExit(f"FAIL: capability 册反查 {_REGISTRY_CAPABILITY_ID} 无 canonical_file——先补册再查")


#: 八类关键词面（口径真源=裁定路由政策 §3 识别问句）；元组序=归类优先级序
#: （处置语义 D1/D8 先于门禁/标准 D2/D3，过程语义 D4/D5 收尾）——首命中为主类。
_CLASS_RULES: Final[tuple[tuple[str, str, tuple[str, ...]], ...]] = (
    (
        "D1",
        "这东西下岗还是死刑？",
        (
            "退役",
            "判死",
            "永久退役",
            "retired",
            "deprecated",
            "下岗",
            "封存",
            "墓碑",
            "清退",
            "摘除",
            "停用",
            "归档",
            "改判",
            "轨 a",
            "轨 b",
        ),
    ),
    ("D8", "是例外还是常态？", ("豁免", "白名单", "escape", "特批", "bypass", "绕过", "例外")),
    (
        "D2",
        "有没有预注册/冻结卡在途？",
        ("预注册", "冻结卡", "开通道", "通道开通", "flag 翻转", "翻 flag", "解禁", "opt-in", "出厂值"),
    ),
    ("D3", "门柱动没动过？", ("及格线", "阈值", "门槛", "门柱", "判据冻结", "冻结为", "预算带", "评分线", "合格线")),
    ("D7", "真源在 YAML 还是 DB？", ("口径", "回补", "真源", "回填", "DDL", "时区", "刷数", "双写")),
    ("D6", "是谁的在途面？", ("事故", "冲突", "踩踏", "无主", "回滚", "误删", "丢失", "死锁", "抢占")),
    ("D4", "这是第几次尝试？", ("换路", "放弃", "再攻", "封顶", "方向性", "路线")),
    ("D5", "价值评级×前置依赖×净零替代？", ("立项", "排序", "优先级", "排期", "算力", "排队")),
)

_CLASS_NAMES: Final[dict[str, str]] = {
    "D1": "生死处置",
    "D2": "通道门禁",
    "D3": "标准阈值",
    "D4": "方向路线",
    "D5": "资源优先级",
    "D6": "事故冲突",
    "D7": "数据口径",
    "D8": "例外豁免",
}

_ROW_LIMIT_MAX: Final[int] = 500


def load_rulings(registry_path: str | Path | None = None) -> list[dict[str, Any]]:
    """只读装载裁定册 entries（真源=YAML 投影；缺失/解析失败=SystemExit 非零）。"""
    import yaml  # noqa: PLC0415 — 懒加载（CLI 常规路径轻启动）

    path = Path(registry_path) if registry_path else _resolve_registry_path()
    if not path.exists():
        raise SystemExit(f"FAIL: 裁定册缺失 {path}（真源锚=REG-RULING-001）")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise SystemExit(f"FAIL: 裁定册 YAML 解析失败 {path}: {exc}") from exc
    entries = data.get("entries")
    if not isinstance(entries, list):
        raise SystemExit(f"FAIL: 裁定册 entries 段缺失或非列表 {path}")
    return [e for e in entries if isinstance(e, dict)]


def classify_ruling(entry: dict[str, Any]) -> tuple[str, list[str], dict[str, str]]:
    """机械归类单条裁定 → (主类, 全命中类, 证据)。

    显式 ``route_class``/``d_class`` 字段优先（政策 §6.1 登记即归类读侧前向兼容）；
    缺省走关键词面，元组序即优先级序，首命中为主类。零命中返回 ("", [], {})——
    未归类=路由缺口信号，禁臆测补类。
    """
    explicit = str(entry.get("route_class") or entry.get("d_class") or "").strip().upper()
    if explicit:
        return explicit, [explicit], {"显式": explicit}
    text = " ".join(str(entry.get(k) or "") for k in ("title", "summary", "category")).lower()
    matched: list[str] = []
    evidence: dict[str, str] = {}
    for cls, _question, keywords in _CLASS_RULES:
        hits = [kw for kw in keywords if kw in text]
        if hits:
            matched.append(cls)
            evidence[cls] = ",".join(hits[:3])
    return (matched[0] if matched else ""), matched, evidence


def search(
    query: str = "",
    route_class: str | None = None,
    status: str | None = None,
    limit: int = 50,
    registry_path: str | Path | None = None,
) -> list[dict[str, Any]]:
    """按类/状态/关键词检索先例（query 匹配 ruling_id/标题/摘要子串；类过滤=全命中集，召回优先）。"""
    q = (query or "").strip().lower()
    cls_filter = (route_class or "").strip().upper() or None
    limit = max(1, min(int(limit), _ROW_LIMIT_MAX))
    results: list[dict[str, Any]] = []
    for entry in load_rulings(registry_path):
        primary, matched, evidence = classify_ruling(entry)
        if cls_filter and cls_filter not in matched:
            continue
        if status and str(entry.get("status") or "") != status:
            continue
        if q:
            rid = str(entry.get("ruling_id") or "").lower()
            text = " ".join(str(entry.get(k) or "") for k in ("title", "summary")).lower()
            if q not in rid and q not in text:
                continue
        results.append({"primary": primary, "matched": matched, "evidence": evidence, "entry": entry})
        if len(results) >= limit:
            break
    return results


def census(registry_path: str | Path | None = None) -> dict[str, Any]:
    """八类普查（主类口径）+未归类计数（>0=路由缺口信号，喂政策 §6 自迭代回路）。"""
    entries = load_rulings(registry_path)
    counts: dict[str, int] = {cls: 0 for cls in _CLASS_NAMES}
    unclassified = 0
    active_by_class: dict[str, int] = {cls: 0 for cls in _CLASS_NAMES}
    for entry in entries:
        primary, _matched, _evidence = classify_ruling(entry)
        if primary:
            counts[primary] += 1
            if str(entry.get("status") or "") == "active":
                active_by_class[primary] += 1
        else:
            unclassified += 1
    return {"total": len(entries), "counts": counts, "active_by_class": active_by_class, "unclassified": unclassified}


def _print_census(data: dict[str, Any]) -> None:
    print(f"裁定册八类普查（真源=ruling_registry.yaml 投影，在册 {data['total']} 条）：")
    for cls, count in data["counts"].items():
        print(f"  {cls} {_CLASS_NAMES[cls]}: {count} 条（active {data['active_by_class'][cls]}）")
    if data["unclassified"]:
        print(f"  未归类: {data['unclassified']} 条（>0=路由缺口信号，E2 零先例=新类流程；登记即归类可消）")
    print("E2 用法：python -m zephyr.library.ruling_precedent <关键词> --class D<N>")


def _print_rows(rows: list[dict[str, Any]]) -> None:
    for row in rows:
        entry = row["entry"]
        also = ",".join(c for c in row["matched"] if c != row["primary"])
        evidence = ";".join(f"{k}={v}" for k, v in list(row["evidence"].items())[:2])
        title = str(entry.get("title") or "")[:60]
        print(
            f"{entry.get('ruling_id')}\t[{row['primary'] or '未归类'}]"
            f"{f' also={also}' if also else ''}\t{entry.get('status')}\t{entry.get('date')}"
            f"\t{evidence}\t{title}"
        )


def _write_cli_audit(session_id: str, payload: dict[str, Any], result_count: int) -> None:
    """审计留痕（同 lookup 裁定#460② 通道）；fail-open 不阻断查询。"""
    try:
        from zephyr.governance.capability_lookup import write_lookup_audit_log  # noqa: PLC0415

        write_lookup_audit_log(
            session_id=session_id,
            query=payload,
            result_count=result_count,
            capability_ids=[],
            tool="zephyr.library.ruling_precedent",
        )
    except Exception as exc:  # noqa: BLE001 — fail-open：审计故障不阻断查询
        import logging

        logging.getLogger(__name__).warning("ruling_precedent: --session 审计留痕失败（fail-open）: %s", exc)


def run_cli(argv: list[str] | None = None) -> int:
    """CLI 入口（退出码：0=有结果/普查，1=无结果；无参数=八类普查）。"""
    parser = argparse.ArgumentParser(
        prog="zephyr.library.ruling_precedent",
        description="裁定先例机检（裁定路由政策 v2 E2 前置；八类 D1-D8 归类检索）",
    )
    parser.add_argument("query", nargs="?", default="", help="关键词（匹配裁定号/标题/摘要；缺省=八类普查）")
    parser.add_argument("--class", dest="route_class", default=None, help="八类过滤（D1-D8；类命中=全命中集）")
    parser.add_argument("--status", default=None, help="状态过滤（active/superseded/deprecated/draft）")
    parser.add_argument("--limit", type=int, default=50, help="上限（默认 50，最大 500）")
    parser.add_argument("--session", default=None, help="session 标识（提供则写 lookup audit 留痕，fail-open）")
    args = parser.parse_args(argv)

    if not args.query.strip() and not (args.route_class or "").strip():
        _print_census(census())
        return 0
    rows = search(args.query, route_class=args.route_class, status=args.status, limit=args.limit)
    if not rows:
        cls_note = f"class={args.route_class.upper()} " if args.route_class else ""
        print(f"(no precedents for {cls_note}query={args.query!r})")
        print('E2 判定：零先例=判"新类"→触发路由表丰富流程（adjudication_routing_policy §2.2）')
        if args.session:
            _write_cli_audit(args.session, {"query": args.query, "face": "ruling_precedent"}, 0)
        return 1
    _print_rows(rows)
    if args.session:
        _write_cli_audit(args.session, {"query": args.query, "face": "ruling_precedent"}, len(rows))
    return 0


def query_face(spec: str) -> int:
    """图书馆总口 ``ruling:`` 检索面委托（lookup.py 调用）。

    spec 形态：``"D3"``/``"D3 <关键词>"``（首 token 命中 D[1-8]=类过滤）或裸关键词。
    """
    text = (spec or "").strip()
    parts = text.split(None, 1)
    cls = None
    query = text
    if parts and re.fullmatch(r"D[1-8]", parts[0].upper()):
        cls = parts[0].upper()
        query = parts[1].strip() if len(parts) > 1 else ""
    return run_cli([query, "--class", cls] if cls else [query])


if __name__ == "__main__":
    sys.exit(run_cli())
