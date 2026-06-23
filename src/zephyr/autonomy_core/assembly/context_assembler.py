# [BLUEPRINT] MOD-INF-008 | docs/03_modules/_cross_layer/context-engine/blueprint.md
# [MODULE] zephyr.autonomy_core.assembly.context_assembler
# [DOMAIN] D-AUTONOMY_CORE
# [DEPENDENCIES] zephyr.integration.shared.schema.schemas; zephyr.autonomy_core.__init__
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
from typing import Self

"""
ContextAssembler — 上下文装配、校验、影子留档
=============================================
依据：MOD-INF-006 G3 门禁（上下文装配完整度）+ §3.1 接口契约

四阶段流水线：
  1. collect   — 读取 context_assembly_manifest 中所有文件
  2. assemble  — 拼接为单一上下文字符串
  3. compress  — 超 token 预算时调用 DocCompressor
  4. shadow    — 生成影子副本供脚本系统 B 线复查
"""

import hashlib
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel, Field

from zephyr.autonomy_core.token_budget import DEFAULT_CONTEXT_TOKEN_BUDGET, estimate_tokens
from zephyr.integration.shared.schema.schemas import BASE_CONFIG

__all__ = [
    "AssembledContext",
    "AssemblyError",
    "ContextAssembler",
    "FileEntry",
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
    ) -> None:
        self._max_bytes = max_file_size_mb * 1024 * 1024
        self._require_absolute = require_absolute_paths

    # ------------------------------------------------------------------
    # 公共 API
    # ------------------------------------------------------------------

    def assemble(
        self,
        manifest: list[dict[str, str]],
        token_budget: int = DEFAULT_CONTEXT_TOKEN_BUDGET,
        *,
        compress: bool = True,
    ) -> Self:
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
    def _probe_file(file_path: str, reason: str = "") -> Self:
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
    ) -> Self:
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

    def _compress_context(
        self,
        ctx: AssembledContext,
        token_budget: int,
    ) -> Self:
        raw = ctx.context_text
        try:
            from zephyr.autonomy_core.support.doc_compressor import DocCompressor

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
