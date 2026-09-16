# [BLUEPRINT] MOD-GOV_LONG_PARAM_LIST_GATE | (auto-injected by S4 reconciler) | §
# [TTL] permanent
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


# ------------------------------------------------------------------ 图可达判据（2026-09-16 增）
# "块可解析"曾是太弱的门槛：id 吞中文描述、并列/紧凑边写法、块标量缩进三类坏图能在门禁全绿
# 下存活（全仓普查 17+29 件，边数静默归零=全景图假绿）。判据真源=validate_graph，
# 本组测试钉住"门禁确实消费它"以及"只在基础设施故障时降级"。
# 反向钉：_YAML_OK 本身字段不全（缺 name_en/输出层）却必须放行——字段欠账不进门禁，
# 否则全仓百余件历史欠账连坐无辜提交人。

_YAML_NO_EDGE = "\n".join(
    ln for ln in _YAML_OK.splitlines() if not ln.strip().startswith(("# 边:", "# I1 -->"))
) + "\n"

_YAML_FANIN = """# ALGO_FLOW 外部真源——demo（并列+紧凑边写法）
doc_type: architecture_view
ttl: permanent
module: zephyr.pkg_a.demo
source_of_truth: src/zephyr/pkg_a/demo.py
algo_flow: |
    # [ALGO_FLOW]
    # 层: 输入
    # - id: I1
    #   name: 入参一
    # - id: I2
    #   name: 入参二
    # 层: 算法
    # - id: F1
    #   name_zh: 汇流
    # - id: A1
    #   name_zh: 主流程
    # 层: 输出
    # - id: O1
    #   name_zh: 出参
    #   is_break: true
    # [/ALGO_FLOW]
    # 边:
    # I1, I2 --> F1 ; F1 --> A1
    # A1 -.->|断点| O1
"""


def _write_mirror(root: Path, text: str) -> None:
    (root / "docs/03_modules/_domain_x/algo_flow/demo.yaml").write_text(text, encoding="utf-8")


def test_mirror_without_edges_blocks(tmp_path: Path) -> None:
    """边段整体不匹配（缩进/紧凑写法病根）→ 边数归零=无图，硬阻断。"""
    root = _make_repo(tmp_path)
    _write_mirror(root, _YAML_NO_EDGE)
    blocked, msg = check_algo_flow_links(["docs/03_modules/_domain_x/algo_flow/demo.yaml"], root)
    assert blocked, msg
    assert "推导图不可达" in msg and "无边定义" in msg


def test_anchor_to_dangling_edge_yaml_blocks(tmp_path: Path) -> None:
    """锚指向的 yaml 图坏（端点未定义）同样阻断——锚校验不止查"文件在不在"。"""
    root = _make_repo(tmp_path)
    _write_mirror(root, _YAML_OK.replace("# I1 --> A1", "# I1 --> A9"))
    blocked, msg = check_algo_flow_links(["src/zephyr/pkg_a/demo.py"], root)
    assert blocked, msg
    assert "边终点未定义" in msg


def test_illegal_node_id_blocks(tmp_path: Path) -> None:
    """id 含中文/空格 → mermaid 节点键必炸，硬阻断。"""
    root = _make_repo(tmp_path)
    _write_mirror(root, _YAML_OK.replace("# - id: I1", "# - id: ① 输入层"))
    blocked, msg = check_algo_flow_links(["docs/03_modules/_domain_x/algo_flow/demo.yaml"], root)
    assert blocked, msg
    assert "节点ID非法" in msg


def test_break_edge_inconsistency_blocks(tmp_path: Path) -> None:
    """正常边指向 is_break 节点（断点标记漂移）→ 图判据不一致，硬阻断。"""
    root = _make_repo(tmp_path)
    _write_mirror(root, _YAML_FANIN.replace("# A1 -.->|断点| O1", "# A1 --> O1"))
    blocked, msg = check_algo_flow_links(["docs/03_modules/_domain_x/algo_flow/demo.yaml"], root)
    assert blocked, msg
    assert "正常边指向断点节点" in msg


def test_shorthand_id_with_description_passes(tmp_path: Path) -> None:
    """速记写法 "- id: I1 中文描述"：id 取首 token、描述不丢，边端点仍可解析 → 放行。"""
    root = _make_repo(tmp_path)
    _write_mirror(root, _YAML_OK.replace("# - id: I1", "# - id: I1 入参闸门"))
    blocked, msg = check_algo_flow_links(
        ["src/zephyr/pkg_a/demo.py", "docs/03_modules/_domain_x/algo_flow/demo.yaml"], root
    )
    assert not blocked, msg


def test_fanin_and_compact_edge_spellings_pass(tmp_path: Path) -> None:
    """并列端点展开 + 分号紧凑写法：旧解析器此处边数归零，修好后必须放行。"""
    root = _make_repo(tmp_path)
    _write_mirror(root, _YAML_FANIN)
    blocked, msg = check_algo_flow_links(
        ["src/zephyr/pkg_a/demo.py", "docs/03_modules/_domain_x/algo_flow/demo.yaml"], root
    )
    assert not blocked, msg


def test_graph_rules_unavailable_degrades_fail_open(tmp_path: Path, monkeypatch) -> None:
    """判据真源不可达=基础设施故障 → 降级放行（不得把"加载失败"判成违规连坐提交人）。"""
    from zephyr.gov_enforcement.commit_gates import algo_flow_link_gate as g

    root = _make_repo(tmp_path)
    _write_mirror(root, _YAML_NO_EDGE)
    monkeypatch.setattr(g, "_load_graph_rules", lambda _root: None)
    blocked, msg = check_algo_flow_links(["docs/03_modules/_domain_x/algo_flow/demo.yaml"], root)
    assert not blocked, msg


_PY_DUP_INLINE = (
    '"""demo —— 说明。\n\n'
    "# [ALGO_FLOW]\n# 层: 输入\n# - id: I1\n#   name: 入参\n# [/ALGO_FLOW]\n"
    "\n"
    "# [ALGO_FLOW]\n# 层: 算法\n# - id: A1\n#   name_zh: 第二块\n# [/ALGO_FLOW]\n"
    '"""\n\nX = 1\n'
)


def test_second_in_body_block_blocks(tmp_path: Path) -> None:
    """体内第 2 块：parse_algo_flow 只认首个 起→止 对，第二块连边段永不可达 → 硬阻断。"""
    root = _make_repo(tmp_path)
    (root / "src/zephyr/pkg_a/twoblocks.py").write_text(_PY_DUP_INLINE, encoding="utf-8")
    blocked, msg = check_algo_flow_links(["src/zephyr/pkg_a/twoblocks.py"], root)
    assert blocked, msg
    assert "多余 ALGO_FLOW 机器块" in msg and "只能有一个 ALGO_FLOW 载体" in msg


_PY_ANCHOR_PLUS_BLOCK = (
    '"""demo —— 说明。\n\n'
    "# [ALGO_FLOW] external: docs/03_modules/_domain_x/algo_flow/demo.yaml\n"
    "# [ALGO_FLOW]\n# 层: 算法\n# - id: A9\n#   name_zh: 写回的块\n# [/ALGO_FLOW]\n"
    '"""\n\nX = 1\n'
)

_PY_BLOCK_PLUS_ANCHOR = (
    '"""demo —— 说明。\n\n'
    "# [ALGO_FLOW]\n# 层: 算法\n# - id: A9\n#   name_zh: 写回的块\n# [/ALGO_FLOW]\n"
    "# [ALGO_FLOW] external: docs/03_modules/_domain_x/algo_flow/demo.yaml\n"
    '"""\n\nX = 1\n'
)


def test_anchor_plus_inline_block_blocks(tmp_path: Path) -> None:
    """红蓝实弹 R2 哑火形态的门禁侧复现（2026-09-17，HEAD=b873ee71d3 真落地过）。

    锚本身合法（yaml 在、图可达），所以锚校验分支一条都不报；违规全在"载体并存"这一条。
    """
    root = _make_repo(tmp_path)
    for name, txt in (("conflict_a.py", _PY_ANCHOR_PLUS_BLOCK), ("conflict_b.py", _PY_BLOCK_PLUS_ANCHOR)):
        (root / f"src/zephyr/pkg_a/{name}").write_text(txt, encoding="utf-8")
        blocked, msg = check_algo_flow_links([f"src/zephyr/pkg_a/{name}"], root)
        assert blocked, f"{name}: {msg}"
        assert "多余 ALGO_FLOW 机器块" in msg, f"{name}: {msg}"
        assert "不存在的 yaml" not in msg, f"{name}: {msg}"


def test_two_judgments_do_not_cross_report(tmp_path: Path) -> None:
    """判据分家（门禁侧）：死块只报"体外"、多块只报"体内"——混装会让清偿者找错位置。"""
    root = _make_repo(tmp_path)
    dead_only = root / "src/zephyr/pkg_a/deadonly.py"
    dead_only.write_text(_PY_DEAD_BLOCK, encoding="utf-8")
    _b1, msg1 = check_algo_flow_links(["src/zephyr/pkg_a/deadonly.py"], root)
    assert "双真源" in msg1 and "多余 ALGO_FLOW 机器块" not in msg1, msg1

    dup_only = root / "src/zephyr/pkg_a/duponly.py"
    dup_only.write_text(_PY_DUP_INLINE, encoding="utf-8")
    _b2, msg2 = check_algo_flow_links(["src/zephyr/pkg_a/duponly.py"], root)
    assert "多余 ALGO_FLOW 机器块" in msg2 and "落在 module docstring 之外" not in msg2, msg2


def test_dup_inline_check_scoped_to_src_zephyr(tmp_path: Path) -> None:
    """范围护栏同死块判据：tests/scripts 夹具里的示例多块样块不入本判据（own-diff 例外口径）。"""
    root = _make_repo(tmp_path)
    s = root / "scripts/governance/demo_twoblocks.py"
    s.parent.mkdir(parents=True, exist_ok=True)
    s.write_text(_PY_DUP_INLINE, encoding="utf-8")
    blocked, msg = check_algo_flow_links(["scripts/governance/demo_twoblocks.py"], root)
    assert not blocked, msg


class _FakeGateway:
    """只提供门禁用到的两个面：project_root 与 run_git（``git show :<path>``）。"""

    def __init__(self, root: Path, staged: dict[str, str]) -> None:
        self.project_root = root
        self._staged = staged
        self.calls: list[list[str]] = []

    def run_git(self, cmd, cwd=None):  # noqa: ANN001, ARG002 — 契约同 gateway.run_git
        import subprocess

        self.calls.append(list(cmd))
        assert cmd[:2] == ["git", "show"] and cmd[2].startswith(":"), cmd
        rel = cmd[2][1:]
        if rel in self._staged:
            return subprocess.CompletedProcess(cmd, 0, self._staged[rel], "")
        return subprocess.CompletedProcess(cmd, 128, "", f"fatal: path '{rel}' does not exist")


def test_gate_spec_reads_staged_blob_not_worktree(tmp_path: Path) -> None:
    """#ARCH-321 治本回归：原 ``gateway.read_staged_file`` 不存在，宽 except 吞异常后
    静默回退读磁盘——门禁判的于是是工作区内容，而 commit 落的是 index 内容。

    双向钉死：① index 脏 / 工作区净 → 必拦（漏判方向）；② index 净 / 工作区脏 → 必放
    （误判方向，且证明它读的是 staged 而非磁盘）。
    """
    from zephyr.gov_enforcement.commit_gates.algo_flow_link_gate import make_algo_flow_link_gate

    root = _make_repo(tmp_path)
    rel = "src/zephyr/pkg_a/demo.py"
    spec = make_algo_flow_link_gate()

    root.joinpath(rel).write_text(_PY_ANCHORED, encoding="utf-8")  # 工作区=净
    dirty = _FakeGateway(root, {rel: _PY_ANCHOR_PLUS_BLOCK})  # index=脏
    passed, msg = spec.check(dirty, [rel])
    assert passed is False, msg
    assert "多余 ALGO_FLOW 机器块" in msg, msg
    assert dirty.calls, "未走 git show :<path>=staged 读取器没接上"

    root.joinpath(rel).write_text(_PY_ANCHOR_PLUS_BLOCK, encoding="utf-8")  # 工作区=脏
    clean = _FakeGateway(root, {rel: _PY_ANCHORED})  # index=净
    passed2, msg2 = spec.check(clean, [rel])
    assert passed2 is True, msg2
