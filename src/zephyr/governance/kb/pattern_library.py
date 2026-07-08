# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md
# [MODULE] zephyr.governance.kb.pattern_library
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.integration.shared.schema.schemas; zephyr.shared.utils.time_utils
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_pattern_library | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# AI-generated: T-3-21 Pattern Library
"""
PatternLibrary · 成功模式库（KB refactor 后独立运行，无外部索引）
=====================================================================

Task ID     : T-3-21
Depends     : T-2-10（chromadb_init.py, 已移除）
safety_level: M

核心职责
--------
1. **模式类型**：success_pattern / failure_pattern / anti_pattern
2. **独立运行**：KB refactor 后不再依赖 kb_repo.py 索引
3. **模式检索**：按 domain / layer / pattern_type 查询
4. **CRUD 操作**：创建、读取、查询、删除模式

零外部依赖：仅 pydantic + 标准库。
"""

from __future__ import annotations

from typing import Final
import logging

logger = logging.getLogger(__name__)

import hashlib
import json
import re
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator

from zephyr.integration.shared.schema.schemas import BASE_CONFIG
from zephyr.shared.utils.time_utils import now_iso

__all__ = [
    "DangerousPattern",
    "DangerousPatternLibrary",
    "DangerousPatternMatch",
    "DangerousPatternType",
    "PatternEntry",
    "PatternLibrary",
    "PatternQuery",
    "PatternType",
    "validate_context",
]


# 5.146.6 修复: 正则复杂度校验, 阻止 ReDoS 攻击模式
# 检测嵌套量词 (如 (a+)+, (a*)*) 和过大重复次数 (如 a{999,})
_NESTED_QUANTIFIER_RE = re.compile(r"\([^)]*[+*?][^)]*\)[+*?]")
_MAX_REPEAT = 100


def _validate_regex_safety(pattern: str) -> None:
    """5.146.6 修复: 校验正则复杂度, 阻止已知 ReDoS 攻击模式。

    检测:
    - 嵌套量词: (a+)+, (a*)* 等可导致指数级回溯
    - 过大重复: a{999,} 可导致线性时间攻击
    """
    if _NESTED_QUANTIFIER_RE.search(pattern):
        raise ValueError(f"Blocked ReDoS pattern (nested quantifier): {pattern!r}")
    for m in re.finditer(r"\{(\d+)(?:,(\d*))?\}", pattern):
        low = int(m.group(1))
        high = int(m.group(2)) if m.group(2) else low
        if low > _MAX_REPEAT or high > _MAX_REPEAT:
            raise ValueError(f"Blocked ReDoS pattern (excessive repeat): {pattern!r}")


class PatternType(str, Enum):
    SUCCESS_PATTERN = "success_pattern"
    FAILURE_PATTERN = "failure_pattern"
    ANTI_PATTERN = "anti_pattern"


class PatternEntry(BaseModel):
    model_config = BASE_CONFIG

    pattern_id: str = Field(pattern=r"^PAT-\d{3,}$", description="模式 ID，如 PAT-001")
    title: str = Field(min_length=1, max_length=300)
    pattern_type: PatternType = Field(description="模式类型")
    domain: str = Field(min_length=1, max_length=50, description="所属域 D0-D9")
    layer: str = Field(min_length=1, max_length=20, description="所属层 D_DATA~D_ML_TRAIN")
    description: str = Field(min_length=1, max_length=2000)
    context: str = Field(default="", max_length=2000, description="适用上下文")
    solution: str = Field(default="", max_length=2000, description="解决方案（success）/ 避免方式（anti）")
    consequences: list[str] = Field(default_factory=list, description="后果/影响")
    tags: list[str] = Field(default_factory=list)
    source_ke_id: str | None = Field(default=None, description="来源 KE 编号")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="置信度")
    occurrence_count: int = Field(default=1, ge=1, description="观测次数")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="更新时间")

    @field_validator("tags")
    @classmethod
    def tags_no_duplicates(cls, v: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for tag in v:
            if tag not in seen:
                seen.add(tag)
                result.append(tag)
        return result


class PatternQuery(BaseModel):
    model_config = BASE_CONFIG

    domain: str | None = None
    layer: str | None = None
    pattern_type: PatternType | None = None
    tags: list[str] | None = None
    keyword: str | None = None


def _compute_fingerprint(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


class PatternLibrary:
    """成功模式库，支持 CRUD + 向量检索。

    Parameters
    ----------
    persist_dir : Path | str | None
        持久化目录（用于 JSON 存储）。
    chroma_client : Any | None
        ChromaDB 客户端（用于向量索引）。
    """

    PATTERNS_COLLECTION = "patterns"

    def __init__(
        self,
        persist_dir: Any | None = None,
        chroma_client: Any | None = None,
    ) -> None:
        self._persist_dir = persist_dir
        self._chroma_client = chroma_client
        self._patterns: dict[str, PatternEntry] = {}
        self._next_id: int = 1

    def create(
        self,
        title: str,
        pattern_type: PatternType,
        domain: str,
        layer: str,
        description: str,
        context: str = "",
        solution: str = "",
        consequences: list[str] | None = None,
        tags: list[str] | None = None,
        source_ke_id: str | None = None,
        confidence: float = 1.0,
    ) -> PatternEntry:
        now_iso_val = now_iso()
        now_dt = datetime.fromisoformat(now_iso_val)
        pattern_id = f"PAT-{self._next_id:03d}"
        self._next_id += 1
        entry = PatternEntry(
            pattern_id=pattern_id,
            title=title,
            pattern_type=pattern_type,
            domain=domain,
            layer=layer,
            description=description,
            context=context,
            solution=solution,
            consequences=consequences or [],
            tags=tags or [],
            source_ke_id=source_ke_id,
            confidence=confidence,
            created_at=now_dt,
            updated_at=now_dt,
        )
        self._patterns[pattern_id] = entry
        self._index_to_chroma(entry)
        return entry

    def get(self, pattern_id: str) -> PatternEntry | None:
        return self._patterns.get(pattern_id)

    def query(self, query: PatternQuery) -> list[PatternEntry]:
        results = list(self._patterns.values())
        if query.domain is not None:
            results = [p for p in results if p.domain == query.domain]
        if query.layer is not None:
            results = [p for p in results if p.layer == query.layer]
        if query.pattern_type is not None:
            results = [p for p in results if p.pattern_type == query.pattern_type]
        if query.tags is not None and query.tags:
            tag_set = {t.lower() for t in query.tags}
            results = [p for p in results if tag_set & {t.lower() for t in p.tags}]
        if query.keyword is not None:
            kw = query.keyword.lower()
            results = [
                p for p in results if kw in p.title.lower() or kw in p.description.lower() or kw in p.context.lower()
            ]
        return results

    def delete(self, pattern_id: str) -> bool:
        entry = self._patterns.pop(pattern_id, None)
        if entry is None:
            return False
        self._delete_from_chroma(pattern_id)
        return True

    def update(
        self,
        pattern_id: str,
        **fields: Any,
    ) -> PatternEntry | None:
        entry = self._patterns.get(pattern_id)
        if entry is None:
            return None
        for key, value in fields.items():
            if hasattr(entry, key):
                setattr(entry, key, value)
        entry.updated_at = datetime.fromisoformat(now_iso())
        self._index_to_chroma(entry)
        return entry

    def list_all(self) -> list[PatternEntry]:
        return list(self._patterns.values())

    def count(self) -> int:
        return len(self._patterns)

    def _index_to_chroma(self, entry: PatternEntry) -> None:
        if self._chroma_client is None:
            return
        try:
            col = self._chroma_client.get_collection(name=self.PATTERNS_COLLECTION)
        except Exception:
            try:
                col = self._chroma_client.create_collection(
                    name=self.PATTERNS_COLLECTION,
                    metadata={"hnsw:space": "cosine"},
                )
            except Exception:
                return
        content = f"{entry.title}\n{entry.description}\n{entry.context}\n{entry.solution}"
        meta = {
            "pattern_id": entry.pattern_id,
            "pattern_type": entry.pattern_type.value,
            "domain": entry.domain,
            "layer": entry.layer,
            "tags": json.dumps(entry.tags),
            "confidence": entry.confidence,
        }
        chunk_id = f"{entry.pattern_id}-chunk-0"
        col.upsert(ids=[chunk_id], documents=[content], metadatas=[meta])

    def _delete_from_chroma(self, pattern_id: str) -> None:
        if self._chroma_client is None:
            return
        try:
            col = self._chroma_client.get_collection(name=self.PATTERNS_COLLECTION)
            chunk_id = f"{pattern_id}-chunk-0"
            col.delete(ids=[chunk_id])
        except Exception as e:
            logger.warning("suppressed error in pattern_library", exc_info=True)

    def search(
        self,
        query_text: str,
        n_results: int = 5,
        pattern_type: PatternType | None = None,
        domain: str | None = None,
    ) -> list[dict[str, Any]]:
        if self._chroma_client is None:
            return []
        try:
            col = self._chroma_client.get_collection(name=self.PATTERNS_COLLECTION)
        except Exception:
            return []
        where_conditions: list[dict[str, Any]] = []
        if pattern_type is not None:
            where_conditions.append({"pattern_type": pattern_type.value})
        if domain is not None:
            where_conditions.append({"domain": domain})
        chroma_where: dict[str, Any] | None = None
        if len(where_conditions) == 1:
            chroma_where = where_conditions[0]
        elif len(where_conditions) > 1:
            chroma_where = {"$and": where_conditions}
        try:
            kwargs: dict[str, Any] = {
                "query_texts": [query_text],
                "n_results": n_results,
            }
            if chroma_where is not None:
                kwargs["where"] = chroma_where
            results = col.query(**kwargs)
        except Exception:
            return []
        hits: list[dict[str, Any]] = []
        if not results["ids"] or not results["ids"][0]:
            return hits
        ids = results["ids"][0]
        distances = results["distances"][0] if results.get("distances") else [0.0] * len(ids)
        docs = results["documents"][0] if results.get("documents") else [""] * len(ids)
        metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(ids)
        for chunk_id, dist, doc, meta in zip(ids, distances, docs, metas, strict=False):
            hits.append(
                {
                    "chunk_id": chunk_id,
                    "score": round(1.0 - dist, 4),
                    "content": doc,
                    "metadata": meta,
                }
            )
        return hits


class DangerousPatternType(str, Enum):
    """VALIDATE 阶段已知危险模式分类。

    三类恶意内容：
      - PROMPT_INJECTION    : 恶意指令注入
      - SENSITIVE_INFO_LEAK : 项目敏感信息泄露
      - DANGEROUS_TOOL_CALL : 危险工具调用建议
    """

    PROMPT_INJECTION = "prompt_injection"
    SENSITIVE_INFO_LEAK = "sensitive_info_leak"
    DANGEROUS_TOOL_CALL = "dangerous_tool_call"


class DangerousPattern(BaseModel):
    """已知危险模式条目。"""

    model_config = BASE_CONFIG

    pattern_id: str = Field(min_length=1, description="模式 ID，如 DNG-001")
    pattern_type: DangerousPatternType
    name: str = Field(min_length=1, max_length=200, description="模式名称")
    detection: str = Field(min_length=1, description="检测规则（正则表达式或关键词）")
    severity: str = Field(default="error", description="严重级别：error/warn/flag")
    description: str = Field(default="", description="模式说明")
    fix_hint: str = Field(default="", description="修复建议")


class DangerousPatternMatch(BaseModel):
    """危险模式匹配结果。"""

    model_config = BASE_CONFIG

    pattern: DangerousPattern
    matched_text: str = Field(default="", description="匹配到的文本片段")
    position_start: int = Field(default=0, ge=0, description="匹配起始位置")
    position_end: int = Field(default=0, ge=0, description="匹配结束位置")


KNOWN_DANGEROUS_PATTERNS: Final[list[DangerousPattern]] = [
    DangerousPattern(
        pattern_id="DNG-001",
        pattern_type=DangerousPatternType.PROMPT_INJECTION,
        name="Ignore Previous Instructions",
        detection=r"(?i)ignore\s+(all\s+)?(previous|above|prior)\s+(instructions?|directions?|prompts?)",
        severity="error",
        description="提示词注入——要求忽略之前的指令",
        fix_hint="LSG 拒绝 -> 移除包含此模式的文本块",
    ),
    DangerousPattern(
        pattern_id="DNG-002",
        pattern_type=DangerousPatternType.PROMPT_INJECTION,
        name="You Are Now DAN",
        detection=r"(?i)(you\s+are\s+now\s+(dan|developer\s+mode)|jailbreak|bypass\s+safety)",
        severity="error",
        description="提示词注入——DAN/Jailbreak 攻击",
        fix_hint="LSG 拒绝 -> 移除包含此模式的文本块",
    ),
    DangerousPattern(
        pattern_id="DNG-003",
        pattern_type=DangerousPatternType.PROMPT_INJECTION,
        name="System Prompt Override",
        detection=r"(?i)(new\s+system\s+(prompt|instruction|role)|override\s+system|act\s+as\s+a\s+different)",
        severity="error",
        description="提示词注入——覆盖系统提示词",
        fix_hint="LSG 拒绝 -> 移除包含此模式的文本块",
    ),
    DangerousPattern(
        pattern_id="DNG-004",
        pattern_type=DangerousPatternType.SENSITIVE_INFO_LEAK,
        name="API Key Exposure",
        detection=r"(?i)(api[_-]?key\s*[=:]\s*[\"']?[a-zA-Z0-9_\-]{20,}|sk-[a-zA-Z0-9]{32,}|ghp_[a-zA-Z0-9]{36,})",
        severity="error",
        description="敏感信息泄露——API Key / Token",
        fix_hint="LSG 拒绝 -> 移除包含凭据的文本块；检查 git history 是否已泄露",
    ),
    DangerousPattern(
        pattern_id="DNG-005",
        pattern_type=DangerousPatternType.SENSITIVE_INFO_LEAK,
        name="Private Key Exposure",
        detection=r"-----BEGIN\s+(RSA|EC|DSA|OPENSSH|PGP)\s+PRIVATE\s+KEY-----",
        severity="error",
        description="敏感信息泄露——私钥",
        fix_hint="LSG 拒绝 -> 移除包含私钥的文本块",
    ),
    DangerousPattern(
        pattern_id="DNG-006",
        pattern_type=DangerousPatternType.SENSITIVE_INFO_LEAK,
        name="Database Credential Exposure",
        detection=r"(?i)(connection[_-]?string|database[_-]?url|db[_-]?password)\s*[=:]\s*[\"']?[^\"'\s]{8,}",
        severity="error",
        description="敏感信息泄露——数据库连接凭据",
        fix_hint="LSG 拒绝 -> 移除包含凭据的文本块",
    ),
    DangerousPattern(
        pattern_id="DNG-007",
        pattern_type=DangerousPatternType.DANGEROUS_TOOL_CALL,
        name="Delete All Files",
        detection=r"(?i)(rm\s+-rf\s+/|del\s+/[fsq]|format\s+[cdef]:|drop\s+table\s+\w+\s*(cascade)?)",
        severity="error",
        description="危险工具调用——删除/格式化操作",
        fix_hint="LSG 拒绝 -> 移除危险工具调用建议；标记 session.degraded=true",
    ),
    DangerousPattern(
        pattern_id="DNG-008",
        pattern_type=DangerousPatternType.DANGEROUS_TOOL_CALL,
        name="Execute Arbitrary Code",
        detection=r"(?i)(exec\s*\(|eval\s*\(|subprocess\.(call|popen|run)\s*\()",
        severity="warn",
        description="危险工具调用——执行任意代码",
        fix_hint="LSG 警告 -> 人工审核该工具调用",
    ),
    DangerousPattern(
        pattern_id="DNG-009",
        pattern_type=DangerousPatternType.DANGEROUS_TOOL_CALL,
        name="Network Penetration Tool",
        detection=r"(?i)(nmap|metasploit|wireshark|tcpdump|hydra|john\s+the\s+ripper)",
        severity="warn",
        description="危险工具调用——网络渗透工具",
        fix_hint="LSG 警告 -> 人工审核该工具调用",
    ),
    DangerousPattern(
        pattern_id="DNG-010",
        pattern_type=DangerousPatternType.PROMPT_INJECTION,
        name="Token Smuggling",
        detection=r"(?i)(concatenate|join.*answer|split.*across|hidden.*instruction|steganography)",
        severity="warn",
        description="提示词注入——Token 走私/隐藏指令",
        fix_hint="LSG 拒绝 -> 移除包含此模式的文本块",
    ),
]


class DangerousPatternLibrary:
    """VALIDATE 阶段已知危险模式扫描器。

    通过正则表达式检测三类恶意内容：
      1. Prompt injection——恶意指令注入
      2. 项目敏感信息泄露
      3. 危险工具调用建议

    Using::

        lib = DangerousPatternLibrary()
        matches = lib.scan(context_text)
        if matches:
            for m in matches:
                print(f"[{m.pattern.severity}] {m.pattern.name}: {m.matched_text[:50]}")
    """

    def __init__(
        self,
        patterns: list[DangerousPattern] | None = None,
    ) -> None:
        self._patterns = patterns or KNOWN_DANGEROUS_PATTERNS
        self._compiled: dict[str, re.Pattern[str]] = {}
        for p in self._patterns:
            try:
                # 5.146.6 修复: 编译前校验正则复杂度, 阻止 ReDoS 攻击模式
                _validate_regex_safety(p.detection)
                self._compiled[p.pattern_id] = re.compile(p.detection)
            except (re.error, ValueError):
                pass

    @property
    def pattern_count(self) -> int:
        return len(self._patterns)

    def scan(self, text: str) -> list[DangerousPatternMatch]:
        """扫描文本，返回所有匹配的危险模式。

        Parameters
        ----------
        text : str
            待扫描的上下文文本

        Returns
        -------
        list[DangerousPatternMatch]
            按位置排序的匹配结果列表
        """
        matches: list[DangerousPatternMatch] = []
        seen_patterns: set[str] = set()

        for pattern in self._patterns:
            compiled = self._compiled.get(pattern.pattern_id)
            if compiled is None:
                continue
            for m in compiled.finditer(text):
                if pattern.pattern_id not in seen_patterns:
                    seen_patterns.add(pattern.pattern_id)
                matches.append(
                    DangerousPatternMatch(
                        pattern=pattern,
                        matched_text=m.group(0),
                        position_start=m.start(),
                        position_end=m.end(),
                    )
                )

        matches.sort(key=lambda x: x.position_start)
        return matches

    def scan_by_type(
        self,
        text: str,
        pattern_type: DangerousPatternType,
    ) -> list[DangerousPatternMatch]:
        """按特定类型扫描文本。

        Parameters
        ----------
        text : str
            待扫描文本
        pattern_type : DangerousPatternType
            要检测的危险模式类型
        """
        all_matches = self.scan(text)
        return [m for m in all_matches if m.pattern.pattern_type == pattern_type]

    def has_dangerous_patterns(self, text: str) -> bool:
        """快速检查文本是否包含任何危险模式。"""
        for pattern in self._patterns:
            compiled = self._compiled.get(pattern.pattern_id)
            if compiled is not None and compiled.search(text):
                return True
        return False

    def get_patterns_by_type(
        self,
        pattern_type: DangerousPatternType,
    ) -> list[DangerousPattern]:
        """返回指定类型的所有危险模式。"""
        return [p for p in self._patterns if p.pattern_type == pattern_type]


_default_dangerous_library: DangerousPatternLibrary | None = None


def validate_context(
    text: str,
    *,
    library: DangerousPatternLibrary | None = None,
    max_retries: int = 3,
) -> tuple[str, list[DangerousPatternMatch]]:
    """VALIDATE 阶段入口——扫描上下文并移除危险内容。

    处理流程：
      1. 扫描危险模式
      2. 移除匹配的文本块
      3. 最多 max_retries 次循环
      4. 第 3 次仍被拒绝 -> 丢弃该块并标记

    Parameters
    ----------
    text : str
        待验证的上下文文本
    library : DangerousPatternLibrary | None
        模式扫描器；None 时使用默认实例
    max_retries : int
        最多重试次数（默认 3）

    Returns
    -------
    tuple[str, list[DangerousPatternMatch]]
        (清理后文本, 被移除的匹配列表)
    """
    lib = library or _get_default_library()
    removed: list[DangerousPatternMatch] = []
    cleaned = text

    for _attempt in range(max_retries):
        matches = lib.scan(cleaned)
        if not matches:
            break

        error_matches = [m for m in matches if m.pattern.severity == "error"]
        if not error_matches and _attempt > 0:
            break

        to_remove = [m for m in matches if m.pattern.severity == "error"]
        if not to_remove:
            to_remove = matches[:1]

        for m in to_remove:
            removed.append(m)
            cleaned = _remove_match(cleaned, m)

    return cleaned, removed


def _get_default_library() -> DangerousPatternLibrary:
    global _default_dangerous_library
    if _default_dangerous_library is None:
        _default_dangerous_library = DangerousPatternLibrary()
    return _default_dangerous_library


def _remove_match(text: str, match: DangerousPatternMatch) -> str:
    lines = text.split("\n")
    start_line = text[: match.position_start].count("\n")
    end_line = text[: match.position_end].count("\n")

    block_start = max(0, start_line - 1)
    block_end = min(len(lines), end_line + 2)

    kept = lines[:block_start] + lines[block_end:]
    return "\n".join(kept)
