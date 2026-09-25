# [A_test] module_id: MOD-GOV-047 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-047 | scripts/governance/commit_queue_landing.py | §快照自验/环境重试闸/改道预检/sid 断言
# [MODULE] tests.governance.test_commit_queue_landing_qcure_m5
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; scripts.commit_queue; scripts.governance.commit_queue_landing; zephyr.gov_enforcement.rule_bridge.commit_preflight; zephyr.gov_enforcement.rule_bridge.git_commit_gateway
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/governance/test_commit_queue_landing_qcure_m5.py
# [MATURITY] testing
# [INVARIANTS] 全 tmp 隔离（tmp git 仓 + tmp 队列根）；QCure 战役四施工件红蓝钉——M5.1 写后读回（篡改字节=红、注册表合并基准=绿、耗尽=死信带处方）、M5.2 fresh 子进程两分支+env_retry 活锁治理、M1.2 改道预检 blocking 拒不降级、M3.2 sid 断言封路；计数器断言读 item JSON meta（跨 drain 轮持久化口径）
# [MODIFY-GUARD] st-qcure-20260925 施工线D（landing_materialize/gate_chain 作业簿 §M5）
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] permanent
"""test_commit_queue_landing_qcure_m5.py — QCure 战役施工线D 四件红蓝钉（st-qcure-20260925）。

1. M5.1 快照写后读回自验：_apply_snapshot write_bytes 后读回 sha256 比对（rsync -c
   语义，治 29 笔 SNAPSHOT-NOT-APPLIED）——tmp 仓写盘后篡改字节验证 SnapshotVerifyError
   退 pending、snapshot_retry≥3 升级死信带处方；注册表族基准=三向合并后字节（假基准
   blob_sha256 必假红）。
2. M5.2 gate 装载失败新鲜判别：fresh 子进程同败=确定性册坏即死信；fresh 通过=纪元
   陈旧退 pending 配 env_retry 计数，≥3 死信带重启 daemon 处方（防全队无限 pending 活锁）。
3. M1.2 改道预检：run_preflight blocking → COMMIT_FAILED 拒不降级直提（禁 GW:3911
   fail-safe 老路）；预检设施异常 → 放行入队（既有口径）。
4. M3.2 sid 断言：畸形 session_id 在触达 gateway 前机械死信（CAPABILITY-LOOKUP 审计
   store 按 sid 寻址，断裂=读空册冤杀）。
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
import yaml

import scripts.commit_queue as cq
import scripts.governance.commit_queue_landing as cql
import zephyr.gov_enforcement.rule_bridge.commit_preflight as pf_mod
from zephyr.gov_enforcement.rule_bridge.gate_auto_registrar import GateAutoRegistrationError
from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import CommitResult, CommitStatus

# ---------------------------------------------------------------------------
# 复用 test_commit_queue_landing.py 的 tmp 仓 + 桩 gateway 组装（自含不跨文件 import）
# ---------------------------------------------------------------------------


def _git(cwd: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, timeout=60)
    if check and r.returncode != 0:
        raise AssertionError(
            f"git {' '.join(args)} -> rc={r.returncode}: {r.stderr.decode('utf-8', errors='replace')[:400]}"
        )
    return r


def _git_text(cwd: Path, *args: str) -> str:
    return _git(cwd, *args).stdout.decode("utf-8", errors="replace").strip()


@pytest.fixture()
def tmp_repo(tmp_path: Path) -> Path:
    """裸 git 仓（与既有 landing 测试同款：main 支初提交，dev 同点）。"""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "test")
    _git(repo, "config", "core.autocrlf", "false")
    (repo / ".gitignore").write_text(".runtime/\n.ailocks/\n", encoding="utf-8")
    (repo / "base.txt").write_text("base\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-qm", "init")
    _git(repo, "branch", "dev")
    return repo


@pytest.fixture()
def queue_root(tmp_path: Path) -> Path:
    return tmp_path / "commit_queue"


class _StubGateway:
    """最小桩：claim/release 留痕，commit 做真 git commit（CAS/幂等走真 git）。"""

    def __init__(self, worktree_path: Path) -> None:
        self._wt = worktree_path
        self.events: list[tuple[str, object]] = []

    def claim_files(self, session_id: str, files: list[str], adopt_prior_work: bool = False) -> list[str]:
        self.events.append(("claim", session_id))
        return list(files)

    def release_files(self, session_id: str, files: list[str]) -> None:
        self.events.append(("release", session_id))

    def commit(
        self, session_id: str, files: list[str], message: str, allow_non_worktree: bool = False, **_: object
    ) -> CommitResult:
        self.events.append(("commit", session_id))
        for f in files:
            target = Path(f)
            if target.is_file():
                _git(self._wt, "add", "--", f)
            else:
                _git(self._wt, "rm", "--cached", "--ignore-unmatch", "--", f)
        _git(self._wt, "commit", "--no-verify", "-qm", message)
        return CommitResult(
            status=CommitStatus.OK, message="stub committed", commit_hash=_git_text(self._wt, "rev-parse", "HEAD")
        )


def _make_landing(repo: Path, qroot: Path) -> tuple[cql.WorktreeLanding, _StubGateway]:
    wt = (qroot / "worktree").resolve()
    stub = _StubGateway(wt)
    return cql.WorktreeLanding(repo_root=repo, queue_root=qroot, gateway=stub), stub


def _tampering_write(monkeypatch: pytest.MonkeyPatch, victim_name: str) -> None:
    """写盘后篡改字节（M5.1 病灶模拟：物化静默丢失）。仅命中受害文件，其余写透传。"""
    real_write = Path.write_bytes

    def _tamper(self: Path, data: bytes) -> None:
        real_write(self, data)
        if self.name == victim_name:
            real_write(self, data + b"\x00CORRUPTED")

    monkeypatch.setattr(Path, "write_bytes", _tamper)


# ---------------------------------------------------------------------------
# M5.1 快照写后读回自验
# ---------------------------------------------------------------------------


class TestM51SnapshotVerify:
    def test_write_then_tamper_raises_snapshot_verify_error(
        self, tmp_repo: Path, queue_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """写盘后篡改字节 → SnapshotVerifyError（继承 LandingEnvironmentError，退 pending 向）。"""
        landing, _stub = _make_landing(tmp_repo, queue_root)
        item = cq.enqueue_item("sess-m51a", "feat: m5.1", [("docs/tamper_me.txt", b"clean\n")], queue_root=queue_root)
        _tampering_write(monkeypatch, "tamper_me.txt")

        with pytest.raises(cql.SnapshotVerifyError) as ei:
            landing(item, queue_root)

        assert isinstance(ei.value, cq.LandingEnvironmentError), "必须继承环境专类（drain 退 pending 依赖）"
        assert ei.value.dead_result is None, "首次失败未耗尽，不带死信回执"
        assert getattr(ei.value, "retried_key", "") == "snapshot_retry"
        assert item["meta"]["snapshot_retry"] == 1, "计数落 item meta（内存）"
        processing = queue_root / "processing" / f"{item['qid']}.json"
        if processing.exists():
            assert json.loads(processing.read_text(encoding="utf-8"))["meta"]["snapshot_retry"] == 1, (
                "计数持久化进项 JSON（跨 drain 轮存活）"
            )

    def test_snapshot_verify_error_returns_to_pending_not_dead(
        self, tmp_repo: Path, queue_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """drain 级：首次自验失败按环境失败退回 pending（绝不死信），计数随项走。"""
        landing, _stub = _make_landing(tmp_repo, queue_root)
        item = cq.enqueue_item("sess-m51b", "feat: m5.1", [("docs/tamper_me.txt", b"clean\n")], queue_root=queue_root)
        _tampering_write(monkeypatch, "tamper_me.txt")

        stats = cq.drain_queue(queue_root, landing=landing)

        assert stats["dead"] == 0 and stats["done"] == 0, "首次失败既不死信也不假落地"
        assert list((queue_root / "pending").glob("q-*.json")), "项退回 pending"
        pending_item = json.loads((queue_root / "pending" / f"{item['qid']}.json").read_text(encoding="utf-8"))
        assert pending_item["meta"]["snapshot_retry"] == 1, "计数持久化（下轮可累计升级）"

    def test_snapshot_verify_exhausts_three_retries_to_dead_letter(
        self, tmp_repo: Path, queue_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """连续 3 次篡改 → 第 3 次升级死信，处方含 requeue 指引与总包号。"""
        landing, _stub = _make_landing(tmp_repo, queue_root)
        item = cq.enqueue_item("sess-m51c", "feat: m5.1", [("docs/tamper_me.txt", b"clean\n")], queue_root=queue_root)
        _tampering_write(monkeypatch, "tamper_me.txt")

        with pytest.raises(cql.SnapshotVerifyError):
            landing(item, queue_root)  # 第 1 次：退 pending
        with pytest.raises(cql.SnapshotVerifyError):
            landing(item, queue_root)  # 第 2 次：退 pending
        r = landing(item, queue_root)  # 第 3 次：耗尽 → 死信回执

        assert not r.ok and not r.landed_id, f"耗尽必须死信且无 landed_id: {r}"
        assert "物化静默丢失" in r.reason and "快照已固化在袋 blob" in r.reason
        assert "requeue" in r.reason and "st-qcure-20260925" in r.reason, f"处方不可行动: {r.reason}"
        assert "snapshot_retry=3" in r.reason
        assert _stub_commit_count(_stub) == 0, "自验失败不得有提交逃逸"

    def test_registry_merged_bytes_are_the_baseline_not_blob_sha(self, tmp_repo: Path, queue_root: Path) -> None:
        """注册表族：袋内 blob 与合并后内容必然不同——若误用 blob_sha256 当基准即假红。

        绿 = 三向合并（dev 基础上追加条目）落地成功，读回基准取合并后 in-memory 字节。
        """
        landing, _stub = _make_landing(tmp_repo, queue_root)
        rel = "docs/01_policies_and_standards/_registry/catalogs/qcure_m5_reg.yaml"
        base = "title: t\nentries:\n  - id: a\n    path: a.md\n"
        (tmp_repo / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_repo / rel).write_text(base, encoding="utf-8")
        _git(
            tmp_repo,
            "add",
            ".",
        )
        _git(tmp_repo, "commit", "-qm", "feat: seed registry")
        _git(tmp_repo, "branch", "-f", "dev", "HEAD")

        theirs = "title: t\nentries:\n  - id: a\n    path: a.md\n  - id: b\n    path: b.md\n"
        base_head = _git_text(tmp_repo, "rev-parse", "refs/heads/dev")
        item = cq.enqueue_item(
            "sess-m51d",
            "feat: registry merge",
            [(rel, theirs.encode("utf-8"))],
            queue_root=queue_root,
            options=cq.EnqueueOptions(base_head=base_head),
        )

        r = landing(item, queue_root)

        assert r.ok, f"注册表合并落地被误拦（假基准假红）: {r.reason}"
        assert r.landed_id != cql._NOOP_LANDED_PREFIX + base_head, "合并应有新内容可落（非 noop）"
        landed = _git_bytes_text(tmp_repo, "show", f"refs/heads/{landing.target_branch}:{rel}")
        assert [e["id"] for e in yaml.safe_load(landed)["entries"]] == ["a", "b"], (
            "落地内容=合并结果（ours+theirs），非袋内 theirs 整文件"
        )


def _stub_commit_count(stub: _StubGateway) -> int:
    return len([e for e in stub.events if e[0] == "commit"])


def _git_bytes_text(repo: Path, *args: str) -> str:
    return _git(repo, *args).stdout.decode("utf-8", errors="replace")


# ---------------------------------------------------------------------------
# M5.2 gate 装载失败新鲜判别 + env_retry 活锁治理
# ---------------------------------------------------------------------------


class TestM52GateRegistrationFreshProbe:
    def _boom_gateway(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def _raise(self):
            raise GateAutoRegistrationError("gate roster unreadable: yaml parse boom")

        monkeypatch.setattr(cql.WorktreeLanding, "_get_gateway", _raise)

    def test_fresh_probe_fails_is_deterministic_dead_letter(
        self, tmp_repo: Path, queue_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """子进程同败 = 确定性册坏 → 死信带修册处方（不退 pending 不活锁）。"""
        self._boom_gateway(monkeypatch)
        monkeypatch.setattr(
            cql.WorktreeLanding, "_probe_fresh_gate_registration", lambda self, timeout=120.0: ("fail", "rc=1: boom")
        )
        landing, _stub = _make_landing(tmp_repo, queue_root)
        item = cq.enqueue_item("sess-m52a", "feat: m5.2", [("docs/x.txt", b"x\n")], queue_root=queue_root)

        r = landing(item, queue_root)

        assert not r.ok
        assert "fresh import 亦败" in r.reason and "修册后重投" in r.reason, f"处方缺失: {r.reason}"
        assert (item.get("meta") or {}).get("env_retry") is None, "确定性死信不消耗 env 计数"

    def test_fresh_probe_unreachable_is_env_retry_not_dead(
        self, tmp_repo: Path, queue_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """红队 P1-4 回归钉：probe 自身未完成（OSError/超时）≠确定性缺陷 → 退 pending 计数而非死信。"""
        self._boom_gateway(monkeypatch)
        monkeypatch.setattr(
            cql.WorktreeLanding,
            "_probe_fresh_gate_registration",
            lambda self, timeout=120.0: ("unreachable", "probe 未完成: TimeoutExpired: 120s"),
        )
        landing, _stub = _make_landing(tmp_repo, queue_root)
        item = cq.enqueue_item("sess-m52d", "feat: m5.2", [("docs/x.txt", b"x\n")], queue_root=queue_root)

        with pytest.raises(cq.LandingEnvironmentError):
            landing(item, queue_root)

        assert item["meta"]["env_retry"] == 1, "unreachable 走 env 计数（瞬态），不立即死信"

    def test_fresh_probe_passes_is_stale_epoch_pending_with_retry_cap(
        self, tmp_repo: Path, queue_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """子进程通过 = 本进程纪元陈旧 → 退 pending 计数；第 3 次升级死信带重启处方。"""
        self._boom_gateway(monkeypatch)
        monkeypatch.setattr(
            cql.WorktreeLanding, "_probe_fresh_gate_registration", lambda self, timeout=120.0: ("pass", "")
        )
        landing, _stub = _make_landing(tmp_repo, queue_root)
        item = cq.enqueue_item("sess-m52b", "feat: m5.2", [("docs/x.txt", b"x\n")], queue_root=queue_root)

        for round_no in (1, 2):
            with pytest.raises(cq.LandingEnvironmentError) as ei:
                landing(item, queue_root)
            assert getattr(ei.value, "retried_key", "") == "env_retry", "异常带已计数标记（pool 免二次计数）"
            assert item["meta"]["env_retry"] == round_no
        r = landing(item, queue_root)  # 第 3 次：耗尽 → 死信

        assert not r.ok
        assert "重启 ZephyrAlpha_BeltDaemon" in r.reason, f"重启处方缺失: {r.reason}"
        assert item["meta"]["env_retry"] == 3

    def test_generic_env_failure_livelock_upgrades_to_dead_across_drain_rounds(
        self, tmp_repo: Path, queue_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """全链路 env 计数（泛化环境失败）：3 轮 drain 后同一 item 升级死信，不再无限 pending。"""
        landing, _stub = _make_landing(tmp_repo, queue_root)
        item = cq.enqueue_item("sess-m52c", "feat: m5.2", [("docs/x.txt", b"x\n")], queue_root=queue_root)

        def _boom(self):
            raise RuntimeError("worktree disk gone（模拟环境故障）")

        monkeypatch.setattr(cql.WorktreeLanding, "ensure_worktree", _boom)
        for _ in range(2):
            stats = cq.drain_queue(queue_root, landing=landing)
            assert stats["dead"] == 0, "未耗尽前绝不死信"
            assert list((queue_root / "pending").glob("q-*.json")), "项退回 pending"
        stats = cq.drain_queue(queue_root, landing=landing)  # 第 3 轮

        assert stats["dead"] == 1 and stats["done"] == 0, f"活锁治理失效: {stats}"
        dead = json.loads((queue_root / "dead" / f"{item['qid']}.json").read_text(encoding="utf-8"))
        assert dead["meta"]["env_retry"] == 3, "计数跨 drain 轮持久化"
        assert "env_retry=3" in dead["dead_reason"] and "requeue" in dead["dead_reason"]

    def test_fresh_probe_real_subprocess_contract(self, tmp_path: Path) -> None:
        """真子进程契约：无名册的干净根 → 0 门 warn 合法 → probe 通过。"""
        landing = cql.WorktreeLanding.__new__(cql.WorktreeLanding)
        landing.repo_root = tmp_path  # 探针只读 repo_root，不建 worktree
        state, detail = landing._probe_fresh_gate_registration()
        assert state == "pass", f"干净根 probe 应通过: {detail}"
        assert detail == ""


# ---------------------------------------------------------------------------
# M1.2 reroute 改道预检：blocking 拒不降级
# ---------------------------------------------------------------------------


class _RerouteStubGateway:
    """reroute 最小桩：project_root + 文件解析（预检整体被 mock，不触门禁设施）。"""

    def __init__(self, root: Path) -> None:
        self.project_root = root

    def _resolve_auto_commit_files(self, files: list[str]) -> list[str]:
        return [str(Path(str(self.project_root)) / "auto_x.txt")]


class TestM12ReroutePreflight:
    def _setup_reroute(self, tmp_repo: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[list[dict], list[dict]]:
        (tmp_repo / "auto_x.txt").write_text("auto\n", encoding="utf-8")
        enqueue_calls: list[dict] = []

        def _spy_enqueue(session_id, message, files, **kwargs):
            enqueue_calls.append({"files": list(files)})
            return {"qid": "q-20260925-sess-m12-0001"}

        monkeypatch.setattr(cq, "enqueue_item", _spy_enqueue)
        monkeypatch.setattr(cql, "bootstrap_drain_with_landing", lambda **kw: {"skipped": True})
        return enqueue_calls, []

    def test_preflight_blocking_returns_failed_never_degrades_or_enqueues(
        self, tmp_repo: Path, queue_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """blocking → COMMIT_FAILED + 处方；不 enqueue、不抛异常（抛了会被 GW:3911 降级直提）。"""
        enqueue_calls, _ = self._setup_reroute(tmp_repo, monkeypatch)

        def _forbidden_enqueue(*args, **kwargs):  # 双保险：blocking 不得触达入队
            raise AssertionError("blocking 批次不得改道回入队")

        monkeypatch.setattr(cq, "enqueue_item", _forbidden_enqueue)
        monkeypatch.setenv(cq.QUEUE_ENV_VAR, str(queue_root))
        captured: dict = {}

        class _Blocking:
            blocking = True
            degraded = False

            def render_report(self, session_id: str) -> str:
                return "PREFLIGHT BLOCKED（test）"

        def _spy_pf(gateway, files, session_id, skip_gate_ids=frozenset(), **kwargs):
            captured["skip"] = set(skip_gate_ids)
            captured["audit_event"] = kwargs.get("audit_event")
            captured["files"] = list(files)
            return _Blocking()

        monkeypatch.setattr(pf_mod, "run_preflight", _spy_pf)
        gw = _RerouteStubGateway(tmp_repo)

        r = cql.reroute_auto_commit_to_queue(gw, "sess-m12", [str(tmp_repo / "auto_x.txt")], "chore: blocked")

        assert r.status is CommitStatus.COMMIT_FAILED, f"blocking 必须拒绝: {r.status}"
        assert "不降级" in (r.message or "") and "处方" in (r.message or ""), f"处方缺失: {r.message}"
        assert captured["skip"] == {"SESSION-REQUIRED", "CLAIM-REQUIRED"}, "与并行线 A 同参"
        assert captured["audit_event"] == "enqueue"
        assert all(Path(f).is_absolute() for f in captured["files"]), "绝对路径对齐 _rel_of 判定面"

    def test_preflight_exception_degrades_to_enqueue_pass_with_audit(
        self, tmp_repo: Path, queue_root: Path, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        """预检设施异常 → 放行入队（既有口径：落地侧锁内权威链兜底）+ warning 留痕。"""
        enqueue_calls, _ = self._setup_reroute(tmp_repo, monkeypatch)
        monkeypatch.setenv(cq.QUEUE_ENV_VAR, str(queue_root))
        audits: list[dict] = []
        monkeypatch.setattr(pf_mod, "_write_audit", lambda gateway, record: audits.append(record))

        def _boom(*args, **kwargs):
            raise RuntimeError("preflight infra down")

        monkeypatch.setattr(pf_mod, "run_preflight", _boom)
        gw = _RerouteStubGateway(tmp_repo)

        r = cql.reroute_auto_commit_to_queue(gw, "sess-m12", [str(tmp_repo / "auto_x.txt")], "chore: degraded")

        assert r.status is CommitStatus.OK and r.commit_hash.startswith("QUEUED:"), "异常放行入队"
        assert len(enqueue_calls) == 1
        assert any(a.get("event") == "degraded_pass" for a in audits), "放行须审计留痕"

    def test_preflight_pass_proceeds_to_enqueue(
        self, tmp_repo: Path, queue_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """预检干净放行 → 正常改道入队（QUEUED 回执，既有语义零变化）。"""
        enqueue_calls, _ = self._setup_reroute(tmp_repo, monkeypatch)
        monkeypatch.setenv(cq.QUEUE_ENV_VAR, str(queue_root))

        class _Clean:
            blocking = False
            degraded = False

            def render_report(self, session_id: str) -> str:  # pragma: no cover — 放行不渲染
                return ""

        monkeypatch.setattr(pf_mod, "run_preflight", lambda *a, **k: _Clean())
        gw = _RerouteStubGateway(tmp_repo)

        r = cql.reroute_auto_commit_to_queue(gw, "sess-m12", [str(tmp_repo / "auto_x.txt")], "chore: clean")

        assert r.status is CommitStatus.OK and r.commit_hash.startswith("QUEUED:")
        assert len(enqueue_calls) == 1


# ---------------------------------------------------------------------------
# M3.2 sid 断言（畸形项进链前机械拒绝）
# ---------------------------------------------------------------------------


class TestM32SessionIdAssertion:
    def test_invalid_session_id_dead_letters_before_gateway_touch(self, tmp_repo: Path, queue_root: Path) -> None:
        """空/非法 sid → 死信带处方；零 git 操作、零 gateway 触达（防读空册冤杀）。"""
        landing, stub = _make_landing(tmp_repo, queue_root)
        item = {"qid": "q-20260925-sess-bad-0001", "session_id": "", "message": "m", "files": [], "meta": {}}

        r = landing(item, queue_root)

        assert not r.ok
        assert "session_id 非法" in r.reason and "requeue" in r.reason, f"处方缺失: {r.reason}"
        assert stub.events == [], "断言必须在触达 gateway 前封路"
        assert not (queue_root / "worktree").exists(), "断言不得触发 worktree 创建（零副作用）"

    def test_valid_session_id_passes_assertion(self, tmp_repo: Path, queue_root: Path) -> None:
        """合法项零行为变化（断言只拦畸形，不误伤正常链路）。"""
        landing, _stub = _make_landing(tmp_repo, queue_root)
        item = cq.enqueue_item("sess-m32ok", "feat: m3.2", [("docs/ok.txt", b"ok\n")], queue_root=queue_root)

        r = landing(item, queue_root)

        assert r.ok, f"合法项被断言误伤: {r.reason}"
