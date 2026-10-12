# [A_test] module_id: MOD-GOV_test_strategy_fingerprint | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.clone_guard.test_strategy_fingerprint
# [TESTS] src/zephyr/clone_guard/strategy_fingerprint.py
# [TTL] task_bound
"""90 号 Phase2 项（#20 工程细节 B-010）：退役策略指纹库 DTW 维 toy 断言。

裁定真源：90_methodology_open_questions.md §20（v2.0.0）——
  三维指纹：AST 哈希（精确复制，Tier1）+ CodeSAGE 语义嵌入（Tier2）+
  DTW PnL 形态（Tier3，Phase 2 缺口）；DTW 管形状、Pearson 管方向，
  两者均超阈值才算相似（DTW 优于 Pearson：允许时间轴非线性对齐）。
"""

from __future__ import annotations

import numpy as np
import pytest

from zephyr.clone_guard.strategy_fingerprint import (
    StrategyFingerprint,
    StrategyFingerprintStore,
    dtw_distance,
)


class TestDtwDistance:
    def test_identical_is_zero(self):
        assert dtw_distance([1.0, 2.0, 3.0], [1.0, 2.0, 3.0]) == pytest.approx(0.0)

    def test_constant_offset(self):
        """[1,2,3] vs [2,3,4]：最优对齐 (1,1)(2,1)(3,2)(3,3) 代价 1+0+0+1=2。"""
        assert dtw_distance([1.0, 2.0, 3.0], [2.0, 3.0, 4.0]) == pytest.approx(2.0)

    def test_nonlinear_time_alignment(self):
        """DTW 核心性质：相位偏移序列距离可为 0（Pearson/欧氏不具备）。"""
        assert dtw_distance([0.0, 1.0, 2.0], [0.0, 1.0, 2.0, 2.0]) == pytest.approx(0.0)

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            dtw_distance([], [1.0])


class TestFingerprintStore:
    def _store(self) -> StrategyFingerprintStore:
        return StrategyFingerprintStore(dtw_max=1.0, pearson_min=0.9)

    def test_add_and_match_identical_pnl(self):
        store = self._store()
        store.add(
            StrategyFingerprint(
                strategy_id="STR-OLD-001",
                ast_hash="abc123",
                embedding=None,
                pnl_series=(0.0, 1.0, 2.0, 3.0),
                retired_at="2026-08-01",
            )
        )
        matches = store.find_similar((0.0, 1.0, 2.0, 3.0))
        assert [m.strategy_id for m in matches] == ["STR-OLD-001"]

    def test_reversed_pnl_not_similar(self):
        """反向序列：DTW 大且 Pearson=-1，双条件均不满足。"""
        store = self._store()
        store.add(
            StrategyFingerprint(
                strategy_id="STR-OLD-001",
                ast_hash="abc123",
                embedding=None,
                pnl_series=(0.0, 1.0, 2.0, 3.0),
                retired_at="2026-08-01",
            )
        )
        assert store.find_similar((3.0, 2.0, 1.0, 0.0)) == []

    def test_duplicate_strategy_id_rejected(self):
        store = self._store()
        fp = StrategyFingerprint("STR-OLD-001", "h", None, (1.0, 2.0), "2026-08-01")
        store.add(fp)
        with pytest.raises(ValueError):
            store.add(fp)

    def test_no_pnl_series_skipped_in_similarity(self):
        """无 PnL 序列的指纹不参与形态比对（Tier3 数据缺失降级）。"""
        store = self._store()
        store.add(StrategyFingerprint("STR-OLD-002", "h", None, None, "2026-08-01"))
        assert store.find_similar((1.0, 2.0)) == []

    def test_query_empty_series_raises(self):
        store = self._store()
        with pytest.raises(ValueError):
            store.find_similar(())
