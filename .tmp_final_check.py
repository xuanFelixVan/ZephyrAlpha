import json
from pathlib import Path

d = json.loads(Path("docs/09_AUDIT/STATE/SENTINEL_L1_SCAN_20260408.json").read_text(encoding="utf-8"))
mod = d.get("module_ids", {})
lnk = d.get("links", {}).get("stats", {})

unique = mod.get("unique_module_ids", 0)
dup_cnt = mod.get("duplicate_ids_count", 0)
dup_rate = 100 * dup_cnt / (dup_cnt + unique) if (dup_cnt + unique) > 0 else 0

print("==== 最终健康度（Path C1+C2 后）====")
print(f"  扫描文件总数       : {d.get('md_file_count', 0)}")
print(f"  有效链接           : {lnk.get('valid', 0)}")
print(f"  断链               : {lnk.get('invalid', 0)}")
print(f"  唯一 module_id     : {unique}")
print(f"  重复 module_id 组  : {dup_cnt}")
print(f"  重复率             : {dup_rate:.2f}%")

if dup_cnt > 0:
    dups = mod.get("duplicates", {})
    print()
    print("  剩余重复组：")
    for mid, files in sorted(dups.items()):
        print(f"    '{mid}' ({len(files)} 个文件)")
        for f in files:
            print(f"      - {f}")
