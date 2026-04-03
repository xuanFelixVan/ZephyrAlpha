"""
QMT服务器配置验证脚本

验证用户提供的服务器地址，并检查QMT客户端配置状态
"""

import os
import sys
import socket
import time
from pathlib import Path
from datetime import datetime

print("=" * 80)
print("QMT服务器配置验证")
print("=" * 80)
print(f"验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Python版本: {sys.version[:20]}...")
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

# 获取服务器配置
sim_server = os.getenv('QMT_SIMULATION_SERVER', '180.169.107.19:56001')
live_server = os.getenv('QMT_LIVE_SERVER', 'qmt.gjzq.com.cn:56001')

print("服务器配置:")
print("-" * 80)
print(f"模拟盘服务器: {sim_server}")
print(f"实盘服务器: {live_server}")
print()

# 解析服务器地址
def parse_server(server_str):
    """解析服务器地址为 (host, port)"""
    if ':' in server_str:
        parts = server_str.split(':')
        host = parts[0]
        port = int(parts[1]) if len(parts) > 1 else 56001
        return host, port
    return server_str, 56001

# 测试网络连接
print("网络连接测试:")
print("-" * 80)

def test_connection(host, port, server_name):
    """测试TCP连接"""
    print(f"\n测试 {server_name} ({host}:{port}):")
    
    try:
        # 创建socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # 5秒超时
        
        start_time = time.time()
        result = sock.connect_ex((host, port))
        elapsed = (time.time() - start_time) * 1000  # 毫秒
        
        sock.close()
        
        if result == 0:
            print(f"  ✅ 连接成功 (延迟: {elapsed:.2f}ms)")
            return True
        else:
            print(f"  ❌ 连接失败 (错误码: {result})")
            print(f"     可能原因:")
            print(f"     1. 服务器未启动")
            print(f"     2. 防火墙阻止连接")
            print(f"     3. 网络问题")
            return False
            
    except socket.gaierror:
        print(f"  ❌ 域名解析失败: {host}")
        print(f"     请检查域名是否正确")
        return False
    except socket.timeout:
        print(f"  ⚠️  连接超时 (5秒)")
        print(f"     可能原因:")
        print(f"     1. 服务器响应慢")
        print(f"     2. 网络延迟高")
        return False
    except Exception as e:
        print(f"  ❌ 连接错误: {e}")
        return False

# 测试模拟盘服务器
sim_host, sim_port = parse_server(sim_server)
sim_ok = test_connection(sim_host, sim_port, "模拟盘服务器")

print()

# 测试实盘服务器  
live_host, live_port = parse_server(live_server)
live_ok = test_connection(live_host, live_port, "实盘服务器")

print()

# QMT客户端配置检查
print("QMT客户端配置检查:")
print("-" * 80)

print("\n1. 客户端登录模式检查:")
print("   ✅ 必须使用【极简模式】或【独立交易】登录")
print("   ⚠️  普通登录模式不支持Python API连接")

print("\n2. 服务器配置检查:")
print("   在QMT客户端登录界面，请确认:")
print(f"   - 模拟账户使用的服务器: {sim_server}")
print(f"   - 实盘账户使用的服务器: {live_server}")

print("\n3. 账户权限检查:")
print("   请确认账户已开通【策略交易】权限")
print("   联系国金证券客服确认权限状态")

print("\n4. 防火墙检查:")
print("   请确保防火墙允许以下程序:")
print("   - QMT客户端 (Qmt.exe)")
print("   - Python解释器 (python.exe)")
print("   - 端口 56001 的TCP连接")

# 总结和建议
print("\n" + "=" * 80)
print("验证总结与建议")
print("=" * 80)

if sim_ok and live_ok:
    print("\n✅ 两个服务器均可连接")
    print("   网络连接正常，问题可能在客户端配置")
else:
    print("\n⚠️  服务器连接存在问题")
    if not sim_ok:
        print(f"   - 模拟盘服务器 {sim_server} 连接失败")
    if not live_ok:
        print(f"   - 实盘服务器 {live_server} 连接失败")

print("\n📋 立即行动:")
print("   1. 检查QMT客户端登录模式 (必须勾选【极简模式】)")
print("   2. 验证QMT客户端中的服务器配置")
print("   3. 确认账户策略交易权限")
print("   4. 检查防火墙设置")

print("\n🔧 诊断命令:")
print("   # 重新运行连接测试")
print("   C:\\Users\\fanzi\\.conda\\envs\\qmt\\python.exe scripts\\test_qmt_connection_v6.py")
print()
print("   # 检查客户端文件")
print("   ls 'E:\\国金QMT交易端模拟\\userdata_mini\\up_queue_xtquant'")
print()

print("=" * 80)
print("完成")
print("=" * 80)