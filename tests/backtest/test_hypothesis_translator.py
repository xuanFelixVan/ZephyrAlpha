# [BLUEPRINT] MOD-BT-190 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_hypothesis_translator
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] pytest
# [CONSUMERS] MOD-BT-190 hypothesis_translator 循环验收（tests 同批）
# [STARTUP] manual
# [MATURITY] experimental
# [MODIFY-GUARD] none
# [INVARIANTS] 零网络零 LLM：prompt/解析/阴性档案纯函数验证；幂等占坑口径以 tmp_path
#   注入 manifest 验收（禁触生产 translated_manifest.csv）
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError(行为不符)
# [TESTS] 本文件
# [A_module] module_id=MOD-BT-190 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""FAC-E3 假说轨翻译单测——prompt 边界/翻译解析/阴性档案/幂等占坑口径，零网络。"""

from __future__ import annotations

import pandas as pd
import pytest

import scripts.backtest.hypothesis_translator as ht
from scripts.backtest.hypothesis_translator import (
    MANIFEST_COLS,
    build_translation_prompt,
    parse_translation,
)


class TestTranslationPrompt:
    def test_deterministic_and_bounded(self):
        p1 = build_translation_prompt("低PE假说", ["ret_1d"], ["add", "log"])
        p2 = build_translation_prompt("低PE假说", ["ret_1d"], ["add", "log"])
        assert p1 == p2
        assert "低PE假说" in p1 and "add" in p1 and "ret_1d" in p1

    def test_boundary_written_into_prompt(self):
        p = build_translation_prompt("x", ["ret_1d"], ["add"])
        for token in ("translatable=false", "事件窗口", "禁止硬翻", "交易对手三问"):
            assert token in p


class TestParseTranslation:
    def test_translatable_object(self):
        raw = '{"translatable": true, "expression": "neg(ret_1d)", "description": "d", "mechanism": "m", "top_n": 15}'
        tr = parse_translation(raw)
        assert tr["translatable"] is True and tr["expression"] == "neg(ret_1d)"
        assert tr["top_n"] == 15

    def test_refusal_object(self):
        raw = '{"translatable": false, "refusal_reason": "涉及财报公告"}'
        tr = parse_translation(raw)
        assert tr["translatable"] is False
        assert "财报" in tr["refusal_reason"]

    def test_garbage_becomes_refusal(self):
        tr = parse_translation("我觉得这条没法翻译")
        assert tr["translatable"] is False and tr["refusal_reason"] == "parse_fail"

    def test_think_block_noise_tolerated(self):
        # r1 类推理模型 <think> 尾噪声：仍能提取 JSON 对象
        raw = '推理过程 {"x": 1} …… 结论 {"translatable": false, "refusal_reason": "r"}'
        assert parse_translation(raw)["translatable"] is False


class TestIdempotentSlotHoldingF22:
    """F22 治本：refusal_reason 前缀 llm_error 的阴性行是基础设施失败，不得占幂等坑。

    旧 load_translated_ids 取 manifest 全部 candidate_id 集跳过 ⇒ 09-26 Ollama 断供班
    写出的 3 行 llm_error:ConnectionError 把 3 条已过审 B 假说永久锁死（无重试路径）。
    """

    def _manifest(self, tmp_path, rows: list[dict]):
        p = tmp_path / "translated_manifest.csv"
        df = pd.DataFrame(rows)
        for c in MANIFEST_COLS:
            if c not in df.columns:
                df[c] = ""
        df[[c for c in MANIFEST_COLS if c in df.columns]].to_csv(
            p, index=False, encoding="utf-8-sig", lineterminator="\n"
        )
        return p

    def test_llm_error_negative_row_frees_the_slot(self, tmp_path, monkeypatch):
        p = self._manifest(
            tmp_path,
            [
                {"candidate_id": "CAND-b1", "translatable": False, "refusal_reason": "llm_error:ConnectionError"},
            ],
        )
        monkeypatch.setattr(ht, "_MANIFEST_CSV", p)
        assert ht.load_translated_ids() == set(), "llm_error 行占坑=断供班永久锁死候选（F22 原缺陷）"

    def test_genuine_refusal_still_holds_the_slot(self, tmp_path, monkeypatch):
        """真阴性（模型如实判不可翻/dsl 不过/表达式重复）是结论，仍跳过——修完不许反向漏翻。"""
        p = self._manifest(
            tmp_path,
            [
                {"candidate_id": "CAND-b2", "translatable": False, "refusal_reason": "dup_expression"},
                {"candidate_id": "CAND-b3", "translatable": False, "refusal_reason": "dsl_比较/筛选条件不属因子表达式"},
            ],
        )
        monkeypatch.setattr(ht, "_MANIFEST_CSV", p)
        assert ht.load_translated_ids() == {"CAND-b2", "CAND-b3"}

    def test_positive_row_holds_the_slot(self, tmp_path, monkeypatch):
        p = self._manifest(
            tmp_path,
            [
                {
                    "candidate_id": "CAND-b4",
                    "translatable": True,
                    "refusal_reason": "",
                    "expression": "neg(ret_1d)",
                    "exam_file": "scripts/backtest/translated/c4_fact_x.py",
                },
            ],
        )
        monkeypatch.setattr(ht, "_MANIFEST_CSV", p)
        assert ht.load_translated_ids() == {"CAND-b4"}

    def test_error_then_later_conclusive_row_holds_the_slot(self, tmp_path, monkeypatch):
        """同 id 先 llm_error 后成功重翻：追加台账里两行并存，坑必须收回（不三度重翻）。"""
        p = self._manifest(
            tmp_path,
            [
                {"candidate_id": "CAND-b5", "translatable": False, "refusal_reason": "llm_error:ConnectionError"},
                {
                    "candidate_id": "CAND-b5",
                    "translatable": True,
                    "refusal_reason": "",
                    "expression": "rank_cs(ret_20d)",
                },
            ],
        )
        monkeypatch.setattr(ht, "_MANIFEST_CSV", p)
        assert ht.load_translated_ids() == {"CAND-b5"}

    def test_infra_mask_helper_is_column_tolerant(self):
        """缺列退化口径：无 translatable 列只看前缀；无 refusal 列一律不豁免。"""
        without_translatable = pd.DataFrame(
            [
                {"candidate_id": "a", "refusal_reason": "llm_error:Timeout"},
                {"candidate_id": "b", "refusal_reason": "parse_fail"},
            ]
        )
        assert ht.infra_negative_rows(without_translatable).tolist() == [True, False]
        without_refusal = pd.DataFrame([{"candidate_id": "a", "translatable": False}])
        assert ht.infra_negative_rows(without_refusal).tolist() == [False]

    def test_missing_manifest_returns_empty(self, tmp_path, monkeypatch):
        monkeypatch.setattr(ht, "_MANIFEST_CSV", tmp_path / "nope.csv")
        assert ht.load_translated_ids() == set()

    def test_damaged_manifest_returns_empty(self, tmp_path, monkeypatch):
        p = tmp_path / "translated_manifest.csv"
        p.write_text("nonsense_col\n1\n", encoding="utf-8")
        monkeypatch.setattr(ht, "_MANIFEST_CSV", p)
        assert ht.load_translated_ids() == set()

    def test_real_20260926_shape_is_retranslatable(self, tmp_path, monkeypatch):
        """09-26 事故形态复刻（3 条 B 过审假说被 3 行 llm_error 占坑）：全部应退回可重翻。"""
        rows = [
            {
                "candidate_id": f"CAND-{i}",
                "birth_channel": "B",
                "translatable": False,
                "refusal_reason": "llm_error:ConnectionError",
            }
            for i in range(3)
        ]
        rows.append(
            {
                "candidate_id": "CAND-passed",
                "birth_channel": "D",
                "translatable": True,
                "refusal_reason": "",
                "expression": "rank_cs(ret_20d)",
            }
        )
        p = self._manifest(tmp_path, rows)
        monkeypatch.setattr(ht, "_MANIFEST_CSV", p)
        assert ht.load_translated_ids() == {"CAND-passed"}


if __name__ == "__main__":  # pragma: no cover
    pytest.main([__file__, "-v"])
