import os
import chardet

# 8个编码问题的INDEX.md文件
files_to_fix = [
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
print('修复8个编码问题的INDEX.md文件')
print('=' * 80)
print()

fixed_count = 0
failed_count = 0

for filepath in files_to_fix:
    print(f'修复文件: {filepath}')
    
    if not os.path.exists(filepath):
        print(f'  ❌ 文件不存在，跳过')
        print()
        failed_count += 1
        continue
    
    # 检测文件编码
    with open(filepath, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
    
    detected_encoding = result['encoding']
    print(f'  检测编码: {detected_encoding} (置信度: {result["confidence"]:.2%})')
    
    # 尝试读取文件
    try:
        # 尝试多种编码
        encodings_to_try = [detected_encoding, 'utf-8', 'gbk', 'gb2312', 'gb18030', 'big5']
        content = None
        used_encoding = None
        
        for encoding in encodings_to_try:
            try:
                with open(filepath, 'r', encoding=encoding) as f:
                    content = f.read()
                used_encoding = encoding
                print(f'  ✅ 使用{encoding}读取成功')
                break
            except:
                continue
        
        if content is None:
            print(f'  ❌ 无法读取文件，跳过')
            print()
            failed_count += 1
            continue
        
        # 检查是否有乱码
        if '\ufffd' in content:
            print(f'  ⚠️ 文件包含乱码字符，尝试修复')
            # 替换乱码字符
            content = content.replace('\ufffd', '')
        
        # 转换为UTF-8并保存
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f'  ✅ 已转换为UTF-8编码并保存')
        fixed_count += 1
        
    except Exception as e:
        print(f'  ❌ 修复失败: {e}')
        failed_count += 1
    
    print()

print('=' * 80)
print('修复完成')
print('=' * 80)
print(f'修复成功: {fixed_count} 个文件')
print(f'修复失败: {failed_count} 个文件')
