# [A_test] module_id: MOD-GOV-029 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-029 | docs/03_modules/_domain_governance/panorama_alignment_engine/blueprint.md | §FP-panorama-gen
# [MODULE] tests.governance.test_generate_blueprint_panorama
# [DOMAIN] D_GOVERNANCE
# [CONSUMERS] pytest
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] tests/governance/test_generate_blueprint_panorama.py
# [TTL] task_bound
# [ARCH-REF] #ARCH-053 #ARCH-056
"""test_generate_blueprint_panorama.py — 蓝图 §0.6 生成器单测（ARCH-053 + ARCH-056）

覆盖纯函数（无需 DB 连接）：
  - _S06_BLOCK_RE 正则边界行为（含回归测试：§0.6 后跟 §0.2/§0.3 时不误吞）
  - _parse_simple_frontmatter frontmatter 解析
  - _S01_TABLE_ROW_RE 表格行匹配

回归测试背景：
  修复前 _S06_BLOCK_RE 前瞻为 \\n## [^#]，只匹配2级标题，
  导致 §0.6 后跟 ### §0.2（3级标题）时正则不停止，误吞 §0.2/§0.3。
  修复后前瞻为 \\n#{2,3} [^#]，同时匹配2级和3级标题作为边界。
  commit 733136ea33
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

# depgraph hint: 让 generate_project_depgraph.py AST 扫描器检测 test→module 依赖边
# 实际测试用 importlib 动态加载（scripts/ 非 Python 包），此 import 运行时必失败
try:
    from scripts.governance.d5_architecture.generators.generate_blueprint_panorama import (  # noqa: F401
        _S06_BLOCK_RE,
    )
except ImportError:
    pass

_SCRIPT_PATH = (
    Path(__file__).resolve().parents[2]
    / "scripts"
    / "governance"
    / "d5_architecture"
    / "generators"
    / "generate_blueprint_panorama.py"
)


@pytest.fixture(scope="module")
def gbp():
    """动态加载 generate_blueprint_panorama.py（避免 __init__.py 依赖问题）。

    注意：生成器使用 @dataclass 装饰器，Python 3.11 的 dataclasses 内部会调用
    sys.modules.get(cls.__module__).__dict__，动态加载的模块必须先注册到
    sys.modules，否则 @dataclass 触发 AttributeError: 'NoneType' object has no attribute '__dict__'。
    """
    mod_name = "generate_blueprint_panorama_under_test"
    spec = importlib.util.spec_from_file_location(mod_name, _SCRIPT_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod  # 注册到 sys.modules，@dataclass 装饰器依赖
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# _S06_BLOCK_RE 回归测试（commit 733136ea33 修复的 bug）
# ---------------------------------------------------------------------------


class TestS06BlockRegex:
    """_S06_BLOCK_RE 边界匹配行为。"""

    def test_stops_at_h3_heading_s02(self, gbp):
        """回归测试：§0.6 后跟 ### §0.2（3级标题）时必须停止，不误吞 §0.2。

        修复前 bug：前瞻 \\n## [^#] 只匹配2级标题，### §0.2 的第3个 # 导致
        [^#] 匹配失败，正则不停止，§0.6 块扩展到 §0.2/§0.3。
        """
        content = (
            "### §0.6 四图对齐视图\n"
            "\n"
            "一些内容\n"
            "\n"
            "### §0.2 对齐验证矩阵\n"
            "\n"
            "| 模块 | 状态 |\n"
        )
        match = gbp._S06_BLOCK_RE.search(content)
        assert match is not None
        assert "对齐验证矩阵" not in match.group(0), "§0.6 块误吞了 §0.2 内容"

    def test_stops_at_h3_heading_s03(self, gbp):
        """回归测试：§0.6 后跟 ### §0.3（3级标题）时必须停止。"""
        content = (
            "### §0.6 四图对齐视图\n"
            "\n"
            "内容\n"
            "\n"
            "### §0.3 版本-代码映射\n"
            "\n"
            "表格\n"
        )
        match = gbp._S06_BLOCK_RE.search(content)
        assert match is not None
        assert "版本-代码映射" not in match.group(0), "§0.6 块误吞了 §0.3 内容"

    def test_stops_at_h2_heading(self, gbp):
        """§0.6 后跟 ## §1（2级标题）时必须停止。"""
        content = (
            "### §0.6 四图对齐视图\n"
            "\n"
            "内容\n"
            "\n"
            "## 1. 核心概念\n"
            "\n"
            "正文\n"
        )
        match = gbp._S06_BLOCK_RE.search(content)
        assert match is not None
        assert "核心概念" not in match.group(0)

    def test_stops_at_hr_separator(self, gbp):
        """§0.6 后跟 --- 分隔线时必须停止。"""
        content = (
            "### §0.6 四图对齐视图\n"
            "\n"
            "内容\n"
            "\n"
            "---\n"
            "\n"
            "## 1. 核心概念\n"
        )
        match = gbp._S06_BLOCK_RE.search(content)
        assert match is not None
        assert "---" not in match.group(0)

    def test_h4_subheading_inside_s06_not_treated_as_boundary(self, gbp):
        """§0.6 内部的 #### 四图位置（4级标题）不应被当作边界，应包含在块内。"""
        content = (
            "### §0.6 四图对齐视图\n"
            "\n"
            "#### 四图位置\n"
            "\n"
            "| 图 | 位置 |\n"
            "\n"
            "#### 四核心字段\n"
            "\n"
            "| 字段 | 值 |\n"
            "\n"
            "---\n"
        )
        match = gbp._S06_BLOCK_RE.search(content)
        assert match is not None
        assert "四图位置" in match.group(0), "§0.6 块应包含内部 4 级子标题"
        assert "四核心字段" in match.group(0)

    def test_matches_h2_level_s06(self, gbp):
        """§0.6 用 ## （2级标题）时也能匹配。"""
        content = (
            "## §0.6 四图对齐视图\n"
            "\n"
            "内容\n"
            "\n"
            "---\n"
        )
        match = gbp._S06_BLOCK_RE.search(content)
        assert match is not None
        assert "内容" in match.group(0)

    def test_no_s06_returns_none(self, gbp):
        """无 §0.6 章节时返回 None。"""
        content = "### §0.1 代码文件清单\n\n内容\n"
        match = gbp._S06_BLOCK_RE.search(content)
        assert match is None


# ---------------------------------------------------------------------------
# _parse_simple_frontmatter 测试
# ---------------------------------------------------------------------------


class TestParseSimpleFrontmatter:
    """_parse_simple_frontmatter frontmatter 解析。"""

    def test_parses_basic_fields(self, gbp):
        """解析基本 key: value 字段。"""
        content = (
            "---\n"
            "module_id: MOD-GOV-029\n"
            "build_status: generated\n"
            "status: Active\n"
            "---\n"
            "\n"
            "正文\n"
        )
        fm = gbp._parse_simple_frontmatter(content)
        assert fm.get("module_id") == "MOD-GOV-029"
        assert fm.get("build_status") == "generated"
        assert fm.get("status") == "Active"

    def test_strips_quotes(self, gbp):
        """值带引号时去除引号。"""
        content = (
            "---\n"
            'module_id: "MOD-GOV-029"\n'
            "status: 'Active'\n"
            "---\n"
        )
        fm = gbp._parse_simple_frontmatter(content)
        assert fm.get("module_id") == "MOD-GOV-029"
        assert fm.get("status") == "Active"

    def test_skips_nested_fields(self, gbp):
        """跳过嵌套字段（以 [ 或 { 开头的值）。"""
        content = (
            "---\n"
            "module_id: MOD-GOV-029\n"
            "tags: [a, b, c]\n"
            "meta: {key: value}\n"
            "---\n"
        )
        fm = gbp._parse_simple_frontmatter(content)
        assert fm.get("module_id") == "MOD-GOV-029"
        assert "tags" not in fm
        assert "meta" not in fm

    def test_no_frontmatter_returns_empty(self, gbp):
        """无 frontmatter 时返回空 dict。"""
        content = "正文无 frontmatter\n"
        fm = gbp._parse_simple_frontmatter(content)
        assert fm == {}

    def test_skips_lines_without_colon(self, gbp):
        """跳过无冒号的行。"""
        content = (
            "---\n"
            "module_id: MOD-GOV-029\n"
            "这是一行没有冒号的文本\n"
            "---\n"
        )
        fm = gbp._parse_simple_frontmatter(content)
        assert fm.get("module_id") == "MOD-GOV-029"
        assert len(fm) == 1


# ---------------------------------------------------------------------------
# _S01_TABLE_ROW_RE 测试
# ---------------------------------------------------------------------------


class TestS01TableRowRegex:
    """_S01_TABLE_ROW_RE 表格数据行匹配。"""

    def test_matches_numbered_rows(self, gbp):
        """匹配 | N | ... 格式的数据行。"""
        content = "| 1 | src/foo.py | foo |\n| 2 | src/bar.py | bar |\n"
        matches = gbp._S01_TABLE_ROW_RE.findall(content)
        assert len(matches) == 2

    def test_no_match_header_row(self, gbp):
        """不匹配表头行（| # | ... |）。"""
        content = "| # | 文件 | 说明 |\n|---|------|------|\n"
        matches = gbp._S01_TABLE_ROW_RE.findall(content)
        assert len(matches) == 0

    def test_no_match_separator_row(self, gbp):
        """不匹配分隔行 |---|---|。"""
        content = "|---|------|------|\n"
        matches = gbp._S01_TABLE_ROW_RE.findall(content)
        assert len(matches) == 0