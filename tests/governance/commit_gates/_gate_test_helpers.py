# [BLUEPRINT] MOD-GOV_LONG_PARAM_LIST_GATE | (auto-injected by S4 reconciler) | §
# [TTL] permanent
"""_gate_test_helpers.py — commit gate 测试共享 mock gateway 构造器。

提取自 test_datetime_now_forbidden_gate.py 的 _make_mock_gateway，
供多个 gate 测试文件复用，消除 mock 逻辑重复。

提供：
- make_mock_gateway: 构造 mock gateway，_run_git 根据 cmd 返回预设结果
  - staged_files: git diff --name-only 返回的文件列表
  - file_diffs: {py_file: [added_line1, added_line2, ...]}（added 行内容）
  - file_contents: {py_file: 完整文件内容}（用于 git show :path 读 staged 版本，
    预计算 docstring 行号集合）。若 None，则根据 file_diffs 自动生成
    "纯 added 行拼接"的简化文件内容（行号从 1 开始）。
  - diff_fail: True 时 git diff --name-only 返回非 0 returncode（模拟 fail-open）。
"""

from __future__ import annotations

from unittest.mock import MagicMock


def make_mock_gateway(
    staged_files: list[str],
    file_diffs: dict[str, list[str]],
    file_contents: dict[str, str] | None = None,
    diff_fail: bool = False,
) -> MagicMock:
    """构造 mock gateway，_run_git 根据 cmd 返回预设结果。"""
    gw = MagicMock()

    def _run_git(cmd):
        result = MagicMock()
        if "--name-only" in cmd:
            if diff_fail:
                result.returncode = 1
                result.stdout = ""
                return result
            result.returncode = 0
            result.stdout = "\n".join(staged_files)
            return result
        # git show :path —— 读 staged 完整文件
        if len(cmd) >= 3 and cmd[1] == "show" and cmd[2].startswith(":"):
            py_file = cmd[2][1:].replace("\\", "/")
            content = (file_contents or {}).get(py_file)
            if content is None:
                # 默认：added 行拼成文件，行号从 1 开始
                lines = file_diffs.get(py_file, [])
                content = "\n".join(lines)
            result.returncode = 0
            result.stdout = content
            return result
        # per-file diff: cmd[-1] 是 py_file
        py_file = cmd[-1].replace("\\", "/")
        lines = file_diffs.get(py_file, [])
        # 如果提供 file_contents，查找 added 行在完整文件中的真实行号
        if file_contents and py_file in file_contents:
            file_lines = file_contents[py_file].splitlines()
            added_with_lineno: list[tuple[int, str]] = []
            for added_content in lines:
                lineno = None
                for i, fl in enumerate(file_lines, 1):
                    if fl == added_content:
                        lineno = i
                        break
                if lineno is None:
                    lineno = 1  # 默认第 1 行
                added_with_lineno.append((lineno, added_content))
            # 若 file_diffs 未指定 added 行，用 file_contents 所有行（模拟新增文件）
            if not added_with_lineno:
                added_with_lineno = list(enumerate(file_lines, 1))
        else:
            # 无 file_contents，added 行从第 1 行开始
            added_with_lineno = list(enumerate(lines, 1))

        if added_with_lineno:
            # 为每个 added 行生成独立 hunk，确保行号映射正确
            # （added 行在文件中可能不连续，不能用单个连续 hunk）
            diff_lines = [f"+++ b/{py_file}"]
            for lineno, content in added_with_lineno:
                diff_lines.append(f"@@ -0,0 +{lineno},1 @@")
                diff_lines.append(f"+{content}")
        else:
            diff_lines = [f"+++ b/{py_file}"]
        result.returncode = 0
        result.stdout = "\n".join(diff_lines)
        return result

    gw.run_git.side_effect = _run_git
    return gw
