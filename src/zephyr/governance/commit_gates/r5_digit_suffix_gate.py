# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.governance.commit_gates.r5_digit_suffix_gate
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.rule_bridge.commit_gate_registry (GateSpec)
# [CONSUMERS] zephyr.governance.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] fail-closed——git ls-tree 失败时阻断 commit；增量检测只阻断新引入的 _NN 目录，历史违规目录（progressive_convergence）跳过
# [MODIFY-GUARD] gate_id="R5-DIGIT-SUFFIX"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] (True, msg)=通过；False=阻断（新引入 _NN 目录或 git 异常 fail-closed）
# [TESTS] tests/governance/commit_gates/test_r5_digit_suffix_gate.py
# [A_module] module_id=MOD-GOV-r5_digit_suffix_gate | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""r5_digit_suffix_gate.py — R5 数字后缀目录禁止门禁（治本：弥补 --no-verify 绕过 pre-commit 的缺口）

GitCommitGateway 用 ``git commit --no-verify`` 绕过 pre-commit 钩子，导致
gov_doc_003_directory_semantics R5（数字后缀目录禁止）在 gateway 路径完全失效。
本 gate 在 commit() 内嵌 R5 等效校验，阻断新建含 _NN 数字后缀的目录。

病根（预存缺口）
----------------
- R5 规则定义在 trae_028_doc_structure_naming.yaml L1224-1228（数字后缀暗示多真源）
- R5 检测脚本 validate_directory_structure.py L234-259 实际是 warning-only（L282-286
  仅 print 到 stderr，不影响 exit code），且未集成到 GitCommitGateway
- GitCommitGateway 用 --no-verify 提交，pre-commit 钩子全部失效
- 导致 AI 可通过 GitCommitGateway 新建 foo_01/ foo_02/ 等违规目录而无人拦截

治本方案
--------
gate 内部增量检测（非 subprocess 复用真源模式），理由：
1. R5 检测逻辑极简（正则 ``_\\d+$``），无需 subprocess 开销
2. 需要增量校验（只检测本次 commit 文件涉及的目录），避免全量扫描历史违规
3. validate_directory_structure.py 是全量扫描且 warning-only，不适合直接 subprocess 复用

历史违规豁免（progressive_convergence 渐进收敛策略）
-----------------------------------------------------
trae_028 L1242: "历史违规目录在下次涉及该目录的refactor时顺带修正;不发起专门批量改名任务"
实现：用 ``git ls-tree HEAD <dir>`` 判断目录是否已存在于 HEAD。
- 存在 -> 历史违规，跳过（允许正常维护）
- 不存在 -> 新引入违规，阻断

设计决策
--------
1. **priority=35**：在 DIRECTORY-CONTRACT(30) 之后、CLAIM-REQUIRED(40) 之前——
   目录命名语义是基础结构检查，应尽早拦截。
2. **fail-closed**：git ls-tree 失败时阻断（R5 是核心约束，环境异常必须阻断）。
3. **增量检测**：只检测本次 commit 的 files 参数中的路径，不全量扫描 src/zephyr/。
4. **deletion 跳过**：文件不存在（deletion commit）时跳过，无法校验目录归属。

Usage::

    from zephyr.governance.commit_gates.r5_digit_suffix_gate import make_r5_digit_suffix_gate

    registry.register(make_r5_digit_suffix_gate())
    # commit() 内部：registry.check_all(gateway, files, session_id=sid, ...)
"""

from __future__ import annotations

import logging
import os
import re
import subprocess

from zephyr.governance.rule_bridge.commit_gate_registry import GateSpec

logger = logging.getLogger(__name__)

__all__ = ["make_r5_digit_suffix_gate"]

# R5 正则——与 validate_directory_structure.py L149 _DIGIT_SUFFIX_RE 同源（_\d+ 结尾）
# 真源：trae_028_doc_structure_naming.yaml L1224-1228 gov_doc_003_directory_semantics R5
_DIGIT_SUFFIX_RE = re.compile(r"_\d+$")


def make_r5_digit_suffix_gate() -> GateSpec:
    """构造 R5 数字后缀目录禁止门禁 GateSpec（fail-closed，阻断型）。

    Returns:
        GateSpec(gate_id="R5-DIGIT-SUFFIX", priority=35)。
        priority=35——在 DIRECTORY-CONTRACT(30) 之后、CLAIM-REQUIRED(40) 之前
        （目录命名语义是基础结构检查，应尽早拦截）。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        project_root = gateway.project_root

        # 1. 收集本次 commit 文件路径中含 _NN 后缀的可疑目录
        suspect_dirs: set[str] = set()
        for f in files:
            if not os.path.isfile(f):
                continue  # deletion commit：文件不存在，跳过
            rel = os.path.relpath(f, str(project_root)).replace("\\", "/")
            parts = rel.split("/")
            # 检查每个父级目录名（排除文件名本身 parts[-1]）
            for i in range(len(parts) - 1):
                dir_name = parts[i]
                if _DIGIT_SUFFIX_RE.search(dir_name):
                    # 构造目录相对路径（含尾部 / 便于 git ls-tree）
                    dir_path = "/".join(parts[: i + 1]) + "/"
                    suspect_dirs.add(dir_path)

        if not suspect_dirs:
            return True, "no digit-suffix directories in commit paths"

        # 2. 用 git ls-tree HEAD 判断每个可疑目录是否新建
        #    存在 -> 历史违规（progressive_convergence 跳过）
        #    不存在 -> 新引入违规（阻断）
        new_violations: list[str] = []
        historical: list[str] = []
        for dir_path in sorted(suspect_dirs):
            try:
                result = subprocess.run(
                    ["git", "ls-tree", "HEAD", dir_path],
                    capture_output=True,
                    cwd=str(project_root),
                    timeout=10,
                )
            except (subprocess.TimeoutExpired, OSError) as e:
                # fail-closed：git 操作失败阻断（R5 是核心约束）
                return False, f"R5 gate fail-closed: git ls-tree failed for {dir_path}: {e}"

            if result.stdout.strip():
                # 目录已存在于 HEAD -> 历史违规，跳过
                historical.append(dir_path)
            else:
                # 目录不存在于 HEAD -> 新引入违规
                new_violations.append(dir_path)

        # 3. 返回结果
        if new_violations:
            return False, (
                f"R5 数字后缀目录禁止: {' '.join(new_violations)} -> "
                f"gov_doc_003_directory_semantics R5 禁止 _NN 数字后缀（暗示多真源，"
                f"违反 SSoT 原则）。如需区分版本请用语义不同的目录名。"
            )

        # 全部是历史违规 -> 通过（progressive_convergence 渐进收敛策略）
        return True, (
            f"digit-suffix dirs exist in HEAD (historical, skipped): "
            f"{', '.join(historical)}"
        )

    return GateSpec(gate_id="R5-DIGIT-SUFFIX", check=_check, priority=35)
