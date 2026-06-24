# [BLUEPRINT]
# [MODULE] scripts.governance._audit_gate_registry
# [DOMAIN]
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
"""DM-201204 STEP 2: 对比磁盘YAML文件和_registry.yaml注册情况.

找出未注册的门禁YAML文件。
"""
import sys
import yaml
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
GATES_DIR = ROOT / "src" / "zephyr" / "governance" / "rule_enforcement"
REGISTRY_FILE = GATES_DIR / "_registry.yaml"


def main() -> int:
    # 加载_registry.yaml
    with open(REGISTRY_FILE, encoding="utf-8") as f:
        registry = yaml.safe_load(f)

    # 提取已注册的file字段
    registered_files = set()
    for gate in registry.get("gates", []):
        file_field = gate.get("file", "")
        if file_field:
            registered_files.add(file_field)

    print(f"[INFO] _registry.yaml 登记了 {len(registry['gates'])} 个门禁")
    print(f"[INFO] 其中有file字段的: {len(registered_files)} 个")

    # 扫描磁盘上的YAML文件（排除_registry.yaml和_template.yaml）
    disk_files = []
    for yf in GATES_DIR.rglob("*.yaml"):
        if yf.name in ("_registry.yaml", "_template.yaml"):
            continue
        rel = yf.relative_to(GATES_DIR).as_posix()
        disk_files.append(rel)

    print(f"[INFO] 磁盘上有 {len(disk_files)} 个门禁YAML文件")

    # 对比
    registered_set = set(registered_files)
    disk_set = set(disk_files)

    # 磁盘上有但注册表中没有的
    unregistered = disk_set - registered_set
    # 注册表中有但磁盘上没有的
    missing_on_disk = registered_set - disk_set

    print(f"\n=== 对比结果 ===")
    print(f"未注册的YAML文件（磁盘有但注册表无）: {len(unregistered)}")
    for f in sorted(unregistered):
        print(f"  - {f}")

    print(f"\n注册表引用但磁盘缺失的文件: {len(missing_on_disk)}")
    for f in sorted(missing_on_disk):
        print(f"  - {f}")

    if not unregistered and not missing_on_disk:
        print("\n[OK] 所有门禁YAML文件都已注册，注册表完整！")
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
