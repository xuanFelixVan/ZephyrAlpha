# [BLUEPRINT] MOD-INF-005 | scripts/governance/scan_exception_debt.py | §one-shot-scan
# [MODULE] scripts.governance.scan_exception_debt
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__; zephyr.gov_enforcement.commit_gates.msg_exposure_gate
# [CONSUMERS] Phase 2 阶段0治标清零——生成5.135/5.168违规清单
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 一次性全量扫描脚本——扫描src/zephyr/**/*.py（排除tests/）的5.135异常粒度过粗+5.168异常信息泄露违规；5.168复用msg_exposure_gate._detect_msg_exposure()；5.135用AST扫描except Exception/BaseException/bare except；noqa注释行豁免；门禁文件governance/commit_gates/自豁免（与MSG-EXPOSURE gate一致）
# [MODIFY-GUARD] none（TTL=task_bound 一次性脚本，完成后退役删除）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] EXIT_PASS=0（始终）；单文件AST解析失败跳过并记录warning
# [TESTS] none（TTL=task_bound 一次性扫描脚本，无单元测试需求）
# [TTL] task_bound
"""scan_exception_debt.py — 一次性扫描5.135异常粒度过粗 + 5.168异常信息泄露违规清单

Phase 2 阶段0治标清零的数据源生成器（architecture_debt_registry.md §6.4）。
文档明确"约40个未跟踪维度无法人工展开，尤其5.135异常粒度697项/5.168异常信息泄露142项"
（L4297），本脚本通过AST全量扫描生成可逐条修复的违规清单。

检测维度
--------
- **5.135 异常粒度过粗**：except Exception / except BaseException / bare except:
  捕获粒度过宽，违反"捕获具体异常"原则。带 ``# noqa`` 注释的行豁免（已显式声明降级理由）。
- **5.168 异常信息泄露**：raise XxxError(f"...{sensitive_var}...") 异常消息f-string
  中插值敏感变量（路径/tx_id/凭据/连接串等）。复用msg_exposure_gate._detect_msg_exposure()。

设计权衡
--------
1. **全量扫描**（非staged增量）：遍历src/zephyr/所有.py文件，生成存量清单。
2. **复用检测逻辑**：5.168直接import _detect_msg_exposure，保证与commit gate一致。
3. **noqa豁免**：5.135检测 ``# noqa`` 任意标记（BLE001/MSG-EXPOSURE等均豁免）；
   5.168复用gate的 ``# noqa: MSG-EXPOSURE`` 行级豁免。
4. **tests/豁免**：与commit gate一致，tests/目录不扫描。
5. **门禁自豁免**：governance/commit_gates/路径不扫描5.168（与gate一致）。

Usage::

    python scripts/governance/scan_exception_debt.py
    python scripts/governance/scan_exception_debt.py --json
    python scripts/governance/scan_exception_debt.py --dim 5.135
    python scripts/governance/scan_exception_debt.py --dim 5.168
"""

from __future__ import annotations

import argparse
import ast
import json
import logging
import os
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

# 项目根目录（scripts/governance/ 的上两级）
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SRC_ROOT = _PROJECT_ROOT / "src" / "zephyr"

# 复用 msg_exposure_gate 的敏感信息检测逻辑（5.168）
try:
    from zephyr.gov_enforcement.commit_gates.msg_exposure_gate import (
        _detect_msg_exposure,
        _filter_noqa_violations,
    )
    _MSG_EXPOSURE_AVAILABLE = True
except ImportError:
    logger.warning("无法导入 msg_exposure_gate._detect_msg_exposure，5.168检测不可用")
    _MSG_EXPOSURE_AVAILABLE = False


# === 5.135 异常粒度过粗检测 ===

def _has_noqa(line_content: str) -> bool:
    """检查行是否含任意 noqa 标记（# noqa / # noqa: XXX 均算豁免）。"""
    return "noqa" in line_content.lower()


def _is_broad_exception(handler: ast.ExceptHandler) -> bool:
    """判断 except handler 是否捕获过宽异常。

    Returns:
        True 表示 except Exception / except BaseException / bare except:
    """
    if handler.type is None:
        # bare except: — 最宽
        return True
    # except Exception / except BaseException
    if isinstance(handler.type, ast.Name):
        return handler.type.id in ("Exception", "BaseException")
    # except (Exception, ...) — 元组中含 Exception/BaseException 也算过宽
    if isinstance(handler.type, ast.Tuple):
        for elt in handler.type.elts:
            if isinstance(elt, ast.Name) and elt.id in ("Exception", "BaseException"):
                return True
    return False


def _detect_broad_exceptions(tree: ast.AST) -> list[tuple[int, str, str]]:
    """AST 中检测 except 异常粒度过粗。

    Returns:
        违规列表 [(lineno, except_kind, exception_name), ...]
        except_kind: "bare" / "Exception" / "BaseException" / "tuple-with-Exception"
    """
    violations: list[tuple[int, str, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ExceptHandler):
            continue
        if not _is_broad_exception(node):
            continue
        if node.type is None:
            kind, name = "bare", "except:"
        elif isinstance(node.type, ast.Name):
            kind, name = node.type.id, f"except {node.type.id}"
        elif isinstance(node.type, ast.Tuple):
            parts = [
                e.id for e in node.type.elts if isinstance(e, ast.Name)
            ]
            kind = "tuple-with-Exception"
            name = f"except ({', '.join(parts)})"
        else:
            kind, name = "unknown", "except ?"
        violations.append((node.lineno, kind, name))
    return violations


# === 文件遍历与扫描 ===

def _is_test_file(rel_path: str) -> bool:
    """tests/ 路径豁免（与 commit gate is_test_exempt 一致）。"""
    return "tests/" in rel_path.replace("\\", "/")


def _is_gate_file(rel_path: str) -> bool:
    """governance/commit_gates/ 路径豁免（与 MSG-EXPOSURE gate 自豁免一致）。"""
    return "governance/commit_gates/" in rel_path.replace("\\", "/")


def _scan_file_for_5135(rel_path: str, abs_path: str, content: str) -> list[dict]:
    """扫描单个文件的5.135违规（排除noqa行）。"""
    try:
        tree = ast.parse(content, filename=abs_path)
    except SyntaxError as e:
        logger.warning("5.135 跳过 %s: AST解析失败(%s: %s)", abs_path, type(e).__name__, e)
        return []
    lines = content.splitlines()
    violations = []
    for lineno, kind, name in _detect_broad_exceptions(tree):
        if lineno < 1 or lineno > len(lines):
            continue
        if _has_noqa(lines[lineno - 1]):
            continue  # noqa豁免
        violations.append({
            "dim": "5.135",
            "file": rel_path,
            "line": lineno,
            "kind": kind,
            "detail": name,
        })
    return violations


def _scan_file_for_5168(rel_path: str, abs_path: str, content: str) -> list[dict]:
    """扫描单个文件的5.168违规（复用msg_exposure_gate检测逻辑）。"""
    if not _MSG_EXPOSURE_AVAILABLE:
        return []
    if _is_gate_file(rel_path):
        return []  # 门禁自豁免
    try:
        tree = ast.parse(content, filename=abs_path)
    except SyntaxError as e:
        logger.warning("5.168 跳过 %s: AST解析失败(%s: %s)", abs_path, type(e).__name__, e)
        return []
    raw_violations = _detect_msg_exposure(tree)
    filtered = _filter_noqa_violations(content, raw_violations)
    return [
        {
            "dim": "5.168",
            "file": rel_path,
            "line": lineno,
            "kind": "msg_exposure",
            "detail": f"raise {exc_name}(f'...{{{hits[0]}}}...') [sensitive: {', '.join(hits)}]",
        }
        for lineno, exc_name, hits in filtered
    ]


def scan_all(dim_filter: str | None = None) -> dict[str, list[dict]]:
    """全量扫描 src/zephyr/**/*.py，返回5.135和5.168违规清单。

    Args:
        dim_filter: None=扫描全部；"5.135"=只扫异常粒度；"5.168"=只扫信息泄露。

    Returns:
        {"5.135": [...], "5.168": [...]}
    """
    results: dict[str, list[dict]] = {"5.135": [], "5.168": []}
    if not _SRC_ROOT.is_dir():
        logger.error("src root 不存在: %s", _SRC_ROOT)
        return results

    py_files = sorted(_SRC_ROOT.rglob("*.py"))
    total = len(py_files)
    scanned = 0
    for abs_path in py_files:
        rel_path = str(abs_path.relative_to(_PROJECT_ROOT)).replace("\\", "/")
        if _is_test_file(rel_path):
            continue
        try:
            content = abs_path.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            logger.warning("读取失败 %s: %s", abs_path, e)
            continue
        scanned += 1
        if dim_filter is None or dim_filter == "5.135":
            results["5.135"].extend(_scan_file_for_5135(rel_path, str(abs_path), content))
        if dim_filter is None or dim_filter == "5.168":
            results["5.168"].extend(_scan_file_for_5168(rel_path, str(abs_path), content))

    logger.info("扫描完成: %d/%d 文件，5.135=%d项，5.168=%d项",
                scanned, total, len(results["5.135"]), len(results["5.168"]))
    return results


# === 输出格式化 ===

def format_console_report(results: dict[str, list[dict]]) -> str:
    """格式化控制台报告——按文件聚类，含计数摘要。"""
    lines = []
    for dim in ("5.135", "5.168"):
        violations = results.get(dim, [])
        lines.append(f"\n{'=' * 70}")
        label = "异常粒度过粗" if dim == "5.135" else "异常信息泄露"
        lines.append(f"{dim} {label} — 共 {len(violations)} 项")
        lines.append("=" * 70)
        if not violations:
            lines.append("  （无违规）")
            continue
        # 按文件聚类
        by_file: dict[str, list[dict]] = {}
        for v in violations:
            by_file.setdefault(v["file"], []).append(v)
        # 按违规数降序排列文件
        for fpath in sorted(by_file, key=lambda f: -len(by_file[f])):
            file_vs = by_file[fpath]
            lines.append(f"\n  {fpath}  ({len(file_vs)} 项)")
            for v in sorted(file_vs, key=lambda x: x["line"])[:20]:
                lines.append(f"    L{v['line']:>5}  [{v['kind']}]  {v['detail']}")
            if len(file_vs) > 20:
                lines.append(f"    ... 还有 {len(file_vs) - 20} 项")
    lines.append(f"\n{'=' * 70}")
    total = sum(len(v) for v in results.values())
    lines.append(f"合计: {total} 项违规待修复")
    lines.append("=" * 70)
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="扫描5.135异常粒度过粗 + 5.168异常信息泄露违规清单（Phase 2 阶段0）"
    )
    parser.add_argument("--json", action="store_true", help="输出JSON格式")
    parser.add_argument("--dim", choices=["5.135", "5.168"], help="只扫描指定维度")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    results = scan_all(dim_filter=args.dim)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(format_console_report(results))
    return 0


if __name__ == "__main__":
    sys.exit(main())
