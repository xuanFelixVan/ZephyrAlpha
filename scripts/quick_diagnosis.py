"""
快速环境诊断 - 确认Python环境状态
"""

import sys
import os
import subprocess
from pathlib import Path

print("=" * 80)
print("快速环境诊断")
print("=" * 80)
print()

# 1. 当前Python版本
print("1. 当前Python版本")
print("-" * 80)
print(f"Python版本: {sys.version}")
print(f"Python路径: {sys.executable}")
print(f"架构: {'64位' if sys.maxsize > 2**32 else '32位'}")
print()

# 2. 检查conda
print("2. 检查conda")
print("-" * 80)
try:
    result = subprocess.run(['conda', '--version'], capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        print(f"✅ conda已安装: {result.stdout.strip()}")
        
        # 列出环境
        result = subprocess.run(['conda', 'env', 'list'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("\nconda环境列表:")
            print(result.stdout)
    else:
        print("❌ conda未正确安装")
except FileNotFoundError:
    print("❌ conda未安装")
except Exception as e:
    print(f"⚠️  conda检查失败: {e}")
print()

# 3. 检查py启动器
print("3. 检查py启动器")
print("-" * 80)
try:
    result = subprocess.run(['py', '-0'], capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        print("✅ py启动器可用")
        print("\n已安装的Python版本:")
        print(result.stdout)
    else:
        print("❌ py启动器不可用")
except FileNotFoundError:
    print("❌ py启动器未安装")
except Exception as e:
    print(f"⚠️  py启动器检查失败: {e}")
print()

# 4. 检查where python
print("4. 检查Python安装位置")
print("-" * 80)
try:
    result = subprocess.run(['where', 'python'], capture_output=True, text=True, timeout=5)
    if result.returncode == 0 and result.stdout.strip():
        print("Python安装位置:")
        for line in result.stdout.strip().split('\n'):
            print(f"  {line}")
    else:
        print("⚠️  未找到Python安装位置")
except Exception as e:
    print(f"⚠️  检查失败: {e}")
print()

# 5. 检查虚拟环境
print("5. 检查虚拟环境")
print("-" * 80)
print("检查当前目录下的虚拟环境...")

venv_dirs = []
for venv_name in ['qmt_env', 'venv', '.venv', 'env']:
    venv_path = Path(venv_name)
    if venv_path.exists():
        activate_script = venv_path / 'Scripts' / 'activate.bat'
        if activate_script.exists():
            venv_dirs.append(venv_name)
            print(f"✅ 找到虚拟环境: {venv_name}")
            print(f"   激活命令: {venv_name}\\Scripts\\activate.bat")

if not venv_dirs:
    print("⚠️  当前目录下未找到虚拟环境")

print()

# 6. 总结和建议
print("=" * 80)
print("诊断总结")
print("=" * 80)

print(f"\n当前Python版本: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

if sys.version_info.major == 3 and sys.version_info.minor == 12:
    print("✅ Python版本正确！")
    print("\n下一步：")
    print("  1. 确保QMT客户端已启动并登录（极简模式）")
    print("  2. 运行测试: python scripts/test_qmt_connection_v4.py")
elif sys.version_info.major == 3 and 6 <= sys.version_info.minor <= 11:
    print("✅ Python版本兼容！")
    print("\n下一步：")
    print("  1. 确保QMT客户端已启动并登录（极简模式）")
    print("  2. 运行测试: python scripts/test_qmt_connection_v4.py")
else:
    print("❌ Python版本不兼容，需要Python 3.6 - 3.12")
    print("\n建议：")
    
    try:
        result = subprocess.run(['conda', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("  ✅ 您已安装conda，可以创建Python 3.12环境：")
            print("     conda create -n qmt python=3.12 -y")
            print("     conda activate qmt")
            print("     pip install xtquant pandas numpy")
        else:
            print("  方案1: 安装Miniconda")
            print("    访问: https://docs.conda.io/en/latest/miniconda.html")
            print("  方案2: 安装Python 3.12")
            print("    访问: https://www.python.org/downloads/")
    except:
        print("  方案1: 安装Miniconda")
        print("    访问: https://docs.conda.io/en/latest/miniconda.html")
        print("  方案2: 安装Python 3.12")
        print("    访问: https://www.python.org/downloads/")

print()
