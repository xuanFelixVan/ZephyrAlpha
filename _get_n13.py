"""获取 N-13 违规清单并分析。"""
import subprocess
import sys
import re
from pathlib import Path

REPO_ROOT = Path(r"d:\ZephyrAlpha")
check_script = REPO_ROOT / "scripts" / "governance" / "d3_metadata" / "check_naming_convention.py"

print("运行命名检查脚本...")
result = subprocess.run(
    [sys.executable, str(check_script), "--scan", "--warn-only"],
    capture_output=True,
    cwd=str(REPO_ROOT),
    timeout=300,
)

stdout_text = result.stdout.decode("utf-8", errors="replace")
lines = stdout_text.splitlines()

# 提取 N-13 违规
n13_violations = []
for line in lines:
    if "[N-13]" in line:
        n13_violations.append(line)

print(f"\n=== N-13 违规清单 ({len(n13_violations)} 个) ===\n")

# 分析违规类型
kebab_count = 0
camel_count = 0
other_count = 0

for i, v in enumerate(n13_violations, 1):
    # 提取文件名
    m = re.search(r":\s*(\S+)\s*$", v)
    if m:
        fname = m.group(1)
        # 判断违规类型
        if "-" in fname and not fname.startswith("."):
            kebab_count += 1
            vtype = "kebab"
        elif re.search(r"[A-Z]", fname):
            camel_count += 1
            vtype = "camel"
        else:
            other_count += 1
            vtype = "other"
        print(f"  {i:3d}. [{vtype:5s}] {fname}")
    else:
        print(f"  {i:3d}. {v}")

print(f"\n=== 违规类型统计 ===")
print(f"  kebab-case (含连字符): {kebab_count}")
print(f"  CamelCase (含大写): {camel_count}")
print(f"  其他: {other_count}")
print(f"  总计: {len(n13_violations)}")
