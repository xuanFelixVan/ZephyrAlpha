# [BLUEPRINT] MOD-GATE_ENGINE | scripts/governance/generate_gate_face_reconciliation.py | §红名单三态
# [TTL] permanent
# [MODULE] tests.governance.test_generate_gate_face_reconciliation
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.governance.generate_gate_face_reconciliation
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] tmp_path 假名册/假树测三列对账生成器核心逻辑（波 1A.3）：三列组行（名册声明/实载/HEAD 命中数）、红名单三态判据（R1 声明有实载 0/R2 触发面空/R3 死触发/R0 实载有名册无）、禁用门不进红名单、md+yaml 产出可复算、--check rc 语义（红非空=1/净=0）、git 面不可用拒出表 rc=2
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [A_module] module_id=MOD-TEST_GATE_FACE_RECON | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_generate_gate_face_reconciliation.py — 触发面三列对账表生成器单元测试（波 1A.3）

覆盖（tmp_path 假名册/假树，零生产路径写入；e2e 用 git init 真树）：
- build_rows: 条件触发命中数（四路语义经 _trigger_hit 真源移植）/always-run/死触发标记
- derive_red_rows: R1/R2/R3/R0 四态判据；enabled=false 不进红名单
- render_markdown/render_yaml: 计数字段承载、行序=名册物理序、红名单段完整
- main e2e（git init 真树）: 出表 rc=1（含 R2）；--check rc 语义；无 .git 面 rc=2 拒出表
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "governance"))

import generate_gate_face_reconciliation as gf  # noqa: E402

#: 真实可装载 factory（本仓在册门），供 e2e 名册走真 import→getattr→factory 链
REAL_GATE = {
    "gate_id": "HELD-OVERLAP",
    "module_path": "zephyr.gov_enforcement.commit_gates.held_overlap_gate",
    "factory_function": "make_held_overlap_gate",
    "source": "in_process",
    "enabled": True,
}

TRACKED = {"src/a.py", "src/b.py", "docs/x.md"}


def _entry(gate_id: str, *, enabled: bool = True, files_trigger: list[str] | None = None) -> dict:
    e: dict = {"gate_id": gate_id, "module_path": "m", "factory_function": "f", "enabled": enabled}
    if files_trigger is not None:
        e["files_trigger"] = files_trigger
    return e


# ── build_rows ──


def test_build_rows_three_columns() -> None:
    entries = [
        _entry("G-TRIG", files_trigger=["src/"]),
        _entry("G-ALWAYS"),
        _entry("G-DEAD", files_trigger=["nohit/"]),
    ]
    rows = gf.build_rows(entries, loaded_ids={"G-TRIG"}, tracked=TRACKED)
    assert [r["gate_id"] for r in rows] == ["G-TRIG", "G-ALWAYS", "G-DEAD"]  # 行序=名册物理序
    assert rows[0]["loaded_in_process"] is True
    assert rows[0]["head_hit_files"] == 2  # src/a.py + src/b.py（目录前缀四路语义）
    assert rows[1]["trigger_mode"] == "always-run" and rows[1]["head_hit_files"] == 0
    assert rows[2]["dead_trigger"] is True and rows[2]["head_hit_files"] == 0


def test_build_rows_per_pattern_hits() -> None:
    entries = [_entry("G", files_trigger=["src/", "docs/", "dead/"])]
    rows = gf.build_rows(entries, set(), TRACKED)
    assert rows[0]["per_pattern_hits"] == {"src/": 2, "docs/": 1, "dead/": 0}


# ── derive_red_rows ──


def test_red_rows_four_kinds() -> None:
    entries = [
        _entry("R1-GATE"),  # 声明 enabled 实载 0
        _entry("R2-GATE", files_trigger=[]),  # 空 list=always-run（与缺省同义）
        _entry("R3-GATE", files_trigger=["dead/"]),  # 死触发
        _entry("OK-GATE", files_trigger=["src/"]),
    ]
    rows = gf.build_rows(entries, {"OK-GATE", "R0-GATE"}, TRACKED)
    reds = gf.derive_red_rows(rows, loaded_ids={"OK-GATE", "R0-GATE"}, declared_ids={e["gate_id"] for e in entries})
    kinds = {(r["gate_id"], r["kind"]) for r in reds}
    assert ("R1-GATE", gf.RED_DECLARED_NOT_LOADED) in kinds
    assert ("R2-GATE", gf.RED_TRIGGER_EMPTY) in kinds
    assert ("R3-GATE", gf.RED_TRIGGER_DEAD) in kinds
    assert ("R0-GATE", gf.RED_LOADED_NOT_DECLARED) in kinds  # 实载有名册无（逆向面）
    assert ("OK-GATE", gf.RED_DECLARED_NOT_LOADED) not in kinds


def test_disabled_gate_not_red() -> None:
    entries = [_entry("OFF-GATE", enabled=False)]
    rows = gf.build_rows(entries, loaded_ids=set(), tracked=TRACKED)
    reds = gf.derive_red_rows(rows, loaded_ids=set(), declared_ids={"OFF-GATE"})
    assert reds == []  # 声明禁用=informational，不进红名单


# ── render ──


def test_render_markdown_contains_counts_and_red_section() -> None:
    entries = [_entry("A", files_trigger=["src/"]), _entry("B")]
    rows = gf.build_rows(entries, loaded_ids={"A"}, tracked=TRACKED)
    reds = gf.derive_red_rows(rows, loaded_ids={"A"}, declared_ids={"A", "B"})
    assert len(reds) == 2  # B 同时触发 R1（声明有实载 0）与 R2（触发面空）
    summary = {
        "generated_at": "2026-09-27T00:00:00+00:00",
        "head_commit": "deadbeef",
        "generator": gf.GENERATOR_REL,
        "roster_rel": "roster.yaml",
        "roster_entries": 2,
        "roster_declared_total_gates": 2,
        "enabled_count": 2,
        "disabled_count": 0,
        "loaded_count": 1,
        "load_aggregate_error": "",
        "trigger_conditional_count": 1,
        "trigger_always_run_count": 1,
        "dead_trigger_count": 0,
        "red_count": len(reds),
    }
    md = gf.render_markdown(rows, reds, [], summary)
    assert "禁手改" in md and "| roster_entries | 2 |" in md and f"| red_count | {len(reds)} |" in md
    assert "R2-trigger-empty-always-run" in md
    assert md.index("| A ") < md.index("| B ")  # 行序=名册物理序


def test_render_yaml_roundtrip() -> None:
    entries = [_entry("B")]
    rows = gf.build_rows(entries, loaded_ids=set(), tracked=TRACKED)
    reds = gf.derive_red_rows(rows, set(), {"B"})
    assert len(reds) == 2  # R1 + R2
    summary = {
        "generated_at": "t",
        "head_commit": "h",
        "generator": "g",
        "roster_rel": "r",
        "roster_entries": 1,
        "roster_declared_total_gates": 1,
        "enabled_count": 1,
        "disabled_count": 0,
        "loaded_count": 0,
        "load_aggregate_error": "",
        "trigger_conditional_count": 0,
        "trigger_always_run_count": 1,
        "dead_trigger_count": 0,
        "red_count": len(reds),
    }
    doc = yaml.safe_load(gf.render_yaml(rows, reds, summary))
    assert doc["summary"]["red_count"] == len(doc["red_list"]) == 2
    assert doc["rows"][0]["gate_id"] == "B"


# ── main e2e（git init 真树）──


def _git_init_repo(tmp_path: Path) -> Path:
    subprocess.run(["git", "init", "-q"], cwd=str(tmp_path), check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=str(tmp_path), check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=str(tmp_path), check=True)
    return tmp_path


def _write_roster(repo: Path, entries: list[dict]) -> None:
    reg = repo / "docs/01_policies_and_standards/_registry/catalogs/in_process_gate_registry.yaml"
    reg.parent.mkdir(parents=True, exist_ok=True)
    reg.write_text(
        yaml.safe_dump({"module_id": "X", "total_gates": len(entries), "gates": entries}, allow_unicode=True),
        encoding="utf-8",
    )


def test_main_e2e_writes_table_and_red_rc(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = _git_init_repo(tmp_path)
    (repo / "src").mkdir()
    (repo / "src" / "a.py").write_text("x", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=str(repo), check=True)
    subprocess.run(["git", "commit", "-qm", "init"], cwd=str(repo), check=True)
    _write_roster(repo, [dict(REAL_GATE), _entry("NO-TRIG-GATE")])
    monkeypatch.setattr(gf, "REPO_ROOT", repo)
    out_dir = repo / "out"
    rc = gf.main(["--output-dir", str(out_dir)])
    assert rc == 1  # NO-TRIG-GATE → R2 红名单非空
    md = (out_dir / "gate_face_reconciliation.md").read_text(encoding="utf-8")
    yml = yaml.safe_load((out_dir / "gate_face_reconciliation.yaml").read_text(encoding="utf-8"))
    assert "HELD-OVERLAP" in md and yml["summary"]["loaded_count"] >= 1


def test_main_e2e_clean_face_rc_zero(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = _git_init_repo(tmp_path)
    (repo / "src").mkdir()
    (repo / "src" / "a.py").write_text("x", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=str(repo), check=True)
    subprocess.run(["git", "commit", "-qm", "init"], cwd=str(repo), check=True)
    _write_roster(repo, [dict(REAL_GATE, files_trigger=["src/a.py"])])
    monkeypatch.setattr(gf, "REPO_ROOT", repo)
    assert gf.main(["--check"]) == 0  # 触发面命中且实载成功=净面


def test_main_refuses_table_without_git_tree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _write_roster(tmp_path, [dict(REAL_GATE)])  # 无 .git → tracked=None → 拒出表
    monkeypatch.setattr(gf, "REPO_ROOT", tmp_path)
    assert gf.main(["--check"]) == 2
