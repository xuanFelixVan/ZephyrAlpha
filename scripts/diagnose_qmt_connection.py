#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
"""
QMT连接问题诊断脚本
详细诊断连接失败的原因
"""

import sys
import os
from pathlib import Path
from datetime import datetime

def diagnose_qmt_connection():
    """诊断QMT连接问题"""
    
    print("=" * 70)
    print("QMT连接问题诊断")
    print("=" * 70)
    print(f"诊断时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 1. 检查环境变量
    print("步骤1: 检查环境变量")
    print("-" * 70)
    
    sim_account = os.getenv('QMT_SIMULATION_ACCOUNT')
    sim_password = os.getenv('QMT_SIMULATION_PASSWORD')
    live_account = os.getenv('QMT_LIVE_ACCOUNT')
    live_password = os.getenv('QMT_LIVE_PASSWORD')
    
    print(f"模拟账户: {sim_account if sim_account else '未设置'}")
    print(f"模拟密码: {'***' if sim_password else '未设置'}")
    print(f"实盘账户: {live_account if live_account else '未设置'}")
    print(f"实盘密码: {'***' if live_password else '未设置'}")
    print()
    
    # 2. 检查QMT客户端路径
    print("步骤2: 检查QMT客户端路径")
    print("-" * 70)
    
    possible_paths = [
        "E:/国金QMT交易端模拟/bin.x64",
        "E:/国金QMT交易端实盘/bin.x64",
        "C:/国金证券/QMT/bin.x64",
        "D:/国金证券/QMT/bin.x64",
    ]
    
    found_paths = []
    for path in possible_paths:
        if Path(path).exists():
            found_paths.append(path)
            print(f"✅ 找到: {path}")
        else:
            print(f"❌ 不存在: {path}")
    print()
    
    if not found_paths:
        print("⚠️  警告: 未找到QMT客户端路径，请手动配置")
        print()
    
    # 3. 测试xtdata连接
    print("步骤3: 测试xtdata数据连接")
    print("-" * 70)
    
    try:
        from xtquant import xtdata
        
        # 尝试获取数据
        data = xtdata.get_full_tick(["000001.SZ"])
        if data and "000001.SZ" in data:
            print("✅ xtdata数据连接正常")
            print(f"   成功获取000001.SZ行情")
        else:
            print("❌ xtdata数据连接失败")
    except Exception as e:
        print(f"❌ xtdata连接异常: {e}")
    print()
    
    # 4. 测试xttrader连接（多种方式）
    print("步骤4: 测试xttrader交易连接")
    print("-" * 70)
    
    try:
        from xtquant.xttrader import XtQuantTrader
        
        # 方式1: 基本连接
        print("\n方式1: 基本连接测试")
        print("-" * 40)
        
        if sim_account and sim_password:
            session_id = int(datetime.now().timestamp())
            
            print(f"  创建会话: session_id={session_id}")
            print(f"  账号: {sim_account}")
            
            trader = XtQuantTrader(sim_account, session_id)
            print(f"  ✅ XtQuantTrader对象创建成功")
            
            # 启动交易线程
            print(f"  启动交易线程...")
            trader.start()
            print(f"  ✅ 交易线程启动成功")
            
            # 尝试连接
            print(f"  尝试连接...")
            result = trader.connect()
            print(f"  连接结果: {result}")
            
            if result == 0:
                print(f"  ✅ 连接成功！")
                
                # 查询账户资产
                try:
                    asset = trader.query_stock_asset(sim_account)
                    print(f"\n  账户资产信息:")
                    print(f"    总资产: {asset.total_asset:.2f}")
                    print(f"    可用资金: {asset.cash:.2f}")
                    print(f"    市值: {asset.market_value:.2f}")
                except Exception as e:
                    print(f"  ❌ 查询账户资产失败: {e}")
                
                # 断开连接
                trader.disconnect()
                print(f"\n  ✅ 已断开连接")
                
            else:
                print(f"  ❌ 连接失败，返回码: {result}")
                print(f"\n  可能的原因:")
                print(f"    1. QMT客户端未正确登录交易账户")
                print(f"    2. 账号密码错误")
                print(f"    3. 账户权限问题")
                print(f"    4. QMT客户端版本不兼容")
                print(f"\n  建议操作:")
                print(f"    1. 在QMT客户端中重新登录交易账户")
                print(f"    2. 检查账号密码是否正确")
                print(f"    3. 查看QMT客户端的交易日志")
                print(f"    4. 尝试重启QMT客户端")
        else:
            print("  ⚠️  未配置模拟账户信息，跳过测试")
        
        # 方式2: 指定客户端路径
        if found_paths:
            print("\n方式2: 指定客户端路径测试")
            print("-" * 40)
            
            for client_path in found_paths:
                print(f"\n  尝试路径: {client_path}")
                
                try:
                    session_id = int(datetime.now().timestamp()) + 1
                    
                    trader2 = XtQuantTrader(sim_account, session_id, client_path)
                    print(f"  ✅ XtQuantTrader对象创建成功（指定路径）")
                    
                    trader2.start()
                    print(f"  ✅ 交易线程启动成功")
                    
                    result = trader2.connect()
                    print(f"  连接结果: {result}")
                    
                    if result == 0:
                        print(f"  ✅ 连接成功！")
                        trader2.disconnect()
                        break
                    else:
                        print(f"  ❌ 连接失败，返回码: {result}")
                        
                except Exception as e:
                    print(f"  ❌ 异常: {e}")
        
    except ImportError as e:
        print(f"❌ xttrader导入失败: {e}")
    except Exception as e:
        print(f"❌ xttrader测试异常: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    
    # 5. 检查QMT客户端状态
    print("步骤5: QMT客户端状态检查")
    print("-" * 70)
    print("请手动检查以下项目:")
    print("  □ QMT客户端是否已启动")
    print("  □ 是否已登录行情服务")
    print("  □ 是否已登录交易账户（模拟/实盘）")
    print("  □ 交易账户登录状态是否显示'已连接'")
    print("  □ 是否有错误提示或弹窗")
    print()
    
    # 6. 提供解决方案
    print("=" * 70)
    print("诊断建议")
    print("=" * 70)
    print("""
根据诊断结果，建议按以下步骤操作:

1. 确认QMT客户端登录状态
   - 打开QMT客户端
   - 检查"交易"菜单下的账户登录状态
   - 确保模拟账户和实盘账户都显示"已连接"

2. 检查账号密码
   - 确认.env.qmt文件中的账号密码正确
   - 注意区分模拟账户和实盘账户

3. 检查QMT客户端版本
   - 确保使用的是支持API交易的版本
   - 联系券商确认API权限已开通

4. 查看QMT客户端日志
   - 位置: QMT安装目录/userdata_mini/logs/
   - 查看最新的日志文件，搜索"error"或"fail"

5. 尝试重启
   - 关闭QMT客户端
   - 重新启动QMT客户端
   - 先登录行情服务，再登录交易账户
   - 等待1-2分钟后再次运行测试

6. 联系券商技术支持
   - 如果以上步骤都无法解决，联系国金证券技术支持
   - 提供错误码: -1
   - 询问API交易权限是否已开通
""")
    
    print("=" * 70)


if __name__ == "__main__":
    # 加载环境变量
    env_path = Path(".env.qmt")
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
    
    diagnose_qmt_connection()
