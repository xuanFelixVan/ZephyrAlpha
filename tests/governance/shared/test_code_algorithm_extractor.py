# [A_test] module_id: MOD-GOV_ALGO_EXTRACTOR | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_ALGO_EXTRACTOR | docs/03_modules/_cross_layer/gov_scripts/blueprint.md
# [MODULE] tests.governance.shared.test_code_algorithm_extractor
# [DOMAIN] D_GOVERNANCE
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_code_algorithm_extractor.py — 模块核心算法提取器单元测试。

覆盖：
- extract_algorithm_from_code：有 docstring+header → 断言字段；truncate=True/False 对比
- extract_algorithm_from_blueprint：有 frontmatter+章节 → 断言字段
- build_blueprint_index：临时目录 2 个 blueprint → 断言映射
- 降级：文件不存在 / 无 docstring / 损坏 AST → source_type='empty' 不抛
"""

from __future__ import annotations

import sys
from pathlib import Path

from zephyr.shared.io.paths import REPO_ROOT

_GOV_DIR = str(REPO_ROOT / "scripts" / "governance")
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.code_algorithm_extractor import (  # noqa: E402
    AlgorithmSummary,
    build_blueprint_index,
    clear_blueprint_cache,
    extract_algorithm_from_blueprint,
    extract_algorithm_from_code,
)

# ── 测试用 .py 文件模板 ──────────────────────────────────────

_PY_WITH_DOCSTRING = '''"""TestModule — 测试用模块（算法提取器验证）。

概述：这是一个测试模块，用于验证算法提取器的 docstring 解析能力。

算法步骤：
  ① 接收输入数据
  ② 校验不变量
  ③ 返回处理结果

不变量：
  input >= 0
  output <= max_value
"""

# [BLUEPRINT] MOD-TEST-001 | docs/03_modules/test/blueprint.md
# [MODULE] tests.test_module
# [INVARIANTS] input>=0; output<=max_value; 降级不抛异常
# [DOMAIN] D_TEST
'''

_PY_NO_DOCSTRING = """# [BLUEPRINT] MOD-TEST-002 | docs/03_modules/test/blueprint.md
# [MODULE] tests.test_no_docstring

def helper():
    pass
"""

_PY_BROKEN_AST = """def broken(
    # 缺少右括号和冒号
"""

# 真文字 + ALGO_FLOW 标记块（含 # 边: 段）混合的 docstring
_PY_WITH_ALGO_FLOW = '''"""价格笼子校验模块。

A 股价格笼子校验，超范围委托直接废单。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 委托限价 limit_price
#   code: check_price_cage (price_cage.py L148)
# 层: 算法
# - id: A1
#   name_zh: ① 笼子边界计算
#   name_en: check_price_cage
#   inputs: I1
#   outputs: PriceCageResult
# 层: 输出
# - id: O1
#   name_zh: 校验结果
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

# [MODULE] tests.test_algo_flow
# [INVARIANTS] 超限夹到边界
'''

# 纯 ALGO_FLOW 标记的 docstring（包入口常见：除标记外无人类可读文字）
_PY_ONLY_ALGO_FLOW = '''"""
# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包导入请求
# 层: 算法
# - id: A1
#   name_zh: ① 包级聚合再导出
#   inputs: I1
#   outputs: 包公共命名空间
# [/ALGO_FLOW]
# 边:
# I1 --> A1
"""

# [MODULE] tests.test_only_flow
'''

_BLUEPRINT_MD = """\
---
module_id: MOD-TEST-BP-001
title: 测试蓝图模块
description: 用于验证蓝图算法提取
---

# 测试蓝图模块

## 概述

这是一个测试蓝图，用于验证算法提取器从 blueprint.md 提取算法的能力。

## 核心规则

1. 输入数据必须经过校验
2. 处理过程中不得违反不变量
3. 输出结果需要持久化

## 关键不变量

- input >= 0
- output <= max_value
- 处理超时需降级
"""


# ── extract_algorithm_from_code ─────────────────────────────


def test_extract_from_code_basic(tmp_path, monkeypatch):
    """有 docstring + header 的 .py → source_type='code'，字段正确。"""
    py = tmp_path / "test_module.py"
    py.write_text(_PY_WITH_DOCSTRING, encoding="utf-8")

    # patch REPO_ROOT 使 relative_to(tmp_path) 可行
    import _shared.code_algorithm_extractor as ext

    monkeypatch.setattr(ext, "REPO_ROOT", tmp_path)

    result = extract_algorithm_from_code(py, module_id="MOD-TEST-001")
    assert result.source_type == "code"
    assert result.module_id == "MOD-TEST-001"
    assert "测试用模块" in result.module_name or "TestModule" in result.module_name
    assert result.summary, "概述不应为空"
    assert result.algo_steps, "算法步骤不应为空"
    assert "接收输入数据" in result.algo_steps
    assert result.invariants, "不变量不应为空"
    assert "input>=0" in result.invariants
    assert result.source_path.endswith("test_module.py")
    assert result.quality_issue.startswith("✅")


def test_extract_from_code_truncate_false(tmp_path, monkeypatch):
    """truncate=False 时算法步骤不截断（完整文本）。"""
    long_docstring = '"""LongModule — 长文档模块。\n\n算法步骤：\n' + "步骤内容很长。" * 200 + '\n"""\n'
    py = tmp_path / "long_module.py"
    py.write_text(long_docstring, encoding="utf-8")

    import _shared.code_algorithm_extractor as ext

    monkeypatch.setattr(ext, "REPO_ROOT", tmp_path)

    result_trunc = extract_algorithm_from_code(py, module_id="MOD-LONG", truncate=True)
    result_full = extract_algorithm_from_code(py, module_id="MOD-LONG", truncate=False)

    assert len(result_full.algo_steps) > len(result_trunc.algo_steps), "truncate=False 应返回更长文本"
    assert "…" not in result_full.algo_steps, "truncate=False 不应有截断省略号"
    assert result_trunc.algo_steps.endswith("…"), "truncate=True 应有截断省略号"


def test_extract_from_code_no_docstring(tmp_path, monkeypatch):
    """无 docstring 的 .py → source_type='empty'，不抛异常。"""
    py = tmp_path / "no_doc.py"
    py.write_text(_PY_NO_DOCSTRING, encoding="utf-8")

    import _shared.code_algorithm_extractor as ext

    monkeypatch.setattr(ext, "REPO_ROOT", tmp_path)

    result = extract_algorithm_from_code(py, module_id="MOD-TEST-002")
    assert result.source_type == "empty"
    assert "无 module docstring" in result.quality_issue


def test_extract_from_code_file_not_exists(tmp_path):
    """文件不存在 → source_type='empty'。"""
    result = extract_algorithm_from_code(tmp_path / "nonexistent.py", module_id="MOD-X")
    assert result.source_type == "empty"
    assert "不存在" in result.quality_issue


def test_extract_from_code_broken_ast(tmp_path, monkeypatch):
    """AST 损坏 → source_type='empty'，不抛异常。"""
    py = tmp_path / "broken.py"
    py.write_text(_PY_BROKEN_AST, encoding="utf-8")

    import _shared.code_algorithm_extractor as ext

    monkeypatch.setattr(ext, "REPO_ROOT", tmp_path)

    result = extract_algorithm_from_code(py, module_id="MOD-BROKEN")
    assert result.source_type == "empty"


# ── ALGO_FLOW 标记块剥离（2026-08-13 泄漏修复回归）─────────────


def test_algo_flow_markers_stripped_from_text_fields(tmp_path, monkeypatch):
    """真文字+ALGO_FLOW 混合 docstring：概述/算法步骤不含标记行，推导图照常解析。"""
    py = tmp_path / "flow_module.py"
    py.write_text(_PY_WITH_ALGO_FLOW, encoding="utf-8")

    import _shared.code_algorithm_extractor as ext

    monkeypatch.setattr(ext, "REPO_ROOT", tmp_path)

    result = extract_algorithm_from_code(py, module_id="MOD-FLOW-001")
    assert result.source_type == "code"
    for field_value in (result.summary, result.algo_steps, result.module_name):
        assert "[ALGO_FLOW]" not in field_value, "文字字段不应含 ALGO_FLOW 起止标记"
        assert "# 边" not in field_value, "文字字段不应含 # 边: 段残行"
        assert "# - id:" not in field_value, "文字字段不应含节点定义行"
        assert "name_zh:" not in field_value, "文字字段不应含字段行"
    assert "价格笼子校验" in result.summary, "概述应为剥离标记后的纯文字"
    assert result.algo_flow is not None, "ALGO_FLOW 块仍应解析成推导图数据"
    assert {n.id for n in result.algo_flow.nodes} == {"I1", "A1", "O1"}
    assert len(result.algo_flow.edges) == 2


def test_algo_flow_only_docstring_yields_empty_text(tmp_path, monkeypatch):
    """纯标记 docstring（包入口）：概述/算法步骤为空（生成器提示看图），质量仍 ✅。"""
    py = tmp_path / "only_flow_pkg.py"
    py.write_text(_PY_ONLY_ALGO_FLOW, encoding="utf-8")

    import _shared.code_algorithm_extractor as ext

    monkeypatch.setattr(ext, "REPO_ROOT", tmp_path)

    result = extract_algorithm_from_code(py, module_id="MOD-FLOW-002")
    assert result.source_type == "code"
    assert result.summary == "", "纯标记 docstring 概述应为空，不得挤入 YAML 标记"
    assert result.algo_steps == "", "纯标记 docstring 算法步骤应为空，不得截断残留「# 边…」"
    assert "#" not in result.module_name, "模块名不应是 # 标记行"
    assert result.algo_flow is not None
    assert result.quality_issue.startswith("✅"), "有推导图的模块不应误报结构不完整"


# ── extract_algorithm_from_blueprint ────────────────────────


def test_extract_from_blueprint_basic(tmp_path, monkeypatch):
    """有 frontmatter + 核心规则章节 → source_type='blueprint'，字段正确。"""
    bp = tmp_path / "blueprint.md"
    bp.write_text(_BLUEPRINT_MD, encoding="utf-8")

    import _shared.code_algorithm_extractor as ext

    monkeypatch.setattr(ext, "REPO_ROOT", tmp_path)

    result = extract_algorithm_from_blueprint(bp, module_id="MOD-TEST-BP-001")
    assert result.source_type == "blueprint"
    assert result.module_id == "MOD-TEST-BP-001"
    assert "测试蓝图" in result.module_name or "MOD-TEST-BP-001" in result.module_name
    assert result.algo_steps, "算法步骤（核心规则）不应为空"
    assert "输入数据必须经过校验" in result.algo_steps
    assert result.invariants, "不变量不应为空"
    assert "input >= 0" in result.invariants
    assert result.quality_issue.startswith("✅")


def test_extract_from_blueprint_not_exists(tmp_path):
    """蓝图文件不存在 → source_type='empty'。"""
    result = extract_algorithm_from_blueprint(tmp_path / "no_bp.md", module_id="MOD-X")
    assert result.source_type == "empty"
    assert "不存在" in result.quality_issue


def test_extract_from_blueprint_truncate_false(tmp_path, monkeypatch):
    """truncate=False 时蓝图算法步骤不截断。"""
    long_body = "## 核心规则\n\n" + "这是一条很长的规则。" * 200 + "\n"
    bp = tmp_path / "long_bp.md"
    bp.write_text("---\nmodule_id: MOD-LONG-BP\ntitle: 长蓝图\n---\n\n" + long_body, encoding="utf-8")

    import _shared.code_algorithm_extractor as ext

    monkeypatch.setattr(ext, "REPO_ROOT", tmp_path)

    result_trunc = extract_algorithm_from_blueprint(bp, truncate=True)
    result_full = extract_algorithm_from_blueprint(bp, truncate=False)
    assert len(result_full.algo_steps) > len(result_trunc.algo_steps)


# ── build_blueprint_index ───────────────────────────────────


def test_build_blueprint_index(tmp_path, monkeypatch):
    """扫描临时目录的 blueprint.md → 返回 {module_id: path} 映射。"""
    # 创建 2 个 blueprint.md
    bp1_dir = tmp_path / "MOD-TEST-A"
    bp1_dir.mkdir()
    (bp1_dir / "blueprint.md").write_text(
        "---\nmodule_id: MOD-TEST-A\ntitle: 模块A\n---\n\n# 模块A\n", encoding="utf-8"
    )
    bp2_dir = tmp_path / "MOD-TEST-B"
    bp2_dir.mkdir()
    (bp2_dir / "blueprint.md").write_text(
        "---\nmodule_id: MOD-TEST-B\ntitle: 模块B\n---\n\n# 模块B\n", encoding="utf-8"
    )

    # 清缓存确保干净状态
    clear_blueprint_cache()
    import _shared.code_algorithm_extractor as ext

    monkeypatch.setattr(ext, "REPO_ROOT", tmp_path)

    index = build_blueprint_index(blueprints_root=tmp_path)
    assert "MOD-TEST-A" in index
    assert "MOD-TEST-B" in index
    assert index["MOD-TEST-A"].name == "blueprint.md"
    assert index["MOD-TEST-B"].parent.name == "MOD-TEST-B"

    # 清理缓存（避免影响其他测试）
    clear_blueprint_cache()


def test_build_blueprint_index_cached(tmp_path, monkeypatch):
    """build_blueprint_index 模块级缓存：第二次调用不重新扫描。"""
    clear_blueprint_cache()
    import _shared.code_algorithm_extractor as ext

    monkeypatch.setattr(ext, "REPO_ROOT", tmp_path)

    bp_dir = tmp_path / "MOD-CACHE"
    bp_dir.mkdir()
    (bp_dir / "blueprint.md").write_text("---\nmodule_id: MOD-CACHE\n---\n\n# Cache Test\n", encoding="utf-8")

    idx1 = build_blueprint_index(blueprints_root=tmp_path)
    assert "MOD-CACHE" in idx1

    # 新增一个 blueprint（缓存应不会感知）
    bp2_dir = tmp_path / "MOD-CACHE-2"
    bp2_dir.mkdir()
    (bp2_dir / "blueprint.md").write_text("---\nmodule_id: MOD-CACHE-2\n---\n\n# Cache Test 2\n", encoding="utf-8")

    idx2 = build_blueprint_index()  # 不传 root，用缓存
    assert "MOD-CACHE-2" not in idx2, "缓存应未感知新增 blueprint"


# ── ALGO_FLOW 外部真源（2026-09-15 外审遗留①：P2-1 出仓实施）─────────────────


def test_external_algo_flow_anchor_loaded(tmp_path, monkeypatch):
    """docstring 一行 external 锚 → extractor 从 yaml 加载块，parse_algo_flow 同管线出图。"""
    import _shared.code_algorithm_extractor as ext

    monkeypatch.setattr(ext, "REPO_ROOT", tmp_path)
    yaml_rel = "docs/03_modules/_domain_test/algo_flow/test_mod.yaml"
    ydir = tmp_path / "docs" / "03_modules" / "_domain_test" / "algo_flow"
    ydir.mkdir(parents=True)
    block = """# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 输入参数
# 层: 算法
# - id: A1
#   name_zh: 处理器
#   name_en: Processor
# 层: 输出
# - id: O1
#   name_zh: 返回值
#
# 边:
# I1 --> A1
# A1 --> O1
# [/ALGO_FLOW]
"""
    (ydir / "test_mod.yaml").write_text(
        "algo_flow: |\n"
        + "\n".join(("    " + ln) if ln.strip() else "" for ln in block.rstrip("\n").splitlines())
        + "\n",
        encoding="utf-8",
    )

    mod = tmp_path / "test_mod.py"
    mod_src = '"""TestExtMod — 外部锚行测试模块。\n\n概述：验证 external 锚行加载。\n\n# [ALGO_FLOW] external: ' + yaml_rel + '\n"""\n\nX = 1\n'
    mod.write_text(mod_src, encoding="utf-8")
    s = ext.extract_algorithm_from_code(mod, module_id="MOD-TEST-EXT", truncate=False)
    assert s.source_type == "code"
    assert s.algo_flow is not None, "外部块应被加载并解析出推导图"
    node_ids = [n.id for n in s.algo_flow.nodes]
    assert "I1" in node_ids and "A1" in node_ids and "O1" in node_ids
    assert [(e.src, e.dst) for e in s.algo_flow.edges] == [("I1", "A1"), ("A1", "O1")]
    # 锚行不泄漏进文字字段
    assert "ALGO_FLOW" not in (s.summary or "") and "ALGO_FLOW" not in (s.algo_steps or "")


def test_external_algo_flow_missing_yaml_degrades(tmp_path, monkeypatch):
    """锚行指向的 yaml 不存在 → 降级 algo_flow=None（回退文字卡片），不抛异常。"""
    import _shared.code_algorithm_extractor as ext

    monkeypatch.setattr(ext, "REPO_ROOT", tmp_path)
    mod = tmp_path / "test_mod_missing.py"
    mod.write_text(
        '"""TestExtMissing — 外部锚行缺失测试。\n\n概述：yaml 缺失时降级。\n\n# [ALGO_FLOW] external: docs/03_modules/_domain_test/algo_flow/ghost.yaml\n"""\n\nX = 1\n',
        encoding="utf-8",
    )
    s = ext.extract_algorithm_from_code(mod, module_id="MOD-TEST-EXT2", truncate=False)
    assert s.source_type == "code"
    assert s.algo_flow is None


def test_external_algo_flow_path_escape_rejected(tmp_path, monkeypatch):
    """安全护栏：锚路径非 docs/ 前缀或非 .yaml → 拒绝加载（路径逃逸防护）。"""
    import _shared.code_algorithm_extractor as ext

    monkeypatch.setattr(ext, "REPO_ROOT", tmp_path)
    # 非法前缀：src/（即使文件存在也不得加载）
    evil_dir = tmp_path / "src"
    evil_dir.mkdir()
    (evil_dir / "evil.yaml").write_text("algo_flow: |\n    # [ALGO_FLOW]\n    # 层: 输入\n    # - id: I1\n", encoding="utf-8")
    mod = tmp_path / "test_evil.py"
    mod.write_text(
        '"""TestEvil — 路径逃逸测试。\n\n# [ALGO_FLOW] external: src/evil.yaml\n"""\n\nX = 1\n',
        encoding="utf-8",
    )
    s = ext.extract_algorithm_from_code(mod, module_id="MOD-TEST-EVIL", truncate=False)
    assert s.algo_flow is None, "非 docs/ 前缀的外部块必须拒绝"

    clear_blueprint_cache()


# ── 修正点①前置豁免：__init__ 自身声明图优先于子文件回扫（2026-09-16 F-A 治本）──

_YAML_ONE_NODE = "algo_flow: |\n    # [ALGO_FLOW]\n    # 层: 输入\n    # - id: PKG1\n    #   name: 包公共面\n    # [/ALGO_FLOW]\n"


def _rich_child(tmp_path, rel="pkg/child.py", n=600):
    """写一个 docstring 远超 _RICH_DOC_LEN 的子模块（旧口径下它会顶掉包入口卡片）。"""
    p = tmp_path / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        '"""ChildRich — 子模块算法真源。\n\n' + "填充说明文字。" * n + '\n"""\n\nY = 1\n',
        encoding="utf-8",
    )
    return p


def test_init_with_anchor_graph_wins_over_rich_child(tmp_path, monkeypatch):
    """包入口仅一行锚（docstring 缩到阈值下）→ 卡片必须仍解到自身，不得张冠李戴给子模块。"""
    import _shared.code_algorithm_extractor as ext

    monkeypatch.setattr(ext, "REPO_ROOT", tmp_path)
    _rich_child(tmp_path)
    yaml_dir = tmp_path / "docs/03_modules/_domain_test/algo_flow"
    yaml_dir.mkdir(parents=True)
    (yaml_dir / "pkg__init__.yaml").write_text(_YAML_ONE_NODE, encoding="utf-8")
    init = tmp_path / "pkg/__init__.py"
    init.write_text(
        '"""PkgInit — 包入口（算法图已出仓）。\n\n'
        "# [ALGO_FLOW] external: docs/03_modules/_domain_test/algo_flow/pkg__init__.yaml\n"
        '"""\n\nZ = 1\n',
        encoding="utf-8",
    )
    s = ext.extract_algorithm_from_code(init, module_id="MOD-TEST-FA1", truncate=False)
    assert s.source_path.replace("\\", "/").endswith("pkg/__init__.py")
    assert [n.id for n in s.algo_flow.nodes] == ["PKG1"]


def test_init_with_short_inline_block_wins_over_rich_child(tmp_path, monkeypatch):
    """判据=「自身是否声明了图」而非 docstring 长度：短内联块同样不得被子文件顶掉。"""
    import _shared.code_algorithm_extractor as ext

    monkeypatch.setattr(ext, "REPO_ROOT", tmp_path)
    _rich_child(tmp_path)
    init = tmp_path / "pkg2/__init__.py"
    init.parent.mkdir(parents=True, exist_ok=True)
    init.write_text(
        '"""PkgInit2 — 包入口。\n\n'
        "# [ALGO_FLOW]\n# 层: 输入\n# - id: PKG2\n# [/ALGO_FLOW]\n"
        '"""\n\nZ = 1\n',
        encoding="utf-8",
    )
    s = ext.extract_algorithm_from_code(init, module_id="MOD-TEST-FA2", truncate=False)
    assert [n.id for n in s.algo_flow.nodes] == ["PKG2"]


def test_init_without_own_graph_still_rescans_rich_child(tmp_path, monkeypatch):
    """既有意图不回退：包入口自身无图 → 仍回扫富 docstring 子文件（修正点①原语义）。"""
    import _shared.code_algorithm_extractor as ext

    monkeypatch.setattr(ext, "REPO_ROOT", tmp_path)
    child = _rich_child(tmp_path, rel="pkg3/child.py")  # noqa: F841 — 仅需存在供回扫命中
    init = tmp_path / "pkg3/__init__.py"
    init.write_text('"""PkgInit3 — 包入口说明，无算法图。\n"""\n\nZ = 1\n', encoding="utf-8")
    s = ext.extract_algorithm_from_code(init, module_id="MOD-TEST-FA3", truncate=False)
    assert s.source_path.replace("\\", "/").endswith("pkg3/child.py")

    clear_blueprint_cache()
