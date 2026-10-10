# [A_test] module_id: MOD-GOV_non_target_unstage_anchor_redproof | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.gov.git.test_non_target_unstage_anchor_redproof
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.git_commit_gateway; zephyr.infrastructure.rollback.forward_fix_runner; scripts.governance.audit_worktree_ops_telemetry
# [CONSUMERS] CI
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 测试隔离——一切 git/锚区/审计写在 tmp_path 临时仓内，禁写生产路径（根宪法 §9.6）
# [MODIFY-GUARD] 红证含 pristine 对照：断言的是 dev 原始字节的缺陷，禁把 pristine 件改成本版
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] self
# [TTL] task_bound
"""test_non_target_unstage_anchor_redproof.py — S3/S12/脸三 蒸发腿红证（maint2 2026-10-11）

覆盖（任务书红证 1-8 项）：
1. 锚住再 unstage：他人 A 条目 reset 前字节入锚区 + 逐路径 jsonl 留痕 + prescription 可复跑
2. 正向腿不坏：跑完后 index 里确实没有 non-target 条目（没被吸进我的 commit）
3. 归属：活属主命中＝claim 册真属主；查无＝null+ownerless（禁猜）
4. 反向钉桩：目标文件不被锚区/留痕逻辑动到
5. S12：四族新模式真匹配（argv 列表形态 + 裸 cmdline 形态），既有模式仍命中
6. forward_fix：修复后只提交自家文件；pristine（dev 原始字节）会把他人条目吸进 commit
7. pristine 红证：三件 dev 原版各自的缺陷成立读数
8. fail-closed：锚区写不进去时仍落一行留痕并标 anchor_failed
"""

from __future__ import annotations

import hashlib
import importlib.util
import inspect
import json
import os
import re
import subprocess
import sys
import uuid
from pathlib import Path

import pytest

_LANE_ROOT = Path(__file__).resolve().parents[3]
if str(_LANE_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_LANE_ROOT / "src"))

from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import (  # noqa: E402
    GitCommitGateway,
)
from zephyr.infrastructure.rollback import forward_fix_runner as ffr_mod  # noqa: E402
from zephyr.infrastructure.rollback.forward_fix_runner import ForwardFixRunner  # noqa: E402
from zephyr.security.access_control.session_concurrency import SessionRegistry  # noqa: E402

# 施工基线（任务书记载的 dev HEAD）——pristine 件的对账锚点，禁写 "dev"（合并后即漂移）
BASELINE_SHA = "cfbebbf8dd49f8b8ae935d186f4fbe7f8cfc6c66"

# ── pristine 字节＝基线 commit 的内容寻址对象（不复制整档进库）─────────────────
# 为什么不落 `.orig` 副本：①docs/_working/ 目录契约只允 .md/.csv/.yaml/.html/.json
# （DCR-005/006 实测拦 .orig，且 .json 进 _working 亦被禁）；②根宪法 §4 全资产净零
# 禁上 MB 级重复件；③blob 由 BASELINE_SHA 永久可达＝同等耐久、零漂移。
# 下方 sha256 是钉死的对账锚：实测与当初落盘的 .orig 副本逐字节同值（等价性已证）。
PRISTINE_SPECS = {
    "git_commit_gateway.py": "src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py",
    "audit_worktree_ops_telemetry.py": "scripts/governance/audit_worktree_ops_telemetry.py",
    "forward_fix_runner.py": "src/zephyr/infrastructure/rollback/forward_fix_runner.py",
}
PRISTINE_SHA256 = {
    "git_commit_gateway.py": "409ad31446c62a8ee0adc7c5a7336a823e61cd0ed92a8089a99eefb09cf57bc0",
    "audit_worktree_ops_telemetry.py": "9c1511f83ad60835b789311eb23a3f0fba14d4ad916233ce1bf4e48d03736a66",
    "forward_fix_runner.py": "a64905c668b0b5a7dee73e605405976c0f74221d62c6aff9a760630f88170375",
}


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=str(repo),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def _write(repo: Path, rel: str, content: str) -> Path:
    f = repo / rel
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content, encoding="utf-8", newline="\n")
    return f


def _init_repo(repo: Path) -> Path:
    """tmp git 仓 + 一个已 commit 的基线文件（测试禁写生产路径）。"""
    env = os.environ.copy()
    env.update(
        {
            "GIT_AUTHOR_NAME": "Test",
            "GIT_AUTHOR_EMAIL": "t@t",
            "GIT_COMMITTER_NAME": "Test",
            "GIT_COMMITTER_EMAIL": "t@t",
        }
    )
    repo.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init"], cwd=str(repo), capture_output=True, env=env, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=str(repo), env=env, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=str(repo), env=env, check=True)
    _write(repo, "base.txt", "base\n")
    _write(repo, "keep.txt", "keep\n")
    subprocess.run(["git", "add", "base.txt", "keep.txt"], cwd=str(repo), env=env, check=True)
    subprocess.run(
        ["git", "commit", "-m", "init", "--no-verify"],
        cwd=str(repo),
        env=env,
        capture_output=True,
        check=True,
    )
    return repo


def _make_registry(repo: Path) -> SessionRegistry:
    """真实 claim 册，但**先自证锚在 tmp 内**再返回（禁写主区/车道生产名册）。"""
    reg = SessionRegistry(repo)
    got = os.path.normcase(str(reg._registry_path))
    want = os.path.normcase(str(repo))
    assert got.startswith(want), f"registry 逃逸出 tmp 仓（禁写生产名册）: {reg._registry_path}"
    return reg


def _gw(repo: Path, registry: SessionRegistry | None = None) -> GitCommitGateway:
    return GitCommitGateway(project_root=repo, registry=registry or _make_registry(repo))


def _staged_paths(repo: Path) -> set[str]:
    r = _git(repo, "diff", "--cached", "--name-only")
    return {ln.strip().replace("\\", "/").lower() for ln in r.stdout.splitlines() if ln.strip()}


def _audit_records(repo: Path) -> list[dict]:
    p = repo / ".runtime" / "gate_audit" / "non_target_unstage.jsonl"
    if not p.exists():
        return []
    return [json.loads(ln) for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()]


def _anchor_files(repo: Path, actor: str, rel: str) -> list[Path]:
    root = repo / ".runtime" / "quarantine" / "non_target_unstage" / actor
    return sorted(root.glob(f"*/{rel}")) if root.exists() else []


def _load_from_file(path: Path, alias: str, tmp_dir: Path | None = None):
    """按字节加载模块（pristine `.orig` 件先落成同名 .py 才可导入）。"""
    assert path.exists(), f"件缺失: {path}"
    target = path
    if path.suffix != ".py":
        dst_dir = (tmp_dir or path.parent) / "pristine_mods" / alias
        dst_dir.mkdir(parents=True, exist_ok=True)
        target = dst_dir / f"{alias}.py"
        target.write_bytes(path.read_bytes())
    name = f"{alias}_{uuid.uuid4().hex[:8]}"
    spec = importlib.util.spec_from_file_location(name, str(target))
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _pristine_raw(stem: str) -> bytes:
    """按钉死的基线 commit 现取原始字节（内容寻址，blob 永久可达）。

    MUST 二进制读：本模块的 `_git` 走文本模式（universal newlines 会把 CRLF 折成 LF），
    那会改动字节使 sha 对账失真——行尾是第四把口径，在册教训同型。
    """
    proc = subprocess.run(
        ["git", "-C", _LANE_ROOT.as_posix(), "show", f"{BASELINE_SHA}:{PRISTINE_SPECS[stem]}"],
        capture_output=True,
        check=False,
    )
    assert proc.returncode == 0, f"基线 blob 取回失败 {stem}: {proc.stderr[:200]}"
    raw = proc.stdout
    assert hashlib.sha256(raw).hexdigest() == PRISTINE_SHA256[stem], "pristine 字节与钉死基线不符（红证失真）"
    return raw


def _load_pristine(tmp_path: Path, orig_name: str, alias: str):
    stem = orig_name[: -len(".orig")] if orig_name.endswith(".orig") else orig_name
    dst = tmp_path / "pristine_src" / stem
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(_pristine_raw(stem))
    return _load_from_file(dst, alias, tmp_path)


def _live_telemetry():
    return _load_from_file(_LANE_ROOT / "scripts" / "governance" / "audit_worktree_ops_telemetry.py", "telemetry_live")


@pytest.fixture(autouse=True)
def _git_identity(monkeypatch):
    """git commit 身份（forward_fix 真提交用；进程内 env，不落任何仓配置）。"""
    monkeypatch.setenv("GIT_AUTHOR_NAME", "Test")
    monkeypatch.setenv("GIT_AUTHOR_EMAIL", "t@t")
    monkeypatch.setenv("GIT_COMMITTER_NAME", "Test")
    monkeypatch.setenv("GIT_COMMITTER_EMAIL", "t@t")


# ── 红证 1/2/8：锚 + 留痕 + 正向腿 ────────────────────────────────────────────
class TestAnchorAndTrail:
    def test_anchor_then_unstage_bytes_and_jsonl(self, tmp_path: Path) -> None:
        repo = _init_repo(tmp_path)
        other_content = "OTHER SESSION WORK IN FLIGHT\nprint(1)\n"
        _write(repo, "other_dir/new_face.py", other_content)
        assert _git(repo, "add", "other_dir/new_face.py").returncode == 0
        # 我自己的目标条目（不在 non_target 清单里，绝不许被动）
        _write(repo, "base.txt", "mine\n")
        assert _git(repo, "add", "base.txt").returncode == 0

        gw = _gw(repo)
        # 真实现场形态：调用方传的是 normcase 后的反斜杠路径（Windows）
        ok, err = gw._unstage_non_target_files(["other_dir\\new_face.py"], session_id="actor-sess")
        assert ok, f"unstage 应成功: {err}"

        # ① 锚区出现该文件字节且 sha 相等
        anchors = _anchor_files(repo, "actor-sess", "other_dir/new_face.py")
        assert len(anchors) == 1, f"锚区应恰有 1 份: {anchors}"
        assert anchors[0].read_text(encoding="utf-8") == other_content, "锚区字节须与在飞面逐字节相等"
        rec = _audit_records(repo)
        assert len(rec) == 1, f"应恰落一行留痕: {rec}"
        rec = rec[0]
        anchor_sha = _git(repo, "hash-object", str(anchors[0])).stdout.strip()
        assert anchor_sha == rec["index_blob_sha"], "锚区 bytes 的 git blob sha 必须等于 index blob sha"
        # ② jsonl 字段口径
        assert rec["path"] == "other_dir/new_face.py"
        assert rec["staged_state"] == "A"
        assert rec["actor_session"] == "actor-sess"
        assert rec["bytes"] == len(other_content.encode("utf-8"))
        assert rec["anchored_from"] == "worktree"
        assert rec["did_unstage"] is True
        assert rec["absorbed"] is False
        assert rec["anchor_failed"] is False
        assert rec["anchored_to"] and rec["anchored_to"].startswith(".runtime/quarantine/non_target_unstage/")
        # 正向腿（红证 2）：index 里确实不再有 non-target 条目，我的目标条目原样在
        staged = _staged_paths(repo)
        assert "other_dir/new_face.py" not in staged, "他人条目应已被 unstage（行为不变）"
        assert "base.txt" in staged, "我自己的目标条目不许被 unstage"

    def test_prescription_rebuilds_evicted_entry(self, tmp_path: Path) -> None:
        """复位管线断成可执行动作：他人面被第二腿物理移出盘面后，按 prescription 复跑。"""
        repo = _init_repo(tmp_path)
        content = "IN FLIGHT THEN EVICTED\n"
        disk = _write(repo, "src_like/evicted.py", content)
        assert _git(repo, "add", "src_like/evicted.py").returncode == 0
        gw = _gw(repo)
        ok, _ = gw._unstage_non_target_files(["src_like/evicted.py"], session_id="actor-sess")
        assert ok
        rec = _audit_records(repo)[0]
        # 模拟另一条腿：未跟踪清扫把 ?? 文件物理移出盘面（字节损失现场）
        disk.unlink()
        assert not disk.exists()
        assert rec["prescription"], "留痕必须带可复跑处方"
        r = subprocess.run(
            ["bash", "-c", rec["prescription"]],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        assert r.returncode == 0, f"prescription 复跑应成功: {r.stdout}{r.stderr}"
        staged = _staged_paths(repo)
        assert "src_like/evicted.py" in staged, "复跑处方后条目应回到 index"
        assert _git(repo, "rev-parse", ":src_like/evicted.py").stdout.strip() == rec["index_blob_sha"], (
            "复位后的 blob sha 必须与留痕记录逐位相等（字节级复位，非同名空壳）"
        )

    def test_anchor_only_is_nondestructive(self, tmp_path: Path) -> None:
        """锚动作本身零破坏：只锚不 reset 时 index 条目必须原样还在。"""
        repo = _init_repo(tmp_path)
        _write(repo, "other_dir/in_flight.py", "still staged\n")
        assert _git(repo, "add", "other_dir/in_flight.py").returncode == 0
        gw = _gw(repo)
        facts = gw._anchor_non_target_paths(["other_dir/in_flight.py"], actor_session="actor-sess")
        key = os.path.normcase("other_dir/in_flight.py")
        assert facts[key]["staged_state"] == "A"
        assert facts[key]["anchor_failed"] is False
        assert "other_dir/in_flight.py" in _staged_paths(repo), "锚不许动 index"
        assert _audit_records(repo) == [], "留痕在 reset 之后写（did_unstage 要真值）"

    def test_fail_closed_when_anchor_write_fails(self, tmp_path: Path, monkeypatch) -> None:
        """红证 8：锚区写不进去（磁盘异常）时不得静默跳过留痕。"""
        repo = _init_repo(tmp_path)
        _write(repo, "other_dir/disk_error.py", "X\n")
        assert _git(repo, "add", "other_dir/disk_error.py").returncode == 0
        gw = _gw(repo)
        import shutil

        def _boom(*a, **k):
            raise OSError("disk full (simulated)")

        monkeypatch.setattr(shutil, "copy2", _boom)
        ok, err = gw._unstage_non_target_files(["other_dir/disk_error.py"], session_id="actor-sess")
        assert ok, f"锚失败不许阻断 unstage（行为不变）: {err}"
        rec = _audit_records(repo)
        assert len(rec) == 1, f"锚失败仍必须落一行留痕: {rec}"
        assert rec[0]["anchor_failed"] is True
        assert rec[0]["anchored_to"] is None
        assert rec[0]["did_unstage"] is True

    def test_target_file_untouched_by_anchor_logic(self, tmp_path: Path) -> None:
        """红证 4（反向钉桩）：目标文件不得被锚区/留痕逻辑动到。"""
        repo = _init_repo(tmp_path)
        _write(repo, "other_dir/foreign.py", "foreign\n")
        assert _git(repo, "add", "other_dir/foreign.py").returncode == 0
        mine = _write(repo, "keep.txt", "mine modified\n")
        assert _git(repo, "add", "keep.txt").returncode == 0
        sha_before = _git(repo, "rev-parse", ":keep.txt").stdout.strip()
        gw = _gw(repo)
        # 清单里只有他人面（真实调用方 _verify_staged_is_clean 的差集口径）
        gw._unstage_non_target_files(["other_dir/foreign.py"], session_id="actor-sess")
        assert _anchor_files(repo, "actor-sess", "keep.txt") == [], "目标文件不许进锚区"
        rec = _audit_records(repo)
        assert [r["path"] for r in rec] == ["other_dir/foreign.py"], "留痕只记 non-target"
        assert mine.read_text(encoding="utf-8") == "mine modified\n"
        assert _git(repo, "rev-parse", ":keep.txt").stdout.strip() == sha_before, "目标 index 条目不许变形"

    def test_full_no_pathspec_commit_wiring_anchors_foreign(self, tmp_path: Path) -> None:
        """接线验证：真走 `_commit_with_file_message` 无 pathspec 分支（非只测私有函数）。

        他人 A 条目 + 我的 M 目标条目同处共享 index ⇒ 触发条件与今晨现场一致；
        断言 commit 只含我的文件，且他人面**已被锚住并留痕**（链路真通）。
        """
        repo = _init_repo(tmp_path)
        _write(repo, "other_dir/foreign_new.py", "FOREIGN NEW FACE\n")
        assert _git(repo, "add", "other_dir/foreign_new.py").returncode == 0
        mine = _write(repo, "base.txt", "mine fixed\n")
        assert _git(repo, "add", "base.txt").returncode == 0
        gw = _gw(repo)
        h, err = gw._commit_with_file_message("test: no pathspec wiring", None, [str(mine)], "actor-sess")
        assert h, f"commit 应成功: {err}"
        names = {
            n.strip() for n in _git(repo, "show", "--name-only", "--format=", "HEAD").stdout.splitlines() if n.strip()
        }
        assert names == {"base.txt"}, f"commit 只许含我的目标文件: {names}"
        assert _anchor_files(repo, "actor-sess", "other_dir/foreign_new.py"), "他人 A 条目必须被锚住"
        rec = _audit_records(repo)
        assert [r["path"] for r in rec] == ["other_dir/foreign_new.py"]
        assert rec[0]["did_unstage"] is True and rec[0]["staged_state"] == "A"

    def test_absorbed_merge_branch_records_without_unstage(self, tmp_path: Path) -> None:
        """A.3：merge 收编腿只加留痕不改行为（did_unstage=false / absorbed=true，不锚）。"""
        repo = _init_repo(tmp_path)
        _write(repo, "other_dir/absorbed.py", "will be absorbed\n")
        assert _git(repo, "add", "other_dir/absorbed.py").returncode == 0
        gw = _gw(repo)
        gw._audit_non_target_unstage(
            ["other_dir/absorbed.py"],
            "actor-sess",
            facts=gw._anchor_non_target_paths(["other_dir/absorbed.py"], actor_session="actor-sess", anchor=False),
            did_unstage={},
            absorbed=True,
        )
        rec = _audit_records(repo)
        assert len(rec) == 1 and rec[0]["absorbed"] is True and rec[0]["did_unstage"] is False
        assert rec[0]["anchored_to"] is None, "收编腿内容进 HEAD 非 erase，不该锚"
        assert rec[0]["staged_state"] == "A" and rec[0]["index_blob_sha"]
        assert "other_dir/absorbed.py" in _staged_paths(repo), "留痕腿不许动 index"


# ── 红证 3：归属判定复用既有单口 ──────────────────────────────────────────────
class TestOwnership:
    def test_owner_sid_is_live_claimer(self, tmp_path: Path) -> None:
        repo = _init_repo(tmp_path)
        held = _write(repo, "other_dir/held_by_bob.py", "bob in flight\n")
        assert _git(repo, "add", "other_dir/held_by_bob.py").returncode == 0
        reg = _make_registry(repo)
        reg.register("bob-sess", pid=os.getpid(), held_files=[str(held)])
        gw = _gw(repo, registry=reg)
        gw._unstage_non_target_files(["other_dir/held_by_bob.py"], session_id="actor-sess")
        rec = _audit_records(repo)[0]
        assert rec["owner_sid"] == "bob-sess", f"归属必须取 claim 册活属主: {rec}"
        assert rec["ownerless"] is False

    def test_ownerless_never_guessed(self, tmp_path: Path) -> None:
        repo = _init_repo(tmp_path)
        _write(repo, "other_dir/no_claim.py", "orphan face\n")
        assert _git(repo, "add", "other_dir/no_claim.py").returncode == 0
        reg = _make_registry(repo)
        # actor 自己 claim 了别的文件——不许被当成他人面的属主
        own = _write(repo, "actor_side.txt", "mine\n")
        reg.register("actor-sess", pid=os.getpid(), held_files=[str(own)])
        gw = _gw(repo, registry=reg)
        gw._unstage_non_target_files(["other_dir/no_claim.py"], session_id="actor-sess")
        rec = _audit_records(repo)[0]
        assert rec["owner_sid"] is None, f"查无归属必须记 null: {rec}"
        assert rec["ownerless"] is True

    def test_dead_session_holder_is_not_owner(self, tmp_path: Path) -> None:
        """判活口径与既有单口一致：死会话的 claim 不构成归属（S3-A PID+TTL）。"""
        repo = _init_repo(tmp_path)
        held = _write(repo, "other_dir/dead_holder.py", "dead held\n")
        assert _git(repo, "add", "other_dir/dead_holder.py").returncode == 0
        reg = _make_registry(repo)
        reg.register("ghost-sess", pid=999999, held_files=[str(held)])
        gw = _gw(repo, registry=reg)
        gw._unstage_non_target_files(["other_dir/dead_holder.py"], session_id="actor-sess")
        rec = _audit_records(repo)[0]
        assert rec["owner_sid"] is None and rec["ownerless"] is True


# ── 红证 5：S12 观测面补齐 ────────────────────────────────────────────────────
class TestErasurePatterns:
    NEW_OPS = {"git_stash_drop_clear", "git_reset_head", "git_checkout_treeish", "git_clean_force"}
    OLD_OPS = {"git_stash_push", "git_restore", "git_checkout_erase", "path_unlink", "shutil_rmtree"}

    @staticmethod
    def _matched_ops(mod, line: str) -> set[str]:
        return {op for pat, op, _sev in mod.ERASURE_PATTERNS if re.compile(pat).search(line)}

    @pytest.mark.parametrize(
        ("line", "op"),
        [
            # 真实 argv 列表形态（现场实测语句）
            ('            ["git", "stash", "drop", ref],', "git_stash_drop_clear"),
            ('        subprocess.run(["git", "stash", "clear"])', "git_stash_drop_clear"),
            ('        result = self.run_git(["git", "reset", "HEAD", "--"] + non_target_files)', "git_reset_head"),
            ('            rc2, _ = _git(root, ["reset", "HEAD", "--", *to_unstage])', "git_reset_head"),
            ('        _git(root, ["reset", "--hard", "deadbeef123"])', "git_reset_head"),
            ('        self.run_git(["git", "checkout", "dev", "--", target])', "git_checkout_treeish"),
            ("    # 处方文案: git checkout -- . 还原整树", "git_checkout_treeish"),
            ('        run_git("git clean -fd")', "git_clean_force"),
            ('        run_git(["git", "clean", "-fdx"])', "git_clean_force"),
        ],
    )
    def test_new_patterns_match_real_forms(self, line: str, op: str) -> None:
        live = _live_telemetry()
        assert op in self.NEW_OPS
        assert op in self._matched_ops(live, line), f"新模式应命中真实形态: {line!r} -> {op}"

    def test_existing_patterns_still_match(self) -> None:
        live = _live_telemetry()
        assert "git_stash_push" in self._matched_ops(
            live, '        r = self.run_git(["git", "stash", "push", "-m", m])'
        )
        assert "git_restore" in self._matched_ops(live, '    run(["git", "restore", "--source", sha, path])')
        assert "git_checkout_erase" in self._matched_ops(live, '    run(["git", "checkout", "--", path])')
        assert "path_unlink" in self._matched_ops(live, "                snap.unlink()")
        assert "shutil_rmtree" in self._matched_ops(live, "        shutil.rmtree(wt_path, ignore_errors=True)")
        assert "quarantine_file" in self._matched_ops(live, "        self._quarantine_file(p)")
        ops = {op for _p, op, _s in live.ERASURE_PATTERNS}
        assert ops >= self.OLD_OPS  # 模式集扩容不许把既有族掉出去

    def test_pristine_telemetry_lacks_four_families(self, tmp_path: Path) -> None:
        """红证 7（S12 半）：dev 原版模式集对四族抹面动作**全盲**（原始字节读数）。"""
        mod = _load_pristine(tmp_path, "audit_worktree_ops_telemetry.py.orig", "telemetry_pristine")
        ops = {op for _p, op, _s in mod.ERASURE_PATTERNS}
        blind = self.NEW_OPS - ops
        assert blind == self.NEW_OPS, f"pristine 应四族全缺，实际缺集={blind}／pristine 全集={ops}"
        probes = [
            '["git", "stash", "drop", ref]',
            'self.run_git(["git", "reset", "HEAD", "--"] + files)',
            'self.run_git(["git", "checkout", "dev", "--", target])',
            'run_git(["git", "clean", "-fdx"])',
        ]
        for line in probes:
            assert self._matched_ops(mod, line) == set(), f"pristine 对 {line!r} 零命中=归因盲区"


# ── 红证 6：forward_fix 共享暂存池归属 ────────────────────────────────────────
class TestForwardFixPathspec:
    @pytest.fixture
    def repo_with_foreign(self, tmp_path: Path) -> Path:
        repo = _init_repo(tmp_path)
        # 他人 staged 条目（未交付工作面）
        _write(repo, "other_inflight.txt", "OTHER SESSION STAGED FACE\n")
        assert _git(repo, "add", "other_inflight.txt").returncode == 0
        # 我自己的修复面（runner 自家产物）
        _write(repo, "base.txt", "fixed by forward fix\n")
        return repo

    def _run(self, runner, repo: Path, target_files) -> dict:
        sha = _git(repo, "rev-parse", "HEAD").stdout.strip()
        res = (
            runner.generate_fix(sha, "boom", target_files)
            if target_files is not None
            else runner.generate_fix(sha, "boom")
        )
        names = _git(repo, "show", "--name-only", "--format=", "HEAD").stdout.splitlines()
        return {
            "result": res,
            "committed": {n.strip().replace("\\", "/").lower() for n in names if n.strip()},
            "staged": _staged_paths(repo),
        }

    def test_fixed_runner_does_not_absorb_foreign(self, tmp_path: Path, repo_with_foreign: Path, monkeypatch) -> None:
        repo = repo_with_foreign
        monkeypatch.setattr(ffr_mod, "REPO_ROOT", repo)
        out = self._run(ForwardFixRunner(project_root=repo), repo, ["base.txt"])
        assert "other_inflight.txt" not in out["committed"], f"他人条目不许进我的 commit: {out['committed']}"
        assert "base.txt" in out["committed"], "自家修复面必须提交"
        assert "other_inflight.txt" in out["staged"], "他人 staged 条目必须原地保留（不 unstage 不吞）"

    def test_pristine_forward_fix_absorbs_foreign(self, tmp_path: Path, repo_with_foreign: Path, monkeypatch) -> None:
        """红证 6/7（原始字节）：dev 原版 `add -A` 确实把他人条目装进自己的 commit。"""
        repo = repo_with_foreign
        mod = _load_pristine(tmp_path, "forward_fix_runner.py.orig", "ffr_pristine")
        monkeypatch.setattr(mod, "REPO_ROOT", repo)
        src = _pristine_raw("forward_fix_runner.py").decode("utf-8")
        assert 'self.run_git(["add", "-A"])' in src, "pristine 原始字节必须含 add -A（防我换基）"
        out = self._run(mod.ForwardFixRunner(project_root=repo), repo, None)
        assert "other_inflight.txt" in out["committed"], (
            f"pristine 归属篡改缺陷应成立（他人条目进我的 commit）: {out['committed']}"
        )

    def test_fail_closed_when_no_own_targets(self, tmp_path: Path, monkeypatch) -> None:
        """自家集为空＝宁可不提交，也不做无 pathspec 全量 commit。"""
        repo = _init_repo(tmp_path / "repo")
        _write(repo, "other_inflight.txt", "OTHER\n")
        assert _git(repo, "add", "other_inflight.txt").returncode == 0
        sha_before = _git(repo, "rev-parse", "HEAD").stdout.strip()
        # patch 产物落在仓外（sibling 目录）⇒ 无可提交的自家文件
        monkeypatch.setattr(ffr_mod, "REPO_ROOT", tmp_path / "outside_repo")
        runner = ForwardFixRunner(project_root=repo)
        res = runner.generate_fix(sha_before, "boom", [])
        assert res.success is False
        assert any("no_own_target_files" in d for d in res.details)
        assert _git(repo, "rev-parse", "HEAD").stdout.strip() == sha_before, "fail-closed 时不许产生新 commit"
        assert "other_inflight.txt" in _staged_paths(repo), "他人条目必须原样留在 index"


# ── 红证 7：pristine 网关无锚无留痕（S3 半）──────────────────────────────────
class TestPristineGatewayRedproof:
    def test_pristine_gateway_has_no_anchor_and_leaves_no_trace(self, tmp_path: Path) -> None:
        mod = _load_pristine(tmp_path, "git_commit_gateway.py.orig", "gw_pristine")
        cls = mod.GitCommitGateway
        assert hasattr(cls, "_anchor_non_target_paths") is False, "pristine 无锚函数=缺陷成立"
        assert hasattr(cls, "_audit_non_target_unstage") is False, "pristine 无逐路径留痕=缺陷成立"
        params = inspect.signature(cls._unstage_non_target_files).parameters
        assert "session_id" not in params, f"pristine 签名无归属参数: {list(params)}"

        repo = _init_repo(tmp_path / "pristine_repo")
        _write(repo, "other_dir/erased.py", "PRISTINE EVAPORATION PROOF\n")
        assert _git(repo, "add", "other_dir/erased.py").returncode == 0
        gw = cls(project_root=repo, registry=_make_registry(repo))
        ok, err = gw._unstage_non_target_files(["other_dir/erased.py"])
        assert ok, f"pristine unstage 本身应成功（缺陷在无痕不在行为）: {err}"
        assert _anchor_files(repo, "unknown", "other_dir/erased.py") == []
        assert not (repo / ".runtime" / "quarantine").exists(), "pristine 锚区目录为空=无复位管线"
        assert _audit_records(repo) == [], "pristine 零留痕=归因盲区（事故无法点名）"
        assert "other_dir/erased.py" not in _staged_paths(repo), "pristine 同样把他人条目 reset 掉"

    def test_pristine_provenance_is_baseline_bytes(self) -> None:
        """pristine 件必须逐字节等于基线 commit 的原始字节（红证不许用改过的基）。"""
        assert (_LANE_ROOT / ".git").exists(), f"非 git 区: {_LANE_ROOT}"
        for name, repo_path in PRISTINE_SPECS.items():
            r = subprocess.run(
                ["git", "-C", _LANE_ROOT.as_posix(), "show", f"{BASELINE_SHA}:{repo_path}"],
                capture_output=True,
            )
            assert r.returncode == 0, f"git show {BASELINE_SHA[:8]}:{repo_path} 失败: {r.stderr[:200]}"
            assert hashlib.sha256(r.stdout).hexdigest() == PRISTINE_SHA256[name], (
                f"基线 {BASELINE_SHA[:8]}:{repo_path} 的字节与钉死 sha 不符——"
                f"红证锚已换基（报告 sha={PRISTINE_SHA256[name]}）"
            )
