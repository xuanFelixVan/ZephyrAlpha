#!/bin/bash
# 批量下载上市公司财务信息所有zip
BDPAN="/root/.local/bin/bdpan"
BASE="量化交易数据/上市公司财务信息"
DEST="/mnt/d/ZephyrAlpha/data/raw/bdpan/financial"

mkdir -p "$DEST"

files=(
    "财报披露计划.zip"
    "财务审计意见数据.zip"
    "财务指标数据.zip"
    "分红配股.zip"
    "分红送股数据.zip"
    "股东人数.zip"
    "股权质押明细.zip"
    "股权质押统计.zip"
    "利润表数据.zip"
    "前十大股东.zip"
    "前十大流通股东.zip"
    "现金流量表数据.zip"
    "限售股解禁.zip"
    "业绩快报数据.zip"
    "业绩预告数据.zip"
    "主营业务构成数据.zip"
    "资产负债表数据.zip"
)

for f in "${files[@]}"; do
    if [[ -f "$DEST/$f" ]]; then
        echo "已存在: $f"
        continue
    fi
    echo "下载: $f ..."
    $BDPAN download "${BASE}/${f}" "$DEST/$f" 2>&1 | tail -2
    if [[ -f "$DEST/$f" ]]; then
        echo "  完成 $(du -h "$DEST/$f" | cut -f1)"
    else
        echo "  失败"
    fi
done
echo "=== 财务数据下载完成 ==="
ls -la "$DEST"
