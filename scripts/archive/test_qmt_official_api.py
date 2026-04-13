#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
"""
QMT官方API连接测试
严格按照官方文档示例进行测试
"""

import sys
import os
from pathlib import Path

def test_official_api():
    """测试官方API连接方式"""
    
    print("=" * 70)
    print("QMT官方API连接测试")
    print("=" * 70)
    
    # 加载环境变量
    env_path = Path(".env.qmt")
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
    
    account = os.getenv('QMT_SIMULATION_ACCOUNT')
    password = os.getenv('QMT_SIMULATION_PASSWORD')
    
    print(f"\n测试账户: {account}")
    print(f"客户端路径: E:/国金QMT交易端模拟/bin.x64\n")
    
    # 测试1: 按照官方文档示例
    print("测试1: 官方文档示例方式")
    print("-" * 70)
    
    try:
        from xtquant.xttrader import XtQuantTrader
        
        # 官方示例：创建交易对象
        session_id = 123456  # 官方示例使用的固定session_id
        client_path = "E:/国金QMT交易端模拟/bin.x64"
        
        print(f"步骤1: 创建XtQuantTrader对象")
        print(f"  account={account}")
        print(f"  session_id={session_id}")
        print(f"  client_path={client_path}")
        
        trader = XtQuantTrader(account, session_id, client_path)
        print(f"✅ 对象创建成功")
        
        # 启动交易线程
        print(f"\n步骤2: 启动交易线程")
        trader.start()
        print(f"✅ 交易线程启动成功")
        
        # 连接
        print(f"\n步骤3: 连接交易账户")
        connect_result = trader.connect()
        print(f"连接结果: {connect_result}")
        
        if connect_result == 0:
            print(f"✅ 连接成功！")
            
            # 订阅账户
            print(f"\n步骤4: 订阅账户")
            trader.subscribe_account(account)
            print(f"✅ 账户订阅成功")
            
            # 查询资产
            print(f"\n步骤5: 查询账户资产")
            try:
                asset = trader.query_stock_asset(account)
                print(f"✅ 资产查询成功")
                print(f"  总资产: {asset.total_asset:.2f}")
                print(f"  可用资金: {asset.cash:.2f}")
                print(f"  市值: {asset.market_value:.2f}")
                print(f"  冻结资金: {asset.frozen_cash:.2f}")
            except Exception as e:
                print(f"❌ 资产查询失败: {e}")
            
            # 查询持仓
            print(f"\n步骤6: 查询持仓")
            try:
                positions = trader.query_stock_positions(account)
                print(f"✅ 持仓查询成功")
                print(f"  持仓数量: {len(positions) if positions else 0}")
                if positions:
                    for pos in positions[:3]:
                        print(f"    {pos.stock_code}: {pos.volume}股")
            except Exception as e:
                print(f"❌ 持仓查询失败: {e}")
            
            # 断开连接
            print(f"\n步骤7: 断开连接")
            trader.disconnect()
            print(f"✅ 已断开连接")
            
        else:
            print(f"❌ 连接失败，返回码: {connect_result}")
            print(f"\n错误码说明:")
            print(f"  -1: 通用错误（通常是未登录或权限问题）")
            print(f"  -2: 网络错误")
            print(f"  -3: 账号或密码错误")
            
            print(f"\n可能的原因:")
            print(f"  1. QMT客户端未登录交易账户")
            print(f"  2. 账号密码错误")
            print(f"  3. API交易权限未开通")
            print(f"  4. QMT客户端版本不支持API")
            
            print(f"\n建议操作:")
            print(f"  1. 在QMT客户端中检查交易账户登录状态")
            print(f"  2. 确认账号密码正确")
            print(f"  3. 联系券商确认API权限")
            print(f"  4. 查看QMT客户端日志文件")
            
    except Exception as e:
        print(f"❌ 异常: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试2: 检查QMT客户端日志
    print("\n" + "=" * 70)
    print("测试2: 检查QMT客户端日志")
    print("-" * 70)
    
    log_path = Path("E:/国金QMT交易端模拟/userdata_mini/logs")
    if log_path.exists():
        print(f"日志目录: {log_path}")
        print(f"\n最新的日志文件:")
        
        log_files = sorted(log_path.glob("*.log"), key=lambda x: x.stat().st_mtime, reverse=True)
        if log_files:
            latest_log = log_files[0]
            print(f"  {latest_log.name}")
            
            # 读取最后几行
            try:
                with open(latest_log, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    print(f"\n最后10行日志:")
                    for line in lines[-10:]:
                        print(f"  {line.rstrip()}")
            except Exception as e:
                print(f"  读取日志失败: {e}")
    else:
        print(f"日志目录不存在: {log_path}")
    
    print("\n" + "=" * 70)
    print("总结")
    print("=" * 70)
    print("""
如果连接仍然失败，请按以下步骤操作:

1. 确认QMT客户端登录状态
   - 打开QMT客户端
   - 点击菜单栏"交易" -> "登录交易账户"
   - 确认账号已登录且状态为"已连接"
   - 截图登录状态

2. 检查API权限
   - 联系国金证券客服
   - 询问是否开通QMT API交易权限
   - 确认账号支持程序化交易

3. 查看客户端日志
   - 打开日志文件查看详细错误信息
   - 搜索关键词: "error", "fail", "connect"

4. 尝试其他账号
   - 如果有其他QMT账号，尝试使用其他账号测试
   - 确认是否为账号特定问题

5. 联系技术支持
   - 国金证券QMT技术支持
   - 提供错误码和日志文件
""")
    
    print("=" * 70)


if __name__ == "__main__":
    test_official_api()
