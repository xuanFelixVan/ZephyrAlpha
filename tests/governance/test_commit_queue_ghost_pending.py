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

矿③ MVP（st-qmine-20260925）演进：① 的原地回写被影子旁路取代（级联 stale 改
O_EXCL 写 pending/.stale/<qid>.json，袋体创建后不可变）——写手族唯一根因结构性
消失，① 的断言对象翻转为 append-only 不变量；② 的 landing 侧四补丁按裁定留一版
作保险带（下版净零拆除）。清标/落账/requeue 的影子随迁清理与双读合并另见
TestStaleShadowSidecar / TestStaleShadowLifecycle / TestRequeueShadowAndLineage。

F1 补强（redblu_robust.md §五；考古合并裁定：影子为准、飞行窗保护保留）：
  ③ 清扫改延时二扫（标记写后 50ms 待认领 rename 飞行窗落定再查，介质=影子：
     目的侧落定 ⇒ 刚写的影子失去作用对象就地撤除）+ 认领返回前 pending 残留
     清源——飞行中 rename 的可见性滞后窗（TestF1InFlightClaimRace）。

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
        # 矿③ 影子化后语义收紧：读窗收窄保留——项已认领则影子也不写（stale 无从谈起，
        # 同旧 D4 第一层口径；孤儿影子等波首清扫兜底）
        assert not cq._stale_shadow_path(root, "q-ghost-0001").exists(), "已认领项不得残留影子指令"

    def test_writeback_sweeps_ghost_created_in_replace_window(self, tmp_path, monkeypatch):
        """矿③ MVP 改断言：级联标记走影子旁路后，"回写产物幽灵"这一竞态面结构性消失——
        判别对象翻转为 append-only 不变量：命中只写影子，袋体字节级零改写。"""
        root = tmp_path / "q"
        cq._ensure_dirs(root)
        item = _mk_item("q-ghost-0002", depends=["q-landed-0002"])
        p = root / "pending" / "q-ghost-0002.json"
        original = json.dumps(item, ensure_ascii=False, indent=2)
        p.write_text(original, encoding="utf-8")

        marked = cq._mark_cascade_stale(root, {"qid": "q-landed-0002", "base_head": "b" * 40})

        assert marked == ["q-ghost-0002"]
        assert p.exists() and p.read_text(encoding="utf-8") == original, (
            "append-only：级联标记不得触碰袋体（幽灵写手族根因=原地改写，MVP 后结构性消失）"
        )
        assert "stale" not in json.loads(p.read_text(encoding="utf-8"))["meta"]
        shadow = cq._read_stale_shadow(root, "q-ghost-0002")
        assert shadow is not None and shadow["stale"] is True and shadow["stale_by"] == "q-landed-0002"
        assert shadow["trigger"] == "depends_on"


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


# ---------------------------------------------------------------------------
# 矿③ stale 影子指令 MVP（st-qmine-20260925）：pending 袋 append-only 化——
# 级联 stale 改 O_EXCL 写 pending/.stale/<qid>.json（袋体零改写=幽灵写手族根因
# 结构性消失），读取侧 _read_item 双读合并一版过渡；影子随袋生命周期迁移清理。
# ---------------------------------------------------------------------------


class TestStaleShadowSidecar:
    """影子写入 / 双读合并 / 无影子兼容 / glob 盲区。"""

    def test_first_trigger_source_preserved(self, tmp_path):
        """影子已存在（首个触发源 stale_by）→ 不重标不覆写，同旧 meta.stale 不重标口径。"""
        root = tmp_path / "q"
        cq._ensure_dirs(root)
        qid = "q-shadow-0003"
        (root / "pending" / f"{qid}.json").write_text(
            json.dumps(_mk_item(qid, depends=["q-new-0001"])), encoding="utf-8"
        )
        assert cq._write_stale_shadow(root, qid, "q-first-0001", "depends_on")

        marked = cq._mark_cascade_stale(root, {"qid": "q-new-0001", "base_head": ""})

        assert marked == [], "已有影子（已标）MUST 不重复计入命中"
        assert cq._read_stale_shadow(root, qid)["stale_by"] == "q-first-0001", "首个触发源不被后来者覆写"

    def test_double_read_merges_stale_view(self, tmp_path):
        """读取侧双读：影子存在 ⇒ _read_item 合并 meta.stale 视图（袋体仍零改写）。"""
        root = tmp_path / "q"
        cq._ensure_dirs(root)
        item = _mk_item("q-shadow-0004")
        bag = root / "processing" / "q-shadow-0004.json"
        bag.write_text(json.dumps(item), encoding="utf-8")
        cq._write_stale_shadow(root, "q-shadow-0004", "q-landed-0004", "base_head")

        merged = cq._read_item(bag)

        assert merged["meta"]["stale"] is True
        assert merged["meta"]["stale_by"] == "q-landed-0004"
        assert merged["meta"]["stale_at"]
        assert "stale" not in json.loads(bag.read_text(encoding="utf-8"))["meta"], "合并只作用内存视图，不改袋体"

    def test_no_shadow_read_is_noop(self, tmp_path):
        """无影子兼容：读袋不注入任何 stale 键（历史袋/无级联路径逐字节零感知）。"""
        root = tmp_path / "q"
        cq._ensure_dirs(root)
        item = _mk_item("q-plain-0005")
        bag = root / "pending" / "q-plain-0005.json"
        bag.write_text(json.dumps(item), encoding="utf-8")

        merged = cq._read_item(bag)

        assert "stale" not in merged["meta"]
        assert "stale_by" not in merged["meta"] and "stale_at" not in merged["meta"]

    def test_stale_dir_invisible_to_q_glob(self, tmp_path):
        """.stale 子目录不进 q-*.json glob 视野（队首扫描/四态计数天然白名单）。"""
        root = tmp_path / "q"
        cq._ensure_dirs(root)
        (root / "pending" / "q-vis-0006.json").write_text(json.dumps(_mk_item("q-vis-0006")), encoding="utf-8")
        cq._write_stale_shadow(root, "q-vis-0006", "q-x", "depends_on")

        heads = sorted((root / "pending").glob("q-*.json"))

        assert [h.name for h in heads] == ["q-vis-0006.json"], "影子目录/文件不得被队列扫描误收"


class TestStaleShadowLifecycle:
    """影子随袋生命周期迁移：清标双清 / done/dead 影随迁 / 波首孤儿清扫。"""

    def test_cleared_stale_removes_shadow(self, tmp_path):
        """清标放行=双清：meta 视图 pop + 影子 unlink；done 袋留 stale_by 审计溯源。"""
        root = tmp_path / "q"
        cq._ensure_dirs(root)
        ix = cq.enqueue_item("AI-X", "mx", [("x.txt", b"x")], queue_root=root)
        iy = cq.enqueue_item(
            "AI-Y", "my", [("y.txt", b"y")], queue_root=root, options=cq.EnqueueOptions(depends_on=[ix["qid"]])
        )
        cq.drain_queue(root, max_items=1)
        assert cq._stale_shadow_path(root, iy["qid"]).exists(), "Y 留 pending 期间影子必须在"

        stats = cq.drain_queue(root)

        assert stats["stale_cleared"] == 1 and stats["done"] == 1
        assert not cq._stale_shadow_path(root, iy["qid"]).exists(), "清标放行 MUST 影子随迁清理"
        done_y = json.loads((root / "done" / f"{iy['qid']}.json").read_text(encoding="utf-8"))
        assert "stale" not in done_y["meta"] and done_y["meta"]["stale_by"] == ix["qid"]

    def test_dead_transition_removes_shadow(self, tmp_path):
        """stale 项降死信（cascade_stale）→ 袋进 dead，影子随迁清理。"""
        root = tmp_path / "q"
        cq._ensure_dirs(root)
        ix = cq.enqueue_item("AI-X", "mx", [("x.txt", b"x")], queue_root=root)
        iy = cq.enqueue_item(
            "AI-Y", "my", [("y.txt", b"y")], queue_root=root, options=cq.EnqueueOptions(depends_on=[ix["qid"]])
        )
        p = root / "pending" / f"{iy['qid']}.json"
        it = json.loads(p.read_text(encoding="utf-8"))
        it["files"][0]["base_blob"] = "blob-old"
        p.write_text(json.dumps(it, ensure_ascii=False, indent=2), encoding="utf-8")

        cq.drain_queue(root, head_reader=lambda path: "blob-new")

        dead = json.loads((root / "dead" / f"{iy['qid']}.json").read_text(encoding="utf-8"))
        assert "cascade_stale" in dead["dead_reason"]
        assert not cq._stale_shadow_path(root, iy["qid"]).exists(), "dead 转移点影子 MUST 随迁清理"

    def test_orphan_shadow_swept_at_wave_start(self, tmp_path):
        """孤儿影子（袋已不在 pending）drain 波首兜底清扫；在 pending 的影子不动。"""
        root = tmp_path / "q"
        cq._ensure_dirs(root)
        cq._write_stale_shadow(root, "q-gone-0007", "q-x", "depends_on")
        iq = cq.enqueue_item("AI-Q", "mq", [("q.txt", b"q")], queue_root=root)
        cq._write_stale_shadow(root, iq["qid"], "q-x", "base_head")

        stats = cq.drain_queue(root, landing=lambda i, r: cq.LandingResult(ok=True))

        assert stats["orphan_shadows_swept"] == 1
        assert not cq._stale_shadow_path(root, "q-gone-0007").exists(), "无主影子 MUST 清扫"
        assert not cq._stale_shadow_path(root, iq["qid"]).exists(), "落账随迁（done 转移点清理）"


class TestRequeueShadowAndLineage:
    """requeue 件：影子指令合并进新袋（不丢 stale 语义）+ requeue_lineage 审计留痕。"""

    @staticmethod
    def _make_dead_with_counts(root: Path) -> str:
        item = cq.enqueue_item("AI-R", "m-orig", [("a.txt", b"v1")], queue_root=root)
        cq.drain_queue(root, landing=lambda i, r: cq.LandingResult(ok=False, reason="boom-模拟门禁失败"))
        # 模拟死前计数积累 + 崩溃窗影子残留（生产上 done/dead 转移点已清，此处构造孤儿）
        dead_path = root / "dead" / f"{item['qid']}.json"
        dead = json.loads(dead_path.read_text(encoding="utf-8"))
        dead["attempts"] = 2
        dead["meta"]["env_retry"] = 1
        dead["meta"]["snapshot_retry"] = 2
        dead_path.write_text(json.dumps(dead, ensure_ascii=False, indent=2), encoding="utf-8")
        cq._write_stale_shadow(root, item["qid"], "q-landed-0008", "base_head")
        return item["qid"]

    def test_requeue_merges_shadow_into_new_bag(self, tmp_path):
        root = tmp_path / "q"
        cq._ensure_dirs(root)
        qid = self._make_dead_with_counts(root)
        wt = tmp_path / "wt"
        wt.mkdir()
        (wt / "a.txt").write_bytes(b"v2-current")

        result = cq.requeue_dead_item(qid, queue_root=root, worktree_root=wt)

        new_item = cq._read_item(root / "pending" / f"{result['new_qid']}.json")
        assert new_item["meta"]["stale"] is True, "影子 stale 语义 MUST 并入新袋（不丢）"
        assert new_item["meta"]["stale_by"] == "q-landed-0008"
        assert not cq._stale_shadow_path(root, qid).exists(), "旧 qid 影子随 requeue 终态清理"

    def test_requeue_lineage_records_prev_counts_without_inheriting(self, tmp_path):
        """矿②：lineage 留痕上一袋计数；袋寿命计数本体不继承（继承即事故）。"""
        root = tmp_path / "q"
        cq._ensure_dirs(root)
        qid = self._make_dead_with_counts(root)
        wt = tmp_path / "wt"
        wt.mkdir()
        (wt / "a.txt").write_bytes(b"v2-current")

        result = cq.requeue_dead_item(qid, queue_root=root, worktree_root=wt)

        new_item = cq._read_item(root / "pending" / f"{result['new_qid']}.json")
        lineage = new_item["meta"]["requeue_lineage"]
        assert lineage["attempts_prev"] == 2
        assert lineage["env_retry_prev"] == 1
        assert lineage["snapshot_retry_prev"] == 2
        assert lineage["requeued_at"]
        # 重置语义不变：attempts 不继承（否则≥5 继承→新袋拾取即死信变砖）
        assert "attempts" not in new_item, "袋寿命计数 MUST 保持重置（不继承）"
        assert new_item["meta"].get("env_retry") in (None, 0)
        assert new_item["meta"].get("snapshot_retry") in (None, 0)


class TestF1InFlightClaimRace:
    """③ F1 竞态窗（redblu_robust.md §五）×矿③ 影子介质：认领 rename 飞行中，二扫双查皆 False。

    真实形态（考古合并裁定：标记介质以影子为准，F1 飞行窗保护逻辑保留）：级联影子
    写入完成后、飞行窗二扫 exists 检查前，认领 rename 恰在飞行中——源侧已 rename 走、
    目的侧（processing）尚未可见（Windows 杀软/索引器可见性滞后放大的窗口）。未修码
    单次双查皆 False ⇒ 影子错标已认领件（拾取侧 _read_item 双读注入 stale 视图）。
    修法：影子写入后延时 50ms 二扫（目的侧落定 ⇒ 影子就地撤除）+ 认领返回前 pending
    残留清源（_pool_claim_item 保险带，介质无关）。
    """

    _VISIBILITY_LAG = 0.03  # 模拟目的侧可见性滞后（须 < 修法延时 0.05s，红蓝双侧确定性）

    def test_sweep_delayed_recheck_withdraws_inflight_claim_shadow(self, tmp_path, monkeypatch):
        """影子写入后认领 rename 飞行中 ⇒ 延时二扫必须撤除影子；漏撤=stale 视图错标真件。"""
        root = tmp_path / "q"
        cq._ensure_dirs(root)
        item = _mk_item("q-f1-0001", depends=["q-landed-f1"])
        p = root / "pending" / "q-f1-0001.json"
        p.write_text(json.dumps(item), encoding="utf-8")
        processing_p = root / "processing" / p.name
        done_p = root / "done" / p.name

        real_write_shadow = cq._write_stale_shadow
        real_exists = Path.exists
        t0 = [0.0]
        lag = self._VISIBILITY_LAG

        def racing_write_shadow(r: Path, qid: str, stale_by: str, trigger: str):
            os.rename(p, processing_p)  # 认领 rename 恰在影子写入前飞行（源侧即走）
            t0[0] = time.monotonic()
            return real_write_shadow(r, qid, stale_by, trigger)

        def lagged_exists(self, *args, **kwargs):
            if self in (processing_p, done_p) and (time.monotonic() - t0[0]) < lag:
                return False  # 目的侧尚未可见（飞行中/滞后窗）——二扫双查皆 False 的病灶形态
            return real_exists(self)

        monkeypatch.setattr(cq, "_write_stale_shadow", racing_write_shadow)
        monkeypatch.setattr(Path, "exists", lagged_exists)

        marked = cq._mark_cascade_stale(root, {"qid": "q-landed-f1", "base_head": "c" * 40})

        assert not p.exists() and processing_p.exists(), "真件应在 processing（影子写不产 pending 幽灵）"
        assert "q-f1-0001" not in marked, "飞行窗内被认领 ⇒ 不得计入命中清单"
        assert not cq._stale_shadow_path(root, "q-f1-0001").exists(), "已认领件的影子必须被延时二扫撤除"

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
