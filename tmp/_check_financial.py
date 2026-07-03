"""验证财务zip完整性 + 对比c3_fundamental表字段"""
import zipfile
import csv
import io
import os
import subprocess

FIN_DIR = r"d:\ZephyrAlpha\data\raw\bdpan\financial"

# c3_fundamental中已有的财务表清单
EXISTING_TABLES = [
    "audit_opinion", "balance_sheet", "cashflow_statement", "disclosure_plan",
    "dividend", "earnings_forecast", "equity_pledge_detail", "equity_pledge_summary",
    "express_report", "financial_indicator", "income_statement", "main_business",
    "restricted_shares", "rights_issue", "shareholder_count",
    "top10_circulating_shareholders", "top10_shareholders"
]

# 网盘zip与c3表的对应关系
ZIP_TABLE_MAP = {
    "财务指标数据.zip": "financial_indicator",
    "利润表数据.zip": "income_statement",
    "现金流量表数据.zip": "cashflow_statement",
    "资产负债表数据.zip": "balance_sheet",
    "股东人数.zip": "shareholder_count",
    "业绩快报数据.zip": "express_report",
    "业绩预告数据.zip": "earnings_forecast",
    "前十大股东.zip": "top10_shareholders",
    "前十大流通股东.zip": "top10_circulating_shareholders",
    "分红送股数据.zip": "dividend",
    "分红配股.zip": "rights_issue",
    "财报披露计划.zip": "disclosure_plan",
    "财务审计意见数据.zip": "audit_opinion",
    "股权质押明细.zip": "equity_pledge_detail",
    "股权质押统计.zip": "equity_pledge_summary",
    "限售股解禁.zip": "restricted_shares",
    "主营业务构成数据.zip": "main_business",
}


def get_table_count(table):
    r = subprocess.run(["wsl", "-d", "Ubuntu", "-e", "clickhouse-client",
                        "--query", f"SELECT count() FROM c3_fundamental.{table} FORMAT TabSeparated"],
                       capture_output=True, timeout=30)
    if r.returncode == 0:
        try:
            return int(r.stdout.decode().strip())
        except ValueError:
            return -1
    return -2


def get_table_maxdate(table):
    """获取表的最大公告日期"""
    # 先看表结构，找出日期列名
    r = subprocess.run(["wsl", "-d", "Ubuntu", "-e", "clickhouse-client",
                        "--query", f"DESCRIBE c3_fundamental.{table} FORMAT TabSeparated"],
                       capture_output=True, timeout=30)
    cols = []
    date_col = None
    for line in r.stdout.decode().splitlines():
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) >= 2:
            col_name = parts[0]
            col_type = parts[1]
            cols.append((col_name, col_type))
            if col_type in ("Date", "DateTime") and date_col is None and ("date" in col_name.lower() or "announce" in col_name.lower()):
                date_col = col_name
    if not date_col:
        # 取第一个Date类型字段
        for col_name, col_type in cols:
            if col_type.startswith("Date"):
                date_col = col_name
                break
    if not date_col:
        return None, cols
    r = subprocess.run(["wsl", "-d", "Ubuntu", "-e", "clickhouse-client",
                        "--query", f"SELECT max({date_col}) FROM c3_fundamental.{table} FORMAT TabSeparated"],
                       capture_output=True, timeout=30)
    if r.returncode == 0:
        return r.stdout.decode().strip(), cols
    return None, cols


def check_zip(zip_name):
    """检查zip完整性，返回CSV文件数和第一行header"""
    zip_path = os.path.join(FIN_DIR, zip_name)
    if not os.path.exists(zip_path):
        return None, None, None
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            names = [n for n in zf.namelist() if n.endswith(".csv")]
            if not names:
                return 0, None, "无CSV文件"
            content = zf.read(names[0])
            reader = csv.reader(io.TextIOWrapper(io.BytesIO(content), encoding="utf-8-sig"))
            try:
                header = next(reader)
                first_row = next(reader)
            except StopIteration:
                return len(names), None, "空文件"
            return len(names), header, first_row
    except zipfile.BadZipFile as e:
        return -1, None, f"损坏: {e}"


def main():
    print("=== c3_fundamental财务表状态 ===")
    print(f"{'表名':<35} {'行数':>10} {'最大日期':<12} {'日期列名':<20}")
    print("-" * 90)
    for table in EXISTING_TABLES:
        cnt = get_table_count(table)
        max_dt, cols = get_table_maxdate(table)
        date_col = ""
        for col_name, col_type in cols:
            if col_type.startswith("Date") and ("date" in col_name.lower() or "announce" in col_name.lower()):
                date_col = col_name
                break
        print(f"{table:<35} {cnt:>10} {str(max_dt):<12} {date_col:<20}")

    print("\n=== 财务zip完整性检查 ===")
    print(f"{'zip文件名':<25} {'CSV数':>8} {'对应表':<25} {'状态'}")
    print("-" * 90)
    for zip_name, table in ZIP_TABLE_MAP.items():
        cnt, header, info = check_zip(zip_name)
        if cnt is None:
            print(f"{zip_name:<25} {'缺失':>8} {table:<25} 未下载")
        elif cnt == -1:
            print(f"{zip_name:<25} {'损坏':>8} {table:<25} {info}")
        else:
            print(f"{zip_name:<25} {cnt:>8} {table:<25} OK (列数={len(header) if header else 0})")


if __name__ == "__main__":
    main()
