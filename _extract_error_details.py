"""提取剩余74个错误的具体信息，用于制定修复策略。"""
import re
from collections import defaultdict
from pathlib import Path

OUTPUT_FILE = r"d:\ZephyrAlpha\_pytest_output.txt"
REPORT_FILE = r"d:\ZephyrAlpha\_error_details.txt"


def main():
    content = Path(OUTPUT_FILE).read_text(encoding="utf-8", errors="replace")
    lines = content.splitlines()

    # 提取每个错误块：______ ERROR collecting tests/xxx.py ______ 到下一个 ERROR 或空行
    error_blocks = []
    current_block = []
    in_error = False

    for i, line in enumerate(lines):
        if re.match(r"^[_=]{2,}\s+ERROR collecting", line):
            if current_block and in_error:
                error_blocks.append(current_block)
            current_block = [line]
            in_error = True
        elif in_error:
            if re.match(r"^[_=]{2,}\s+ERROR collecting", line) or re.match(r"^=+\s+\d+ errors? in", line):
                error_blocks.append(current_block)
                current_block = [line] if re.match(r"^[_=]{2,}\s+ERROR", line) else []
                in_error = re.match(r"^[_=]{2,}\s+ERROR", line) is not None
            else:
                current_block.append(line)

    if current_block and in_error:
        error_blocks.append(current_block)

    # 解析每个错误块
    error_details = []
    for block in error_blocks:
        if not block:
            continue
        # 第一行：______ ERROR collecting tests/xxx.py ______
        header = block[0]
        m = re.search(r"ERROR collecting (\S+)", header)
        if not m:
            continue
        test_file = m.group(1)

        # 提取错误类型和消息
        error_type = "Unknown"
        error_msg = ""
        for line in block[1:]:
            # E  ImportError: cannot import name 'X' from 'Y'
            # E  ModuleNotFoundError: No module named 'X'
            # E  SyntaxError: ...
            m_err = re.match(r"^E\s+(\w+(?:Error|Exception)):\s*(.*)", line)
            if m_err:
                error_type = m_err.group(1)
                error_msg = m_err.group(2)
                break
            # 也匹配不带 E 前缀的
            m_err2 = re.match(r"^(\w+(?:Error|Exception)):\s*(.*)", line)
            if m_err2:
                error_type = m_err2.group(1)
                error_msg = m_err2.group(2)
                break

        error_details.append({
            "test_file": test_file,
            "error_type": error_type,
            "error_msg": error_msg,
            "block": block[:15],  # 前15行用于调试
        })

    # 按错误类型分组输出
    by_type = defaultdict(list)
    for e in error_details:
        by_type[e["error_type"]].append(e)

    report_lines = []
    report_lines.append(f"总错误数: {len(error_details)}")
    report_lines.append(f"错误类型分类:")
    for et, items in sorted(by_type.items(), key=lambda x: -len(x[1])):
        report_lines.append(f"  {et}: {len(items)}")
    report_lines.append("")
    report_lines.append("=" * 80)
    report_lines.append("详细错误列表（按错误类型分组）")
    report_lines.append("=" * 80)

    for et, items in sorted(by_type.items(), key=lambda x: -len(x[1])):
        report_lines.append(f"\n{'='*60}")
        report_lines.append(f"## {et} ({len(items)}个)")
        report_lines.append(f"{'='*60}")
        for i, e in enumerate(items, 1):
            report_lines.append(f"\n  [{i}] 文件: {e['test_file']}")
            report_lines.append(f"      消息: {e['error_msg']}")
            # 输出block前几行用于调试
            for line in e["block"][:8]:
                report_lines.append(f"      | {line}")

    Path(REPORT_FILE).write_text("\n".join(report_lines), encoding="utf-8")
    print(f"总错误数: {len(error_details)}")
    print(f"详细报告已保存到: {REPORT_FILE}")

    # 输出每个错误类型的简短统计
    print("\n按错误消息分组（前30）:")
    msg_groups = defaultdict(int)
    for e in error_details:
        # 提取关键信息
        msg = e["error_msg"]
        # 标准化：去掉具体路径
        msg_norm = re.sub(r"'[^']+'", "'X'", msg)
        msg_norm = re.sub(r"tests/\S+", "tests/X", msg_norm)
        key = f"{e['error_type']}: {msg_norm}"
        msg_groups[key] += 1

    for key, count in sorted(msg_groups.items(), key=lambda x: -x[1])[:30]:
        print(f"  {count:4d}  {key}")


if __name__ == "__main__":
    main()
