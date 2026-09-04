# [A_test] module_id: MOD-GOV_frontend_truth_source_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_FRONTEND_TRUTH_SOURCE_GATE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_frontend_truth_source_gate_redteam
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GOV_FRONTEND_TRUTH_SOURCE_GATE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_frontend_truth_source_gate_redteam.py — FRONTEND-TRUTH-SOURCE 红蓝对抗测试（Owner 2026-09-04 要求补做）

红队视角： adversarial AI 想给页面塞自建数据且不被 gate 点名，会怎么绕？
每个 R* 用例=一种攻击手法。R1-R4 为**真实击穿**（修复前必 FAIL，修复后转绿锁死）；
R5/R9 为**接受风险**（文档化，靠 TRAE-086 目录契约+评审兜底，非 gate 职责）；
R6/R7 验证 gate 语义边界正确。

攻击手法清单：
- R1 单行密集数组：`var t=[{a:1},{b:2},...]` 一行塞完——行级正则不识别（修复：密集 `},{` 计数）
- R2 多行键值块：对象行拆成 `{`/键值行/`},`——行级正则逐行不命中（修复：键值块状态机）
- R3 嵌套对象行：`{a:{b:1},c:2},`——`[^{}]*` 遇内层花括号失配（修复：花括号配平判定）
- R4 HTML 内联脚本：数据塞 pages/*.html 的 <script>——gate 只扫 .js（修复：Check A 纳入 .html）
- R5 widgets 伪装：数据组件伪装纯 UI 件进 widgets/——接受风险（目录契约管）
- R6 注释掉的数据行：不渲染=无害，gate 应放行（语义边界）
- R7 XHR 绕过 fetch：零接线检测仍应命中（异因同罚）
- R8 改名逃逸：数组名不含 DEMO/MOCK——行级启发式仍应命中（命名无关性）
- R9 vendor/ 藏匿：接受风险（vendor 提交本身是评审事件）

测试隔离：MagicMock 模拟 gateway.run_git + tmp_path 隔离审计，不读/不写真实仓库。
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.gov_enforcement.commit_gates.frontend_truth_source_gate import (  # noqa: E402
    make_frontend_truth_source_gate,
)

_WEB = "src/zephyr/frontend/dashboard/web/"


@dataclass
class _MockResult:
    returncode: int = 0
    stdout: str = ""


def _make_gateway(staged_files, file_contents, tmp_root):
    gw = MagicMock()
    gw.project_root = str(tmp_root)

    def _run_git(cmd, *a, **k):
        cmd = list(cmd)
        if "--name-only" in cmd:
            return _MockResult(returncode=0, stdout="\n".join(staged_files))
        if "--unified=0" in cmd:
            content = file_contents.get(cmd[-1])
            if content is None:
                return _MockResult(returncode=1, stdout="")
            body = "".join("+" + ln + "\n" for ln in content.splitlines())
            return _MockResult(returncode=0, stdout=f"@@ -0,0 +1,{len(content.splitlines())} @@\n" + body)
        if cmd[0:2] == ["git", "show"]:
            return _MockResult(returncode=0, stdout=file_contents.get(cmd[2][1:], ""))
        return _MockResult(returncode=0, stdout="")

    gw.run_git = _run_git
    return gw


def _run_gate(tmp_path, staged_files, file_contents):
    gw = _make_gateway(staged_files, file_contents, tmp_path)
    return make_frontend_truth_source_gate().check(gw, staged_files)


# ── R1 单行密集数组（修复前必击穿）──
def test_r1_single_line_dense_array(tmp_path):
    path = _WEB + "core/sneak.js"
    content = "var t = [{a:1},{b:2},{c:3},{d:4},{e:5},{f:6},{g:7}];\nbox.innerHTML = t.length;\n"
    passed, detail = _run_gate(tmp_path, [path], {path: content})
    assert passed is True
    assert "疑似自建数据" in detail, "R1 击穿：单行密集数组绕过了行级启发式"


# ── R2 多行键值块（修复前必击穿）──
def test_r2_multiline_kv_block(tmp_path):
    path = _WEB + "core/sneak2.js"
    rows = []
    for i in range(1, 5):
        rows += ["  {", f"    id: {i},", f'    name: "row{i}",', f"    val: {i * 10}", "  },"]
    content = "var rows = [\n" + "\n".join(rows) + "\n];\n"
    passed, detail = _run_gate(tmp_path, [path], {path: content})
    assert passed is True
    assert "疑似自建数据" in detail, "R2 击穿：多行键值块绕过了行级启发式"


# ── R3 嵌套对象行（修复前必击穿）──
def test_r3_nested_object_rows(tmp_path):
    path = _WEB + "core/sneak3.js"
    rows = "\n".join(f'  {{ id: {i}, cfg: {{ up: {i}, dn: {i * 2} }}, name: "x{i}" }},' for i in range(1, 7))
    content = "var rows = [\n" + rows + "\n];\n"
    passed, detail = _run_gate(tmp_path, [path], {path: content})
    assert passed is True
    assert "疑似自建数据" in detail, "R3 击穿：嵌套对象行绕过 [^{}]* 正则"


# ── R4 HTML 内联脚本数据（修复前必击穿）──
def test_r4_html_inline_script_data(tmp_path):
    path = _WEB + "pages/sneak.html"
    rows = "\n".join(f'{{ id: {i}, name: "x{i}" }},' for i in range(1, 7))
    content = "<section><script>\nvar rows = [\n" + rows + "\n];\nrender(rows);\n</script></section>\n"
    passed, detail = _run_gate(tmp_path, [path], {path: content})
    assert passed is True
    assert "疑似自建数据" in detail, "R4 击穿：HTML 内联数据不在 .js 扫描范围"


# ── R5 widgets 伪装（接受风险：TRAE-086 目录契约+评审兜底，gate 有意豁免纯 UI 件防误报）──
def test_r5_widgets_disguise_accepted_risk(tmp_path):
    path = _WEB + "widgets/sneaky.js"
    rows = "\n".join(f'  {{ id: {i}, name: "x{i}" }},' for i in range(1, 9))
    content = "var rows = [\n" + rows + "\n];\n"
    passed, detail = _run_gate(tmp_path, [path], {path: content})
    assert passed is True and detail == ""  # 文档化现状：widgets/ 豁免=接受风险，非 gate 缺陷


# ── R6 注释掉的数据行（语义边界：不渲染=无害，应放行）──
def test_r6_commented_rows_pass(tmp_path):
    path = _WEB + "core/x.js"
    rows = "\n".join(f"// {{ id: {i}, name: 'x' }}," for i in range(1, 9))
    content = "ZK.api.fetchStatus();\n" + rows + "\n"
    passed, detail = _run_gate(tmp_path, [path], {path: content})
    assert passed is True and detail == ""


# ── R7 XHR 绕过 fetch（零接线检测仍命中：异因同罚）──
def test_r7_xhr_bypass_still_warns(tmp_path):
    path = _WEB + "core/sneak4.js"
    content = "var x = new XMLHttpRequest();\nx.open('GET', '/api/data');\nx.send();\n"
    passed, detail = _run_gate(tmp_path, [path], {path: content})
    assert passed is True
    assert "零后端接线" in detail, "R7 击穿：XHR 绕过 fetch 指纹且未触发零接线告警"


# ── R8 改名逃逸（命名无关性：行级启发式不应依赖 DEMO/MOCK 命名）──
def test_r8_innocent_name_still_caught(tmp_path):
    path = _WEB + "core/sneak5.js"
    rows = "\n".join(f'  {{ id: {i}, name: "x{i}" }},' for i in range(1, 9))
    content = "var t = [\n" + rows + "\n];\n"
    passed, detail = _run_gate(tmp_path, [path], {path: content})
    assert passed is True
    assert "疑似自建数据" in detail


# ── R9 vendor 藏匿（接受风险：提交 vendor 库本身是评审事件，gate 有意豁免防海量误报）──
def test_r9_vendor_hide_accepted_risk(tmp_path):
    path = _WEB + "vendor/sneaky.js"
    rows = "\n".join(f'  {{ id: {i}, name: "x{i}" }},' for i in range(1, 9))
    content = "var rows = [\n" + rows + "\n];\n"
    passed, detail = _run_gate(tmp_path, [path], {path: content})
    assert passed is True and detail == ""  # 文档化现状：vendor/ 豁免=接受风险
