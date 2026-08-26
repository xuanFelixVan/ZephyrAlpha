# [BLUEPRINT] MOD-INT-OPENAPI | docs/03_modules/_domain_integration/api_documentation_generator/blueprint.md
# [MODULE] zephyr.integration.api_documentation_generator
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES] 无（协议核心纯内存；docs_writer/alert_sink/clock 全注入）
# [CONSUMERS] 运行时装配批（contracts/api 路由注解登记 / CI 契约漂移校验 / docs 输出供 MCP/前端消费）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 路由方法词表闭合(GET|POST|PUT|DELETE|PATCH); operation_id 全局唯一; 字段类型词表闭合; 生成结果按 path/field 名确定性排序; 同注册表必同文档; diff 超阈值必告警留痕; docs 输出仅经注入回调不触盘
# [MODIFY-GUARD] docs/03_modules/_domain_integration/api_documentation_generator/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ApiDocError(占位 ZA-INT-UNREGISTERED-API-DOC)——非法方法/空路径/operation_id 重复/非法字段类型/非法阈值/未知路由时抛
# [TESTS] tests/integration/test_api_documentation_generator.py
# [A_module] module_id=MOD-INT-OPENAPI | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""ApiDocumentationGenerator — API 文档生成器（MOD-INT-OPENAPI）。

B1-00337（AUD-DRAFT-001-DIGEST P2 波 P2-W13，CAND-BACL-004，C2 D-INT-05）：
从 contracts/api 路由注解**生成 OpenAPI 3.0 文档**（路由注册表 + schema 推导）
+ CI **契约漂移校验**（生成结果与基线 diff 超阈值告警）+ **输出至 docs** 供
MCP/前端消费语义（输出仅经注入回调，本件不触盘不触网）。

查重分工：llm_gateway/mcp gateway_server=协议实现（本件只产文档不跑服务）；
ctr002_producer_validator=信号契约校验（本件=HTTP 路由契约文档，零交集）。
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass
from typing import Callable, Final, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "ApiDocError",
    "ApiDocumentationGenerator",
    "DriftReport",
    "FieldSpec",
    "RouteSpec",
]

#: HTTP 方法词表（闭合）
_HTTP_METHODS: Final[frozenset[str]] = frozenset(
    {"GET", "POST", "PUT", "DELETE", "PATCH"}
)

#: JSON Schema 字段类型词表（闭合）
_FIELD_TYPES: Final[frozenset[str]] = frozenset(
    {"string", "integer", "number", "boolean", "object", "array"}
)

_OPENAPI_VERSION: Final = "3.0.3"


class ApiDocError(Exception):
    """API 文档生成输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-INT-UNREGISTERED-API-DOC。
    """


@dataclass(frozen=True)
class FieldSpec:
    """字段规格（schema 推导最小单元，frozen）。"""

    name: str
    type: str
    required: bool = True
    description: str = ""


@dataclass(frozen=True)
class RouteSpec:
    """路由注册条目（contracts/api 路由注解载体，frozen）。"""

    method: str
    path: str
    operation_id: str
    summary: str = ""
    tags: tuple[str, ...] = ()
    request_fields: tuple[FieldSpec, ...] = ()
    response_fields: tuple[FieldSpec, ...] = ()


@dataclass(frozen=True)
class DriftReport:
    """契约漂移报告（diff 告警载荷，frozen）。"""

    added: tuple[str, ...]
    removed: tuple[str, ...]
    changed: tuple[str, ...]
    diff_ratio: float
    threshold: float
    exceeded: bool
    generated_at: datetime.datetime


class ApiDocumentationGenerator:
    """OpenAPI 3.0 文档生成器（路由注册表 + schema 推导 + 漂移校验）。"""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
        alert_sink: Callable[[DriftReport], None] | None = None,
        docs_writer: Callable[[str], None] | None = None,
        drift_threshold: float = 0.2,
    ) -> None:
        if not 0.0 < drift_threshold <= 1.0:
            raise ApiDocError(f"非法漂移阈值: {drift_threshold!r}（须 (0,1]）")
        self._clock = clock or datetime.datetime.now
        self._alert_sink = alert_sink
        self._docs_writer = docs_writer
        self._drift_threshold = drift_threshold
        self._routes: dict[str, RouteSpec] = {}  # operation_id -> route
        self._published: list[str] = []  # docs_writer 缺省时的内存留痕

    # ── 内部 ─────────────────────────────────────────────────────────────

    @staticmethod
    def _validate_fields(fields: tuple[FieldSpec, ...], owner: str) -> None:
        seen: set[str] = set()
        for f in fields:
            if not f.name:
                raise ApiDocError(f"{owner} 字段名为空")
            if f.type not in _FIELD_TYPES:
                raise ApiDocError(f"{owner} 非法字段类型: {f.type!r}")
            if f.name in seen:
                raise ApiDocError(f"{owner} 字段名重复: {f.name!r}")
            seen.add(f.name)

    @staticmethod
    def _key(route: RouteSpec) -> str:
        return f"{route.method} {route.path}"

    @staticmethod
    def _schema_of(fields: tuple[FieldSpec, ...]) -> dict:
        properties = {f.name: {"type": f.type} for f in sorted(fields, key=lambda x: x.name)}
        required = sorted(f.name for f in fields if f.required)
        schema: dict = {"type": "object", "properties": properties}
        if required:
            schema["required"] = required
        return schema

    # ── 路由注册 ──────────────────────────────────────────────────────────

    def register_route(self, route: RouteSpec) -> None:
        """登记路由：方法/路径/operation_id/字段类型全校验（Fail-Closed）。"""
        if route.method not in _HTTP_METHODS:
            raise ApiDocError(f"非法 HTTP 方法: {route.method!r}")
        if not route.path or not route.path.startswith("/"):
            raise ApiDocError(f"非法路径: {route.path!r}（须以 / 开头）")
        if not route.operation_id:
            raise ApiDocError("operation_id 为空")
        if route.operation_id in self._routes:
            raise ApiDocError(f"operation_id 重复: {route.operation_id!r}")
        for existing in self._routes.values():
            if self._key(existing) == self._key(route):
                raise ApiDocError(f"路由重复: {self._key(route)!r}")
        self._validate_fields(route.request_fields, f"{self._key(route)} 请求")
        self._validate_fields(route.response_fields, f"{self._key(route)} 响应")
        self._routes[route.operation_id] = route

    def routes(self) -> tuple[RouteSpec, ...]:
        """已登记路由视图（按 (path, method) 确定性排序）。"""
        return tuple(sorted(self._routes.values(), key=lambda r: (r.path, r.method)))

    # ── 文档生成 ──────────────────────────────────────────────────────────

    def generate_openapi(self) -> dict:
        """生成 OpenAPI 3.0 文档 dict（确定性排序，同注册表必同输出）。"""
        paths: dict[str, dict] = {}
        for route in self.routes():
            operation: dict = {
                "operationId": route.operation_id,
                "responses": {
                    "200": {
                        "description": "OK",
                        "content": {
                            "application/json": {
                                "schema": self._schema_of(route.response_fields)
                            }
                        },
                    }
                },
            }
            if route.summary:
                operation["summary"] = route.summary
            if route.tags:
                operation["tags"] = sorted(route.tags)
            if route.request_fields:
                operation["requestBody"] = {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": self._schema_of(route.request_fields)
                        }
                    },
                }
            paths.setdefault(route.path, {})[route.method.lower()] = operation
        return {
            "openapi": _OPENAPI_VERSION,
            "info": {"title": "ZephyrAlpha API", "version": "1.0.0"},
            "paths": {p: paths[p] for p in sorted(paths)},
        }

    def generate_yaml(self) -> str:
        """生成确定性 YAML 文本（键排序、缩进 2，纯内存渲染不依赖外部库）。"""
        return self._render_yaml(self.generate_openapi())

    @classmethod
    def _render_yaml(cls, obj: object, indent: int = 0) -> str:
        lines: list[str] = []
        pad = "  " * indent
        if isinstance(obj, Mapping):
            for key in sorted(obj, key=str):
                value = obj[key]
                if isinstance(value, (Mapping, list)) and value:
                    lines.append(f"{pad}{key}:")
                    lines.append(cls._render_yaml(value, indent + 1))
                elif isinstance(value, (Mapping, list)):
                    lines.append(f"{pad}{key}: {'{}' if isinstance(value, Mapping) else '[]'}")
                else:
                    lines.append(f"{pad}{key}: {cls._scalar(value)}")
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, (Mapping, list)):
                    lines.append(f"{pad}-")
                    lines.append(cls._render_yaml(item, indent + 1))
                else:
                    lines.append(f"{pad}- {cls._scalar(item)}")
        else:
            lines.append(f"{pad}{cls._scalar(obj)}")
        return "\n".join(lines) + ("\n" if indent == 0 else "")

    @staticmethod
    def _scalar(value: object) -> str:
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, (int, float)):
            return str(value)
        return str(value)

    # ── docs 输出（注入回调，缺省内存留痕） ─────────────────────────────────

    def publish_docs(self) -> str:
        """输出文档：经注入 docs_writer 回调；未注入则内存留痕。返回 YAML。"""
        content = self.generate_yaml()
        if self._docs_writer is not None:
            self._docs_writer(content)
        else:
            self._published.append(content)
        _log.info("OpenAPI 文档已输出（%d 路由）", len(self._routes))
        return content

    @property
    def published(self) -> tuple[str, ...]:
        """docs_writer 缺省时的内存留痕视图。"""
        return tuple(self._published)

    # ── 契约漂移校验（CI 语义） ─────────────────────────────────────────────

    def diff_against_baseline(self, baseline: Mapping) -> DriftReport:
        """与基线 OpenAPI 文档（Mapping 注入）diff；超阈值告警留痕。

        粒度=operation（方法+路径）；响应 schema 变化记 changed。
        diff_ratio = |added|+|removed|+|changed| / max(|基线∪当前|, 1)。
        """
        if not isinstance(baseline, Mapping) or "paths" not in baseline:
            raise ApiDocError("基线非法：须为含 paths 键的 OpenAPI Mapping")
        current_ops = self._operations_of(self.generate_openapi())
        baseline_ops = self._operations_of(baseline)
        added = tuple(sorted(k for k in current_ops if k not in baseline_ops))
        removed = tuple(sorted(k for k in baseline_ops if k not in current_ops))
        changed = tuple(sorted(
            k for k in current_ops.keys() & baseline_ops.keys()
            if current_ops[k] != baseline_ops[k]
        ))
        union = len(current_ops.keys() | baseline_ops.keys())
        ratio = (len(added) + len(removed) + len(changed)) / max(union, 1)
        exceeded = ratio > self._drift_threshold
        report = DriftReport(
            added=added,
            removed=removed,
            changed=changed,
            diff_ratio=ratio,
            threshold=self._drift_threshold,
            exceeded=exceeded,
            generated_at=self._clock(),
        )
        if exceeded:
            _log.warning(
                "契约漂移超阈值: ratio=%.3f > %.3f (added=%d removed=%d changed=%d)",
                ratio, self._drift_threshold, len(added), len(removed), len(changed),
            )
            if self._alert_sink is not None:
                try:
                    self._alert_sink(report)
                except Exception:  # noqa: BLE001 — 告警不阻断生成
                    _log.exception("alert_sink 告警失败")
        return report

    @staticmethod
    def _operations_of(doc: Mapping) -> dict[str, dict]:
        """拍平 OpenAPI 文档为 {方法+路径: operation}（确定性）。"""
        ops: dict[str, dict] = {}
        paths = doc.get("paths", {})
        if not isinstance(paths, Mapping):
            return ops
        for path, item in paths.items():
            if not isinstance(item, Mapping):
                continue
            for method, operation in item.items():
                ops[f"{str(method).upper()} {path}"] = operation
        return ops
