"""
Vibe Experiment Tracker — 氛围编程快速实验容量税 (盲点 #41)
特性：
  - 每日 200K tokens / 15 次实验上限
  - 自动清理实验产物
"""
import time
from dataclasses import dataclass
from typing import Any, Optional


class VibeExperimentTracker:
    """
    氛围编程实验追踪器 (盲点 #41)
    """

    DAILY_TOKEN_LIMIT = 200000
    DAILY_EXPERIMENT_LIMIT = 15

    def __init__(self):
        self._experiments_today = 0
        self._tokens_used_today = 0
        self._day_start = time.time()
        self._products: list[str] = []

    def _reset_if_new_day(self):
        if time.time() - self._day_start > 86400:
            self._experiments_today = 0
            self._tokens_used_today = 0
            self._day_start = time.time()

    def can_experiment(self, tokens_needed: int = 1000) -> bool:
        self._reset_if_new_day()
        if self._experiments_today >= self.DAILY_EXPERIMENT_LIMIT:
            return False
        if self._tokens_used_today + tokens_needed > self.DAILY_TOKEN_LIMIT:
            return False
        return True

    def record_experiment(self, tokens_used: int, product_path: str = ""):
        self._experiments_today += 1
        self._tokens_used_today += tokens_used
        if product_path:
            self._products.append(product_path)

    def get_status(self) -> dict:
        self._reset_if_new_day()
        return {
            "experiments_today": self._experiments_today,
            "experiments_remaining": self.DAILY_EXPERIMENT_LIMIT - self._experiments_today,
            "tokens_used_today": self._tokens_used_today,
            "tokens_remaining": self.DAILY_TOKEN_LIMIT - self._tokens_used_today,
            "experiment_limit": self.DAILY_EXPERIMENT_LIMIT,
            "token_limit": self.DAILY_TOKEN_LIMIT,
        }
