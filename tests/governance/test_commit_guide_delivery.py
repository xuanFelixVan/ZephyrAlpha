# [BLUEPRINT] MOD-INF-005 | scripts/git_commit.py | §指南锚点 + scripts/governance/d3_metadata/batch_creation_tokens.py | §emit-guide
# [MODULE] tests.governance.test_commit_guide_delivery
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] pytest; scripts.governance.d3_metadata.batch_creation_tokens
# [CONSUMERS] 递送接口质量守卫（token 面 checklist 递送 + git_commit 面死因锚点）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 全部用例只读真仓源册+capsys 断言零生产写；红=裸建文件路径必须命中 CREATE-GUARD 预警；接口故障必须降级不抛
# [MODIFY-GUARD] 与两接口同批演进
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""提交指路指南递送接口守卫——红=旧方式裸建文件指南必须预警，蓝=正常路径递送全绿。"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import scripts.governance.d3_metadata.batch_creation_tokens as bct

_REPO = Path(__file__).resolve().parents[2]


def _load_git_commit():
    spec = importlib.util.spec_from_file_location("git_commit_under_test", _REPO / "scripts" / "git_commit.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_detect_file_types_matrix():
    assert bct.detect_file_type("src/zephyr/gov_enforcement/commit_gates/new_gate.py") == "new_src_py"
    assert bct.detect_file_type("scripts/governance/tools/foo.py") == "new_script_py"
    assert bct.detect_file_type("tests/gov/test_x.py") == "new_test_py"
    assert bct.detect_file_type("docs/01_policies_and_standards/rules/trae_088_x_y.yaml") == "rules_yaml"
    assert bct.detect_file_type("docs/01_policies_and_standards/_registry/catalogs/new_reg.yaml") == "registry_yaml"
    assert bct.detect_file_type("docs/_working/commit_system_opt/LEDGER.md") == "working_md"
    assert bct.detect_file_type("docs/01_policies_and_standards/sop/x/guide.md") == "formal_md"
    assert bct.detect_file_type("config/new_policy.yaml") == "config_yaml"
    assert bct.detect_file_type("scripts/ops/run.ps1") == "ps1"
    assert bct.detect_file_type("data/runtime/snap.json") == "other_new_asset"
    assert bct.detect_file_type("scripts/tool.sh") == "other_new_asset"
    assert bct.detect_file_type("docs/graph.mmd") == "other_new_asset"
    assert bct.detect_file_type("data/unknown.bin") is None


def test_emit_guide_warns_on_bare_new_file_red(capsys):
    """红：裸建 src .py（旧方式无 token）→ 递送段必须预警 CREATE-GUARD 步骤。"""
    bct.print_guide_for_path("src/zephyr/some_module/new_thing.py")
    out = capsys.readouterr().out
    assert "new_src_py" in out
    assert "CREATE-GUARD" in out
    assert "token 先行" in out
    assert "commit_navigation_playbook.md" in out


def test_emit_guide_degrades_fail_open(capsys, monkeypatch):
    """接口故障降级为一行指针，绝不抛异常。"""
    monkeypatch.setattr(bct, "_GUIDE_SOURCES", _REPO / "nonexistent_sources_dir")
    bct.print_guide_for_path("src/zephyr/x.py")
    out = capsys.readouterr().out
    assert "降级" in out
    assert "commit_navigation_playbook.md" in out


def test_git_commit_guide_anchor_hits_gate(capsys):
    """红：CREATE-GUARD 死因文案 → 必须附带指南锚点行。"""
    m = _load_git_commit()
    m._print_guide_anchor("CREATE-GUARD fail-closed: 无 creation_token，禁止造第二真源: docs/x.md")
    err = capsys.readouterr().err
    assert "GUIDE: 指路锚点" in err
    assert "CREATE-GUARD" in err


def test_git_commit_guide_anchor_silent_on_no_match(capsys):
    m = _load_git_commit()
    m._print_guide_anchor("某个与门禁无关的普通失败")
    err = capsys.readouterr().err
    assert "GUIDE: 指路锚点" not in err


def test_git_commit_guide_anchor_fail_open(capsys, monkeypatch):
    """源册不可达时静默降级（零输出零异常）。"""
    m = _load_git_commit()
    monkeypatch.setattr(m, "_DIGEST_REL", "nonexistent/digest.yaml")
    m._print_guide_anchor("CREATE-GUARD 某失败")
    captured = capsys.readouterr()
    assert "GUIDE: 指路锚点" not in captured.err
