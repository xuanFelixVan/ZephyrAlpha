# [BLUEPRINT] MOD-GOV_CHECK_VOCAB_HARDCODE | tests/test_check_vocab_hardcode.py | §gate-vocab-detection7-tests
# [MODULE] tests.test_check_vocab_hardcode
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d3_metadata.check_vocab_hardcode
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 测试隔离——monkeypatch REPO_ROOT 指向 tmp_path，不扫描真实仓库；仅测检测7（commit_gates 硬编码 tests/）
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] self
# [TTL] task_bound
"""test_check_vocab_hardcode.py — GATE-VOCAB 检测7 单元测试（2026-06-30 治本补全）

覆盖检测7（commit_gates 测试目录名硬编码，红攻发现2治本）的核心场景：
1. commit_gates 中硬编码 "tests/" 字面量 → 检出
2. docstring 内 "tests/" → 不检出（docstring 豁免）
3. # noqa: gate-vocab 行 → 不检出（内联豁免）
4. 非 commit_gates 目录的 "tests/" → 不检出（范围限制）
5. "tests" 无斜杠 → 不检出（子串匹配 "tests/"）
6. f-string 含 "tests/" → 检出（JoinedStr 内 Constant 节点）
7. 列表多元素含 "tests/" → 检出（每个 Constant 独立命中）

测试隔离：monkeypatch cvh.REPO_ROOT → tmp_path，_check_file 在 tmp_path 下判定
commit_gates 范围，不扫描真实仓库 3575 文件。
"""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_D3_META = _PROJECT_ROOT / "scripts" / "governance" / "d3_metadata"
if str(_D3_META) not in sys.path:
    sys.path.insert(0, str(_D3_META))

import check_vocab_hardcode as cvh  # noqa: E402

_COMMIT_GATES_REL = "src/zephyr/gov_enforcement/commit_gates"


def _make_commit_gate_file(tmp_path: Path, name: str, content: str) -> Path:
    """在 tmp_path 下创建模拟 commit_gates 文件，返回绝对路径。"""
    fp = tmp_path / _COMMIT_GATES_REL / name
    fp.parent.mkdir(parents=True, exist_ok=True)
    fp.write_text(content, encoding="utf-8")
    return fp


def _detection7_issues(issues: list[tuple[int, str]]) -> list[tuple[int, str]]:
    """从 _check_file 结果中筛选检测7的 issue（含 '硬编码测试目录名'）。"""
    return [i for i in issues if "硬编码测试目录名" in i[1]]


def test_detection7_hardcoded_tests_slash(tmp_path, monkeypatch):
    """检测7: commit_gates 中硬编码 'tests/' 字面量 → 检出。"""
    monkeypatch.setattr(cvh, "REPO_ROOT", tmp_path)
    fp = _make_commit_gate_file(tmp_path, "fake_gate.py", '_EXEMPT = "tests/"\n')
    issues = cvh.check_file(fp, tmp_path / "vocabs")
    d7 = _detection7_issues(issues)
    assert len(d7) == 1, f"应检出1处硬编码tests/, 实际: {d7}"
    assert d7[0][0] == 1, f"应在第1行检出, 实际行号: {d7[0][0]}"


def test_detection7_docstring_exempt(tmp_path, monkeypatch):
    """检测7: docstring 内 'tests/' → 不检出（docstring 豁免）。"""
    monkeypatch.setattr(cvh, "REPO_ROOT", tmp_path)
    content = '"""模块说明\n\ntests/ 豁免设计说明。\n"""\n'
    fp = _make_commit_gate_file(tmp_path, "fake_gate.py", content)
    issues = cvh.check_file(fp, tmp_path / "vocabs")
    d7 = _detection7_issues(issues)
    assert len(d7) == 0, f"docstring 应豁免, 实际检出: {d7}"


def test_detection7_noqa_exempt(tmp_path, monkeypatch):
    """检测7: # noqa: gate-vocab 行 → 不检出（内联豁免）。"""
    monkeypatch.setattr(cvh, "REPO_ROOT", tmp_path)
    content = '_EXEMPT = "tests/"  # noqa: gate-vocab\n'
    fp = _make_commit_gate_file(tmp_path, "fake_gate.py", content)
    issues = cvh.check_file(fp, tmp_path / "vocabs")
    d7 = _detection7_issues(issues)
    assert len(d7) == 0, f"noqa 应豁免, 实际检出: {d7}"


def test_detection7_non_commit_gates_scope(tmp_path, monkeypatch):
    """检测7: 非 commit_gates 目录的 'tests/' → 不检出（范围限制）。"""
    monkeypatch.setattr(cvh, "REPO_ROOT", tmp_path)
    fp = tmp_path / "src" / "zephyr" / "other_module.py"
    fp.parent.mkdir(parents=True, exist_ok=True)
    fp.write_text('_EXEMPT = "tests/"\n', encoding="utf-8")
    issues = cvh.check_file(fp, tmp_path / "vocabs")
    d7 = _detection7_issues(issues)
    assert len(d7) == 0, f"非commit_gates不应检出, 实际: {d7}"


def test_detection7_tests_without_slash(tmp_path, monkeypatch):
    """检测7: 'tests' 无斜杠 → 不检出（子串匹配 'tests/'）。"""
    monkeypatch.setattr(cvh, "REPO_ROOT", tmp_path)
    fp = _make_commit_gate_file(tmp_path, "fake_gate.py", '_X = "tests"\n')
    issues = cvh.check_file(fp, tmp_path / "vocabs")
    d7 = _detection7_issues(issues)
    assert len(d7) == 0, f"'tests'无斜杠不应检出, 实际: {d7}"


def test_detection7_fstring(tmp_path, monkeypatch):
    """检测7: f-string 含 'tests/' → 检出（JoinedStr 内 Constant 节点）。"""
    monkeypatch.setattr(cvh, "REPO_ROOT", tmp_path)
    fp = _make_commit_gate_file(tmp_path, "fake_gate.py", '_X = f"tests/{name}"\n')
    issues = cvh.check_file(fp, tmp_path / "vocabs")
    d7 = _detection7_issues(issues)
    assert len(d7) == 1, f"f-string应检出, 实际: {d7}"


def test_detection7_list_multiple(tmp_path, monkeypatch):
    """检测7: 列表多元素含 'tests/' → 检出（每个 Constant 独立命中）。"""
    monkeypatch.setattr(cvh, "REPO_ROOT", tmp_path)
    fp = _make_commit_gate_file(tmp_path, "fake_gate.py", '_X = ["tests/a", "tests/b"]\n')
    issues = cvh.check_file(fp, tmp_path / "vocabs")
    d7 = _detection7_issues(issues)
    assert len(d7) == 2, f"列表2元素应各检出1处(共2), 实际: {len(d7)}"


# ──────────────────────────────────────────────────────────────────────────
# #ARCH-VOCAB-NOQA-CONVERGENCE-001 Phase 1: noqa_exempt_registry smoke test
# ──────────────────────────────────────────────────────────────────────────
# 验证 registry 加载、基线自动计算、混合匹配（line 精确 + reason fallback）、
# 闭环校验（未登记 noqa = 违规）。真实调用 _load_noqa_registry（真实 YAML 真源），
# 非mock——满足 memory 规则"核心治理工具必须有 smoke test（真实调用 + 真实文件）"。


class TestNoqaRegistrySmoke:
    """Registry smoke test——真实 YAML + 真实 74 豁免 + 真实匹配逻辑。"""

    def test_registry_loads_successfully(self):
        """registry YAML 可加载 + 74 个 exemptions + 6 个 categories。"""
        registry = cvh._load_noqa_registry()
        assert registry is not None, "registry 应可加载（config/governance/noqa_exempt_registry.yaml 存在）"
        assert isinstance(registry, dict)
        assert "exemptions" in registry and isinstance(registry["exemptions"], list)
        assert "categories" in registry and isinstance(registry["categories"], list)
        # 74 个豁免（当前基线，治本降低后此数会下降）
        assert len(registry["exemptions"]) == 74, f"应有74个豁免, 实际: {len(registry['exemptions'])}"
        # 6 个分类
        assert len(registry["categories"]) == 6

    def test_baseline_from_registry(self):
        """基线 = len(exemptions) = 74（从 registry 自动计算，非硬编码 33）。"""
        registry = cvh._load_noqa_registry()
        baseline = cvh._noqa_baseline(registry)
        assert baseline == 74, f"基线应从 registry 计算=74, 实际: {baseline}"

    def test_baseline_fallback_when_registry_none(self):
        """registry=None 时退化为 fallback 基线 33。"""
        baseline = cvh._noqa_baseline(None)
        assert baseline == 33, f"fallback 基线应为33, 实际: {baseline}"

    def test_registered_keys_built(self):
        """_registered_exemption_keys 返回 (file, line) 集合，非空。"""
        registry = cvh._load_noqa_registry()
        keys = cvh._registered_exemption_keys(registry)
        assert len(keys) == 74, f"应有74个键, 实际: {len(keys)}"
        # 验证键格式：(str, int)
        for file_path, line in keys:
            assert isinstance(file_path, str) and "\\" not in file_path, "file 应为正斜杠规范化"
            assert isinstance(line, int) and line > 0

    def test_registered_reason_map_built(self):
        """_registered_reason_map 返回 {file -> {reason, ...}}，覆盖所有文件。"""
        registry = cvh._load_noqa_registry()
        reason_map = cvh._registered_reason_map(registry)
        assert len(reason_map) > 0
        # 验证每个文件至少有1个 reason
        for file_path, reasons in reason_map.items():
            assert "\\" not in file_path, "file 应为正斜杠规范化"
            assert len(reasons) > 0, f"{file_path} 应至少有1个 reason"

    def test_is_registered_line_match(self):
        """精确 (file, line) 匹配——已登记的 noqa 返回 True。"""
        registry = cvh._load_noqa_registry()
        keys = cvh._registered_exemption_keys(registry)
        reason_map = cvh._registered_reason_map(registry)
        # 取第一个登记的 (file, line) 验证精确匹配
        sample_file, sample_line = next(iter(keys))
        assert cvh._is_noqa_registered(sample_file, sample_line, "any reason", keys, reason_map) is True

    def test_is_registered_reason_fallback_for_line_drift(self):
        """行号漂移时 reason fallback 匹配——行号变化但 reason 一致仍命中。"""
        registry = cvh._load_noqa_registry()
        keys = cvh._registered_exemption_keys(registry)
        reason_map = cvh._registered_reason_map(registry)
        # 取第一个登记的 entry，故意用错误行号（+1000 模拟漂移）
        sample_entry = registry["exemptions"][0]
        sample_file = sample_entry["file"].replace("\\", "/")
        sample_reason = sample_entry["reason"].strip().lstrip("# ").strip()
        drifted_line = sample_entry["line"] + 1000  # 行号漂移
        # 精确匹配应失败，reason fallback 应命中
        assert cvh._is_noqa_registered(sample_file, drifted_line, sample_reason, keys, reason_map) is True

    def test_is_registered_unregistered_returns_false(self):
        """未登记的 (file, line, reason) 返回 False——闭环校验核心。"""
        registry = cvh._load_noqa_registry()
        keys = cvh._registered_exemption_keys(registry)
        reason_map = cvh._registered_reason_map(registry)
        # 完全未登记的 file + line + reason
        result = cvh._is_noqa_registered(
            "nonexistent/file.py", 9999, "完全未登记的豁免理由", keys, reason_map
        )
        assert result is False, "未登记的 noqa 应返回 False"

    def test_main_exits_zero_warn_only(self, monkeypatch, capsys):
        """main() warn-only 模式 exit 0（即使有 7 个硬编码违规）。"""
        # 不传 --ci，默认 warn-only
        monkeypatch.setattr("sys.argv", ["check_vocab_hardcode.py"])
        exit_code = cvh.main()
        captured = capsys.readouterr()
        assert exit_code == 0, f"warn-only 应 exit 0, 实际: {exit_code}"
        # 应输出 NOQA AUDIT 行，baseline=74 via registry
        assert "NOQA AUDIT" in captured.out
        assert "baseline=74 via registry" in captured.out
        assert "trend=0" in captured.out  # 74-74=0，闭环收敛
        # 不应有 UNREGISTERED（74 个全部登记）
        assert "UNREGISTERED" not in captured.out


class TestNoqaRegistryDriftResistance:
    """行号漂移免疫测试——模拟 100% AI 开发场景下代码频繁修改。"""

    def test_check_vocab_hardcode_self_noqa_matches_via_reason(self):
        """check_vocab_hardcode.py 自身的 noqa（L287，原 L277 漂移后）通过 reason 匹配。

        场景：本会话修改 check_vocab_hardcode.py 后行号从 L277→L287。
        registry 中登记的是 L277（生成时行号），但 reason 一致。
        混合匹配应通过 reason fallback 命中，不报 UNREGISTERED。
        """
        registry = cvh._load_noqa_registry()
        keys = cvh._registered_exemption_keys(registry)
        reason_map = cvh._registered_reason_map(registry)
        # 实际 noqa 在 L287（漂移后），reason 为 "R4 豁免：批量加载所有词表..."
        # registry 中登记的是 L277，但 reason 一致
        actual_reason = "# R4 豁免：批量加载所有词表（SSoT 不支持批量，合理不收敛）"
        # 行号 287 不在 keys 中（keys 有 277），但 reason 应 fallback 命中
        file_path = "scripts/governance/d3_metadata/check_vocab_hardcode.py"
        assert (file_path, 287) not in keys, "L287 不应在精确 keys 中（漂移后）"
        # reason fallback 应命中
        result = cvh._is_noqa_registered(file_path, 287, actual_reason, keys, reason_map)
        assert result is True, "行号漂移后 reason fallback 应命中"
