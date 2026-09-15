# [BLUEPRINT] MOD-BT-193 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_sim_promotion_memo
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts.backtest.sim_promotion_memo
# [CONSUMERS] MOD-BT-193 循环验收
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 测试隔离零生产 IO（注册表/CH/输出目录全 monkeypatch/tmp）
# [MODIFY-GUARD] scripts/backtest/sim_promotion_memo.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即红
# [TESTS] 本文件
# [A_module] module_id=MOD-BT-193 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""sim 转正建议书生成器测试——分档收集/降级不阻断/只读语义（交接清单⑭验收）。"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts/backtest"))

import sim_promotion_memo as memo  # noqa: E402


def _registry(tmp_path, entries):
    p = tmp_path / "strategy_registry.yaml"
    p.write_text(yaml.safe_dump({"strategies": entries}, allow_unicode=True), encoding="utf-8")
    return p


class TestCollect:
    def test_split_by_lifecycle(self, tmp_path, monkeypatch):
        monkeypatch.setattr(memo, "REGISTRY", _registry(tmp_path, [
            {"strategy_id": "STR-A-001", "name": "A", "strategy_class": "x",
             "code_path": "scripts/backtest/translated/c4_a.py", "lifecycle_status": "sim",
             "evidence": "e"},
            {"strategy_id": "STR-B-001", "name": "B", "strategy_class": "y",
             "code_path": "scripts/backtest/translated/c4_b.py", "lifecycle_status": "candidate"},
            {"strategy_id": "STR-C-001", "name": "C", "strategy_class": "z",
             "code_path": "scripts/backtest/translated/c4_c.py", "lifecycle_status": "retired"},
        ]))
        monkeypatch.setattr(memo, "_stats_for", lambda sf: {"is_sharpe": 1.0, "oos": []})
        data = memo.collect()
        assert [x["sid"] for x in data["sim"]] == ["STR-A-001"]
        assert [x["sid"] for x in data["candidate"]] == ["STR-B-001"]

    def test_stats_error_degrades(self, tmp_path, monkeypatch):
        monkeypatch.setattr(memo, "REGISTRY", _registry(tmp_path, [
            {"strategy_id": "STR-A-001", "name": "A", "strategy_class": "x",
             "code_path": "scripts/backtest/translated/c4_a.py", "lifecycle_status": "sim"},
        ]))

        def boom(sf):
            raise RuntimeError("ch down")
        monkeypatch.setattr(memo, "_stats_for", boom)
        data = memo.collect()
        assert "error" in data["sim"][0]["stats"]


class TestGenerate:
    def test_memo_written_and_readonly(self, tmp_path, monkeypatch):
        monkeypatch.setattr(memo, "REGISTRY", _registry(tmp_path, [
            {"strategy_id": "STR-A-001", "name": "A", "strategy_class": "x",
             "code_path": "scripts/backtest/translated/c4_a.py", "lifecycle_status": "sim",
             "evidence": "双窗及格"},
        ]))
        monkeypatch.setattr(memo, "_stats_for",
                            lambda sf: {"is_sharpe": 0.9, "oos": [{"batch": "C4-OOS", "sharpe": 0.5,
                                                                   "decay": 0.1}]})
        out = memo.generate(out_dir=tmp_path / "memos", now=(2026, 9, 15, 0, 0, 0, 0, 0, 0))
        md = Path(out["path"])
        assert md.exists() and out["sim_n"] == 1
        text = md.read_text(encoding="utf-8")
        assert "STR-A-001" in text and "Owner 门" in text  # 签字权声明必须在场
        assert "评估要点" in text
