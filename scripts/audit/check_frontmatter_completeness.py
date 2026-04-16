import os, re, sys
from pathlib import Path

REQUIRED_FIELDS = ['owner', 'version', 'status']

def check_file(path):
    try:
        with open(path, 'r', encoding='utf-8-sig') as f:
            content = f.read(10000)
    except Exception as e:
        return None, f"读取失败: {e}"
    # 检测 frontmatter
    match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return False, "无 YAML frontmatter"
    fm = match.group(1)
    # 解析字段
    fields = {}
    for line in fm.split('\n'):
        if ':' in line:
            key, val = line.split(':', 1)
            fields[key.strip()] = val.strip()
    missing = [f for f in REQUIRED_FIELDS if f not in fields]
    if missing:
        return False, f"缺失字段: {', '.join(missing)}"
    return True, "OK"

def main():
    root = Path('.')
    md_files = list(root.rglob('*.md'))
    print(f"扫描 .md 文件总数: {len(md_files)}")
    results = []
    for md in md_files:
        # 跳过隐藏目录
        if any(part.startswith('.') for part in md.parts):
            continue
        if any(part in ('__pycache__', 'node_modules') for part in md.parts):
            continue
        ok, msg = check_file(md)
        results.append((md, ok, msg))

    # 分类统计
    total = len(results)
    valid = sum(1 for _, ok, _ in results if ok)
    invalid = total - valid
    missing_frontmatter = sum(1 for _, _, msg in results if '无 YAML frontmatter' in msg)
    missing_fields = sum(1 for _, _, msg in results if msg.startswith('缺失字段'))
    read_errors = sum(1 for _, _, msg in results if '读取失败' in msg)

    print(f"\n检查完成:")
    print(f"  有效 frontmatter: {valid}")
    print(f"  无效 frontmatter: {invalid}")
    print(f"    无 YAML frontmatter: {missing_frontmatter}")
    print(f"    字段缺失: {missing_fields}")
    print(f"    读取错误: {read_errors}")

    # 输出有问题的文件（最多20个）
    print("\n=== 问题文件列表 (最多20个) ===")
    count = 0
    for path, ok, msg in results:
        if not ok:
            print(f"{path}: {msg}")
            count += 1
            if count >= 20:
                print("... (更多文件未显示)")
                break

    # 保存完整结果到文件
    with open('frontmatter_audit_report.txt', 'w', encoding='utf-8') as f:
        f.write("前端元数据完整性审计报告\n")
        f.write("="*50 + "\n")
        for path, ok, msg in results:
            status = 'OK' if ok else 'FAIL'
            f.write(f"{status}: {path}\n")
            if not ok:
                f.write(f"    原因: {msg}\n")

    print(f"\n完整报告已保存到 frontmatter_audit_report.txt")

if __name__ == '__main__':
    main()
