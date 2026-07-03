#!/bin/bash
# 批量下载小CSV文件+格式样本
BDPAN=/root/.local/bin/bdpan
BASE="量化交易数据"
DLDIR="/mnt/d/ZephyrAlpha/data/raw/bdpan"

mkdir -p "$DLDIR/csv" "$DLDIR/sample"

echo "=== 下载CSV文件 ==="
$BDPAN download "$BASE/A股数据_zip/股票列表.csv" "$DLDIR/csv/stock_list.csv" 2>&1 | tail -1
$BDPAN download "$BASE/A股数据_zip/交易日历.csv" "$DLDIR/csv/trade_calendar.csv" 2>&1 | tail -1
$BDPAN download "$BASE/A股数据_zip/退市股票列表.csv" "$DLDIR/csv/delisted_stocks.csv" 2>&1 | tail -1
$BDPAN download "$BASE/A股分钟数据/A股_分时数据_沪深/股票列表_沪深.csv" "$DLDIR/csv/stock_list_sh.csv" 2>&1 | tail -1
$BDPAN download "$BASE/A股数据_分笔成交_指数/指数列表_沪深京.csv" "$DLDIR/csv/index_list.csv" 2>&1 | tail -1
$BDPAN download "$BASE/港股_分笔成交/港股股票列表.csv" "$DLDIR/csv/hk_stock_list.csv" 2>&1 | tail -1
$BDPAN download "$BASE/港股_分笔成交/港股交易日历.csv" "$DLDIR/csv/hk_trade_calendar.csv" 2>&1 | tail -1
$BDPAN download "$BASE/可转债_分笔成交/可转债基础信息列表.csv" "$DLDIR/csv/convertible_bond_list.csv" 2>&1 | tail -1
$BDPAN download "$BASE/基金_分笔成交/ETF基础信息列表.csv" "$DLDIR/csv/etf_list.csv" 2>&1 | tail -1
$BDPAN download "$BASE/基金_分笔成交/ETF基准指数列表.csv" "$DLDIR/csv/etf_benchmark.csv" 2>&1 | tail -1
$BDPAN download "$BASE/基金_分笔成交/LOF基金列表.csv" "$DLDIR/csv/lof_list.csv" 2>&1 | tail -1
$BDPAN download "$BASE/通达信板块_分笔成交/板块信息_通达信.csv" "$DLDIR/csv/tdx_sector_info.csv" 2>&1 | tail -1
$BDPAN download "$BASE/通达信板块_分笔成交/市场统计指数_通达信.csv" "$DLDIR/csv/tdx_market_index.csv" 2>&1 | tail -1

echo ""
echo "=== 下载格式样本 ==="
$BDPAN download "$BASE/A股分钟数据/A股_分时数据_沪深/5分钟_按月归档/2000-06/20000609_5min.zip" "$DLDIR/sample/5min_sample.zip" 2>&1 | tail -1

echo ""
echo "=== 下载完成 ==="
ls -la "$DLDIR/csv/" "$DLDIR/sample/"
