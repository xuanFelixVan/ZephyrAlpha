# [MODULE] tests.governance.rule_bridge.test_session_worktree_merge_preflight
# [DOMAIN] D_GOV_CODE_QUALITY
# [TTL] permanent
# [DEPENDENCIES] scripts.session_worktree (_merge_preflight_issues/cmd_merge)；
#   zephyr.gov_enforcement.commit_gates.registry_yaml_parse_gate（判据真源，单口复用）
# [CONSUMERS] pytest（tests/governance/rule_bridge/）
# [STARTUP] imported
# [MATURITY] production
# [BLUEPRINT] MOD-INF-037 | docs/03_modules/_domain_governance/registry_governance/blueprint.md | §W-M1
# [INVARIANTS] 本文件只验 merge 通道补检：结构红判必拦、健康必放、未触碰不连坐、
#   补检不可执行默认同样拦（越权须显式旗）；判据本体由 test_registry_yaml_parse_gate.py 负责
# [MODIFY-GUARD] 新建 2026-10-10 st-maint1-20261010（维护一班 T1 件③红证）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败=防线缺失；永不 skip（tmp git 仓不可用时 raise，禁静默放行）
# [TESTS] 本文件即测试
"""merge 通道补检红蓝对抗测试（A-14，st-maint1-20261010 件③）。

背景（2026-10-10 实弹）：`git merge` 结构性不触发 pre-commit hooks，且
validate_commit_gateway 明记"合并提交放行"——两条叠加使 merge 成为门禁零覆盖通道。
一枚 R5 投影同步袋经此通道把"顶层 di_seam_exemptions 键缺失"的剥光 CAP 册烤进 dev
（e0c72f63c4），随后全仓新建件入库被 REGISTRY-YAML-PARSE 同签名熔断连堵 6 次。
本测试钉死"同形 merge 必拦"。
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


def _repo_root() -> Path:
    """从测试文件位置上溯找仓根（禁硬编码 parents[N]——目录搬迁即静默指空）。"""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "scripts" / "session_worktree.py").exists():
            return parent
    raise RuntimeError(f"未从 {here} 上溯到含 scripts/session_worktree.py 的仓根")


_ROOT = _repo_root()
sys.path.insert(0, str(_ROOT / "scripts"))
sys.path.insert(0, str(_ROOT / "src"))

import session_worktree as sw  # noqa: E402

assert str(_ROOT) in str(sw.__file__), f"装载来源非本仓（假绿风险）: {sw.__file__}"

REG_RELPATH = "docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml"

_HEALTHY = """<!-- GENERATED FILE — regenerate: python scripts/governance/registry_projection/registry_projection_generator.py --render -->
unique_key:
  capabilities:
  - capability_id
  creation_tokens:
  - file
  - token
capabilities:
- capability_id: alpha
  description: 甲能力
creation_tokens:
- file: src/alpha.py
  token: alpha-token-20261010
  capability: alpha
di_seam_exemptions: []
"""

# 剥光形态 = 10-10 事故现场：头部 verbatim + 尾部 di_seam_exemptions 一起丢
_STRIPPED = """capabilities:
- capability_id: alpha
  description: 甲能力
creation_tokens:
- file: src/alpha.py
  token: alpha-token-20261010
  capability: alpha
"""


def _git(repo: Path, *args: str) -> str:
    out = subprocess.run(
        ["git", *args],
        cwd=str(repo),
        capture_output=True,
        text=True,
        check=True,
        encoding="utf-8",
    )
    return out.stdout


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    """临时双分支仓：target=dev 持健康册，lane 持剥光册（复刻 R5 袋终态）。"""
    (tmp_path / "src").mkdir(parents=True, exist_ok=True)
    reg = tmp_path / REG_RELPATH
    reg.parent.mkdir(parents=True, exist_ok=True)
    _git(tmp_path, "init", "-b", "dev", ".")
    _git(tmp_path, "config", "user.email", "t@example.com")
    _git(tmp_path, "config", "user.name", "t")
    (tmp_path / "src" / "alpha.py").write_text("print(1)\n", encoding="utf-8")
    reg.write_text(_HEALTHY, encoding="utf-8")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-m", "base: healthy projection")
    return tmp_path


def _make_lane(repo: Path, branch: str, reg_text: str) -> None:
    _git(repo, "checkout", "-b", branch)
    (repo / REG_RELPATH).write_text(reg_text, encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "lane: registry change")
    _git(repo, "checkout", "dev")


def _preflight(repo: Path, target: str, branch: str) -> tuple[list[str], str]:
    """把补检指向临时仓（_run_git 缺省 cwd=模块级 REPO_ROOT）。"""
    old_root = sw.REPO_ROOT
    sw.REPO_ROOT = repo
    try:
        return sw._merge_preflight_issues(target, branch)
    finally:
        sw.REPO_ROOT = old_root


def test_stripped_registry_merge_is_blocked(repo: Path) -> None:
    """红证主案：袋内册缺 di_seam_exemptions → 同形 merge 必拦（10-10 事故形态复现）。"""
    _make_lane(repo, "ai/lane/stripped", _STRIPPED)

    issues, state = _preflight(repo, "dev", "ai/lane/stripped")

    assert state == "checked", f"补检未执行（state={state}）＝防线未装载: {issues}"
    assert issues, "剥光册经 merge 入 dev 未被拦——merge 通道仍是门禁零覆盖面"
    joined = " | ".join(issues)
    assert "di_seam_exemptions" in joined, joined


def test_healthy_registry_merge_passes(repo: Path) -> None:
    """蓝证：健康册合并不受扰动（补检不得成为橡皮图章式乱拦）。"""
    _make_lane(repo, "ai/lane/healthy-touch", _HEALTHY.replace("甲能力", "甲能力改"))

    issues, state = _preflight(repo, "dev", "ai/lane/healthy-touch")

    assert state == "checked"
    assert issues == [], f"健康册被误拦: {issues}"


def test_registry_untouched_by_merge_is_not_guilty(repo: Path) -> None:
    """own-diff 作用域（宪法 §3.1）：本次 merge 未碰该册 → 既有病不连坐本次合并。"""
    _git(repo, "checkout", "-b", "ai/lane/docs-only")
    (repo / "note.md").write_text("only docs\n", encoding="utf-8")
    _git(repo, "add", "note.md")
    _git(repo, "commit", "-m", "lane: docs only")
    _git(repo, "checkout", "dev")

    issues, state = _preflight(repo, "dev", "ai/lane/docs-only")

    assert state == "checked"
    assert issues == [], f"未触碰注册表的合并被连坐: {issues}"


def test_duplicate_root_key_merge_is_blocked(repo: Path) -> None:
    """同判据面第二形：重复根键（PyYAML 静默取后者→前段条目被无感忽略）。"""
    dup = _HEALTHY + "capabilities:\n- capability_id: beta\n  description: 乙能力\n"
    _make_lane(repo, "ai/lane/dupkey", dup)

    issues, state = _preflight(repo, "dev", "ai/lane/dupkey")

    assert state == "checked"
    assert any("根键重复" in i for i in issues), f"重复根键未被拦: {issues}"


def test_conflicted_merge_defers_to_git(repo: Path) -> None:
    """冲突态不抢判：merge-tree rc=1 → state=conflict 且无结构判词（交回 git 正常流程）。"""
    _git(repo, "checkout", "-b", "ai/lane/conflict")
    (repo / "src" / "alpha.py").write_text("print('lane')\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "lane edits alpha")
    _git(repo, "checkout", "dev")
    (repo / "src" / "alpha.py").write_text("print('dev')\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "dev edits alpha")

    issues, state = _preflight(repo, "dev", "ai/lane/conflict")

    assert state == "conflict", state
    assert issues == []


def test_cmd_merge_refuses_before_touching_git(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """端到端：cmd_merge 遇红判必须在**任何 merge 动作之前**返回 1（不是合并后再回滚）。"""
    _make_lane(repo, "ai/lane/stripped2", _STRIPPED)

    calls: list[list[str]] = []
    real_run_git = sw._run_git

    def spy(args, cwd=None, check=True):  # noqa: ANN001 - 透传签名
        calls.append(list(args))
        return real_run_git(args, cwd=cwd, check=check)

    monkeypatch.setattr(sw, "REPO_ROOT", repo)
    monkeypatch.setattr(sw, "WORKTREE_ROOT", repo / ".worktrees")
    monkeypatch.setattr(sw, "_run_git", spy)
    monkeypatch.setattr(sw, "_find_branch_for_session", lambda sid: "ai/lane/stripped2")
    (repo / ".worktrees" / "lane").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(sw, "_worktree_path", lambda sid: repo / ".worktrees" / "lane")

    class _Args:
        session_id = "lane"
        to = "dev"
        squash = False
        yes = True
        allow_unchecked_merge = False

    rc = sw.cmd_merge(_Args())

    assert rc == 1, f"补检红判未阻断（rc={rc}）"
    assert not any(c and c[0] == "merge" for c in calls), f"补检之后仍执行了 merge: {calls}"


def test_unchecked_merge_needs_explicit_flag(repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """『补检不可执行』态默认同样阻断；显式 --allow-unchecked-merge 才放行（且留痕）。"""
    _make_lane(repo, "ai/lane/unavail", _STRIPPED)

    # 让 cmd_merge 能走到补检之后（worktree/分支两道前置检查先满足），
    # 否则它会因"worktree 不存在"提前 return 1——那会让本测试两个断言都通过得没有意义
    (repo / ".worktrees" / "lane").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(sw, "REPO_ROOT", repo)
    monkeypatch.setattr(sw, "WORKTREE_ROOT", repo / ".worktrees")
    monkeypatch.setattr(sw, "_worktree_path", lambda sid: repo / ".worktrees" / "lane")
    monkeypatch.setattr(sw, "_find_branch_for_session", lambda sid: "ai/lane/unavail")
    monkeypatch.setattr(sw, "cmd_abort_inner", lambda sid, **kw: 0)
    monkeypatch.setattr(
        sw,
        "_merge_preflight_issues",
        lambda target, branch: (["merge-tree 不可执行（rc=128）: 人为构造"], "unavailable"),
    )

    class _Args:
        to = "dev"
        session_id = "lane"
        squash = False
        yes = True
        allow_unchecked_merge = False

    assert sw.cmd_merge(_Args()) == 1, "补检不可执行却被静默放行（fail-open 洞）"

    _Args.allow_unchecked_merge = True
    # 越权放行后 merge 真跑：把 git 通道 stub 成"全部成功"，只验判据结论不验 git 结果
    monkeypatch.setattr(sw, "_run_git", lambda args, cwd=None, check=True: subprocess.CompletedProcess(args, 0, "", ""))
    assert sw.cmd_merge(_Args()) == 0, "显式越权旗未生效"
    audit = repo / sw.MERGE_PREFLIGHT_AUDIT_REL
    assert audit.exists(), "越权放行未写审计行"
    body = audit.read_text(encoding="utf-8")
    assert '"bypassed": true' in body, f"审计行未标 bypassed: {body[:200]}"


# ── 生产通道（rule_bridge.session_worktree_merge）同一补检 ────────────────────
# 真实埋雷通道是这条：#ARCH-WORKTREE-PRE-MERGE-SYSPATH-001 把 pre-merge 的 commit gate
# 整体跳过（_PRE_MERGE_SKIP_ALL_COMMIT_GATES=True），CLI 那条只是第二处零覆盖面。
# 两条都必须拦住，否则补检只是把门牌换了个地方挂。


def _load_rule_bridge():
    import importlib

    return importlib.import_module("zephyr.gov_enforcement.rule_bridge.session_worktree")


def test_rule_bridge_channel_blocks_stripped_registry(repo: Path) -> None:
    """生产通道红证：剥光册作为 lane tip 合入 dev 时，结构补检必须给出违规清单。"""
    rb = _load_rule_bridge()

    # 同一临时仓内取两端 rev：dev=健康、lane=剥光（等价于 root=主区 / wt_path=车道，
    # 判据只吃两个 rev 的 merge-tree 数学，不依赖真的存在第二个 worktree）
    _git(repo, "checkout", "-b", "ai/lane/prod")
    (repo / REG_RELPATH).write_text(_STRIPPED, encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "lane: stripped projection (R5 同形)")
    lane_tip = _git(repo, "rev-parse", "HEAD").strip()
    _git(repo, "checkout", "dev")
    dev_tip = _git(repo, "rev-parse", "HEAD").strip()

    real_hidden = rb.run_subprocess_hidden

    # merge-tree/diff/show 走真 git；只把两处 rev-parse 的来源换成受控值
    # （等价于 root=主区 HEAD、wt_path=车道 tip——判据只吃两个 rev 的对象库数学）
    def run_hidden(cmd, **kw):  # noqa: ANN001 - 透传
        c = list(cmd)
        if c[:2] == ["git", "rev-parse"]:
            return subprocess.CompletedProcess(c, 0, dev_tip + "\n", "")
        if c[:3] == ["git", "-C", str(kw.get("cwd"))]:
            return subprocess.CompletedProcess(c, 0, lane_tip + "\n", "")
        return real_hidden(cmd, **kw)

    orig = rb.run_subprocess_hidden
    rb.run_subprocess_hidden = run_hidden
    try:
        issues, state = rb._pre_merge_registry_structure_check(repo, repo)
    finally:
        rb.run_subprocess_hidden = orig

    assert state == "checked", f"补检未执行（state={state}）: {issues}"
    assert issues, "剥光册经生产通道合入未被识别——R5 同形仍零覆盖"
    assert any("di_seam_exemptions" in i for i in issues), issues


def test_rule_bridge_channel_passes_healthy_registry(repo: Path) -> None:
    """蓝证：健康册合入时生产通道零误报（不得把正常 merge 变成拦路）。"""
    rb = _load_rule_bridge()

    _git(repo, "checkout", "-b", "ai/lane/prodok")
    (repo / REG_RELPATH).write_text(_HEALTHY.replace("甲能力", "甲能力ok"), encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "lane: healthy tweak")
    lane_tip = _git(repo, "rev-parse", "HEAD").strip()
    _git(repo, "checkout", "dev")
    dev_tip = _git(repo, "rev-parse", "HEAD").strip()

    real_hidden = rb.run_subprocess_hidden

    def run_hidden(cmd, **kw):  # noqa: ANN001 - 透传
        c = list(cmd)
        if c[:2] == ["git", "rev-parse"]:
            return subprocess.CompletedProcess(c, 0, dev_tip + "\n", "")
        if c[:3] == ["git", "-C", str(kw.get("cwd"))]:
            return subprocess.CompletedProcess(c, 0, lane_tip + "\n", "")
        return real_hidden(cmd, **kw)

    orig = rb.run_subprocess_hidden
    rb.run_subprocess_hidden = run_hidden
    try:
        issues, state = rb._pre_merge_registry_structure_check(repo, repo)
    finally:
        rb.run_subprocess_hidden = orig

    assert state == "checked", state
    assert issues == [], f"健康册被误拦: {issues}"
