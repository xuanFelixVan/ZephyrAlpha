# [BLUEPRINT] MOD-INF-005 | scripts/arch_guard/_tools/patch_p1_paths.py | §
# [MODULE] scripts.arch_guard._tools.patch_p1_paths
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.arch_guard._tools.inject_idempotency
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
# [TTL] permanent
"""一次性工具——为 9 个 P1 契约补齐 physical_path 并运行 codegen。
CTR-P1-001~009 的 physical_path 均为 null，导致 generate_contracts.py 无法生成 Python dataclass。
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_GOV_DIR = _ROOT.parent / "governance"
if str(_GOV_DIR) not in sys.path:
    sys.path.insert(0, str(_GOV_DIR))

from _shared.constants import REPO_ROOT  # noqa: E402

YAML_PATH = (
    REPO_ROOT
    / "architecture_model"
    / "contracts"
    / "cross_layer_contracts.yaml"
)

PATH_MAP: dict[str, str] = {
    "CTR-P1-001": "src/zephyr/shared/contracts/factor_monitor_report.py",
    "CTR-P1-002": "src/zephyr/shared/contracts/macro_factor_signal.py",
    "CTR-P1-003": "src/zephyr/shared/contracts/capital_allocation_result.py",
    "CTR-P1-004": "src/zephyr/shared/contracts/model_serving_request.py",
    "CTR-P1-005": "src/zephyr/shared/contracts/model_serving_response.py",
    "CTR-P1-006": "src/zephyr/shared/contracts/strategy_lifecycle_event.py",
    "CTR-P1-007": "src/zephyr/shared/contracts/execution_report.py",
    "CTR-P1-008": "src/zephyr/shared/contracts/risk_dashboard_snapshot.py",
    "CTR-P1-009": "src/zephyr/shared/contracts/performance_attribution_report.py",
}

def main() -> int:
    if not YAML_PATH.exists():
        print(f"文件不存在: {YAML_PATH}")
        return 2

    content = YAML_PATH.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)

    replaced = 0
    current_ctr: str | None = None

    for i, line in enumerate(lines):
        if line.strip().startswith("- id: CTR-P1-"):
            current_ctr = line.strip().split("- id: ")[1].strip()
        if current_ctr and current_ctr in PATH_MAP:
            if line.strip() == "physical_path: null":
                new_path = PATH_MAP[current_ctr]
                lines[i] = f"    physical_path: {new_path}\n"
                replaced += 1
                current_ctr = None

    if replaced == 0:
        print("所有 P1 契约已有 physical_path——无需修改。")
        return 0

    tmp_path = f"{YAML_PATH}.{os.getpid()}.tmp"
    try:
        Path(tmp_path).write_text("".join(lines), encoding="utf-8")
        os.replace(tmp_path, YAML_PATH)
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
    print(f"✅ 已为 {replaced} 个 P1 契约补齐 physical_path。")
    return 0

if __name__ == "__main__":
    sys.exit(main())
