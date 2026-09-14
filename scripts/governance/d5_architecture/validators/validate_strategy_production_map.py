# [BLUEPRINT] MOD-BT-080 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.governance.d5_architecture.validators.validate_strategy_production_map
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] yaml; zephyr.data.ch_config(仅 check-stores 模式)
# [CONSUMERS] 策略生产全景图（config/strategy_production_map.yaml）质量门禁；
#   tests/backtest/test_strategy_production_map_adversarial.py；
#   zephyr.gov_enforcement.commit_gates.strategy_factory_map_gate（FACTORY-MAP gate，
#   结构校验单一真源复用）；scripts.governance.d5_architecture.generators.align_all（第八节）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 台账只读（本工具禁写）；结构错误=exit 1，警告（待定入库位）不阻断；
#   检查项=字段完整性/边引用闭合/层位合法/laws 存在/反馈环声明/自环拒绝/built 必有锚/
#   lane 必带归属/store_refs 三要素；判噪音规则=v0.2 schema 真源
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SystemExit(1)=结构违规; SystemExit(2)=文件/解析失败
# [TESTS] tests/backtest/test_strategy_production_map_adversarial.py
# [A_module] module_id=MOD-BT-080 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""策略生产全景图结构校验器——v0.2 schema 的字段完整性/边闭合/层位/laws/仓储存在性校验。

对照 TDM decision_map validate 的工厂版：本工具只读校验 config/strategy_production_map.yaml，
不修改任何文件。结构错误（缺字段/断边/非法层位/built 无锚等）exit 1；
"待定"入库位为警告不阻断（对应施工前占位声明）。
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

DEFAULT_MAP = Path("config/strategy_production_map.yaml")
REQUIRED_TOP = ["schema_version", "map_id", "name_zh", "layers", "nodes", "edges",
                "laws", "products", "boundary", "feedback_loops"]
REQUIRED_NODE = ["node_id", "name_zh", "stage", "node_type", "decision_question",
                 "algo_note_zh", "compute_class", "build_status", "data_refs",
                 "design_refs", "store_refs"]
COMPUTE_CLASSES = {"local", "local_gpu", "api", "mixed"}
BUILD_STATUS = {"built", "pending", "partial"}
NODE_TYPES = {"stage", "lane"}
STAGES = [f"E{i}" for i in range(10)]


def _err(errors: list[str], msg: str) -> None:
    errors.append(msg)


def validate_structure(data: dict) -> list[str]:
    errors: list[str] = []
    for k in REQUIRED_TOP:
        if k not in data:
            _err(errors, f"缺顶层必填键: {k}")
    if errors:
        return errors
    if not data.get("laws"):
        _err(errors, "laws（全图铁律）不得为空")
    if not data.get("products"):
        _err(errors, "products（工厂产品清单）不得为空")

    layers = {l.get("layer_id") for l in data.get("layers", [])}
    for s in STAGES:
        if s not in layers:
            _err(errors, f"缺标准环节层位: {s}")

    nodes = data.get("nodes", [])
    ids: list[str] = []
    for n in nodes:
        nid = n.get("node_id", "<无 node_id>")
        ids.append(nid)
        for f in REQUIRED_NODE:
            if f not in n or n[f] in (None, ""):
                _err(errors, f"{nid}: 缺必填字段 {f}")
        if n.get("stage") not in STAGES:
            _err(errors, f"{nid}: stage 非法 {n.get('stage')!r}")
        if n.get("node_type") not in NODE_TYPES:
            _err(errors, f"{nid}: node_type 非法 {n.get('node_type')!r}")
        if n.get("node_type") == "lane" and not n.get("lane"):
            _err(errors, f"{nid}: lane 节点必须带 lane 归属")
        if n.get("compute_class") not in COMPUTE_CLASSES:
            _err(errors, f"{nid}: compute_class 非法 {n.get('compute_class')!r}")
        if n.get("build_status") not in BUILD_STATUS:
            _err(errors, f"{nid}: build_status 非法 {n.get('build_status')!r}")
        if n.get("build_status") == "built" and not n.get("module_ref"):
            _err(errors, f"{nid}: built 节点必须有 module_ref 代码锚")
        if len(str(n.get("decision_question", ""))) > 120:
            _err(errors, f"{nid}: decision_question 超 120 字")
        for sr in n.get("store_refs", []):
            if not sr.get("artifact") or not sr.get("location") or not sr.get("retention"):
                _err(errors, f"{nid}: store_refs 条目缺 artifact/location/retention")

    if len(ids) != len(set(ids)):
        _err(errors, "node_id 存在重复")

    valid_ids = set(ids)
    seen_edges: set[tuple[str, str]] = set()
    feedback: set[tuple[str, str]] = {
        (f.get("from"), f.get("to")) for f in data.get("feedback_loops", [])}
    import re

    def _stage_num(node_id: str):
        m = re.match(r"FAC-E(\d+)$", node_id)
        return int(m.group(1)) if m else None

    for e in data.get("edges", []):
        if len(e) != 2:
            _err(errors, f"边格式非法（须 [from,to]）: {e}")
            continue
        a, b = e[0], e[1]
        if a not in valid_ids or b not in valid_ids:
            _err(errors, f"边引用了不存在的节点: {a}->{b}")
            continue
        if (a, b) in seen_edges:
            _err(errors, f"重复边: {a}->{b}")
        seen_edges.add((a, b))
        if a == b:
            _err(errors, f"自环边: {a}")
        if (a, b) in feedback:
            continue
        sa, sb = _stage_num(a), _stage_num(b)
        if sa is not None and sb is not None and sa > sb:
            _err(errors, f"未声明为反馈环的反向边: {a}->{b}（反馈环必须在 "
                         f"feedback_loops 显式声明）")
    return errors


def check_stores(data: dict, root: Path | None = None) -> tuple[list[str], list[str]]:
    """store_refs 入库位存在性：磁盘路径或 CH 表（c1_x.y 形态）。待定=警告。

    Args:
        data: 图 YAML 解析结果。
        root: 磁盘路径解析根（默认 cwd；align_all 第八节传仓库根防 CWD 漂移，
              2026-09-13 九图挂轴批扩展）。
    """
    errors: list[str] = []
    warnings: list[str] = []
    root = root or Path.cwd()
    seen_targets: set[str] = set()
    for n in data.get("nodes", []):
        for sr in n.get("store_refs", []):
            loc = str(sr.get("location", ""))
            if loc not in seen_targets:
                seen_targets.add(loc)
                if loc.startswith("待定"):
                    warnings.append(f"{n.get('node_id')}: 入库位待定（施工时定）: {loc}")
                    continue
                for part in loc.split(" + "):
                    part = part.strip()
                    if not part:
                        continue
                    if part.startswith("c1_") and "." in part:
                        try:
                            from zephyr.infrastructure.database_service import get_db_service
                            db, tbl = part.split(".", 1)
                            cli = get_db_service().get_clickhouse_conn(role="reader")
                            if not cli.execute(f"EXISTS TABLE {db}.{tbl}")[0][0]:
                                errors.append(f"CH 表不存在: {part}")
                        except Exception as exc:  # noqa: BLE001
                            errors.append(f"CH 表检查失败 {part}: {exc}")
                    elif not (root / part).exists():
                        errors.append(f"路径不存在: {part}")
    return errors, warnings


def main() -> int:
    ap = argparse.ArgumentParser(description="策略生产全景图结构+仓储校验（只读）")
    ap.add_argument("--map", default=str(DEFAULT_MAP), help="图 YAML 路径")
    ap.add_argument("--skip-stores", action="store_true", help="跳过仓储存在性检查")
    args = ap.parse_args()
    path = Path(args.map)
    if not path.exists():
        print(f"FAIL: 图文件不存在: {path}", file=sys.stderr)
        return 2
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        print(f"FAIL: YAML 解析失败: {exc}", file=sys.stderr)
        return 2
    if not isinstance(data, dict):
        print("FAIL: YAML 顶层非对象", file=sys.stderr)
        return 2

    errors = validate_structure(data)
    if not args.skip_stores:
        s_errors, s_warnings = check_stores(data)
        errors.extend(s_errors)
        for w in s_warnings:
            print(f"WARN: {w}")
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        print(f"FAILED: {len(errors)} 个结构违规", file=sys.stderr)
        return 1
    print(f"PASS: 结构校验通过（nodes={len(data['nodes'])} edges={len(data['edges'])}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
