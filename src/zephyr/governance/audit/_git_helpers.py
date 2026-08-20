# [BLUEPRINT] MOD-GOV_GIT_HELPERS | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.governance.audit._git_helpers
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] stdlib (subprocess)
# [CONSUMERS] zephyr.governance.audit.cross_layer_contract_signature_reconciler; zephyr.governance.audit.blueprint_status_transition_reconciler
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 纯函数——reconciler 共享 git show 工具模块，提取 cross_layer_contract_signature_reconciler 与 blueprint_status_transition_reconciler 公共 _git_show_file 函数，消除 FUNCTION-DUP gate 阻断（同目录同 name+body hash 重复函数）；不可达路径 fail-open（返回 None）；纯函数无副作用
# [MODIFY-GUARD] 函数签名：git_show_file(repo_root, rel_path, ref) -> str | None
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] git 异常/超时/非零 rc 降级为 None（fail-open 不阻断调用方 reconciler）
# [TESTS] tests/governance/audit/test_git_helpers.py
# [A_module] module_id=MOD-GOV_GIT_HELPERS | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

_git_helpers.py — audit reconciler 共享 git 工具模块

治本（2026-07-21，FUNCTION-DUP 消除）：cross_layer_contract_signature_reconciler.py
与 blueprint_status_transition_reconciler.py 存在函数体完全相同的私有 helper
``_git_show_file``（git show <ref>:<path> 获取指定 ref 的文件内容），被 FUNCTION-DUP
gate 阻断。提取到本模块，通过同一实现共享给两个 reconciler。

公共函数：
- git_show_file: ``git show <ref>:<path>`` 获取指定 ref 的文件内容（fail-open 返回 None）

Usage::

    from zephyr.governance.audit._git_helpers import git_show_file

    old_source = git_show_file(str(project_root), rel_path, "HEAD~1")

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: git 仓库历史版本内容 subprocess 数据
#   fields: repo_root 仓库根 + rel_path 相对路径 + ref（HEAD/HEAD~1/commit hash）
#   code: git_show_file(repo_root, rel_path, ref) L40
# 层: 算法
# - id: A1
#   name_zh: ① git show 内容读取
#   name_en: git_show_file
#   intro: 用 git show <ref>:<path> 取指定历史版本的文件内容，失败一律返回 None
#   desc: run_subprocess_hidden 执行 git show（15s 超时，encoding=utf-8 errors=replace）→ returncode≠0 返回 None → 成功返回 stdout；异常 fail-open 返回 None
#   inputs: I1
#   outputs: 文件内容 str 或 None
#   invariant: 纯函数无副作用；fail-open 不抛异常
# 层: 输出
# - id: O1
#   name_zh: 历史版本文件内容
#   name_en: str | None
#   intro: 指定 ref 的文件文本，供 reconciler 对比新旧版本；None 表示不可达
#   downstream: cross_layer_contract_signature_reconciler 与 blueprint_status_transition_reconciler（[CONSUMERS]）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from zephyr.shared.infra.process_pool import run_subprocess_hidden

# git show 超时（秒）——对标 _reference_helpers._GIT_SHOW_TIMEOUT
_GIT_SHOW_TIMEOUT = 15


def git_show_file(repo_root: str, rel_path: str, ref: str) -> str | None:
    """``git show <ref>:<path>`` 获取指定 ref 的文件内容。

    fail-open：git 失败、文件不存在或超时均返回 None（不抛异常）。

    Args:
        repo_root: 仓库根路径。
        rel_path: 相对路径（POSIX 风格）。
        ref: git ref（如 "HEAD" / "HEAD~1" / commit hash）。

    Returns:
        文件内容字符串；失败或文件不存在返回 None。
    """
    try:
        result = run_subprocess_hidden(  # noqa: bare-subprocess  git 命令非 Python spawn，对标 _reference_helpers.get_head_content 模式
            ["git", "show", f"{ref}:{rel_path}"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=_GIT_SHOW_TIMEOUT,
        )
        if result.returncode != 0:
            return None
        return result.stdout
    except Exception:  # noqa: BLE001 — fail-open 不阻断调用方
        return None
