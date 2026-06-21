import yaml
import os
import time
from concurrent.futures import ThreadPoolExecutor

REGISTRY = "data/asset_index/migration-registry.yaml"
PROJECT_ROOT = "D:/ZephyrAlpha"

SCAN_DIRS = [
    ("src/zephyr/", ".py"),
    ("scripts/", ".py"),
    ("tests/", ".py"),
    ("config/", ".yaml"),
]

def scan_disk_files():
    disk_files = set()
    t0 = time.perf_counter()

    def scan_dir(dir_path, ext):
        found = set()
        full_path = os.path.join(PROJECT_ROOT, dir_path)
        if not os.path.exists(full_path):
            return found
        for root, dirs, files in os.walk(full_path):
            for f in files:
                if f.endswith(ext) or f.endswith(".py"):
                    rel = os.path.join(root, f).replace("\\", "/")
                    rel = rel.replace(PROJECT_ROOT + "/", "")
                    found.add(rel)
        return found

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for dir_path, ext in SCAN_DIRS:
            futures.append(executor.submit(scan_dir, dir_path, ext))
        for future in futures:
            disk_files.update(future.result())

    print(f"  Scanned disk: {len(disk_files)} files in {time.perf_counter()-t0:.2f}s")
    return disk_files

def check_coverage():
    print("=== STEP 2C Loop Check: Disk vs Registry ===")
    print()

    print("[1/3] Loading migration registry...")
    t0 = time.perf_counter()
    with open(REGISTRY, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    print(f"  Loaded: {time.perf_counter()-t0:.2f}s")

    registry_paths = set()
    for entry in data.get("entries", []):
        p = entry.get("old_state", {}).get("path", "")
        if p:
            registry_paths.add(p)
    for entry in data.get("non_migrable_files", []):
        p = entry.get("path", "")
        if p:
            registry_paths.add(p)
    print(f"  Registry paths: {len(registry_paths)}")

    print("\n[2/3] Scanning disk files...")
    disk_files = scan_disk_files()

    print("\n[3/3] Comparing...")
    on_disk_not_in_registry = disk_files - registry_paths
    in_registry_not_on_disk = registry_paths - disk_files

    print(f"\n  On disk but NOT in registry: {len(on_disk_not_in_registry)}")
    if on_disk_not_in_registry:
        by_prefix = {}
        for f in sorted(on_disk_not_in_registry):
            parts = f.split("/")
            prefix = "/".join(parts[:3]) if len(parts) > 3 else f
            by_prefix[prefix] = by_prefix.get(prefix, 0) + 1
        print("  Breakdown by prefix:")
        for prefix, count in sorted(by_prefix.items(), key=lambda x: -x[1]):
            print(f"    {prefix}: {count}")
        print("\n  First 30 missing files:")
        for f in sorted(on_disk_not_in_registry)[:30]:
            print(f"    {f}")

    print(f"\n  In registry but NOT on disk: {len(in_registry_not_on_disk)}")
    if in_registry_not_on_disk:
        by_prefix = {}
        for f in sorted(in_registry_not_on_disk):
            parts = f.split("/")
            prefix = "/".join(parts[:3]) if len(parts) > 3 else f
            by_prefix[prefix] = by_prefix.get(prefix, 0) + 1
        print("  Breakdown by prefix:")
        for prefix, count in sorted(by_prefix.items(), key=lambda x: -x[1]):
            print(f"    {prefix}: {count}")

    print(f"\n=== RESULT ===")
    print(f"  Disk files: {len(disk_files)}")
    print(f"  Registry paths: {len(registry_paths)}")
    print(f"  Missing from registry: {len(on_disk_not_in_registry)}")
    print(f"  Ghost entries (not on disk): {len(in_registry_not_on_disk)}")
    print(f"  Coverage: {(len(disk_files) - len(on_disk_not_in_registry)) / len(disk_files) * 100:.1f}%")

    return len(on_disk_not_in_registry)

if __name__ == "__main__":
    check_coverage()
