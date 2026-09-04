# [A_test] module_id: MOD-GOV_frontend_truth_source_gate | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV_FRONTEND_TRUTH_SOURCE_GATE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] tests.governance.commit_gates.test_frontend_truth_source_gate
# [DOMAIN] D_GOV_ENFORCEMENT
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-GOV_FRONTEND_TRUTH_SOURCE_GATE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_frontend_truth_source_gate.py — FRONTEND-TRUTH-SOURCE 门禁单测

权威依据：frontend_truth_source_gate.py（make_frontend_truth_source_gate）

测试组：
- TestGateSpecFields: gate_id / priority=136 / isinstance(GateSpec)
- TestEligibleFilter: 目录契约过滤（web/ core/features 参检；services/api.js、
  loader/event_bus、app*/theme、widgets/vendor/mocks 豁免；web 外/.html 排除）
- TestInlineDataRowHeuristic: 连续 ≥6 对象行命中 / 5 行不命中 / DEMO 型数组声明 / 合法配置变量名不命中
- TestZeroWiring: 有 ZK.api/fetch 引用 → 无告警；零引用 → warn
- TestGatewayIntegration: mock gateway 流程（warn 型恒 passed=True；_HARD_BLOCK 升硬 passed=False；
  豁免文件放行；fail-open on git 失败；审计 jsonl 落盘）

测试隔离：MagicMock 模拟 gateway.run_git + tmp_path 隔离审计落盘，不读/不写真实仓库。
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import zephyr.gov_enforcement.commit_gates.frontend_truth_source_gate as g  # noqa: E402
from zephyr.gov_enforcement.commit_gates.frontend_truth_source_gate import (  # noqa: E402
    _DEMO_ARRAY_RE,
    _is_eligible,
    _is_obj_row,
    _scan_inline_data_rows,
    _scan_zero_wiring,
    make_frontend_truth_source_gate,
)
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec  # noqa: E402

_WEB = "src/zephyr/frontend/dashboard/web/"


@dataclass
class _MockResult:
    returncode: int = 0
    stdout: str = ""


def _obj_row(i: int) -> str:
    return '{ id: ' + str(i) + ', name: "x' + str(i) + '", rows: ' + str(i * 10) + ' },'


def _make_gateway(staged_files=None, file_contents=None, diff_fails=False, tmp_root=None):
    """mock gateway：name-only 返回文件列表；per-file unified=0 diff=全文件新增；git show :path 返回内容。"""
    gw = MagicMock()
    gw.project_root = tmp_root if tmp_root is not None else str(_PROJECT_ROOT)
    staged_files = staged_files or []
    file_contents = file_contents or {}

    def _run_git(cmd, *a, **k):
        cmd = list(cmd)
        if "--name-only" in cmd:
            if diff_fails:
                return _MockResult(returncode=128, stdout="")
            return _MockResult(returncode=0, stdout="\n".join(staged_files))
        if "--unified=0" in cmd:
            path = cmd[-1]
            content = file_contents.get(path)
            if content is None or diff_fails:
                return _MockResult(returncode=1, stdout="")
            body = "".join("+" + ln + "\n" for ln in content.splitlines())
            n = len(content.splitlines())
            return _MockResult(returncode=0, stdout=f"@@ -0,0 +1,{n} @@\n" + body)
        if cmd[0:2] == ["git", "show"]:
            path = cmd[2][1:]  # strip leading ':'
            return _MockResult(returncode=0, stdout=file_contents.get(path, ""))
        return _MockResult(returncode=0, stdout="")

    gw.run_git = _run_git
    return gw


class TestGateSpecFields:
    def test_gate_id_and_priority(self):
        spec = make_frontend_truth_source_gate()
        assert isinstance(spec, GateSpec)
        assert spec.gate_id == "FRONTEND-TRUTH-SOURCE"
        assert spec.priority == 136


class TestEligibleFilter:
    @pytest.mark.parametrize("path,expected", [
        (_WEB + "core/download.js", True),
        (_WEB + "core/services.js", True),
        (_WEB + "features/stockq/sq-key-data.js", True),
        (_WEB + "services/api.js", False),          # 通道基建豁免
        (_WEB + "core/loader.js", False),           # 启动器豁免
        (_WEB + "core/event_bus.js", False),        # 事件总线豁免
        (_WEB + "core/app1.js", False),             # 宿主豁免
        (_WEB + "core/theme.js", False),            # 主题豁免
        (_WEB + "widgets/tabs.js", False),          # 纯 UI 件豁免
        (_WEB + "vendor/echarts.min.js", False),    # 第三方豁免
        (_WEB + "mocks/seed.js", False),            # 演示隔离区豁免
        ("src/zephyr/frontend/dashboard/api_server.py", False),  # 非 web/ .js
        (_WEB + "pages/download.html", True),       # HTML 纳入 Check A（红队 R4 加固）
    ])
    def test_eligible(self, path, expected):
        assert _is_eligible(path) is expected


class TestInlineDataRowHeuristic:
    def test_obj_row_regex(self):
        assert _is_obj_row('  { id: 1, name: "x" },')
        assert _is_obj_row('{a:1}')                          # 末行无逗号也命中
        assert _is_obj_row('  { id: 1, cfg: { up: 1 } },')   # 一层嵌套（红队 R3 加固）
        assert not _is_obj_row('{a:1}]')                     # 行尾带 ] 非独立对象行
        assert not _is_obj_row("  h += '<td>' + t.name + '</td>';")
        assert not _is_obj_row("  name:   { label: 'x' },")  # 键开头非对象行
        assert not _is_obj_row('  { id: 1, name: "x"')       # 未闭合

    def test_run_of_six_hits(self):
        lines = [(i + 1, _obj_row(i)) for i in range(6)]
        findings = _scan_inline_data_rows(lines)
        assert len(findings) == 1
        assert "连续 6 行" in findings[0]

    def test_run_of_five_misses(self):
        lines = [(i + 1, _obj_row(i)) for i in range(5)]
        assert _scan_inline_data_rows(lines) == []

    def test_run_broken_by_code_line(self):
        lines = [(i + 1, _obj_row(i)) for i in range(4)]
        lines.append((5, "  h += '<tr>';"))
        lines += [(i + 6, _obj_row(i)) for i in range(4)]
        assert _scan_inline_data_rows(lines) == []

    def test_demo_array_declaration_hits(self):
        findings = _scan_inline_data_rows([(7, "var DL_DEMO_ROWS = [")])
        assert len(findings) == 1
        assert "DEMO/MOCK 型数组声明" in findings[0]

    def test_demo_regex_case_insensitive_and_scope(self):
        assert _DEMO_ARRAY_RE.search("const mockData = [")
        assert _DEMO_ARRAY_RE.search("let SAMPLES = [")
        assert not _DEMO_ARRAY_RE.search("var config = [")
        assert not _DEMO_ARRAY_RE.search("var DL_ORDER = {")

    def test_legit_config_var_misses(self):
        lines = [(i + 1, _obj_row(i)) for i in range(3)]
        lines.insert(0, (0, "var MENU_CFG = ["))
        assert _scan_inline_data_rows(lines) == []


class TestZeroWiring:
    def test_wired_via_zk_api(self):
        assert _scan_zero_wiring("ZK.api.fetchDownloadStatus().then(...)") == ""

    def test_wired_via_fetch(self):
        assert _scan_zero_wiring("fetch(BASE + path).then(res)") == ""

    def test_zero_wiring_warns(self):
        out = _scan_zero_wiring("function render(){ box.innerHTML = '<b>x</b>'; }")
        assert "零后端接线" in out

    def test_none_content_treated_as_unwired(self):
        assert "零后端接线" in _scan_zero_wiring(None)


class TestGatewayIntegration:
    def _fabricated_js(self):
        rows = "\n".join("  " + _obj_row(i) for i in range(8))
        return ("function render(){\nvar ROWS = [\n" + rows + "\n];\n"
                "box.innerHTML = ROWS.map(r => r.name).join();\n}\n")

    def test_fabricated_data_warns_but_passes(self, tmp_path):
        path = _WEB + "core/fake_page.js"
        gw = _make_gateway([path], {path: self._fabricated_js()}, tmp_root=tmp_path)
        passed, detail = make_frontend_truth_source_gate().check(gw, [path])
        assert passed is True                     # warn-only 起步
        assert "FRONTEND-TRUTH-SOURCE" in detail
        assert "疑似自建数据数组" in detail
        assert "零后端接线" in detail             # 该文件也无 ZK.api/fetch
        audit = tmp_path / ".runtime" / "gate_audit" / "frontend_truth_source.jsonl"
        assert audit.exists()
        rec = json.loads(audit.read_text(encoding="utf-8").strip().splitlines()[-1])
        assert rec["mode"] == "warn_only"
        assert path in rec["findings"]

    def test_wired_clean_file_passes_silent(self, tmp_path):
        path = _WEB + "core/good_page.js"
        content = ("dlLoad();\nZK.api.fetchDownloadStatus().then(function(st){ dlRender(st); });\n")
        gw = _make_gateway([path], {path: content}, tmp_root=tmp_path)
        passed, detail = make_frontend_truth_source_gate().check(gw, [path])
        assert passed is True
        assert detail == ""

    def test_exempt_files_silent(self, tmp_path):
        files = [_WEB + "services/api.js", _WEB + "core/loader.js", _WEB + "core/app2.js",
                 _WEB + "widgets/panel.js", _WEB + "vendor/x.js"]
        contents = {f: "var ROWS = [\n" + "\n".join("  " + _obj_row(i) for i in range(10)) + "\n];" for f in files}
        gw = _make_gateway(files, contents, tmp_root=tmp_path)
        passed, detail = make_frontend_truth_source_gate().check(gw, files)
        assert passed is True
        assert detail == ""

    def test_hard_block_escalation(self, tmp_path, monkeypatch):
        monkeypatch.setattr(g, "_HARD_BLOCK", True)
        path = _WEB + "core/fake_page.js"
        gw = _make_gateway([path], {path: self._fabricated_js()}, tmp_root=tmp_path)
        passed, detail = make_frontend_truth_source_gate().check(gw, [path])
        assert passed is False
        assert "FRONTEND-TRUTH-SOURCE" in detail

    def test_fail_open_on_git_error(self, tmp_path):
        path = _WEB + "core/x.js"
        gw = _make_gateway([path], {path: self._fabricated_js()}, diff_fails=True, tmp_root=tmp_path)
        passed, detail = make_frontend_truth_source_gate().check(gw, [path])
        assert passed is True
        assert detail == ""

    def test_no_web_files_silent(self, tmp_path):
        gw = _make_gateway(["src/zephyr/trading/order.py"], {}, tmp_root=tmp_path)
        passed, detail = make_frontend_truth_source_gate().check(gw, ["src/zephyr/trading/order.py"])
        assert passed is True
        assert detail == ""

    def test_audit_write_failure_non_blocking(self, tmp_path, monkeypatch):
        path = _WEB + "core/fake_page.js"
        gw = _make_gateway([path], {path: self._fabricated_js()}, tmp_root=tmp_path)
        # project_root 指向一个"文件"→ mkdir 必炸 → 审计静默不阻断
        blocker = tmp_path / "blocker"
        blocker.write_text("x", encoding="utf-8")
        gw.project_root = str(blocker)
        passed, detail = make_frontend_truth_source_gate().check(gw, [path])
        assert passed is True
        assert "FRONTEND-TRUTH-SOURCE" in detail
