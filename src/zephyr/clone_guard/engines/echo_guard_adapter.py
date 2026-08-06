# [BLUEPRINT] MOD-CLONE_GUARD | docs/03_modules/_cross_layer/clone_guard/blueprint.md | §4.3
# [MODULE] zephyr.clone_guard.engines.echo_guard_adapter
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.clone_guard.config (CloneGuardConfig); subprocess; json; logging
# [CONSUMERS] zephyr.clone_guard.orchestrator
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Adapter 模式——封装 echo-guard CLI 调用，对编排层暴露统一 detect() 接口；echo-guard 不可用时返回空列表 + degraded 标记；永不抛异常
# [MODIFY-GUARD] blueprint=docs/03_modules/_cross_layer/clone_guard/blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] detect() 永不抛异常——CLI 失败/超时/索引缺失返回 ([], degraded=True)
# [TESTS] tests/clone_guard/test_echo_guard_adapter.py
# [A_module] module_id=MOD-CLONE_GUARD | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""EchoGuardAdapter — Echo-Guard 引擎适配器（Phase A MVP）。

封装 echo-guard CLI 的 check 命令，对编排层暴露统一 detect() 接口。
通过 `echo-guard check --output json FILES...` 调用，解析 JSON 输出为 Finding 列表。

降级策略（守 blueprint §5.2）：
  - echo-guard 未安装 → degraded=True, 返回空列表
  - 索引不存在 → degraded=True, 返回空列表
  - 超时 → degraded=True, 返回空列表
  - CLI 崩溃 → degraded=True, 返回空列表
  - 正常执行 → 返回 Finding 列表
"""

from __future__ import annotations

import json
import logging
import os
import subprocess  # noqa: bare-subprocess  echo-guard CLI 调用需要 subprocess
from dataclasses import dataclass
from pathlib import Path

from zephyr.clone_guard.config import CloneGuardConfig

logger = logging.getLogger(__name__)

__all__ = ["EchoGuardAdapter", "Finding"]


@dataclass(frozen=True)
class Finding:
    """统一的克隆检测结果（跨引擎统一格式）。

    Phase A 简化版——仅包含 Echo-Guard 返回的核心字段。
    Phase B 起由 aggregator.py 合并多引擎结果后补充 engines/saved_lines 等字段。
    """

    finding_id: str
    severity: str  # extract / review
    clone_type: str  # T1 / T2 / T3 / T4
    similarity: float
    source_file: str
    source_function: str
    source_lineno: int
    existing_file: str
    existing_function: str
    existing_lineno: int
    import_suggestion: str | None = None


class EchoGuardAdapter:
    """Echo-Guard 引擎适配器。

    封装 echo-guard CLI 调用，对编排层暴露统一 detect() 接口。
    引擎升级/替换不影响编排层（Adapter 模式）。
    """

    def __init__(self, repo_root: Path, config: CloneGuardConfig | None = None):
        self._repo_root = repo_root
        self._config = config or CloneGuardConfig()

    def health_check(self) -> bool:
        """检查 echo-guard 是否可用（CLI 存在 + 索引已建）。"""
        index_path = self._repo_root / ".echo-guard" / "index.duckdb"
        if not index_path.exists():
            return False
        try:
            result = subprocess.run(  # noqa: bare-subprocess  echo-guard CLI 健康检查
                ["echo-guard", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=str(self._repo_root),
                env={**os.environ, **self._config.env},
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def detect(self, files: list[str], timeout: int | None = None) -> tuple[list[Finding], bool]:
        """检测给定文件的克隆。

        Args:
            files: 待检测文件路径列表（相对路径）。
            timeout: 超时秒数（None 时使用配置默认值）。

        Returns:
            (findings, degraded) 元组：
            - findings: Finding 列表（检测失败时为空列表）
            - degraded: True 表示 echo-guard 不可用/超时/崩溃
        """
        if not files:
            return [], False

        if not self._config.echo_guard_enabled:
            logger.debug("echo-guard 已在配置中禁用，跳过检测")
            return [], True

        timeout_sec = timeout or self._config.pre_commit_timeout_sec

        try:
            result = subprocess.run(  # noqa: bare-subprocess  echo-guard CLI check 调用
                ["echo-guard", "check", "--output", "json"] + files,
                capture_output=True,
                text=True,
                timeout=timeout_sec,
                cwd=str(self._repo_root),
                env={**os.environ, **self._config.env},
            )
        except FileNotFoundError:
            logger.warning("EchoGuardAdapter degraded: echo-guard CLI 未安装")
            return [], True
        except subprocess.TimeoutExpired:
            logger.warning("EchoGuardAdapter degraded: echo-guard check 超时(%ds)", timeout_sec)
            return [], True
        except Exception as e:  # noqa: BLE001  适配器不抛异常
            logger.warning("EchoGuardAdapter degraded: echo-guard check 异常(%s: %s)", type(e).__name__, e)
            return [], True

        # echo-guard exit codes: 0=无阻断发现, 1=有阻断发现, 2=无索引
        if result.returncode == 2:
            logger.warning("EchoGuardAdapter degraded: echo-guard 索引不存在，运行 `echo-guard index` 构建")
            return [], True

        if result.returncode not in (0, 1):
            logger.warning(
                "EchoGuardAdapter degraded: echo-guard check 退出码=%d, stderr=%s",
                result.returncode,
                result.stderr[:200] if result.stderr else "",
            )
            return [], True

        # 解析 JSON 输出
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            logger.warning("EchoGuardAdapter degraded: JSON 解析失败(%s)", e)
            return [], True

        findings = self._parse_findings(data)
        return findings, False

    def _parse_findings(self, data: dict) -> list[Finding]:
        """将 echo-guard JSON 输出解析为 Finding 列表。"""
        findings: list[Finding] = []
        for item in data.get("findings", []):
            try:
                if item.get("type") == "match":
                    findings.append(self._parse_match(item))
                elif item.get("type") == "group":
                    findings.extend(self._parse_group(item))
            except (KeyError, TypeError) as e:
                logger.debug("跳过无法解析的 finding: %s (%s)", item.get("finding_id", "?"), e)
        return findings

    def _parse_match(self, item: dict) -> Finding:
        """解析 type=match 的 finding。"""
        source = item["source"]
        existing = item["existing"]
        return Finding(
            finding_id=item["finding_id"],
            severity=item["severity"],
            clone_type=item.get("clone_type", "T?"),
            similarity=float(item.get("similarity_score", 0.0)),
            source_file=source["filepath"],
            source_function=source["name"],
            source_lineno=int(source.get("lineno", 0)),
            existing_file=existing["filepath"],
            existing_function=existing["name"],
            existing_lineno=int(existing.get("lineno", 0)),
            import_suggestion=existing.get("import_suggestion"),
        )

    def _parse_group(self, item: dict) -> list[Finding]:
        """解析 type=group 的 finding（多副本组）。"""
        findings: list[Finding] = []
        functions = item.get("functions", [])
        if len(functions) < 2:
            return findings
        # group 的第一个函数是 source，其余是 existing
        source = functions[0]
        for existing in functions[1:]:
            findings.append(
                Finding(
                    finding_id=item.get("finding_id", ""),
                    severity=item["severity"],
                    clone_type=item.get("clone_type", "T?"),
                    similarity=float(item.get("similarity_score", 0.0)),
                    source_file=source["filepath"],
                    source_function=source["name"],
                    source_lineno=int(source.get("lineno", 0)),
                    existing_file=existing["filepath"],
                    existing_function=existing["name"],
                    existing_lineno=int(existing.get("lineno", 0)),
                    import_suggestion=None,
                )
            )
        return findings
