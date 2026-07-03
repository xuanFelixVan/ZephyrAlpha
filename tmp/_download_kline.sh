#!/bin/bash
BDPAN=/root/.local/bin/bdpan
BASE="量化交易数据"
DLDIR="/mnt/d/ZephyrAlpha/data/raw/bdpan"

mkdir -p "$DLDIR/kline" "$DLDIR/5min"

echo "=== 下载 weekly_qfq.zip (113.7MB) ==="
$BDPAN download "$BASE/A股数据_zip/weekly_qfq.zip" "$DLDIR/kline/weekly_qfq.zip" 2>&1 | tail -2
echo ""

echo "=== 下载 monthly_qfq.zip (31MB) ==="
$BDPAN download "$BASE/A股数据_zip/monthly_qfq.zip" "$DLDIR/kline/monthly_qfq.zip" 2>&1 | tail -2
echo ""

echo "=== 下载 5分钟K线 2000年 (83MB) ==="
$BDPAN download "$BASE/A股分钟数据/A股_分时数据_沪深/5分钟_按年汇总/2000_5min.zip" "$DLDIR/5min/2000_5min.zip" 2>&1 | tail -2
echo ""

echo "=== 下载完成 ==="
ls -la "$DLDIR/kline/" "$DLDIR/5min/"
