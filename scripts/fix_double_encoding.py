# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

file_path = r'd:\ZephyrAlpha\docs\10_AI_WORKFLOW\SENTIMENT_ANALYSIS_SHORT_TERM_TECHNICAL_SPECIFICATION.md'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

try:
    fixed_content = content.encode('latin-1').decode('utf-8')
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print('文件编码修复成功！')
    print('\n前200个字符:')
    print(fixed_content[:200])
except Exception as e:
    print(f'修复失败: {e}')
    print('\n尝试其他方法...')
    
    try:
        fixed_content = content.encode('cp1252').decode('utf-8')
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print('文件编码修复成功（使用cp1252）！')
        print('\n前200个字符:')
        print(fixed_content[:200])
    except Exception as e2:
        print(f'修复失败（使用cp1252）: {e2}')
