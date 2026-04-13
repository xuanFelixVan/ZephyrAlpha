# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
QMT Python 3.12环境配置完整指南

问题：当前使用Python 3.13，需要切换到Python 3.12
"""

print("=" * 80)
print("QMT Python 3.12环境配置指南")
print("=" * 80)

print("\n当前状态：")
print("  ❌ Python版本: 3.13.12 (不兼容)")
print("  ✅ xtquant库: 已安装")
print("  ⚠️  XtAccount类: 不可用（Python版本问题）")

print("\n" + "=" * 80)
print("解决方案")
print("=" * 80)

print("\n方案1: 安装Miniconda（推荐）")
print("-" * 80)

print("\n步骤1: 下载Miniconda")
print("  访问: https://docs.conda.io/en/latest/miniconda.html")
print("  下载: Miniconda3 Windows 64-bit")
print("  文件名: Miniconda3-latest-Windows-x86_64.exe")

print("\n步骤2: 安装Miniconda")
print("  1. 双击运行安装程序")
print("  2. 选择 'Just Me (recommended)'")
print("  3. 选择安装路径（建议默认）")
print("  4. ✅ 勾选 'Add Miniconda3 to my PATH environment variable'")
print("  5. 点击 Install")

print("\n步骤3: 重启终端")
print("  关闭当前终端，重新打开")

print("\n步骤4: 创建Python 3.12环境")
print("  conda create -n qmt python=3.12 -y")

print("\n步骤5: 激活环境")
print("  conda activate qmt")

print("\n步骤6: 安装依赖")
print("  pip install xtquant pandas numpy")

print("\n步骤7: 验证安装")
print("  python --version")
print("  # 应显示: Python 3.12.x")

print("\n" + "=" * 80)
print("方案2: 安装Python 3.12（独立安装）")
print("-" * 80)

print("\n步骤1: 下载Python 3.12")
print("  访问: https://www.python.org/downloads/")
print("  下载: Python 3.12.x (64-bit)")
print("  文件名: python-3.12.x-amd64.exe")

print("\n步骤2: 安装Python 3.12")
print("  1. 双击运行安装程序")
print("  2. ✅ 勾选 'Add Python 3.12 to PATH'")
print("  3. 选择 'Install Now'")

print("\n步骤3: 创建虚拟环境")
print("  # 使用Python 3.12创建虚拟环境")
print("  py -3.12 -m venv qmt_env")

print("\n步骤4: 激活虚拟环境")
print("  # Windows PowerShell")
print("  qmt_env\\Scripts\\Activate.ps1")
print("  ")
print("  # Windows CMD")
print("  qmt_env\\Scripts\\activate.bat")

print("\n步骤5: 安装依赖")
print("  pip install xtquant pandas numpy")

print("\n步骤6: 验证安装")
print("  python --version")
print("  # 应显示: Python 3.12.x")

print("\n" + "=" * 80)
print("方案3: 使用已有的Python 3.12环境")
print("-" * 80)

print("\n如果您已经创建了Python 3.12环境，请：")

print("\n对于conda环境：")
print("  1. 打开Anaconda Prompt")
print("  2. 激活环境: conda activate qmt")
print("  3. 验证版本: python --version")
print("  4. 运行测试: python scripts/test_qmt_connection_v4.py")

print("\n对于venv环境：")
print("  1. 激活环境: qmt_env\\Scripts\\Activate.ps1")
print("  2. 验证版本: python --version")
print("  3. 运行测试: python scripts/test_qmt_connection_v4.py")

print("\n" + "=" * 80)
print("验证环境配置")
print("=" * 80)

print("\n运行以下命令验证环境：")
print("  python scripts/verify_qmt_environment.py")

print("\n预期结果：")
print("  ✅ Python版本: 3.12.x")
print("  ✅ 64位架构")
print("  ✅ xtquant库可用")
print("  ✅ XtAccount类可用")

print("\n" + "=" * 80)
print("测试QMT连接")
print("=" * 80)

print("\n环境配置完成后：")
print("  1. 启动QMT客户端")
print("  2. 登录时勾选【极简模式】或【独立交易】")
print("  3. 运行测试: python scripts/test_qmt_connection_v4.py")

print("\n预期结果：")
print("  ✅ 数据接口连接成功")
print("  ✅ 交易接口连接成功")
print("  ✅ 账户订阅成功")

print("\n" + "=" * 80)
print("常见问题")
print("=" * 80)

print("\nQ: 如何知道我是否安装了conda？")
print("A: 在终端运行: conda --version")
print("   如果显示版本号，说明已安装")

print("\nQ: 如何知道我有哪些Python版本？")
print("A: 在终端运行: py -0")
print("   或运行: where python")

print("\nQ: 如何切换Python版本？")
print("A: 使用conda环境: conda activate qmt")
print("   或使用venv环境: qmt_env\\Scripts\\Activate.ps1")

print("\nQ: 为什么XtAccount类不可用？")
print("A: 因为Python 3.13不兼容xtquant库")
print("   需要使用Python 3.6 - 3.12")

print("\n" + "=" * 80)
print("需要帮助？")
print("=" * 80)

print("\n如果遇到问题，请提供以下信息：")
print("  1. conda --version 的输出")
print("  2. python --version 的输出")
print("  3. where python 的输出")
print("  4. 是否安装了Anaconda或Miniconda")

print()
