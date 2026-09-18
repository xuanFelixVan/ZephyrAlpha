# [A_test] module_id: MOD-GOV_vocab_convergence_test | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/validators/check_vocab_domain_convergence.py
# [MODULE] tests.governance.d5_architecture.test_check_vocab_domain_convergence
# [DOMAIN] D_GOV_SCRIPTS
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TTL] permanent
# [TESTS] —
r"""check_vocab_domain_convergence 测试（裁定#335 战役 st-vocabconsol-20260918）。

覆盖：①差集非空→exit 1；②收敛→exit 0；③散文/通配/注释不算在用（字段位口径）；
④DB advisory 不翻转 exit；⑤真实三源差集=∅ 常驻验收（本战役封账判据的测试化身）。
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
_SCRIPT = REPO_ROOT / "scripts/governance/d5_architecture/validators/check_vocab_domain_convergence.py"


def _load_mod(monkeypatch, known: set[str]):
    spec = importlib.util.spec_from_file_location("check_vocab_domain_convergence", _SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    monkeypatch.setattr(mod, "_load_known", lambda: set(known))
    return mod


def _write_yaml(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


@pytest.fixture()
def argv_clean(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["check_vocab_domain_convergence"])


def _make_fdr(path: Path, domains: list[str], prose: str = "") -> Path:
    lines = ["entries:"]
    for d in domains:
        lines.append(f"  - domain: {d}\n    subdomain: x")
    if prose:
        lines.append(f"# {prose}")
    return _write_yaml(path, "\n".join(lines) + "\n")


def _make_tr(path: Path, domains: list[str], prose: str = "") -> Path:
    lines = ["entries:"]
    for d in domains:
        lines.append(f"  - module_path: pkg.{d.lower()}\n    domain_id: {d}")
    if prose:
        lines.append('plain_note: "模板示例见 D_XXX 与 D_FBL_* 通配"')
    return _write_yaml(path, "\n".join(lines) + "\n")


def test_converged_exits_pass(monkeypatch, tmp_path, argv_clean, capsys):
    mod = _load_mod(monkeypatch, {"D_ALPHA", "D_BETA"})
    monkeypatch.setattr(mod, "FDR_PATH", _make_fdr(tmp_path / "fdr.yaml", ["D_ALPHA"]))
    monkeypatch.setattr(mod, "TR_PATH", _make_tr(tmp_path / "tr.yaml", ["D_BETA"]))
    with pytest.raises(SystemExit) as e:
        mod.main()
    assert e.value.code == 0


def test_lagging_domain_exits_findings(monkeypatch, tmp_path, argv_clean, capsys):
    mod = _load_mod(monkeypatch, {"D_ALPHA"})
    monkeypatch.setattr(mod, "FDR_PATH", _make_fdr(tmp_path / "fdr.yaml", ["D_ALPHA", "D_LAGGARD"]))
    monkeypatch.setattr(mod, "TR_PATH", _make_tr(tmp_path / "tr.yaml", ["D_LAGGARD"]))
    with pytest.raises(SystemExit) as e:
        mod.main()
    assert e.value.code == 1
    err = capsys.readouterr().err
    assert "D_LAGGARD" in err


def test_prose_and_wildcards_not_counted(monkeypatch, tmp_path, argv_clean):
    """注释里的退役留案/模板通配（D_XXX、D_FBL_*）不算在用——字段位口径。"""
    mod = _load_mod(monkeypatch, {"D_ALPHA"})
    monkeypatch.setattr(
        mod, "FDR_PATH", _make_fdr(tmp_path / "fdr.yaml", ["D_ALPHA"], prose="D_RETIRED 空域退役留案, D_XXX 格式示例")
    )
    monkeypatch.setattr(mod, "TR_PATH", _make_tr(tmp_path / "tr.yaml", ["D_ALPHA"], prose="wildcard"))
    with pytest.raises(SystemExit) as e:
        mod.main()
    assert e.value.code == 0


def test_db_advisory_never_flips_exit(monkeypatch, tmp_path, argv_clean):
    mod = _load_mod(monkeypatch, {"D_ALPHA"})
    monkeypatch.setattr(mod, "FDR_PATH", _make_fdr(tmp_path / "fdr.yaml", ["D_ALPHA"]))
    monkeypatch.setattr(mod, "TR_PATH", _make_tr(tmp_path / "tr.yaml", []))
    monkeypatch.setattr(mod, "_db_domains_advisory", lambda: ["D_DB_ONLY"])
    monkeypatch.setattr(sys, "argv", ["prog", "--with-db"])
    with pytest.raises(SystemExit) as e:
        mod.main()
    assert e.value.code == 0


def test_missing_registry_exits_error(monkeypatch, tmp_path, argv_clean):
    mod = _load_mod(monkeypatch, {"D_ALPHA"})
    monkeypatch.setattr(mod, "FDR_PATH", tmp_path / "nope.yaml")
    monkeypatch.setattr(mod, "TR_PATH", tmp_path / "nope2.yaml")
    with pytest.raises(SystemExit) as e:
        mod.main()
    assert e.value.code == 2


def test_real_three_source_convergence_is_empty():
    """常驻验收：真实词表×FDR×TR 差集=∅（本战役封账判据）。"""
    spec = importlib.util.spec_from_file_location("cvdc_real", _SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    known = mod._load_known()
    used = mod._fdr_domains() | mod._tr_domains()
    assert used - known == set(), f"词表滞后域: {sorted(used - known)}"
    assert "D_GOV" in known and "D_REPORTING" in known  # 别名与收编值均可见
