# [BLUEPRINT] MOD-INF-027 | scripts/governance/d11_compliance/validate_llm_security_gateway.py | §
# [MODULE] scripts.governance.d11_compliance.validate_llm_security_gateway
# [DOMAIN] D-GOVERNANCE
# [DEPENDENCIES] scripts.governance.d11_compliance.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
"""
validate_llm_security_gateway.py — 裸调 LLM API 检测门禁

对标：RULE-LSG-001 — 所有 LLM 调用必须经过 LSGSecurityGateway
      100% AI 开发场景下，AI 可能不知道 LSG 存在而直接裸调 LLM API
      本门禁在 pre-commit 阶段拦截，强制 AI 发现并使用 LSG

检测内容：
- 裸调 OpenAI API（client.chat.completions.create / openai.OpenAI）
- 裸调 Anthropic API（client.messages.create / anthropic.Anthropic）
- 裸调 LangChain（ChatOpenAI / ChatAnthropic）
- 裸调 litellm（litellm.completion）

豁免规则：
- 已导入 LSGSecurityGateway 的文件（已受保护）
- LSG 模块自身
- 测试文件（tests/ 目录）
- 豁免清单中的既有文件（待迁移后移除）

exit codes: 0=pass, 1=bare-llm-call-violation, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: [--ci, --warn-only]
description: 裸调 LLM API 检测——拦截绕过 LSG 的 LLM 调用
dimensions:
- D11
priority: P0
timeout_seconds: 30
warn_only: false
"""

import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

# ── 裸调 LLM API 方法签名 ──
_BARE_LLM_METHODS = {
    # OpenAI: client.chat.completions.create(...)
    "chat.completions.create",
    # Anthropic: client.messages.create(...)
    "messages.create",
    # litellm: litellm.completion(...)
    "completion",
}

# ── 裸调 LLM 客户端创建（被视作"即将裸调"） ──
_BARE_LLM_CLIENTS = {
    "OpenAI",           # openai.OpenAI()
    "AsyncOpenAI",      # openai.AsyncOpenAI()
    "Anthropic",        # anthropic.Anthropic()
    "AsyncAnthropic",   # anthropic.AsyncAnthropic()
    "ChatOpenAI",       # langchain.chat_models.ChatOpenAI()
    "ChatAnthropic",    # langchain.chat_models.ChatAnthropic()
}

# ── LSG 导入标识 ──
_LSG_IMPORT_PATTERNS = (
    "LSGSecurityGateway",
    "llm_security.gateway",
    "llm_security_01",
)

# ── 存量豁免清单（待迁移后移除）──
# 这些文件存在裸调但已有迁移计划，暂不阻断
_EXEMPTED_FILES = {
    # model_profiling 系列 — 模型评测基础设施，非业务 LLM 调用
    "src\\zephyr\\intelligence\\model_profiling\\",
    "src\\zephyr\\integration\\model_profiler\\",
    "src\\zephyr\\infrastructure\\pipeline\\model_profiler\\",
    "src\\zephyr\\infrastructure\\model_profiler\\",
}


def _has_lsg_import(tree: ast.AST) -> bool:
    """检查 AST 是否已导入 LSG 模块（含 importlib.import_module 动态导入）."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if any(pat in alias.name for pat in _LSG_IMPORT_PATTERNS):
                    return True
        elif isinstance(node, ast.ImportFrom):
            if node.module and any(pat in node.module for pat in _LSG_IMPORT_PATTERNS):
                return True
        elif isinstance(node, ast.Call):
            # 检测 importlib.import_module("...llm_security...") 动态导入
            if isinstance(node.func, ast.Attribute):
                if node.func.attr == "import_module":
                    if node.args and isinstance(node.args[0], ast.Constant):
                        if any(pat in node.args[0].value for pat in _LSG_IMPORT_PATTERNS):
                            return True
    return False


def _find_bare_llm_calls(tree: ast.AST) -> list[tuple[int, str]]:
    """在 AST 中查找裸调 LLM API 的位置，返回 [(行号, 描述), ...]."""
    violations: list[tuple[int, str]] = []

    for node in ast.walk(tree):
        # 1. 检测裸调 LLM 方法：xxx.chat.completions.create(...) / xxx.messages.create(...)
        if isinstance(node, ast.Call):
            # 链式调用: a.b.c.d(...)
            chain = []
            cur = node.func
            while isinstance(cur, ast.Attribute):
                chain.append(cur.attr)
                cur = cur.value
            if isinstance(cur, ast.Name):
                chain.append(cur.id)
            # 匹配 2 级后缀: xxx.chat.completions.create → ["create", "completions", "chat", "xxx"]
            if len(chain) >= 3:
                suffix3 = ".".join(reversed(chain[:3]))  # e.g. "chat.completions.create"
                if suffix3 in _BARE_LLM_METHODS:
                    violations.append((node.lineno, f"裸调 {suffix3}()"))
                    continue
                suffix2 = ".".join(reversed(chain[:2]))  # e.g. "messages.create"
                if suffix2 in _BARE_LLM_METHODS:
                    violations.append((node.lineno, f"裸调 {suffix2}()"))
                    continue

            # 2. 检测客户端创建: openai.OpenAI() / anthropic.Anthropic() / ChatOpenAI()
            if isinstance(node.func, ast.Name):
                if node.func.id in _BARE_LLM_CLIENTS:
                    violations.append((node.lineno, f"裸调 {node.func.id}() 客户端创建"))
                    continue
            elif isinstance(node.func, ast.Attribute):
                if node.func.attr in _BARE_LLM_CLIENTS:
                    violations.append((node.lineno, f"裸调 {node.func.attr}() 客户端创建"))
                    continue

            # 3. 检测 litellm.completion() / litellm.acompletion()
            if isinstance(node.func, ast.Attribute):
                if node.func.attr in ("completion", "acompletion"):
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == "litellm":
                        violations.append((node.lineno, f"裸调 litellm.{node.func.attr}()"))
                        continue

    return violations


def _is_exempted(file_path: Path) -> bool:
    """检查文件是否在豁免清单中."""
    rel = str(file_path.relative_to(REPO_ROOT))
    for prefix in _EXEMPTED_FILES:
        if rel.startswith(prefix):
            return True
    return False


def _is_lsg_module(file_path: Path) -> bool:
    """检查是否为 LSG 模块自身."""
    rel = str(file_path.relative_to(REPO_ROOT))
    return "llm_security" in rel and "test" not in rel


def _is_test_file(file_path: Path) -> bool:
    """检查是否为测试文件."""
    rel = str(file_path.relative_to(REPO_ROOT))
    return rel.startswith("tests") or rel.startswith("tests\\")


def scan_file(file_path: Path) -> list[str]:
    """扫描单个 Python 文件，返回违规描述列表."""
    if not file_path.suffix == ".py":
        return []
    if _is_test_file(file_path):
        return []
    if _is_lsg_module(file_path):
        return []
    if _is_exempted(file_path):
        return []

    try:
        source = file_path.read_text(encoding="utf-8")
    except Exception:
        return []

    try:
        tree = ast.parse(source, filename=str(file_path))
    except SyntaxError:
        return []

    # 已导入 LSG → 放行
    if _has_lsg_import(tree):
        return []

    # 查找裸调
    violations = _find_bare_llm_calls(tree)
    rel = file_path.relative_to(REPO_ROOT)
    return [f"{rel}:{lineno}: {desc}" for lineno, desc in violations]


def scan_all(warn_only: bool = False) -> tuple[int, list[str]]:
    """扫描 src/zephyr/ 下所有 Python 文件，返回 (exit_code, violations).

    exit_code: 0=pass, 1=violations found
    """
    all_violations: list[str] = []
    src_dir = REPO_ROOT / "src" / "zephyr"

    if not src_dir.exists():
        print(f"ERROR: src/zephyr/ not found at {src_dir}", file=sys.stderr)
        return 2, []

    for py_file in sorted(src_dir.rglob("*.py")):
        violations = scan_file(py_file)
        all_violations.extend(violations)

    if all_violations:
        level = "WARNING" if warn_only else "ERROR"
        print(f"[{level}] 发现 {len(all_violations)} 处裸调 LLM API（未经过 LSGSecurityGateway）：")
        for v in all_violations:
            print(f"  {v}")
        print()
        print("修复方式：将 LLM 调用替换为通过 LSGSecurityGateway 的 scan_input/scan_output 包裹。")
        print("  参考：src/zephyr/autonomy_core/llm_gateway.py 中的 _lsg_scan_input_sync / _lsg_scan_output_sync 模式")
        return 0 if warn_only else 1, all_violations
    else:
        print("PASS: 所有 LLM 调用均已通过 LSGSecurityGateway 保护")
        return 0, []


def main() -> int:
    """入口."""
    warn_only = "--warn-only" in sys.argv
    ci = "--ci" in sys.argv

    if "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: python validate_llm_security_gateway.py [--ci] [--warn-only]")
        print()
        print("  --ci         硬阻断模式（默认），发现裸调 exit(1)")
        print("  --warn-only  仅警告，不阻断（骨架阶段）")
        print()
        print("检测所有 src/zephyr/**/*.py 中的裸调 LLM API 调用。")
        print("裸调 = 未导入 LSGSecurityGateway 的文件中直接调用 openai/anthropic/langchain API。")
        return 0

    exit_code, violations = scan_all(warn_only=warn_only)
    if violations and not (warn_only or ci):
        # 默认 CI 模式
        return 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())