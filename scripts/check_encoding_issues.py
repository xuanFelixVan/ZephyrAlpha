# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os
import chardet

# 8个编码问题的INDEX.md文件
files_to_check = [
    'docs/00_OVERVIEW/INDEX.md',
    'docs/00_RESOURCES/INDEX.md',
    'docs/03_TRADING_TACTICS/INDEX.md',
    'docs/03_TRADING_TACTICS/01_STRATEGY_FRAMEWORK/INDEX.md',
    'docs/04_Execution/01_EVENT_ENGINE/INDEX.md',
    'docs/04_Execution/03_MONITORING/INDEX.md',
    'docs/05_IMPLEMENTATION/01_QUICKSTART/INDEX.md',
    'docs/05_IMPLEMENTATION/02_DEVELOPMENT/INDEX.md',
]

print('=' * 80)
print('检查8个编码问题的INDEX.md文件')
print('=' * 80)
print()

for filepath in files_to_check:
    print(f'检查文件: {filepath}')
    
    if not os.path.exists(filepath):
        print(f'  ❌ 文件不存在')
        print()
        continue
    
    # 检测文件编码
    with open(filepath, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
    
    print(f'  检测编码: {result["encoding"]}')
    print(f'  置信度: {result["confidence"]:.2%}')
    
    # 尝试读取文件
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f'  ✅ UTF-8读取成功')
    except UnicodeDecodeError as e:
        print(f'  ❌ UTF-8读取失败: {e}')
        
        # 尝试使用检测到的编码读取
        try:
            with open(filepath, 'r', encoding=result['encoding']) as f:
                content = f.read()
            print(f'  ✅ 使用{result["encoding"]}读取成功')
            
            # 检查是否有乱码
            if '\ufffd' in content:
                print(f'  ⚠️ 文件包含乱码字符')
        except Exception as e:
            print(f'  ❌ 使用{result["encoding"]}读取失败: {e}')
    
    print()

print('=' * 80)
print('检查完成')
print('=' * 80)
