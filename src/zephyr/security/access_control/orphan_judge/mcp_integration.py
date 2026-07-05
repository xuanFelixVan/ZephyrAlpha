# [BLUEPRINT] MOD-INF-029 | docs/03_modules/_cross_layer/orphan_judge/blueprint.md | §7.2
# [MODULE] zephyr.security.access_control.orphan_judge.mcp_integration
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.access_control.orphan_judge.judge; zephyr.governance.__init__
# [CONSUMERS] MCP Server Tool Registry; FastMCP clients
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 不实现MCP协议; 仅注册工具到MCP_TOOLS字典
# [MODIFY-GUARD] MCP_TOOLS注册格式变更时同步此文件
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 注册失败返回空dict
# [TESTS] tests/orphan-judge/test_mcp_integration.py
# [A_module] module_id=MOD-SEC_mcp_integration | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

__all__ = ["ORPHAN_JUDGE_TOOLS", "register_tools"]


def _judge_file(file_path: str) -> dict[str, Any]:
    from zephyr.security.access_control.orphan_judge.judge import OrphanJudge

    judge = OrphanJudge()
    result = judge.judge(file_path, dry_run=True)
    return {
        "path": result.path,
        "verdict": result.verdict.value,
        "confidence": result.confidence.value,
        "reason": result.reason,
    }


def _scan_directory(directory: str, limit: int = 100) -> dict[str, Any]:
    from zephyr.security.access_control.orphan_judge.judge import OrphanJudge

    root = Path(directory)
    if not root.is_dir():
        return {"error": f"Not a directory: {directory}"}
    py_files = sorted(root.rglob("*.py"))[:limit]
    judge = OrphanJudge()
    results = []
    for fpath in py_files:
        rel_path = str(fpath).replace("\\", "/")
        try:
            result = judge.judge(rel_path, dry_run=True)
            results.append(
                {
                    "path": rel_path,
                    "verdict": result.verdict.value,
                    "confidence": result.confidence.value,
                }
            )
        except Exception as exc:
            results.append({"path": rel_path, "error": str(exc)})
    summary = {}
    for r in results:
        v = r.get("verdict", "ERROR")
        summary[v] = summary.get(v, 0) + 1
    return {"total": len(results), "summary": summary, "results": results}


ORPHAN_JUDGE_TOOLS: dict[str, dict[str, Any]] = {
    "judge_file": {
        "function": _judge_file,
        "description": "对单个文件运行孤儿判定引擎（五层全链路+决策表）",
        "parameters": {"file_path": "str"},
    },
    "scan_directory": {
        "function": _scan_directory,
        "description": "对目录批量运行孤儿判定",
        "parameters": {"directory": "str", "limit": "int"},
    },
}


def register_tools() -> bool:
    try:
        from zephyr.infrastructure.asset_inventory.mcp_server import MCP_TOOLS

        MCP_TOOLS.update(ORPHAN_JUDGE_TOOLS)
        logger.info("orphan-judge tools registered to MCP_TOOLS")
        return True
    except ImportError:
        logger.warning("MCP server not available, tools not registered")
        return False
    except Exception as exc:
        logger.error("MCP tool registration failed: %s", exc)
        return False
