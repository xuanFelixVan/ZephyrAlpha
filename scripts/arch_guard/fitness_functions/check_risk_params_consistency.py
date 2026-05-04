"""
check_risk_params_consistency.py — 风控参数三平面一致性检查 (INV-013) [桩文件]

INV-013: Cold 回测 / Warm 实盘 / Hot 拦截必须使用同一 config/risk_params.yaml。
status: stub — 需 config/risk_params.yaml 被多平面引用后激活。

激活条件：
  1. config/risk_params.yaml 存在且有实质内容
  2. Cold/Warm/Hot 三个平面均有引用该文件的代码
  3. 可对比三个平面引用的参数文件是否为同一 canonical source
"""
import sys


def main() -> int:
    print("⏭ INV-013 风控参数一致性检查 —— [桩文件] 跳过")
    print("   激活条件：config/risk_params.yaml 被多平面引用。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
