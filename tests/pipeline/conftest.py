# [A_test] module_id: MOD-GOV_conftest | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-009 | docs/03_modules/_cross_layer/pipeline/blueprint.md | §
# [MODULE] tests.unit.pipeline.conftest
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""Pipeline 测试全局配置——阻止单元测试命中真实 LLM API。

清除所有 LLM provider 的 API key 环境变量，强制 LLMGateway 进入 simulated 模式，
避免单元测试因真实 API 调用而挂起或产生费用。
"""

from __future__ import annotations

import os

import pytest

_LLM_API_KEY_VARS = (
    "DEEPSEEK_API_KEY",
    "GLM_API_KEY",
    "ANTHROPIC_API_KEY",
    "OPENAI_API_KEY",
)


@pytest.fixture(autouse=True)
def _isolate_llm_api_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    """清除所有 LLM API key 环境变量，确保测试使用 simulated 模式。"""
    for var in _LLM_API_KEY_VARS:
        monkeypatch.delenv(var, raising=False)
