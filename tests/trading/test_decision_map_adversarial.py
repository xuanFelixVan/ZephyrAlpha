# [BLUEPRINT] MOD-TRADING-015 | docs/03_modules/_domain_trading/decision_map/blueprint.md
# [DOMAIN] D_TRADING
# [TESTS] tests/trading/test_decision_map_adversarial.py
# [TTL] permanent
"""交易决策地图红蓝极限对抗测试——红队攻击用例 vs 蓝方门禁 R1-R25（D34 Owner 指令）。

红队武器库（每类攻击对应蓝方断言：error 必须拦截 / 合法语义必须放行）：
  A 绕过类：注册表缺失/空地图/目录冒充文件/路径穿越——防违规静默通过（假阴性）
  B 边界值类：卡线 100 字/8 挂载/树深 4/流预算 80——精确放行，+1 必拦
  C 伪装类：大小写/后缀/畸形 node_id/module_id——防枚举与格式绕过
  D 交叉对账类：MOD 锚与 depgraph 缓存不一致/缓存缺失降级/supplement 清洗
  E 组合攻击类：多重违规叠加全报 / feedback 合法回指放行（防误杀）
  F warning 语义类：欠账浮出但 ok=True（防 warning 变相阻断）
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from zephyr.trading.decision_map import (
    load_decision_map,
    validate_decision_map,
)

_REPO = Path(__file__).resolve().parents[2]
_REGISTRY_DIR = _REPO / "docs" / "01_policies_and_standards" / "_registry" / "catalogs"

_KNOWN_STRATEGIES = frozenset(
    {
        "daban-sleeve",
        "default-equity",
        "eventdriven-sleeve",
        "multifactor-sleeve",
        "topn-momentum",
        "intraday-surge-fall",
        "orderbook-imbalance",
        "vwap-reversion",
    }
)


def _node(**overrides) -> dict:
    base = {
        "node_id": "TDM-T-1",
        "name_zh": "测试环节",
        "market": "cn_a",
        "flow": "entry_flow",
        "layer": "L9",
        "node_type": "stage",
        "point": "盘前",
        "decision_question": "测试问题",
        "factor_refs": [],
        "data_refs": [],
        "module_ref": None,
        "strategy_mounts": [],
    }
    base.update(overrides)
    return base


def _write_map(tmp_path: Path, payload: dict) -> Path:
    p = tmp_path / "map.yaml"
    p.write_text(yaml.safe_dump(payload, allow_unicode=True), encoding="utf-8")
    return p


def _write_cache(tmp_path: Path, path_to_mod: dict[str, str]) -> Path:
    """构造 depgraph 扫描缓存（红队可控的 path→blueprint_id 映射）。"""
    entries = {
        path: {"deadbeef": {"path": path, "blueprint_id": mod}} for path, mod in path_to_mod.items()
    }
    p = tmp_path / "dep.json"
    p.write_text(json.dumps({"_meta": {}, "entries": entries}), encoding="utf-8")
    return p


def _payload() -> dict:
    return {
        "schema_version": "1.0",
        "map_id": "TDMAP-ADV",
        "markets": ["cn_a"],
        "nodes": [_node()],
        "edges": [],
        "state_matrix": {"states": ["强势"], "cells": []},
    }


def _validate(tmp_path: Path, payload: dict, registry_dir: Path = _REGISTRY_DIR, cache: Path | None = None):
    dm = load_decision_map(_write_map(tmp_path, payload))
    return validate_decision_map(dm, registry_dir, _KNOWN_STRATEGIES, depgraph_cache=cache)


# ── A 绕过类：违规不得静默通过 ───────────────────────────────────────────────


class TestBypass:
    def test_a1_missing_registry_is_error_not_silent_pass(self, tmp_path: Path) -> None:
        """A1 注册表目录不存在 → R99 error（防引用校验假阴性）。"""
        payload = _payload()
        payload["nodes"][0]["strategy_mounts"] = [
            {"strategy_ref": "daban-sleeve", "confidence": "proposed", "evidence": None}
        ]
        ok, issues = _validate(tmp_path, payload, registry_dir=tmp_path / "no_registry")
        assert ok is False
        assert any(i.code == "R99" and "strategy_registry" in i.detail for i in issues)

    def test_a2_empty_nodes_is_error(self, tmp_path: Path) -> None:
        """A2 空节点地图 → R98 error。"""
        payload = _payload()
        payload["nodes"] = []
        ok, issues = _validate(tmp_path, payload)
        assert ok is False
        assert any(i.code == "R98" and "nodes 为空" in i.detail for i in issues)

    def test_a3_empty_states_is_error(self, tmp_path: Path) -> None:
        """A3 空列轴 → R98 error。"""
        payload = _payload()
        payload["state_matrix"]["states"] = []
        ok, issues = _validate(tmp_path, payload)
        assert ok is False
        assert any(i.code == "R98" and "列轴" in i.detail for i in issues)

    def test_a4_doc_ref_pointing_to_directory(self, tmp_path: Path) -> None:
        """A4 doc_ref 指向目录（docs/ 存在但不是文件）→ R14 error。"""
        payload = _payload()
        payload["nodes"][0]["doc_ref"] = "docs"
        ok, issues = _validate(tmp_path, payload)
        assert ok is False
        assert any(i.code == "R14" and "非文件" in i.detail for i in issues)

    def test_a5_module_ref_pointing_to_directory(self, tmp_path: Path) -> None:
        """A5 module_ref 指向目录 → R19 error。"""
        payload = _payload()
        payload["nodes"][0]["module_ref"] = "src"
        ok, issues = _validate(tmp_path, payload)
        assert ok is False
        assert any(i.code == "R19" and "非文件" in i.detail for i in issues)

    def test_a6_doc_ref_absolute_path_escape(self, tmp_path: Path) -> None:
        """A6 doc_ref 绝对路径（盘符）→ R14 error（防绕过仓库根）。"""
        payload = _payload()
        payload["nodes"][0]["doc_ref"] = "C:/Windows/system32/config.sys"
        ok, issues = _validate(tmp_path, payload)
        assert ok is False
        assert any(i.code == "R14" and "绝对路径" in i.detail for i in issues)

    def test_a7_doc_ref_dotdot_escape(self, tmp_path: Path) -> None:
        """A7 doc_ref 上跳 ../ → R14 error。"""
        payload = _payload()
        payload["nodes"][0]["doc_ref"] = "../AGENTS.md"
        ok, issues = _validate(tmp_path, payload)
        assert ok is False
        assert any(i.code == "R14" and "上跳" in i.detail for i in issues)

    def test_a8_module_ref_dotdot_escape(self, tmp_path: Path) -> None:
        """A8 module_ref 上跳 → R19 error。"""
        payload = _payload()
        payload["nodes"][0]["module_ref"] = "src/zephyr/../../pyproject.toml"
        ok, issues = _validate(tmp_path, payload)
        assert ok is False
        assert any(i.code == "R19" and "上跳" in i.detail for i in issues)


# ── B 边界值类：卡线精确放行，+1 必拦 ─────────────────────────────────────────


class TestBoundary:
    def test_b1_question_exactly_100_passes(self, tmp_path: Path) -> None:
        payload = _payload()
        payload["nodes"][0]["decision_question"] = "问" * 100
        ok, issues = _validate(tmp_path, payload)
        assert ok is True
        assert not any(i.code == "R17" for i in issues)

    def test_b2_question_101_blocked(self, tmp_path: Path) -> None:
        payload = _payload()
        payload["nodes"][0]["decision_question"] = "问" * 101
        ok, issues = _validate(tmp_path, payload)
        assert ok is False
        assert any(i.code == "R17" and "超上限" in i.detail for i in issues)

    def test_b3_data_refs_exactly_8_passes(self, tmp_path: Path) -> None:
        """data_refs 卡线 8 个（需真实存在的 DS-* 才不触发 R5，取 registry 真值）。"""
        reg = yaml.safe_load((_REGISTRY_DIR / "data_asset_registry.yaml").read_text(encoding="utf-8"))
        ds_ids = [d["dataset_id"] for d in reg["datasets"]][:8]
        payload = _payload()
        payload["nodes"][0]["data_refs"] = ds_ids
        ok, issues = _validate(tmp_path, payload)
        assert ok is True
        assert not any(i.code == "R17" and "data_refs" in i.detail for i in issues)

    def test_b4_tree_depth_exactly_4_passes(self, tmp_path: Path) -> None:
        """树深 4（根→1→2→3→4 共 5 节点链）→ 放行。"""
        payload = _payload()
        for i in range(2, 6):
            payload["nodes"].append(
                _node(
                    node_id=f"TDM-T-{i}",
                    name_zh=f"环节{i}",
                    parent_node=f"TDM-T-{i-1}",
                    activation="intraday",
                    ai_autonomy="auto",
                )
            )
        ok, issues = _validate(tmp_path, payload)
        assert ok is True
        assert not any(i.code == "R16" and "树深度" in i.detail for i in issues)

    def test_b5_tree_depth_5_blocked(self, tmp_path: Path) -> None:
        payload = _payload()
        for i in range(2, 7):
            payload["nodes"].append(
                _node(
                    node_id=f"TDM-T-{i}",
                    name_zh=f"环节{i}",
                    parent_node=f"TDM-T-{i-1}",
                    activation="intraday",
                    ai_autonomy="auto",
                )
            )
        ok, issues = _validate(tmp_path, payload)
        assert ok is False
        assert any(i.code == "R16" and "树深度" in i.detail for i in issues)

    def test_b6_flow_budget_81_warns_not_blocks(self, tmp_path: Path) -> None:
        """R23 流预算 81 节点 → warning 但 ok=True（软预算防膨胀提示）。"""
        payload = _payload()
        for i in range(2, 82):
            payload["nodes"].append(_node(node_id=f"TDM-T-{i:03d}", name_zh=f"环节{i}"))
        ok, issues = _validate(tmp_path, payload)
        assert ok is True
        assert any(i.code == "R23" and "超预算" in i.detail for i in issues)


# ── C 伪装类：大小写/后缀/畸形格式 ────────────────────────────────────────────


class TestDisguise:
    def test_c1_lowercase_node_id(self, tmp_path: Path) -> None:
        payload = _payload()
        payload["nodes"][0]["node_id"] = "tdm-e-l1"
        ok, issues = _validate(tmp_path, payload)
        assert ok is False
        assert any(i.code == "R20" for i in issues)

    def test_c2_two_segment_node_id(self, tmp_path: Path) -> None:
        payload = _payload()
        payload["nodes"][0]["node_id"] = "TDM-E"
        ok, issues = _validate(tmp_path, payload)
        assert ok is False
        assert any(i.code == "R20" for i in issues)

    def test_c3_module_id_with_suffix_disguise(self, tmp_path: Path) -> None:
        """module_id 带 "supplement" 后缀伪装 → R21 格式拦截。"""
        payload = _payload()
        payload["nodes"][0]["module_id"] = "MOD-SIG-026 supplement"
        ok, issues = _validate(tmp_path, payload)
        assert ok is False
        assert any(i.code == "R21" and "MOD-*" in i.detail for i in issues)

    def test_c4_activation_case_disguise(self, tmp_path: Path) -> None:
        payload = _payload()
        payload["nodes"][0]["activation"] = "Intraday"
        ok, issues = _validate(tmp_path, payload)
        assert ok is False
        assert any(i.code == "R15" and "activation 非法" in i.detail for i in issues)

    def test_c5_strategy_ref_case_disguise(self, tmp_path: Path) -> None:
        payload = _payload()
        payload["nodes"][0]["strategy_mounts"] = [
            {"strategy_ref": "Daban-Sleeve", "confidence": "proposed", "evidence": None}
        ]
        ok, issues = _validate(tmp_path, payload)
        assert ok is False
        assert any(i.code == "R3" and "Daban-Sleeve" in i.detail for i in issues)

    def test_c6_vague_word_embedded_in_long_question(self, tmp_path: Path) -> None:
        """模糊词藏在长句中间 → R17 必须抓到。"""
        payload = _payload()
        payload["nodes"][0]["decision_question"] = "涨停家数不足二十家且炸板率超四成时看情况降仓位到半仓以下运行"
        ok, issues = _validate(tmp_path, payload)
        assert ok is False
        assert any(i.code == "R17" and "模糊词" in i.detail for i in issues)


# ── D 交叉对账类：MOD 锚 vs depgraph 缓存 ────────────────────────────────────


class TestCrossReconciliation:
    def test_d1_module_id_cache_mismatch(self, tmp_path: Path) -> None:
        """module_id 与缓存 blueprint_id 不一致 → R21 error（文件真实存在，隔离 R19 干扰）。"""
        real = "src/zephyr/trading/decision_map.py"
        cache = _write_cache(tmp_path, {real: "MOD-AAA-001"})
        payload = _payload()
        payload["nodes"][0]["module_ref"] = real
        payload["nodes"][0]["module_id"] = "MOD-BBB-002"
        ok, issues = _validate(tmp_path, payload, cache=cache)
        assert ok is False
        assert any(i.code == "R21" and "不一致" in i.detail for i in issues)

    def test_d2_module_id_cache_match_ok(self, tmp_path: Path) -> None:
        real = "src/zephyr/trading/decision_map.py"
        cache = _write_cache(tmp_path, {real: "MOD-AAA-001"})
        payload = _payload()
        payload["nodes"][0]["module_ref"] = real
        payload["nodes"][0]["module_id"] = "MOD-AAA-001"
        ok, issues = _validate(tmp_path, payload, cache=cache)
        assert ok is True
        assert not any(i.code == "R21" and i.level == "error" for i in issues)

    def test_d3_missing_cache_degrades_to_warning(self, tmp_path: Path) -> None:
        payload = _payload()
        payload["nodes"][0]["module_ref"] = "src/zephyr/trading/decision_map.py"
        payload["nodes"][0]["module_id"] = "MOD-AAA-001"
        ok, issues = _validate(tmp_path, payload, cache=tmp_path / "no_cache.json")
        assert ok is True
        assert any(i.code == "R21" and i.level == "warning" and "缓存缺失" in i.detail for i in issues)

    def test_d4_supplement_suffix_cleaned_in_cache(self, tmp_path: Path) -> None:
        real = "src/zephyr/trading/decision_map.py"
        cache = _write_cache(tmp_path, {real: "MOD-SIG-026 supplement"})
        payload = _payload()
        payload["nodes"][0]["module_ref"] = real
        payload["nodes"][0]["module_id"] = "MOD-SIG-026"
        ok, issues = _validate(tmp_path, payload, cache=cache)
        assert ok is True
        assert not any(i.code == "R21" and i.level == "error" for i in issues)

    def test_d5_module_ref_without_module_id_warns(self, tmp_path: Path) -> None:
        """有 module_ref 无 module_id → R21 欠账 warning（不阻断）。"""
        payload = _payload()
        payload["nodes"][0]["module_ref"] = "src/zephyr/trading/decision_map.py"
        ok, issues = _validate(tmp_path, payload)
        assert ok is True
        assert any(i.code == "R21" and "交叉锚欠账" in i.detail for i in issues)


# ── E 组合攻击类：多重违规叠加 ───────────────────────────────────────────────


class TestCombined:
    def test_e1_multi_violation_all_reported(self, tmp_path: Path) -> None:
        """一次塞入 5 类违规 → 每类门禁各自报出（不漏报）。"""
        payload = _payload()
        payload["nodes"].append(_node(node_id="tdm-bad", name_zh="测试环节"))
        payload["nodes"][0]["decision_question"] = "问" * 150 + "到时候再说"
        payload["nodes"][0]["strategy_mounts"] = [
            {"strategy_ref": "daban-sleeve", "confidence": "proposed", "evidence": None}
        ] * 9
        payload["nodes"][0]["activation"] = "半夜"
        payload["nodes"][0]["parent_node"] = "TDM-GHOST"
        ok, issues = _validate(tmp_path, payload)
        assert ok is False
        codes = {i.code for i in issues if i.level == "error"}
        assert {"R17", "R18", "R15", "R16", "R20"} <= codes

    def test_e2_feedback_backedge_allowed(self, tmp_path: Path) -> None:
        """feedback 边回指 → 放行（指数↔情绪合法双向，防误杀）。"""
        payload = _payload()
        payload["nodes"].append(_node(node_id="TDM-T-2", name_zh="第二环节"))
        payload["edges"] = [
            {"from_node": "TDM-T-1", "to_node": "TDM-T-2", "edge_type": "sequence"},
            {"from_node": "TDM-T-2", "to_node": "TDM-T-1", "edge_type": "feedback"},
        ]
        ok, issues = _validate(tmp_path, payload)
        assert ok is True
        assert not any(i.code == "R8" for i in issues)

    def test_e3_self_parent_cycle(self, tmp_path: Path) -> None:
        """自指 parent → R16 成环 error。"""
        payload = _payload()
        payload["nodes"][0]["parent_node"] = "TDM-T-1"
        ok, issues = _validate(tmp_path, payload)
        assert ok is False
        assert any(i.code == "R16" and "成环" in i.detail for i in issues)


# ── F warning 语义类：欠账浮出但不阻断 ────────────────────────────────────────


class TestWarningSemantics:
    def test_f1_factor_debt_warns_but_ok(self, tmp_path: Path) -> None:
        """挂策略无因子 → R24 warning 且 ok=True。"""
        payload = _payload()
        payload["nodes"][0]["strategy_mounts"] = [
            {"strategy_ref": "daban-sleeve", "confidence": "proposed", "evidence": None}
        ]
        ok, issues = _validate(tmp_path, payload)
        assert ok is True
        assert any(i.code == "R24" and i.level == "warning" for i in issues)

    def test_f2_idle_leaf_warns_but_ok(self, tmp_path: Path) -> None:
        """叶子节点零引用 → R25 warning 且 ok=True。"""
        payload = _payload()
        ok, issues = _validate(tmp_path, payload)
        assert ok is True
        assert any(i.code == "R25" and i.level == "warning" for i in issues)

    def test_f3_matrix_uncovered_warns_but_ok(self, tmp_path: Path) -> None:
        """挂策略未进矩阵 → R22 warning 且 ok=True。"""
        payload = _payload()
        payload["nodes"][0]["strategy_mounts"] = [
            {"strategy_ref": "daban-sleeve", "confidence": "proposed", "evidence": None}
        ]
        ok, issues = _validate(tmp_path, payload)
        assert ok is True
        assert any(i.code == "R22" and i.level == "warning" for i in issues)

    def test_f4_repo_map_full_gates_still_green(self) -> None:
        """真源地图对抗回归锚：R1-R25 全门禁下 error=0（欠账 warning 允许存在）。

        D35 因子补挂后：R24（因子欠账）必须清零、R21 必须无脏数据；
        R25（空转叶子）/R22（矩阵未覆盖）/R1（红节点占位）为血肉阶段持续欠账，必须浮出。
        """
        dm = load_decision_map(_REPO / "config" / "trading_decision_map.yaml")
        ok, issues = validate_decision_map(dm, _REGISTRY_DIR, _KNOWN_STRATEGIES)
        assert ok is True, [i for i in issues if i.level == "error"]
        codes = {i.code for i in issues}
        # 已清账：因子交叉欠账（R24）与 MOD 脏数据（R21）不得复发
        assert "R24" not in codes, "R24 因子欠账复发（挂策略节点 factor_refs 又空了）"
        assert not any(i.code == "R21" for i in issues), "R21 脏 MOD 复发"
        # 持续欠账：必须可见（防门禁静默失效）
        assert {"R25", "R22"} <= codes
