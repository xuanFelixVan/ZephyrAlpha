"""
QMT连接测试脚本 v2.0 - 基于官方文档的正确连接方式

关键发现：
1. 必须使用MiniQMT客户端（不是普通版QMT）
2. 需要Token认证（从 https://xuntou.net/#/userInfo 获取）
3. 账号需要开通API交易权限

参考文档：
- docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/QMT_INTERFACE.md
- docs/05_IMPLEMENTATION/04_OPERATIONS/improvements/IMP_002_QMT_API_COMMUNITY_RESEARCH.md
"""

import os
import sys
from pathlib import Path
from datetime import datetime

print("=" * 80)
print("QMT连接测试 v2.0 - 基于官方文档的正确方式")
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
                if 'PASSWORD' not in key:
                    print(f"  {key}: {value}")
else:
    print("❌ 未找到配置文件: .env.qmt")

print()

# 步骤2: 检查Token
print("步骤2: 检查Token认证")
print("-" * 80)

qmt_token = os.getenv('QMT_TOKEN')
if qmt_token:
    print(f"✅ Token已设置: {qmt_token[:10]}...")
else:
    print("❌ Token未设置")
    print("\n⚠️  关键问题：缺少Token认证！")
    print("\n获取Token的步骤：")
    print("  1. 访问: https://xuntou.net/#/userInfo")
    print("  2. 注册账号（如果还没有）")
    print("  3. 获取Token")
    print("  4. 在 .env.qmt 文件中添加: QMT_TOKEN=您的token")
    print("\n⚠️  没有Token将无法连接行情服务！")

print()

# 步骤3: 检查QMT客户端版本
print("步骤3: 检查QMT客户端版本")
print("-" * 80)

client_path = os.getenv('QMT_SIMULATION_CLIENT_PATH', 'E:/国金QMT交易端模拟/bin.x64')
print(f"客户端路径: {client_path}")

if Path(client_path).exists():
    print(f"✅ 客户端路径存在")
    
    # 检查是否是MiniQMT
    print("\n⚠️  重要：请确认您的QMT是MiniQMT版本！")
    print("\n如何确认：")
    print("  1. 打开QMT客户端")
    print("  2. 点击'帮助' -> '关于'")
    print("  3. 查看版本信息中是否有'MiniQMT'字样")
    print("\n如果不是MiniQMT：")
    print("  - 下载地址: https://xuntou.net/")
    print("  - 或联系国金证券客服获取")
else:
    print(f"❌ 客户端路径不存在: {client_path}")

print()

# 步骤4: 检查账号权限
print("步骤4: 检查账号权限")
print("-" * 80)

sim_account = os.getenv('QMT_SIMULATION_ACCOUNT')
live_account = os.getenv('QMT_LIVE_ACCOUNT')

print(f"模拟账户: {sim_account if sim_account else '未设置'}")
print(f"实盘账户: {live_account if live_account else '未设置'}")

print("\n⚠️  重要：请确认账号已开通API交易权限！")
print("\n如何确认：")
print("  1. 联系国金证券客服: 95310")
print("  2. 询问账号是否开通了QMT API交易权限")
print("  3. 如果没有，申请开通API权限")

print()

# 步骤5: 测试xtquant库
print("步骤5: 测试xtquant库")
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

# 步骤6: 测试数据接口（需要Token）
print("步骤6: 测试数据接口")
print("-" * 80)

if not qmt_token:
    print("⚠️  跳过数据接口测试（缺少Token）")
else:
    try:
        from xtquant import xtdatacenter as xtdc
        
        # 设置Token
        xtdc.set_token(qmt_token)
        print("✅ Token设置成功")
        
        # 初始化行情模块
        xtdc.init()
        print("✅ 行情模块初始化成功")
        
        # 测试获取数据
        from xtquant import xtdata
        data = xtdata.get_full_tick(['000001.SZ'])
        
        if data:
            print("✅ 数据接口测试成功")
            print(f"  获取到 {len(data)} 只股票的行情数据")
        else:
            print("⚠️  数据接口返回空数据")
            
    except Exception as e:
        print(f"❌ 数据接口测试失败: {e}")

print()

# 步骤7: 测试交易接口
print("步骤7: 测试交易接口")
print("-" * 80)

if not sim_account:
    print("⚠️  跳过交易接口测试（缺少账号信息）")
else:
    try:
        from xtquant import xttrader
        
        # 创建交易对象
        session_id = 123456
        trader = xttrader.XtQuantTrader(sim_account, session_id, client_path)
        print("✅ 交易对象创建成功")
        
        # 启动交易线程
        trader.start()
        print("✅ 交易线程启动成功")
        
        # 连接
        print("\n尝试连接交易账户...")
        connect_result = trader.connect()
        
        if connect_result == 0:
            print("✅ 交易接口连接成功！")
            
            # 查询资产
            try:
                asset = trader.query_stock_asset(sim_account)
                if asset:
                    print(f"\n账户资产信息:")
                    print(f"  总资产: {asset.total_asset}")
                    print(f"  可用资金: {asset.cash}")
            except Exception as e:
                print(f"⚠️  查询资产失败: {e}")
                
        else:
            print(f"❌ 交易接口连接失败，返回码: {connect_result}")
            
            if connect_result == -1:
                print("\n返回码 -1 的可能原因：")
                print("  1. QMT客户端未启动或未登录交易账户")
                print("  2. 账号未开通API交易权限")
                print("  3. 使用的不是MiniQMT版本")
                print("  4. Token未设置或无效")
                
    except Exception as e:
        print(f"❌ 交易接口测试失败: {e}")

print()

# 总结
print("=" * 80)
print("测试总结")
print("=" * 80)

print("\n关键问题排查清单：")
print("  [ ] 1. 确认使用的是MiniQMT版本（不是普通版QMT）")
print("  [ ] 2. 获取Token并设置到 .env.qmt 文件中")
print("  [ ] 3. 联系券商确认账号已开通API交易权限")
print("  [ ] 4. 在QMT客户端中手动登录交易账户")

print("\n下一步行动：")
print("  1. 访问 https://xuntou.net/#/userInfo 获取Token")
print("  2. 确认QMT版本是否为MiniQMT")
print("  3. 联系国金证券客服: 95310 确认API权限")
print("  4. 重新运行此测试脚本")

print("\n参考文档：")
print("  - docs/02_FACTOR_LIBRARY/04_DATA_SOURCE/QMT_INTERFACE.md")
print("  - docs/05_IMPLEMENTATION/04_OPERATIONS/improvements/IMP_002_QMT_API_COMMUNITY_RESEARCH.md")
print("  - docs/05_IMPLEMENTATION/04_OPERATIONS/QMT_CONNECTION_TROUBLESHOOTING.md")

print()
