"""
check_survivorship_bias.py — Survivorship Bias 检查 (INV-014) [桩文件]

INV-014: 回测数据集必须包含退市/停牌标的，不得使用存活者偏差数据。
status: stub — 需回测数据集有退市/停牌标的后激活。

激活条件：
  1. L00 Data Source 有完整的历史成分股/退市数据
  2. 回测数据集包含足够的历史覆盖期
  3. 可检测数据集中是否包含退市标的（通过对比指数成分股历史变动）
"""
import sys


def main() -> int:
    print("⏭ INV-014 Survivorship Bias 检查 —— [桩文件] 跳过")
    print("   激活条件：回测数据集有完整退市/停牌标的。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
