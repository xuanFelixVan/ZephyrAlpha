# [TTL] permanent
"""D4 幽灵 pending 双落地 —— 判别测试（红证：本文件落笔时对未修码全红）。

构造依据 .runtime/tmp/cs-tbl/ghost_chain_demo.py 的闭链证明（未打补丁 dev 码 4/4）：
  _mark_cascade_stale 读 pending X 的窗口内，X 被工线程原子认领（rename→processing），
  随后的回写经 _atomic_write 的 os.replace 把 pending/X.json **重新创建**
  （:1060 的 FileNotFoundError 保护对 replace 永不触发）⇒ 幽灵与真件同名并存 ⇒
  ① 再认领抛 FileExistsError（不在 _pool_claim_item 容忍集）⇒ 工线程死亡（D3 症状）；
  ② 另一时序（真件已到 done/）幽灵被再次认领落地 ⇒ done 计数膨胀。

修法两层（本批 D4）：
  ① _mark_cascade_stale：回写前收窄（项已不在 pending 则不回写）+ 回写后清扫
     （processing/done 出现同名 ⇒ 本回写产物即幽灵，当场移除）；
  ② _pool_claim_item：认领前后终止性复查 done/（幽灵弃置续扫，不二次落地）。
F1 补强（redblu_robust.md §五，本批）：
  ③ 清扫改延时二扫（回写后 50ms 待认领 rename 飞行窗落定再查）+ 认领返回前
     pending 残留清源——飞行中 rename 的可见性滞后窗（TestF1InFlightClaimRace）。

判别力自证：每条测试在修复前的码上必红（ghost 复活/幽灵被认领/终态被覆盖），
修复后全绿——不存在两边都绿的零判别力形态。
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import scripts.commit_queue as cq
import scripts.governance.commit_queue_landing as cql


def _mk_item(qid: str, *, depends: list[str] | None = None, base: str = "") -> dict:
    return {
        "qid": qid,
        "session_id": "s-ghost-test",
        "created_at": "2026-09-24T00:00:00+08:00",
        "base_head": base,
        "meta": {"depends_on": depends or []},
        "files": [],
    }


class TestMarkCascadeStaleGhost:
    """① 回写不得复活已被认领的项（读窗竞态）。"""

    def test_writeback_does_not_recreate_claimed_item(self, tmp_path, monkeypatch):
        root = tmp_path / "q"
        cq._ensure_dirs(root)
        item = _mk_item("q-ghost-0001", depends=["q-landed-0001"])
        p = root / "pending" / "q-ghost-0001.json"
        p.write_text(json.dumps(item), encoding="utf-8")

        real_read_text = Path.read_text
        claimed = {"done": False}

        def racing_read_text(self, *args, **kwargs):
            text = real_read_text(self, *args, **kwargs)
            if self == p and not claimed["done"]:
                claimed["done"] = True
                os.rename(p, root / "processing" / p.name)
            return text

        monkeypatch.setattr(Path, "read_text", racing_read_text)

        marked = cq._mark_cascade_stale(root, {"qid": "q-landed-0001", "base_head": "a" * 40})

        assert not p.exists(), "幽灵复活：读窗内项被认领后，回写仍重建了 pending 路径"
        assert (root / "processing" / p.name).exists(), "真件应在 processing"
        assert "q-ghost-0001" not in marked, "幽灵不应计入命中清单"

    def test_writeback_sweeps_ghost_created_in_replace_window(self, tmp_path, monkeypatch):
        """①补充：收窄检查之后、os.replace 之前才被认领 ⇒ 清扫必须当场移除幽灵。"""
        root = tmp_path / "q"
        cq._ensure_dirs(root)
        item = _mk_item("q-ghost-0002", depends=["q-landed-0002"])
        p = root / "pending" / "q-ghost-0002.json"
        p.write_text(json.dumps(item), encoding="utf-8")

        real_atomic = cq._atomic_write

        def racing_atomic(path: Path, data: bytes):
            os.rename(p, root / "processing" / p.name)
            return real_atomic(path, data)

        monkeypatch.setattr(cq, "_atomic_write", racing_atomic)

        cq._mark_cascade_stale(root, {"qid": "q-landed-0002", "base_head": "b" * 40})

        assert not p.exists(), "幽灵残留：replace 窗口内被认领后，回写产物未被清扫"
        assert (root / "processing" / p.name).exists()


class TestPoolClaimTerminalRecheck:
    """② 认领终止性复查：done/ 已有同名 ⇒ 任何活副本都是幽灵，弃置不落地。"""

    def test_claim_discards_ghost_of_landed_item(self, tmp_path):
        root = tmp_path / "q"
        cq._ensure_dirs(root)
        name = "q-20260924-s-0001.json"
        (root / "pending" / name).write_text(json.dumps(_mk_item("q-20260924-s-0001")), encoding="utf-8")
        (root / "done" / name).write_text(
            json.dumps({"qid": "q-20260924-s-0001", "landed_id": "abc123"}), encoding="utf-8"
        )

        claimed = cql._pool_claim_item(root)

        assert claimed is None, "幽灵被认领成 processing：将造成同件二次落地"
        assert not (root / "processing" / name).exists()
        assert not (root / "pending" / name).exists(), "pending 侧幽灵应被清除"
        assert (root / "done" / name).exists(), "终态件不得被动"

    def test_claim_sweeps_processing_copy_when_done_appears(self, tmp_path, monkeypatch):
        """②补充：认领 rename 成功后 done/ 才出现同名（同窗另一时序）⇒ 副本弃置。"""
        root = tmp_path / "q"
        cq._ensure_dirs(root)
        name = "q-20260924-s-0002.json"
        (root / "pending" / name).write_text(json.dumps(_mk_item("q-20260924-s-0002")), encoding="utf-8")

        real_rename = os.rename

        def racing_rename(src, dst, *args, **kwargs):
            result = real_rename(src, dst, *args, **kwargs)
            dst_path = Path(dst)
            if dst_path.parent.name == "processing":
                (root / "done" / dst_path.name).write_text(
                    json.dumps({"qid": "q-20260924-s-0002", "landed_id": "def456"}), encoding="utf-8"
                )
            return result

        monkeypatch.setattr(os, "rename", racing_rename)

        claimed = cql._pool_claim_item(root)

        assert claimed is None or not (root / "processing" / name).exists(), (
            "认领返回的副本在 done 同名出现后仍存活：双落地窗口未闭合"
        )
        assert (root / "done" / name).exists()


class TestF1InFlightClaimRace:
    """③ F1 竞态窗（redblu_robust.md §五）：认领 rename 飞行中，清扫双查皆 False。

    真实形态：_mark_cascade_stale 回写完成后、清扫 exists 检查前，认领 rename 恰在
    飞行中——源侧已 rename 走、目的侧（processing）尚未可见（Windows 杀软/索引器
    可见性滞后放大的窗口）。未修码单次双查皆 False ⇒ 幽灵漏扫 ⇒ 二次认领 +
    首落 done 并存 = 同件双完成（红蓝实测满载 ~1/10：stats.done>N、processed_qids
    同 qid ×2）。修法：回写后延时 50ms 二扫 + 认领返回前 pending 残留清源。
    """

    _VISIBILITY_LAG = 0.03  # 模拟目的侧可见性滞后（须 < 修法延时 0.05s，红蓝双侧确定性）

    def test_sweep_delayed_recheck_removes_inflight_claim_ghost(self, tmp_path, monkeypatch):
        """回写后认领 rename 飞行中 ⇒ 延时二扫必须清掉幽灵；漏扫即双完成入口。"""
        root = tmp_path / "q"
        cq._ensure_dirs(root)
        item = _mk_item("q-f1-0001", depends=["q-landed-f1"])
        p = root / "pending" / "q-f1-0001.json"
        p.write_text(json.dumps(item), encoding="utf-8")
        processing_p = root / "processing" / p.name
        done_p = root / "done" / p.name

        real_atomic = cq._atomic_write
        real_exists = Path.exists
        t0 = [0.0]
        lag = self._VISIBILITY_LAG

        def racing_atomic(path: Path, data: bytes):
            os.rename(p, processing_p)  # 认领 rename 恰在回写前飞行（源侧即走）
            t0[0] = time.monotonic()
            return real_atomic(path, data)  # os.replace 重建 pending 侧 = 幽灵

        def lagged_exists(self, *args, **kwargs):
            if self in (processing_p, done_p) and (time.monotonic() - t0[0]) < lag:
                return False  # 目的侧尚未可见（飞行中/滞后窗）——清扫双查皆 False 的病灶形态
            return real_exists(self)

        monkeypatch.setattr(cq, "_atomic_write", racing_atomic)
        monkeypatch.setattr(Path, "exists", lagged_exists)

        marked = cq._mark_cascade_stale(root, {"qid": "q-landed-f1", "base_head": "c" * 40})

        assert not p.exists(), "幽灵漏扫：飞行窗双查皆 False，回写产物残留 pending（双完成入口）"
        assert processing_p.exists(), "真件应在 processing"
        assert "q-f1-0001" not in marked, "幽灵不应计入命中清单"

        # 红证链（未修码必现双完成形态）：幽灵漏扫后 A 首落 done，B 在 done 可见性滞后
        # 窗内二次认领 ⇒ done 同名与 B 的 processing 副本并存 ⇒ 两副本都记账 =
        # stats.done>N、processed_qids 同 qid ×2 的根因形态。修后 pending 已清 ⇒ None。
        os.rename(processing_p, done_p)  # A 首落
        t0[0] = time.monotonic()  # done 可见性滞后窗重新张开（复刻事发时序）
        claimed = cql._pool_claim_item(root)
        assert claimed is None, "未修码：幽灵被二次认领且 done 已有首落 ⇒ 同件双完成"

    def test_claim_unlinks_pending_residue_after_rename(self, tmp_path, monkeypatch):
        """第二道保险：认领 rename 落定后 pending 同名再现（清扫残留）⇒ 清源不落三手。"""
        root = tmp_path / "q"
        cq._ensure_dirs(root)
        name = "q-f1-0002.json"
        item = _mk_item("q-f1-0002")
        (root / "pending" / name).write_text(json.dumps(item), encoding="utf-8")

        real_rename = os.rename

        def racing_rename(src, dst, *args, **kwargs):
            result = real_rename(src, dst, *args, **kwargs)
            if Path(dst).parent.name == "processing":
                # 清扫写回恰在认领 rename 落定后一线复活 pending 同名（F1 残留形态）
                (root / "pending" / name).write_text(json.dumps(item), encoding="utf-8")
            return result

        monkeypatch.setattr(os, "rename", racing_rename)

        claimed = cql._pool_claim_item(root)

        assert claimed is not None and claimed.exists(), "工应持 processing 真身"
        assert not (root / "pending" / name).exists(), "清扫残留未被清源：第三手可再认领同件"
