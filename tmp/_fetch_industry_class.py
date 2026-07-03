"""#7 行业分类 → industry_class（iFind THS_DataPool，P1，全量静态）。

策略：
- 静态数据，无时间范围
- 获取申万一级行业列表 → 每个行业用 THS_DataPool 获取成分股
- 同时获取同花顺行业（THS 行业指数 .TI 后缀）
- 写入 industry_class(symbol, industry_sw, industry_zsi, industry_level)

用法:
    python _fetch_industry_class.py

THS_DataPool 签名:
    THS_DataPool('index', '日期;指数代码', 'date:Y,thscode:Y,security_name:Y')
"""
import sys
import time

sys.path.insert(0, r"d:\ZephyrAlpha\tmp")
from _ds_common import setup_logging, load_env, ch_insert_tsv, tsv_escape

log = setup_logging("fetch_industry_class")

# 申万一级行业指数代码（.TI 后缀，示例，需实测补全）
# 同花顺行业指数 884xxx.TI 系列
SW_INDUSTRIES = [
    ("801010", "农林牧渔"), ("801030", "化工"), ("801040", "钢铁"),
    ("801050", "有色金属"), ("801080", "电子"), ("801110", "家用电器"),
    ("801120", "食品饮料"), ("801150", "纺织服装"), ("801160", "轻工制造"),
    ("801170", "医药生物"), ("801180", "建筑装饰"), ("801200", "商贸零售"),
    ("801210", "社会服务"), ("801230", "综合"), ("801710", "建筑材料"),
    ("801720", "电力设备"), ("801730", "国防军工"), ("801740", "计算机"),
    ("801750", "传媒"), ("801760", "通信"), ("801770", "银行"),
    ("801780", "非银金融"), ("801790", "机械设备"), ("801880", "汽车"),
    ("801890", "交通运输"),
]


def to_symbol(code):
    s = str(code).strip().upper()
    for pfx in (".SZ", ".SH", ".BJ", ".TI"):
        s = s.replace(pfx, "")
    for pfx in ("SH", "SZ", "BJ"):
        if s.startswith(pfx):
            s = s[len(pfx):]
    return s if s.isdigit() and len(s) == 6 else ""


def fetch_industry_members(industry_code: str, industry_name: str, level: int):
    """获取某行业的成分股列表。返回 [(symbol, industry_name, level), ...]。"""
    from iFinDPy import THS_DataPool
    # 申万行业指数代码格式: 801010.SW 或 .TI
    idx_code = f"{industry_code}.SW"
    date = "2026-07-04"
    try:
        data = THS_DataPool("index", f"{date};{idx_code}",
                            "date:Y,thscode:Y,security_name:Y")
        # 提取成分股代码
        codes = data["tables"][0]["table"]["THSCODE"]
        names = data["tables"][0]["table"].get("SECURITY_NAME", [])
        result = []
        for i, code in enumerate(codes):
            sym = to_symbol(code)
            if sym:
                nm = names[i] if i < len(names) else ""
                result.append((sym, industry_name, industry_name, level, nm))
        return result
    except Exception as e:
        log.warning(f"  {industry_code} {industry_name} 获取失败: {e}")
        # 备选: 用 .TI 后缀
        try:
            idx_code = f"{industry_code}.TI"
            data = THS_DataPool("index", f"{date};{idx_code}",
                                "date:Y,thscode:Y,security_name:Y")
            codes = data["tables"][0]["table"]["THSCODE"]
            names = data["tables"][0]["table"].get("SECURITY_NAME", [])
            result = []
            for i, code in enumerate(codes):
                sym = to_symbol(code)
                if sym:
                    nm = names[i] if i < len(names) else ""
                    result.append((sym, industry_name, industry_name, level, nm))
            return result
        except Exception as e2:
            log.error(f"  {industry_code} 备选也失败: {e2}")
            return []


def main():
    load_env()
    from iFinDPy import THS_iFinDLogin
    import os
    r = THS_iFinDLogin(os.environ["IFIND_USERNAME"], os.environ["IFIND_PASSWORD"])
    if r != 0:
        log.error(f"iFind 登录失败: {r}")
        return
    log.info("iFind 登录成功")

    all_rows = []
    for idx_code, idx_name in SW_INDUSTRIES:
        log.info(f"获取行业: {idx_name} ({idx_code})")
        members = fetch_industry_members(idx_code, idx_name, level=1)
        for sym, ind_sw, ind_zsi, lvl, nm in members:
            # industry_class 表: symbol, industry_sw, industry_zsi, industry_level
            line = "\t".join([
                sym,
                tsv_escape(ind_sw),
                tsv_escape(ind_zsi),
                tsv_escape(lvl),
            ])
            all_rows.append(line)
        log.info(f"  {idx_name}: {len(members)} 只成分股")
        time.sleep(1.0)

    if all_rows:
        tsv = ("\n".join(all_rows) + "\n").encode("utf-8")
        if ch_insert_tsv("industry_class", tsv):
            log.info(f"行业分类写入完成: {len(all_rows)} 行")
        # 去重（保留每个 symbol 第一条）
        log.info("执行去重...")
        from _ds_common import ch_execute
        ch_execute("""
OPTIMIZE TABLE c1_market.industry_class FINAL
""")


if __name__ == "__main__":
    main()
