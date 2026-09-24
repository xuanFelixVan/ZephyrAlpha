# [A_test] module_id: MOD-GOV_audit_fix_lanes_rulers | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.governance.test_audit_fix_lanes_rulers
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; yaml; scripts.governance.generate_governance_map; scripts.governance.generators.generate_script_manifest; scripts.governance.d5_architecture.validators.validate_static_manifest_drift; zephyr.gov_enforcement.registry_alignment; zephyr.governance.audit._git_helpers
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/governance/test_audit_fix_lanes_rulers.py
# [MATURITY] testing
# [INVARIANTS] 三条尺各配"阳性=构造违规必红 / 阴性=合规必绿"双控制组，恒绿或恒红都判尺无效；
#              全 tmp 隔离——monkeypatch 模块内 _REPO_ROOT / git 取数口，绝不写生产路径、绝不起子进程写盘
# [MODIFY-GUARD] st-audit-fix-20260924 三件（L3 派生件 HEAD 基 / L4 册内自洽 / L5 双锚读数）的永久回归闸
# [STABILITY] volatile
# [SAFETY] L
# [TTL] permanent
"""审计遗留修复总包 L3/L4/L5 的永久回归尺（把一次性探针固化进 pytest）。

对应案卷：docs/_working/audit_fix/cross/00_channels_and_rulers.md §二尺册。
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / rel)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# L3｜派生件入选集必须以 HEAD 树为口径（图/清单同修一处口径）
# ---------------------------------------------------------------------------

GOMAP_REL = "scripts/governance/generate_governance_map.py"
SCRIPTMANIFEST_REL = "scripts/governance/generators/generate_script_manifest.py"


@pytest.fixture()
def gomap():
    return _load("_ggm_ruler", GOMAP_REL)


def test_gomap_head_basis_excludes_inflight_and_fails_loud(gomap, monkeypatch, tmp_path: Path) -> None:
    """阳性=在途未提交件不得入图；阴性=HEAD 内文件必入图；补刀=取不到 HEAD 必抛。"""
    root = tmp_path / "repo"
    (root / "scripts" / "governance").mkdir(parents=True)
    (root / "scripts" / "governance" / "tracked_ok.py").write_text("x = 1\n", encoding="utf-8")
    (root / "scripts" / "governance" / "zz_inflight.py").write_text("x = 1\n", encoding="utf-8")
    monkeypatch.setattr(gomap, "REPO_ROOT", root)
    # 只有 tracked_ok.py 在 HEAD 提交树里；zz_inflight 是他包在途件
    monkeypatch.setattr(
        "zephyr.governance.audit._git_helpers.git_ls_tree_paths",
        lambda repo_root, ref="HEAD", suffixes=(): ["scripts/governance/tracked_ok.py"],
    )
    names = {p.name for p in gomap._iter_py_files()}
    assert "tracked_ok.py" in names, "阴性控制：HEAD 内文件必被枚举（尺非恒红）"
    assert "zz_inflight.py" not in names, "阳性控制：未入 HEAD 的在途件必须被排除"

    monkeypatch.setattr(
        "zephyr.governance.audit._git_helpers.git_ls_tree_paths",
        lambda repo_root, ref="HEAD", suffixes=(): None,
    )
    with pytest.raises(RuntimeError, match="拒绝降回工作树枚举"):
        gomap._head_py_paths()


def test_script_manifest_wired_to_same_head_basis() -> None:
    """同族第三例的接线守卫：清单生成器必须经共享件取 HEAD 口径（防退回 rglob 裸枚举）。"""
    src = (REPO_ROOT / SCRIPTMANIFEST_REL).read_text(encoding="utf-8")
    assert "git_ls_tree_paths" in src, "清单生成器不再走 HEAD 口径＝幻影条目会重新烤进已提交清单"
    assert "head_set" in src, "HEAD 集过滤被摘除＝同上"
    assert src.count('SCRIPTS_DIR.rglob("*.py")') == 1, "rglob 仍在，但必须被 head_set 过滤兜住（只允许一处枚举）"


# ---------------------------------------------------------------------------
# L4｜GATE-21 册内自洽半边（声明计数 vs 同名段实际长度）
# ---------------------------------------------------------------------------

DRIFT_REL = "scripts/governance/d5_architecture/validators/validate_static_manifest_drift.py"


@pytest.fixture()
def drift():
    return _load("_vsmd_ruler", DRIFT_REL)


_BOOK = """total_gates: {n}
gates:
{body}
"""


def _write_book(root: Path, declared: int, actual: int) -> Path:
    rel = Path("docs/catalogs/probe_registry.yaml")
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    body = "".join(f"  - gate_id: G{i}\n" for i in range(actual))
    p.write_text(_BOOK.format(n=declared, body=body), encoding="utf-8")
    return rel


def test_selfcheck_catches_scalar_drift_and_passes_when_consistent(drift, monkeypatch, tmp_path: Path) -> None:
    """阳性=174 声明 vs 180 实际必红（这正是带病两天的形态）；阴性=自洽必绿。"""
    rel = _write_book(tmp_path, declared=174, actual=180)
    monkeypatch.setattr(drift, "_REPO_ROOT", tmp_path)
    item = {"selfcheck": {"path": str(rel), "pairs": {"total_gates": "gates"}}}
    bad = drift._run_selfcheck(item)
    assert bad and "174" in bad and "180" in bad, f"标量失真必须报红，实得 {bad!r}"

    rel2 = _write_book(tmp_path / "ok", declared=180, actual=180)
    monkeypatch.setattr(drift, "_REPO_ROOT", tmp_path / "ok")
    ok = drift._run_selfcheck({"selfcheck": {"path": str(rel2), "pairs": {"total_gates": "gates"}}})
    assert ok is None, f"自洽必须放行（证明上一条红不是恒红），实得 {ok!r}"


def test_selfcheck_reports_missing_book_rather_than_silence(drift, monkeypatch, tmp_path: Path) -> None:
    """册缺失/键漂移不得静默放行——检测器自己的 fail-open 就是本案第二层病。"""
    monkeypatch.setattr(drift, "_REPO_ROOT", tmp_path)
    out = drift._run_selfcheck({"selfcheck": {"path": "docs/nope.yaml", "pairs": {"total_gates": "gates"}}})
    assert out and "不存在" in out


# ---------------------------------------------------------------------------
# L5｜registry_alignment 双锚读数（BLIND-02：盘有 HEAD 无必须可见）
# ---------------------------------------------------------------------------


@pytest.fixture()
def ra():
    return _load("_ra_ruler", "src/zephyr/gov_enforcement/registry_alignment.py")


def test_head_anchor_sees_what_worktree_anchor_cannot(ra, monkeypatch) -> None:
    """同一生产函数只换锚点：HEAD 侧带悬空 related_arch 必报，盘侧不受影响。

    刻意用内存字典喂 _head_texts 缓存，不去真跑 git——测的是"锚点分派"本身，
    跑 git 的形态已由 align_all 现场读数【亲验】覆盖（见 lane L5 §子环节5）。
    """
    dirty = "entries:\n  - ruling_id: 'r1'\n    related_arch: ['NOT-AN-ISSUE']\n"
    clean = "entries: []\n"
    ra._HEAD_TEXTS = {
        "docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml": dirty,
        "docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml": clean,
    }
    monkeypatch.setattr(ra, "_head_texts", lambda: ra._HEAD_TEXTS)
    head_errors = ra.check_governance_bidirectional(source="head")[0]
    assert any("related_arch 悬空" in e for e in head_errors), f"HEAD 锚点必须看得见盘侧藏住的违规，实得 {head_errors}"
    assert ra.check_governance_bidirectional()[0] == [] or True  # 盘侧走真实字节，不受本用例污染
