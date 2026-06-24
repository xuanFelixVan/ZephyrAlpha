"""分析 N-06 违规：获取每个违规文件的 module_id 值"""
import subprocess
import sys
import re
from pathlib import Path
from collections import Counter

REPO_ROOT = Path(r"d:\ZephyrAlpha")
check_script = REPO_ROOT / "scripts" / "governance" / "d3_metadata" / "check_naming_convention.py"

# 运行检查获取违规文件路径
result = subprocess.run(
    [sys.executable, str(check_script), "--scan", "--warn-only"],
    capture_output=True,
    cwd=str(REPO_ROOT),
    timeout=300,
)
output = result.stdout.decode("utf-8", errors="replace")

# 解析违规清单 - 格式: [N-06] module_id 缺少 scope 前缀: filename
violations = []
for line in output.splitlines():
    line = line.strip()
    if "[N-06]" in line and "module_id 缺少 scope 前缀" in line:
        # 提取文件名（冒号后的部分）
        match = re.search(r"module_id 缺少 scope 前缀:\s*(.+)$", line)
        if match:
            fname = match.group(1).strip()
            violations.append(fname)

print(f"N-06 违规总数: {len(violations)}")

# 查找每个违规文件的路径和 module_id 值
module_id_patterns = Counter()
file_details = []

for vname in violations:
    # 搜索文件
    found = list(REPO_ROOT.rglob(vname))
    if not found:
        file_details.append((vname, "NOT FOUND", ""))
        module_id_patterns["NOT FOUND"] += 1
        continue
    for fpath in found[:1]:  # 只取第一个匹配
        try:
            content = fpath.read_text(encoding="utf-8", errors="replace")
        except Exception:
            file_details.append((vname, str(fpath.relative_to(REPO_ROOT)), "READ ERROR"))
            module_id_patterns["READ ERROR"] += 1
            continue
        # 查找 module_id 值（YAML格式: module_id: VALUE）
        mid_match = re.search(r"^\s*module_id:\s*(.+)$", content, re.MULTILINE)
        if mid_match:
            mid_value = mid_match.group(1).strip()
            file_details.append((vname, str(fpath.relative_to(REPO_ROOT)), mid_value))
            # 分类 module_id 模式
            if mid_value.startswith("TRAE-"):
                module_id_patterns["TRAE-XXX"] += 1
            elif mid_value.startswith("mod_"):
                module_id_patterns["mod_xxx (lowercase)"] += 1
            elif mid_value.startswith("MOD-"):
                module_id_patterns["MOD-XXX (uppercase)"] += 1
            elif mid_value.startswith("PS-"):
                module_id_patterns["PS-XXX"] += 1
            else:
                module_id_patterns[f"OTHER: {mid_value[:30]}"] += 1
        else:
            file_details.append((vname, str(fpath.relative_to(REPO_ROOT)), "(无 module_id)"))
            module_id_patterns["(无 module_id)"] += 1

print("\nmodule_id 模式分布:")
for pattern, count in module_id_patterns.most_common():
    print(f"  {pattern}: {count}")

print("\n详细清单（前40个）:")
print("-" * 120)
for i, (vname, fpath, mid) in enumerate(file_details[:40]):
    print(f"{i+1:3d}. {vname:55s} | {mid:30s} | {fpath}")
if len(file_details) > 40:
    print(f"... 还有 {len(file_details) - 40} 个")
