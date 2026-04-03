"""
QMT Python环境配置指南

问题：Python 3.13不兼容xtquant库
解决：创建Python 3.12虚拟环境
"""

print("=" * 80)
print("QMT Python环境配置指南")
print("=" * 80)

print("\n❌ 当前问题：")
print("  - Python版本: 3.13.12")
print("  - xtquant支持: Python 3.6 - 3.12 (64位)")
print("  - 结果: API导入失败，连接返回-1")

print("\n✅ 解决方案：创建Python 3.12虚拟环境")

print("\n" + "=" * 80)
print("方案1: 使用conda创建环境（推荐）")
print("=" * 80)

print("\n步骤1: 创建Python 3.12环境")
print("  conda create -n qmt python=3.12 -y")

print("\n步骤2: 激活环境")
print("  conda activate qmt")

print("\n步骤3: 安装依赖")
print("  pip install xtquant")
print("  pip install pandas numpy")

print("\n步骤4: 验证安装")
print("  python -c \"import xtquant; print('✅ xtquant安装成功')\"")

print("\n" + "=" * 80)
print("方案2: 使用venv创建环境")
print("=" * 80)

print("\n前提：需要先安装Python 3.12")

print("\n步骤1: 下载Python 3.12")
print("  访问: https://www.python.org/downloads/")
print("  下载: Python 3.12.x (64位)")

print("\n步骤2: 创建虚拟环境")
print("  py -3.12 -m venv qmt_env")

print("\n步骤3: 激活环境")
print("  Windows: qmt_env\\Scripts\\activate")
print("  Linux/Mac: source qmt_env/bin/activate")

print("\n步骤4: 安装依赖")
print("  pip install xtquant pandas numpy")

print("\n" + "=" * 80)
print("验证环境配置")
print("=" * 80)

print("\n运行以下命令验证：")
print("  python --version")
print("  # 应该显示: Python 3.12.x")
print()
print("  python -c \"import sys; print(f'Python {sys.version}')\"")
print("  python -c \"import xtquant; print('✅ xtquant可用')\"")

print("\n" + "=" * 80)
print("配置完成后重新测试")
print("=" * 80)

print("\n1. 激活qmt环境")
print("   conda activate qmt")

print("\n2. 运行测试脚本")
print("   python scripts/test_qmt_connection_v4.py")

print("\n" + "=" * 80)
print("重要提示")
print("=" * 80)

print("\n⚠️  Python版本必须是64位！")
print("  - ✅ Python 3.12.0 (64-bit)")
print("  - ❌ Python 3.12.0 (32-bit)")

print("\n⚠️  确保QMT客户端已启动并登录")
print("  - 登录时勾选【极简模式】或【独立交易】")
print("  - 路径配置为 userdata_mini 文件夹")

print()
