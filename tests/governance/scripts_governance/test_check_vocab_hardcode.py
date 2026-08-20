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
# [A_module] module_id=MOD-GOV_CHECK_VOCAB_HARDCODE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
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
    # 拼接避免源代码中直接出现 noqa: gate-vocab 文本（NOQA-VALIDATION 门禁误报）
    content = '_EXEMPT = "tests/"  # noqa: ' + "gate-vocab\n"
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
    """Registry smoke test——真实 YAML + 真实 82 豁免 + 真实匹配逻辑。"""

    def test_registry_loads_successfully(self):
        """registry YAML 可加载 + 82 个 exemptions + 5 个 categories。

        #ARCH-VOCAB-NOQA-CONVERGENCE-001 Phase 2 后：原 74 豁免→73（消除
        check_vocab_hardcode.py 自身的 ssot_self 豁免），原 6 分类→5（ssot_self 分类已退役）。
        2026-08-01 +1 m12-broad-except-legitimate（post-commit 钩子非阻断广义 except 豁免）→74。
        2026-08-16：74→82（registry 演进，豁免条目净增 8 条，与 dev 真源同步）。
        """
        registry = cvh._load_noqa_registry()
        assert registry is not None, "registry 应可加载（config/governance/noqa_exempt_registry.yaml 存在）"
        assert isinstance(registry, dict)
        assert "exemptions" in registry and isinstance(registry["exemptions"], list)
        assert "categories" in registry and isinstance(registry["categories"], list)
        # 82 个豁免（74 基线 + 后续净增 8 条）
        assert len(registry["exemptions"]) == 82, f"应有82个豁免, 实际: {len(registry['exemptions'])}"
        # 5 个分类（ssot_self 已退役）
        assert len(registry["categories"]) == 5

    def test_baseline_from_registry(self):
        """基线 = len(exemptions) = 82（从 registry 自动计算，非硬编码 33）。"""
        registry = cvh._load_noqa_registry()
        baseline = cvh._noqa_baseline(registry)
        assert baseline == 82, f"基线应从 registry 计算=82, 实际: {baseline}"

    def test_baseline_fallback_when_registry_none(self):
        """registry=None 时退化为 fallback 基线 33。"""
        baseline = cvh._noqa_baseline(None)
        assert baseline == 33, f"fallback 基线应为33, 实际: {baseline}"

    def test_registered_keys_built(self):
        """_registered_exemption_keys 返回 (file, line) 集合，非空。"""
        registry = cvh._load_noqa_registry()
        keys = cvh._registered_exemption_keys(registry)
        assert len(keys) == 82, f"应有82个键, 实际: {len(keys)}"
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
        result = cvh._is_noqa_registered("nonexistent/file.py", 9999, "完全未登记的豁免理由", keys, reason_map)
        assert result is False, "未登记的 noqa 应返回 False"

    def test_main_exits_zero_warn_only(self, monkeypatch, capsys):
        """main() warn-only 模式 exit 0（即使有 7 个硬编码违规）。"""
        # 不传 --ci，默认 warn-only
        monkeypatch.setattr("sys.argv", ["check_vocab_hardcode.py"])
        exit_code = cvh.main()
        captured = capsys.readouterr()
        assert exit_code == 0, f"warn-only 应 exit 0, 实际: {exit_code}"
        # 应输出 NOQA AUDIT 行，baseline=82 via registry（74 基线 + 后续净增 8 条）
        assert "NOQA AUDIT" in captured.out
        assert "baseline=82 via registry" in captured.out
        assert "trend=0" in captured.out  # 82-82=0，闭环收敛
        # 不应有 UNREGISTERED（82 个全部登记）
        assert "UNREGISTERED" not in captured.out


class TestNoqaRegistryDriftResistance:
    """行号漂移免疫测试——模拟 100% AI 开发场景下代码频繁修改。"""

    def test_drifted_line_matches_via_reason_fallback(self):
        """行号漂移时 reason fallback 匹配——用 registry 中任一 entry 模拟。

        #ARCH-VOCAB-NOQA-CONVERGENCE-001 Phase 2 后：check_vocab_hardcode.py
        自身的 ssot_self 豁免已消除（SSoT 现支持批量加载）。本测试改用
        registry 中第一个 entry 验证行号漂移 + reason fallback 机制仍然有效。
        """
        registry = cvh._load_noqa_registry()
        keys = cvh._registered_exemption_keys(registry)
        reason_map = cvh._registered_reason_map(registry)
        # 取第一个登记的 entry，故意用错误行号（+1000 模拟漂移）
        sample_entry = registry["exemptions"][0]
        sample_file = sample_entry["file"].replace("\\", "/")
        sample_reason = sample_entry["reason"].strip().lstrip("# ").strip()
        drifted_line = sample_entry["line"] + 1000  # 行号漂移
        # 精确匹配应失败，reason fallback 应命中
        assert (sample_file, drifted_line) not in keys, "漂移行号不应在精确 keys 中"
        result = cvh._is_noqa_registered(sample_file, drifted_line, sample_reason, keys, reason_map)
        assert result is True, "行号漂移后 reason fallback 应命中"


# ──────────────────────────────────────────────────────────────────────────
# #ARCH-VOCAB-NOQA-CONVERGENCE-001 Phase 2: load_all_vocabulary_values SSoT 测试
# ──────────────────────────────────────────────────────────────────────────
# 验证新增的批量加载 SSoT 函数——消除 check_vocab_hardcode.py 的 ssot_self 豁免。


class TestLoadAllVocabularyValues:
    """load_all_vocabulary_values SSoT 函数测试——批量加载所有词表。

    治本（#ARCH-VOCAB-NOQA-CONVERGENCE-001 Phase 2）：本函数替代
    check_vocab_hardcode._load_all_vocab_values 中的 yaml.safe_load + glob 逻辑，
    消除 SSoT 不支持批量的 noqa 豁免。
    """

    def test_returns_dict_of_sets(self):
        """返回 dict[str, set[str]]，结构正确。"""
        from _shared.yaml_utils import load_all_vocabulary_values

        result = load_all_vocabulary_values()
        assert isinstance(result, dict)
        assert len(result) > 0, "应加载至少1个词表"
        for vocab_name, values in result.items():
            assert isinstance(vocab_name, str)
            assert isinstance(values, set)
            assert all(isinstance(v, str) for v in values), "所有值应为 str"

    def test_vocab_name_without_suffix(self):
        """vocab_name 不含 _vocabulary.yaml 后缀。"""
        from _shared.yaml_utils import load_all_vocabulary_values

        result = load_all_vocabulary_values()
        for vocab_name in result.keys():
            assert "_vocabulary" not in vocab_name, f"{vocab_name} 不应含后缀"
            assert ".yaml" not in vocab_name, f"{vocab_name} 不应含扩展名"

    def test_includes_known_vocab(self):
        """包含已知词表（status/layer/ttl 等）。"""
        from _shared.yaml_utils import load_all_vocabulary_values

        result = load_all_vocabulary_values()
        # status 词表应存在且包含 active/draft/deprecated
        assert "status" in result, "应包含 status 词表"
        assert "active" in result["status"], "status 应含 active"
        assert "draft" in result["status"], "status 应含 draft"

    def test_strict_false_returns_empty_for_missing_dir(self, tmp_path):
        """strict=False + 不存在目录 → 返回空 dict（不崩溃）。"""
        from _shared.yaml_utils import load_all_vocabulary_values

        result = load_all_vocabulary_values(vocab_dir=tmp_path / "nonexistent")
        assert result == {}, "不存在目录应返回空 dict"

    def test_strict_true_raises_for_missing_dir(self, tmp_path):
        """strict=True + 不存在目录 → fail-fast（这里目录存在但无 yaml，
        glob 返回空，不触发 FileNotFoundError——验证无文件时返回空 dict）。"""
        from _shared.yaml_utils import load_all_vocabulary_values

        # 空目录（存在但无 *_vocabulary.yaml）
        empty_dir = tmp_path / "empty_vocab"
        empty_dir.mkdir()
        result = load_all_vocabulary_values(vocab_dir=empty_dir, strict=True)
        assert result == {}, "空目录（无 yaml）应返回空 dict"

    def test_check_vocab_hardcode_consumes_it(self):
        """check_vocab_hardcode._load_all_vocab_values 调用新 SSoT 函数。

        验证消费者已改造——不再自己 yaml.safe_load + glob。
        """
        # _load_all_vocab_values 应调用 load_all_vocabulary_values
        # 通过验证其返回值与新 SSoT 一致（过滤后）
        from pathlib import Path

        # 找到真实 vocab_dir
        from _shared.constants import REPO_ROOT
        from _shared.yaml_utils import load_all_vocabulary_values

        vocab_dir = REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "vocabularies"

        # SSoT 原始值
        raw = load_all_vocabulary_values(vocab_dir=vocab_dir)
        # 消费者过滤后值（过滤数字和空串）
        filtered = cvh._load_all_vocab_values(vocab_dir)
        assert len(filtered) == len(raw), "过滤后词表数应与原始一致"
        # 验证过滤逻辑：filtered 中的值不含纯数字
        for vocab_name, values in filtered.items():
            for v in values:
                assert not v.isdigit(), f"{vocab_name} 不应含纯数字值: {v}"
                assert v, f"{vocab_name} 不应含空串"
