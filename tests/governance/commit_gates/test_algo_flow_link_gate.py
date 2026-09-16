"""ALGO-FLOW-LINK 门禁纯逻辑单测（批9 收尾批 T3，tmp_path 隔离）。"""

from __future__ import annotations

from pathlib import Path

from zephyr.gov_enforcement.commit_gates.algo_flow_link_gate import check_algo_flow_links

_YAML_OK = """# ALGO_FLOW 外部真源——demo（真源 src/zephyr/pkg_a/demo.py）
doc_type: architecture_view
ttl: permanent
module: zephyr.pkg_a.demo
source_of_truth: src/zephyr/pkg_a/demo.py
algo_flow: |
    # [ALGO_FLOW]
    # 层: 输入
    # - id: I1
    #   name: 入参
    # 层: 算法
    # - id: A1
    #   name_zh: ① 主流程
    # [/ALGO_FLOW]
    # 边:
    # I1 --> A1
"""

_YAML_BROKEN = _YAML_OK.replace("# [/ALGO_FLOW]\n", "")

_PY_ANCHORED = '"""doc"""\n\n# [ALGO_FLOW] external: docs/03_modules/_domain_x/algo_flow/demo.yaml\n\nfrom __future__ import annotations\n'


def _make_repo(tmp_path: Path) -> Path:
    (tmp_path / "src/zephyr/pkg_a").mkdir(parents=True)
    (tmp_path / "src/zephyr/pkg_a/demo.py").write_text(_PY_ANCHORED, encoding="utf-8")
    y = tmp_path / "docs/03_modules/_domain_x/algo_flow"
    y.mkdir(parents=True)
    (y / "demo.yaml").write_text(_YAML_OK, encoding="utf-8")
    return tmp_path


def test_valid_link_passes(tmp_path: Path) -> None:
    root = _make_repo(tmp_path)
    blocked, msg = check_algo_flow_links(
        ["src/zephyr/pkg_a/demo.py", "docs/03_modules/_domain_x/algo_flow/demo.yaml"], root
    )
    assert not blocked, msg


def test_anchor_to_missing_yaml_blocks(tmp_path: Path) -> None:
    root = _make_repo(tmp_path)
    (root / "docs/03_modules/_domain_x/algo_flow/demo.yaml").unlink()
    blocked, msg = check_algo_flow_links(["src/zephyr/pkg_a/demo.py"], root)
    assert blocked
    assert "不存在的 yaml" in msg


def test_anchor_to_broken_yaml_blocks(tmp_path: Path) -> None:
    root = _make_repo(tmp_path)
    (root / "docs/03_modules/_domain_x/algo_flow/demo.yaml").write_text(_YAML_BROKEN, encoding="utf-8")
    blocked, msg = check_algo_flow_links(["src/zephyr/pkg_a/demo.py"], root)
    assert blocked
    assert "不可解析" in msg


def test_yaml_missing_source_of_truth_blocks(tmp_path: Path) -> None:
    root = _make_repo(tmp_path)
    y = root / "docs/03_modules/_domain_x/algo_flow/demo.yaml"
    y.write_text("\n".join(l for l in _YAML_OK.splitlines() if not l.startswith("source_of_truth")) + "\n", encoding="utf-8")
    blocked, msg = check_algo_flow_links(["docs/03_modules/_domain_x/algo_flow/demo.yaml"], root)
    assert blocked
    assert "source_of_truth" in msg


def test_yaml_dangling_source_of_truth_blocks(tmp_path: Path) -> None:
    root = _make_repo(tmp_path)
    y = root / "docs/03_modules/_domain_x/algo_flow/demo.yaml"
    y.write_text(_YAML_OK.replace("src/zephyr/pkg_a/demo.py", "src/zephyr/pkg_a/gone.py"), encoding="utf-8")
    blocked, msg = check_algo_flow_links(["docs/03_modules/_domain_x/algo_flow/demo.yaml"], root)
    assert blocked
    assert "不存在的源文件" in msg


def test_non_algo_flow_files_ignored(tmp_path: Path) -> None:
    root = _make_repo(tmp_path)
    blocked, msg = check_algo_flow_links(["docs/README.md", "config/app.yaml"], root)
    assert not blocked, msg


def test_empty_files_pass(tmp_path: Path) -> None:
    assert check_algo_flow_links([], tmp_path) == (False, "")
    assert check_algo_flow_links(None, tmp_path) == (False, "")


_PY_DEAD_BLOCK = (
    '# [BLUEPRINT] MOD-X | docs/03_modules/_domain_x/blueprint.md\n'
    "# [ALGO_FLOW]\n# 层: 输入\n# - id: I9\n#   name: 契约头副本\n# [/ALGO_FLOW]\n"
    '"""demo —— 说明。\n\n'
    "# [ALGO_FLOW] external: docs/03_modules/_domain_x/algo_flow/demo.yaml\n"
    '"""\n\nX = 1\n'
)


def test_dead_block_outside_docstring_blocks(tmp_path: Path) -> None:
    """锚 + 契约头副本=双真源（读卡路径看不见副本）→ 硬阻断，且指名清偿命令。"""
    root = _make_repo(tmp_path)
    (root / "src/zephyr/pkg_a/dead.py").write_text(_PY_DEAD_BLOCK, encoding="utf-8")
    blocked, msg = check_algo_flow_links(["src/zephyr/pkg_a/dead.py"], root)
    assert blocked, msg
    assert "双真源" in msg and "externalize_algo_flow.py" in msg


def test_dead_block_check_scoped_to_src_zephyr(tmp_path: Path) -> None:
    """范围护栏：scripts/tests 下的夹具字符串块不入本判据（波次夹具大量合法内联样块）。"""
    root = _make_repo(tmp_path)
    s = root / "scripts/governance/demo.py"
    s.parent.mkdir(parents=True)
    s.write_text(_PY_DEAD_BLOCK, encoding="utf-8")
    blocked, msg = check_algo_flow_links(["scripts/governance/demo.py"], root)
    assert not blocked, msg


def test_dead_block_check_survives_missing_syspath_bootstrap(tmp_path: Path, monkeypatch) -> None:
    """网关进程未必预置 scripts/governance：判据必须自己补 bootstrap，不得静默放行。"""
    import sys
    from pathlib import PurePosixPath

    root = _make_repo(tmp_path)
    (root / "src/zephyr/pkg_a/dead.py").write_text(_PY_DEAD_BLOCK, encoding="utf-8")
    saved = list(sys.path)
    removed = {m: sys.modules.pop(m) for m in list(sys.modules) if m.startswith("_shared")}
    monkeypatch.setattr(sys, "path", [p for p in saved if "governance" not in p.replace("\\", "/")])
    try:
        blocked, msg = check_algo_flow_links(["src/zephyr/pkg_a/dead.py"], root)
    finally:
        sys.modules.update(removed)
    assert blocked, f"bootstrap 缺失导致 fail-open: {msg}"
    assert "双真源" in msg


def test_inline_block_in_docstring_not_flagged(tmp_path: Path) -> None:
    """合法内联块（出仓前形态，块在 docstring 内）不触发双真源判据。"""
    root = _make_repo(tmp_path)
    p = root / "src/zephyr/pkg_a/inline.py"
    p.write_text(
        '"""demo —— 说明。\n\n'
        "# [ALGO_FLOW]\n# 层: 输入\n# - id: I1\n#   name: 入参\n# [/ALGO_FLOW]\n"
        '"""\n\nX = 1\n',
        encoding="utf-8",
    )
    blocked, msg = check_algo_flow_links(["src/zephyr/pkg_a/inline.py"], root)
    assert not blocked, msg


def test_staged_content_preferred(tmp_path: Path) -> None:
    """staged 版本可解析而工作区坏 → 以 staged 为准放行（commit 语义真源）。"""
    root = _make_repo(tmp_path)
    staged_ok = {"docs/03_modules/_domain_x/algo_flow/demo.yaml": _YAML_OK}

    def read_staged(rel: str) -> str | None:
        return staged_ok.get(rel)

    (root / "docs/03_modules/_domain_x/algo_flow/demo.yaml").write_text(_YAML_BROKEN, encoding="utf-8")
    blocked, msg = check_algo_flow_links(
        ["docs/03_modules/_domain_x/algo_flow/demo.yaml"], root, read_staged=read_staged
    )
    assert not blocked, msg
