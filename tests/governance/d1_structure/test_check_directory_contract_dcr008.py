# [TTL] task_bound
"""test_check_directory_contract_dcr008.py — DCR-008 单元测试。

治本 #ARCH-TEMP-FILE-PLACEMENT-001（2026-07-20）：DCR-008 校验文件扩展名必须匹配
directory_contract.yaml directory_extensions[].purpose_allowed_extensions 字段。

测试组：
- TestRuntimeTmpPass: .runtime/tmp/ 合法扩展名通过（.ps1/.py/.sh/.txt/.log）
- TestRuntimeTmpBlock: .runtime/tmp/ 非法扩展名阻断（.md/.csv/.yaml/.json）
- TestDocsWorkingPass: docs/_working/ 合法扩展名通过（.md/.csv/.yaml）
- TestDocsWorkingBlock: docs/_working/ 非法扩展名阻断（.py/.ps1）
- TestAidraftsPass: .aidrafts/ 无规则放行（worktree 目录）
- TestResearchNotesPass: docs/_working/research_notes/ 子目录继承（longest-prefix match）
- TestExemptPrefixes: 豁免区（docs/_archive/、templates/）不强制用途匹配
- TestScanFilesIntegration: scan_files 集成验证调用 check_purpose_extension
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

# 确保能 import zephyr.*（pytest 自动加 src/ 到 path，但独立运行也兼容）
_SRC = Path(__file__).parent.parent.parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

# ── check_directory_contract.py 纯函数加载 ──
# check_directory_contract.py 在 scripts/ 下（非包模块），用 importlib 从文件路径加载。
# 模块自身有 bootstrap 把 _shared 所在目录加到 sys.path，exec_module 时自动执行。
_SCRIPT_DIR = Path(__file__).resolve().parent.parent.parent.parent / "scripts" / "governance" / "d1_structure"
_spec = importlib.util.spec_from_file_location(
    "_check_directory_contract_dcr008_under_test",
    _SCRIPT_DIR / "check_directory_contract.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
check_purpose_extension = _mod.check_purpose_extension
scan_files = _mod.scan_files
load_contract = _mod.load_contract


def _real_contract() -> dict:
    """加载真实 directory_contract.yaml（避免硬编码 purpose_allowed_extensions）。"""
    return load_contract()


# ════════════════════════════════════════════════════════════════════════════
# .runtime/tmp/ 合法扩展名通过（purpose_allowed_extensions: .ps1/.py/.sh/.txt/.log）
# ════════════════════════════════════════════════════════════════════════════


class TestRuntimeTmpPass:
    """.runtime/tmp/ 合法扩展名通过——LAW-2 运行时辅助脚本区。"""

    def test_ps1_pass(self):
        findings = check_purpose_extension(".runtime/tmp/script.ps1", _real_contract())
        assert findings == []

    def test_py_pass(self):
        findings = check_purpose_extension(".runtime/tmp/helper.py", _real_contract())
        assert findings == []

    def test_sh_pass(self):
        findings = check_purpose_extension(".runtime/tmp/run.sh", _real_contract())
        assert findings == []

    def test_txt_pass(self):
        findings = check_purpose_extension(".runtime/tmp/note.txt", _real_contract())
        assert findings == []

    def test_log_pass(self):
        findings = check_purpose_extension(".runtime/tmp/run.log", _real_contract())
        assert findings == []


# ════════════════════════════════════════════════════════════════════════════
# .runtime/tmp/ 非法扩展名阻断（.md 任务文档应放 docs/_working/，LAW-1）
# ════════════════════════════════════════════════════════════════════════════


class TestRuntimeTmpBlock:
    """.runtime/tmp/ 非法扩展名阻断——LAW-1 任务文档必放 docs/_working/。"""

    def test_md_blocked(self):
        findings = check_purpose_extension(".runtime/tmp/task.md", _real_contract())
        assert len(findings) == 1
        assert findings[0]["rule"] == "DCR-008"
        assert findings[0]["severity"] == "error"
        assert ".md" in findings[0]["detail"]
        assert ".runtime/tmp/" in findings[0]["detail"]

    def test_csv_blocked(self):
        findings = check_purpose_extension(".runtime/tmp/data.csv", _real_contract())
        assert len(findings) == 1
        assert findings[0]["rule"] == "DCR-008"

    def test_yaml_blocked(self):
        findings = check_purpose_extension(".runtime/tmp/conf.yaml", _real_contract())
        assert len(findings) == 1
        assert findings[0]["rule"] == "DCR-008"

    def test_json_blocked(self):
        findings = check_purpose_extension(".runtime/tmp/state.json", _real_contract())
        assert len(findings) == 1
        assert findings[0]["rule"] == "DCR-008"


# ════════════════════════════════════════════════════════════════════════════
# docs/_working/ 合法扩展名通过（purpose_allowed_extensions: .md/.csv/.yaml）
# ════════════════════════════════════════════════════════════════════════════


class TestDocsWorkingPass:
    """docs/_working/ 合法扩展名通过——LAW-1 任务文档区。"""

    def test_md_pass(self):
        findings = check_purpose_extension("docs/_working/report.md", _real_contract())
        assert findings == []

    def test_csv_pass(self):
        findings = check_purpose_extension("docs/_working/data.csv", _real_contract())
        assert findings == []

    def test_yaml_pass(self):
        findings = check_purpose_extension("docs/_working/conf.yaml", _real_contract())
        assert findings == []


# ════════════════════════════════════════════════════════════════════════════
# docs/_working/ 非法扩展名阻断（.py/.ps1 应放 .runtime/tmp/，LAW-2）
# ════════════════════════════════════════════════════════════════════════════


class TestDocsWorkingBlock:
    """docs/_working/ 非法扩展名阻断——LAW-2 运行时辅助脚本必放 .runtime/tmp/。"""

    def test_py_blocked(self):
        findings = check_purpose_extension("docs/_working/script.py", _real_contract())
        assert len(findings) == 1
        assert findings[0]["rule"] == "DCR-008"

    def test_ps1_blocked(self):
        findings = check_purpose_extension("docs/_working/run.ps1", _real_contract())
        assert len(findings) == 1
        assert findings[0]["rule"] == "DCR-008"

    def test_sh_blocked(self):
        findings = check_purpose_extension("docs/_working/run.sh", _real_contract())
        assert len(findings) == 1
        assert findings[0]["rule"] == "DCR-008"


# ════════════════════════════════════════════════════════════════════════════
# .aidrafts/ 无 directory_extensions 规则 → 放行（worktree 目录，LAW-3）
# ════════════════════════════════════════════════════════════════════════════


class TestAidraftsPass:
    """.aidrafts/ 无规则放行——LAW-3 AI session worktree 区。"""

    def test_py_pass(self):
        findings = check_purpose_extension(".aidrafts/sess-xxx/file.py", _real_contract())
        assert findings == []

    def test_md_pass(self):
        findings = check_purpose_extension(".aidrafts/sess-xxx/note.md", _real_contract())
        assert findings == []


# ════════════════════════════════════════════════════════════════════════════
# docs/_working/research_notes/ 子目录继承（longest-prefix match）
# ════════════════════════════════════════════════════════════════════════════


class TestResearchNotesPass:
    """docs/_working/research_notes/ 子目录继承——longest-prefix match 取最具体规则。"""

    def test_txt_pass(self):
        # research_notes/ purpose_allowed_extensions: [".md", ".txt", ".yaml"]
        # 比 docs/_working/ 的 [".md", ".csv", ".yaml"] 更具体，.txt 在 research_notes 允许
        findings = check_purpose_extension("docs/_working/research_notes/note.txt", _real_contract())
        assert findings == []

    def test_md_pass(self):
        findings = check_purpose_extension("docs/_working/research_notes/note.md", _real_contract())
        assert findings == []

    def test_yaml_pass(self):
        findings = check_purpose_extension("docs/_working/research_notes/notes.yaml", _real_contract())
        assert findings == []

    def test_csv_blocked_in_research_notes(self):
        # research_notes/ purpose_allowed_extensions 不含 .csv，应阻断
        findings = check_purpose_extension("docs/_working/research_notes/data.csv", _real_contract())
        assert len(findings) == 1
        assert findings[0]["rule"] == "DCR-008"


# ════════════════════════════════════════════════════════════════════════════
# 豁免区（docs/_archive/、templates/）不强制用途匹配
# ════════════════════════════════════════════════════════════════════════════


class TestExemptPrefixes:
    """豁免区不强制用途匹配——_DCR_EXTENSION_EXEMPT_PREFIXES。"""

    def test_archive_py_pass(self):
        # docs/_archive/ 在 _DCR_EXTENSION_EXEMPT_PREFIXES 中（历史归档，不强制扩展名）
        findings = check_purpose_extension("docs/_archive/legacy/script.py", _real_contract())
        assert findings == []

    def test_archive_md_pass(self):
        findings = check_purpose_extension("docs/_archive/legacy/old.md", _real_contract())
        assert findings == []

    def test_templates_py_pass(self):
        # templates/ 在 _DCR_EXTENSION_EXEMPT_PREFIXES 中（模板区，可能含多种格式示例）
        findings = check_purpose_extension("docs/01_policies_and_standards/templates/tpl.py", _real_contract())
        assert findings == []


# ════════════════════════════════════════════════════════════════════════════
# scan_files 集成——验证 scan_files 调用 check_purpose_extension（防漏调）
# ════════════════════════════════════════════════════════════════════════════


class TestScanFilesIntegration:
    """scan_files 集成——验证 scan_files 调用 check_purpose_extension（防漏调）。"""

    def test_scan_files_calls_check_purpose_extension(self, monkeypatch):
        """用 monkeypatch 替换为 spy，验证每个文件都被检测。防未来误删 scan_files 的调用。"""
        called = []

        def _spy(rel_path, contract):
            called.append(rel_path)
            return []

        monkeypatch.setattr(_mod, "check_purpose_extension", _spy)
        monkeypatch.setattr(_mod, "check_doc_type_directory", lambda *a, **k: [])
        monkeypatch.setattr(_mod, "check_extension", lambda *a, **k: [])
        monkeypatch.setattr(_mod, "check_root_whitelist", lambda *a, **k: [])
        monkeypatch.setattr(_mod, "check_ttl_zone", lambda *a, **k: [])
        monkeypatch.setattr(_mod, "check_deprecated_directory", lambda *a, **k: [])
        scan_files(["foo.py", "bar.md"], {})
        assert called == ["foo.py", "bar.md"]

    def test_scan_files_propagates_dcr008_findings(self, monkeypatch):
        """scan_files 应将 check_purpose_extension 的 finding 传播到结果中。"""
        fake_findings = [
            {
                "rule": "DCR-008",
                "severity": "error",
                "file": ".runtime/tmp/task.md",
                "detail": "test",
            }
        ]

        monkeypatch.setattr(_mod, "check_purpose_extension", lambda *a, **k: fake_findings)
        monkeypatch.setattr(_mod, "check_doc_type_directory", lambda *a, **k: [])
        monkeypatch.setattr(_mod, "check_extension", lambda *a, **k: [])
        monkeypatch.setattr(_mod, "check_root_whitelist", lambda *a, **k: [])
        monkeypatch.setattr(_mod, "check_ttl_zone", lambda *a, **k: [])
        monkeypatch.setattr(_mod, "check_deprecated_directory", lambda *a, **k: [])
        findings = scan_files([".runtime/tmp/task.md"], {})
        assert fake_findings[0] in findings

    def test_scan_files_real_contract_runtime_tmp_md_blocked(self):
        """端到端——用真实 contract 验证 .runtime/tmp/task.md 被 DCR-008 阻断。"""
        findings = scan_files([".runtime/tmp/task.md"], _real_contract())
        dcr008 = [f for f in findings if f["rule"] == "DCR-008"]
        assert len(dcr008) == 1
        assert dcr008[0]["file"] == ".runtime/tmp/task.md"

    def test_scan_files_real_contract_docs_working_md_pass(self):
        """端到端——用真实 contract 验证 docs/_working/report.md 通过 DCR-008。"""
        findings = scan_files(["docs/_working/report.md"], _real_contract())
        dcr008 = [f for f in findings if f["rule"] == "DCR-008"]
        assert dcr008 == []
