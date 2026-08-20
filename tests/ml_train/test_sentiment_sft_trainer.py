# [BLUEPRINT] MOD-L11-001 | docs/03_modules/_domain_machine_learning_train/blueprint.md | §Phase4
# [MODULE] tests.ml_train.test_sentiment_sft_trainer
# [DOMAIN] D_ML_TRAIN
# [DEPENDENCIES] zephyr.ml_train.implementations.sentiment_sft_trainer
# [CONSUMERS] (测试，无消费者)
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] 不依赖 torch/peft/trl（重依赖 lazy-import）；仅测 config/messages/error 纯逻辑
# [MODIFY-GUARD] 13_regime_phase3_engineering_plan.md §3.1.9
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败 exit 1
# [TESTS] (本文件即测试)
# [TTL] permanent
"""test_sentiment_sft_trainer — SentimentSFTTrainer 纯逻辑桩测试。

不加载 torch/peft/trl（trainer 重依赖 lazy-import 到方法内），仅覆盖：
  - SFTTrainConfig 默认值（QLoRA 超参 §3.1.9）
  - build_sft_messages 消息格式（system/user/assistant，assistant 为 JSON）
  - SFTTrainError error_code
  - build_sft_messages score 截断/标签规范化

训练/推理路径（train/validate/_batch_predict）依赖 torch+GPU，属 [ml-train] extras
集成测试范畴，不在此桩覆盖。
"""

from __future__ import annotations

import json

import pytest

from zephyr.ml_train.implementations.sentiment_sft_trainer import (
    DEFAULT_LORA_ALPHA,
    DEFAULT_LORA_DROPOUT,
    DEFAULT_LORA_R,
    DEFAULT_LORA_TARGETS,
    LABELS,
    SFTTrainConfig,
    SFTTrainError,
    build_sft_messages,
)


class TestSFTTrainConfig:
    """SFTTrainConfig 默认值（§3.1.9 QLoRA 超参）。"""

    def test_lora_defaults(self) -> None:
        cfg = SFTTrainConfig()
        assert cfg.lora_r == DEFAULT_LORA_R == 8
        assert cfg.lora_alpha == DEFAULT_LORA_ALPHA == 16
        assert cfg.lora_dropout == DEFAULT_LORA_DROPOUT == 0.05

    def test_lora_targets(self) -> None:
        cfg = SFTTrainConfig()
        assert list(cfg.lora_targets) == DEFAULT_LORA_TARGETS
        assert "q_proj" in cfg.lora_targets

    def test_training_defaults(self) -> None:
        cfg = SFTTrainConfig()
        assert cfg.epochs == 3
        assert cfg.batch_size * cfg.grad_accum == 16  # effective batch

    def test_frozen(self) -> None:
        cfg = SFTTrainConfig()
        with pytest.raises(Exception):  # frozen dataclass 不可变
            cfg.lora_r = 16  # type: ignore[misc]


class TestBuildSFTMessages:
    """build_sft_messages 消息格式（对齐 Qwen chat_template）。"""

    def test_three_roles(self) -> None:
        msgs = build_sft_messages("标题", "内容", "positive", 0.9)
        assert len(msgs) == 3
        assert [m["role"] for m in msgs] == ["system", "user", "assistant"]

    def test_assistant_is_json(self) -> None:
        msgs = build_sft_messages("标题", "内容", "negative", 0.8)
        payload = json.loads(msgs[2]["content"])
        assert payload["sentiment"] == "negative"
        assert 0.0 <= payload["score"] <= 1.0

    def test_score_rounding(self) -> None:
        msgs = build_sft_messages("t", "c", "neutral", 0.55555)
        payload = json.loads(msgs[2]["content"])
        # round(float, 3)
        assert payload["score"] == round(0.55555, 3)

    def test_user_template_substitution(self) -> None:
        msgs = build_sft_messages("某标题X", "某内容Y", "positive", 0.7)
        assert "某标题X" in msgs[1]["content"]
        assert "某内容Y" in msgs[1]["content"]


class TestSFTTrainError:
    def test_error_code(self) -> None:
        assert SFTTrainError.error_code == "ZA-MLT-0001"

    def test_raises(self) -> None:
        with pytest.raises(SFTTrainError):
            raise SFTTrainError("测试")


class TestLabels:
    def test_labels(self) -> None:
        assert LABELS == ["positive", "negative", "neutral"]
