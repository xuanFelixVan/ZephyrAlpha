"""
QMT连接测试脚本 v6 - 修正XtQuantTrader参数顺序

修复：
1. ✅ 修正XtQuantTrader参数顺序（path, session_id）
2. ✅ 移除XtAccount导入（不存在）
3. ✅ 使用账户字符串而不是XtAccount对象
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime

print("=" * 80)
print("QMT连接测试脚本 v6")
print("=" * 80)
print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Python版本: {sys.version}")
print()

# 检查Python版本
if not (sys.version_info.major == 3 and sys.version_info.minor == 12):
    print(f"⚠️  警告: Python版本应为3.12，当前为{sys.version_info.major}.{sys.version_info.minor}")
    print("   这可能导致xtquant API不兼容")
    print("   建议使用Python 3.12环境")
    print()

# 加载环境变量
env_path = Path(".env.qmt")
if env_path.exists():
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()
    print("✅ 已加载 .env.qmt 配置文件")
else:
    print("❌ 未找到 .env.qmt 配置文件")
    print("   请确保配置文件存在并包含QMT账户信息")
    sys.exit(1)

# 显示配置信息
print()
print("配置信息:")
print("-" * 80)
sim_account = os.getenv('QMT_SIMULATION_ACCOUNT', '未设置')
live_account = os.getenv('QMT_LIVE_ACCOUNT', '未设置')
sim_path = os.getenv('QMT_SIMULATION_CLIENT_PATH', '未设置')

print(f"模拟账户: {sim_account}")
print(f"实盘账户: {live_account}")
print(f"客户端路径: {sim_path}")

# 检查路径是否存在
if sim_path != '未设置':
    path_exists = Path(sim_path).exists()
    print(f"路径存在: {'✅' if path_exists else '❌'}")
else:
    print("路径存在: ⚠️  未配置")

print()

# 导入xtquant
print("导入xtquant库:")
print("-" * 80)
try:
    from xtquant import xtdata
    from xtquant.xttrader import XtQuantTrader
    print("✅ xtquant导入成功")
except ImportError as e:
    print(f"❌ xtquant导入失败: {e}")
    print("   可能原因:")
    print("   1. xtquant未安装")
    print("   2. Python版本不兼容（需要3.6-3.12）")
    print("   3. 不在正确的Python环境中")
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
    print("   可能原因:")
    print("   1. QMT客户端未启动")
    print("   2. xtquant库问题")

print()

# 步骤2: 测试交易接口
print("步骤2: 测试交易接口 (xttrader)")
print("-" * 80)

# 使用新的session避免冲突
session_id = int(time.time()) % 1000000 + 100000
print(f"使用session: {session_id}")

try:
    # 创建交易对象 - 注意参数顺序: (path, session_id)
    path = os.getenv('QMT_SIMULATION_CLIENT_PATH')
    if not path:
        print("❌ 未配置客户端路径")
        print("   请在.env.qmt中设置QMT_SIMULATION_CLIENT_PATH")
        sys.exit(1)
    
    print(f"连接路径: {path}")
    print(f"Session ID: {session_id}")
    
    # 重要: 参数顺序是 (path, session_id)
    trader = XtQuantTrader(path, session_id)
    print("✅ XtQuantTrader对象创建成功")
    
    # 连接
    print()
    print("正在连接QMT交易接口...")
    connect_result = trader.connect()
    print(f"连接结果: {connect_result}")
    
    if connect_result == 0:
        print("✅ 交易接口连接成功！")
        print()
        
        # 订阅账户（使用账户字符串）
        account_id = sim_account
        print(f"订阅账户: {account_id}")
        subscribe_result = trader.subscribe(account_id)
        print(f"订阅结果: {subscribe_result}")
        
        if subscribe_result == 0:
            print("✅ 账户订阅成功！")
            print()
            
            # 查询资产（使用账户字符串）
            print("查询账户资产...")
            try:
                asset = trader.query_stock_asset(account_id)
                if asset:
                    print("✅ 资产查询成功")
                    print(f"   总资产: {asset.total_asset}")
                    print(f"   可用资金: {asset.cash}")
                    print(f"   市值: {asset.market_value}")
                else:
                    print("⚠️  资产查询返回空")
            except Exception as e:
                print(f"⚠️  资产查询失败: {e}")
                print("   可能原因:")
                print("   1. 账户未正确订阅")
                print("   2. QMT客户端问题")
        else:
            print(f"❌ 账户订阅失败，返回码: {subscribe_result}")
            print("   可能原因:")
            print("   1. 账户ID错误")
            print("   2. 账户未在QMT客户端中登录")
            print("   3. 权限问题")
    else:
        print(f"❌ 交易接口连接失败，返回码: {connect_result}")
        print()
        print("诊断建议:")
        print("-" * 80)
        
        if connect_result == -1:
            print("返回码 -1 的可能原因：")
            print("  1. ❌ 客户端未以极简模式登录")
            print("     → 解决：在QMT登录界面勾选【极简模式】或【独立交易】")
            print()
            print("  2. ❌ 路径不正确")
            print(f"     → 当前路径: {path}")
            print("     → 应该指向 userdata_mini 文件夹")
            print()
            print("  3. ❌ 客户端未正确登录交易账户")
            print(f"     → 确认登录账号: {sim_account}")
            print("     → 解决：在QMT客户端中重新登录")
            print()
            print("  4. ❌ Session冲突")
            print("     → 解决：等待5秒后重试，或使用不同的session")
            print()
            print("  5. ❌ Python版本不兼容")
            print(f"     → 当前版本: Python {sys.version_info.major}.{sys.version_info.minor}")
            print("     → xtquant支持: Python 3.6 - 3.12")
        else:
            print(f"未知错误码: {connect_result}")
            print("参考官方文档: https://dict.thinktrader.net/nativeApi/question_function.html")
        
except Exception as e:
    print(f"❌ 交易接口测试失败: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 80)
print("测试完成")
print("=" * 80)
print()
print("下一步建议:")
print("  1. 如果连接成功 → 开始开发QMT执行器")
print("  2. 如果连接失败 → 检查QMT客户端是否以极简模式登录")
print("  3. 运行诊断脚本: scripts/diagnose_qmt_permission.py")
print()