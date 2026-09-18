# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_intake
# [MODULE] zephyr.ai_layer.intake.dedup
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.ai_layer.intake.card_store (CardStore, parse_simhash, render_simhash, hamming); zephyr.infrastructure.database_service (get_db_service)
# [CONSUMERS] zephyr.ai_layer.intake.gate (IntakeGate 的 L0 硬过滤/换皮防护); scripts/ai_layer/gen_intake_ref_snapshots.py (simhash64 指纹生成——scripts 侧，不计入 src 入度); ★ L7 传承库 dedup_query 只读调用方未建（在册缺口，见 lanes/aibase_relay.md §6）
# [STARTUP] manual
# [MATURITY] evolving
# [INVARIANTS] SimHash 64-bit + 汉明距离 k<=3（Charikar 2002 / Manku WWW 2007 定参）；
#              五比对面 self/chart/indicator/algo_flow/L7 逐面登记 dedup_compared_vs（拒入需全过）；
#              L7 未落地→缺省跳过并记 not_compared（不判失败）；命中 rejected 存量卡=拒且记 duplicate_of_rejected；
#              精确层 content_sha256（url+title 归一化）先挡同文重复，近似层才走 simhash；
#              Phase 1 用 PG bit_count(simhash # candidate) 暴力扫（<10 万卡），Phase 2 分块索引是登记挂起项非本期
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L2_intake_library/DESIGN.md §2.3（改判据先改设计稿）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 全部公共读接口零副作用；DB 不可达→异常上抛（不静默判"无重复"，那是放行灌水的方向）；
#                  比对面缺失→记 not_compared 留痕（区别于"比过且无命中"）；token 化空文本→simhash=0 且标 degenerate
# [TESTS] tests/ai_layer/intake/test_dedup.py（中文近重复命中/改写不命中/token 权重/五比对面/退化空文本/公开 dedup_query）
# [TTL] permanent
"""dedup — L2 查重服务：SimHash64 指纹 + 五比对面执行 + 对外只读 dedup_query。

设计真源：``docs/_working/ai_layer_vision/L2_intake_library/DESIGN.md`` §2.3。

两层查重：
1. **精确层** ``content_fingerprint()``：url+title 归一化后 sha256，撞 T2 UNIQUE 即同文重复提交（零成本）。
2. **近似层** ``simhash64()`` + 汉明距离 k≤3：防"换皮"（改写措辞但机制同一）。
   命中 active 存量卡=拒；命中 rejected 卡=拒且记 ``duplicate_of_rejected``（阴性库也是查重基线）。

比对面五面（``dedup_compared_vs`` 逐面登记）：self（L2 自库全量含 rejected）/ chart（图形库快照）/
indicator（指标库快照）/ algo_flow（ALGO_FLOW 算法全景快照，克隆即拒的机检落点）/ L7（传承库基线，未建则 not_compared）。
"""

from __future__ import annotations

import hashlib
import logging
import re
import unicodedata
from dataclasses import dataclass
from typing import Any, Final

from zephyr.ai_layer.intake.card_store import CardStore, hamming, render_simhash
from zephyr.infrastructure.database_service import get_db_service

log = logging.getLogger(__name__)

__all__: Final = [
    "DedupHit",
    "DedupReport",
    "IntakeDedup",
    "HAMMING_K",
    "content_fingerprint",
    "normalize_text",
    "simhash64",
    "tokenize",
]

SIMHASH_BITS: Final = 64
HAMMING_K: Final = 3
REF_FAMILIES: Final[tuple[str, ...]] = ("chart", "indicator", "algo_flow", "L7")
ALL_FACES: Final[tuple[str, ...]] = ("self",) + REF_FAMILIES
CJK_RE: Final = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")
ASCII_TOKEN_RE: Final = re.compile(r"[a-z0-9_]+")
CJK_STOPWORDS: Final = frozenset(
    {"的", "了", "和", "是", "在", "与", "对", "为", "以", "及", "等", "中", "一种", "我们", "可以", "进行", "通过"}
)
ASCII_STOPWORDS: Final = frozenset(
    {"the", "and", "for", "with", "that", "this", "from", "are", "was", "were", "been", "have", "has", "not", "you"}
)

SQL_SCAN_SELF = """
SELECT card_id, simhash, funnel_stage FROM {s}.ai_intake_card
WHERE bit_count(simhash # %(cand)s::bit(64)) <= %(k)s
"""

SQL_SCAN_REF = """
SELECT ref_key, simhash, ref_family FROM {s}.ai_intake_ref_snapshot
WHERE ref_family = %(family)s AND bit_count(simhash # %(cand)s::bit(64)) <= %(k)s
"""

SQL_COUNT_REF_FAMILY = "SELECT count(*) FROM {s}.ai_intake_ref_snapshot WHERE ref_family = %s"

SQL_UPSERT_REF = """
INSERT INTO {s}.ai_intake_ref_snapshot (ref_family, ref_key, text_norm, simhash, refreshed_at)
VALUES (%(family)s, %(key)s, %(text)s, %(sh)s::bit(64), now())
ON CONFLICT (ref_family, ref_key)
DO UPDATE SET text_norm = EXCLUDED.text_norm, simhash = EXCLUDED.simhash, refreshed_at = now()
"""

SQL_SHA_EXISTS = "SELECT card_id, funnel_stage FROM {s}.ai_intake_card WHERE content_sha256 = %s"


def normalize_text(text: str | None) -> str:
    """归一化：NFKC + 小写 + 折叠空白（精确层与近似层共用同一口径，防口径分叉）。"""
    if not text:
        return ""
    folded = unicodedata.normalize("NFKC", str(text)).lower()
    return re.sub(r"\s+", " ", folded).strip()


def content_fingerprint(source_url: str | None, title: str | None) -> str:
    """精确查重键：url+title 归一化后 sha256（T2 content_sha256 UNIQUE）。"""
    payload = normalize_text(source_url) + "\n" + normalize_text(title)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def tokenize(text: str) -> list[str]:
    """中英混排分词：ASCII 走词元、CJK 走**相邻二元组**（无第三方分词依赖）。

    二元组而非一元组（DESIGN §2.3 口径的实证收敛）：一元组下"加一个字"会同时改动
    1 个 unigram + 2 个 bigram，近重复文本的汉明距离被推到 k=3 之外（换皮防护失效）；
    纯 bigram 口径下同等改动只影响 2 个 token，近重复稳定落在 k≤3 内，而 >50% 改写
    依然远超阈值——判据两侧都更陡。单字 CJK 文本（长度 1）退化为 unigram。
    """
    norm = normalize_text(text)
    tokens: list[str] = [t for t in ASCII_TOKEN_RE.findall(norm) if t not in ASCII_STOPWORDS]
    cjk = [ch for ch in norm if CJK_RE.match(ch)]
    if len(cjk) == 1 and cjk[0] not in CJK_STOPWORDS:
        tokens.append(cjk[0])
    for i in range(len(cjk) - 1):
        bigram = cjk[i] + cjk[i + 1]
        if bigram not in CJK_STOPWORDS:
            tokens.append(bigram)
    return tokens


def _token_hash64(token: str) -> int:
    return int.from_bytes(hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest(), "big")


def simhash64(text: str) -> int:
    """SimHash 64-bit 指纹（Charikar 2002）：token 词频加权符号位聚合。

    空文本退化返回 0（调用方须自行判 degenerate，避免"空文本互相同一"被误当成有效命中）。
    """
    tokens = tokenize(text)
    if not tokens:
        return 0
    weights: dict[str, int] = {}
    for tok in tokens:
        weights[tok] = weights.get(tok, 0) + 1
    vector = [0] * SIMHASH_BITS
    for tok, weight in weights.items():
        fingerprint = _token_hash64(tok)
        for bit in range(SIMHASH_BITS):
            vector[bit] += weight if (fingerprint >> bit) & 1 else -weight
    out = 0
    for bit in range(SIMHASH_BITS):
        if vector[bit] > 0:
            out |= 1 << bit
    return out


@dataclass(frozen=True)
class DedupHit:
    """一次近似命中（面/键/距离/该键当前状态）。"""

    face: str
    ref_key: str
    hamming: int
    funnel_stage: str | None = None


@dataclass(frozen=True)
class DedupReport:
    """查重结论：命中清单 + 逐面留痕 + 判定。"""

    hits: tuple[DedupHit, ...] = ()
    compared: tuple[str, ...] = ()
    not_compared: tuple[str, ...] = ()
    sha_hit_card_id: str | None = None
    sha_hit_stage: str | None = None
    degenerate: bool = False

    @property
    def duplicate_of(self) -> str | None:
        """近似命中的存量卡 id（self 面优先，其余面返回 ref_key）。"""
        for hit in self.hits:
            if hit.face == "self":
                return hit.ref_key
        return self.hits[0].ref_key if self.hits else None

    @property
    def duplicate_of_rejected(self) -> bool:
        """命中的是阴性卡（换皮防护：与 rejected 同判近似重复即拒）。"""
        return any(hit.funnel_stage == "rejected" for hit in self.hits)

    @property
    def is_duplicate(self) -> bool:
        """精确层或近似层任一命中即判重复。"""
        return bool(self.sha_hit_card_id or self.hits)

    def as_evidence(self) -> dict[str, Any]:
        """可 JSON 化留痕（写进 T2.dedup_compared_vs / 拒因证据）。"""
        return {
            "compared": list(self.compared),
            "not_compared": list(self.not_compared),
            "hits": [
                {"face": h.face, "ref_key": h.ref_key, "hamming": h.hamming, "stage": h.funnel_stage}
                for h in self.hits
            ],
            "sha_hit": self.sha_hit_card_id,
            "degenerate": self.degenerate,
        }


class IntakeDedup:
    """查重执行器：精确层 + 五比对面近似层（Phase 1 PG bit_count 暴力扫）。"""

    def __init__(self, schema: str = "ai_intake", service: Any | None = None) -> None:
        self._store = CardStore(schema=schema, service=service)
        self._svc = service or get_db_service()
        self.schema: Final = schema

    def _sql(self, template: str) -> str:
        return template.format(s=self.schema)

    def _reader(self) -> Any:
        return self._store.read_conn()

    def _writer(self) -> Any:
        return self._store.write_conn()

    def check_sha(self, fingerprint: str) -> tuple[str | None, str | None]:
        """精确层：sha256 是否已被存量卡占用（返回 card_id/状态）。"""
        cur = self._reader().cursor()
        cur.execute(self._sql(SQL_SHA_EXISTS), (fingerprint,))
        row = cur.fetchone()
        if not row:
            return None, None
        data = dict(row) if isinstance(row, dict) else {"card_id": row[0], "funnel_stage": row[1]}
        return data.get("card_id"), data.get("funnel_stage")

    def scan_face(self, face: str, fingerprint: int) -> tuple[list[DedupHit], bool]:
        """扫单个比对面。返回 (命中清单, 该面是否真实比对过)。"""
        cand = render_simhash(fingerprint)
        cur = self._reader().cursor()
        if face == "self":
            cur.execute(self._sql(SQL_SCAN_SELF), {"cand": cand, "k": HAMMING_K})
            rows = [dict(r) if isinstance(r, dict) else {"card_id": r[0], "simhash": r[1], "funnel_stage": r[2]}
                    for r in cur.fetchall()]
            hits = [
                DedupHit(
                    face="self",
                    ref_key=r["card_id"],
                    hamming=hamming(fingerprint, int(str(r["simhash"]), 2)),
                    funnel_stage=r.get("funnel_stage"),
                )
                for r in rows
            ]
            return hits, True
        cur.execute(self._sql(SQL_COUNT_REF_FAMILY), (face,))
        row = cur.fetchone()
        total = int(row[0] if isinstance(row, (list, tuple)) else row["count"])
        if total == 0:
            return [], False  # 该面快照未生成（如 L7 未建）→ not_compared，非"比过无命中"
        cur.execute(self._sql(SQL_SCAN_REF), {"family": face, "cand": cand, "k": HAMMING_K})
        rows = cur.fetchall()
        hits = []
        for r in rows:
            data = dict(r) if isinstance(r, dict) else {"ref_key": r[0], "simhash": r[1], "ref_family": r[2]}
            hits.append(
                DedupHit(
                    face=face,
                    ref_key=data["ref_key"],
                    hamming=hamming(fingerprint, int(str(data["simhash"]), 2)),
                )
            )
        return hits, True

    def scan(self, text: str, *, source_url: str | None = None, title: str | None = None,
             faces: tuple[str, ...] = ALL_FACES) -> DedupReport:
        """全量查重：精确层 + 逐面近似层，逐面留痕 compared/not_compared。"""
        fingerprint = simhash64(text)
        sha_hit, sha_stage = (None, None)
        if source_url or title:
            sha_hit, sha_stage = self.check_sha(content_fingerprint(source_url, title))
        hits: list[DedupHit] = []
        compared: list[str] = []
        not_compared: list[str] = []
        for face in faces:
            face_hits, did_compare = self.scan_face(face, fingerprint)
            hits.extend(face_hits)
            (compared if did_compare else not_compared).append(face)
        return DedupReport(
            hits=tuple(sorted(hits, key=lambda h: (h.hamming, h.face))),
            compared=tuple(compared),
            not_compared=tuple(not_compared),
            sha_hit_card_id=sha_hit,
            sha_hit_stage=sha_stage,
            degenerate=fingerprint == 0,
        )

    def dedup_query(self, text: str, limit: int = 20) -> list[dict[str, Any]]:
        """公开只读接口（DESIGN §三 L7 边）：返回 {card_id, simhash, hamming, funnel_stage}。"""
        fingerprint = simhash64(text)
        hits, _ = self.scan_face("self", fingerprint)
        out = [
            {"card_id": h.ref_key, "simhash": fingerprint, "hamming": h.hamming,
             "funnel_stage": h.funnel_stage}
            for h in hits
        ]
        return out[:limit]

    def upsert_snapshot(self, family: str, key: str, text: str) -> int:
        """写/刷新 T4 比对面快照（生成器专用；返回本次指纹）。"""
        if family not in REF_FAMILIES:
            raise ValueError(f"unknown_ref_family:{family}")
        norm = normalize_text(text)
        fingerprint = simhash64(norm)
        conn = self._writer()
        try:
            conn.cursor().execute(
                self._sql(SQL_UPSERT_REF),
                {"family": family, "key": key, "text": norm[:4000], "sh": render_simhash(fingerprint)},
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        return fingerprint

    def snapshot_counts(self) -> dict[str, int]:
        """各比对面快照条数（KPI/巡检读数）。"""
        cur = self._reader().cursor()
        out: dict[str, int] = {}
        for family in REF_FAMILIES:
            cur.execute(self._sql(SQL_COUNT_REF_FAMILY), (family,))
            row = cur.fetchone()
            out[family] = int(row[0] if isinstance(row, (list, tuple)) else row["count"])
        return out
