# [BLUEPRINT] MOD-GOV-047 | scripts/governance/commit_queue_landing.py | §
# [MODULE] tests.governance.test_commit_queue_contention_reroute
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] stdlib; tests.governance.test_commit_queue_landing (夹具约定对照); scripts.commit_queue; scripts.governance.commit_queue_landing
# [CONSUMERS] pytest（热册三连自动改道 A3 任务1 验收）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 自含不跨测试文件 import（与 test_commit_queue_landing 同款约定）；tests/ 豁免 CREATE-GUARD；测试输出全落 tmp_path（测试隔离铁律）；本件只测分类器纯函数+专类语义+drain 退 pending 参数化三态，不测门禁判定本身（gate 语义归 gateway 测试）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败；不写生产路径
# [TESTS] tests/governance/test_commit_queue_contention_reroute.py（本件）
# [A_module] module_id=MOD-GOV-047 | layer=test | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""热册三连自动改道验收（A3 任务1，st-circ-a3-20260930）。

FOREIGN-CHANGE / HELD-OVERLAP / HOT-FILE-BASE-FRESHNESS 三类阻断集中打
module_translation_registry.yaml 与 capability_canonical_file_registry.yaml 两热册
——多会话并发互踩=结构性并发非物品违规，landing 识别后抛 HotRegistryContentionError
（LandingEnvironmentError 子类）走 env 通道退 pending + B5 attempts 退避，绝不死信回人工。

独立成件原因：tests/governance/test_commit_queue_landing.py 由兄弟车道
st-circ-a1-20260930 持 claim 在飞（第1批 LANDING-TIMEOUT env 类），冲突让位不共件——
本件自含夹具（字节安全 _git/tmp_repo/queue_root 同款约定），零跨文件 import。
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

import scripts.commit_queue as cq
import scripts.governance.commit_queue_landing as cql
from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import CommitResult, CommitStatus

# ---------------------------------------------------------------------------
# 基础工具（与 test_commit_queue_landing 同款约定：字节安全、tmp 隔离）
# ---------------------------------------------------------------------------


def _git(cwd: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, timeout=60)
    if check and r.returncode != 0:
        raise AssertionError(
            f"git {' '.join(args)} -> rc={r.returncode}: "
            f"stderr={r.stderr.decode('utf-8', errors='replace')[:400]} "
            f"stdout={r.stdout.decode('utf-8', errors='replace')[:400]}"
        )
    return r


def _git_text(cwd: Path, *args: str) -> str:
    return _git(cwd, *args).stdout.decode("utf-8", errors="replace").strip()


@pytest.fixture()
def tmp_repo(tmp_path: Path) -> Path:
    """裸 git 仓：main 分支持初始提交，dev 分支同点（落盘目标）。"""
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
    """队列根固定落 tmp_path（隔离真实 .runtime/commit_queue）。"""
    return tmp_path / "commit_queue"


class _ContentionStubGateway:
    """commit 恒返回指定阻断结果的桩（热册并发模拟；claim/release 留痕照旧）。"""

    def __init__(self, worktree_path: Path, status: CommitStatus, message: str) -> None:
        self._wt = worktree_path
        self._status = status
        self._message = message
        self.events: list[tuple[str, object]] = []

    def claim_files(self, session_id: str, files: list[str], adopt_prior_work: bool = False) -> list[str]:
        self.events.append(("claim", (session_id, list(files))))
        return list(files)

    def release_files(self, session_id: str, files: list[str]) -> None:
        self.events.append(("release", (session_id, list(files))))

    def commit(  # noqa: PLR0913 — 与 WorktreeLanding 调用签名逐参对齐
        self,
        session_id: str,
        files: list[str],
        message: str,
        allow_non_worktree: bool = False,
        allow_tracked_drift: bool = False,
        allow_multi_domain: bool = False,
        allow_promote: bool = False,
        lock_wait_timeout: float | None = None,
    ) -> CommitResult:
        self.events.append(("commit", {"session_id": session_id, "files": list(files), "message": message}))
        return CommitResult(status=self._status, message=self._message)


# ---------------------------------------------------------------------------
# 热册三连自动改道（A3 任务1）
# ---------------------------------------------------------------------------


class TestHotRegistryContentionReroute:
    def test_classifier_matches_exactly_three_block_classes(self) -> None:
        # 命中类：两专用 status + COMMIT_FAILED 带 HOT-FILE-BASE-FRESHNESS 门禁标记
        assert cql.is_hot_registry_contention_block("FOREIGN_CHANGE_VIOLATION", "FOREIGN_CHANGE_VIOLATION: x")
        assert cql.is_hot_registry_contention_block("HELD_OVERLAP_VIOLATION", "HELD_OVERLAP_VIOLATION: x")
        assert cql.is_hot_registry_contention_block("COMMIT_FAILED", "门禁 HOT-FILE-BASE-FRESHNESS 阻断: base 漂移")
        # 不命中类：其他门禁阻断/普通 git 失败/成功——死信语义原样保留
        assert not cql.is_hot_registry_contention_block("COMMIT_FAILED", "门禁 COMMIT-SCOPE 阻断: 跨域")
        assert not cql.is_hot_registry_contention_block("COMMIT_FAILED", "git rc=128: did not match")
        assert not cql.is_hot_registry_contention_block("OK", "")
        assert not cql.is_hot_registry_contention_block("NOTHING_TO_COMMIT", "")

    def test_contention_error_is_env_requeue_class_without_env_budget(self) -> None:
        # 继承 LandingEnvironmentError（drain/pool env 分支按类型捕获退 pending）；
        # retried_key="contention" 供 pool 免烧 env_retry 计数（热册并发不耗环境预算）
        err = cql.HotRegistryContentionError("热册并发阻断")
        assert isinstance(err, cq.LandingEnvironmentError)
        assert getattr(err, "retried_key", "") == "contention"

    @pytest.mark.parametrize(
        ("status", "message"),
        [
            (
                CommitStatus.FOREIGN_CHANGE_VIOLATION,
                "FOREIGN_CHANGE_VIOLATION: staged 与 claim 基线不符 "
                "docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml",
            ),
            (
                CommitStatus.HELD_OVERLAP_VIOLATION,
                "HELD_OVERLAP_VIOLATION: 以下文件被其他活跃 session 持有 "
                "docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml",
            ),
            (
                CommitStatus.COMMIT_FAILED,
                "门禁 HOT-FILE-BASE-FRESHNESS 阻断: 热文件基底漂移 "
                "docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml",
            ),
        ],
    )
    def test_contention_block_requeues_to_pending_with_backoff_not_dead(
        self,
        tmp_repo: Path,
        queue_root: Path,
        status: CommitStatus,
        message: str,
    ) -> None:
        wt = (queue_root / "worktree").resolve()
        stub = _ContentionStubGateway(wt, status, message)
        landing = cql.WorktreeLanding(repo_root=tmp_repo, queue_root=queue_root, gateway=stub)
        sid = "sess-hot-a3"
        item = cq.enqueue_item(
            sid,
            "feat: 热册批",
            [("docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml", b"entries: []\n")],
            queue_root=queue_root,
        )

        stats = cq.drain_queue(queue_root, landing=landing)

        # 结构性并发：绝不死信、绝不假成功——项退回 pending 等下次自举
        assert stats["dead"] == 0, f"热册并发不得死信回人工: {stats}"
        assert stats["done"] == 0, f"热册并发不得记 done（假落地防线）: {stats}"
        dev_base = _git_text(tmp_repo, "rev-list", "--max-parents=0", "dev")
        assert _git_text(tmp_repo, "rev-list", f"{dev_base}..dev") == "", "阻断路径不得推进 dev"
        pending_path = queue_root / "pending" / f"{item['qid']}.json"
        assert pending_path.is_file(), f"项应退回 pending: {sorted(p.name for p in (queue_root / 'pending').glob('*'))}"
        requeued = json.loads(pending_path.read_text(encoding="utf-8"))
        # B5 attempts 退避计数已 +1（≥3 次 15min/次惩罚、≥5 次拾取死信兜底防活锁）
        assert int(requeued.get("attempts") or 0) == 1, f"退回应带 attempts+1 退避: {requeued}"
        assert "热册并发" in str(requeued.get("last_failure") or ""), f"退避留痕应可归因热册并发: {requeued}"
        # claim 已被 finally 释放（不占册——持册会话落地后重投即自愈的前提）
        assert stub.events[-1][0] == "release", f"阻断路径必须释放 claim: {[k for k, _ in stub.events]}"
