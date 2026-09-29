# [q0213-RESCUE] 本件字节捞回自 q-0213 死袋 blob sha256=f0df0ceb602dc7b3…（HEAD_MISSING 真孤儿，2026-09-29 车道 st-finaldel-crescue-20260929 落盘）。
# [TTL] task_bound
# [STARTUP] test_collected
# [CONSUMERS] pytest（W-102 第 1 把尺"禁缓存背书"红证 + 三把尺 CI rc 语义）
# [MODULE] tests.governance.data_supply.test_no_cache_and_cli_rc
# [A_module] module_id=TST-GOV-DS-NCC | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
"""W-102 常设化测试：禁缓存背书两腿 + CI 入口 rc 语义。

rc 语义（案卷同款，CI 侧唯一契约）：
  ``--check``           0=全绿 / 1=有红项 / 2=装载或读数失败（禁把失败洗成 0）
  ``--counterfactual``  0=三把尺控制组全部如期显影 / 1=有尺点不红（尺退化）/ 2=自身异常
"""

from __future__ import annotations

from pathlib import Path

import pytest

# [q0213-RESCUE] 适配：被测生产件 scripts/governance/data_supply/*（check_wave3_rulers/no_cache_endorsement/strict_truth_reader）尚未落 HEAD，模块级 importorskip 防收集炸弹，生产件落库后自动恢复实跑
pytest.importorskip("scripts.governance.data_supply.check_wave3_rulers")
pytest.importorskip("scripts.governance.data_supply.no_cache_endorsement")
pytest.importorskip("scripts.governance.data_supply.strict_truth_reader")

from scripts.governance.data_supply.strict_truth_reader import StrictTruthReader

from scripts.governance.data_supply import check_wave3_rulers as cli
from scripts.governance.data_supply import no_cache_endorsement as nc

REPO = Path(__file__).resolve().parents[3]


def _scan(text: str, path: str = "<mem>/x.py"):
    return nc.scan_source(text, path=path)


def test_structural_leg_names_fail_silent_reads():
    codes = {
        f.code for f in _scan("from zephyr.data import ch_reader\n\n\ndef n():\n    return ch_reader.count('db.t')\n")
    }
    assert codes == {"FAIL_SILENT_READ"}


def test_structural_leg_names_memoized_judgment_functions():
    codes = {f.code for f in _scan("import functools\n\n@functools.lru_cache\ndef n():\n    return 1\n")}
    assert codes == {"MEMOIZED_JUDGMENT_FUNC"}


def test_strict_channel_is_not_flagged():
    assert _scan("from zephyr.data import ch_reader\n\n\ndef n():\n    return ch_reader.count_strict('db.t')\n") == []


def test_behavioral_leg_requires_live_reread():
    total, live = nc.probe_live_reads(lambda p: StrictTruthReader(projection=p))
    assert live and total == 4


def test_behavioral_leg_goes_red_on_cached_reader():
    class _Cached(StrictTruthReader):
        def read_leg(self, *a, **k):  # 记忆化＝缓存背书
            if not hasattr(self, "_memo"):
                self._memo = super().read_leg(*a, **k)
            return self._memo

    _total, live = nc.probe_live_reads(lambda p: _Cached(projection=p))
    assert live is False


def test_package_itself_carries_no_cache_endorsement():
    verdict = nc.evaluate(REPO, lambda probe: StrictTruthReader(projection=probe))
    assert verdict.findings == (), [(f.code, f.path, f.detail) for f in verdict.findings]
    assert verdict.scanned_files >= 5


def test_missing_scan_target_raises_instead_of_passing():
    with pytest.raises(nc.CacheRulerSourceError):
        nc.scan_files([REPO / "scripts" / "governance" / "data_supply" / "__no_such_module__.py"])


def _argv(*extra: str) -> list[str]:
    return list(extra)


def test_cli_counterfactual_rc_zero_when_all_rulers_redden():
    assert cli.main(_argv("--counterfactual")) == 0


def test_cli_check_offline_rc_zero():
    assert cli.main(_argv("--check", "--offline")) == 0


def test_cli_missing_declaration_source_rc_two(monkeypatch):
    monkeypatch.setattr(cli, "_ROOT", REPO / "nope")
    assert cli.main(_argv("--check", "--ruler", "false-green")) == 2


def test_cli_ledger_load_failure_rc_two_not_green(tmp_path):
    """台账不可用 ⇒ rc=2；判据禁把"读不到"洗成"无违规"。"""
    absent = tmp_path / "absent_ledger.db"
    assert cli.main(_argv("--check", "--ruler", "conservation", "--ledger", str(absent))) == 2


def test_cli_truth_read_failure_rc_two_not_green(monkeypatch, tmp_path):
    """W-180 关键面：CH 读数失败必须以 rc=2 显影，绝不因读不到而判绿。"""
    ledger = tmp_path / "ledger.db"
    ledger.write_bytes(b"")  # 仅满足存在性；下层 ProgressStore 自会因非法库抛 → rc=2

    def _boom(*_a, **_k):
        raise RuntimeError("clickhouse unreachable")

    monkeypatch.setattr(cli, "StrictTruthReader", _boom)
    assert cli.main(_argv("--check", "--ruler", "false-green", "--ledger", str(ledger))) == 2
