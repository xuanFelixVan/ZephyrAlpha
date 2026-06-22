import yaml

with open("data/asset_index/import-update-manifest.yaml", encoding="utf-8") as f:
    data = yaml.safe_load(f)

meta = data["metadata"]
print("=== Import Update Manifest Summary ===")
print(f"Files with updates: {meta['files_with_updates']}")
print(f"Total changes: {meta['total_import_changes']}")
print(f"Exact matches: {meta['match_stats'].get('exact_match', 0)}")
print()

top_files = sorted(data["updates"], key=lambda x: -x["change_count"])[:10]
print("Top 10 files by change count:")
for u in top_files:
    print(f"  {u['file']}: {u['change_count']} changes")

print()
print("Sample changes (first 5 files, first 3 changes each):")
for u in data["updates"][:5]:
    print(f"  File: {u['file']}")
    for c in u["changes"][:3]:
        print(f"    L{c['line']}: {c['old']} -> {c['new']} ({c['match_type']})")

old_pkgs = set()
new_pkgs = set()
for u in data["updates"]:
    for c in u["changes"]:
        op = c["old"].split(".")
        np = c["new"].split(".")
        if len(op) > 1:
            old_pkgs.add(op[1])
        if len(np) > 1:
            new_pkgs.add(np[1])

print(f"\nDistinct old zephyr sub-packages: {sorted(old_pkgs)}")
print(f"Distinct new zephyr sub-packages: {sorted(new_pkgs)}")
