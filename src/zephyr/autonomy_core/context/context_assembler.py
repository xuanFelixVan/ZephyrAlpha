from typing import TYPE_CHECKING
# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md
# [MODULE] zephyr.autonomy_core.context.context_assembler
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.integration.shared.schema.schemas; zephyr.autonomy_core.__init__; zephyr.intelligence.model_evaluation.unified_memory_api; zephyr.intelligence.model_evaluation.reranker; zephyr.governance.__init__
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
# [A_module] module_id=MOD-ORC_context_assembler | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
ContextAssembler — 上下文装配、校验、影子留档
=============================================
依据：MOD-TASK_SYSTEM G3 门禁（上下文装配完整度）+ §3.1 接口契约

四阶段流水线：
  1. collect   — 读取 context_assembly_manifest 中所有文件
  2. assemble  — 拼接为单一上下文字符串
  3. compress  — 超 token 预算时调用 DocCompressor
  4. shadow    — 生成影子副本供脚本系统 B 线复查
"""

from __future__ import annotations

import hashlib
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from zephyr.infrastructure.capacity_assurance.token_budget import DEFAULT_CONTEXT_TOKEN_BUDGET, estimate_tokens
from zephyr.integration.shared.schema.schemas import BASE_CONFIG

from zephyr.autonomy_core.context.context_rule_registry import ContextRuleRegistry  # 5.12.10 修复：移除 if TYPE_CHECKING: 死分支（条件import残留）

__all__ = [
    "AssembledContext",
    "AssemblyError",
    "ContextAssembler",
    "FileEntry",
    "RawContext",
    "build_context",
]


class FileEntry(BaseModel):
    """manifest 中的单条文件记录"""

    model_config = BASE_CONFIG

    file_path: str = Field(..., description="文件完整绝对路径")
    reason: str = Field(default="", description="为什么需要这个文件")
    token_estimate: int = Field(default=0, ge=0, description="预估 token 数")
    exists: bool = Field(default=False)
    readable: bool = Field(default=False)
    encoding: str = Field(default="utf-8")


class AssembledContext(BaseModel):
    """装配后的上下文结构"""

    model_config = BASE_CONFIG

    context_text: str = Field(default="", description="装配后的完整上下文字符串（可能已压缩）")
    raw_context_text: str = Field(
        default="",
        description="压缩前的原始全文；未压缩时为空串以省内存（Anti-Pattern AP4）",
    )
    file_count: int = Field(default=0, ge=0, description="成功读取的文件数")
    total_chars: int = Field(default=0, ge=0, description="总字符数")
    token_estimate: int = Field(default=0, ge=0, description="预估 token 数（按 chars÷4）")
    token_budget: int = Field(default=DEFAULT_CONTEXT_TOKEN_BUDGET, ge=0, description="token 预算上限")
    budget_remaining: int = Field(
        default=DEFAULT_CONTEXT_TOKEN_BUDGET,
        ge=0,
        description="剩余 token 预算",
    )
    was_compressed: bool = Field(default=False, description="是否触发了压缩")
    compressed_size_before: int = Field(default=0, ge=0)
    compressed_size_after: int = Field(default=0, ge=0)
    shadow_path: str = Field(default="", description="影子副本路径")
    shadow_hash: str = Field(default="", description="影子副本 SHA-256")
    entries: list[FileEntry] = Field(default_factory=list, description="逐文件状态")
    errors: list[str] = Field(default_factory=list, description="装配过程中的错误")
    assembled_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())

    @property
    def is_complete(self) -> bool:
        return len(self.errors) == 0 and self.file_count == len(self.entries)

    @property
    def is_within_budget(self) -> bool:
        return self.token_estimate <= self.token_budget


class AssemblyError(Exception):
    """上下文装配异常"""


class ContextAssembler:
    """从 TaskCard 的 context_assembly_manifest 装配执行上下文

    G3 门禁核心：
      - 所有 manifest 文件必须存在且可读
      - 装配后 token 数必须在 token_budget 内
      - 超过预算触发 DocCompressor 压缩
      - 生成影子副本供 B 线审计

    Using::

        assembler = ContextAssembler(max_file_size_mb=5)
        ctx = assembler.assemble(manifest, token_budget=DEFAULT_CONTEXT_TOKEN_BUDGET)
        if not ctx.is_complete:
            raise AssemblyError(ctx.errors)
        assembler.shadow(ctx, output_dir="changes/shadows/")
    """

    def __init__(
        self,
        max_file_size_mb: int = 5,
        require_absolute_paths: bool = True,
        rule_registry: ContextRuleRegistry | None = None,
    ) -> None:
        self._max_bytes = max_file_size_mb * 1024 * 1024
        self._require_absolute = require_absolute_paths
        self._rule_registry = rule_registry

    # ------------------------------------------------------------------
    # 公共 API
    # ------------------------------------------------------------------

    def assemble(
        self,
        manifest: list[dict[str, str]],
        token_budget: int = DEFAULT_CONTEXT_TOKEN_BUDGET,
        *,
        compress: bool = True,
    ) -> AssembledContext:
        """从 context_assembly_manifest 装配上下文

        参数
        ----
        manifest
            TaskCard.context_assembly_manifest ——
            [{"file_path": "D:\\...", "reason": "说明"}, ...]
        token_budget
            允许的最大 token 数（超过触发压缩）
        compress
            是否启用压缩（False = 只组装不压缩，用于调试）

        返回
        ----
        AssembledContext
            装配结果——含上下文文本、文件状态、压缩信息
        """
        entries, errors = self._collect_files(manifest)
        assembled = self._assemble(entries, errors, token_budget)

        if self._rule_registry is not None:
            assembled = self._inject_rules(assembled, token_budget)

        if compress and assembled.token_estimate > token_budget:
            assembled = self._compress_context(assembled, token_budget)

        return assembled

    def validate(self, ctx: AssembledContext) -> bool:
        """G3 门禁校验——上下文是否满足装配要求

        校验规则：
          1. 所有文件存在且可读（errors 为空）
          2. token 数 ≤ 预算（压缩后）
          3. file_count > 0（至少有一个文件）
        """
        return len(ctx.errors) == 0 and ctx.is_within_budget and ctx.file_count > 0

    def shadow(
        self,
        ctx: AssembledContext,
        output_dir: str,
    ) -> Path:
        """生成上下文影子副本——G3 门禁审计证据

        影子副本包含：
          - 装配时间戳
          - 文件清单
          - 完整上下文字符串
          - SHA-256 哈希

        返回
        ----
        Path
            影子副本文件路径
        """
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)

        ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        shadow_path = out / f"context-shadow-{ts}.md"

        sha = hashlib.sha256(ctx.context_text.encode("utf-8")).hexdigest()[:12]

        header = (
            f"# 上下文影子副本 — G3 门禁审计证据\n\n"
            f"- 装配时间：{ctx.assembled_at}\n"
            f"- 文件数：{ctx.file_count}\n"
            f"- 总字符数：{ctx.total_chars}\n"
            f"- Token 估算：{ctx.token_estimate}/{ctx.token_budget}\n"
            f"- 是否压缩：{'是' if ctx.was_compressed else '否'}\n"
            f"- SHA-256（前 12 位）：{sha}\n"
            f"- 错误数：{len(ctx.errors)}\n\n"
            f"---\n\n"
        )

        manifest_section = "## 文件清单\n\n"
        for e in ctx.entries:
            status = "OK" if (e.exists and e.readable) else ("ERR" if not e.exists else "UNREADABLE")
            manifest_section += f"- [{status}] `{e.file_path}` — {e.reason} (est. {e.token_estimate} tokens)\n"
        manifest_section += "\n---\n\n"

        sections = header + manifest_section + "## 完整上下文\n\n```text\n" + ctx.context_text + "\n```\n"

        shadow_path.write_text(sections, encoding="utf-8")

        ctx.shadow_path = str(shadow_path)
        ctx.shadow_hash = sha

        return shadow_path

    # ------------------------------------------------------------------
    # 内部：文件采集
    # ------------------------------------------------------------------

    def _collect_files(
        self,
        manifest: list[dict[str, str]],
    ) -> tuple[list[FileEntry], list[str]]:
        entries: list[FileEntry] = []
        errors: list[str] = []

        seen: set[str] = set()

        for item in manifest:
            fp = item.get("file_path", "").strip()
            if not fp:
                errors.append("MISSING_FILE_PATH: manifest 条目缺少 file_path")
                continue

            p_check = Path(fp)
            if self._require_absolute and not p_check.is_absolute():
                errors.append(f"NOT_ABSOLUTE: {fp}")
                continue

            try:
                normalized = str(p_check.resolve())
            except OSError:
                normalized = fp
            if normalized in seen:
                continue
            seen.add(normalized)

            entry = self._probe_file(fp, reason=item.get("reason", ""))
            entries.append(entry)

            if not entry.exists:
                errors.append(f"FILE_NOT_FOUND: {fp}")
            elif not entry.readable:
                errors.append(f"FILE_UNREADABLE: {fp}")

        return entries, errors

    @staticmethod
    def _probe_file(file_path: str, reason: str = "") -> FileEntry:
        p = Path(file_path)
        exists = p.exists()
        readable = exists and p.is_file()
        return FileEntry(
            file_path=file_path,
            reason=reason,
            exists=exists,
            readable=readable,
            encoding="utf-8",
        )

    # ------------------------------------------------------------------
    # 内部：上下文拼接
    # ------------------------------------------------------------------

    def _assemble(
        self,
        entries: list[FileEntry],
        errors: list[str],
        token_budget: int,
    ) -> AssembledContext:
        parts: list[str] = []
        read_count = 0

        for entry in entries:
            if not entry.readable:
                continue

            path = Path(entry.file_path)
            size = path.stat().st_size
            if size > self._max_bytes:
                errors.append(f"FILE_TOO_LARGE: {entry.file_path} ({size:,} bytes > {self._max_bytes:,} max)")
                continue

            try:
                content = path.read_text(encoding="utf-8")
            except Exception as e:
                errors.append(f"READ_ERROR: {entry.file_path} — {e}")
                continue

            read_count += 1
            est = estimate_tokens(content)
            entry.token_estimate = est

            parts.append(f"\n--- FILE: {path.name} ({entry.reason}) ---\nPATH: {entry.file_path}\n\n{content}\n")

        full_text = "\n".join(parts)
        total_chars = len(full_text)
        est_tokens = estimate_tokens(full_text)

        return AssembledContext(
            context_text=full_text,
            file_count=read_count,
            total_chars=total_chars,
            token_estimate=est_tokens,
            token_budget=token_budget,
            budget_remaining=max(token_budget - est_tokens, 0),
            entries=entries,
            errors=errors,
        )

    # ------------------------------------------------------------------
    # 内部：压缩
    # ------------------------------------------------------------------

    def _inject_rules(
        self,
        ctx: AssembledContext,
        token_budget: int,
    ) -> AssembledContext:
        matched = self._rule_registry.lookup(
            task_type="",
            tags=[],
        )
        if not matched:
            return ctx

        rule_parts: list[str] = []
        for rule in matched:
            rule_parts.append(f"[CE_RULE:{rule.rule_id} ({rule.injection_level})]\n{rule.content}")

        rule_text = "\n\n".join(rule_parts)
        separator = "\n\n--- INJECTED_RULES ---\n\n"
        ctx.context_text = ctx.context_text + separator + rule_text
        ctx.total_chars = len(ctx.context_text)
        ctx.token_estimate = estimate_tokens(ctx.context_text)
        ctx.budget_remaining = max(token_budget - ctx.token_estimate, 0)
        return ctx

    def _compress_context(
        self,
        ctx: AssembledContext,
        token_budget: int,
    ) -> AssembledContext:
        raw = ctx.context_text
        try:
            from zephyr.shared.io.doc_compressor import DocCompressor

            compressor = DocCompressor()
            outcome = compressor.compress_with_provenance(raw)
            ctx.raw_context_text = outcome.raw_text
            ctx.context_text = outcome.compressed_text
        except (ImportError, Exception) as e:
            ctx.errors.append(f"COMPRESSION_FAILED: {e}")
            ctx.was_compressed = False
            ctx.raw_context_text = ""
            return ctx

        ctx.was_compressed = True
        ctx.compressed_size_after = len(ctx.context_text)
        ctx.compressed_size_before = ctx.total_chars
        ctx.token_estimate = estimate_tokens(ctx.context_text)
        ctx.budget_remaining = max(token_budget - ctx.token_estimate, 0)

        return ctx


class RawContext(BaseModel):
    """BUILD 阶段产物——从 4 个 VMS Collection 检索的原始上下文。

    §2.1 检索参数表：
      ke_entries       ×5  — 历史经验（task_type + target_layer 语义相似）
      vibe_rules       ×3  — 合规约束（task_type 相关治理规则）
      blueprints       ×2  — 架构参考（target_layer 相关蓝图）
      failure_patterns ×3  — 避坑指南（task_type 历史失败模式）
    """

    model_config = BASE_CONFIG

    ke_entries: list[str] = Field(default_factory=list, description="知识条目——历史经验")
    vibe_rules: list[str] = Field(default_factory=list, description="Vibe 规则——合规约束")
    blueprints: list[str] = Field(default_factory=list, description="蓝图——架构参考")
    failure_patterns: list[str] = Field(default_factory=list, description="失败模式——避坑指南")

    degraded: bool = Field(default=False, description="VMS 不可用降级标记：session.degraded=true")
    embedded_defaults: list[str] = Field(
        default_factory=list,
        description="降级默认上下文 (AGENTS.md rules + 模块蓝图)",
    )

    @property
    def total_items(self) -> int:
        return len(self.ke_entries) + len(self.vibe_rules) + len(self.blueprints) + len(self.failure_patterns)

    @property
    def is_empty(self) -> bool:
        return self.total_items == 0 and not self.embedded_defaults


def build_context(
    task: TaskCard | None = None,
    *,
    task_type: str | None = None,
    target_layer: str | None = None,
    session_id: str = "",
    vms: Any | None = None,
) -> RawContext:
    """BUILD 阶段入口——从 VMS 四 Collection 检索组装原始上下文。

    AP4 防护：同 session_id + 同 query 缓存，TTL=5min。

    Parameters
    ----------
    task : TaskCard | None
    task_type : str | None
    target_layer : str | None
    session_id : str
    vms : Any | None
        VMS 客户端；None 时触发 VMS 不可用降级

    Returns
    -------
    RawContext
    """
    if task is not None:
        _task_type = task_type or _infer_task_type(task)
        _layer = target_layer or task.target_layer or ""
    else:
        _task_type = task_type or ""
        _layer = target_layer or ""

    cache_key = f"{session_id}:{_task_type}:{_layer}"
    cached = _BUILD_CACHE.get(cache_key)
    if cached is not None:
        cached_at, ctx = cached
        if (datetime.now(UTC) - cached_at).total_seconds() < 300:
            return ctx

    if vms is None:
        ctx = RawContext(degraded=True, embedded_defaults=_get_embedded_defaults(_task_type, _layer))
        _BUILD_CACHE[cache_key] = (datetime.now(UTC), ctx)
        return ctx

    ctx = RawContext()

    # 5.151.7 修复: 原 4 处 except Exception: pass 静默吞没 VMS 检索失败,
    # AI 拿到空上下文不知是真无数据还是检索失败。改为记录 warning 使失败可见
    try:
        ctx.ke_entries = _safe_search(vms, "ke_entries", _task_type, top_k=5)
    except Exception as e:
        _logger.warning("context_assembler: ke_entries search failed: %s", e)
    try:
        ctx.vibe_rules = _safe_search(vms, "vibe_rules", _task_type, top_k=3)
    except Exception as e:
        _logger.warning("context_assembler: vibe_rules search failed: %s", e)
    try:
        ctx.blueprints = _safe_search(vms, "blueprints", _layer, top_k=2)
    except Exception as e:
        _logger.warning("context_assembler: blueprints search failed: %s", e)
    try:
        ctx.failure_patterns = _safe_search(vms, "failure_patterns", _task_type, top_k=3)
    except Exception as e:
        _logger.warning("context_assembler: failure_patterns search failed: %s", e)

    if ctx.is_empty:
        ctx.degraded = True
        ctx.embedded_defaults = _get_embedded_defaults(_task_type, _layer)

    _BUILD_CACHE[cache_key] = (datetime.now(UTC), ctx)
    return ctx


def _infer_task_type(task: TaskCard) -> str:
    pipeline_type = getattr(task, "pipeline_task_type", None)
    if pipeline_type:
        return pipeline_type

    tags = getattr(task, "tags", []) or []
    for tag in tags:
        tag_lower = tag.lower()
        if tag_lower in {
            "code_gen",
            "code_review",
            "analysis",
            "ops_fix",
            "doc",
            "refactor",
            "test",
            "audit",
            "query",
            "debug",
        }:
            return tag_lower

    title = getattr(task, "title", "") or ""
    title_lower = title.lower()
    type_keywords = {
        "code_gen": ["生成", "创建", "实现", "编写", "generate", "create", "implement", "build"],
        "code_review": ["审查", "检查", "review", "inspect", "audit"],
        "analysis": ["分析", "分析报告", "analysis", "report", "评估"],
        "ops_fix": ["修复", "故障", "修复漏洞", "fix", "bug", "hotfix", "patch"],
        "doc": ["文档", "doc", "documentation", "readme"],
        "refactor": ["重构", "refactor", "restructure"],
        "test": ["测试", "test", "单元测试", "pytest"],
        "audit": ["审计", "audit", "合规", "compliance"],
        "query": ["查询", "问题", "question", "query"],
        "debug": ["调试", "debug", "排查"],
    }
    for intent, kws in type_keywords.items():
        for kw in kws:
            if kw in title_lower:
                return intent

    return "code_gen"


def _safe_search(vms: Any, collection: str, query: str, top_k: int) -> list[str]:
    if not query:
        return []
    results = vms.search(collection, query, top_k=top_k)
    if isinstance(results, list):
        return [str(r) for r in results]
    return []


_BUILD_CACHE: dict[str, tuple[datetime, RawContext]] = {}

_logger = logging.getLogger(__name__)

EMBEDDED_DEFAULTS_BASE: list[str] = [
    "R-ONLY-CREATE: Never delete files, only Write and SearchReplace",
    "R-NO-ASK: Never ask questions, work autonomously",
    "R-LOG-EVERY: Log every completed card",
    "R-STRICT-SCOPE: Only execute assigned layer, do not cross boundaries",
    "R-FIRST-READ: Always read journal and checkpoints before starting",
    "R-UTF8: Always use encoding='utf-8' for file operations",
    "R-ATOMIC: Related changes in same commit, never partial",
    "R-AUDIT: Post-task ten-dimension audit is mandatory",
]


def _get_embedded_defaults(task_type: str, layer: str) -> list[str]:
    defaults = list(EMBEDDED_DEFAULTS_BASE)
    if task_type:
        defaults.append(f"Task type: {task_type} — follow associated compliance rules")
    if layer:
        defaults.append(f"Layer: {layer} — consult blueprint §{layer} for architecture context")
    _logger.debug("VMS unavailable — using embedded defaults (%d rules)", len(defaults))
    return defaults


def _build_context_from_kb(task_type: str, layer: str) -> RawContext:
    ctx = RawContext(embedded_defaults=_get_embedded_defaults(task_type, layer))

    try:
        from zephyr.intelligence.model_evaluation.reranker import Reranker

        kb = _get_or_init_kb()
        if kb is None:
            ctx.degraded = True
            return ctx

        rk = Reranker(top_k=5)

        if task_type:
            hits = kb.search(query=task_type, k=5)
            if hits:
                docs = [h.content for h in hits]
                metas = [h.metadata for h in hits]
                ranked = rk.rerank(task_type, docs, metadatas=metas)
                ctx.ke_entries = [h.text for h in ranked[:5]]

        if layer:
            blueprint_hits = kb.search(query=f"blueprint {layer} architecture", k=3, topic=None)
            if blueprint_hits:
                ctx.blueprints = [h.content for h in blueprint_hits[:2]]
    except Exception:
        _logger.debug("KB search failed, using embedded defaults only")

    ctx.degraded = not ctx.ke_entries and not ctx.blueprints
    return ctx


_KBS_CACHE: UnifiedMemoryAPI | None = None


def _get_or_init_kb() -> UnifiedMemoryAPI | None:
    global _KBS_CACHE
    if _KBS_CACHE is not None:
        return _KBS_CACHE
    try:
        from pathlib import Path

        from zephyr.governance.kb.bootstrap import Bootstrap, BootstrapConfig
        from zephyr.intelligence.model_evaluation.unified_memory_api import InMemoryMemoryBackend, UnifiedMemoryAPI

        kb = UnifiedMemoryAPI(backend=InMemoryMemoryBackend(), enforce_capability=False)
        config = BootstrapConfig(min_ke_count=1, min_categories=1, max_chunks_per_file=10)
        engine = Bootstrap(project_root=Path.cwd(), config=config, kb_api=kb)
        result = engine.run()
        _KBS_CACHE = kb
        _logger.info(
            "KB context bridge initialized: %d KEs in %d categories",
            result.total_activated,
            len(result.categories_found),
        )
        return kb
    except Exception as exc:
        _logger.warning("KB context bridge initialization failed: %s", exc)
        return None


AUTHORITY_MIN_SCORE: float = 0.7


def validate_authority_chain(
    sources: list[str],
    *,
    min_trusted_count: int = 2,
) -> tuple[bool, float, str]:
    """TASK-018: 验证上下文来源的权威链。

    至少 min_trusted_count 个来源需来自已知权威路径。

    Returns
    -------
    tuple[bool, float, str]
        (passed, computed_score, detail_message)
    """
    trusted_prefixes = {
        "AGENTS.md",
        "root:AGENTS.md",
        "CT-",
        "blueprint:",
        "architecture-context.json",
        "contracts",
    }
    trusted_count = 0
    for source in sources:
        s = source.strip()
        if any(s.startswith(prefix) for prefix in trusted_prefixes):
            trusted_count += 1

    passed = trusted_count >= min_trusted_count
    score = min(1.0, trusted_count / max(1, len(sources)) * 1.2) if sources else 0.7
    msg = (
        f"Authority chain: {trusted_count}/{len(sources)} trusted sources "
        f"(min {min_trusted_count}) — {'PASSED' if passed else 'FAILED'}"
    )
    return passed, round(score, 2), msg
