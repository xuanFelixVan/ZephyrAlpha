# [BLUEPRINT] MOD-L11-001 | docs/03_modules/_domain_machine_learning_train/blueprint.md | §Phase4
# [MODULE] zephyr.ml_train.implementations.sentiment_sft_trainer
# [DOMAIN] D_ML_TRAIN
# [DEPENDENCIES] zephyr.ml_train.trainer_base; peft; trl; transformers; torch; datasets; sklearn.metrics
# [CONSUMERS] scripts/ml/run_sft_train.py; P1-E3 NLP 管道 Phase 4
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] QLoRA 4bit（r=8/alpha=16/dropout=0.05/target=q,k,v,o_proj）；继承 ModelTrainerBase；重依赖 lazy-import；训练数据 messages 格式对齐 nlp_inference prompt 模板；LoRA adapter 持久化 models/qwen25-7b-sft-v1/
# [MODIFY-GUARD] 13_regime_phase3_engineering_plan.md §3.1.9
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SFTTrainError(ZA-MLT-0001)——模型加载/训练失败时抛；推理解析失败降级 neutral
# [TESTS] tests/ml_train/test_sentiment_sft_trainer.py
# [A_module] module_id=MOD-L11-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #ARCH-NLP-PIPELINE-001 Phase 4

"""
MOD-L11-001 SentimentSFTTrainer — Qwen2.5-7B-Instruct LoRA SFT（P1-E3 Phase 4）。

对 Qwen2.5-7B-Instruct 做 QLoRA 4bit 微调，学习 A 股新闻情感分类（positive/negative/neutral），
输出对齐 ``nlp_inference`` 的 JSON 格式 ``{"sentiment": ..., "score": ...}``。

设计原则（P1-E3 架构裁定 §1.4/§3.1.9）：
- 训练轨用 torch/peft/trl QLoRA（无法对 Ollama GGUF 做 peft）
- QLoRA 超参：r=8 / alpha=16 / dropout=0.05 / target=q,k,v,o_proj / nf4 + double_quant + bf16 compute
- 训练数据 messages 格式 → SFTTrainer 自动 apply Qwen chat_template（与推理格式一致）
- ``assistant_only_loss=True`` 只对 assistant JSON 输出算 loss
- 产物 LoRA adapter 持久化 ``models/qwen25-7b-sft-v1/adapter_*``（Phase 6 转 GGUF 回灌 Ollama）
- 继承 ``ModelTrainerBase``（OCP 扩展点 D_ML_TRAIN-TRN），注册 ``ModelRegistry``

重依赖（torch/peft/trl/transformers/datasets）lazy-import 到方法内，
确保无 ``[ml-train]`` extras 环境也能 import 本模块（注册器模式需要）。

依据: 13_regime_phase3_engineering_plan.md §3.1.9
SSoT: #ARCH-NLP-PIPELINE-001
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: title 参数
#   fields: 参数 title，类型注解 str
#   code: sentiment_sft_trainer.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: content 参数
#   fields: 参数 content，类型注解 str
#   code: sentiment_sft_trainer.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: sentiment 参数
#   fields: 参数 sentiment，类型注解 str
#   code: sentiment_sft_trainer.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: score 参数
#   fields: 参数 score，类型注解 float
#   code: sentiment_sft_trainer.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① build_sft_messages
#   name_en: build_sft_messages
#   intro: 构造单条 SFT 训练样本（messages 格式，对齐 Qwen chat_template）。
#   desc: 构造单条 SFT 训练样本（messages 格式，对齐 Qwen chat_template）。 Parameters ---------- title / content :…；源码 L202-L221
#   inputs: title content sentiment score
#   outputs: list[dict[str, str]]
# - id: A2
#   name_zh: ② build_sft_dataset
#   name_en: build_sft_dataset
#   intro: 从样本列表构造 ``datasets.Dataset``（messages 格式）。
#   desc: 从样本列表构造 ``datasets.Dataset``（messages 格式）。 Parameters ---------- samples : 每条含 ``title``…；源码 L224-L250
#   inputs: samples max_content_chars
#   outputs: Any
# - id: A3
#   name_zh: ③ SentimentSFTTrainer
#   name_en: SentimentSFTTrainer
#   intro: Qwen2.5-7B-Instruct LoRA SFT 训练器（P1-E3 Phase 4）。
#   desc: Qwen2.5-7B-Instruct LoRA SFT 训练器（P1-E3 Phase 4）。 继承 ``ModelTrainerBase``（OCP 扩展点 D_ML_TRA…；公共方法（定义序）: train,…
#   inputs: config
#   outputs: 返回值
#   （注：A3 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: list[dict[str, str]]
#   name_en: list[dict[str, str]]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: scripts/ml/run_sft_train.py; P1-E3 NLP 管道 Phase 4
# - id: O2
#   name_zh: Any
#   name_en: Any
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: scripts/ml/run_sft_train.py; P1-E3 NLP 管道 Phase 4
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

import json
import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from zephyr.ml_train.trainer_base import ModelMetadata, ModelRegistry, ModelTrainerBase

if TYPE_CHECKING:
    pass

_log = logging.getLogger(__name__)

# ── 默认配置（§3.1.9 QLoRA 超参）──
DEFAULT_BASE_MODEL = "Qwen/Qwen2.5-7B-Instruct"
DEFAULT_LORA_R = 8
DEFAULT_LORA_ALPHA = 16
DEFAULT_LORA_DROPOUT = 0.05
DEFAULT_LORA_TARGETS = ["q_proj", "k_proj", "v_proj", "o_proj"]

# 训练超参（QLoRA SFT 经验值）
DEFAULT_EPOCHS = 3
DEFAULT_BATCH_SIZE = 4
DEFAULT_GRAD_ACCUM = 4  # effective batch = 4*4 = 16
DEFAULT_LR = 2e-4  # LoRA 学习率（比全量微调高一个量级）
DEFAULT_WARMUP_RATIO = 0.03
DEFAULT_WEIGHT_DECAY = 0.01
DEFAULT_MAX_NEW_TOKENS = 64  # JSON 输出短

# 默认输出目录（LoRA adapter 持久化）
_DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[4] / "models" / "qwen25-7b-sft-v1"
# 评估集默认路径
_DEFAULT_EVAL_PATH = Path(__file__).resolve().parents[4] / "data" / "eval" / "news_sentiment_200.jsonl"

LABELS = ["positive", "negative", "neutral"]


class SFTTrainError(Exception):
    """ZA-MLT-0001: SFT 训练/推理失败。"""

    error_code = "ZA-MLT-0001"


@dataclass(frozen=True)
class SFTTrainConfig:
    """SFT 训练配置——打包 QLoRA + 训练超参，避免长参数列表（§5.150）。

    Attributes
    ----------
    base_model : HF 模型 ID（默认 Qwen2.5-7B-Instruct）。
    output_dir : LoRA adapter 持久化目录。
    lora_r / lora_alpha / lora_dropout : LoRA 超参（§3.1.9）。
    lora_targets : LoRA 目标模块。
    epochs / batch_size / grad_accum / lr : 训练超参。
    max_seq_length : 最大序列长度（截断长新闻内容）。
    eval_steps / save_steps / logging_steps : 评估/保存/日志步频。
    """

    base_model: str = DEFAULT_BASE_MODEL
    output_dir: str = str(_DEFAULT_OUTPUT_DIR)
    lora_r: int = DEFAULT_LORA_R
    lora_alpha: int = DEFAULT_LORA_ALPHA
    lora_dropout: float = DEFAULT_LORA_DROPOUT
    lora_targets: tuple[str, ...] = tuple(DEFAULT_LORA_TARGETS)
    epochs: float = DEFAULT_EPOCHS
    batch_size: int = DEFAULT_BATCH_SIZE
    grad_accum: int = DEFAULT_GRAD_ACCUM
    lr: float = DEFAULT_LR
    warmup_ratio: float = DEFAULT_WARMUP_RATIO
    weight_decay: float = DEFAULT_WEIGHT_DECAY
    max_seq_length: int = 1024
    eval_steps: int = 50
    save_steps: int = 100
    logging_steps: int = 10
    save_total_limit: int = 2
    seed: int = 42
    # 复用 nlp_inference 的 SYSTEM_PROMPT（保证训练/推理 prompt 一致）
    system_prompt: str = ""


# 复用 nlp_inference 的 prompt 模板（单一真源）
def _load_prompt_template() -> tuple[str, str]:
    """从 nlp_inference 加载 SYSTEM_PROMPT / USER_TEMPLATE（训练/推理对齐）。"""
    try:
        from zephyr.nlp.nlp_inference import SYSTEM_PROMPT, USER_TEMPLATE

        return SYSTEM_PROMPT, USER_TEMPLATE
    except Exception:  # noqa: BLE001 — 回退内置精简版
        _log.warning("sentiment_sft_trainer: 无法导入 nlp_inference prompt，用回退版")
        return (
            '你是 A 股金融新闻情感分析专家。输出 JSON: {"sentiment": "positive|negative|neutral", "score": 0.0-1.0}',
            "新闻标题: {title}\n新闻内容: {content}\n请分析情感，输出 JSON。",
        )


def build_sft_messages(title: str, content: str, sentiment: str, score: float) -> list[dict[str, str]]:
    """构造单条 SFT 训练样本（messages 格式，对齐 Qwen chat_template）。

    Parameters
    ----------
    title / content : 新闻文本（content 已截断）。
    sentiment : positive / negative / neutral（标签）。
    score : 情感强度 [0, 1]。

    Returns
    -------
    [{"role":"system",...}, {"role":"user",...}, {"role":"assistant",...}]
    """
    system, user_tpl = _load_prompt_template()
    assistant = json.dumps({"sentiment": sentiment, "score": round(float(score), 3)}, ensure_ascii=False)
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user_tpl.format(title=title, content=content)},
        {"role": "assistant", "content": assistant},
    ]


def build_sft_dataset(samples: list[dict[str, Any]], *, max_content_chars: int = 300) -> Any:
    """从样本列表构造 ``datasets.Dataset``（messages 格式）。

    Parameters
    ----------
    samples : 每条含 ``title`` / ``content`` / ``sentiment`` / ``score``。
    max_content_chars : content 截断长度（控制 token 成本）。

    Returns
    -------
    datasets.Dataset，字段 ``messages``（list[dict]）。
    """
    from datasets import Dataset

    rows = []
    for s in samples:
        title = str(s.get("title", "")).strip()
        content = str(s.get("content", ""))[:max_content_chars]
        sentiment = str(s.get("sentiment", "neutral")).strip().lower()
        if sentiment not in LABELS:
            sentiment = "neutral"
        try:
            score = float(s.get("score", 0.5))
        except (TypeError, ValueError):
            score = 0.5
        rows.append({"messages": build_sft_messages(title, content, sentiment, score)})
    return Dataset.from_list(rows)


@ModelRegistry.register
class SentimentSFTTrainer(ModelTrainerBase):
    """Qwen2.5-7B-Instruct LoRA SFT 训练器（P1-E3 Phase 4）。

    继承 ``ModelTrainerBase``（OCP 扩展点 D_ML_TRAIN-TRN），实现：
      - ``train()``: QLoRA 4bit + SFTTrainer 训练，返回 ``{train_loss, eval_loss}``
      - ``validate()``: 评估集推理 + Macro-F1（与 eval_sentiment.py 同口径）
      - ``save_model()``: LoRA adapter 持久化

    训练数据通过 ``features`` 传入：
      - ``features["train_dataset"]``: datasets.Dataset（messages 格式）
      - ``features["eval_dataset"]``: datasets.Dataset（可选，messages 格式）
      - ``features["eval_items"]``: list[dict]（可选，validate 用，含 title/content/sentiment）
    """

    __model_id__ = "qwen25-7b-sentiment-v1"

    def __init__(self, config: SFTTrainConfig | None = None) -> None:
        self.config = config or SFTTrainConfig()
        self._model: Any = None  # 训练后的 PeftModel
        self._tokenizer: Any = None
        self._trainer: Any = None  # SFTTrainer 实例（train 后保留供 validate）
        self._metadata: ModelMetadata | None = None

    # ── 模型构建 ──────────────────────────────────────────────────────

    def _build_quant_model(self) -> tuple[Any, Any]:
        """加载 4bit 量化基座模型 + tokenizer（QLoRA）。"""
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

        cfg = self.config
        _log.info("加载 4bit 量化基座: %s", cfg.base_model)

        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
        )
        tokenizer = AutoTokenizer.from_pretrained(cfg.base_model)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        model = AutoModelForCausalLM.from_pretrained(
            cfg.base_model,
            quantization_config=bnb_config,
            device_map="auto",
            attn_implementation="sdpa",
            torch_dtype=torch.bfloat16,
        )
        # QLoRA: 准备 kbit 训练（梯度/层归一化/输入嵌入 cast）
        from peft import prepare_model_for_kbit_training

        model = prepare_model_for_kbit_training(model)
        # 启用 gradient_checkpointing 节省显存（需 use_reentrant=False 配合 PEFT）
        if hasattr(model, "gradient_checkpointing_enable"):
            model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
        if hasattr(model, "config") and hasattr(model.config, "use_cache"):
            model.config.use_cache = False
        return model, tokenizer

    def _build_lora_config(self) -> Any:
        from peft import LoraConfig

        cfg = self.config
        return LoraConfig(
            r=cfg.lora_r,
            lora_alpha=cfg.lora_alpha,
            lora_dropout=cfg.lora_dropout,
            target_modules=list(cfg.lora_targets),
            bias="none",
            task_type="CAUSAL_LM",
        )

    def _build_sft_config(self) -> Any:
        from trl import SFTConfig

        cfg = self.config
        Path(cfg.output_dir).mkdir(parents=True, exist_ok=True)
        return SFTConfig(
            output_dir=cfg.output_dir,
            num_train_epochs=cfg.epochs,
            per_device_train_batch_size=cfg.batch_size,
            gradient_accumulation_steps=cfg.grad_accum,
            learning_rate=cfg.lr,
            warmup_ratio=cfg.warmup_ratio,
            weight_decay=cfg.weight_decay,
            lr_scheduler_type="cosine",
            optim="paged_adamw_8bit",  # QLoRA 推荐（分页避免 OOM）
            bf16=True,
            gradient_checkpointing=True,
            gradient_checkpointing_kwargs={"use_reentrant": False},
            logging_steps=cfg.logging_steps,
            eval_strategy="steps",
            eval_steps=cfg.eval_steps,
            save_strategy="steps",
            save_steps=cfg.save_steps,
            save_total_limit=cfg.save_total_limit,
            seed=cfg.seed,
            report_to="none",
            assistant_only_loss=True,  # 只对 assistant JSON 算 loss
            dataset_num_proc=4,
            max_length=cfg.max_seq_length,
        )

    # ── ModelTrainerBase 实现 ────────────────────────────────────────

    def train(
        self,
        features: dict[str, Any],
        target: object,
        idempotency_key: str,
    ) -> dict[str, float]:
        """QLoRA SFT 训练。

        Parameters
        ----------
        features : 含 ``train_dataset`` (datasets.Dataset, messages 格式)；
            可选 ``eval_dataset`` (datasets.Dataset)。
        target : 未用（保留接口对齐基类）。
        idempotency_key : 幂等键（当前记日志，未做断点续训）。

        Returns
        -------
        ``{"train_loss": float, "eval_loss": float}``

        Raises
        ------
        SFTTrainError
            训练失败。
        """
        train_ds = features.get("train_dataset")
        if train_ds is None:
            raise SFTTrainError("features['train_dataset'] 缺失（messages 格式 datasets.Dataset）")
        eval_ds = features.get("eval_dataset")

        _log.info(
            "SFT 训练开始: train=%d eval=%s key=%s", len(train_ds), len(eval_ds) if eval_ds else "None", idempotency_key
        )

        try:
            model, tokenizer = self._build_quant_model()
            lora_config = self._build_lora_config()
            sft_config = self._build_sft_config()

            from trl import SFTTrainer

            trainer = SFTTrainer(
                model=model,
                args=sft_config,
                train_dataset=train_ds,
                eval_dataset=eval_ds,
                processing_class=tokenizer,
                peft_config=lora_config,
            )
            self._trainer = trainer
            self._tokenizer = tokenizer

            result = trainer.train()
            self._model = trainer.model

            metrics: dict[str, float] = {"train_loss": float(result.training_loss)}
            if eval_ds is not None:
                eval_metrics = trainer.evaluate()
                metrics["eval_loss"] = float(eval_metrics.get("eval_loss", 0.0))

            # 持久化 adapter + metadata
            self.save_model(self.config.output_dir)
            self._metadata = ModelMetadata(
                model_id=self.__model_id__,
                model_version="1.0.0",
                model_type="lora-sft",
                framework="peft/trl",
                features=["title", "content"],
                target="sentiment",
                metrics=metrics,
                status="trained",
            )
            _log.info("SFT 训练完成: %s", metrics)
            return metrics
        except SFTTrainError:
            raise
        except Exception as exc:  # noqa: BLE001 — 训练失败统一包装
            raise SFTTrainError(f"SFT 训练失败: {exc}") from exc

    def validate(self, features: dict[str, Any], target: object) -> dict[str, float]:
        """在评估集上推理 + 计算 Macro-F1 / Accuracy。

        Parameters
        ----------
        features : 含 ``eval_items`` (list[dict]，每条 title/content/sentiment)；
            缺失则从默认路径 ``data/eval/news_sentiment_200.jsonl`` 加载。

        Returns
        -------
        ``{"macro_f1": float, "accuracy": float, "n": int}``
        """
        from sklearn.metrics import accuracy_score, f1_score

        eval_items = features.get("eval_items")
        if not eval_items:
            eval_items = self._load_default_eval()
        if not eval_items:
            raise SFTTrainError("validate: 无评估数据")

        y_true: list[str] = []
        y_pred: list[str] = []
        for pred, gold in self._batch_predict(eval_items):
            y_pred.append(pred)
            y_true.append(gold)

        macro_f1 = f1_score(y_true, y_pred, labels=LABELS, average="macro", zero_division=0)
        acc = accuracy_score(y_true, y_pred)
        _log.info("SFT validate: n=%d macro_f1=%.4f acc=%.4f", len(y_true), macro_f1, acc)
        return {"macro_f1": float(macro_f1), "accuracy": float(acc), "n": float(len(y_true))}

    def save_model(self, path: str) -> None:
        """持久化 LoRA adapter + tokenizer 到 ``path``。"""
        if self._model is None or self._trainer is None:
            raise SFTTrainError("save_model: 模型未训练（self._model is None）")
        out = Path(path)
        out.mkdir(parents=True, exist_ok=True)
        # peft save_pretrained 保存 adapter_config.json + adapter_model.safetensors
        self._model.save_pretrained(out)
        if self._tokenizer is not None:
            self._tokenizer.save_pretrained(out)
        _log.info("LoRA adapter 已保存: %s", out)

    # ── 推理辅助 ──────────────────────────────────────────────────────

    def _batch_predict(self, eval_items: list[dict], *, batch_size: int = 1) -> list[tuple[str, str]]:
        """逐条 generate 推理，返回 [(pred_sentiment, gold_sentiment), ...]。

        默认 ``batch_size=1``：单条推理无需 padding，``out[:, prompt_lens:]`` 切片精确，
        彻底规避 decoder-only 批量生成 left/right-padding 错位问题（smoke 实测 batch=8
        时即便切 ``padding_side='left'`` 仍触发 right-padding 警告致开头 "{" 被切掉）。
        200 条 × ~1s/条 ≈ 3min，可接受；正确性优先于吞吐。
        """
        import torch

        from zephyr.nlp.nlp_inference import parse_sentiment

        if self._model is None or self._tokenizer is None:
            raise SFTTrainError("_batch_predict: 模型未训练")

        system, user_tpl = _load_prompt_template()
        self._model.eval()
        results: list[tuple[str, str]] = []

        # 切 left-padding（decoder-only 生成必需）
        orig_padding_side = self._tokenizer.padding_side
        self._tokenizer.padding_side = "left"
        try:
            for i in range(0, len(eval_items), batch_size):
                batch = eval_items[i : i + batch_size]
                prompts = []
                golds: list[str] = []
                for item in batch:
                    title = str(item.get("title", ""))
                    content = str(item.get("content", ""))[:300]
                    msg = [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user_tpl.format(title=title, content=content)},
                    ]
                    prompts.append(self._tokenizer.apply_chat_template(msg, tokenize=False, add_generation_prompt=True))
                    golds.append(str(item.get("sentiment", "neutral")).strip().lower())

                inputs = self._tokenizer(
                    prompts, return_tensors="pt", padding=True, truncation=True, max_length=self.config.max_seq_length
                )
                inputs = {k: v.to(self._model.device) for k, v in inputs.items()}
                with torch.no_grad():
                    out = self._model.generate(
                        **inputs,
                        max_new_tokens=DEFAULT_MAX_NEW_TOKENS,
                        do_sample=False,
                        pad_token_id=self._tokenizer.pad_token_id,
                    )
                # left-padding 下 input_ids.shape[1] = padding+prompt 长度，生成部分在其后
                prompt_lens = inputs["input_ids"].shape[1]
                generated = out[:, prompt_lens:]
                texts = self._tokenizer.batch_decode(generated, skip_special_tokens=True)
                for txt, gold in zip(texts, golds, strict=True):
                    sentiment, _ = parse_sentiment(txt)
                    results.append((sentiment, gold))
                _log.info("validate 进度: %d/%d", min(i + batch_size, len(eval_items)), len(eval_items))
        finally:
            self._tokenizer.padding_side = orig_padding_side
        return results

    def _load_default_eval(self) -> list[dict]:
        """从默认路径加载评估集。"""
        if not _DEFAULT_EVAL_PATH.exists():
            return []
        items: list[dict] = []
        with open(_DEFAULT_EVAL_PATH, encoding="utf-8") as f:
            for line in f:
                try:
                    items.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return items


__all__ = [
    "SentimentSFTTrainer",
    "SFTTrainConfig",
    "SFTTrainError",
    "build_sft_messages",
    "build_sft_dataset",
]
