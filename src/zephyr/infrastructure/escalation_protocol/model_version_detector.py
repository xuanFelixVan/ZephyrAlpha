"""Model Version Detector — v0.10.0 模型版本突变检测: model version change→degraded auto_guard。"""
from __future__ import annotations

class ModelVersionDetector:
    def __init__(self):
        self._known_versions:dict[str,str]={}

    def record_version(self, model_id:str, version:str):
        self._known_versions[model_id]=version

    def detect_change(self, model_id:str, current_version:str)->bool:
        known=self._known_versions.get(model_id)
        return known is not None and known!=current_version

    def should_degrade(self, model_id:str, current_version:str)->bool:
        return self.detect_change(model_id,current_version)
