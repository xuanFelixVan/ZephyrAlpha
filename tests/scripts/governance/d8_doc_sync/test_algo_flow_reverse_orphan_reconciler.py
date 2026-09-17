# [BLUEPRINT] MOD-algo_flow_reverse_orphan | scripts/governance/d8_doc_sync/algo_flow_reverse_orphan_reconciler.py | §
# [TTL] permanent
"""test_algo_flow_reverse_orphan_reconciler.py — 反向孤件普查/退役判据（#ARCH-326）

判据面用真 git 仓（tmp_path + 真实 commit）而非 mock：孤件三要素里"源确有退役提交"
只能由真历史证明，mock git 会让整条判据退化成"断言我自己写的假数据"。

红蓝对照（每条正向判据都配一条反向证明，防止"永远 clean 的假绿"）：
- 源在 → 0 孤件；源被删 → 1 孤件（同一 fixture 只差一次 commit）
- 缺 source_of_truth 键 → 不判孤件
- 源从未被跟踪（路径写错）→ 引用异常桶，永不退役
- 源侧仍有 live 反向锚 → 否决，不判孤件
- 退役面：无裁定/裁定未点名/裁定非 active → 拒执行且盘上零改动
- 变异证明：逐条撤护栏（monkeypatch），误判必须复现
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
import yaml

_REPO_ROOT = Path(__file__).resolve().parents[4]
for _p in (
    str(_REPO_ROOT / "src"),
    str(_REPO_ROOT / "scripts"),
    str(_REPO_ROOT / "scripts" / "governance" / "d3_metadata"),
    str(_REPO_ROOT / "scripts" / "governance" / "d8_doc_sync"),
):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import algo_flow_reverse_orphan_reconciler as rev  # noqa: E402

MIRROR_REL = "docs/03_modules/_domain_x/algo_flow/pkg/mod__init__.yaml"
SOT_REL = "src/zephyr/infrastructure/pkg/__init__.py"
REGISTRY_REL = "docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml"
RULING_REL = "docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml"
KEEP_MIRROR_REL = "docs/03_modules/_domain_x/algo_flow/keep/keep__init__.yaml"
KEEP_SOT_REL = "src/zephyr/infrastructure/keep/__init__.py"

_MIRROR_TEXT = (
    "# ALGO_FLOW 外部真源——__init__\n"
    "doc_type: architecture_view\n"
    "ttl: permanent\n"
    "module: src.zephyr.infrastructure.pkg.__init__\n"
    f"source_of_truth: {SOT_REL}\n"
    "algo_flow: |\n"
    "    # [ALGO_FLOW]\n"
    "    # 层: 输入\n"
)

_SOT_TEXT = '"""pkg."""\n\nX = 1\n'


def registry_text(entries: list[str], *, tail_key: str = "di_seam_exemptions") -> str:
    body = "".join(f"- file: {rel}\n  token: tok-{i}\n  created_by: st-test\n  capability: test_cap\n" for i, rel in enumerate(entries))
    return f"module_id: REG-TEST\nttl: permanent\ncreation_tokens:\n{body}{tail_key}: []\n"


def rulings_text(ruling_id: str, *, status: str, target: str) -> str:
    # 根键=entries：与仓内 ruling_registry.yaml 实际 schema 对齐（unique_key=ruling_id）
    return (
        "module_id: REG-RULING-TEST\n"
        "unique_key: ['ruling_id']\n"
        "entries:\n"
        f"- ruling_id: '{ruling_id}'\n"
        f"  status: '{status}'\n"
        f"  summary: >-\n    批准退役 {target}\n"
        f"  affected_files: ['{target}']\n"
    )


class Gw:
    """真 git 仓之上的最小 gateway 面（run_git 跑真 git，不 mock）。"""

    def __init__(self, root: Path, *, commit_shell: bool = False) -> None:
        self.project_root = Path(root)
        self.commits: list[tuple[str, list[str], str]] = []
        self._commit_shell = commit_shell

    def run_git(self, cmd: list[str]):
        return subprocess.run(
            cmd,
            cwd=str(self.project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )

    def _commit_auto(self, session_id: str, files: list[str], message: str):
        self.commits.append((session_id, files, message))
        if not self._commit_shell:
            return type("_R", (), {"status": "OK"})()
        for f in files:
            self.run_git(["git", "add", "-A", "--", f])
        r = self.run_git(["git", "commit", "-m", message, "--no-verify"])
        status = "OK" if r.returncode == 0 else f"FAILED({r.stdout[-150:]}{r.stderr[-150:]})"
        return type("_R", (), {"status": status})()


class Repo:
    """tmp_path 真 git 仓 + 写文件/提交 helper + gateway 构造位。"""

    def __init__(self, root: Path) -> None:
        self.root = root

    def git(self, *args: str) -> str:
        r = subprocess.run(
            ["git", *args],
            cwd=str(self.root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert r.returncode == 0, f"git {' '.join(args)}: {r.stdout}{r.stderr}"
        return r.stdout

    def write(self, rel: str, text: str) -> Path:
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8", newline="")
        return p

    def read(self, rel: str) -> str:
        return (self.root / rel).read_text(encoding="utf-8")

    def commit(self, message: str) -> None:
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)

    def gw(self, **kw) -> Gw:
        return Gw(self.root, **kw)


@pytest.fixture()
def repo(tmp_path, monkeypatch):
    """真 git 仓：被测镜像 + 存活源 + 对照镜像 + 注册表（裁定登记表按需由 _grant 写入）。"""
    import ops_guard

    root = tmp_path / "wt"
    root.mkdir()
    r = Repo(root)
    r.git("init", "-q", "-b", "main")
    r.git("config", "user.email", "t@t")
    r.git("config", "user.name", "t")
    r.git("config", "commit.gpgsign", "false")

    r.write(MIRROR_REL, _MIRROR_TEXT)
    r.write(SOT_REL, _SOT_TEXT)
    r.write(KEEP_MIRROR_REL, _MIRROR_TEXT.replace(SOT_REL, KEEP_SOT_REL))
    r.write(KEEP_SOT_REL, _SOT_TEXT)
    r.write(REGISTRY_REL, registry_text([MIRROR_REL, KEEP_MIRROR_REL]))
    r.commit("init: mirrors + live sources")

    monkeypatch.setattr(ops_guard, "_PROJECT_ROOT_CACHE", root)
    return r


def _retire_source(r: Repo) -> None:
    r.git("rm", "-q", SOT_REL)
    r.git("commit", "-q", "-m", "retire source")


def _grant(r: Repo, *, status: str = "active", target: str = MIRROR_REL, ruling: str = "裁定#901") -> None:
    r.write(RULING_REL, rulings_text(ruling, status=status, target=target))
    r.commit(f"ruling {ruling} {status}")


def census(r: Repo) -> dict:
    gw = r.gw()
    tree = rev._head_tree_files(gw)
    assert tree is not None
    return rev._classify(gw, tree)


# ── 判据面：正反向对照 ──


def test_live_source_is_not_orphan(repo):
    c = census(repo)
    assert c["scanned"] == 2
    assert c["orphans"] == []
    assert c["broken_source_references"] == []


def test_retired_source_makes_reverse_orphan(repo):
    _retire_source(repo)
    c = census(repo)
    assert [o["mirror"] for o in c["orphans"]] == [MIRROR_REL]
    assert c["orphans"][0]["source_of_truth"] == SOT_REL
    assert len(c["orphans"][0]["retired_by"]) >= 7


def test_missing_source_of_truth_key_is_never_judged_orphan(repo):
    repo.write(MIRROR_REL, "# no sot here\ndoc_type: architecture_view\nttl: permanent\n")
    repo.commit("drop sot key")
    _retire_source(repo)
    c = census(repo)
    assert c["orphans"] == []
    assert c["unreadable"] == 1


def test_source_never_tracked_goes_to_broken_bucket(repo):
    repo.write(MIRROR_REL, _MIRROR_TEXT.replace(SOT_REL, "src/zephyr/infrastructure/ghost/__init__.py"))
    repo.commit("point at path that never existed")
    c = census(repo)
    assert c["orphans"] == []
    assert [b["mirror"] for b in c["broken_source_references"] if b.get("reason") == "never_tracked"] == [MIRROR_REL]


def test_live_reverse_anchor_vetoes_orphan(repo):
    repo.write("src/zephyr/infrastructure/keel/__init__.py", f'"""keel."""\n# [ALGO_FLOW] external: {MIRROR_REL}\n')
    repo.commit("anchor still references mirror")
    _retire_source(repo)
    c = census(repo)
    assert c["orphans"] == []
    assert any(b.get("reason") == "reverse_anchor_alive" for b in c["broken_source_references"])


def test_head_tree_failure_degrades_to_warn(repo):
    class _BrokenGw(Gw):
        def run_git(self, cmd):
            return subprocess.CompletedProcess(cmd, 128, "", "boom")

    result = rev._reconcile(_BrokenGw(repo.root), [str(repo.root / "src/zephyr/a.py")], "st-test")
    assert result.action == "warn"
    assert "ls-tree" in result.detail


def test_reconcile_critical_warn_names_owner_gate(repo):
    _retire_source(repo)
    result = rev._reconcile(repo.gw(), [str(repo.root / SOT_REL)], "st-test")
    assert result.action == "critical_warn"
    assert MIRROR_REL in result.detail
    assert "裁定#307" in result.detail
    assert "--apply" in result.detail  # 报了必须给出可执行出口
    report = sorted((repo.root / ".runtime" / "reconcile_reports").glob("algo_flow_reverse_orphan_*.json"))
    assert report and MIRROR_REL in report[-1].read_text(encoding="utf-8")


def test_reconcile_clean_when_no_orphan(repo):
    result = rev._reconcile(repo.gw(), [str(repo.root / SOT_REL)], "st-test")
    assert result.action == "clean"
    assert "普查 2 件" in result.detail


# ── 触发面（含 linked worktree 锚定钉）──


def test_trigger_fires_on_src_py_and_mirrors(repo):
    assert rev._should_trigger(repo.root, [str(repo.root / "src/zephyr/x.py")])
    assert rev._should_trigger(repo.root, [str(repo.root / MIRROR_REL)])
    assert not rev._should_trigger(repo.root, [str(repo.root / "docs/02_enterprise_architecture/readme.md")])


def test_trigger_resolves_against_gateway_root_not_default_root():
    """#ARCH-324 同型坑：committed 绝对路径锚在 linked worktree，用默认根相对化会失败→静默不触发。"""
    other = Path("D:/elsewhere/.runtime/commit_queue/worktree")
    assert rev._should_trigger(other, [str(other / "src/zephyr/x.py")])
    assert not rev._should_trigger(Path("D:/ZephyrAlpha"), [str(other / "src/zephyr/x.py")])


def test_spec_declares_read_only_file_ops(repo):
    """检测面绝不自动持有退役能力（裁定#307①）——file_ops 被加宽时本钉必须红。"""
    spec = rev.make_algo_flow_reverse_orphan_reconciler(repo.gw())
    assert spec.gate_id == "GATE-ALGO-FLOW-REVERSE-ORPHAN"
    assert spec.priority == 245
    assert spec.file_ops == frozenset({"read"})


# ── 退役面：Owner 门位机判 ──


def test_retire_refuses_when_ruling_registry_absent(repo):
    _retire_source(repo)
    with pytest.raises(rev.RetireRefused, match="裁定登记表不可读"):
        rev.retire_orphan(repo.gw(), MIRROR_REL, owner_ruling="901")
    assert (repo.root / MIRROR_REL).is_file()
    assert MIRROR_REL in repo.read(REGISTRY_REL)


def test_retire_refuses_without_ruling_recorded(repo):
    _retire_source(repo)
    _grant(repo, ruling="裁定#888")
    with pytest.raises(rev.RetireRefused, match="未登记"):
        rev.retire_orphan(repo.gw(), MIRROR_REL, owner_ruling="901")
    assert (repo.root / MIRROR_REL).is_file()


def test_retire_refuses_when_ruling_does_not_name_this_mirror(repo):
    _retire_source(repo)
    _grant(repo, target="docs/03_modules/_domain_x/algo_flow/other/other__init__.yaml")
    with pytest.raises(rev.RetireRefused, match="未点名"):
        rev.retire_orphan(repo.gw(), MIRROR_REL, owner_ruling="901")
    assert (repo.root / MIRROR_REL).is_file()


def test_retire_refuses_when_ruling_is_not_active(repo):
    _retire_source(repo)
    _grant(repo, status="superseded")
    with pytest.raises(rev.RetireRefused, match="非 active"):
        rev.retire_orphan(repo.gw(), MIRROR_REL, owner_ruling="901")


def test_grant_check_speaks_real_registry_schema():
    """真源 schema 钉：fixture 自造键名会让全例绿而真仓 --apply 恒判"未登记"。

    2026-09-18 05:55 实证：本件 fixture 原写 rulings: 根键，真源 ruling_registry.yaml
    实为 entries:——检测面全绿、门位机判在真仓永远拒授权（假绿 + 假拒双向失真）。
    判据必须"真表里存在的授权裁定问得出结果"，只断言文件结构不算钉。
    """
    real = _REPO_ROOT / RULING_REL
    if not real.is_file():
        pytest.skip("真仓裁定登记表不在检出内")
    data = yaml.safe_load(real.read_text(encoding="utf-8"))
    entries = [e for e in (data.get("entries") or []) if isinstance(e, dict)]
    assert entries
    donor = next(
        (
            e
            for e in entries
            if str(e.get("status", "")).strip() == "active"
            and any(isinstance(p, str) and "/" in p for p in (e.get("affected_files") or []))
        ),
        None,
    )
    assert donor is not None, "真表里找不到一条 active 且点名文件的裁定——判据无从校验"
    target = next(p for p in donor["affected_files"] if isinstance(p, str) and "/" in p)

    class _RealGw:
        project_root = _REPO_ROOT

    gw = _RealGw()
    rid = str(donor["ruling_id"])
    assert rev.assert_owner_grant(gw, target, rid.removeprefix("裁定#")) == rid
    with pytest.raises(rev.RetireRefused, match="未登记"):
        rev.assert_owner_grant(gw, "docs/_no_such_mirror.yaml", "999999")


def test_retire_refuses_on_unconfirmed_orphan(repo):
    _grant(repo)
    with pytest.raises(rev.RetireRefused, match="不在本次复核"):
        rev.retire_orphan(repo.gw(), MIRROR_REL, owner_ruling="901")
    assert (repo.root / MIRROR_REL).is_file()


def test_retire_dry_run_writes_nothing(repo):
    _retire_source(repo)
    _grant(repo)
    before = (repo.root / REGISTRY_REL).read_bytes()
    out = rev.retire_orphan(repo.gw(), MIRROR_REL, owner_ruling="901", dry_run=True)
    assert out["dry_run"] is True
    assert out["creation_tokens_before"] == 2
    assert (repo.root / REGISTRY_REL).read_bytes() == before
    assert (repo.root / MIRROR_REL).is_file()
    assert not (repo.root / ".runtime" / "recycle_bin").exists()


def test_retire_recycles_mirror_and_shrinks_registry(repo):
    _retire_source(repo)
    _grant(repo)
    out = rev.retire_orphan(repo.gw(), MIRROR_REL, owner_ruling="901", commit=False)

    # 镜像永不物理删除：回收站里可恢复
    assert not (repo.root / MIRROR_REL).is_file()
    recycled = sorted((repo.root / ".runtime" / "recycle_bin").rglob("mod__init__.yaml"))
    assert recycled and repo.root / out["recycled_to"] == recycled[0]

    data = yaml.safe_load(repo.read(REGISTRY_REL))
    files = [e["file"] for e in data["creation_tokens"]]
    assert MIRROR_REL not in files and files == [KEEP_MIRROR_REL.replace("\\", "/")]
    assert list(data.keys())[-1] == "di_seam_exemptions"
    assert out["creation_tokens_after"] == 1


def test_retire_twice_refuses_second_time(repo):
    _retire_source(repo)
    _grant(repo)
    rev.retire_orphan(repo.gw(), MIRROR_REL, owner_ruling="901", commit=False)
    with pytest.raises(rev.RetireRefused, match="不在本次复核"):
        rev.retire_orphan(repo.gw(), MIRROR_REL, owner_ruling="901", commit=False)


def test_retire_rolls_back_registry_when_struct_broken(repo):
    """写后自检必拦结构走样并回滚（走真实分支，不 mock 自检本体）。

    构造：注册表末位顶层键不是 di_seam_exemptions → 摘条后自检报警 → 回滚写前文本。
    """
    _retire_source(repo)
    _grant(repo)
    repo.write(REGISTRY_REL, registry_text([MIRROR_REL, "x.yaml"], tail_key="extra_tail"))
    repo.commit("registry with non-tail di_seam")
    before = (repo.root / REGISTRY_REL).read_bytes()

    with pytest.raises(rev.RetireRefused, match="写后自检不过"):
        rev.retire_orphan(repo.gw(), MIRROR_REL, owner_ruling="901", commit=False)
    assert (repo.root / REGISTRY_REL).read_bytes() == before


def test_registry_removal_refuses_ambiguous_anchor():
    entry = f"- file: {MIRROR_REL}\n  token: tok\n  created_by: c\n  capability: k\n"
    dup = f"creation_tokens:\n{entry}{entry}di_seam_exemptions: []\n"
    with pytest.raises(rev.RetireRefused, match="命中 2 条"):
        rev._registry_removal(dup, MIRROR_REL)
    absent = f"creation_tokens:\n- file: other.yaml\n  token: tok\ndi_seam_exemptions: []\n"
    with pytest.raises(rev.RetireRefused, match="命中 0 条"):
        rev._registry_removal(absent, MIRROR_REL)
    out, removed = rev._registry_removal(f"creation_tokens:\n{entry}di_seam_exemptions: []\n", MIRROR_REL)
    assert removed == 4 and MIRROR_REL not in out


def test_retire_commit_message_carries_governance_markers(repo):
    _retire_source(repo)
    _grant(repo)
    gw = repo.gw()
    rev.retire_orphan(gw, MIRROR_REL, owner_ruling="901", session_id="st-reverse-orphan")
    session_id, files, message = gw.commits[0]
    assert session_id == "st-reverse-orphan"
    assert any(f.endswith("mod__init__.yaml") for f in files)
    assert any(f.endswith("capability_canonical_file_registry.yaml") for f in files)
    assert "[allow-mass-deletion:裁定#901" in message  # 注册表净删必须带逃生钉
    assert "[RULING-REFERENCE: 裁定#901]" in message


def test_retire_lands_deletion_through_real_commit(repo):
    """deletion 经 _commit_auto 的 pathspec add 真实落地（HEAD 树与注册表同步收敛）。"""
    _retire_source(repo)
    _grant(repo)
    gw = repo.gw(commit_shell=True)
    out = rev.retire_orphan(gw, MIRROR_REL, owner_ruling="901", session_id="st-reverse-orphan")
    assert out["commit_status"] == "OK", out
    assert gw.run_git(["git", "ls-files", "--", MIRROR_REL]).stdout.strip() == ""
    assert MIRROR_REL not in gw.run_git(["git", "show", f"HEAD:{REGISTRY_REL}"]).stdout
    assert KEEP_MIRROR_REL in gw.run_git(["git", "show", f"HEAD:{REGISTRY_REL}"]).stdout


# ── 机制钉：不 mock 自身的 CAS ──


def test_safe_write_text_refuses_stale_base(repo):
    """本件依赖的并发覆盖防线必须真实生效（不 mock 被测机制）。"""
    from zephyr.shared.io.file_utils import StaleWriteRefused, content_sha256, safe_write_text

    target = repo.root / REGISTRY_REL
    stale = content_sha256("whatever-was-read-before")
    target.write_text(repo.read(REGISTRY_REL) + "\n# foreign touched it\n", encoding="utf-8")
    with pytest.raises(StaleWriteRefused):
        safe_write_text(target, "new content", expected_base_sha256=stale, repo_root=str(repo.root), newline="")


# ── 变异证明：逐条撤掉承重护栏，判据必须失守（证明护栏承重，不是 fixture 巧合）──


def test_mutation_reverse_anchor_veto_is_load_bearing(repo, monkeypatch):
    repo.write("src/zephyr/infrastructure/keel/__init__.py", f'"""keel."""\n# [ALGO_FLOW] external: {MIRROR_REL}\n')
    repo.commit("anchor still references mirror")
    _retire_source(repo)
    assert census(repo)["orphans"] == []  # 护栏在场：否决
    monkeypatch.setattr(rev, "_reverse_anchored", lambda gw, rel: False)
    assert [o["mirror"] for o in census(repo)["orphans"]] == [MIRROR_REL]  # 撤护栏：误判孤件


def test_mutation_history_guard_is_load_bearing(repo, monkeypatch):
    repo.write(MIRROR_REL, _MIRROR_TEXT.replace(SOT_REL, "src/zephyr/infrastructure/ghost/__init__.py"))
    repo.commit("point at path that never existed")
    assert census(repo)["orphans"] == []
    monkeypatch.setattr(rev, "_touching_commits", lambda gw, rel, extra: "0" * 40)
    assert [o["mirror"] for o in census(repo)["orphans"]] == [MIRROR_REL]  # 撤历史核验：幻觉退役提交也被当真


def test_mutation_owner_grant_is_load_bearing(repo, monkeypatch):
    _retire_source(repo)  # 无授权裁定
    with pytest.raises(rev.RetireRefused):
        rev.retire_orphan(repo.gw(), MIRROR_REL, owner_ruling="901", commit=False)
    monkeypatch.setattr(rev, "assert_owner_grant", lambda gw, rel, ref: f"裁定#{ref}")
    out = rev.retire_orphan(repo.gw(), MIRROR_REL, owner_ruling="901", commit=False)
    assert not (repo.root / MIRROR_REL).is_file()  # 撤门位：镜像即被移走（危害实证）
    assert out["creation_tokens_after"] == 1


def test_mutation_post_write_check_is_load_bearing(repo, monkeypatch):
    _retire_source(repo)
    _grant(repo)
    repo.write(REGISTRY_REL, registry_text([MIRROR_REL, "x.yaml"], tail_key="extra_tail"))
    repo.commit("registry with non-tail di_seam")
    monkeypatch.setattr(rev, "_registry_post_write_issues", lambda text, rel, n: [])
    rev.retire_orphan(repo.gw(), MIRROR_REL, owner_ruling="901", commit=False)
    data = yaml.safe_load(repo.read(REGISTRY_REL))
    assert list(data.keys())[-1] != "di_seam_exemptions"  # 撤自检：结构走样静默入库


def test_apply_command_is_copy_pasteable(repo):
    cmd = rev._apply_command(MIRROR_REL)
    assert "--apply" in cmd and "--owner-ruling" in cmd and MIRROR_REL in cmd
