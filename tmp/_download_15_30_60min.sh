#!/bin/bash
# 下载15/30/60min的2025+2026年zip
BDPAN="/root/.local/bin/bdpan"
BASE="量化交易数据/A股分钟数据/A股_分时数据_沪深"

for period in "15分钟_按年汇总" "30分钟_按年汇总" "60分钟_按年汇总"; do
    # 从中文周期名提取英文目录名
    if [[ "$period" == "15分钟_按年汇总" ]]; then
        dir="15min"
    elif [[ "$period" == "30分钟_按年汇总" ]]; then
        dir="30min"
    else
        dir="60min"
    fi

    mkdir -p "/mnt/d/ZephyrAlpha/data/raw/bdpan/$dir"

    for year in 2025 2026; do
        zip_file="${year}_${dir}.zip"
        local_path="/mnt/d/ZephyrAlpha/data/raw/bdpan/$dir/$zip_file"
        if [[ -f "$local_path" ]]; then
            echo "$zip_file 已存在"
            continue
        fi
        echo "下载 $zip_file ..."
        $BDPAN download "${BASE}/${period}/${year}_${dir}.zip" "$local_path" 2>&1 | tail -3
        if [[ -f "$local_path" ]]; then
            echo "  完成 $(du -h "$local_path" | cut -f1)"
        else
            echo "  失败"
        fi
    done
done
echo "=== 下载完成 ==="
