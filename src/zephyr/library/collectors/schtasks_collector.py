# [BLUEPRINT] MOD-LIB-004 | docs/03_modules/_domain_library/blueprint.md | §4.4
# [MODULE] zephyr.library.collectors.schtasks_collector
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.library.schema; zephyr.shared.infra.process_pool (run_subprocess_hidden)
# [CONSUMERS] zephyr.library.collectors
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 只读 schtasks /query；子进程必经 run_subprocess_hidden（BARE-SUBPROCESS）；只收 ZephyrAlpha_*/tilib* 相关任务
# [MODIFY-GUARD] gate_id 不适用
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] schtasks 失败折叠为 [{"error": ...}]
# [TESTS] tests/library/test_library_smoke.py
# [A_module] module_id=MOD-LIB-004 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""schtasks_collector — 图书馆采集器（MOD-LIB-004，只读）。

# [ALGO_FLOW] external: docs/03_modules/_domain_library/algo_flow/collectors/schtasks_collector.yaml
"""

from __future__ import annotations

import csv
import io
from typing import Any, Final

from zephyr.library.ledger_schema import derive_asset_id
from zephyr.shared.infra.process_pool import run_subprocess_hidden

__all__ = ["collect"]  # noqa: n114-final  n114-final豁免: __all__是Python导出约定，非可变常量，无需Final标注（先例=asyncio_run_in_context_gate.py L77）

_INTERESTING = ("zephyralpha", "tilib")


def collect() -> list[dict[str, Any]]:
    """枚举 Windows 计划任务，产出 TASK: 资产（仅 ZephyrAlpha 相关）。

    Returns:
        资产字典列表；失败折叠为 [{"error": ...}]。

    """
    try:
        done = run_subprocess_hidden(
            ["schtasks", "/query", "/fo", "CSV", "/nh"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )
    except Exception as exc:  # noqa: BLE001 — fail-soft
        return [{"error": f"{type(exc).__name__}: {exc}"}]
    if done.returncode != 0:
        return [{"error": f"schtasks exit={done.returncode}"}]
    out: list[dict[str, Any]] = []
    reader = csv.reader(io.StringIO(done.stdout or ""))
    for row in reader:
        if not row:
            continue
        task_name = row[0].strip()
        lowered = task_name.lower()
        if not any(tag in lowered for tag in _INTERESTING):
            continue
        status = row[3].strip() if len(row) > 3 else "Unknown"
        out.append(
            {
                "asset_id": derive_asset_id("task", f"schtasks:{task_name}"),
                "kind": "task",
                "home": f"schtasks:{task_name}",
                "fingerprint_sha256": None,
                "fingerprint_aux": {"status": status},
                "title": task_name,
                "ai_contract": None,
                "owner_domain": None,
                "tags": ["schtasks", "外溢资产"],
            }
        )
    return out
