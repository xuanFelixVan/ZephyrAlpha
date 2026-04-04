"""
QMT API交易验证脚本 - 测试实盘和模拟盘连接

验证内容：
1. 模拟盘API连接
2. 实盘API连接
3. 账户订阅
4. 资产查询
"""

import os
import sys
import time
import random
from pathlib import Path
from datetime import datetime

print("=" * 80)
print("QMT API交易验证")
print("=" * 80)
print(f"验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Python版本: {sys.version}")
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
    print("⚠️  未找到 .env.qmt 配置文件，使用默认配置")

print()

# 导入xtquant库
print("导入xtquant库:")
print("-" * 80)
try:
    from xtquant import xtdata
    from xtquant.xttrader import XtQuantTrader
    from xtquant.xttype import StockAccount
    print("✅ xtquant导入成功")
    print(f"   xtdata模块: {xtdata}")
    print(f"   XtQuantTrader类: {XtQuantTrader}")
except ImportError as e:
    print(f"❌ xtquant导入失败: {e}")
    print("   请确保xtquant已正确安装")
    sys.exit(1)

print()

# 获取配置
sim_account = os.getenv('QMT_SIMULATION_ACCOUNT', '8886156677')
sim_path = os.getenv('QMT_SIMULATION_CLIENT_PATH', 'E:/国金QMT交易端模拟/userdata_mini')
live_account = os.getenv('QMT_LIVE_ACCOUNT', '8887871993')
live_path = os.getenv('QMT_LIVE_CLIENT_PATH', 'D:/国金证券QMT交易端/userdata_mini')

print("配置信息:")
print("-" * 80)
print(f"模拟账户: {sim_account}")
print(f"模拟路径: {sim_path}")
print(f"实盘账户: {live_account}")
print(f"实盘路径: {live_path}")
print()

# 测试数据接口
print("=" * 80)
print("步骤1: 测试数据接口 (xtdata)")
print("=" * 80)
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

# 测试模拟盘交易接口
print("=" * 80)
print("步骤2: 测试模拟盘交易接口 (xttrader)")
print("=" * 80)

session_id = random.randint(100000, 999999)
print(f"使用Session ID: {session_id}")
print(f"连接路径: {sim_path}")

try:
    # 创建交易对象
    xt_trader_sim = XtQuantTrader(sim_path, session_id)
    print("✅ XtQuantTrader对象创建成功")
    
    # 启动
    print("启动交易接口...")
    xt_trader_sim.start()
    time.sleep(1)
    
    # 连接
    print("连接QMT交易端...")
    connect_result = xt_trader_sim.connect()
    
    if connect_result == 0:
        print("✅ 模拟盘连接成功！")
        print()
        
        # 订阅账户
        print(f"订阅账户: {sim_account}")
        acc_sim = StockAccount(sim_account)
        subscribe_result = xt_trader_sim.subscribe(acc_sim)
        
        if subscribe_result == 0:
            print("✅ 模拟盘账户订阅成功！")
            print()
            
            # 查询资产
            print("查询账户资产...")
            try:
                asset = xt_trader_sim.query_stock_asset(acc_sim)
                if asset:
                    print("✅ 模拟盘资产查询成功")
                    print(f"   账户ID: {asset.account_id}")
                    print(f"   总资产: {asset.total_asset}")
                    print(f"   可用资金: {asset.cash}")
                    print(f"   市值: {asset.market_value}")
                    print(f"   冻结资金: {asset.frozen_cash}")
                else:
                    print("⚠️  资产查询返回空")
            except Exception as e:
                print(f"⚠️  资产查询失败: {e}")
        else:
            print(f"❌ 模拟盘账户订阅失败，返回码: {subscribe_result}")
    else:
        print(f"❌ 模拟盘连接失败，返回码: {connect_result}")
        print()
        print("可能原因：")
        print("  1. MiniQMT未启动或未登录")
        print("  2. 路径不正确")
        print("  3. 账号未在MiniQMT中登录")
        
except Exception as e:
    print(f"❌ 模拟盘测试失败: {e}")
    import traceback
    traceback.print_exc()

print()

# 测试实盘交易接口
print("=" * 80)
print("步骤3: 测试实盘交易接口 (xttrader)")
print("=" * 80)

session_id_live = random.randint(100000, 999999)
print(f"使用Session ID: {session_id_live}")
print(f"连接路径: {live_path}")

try:
    # 创建交易对象
    xt_trader_live = XtQuantTrader(live_path, session_id_live)
    print("✅ XtQuantTrader对象创建成功")
    
    # 启动
    print("启动交易接口...")
    xt_trader_live.start()
    time.sleep(1)
    
    # 连接
    print("连接QMT交易端...")
    connect_result = xt_trader_live.connect()
    
    if connect_result == 0:
        print("✅ 实盘连接成功！")
        print()
        
        # 订阅账户
        print(f"订阅账户: {live_account}")
        acc_live = StockAccount(live_account)
        subscribe_result = xt_trader_live.subscribe(acc_live)
        
        if subscribe_result == 0:
            print("✅ 实盘账户订阅成功！")
            print()
            
            # 查询资产
            print("查询账户资产...")
            try:
                asset = xt_trader_live.query_stock_asset(acc_live)
                if asset:
                    print("✅ 实盘资产查询成功")
                    print(f"   账户ID: {asset.account_id}")
                    print(f"   总资产: {asset.total_asset}")
                    print(f"   可用资金: {asset.cash}")
                    print(f"   市值: {asset.market_value}")
                    print(f"   冻结资金: {asset.frozen_cash}")
                else:
                    print("⚠️  资产查询返回空")
            except Exception as e:
                print(f"⚠️  资产查询失败: {e}")
        else:
            print(f"❌ 实盘账户订阅失败，返回码: {subscribe_result}")
    else:
        print(f"❌ 实盘连接失败，返回码: {connect_result}")
        print()
        print("可能原因：")
        print("  1. MiniQMT未启动或未登录实盘账户")
        print("  2. 路径不正确")
        print("  3. 实盘账号未在MiniQMT中登录")
        
except Exception as e:
    print(f"❌ 实盘测试失败: {e}")
    import traceback
    traceback.print_exc()

print()

# 总结
print("=" * 80)
print("验证总结")
print("=" * 80)
print()
print("✅ 如果所有测试通过，说明：")
print("   1. MiniQMT已正确启动")
print("   2. API接口可用")
print("   3. 可以开始开发QMT执行器")
print()
print("❌ 如果测试失败，请检查：")
print("   1. MiniQMT是否已启动并登录")
print("   2. 登录时是否勾选了【极简模式】")
print("   3. 账号是否正确")
print("   4. 路径是否正确")
print()

print("=" * 80)
print("验证完成")
print("=" * 80)