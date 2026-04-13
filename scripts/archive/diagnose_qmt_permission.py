# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
QMT权限诊断脚本 - 检查账号是否有策略交易权限

根据官方文档：
如果miniqmt开启后, userdata_mini文件夹内没有up_queue_xtquant文件，
说明用户没有对应函数下单的权限，需要联系券商开启
"""

import os
from pathlib import Path
from datetime import datetime

print("=" * 80)
print("QMT权限诊断脚本")
print("=" * 80)
print(f"诊断时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 步骤1: 检查客户端路径
print("步骤1: 检查客户端路径")
print("-" * 80)

client_path = os.getenv('QMT_SIMULATION_CLIENT_PATH', 'E:/国金QMT交易端模拟/bin.x64')
print(f"配置的客户端路径: {client_path}")

# 检查是否是bin.x64路径，需要转换为userdata_mini
if 'bin.x64' in client_path:
    userdata_path = client_path.replace('bin.x64', 'userdata_mini')
    print(f"转换后的userdata_mini路径: {userdata_path}")
else:
    userdata_path = client_path

print()

# 步骤2: 检查userdata_mini文件夹
print("步骤2: 检查userdata_mini文件夹")
print("-" * 80)

userdata_path_obj = Path(userdata_path)

if userdata_path_obj.exists():
    print(f"✅ userdata_mini文件夹存在: {userdata_path}")
    
    # 列出文件夹内容
    print("\n文件夹内容:")
    items = list(userdata_path_obj.iterdir())
    for item in sorted(items)[:20]:  # 只显示前20个
        print(f"  {'[文件夹]' if item.is_dir() else '[文件]  '} {item.name}")
    
    if len(items) > 20:
        print(f"  ... 还有 {len(items) - 20} 个项目")
    
    print()
    
    # 步骤3: 检查关键文件
    print("步骤3: 检查关键权限文件")
    print("-" * 80)
    
    # 检查up_queue_xtquant文件
    up_queue_files = list(userdata_path_obj.glob('up_queue_xtquant*'))
    
    if up_queue_files:
        print(f"✅ 找到 up_queue_xtquant 文件 ({len(up_queue_files)} 个)")
        print("  → 说明账号有策略交易权限")
        for f in up_queue_files[:5]:
            print(f"    {f.name}")
    else:
        print("❌ 未找到 up_queue_xtquant 文件")
        print("  → 说明账号没有策略交易权限！")
        print("\n⚠️  这是连接失败（返回码 -1）的根本原因！")
    
    print()
    
    # 检查down_queue文件
    down_queue_files = list(userdata_path_obj.glob('down_queue*'))
    
    if down_queue_files:
        print(f"✅ 找到 down_queue 文件 ({len(down_queue_files)} 个)")
        for f in down_queue_files[:5]:
            print(f"    {f.name}")
    else:
        print("⚠️  未找到 down_queue 文件")
    
    print()
    
    # 步骤4: 检查写入权限
    print("步骤4: 检查写入权限")
    print("-" * 80)
    
    test_file = userdata_path_obj / 'test_permission.txt'
    try:
        with open(test_file, 'w') as f:
            f.write('test')
        test_file.unlink()  # 删除测试文件
        print("✅ 有写入权限")
    except PermissionError:
        print("❌ 没有写入权限")
        print("  → 如果安装在C盘，需要以管理员身份运行")
    except Exception as e:
        print(f"⚠️  写入测试失败: {e}")
    
else:
    print(f"❌ userdata_mini文件夹不存在: {userdata_path}")
    print("\n可能的原因：")
    print("  1. QMT客户端路径配置错误")
    print("  2. QMT客户端未启动或未登录")
    print("  3. 未以极简模式登录")

print()

# 步骤5: 检查QMT进程
print("步骤5: 检查QMT进程")
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
        print("❌ 未找到QMT进程")
        print("  → 请确保QMT客户端已启动")
        
except ImportError:
    print("⚠️  psutil库未安装，无法检查进程")
    print("  安装命令: pip install psutil")

print()

# 总结
print("=" * 80)
print("诊断总结")
print("=" * 80)

print("\n关键检查项：")

# 检查userdata_mini是否存在
userdata_exists = Path(userdata_path).exists()
print(f"  [{'✅' if userdata_exists else '❌'}] 1. userdata_mini文件夹存在")

# 检查up_queue_xtquant文件
up_queue_exists = bool(list(Path(userdata_path).glob('up_queue_xtquant*'))) if userdata_exists else False
print(f"  [{'✅' if up_queue_exists else '❌'}] 2. up_queue_xtquant文件存在（策略交易权限）")

# 检查QMT进程
try:
    import psutil
    qmt_running = any('QMT' in (proc.info['exe'] or '') for proc in psutil.process_iter(['exe']))
    print(f"  [{'✅' if qmt_running else '❌'}] 3. QMT进程正在运行")
except:
    print(f"  [?] 3. QMT进程状态未知")

print()

if not up_queue_exists and userdata_exists:
    print("⚠️  诊断结果：账号缺少策略交易权限！")
    print("\n解决方案：")
    print("  1. 联系国金证券客服：95310")
    print("  2. 说明情况：需要开通QMT策略交易权限")
    print("  3. 在开通QMT的页面，勾选【策略交易权限】")
    print("  4. 等待权限开通后，重新测试连接")
    
    print("\n参考链接：")
    print("  - 官方论坛: https://www.xuntou.net/forum.php?mod=viewthread&tid=1705")
    print("  - 官方文档: http://dict.thinktrader.net/nativeApi/question_function.html")

elif not userdata_exists:
    print("⚠️  诊断结果：userdata_mini文件夹不存在！")
    print("\n解决方案：")
    print("  1. 确保QMT客户端已启动")
    print("  2. 确保以极简模式登录")
    print("  3. 检查客户端路径配置")

else:
    print("✅ 诊断结果：权限检查通过！")
    print("\n如果仍然连接失败，请检查：")
    print("  1. 是否以极简模式登录")
    print("  2. Session是否冲突（换个session试试）")
    print("  3. 是否安装在C盘（需要管理员权限）")

print()
