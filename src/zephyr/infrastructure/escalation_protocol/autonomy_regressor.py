"""Autonomy Regressor — v0.10.0 渐进自治可逆性管理器: confidence<阈值→自动regress自治级别。"""
from __future__ import annotations

class AutonomyRegressor:
    LEVELS=["autonomous","auto_guard","blocked"]

    def should_regress(self, current_level:str, confidence:float, error_count:int)->str:
        idx=self.LEVELS.index(current_level) if current_level in self.LEVELS else 0
        if confidence<0.3 and idx<len(self.LEVELS)-1:
            return self.LEVELS[idx+1]
        if error_count>5 and idx<len(self.LEVELS)-1:
            return self.LEVELS[idx+1]
        return current_level

    def regression_path(self, level:str)->list[str]:
        idx=self.LEVELS.index(level) if level in self.LEVELS else 0
        return self.LEVELS[idx:]
