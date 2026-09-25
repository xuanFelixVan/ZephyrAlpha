# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_heritage
# [MODULE] zephyr.ai_layer.heritage.store
# [DOMAIN] D_GOVERNANCE
# [TESTS] tests/ai_layer/（对应段测试目录）
# [TTL] permanent
# [DEPENDENCIES] zephyr.ai_layer.heritage.policy (HeritagePolicy/load_policy——参数唯一真源);
#                zephyr.ai_layer.intake.dedup (normalize_text/simhash64——指纹算法 SSOT 复用不复制);
#                zephyr.governance.depgraph_schema (get_depgraph_pg_connection 写角色——L2 同款裁定);
#                zephyr.infrastructure.database_service (get_db_service 读角色);
#                zephyr.shared.utils.time_utils (now_utc)
# [CONSUMERS] zephyr.ai_layer.heritage.heritage_events (事件消费落库); zephyr.ai_layer.heritage.forget (降级执行);
#             zephyr.ai_layer.heritage.priors (只读连接); scripts/ai_layer/gen_heritage_dedup_snapshot.py;
#             scripts/ai_layer/gen_heritage_human_digest.py
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] 全部读写经 DatabaseService/depgraph 通道（禁裸 duckdb/psycopg2；写侧直连 depgraph_writer=
#              L2 card_store 同款已登记裁定，DatabaseService 写路径修复后回切）;
#              零物理删除：本模块无 DELETE FROM，遗忘=降 status 只降级压缩（DESIGN §2.8 删除红线）;
#              状态机只降级不越级：elite active→archived→compressed / criteria active→archived→compressed /
#              defect active⇄retired、retired→compressed（compressed 终态，复发 un-retire 仅限 retired）;
#              登记闸（§2.5）纯判据 validate_draft 零 DB 可全枚举；自查重 sha 精确层+simhash 汉明≤3 近似层;
#              hit_count 一律异步聚合回写（红蓝 R1-B7：消费路径只写计数流水，月度体检窗 SUM 落库）;
#              criteria 判据一致性=与 L4 实验卡哈希比对（l4_hash_lookup 可注入；L4 库不可达=fail-closed 拒收）;
#              domain_id 词表真源=L2 ai_intake_domain（应用层校验，domain_lookup 可注入，不建跨 schema FK）;
#              state_dir 全部文件产物（hit 流水/occurrence 流水/snapshot dirty 标记）可注入，测试传 tmp_path
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L7_heredity/DESIGN.md §2.3/§2.5/§2.8（改闸/改状态机先改设计稿）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 登记违规→RegistrationRefused(reason,detail) 机读拒因（缺锚点/占位/自查重/哈希不一致/无案例等）;
#                  非法状态流转→RuntimeError(illegal_transition) fail-closed; entry 不存在→RuntimeError(entry_not_found);
#                  L4 库不可达→拒因 l4_unavailable（绝不放行未核判据）; DB 不可达→异常上抛（不吞不降级）
# [TESTS] tests/ai_layer/heritage/test_heritage_store.py（五类拒收样本/状态机全枚举/零物理删除源扫描/
#         hit 聚合回写轮转/登记→P1 快照 dirty 标记；DB 用例只写 ai_heritage_test_* 临时 schema）
"""store — L7 传承库服务：登记闸 + 三类条目落库 + 状态机降级 + hit_count 月度聚合回写。

设计真源：``docs/_working/ai_layer_vision/L7_heredity/DESIGN.md`` §2.3（H1-H4）/§2.5（登记闸）/
§2.8（遗忘状态机）/§2.4 红蓝 R1-B7（hit_count 异步聚合裁定）。

分层裁定：登记闸判据 ``validate_draft`` 与状态机判据 ``check_status_transition`` 是**纯函数**
（零 DB 依赖，可全枚举单测）；DB 侧只负责查重比对与读写。指纹算法复用 L2 dedup（DESIGN §2.3：
"算法复用 L2 dedup.py 实现"），normalize/simhash 不另设真源。
"""

from __future__ import annotations

import difflib
import hashlib
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Final

from zephyr.ai_layer.heritage.policy import HeritagePolicy, HeritagePolicyError, load_policy
from zephyr.ai_layer.intake.dedup import normalize_text, simhash64
from zephyr.governance.depgraph_schema import get_depgraph_pg_connection
from zephyr.infrastructure.database_service import get_db_service
from zephyr.shared.utils.time_utils import now_utc

log = logging.getLogger(__name__)

__all__: Final = [
    "HeritageDraft",
    "HeritageStore",
    "L4StoreUnavailable",
    "RegistrationRefused",
    "ENTRY_KINDS",
    "STATUS_FLOW",
    "build_text_norm",
    "check_status_transition",
    "recipe_delta_chars",
    "validate_draft",
]

ENTRY_KINDS: Final[frozenset[str]] = frozenset({"elite", "criteria", "defect"})
DEFAULT_SCHEMA: Final = "ai_heritage"
DEFAULT_STATE_DIR: Final = Path(".runtime") / "ai_heritage"
HIT_LOG_NAME: Final = "hit_counts.jsonl"
OCCURRENCE_LOG_NAME: Final = "occurrences.jsonl"
DIRTY_MARKER_NAME: Final = "snapshot_dirty.json"
ENTRY_ID_RE: Final = re.compile(r"^HT-[0-9]{8}-[0-9]{3}$")
SHA256_RE: Final = re.compile(r"^[0-9a-f]{64}$")
PLACEHOLDER_MARKS: Final[frozenset[str]] = frozenset({"待填", "略", "todo", "tbd", "n/a", "none"})
TOOLING_DOMAIN_ID: Final = "tooling"  # 工具域词表锚=L2 T1 域字典 v0（红蓝 R1-B2）

# SQL 集中化常量（§5.160.2 / NO-BARE-SQL 治本）：模板 {s}=schema 占位，经 HeritageStore._sql 注入。
_SQL_L4_CRITERIA_HASH_SELECT = (
    "SELECT criteria_hash FROM ai_compare.ai_comparison_experiment WHERE experiment_id = %s"
)
_SQL_DOMAIN_EXISTS_SELECT = (
    "SELECT 1 FROM ai_intake.ai_intake_domain WHERE domain_id = %s"
)
_SQL_ENTRY_BY_SHA_SELECT = (
    "SELECT entry_id FROM {s}.ai_heritage_entry WHERE content_sha256 = %s"
)
_SQL_SIMHASH_NEAR_SELECT = (
    "SELECT entry_id FROM {s}.ai_heritage_entry "
    "WHERE bit_count(simhash # %(cand)s::bit(64)) <= %(k)s AND status <> 'compressed' "
    "ORDER BY entry_id LIMIT 1"
)
_SQL_ENTRY_ID_LIKE_SELECT = (
    "SELECT entry_id FROM {s}.ai_heritage_entry WHERE entry_id LIKE %s "
    "ORDER BY entry_id DESC LIMIT 1"
)
_SQL_ENTRY_INSERT = (
    "INSERT INTO {s}.ai_heritage_entry (entry_id, entry_kind, title, plain_zh, domain_id, "
    "source_kind, source_ref, text_norm, simhash, content_sha256, created_at, updated_at) "
    "VALUES (%(entry_id)s, %(kind)s, %(title)s, %(plain_zh)s, %(domain_id)s, "
    "%(source_kind)s, %(source_ref)s, %(text_norm)s, %(simhash)s::bit(64), %(sha)s, "
    "%(stamp)s, %(stamp)s)"
)
_SQL_ELITE_INSERT = (
    "INSERT INTO {s}.ai_heritage_elite (entry_id, surface, winner_ref, loser_ref, diff_summary, "
    "evidence_ref, score_summary, mechanism_family, gen, parent_entry_id) "
    "VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s)"
)
_SQL_CRITERIA_INSERT = (
    "INSERT INTO {s}.ai_heritage_criteria (entry_id, experiment_id, criteria_hash, venue, verdict, "
    "simhash, mechanism_family, why_win, still_valid, invalidated_by) "
    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
)
_SQL_DEFECT_INSERT = (
    "INSERT INTO {s}.ai_heritage_defect (entry_id, root_cause, signature, recipe, pattern_norm, "
    "affected_surfaces, tool_id, scene, exclusion_keywords, occurrence_count, first_seen, last_seen, "
    "fused_into_gate) VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s::jsonb, %s, %s, %s, %s)"
)
_SQL_ENTRY_BY_ID_SELECT = (
    "SELECT * FROM {s}.ai_heritage_entry WHERE entry_id = %s"
)
_SQL_ENTRY_STATUS_UPDATE = (
    "UPDATE {s}.ai_heritage_entry SET status = %s, updated_at = now() WHERE entry_id = %s"
)
_SQL_DEFECT_OCCURRENCE_UPDATE = (
    "UPDATE {s}.ai_heritage_defect SET occurrence_count = occurrence_count + 1, "
    "last_seen = %s WHERE entry_id = %s RETURNING occurrence_count"
)
_SQL_ENTRY_HIT_UPDATE = (
    "UPDATE {s}.ai_heritage_entry SET hit_count = hit_count + %s, "
    "last_hit_at = %s, updated_at = now() WHERE entry_id = %s"
)
_SQL_DEFECT_FACES_SELECT = (
    "SELECT e.entry_id, e.title, e.plain_zh, e.text_norm FROM {s}.ai_heritage_entry e "
    "JOIN {s}.ai_heritage_defect d ON d.entry_id = e.entry_id WHERE e.status = 'active' "
    "ORDER BY e.entry_id"
)
_SQL_ELITE_FACES_SELECT = (
    "SELECT entry_id, text_norm FROM ("
    "  SELECT e.entry_id, e.text_norm, row_number() OVER ("
    "     PARTITION BY x.surface, x.mechanism_family ORDER BY e.created_at, e.entry_id) AS rn"
    "  FROM {s}.ai_heritage_entry e"
    "  JOIN {s}.ai_heritage_elite x ON x.entry_id = e.entry_id"
    "  WHERE e.status = 'active'"
    ") ranked WHERE rn <= %(keep)s ORDER BY entry_id"
)

# 状态机合法流转表（DESIGN §2.8 三类差异化；compressed 终态零出边）
STATUS_FLOW: Final[dict[str, dict[str, frozenset[str]]]] = {
    "elite": {"active": frozenset({"archived"}), "archived": frozenset({"compressed"})},
    "criteria": {"active": frozenset({"archived"}), "archived": frozenset({"compressed"})},
    "defect": {
        "active": frozenset({"retired"}),
        "retired": frozenset({"active", "compressed"}),
    },
}

L4HashLookup = Callable[[str], str | None]
DomainLookup = Callable[[str], bool]


class L4StoreUnavailable(LookupError):
    """ai_compare 实验卡库不可达（schema 未部署/连接失败）——fail-closed 信号。"""


class RegistrationRefused(Exception):
    """登记闸拒收（reason 机读枚举，detail 人读补充）。

    reason 词表：missing_source_anchor / bad_source_ref_format / placeholder_plain_zh /
    incomplete / no_real_case / recipe_repeats_root_cause / bad_pattern_slug /
    tool_fields_missing / unknown_domain / duplicate_of / hash_mismatch /
    experiment_card_not_found / l4_unavailable
    """

    def __init__(self, reason: str, detail: str = "") -> None:
        super().__init__(f"{reason}:{detail}" if detail else reason)
        self.reason = reason
        self.detail = detail


@dataclass(frozen=True)
class HeritageDraft:
    """登记草稿（register() 唯一入参形态，kind 判别键决定哪些字段必填）。"""

    entry_kind: str
    title: str
    plain_zh: str
    domain_id: str
    source_kind: str
    source_ref: str
    # ---- elite 专用 ----
    surface: str | None = None
    winner_ref: str | None = None
    loser_ref: str | None = None
    diff_summary: str | None = None
    evidence_ref: str | None = None
    score_summary: dict[str, Any] = field(default_factory=dict)
    mechanism_family: str | None = None
    gen: int = 1
    parent_entry_id: str | None = None
    # ---- criteria 专用 ----
    experiment_id: str | None = None
    criteria_hash: str | None = None
    venue: str | None = None
    verdict: str | None = None
    why_win: str | None = None
    still_valid: bool = True
    invalidated_by: str | None = None
    # ---- defect 专用 ----
    root_cause: str | None = None
    signature: str | None = None
    recipe: str | None = None
    pattern_norm: str | None = None
    affected_surfaces: tuple[str, ...] = ()
    tool_id: str | None = None
    scene: str | None = None
    exclusion_keywords: tuple[str, ...] = ()
    fused_into_gate: str | None = None


def build_text_norm(draft: HeritageDraft) -> str:
    """归一化文本（H1.text_norm；simhash/content_sha256 的输入；title+核心字段拼接）。"""
    parts: list[str] = [draft.title]
    if draft.entry_kind == "elite":
        parts += [draft.diff_summary or "", draft.winner_ref or "", draft.evidence_ref or ""]
    elif draft.entry_kind == "criteria":
        parts += [draft.why_win or "", draft.experiment_id or "", draft.verdict or ""]
    elif draft.entry_kind == "defect":
        parts += [draft.root_cause or "", draft.signature or "", draft.recipe or ""]
    return normalize_text(" ".join(p for p in parts if p))


def recipe_delta_chars(root_cause: str, recipe: str) -> int:
    """配方相对根因的差异字符数（SequenceMatcher 匹配块之外的 recipe 字符量）。

    判据=DESIGN §2.5"recipe≠root_cause 复读（≥20 字差异校验）"：差异量不足即判复读。
    """
    matcher = difflib.SequenceMatcher(None, normalize_text(root_cause), normalize_text(recipe))
    matched = sum(block.size for block in matcher.get_matching_blocks())
    return len(normalize_text(recipe)) - matched


def _check_source_anchor(draft: HeritageDraft, policy: HeritagePolicy) -> None:
    """闸1 来源可溯：双非空+前缀白名单。"""
    if not draft.source_kind or not str(draft.source_ref or "").strip():
        raise RegistrationRefused("missing_source_anchor", f"{draft.source_kind}/{draft.source_ref}")
    ref = str(draft.source_ref).strip()
    if not any(ref.startswith(prefix) for prefix in policy.registration.source_ref_prefixes):
        raise RegistrationRefused("bad_source_ref_format", ref)


def _check_plain_zh(draft: HeritageDraft, policy: HeritagePolicy) -> None:
    """闸5 plain_zh 非占位：≥N 字且非'待填/略'。"""
    text = str(draft.plain_zh or "").strip()
    if len(text) < policy.registration.min_plain_zh_chars:
        raise RegistrationRefused(
            "placeholder_plain_zh", f"len={len(text)}<{policy.registration.min_plain_zh_chars}"
        )
    if text.lower() in PLACEHOLDER_MARKS or text.startswith("待填"):
        raise RegistrationRefused("placeholder_plain_zh", text[:20])


def _check_elite(draft: HeritageDraft, policy: HeritagePolicy) -> None:
    """闸2 类内完备（elite）：winner_ref+diff_summary≥30 字+evidence_ref。"""
    if not str(draft.winner_ref or "").strip():
        raise RegistrationRefused("incomplete", "elite.winner_ref")
    if not str(draft.evidence_ref or "").strip():
        raise RegistrationRefused("incomplete", "elite.evidence_ref")
    if len(str(draft.diff_summary or "").strip()) < policy.registration.min_narrative_chars:
        raise RegistrationRefused("incomplete", f"elite.diff_summary<{policy.registration.min_narrative_chars}")
    if draft.parent_entry_id and not ENTRY_ID_RE.match(draft.parent_entry_id):
        raise RegistrationRefused("bad_source_ref_format", f"parent:{draft.parent_entry_id}")


def _check_criteria(draft: HeritageDraft, policy: HeritagePolicy) -> None:
    """闸2 类内完备（criteria）：experiment_id+criteria_hash+why_win≥30 字。"""
    if not str(draft.experiment_id or "").strip():
        raise RegistrationRefused("incomplete", "criteria.experiment_id")
    hash_text = str(draft.criteria_hash or "").strip().lower()
    if not SHA256_RE.match(hash_text):
        raise RegistrationRefused("incomplete", "criteria.criteria_hash(sha256)")
    if len(str(draft.why_win or "").strip()) < policy.registration.min_narrative_chars:
        raise RegistrationRefused("incomplete", f"criteria.why_win<{policy.registration.min_narrative_chars}")


def _check_defect_three_fields(draft: HeritageDraft, policy: HeritagePolicy) -> None:
    """三字段全非空+配方非复读（DESIGN §2.5 闸2 defect 前半）。"""
    for name in ("root_cause", "signature", "recipe"):
        if not str(getattr(draft, name) or "").strip():
            raise RegistrationRefused("incomplete", f"defect.{name}")
    delta = recipe_delta_chars(draft.root_cause or "", draft.recipe or "")
    if delta < policy.registration.min_recipe_delta_chars:
        raise RegistrationRefused(
            "recipe_repeats_root_cause", f"delta={delta}<{policy.registration.min_recipe_delta_chars}"
        )


def _check_defect(draft: HeritageDraft, policy: HeritagePolicy) -> None:
    """闸2+闸3 类内完备/无案例不入册（defect）：三字段+案例通道白名单+词表/受影响面/工具域。"""
    _check_defect_three_fields(draft, policy)
    if draft.source_kind not in policy.registration.defect_source_kinds:
        raise RegistrationRefused(
            "no_real_case", f"source_kind={draft.source_kind} 不在案例通道白名单"
        )
    slug = str(draft.pattern_norm or "").strip()
    if not policy.registration.pattern_slug_re.match(slug):
        raise RegistrationRefused("bad_pattern_slug", slug)
    if not draft.affected_surfaces:
        raise RegistrationRefused("incomplete", "defect.affected_surfaces")
    if draft.domain_id == TOOLING_DOMAIN_ID and (
        not str(draft.tool_id or "").strip() or not str(draft.scene or "").strip()
    ):
        # 工具域条目必填 tool_id/scene（红蓝 R1-B2，DESIGN §2.3 H4）
        raise RegistrationRefused("tool_fields_missing", "tooling 域缺 tool_id/scene")


def validate_draft(draft: HeritageDraft, policy: HeritagePolicy) -> str:
    """登记闸纯判据（DESIGN §2.5 五闸中不依赖 DB 的四闸）。通过返回 text_norm。

    :raises RegistrationRefused: 任一闸不过即拒（拒因机读）
    """
    if draft.entry_kind not in ENTRY_KINDS:
        raise RegistrationRefused("incomplete", f"entry_kind={draft.entry_kind}")
    if not str(draft.title or "").strip():
        raise RegistrationRefused("incomplete", "title")
    _check_source_anchor(draft, policy)
    _check_plain_zh(draft, policy)
    if draft.entry_kind == "elite":
        _check_elite(draft, policy)
    elif draft.entry_kind == "criteria":
        _check_criteria(draft, policy)
    else:
        _check_defect(draft, policy)
    text_norm = build_text_norm(draft)
    if not text_norm:
        raise RegistrationRefused("incomplete", "text_norm_empty")
    return text_norm


def check_status_transition(kind: str, current: str, target: str) -> tuple[bool, str]:
    """遗忘状态机合法性纯判据（DESIGN §2.8；compressed 终态；只降级+defect 可 un-retire）。"""
    if kind not in STATUS_FLOW:
        return False, f"unknown_kind:{kind}"
    if current == target:
        if current == "compressed" or current in STATUS_FLOW[kind]:
            return True, "noop_same_status"
        return False, f"unknown_state:{kind}:{current}"
    if current == "compressed":
        return False, "compressed_is_terminal"
    if current not in STATUS_FLOW[kind] or target not in STATUS_FLOW[kind].get(current, frozenset()):
        return False, f"illegal_transition:{current}->{target}"
    return True, f"demote:{current}->{target}"


def _default_l4_hash_lookup(experiment_id: str) -> str | None:
    """L4 实验卡判据哈希查询（ai_compare.ai_comparison_experiment 只读）。

    :returns: 卡存在=criteria_hash；卡不存在=None
    :raises L4StoreUnavailable: schema/表未部署或查询失败（fail-closed 信号）
    """
    from psycopg2 import OperationalError  # noqa: PLC0415——局部依赖，仅在异常翻译时需要

    conn = get_depgraph_pg_connection(read_only=True)
    try:
        cur = conn.cursor()
        cur.execute(
            _SQL_L4_CRITERIA_HASH_SELECT,
            (experiment_id,),
        )
        row = cur.fetchone()
    except OperationalError as exc:
        raise L4StoreUnavailable(f"ai_compare 不可达：{exc}") from exc
    if not row:
        return None
    value = row["criteria_hash"] if isinstance(row, dict) else row[0]
    return str(value).strip() if value is not None else None


def _default_domain_lookup(domain_id: str) -> bool:
    """L2 域字典词表校验（ai_intake.ai_intake_domain 只读；不建跨 schema FK 的应用层校验）。"""
    conn = get_depgraph_pg_connection(read_only=True)
    cur = conn.cursor()
    cur.execute(_SQL_DOMAIN_EXISTS_SELECT, (domain_id,))
    return bool(cur.fetchone())


class _HeritageStoreRegistrationMixin:
    """登记入库组 Mixin：register 全闸过闸 + 自查重 + 三类扩展表同事务落库。

    方法体自 :class:`HeritageStore` 逐字节迁移（NO-GOD-CLASS 拆分）；
    宿主提供 .schema/_policy/_domain_ok/_l4_lookup/read_conn/write_conn/_sql/_row_value 承载。
    """

    # ---------------------------------------------------------------- 登记闸（DB 侧）
    def register(self, draft: HeritageDraft, *, as_of: datetime | None = None) -> str:
        """登记一条传承条目（§2.5 全闸过后落 H1+扩展表）。返回 entry_id。

        :param as_of: 时间注入点（first_seen/last_seen/occurrence 基准；缺省 now_utc）
        :raises RegistrationRefused: 任一闸不过（拒因机读，含 duplicate_of=<entry_id>）
        """
        stamp = as_of or now_utc()
        text_norm = validate_draft(draft, self._policy)
        if draft.domain_id and not self._domain_ok(draft.domain_id):
            raise RegistrationRefused("unknown_domain", draft.domain_id)
        content_sha = hashlib.sha256(text_norm.encode("utf-8")).hexdigest()
        simhash = simhash64(text_norm)
        seen = self._find_similar(content_sha, simhash)
        if seen is not None:
            raise RegistrationRefused("duplicate_of", seen)
        if draft.entry_kind == "criteria":
            self.verify_criteria_hash(draft)
        entry_id = self._next_entry_id(stamp)
        self._insert(entry_id, draft, text_norm, content_sha, simhash, stamp)
        self.mark_snapshot_dirty(f"register:{entry_id}")
        log.info("heritage 登记成功：%s kind=%s pattern=%s", entry_id, draft.entry_kind, draft.pattern_norm)
        return entry_id

    def _find_similar(self, content_sha: str, simhash: int) -> str | None:
        """闸4 自查重：content_sha256 精确层+simhash 全库汉明≤k 近似层。返回既有 entry_id 或 None。"""
        conn = self.read_conn()
        cur = conn.cursor()
        cur.execute(
            self._sql(_SQL_ENTRY_BY_SHA_SELECT),
            (content_sha,),
        )
        row = cur.fetchone()
        if row:
            return self._row_value(row, "entry_id")
        k = self._policy.registration.simhash_hamming_max
        cur.execute(
            self._sql(_SQL_SIMHASH_NEAR_SELECT),
            {"cand": format(simhash, "064b"), "k": k},
        )
        row = cur.fetchone()
        return self._row_value(row, "entry_id") if row else None

    def verify_criteria_hash(self, draft: HeritageDraft) -> None:
        """闸5 判据一致性：与 L4 实验卡哈希比对（卡缺=L4 不可达均 fail-closed 拒收）。

        公共方法（纯闸面零前置 DB——自查重之外的独立闸，可单测直调）。
        """
        try:
            real_hash = self._l4_lookup(str(draft.experiment_id))
        except L4StoreUnavailable as exc:
            raise RegistrationRefused("l4_unavailable", str(exc)) from exc
        if real_hash is None:
            raise RegistrationRefused("experiment_card_not_found", str(draft.experiment_id))
        if str(real_hash).strip().lower() != str(draft.criteria_hash).strip().lower():
            raise RegistrationRefused("hash_mismatch", str(draft.experiment_id))

    def _next_entry_id(self, stamp: datetime) -> str:
        """HT-<yyyymmdd>-<NNN> 当日序号（kind 无关统一编号；冲突由 PK 兜底重试由调用方处置）。"""
        day = stamp.strftime("%Y%m%d")
        conn = self.read_conn()
        cur = conn.cursor()
        cur.execute(
            self._sql(_SQL_ENTRY_ID_LIKE_SELECT),
            (f"HT-{day}-%",),
        )
        row = cur.fetchone()
        last_seq = 0
        if row:
            raw = self._row_value(row, "entry_id")
            last_seq = int(str(raw).rsplit("-", 1)[-1])
        return f"HT-{day}-{last_seq + 1:03d}"

    def _insert(
        self, entry_id: str, draft: HeritageDraft, text_norm: str, content_sha: str, simhash: int,
        stamp: datetime,
    ) -> None:
        """H1+扩展表同事务落库（CHECK 值域由 DDL 兜底，应用闸已前置）。"""
        conn = self.write_conn()
        iso_stamp = stamp.isoformat()
        cur = conn.cursor()
        try:
            cur.execute(
                self._sql(_SQL_ENTRY_INSERT),
                {
                    "entry_id": entry_id,
                    "kind": draft.entry_kind,
                    "title": draft.title,
                    "plain_zh": draft.plain_zh,
                    "domain_id": draft.domain_id,
                    "source_kind": draft.source_kind,
                    "source_ref": draft.source_ref,
                    "text_norm": text_norm,
                    "simhash": format(simhash, "064b"),
                    "sha": content_sha,
                    "stamp": iso_stamp,
                },
            )
            if draft.entry_kind == "elite":
                self._insert_elite(cur, entry_id, draft)
            elif draft.entry_kind == "criteria":
                self._insert_criteria(cur, entry_id, draft)
            else:
                self._insert_defect(cur, entry_id, draft, iso_stamp)
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    def _insert_elite(self, cur: Any, entry_id: str, draft: HeritageDraft) -> None:
        cur.execute(
            self._sql(_SQL_ELITE_INSERT),
            (
                entry_id,
                draft.surface,
                draft.winner_ref,
                draft.loser_ref,
                draft.diff_summary,
                draft.evidence_ref,
                json.dumps(draft.score_summary, ensure_ascii=False),
                draft.mechanism_family,
                draft.gen,
                draft.parent_entry_id,
            ),
        )

    def _insert_criteria(self, cur: Any, entry_id: str, draft: HeritageDraft) -> None:
        cur.execute(
            self._sql(_SQL_CRITERIA_INSERT),
            (
                entry_id,
                draft.experiment_id,
                str(draft.criteria_hash).strip().lower(),
                draft.venue,
                draft.verdict,
                None,
                draft.mechanism_family,
                draft.why_win,
                bool(draft.still_valid),
                draft.invalidated_by,
            ),
        )

    def _insert_defect(self, cur: Any, entry_id: str, draft: HeritageDraft, iso_stamp: str) -> None:
        cur.execute(
            self._sql(_SQL_DEFECT_INSERT),
            (
                entry_id,
                draft.root_cause,
                draft.signature,
                draft.recipe,
                draft.pattern_norm,
                json.dumps(list(draft.affected_surfaces), ensure_ascii=False),
                draft.tool_id,
                draft.scene,
                json.dumps(list(draft.exclusion_keywords), ensure_ascii=False),
                1,
                iso_stamp,
                iso_stamp,
                draft.fused_into_gate,
            ),
        )


class _HeritageStoreQueriesMixin:
    """查询组 Mixin：按 entry_id 反查 / 轻量状态读 / 快照面提取（T4 源）。

    方法体自 :class:`HeritageStore` 逐字节迁移（NO-GOD-CLASS 拆分）。
    """

    # ---------------------------------------------------------------- 读
    def get(self, entry_id: str) -> dict[str, Any] | None:
        """按 entry_id 反查全量（含 compressed——DESIGN §2.8：DB 不删，10 年内可反查）。"""
        conn = self.read_conn()
        cur = conn.cursor()
        cur.execute(
            self._sql(_SQL_ENTRY_BY_ID_SELECT), (entry_id,)
        )
        row = cur.fetchone()
        if not row:
            return None
        base = dict(row) if isinstance(row, dict) else {d.name: v for d, v in zip(cur.description, row)}
        base["simhash"] = int(str(base.get("simhash")), 2) if base.get("simhash") is not None else None
        return base

    def status_of(self, entry_id: str) -> str | None:
        """轻量读当前状态（状态机流转前置检查）。"""
        entry = self.get(entry_id)
        return str(entry["status"]) if entry else None

    # ---------------------------------------------------------------- 快照面提取（T4 源）
    def snapshot_faces(self) -> dict[str, list[dict[str, Any]]]:
        """入快照面（DESIGN §2.4）：V2 缺陷全量+V1 精英每格 top3。

        返回 {"defect": [(ref_key, text_norm)], "elite": [...]}——ref_key=HT:<entry_id>。
        """
        conn = self.read_conn()
        cur = conn.cursor()
        faces: dict[str, list[dict[str, Any]]] = {}
        cur.execute(
            self._sql(_SQL_DEFECT_FACES_SELECT)
        )
        faces["defect"] = [
            {"ref_key": f"HT:{self._row_value(r, 'entry_id')}", "text_norm": self._row_value(r, "text_norm")}
            for r in cur.fetchall()
        ]
        keep = self._policy.forget.elite.keep_per_cell
        cur.execute(
            self._sql(_SQL_ELITE_FACES_SELECT),
            {"keep": keep},
        )
        faces["elite"] = [
            {"ref_key": f"HT:{self._row_value(r, 'entry_id')}", "text_norm": self._row_value(r, "text_norm")}
            for r in cur.fetchall()
        ]
        return faces


class _HeritageStoreLifecycleMixin:
    """遗忘降级 + 事件流水 + 快照留痕组 Mixin：状态机流转 / occurrence、hit 流水 / 脏标记。

    方法体自 :class:`HeritageStore` 逐字节迁移（NO-GOD-CLASS 拆分）。
    """

    # ---------------------------------------------------------------- 状态机
    def transition_status(self, entry_id: str, target: str, *, note: str = "") -> str:
        """遗忘状态机流转（判据=check_status_transition 纯函数，非法即 RuntimeError fail-closed）。"""
        entry = self.get(entry_id)
        if entry is None:
            raise RuntimeError(f"entry_not_found:{entry_id}")
        kind = str(entry["entry_kind"])
        current = str(entry["status"])
        ok, why = check_status_transition(kind, current, target)
        if not ok:
            raise RuntimeError(f"illegal_transition:{entry_id}:{why}")
        if why == "noop_same_status":
            return why
        conn = self.write_conn()
        cur = conn.cursor()
        try:
            cur.execute(
                self._sql(_SQL_ENTRY_STATUS_UPDATE),
                (target, entry_id),
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        log.info("heritage 状态降级：%s %s->%s note=%s", entry_id, current, target, note)
        self.mark_snapshot_dirty(f"transition:{entry_id}:{target}")
        return why

    # ---------------------------------------------------------------- occurrence / hit 流水
    def record_occurrence(self, entry_id: str, source_ref: str, *, as_of: datetime | None = None) -> int:
        """同坑复发归并（§2.5 闸4：同 pattern 累加 occurrence_count 不新登记）。

        source_ref 追加留痕在 occurrence 流水 JSONL（H4 无 source_refs 列的 v0 落位，append-only）。
        """
        stamp = (as_of or now_utc()).isoformat()
        conn = self.write_conn()
        cur = conn.cursor()
        try:
            cur.execute(
                self._sql(_SQL_DEFECT_OCCURRENCE_UPDATE),
                (stamp, entry_id),
            )
            row = cur.fetchone()
            if not row:
                raise RuntimeError(f"entry_not_found:{entry_id}")
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        self._append_log(OCCURRENCE_LOG_NAME, {"entry_id": entry_id, "source_ref": source_ref, "ts": stamp})
        count = row[0] if isinstance(row, (list, tuple)) else row["occurrence_count"]
        self.mark_snapshot_dirty(f"occurrence:{entry_id}")
        return int(count)

    def record_hit(self, entry_id: str, channel: str, *, as_of: datetime | None = None) -> None:
        """消费路径计数流水（红蓝 R1-B7：只追加 JSONL，不回写 DB——月度聚合窗统一 SUM 落库）。"""
        self._append_log(
            HIT_LOG_NAME, {"entry_id": entry_id, "channel": channel, "ts": (as_of or now_utc()).isoformat()}
        )

    def aggregate_hits_monthly(self, *, as_of: datetime | None = None) -> dict[str, int]:
        """月度体检窗：流水 SUM 一次性回写 H1.hit_count/last_hit_at，已处理流水轮转归档。"""
        stamp = as_of or now_utc()
        log_path = self.state_dir / HIT_LOG_NAME
        if not log_path.exists():
            return {"aggregated": 0}
        totals: dict[str, int] = {}
        last_ts: dict[str, str] = {}
        for line in log_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            row = json.loads(stripped)
            eid = str(row.get("entry_id") or "")
            if not eid:
                continue
            totals[eid] = totals.get(eid, 0) + 1
            prev = last_ts.get(eid)
            if prev is None or str(row.get("ts") or "") > prev:
                last_ts[eid] = str(row.get("ts") or "")
        if totals:
            conn = self.write_conn()
            cur = conn.cursor()
            try:
                for eid, delta in totals.items():
                    cur.execute(
                        self._sql(_SQL_ENTRY_HIT_UPDATE),
                        (delta, last_ts[eid], eid),
                    )
                conn.commit()
            except Exception:
                conn.rollback()
                raise
        archive = self.state_dir / f"hit_counts-{stamp.strftime('%Y-%m')}.jsonl"
        archive.parent.mkdir(parents=True, exist_ok=True)
        with archive.open("a", encoding="utf-8") as handle:
            handle.write(log_path.read_text(encoding="utf-8"))
        log_path.unlink()
        log.info("heritage hit 聚合回写：%d 条目", len(totals))
        return {"aggregated": len(totals)}

    # ---------------------------------------------------------------- 文件留痕
    def _append_log(self, name: str, payload: dict[str, Any]) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        with (self.state_dir / name).open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")

    def mark_snapshot_dirty(self, reason: str) -> None:
        """登记/降级后置快照脏标记（T4 ref_family='L7' 刷新触发源，DESIGN §2.4）。"""
        self.state_dir.mkdir(parents=True, exist_ok=True)
        marker = {"dirty_at": now_utc().isoformat(), "reason": reason}
        (self.state_dir / DIRTY_MARKER_NAME).write_text(
            json.dumps(marker, ensure_ascii=False), encoding="utf-8"
        )

    def dirty_since(self) -> datetime | None:
        """读快照脏标记时间（生成器 --if-dirty 判据；无标记=None）。"""
        path = self.state_dir / DIRTY_MARKER_NAME
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return datetime.fromisoformat(str(data.get("dirty_at")))
        except (ValueError, OSError):
            return None

    def clear_dirty_marker(self) -> None:
        """快照刷新成功后清脏标记（仅删标记文件，非传承条目物理删除）。"""
        path = self.state_dir / DIRTY_MARKER_NAME
        if path.exists():
            path.unlink()

    # ---------------------------------------------------------------- 快照辅助
    def stale_days(self, *, as_of: datetime | None = None) -> int | None:
        """快照脏标记距今天数（月度兜底刷新判据；无标记=None）。"""
        dirty_at = self.dirty_since()
        if dirty_at is None:
            return None
        return int(((as_of or now_utc()) - dirty_at).total_seconds() // 86400)

    def retention_horizon(self) -> timedelta:
        """传承条目反查保留期（DESIGN §2.8：compressed 条目 10 年内可反查）。"""
        return timedelta(days=3650)


class HeritageStore(
    _HeritageStoreRegistrationMixin,
    _HeritageStoreQueriesMixin,
    _HeritageStoreLifecycleMixin,
):
    """L7 传承库服务：登记闸 + 三类条目 + 遗忘状态机 + hit 流水月度聚合（全部经 depgraph 通道）。

    NO-GOD-CLASS 拆分：方法按职责迁至同文件三个 Mixin（登记入库 / 查询 /
    遗忘降级+事件+留痕），本类继承获得，对外类型与用法零变化。
    本类体仅保留连接管理（read_conn/write_conn/close/_sql）与共享 helper（_row_value）。
    """

    def __init__(
        self,
        schema: str = DEFAULT_SCHEMA,
        *,
        service: Any | None = None,
        state_dir: Path | str | None = None,
        l4_hash_lookup: L4HashLookup | None = None,
        domain_lookup: DomainLookup | None = None,
        policy: HeritagePolicy | None = None,
    ) -> None:
        if not re.match(r"^ai_heritage(_test_[a-z0-9_]+)?$", schema or ""):
            raise ValueError(f"schema 名不合规：{schema!r}（只许 ai_heritage / ai_heritage_test_*）")
        self.schema: Final = schema
        self._svc = service or get_db_service()
        self.state_dir: Final = Path(state_dir) if state_dir else DEFAULT_STATE_DIR
        self._l4_lookup: Final = l4_hash_lookup or _default_l4_hash_lookup
        self._domain_ok: Final = domain_lookup or _default_domain_lookup
        self._policy: Final = policy or load_policy()
        self._write_conn: Any | None = None

    # ---------------------------------------------------------------- 连接
    def read_conn(self) -> Any:
        """只读连接（读路径唯一真源，read_only=True）。"""
        return self._svc.get_depgraph_conn(read_only=True)

    def write_conn(self) -> Any:
        """写连接（depgraph_writer 角色；L2 card_store 同款裁定，见其头注 req_ailayerB_03）。"""
        if self._write_conn is None or self._write_conn.closed:
            self._write_conn = get_depgraph_pg_connection(read_only=False, autocommit=True)
        return self._write_conn

    def close(self) -> None:
        if self._write_conn is not None and not self._write_conn.closed:
            self._write_conn.close()
        self._write_conn = None

    def _sql(self, template: str) -> str:
        return template.format(s=self.schema)

    @staticmethod
    def _row_value(row: Any, key: str) -> Any:
        return row[key] if isinstance(row, dict) else row[0]


def policy_or_raise(path: Path | str | None = None) -> HeritagePolicy:
    """显式装载入口（配置缺位=HeritagePolicyError，比 import 期隐式加载更显眼）。"""
    try:
        return load_policy(path)
    except HeritagePolicyError:
        raise
