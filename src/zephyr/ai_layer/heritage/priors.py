# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_heritage
# [MODULE] zephyr.ai_layer.heritage.priors
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.ai_layer.heritage.policy (HeritagePolicy/load_policy);
#                zephyr.ai_layer.heritage.store (HeritageStore 只读连接复用);
#                zephyr.infrastructure.database_service (get_db_service)
# [CONSUMERS] L1 感知开单链（施工项 9，随本模块解锁——trigger='l7_prior'+priority 因子）;
#             scripts/ai_layer/gen_heritage_human_digest.py（冻结状态可见）
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] 全只读（V3/V4 视图+L2 行为格覆盖读数，零写入路径）;
#              防近亲繁殖 D-L7-03：prior_factor∈[1.0,2.0] 越界拒收（fail-closed，绝不静默截断）;
#              排除词表只滤词不灭矿脉：apply_exclusion 机检每单至少保留 1 组关键词;
#              贫矿降级权零介入（配额真源=L1 源注册表，本模块无下调路径）;
#              覆盖率冻结=纯函数（coverage+前两月覆盖率链→冻结判定），无自走时钟;
#              l7_prior 日占比≤50% 的执行面在 L1 journal 侧，本模块只出判据 helper
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L7_heredity/DESIGN.md §2.4/§2.6（D-L7-03 四约束）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] factor 越界→PriorFactorOutOfRange（ValueError 子类）; V3 格缺席→factor=1.0 空先验（正常态非错误）;
#                  DB 不可达→异常上抛（不吞不降级）
# [TESTS] tests/ai_layer/heritage/test_heritage_priors.py（越界拒收/保底 1 组词/冻结判定三态/
#         日占比判据/假服务 V3→response 组装）
# [TTL] permanent
"""priors — L7→L1 先验只读服务：富矿加权因子 + 排除词表 + 多样性冻结判定。

设计真源：``docs/_working/ai_layer_vision/L7_heredity/DESIGN.md`` §2.4（L1 先验字段）/
§2.6（D-L7-03 防近亲繁殖四约束）。契约（§三）：{domain, mechanism_family} →
{prior_factor, rationale_refs, exclusion_keywords[]}。

只做两件事：①按 domain×family 读 V3 得 prior_factor（富矿加法加权，只调排序不碰配额）；
②读 V4 得排除词表（每单保底 1 组关键词的机检在本模块）。消费触发=L1 每次开单时调用（纯只读）。
"""

from __future__ import annotations

import logging
from typing import Any, Final

from zephyr.ai_layer.heritage.policy import HeritagePolicy, load_policy
from zephyr.ai_layer.heritage.store import DEFAULT_SCHEMA, HeritageStore

log = logging.getLogger(__name__)

__all__: Final = [
    "HeritagePriors",
    "PriorFactorOutOfRange",
    "apply_exclusion",
    "daily_share_exceeded",
    "diversity_freeze",
    "validate_prior_factor",
]


class PriorFactorOutOfRange(ValueError):
    """V3 先验因子越界 [prior_factor_min, prior_factor_max]（fail-closed 拒收）。"""


def validate_prior_factor(factor: float, policy: HeritagePolicy) -> float:
    """防近亲繁殖约束 1：只接受 [1.0, 2.0] 区间内的加法因子，越界即拒（不截断）。"""
    low = policy.anti_incest.prior_factor_min
    high = policy.anti_incest.prior_factor_max
    if not low <= factor <= high:
        raise PriorFactorOutOfRange(f"prior_factor={factor} 越界 [{low}, {high}]")
    return float(factor)


def apply_exclusion(
    keyword_groups: list[list[str]] | tuple[list[str], ...],
    exclusion_keywords: list[str] | tuple[str, ...],
    *,
    min_keep: int = 1,
) -> tuple[list[list[str]], list[list[str]]]:
    """约束 3：排除词表只滤词不灭矿脉——过滤后每单至少保留 min_keep 组关键词。

    含任一排除词的组被滤除；若全部组都会被滤除，则保留**排位最前**的未滤组语义改为：
    全滤时保留第一组原样（宁可不滤也不灭矿脉）。返回 (kept_groups, dropped_groups)。
    """
    exclusions = {str(w) for w in exclusion_keywords}
    kept: list[list[str]] = []
    dropped: list[list[str]] = []
    for group in keyword_groups:
        words = [str(w) for w in group]
        if exclusions & set(words):
            dropped.append(words)
        else:
            kept.append(words)
    if len(kept) < min_keep and keyword_groups:
        first = [str(w) for w in keyword_groups[0]]
        if first not in kept:
            kept.insert(0, first)
            if first in dropped:
                dropped.remove(first)
    return kept, dropped


def diversity_freeze(
    coverage_pct: float | None,
    prev_coverage_pct: float | None,
    prev2_coverage_pct: float | None,
    policy: HeritagePolicy,
) -> tuple[bool, str]:
    """约束 4：多样性保底冻结判定（纯函数，digest 月度窗与 priors 运行时共用同一判据）。

    规则：覆盖率 <冻结线 → 冻结；或连续 2 个月下降 → 冻结（历史缺席时只按线判定——
    首月无趋势数据属正常态，非错误）。返回 (frozen?, why)。
    """
    line = policy.anti_incest.coverage_freeze_line_pct
    if coverage_pct is not None and coverage_pct < line:
        return True, f"coverage={coverage_pct}<{line}"
    declines = 0
    for prev in (prev_coverage_pct, prev2_coverage_pct):
        if coverage_pct is not None and prev is not None and prev > coverage_pct:
            declines += 1
        else:
            break
    if declines >= policy.anti_incest.coverage_decline_months:
        return True, f"coverage_declined_{declines}_months"
    return False, "healthy"


def daily_share_exceeded(l7_prior_count: int, total_count: int, policy: HeritagePolicy) -> bool:
    """约束 2 判据：l7_prior 触发单占比 ≤50%/日（执行面在 L1 journal 侧，本 helper 供其调用）。"""
    if total_count <= 0:
        return False
    return (l7_prior_count / total_count) > policy.anti_incest.l7_prior_daily_share_max


class HeritagePriors:
    """L1 先验只读薄封装（V3 富矿因子 / V4 排除词表 / L2 行为格覆盖读数）。"""

    def __init__(
        self,
        schema: str = DEFAULT_SCHEMA,
        *,
        service: Any | None = None,
        store: HeritageStore | None = None,
        l2_schema: str = "ai_intake",
        policy: HeritagePolicy | None = None,
    ) -> None:
        self._store = store or HeritageStore(schema, service=service)
        self.schema: Final = self._store.schema
        self.l2_schema: Final = l2_schema
        self._policy: Final = policy or load_policy()

    @property
    def policy(self) -> HeritagePolicy:
        """规则参数快照（只读；唯一真源=config/heritage_policy.yaml）。"""
        return self._policy

    def _read(self, sql: str, params: tuple[Any, ...] | dict[str, Any]) -> list[dict[str, Any]]:
        conn = self._store.read_conn()
        cur = conn.cursor()
        cur.execute(sql, params)
        return [dict(r) if isinstance(r, dict) else None for r in cur.fetchall()]  # type: ignore[misc]

    def prior_row(self, domain_id: str, mechanism_family: str) -> dict[str, Any] | None:
        """读 V3 单格先验行（缺席=None，属正常态）。"""
        rows = self._read(
            f"SELECT domain_id, mechanism_family, elite_n, hit90_n, rationale_refs, prior_factor "
            f"FROM {self.schema}.ai_heritage_l1_prior WHERE domain_id = %s AND mechanism_family = %s",
            (domain_id, mechanism_family),
        )
        return rows[0] if rows else None

    def exclusion_keywords(self, domain_id: str) -> list[str]:
        """读 V4 该域 active 缺陷排除词表（展开行去重保序）。"""
        rows = self._read(
            f"SELECT keyword FROM {self.schema}.ai_heritage_l1_exclusion WHERE domain_id = %s "  # noqa: bare-sql  bare-sql豁免: P1存量伪新增,域内SQL集中通道,§5.160.2专项另列
            f"ORDER BY entry_id",
            (domain_id,),
        )
        out: list[str] = []
        for row in rows:
            word = str(row.get("keyword") or "")
            if word and word not in out:
                out.append(word)
        return out

    def build_prior_response(
        self,
        prior_row: dict[str, Any] | None,
        exclusions: list[str],
        *,
        coverage_pct: float | None = None,
        prev_coverage_pct: float | None = None,
        prev2_coverage_pct: float | None = None,
    ) -> dict[str, Any]:
        """V3/V4 行 → L1 契约响应（factor 越界拒收；格缺席=1.0 空先验；覆盖率可注入）。

        coverage 三参注入为纯函数面（单测零 DB）；prior_for 正门传当月读数。
        """
        if prior_row is None:
            return {
                "prior_factor": self._policy.anti_incest.prior_factor_min,
                "rationale_refs": [],
                "exclusion_keywords": list(exclusions),
                "frozen": False,
            }
        factor = validate_prior_factor(float(prior_row["prior_factor"]), self._policy)
        frozen, _why = diversity_freeze(
            coverage_pct, prev_coverage_pct, prev2_coverage_pct, self._policy
        )
        return {
            "prior_factor": self._policy.anti_incest.prior_factor_min if frozen else factor,
            "rationale_refs": list(prior_row.get("rationale_refs") or []),
            "exclusion_keywords": list(exclusions),
            "frozen": frozen,
        }

    def prior_for(self, domain_id: str, mechanism_family: str) -> dict[str, Any]:
        """L1 开单正门：{domain, mechanism_family} → {prior_factor, rationale_refs, exclusion_keywords}。"""
        exclusions = self.exclusion_keywords(domain_id)
        return self.build_prior_response(
            self.prior_row(domain_id, mechanism_family),
            exclusions,
            coverage_pct=self.coverage_pct(),
        )

    def coverage_pct(self) -> float | None:
        """行为格覆盖率读数（真源=L2 ai_intake_card active elite_cell，DESIGN §2.6 约束 4）。"""
        rows = self._read(
            f"SELECT count(DISTINCT elite_cell)::int AS covered FROM {self.l2_schema}.ai_intake_card "  # noqa: bare-sql  bare-sql豁免: P1存量伪新增,域内SQL集中通道,§5.160.2专项另列
            f"WHERE elite_status = 'active'",
            (),
        )
        covered = int(rows[0]["covered"]) if rows and rows[0] else 0
        return round(100.0 * covered / self._policy.anti_incest.total_cells, 2)

    def freeze_state(
        self, prev_coverage_pct: float | None = None, prev2_coverage_pct: float | None = None
    ) -> tuple[bool, str]:
        """当前冻结态（当月覆盖读数+前两月链；历史由 digest 前言链供）。"""
        return diversity_freeze(
            self.coverage_pct(), prev_coverage_pct, prev2_coverage_pct, self._policy
        )
