from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class ReviewChunk:
    level: str
    chunk_id: str
    time_budget_minutes: int = 30

REVIEW_DIMENSIONS: dict[str, str] = {
    "consistency": "语义割裂检测",
    "accuracy": "数字引用验证",
    "completeness": "context manifest字段全",
    "traceability": "正反向链路",
    "token_efficiency": "审查Token/成果",
    "no_regression": "无下降→对比上次",
}
