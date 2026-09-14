# [BLUEPRINT] MOD-BT-187 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.strategy_pipeline.test_bh_fdr
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.strategy_pipeline.bh_fdr
# [CONSUMERS] MOD-BT-187 循环验收
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 测试隔离零 IO；红蓝门=真 H0 族必被拒/挑尾必被拒
# [MODIFY-GUARD] src/zephyr/strategy_pipeline/bh_fdr.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红
# [TESTS] 本文件
# [A_module] module_id=MOD-BT-187 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""BH-FDR 门测试——验收④红蓝条款（方案 §4.3：伪造 p 值族必被拒）。"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zephyr.strategy_pipeline.bh_fdr import bh_filter  # noqa: E402


class TestBHFilter:
    def test_clean_signal_passes(self):
        # 1 个真信号 + 19 个 H0（p 均匀），小 p 应通过
        family = {"real": 0.001}
        family.update({f"null_{i}": 0.4 + i * 0.02 for i in range(19)})
        keep, _ = bh_filter(family, q=0.10)
        assert "real" in keep

    def test_pure_null_family_all_rejected(self):
        # 红：全员 H0（p 均匀撒在 (0,1]）——全自动管线下最危险的一批
        family = {f"null_{i}": round((i + 1) / 20, 3) for i in range(20)}
        keep, report = bh_filter(family, q=0.10)
        # p=0.05 恰好=1/20*1.0 边界，q=0.10 时 threshold=0.005*k：k=1→0.005>0.05 全不过
        assert keep == set()

    def test_p_hacking_tail_pick_rejected(self):
        # 红：挑尾——把一个大 p 塞在小 p 后面想搭车
        family = {"real_1": 0.001, "real_2": 0.002, "hacker": 0.9}
        keep, report = bh_filter(family, q=0.10)
        assert "hacker" not in keep  # 超过最后通过步进=拒
        assert report["hacker"]["passed"] is False

    def test_stepwise_monotonicity(self):
        # 通过集必须是 rank1 起的连续段（BH 步进语义）
        family = {"a": 0.005, "b": 0.02, "c": 0.03}
        keep, report = bh_filter(family, q=0.10)
        ranks = sorted(report[s]["bh_rank"] for s in keep)
        assert ranks == list(range(1, len(keep) + 1))  # 无空洞
        # 红：挑尾——rank 连续段之外的小 p 之前有条目未通过时，后续全拒
        family2 = {"a": 0.001, "b": 0.5, "c": 0.11}
        keep2, _ = bh_filter(family2, q=0.10)
        assert keep2 == {"a"}  # b(0.5) > 0.067 断链，c(0.11) > 0.1 也不过，防搭车

    def test_empty_family_rejected(self):
        with pytest.raises(ValueError, match="空假设族"):
            bh_filter({}, q=0.10)

    def test_q_out_of_range_rejected(self):
        with pytest.raises(ValueError, match="q 越界"):
            bh_filter({"a": 0.01}, q=0.0)

    def test_q_one_is_benign(self):
        # q=1 时全部 p<=k/m*1 恒真（p≤1）——数学上无过滤力，参数合法即可
        keep, _ = bh_filter({"a": 0.5, "b": 0.7}, q=1.0)
        assert keep == {"a", "b"}
