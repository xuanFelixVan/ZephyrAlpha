# [BLUEPRINT] MOD-BT-171 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_auto_mount
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts.backtest.auto_mount
# [CONSUMERS] MOD-BT-171 循环验收
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 测试隔离（tmp_path fixture，禁写生产路径）；手术函数纯文本测试零 IO；
#   红蓝门测试=伪造删行必被拒
# [MODIFY-GUARD] scripts/backtest/auto_mount.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红
# [TESTS] 本文件
# [A_module] module_id=MOD-BT-171 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""auto_mount 单元测试——文本手术引擎+only-add 红蓝门+映射表规则（MOD-BT-171）。"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from backtest.auto_mount import (  # noqa: E402
    CLASS_CANDIDATE_STATES,
    FAMILY_DEFAULT_ROUTE,
    IS_WIN,
    MIN_SEG_DAYS,
    NEW_SLEEVE_WEIGHT,
    R2SIX,
    insert_cell,
    insert_node_mount,
    insert_sleeve,
    mount_audit,
    only_add_assert,
    sleeve_plan,
    write_report,
)

# ---------- fixtures：最小地图片段（真实格式的等价样本） ----------
NODE_BLOCK = """- node_id: TDM-E-L1
  name_zh: 大盘总闸
  strategy_mounts:
  - {strategy_ref: STR-VREV-025, confidence: verified, evidence: 'run=x'}
  materiality: critical
  decay_scan_frequency: monthly
"""

CELLS = """  cells:
  - {node_id: TDM-E-L1, state: capitulation, mounted: [STR-VREV-025], confidence: proposed}
  - {node_id: TDM-E-L1, state: accumulation, mounted: [], confidence: proposed}
"""

SLEEVES = """  sleeves:
  - {strategy_ref: default-equity, weight: 0.14, activation_state: null}
  - {strategy_ref: STR-VREV-025, weight: 0.05, activation_state: [capitulation]}
  # 注释行
"""


# ---------- ① 映射表规则 ----------
class TestMappingRules:
    def test_family_fallback_route_whitelisted(self):
        # 2026-09-16 双层分离批：路由真源=注册表 mount_route 字段；代码兜底表只收无歧义家族。
        # multifactor=打分链（S07-G2 derive_class 兜底）；其余家族同族路由异构（value_reversal
        # 既有个股反转也有指数择时），设兜底必误挂——白名单外新增须先过架构评审。
        assert set(FAMILY_DEFAULT_ROUTE) == {"multifactor"}
        assert FAMILY_DEFAULT_ROUTE["multifactor"] == "TDM-E-L3-07-2"

    def test_candidate_states_keyed_by_family(self):
        # 候选态按分类家族键：择时类家族必须有候选态；选股/打分类 None 或缺省（缺省=不挂状态格）
        assert CLASS_CANDIDATE_STATES["value_reversal"] == {"capitulation", "accumulation"}
        assert CLASS_CANDIDATE_STATES["momentum_trend"] == {"expansion", "ignition"}
        assert CLASS_CANDIDATE_STATES["daban"] == {"accumulation", "expansion"}
        assert CLASS_CANDIDATE_STATES["multifactor"] is None
        assert CLASS_CANDIDATE_STATES.get("sector_rotation", set()) == set()

    def test_route_resolution_prefers_explicit(self):
        # 显式 mount_route 优先于家族兜底（TSMALL/VAL 虽归 multifactor，路由仍走 L3-07-3 选股链）
        e = {"route": "TDM-E-L3-07-3", "cls": "multifactor"}
        assert (e.get("route") or FAMILY_DEFAULT_ROUTE.get(e["cls"])) == "TDM-E-L3-07-3"
        e2 = {"route": None, "cls": "multifactor"}
        assert (e2.get("route") or FAMILY_DEFAULT_ROUTE.get(e2["cls"])) == "TDM-E-L3-07-2"

    def test_r2six_states_are_six_phase(self):
        valid = {"capitulation", "accumulation", "ignition", "expansion", "euphoria", "distribution"}
        assert set(R2SIX.values()) <= valid
        assert "r1" not in R2SIX and "r2" not in R2SIX  # 低波/中波保守不路由（宁漏勿误）


# ---------- ② 文本级手术 ----------
class TestTextSurgery:
    def test_insert_node_mount_appends_and_idempotent(self):
        once = insert_node_mount(NODE_BLOCK, "TDM-E-L1", "STR-TEST-001", "evidence run=y")
        assert "strategy_ref: STR-TEST-001" in once
        assert "STR-VREV-025" in once  # 既有挂载保留（only-add）
        with pytest.raises(AssertionError):  # 幂等：已挂再插必拒
            insert_node_mount(once, "TDM-E-L1", "STR-TEST-001", "again")

    def test_insert_node_mount_bad_anchor(self):
        with pytest.raises(AssertionError):
            insert_node_mount("- node_id: TDM-X\n  name_zh: 无挂载区\n", "TDM-X", "STR-A", "e")

    def test_insert_cell_state_aware(self):
        # 2026-09-16 治本：一格一插，兄弟格子零扰动（旧实现向全部格子扩散，VREV-027 曾被污染四格）
        out = insert_cell(CELLS, "TDM-E-L1", "capitulation", "STR-TEST-001")
        assert "state: capitulation, mounted: [STR-VREV-025, STR-TEST-001]" in out
        assert "state: accumulation, mounted: []" in out  # 兄弟格零扰动
        assert out.count("confidence: proposed") == CELLS.count("confidence: proposed")
        with pytest.raises(AssertionError):  # 幂等：已在该格再插必拒
            insert_cell(out, "TDM-E-L1", "capitulation", "STR-TEST-001")
        out2 = insert_cell(CELLS, "TDM-E-L1", "accumulation", "STR-TEST-002")
        assert "state: accumulation, mounted: [STR-TEST-002]" in out2
        assert "state: capitulation, mounted: [STR-VREV-025]" in out2

    def test_insert_cell_unknown_state_rejected(self):
        with pytest.raises(AssertionError):
            insert_cell(CELLS, "TDM-E-L1", "nonexistent_state", "STR-TEST-001")

    def test_insert_sleeve_appends_after_last_str(self):
        out = insert_sleeve(SLEEVES, "STR-TEST-001", ["capitulation"])
        assert "strategy_ref: STR-TEST-001, weight: 0.05, activation_state: [capitulation]" in out
        lines = [l for l in out.splitlines() if "strategy_ref:" in l]
        assert lines[-1].startswith("  - {strategy_ref: STR-TEST-001")  # 追加在最后一条 STR 后
        null_case = insert_sleeve(SLEEVES, "STR-TEST-002", None)
        assert "activation_state: null" in null_case

    def test_insert_sleeve_anchor_not_unique(self):
        dup = SLEEVES + "  sleeves:\n"
        with pytest.raises(AssertionError):
            insert_sleeve(dup, "STR-A", None)


# ---------- ③ only-add 红蓝门（语义级） ----------
MAP_MIN = """nodes:
- node_id: TDM-E-L1
  name_zh: 大盘总闸
  strategy_mounts:
  - {strategy_ref: STR-VREV-025, confidence: verified, evidence: 'run=x'}
state_matrix:
  cells:
  - {node_id: TDM-E-L1, state: capitulation, mounted: [STR-VREV-025], confidence: proposed}
portfolio_plan:
  plan_id: PP-001
  sleeves:
  - {strategy_ref: default-equity, weight: 0.14, activation_state: null}
  - {strategy_ref: topn-momentum, weight: 0.07, activation_state: null}
"""


class TestOnlyAddGate:
    def test_semantic_additions_pass(self):
        added = MAP_MIN + """  - {strategy_ref: STR-NEW-001, weight: 0.05, activation_state: null}
"""
        only_add_assert(MAP_MIN, added)  # 新增 sleeve+等比缩水=立项设计行为，放行

    def test_forged_mount_deletion_rejected(self):
        tampered = MAP_MIN.replace("  - {strategy_ref: STR-VREV-025, confidence: verified, evidence: 'run=x'}\n", "")
        with pytest.raises(AssertionError, match="only-add"):
            only_add_assert(MAP_MIN, tampered)

    def test_modified_evidence_rejected(self):
        tampered = MAP_MIN.replace("run=x", "run=mutated")
        with pytest.raises(AssertionError):
            only_add_assert(MAP_MIN, tampered)

    def test_cell_deletion_rejected(self):
        tampered = MAP_MIN.replace("  - {node_id: TDM-E-L1, state: capitulation, mounted: [STR-VREV-025], confidence: proposed}\n", "")
        with pytest.raises(AssertionError):
            only_add_assert(MAP_MIN, tampered)

    def test_cell_mount_shrink_rejected(self):
        tampered = MAP_MIN.replace("mounted: [STR-VREV-025]", "mounted: []")
        with pytest.raises(AssertionError):
            only_add_assert(MAP_MIN, tampered)

    def test_non_proportional_weight_change_rejected(self):
        tampered = MAP_MIN.replace("weight: 0.14", "weight: 0.20")
        with pytest.raises(AssertionError, match="非等比"):
            only_add_assert(MAP_MIN, tampered)

    def test_new_sleeve_wrong_starter_rejected(self):
        tampered = MAP_MIN + "  - {strategy_ref: STR-NEW-001, weight: 0.08, activation_state: null}\n"
        with pytest.raises(AssertionError, match="起步档"):
            only_add_assert(MAP_MIN, tampered)


# ---------- ④ 等权起步档 ----------
class TestSleevePlan:
    def test_scale_preserves_total(self):
        old = [{"strategy_ref": "a", "weight": 0.14}, {"strategy_ref": "b", "weight": 0.105},
               {"strategy_ref": "c", "weight": 0.07}]
        plan = sleeve_plan(["STR-X", "STR-Y"], old)
        assert plan["STR-X"] == plan["STR-Y"] == NEW_SLEEVE_WEIGHT
        assert abs(sum(plan.values()) - 1.0) < 1e-9

    def test_old_weights_shrink_not_reorder(self):
        old = [{"strategy_ref": "a", "weight": 0.2}, {"strategy_ref": "b", "weight": 0.1}]
        plan = sleeve_plan(["STR-Z"], old)
        assert plan["a"] > plan["b"]  # 等比缩水保序
        assert abs(plan["a"] - round(0.2 * (0.95 / 0.3), 6)) < 1e-9  # 与实现同口径 6 位舍入


# ---------- ⑥ 钩子②③：月度审计+报告落盘 ----------
class TestMountAudit:
    def test_audit_detects_cell_drift(self, tmp_path, monkeypatch):
        """格子 mounted 里的 STR-* 不在节点挂载区 = 漂移必报（审计核心职责）。"""
        import backtest.auto_mount as am
        map_drift = """nodes:
- node_id: TDM-E-L1
  name_zh: 大盘总闸
  strategy_mounts:
  - {strategy_ref: STR-VREV-025, confidence: verified, evidence: 'run=x'}
state_matrix:
  cells:
  - {node_id: TDM-E-L1, state: capitulation, mounted: [STR-GHOST-999], confidence: proposed}
portfolio_plan:
  plan_id: PP-001
  sleeves:
  - {strategy_ref: default-equity, weight: 1.0, activation_state: null}
"""
        fake_map = tmp_path / "map.yaml"
        fake_map.write_text(map_drift, encoding="utf-8")
        monkeypatch.setattr(am, "MAP_YAML", fake_map)
        monkeypatch.setattr(am, "validate_map", lambda: [])
        out = am.mount_audit(scan_frequency=None)
        assert out["audit"] == "fails"
        assert out["drift"] and "STR-GHOST-999" in out["drift"][0]

    def test_audit_shape_clean(self, tmp_path, monkeypatch):
        """无漂移+无 fails 时 audit=ok；decay 档失败降级为 error 字段不阻断。"""
        import backtest.auto_mount as am
        map_clean = """nodes:
- node_id: TDM-E-L1
  name_zh: 大盘总闸
  strategy_mounts:
  - {strategy_ref: STR-VREV-025, confidence: verified, evidence: 'run=x'}
state_matrix:
  cells:
  - {node_id: TDM-E-L1, state: capitulation, mounted: [STR-VREV-025], confidence: proposed}
portfolio_plan:
  plan_id: PP-001
  sleeves:
  - {strategy_ref: default-equity, weight: 1.0, activation_state: null}
"""
        fake_map = tmp_path / "map.yaml"
        fake_map.write_text(map_clean, encoding="utf-8")
        monkeypatch.setattr(am, "MAP_YAML", fake_map)
        monkeypatch.setattr(am, "validate_map", lambda: [])
        out = mount_audit(scan_frequency=None)
        assert out["audit"] == "ok" and out["drift"] == [] and out["mounted_count"] == 1


class TestWriteReport:
    def test_report_written_with_three_sections(self, tmp_path):
        payload = {
            "diff": "+++ map.after\n+mount line",
            "judgements": [{"sid": "STR-X-001", "cls": "value_reversal", "node": "TDM-E-L1",
                             "activated": ["capitulation"],
                             "segments": {"capitulation": (73, 3.72)}}],
            "fails": [],
            "weights": "{\"STR-X-001\": 0.05}",
        }
        rp = write_report(payload, "STR-X-001", out_dir=tmp_path)
        text = rp.read_text(encoding="utf-8")
        assert "## 挂了哪" in text and "## 为什么" in text and "## 证据指针" in text
        assert "STR-X-001" in text and "+3.72(73d)" in text and "TDM-E-L1" in text

    def test_report_replay_zero_diff_shape(self, tmp_path):
        payload = {"diff": None, "judgements": [], "fails": [], "weights": "{}"}
        rp = write_report(payload, "", out_dir=tmp_path)
        assert "零 diff" in rp.read_text(encoding="utf-8")


# ---------- ⑤ 常量契约 ----------
class TestConstants:
    def test_window_frozen(self):
        assert IS_WIN == ("2020-01-01", "2023-12-31")

    def test_min_seg_days(self):
        assert MIN_SEG_DAYS == 30

    def test_starter_weight(self):
        assert NEW_SLEEVE_WEIGHT == 0.05
