# [A_test] module_id: scripts.governance.d6_security.detect_shell_dangerous | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.governance.scripts_governance.test_detect_shell_dangerous_selfdoc
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] pytest; scripts.governance.d6_security.detect_shell_dangerous
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/gov/governance/scripts_governance/test_detect_shell_dangerous_selfdoc.py
# [MATURITY] testing
# [INVARIANTS] GATE-SELFDOC .md 文档面豁免三态（2026-10-09 平权移植，同
#              test_detect_git_dangerous_selfdoc.py 红蓝基准）：带标记放行/不带标记照拦/
#              超限照拦；.md-only + 精确 gate_id（SHELL-DANGEROUS）收窄；REPO_ROOT
#              monkeypatch 到 tmp_path——测试零生产路径写入
# [MODIFY-GUARD] —
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] task_bound
"""test_detect_shell_dangerous_selfdoc.py — 危险 shell 命令门 GATE-SELFDOC 豁免三态单测。

背景（死信专案 01_ledger §三受阻件工单）：列举"禁止哪些命令"的清洁册（.md）与
案卷引文（如 night_sweep/e6_vm_assessment.md 照录 VM 复活预案删除命令）被本门
整件拦死，而 GATE-SELFDOC 行级豁免腿只存在于 git 危险命令检测器。
平权移植语义：行级标记 [GATE-SELFDOC:SHELL-DANGEROUS]（≤10 行/文件）或
frontmatter gate_selfdoc: SHELL-DANGEROUS（违规行 ≤10）放行；标记缺失=现状行为零变化。
"""

from __future__ import annotations

import importlib

import pytest

_DETECTOR = "scripts.governance.d6_security.detect_shell_dangerous"
_MARK = "[GATE-SELFDOC:SHELL-DANGEROUS]"


@pytest.fixture()
def detector(tmp_path, monkeypatch):
    """导入被测脚本并把 REPO_ROOT 锚到 tmp_path（scan_files 的仓内约束 + 审计留痕隔离）。"""
    mod = importlib.import_module(_DETECTOR)
    monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)
    return mod


def _write(tmp_path, name, text):
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return p


def test_md_marked_line_allows(detector, tmp_path, capsys):
    """带标记放行（绿证 A）：清洁册文档行引用危险字面量 + 行级标记 → 放行+审计留痕。"""
    md = _write(
        tmp_path,
        "clean_handbook.md",
        "禁止项示例：rm -rf / <!-- " + _MARK + " 策略定义文本 -->\n",
    )
    findings, _scanned, _errors = detector.scan_files([str(md)])
    assert findings == []
    err = capsys.readouterr().err
    assert "GATE-SELFDOC" in err and "audit" in err


def test_md_without_marker_blocks(detector, tmp_path, capsys):
    """不带标记照拦（红证 B）：同样本含 rm -rf / 危险字面量无标记 → 现状发现照报。"""
    md = _write(tmp_path, "plain.md", "禁止项示例：rm -rf /\n")
    findings, _scanned, _errors = detector.scan_files([str(md)])
    assert findings and "ABS-38" in findings[0]["pattern"]
    assert "GATE-SELFDOC" not in capsys.readouterr().err


def test_md_over_limit_blocks(detector, tmp_path, capsys):
    """超限照拦：标记行 11 行 > 单文件上限 10 → 照报 + stderr 提示上限。"""
    body = "".join(f"禁止项 {i}：rm -rf / <!-- " + _MARK + " -->\n" for i in range(1, 12))
    md = _write(tmp_path, "big_handbook.md", body)
    findings, _scanned, _errors = detector.scan_files([str(md)])
    assert findings
    err = capsys.readouterr().err
    assert "GATE-SELFDOC" in err and "上限" in err


def test_md_frontmatter_allows(detector, tmp_path):
    """frontmatter 形态放行：gate_selfdoc: SHELL-DANGEROUS + 违规行 ≤10 → 整文件放行。"""
    md = _write(
        tmp_path,
        "front.md",
        "---\n"
        "ttl: task_bound\n"
        "gate_selfdoc: SHELL-DANGEROUS\n"
        "---\n"
        "# shell 安全清洁册\n"
        "rm -rf / 与 chmod 777 均为禁止命令的文档枚举。\n",
    )
    findings, _scanned, _errors = detector.scan_files([str(md)])
    assert findings == []


def test_md_partial_marker_still_blocks(detector, tmp_path):
    """行级粒度：未标记行的命中照报（案卷引文同款形态：e6 评估卡恢复命令行）。"""
    md = _write(
        tmp_path,
        "partial.md",
        "标记行：rm -rf / <!-- " + _MARK + " -->\n未标记行：mkfs.ext4 /dev/sda1\n",
    )
    findings, _scanned, _errors = detector.scan_files([str(md)])
    assert findings and any("mkfs" in f["pattern"] for f in findings)
    assert all(f["line"] != 1 for f in findings)


def test_non_md_marker_ignored(detector, tmp_path):
    """收窄 .md-only：.py 带标记不豁免（代码面操作指令不给文档豁免通道）。"""
    py = _write(tmp_path, "runbook.py", 'cmd = "rm -rf /"  # ' + _MARK + "\n")
    findings, _scanned, _errors = detector.scan_files([str(py)])
    assert findings


def test_wrong_gate_id_blocked(detector, tmp_path):
    """收窄精确匹配：他门标记不豁免本门（防串用）。"""
    md = _write(
        tmp_path,
        "other.md",
        "rm -rf / <!-- [GATE-SELFDOC:GIT-DANGEROUS] 他门标记 -->\n",
    )
    findings, _scanned, _errors = detector.scan_files([str(md)])
    assert findings
