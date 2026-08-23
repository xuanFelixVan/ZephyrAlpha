# [MODULE] tests.scripts.test_ml_run_sft_train
# [DOMAIN] D_ML_TRAIN
# [TTL] permanent
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] python -m pytest tests/scripts/test_ml_run_sft_train.py -q
"""test_ml_run_sft_train.py — SFT 训练脚本 metrics 落盘件单元测试。

覆盖（纯函数，不触真训练/torch）：
  1. write_metrics_json —— macro_f1/accuracy/n 字段落盘（验收检查项 1 生产者）
  2. 父目录自动创建 / 附带 train_loss 与 generated_at 留痕
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
import sys

_ROOT = pathlib.Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "run_sft_train",
    _ROOT / "scripts" / "ml" / "run_sft_train.py",
)
rst = importlib.util.module_from_spec(_spec)
sys.modules["run_sft_train"] = rst
_spec.loader.exec_module(rst)


class TestWriteMetricsJson:
    def test_fields_written(self, tmp_path):
        out = tmp_path / "sft_metrics.json"
        rst.write_metrics_json({"macro_f1": 0.7699, "accuracy": 0.825, "n": 200}, out)
        obj = json.loads(out.read_text(encoding="utf-8"))
        assert obj["macro_f1"] == 0.7699
        assert obj["accuracy"] == 0.825
        assert obj["n"] == 200
        assert "generated_at" in obj

    def test_parent_dir_created(self, tmp_path):
        out = tmp_path / "sub" / "dir" / "sft_metrics.json"
        rst.write_metrics_json({"macro_f1": 0.8}, out)
        assert out.exists()

    def test_extra_fields_passthrough(self, tmp_path):
        out = tmp_path / "sft_metrics.json"
        rst.write_metrics_json({"macro_f1": 0.8, "train_loss": 0.06}, out)
        obj = json.loads(out.read_text(encoding="utf-8"))
        assert obj["train_loss"] == 0.06
