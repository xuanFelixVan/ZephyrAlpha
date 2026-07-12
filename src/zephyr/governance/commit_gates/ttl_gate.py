# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.governance.commit_gates.ttl_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec); scripts.governance.d3_metadata.check_frontmatter_metadata (subprocess 调用，检测真源)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] fail-closed——checker 缺失/执行失败时阻断 commit（ttl 是强制字段，环境损坏必须阻断）；通过 subprocess 调用 check_frontmatter_metadata.py 复用真源，禁止在 gateway 内复制 ttl 校验逻辑
# [MODIFY-GUARD] gate_id="TTL-METADATA"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=通过；exit 1=有违规（阻断 commit）；exit 2=脚本异常（阻断 commit，fail-closed）
# [TESTS] tests/governance/commit_gates/test_ttl_gate.py
# [A_module] module_id=MOD-GOV-ttl_gate | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""ttl_gate.py — ttl 字段校验门禁（治本：弥补 --no-verify 绕过 pre-commit GATE-15 的缺口）

GitCommitGateway 用 ``git commit --no-verify`` 绕过 pre-commit 钩子（包括
gate-frontmatter / GATE-15），导致 ttl 字段校验在 gateway 路径完全失效。本 gate
在 commit() 内嵌 ttl 等效校验，通过 subprocess 调用 check_frontmatter_metadata.py
复用真源，避免在 gateway 内复制检测逻辑导致真源分裂。

病根（防御断层）
---------------------------------
- pre-commit 钩子 gate-frontmatter（GATE-15）只在 ``git commit``（不带 --no-verify）时触发
- GitCommitGateway 是项目唯一合法 commit 入口，但它用 --no-verify 绕过 pre-commit
- 导致 ttl 字段校验（全格式：.md/.py/.sh/.ps1/.mmd/.yaml/.json）在 gateway 路径失效
- 攻击者通过 GitCommitGateway 提交缺 ttl / ttl 值非法的文件 -> gateway 不检 ttl ->
  提交成功 -> ttl 约束被绕过（历史教训：2026-06-29 删除的 11 个漂移 YAML 正是利用
  ``# ttl: permanent`` 注释锚定自欺永久，绕过 frontmatter ttl 校验）

治本方案
--------
通过 subprocess 调用 check_frontmatter_metadata.py 复用真源（subprocess 复用真源模式，
gateway 内不复制检测逻辑）。fail-closed：checker 缺失/执行失败时阻断（ttl 是强制字段，
fail-closed 设计，防 checker 被删后静默放行）。

设计决策
--------
1. **文件列表而非 --staged**：commit() 在 gate 检查时还未 git add（gate 先于
   _commit_locked 的 git add），--staged 会返回空。改用文件列表参数。
2. **fail-closed 而非 fail-open**：ttl fail-closed 是因为"ttl 字段缺失/非法会导致
   归档判定、task_bound 清理逻辑失效"，checker 缺失属环境异常必须阻断。
3. **priority=32**：在 DIRECTORY-CONTRACT(30) 之后、R5-DIGIT-SUFFIX(35) 之前执行——
   先校验目录契约（文件放对地方），再校验 ttl 元数据（字段合法），最后校验其他约束。
4. **不传 --all-files**：增量校验（只校验本次 commit 的文件），避免全量扫描开销。
   check_frontmatter_metadata.py 自动忽略不支持的格式（只校验
   .md/.py/.sh/.ps1/.mmd/.yaml/.json）。

Usage::

    from zephyr.governance.commit_gates.ttl_gate import make_ttl_gate

    registry.register(make_ttl_gate())
    # commit() 内部：registry.check_all(gateway, files, session_id=sid, ...)
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__ = ["make_ttl_gate"]

# 命令行长度安全阈值——超过则改用 --all-files 全量扫描（避免 Windows WinError 206）
# 同 directory_contract_gate.py（ARCH-029 批次 2-15 迁移 406 文件触发 --all-files 先例）
_MAX_INLINE_FILES = 500


def make_ttl_gate() -> GateSpec:
    """构造 ttl 字段校验门禁 GateSpec（fail-closed，阻断型）。

    Returns:
        GateSpec(gate_id="TTL-METADATA", priority=32)。
        priority=32——在 DIRECTORY-CONTRACT(30) 之后、R5-DIGIT-SUFFIX(35) 之前执行
        （先校验目录契约，再校验 ttl 元数据）。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 1. 转相对路径（check_frontmatter_metadata.py 接受相对路径）
        project_root = gateway.project_root
        rel_files: list[str] = []
        for f in files:
            if not os.path.isfile(f):
                continue  # deletion commit：文件不存在，跳过（无法校验 ttl）
            rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
            rel_files.append(rel)
        if not rel_files:
            return True, "no files to check (all deletions or missing)"

        # 2. 定位 check_frontmatter_metadata.py（真源）
        check_script = (
            project_root
            / "scripts"
            / "governance"
            / "d3_metadata"
            / "check_frontmatter_metadata.py"
        )
        if not check_script.is_file():
            # fail-closed：checker 缺失是环境异常，必须阻断
            return False, f"check_frontmatter_metadata.py not found: {check_script}"

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
            # fail-closed：执行失败阻断（ttl 是强制字段）
            return False, f"check_frontmatter_metadata.py execution failed: {e}"

        # 5. 解析结果——exit 0=通过，1=有违规，2=脚本异常
        if result.returncode == 0:
            return True, "ttl metadata check passed"
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        if not detail:
            detail = result.stdout.decode("utf-8", errors="replace").strip()
        return False, detail or "ttl metadata violation (unknown detail)"

    return GateSpec(gate_id="TTL-METADATA", check=_check, priority=32)
