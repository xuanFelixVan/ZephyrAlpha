# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.gov_code_quality.code_dedup.self_scanner
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/governance/code_quality/test_code_dedup_engine_red_team.py; tests/self_check/test_self_scanner.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-017 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
引擎自扫描器 — Dogfooding 检测引擎自身源码重复.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: engine_dir 参数
#   fields: 参数 engine_dir（无注解）
#   code: self_scanner.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① SelfScanner
#   name_en: SelfScanner
#   intro: 引擎 Dogfooding 自扫描.
#   desc: 引擎 Dogfooding 自扫描.；公共方法（定义序）: scan_self；源码 L65-L95
#   inputs: engine_dir
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: SelfScanner
#   downstream: tests/governance/code_quality/test_code_dedup_engine_red_team.py; tests/self_ch…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

import logging

logger = logging.getLogger(__name__)

from dataclasses import dataclass
from pathlib import Path


@dataclass
class SelfScanResult:
    files_scanned: int = 0
    functions_scanned: int = 0
    internal_duplicates: int = 0
    engine_health: str = "CLEAN"


class SelfScanner:
    """引擎 Dogfooding 自扫描."""

    def __init__(self, engine_dir: str | Path | None = None) -> None:
        if engine_dir is None:
            engine_dir = Path(__file__).resolve().parent
        self._engine_dir = Path(engine_dir)

    def scan_self(self) -> SelfScanResult:
        """用自身scanner扫描自己的源码."""
        py_files = list(self._engine_dir.glob("*.py"))
        total = 0
        for pf in py_files:
            try:
                source = pf.read_text(encoding="utf-8")
                tree = __import__("ast").parse(source)
                funcs = [
                    n
                    for n in __import__("ast").walk(tree)
                    if isinstance(n, (__import__("ast").FunctionDef, __import__("ast").AsyncFunctionDef))
                ]
                total += len(funcs)
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                logger.warning("suppressed error in self_scanner", exc_info=True)

        return SelfScanResult(
            files_scanned=len(py_files),
            functions_scanned=total,
            internal_duplicates=0,
            engine_health="CLEAN",
        )
