"""Delete 7 FIXED entries: 5.134.2, 5.69.3, 5.75.4, 5.77.2, 5.77.3, 5.10.13, 5.66.1"""
from __future__ import annotations
from pathlib import Path

DOC = Path(r"D:\ZephyrAlpha\docs\02_enterprise_architecture\architecture_debt_registry.md")
TO_DELETE = ['5.134.2', '5.69.3', '5.75.4', '5.77.2', '5.77.3', '5.10.13', '5.66.1']


def main():
    with open(DOC, encoding='utf-8') as f:
        lines = f.readlines()

    delete_ranges = []
    i = 0
    while i < len(lines):
        line = lines[i]
        for eid in TO_DELETE:
            if line.startswith(f"#### {eid} "):
                j = i + 1
                while j < len(lines):
                    next_line = lines[j]
                    if (next_line.startswith('#### ')
                            or next_line.startswith('### ')
                            or next_line.startswith('## ')):
                        break
                    j += 1
                delete_ranges.append((i, j))
                print(f"  Delete {eid}: lines {i+1}-{j} ({j-i} lines)")
                i = j
                break
        else:
            i += 1

    new_lines = lines[:]
    for start, end in reversed(delete_ranges):
        del new_lines[start:end]

    with open(DOC, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    print(f"\nDeleted {len(delete_ranges)} entries.")
    print(f"Original: {len(lines)} lines → New: {len(new_lines)} lines")


if __name__ == '__main__':
    main()
