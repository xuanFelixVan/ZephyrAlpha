# [A_test] module_id: MOD-TEST-RB14-S3 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-RB14 | scripts/commit_queue.py | §drain_queue 环境失败/死信/状态写
# [MODULE] governance.red_blue_pkg14.test_rb14_s3_fault_injection
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] pytest; scripts.commit_queue; _common(本包)
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/governance/red_blue_pkg14/test_rb14_s3_fault_injection.py
# [MATURITY] testing
# [INVARIANTS] 全沙盒（tmp 队列根 + 注入式 landing 可调用体）；判据：
#   ①git 锁占用（LandingEnvironmentError）→ 退回 pending+attempts+1+终止本轮，绝不死信；
#   ②landing 崩（普通 Exception）→ 死信带 reason+prescription+owner_session，队列不卡；
#   ③状态写 ENOSPC → 大声失败（异常出 drain），不静默假绿；重跑后遗孤复活收齐；
#   ④假绿状态写（吞错不写）→ done 件缺 landed_id，尺必须能红。
# [MODIFY-GUARD] 包14 场景3（故障注入）
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] task_bound
"""test_rb14_s3_fault_injection.py — 场景3「故障注入」红蓝对抗（死信路径/无假绿尺）。

红证两件：
  - 环境失败走普通死信（2026-09-10 事故旧语义的手术副本）→ 「环境失败不死信」尺红；
  - 假绿状态写（吞 OSError 假装写了）→ 「done 件必须带 landed_id」尺红。
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.commit_queue as cq
from governance.red_blue_pkg14._common import (
    QUEUE_SRC,
    load_surgered,
    sha256_file,
)

_LOCK_MSG = (
    "fatal: Unable to create 'D:/x/.git/index.lock': File exists. "
    "Another git process seems to be running in this repository"
)


class _FakeLanding:
    """可编程 landing：按 qid 前缀决定行为；记录调用与返回。"""

    def __init__(self) -> None:
        self.calls: list[str] = []

    def __call__(self, item: dict, root: Path):  # noqa: ANN001
        qid = item.get("qid", "?")
        self.calls.append(qid)
        script = (item.get("message") or "").split(":")[0]
        if script == "ENVLOCK":
            raise cq.LandingEnvironmentError(_LOCK_MSG)
        if script == "CRASH":
            raise RuntimeError("ImportError: gate module boom（rb14 注入 landing 崩）")
        if script == "GATEDEAD":
            return cq.LandingResult(ok=False, reason="GATE-IMPORT-FAILED: fresh 子进程同败（确定性册坏）")
        return cq.LandingResult(ok=True, landed_id=f"fake-{qid}")


def _enqueue_scripted(root: Path, tag: str, msg: str) -> str:
    return cq.enqueue_item(tag, msg, [(f"s3/{tag}.txt", f"content {tag}\n".encode())], queue_root=root)["qid"]


# ── 蓝方 ①：git 锁占用=环境失败 → 退回 pending 不死信 ───────────────────────


def test_s3_blue_env_failure_requeues_not_dead(sb_queue):
    q1 = _enqueue_scripted(sb_queue, "rb14-s3a", "ENVLOCK: 占锁件")
    q2 = _enqueue_scripted(sb_queue, "rb14-s3b", "OK: 正常件")
    landing = _FakeLanding()

    stats = cq.drain_queue(sb_queue, landing=landing, done_ttl_days=None)

    # 环境失败：终止本轮（q2 未被 landing），q1 退回 pending 且 attempts+1
    assert landing.calls == [q1], f"环境失败必须终止本轮: {landing.calls}"
    assert stats["done"] == 0 and stats["dead"] == 0, f"环境失败绝不死信: {stats}"
    assert not list((sb_queue / "dead").glob("*.json")), "死信目录必须干净"
    p1 = sb_queue / "pending" / f"{q1}.json"
    assert p1.exists(), "q1 必须退回 pending"
    item = json.loads(p1.read_text(encoding="utf-8"))
    assert item["attempts"] == 1, f"B5：退回前 attempts+1 持久化: {item}"
    assert "index.lock" in item.get("last_failure", ""), "末次失败原因留痕"

    # 环境恢复后重跑收齐（B5 attempts<5 不影响拾取；锁已释放 → 全部按 OK 落）
    stats2 = cq.drain_queue(
        sb_queue,
        landing=lambda item, root: cq.LandingResult(ok=True, landed_id=f"fake-{item['qid']}"),
        done_ttl_days=None,
    )
    assert stats2["done"] == 2, f"恢复后收齐: {stats2}"


def test_s3_red_env_failure_dead_lettered_by_old_semantics(sb_queue, tmp_path, monkeypatch):
    """红证：旧语义（环境失败=死信，2026-09-10 事故形态）下「不死信」尺必红。"""
    before = sha256_file(QUEUE_SRC)
    old = load_surgered(
        QUEUE_SRC,
        [("except LandingEnvironmentError as exc:", "except _Rb14NeverRaised as exc:")],
        "cq_rb14_s3_old",
        tmp_path,
        expected_counts=[1],
        append_tail="\nclass _Rb14NeverRaised(Exception):\n    pass\n",
    )
    assert sha256_file(QUEUE_SRC) == before, "产品文件被手术污染（红线）"
    monkeypatch.setattr(old, "_ATTEMPTS_BACKOFF_ENV", "ZEPHYR_RB14_UNUSED")  # 隔离 B5 计数面
    # A1 瞬态截收网（_transient_env_failure_of，b7acad9ba1 落地）加入后，旧语义手术
    # 副本须同步摘除这道第二截收网才是忠实旧码：否则 env 失败经文本标记再次改道
    # requeue，红证失真（2026-10-01 总集成验收车道 st-circ-integ-20261001 发现并修）。
    monkeypatch.setattr(old, "_transient_env_failure_of", lambda exc: False)

    q1 = _enqueue_scripted(sb_queue, "rb14-s3c", "ENVLOCK: 占锁件")
    landing = _FakeLanding()

    stats = old.drain_queue(sb_queue, landing=landing, done_ttl_days=None)

    # 旧码红象：环境失败被当普通失败 → q1 死信（物品被环境事故拖进坟墓）
    assert stats["dead"] == 1, f"旧码应把环境失败死信化（红证）: {stats}"
    assert (sb_queue / "dead" / f"{q1}.json").exists(), "旧码死信目录有 q1"


# ── 蓝方 ②：landing 崩 → 死信带处方，队列不卡 ───────────────────────────────


@pytest.mark.parametrize(
    "msg,expect_reason",
    [
        ("CRASH: landing 内部崩", "landing 异常: RuntimeError"),
        ("GATEDEAD: gate 装载确定性失败", "GATE-IMPORT-FAILED"),
    ],
)
def test_s3_blue_crash_dead_letter_clean_queue_continues(sb_queue, msg, expect_reason):
    qbad = _enqueue_scripted(sb_queue, "rb14-s3d", msg)
    qok = _enqueue_scripted(sb_queue, "rb14-s3e", "OK: 后续件")
    landing = _FakeLanding()

    stats = cq.drain_queue(sb_queue, landing=landing, done_ttl_days=None)

    assert stats["dead"] == 1 and stats["done"] == 1, f"死信不卡队（后续件同轮落地）: {stats}"
    deadp = sb_queue / "dead" / f"{qbad}.json"
    assert deadp.exists(), "坏件入墓"
    dead = json.loads(deadp.read_text(encoding="utf-8"))
    assert expect_reason in dead["dead_reason"], f"死因如实: {dead['dead_reason']}"
    assert dead.get("prescription"), "M3.3 处方必附"
    assert dead.get("owner_session") == "rb14-s3d", "责任会话随袋落册"
    assert (sb_queue / "done" / f"{qok}.json").exists(), "好件照常落地"
    assert not list((sb_queue / "processing").glob("*.json")), "processing 清空（无滞留）"


# ── 蓝方 ③+红证：状态写 ENOSPC → 大声失败+可恢复；假绿必被尺抓 ──────────────


def test_s3_blue_disk_full_loud_failure_then_recover(sb_queue, monkeypatch):
    q1 = _enqueue_scripted(sb_queue, "rb14-s3f", "OK: 唯一件")
    landing = _FakeLanding()

    real_write = cq._atomic_write

    def enospc(path, data):  # noqa: ANN001
        raise OSError(28, "No space left on device")

    monkeypatch.setattr(cq, "_atomic_write", enospc)
    with pytest.raises(OSError, match="No space left"):
        cq.drain_queue(sb_queue, landing=landing, done_ttl_days=None)
    assert landing.calls == [q1], "landing 已成功（内容已落），死在 done 记账写"
    assert not list((sb_queue / "done").glob("*.json")), "磁盘满不得产生假 done"
    assert (sb_queue / "processing" / f"{q1}.json").exists(), "项留 processing 等孤儿回收"

    # 环境恢复：重跑 → 孤儿回收 → 重落（幂等 landing 返回同 landed_id）→ 收齐
    monkeypatch.setattr(cq, "_atomic_write", real_write)
    stats2 = cq.drain_queue(sb_queue, landing=landing, done_ttl_days=None)
    assert stats2["recovered"] == 1 and stats2["done"] == 1, f"遗孤复活收齐: {stats2}"
    assert stats2["dead"] == 0, "磁盘满绝不死信"
    done_item = json.loads((sb_queue / "done" / f"{q1}.json").read_text(encoding="utf-8"))
    assert done_item.get("landed_id") == f"fake-{q1}", "done 件必须带真实 landed_id"
    assert done_item.get("landed_at"), "done 件必须带 landed_at"


def test_s3_red_fake_green_writer_produced_done_without_landed_id(sb_queue, monkeypatch):
    """红证：假绿状态写（吞 OSError 假装成功）时「done 带 landed_id」尺必红。"""
    q1 = _enqueue_scripted(sb_queue, "rb14-s3g", "OK: 唯一件")

    def fake_green_write(path, data):  # noqa: ANN001
        pass  # 吞掉写入——假绿形态

    monkeypatch.setattr(cq, "_atomic_write", fake_green_write)
    stats = cq.drain_queue(sb_queue, landing=_FakeLanding(), done_ttl_days=None)

    # 假绿后果实证：done 件是「未记账的旧 JSON」，缺 landed_id/landed_at——
    # 这正是蓝方尺（done 必须带 landed_id）要抓的形态；此处断言其确实发生=红证成立。
    assert stats["done"] == 1, f"假绿 writer 骗过了 done 计数: {stats}"
    done_item = json.loads((sb_queue / "done" / f"{q1}.json").read_text(encoding="utf-8"))
    assert not done_item.get("landed_id") and not done_item.get("landed_at"), (
        "红证失真：假绿 writer 未产出缺记账的 done 件——本尺对假绿无判别力"
    )
