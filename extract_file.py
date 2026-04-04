import subprocess
import sys

print("开始提取文件...")
sys.stdout.flush()

result = subprocess.run(
    ["git", "cat-file", "-p", "72d1c02:docs/02_FACTOR_LIBRARY/01_METHODOLOGY/FACTOR_SCREENING_STRATEGY.md"],
    capture_output=True,
    text=True,
    encoding='utf-8'
)

print(f"返回码: {result.returncode}")
print(f"标准输出长度: {len(result.stdout)}")
print(f"标准错误: {result.stderr[:200] if result.stderr else 'None'}")
sys.stdout.flush()

if result.returncode == 0 and len(result.stdout) > 100:
    content = result.stdout
    print(f"✓ 内容长度: {len(content)} 字符")
    print(f"✓ 行数: {len(content.splitlines())} 行")
    sys.stdout.flush()
    
    with open("docs/02_FACTOR_LIBRARY/01_STANDARDS/FACTOR_SCREENING_STRATEGY.md", "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"✓ 文件已保存")
    
    print(f"\n前10行预览:")
    lines = content.splitlines()
    for i, line in enumerate(lines[:10], 1):
        print(f"{i:3d}: {line[:80]}")
else:
    print(f"✗ 提取失败或内容过短")
    if len(result.stdout) < 100:
        print(f"实际内容: {result.stdout[:200]}")
