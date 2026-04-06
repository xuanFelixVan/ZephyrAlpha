import chardet

file_path = r'd:\ZephyrAlpha\docs\10_AI_WORKFLOW\SENTIMENT_ANALYSIS_SHORT_TERM_TECHNICAL_SPECIFICATION.md'

with open(file_path, 'rb') as f:
    data = f.read()
    result = chardet.detect(data)
    print(f'检测到的编码: {result["encoding"]}')
    print(f'置信度: {result["confidence"]}')

try:
    decoded_text = data.decode(result['encoding'])
    print(f'\n前100个字符:')
    print(decoded_text[:100])
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(decoded_text)
    print(f'\n文件已转换为UTF-8编码')
except Exception as e:
    print(f'转换失败: {e}')
