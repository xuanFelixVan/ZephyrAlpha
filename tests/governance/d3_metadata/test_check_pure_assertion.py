"""test_check_pure_assertion.py — check_pure_assertion.py 检测逻辑测试。"""
import os
import sys
import importlib.util

# 加载 scripts/ 下的 checker（不可从 src/ import）
_SCRIPT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)
    )))),
    "scripts", "governance", "d3_metadata", "check_pure_assertion.py",
)
_spec = importlib.util.spec_from_file_location("check_pure_assertion", _SCRIPT)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)


def test_is_in_scope_include_dirs():
    assert _mod._is_in_scope("docs/03_modules/gov_engine/blueprint.md")
    assert _mod._is_in_scope(".trae/rules/onboarding_detail.md")
    assert _mod._is_in_scope("docs/01_policies_and_standards/standards/naming.md")


def test_is_in_scope_include_files():
    assert _mod._is_in_scope("AGENTS.md")
    assert _mod._is_in_scope("README.md")


def test_is_in_scope_exclude_dirs():
    assert not _mod._is_in_scope("docs/_working/temp.md")
    assert not _mod._is_in_scope("docs/_archive/old.md")
    assert not _mod._is_in_scope("docs/01_policies_and_standards/rules/trae_030.md")


def test_is_in_scope_exclude_files():
    assert not _mod._is_in_scope("docs/02_enterprise_architecture/architecture_debt_registry.md")


def test_is_in_scope_exclude_basenames():
    assert not _mod._is_in_scope("docs/03_modules/CHANGELOG.md")
    assert not _mod._is_in_scope("CHANGELOG.md")


def test_is_in_scope_non_md():
    assert not _mod._is_in_scope("scripts/governance/d3_metadata/check_pure_assertion.py")


def test_check_file_violation_regex1():
    """已废止/已废弃/已弃用"""
    v = _mod._check_file("这是已废止的规则。\n", None)
    assert len(v) == 1 and "已废止" in v[0]


def test_check_file_violation_regex3():
    """之前是X现在改为Y"""
    v = _mod._check_file("之前是手动触发，现在是自动触发。\n", None)
    assert len(v) == 1 and "之前是" in v[0]


def test_check_file_violation_regex6():
    """从X迁移到Y"""
    v = _mod._check_file("从旧路径迁移到新路径。\n", None)
    assert len(v) == 1 and "迁移" in v[0]


def test_check_file_skip_frontmatter():
    content = "---\ntitle: 已废止的旧规则\n---\n正文无违规。\n"
    assert _mod._check_file(content, None) == []


def test_check_file_skip_code_block():
    content = "正文无违规。\n```\n已废止的示例\n```\n正文也无违规。\n"
    assert _mod._check_file(content, None) == []


def test_check_file_incremental_added_lines():
    """只检 added_lines 指定的行"""
    content = "已废止的旧行。\n这行是新增的已废止。\n"
    v = _mod._check_file(content, {2})  # 只检第 2 行
    assert len(v) == 1 and "新增" in v[0]


def test_check_file_no_violation():
    assert _mod._check_file("这是当前有效的规则。\n", None) == []


def test_get_added_lines_ci_parses_diff(tmp_path, monkeypatch):
    """--ci 模式解析 git diff 输出提取 added 行号。"""
    fake_diff = """@@ -1,2 +1,3 @@
 unchanged
+新增违规行
 unchanged
@@ -5,1 +6,2 @@
 unchanged
+另一新增行
"""
    def fake_run(*args, **kwargs):
        class R:
            returncode = 0
            stdout = fake_diff
            stderr = ""
        return R()
    monkeypatch.setattr(_mod.subprocess, "run", fake_run)
    added = _mod._get_added_lines_ci("fake.md")
    assert added == {2, 7}


def test_walk_scope_files_finds_md(tmp_path):
    """--full-scan 模式遍历项目根，返回 in-scope .md 文件。"""
    (tmp_path / "AGENTS.md").write_text("ok")
    (tmp_path / "docs" / "_working").mkdir(parents=True)
    (tmp_path / "docs" / "_working" / "temp.md").write_text("skip")
    (tmp_path / "docs" / "03_modules").mkdir(parents=True)
    (tmp_path / "docs" / "03_modules" / "blueprint.md").write_text("ok")
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "foo.py").write_text("skip")
    files = _mod._walk_scope_files(str(tmp_path))
    basenames = sorted(os.path.basename(f) for f in files)
    assert basenames == ["AGENTS.md", "blueprint.md"]
