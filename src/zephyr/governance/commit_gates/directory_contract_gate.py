# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.governance.commit_gates.directory_contract_gate
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.rule_bridge.commit_gate_registry (GateSpec); scripts.governance.d1_structure.check_directory_contract (subprocess 调用，检测真源)
# [CONSUMERS] zephyr.governance.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] fail-closed——checker 缺失/执行失败时阻断 commit（目录契约是核心约束，环境损坏必须阻断）；通过 subprocess 调用 check_directory_contract.py 复用真源，禁止在 gateway 内复制 DCR 逻辑
# [MODIFY-GUARD] gate_id="DIRECTORY-CONTRACT"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=通过；exit 1=有违规（阻断 commit）；exit 2=脚本异常（阻断 commit，fail-closed）
# [TESTS] tests/governance/commit_gates/test_directory_contract_gate.py
# [A_module] module_id=MOD-GOV-directory_contract_gate | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""directory_contract_gate.py — DCR-001~007 等效校验门禁（治本：弥补 --no-verify 绕过 pre-commit 的缺口）

GitCommitGateway 用 ``git commit --no-verify`` 绕过 pre-commit 钩子（包括
gate-directory-contract），导致 DCR-001~007 在 gateway 路径完全失效。本 gate
在 commit() 内嵌 DCR 等效校验，通过 subprocess 调用 check_directory_contract.py
复用真源，避免在 gateway 内复制检测逻辑导致真源分裂。

病根（审查报告问题1：防御断层）
---------------------------------
- pre-commit 钩子 gate-directory-contract 只在 ``git commit``（不带 --no-verify）时触发
- GitCommitGateway 是项目唯一合法 commit 入口，但它用 --no-verify 绕过 pre-commit
- 导致 DCR-001（doc_type 目录归属）、DCR-002、DCR-005（扩展名白名单）、
  DCR-006（扩展名黑名单）、DCR-007（根目录白名单）在 gateway 路径全部失效
- 攻击者通过 GitCommitGateway 提交 ``docs/03_modules/foo.py``（DCR-006 应阻断）
  -> gateway 不检扩展名 -> 提交成功 -> 目录契约被绕过

治本方案
--------
通过 subprocess 调用 check_directory_contract.py 复用真源（subprocess 复用真源模式，
gateway 内不复制检测逻辑）。fail-closed：checker 缺失/执行失败时阻断（目录契约是
核心约束，fail-closed 设计，防 checker 被删后静默放行）。

设计决策
--------
1. **文件列表而非 --staged**：commit() 在 gate 检查时还未 git add（L714 gate 先于
   L742 _commit_locked 的 git add），--staged 会返回空。改用文件列表参数。
2. **fail-closed 而非 fail-open**：DCR fail-closed 是因为"目录契约违规会导致文件
   放错地方，是严重问题"，checker 缺失属环境异常必须阻断（与检测器缺失不阻断业务
   的 fail-open 场景不同）。
3. **priority=30**：在 CLAIM-REQUIRED(40)、HELD-OVERLAP(50) 之前执行——目录契约
   是最基础的检查，应尽早拦截违规文件。
4. **不传 --all-files**：增量校验（只校验本次 commit 的文件），避免全量扫描开销。
   DCR-007（根目录白名单）对传入的根目录文件同样生效。

Usage::

    from zephyr.governance.commit_gates.directory_contract_gate import make_directory_contract_gate

    registry.register(make_directory_contract_gate())
    # commit() 内部：registry.check_all(gateway, files, session_id=sid, ...)
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys

from zephyr.governance.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__ = ["make_directory_contract_gate"]

# 命令行长度安全阈值——超过则改用 --all-files 全量扫描（避免 Windows WinError 206）
# Windows 命令行限制约32767字符，500文件×平均30字符≈15000字符，在限制内
# 200过保守（ARCH-029批次2-15迁移406文件触发--all-files全量扫描发现68预存违规阻断）
_MAX_INLINE_FILES = 500


def make_directory_contract_gate() -> GateSpec:
    """构造 DCR-001~007 等效校验门禁 GateSpec（fail-closed，阻断型）。

    Returns:
        GateSpec(gate_id="DIRECTORY-CONTRACT", priority=30)。
        priority=30——在 CLAIM-REQUIRED(40)、HELD-OVERLAP(50) 之前执行
        （目录契约是最基础检查，应尽早拦截）。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 1. 转相对路径（check_directory_contract.py 接受相对路径）
        project_root = gateway.project_root
        rel_files: list[str] = []
        for f in files:
            if not os.path.isfile(f):
                continue  # deletion commit：文件不存在，跳过（无法校验目录归属）
            rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
            rel_files.append(rel)
        if not rel_files:
            return True, "no files to check (all deletions or missing)"

        # 2. 定位 check_directory_contract.py（真源）
        check_script = (
            project_root
            / "scripts"
            / "governance"
            / "d1_structure"
            / "check_directory_contract.py"
        )
        if not check_script.is_file():
            # fail-closed：checker 缺失是环境异常，必须阻断
            return False, f"check_directory_contract.py not found: {check_script}"

        # 3. 构造命令——文件数过多时改用 --all-files（避免 WinError 206）
        if len(rel_files) > _MAX_INLINE_FILES:
            cmd = [sys.executable, str(check_script), "--all-files"]
        else:
            cmd = [sys.executable, str(check_script)] + rel_files

        # 4. subprocess 调用复用真源
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                cwd=str(project_root),
                timeout=60,
            )
        except (subprocess.TimeoutExpired, OSError) as e:
            # fail-closed：执行失败阻断（目录契约是核心约束）
            return False, f"check_directory_contract.py execution failed: {e}"

        # 5. 解析结果——exit 0=通过，1=有违规，2=脚本异常
        if result.returncode == 0:
            return True, "directory contract check passed"
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        if not detail:
            detail = result.stdout.decode("utf-8", errors="replace").strip()
        return False, detail or "directory contract violation (unknown detail)"

    return GateSpec(gate_id="DIRECTORY-CONTRACT", check=_check, priority=30)
