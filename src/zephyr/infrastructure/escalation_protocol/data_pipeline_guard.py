"""Data Pipeline Guard — v0.10.0 数据管道完整性防护: schema validation+row count check+checksum verify。"""
from __future__ import annotations
import hashlib

class DataPipelineGuard:
    def validate_schema(self, actual_columns:list[str], expected_columns:list[str])->list[str]:
        return list(set(expected_columns)-set(actual_columns))

    def verify_checksum(self, data:str, expected:str)->bool:
        actual=hashlib.sha256(data.encode()).hexdigest()[:8]
        return actual==expected

    def check_row_count(self, actual:int, expected:int, tolerance_pct:int=5)->bool:
        if expected==0:return actual==0
        diff=abs(actual-expected)/expected*100
        return diff<=tolerance_pct
