# [BLUEPRINT] MOD-REGIME-P2-E8 | 13_regime_phase3_engineering_plan.md | §4.2
# [TTL] permanent
"""test_scan_forward_days.py — P2-E8 forward_days 扫描脚本单元测试。

覆盖：
  1. scan_forward_days —— 最优选择（fd=5 可分离时 ECE 最小）/degraded 候选不阻断
     /全 degraded → best=None /自定义候选子集
  2. 加载器 —— detect_records JSONL 解析 / close CSV 校验（缺列报错）
  3. main 守卫 —— 输入文件缺失 exit 1；正常跑通写报告
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import sys

import pandas as pd
import pytest

_ROOT = pathlib.Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "scan_forward_days", _ROOT / "scripts" / "scan_forward_days.py",
)
sfd = importlib.util.module_from_spec(_spec)
sys.modules["scan_forward_days"] = sfd  # dataclass 字符串注解解析需模块在册
_spec.loader.exec_module(sfd)


def _synthetic(n: int = 300, conf: float = 0.9):
    """锯齿 close（100/110 交替）+ 奇偶双 regime 记录——fd=奇数完全可分离。

    fd=5：regime A（偶位）forward>0 / B（奇位）<0 → occurred 全 1 → ECE=|0.9-1|=0.1
    fd=偶数：forward=0 → 态无方向 → degraded（样本<50 或零方向）
    """
    idx = pd.bdate_range("2025-01-01", periods=n)
    close = pd.Series([100.0 if i % 2 == 0 else 110.0 for i in range(n)], index=idx)
    records = [
        {
            "timestamp": idx[i],
            "confidence": conf,
            "dominant_regime": "A" if i % 2 == 0 else "B",
        }
        for i in range(n - 130)  # 尾部留余量给最大 fd=120 的 forward 窗口
    ]
    return records, close


# ============ 1. scan_forward_days ============


class TestScanForwardDays:
    def test_best_is_separable_horizon(self):
        records, close = _synthetic()
        report = sfd.scan_forward_days(records, close)
        assert report.best_forward_days == 5
        assert report.best_ece == pytest.approx(0.1, abs=1e-6)

    def test_even_horizons_degraded_not_block(self):
        records, close = _synthetic()
        report = sfd.scan_forward_days(records, close, candidates=[5, 10])
        by_fd = {r.forward_days: r for r in report.rows}
        assert by_fd[5].degraded is False
        assert by_fd[10].degraded is True  # forward=0 态无方向 → degraded
        assert report.best_forward_days == 5  # degraded 不阻断选优

    def test_all_degraded_best_none(self):
        records, close = _synthetic()
        report = sfd.scan_forward_days(records, close, candidates=[10, 20])
        assert all(r.degraded for r in report.rows)
        assert report.best_forward_days is None
        assert report.best_ece is None

    def test_candidate_order_stable_on_tie(self):
        # 两个奇数候选都可分离且 ECE 相同 → 取候选序列先者
        records, close = _synthetic()
        report = sfd.scan_forward_days(records, close, candidates=[5, 15])
        assert report.rows[0].ece == pytest.approx(report.rows[1].ece)
        assert report.best_forward_days == 5

    def test_report_to_dict(self):
        records, close = _synthetic()
        d = sfd.scan_forward_days(records, close).to_dict()
        assert set(d) == {"rows", "best_forward_days", "best_ece"}
        assert len(d["rows"]) == 6  # 默认 6 候选（13 号 §4.2.2）


# ============ 2. 加载器 ============


class TestLoaders:
    def test_load_detect_records(self, tmp_path):
        p = tmp_path / "rec.jsonl"
        with open(p, "w", encoding="utf-8") as f:
            f.write(json.dumps({"timestamp": "2026-08-01", "confidence": 0.8, "dominant_regime": "r3"}) + "\n")
            f.write("{bad json}\n")
        recs = sfd.load_detect_records(p)
        assert len(recs) == 1
        assert isinstance(recs[0]["timestamp"], pd.Timestamp)
        assert recs[0]["confidence"] == 0.8

    def test_load_close(self, tmp_path):
        p = tmp_path / "close.csv"
        p.write_text("date,close\n2026-08-03,100.5\n2026-08-04,101.0\n", encoding="utf-8")
        s = sfd.load_close(p)
        assert len(s) == 2
        assert s.iloc[0] == 100.5
        assert s.index.is_monotonic_increasing

    def test_load_close_missing_column_raises(self, tmp_path):
        p = tmp_path / "close.csv"
        p.write_text("date,price\n2026-08-03,100.5\n", encoding="utf-8")
        with pytest.raises(ValueError, match="date,close"):
            sfd.load_close(p)


# ============ 3. main ============


class TestMain:
    def _inputs(self, tmp_path: pathlib.Path) -> tuple[pathlib.Path, pathlib.Path]:
        records, close = _synthetic()
        rec_path = tmp_path / "rec.jsonl"
        with open(rec_path, "w", encoding="utf-8") as f:
            for r in records:
                f.write(
                    json.dumps(
                        {
                            "timestamp": r["timestamp"].strftime("%Y-%m-%d"),
                            "confidence": r["confidence"],
                            "dominant_regime": r["dominant_regime"],
                        }
                    )
                    + "\n"
                )
        close_path = tmp_path / "close.csv"
        close.to_frame("close").rename_axis("date").to_csv(close_path)
        return rec_path, close_path

    def test_missing_input_exits_1(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            sfd.sys, "argv",
            ["scan_forward_days.py", "--detect-records", str(tmp_path / "no.jsonl"),
             "--close-csv", str(tmp_path / "no.csv")],
        )
        with pytest.raises(SystemExit) as exc:
            sfd.main()
        assert exc.value.code == 1

    def test_main_runs_and_writes_report(self, tmp_path, monkeypatch):
        rec_path, close_path = self._inputs(tmp_path)
        out_path = tmp_path / "report.json"
        monkeypatch.setattr(
            sfd.sys, "argv",
            ["scan_forward_days.py", "--detect-records", str(rec_path),
             "--close-csv", str(close_path), "--out", str(out_path)],
        )
        sfd.main()
        report = json.loads(out_path.read_text(encoding="utf-8"))
        assert report["best_forward_days"] == 5
        assert len(report["rows"]) == 6
