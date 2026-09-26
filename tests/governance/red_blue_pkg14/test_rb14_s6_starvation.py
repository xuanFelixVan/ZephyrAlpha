# [A_test] module_id: MOD-TEST-RB14-S6 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-RB14 | scripts/commit_queue.py | §B4 (created_at,qid) FIFO + B5 退避/死信阈 + C1 合批
# [MODULE] governance.red_blue_pkg14.test_rb14_s6_starvation
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] pytest; scripts.commit_queue; _common(本包)
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/governance/red_blue_pkg14/test_rb14_s6_starvation.py
# [MATURITY] testing
# [INVARIANTS] 全沙盒（tmp 队列根+注入式 landing）；判据：
#   ①超大袋+持续小袋灌入：落袋次序=created_at 序（B4 不倒挂），超大袋先落，done==件数；
#   ②毒药件（attempts≥3）排队键退避让位新件（惩罚=未来时刻）；attempts≥5 拾取即死信
#   不再白耗 landing，同轮后续件照常落地；③同会话小袋流 C1 合批=1 袋落地。
# 红证：B5 退避被产品自带 kill switch（ZEPHYR_CQ_ATTEMPTS_BACKOFF=0）关掉后，
# 最老毒药件重新垄断队首——尺对「退避缺失=饿死回潮」有判别力（免手术）。
# [MODIFY-GUARD] 包14 场景6（饿死与独占）
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] task_bound
"""test_rb14_s6_starvation.py — 场景6「饿死与独占」红蓝对抗（B4/B5/C1 尺）。"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest

import scripts.commit_queue as cq


class _OrderRecordingLanding:
    """记录落地次序；对 POISON 标记件永不落地（配 B5 死信阈断言）。"""

    def __init__(self, slow_qids: set[str] | None = None) -> None:
        self.order: list[str] = []
        self.slow = slow_qids or set()
        self.calls: list[str] = []

    def __call__(self, item: dict, root: Path):  # noqa: ANN001
        qid = item["qid"]
        self.calls.append(qid)
        self.order.append(qid)
        return cq.LandingResult(ok=True, landed_id=f"fake-{qid}")


def _enqueue_at(qroot: Path, sid: str, rel: str, created_at: datetime, msg: str = "rb14 s6") -> str:
    """入队后改写 created_at（沙盒内构造到达序，绕开真实时钟粒度）。"""
    item = cq.enqueue_item(sid, msg, [(rel, f"content {rel}\n".encode())], queue_root=qroot)
    p = qroot / "pending" / f"{item['qid']}.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    data["created_at"] = created_at.isoformat()
    data["attempts"] = data.get("attempts", 0)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return item["qid"]


def _enqueue_poison(qroot: Path, sid: str, rel: str, created_at: datetime, attempts: int) -> str:
    qid = _enqueue_at(qroot, sid, rel, created_at)
    p = qroot / "pending" / f"{qid}.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    data["attempts"] = attempts
    data["last_failure"] = "LandingEnvironmentError: 历史环境失败（rb14 构造）"
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return qid


# ── 蓝方 ①：超大袋+持续小袋灌入 → FIFO 不倒挂 ──────────────────────────────


def test_s6_blue_huge_bag_then_small_bags_no_inversion(sb_queue):
    t0 = datetime.now().astimezone()
    # 超大袋（35 文件 <40 硬顶）最早到；随后 5 个他会话小袋灌入
    huge = cq.enqueue_item(
        "rb14-s6-huge",
        "超大袋",
        [(f"s6/huge/f{i:02d}.txt", f"v{i}\n".encode()) for i in range(35)],
        queue_root=sb_queue,
    )
    p = sb_queue / "pending" / f"{huge['qid']}.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    data["created_at"] = t0.isoformat()
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    arrivals: list[tuple[str, str]] = []
    for i in range(5):
        sid = f"rb14-s6-{chr(ord('a') + i)}"  # 字典序与到达序刻意交错
        arrivals.append((sid, _enqueue_at(sb_queue, sid, f"s6/small/{sid}.txt", t0 + timedelta(seconds=10 + i))))

    landing = _OrderRecordingLanding()
    stats = cq.drain_queue(sb_queue, landing=landing, done_ttl_days=None)

    assert stats["done"] == 6, f"全部落地: {stats}"
    expected_head = [huge["qid"]] + [q for _, q in arrivals]
    assert landing.order == expected_head, f"B4 FIFO 倒挂检测：落地序 {landing.order} != 到达序 {expected_head}"
    # 超大袋完整性：35 文件全部记账于 done 件
    done_item = json.loads((sb_queue / "done" / f"{huge['qid']}.json").read_text(encoding="utf-8"))
    assert len(done_item["files"]) == 35, "超大袋文件集零丢失"


# ── 蓝方 ②：毒药退避让位 + attempts≥5 拾取即死信不白耗 landing ──────────────


def test_s6_blue_poison_backoff_yields_and_dead_threshold(sb_queue):
    t0 = datetime.now().astimezone()
    poison = _enqueue_poison(sb_queue, "rb14-s6-pois", "s6/poison.txt", t0, attempts=4)
    fresh = _enqueue_at(sb_queue, "rb14-s6-fresh", "s6/fresh.txt", t0 + timedelta(seconds=5))

    head, _lane = cq._pick_head(sorted((sb_queue / "pending").glob("q-*.json")))
    assert head is not None and head.stem == fresh, (
        f"B5 退避：attempts=4 毒药必须让位（惩罚=未来时刻），新件先走: got {head.stem}"
    )

    # attempts=5：拾取即死信，不再调 landing；同轮后续件照常落地
    dead5 = _enqueue_poison(sb_queue, "rb14-s6-dead", "s6/dead5.txt", t0 - timedelta(hours=1), attempts=5)
    fresh2 = _enqueue_at(sb_queue, "rb14-s6-last", "s6/last.txt", t0 + timedelta(seconds=6))
    landing = _OrderRecordingLanding()
    stats = cq.drain_queue(sb_queue, landing=landing, done_ttl_days=None)

    assert dead5 not in landing.calls, "attempts≥5 拾取即死信：绝不白耗一次 landing"
    assert stats["dead"] == 1, f"毒药入墓: {stats}"
    dead_item = json.loads((sb_queue / "dead" / f"{dead5}.json").read_text(encoding="utf-8"))
    assert dead_item["dead_reason"].startswith("attempts_exhausted"), "死因=退避耗尽"
    assert dead_item.get("prescription"), "死信带处方"
    assert {poison, fresh, fresh2} <= set(landing.order), f"其余件全部落地: {landing.order}"
    assert stats["done"] == 3, f"done==3: {stats}"


def test_s6_red_backoff_kill_switch_restores_head_monopoly(sb_queue, monkeypatch):
    """红证：关掉 B5 退避（产品自带 kill switch）→ 最老毒药件重新垄断队首。"""
    monkeypatch.setenv(cq._ATTEMPTS_BACKOFF_ENV, "0")
    assert not cq._attempts_backoff_enabled(), "kill switch 必须生效（红方杠杆就位）"

    t0 = datetime.now().astimezone()
    poison = _enqueue_poison(sb_queue, "rb14-s6-pois", "s6/poison.txt", t0, attempts=4)
    fresh = _enqueue_at(sb_queue, "rb14-s6-fresh", "s6/fresh.txt", t0 + timedelta(seconds=5))

    head, _lane = cq._pick_head(sorted((sb_queue / "pending").glob("q-*.json")))
    assert head is not None and head.stem == poison, f"红象：无退避时最老毒药件垄断队首: got {head and head.stem}"
    # 蓝方对照：恢复退避 → 毒药让位（同一构造，两态结果相反=尺有判别力）
    monkeypatch.setenv(cq._ATTEMPTS_BACKOFF_ENV, "1")
    head2, _lane2 = cq._pick_head(sorted((sb_queue / "pending").glob("q-*.json")))
    assert head2 is not None and head2.stem == fresh, "退避恢复后毒药必须让位新件"


# ── 蓝方 ③：同会话小袋流 C1 合批 → 一袋落地 ────────────────────────────────


def test_s6_blue_continuous_small_bags_c1_merge(sb_repo, sb_queue):
    wt = str(sb_repo)
    first = cq.enqueue_item(
        "rb14-s6-c1",
        "c1 流第一袋",
        [("s6/c1/a.txt", b"A\n")],
        queue_root=sb_queue,
        options=cq.EnqueueOptions(worktree_root=wt),
    )
    absorbed = []
    for name in ("b", "c", "d"):
        r = cq.enqueue_item(
            "rb14-s6-c1",
            f"c1 流第 {name} 袋",
            [(f"s6/c1/{name}.txt", f"{name.upper()}\n".encode())],
            queue_root=sb_queue,
            options=cq.EnqueueOptions(worktree_root=wt),
        )
        assert r.get("absorbed"), f"第 {name} 袋必须被 C1 吸收: {r}"
        absorbed.append(r["absorbed"]["qid"])

    pending = list((sb_queue / "pending").glob("q-*.json"))
    assert len(pending) == 1, f"4 次入队合为 1 袋: {[p.name for p in pending]}"
    item = json.loads(pending[0].read_text(encoding="utf-8"))
    assert {f["path"] for f in item["files"]} == {"s6/c1/a.txt", "s6/c1/b.txt", "s6/c1/c.txt", "s6/c1/d.txt"}
    assert item["meta"]["merged_count"] == 3, "合批审计链完整"
    for qid in absorbed:
        for d in ("pending", "processing", "done", "dead"):
            assert not (sb_queue / d / f"{qid}.json").exists(), f"absorbed qid 不得落 {d}"

    landing = _OrderRecordingLanding()
    stats = cq.drain_queue(sb_queue, landing=landing, done_ttl_days=None)
    assert stats["done"] == 1, f"一袋一次落地: {stats}"
    # 桩 landing 不写真盘——文件集完整性断言在 done 件 JSON 上（快照语义）
    done_item = json.loads((sb_queue / "done" / pending[0].name).read_text(encoding="utf-8"))
    assert {f["path"] for f in done_item["files"]} == {"s6/c1/a.txt", "s6/c1/b.txt", "s6/c1/c.txt", "s6/c1/d.txt"}, (
        "合批袋文件集零丢失"
    )
