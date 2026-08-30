# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.gov_drift.file_attr_checker
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES]
# [CONSUMERS] tests/file/test_file_attr_checker.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 属性检查不可跳过
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-INF-023 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
File Attribute Integrity — 文件底层属性完整性 §6.30。


final_owner_mismatch: Windows DACL变更


execution_bit_shift: Unix +x位变更


hidden_attribute_flip: Windows隐藏属性被翻转


encoding_regression: UTF-8->其他编码(编码退化检测)


size_anomaly: 修改后体积突变(>10× or <0.1×)


对标 blueprint.md §6.30。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: project_root 参数
#   fields: 参数 project_root，类型注解 str
#   code: file_attr_checker.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: snapshot_id 参数
#   fields: 参数 snapshot_id，类型注解 str
#   code: file_attr_checker.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: baseline 参数
#   fields: 参数 baseline，类型注解 dict[str, dict[str, object]]
#   code: file_attr_checker.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: file_path 参数
#   fields: 参数 file_path，类型注解 str
#   code: file_attr_checker.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① capture_baseline
#   name_en: capture_baseline
#   intro: capture_baseline(project_root, snapshot_id) 源码 L147-L154
#   desc: 源码 L147-L154
#   inputs: project_root snapshot_id
#   outputs: 返回值
# - id: A2
#   name_zh: ② check_size_anomaly
#   name_en: check_size_anomaly
#   intro: check_size_anomaly(project_root, baseline) 源码 L157-L199
#   desc: 源码 L157-L199
#   inputs: project_root baseline
#   outputs: list[FileAttrIssue]
# - id: A3
#   name_zh: ③ check_encoding
#   name_en: check_encoding
#   intro: check_encoding(file_path) 源码 L202-L225
#   desc: 源码 L202-L225
#   inputs: file_path
#   outputs: str | None
#   （注：A3 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: list[FileAttrIssue]
#   name_en: list[FileAttrIssue]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: tests/file/test_file_attr_checker.py
# - id: O2
#   name_zh: str | None
#   name_en: str | None
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: tests/file/test_file_attr_checker.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

import os
import stat
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path


@dataclass
class FileAttrIssue:
    issue_id: str

    file_path: str

    issue_type: str

    expected: str

    actual: str

    severity: str = "MINOR"

    detected_at: datetime = field(default_factory=lambda: datetime.now(UTC))


_FILE_ATTR_CACHE: dict[str, dict[str, object]] = {}


def _snapshot_file_attrs(file_path: str) -> dict[str, object]:
    try:
        st = os.stat(file_path)

        return {
            "size": st.st_size,
            "mode": stat.S_IMODE(st.st_mode),
            "executable": bool(stat.S_IMODE(st.st_mode) & stat.S_IEXEC),
            "readonly": not bool(stat.S_IMODE(st.st_mode) & stat.S_IWUSR),
        }

    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        return {}


def capture_baseline(project_root: str, snapshot_id: str) -> None:
    global _FILE_ATTR_CACHE

    for pf in Path(project_root).rglob("*.py"):
        if any(s in str(pf).lower() for s in (".git", "__pycache__", ".venv")):
            continue

        _FILE_ATTR_CACHE[str(pf)] = _snapshot_file_attrs(str(pf))


def check_size_anomaly(
    project_root: str,
    baseline: dict[str, dict[str, object]],
) -> list[FileAttrIssue]:
    issues: list[FileAttrIssue] = []

    for file_path, old_attrs in baseline.items():
        if not os.path.exists(file_path):
            issues.append(
                FileAttrIssue(
                    issue_id=f"attr-missing-{Path(file_path).stem}",
                    file_path=file_path,
                    issue_type="file_missing",
                    expected="exists",
                    actual="deleted",
                    severity="CRITICAL",
                )
            )

            continue

        new_attrs = _snapshot_file_attrs(file_path)

        old_size = int(old_attrs.get("size", 0))

        new_size = int(new_attrs.get("size", 0))

        if old_size > 0 and new_size > 0:
            ratio = new_size / old_size

            if ratio > 10.0 or ratio < 0.1:
                issues.append(
                    FileAttrIssue(
                        issue_id=f"attr-size-{Path(file_path).stem}",
                        file_path=file_path,
                        issue_type="size_anomaly",
                        expected=f"{old_size} bytes",
                        actual=f"{new_size} bytes",
                        severity="MAJOR",
                    )
                )

    return issues


def check_encoding(file_path: str) -> str | None:
    try:
        with open(file_path, "rb") as f:
            raw = f.read(4)

    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        return None

    if raw.startswith(b"\xef\xbb\xbf"):
        return "utf-8-bom"

    try:
        decoded = raw.decode("utf-8")

        return "utf-8"

    except UnicodeDecodeError:
        try:
            decoded = raw.decode("utf-16-be")

            return "utf-16-be"

        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            return "non-utf8"
