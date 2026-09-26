# [A_test] module_id: MOD-TEST-RB14-S1 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-RB14 | scripts/governance/commit_queue_landing.py | §D3 工线程 resilience
# [MODULE] governance.red_blue_pkg14.test_rb14_s1_worker_revival
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] pytest; scripts.governance.commit_queue_landing; conftest(本包)
# [CONSUMERS] pytest 自动发现
# [STARTUP] python -m pytest tests/governance/red_blue_pkg14/test_rb14_s1_worker_revival.py
# [MATURITY] testing
# [INVARIANTS] 全沙盒（tmp 仓+tmp 队列）；独立 serializer 进程用例绝不指向生产队列根；
#   红方手术副本零触碰产品文件（sha256 前后全等断言）；workers>=2（k=1 走 legacy 降级
#   支不进池化路径）；判据：单工一次瞬态异常→就地记档（pool_wave.log claim_raised）
#   续跑全部落地；连错 20 次才 GIVEUP；成功重置 streak；硬杀独立进程→遗孤下一轮
#   _recover_orphans 复活、零双落地。
# [MODIFY-GUARD] 包14 场景1（杀工复活，D3 回归尺）
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] task_bound
"""test_rb14_s1_worker_revival.py — 场景1「杀工复活」红蓝对抗（D3 尺）。

红方攻击=构造单工异常（认领段 RuntimeError 注入/持续注入/BaseException 硬杀进程）。
蓝方判据（D3 修复语义，scripts/governance/commit_queue_landing.py `_worker`）：
  ① 每工一次瞬态异常 → pool_wave.log 就地记档（claim_raised streak=1）后继续，全部落地；
  ② 连错 _WORKER_ERR_STREAK(20) 次才收工（GIVEUP 只出现在 streak=20）；
  ③ 一次成功重置连错计数（19 错+成功+19 错 → 无 GIVEUP 全落地）；
  ④ 独立进程硬杀（os._exit）→ 遗孤留 processing，下一轮 drain 复活收齐，零双落地。

红证（能红）：对 D3 前行为做手术副本（worker 首错即 re-raise=线程死）跑同一攻击——
done<全部、无记档——证明本尺对「工线程早退」有判别力，非恒绿尺。
"""

from __future__ import annotations

import json
import threading
from pathlib import Path

import pytest

import scripts.governance.commit_queue_landing as cql
from governance.red_blue_pkg14._common import (
    LANDING_SRC,
    S1_SUBPROCESS_TEMPLATE,
    enqueue,
    git_text,
    load_surgered,
    make_stub_landing_factory,
    read_wave_log,
    run_py_subprocess,
    sha256_file,
)

_N_ITEMS = 3
_K = 2  # 池化工数（k=1 走 legacy 降级支不进池化路径，红蓝均须 >=2）


def _seed(repo: Path, qroot: Path) -> list[str]:
    qids = []
    for i in range(_N_ITEMS):
        item = enqueue(repo, qroot, "rb14-s1", f"s1/f{i}.txt", f"content {i}\n", f"rb14 s1 item {i}")
        qids.append(item["qid"])
    return qids


def _per_thread_raise_once(real_claim, tl, tag: str):
    """每工线程首次认领注入一次瞬态异常（线程本地，避免共享 schedule 竞态）。"""

    def flaky(root):
        if not getattr(tl, "raised", False):
            tl.raised = True
            raise RuntimeError(f"rb14-S1 注入单次认领异常({tag})")
        return real_claim(root)

    return flaky


# ── 蓝方 ①：单工瞬态异常→就地记档续跑全部落地 ──────────────────────────────


def test_s1_blue_transient_claim_failure_logged_and_survives(sb_repo, sb_queue, monkeypatch):
    _seed(sb_repo, sb_queue)
    real_claim = cql._pool_claim_item
    monkeypatch.setattr(cql, "_pool_claim_item", _per_thread_raise_once(real_claim, threading.local(), "blue1"))
    monkeypatch.setattr(cql, "make_worker_landing", make_stub_landing_factory([]))

    stats = cql.drain_queue_pool(sb_queue, repo_root=sb_repo, workers=_K)

    assert stats["done"] == _N_ITEMS, f"瞬态单错后必须续跑全部落地: {stats}"
    assert not list((sb_queue / "dead").glob("*.json")), "瞬态异常绝不入死信"
    log = read_wave_log(sb_queue)
    raised = [ln for ln in log.splitlines() if "claim_raised RuntimeError" in ln]
    assert len(raised) >= _K, f"每工异常须就地记档: {raised}"
    assert all("streak=1" in ln for ln in raised), f"注入计划=每工恰 1 错，记档须全为 streak=1: {raised}"
    assert "GIVEUP" not in log, "单次瞬态异常不得触发收工"


# ── 蓝方 ②：连错 20 次才收工 ────────────────────────────────────────────────


def test_s1_blue_giveup_only_after_20_consecutive_errors(sb_repo, sb_queue, monkeypatch):
    _seed(sb_repo, sb_queue)

    def always_raise(root):
        raise RuntimeError("rb14-S1 注入持续认领异常")

    monkeypatch.setattr(cql, "_pool_claim_item", always_raise)
    monkeypatch.setattr(cql, "make_worker_landing", make_stub_landing_factory([]))

    stats = cql.drain_queue_pool(sb_queue, repo_root=sb_repo, workers=_K)

    assert stats["done"] == 0, "持续异常下不得有假 done"
    log = read_wave_log(sb_queue)
    raised = [ln for ln in log.splitlines() if "claim_raised" in ln]
    gives = [ln for ln in raised if "GIVEUP" in ln]
    assert len(raised) == _K * cql._WORKER_ERR_STREAK, f"每工连错恰 {cql._WORKER_ERR_STREAK} 次记档: {raised[-4:]}"
    assert len(gives) == _K, f"每工恰一次 GIVEUP: {gives}"
    assert all("streak=20" in ln for ln in gives), "GIVEUP 必须挂在第 20 连错上"
    assert all("GIVEUP" not in ln for ln in raised if "streak=19" in ln), "streak=19 不得 GIVEUP"


# ── 蓝方 ③：成功重置连错计数（19 错+成功+19 错 → 无 GIVEUP）────────────────


def test_s1_blue_success_resets_error_streak(sb_repo, sb_queue, monkeypatch):
    _seed(sb_repo, sb_queue)
    real_claim = cql._pool_claim_item

    def scheduled(root):
        tl = getattr(scheduled, "_tl", None)
        if tl is None:
            tl = threading.local()
            scheduled._tl = tl
        n = getattr(tl, "n", 0)
        tl.n = n + 1
        # 每线程：19 错 → ok → 19 错 → ok → 恒 ok。无重置则第二段第 1 错即累计 20 → GIVEUP。
        if n in set(range(19)) | set(range(20, 39)):
            raise RuntimeError("rb14-S1 计划性认领异常")
        return real_claim(root)

    monkeypatch.setattr(cql, "_pool_claim_item", scheduled)
    monkeypatch.setattr(cql, "make_worker_landing", make_stub_landing_factory([]))

    stats = cql.drain_queue_pool(sb_queue, repo_root=sb_repo, workers=_K)

    assert stats["done"] == _N_ITEMS, f"成功必须重置连错计数（无 GIVEUP 全落地）: {stats}"
    log = read_wave_log(sb_queue)
    assert "GIVEUP" not in log, f"38 次错误被成功切分后绝不允许 GIVEUP: {log[-500:]}"
    assert "claim_none" in log or stats["done"] == _N_ITEMS  # 出口留痕（A3 装表）


# ── 红证：D3 前行为（首错=工死）下本尺必红 ─────────────────────────────────


@pytest.mark.filterwarnings("ignore::pytest.PytestUnhandledThreadExceptionWarning")
def test_s1_red_old_code_workers_die_on_first_error(sb_repo, sb_queue, tmp_path, monkeypatch):
    before = sha256_file(LANDING_SRC)
    old = load_surgered(
        LANDING_SRC,
        [
            (
                "                if err_streak >= _WORKER_ERR_STREAK:\n"
                "                    return\n"
                "                continue\n",
                "                raise  # RB14-OLD: D3 前行为——首错即线程死\n",
            )
        ],
        "cql_rb14_s1_old",
        tmp_path,
        expected_counts=[2],
    )
    assert sha256_file(LANDING_SRC) == before, "产品文件被手术污染（红线）"

    _seed(sb_repo, sb_queue)
    real_claim = old._pool_claim_item
    monkeypatch.setattr(old, "_pool_claim_item", _per_thread_raise_once(real_claim, threading.local(), "red"))

    # 旧副本工不做真落地：processing 项直接标 done（本尺只对「工死后余件无人认领」敏感）
    def old_process(landing, root, processing_path, stats, stats_lock, shared):
        with stats_lock:
            item = json.loads(processing_path.read_text(encoding="utf-8"))
            item["landed_at"] = item.get("created_at")
            item["landed_id"] = "old-replica"
            processing_path.write_text(json.dumps(item, ensure_ascii=False), encoding="utf-8")
            processing_path.replace(root / "done" / processing_path.name)
            stats["done"] += 1
            shared["processed"] += 1

    monkeypatch.setattr(old, "_pool_process_item", old_process)

    stats = old.drain_queue_pool(sb_queue, repo_root=sb_repo, workers=_K)

    # 旧码红象：两工首错齐死 → 本波余件永无人认领 → done=0（决策志旧码判别：done=0）。
    # 注：手术副本保留记档语句（手术只回退 retry 语义），故不对 log 缺失做断言。
    assert stats["done"] == 0, f"旧码（首错工死）应零落地——若此断言失败说明红证失真: {stats}"
    assert not list((sb_queue / "done").glob("*.json")), "旧码不得有 done 件"


# ── 蓝方 ④：独立 serializer 进程硬杀→遗孤复活零双落 ────────────────────────


def test_s1_process_kill_orphan_revival_no_double_landing(sb_repo, sb_queue, tmp_path):
    # 单件播种：硬杀发生在首个 _pool_process_item——另一工在杀点前不可能完成任何件
    # （队列里再无可认领项），done 恒空是确定性结论，非竞态运气。
    enqueue(sb_repo, sb_queue, "rb14-s1", "s1/f0.txt", "content 0\n", "rb14 s1 kill-revival")
    dev_tip0 = git_text(sb_repo, "rev-parse", "refs/heads/dev")

    script = tmp_path / "rb14_s1_worker.py"
    script.write_text(S1_SUBPROCESS_TEMPLATE, encoding="utf-8")

    # 进程 A：认领第 1 件后 os._exit(9) 硬杀（独立 serializer 进程，非 belt）
    r1 = run_py_subprocess(
        script, [str(sb_repo), str(sb_queue), "process_crash_once", str(tmp_path / "a.json")], timeout=300
    )
    assert r1.returncode == 9, (
        f"进程 A 应以注入码 9 退出: rc={r1.returncode} {r1.stderr.decode(errors='replace')[-400:]}"
    )
    assert (sb_queue / "processing").is_dir(), "被杀工的当前项留 processing"
    assert not list((sb_queue / "done").glob("*.json")), "硬杀点不得出现假 done"

    # 进程 B：全新 drain → 遗孤 _recover_orphans 复活 + 收齐
    r2 = run_py_subprocess(script, [str(sb_repo), str(sb_queue), "plain", str(tmp_path / "b.json")], timeout=300)
    assert r2.returncode == 0, f"进程 B 排空失败: {r2.stderr.decode(errors='replace')[-400:]}"
    stats_b = json.loads((tmp_path / "b.json").read_text(encoding="utf-8"))
    assert stats_b["done"] == 1, f"遗孤必须复活且收齐: {stats_b}"

    # 零双落地判据（D4 断链）：done 零重名 + dev 上该文件恰一次提交
    done_names = [p.name for p in (sb_queue / "done").glob("*.json")]
    assert len(done_names) == len(set(done_names)) == 1
    n = git_text(sb_repo, "log", "dev", "--oneline", "--", "s1/f0.txt")
    assert len(n.splitlines()) == 1, f"s1/f0.txt 落地次数 != 1（双落地）: {n}"
    assert git_text(sb_repo, "rev-parse", "refs/heads/dev") != dev_tip0
