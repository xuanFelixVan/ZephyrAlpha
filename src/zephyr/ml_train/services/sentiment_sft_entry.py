# [BLUEPRINT] MOD-ML-001 | docs/03_modules/_domain_machine_learning_train/blueprint.md
# [MODULE] zephyr.ml_train.services.sentiment_sft_entry
# [DOMAIN] D_ML_TRAIN
# [DEPENDENCIES] zephyr.ml_train.implementations.sentiment_sft_trainer
# [CONSUMERS] MOD-ML-001 training_pipeline（编排位预留）；scripts/ml/run_sft_train.py（未来接线）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 禁真训练大模型——dry_run=False 恒抛 ZA-MLT-0003；dry_run 只产训练计划不落任何权重
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CandidateTrainDisabledError(ZA-MLT-0003)——候选骨架真训练调用即抛；空样本→ValueError
# [TESTS] tests/ml_train/test_gap_f35_candidate_skeletons.py
# [A_module] module_id=MOD-ML-SFT-ENTRY | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

"""D_ML_TRAIN — GAP-F-35 舆情情感 SFT 训练入口桩（ML-SFT-001）。

既有壳 ``implementations/sentiment_sft_trainer.py``（QLoRA 4bit SFT 全实现）
补统一训练入口：本模块只做训练计划装配（样本校验/配置打包/dry_run 计划产出），
``dry_run=False`` 真训练路径恒抛 ``CandidateTrainDisabledError``（ZA-MLT-0003）——
大模型真训练属 B-007 人工闸门事项，AI 不可自行触发。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Final

_log = logging.getLogger(__name__)

_MODEL_ID: Final[str] = "ML-SFT-001"

#: 样本必填字段（对齐 build_sft_dataset 消费面）
SAMPLE_REQUIRED_FIELDS: Final[tuple[str, ...]] = ("title", "content", "sentiment", "score")


class CandidateTrainDisabledError(Exception):
    """ZA-MLT-0003: 候选骨架真训练被禁（B-007 人工闸门未批）。"""

    error_code = "ZA-MLT-0003"


@dataclass(frozen=True)
class SFTEntryConfig:
    """SFT 训练入口配置。

    Attributes
    ----------
    dry_run : True=只产训练计划（默认，唯一安全路径）；False=真训练（恒抛 ZA-MLT-0003）。
    max_content_chars : content 截断长度（对齐 build_sft_dataset）。
    min_samples : 最小样本数。
    """

    dry_run: bool = True
    max_content_chars: int = 300
    min_samples: int = 1


def run_sentiment_sft_training_entry(
    samples: list[dict[str, Any]],
    config: SFTEntryConfig | None = None,
) -> dict[str, Any]:
    """舆情 SFT 训练入口桩。

    Parameters
    ----------
    samples : 每条含 title/content/sentiment/score。
    config : 入口配置（默认 dry_run=True）。

    Returns
    -------
    dict
        dry_run 训练计划：model_id/n_samples/status/label_distribution。

    Raises
    ------
    ValueError
        samples 为空或样本字段缺失。
    CandidateTrainDisabledError
        dry_run=False（真训练禁触发，ZA-MLT-0003）。
    """
    cfg = config or SFTEntryConfig()
    if not samples:
        raise ValueError("samples 为空——训练入口至少需要 min_samples 条样本")
    if len(samples) < cfg.min_samples:
        raise ValueError(f"samples 不足: {len(samples)} < {cfg.min_samples}")
    for i, s in enumerate(samples):
        missing = [f for f in SAMPLE_REQUIRED_FIELDS if f not in s]
        if missing:
            raise ValueError(f"样本[{i}] 字段缺失: {missing}")

    if not cfg.dry_run:
        _log.warning("ML-SFT-001 真训练路径被禁（B-007 人工闸门）")
        raise CandidateTrainDisabledError(
            "ML-SFT-001 舆情 SFT 真训练属 B-007 人工闸门事项，AI 不可自行触发；"
            "请走 dry_run 计划 + Owner 批准后由人工执行"
        )

    label_dist: dict[str, int] = {}
    for s in samples:
        label = str(s.get("sentiment", "neutral")).strip().lower()
        label_dist[label] = label_dist.get(label, 0) + 1

    plan: dict[str, Any] = {
        "model_id": _MODEL_ID,
        "status": "dry_run",
        "n_samples": len(samples),
        "label_distribution": label_dist,
        "max_content_chars": cfg.max_content_chars,
        "trainer": "zephyr.ml_train.implementations.sentiment_sft_trainer.SentimentSFTTrainer",
    }
    _log.info("SFT 训练入口 dry_run 计划: %s", plan)
    return plan


__all__ = [
    "SAMPLE_REQUIRED_FIELDS",
    "CandidateTrainDisabledError",
    "SFTEntryConfig",
    "run_sentiment_sft_training_entry",
]
