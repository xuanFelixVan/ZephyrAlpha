# [BLUEPRINT] MOD-D5_ARCH_TOOLS | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""test_mount_route_consistency.py — 挂图路由真源一致性守卫（2026-09-15 双层分离批）

背景：挂图路由原埋在 auto_mount.CLASS_NODE_MAP 代码常量里，与注册表 strategy_class
（知识身份层）耦合——C5 批临时类 vs 家族法的静默漂移即由此生。双层分离后：

- 路由真源 = 注册表 mount_route 字段（显式，逐策略）
- 家族兜底 = auto_mount.FAMILY_DEFAULT_ROUTE（仅无歧义家族，白名单制）
- 本守卫 = 双向漂移检测：路由目标必须存在于决策图；已路由策略必须真的挂在图上。

测试隔离：只读注册表与决策图 YAML（git 真源），无 DB 依赖。
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

_REGISTRY = _PROJECT_ROOT / "docs/01_policies_and_standards/_registry/catalogs/strategy_registry.yaml"
_MAP = _PROJECT_ROOT / "config/trading_decision_map.yaml"


def _routed() -> dict[str, str]:
    data = yaml.safe_load(_REGISTRY.read_text(encoding="utf-8"))
    return {e["strategy_id"]: e["mount_route"] for e in data.get("strategies", [])
            if e.get("mount_route")}


def _map_nodes() -> dict[str, dict]:
    data = yaml.safe_load(_MAP.read_text(encoding="utf-8"))
    return {n["node_id"]: n for n in data.get("nodes", [])}


class TestRouteTargetsExist:
    """路由字段的每个目标必须是决策图真实节点（防幽灵节点路由）。"""

    def test_all_route_targets_are_map_nodes(self):
        nodes = _map_nodes()
        bad = {sid: r for sid, r in _routed().items() if r not in nodes}
        assert not bad, f"mount_route 指向不存在的节点: {bad}"

    def test_route_values_are_tdm_nodes(self):
        bad = {sid: r for sid, r in _routed().items() if not r.startswith("TDM-")}
        assert not bad, f"mount_route 非 TDM 决策图节点: {bad}"


class TestRouteResidentsMounted:
    """已路由策略必须真的挂在目标节点的 strategy_mounts 上（注册表↔地图双向对账）。"""

    def test_routed_sids_present_in_node_mounts(self):
        nodes = _map_nodes()
        missing = []
        for sid, route in sorted(_routed().items()):
            mounts = nodes.get(route, {}).get("strategy_mounts") or []
            refs = {m.get("strategy_ref") for m in mounts}
            if sid not in refs:
                missing.append(f"{sid} -> {route}（地图 strategy_mounts 无此条）")
        assert not missing, "已路由未挂图:\n" + "\n".join(missing)


class TestFamilyFallbackSafety:
    """家族兜底路由只收无歧义家族，且目标节点存在（防兜底误挂）。"""

    def test_fallback_whitelist_and_targets(self):
        sys.path.insert(0, str(_PROJECT_ROOT / "scripts"))
        from backtest.auto_mount import FAMILY_DEFAULT_ROUTE  # noqa: E402

        nodes = _map_nodes()
        allowed = {"multifactor"}  # S07-G2 打分链兜底；扩白名单须过架构评审（同族路由异构禁兜底）
        assert set(FAMILY_DEFAULT_ROUTE) <= allowed, (
            f"兜底白名单外家族: {set(FAMILY_DEFAULT_ROUTE) - allowed}")
        bad = {cls: n for cls, n in FAMILY_DEFAULT_ROUTE.items() if n not in nodes}
        assert not bad, f"兜底路由指向不存在节点: {bad}"


class TestCellStateLaw:
    """格律法（2026-09-15 insert_cell 全格扩散 bug 治本配套）：
    状态格里的 STR-* 必须 (a) 路由指向该节点 (b) 该态在其家族候选态内。"""

    def test_cell_members_are_routed_and_in_candidate_states(self):
        sys.path.insert(0, str(_PROJECT_ROOT / "scripts"))
        from backtest.auto_mount import CLASS_CANDIDATE_STATES  # noqa: E402

        reg = yaml.safe_load(_REGISTRY.read_text(encoding="utf-8"))
        cls_of = {e["strategy_id"]: e.get("strategy_class") for e in reg.get("strategies", [])}
        route_of = {e["strategy_id"]: e.get("mount_route") for e in reg.get("strategies", [])}
        data = yaml.safe_load(_MAP.read_text(encoding="utf-8"))
        cells = (data.get("state_matrix") or {}).get("cells") or []
        bad = []
        for c in cells:
            state, node = c.get("state"), c.get("node_id")
            for sid in (c.get("mounted") or []):
                if not str(sid).startswith("STR-"):
                    continue  # 旧 sleeve 命名不在此律
                if sid not in cls_of:
                    continue  # 注册表外悬挂 sid（如 VREV-027 未入库遗留）=注册表属主线另册清理，非本律
                fam = cls_of.get(sid)
                cands = CLASS_CANDIDATE_STATES.get(fam, set())
                if route_of.get(sid) != node:
                    bad.append(f"{node}/{state}: {sid} route={route_of.get(sid)}")
                elif cands is None:
                    bad.append(f"{node}/{state}: {sid} 选股族无状态格")
                elif state not in cands:
                    bad.append(f"{node}/{state}: {sid} 态外挂载（{state}∉{sorted(cands)}）")
        assert not bad, "格律法违规:\n" + "\n".join(bad)
