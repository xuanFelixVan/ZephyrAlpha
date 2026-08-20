# [A_test] module_id: MOD-GOV_commit_scope_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.test_commit_scope_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""test_commit_scope_gate.py — 提交边界域一致性门禁单测（COMMIT-SCOPE，13a5e1d512 混合提交治本）

权威依据：commit_scope_gate.py（make_commit_scope_gate）

测试组：
- TestGateSpecFields: gate_id / priority 字段正确
- TestSingleDomainPasses: 单域 commit → passed=True
- TestCrossDomainBlocked: 跨≥2 域 → passed=False（COMMIT_SCOPE_VIOLATION）
- TestEscapeHatch: allow_multi_domain=True 逃生通道放行
- TestAllUnknownPasses: 全 UNKNOWN（无 [DOMAIN] 头 + 无路径映射）→ passed=True
- TestPathInference: ssot_path 最长前缀匹配
- TestFailOpen: 文件读取异常 → fail-open（passed=True）
- TestAccidentReplay: 复现 13a5e1d512 事故 5 文件跨域场景
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from zephyr.gov_enforcement.commit_gates.commit_scope_gate import (
    _infer_domain_by_path,
    make_commit_scope_gate,
)


def _make_gateway(project_root: Path) -> MagicMock:
    """构造 mock gateway。

    run_git 返回 returncode=1（模拟非 git 仓库 / 无 staged 版本），
    使 _read_staged_file 返回 None → _load_path_domain_map fallback 读工作区
    YAML（tmp_path 下不存在）→ 返回 None（fail-open，path_map=None）。
    这样测试聚焦 .py [DOMAIN] 头部判定路径。
    """
    gw = MagicMock()
    gw.project_root = project_root
    gw.run_git.return_value.returncode = 1
    gw.run_git.return_value.stdout = ""
    return gw


def _write_py(path: Path, domain: str | None, body: str = "x = 1\n") -> None:
    """写 .py 文件，可选 [DOMAIN] 头部。"""
    header = f"# [DOMAIN] {domain}\n# [MODULE] test\n" if domain else "# [MODULE] test\n"
    path.write_text(header + body, encoding="utf-8")


class TestGateSpecFields:
    """gate_id / priority 字段正确。"""

    def test_gate_id_and_priority(self):
        gate = make_commit_scope_gate()
        assert gate.gate_id == "COMMIT-SCOPE"
        assert gate.priority == 48


class TestSingleDomainPasses:
    """单域 commit → passed=True。"""

    def test_single_domain_two_files(self, tmp_path):
        f1 = tmp_path / "a.py"
        f2 = tmp_path / "b.py"
        _write_py(f1, "D_REGIME")
        _write_py(f2, "D_REGIME")
        gw = _make_gateway(tmp_path)
        gate = make_commit_scope_gate()
        passed, _ = gate.check(gw, [str(f1), str(f2)])
        assert passed is True

    def test_single_file_passes(self, tmp_path):
        f1 = tmp_path / "a.py"
        _write_py(f1, "D_GOVERNANCE")
        gw = _make_gateway(tmp_path)
        gate = make_commit_scope_gate()
        passed, _ = gate.check(gw, [str(f1)])
        assert passed is True


class TestCrossDomainBlocked:
    """跨≥2 域 → passed=False（COMMIT_SCOPE_VIOLATION）。"""

    def test_two_domains_blocked(self, tmp_path):
        f1 = tmp_path / "a.py"
        f2 = tmp_path / "b.py"
        _write_py(f1, "D_REGIME")
        _write_py(f2, "D_GOVERNANCE")
        gw = _make_gateway(tmp_path)
        gate = make_commit_scope_gate()
        passed, detail = gate.check(gw, [str(f1), str(f2)])
        assert passed is False
        assert "COMMIT_SCOPE_VIOLATION" in detail
        assert "D_REGIME" in detail
        assert "D_GOVERNANCE" in detail
        assert "allow_multi_domain" in detail  # 提示逃生通道

    def test_three_domains_blocked(self, tmp_path):
        files = []
        for i, dom in enumerate(["D_REGIME", "D_GOVERNANCE", "D_INFRA_A2A"]):
            f = tmp_path / f"f{i}.py"
            _write_py(f, dom)
            files.append(str(f))
        gw = _make_gateway(tmp_path)
        gate = make_commit_scope_gate()
        passed, detail = gate.check(gw, files)
        assert passed is False
        assert "3 个域" in detail


class TestEscapeHatch:
    """allow_multi_domain=True 逃生通道放行。"""

    def test_escape_hatch_passes(self, tmp_path):
        f1 = tmp_path / "a.py"
        f2 = tmp_path / "b.py"
        _write_py(f1, "D_REGIME")
        _write_py(f2, "D_GOVERNANCE")
        gw = _make_gateway(tmp_path)
        gate = make_commit_scope_gate()
        passed, _ = gate.check(gw, [str(f1), str(f2)], allow_multi_domain=True)
        assert passed is True


class TestAllUnknownPasses:
    """全 UNKNOWN（无 [DOMAIN] 头 + 无路径映射）→ passed=True（避免误报）。"""

    def test_no_domain_header_passes(self, tmp_path):
        f1 = tmp_path / "a.py"
        f2 = tmp_path / "b.py"
        _write_py(f1, None)
        _write_py(f2, None)
        gw = _make_gateway(tmp_path)
        gate = make_commit_scope_gate()
        passed, _ = gate.check(gw, [str(f1), str(f2)])
        assert passed is True

    def test_non_py_files_unknown_passes(self, tmp_path):
        """非 .py 文件无路径映射时全 UNKNOWN → PASS。"""
        f1 = tmp_path / "a.yaml"
        f2 = tmp_path / "b.md"
        f1.write_text("key: value\n")
        f2.write_text("# doc\n")
        gw = _make_gateway(tmp_path)
        gate = make_commit_scope_gate()
        passed, _ = gate.check(gw, [str(f1), str(f2)])
        assert passed is True


class TestPathInference:
    """ssot_path 最长前缀匹配（直接测辅助函数）。"""

    def test_infer_by_ssot_path(self):
        path_map = {
            "src/zephyr/regime/": "D_REGIME",
            "src/zephyr/governance/": "D_GOVERNANCE",
        }
        assert _infer_domain_by_path("src/zephyr/regime/foo.yaml", path_map) == "D_REGIME"
        assert _infer_domain_by_path("src/zephyr/governance/bar.yaml", path_map) == "D_GOVERNANCE"
        assert _infer_domain_by_path("docs/other.md", path_map) == "UNKNOWN"

    def test_longest_prefix_match(self):
        """最长前缀匹配——子路径域优先于父路径域。"""
        path_map = {
            "src/zephyr/": "D_ROOT",
            "src/zephyr/regime/": "D_REGIME",
        }
        assert _infer_domain_by_path("src/zephyr/regime/x.yaml", path_map) == "D_REGIME"
        assert _infer_domain_by_path("src/zephyr/other/x.yaml", path_map) == "D_ROOT"

    def test_backslash_normalization(self):
        """Windows 反斜杠归一化。"""
        path_map = {"src/zephyr/regime/": "D_REGIME"}
        assert _infer_domain_by_path("src\\zephyr\\regime\\x.yaml", path_map) == "D_REGIME"


class TestFailOpen:
    """文件读取异常 → fail-open（passed=True，不阻断）。"""

    def test_nonexistent_file_fail_open(self, tmp_path):
        """文件不存在（如 staged delete）→ UNKNOWN → 单文件 PASS。"""
        gw = _make_gateway(tmp_path)
        gate = make_commit_scope_gate()
        passed, _ = gate.check(gw, [str(tmp_path / "nonexistent.py")])
        assert passed is True


class TestAccidentReplay:
    """复现 13a5e1d512 事故场景：5 文件跨 D_REGIME + D_GOVERNANCE。

    事故中并发 session 把 regime 校准器（D_REGIME）+ DQ 维度扩展（D_GOVERNANCE）
    混合在一个 commit。本测试验证 COMMIT-SCOPE gate 能阻断此场景。
    """

    def test_accident_scenario_blocked(self, tmp_path):
        # 模拟事故 5 文件的域归属
        regime_dir = tmp_path / "src/zephyr/regime/validation/phase2"
        regime_dir.mkdir(parents=True)
        f_b4 = regime_dir / "b4_transition_accuracy.py"
        f_runner = regime_dir / "phase2_runner.py"
        _write_py(f_b4, "D_REGIME")
        _write_py(f_runner, "D_REGIME")

        gov_dir = tmp_path / "src/zephyr/governance/data_governance"
        gov_dir.mkdir(parents=True)
        f_dq = gov_dir / "data_quality.py"
        _write_py(f_dq, "D_GOVERNANCE")

        test_dir = tmp_path / "tests/data"
        test_dir.mkdir(parents=True)
        f_test = test_dir / "test_data_quality.py"
        _write_py(f_test, None)  # 测试文件无 [DOMAIN] 头 → UNKNOWN，不参与跨域判定

        gw = _make_gateway(tmp_path)
        gate = make_commit_scope_gate()
        passed, detail = gate.check(gw, [str(f_b4), str(f_runner), str(f_dq), str(f_test)])
        assert passed is False
        assert "D_REGIME" in detail
        assert "D_GOVERNANCE" in detail

    def test_accident_split_passes(self, tmp_path):
        """事故拆分为单域 commit 后各自通过（治本效果验证）。"""
        regime_dir = tmp_path / "src/zephyr/regime/validation/phase2"
        regime_dir.mkdir(parents=True)
        f_b4 = regime_dir / "b4_transition_accuracy.py"
        f_runner = regime_dir / "phase2_runner.py"
        _write_py(f_b4, "D_REGIME")
        _write_py(f_runner, "D_REGIME")

        gw = _make_gateway(tmp_path)
        gate = make_commit_scope_gate()
        # regime 域单独 commit → PASS
        passed, _ = gate.check(gw, [str(f_b4), str(f_runner)])
        assert passed is True
