# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §redblue-20260916
# [MODULE] tests.zephyr.data.test_hardening_redblue_20260916
# [DOMAIN] D_DATA
# [A_module] module_id=test-hardening-redblue-20260916 | layer=test | stability=volatile | safety=L | ai_modonomy=ai_modifiable
# [TTL] permanent
"""红蓝对抗（2026-09-16）：当日故障链完整重演，攻击三件套+溢出旁路的自愈闭环。

蓝军防线（被攻击对象）：
- A1 ch_writer 连接自愈（连续 5xx→失效 host/TCP 重建）
- A2 replay_catchup 追平模式（大积压连续排水）
- A4b 溢出旁路（队列满暂存不丢弃）

红军场景（当日实损重演）：
1. CH 断供→落兜底→CH 复活→catchup 追平清零（09:36-12:49 断供+排水闭环）
2. 死条目头部堆积+真实积压并存→catchup 不被预算饿死（昨晚 pop-bug 后遗症回归）
3. 队列钉死→溢出暂存→下游恢复→全部转储（盘中丢 44 万行的假如重演）
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from src.zephyr.data import ch_writer as cw
from src.zephyr.data import local_replay
from src.zephyr.data.local_replay import has_backlog, replay_catchup


def _make_sub():
    """最小 TickSubscriber 实例（与 test_tick_subscriber._make_sub 同构）。"""
    from src.zephyr.data.tick_subscriber import TickSubscriber

    sub = TickSubscriber()
    sub.running = True
    return sub


def _v19_tick():
    return {
        "time": 1720838403000,
        "lastPrice": 10.5,
        "volume": 100,
        "amount": 1050.0,
        "bidPrice": [10.49, 10.48, 10.47, 10.46, 10.45],
        "askPrice": [10.51, 10.52, 10.53, 10.54, 10.55],
        "bidVol": [5, 4, 3, 2, 1],
        "askVol": [6, 7, 8, 9, 10],
    }


class TestRedBlueSupplyCutAndRecovery:
    """场景 1：断供→兜底→复活→追平（当日 09:36-12:49 事故闭环重演）。"""

    def test_outage_backfill_recovery_cycle(self, tmp_path, monkeypatch):
        monkeypatch.setattr(local_replay, "_FALLBACK_DIR", tmp_path)
        manifest_path = tmp_path / "_manifest.jsonl"
        monkeypatch.setattr(local_replay, "_MANIFEST_PATH", manifest_path)

        # 断供期：5 个批次写入全部失败→落兜底
        with patch("src.zephyr.data.ch_writer.write_tsv", return_value=False):
            for i in range(5):
                f = tmp_path / ("outage_%d.tsv" % i)
                f.write_bytes(b"v\n")
                assert local_replay.save_fallback(
                    "c1_market.tick_data", "(a, b)", b"1\tx\n"
                )
        assert has_backlog()
        assert len(local_replay._read_manifest()) == 5

        # CH 复活：追平模式一轮清空
        with patch("src.zephyr.data.ch_writer.write_tsv", return_value=True):
            r = replay_catchup(time_budget_sec=60)
        assert r["replayed"] == 5
        assert r["failed"] == 0
        assert not has_backlog()
        assert not manifest_path.exists()  # manifest 归零删除


class TestRedBlueDeadEntryBudgetStarvation:
    """场景 2：死条目头部堆积不饿死预算（pop-bug 后遗症回归防线）。"""

    def test_catchup_reaches_live_files_behind_dead_entries(self, tmp_path, monkeypatch):
        monkeypatch.setattr(local_replay, "_FALLBACK_DIR", tmp_path)
        manifest_path = tmp_path / "_manifest.jsonl"
        monkeypatch.setattr(local_replay, "_MANIFEST_PATH", manifest_path)

        entries = []
        # 头部 150 个死条目（文件不存在的幽灵，旧 bug 产物形态）
        for i in range(150):
            entries.append(
                {
                    "table": "c1_market.tick_data",
                    "file": "c1_market__tick_data\\20260915_%06d_dead.tsv" % i,
                    "rows": 1500,
                }
            )
        # 其后 10 个活文件（真实积压）
        for i in range(10):
            (tmp_path / "c1_market__tick_data").mkdir(exist_ok=True)
            (tmp_path / "c1_market__tick_data" / ("live_%d.tsv" % i)).write_bytes(b"v\n")
            entries.append(
                {
                    "table": "c1_market.tick_data",
                    "file": "c1_market__tick_data\\live_%d.tsv" % i,
                    "rows": 1500,
                }
            )
        manifest_path.write_text("\n".join(json.dumps(e) for e in entries) + "\n", encoding="utf-8")

        with patch("src.zephyr.data.ch_writer.write_tsv", return_value=True):
            r = replay_catchup(time_budget_sec=120, max_files_per_batch=500)
        assert r["skipped"] == 150  # 死条目全部消化
        assert r["replayed"] == 10  # 活文件全部到达（未被预算饿死）
        assert not has_backlog()


class TestRedBlueQueueOverflowSpillChain:
    """场景 3：队列钉死→溢出暂存→下游恢复→转储清零（假如重演）。"""

    def test_overflow_spill_full_chain(self):
        sub = _make_sub()
        sub._writer = MagicMock()
        sub._writer.add.return_value = True
        sub._tick_queue = __import__("queue").Queue(maxsize=1)  # 钉死态模拟
        try:
            # 队列钉死期：10 个 tick 全部溢出暂存，零丢弃
            for i in range(10):
                sub._spill_overflow("000001.SZ", _v19_tick(), "miniqmt")
            assert len(sub._overflow) == 10
            assert sub._overflow_dropped == 0

            # 下游恢复：writer 正常→转储清零
            flushed_total = 0
            while len(sub._overflow) > 0:
                flushed = sub._flush_overflow_once()
                assert flushed > 0  # 恢复后不空转
                flushed_total += flushed
            assert flushed_total == 10
            assert sub._overflow_spilled == 10
        finally:
            pass
