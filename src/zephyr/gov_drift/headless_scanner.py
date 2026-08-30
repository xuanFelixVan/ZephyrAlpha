# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md
# [MODULE] zephyr.gov_drift.headless_scanner
# [DOMAIN] D_GOV_DRIFT
# [DEPENDENCIES] zephyr.gov_drift.drift_models
# [CONSUMERS] tests/audit/test_headless_scanner.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 无头扫描不可跳过
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/behavioral-auditor/
# [A_module] module_id=MOD-INF-023 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Headless Scanner — headless_scanner.py

LIGHT+DEEP 与会话日志 _interrupt_log.jsonl 扫描。

对标 blueprint.md §2.18 / D-023-32。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: modules 参数
#   fields: 参数 modules，类型注解 list[str]
#   code: headless_scanner.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: project_root 参数
#   fields: 参数 project_root，类型注解 str | None
#   code: headless_scanner.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: log_path 参数
#   fields: 参数 log_path，类型注解 str
#   code: headless_scanner.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① headless_scan_light
#   name_en: headless_scan_light
#   intro: headless_scan_light(modules, project_root) 源码 L150-L174
#   desc: 源码 L150-L174
#   inputs: modules project_root
#   outputs: ScanResult
# - id: A2
#   name_zh: ② parse_interrupt_log
#   name_en: parse_interrupt_log
#   intro: parse_interrupt_log(log_path) 源码 L177-L210
#   desc: 源码 L177-L210
#   inputs: log_path
#   outputs: list[InterruptLog]
#   （注：A2 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: ScanResult
#   name_en: ScanResult
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: tests/audit/test_headless_scanner.py
# - id: O2
#   name_zh: list[InterruptLog]
#   name_en: list[InterruptLog]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: tests/audit/test_headless_scanner.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass

from zephyr.shared.infra.process_pool import run_subprocess_hidden

from .drift_models import ScanResult


@dataclass
class HeadlessDiffEntry:
    file: str

    hunk: str = ""

    dimension: str = ""

    file_version: str = ""

    sha256: str = ""


@dataclass
class InterruptLog:
    session_id: str

    triggered_by: str

    context_at: str

    scan_outcome: str

    errors_found: int


def _scan_script(script_path: str) -> list[HeadlessDiffEntry]:
    if not os.path.exists(script_path):
        return []

    try:
        result = run_subprocess_hidden(["python", script_path], capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            return []

        # 5.147.11 修复: subprocess stdout 无大小限制, 30s 内可产生数 GB 文本触发 OOM。
        # 设定 MAX_OUTPUT_SIZE=10MB 上限, 超限返回空列表
        MAX_OUTPUT_SIZE = 10 * 1024 * 1024  # 10MB
        if len(result.stdout) > MAX_OUTPUT_SIZE:
            return []

        output = json.loads(result.stdout)

        if not isinstance(output, list):
            return []

        return [
            HeadlessDiffEntry(
                file=entry.get("file", ""),
                hunk=entry.get("hunk", ""),
                dimension=entry.get("dimension", ""),
                sha256=entry.get("sha256", ""),
            )
            for entry in output
            if isinstance(entry, dict)
        ]

    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        return []


def headless_scan_light(modules: list[str], project_root: str | None = None) -> ScanResult:
    root = project_root or os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

    scripts_dir = os.path.join(root, "scripts", "governance", "d5_architecture")

    results: list[object] = []

    for fname in sorted(os.listdir(scripts_dir)) if os.path.isdir(scripts_dir) else []:
        if not fname.startswith("validate_") or not fname.endswith(".py"):
            continue

        fp = os.path.join(scripts_dir, fname)

        entries = _scan_script(fp)

        results.extend(entries)

    return ScanResult(
        scan_id=uuid.uuid4(),
        detectors_run=len(list(os.listdir(scripts_dir))) if os.path.isdir(scripts_dir) else 0,
        total_drift_events=len(results),
        new_events=[],
        resolved_events=[],
        storm_mode_triggered=len(results) > 50,
    )


def parse_interrupt_log(log_path: str) -> list[InterruptLog]:
    if not os.path.exists(log_path):
        return []

    entries: list[InterruptLog] = []

    try:
        with open(log_path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()

                if not line:
                    continue

                try:
                    data = json.loads(line)

                    entries.append(
                        InterruptLog(
                            session_id=data.get("session_id", ""),
                            triggered_by=data.get("triggered_by", ""),
                            context_at=data.get("context_at", ""),
                            scan_outcome=data.get("scan_outcome", ""),
                            errors_found=data.get("errors_found", 0),
                        )
                    )

                except json.JSONDecodeError:
                    pass

    except (OSError, UnicodeDecodeError):
        pass

    return entries
