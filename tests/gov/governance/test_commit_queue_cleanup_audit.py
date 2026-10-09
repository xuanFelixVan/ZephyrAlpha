# [MODULE] tests.gov.governance.test_commit_queue_cleanup_audit
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] pytest; scripts.commit_queue
# [CONSUMERS] 队列完整性增补令质量守卫：cleanup 移除必留审计行+域限 done/（禁触 pending/processing）
# [INVARIANTS] 全部用例 tmp 队列（零主区）；红证=移除必留痕（消失必留痕铁律）、在途态零触碰
# [MODIFY-GUARD] 新建 2026-10-10 st-regsolo-20261010（总统筹增补令·队列完整性随批测试，tests/ 豁免 token；
#   独立成文件避让他会话 staged 的 test_commit_queue.py WIP 共写）
# [TTL] permanent
"""commit_queue cleanup 队列完整性守卫（总统筹 2026-10-10 增补令）。

病灶（第 4 件队列完整性）：在途 processing 巨袋被扫除后四分区查无、无归档、无死信
——队列层面凭空消失。铁律：①cleanup 只准清 done/ 登记残留（glob 域硬限）；
②凡移除必留审计行（qid+原因+去向，cleanup_audit.jsonl）。
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[5]))

from scripts import commit_queue as cq  # noqa: E402


def _seed_done(queue_root: Path, qid: str, age_days: float) -> None:
    done = queue_root / "done"
    done.mkdir(parents=True, exist_ok=True)
    item = {
        "qid": qid,
        "state": "done",
        "landed_at": (datetime.now().astimezone() - timedelta(days=age_days)).isoformat(),
    }
    (done / f"{qid}.json").write_text(json.dumps(item), encoding="utf-8")


def test_cleanup_removal_writes_audit_line(tmp_path, monkeypatch):
    """红证②：移除必留审计行（qid+原因+去向）。"""
    # worktree 内 tmp 落 .aidrafts 车道 → resolve_queue_root 车道感知会截断重定向；
    # 本测试打桩恒等（隔离自足，不依赖仓库根位置）。
    monkeypatch.setattr(cq, "resolve_queue_root", lambda q=None: Path(q))
    qroot = tmp_path / "commit_queue"
    qroot.mkdir(parents=True)
    _seed_done(qroot, "q-test-audit-0001", age_days=30)
    result = cq.cleanup_done(qroot, ttl_days=7)
    assert result["removed"] == ["q-test-audit-0001"]
    audit = qroot / "cleanup_audit.jsonl"
    assert audit.is_file(), "消失必留痕：cleanup_audit.jsonl 必须在册"
    rec = json.loads(audit.read_text(encoding="utf-8").strip().splitlines()[-1])
    assert rec["qid"] == "q-test-audit-0001"
    assert "done_ttl" in rec["reason"]
    assert rec["destination"] == "deleted"


def test_cleanup_never_touches_pending_or_processing(tmp_path):
    """红证①：pending/processing 在途袋零触碰（glob 域硬限 done/）。"""
    qroot = tmp_path / "commit_queue"
    for zone in ("pending", "processing"):
        (qroot / zone).mkdir(parents=True, exist_ok=True)
        item = {"qid": f"q-test-inflight-{zone}", "state": zone}
        (qroot / zone / f"q-test-inflight-{zone}.json").write_text(json.dumps(item), encoding="utf-8")
    # 把在途两件的 mtime 拨老（若越域扫到必被 TTL 判删——用域限防）
    old = (datetime.now() - timedelta(days=30)).timestamp()
    for zone in ("pending", "processing"):
        f = qroot / zone / f"q-test-inflight-{zone}.json"
        os_touch = f.stat()
        import os

        os.utime(f, (old, old))

    result = cq.cleanup_done(qroot, ttl_days=7)
    assert result["removed"] == [], "在途态必须零触碰（第 4 件队列完整性病灶铁律）"
    for zone in ("pending", "processing"):
        assert (qroot / zone / f"q-test-inflight-{zone}.json").is_file()
    assert (
        not (qroot / "cleanup_audit.jsonl").exists()
        or not (qroot / "cleanup_audit.jsonl").read_text(encoding="utf-8").strip()
    ), "零移除=零审计行"
