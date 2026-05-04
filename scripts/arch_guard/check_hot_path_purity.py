"""
check_hot_path_purity.py — Hot Path 纯度检查 (INV-012) [桩文件]

INV-012: Hot 路径严禁同步调用任何 Python asyncio 代码。
status: stub — 需 Hot Path 有 Python 代码后激活。

激活条件：
  1. Hot Path 中有 Python 代码（当前主要为配置/YAML）
  2. 可通过 AST 分析检测 asyncio 调用链
  3. 检测是否有阻塞式 I/O 或同步调用模式
"""
import sys


def main() -> int:
    print("⏭ INV-012 Hot Path 纯度检查 —— [桩文件] 跳过")
    print("   激活条件：Hot Path 有 Python 代码。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
