"""验证: 直接传registry路径"""
import os
from pathlib import Path
from zephyr.governance.drift_detection.drift_engine import load_detector_registry

registry_path = r"d:\ZephyrAlpha\src\zephyr\governance\drift_detection\_detector_registry.yaml"
print(f"Registry exists: {os.path.exists(registry_path)}")

detectors = load_detector_registry(registry_path=registry_path)
print(f"Loaded {len(detectors)} detectors")

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

if not missing and len(found) == 18:
    print("\n✅ All 18 detector scripts exist - no silent skip")
else:
    print(f"\n❌ {len(missing)} scripts still missing")
