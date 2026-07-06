# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.security.ssot_guard
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SEC_ssot_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from typing import Final
from typing import Self

#!/usr/bin/env python3
"""
SSoT 锁定卫兵 (SSoT Guard) - Pre-commit Hook
任务 ID : T-1-26
safety_level : H（治理层代码）

功能
----
检查 ``rule_catalog_registry.yaml``（规则路径目录）与暂存区治理敏感文件之间的一致性，
防止注册表与磁盘状态脱节。

真源
----
- ``REGISTRY_REL_PATH`` → ``docs/01_policies_and_standards/_registry/catalogs/rule_catalog_registry.yaml``

检查项
------
C-1  新增治理敏感文件 → 注册表必须在同一 commit 中同步暂存
C-2  注册表已暂存    → 声明的所有路径必须在磁盘上真实存在
C-3  删除治理敏感文件 → 注册表必须在同一 commit 中同步暂存
C-4  注册表路径声明格式必须合法（不允许绝对路径、反斜杠分隔符）

治理敏感路径（WATCHED_PREFIXES）
---------------------------------
见本模块 ``WATCHED_PREFIXES`` 常量（含 ``src/zephyr/``、``docs/01_policies_and_standards/`` 等）。

用法
----
作为 pre-commit hook 直接执行::

    python src/zephyr/shared/ssot_guard.py

作为模块导入（单元测试 / 集成测试）::

    from zephyr.shared.security.ssot_guard import SsotGuard, SsotViolation

pre-commit 钩子配置示例（`.pre-commit-config.yaml`）::

    - id: ssot-guard
      name: SSoT 锁定卫兵
      entry: python src/zephyr/shared/ssot_guard.py
      language: system
      pass_filenames: false
      stages: [commit]
"""

import io
import re
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path


def _fix_windows_console() -> None:
    """将 Windows 控制台 stdout/stderr 设置为 UTF-8，仅在脚本直接运行时调用。"""
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

REGISTRY_REL_PATH: Final[str] = "docs/01_policies_and_standards/_registry/catalogs/rule_catalog_registry.yaml"

WATCHED_PREFIXES: Final[tuple[str, ...]] = (
    "scripts/hooks/",
    "scripts/governance/",
    "scripts/ci_audit/",
    ".github/workflows/",
    "docs/_working/audit/STANDARDS/",
    "src/zephyr/",
    "docs/01_policies_and_standards/",
    "docs/00_meta/",
)

WATCHED_EXTENSIONS: Final[frozenset[str]] = frozenset({".py", ".yml", ".yaml", ".md"})

# 注册表 YAML 中表示文件路径的字段名（用于路径提取）
PATH_FIELD_PATTERNS: Final[tuple[str, ...]] = (
    r"^\s+path:\s+['\"]?([^\s'\"#]+)",
    r"^\s*-\s+path:\s+['\"]?([^\s'\"#]+)",
    r"^\s+core_file:\s+['\"]?([^\s'\"#]+)",
    r"^\s+canonical_path:\s+['\"]?([^\s'\"#]+)",
    r"^\s+script:\s+['\"]?([^\s'\"#]+)",
    r"^\s+entry:\s+['\"]?([^\s'\"#]+)",
)

# ---------------------------------------------------------------------------
# 例外类（继承 ZephyrBaseError 体系，保持 backward-compatible 别名）
# ---------------------------------------------------------------------------

from zephyr.shared.foundation.errors import ZephyrBaseError


class SsotError(ZephyrBaseError):
    """SSoT Guard 模块专属基类。"""
    error_code = "ZA-SH-0014"


class SsotViolation(SsotError):
    """SSoT 一致性违规——应阻断 commit。"""

    def __init__(self, check_id: str, message: str) -> None:
        self.check_id = check_id
        self.message = message
        super().__init__(f"[{check_id}] {message}")


class RegistryParseError(SsotError):
    """注册表 YAML 解析失败。"""
    error_code = "ZA-SH-0015"


# ---------------------------------------------------------------------------
# 数据结构
# ---------------------------------------------------------------------------


@dataclass
class CheckResult:
    """单条检查项的结果。"""

    check_id: str
    passed: bool
    message: str
    details: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        icon = "✅" if self.passed else "❌"
        lines = [f"{icon} [{self.check_id}] {self.message}"]
        lines.extend(f"   • {d}" for d in self.details)
        return "\n".join(lines)


@dataclass
class GuardReport:
    """完整验收报告。"""

    results: list[CheckResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(r.passed for r in self.results)

    def add(self, result: CheckResult) -> None:
        self.results.append(result)

    def __str__(self) -> str:
        sep = "─" * 60
        lines = [sep, "SSoT 锁定卫兵检查报告", sep]
        for r in self.results:
            lines.append(str(r))
        lines.append(sep)
        verdict = "✅ 全部通过，允许提交" if self.passed else "❌ 存在 SSoT 违规，已阻断提交"
        lines.append(verdict)
        lines.append(sep)
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Git 辅助函数
# ---------------------------------------------------------------------------


def _repo_root() -> Path:
    """返回 git 仓库根目录。"""
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(result.stdout.strip())


def _staged_files(repo_root: Path) -> dict[str, str]:
    """
    返回暂存区文件字典：{相对路径(forward-slash) -> git status 字符('A','M','D','R',...)}。
    使用 --diff-filter=ACDMR 涵盖新增/修改/删除/重命名/复制。
    """
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-status", "--diff-filter=ACDMR"],
        capture_output=True,
        text=True,
        cwd=repo_root,
        check=True,
    )
    staged: dict[str, str] = {}
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t")
        status_char = parts[0][0]  # 'A', 'M', 'D', 'R', 'C'
        if status_char == "R" and len(parts) >= 3:
            # 重命名：old_path -> new_path
            staged[parts[1].replace("\\", "/")] = "D"
            staged[parts[2].replace("\\", "/")] = "A"
        elif len(parts) >= 2:
            staged[parts[1].replace("\\", "/")] = status_char
    return staged


# ---------------------------------------------------------------------------
# 注册表路径提取
# ---------------------------------------------------------------------------


def _extract_declared_paths(registry_content: str) -> list[str]:
    """
    从注册表 YAML 文本中提取所有声明的文件/目录路径。
    仅做正则提取，不做完整 YAML 解析（避免 pyyaml 不可用时崩溃）。
    提取结果统一转为 forward-slash 格式，并去重。
    """
    paths: list[str] = []
    compiled = [re.compile(p) for p in PATH_FIELD_PATTERNS]
    for line in registry_content.splitlines():
        for pattern in compiled:
            m = pattern.match(line)
            if m:
                raw = m.group(1).strip().rstrip("/")
                if raw and not raw.startswith("#"):
                    paths.append(raw)  # 保留原始路径，不做反斜杠替换
                break
    return list(dict.fromkeys(paths))  # 去重保序


def _validate_path_format(path: str) -> str | None:
    """
    验证路径格式是否合法。
    返回 None 表示合法；返回错误说明字符串表示违规。
    """
    if path.startswith("/") or (len(path) > 1 and path[1] == ":"):
        return f"绝对路径不允许出现在注册表中: {path}"
    if "\\" in path:
        return f"反斜杠分隔符不允许出现在注册表路径中: {path}"
    return None


# ---------------------------------------------------------------------------
# 主检查类
# ---------------------------------------------------------------------------


class SsotGuard:
    """
    SSoT 一致性守卫。

    参数
    ----
    repo_root : Path
        git 仓库根目录（默认自动探测）。
    registry_rel : str
        注册表文件相对仓库根目录的路径。
    watched_prefixes : Sequence[str]
        治理敏感路径前缀列表。
    """

    def __init__(
        self,
        repo_root: Path | None = None,
        registry_rel: str = REGISTRY_REL_PATH,
        watched_prefixes: Sequence[str] = WATCHED_PREFIXES,
    ) -> None:
        self._repo_root: Path = repo_root or _repo_root()
        self._registry_rel = registry_rel.replace("\\", "/")
        self._watched_prefixes = tuple(p.replace("\\", "/") for p in watched_prefixes)

    # ------------------------------------------------------------------ #
    # 公开接口                                                             #
    # ------------------------------------------------------------------ #

    def run(self) -> GuardReport:
        """执行全量检查，返回报告。不抛出异常，所有结果封装在报告内。"""
        report = GuardReport()
        try:
            staged = _staged_files(self._repo_root)
        except subprocess.CalledProcessError as exc:
            report.add(
                CheckResult(
                    check_id="GIT",
                    passed=False,
                    message="无法读取 git 暂存区",
                    details=[str(exc)],
                )
            )
            return report

        registry_staged = self._registry_rel in staged

        # 暂存区中的治理敏感文件列表
        watched_staged = {path: status for path, status in staged.items() if self._is_watched(path)}

        report.add(self._check_c1(watched_staged, registry_staged))
        report.add(self._check_c3(watched_staged, registry_staged))
        if registry_staged:
            report.add(self._check_c2())
        report.add(self._check_c4_format(registry_staged))

        return report

    # ------------------------------------------------------------------ #
    # 内部检查方法                                                         #
    # ------------------------------------------------------------------ #

    def _is_watched(self, path: str) -> bool:
        """判断路径是否属于治理敏感区域。"""
        normalized = path.replace("\\", "/")
        if Path(normalized).suffix not in WATCHED_EXTENSIONS:
            return False
        return any(normalized.startswith(prefix) for prefix in self._watched_prefixes)

    def _check_c1(
        self,
        watched_staged: dict[str, str],
        registry_staged: bool,
    ) -> CheckResult:
        """C-1：新增治理文件时注册表必须同步暂存。"""
        new_files = [p for p, s in watched_staged.items() if s == "A"]
        if not new_files:
            return CheckResult(
                check_id="C-1",
                passed=True,
                message="未检测到新增治理敏感文件，跳过",
            )
        if registry_staged:
            return CheckResult(
                check_id="C-1",
                passed=True,
                message=f"新增 {len(new_files)} 个治理文件，注册表已同步暂存",
                details=new_files,
            )
        return CheckResult(
            check_id="C-1",
            passed=False,
            message=(
                f"新增了 {len(new_files)} 个治理敏感文件，"
                f"但 {self._registry_rel} 未在暂存区中。"
                "请在同一 commit 中更新注册表（AGENTS.md §B1）。"
            ),
            details=new_files,
        )

    def _check_c3(
        self,
        watched_staged: dict[str, str],
        registry_staged: bool,
    ) -> CheckResult:
        """C-3：删除治理文件时注册表必须同步暂存。"""
        deleted_files = [p for p, s in watched_staged.items() if s == "D"]
        if not deleted_files:
            return CheckResult(
                check_id="C-3",
                passed=True,
                message="未检测到删除治理敏感文件，跳过",
            )
        if registry_staged:
            return CheckResult(
                check_id="C-3",
                passed=True,
                message=f"删除 {len(deleted_files)} 个治理文件，注册表已同步暂存",
                details=deleted_files,
            )
        return CheckResult(
            check_id="C-3",
            passed=False,
            message=(
                f"删除了 {len(deleted_files)} 个治理敏感文件，"
                f"但 {self._registry_rel} 未在暂存区中。"
                "请在同一 commit 中从注册表移除对应条目（AGENTS.md §B1）。"
            ),
            details=deleted_files,
        )

    def _check_c2(self) -> CheckResult:
        """C-2：注册表已暂存时，声明路径必须真实存在（仅检查文件，不检查目录）。"""
        registry_path = self._repo_root / self._registry_rel.replace("/", "\\")
        if not registry_path.exists():
            return CheckResult(
                check_id="C-2",
                passed=False,
                message=f"注册表文件不存在: {self._registry_rel}",
            )
        try:
            content = registry_path.read_text(encoding="utf-8")
        except OSError as exc:
            return CheckResult(
                check_id="C-2",
                passed=False,
                message=f"无法读取注册表文件: {exc}",
            )

        declared = _extract_declared_paths(content)
        missing: list[str] = []
        for p in declared:
            # 归一化：Windows 反斜杠 → 正斜杠，再用 Path 解析
            normalized = p.replace("\\", "/")
            full = self._repo_root / normalized
            if full.suffix and not full.exists():
                missing.append(p)

        if missing:
            return CheckResult(
                check_id="C-2",
                passed=False,
                message=(
                    f"注册表中声明了 {len(missing)} 个文件路径，但磁盘上不存在。"
                    "请更新注册表以移除失效条目（AGENTS.md §B1）。"
                ),
                details=missing[:20],  # 最多展示 20 条，避免刷屏
            )
        return CheckResult(
            check_id="C-2",
            passed=True,
            message=f"注册表声明的 {len(declared)} 条路径均有效",
        )

    def _check_c4_format(self, registry_staged: bool) -> CheckResult:
        """C-4：注册表已暂存时，路径字段格式必须合法。"""
        if not registry_staged:
            return CheckResult(
                check_id="C-4",
                passed=True,
                message="注册表未暂存，跳过格式检查",
            )
        registry_path = self._repo_root / self._registry_rel.replace("/", "\\")
        if not registry_path.exists():
            return CheckResult(
                check_id="C-4",
                passed=False,
                message=f"注册表文件不存在: {self._registry_rel}",
            )
        try:
            content = registry_path.read_text(encoding="utf-8")
        except OSError as exc:
            return CheckResult(
                check_id="C-4",
                passed=False,
                message=f"无法读取注册表文件: {exc}",
            )

        declared = _extract_declared_paths(content)
        violations: list[str] = []
        for p in declared:
            err = _validate_path_format(p)
            if err:
                violations.append(err)

        if violations:
            return CheckResult(
                check_id="C-4",
                passed=False,
                message=f"注册表路径格式违规 {len(violations)} 处",
                details=violations,
            )
        return CheckResult(
            check_id="C-4",
            passed=True,
            message="注册表路径格式全部合法",
        )


# ---------------------------------------------------------------------------
# CLI 入口
# ---------------------------------------------------------------------------


def main() -> int:
    """Pre-commit hook 入口，返回 0（通过）或 1（阻断）。"""
    _fix_windows_console()
    print("🔒 SSoT 锁定卫兵启动...")
    guard = SsotGuard()
    report = guard.run()
    print(str(report))
    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main())
