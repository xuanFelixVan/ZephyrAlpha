"""获取 N-13 违规文件的完整路径。"""
import subprocess
import sys
import re
from pathlib import Path

REPO_ROOT = Path(r"d:\ZephyrAlpha")
check_script = REPO_ROOT / "scripts" / "governance" / "d3_metadata" / "check_naming_convention.py"

result = subprocess.run(
    [sys.executable, str(check_script), "--scan", "--warn-only"],
    capture_output=True,
    cwd=str(REPO_ROOT),
    timeout=300,
)

stdout_text = result.stdout.decode("utf-8", errors="replace")
lines = stdout_text.splitlines()

# 提取 N-13 违规的完整路径
n13_files = []
for line in lines:
    if "[N-13]" in line:
        # N-13 输出格式: [N-13] ... : filename
        # 但实际路径需要从其他信息提取
        n13_files.append(line)

# 按文件名分组
from collections import defaultdict
name_groups = defaultdict(list)

for line in n13_files:
    m = re.search(r":\s*(\S+)\s*$", line)
    if m:
        fname = m.group(1)
        name_groups[fname].append(line)

print(f"=== N-13 违规按文件名分组 ({len(n13_files)} 个) ===\n")
for name, lines in sorted(name_groups.items()):
    print(f"  {name} ({len(lines)} 个)")
    for l in lines:
        print(f"    {l}")

# 查找这些文件的实际路径
print(f"\n=== 文件实际路径 ===\n")
import os
all_files = []
for root, dirs, files in os.walk(REPO_ROOT):
    if ".git" in root or "node_modules" in root:
        continue
    for f in files:
        all_files.append(os.path.join(root, f))

for name in sorted(name_groups.keys()):
    matches = [f for f in all_files if f.endswith(name) or os.path.basename(f) == name]
    for m in matches:
        rel = os.path.relpath(m, REPO_ROOT)
        print(f"  {name:40s} → {rel}")
