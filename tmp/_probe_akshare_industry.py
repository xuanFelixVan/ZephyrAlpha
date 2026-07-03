"""探查 AKShare 行业分类接口（为 industry_class 修复准备）。

iFind THS_DataPool 申万行业在试用账号下不可用（-4001），
改用 AKShare 获取行业分类。

候选接口：
1. ak.stock_board_industry_name_em() - 东方财富行业列表
2. ak.stock_board_industry_name_ths() - 同花顺行业列表
3. ak.stock_board_industry_cons_em(symbol) - 东方财富行业成分股
4. ak.stock_industry_clf_sw() - 申万行业分类
"""
import sys
sys.path.insert(0, r"d:\ZephyrAlpha\tmp")
from _ds_common import setup_logging

log = setup_logging("probe_akshare_industry")


def main():
    import akshare as ak
    log.info(f"akshare version: {ak.__version__}")

    # 测试1: 东方财富行业列表
    log.info("=" * 50)
    log.info("[测试1] ak.stock_board_industry_name_em()")
    try:
        df = ak.stock_board_industry_name_em()
        log.info(f"  shape: {df.shape}")
        log.info(f"  columns: {list(df.columns)}")
        log.info(f"  前3行: {df.head(3).to_dict('records')}")
    except Exception as e:
        log.warning(f"  失败: {e}")

    # 测试2: 同花顺行业列表
    log.info("=" * 50)
    log.info("[测试2] ak.stock_board_industry_name_ths()")
    try:
        df = ak.stock_board_industry_name_ths()
        log.info(f"  shape: {df.shape}")
        log.info(f"  columns: {list(df.columns)}")
        log.info(f"  前3行: {df.head(3).to_dict('records')}")
    except Exception as e:
        log.warning(f"  失败: {e}")

    # 测试3: 申万行业分类（股票+行业映射）
    log.info("=" * 50)
    log.info("[测试3] ak.stock_industry_clf_sw(symbol='申万一级')")
    try:
        # 申万行业分类
        df = ak.stock_industry_clf_sw(symbol="申万一级")
        log.info(f"  shape: {df.shape}")
        log.info(f"  columns: {list(df.columns)}")
        log.info(f"  前5行: {df.head(5).to_dict('records')}")
        return  # 成功就用这个
    except Exception as e:
        log.warning(f"  失败: {e}")

    # 测试4: 东方财富某行业成分股
    log.info("=" * 50)
    log.info("[测试4] ak.stock_board_industry_cons_em(symbol='小金属')")
    try:
        df = ak.stock_board_industry_cons_em(symbol="小金属")
        log.info(f"  shape: {df.shape}")
        log.info(f"  columns: {list(df.columns)}")
        log.info(f"  前3行: {df.head(3).to_dict('records')}")
    except Exception as e:
        log.warning(f"  失败: {e}")

    # 测试5: 申万行业成分股（新版）
    log.info("=" * 50)
    log.info("[测试5] ak.index_component_sw(symbol='801010')")
    try:
        df = ak.index_component_sw(symbol="801010")
        log.info(f"  shape: {df.shape}")
        log.info(f"  columns: {list(df.columns)}")
        log.info(f"  前3行: {df.head(3).to_dict('records')}")
    except Exception as e:
        log.warning(f"  失败: {e}")

    # 测试6: 申万行业分类（旧版）
    log.info("=" * 50)
    log.info("[测试6] ak.stock_industry_category_cninfo()")
    try:
        df = ak.stock_industry_category_cninfo()
        log.info(f"  shape: {df.shape}")
        log.info(f"  columns: {list(df.columns)}")
        log.info(f"  前3行: {df.head(3).to_dict('records')}")
    except Exception as e:
        log.warning(f"  失败: {e}")


if __name__ == "__main__":
    main()
