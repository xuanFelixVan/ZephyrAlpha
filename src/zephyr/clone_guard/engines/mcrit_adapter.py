# [BLUEPRINT] MOD-CLONE_GUARD | docs/03_modules/_cross_layer/clone_guard/blueprint.md | §4.3
# [MODULE] zephyr.clone_guard.engines.mcrit_adapter
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.clone_guard.config (CloneGuardConfig); zephyr.clone_guard.engines.echo_guard_adapter (Finding); subprocess; json; shutil; logging; pathlib
# [CONSUMERS] zephyr.clone_guard.orchestrator
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Adapter 模式——封装 mcrit CLI 调用，统一 detect() 接口；CLI 不可用/索引未建返回空 + degraded；永不抛异常
# [MODIFY-GUARD] blueprint=docs/03_modules/_cross_layer/clone_guard/blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] detect()/search() 永不抛异常——CLI 失败/超时/索引未建返回 ([], degraded=True)
# [TESTS] tests/clone_guard/test_mcrit_adapter.py
# [A_module] module_id=MOD-CLONE_GUARD | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""McritAdapter — mcrit 索引引擎适配器（Phase C）。

封装 mcrit CLI（MinHash-based Code Relationship Intelligence Tool），
对编排层暴露统一 detect() 接口 + search() 方法（L0 按函数查重）。
mcrit 职责：MinHash 索引底座，支持大规模代码关系图查询，是 L2 审计加速器。

与 reDUP 互补——reDUP 强 T3/T4 语义克隆精检，mcrit 强 L0 快速查重（MinHash 预筛）。

降级策略（守 blueprint §5.2）：
  - mcrit 未安装 → degraded=True, 返回空列表
  - 索引未建（.mcrit/index.db 不存在）→ degraded=True, 返回空列表
  - 超时 → degraded=True, 返回空列表
  - CLI 崩溃 → degraded=True, 返回空列表
  - 正常执行 → 返回 Finding 列表
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess  # noqa: bare-subprocess  mcrit CLI 调用需要 subprocess
from pathlib import Path

from zephyr.clone_guard.config import CloneGuardConfig
from zephyr.clone_guard.engines.echo_guard_adapter import Finding

logger = logging.getLogger(__name__)

__all__ = ["McritAdapter"]


class McritAdapter:
    """mcrit 索引引擎适配器（Phase C L2 审计加速 + L0 查重）。

    封装 mcrit CLI 调用，对编排层暴露统一 detect() 接口 + search() 方法。
    引擎升级/替换不影响编排层（Adapter 模式）。
    """

    def __init__(self, repo_root: Path, config: CloneGuardConfig | None = None):
        self._repo_root = Path(repo_root)
        self._config = config or CloneGuardConfig()
        self._index_path = self._repo_root / self._config.mcrit_index_path

    def health_check(self) -> bool:
        """检查 mcrit 是否可用（CLI 存在 + 索引已建）。"""
        if shutil.which("mcrit") is None:
            return False
        return self._index_path.exists()

    def detect(self, files: list[str], timeout: int | None = None) -> tuple[list[Finding], bool]:
        """检测给定文件在 mcrit 索引中的近似函数（L2 审计场景）。

        Args:
            files: 待检测文件路径列表（相对路径）。
            timeout: 超时秒数（None 时使用 audit_timeout_sec）。

        Returns:
            (findings, degraded) 元组：degraded=True 表示 mcrit 不可用/超时/索引未建。
        """
        if not files:
            return [], False

        if not self._config.mcrit_enabled:
            logger.debug("mcrit 已在配置中禁用，跳过检测")
            return [], True

        if shutil.which("mcrit") is None:
            logger.debug("McritAdapter: mcrit CLI 未安装，跳过检测")
            return [], True

        if not self._index_path.exists():
            logger.debug("McritAdapter: 索引未建(%s)，跳过检测", self._index_path)
            return [], True

        timeout_sec = timeout or self._config.audit_timeout_sec
        cmd = self._build_query_command(files)

        try:
            result = subprocess.run(  # noqa: bare-subprocess  mcrit CLI query 调用
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_sec,
                cwd=str(self._repo_root),
                env={**os.environ, **self._config.env},
            )
        except FileNotFoundError:
            logger.warning("McritAdapter degraded: mcrit CLI 未安装")
            return [], True
        except subprocess.TimeoutExpired:
            logger.warning("McritAdapter degraded: mcrit query 超时(%ds)", timeout_sec)
            return [], True
        except Exception as e:  # noqa: BLE001  适配器不抛异常
            logger.warning("McritAdapter degraded: mcrit query 异常(%s: %s)", type(e).__name__, e)
            return [], True

        # mcrit exit codes: 0=成功（无论有无匹配）, 其他=错误
        if result.returncode != 0:
            logger.warning(
                "McritAdapter degraded: mcrit query 退出码=%d, stderr=%s",
                result.returncode,
                result.stderr[:200] if result.stderr else "",
            )
            return [], True

        try:
            data = json.loads(result.stdout) if result.stdout.strip() else {}
        except json.JSONDecodeError as e:
            logger.warning("McritAdapter degraded: JSON 解析失败(%s)", e)
            return [], True

        findings = self._parse_findings(data)
        return findings, False

    def search(self, query: str, top_k: int | None = None) -> list[Finding]:
        """L0 按函数签名/语义搜索已有函数（MCP search_functions 工具复用）。

        Args:
            query: 搜索查询（函数签名/片段）。
            top_k: 返回 top-k 结果（None 时用 config.relate_top_k）。

        Returns:
            Finding 列表（severity 均为 acknowledged，预筛结果不直接阻断）。
            mcrit 不可用时返回空列表。
        """
        if not self._config.mcrit_enabled:
            return []
        if shutil.which("mcrit") is None or not self._index_path.exists():
            logger.debug("McritAdapter.search: mcrit 不可用，返回空")
            return []

        k = top_k or self._config.relate_top_k
        cmd = [
            "mcrit", "search",
            "--index", str(self._index_path),
            "--query", query,
            "--top-k", str(k),
            "--json",
        ]
        try:
            result = subprocess.run(  # noqa: bare-subprocess
                cmd, capture_output=True, text=True,
                timeout=self._config.audit_timeout_sec, cwd=str(self._repo_root),
                env={**os.environ, **self._config.env},
            )
        except Exception as e:  # noqa: BLE001
            logger.debug("McritAdapter.search 异常(%s)", e)
            return []
        if result.returncode != 0:
            return []
        try:
            data = json.loads(result.stdout) if result.stdout.strip() else {}
        except json.JSONDecodeError:
            return []

        findings: list[Finding] = []
        for idx, item in enumerate(data.get("results", [])):
            try:
                findings.append(self._parse_search_result(item, idx))
            except (KeyError, TypeError, ValueError):
                continue
        return findings

    def _build_query_command(self, files: list[str]) -> list[str]:
        """构造 mcrit query 命令。"""
        return [
            "mcrit", "query",
            "--index", str(self._index_path),
            "--threshold", str(self._config.mcrit_query_threshold),
            "--json",
        ] + files

    def _parse_findings(self, data: dict) -> list[Finding]:
        """将 mcrit JSON 输出解析为 Finding 列表。

        mcrit 输出结构（约定）::

            {"matches": [{"function", "file", "line", "similarity",
                          "matched_function", "matched_file", "matched_line"}]}
        """
        findings: list[Finding] = []
        for idx, m in enumerate(data.get("matches", [])):
            try:
                findings.append(self._parse_match(m, idx))
            except (KeyError, TypeError, ValueError) as e:
                logger.debug("跳过无法解析的 mcrit match: %s (%s)", idx, e)
        return findings

    def _parse_match(self, m: dict, idx: int) -> Finding:
        """解析单个 mcrit match 为 Finding。"""
        similarity = float(m.get("similarity", 0.0))
        source_file = self._to_relative_path(m.get("file", ""))
        existing_file = self._to_relative_path(m.get("matched_file", ""))

        return Finding(
            finding_id=f"MC-{idx}-{source_file}-{existing_file}",
            severity=self._severity_for(similarity),
            clone_type="T2",  # MinHash 检测 token 级近似（T2 类）
            similarity=similarity,
            source_file=source_file,
            source_function=m.get("function", "unknown"),
            source_lineno=int(m.get("line", 0)),
            existing_file=existing_file,
            existing_function=m.get("matched_function", "unknown"),
            existing_lineno=int(m.get("matched_line", 0)),
            import_suggestion=None,
        )

    def _parse_search_result(self, item: dict, idx: int) -> Finding:
        """解析 search() 的单个结果为 Finding（severity=acknowledged）。"""
        similarity = float(item.get("similarity", 0.0))
        return Finding(
            finding_id=f"MC-S{idx}",
            severity="acknowledged",  # 预筛结果不阻断
            clone_type="T2",
            similarity=similarity,
            source_file="",  # 搜索场景无 source
            source_function="",
            source_lineno=0,
            existing_file=self._to_relative_path(item.get("file", "")),
            existing_function=item.get("function", "unknown"),
            existing_lineno=int(item.get("line", 0)),
            import_suggestion=item.get("import_path"),
        )

    def _severity_for(self, similarity: float) -> str:
        """按相似度映射 severity：≥0.85→extract，≥0.7→review，其余 acknowledged。"""
        if similarity >= 0.85:
            return "extract"
        if similarity >= self._config.mcrit_query_threshold:
            return "review"
        return "acknowledged"

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
