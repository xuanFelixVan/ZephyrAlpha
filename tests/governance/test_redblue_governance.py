# [A_test] module_id: MOD-GOV_redblue_governance | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-005 | docs/03_modules/_domain_governance/blueprint.md | §git-hooks,§gate-cache,§commit-queue
# [MODULE] tests.governance.test_redblue_governance
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; subprocess(git/bash); scripts/governance/git_hooks/{reference_transaction_guard,post_commit_guard}.sh; zephyr.gov_enforcement.rule_bridge.gate_cache_preflight; scripts.commit_queue
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/governance/test_redblue_governance.py
# [MATURITY] testing
# [INVARIANTS] 全部攻击/重放在一次性 tmp_path 沙盘仓与 tmp 队列根（永不触生产 .runtime/commit_queue、主区 index、生产钩子）；
#              场景④三伪造形态必须 exit 1 或落审计；剥钩红证证明"拦/审计"出自钩子本身；
#              场景⑤缓存键=own blob sha（own 变→miss/他人动→hit/mtime 变→miss/畸形→None 不崩/TTL 过→miss）；
#              场景⑥ 120 件在 _HEAD_SCAN_BOUND=400 界内：B4 created_at FIFO/interactive 不被 machine 洪灌饿死/B5 attempts 退避让位。
# [MODIFY-GUARD] st-commitspeed-tbl-20260924 红蓝车道 csx-s1（2026-09-25）：本文件是场景④⑤⑥的攻面回归钉；
#                改 reference_transaction_guard.sh/post_commit_guard.sh 孪生段、GateResultCache._path 键公式、
#                _pick_head 排序键任一处 MUST 同步本文件。
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败；bash 不可用 → 场景④直跑组 skip
# [TESTS] 本文件
# [TTL] permanent
"""test_redblue_governance.py — 提交链红蓝对抗场景④⑤⑥回归钉（治理组，csx-s1）

三场景（每场景 ≥2 测试，全沙盘隔离，先红证后钉绿）：

场景④ 红方伪造 [GW:]/绕门
  - 三伪造形态 bash 直跑 reference_transaction_guard.sh（合成 stdin）：
    未注册 sid / 注册表字段名当 sid → 必须 exit 1+block 审计；
    冒充在活他人 sid → 修复前静默通过（实测病根，★ 残余风险②），
    本车道把静默面收窄为 warn_only 审计（violation=gw_sid_channel_unverifiable），
    归属级治本（HMAC 载体）仍待总包裁定——测试钉"exit 1 **或**落审计"。
  - commit-tree+update-ref 绕 pre-commit：hook 链必须拦；剥钩重放必须能落
    （红证：证明拦截出自 reference-transaction 钩子，尺有判别力）。
  - [GW:sid:emergency] 逃生道：放行但必须落 unregistered_gw_sid 审计；
    剥钩重放同形落库且无审计（红证：审计出自钩子）。

场景⑤ GateResultCache 缓存投毒与失效（T7 键=own blob sha 合集）
  own staged 内容改→miss；他人向 index 塞文件（write-tree 全树 sha 必变，
  测试内实证）→仍 hit；config/flags.yaml mtime 变→miss；缓存 JSON 畸形→
  lookup 返 None 不崩；TTL（600s）过期→miss。

场景⑥ 超顶大批与队首饿死（tmp 队列根 120 件 pending，< _HEAD_SCAN_BOUND=400）
  最老件（created_at 最早、qid 字典序垫底）必须被选中（B4 FIFO）；
  1 interactive+119 machine 洪灌→interactive 优先不饿死（machine 饿死逃逸
  30min 双向护栏同测）；attempts≥3 毒药件排队键退避让位不永久霸占（B5），
  开关关闭回退现行为（off 态如实钉档）。
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest

import scripts.commit_queue as cq  # noqa: E402
from zephyr.gov_enforcement.rule_bridge import gate_cache_preflight as gcp  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOKS = REPO_ROOT / "scripts" / "governance" / "git_hooks"
REF_TX = HOOKS / "reference_transaction_guard.sh"
POST_COMMIT = HOOKS / "post_commit_guard.sh"

VICTIM_SID = "st-csx-victim-lane"  # 注册表中在活的他人会话（被冒充对象）
FORGER_SID = "sess-forger-777"  # 未注册 sid（伪造者自有命名）
EMERGENCY_SID = "sess-emerg-911"  # 未注册但走 emergency 逃生


def _now() -> datetime:
    return datetime.now(timezone.utc).astimezone()


def _iso(dt: datetime) -> str:
    return dt.isoformat()


def _git(repo: Path, *args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    e = {
        **os.environ,
        "GIT_AUTHOR_NAME": "t",
        "GIT_AUTHOR_EMAIL": "t@t",
        "GIT_COMMITTER_NAME": "t",
        "GIT_COMMITTER_EMAIL": "t@t",
    }
    if env:
        e.update(env)
    return subprocess.run(
        ["git", *args], cwd=str(repo), capture_output=True, text=True, encoding="utf-8", errors="replace", env=e
    )


def _git_ok(repo: Path, *args: str, env: dict | None = None) -> str:
    r = _git(repo, *args, env=env)
    assert r.returncode == 0, f"git {' '.join(args)} 失败: {r.stdout}{r.stderr}"
    return r.stdout.strip()


# ---------------------------------------------------------------------------
# 沙盘仓 fixture（一次性 tmp 仓；注册表=SessionRegistry._save indent=2 同款扁平布局）
# ---------------------------------------------------------------------------
def _write_registry(repo: Path) -> None:
    reg = repo / ".runtime"
    reg.mkdir(exist_ok=True)
    (reg / "session_registry.json").write_text(
        "{"
        + chr(10)
        + f'  "{VICTIM_SID}": '
        + "{"
        + chr(10)
        + '    "session_id": "'
        + VICTIM_SID
        + '",'
        + chr(10)
        + '    "pid": 0,'
        + chr(10)
        + '    "held_files": ['
        + chr(10)
        + '      "docs/x.yaml"'
        + chr(10)
        + "    ],"
        + chr(10)
        + '    "last_heartbeat": 1'
        + chr(10)
        + "  }"
        + chr(10)
        + "}"
        + chr(10),
        encoding="utf-8",
    )


@pytest.fixture
def scratch_repo(tmp_path: Path) -> Path:
    """直跑沙盘仓：只装注册表与种子提交，钩子**不装**（bash 直跑合成本地 stdin）。"""
    repo = tmp_path / "scratch"
    repo.mkdir()
    _git_ok(repo, "init", "-q", "--initial-branch=dev")
    _git_ok(repo, "config", "user.email", "t@t")
    _git_ok(repo, "config", "user.name", "t")
    _write_registry(repo)
    (repo / "seed.txt").write_text("seed" + chr(10), encoding="utf-8")
    _git_ok(repo, "add", "--", "seed.txt")
    _git_ok(repo, "commit", "-q", "--no-verify", "-m", f"seed [GW:{VICTIM_SID}]")
    return repo


def _install_hooks(repo: Path) -> None:
    """把两个 guard 源文件逐字节复制进仓并以 .git/hooks 包装器 sourcing（生产同构）。"""
    hooks_src = repo / "hooks_src"
    hooks_src.mkdir()
    for src in (POST_COMMIT, REF_TX):
        shutil.copyfile(src, hooks_src / src.name)
    h = repo / ".git" / "hooks"
    h.mkdir(exist_ok=True)
    (h / "post-commit").write_text(
        "#!/bin/sh"
        + chr(10)
        + 'if [ -f "hooks_src/post_commit_guard.sh" ]; then'
        + chr(10)
        + "    . hooks_src/post_commit_guard.sh"
        + chr(10)
        + "fi"
        + chr(10),
        encoding="utf-8",
    )
    (h / "reference-transaction").write_text(
        "#!/bin/sh"
        + chr(10)
        + 'if [ -f "hooks_src/reference_transaction_guard.sh" ]; then'
        + chr(10)
        + "    . hooks_src/reference_transaction_guard.sh"
        + chr(10)
        + "fi"
        + chr(10),
        encoding="utf-8",
    )


@pytest.fixture
def hook_repo(tmp_path: Path) -> Path:
    """钩子链沙盘仓：scratch_repo + 两个 guard 已安装（真实 git 调用触发）。"""
    repo = tmp_path / "hooked"
    repo.mkdir()
    _git_ok(repo, "init", "-q", "--initial-branch=dev")
    _git_ok(repo, "config", "user.email", "t@t")
    _git_ok(repo, "config", "user.name", "t")
    _write_registry(repo)
    _install_hooks(repo)
    (repo / "seed.txt").write_text("seed" + chr(10), encoding="utf-8")
    _git_ok(repo, "add", "--", "seed.txt")
    _git_ok(repo, "commit", "-q", "--no-verify", "-m", f"seed [GW:{VICTIM_SID}]", env={"ZEPHYR_COMMIT_GATEWAY": "1"})
    return repo


def _plumb_commit(repo: Path, msg: str, payload_dir: Path, name: str = "evil") -> str:
    """commit-tree plumbing 造件（read-tree/update-index/write-tree，不触仓 index）。"""
    payload_dir.mkdir(exist_ok=True)
    src = payload_dir / f"{name}.txt"
    src.write_text("evil payload" + chr(10), encoding="utf-8")
    blob = _git_ok(repo, "hash-object", "-w", "--", str(src))
    idx = repo / ".git" / "t_index.tmp"
    if idx.exists():
        idx.unlink()
    e = {"GIT_INDEX_FILE": str(idx)}
    _git_ok(repo, "read-tree", "HEAD", env=e)
    _git_ok(repo, "update-index", "--add", "--cacheinfo", f"100644,{blob},{name}", env=e)
    tree = _git_ok(repo, "write-tree", env=e)
    return _git_ok(repo, "commit-tree", tree, "-p", "HEAD", "-m", msg)


def _run_ref_tx_direct(repo: Path, old: str, new: str) -> subprocess.CompletedProcess:
    """bash 直跑 ref_tx guard：合成 stdin 一行 "<old> <new> refs/heads/dev"（prepared 态）。"""
    return subprocess.run(
        ["bash", str(REF_TX), "prepared"],
        cwd=str(repo),
        input=f"{old} {new} refs/heads/dev" + chr(10),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env={**os.environ},
    )


def _reports(repo: Path, gate: str = "reference_transaction_guard") -> list[Path]:
    d = repo / ".runtime" / "reconcile_reports"
    return sorted(d.glob(f"{gate}_*.json")) if d.exists() else []


# ===========================================================================
# 场景④ 红方伪造 [GW:]/绕门
# ===========================================================================
@pytest.mark.skipif(shutil.which("bash") is None, reason="bash 不可用（钩子直跑法需要）")
class TestS4AForgedMarkersDirectRun:
    """三伪造形态 bash 直跑 ref_tx guard（合成 stdin）——exit 1 或落审计。"""

    def test_s4a1_unregistered_sid_blocked_with_block_audit(self, scratch_repo, tmp_path):
        old = _git_ok(scratch_repo, "rev-parse", "HEAD")
        new = _plumb_commit(scratch_repo, f"未注册伪造 [GW:{FORGER_SID}]", tmp_path / "pl1")
        scratch_repo.joinpath(".runtime/reconcile_reports").mkdir(exist_ok=True)
        before = _reports(scratch_repo)
        r = _run_ref_tx_direct(scratch_repo, old, new)
        assert r.returncode == 1, f"未注册 sid 伪造必须 exit 1：rc={r.returncode} {r.stderr}"
        assert "伪造 GW 标记" in (r.stdout + r.stderr)
        new_reports = [p for p in _reports(scratch_repo) if p not in before]
        assert new_reports, "block 必须伴随审计落盘（可疑不静默）"
        payload = json.loads(new_reports[-1].read_text(encoding="utf-8"))
        assert payload["action"] == "block"
        assert payload.get("session_id") is None or FORGER_SID not in str(payload.get("session_id"))

    @pytest.mark.parametrize("shadow", ["pid", "held_files", "last_heartbeat", "session_id"])
    def test_s4a2_registry_field_name_tokens_blocked(self, scratch_repo, tmp_path, shadow):
        old = _git_ok(scratch_repo, "rev-parse", "HEAD")
        new = _plumb_commit(scratch_repo, f"字段名当通行证 [GW:{shadow}]", tmp_path / "pl2")
        r = _run_ref_tx_direct(scratch_repo, old, new)
        assert r.returncode == 1, f"注册表字段名 {shadow} 被当 sid 通行证：{r.stdout}{r.stderr}"

    def test_s4a3_impersonating_live_foreign_sid_exit1_or_audit(self, scratch_repo, tmp_path):
        """冒充在活他人 sid（★ 残余风险②，修复前=静默 exit 0 零审计）。

        验收口径：exit 1 **或**落审计。本车道收窄后=warn_only 审计
        （violation=gw_sid_channel_unverifiable）；归属级治本（HMAC 载体）
        待总包裁定——若未来升级为硬拦（exit 1），本测试仍绿。
        """
        assert not _reports(scratch_repo), "前置：沙盘仓零审计——落下的审计必出自本看守卫"
        old = _git_ok(scratch_repo, "rev-parse", "HEAD")
        new = _plumb_commit(scratch_repo, f"冒充在活他人 [GW:{VICTIM_SID}]", tmp_path / "pl3")
        r = _run_ref_tx_direct(scratch_repo, old, new)
        reports = _reports(scratch_repo)
        assert r.returncode == 1 or reports, f"冒充在活 sid 既未拦也未审计（静默放行）: rc={r.returncode} {r.stderr}"
        assert reports, "warn_only 收窄必须落审计"
        payload = json.loads(reports[-1].read_text(encoding="utf-8"))
        assert payload["violation"] == "gw_sid_channel_unverifiable"
        assert VICTIM_SID in payload["session_id"], "审计必须记录被冒充的 sid"
        assert payload["action"] == "warn_only", "通道不可证=可疑留痕，不是既证伪造，不阻断"


@pytest.mark.skipif(shutil.which("bash") is None, reason="bash 不可用（钩子直跑法需要）")
class TestS4BPlumbingBypassHookChain:
    """commit-tree+update-ref 绕 pre-commit——hook 链必须拦；剥钩红证尺能红。"""

    def test_s4b1_commit_tree_update_ref_bypass_blocked(self, hook_repo, tmp_path):
        new = _plumb_commit(hook_repo, "无标记 plumbing 绕过", tmp_path / "plb")
        tip = _git_ok(hook_repo, "rev-parse", "HEAD")
        r = _git(hook_repo, "update-ref", "refs/heads/dev", new)  # 不带 old=假 creation
        assert r.returncode != 0, f"plumbing 绕过未被 hook 链拦截：{r.stdout}{r.stderr}"
        assert _git_ok(hook_repo, "rev-parse", "HEAD") == tip, "被拦事务不得推进分支"

    def test_s4b2_red_proof_hook_stripped_same_replay_lands(self, hook_repo, tmp_path):
        """红证：剥掉钩子内容重放同一 bypass——必须能落。证明 s4b1 的拦截
        出自 reference-transaction 钩子本身（尺有判别力，非环境假阳性）。"""
        new = _plumb_commit(hook_repo, "剥钩红证 plumbing", tmp_path / "plb2")
        (hook_repo / ".git" / "hooks" / "reference-transaction").write_text(
            "#!/bin/sh" + chr(10) + "exit 0" + chr(10), encoding="utf-8"
        )
        r = _git(hook_repo, "update-ref", "refs/heads/dev", new)
        assert r.returncode == 0, f"剥钩后重放仍被拦=钩子不是拦截主体，红证失败：{r.stderr}"
        assert _git_ok(hook_repo, "rev-parse", "HEAD") == new, "剥钩后 bypass 必须真实落地"


@pytest.mark.skipif(shutil.which("bash") is None, reason="bash 不可用（钩子直跑法需要）")
class TestS4CEmergencyEscapeHatch:
    """[GW:sid:emergency] 逃生道：放行但必须落审计；剥钩红证审计出自钩子。"""

    def test_s4c1_emergency_passes_with_unregistered_sid_audit(self, hook_repo, tmp_path):
        tip = _git_ok(hook_repo, "rev-parse", "HEAD")
        new = _plumb_commit(hook_repo, f"P0 紧急修复 [GW:{EMERGENCY_SID}:emergency]", tmp_path / "plc")
        r = _git(hook_repo, "update-ref", "refs/heads/dev", new, tip)  # CAS 快进
        assert r.returncode == 0, f"emergency 逃生通道被误杀：{r.stdout}{r.stderr}"
        assert _git_ok(hook_repo, "rev-parse", "HEAD") == new, "逃生放行必须真实落地"
        reports = _reports(hook_repo)
        assert reports, "emergency 放行必须落审计（unregistered_gw_sid，可疑不静默）"
        payload = json.loads(reports[-1].read_text(encoding="utf-8"))
        assert payload["violation"] == "unregistered_gw_sid"
        assert EMERGENCY_SID in payload["session_id"]

    def test_s4c2_red_proof_stripped_hook_emergency_lands_silently(self, hook_repo, tmp_path):
        """红证：剥钩后同一 CAS 重放落库且**零审计**——证明 s4c1 的审计出自钩子。"""
        (hook_repo / ".git" / "hooks" / "reference-transaction").write_text(
            "#!/bin/sh" + chr(10) + "exit 0" + chr(10), encoding="utf-8"
        )
        assert not _reports(hook_repo)
        tip = _git_ok(hook_repo, "rev-parse", "HEAD")
        new = _plumb_commit(hook_repo, f"剥钩红证 [GW:{EMERGENCY_SID}:emergency]", tmp_path / "plc2")
        r = _git(hook_repo, "update-ref", "refs/heads/dev", new, tip)
        assert r.returncode == 0, f"剥钩后 emergency 重放被拦：{r.stderr}"
        assert _git_ok(hook_repo, "rev-parse", "HEAD") == new
        assert not _reports(hook_repo), "剥钩后不应有审计——有则说明审计另有所源（尺失判别力）"


# ===========================================================================
# 场景⑤ GateResultCache 缓存投毒与失效（T7 键=own blob sha 合集）
# ===========================================================================
@pytest.fixture()
def cache_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "crepo"
    repo.mkdir()
    _git_ok(repo, "init", "-q", "--initial-branch=main")
    _git_ok(repo, "config", "core.autocrlf", "false")
    _git_ok(repo, "config", "user.email", "t@t")
    _git_ok(repo, "config", "user.name", "t")
    (repo / "own.py").write_text("X = 1" + chr(10), encoding="utf-8")
    (repo / "config").mkdir()
    (repo / "config" / "flags.yaml").write_text("flags: {}" + chr(10), encoding="utf-8")
    _git_ok(repo, "add", "-A")
    _git_ok(repo, "commit", "-qm", "init")
    return repo


def _cache_gateway(repo: Path) -> SimpleNamespace:
    def run_git(argv, cwd=None):
        return subprocess.run(argv, cwd=str(repo), capture_output=True, text=True)

    return SimpleNamespace(run_git=run_git, project_root=str(repo))


def _stage(repo: Path, name: str, text: str) -> None:
    (repo / name).write_text(text, encoding="utf-8")
    _git_ok(repo, "add", "--", name)


def _cache_files(repo: Path) -> list[Path]:
    return sorted((repo / ".runtime" / "gate_cache").glob("*.json"))


class TestS5CachePoisoningAndInvalidation:
    def test_s5a_own_staged_content_change_misses(self, cache_repo):
        """投毒逆命题：gate 判过后 own 文件 staged 内容被改 → 陈旧 passed 不得复用。"""
        gw = _cache_gateway(cache_repo)
        cache = gcp.GateResultCache(gw, ["own.py"])
        cache.store("ENCODING-SAFETY", "scope-a", "passed-v1")
        assert gcp.GateResultCache(gw, ["own.py"]).lookup("ENCODING-SAFETY", "scope-a") == "passed-v1"
        _stage(cache_repo, "own.py", "X = 'DROP TABLE users'" + chr(10))  # 改后本应 fail 的内容
        cache2 = gcp.GateResultCache(gw, ["own.py"])
        assert cache2.lookup("ENCODING-SAFETY", "scope-a") is None, "own 内容变化 ⇒ 必须 miss"

    def test_s5b_foreign_index_activity_still_hits(self, cache_repo):
        """键隔离：他人向共享 index 塞文件（全树 sha 必变，内证）不得作废 own 缓存。"""
        gw = _cache_gateway(cache_repo)
        tree_before = _git_ok(cache_repo, "write-tree")
        cache = gcp.GateResultCache(gw, ["own.py"])
        cache.store("NO-BARE-SQL", "scope-b", "passed-v2")
        # 他人连塞三个无关文件（write-tree 全树 sha 必变——证明攻击真实发生）
        for i in range(3):
            _stage(cache_repo, f"foreign_{i}.py", f"Y{i} = {i}" + chr(10))
        assert _git_ok(cache_repo, "write-tree") != tree_before, "index 未变=本测试无判别力"
        cache2 = gcp.GateResultCache(gw, ["own.py"])
        assert cache2.lookup("NO-BARE-SQL", "scope-b") == "passed-v2", (
            "own 内容未变 ⇒ 他人 index 活动不得逐出缓存（键隔离）"
        )

    def test_s5c_flags_mtime_change_misses(self, cache_repo):
        """配置册变更失效：flags mtime 进键——改 mtime 后必须 miss。"""
        gw = _cache_gateway(cache_repo)
        cache = gcp.GateResultCache(gw, ["own.py"])
        cache.store("NO-BARE-SQL", "scope-c", "passed-v3")
        flags = cache_repo / "config" / "flags.yaml"
        mt = os.path.getmtime(flags)
        os.utime(flags, (mt + 5.0, mt + 5.0))
        cache2 = gcp.GateResultCache(gw, ["own.py"])
        assert cache2.lookup("NO-BARE-SQL", "scope-c") is None, "flags mtime 变 ⇒ 必须 miss"

    @pytest.mark.parametrize(
        "payload",
        [
            "{{{not-json-at-all",  # JSONDecodeError（ValueError 子类）
            '{"gate_id":"G","detail":"x"}',  # 缺 ts → KeyError
            '{"gate_id":"G","detail":"x","ts":"not-a-number"}',  # float() → ValueError
            '{"gate_id":"G","detail":"x","ts":null}',  # float(None) → TypeError
        ],
    )
    def test_s5d_malformed_cache_json_returns_none(self, cache_repo, payload):
        """缓存文件被写畸形 → lookup 返 None 不崩（fail-safe 回退现算）。"""
        gw = _cache_gateway(cache_repo)
        cache = gcp.GateResultCache(gw, ["own.py"])
        cache.store("NO-BARE-SQL", "scope-d", "passed-v4")
        files = _cache_files(cache_repo)
        assert len(files) == 1, "沙盘缓存目录应恰有一个键文件"
        files[0].write_text(payload, encoding="utf-8")
        assert gcp.GateResultCache(gw, ["own.py"]).lookup("NO-BARE-SQL", "scope-d") is None

    def test_s5e_ttl_expired_misses(self, cache_repo):
        """TTL 600s：过期为 miss，界内仍 hit（证明 miss 出自 TTL 而非别的）。"""
        gw = _cache_gateway(cache_repo)
        cache = gcp.GateResultCache(gw, ["own.py"])
        cache.store("NO-BARE-SQL", "scope-e", "passed-v5")
        f = _cache_files(cache_repo)[0]
        data = json.loads(f.read_text(encoding="utf-8"))
        now = datetime.now(timezone.utc).timestamp()
        data["ts"] = now - 100.0  # 界内
        f.write_text(json.dumps(data), encoding="utf-8")
        assert gcp.GateResultCache(gw, ["own.py"]).lookup("NO-BARE-SQL", "scope-e") == "passed-v5"
        data["ts"] = now - 601.0  # 过期
        f.write_text(json.dumps(data), encoding="utf-8")
        assert gcp.GateResultCache(gw, ["own.py"]).lookup("NO-BARE-SQL", "scope-e") is None, "TTL 过期 ⇒ 必须 miss"


# ===========================================================================
# 场景⑥ 超顶大批与队首饿死（tmp 队列根 120 件，_HEAD_SCAN_BOUND=400 界内）
# ===========================================================================
def _mk_item(qid: str, created_at: str, *, attempts: int | None = None, lane: str | None = None) -> dict:
    item: dict = {
        "qid": qid,
        "session_id": "s-csx-rb",
        "created_at": created_at,
        "base_head": "",
        "meta": {"lane": lane} if lane else {},
        "files": [{"path": "docs/_working/csx_rb_stub.txt"}],
    }
    if attempts is not None:
        item["attempts"] = attempts
    return item


def _write_pending(root: Path, item: dict) -> Path:
    p = root / "pending" / f"{item['qid']}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(item, ensure_ascii=False), encoding="utf-8")
    return p


def _batch(root: Path, specs: list[dict]) -> list[Path]:
    """写 120 件并按 qid 字典序返回（模拟 drain 调用方的 sorted(pending.glob) 预排）。"""
    paths = [_write_pending(root, s["item"]) for s in specs]
    return sorted(paths, key=lambda p: p.name)


class TestS6OversizedBatchAndStarvation:
    def test_s6a_oldest_of_120_wins_despite_lexicographic_last(self, tmp_path):
        """B4 FIFO：120 件中 created_at 最早者被选中——即便它 qid 字典序垫底
        （排在扫描名单最后；扫描界 400 覆盖 120，改回 64 本测试必红）。"""
        root = tmp_path / "q6a"
        now = _now()
        specs = [
            {"item": _mk_item(f"q-rb-a-{i:04d}", _iso(now - timedelta(seconds=60 * i)))}
            for i in range(1, 120)  # 119 件新鲜件（1~118 分钟前）
        ]
        specs.append({"item": _mk_item("q-rb-z-9999", _iso(now - timedelta(hours=24)))})  # 最老垫底
        heads = _batch(root, specs)
        assert len(heads) == 120
        head, lane = cq._pick_head(heads)
        assert head is not None and head.stem == "q-rb-z-9999", (
            "最老件（字典序最后）必须被选中——B4 created_at FIFO 被字典序短路即红"
        )
        assert lane == "interactive"

    def test_s6b_single_interactive_not_starved_by_119_machine(self, tmp_path):
        """119 machine 洪灌 + 1 interactive → interactive 优先（车道语义不被洪灌淹没）。"""
        root = tmp_path / "q6b"
        now = _now()
        specs = [
            {"item": _mk_item(f"q-rb-m-{i:04d}", _iso(now - timedelta(seconds=30 + i)), lane="machine")}
            for i in range(1, 120)  # 最老 machine ≈ 149s 前 < 30min 饿死线，不触发逃逸
        ]
        specs.append({"item": _mk_item("q-rb-z-9999", _iso(now - timedelta(hours=24)))})  # 最老 interactive
        heads = _batch(root, specs)
        head, lane = cq._pick_head(heads)
        assert lane == "interactive" and head is not None and head.stem == "q-rb-z-9999", (
            "interactive 必须压过 machine 洪灌被优先拾取"
        )

    def test_s6b2_machine_lane_starvation_escape_still_works(self, tmp_path):
        """双向护栏：最老 machine 饿过 30min → 即便有 interactive 也提前放行 machine。"""
        root = tmp_path / "q6b2"
        now = _now()
        specs = [
            {"item": _mk_item(f"q-rb-m-{i:04d}", _iso(now - timedelta(seconds=10 * i)), lane="machine")}
            for i in range(1, 120)  # 其余 machine 件 10~1180s 前，均在 30min 饿死线内
        ]
        specs[0]["item"]["created_at"] = _iso(now - timedelta(seconds=1900))  # 唯一超饿死线者
        specs.append({"item": _mk_item("q-rb-i-0001", _iso(now - timedelta(seconds=1)))})  # 新鲜 interactive
        heads = _batch(root, specs)
        head, lane = cq._pick_head(heads)
        assert lane == "machine" and head is not None and head.stem == "q-rb-m-0001", (
            "machine 饿死逃逸（30min）必须仍生效——interactive 存在不得永久压死 machine"
        )

    def test_s6c_poison_item_backed_off_not_permanent_head(self, tmp_path, monkeypatch):
        """B5：attempts≥3 毒药件（created_at 最早居队首）排队键退避让位正常件。"""
        monkeypatch.delenv(cq._ATTEMPTS_BACKOFF_ENV, raising=False)  # 缺省 ON
        root = tmp_path / "q6c"
        now = _now()
        specs = [{"item": _mk_item("q-rb-a-0001", _iso(now - timedelta(hours=24)), attempts=4)}]
        specs += [{"item": _mk_item(f"q-rb-b-{i:04d}", _iso(now - timedelta(seconds=30 + i)))} for i in range(1, 120)]
        heads = _batch(root, specs)
        head, _lane = cq._pick_head(heads)
        assert head is not None and head.stem != "q-rb-a-0001", (
            "attempts=4 毒药件必须退避让位（B5 惩罚键生效；恒霸队首即红）"
        )
        assert head.stem == "q-rb-b-0119", "让位后应拾取最老正常件（FIFO 在正常件间保持）"

    def test_s6c2_backoff_switch_off_restores_fifo(self, tmp_path, monkeypatch):
        """开关关闭=回退现行为（created_at FIFO，毒药件按老幼居首）——off 态如实钉档。"""
        monkeypatch.setenv(cq._ATTEMPTS_BACKOFF_ENV, "0")
        root = tmp_path / "q6c2"
        now = _now()
        specs = [{"item": _mk_item("q-rb-a-0001", _iso(now - timedelta(hours=24)), attempts=4)}]
        specs += [{"item": _mk_item(f"q-rb-b-{i:04d}", _iso(now - timedelta(seconds=30 + i)))} for i in range(1, 120)]
        heads = _batch(root, specs)
        head, _lane = cq._pick_head(heads)
        assert head is not None and head.stem == "q-rb-a-0001", "开关关闭=退避停用，FIFO 原语义"
