# [TTL] permanent
"""F7 上下文豁免通道红蓝测试（st-govfix-g4-20261007）。

被测：scripts/governance/d3_metadata/check_vocab_hardcode.py 的
``# gate-vocab-context:`` 行尾标注通道（检测4/9/10 值匹配豁免）。

红蓝矩阵：
- 红：A/B/C/D 字面量集合无标注 → 报（governance_family 4/4 全子集）
- 蓝：同名值集合 + 行尾标注点名 governance_family → 不报
- 红：标注点名错误词表 → 惰性标注照报（防滥用）
- 红：检测1 变量名匹配不受标注影响（VALID_* 命中照报）
- 红：safety_level H/M 单字母默认照报（盲区3 治本不放宽）
- 蓝：safety_level H/M + 点名 safety_level 标注 → 不报（per-line 通道）

测试隔离：vocab_values 手工构造（不依赖仓库词表目录），vocab_dir 指 tmp_path
（检测2 引用存在性无引用即不触发），输出零落盘生产路径。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "governance" / "d3_metadata" / "check_vocab_hardcode.py"
sys.path.insert(0, str(SCRIPT.parent))

import check_vocab_hardcode as cvh  # noqa: E402

# 手工构造词表值域（镜像 governance_family/safety_level 真值，避免依赖仓库词表目录）
_VOCAB_VALUES = {
    "governance_family": {"A", "B", "C", "D"},
    "safety_level": {"H", "M", "L"},
}


def _check(tmp_path: Path, source: str) -> list[tuple[int, str]]:
    """写临时 .py 文件并跑 _check_file，返回违规列表。"""
    f = tmp_path / "sample.py"
    f.write_text(source, encoding="utf-8")
    return cvh._check_file(f, tmp_path, startup_values=None, vocab_values=_VOCAB_VALUES)


def test_red_family_abcd_without_annotation_reports(tmp_path: Path) -> None:
    """红：治理家族 A/B/C/D 字面量集合无标注 → 值匹配照报（误伤面存在性钉死）。"""
    issues = _check(tmp_path, 'FAMILY_PRIORITY = ["A", "B", "C", "D"]\n')
    assert len(issues) == 1
    assert "governance_family" in issues[0][1]


def test_blue_family_abcd_with_annotation_passes(tmp_path: Path) -> None:
    """蓝：行尾标注点名 governance_family → 值匹配豁免（F7 通道主用例）。"""
    issues = _check(
        tmp_path,
        'FAMILY_PRIORITY = ["A", "B", "C", "D"]  # gate-vocab-context: governance_family\n',
    )
    assert issues == []


def test_red_wrong_vocab_annotation_inert(tmp_path: Path) -> None:
    """红：标注点名错误词表（status ≠ 命中的 governance_family）→ 惰性标注照报。"""
    issues = _check(
        tmp_path,
        'FAMILY_PRIORITY = ["A", "B", "C", "D"]  # gate-vocab-context: status\n',
    )
    assert len(issues) == 1
    assert "governance_family" in issues[0][1]


def test_red_detection1_varname_not_exempted(tmp_path: Path) -> None:
    """红：检测1 变量名匹配（VALID_*）不受上下文标注影响——真复制无法借道逃逸。"""
    issues = _check(
        tmp_path,
        'VALID_FAMILY_VALUES = ["A", "B", "C", "D"]  # gate-vocab-context: governance_family\n',
    )
    assert len(issues) == 1
    assert "VALID_FAMILY_VALUES" in issues[0][1]


def test_red_safety_hm_default_reports(tmp_path: Path) -> None:
    """红：safety_level H/M 双值子集默认照报（盲区3 治本面不放宽）。"""
    issues = _check(tmp_path, 'LEVEL = ("H", "M")\n')
    assert len(issues) == 1
    assert "safety_level" in issues[0][1]


def test_blue_safety_hm_with_annotation_passes(tmp_path: Path) -> None:
    """蓝：safety_level H/M + 点名 safety_level 标注 → per-line 豁免。"""
    issues = _check(tmp_path, 'LEVEL = ("H", "M")  # gate-vocab-context: safety_level\n')
    assert issues == []


def test_collect_context_exemptions_ignores_docstring() -> None:
    """审计收集器用 tokenize 识别真注释——docstring 中的文字引用不计。"""
    source = 'x = ("H", "M")  # gate-vocab-context: safety_level\n"""docstring 提及 gate-vocab-context: 不应计入"""\n'
    hits = cvh._collect_context_exemptions(source)
    assert len(hits) == 1
    assert hits[0][0] == 1
    assert hits[0][1] == "safety_level"


def test_multi_vocab_annotation_semicolon(tmp_path: Path) -> None:
    """分号分隔多词表标注：命中任一点名词表即豁免。"""
    issues = _check(
        tmp_path,
        'LEVEL = ("H", "M")  # gate-vocab-context: governance_family;safety_level\n',
    )
    assert issues == []


@pytest.mark.parametrize("annotation", ["", "# gate-vocab-context:", "# gate-vocab-context:   "])
def test_empty_annotation_inert(tmp_path: Path, annotation: str) -> None:
    """空点名/无点名词表标注=惰性（照报），防空标注形同全豁免。"""
    issues = _check(tmp_path, f'FAMILY_PRIORITY = ["A", "B", "C", "D"]  {annotation}\n'.rstrip() + "\n")
    assert len(issues) == 1
