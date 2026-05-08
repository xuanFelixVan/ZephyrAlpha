"""
Agent Spec → Pipeline 集成桥接层

提供:
  - PipelineSkillBridge: Pipeline → SkillLoader 双向桥接
  - SkillContextInjector: 将加载的 Skill 注入 Pipeline 模块执行上下文
"""

from zephyr.agent_spec.integration.pipeline_bridge import (
    PipelineSkillBridge,
    SkillContextInjector,
    SkillInjectionResult,
)

__all__ = ['PipelineSkillBridge', 'SkillContextInjector', 'SkillInjectionResult', 'pipeline_bridge']
