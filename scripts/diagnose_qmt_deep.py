# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
QMT连接问题深度诊断 - 检查所有可能的原因

根据官方文档，返回码-1的可能原因：
1. ✅ 客户端未以极简模式登录
2. ✅ 路径不正确
3. ✅ C盘权限问题
4. ✅ 账号没有策略交易权限（已排除）
5. ⚠️ Session冲突
6. ⚠️ 客户端未正确登录交易账户
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime

print("=" * 80)
print("QMT连接问题深度诊断")
print("=" * 80)
print(f"诊断时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 加载环境变量
env_path = Path(".env.qmt")
if env_path.exists():
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

# 检查1: Session冲突
print("检查1: Session冲突检查")
print("-" * 80)

print("\n⚠️  重要提示：")
print("根据官方文档：")
print("  '同一个session的两次python进程connect之间必须超过3秒钟'")
print("\n如果您刚刚运行过连接测试，请等待至少5秒后再试！")

print("\n建议：使用不同的session_id")
print("  当前时间戳session:", int(time.time()))
print("  建议session范围: 100000 - 999999")

print()

# 检查2: 客户端登录状态
print("检查2: 客户端登录状态检查")
print("-" * 80)

print("\n请确认以下信息：")
print("  1. QMT客户端是否已启动？")
print("  2. 是否在登录时勾选了【极简模式】或【独立交易】？")
print("  3. 登录的账号是否与配置文件一致？")
print(f"     配置的模拟账户: {os.getenv('QMT_SIMULATION_ACCOUNT')}")
print(f"     配置的实盘账户: {os.getenv('QMT_LIVE_ACCOUNT')}")

print("\n⚠️  关键检查：")
print("  在QMT登录界面，确认勾选了以下选项之一：")
print("  ☑️ 极简模式")
print("  或 ☑️ 独立交易")

print()

# 检查3: 路径格式
print("检查3: 路径格式检查")
print("-" * 80)

client_path = os.getenv('QMT_SIMULATION_CLIENT_PATH', 'E:/国金QMT交易端模拟/bin.x64')
print(f"配置的路径: {client_path}")

# 检查路径格式
if 'bin.x64' in client_path:
    print("⚠️  路径格式可能不正确！")
    print("\n根据官方文档，路径应该指向 userdata_mini 文件夹：")
    
    # 转换路径
    if '/bin.x64' in client_path:
        correct_path = client_path.replace('/bin.x64', '/userdata_mini')
    elif '\\bin.x64' in client_path:
        correct_path = client_path.replace('\\bin.x64', '\\userdata_mini')
    else:
        correct_path = client_path
    
    print(f"\n当前路径: {client_path}")
    print(f"建议路径: {correct_path}")
    
    print("\n⚠️  这是连接失败的可能原因！")
    print("请更新 .env.qmt 文件中的路径：")
    print(f"  QMT_SIMULATION_CLIENT_PATH={correct_path}")
else:
    print("✅ 路径格式正确")

print()

# 检查4: Python版本
print("检查4: Python版本检查")
print("-" * 80)

import sys
print(f"Python版本: {sys.version}")

if sys.version_info.major == 3 and sys.version_info.minor in [6, 7, 8, 9, 10, 11, 12]:
    print("✅ Python版本符合要求（3.6-3.12）")
else:
    print("⚠️  Python版本可能不兼容")
    print("  官方支持的版本: Python 3.6 - 3.12 (64位)")

print()

# 检查5: xtquant版本
print("检查5: xtquant库检查")
print("-" * 80)

try:
    import xtquant
    print(f"✅ xtquant已安装")
    print(f"  版本: {xtquant.__version__ if hasattr(xtquant, '__version__') else '未知'}")
except ImportError:
    print("❌ xtquant未安装")

print()

# 总结和建议
print("=" * 80)
print("诊断总结与建议")
print("=" * 80)

print("\n🔴 最可能的原因：路径格式不正确")
print("\n根据官方文档：")
print("  'miniqmt：路径指定到安装目录下\\userdata_mini文件夹'")
print("\n您当前的路径：")
print(f"  {client_path}")
print("\n应该改为：")
print(f"  {client_path.replace('/bin.x64', '/userdata_mini').replace(chr(92)+'bin.x64', chr(92)+'userdata_mini')}")

print("\n\n📋 立即行动：")
print("  1. 编辑 .env.qmt 文件")
print("  2. 将路径从 bin.x64 改为 userdata_mini")
print("  3. 保存文件")
print("  4. 重新运行测试脚本")

print("\n\n📝 示例配置：")
print("  QMT_SIMULATION_CLIENT_PATH=E:/国金QMT交易端模拟/userdata_mini")
print("  QMT_LIVE_CLIENT_PATH=E:/国金QMT交易端实盘/userdata_mini")

print()
