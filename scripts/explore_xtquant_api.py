# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
探索xtquant API，特别是XtQuantTrader构造函数的参数
"""

import inspect
from xtquant.xttrader import XtQuantTrader

print("=" * 80)
print("XtQuantTrader API 探索")
print("=" * 80)

# 检查构造函数签名
print("\n1. XtQuantTrader构造函数签名:")
try:
    sig = inspect.signature(XtQuantTrader.__init__)
    print(f"   签名: {sig}")
    
    # 分析参数
    print("\n   参数分析:")
    for param_name, param in sig.parameters.items():
        if param_name == 'self':
            continue
        print(f"     - {param_name}:")
        print(f"        类型: {param.annotation if param.annotation != inspect.Parameter.empty else '未指定'}")
        print(f"        默认值: {param.default if param.default != inspect.Parameter.empty else '无'}")
except Exception as e:
    print(f"   获取签名失败: {e}")

# 检查类的文档字符串
print("\n2. XtQuantTrader文档字符串:")
try:
    doc = XtQuantTrader.__doc__
    if doc:
        print(f"   文档:\n{doc[:500]}...")  # 只显示前500字符
    else:
        print("   无文档字符串")
except Exception as e:
    print(f"   获取文档失败: {e}")

# 检查类的所有方法
print("\n3. XtQuantTrader的主要方法:")
try:
    methods = [m for m in dir(XtQuantTrader) if not m.startswith('_')]
    print(f"   公共方法数量: {len(methods)}")
    print(f"   方法列表: {methods[:20]}")  # 显示前20个
except Exception as e:
    print(f"   获取方法失败: {e}")

# 检查connect方法
print("\n4. connect方法签名:")
try:
    connect_method = getattr(XtQuantTrader, 'connect', None)
    if connect_method:
        sig = inspect.signature(connect_method)
        print(f"   签名: {sig}")
        
        # 检查是否有额外参数
        print("\n   connect参数分析:")
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            print(f"     - {param_name}:")
            print(f"        类型: {param.annotation if param.annotation != inspect.Parameter.empty else '未指定'}")
            print(f"        默认值: {param.default if param.default != inspect.Parameter.empty else '无'}")
    else:
        print("   未找到connect方法")
except Exception as e:
    print(f"   获取connect签名失败: {e}")

print("\n" + "=" * 80)
print("完成")
print("=" * 80)