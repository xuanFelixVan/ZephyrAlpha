# [BLUEPRINT] MOD-AU-003 | docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/15_autonomy_boundary_risk.md | §4.2-S1.3
# [MODULE] tests.autonomy_core.test_drift_semantic_reviewer
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [TESTS] 本文件（pytest -n 0 -q；嵌入模型注入 mock，禁真调模型/网络/DB）
# [TTL] permanent
"""MOD-AU-003 drift_semantic_reviewer 验收测试（15号文 §4.2 S1.3）.

验收对照：
- S1.3：日/周频批量档骨架——嵌入相似度比对（当前动作链 vs 原始任务意图）接口位注入，
  产出复核报告结构（落盘人审，status=pending_human_review）；嵌入模型 mock 可测。
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Sequence

import pytest

from zephyr.autonomy_core.drift_semantic_reviewer import (
    SemanticReviewConfig,
    SemanticReviewError,
    SemanticReviewer,
    SessionChainReview,
    cosine_similarity,
    review_sessions,
    run_batch,
)


class MockEmbedder:
    """确定性 mock 嵌入器：按文本是否含关键词映射到固定方向，禁真调模型."""

    def __init__(self, dim: int = 8) -> None:
        self._dim = dim
        self.calls: list[list[str]] = []

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        self.calls.append([str(t) for t in texts])
        vectors: list[list[float]] = []
        for text in texts:
            if "修 Bug" in text or "autonomy_core" in text:
                vec = [1.0] + [0.0] * (self._dim - 1)
            else:
                vec = [0.0, 1.0] + [0.0] * (self._dim - 2)
            vectors.append(vec)
        return vectors


def _aligned_session() -> SessionChainReview:
    return SessionChainReview(
        session_ref="sess-aligned",
        original_intent="修 Bug：autonomy_core 的某判定逻辑",
        action_summary="在 autonomy_core 内修 Bug并补测试",
    )


def _drifted_session() -> SessionChainReview:
    return SessionChainReview(
        session_ref="sess-drifted",
        original_intent="修 Bug：autonomy_core 的某判定逻辑",
        action_summary="批量重写交易策略参数并调整熔断阈值",
    )


def test_cosine_similarity_math() -> None:
    assert cosine_similarity([1.0, 0.0], [1.0, 0.0]) == pytest.approx(1.0)
    assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)
    assert cosine_similarity([0.0, 0.0], [1.0, 0.0]) == 0.0  # 零向量 fail-safe


def test_aligned_session_not_flagged() -> None:
    embedder = MockEmbedder()
    report = review_sessions([_aligned_session()], embedder)
    assert report.n_sessions == 1
    assert report.flagged == ()
    assert report.status == "pending_human_review"  # 产出人审，不自动处置


def test_drifted_session_flagged() -> None:
    embedder = MockEmbedder()
    report = review_sessions([_drifted_session()], embedder)
    assert len(report.flagged) == 1
    flag = report.flagged[0]
    assert flag.session_ref == "sess-drifted"
    assert flag.similarity < report.similarity_threshold


def test_mixed_batch_flags_only_drifted() -> None:
    embedder = MockEmbedder()
    report = review_sessions([_aligned_session(), _drifted_session()], embedder)
    assert report.n_sessions == 2
    assert [f.session_ref for f in report.flagged] == ["sess-drifted"]
    # 嵌入经注入接口批量调用，未触碰任何真实模型
    assert len(embedder.calls) >= 1


def test_report_structure_and_persistence(tmp_path: Path) -> None:
    """周频跑批产出报告：结构完整 + 落盘 JSON 人审."""
    embedder = MockEmbedder()
    config = SemanticReviewConfig(frequency="weekly")
    report, rel_path = run_batch([_aligned_session(), _drifted_session()], embedder, tmp_path, config=config)
    assert report.frequency == "weekly"
    assert report.report_id
    assert report.generated_at
    assert report.similarity_threshold == config.similarity_threshold
    payload = json.loads((tmp_path / Path(rel_path).name).read_text(encoding="utf-8"))
    assert payload["schema_version"] == "1.0"
    assert payload["status"] == "pending_human_review"
    assert payload["n_sessions"] == 2
    assert len(payload["flagged"]) == 1
    assert payload["flagged"][0]["similarity"] < payload["similarity_threshold"]


def test_empty_batch_produces_empty_report(tmp_path: Path) -> None:
    report, _ = run_batch([], MockEmbedder(), tmp_path)
    assert report.n_sessions == 0
    assert report.flagged == ()


def test_invalid_config_and_vector_mismatch_rejected() -> None:
    with pytest.raises(SemanticReviewError):
        review_sessions([_aligned_session()], MockEmbedder(), config=SemanticReviewConfig(similarity_threshold=1.5))

    class BadEmbedder:
        def embed(self, texts: Sequence[str]) -> list[list[float]]:
            return [[1.0, 2.0]] * len(texts)  # 维度不齐（需成对同维）

    class RaggedEmbedder:
        def embed(self, texts: Sequence[str]) -> list[list[float]]:
            return [[1.0] * (i + 2) for i, _ in enumerate(texts)]

    with pytest.raises(SemanticReviewError):
        review_sessions([_aligned_session()], RaggedEmbedder())
    _ = BadEmbedder  # silence unused


def test_reviewer_class_wrapper(tmp_path: Path) -> None:
    """SemanticReviewer 类封装：注入 embedder + report_dir，等价函数入口."""
    reviewer = SemanticReviewer(embedder=MockEmbedder(), report_dir=tmp_path)
    report = reviewer.review([_drifted_session()])
    assert len(report.flagged) == 1
    report2, rel = reviewer.run_batch([_aligned_session()])
    assert report2.n_sessions == 1
    assert (tmp_path / Path(rel).name).exists()


def test_math_sanity_of_threshold_direction() -> None:
    """相似度低于阈值=疑似意图偏差（阈值语义方向防回归）."""
    assert math.isclose(cosine_similarity([1.0, 1.0], [1.0, 1.0]), 1.0)
