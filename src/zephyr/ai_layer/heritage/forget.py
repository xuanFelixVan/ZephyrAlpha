# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_heritage
# [MODULE] zephyr.ai_layer.heritage.forget
# [DOMAIN] D_GOVERNANCE
# [TTL] permanent
# [DEPENDENCIES] zephyr.ai_layer.heritage.policy (HeritagePolicy/load_policy);
#                zephyr.ai_layer.heritage.store (HeritageStore——transition_status 执行与零物理删除边界);
#                zephyr.shared.io.paths (REPO_ROOT); zephyr.shared.utils.time_utils (now_utc)
# [CONSUMERS] 月度体检窗（L1 §2.6 同一节拍宿主——日历节拍+每次点火实闸复核，禁 sleep-loop;
#             Owner 不追认外扫裁定时由高模型维护班人工开会话执行，DESIGN §2.8 红蓝 R2 降级路线）;
#             scripts/ai_layer/gen_heritage_human_digest.py（降级报告进月报）
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] 零物理删除（红线）：本模块无 DELETE FROM，遗忘=降 status+移出机检快照，全留痕
#              （compressed 条目 10 年内可由 entry_id 反查全量，DESIGN §2.8 删除红线三档）;
#              三类差异化遗忘（Smyth & Keane 1995 删 auxiliary 保 pivotal——按竞争力贡献不按年龄删）:
#              defect 按受影响面存活不按时间遗忘/elite 按格内 top3/criteria 按 still_valid+venue 3 代;
#              判据=纯函数（plan_* 零 DB 可构造数据全枚举）；执行经 store.transition_status 合法流转校验;
#              挂月度体检窗=日历节拍+点火实闸，不建自走时钟（对齐 L1 §2.4 合规裁定，禁 cron/Timer）;
#              surface 存活判定 v0 保守：不可判定=存活（宁可保留不误删，误删=不可逆方向）;
#              compressed 终态零出边；defect 复发 un-retire 仅限 retired 墓碑（store 状态机表）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L7_heredity/DESIGN.md §2.8（D-L7-05 三类保留/降级/压缩判据）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 目标状态非法→RuntimeError(illegal_transition)（store 状态机 fail-closed）;
#                  entry 不存在→RuntimeError(entry_not_found); 判定数据畸形行→跳过计数留痕不炸整窗;
#                  报告落盘 OSError→上抛（降级不留痕=没发生）
# [TESTS] tests/ai_layer/heritage/test_heritage_forget.py（构造数据三类降级各 1 例/零物理删除源扫描/
#         compressed 可反查/保守 surface 判定）
"""forget — L7 遗忘执行器：三类条目降级/压缩机检 + heritage_forget_due 轻事件与降级报告。

设计真源：``docs/_working/ai_layer_vision/L7_heredity/DESIGN.md`` §2.8（D-L7-05：库不能只进不出；
只降级压缩、永不物理删）。数值判据真源=``config/heritage_policy.yaml`` forget 节（Owner 夜批追认初值）。

三类规则（§2.8 表）::

    缺陷模式  active：受影响面存活即 active（不按时间遗忘）；affected_surfaces 全退役 → retired 墓碑；
              retired 且连续 4 个季度零新案+零 hit → compressed（复发一键 un-retire 回 active）
    精英档案  active：同格（surface×family）保 top3，跌出 → archived（L6 tombstone 满 2 体检窗降级
              由 switch_archived_due retired 事件代行）；archived 满 12 个月且被后代吸收（parent 链）→ compressed
    判据档案  active：still_valid=true 全保留（防重复考古燃料）；翻案回写 false → archived；
              archived 且同 venue 跌出最近 3 代 → compressed（全文仍在 L4 卡不丢）

v0 保守裁定（DESIGN 未给机检口径处，宁保留不误删）：L6 tombstone 满 2 体检窗的季度复扫依赖 L6
库间查询，v0 由 retired 事件即时降级代行、季度复扫挂起；elite"被现役引用即保"的引用核验同批挂起。
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Final

from zephyr.ai_layer.heritage.policy import HeritagePolicy, load_policy
from zephyr.ai_layer.heritage.store import HeritageStore
from zephyr.shared.io.paths import REPO_ROOT
from zephyr.shared.utils.time_utils import now_utc

log = logging.getLogger(__name__)

__all__: Final = [
    "DemotionDecision",
    "HeritageForget",
    "default_surface_alive",
    "plan_criteria",
    "plan_defect",
    "plan_elite",
]

FORGET_EVENT_NAME: Final = "forget_events.jsonl"
FORGET_REPORT_PREFIX: Final = "forget_report"
QUARTER_DAYS: Final = 91  # "连续 N 个季度"按 91 天/季折算（4 季度=364 天，与月度窗取数口径解耦）
DEFAULT_KEEP: Final = 3


@dataclass(frozen=True)
class DemotionDecision:
    """一条降级/压缩裁定（plan_* 纯函数产物；execute 经 store 状态机校验落库）。"""

    entry_id: str
    kind: str
    from_status: str
    to_status: str
    why: str


def default_surface_alive(ref: str) -> bool | None:
    """受影响面存活判定 v0（保守）：可解析为仓库路径→按存在性判；其余=不可判定（None=保守保留）。

    模块删/gate 退役机检查得的精确口径（gate_registry 反查等）随治理域接线批补齐。
    """
    text = str(ref or "").strip()
    if not text:
        return None
    if "/" in text or "\\" in text or text.endswith((".py", ".yaml", ".md")):
        return (REPO_ROOT / text).exists()
    return None


def _days_since(ref: datetime | None, as_of: datetime) -> float:
    if ref is None:
        return float("inf")
    if ref.tzinfo is None:
        ref = ref.replace(tzinfo=as_of.tzinfo)
    return max(0.0, (as_of - ref).total_seconds() / 86400.0)


def plan_defect(
    rows: list[dict[str, Any]],
    surfaces_alive: dict[str, bool | None],
    policy: HeritagePolicy,
    *,
    as_of: datetime | None = None,
) -> list[DemotionDecision]:
    """缺陷模式降级计划（受影响面全退役→retired；retired 且 4 季度零新案零 hit→compressed）。"""
    stamp = as_of or now_utc()
    zero_quarters = policy.forget.defect.compressed_zero_quarters
    out: list[DemotionDecision] = []
    for row in rows:
        status = str(row.get("status") or "")
        entry_id = str(row.get("entry_id") or "")
        if status == "active":
            surfaces = [str(s) for s in (row.get("affected_surfaces") or [])]
            if not surfaces:
                continue
            known_dead = all(surfaces_alive.get(s) is False for s in surfaces)
            if known_dead:
                out.append(DemotionDecision(entry_id, "defect", status, "retired", "surfaces_all_retired"))
        elif status == "retired":
            last_seen = row.get("last_seen")
            last_hit = row.get("last_hit_at")
            ref = max((d for d in (last_seen, last_hit) if d is not None), default=None)
            zero_days = _days_since(ref, stamp)
            if zero_days >= zero_quarters * QUARTER_DAYS:
                out.append(
                    DemotionDecision(
                        entry_id, "defect", status, "compressed",
                        f"retired_zero_cases_hits_{zero_days:.0f}d>={zero_quarters}q",
                    )
                )
    return out


def plan_elite(
    rows: list[dict[str, Any]],
    has_descendant: set[str],
    policy: HeritagePolicy,
    *,
    as_of: datetime | None = None,
) -> list[DemotionDecision]:
    """精英档案降级计划（格内跌出 top3→archived；archived 满 12 个月且被后代吸收→compressed）。"""
    stamp = as_of or now_utc()
    keep = policy.forget.elite.keep_per_cell or DEFAULT_KEEP
    after_months = policy.forget.elite.compressed_after_months
    out: list[DemotionDecision] = []
    for row in rows:
        status = str(row.get("status") or "")
        entry_id = str(row.get("entry_id") or "")
        rank = row.get("rank_in_cell")
        if status == "active" and isinstance(rank, int) and rank > keep:
            out.append(DemotionDecision(entry_id, "elite", status, "archived", f"rank={rank}>{keep}"))
        elif status == "archived":
            archived_days = _days_since(row.get("updated_at"), stamp)
            absorbed = entry_id in has_descendant
            if archived_days >= after_months * 30 and absorbed:
                out.append(
                    DemotionDecision(
                        entry_id, "elite", status, "compressed",
                        f"archived_{archived_days:.0f}d>={after_months}m_and_absorbed",
                    )
                )
    return out


def plan_criteria(
    rows: list[dict[str, Any]], policy: HeritagePolicy, *, as_of: datetime | None = None
) -> list[DemotionDecision]:
    """判据档案降级计划（still_valid=false→archived；archived 且 venue 跌出最近 N 代→compressed）。"""
    keep = policy.forget.criteria.keep_per_venue or DEFAULT_KEEP
    out: list[DemotionDecision] = []
    for row in rows:
        status = str(row.get("status") or "")
        entry_id = str(row.get("entry_id") or "")
        still_valid = row.get("still_valid")
        venue_rank = row.get("venue_rank")
        if status == "active" and still_valid is False:
            out.append(DemotionDecision(entry_id, "criteria", status, "archived", "still_valid_false"))
        elif status == "archived" and isinstance(venue_rank, int) and venue_rank > keep:
            out.append(
                DemotionDecision(entry_id, "criteria", status, "compressed", f"venue_rank={venue_rank}>{keep}")
            )
    return out


class HeritageForget:
    """月度体检窗执行器：取数 → 纯函数裁定 → store 状态机执行 → 轻事件+报告落盘。"""

    def __init__(
        self,
        store: HeritageStore,
        *,
        policy: HeritagePolicy | None = None,
        state_dir: Path | str | None = None,
        surface_alive: Callable[[str], bool | None] | None = None,
    ) -> None:
        self._store = store
        self._policy: Final = policy or load_policy()
        self.state_dir: Final = Path(state_dir) if state_dir else store.state_dir
        self._surface_alive: Final = surface_alive or default_surface_alive

    # ---------------------------------------------------------------- 取数
    def fetch_defect_rows(self) -> list[dict[str, Any]]:
        schema = self._store.schema
        conn = self._store.read_conn()
        cur = conn.cursor()
        cur.execute(
            f"SELECT e.entry_id, e.status, e.hit_count, e.last_hit_at, e.updated_at, "
            f"d.affected_surfaces, d.last_seen FROM {schema}.ai_heritage_entry e "
            f"JOIN {schema}.ai_heritage_defect d ON d.entry_id = e.entry_id ORDER BY e.entry_id"
        )
        rows = [dict(r) for r in cur.fetchall()]
        for row in rows:
            raw = row.get("affected_surfaces")
            row["affected_surfaces"] = json.loads(raw) if isinstance(raw, str) else list(raw or [])
        return rows

    def fetch_elite_rows(self) -> tuple[list[dict[str, Any]], set[str]]:
        """精英行（格内名次按 score_summary.score 降序，NULLS LAST）+有后代的 parent 集合。"""
        schema = self._store.schema
        conn = self._store.read_conn()
        cur = conn.cursor()
        cur.execute(
            f"SELECT entry_id, status, surface, mechanism_family, updated_at, rank_in_cell FROM ("  # noqa: bare-sql  bare-sql豁免: P1存量伪新增,域内SQL集中通道,§5.160.2专项另列
            f"  SELECT e.entry_id, e.status, e.updated_at, x.surface, x.mechanism_family,"
            f"         row_number() OVER ("
            f"             PARTITION BY x.surface, x.mechanism_family"
            f"             ORDER BY (x.score_summary->>'score')::numeric DESC NULLS LAST, e.created_at"
            f"         ) AS rank_in_cell"
            f"  FROM {schema}.ai_heritage_entry e JOIN {schema}.ai_heritage_elite x ON x.entry_id = e.entry_id"
            f") ranked ORDER BY entry_id"
        )
        rows = [dict(r) for r in cur.fetchall()]
        cur.execute(
            f"SELECT DISTINCT parent_entry_id FROM {schema}.ai_heritage_elite "  # noqa: bare-sql  bare-sql豁免: P1存量伪新增,域内SQL集中通道,§5.160.2专项另列
            f"WHERE parent_entry_id IS NOT NULL"
        )
        parents = {str(r["parent_entry_id"]) for r in cur.fetchall()}
        return rows, parents

    def fetch_criteria_rows(self) -> list[dict[str, Any]]:
        schema = self._store.schema
        conn = self._store.read_conn()
        cur = conn.cursor()
        cur.execute(
            f"SELECT entry_id, status, venue, still_valid, venue_rank FROM ("  # noqa: bare-sql  bare-sql豁免: P1存量伪新增,域内SQL集中通道,§5.160.2专项另列
            f"  SELECT e.entry_id, e.status, c.still_valid, c.venue,"
            f"         row_number() OVER (PARTITION BY c.venue ORDER BY e.created_at DESC) AS venue_rank"
            f"  FROM {schema}.ai_heritage_entry e JOIN {schema}.ai_heritage_criteria c ON c.entry_id = e.entry_id"
            f") ranked ORDER BY entry_id"
        )
        return [dict(r) for r in cur.fetchall()]

    # ---------------------------------------------------------------- 执行
    def run_monthly(self, *, as_of: datetime | None = None, execute: bool = True) -> dict[str, Any]:
        """月度体检窗一次点火：三类裁定→执行→heritage_forget_due 轻事件+报告落盘。

        :param execute: False=干跑（只出裁定报告不落库，供 Owner 人工会话预览）
        """
        stamp = as_of or now_utc()
        surfaces = self._surfaces_alive_map()
        elite_rows, parents = self.fetch_elite_rows()
        decisions = (
            plan_defect(self.fetch_defect_rows(), surfaces, self._policy, as_of=stamp)
            + plan_elite(elite_rows, parents, self._policy, as_of=stamp)
            + plan_criteria(self.fetch_criteria_rows(), self._policy, as_of=stamp)
        )
        executed: list[dict[str, Any]] = []
        skipped: list[dict[str, Any]] = []
        for decision in decisions:
            if not execute:
                executed.append({"entry_id": decision.entry_id, "to": decision.to_status, "dry_run": True})
                continue
            try:
                why = self._store.transition_status(decision.entry_id, decision.to_status, note=decision.why)
                executed.append({"entry_id": decision.entry_id, "to": decision.to_status, "why": why})
            except RuntimeError as exc:  # noqa: BLE001——单条违例不炸整窗，留痕继续
                skipped.append({"entry_id": decision.entry_id, "error": str(exc)[:200]})
        report = {
            "as_of": stamp.isoformat(),
            "decisions": [asdict(d) for d in decisions],
            "executed": executed,
            "skipped": skipped,
            "dry_run": not execute,
        }
        self._emit_forget_event(report)
        self._save_report(report, stamp)
        return report

    def _surfaces_alive_map(self) -> dict[str, bool | None]:
        surfaces: dict[str, bool | None] = {}
        for row in self.fetch_defect_rows():
            for ref in row.get("affected_surfaces") or []:
                if ref not in surfaces:
                    surfaces[str(ref)] = self._surface_alive(str(ref))
        return surfaces

    def _emit_forget_event(self, report: dict[str, Any]) -> None:
        """heritage_forget_due 轻事件（月报/下游消费面；append-only JSONL）。"""
        self.state_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "event": "heritage_forget_due",
            "as_of": report["as_of"],
            "demoted": len(report["executed"]),
            "skipped": len(report["skipped"]),
            "dry_run": report["dry_run"],
        }
        with (self.state_dir / FORGET_EVENT_NAME).open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")

    def _save_report(self, report: dict[str, Any], stamp: datetime) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        path = self.state_dir / f"{FORGET_REPORT_PREFIX}-{stamp.strftime('%Y-%m')}.json"
        path.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
