# [A_test] test_id=W4-SELFREF-001 | module=scripts/governance/d5_architecture/generators/externalize_algo_flow.py | gate=pytest
# [BLUEPRINT] MOD-GOV_ALGO_EXTRACTOR | scripts/governance/d5_architecture/generators/externalize_algo_flow.py | W4 自指豁免
# [MODULE] tests.governance.test_w4_selfref_exemption
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
"""test_w4_selfref_exemption.py — W4 自指 fixture 判据式豁免双向钉（裁定#392 施工授权）。

判据真源：docs/_working/archive/2026-09/2026-09-18-landing-anchor-algo-flow-closeout/
W4_selfref_exemption.md（谓词A=克隆区间⊆单一 Constant str；谓词B=解析器家族自引用；
禁路径白名单=裁定#273）。

双向钉（照卡验收）：
  钉1 谓词命中→豁免：克隆区间整体位于单一字符串字面量（夹具样本正文）→ 谓词 True；
  钉2 真克隆仍被抓：同形逻辑以真实可执行代码出现（或区间半出字符串）→ 谓词 False。
另钉谓词B 双向（解析器家族注释示例段=豁免；非解析器文件同形注释=不豁）与
不可解析源码=不豁（豁免必须可证）。

全程只调单函数 is_selfref_fixture_clone；夹具文件经 tmp_path 构造后读回文本，
零触真仓生成器批处理（禁全量）。
"""

from __future__ import annotations

import sys
from pathlib import Path

from zephyr.shared.io.paths import REPO_ROOT

_GOV_DIR = str(REPO_ROOT / "scripts" / "governance")
_GEN_DIR = str(REPO_ROOT / "scripts" / "governance" / "d5_architecture" / "generators")
for _p in (_GOV_DIR, _GEN_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import externalize_algo_flow as ext  # noqa: E402


def _span_of(src: str, start_needle: str, end_needle: str) -> tuple[int, int]:
    """夹具文本中 [start_needle 首行, end_needle 首行] 的 1 基闭区间行号。"""
    lines = src.splitlines()
    start = end = -1
    for i, ln in enumerate(lines):
        if start < 0 and start_needle in ln:
            start = i + 1
        if start > 0 and end_needle in ln:
            end = i + 1
            break
    assert start > 0 and end >= start, f"夹具缺标记: {start_needle!r}/{end_needle!r}"
    return start, end


def _mk_fixture(tmp_path: Path, name: str, src: str) -> Path:
    """tmp_path 构造夹具文件（测试隔离：禁写生产路径），返回路径。"""
    p = tmp_path / name
    p.write_text(src, encoding="utf-8")
    return p


# 钉1：谓词命中（docstring 内 ALGO_FLOW 样本=单一 Constant str）→ 豁免
_DOCSTRING_FIXTURE = '''"""demo —— 自指夹具模块（样本正文是数据不是实现）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 入参
# 层: 算法
# - id: A1
#   name_zh: 主流程
# [/ALGO_FLOW]
# 边:
# I1 --> A1
"""


def real_entry(x: int) -> int:
    return x + 1
'''


def test_predicate_a_clone_inside_single_string_literal_is_exempt(tmp_path: Path) -> None:
    src = _mk_fixture(tmp_path, "docstring_fixture.py", _DOCSTRING_FIXTURE).read_text(encoding="utf-8")
    s, e = _span_of(src, "# [ALGO_FLOW]", "# I1 --> A1")
    # 谓词A：区间整体位于单一字符串字面量内 → 豁免（fixture 自指对任一侧命中即本断言面）
    assert ext.is_selfref_fixture_clone(src, s, e) is True
    assert ext._SELFREF_FIXTURE_SKIP_REASON  # 豁免报因常数族在册（report 侧分类消费锚点）


# 钉2：真克隆仍被抓（两份真实可执行函数体，无字符串字面量可容身）
_REAL_CLONE_FIXTURE = """def compute_total(items):
    total = 0
    for it in items:
        total += it
    return total


def compute_total_copy(items):
    total = 0
    for it in items:
        total += it
    return total
"""


def test_real_code_clone_is_not_exempt(tmp_path: Path) -> None:
    src = _mk_fixture(tmp_path, "real_clone_fixture.py", _REAL_CLONE_FIXTURE).read_text(encoding="utf-8")
    s, e = _span_of(src, "def compute_total_copy", "return total")
    assert (s, e) == (8, 12)
    assert ext.is_selfref_fixture_clone(src, s, e) is False


def test_interval_half_outside_string_literal_is_not_exempt(tmp_path: Path) -> None:
    """变异钉：区间半出字符串字面量必须不豁（防"含交集即豁免"式放宽）。"""
    src = _mk_fixture(tmp_path, "half_span_fixture.py", _DOCSTRING_FIXTURE).read_text(encoding="utf-8")
    lines = src.splitlines()
    close_line = next(i + 1 for i, ln in enumerate(lines) if ln.strip() == '"""')
    # 从 docstring 倒数第二行起、穿过收引号直到真实代码行——只有一半在字面量内
    assert ext.is_selfref_fixture_clone(src, close_line - 1, close_line + 2) is False


# 谓词B 双向钉：解析器家族（按内容判定：AST 引用家族 API）的注释形态示例段
_PARSER_COMMENT_FIXTURE = """from _shared.code_algorithm_extractor import parse_algo_flow

# 用法示例（注释形态，非字符串字面量）：
# [ALGO_FLOW]
# - id: I1
# [/ALGO_FLOW]
result = parse_algo_flow("demo")
"""

_PLAIN_COMMENT_FIXTURE = """x = 1
# [ALGO_FLOW]
# - id: I1
# [/ALGO_FLOW]
"""


def test_predicate_b_parser_family_comment_example_is_exempt(tmp_path: Path) -> None:
    src = _mk_fixture(tmp_path, "parser_example_fixture.py", _PARSER_COMMENT_FIXTURE).read_text(encoding="utf-8")
    s, e = _span_of(src, "# 用法示例", "# [/ALGO_FLOW]")
    assert ext.is_selfref_fixture_clone(src, s, e) is True


def test_predicate_b_same_comments_in_non_parser_file_is_not_exempt(tmp_path: Path) -> None:
    """对照钉：同形注释块在非解析器文件（无家族 API 引用）不豁——B 靠内容不靠注释形态。"""
    src = _mk_fixture(tmp_path, "plain_comment_fixture.py", _PLAIN_COMMENT_FIXTURE).read_text(encoding="utf-8")
    s, e = _span_of(src, "# [ALGO_FLOW]", "# [/ALGO_FLOW]")
    assert ext.is_selfref_fixture_clone(src, s, e) is False


def test_unparsable_source_is_never_exempt() -> None:
    """豁免必须可证：源码不可解析一律 False（证不出就不豁）。"""
    assert ext.is_selfref_fixture_clone("def broken(:", 1, 1) is False
    assert ext.is_selfref_fixture_clone("", 0, 0) is False  # 非法区间同口径
