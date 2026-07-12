# [A_test] module_id: SRC-TST-0065 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-223 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.architecture.test_money_and_docs
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
架构适应度函数：金融精度强制 + 文档完整性
============================================

架构不变式
----------
- LF04: 层源码中金额相关变量/注解不使用 float（必须 Decimal）
- LF05: 所有模块 .py 文件有完整的 frontmatter（layer/category/status/created）

Safety: HIGH（金融精度是不可协商的安全约束）
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest
from zephyr.shared.io.paths import REPO_ROOT

MONEY_PATTERNS = [
    "price",
    "amount",
    "cost",
    "fee",
    "commission",
    "quantity",
    "volume",
    "value",
    "notional",
    "market_value",
    "nav",
    "cash",
    "balance",
    "equity",
    "open",
    "high",
    "low",
    "close",
    "limit_price",
    "fill_price",
    "avg_price",
    "entry_price",
    "exit_price",
]

SRC_DIR = REPO_ROOT / "src" / "zephyr"

LAYER_ORDER = [
    "l00-data-source",
    "l01-infrastructure",
    "l02-alpha-factor",
    "l03-signal-generation",
    "l04-risk-management",
    "l05-portfolio-construction",
    "l06-trade-execution",
    "l07-post-trade-analytics",
]


def _is_money_name(name: str) -> bool:
    lower = name.lower()
    return any(p in lower for p in MONEY_PATTERNS)


def _annotation_is_float(node: ast.expr) -> bool:
    if isinstance(node, ast.Name) and node.id == "float":
        return True
    if isinstance(node, ast.Subscript):
        v = node.value
        if isinstance(v, ast.Name) and v.id == "float":
            return True
    if isinstance(node, ast.Attribute) and node.attr == "float":
        return True
    return False


class TestNoFloatInMoneyPaths:
    """LF04: 金额相关路径不允许 float。"""

    def test_layer_source_no_float_annotations(self):
        violations: list[str] = []
        for layer_name in LAYER_ORDER:
            layer_dir = SRC_DIR / layer_name
            if not layer_dir.exists():
                continue
            for py_file in layer_dir.rglob("*.py"):
                if not py_file.is_file():
                    continue
                source = py_file.read_text(encoding="utf-8", errors="replace")
                try:
                    tree = ast.parse(source, filename=str(py_file))
                except SyntaxError:
                    continue

                for node in ast.walk(tree):
                    if isinstance(node, ast.AnnAssign) and node.annotation:
                        name = None
                        if isinstance(node.target, ast.Name):
                            name = node.target.id
                        elif isinstance(node.target, ast.Attribute):
                            name = node.target.attr
                        if name and _is_money_name(name) and _annotation_is_float(node.annotation):
                            rel = py_file.relative_to(REPO_ROOT)
                            violations.append(f"{rel}:{node.lineno} — '{name}' 使用了 float 注解，必须用 Decimal")

        if violations:
            pytest.fail(f"检测到 {len(violations)} 处 float 违规:\n" + "\n".join(f"  - {v}" for v in violations[:20]))


class TestDocumentFrontmatterCompleteness:
    """LF05: 模块文件有完整的 frontmatter 元数据。"""

    REQUIRED_FRONTMATTER_KEYS = {"layer", "category", "status", "created"}

    def test_all_module_py_files_have_frontmatter(self):
        violations: list[str] = []
        for layer_name in LAYER_ORDER:
            layer_dir = SRC_DIR / layer_name
            if not layer_dir.exists():
                continue
            for py_file in layer_dir.rglob("*.py"):
                if not py_file.is_file():
                    continue
                if py_file.name == "__init__.py":
                    continue

                source = py_file.read_text(encoding="utf-8", errors="replace")
                if not source.strip():
                    violations.append(f"{py_file.relative_to(REPO_ROOT)}: 空文件")
                    continue

                found_keys = set()
                in_frontmatter = False
                for line in source.split("\n")[:30]:
                    line = line.strip()
                    if line == "# ---":
                        if not in_frontmatter:
                            in_frontmatter = True
                            continue
                        else:
                            break
                    if in_frontmatter and line.startswith("# ") and ":" in line:
                        content = line[2:]
                        if ":" in content:
                            key = content.split(":")[0].strip()
                            found_keys.add(key)

                if not in_frontmatter:
                    violations.append(f"{py_file.relative_to(REPO_ROOT)}: 缺少 YAML frontmatter (# ---)")
                else:
                    missing = self.REQUIRED_FRONTMATTER_KEYS - found_keys
                    if missing:
                        violations.append(f"{py_file.relative_to(REPO_ROOT)}: 缺少 frontmatter 字段: {missing}")

        if violations:
            pytest.fail(
                f"检测到 {len(violations)} 处 frontmatter 问题:\n" + "\n".join(f"  - {v}" for v in violations[:20])
            )
