# [BLUEPRINT] MOD-RPT-032 | 待统筹登记（55 号 §6 模板引擎固化外化行，GAP-F-40 模板迁出）
# [MODULE] zephyr.reporting.review_template_registry
# [DOMAIN] D_REPORTING
# [DEPENDENCIES] zephyr.shared.foundation.errors; zephyr.shared.io.paths; config/review_templates.yaml(模板注册表真源)
# [CONSUMERS] MOD-RPT-009_summary(ai_review_summary 战报/prompt/兜底模板供给) ; 复盘页调用方(版本切换)
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 模板单一真源=config/review_templates.yaml(本模块打包默认 v1 与在档 v1 双向一致性锁,防双真源漂移); 版本可切换(get(kind, version)); 默认模板回退(version=None/版本缺失→default_version+notes; 文件缺失→打包默认模板+notes,复盘页不因模板缺失空白); schema/占位符畸形 fail-closed(必需占位符缺失/未声明占位符/默认版本缺席一律 raise); 占位符封闭集按 kind 声明; frozen dataclass JSON 可序列化
# [MODIFY-GUARD] 55_monitoring_review.md §6; docs/_working/2026-08-22-frontend-backend-gap-ledger.md GAP-F-40 行
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ReviewTemplateRegistryError(ZA-RPT-0034, schema/YAML 畸形 fail-closed)
# [TESTS] tests/reporting/test_review_template_registry.py
# [A_module] module_id=MOD-RPT-032 | layer=module | stability=testing | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-RPT-032 — 复盘模板注册表（55 号 §6 模板引擎固化外化，GAP-F-40 模板迁出）。

55 号 §6 暂缓项"复盘模板内容固化进代码（模板引擎）"施工：GAP-F-40
ai_review_summary 的战报/prompt/兜底结语三模板从代码常量迁出到注册位
（config/review_templates.yaml）——**版本可切换 + 默认模板回退**：

  - 版本可切换：``get(kind, version)`` 按版本取模板（注册表多版本并存）；
  - 默认模板回退：version=None 或版本未注册 → default_version（notes 留痕）；
    注册表文件缺失 → 打包默认模板（embedded_default，v1=迁移前代码常量原文，
    notes 留痕）——复盘页不因模板缺失而空白（同 ai_review_summary 降级链哲学）；
  - fail-closed 侧：YAML 畸形 / schema 畸形 / 必需占位符缺失 / 未声明占位符 /
    默认版本缺席一律 ReviewTemplateRegistryError（治理件不给坏模板让路）。

与 threshold_loader 的口径差异（留痕）：阈值注册表缺文件 fail-closed（风控件
禁止第二真源）；模板注册表缺文件 fail-open 回退打包默认（展示件，任务口径
"默认模板回退"）——在档文件 v1 与打包默认 v1 有一致性测试锁防双真源漂移。

模板 kind 封闭集（GAP-F-40 三模板，占位符封闭集见 _REQUIRED_PLACEHOLDERS）：
  - war_report       每日战报五段（市场回顾/板块亮点/预案执行/风险事件/AI 结语）
  - prompt_summary   LLM 结语 prompt 参数化模板
  - fallback_summary 网关降级兜底结语模板
  新增 kind 免占位符校验（通用注册表位）；既有三 kind 占位符全闭合校验。
"""

from __future__ import annotations

import logging
import string
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Final, Mapping, Sequence

import yaml

from zephyr.shared.foundation.errors import ZephyrBaseError
from zephyr.shared.io.paths import REPO_ROOT

_logger = logging.getLogger(__name__)

__all__: Final = [
    "REVIEW_TEMPLATES_PATH",
    "ReviewTemplateRegistry",
    "ReviewTemplateRegistryError",
    "TEMPLATE_FALLBACK_SUMMARY",
    "TEMPLATE_PROMPT_SUMMARY",
    "TEMPLATE_WAR_REPORT",
    "TemplateSpec",
]

#: 模板 kind 封闭集（GAP-F-40 三模板）
TEMPLATE_WAR_REPORT: Final[str] = "war_report"
TEMPLATE_PROMPT_SUMMARY: Final[str] = "prompt_summary"
TEMPLATE_FALLBACK_SUMMARY: Final[str] = "fallback_summary"

#: 模板注册表真源路径（版本可切换+默认回退的载体）
REVIEW_TEMPLATES_PATH: Final[Path] = REPO_ROOT / "config" / "review_templates.yaml"

#: 各 kind 占位符封闭集（必需=允许，渲染字段完备性 fail-closed 校验口径）
_REQUIRED_PLACEHOLDERS: Final[dict[str, frozenset[str]]] = {
    TEMPLATE_WAR_REPORT: frozenset(
        {"trade_date", "market_overview", "sector_highlights", "plan_outcomes", "risk_events", "summary"}
    ),
    TEMPLATE_PROMPT_SUMMARY: frozenset(
        {"trade_date", "market_overview", "sector_highlights", "plan_outcomes", "risk_events", "max_chars"}
    ),
    TEMPLATE_FALLBACK_SUMMARY: frozenset(
        {"trade_date", "market_overview", "sector_highlights", "plan_outcomes", "risk_events"}
    ),
}

#: 打包默认模板 v1（GAP-F-40 迁移前 ai_review_summary 代码常量原文，单一真源锚点）
_EMBEDDED_V1_BODIES: Final[dict[str, str]] = {
    TEMPLATE_WAR_REPORT: """# 每日战报 {trade_date}

## 1. 市场回顾
{market_overview}

## 2. 板块亮点
{sector_highlights}

## 3. 预案执行
{plan_outcomes}

## 4. 风险事件
{risk_events}

## 5. AI 结语
{summary}
""",
    TEMPLATE_PROMPT_SUMMARY: (
        "你是盘后复盘助手。请基于以下 {trade_date} 盘面事实，用一句话总结今日行情并给出明日操作建议"
        "（不超过 {max_chars} 字，只说事实与纪律，不预测点位）：\n"
        "市场回顾：{market_overview}\n"
        "板块亮点：{sector_highlights}\n"
        "预案执行：{plan_outcomes}\n"
        "风险事件：{risk_events}\n"
    ),
    TEMPLATE_FALLBACK_SUMMARY: (
        "{trade_date} 复盘：{market_overview}；板块亮点：{sector_highlights}；"
        "预案执行：{plan_outcomes}；风险事件：{risk_events}。"
        "操作建议：严格按预案边界执行，控制仓位，不追预案外标的。"
    ),
}

_EMBEDDED_DEFAULT_VERSION: Final[str] = "v1"


class ReviewTemplateRegistryError(ZephyrBaseError):
    """复盘模板注册表畸形——YAML/schema/占位符/默认版本问题（fail-closed）。"""

    error_code = "ZA-RPT-0034"


@dataclass(frozen=True, slots=True)
class TemplateSpec:
    """单条模板产出（kind+version 定位，notes 留痕回退原因）。"""

    kind: str
    version: str
    body: str
    status: str
    source: str  # registry_file | embedded_default
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _placeholders(body: str) -> set[str]:
    """提取 .format 占位符根名（{a.b}/{a[0]} 归一为 a；{} 自动序号视为未声明）。"""
    found: set[str] = set()
    for _, field_name, _, _ in string.Formatter().parse(body):
        if field_name is None:
            continue
        root = field_name.split(".")[0].split("[")[0]
        found.add(root)
    return found


class ReviewTemplateRegistry:
    """复盘模板注册表（版本可切换 + 默认模板回退）。

    Args:
        templates: {kind: {version: body}} 映射。
        default_version: 默认版本（每个 kind 都必须含有该版本，fail-closed）。
        source: 来源标定（registry_file / embedded_default）。
        statuses: {kind: {version: status}}（可选，默认 active）。
        notes: 注册表级留痕（如"文件缺失回退打包默认"）。
    """

    def __init__(
        self,
        templates: Mapping[str, Mapping[str, str]],
        *,
        default_version: str,
        source: str,
        statuses: Mapping[str, Mapping[str, str]] | None = None,
        notes: Sequence[str] = (),
    ) -> None:
        if not isinstance(default_version, str) or not default_version.strip():
            raise ReviewTemplateRegistryError(
                "default_version 非法（强制非空字符串）",
                details={"default_version": repr(default_version)},
            )
        if not isinstance(templates, Mapping) or not templates:
            raise ReviewTemplateRegistryError("templates 非法（强制非空映射）", details={})
        self._default_version = default_version.strip()
        self._source = source
        self._notes = tuple(notes)
        self._templates: dict[str, dict[str, str]] = {}
        self._statuses: dict[str, dict[str, str]] = {}
        for kind, versions in templates.items():
            if not isinstance(kind, str) or not kind.strip():
                raise ReviewTemplateRegistryError("模板 kind 不允许为空", details={})
            if not isinstance(versions, Mapping) or not versions:
                raise ReviewTemplateRegistryError(
                    f"模板 {kind} 缺 versions（强制非空映射）",
                    details={"kind": kind},
                )
            if self._default_version not in versions:
                raise ReviewTemplateRegistryError(
                    f"模板 {kind} 缺默认版本 {self._default_version}",
                    details={"kind": kind, "default_version": self._default_version},
                )
            self._templates[kind] = {}
            self._statuses[kind] = {}
            for version, body in versions.items():
                if not isinstance(version, str) or not version.strip():
                    raise ReviewTemplateRegistryError(
                        f"模板 {kind} 版本名不允许为空", details={"kind": kind}
                    )
                if not isinstance(body, str) or not body.strip():
                    raise ReviewTemplateRegistryError(
                        f"模板 {kind}@{version} body 非法（强制非空字符串）",
                        details={"kind": kind, "version": repr(version)},
                    )
                self._validate_placeholders(kind, version, body)
                self._templates[kind][version] = body
                status = (statuses or {}).get(kind, {}).get(version, "active")
                self._statuses[kind][version] = str(status)

    @staticmethod
    def _validate_placeholders(kind: str, version: str, body: str) -> None:
        required = _REQUIRED_PLACEHOLDERS.get(kind)
        if required is None:
            return  # 未登记 kind 免占位符校验（通用注册表位）
        found = _placeholders(body)
        missing = required - found
        if missing:
            raise ReviewTemplateRegistryError(
                f"模板 {kind}@{version} 必需占位符缺失: {sorted(missing)}",
                details={"kind": kind, "version": version, "missing": sorted(missing)},
            )
        undeclared = found - required
        if undeclared:
            raise ReviewTemplateRegistryError(
                f"模板 {kind}@{version} 含未声明占位符: {sorted(undeclared)}（封闭集口径）",
                details={"kind": kind, "version": version, "undeclared": sorted(undeclared)},
            )

    # ── 构造入口 ──

    @classmethod
    def embedded_default(cls, *, notes: Sequence[str] = ()) -> "ReviewTemplateRegistry":
        """打包默认注册表（v1=GAP-F-40 迁移前代码常量原文）。"""
        return cls(
            {kind: {_EMBEDDED_DEFAULT_VERSION: body} for kind, body in _EMBEDDED_V1_BODIES.items()},
            default_version=_EMBEDDED_DEFAULT_VERSION,
            source="embedded_default",
            notes=notes,
        )

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any], *, source: str = "registry_file") -> "ReviewTemplateRegistry":
        """从 YAML 解析产物构造（schema 畸形 fail-closed）。"""
        if not isinstance(raw, Mapping):
            raise ReviewTemplateRegistryError("注册表根节点非法（须映射）", details={})
        default_version = raw.get("default_version")
        templates_raw = raw.get("templates")
        if not isinstance(templates_raw, Mapping):
            raise ReviewTemplateRegistryError("templates 节点非法（须映射）", details={})
        templates: dict[str, dict[str, str]] = {}
        statuses: dict[str, dict[str, str]] = {}
        for kind, entry in templates_raw.items():
            if not isinstance(entry, Mapping):
                raise ReviewTemplateRegistryError(
                    f"模板 {kind} 条目非法（须映射）", details={"kind": str(kind)}
                )
            versions_raw = entry.get("versions")
            if not isinstance(versions_raw, Mapping):
                raise ReviewTemplateRegistryError(
                    f"模板 {kind} 缺 versions 映射", details={"kind": str(kind)}
                )
            templates[str(kind)] = {}
            statuses[str(kind)] = {}
            for version, ver_entry in versions_raw.items():
                if not isinstance(ver_entry, Mapping) or "body" not in ver_entry:
                    raise ReviewTemplateRegistryError(
                        f"模板 {kind}@{version} 缺 body 字段",
                        details={"kind": str(kind), "version": str(version)},
                    )
                templates[str(kind)][str(version)] = ver_entry["body"]
                statuses[str(kind)][str(version)] = str(ver_entry.get("status", "active"))
        return cls(
            templates,
            default_version=default_version if isinstance(default_version, str) else "",
            source=source,
            statuses=statuses,
        )

    @classmethod
    def load(cls, path: Path | str | None = None) -> "ReviewTemplateRegistry":
        """从注册表文件加载（默认 REVIEW_TEMPLATES_PATH）。

        文件缺失 → 打包默认模板回退（fail-open 留痕，展示件口径）；
        文件存在但 YAML/schema 畸形 → ReviewTemplateRegistryError（fail-closed）。
        """
        target = Path(path) if path is not None else REVIEW_TEMPLATES_PATH
        if not target.is_file():
            _logger.warning("REVIEW_TEMPLATES_MISSING path=%s（回退打包默认模板）", target)
            return cls.embedded_default(notes=(f"模板注册表文件缺失：{target}（回退打包默认模板）",))
        try:
            raw = yaml.safe_load(target.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            raise ReviewTemplateRegistryError(
                f"模板注册表 YAML 畸形: {target}",
                details={"path": str(target), "error": str(exc)},
            ) from exc
        except OSError as exc:
            raise ReviewTemplateRegistryError(
                f"模板注册表读取失败: {target}",
                details={"path": str(target), "error": str(exc)},
            ) from exc
        if raw is None:
            raise ReviewTemplateRegistryError(
                f"模板注册表为空文件: {target}", details={"path": str(target)}
            )
        return cls.from_dict(raw, source="registry_file")

    # ── 查询面 ──

    @property
    def default_version(self) -> str:
        return self._default_version

    @property
    def source(self) -> str:
        return self._source

    def kinds(self) -> list[str]:
        return sorted(self._templates)

    def versions(self, kind: str) -> list[str]:
        if kind not in self._templates:
            raise ReviewTemplateRegistryError(
                f"未知模板 kind: {kind}", details={"kind": str(kind)}
            )
        return sorted(self._templates[kind])

    def get(self, kind: str, version: str | None = None) -> TemplateSpec:
        """取模板（版本可切换；缺失版本→默认版本回退+notes）。

        Raises:
            ReviewTemplateRegistryError: 未知 kind（调用方 bug，fail-closed）。
        """
        if kind not in self._templates:
            raise ReviewTemplateRegistryError(
                f"未知模板 kind: {kind}（已注册: {self.kinds()}）",
                details={"kind": str(kind)},
            )
        notes: list[str] = list(self._notes)
        resolved = version if version is not None else self._default_version
        if resolved not in self._templates[kind]:
            notes.append(f"模板版本 {resolved} 未注册（回退默认 {self._default_version}）")
            resolved = self._default_version
        return TemplateSpec(
            kind=kind,
            version=resolved,
            body=self._templates[kind][resolved],
            status=self._statuses[kind][resolved],
            source=self._source,
            notes=tuple(notes),
        )
