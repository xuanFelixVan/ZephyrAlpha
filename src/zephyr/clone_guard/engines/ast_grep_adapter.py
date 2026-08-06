# [BLUEPRINT] MOD-CLONE_GUARD | docs/03_modules/_cross_layer/clone_guard/blueprint.md | §4.3
# [MODULE] zephyr.clone_guard.engines.ast_grep_adapter
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.clone_guard.config (CloneGuardConfig); subprocess; json; logging; pathlib
# [CONSUMERS] zephyr.clone_guard.orchestrator
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Adapter 模式——封装 ast-grep CLI 调用，统一 detect() 接口；CLI 不可用时返回空 + degraded；永不抛异常
# [MODIFY-GUARD] blueprint=docs/03_modules/_cross_layer/clone_guard/blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] detect() 永不抛异常——CLI 失败/超时/规则解析失败返回 ([], degraded=True)
# [TESTS] tests/clone_guard/test_ast_grep_adapter.py
# [A_module] module_id=MOD-CLONE_GUARD | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""AstGrepAdapter — ast-grep 规则引擎适配器（Phase B）。

封装 ast-grep CLI 的 scan 命令，对编排层暴露统一 detect() 接口。
通过 `ast-grep scan --rule <rule.yml> --json=compact --include-metadata FILES` 调用，
解析 JSON 输出为 Finding 列表。

ast-grep 职责：YAML 自定义结构化模式匹配（业务规则，如"禁止 bare except"）。
与 Echo-Guard 互补——Echo-Guard 检测代码克隆，ast-grep 检测结构反模式。

降级策略（守 blueprint §5.2）：
  - ast-grep 未安装 → degraded=True, 返回空列表
  - 规则文件不存在 → degraded=True, 返回空列表
  - 超时 → degraded=True, 返回空列表
  - CLI 崩溃 → degraded=True, 返回空列表
  - 正常执行 → 返回 Finding 列表
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess  # noqa: bare-subprocess  ast-grep CLI 调用需要 subprocess
from pathlib import Path

from zephyr.clone_guard.config import CloneGuardConfig
from zephyr.clone_guard.engines.echo_guard_adapter import Finding

logger = logging.getLogger(__name__)

__all__ = ["AstGrepAdapter"]

# ast-grep severity → CloneGuard severity 映射
_SEVERITY_MAP: dict[str, str] = {
    "error": "extract",    # ast-grep error → extract 级（硬阻断）
    "warning": "review",   # ast-grep warning → review 级（警告）
    "info": "acknowledged",  # ast-grep info → acknowledged（跳过）
}

# 默认规则目录（相对仓库根目录）
_DEFAULT_RULES_DIR = "clone_guard/rules"


class AstGrepAdapter:
    """ast-grep 规则引擎适配器。

    封装 ast-grep CLI 调用，对编排层暴露统一 detect() 接口。
    引擎升级/替换不影响编排层（Adapter 模式）。
    """

    def __init__(self, repo_root: Path, config: CloneGuardConfig | None = None):
        self._repo_root = Path(repo_root)
        self._config = config or CloneGuardConfig()
        self._rules_dir = self._repo_root / _DEFAULT_RULES_DIR

    def health_check(self) -> bool:
        """检查 ast-grep 是否可用（CLI 存在 + 规则目录有 .yml 文件）。"""
        ast_grep = shutil.which("ast-grep")
        if ast_grep is None:
            return False

        if not self._rules_dir.exists():
            return False

        rule_files = list(self._rules_dir.glob("*.yml"))
        return len(rule_files) > 0

    def detect(self, files: list[str], timeout: int | None = None) -> tuple[list[Finding], bool]:
        """检测给定文件的结构反模式。

        遍历规则目录下所有 .yml 规则文件，对每个规则运行 ast-grep scan。

        Args:
            files: 待检测文件路径列表（相对路径）。
            timeout: 超时秒数（None 时使用配置默认值）。

        Returns:
            (findings, degraded) 元组：
            - findings: Finding 列表（检测失败时为空列表）
            - degraded: True 表示 ast-grep 不可用/超时/崩溃
        """
        if not files:
            return [], False

        # 检查 CLI 可用性
        ast_grep = shutil.which("ast-grep")
        if ast_grep is None:
            logger.debug("AstGrepAdapter: ast-grep CLI 未安装，跳过检测")
            return [], True

        # 检查规则目录
        if not self._rules_dir.exists():
            logger.debug("AstGrepAdapter: 规则目录不存在(%s)，跳过检测", self._rules_dir)
            return [], True

        rule_files = sorted(self._rules_dir.glob("*.yml"))
        if not rule_files:
            logger.debug("AstGrepAdapter: 规则目录无 .yml 文件，跳过检测")
            return [], True

        timeout_sec = timeout or self._config.pre_commit_timeout_sec
        all_findings: list[Finding] = []
        any_degraded = False

        for rule_file in rule_files:
            findings, degraded = self._run_single_rule(rule_file, files, timeout_sec)
            all_findings.extend(findings)
            if degraded:
                any_degraded = True

        return all_findings, any_degraded

    def _run_single_rule(
        self, rule_file: Path, files: list[str], timeout_sec: int
    ) -> tuple[list[Finding], bool]:
        """对单个规则文件运行 ast-grep scan。"""
        try:
            # Windows 上 ast-grep 是 .cmd 文件，需要 shell=True
            result = subprocess.run(  # noqa: bare-subprocess  ast-grep CLI scan 调用
                [
                    "ast-grep", "scan",
                    "--rule", str(rule_file),
                    "--json=compact",
                    "--include-metadata",
                ] + files,
                capture_output=True,
                text=True,
                timeout=timeout_sec,
                cwd=str(self._repo_root),
                env={**os.environ, **self._config.env},
                shell=True,  # Windows .cmd 兼容
            )
        except FileNotFoundError:
            logger.warning("AstGrepAdapter degraded: ast-grep CLI 未安装")
            return [], True
        except subprocess.TimeoutExpired:
            logger.warning("AstGrepAdapter degraded: ast-grep scan 超时(%ds)", timeout_sec)
            return [], True
        except Exception as e:  # noqa: BLE001  适配器不抛异常
            logger.warning("AstGrepAdapter degraded: ast-grep scan 异常(%s: %s)", type(e).__name__, e)
            return [], True

        # ast-grep exit codes: 0=无匹配, 1=有匹配, 8=规则解析错误
        if result.returncode == 8:
            logger.warning(
                "AstGrepAdapter degraded: 规则 %s 解析错误: %s",
                rule_file.name,
                result.stderr[:200] if result.stderr else "",
            )
            return [], True

        if result.returncode not in (0, 1):
            logger.warning(
                "AstGrepAdapter degraded: ast-grep scan 退出码=%d, stderr=%s",
                result.returncode,
                result.stderr[:200] if result.stderr else "",
            )
            return [], True

        # 解析 JSON 输出
        try:
            data = json.loads(result.stdout) if result.stdout.strip() else []
        except json.JSONDecodeError as e:
            logger.warning("AstGrepAdapter degraded: JSON 解析失败(%s)", e)
            return [], True

        findings = self._parse_findings(data, rule_file)
        return findings, False

    def _parse_findings(self, data: list[dict], rule_file: Path) -> list[Finding]:
        """将 ast-grep JSON 输出解析为 Finding 列表。"""
        findings: list[Finding] = []
        for item in data:
            try:
                findings.append(self._parse_finding(item, rule_file))
            except (KeyError, TypeError, ValueError) as e:
                logger.debug("跳过无法解析的 ast-grep finding: %s (%s)", item.get("ruleId", "?"), e)
        return findings

    def _parse_finding(self, item: dict, rule_file: Path) -> Finding:
        """解析单个 ast-grep match 为 Finding。"""
        rule_id = item.get("ruleId", rule_file.stem)

        # 文件路径 → 相对路径
        file_path = item.get("file", "")
        rel_path = self._to_relative_path(file_path)

        # 行号（ast-grep 是 0-indexed，Finding 用 1-indexed）
        range_info = item.get("range", {})
        start_info = range_info.get("start", {})
        lineno = int(start_info.get("line", 0)) + 1  # 0-indexed → 1-indexed

        # 严重性映射
        ast_grep_severity = item.get("severity", "warning")
        severity = _SEVERITY_MAP.get(ast_grep_severity, "review")

        # 生成稳定 finding_id
        finding_id = f"SG-{rule_id}-{rel_path}-{lineno}"

        return Finding(
            finding_id=finding_id,
            severity=severity,
            clone_type="rule",  # 结构模式匹配，非克隆
            similarity=1.0,  # 精确模式匹配
            source_file=rel_path,
            source_function="unknown",  # ast-grep 不提供函数上下文
            source_lineno=lineno,
            existing_file=str(rule_file.relative_to(self._repo_root)).replace("\\", "/"),
            existing_function=rule_id,  # 规则名作为 existing_function
            existing_lineno=0,
            import_suggestion=None,  # 规则违规无 import 建议
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
            # 路径不在仓库根目录下，返回原路径
            return file_path.replace("\\", "/")
