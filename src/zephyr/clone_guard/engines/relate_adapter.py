# [BLUEPRINT] MOD-CLONE_GUARD | docs/03_modules/_cross_layer/clone_guard/blueprint.md | §4.3
# [MODULE] zephyr.clone_guard.engines.relate_adapter
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.clone_guard.config (CloneGuardConfig); zephyr.clone_guard.engines.echo_guard_adapter (Finding); subprocess; json; shutil; logging; pathlib
# [CONSUMERS] zephyr.clone_guard.orchestrator
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Adapter 模式——封装 relate CLI 调用，统一 detect() 接口；CLI 不可用/索引未建返回空 + degraded；severity 仅 review/acknowledged（预筛器不直接 extract）；永不抛异常
# [MODIFY-GUARD] blueprint=docs/03_modules/_cross_layer/clone_guard/blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] detect()/search() 永不抛异常——CLI 失败/超时/索引未建返回 ([], degraded=True)
# [TESTS] tests/clone_guard/test_relate_adapter.py
# [A_module] module_id=MOD-CLONE_GUARD | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""RelateAdapter — relate 快速预筛适配器（Phase C L2/L3 加速器）。

封装 relate CLI（无模型压缩相似度），对编排层暴露统一 detect() 接口 +
search() 方法（L0 按语义搜已有函数）。relate 职责：无模型压缩相似度快速
预筛，加速重引擎（reDUP/mcrit）检测——先粗筛候选集，再精检。

与 reDUP/mcrit 互补——relate 是预筛器（轻量、无模型），reDUP/mcrit 是精检器。
relate 不直接判 extract（预筛结果保守，仅 review/acknowledged），由精检器
决定是否升级到 extract。

降级策略（守 blueprint §5.2）：
  - relate 未安装 → degraded=True, 返回空列表
  - 索引未建（.relate/index 不存在）→ degraded=True, 返回空列表
  - 超时 → degraded=True, 返回空列表
  - CLI 崩溃 → degraded=True, 返回空列表
  - 正常执行 → 返回 Finding 列表（severity 仅 review/acknowledged）
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess  # noqa: bare-subprocess  relate CLI 调用需要 subprocess
from pathlib import Path

from zephyr.clone_guard.config import CloneGuardConfig
from zephyr.clone_guard.engines.echo_guard_adapter import Finding

logger = logging.getLogger(__name__)

__all__ = ["RelateAdapter"]


class RelateAdapter:
    """relate 快速预筛适配器（Phase C L2/L3 加速器）。

    封装 relate CLI 调用，对编排层暴露统一 detect() 接口 + search() 方法。
    severity 仅 review/acknowledged（预筛器不直接 extract）。
    """

    def __init__(self, repo_root: Path, config: CloneGuardConfig | None = None):
        self._repo_root = Path(repo_root)
        self._config = config or CloneGuardConfig()
        self._index_path = self._repo_root / self._config.relate_index_path

    def health_check(self) -> bool:
        """检查 relate 是否可用（CLI 存在 + 索引已建）。"""
        if shutil.which("relate") is None:
            return False
        return self._index_path.exists()

    def detect(self, files: list[str], timeout: int | None = None) -> tuple[list[Finding], bool]:
        """检测给定文件的快速预筛候选（L2/L3 加速场景）。

        Args:
            files: 待检测文件路径列表（相对路径）。
            timeout: 超时秒数（None 时使用 audit_timeout_sec）。

        Returns:
            (findings, degraded) 元组：degraded=True 表示不可用/超时/索引未建。
        """
        if not files:
            return [], False

        if not self._config.relate_enabled:
            logger.debug("relate 已在配置中禁用，跳过检测")
            return [], True

        if shutil.which("relate") is None:
            logger.debug("RelateAdapter: relate CLI 未安装，跳过检测")
            return [], True

        if not self._index_path.exists():
            logger.debug("RelateAdapter: 索引未建(%s)，跳过检测", self._index_path)
            return [], True

        timeout_sec = timeout or self._config.audit_timeout_sec
        cmd = self._build_detect_command(files)

        try:
            result = subprocess.run(  # noqa: bare-subprocess  relate CLI detect 调用
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_sec,
                cwd=str(self._repo_root),
                env={**os.environ, **self._config.env},
            )
        except FileNotFoundError:
            logger.warning("RelateAdapter degraded: relate CLI 未安装")
            return [], True
        except subprocess.TimeoutExpired:
            logger.warning("RelateAdapter degraded: relate detect 超时(%ds)", timeout_sec)
            return [], True
        except Exception as e:  # noqa: BLE001  适配器不抛异常
            logger.warning("RelateAdapter degraded: relate detect 异常(%s: %s)", type(e).__name__, e)
            return [], True

        if result.returncode not in (0, 1):
            logger.warning(
                "RelateAdapter degraded: relate detect 退出码=%d, stderr=%s",
                result.returncode,
                result.stderr[:200] if result.stderr else "",
            )
            return [], True

        try:
            data = json.loads(result.stdout) if result.stdout.strip() else {}
        except json.JSONDecodeError as e:
            logger.warning("RelateAdapter degraded: JSON 解析失败(%s)", e)
            return [], True

        findings = self._parse_findings(data)
        return findings, False

    def search(self, query: str, top_k: int | None = None) -> list[Finding]:
        """L0 按语义搜已有函数（MCP search_functions 工具复用）。

        Args:
            query: 搜索查询（函数签名/片段）。
            top_k: 返回 top-k 结果（None 时用 config.relate_top_k）。

        Returns:
            Finding 列表（severity 均为 acknowledged，预筛结果不阻断）。
        """
        if not self._config.relate_enabled:
            return []
        if shutil.which("relate") is None or not self._index_path.exists():
            logger.debug("RelateAdapter.search: relate 不可用，返回空")
            return []

        k = top_k or self._config.relate_top_k
        cmd = [
            "relate", "search",
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
            logger.debug("RelateAdapter.search 异常(%s)", e)
            return []
        if result.returncode != 0:
            return []
        try:
            data = json.loads(result.stdout) if result.stdout.strip() else {}
        except json.JSONDecodeError:
            return []

        findings: list[Finding] = []
        for idx, item in enumerate(data.get("candidates", [])):
            try:
                findings.append(self._parse_candidate(item, idx))
            except (KeyError, TypeError, ValueError):
                continue
        return findings

    def _build_detect_command(self, files: list[str]) -> list[str]:
        """构造 relate detect 命令。"""
        return [
            "relate", "detect",
            "--index", str(self._index_path),
            "--json",
        ] + files

    def _parse_findings(self, data: dict) -> list[Finding]:
        """将 relate JSON 输出解析为 Finding 列表。

        relate 输出结构（约定）::

            {"candidates": [{"file", "function", "line",
                             "matched_file", "matched_function", "matched_line",
                             "similarity"}]}
        """
        findings: list[Finding] = []
        for idx, c in enumerate(data.get("candidates", [])):
            try:
                findings.append(self._parse_candidate(c, idx))
            except (KeyError, TypeError, ValueError) as e:
                logger.debug("跳过无法解析的 relate candidate: %s (%s)", idx, e)
        return findings

    def _parse_candidate(self, c: dict, idx: int) -> Finding:
        """解析单个 relate candidate 为 Finding（severity 仅 review/acknowledged）。"""
        similarity = float(c.get("similarity", 0.0))
        source_file = self._to_relative_path(c.get("file", ""))
        existing_file = self._to_relative_path(c.get("matched_file", ""))

        # 预筛器保守：≥0.7→review，其余 acknowledged（永不 extract）
        severity = "review" if similarity >= 0.7 else "acknowledged"

        return Finding(
            finding_id=f"RL-{idx}-{source_file}-{existing_file}",
            severity=severity,
            clone_type="T2",  # 压缩相似度 token 级（T2 类）
            similarity=similarity,
            source_file=source_file,
            source_function=c.get("function", "unknown"),
            source_lineno=int(c.get("line", 0)),
            existing_file=existing_file,
            existing_function=c.get("matched_function", "unknown"),
            existing_lineno=int(c.get("matched_line", 0)),
            import_suggestion=c.get("import_path"),
        )

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
