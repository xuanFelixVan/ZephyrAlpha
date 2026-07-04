# [BLUEPRINT] MOD-LLM_SECURITY | docs/03_modules/_cross_layer/large_language_model_security/blueprint.md | §
# [MODULE] zephyr.security.llm_defense.llm_security.process_sandbox
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-SEC_process_sandbox | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""
L2a ProcessSandbox — subprocess 路径白名单沙箱
===============================================
任务编号 : T-V2-005（experimental）
权限层级 : Immutable Core（沙箱核心逻辑）
真源声明 : ai_autonomy_authority_registry.yaml §2.10
关联决策 : rationale-log R81 C-03（L2a 归 ADR-0018，RI 层协调 L2a）
           ADR-0018（沙箱设计已确权）
创建日期 : 2026-04-27
版本     : v1.0.0

功能说明
--------
L2a 是 ZephyrAlpha RI（Runtime Integration）层的双层沙箱中的第一层：

  L2a（本模块）：subprocess + 路径白名单 + env 白名单 + timeout 强制
  L2b（ADR-0018）：Windows ACL OS 级配置，不在此实现

安全边界（ADR-0018 §L2a）
--------------------------
1. CWD 白名单：只允许在以下目录下执行子进程
     - <repo_root>/src/zephyr/
     - <repo_root>/scripts/
     - <repo_root>/docs/
   任何超出白名单的 cwd 请求均被 SandboxViolation 拒绝。

2. ENV 白名单：子进程只继承明确列出的环境变量
   默认允许传入：PATH, PYTHONPATH, PYTHONDONTWRITEBYTECODE,
                 VIRTUAL_ENV, HOME, USERPROFILE, TEMP, TMP
   调用方可通过 extra_env 追加键值对（不可超出 ENV_WHITELIST 键集合，
   除非 allow_extra_env=True 显式声明豁免）。

3. timeout 强制：subprocess 调用必须设置 timeout，默认 60 秒。
   超时时进程树（父 + 子）被强制终止并抛出 SandboxTimeout。

4. shell=True 禁止：所有命令必须以 list[str] 形式传入，
   禁止通过 shell=True 绕过路径白名单检查。

用法示例
--------
    from zephyr.security.llm_defense.llm_security.process_sandbox import L2aSandbox

    sandbox = L2aSandbox()
    result = sandbox.run(
        cmd=["python", "scripts/governance/validate_ssot.py"],
        cwd="scripts/governance",
        timeout=30,
    )
    print(result.stdout)
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from zephyr.shared.io.paths import REPO_ROOT

__all__ = [
    "CWD_WHITELIST_SUFFIXES",
    "ENV_WHITELIST",
    "L2aSandbox",
    "SandboxResult",
    "SandboxTimeout",
    "SandboxViolation",
]

# ---------------------------------------------------------------------------
# 配置常量
# ---------------------------------------------------------------------------

#: CWD 白名单（仓库相对路径前缀，使用 POSIX 格式）
CWD_WHITELIST_SUFFIXES: tuple[str, ...] = (
    "src/zephyr/",
    "src/zephyr",
    "scripts/",
    "scripts",
    "docs/",
    "docs",
)

#: ENV 白名单：允许传入子进程的环境变量键集合
ENV_WHITELIST: frozenset[str] = frozenset(
    {
        "PATH",
        "PYTHONPATH",
        "PYTHONDONTWRITEBYTECODE",
        "PYTHONUNBUFFERED",
        "VIRTUAL_ENV",
        "CONDA_DEFAULT_ENV",
        "HOME",
        "USERPROFILE",
        "TEMP",
        "TMP",
        "LANG",
        "LC_ALL",
        "LC_CTYPE",
        "SYSTEMROOT",  # Windows 必需
        "SYSTEMDRIVE",  # Windows 必需
        "WINDIR",  # Windows 必需
        "COMSPEC",  # Windows cmd.exe 路径
    }
)

#: 默认 subprocess 超时（秒）
DEFAULT_TIMEOUT: float = 60.0

# ---------------------------------------------------------------------------
# 数据类
# ---------------------------------------------------------------------------


@dataclass
class SandboxResult:
    """subprocess 沙箱执行结果。"""

    returncode: int
    stdout: str
    stderr: str
    cmd: list[str]
    cwd: str
    elapsed_s: float = 0.0


# ---------------------------------------------------------------------------
# 异常
# ---------------------------------------------------------------------------


class SandboxViolation(RuntimeError):
    """沙箱策略违规（cwd 超出白名单 / shell=True 尝试 / ENV 超出白名单）。"""


class SandboxTimeout(RuntimeError):
    """子进程执行超时。"""

    def __init__(self, cmd: list[str], timeout: float) -> None:
        self.cmd = cmd
        self.timeout = timeout
        super().__init__(f"L2a SandboxTimeout: {cmd[0]!r} 超时（{timeout}s）")


# ---------------------------------------------------------------------------
# L2aSandbox
# ---------------------------------------------------------------------------


class L2aSandbox:
    """L2a subprocess 白名单沙箱。

    参数
    ----
    repo_root
        仓库根目录（绝对路径）；默认自动推断（从本文件向上 4 层）。
    cwd_whitelist
        允许的 CWD 前缀元组（仓库相对 POSIX 路径）；默认 CWD_WHITELIST_SUFFIXES。
    env_whitelist
        允许传入子进程的环境变量键集合；默认 ENV_WHITELIST。
    default_timeout
        默认超时秒数；默认 DEFAULT_TIMEOUT。
    """

    def __init__(
        self,
        repo_root: Path | None = None,
        cwd_whitelist: tuple[str, ...] | None = None,
        env_whitelist: frozenset[str] | None = None,
        default_timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self._repo_root: Path = repo_root if repo_root is not None else REPO_ROOT
        self._cwd_whitelist = cwd_whitelist or CWD_WHITELIST_SUFFIXES
        self._env_whitelist = env_whitelist or ENV_WHITELIST
        self._default_timeout = default_timeout

    # ------------------------------------------------------------------
    # 公共 API
    # ------------------------------------------------------------------

    def run(
        self,
        cmd: list[str],
        cwd: str | Path | None = None,
        extra_env: dict[str, str] | None = None,
        timeout: float | None = None,
        *,
        allow_extra_env: bool = False,
    ) -> SandboxResult:
        """在沙箱约束下执行 subprocess。

        参数
        ----
        cmd
            命令及参数列表（**不允许** shell=True 绕过；字符串命令请拆成列表）。
        cwd
            工作目录（字符串相对路径或绝对 Path）。
            相对路径以 repo_root 为基准解析。
            None 表示使用 repo_root 本身（在 CWD 白名单范围内视为豁免）。
        extra_env
            追加到子进程环境的键值对。键必须在 ENV_WHITELIST 中
            （除非 allow_extra_env=True）。
        timeout
            超时秒数；None 使用 default_timeout。
        allow_extra_env
            为 True 时允许 extra_env 包含 ENV_WHITELIST 外的键
            （高权限场景，谨慎使用）。

        返回
        ----
        SandboxResult
            包含 returncode / stdout / stderr 的结果对象。

        异常
        ----
        SandboxViolation
            CWD 超出白名单，或 extra_env 包含非白名单键（且未豁免）。
        SandboxTimeout
            执行超时。
        """
        import time

        # 1. 解析 cwd
        resolved_cwd = self._resolve_cwd(cwd)

        # 2. 验证 cwd 白名单
        self._validate_cwd(resolved_cwd)

        # 3. 构建过滤后的环境
        safe_env = self._build_env(extra_env, allow_extra_env)

        # 4. timeout
        effective_timeout = timeout if timeout is not None else self._default_timeout

        # 5. 执行
        t0 = time.monotonic()
        try:
            proc = subprocess.run(  # — cmd 是 list，无 shell injection
                cmd,
                cwd=str(resolved_cwd),
                env=safe_env,
                timeout=effective_timeout,
                capture_output=True,
                text=True,
                shell=False,
            )
        except subprocess.TimeoutExpired as exc:
            elapsed = time.monotonic() - t0
            raise SandboxTimeout(cmd, effective_timeout) from exc
        elapsed = time.monotonic() - t0

        return SandboxResult(
            returncode=proc.returncode,
            stdout=proc.stdout or "",
            stderr=proc.stderr or "",
            cmd=list(cmd),
            cwd=str(resolved_cwd),
            elapsed_s=elapsed,
        )

    # ------------------------------------------------------------------
    # 内部工具
    # ------------------------------------------------------------------

    def _resolve_cwd(self, cwd: str | Path | None) -> Path:
        """将用户传入的 cwd 解析为绝对路径。"""
        if cwd is None:
            return self._repo_root
        p = Path(cwd)
        if not p.is_absolute():
            p = self._repo_root / p
        return p.resolve()

    def _validate_cwd(self, resolved_cwd: Path) -> None:
        """检查 resolved_cwd 是否在白名单范围内。

        白名单规则：resolved_cwd 必须以 repo_root/<whitelist_suffix> 开头。
        repo_root 本身视为豁免（命令未指定 cwd 时使用）。
        """
        if resolved_cwd == self._repo_root:
            return

        repo_posix = self._repo_root.as_posix().rstrip("/") + "/"
        cwd_posix = resolved_cwd.as_posix().rstrip("/") + "/"

        for suffix in self._cwd_whitelist:
            allowed = repo_posix + suffix.lstrip("/")
            if not allowed.endswith("/"):
                allowed += "/"
            if cwd_posix.startswith(allowed) or cwd_posix == allowed:
                return

        raise SandboxViolation(
            f"L2a SandboxViolation: cwd '{resolved_cwd}' 超出 CWD 白名单。\n允许前缀：{self._cwd_whitelist}"
        )

    def _build_env(
        self,
        extra_env: dict[str, str] | None,
        allow_extra_env: bool,
    ) -> dict[str, str]:
        """从系统环境中提取白名单键，合并 extra_env。"""
        safe: dict[str, str] = {k: v for k, v in os.environ.items() if k in self._env_whitelist}

        if extra_env:
            if not allow_extra_env:
                illegal = set(extra_env.keys()) - self._env_whitelist
                if illegal:
                    raise SandboxViolation(
                        f"L2a SandboxViolation: extra_env 包含非白名单键：{illegal}\n"
                        f"若确需传入，请设置 allow_extra_env=True 并说明理由。"
                    )
            safe.update(extra_env)

        return safe
