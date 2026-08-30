# [BLUEPRINT] SH-MAIN-001 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.shared.maintenance.zero_config
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.maintenance.dogfooding
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-zero_config | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: project_root 参数
#   fields: 参数 project_root（无注解）
#   code: zero_config.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ZeroConfig
#   name_en: ZeroConfig
#   intro: class ZeroConfig 源码 L82-L189
#   desc: 公共方法（定义序）: check_python, check_git_config, scan；源码 L82-L189
#   inputs: project_root
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: ZeroConfig
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.shared.infra.process_pool import run_subprocess_hidden

"""
Zero Config — 零配置自检扫描器。

依据：
    蓝图 MOD-TASK_SYSTEM §6.5.1 + v0.6.0
    任务卡 TASK-INF-0110 (Part 1/4)
"""

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ConfigCheck:
    name: str
    passed: bool
    value: str
    message: str = ""


@dataclass
class ZeroConfigResult:
    all_passed: bool
    checks: list[ConfigCheck]
    missing: list[str]
    recommendations: list[str]


class ZeroConfig:
    REQUIRED_CONFIGS: dict[str, dict[str, Any]] = {
        "PYTHON_VERSION": {"min": "3.10", "cmd": "python --version"},
        "GIT_CONFIG": {"required": ["user.name", "user.email"]},
        "ENCODING": {"value": "utf-8"},
        "PROJECT_ROOT": {},
    }

    def __init__(self, project_root: Path | None = None) -> None:
        self._project_root = project_root or Path.cwd()

    def check_python(self) -> ConfigCheck:
        """公共接口：check_python（Stage 4 公共化）。"""
        return self._check_python()

    def check_git_config(self) -> ConfigCheck:
        """公共接口：check_git_config（Stage 4 公共化）。"""
        return self._check_git_config()

    def scan(self) -> ZeroConfigResult:
        checks: list[ConfigCheck] = []
        missing: list[str] = []
        recommendations: list[str] = []

        checks.append(self._check_python())
        checks.append(self._check_git_config())

        encoding = os.environ.get("PYTHONIOENCODING", "utf-8")
        checks.append(
            ConfigCheck(
                name="ENCODING",
                passed=encoding.lower() in ("utf-8", "utf8"),
                value=encoding,
                message="UTF-8 encoding required" if encoding.lower() not in ("utf-8", "utf8") else "OK",
            )
        )

        if not (self._project_root / ".git").exists():
            checks.append(
                ConfigCheck(
                    name="GIT_REPO",
                    passed=False,
                    value=str(self._project_root),
                    message="Not a Git repository",
                )
            )
            missing.append("git_repo")

        return ZeroConfigResult(
            all_passed=all(c.passed for c in checks),
            checks=checks,
            missing=missing,
            recommendations=recommendations,
        )

    def _check_python(self) -> ConfigCheck:
        try:
            result = run_subprocess_hidden(
                ["python", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            version_str = result.stdout.strip()
            return ConfigCheck(
                name="PYTHON",
                passed=result.returncode == 0,
                value=version_str,
                message="OK" if result.returncode == 0 else "Python not found",
            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return ConfigCheck(
                name="PYTHON",
                passed=False,
                value="N/A",
                message="Python not available",
            )

    def _check_git_config(self) -> ConfigCheck:
        try:
            user_name = run_subprocess_hidden(
                ["git", "config", "user.name"],
                capture_output=True,
                text=True,
                timeout=5,
            ).stdout.strip()

            user_email = run_subprocess_hidden(
                ["git", "config", "user.email"],
                capture_output=True,
                text=True,
                timeout=5,
            ).stdout.strip()

            ok = bool(user_name and user_email)
            return ConfigCheck(
                name="GIT_CONFIG",
                passed=ok,
                value=f"name={user_name or 'N/A'}, email={user_email or 'N/A'}",
                message="OK" if ok else "Missing user.name or user.email",
            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return ConfigCheck(
                name="GIT_CONFIG",
                passed=False,
                value="N/A",
                message="Git not available",
            )
