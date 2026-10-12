# [MODULE] tests.meta.scripts.test_build_sft_dataset_determinism
# [DOMAIN] D_DATA
# [DEPENDENCIES] scripts/ml/build_sft_dataset.py（importlib 按路径装载）; pytest
# [CONSUMERS] CI（工单 GPU-03B P0 守卫：训练样本级可复现）
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 本文件只测纯函数（零 CH 零网络零写盘）；红证＝同一套判据打在修复前的 dev 副本上必判败
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] python -m pytest tests/meta/scripts/test_build_sft_dataset_determinism.py -q
# [TTL] permanent
"""GPU-03B P0 守卫测：训练集重跑必须落到**同一批样本**。

实测修的正是这个洞：build_sft_dataset 的三条腿（CH 新闻/FPB/平衡抽样）里，CH 查询没有 ORDER BY、
datasets 分片加载序也不固定，而 balance_sample 用 random.Random(seed).sample(pool, k) —— 池序一变，
同 seed 也换样本。修前实测重跑只重合 1178/3600（jaccard 0.1956），即"重灌＝换考卷"。
"""

from __future__ import annotations

import importlib.util
import pathlib
import random
import sys

_ROOT = pathlib.Path(__file__).resolve().parents[3]
_spec = importlib.util.spec_from_file_location(
    "build_sft_dataset_det",
    str(_ROOT / "scripts" / "ml" / "build_sft_dataset.py"),
)
bsd = importlib.util.module_from_spec(_spec)
sys.modules["build_sft_dataset_det"] = bsd
_spec.loader.exec_module(bsd)


def _pool(n: int, label: str, start: int = 0):
    return [
        {
            "news_id": f"N{start + i:05d}",
            "title": f"t{start + i}",
            "content": f"c{start + i}",
            "sentiment": label,
            "score": 0.5,
            "source": "ch_news_kw",
        }
        for i in range(n)
    ]


class TestStableKey:
    def test_prefers_news_id(self):
        assert bsd.stable_key({"news_id": "N1", "content": "x"}) == "n|N1"

    def test_falls_back_to_source_and_text_for_english_leg(self):
        k1 = bsd.stable_key({"source": "fpb_allagree", "title": "a", "content": "b"})
        k2 = bsd.stable_key({"source": "fpb_allagree", "title": "a", "content": "c"})
        assert k1 != k2
        assert k1.startswith("c|fpb_allagree|")


class TestBalanceSampleIsInputOrderInvariant:
    """判据本体：同一批样本、任意来货顺序，seeded 抽样必须给同一结果。"""

    def test_large_pool_same_selection_under_shuffled_input(self):
        base = _pool(50, "positive")
        shuffled = list(base)
        random.Random(7).shuffle(shuffled)
        out1 = [x["news_id"] for x in bsd.balance_sample(base, target_per_class=10, seed=42)]
        out2 = [x["news_id"] for x in bsd.balance_sample(shuffled, target_per_class=10, seed=42)]
        assert out1 == out2, "同 seed 不同来货序给出不同样本＝重灌换考卷，P0 要治的就是这个"
        assert len(out1) == 10

    def test_small_pool_kept_all_and_deterministic(self):
        base = _pool(6, "negative")
        shuffled = list(base)
        random.Random(3).shuffle(shuffled)
        out1 = [x["news_id"] for x in bsd.balance_sample(base, target_per_class=20, seed=42)]
        out2 = [x["news_id"] for x in bsd.balance_sample(shuffled, target_per_class=20, seed=42)]
        # 不足目标数 ⇒ 全留；出口还有一次 seeded shuffle，所以判"两次逐位一致＋集合完整"而非"升序"
        assert out1 == out2, "来货序影响出口序＝不可复现"
        assert set(out1) == {f"N{i:05d}" for i in range(6)}
        assert len(out1) == 6


class TestCollectedNewsSortedBeforeReturn:
    def test_collect_output_is_key_sorted(self, monkeypatch):
        """采集腿出口处必须已排序（否则 balance 之前的任何消费方仍拿到随机序）。"""
        import pandas as pd

        class _Collector:
            pass

        offsets = {start: (i + 1) * 10000 for i, (start, _e, _lim) in enumerate(bsd.PERIODS)}

        def fake_collect(start, end, limit=0):
            # 段落偏移按 PERIODS 序号定（禁用 str hash——PYTHONHASHSEED 逐进程变会让测试自身不可复现）
            rows = _pool(int(limit), "neutral", start=offsets[start])
            rows = list(reversed(rows))  # 故意给逆序，模拟"来货序不可信"
            return pd.DataFrame(rows)

        import zephyr.data.news_collector as nc

        monkeypatch.setattr(nc, "collect_news", fake_collect)
        out = bsd.collect_chinese_news(set())
        keys = [bsd.stable_key(x) for x in out]
        assert keys == sorted(keys), "collect_chinese_news 出口未按稳定键排序"


class TestNothingWritesProductionPaths:
    def test_pure_functions_never_touch_output_dir(self, tmp_path, monkeypatch):
        """本测试面禁写 data/sft：只调纯函数，且出口目录被改到 tmp 后仍不应出现任何文件。"""
        monkeypatch.setattr(bsd, "OUTPUT_DIR", tmp_path / "sft")
        bsd.balance_sample(_pool(4, "positive"), target_per_class=99, seed=42)
        assert not (tmp_path / "sft").exists()
        assert list(tmp_path.iterdir()) == []
