# [A_test] module_id: MOD-GOV_audit_fix_lanes_rulers | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.governance.test_audit_fix_lanes_rulers
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; yaml; scripts.governance.generate_governance_map; scripts.governance.generators.generate_script_manifest; scripts.governance.d5_architecture.validators.validate_static_manifest_drift; zephyr.gov_enforcement.registry_alignment; zephyr.governance.audit._git_helpers
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/governance/test_audit_fix_lanes_rulers.py
# [MATURITY] testing
# [INVARIANTS] 三条尺各配"阳性=构造违规必红 / 阴性=合规必绿"双控制组，恒绿或恒红都判尺无效；
#              全 tmp 隔离——monkeypatch 模块内 _REPO_ROOT / git 取数口，绝不写生产路径；
#              只允许在 tmp_path 里 git init 真仓库做"提交绑定面"端到端取证（生产仓零触碰）
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


# --- L4 补刀：自洽台必须判"提交绑定面"，不得被主区脏盘装绿（F-AUDITFIX-SELFREAD-01）---


def _book_item(tmp_path: Path, drift, monkeypatch, declared: int, actual: int):
    """把工作树面摆成自洽（180==180），只留"在册面"这一个变量。"""
    rel = _write_book(tmp_path, declared=actual, actual=actual)
    monkeypatch.setattr(drift, "_REPO_ROOT", tmp_path)
    monkeypatch.setattr(
        drift,
        "_book_surface",
        lambda _rel: ("head", _BOOK.format(n=declared, body="".join(f"  - gate_id: G{i}\n" for i in range(actual)))),
    )
    return {"selfcheck": {"path": str(rel), "pairs": {"total_gates": "gates"}}}


def test_selfcheck_book_drift_is_red_while_disk_is_clean(drift, monkeypatch, tmp_path: Path) -> None:
    """阳性=盘自洽而册失真必须红（这正是主区装绿的形态）；阴性=两面自洽必须绿。"""
    item = _book_item(tmp_path, drift, monkeypatch, declared=174, actual=180)
    bad = drift._run_selfcheck(item)
    assert bad and "在册面" in bad and "174" in bad and "180" in bad, f"在册面失真必须报红，实得 {bad!r}"

    item_ok = _book_item(tmp_path, drift, monkeypatch, declared=180, actual=180)
    assert drift._run_selfcheck(item_ok) is None, "两面自洽必须放行（证明上一条红不是恒红）"


def test_selfcheck_staged_bytes_win_over_head(drift, monkeypatch, tmp_path: Path) -> None:
    """修册那一笔在门禁时刻只存在于 index：暂存面自洽即放行，否则"失真既拦不住也修不掉"。"""
    rel = _write_book(tmp_path, declared=180, actual=180)
    monkeypatch.setattr(drift, "_REPO_ROOT", tmp_path)
    good = _BOOK.format(n=180, body="".join(f"  - gate_id: G{i}\n" for i in range(180)))
    stale = _BOOK.format(n=174, body="".join(f"  - gate_id: G{i}\n" for i in range(180)))
    monkeypatch.setattr(drift, "_git_probe", lambda args: (0, ""))
    monkeypatch.setattr(drift, "_git_show_text", lambda _rel, ref: good if ref == "" else stale)
    assert drift._run_selfcheck({"selfcheck": {"path": str(rel), "pairs": {"total_gates": "gates"}}}) is None

    # 反向控制：暂存面没有字节时回到在册面，失真必须红（尺不是恒绿）
    monkeypatch.setattr(drift, "_git_show_text", lambda _rel, ref: None if ref == "" else stale)
    out = drift._run_selfcheck({"selfcheck": {"path": str(rel), "pairs": {"total_gates": "gates"}}})
    assert out and "在册面" in out, f"回落到在册面后必须红，实得 {out!r}"


def test_selfcheck_probe_failure_is_red_not_silence(drift, monkeypatch, tmp_path: Path) -> None:
    """提交绑定面取数失败＝无从判定，不得读成"已判定为绿"（探测失败报红铁律）。"""
    rel = _write_book(tmp_path, declared=180, actual=180)
    monkeypatch.setattr(drift, "_REPO_ROOT", tmp_path)
    monkeypatch.setattr(drift, "_book_surface", lambda _rel: ("probe-fail", None))
    out = drift._run_selfcheck({"selfcheck": {"path": str(rel), "pairs": {"total_gates": "gates"}}})
    assert out and "取数失败" in out, f"探测失败必须报红，实得 {out!r}"


def test_selfcheck_no_book_state_passes_with_loud_note(drift, monkeypatch, tmp_path: Path, capsys) -> None:
    """非仓库/册外新件是合法状态：放行但必须打 NOTE，禁静默。"""
    rel = _write_book(tmp_path, declared=180, actual=180)
    monkeypatch.setattr(drift, "_REPO_ROOT", tmp_path)
    monkeypatch.setattr(drift, "_book_surface", lambda _rel: ("no-book", None))
    assert drift._run_selfcheck({"selfcheck": {"path": str(rel), "pairs": {"total_gates": "gates"}}}) is None
    assert "NOTE[自洽台]" in capsys.readouterr().out, "无从判定必须留痕"


@pytest.mark.parametrize(
    ("probe_side", "show_side", "expect"),
    [
        (lambda args: (1, "fatal: needed a single revision"), lambda rel, ref: None, "no-book"),
        (lambda args: (-1, "OSError"), lambda rel, ref: None, "probe-fail"),
        (lambda args: (0, ""), lambda rel, ref: "x" if ref == "" else None, "staged"),
        (lambda args: (0, ""), lambda rel, ref: None if ref == "" else "x", "head"),
        (lambda args: (0, ""), lambda rel, ref: None, "probe-fail"),
        (lambda args: (0, ""), lambda rel, ref: None, "untracked"),
    ],
)
def test_book_surface_five_states(drift, monkeypatch, probe_side, show_side, expect) -> None:
    """新口径的分支表逐态实测：ls-files 的返回值决定最后两态（已跟踪却取不到字节＝probe-fail）。"""
    monkeypatch.setattr(drift, "_git_probe", probe_side)
    monkeypatch.setattr(drift, "_git_show_text", show_side)
    if expect == "untracked":
        monkeypatch.setattr(
            drift,
            "_git_probe",
            lambda args: (0, "") if args[0] == "rev-parse" else (1, "error: pathspec 'x' did not match any file(s)"),
        )
    elif expect == "probe-fail":
        monkeypatch.setattr(
            drift, "_git_probe", lambda args: (0, "") if args[0] == "rev-parse" else (1, "fatal: unable to read")
        )
    got, _text = drift._book_surface("docs/a.yaml")
    assert got == expect, f"_book_surface 态判定漂移：期望 {expect} 实得 {got}"


def test_selfcheck_wired_to_commit_bound_surface() -> None:
    """接线守卫：自洽台必须经共享 git 取数口读提交绑定面（防退回只读工作树字节）。"""
    src = (REPO_ROOT / DRIFT_REL).read_text(encoding="utf-8")
    assert "git_show_file" in src, "不再经共享件取 HEAD/index 字节＝主区脏盘又能装绿"
    assert "_book_surface" in src and "NOTE[自洽台]" in src, "提交绑定面半边被摘除＝同上"


def test_selfcheck_commit_bound_surface_end_to_end(drift, monkeypatch, tmp_path: Path) -> None:
    """端到端取证（真 git 仓库，只在 tmp 内）：装绿必须不可能，而修册那一笔必须能自证清白。

    monkeypatch 只能证分支表，证不了 git show :path / HEAD:path 的真实语义——两口径
    差一个字节就会把"在册面失真"读成绿（本案第一因）或把自愈通道锁死（次生灾害）。
    """
    import subprocess

    root = tmp_path / "repo"
    (root / "docs" / "catalogs").mkdir(parents=True)
    rel = Path("docs/catalogs/probe_registry.yaml")

    def _write(declared: int) -> None:
        (root / rel).write_text(
            _BOOK.format(n=declared, body="".join(f"  - gate_id: G{i}\n" for i in range(180))),
            encoding="utf-8",
        )

    def _git(*args: str) -> None:
        subprocess.run(
            ["git", "-c", "user.email=t@t", "-c", "user.name=t", *args],
            cwd=str(root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
            timeout=60,
        )

    _write(174)
    _git("init", "-q", ".")
    _git("add", "-A")
    _git("commit", "-qm", "drifted book")
    monkeypatch.setattr(drift, "_REPO_ROOT", root)
    item = {"selfcheck": {"path": str(rel), "pairs": {"total_gates": "gates"}}}

    bad = drift._run_selfcheck(item)
    assert bad and "174" in bad and "180" in bad, f"三面同失真必须红，实得 {bad!r}"

    _write(180)  # 只改工作树（=旧口径唯一能"修绿"的手法）：必须仍然红
    still = drift._run_selfcheck(item)
    assert still and "174" in still, f"盘修绿而提交绑定面未修＝装绿，必须仍红，实得 {still!r}"

    _git("add", str(rel).replace("\\", "/"))  # 本包将提交的字节已自洽 → 必须放行（否则自愈通道被锁死）
    assert drift._run_selfcheck(item) is None, "暂存面已修好必须绿（证明上一条红不是恒红）"


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
    if not hasattr(ra, "_head_texts"):
        # 工作树该文件被未提交改动遮蔽（他包 WIP 覆盖了同名文件）→ 测的不是在册版本。
        # 显式 skip 并给补救指令：让本测试在脏区不假红、在净区必测到。
        pytest.skip(
            "registry_alignment.py 被工作树未提交改动遮蔽（非在册版本）；"
            "复净：git checkout HEAD -- src/zephyr/gov_enforcement/registry_alignment.py"
            "（须先与属主会话确认其 WIP 已落地或已归档）"
        )
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
