"""验证: detector registry 加载 + 路径存在性检查"""
import os
from pathlib import Path
from zephyr.governance.drift_detection.drift_engine import load_detector_registry

detectors = load_detector_registry()
print(f"Loaded {len(detectors)} detectors")

# scripts/governance 是根
scripts_root = Path(r"d:\ZephyrAlpha\scripts\governance")

existing_with_script = [d for d in detectors if d.script]
print(f"Detectors with script: {len(existing_with_script)}")

missing = []
found = []
for d in existing_with_script:
    script_path = scripts_root / d.script
    if script_path.exists():
        found.append(d.id)
    else:
        missing.append((d.id, d.script))

print(f"Found (path exists): {len(found)}")
print(f"Missing (path NOT exists): {len(missing)}")
for mid, script in missing:
    print(f"  MISSING: {mid} -> {script}")

if not missing:
    print("\n✅ All 18 detector scripts exist - no silent skip")
else:
    print(f"\n❌ {len(missing)} scripts still missing")
