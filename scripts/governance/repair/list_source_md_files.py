# -*- coding: utf-8 -*-
"""扫描临时工作区源MD文件清单"""
import os
import sys

DIRS = [
    r"D:\临时工作区\依赖图",
    r"D:\临时工作区\架构图",
]
FILES = [
    r"D:\临时工作区\ZephyrAlpha全系统模块清单.md",
    r"D:\临时工作区\能力定位书.md",
]

all_files = []

# 扫描目录
for d in DIRS:
    if os.path.exists(d):
        for name in sorted(os.listdir(d)):
            if name.endswith(".md"):
                all_files.append(os.path.join(d, name))
    else:
        print(f"[WARNING] 目录不存在: {d}")

# 添加单独文件
for f in FILES:
    if os.path.exists(f):
        all_files.append(f)
    else:
        print(f"[WARNING] 文件不存在: {f}")

print(f"共找到 {len(all_files)} 个MD文件:")
for i, f in enumerate(all_files, 1):
    print(f"  {i}. {f}")
