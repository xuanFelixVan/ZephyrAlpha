# [MODULE] tests.governance.rule_bridge.test_worktree_drift_watchdog_redteam_injection
# [DOMAIN] D_GOV_ENFORCEMENT
# [MATURITY] production
# [TTL] permanent
"""#ARCH-308 A2 派生自动收敛——红队注入/绕过攻击测试（2026-09-03）。

攻击面：`_auto_commit_derived` 的五重安全边界（零会话在场 / B类白名单 /
稳定窗 / protected_paths / index.lock）与白名单加载器 `_load_allowlist_b_class`、
匹配器 `_match_allowlist` 的注入/绕过面。

场景矩阵：
- R2.1 白名单路径穿越条目（../../etc/passwd）——验证穿越路径进不了候选集
- R2.2 保护路径伪装 B 类（AGENTS.md 入白名单）——验证 protected_paths 闸兜底
- R2.3 B 类路径写恶意内容——验证攻击面边界=白名单自身安全（设计内信任）
- R2.4 fnmatch 模式越界——验证 `*` 是否跨目录（防误配语义确认）
- R2.5 白名单 entry 缺 class 字段——验证不收录（fail-closed）
- R2.6 白名单损坏 YAML——验证返回空（自动提交面关闭）
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

import zephyr.gov_enforcement.rule_bridge.worktree_drift_watchdog as wd


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=str(repo),
        check=True,
        capture_output=True,
        text=True,
    )


def _commit(repo: Path, msg: str) -> None:
    _git(
        repo,
        "-c",
        "user.email=t@t",
        "-c",
        "user.name=t",
        "-c",
        "core.autocrlf=false",
        "commit",
        "-q",
        "-m",
        msg,
    )


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    """临时 git 仓库：含一个已提交 tracked 文件 hot.txt。"""
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "data" / "databases").mkdir(parents=True)  # reconcile_execution_log 落库目录
    _git(repo, "init", "-q", "-b", "dev")
    _git(
        repo,
        "-c",
        "user.email=t@t",
        "-c",
        "user.name=t",
        "-c",
        "core.autocrlf=false",
        "commit",
        "--allow-empty",
        "-q",
        "-m",
        "init",
    )
    (repo / "hot.txt").write_text("v1\n", encoding="utf-8")
    _git(repo, "add", "hot.txt")
    _commit(repo, "add hot")
    return repo


class _FakeCommitResult:
    def __init__(self, status: str = "OK", commit_hash: str = "abc123") -> None:
        self.status = status
        self.commit_hash = commit_hash


class _CaptureGW:
    """捕获 _commit_auto 调用的假网关（不真正提交）。"""

    calls: list[tuple] = []

    def __init__(self, project_root=None, registry=None) -> None:  # noqa: ANN001
        pass

    def _commit_auto(self, sid, files, msg):  # noqa: ANN001
        type(self).calls.append((sid, list(files), msg))
        return _FakeCommitResult()


@pytest.fixture
def capture_gateway(monkeypatch) -> type[_CaptureGW]:
    _CaptureGW.calls = []
    monkeypatch.setattr(
        "zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway", _CaptureGW
    )
    return _CaptureGW


_ALLOWLIST_REL = wd._TRACKED_WRITE_ALLOWLIST_REL


def _write_allowlist(repo: Path, body: str) -> Path:
    p = repo / _ALLOWLIST_REL
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")
    return p


# ── R2.1：白名单路径穿越条目 ──────────────────────────────────────────────────


def test_r21_traversal_entry_never_enters_candidates(git_repo: Path, monkeypatch, capture_gateway) -> None:
    """白名单塞入 ../../etc/passwd：穿越路径根本进不了 A2 候选集，零提交。

    攻击假设：若 allowlist exact 集含仓外路径，A2 可能 git add 仓外文件。
    防御机理：候选来源唯一 = `git status --porcelain`（_dirty_tracked），
    git 只会报告仓内 tracked 路径——白名单匹配发生在 dirty 清单**之后**，
    穿越条目永远匹配不到任何候选。
    """
    monkeypatch.setattr(wd, "_load_allowlist_b_class", lambda root: ({"../../etc/passwd"}, []))
    (git_repo / "hot.txt").write_text("dirty\n", encoding="utf-8")  # 仓内有脏文件作对照

    # 匹配器本身会命中穿越串（若它能到达匹配器的话）——证明拦截点在候选来源
    assert wd._match_allowlist("../../etc/passwd", {"../../etc/passwd"}, []) is True
    # 但 _dirty_tracked 的全部输出恒为仓内相对路径
    dirty = wd._dirty_tracked(git_repo)
    assert dirty, "前置：仓内必须有脏文件作攻击载体对照"
    for rel in dirty:
        assert not rel.startswith(".."), rel
        assert (git_repo / rel).resolve().is_relative_to(git_repo.resolve()), rel

    s1 = wd._auto_commit_derived(git_repo)
    s2 = wd._auto_commit_derived(git_repo)
    assert s1["committed"] == 0 and s1["candidates"] == 0, s1
    assert s2["committed"] == 0 and s2["candidates"] == 0, s2
    assert capture_gateway.calls == [], "穿越条目绝不得触达提交通道"


# ── R2.2：保护路径伪装 B 类 ──────────────────────────────────────────────────


def test_r22_protected_path_in_b_allowlist_still_blocked(git_repo: Path, monkeypatch, capture_gateway) -> None:
    """攻击者把 AGENTS.md 塞进 B 类白名单：protected_paths 闸④必须兜底拦截。

    白名单与 protected_paths 是两套独立真源——即使白名单被污染（误配/注入），
    保护路径仍留人工审批通道，自动提交永不碰。本场景走**真实** find_protected_hits。
    """
    from zephyr.gov_enforcement.commit_gates.protected_paths_gate import find_protected_hits

    assert find_protected_hits(["AGENTS.md"]), "前置：真实保护清单必须覆盖 AGENTS.md"

    (git_repo / "AGENTS.md").write_text("rules-v1\n", encoding="utf-8")
    _git(git_repo, "add", "AGENTS.md")
    _commit(git_repo, "add agents")
    # 攻击载荷：白名单污染（AGENTS.md 被标为 B 类派生）
    monkeypatch.setattr(wd, "_load_allowlist_b_class", lambda root: ({"AGENTS.md"}, []))
    (git_repo / "AGENTS.md").write_text("rules-PWNED\n", encoding="utf-8")

    wd._auto_commit_derived(git_repo)  # 第一周期登记候选
    s = wd._auto_commit_derived(git_repo)  # 第二周期稳定——但必须被保护闸拦下
    assert s["committed"] == 0 and s["skipped_protected"] >= 1, s
    assert capture_gateway.calls == [], "保护路径绝不得进入提交通道"
    # 再多跑几轮也不得有漏网
    for _ in range(2):
        s = wd._auto_commit_derived(git_repo)
        assert s["committed"] == 0 and s["skipped_protected"] >= 1, s


# ── R2.3：B 类路径写恶意内容（设计内信任边界实测）─────────────────────────────


def test_r23_malicious_content_in_b_class_is_committed_by_design(
    git_repo: Path, monkeypatch, capture_gateway
) -> None:
    """B 类白名单文件写入恶意内容：A2 会照单提交——攻击面边界=白名单自身安全。

    本测试固化该信任边界：A2 对 B 类内容零审查（这是设计，非漏洞）——
    白名单是 tracked 真源，改它必须过 commit 门禁。同时验证该文件确实不在
    真实保护清单（否则本场景退化为 R2.2），边界刻画才成立。
    """
    from zephyr.gov_enforcement.commit_gates.protected_paths_gate import find_protected_hits

    rel = "scripts/governance/script_manifest.yaml"
    assert find_protected_hits([rel]) == [], "前置：该 B 类文件必须不在保护清单"

    target = git_repo / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("scripts: []\n", encoding="utf-8")
    _git(git_repo, "add", rel)
    _commit(git_repo, "add manifest")

    monkeypatch.setattr(wd, "_load_allowlist_b_class", lambda root: ({rel}, []))
    malicious = "scripts: []\nimport os\nos.system('echo pwned')\n"
    target.write_text(malicious, encoding="utf-8")

    s1 = wd._auto_commit_derived(git_repo)
    assert s1["committed"] == 0 and s1["candidates"] == 1, s1  # 稳定窗未达
    s2 = wd._auto_commit_derived(git_repo)
    assert s2["committed"] == 1 and s2["skipped_protected"] == 0, s2
    # 提交通道收到的正是恶意内容文件（绝对路径、原样内容）
    assert len(capture_gateway.calls) == 1
    sid, files, _msg = capture_gateway.calls[0]
    assert sid == wd._AUTO_DERIVED_SESSION
    assert files == [str(git_repo / rel)]
    assert Path(files[0]).read_text(encoding="utf-8") == malicious
    # 结论锚点：A2 防线=白名单+protected_paths+稳定窗，内容审查不在其内


# ── R2.4：fnmatch 模式越界（语义确认，防误配）─────────────────────────────────


def test_r24_fnmatch_star_must_not_cross_directory_boundary() -> None:
    """`docs/*` 不得命中 `docs/03_modules/x/blueprint.md`（只许 `**` 模式命中深层）。

    安全预期：白名单维护者写 `docs/*` 时意图=仅直接子级；若 fnmatch 的 `*`
    跨目录分隔符，则任何浅层模式都会把整棵子树纳入 A2 自动提交面——
    误配即扩大攻击面（白名单虽过门禁，但评审者按 glob 直觉审不出越界）。
    """
    deep = "docs/03_modules/x/blueprint.md"
    shallow = "docs/a.md"
    # `**` 模式命中深层路径——预期内
    assert wd._match_allowlist(deep, set(), ["docs/**/*.md"]) is True
    # `*` 模式命中直接子级——预期内
    assert wd._match_allowlist(shallow, set(), ["docs/*"]) is True
    # 安全关键断言：`*` 绝不得跨目录命中深层路径（否则浅层模式=整棵子树）
    assert wd._match_allowlist(deep, set(), ["docs/*"]) is False, (
        "漏洞：fnmatch 的 `*` 跨目录分隔符——`docs/*` 实际命中整棵 docs/ 子树，"
        "白名单浅层模式误配将把深层文件纳入 A2 自动提交面"
    )
    # 同理：`scripts/*` 不得命中 scripts/governance/x
    assert wd._match_allowlist("scripts/governance/x.yaml", set(), ["scripts/*"]) is False, (
        "漏洞：fnmatch `*` 越界（scripts 子树）"
    )


# ── R2.5：白名单 entry 缺 class 字段 ──────────────────────────────────────────


def test_r25_entry_without_class_not_loaded(git_repo: Path, capture_gateway) -> None:
    """entry 只有 path 没有 class → 不得收录进 B 类面（fail-closed 分类）。

    攻击假设：若缺省 class 被宽容处理为 B，攻击者可提交一个"忘了写 class"的
    entry 绕过分类审查。同时验证 class=A 不收、class=b 小写归一后收。
    """
    _write_allowlist(
        git_repo,
        "entries:\n"
        "  - path: nocls.txt\n"  # 缺 class → 不得收录
        "  - path: hot.txt\n"
        "    class: A\n"  # A 类 → 不得收录
        "  - path: lower.txt\n"
        "    class: b\n"  # 小写 b → 归一后收录
        "  - path: upper.txt\n"
        "    class: B\n",  # 标准 B → 收录
    )
    exact, patterns = wd._load_allowlist_b_class(git_repo)
    assert "nocls.txt" not in exact, "缺 class 的 entry 绝不得入 B 类面"
    assert "hot.txt" not in exact, "class=A 不得入 B 类面"
    assert {"lower.txt", "upper.txt"} <= exact
    assert patterns == []

    # 功能验证：缺 class 的文件即使有脏漂移也绝不进入自动提交
    (git_repo / "nocls.txt").write_text("v1\n", encoding="utf-8")
    _git(git_repo, "add", "nocls.txt")
    _commit(git_repo, "add nocls")
    (git_repo / "nocls.txt").write_text("v2-pwn\n", encoding="utf-8")
    s1 = wd._auto_commit_derived(git_repo)
    s2 = wd._auto_commit_derived(git_repo)
    assert s1["committed"] == 0 and s2["committed"] == 0, (s1, s2)
    assert capture_gateway.calls == []


# ── R2.6：白名单损坏 YAML ────────────────────────────────────────────────────


def test_r26_broken_yaml_fails_closed(git_repo: Path, capture_gateway) -> None:
    """白名单文件为非法 YAML → 加载返回空 → 自动提交面整体关闭（fail-closed）。

    攻击假设：损坏/畸形 YAML 若被宽容解析出部分 entry，攻击面不可预期。
    防御要求：解析异常=零白名单=零自动提交（不告警崩溃、不部分收录）。
    """
    _write_allowlist(git_repo, "entries:\n  - path: hot.txt\n    class: B\n  - [unclosed\n\t:\n")
    exact, patterns = wd._load_allowlist_b_class(git_repo)
    assert exact == set() and patterns == [], "损坏 YAML 必须解析为空（fail-closed）"

    (git_repo / "hot.txt").write_text("dirty\n", encoding="utf-8")
    s1 = wd._auto_commit_derived(git_repo)
    s2 = wd._auto_commit_derived(git_repo)
    assert s1["committed"] == 0 and s1["candidates"] == 0, s1
    assert s2["committed"] == 0 and s2["candidates"] == 0, s2
    assert capture_gateway.calls == []
