"""
QMT连接测试脚本 v3.0 - 正确的MiniQMT模式登录方式

重要发现：
1. 不需要单独下载MiniQMT客户端
2. 在国金QMT登录时勾选"极简模式"或"独立交易"即可
3. xtquant库已安装，可以直接使用

操作步骤：
1. 打开国金QMT软件
2. 登录时勾选"极简模式"或"独立交易"
3. 登录成功后运行此脚本
"""

import os
import sys
from pathlib import Path
from datetime import datetime

print("=" * 80)
print("QMT连接测试 v3.0 - MiniQMT模式登录指南")
print("=" * 80)
print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 步骤1: 检查环境变量
print("步骤1: 检查环境变量")
print("-" * 80)

env_path = Path(".env.qmt")
if env_path.exists():
    print("✅ 找到配置文件: .env.qmt")
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()
                if 'PASSWORD' not in key and 'TOKEN' not in key:
                    print(f"  {key}: {value}")
else:
    print("❌ 未找到配置文件: .env.qmt")

print()

# 步骤2: 检查xtquant库
print("步骤2: 检查xtquant库")
print("-" * 80)

try:
    import xtquant
    print(f"✅ xtquant库已安装")
    print(f"  版本: {xtquant.__version__ if hasattr(xtquant, '__version__') else '未知'}")
except ImportError as e:
    print(f"❌ xtquant库未安装: {e}")
    print("\n安装命令: pip install xtquant")
    sys.exit(1)

print()

# 步骤3: MiniQMT模式登录指南
print("步骤3: MiniQMT模式登录指南")
print("-" * 80)

print("\n⚠️  重要：请按照以下步骤登录MiniQMT模式！\n")

print("操作步骤：")
print("  1. 打开国金QMT软件")
print("  2. 在登录界面，勾选【极简模式】或【独立交易】")
print("  3. 输入账号密码：")
print(f"     模拟账户: {os.getenv('QMT_SIMULATION_ACCOUNT', '未设置')}")
print(f"     实盘账户: {os.getenv('QMT_LIVE_ACCOUNT', '未设置')}")
print("  4. 点击登录")
print("  5. 登录成功后，回到此脚本按回车继续...")

input("\n按回车键继续（确保已在MiniQMT模式下登录）...")

print()

# 步骤4: 测试数据接口
print("步骤4: 测试数据接口")
print("-" * 80)

try:
    from xtquant import xtdata
    
    print("测试获取实时行情...")
    data = xtdata.get_full_tick(['000001.SZ'])
    
    if data:
        print("✅ 数据接口测试成功")
        print(f"  获取到 {len(data)} 只股票的行情数据")
        
        # 显示部分数据
        if '000001.SZ' in data:
            quote = data['000001.SZ']
            print(f"\n  平安银行(000001.SZ)行情:")
            print(f"    最新价: {quote.get('lastPrice', 'N/A')}")
            print(f"    买一价: {quote.get('bidPrice', [0])[0] if quote.get('bidPrice') else 'N/A'}")
            print(f"    卖一价: {quote.get('askPrice', [0])[0] if quote.get('askPrice') else 'N/A'}")
    else:
        print("⚠️  数据接口返回空数据")
        print("  可能原因：QMT未登录或未选择MiniQMT模式")
        
except Exception as e:
    print(f"❌ 数据接口测试失败: {e}")
    print("\n可能原因：")
    print("  1. QMT未启动或未登录")
    print("  2. 未选择MiniQMT模式（极简模式/独立交易）")
    print("  3. 网络连接问题")

print()

# 步骤5: 测试交易接口
print("步骤5: 测试交易接口")
print("-" * 80)

sim_account = os.getenv('QMT_SIMULATION_ACCOUNT')
live_account = os.getenv('QMT_LIVE_ACCOUNT')

if not sim_account:
    print("⚠️  跳过交易接口测试（缺少账号信息）")
else:
    try:
        from xtquant import xttrader
        
        # 获取客户端路径
        client_path = os.getenv('QMT_SIMULATION_CLIENT_PATH', 'E:/国金QMT交易端模拟/bin.x64')
        
        print(f"客户端路径: {client_path}")
        print(f"测试账户: {sim_account}\n")
        
        # 创建交易对象
        session_id = 123456
        print("步骤5.1: 创建交易对象...")
        trader = xttrader.XtQuantTrader(sim_account, session_id, client_path)
        print("✅ 交易对象创建成功")
        
        # 启动交易线程
        print("\n步骤5.2: 启动交易线程...")
        trader.start()
        print("✅ 交易线程启动成功")
        
        # 连接
        print("\n步骤5.3: 连接交易账户...")
        connect_result = trader.connect()
        
        if connect_result == 0:
            print("✅ 交易接口连接成功！\n")
            
            # 查询资产
            print("步骤5.4: 查询账户资产...")
            try:
                asset = trader.query_stock_asset(sim_account)
                if asset:
                    print(f"\n账户资产信息:")
                    print(f"  总资产: {asset.total_asset:,.2f}")
                    print(f"  可用资金: {asset.cash:,.2f}")
                    print(f"  市值: {asset.market_value:,.2f}")
                    print(f"  账户类型: {'模拟' if '8886156677' in sim_account else '实盘'}")
            except Exception as e:
                print(f"⚠️  查询资产失败: {e}")
            
            # 查询持仓
            print("\n步骤5.5: 查询持仓...")
            try:
                positions = trader.query_stock_positions(sim_account)
                if positions:
                    print(f"  持仓数量: {len(positions)}")
                    for pos in positions[:3]:  # 只显示前3个
                        print(f"    {pos.stock_code}: {pos.volume}股")
                else:
                    print("  当前无持仓")
            except Exception as e:
                print(f"⚠️  查询持仓失败: {e}")
                
        else:
            print(f"❌ 交易接口连接失败，返回码: {connect_result}")
            
            if connect_result == -1:
                print("\n返回码 -1 的可能原因：")
                print("  1. ⚠️  QMT未在MiniQMT模式下登录")
                print("     → 解决：重新登录QMT，勾选【极简模式】或【独立交易】")
                print("  2. ⚠️  账号未开通API交易权限")
                print("     → 解决：联系国金证券客服95310确认权限")
                print("  3. ⚠️  客户端路径不正确")
                print("     → 解决：检查.env.qmt中的QMT_SIMULATION_CLIENT_PATH")
                
    except Exception as e:
        print(f"❌ 交易接口测试失败: {e}")
        import traceback
        traceback.print_exc()

print()

# 总结
print("=" * 80)
print("测试总结")
print("=" * 80)

print("\n关键步骤回顾：")
print("  [✓] 1. xtquant库已安装")
print("  [?] 2. QMT是否在MiniQMT模式下登录？")
print("       → 登录时勾选【极简模式】或【独立交易】")
print("  [?] 3. 账号API权限是否已开通？")
print("       → 联系国金证券客服95310确认")

print("\n如果连接失败，请检查：")
print("  1. QMT是否在【极简模式】或【独立交易】下登录")
print("  2. 登录的账号是否与配置文件中的账号一致")
print("  3. 客户端路径是否正确")

print("\n参考文档：")
print("  - docs/05_IMPLEMENTATION/04_OPERATIONS/QMT_CONNECTION_ROOT_CAUSE_ANALYSIS.md")
print("  - docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/QMT_INTERFACE.md")

print()
