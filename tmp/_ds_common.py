"""数据源下载脚本共享工具（指令2 热身）。

ClickHouse 运行在 WSL 内，Windows Python 无法直连 localhost:9000，
故所有 CH 读写通过 `wsl clickhouse-client` subprocess 完成（与 _import_base_csv.py 一致）。
"""
import os
import sys
import json
import subprocess
import logging
import time

REPO = r"d:\ZephyrAlpha"
ENV_PATH = os.path.join(REPO, ".env")
PROGRESS_DIR = os.path.join(REPO, "tmp", "_ds_progress")
WSL = ["wsl", "-d", "Ubuntu", "-e", "clickhouse-client"]
CH_DB = "c1_market"


def setup_logging(name: str) -> logging.Logger:
    """配置日志，输出到 stdout + 文件。"""
    os.makedirs(PROGRESS_DIR, exist_ok=True)
    log = logging.getLogger(name)
    if log.handlers:
        return log
    log.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%H:%M:%S")
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    log.addHandler(sh)
    fh = logging.FileHandler(os.path.join(PROGRESS_DIR, f"{name}.log"), encoding="utf-8")
    fh.setFormatter(fmt)
    log.addHandler(fh)
    return log


def load_env() -> dict:
    """从 .env 读取键值对（不依赖 python-dotenv）。"""
    env = {}
    if not os.path.exists(ENV_PATH):
        return env
    with open(ENV_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    for k, v in env.items():
        os.environ.setdefault(k, v)
    return env


def ch_query(sql: str, timeout: int = 120) -> str:
    """执行 ClickHouse 查询，返回 stdout 文本。"""
    r = subprocess.run(WSL + ["--query", sql], capture_output=True, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError(f"CH query failed: {r.stderr.decode('utf-8', errors='replace')[:300]}")
    return r.stdout.decode("utf-8", errors="replace")


def ch_execute(sql: str, timeout: int = 120) -> bool:
    """执行 ClickHouse DDL/DML（CREATE/ALTER/TRUNCATE 等）。"""
    r = subprocess.run(WSL + ["--multiquery", "--query", sql],
                       capture_output=True, timeout=timeout)
    if r.returncode != 0:
        sys.stderr.write(f"CH execute failed: {r.stderr.decode('utf-8', errors='replace')[:300]}\n")
        return False
    return True


def ch_insert_tsv(table: str, tsv_bytes: bytes, timeout: int = 300) -> bool:
    """通过 stdin TSV 批量插入。table 可含库名前缀。"""
    full = table if "." in table else f"{CH_DB}.{table}"
    r = subprocess.run(WSL + ["--query", f"INSERT INTO {full} FORMAT TSV"],
                       input=tsv_bytes, capture_output=True, timeout=timeout)
    if r.returncode != 0:
        sys.stderr.write(f"CH insert failed ({full}): {r.stderr.decode('utf-8', errors='replace')[:300]}\n")
        return False
    return True


def ch_count(table: str, where: str = "") -> int:
    """返回表行数。"""
    sql = f"SELECT count() FROM {CH_DB}.{table}"
    if where:
        sql += f" WHERE {where}"
    return int(ch_query(sql).strip() or "0")


def get_stock_list(only_listed: bool = True) -> list:
    """从 ClickHouse 读取股票列表。返回 [(ts_code, symbol, name), ...]。

    ts_code 格式 000001.SZ（iFind 用），symbol 格式 000001（daily_valuation 用）。
    """
    where = "WHERE list_status='上市'" if only_listed else ""
    out = ch_query(f"SELECT ts_code, symbol, name FROM {CH_DB}.stock_list {where} ORDER BY ts_code")
    rows = []
    for line in out.strip().split("\n"):
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) >= 3:
            rows.append((parts[0], parts[1], parts[2]))
    return rows


def load_progress(name: str) -> dict:
    """读取断点续传状态。"""
    p = os.path.join(PROGRESS_DIR, f"{name}.json")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_progress(name: str, state: dict):
    """保存断点续传状态。"""
    os.makedirs(PROGRESS_DIR, exist_ok=True)
    p = os.path.join(PROGRESS_DIR, f"{name}.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def tsv_escape(v) -> str:
    """TSV 字段转义：None→空，tab/换行替换为空格。"""
    if v is None:
        return ""
    s = str(v)
    return s.replace("\t", " ").replace("\n", " ").replace("\r", " ")


def year_months_backward(start_year: int, start_month: int, end_year: int = 1990):
    """生成 (year, month) 从 start 倒序到 end_year 的列表。"""
    out = []
    y, m = start_year, start_month
    while y > end_year or (y == end_year and m >= 1):
        out.append((y, m))
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    return out
