# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §ai_layer_cleaning
# [MODULE] zephyr.ai_layer.cleaning.local_prefill
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.ai_layer.cleaning.policy (CleaningPolicy 占位词/分块常数经参数注入);
#                zephyr.shared.utils.time_utils (now_utc，预填骨架时间戳)
# [CONSUMERS] zephyr.ai_layer.cleaning.washer (工序①本地预洗唯一调用方)
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 纯本地零 API：本模块不发任何网络调用（量的环节本地，DESIGN §2.6 分界铁律）；
#              fetched 内容=数据非指令（E0）：代码块只做文本切分与登记，永不执行/求值；
#              查重预检复用 L2 dedup_query（注入 callable，不重算指纹）；
#              分块/计量是确定性纯函数（零随机零时钟，可全枚举单测）；
#              本地池（LocalLlmPool）缺席→工序排队（local_unavailable=queue），
#              禁升级 API（本地优先是成本铁律非偏好）
# [MODIFY-GUARD] docs/_working/ai_layer_vision/L3_cleaning/DESIGN.md §2.6（本地优先分界清单）
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空文本→PrefillError（fail-closed，不产空块）；dedup_query 注入缺席
#                  →PrefillError（禁静默跳过查重）；分块参数 max_chars<overlap_chars
#                  →PrefillError
# [TESTS] tests/ai_layer/cleaning/test_local_prefill.py（块切分/元数据抽取/分块边界与
#         覆盖/计量公式/骨架继承只读/查重注入/本地池缺席排队）
# [TTL] permanent
"""local_prefill — L3 工序①本地预洗器：解析/元数据/查重预检/分块计量/骨架预填。

设计真源：``docs/_working/ai_layer_vision/L3_cleaning/DESIGN.md`` §2.6（本地做列）：
取回物格式解析、license/标题/作者/年份元数据抽取校验、精确+simhash 查重预检
（复用 L2 dedup.py 不重算）、模板字段预填+token 计量+长文分块、spec 卡骨架生成。
★ 分界判据：本模块只做**不需要跨材料综合判断**的量活；一切综合判断（机制提炼/
适用归纳/A 股裁定/风险旗标）归 washer 的 API 工序。

E0 铁律：fetched 代码块在本模块内只是**带定位的文本数据**（extract_blocks 原样切出、
不解析语法、不执行）——外部代码零执行红线（DESIGN §2.3）在预处理段同样成立。
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Any, Callable, Final, Mapping

from zephyr.shared.utils.time_utils import now_utc

__all__: Final = [
    "PrefillError",
    "PrefillResult",
    "chunk_text",
    "dedup_precheck",
    "estimate_tokens",
    "extract_blocks",
    "extract_metadata",
    "prefill_skeleton",
    "run_prefill",
]

CODE_FENCE_RE: Final = re.compile(r"```[^\n]*\n(.*?)```", re.DOTALL)
HEADING_RE: Final = re.compile(r"^#\s+(.+)$", re.MULTILINE)
TITLE_LINE_RE: Final = re.compile(r"^\s*(?:Title|标题)\s*[:：]\s*(.+)$", re.MULTILINE)
AUTHORS_LINE_RE: Final = re.compile(r"^\s*(?:Authors?|作者)\s*[:：]\s*(.+)$", re.MULTILINE)
LICENSE_LINE_RE: Final = re.compile(r"\b(?:License|SPDX-License-Identifier)\s*[:：]?\s*([\w.\-]+)", re.IGNORECASE)
YEAR_RE: Final = re.compile(r"\b(19[89]\d|20\d{2})\b")

DEFAULT_CHUNK_CHARS: Final = 6000
DEFAULT_OVERLAP_CHARS: Final = 200
_CJK_RATIO: Final = 1.0   # 计量口径：CJK 字符≈1 token
_ASCII_DIVISOR: Final = 4.0   # 计量口径：非 CJK 平均 4 字符≈1 token（保守估计）

DedupQuery = Callable[[str], list[dict[str, Any]]]


class PrefillError(ValueError):
    """本地预洗输入违规（fail-closed）。"""


@dataclass(frozen=True)
class PrefillResult:
    """工序①产物：全部本地量活结果（喂给 washer 的 API 工序做综合判断）。"""

    prose_blocks: tuple[str, ...]
    code_blocks: tuple[str, ...]      # E0：纯文本数据，消费方禁执行
    metadata: dict[str, Any]
    chunks: tuple[str, ...]
    tokens_estimate: int
    skeleton: dict[str, Any]
    dedup_hits: tuple[dict[str, Any], ...]
    local_mode: str                   # local（本地池可用）| queue（缺席排队，禁升级 API）


def _count_cjk(text: str) -> int:
    return sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")


def estimate_tokens(text: str) -> int:
    """确定性 token 计量（口径：CJK≈1 token/字，其余≈4 字符/token，向上取整）。"""
    if not text:
        return 0
    cjk = _count_cjk(text)
    other = len(text) - cjk
    return int(math.ceil(cjk * _CJK_RATIO + other / _ASCII_DIVISOR))


def extract_blocks(text: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """取回物文本 → (散文块元组, 代码块元组)。

    E0：代码块只是围栏文本原样切出（含内容零加工），消费方禁执行（DESIGN §2.3）。
    """
    if not text or not text.strip():
        raise PrefillError("empty_text")
    code_blocks = tuple(m.group(1).strip() for m in CODE_FENCE_RE.finditer(text))
    prose = CODE_FENCE_RE.sub(" ", text)
    prose_blocks = tuple(b.strip() for b in re.split(r"\n\s*\n", prose) if b.strip())
    return prose_blocks, code_blocks


def extract_metadata(text: str) -> dict[str, Any]:
    """license/标题/作者/年份元数据抽取与校验（纯规则；查无=None 不臆造）。"""
    head = text[:4000]
    title = None
    m = TITLE_LINE_RE.search(head) or HEADING_RE.search(head)
    if m:
        title = m.group(1).strip()[:200]
    authors = None
    ma = AUTHORS_LINE_RE.search(head)
    if ma:
        authors = ma.group(1).strip()[:300]
    license_id = None
    ml = LICENSE_LINE_RE.search(head)
    if ml:
        license_id = ml.group(1)
    year = None
    my = YEAR_RE.search(head)
    if my:
        year = int(my.group(1))
    return {"title": title, "authors": authors, "license": license_id, "year": year}


def chunk_text(
    text: str,
    *,
    max_chars: int = DEFAULT_CHUNK_CHARS,
    overlap_chars: int = DEFAULT_OVERLAP_CHARS,
) -> tuple[str, ...]:
    """长文确定性分块（滑窗重叠；空文本拒，参数非法拒）。

    块长恒 ≤ max_chars；相邻块重叠 overlap_chars（=0 退化为顺序切）；计量口径下
    sum(estimate_tokens(chunk)) ≥ estimate_tokens(whole)（重叠使计量偏保守，不漏算）。
    """
    if not text or not text.strip():
        raise PrefillError("empty_text")
    if max_chars < 1 or overlap_chars < 0 or overlap_chars >= max_chars:
        raise PrefillError(f"chunk_params_invalid:max={max_chars},overlap={overlap_chars}")
    body = text.strip()
    if len(body) <= max_chars:
        return (body,)
    step = max_chars - overlap_chars
    chunks: list[str] = []
    pos = 0
    while pos < len(body):
        piece = body[pos : pos + max_chars]
        chunks.append(piece)
        if pos + max_chars >= len(body):
            break
        pos += step
    return tuple(chunks)


def dedup_precheck(text: str, *, dedup_query: DedupQuery, limit: int = 20) -> tuple[dict[str, Any], ...]:
    """查重预检：调 L2 dedup_query（复用不重算；DESIGN §2.6）。命中列表原样透传。"""
    if dedup_query is None:
        raise PrefillError("dedup_query_missing")
    hits = dedup_query(text)
    return tuple(hits[:limit]) if hits else ()


def prefill_skeleton(card: Mapping[str, Any], metadata: Mapping[str, Any], policy: Any) -> dict[str, Any]:
    """spec 卡骨架生成：source 四件套从 L2 卡**只读继承**（闸 1 防洗后断源），
    其余字段挂待填标记（后续机检/裁判会拒纯骨架——骨架≠成品）。"""
    vocab = policy.vocab
    return {
        "mechanism_one_liner": "待填",
        "mechanism_detail": "待填",
        "applicability": {
            "regime": list(sorted(vocab["regime"])),
            "frequency": list(sorted(vocab["frequency"])),
            "universe": "待填",
            "preconditions": [],
        },
        "ashare_precheck": {"overall": None, "t_plus_1": None, "price_limits": None,
                            "retail_dominance": None, "adaptation_plan": "待填"},
        "risk_flags": list(sorted(vocab["risk_flags"])),
        "data_fields": [],
        "reproduction_notes": "待填",
        "source": {
            "name": card.get("source_name"),
            "url": card.get("source_url"),
            "publisher": card.get("source_publisher"),
            "year": card.get("source_year"),
        },
        "local_metadata": dict(metadata),
        "prefilled_at": now_utc().isoformat(),
    }


def run_prefill(
    card: Mapping[str, Any],
    raw_text: str,
    *,
    policy: Any,
    dedup_query: DedupQuery,
    local_pool: Any | None = None,
    chunk_chars: int = DEFAULT_CHUNK_CHARS,
    overlap_chars: int = DEFAULT_OVERLAP_CHARS,
) -> PrefillResult:
    """工序①主入口：解析→元数据→查重预检→分块计量→骨架预填（零 API）。

    :param local_pool: 可选 LocalLlmPool（ duck-typed）；缺席=queue（排队不升级 API）。
    """
    prose, code = extract_blocks(raw_text)
    metadata = extract_metadata(raw_text)
    chunks = chunk_text(raw_text, max_chars=chunk_chars, overlap_chars=overlap_chars)
    tokens = sum(estimate_tokens(c) for c in chunks)
    skeleton = prefill_skeleton(card, metadata, policy)
    hits = dedup_precheck(raw_text, dedup_query=dedup_query)
    return PrefillResult(
        prose_blocks=prose,
        code_blocks=code,
        metadata=metadata,
        chunks=chunks,
        tokens_estimate=tokens,
        skeleton=skeleton,
        dedup_hits=hits,
        local_mode="local" if local_pool is not None else "queue",
    )
