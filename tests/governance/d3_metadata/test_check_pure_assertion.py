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


# ---------------------------------------------------------------------------
# 豁免测试（Task 5：表格行/受控词表/文件树/词汇 bullet/生命周期枚举）
# ---------------------------------------------------------------------------

def test_check_file_exempt_table_row_deprecated():
    """表格行中的'已废弃'状态值豁免（当前态描述，非历史过渡）。"""
    content = "| 模块A | §1 | 已废弃 | 备注 |\n"
    assert _mod._check_file(content, None) == []


def test_check_file_exempt_table_row_superseded():
    """表格行中的'已被取代'状态值豁免（当前态描述）。"""
    content = "| 旧蓝图 | §1-§10 | 已被取代的旧蓝图 |\n"
    assert _mod._check_file(content, None) == []


def test_check_file_exempt_controlled_vocab():
    """受控词表定义行中的'已废弃'豁免。"""
    content = "> **存在性状态受控词表**：`未实现` / `已实现` / `已阻塞` / `已废弃`\n"
    assert _mod._check_file(content, None) == []


def test_check_file_exempt_controlled_vocab_variant():
    """受控词表变体行中的'已废弃'豁免（存在性：未实现/已实现...）。"""
    content = "> 存在性：未实现/已实现/已阻塞（MUST注明原因）/已废弃（MUST在§5.3说明）\n"
    assert _mod._check_file(content, None) == []


def test_check_file_exempt_file_tree_line():
    """文件树行中的'已废弃'当前态标签豁免。"""
    content = "│   │   ├── validate_session_budget.py  — Session 操作预算校验（已废弃）\n"
    assert _mod._check_file(content, None) == []


def test_check_file_non_table_deprecated_still_caught():
    """非表格行的'已废弃'仍被检测。"""
    content = "这是已废弃的旧规则。\n"
    v = _mod._check_file(content, None)
    assert len(v) == 1 and "已废弃" in v[0]


def test_check_file_table_row_migration_still_caught():
    """表格行中的'从X迁移到Y'仍被检测（非状态值，是历史过渡）。"""
    content = "| 从旧路径迁移到新路径 | 备注 |\n"
    v = _mod._check_file(content, None)
    assert len(v) == 1 and "迁移" in v[0]


def test_check_file_exempt_vocab_bullet_backtick_deprecated():
    """受控词表 bullet 定义行 '- `deprecated`：已废弃/已退役' 豁免。"""
    content = "- `deprecated`：已废弃/已退役\n"
    assert _mod._check_file(content, None) == []


def test_check_file_exempt_vocab_bullet_backtick_deprecated_zh():
    """受控词表 bullet 定义行 '> - `已废弃`：...' 豁免。"""
    content = "> - `已废弃`：设计变更后不再需要 → MUST 在 §5.3 迁移方案中说明\n"
    assert _mod._check_file(content, None) == []


def test_check_file_exempt_lifecycle_arrow_enumeration():
    """生命周期值枚举行 '...→已废弃' 豁免。"""
    content = "1. 4 值覆盖域完整生命周期（生产运行→原型验证→纯设计态→已废弃）\n"
    assert _mod._check_file(content, None) == []
