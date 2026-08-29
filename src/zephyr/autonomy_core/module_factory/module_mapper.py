# [BLUEPRINT] MOD-FACTORY-002 | docs/03_modules/_domain_autonomy_core/module_mapper/blueprint.md | §
# [MODULE] zephyr.autonomy_core.module_factory.module_mapper
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.module_factory.knowledge_classifier（ClassificationResult/KnowledgeItem 类型）；zephyr.integration.llm_runtime_gateway（仅消费既有 infer 签名，不改其源文件）；zephyr.shared.io.paths(REPO_ROOT SSoT)；pyyaml（注册表 YAML 只读加载）；sqlite3 FTS5（进程内 :memory: 检索索引）
# [CONSUMERS] 模块工厂流水线人工编排（Phase 1 手动触发；产出 ModuleSpec 供人审台）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 产出=建议草稿，100% human_gated；注册表 YAML 一律只读（不写不改）；embedding 通道不可用时降级 FTS5-only 并在产出中显式标注；裁决理由全留痕（人审可读）；四选一裁决之外不产隐式第五态（fail-closed=verdict:error）
# [MODIFY-GUARD] 变更须同步 13号文 §3.3
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] 构造期阈值非法/语料注入类型错误 -> ModuleMapperError；classify 未通过（verdict!=classified）的知识强行映射 -> ModuleMapperError；schema_plan 生成 LLM 失败/JSON 校验失败 -> ModuleSpec(verdict="error") 不抛（fail-closed）；注册表 YAML 缺失/解析失败 -> ModuleMapperError
# [TESTS] tests/autonomy/test_module_mapper.py
# [A_module] module_id=MOD-FACTORY-002 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent

"""module_mapper — MOD-FACTORY-002 知识→模块映射引擎（13号文 §3.3，Phase 1）
========================================================================================

模块工厂六环节之"知识→模块映射"（核心独创环节）。三段映射：

1. **语义抽象**：生成 schema_plan={event, context, qualities, direction, output}
   （62号文 v1.19.0 已预留字段，对标 AlphaSchema；LLM 生成，严格 JSON 校验，
   失败 fail-closed）。调用方也可直接提供 schema_plan 跳过 LLM。
2. **双通道语义检索**：embedding 通道（注入 EmbeddingRouter 兼容对象，缺省/异常
   时降级 FTS5-only 并显式标注）+ SQLite FTS5 通道（进程内 :memory: 索引，
   CJK 单字+双字 tokenize）。检索范围=factor_registry.yaml + strategy_registry.yaml
   （catalogs 落盘 YAML，**只读**；含已退役条目=失效墓园，命中即告警防重新发明）。
3. **四选一裁决**：new_entry / variant_of / reject_duplicate / combination，
   阈值全配置化（MapperThresholds），裁决理由留痕（人审可读）。

输出 ModuleSpec={目标 registry + 条目草稿（schema MUST 字段预填）+ 代码骨架规格 +
验证计划}。产出 100% human_gated：本模块不写任何注册表 YAML、不做自动入库。
"""

from __future__ import annotations

import json
import logging
import math
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final, Mapping, Protocol, Sequence, runtime_checkable

import yaml

from zephyr.autonomy_core.module_factory.knowledge_classifier import (
    ClassificationResult,
    KnowledgeItem,
)
from zephyr.shared.io.paths import REPO_ROOT

__all__: Final = [
    "DEFAULT_CATALOGS_DIR",
    "DEFAULT_THRESHOLDS",
    "DEFAULT_VERIFICATION_PLAN",
    "MAPPER_TASK_TYPE",
    "MatchCandidate",
    "ModuleMapper",
    "ModuleMapperError",
    "ModuleSpec",
    "MapperThresholds",
    "RegistryEntryDoc",
    "load_registry_entries",
]

_log = logging.getLogger(__name__)

MAPPER_TASK_TYPE: Final[str] = "module_factory_schema_plan"

DEFAULT_CATALOGS_DIR: Final[Path] = (
    REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs"
)
_FACTOR_REGISTRY_FILE: Final[str] = "factor_registry.yaml"
_STRATEGY_REGISTRY_FILE: Final[str] = "strategy_registry.yaml"

SCHEMA_PLAN_KEYS: Final[tuple[str, ...]] = ("event", "context", "qualities", "direction", "output")

# 其他分流路由表（13号文 §3.2 主分类 3 / §3.6 双通道；Phase 1 检索范围仅 factor/strategy，
# 其他类不检索直接路由，人审处理）
_OTHER_ROUTING: Final[dict[str, str]] = {
    "risk_rule": "risk_limit_registry",
    "execution_algo": "execution_algo_registry",
    "data_asset": "data_asset_registry",
    "technical_indicator": "technical_indicator_registry",
    "tool": "candidate_module_registry",
    "knowledge_only": "knowledge_article_registry",
}

_RETIRED_STATUSES: Final[frozenset[str]] = frozenset({"retired", "deprecated", "decayed"})

DEFAULT_VERIFICATION_PLAN: Final[tuple[str, ...]] = (
    "L1 静态验证：AST 安全扫描 + 复杂度上限 + 词表合规（复用 skill_sandbox，13号文 §3.5）",
    "L2 回测验证：C-003 全量回测 + 过拟合检测（阈值以 62号文 §4.13 G1/G2 为真源）",
    "L3 合规验证：A股规则模拟（T+1 / 涨跌停不可成交 / 融券受限 / PIT 防前视）",
    "L4 人工审核：人审台批量批准/驳回（62号文 G8 人工签批，不可降级）",
)

_EMBEDDING_COLLECTION: Final[str] = "knowledge"  # EmbeddingRouter BGE-M3 路由集合
_EMBED_TEXT_MAX_CHARS: Final[int] = 2000
_FTS_TABLE: Final[str] = "module_factory_fts"
_FTS_CANDIDATE_LIMIT: Final[int] = 200


class ModuleMapperError(Exception):
    """模块映射器构造/调用契约错误（占位 ZA-FACTORY-UNREGISTERED-002）。"""


@runtime_checkable
class EmbedderProtocol(Protocol):
    """嵌入通道注入契约——对齐 EmbeddingRouter.embed(text, collection_name) 签名。

    返回一维浮点向量（list/tuple/np.ndarray 均可，本模块转 tuple[float]）。
    测试注入 fake；None=embedding 通道缺失 -> 降级 FTS5-only 并显式标注。
    """

    def embed(self, text: str, collection_name: str) -> Any: ...


@dataclass(frozen=True)
class MapperThresholds:
    """重复/变体/组合判定阈值（配置参数化；0<combination<variant<duplicate<1 构造期校验）。"""

    duplicate: float = 0.90
    variant: float = 0.70
    combination: float = 0.45
    combination_min_components: int = 2
    embedding_weight: float = 0.6
    fts_weight: float = 0.4
    max_candidates: int = 5


DEFAULT_THRESHOLDS: Final = MapperThresholds()


@dataclass(frozen=True)
class RegistryEntryDoc:
    """注册表检索文档（只读语料；retired=True 即失效墓园条目）。"""

    entry_id: str
    registry: str  # factor_registry / strategy_registry
    name: str
    status: str
    retired: bool
    text: str


@dataclass(frozen=True)
class MatchCandidate:
    """单个候选匹配（双通道分数留痕，fts/embedding 缺失侧为 None）。"""

    entry_id: str
    registry: str
    name: str
    status: str
    retired: bool
    score: float
    fts_score: float | None
    embedding_score: float | None


@dataclass(frozen=True)
class ModuleSpec:
    """映射裁决产出（建议草稿，100% human_gated；不写注册表 YAML）。

    verdict: new_entry / variant_of / reject_duplicate / combination /
             routed（其他分流，未经 factor/strategy 检索） / error（fail-closed）。
    """

    verdict: str
    target_registry: str
    schema_plan: dict[str, str]
    entry_draft: dict[str, Any] | None
    code_skeleton: dict[str, Any] | None
    verification_plan: tuple[str, ...]
    candidates: tuple[MatchCandidate, ...]
    draft_notes: tuple[str, ...]
    rationale: str
    retrieval_channel: str  # dual / fts_only / none
    degraded: bool
    degradation_reason: str | None
    human_gate_required: bool = True


# ── CJK FTS5 分词（unicode61 不切中文 -> 单字+双字 token 化，确定性离线实现）──
_ASCII_WORD_RE: Final = re.compile(r"[a-z0-9_]+")
_CJK_CHAR_RE: Final = re.compile(r"[一-鿿]")


def _tokenize(text: str) -> list[str]:
    """文本 -> FTS5 词元：ASCII 词（小写）+ CJK 单字 + CJK 相邻双字。"""
    tokens = _ASCII_WORD_RE.findall(text.lower())
    cjk = _CJK_CHAR_RE.findall(text)
    tokens.extend(cjk)
    tokens.extend(a + b for a, b in zip(cjk, cjk[1:]))
    return tokens


def _cosine(a: Sequence[float], b: Sequence[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


def _flatten_text(value: Any) -> str:
    """任意嵌套（list/dict/标量/None）-> 空格连接文本（检索语料用）。"""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, Mapping):
        return " ".join(_flatten_text(v) for v in value.values())
    if isinstance(value, (list, tuple, set)):
        return " ".join(_flatten_text(v) for v in value)
    return str(value)


def _normalize_entry(raw: Mapping[str, Any], registry: str) -> RegistryEntryDoc:
    entry_id = str(raw.get("factor_id") or raw.get("strategy_id") or "")
    if not entry_id:
        raise ModuleMapperError(f"注册表条目缺 factor_id/strategy_id: {registry}")
    status = str(raw.get("status") or raw.get("lifecycle_status") or "")
    text = " ".join(
        part
        for part in (
            entry_id,
            _flatten_text(raw.get("name")),
            _flatten_text(raw.get("name_zh")),
            _flatten_text(raw.get("aliases")),
            _flatten_text(raw.get("factor_class") or raw.get("strategy_class")),
            _flatten_text(raw.get("formula")),
            _flatten_text(raw.get("entry_logic")),
            _flatten_text(raw.get("exit_logic")),
            _flatten_text(raw.get("position_sizing")),
            _flatten_text(raw.get("alpha_source")),
            _flatten_text(raw.get("tags")),
            _flatten_text(raw.get("schema_plan")),
            _flatten_text(raw.get("code_symbol")),
        )
        if part
    )
    return RegistryEntryDoc(
        entry_id=entry_id,
        registry=registry,
        name=str(raw.get("name_zh") or raw.get("name") or ""),
        status=status,
        retired=status in _RETIRED_STATUSES,
        text=text,
    )


def load_registry_entries(catalogs_dir: Path | str | None = None) -> tuple[RegistryEntryDoc, ...]:
    """只读加载 factor_registry.yaml + strategy_registry.yaml 为检索语料。

    本函数与 ModuleMapper 对注册表 YAML 一律只读（13号文 §4.5：写操作仅 candidate
    追加且非本模块职责）。文件缺失/解析失败 -> ModuleMapperError（fail-closed）。
    """
    base = Path(catalogs_dir) if catalogs_dir is not None else DEFAULT_CATALOGS_DIR
    docs: list[RegistryEntryDoc] = []
    for filename, key, registry in (
        (_FACTOR_REGISTRY_FILE, "factors", "factor_registry"),
        (_STRATEGY_REGISTRY_FILE, "strategies", "strategy_registry"),
    ):
        path = base / filename
        if not path.is_file():
            raise ModuleMapperError(f"注册表 YAML 缺失: {path}")
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            raise ModuleMapperError(f"注册表 YAML 解析失败: {path}: {exc}") from exc
        entries = (data or {}).get(key) or []
        for raw in entries:
            if isinstance(raw, Mapping):
                docs.append(_normalize_entry(raw, registry))
    return tuple(docs)


# ── schema_plan LLM 生成 prompt（13号文 §3.3 ① 语义抽象）──
_SCHEMA_PLAN_SYSTEM: Final = (
    "你是量化因子/策略语义抽象器。你只输出一个 JSON 对象，不输出任何其他文字。"
)
_SCHEMA_PLAN_PROMPT: Final = """把以下已分类知识抽象为 schema_plan 五字段语义计划（AlphaSchema 式，
先语义后实现：同一语义可换实现公式，同一公式可回溯经济含义）。

严格输出 JSON（不要任何额外文字），键名严格为：
{{
  "event": "触发事件/信号条件（何时进场/何时计算）",
  "context": "适用上下文（市场环境/板块/标的前提）",
  "qualities": "标的质地要求（筛选条件/过滤维度）",
  "direction": "经济方向（做多/做空什么，赚什么钱）",
  "output": "输出语义（排序分/触发信号/目标权重及经济含义一句话）"
}}
五字段均为非空字符串，不得多键少键。

【知识条目】
标题：{title}
分类：{kind_desc}
多维标注：{annotation}
正文：
{content}
"""


def _extract_json_obj(text: str) -> dict[str, Any]:
    """LLM 输出 -> JSON dict（裸 JSON -> 首尾花括号截取）；失败抛 ValueError。"""
    stripped = text.strip()
    if not stripped:
        raise ValueError("LLM 输出为空")
    try:
        obj = json.loads(stripped)
        if isinstance(obj, dict):
            return obj
    except json.JSONDecodeError:
        pass
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start != -1 and end > start:
        obj = json.loads(stripped[start : end + 1])
        if isinstance(obj, dict):
            return obj
    raise ValueError("LLM 输出中未找到可解析的 JSON 对象")


def _validate_schema_plan(raw: Mapping[str, Any]) -> dict[str, str]:
    """schema_plan 严格校验：恰好五键、全为非空字符串；失败抛 ValueError。"""
    keys = set(raw.keys())
    if keys != set(SCHEMA_PLAN_KEYS):
        raise ValueError(f"schema_plan 键集不符（期望 {SCHEMA_PLAN_KEYS}）: {sorted(keys)}")
    plan: dict[str, str] = {}
    for key in SCHEMA_PLAN_KEYS:
        value = raw[key]
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"schema_plan.{key} 必须为非空字符串")
        plan[key] = value.strip()
    return plan


class ModuleMapper:
    """知识→模块映射引擎（三段映射：schema_plan -> 双通道检索 -> 四选一裁决）。

    - llm：schema_plan 生成用网关（LLMInferProtocol 兼容；缺省懒构造真实网关）。
      调用方直接提供 schema_plan 时完全不触发 LLM。
    - embedder：embedding 通道（EmbedderProtocol 兼容，如 EmbeddingRouter）；
      None 或调用异常 -> 降级 FTS5-only，ModuleSpec.degraded=True 显式标注。
    - entries：检索语料直接注入（测试/离线）；None -> 懒加载 catalogs YAML（只读）。
    - fts_connection：FTS5 索引宿主 sqlite 连接注入（测试隔离）；None -> 自建 :memory:。
    """

    def __init__(
        self,
        *,
        llm: Any | None = None,
        embedder: Any | None = None,
        catalogs_dir: Path | str | None = None,
        entries: Sequence[RegistryEntryDoc | Mapping[str, Any]] | None = None,
        thresholds: MapperThresholds = DEFAULT_THRESHOLDS,
        fts_connection: sqlite3.Connection | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.1,
    ) -> None:
        t = thresholds
        if not (0.0 < t.combination < t.variant < t.duplicate < 1.0):
            raise ModuleMapperError(
                f"阈值须满足 0<combination<variant<duplicate<1: "
                f"{t.combination}/{t.variant}/{t.duplicate}"
            )
        if t.embedding_weight <= 0 or t.fts_weight <= 0:
            raise ModuleMapperError("通道权重必须为正")
        if t.combination_min_components < 2:
            raise ModuleMapperError("combination_min_components 必须 >=2（组合=多条目）")
        if t.max_candidates < 1:
            raise ModuleMapperError("max_candidates 必须 >=1")
        self._llm = llm
        self._embedder = embedder
        self._catalogs_dir = catalogs_dir
        self._injected_entries = tuple(entries) if entries is not None else None
        self._thresholds = t
        self._fts_conn = fts_connection
        self._owns_fts_conn = fts_connection is None
        self._max_tokens = max_tokens
        self._temperature = temperature
        # 懒建索引状态
        self._docs: tuple[RegistryEntryDoc, ...] | None = None
        self._embeddings: tuple[tuple[float, ...], ...] | None = None
        self._embedding_disabled_reason: str | None = None
        self._fts_ready = False

    # ── 索引构建（懒，首次 map 时）──

    def _resolve_llm(self) -> Any:
        if self._llm is None:
            from zephyr.integration.llm_runtime_gateway import LLMRuntimeGateway

            self._llm = LLMRuntimeGateway()
        return self._llm

    def _ensure_index(self) -> None:
        if self._docs is not None:
            return
        if self._injected_entries is not None:
            docs: list[RegistryEntryDoc] = []
            for item in self._injected_entries:
                if isinstance(item, RegistryEntryDoc):
                    docs.append(item)
                elif isinstance(item, Mapping):
                    registry = str(item.get("registry") or "").strip()
                    if not registry:
                        registry = (
                            "factor_registry" if item.get("factor_id") else "strategy_registry"
                        )
                    docs.append(_normalize_entry(item, registry))
                else:
                    raise ModuleMapperError(f"语料条目类型不支持: {type(item).__name__}")
            self._docs = tuple(docs)
        else:
            self._docs = load_registry_entries(self._catalogs_dir)

        if self._fts_conn is None:
            self._fts_conn = sqlite3.connect(":memory:")
        self._fts_conn.execute(
            f"CREATE VIRTUAL TABLE IF NOT EXISTS {_FTS_TABLE} "
            "USING fts5(entry_id UNINDEXED, content)"
        )
        self._fts_conn.execute(f"DELETE FROM {_FTS_TABLE}")
        self._fts_conn.executemany(
            f"INSERT INTO {_FTS_TABLE} (entry_id, content) VALUES (?, ?)",
            [(d.entry_id, " ".join(_tokenize(d.text))) for d in self._docs],
        )
        self._fts_ready = True

        self._embeddings = None
        self._embedding_disabled_reason = None
        if self._embedder is None:
            self._embedding_disabled_reason = "embedder 未注入（embedding 通道缺失）"
        elif self._docs:
            try:
                vectors = tuple(
                    tuple(float(x) for x in self._embedder.embed(d.text[:_EMBED_TEXT_MAX_CHARS], _EMBEDDING_COLLECTION))
                    for d in self._docs
                )
                self._embeddings = vectors
            except Exception as exc:  # noqa: BLE001 — embedding 通道降级不阻断 FTS5
                _log.warning("module_mapper embedding 语料向量化失败，降级 FTS5-only: %s", exc)
                self._embedding_disabled_reason = f"embedder 异常: {type(exc).__name__}: {exc}"

    # ── ① 语义抽象 ──

    def _generate_schema_plan(
        self, item: KnowledgeItem, classification: Any
    ) -> dict[str, str]:
        cls = classification.classification
        if cls.target_kind == "factor":
            kind_desc = f"factor/{cls.factor_class}"
        elif cls.target_kind == "strategy":
            kind_desc = f"strategy/{cls.strategy_class}"
        else:
            kind_desc = f"other/{cls.other_subtype}"
        annotation = (
            f"primary_timeframe={cls.primary_timeframe}; direction={cls.direction}; "
            f"entry_role={cls.entry_role}; tags={list(cls.tags)}"
        )
        prompt = _SCHEMA_PLAN_PROMPT.format(
            title=item.title,
            kind_desc=kind_desc,
            annotation=annotation,
            content=item.content[:_EMBED_TEXT_MAX_CHARS],
        )
        response = self._resolve_llm().infer(
            MAPPER_TASK_TYPE,
            prompt,
            system=_SCHEMA_PLAN_SYSTEM,
            max_tokens=self._max_tokens,
            temperature=self._temperature,
        )
        if getattr(response, "status", None) != "ok":
            raise ValueError(f"llm_status={getattr(response, 'status', None)!r}")
        return _validate_schema_plan(_extract_json_obj(getattr(response, "text", "") or ""))

    # ── ② 双通道检索 ──

    def _fts_scores(self, query_text: str) -> dict[str, float]:
        """FTS5 通道打分=查询词元覆盖率 |Q∩D|/|Q| ∈[0,1]（确定性，variant 裁决可达）。

        FTS5 MATCH 只做召回过滤（命中≥1 词元），覆盖率在 Python 侧计算——
        bm25 的 min-max 归一化会使 top 候选恒为 1.0，导致 variant 区间不可达。
        """
        q_tokens = set(_tokenize(query_text))
        if not q_tokens or not self._docs:
            return {}
        query = " OR ".join(sorted(q_tokens))
        rows = self._fts_conn.execute(
            f"SELECT entry_id FROM {_FTS_TABLE} "
            f"WHERE {_FTS_TABLE} MATCH ? LIMIT ?",
            (query, _FTS_CANDIDATE_LIMIT),
        ).fetchall()
        matched = {str(r[0]) for r in rows}
        result: dict[str, float] = {}
        for doc in self._docs:
            if doc.entry_id not in matched:
                continue
            d_tokens = set(_tokenize(doc.text))
            result[doc.entry_id] = round(len(q_tokens & d_tokens) / len(q_tokens), 6)
        return result

    def _retrieve(self, query_text: str) -> tuple[tuple[MatchCandidate, ...], str, str | None]:
        """返回 (candidates, retrieval_channel, degradation_reason)。"""
        docs = self._docs or ()
        fts = self._fts_scores(query_text)

        embeddings = self._embeddings
        disabled = self._embedding_disabled_reason
        query_vec: tuple[float, ...] | None = None
        if embeddings is not None and self._embedder is not None:
            try:
                query_vec = tuple(
                    float(x)
                    for x in self._embedder.embed(query_text[:_EMBED_TEXT_MAX_CHARS], _EMBEDDING_COLLECTION)
                )
            except Exception as exc:  # noqa: BLE001 — 查询期 embedding 失败降级
                _log.warning("module_mapper 查询向量化失败，本次降级 FTS5-only: %s", exc)
                disabled = f"embedder 查询异常: {type(exc).__name__}: {exc}"
                query_vec = None

        t = self._thresholds
        candidates: list[MatchCandidate] = []
        if query_vec is not None and embeddings is not None:
            w_sum = t.embedding_weight + t.fts_weight
            for i, doc in enumerate(docs):
                emb = max(0.0, _cosine(query_vec, embeddings[i]))
                fts_score = fts.get(doc.entry_id)
                score = (t.embedding_weight * emb + t.fts_weight * (fts_score or 0.0)) / w_sum
                if score > 0.0:
                    candidates.append(
                        MatchCandidate(
                            entry_id=doc.entry_id,
                            registry=doc.registry,
                            name=doc.name,
                            status=doc.status,
                            retired=doc.retired,
                            score=round(score, 6),
                            fts_score=fts_score,
                            embedding_score=round(emb, 6),
                        )
                    )
            channel = "dual"
            reason = None
        else:
            for doc in docs:
                fts_score = fts.get(doc.entry_id)
                if fts_score is None:
                    continue
                candidates.append(
                    MatchCandidate(
                        entry_id=doc.entry_id,
                        registry=doc.registry,
                        name=doc.name,
                        status=doc.status,
                        retired=doc.retired,
                        score=round(fts_score, 6),
                        fts_score=fts_score,
                        embedding_score=None,
                    )
                )
            channel = "fts_only"
            reason = disabled or "embedding 通道不可用"
        candidates.sort(key=lambda c: (-c.score, c.entry_id))
        return tuple(candidates[: t.max_candidates]), channel, reason

    # ── ③ 四选一裁决 ──

    def _decide(
        self, candidates: tuple[MatchCandidate, ...]
    ) -> tuple[str, MatchCandidate | None, tuple[MatchCandidate, ...]]:
        t = self._thresholds
        if not candidates:
            return "new_entry", None, ()
        top = candidates[0]
        if top.score >= t.duplicate:
            return "reject_duplicate", top, ()
        if top.score >= t.variant:
            return "variant_of", top, ()
        components = tuple(c for c in candidates if c.score >= t.combination)
        if len(components) >= t.combination_min_components:
            return "combination", None, components
        return "new_entry", None, ()

    # ── ModuleSpec 组装 ──

    @staticmethod
    def _frequency_of(primary_timeframe: str | None) -> str | None:
        if primary_timeframe is None:
            return None
        return "daily" if primary_timeframe in ("daily", "weekly", "monthly") else "intraday"

    def _build_factor_draft(
        self,
        item: KnowledgeItem,
        cls: Any,
        schema_plan: dict[str, str],
        parent: MatchCandidate | None,
    ) -> dict[str, Any]:
        return {
            "factor_id": None,  # 人审分配（FCT-{CLASS}-{NNN} 编号纪律）
            "name": item.title,
            "name_zh": item.title,
            "aliases": [],
            "factor_class": cls.factor_class,
            "formula": "",  # Phase 1 人写（受控生成通道属 Phase 2）；schema_plan 已预填
            "params": {},
            "inputs": [],
            "outputs": [],
            "alpha_source": item.source_ref or cls.rationale,
            "frequency": self._frequency_of(cls.primary_timeframe),
            "lookback_period": None,
            "universe": "UNI-RULE-001",
            "benchmark_id": "BMK-INDEX-001",
            "neutralization": "none",
            "pit_policy": None,  # MUST 人审填写（62号文入库硬要求）
            "module_id": None,  # 代码落地后绑定
            "doc_ref": item.source_ref,
            "code_path": "",
            "belongs_to_strategies": [],
            "variant_of": parent.entry_id if parent else None,
            "status": "candidate",
            "algorithm_status": "pending_backtest",
            "evidence": "",
            "discovery_agent": "module_factory",  # #ARCH-286 Q5 裁定批准扩展枚举
            "llm_safety_stack": None,  # Phase 2 受控生成环节回填五声明（discovery_agent!=human MUST）
            "causal_graph": None,  # 注册时 MUST 声明（62号文，防事后合理化）
            "schema_plan": dict(schema_plan),
            "primary_timeframe": cls.primary_timeframe,
            "applicable_timeframes": list(cls.applicable_timeframes),
            "regime_valid": list(cls.regime_valid),
            "regime_invalid": list(cls.regime_invalid),
            "direction": cls.direction,
            "entry_role": cls.entry_role,
            "applies_to": list(cls.applies_to),
            "tags": list(cls.tags),
            "code_symbol": None,
            "code_fingerprint": None,
        }

    def _build_strategy_draft(
        self,
        item: KnowledgeItem,
        cls: Any,
        parent: MatchCandidate | None,
    ) -> dict[str, Any]:
        return {
            "strategy_id": None,  # 人审分配（STR-{CLASS}-{NNN} 编号纪律）
            "name": item.title,
            "name_zh": item.title,
            "aliases": [],
            "strategy_class": cls.strategy_class,
            "sleeve": "alpha",
            "alpha_sources": [],
            "variant_of": parent.entry_id if parent else None,
            "entry_logic": "",  # Phase 1 人写
            "exit_logic": "",
            "position_sizing": "",
            "risk_rules": [],  # MUST 非空（62号文入库硬要求，人审补齐）
            "holding_period": None,
            "benchmark_id": "BMK-INDEX-001",
            "universe_id": "UNI-RULE-001",
            "cost_model_id": None,  # MUST 人审绑定（A4 三件套）
            "module_id": None,
            "doc_ref": item.source_ref,
            "code_path": "",
            "lifecycle_status": "candidate",
            "status": "candidate",
            "origin": "hybrid",  # LLM 分类/映射 + Phase 1 人写代码
            "distilled_to_code": False,
            "algorithm_status": "pending_backtest",
            "evidence": "",
            "primary_timeframe": cls.primary_timeframe,
            "applicable_timeframes": list(cls.applicable_timeframes),
            "regime_valid": list(cls.regime_valid),
            "regime_invalid": list(cls.regime_invalid),
            "direction": cls.direction,
            "entry_role": cls.entry_role,
            "applies_to": list(cls.applies_to),
            "tags": list(cls.tags),
            "code_symbol": None,
            "code_fingerprint": None,
        }

    @staticmethod
    def _build_code_skeleton(
        kind: str, components: tuple[MatchCandidate, ...]
    ) -> dict[str, Any]:
        if kind == "strategy":
            return {
                "form": "strategy_template",
                "sections": ("entry_logic", "exit_logic", "position_sizing"),
                "target_path_hint": "src/zephyr/governance/strategies/（62号文 §6.1.2 策略代码落点）",
                "generation": "Phase 1 人工编写（受控生成通道属 Phase 2，13号文 §3.4）",
                "must_have": (
                    "blueprint 锚定文件头",
                    "code_symbol 锚点",
                    "risk_rules 非空（risk_limit_id 列表）",
                ),
            }
        skeleton: dict[str, Any] = {
            "form": "qlib_expression",
            "fallback_form": "factor_base_template",
            "target_path_hint": "src/zephyr/factor/（62号文 §6.1.1 因子代码落点）",
            "generation": "Phase 1 人工编写（受控生成通道属 Phase 2，13号文 §3.4）",
            "must_have": (
                "blueprint 锚定文件头",
                "code_symbol 锚点",
                "llm_safety_stack 五声明（discovery_agent!=human 时 MUST，Phase 2 回填）",
            ),
        }
        if components:
            skeleton["form"] = "combination"
            skeleton["components"] = [c.entry_id for c in components]
            skeleton["note"] = (
                "多条目组合：对应 62号文 combination_strategy 字段"
                "（regime_detector + allocation_weights），人工组装"
            )
        return skeleton

    # ── 主入口 ──

    def map_knowledge(
        self,
        item: KnowledgeItem,
        classification: ClassificationResult,
        *,
        schema_plan: Mapping[str, str] | None = None,
    ) -> ModuleSpec:
        """映射一条已分类知识 -> ModuleSpec（建议草稿，human_gated）。

        classification.verdict!="classified"（含质量门禁 REJECT）-> ModuleMapperError
        （13号文 §3.1：REJECT 不进分类更不进映射，fail-closed）。
        schema_plan 缺省时经 LLM 生成；生成/校验失败 -> ModuleSpec(verdict="error")。
        """
        if classification is None or getattr(classification, "verdict", None) != "classified":
            raise ModuleMapperError(
                "仅接受 verdict=classified 的分类结果（REJECT/错误知识不进映射，13号文 §3.1）"
            )
        cls = classification.classification
        if cls is None:
            raise ModuleMapperError("分类结果缺 classification 载荷（fail-closed）")

        # 其他分流：不经 factor/strategy 检索，直接路由人审（13号文 §3.2 主分类 3）
        if cls.target_kind == "other":
            target = _OTHER_ROUTING.get(str(cls.other_subtype), "knowledge_article_registry")
            return ModuleSpec(
                verdict="routed",
                target_registry=target,
                schema_plan={},
                entry_draft=None,
                code_skeleton=None,
                verification_plan=DEFAULT_VERIFICATION_PLAN,
                candidates=(),
                draft_notes=("其他分流条目：不走 factor/strategy 检索，人审确认目标注册表后处理",),
                rationale=(
                    f"target_kind=other/{cls.other_subtype} -> 分流至 {target}"
                    "（13号文 §3.2：风控/执行/数据/指标/工具/纯知识分流到对应注册表或候选库）"
                ),
                retrieval_channel="none",
                degraded=False,
                degradation_reason=None,
            )

        # ① 语义抽象
        if schema_plan is not None:
            try:
                plan = _validate_schema_plan(schema_plan)
            except ValueError as exc:
                raise ModuleMapperError(f"调用方提供 schema_plan 非法: {exc}") from exc
        else:
            try:
                plan = self._generate_schema_plan(item, classification)
            except Exception as exc:  # noqa: BLE001 — schema_plan 失败 fail-closed
                _log.warning("module_mapper schema_plan 生成失败: %s", exc)
                return ModuleSpec(
                    verdict="error",
                    target_registry="",
                    schema_plan={},
                    entry_draft=None,
                    code_skeleton=None,
                    verification_plan=DEFAULT_VERIFICATION_PLAN,
                    candidates=(),
                    draft_notes=(),
                    rationale=f"schema_plan 生成/校验失败（fail-closed）: {type(exc).__name__}: {exc}",
                    retrieval_channel="none",
                    degraded=False,
                    degradation_reason=None,
                )

        # ② 双通道检索
        self._ensure_index()
        query_text = " ".join(
            (
                item.title,
                plan["event"],
                plan["context"],
                plan["qualities"],
                plan["direction"],
                plan["output"],
                " ".join(cls.tags),
                str(cls.factor_class or cls.strategy_class or ""),
            )
        )
        candidates, channel, degradation = self._retrieve(query_text)

        # ③ 四选一裁决
        verdict, parent, components = self._decide(candidates)

        target_registry = (
            "factor_registry" if cls.target_kind == "factor" else "strategy_registry"
        )
        rationale_parts: list[str] = [
            f"裁决={verdict}（阈值 duplicate>={self._thresholds.duplicate} / "
            f"variant>={self._thresholds.variant} / combination>={self._thresholds.combination}"
            f"x{self._thresholds.combination_min_components}）"
        ]
        if candidates:
            top_desc = "; ".join(
                f"{c.entry_id}({c.registry}, score={c.score}, retired={c.retired})"
                for c in candidates[:3]
            )
            rationale_parts.append(f"top 候选: {top_desc}")
        else:
            rationale_parts.append("无候选命中（score>0）")
        if verdict == "variant_of" and parent is not None:
            rationale_parts.append(f"变体指向 parent={parent.entry_id}（相关性分组治理字段天然合规）")
        if verdict == "reject_duplicate" and parent is not None:
            rationale_parts.append(f"重复于 {parent.entry_id}——拦截重复造轮子（13号文 §3.3）")
        if verdict == "combination":
            rationale_parts.append(
                f"组合成分: {', '.join(c.entry_id for c in components)}"
            )
        graveyard = [c for c in candidates if c.retired]
        if graveyard:
            rationale_parts.append(
                "⚠ 命中失效墓园条目: "
                + ", ".join(c.entry_id for c in graveyard)
                + "（警惕重新发明已失效因子，人审重点复核）"
            )
        if degradation:
            rationale_parts.append(f"检索降级: {degradation}")

        entry_draft: dict[str, Any] | None = None
        code_skeleton: dict[str, Any] | None = None
        draft_notes: list[str] = []
        if verdict in ("new_entry", "variant_of", "combination"):
            if cls.target_kind == "factor":
                entry_draft = self._build_factor_draft(item, cls, plan, parent)
                draft_notes.extend(
                    (
                        "factor_id 人审分配（FCT-{CLASS}-{NNN}）",
                        "pit_policy / causal_graph MUST 人审填写（62号文入库硬要求）",
                        "formula Phase 1 人写；llm_safety_stack 五声明 Phase 2 生成环节回填",
                    )
                )
            else:
                entry_draft = self._build_strategy_draft(item, cls, parent)
                draft_notes.extend(
                    (
                        "strategy_id 人审分配（STR-{CLASS}-{NNN}）",
                        "entry_logic/exit_logic/position_sizing Phase 1 人写；risk_rules MUST 非空",
                        "cost_model_id MUST 人审绑定（A4 三件套）",
                    )
                )
            code_skeleton = self._build_code_skeleton(cls.target_kind, components)
        draft_notes.append("条目草稿经人审后才可 candidate 追加入库（本模块不写注册表 YAML）")

        return ModuleSpec(
            verdict=verdict,
            target_registry=target_registry,
            schema_plan=plan,
            entry_draft=entry_draft,
            code_skeleton=code_skeleton,
            verification_plan=DEFAULT_VERIFICATION_PLAN,
            candidates=candidates,
            draft_notes=tuple(draft_notes),
            rationale="\n".join(rationale_parts),
            retrieval_channel=channel,
            degraded=channel != "dual",
            degradation_reason=degradation,
        )
