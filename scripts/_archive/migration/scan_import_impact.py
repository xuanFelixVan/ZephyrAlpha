import ast
import os
import re
import yaml
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

REGISTRY = "data/asset_index/migration-registry.yaml"
PROJECT_ROOT = "D:/ZephyrAlpha"
OUTPUT = "data/asset_index/import-update-manifest.yaml"

SCAN_DIRS = ["src/zephyr/", "scripts/", "tests/"]

def build_import_map(registry_path):
    print("[1/4] Loading migration registry...")
    t0 = time.perf_counter()
    with open(registry_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    print(f"  Loaded: {time.perf_counter()-t0:.2f}s")

    old_to_new = {}
    for entry in data.get("entries", []):
        old = entry.get("old_state", {}).get("path", "")
        new = entry.get("new_state", {}).get("path", "")
        if not old or not new or old == new:
            continue
        if old.startswith("src/zephyr/") and new.startswith("src/zephyr/"):
            old_imp = old.removeprefix("src/").removesuffix(".py").replace("/", ".")
            new_imp = new.removeprefix("src/").removesuffix(".py").replace("/", ".")
            if old_imp != new_imp:
                old_to_new[old_imp] = new_imp

    print(f"  Import path changes: {len(old_to_new)}")

    prefix_map = {}
    for old_imp, new_imp in sorted(old_to_new.items(), key=lambda x: -len(x[0])):
        parts = old_imp.split(".")
        for i in range(2, len(parts) + 1):
            prefix = ".".join(parts[:i])
            if prefix not in prefix_map and prefix in old_to_new:
                prefix_map[prefix] = old_to_new[prefix]

    print(f"  Prefix map entries: {len(prefix_map)}")
    return old_to_new, prefix_map

def scan_file_imports(filepath):
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            source = f.read()
    except (OSError, PermissionError):
        return []

    imports = []
    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError:
        lines = source.split("\n")
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            m = re.match(r"^from\s+([\w.]+)\s+import", stripped)
            if m:
                imports.append({"line": i, "module": m.group(1), "raw": stripped, "type": "from_import"})
                continue
            m = re.match(r"^import\s+([\w.]+)", stripped)
            if m:
                imports.append({"line": i, "module": m.group(1), "raw": stripped, "type": "import"})
        return imports

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imports.append({
                "line": node.lineno,
                "module": node.module,
                "names": [alias.name for alias in node.names],
                "raw": f"from {node.module} import ...",
                "type": "from_import",
            })
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append({
                    "line": node.lineno,
                    "module": alias.name,
                    "names": [alias.name],
                    "raw": f"import {alias.name}",
                    "type": "import",
                })
    return imports

def find_all_py_files():
    py_files = []
    for scan_dir in SCAN_DIRS:
        full = os.path.join(PROJECT_ROOT, scan_dir)
        if not os.path.exists(full):
            continue
        for root, dirs, files in os.walk(full):
            for f in files:
                if f.endswith(".py"):
                    abs_path = os.path.join(root, f)
                    rel_path = abs_path.replace("\\", "/").replace(PROJECT_ROOT + "/", "")
                    py_files.append((abs_path, rel_path))
    return py_files

def match_import(imp_module, old_to_new, prefix_map):
    if imp_module in old_to_new:
        return old_to_new[imp_module], "exact_match"

    for i in range(len(imp_module.split(".")), 1, -1):
        prefix = ".".join(imp_module.split(".")[:i])
        if prefix in old_to_new:
            new_prefix = old_to_new[prefix]
            suffix = imp_module[len(prefix):]
            return new_prefix + suffix, "prefix_match"

    if imp_module.startswith("zephyr."):
        parts = imp_module.split(".")
        if len(parts) >= 2:
            top_pkg = parts[1]
            for old_imp in old_to_new:
                old_parts = old_imp.split(".")
                if len(old_parts) >= 2 and old_parts[1] == top_pkg:
                    return None, "needs_manual_review"

    return None, "no_change_needed"

def main():
    print("=== STEP 2D: Import Update Manifest Generator ===\n")

    old_to_new, prefix_map = build_import_map(REGISTRY)

    print("\n[2/4] Scanning .py files...")
    t0 = time.perf_counter()
    py_files = find_all_py_files()
    print(f"  Found {len(py_files)} .py files in {time.perf_counter()-t0:.2f}s")

    print("\n[3/4] Parsing imports...")
    t0 = time.perf_counter()
    all_updates = []
    files_with_updates = 0
    total_imports_scanned = 0
    zephyr_imports_scanned = 0
    match_stats = defaultdict(int)

    def process_file(item):
        abs_path, rel_path = item
        imports = scan_file_imports(abs_path)
        file_updates = []
        for imp in imports:
            if not imp["module"].startswith("zephyr."):
                continue
            new_module, match_type = match_import(imp["module"], old_to_new, prefix_map)
            if new_module and new_module != imp["module"]:
                file_updates.append({
                    "line": imp["line"],
                    "old": imp["module"],
                    "new": new_module,
                    "type": imp["type"],
                    "match_type": match_type,
                })
        return rel_path, imports, file_updates

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(process_file, item): item for item in py_files}
        for future in as_completed(futures):
            rel_path, imports, file_updates = future.result()
            total_imports_scanned += len(imports)
            zephyr_imports_scanned += sum(1 for i in imports if i["module"].startswith("zephyr."))
            if file_updates:
                files_with_updates += 1
                for u in file_updates:
                    match_stats[u["match_type"]] += 1
                all_updates.append({
                    "file": rel_path,
                    "change_count": len(file_updates),
                    "changes": file_updates,
                })

    print(f"  Scanned {len(py_files)} files, {total_imports_scanned} imports, {zephyr_imports_scanned} zephyr imports")
    print(f"  Files with updates needed: {files_with_updates}")
    print(f"  Total import changes: {sum(u['change_count'] for u in all_updates)}")
    print(f"  Match stats: {dict(match_stats)}")
    print(f"  Time: {time.perf_counter()-t0:.2f}s")

    print("\n[4/4] Writing manifest...")
    output_data = {
        "metadata": {
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
            "total_files_scanned": len(py_files),
            "total_imports_scanned": total_imports_scanned,
            "zephyr_imports_scanned": zephyr_imports_scanned,
            "files_with_updates": files_with_updates,
            "total_import_changes": sum(u["change_count"] for u in all_updates),
            "match_stats": dict(match_stats),
        },
        "updates": all_updates,
    }

    tmp_path = OUTPUT + f".{os.getpid()}.tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            yaml.dump(output_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        os.replace(tmp_path, OUTPUT)
        print(f"  Written to {OUTPUT}")
    except PermissionError:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        raise

    file_size_mb = os.path.getsize(OUTPUT) / (1024 * 1024)
    print(f"  File size: {file_size_mb:.1f} MB")

    print(f"\n=== SUMMARY ===")
    print(f"  Files scanned: {len(py_files)}")
    print(f"  Files needing import updates: {files_with_updates}")
    print(f"  Total import changes: {sum(u['change_count'] for u in all_updates)}")
    print(f"  Exact matches: {match_stats.get('exact_match', 0)}")
    print(f"  Prefix matches: {match_stats.get('prefix_match', 0)}")

if __name__ == "__main__":
    main()
