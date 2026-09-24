# [A_test] module_id: MOD-GOV-046 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-GOV-046 | scripts/commit_queue.py | §B5 attempts 计数+退避（毒药队首止血）
# [MODULE] tests.governance.test_commit_queue_b5_backoff
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; scripts.commit_queue; scripts.governance.commit_queue_landing
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/governance/test_commit_queue_b5_backoff.py
# [MATURITY] testing
# [INVARIANTS] 全 tmp_path 隔离，不碰真实 .runtime/commit_queue 与 git；只测队列调度面：门禁判据/退出码零耦合；正常件（attempts=0/缺字段）惩罚恒 0 零影响
# [MODIFY-GUARD] st-commitspeed-tbl-20260924 批·B5：重试退回 attempts+1 持久化 / attempts≥3 排队键惩罚退避 / attempts≥5 拾取即死信（dead_reason=attempts_exhausted 附末次失败原因）
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TTL] permanent
"""B5 attempts 计数+退避 —— 判别测试（红证：本文件落笔时对未修码全红）。

毒药机理实证（st-commitspeed-tbl-20260924 提交等待调查 R5 + B4 排队键 docstring
残留风险登记）：landing 环境失败（LandingEnvironmentError）的项退回 pending 时保留
原 created_at，B4 先来先服务下它恒居队首——每轮自举排空白耗一次 landing+终止整轮，
实测 09-24 14:29-15:21 主区 HEAD 零推进 52 分钟即该形态。

B5 止血三件（只动队列调度面，不改门禁判据/退出码）：
  ① 重试退回 pending 前 attempts+1 持久化在项文件（last_failure/last_retry_at 留痕）；
  ② _pick_head 排序键对 attempts≥3 的项加惩罚（+15min/超限次，复用 (created_at,qid)
     排序=延迟可拾取，不挪文件不改状态）；
  ③ attempts≥5 的项拾取即死信（dead_reason=attempts_exhausted 附末次失败原因，
     三分类随末次原因走——env 失败仍归 env 可 requeue），不再白耗 landing。

判别力自证：每条测试在修复前的码上必红（无 attempts 字段/毒药恒居队首/永不死信），
修复后全绿——不存在两边都绿的零判别力形态。
"""

from __future__ import annotations

import json
import threading
from datetime import datetime, timedelta, timezone

import pytest

import scripts.commit_queue as cq
import scripts.governance.commit_queue_landing as cql

# ---------------------------------------------------------------------------
# 工具（全 tmp_path 隔离；项直接写 pending 与 ghost 判别测试同款）
# ---------------------------------------------------------------------------
_OLD_TS = "2026-09-24T00:00:00+08:00"


def _mk_item(
    qid: str, *, created_at: str = _OLD_TS, attempts: int | None = None, last_failure: str | None = None
) -> dict:
    item: dict = {
        "qid": qid,
        "session_id": "s-b5-test",
        "created_at": created_at,
        "base_head": "",
        "meta": {},
        "files": [{"path": "docs/_working/b5_stub.txt"}],
    }
    if attempts is not None:
        item["attempts"] = attempts
    if last_failure is not None:
        item["last_failure"] = last_failure
    return item


def _write_pending(root, item: dict):
    p = root / "pending" / f"{item['qid']}.json"
    p.write_text(json.dumps(item, ensure_ascii=False), encoding="utf-8")
    return p


def _read_state(root, qid: str, state: str = "pending") -> dict:
    p = root / state / f"{qid}.json"
    assert p.exists(), f"qid={qid} 应在 {state}/"
    return json.loads(p.read_text(encoding="utf-8"))


def _fresh_ts() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat()


class _EnvFailLanding:
    """毒药 landing：恒抛环境失败（退回 pending 语义，绝不死信的既有语义）。"""

    def __init__(self):
        self.calls = 0

    def __call__(self, item, root):
        self.calls += 1
        raise cq.LandingEnvironmentError("git index.lock 争用（B5 测试毒药）")


class _OkLanding:
    """正常 landing：恒落地成功。"""

    def __init__(self):
        self.calls = 0

    def __call__(self, item, root):
        self.calls += 1
        return cq.LandingResult(ok=True, reason="", landed_id="b" * 40)


# ---------------------------------------------------------------------------
# ① attempts 计数：重试退回 pending 前 +1 持久化
# ---------------------------------------------------------------------------
class TestAttemptsCounting:
    def test_env_fail_retry_increments_attempts_and_persists(self, tmp_path):
        root = tmp_path / "q"
        cq._ensure_dirs(root)
        _write_pending(root, _mk_item("q-b5-count-0001"))
        landing = _EnvFailLanding()

        stats = cq.drain_queue(queue_root=root, landing=landing, done_ttl_days=None)

        item = _read_state(root, "q-b5-count-0001")
        assert item.get("attempts") == 1, "环境失败退回 pending 必须持久化 attempts=1（未修码无此字段=红）"
        assert "index.lock" in item.get("last_failure", ""), "末次失败原因应留痕供死信三分类"
        assert item.get("last_retry_at"), "重试时刻应留痕"
        assert landing.calls == 1
        assert stats["dead"] == 0, "环境失败绝不死信（既有语义不变）——计数≠死信"

    def test_second_round_increments_again(self, tmp_path):
        root = tmp_path / "q"
        cq._ensure_dirs(root)
        _write_pending(root, _mk_item("q-b5-count-0002", attempts=1))
        cq.drain_queue(queue_root=root, landing=_EnvFailLanding(), done_ttl_days=None)
        item = _read_state(root, "q-b5-count-0002")
        assert item.get("attempts") == 2, "第二轮重试应累加（attempts=1→2），不重置不覆盖"

    def test_bump_failure_never_blocks_return_to_pending(self, tmp_path, monkeypatch):
        """持久化失败（IO 瞬态）不得阻断退回 pending——宁漏计数不丢物品。"""
        root = tmp_path / "q"
        cq._ensure_dirs(root)
        path = _write_pending(root, _mk_item("q-b5-count-0003"))

        import scripts.commit_queue as cq_mod

        def broken_write(p, data):
            raise OSError("disk full（测试注入）")

        monkeypatch.setattr(cq_mod, "_atomic_write", broken_write)
        cq.drain_queue(queue_root=root, landing=_EnvFailLanding(), done_ttl_days=None)
        assert (root / "pending" / path.name).exists(), "退回 pending 必须照常发生"


# ---------------------------------------------------------------------------
# ② 排队键退避：attempts≥3 加惩罚键，毒药件让出队首
# ---------------------------------------------------------------------------
class TestPickHeadBackoff:
    def _two_heads(self, tmp_path, qid_old: str, qid_new: str, attempts_old):
        root = tmp_path / "q"
        root.mkdir(parents=True, exist_ok=True)
        (root / "pending").mkdir(exist_ok=True)
        p_old = _write_pending(root, _mk_item(qid_old, attempts=attempts_old))
        p_new = _write_pending(root, _mk_item(qid_new, created_at=_fresh_ts()))
        return root, [p_old, p_new]

    def test_attempts3_poison_loses_head_to_fresh_item(self, tmp_path):
        root, heads = self._two_heads(tmp_path, "q-b5-poison-0001", "q-b5-fresh-0001", attempts_old=3)
        head, _lane = cq._pick_head(heads)
        assert head is not None and head.stem == "q-b5-fresh-0001", (
            "attempts=3 毒药件必须让出队首给新件（惩罚键生效；未修码按 created_at 恒选毒药=红）"
        )

    def test_attempts_below_threshold_keeps_fifo(self, tmp_path):
        root, heads = self._two_heads(tmp_path, "q-b5-old-0002", "q-b5-fresh-0002", attempts_old=2)
        head, _lane = cq._pick_head(heads)
        assert head is not None and head.stem == "q-b5-old-0002", "阈值之下（attempts=2）不惩罚，FIFO 不变"

    def test_penalty_monotonic_in_attempts(self, tmp_path):
        """attempts 越多惩罚越重（4 次比 3 次退得更远）——防轻惩罚下反复插队。

        p4 更老（created_at 更早）但 attempts=4；p3 更新但 attempts=3——惩罚单调
        （步长×超限次）下 p3 有效时刻仍早于 p4 ⇒ 轻者先行。未修码按 created_at
        恒选 p4=红。
        """
        root = tmp_path / "q"
        (root / "pending").mkdir(parents=True)
        older = (datetime.now(timezone.utc).astimezone() - timedelta(seconds=10)).isoformat()
        p4 = _write_pending(root, _mk_item("q-b5-p4-0001", attempts=4, created_at=older))
        p3 = _write_pending(root, _mk_item("q-b5-p3-0001", attempts=3, created_at=_fresh_ts()))
        head, _ = cq._pick_head([p3, p4])
        assert head.stem == "q-b5-p3-0001", "同为毒药时轻者先行（惩罚单调），更老的 p4 不应反超"

    def test_env_off_restores_current_behavior(self, tmp_path, monkeypatch):
        root, heads = self._two_heads(tmp_path, "q-b5-old-0003", "q-b5-fresh-0003", attempts_old=5)
        monkeypatch.setenv(cq._ATTEMPTS_BACKOFF_ENV, "0")
        head, _lane = cq._pick_head(heads)
        assert head is not None and head.stem == "q-b5-old-0003", "开关关闭=回退现行为（created_at FIFO）"

    def test_normal_items_zero_penalty(self, tmp_path):
        root = tmp_path / "q"
        (root / "pending").mkdir(parents=True)
        item = _mk_item("q-b5-norm-0001")
        assert cq._backoff_penalty_seconds(item) == 0.0, "正常件惩罚恒 0——零影响"
        assert cq._backoff_penalty_seconds(None) == 0.0, "项缺失/不可读时惩罚恒 0（不冤枉）"


# ---------------------------------------------------------------------------
# ③ attempts≥5 拾取即死信：不再白耗 landing，队列前进
# ---------------------------------------------------------------------------
class TestAttemptsDeadLetter:
    def test_attempts5_dead_letter_at_pickup_without_landing(self, tmp_path):
        root = tmp_path / "q"
        cq._ensure_dirs(root)
        _write_pending(root, _mk_item("q-b5-dead-0001", attempts=5, last_failure="git index.lock 争用"))
        landing = _EnvFailLanding()

        stats = cq.drain_queue(queue_root=root, landing=landing, done_ttl_days=None)

        assert landing.calls == 0, "attempts≥5 拾取即死信，不再白耗一次 landing（未修码仍会调 landing=红）"
        item = _read_state(root, "q-b5-dead-0001", state="dead")
        assert item["dead_reason"].startswith("attempts_exhausted"), "死因必须注明 attempts 耗尽"
        assert "index.lock" in item["dead_reason"], "死因附末次失败原因供人工三分类"
        assert item.get("dead_at")
        assert stats["dead"] == 1 and stats["done"] == 0
        assert "q-b5-dead-0001" in stats["processed_qids"]
        assert not (root / "pending" / "q-b5-dead-0001.json").exists(), "毒药件移出 pending=队列前进"

    def test_exhausted_env_failure_classified_env_requeueable(self, tmp_path):
        """死因三分类随末次原因走：env 失败耗尽仍归 env（物品无辜可 requeue）。"""
        root = tmp_path / "q"
        cq._ensure_dirs(root)
        _write_pending(
            root,
            _mk_item("q-b5-dead-0002", attempts=6, last_failure="LandingEnvironmentError: git index.lock 争用"),
        )
        cq.drain_queue(queue_root=root, landing=_EnvFailLanding(), done_ttl_days=None)
        item = _read_state(root, "q-b5-dead-0002", state="dead")
        assert cq.classify_dead_reason(item["dead_reason"]) == "env", "耗尽死信的分类必须继承末次 env 失败"

    def test_exhausted_item_does_not_block_following_items(self, tmp_path):
        """毒药件死信后同轮后续正常件照常落地——队首止血的本义。"""
        root = tmp_path / "q"
        cq._ensure_dirs(root)
        _write_pending(root, _mk_item("q-b5-dead-0003", attempts=5))
        _write_pending(root, _mk_item("q-b5-good-0003", created_at=_fresh_ts()))
        stats = cq.drain_queue(queue_root=root, landing=_OkLanding(), done_ttl_days=None)
        assert stats["dead"] == 1 and stats["done"] == 1, "毒药死信不终轮，后续件同轮落地"
        assert _read_state(root, "q-b5-good-0003", state="done").get("landed_id") == "b" * 40


# ---------------------------------------------------------------------------
# 正常件零影响：无 attempts 字段=现行为逐字节不变
# ---------------------------------------------------------------------------
class TestNormalItemsUnaffected:
    def test_normal_fifo_order_and_no_attempts_written(self, tmp_path):
        root = tmp_path / "q"
        cq._ensure_dirs(root)
        _write_pending(root, _mk_item("q-b5-n1-0001"))
        _write_pending(root, _mk_item("q-b5-n2-0001", created_at=_fresh_ts()))
        stats = cq.drain_queue(queue_root=root, landing=_OkLanding(), done_ttl_days=None)
        assert stats["done"] == 2 and stats["dead"] == 0
        assert stats["processed_qids"] == ["q-b5-n1-0001", "q-b5-n2-0001"], "FIFO 序不变"
        for qid in ("q-b5-n1-0001", "q-b5-n2-0001"):
            assert "attempts" not in _read_state(root, qid, state="done"), "正常件不得被写入 attempts 字段"


# ---------------------------------------------------------------------------
# 池化路径（k=4）同语义：_pool_process_item 计数+拾取死信
# ---------------------------------------------------------------------------
class _FakePoolLanding:
    """池工桩：_item_paths 空=零路径锁；repo_root 指向 tmp（装表落 tmp 不落 cwd）。"""

    def __init__(self, behavior):
        self._behavior = behavior
        self.calls = 0
        self.repo_root = None

    def _item_paths(self, item):
        return []

    def __call__(self, item, root):
        self.calls += 1
        return self._behavior(item, root)


class TestPoolPathAttempts:
    def _run_pool_single(self, tmp_path, item: dict, landing):
        root = tmp_path / "q"
        cq._ensure_dirs(root)
        proc = root / "processing" / f"{item['qid']}.json"
        proc.write_text(json.dumps(item, ensure_ascii=False), encoding="utf-8")
        landing.repo_root = tmp_path
        stats: dict = {"dead": 0, "done": 0, "processed_qids": [], "stale_cleared": 0, "cascade_marked": 0}
        shared: dict = {"processed": 0, "budget_left": None, "env_aborted": False}
        cql._pool_process_item(landing, root, proc, stats, threading.Lock(), shared)
        return root, stats, shared

    def test_pool_env_fail_increments_attempts(self, tmp_path):
        root, stats, shared = self._run_pool_single(tmp_path, _mk_item("q-b5-pool-0001"), _FakePoolLanding(_env_fail))
        assert shared["env_aborted"] is True, "环境失败终止旗语义不变"
        item = _read_state(root, "q-b5-pool-0001")
        assert item.get("attempts") == 1, "池化路径重试同样 attempts+1（未修码无字段=红）"

    def test_pool_attempts5_dead_letter(self, tmp_path):
        landing = _FakePoolLanding(_env_fail)
        root, stats, shared = self._run_pool_single(tmp_path, _mk_item("q-b5-pool-0002", attempts=5), landing)
        assert landing.calls == 0, "池化路径拾取即死信，不调 landing"
        assert stats["dead"] == 1
        item = _read_state(root, "q-b5-pool-0002", state="dead")
        assert item["dead_reason"].startswith("attempts_exhausted")


def _env_fail(item, root):
    raise cq.LandingEnvironmentError("git index.lock 争用（B5 池化测试）")
