# [BLUEPRINT] MOD-INF-088 | docs/03_modules/_domain_infrastructure_operations/loki_log_pipeline/blueprint.md
# [MODULE] zephyr.infra_ops.loki_log_pipeline
# [DOMAIN] D_INFRA_OPS
# [DEPENDENCIES] 无（纯内存管道；loki_push_client/sanitizer/clock 全注入，不真发 HTTP）
# [CONSUMERS] 运行时装配批（Loki push client 绑定 / 脱敏钩子装配 / 保留策略裁决与 Parquet 导出编排）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 日志类别词表闭合; 推送仅经注入 client(未注入 Fail-Closed 不真发 HTTP); 失败重试计数确定性(超限入 DLQ); LogQL 选择器键序确定性; 热30天/冷Parquet 导出策略由注入时钟裁决; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_infrastructure_operations/loki_log_pipeline/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] LokiPipelineError(占位 ZA-INF-UNREGISTERED-LOKI-PIPELINE)——非法类别/非法标签/client缺失/参数非法/选择器为空时抛
# [TESTS] tests/infra_ops/test_loki_log_pipeline.py
# [A_module] module_id=MOD-INF-088 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
LokiLogPipeline — Loki 日志聚合管道（MOD-INF-088）。

B8-10662（AUD-DRAFT-001-DIGEST P2 波 P2-W01，CAND-INFRAOPS-006，A8集成
架构）：Loki 本地单实例对接面——JSON 结构化日志（Agent 决策 / 自治边界
检查 / 风控否决 / 异常事件）构建与推送管道（loki_push_client 注入，不真
发 HTTP；失败重试计数 + DLQ 队列），LogQL 查询构建器，热 30 天保留 +
冷数据导出 Parquet 策略裁决（注入时钟），日志脱敏钩子注入。
docker-compose 部署面归 Owner 窗口，不在本件范围。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: loki_push_client 参数
#   fields: 参数 loki_push_client（无注解）
#   code: loki_log_pipeline.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: loki_log_pipeline.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: sanitizer 参数
#   fields: 参数 sanitizer（无注解）
#   code: loki_log_pipeline.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: max_retries 参数
#   fields: 参数 max_retries（无注解）
#   code: loki_log_pipeline.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① LokiLogPipeline
#   name_en: LokiLogPipeline
#   intro: Loki 日志管道件（构建 + 推送重试/DLQ + LogQL + 保留裁决）。
#   desc: Loki 日志管道件（构建 + 推送重试/DLQ + LogQL + 保留裁决）。；公共方法（定义序）: build_entry, push, retry_count, dlq, build_logql, retent…
#   inputs: loki_push_client clock sanitizer max_retries hot_retention_days
#   outputs: 返回值
#   （注：A1 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（4 定义）
#   name_en: public defs
#   intro: LokiLogPipeline
#   downstream: 运行时装配批（Loki push client 绑定 / 脱敏钩子装配 / 保留策略裁决与 Parquet 导出编排）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import logging
from enum import Enum
from typing import Callable, Final, Iterable, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "LogCategory",
    "LokiLogPipeline",
    "LokiPipelineError",
    "RetentionTier",
]


class LokiPipelineError(Exception):
    """Loki 管道输入/推送非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-INF-UNREGISTERED-LOKI-PIPELINE。
    """


class LogCategory(str, Enum):
    """结构化日志类别（词表闭合）。"""

    AGENT_DECISION = "agent_decision"
    AUTONOMY_BOUNDARY = "autonomy_boundary"
    RISK_VETO = "risk_veto"
    ANOMALY_EVENT = "anomaly_event"


class RetentionTier(str, Enum):
    """保留策略裁决结果。"""

    HOT = "hot"
    COLD_EXPORT = "cold_export"  # 冷数据导出 Parquet


class LokiLogPipeline:
    """Loki 日志管道件（构建 + 推送重试/DLQ + LogQL + 保留裁决）。"""

    def __init__(
        self,
        *,
        loki_push_client: Callable[[dict], bool] | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
        sanitizer: Callable[[dict], dict] | None = None,
        max_retries: int = 3,
        hot_retention_days: int = 30,
    ) -> None:
        if max_retries < 0:
            raise LokiPipelineError(f"max_retries 不可为负: {max_retries}")
        if hot_retention_days <= 0:
            raise LokiPipelineError(f"hot_retention_days 须为正: {hot_retention_days}")
        self._client = loki_push_client
        self._clock = clock or datetime.datetime.now
        self._sanitizer = sanitizer
        self._max_retries = max_retries
        self._hot_days = hot_retention_days
        self._retry_count = 0
        self._dlq: list[dict] = []

    # ── 结构化日志构建 ────────────────────────────────────────────────────

    def build_entry(
        self,
        category: LogCategory,
        labels: Mapping[str, str],
        payload: Mapping,
        ts: datetime.datetime | None = None,
    ) -> dict:
        """构建 JSON 结构化日志（payload 经注入脱敏钩子处理）。"""
        if not isinstance(category, LogCategory):
            raise LokiPipelineError(f"非法日志类别: {category!r}")
        if labels is None:
            raise LokiPipelineError("labels 不可为 None")
        clean_labels = dict(labels)
        for k, v in clean_labels.items():
            if not k or not isinstance(k, str):
                raise LokiPipelineError(f"非法标签键: {k!r}")
            if not isinstance(v, str):
                raise LokiPipelineError(f"非法标签值（须为 str）: {k}={v!r}")
        if payload is None:
            raise LokiPipelineError("payload 不可为 None")
        clean_payload = dict(payload)
        if self._sanitizer is not None:
            clean_payload = dict(self._sanitizer(clean_payload))
        stamp = ts if ts is not None else self._clock()
        return {
            "category": category.value,
            "labels": clean_labels,
            "ts": stamp.isoformat(),
            "payload": clean_payload,
        }

    # ── 推送管道（重试 + DLQ） ────────────────────────────────────────────

    def push(self, entry: Mapping) -> bool:
        """推送一条：client 未注入 Fail-Closed；失败重试计数，超限入 DLQ。"""
        if self._client is None:
            raise LokiPipelineError("loki_push_client 未注入（禁止真发 HTTP 旁路）")
        if not isinstance(entry, Mapping) or "category" not in entry or "ts" not in entry:
            raise LokiPipelineError("entry 结构非法（须含 category/ts）")
        attempt = 0
        while True:
            try:
                ok = bool(self._client(dict(entry)))
            except Exception:  # noqa: BLE001 — 推送异常按失败重试
                _log.exception("loki_push_client 推送异常")
                ok = False
            if ok:
                return True
            attempt += 1
            if attempt > self._max_retries:
                self._dlq.append(dict(entry))
                _log.warning("推送超限入 DLQ: category=%s", entry.get("category"))
                return False
            self._retry_count += 1

    @property
    def retry_count(self) -> int:
        """累计重试次数。"""
        return self._retry_count

    @property
    def dlq(self) -> list[dict]:
        """死信队列（推送超限条目）。"""
        return list(self._dlq)

    # ── LogQL 查询构建 ────────────────────────────────────────────────────

    def build_logql(
        self,
        selector: Mapping[str, str],
        filters: Iterable[str] | None = None,
    ) -> str:
        """LogQL 构建：{k="v",...}（键确定性排序）+ 行过滤器 |= \"f\"。"""
        if not selector:
            raise LokiPipelineError("selector 为空（LogQL 须至少一个标签选择器）")
        parts = []
        for k in sorted(selector):
            v = selector[k]
            if not k or not isinstance(v, str) or not v:
                raise LokiPipelineError(f"非法选择器: {k!r}={v!r}")
            parts.append(f'{k}="{v}"')
        query = "{" + ", ".join(parts) + "}"
        for f in filters or ():
            if not f:
                raise LokiPipelineError("过滤器为空串")
            query += f' |= "{f}"'
        return query

    # ── 保留策略裁决（热30天/冷 Parquet 导出） ─────────────────────────────

    def retention_decision(self, ts: datetime.datetime) -> RetentionTier:
        """按注入时钟裁决：距今 ≤hot_retention_days → HOT，否则 COLD_EXPORT。"""
        age = self._clock() - ts
        if age <= datetime.timedelta(days=self._hot_days):
            return RetentionTier.HOT
        return RetentionTier.COLD_EXPORT

    def entries_for_export(self, entries: Iterable[Mapping]) -> list[dict]:
        """筛出需冷导出 Parquet 的条目（按 entry["ts"] ISO 解析裁决）。"""
        out: list[dict] = []
        for entry in entries:
            stamp = entry.get("ts")
            if not isinstance(stamp, str):
                raise LokiPipelineError(f"entry ts 非法: {stamp!r}")
            ts = datetime.datetime.fromisoformat(stamp)
            if self.retention_decision(ts) is RetentionTier.COLD_EXPORT:
                out.append(dict(entry))
        return out
