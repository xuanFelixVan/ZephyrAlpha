#!/bin/bash
BDPAN=/root/.local/bin/bdpan
BASE="量化交易数据/A股分钟数据/A股_分时数据_沪深"
for p in "15分钟" "30分钟" "60分钟" "1分钟"; do
  echo "=== ${p}_按年汇总 ==="
  $BDPAN ls "$BASE/${p}_按年汇总" 2>&1 | head -5
  echo "..."
  $BDPAN ls "$BASE/${p}_按年汇总" 2>&1 | tail -3
  echo ""
done
