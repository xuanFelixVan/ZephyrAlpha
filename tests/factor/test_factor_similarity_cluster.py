# [A_test] module_id: MOD-L02_ANA_cluster | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L02_ANA | docs/03_modules/_domain_factor/blueprint.md | 缺口总账 GAP-F-38 行
# [MODULE] tests.factor.test_factor_similarity_cluster
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

"""因子相似度聚类器（GAP-F-38，factor/analysis 子包）施工验证测试。

覆盖：
- 相关性矩阵：对称、对角 1、高相关因子对数值合理；
- 层次聚类：高相关同组、独立因子独立成组；DBSCAN 同义；
- 组内代表排名：默认 mean|IC| 最高者为代表；quality_scores 注入可覆盖；
- 确定性：同输入同标签（归一化簇号按首现序）；
- fail-closed：因子数不足/序列不等长/长度过短/非有限/零方差/非法方法/阈值越界；
- 契约：frozen、to_dict JSON 可序列化。
全程内存合成数据，无 DB；sklearn 真实计算（小矩阵）。
"""

from __future__ import annotations

import dataclasses
import json

import numpy as np
import pytest

from zephyr.factor.analysis.factor_similarity_cluster import (
    METHOD_DBSCAN,
    METHOD_HIERARCHICAL,
    ClusterConfig,
    FactorClusterResult,
    cluster_factors,
)


def _series_pack(n: int = 120):
    rng = np.random.default_rng(3)
    base = rng.standard_normal(n)
    indep = rng.standard_normal(n)
    return {
        "F_A": (base + 0.05 * rng.standard_normal(n)).tolist(),
        "F_B": (1.5 * base + 0.05 * rng.standard_normal(n)).tolist(),
        "F_C": indep.tolist(),
    }


class TestCorrelationMatrix:
    def test_matrix_symmetric_unit_diag(self) -> None:
        res = cluster_factors(_series_pack())
        mat = res.correlation_matrix
        ids = list(res.factor_ids)
        for i in range(3):
            assert mat[i][i] == pytest.approx(1.0)
            for j in range(3):
                assert mat[i][j] == pytest.approx(mat[j][i])
        ia, ib, ic = ids.index("F_A"), ids.index("F_B"), ids.index("F_C")
        assert mat[ia][ib] > 0.9
        assert abs(mat[ia][ic]) < 0.3


class TestClustering:
    def test_hierarchical_groups_correlated(self) -> None:
        res = cluster_factors(_series_pack(), config=ClusterConfig(similarity_threshold=0.5))
        labels = res.labels
        assert labels["F_A"] == labels["F_B"]
        assert labels["F_C"] != labels["F_A"]
        assert res.n_clusters == 2

    def test_dbscan_same_grouping(self) -> None:
        res = cluster_factors(
            _series_pack(), config=ClusterConfig(method=METHOD_DBSCAN, similarity_threshold=0.5)
        )
        assert res.method == METHOD_DBSCAN
        assert res.labels["F_A"] == res.labels["F_B"]
        assert res.labels["F_C"] != res.labels["F_A"]

    def test_strict_threshold_splits(self) -> None:
        res = cluster_factors(_series_pack(), config=ClusterConfig(similarity_threshold=0.999))
        assert res.n_clusters == 3

    def test_deterministic(self) -> None:
        a = cluster_factors(_series_pack())
        b = cluster_factors(_series_pack())
        assert a.labels == b.labels
        assert a.to_dict() == b.to_dict()


class TestRepresentative:
    def test_default_mean_abs_ic(self) -> None:
        pack = _series_pack()
        res = cluster_factors(pack, config=ClusterConfig(similarity_threshold=0.5))
        cluster = next(c for c in res.clusters if "F_A" in c.members)
        mean_abs = {fid: float(np.mean(np.abs(pack[fid]))) for fid in cluster.members}
        expected = max(cluster.members, key=lambda f: mean_abs[f])
        assert cluster.representative == expected

    def test_quality_scores_override(self) -> None:
        res = cluster_factors(
            _series_pack(),
            config=ClusterConfig(similarity_threshold=0.5),
            quality_scores={"F_A": 0.9, "F_B": 0.1, "F_C": 0.5},
        )
        cluster = next(c for c in res.clusters if "F_A" in c.members)
        assert cluster.representative == "F_A"
        assert cluster.member_ranking[0] == "F_A"

    def test_intra_cluster_corr(self) -> None:
        res = cluster_factors(_series_pack(), config=ClusterConfig(similarity_threshold=0.5))
        cluster = next(c for c in res.clusters if "F_A" in c.members)
        assert cluster.intra_corr_mean > 0.9


class TestValidation:
    def test_too_few_factors_rejected(self) -> None:
        with pytest.raises(ValueError, match="因子数"):
            cluster_factors({"ONLY": [0.1, 0.2, 0.3, 0.4, 0.5]})

    def test_unequal_length_rejected(self) -> None:
        with pytest.raises(ValueError, match="等长"):
            cluster_factors({"A": [0.1, 0.2, 0.3, 0.4, 0.5], "B": [0.1, 0.2]})

    def test_short_series_rejected(self) -> None:
        with pytest.raises(ValueError, match="长度"):
            cluster_factors({"A": [0.1, 0.2, 0.3], "B": [0.1, 0.2, 0.4]})

    def test_non_finite_rejected(self) -> None:
        with pytest.raises(ValueError, match="有限"):
            cluster_factors({"A": [0.1, 0.2, float("nan"), 0.4, 0.5], "B": [0.1, 0.2, 0.3, 0.4, 0.5]})

    def test_zero_variance_rejected(self) -> None:
        with pytest.raises(ValueError, match="方差"):
            cluster_factors({"A": [0.5] * 10, "B": list(range(10))})

    def test_bad_method_rejected(self) -> None:
        with pytest.raises(ValueError, match="method"):
            ClusterConfig(method="kmeans")

    def test_threshold_out_of_range_rejected(self) -> None:
        with pytest.raises(ValueError, match="similarity_threshold"):
            ClusterConfig(similarity_threshold=1.5)

    def test_unknown_quality_factor_rejected(self) -> None:
        with pytest.raises(ValueError, match="quality_scores"):
            cluster_factors(_series_pack(), quality_scores={"F_X": 1.0})


class TestContract:
    def test_to_dict_json_serializable(self) -> None:
        res = cluster_factors(_series_pack())
        text = json.dumps(res.to_dict(), ensure_ascii=False)
        assert "clusters" in text

    def test_frozen(self) -> None:
        res = cluster_factors(_series_pack())
        assert isinstance(res, FactorClusterResult)
        with pytest.raises(dataclasses.FrozenInstanceError):
            res.n_clusters = 9  # type: ignore[misc]
