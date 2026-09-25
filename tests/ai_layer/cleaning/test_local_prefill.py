# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_cleaning
# [MODULE] tests.ai_layer.cleaning.test_local_prefill
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.ai_layer.cleaning.local_prefill; zephyr.ai_layer.cleaning.policy
# [CONSUMERS] pytest tests/ai_layer/cleaning/test_local_prefill.py
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 纯函数零 API 零网络零写盘（tmp_path 都不需要）；代码块只断言被切出为数据；
#              计量/分块为已知值断言（分块计量准确验收）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L3_cleaning/DESIGN.md §2.6
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红
# [TESTS] tests/ai_layer/cleaning/test_local_prefill.py
# [TTL] permanent
"""test_local_prefill - 工序①本地预洗验收（C5）：解析/元数据/分块计量/骨架/查重注入/排队。"""

from __future__ import annotations

import pytest

from zephyr.ai_layer.cleaning.local_prefill import (
    PrefillError,
    chunk_text,
    dedup_precheck,
    estimate_tokens,
    extract_blocks,
    extract_metadata,
    prefill_skeleton,
    run_prefill,
)
from zephyr.ai_layer.cleaning.policy import load_cleaning_policy


SAMPLE = """# Momentum in Trending Markets

Authors: Zhang et al.
License: mit
A momentum strategy accelerates entries in trending regimes.

```python
import evil  # fetched 代码块——数据非指令
evil.run()
```

Second prose paragraph about drawdown control.
"""


# ---------------------------------------------------------------- 块切分（E0）


def test_extract_blocks_splits_code_and_prose() -> None:
    prose, code = extract_blocks(SAMPLE)
    assert any("momentum strategy" in p for p in prose)
    assert any("drawdown" in p for p in prose)
    assert len(code) == 1 and "evil.run()" in code[0], "代码块原样切出为数据（E0）"
    assert not any("evil" in p for p in prose), "代码内容不混入散文块"


def test_extract_blocks_rejects_empty() -> None:
    with pytest.raises(PrefillError, match="empty_text"):
        extract_blocks("   \n  ")


# ---------------------------------------------------------------- 元数据


def test_extract_metadata_known_values() -> None:
    meta = extract_metadata(SAMPLE)
    assert meta["title"] == "Momentum in Trending Markets"
    assert meta["authors"] == "Zhang et al."
    assert meta["license"] == "mit"
    assert meta["year"] is None or isinstance(meta["year"], int)


# ---------------------------------------------------------------- 分块与计量


def test_chunk_text_bounds_and_overlap() -> None:
    body = "".join(str(i % 10) for i in range(250))
    chunks = chunk_text(body, max_chars=100, overlap_chars=20)
    assert all(len(c) <= 100 for c in chunks)
    assert len(chunks) >= 3
    assert chunks[1].startswith(body[80:100]), "第二块以 overlap 接续"
    assert chunks[-1].endswith(body[-5:]), "尾部不丢"
    assert chunk_text("short", max_chars=100, overlap_chars=20) == ("short",)


def test_chunk_text_param_guard() -> None:
    with pytest.raises(PrefillError, match="chunk_params_invalid"):
        chunk_text("x" * 10, max_chars=5, overlap_chars=5)
    with pytest.raises(PrefillError, match="empty_text"):
        chunk_text("", max_chars=10)


def test_estimate_tokens_known_values() -> None:
    assert estimate_tokens("") == 0
    assert estimate_tokens("abcd" * 10) == 10, "40 ASCII ≈ 10 tokens"
    assert estimate_tokens("趋势跟踪策略") == 6, "6 CJK ≈ 6 tokens"
    mixed = estimate_tokens("趋势abcd")
    assert mixed == 2 + 1, "CJK 2 + ASCII 4/4 = 3"


# ---------------------------------------------------------------- 骨架与查重


def test_skeleton_inherits_source_readonly() -> None:
    policy = load_cleaning_policy()
    card = {"source_name": "arxiv", "source_url": "https://arxiv.org/abs/2505.15155",
            "source_publisher": "arXiv", "source_year": 2025}
    skeleton = prefill_skeleton(card, {"title": "t"}, policy)
    assert skeleton["source"]["url"] == card["source_url"], "来源四件套只读继承（闸 1）"
    assert skeleton["mechanism_one_liner"] == "待填"
    assert set(skeleton["applicability"]["regime"]) == {"趋势", "震荡", "高波", "事件驱动"}


def test_dedup_precheck_injected_query() -> None:
    hits = [{"card_id": "CC-1", "hamming": 2}]
    seen: list[str] = []

    def query(text: str) -> list[dict[str, object]]:
        seen.append(text)
        return hits

    out = dedup_precheck("some text", dedup_query=query)
    assert out == tuple(hits) and seen == ["some text"]
    with pytest.raises(PrefillError, match="dedup_query_missing"):
        dedup_precheck("x", dedup_query=None)  # type: ignore[arg-type]


def test_run_prefill_local_unavailable_queues_not_api() -> None:
    policy = load_cleaning_policy()

    def query(text: str) -> list[dict[str, object]]:
        return []

    result = run_prefill({"source_url": "https://x"}, SAMPLE, policy=policy,
                         dedup_query=query, local_pool=None)
    assert result.local_mode == "queue", "本地池缺席=排队，禁升级 API"
    assert result.tokens_estimate == sum(estimate_tokens(c) for c in result.chunks)
    assert result.dedup_hits == ()
    with_pool = run_prefill({"source_url": "https://x"}, SAMPLE, policy=policy,
                            dedup_query=query, local_pool=object())
    assert with_pool.local_mode == "local"
