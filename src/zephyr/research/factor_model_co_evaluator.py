# [BLUEPRINT] MOD-FAC-005 | docs/03_modules/_domain_factor/factor_model_co_evaluator/blueprint.md
# [MODULE] zephyr.research.factor_model_co_evaluator
# [DOMAIN] D_FACTOR
# [DEPENDENCIES] 无（协议核心纯内存；contribution_evaluator/utilization_evaluator 全注入）
# [CONSUMERS] 运行时装配批（因子↔模型联合评估批 / 淘汰清单与迭代方向入研究治理流）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 双向评估固定：因子→模型=mean(contribution(f,m))；模型→因子=mean(utilization(m,f))；评估器全注入（缺失/异常/返回非法 Fail-Closed）；裁决词表闭合 eliminate|iterate|keep（contrib<淘汰线→eliminate；淘汰线≤contrib<高贡献线且 util≥高利用线→iterate；余者 keep）；淘汰/迭代清单按 (得分,factor_id) 确定性排序；报告版本化（version 自 1 单调递增、写后不可变、未知版本查询 Fail-Closed）；同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_factor/factor_model_co_evaluator/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] CoEvaluatorError(占位 ZA-FAC-UNREGISTERED-CO-EVALUATOR)——评估器缺失或异常/阈值序非法/因子或模型 id 空或重复/未知报告版本时抛
# [TESTS] tests/research/test_factor_model_co_evaluator.py
# [A_module] module_id=MOD-FAC-005 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""FactorModelCoEvaluator — 因子模型联合评估器（MOD-FAC-005）。

B10-01230（AUD-DRAFT-001-DIGEST P2 波 P2-W07，CAND-FAC-017，A1 v8.2）：
R&D-Agent-Quant 联合优化——因子↔模型**双向评估**（因子贡献于模型性能 / 模型
对因子利用度双向报告）+ 淘汰/迭代建议（低贡献因子**淘汰清单** + 高潜力**迭
代方向**）+ **报告版本化**。

查重分工（蓝图 §0）：factor_vote_mining=多 Agent 因子**产出**协议（上游）；
本件=存量因子×存量模型的**双向贡献/利用度体检**（下游治理面，不产新因子、
不改注册表，仅产版本化评估报告）。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Sequence

_log = logging.getLogger(__name__)

__all__: Final = [
    "CoEvaluationReport",
    "CoEvaluatorError",
    "FactorDirectionScore",
    "FactorModelCoEvaluator",
    "FactorVerdict",
    "ModelDirectionScore",
]


class CoEvaluatorError(Exception):
    """联合评估输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-FAC-UNREGISTERED-CO-EVALUATOR。
    """


class FactorVerdict(str, Enum):
    """因子裁决词表（闭合）。"""

    ELIMINATE = "eliminate"
    ITERATE = "iterate"
    KEEP = "keep"


@dataclass(frozen=True)
class FactorDirectionScore:
    """单因子双向得分与裁决（frozen）。"""

    factor_id: str
    mean_contribution: float
    mean_utilization: float
    verdict: FactorVerdict


@dataclass(frozen=True)
class ModelDirectionScore:
    """单模型因子利用度得分（frozen）。"""

    model_id: str
    mean_utilization: float


@dataclass(frozen=True)
class CoEvaluationReport:
    """联合评估报告（frozen；版本化不可变）。"""

    version: int
    factor_scores: tuple[FactorDirectionScore, ...]
    model_scores: tuple[ModelDirectionScore, ...]
    elimination_list: tuple[str, ...]
    iteration_list: tuple[str, ...]


class FactorModelCoEvaluator:
    """因子↔模型双向评估器（淘汰/迭代建议 + 报告版本化）。

    Args:
        contribution_evaluator: 注入贡献评估器，``(factor_id, model_id) -> float``。
        utilization_evaluator: 注入利用度评估器，``(model_id, factor_id) -> float``。
        eliminate_threshold: 低贡献淘汰线（contrib < 线 → eliminate）。
        high_contribution: 高贡献线（∈ (淘汰线, 1]）。
        high_utilization: 高利用线（∈ [0,1]；中贡献高利用 → iterate）。
    """

    def __init__(
        self,
        *,
        contribution_evaluator: Callable[[str, str], float] | None,
        utilization_evaluator: Callable[[str, str], float] | None,
        eliminate_threshold: float = 0.05,
        high_contribution: float = 0.20,
        high_utilization: float = 0.50,
    ) -> None:
        if contribution_evaluator is None:
            raise CoEvaluatorError("contribution_evaluator 未注入（Fail-Closed）")
        if utilization_evaluator is None:
            raise CoEvaluatorError("utilization_evaluator 未注入（Fail-Closed）")
        et, hc, hu = float(eliminate_threshold), float(high_contribution), float(high_utilization)
        if not (0.0 <= et < hc <= 1.0):
            raise CoEvaluatorError(f"阈值序非法（须 0≤淘汰线<高贡献线≤1）: {et!r} / {hc!r}")
        if not (0.0 <= hu <= 1.0):
            raise CoEvaluatorError(f"高利用线非法（须 ∈ [0,1]）: {hu!r}")
        self._contrib = contribution_evaluator
        self._util = utilization_evaluator
        self._elim = et
        self._high_c = hc
        self._high_u = hu
        self._reports: dict[int, CoEvaluationReport] = {}

    # ── 内部 ─────────────────────────────────────────────────────────────

    @staticmethod
    def _ids(kind: str, ids: Sequence[str]) -> tuple[str, ...]:
        if not ids:
            raise CoEvaluatorError(f"{kind} 为空（无评估对象）")
        out = tuple(ids)
        if any(not isinstance(i, str) or not i.strip() for i in out):
            raise CoEvaluatorError(f"{kind} 含空白 id: {list(out)!r}")
        if len(set(out)) != len(out):
            raise CoEvaluatorError(f"{kind} 含重复 id: {list(out)!r}")
        return tuple(i.strip() for i in out)

    def _score(self, fn: Callable[[str, str], float], a: str, b: str, label: str) -> float:
        try:
            v = fn(a, b)
        except CoEvaluatorError:
            raise
        except Exception as exc:  # noqa: BLE001 — 注入件异常 Fail-Closed
            raise CoEvaluatorError(f"{label} 异常: ({a!r},{b!r})（{type(exc).__name__}）") from exc
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            raise CoEvaluatorError(f"{label} 返回非法: {v!r}（({a!r},{b!r})）")
        return float(v)

    def _verdict(self, contrib: float, util: float) -> FactorVerdict:
        if contrib < self._elim:
            return FactorVerdict.ELIMINATE
        if contrib < self._high_c and util >= self._high_u:
            return FactorVerdict.ITERATE
        return FactorVerdict.KEEP

    # ── 双向评估 ──────────────────────────────────────────────────────────

    def evaluate(
        self,
        factor_ids: Sequence[str],
        model_ids: Sequence[str],
    ) -> CoEvaluationReport:
        """双向评估主入口：因子→模型贡献 / 模型→因子利用 + 淘汰/迭代清单。"""
        factors = self._ids("factor_ids", factor_ids)
        models = self._ids("model_ids", model_ids)
        # 双向评分矩阵（每对仅评估一次，确定性）
        contrib_m = {
            (f, m): self._score(self._contrib, f, m, "contribution_evaluator")
            for f in factors
            for m in models
        }
        util_m = {
            (m, f): self._score(self._util, m, f, "utilization_evaluator")
            for m in models
            for f in factors
        }
        f_scores: list[FactorDirectionScore] = []
        for f in factors:
            contrib = round(sum(contrib_m[(f, m)] for m in models) / len(models), 6)
            util = round(sum(util_m[(m, f)] for m in models) / len(models), 6)
            f_scores.append(
                FactorDirectionScore(
                    factor_id=f,
                    mean_contribution=contrib,
                    mean_utilization=util,
                    verdict=self._verdict(contrib, util),
                )
            )
        m_scores = tuple(
            ModelDirectionScore(
                model_id=m,
                mean_utilization=round(sum(util_m[(m, f)] for f in factors) / len(factors), 6),
            )
            for m in models
        )
        elim = tuple(
            s.factor_id
            for s in sorted(
                (s for s in f_scores if s.verdict is FactorVerdict.ELIMINATE),
                key=lambda s: (s.mean_contribution, s.factor_id),
            )
        )
        it = tuple(
            s.factor_id
            for s in sorted(
                (s for s in f_scores if s.verdict is FactorVerdict.ITERATE),
                key=lambda s: (s.mean_contribution, s.factor_id),
            )
        )
        version = len(self._reports) + 1
        report = CoEvaluationReport(
            version=version,
            factor_scores=tuple(f_scores),
            model_scores=m_scores,
            elimination_list=elim,
            iteration_list=it,
        )
        self._reports[version] = report  # 写后不可变（frozen 报告）
        _log.info(
            "联合评估报告 v%d: 因子 %d / 模型 %d / 淘汰 %d / 迭代 %d",
            version, len(factors), len(models), len(elim), len(it),
        )
        return report

    # ── 版本化查询 ──────────────────────────────────────────────────────────

    def get_report(self, version: int) -> CoEvaluationReport:
        """按版本取报告（未知版本 Fail-Closed）。"""
        report = self._reports.get(version)
        if report is None:
            raise CoEvaluatorError(f"未知报告版本: {version!r}")
        return report

    def list_versions(self) -> tuple[int, ...]:
        """已产报告版本（升序确定性）。"""
        return tuple(sorted(self._reports))

    def latest(self) -> CoEvaluationReport:
        """最新报告（无报告 Fail-Closed）。"""
        if not self._reports:
            raise CoEvaluatorError("尚无评估报告（先 evaluate）")
        return self._reports[max(self._reports)]
