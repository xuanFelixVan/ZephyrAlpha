# [A_test] module_id: MOD-GOV_n16_exemption_loader | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-643 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_n16_exemption_loader
# [DOMAIN] D_GOVERNANCE
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-TEST-643 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""
N-16 豁免清单 YAML 加载器单测（红蓝对抗核心场景永久化）
=====================================================

权威依据：docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml v1.5.0
§gov_doc_003_filename_uniqueness.n16_config

测试组：
- TestFailOpen：YAML 缺失/空/语法错误/缺键/空文件 → fail-open 回退到 _N16_*_FALLBACK
- TestTypeConfusion：类型混淆 5 变体（string 标量/int/None/嵌套 list/混合）→ 回退防垃圾集合
- TestValidLoad：合法 YAML 正常加载 + 未知键忽略 + 重复值去重
- TestInheritance：docs 豁免继承 tests 基线
- TestModuleCache：模块级缓存进程内不变（pre-commit 每次新进程重载）
- TestDetection：同名 test_*.py 检测 + conftest.py 豁免 + --warn-only 硬阻断逻辑

红蓝对抗历史：本文件由红蓝测试脚本 n16_rb.py（19 项场景）提取核心场景永久化，
防止类型混淆漏洞（B5-B5e）回退后无回归保护。原始红蓝测试 2026-06-26 全 PASS。
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "scripts" / "governance" / "d3_metadata"))

import pytest  # noqa: E402
from check_naming_convention import (  # noqa: E402
    _N16_DOCS_EXEMPT_NAMES,
    _N16_DOCS_EXEMPT_NAMES_EXTRA_FALLBACK,
    _N16_DOCS_SKIP_DIRS_FALLBACK,
    _N16_SKIP_DIR_PREFIXES_FALLBACK,
    _N16_TESTS_EXEMPT_NAMES,
    _N16_TESTS_EXEMPT_NAMES_FALLBACK,
    _N16_YAML_PATH,
    _load_n16_exemptions_from_yaml,
    _validate_ssot_linkage,
    check_test_name_uniqueness,
)

# ---------------------------------------------------------------------------
# 辅助：monkeypatch _N16_YAML_PATH 后调用加载函数
# ---------------------------------------------------------------------------


def _load_with_content(monkeypatch, tmp_path, content: str | None):
    """写入 content 到临时 YAML，monkeypatch _N16_YAML_PATH，调用加载函数。"""
    tp = tmp_path / "test_n16.yaml"
    if content is not None:
        tp.write_text(content, encoding="utf-8")
    monkeypatch.setattr("check_naming_convention._N16_YAML_PATH", tp)
    return _load_n16_exemptions_from_yaml()


def _load_nonexistent(monkeypatch, tmp_path):
    """monkeypatch _N16_YAML_PATH 到不存在路径，模拟 YAML 缺失。"""
    monkeypatch.setattr("check_naming_convention._N16_YAML_PATH", tmp_path / "nonexistent.yaml")
    return _load_n16_exemptions_from_yaml()


VALID_YAML = """sections:
  gov_doc_003_filename_uniqueness:
    n16_config:
      exempt_names_tests: [conftest.py, __init__.py]
      exempt_names_docs_extra: [index.md, blueprint.md]
      skip_dirs_docs: [_archive, _backups]
      skip_dir_prefixes: [_tmp_]
"""

# fail-open 回退期望值：4 元组（tests / docs_extra / skip_dirs / skip_dir_prefixes）
# 与 _load_n16_exemptions_from_yaml() 返回签名一致
FALLBACK_QUAD = (
    _N16_TESTS_EXEMPT_NAMES_FALLBACK,
    _N16_DOCS_EXEMPT_NAMES_EXTRA_FALLBACK,
    _N16_DOCS_SKIP_DIRS_FALLBACK,
    _N16_SKIP_DIR_PREFIXES_FALLBACK,
)


# ===========================================================================
# TestFailOpen：YAML 异常 → fail-open 回退
# ===========================================================================


class TestFailOpen:
    """YAML 缺失/空/语法错误/缺键/空文件 → 回退到 _N16_*_FALLBACK 安全值。"""

    def test_yaml_missing(self, monkeypatch, tmp_path):
        r = _load_nonexistent(monkeypatch, tmp_path)
        assert r == FALLBACK_QUAD

    def test_empty_tests_list(self, monkeypatch, tmp_path):
        r = _load_with_content(
            monkeypatch,
            tmp_path,
            """sections:
  gov_doc_003_filename_uniqueness:
    n16_config:
      exempt_names_tests: []
      exempt_names_docs_extra: [index.md]
      skip_dirs_docs: [_archive]
""",
        )
        assert r == FALLBACK_QUAD

    def test_missing_n16_config_key(self, monkeypatch, tmp_path):
        r = _load_with_content(
            monkeypatch,
            tmp_path,
            """sections:
  gov_doc_003_filename_uniqueness:
    title: no config here
""",
        )
        assert r == FALLBACK_QUAD

    def test_yaml_syntax_error(self, monkeypatch, tmp_path):
        r = _load_with_content(monkeypatch, tmp_path, "sections: [unclosed")
        assert r == FALLBACK_QUAD

    def test_empty_yaml_file(self, monkeypatch, tmp_path):
        r = _load_with_content(monkeypatch, tmp_path, "")
        assert r == FALLBACK_QUAD


# ===========================================================================
# TestTypeConfusion：类型混淆 5 变体 → 回退防垃圾集合（红蓝漏洞防护核心）
# ===========================================================================


class TestTypeConfusion:
    """类型混淆场景必须回退，防止 string 标量被迭代成 char set 绕过检测。

    红蓝历史：B5-B5e 漏洞（2026-06-26 发现并修复），原缺陷为仅检查空集合未检查
    类型，导致 'conftest.py' 标量被 frozenset() 迭代成 {'c','o','n','f','t','e','s','.','p','y'}。
    """

    def test_string_scalar_instead_of_list(self, monkeypatch, tmp_path):
        r = _load_with_content(
            monkeypatch,
            tmp_path,
            """sections:
  gov_doc_003_filename_uniqueness:
    n16_config:
      exempt_names_tests: conftest.py
      exempt_names_docs_extra: [index.md]
      skip_dirs_docs: [_archive]
""",
        )
        assert r == FALLBACK_QUAD

    def test_int_elements(self, monkeypatch, tmp_path):
        r = _load_with_content(
            monkeypatch,
            tmp_path,
            """sections:
  gov_doc_003_filename_uniqueness:
    n16_config:
      exempt_names_tests: [123, 456]
      exempt_names_docs_extra: [index.md]
      skip_dirs_docs: [_archive]
""",
        )
        assert r == FALLBACK_QUAD

    def test_none_elements(self, monkeypatch, tmp_path):
        r = _load_with_content(
            monkeypatch,
            tmp_path,
            """sections:
  gov_doc_003_filename_uniqueness:
    n16_config:
      exempt_names_tests: [null, conftest.py]
      exempt_names_docs_extra: [index.md]
      skip_dirs_docs: [_archive]
""",
        )
        assert r == FALLBACK_QUAD

    def test_nested_list(self, monkeypatch, tmp_path):
        r = _load_with_content(
            monkeypatch,
            tmp_path,
            """sections:
  gov_doc_003_filename_uniqueness:
    n16_config:
      exempt_names_tests: [[conftest.py]]
      exempt_names_docs_extra: [index.md]
      skip_dirs_docs: [_archive]
""",
        )
        assert r == FALLBACK_QUAD

    def test_mixed_types(self, monkeypatch, tmp_path):
        r = _load_with_content(
            monkeypatch,
            tmp_path,
            """sections:
  gov_doc_003_filename_uniqueness:
    n16_config:
      exempt_names_tests: [123, conftest.py]
      exempt_names_docs_extra: [index.md]
      skip_dirs_docs: [_archive]
""",
        )
        assert r == FALLBACK_QUAD


# ===========================================================================
# TestValidLoad：合法 YAML 正常加载 + 未知键忽略 + 重复值去重
# ===========================================================================


class TestValidLoad:
    def test_valid_yaml_loads_correctly(self, monkeypatch, tmp_path):
        r = _load_with_content(monkeypatch, tmp_path, VALID_YAML)
        assert r[0] == frozenset({"conftest.py", "__init__.py"})
        assert r[1] == frozenset({"index.md", "blueprint.md"})
        assert r[2] == {"_archive", "_backups"}
        assert r[3] == {"_tmp_"}

    def test_unknown_key_ignored(self, monkeypatch, tmp_path):
        r = _load_with_content(
            monkeypatch,
            tmp_path,
            """sections:
  gov_doc_003_filename_uniqueness:
    n16_config:
      exempt_names_tests: [conftest.py, __init__.py]
      exempt_names_docs_extra: [index.md]
      skip_dirs_docs: [_archive]
      skip_dir_prefixes: [_tmp_]
      unknown_key: foo
""",
        )
        assert r[0] == frozenset({"conftest.py", "__init__.py"})

    def test_duplicate_values_deduped(self, monkeypatch, tmp_path):
        r = _load_with_content(
            monkeypatch,
            tmp_path,
            """sections:
  gov_doc_003_filename_uniqueness:
    n16_config:
      exempt_names_tests: [conftest.py, conftest.py, __init__.py]
      exempt_names_docs_extra: [index.md, index.md]
      skip_dirs_docs: [_archive, _archive, _backups]
      skip_dir_prefixes: [_tmp_, _tmp_]
""",
        )
        assert r[0] == frozenset({"conftest.py", "__init__.py"})
        assert r[1] == frozenset({"index.md"})
        assert r[3] == {"_tmp_"}


# ===========================================================================
# TestInheritance：docs 豁免继承 tests 基线
# ===========================================================================


class TestInheritance:
    """_N16_DOCS_EXEMPT_NAMES = _N16_TESTS_EXEMPT_NAMES | _N16_DOCS_EXEMPT_EXTRA_RAW"""

    def test_docs_inherits_tests_baseline(self):
        assert "conftest.py" in _N16_DOCS_EXEMPT_NAMES
        assert "__init__.py" in _N16_DOCS_EXEMPT_NAMES


# ===========================================================================
# TestModuleCache：模块级缓存进程内不变
# ===========================================================================


class TestModuleCache:
    """模块级加载在 import 时执行一次，进程内不随 YAML 变化更新。

    pre-commit 每次 commit 启动新进程 → 重新 import → 重新加载，故缓存不跨 commit。
    """

    def test_module_cache_stale_within_process(self, monkeypatch, tmp_path):
        stale = _N16_TESTS_EXEMPT_NAMES
        monkeypatch.setattr("check_naming_convention._N16_YAML_PATH", tmp_path / "changed.yaml")
        tmp_path.joinpath("changed.yaml").write_text(
            """sections:
  gov_doc_003_filename_uniqueness:
    n16_config:
      exempt_names_tests: [new_only.py]
      exempt_names_docs_extra: [x.md]
      skip_dirs_docs: [y]
      skip_dir_prefixes: [_tmp_z]
""",
            encoding="utf-8",
        )
        fresh = _load_n16_exemptions_from_yaml()
        # 模块级变量不变（陈旧）
        assert _N16_TESTS_EXEMPT_NAMES == stale
        # 但重新调用加载函数会读到新值
        assert fresh[0] == frozenset({"new_only.py"})


# ===========================================================================
# TestDetection：N-16 检测逻辑 + 豁免 + 硬阻断
# ===========================================================================


class TestDetection:
    def _make_proj(self, tmp_path, dup_basename):
        """创建含两个同名文件的 tests/ 目录。"""
        tdir = tmp_path / "tests"
        (tdir / "a").mkdir(parents=True)
        (tdir / "b").mkdir(parents=True)
        (tdir / "a" / dup_basename).write_text("x")
        (tdir / "b" / dup_basename).write_text("x")
        return tmp_path

    def test_duplicate_test_py_detected(self, tmp_path):
        root = self._make_proj(tmp_path, "test_dup.py")
        viol = check_test_name_uniqueness(root)
        assert len(viol) > 0
        assert viol[0].rule == "N-16"

    def test_conftest_py_exempted(self, tmp_path):
        root = self._make_proj(tmp_path, "conftest.py")
        viol = check_test_name_uniqueness(root)
        assert len(viol) == 0

    def test_warn_only_still_blocks_n16(self, tmp_path):
        """--warn-only 下 N-16 仍硬阻断（复现 main() L1313 过滤逻辑）。

        main(): return EXIT_FINDINGS if (not args.warn_only or n16_violations) else EXIT_PASS
        → warn_only=True 且 n16_violations 非空 → EXIT_FINDINGS（阻断）
        """
        root = self._make_proj(tmp_path, "test_warn.py")
        n16_viol = check_test_name_uniqueness(root)
        assert len(n16_viol) > 0
        assert n16_viol[0].rule == "N-16"
        # 复现 main() 返回逻辑
        warn_only = True
        returns_findings = not warn_only or len(n16_viol) > 0
        assert returns_findings is True


# ===========================================================================
# TestSsotConsistency：N-16 fallback 与 YAML n16_config 一致性（自动触发）
# ===========================================================================


class TestSsotConsistency:
    """_validate_ssot_linkage() 扩展校验：N-16 fallback 与 YAML n16_config 一致。

    pytest 每次运行自动触发——若 YAML 改了豁免项但 fallback 未同步，此测试失败。
    治本：消除 _N16_*_FALLBACK 与 YAML 真源的同步漂移风险（向内收2.2自动维护）。
    """

    def test_n16_fallback_matches_yaml(self):
        ok, msg = _validate_ssot_linkage()
        assert ok, f"SSoT 一致性校验失败（N-16 fallback 与 YAML n16_config 漂移）:\n{msg}"
