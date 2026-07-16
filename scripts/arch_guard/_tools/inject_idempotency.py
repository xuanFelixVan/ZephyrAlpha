# [BLUEPRINT] MOD-INF-005 | scripts/arch_guard/_tools/inject_idempotency.py | §
# [MODULE] scripts.arch_guard._tools.inject_idempotency
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] scripts.arch_guard._tools.build_ocp_manifest
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
"""为所有 P0/P1 契约添加 idempotency_key 字段——状态感知版本。

策略：
  - 遍历 YAML 的每个契约
  - 如果契约已有 idempotency_key → 跳过
  - 如果契约有 trace_context → 在其前插入
  - 否则 → 在 schema_version 前插入
"""

from __future__ import annotations

import os
import re
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

IDEMPOTENCY_FIELD = '- {name: idempotency_key, type: str, required: true, description: "幂等键（UUID），防止重复处理"}'
TRACE_CONTEXT_RE = re.compile(r"^\s*- \{name: trace_context,")
SCHEMA_VERSION_RE = re.compile(r"^\s*- \{name: schema_version,")
IDEMPOTENCY_RE = re.compile(r"^\s*- \{name: idempotency_key,")
CONTRACT_START_RE = re.compile(r"^\s*- id: (CTR-|OCP-)")

def process_yaml(content: str) -> tuple[str, int]:
    lines = content.splitlines(keepends=True)
    result: list[str] = []
    added = 0

    # 收集每个契约的行范围
    contract_ranges: list[tuple[int, int, str]] = []
    current_start: int | None = None
    current_id: str = ""

    for i, line in enumerate(lines):
        if CONTRACT_START_RE.match(line):
            if current_start is not None:
                contract_ranges.append((current_start, i, current_id))
            current_start = i
            m = CONTRACT_START_RE.match(line)
            current_id = m.group(0).strip() if m else ""

    if current_start is not None:
        contract_ranges.append((current_start, len(lines), current_id))

    # 对每个契约处理
    offset = 0
    for start, end, cid in contract_ranges:
        adj_start = start + offset
        adj_end = end + offset

        contract_lines = lines[adj_start:adj_end]
        contract_text = "".join(contract_lines)

        # 跳过已有 idempotency_key 的契约
        if IDEMPOTENCY_RE.search(contract_text):
            continue

        # 查找注入锚点
        inject_before = None
        inject_indent = "      "

        for j, line in enumerate(contract_lines):
            if TRACE_CONTEXT_RE.match(line):
                inject_before = j
                indent_match = re.match(r"^(\s*)", line)
                if indent_match:
                    inject_indent = indent_match.group(1)
                break

        if inject_before is None:
            for j, line in enumerate(contract_lines):
                if SCHEMA_VERSION_RE.match(line):
                    inject_before = j
                    indent_match = re.match(r"^(\s*)", line)
                    if indent_match:
                        inject_indent = indent_match.group(1)
                    break

        if inject_before is None:
            continue

        # 注入
        global_idx = adj_start + inject_before
        result.extend(lines[:global_idx])
        result.append(f"{inject_indent}{IDEMPOTENCY_FIELD}\n")
        result.extend(lines[global_idx:])
        lines = result
        result = []
        added += 1
        offset += 1

    # 剩余行
    if result:
        result.extend(lines)
    else:
        result = list(lines)

    return "".join(result), added

def main() -> int:
    if not YAML_PATH.exists():
        print(f"文件不存在: {YAML_PATH}")
        return 2

    content = YAML_PATH.read_text(encoding="utf-8")
    new_content, added = process_yaml(content)

    if added == 0:
        print("所有契约已包含 idempotency_key——无需修改。")
        return 0

    tmp_path = f"{YAML_PATH}.{os.getpid()}.tmp"
    try:
        Path(tmp_path).write_text(new_content, encoding="utf-8")
        os.replace(tmp_path, YAML_PATH)
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
    print(f"✅ 已为 {added} 条契约添加 idempotency_key 字段。")
    return 0

if __name__ == "__main__":
    sys.exit(main())
