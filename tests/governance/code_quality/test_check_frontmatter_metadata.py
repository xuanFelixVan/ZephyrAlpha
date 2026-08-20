# [A_test] module_id: MOD-GOV_check_frontmatter_metadata | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/check_frontmatter_metadata.py | §gate-15
# [MODULE] tests.unit.governance.test_check_frontmatter_metadata
# [DOMAIN] D_GOVERNANCE
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""
单元测试：scripts/governance/d3_metadata/check_frontmatter_metadata.py（GATE-15）

测试矩阵
--------
test_ttl_valid            : 合法 ttl → 无 issues
test_ttl_missing          : 缺 ttl → issues 含 "missing required field 'ttl'"
test_ttl_invalid          : 非法 ttl → issues 含 "invalid ttl="
test_doctype_valid        : 合法 doc_type → 无 issues
test_doctype_missing_warn : 缺 doc_type, warn-only → 无 issues（WARN 输出）
test_doctype_missing_strict : 缺 doc_type, strict → issues 含 "missing required field 'doc_type'"
test_doctype_invalid_strict : 非法 doc_type, strict → issues 含 "invalid doc_type="
test_doctype_deprecated_warn : 废弃值 warn-only → 无 issues（WARN 含迁移目标）
test_generic_loader       : load_vocabulary_values("ttl_vocabulary.yaml") 回归验证
"""

from __future__ import annotations

from pathlib import Path

import pytest

# 治本：_load_deprecated_values/load_vocabulary_values 已重构为共享 util（D-D-05：禁止复制 _load_xxx）。
# 新函数 load_vocabulary_values/load_vocabulary_deprecated_map 在 _shared.yaml_utils，
# 由 check_frontmatter_metadata 模块级 re-export，故从同一模块导入。
import scripts.governance.d3_metadata.check_frontmatter_metadata as _cfm
from scripts.governance.d3_metadata.check_frontmatter_metadata import (
    _FIELD_RULES,
    _check_file,
    load_vocabulary_deprecated_map,
    load_vocabulary_values,
)

# ── fixtures ──


@pytest.fixture
def vocab_cache():
    """预加载所有字段的词表缓存。"""
    cache = {}
    for field, rule in _FIELD_RULES.items():
        cache[field] = load_vocabulary_values(rule["vocab_file"])
    return cache


@pytest.fixture
def deprecated_cache():
    """预加载废弃值缓存。"""
    cache = {}
    for field, rule in _FIELD_RULES.items():
        if "deprecated_key" in rule:
            cache[field] = load_vocabulary_deprecated_map(rule["vocab_file"], deprecated_key=rule["deprecated_key"])
    return cache


def _make_md(tmp_path: Path, frontmatter: str, body: str = "# test") -> Path:
    """创建临时 .md 文件。"""
    fpath = tmp_path / "test.md"
    fpath.write_text(f"---\n{frontmatter}\n---\n\n{body}\n", encoding="utf-8")
    return fpath


# ── ttl 测试 ──


def test_ttl_valid(tmp_path, vocab_cache, deprecated_cache):
    """合法 ttl → 无 issues。"""
    fpath = _make_md(tmp_path, "ttl: permanent\ndoc_type: policy")
    issues = _check_file(fpath, _FIELD_RULES, vocab_cache, deprecated_cache, strict_doctype=False)
    assert issues == []


def test_ttl_missing(tmp_path, vocab_cache, deprecated_cache):
    """缺 ttl → issues 含 missing required field 'ttl'。"""
    fpath = _make_md(tmp_path, "doc_type: policy")
    issues = _check_file(fpath, _FIELD_RULES, vocab_cache, deprecated_cache, strict_doctype=False)
    assert len(issues) == 1
    assert "missing required field 'ttl'" in issues[0]


def test_ttl_invalid(tmp_path, vocab_cache, deprecated_cache):
    """非法 ttl → issues 含 invalid ttl=。"""
    fpath = _make_md(tmp_path, "ttl: forever\ndoc_type: policy")
    issues = _check_file(fpath, _FIELD_RULES, vocab_cache, deprecated_cache, strict_doctype=False)
    assert len(issues) == 1
    assert "invalid ttl=" in issues[0]


# ── doc_type 测试 ──


def test_doctype_valid(tmp_path, vocab_cache, deprecated_cache):
    """合法 doc_type → 无 issues。"""
    fpath = _make_md(tmp_path, "ttl: permanent\ndoc_type: policy")
    issues = _check_file(fpath, _FIELD_RULES, vocab_cache, deprecated_cache, strict_doctype=False)
    assert issues == []


def test_doctype_missing_warn(tmp_path, vocab_cache, deprecated_cache, capsys):
    """缺 doc_type, warn-only → 无 issues（但 WARN 输出到 stdout）。"""
    fpath = _make_md(tmp_path, "ttl: permanent")
    issues = _check_file(fpath, _FIELD_RULES, vocab_cache, deprecated_cache, strict_doctype=False)
    assert issues == []  # warn-only: 不计入 issues
    captured = capsys.readouterr()
    assert "missing required field 'doc_type'" in captured.out  # WARN 输出


def test_doctype_missing_strict(tmp_path, vocab_cache, deprecated_cache):
    """缺 doc_type, strict → issues 含 missing required field 'doc_type'。"""
    fpath = _make_md(tmp_path, "ttl: permanent")
    issues = _check_file(fpath, _FIELD_RULES, vocab_cache, deprecated_cache, strict_doctype=True)
    assert len(issues) == 1
    assert "missing required field 'doc_type'" in issues[0]


def test_doctype_invalid_strict(tmp_path, vocab_cache, deprecated_cache):
    """非法 doc_type, strict → issues 含 invalid doc_type=。"""
    fpath = _make_md(tmp_path, "ttl: permanent\ndoc_type: not_a_real_type")
    issues = _check_file(fpath, _FIELD_RULES, vocab_cache, deprecated_cache, strict_doctype=True)
    assert len(issues) == 1
    assert "invalid doc_type=" in issues[0]


def test_doctype_deprecated_warn(tmp_path, vocab_cache, deprecated_cache, capsys):
    """废弃值 warn-only → 无 issues（WARN 含迁移目标提示）。"""
    # governance_standard 是废弃值，migrated_to: ["policy", "standard"]
    fpath = _make_md(tmp_path, "ttl: permanent\ndoc_type: governance_standard")
    issues = _check_file(fpath, _FIELD_RULES, vocab_cache, deprecated_cache, strict_doctype=False)
    assert issues == []  # warn-only
    captured = capsys.readouterr()
    assert "deprecated doc_type='governance_standard'" in captured.out


# ── 通用加载器回归测试 ──


def test_generic_loader_ttl_regression():
    """load_vocabulary_values("ttl_vocabulary.yaml") 返回与旧 _load_ttl_values() 相同的集合。

    旧 _load_ttl_values(): {v["value"] for v in data.get("values", [])}
    新 load_vocabulary_values(): 支持 dict（entry.get("value")）和 str 两种格式
    ttl_vocabulary.yaml 使用 dict 格式，两者结果应一致。
    """
    values = load_vocabulary_values("ttl_vocabulary.yaml")
    # ttl_vocabulary.yaml 的合法值至少包含 permanent 和 task_bound
    assert "permanent" in values
    assert "task_bound" in values
    # 确保返回的是 set
    assert isinstance(values, set)


def test_generic_loader_doctype():
    """load_vocabulary_values("doc_type_vocabulary.yaml") 返回 doc_type 合法值。"""
    values = load_vocabulary_values("doc_type_vocabulary.yaml")
    # 验证几个已知合法值
    assert "policy" in values
    assert "policy" in values
    assert "vocabulary" in values
    assert isinstance(values, set)


# ── zone-aware fail-open 测试（治本 #ARCH-TTL-FAILOPEN-001）──
# 不可能三角解法验证：temporary zone 跳过 doc_type 但保留 ttl；
#   permanent/temporary zone 无 frontmatter → HARD BLOCK


def test_no_fm_permanent_zone_blocks(tmp_path, vocab_cache, deprecated_cache, monkeypatch):
    """permanent zone .md 无 frontmatter → HARD BLOCK。"""
    monkeypatch.setattr(_cfm, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(_cfm, "_classify_file_zone", lambda rel: "permanent")
    fpath = tmp_path / "test.md"
    fpath.write_text("# just a title\n\nno frontmatter here\n", encoding="utf-8")
    issues = _check_file(fpath, _FIELD_RULES, vocab_cache, deprecated_cache, strict_doctype=False)
    assert len(issues) == 1
    assert "missing frontmatter in permanent zone" in issues[0]


def test_no_fm_temporary_zone_blocks(tmp_path, vocab_cache, deprecated_cache, monkeypatch):
    """temporary zone .md 无 frontmatter → HARD BLOCK（ttl required）。"""
    monkeypatch.setattr(_cfm, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(_cfm, "_classify_file_zone", lambda rel: "temporary")
    fpath = tmp_path / "test.md"
    fpath.write_text("# just a title\n\nno frontmatter here\n", encoding="utf-8")
    issues = _check_file(fpath, _FIELD_RULES, vocab_cache, deprecated_cache, strict_doctype=False)
    assert len(issues) == 1
    assert "missing ttl frontmatter in temporary zone" in issues[0]


def test_no_fm_neutral_zone_passes(tmp_path, vocab_cache, deprecated_cache, monkeypatch):
    """neutral zone .md 无 frontmatter → PASS（向后兼容）。"""
    monkeypatch.setattr(_cfm, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(_cfm, "_classify_file_zone", lambda rel: "neutral")
    fpath = tmp_path / "test.md"
    fpath.write_text("# just a title\n\nno frontmatter here\n", encoding="utf-8")
    issues = _check_file(fpath, _FIELD_RULES, vocab_cache, deprecated_cache, strict_doctype=False)
    assert issues == []


def test_temporary_zone_skips_doctype(tmp_path, vocab_cache, deprecated_cache, monkeypatch):
    """temporary zone .md 有 ttl 无 doc_type, strict=True → PASS（doc_type 跳过）。"""
    monkeypatch.setattr(_cfm, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(_cfm, "_classify_file_zone", lambda rel: "temporary")
    fpath = _make_md(tmp_path, "ttl: task_bound")  # 有 ttl, 无 doc_type
    issues = _check_file(fpath, _FIELD_RULES, vocab_cache, deprecated_cache, strict_doctype=True)
    assert issues == []


def test_temporary_zone_ttl_still_required(tmp_path, vocab_cache, deprecated_cache, monkeypatch):
    """temporary zone .md 有 doc_type 无 ttl → BLOCK on ttl（ttl 仍必填）。"""
    monkeypatch.setattr(_cfm, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(_cfm, "_classify_file_zone", lambda rel: "temporary")
    fpath = _make_md(tmp_path, "doc_type: policy")  # 有 doc_type, 无 ttl
    issues = _check_file(fpath, _FIELD_RULES, vocab_cache, deprecated_cache, strict_doctype=True)
    assert len(issues) == 1
    assert "missing required field 'ttl'" in issues[0]


# ── archive_zone 解耦测试（治本 #ARCH-TTL-EXEMPT-DECOUPLE）──
# 归档区（docs/_archive/）有 frontmatter 时跳过 doc_type（与 EXEMPT-ZONE-FM 解耦），
# 但 ttl 仍必填；归档区无 frontmatter → PASS


def test_archive_zone_skips_doctype(tmp_path, vocab_cache, deprecated_cache, monkeypatch):
    """archive_zone .md 有 ttl 无 doc_type, strict=True → PASS（doc_type 跳过）。"""
    monkeypatch.setattr(_cfm, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(_cfm, "_classify_file_zone", lambda rel: "archive_zone")
    fpath = _make_md(tmp_path, "ttl: permanent")  # 有 ttl, 无 doc_type（归档文件不应有 doc_type）
    issues = _check_file(fpath, _FIELD_RULES, vocab_cache, deprecated_cache, strict_doctype=True)
    assert issues == []


def test_archive_zone_ttl_still_required(tmp_path, vocab_cache, deprecated_cache, monkeypatch):
    """archive_zone .md 无 ttl → BLOCK on ttl（ttl 仍必填，仅 doc_type 跳过）。"""
    monkeypatch.setattr(_cfm, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(_cfm, "_classify_file_zone", lambda rel: "archive_zone")
    fpath = _make_md(tmp_path, "module_id: MOD-TEST")  # 有 frontmatter, 无 ttl, 无 doc_type
    issues = _check_file(fpath, _FIELD_RULES, vocab_cache, deprecated_cache, strict_doctype=True)
    assert len(issues) == 1
    assert "missing required field 'ttl'" in issues[0]


def test_archive_zone_no_fm_passes(tmp_path, vocab_cache, deprecated_cache, monkeypatch):
    """archive_zone .md 无 frontmatter → PASS（归档文件可不带 frontmatter）。"""
    monkeypatch.setattr(_cfm, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(_cfm, "_classify_file_zone", lambda rel: "archive_zone")
    fpath = tmp_path / "test.md"
    fpath.write_text("# archived doc\n\nno frontmatter\n", encoding="utf-8")
    issues = _check_file(fpath, _FIELD_RULES, vocab_cache, deprecated_cache, strict_doctype=True)
    assert issues == []
