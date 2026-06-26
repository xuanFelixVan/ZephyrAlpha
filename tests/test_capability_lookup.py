# [A_test] module_id=MOD-GOV_capability_lookup_test | suite=capability_lookup | scope=unit | safety=L | ai_autonomy=ai_modifiable

"""
test_capability_lookup — CapabilityLookup 反查注册表查询 API 测试。

覆盖：
  - find / get / list_duplicates / list_ssot_conflicts / check_file_canonical
  - _parse_header（代码头部提取）
  - pending_candidates 发现（同 module_id / 同 module_path）
  - canonical_alive 检测（磁盘文件缺失）
  - YAML 缺失报错
  - --no-scan 模式
  - reload
"""

from __future__ import annotations

from pathlib import Path

import pytest

from zephyr.governance.capability_lookup import (
    CapabilityEntry,
    CapabilityLookup,
    HeaderInfo,
    _normalize_path,
)


# ---------------------------------------------------------------------------
# 测试夹具
# ---------------------------------------------------------------------------

SAMPLE_YAML = """
schema_version: "1.0.0"
capabilities:
  - capability_id: test_cap
    name: "Test Capability"
    canonical_file: src/zephyr/test/canonical.py
    module_id: MOD-TEST_canonical
    blueprint_id: MOD-TEST
    domain: D-TEST
    maturity: production
    status: alive
    aliases:
      - test
      - 测试
    description: "A test capability"
    duplicates:
      - path: src/zephyr/test/duplicate.py
        module_id: MOD-TEST_duplicate
        blueprint_id: MOD-TEST
        domain: D-TEST
        maturity: prototype
        relation: conflicting
        note: "conflict"
    removed_duplicates:
      - path: src/zephyr/test/removed.py
        removed_in_commit: abc123
        note: "removed"
"""


def _make_py_file(
    path: Path,
    module_path: str,
    module_id: str,
    blueprint: str = "",
    domain: str = "",
    maturity: str = "",
    docstring: str = "Docstring first line.",
) -> None:
    """生成带十一字段头部的 .py 测试文件。"""
    header_lines = [f"# [MODULE] {module_path}"]
    if blueprint:
        header_lines.append(f"# [BLUEPRINT] {blueprint} | docs/x.md")
    if domain:
        header_lines.append(f"# [DOMAIN] {domain}")
    if maturity:
        header_lines.append(f"# [MATURITY] {maturity}")
    header_lines.append(f"# [A_module] module_id={module_id} | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable")
    header_lines.append("")
    header_lines.append(f'"""{docstring}"""')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(header_lines) + "\n", encoding="utf-8")


@pytest.fixture
def setup_registry(tmp_path: Path):
    """构造临时 YAML + 临时 scan_root（含 canonical + duplicate 文件）。"""
    yaml_path = tmp_path / "registry.yaml"
    yaml_path.write_text(SAMPLE_YAML, encoding="utf-8")
    scan_root = tmp_path / "src" / "zephyr"
    scan_root.mkdir(parents=True, exist_ok=True)
    test_dir = scan_root / "test"
    test_dir.mkdir()
    _make_py_file(
        test_dir / "canonical.py",
        "zephyr.test.canonical",
        "MOD-TEST_canonical",
        blueprint="MOD-TEST",
        domain="D-TEST",
        maturity="production",
    )
    _make_py_file(
        test_dir / "duplicate.py",
        "zephyr.test.duplicate",
        "MOD-TEST_duplicate",
        blueprint="MOD-TEST",
        domain="D-TEST",
        maturity="prototype",
    )
    return yaml_path, scan_root


# ---------------------------------------------------------------------------
# find / get 测试
# ---------------------------------------------------------------------------

def test_find_by_keyword(setup_registry):
    yaml_path, scan_root = setup_registry
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    results = reg.find("test")
    assert len(results) == 1
    assert results[0]["capability_id"] == "test_cap"


def test_find_by_alias_chinese(setup_registry):
    yaml_path, scan_root = setup_registry
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    results = reg.find("测试")
    assert len(results) == 1


def test_find_by_canonical_file(setup_registry):
    yaml_path, scan_root = setup_registry
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    results = reg.find("canonical.py")
    assert len(results) == 1


def test_find_no_match(setup_registry):
    yaml_path, scan_root = setup_registry
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    assert reg.find("nonexistent_xyz") == []


def test_get_existing(setup_registry):
    yaml_path, scan_root = setup_registry
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    r = reg.get("test_cap")
    assert r is not None
    assert r["canonical_file"] == "src/zephyr/test/canonical.py"
    assert r["module_id"] == "MOD-TEST_canonical"


def test_get_not_found(setup_registry):
    yaml_path, scan_root = setup_registry
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    assert reg.get("nonexistent") is None


# ---------------------------------------------------------------------------
# list_duplicates / list_ssot_conflicts 测试
# ---------------------------------------------------------------------------

def test_list_duplicates(setup_registry):
    yaml_path, scan_root = setup_registry
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    dups = reg.list_duplicates()
    assert len(dups) == 1
    assert dups[0]["capability_id"] == "test_cap"
    assert len(dups[0]["duplicates"]) == 1


def test_list_ssot_conflicts(setup_registry):
    yaml_path, scan_root = setup_registry
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    conflicts = reg.list_ssot_conflicts()
    assert len(conflicts) == 1
    assert conflicts[0]["capability_id"] == "test_cap"
    assert conflicts[0]["blueprint_id"] == "MOD-TEST"
    assert len(conflicts[0]["conflicts"]) == 1


def test_list_ssot_conflicts_excludes_sibling(tmp_path: Path):
    """relation=sibling 不算 SSoT 冲突。"""
    yaml_path = tmp_path / "registry.yaml"
    yaml_path.write_text("""
capabilities:
  - capability_id: cap_with_sibling
    name: "Has Sibling"
    canonical_file: src/zephyr/c.py
    duplicates:
      - path: src/zephyr/d.py
        relation: sibling
""", encoding="utf-8")
    scan_root = tmp_path / "src" / "zephyr"
    scan_root.mkdir(parents=True)
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    assert reg.list_ssot_conflicts() == []


# ---------------------------------------------------------------------------
# check_file_canonical 测试
# ---------------------------------------------------------------------------

def test_check_file_canonical_canonical(setup_registry):
    yaml_path, scan_root = setup_registry
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    r = reg.check_file_canonical("src/zephyr/test/canonical.py")
    assert r is not None
    assert r["is_canonical"] is True
    assert r["capability_id"] == "test_cap"


def test_check_file_canonical_duplicate(setup_registry):
    yaml_path, scan_root = setup_registry
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    r = reg.check_file_canonical("src/zephyr/test/duplicate.py")
    assert r is not None
    assert r["is_canonical"] is False
    assert r["relation"] == "conflicting"


def test_check_file_canonical_backslash_path(setup_registry):
    """Windows 反斜杠路径要能匹配正斜杠声明。"""
    yaml_path, scan_root = setup_registry
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    r = reg.check_file_canonical("src\\zephyr\\test\\canonical.py")
    assert r is not None
    assert r["is_canonical"] is True


def test_check_file_canonical_not_in_registry(setup_registry):
    yaml_path, scan_root = setup_registry
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    assert reg.check_file_canonical("src/zephyr/nonexistent.py") is None


# ---------------------------------------------------------------------------
# summary / canonical_alive 测试
# ---------------------------------------------------------------------------

def test_summary(setup_registry):
    yaml_path, scan_root = setup_registry
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    s = reg.summary()
    assert s["total_declared"] == 1
    assert s["alive"] == 1
    assert s["dead"] == 0
    assert s["with_duplicates"] == 1
    assert s["ssot_conflicts"] == 1


def test_canonical_dead_when_file_missing(tmp_path: Path):
    """YAML 声明 canonical 但磁盘无文件 → dead。"""
    yaml_path = tmp_path / "registry.yaml"
    yaml_path.write_text("""
capabilities:
  - capability_id: dead_cap
    name: "Dead"
    canonical_file: src/zephyr/dead.py
    module_id: MOD-DEAD
""", encoding="utf-8")
    scan_root = tmp_path / "src" / "zephyr"
    scan_root.mkdir(parents=True)
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    s = reg.summary()
    assert s["dead"] == 1
    assert s["alive"] == 0


# ---------------------------------------------------------------------------
# _parse_header 测试
# ---------------------------------------------------------------------------

def test_parse_header_full(tmp_path: Path):
    py = tmp_path / "mod.py"
    py.write_text(
        "# [BLUEPRINT] MOD-TEST | docs/x.md | §1\n"
        "# [MODULE] zephyr.test.mod\n"
        "# [DOMAIN] D-TEST\n"
        "# [MATURITY] production\n"
        "# [A_module] module_id=MOD-TEST_mod | layer=module | stability=evolving\n"
        "\n"
        '"""First docstring line."""\n'
        "pass\n",
        encoding="utf-8",
    )
    info = CapabilityLookup._parse_header(py, "mod.py")
    assert info.module_path == "zephyr.test.mod"
    assert info.module_id == "MOD-TEST_mod"
    assert info.blueprint_id == "MOD-TEST"
    assert info.domain == "D-TEST"
    assert info.maturity == "production"
    assert info.docstring == "First docstring line."


def test_parse_header_missing_fields(tmp_path: Path):
    """只有 [MODULE] 的文件也应被收录（有头部声明的下限）。"""
    py = tmp_path / "mod.py"
    py.write_text(
        "# [MODULE] zephyr.minimal\n"
        "pass\n",
        encoding="utf-8",
    )
    info = CapabilityLookup._parse_header(py, "mod.py")
    assert info.module_path == "zephyr.minimal"
    assert info.module_id == ""
    assert info.blueprint_id == ""


def test_parse_header_multiline_docstring(tmp_path: Path):
    py = tmp_path / "mod.py"
    py.write_text(
        "# [MODULE] zephyr.test\n"
        '"""\n'
        "First line of multi-line docstring.\n"
        "Second line.\n"
        '"""\n'
        "pass\n",
        encoding="utf-8",
    )
    info = CapabilityLookup._parse_header(py, "mod.py")
    assert info.docstring == "First line of multi-line docstring."


def test_parse_header_no_header(tmp_path: Path):
    """无头部声明的文件不被收录（_scan_disk_headers 过滤）。"""
    py = tmp_path / "mod.py"
    py.write_text("print('hello')\n", encoding="utf-8")
    info = CapabilityLookup._parse_header(py, "mod.py")
    assert info.module_path == ""
    assert info.module_id == ""


# ---------------------------------------------------------------------------
# pending_candidates 测试
# ---------------------------------------------------------------------------

def test_pending_candidates_same_module_path(tmp_path: Path):
    """磁盘上有文件声明与 canonical 相同 module_path，但 YAML 未声明 → pending。"""
    yaml_path = tmp_path / "registry.yaml"
    yaml_path.write_text("""
capabilities:
  - capability_id: test_cap
    name: "Test"
    canonical_file: src/zephyr/canonical.py
    module_id: MOD-TEST_canonical
""", encoding="utf-8")
    scan_root = tmp_path / "src" / "zephyr"
    scan_root.mkdir(parents=True)
    _make_py_file(scan_root / "canonical.py", "zephyr.canonical", "MOD-TEST_canonical")
    _make_py_file(scan_root / "shadow.py", "zephyr.canonical", "MOD-TEST_shadow")
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    cap = reg.get("test_cap")
    assert len(cap["pending_candidates"]) == 1
    assert cap["pending_candidates"][0]["path"] == "src/zephyr/shadow.py"
    assert "same module_path" in cap["pending_candidates"][0]["match_reason"]


def test_pending_candidates_same_module_id(tmp_path: Path):
    """磁盘上有文件声明与 canonical 相同 module_id，但 YAML 未声明 → pending。"""
    yaml_path = tmp_path / "registry.yaml"
    yaml_path.write_text("""
capabilities:
  - capability_id: test_cap
    name: "Test"
    canonical_file: src/zephyr/canonical.py
    module_id: MOD-TEST_canonical
""", encoding="utf-8")
    scan_root = tmp_path / "src" / "zephyr"
    scan_root.mkdir(parents=True)
    _make_py_file(scan_root / "canonical.py", "zephyr.canonical", "MOD-TEST_canonical")
    _make_py_file(scan_root / "other.py", "zephyr.other", "MOD-TEST_canonical")
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    cap = reg.get("test_cap")
    assert len(cap["pending_candidates"]) == 1
    assert "same module_id" in cap["pending_candidates"][0]["match_reason"]


def test_pending_candidates_excludes_declared(tmp_path: Path):
    """duplicates[] 已声明的文件不算 pending。"""
    yaml_path = tmp_path / "registry.yaml"
    yaml_path.write_text("""
capabilities:
  - capability_id: test_cap
    name: "Test"
    canonical_file: src/zephyr/canonical.py
    module_id: MOD-TEST_canonical
    duplicates:
      - path: src/zephyr/declared.py
        module_id: MOD-TEST_canonical
        relation: conflicting
""", encoding="utf-8")
    scan_root = tmp_path / "src" / "zephyr"
    scan_root.mkdir(parents=True)
    _make_py_file(scan_root / "canonical.py", "zephyr.canonical", "MOD-TEST_canonical")
    _make_py_file(scan_root / "declared.py", "zephyr.declared", "MOD-TEST_canonical")
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    cap = reg.get("test_cap")
    assert cap["pending_candidates"] == []


# ---------------------------------------------------------------------------
# 边界 / 错误处理测试
# ---------------------------------------------------------------------------

def test_yaml_missing_raises(tmp_path: Path):
    scan_root = tmp_path / "src" / "zephyr"
    scan_root.mkdir(parents=True)
    with pytest.raises(FileNotFoundError):
        CapabilityLookup(yaml_path=tmp_path / "nonexistent.yaml", scan_root=scan_root)


def test_no_scan_mode(setup_registry):
    """scan=False 时不扫盘，canonical_alive 默认 True（未 reconcile）。"""
    yaml_path, scan_root = setup_registry
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root, scan=False)
    assert len(reg.list_all()) == 1
    # 不扫描时 pending_candidates 为空
    cap = reg.get("test_cap")
    assert cap["pending_candidates"] == []


def test_reload(setup_registry):
    yaml_path, scan_root = setup_registry
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    assert len(reg.list_all()) == 1
    # 修改 YAML 加一条
    yaml_path.write_text(SAMPLE_YAML + """
  - capability_id: second_cap
    name: "Second"
    canonical_file: src/zephyr/test/canonical.py
""", encoding="utf-8")
    reg.reload()
    assert len(reg.list_all()) == 2


def test_normalize_path():
    assert _normalize_path("src\\zephyr\\test.py") == "src/zephyr/test.py"
    assert _normalize_path("./src/test.py") == "src/test.py"
    assert _normalize_path("src/test.py") == "src/test.py"


def test_empty_yaml(tmp_path: Path):
    """空 YAML（无 capabilities 键）应返回空列表，不报错。"""
    yaml_path = tmp_path / "registry.yaml"
    yaml_path.write_text("schema_version: '1.0.0'\n", encoding="utf-8")
    scan_root = tmp_path / "src" / "zephyr"
    scan_root.mkdir(parents=True)
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    assert reg.list_all() == []
    assert reg.summary()["total_declared"] == 0


# ---------------------------------------------------------------------------
# 真实项目注册表集成测试（确保种子条目可加载）
# ---------------------------------------------------------------------------

def test_real_registry_loads():
    """集成测试：真实项目 YAML 能加载，且包含 2 个种子条目。

    用 --no-scan 避免扫全项目拖慢测试。
    """
    reg = CapabilityLookup(scan=False)
    caps = reg.list_all()
    cap_ids = {c["capability_id"] for c in caps}
    assert "session_handoff_continuity" in cap_ids
    assert "rollback_executor" in cap_ids


def test_real_registry_has_ssot_conflict():
    """集成测试：真实注册表应有 rollback_executor 的 SSoT 冲突。"""
    reg = CapabilityLookup(scan=False)
    conflicts = reg.list_ssot_conflicts()
    cap_ids = {c["capability_id"] for c in conflicts}
    assert "rollback_executor" in cap_ids
