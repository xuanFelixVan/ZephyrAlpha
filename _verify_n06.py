"""验证 N-06 违规数量"""
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(r"d:\ZephyrAlpha")
check_script = REPO_ROOT / "scripts" / "governance" / "d3_metadata" / "check_naming_convention.py"

result = subprocess.run(
    [sys.executable, str(check_script), "--scan", "--warn-only"],
    capture_output=True,
    cwd=str(REPO_ROOT),
    timeout=300,
)

output = result.stdout.decode("utf-8", errors="replace")
n06_violations = []
for line in output.splitlines():
    if "N-06" in line:
        n06_violations.append(line.strip())

print(f"N-06 违规总数: {len(n06_violations)}")
print("-" * 80)
for v in n06_violations[:30]:
    print(v)
if len(n06_violations) > 30:
    print(f"... 还有 {len(n06_violations) - 30} 个")
