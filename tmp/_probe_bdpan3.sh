#!/bin/bash
BDPAN=/root/.local/bin/bdpan
BASE="量化交易数据"
echo "=== 5分钟_按月归档 (前20) ==="
$BDPAN ls "$BASE/A股分钟数据/A股_分时数据_沪深/5分钟_按月归档" 2>&1 | head -25
echo ""
echo "=== 1分钟_按年汇总 (前20) ==="
$BDPAN ls "$BASE/A股分钟数据/A股_分时数据_沪深/1分钟_按年汇总" 2>&1 | head -25
echo ""
echo "=== 分笔成交_按月归档_沪深 (前25) ==="
$BDPAN ls "$BASE/A股数据_分笔数据/分笔成交_按月归档_沪深" 2>&1 | head -30
echo ""
echo "=== ETF分笔成交_按月归档 (前15) ==="
$BDPAN ls "$BASE/基金_分笔成交/ETF分笔成交_按月归档" 2>&1 | head -20
echo ""
echo "=== 可转债_分笔成交_按月归档 (前15) ==="
$BDPAN ls "$BASE/可转债_分笔成交/可转债_分笔成交_按月归档" 2>&1 | head -20
