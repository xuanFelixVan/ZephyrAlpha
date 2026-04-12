# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import codecs

file_path = r'd:\ZephyrAlpha\docs\10_AI_WORKFLOW\SENTIMENT_ANALYSIS_SHORT_TERM_TECHNICAL_SPECIFICATION.md'

with open(file_path, 'rb') as f:
    data = f.read()
    
print('前100个字节的十六进制:')
print(data[:100].hex())

print('\n尝试不同编码解码:')
encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'gb18030', 'big5', 'latin-1']

for encoding in encodings:
    try:
        decoded = data.decode(encoding)
        print(f'\n{encoding}:')
        print(decoded[:100])
        print('✓ 成功')
    except Exception as e:
        print(f'\n{encoding}: ✗ 失败 - {e}')
