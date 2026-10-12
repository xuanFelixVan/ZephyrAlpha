# [MODULE] tests.scripts.test_ml_run_sft_train
# [DOMAIN] D_ML_TRAIN
# [TTL] permanent
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] python -m pytest tests/meta/scripts/test_ml_run_sft_train.py -q
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

import pytest

_ROOT = pathlib.Path(__file__).resolve().parents[3]
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


def _jl(path, rows):
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")
    return path


def _gold(nid, label, content="c"):
    return {"news_id": nid, "title": "t", "content": content, "sentiment": label}


def _exp(nid, label, content="c"):
    return {
        "news_id": nid,
        "title": "t",
        "content": content,
        "human_label": label,
        "label_source": "teacher_ratified_by_ruling1",
    }


LABELS = ["positive", "negative", "neutral"]


class TestGoldMergeAndIsolation:
    """裁定①④⑤的执行面守卫：训练只认冻结金标，考卷不许混进作业本，且必须"能红"。"""

    def test_two_sources_renorm_and_union(self, tmp_path):
        a = _jl(tmp_path / "a.jsonl", [_gold("1", "positive"), _gold("2", "neutral")])
        b = _jl(tmp_path / "b.jsonl", [_exp("3", "negative")])
        rows, rep = rst.merge_gold_rows([a, b], labels=LABELS)
        assert [r["news_id"] for r in rows] == ["1", "2", "3"]
        assert rows[2]["sentiment"] == "negative"  # human_label 改名不改值
        assert rep["gold_rows_read"] == 3 and rep["gold_rows"] == 3

    def test_cross_source_exact_duplicate_collapses_but_intra_file_duplicate_does_not(self, tmp_path):
        """跨册同题折叠；**册内**重复原样保留——否则单册默认口径的分母被悄悄改掉＝现产线变更。"""
        dup_in = _jl(tmp_path / "in.jsonl", [_gold("1", "neutral", "same"), _gold("1", "neutral", "same")])
        rows, rep = rst.merge_gold_rows([dup_in], labels=LABELS)
        assert len(rows) == 2, "单册内重复必须保留（现产线 n 不变）"
        assert rep["intra_file_duplicate_ids"] == ["1"], rep  # 但必须显影
        assert rep["collapsed_cross_source"] == 0

        dup_across = _jl(tmp_path / "across.jsonl", [_gold("1", "neutral", "same")])
        rows2, rep2 = rst.merge_gold_rows([dup_in, dup_across], labels=LABELS)
        assert rep2["collapsed_cross_source"] == 1
        assert len(rows2) == 2

    def test_same_id_different_label_fails_loud(self, tmp_path):
        a = _jl(tmp_path / "a.jsonl", [_gold("1", "positive", "c1"), _gold("1", "negative", "c2")])
        with pytest.raises(SystemExit) as exc:
            rst.merge_gold_rows([a], labels=LABELS)
        assert exc.value.code == 2

    def test_intra_file_conflicting_label_for_same_id_fails_loud(self, tmp_path):
        a = _jl(tmp_path / "a.jsonl", [_gold("1", "positive"), _gold("1", "negative")])
        with pytest.raises(SystemExit) as exc:
            rst.merge_gold_rows([a], labels=LABELS)
        assert exc.value.code == 2

    def test_cross_source_conflicting_label_for_same_id_fails_loud(self, tmp_path):
        """两本金标给同一题不同档＝真源打架，必须拦死而不是"后读的册覆盖先读的"。"""
        a = _jl(tmp_path / "a.jsonl", [_gold("9", "positive", "c")])
        b = _jl(tmp_path / "b.jsonl", [_exp("9", "negative", "c")])
        with pytest.raises(SystemExit) as exc:
            rst.merge_gold_rows([a, b], labels=LABELS)
        assert exc.value.code == 2

    def test_missing_label_and_foreign_vocab_and_blank_id_all_exit_2(self, tmp_path):
        no_label = _jl(
            tmp_path / "n.jsonl", [{"news_id": "1", "title": "t", "content": "c", "draft_sentiment": "positive"}]
        )
        bad_vocab = _jl(tmp_path / "v.jsonl", [_exp("2", "bullish")])
        blank_id = _jl(tmp_path / "b.jsonl", [_gold("", "neutral")])
        empty = _jl(tmp_path / "e.jsonl", [_gold("3", "neutral")])
        empty.write_text("", encoding="utf-8")
        for p in (no_label, bad_vocab, blank_id, empty):
            with pytest.raises(SystemExit) as exc:
                rst.merge_gold_rows([p], labels=LABELS)
            assert exc.value.code == 2, p

    def test_leakage_guard_blocks_train_ids_present_in_gold(self, tmp_path):
        train = _jl(tmp_path / "tr.jsonl", [_gold("X1", "positive"), _gold("X2", "neutral")])
        gold = _jl(tmp_path / "g.jsonl", [_exp("X2", "negative")])
        tr = rst.load_jsonl(train)
        gd, _ = rst.merge_gold_rows([gold], labels=LABELS)
        with pytest.raises(SystemExit) as exc:
            rst.assert_no_gold_leakage(tr, gd)
        assert exc.value.code == 2
        # 正对照：不相交的两侧必须放行（否则守卫等于永远红）
        rst.assert_no_gold_leakage([_gold("X1", "positive")], gd)

    def test_new_flags_exist_with_production_defaults(self):
        """默认值＝现产线口径零变更：三路径与及格线都指回原常量，改动只在显式传参时生效。"""
        src = (_ROOT / "scripts" / "ml" / "run_sft_train.py").read_text(encoding="utf-8")
        for flag, default in (
            ("--train-path", "SFT_TRAIN_PATH"),
            ("--eval-path", "SFT_EVAL_PATH"),
            ("--gold-path", "[EVAL_200_PATH]"),
            ("--pass-line", "DEFAULT_PASS_LINE"),
        ):
            assert flag in src, flag
            assert default in src, default
        assert rst.DEFAULT_PASS_LINE == 0.75

    def test_main_wires_args_paths_not_constants(self):
        """main() 必须真的读 args（在册假绿形态＝加了旗但 main 仍用常量）。"""
        src = (_ROOT / "scripts" / "ml" / "run_sft_train.py").read_text(encoding="utf-8")
        body = src.split("def main()")[1]
        assert "load_jsonl(args.train_path)" in body
        assert "load_jsonl(args.eval_path)" in body
        assert "merge_gold_rows(list(args.gold_path)" in body
        assert "assert_no_gold_leakage(train_items, gold_items)" in body
        assert "args.pass_line" in body
