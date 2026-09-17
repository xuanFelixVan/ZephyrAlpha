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
    """判据源**不在盘上**=环境降级 → 结构性兜底放行（不得把环境问题判成违规连坐提交人）。"""
    from zephyr.gov_enforcement.commit_gates import algo_flow_link_gate as g

    root = _make_repo(tmp_path)
    _write_mirror(root, _YAML_NO_EDGE)
    monkeypatch.setattr(g, "_load_graph_rules", lambda _root: None)
    monkeypatch.setattr(g, "_rules_source_present", lambda _root: False)
    blocked, msg = check_algo_flow_links(["docs/03_modules/_domain_x/algo_flow/demo.yaml"], root)
    assert not blocked, msg


def test_criteria_source_on_disk_but_unloadable_blocks(tmp_path: Path, monkeypatch) -> None:
    """判据源在盘上却拿不到=仓库自身缺陷 → 必须阻断。

    旧行为是 rules=None 一律降级：死块/体内多块/图可达三条判据整体静默关闭而门禁全绿，
    2026-09-17 红蓝实弹 R1/R3 经生产队列真落地（e10ac5acc4 / 2924601305）的机制半边。
    """
    from zephyr.gov_enforcement.commit_gates import algo_flow_link_gate as g

    root = _make_repo(tmp_path)
    _write_mirror(root, _YAML_NO_EDGE)
    monkeypatch.setattr(g, "_load_graph_rules", lambda _root: None)
    monkeypatch.setattr(g, "_rules_source_present", lambda _root: True)
    blocked, msg = check_algo_flow_links(["docs/03_modules/_domain_x/algo_flow/demo.yaml"], root)
    assert blocked, "判据源在场却加载失败被当环境问题放行=假绿"
    assert "判据真源" in msg and "fail-closed" in msg, msg


# R1 实弹形态：锚在 docstring 内、机器块紧跟 docstring 之后（与 _PY_DEAD_BLOCK 的"之前"对称）
_PY_DEAD_BLOCK_AFTER_DOCSTRING = (
    '"""demo —— 说明。\n\n'
    "# [ALGO_FLOW] external: docs/03_modules/_domain_x/algo_flow/demo.yaml\n"
    '"""\n'
    "# [ALGO_FLOW]\n# 层: 算法\n# - id: RB9\n#   name: 红蓝探针块\n# [/ALGO_FLOW]\n"
    "# 边:\n# RB9 --> RB9\n\nX = 1\n"
)


def test_stale_sys_modules_criteria_does_not_disable_gate(tmp_path: Path, monkeypatch) -> None:
    """常驻进程 sys.modules 里的**旧判据副本**不得让判据线失能（R1/R3 落地根因半边）。

    复刻事故形态：`_shared.code_algorithm_extractor` 已被某更早的 import 缓存、且缺
    2026-09-16/17 新增的两个几何符号——旧写法 `from _shared... import` 撞 ImportError
    → rules=None → 死块判据静默关闭（belt 守护 07:17 常驻，死块符号 21:58 才进
    extractor，实测 R1 落地）。现写法按盘上文件直载，判据语义与提交时刻仓库一致。
    """
    import sys
    import types

    from zephyr.gov_enforcement.commit_gates import algo_flow_link_gate as g

    stale_ext = types.ModuleType("_shared.code_algorithm_extractor")
    stale_ext.parse_algo_flow = lambda *a, **k: None  # 只有旧符号，几何判据缺席
    stale_val = types.ModuleType("_shared.algo_flow_validate_marker")
    pkg = types.ModuleType("_shared")
    pkg.__path__ = []  # type: ignore[attr-defined]
    pkg.code_algorithm_extractor = stale_ext  # type: ignore[attr-defined]
    pkg.algo_flow_validate_marker = stale_val  # type: ignore[attr-defined]
    for name, mod in (("_shared", pkg),
                      ("_shared.code_algorithm_extractor", stale_ext),
                      ("_shared.algo_flow_validate_marker", stale_val)):
        monkeypatch.setitem(sys.modules, name, mod)

    assert g._load_graph_rules(tmp_path) is not None, "判据须从盘上直载，不吃 sys.modules 旧缓存"

    root = _make_repo(tmp_path)
    (root / "src/zephyr/pkg_a/after.py").write_text(
        _PY_DEAD_BLOCK_AFTER_DOCSTRING, encoding="utf-8"
    )
    blocked, msg = check_algo_flow_links(["src/zephyr/pkg_a/after.py"], root)
    assert blocked and "落在 module docstring 之外" in msg, msg


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
    """只提供门禁用到的面：project_root 与 run_git（``git show``/``diff --cached``/``grep``）。"""

    def __init__(
        self,
        root: Path,
        staged: dict[str, str],
        *,
        deleted: list[str] | None = None,
        anchors: dict[str, list[str]] | None = None,
    ) -> None:
        self.project_root = root
        self._staged = staged
        self._deleted = deleted or []
        self._anchors = anchors or {}
        self.calls: list[list[str]] = []

    def run_git(self, cmd, cwd=None):  # noqa: ANN001, ARG002 — 契约同 gateway.run_git
        import subprocess

        self.calls.append(list(cmd))
        if cmd[:3] == ["git", "diff", "--cached"]:
            return subprocess.CompletedProcess(cmd, 0, "\n".join(self._deleted), "")
        if cmd[:3] == ["git", "grep", "-l"]:
            assert cmd[3] == "-F" and cmd[5] == "HEAD", cmd
            hits = self._anchors.get(cmd[4], [])
            out = "".join(f"{h}\n" for h in hits)
            return subprocess.CompletedProcess(cmd, 0 if hits else 1, out, "")
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


# ---------------------------------------------------------------- 退役方向（#ARCH-326 清偿通道）

_MIRROR_REL = "docs/03_modules/_domain_x/algo_flow/demo.yaml"


def _retire_repo(tmp_path: Path) -> Path:
    """镜像已从盘上消失（退役）的仓库——源侧无锚（源早已随模块外迁/删除）。"""
    root = _make_repo(tmp_path)
    (root / _MIRROR_REL).unlink()
    return root


def test_unreadable_yaml_without_delete_declaration_still_blocks(tmp_path: Path) -> None:
    """默认（未声明 deleted 判据）=旧硬阻断行为一字不改：文件损坏/半写不被"没读到就算删"放过。"""
    root = _retire_repo(tmp_path)
    blocked, msg = check_algo_flow_links([_MIRROR_REL], root)
    assert blocked
    assert "不可读" in msg


def test_declared_delete_without_anchor_probe_blocks(tmp_path: Path) -> None:
    """核心 API 不许"没查=没锚"：声明了删除却没给探测器，一律 fail-closed。"""
    root = _retire_repo(tmp_path)
    blocked, msg = check_algo_flow_links([_MIRROR_REL], root, deleted=lambda _rel: True)
    assert blocked
    assert "未提供反向锚探测器" in msg


def test_retired_mirror_without_live_anchor_passes(tmp_path: Path) -> None:
    root = _retire_repo(tmp_path)
    blocked, msg = check_algo_flow_links(
        [_MIRROR_REL], root, deleted=lambda _rel: True, reverse_anchor=lambda _rel: []
    )
    assert not blocked, msg


def test_retired_mirror_with_live_anchor_blocks(tmp_path: Path) -> None:
    """删早了必须红：仍有 external 锚指着它 = 全景图当场断链，且消息点名锚文件可清。"""
    root = _retire_repo(tmp_path)
    blocked, msg = check_algo_flow_links(
        [_MIRROR_REL],
        root,
        deleted=lambda _rel: True,
        reverse_anchor=lambda _rel: ["src/zephyr/pkg_a/demo.py"],
    )
    assert blocked
    assert "仍有 1 处 external 锚指向它" in msg and "src/zephyr/pkg_a/demo.py" in msg


def _spec():
    from zephyr.gov_enforcement.commit_gates.algo_flow_link_gate import (
        make_algo_flow_link_gate,
    )

    return make_algo_flow_link_gate()


def test_gate_spec_allows_declared_mirror_retirement(tmp_path: Path) -> None:
    """接线钉（不 mock 判据本身）：staged 删除清单 + 反向锚探测两条 git 调用必须真被消费。"""
    root = _retire_repo(tmp_path)
    gw = _FakeGateway(root, {}, deleted=[_MIRROR_REL], anchors={_MIRROR_REL: []})
    passed, msg = _spec().check(gw, [_MIRROR_REL])
    assert passed is True, msg
    assert any(c[:3] == ["git", "diff", "--cached"] for c in gw.calls), gw.calls


def test_gate_spec_blocks_retirement_while_anchor_survives(tmp_path: Path) -> None:
    root = _retire_repo(tmp_path)
    gw = _FakeGateway(
        root, {}, deleted=[_MIRROR_REL], anchors={_MIRROR_REL: ["src/zephyr/pkg_a/demo.py"]}
    )
    passed, msg = _spec().check(gw, [_MIRROR_REL])
    assert passed is False
    assert "external 锚指向它" in msg, msg


def test_gate_spec_keeps_hard_block_when_delete_not_staged(tmp_path: Path) -> None:
    """反向证明：盘上没有 + 本次没 staged 删除（清单为空/观测故障）→ 回到硬阻断，不 fail-open。"""
    root = _retire_repo(tmp_path)
    gw = _FakeGateway(root, {}, deleted=[], anchors={_MIRROR_REL: []})
    passed, msg = _spec().check(gw, [_MIRROR_REL])
    assert passed is False
    assert "不可读" in msg, msg


def test_gate_spec_ignores_anchor_in_file_deleted_same_commit(tmp_path: Path) -> None:
    """整模块退役双向钉：HEAD 里的锚若属同批删除的 .py，随文件一起消失=放行；
    锚在既没改也没删的文件里=当场断链，必须红。只写第一向可以被"干脆不看锚"蒙过。"""
    root = _retire_repo(tmp_path)
    gw_del = _FakeGateway(
        root,
        {},
        deleted=[_MIRROR_REL, "src/zephyr/pkg_a/demo.py"],
        anchors={_MIRROR_REL: ["src/zephyr/pkg_a/demo.py"]},
    )
    passed, msg = _spec().check(gw_del, [_MIRROR_REL])
    assert passed is True, msg

    root2 = _retire_repo(tmp_path / "second")
    gw_keep = _FakeGateway(
        root2,
        {},
        deleted=[_MIRROR_REL],
        anchors={_MIRROR_REL: ["src/zephyr/pkg_a/demo.py"]},
    )
    passed2, msg2 = _spec().check(gw_keep, [_MIRROR_REL])
    assert passed2 is False
    assert "external 锚指向它" in msg2, msg2
