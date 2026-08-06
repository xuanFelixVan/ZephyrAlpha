# [BLUEPRINT] MOD-CLONE_GUARD | docs/03_modules/_cross_layer/clone_guard/blueprint.md | §4.3
# [MODULE] tests.clone_guard.test_relate_adapter
# [DOMAIN] D_GOV_CODE_QUALITY
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] tests/clone_guard/test_relate_adapter.py
# [A_test] module_id: MOD-CLONE_GUARD | layer=test | stability=volatile | safety=L | ai_modifiable
# [TTL] permanent
"""RelateAdapter 单元测试——Path B (datasketch MinHash LSH) 进程内实现。

测试策略（验证后集成纪律）：
  - 用真实 datasketch 库（非 mock subprocess）验证实际 MinHash LSH 行为
  - 用 fixtures/relate_corpus/ 语料 fixture（near_dup_a/b + different）验证 Type-2 克隆检测
  - 降级路径 mock _check_datasketch（datasketch 未装场景）
  - 关系映射 fixture: fixtures/relate_sample.json（真实适配器输出样本）
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from zephyr.clone_guard.config import CloneGuardConfig
from zephyr.clone_guard.engines.relate_adapter import RelateAdapter, _check_datasketch

# datasketch 可用性——决定测试是否跳过
_HAS_DATASKETCH = _check_datasketch()
_skip_no_datasketch = pytest.mark.skipif(
    not _HAS_DATASKETCH, reason="datasketch 未安装——relate Path B 降级路径已由 mock 测试覆盖"
)

# 语料 fixture 目录
_CORPUS_DIR = Path(__file__).parent / "fixtures" / "relate_corpus"


@pytest.fixture
def corpus_repo(tmp_path: Path) -> Path:
    """提供 relate_corpus 语料的临时副本（避免污染 fixture 原文件）。"""
    import shutil

    dst = tmp_path / "corpus"
    shutil.copytree(_CORPUS_DIR, dst)
    return dst


@pytest.fixture
def enabled_config() -> CloneGuardConfig:
    """relate_enabled=True 的配置。"""
    return CloneGuardConfig(relate_enabled=True)


# ======================================================================
# health_check
# ======================================================================


class TestRelateHealthCheck:
    """health_check 测试。"""

    @_skip_no_datasketch
    def test_datasketch_available_returns_true(self, tmp_path: Path):
        """datasketch 已安装时 health_check 返回 True。"""
        adapter = RelateAdapter(tmp_path, CloneGuardConfig(relate_enabled=True))
        assert adapter.health_check() is True

    def test_datasketch_missing_returns_false(self, tmp_path: Path):
        """datasketch 未安装时 health_check 返回 False。"""
        adapter = RelateAdapter(tmp_path, CloneGuardConfig(relate_enabled=True))
        with patch("zephyr.clone_guard.engines.relate_adapter._check_datasketch", return_value=False):
            assert adapter.health_check() is False


# ======================================================================
# index
# ======================================================================


@_skip_no_datasketch
class TestRelateIndex:
    """index 测试——显式构建 MinHash LSH 索引。"""

    def test_index_returns_count(self, corpus_repo: Path, enabled_config: CloneGuardConfig):
        """index 返回成功索引的文件数。"""
        adapter = RelateAdapter(corpus_repo, enabled_config)
        count = adapter.index(["near_dup_a.py", "different.py"])
        assert count == 2
        assert adapter._indexed is True
        assert len(adapter._sketches) == 2

    def test_index_empty_files_skipped(self, corpus_repo: Path, enabled_config: CloneGuardConfig):
        """空文件（无 token）被跳过，不计入索引数。"""
        (corpus_repo / "empty.py").write_text("# only a comment\n\n", encoding="utf-8")
        adapter = RelateAdapter(corpus_repo, enabled_config)
        count = adapter.index(["near_dup_a.py", "empty.py"])
        assert count == 1  # empty.py 被跳过

    def test_index_nonexistent_file_skipped(self, corpus_repo: Path, enabled_config: CloneGuardConfig):
        """不存在的文件被跳过。"""
        adapter = RelateAdapter(corpus_repo, enabled_config)
        count = adapter.index(["near_dup_a.py", "does_not_exist.py"])
        assert count == 1

    def test_index_duplicate_key_skipped(self, corpus_repo: Path, enabled_config: CloneGuardConfig):
        """同一文件二次索引时跳过重复键（不抛异常）。"""
        adapter = RelateAdapter(corpus_repo, enabled_config)
        adapter.index(["near_dup_a.py"])
        # 二次 index 重建——不抛异常
        count = adapter.index(["near_dup_a.py", "near_dup_a.py"])
        assert count == 1  # 第二个 near_dup_a 被跳过（重复键）

    def test_index_datasketch_missing_returns_zero(self, corpus_repo: Path, enabled_config: CloneGuardConfig):
        """datasketch 未装时 index 返回 0。"""
        adapter = RelateAdapter(corpus_repo, enabled_config)
        with patch("zephyr.clone_guard.engines.relate_adapter._check_datasketch", return_value=False):
            assert adapter.index(["near_dup_a.py"]) == 0


# ======================================================================
# detect
# ======================================================================


@_skip_no_datasketch
class TestRelateDetect:
    """detect 测试——覆盖降级路径和正常检测路径。"""

    def test_empty_files(self, corpus_repo: Path, enabled_config: CloneGuardConfig):
        """空文件列表直接返回（不调用索引）。"""
        adapter = RelateAdapter(corpus_repo, enabled_config)
        findings, degraded = adapter.detect([])
        assert findings == []
        assert degraded is False

    def test_disabled_in_config(self, corpus_repo: Path):
        """relate_enabled=False 时降级。"""
        adapter = RelateAdapter(corpus_repo, CloneGuardConfig(relate_enabled=False))
        findings, degraded = adapter.detect(["near_dup_b.py"])
        assert findings == []
        assert degraded is True

    def test_datasketch_missing_degraded(self, corpus_repo: Path, enabled_config: CloneGuardConfig):
        """datasketch 未安装时降级。"""
        adapter = RelateAdapter(corpus_repo, enabled_config)
        with patch("zephyr.clone_guard.engines.relate_adapter._check_datasketch", return_value=False):
            findings, degraded = adapter.detect(["near_dup_b.py"])
        assert findings == []
        assert degraded is True

    def test_empty_corpus_no_match(self, tmp_path: Path, enabled_config: CloneGuardConfig):
        """语料为空时返回空（非故障 degraded=False）。"""
        adapter = RelateAdapter(tmp_path, enabled_config)
        # 无显式 index + 空目录 → _build_corpus_index 找不到 .py 文件
        findings, degraded = adapter.detect(["nonexistent.py"])
        assert findings == []
        assert degraded is False

    def test_near_dup_type2_detected(self, corpus_repo: Path, enabled_config: CloneGuardConfig):
        """Type-2 克隆（变量重命名）经标识符归一化后被检测到。"""
        adapter = RelateAdapter(corpus_repo, enabled_config)
        adapter.index(["near_dup_a.py", "different.py"])
        findings, degraded = adapter.detect(["near_dup_b.py"])
        assert degraded is False
        assert len(findings) == 1
        f = findings[0]
        assert f.source_file == "near_dup_b.py"
        assert f.existing_file == "near_dup_a.py"
        assert f.clone_type == "T2"
        assert f.similarity >= 0.7  # 标识符归一化后 Type-2 sim≈1.0
        assert f.severity == "review"

    def test_different_file_no_match(self, corpus_repo: Path, enabled_config: CloneGuardConfig):
        """无关文件不产生 finding。"""
        adapter = RelateAdapter(corpus_repo, enabled_config)
        adapter.index(["near_dup_a.py", "near_dup_b.py"])
        findings, _ = adapter.detect(["different.py"])
        assert findings == []

    def test_self_match_skipped(self, corpus_repo: Path, enabled_config: CloneGuardConfig):
        """输入文件在语料中时跳过自匹配。"""
        adapter = RelateAdapter(corpus_repo, enabled_config)
        adapter.index(["near_dup_a.py", "near_dup_b.py"])
        # near_dup_a 在语料中——detect 不应返回自匹配
        findings, _ = adapter.detect(["near_dup_a.py"])
        # near_dup_a 与 near_dup_b 是 Type-2 克隆 → 应匹配 b 但不匹配自己
        matches = [f for f in findings if f.existing_file == "near_dup_a.py"]
        assert len(matches) == 0  # 无自匹配
        matches_b = [f for f in findings if f.existing_file == "near_dup_b.py"]
        assert len(matches_b) == 1  # 匹配 near_dup_b

    def test_severity_never_extract(self, corpus_repo: Path, enabled_config: CloneGuardConfig):
        """sim=1.0 时 severity 仍为 review（预筛器永不 extract）。"""
        adapter = RelateAdapter(corpus_repo, enabled_config)
        adapter.index(["near_dup_a.py"])
        findings, _ = adapter.detect(["near_dup_b.py"])
        assert len(findings) == 1
        assert findings[0].similarity == 1.0
        assert findings[0].severity == "review"  # 永不 extract

    def test_finding_id_format(self, corpus_repo: Path, enabled_config: CloneGuardConfig):
        """finding_id 格式为 RL-{idx}-{source}-{existing}。"""
        adapter = RelateAdapter(corpus_repo, enabled_config)
        adapter.index(["near_dup_a.py"])
        findings, _ = adapter.detect(["near_dup_b.py"])
        assert findings[0].finding_id == "RL-0-near_dup_b.py-near_dup_a.py"

    def test_absolute_path_normalized(self, corpus_repo: Path, enabled_config: CloneGuardConfig):
        """绝对路径转为相对仓库根目录。"""
        adapter = RelateAdapter(corpus_repo, enabled_config)
        adapter.index(["near_dup_a.py"])
        abs_b = str(corpus_repo / "near_dup_b.py")
        findings, _ = adapter.detect([abs_b])
        assert len(findings) == 1
        assert findings[0].source_file == "near_dup_b.py"
        assert findings[0].existing_file == "near_dup_a.py"


# ======================================================================
# search
# ======================================================================


@_skip_no_datasketch
class TestRelateSearch:
    """search 测试——L0 按语义搜已有函数。"""

    def test_disabled_returns_empty(self, corpus_repo: Path):
        """relate_enabled=False 时返回空。"""
        adapter = RelateAdapter(corpus_repo, CloneGuardConfig(relate_enabled=False))
        assert adapter.search("def calc") == []

    def test_datasketch_missing_returns_empty(self, corpus_repo: Path, enabled_config: CloneGuardConfig):
        """datasketch 未安装时返回空。"""
        adapter = RelateAdapter(corpus_repo, enabled_config)
        with patch("zephyr.clone_guard.engines.relate_adapter._check_datasketch", return_value=False):
            assert adapter.search("def calc") == []

    def test_empty_query_returns_empty(self, corpus_repo: Path, enabled_config: CloneGuardConfig):
        """空查询返回空。"""
        adapter = RelateAdapter(corpus_repo, enabled_config)
        adapter.index(["near_dup_a.py"])
        assert adapter.search("") == []
        assert adapter.search("   ") == []

    def test_search_returns_results(self, corpus_repo: Path, enabled_config: CloneGuardConfig):
        """search 返回按相似度降序的结果。"""
        adapter = RelateAdapter(corpus_repo, enabled_config)
        adapter.index(["near_dup_a.py", "different.py"])
        results = adapter.search("def calculate_total(price, tax): subtotal = price * tax return subtotal")
        assert len(results) >= 1
        # near_dup_a 应在结果中（与查询结构相似）
        files = [r.existing_file for r in results]
        assert "near_dup_a.py" in files
        # 结果按相似度降序
        sims = [r.similarity for r in results]
        assert sims == sorted(sims, reverse=True)

    def test_search_severity_always_acknowledged(self, corpus_repo: Path, enabled_config: CloneGuardConfig):
        """search 结果 severity 始终为 acknowledged（预筛不阻断）。"""
        adapter = RelateAdapter(corpus_repo, enabled_config)
        adapter.index(["near_dup_a.py"])
        results = adapter.search("def calculate_total(price, tax): subtotal = price * tax")
        for r in results:
            assert r.severity == "acknowledged"

    def test_search_top_k_limit(self, corpus_repo: Path, enabled_config: CloneGuardConfig):
        """top_k 限制返回数量。"""
        adapter = RelateAdapter(corpus_repo, enabled_config)
        adapter.index(["near_dup_a.py", "different.py"])
        results = adapter.search("def calculate_total", top_k=1)
        assert len(results) <= 1


# ======================================================================
# 归一化（_normalize_and_shingle）
# ======================================================================


@_skip_no_datasketch
class TestRelateNormalization:
    """_normalize_and_shingle 测试——标识符归一化 + shingling。"""

    def test_docstring_stripped(self, corpus_repo: Path, enabled_config: CloneGuardConfig):
        """三引号文档串被去除。"""
        adapter = RelateAdapter(corpus_repo, enabled_config)
        text = '"""docstring here"""\ndef foo():\n    return 1\n'
        shingles = adapter._normalize_and_shingle(text)
        joined = " ".join(shingles)
        assert "docstring" not in joined
        assert "here" not in joined

    def test_string_literal_stripped(self, corpus_repo: Path, enabled_config: CloneGuardConfig):
        """字符串字面量被替换为 S。"""
        adapter = RelateAdapter(corpus_repo, enabled_config)
        text = 'x = "hello world"\n'
        shingles = adapter._normalize_and_shingle(text)
        joined = " ".join(shingles)
        assert "hello" not in joined
        assert "world" not in joined

    def test_comment_stripped(self, corpus_repo: Path, enabled_config: CloneGuardConfig):
        """全行注释被去除。"""
        adapter = RelateAdapter(corpus_repo, enabled_config)
        text = "# this is a comment\ndef foo():\n    return 1\n"
        shingles = adapter._normalize_and_shingle(text)
        joined = " ".join(shingles)
        assert "comment" not in joined
        assert "this" not in joined

    def test_identifier_normalized(self, corpus_repo: Path, enabled_config: CloneGuardConfig):
        """非关键字标识符归一化为 ID。"""
        adapter = RelateAdapter(corpus_repo, enabled_config)
        text = "def my_function(var1, var2):\n    return var1 + var2\n"
        shingles = adapter._normalize_and_shingle(text)
        joined = " ".join(shingles)
        assert "my_function" not in joined
        assert "var1" not in joined
        assert "var2" not in joined
        assert "def" in joined
        assert "return" in joined

    def test_keywords_preserved(self, corpus_repo: Path, enabled_config: CloneGuardConfig):
        """Python 关键字保留（不归一化为 ID）。"""
        adapter = RelateAdapter(corpus_repo, enabled_config)
        text = "def foo():\n    if True:\n        return None\n"
        shingles = adapter._normalize_and_shingle(text)
        joined = " ".join(shingles)
        assert "def" in joined
        assert "if" in joined
        assert "return" in joined

    def test_numbers_normalized(self, corpus_repo: Path, enabled_config: CloneGuardConfig):
        """数字归一化为 N。"""
        adapter = RelateAdapter(corpus_repo, enabled_config)
        text = "x = 42\ny = 3.14\n"
        shingles = adapter._normalize_and_shingle(text)
        joined = " ".join(shingles)
        assert "42" not in joined
        assert "3" not in joined  # 3.14 → N . N

    def test_short_text_single_shingle(self, corpus_repo: Path, enabled_config: CloneGuardConfig):
        """token 不足 k 时整体作为一个 shingle。"""
        adapter = RelateAdapter(corpus_repo, CloneGuardConfig(relate_enabled=True, relate_shingle_size=10))
        text = "def foo():\n    pass\n"
        shingles = adapter._normalize_and_shingle(text)
        assert len(shingles) == 1  # 4 tokens < k=10 → 1 shingle

    def test_empty_text_returns_empty(self, corpus_repo: Path, enabled_config: CloneGuardConfig):
        """空文本/纯注释返回空集合。"""
        adapter = RelateAdapter(corpus_repo, enabled_config)
        assert adapter._normalize_and_shingle("") == set()
        assert adapter._normalize_and_shingle("# only comment\n") == set()
        assert adapter._normalize_and_shingle("\n\n\n") == set()


# ======================================================================
# 语料惰性构建（_build_corpus_index）
# ======================================================================


@_skip_no_datasketch
class TestRelateCorpusBuild:
    """_build_corpus_index 测试——惰性构建 + ignore_paths。"""

    def test_lazy_build_from_repo(self, tmp_path: Path, enabled_config: CloneGuardConfig):
        """detect 触发惰性构建——扫描仓库 .py 文件。"""
        (tmp_path / "a.py").write_text("def foo():\n    return 1\n", encoding="utf-8")
        (tmp_path / "b.py").write_text("def foo():\n    return 1\n", encoding="utf-8")
        adapter = RelateAdapter(tmp_path, enabled_config)
        findings, degraded = adapter.detect(["b.py"])
        assert degraded is False
        assert len(findings) == 1
        assert findings[0].existing_file == "a.py"

    def test_lazy_build_excludes_input_files(self, tmp_path: Path, enabled_config: CloneGuardConfig):
        """惰性构建排除 detect 输入文件（避免自匹配）。"""
        (tmp_path / "a.py").write_text("def foo():\n    return 1\n", encoding="utf-8")
        adapter = RelateAdapter(tmp_path, enabled_config)
        findings, _ = adapter.detect(["a.py"])
        assert findings == []  # a.py 被排除出语料 → 无匹配

    def test_lazy_build_respects_ignore_paths(self, tmp_path: Path, enabled_config: CloneGuardConfig):
        """惰性构建尊重 ignore_paths（tests/ 等被排除）。"""
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "target.py").write_text("def foo():\n    return 1\n", encoding="utf-8")
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "clone.py").write_text("def foo():\n    return 1\n", encoding="utf-8")
        adapter = RelateAdapter(tmp_path, enabled_config)
        findings, _ = adapter.detect(["src/target.py"])
        assert findings == []  # tests/ 被忽略 → clone.py 不在语料中 → 无匹配

    def test_lazy_build_skips_pycache(self, tmp_path: Path, enabled_config: CloneGuardConfig):
        """惰性构建跳过 __pycache__。"""
        (tmp_path / "a.py").write_text("def foo():\n    return 1\n", encoding="utf-8")
        (tmp_path / "__pycache__").mkdir()
        (tmp_path / "__pycache__" / "a.cpython-312.pyc").write_text("garbage", encoding="utf-8")
        adapter = RelateAdapter(tmp_path, enabled_config)
        findings, degraded = adapter.detect(["a.py"])
        assert degraded is False
