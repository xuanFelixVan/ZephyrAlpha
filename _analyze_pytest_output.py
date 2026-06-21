"""分析 pytest 输出文件，统计错误分类。

运行后立即删除（RULE-FIVE 零残留）。
"""
import re
from collections import Counter

OUTPUT_FILE = r"d:\ZephyrAlpha\_pytest_output.txt"

with open(OUTPUT_FILE, "r", encoding="utf-8", errors="replace") as f:
    output = f.read()

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

# 统计错误类型
error_types = re.findall(r"^E\s+(\w+(?:Error|Exception)):", output, re.MULTILINE)
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

# SyntaxError 文件列表
syntax_errors = re.findall(r"^ERROR\s+(\S+\.py)\s+-\s+SyntaxError", output, re.MULTILINE)
if syntax_errors:
    print(f"\nSyntaxError 文件列表:")
    for fp in syntax_errors:
        print(f"  {fp}")
