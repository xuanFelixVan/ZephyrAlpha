"""Fixture: relate 预筛语料——近重源文件 A（与 near_dup_b.py 高度相似）。"""


def calculate_total(price, tax):
    subtotal = price * tax
    discount = subtotal * 0.1
    final = subtotal - discount
    return final


def format_report(title, rows):
    header = title.upper()
    body = "\n".join(rows)
    return header + "\n" + body
