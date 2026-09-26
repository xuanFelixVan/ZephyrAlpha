# [BLUEPRINT] MOD-CHAINPILE-METAQ | docs/_working/chain_piling_campaign/infra_mining/10_intake_gate_design.md | §7 写入 API 契约
# [MODULE] zephyr.governance.meta_question.meta_question_registry
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.meta_question.exam_ops（考试生命周期簇 Mixin/异常/词表常量回 import，NO-GOD-CLASS 拆分件）; zephyr.governance.depgraph_schema (get_depgraph_pg_connection, 惰性默认); zephyr.shared.utils.time_utils (now_utc); zephyr.shared.io.file_utils（不经本模块——JSONL 为追加账非热文件，照 intake journal 先例 append）
# [CONSUMERS] zephyr.governance.meta_question.snapshot（同表只读侧）; 四件套姊妹件（模板生成器/未答看板/考试回填闭环，后续接线批）; tests/governance/meta_question/test_registry.py（mock 连接注入）
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] register 校验顺序=10§7.1（A 级必填→layer 枚举→五要素机检→查重→净零→q_id 机生），失败即短路抛 QuestionValidationError(snake_case subcode)；
#              状态流转只走 13§1.5+10§7.4 合法边（LEGAL_TRANSITIONS 硬编码，含挂起→registered 唤醒边与 in_exam/answered→挂起边；任意非终态→merged/retired 通配边）；
#              PG 行写一律乐观锁 UPDATE...WHERE version=:expected，零行命中=VersionConflictError（20§3.2，禁 SELECT 后裸 UPDATE）；
#              审计双轨（20§2.2）：meta_question_audit 行 + audit_jsonl_path JSONL 追加；what 全部取自 20§2.1 四族 SSOT 词表（AUDIT_WHAT_VOCAB），禁另立枚举；
#              时间一律 now_utc()（UTC aware timestamptz 口径），禁裸 datetime.now()；
#              认领鉴权：活跃租约内 transition/回写须 claimed_by==actor，Max/Owner 角色可越过（10§7.4①/13§1 回写鉴权句）；
#              五要素机检为真检口径（WO-001）：要素1/要素5 命中 W4 机器可读册、要素3 命中七层枚举+functional_domain_registry，
#                判定不过的要素逐项附 degraded_check 事件（10§3 降级口径声明；册缺失/漂移=fail-closed 全要素降级，禁读不到就当过）；
#              连接注入：构造参数 get_conn(*, read_only)（默认惰性 get_depgraph_pg_connection），测试可注入 mock；
#              q_id 墓碑不复用：分配=全表 max+1 连号，永不回收（纪要§7）
# [MODIFY-GUARD] docs/_working/chain_piling_campaign/infra_mining/10_intake_gate_design.md §7 + 13_exam_backfill_loop_design.md §1.5 + 20_management_policy.md §2/§3（改契约先改设计稿）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 全部校验失败=QuestionValidationError(subcode, details)（subcode 机读 snake_case，对齐 10§7.2 错误码表）；
#                  乐观锁零行命中=VersionConflictError(q_id, expected_version)（调用方重读重放，20§3.2）；
#                  连接失败/SQL 错误=原样上抛（fail-closed，禁降级直写）；register 校验失败零副作用（不产生任何写）；
#                  audit what 不在 SSOT 词表=ValueError（写入前硬拦，防词表漂移）
# [TESTS] tests/governance/meta_question/test_registry.py（SQLite mock 连接注入；JSONL/输出全走 tmp_path，禁写生产路径）
# [TTL] permanent
"""registry — meta_question_registry 写入 API（原问题中央登记表唯一写入口）。

设计真源：``docs/_working/chain_piling_campaign/infra_mining/10_intake_gate_design.md`` §7
（校验顺序/错误码/审计事件/状态流转端点）+ ``13_exam_backfill_loop_design.md`` §1.5（状态机）
+ ``20_management_policy.md`` §2/§3（审计账本/乐观锁）。

用法（生产，PG 同实例）::

    from zephyr.governance.meta_question import MetaQuestionRegistry

    reg = MetaQuestionRegistry(
        schema="meta_question",
        audit_jsonl_path=".runtime/chain_piling/meta_question_audit.jsonl",
    )
    q_id = reg.register(question_dict, actor="st-chainpile-20260922|AI")
    reg.transition(q_id, "mining", actor=..., evidence=...)

用法（测试，mock 连接注入）::

    reg = MetaQuestionRegistry(schema="main", get_conn=fake_conn_factory,
                               audit_jsonl_path=tmp_path / "audit.jsonl")

校验顺序（10§7.1，失败即短路）::

    A 级字段完备 → layer 枚举 → 五要素机检（真检：命中册面即放行，未命中项留降级痕）→ 查重 → 净零声明 → q_id 机生 → 写入+审计

错误码（10§7.2 全集内取用，机读 snake_case）::

    field_missing:<f> / layer_invalid / frequency_not_in_enum / status_invalid /
    data_sources_empty / exam_plan_no_threshold / event_source_ref_missing /
    consumer_unresolvable / pit_proof_missing / dup_high_similarity /
    net_zero_note_missing / qid_not_found / illegal_transition / claim_mismatch /
    claim_conflict / claim_not_held / release_not_claimant / qid_alloc_failed
# target: src/zephyr/governance/meta_question/registry.py (docstring 1324 字, 32 函数, 0 步骤)
# [ALGO_FLOW] external: docs/03_modules/_domain_governance/algo_flow/registry.yaml
"""

from __future__ import annotations

import logging
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Final

from zephyr.governance.meta_question.exam_ops import (
    _MAIN_COLUMNS,
    AUDIT_WHAT_VOCAB,
    BYPASS_ACTORS,
    LEGAL_TRANSITIONS,
    MetaQuestionAuditEvent,
    MetaQuestionExamMixin,
    QuestionValidationError,
    VersionConflictError,
    _as_json,
)
from zephyr.shared.io.yaml_utils import load_vocabulary_values
from zephyr.shared.utils.time_utils import now_utc

log = logging.getLogger(__name__)

__all__: Final = [
    "AUDIT_WHAT_VOCAB",
    "BYPASS_ACTORS",
    "LEGAL_TRANSITIONS",
    "MetaQuestionRegistry",
    "QuestionValidationError",
    "VALID_FREQUENCIES",
    "VALID_LAYERS",
    "VALID_OUTCOMES",
    "VALID_STATUSES",
    "VersionConflictError",
    "normalize_title",
]

# ---------------------------------------------------------------------------
# 词表与枚举（SSOT：20_management_policy.md §2.1 / 10_intake_gate_design.md §3；
# 考试簇常量见 exam_ops.py——本模块经 import 回用保持兼容面）
# ---------------------------------------------------------------------------

VALID_LAYERS: Final[tuple[str, ...]] = tuple(sorted(load_vocabulary_values("meta_question_layers_vocabulary.yaml")))
VALID_FREQUENCIES: Final[tuple[str, ...]] = tuple(load_vocabulary_values("meta_question_frequencies_vocabulary.yaml"))
VALID_STATUSES: Final[tuple[str, ...]] = tuple(load_vocabulary_values("meta_question_statuses_vocabulary.yaml"))
VALID_OUTCOMES: Final[tuple[str, ...]] = tuple(load_vocabulary_values("meta_question_outcomes_vocabulary.yaml"))

#: A 级入库必填字段（10§2.2；q_id 机生、status 机置不在逐项校验之列；net_zero_note 由
#: 专用步骤按 net_zero_note_missing 码校验缺/空，不走 field_missing 码）
REQUIRED_A_FIELDS: Final[tuple[str, ...]] = (
    "title",
    "layer",
    "data_sources",
    "exam_plan",
    "consumers",
    "frequency",
    "pit_proof",
    "provenance",
)

#: A 级字段中仅查"键存在"的（空白串留给五要素机检按专用码拒）
_PRESENCE_ONLY_FIELDS: Final[frozenset[str]] = frozenset({"pit_proof"})

JSONB_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "data_sources",
        "exam_plan",
        "consumers",
        "provenance",
        "chain_refs",
        "evidence_refs",
    }
)


def normalize_title(title: str) -> str:
    """标题归一化（查重用）：NFKC → 转小写 → 去空白 → 去标点（10§4 机械方法降级通道）。"""
    text = unicodedata.normalize("NFKC", str(title or ""))
    return "".join(ch for ch in text.lower() if not ch.isspace() and not unicodedata.category(ch).startswith("P"))


# ---------------------------------------------------------------------------
# W4 源线谱机器可读册真检（WO-001：命中即不降级）
# 真源链：docs/_working/chain_piling_campaign/02_source_line_registry.md（人读 W4）
#   → data/registers/metaq_source_line/source_line_registry.yaml（机生册，禁手改）
#   生成器=scripts/governance/meta_question/wo001_003/generate_source_line_register.py
# 判据真源：10_intake_gate_design.md §3 行1（要素1 命中真源=W4）/行5（要素5 时戳结构可机判）
#   /行3（要素3 真源=functional_domain_registry，四件套消费清单属 W2 产物未建→保留降级痕）。
# fail-closed 方向：册缺失/漂移/不可读=判定不成立→照旧附 degraded_check（禁"读不到就当过"）。
# ---------------------------------------------------------------------------

#: W4 机器可读册仓内相对路径（构造参数可覆盖，测试侧注入 tmp 副本）
SOURCE_LINE_REGISTER_PATH: Final[str] = "data/registers/metaq_source_line/source_line_registry.yaml"

#: 消费方层码前缀（七层枚举 L0-L6 与 functional_domain_registry 之外的唯一机械命中式）
_CONSUMER_LAYER_RE: Final[re.Pattern[str]] = re.compile(r"^(L\d+)(?:[^A-Za-z0-9]|$)")

#: 册面缓存（key=绝对路径 → (mtime, doc|None)）；mtime 变更即重读，禁进程内陈旧命中
_REGISTER_CACHE: Final[dict[str, tuple[float, dict[str, Any] | None]]] = {}
_DOMAIN_CACHE: Final[dict[str, tuple[float, frozenset[str]]]] = {}

_FUNCTIONAL_DOMAIN_REGISTRY_REL: Final[str] = (
    "docs/01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml"
)


def load_source_line_register(path: str | Path | None = None) -> dict[str, Any] | None:
    """读 W4 机器可读册；缺失/结构不合/计数漂移一律返回 None（=真检不成立，走降级）。"""
    target = Path(path) if path else _repo_root() / SOURCE_LINE_REGISTER_PATH
    if not target.exists():
        return None
    key, mtime = str(target), target.stat().st_mtime
    cached = _REGISTER_CACHE.get(key)
    if cached and cached[0] == mtime:
        return cached[1]
    doc = _read_register_file(target)
    _REGISTER_CACHE[key] = (mtime, doc)
    return doc


def _read_register_file(target: Path) -> dict[str, Any] | None:
    try:
        import yaml

        doc = yaml.safe_load(target.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 册坏≠登记坏——降级留痕，禁抛断入库闸
        log.warning("W4 源线谱册读取失败，本次登记走降级口径：%s", exc)
        return None
    if not isinstance(doc, dict) or not isinstance(doc.get("lines"), list) or not doc["lines"]:
        log.warning("W4 源线谱册结构不合 schema（缺 lines 或空册）：%s", target)
        return None
    counts = doc.get("counts") or {}
    if int(counts.get("lines") or 0) != len(doc["lines"]):
        log.warning(
            "W4 源线谱册 counts.lines=%s ≠ 条目数 %s（漂移，判定不采信）", counts.get("lines"), len(doc["lines"])
        )
        return None
    return doc


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _register_index(doc: dict[str, Any]) -> tuple[frozenset[str], frozenset[str], dict[str, bool]]:
    """册面摊平：(线 id 集, 命中 token 宇宙, 线→PIT as-of 声明)。"""
    line_ids: list[str] = []
    tokens: list[str] = [str(t) for t in (doc.get("ds_anchor_universe") or [])]
    pit: dict[str, bool] = {}
    for entry in doc["lines"]:
        line_id = str(entry.get("line_id") or "").strip()
        if not line_id:
            continue
        line_ids.append(line_id)
        tokens += [str(t) for t in (entry.get("source_tokens") or [])]
        pit[line_id] = bool(entry.get("pit_asof_declared"))
    return frozenset(line_ids), frozenset(tokens), pit


def _touched_lines(doc: dict[str, Any], sources: list[str]) -> set[str]:
    """问题声明的数据源 token → 命中的源线 id 集。"""
    declared = {str(s).strip() for s in sources if str(s).strip()}
    return {
        str(entry.get("line_id"))
        for entry in doc["lines"]
        if declared & {str(t) for t in (entry.get("source_tokens") or [])}
    }


def _source_line_resolvable(q: dict[str, Any], doc: dict[str, Any] | None) -> bool:
    """要素 1 真检（10§3 行1）：line_ref 在册 **且** 每个 data_source 都命中册面 token 宇宙。"""
    if doc is None:
        return False
    line_ids, tokens, _ = _register_index(doc)
    line_ref = str(q.get("line_ref") or "").strip()
    sources = [str(s).strip() for s in (q.get("data_sources") or []) if str(s).strip()]
    if line_ref not in line_ids or not sources:
        return False
    return all(source in tokens for source in sources)


def _pit_columns_declared(q: dict[str, Any], doc: dict[str, Any] | None) -> bool:
    """要素 5 真检（10§3 行5）：问题触及的每条源线在册内都声明了可用 as-of 时戳机制。"""
    if doc is None:
        return False
    _, _, pit = _register_index(doc)
    touched = _touched_lines(doc, [str(s) for s in (q.get("data_sources") or [])])
    line_ref = str(q.get("line_ref") or "").strip()
    if line_ref:
        touched.add(line_ref)
    return bool(touched) and all(pit.get(line_id) for line_id in touched)


def _consumers_resolvable(q: dict[str, Any]) -> bool:
    """要素 3 真检（10§3 行3）：每项 consumer 命中七层枚举或 functional_domain_registry。

    四件套消费清单（未答看板/入库闸/模板生成器/考试回填闭环）属 W2 立项产物、尚未机器
    可读，命中不了的项保留降级痕——禁把"无真源"洗成"通过"。
    """
    consumers = [str(c).strip() for c in (q.get("consumers") or []) if str(c).strip()]
    if not consumers or len(consumers) != len(q.get("consumers") or []):
        return False
    domains = _functional_domain_names()
    return all(_consumer_hit(consumer, domains) for consumer in consumers)


def _consumer_hit(consumer: str, domains: frozenset[str]) -> bool:
    match = _CONSUMER_LAYER_RE.match(consumer)
    if match and match.group(1) in VALID_LAYERS:
        return True
    return consumer in domains


def _functional_domain_names() -> frozenset[str]:
    """functional_domain_registry 的 domain/subdomain/中文名并集（mtime 缓存）。"""
    target = _repo_root() / _FUNCTIONAL_DOMAIN_REGISTRY_REL
    if not target.exists():
        return frozenset()
    key, mtime = str(target), target.stat().st_mtime
    cached = _DOMAIN_CACHE.get(key)
    if cached and cached[0] == mtime:
        return cached[1]
    names = _read_domain_names(target)
    _DOMAIN_CACHE[key] = (mtime, names)
    return names


def _read_domain_names(target: Path) -> frozenset[str]:
    try:
        import yaml

        doc = yaml.safe_load(target.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 域册读不到≠要素3 通过——按降级留痕
        log.warning("functional_domain_registry 读取失败，要素3 走降级口径：%s", exc)
        return frozenset()
    entries = doc.get("domains") or doc.get("entries") or [] if isinstance(doc, dict) else []
    names: list[str] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        for field_name in ("domain", "subdomain", "domain_name_zh", "name_zh"):
            value = str(entry.get(field_name) or "").strip()
            if value:
                names.append(value)
        names += [str(a).strip() for a in (entry.get("aliases") or []) if str(a).strip()]
    return frozenset(names)


def _degraded_evidence(degraded: list[str], doc: dict[str, Any] | None) -> str:
    """降级痕证据：册未建成=W4_source_line_registry_pending（历史口径原样保留）；
    册已建成而某要素判定不过=逐项点名（复考与抽卷据此定位缺哪一条）。"""
    if doc is None:
        return "W4_source_line_registry_pending"
    return "real_check_miss:" + ",".join(degraded)


# ---------------------------------------------------------------------------
# SQL（%s 占位符 psycopg2 口径；测试侧 SQLite wrapper 做 %s→? 翻译；
# 列集/考试簇 SQL 真源在 exam_ops.py，_MAIN_COLUMNS 经 import 回用）
# ---------------------------------------------------------------------------

_SQL_INSERT_MAIN = "INSERT INTO {{s}}.meta_question ({cols}) VALUES ({ph})".format(
    cols=", ".join(_MAIN_COLUMNS), ph=", ".join(["%s"] * len(_MAIN_COLUMNS))
)
_SQL_DEDUP_SCAN = "SELECT q_id, title, line_ref FROM {s}.meta_question WHERE layer = %s ORDER BY q_id"
_SQL_ALLOC_QID = "SELECT q_id FROM {s}.meta_question WHERE q_id LIKE 'PQ-%'"


class MetaQuestionRegistry(MetaQuestionExamMixin):
    """meta_question_registry 写入 API（登记/流转/认领/考试记账 + 审计双轨）。

    NO-GOD-CLASS 拆分（st-metaq-20260923）：考试生命周期簇 10 方法
    （transition/claim/release_claim/record_exam_result + 审计双轨 + 行读取）
    迁至 :mod:`zephyr.governance.meta_question.exam_ops` 的
    :class:`MetaQuestionExamMixin`，本类继承获得，公共 API 零变化。

    :param schema: 目标 schema（生产 ``meta_question``；SQLite mock 侧传 ``main``）
    :param get_conn: 连接工厂 ``get_conn(*, read_only: bool) -> conn``；
        缺省惰性走 ``get_depgraph_pg_connection``（depgraph 同实例通道先例）
    :param audit_jsonl_path: 审计 JSONL 双轨路径（20§2.2；生产由调用方传 ``.runtime`` 下
        路径，测试传 tmp_path；None=只写 PG 审计表不落 JSONL）
    :param source_line_register_path: W4 源线谱机器可读册路径（None=仓内默认 data/registers/metaq_source_line/source_line_registry.yaml）
    """

    def __init__(
        self,
        schema: str = "meta_question",
        get_conn: Callable[..., Any] | None = None,
        audit_jsonl_path: str | Path | None = None,
        source_line_register_path: str | Path | None = None,
    ) -> None:
        self.schema: Final[str] = schema
        #: 连接工厂（公开属性：snapshot 导出器与测试侧复用同一注入口径）
        self.get_conn: Final[Callable[..., Any]] = get_conn or self._default_get_conn
        self.audit_jsonl_path: Final[Path | None] = Path(audit_jsonl_path) if audit_jsonl_path else None
        #: W4 机器可读册路径覆盖口（None=仓内默认路径；测试侧注入 tmp 副本，生产禁指他处）
        self.source_line_register_path: Final[Path | None] = (
            Path(source_line_register_path) if source_line_register_path else None
        )

    # -- 连接 ---------------------------------------------------------------

    @staticmethod
    def _default_get_conn(*, read_only: bool = True) -> Any:  # noqa: any-abuse  any-abuse豁免: DB游标/连接/外部驱动动态对象，签名无法具体化（容器型与Protocol重构另行）
        """默认通道：depgraph 同实例 PG（惰性 import，避免 mock 场景硬依赖 psycopg2）。"""
        from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

        return get_depgraph_pg_connection(read_only=read_only)

    def _conn(self, *, read_only: bool) -> Any:  # noqa: any-abuse  any-abuse豁免: DB游标/连接/外部驱动动态对象，签名无法具体化（容器型与Protocol重构另行）
        return self.get_conn(read_only=read_only)

    # -- 登记（10§7.1/§7.2）-------------------------------------------------

    def register(self, question: dict[str, Any], *, actor: str = "") -> str:
        """入库闸：校验→查重→q_id 机生→写入（status=registered，10§5.3 机械层自动定案）。

        返回机生 q_id（PQ-NNNN 连号 max+1，墓碑不复用）。任一校验失败短路抛
        :class:`QuestionValidationError`，零副作用。
        """
        q = dict(question or {})
        degraded = self._validate_for_register(q)
        conn = self._conn(read_only=False)
        try:
            cur = conn.cursor()
            q_id = self._alloc_q_id(cur)
            now = now_utc()
            provenance = self._prepare_register_provenance(q, actor, now)
            cur.execute(
                _SQL_INSERT_MAIN.format(s=self.schema),
                self._build_register_row(q_id, q, provenance, now),
            )
            self._write_register_audits(cur, q_id=q_id, actor=actor, provenance=provenance, degraded=degraded)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
        log.info("registered %s layer=%s actor=%s", q_id, q["layer"], actor)
        return q_id

    def _validate_for_register(self, q: dict[str, Any]) -> list[str]:
        """登记前置校验链（10§7.1 顺序：A 级必填→layer 枚举→五要素机检→查重→净零）。

        失败即短路抛 :class:`QuestionValidationError`；返回五要素降级检查清单
        （留 degraded_check 痕）。
        """
        # ① A 级字段完备性（10§2.2，缺一即拒）
        self._check_required_fields(q)
        # ② 枚举合法：layer
        self._check_layer(q)
        # ③ 五要素机检（10§3 真检：W4 册命中即放行，未命中项留降级痕）
        degraded = self._check_five_elements(q, register=self._source_line_register())
        # ④ 查重（标题归一化+layer+line_ref 全表比对；高相似=拒，附 duplicate_of）
        duplicate_of = self._find_duplicate(q)
        if duplicate_of:
            raise QuestionValidationError(
                "dup_high_similarity",
                {"duplicate_of": duplicate_of, "layer": q.get("layer")},
            )
        # ⑤ 净零声明非空（20§5 强制点 1）
        if not str(q.get("net_zero_note") or "").strip():
            raise QuestionValidationError("net_zero_note_missing", {"field": "net_zero_note"})
        return degraded

    @staticmethod
    def _prepare_register_provenance(q: dict[str, Any], actor: str, now: datetime) -> dict[str, Any]:
        """登记 provenance 组装：机置 registered_at/registered_by（OSF 注册时戳对标，10§2.1）。"""
        provenance = dict(q.get("provenance") or {})
        provenance.setdefault("registered_at", now.isoformat())
        provenance.setdefault("registered_by", actor)
        return provenance

    @staticmethod
    def _build_register_row(q_id: str, q: dict[str, Any], provenance: dict[str, Any], now: datetime) -> tuple[Any, ...]:
        """INSERT 行元组（列序对齐 _MAIN_COLUMNS；JSONB 字段经 _as_json 序列化）。"""
        return (
            q_id,
            str(q["title"]).strip(),
            q["layer"],
            q.get("line_ref"),
            q.get("graph_ref"),
            _as_json(list(q.get("data_sources") or [])),
            _as_json(dict(q.get("exam_plan") or {})),
            _as_json(list(q.get("consumers") or [])),
            q["frequency"],
            str(q.get("pit_proof") or ""),
            "registered",
            q.get("parent_id"),
            q.get("merged_into"),
            _as_json(provenance),
            str(q.get("net_zero_note") or "").strip(),
            _as_json(list(q.get("chain_refs") or [])),
            _as_json(list(q.get("evidence_refs") or [])),
            None,
            None,
            None,
            None,
            None,
            1,
            now,
            now,
        )

    def _write_register_audits(
        self,
        cur: Any,  # noqa: any-abuse  any-abuse豁免: DB游标/连接/外部驱动动态对象，签名无法具体化（容器型与Protocol重构另行）
        *,
        q_id: str,
        actor: str,
        provenance: dict[str, Any],
        degraded: list[str],
    ) -> None:
        """登记审计：register 事件 + （降级时）degraded_check 声明（10§3 降级口径声明）。"""
        self._write_audit(
            cur,
            MetaQuestionAuditEvent(
                q_id=q_id,
                actor=actor,
                what="register",
                before=None,
                after={"status": "registered"},
                evidence=str(provenance.get("evidence") or ""),
                diff=[{"field": "status", "old": None, "new": "registered"}],
            ),
        )
        if degraded:
            # 降级检查显式声明（10§3：真检未成立的要素逐项点名，全过则本事件不产生）
            self._write_audit(
                cur,
                MetaQuestionAuditEvent(
                    q_id=q_id,
                    actor=actor,
                    what="degraded_check",
                    before=None,
                    after={"checks": degraded},
                    evidence=_degraded_evidence(degraded, self._source_line_register()),
                    diff=[],
                ),
            )

    @staticmethod
    def _check_required_fields(q: dict[str, Any]) -> None:
        """A 级字段缺一即拒（10§2.2；短路返回首缺）。

        pit_proof 仅查键存在：空白串留给五要素机检按 ``pit_proof_missing`` 码拒
        （对齐 10§7.2 错误码表），避免同一缺口在两级校验出两个码。
        """
        for field_name in REQUIRED_A_FIELDS:
            value = q.get(field_name)
            if field_name in _PRESENCE_ONLY_FIELDS:
                if value is None:
                    raise QuestionValidationError(f"field_missing:{field_name}", {"stage": "required_fields"})
                continue
            if value is None or (isinstance(value, str) and not value.strip()):
                raise QuestionValidationError(f"field_missing:{field_name}", {"stage": "required_fields"})

    @staticmethod
    def _check_layer(q: dict[str, Any]) -> None:
        if q.get("layer") not in VALID_LAYERS:
            raise QuestionValidationError("layer_invalid", {"layer": q.get("layer")})

    @staticmethod
    def _check_five_elements(q: dict[str, Any], register: dict[str, Any] | None = None) -> list[str]:
        """五要素机检（纪要§2 资格线；10§3 真检判据）。返回未成立要素清单（留 degraded_check 痕）。

        逐要素独立子检查（COMPLEXITY 拆分）：A 级结构不合格即短路抛专用 subcode；
        结构合格但真检不成立（源线不命中/PIT as-of 未声明/消费方无真源命中）的要素
        逐项登记降级标记——**册命中即不登记**（WO-001 关闸点，旧口径为无条件登记）。
        """
        degraded: list[str] = []
        MetaQuestionRegistry._check_element1_data_sources(q, degraded, register)
        MetaQuestionRegistry._check_element2_exam_plan(q)
        MetaQuestionRegistry._check_element3_consumers(q, degraded)
        MetaQuestionRegistry._check_element4_frequency(q)
        MetaQuestionRegistry._check_element5_pit_proof(q, degraded, register)
        return degraded

    @staticmethod
    def _check_element1_data_sources(
        q: dict[str, Any], degraded: list[str], register: dict[str, Any] | None = None
    ) -> None:
        """要素 1 能被数据回答：A 级=非空数组逐项非空串；真检=每项命中 W4 册（10§3 行1）。"""
        sources = q.get("data_sources")
        if not isinstance(sources, list) or not sources or not all(isinstance(s, str) and s.strip() for s in sources):
            raise QuestionValidationError("data_sources_empty", {"element": 1})
        if not _source_line_resolvable(q, register):
            degraded.append("source_line_resolvability")

    @staticmethod
    def _check_element2_exam_plan(q: dict[str, Any]) -> None:
        """要素 2 能被考试证伪：exam_plan 同时含判定字段(criterion)与阈值字段(threshold)。"""
        # （threshold 允许数值 0，禁用 truthy 判定）
        plan = q.get("exam_plan")
        threshold = plan.get("threshold") if isinstance(plan, dict) else None
        threshold_ok = threshold is not None and str(threshold).strip() != ""
        criterion_ok = isinstance(plan, dict) and str(plan.get("criterion") or "").strip() != ""
        if not (criterion_ok and threshold_ok):
            raise QuestionValidationError("exam_plan_no_threshold", {"element": 2})

    @staticmethod
    def _check_element3_consumers(q: dict[str, Any], degraded: list[str]) -> None:
        """要素 3 有明确消费方：A 级=非空；真检=逐项命中七层枚举或 functional_domain_registry（10§3 行3）。"""
        consumers = q.get("consumers")
        if (
            not isinstance(consumers, list)
            or not consumers
            or not all(isinstance(c, str) and c.strip() for c in consumers)
        ):
            raise QuestionValidationError("consumer_unresolvable", {"element": 3})
        if not _consumers_resolvable(q):
            degraded.append("consumer_registry_resolvability")

    @staticmethod
    def _check_element4_frequency(q: dict[str, Any]) -> None:
        """要素 4 有更新频率：枚举机判；event_driven 须事件源引用非空（A 级机检，R-20）。"""
        if q.get("frequency") not in VALID_FREQUENCIES:
            raise QuestionValidationError("frequency_not_in_enum", {"frequency": q.get("frequency")})
        if (
            q["frequency"] == "event_driven"
            and not str((q.get("exam_plan") or {}).get("event_source_ref") or "").strip()
        ):
            raise QuestionValidationError("event_source_ref_missing", {"frequency": "event_driven"})

    @staticmethod
    def _check_element5_pit_proof(
        q: dict[str, Any], degraded: list[str], register: dict[str, Any] | None = None
    ) -> None:
        """要素 5 PIT 安全：A 级=pit_proof 非空；真检=所触及源线在册内声明可用 as-of 时戳（10§3 行5）。"""
        if not str(q.get("pit_proof") or "").strip():
            raise QuestionValidationError("pit_proof_missing", {"element": 5})
        if not _pit_columns_declared(q, register):
            degraded.append("pit_timestamp_col_check")

    def _source_line_register(self) -> dict[str, Any] | None:
        """本次登记用的 W4 机器可读册（mtime 缓存；None=册不可用，全要素按降级处理）。"""
        return load_source_line_register(self.source_line_register_path)

    def _find_duplicate(self, q: dict[str, Any]) -> str | None:
        """查重（10§4 降级通道）：同 layer + 标题归一化相等 + line_ref 相等 → 高相似。"""
        norm = normalize_title(str(q.get("title") or ""))
        if not norm:
            return None
        conn = self._conn(read_only=True)
        try:
            cur = conn.cursor()
            cur.execute(_SQL_DEDUP_SCAN.format(s=self.schema), (q.get("layer"),))
            cols = [d[0] for d in cur.description]
            for row in cur.fetchall():
                row_dict = dict(zip(cols, row, strict=True))
                if normalize_title(str(row_dict.get("title") or "")) != norm:
                    continue
                if (row_dict.get("line_ref") or None) != (q.get("line_ref") or None):
                    continue
                return str(row_dict["q_id"])
        finally:
            conn.close()
        return None

    def _alloc_q_id(self, cur: Any) -> str:  # noqa: any-abuse  any-abuse豁免: DB游标/连接/外部驱动动态对象，签名无法具体化（容器型与Protocol重构另行）
        """q_id 机生：全表 PQ-* max+1 连号（墓碑不复用，纪要§7）。"""
        cur.execute(_SQL_ALLOC_QID.format(s=self.schema))
        max_no = 0
        for (q_id,) in cur.fetchall():
            suffix = str(q_id)[3:]
            if suffix.isdigit():
                max_no = max(max_no, int(suffix))
        return f"PQ-{max_no + 1:04d}"
