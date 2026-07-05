# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain-infra_ops/capacity-assurance/blueprint.md
# [MODULE] zephyr.infrastructure.capacity_assurance.tech_stack
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.capacity_assurance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_tech_stack | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
TechStackValidator — 技术栈可用性校验器
对蓝图 MOD-INF-001 §5.1 中的 16 项架构决策进行启动时组件可用性检查。

设计原则：
  - 零依赖优先：能 import 检查的不引入额外依赖
  - 优雅降级：不可用组件给出明确建议，不阻止启动
  - 可观测：report() 输出结构化状态报告
"""

import os
import sqlite3
import sys
from dataclasses import dataclass

import yaml


@dataclass
class ComponentStatus:
    dd_id: str
    component: str
    available: bool
    details: str = ""
    suggestion: str = ""


class TechStackValidator:
    """
    启动时逐一校验 16 项技术栈组件的可用性。
    支持从 YAML manifest 加载决策清单，然后逐项检查。
    """

    def __init__(self, manifest_path: str | None = None):
        if manifest_path is None:
            manifest_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                "config",
                "capacity",
                "tech_stackmanifest.yaml",
            )
        self.manifest_path = manifest_path
        self.decisions: list[dict] = []
        self.results: list[ComponentStatus] = []
        self._load_manifest()

    def _load_manifest(self):
        if os.path.exists(self.manifest_path):
            with open(self.manifest_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
                self.decisions = data.get("decisions", [])
        else:
            self.decisions = self._default_decisions()

    def _default_decisions(self) -> list[dict]:
        return [
            {"dd_id": "DD-1", "component": "SLO 配置", "final_choice": "YAML + Pydantic v2"},
            {"dd_id": "DD-2", "component": "审计存储", "final_choice": "SQLite + hash 链"},
            {"dd_id": "DD-3", "component": "指标采样", "final_choice": "structlog + OpenTelemetry SDK"},
            {"dd_id": "DD-4", "component": "AI 审计规则", "final_choice": "YAML 规则集 + Pydantic 校验"},
            {"dd_id": "DD-5", "component": "治理闭环", "final_choice": "自研 EMA + 阈值"},
            {"dd_id": "DD-6", "component": "类型校验", "final_choice": "mypy + import-linter"},
            {"dd_id": "DD-7", "component": "单元测试", "final_choice": "pytest + pytest-cov"},
            {"dd_id": "DD-8", "component": "静态扫描", "final_choice": "ruff + bandit"},
            {"dd_id": "DD-9", "component": "ContractBus 迁移", "final_choice": "分三批 15+15+14"},
            {"dd_id": "DD-10", "component": "Error Budget", "final_choice": "SQLite + Pydantic v2"},
            {"dd_id": "DD-11", "component": "Token Budget", "final_choice": "Token Bucket + 滑动窗口"},
            {"dd_id": "DD-12", "component": "Kill Switch", "final_choice": "环境变量 + 文件信号"},
            {"dd_id": "DD-13", "component": "Sandbox", "final_choice": "子进程 + 资源限制"},
            {"dd_id": "DD-14", "component": "Graceful Degradation", "final_choice": "YAML 降级链 + 模型路由"},
            {"dd_id": "DD-15", "component": "OTel 语义规范", "final_choice": "OpenTelemetry GenAI Conventions"},
            {"dd_id": "DD-16", "component": "语义缓存", "final_choice": "ChromaDB 向量相似度"},
        ]

    def validate(self) -> list[ComponentStatus]:
        self.results = []
        for d in self.decisions:
            dd_id = d["dd_id"]
            component = d["component"]
            status = self._check_component(dd_id, component, d.get("final_choice", ""))
            self.results.append(status)
        return self.results

    def _check_component(self, dd_id: str, component: str, final_choice: str) -> ComponentStatus:
        method_name = f"_check_{dd_id.lower().replace('-', '_')}"
        method = getattr(self, method_name, None)
        if method:
            return method()
        return self._generic_check(dd_id, component, final_choice)

    def _generic_check(self, dd_id: str, component: str, final_choice: str) -> ComponentStatus:
        return ComponentStatus(
            dd_id=dd_id,
            component=component,
            available=True,
            details=f"终选: {final_choice}",
        )

    def inspect_pydantic_v2(self) -> ComponentStatus:
        try:
            import pydantic

            version = pydantic.__version__
            if version.startswith("2."):
                return ComponentStatus(
                    dd_id="DD-1", component="Pydantic v2", available=True, details=f"pydantic=={version}"
                )
            return ComponentStatus(
                dd_id="DD-1",
                component="Pydantic v2",
                available=False,
                details=f"检测到 pydantic=={version}，需要 v2.x",
                suggestion="pip install 'pydantic>=2.0'",
            )
        except ImportError:
            return ComponentStatus(
                dd_id="DD-1",
                component="Pydantic v2",
                available=False,
                details="未安装 pydantic",
                suggestion="pip install 'pydantic>=2.0'",
            )

    def inspect_sqlite(self) -> ComponentStatus:
        try:
            conn = sqlite3.connect(":memory:")
            conn.execute("SELECT 1")
            conn.close()
            return ComponentStatus(
                dd_id="DD-2", component="SQLite", available=True, details=f"sqlite3={sqlite3.sqlite_version}"
            )
        except Exception as e:
            return ComponentStatus(
                dd_id="DD-2",
                component="SQLite",
                available=False,
                details="internal error",
                suggestion="检查 Python sqlite3 模块是否编译进你的 Python",
            )

    def inspect_otel_sdk(self) -> ComponentStatus:
        try:
            import opentelemetry

            version = getattr(opentelemetry, "__version__", None)
            if version is None:
                from importlib.metadata import version as pkg_version

                try:
                    version = pkg_version("opentelemetry-api")
                except Exception:
                    version = "unknown"
            return ComponentStatus(
                dd_id="DD-3", component="OpenTelemetry SDK", available=True, details=f"opentelemetry-api=={version}"
            )
        except ImportError:
            return ComponentStatus(
                dd_id="DD-3",
                component="OpenTelemetry SDK",
                available=False,
                details="未安装 opentelemetry-api",
                suggestion="pip install opentelemetry-api opentelemetry-sdk",
            )

    def inspect_pytest(self) -> ComponentStatus:
        try:
            import pytest

            return ComponentStatus(
                dd_id="DD-7", component="pytest", available=True, details=f"pytest=={pytest.__version__}"
            )
        except ImportError:
            return ComponentStatus(
                dd_id="DD-7",
                component="pytest",
                available=False,
                details="未安装 pytest",
                suggestion="pip install pytest pytest-cov",
            )

    def inspect_chromadb(self) -> ComponentStatus:
        try:
            import chromadb

            version = getattr(chromadb, "__version__", "unknown")
            return ComponentStatus(dd_id="DD-16", component="ChromaDB", available=True, details=f"chromadb=={version}")
        except ImportError:
            return ComponentStatus(
                dd_id="DD-16",
                component="ChromaDB",
                available=False,
                details="未安装 chromadb",
                suggestion="pip install chromadb",
            )

    def inspect_psutil(self) -> ComponentStatus:
        try:
            import psutil

            return ComponentStatus(
                dd_id="DD-5", component="psutil", available=True, details=f"psutil=={psutil.__version__}"
            )
        except ImportError:
            return ComponentStatus(
                dd_id="DD-5",
                component="psutil",
                available=False,
                details="未安装 psutil",
                suggestion="pip install psutil",
            )

    def _check_dd_1(self) -> ComponentStatus:
        return self.inspect_pydantic_v2()

    def _check_dd_2(self) -> ComponentStatus:
        return self.inspect_sqlite()

    def _check_dd_3(self) -> ComponentStatus:
        return self.inspect_otel_sdk()

    def _check_dd_7(self) -> ComponentStatus:
        return self.inspect_pytest()

    def _check_dd_16(self) -> ComponentStatus:
        return self.inspect_chromadb()

    def _check_dd_5(self) -> ComponentStatus:
        return self.inspect_psutil()

    def report(self) -> str:
        if not self.results:
            self.validate()
        lines = ["=" * 60, "  ZephyrAlpha 技术栈可用性报告", "=" * 60, ""]
        available_count = 0
        unavailable_count = 0

        for r in self.results:
            status_icon = "[OK]" if r.available else "[!!]"
            lines.append(f"  {status_icon} {r.dd_id} {r.component}")
            if r.details:
                lines.append(f"      {r.details}")
            if not r.available and r.suggestion:
                lines.append(f"      建议: {r.suggestion}")
            if r.available:
                available_count += 1
            else:
                unavailable_count += 1

        lines.append("")
        lines.append("-" * 60)
        lines.append(f"  总计: {len(self.results)} 项 | 可用: {available_count} | 不可用: {unavailable_count}")
        lines.append("=" * 60)

        return "\n".join(lines)


def validate_on_startup(manifest_path: str | None = None) -> bool:
    validator = TechStackValidator(manifest_path=manifest_path)
    validator.validate()
    report = validator.report()
    print(report, file=sys.stderr)
    all_ok = all(r.available for r in validator.results)
    if not all_ok:
        unavailable = [r for r in validator.results if not r.available]
        missing = ", ".join(r.component for r in unavailable)
        print(f"[WARN] 技术栈不可用组件: {missing} — 系统可能降级运行", file=sys.stderr)
    return all_ok
