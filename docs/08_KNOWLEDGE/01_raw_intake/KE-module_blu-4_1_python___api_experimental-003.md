---
module_id: KE-module_blu-4_1_python___api_experimental-003
title: 4.1 Python 库 API（experimental 主用）
category: module_blueprint
---

# 4.1 Python 库 API（experimental 主用）

4.1 Python 库 API（experimental 主用）

```python
class InProcessLLMSecurityGateway:  # implements LLMSecurityGatewayProtocol

    def __init__(self, config: LSGConfig) -> None: ...

    # ───── L1+L2：输入审查 ─────
    async def validate_input(self, payload: InputPayload) -> InputVerdict:
        """
        输入 LLM 前调用。
        流程：L1 分类 → 若 HOSTILE 直接拒；否则走 L2 包裹生成 isolated_prompt。
        返回 verdict.allow + isolated_prompt（供 Agent 直接送给 LLM）。
        """

    # ───── L3+L4：输出审查 ─────
    async def validate_output(
        self,
        payload: OutputPayload,
        schema_id: str | None = None,
    ) -> OutputVerdict:
        """
        LLM 输出后调用（工具调用参数 / 最终 result）。
        流程：
          1. L3 Pydantic 校验（若提供 schema_id）
          2. L4 异常模式扫描（含 secret_scan + pattern_inspect）
          3. 任一不通过 → allow=False + violations
        """

    async def scan_secrets(self, text: str, context: str = "generic") -> SecretScanResult:
        """
        独立 secret 扫描入口（pre-commit / 运行时审计都可调）。
        """

    async def inspect_patterns(self, text: str, profile: str = "default") -> PatternScanResult:
        """
        独立异常模式扫描（专供 content moderation 场景）。
        """

    # ───── 策略管理 ─────
    async def register_schema(self, schema_id: str, schema_cls: type) -> None:
        """下游服务调用时注册 Pydantic schema（完成于 wiring 阶段）。"""

    async def bump_strictness(
        self,
        delta: float,
        ttl_minutes: int,
        reason: str,
    ) -> None:
        """
        FLE 通过 LSGControlActionProtocol 调用：临时提升严格度（拒绝阈值下调）。
        TTL 到期自动回默认。
        """

    async def get_strictness(self) -> StrictnessSnapshot: ...

    # ───── 统计 ─────
    async def stats(self) -> LSGStats:
        """输出供 FLE 上报：bypass_rate / reject_rate / secret_leak_events / 异常模式命中分布等。"""
```
