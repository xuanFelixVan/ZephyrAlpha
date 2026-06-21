"""运行 pytest collect-only 并保存输出到文件。

运行后立即删除（RULE-FIVE 零残留）。
"""
import subprocess
import sys

REPO_ROOT = r"d:\ZephyrAlpha"
OUTPUT_FILE = r"d:\ZephyrAlpha\_pytest_output.txt"

print("运行 pytest collect-only...")
sys.stdout.flush()

# 用 -q --tb=line 减少输出量
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    result = subprocess.run(
        ["python", "-m", "pytest", "tests/", "--collect-only", "-q", "--tb=line", "-p", "no:cacheprovider"],
        cwd=REPO_ROOT,
        stdout=f,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=1800,  # 30分钟
    )

print(f"pytest 完成，exit code: {result.returncode}")
print(f"输出保存到: {OUTPUT_FILE}")
