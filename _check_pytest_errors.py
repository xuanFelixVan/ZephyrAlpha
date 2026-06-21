"""快速统计 pytest collect-only 错误数（v3，仅统计不分析）。

运行后立即删除（RULE-FIVE 零残留）。
"""
import re
import subprocess

REPO_ROOT = r"d:\ZephyrAlpha"

# 用 -q --tb=line 减少输出量，加快速度
result = subprocess.run(
    ["python", "-m", "pytest", "tests/", "--collect-only", "-q", "--tb=line", "-p", "no:cacheprovider"],
    cwd=REPO_ROOT,
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="replace",
    timeout=900,
)

output = result.stdout + result.stderr

# 统计关键数字
total_match = re.search(r"(\d+) errors during collection", output)
total_errors = int(total_match.group(1)) if total_match else 0
collected_match = re.search(r"(\d+) tests collected", output)
collected = collected_match.group(1) if collected_match else "?"

print(f"总错误数: {total_errors}")
print(f"tests collected: {collected}")

# 统计 ERROR 行数
error_lines = re.findall(r"^ERROR\s+(\S+\.py)", output, re.MULTILINE)
print(f"ERROR 行数: {len(error_lines)}")

# 统计错误类型（从 E   ErrorType: 行）
error_types = re.findall(r"^E\s+(\w+(?:Error|Exception)):", output, re.MULTILINE)
from collections import Counter
type_counter = Counter(error_types)
print(f"\n按错误类型分类:")
for error_type, count in type_counter.most_common():
    print(f"  {error_type}: {count}")

# ModuleNotFoundError 模块路径统计
module_not_found = re.findall(r"No module named '([^']+)'", output)
if module_not_found:
    print(f"\nModuleNotFoundError 模块路径统计（前30）:")
    mod_counter = Counter(module_not_found)
    for mod, count in mod_counter.most_common(30):
        print(f"  {count:4d}  {mod}")

# ImportError cannot import name 统计
cannot_import = re.findall(r"cannot import name '([^']+)'", output)
if cannot_import:
    print(f"\nImportError cannot import name 统计（前20）:")
    name_counter = Counter(cannot_import)
    for name, count in name_counter.most_common(20):
        print(f"  {count:4d}  {name}")
