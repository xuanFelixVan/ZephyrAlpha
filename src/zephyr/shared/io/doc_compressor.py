# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md
# [MODULE] zephyr.shared.io.doc_compressor
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.shared.security.capability
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
# [A_module] module_id=MOD-ORC_doc_compressor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
DocCompressor — 文档压缩服务（CL-018 RI 扩展模式）
===================================================
任务编号 : T-V2-006（experimental）
权限层级 : Immutable Core（CompressionPolicy 不变量字段）
           AI-Modifiable（压缩算法实现）
真源声明 : ai_autonomy_authority_registry.yaml §2.11 (CL-018)
关联决策 : rationale-log R83（CL-018 升级为 RI 扩展模式）
           config/compression_policy.yaml（CBAC allow）
创建日期 : 2026-04-27
版本     : v1.0.0

功能说明
--------
DocCompressor 是 M1 build() pipeline 注入的单例服务，向 M3 触发器提供文档压缩能力：

1. CompressionPolicy（Pydantic v2 frozen）— 5 个不变量字段
   - min_chars          : 压缩后最小字符数（≥ 100）
   - max_chars          : 压缩后最大字符数（≤ 10000）
   - preserve_structure : 保留所有 Markdown 章节标题
   - preserve_provenance: 保留 frontmatter YAML 块
   - preserve_immutable_blocks: 保留指定标记包围的代码块

2. CompressionInvariantError — 不变量违反时抛出（含违反字段 + 原值/压缩值）

3. DocCompressor.compress(text, ...) — 便捷入口，等价于 ``compress_with_provenance(...).compressed_text``。
4. ``compress_with_provenance`` — **AP4 类型保障**：一并返回 ``raw_text`` 与 ``compressed_text``，
   避免仅靠调用方手写备份。

不变量 Immutable Core 约束
--------------------------
CompressionPolicy 字段一旦加载后不可在运行时修改（frozen=True）。
调用方须通过 DocCompressor.instance(policy=new_policy) 重新实例化来更换策略，
且 new_policy 修改须经 Owner 审批（Human-Gated）。

CBAC 集成
---------
compress() 在写文件时调用 capability_check("write", target_path)，
确保目标路径在 capabilities.yaml allow 范围内。
"""

from __future__ import annotations

from typing import Final
import logging
import re
from pathlib import Path
from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）
from threading import RLock
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from zephyr.shared.security.capability import capability_check

_log = logging.getLogger(__name__)

__all__ = [
    "DEFAULT_POLICY",
    "CompressionInvariantError",
    "CompressionOutcome",
    "CompressionPolicy",
    "DocCompressor",
    "load_policy_from_yaml",
]

# ---------------------------------------------------------------------------
# 路径常量
# ---------------------------------------------------------------------------

DEFAULT_POLICY_PATH: Final[Path] = REPO_ROOT / "config" / "compression_policy.yaml"

# ---------------------------------------------------------------------------
# 不变量模型（Immutable Core）
# ---------------------------------------------------------------------------


class CompressionPolicy(BaseModel):
    """DocCompressor 不变量约束（Pydantic v2 frozen）。

    Immutable Core 说明
    -------------------
    本模型的所有字段是 experimental 最小不变量集合：
      - min_chars / max_chars        : 长度约束
      - preserve_structure           : 章节标题不可压缩
      - preserve_provenance          : frontmatter 块不可压缩
      - preserve_immutable_blocks    : 指定标记块不可压缩

    beta 扩展时须通过 Owner 审批（Human-Gated）。
    """

    model_config = ConfigDict(frozen=True)

    min_chars: int = Field(default=200, ge=100, description="压缩后最小字符数（≥ 100）")
    max_chars: int = Field(default=4000, le=10000, description="压缩后最大字符数（≤ 10000）")
    preserve_structure: bool = Field(default=True, description="保留所有 Markdown 章节标题")
    preserve_provenance: bool = Field(default=True, description="保留 frontmatter YAML 块")
    preserve_immutable_blocks: list[str] = Field(
        default_factory=lambda: [
            "<!-- IMMUTABLE_START -->",
            "<!-- AFFECTED_FILES_START -->",
            "<!-- CIRCUIT_BREAKER_START -->",
        ],
        description="须整块保留的标记字符串列表（如 '<!-- IMMUTABLE_START -->'）",
    )

    @model_validator(mode="after")
    def _validate_cross_fields(self) -> CompressionPolicy:
        if self.min_chars >= self.max_chars:
            raise ValueError(f"min_chars({self.min_chars}) must be less than max_chars({self.max_chars})")
        for marker in self.preserve_immutable_blocks:
            if not marker.strip():
                raise ValueError("preserve_immutable_blocks items must be non-empty strings")
            if "start" not in marker.lower():
                raise ValueError(
                    f"preserve_immutable_blocks marker '{marker}' must contain 'START' "
                    f"(case-insensitive) — required to derive corresponding END marker "
                    f"(e.g. '<!-- IMMUTABLE_START -->' -> '<!-- IMMUTABLE_END -->')"
                )
        return self


DEFAULT_POLICY: Final[CompressionPolicy] = CompressionPolicy()
"""默认策略（所有不变量启用，含 3 个 immutable_blocks 标记——与 policy.yaml 保持一致）。"""

# ---------------------------------------------------------------------------
# 异常
# ---------------------------------------------------------------------------


class CompressionInvariantError(Exception):
    """压缩不变量违反异常。

    参数
    ----
    field
        违反的不变量字段名（如 "preserve_structure"）。
    original
        原始值说明（如 "header '## Installation' 在原文中存在"）。
    compressed
        压缩后值说明（如 "header '## Installation' 在压缩结果中缺失"）。
    """
    error_code = "ZA-SH-0036"

    def __init__(self, field: str, original: str, compressed: str, *, error_code: str | None = None) -> None:
        self.field = field
        self.original = original
        self.compressed = compressed
        super().__init__(f"CompressionInvariantError: field='{field}'\n  原始：{original}\n  压缩：{compressed}")
        if error_code is not None:
            self.error_code = error_code


class CompressionOutcome(BaseModel):
    """压缩结果（AP4：类型层同时携带原文与压缩稿，避免静默丢原文）。"""

    model_config = ConfigDict(frozen=True)

    raw_text: str = Field(description="输入原文")
    compressed_text: str = Field(description="压缩后正文")


# ---------------------------------------------------------------------------
# YAML Policy 加载器
# ---------------------------------------------------------------------------


def load_policy_from_yaml(
    path: Path | None = None,
) -> CompressionPolicy:
    """从 config/compression_policy.yaml 加载 CompressionPolicy。

    文件不存在或解析失败时返回 DEFAULT_POLICY。

    参数
    ----
    path
        YAML 路径；默认 DEFAULT_POLICY_PATH。
    """
    resolved = path or DEFAULT_POLICY_PATH
    if not resolved.exists():
        import warnings

        warnings.warn(
            f"CompressionPolicy YAML not found: {resolved} — using DEFAULT_POLICY with hardcoded immutable blocks",
            stacklevel=2,
        )
        return DEFAULT_POLICY

    try:
        with resolved.open(encoding="utf-8") as fh:
            data: dict[str, Any] = yaml.safe_load(fh) or {}
        yaml_version = data.get("version")
        if yaml_version and str(yaml_version).split(".", 1)[0] != "1":
            import warnings

            warnings.warn(
                f"policy.yaml version={yaml_version} — loader expects v1.x, possible schema mismatch",
                stacklevel=2,
            )
        policy_dict = data.get("policy", {})
        return CompressionPolicy(**policy_dict)
    except Exception as exc:
        _log.warning("CompressionPolicy YAML parse failed: %s — using DEFAULT_POLICY (%s)", resolved, exc, exc_info=True)
        return DEFAULT_POLICY


# ---------------------------------------------------------------------------
# DocCompressor
# ---------------------------------------------------------------------------


class DocCompressor:
    """文档压缩服务单例。

    M1 build() 通过 ``DocCompressor.instance()`` 注入，
    M3 触发器通过同一接口获取实例后调用 ``compress()``。

    线程安全：单例创建使用 threading.Lock，compress() 无状态可安全并发调用。
    """

    _instance: DocCompressor | None = None
    _lock: RLock = RLock()

    def __init__(
        self,
        policy: CompressionPolicy | None = None,
        policy_path: Path | None = None,
    ) -> None:
        if policy is not None:
            self._policy = policy
        else:
            self._policy = load_policy_from_yaml(policy_path)

    # ------------------------------------------------------------------
    # 单例接口
    # ------------------------------------------------------------------

    @classmethod
    def instance(
        cls,
        policy: CompressionPolicy | None = None,
        policy_path: Path | None = None,
        *,
        reset: bool = False,
    ) -> DocCompressor:
        """返回 DocCompressor 单例。

        参数
        ----
        policy
            指定 CompressionPolicy；None 时从 YAML 加载。
        policy_path
            YAML 策略文件路径；None 时使用默认路径。
        reset
            为 True 时强制重建单例（测试场景用，生产禁止）。
        """
        with cls._lock:
            if reset or cls._instance is None:
                cls._instance = cls(policy=policy, policy_path=policy_path)
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """重置单例（仅测试使用）。"""
        with cls._lock:
            cls._instance = None

    # ------------------------------------------------------------------
    # 公共 API
    # ------------------------------------------------------------------

    @property
    def policy(self) -> CompressionPolicy:
        """返回当前激活的压缩策略（只读）。"""
        return self._policy

    def compress_with_provenance(
        self,
        text: str,
        target_path: str | None = None,
        session_id: str = "default",
    ) -> CompressionOutcome:
        """规则基压缩，**同时**返回原文与压缩正文（AP4 类型保障）。

        ``session_id`` 保留供未来与 ContextBudgetTracker / 遥测关联。
        """
        if target_path is not None:
            capability_check("write", target_path)

        policy = self._policy
        compressed = self._rule_based_compress(text, policy)
        self._check_invariants(text, compressed, policy)
        return CompressionOutcome(raw_text=text, compressed_text=compressed)

    def compress(
        self,
        text: str,
        target_path: str | None = None,
        session_id: str = "default",
    ) -> str:
        """对文本执行规则基压缩，检查不变量后返回结果。

        参数
        ----
        text
            待压缩的文档文本。
        target_path
            目标文件路径（供 CBAC 检查；写文件时传入）。
            若为 None，跳过 CBAC 检查（纯内存压缩）。
        session_id
            会话标识（供 ContextBudgetTracker 关联使用）。

        返回
        ----
        str
            压缩后文本（满足所有不变量约束）。

        异常
        ----
        CompressionInvariantError
            任一不变量被违反时抛出。
        CapabilityDenied（来自 zephyr.shared.capability）
            target_path 不在 CBAC allow 列表时抛出。
        """
        return self.compress_with_provenance(text, target_path=target_path, session_id=session_id).compressed_text

    # ------------------------------------------------------------------
    # 内部：规则基压缩（experimental 实现）
    # ------------------------------------------------------------------

    def _rule_based_compress(self, text: str, policy: CompressionPolicy) -> str:
        """experimental 规则基压缩算法（无 LLM 依赖）。

        算法流程
        --------
        1. 提取并保护 frontmatter（如 preserve_provenance=True）
        2. 提取并保护 immutable_blocks（如有）
        3. 提取并保护所有 Markdown 标题（如 preserve_structure=True）
        4. 对正文段落执行精简（去除冗余空行 + 段落截断）
        5. 重新拼接，控制长度在 [min_chars, max_chars] 区间
        6. 若结果过长则从末尾截断（保留完整行）
        """
        if not text:
            return text

        # Step 1: 提取 frontmatter
        frontmatter_block = ""
        body = text
        if policy.preserve_provenance:
            fm_match = re.match(r"^(---\n.*?\n---\n?)", text, re.DOTALL)
            if fm_match:
                frontmatter_block = fm_match.group(1)
                body = text[len(frontmatter_block) :]

        # Step 2: 提取并保护 immutable_blocks
        protected: dict[str, str] = {}
        body = self._protect_immutable_blocks(body, policy.preserve_immutable_blocks, protected)

        # Step 3: 提取并记录标题（preserve_structure 校验用）
        headers = _extract_headers(body) if policy.preserve_structure else []

        # Step 4: 正文精简
        body = self._compress_body(body)

        # Step 5: 还原 immutable_blocks
        for placeholder, original in protected.items():
            body = body.replace(placeholder, original)

        # 拼接结果
        result = frontmatter_block + body

        # Step 6: 长度控制
        result = self._enforce_length(result, policy)

        return result

    @staticmethod
    def _protect_immutable_blocks(
        text: str,
        markers: list[str],
        protected: dict[str, str],
    ) -> str:
        """将 immutable_blocks 中标记对包围的内容替换为占位符。"""
        if not markers:
            return text

        for i, marker in enumerate(markers):
            end_marker = re.sub(r"_START\b", "_END", marker, flags=re.IGNORECASE)
            if end_marker == marker:
                import warnings

                warnings.warn(
                    f"preserve_immutable_blocks marker '{marker}' does not contain '_START' — "
                    f"cannot derive END marker. This block will NOT be protected. "
                    f"Add '_START' suffix to the marker name.",
                    stacklevel=2,
                )
                continue
            pattern = re.escape(marker) + r"(.*?)" + re.escape(end_marker)

            def _replacer(m: re.Match, idx: int = i, sm: str = marker, em: str = end_marker) -> str:
                placeholder = f"__IMMUTABLE_BLOCK_{idx}__"
                protected[placeholder] = sm + m.group(1) + em
                return placeholder

            text = re.sub(pattern, _replacer, text, flags=re.DOTALL)

        return text

    @staticmethod
    def _compress_body(body: str) -> str:
        """对正文段落执行精简。

        规则：
        1. 连续 3 个以上空行压缩为 2 个空行
        2. 移除行末尾多余空白
        3. 对超过 3 行的纯正文段落，保留前 2 行 + "..."
        """
        # 规则 1: 压缩多余空行（4 个以上 -> 2 个）
        body = re.sub(r"\n{4,}", "\n\n\n", body)

        # 规则 2: 移除行末尾空白
        lines = [line.rstrip() for line in body.split("\n")]
        body = "\n".join(lines)

        # 规则 3: 压缩长段落（连续非空且非标题行超过 4 行）
        body = _compress_long_paragraphs(body, max_lines=4)

        return body

    @staticmethod
    def _enforce_length(text: str, policy: CompressionPolicy) -> str:
        """将文本长度控制在 [min_chars, max_chars] 范围内。

        - 超出 max_chars 时：截断到 max_chars 附近，追加 "…（已截断）"
        - 不足 min_chars 时：直接返回（不填充，由调用方决定是否 warn）

        换行对齐策略
        -----------
        仅在截断点后 50% ~ 100% 区间内查找最后一个换行符做对齐；
        若该区间无换行（如长段落无换行），则直接在字符边界截断，
        避免极端情况下截到文件头部的换行而丢弃大量内容。
        """
        if len(text) <= policy.max_chars:
            return text

        suffix = "\n…（已截断）"
        cutoff = max(policy.max_chars - len(suffix), 1)
        truncated = text[:cutoff]

        # 只在截断点后半段查找换行，避免极端截断到文件头部
        search_from = len(truncated) // 2
        last_nl = truncated.rfind("\n", search_from)
        if last_nl > search_from:
            truncated = truncated[:last_nl]

        return truncated + suffix

    # ------------------------------------------------------------------
    # 不变量校验
    # ------------------------------------------------------------------

    def _check_invariants(
        self,
        original: str,
        compressed: str,
        policy: CompressionPolicy,
    ) -> None:
        """检查所有 CompressionPolicy 不变量。

        不变量违反时抛出 CompressionInvariantError。
        """
        # 不变量 1：preserve_structure
        if policy.preserve_structure:
            orig_headers = _extract_headers(original)
            comp_headers = _extract_headers(compressed)
            # frontmatter 可能含 ---，排除掉非 # 格式标题
            for h in orig_headers:
                if h not in comp_headers:
                    raise CompressionInvariantError(
                        field="preserve_structure",
                        original=f"标题 '{h}' 在原文中存在",
                        compressed=f"标题 '{h}' 在压缩结果中缺失",
                    )

        # 不变量 2：preserve_provenance（frontmatter 保留校验）
        if policy.preserve_provenance:
            orig_fm = _has_frontmatter(original)
            comp_fm = _has_frontmatter(compressed)
            if orig_fm and not comp_fm:
                raise CompressionInvariantError(
                    field="preserve_provenance",
                    original="原文含 frontmatter 块",
                    compressed="压缩结果缺失 frontmatter 块",
                )

        # 不变量 3：preserve_immutable_blocks
        for marker in policy.preserve_immutable_blocks:
            if marker in original and marker not in compressed:
                raise CompressionInvariantError(
                    field="preserve_immutable_blocks",
                    original=f"标记 '{marker}' 在原文中存在",
                    compressed=f"标记 '{marker}' 在压缩结果中缺失",
                )

        # 不变量 4：min_chars（长度下界）
        if len(compressed) < policy.min_chars and len(original) >= policy.min_chars:
            raise CompressionInvariantError(
                field="min_chars",
                original=f"原文长度 {len(original)} 字符 ≥ min_chars={policy.min_chars}",
                compressed=f"压缩结果 {len(compressed)} 字符 < min_chars={policy.min_chars}",
            )


# ---------------------------------------------------------------------------
# 内部工具函数
# ---------------------------------------------------------------------------


def _extract_headers(text: str) -> list[str]:
    """从 Markdown 文本中提取所有 `#` 级标题（完整标题行）。"""
    return [line.strip() for line in text.split("\n") if re.match(r"^#{1,6}\s+\S", line)]


def _has_frontmatter(text: str) -> bool:
    """检查文本是否以 `---\n...\n---` 开头的 YAML frontmatter 块。"""
    return bool(re.match(r"^---\n", text))


def _compress_long_paragraphs(body: str, max_lines: int = 4) -> str:
    """对连续纯文本段落（非标题、非代码块、非列表）压缩长段落。

    超过 max_lines 行的段落截断为前 max_lines-1 行 + "..."。
    """
    lines = body.split("\n")
    result: list[str] = []
    para_lines: list[str] = []
    in_code_block = False

    for line in lines:
        # 检测代码块边界
        if line.startswith("```"):
            in_code_block = not in_code_block
            if para_lines:
                result.extend(_maybe_truncate_para(para_lines, max_lines))
                para_lines = []
            result.append(line)
            continue

        if in_code_block:
            result.append(line)
            continue

        # 标题、列表、空行：不纳入段落
        is_structural = (
            re.match(r"^#{1,6}\s", line)
            or re.match(r"^[-*+]\s", line)
            or re.match(r"^\d+\.\s", line)
            or re.match(r"^\|", line)
            or not line.strip()
        )

        if is_structural:
            if para_lines:
                result.extend(_maybe_truncate_para(para_lines, max_lines))
                para_lines = []
            result.append(line)
        else:
            para_lines.append(line)

    if para_lines:
        result.extend(_maybe_truncate_para(para_lines, max_lines))

    return "\n".join(result)


def _maybe_truncate_para(para_lines: list[str], max_lines: int) -> list[str]:
    """如果段落超过 max_lines 行，截断并追加 "..."。"""
    if len(para_lines) <= max_lines:
        return para_lines
    return para_lines[: max_lines - 1] + ["..."]
