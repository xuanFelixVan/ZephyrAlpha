"""
QMT连接测试脚本 v4 - 使用正确的路径格式

修复：
1. ✅ 路径从 bin.x64 改为 userdata_mini
2. ✅ 使用新的session避免冲突
3. ✅ 添加详细的错误诊断
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime

print("=" * 80)
print("QMT连接测试脚本 v4")
print("=" * 80)
print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 加载环境变量
env_path = Path(".env.qmt")
if env_path.exists():
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()
    print("✅ 已加载 .env.qmt 配置文件\n")
else:
    print("❌ 未找到 .env.qmt 配置文件\n")
    sys.exit(1)

# 显示配置信息
print("配置信息:")
print("-" * 80)
print(f"模拟账户: {os.getenv('QMT_SIMULATION_ACCOUNT')}")
print(f"实盘账户: {os.getenv('QMT_LIVE_ACCOUNT')}")
print(f"模拟客户端路径: {os.getenv('QMT_SIMULATION_CLIENT_PATH')}")
print(f"实盘客户端路径: {os.getenv('QMT_LIVE_CLIENT_PATH')}")
print()

# 检查路径是否存在
sim_path = Path(os.getenv('QMT_SIMULATION_CLIENT_PATH', ''))
live_path = Path(os.getenv('QMT_LIVE_CLIENT_PATH', ''))

print("路径检查:")
print("-" * 80)
print(f"模拟路径存在: {'✅' if sim_path.exists() else '❌'} {sim_path}")
print(f"实盘路径存在: {'✅' if live_path.exists() else '❌'} {live_path}")
print()

# 导入xtquant
print("导入xtquant库:")
print("-" * 80)
try:
    from xtquant import xtdata
    from xtquant.xttrader import XtQuantTrader, XtAccount
    print("✅ xtquant导入成功")
except ImportError as e:
    print(f"❌ xtquant导入失败: {e}")
    sys.exit(1)

print()

# 步骤1: 测试数据接口
print("步骤1: 测试数据接口 (xtdata)")
print("-" * 80)
try:
    stock_list = xtdata.get_stock_list_in_sector('沪深A股')
    if stock_list:
        print(f"✅ 数据接口测试成功")
        print(f"   获取到 {len(stock_list)} 只股票")
        print(f"   示例: {stock_list[:5]}")
    else:
        print("⚠️  数据接口返回空列表")
except Exception as e:
    print(f"❌ 数据接口测试失败: {e}")

print()

# 步骤2: 测试交易接口
print("步骤2: 测试交易接口 (xttrader)")
print("-" * 80)

# 使用新的session避免冲突
session_id = int(time.time()) % 1000000 + 100000
print(f"使用session: {session_id}")

try:
    # 创建交易对象
    path = os.getenv('QMT_SIMULATION_CLIENT_PATH')
    print(f"\n连接路径: {path}")
    
    trader = XtQuantTrader(session_id, path)
    print("✅ XtQuantTrader对象创建成功")
    
    # 连接
    print("\n正在连接...")
    connect_result = trader.connect()
    print(f"连接结果: {connect_result}")
    
    if connect_result == 0:
        print("✅ 交易接口连接成功！")
        
        # 订阅账户
        account = XtAccount(
            account_type='STOCK',  # 股票账户
            account_id=os.getenv('QMT_SIMULATION_ACCOUNT')
        )
        
        print(f"\n订阅账户: {account.account_id}")
        subscribe_result = trader.subscribe(account)
        print(f"订阅结果: {subscribe_result}")
        
        if subscribe_result == 0:
            print("✅ 账户订阅成功！")
            
            # 查询资产
            print("\n查询账户资产...")
            try:
                asset = trader.query_stock_asset(account)
                if asset:
                    print("✅ 资产查询成功")
                    print(f"   总资产: {asset.total_asset}")
                    print(f"   可用资金: {asset.cash}")
                    print(f"   市值: {asset.market_value}")
                else:
                    print("⚠️  资产查询返回空")
            except Exception as e:
                print(f"⚠️  资产查询失败: {e}")
        else:
            print(f"❌ 账户订阅失败，返回码: {subscribe_result}")
    else:
        print(f"❌ 交易接口连接失败，返回码: {connect_result}")
        
        # 诊断建议
        print("\n诊断建议:")
        print("-" * 80)
        
        if connect_result == -1:
            print("返回码 -1 的可能原因：")
            print("  1. ❌ 客户端未以极简模式登录")
            print("     → 解决：在QMT登录界面勾选【极简模式】或【独立交易】")
            print()
            print("  2. ❌ Python版本不兼容")
            print(f"     → 当前版本: Python {sys.version_info.major}.{sys.version_info.minor}")
            print("     → 官方支持: Python 3.6 - 3.12 (64位)")
            print("     → 解决：降级到Python 3.12或更低版本")
            print()
            print("  3. ❌ Session冲突")
            print("     → 解决：等待5秒后重试，或使用不同的session")
            print()
            print("  4. ❌ 客户端未正确登录交易账户")
            print(f"     → 确认登录账号: {os.getenv('QMT_SIMULATION_ACCOUNT')}")
            print("     → 解决：在QMT客户端中重新登录")
        
except Exception as e:
    print(f"❌ 交易接口测试失败: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
print("测试完成")
print("=" * 80)
