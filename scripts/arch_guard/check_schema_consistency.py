"""
check_schema_consistency.py — Schema 三平面一致性检查 (INV-010) [桩文件]

INV-010: Cold / Warm / Hot 三平面必须共享 shared/contracts/ canonical schema。
status: stub — 需 Cold/Warm/Hot 三平面均有 active 代码后激活。

激活条件：
  1. Cold 平面（回测）有完整的 Python 数据生成代码
  2. Warm 平面（实盘）有数据消费代码
  3. Hot 平面（实时风控）有数据校验代码
  4. 可对比三个平面的 schema 定义是否一致
"""
import sys


def main() -> int:
    print("⏭ INV-010 Schema 三平面一致性检查 —— [桩文件] 跳过")
    print("   激活条件：Cold/Warm/Hot 三平面均有 active 代码。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
