# [BLUEPRINT] MOD-INF-017 | docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md
# [MODULE] zephyr.gov_code_quality.code_dedup.path_index_validator
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] tests/path/test_path_index_validator.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-017 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
路径索引验证——验证 config 数据集相对路径表与实际文件系统同步.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: path_index_validator.py
# 层: 算法
# - id: A1
#   name_zh: ① PathIndexValidator
#   name_en: PathIndexValidator
#   intro: class PathIndexValidator 源码 L63-L87
#   desc: 公共方法（定义序）: validate；源码 L63-L87
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: PathIndexValidator
#   downstream: tests/path/test_path_index_validator.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class PathMismatch:
    indexed_path: str
    actual_status: str
    expected_exists: bool
    actual_exists: bool


@dataclass
class PathIndexValidator:
    root: Path = field(default_factory=lambda: Path.cwd())
    mismatches: list[PathMismatch] = field(default_factory=list)

    def validate(self, indexed_paths: list[str]) -> dict[str, Any]:
        self.mismatches.clear()
        for ip in indexed_paths:
            fp = self.root / ip
            exists = fp.exists()
            if not exists:
                self.mismatches.append(
                    PathMismatch(
                        indexed_path=ip,
                        actual_status="MISSING",
                        expected_exists=True,
                        actual_exists=False,
                    )
                )

        return {
            "total_checked": len(indexed_paths),
            "mismatches": len(self.mismatches),
            "clean": len(self.mismatches) == 0,
            "details": [{"path": m.indexed_path, "status": m.actual_status} for m in self.mismatches],
        }
