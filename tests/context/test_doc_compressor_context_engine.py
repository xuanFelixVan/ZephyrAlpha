# [A_test] module_id: MOD-GOV_doc_compressor_context_engine | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-467 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.context_engine.test_doc_compressor
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
T-V2-006 单元测试 — DocCompressor + CompressionPolicy
=======================================================
覆盖场景（验收标准 #6 ≥ 80%）：
  - CompressionPolicy frozen：Pydantic v2 frozen 不可变
  - 5 个不变量字段：min_chars / max_chars / preserve_structure /
    preserve_provenance / preserve_immutable_blocks
  - 不变量违反：对应 CompressionInvariantError（含 field / original / compressed）
  - DocCompressor 单例：instance() 返回同一对象
  - compress() 正常流程：输出长度在 [min_chars, max_chars]
  - compress() 保留 frontmatter
  - compress() 保留标题结构
  - compress() 超长截断
  - load_policy_from_yaml：YAML 存在时正确加载，缺失时返回 DEFAULT_POLICY
  - ContextBudgetTracker DocCompressor 注入接口
"""

import textwrap
import time
from pathlib import Path

import pytest

from zephyr.shared.io.doc_compressor import (
    DEFAULT_POLICY,
    CompressionInvariantError,
    CompressionPolicy,
    DocCompressor,
    _extract_headers,
    _has_frontmatter,
    load_policy_from_yaml,
)

# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def reset_singleton():
    """每个测试前后重置 DocCompressor 单例，避免测试间污染。"""
    DocCompressor.reset_instance()
    yield
    DocCompressor.reset_instance()


@pytest.fixture
def strict_policy():
    return CompressionPolicy(
        min_chars=100,
        max_chars=500,
        preserve_structure=True,
        preserve_provenance=True,
        preserve_immutable_blocks=["<!-- IMMUTABLE_START -->"],
    )


@pytest.fixture
def compressor(strict_policy):
    return DocCompressor(policy=strict_policy)


# ---------------------------------------------------------------------------
# 1. CompressionPolicy — Pydantic v2 frozen
# ---------------------------------------------------------------------------


class TestCompressionPolicy:
    def test_frozen_cannot_mutate(self):
        policy = CompressionPolicy()
        with pytest.raises(Exception):
            policy.min_chars = 50  # type: ignore[misc]

    def test_min_chars_lower_bound(self):
        with pytest.raises(Exception):
            CompressionPolicy(min_chars=50)  # < 100

    def test_max_chars_upper_bound(self):
        with pytest.raises(Exception):
            CompressionPolicy(max_chars=20000)  # > 10000

    def test_valid_default_policy(self):
        p = CompressionPolicy()
        assert p.min_chars == 200
        assert p.max_chars == 4000
        assert p.preserve_structure is True
        assert p.preserve_provenance is True
        assert p.preserve_immutable_blocks == [
            "<!-- IMMUTABLE_START -->",
            "<!-- AFFECTED_FILES_START -->",
            "<!-- CIRCUIT_BREAKER_START -->",
        ]

    def test_custom_policy_values(self):
        p = CompressionPolicy(
            min_chars=100,
            max_chars=1000,
            preserve_structure=False,
            preserve_provenance=False,
            preserve_immutable_blocks=["<!-- CUSTOM_START -->"],
        )
        assert p.min_chars == 100
        assert p.preserve_immutable_blocks == ["<!-- CUSTOM_START -->"]


# ---------------------------------------------------------------------------
# 2. CompressionInvariantError
# ---------------------------------------------------------------------------


class TestCompressionInvariantError:
    def test_error_attributes(self):
        err = CompressionInvariantError(
            field="preserve_structure",
            original="标题 '## 安装' 在原文中存在",
            compressed="标题 '## 安装' 在压缩结果中缺失",
        )
        assert err.field == "preserve_structure"
        assert "preserve_structure" in str(err)
        assert "安装" in str(err)

    def test_is_exception(self):
        with pytest.raises(CompressionInvariantError):
            raise CompressionInvariantError("min_chars", "原始", "压缩")


# ---------------------------------------------------------------------------
# 3. DocCompressor 单例
# ---------------------------------------------------------------------------


class TestDocCompressorSingleton:
    def test_instance_returns_same_object(self):
        a = DocCompressor.instance()
        b = DocCompressor.instance()
        assert a is b

    def test_reset_creates_new_instance(self):
        a = DocCompressor.instance()
        DocCompressor.reset_instance()
        b = DocCompressor.instance()
        assert a is not b

    def test_instance_uses_provided_policy(self):
        policy = CompressionPolicy(min_chars=100, max_chars=1000)
        c = DocCompressor.instance(policy=policy, reset=True)
        assert c.policy.max_chars == 1000

    def test_instance_reset_flag(self):
        a = DocCompressor.instance()
        b = DocCompressor.instance(reset=True)
        assert a is not b


# ---------------------------------------------------------------------------
# 4. compress() 正常流程
# ---------------------------------------------------------------------------


class TestCompressNormal:
    def _make_text(self, n_chars: int = 600) -> str:
        """生成指定长度的测试文本（含标题和正文）。"""
        return "## 安装说明\n\n" + ("这是一段测试正文内容。" * (n_chars // 12 + 1))[:n_chars]

    def test_compress_returns_string(self, compressor):
        text = self._make_text(600)
        result = compressor.compress(text)
        assert isinstance(result, str)

    def test_compress_respects_max_chars(self):
        c = DocCompressor(policy=CompressionPolicy(min_chars=100, max_chars=300))
        text = "## 标题\n\n" + "A" * 500
        result = c.compress(text)
        assert len(result) <= 300 + 20  # 含截断后缀

    def test_compress_empty_text_returns_empty(self, compressor):
        assert compressor.compress("") == ""

    def test_compress_short_text_unchanged(self):
        c = DocCompressor(policy=CompressionPolicy(min_chars=100, max_chars=1000))
        text = "## 标题\n\n简短内容。\n"
        result = c.compress(text)
        assert "标题" in result


# ---------------------------------------------------------------------------
# 5. 不变量 1：preserve_structure
# ---------------------------------------------------------------------------


class TestInvariantPreserveStructure:
    def test_headers_preserved_in_output(self):
        c = DocCompressor(policy=CompressionPolicy(min_chars=100, max_chars=2000))
        text = "## 安装说明\n\n" + "正文内容。" * 30 + "\n\n## 配置\n\n配置内容。" * 20
        result = c.compress(text)
        assert "## 安装说明" in result
        assert "## 配置" in result

    def test_missing_header_in_output_raises_invariant_error(self, monkeypatch):
        """模拟压缩后标题被删除 → 触发 CompressionInvariantError。"""
        policy = CompressionPolicy(min_chars=100, max_chars=10000, preserve_structure=True)
        c = DocCompressor(policy=policy)
        # 原文须 >= min_chars=100 以触发不变量检查
        original = "## 重要标题\n\n" + "正文内容。" * 20

        def _bad_compress(text, pol):
            return "标题被删除了，这是压缩结果。" * 10  # 返回内容 > min_chars 但无标题

        monkeypatch.setattr(c, "_rule_based_compress", lambda text, pol: _bad_compress(text, pol))

        with pytest.raises(CompressionInvariantError) as exc_info:
            c.compress(original)
        assert exc_info.value.field == "preserve_structure"
        assert "重要标题" in exc_info.value.original

    def test_preserve_structure_false_skips_check(self, monkeypatch):
        policy = CompressionPolicy(min_chars=100, max_chars=10000, preserve_structure=False)
        c = DocCompressor(policy=policy)
        # 原文较长确保不触发 min_chars 不变量
        original = "## 标题\n\n" + "正文内容正文内容正文内容。" * 20
        result_text = "标题被删除了。" * 20  # 确保 >= min_chars=100
        monkeypatch.setattr(c, "_rule_based_compress", lambda text, pol: result_text)
        result = c.compress(original)
        assert result == result_text


# ---------------------------------------------------------------------------
# 6. 不变量 2：preserve_provenance
# ---------------------------------------------------------------------------


class TestInvariantPreserveProvenance:
    def test_frontmatter_preserved(self):
        c = DocCompressor(policy=CompressionPolicy(min_chars=100, max_chars=2000))
        text = (
            textwrap.dedent(
                """\
            ---
            title: 测试文档
            last_updated: 2026-04-27
            ---

            ## 安装

            """
            )
            + "正文内容。" * 30
        )
        result = c.compress(text)
        assert _has_frontmatter(result)
        assert "title: 测试文档" in result

    def test_missing_frontmatter_in_output_raises(self, monkeypatch):
        # preserve_structure=False 确保标题不影响本测试的触发路径
        policy = CompressionPolicy(
            min_chars=100,
            max_chars=10000,
            preserve_provenance=True,
            preserve_structure=False,
        )
        c = DocCompressor(policy=policy)
        original = "---\ntitle: 测试\n---\n\n" + "正文内容。" * 20

        def _strip_fm(text, pol):
            return "正文只保留了这些。" * 15  # > min_chars=100 但无 frontmatter

        monkeypatch.setattr(c, "_rule_based_compress", _strip_fm)
        with pytest.raises(CompressionInvariantError) as exc_info:
            c.compress(original)
        assert exc_info.value.field == "preserve_provenance"

    def test_preserve_provenance_false_skips(self, monkeypatch):
        policy = CompressionPolicy(
            min_chars=100,
            max_chars=10000,
            preserve_provenance=False,
            preserve_structure=False,
        )
        c = DocCompressor(policy=policy)
        original = "---\ntitle: 测试\n---\n\n" + "正文内容。" * 20
        result_text = "无 FM 内容。" * 20  # >= min_chars
        monkeypatch.setattr(c, "_rule_based_compress", lambda text, pol: result_text)
        result = c.compress(original)
        assert result == result_text


# ---------------------------------------------------------------------------
# 7. 不变量 3：preserve_immutable_blocks
# ---------------------------------------------------------------------------


class TestInvariantPreserveImmutableBlocks:
    def test_immutable_marker_preserved(self):
        policy = CompressionPolicy(
            min_chars=100,
            max_chars=3000,
            preserve_immutable_blocks=["<!-- IMMUTABLE_START -->"],
        )
        c = DocCompressor(policy=policy)
        text = "## 标题\n\n<!-- IMMUTABLE_START -->不可压缩内容<!-- IMMUTABLE_END -->\n\n" + "可压缩正文。" * 20
        result = c.compress(text)
        assert "<!-- IMMUTABLE_START -->" in result

    def test_missing_immutable_marker_raises(self, monkeypatch):
        # preserve_structure=False 确保标题检查不干扰本测试
        policy = CompressionPolicy(
            min_chars=100,
            max_chars=10000,
            preserve_structure=False,
            preserve_immutable_blocks=["<!-- IMMUTABLE_START -->"],
        )
        c = DocCompressor(policy=policy)
        original = "<!-- IMMUTABLE_START -->内容<!-- IMMUTABLE_END -->\n" + "正文。" * 30
        bad_result = "标记被删除了。" * 20  # > min_chars=100，但无标记
        monkeypatch.setattr(c, "_rule_based_compress", lambda text, pol: bad_result)
        with pytest.raises(CompressionInvariantError) as exc_info:
            c.compress(original)
        assert exc_info.value.field == "preserve_immutable_blocks"


# ---------------------------------------------------------------------------
# 8. 不变量 4：min_chars
# ---------------------------------------------------------------------------


class TestInvariantMinChars:
    def test_min_chars_violation_raises(self, monkeypatch):
        # preserve_structure=False 确保标题检查不干扰本测试
        policy = CompressionPolicy(min_chars=200, max_chars=5000, preserve_structure=False)
        c = DocCompressor(policy=policy)
        original = "正文内容正文内容。" * 50  # 原文 >> 200 chars，无标题
        monkeypatch.setattr(c, "_rule_based_compress", lambda text, pol: "太短了")
        with pytest.raises(CompressionInvariantError) as exc_info:
            c.compress(original)
        assert exc_info.value.field == "min_chars"

    def test_short_original_no_min_chars_error(self):
        """原文本身就短于 min_chars，不触发 min_chars 不变量。"""
        policy = CompressionPolicy(min_chars=200, max_chars=5000)
        c = DocCompressor(policy=policy)
        short_text = "## 标题\n\n短文本。\n"
        result = c.compress(short_text)
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# 9. load_policy_from_yaml
# ---------------------------------------------------------------------------


class TestLoadPolicyFromYaml:
    @pytest.mark.filterwarnings("ignore::UserWarning")
    def test_returns_default_when_file_missing(self, tmp_path: Path):
        result = load_policy_from_yaml(tmp_path / "nonexistent.yaml")
        assert result == DEFAULT_POLICY

    def test_loads_valid_yaml(self, tmp_path: Path):
        policy_file = tmp_path / "policy.yaml"
        policy_file.write_text(
            "version: '1.0.0'\npolicy:\n  min_chars: 150\n  max_chars: 3000\n",
            encoding="utf-8",
            newline="\n",
        )
        result = load_policy_from_yaml(policy_file)
        assert result.min_chars == 150
        assert result.max_chars == 3000

    @pytest.mark.filterwarnings("ignore::UserWarning")
    def test_returns_default_on_invalid_yaml(self, tmp_path: Path):
        policy_file = tmp_path / "bad.yaml"
        policy_file.write_text("policy:\n  min_chars: abc\n", encoding="utf-8", newline="\n")
        result = load_policy_from_yaml(policy_file)
        assert result == DEFAULT_POLICY


# ---------------------------------------------------------------------------
# 10. ContextBudgetTracker DocCompressor 注入接口
# ---------------------------------------------------------------------------


class TestBudgetTrackerDocCompressorIntegration:
    def _make_tracker(self):
        from unittest.mock import MagicMock

        from zephyr.autonomy_core.context.context_budget_tracker import (
            ContextBudgetTracker,
        )

        observer = MagicMock()
        return ContextBudgetTracker(observer, session_limit=100)

    def test_register_and_get_compressor(self):
        tracker = self._make_tracker()
        compressor = DocCompressor.instance()
        tracker.register_doc_compressor(compressor)
        assert tracker.get_doc_compressor() is compressor

    def test_get_compressor_returns_none_before_register(self):
        tracker = self._make_tracker()
        assert tracker.get_doc_compressor() is None

    def test_compress_session_context_returns_none_when_no_compressor(self):
        tracker = self._make_tracker()
        result = tracker.compress_session_context("some text")
        assert result is None

    def test_compress_session_context_calls_compressor(self):
        tracker = self._make_tracker()
        policy = CompressionPolicy(min_chars=100, max_chars=2000)
        compressor = DocCompressor.instance(policy=policy, reset=True)
        tracker.register_doc_compressor(compressor)
        text = "## 标题\n\n" + "正文内容。" * 30
        result = tracker.compress_session_context(text)
        assert result is not None
        assert isinstance(result, str)

    def test_l2_throttle_event_includes_compression_suggested(self):
        from unittest.mock import MagicMock

        from zephyr.autonomy_core.context.context_budget_tracker import (
            ContextBudgetLevel,
            ContextBudgetTracker,
        )

        captured_payloads = []
        observer = MagicMock()
        observer.emit.side_effect = lambda et, payload: captured_payloads.append(payload)

        tracker = ContextBudgetTracker(
            observer,
            session_limit=100,
            thresholds={
                ContextBudgetLevel.L1_WARNING: 0.80,
                ContextBudgetLevel.L2_THROTTLE: 0.85,
                ContextBudgetLevel.L3_HARD_STOP: 0.95,
            },
        )
        # 向 session 直接写入超过 L2 阈值的 token 数
        tracker._sessions["s1"] = {
            "token_count": 90,  # 90% > L2(85%)
            "limit": 100,
            "triggered_levels": set(),
            "created_at": time.time(),
        }
        tracker.evaluate_budget("s1")

        l2_payloads = [p for p in captured_payloads if p.get("budget_level") == ContextBudgetLevel.L2_THROTTLE.value]
        assert len(l2_payloads) == 1
        assert l2_payloads[0]["compression_suggested"] is True


# ---------------------------------------------------------------------------
# 11. 工具函数
# ---------------------------------------------------------------------------


class TestHelperFunctions:
    def test_extract_headers_empty(self):
        assert _extract_headers("") == []

    def test_extract_headers_finds_all_levels(self):
        text = "# H1\n## H2\n### H3\n正文内容。\n"
        headers = _extract_headers(text)
        assert "# H1" in headers
        assert "## H2" in headers
        assert "### H3" in headers

    def test_extract_headers_skips_non_headers(self):
        text = "正文行\n#不是标题（无空格）\n## 是标题\n"
        headers = _extract_headers(text)
        assert "## 是标题" in headers
        assert "正文行" not in headers

    def test_has_frontmatter_true(self):
        assert _has_frontmatter("---\ntitle: test\n---\n内容\n") is True

    def test_has_frontmatter_false(self):
        assert _has_frontmatter("## 标题\n内容\n") is False
        assert _has_frontmatter("") is False
