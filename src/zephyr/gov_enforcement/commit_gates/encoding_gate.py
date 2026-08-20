# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.encoding_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec); scripts.governance.d7_code.check_encoding (subprocess 调用，检测真源)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] fail-open on env error——checker 缺失/超时/exit 2 时不阻断 commit（与 pure_shim_gate/vocab_hardcode_gate/pure_assertion_gate 一致：环境异常非违规）；exit 1（检出违规）时硬阻断；通过 subprocess 调用 check_encoding.py 复用真源，禁止在 gateway 内复制编码校验逻辑
# [MODIFY-GUARD] gate_id="ENCODING-SAFETY"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=通过；exit 1=有违规（阻断 commit）；exit 2=脚本异常（fail-open，不阻断）
# [TESTS] tests/governance/commit_gates/test_encoding_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""encoding_gate.py — 编码安全校验门禁（治本：弥补 --no-verify 绕过 pre-commit GATE-ENCODING 的缺口）

GitCommitGateway 用 ``git commit --no-verify`` 绕过 pre-commit 钩子（包括
GATE-ENCODING），导致编码合规校验在 gateway 路径完全失效。本 gate 在 commit()
内嵌编码等效校验，通过 subprocess 调用 check_encoding.py 复用真源，避免在
gateway 内复制检测逻辑导致真源分裂。

病根（防御断层）
---------------------------------
- pre-commit 钩子 GATE-ENCODING 只在 ``git commit``（不带 --no-verify）时触发
- GitCommitGateway 是项目唯一合法 commit 入口，但它用 --no-verify 绕过 pre-commit
- 导致编码校验（BOM/mojibake/CRLF/.ps1 非 ASCII）在 gateway 路径失效
- 攻击者通过 GitCommitGateway 提交含中文的 .ps1 文件 -> gateway 不检编码 ->
  提交成功 -> PowerShell 5.1 ANSI 解码乱码 -> 备份脚本崩溃

治本方案
--------
通过 subprocess 调用 check_encoding.py 复用真源（subprocess 复用真源模式，
gateway 内不复制检测逻辑）。fail-open on env error：checker 缺失/超时/exit 2
时不阻断（与 pure_shim_gate/vocab_hardcode_gate/pure_assertion_gate 一致），
exit 1（检出违规）时硬阻断。

设计决策
--------
1. **文件列表而非 --staged**：commit() 在 gate 检查时还未 git add（gate 先于
   _commit_locked 的 git add），--staged 会返回空。改用文件列表参数。
2. **fail-open on env error**（2026-07-17 裁定治本）：原设计 fail-closed 导致
   测试环境（临时 git repo 无 check_encoding.py）下所有 commit 被阻断（12 个
   gateway 测试失败）。与 pure_shim_gate/vocab_hardcode_gate/pure_assertion_gate
   统一：环境异常（checker 缺失/超时/exit 2）fail-open，仅 exit 1（违规检出）
   fail-closed。checker 缺失不等于编码违规——阻断所有 commit 不解决环境问题。
3. **priority=42**：在 RENAME-DEPGRAPH-SYNC(39) 之后、FOREIGN-CHANGE(45) 之前
   执行——编码是文件级基础检查，先于内容语义检查（priority=40 已被 CLAIM-REQUIRED
   占用，priority=41 预留给 DATA-TASK-COMPLETENESS 迁移，故选 42）。
4. **按后缀过滤**：只校验 .py/.md/.yaml/.yml/.json/.toml/.ps1（与 check_encoding.py
   check_dir_encoding 一致），避免对 .png/.bin 等二进制文件无意义调用。
5. **逐文件调用 --file**：check_encoding.py 的 --file 模式只接受单个文件，
   逐文件 subprocess 调用（典型 commit 1-5 文件，性能可接受）。

Usage::

    from zephyr.gov_enforcement.commit_gates.encoding_gate import make_encoding_gate

    registry.register(make_encoding_gate())
    # commit() 内部：registry.check_all(gateway, files, session_id=sid, ...)
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys
from pathlib import Path

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec
from zephyr.shared.infra.process_pool import run_subprocess_hidden

logger = logging.getLogger(__name__)

__all__ = ["make_encoding_gate"]

# check_encoding.py 支持的后缀（与 check_dir_encoding 一致）
_CHECKED_SUFFIXES = frozenset({".py", ".md", ".yaml", ".yml", ".json", ".toml", ".ps1"})


def make_encoding_gate() -> GateSpec:
    """构造编码安全校验门禁 GateSpec（fail-closed，阻断型）。

    Returns:
        GateSpec(gate_id="ENCODING-SAFETY", priority=42)。
        priority=42——在 RENAME-DEPGRAPH-SYNC(39) 之后、FOREIGN-CHANGE(45) 之前
        （编码是文件级基础检查，先于内容语义检查；priority=40 被 CLAIM-REQUIRED 占用，
        priority=41 预留给 DATA-TASK-COMPLETENESS 迁移）。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        project_root = gateway.project_root

        # 1. 过滤相关后缀 + 转相对路径
        rel_files: list[str] = []
        for f in files:
            if not os.path.isfile(f):
                continue  # deletion commit：文件不存在，跳过
            if Path(f).suffix not in _CHECKED_SUFFIXES:
                continue
            rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
            rel_files.append(rel)
        if not rel_files:
            return True, "no files to check (no relevant suffixes)"

        # 2. 定位 check_encoding.py（真源）
        check_script = project_root / "scripts" / "governance" / "d7_code" / "check_encoding.py"
        if not check_script.is_file():
            # fail-open：checker 缺失是环境异常（测试环境/非 ZephyrAlpha 项目），
            # 不阻断 commit——与 pure_shim_gate/vocab_hardcode_gate/pure_assertion_gate 一致
            logger.warning(
                "ENCODING-SAFETY gate fail-open: check_encoding.py 不存在(%s)，检测器失效。",
                check_script,
            )
            return True, f"check_encoding.py not found, skip (fail-open): {check_script}"

        # 3. 逐文件 subprocess 调用复用真源
        failures: list[str] = []
        for rel in rel_files:
            cmd = [sys.executable, str(check_script), "--file", rel]
            try:
                result = run_subprocess_hidden(cmd, capture_output=True, cwd=str(project_root), timeout=30, text=False)
            except (subprocess.TimeoutExpired, OSError) as e:
                # fail-open：subprocess 异常是环境问题，不阻断
                logger.warning(
                    "ENCODING-SAFETY gate fail-open: check_encoding.py 执行异常(%s: %s)。",
                    type(e).__name__,
                    e,
                )
                return True, f"check_encoding.py execution error, skip (fail-open): {e}"

            # exit 0=通过，1=有违规（findings），2=脚本异常
            if result.returncode == 0:
                continue
            if result.returncode == 1:
                detail = result.stdout.decode("utf-8", errors="replace").strip()
                if not detail:
                    detail = result.stderr.decode("utf-8", errors="replace").strip()
                failures.append(detail or f"encoding violation in {rel}")
            else:
                # exit 2 或其他：脚本异常，fail-open（与 pure_shim_gate 一致）
                err = result.stderr.decode("utf-8", errors="replace").strip()
                logger.warning(
                    "ENCODING-SAFETY gate fail-open: check_encoding.py 异常(exit %d)：%s",
                    result.returncode,
                    err,
                )
                return True, f"check_encoding.py script error, skip (fail-open): {err}"

        if failures:
            return False, "\n".join(failures)
        return True, f"encoding check passed ({len(rel_files)} file(s))"

    return GateSpec(gate_id="ENCODING-SAFETY", check=_check, priority=42)
