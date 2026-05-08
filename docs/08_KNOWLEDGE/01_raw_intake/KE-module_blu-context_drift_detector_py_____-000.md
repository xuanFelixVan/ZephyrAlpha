---
module_id: KE-module_blu-context_drift_detector_py_____-000
title: context_drift_detector.py — 新增文件（L2 ABAC 扩展）
category: module_blueprint
---

# context_drift_detector.py — 新增文件（L2 ABAC 扩展）

context_drift_detector.py — 新增文件（L2 ABAC 扩展）
class ContextDriftDetector:
    """
    Context Drift 检测器——实时追踪Agent操作链中的意图漂移。
    
    核心原理：
    - 对比"当前操作模式"与"任务启动时的原始意图"
    - 当语义距离超过阈值 → 标记为漂移
    """
    
    def __init__(self, drift_window: int = 10):
        self.drift_window = drift_window  # 检测最近N步操作链
    
    async def detect_drift(
        self,
        original_intent: str,
        operation_chain: list[Action],
        current_action: Action,
    ) -> DriftReport:
        """
        检测操作链中的意图漂移。
        
        三个检测维度：
        1. 操作类型漂移——初始为read→逐步转为write/delete（类型熵增）
        2. 路径漂移——操作目标从src/逐步扩展到config/、data/（路径熵增）
        3. 语义漂移——借助嵌入相似度对比"原始意图"与"当前操作描述"的语义距离
        """
        # 维度1: 操作类型熵
        type_entropy = self._compute_type_entropy(operation_chain)
        type_drift = type_entropy > 1.5  # 从单一操作类型变为多类型混合
        
        # 维度2: 路径熵
        path_entropy = self._compute_path_entropy(operation_chain)
        path_drift = path_entropy > 2.0  # 操作路径明显扩展
        
        # 维度3: 语义距离
        semantic_drift = await self._compute_semantic_drift(
            original_intent, operation_chain
        )
        
        return DriftReport(
            type_drift=type_drift,
            path_drift=path_drift,
            semantic_drift=semantic_drift,
            overall_drift_score=(type_entropy + path_entropy + semantic_drift) / 3,
            recommendation=(
                "BLOCKED" if semantic_drift > 0.7
                else "AUTO_GUARD" if semantic_drift > 0.4
                else "ALLOW"
            ),
        )

class DriftReport(BaseModel):
    type_drift: bool
    path_drift: bool
    semantic_drift: float          # 0-1, 越高越偏离
    overall_drift_score: float
    recommendation: str             # ALLOW | AUTO_GUARD | BLOCKED
    detected_at_step: int           # 在第几步检测到漂移
```

---
