#!/bin/bash
BDPAN=/root/.local/bin/bdpan
BASE="量化交易数据"
echo "=== A股分钟数据/沪深 ==="
$BDPAN ls "$BASE/A股分钟数据/A股_分时数据_沪深" 2>&1 | head -30
echo ""
echo "=== A股数据_分笔数据 ==="
$BDPAN ls "$BASE/A股数据_分笔数据" 2>&1 | head -30
echo ""
echo "=== A股数据_分笔成交_指数 ==="
$BDPAN ls "$BASE/A股数据_分笔成交_指数" 2>&1 | head -20
echo ""
echo "=== 港股_分笔成交 ==="
$BDPAN ls "$BASE/港股_分笔成交" 2>&1 | head -20
echo ""
echo "=== 可转债_分笔成交 ==="
$BDPAN ls "$BASE/可转债_分笔成交" 2>&1 | head -20
echo ""
echo "=== 基金_分笔成交 ==="
$BDPAN ls "$BASE/基金_分笔成交" 2>&1 | head -20
echo ""
echo "=== 基金_分钟数据 ==="
$BDPAN ls "$BASE/基金_分钟数据" 2>&1 | head -20
echo ""
echo "=== 通达信板块_分笔成交 ==="
$BDPAN ls "$BASE/通达信板块_分笔成交" 2>&1 | head -20
