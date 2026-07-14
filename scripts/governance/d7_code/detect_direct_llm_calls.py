# [BLUEPRINT] MOD-INF-005 | scripts/governance/d7_code/detect_direct_llm_calls.py | §
# [MODULE] scripts.governance.d7_code.detect_direct_llm_calls
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.d7_code.__init__
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
# [TTL] task_bound
"""
detect_direct_llm_calls.py — 裸调 LLM API 检测门禁（GATE-20）

对标：
  - COND-30 — D_FACTOR-D_REPORTING 禁止直接 import LLM SDK（存量检测）
  - RULE-LSG-001 — 所有 LLM 调用必须经过 LSGSecurityGateway（强制门禁）

检测内容：
  - 裸调 LLM API 调用（chat.completions.create / messages.create / litellm.completion）
  - 裸调 LLM 客户端创建（openai.OpenAI / anthropic.Anthropic / ChatOpenAI / ChatAnthropic）
  - exec/eval/compile 字符串参数包裹的裸调 LLM API
  - 字符串常量中含裸调 LLM API（疑似变量赋值后 exec）
  - 传统 COND-30 检测：D_FACTOR-D_REPORTING 层直接 import LLM SDK

豁免规则：
  - 已导入 LSGSecurityGateway / llm_security 的文件（已受保护）
  - LSG 模块自身
  - 测试文件（tests/ 目录）
  - model_profiling 基础设施（待迁移后移除）

exit codes: 0=pass, 1=findings, 2=error
"""

from __future__ import annotations

__manifest__ = """
args: [--ci, --warn-only]
description: 裸调 LLM API 检测门禁——拦截绕过 LSG 的 LLM 调用（RULE-LSG-001）+ COND-30 导入检测
dimensions:
- D7
- D11
priority: P0
timeout_seconds: 30
warn_only: false
"""

import ast
import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.constants import EXIT_PASS, REPO_ROOT, SCAN_EXTENSIONS_PY
from _shared.encoding import ensure_utf8_stdout
from _shared.walk import iter_files

ensure_utf8_stdout()
import argparse

# ── LLM SDK 导入检测（COND-30 存量） ──
_LLM_IMPORTS = {
    "openai",
    "anthropic",
    "langchain",
    "cohere",
    "huggingface_hub",
    "transformers",
    "tiktoken",
    "replicate",
    "together",
    "groq",
}

# ── 裸调 LLM 方法签名（用于 exec/eval 字符串扫描 + API 调用检测） ──
_BARE_LLM_SIGNATURES = [
    "chat.completions.create",
    "messages.create",
    "litellm.completion",
    "litellm.acompletion",
    "openai.OpenAI",
    "openai.AsyncOpenAI",
    "anthropic.Anthropic",
    "anthropic.AsyncAnthropic",
    "ChatOpenAI",
    "ChatAnthropic",
]

# ── 裸调 LLM 客户端创建（被视作"即将裸调"） ──
_BARE_LLM_CLIENTS = {
    "OpenAI",
    "AsyncOpenAI",
    "Anthropic",
    "AsyncAnthropic",
    "ChatOpenAI",
    "ChatAnthropic",
}

# ── LSG 导入标识 ──
_LSG_IMPORT_PATTERNS = (
    "LSGSecurityGateway",
    "llm_security.gateway",
)

# ── 存量豁免清单（待迁移后移除）──
_EXEMPTED_FILES = {
    "src\\zephyr\\intelligence\\model_profiling\\",
    "src\\zephyr\\integration\\model_profiler\\",
    "src\\zephyr\\infrastructure\\pipeline\\model_profiler\\",
    "src\\zephyr\\infrastructure\\model_profiler\\",
}

# ── COND-30 业务层判定 ──
_LAYER_PATTERN = re.compile(r"l(0[2-9]|[1-3]\d)_", re.IGNORECASE)
_B_TRACK_DIRS = {
    "llm-security", "vector-memory", "context-engine", "orchestrator",
    "feedback-loop", "gates", "db", "kb", "mcp", "shared",
}


# ============================================================================
# 辅助函数
# ============================================================================

def _is_business_layer(filepath: Path, src_dir: Path) -> bool:
    """判断是否为业务层（COND-30 范围）."""
    try:
        rel = filepath.relative_to(src_dir)
        parts = rel.parts
    except ValueError:
        return False
    if not parts:
        return False
    first = parts[0]
    if _LAYER_PATTERN.match(first):
        return True
    return first in _B_TRACK_DIRS


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


def _get_string_value(node: ast.expr) -> str | None:
    """安全提取 AST 节点的字符串值（支持常量 + 简单拼接）."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = _get_string_value(node.left)
        right = _get_string_value(node.right)
        if left is not None and right is not None:
            return left + right
    return None


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
            if isinstance(node.func, ast.Attribute) and node.func.attr == "import_module":
                if node.args and isinstance(node.args[0], ast.Constant):
                    if any(pat in node.args[0].value for pat in _LSG_IMPORT_PATTERNS):
                        return True
    return False


# ============================================================================
# 检测引擎
# ============================================================================

def _find_bare_llm_calls(tree: ast.AST) -> list[tuple[int, str]]:
    """在 AST 中查找裸调 LLM API 的位置，返回 [(行号, 描述), ...]."""
    violations: list[tuple[int, str]] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # 1. 链式调用检测: xxx.chat.completions.create(...) / xxx.messages.create(...)
            chain = []
            cur = node.func
            while isinstance(cur, ast.Attribute):
                chain.append(cur.attr)
                cur = cur.value
            if isinstance(cur, ast.Name):
                chain.append(cur.id)
            if len(chain) >= 3:
                suffix3 = ".".join(reversed(chain[:3]))
                if suffix3 in ("chat.completions.create", "messages.create"):
                    violations.append((node.lineno, f"裸调 {suffix3}()"))
                    continue
            if len(chain) >= 2:
                suffix2 = ".".join(reversed(chain[:2]))
                if suffix2 == "messages.create":
                    violations.append((node.lineno, f"裸调 {suffix2}()"))
                    continue

            # 2. 客户端创建检测: openai.OpenAI() / anthropic.Anthropic() / ChatOpenAI()
            if isinstance(node.func, ast.Name):
                if node.func.id in _BARE_LLM_CLIENTS:
                    violations.append((node.lineno, f"裸调 {node.func.id}() 客户端创建"))
                    continue
            elif isinstance(node.func, ast.Attribute):
                if node.func.attr in _BARE_LLM_CLIENTS:
                    violations.append((node.lineno, f"裸调 {node.func.attr}() 客户端创建"))
                    continue

            # 3. litellm.completion() / litellm.acompletion()
            if isinstance(node.func, ast.Attribute):
                if node.func.attr in ("completion", "acompletion"):
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == "litellm":
                        violations.append((node.lineno, f"裸调 litellm.{node.func.attr}()"))
                        continue

            # 4. exec/eval/compile 字符串参数中的裸调 LLM API
            if isinstance(node.func, ast.Name) and node.func.id in ("exec", "eval", "compile"):
                if node.args:
                    first_arg = node.args[0]
                    arg_str = _get_string_value(first_arg)
                    if arg_str:
                        for sig in _BARE_LLM_SIGNATURES:
                            if sig in arg_str:
                                violations.append(
                                    (node.lineno,
                                     f"exec/eval/compile 包裹裸调 LLM API（检测到 {sig}）")
                                )
                                break
                continue

        # 5. 全局扫描：任何字符串常量中含裸调 LLM API → 疑似 exec 变量赋值
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            s = node.value
            for sig in _BARE_LLM_SIGNATURES:
                if sig in s:
                    violations.append(
                        (node.lineno,
                         f"字符串常量含裸调 LLM API（检测到 {sig}）——疑似 exec/eval 变量赋值")
                    )
                    break

    return violations


def _check_llm_imports(filepath: Path) -> list[dict]:
    """检查 LLM 直接 import（COND-30 存量检测）."""
    findings = []
    try:
        source = filepath.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(filepath))
    except (SyntaxError, OSError, UnicodeDecodeError):
        return findings
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root_module = alias.name.split(".")[0]
                if root_module in _LLM_IMPORTS:
                    findings.append({"line": node.lineno, "import_name": alias.name})
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root_module = node.module.split(".")[0]
                if root_module in _LLM_IMPORTS:
                    findings.append({"line": node.lineno, "import_name": f"from {node.module}"})
    return findings


# ============================================================================
# 扫描入口
# ============================================================================

def scan_file(file_path: Path) -> list[str]:
    """扫描单个 Python 文件（RULE-LSG-001 门禁），返回违规描述列表."""
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

    violations = _find_bare_llm_calls(tree)
    rel = file_path.relative_to(REPO_ROOT)
    return [f"{rel}:{lineno}: {desc}" for lineno, desc in violations]


def scan_all(warn_only: bool = False) -> tuple[int, list[str]]:
    """扫描 src/zephyr/ 下所有 Python 文件（RULE-LSG-001 全量），返回 (exit_code, violations)."""
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
        print(f"[{level}] 发现 {len(all_violations)} 处裸调 LLM API（未经过 LSGSecurityGateway）：", file=sys.stderr)
        for v in all_violations:
            print(f"  {v}", file=sys.stderr)
        print(file=sys.stderr)
        print("修复方式：将 LLM 调用替换为通过 LSGSecurityGateway 的 scan_input/scan_output 包裹。", file=sys.stderr)
        print("  参考：src/zephyr/autonomy_core/llm_gateway.py 中的 _lsg_scan_input_sync / _lsg_scan_output_sync 模式", file=sys.stderr)
        return 0 if warn_only else 1, all_violations
    else:
        print("PASS: 所有 LLM 调用均已通过 LSGSecurityGateway 保护", file=sys.stderr)
        return 0, []


# ============================================================================
# 入口
# ============================================================================

def main() -> int:
    parser = argparse.ArgumentParser(
        description="裸调 LLM API 检测门禁（GATE-20：RULE-LSG-001 + COND-30）"
    )
    parser.add_argument("--ci", action="store_true", help="硬阻断模式（pre-commit），发现裸调 exit(1)")
    parser.add_argument("--warn-only", action="store_true", help="仅警告，不阻断")
    parser.add_argument("--cond30", action="store_true", help="仅运行 COND-30 导入检测（存量模式）")
    args = parser.parse_args()

    # COND-30 模式：仅检测业务层 LLM SDK 导入
    if args.cond30:
        src_dir = REPO_ROOT / "src" / "zephyr"
        if not src_dir.exists():
            print("[LLM-CALL] src/zephyr/ 不存在，跳过", file=sys.stderr)
            return EXIT_PASS
        all_findings = []
        for filepath in iter_files(src_dir, extensions=SCAN_EXTENSIONS_PY):
            if not _is_business_layer(filepath, src_dir):
                continue
            findings = _check_llm_imports(filepath)
            for f in findings:
                rel = str(filepath.relative_to(REPO_ROOT)).replace("\\", "/")
                all_findings.append({"file": rel, "line": f["line"], "import_name": f["import_name"], "severity": "HIGH"})
        if all_findings:
            print(f"\n[LLM-CALL] {len(all_findings)} 个业务层直接 LLM 调用:", file=sys.stderr)
            for f in all_findings:
                print(f"  [{f['severity']}] {f['file']}:{f['line']}", file=sys.stderr)
                print(f"    {f['import_name']}", file=sys.stderr)
        else:
            print("[LLM-CALL] 业务层无直接 LLM 调用", file=sys.stderr)
        return EXIT_PASS if (args.warn_only or not all_findings) else 1

    # RULE-LSG-001 模式：全量 API 调用检测
    exit_code, violations = scan_all(warn_only=args.warn_only)
    if violations and not (args.warn_only or args.ci):
        return 1
    return exit_code


if __name__ == "__main__":
    sys.exit(main())