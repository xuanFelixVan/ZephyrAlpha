# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
QMT环境验证脚本 - 验证Python 3.12环境和xtquant配置
"""

import sys
import os
from pathlib import Path
from datetime import datetime

print("=" * 80)
print("QMT环境验证脚本")
print("=" * 80)
print(f"验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 检查1: Python版本
print("检查1: Python版本")
print("-" * 80)
print(f"Python版本: {sys.version}")
print(f"Python路径: {sys.executable}")

version_info = sys.version_info
print(f"\n版本详情:")
print(f"  主版本: {version_info.major}")
print(f"  次版本: {version_info.minor}")
print(f"  微版本: {version_info.micro}")
print(f"  架构: {'64位' if sys.maxsize > 2**32 else '32位'}")

if version_info.major == 3 and version_info.minor == 12:
    print("\n✅ Python版本正确: Python 3.12.x")
elif version_info.major == 3 and 6 <= version_info.minor <= 11:
    print(f"\n✅ Python版本兼容: Python 3.{version_info.minor}.x")
else:
    print(f"\n❌ Python版本不兼容: Python {version_info.major}.{version_info.minor}.x")
    print("   官方支持: Python 3.6 - 3.12 (64位)")

print()

# 检查2: 必要的库
print("检查2: 必要的库")
print("-" * 80)

required_packages = {
    'xtquant': 'xtquant',
    'pandas': 'pandas',
    'numpy': 'numpy'
}

for package_name, import_name in required_packages.items():
    try:
        module = __import__(import_name)
        version = getattr(module, '__version__', '未知版本')
        print(f"✅ {package_name}: {version}")
    except ImportError:
        print(f"❌ {package_name}: 未安装")

print()

# 检查3: xtquant模块完整性
print("检查3: xtquant模块完整性")
print("-" * 80)

try:
    # 检查xtdata
    from xtquant import xtdata
    print("✅ xtdata模块可用")
    
    # 检查xttrader
    from xtquant.xttrader import XtQuantTrader
    print("✅ XtQuantTrader类可用")
    
    # 检查XtAccount（这是之前失败的关键）
    try:
        from xtquant.xttrader import XtAccount
        print("✅ XtAccount类可用")
    except ImportError:
        print("⚠️  XtAccount类不可用（可能使用其他账户配置方式）")
    
    # 检查xtquant版本
    try:
        import xtquant
        if hasattr(xtquant, '__version__'):
            print(f"✅ xtquant版本: {xtquant.__version__}")
        else:
            print("✅ xtquant已安装（版本信息不可用）")
    except:
        pass
        
except ImportError as e:
    print(f"❌ xtquant模块导入失败: {e}")

print()

# 检查4: 环境变量配置
print("检查4: 环境变量配置")
print("-" * 80)

env_path = Path(".env.qmt")
if env_path.exists():
    print("✅ .env.qmt文件存在")
    
    with open(env_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    config = {}
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            config[key.strip()] = value.strip()
    
    print("\n配置信息:")
    for key in ['QMT_SIMULATION_ACCOUNT', 'QMT_LIVE_ACCOUNT']:
        if key in config:
            print(f"  {key}: {config[key]}")
    
    print("\n路径配置:")
    for key in ['QMT_SIMULATION_CLIENT_PATH', 'QMT_LIVE_CLIENT_PATH']:
        if key in config:
            path = Path(config[key])
            exists = "✅ 存在" if path.exists() else "❌ 不存在"
            print(f"  {key}: {exists}")
            print(f"    {config[key]}")
else:
    print("❌ .env.qmt文件不存在")

print()

# 检查5: QMT客户端状态（快速检查）
print("检查5: QMT客户端状态")
print("-" * 80)

try:
    import psutil
    
    qmt_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            if proc.info['exe'] and 'QMT' in proc.info['exe']:
                qmt_processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    if qmt_processes:
        print(f"✅ 找到 {len(qmt_processes)} 个QMT进程")
        for proc in qmt_processes:
            print(f"  PID: {proc['pid']}, 名称: {proc['name']}")
    else:
        print("⚠️  未找到QMT进程")
        print("   请确保QMT客户端已启动并登录")
        
except ImportError:
    print("⚠️  psutil库未安装，无法检查进程")
    print("   安装命令: pip install psutil")

print()

# 总结
print("=" * 80)
print("验证总结")
print("=" * 80)

checks = []

# Python版本检查
if version_info.major == 3 and 6 <= version_info.minor <= 12:
    checks.append(("Python版本", True))
else:
    checks.append(("Python版本", False))

# 架构检查
is_64bit = sys.maxsize > 2**32
checks.append(("64位架构", is_64bit))

# xtquant检查
try:
    from xtquant import xtdata
    from xtquant.xttrader import XtQuantTrader
    checks.append(("xtquant库", True))
except:
    checks.append(("xtquant库", False))

# 配置文件检查
checks.append(("配置文件", env_path.exists()))

print("\n检查结果:")
for name, passed in checks:
    status = "✅" if passed else "❌"
    print(f"  {status} {name}")

all_passed = all(passed for _, passed in checks)

print()
if all_passed:
    print("🎉 所有检查通过！环境配置正确。")
    print("\n下一步：")
    print("  1. 确保QMT客户端已启动")
    print("  2. 在登录时勾选【极简模式】或【独立交易】")
    print("  3. 运行测试脚本: python scripts/test_qmt_connection_v4.py")
else:
    print("⚠️  部分检查未通过，请根据上述提示修复。")

print()
