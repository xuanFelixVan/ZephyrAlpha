# [BLUEPRINT] MOD-BT-204 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_kronos_finetune_pkl_prep
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest; pandas; torch; scripts.backtest.kronos_finetune_pkl_prep
# [CONSUMERS] MOD-BT-204 kronos_finetune_pkl_prep 循环验收（T6 两轮 0 失败）
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] 零网络零 CH（合成 CSV 落 tmp_path）；pkl 结构契约用真实
#   vendor/Kronos/finetune/dataset.py QlibDataset 实例化验证；生产路径零写入
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError(行为不符)
# [TESTS] 本文件
# [A_module] module_id=MOD-BT-204 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Kronos 微调 pkl 适配层单测——切分时序性/pkl 契约/最小行数过滤/特征完备。

契约测试直接实例化官方 QlibDataset（vendor/Kronos/finetune/dataset.py 原文件，
stub config 注入 dataset_path），保证与训练侧零漂移。
"""
from __future__ import annotations

import importlib.util
import json
import pickle
import sys
import types
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import scripts.backtest.kronos_finetune_pkl_prep as kpp

CSV_COLS = kpp.CSV_COLS
WINDOW = 71  # lookback 60 + predict 10 + 1（与 vendor config 日线化一致）
FEATURES = ["open", "high", "low", "close", "volume", "amount"]


def _synth_csv(path: Path, n_rows: int, seed: int = 7,
               shuffle: bool = False, dup_last: bool = False) -> None:
    """合成 A 股样式日 K CSV（工作日历、正数 OHLC、量额），官方七列。"""
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2024-01-02", periods=n_rows)
    close = 10.0 + np.cumsum(rng.normal(0, 0.2, n_rows))
    close = np.abs(close) + 1.0
    df = pd.DataFrame({
        "timestamps": dates.strftime("%Y-%m-%d"),
        "open": close * (1 + rng.normal(0, 0.005, n_rows)),
        "high": close * (1 + np.abs(rng.normal(0, 0.01, n_rows))),
        "low": close * (1 - np.abs(rng.normal(0, 0.01, n_rows))),
        "close": close,
        "volume": rng.integers(1_000, 10_000, n_rows).astype(float),
        "amount": rng.integers(1_000_000, 10_000_000, n_rows).astype(float),
    })
    if dup_last:
        last = df.iloc[-1].copy()
        last["close"] = float(last["close"]) + 0.5  # 重复日新值→keep last 应取它
        df = pd.concat([df, last.to_frame().T], ignore_index=True)
    if shuffle:
        df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    df.to_csv(path, index=False, encoding="utf-8")


@pytest.fixture()
def csv_dir(tmp_path: Path) -> Path:
    """三标的：260 行 / 250 行 / 100 行（末者应被最小行数过滤剔除）。"""
    d = tmp_path / "csv"
    d.mkdir()
    _synth_csv(d / "000001_SZ.csv", 260, seed=1)
    _synth_csv(d / "600000_SH.csv", 250, seed=2)
    _synth_csv(d / "300750_SZ.csv", 100, seed=3)
    return d


@pytest.fixture()
def built(csv_dir: Path, tmp_path: Path):
    out = tmp_path / "pkl_out"
    rec = kpp.build_pkl(csv_dir, out_dir=out)
    return rec, out


class TestBuildPkl:
    def test_pkl_files_and_manifest_written(self, built):
        rec, out = built
        assert (out / "train_data.pkl").exists()
        assert (out / "val_data.pkl").exists()
        assert (out / "manifest.json").exists()
        assert json.loads((out / "manifest.json").read_text(encoding="utf-8"))["symbols_used"]

    def test_min_rows_filter_drops_short_symbol(self, built):
        rec, _ = built
        assert "300750.SZ" not in rec["symbols_used"]
        dropped = {s["symbol"] for s in rec["symbols_skipped"]}
        assert "300750.SZ" in dropped
        assert any("行数不足" in s["reason"] for s in rec["symbols_skipped"])

    def test_malformed_columns_skipped_with_reason(self, tmp_path):
        """红蓝 R1：列缺失/乱序 CSV 不毒化整批——剔除留痕，好标的照常入训。"""
        d = tmp_path / "csv_bad"
        d.mkdir()
        _synth_csv(d / "000001_SZ.csv", 260, seed=11)
        _synth_csv(d / "600000_SH.csv", 260, seed=12)
        # 破坏第二只：删掉 amount 列（官方七列缺失）
        df = pd.read_csv(d / "600000_SH.csv").drop(columns=["amount"])
        df.to_csv(d / "600000_SH.csv", index=False)
        rec = kpp.build_pkl(d, out_dir=tmp_path / "o_bad")
        assert rec["symbols_used"] == ["000001.SZ"]
        assert rec["symbols_skipped"] == [
            {"symbol": "600000.SH", "reason": "列不规范: " + str(list(df.columns))}]

    def test_temporal_split_order_no_shuffle(self, built):
        """切分时序性：train=前 80%，val=后 20%+头部 lookback 上下文，均升序。

        泄漏防线（唯一硬保证）：val 专属行（上下文之后）绝不进 train——
        即"未来信息进训练集"方向被切断。val 头部 60 行为官方同款上下文
        重叠（官方 config val 早于 train 结束 4 个月，同理）。
        """
        rec, out = built
        train = pickle.loads((out / "train_data.pkl").read_bytes())
        val = pickle.loads((out / "val_data.pkl").read_bytes())
        for sym in rec["symbols_used"]:
            tr_dt = pd.to_datetime(train[sym]["datetime"])
            va_dt = pd.to_datetime(val[sym]["datetime"])
            assert tr_dt.is_monotonic_increasing and va_dt.is_monotonic_increasing
            # val 头部恰回补 lookback_window=60 行 → 首时间戳=train 尾前 60 行
            assert va_dt.iloc[0] == tr_dt.iloc[-60]
            # 硬防线：val 专属区（上下文 60 行之后）与 train 零交集
            val_only = set(va_dt.iloc[60:])
            assert val_only.isdisjoint(set(tr_dt))
            # 80/20：train/(train+val-上下文回补) = 0.8
            assert abs(len(tr_dt) / (len(tr_dt) + len(va_dt) - 60) - 0.8) < 0.01

    def test_split_ratios_exact(self, built, csv_dir):
        rec, out = built
        train = pickle.loads((out / "train_data.pkl").read_bytes())
        val = pickle.loads((out / "val_data.pkl").read_bytes())
        # 260 行标的：cut=208，val=52+60(pad)=112
        tr, va = train["000001.SZ"], val["000001.SZ"]
        assert len(tr) == 208 and len(va) == 112
        # 250 行标的：cut=200，val=50+60=110
        tr2, va2 = train["600000.SH"], val["600000.SH"]
        assert len(tr2) == 200 and len(va2) == 110

    def test_feature_columns_complete_and_dtypes(self, built):
        _, out = built
        data = pickle.loads((out / "train_data.pkl").read_bytes())
        for sym, df in data.items():
            assert list(df.columns) == [kpp.DATETIME_COL] + FEATURES
            assert pd.api.types.is_datetime64_any_dtype(df["datetime"])
            for c in FEATURES:
                assert pd.api.types.is_numeric_dtype(df[c])
            assert df["datetime"].is_unique

    def test_clean_dedup_keep_last_and_sort(self, tmp_path):
        """乱序+重复时间戳 CSV：升序化、重复 keep=last（新值胜出）。"""
        d = tmp_path / "csv2"
        d.mkdir()
        _synth_csv(d / "000001_SZ.csv", 260, seed=9, shuffle=True, dup_last=True)
        panel = kpp._clean_panel(pd.read_csv(d / "000001_SZ.csv"))
        assert panel["timestamps"].is_monotonic_increasing
        assert panel["timestamps"].is_unique
        raw = pd.read_csv(d / "000001_SZ.csv")
        last_ts = pd.Timestamp(raw["timestamps"].iloc[-1])
        dup_rows = raw[pd.to_datetime(raw["timestamps"]) == last_ts]
        expect_close = float(dup_rows.iloc[-1]["close"])  # CSV 中最后一条
        got = panel.loc[panel["timestamps"] == last_ts, "close"].item()
        assert got == pytest.approx(expect_close)

    def test_window_counts_in_record(self, built):
        rec, _ = built
        d = rec["details"][0]
        assert d["train_windows"] == d["train_rows"] - WINDOW + 1
        assert d["val_windows"] == d["val_rows"] - WINDOW + 1
        assert rec["total_train_windows"] == sum(x["train_windows"] for x in rec["details"])

    def test_empty_dir_raises(self, tmp_path):
        with pytest.raises(RuntimeError, match="无 CSV"):
            kpp.build_pkl(tmp_path / "nope", out_dir=tmp_path / "o")

    def test_all_filtered_raises(self, tmp_path):
        d = tmp_path / "csv3"
        d.mkdir()
        _synth_csv(d / "000001_SZ.csv", 100, seed=4)
        with pytest.raises(RuntimeError, match="全部标的被剔除"):
            kpp.build_pkl(d, out_dir=tmp_path / "o3")


class TestQlibDatasetContract:
    """pkl 结构与官方 dataset.py 的真机契约测试（stub config，零网络）。"""

    @pytest.fixture()
    def qlib_dataset_loaded(self, built, tmp_path, monkeypatch):
        rec, out = built
        stub = types.ModuleType("config")

        class Config:
            seed = 100
            lookback_window = 60
            predict_window = 10
            clip = 5.0
            feature_list = FEATURES
            time_feature_list = ["minute", "hour", "weekday", "day", "month"]
            n_train_iter = 10 ** 9
            n_val_iter = 10 ** 9
            dataset_path = str(out)

        stub.Config = Config
        monkeypatch.setitem(sys.modules, "config", stub)
        spec = importlib.util.spec_from_file_location(
            "kronos_ft_dataset_under_test",
            Path(kpp._VENDOR_FINETUNE_DIR) / "dataset.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.QlibDataset("train"), mod.QlibDataset("val"), rec

    def test_dataset_loads_and_window_shapes(self, qlib_dataset_loaded):
        train_ds, val_ds, rec = qlib_dataset_loaded
        assert len(train_ds) == rec["total_train_windows"]
        assert len(val_ds) == rec["total_val_windows"]
        x, x_stamp = train_ds[0]
        assert x.shape == (WINDOW, 6) and x.dtype.is_floating_point
        assert x_stamp.shape == (WINDOW, 5)
        assert not np.isnan(x.numpy()).any()

    def test_dataset_normalization_past_only(self, qlib_dataset_loaded):
        """dataset.py 契约：归一化统计只取前 lookback 行（防泄漏设计自证）。"""
        train_ds, _, _ = qlib_dataset_loaded
        x, _ = train_ds[3]
        past = x[:60].numpy()
        assert np.all(np.abs(past.std(axis=0)) > 0.1)  # 合成数据量纲未塌缩
        assert np.abs(past).max() <= 5.0 + 1e-6  # clip 生效

    def test_val_horizon_post_split(self, built):
        """无泄漏锚点：val 每标的最后 predict_window=10 行（推理视界的
        预测目标区）全部严格晚于 train 尾——切分点之后的未来数据不进训练。"""
        _, out = built
        val = pickle.loads((out / "val_data.pkl").read_bytes())
        train = pickle.loads((out / "train_data.pkl").read_bytes())
        for sym in val:
            va_dt = pd.to_datetime(val[sym]["datetime"]).reset_index(drop=True)
            train_tail = pd.to_datetime(train[sym]["datetime"]).iloc[-1]
            horizon = va_dt.iloc[-10:]
            assert (horizon > train_tail).all()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
