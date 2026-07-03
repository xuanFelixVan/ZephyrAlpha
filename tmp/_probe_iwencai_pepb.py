"""探查 iFind i问财 PE/PB/PS/PCF 查询返回格式。

测试查询：
- "全部A股 市盈率 市净率"
- "全部A股 市盈率 市净率 市销率 市现率"
"""
import sys
import os

sys.path.insert(0, r"d:\ZephyrAlpha\tmp")
from _ds_common import setup_logging, load_env, iwencai_to_df

log = setup_logging("probe_iwencai_pepb")


def main():
    load_env()
    from iFinDPy import THS_iFinDLogin, THS_iwencai

    r = THS_iFinDLogin(os.environ["IFIND_USERNAME"], os.environ["IFIND_PASSWORD"])
    if r != 0:
        log.error(f"iFind 登录失败: {r}")
        return
    log.info("iFind 登录成功")

    queries = [
        "全部A股 市盈率 市净率",
        "全部A股 市盈率 市净率 市销率 市现率",
        "全部A股 市盈率TTM 市净率MRQ 市销率TTM 市现率TTM",
    ]
    for q in queries:
        log.info(f"=== 测试: {q} ===")
        try:
            result = THS_iwencai(q, "stock")
            df = iwencai_to_df(result)
            log.info(f"  返回 {len(df)} 行, 列: {list(df.columns)}")
            if len(df) > 0:
                log.info(f"  首行: {df.iloc[0].to_dict()}")
        except Exception as e:
            log.error(f"  失败: {e}")


if __name__ == "__main__":
    main()
