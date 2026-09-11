# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.generate_backtest_backlog
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.shared.io.file_utils; zephyr.shared.io.paths
# [CONSUMERS] SOP-A Step A0/A1/A2; scripts/backtest/verify_run_archive.py(间接); 批次决策点
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 注册先行(SOP-A §1: 无注册条目的回测结果不予归档); 再生成保留既有条目的 plan/threshold_status 字段(禁事后挪门柱——冻结阈值只许批次决策点公开修订); 对象从地图解析导出禁手工挑; 结构容器/流根标 testable=false(行为由子节点承载,D108 合并判据)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 地图缺 nodes/字段异常->BacklogError; --check 模式漂移->退出码1
# [TESTS] python scripts/backtest/generate_backtest_backlog.py --check (smoke)
# [A_module] module_id=MOD-BT-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  A0 登记表再生成 CLI 工具（代码归类表 A 类运维脚本），非常驻服务，批次决策点按需触发
"""SOP-A Step A0：交易决策地图 → 回测对象注册表（backtest_backlog.yaml）生成器。

规范真源：docs/01_policies_and_standards/sop/backtest_system_sop/sop_a_full_map_orchestration.md §1-§3。
落点（裁定修正）：docs/01_policies_and_standards/_registry/catalogs/backtest_backlog.yaml
（预注册=可审计真源，必须进 git；非 SOP-A 原文的 data/ 落点——evidence-log §八关键发现修正）。

推导规则（本文件=规则的代码形态）：
    回测类型: 地图 node_type sensor→sensor / gate→gate / stage→strategy / aggregation+cross_cutting→aggregation；
              语义覆盖（SOP-A §4 判据表点名的判定类）: TDM-E-L2-04 板块级市场状态、TDM-E-L3-06 环境开关、
              TDM-E-L2-05-1 水温档推导 → gate（地图 stage/aggregation 标注不改变其判定语义）。
    优先级（SOP-A §3）: P0={L1-AGG, L1 总闸, 成本模型三件套(cost_model_refs 节点族)}；
              P1=主链{L1 传感器(上游先验), L2-01 族, L3-02→08 漏斗, L4-01/02 时序}；
              P2=树枝{L0 族, L2-02~10 其余, L3-01/09/10/11/12, L4-03~14}；
              P3=流级{P/X/F 族全量}+结构点+crypto 骨架（另册挂起）。
    可测性: 流根(LROOT/PFLOW/XFLOW/CFLOW)与 module_ref=null 的容器环节 → testable=false（纯结构/行为在子节点）；
              module_ref=null 且非容器 → pending_build=true（不许回测不存在的行为）。

用法::
    python scripts/backtest/generate_backtest_backlog.py            # 生成/再生成（保留冻结 plan）
    python scripts/backtest/generate_backtest_backlog.py --check    # 漂移检查（退出码语义）
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Final
from zoneinfo import ZoneInfo

import yaml

_REPO_ROOT: Final = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))

from zephyr.shared.io.file_utils import content_sha256, safe_write_text  # noqa: E402
from zephyr.shared.io.paths import REPO_ROOT  # noqa: E402

_MAP_PATH: Final = REPO_ROOT / "config" / "trading_decision_map.yaml"
_OUT_PATH: Final = (
    REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "backtest_backlog.yaml"
)
_TZ_SH: Final = ZoneInfo("Asia/Shanghai")

# SOP-A §4 判据表点名的判定类覆盖（地图标注 ≠ 判定语义时的显式覆盖表）
_GATE_OVERRIDES: Final[frozenset[str]] = {"TDM-E-L1-AGG", "TDM-E-L2-04", "TDM-E-L3-06", "TDM-E-L2-05-1"}
_STRUCTURAL_LAYERS: Final[frozenset[str]] = {"LROOT", "PFLOW", "XFLOW", "CFLOW"}
# P0 三件套（SOP-A §3 铁行）
_P0_NODE_IDS: Final[set[str]] = {"TDM-E-L1-AGG", "TDM-E-L1"}
_COST_NODE_IDS: Final[set[str]] = {"TDM-E-L4-09", "TDM-P-P2-01", "TDM-P-P2-03", "TDM-X-S2-01"}
# P1 主链（L2-01 板块强度 → L3-02→08 漏斗 → L4 时序）
_P1_NODE_IDS: Final[set[str]] = {
    "TDM-E-L2-01", "TDM-E-L2-01-1", "TDM-E-L2-01-2", "TDM-E-L2-01-3", "TDM-E-L2-01-4", "TDM-E-L2-01-5",
    "TDM-E-L3-02", "TDM-E-L3-03", "TDM-E-L3-03-1", "TDM-E-L3-03-2", "TDM-E-L3-03-3",
    "TDM-E-L3-04", "TDM-E-L3-05", "TDM-E-L3-06", "TDM-E-L3-07", "TDM-E-L3-07-1",
    "TDM-E-L3-07-2", "TDM-E-L3-07-3", "TDM-E-L3-08",
    "TDM-E-L4-01", "TDM-E-L4-02",
}
_P1_SENSOR_LAYER: Final = "L1"   # 传感器=AGG 上游，先上游后下游 → P1 先验批

# P0 预注册阈值草案（AI 提案；threshold_status=draft——批次决策点确认后冻结，禁跑未冻结对象）
_P0_PLANS: Final[dict] = {
    "TDM-E-L1-AGG": {
        "validation_method": "agg_discrimination",
        "min_samples": "每档>=20 次触发且总触发>=30",
        "thresholds": {
            "adjacent_t_test_p": 0.05,
            "top_bottom_spread_20d_pct": 1.0,
        },
        "verdict_mapping": "p<0.05 且高低档差>=1.0%→valid；p<0.10→pending；其余→noise（registry verdict_mapping+数值提案）",
        "threshold_status": "draft",
        "source": "validation_method_registry.yaml agg_discrimination + AI 数值提案 2026-09-12",
    },
    "TDM-E-L1": {
        "validation_method": "agg_discrimination",
        "min_samples": "谨慎度分档每档>=20 且总触发>=30",
        "thresholds": {
            "adjacent_t_test_p": 0.05,
            "high_caution_drawdown_delta_20d_pct": 2.0,
        },
        "verdict_mapping": "高谨慎档后续 20 日最大回撤显著更深（p<0.05 且档差>=2.0%）→valid；方向反→noise",
        "threshold_status": "draft",
        "source": "validation_method_registry.yaml agg_discrimination + 总闸谨慎度语义 + AI 数值提案 2026-09-12",
    },
    "__COST__": {
        "validation_method": "exec_quality",
        "min_samples": "总触发>=30（土规）",
        "thresholds": {
            "slip_bp_valid": 20.0,
            "slip_bp_pending": 40.0,
            "cost_items": "佣金+印花税+滑点+市场冲击+做T额外成本（费率读实际账户配置，禁硬编码）",
        },
        "verdict_mapping": "滑点均值<=20bp→valid；<=40bp→pending；>40bp→noise（registry exec_quality 土规线）",
        "threshold_status": "draft",
        "source": "validation_method_registry.yaml exec_quality（裁定土规线，非 AI 提案）",
    },
}


class BacklogError(Exception):
    """地图解析/生成异常。"""

    error_code = "ZA-BTB-0001"


def _derive_test_type(node: dict) -> str:
    if node.get("node_type") == "sensor":
        return "sensor"
    if node.get("node_type") == "gate":
        return "gate"
    if node["node_id"] in _GATE_OVERRIDES:
        return "gate"
    if node.get("node_type") in ("aggregation", "cross_cutting"):
        return "aggregation"
    return "strategy"


def _derive_priority(node: dict) -> str:
    nid = node["node_id"]
    if nid in _P0_NODE_IDS or nid in _COST_NODE_IDS:
        return "P0"
    if nid in _P1_NODE_IDS:
        return "P1"
    if node.get("market") == "crypto":
        return "P3"
    if node.get("layer") == "L1" and _derive_test_type(node) == "sensor":
        return "P1"
    if node.get("flow") == "entry_flow" and node.get("market") == "cn_a":
        return "P2"
    return "P3"   # P/X/F 流级 + 结构点


def _is_structural(node: dict) -> bool:
    if node.get("layer") in _STRUCTURAL_LAYERS:
        return True
    # module_ref=null 的容器环节（行为由子节点承载，D108 合并判据）
    return node.get("module_ref") is None and node.get("layer") in {"L2", "L3", "L4", "L0", "P1", "P2", "P3", "S1", "S2", "C1", "C2", "C3", "X1"}


def build_objects(map_raw: dict) -> list[dict]:
    nodes = map_raw.get("nodes") or []
    if not nodes:
        raise BacklogError(f"地图无 nodes: {_MAP_PATH}")
    objects: list[dict] = []
    counters: dict[str, int] = {}
    # P0 成本三件套为多节点合并对象（先产出，占用 P0-003）
    cost_nodes = [n for n in nodes if n["node_id"] in _COST_NODE_IDS]
    for n in nodes:
        nid = n["node_id"]
        structural = _is_structural(n)
        if nid in _COST_NODE_IDS:
            continue   # 已并入成本三件套对象
        pri = _derive_priority(n)
        counters[pri] = counters.get(pri, 0) + 1
        obj = {
            "object_id": f"BT-{pri}-{counters[pri]:03d}",
            "node_ids": [nid],
            "node_type": _derive_test_type(n),
            "layer": "L0节点",
            "map_layer": n.get("layer"),
            "flow": n.get("flow"),
            "market": n.get("market"),
            "module_ref": n.get("module_ref"),
            "testable": not structural,
            "confidence": "untested",
        }
        if structural:
            obj["testable"] = False
            obj["testable_note"] = "结构点/容器环节——行为由子节点或全流承载（D108 合并判据），不独立开回测对象"
        elif n.get("module_ref") is None:
            obj["pending_build"] = True   # SOP-A §1：不许回测不存在的行为
        if nid in _P0_PLANS:
            obj["plan"] = dict(_P0_PLANS[nid])
        else:
            obj["plan"] = None
            obj["plan_note"] = "验收阈值未预注册——批次决策点填写并冻结前禁跑（SOP-B 护栏③）"
        objects.append(obj)
    if cost_nodes:
        counters["P0"] = counters.get("P0", 0) + 1
        objects.append({
            "object_id": f"BT-P0-{counters['P0']:03d}",
            "node_ids": sorted(n["node_id"] for n in cost_nodes),
            "node_type": "aggregation",
            "layer": "L0节点",
            "map_layer": "cross_cutting",
            "flow": "cross_flow",
            "market": "cn_a",
            "module_ref": "cost_model_registry(CST-ASTOCK-001/CST-T0-001)",
            "testable": True,
            "confidence": "untested",
            "merge_note": "成本模型三件套（SOP-A P0 铁行）：cost_model_refs 承载节点族合并验证",
            "plan": dict(_P0_PLANS["__COST__"]),
        })
    return objects


# 再生成保留字段（禁事后挪门柱：冻结阈值只许批次决策点公开修订）
_PRESERVE_KEYS: Final[tuple] = ("plan", "plan_note", "confidence", "verdict_ref")
_PRESERVE_BY_NODES: Final = "node_ids"


def _preserve_existing(existing: list[dict], objects: list[dict]) -> tuple[list[dict], list[str]]:
    notes: list[str] = []
    by_nodes = {tuple(o.get("node_ids") or []): o for o in existing}
    for o in objects:
        prev = by_nodes.get(tuple(o.get("node_ids") or []))
        if not prev:
            continue
        if prev.get("object_id") != o["object_id"]:
            notes.append(f"object_id 变更 {prev.get('object_id')} → {o['object_id']}"
                         f"（node_ids={o['node_ids']}，保留原 id 以防台账断链）")
            o["object_id"] = prev["object_id"]   # run 台账按 object_id 回溯——重排编号断链禁忍
        for k in _PRESERVE_KEYS:
            if prev.get(k) is not None:
                o[k] = prev[k]
    return objects, notes


def generate(*, check: bool = False) -> int:
    map_raw = yaml.safe_load(_MAP_PATH.read_text(encoding="utf-8"))
    objects = build_objects(map_raw)
    notes: list[str] = []
    if _OUT_PATH.exists():
        try:
            old = yaml.safe_load(_OUT_PATH.read_text(encoding="utf-8")) or {}
            objects, notes = _preserve_existing(old.get("objects", []), objects)
        except yaml.YAMLError:
            notes.append("既有 backlog YAML 解析失败——按全新生成处理（人工核查！）")
    header = {
        "module_id": "REG-BTB-001",
        "ttl": "permanent",
        "schema_version": "1.0",
        "registry_id": "REG-BTB-001",
        "name": "Backtest Object Backlog",
        "name_zh": "回测对象预注册登记表",
        "description": (
            "SOP-A Step A0 产物：交易决策地图全部节点的回测对象注册（从地图解析导出，禁手工挑）。"
            "预注册=可审计真源（验收阈值跑前写死，禁事后挪门柱；threshold_status=draft 的数值"
            "为 AI 提案，批次决策点确认冻结后才可跑）。再生成保留既有 plan/confidence/object_id"
            "（防台账断链与挪门柱）。真源文档=sop/backtest_system_sop/sop_a_full_map_orchestration.md。"
        ),
        "source_map": "config/trading_decision_map.yaml",
        "map_schema_version": str(map_raw.get("schema_version", "")),
        "map_effective_from": str(map_raw.get("effective_from", "")),
        "generated_at": datetime.now(_TZ_SH).isoformat(timespec="seconds"),  # noqa: m46-time  业务墙钟=Asia/Shanghai 登记时间戳（RULE-SCHEMA-TZ 业务列时区），非系统时钟运算
        "generated_by": "scripts/backtest/generate_backtest_backlog.py",
        "priority_legend": "P0=生死线三件套 P1=主链 P2=树枝 P3=流级/结构/crypto另册",
    }
    if check:
        # 漂移比对剔除 generated_at 时间戳（每次生成必变，非语义漂移）
        def _norm(text: str) -> str:
            return re.sub(r"^generated_at: .*$", "generated_at: <ts>", text, flags=re.M)

        old_text = _OUT_PATH.read_text(encoding="utf-8") if _OUT_PATH.exists() else ""
        new_text = _norm(yaml.safe_dump({**header, "objects": objects}, allow_unicode=True, sort_keys=False, width=100))
        drift = _norm(old_text) != new_text if old_text else True
        print("DRIFT" if drift else "CLEAN")
        return 1 if drift else 0
    text = "# [A_config] module_id=REG-BTB-001 | layer=config | stability=evolving | safety=L | ai_autonomy=ai_modifiable\n"
    text += yaml.safe_dump({**header, "objects": objects}, allow_unicode=True, sort_keys=False, width=100)
    if notes:
        text += "regenerate_notes:\n" + "\n".join(f"- {n}" for n in notes) + "\n"
    base = content_sha256(_OUT_PATH.read_text(encoding="utf-8")) if _OUT_PATH.exists() else None
    result = safe_write_text(_OUT_PATH, text, expected_base_sha256=base, encoding="utf-8", newline="\n")
    print(f"WROTE {_OUT_PATH.relative_to(REPO_ROOT)} objects={len(objects)}"
          f" preserved_notes={len(notes)} ok={getattr(result, 'written', None)}")
    from collections import Counter

    print("by_priority:", dict(Counter(o["object_id"].split("-")[1] for o in objects)))
    print("by_type:", dict(Counter(o["node_type"] for o in objects)))
    print("testable:", sum(1 for o in objects if o.get("testable")),
          "/ structural:", sum(1 for o in objects if not o.get("testable")))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="SOP-A A0：地图→回测对象预注册登记表")
    ap.add_argument("--check", action="store_true", help="漂移检查（不写盘）")
    args = ap.parse_args()
    return generate(check=args.check)


if __name__ == "__main__":
    sys.exit(main())
