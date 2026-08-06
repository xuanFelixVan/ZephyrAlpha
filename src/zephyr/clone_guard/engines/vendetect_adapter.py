# [BLUEPRINT] MOD-CLONE_GUARD | docs/03_modules/_cross_layer/clone_guard/blueprint.md | §4.3
# [MODULE] zephyr.clone_guard.engines.vendetect_adapter
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.clone_guard.config (CloneGuardConfig); zephyr.clone_guard.engines.echo_guard_adapter (Finding); subprocess; json; shutil; logging; pathlib
# [CONSUMERS] zephyr.clone_guard.orchestrator
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Adapter 模式——封装 Vendetect CLI 调用，统一 detect() 接口；CLI 不可用/未配 remote 降级；AGPL 许可证隔离（仅 subprocess，不链接进 src/）；永不抛异常
# [MODIFY-GUARD] blueprint=docs/03_modules/_cross_layer/clone_guard/blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] detect() 永不抛异常——CLI 失败/超时/未配 remote_url 返回 ([], degraded=True)
# [TESTS] tests/clone_guard/test_vendetect_adapter.py
# [A_module] module_id=MOD-CLONE_GUARD | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""VendetectAdapter — Vendetect 跨仓库合规审计适配器（Phase C L3）。

封装 Vendetect CLI 的 compare 命令，对编排层暴露统一 detect() 接口。
Vendetect 职责：检测跨仓库 vendored 代码，识别许可证合规风险（如 AGPL 代码
混入项目）。AGPL-3.0 许可证——本适配器仅 subprocess 调 CLI，不 import/链接
Vendetect 源码进 src/，守许可证隔离铁律。

降级策略（守 blueprint §5.2）：
  - Vendetect 未安装 → degraded=True, 返回空列表
  - 未配 remote_url → degraded=True, 返回空列表
  - 超时 → degraded=True, 返回空列表
  - CLI 崩溃 → degraded=True, 返回空列表
  - 正常执行 → 返回 Finding 列表

severity 策略（合规硬阻断）：
  - AGPL/未知许可证 + similarity≥0.95 → extract（合规硬阻断）
  - 高相似但许可证兼容 → review（警告，建议 attribution）
  - 低相似 → acknowledged
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess  # noqa: bare-subprocess  Vendetect CLI 调用需要 subprocess
from pathlib import Path

from zephyr.clone_guard.config import CloneGuardConfig
from zephyr.clone_guard.engines.echo_guard_adapter import Finding

logger = logging.getLogger(__name__)

__all__ = ["VendetectAdapter"]

# 合规风险许可证——出现即硬阻断（extract）
_HIGH_RISK_LICENSES: frozenset[str] = frozenset({
    "AGPL-3.0", "AGPL-3.0-only", "AGPL-3.0-or-later",
    "GPL-3.0", "GPL-3.0-only", "GPL-3.0-or-later",
    "Unknown", "unknown", "",
})


class VendetectAdapter:
    """Vendetect 跨仓库合规审计适配器（Phase C L3）。

    封装 Vendetect CLI 调用，对编排层暴露统一 detect() 接口。
    AGPL 许可证隔离：仅 subprocess 调 CLI，不链接进 src/。
    """

    def __init__(self, repo_root: Path, config: CloneGuardConfig | None = None):
        self._repo_root = Path(repo_root)
        self._config = config or CloneGuardConfig()

    def health_check(self) -> bool:
        """检查 Vendetect 是否可用（CLI 存在 + 已配 remote_url）。"""
        if shutil.which("vendetect") is None:
            return False
        return bool(self._config.vendetect_remote_url)

    def detect(self, files: list[str], timeout: int | None = None) -> tuple[list[Finding], bool]:
        """检测给定文件在远程仓库中的 vendored 代码（L3 跨边界审计）。

        Args:
            files: 待检测文件路径列表（相对路径）。
            timeout: 超时秒数（None 时使用 compare_timeout_sec）。

        Returns:
            (findings, degraded) 元组：degraded=True 表示不可用/超时/未配 remote。
        """
        if not files:
            return [], False

        if not self._config.vendetect_enabled:
            logger.debug("Vendetect 已在配置中禁用，跳过检测")
            return [], True

        if shutil.which("vendetect") is None:
            logger.debug("VendetectAdapter: Vendetect CLI 未安装，跳过检测")
            return [], True

        remote_url = self._config.vendetect_remote_url
        if not remote_url:
            logger.debug("VendetectAdapter: 未配 vendetect_remote_url，跳过检测")
            return [], True

        timeout_sec = timeout or self._config.compare_timeout_sec
        cmd = self._build_command(files, remote_url)

        try:
            result = subprocess.run(  # noqa: bare-subprocess  Vendetect CLI compare 调用
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_sec,
                cwd=str(self._repo_root),
                env={**os.environ, **self._config.env},
            )
        except FileNotFoundError:
            logger.warning("VendetectAdapter degraded: Vendetect CLI 未安装")
            return [], True
        except subprocess.TimeoutExpired:
            logger.warning("VendetectAdapter degraded: Vendetect compare 超时(%ds)", timeout_sec)
            return [], True
        except Exception as e:  # noqa: BLE001  适配器不抛异常
            logger.warning("VendetectAdapter degraded: Vendetect compare 异常(%s: %s)", type(e).__name__, e)
            return [], True

        if result.returncode not in (0, 1):
            logger.warning(
                "VendetectAdapter degraded: Vendetect compare 退出码=%d, stderr=%s",
                result.returncode,
                result.stderr[:200] if result.stderr else "",
            )
            return [], True

        try:
            data = json.loads(result.stdout) if result.stdout.strip() else {}
        except json.JSONDecodeError as e:
            logger.warning("VendetectAdapter degraded: JSON 解析失败(%s)", e)
            return [], True

        findings = self._parse_findings(data)
        return findings, False

    def _build_command(self, files: list[str], remote_url: str) -> list[str]:
        """构造 Vendetect compare 命令。"""
        return [
            "vendetect", "compare",
            "--local", str(self._repo_root),
            "--remote", remote_url,
            "--json",
        ] + files

    def _parse_findings(self, data: dict) -> list[Finding]:
        """将 Vendetect JSON 输出解析为 Finding 列表。

        Vendetect 输出结构（约定）::

            {"vendored": [{"local_file", "local_function", "local_line",
                           "remote_file", "remote_function", "remote_line",
                           "similarity", "license", "remote_url"}]}
        """
        findings: list[Finding] = []
        for idx, v in enumerate(data.get("vendored", [])):
            try:
                findings.append(self._parse_vendored(v, idx))
            except (KeyError, TypeError, ValueError) as e:
                logger.debug("跳过无法解析的 Vendetect vendored: %s (%s)", idx, e)
        return findings

    def _parse_vendored(self, v: dict, idx: int) -> Finding:
        """解析单个 vendored match 为 Finding（合规 severity 判定）。"""
        similarity = float(v.get("similarity", 0.0))
        license_ = str(v.get("license", "")).strip()
        source_file = self._to_relative_path(v.get("local_file", ""))
        existing_file = v.get("remote_file", "")  # 远程文件路径保持原样（跨仓库）

        severity = self._severity_for(license_, similarity)
        clone_type = "vendored"  # 跨仓库 vendored 代码

        return Finding(
            finding_id=f"VD-{idx}-{source_file}-{existing_file}",
            severity=severity,
            clone_type=clone_type,
            similarity=similarity,
            source_file=source_file,
            source_function=v.get("local_function", "unknown"),
            source_lineno=int(v.get("local_line", 0)),
            existing_file=existing_file,
            existing_function=v.get("remote_function", "unknown"),
            existing_lineno=int(v.get("remote_line", 0)),
            import_suggestion=v.get("remote_url"),  # 远程 URL 作为溯源建议
        )

    @staticmethod
    def _severity_for(license_: str, similarity: float) -> str:
        """合规 severity 判定。

        - AGPL/GPL/未知许可证 + similarity≥0.95 → extract（合规硬阻断）
        - 兼容许可证 + similarity≥0.95 → review（建议 attribution）
        - similarity≥0.7 → review
        - 其余 → acknowledged
        """
        license_risky = license_ in _HIGH_RISK_LICENSES
        if license_risky and similarity >= 0.95:
            return "extract"  # 合规硬阻断
        if similarity >= 0.95:
            return "review"  # 兼容许可但需 attribution
        if similarity >= 0.7:
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
