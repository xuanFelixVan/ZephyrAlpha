# [BLUEPRINT] MOD-CLONE_GUARD | docs/03_modules/_cross_layer/clone_guard/blueprint.md | §4.3
# [MODULE] zephyr.clone_guard.engines.redup_adapter
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.clone_guard.config (CloneGuardConfig); zephyr.clone_guard.engines.echo_guard_adapter (Finding); subprocess; json; shutil; logging; pathlib
# [CONSUMERS] zephyr.clone_guard.orchestrator
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Adapter 模式——封装 reDUP CLI 调用，统一 detect() 接口；CLI 不可用时返回空 + degraded；永不抛异常
# [MODIFY-GUARD] blueprint=docs/03_modules/_cross_layer/clone_guard/blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] detect() 永不抛异常——CLI 失败/超时/未安装返回 ([], degraded=True)
# [TESTS] tests/clone_guard/test_redup_adapter.py
# [A_module] module_id=MOD-CLONE_GUARD | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""RedupAdapter — reDUP 深度分析引擎适配器（Phase B 补齐）。

封装 reDUP CLI 的 scan 命令，对编排层暴露统一 detect() 接口。
reDUP 职责：六层语义克隆检测（T1/T2/T3/T4）+ 重构规划 + 影响评分 + 跨项目比较。
与 Echo-Guard 互补——Echo-Guard 主 T1/T2 AST 哈希，reDUP 强 T3/T4 语义克隆。

双模式（由 config.redup_mode 控制）：
  - "changed-only"（L1 pre-commit）：``redup scan --changed-only --output json FILES``
  - "semantic"（L2 audit）：``redup scan --semantic --output json``

降级策略（守 blueprint §5.2）：
  - reDUP 未安装 → degraded=True, 返回空列表
  - 超时 → degraded=True, 返回空列表
  - CLI 崩溃 → degraded=True, 返回空列表
  - 正常执行 → 返回 Finding 列表
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess  # noqa: bare-subprocess  reDUP CLI 调用需要 subprocess
from pathlib import Path

from zephyr.clone_guard.config import CloneGuardConfig
from zephyr.clone_guard.engines.echo_guard_adapter import Finding

logger = logging.getLogger(__name__)

__all__ = ["RedupAdapter"]

# reDUP severity → CloneGuard severity 映射
_SEVERITY_MAP: dict[str, str] = {
    "critical": "extract",   # 3+ 副本或高影响 → 硬阻断
    "high": "extract",       # saved_lines 大 → 硬阻断
    "medium": "review",      # 2 副本中等相似 → 警告
    "low": "review",         # 2 副本低相似 → 警告
    "info": "acknowledged",  # 已确认/生成代码 → 跳过
}


class RedupAdapter:
    """reDUP 深度分析引擎适配器。

    封装 reDUP CLI 调用，对编排层暴露统一 detect() 接口。
    引擎升级/替换不影响编排层（Adapter 模式）。
    """

    def __init__(self, repo_root: Path, config: CloneGuardConfig | None = None):
        self._repo_root = Path(repo_root)
        self._config = config or CloneGuardConfig()

    def health_check(self) -> bool:
        """检查 reDUP 是否可用（CLI 存在）。reDUP 无需预建索引，scan 即时分析。"""
        return shutil.which("redup") is not None

    def detect(self, files: list[str], timeout: int | None = None) -> tuple[list[Finding], bool]:
        """检测给定文件的语义克隆。

        Args:
            files: 待检测文件路径列表（相对路径）。
            timeout: 超时秒数（None 时使用配置默认值）。

        Returns:
            (findings, degraded) 元组：
            - findings: Finding 列表（检测失败时为空列表）
            - degraded: True 表示 reDUP 不可用/超时/崩溃
        """
        if not files:
            return [], False

        if not self._config.redup_enabled:
            logger.debug("reDUP 已在配置中禁用，跳过检测")
            return [], True

        # 检查 CLI 可用性
        if shutil.which("redup") is None:
            logger.debug("RedupAdapter: reDUP CLI 未安装，跳过检测")
            return [], True

        timeout_sec = timeout or self._config.pre_commit_timeout_sec
        cmd = self._build_command(files)

        try:
            result = subprocess.run(  # noqa: bare-subprocess  reDUP CLI scan 调用
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_sec,
                cwd=str(self._repo_root),
                env={**os.environ, **self._config.env},
            )
        except FileNotFoundError:
            logger.warning("RedupAdapter degraded: reDUP CLI 未安装")
            return [], True
        except subprocess.TimeoutExpired:
            logger.warning("RedupAdapter degraded: reDUP scan 超时(%ds)", timeout_sec)
            return [], True
        except Exception as e:  # noqa: BLE001  适配器不抛异常
            logger.warning("RedupAdapter degraded: reDUP scan 异常(%s: %s)", type(e).__name__, e)
            return [], True

        # reDUP exit codes: 0=无发现, 1=有发现, 其他=错误
        if result.returncode not in (0, 1):
            logger.warning(
                "RedupAdapter degraded: reDUP scan 退出码=%d, stderr=%s",
                result.returncode,
                result.stderr[:200] if result.stderr else "",
            )
            return [], True

        # 解析 JSON 输出
        try:
            data = json.loads(result.stdout) if result.stdout.strip() else {}
        except json.JSONDecodeError as e:
            logger.warning("RedupAdapter degraded: JSON 解析失败(%s)", e)
            return [], True

        findings = self._parse_findings(data)
        return findings, False

    def _build_command(self, files: list[str]) -> list[str]:
        """构造 reDUP scan 命令（依据 config.redup_mode 选择 L1/L2 模式）。"""
        cmd: list[str] = ["redup", "scan", "--output", "json"]
        if self._config.redup_mode == "semantic":
            # L2 全量语义模式
            cmd.append("--semantic")
            cmd.append("--semantic-threshold")
            cmd.append(str(self._config.redup_min_sim))
        else:
            # L1 changed-only 增量模式（默认）
            cmd.append("--changed-only")
            cmd.append("--min-sim")
            cmd.append(str(self._config.redup_min_sim))
        # 限制组数（0=不限，由 fail_on_severity 判阻断）
        if self._config.redup_max_groups > 0:
            cmd.extend(["--max-groups", str(self._config.redup_max_groups)])
        cmd.extend(files)
        return cmd

    def _parse_findings(self, data: dict) -> list[Finding]:
        """将 reDUP JSON 输出解析为 Finding 列表。

        reDUP 输出结构（约定）::

            {"duplicates": [{"id", "similarity", "clone_type", "severity",
                             "saved_lines", "refactoring_hint",
                             "occurrences": [{"file", "function", "line"}]}]}

        每个 duplicate 的 N 个 occurrences → 生成 N-1 个 Finding
        （第一个是 source，其余是 existing）。
        """
        findings: list[Finding] = []
        for dup in data.get("duplicates", []):
            try:
                findings.extend(self._parse_duplicate(dup))
            except (KeyError, TypeError, ValueError) as e:
                logger.debug("跳过无法解析的 reDUP duplicate: %s (%s)", dup.get("id", "?"), e)
        return findings

    def _parse_duplicate(self, dup: dict) -> list[Finding]:
        """解析单个 duplicate 组为 N-1 个 Finding。"""
        occurrences = dup.get("occurrences", [])
        if len(occurrences) < 2:
            return []

        dup_id = dup.get("id", "")
        similarity = float(dup.get("similarity", 0.0))
        clone_type = dup.get("clone_type", "T?")
        refactoring_hint = dup.get("refactoring_hint")

        # severity 映射：优先用 reDUP 的 severity 字段，fallback 按 similarity + 副本数
        redup_severity = dup.get("severity")
        if redup_severity and redup_severity in _SEVERITY_MAP:
            severity = _SEVERITY_MAP[redup_severity]
        else:
            severity = self._infer_severity(similarity, len(occurrences))

        # 第一个 occurrence 是 source，其余是 existing
        source = occurrences[0]
        source_file = self._to_relative_path(source.get("file", ""))
        source_function = source.get("function", "unknown")
        source_lineno = int(source.get("line", 0))

        findings: list[Finding] = []
        for idx, existing in enumerate(occurrences[1:], start=1):
            existing_file = self._to_relative_path(existing.get("file", ""))
            existing_function = existing.get("function", "unknown")
            existing_lineno = int(existing.get("line", 0))

            finding_id = (
                f"RD-{dup_id}-{idx}" if dup_id else f"RD-{source_file}-{existing_file}-{idx}"
            )

            findings.append(
                Finding(
                    finding_id=finding_id,
                    severity=severity,
                    clone_type=clone_type,
                    similarity=similarity,
                    source_file=source_file,
                    source_function=source_function,
                    source_lineno=source_lineno,
                    existing_file=existing_file,
                    existing_function=existing_function,
                    existing_lineno=existing_lineno,
                    import_suggestion=refactoring_hint,
                )
            )
        return findings

    @staticmethod
    def _infer_severity(similarity: float, occurrence_count: int) -> str:
        """reDUP 未输出 severity 字段时的 fallback 推断。"""
        if occurrence_count >= 3 or similarity >= 0.95:
            return "extract"  # 3+ 副本或极高相似 → 硬阻断
        return "review"  # 2 副本 → 警告

    def _to_relative_path(self, file_path: str) -> str:
        """将绝对路径转为相对仓库根目录的路径（归一化斜杠）。"""
        try:
            p = Path(file_path)
            if p.is_absolute():
                rel = p.relative_to(self._repo_root)
                return str(rel).replace("\\", "/")
            return file_path.replace("\\", "/")
        except ValueError:
            return file_path.replace("\\", "/")
