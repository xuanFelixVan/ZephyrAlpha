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
# [A_module] module_id=MOD-GOV-029 | layer=module | stability=volatile | safety=L | ai_autonomy=ai_modifiable
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
import re
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
        content = "### §0.6 五图对齐视图\n\n一些内容\n\n### §0.2 对齐验证矩阵\n\n| 模块 | 状态 |\n"
        match = gbp._S06_BLOCK_RE.search(content)
        assert match is not None
        assert "对齐验证矩阵" not in match.group(0), "§0.6 块误吞了 §0.2 内容"

    def test_stops_at_h3_heading_s03(self, gbp):
        """回归测试：§0.6 后跟 ### §0.3（3级标题）时必须停止。"""
        content = "### §0.6 五图对齐视图\n\n内容\n\n### §0.3 版本-代码映射\n\n表格\n"
        match = gbp._S06_BLOCK_RE.search(content)
        assert match is not None
        assert "版本-代码映射" not in match.group(0), "§0.6 块误吞了 §0.3 内容"

    def test_stops_at_h2_heading(self, gbp):
        """§0.6 后跟 ## §1（2级标题）时必须停止。"""
        content = "### §0.6 五图对齐视图\n\n内容\n\n## 1. 核心概念\n\n正文\n"
        match = gbp._S06_BLOCK_RE.search(content)
        assert match is not None
        assert "核心概念" not in match.group(0)

    def test_stops_at_hr_separator(self, gbp):
        """§0.6 后跟 --- 分隔线时必须停止。"""
        content = "### §0.6 五图对齐视图\n\n内容\n\n---\n\n## 1. 核心概念\n"
        match = gbp._S06_BLOCK_RE.search(content)
        assert match is not None
        assert "---" not in match.group(0)

    def test_h4_subheading_inside_s06_not_treated_as_boundary(self, gbp):
        """§0.6 内部的 #### 全景位置（4级标题）不应被当作边界，应包含在块内。"""
        content = "### §0.6 五图对齐视图\n\n#### 全景位置\n\n| 图 | 位置 |\n\n#### 四核心字段\n\n| 字段 | 值 |\n\n---\n"
        match = gbp._S06_BLOCK_RE.search(content)
        assert match is not None
        assert "全景位置" in match.group(0), "§0.6 块应包含内部 4 级子标题"
        assert "四核心字段" in match.group(0)

    def test_matches_h2_level_s06(self, gbp):
        """§0.6 用 ## （2级标题）时也能匹配。"""
        content = "## §0.6 五图对齐视图\n\n内容\n\n---\n"
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
        content = "---\nmodule_id: MOD-GOV-029\nbuild_status: generated\nstatus: Active\n---\n\n正文\n"
        fm = gbp._parse_simple_frontmatter(content)
        assert fm.get("module_id") == "MOD-GOV-029"
        assert fm.get("build_status") == "generated"
        assert fm.get("status") == "Active"

    def test_strips_quotes(self, gbp):
        """值带引号时去除引号。"""
        content = "---\nmodule_id: \"MOD-GOV-029\"\nstatus: 'Active'\n---\n"
        fm = gbp._parse_simple_frontmatter(content)
        assert fm.get("module_id") == "MOD-GOV-029"
        assert fm.get("status") == "Active"

    def test_skips_nested_fields(self, gbp):
        """跳过嵌套字段（以 [ 或 { 开头的值）。"""
        content = "---\nmodule_id: MOD-GOV-029\ntags: [a, b, c]\nmeta: {key: value}\n---\n"
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
        content = "---\nmodule_id: MOD-GOV-029\n这是一行没有冒号的文本\n---\n"
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


# ---------------------------------------------------------------------------
# _remove_s06_block / _cleanup_orphan_s06 测试
# (#ARCH-REGEN-CONCURRENCY-001 P2-2a：已删除模块 §0.6 残留清理)
# ---------------------------------------------------------------------------
#
# 背景：generate_all 原先只遍历 depgraph_map.keys()，对已从 depgraph 删除但蓝图
# 仍残留 §0.6 的模块（孤儿）不做清理，导致 §0.6 内容陈旧。P2-2a 新增
# _remove_s06_block（纯函数：移除单个蓝图文本的 §0.6）+ _cleanup_orphan_s06
# （编排：比对 blueprint_map 与 depgraph 模块集合，清理孤儿）。
#
# 测试策略：先写测试（TDD red），再实现函数（green）。纯函数 + tmp_path 文件 IO，
# 无需 DB 连接。
# ---------------------------------------------------------------------------


def _make_blueprint_with_s06(module_id: str = "MOD-DELETED-001") -> str:
    """构造带 §0.6 的蓝图文本（结构对标 _replace_or_insert_s06 插入后的产物）。"""
    return (
        "---\n"
        f"module_id: {module_id}\n"
        "status: Active\n"
        "---\n"
        "\n"
        "### §0.1 代码文件清单\n"
        "\n"
        "| # | 文件 | 说明 |\n"
        "|---|------|------|\n"
        "| 1 | src/foo.py | foo |\n"
        "\n"
        "### §0.6 五图对齐视图\n"
        "\n"
        "<!-- AUTOGEN: source=depgraph+dataflow+decision -->\n"
        "\n"
        "> **自动生成**：本节由 generate_blueprint_panorama.py 派生。\n"
        "\n"
        "#### 全景位置\n"
        "\n"
        "| 图 | 位置 | 状态 |\n"
        "|----|------|------|\n"
        "\n"
        "#### 四核心字段\n"
        "\n"
        "| 字段 | depgraph 值 | 蓝图值 | 是否一致 |\n"
        "|------|------------|--------|:-------:|\n"
        "\n"
        "> 冲突时以 depgraph 为准。\n"
        "\n"
        "---\n"
        "\n"
        "## 1. 核心概念\n"
        "\n"
        "正文\n"
    )


class TestRemoveS06Block:
    """_remove_s06_block：移除孤儿蓝图中的 §0.6 自动生成章节。"""

    def test_removes_s06_block_and_closing_separator(self, gbp):
        """§0.6 + 其闭合 --- 分隔线一并移除，§0.1 与 §1 保留。"""
        content = _make_blueprint_with_s06()
        result = gbp._remove_s06_block(content)
        assert "### §0.6" not in result, "§0.6 标题未移除"
        assert "AUTOGEN" not in result, "§0.6 自动生成内容未移除"
        assert "全景位置" not in result, "§0.6 全景位置表未移除"
        assert "### §0.1 代码文件清单" in result, "§0.1 被误删"
        assert "## 1. 核心概念" in result, "§1 被误删"
        assert "src/foo.py" in result, "§0.1 表格内容被误删"

    def test_no_orphan_separator_left(self, gbp):
        """移除后不遗留孤立 --- 分隔线（原 §0.6 的闭合分隔线）。

        注意：§0.1 表格的分隔行 |---|------|------| 合法包含 ---，不算孤立分隔线。
        孤立分隔线指独占一行的 --- 水平线（frontmatter 闭合 / §0.6 闭合产物）。
        """
        content = _make_blueprint_with_s06()
        result = gbp._remove_s06_block(content)
        # §0.1 与 §1 之间不应遗留 §0.6 原闭合的 ---（独占一行的水平线，非表格分隔行）
        s01_idx = result.index("### §0.1")
        s1_idx = result.index("## 1. 核心概念")
        between = result[s01_idx:s1_idx]
        orphan_hr = re.search(r"^---\s*$", between, re.MULTILINE)
        assert orphan_hr is None, f"§0.1 与 §1 之间遗留孤立分隔线: {between!r}"

    def test_idempotent(self, gbp):
        """二次移除 = 一次移除（无 §0.6 时原样返回 → 幂等）。"""
        content = _make_blueprint_with_s06()
        once = gbp._remove_s06_block(content)
        twice = gbp._remove_s06_block(once)
        assert once == twice, "二次移除结果不一致，非幂等"

    def test_no_s06_returns_unchanged(self, gbp):
        """无 §0.6 章节时原样返回。"""
        content = "---\nmodule_id: MOD-X\n---\n\n### §0.1 代码文件清单\n\n| # | 文件 |\n\n## 1. 核心概念\n"
        assert gbp._remove_s06_block(content) == content

    def test_s06_without_separator_followed_by_h2(self, gbp):
        """§0.6 后直接跟 ## §1（无闭合 ---）时，§0.6 移除、§1 保留。"""
        content = "### §0.1 清单\n\n内容\n\n### §0.6 五图对齐视图\n\n自动生成内容\n\n## 1. 核心概念\n\n正文\n"
        result = gbp._remove_s06_block(content)
        assert "### §0.6" not in result
        assert "自动生成内容" not in result
        assert "### §0.1 清单" in result
        assert "## 1. 核心概念" in result

    def test_s06_at_end_of_file(self, gbp):
        """§0.6 位于文件末尾时干净移除，前置内容保留。"""
        content = "### §0.1 清单\n\n内容\n\n### §0.6 五图对齐视图\n\n末尾自动生成内容\n"
        result = gbp._remove_s06_block(content)
        assert "### §0.6" not in result
        assert "末尾自动生成内容" not in result
        assert "### §0.1 清单" in result
        assert "内容" in result

    def test_preserves_frontmatter(self, gbp):
        """frontmatter 不受影响。"""
        content = _make_blueprint_with_s06(module_id="MOD-KEEP-FM")
        result = gbp._remove_s06_block(content)
        assert result.startswith("---\n")
        assert "module_id: MOD-KEEP-FM" in result
        assert "status: Active" in result


class TestCleanupOrphanS06:
    """_cleanup_orphan_s06：清理已从 depgraph 删除的孤儿蓝图 §0.6。"""

    def _make_bp(self, gbp, tmp_path, module_id, with_s06=True):
        """构造 BlueprintFrontmatter（content 写入 tmp_path 文件）。"""
        fpath = tmp_path / f"{module_id}.md"
        if with_s06:
            content = _make_blueprint_with_s06(module_id=module_id)
        else:
            content = f"---\nmodule_id: {module_id}\n---\n\n## 1. 核心概念\n"
        fpath.write_text(content, encoding="utf-8")
        return gbp.BlueprintFrontmatter(
            module_id=module_id,
            responsibility_domain="",
            design_maturity="",
            build_status="",
            status="Active",
            file_path=fpath,
            content=content,
        )

    def test_cleans_orphan_with_s06(self, gbp, tmp_path):
        """孤儿蓝图（不在 depgraph）有 §0.6 → 清理并返回 1。"""
        bp = self._make_bp(gbp, tmp_path, "MOD-DELETED-001", with_s06=True)
        blueprint_map = {"MOD-DELETED-001": bp}
        cleaned = gbp._cleanup_orphan_s06(blueprint_map, set(), dry_run=False)
        assert cleaned == 1
        new_content = bp.file_path.read_text(encoding="utf-8")
        assert "### §0.6" not in new_content
        assert "## 1. 核心概念" in new_content

    def test_skips_non_orphan(self, gbp, tmp_path):
        """非孤儿（在 depgraph 中）蓝图不被清理。"""
        bp = self._make_bp(gbp, tmp_path, "MOD-ALIVE-001", with_s06=True)
        blueprint_map = {"MOD-ALIVE-001": bp}
        original = bp.file_path.read_text(encoding="utf-8")
        cleaned = gbp._cleanup_orphan_s06(blueprint_map, {"MOD-ALIVE-001"}, dry_run=False)
        assert cleaned == 0
        assert bp.file_path.read_text(encoding="utf-8") == original

    def test_skips_orphan_without_s06(self, gbp, tmp_path):
        """孤儿蓝图无 §0.6 → 不动文件，返回 0。"""
        bp = self._make_bp(gbp, tmp_path, "MOD-DELETED-002", with_s06=False)
        blueprint_map = {"MOD-DELETED-002": bp}
        original = bp.file_path.read_text(encoding="utf-8")
        cleaned = gbp._cleanup_orphan_s06(blueprint_map, set(), dry_run=False)
        assert cleaned == 0
        assert bp.file_path.read_text(encoding="utf-8") == original

    def test_dry_run_does_not_write(self, gbp, tmp_path):
        """dry_run=True → 返回计数但不写文件。"""
        bp = self._make_bp(gbp, tmp_path, "MOD-DELETED-003", with_s06=True)
        blueprint_map = {"MOD-DELETED-003": bp}
        original = bp.file_path.read_text(encoding="utf-8")
        cleaned = gbp._cleanup_orphan_s06(blueprint_map, set(), dry_run=True)
        assert cleaned == 1
        assert bp.file_path.read_text(encoding="utf-8") == original, "dry_run 不应写文件"

    def test_multiple_orphans(self, gbp, tmp_path):
        """多个孤儿蓝图 → 全部清理，存活模块不动，返回正确计数。"""
        bp1 = self._make_bp(gbp, tmp_path, "MOD-DEL-A", with_s06=True)
        bp2 = self._make_bp(gbp, tmp_path, "MOD-DEL-B", with_s06=True)
        bp_alive = self._make_bp(gbp, tmp_path, "MOD-ALIVE", with_s06=True)
        blueprint_map = {"MOD-DEL-A": bp1, "MOD-DEL-B": bp2, "MOD-ALIVE": bp_alive}
        cleaned = gbp._cleanup_orphan_s06(blueprint_map, {"MOD-ALIVE"}, dry_run=False)
        assert cleaned == 2
        assert "### §0.6" not in bp1.file_path.read_text(encoding="utf-8")
        assert "### §0.6" not in bp2.file_path.read_text(encoding="utf-8")
        assert "### §0.6" in bp_alive.file_path.read_text(encoding="utf-8"), "存活模块 §0.6 不应被清理"
