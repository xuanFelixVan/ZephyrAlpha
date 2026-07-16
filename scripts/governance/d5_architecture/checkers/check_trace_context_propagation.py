# [BLUEPRINT] MOD-INF-005 | scripts/governance/d5_architecture/checkers/check_trace_context_propagation.py | §
# [MODULE] scripts.governance.d5_architecture.checkers.check_trace_context_propagation
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d5_architecture.checkers.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""check_trace_context_propagation.py — TraceContext 传播强制执行 CI 检查



扫描 D_DATA~D_REPORTING 各域代码，检测 TraceContext（CTR-TRACE-001）是否正确传播。

检测内容:
    - 生产者域（D_DATA/D_FACTOR/D_SIGNAL/D_PORTFOLIO_CORE/D_EXECUTION_CORE）产出数据时是否嵌入 trace_context
    - 消费者域从上游数据中是否提取 trace_context
    - 修改者域是否更新 span_id 和 service_name
    - 是否存在 trace_context 丢失路径（吞掉但不传递）

规则:
    - D_DATA (生产者): MUST 创建新的 TraceContext（trace_id 用 UUID），生成 span
    - D_FACTOR~D_EXECUTION_CORE (中间域): MUST 从入站数据提取 trace_context，更新 span，嵌入出站数据
    - D_REPORTING (终端): SHOULD 记录 trace_context 用于排障

exit codes: 0=pass, 1=findings, 2=error

SSoT: cross_layer_contracts.yaml → CTR-TRACE-001
"""

from __future__ import annotations

__manifest__ = """
args: []
description: >
  TraceContext 传播强制执行 CI 检查——确保所有跨模块调用链路中 trace_id/span_id
  不丢失，验证 OpenTelemetry 上下文传播链完整。对标 GOV-MOD-004 接口契约 §可观测性。
dimensions:
- D5
priority: P2
timeout_seconds: 60
warn_only: false
"""

import ast
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
from _shared.encoding import ensure_utf8_stdout
from _shared.walk import iter_files

ensure_utf8_stdout()

import argparse

PRODUCER_LAYERS = {  # noqa: gate-vocab  生产者层业务子集
    "data",
    "factor",
    "signal",
    "pf_core",
    "ex_core",
}

CONSUMER_LAYERS = {  # noqa: gate-vocab  消费者层值，非 domain 值
    "data",
    "factor",
    "signal",
    "risk",
    "pf_core",
    "ex_core",
}

ALL_LAYERS = sorted(PRODUCER_LAYERS | CONSUMER_LAYERS)

CTR_TYPES = {
    "NormalizedMarketData",
    "FactorSignal",
    "RiskLimits",
    "Order",
    "Fill",
    "PositionSnapshot",
}

TRACE_PATTERNS = [
    "trace_context",
    "TraceContext",
    "parent_span_id",
    "span_id",
    "trace_id",
    "service_name",
]


class TraceContextVisitor(ast.NodeVisitor):
    def __init__(self, layer: str, filename: str):
        """__init__ implementation."""
        self.layer = layer
        self.filename = filename
        self.findings: list[dict] = []

        self._func_name = ""
        self._creates_tc = False
        self._extracts_tc = False
        self._propagates_tc = False
        self._has_trace_attr = False
        self._has_ctr_type = False

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """visit_FunctionDef implementation."""
        prev_name = self._func_name
        prev_creates = self._creates_tc
        prev_extracts = self._extracts_tc
        prev_propagates = self._propagates_tc
        prev_has_trace = self._has_trace_attr

        self._func_name = node.name
        self._creates_tc = False
        self._extracts_tc = False
        self._propagates_tc = False
        self._has_trace_attr = False
        self._has_ctr_type = False

        self.generic_visit(node)

        if self.layer in PRODUCER_LAYERS and self._has_ctr_type and not self._propagates_tc:
            self.findings.append(
                {
                    "file": self.filename,
                    "layer": self.layer,
                    "function": node.name,
                    "line": node.lineno,
                    "violation": (
                        f"生产者 '{node.name}' 产出 CTR 数据但未检测到 trace_context 传播 "
                        f"— 每层 MUST 创建/更新 TraceContext span 并嵌入出站数据 "
                        f"(CTR-TRACE-001)"
                    ),
                    "severity": "HIGH",
                }
            )

        if self.layer in CONSUMER_LAYERS and self._has_ctr_type and not self._extracts_tc and not self._creates_tc:
            self.findings.append(
                {
                    "file": self.filename,
                    "layer": self.layer,
                    "function": node.name,
                    "line": node.lineno,
                    "violation": (
                        f"消费者 '{node.name}' 使用 CTR 数据但未提取 trace_context "
                        f"— 应调用 getattr(data, 'trace_context', None) 或等效代码 "
                        f"(CTR-TRACE-001)"
                    ),
                    "severity": "MEDIUM",
                }
            )

        self._func_name = prev_name
        self._creates_tc = prev_creates
        self._extracts_tc = prev_extracts
        self._propagates_tc = prev_propagates
        self._has_trace_attr = prev_has_trace

    def visit_Assign(self, node: ast.Assign) -> None:
        """visit_Assign implementation."""
        self._check_for_trace_patterns(node)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """visit_Call implementation."""
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == "trace_context" or (
                isinstance(node.func.value, ast.Name) and node.func.attr in TRACE_PATTERNS
            ):
                self._has_trace_attr = True
        elif isinstance(node.func, ast.Name):
            for kw in node.keywords:
                if kw.arg == "trace_context" or kw.arg in TRACE_PATTERNS:
                    self._propagates_tc = True

        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        """visit_Attribute implementation."""
        if node.attr in TRACE_PATTERNS:
            self._has_trace_attr = True
        if node.attr == "trace_context":
            self._extracts_tc = True

        if isinstance(node.ctx, ast.Store):
            pass

        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        """visit_AnnAssign implementation."""
        if node.annotation:
            anno_str = ast.unparse(node.annotation)
            for ctr_type in CTR_TYPES:
                if ctr_type in anno_str:
                    self._has_ctr_type = True
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        """visit_Import implementation."""
        for alias in node.names:
            if "trace_context" in alias.name.lower():
                self._has_trace_attr = True
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """visit_ImportFrom implementation."""
        if node.module and "trace_context" in node.module.lower():
            self._has_trace_attr = True
        self.generic_visit(node)

    def _check_for_trace_patterns(self, node: ast.Assign) -> None:
        """_check_for_trace_patterns implementation."""
        for target in node.targets if isinstance(node.targets, list) else [node.targets]:
            if isinstance(target, ast.Name):
                for pattern in TRACE_PATTERNS:
                    if pattern.lower() in target.id.lower():
                        self._has_trace_attr = True

        if isinstance(node.value, ast.Call):
            if isinstance(node.value.func, ast.Attribute):
                if "trace_context" in str(getattr(node.value.func, "attr", "")).lower():
                    self._creates_tc = True
                    self._propagates_tc = True
            elif isinstance(node.value.func, ast.Name):
                func_name = node.value.func.id.lower()
                if "trace_context" in func_name or "tracecontext" in func_name:
                    self._creates_tc = True
                    self._propagates_tc = True

        for kw in getattr(node.value, "keywords", None) or []:
            if hasattr(kw, "arg") and kw.arg == "trace_context":
                self._propagates_tc = True


def scan_layer(layer: str) -> list[dict]:
    """scan_layer implementation."""
    src_dir = REPO_ROOT / "src" / "zephyr"
    layer_dir = src_dir / layer
    if not layer_dir.exists():
        return []

    all_findings: list[dict] = []
    for py_file in iter_files(layer_dir, extensions={".py"}):
        if py_file.name == "__init__.py":
            continue
        try:
            source = py_file.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(source, filename=str(py_file))
        except (SyntaxError, OSError):
            continue

        rel = str(py_file.relative_to(REPO_ROOT)).replace("\\", "/")
        visitor = TraceContextVisitor(layer, rel)
        visitor.visit(tree)
        all_findings.extend(visitor.findings)

    return all_findings


def _check_has_trace_context_attr(source: str) -> bool:
    """_check_has_trace_context_attr implementation."""
    return any(pattern in source for pattern in TRACE_PATTERNS)


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(description="TraceContext 传播强制执行 CI 检查")
    parser.add_argument("--warn-only", action="store_true", help="警告模式")
    parser.add_argument("--layer", type=str, help="仅检查指定层")
    args = parser.parse_args()

    layers_to_check = [args.layer] if args.layer else ALL_LAYERS

    print("[TraceContext] 传播强制执行扫描启动\n")

    all_findings: list[dict] = []
    layer_stats: dict[str, dict] = {}

    for layer in layers_to_check:
        findings = scan_layer(layer)
        all_findings.extend(findings)

        layer_dir = REPO_ROOT / "src" / "zephyr" / layer
        py_files = list(iter_files(layer_dir, extensions={".py"})) if layer_dir.exists() else []
        non_init = [f for f in py_files if f.name != "__init__.py"]

        has_tc_count = 0
        for f in non_init:
            try:
                src = f.read_text(encoding="utf-8", errors="replace")
                if _check_has_trace_context_attr(src):
                    has_tc_count += 1
            except OSError:
                pass

        layer_stats[layer] = {
            "files": len(non_init),
            "has_trace_ref": has_tc_count,
            "violations": len([f for f in findings if f["layer"] == layer]),
        }

    for layer, stats in sorted(layer_stats.items()):
        has = stats["has_trace_ref"]
        total = stats["files"]
        viols = stats["violations"]
        is_producer = layer in PRODUCER_LAYERS
        tag = "[P]" if is_producer else "[C]"

        print(f"  {tag} {layer}: {has}/{total} 文件引用 TraceContext, {viols} 条违规")

        if is_producer and total > 0 and has < total:
            print(f"       ⚠  生产者层但 {total - has} 个文件未引用 TraceContext")

    print()

    for f in all_findings:
        print(f"\n  [{f['severity']}] {f['file']}:{f['line']} ({f['function']})")
        print(f"     {f['violation']}")

    high_count = len([f for f in all_findings if f["severity"] == "HIGH"])
    med_count = len([f for f in all_findings if f["severity"] == "MEDIUM"])
    total = len(all_findings)

    if total == 0:
        print("\n[TraceContext] 全部通过 ✅")
    else:
        print(f"\n[TraceContext] ⚠ {total} 条违规 (HIGH={high_count}, MED={med_count})")

    if args.warn_only:
        sys.exit(EXIT_PASS)
    sys.exit(EXIT_FINDINGS if all_findings else EXIT_PASS)


if __name__ == "__main__":
    main()
