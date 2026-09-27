# [A_test] module_id: MOD-GOV_domain_fk_gate_wave73 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.redblue_wave73.test_v1_v3_forged_node_and_domain
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""波7.3 红蓝对抗 V1 伪造节点 + V3 越域挂载（st-c7-rb-20260927）

攻击面：
- V1a 伪造节点进 module_id_registry.yaml（条目+total 不派生）→ MODULE-ID-CONSISTENCY
- V1b 新 .py 撞既有 module_id（跨 blueprint）→ MODULE-ID-CONSISTENCY 跨文件唯一性
- V1c 名册装载证明：in_process 名册真载出 GATE-DOMAIN-FK/MODULE-ID-CONSISTENCY/
  DOC-HEADER-SUITE 三台（治"在册不触发"记录病族——先证 LOADED 再证 TRIGGERED）
- V3a [DOMAIN] 指向不存在域 → GATE-DOMAIN-FK 阻断（红样本）
- V3b [DOMAIN] 指向存在但错误的域（越域挂载本体）→ 当前无门拦（在案发现，测试
  固化现状为红队证据，不改判据）
"""

from __future__ import annotations

import importlib
from pathlib import Path
from unittest.mock import MagicMock

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import CommitGateRegistry
from zephyr.gov_enforcement.rule_bridge.gate_auto_registrar import load_gate_entries

_PROJECT_ROOT = Path(__file__).resolve().parents[3]

_REGISTRY_REL = "architecture_model/module_id_registry.yaml"


def _mock_run_git(mapping: dict[tuple[str, ...], tuple[int, str]]):
    """run_git 路由：按 git 子命令元组前缀查映射。"""

    def _run(cmd: list[str]):
        key = tuple(cmd[:4])
        for k, (rc, out) in mapping.items():
            if tuple(cmd[: len(k)]) == k or cmd == list(k):
                res = MagicMock()
                res.returncode, res.stdout = rc, out
                return res
        res = MagicMock()
        res.returncode, res.stdout = mapping.get(key, (1, ""))
        return res

    return _run


class TestV1ForgedNode:
    """V1 伪造节点——MODULE-ID-CONSISTENCY 真触发真阻断。"""

    def test_forged_registry_node_without_count_derivation_blocks(self, tmp_path):
        gw = MagicMock()
        gw.project_root = tmp_path
        mod = importlib.import_module("zephyr.gov_enforcement.commit_gates.module_id_consistency_gate")
        gate = mod.make_module_id_consistency_gate()
        target = tmp_path / _REGISTRY_REL
        target.parent.mkdir(parents=True, exist_ok=True)
        # 伪造节点：注入 MOD-FAKE-NODE 但 total_registered 未派生（1 != 2）
        target.write_text(
            "# [A_config] module_id=CFG-REG-001\n"
            "# module_id: MOD-REG-001\n"
            "module_id: REG-REG-001\n"
            "total_registered: 1\n"
            "modules:\n"
            "  - module_id: MOD-REAL-001\n"
            "  - module_id: MOD-FAKE-NODE\n",
            encoding="utf-8",
        )
        passed, detail = gate.check(gw, [str(target)])
        assert passed is False, "伪造节点未触发 count 派生——尺失效"
        assert "count_mismatch" in detail

    def test_cross_file_module_id_collision_blocks(self, tmp_path):
        gw = MagicMock()
        gw.project_root = tmp_path
        mod = importlib.import_module("zephyr.gov_enforcement.commit_gates.module_id_consistency_gate")
        gate = mod.make_module_id_consistency_gate()
        new_py = tmp_path / "src" / "fake_new.py"
        new_py.parent.mkdir(parents=True, exist_ok=True)
        new_py.write_text(
            "# [BLUEPRINT] MOD-OTHER-BP | docs/x.md\n"
            "# [A_module] module_id=MOD-STOLEN-IDENTITY | layer=module\n",
            encoding="utf-8",
        )
        incumbent = tmp_path / "src" / "incumbent.py"
        incumbent.write_text(
            "# [BLUEPRINT] MOD-INCUMBENT-BP | docs/y.md\n"
            "# [A_module] module_id=MOD-STOLEN-IDENTITY | layer=module\n",
            encoding="utf-8",
        )
        gw.run_git = _mock_run_git(
            {
                ("git", "ls-tree", "HEAD", "src/fake_new.py"): (0, ""),  # 新文件：HEAD 无
                ("git", "grep", "-l", "-F"): (0, "src/incumbent.py\n"),
            }
        )
        passed, detail = gate.check(gw, [str(new_py)])
        assert passed is False, "撞既有 module_id（跨 blueprint）未阻断——身份伪造可入册"
        assert "module_id_collision" in detail

    def test_roster_loads_the_three_candidate_defenders(self):
        """名册装载证明：三台候选防御者真从 in_process 名册载出并可注册。"""
        entries = load_gate_entries(_PROJECT_ROOT)
        by_id = {e["gate_id"]: e for e in entries if isinstance(e, dict)}
        registry = CommitGateRegistry()
        for gate_id in ("MODULE-ID-CONSISTENCY", "GATE-DOMAIN-FK", "DOC-HEADER-SUITE"):
            assert gate_id in by_id, f"{gate_id} 不在 in_process 名册"
            entry = by_id[gate_id]
            module = importlib.import_module(entry["module_path"])
            spec = getattr(module, entry["factory_function"])()
            assert spec.gate_id == gate_id
            assert callable(spec.check)
            registry.register(spec)
        ids = set(registry.list_gate_ids())
        assert {"MODULE-ID-CONSISTENCY", "GATE-DOMAIN-FK", "DOC-HEADER-SUITE"} <= ids


class TestV3DomainMount:
    """V3 越域挂载——GATE-DOMAIN-FK 只防假域，不防真域错挂。"""

    _SAMPLE_YAML = "- domain: D_GOV_ENFORCEMENT\n- domain: D_GOV_CODE_QUALITY\n"
    _PY_REL = "src/zephyr/fake_domain_holder.py"

    def _gateway(self, domain_line: str):
        gw = MagicMock()
        gw.project_root = _PROJECT_ROOT

        def _run(cmd: list[str]):
            res = MagicMock()
            res.returncode = 0
            if cmd[:3] == ["git", "diff", "--cached"] and "--name-only" in cmd:
                res.stdout = self._PY_REL + "\n"
            elif "--unified=0" in cmd:
                res.stdout = f"@@ -0,0 +1,1 @@\n+{domain_line}\n"
            elif cmd[:2] == ["git", "show"] and cmd[2].startswith(":"):
                if "functional_domain_registry" in cmd[2]:
                    res.stdout = self._SAMPLE_YAML
                else:
                    res.stdout = domain_line + "\n"
            else:
                res.returncode = 1
                res.stdout = ""
            return res

        gw.run_git = _run
        return gw

    def test_nonexistent_domain_blocks(self):
        from zephyr.gov_enforcement.commit_gates.domain_fk_gate import make_domain_fk_gate

        gate = make_domain_fk_gate()
        passed, _ = gate.check(self._gateway("# [DOMAIN] D_NOT_A_REAL_DOMAIN"), [self._PY_REL])
        assert passed is False, "假域头未阻断——FK 失效"

    def test_wrong_but_real_domain_currently_passes__documented_finding(self):
        """在案发现（红样本）：真域错挂（gov 域头挂 trading 文件）当前无任何提交面门拦。

        本测试固化现状而非认可它：若未来落地 路径↔声明域 一致性门，此测试必须红，
        届时以修复测试替换本条（判据升级不算 weaken）。
        """
        from zephyr.gov_enforcement.commit_gates.domain_fk_gate import make_domain_fk_gate

        gate = make_domain_fk_gate()
        passed, _ = gate.check(self._gateway("# [DOMAIN] D_GOV_ENFORCEMENT"), [self._PY_REL])
        assert passed is True, "GATE-DOMAIN-FK 语义=存在性 FK，非归属一致性——此断言若变红说明新增了归属门"
