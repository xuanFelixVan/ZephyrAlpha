# [BLUEPRINT] MOD-TASK_SYSTEM | docs/03_modules/_domain_infrastructure_runtime/task_system/blueprint.md | §task-system
# [MODULE] zephyr.governance.architecture_governance.post_sync_validator
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] (none — stdlib only: shlex/subprocess/sys/re/pathlib)
# [CONSUMERS] zephyr.governance.persistence.task_repo (L1 预防); scripts.governance.audit_post_sync_commands (L3 监控)
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] post_sync_standard 命令校验逻辑的唯一真源（SSoT）；L1(task_repo.create/update) 与 L3(audit_post_sync_commands) 共同复用，禁止任何一方再行复制；返回 None=通过，str=失败原因（调用方决定抛异常或聚合报告）；仅校验含 .py 脚本的命令，非 .py（echo/git 等）跳过；--help 超时/失败不阻断（仅 flag 缺失与脚本不存在阻断）
# [MODIFY-GUARD] validate_post_sync_command / _validate_single_sub_cmd / validate_post_sync_specific / validate_rollback_instructions — 任何分支变更必须同步 task_repo._validate_post_sync_commands + task_repo._validate_post_sync_extensions 与 audit_post_sync_commands._validate_one_command 的调用方语义；行为等价性由 tests/governance/shared/test_post_sync_validation.py 36 场景守门（R01-R24 红队 + R25-R27 mutation 反馈加固 + R28-R36 W3 孪生字段扩展），并经 scripts/governance/meta/mutation_test_post_sync_validator.py 17 变异 100% 杀灭验证
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 无异常抛出——纯函数返回 str | None；调用方负责将 reason 包装为 PostSyncValidationError（L1）或聚合到报告（L3）
# [TESTS] tests/governance/shared/test_post_sync_validation.py (36 场景 R01-R36，覆盖 7 类攻击面 + W3 孪生字段)；scripts/governance/meta/mutation_test_post_sync_validator.py (17 变异, score 100%)
# [A_module] module_id=MOD-DAT_post_sync_validator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
post_sync_validator — post_sync_standard 命令校验逻辑的唯一真源（SSoT）。

消除 task_repo.py（L1 预防）与 audit_post_sync_commands.py（L3 监控）的双份逻辑漂移风险。
两个调用方对同一校验结果采取不同处置：
  - L1 (task_repo.create/update): reason 非 None 时抛 PostSyncValidationError 阻断建卡
  - L3 (audit_post_sync_commands): reason 非 None 时聚合到 broken 命令报告

校验流程（机械拦截 AI 幻觉——臆造脚本/flag）：
  1. 链式命令（&& / || / 换行）拆分为子命令，逐条校验，取第一条失败
  2. shell 解析（shlex posix=False 保留 Windows 反斜杠路径；strip 引号）
  3. pytest / py_compile 命令跳过 flag 校验（flag 由 pytest 自身管理，非 argparse）
     ——但仍校验 .py 文件存在性
  4. 定位 .py 脚本；非 .py 命令（echo/git 等）无法内省，跳过
  5. 脚本存在性（相对路径基于 repo_root 解析）
  6. 提取 --flag 参数（处理 --flag=value 格式：只取 = 前面的 flag 名）
  7. 通过 --help subprocess 校验 flag 是否在 argparse 注册（超时/失败不阻断）

历史根因：D-SIGNAL 改名 20 卡死锁事故——建卡 AI 臆造 apply_depgraph.py --diagnose，
argparse 从未注册该 flag，导致所有卡无法 transition(COMPLETED)。
"""

from __future__ import annotations

import re
import shlex
import subprocess
import sys
from pathlib import Path

__all__ = [
    "validate_post_sync_command",
    "validate_post_sync_commands",
    "validate_post_sync_specific",
    "validate_post_sync_specifics",
    "validate_rollback_instructions",
]


def validate_post_sync_command(cmd: str, repo_root: Path) -> str | None:
    """校验单条 post_sync_standard 命令（含 && / || / 换行 链式拆分）。

    返回 None 表示通过；返回字符串表示失败原因（取第一条子命令失败）。

    这是 L1(task_repo) 与 L3(audit_post_sync_commands) 共同复用的唯一真源。
    调用方负责将 reason 包装为异常（L1）或聚合到报告（L3）。
    """
    # 链式/多行命令（&&, ||, 换行）拆分为子命令逐条校验，取第一条失败
    sub_cmds = re.split(r"\s*(?:&&|\|\||\n)\s*", cmd.strip())
    for sub in sub_cmds:
        reason = _validate_single_sub_cmd(sub, repo_root)
        if reason is not None:
            return reason
    return None


def validate_post_sync_commands(
    cmds: list[str], repo_root: Path
) -> list[tuple[str, str | None]]:
    """校验一组 post_sync_standard 命令。

    返回 [(cmd, reason | None), ...]，与输入一一对应。
    reason 为 None 表示该命令通过，非 None 表示失败原因。
    """
    return [(cmd, validate_post_sync_command(cmd, repo_root)) for cmd in cmds]


def validate_post_sync_specific(cmd: str, repo_root: Path) -> str | None:
    """校验单条 post_sync_specific 命令。

    post_sync_specific 与 post_sync_standard 同型同语义（均 list[str] 命令，
    描述"完成后必须执行的同步更新"），校验逻辑完全相同——直接委托 SSoT 主体，
    禁止复制 _validate_single_sub_cmd 逻辑（MODIFY-GUARD 约束）。

    薄包装存在意义：语义清晰 + 为未来分叉留位（"specific" 可能引入更严格规则）。
    """
    return validate_post_sync_command(cmd, repo_root)


def validate_post_sync_specifics(
    cmds: list[str], repo_root: Path
) -> list[tuple[str, str | None]]:
    """校验一组 post_sync_specific 命令（与 validate_post_sync_commands 对称）。"""
    return [(cmd, validate_post_sync_specific(cmd, repo_root)) for cmd in cmds]


# rollback_instructions 轻量语义校验阈值（与 task_repo.py dimension 函数对齐）
_ROLLBACK_MIN_LENGTH = 20
# 仅在出现 `python xxx.py` 调用时触发脚本存在性轻校验（git/echo/描述性文本不触发）
_PY_INVOCATION_RE = re.compile(r"\bpython\s+\S+\.py\b")


def validate_rollback_instructions(text: str, repo_root: Path) -> str | None:
    """校验 rollback_instructions 字段（str，异构：描述性步骤 + 命令混合）。

    轻量语义校验（不套命令级校验，避免误杀描述性内容）：
      1. 非空且 strip 后非空
      2. 长度 ≥ 20 字符（与 task_repo.py L1783 dimension 阈值对齐）
      3. 若文本中出现 ``python xxx.py`` 调用，对其中 .py 路径做存在性轻校验
         （仅存在性，不做 argparse flag 校验——回滚步骤的 flag 可能是临时的）
      4. 描述性文本 / git 命令 / "用 X 覆盖 Y" 等纯描述：直接通过

    返回 None 表示通过；返回字符串表示失败原因。
    """
    if not text or not text.strip():
        return "rollback_instructions 为空"
    stripped = text.strip()
    if len(stripped) < _ROLLBACK_MIN_LENGTH:
        return f"rollback_instructions 过短（<{_ROLLBACK_MIN_LENGTH}字），无法表达撤销步骤"
    # 仅对 python .py 调用做存在性轻校验（git checkout / 描述性文本不触发）
    for match in _PY_INVOCATION_RE.finditer(text):
        script_token = match.group(0).split()[1]  # 取 "python xxx.py" 的 xxx.py
        p = Path(script_token)
        if not p.is_absolute():
            p = repo_root / p
        if not p.exists():
            return f"rollback_instructions 引用不存在的脚本: {script_token}（解析为 {p}）"
    return None


def _check_pytest_py_compile_shortcut(parts: list[str], repo_root: Path) -> str | None:
    """pytest / py_compile 命令的 flag 校验短路处理。

    pytest 的 --tb/--timeout 等 flag 由 pytest 自身管理，不是 test 文件的 argparse flag；
    py_compile 的目标 .py 是编译目标，不是可执行脚本。
    仍校验 .py 文件存在性，但不校验 flag，直接返回 None（通过）。
    """
    # 仍校验 .py 文件存在性，但不校验 flag
    script_path = next((t for t in parts if t.endswith(".py")), None)
    if script_path is not None:
        p = Path(script_path)
        if not p.is_absolute():
            p = repo_root / p
        if not p.exists():
            return f"文件不存在: {script_path}（解析为 {p}）"
    return None  # pytest/py_compile flag 由模块自身管理，跳过


def _validate_flags_via_help(parts: list[str], script_path_obj: Path) -> str | None:
    """提取 --flag 参数，通过 ``<脚本> --help`` 输出校验 flag 是否在 argparse 注册。

    处理 ``--flag=value`` 格式：只取 = 前面的 flag 名（argparse 合法语法）。
    --help 超时/异常/非零退出码均不阻断（视为通过，跳过 flag 校验）。
    """
    # 处理 --flag=value 格式：只取 = 前面的 flag 名（argparse 合法语法）
    flags = [t.split("=")[0] for t in parts if t.startswith("--")]
    if not flags:
        return None

    try:
        result = subprocess.run(
            [sys.executable, str(script_path_obj), "--help"],
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (subprocess.TimeoutExpired, Exception):
        # --help 超时或异常无法校验，视为通过（不阻断）
        return None

    if result.returncode != 0:
        # --help 自身失败（脚本可能有 import 错误等），跳过 flag 校验
        return None

    help_text = result.stdout + result.stderr
    missing = [f for f in flags if f not in help_text]
    if missing:
        return (
            f"argparse 未注册 flag {missing}（--help 输出中未找到；"
            f"疑似臆造 flag 或 CLI 漂移，请对照 '<脚本> --help' 实际输出）"
        )

    return None


def _validate_single_sub_cmd(cmd: str, repo_root: Path) -> str | None:
    """校验单条 post_sync_standard 子命令（不含 && / || 链式操作符）。

    返回 None 表示通过；返回字符串表示失败原因。
    仅校验含 .py 脚本的命令；非 .py（echo/git 等）跳过。
    """
    # 1. shell 解析（posix=False 保留 Windows 反斜杠路径；strip 引号）
    try:
        parts = [t.strip("'\"") for t in shlex.split(cmd, posix=False)]
    except ValueError as exc:
        return f"shell 解析失败: {exc}"
    if not parts:
        return None

    # 1.5 pytest / py_compile 命令跳过 flag 校验
    # pytest 的 --tb/--timeout 等 flag 由 pytest 自身管理，不是 test 文件的 argparse flag
    # py_compile 的目标 .py 是编译目标，不是可执行脚本
    parts_lower = [p.lower() for p in parts]
    if "-m" in parts_lower:
        idx = parts_lower.index("-m")
        if idx + 1 < len(parts_lower) and parts_lower[idx + 1] in ("pytest", "py_compile"):
            return _check_pytest_py_compile_shortcut(parts, repo_root)

    # 2. 定位 .py 脚本（可能是 'python script.py' 或 'script.py'）
    script_path = next((t for t in parts if t.endswith(".py")), None)
    if script_path is None:
        # 非 .py 命令（echo/git 等），无法内省，跳过
        return None

    # 3. 脚本存在性（相对路径基于 repo_root 解析）
    p = Path(script_path)
    if not p.is_absolute():
        p = repo_root / p
    if not p.exists():
        return f"脚本不存在: {script_path}（解析为 {p}）"

    # 4. 提取 --flag 参数，通过 --help 输出校验是否注册
    return _validate_flags_via_help(parts, p)
