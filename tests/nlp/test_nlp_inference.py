# [MODULE] tests.nlp.test_nlp_inference
# [DOMAIN] D_DATA
# [TTL] permanent
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] python -m pytest tests/nlp/test_nlp_inference.py -q
"""test_nlp_inference.py — nlp_inference 单元测试（P1-E3 Phase 2）。

覆盖：
  1. parse_sentiment —— 干净JSON / markdown围栏 / think块 / 噪声 / 空串 / 垃圾 / 字段缺失
  2. sentiment_to_score —— positive/negative/neutral 映射 + 边界裁剪
  3. infer_sentiment —— 正常推理 / 缓存命中 / 缓存写入 / 推理失败降级 / chat=None / model_version 隔离
  4. infer_batch —— 顺序一致 / 混合成败

测试隔离：FakeChat 零外部依赖（不连 Ollama）；CacheLayer 用真实内存实例。
"""

from __future__ import annotations

import pytest

from zephyr.integration.local_model.cache_layer import CacheLayer
from zephyr.nlp.nlp_inference import (
    NEGATIVE,
    NEUTRAL,
    POSITIVE,
    PROMPT_VERSION,
    PROMPT_VERSION_ENV,
    PROMPT_VERSION_V3,
    SCOPE_MARKET,
    SCOPE_SECTOR,
    SCOPE_STOCK,
    SYSTEM_PROMPT,
    SYSTEM_PROMPT_V3,
    InferConfig,
    NLPInferenceError,
    SentimentResult,
    infer_batch,
    infer_sentiment,
    parse_sentiment,
    parse_sentiment_v3,
    sentiment_to_score,
)

# ============ Fake chat backends（零外部依赖）============


class _FakeChat:
    """返回固定响应的 fake 推理后端。"""

    def __init__(self, response: str = '{"sentiment": "neutral", "score": 0.5}') -> None:
        self._response = response
        self.calls: list[tuple[str, str, float | None]] = []

    def ask(self, prompt: str, *, system: str = "", temperature: float | None = None) -> str:
        self.calls.append((prompt, system, temperature))
        return self._response


class _RaisingChat:
    """ask 永远抛异常的 fake 推理后端。"""

    def ask(self, prompt: str, *, system: str = "", temperature: float | None = None) -> str:
        raise RuntimeError("ollama down")


# ============ TestParseSentiment ============


class TestParseSentiment:
    """parse_sentiment —— 各类输入格式的解析。"""

    def test_clean_json(self) -> None:
        s, sc = parse_sentiment('{"sentiment": "positive", "score": 0.9}')
        assert s == POSITIVE
        assert sc == pytest.approx(0.9)

    def test_markdown_fenced_json(self) -> None:
        raw = '```json\n{"sentiment": "negative", "score": 0.8}\n```'
        s, sc = parse_sentiment(raw)
        assert s == NEGATIVE
        assert sc == pytest.approx(0.8)

    def test_markdown_fence_no_lang(self) -> None:
        raw = '```\n{"sentiment": "neutral", "score": 0.5}\n```'
        s, sc = parse_sentiment(raw)
        assert s == NEUTRAL
        assert sc == pytest.approx(0.5)

    def test_think_block_then_json(self) -> None:
        raw = '<think>这条新闻讲降准，属于利好</think>{"sentiment": "positive", "score": 0.85}'
        s, sc = parse_sentiment(raw)
        assert s == POSITIVE
        assert sc == pytest.approx(0.85)

    def test_noise_then_json(self) -> None:
        raw = '分析结果如下：\n{"sentiment": "negative", "score": 0.7}\n以上是结论。'
        s, sc = parse_sentiment(raw)
        assert s == NEGATIVE
        assert sc == pytest.approx(0.7)

    def test_empty_string(self) -> None:
        assert parse_sentiment("") == (NEUTRAL, 0.5)

    def test_whitespace_only(self) -> None:
        assert parse_sentiment("   \n  ") == (NEUTRAL, 0.5)

    def test_pure_garbage_no_json(self) -> None:
        s, sc = parse_sentiment("我不知道怎么分类")
        assert s == NEUTRAL
        assert sc == 0.5

    def test_missing_sentiment_field(self) -> None:
        s, sc = parse_sentiment('{"score": 0.8}')
        assert s == NEUTRAL  # 缺 sentiment → 默认 neutral
        assert sc == pytest.approx(0.8)

    def test_invalid_sentiment_value(self) -> None:
        s, sc = parse_sentiment('{"sentiment": "bullish", "score": 0.8}')
        assert s == NEUTRAL  # 非法值 → neutral
        assert sc == pytest.approx(0.8)

    def test_missing_score_field(self) -> None:
        s, sc = parse_sentiment('{"sentiment": "positive"}')
        assert s == POSITIVE
        assert sc == 0.5  # 缺 score → 默认 0.5

    def test_score_out_of_range_high(self) -> None:
        s, sc = parse_sentiment('{"sentiment": "positive", "score": 1.5}')
        assert s == POSITIVE
        assert sc == 1.0  # 裁剪到 [0, 1]

    def test_score_out_of_range_negative(self) -> None:
        s, sc = parse_sentiment('{"sentiment": "negative", "score": -0.3}')
        assert s == NEGATIVE
        assert sc == 0.0  # 裁剪到 [0, 1]

    def test_non_dict_json_array(self) -> None:
        s, sc = parse_sentiment("[1, 2, 3]")
        assert s == NEUTRAL
        assert sc == 0.5

    def test_score_non_numeric(self) -> None:
        s, sc = parse_sentiment('{"sentiment": "positive", "score": "high"}')
        assert s == POSITIVE
        assert sc == 0.5  # 非数字 → 默认 0.5


# ============ TestSentimentToScore ============


class TestSentimentToScore:
    """sentiment_to_score —— 有向极性归一化。"""

    def test_positive(self) -> None:
        assert sentiment_to_score(POSITIVE, 0.8) == pytest.approx(0.8)

    def test_negative(self) -> None:
        assert sentiment_to_score(NEGATIVE, 0.8) == pytest.approx(-0.8)

    def test_neutral(self) -> None:
        assert sentiment_to_score(NEUTRAL, 0.8) == 0.0

    def test_positive_zero_score(self) -> None:
        assert sentiment_to_score(POSITIVE, 0.0) == 0.0

    def test_negative_full_score(self) -> None:
        assert sentiment_to_score(NEGATIVE, 1.0) == pytest.approx(-1.0)

    def test_score_clamped_high(self) -> None:
        assert sentiment_to_score(POSITIVE, 1.5) == pytest.approx(1.0)

    def test_score_clamped_low(self) -> None:
        assert sentiment_to_score(NEGATIVE, -0.5) == pytest.approx(0.0)

    def test_unknown_sentiment_treated_neutral(self) -> None:
        assert sentiment_to_score("bullish", 0.9) == 0.0


# ============ TestInferSentiment ============


class TestInferSentiment:
    """infer_sentiment —— 推理 + 缓存 + 降级。"""

    def test_normal_inference(self) -> None:
        chat = _FakeChat('{"sentiment": "positive", "score": 0.9}')
        r = infer_sentiment("央行降准", "央行宣布降准0.5个百分点", chat=chat)
        assert r.sentiment == POSITIVE
        assert r.score == pytest.approx(0.9)
        assert r.polarity == pytest.approx(0.9)
        assert r.cached is False
        assert r.error == ""
        assert len(chat.calls) == 1

    def test_cache_hit_skips_inference(self) -> None:
        cache = CacheLayer()
        chat = _FakeChat('{"sentiment": "positive", "score": 0.9}')
        # 第一次：miss → 推理 + 写缓存
        r1 = infer_sentiment("央行降准", "降准利好", chat=chat, cache=cache, config=InferConfig(model_version="v1"))
        assert r1.cached is False
        assert len(chat.calls) == 1
        # 第二次：同文本同模型 → hit
        r2 = infer_sentiment("央行降准", "降准利好", chat=chat, cache=cache, config=InferConfig(model_version="v1"))
        assert r2.cached is True
        assert r2.sentiment == POSITIVE
        assert len(chat.calls) == 1  # 未再次调用 ask

    def test_cache_miss_different_text(self) -> None:
        cache = CacheLayer()
        chat = _FakeChat('{"sentiment": "neutral", "score": 0.5}')
        infer_sentiment("标题A", "内容A", chat=chat, cache=cache)
        infer_sentiment("标题B", "内容B", chat=chat, cache=cache)
        assert len(chat.calls) == 2  # 不同文本 → 两次推理

    def test_model_version_isolates_cache(self) -> None:
        """不同 model_version 的缓存互不干扰（换模型不读旧结果）。"""
        cache = CacheLayer()
        chat = _FakeChat('{"sentiment": "positive", "score": 0.9}')
        infer_sentiment("央行降准", "降准", chat=chat, cache=cache, config=InferConfig(model_version="qwen3:8b"))
        # 换模型版本 → 不命中旧缓存 → 重新推理
        infer_sentiment("央行降准", "降准", chat=chat, cache=cache, config=InferConfig(model_version="sft-v1"))
        assert len(chat.calls) == 2

    def test_inference_failure_degrades_neutral(self) -> None:
        chat = _RaisingChat()
        r = infer_sentiment("标题", "内容", chat=chat)
        assert r.sentiment == NEUTRAL
        assert r.score == 0.5
        assert r.polarity == 0.0
        assert r.error != ""  # 记录了错误信息
        assert "ollama down" in r.error

    def test_chat_none_raises(self) -> None:
        with pytest.raises(NLPInferenceError, match="chat"):
            infer_sentiment("标题", chat=None)  # type: ignore[arg-type]

    def test_content_truncated(self) -> None:
        """content 超过 max_content_chars 被截断。"""
        chat = _FakeChat('{"sentiment": "neutral", "score": 0.5}')
        long_content = "x" * 500
        infer_sentiment("标题", long_content, chat=chat, config=InferConfig(max_content_chars=50))
        # prompt 中 content 应被截断到 50 字符
        prompt, _sys, _t = chat.calls[0]
        assert "x" * 50 in prompt
        assert "x" * 51 not in prompt

    def test_empty_content_handled(self) -> None:
        chat = _FakeChat('{"sentiment": "neutral", "score": 0.5}')
        r = infer_sentiment("只有标题的新闻", "", chat=chat)
        assert r.sentiment == NEUTRAL
        assert len(chat.calls) == 1

    def test_news_id_propagated(self) -> None:
        chat = _FakeChat('{"sentiment": "positive", "score": 0.8}')
        r = infer_sentiment("标题", "内容", chat=chat, news_id="nid-123")
        assert r.news_id == "nid-123"

    def test_temperature_passed_through(self) -> None:
        chat = _FakeChat('{"sentiment": "neutral", "score": 0.5}')
        infer_sentiment("标题", "内容", chat=chat, config=InferConfig(temperature=0.0))
        _prompt, _sys, temp = chat.calls[0]
        assert temp == 0.0

    def test_cache_write_then_invalidate(self) -> None:
        """缓存写入后，invalidate 后重新推理。"""
        cache = CacheLayer()
        chat = _FakeChat('{"sentiment": "positive", "score": 0.9}')
        infer_sentiment("标题", "内容", chat=chat, cache=cache)
        cache.invalidate_collection("news_sentiment")
        infer_sentiment("标题", "内容", chat=chat, cache=cache)
        assert len(chat.calls) == 2  # 失效后重新推理


# ============ TestInferBatch ============


class TestInferBatch:
    """infer_batch —— 批量推理。"""

    def test_order_and_count(self) -> None:
        chat = _FakeChat('{"sentiment": "neutral", "score": 0.5}')
        items = [
            {"news_id": "a", "title": "标题A", "content": "内容A"},
            {"news_id": "b", "title": "标题B", "content": "内容B"},
            {"news_id": "c", "title": "标题C", "content": "内容C"},
        ]
        results = infer_batch(items, chat=chat)
        assert len(results) == 3
        assert [r.news_id for r in results] == ["a", "b", "c"]
        assert all(r.sentiment == NEUTRAL for r in results)

    def test_mixed_success_failure(self) -> None:
        """某条推理失败不阻断批量——降级 neutral 继续。"""
        call_count = 0

        class _MixedChat:
            def ask(self, prompt: str, *, system: str = "", temperature: float | None = None) -> str:
                nonlocal call_count
                call_count += 1
                if call_count == 2:
                    raise RuntimeError("second item fails")
                return '{"sentiment": "positive", "score": 0.8}'

        items = [
            {"news_id": "ok1", "title": "标题1"},
            {"news_id": "fail", "title": "标题2"},
            {"news_id": "ok2", "title": "标题3"},
        ]
        results = infer_batch(items, chat=_MixedChat())
        assert len(results) == 3
        assert results[0].sentiment == POSITIVE
        assert results[1].sentiment == NEUTRAL  # 降级
        assert results[1].error != ""
        assert results[2].sentiment == POSITIVE

    def test_empty_list(self) -> None:
        chat = _FakeChat()
        assert infer_batch([], chat=chat) == []

    def test_batch_uses_cache(self) -> None:
        """批量推理中重复文本命中缓存。"""
        cache = CacheLayer()
        chat = _FakeChat('{"sentiment": "positive", "score": 0.9}')
        items = [
            {"title": "重复标题", "content": "重复内容"},
            {"title": "重复标题", "content": "重复内容"},  # 与上一条相同
        ]
        results = infer_batch(items, chat=chat, cache=cache)
        assert results[0].cached is False
        assert results[1].cached is True
        assert len(chat.calls) == 1  # 第二条命中缓存，未推理


# ============ TestPromptV3Scope（CAND-NLP-003 主体范围轴）============


class TestPromptV3Template:
    """v3 prompt 模板契约：scope 三分类指令 + JSON 输出 schema。"""

    def test_default_version_stays_v2(self) -> None:
        """默认版本不翻牌——PROMPT_VERSION 仍为 v2（v3 走灰度）。"""
        assert PROMPT_VERSION == "v2-fewshot"
        assert PROMPT_VERSION_V3 == "v3-scope"

    def test_v3_system_prompt_has_scope_contract(self) -> None:
        assert '"scope": "market|sector|stock"' in SYSTEM_PROMPT_V3
        assert "影响主体范围" in SYSTEM_PROMPT_V3
        # v2 模板不带 scope（并存不串扰）
        assert "scope" not in SYSTEM_PROMPT


class TestParseSentimentV3:
    """parse_sentiment_v3 —— scope 提取/缺失降级/解析容错。"""

    def test_clean_json_with_scope(self) -> None:
        s, sc, scope = parse_sentiment_v3('{"sentiment": "positive", "score": 0.9, "scope": "sector"}')
        assert s == POSITIVE and sc == pytest.approx(0.9) and scope == SCOPE_SECTOR

    def test_missing_scope_degrades_empty(self) -> None:
        """scope 字段缺失 → ""（聚合层视为 market，向后兼容 v2 输出）。"""
        s, sc, scope = parse_sentiment_v3('{"sentiment": "negative", "score": 0.7}')
        assert s == NEGATIVE and sc == pytest.approx(0.7) and scope == ""

    def test_invalid_scope_degrades_empty(self) -> None:
        """scope 非法取值 → ""（不进 _VALID_SCOPES 的一律降级）。"""
        _s, _sc, scope = parse_sentiment_v3('{"sentiment": "positive", "score": 0.8, "scope": "universe"}')
        assert scope == ""

    def test_markdown_fenced_with_scope(self) -> None:
        raw = '```json\n{"sentiment": "positive", "score": 0.85, "scope": "market"}\n```'
        s, sc, scope = parse_sentiment_v3(raw)
        assert s == POSITIVE and scope == SCOPE_MARKET

    def test_field_regex_fallback_with_scope(self) -> None:
        """缺开头花括号的残缺输出仍能从字段级正则抠出 scope。"""
        raw = '"sentiment": "negative", "score": 0.6, "scope": "stock"}'
        s, sc, scope = parse_sentiment_v3(raw)
        assert s == NEGATIVE and sc == pytest.approx(0.6) and scope == SCOPE_STOCK

    def test_garbage_full_degrade(self) -> None:
        assert parse_sentiment_v3("完全不是 JSON") == (NEUTRAL, 0.5, "")
        assert parse_sentiment_v3("") == (NEUTRAL, 0.5, "")

    def test_v2_parse_ignores_scope(self) -> None:
        """v2 parse_sentiment 对 v3 输出保持原契约（丢 scope 不报错）。"""
        s, sc = parse_sentiment('{"sentiment": "positive", "score": 0.9, "scope": "sector"}')
        assert s == POSITIVE and sc == pytest.approx(0.9)


class TestInferSentimentV3:
    """infer_sentiment —— v3 版本路由 / 灰度开关 / 缓存隔离。"""

    def test_explicit_v3_returns_scope(self) -> None:
        chat = _FakeChat('{"sentiment": "positive", "score": 0.8, "scope": "stock"}')
        r = infer_sentiment("某公司中标大单", "内容", chat=chat, config=InferConfig(prompt_version=PROMPT_VERSION_V3))
        assert r.scope == SCOPE_STOCK
        assert r.sentiment == POSITIVE
        # 走的是 v3 system prompt
        assert chat.calls[0][1] == SYSTEM_PROMPT_V3

    def test_default_path_stays_v2_no_scope(self) -> None:
        chat = _FakeChat('{"sentiment": "positive", "score": 0.8, "scope": "stock"}')
        r = infer_sentiment("标题", "内容", chat=chat)
        assert chat.calls[0][1] == SYSTEM_PROMPT  # v2 模板
        assert r.scope == ""  # v2 路径不产出 scope

    def test_env_var_gray_switch(self, monkeypatch) -> None:
        """ZEPHYR_NLP_PROMPT_VERSION=v3-scope 环境变量灰度启用 v3。"""
        monkeypatch.setenv(PROMPT_VERSION_ENV, PROMPT_VERSION_V3)
        chat = _FakeChat('{"sentiment": "neutral", "score": 0.5, "scope": "market"}')
        r = infer_sentiment("标题", "内容", chat=chat)
        assert chat.calls[0][1] == SYSTEM_PROMPT_V3
        assert r.scope == SCOPE_MARKET

    def test_config_overrides_env(self, monkeypatch) -> None:
        """InferConfig.prompt_version 显式指定优先于环境变量。"""
        monkeypatch.setenv(PROMPT_VERSION_ENV, PROMPT_VERSION_V3)
        chat = _FakeChat('{"sentiment": "neutral", "score": 0.5, "scope": "stock"}')
        r = infer_sentiment("标题", "内容", chat=chat, config=InferConfig(prompt_version=PROMPT_VERSION))
        assert chat.calls[0][1] == SYSTEM_PROMPT
        assert r.scope == ""

    def test_unknown_version_falls_back_v2(self) -> None:
        """未知版本号 fail-safe 回退 v2 路径。"""
        chat = _FakeChat('{"sentiment": "neutral", "score": 0.5}')
        r = infer_sentiment("标题", "内容", chat=chat, config=InferConfig(prompt_version="v9-x"))
        assert chat.calls[0][1] == SYSTEM_PROMPT
        assert r.scope == ""

    def test_cache_isolation_between_versions(self) -> None:
        """同一标题 v2/v3 缓存键隔离（版本入键，不串读）。"""
        cache = CacheLayer()
        chat = _FakeChat('{"sentiment": "positive", "score": 0.9, "scope": "sector"}')
        r1 = infer_sentiment("同一条新闻", "内容", chat=chat, cache=cache)
        r2 = infer_sentiment(
            "同一条新闻", "内容", chat=chat, cache=cache, config=InferConfig(prompt_version=PROMPT_VERSION_V3)
        )
        assert r1.cached is False and r2.cached is False
        assert len(chat.calls) == 2  # v2/v3 各自推理一次
        assert r1.scope == "" and r2.scope == SCOPE_SECTOR

    def test_v3_cache_roundtrip_keeps_scope(self) -> None:
        """v3 结果写缓存后命中读取仍带 scope。"""
        cache = CacheLayer()
        chat = _FakeChat('{"sentiment": "negative", "score": 0.7, "scope": "stock"}')
        cfg = InferConfig(prompt_version=PROMPT_VERSION_V3)
        infer_sentiment("标题", "内容", chat=chat, cache=cache, config=cfg)
        r = infer_sentiment("标题", "内容", chat=chat, cache=cache, config=cfg)
        assert r.cached is True and r.scope == SCOPE_STOCK
        assert len(chat.calls) == 1
