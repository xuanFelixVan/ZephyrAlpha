# [BLUEPRINT] MOD-INF-005 | scripts/governance/generators/generate_commit_guide.py | §机生守卫
# [MODULE] tests.governance.generators.test_generate_commit_guide
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] pytest; yaml; scripts.governance.generators.generate_commit_guide
# [CONSUMERS] 指南生成器质量守卫（三道硬校验+新鲜度闸+锚点约定）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 单元用例全部构造于 tmp 假仓（monkeypatch _REPO 等模块常量，零生产写）；集成用例只读真仓渲染零写盘
# [MODIFY-GUARD] 与生成器同批演进
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError / pytest.raises(SystemExit)
# [TESTS] self
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""generate_commit_guide 机生守卫——红蓝双向：红=坏引用/坏哈希必须拦，蓝=正常渲染全绿。"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

import scripts.governance.generators.generate_commit_guide as gcg

_REGISTRY_BODY = """ttl: permanent
gates:
- gate_id: A-GATE
  module_path: zephyr.gov_enforcement.commit_gates.a_gate
  factory_function: make_a
  enabled: true
- gate_id: B-GATE
  module_path: zephyr.gov_enforcement.commit_gates.b_gate
  factory_function: make_b
  enabled: true
"""

_GATE_SRC = '# [BLUEPRINT] MOD-X | bp.md\n"""a gate docstring"""\n'


def _make_tmp_repo(tmp_path: Path, digest_extra: str = "", checklist_refs: str = "A-GATE") -> Path:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a_gate.py").write_text(_GATE_SRC, encoding="utf-8")
    reg = tmp_path / "in_process_gate_registry.yaml"
    reg.write_text(_REGISTRY_BODY, encoding="utf-8")
    src_dir = tmp_path / "sources"
    src_dir.mkdir()
    digest = (
        "gates:\n"
        "- gate_id: A-GATE\n"
        "  source_file: src/a_gate.py\n"
        "  block_or_warn: block\n"
        "  trigger: t\n"
        "  enforce: e\n"
        "  exempt: none\n"
        "  fix: f\n" + digest_extra
    )
    (src_dir / "gate_digest_registry.yaml").write_text(digest, encoding="utf-8")
    checklists = (
        "universal:\n"
        "  title: u\n"
        "  steps:\n"
        "  - step one\n"
        "  gate_refs: [" + checklist_refs + "]\n"
        "file_types:\n"
        "- type_id: demo\n"
        "  title: demo type\n"
        "  match_hint: mh\n"
        "  steps:\n"
        "  - do x\n"
        "  gate_refs: [" + checklist_refs + "]\n"
        "  common_deaths:\n"
        "  - case: c1\n"
        "    gate: " + checklist_refs + "\n"
        "    prescription: p1\n"
    )
    (src_dir / "file_type_checklists_registry.yaml").write_text(checklists, encoding="utf-8")
    cases = (
        "cases:\n"
        "- case_id: CASE-1\n"
        "  symptom: s\n"
        "  gate: " + checklist_refs + "\n"
        "  root_cause: rc\n"
        "  prescription: p\n"
        "  cost_note: P50 1min\n"
    )
    (src_dir / "death_cases_registry.yaml").write_text(cases, encoding="utf-8")
    return tmp_path


def _patch_paths(monkeypatch: pytest.MonkeyPatch, root: Path) -> None:
    monkeypatch.setattr(gcg, "_REPO", root)
    monkeypatch.setattr(gcg, "_SOURCES_DIR", root / "sources")
    monkeypatch.setattr(gcg, "_REGISTRY_PATH", root / "in_process_gate_registry.yaml")
    monkeypatch.setattr(gcg, "_OUTPUT_PATH", root / "guide.md")


def test_render_happy_path_and_anchors(tmp_path, monkeypatch):
    root = _make_tmp_repo(tmp_path)
    _patch_paths(monkeypatch, root)
    text = gcm_render = gcg._render()
    assert "# 提交指路指南（机生版）" in gcm_render
    assert "### A-GATE" in gcm_render  # 锚点约定：纯 ASCII gate 标题
    assert "## FT-demo — demo type" in gcm_render
    assert "## FT-universal" in gcm_render
    assert "### CASE-CASE-1" in gcm_render
    assert "在册覆盖: 1/2" in gcm_render  # B-GATE 未蒸馏进附录
    assert "- B-GATE" in gcm_render


def test_unknown_gate_ref_hard_fails(tmp_path, monkeypatch):
    root = _make_tmp_repo(tmp_path, checklist_refs="GHOST-GATE")
    _patch_paths(monkeypatch, root)
    with pytest.raises(SystemExit) as ei:
        gcg._render()
    assert "GHOST-GATE" in str(ei.value)


def test_missing_source_file_hard_fails(tmp_path, monkeypatch):
    root = _make_tmp_repo(tmp_path)
    (root / "src" / "a_gate.py").unlink()
    _patch_paths(monkeypatch, root)
    with pytest.raises(SystemExit) as ei:
        gcg._render()
    assert "source_file 不存在" in str(ei.value)


def test_drifted_hash_shows_banner(tmp_path, monkeypatch):
    root = _make_tmp_repo(
        tmp_path,
        digest_extra="  source_sha256: " + "deadbeef" * 8 + "\n",
    )
    _patch_paths(monkeypatch, root)
    text = gcg._render()
    assert "待重蒸馏" in text
    assert "A-GATE ⚠️" in text


def test_refresh_hashes_fills_placeholder(tmp_path, monkeypatch):
    root = _make_tmp_repo(
        tmp_path,
        digest_extra="  source_sha256: pending-refresh\n",
    )
    _patch_paths(monkeypatch, root)
    patched = gcg._refresh_hashes(root / "sources" / "gate_digest_registry.yaml")
    assert patched == 1
    data = yaml.safe_load((root / "sources" / "gate_digest_registry.yaml").read_text(encoding="utf-8"))
    h = data["gates"][0]["source_sha256"]
    assert re.fullmatch(r"[0-9a-f]{64}", h)
    assert h == gcg._sha256_of(root / "src" / "a_gate.py")


def test_cost_sort_numeric_not_lexicographic(tmp_path, monkeypatch):
    """红队 F2：死因速查按 P50 分钟数值降序，非字符串字典序。"""
    root = _make_tmp_repo(tmp_path)
    src_dir = root / "sources"
    lines = ["cases:"]
    for cid, note in (("CASE-CHEAP", "P50 4.1min/封"), ("CASE-EXPENSIVE", "P50 182.8min/封（最贵档）")):
        lines += [
            "- case_id: " + cid,
            "  symptom: s",
            "  gate: A-GATE",
            "  root_cause: rc",
            "  prescription: p",
            '  cost_note: "' + note + '"',
        ]
    (src_dir / "death_cases_registry.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    _patch_paths(monkeypatch, root)
    text = gcg._render()
    cheap = text.index("CASE-CHEAP")
    expensive = text.index("CASE-EXPENSIVE")
    assert expensive < cheap  # 贵的排前


def test_integration_real_repo_render_readonly():
    """真仓集成（只读）：真实四源可渲染、99 台覆盖、锚点约定成立。"""
    text = gcg._render()
    # 覆盖=在册∩蒸馏 台数随名册成长动态变（99→102+），蒸馏数=当期 digest 全量
    import re as _re

    m = _re.search(r"在册覆盖: (\d+)/(\d+)", text)
    assert m and m.group(1) == m.group(2)  # 不变量=在册全覆盖（台数随名册成长动态）
    assert "### CREATE-GUARD" in text
    assert "### ORPHAN-MODULE" in text
    # 漂移台数允许动态（判据源随他班演进），横幅机制本身必须在场
    assert _re.search(r"漂移待重蒸馏: \d+ 台", text)
