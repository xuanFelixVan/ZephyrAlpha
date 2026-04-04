import subprocess

result = subprocess.run(
    ["git", "cat-file", "-p", "72d1c02:docs/02_FACTOR_LIBRARY/01_METHODOLOGY/FACTOR_SCREENING_STRATEGY.md"],
    capture_output=True,
    text=True,
    encoding='utf-8'
)

if result.returncode == 0:
    content = result.stdout
    print(f"内容长度: {len(content)} 字符")
    print(f"行数: {len(content.splitlines())} 行")
    
    with open("docs/02_FACTOR_LIBRARY/01_STANDARDS/FACTOR_SCREENING_STRATEGY.md", "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"✓ 文件已保存")
else:
    print(f"✗ 错误: {result.stderr}")
