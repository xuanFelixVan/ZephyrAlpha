# [BLUEPRINT] MOD-INF-018 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_test] module_id=MOD-GOV_capability_lookup_test | suite=capability_lookup | scope=unit | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""
test_capability_lookup — CapabilityLookup 反查注册表查询 API + 派生逻辑测试。

覆盖：
  - find / get / list_duplicates / list_ssot_conflicts / check_file_canonical
  - canonical 派生（单候选 / 多候选成熟度排序 / canonical_override / 歧义）
  - duplicates 派生（relation 由 blueprint 比对派生：conflicting / sibling）
  - duplicates_manual 合并（auto 漏掉的语义 sibling）
  - removed_duplicates git log 派生（mock subprocess）+ manual 追加
  - _parse_header / _parse_header_from_text（代码头部 + git show 文本）
  - pending_candidates 发现（同 module_id / 同 module_path）
  - canonical_alive 检测（磁盘文件缺失）
  - YAML 缺失报错 / --no-scan 模式 / reload
"""

from __future__ import annotations

from pathlib import Path

import pytest

from zephyr.governance.capability_lookup import (
    CapabilityDuplicate,
    CapabilityEntry,
    CapabilityLookup,
    HeaderInfo,
    _normalize_path,
)

# ---------------------------------------------------------------------------
# 测试夹具
# ---------------------------------------------------------------------------

# Slim YAML（v1.1.0 格式）：只声明 capability_id / aliases / description
SAMPLE_YAML = """
schema_version: "1.1.0"
capabilities:
  - capability_id: test_cap
    aliases:
      - canonical
      - 测试
    description: "A test capability"
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
    """生成带十五字段头部的 .py 测试文件。"""
    header_lines = [f"# [MODULE] {module_path}"]
    if blueprint:
        header_lines.append(f"# [BLUEPRINT] {blueprint} | docs/x.md")
    if domain:
        header_lines.append(f"# [DOMAIN] {domain}")
    if maturity:
        header_lines.append(f"# [MATURITY] {maturity}")
    header_lines.append(
        f"# [A_module] module_id={module_id} | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable"
    )
    header_lines.append("")
    header_lines.append(f'"""{docstring}"""')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(header_lines) + "\n", encoding="utf-8")


@pytest.fixture
def setup_registry(tmp_path: Path):
    """构造临时 YAML + 临时 scan_root（canonical + 同 basename 重复）。

    canonical = src/zephyr/test/canonical.py (production)
    duplicate = src/zephyr/shadow/canonical.py (design, 同蓝图 MOD-TEST → conflicting)
    两者 basename 都是 canonical，匹配 alias → auto 派生。
    """
    yaml_path = tmp_path / "registry.yaml"
    yaml_path.write_text(SAMPLE_YAML, encoding="utf-8")
    scan_root = tmp_path / "src" / "zephyr"
    scan_root.mkdir(parents=True, exist_ok=True)
    # canonical（production）
    _make_py_file(
        scan_root / "test" / "canonical.py",
        "zephyr.test.canonical",
        "MOD-TEST_canonical",
        blueprint="MOD-TEST",
        domain="D-TEST",
        maturity="production",
    )
    # 同 basename 重复（design，同蓝图 → conflicting）
    _make_py_file(
        scan_root / "shadow" / "canonical.py",
        "zephyr.shadow.canonical",
        "MOD-TEST_duplicate",
        blueprint="MOD-TEST",
        domain="D-TEST",
        maturity="design",
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
    """find 能匹配派生的 canonical_file 路径。"""
    yaml_path, scan_root = setup_registry
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    results = reg.find("canonical.py")
    assert len(results) == 1


def test_find_no_match(setup_registry):
    yaml_path, scan_root = setup_registry
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    assert reg.find("nonexistent_xyz") == []


def test_find_chinese_token_match(tmp_path: Path):
    """token 包含匹配治本验证：中文变体不在 aliases 中也能命中（core 在 description 中）。

    场景对标 project_root_resolution：alias 保留"仓库根"，description 含"仓库根目录"，
    查询变体"仓库根路径"（已删 alias）经 core"仓库根"公共子串命中——不再靠堆 alias。
    """
    yaml_path = tmp_path / "registry.yaml"
    yaml_path.write_text(
        """
schema_version: "1.1.0"
capabilities:
  - capability_id: repo_root_resolver
    aliases:
      - 仓库根
      - REPO_ROOT
    description: "仓库根目录的权威解析入口"
""",
        encoding="utf-8",
    )
    scan_root = tmp_path / "src" / "zephyr"
    scan_root.mkdir(parents=True)
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    # 变体"仓库根路径"不在 aliases，但 core"仓库根"在 description/alias → token 命中
    results = reg.find("仓库根路径")
    assert len(results) == 1
    assert results[0]["capability_id"] == "repo_root_resolver"
    # 原 alias 仍命中（精确子串）
    assert len(reg.find("仓库根")) == 1
    assert len(reg.find("REPO_ROOT")) == 1
    # core 不在 haystack 的查询不命中（避免误匹配）
    assert reg.find("完全无关的词") == []


def test_find_ascii_multi_word(setup_registry):
    """ASCII 多词短语查询：按空白分词后 AND 匹配（无需连续出现）。

    回归 bug：'test canonical' 两词分别落在不同字段（capability_id 含 'test'，
    canonical_file/alias 含 'canonical'），子串匹配因不连续返回空；
    token AND 匹配应命中。对标 find("session handoff") 原失效场景。
    """
    yaml_path, scan_root = setup_registry
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    results = reg.find("test canonical")
    assert len(results) == 1
    assert results[0]["capability_id"] == "test_cap"
    # 单词行为不退化（守卫：保留原子串匹配语义）
    assert len(reg.find("test")) == 1
    assert len(reg.find("canonical")) == 1
    # 含未命中词的多词查询不误命中
    assert reg.find("test nonexistent_xyz") == []


def test_find_degenerate_query_guard():
    """退化查询守卫：空/空白/单字符查询返回 []，不返回宽泛命中。

    回归 bug：find('') 返回全部（'' in haystack 恒 True），find('a')/find('的')
    返回 16/11 条（单字符作为子串出现在所有 description）。守卫 len(q.strip())>=2 拦截。
    对标红蓝对抗发现 2（单字符过宽匹配绕过守卫）——治本：在 find() 入口拦截退化输入。
    """
    reg = CapabilityLookup(scan=False)
    # 空查询（旧版返回全部：'' in haystack 恒 True）
    assert reg.find("") == []
    # 纯空白（旧版 '   '.lower()='   ' in haystack 多数为 True）
    assert reg.find("   ") == []
    assert reg.find("\t\n") == []
    # 单 ASCII 字符（旧版 'a' 返回 16：a 作为子串出现在所有 capability_id/canonical_file）
    assert reg.find("a") == []
    assert reg.find("e") == []
    # 单 CJK 字符（旧版 '的' 返回 11：的 作为子串出现在所有 description）
    assert reg.find("的") == []
    assert reg.find("了") == []
    # 2 字符查询不被守卫拦（有意义的最小查询长度）
    # find('ab') 不一定命中，但守卫不应返回空（除非确实无匹配）
    reg.find("ab")  # 不 assert 返回值，只验证不崩溃且不被守卫误拦


def test_find_adversarial_vectors():
    """红蓝对抗向量永久回归：极端输入不崩溃 + 正向查询不退化。

    覆盖：正则元字符/SQL注入样式/超长DoS/换行制表符/大小写/空白/Unicode/负向。
    守护 find() 在极端输入下的健壮性，防未来改动静默回归。
    """
    reg = CapabilityLookup(scan=False)
    # 正则元字符不崩溃（find 用 `in` 非 re，元字符当字面量处理）
    for q in [".*", "[]()", "$^", "\\d+", "'; DROP TABLE--;"]:
        results = reg.find(q)
        assert isinstance(results, list), f"crash on {q!r}"
    # 超长查询不 DoS（应在 1s 内返回，实际 <10ms）
    import time

    t0 = time.time()
    reg.find("vocabulary " * 2000)
    assert time.time() - t0 < 1.0, "20k 字符查询超 1s（DoS 风险）"
    # 换行/制表符分词正常（\W+ 切分，token AND 匹配）
    ids = {r["capability_id"] for r in reg.find("vocabulary\nloader\t")}
    assert "vocabulary_values_loader" in ids
    # 大小写不敏感（全大写/混合/带空白）
    for q in ["SESSION HANDOFF", "Session Handoff", "  session handoff  "]:
        ids = {r["capability_id"] for r in reg.find(q)}
        assert "session_handoff_continuity" in ids, f"failed for {q!r}: {ids}"
    # 制表符/多空格分隔（\W+ 统一切分）
    assert "session_handoff_continuity" in {r["capability_id"] for r in reg.find("session\thandoff")}
    assert "session_handoff_continuity" in {r["capability_id"] for r in reg.find("session   handoff")}
    # 负向：完全无关查询返回空（不误命中）
    assert reg.find("完全无关的查询xyz123") == []


def test_get_existing(setup_registry):
    """get 返回派生的 canonical_file + 从头部派生的 module_id。"""
    yaml_path, scan_root = setup_registry
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    r = reg.get("test_cap")
    assert r is not None
    # canonical 派生：production > design → test/canonical.py 胜出
    assert r["canonical_file"] == "src/zephyr/test/canonical.py"
    assert r["module_id"] == "MOD-TEST_canonical"
    assert r["maturity"] == "production"
    assert r["derivation_note"].startswith("derived from 2 candidates")


def test_get_not_found(setup_registry):
    yaml_path, scan_root = setup_registry
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    assert reg.get("nonexistent") is None


# ---------------------------------------------------------------------------
# canonical 派生测试（v1.1.0 新增）
# ---------------------------------------------------------------------------


def test_canonical_single_candidate(tmp_path: Path):
    """单候选 → auto canonical（无需成熟度排序）。"""
    yaml_path = tmp_path / "registry.yaml"
    yaml_path.write_text(
        """
capabilities:
  - capability_id: solo_cap
    aliases: [solo]
    description: "solo"
""",
        encoding="utf-8",
    )
    scan_root = tmp_path / "src" / "zephyr"
    scan_root.mkdir(parents=True)
    _make_py_file(
        scan_root / "m" / "solo.py",
        "zephyr.m.solo",
        "MOD-SOLO",
        blueprint="MOD-SOLO",
        domain="D-SOLO",
        maturity="design",
    )
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    cap = reg.get("solo_cap")
    assert cap["canonical_file"] == "src/zephyr/m/solo.py"
    assert "single candidate" in cap["derivation_note"]


def test_canonical_multiple_maturity_sort(setup_registry):
    """多候选 → 成熟度排序（production > design）。"""
    yaml_path, scan_root = setup_registry
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    cap = reg.get("test_cap")
    assert cap["canonical_file"] == "src/zephyr/test/canonical.py"  # production
    assert cap["maturity"] == "production"
    # 重复是 design 版
    assert len(cap["duplicates"]) == 1
    assert cap["duplicates"][0]["path"] == "src/zephyr/shadow/canonical.py"
    assert cap["duplicates"][0]["maturity"] == "design"


def test_canonical_override(tmp_path: Path):
    """canonical_override 覆盖派生（强制选 design 版）。"""
    yaml_path = tmp_path / "registry.yaml"
    yaml_path.write_text(
        """
capabilities:
  - capability_id: override_cap
    aliases: [picker]
    description: "override test"
    canonical_override: src/zephyr/proto/picker.py
""",
        encoding="utf-8",
    )
    scan_root = tmp_path / "src" / "zephyr"
    scan_root.mkdir(parents=True)
    # production 版（默认会被选中，但 override 强制选 design 版）
    _make_py_file(
        scan_root / "prod" / "picker.py",
        "zephyr.prod.picker",
        "MOD-PICKER_prod",
        blueprint="MOD-PICKER",
        domain="D-PICKER",
        maturity="production",
    )
    # design 版（override 指定）
    _make_py_file(
        scan_root / "proto" / "picker.py",
        "zephyr.proto.picker",
        "MOD-PICKER_proto",
        blueprint="MOD-PICKER",
        domain="D-PICKER",
        maturity="design",
    )
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    cap = reg.get("override_cap")
    assert cap["canonical_file"] == "src/zephyr/proto/picker.py"
    assert cap["maturity"] == "design"
    assert "canonical_override" in cap["derivation_note"]
    # production 版降为 duplicate
    assert len(cap["duplicates"]) == 1
    assert cap["duplicates"][0]["path"] == "src/zephyr/prod/picker.py"


def test_canonical_ambiguous_when_tied(tmp_path: Path):
    """两候选成熟度+import 数都打平 → AMBIGUOUS 标记。"""
    yaml_path = tmp_path / "registry.yaml"
    yaml_path.write_text(
        """
capabilities:
  - capability_id: tied_cap
    aliases: [tied]
    description: "tied"
""",
        encoding="utf-8",
    )
    scan_root = tmp_path / "src" / "zephyr"
    scan_root.mkdir(parents=True)
    # 两个 design 候选（成熟度相同，无 import → 打平）
    _make_py_file(
        scan_root / "a" / "tied.py",
        "zephyr.a.tied",
        "MOD-TIED_a",
        blueprint="MOD-TIED",
        domain="D-TIED",
        maturity="design",
    )
    _make_py_file(
        scan_root / "b" / "tied.py",
        "zephyr.b.tied",
        "MOD-TIED_b",
        blueprint="MOD-TIED",
        domain="D-TIED",
        maturity="design",
    )
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    cap = reg.get("tied_cap")
    assert "AMBIGUOUS" in cap["derivation_note"]
    # 路径字典序 tiebreak：a/ < b/
    assert cap["canonical_file"] == "src/zephyr/a/tied.py"


def test_duplicate_relation_conflicting(setup_registry):
    """同蓝图 → relation=conflicting。"""
    yaml_path, scan_root = setup_registry
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    cap = reg.get("test_cap")
    assert cap["duplicates"][0]["relation"] == "conflicting"


def test_duplicate_relation_sibling(tmp_path: Path):
    """异蓝图 → relation=sibling。"""
    yaml_path = tmp_path / "registry.yaml"
    yaml_path.write_text(
        """
capabilities:
  - capability_id: sib_cap
    aliases: [shared_name]
    description: "sibling test"
""",
        encoding="utf-8",
    )
    scan_root = tmp_path / "src" / "zephyr"
    scan_root.mkdir(parents=True)
    _make_py_file(
        scan_root / "a" / "shared_name.py",
        "zephyr.a.shared_name",
        "MOD-A",
        blueprint="MOD-A",
        domain="D-A",
        maturity="production",
    )
    _make_py_file(
        scan_root / "b" / "shared_name.py",
        "zephyr.b.shared_name",
        "MOD-B",
        blueprint="MOD-B",
        domain="D-B",
        maturity="design",
    )
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    cap = reg.get("sib_cap")
    assert cap["duplicates"][0]["relation"] == "sibling"


def test_duplicates_manual_merged(tmp_path: Path):
    """duplicates_manual（语义 sibling）合并到 duplicates[]。"""
    yaml_path = tmp_path / "registry.yaml"
    yaml_path.write_text(
        """
capabilities:
  - capability_id: manual_cap
    aliases: [main]
    description: "manual dup test"
    duplicates_manual:
      - path: src/zephyr/sibling/manager.py
        relation: sibling
        note: "语义 sibling，basename 不匹配，auto 派生漏掉"
""",
        encoding="utf-8",
    )
    scan_root = tmp_path / "src" / "zephyr"
    scan_root.mkdir(parents=True)
    _make_py_file(
        scan_root / "core" / "main.py",
        "zephyr.core.main",
        "MOD-MAIN",
        blueprint="MOD-MAIN",
        domain="D-MAIN",
        maturity="production",
    )
    _make_py_file(
        scan_root / "sibling" / "manager.py",
        "zephyr.sibling.manager",
        "MOD-MGR",
        blueprint="MOD-MGR",
        domain="D-MGR",
        maturity="production",
    )
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    cap = reg.get("manual_cap")
    # auto canonical = main.py
    assert cap["canonical_file"] == "src/zephyr/core/main.py"
    # manual sibling 合并进来（basename manager 不匹配 alias main，auto 派生不会发现）
    paths = [d["path"] for d in cap["duplicates"]]
    assert "src/zephyr/sibling/manager.py" in paths
    # relation 来自 manual 声明
    manual_dup = [d for d in cap["duplicates"] if d["path"] == "src/zephyr/sibling/manager.py"][0]
    assert manual_dup["relation"] == "sibling"


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
    yaml_path.write_text(
        """
capabilities:
  - capability_id: cap_with_sibling
    aliases: [main_only]
    description: "has sibling"
    duplicates_manual:
      - path: src/zephyr/d.py
        relation: sibling
""",
        encoding="utf-8",
    )
    scan_root = tmp_path / "src" / "zephyr"
    scan_root.mkdir(parents=True)
    _make_py_file(
        scan_root / "c.py",
        "zephyr.c",
        "MOD-C",
        blueprint="MOD-C",
        domain="D-C",
        maturity="production",
    )
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
    r = reg.check_file_canonical("src/zephyr/shadow/canonical.py")
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
    """无候选（磁盘无匹配文件）→ canonical_alive=False, status=dead。"""
    yaml_path = tmp_path / "registry.yaml"
    yaml_path.write_text(
        """
capabilities:
  - capability_id: dead_cap
    aliases: [dead_alias]
    description: "Dead"
""",
        encoding="utf-8",
    )
    scan_root = tmp_path / "src" / "zephyr"
    scan_root.mkdir(parents=True)
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    s = reg.summary()
    assert s["dead"] == 1
    assert s["alive"] == 0
    cap = reg.get("dead_cap")
    assert cap["canonical_alive"] is False
    assert cap["status"] == "dead"
    assert cap["canonical_file"] == ""


# ---------------------------------------------------------------------------
# _parse_header / _parse_header_from_text 测试
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
    info = CapabilityLookup.parse_header(py, "mod.py")
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
        "# [MODULE] zephyr.minimal\npass\n",
        encoding="utf-8",
    )
    info = CapabilityLookup.parse_header(py, "mod.py")
    assert info.module_path == "zephyr.minimal"
    assert info.module_id == ""
    assert info.blueprint_id == ""


def test_parse_header_multiline_docstring(tmp_path: Path):
    py = tmp_path / "mod.py"
    py.write_text(
        '# [MODULE] zephyr.test\n"""\nFirst line of multi-line docstring.\nSecond line.\n"""\npass\n',
        encoding="utf-8",
    )
    info = CapabilityLookup.parse_header(py, "mod.py")
    assert info.docstring == "First line of multi-line docstring."


def test_parse_header_no_header(tmp_path: Path):
    """无头部声明的文件不被收录（scan_disk_headers 过滤）。"""
    py = tmp_path / "mod.py"
    py.write_text("print('hello')\n", encoding="utf-8")
    info = CapabilityLookup.parse_header(py, "mod.py")
    assert info.module_path == ""
    assert info.module_id == ""


def test_parse_header_from_text_string_input():
    """_parse_header_from_text 直接接受字符串（供 git show 输出复用）。"""
    text = "# [MODULE] zephyr.old.ghost\n# [BLUEPRINT] MOD-OLD\n# [A_module] module_id=MOD-OLD_ghost\npass\n"
    info = CapabilityLookup.parse_header_from_text(text, "src/zephyr/old/ghost.py")
    assert info.module_path == "zephyr.old.ghost"
    assert info.module_id == "MOD-OLD_ghost"
    assert info.blueprint_id == "MOD-OLD"


# ---------------------------------------------------------------------------
# pending_candidates 测试
# ---------------------------------------------------------------------------


def test_pending_candidates_same_module_path(tmp_path: Path):
    """磁盘上有文件声明与 canonical 相同 module_path，但不在派生结果里 → pending。"""
    yaml_path = tmp_path / "registry.yaml"
    yaml_path.write_text(
        """
capabilities:
  - capability_id: test_cap
    aliases: [canonical]
    description: "Test"
""",
        encoding="utf-8",
    )
    scan_root = tmp_path / "src" / "zephyr"
    scan_root.mkdir(parents=True)
    _make_py_file(scan_root / "canonical.py", "zephyr.canonical", "MOD-TEST_canonical")
    # shadow 声明相同 module_path（但 basename 不同，不在 candidates 里）
    _make_py_file(scan_root / "shadow.py", "zephyr.canonical", "MOD-TEST_shadow")
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    cap = reg.get("test_cap")
    assert len(cap["pending_candidates"]) == 1
    assert cap["pending_candidates"][0]["path"] == "src/zephyr/shadow.py"
    assert "same module_path" in cap["pending_candidates"][0]["match_reason"]


def test_pending_candidates_same_module_id(tmp_path: Path):
    """磁盘上有文件声明与 canonical 相同 module_id，但不在派生结果里 → pending。"""
    yaml_path = tmp_path / "registry.yaml"
    yaml_path.write_text(
        """
capabilities:
  - capability_id: test_cap
    aliases: [canonical]
    description: "Test"
""",
        encoding="utf-8",
    )
    scan_root = tmp_path / "src" / "zephyr"
    scan_root.mkdir(parents=True)
    _make_py_file(scan_root / "canonical.py", "zephyr.canonical", "MOD-TEST_canonical")
    # other 声明相同 module_id（basename 不同，不在 candidates 里）
    _make_py_file(scan_root / "other.py", "zephyr.other", "MOD-TEST_canonical")
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    cap = reg.get("test_cap")
    assert len(cap["pending_candidates"]) == 1
    assert "same module_id" in cap["pending_candidates"][0]["match_reason"]


def test_pending_candidates_excludes_declared(tmp_path: Path):
    """派生 canonical + duplicates 已收录的文件不算 pending。"""
    yaml_path = tmp_path / "registry.yaml"
    yaml_path.write_text(
        """
capabilities:
  - capability_id: test_cap
    aliases: [canonical]
    description: "Test"
""",
        encoding="utf-8",
    )
    scan_root = tmp_path / "src" / "zephyr"
    scan_root.mkdir(parents=True)
    _make_py_file(
        scan_root / "a" / "canonical.py",
        "zephyr.canonical",
        "MOD-TEST_canonical",
        blueprint="MOD-TEST",
        maturity="production",
    )
    # 同 basename 同 module_id 的派生 duplicate（会被 _derive 收录，不算 pending）
    _make_py_file(
        scan_root / "b" / "canonical.py",
        "zephyr.canonical",
        "MOD-TEST_canonical",
        blueprint="MOD-TEST",
        maturity="design",
    )
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    cap = reg.get("test_cap")
    assert cap["pending_candidates"] == []


# ---------------------------------------------------------------------------
# removed_duplicates git log 派生测试（mock subprocess）
# ---------------------------------------------------------------------------


def test_removed_duplicates_git_derived(tmp_path: Path, monkeypatch):
    """git log --diff-filter=D 派生 removed_duplicates（mock subprocess）。"""
    yaml_path = tmp_path / "registry.yaml"
    yaml_path.write_text(
        """
capabilities:
  - capability_id: ghost_cap
    aliases: [ghost]
    description: "ghost capability"
""",
        encoding="utf-8",
    )
    scan_root = tmp_path / "src" / "zephyr"
    scan_root.mkdir(parents=True)
    # 磁盘无 ghost.py（已被删除），但有另一个活文件让 canonical_alive 检测正常
    # 实际上无候选 → canonical_file="" canonical_alive=False
    fake_commit = "a" * 40
    # git log 输出：commit hash + 删除文件路径
    git_log_stdout = f"{fake_commit}\nsrc/zephyr/old/ghost.py\n"
    # git show 输出：被删文件的内容（含匹配能力的头部）
    deleted_content = "# [MODULE] zephyr.old.ghost\n# [A_module] module_id=MOD-OLD_ghost\npass\n"

    def fake_run(cmd, **kwargs):
        class FakeResult:
            returncode = 0
            stdout = ""
            stderr = ""

        r = FakeResult()
        cmd_str = " ".join(cmd) if isinstance(cmd, list) else str(cmd)
        if "log" in cmd_str and "--diff-filter=D" in cmd_str:
            r.stdout = git_log_stdout
        elif "show" in cmd_str:
            r.stdout = deleted_content
        return r

    monkeypatch.setattr("zephyr.governance.capability_lookup.subprocess.run", fake_run)
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    cap = reg.get("ghost_cap")
    # git 派生应找到 1 条 removed_duplicate
    git_derived = [d for d in cap["removed_duplicates"] if "git-derived" in d.get("note", "")]
    assert len(git_derived) == 1
    assert git_derived[0]["path"] == "src/zephyr/old/ghost.py"
    assert git_derived[0]["removed_in_commit"] == fake_commit
    assert git_derived[0]["module_id"] == "MOD-OLD_ghost"


def test_removed_duplicates_git_header_mismatch_skipped(tmp_path: Path, monkeypatch):
    """basename 匹配但头部不匹配能力 → 跳过（避免 basename 巧合误报）。"""
    yaml_path = tmp_path / "registry.yaml"
    yaml_path.write_text(
        """
capabilities:
  - capability_id: real_cap
    aliases: [ghost]
    description: "real capability"
""",
        encoding="utf-8",
    )
    scan_root = tmp_path / "src" / "zephyr"
    scan_root.mkdir(parents=True)
    fake_commit = "b" * 40
    git_log_stdout = f"{fake_commit}\nsrc/zephyr/old/ghost.py\n"
    # 头部 module_path 是 unrelated，不匹配 ghost 能力
    deleted_content = "# [MODULE] zephyr.unrelated.thing\n# [A_module] module_id=MOD-UNRELATED\npass\n"

    def fake_run(cmd, **kwargs):
        class FakeResult:
            returncode = 0
            stdout = ""
            stderr = ""

        r = FakeResult()
        cmd_str = " ".join(cmd) if isinstance(cmd, list) else str(cmd)
        if "log" in cmd_str:
            r.stdout = git_log_stdout
        elif "show" in cmd_str:
            r.stdout = deleted_content
        return r

    monkeypatch.setattr("zephyr.governance.capability_lookup.subprocess.run", fake_run)
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    cap = reg.get("real_cap")
    # 头部不匹配 → 不收录
    git_derived = [d for d in cap["removed_duplicates"] if "git-derived" in d.get("note", "")]
    assert git_derived == []


def test_removed_duplicates_manual_appended(tmp_path: Path, monkeypatch):
    """removed_duplicates_manual 始终追加（未被 git 跟踪的历史文件）。"""
    yaml_path = tmp_path / "registry.yaml"
    yaml_path.write_text(
        """
capabilities:
  - capability_id: manual_cap
    aliases: [manual]
    description: "manual test"
    removed_duplicates_manual:
      - path: src/zephyr/never_tracked/manual.py
        note: "未被 git 跟踪的历史死副本"
""",
        encoding="utf-8",
    )
    scan_root = tmp_path / "src" / "zephyr"
    scan_root.mkdir(parents=True)

    # mock git log 返回空（无 git 派生）
    def fake_run(cmd, **kwargs):
        class FakeResult:
            returncode = 0
            stdout = ""
            stderr = ""

        return FakeResult()

    monkeypatch.setattr("zephyr.governance.capability_lookup.subprocess.run", fake_run)
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    cap = reg.get("manual_cap")
    paths = [d["path"] for d in cap["removed_duplicates"]]
    assert "src/zephyr/never_tracked/manual.py" in paths
    manual_entry = [d for d in cap["removed_duplicates"] if d["path"] == "src/zephyr/never_tracked/manual.py"][0]
    assert "未被 git 跟踪" in manual_entry["note"]


# ---------------------------------------------------------------------------
# check_capability_duplicates 测试
# ---------------------------------------------------------------------------
# B 方案：所有信号皆阻断（无 advisory）。覆盖决策矩阵 4 分支：
#   1. conflicting（新文件是同蓝图 duplicate → 阻断）
#   2. sibling（同 basename 异蓝图 → 阻断，B 方案从 advisory 升级为阻断）
#   3. canonical_displaced（新 canonical 挤占已有同 basename 文件 → 阻断）
#   4. no signal（合法首实现 → 空列表）


def test_check_capability_duplicates_hard_conflicting(setup_registry):
    """conflicting：新文件是已有 canonical 的同蓝图 duplicate → 阻断。

    场景：setup_registry 已有 test/canonical.py (production, MOD-TEST) 作 canonical，
    shadow/canonical.py (design, MOD-TEST) 是 conflicting duplicate。
    以 shadow/canonical.py 为"新增文件"调用 → relation=conflicting。
    """
    yaml_path, scan_root = setup_registry
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    new_file = (
        str(scan_root / "shadow" / "canonical.py"),
        "src/zephyr/shadow/canonical.py",
    )
    dups = reg.check_capability_duplicates([new_file])
    assert len(dups) == 1
    assert dups[0].relation == "conflicting"
    assert dups[0].capability_id == "test_cap"
    assert "conflicting duplicate" in dups[0].detail


def test_check_capability_duplicates_sibling_block(tmp_path: Path):
    """sibling：同 basename 不同蓝图 → 阻断（B 方案从 advisory 升级为阻断）。

    场景：canonical (MOD-A, production) + duplicate (MOD-B, design)，同 basename
    "canonical" 但异蓝图 → relation=sibling（非 conflicting）→ 阻断。
    """
    yaml_path = tmp_path / "registry.yaml"
    yaml_path.write_text(SAMPLE_YAML, encoding="utf-8")
    scan_root = tmp_path / "src" / "zephyr"
    scan_root.mkdir(parents=True, exist_ok=True)
    _make_py_file(
        scan_root / "test" / "canonical.py",
        "zephyr.test.canonical",
        "MOD-A_canonical",
        blueprint="MOD-A",
        domain="D-TEST",
        maturity="production",
    )
    _make_py_file(
        scan_root / "shadow" / "canonical.py",
        "zephyr.shadow.canonical",
        "MOD-B_duplicate",
        blueprint="MOD-B",
        domain="D-TEST",
        maturity="design",
    )
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    new_file = (
        str(scan_root / "shadow" / "canonical.py"),
        "src/zephyr/shadow/canonical.py",
    )
    dups = reg.check_capability_duplicates([new_file])
    assert len(dups) == 1
    assert dups[0].relation == "sibling"
    assert dups[0].capability_id == "test_cap"


def test_check_capability_duplicates_canonical_displaced(setup_registry):
    """canonical_displaced：新文件成为 canonical 但已有同蓝图 duplicate → 阻断。

    场景：setup_registry 中 test/canonical.py (production, MOD-TEST) 是 canonical，
    shadow/canonical.py (design, MOD-TEST) 是 conflicting duplicate。
    以 test/canonical.py 为"新增文件"调用 → 它是 canonical，但 duplicates 含
    conflicting → relation=canonical_displaced_conflicting。
    """
    yaml_path, scan_root = setup_registry
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    new_file = (
        str(scan_root / "test" / "canonical.py"),
        "src/zephyr/test/canonical.py",
    )
    dups = reg.check_capability_duplicates([new_file])
    assert len(dups) == 1
    assert dups[0].relation == "canonical_displaced_conflicting"
    assert dups[0].capability_id == "test_cap"


def test_check_capability_duplicates_no_signal(setup_registry):
    """无信号：新文件 basename 不撞任何 cap → 空列表（门禁 ALLOW）。

    场景：合法首实现——新文件 module_path "zephyr.brand_new.thing"，basename "thing"
    不在 match_tokens 中 → check_file_canonical 返回 None → results=[]。
    """
    yaml_path, scan_root = setup_registry
    # 新建一个完全不相关的文件（合法首实现）
    _make_py_file(
        scan_root / "brand_new" / "thing.py",
        "zephyr.brand_new.thing",
        "MOD-BRAND_thing",
        blueprint="MOD-BRAND",
        domain="D-NEW",
        maturity="production",
    )
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    new_file = (
        str(scan_root / "brand_new" / "thing.py"),
        "src/zephyr/brand_new/thing.py",
    )
    dups = reg.check_capability_duplicates([new_file])
    assert dups == []


def test_removed_duplicates_no_git_keeps_manual(tmp_path: Path, monkeypatch):
    """非 git 仓库（git log 失败）→ git 派生为空，manual 条目保留。"""
    yaml_path = tmp_path / "registry.yaml"
    yaml_path.write_text(
        """
capabilities:
  - capability_id: nogit_cap
    aliases: [nogit]
    description: "no git"
    removed_duplicates_manual:
      - path: src/zephyr/old/nogit.py
        note: "manual only"
""",
        encoding="utf-8",
    )
    scan_root = tmp_path / "src" / "zephyr"
    scan_root.mkdir(parents=True)

    def fake_run(cmd, **kwargs):
        class FakeResult:
            returncode = 128  # git 错误
            stdout = ""
            stderr = "not a git repository"

        return FakeResult()

    monkeypatch.setattr("zephyr.governance.capability_lookup.subprocess.run", fake_run)
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    cap = reg.get("nogit_cap")
    # git 派生失败 → 只有 manual 条目
    assert len(cap["removed_duplicates"]) == 1
    assert cap["removed_duplicates"][0]["path"] == "src/zephyr/old/nogit.py"


def test_no_derive_removed_skips_git(tmp_path: Path, monkeypatch):
    """derive_removed=False → 不调用 git，removed_duplicates 只有 manual。"""
    yaml_path = tmp_path / "registry.yaml"
    yaml_path.write_text(
        """
capabilities:
  - capability_id: skip_cap
    aliases: [skip]
    description: "skip git"
    removed_duplicates_manual:
      - path: src/zephyr/old/skip.py
        note: "manual"
""",
        encoding="utf-8",
    )
    scan_root = tmp_path / "src" / "zephyr"
    scan_root.mkdir(parents=True)
    _make_py_file(scan_root / "skip.py", "zephyr.skip", "MOD-SKIP", blueprint="MOD-SKIP", maturity="production")

    call_count = [0]

    def fake_run(cmd, **kwargs):
        call_count[0] += 1

        class FakeResult:
            returncode = 0
            stdout = ""
            stderr = ""

        return FakeResult()

    monkeypatch.setattr("zephyr.governance.capability_lookup.subprocess.run", fake_run)
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root, derive_removed=False)
    assert call_count[0] == 0  # 未调用 git
    cap = reg.get("skip_cap")
    assert len(cap["removed_duplicates"]) == 1  # 只有 manual


# ---------------------------------------------------------------------------
# 边界 / 错误处理测试
# ---------------------------------------------------------------------------


def test_yaml_missing_raises(tmp_path: Path):
    scan_root = tmp_path / "src" / "zephyr"
    scan_root.mkdir(parents=True)
    with pytest.raises(FileNotFoundError):
        CapabilityLookup(yaml_path=tmp_path / "nonexistent.yaml", scan_root=scan_root)


def test_no_scan_mode(setup_registry):
    """scan=False 时不扫盘+不派生，canonical_file=""（未派生）。"""
    yaml_path, scan_root = setup_registry
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root, scan=False)
    assert len(reg.list_all()) == 1
    cap = reg.get("test_cap")
    # scan=False → 未派生 canonical_file
    assert cap["canonical_file"] == ""
    assert cap["pending_candidates"] == []


def test_reload(setup_registry):
    yaml_path, scan_root = setup_registry
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    assert len(reg.list_all()) == 1
    # 修改 YAML 加一条
    yaml_path.write_text(
        SAMPLE_YAML
        + """
  - capability_id: second_cap
    aliases: [second]
    description: "Second"
""",
        encoding="utf-8",
    )
    # 为 second_cap 创建磁盘文件
    _make_py_file(scan_root / "second.py", "zephyr.second", "MOD-SECOND", blueprint="MOD-SECOND", maturity="production")
    reg.reload()
    assert len(reg.list_all()) == 2


def test_normalize_path():
    assert _normalize_path("src\\zephyr\\test.py") == "src/zephyr/test.py"
    assert _normalize_path("./src/test.py") == "src/test.py"
    assert _normalize_path("src/test.py") == "src/test.py"


def test_empty_yaml(tmp_path: Path):
    """空 YAML（无 capabilities 键）应返回空列表，不报错。"""
    yaml_path = tmp_path / "registry.yaml"
    yaml_path.write_text("schema_version: '1.1.0'\n", encoding="utf-8")
    scan_root = tmp_path / "src" / "zephyr"
    scan_root.mkdir(parents=True)
    reg = CapabilityLookup(yaml_path=yaml_path, scan_root=scan_root)
    assert reg.list_all() == []
    assert reg.summary()["total_declared"] == 0


# ---------------------------------------------------------------------------
# 真实项目注册表集成测试（确保种子条目可加载 + 派生正确）
# ---------------------------------------------------------------------------


def test_real_registry_loads():
    """集成测试：真实项目 YAML 能加载，且包含 2 个种子条目。

    用 --no-scan 避免扫全项目拖慢测试（仅验证 YAML 加载）。
    """
    reg = CapabilityLookup(scan=False)
    caps = reg.list_all()
    cap_ids = {c["capability_id"] for c in caps}
    assert "session_handoff_continuity" in cap_ids
    assert "rollback_executor" in cap_ids


def test_find_ascii_multi_word_real_registry():
    """ASCII 多词短语回归测试（真注册表）——守护 _token_match 的 ASCII AND 分支。

    回归 bug：注册表 YAML 自广告的示范用法 find("session handoff") 旧版返回空
    （子串匹配无法跨 capability_id 的下划线），token AND 匹配后应命中。
    scan=False 覆盖 YAML 加载字段（capability_id/aliases/description）即可触发，
    避免扫全盘拖慢测试。
    """
    reg = CapabilityLookup(scan=False)
    # YAML 文档示范用法（capability_canonical_file_registry.yaml §AI 使用方式）
    results = reg.find("session handoff")
    cap_ids = {r["capability_id"] for r in results}
    assert "session_handoff_continuity" in cap_ids
    # 原失效场景另一例
    results = reg.find("vocabulary loader")
    cap_ids = {r["capability_id"] for r in results}
    assert "vocabulary_values_loader" in cap_ids
    # vocab_hardcode_detector 含 'vocabulary' 但不含 'loader' → 不误命中（AND 语义）
    assert "vocab_hardcode_detector" not in cap_ids


def test_real_registry_ssot_conflict_resolved_for_rollback_executor():
    """集成测试：rollback_executor SSoT 冲突已解决。

    ARCH-034 P4 删除 governance/rollback_executor.py 孤儿副本后，
    rollback_executor 不再出现在 list_ssot_conflicts() 中。
    rollback_executor 曾是唯一已登记的 SSoT 冲突
    （capability_canonical_file_registry.yaml 显式标注）。
    """
    reg = CapabilityLookup(scan=True, derive_removed=False)
    conflicts = reg.list_ssot_conflicts()
    cap_ids = {c["capability_id"] for c in conflicts}
    assert "rollback_executor" not in cap_ids


def test_real_registry_canonical_derived():
    """集成测试：真实注册表 canonical_file 由磁盘派生（非 YAML 硬编码）。"""
    reg = CapabilityLookup(scan=True, derive_removed=False)
    # rollback_executor canonical = infrastructure 版（production）
    rb = reg.get("rollback_executor")
    assert rb["canonical_file"] == "src/zephyr/infrastructure/rollback/rollback_executor.py"
    assert rb["maturity"] == "production"
    # module_id 真源对齐 depgraph 数字号（89bb5c2c59 文件头 module_id 对齐演进）
    assert rb["module_id"] == "MOD-INF-021"
    # session_handoff_continuity canonical = shared/session/session_continuity.py
    # （单候选：shared_services proxy 版已删除，commit 9ae4970995，P2 闭环）
    sh = reg.get("session_handoff_continuity")
    assert sh["canonical_file"] == "src/zephyr/shared/session/session_continuity.py"
    assert sh["maturity"] == "production"  # ARCH-MM-002: prototype→production
