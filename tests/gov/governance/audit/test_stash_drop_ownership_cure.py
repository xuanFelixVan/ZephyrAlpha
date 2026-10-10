# [MODULE] tests.governance.audit.test_stash_drop_ownership_cure
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.audit.reconciliation_registry, zephyr.security.access_control.session_concurrency, scripts.git_guard
# [CONSUMERS] —
# [STARTUP] manual
# [MATURITY] evolving
# [INVARIANTS] 测试隔离——一律 tmp_path 临时 git 仓 + tmp_path/.runtime 会话片，禁写生产 .runtime/.ailocks；
#   活性判据走真源 liveness_verdict（不 mock 判据本身，只把会话片与 cwd 锚到 tmp 仓）；
#   "确认已死 PID"用 Popen 立即退出的子进程真实构造；时间判据用 GIT_COMMITTER_DATE 造旧，禁 sleep。
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] self
# [A_module] module_id=TEST-MOD-GATE_ENGINE-TEST_STASH_DROP_OWNERSHIP_CURE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_stash_drop_ownership_cure.py — stash drop "认人+存证+留痕" 治本红证（st-maint1 件②，2026-10-10）

判据真源：
- ``reconciliation_registry.govern_stash_drop`` / ``drop_governed_stash``（三前置）
- 会话活性唯一裁决表 ``session_concurrency.liveness_verdict``（裁定#480 C-2，:1637）
- ``scripts/git_guard.py::_handle_stash_destructive``（drop/clear 不再只读放行）

覆盖（每一条都对着一张蒸发脸）：
1. 属主为**在场活会话**的过期 stash → 不被 drop（旧口径：反向匹配反推"AI 创建"即 drop）
2. 属主**判死**（真死 PID）且已存证 → 被 drop，且字节仍可从 refs/quarantine 锚一命令取回
3. 属主未注册（ghost）/ message 无 sid / sid 歧义 → 一律豁免
4. 存证锚写不下去（refs/quarantine 被占位为 ref 冲突）→ 不 drop（fail-closed 于动手侧）
5. TTL 仍有效：属主判死但 stash 新鲜（<4h）→ 保留
6. 每笔判定都落 .runtime/gate_audit/stash_drop_governance.jsonl（含"是否真 drop"）
7. git_guard：``stash drop`` 不再 passthrough（rc=1 + 字节仍在）；``stash clear`` 默认阻断；
   非白名单逃生标记不生效；白名单逃生仍先落锚再放行
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import types
from datetime import UTC, datetime
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[4]
for _p in (str(_PROJECT_ROOT), str(_PROJECT_ROOT / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from zephyr.governance.audit.reconciliation_registry import (  # noqa: E402
    make_stash_lifecycle_reconciler,
)
from zephyr.security.access_control.session_concurrency import (  # noqa: E402
    SessionRegistry,
    liveness_verdict,
)

# 判据面新增符号（govern_stash_drop / drop_governed_stash / anchor_stash_ref /
# stash_owner_candidates / STASH_DROP_AUDIT_RELPATH）在需要它们的用例内 **延迟 import**
# ——这样"红证"能在未修码上先跑出**行为断言失败**（旧口径真把活会话 stash drop 了），
# 而不是只会 ImportError 的假红。
_STASH_AUDIT_RELPARTS = (".runtime", "gate_audit", "stash_drop_governance.jsonl")

# git_guard 授权类 env（子进程必须显式清理，否则闸门被绕过）
_AUTH_ENVS = (
    "ZEPHYR_FORCE_STASH",
    "ZEPHYR_COMMIT_GATEWAY",
    "ZEPHYR_GIT_GUARD_FAST_PATH",
    "ZEPHYR_SERIALIZER_MODE",
    "ZEPHYR_STASH_DROP_ESCAPE",
    "ZEPHYR_STASH_LIFECYCLE_AGGRESSIVE",
)

_GIT_GUARD = _PROJECT_ROOT / "scripts" / "git_guard.py"


# —— 夹具：临时 git 仓 + 真源会话片 ——


def _clean_env() -> dict[str, str]:
    env = os.environ.copy()
    for key in _AUTH_ENVS:
        env.pop(key, None)
    return env


def _git_env(*, date_iso: str | None = None) -> dict[str, str]:
    """clean env + 固定 git 身份（tmp 仓不继承生产 user.name/email）。"""
    env = _clean_env()
    for k, v in (
        ("GIT_AUTHOR_NAME", "Test"),
        ("GIT_AUTHOR_EMAIL", "test@test.com"),
        ("GIT_COMMITTER_NAME", "Test"),
        ("GIT_COMMITTER_EMAIL", "test@test.com"),
    ):
        env[k] = v
    if date_iso:
        env["GIT_AUTHOR_DATE"] = date_iso
        env["GIT_COMMITTER_DATE"] = date_iso
    return env


def _init_git_repo(path: Path) -> None:
    env = _git_env()
    subprocess.run(["git", "init"], cwd=str(path), capture_output=True, env=env, check=True)
    (path / "README.md").write_text("init", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=str(path), capture_output=True, env=env, check=True)
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=str(path),
        capture_output=True,
        env=env,
        check=True,
    )


def _make_dead_pid() -> int:
    """真实构造"确认已死 PID"：起一个立即退出的子进程并 wait 收尸（禁 sleep）。"""
    proc = subprocess.Popen([sys.executable, "-c", "import os; os._exit(0)"])
    proc.wait(timeout=30)
    assert proc.returncode == 0
    return proc.pid


def _register_session(root: Path, sid: str, *, pid: int, heartbeat_age: float = 5.0) -> None:
    """把会话片写进 **tmp 仓**的 .runtime/session_registry/（活性判据真源数据面）。

    写片形态对齐 SessionRegistry 分片真源（文件名 = ``_shard_filename(sid)``），
    活性判定不 mock——由 ``liveness_verdict`` 自己读片 + ``is_pid_alive`` 真判。
    """
    shard_dir = root / ".runtime" / "session_registry"
    shard_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "session_id": sid,
        "pid": pid,
        "start_time": time.time() - 3600,
        "last_heartbeat": time.time() - heartbeat_age,
        "last_activity": time.time() - heartbeat_age,
        "held_files": [],
        "task_files": [],
    }
    (shard_dir / SessionRegistry._shard_filename(sid)).write_text(
        json.dumps(payload, ensure_ascii=False), encoding="utf-8"
    )


def _create_stash(
    path: Path,
    message: str,
    filename: str,
    *,
    age_seconds: float | None = None,
) -> str:
    """建一条 stash（tracked 文件先 commit，再改再 stash）。

    ``age_seconds`` 用 GIT_COMMITTER_DATE/GIT_AUTHOR_DATE 造旧——时间判据靠构造
    数据面，不靠 sleep，也不改阈值。
    """
    env = _git_env()
    target = path / filename
    target.write_text("initial", encoding="utf-8")
    subprocess.run(["git", "add", "--", filename], cwd=str(path), capture_output=True, env=env, check=True)
    subprocess.run(
        ["git", "commit", "-m", f"add {filename}"],
        cwd=str(path),
        capture_output=True,
        env=env,
        check=True,
    )
    payload = f"content-for-{message}"
    target.write_text(payload, encoding="utf-8")
    if age_seconds is not None:
        iso = datetime.fromtimestamp(time.time() - age_seconds, tz=UTC).strftime("%Y-%m-%dT%H:%M:%S+00:00")
        env = _git_env(date_iso=iso)
    r = subprocess.run(
        ["git", "stash", "push", "-m", message, "--", filename],
        cwd=str(path),
        capture_output=True,
        text=True,
        env=env,
        timeout=20,
    )
    assert r.returncode == 0, f"stash push 失败: {r.stderr}"
    return payload


def _stash_msgs(path: Path) -> list[str]:
    r = subprocess.run(
        ["git", "stash", "list", "--format=%s"],
        cwd=str(path),
        capture_output=True,
        text=True,
        timeout=20,
    )
    return [line.strip() for line in (r.stdout or "").splitlines() if line.strip()]


def _refs(path: Path, prefix: str) -> list[str]:
    r = subprocess.run(
        ["git", "for-each-ref", "--format=%(refname)", prefix],
        cwd=str(path),
        capture_output=True,
        text=True,
        timeout=20,
    )
    return [line.strip() for line in (r.stdout or "").splitlines() if line.strip()]


def _run_reconciler(path: Path, monkeypatch: pytest.MonkeyPatch, *, aggressive: bool = False):
    monkeypatch.delenv("ZEPHYR_STASH_LIFECYCLE_AGGRESSIVE", raising=False)
    if aggressive:
        monkeypatch.setenv("ZEPHYR_STASH_LIFECYCLE_AGGRESSIVE", "1")
    spec = make_stash_lifecycle_reconciler(types.SimpleNamespace(project_root=path))
    return spec.reconcile(["some-file.py"], "tester-session")


def _audit_records(path: Path) -> list[dict]:
    p = path.joinpath(*_STASH_AUDIT_RELPARTS)
    if not p.exists():
        return []
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


# ============================================================================
# ① 认人：活会话 / 未注册 / 无 sid / 歧义 → 一律豁免
# ============================================================================


class TestOwnershipGate:
    def test_live_owner_stash_is_never_dropped(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """属主=在场活会话（真 PID 在岗）的过期 stash MUST NOT 被 drop。

        这就是 2026-10-10 蒸发战争的脸：旧口径只看前缀不看人，把在场活会话尚未
        落地（未 commit）的在飞面直接 drop 掉。
        """
        _init_git_repo(tmp_path)
        monkeypatch.chdir(tmp_path)  # liveness_verdict 读 cwd 锚定的主仓根
        sid = "st-liveowner-0001"
        _register_session(tmp_path, sid, pid=os.getpid())
        payload = _create_stash(tmp_path, f"WIP 在飞面 {sid} 未落地", "live.py", age_seconds=6 * 3600)

        result = _run_reconciler(tmp_path, monkeypatch)

        assert "dropped=0" in result.detail, result.detail
        assert "exempt=1" in result.detail, result.detail
        assert _stash_msgs(tmp_path) == [f"On master: WIP 在飞面 {sid} 未落地"]
        # 字节仍在 stash 里（未被 drop 自然可取回）
        got = subprocess.run(
            ["git", "show", "stash@{0}:live.py"],
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
            timeout=20,
        )
        assert got.stdout == payload
        assert _refs(tmp_path, "refs/quarantine/") == []  # 没动手就不该留"已 drop"的锚

    def test_unregistered_owner_exempt(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """sid 抽得出但注册表无片（未注册=判活不明，liveness=ghost）→ 豁免。"""
        _init_git_repo(tmp_path)
        monkeypatch.chdir(tmp_path)
        _create_stash(tmp_path, "pre-merge-cleanup-sess-never-registered", "ghost.py", age_seconds=6 * 3600)

        result = _run_reconciler(tmp_path, monkeypatch)

        assert "dropped=0" in result.detail, result.detail
        assert len(_stash_msgs(tmp_path)) == 1

    def test_message_without_sid_exempt(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """message 里没有任何可判 sid → 归属不可判 → 豁免（旧口径会直接反推 AI 即 drop）。"""
        _init_git_repo(tmp_path)
        monkeypatch.chdir(tmp_path)
        _create_stash(
            tmp_path,
            "CONSUMERS-ACCURACY work-in-progress from previous session",
            "nosid.py",
            age_seconds=6 * 3600,
        )

        result = _run_reconciler(tmp_path, monkeypatch)

        assert "dropped=0" in result.detail, result.detail
        assert len(_stash_msgs(tmp_path)) == 1

    def test_ambiguous_owner_sid_exempt(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """一条 message 命中两个 sid=归属歧义 → 保守侧豁免（宁可不 drop）。"""
        _init_git_repo(tmp_path)
        monkeypatch.chdir(tmp_path)
        _register_session(tmp_path, "st-amb-dead", pid=_make_dead_pid())
        _create_stash(tmp_path, "mixed st-amb-dead and st-amb-alive", "amb.py", age_seconds=6 * 3600)

        result = _run_reconciler(tmp_path, monkeypatch)

        assert "dropped=0" in result.detail, result.detail
        assert len(_stash_msgs(tmp_path)) == 1

    def test_owner_candidates_extraction(self) -> None:
        """sid 抽取本身的口径（显式署名优先 + st-/sess- token 兜底 + 去重）。"""
        from zephyr.governance.audit.reconciliation_registry import stash_owner_candidates

        assert stash_owner_candidates("On dev: session_worktree_pre_merge: sess-49896-wiki-md") == [
            "sess-49896-wiki-md"
        ]
        assert stash_owner_candidates("On dev: st-finalclean2 whole-dir sweep") == ["st-finalclean2"]
        assert stash_owner_candidates("other-session-wip-module-id-naming-fix") == []


# ============================================================================
# ② 存证：判死属主的 stash 可 drop，且 drop 后字节仍可从锚 ref 一命令取回
# ============================================================================


class TestDeadOwnerDropWithAnchor:
    def test_dead_owner_dropped_and_bytes_recoverable_from_anchor(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """属主判死（真死 PID，活性裁决=dead/PID-DEAD）→ drop，且锚里字节可取回。"""
        _init_git_repo(tmp_path)
        monkeypatch.chdir(tmp_path)
        sid = "st-deadowner-0001"
        dead_pid = _make_dead_pid()
        _register_session(tmp_path, sid, pid=dead_pid)
        # 前置自检：判据真源确实判 dead（防夹具与真源漂移）
        assert liveness_verdict(sid).state == "dead"

        payload = _create_stash(tmp_path, f"stale pre-merge {sid}", "dead.py", age_seconds=6 * 3600)

        result = _run_reconciler(tmp_path, monkeypatch)

        assert "dropped=1" in result.detail, result.detail
        assert _stash_msgs(tmp_path) == []

        anchors = _refs(tmp_path, "refs/quarantine/")
        assert len(anchors) == 1
        assert f"stash-{sid}-" in anchors[0]
        got = subprocess.run(
            ["git", "show", f"{anchors[0]}:dead.py"],
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
            timeout=20,
        )
        assert got.returncode == 0, got.stderr
        assert got.stdout == payload  # drop 之后仍能一命令取回字节

    def test_fresh_stash_of_dead_owner_still_kept_by_ttl(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """TTL 未被放松：属主判死但 stash <4h → 保留（时间判据靠造数据面，无 sleep）。"""
        _init_git_repo(tmp_path)
        monkeypatch.chdir(tmp_path)
        sid = "st-deadowner-0002"
        _register_session(tmp_path, sid, pid=_make_dead_pid())
        _create_stash(tmp_path, f"just-made {sid}", "fresh.py", age_seconds=60)

        result = _run_reconciler(tmp_path, monkeypatch)

        # 连候选都不成立（TTL 未到）→ skip，且不落动手判定审计（根本没走到治理面）
        assert result.action == "skip", f"expected skip, got {result.action}: {result.detail}"
        assert len(_stash_msgs(tmp_path)) == 1
        assert _audit_records(tmp_path) == []

    def test_govern_refuses_when_anchor_cannot_be_written(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """存证锚写不下去 → 不 drop（fail-closed 关在动手侧）。

        锚失败用 ref 目录位冲突机械制造：先把 refs/quarantine 占成一个 ref，
        则 refs/quarantine/stash-… 无法写入（git 报 cannot allocate 类错）。
        """
        _init_git_repo(tmp_path)
        monkeypatch.chdir(tmp_path)
        sid = "st-deadowner-0003"
        _register_session(tmp_path, sid, pid=_make_dead_pid())
        _create_stash(tmp_path, f"anchor will fail {sid}", "anchorfail.py", age_seconds=6 * 3600)

        sha = subprocess.run(
            ["git", "rev-parse", "stash@{0}"],
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
            timeout=20,
        ).stdout.strip()
        blocked = subprocess.run(
            ["git", "update-ref", "refs/quarantine", sha],
            cwd=str(tmp_path),
            capture_output=True,
            timeout=20,
        )
        assert blocked.returncode == 0, blocked.stderr

        from zephyr.governance.audit.reconciliation_registry import govern_stash_drop

        verdict = govern_stash_drop(tmp_path, "stash@{0}")

        assert verdict.allowed is False
        assert "存证锚" in verdict.reason, verdict.reason
        assert verdict.quarantine_ref == ""

    def test_drop_governed_stash_reports_sha_and_anchor(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """``drop_governed_stash`` 直接调用面：allowed+dropped+锚 sha 三件齐。"""
        _init_git_repo(tmp_path)
        monkeypatch.chdir(tmp_path)
        sid = "st-deadowner-0004"
        _register_session(tmp_path, sid, pid=_make_dead_pid())
        _create_stash(tmp_path, f"direct api {sid}", "direct.py", age_seconds=6 * 3600)

        from zephyr.governance.audit.reconciliation_registry import drop_governed_stash

        verdict = drop_governed_stash(tmp_path, "stash@{0}", actor="unit")

        assert verdict.allowed and verdict.dropped, verdict.reason
        assert verdict.stash_sha and verdict.quarantine_ref
        assert _refs(tmp_path, "refs/quarantine/") == [verdict.quarantine_ref]


# ============================================================================
# ③ 留痕：每笔判定（含未动手的豁免）都落 gate_audit jsonl
# ============================================================================


class TestAuditTrail:
    def test_audit_written_for_blocked_and_dropped(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """审计行含 stash sha／属主 sid／判死依据／存证 ref／是否真 drop 五要素。"""
        _init_git_repo(tmp_path)
        monkeypatch.chdir(tmp_path)
        sid = "st-audit-0001"
        _register_session(tmp_path, sid, pid=_make_dead_pid())
        _create_stash(tmp_path, f"audited drop {sid}", "a1.py", age_seconds=6 * 3600)
        _create_stash(tmp_path, "no owner sid here at all", "a2.py", age_seconds=6 * 3600)

        _run_reconciler(tmp_path, monkeypatch)

        records = _audit_records(tmp_path)
        assert len(records) == 2, records
        dropped = [r for r in records if r["did_drop"]]
        blocked = [r for r in records if not r["did_drop"]]
        assert len(dropped) == 1 and len(blocked) == 1
        assert dropped[0]["owner_sid"] == sid
        assert dropped[0]["liveness_state"] == "dead"
        assert dropped[0]["stash_sha"]
        assert dropped[0]["quarantine_ref"].startswith("refs/quarantine/stash-")
        assert "PID-DEAD" in dropped[0]["reason"]  # 判死依据入册
        assert blocked[0]["owner_sid"] == ""
        assert blocked[0]["quarantine_ref"] == ""
        assert blocked[0]["allowed"] is False


# ============================================================================
# ④ git_guard：drop/clear 不再被当只读无条件放行
# ============================================================================


def _run_guard(repo: Path, *guard_args: str) -> subprocess.CompletedProcess:
    env = _clean_env()
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(
        [sys.executable, str(_GIT_GUARD), *guard_args],
        cwd=str(repo),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
        timeout=120,
    )


class TestGitGuardStashDrop:
    def test_drop_is_not_readonly_constant(self) -> None:
        """分类面真源：drop 已移出 STASH_READONLY。"""
        sys.path.insert(0, str(_PROJECT_ROOT / "scripts"))
        import git_guard

        readonly = set(git_guard.STASH_READONLY)
        destructive = set(git_guard.STASH_DESTRUCTIVE)
        assert readonly == {"list", "show"}, f"drop 必须已移出只读集: {readonly}"
        assert {"drop", "clear"} <= destructive, f"破坏性集缺项: {destructive}"

    def test_stash_drop_blocked_for_unowned_stash(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """归属不可判 → git stash drop 被阻断（rc=1），字节仍在（旧口径=无条件 passthrough）。"""
        _init_git_repo(tmp_path)
        monkeypatch.chdir(tmp_path)
        payload = _create_stash(tmp_path, "manual wip nobody claims", "guard.py")

        r = _run_guard(tmp_path, "stash", "drop", "stash@{0}")

        assert r.returncode == 1, f"stdout={r.stdout}\nstderr={r.stderr}"
        assert "破坏性" in r.stderr, r.stderr
        assert len(_stash_msgs(tmp_path)) == 1
        got = subprocess.run(
            ["git", "show", "stash@{0}:guard.py"],
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
            timeout=20,
        )
        assert got.stdout == payload
        # 阻断也要留痕
        audit = tmp_path / ".runtime" / "gate_audit" / "git_guard_self_harm.jsonl"
        assert audit.exists()
        rows = [json.loads(line) for line in audit.read_text(encoding="utf-8").splitlines() if line.strip()]
        assert rows[-1]["action"] == "stash drop"
        assert rows[-1]["forced"] is False

    def test_stash_drop_allowed_for_dead_owner_with_anchor(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """属主判死 → 闸门放行（rc=0），且 drop 前先落字节锚。"""
        _init_git_repo(tmp_path)
        monkeypatch.chdir(tmp_path)
        sid = "st-guard-dead-0001"
        _register_session(tmp_path, sid, pid=_make_dead_pid())
        _create_stash(tmp_path, f"guard dead owner {sid}", "guard2.py")

        r = _run_guard(tmp_path, "stash", "drop", "stash@{0}")

        assert r.returncode == 0, f"stderr={r.stderr}"
        assert _stash_msgs(tmp_path) == []
        anchors = _refs(tmp_path, "refs/quarantine/")
        assert len(anchors) == 1 and f"stash-{sid}-" in anchors[0]

    def test_non_whitelist_escape_reason_does_not_pass(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """逃生标记必须命中白名单关键词——随便写一句理由不算逃生（禁自造豁免）。"""
        _init_git_repo(tmp_path)
        monkeypatch.chdir(tmp_path)
        _create_stash(tmp_path, "unowned for escape test", "guard3.py")

        env = _clean_env()
        env["ZEPHYR_STASH_DROP_ESCAPE"] = "i-am-in-a-hurry"
        r = subprocess.run(
            [sys.executable, str(_GIT_GUARD), "stash", "drop", "stash@{0}"],
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            timeout=120,
        )

        assert r.returncode == 1, f"stdout={r.stdout}\nstderr={r.stderr}"
        assert len(_stash_msgs(tmp_path)) == 1

    def test_whitelist_escape_still_anchors_before_drop(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """白名单逃生只豁免"归属判定"，不豁免"存证"——放行后字节仍可从锚取回。"""
        _init_git_repo(tmp_path)
        monkeypatch.chdir(tmp_path)
        payload = _create_stash(tmp_path, "escape-but-keep-bytes", "guard4.py")

        env = _clean_env()
        env["ZEPHYR_STASH_DROP_ESCAPE"] = "dead-session-cleanup:registry says reaped"
        r = subprocess.run(
            [sys.executable, str(_GIT_GUARD), "stash", "drop", "stash@{0}"],
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            timeout=120,
        )

        assert r.returncode == 0, f"stdout={r.stdout}\nstderr={r.stderr}"
        assert _stash_msgs(tmp_path) == []
        anchors = _refs(tmp_path, "refs/quarantine/")
        assert len(anchors) == 1, anchors
        got = subprocess.run(
            ["git", "show", f"{anchors[0]}:guard4.py"],
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
            timeout=20,
        )
        assert got.stdout == payload

    def test_stash_clear_blocked_by_default(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """clear 由"仅 warn"升为默认阻断（旧 L610-612 warn 后 passthrough）。"""
        _init_git_repo(tmp_path)
        monkeypatch.chdir(tmp_path)
        _create_stash(tmp_path, "clear me? not without a person", "c1.py")

        r = _run_guard(tmp_path, "stash", "clear")

        assert r.returncode == 1, f"stdout={r.stdout}\nstderr={r.stderr}"
        assert len(_stash_msgs(tmp_path)) == 1

    def test_stash_list_show_still_passthrough(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """只读子命令不受影响（别把闸门拧成新故障源）。"""
        _init_git_repo(tmp_path)
        monkeypatch.chdir(tmp_path)
        _create_stash(tmp_path, "read only please", "r1.py")

        assert _run_guard(tmp_path, "stash", "list").returncode == 0
        assert _run_guard(tmp_path, "stash", "show", "stash@{0}").returncode == 0
