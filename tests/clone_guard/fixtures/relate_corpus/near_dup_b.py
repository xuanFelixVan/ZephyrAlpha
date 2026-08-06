"""Fixture: relate 预筛语料——近重源文件 B（near_dup_a.py 的 Type-2 克隆：变量重命名）。"""


def calculate_total(cost, rate):
    subtotal = cost * rate
    discount = subtotal * 0.1
    final = subtotal - discount
    return final


def format_report(heading, lines):
    header = heading.upper()
    body = "\n".join(lines)
    return header + "\n" + body
