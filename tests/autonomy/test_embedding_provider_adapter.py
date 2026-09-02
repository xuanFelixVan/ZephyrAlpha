# [BLUEPRINT] MOD-AU-003 | docs/02_enterprise_architecture/09_ai_architecture/implementation_plans/15_autonomy_boundary_risk.md | §4.2-S1.3
# [MODULE] tests.autonomy.test_embedding_provider_adapter
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [TESTS] 本文件（pytest -q；嵌入模型经 stub/fake 注入，禁真调模型/网络/GPU；落盘走 tmp_path）
# [TTL] permanent
"""S1.3 嵌入适配器 + 批量档手动 CLI 验收测试（15号文 §4.2 S1.3）.

验收对照：
- 嵌入适配器：EmbeddingRouterAdapter 把 EmbeddingRouterProtocol 桥接为
  EmbeddingProvider（批量转发、集合路由名透传、ndarray→list[list[float]] 转换、
  auto_warmup 仅一次）；fake 注入复核核可测。
- 真实适配层冒烟：真适配器类 + 离线 stub 路由端到端跑 review_sessions。
- 批量 CLI：盘中（工作日 09:30-15:00 CST）拒跑返回 3；盘后窗口跑批落盘返回 0；
  输入非法返回 2。

被测对象：src/zephyr/autonomy_core/embedding_provider_adapter.py。
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Sequence

import numpy as np
import pytest

from zephyr.autonomy_core.drift_semantic_reviewer import (
    EmbeddingProvider,
    SemanticReviewError,
    SessionChainReview,
    review_sessions,
)
from zephyr.autonomy_core.embedding_provider_adapter import (
    DEFAULT_COLLECTION,
    EmbeddingRouterAdapter,
    main,
)

CN_TZ = timezone(timedelta(hours=8))
# 2026-08-28 为周五（工作日）
WORKDAY_INTRADAY = datetime(2026, 8, 28, 10, 0, tzinfo=CN_TZ)
WORKDAY_OFFHOURS = datetime(2026, 8, 28, 16, 0, tzinfo=CN_TZ)


class FakeProvider:
    """fake 注入嵌入器：含「修 Bug」文本映射方向 e1，否则 e2（确定性，禁真调模型）."""

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        return [[1.0, 0.0] if "修 Bug" in t else [0.0, 1.0] for t in texts]


class StubRouter:
    """离线 stub EmbeddingRouterProtocol：确定性向量，记录 warmup/embed_batch 调用."""

    def __init__(self, dim: int = 4) -> None:
        self._dim = dim
        self._available = False
        self.warmup_calls = 0
        self.batch_calls: list[tuple[list[str], str]] = []

    @property
    def bge_m3_available(self) -> bool:
        return self._available

    @property
    def bge_small_available(self) -> bool:
        return False

    @property
    def bge_m3_dim(self) -> int:
        return self._dim

    @property
    def bge_small_dim(self) -> int:
        return 0

    @property
    def fallback_mode(self) -> str:
        return "none"

    @property
    def backend(self) -> str:
        return "stub"

    def warmup(self) -> None:
        self.warmup_calls += 1
        self._available = True

    def embed(self, text: str, collection_name: str) -> np.ndarray:
        return self.embed_batch([text], collection_name)[0]

    def embed_batch(self, texts: list[str], collection_name: str) -> np.ndarray:
        self.batch_calls.append((list(texts), collection_name))
        vecs = np.zeros((len(texts), self._dim), dtype=np.float32)
        for i, t in enumerate(texts):
            # 确定性方向：含「修 Bug」→ e0，否则 → e1（模拟意图对齐/偏离）
            vecs[i, 0 if "修 Bug" in t else 1 % self._dim] = 1.0
        return vecs

    def health_check(self) -> dict[str, Any]:
        return {"backend": "stub"}

    def shutdown(self) -> None:
        self._available = False


def _aligned_session() -> SessionChainReview:
    return SessionChainReview(
        session_ref="sess-aligned",
        original_intent="修 Bug：autonomy_core 的某判定逻辑",
        action_summary="在 autonomy_core 内修 Bug 并补测试",
    )


def _drifted_session() -> SessionChainReview:
    return SessionChainReview(
        session_ref="sess-drifted",
        original_intent="修 Bug：autonomy_core 的某判定逻辑",
        action_summary="批量重写交易策略参数并调整熔断阈值",
    )


class TestFakeProviderInjection:
    """fake 注入：复核核经 EmbeddingProvider 协议消费，不触真实模型."""

    def test_fake_provider_flags_drifted_session(self) -> None:
        report = review_sessions([_aligned_session(), _drifted_session()], FakeProvider())
        assert report.n_sessions == 2
        assert report.status == "pending_human_review"
        assert [f.session_ref for f in report.flagged] == ["sess-drifted"]


class TestEmbeddingRouterAdapter:
    """真实适配层：EmbeddingRouterAdapter 桥接 stub 路由（离线，无模型/网络）."""

    def test_forwards_batch_and_converts_types(self) -> None:
        router = StubRouter(dim=4)
        adapter = EmbeddingRouterAdapter(router)
        vectors = adapter.embed(["修 Bug：x", "改配置 y"])
        assert router.batch_calls == [(["修 Bug：x", "改配置 y"], DEFAULT_COLLECTION)]
        assert len(vectors) == 2
        assert all(len(v) == 4 for v in vectors)
        assert all(isinstance(x, float) for v in vectors for x in v)
        assert vectors[0][0] == 1.0  # 对齐方向 e0
        assert vectors[1][1] == 1.0  # 偏离方向 e1

    def test_collection_name_routed(self) -> None:
        router = StubRouter()
        adapter = EmbeddingRouterAdapter(router, collection_name="lessons")
        adapter.embed(["text"])
        assert router.batch_calls[0][1] == "lessons"

    def test_auto_warmup_invoked_once(self) -> None:
        router = StubRouter()
        adapter = EmbeddingRouterAdapter(router)
        assert router.warmup_calls == 0
        adapter.embed(["a"])
        adapter.embed(["b"])
        assert router.warmup_calls == 1

    def test_empty_input_short_circuit(self) -> None:
        router = StubRouter()
        adapter = EmbeddingRouterAdapter(router)
        assert adapter.embed([]) == []
        assert router.batch_calls == []
        assert router.warmup_calls == 0

    def test_blank_collection_rejected(self) -> None:
        with pytest.raises(SemanticReviewError):
            EmbeddingRouterAdapter(StubRouter(), collection_name="  ")

    def test_adapter_satisfies_provider_protocol(self) -> None:
        assert isinstance(EmbeddingRouterAdapter(StubRouter()), EmbeddingProvider)

    def test_adapter_smoke_with_review_sessions(self) -> None:
        """真实适配层冒烟：adapter + review_sessions 端到端（stub 路由离线）."""
        adapter = EmbeddingRouterAdapter(StubRouter())
        report = review_sessions([_aligned_session(), _drifted_session()], adapter)
        assert [f.session_ref for f in report.flagged] == ["sess-drifted"]


def _write_sessions_json(path: Path) -> None:
    payload = [
        {
            "session_ref": s.session_ref,
            "original_intent": s.original_intent,
            "action_summary": s.action_summary,
        }
        for s in (_aligned_session(), _drifted_session())
    ]
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


class TestBatchCli:
    """批量档手动 CLI：盘中拒跑 / 盘后跑批落盘 / 输入非法."""

    def test_intraday_refused(self, tmp_path, capsys) -> None:
        sessions_json = tmp_path / "sessions.json"
        _write_sessions_json(sessions_json)
        report_dir = tmp_path / "reports"
        rc = main(
            ["--sessions", str(sessions_json), "--report-dir", str(report_dir)],
            at=WORKDAY_INTRADAY,
            provider=FakeProvider(),
        )
        assert rc == 3
        assert "盘中禁跑" in capsys.readouterr().err
        assert not report_dir.exists() or not list(report_dir.glob("*.json"))

    def test_offhours_runs_and_writes_report(self, tmp_path, capsys) -> None:
        sessions_json = tmp_path / "sessions.json"
        _write_sessions_json(sessions_json)
        report_dir = tmp_path / "reports"
        rc = main(
            ["--sessions", str(sessions_json), "--report-dir", str(report_dir)],
            at=WORKDAY_OFFHOURS,
            provider=FakeProvider(),
        )
        assert rc == 0
        assert "S1.3" in capsys.readouterr().out
        reports = list(report_dir.glob("drift_semantic_review-*.json"))
        assert len(reports) == 1
        payload = json.loads(reports[0].read_text(encoding="utf-8"))
        assert payload["status"] == "pending_human_review"
        assert payload["n_sessions"] == 2
        assert [f["session_ref"] for f in payload["flagged"]] == ["sess-drifted"]

    def test_malformed_sessions_returns_2(self, tmp_path) -> None:
        bad = tmp_path / "bad.json"
        bad.write_text('{"not": "a list"}', encoding="utf-8")
        rc = main(
            ["--sessions", str(bad), "--report-dir", str(tmp_path / "r")],
            at=WORKDAY_OFFHOURS,
            provider=FakeProvider(),
        )
        assert rc == 2

    def test_missing_field_returns_2(self, tmp_path) -> None:
        bad = tmp_path / "missing.json"
        bad.write_text(json.dumps([{"session_ref": "s", "original_intent": "x"}]), encoding="utf-8")
        rc = main(
            ["--sessions", str(bad), "--report-dir", str(tmp_path / "r")],
            at=WORKDAY_OFFHOURS,
            provider=FakeProvider(),
        )
        assert rc == 2
