"""Fixture: relate 预筛语料——无关文件（与 near_dup_*.py 无相似性）。"""


class DataValidator:
    def __init__(self, schema):
        self.rules = schema

    def validate(self, record):
        for field, constraint in self.rules.items():
            if field not in record:
                return False
            if not constraint(record[field]):
                return False
        return True
