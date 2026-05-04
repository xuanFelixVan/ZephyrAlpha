"""
Pipeline 数据模型
=================
依据：MOD-INF-006 §3.2.2 + GOV-AI-002 v2.0.0 模型路由策略
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field

from zephyr.shared.schemas import BASE_CONFIG

__all__ = [
    "M_MODULES",
    "M_MODULE_SPECS",
    "ClaudeRescueTrigger",
    "ModuleResult",
    "PipelineOrchestratorConfig",
    "PipelineResult",
    "PipelineStatus",
]


class PipelineStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    PARTIAL_FAILURE = "partial_failure"
    FAILURE = "failure"
    CLAUDE_RESCUE = "claude_rescue"


class ModuleStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    SKIPPED = "skipped"


class ModuleResult(BaseModel):
    """单模块执行结果"""
    model_config = BASE_CONFIG

    module_id: str = Field(..., pattern=r"^M(1[0-1]|[1-9])$")
    pipeline: str = Field(..., pattern=r"^[ABC]$")
    model: str = Field(...)
    status: ModuleStatus = ModuleStatus.PENDING
    output: dict[str, Any] = {}
    errors: list[str] = []
    tokens_used: int = 0
    duration_ms: int = 0
    started_at: Optional[str] = None
    finished_at: Optional[str] = None


class PipelineResult(BaseModel):
    """管线执行结果"""
    model_config = BASE_CONFIG

    task_id: str
    pipeline: str
    modules_executed: list[ModuleResult] = []
    overall_status: PipelineStatus = PipelineStatus.PENDING
    needs_claude_rescue: bool = False
    rescue_reason: str = ""
    started_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    finished_at: Optional[str] = None


class ClaudeRescueTrigger(BaseModel):
    """Claude 特种救援触发记录——GOV-AI-002 §三"""
    model_config = BASE_CONFIG

    triggered: bool = False
    reason: str = ""
    deepseek_failure_count: int = 0
    glm_rejection_count: int = 0
    is_owner_critical: bool = False
    has_security_tag: bool = False
    is_experimental: bool = False


class PipelineOrchestratorConfig(BaseModel):
    """管线编排器配置"""
    model_config = BASE_CONFIG

    max_retries: int = 3
    claude_rescue_threshold: int = 3
    glm_rejection_threshold: int = 2
    default_timeout_s: int = 300
    enable_parallel_modules: bool = False


# ============================================================================
# M1-M11 模块静态规格——GOV-AI-002 决策树的具体化
# ============================================================================

M_MODULE_SPECS: dict[str, dict[str, str]] = {
    "M1":  {"pipeline": "A", "model": "deepseek", "role": "任务卡解析→结构化执行计划"},
    "M2":  {"pipeline": "A", "model": "deepseek", "role": "上下文装配→调用 context_engine"},
    "M3":  {"pipeline": "A", "model": "deepseek", "role": "代码/文档生成——核心生产"},
    "M4":  {"pipeline": "A", "model": "deepseek", "role": "格式校验"},
    "M5":  {"pipeline": "A", "model": "glm",      "role": "产物打包"},
    "M6":  {"pipeline": "B", "model": "deepseek", "role": "差异检测——产出 vs 期望"},
    "M7":  {"pipeline": "B", "model": "glm",      "role": "深度审查——逐个文件逻辑/合规"},
    "M8":  {"pipeline": "B", "model": "deepseek", "role": "标准合规——PS/GOV/ADR"},
    "M9":  {"pipeline": "B", "model": "deepseek", "role": "风险评估——OWASP LLM Top 10"},
    "M10": {"pipeline": "B", "model": "deepseek", "role": "审计报告→Finding 格式"},
    "M11": {"pipeline": "B", "model": "deepseek", "role": "门禁裁决——G5/G6"},
}

M_MODULES: list[str] = sorted(M_MODULE_SPECS.keys(), key=lambda x: int(x[1:]))
