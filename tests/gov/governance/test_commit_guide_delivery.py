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
# [A_module] module_id=TEST-MOD-INF-005-TEST_COMMIT_GUIDE_DELIVERY | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""提交指路指南递送接口守卫——红=旧方式裸建文件指南必须预警，蓝=正常路径递送全绿。"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

import scripts.governance.d3_metadata.batch_creation_tokens as bct

_REPO = Path(__file__).resolve().parents[3]


def _load_git_commit():
    spec = importlib.util.spec_from_file_location("git_commit_under_test", _REPO / "scripts" / "git_commit.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def guide_sink(tmp_path, monkeypatch):
    """递送审计 sink 重定向到 tmp（零生产写不变量；绝对路径 join 覆盖 REPO_ROOT 前缀）。"""
    sink = tmp_path / "audit" / "commit_guidance_deliveries.jsonl"
    m = _load_git_commit()
    monkeypatch.setattr(m, "_GUIDE_SINK_REL", str(sink))
    return m, sink


def _read_sink(sink: Path) -> list[dict]:
    if not sink.exists():
        return []
    return [json.loads(line) for line in sink.read_text(encoding="utf-8").splitlines() if line.strip()]


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


def test_git_commit_guide_anchor_hits_gate(guide_sink, capsys):
    """红：CREATE-GUARD 死因文案 → 必须附带指南锚点行。"""
    m, sink = guide_sink
    m._print_guide_anchor("CREATE-GUARD fail-closed: 无 creation_token，禁止造第二真源: docs/x.md")
    err = capsys.readouterr().err
    assert "GUIDE: 指路锚点" in err
    assert "CREATE-GUARD" in err


def test_git_commit_guide_sink_records_delivery(guide_sink, capsys):
    """D11-C02 收口件：GUIDE 递送必须留 jsonl 回执（时间戳×exit 码×命中词条×delivered）。"""
    m, sink = guide_sink
    m._print_guide_anchor("CREATE-GUARD fail-closed: 无 creation_token: docs/x.md", exit_code=1, status="COMMIT_FAILED")
    capsys.readouterr()
    rows = _read_sink(sink)
    assert len(rows) == 1
    r = rows[0]
    assert r["delivered"] is True
    assert "CREATE-GUARD" in r["matched"]
    assert r["exit_code"] == 1
    assert r["status"] == "COMMIT_FAILED"
    assert r["ts"]  # UTC 时间戳在账


def test_git_commit_guide_sink_records_miss(guide_sink, capsys):
    """未命中词条（无 GUIDE 行）也留 delivered=false 行——递送 vs 无锚可分。"""
    m, sink = guide_sink
    m._print_guide_anchor("某个与门禁无关的普通失败", exit_code=2, status="LOCK_TIMEOUT")
    err = capsys.readouterr().err
    assert "GUIDE: 指路锚点" not in err
    rows = _read_sink(sink)
    assert len(rows) == 1
    assert rows[0]["delivered"] is False
    assert rows[0]["matched"] == []


def test_git_commit_guide_sink_fail_open(guide_sink, capsys, tmp_path, monkeypatch):
    """sink 故障（目录被文件占位）零影响递送主面：不抛、GUIDE 行照出。"""
    m, sink = guide_sink
    blocker = tmp_path / "blocker_file"
    blocker.write_text("x", encoding="utf-8")
    # 把 sink 指到"文件路径下的子目录"→ mkdir 必败
    monkeypatch.setattr(m, "_GUIDE_SINK_REL", str(blocker / "audit" / "sink.jsonl"))
    m._print_guide_anchor("CREATE-GUARD fail-closed: 无 creation_token: docs/x.md", exit_code=1, status="FAILED")
    err = capsys.readouterr().err
    assert "GUIDE: 指路锚点" in err  # 递送主面不受 sink 故障影响


def test_git_commit_guide_anchor_silent_on_no_match(guide_sink, capsys):
    m, _sink = guide_sink
    m._print_guide_anchor("某个与门禁无关的普通失败")
    err = capsys.readouterr().err
    assert "GUIDE: 指路锚点" not in err


def test_git_commit_guide_anchor_fail_open(capsys, monkeypatch):
    """源册不可达时静默降级（零输出零异常零 sink 行）。"""
    m = _load_git_commit()
    monkeypatch.setattr(m, "_DIGEST_REL", "nonexistent/digest.yaml")
    sink = _REPO / ".runtime" / "audit" / "commit_guidance_deliveries.jsonl"
    before = sink.stat().st_size if sink.exists() else 0
    m._print_guide_anchor("CREATE-GUARD 某失败")
    captured = capsys.readouterr()
    assert "GUIDE: 指路锚点" not in captured.err
    after = sink.stat().st_size if sink.exists() else 0
    assert after == before  # 降级路径零 sink 写（真仓 .runtime 不被测试污染）
