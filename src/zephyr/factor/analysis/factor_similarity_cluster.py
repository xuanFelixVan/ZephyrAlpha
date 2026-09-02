# [BLUEPRINT] MOD-L02_ANA | docs/03_modules/_domain_factor/blueprint.md | 待统筹登记（缺口总账 GAP-F-38 行）
# [MODULE] zephyr.factor.analysis.factor_similarity_cluster
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] numpy; sklearn.cluster（lazy import，与 ml_train density_quantile_trainer 同口径——sklearn 非核心依赖，仅在函数体内引入）
# [CONSUMERS] （候选：研究组·因子库页"相似组"列 + 相似阈值滑块，GAP-F-38 消费位）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 双法封闭 {hierarchical, dbscan}；相关性=Pearson（IC/暴露序列对齐位点）；距离=1-corr；层次=AgglomerativeClustering(metric=precomputed, linkage=average, distance_threshold=1-阈值)；DBSCAN eps=1-阈值 min_samples=1（零噪声点全成簇）；簇号归一化按首现序保确定性；组内代表=质量分最高（默认 mean|IC|，quality_scores 注入可覆盖，未知因子键 fail-closed）；frozen dataclass JSON 可序列化
# [MODIFY-GUARD] docs/_working/2026-08-22-frontend-backend-gap-ledger.md GAP-F-38 行
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError（因子数/序列长度/非有限/零方差/方法/阈值非法，fail-closed）
# [TESTS] tests/factor/test_factor_similarity_cluster.py
# [A_module] module_id=MOD-L02_ANA_cluster | layer=module | stability=testing | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""因子相似度聚类器（GAP-F-38，factor/analysis 子包）。

缺口总账 GAP-F-38（研究组·因子库页）：因子暴露/IC 序列相关性矩阵 + 层次/
DBSCAN 聚类 + 组内代表因子排名。前端"相似阈值滑块"对应 config.similarity_threshold
（相似度阈值 τ → 距离阈 1-τ）。

算法：
    ① 序列对齐校验（等长、≥min_series_len、有限、非零方差）→ Pearson 相关矩阵；
    ② 距离阵 D=1-corr（clip [0,2]），对角置 0；
    ③ hierarchical：sklearn AgglomerativeClustering(metric="precomputed",
       linkage="average", distance_threshold=1-τ, n_clusters=None)；
       dbscan：DBSCAN(metric="precomputed", eps=1-τ, min_samples=1)；
    ④ 簇号按首现序归一化（sklearn 标签任意整数 → 0..G-1 稳定序）；
    ⑤ 组内排名：质量分降序（默认 mean|IC|，quality_scores 注入覆盖），
       代表=第一名；intra_corr_mean=组内两两相关均值（单因子组=1.0 留痕）。

不做什么：不读因子库/注册表（序列由上游装载注入）/不做因子评价结论
（聚类是结构描摹，不代表因子优劣）。

依据: 缺口总账 GAP-F-38
SSoT: depgraph node 10505568（blueprint MOD-L02_ANA）
Version: 0.1.0

# [ALGO_FLOW]
# 输入: ic_series {factor_id: IC/暴露序列} + 可选 quality_scores + ClusterConfig
# 特征: Pearson 相关矩阵 / 距离阵
# 算法: 层次（average linkage 距离阈）| DBSCAN（precomputed eps）→ 簇归一化 → 组内排名
# 输出: FactorClusterResult（labels/clusters/代表/组内均相关/矩阵）
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field
from typing import Any, Final, Mapping, Sequence

import numpy as np

logger = logging.getLogger(__name__)

__all__: Final = [
    "METHOD_DBSCAN",
    "METHOD_HIERARCHICAL",
    "ClusterConfig",
    "FactorCluster",
    "FactorClusterResult",
    "cluster_factors",
]

METHOD_HIERARCHICAL: Final = "hierarchical"
METHOD_DBSCAN: Final = "dbscan"
_METHODS: Final = frozenset({METHOD_HIERARCHICAL, METHOD_DBSCAN})


@dataclass(frozen=True, slots=True)
class ClusterConfig:
    """聚类配置（相似阈值=前端滑块语义）。"""

    method: str = METHOD_HIERARCHICAL
    similarity_threshold: float = 0.7  # τ：corr ≥ τ 视为同组（距离阈=1-τ）
    min_series_len: int = 5

    def __post_init__(self) -> None:
        if self.method not in _METHODS:
            raise ValueError(f"method 非法（合法={sorted(_METHODS)}）: {self.method!r}")
        if not (0.0 < float(self.similarity_threshold) < 1.0):
            raise ValueError(f"similarity_threshold 非法（须 ∈ (0,1)）: {self.similarity_threshold!r}")
        if int(self.min_series_len) < 3:
            raise ValueError(f"min_series_len 非法（须 ≥3）: {self.min_series_len!r}")


@dataclass(frozen=True, slots=True)
class FactorCluster:
    """单个相似组（成员+代表+组内排名+组内均相关）。"""

    cluster_id: int
    members: tuple[str, ...]
    representative: str
    member_ranking: tuple[str, ...]  # 质量分降序
    intra_corr_mean: float


@dataclass(frozen=True, slots=True)
class FactorClusterResult:
    """聚类总产出（JSON 可序列化）。"""

    method: str
    similarity_threshold: float
    n_clusters: int
    factor_ids: tuple[str, ...]
    labels: dict[str, int]
    clusters: tuple[FactorCluster, ...]
    correlation_matrix: tuple[tuple[float, ...], ...]  # 按 factor_ids 序
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _validate_series(ic_series: Mapping[str, Sequence[float]], min_len: int) -> tuple[tuple[str, ...], np.ndarray]:
    ids = tuple(str(k) for k in ic_series.keys())
    if len(ids) < 2:
        raise ValueError(f"因子数不足（须 ≥2）: {len(ids)}")
    cols = []
    length: int | None = None
    for fid in ids:
        arr = np.asarray(list(ic_series[fid]), dtype=float)
        if length is None:
            length = len(arr)
        elif len(arr) != length:
            raise ValueError(f"序列须等长: {fid} 长度 {len(arr)} ≠ {length}")
        if not np.all(np.isfinite(arr)):
            raise ValueError(f"序列非法（须全部有限）: {fid}")
        cols.append(arr)
    assert length is not None
    if length < min_len:
        raise ValueError(f"序列长度不足（须 ≥{min_len}）: {length}")
    mat = np.column_stack(cols)
    if np.any(np.std(mat, axis=0, ddof=1) == 0.0):
        bad = ids[int(np.argmin(np.std(mat, axis=0, ddof=1)))]
        raise ValueError(f"序列零方差（常量无法相关）: {bad}")
    return ids, mat


def _cluster_labels(dist: np.ndarray, cfg: ClusterConfig) -> np.ndarray:
    from sklearn.cluster import DBSCAN, AgglomerativeClustering  # lazy import（非核心依赖）

    if cfg.method == METHOD_HIERARCHICAL:
        model = AgglomerativeClustering(
            n_clusters=None,
            metric="precomputed",
            linkage="average",
            distance_threshold=1.0 - float(cfg.similarity_threshold),
        )
    else:
        model = DBSCAN(
            metric="precomputed",
            eps=1.0 - float(cfg.similarity_threshold),
            min_samples=1,
        )
    return np.asarray(model.fit_predict(dist), dtype=int)


def _normalize_labels(raw: np.ndarray) -> np.ndarray:
    """簇号按首现序归一化（确定性输出）。"""
    mapping: dict[int, int] = {}
    out = np.empty_like(raw)
    for i, lab in enumerate(raw):
        key = int(lab)
        if key not in mapping:
            mapping[key] = len(mapping)
        out[i] = mapping[key]
    return out


def cluster_factors(
    ic_series: Mapping[str, Sequence[float]],
    *,
    config: ClusterConfig | None = None,
    quality_scores: Mapping[str, float] | None = None,
) -> FactorClusterResult:
    """因子相似度聚类主入口（相关性矩阵+层次/DBSCAN+组内代表排名）。

    Args:
        ic_series: {factor_id: IC/暴露序列}（等长对齐，≥2 个因子）。
        config: 聚类配置（None=层次法+阈值 0.7）。
        quality_scores: 可选质量分 {factor_id: score}（组内排名依据；
            None=mean|IC|；键必须是 ic_series 子集，否则 fail-closed）。

    Returns:
        FactorClusterResult（labels/clusters/矩阵，JSON 可序列化）。

    Raises:
        ValueError: 输入/参数非法（fail-closed）。
    """
    cfg = config or ClusterConfig()
    ids, mat = _validate_series(ic_series, cfg.min_series_len)
    if quality_scores is not None:
        unknown = sorted(set(str(k) for k in quality_scores) - set(ids))
        if unknown:
            raise ValueError(f"quality_scores 含未知因子键: {unknown}")

    corr = np.corrcoef(mat, rowvar=False)
    dist = np.clip(1.0 - corr, 0.0, 2.0)
    np.fill_diagonal(dist, 0.0)

    labels = _normalize_labels(_cluster_labels(dist, cfg))
    quality = (
        {fid: float(quality_scores[fid]) for fid in ids}
        if quality_scores is not None
        else {fid: float(np.mean(np.abs(mat[:, i]))) for i, fid in enumerate(ids)}
    )

    clusters: list[FactorCluster] = []
    for cid in sorted(set(labels.tolist())):
        members = tuple(fid for i, fid in enumerate(ids) if int(labels[i]) == cid)
        ranking = tuple(sorted(members, key=lambda f: (-quality[f], f)))
        if len(members) > 1:
            idx = [ids.index(m) for m in members]
            sub = corr[np.ix_(idx, idx)]
            off_diag = sub[np.triu_indices(len(idx), k=1)]
            intra = float(np.mean(off_diag))
        else:
            intra = 1.0
        clusters.append(
            FactorCluster(
                cluster_id=cid,
                members=members,
                representative=ranking[0],
                member_ranking=ranking,
                intra_corr_mean=round(intra, 6),
            )
        )

    return FactorClusterResult(
        method=cfg.method,
        similarity_threshold=float(cfg.similarity_threshold),
        n_clusters=len(clusters),
        factor_ids=ids,
        labels={fid: int(labels[i]) for i, fid in enumerate(ids)},
        clusters=tuple(clusters),
        correlation_matrix=tuple(tuple(round(float(x), 6) for x in row) for row in corr),
        notes=(),
    )
