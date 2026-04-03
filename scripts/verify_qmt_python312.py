#!/usr/bin/env python3
"""
验证QMT Python 3.12环境配置
检查xtquant模块在Python 3.12中是否可用
"""

import sys
import os

print("=" * 80)
print("QMT Python 3.12环境验证脚本")
print("=" * 80)
print()

# 1. 检查Python版本
print("1. Python版本检查")
print("-" * 80)
print(f"Python版本: {sys.version}")
print(f"Python路径: {sys.executable}")
print(f"架构: {'64位' if sys.maxsize > 2**32 else '32位'}")
print()

# 2. 检查xtquant模块
print("2. xtquant模块检查")
print("-" * 80)
try:
    import xtquant
    print(f"✅ xtquant导入成功")
    if hasattr(xtquant, '__version__'):
        print(f"   版本: {xtquant.__version__}")
    else:
        print(f"   版本信息: 未知")
except ImportError as e:
    print(f"❌ xtquant导入失败: {e}")
    sys.exit(1)

# 3. 检查xtdata模块
print()
print("3. xtdata模块检查")
print("-" * 80)
try:
    from xtquant import xtdata
    print("✅ xtdata导入成功")
    
    # 尝试获取股票列表（不连接QMT客户端）
    stock_list = xtdata.get_stock_list_in_sector('沪深A股')
    if stock_list:
        print(f"✅ 数据接口测试成功")
        print(f"   获取到 {len(stock_list)} 只股票")
        print(f"   示例: {stock_list[:5]}")
    else:
        print("⚠️  数据接口返回空列表（可能未连接QMT客户端）")
except Exception as e:
    print(f"⚠️  xtdata检查异常: {e}")
    print("   这可能是正常的，因为QMT客户端可能未启动")

# 4. 检查xttrader模块
print()
print("4. xttrader模块检查")
print("-" * 80)
try:
    from xtquant.xttrader import XtQuantTrader
    print("✅ XtQuantTrader导入成功")
    
    # 尝试导入XtAccount（之前失败的关键）
    try:
        from xtquant.xttrader import XtAccount
        print("✅ XtAccount导入成功")
        print("   ⭐ 这是之前失败的关键点，现在成功了！")
    except ImportError as e:
        print(f"❌ XtAccount导入失败: {e}")
        print("   这可能是xtquant版本问题")
except Exception as e:
    print(f"⚠️  xttrader检查异常: {e}")

# 5. 检查环境变量
print()
print("5. 环境变量检查")
print("-" * 80)
env_path = ".env.qmt"
if os.path.exists(env_path):
    print(f"✅ 配置文件存在: {env_path}")
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            config_lines = [line.strip() for line in lines if '=' in line and not line.startswith('#')]
            print(f"   配置项数量: {len(config_lines)}")
    except Exception as e:
        print(f"⚠️  读取配置文件失败: {e}")
else:
    print(f"⚠️  配置文件不存在: {env_path}")

# 6. 总结
print()
print("=" * 80)
print("验证总结")
print("=" * 80)

checks = [
    ("Python版本 (3.12.x)", sys.version_info.major == 3 and sys.version_info.minor == 12),
    ("xtquant模块", "xtquant" in sys.modules),
    ("xtdata模块", "xtquant.xtdata" in str(sys.modules)),
    ("XtQuantTrader类", "xtquant.xttrader.XtQuantTrader" in str(sys.modules)),
]

try:
    from xtquant.xttrader import XtAccount
    checks.append(("XtAccount类", True))
except:
    checks.append(("XtAccount类", False))

all_passed = all(passed for _, passed in checks)

print("\n检查结果:")
for name, passed in checks:
    status = "✅" if passed else "❌"
    print(f"  {status} {name}")

print()
if all_passed:
    print("🎉 所有检查通过！Python 3.12环境配置成功！")
    print()
    print("下一步：")
    print("  1. 启动QMT客户端")
    print("  2. 登录时勾选【极简模式】或【独立交易】")
    print("  3. 运行测试脚本: python scripts/test_qmt_connection_v4.py")
else:
    print("⚠️  部分检查未通过，请根据上述提示修复。")

print()
