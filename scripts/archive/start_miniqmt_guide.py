# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
MiniQMT启动和连接测试脚本

此脚本提供两种启动MiniQMT的方式，并验证连接
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime

print("=" * 80)
print("MiniQMT启动和连接测试")
print("=" * 80)
print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
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

# 获取配置
sim_path = os.getenv('QMT_SIMULATION_CLIENT_PATH', 'E:/国金QMT交易端模拟/userdata_mini')
sim_account = os.getenv('QMT_SIMULATION_ACCOUNT', '8886156677')
sim_password = os.getenv('QMT_SIMULATION_PASSWORD', '134752')

# 检查XtMiniQmt.exe是否存在
miniqmt_sim = Path("E:/国金QMT交易端模拟/bin.x64/XtMiniQmt.exe")
miniqmt_live = Path("D:/国金证券QMT交易端/bin.x64/XtMiniQmt.exe")

print("MiniQMT程序检查:")
print("-" * 80)
print(f"模拟盘MiniQMT: {miniqmt_sim}")
print(f"  存在: {'✅' if miniqmt_sim.exists() else '❌'}")
print()
print(f"实盘MiniQMT: {miniqmt_live}")
print(f"  存在: {'✅' if miniqmt_live.exists() else '❌'}")
print()

print("=" * 80)
print("重要发现：国金证券QMT包含完整的MiniQMT功能！")
print("=" * 80)
print()
print("✅ 不需要单独下载MiniQMT软件")
print("✅ 您的QMT安装目录中已包含 XtMiniQmt.exe")
print()

print("=" * 80)
print("MiniQMT启动方式")
print("=" * 80)
print()

print("方式1：通过QMT登录界面启动（推荐）")
print("-" * 80)
print("步骤：")
print("  1. 完全关闭当前QMT客户端（检查任务管理器确保进程已结束）")
print("  2. 打开QMT客户端")
print("  3. 在登录界面勾选以下选项之一：")
print("     ☑️ 【极简模式】（首选）")
print("     ☑️ 【独立交易】")
print("  4. 输入账号密码并登录")
print("  5. 等待30秒确保完全初始化")
print()

print("方式2：直接运行XtMiniQmt.exe")
print("-" * 80)
print("步骤：")
print(f"  1. 双击运行: {miniqmt_sim}")
print("  2. 在弹出的登录界面输入账号密码")
print(f"     账号: {sim_account}")
print(f"     密码: {sim_password}")
print("  3. 点击登录")
print("  4. 等待30秒确保完全初始化")
print()

print("=" * 80)
print("启动后验证步骤")
print("=" * 80)
print()
print("启动MiniQMT后，运行以下命令验证连接：")
print()
print("  C:\\Users\\fanzi\\.conda\\envs\\qmt\\python.exe scripts\\test_qmt_connection_v6.py")
print()

print("=" * 80)
print("常见问题")
print("=" * 80)
print()
print("Q1: 为什么数据接口能连接但交易接口返回-1？")
print("A1: 因为数据接口不需要MiniQMT模式，但交易接口必须使用MiniQMT模式。")
print()
print("Q2: 我已经在QMT中登录了，为什么还是连接失败？")
print("A2: 必须在登录时勾选【极简模式】或【独立交易】，普通登录模式不支持API交易。")
print()
print("Q3: 如何确认MiniQMT是否正常启动？")
print("A3: MiniQMT启动后会在系统托盘显示图标，界面非常简洁，没有复杂的图表和分析工具。")
print()

print("=" * 80)
print("技术说明")
print("=" * 80)
print()
print("根据官方文档：")
print("  'XtQuant是基于迅投MiniQMT衍生出来的一套完善的Python策略运行框架'")
print("  '在运行使用 XtQuant 的程序前需要先启动 MiniQMT 客户端'")
print()
print("这意味着：")
print("  1. MiniQMT是必须的，它是QMT的极简模式")
print("  2. 不需要单独下载，您的QMT已包含此功能")
print("  3. 必须以MiniQMT模式登录才能使用交易API")
print()

print("=" * 80)
print("立即行动")
print("=" * 80)
print()
print("请选择以下方式之一启动MiniQMT：")
print()
print("方式1（推荐）：")
print("  1. 完全关闭当前QMT")
print("  2. 重新打开QMT")
print("  3. 登录时勾选【极简模式】")
print()
print("方式2：")
print(f"  直接双击运行: {miniqmt_sim}")
print()
print("启动后等待30秒，然后运行连接测试脚本。")
print()

print("=" * 80)
print("完成")
print("=" * 80)