#!/bin/bash
# 下载1分钟K线2025+2026年zip + 重新下载失败的财务zip
BDPAN="/root/.local/bin/bdpan"
KLINE_BASE="量化交易数据/A股分钟数据/A股_分时数据_沪深/1分钟_按年汇总"
FIN_BASE="量化交易数据/上市公司财务信息"

# 1分钟K线
mkdir -p /mnt/d/ZephyrAlpha/data/raw/bdpan/1min
for year in 2025 2026; do
    f="${year}_1min.zip"
    dst="/mnt/d/ZephyrAlpha/data/raw/bdpan/1min/$f"
    if [[ -f "$dst" ]]; then
        echo "已存在: $f"
    else
        echo "下载1min: $f ..."
        $BDPAN download "${KLINE_BASE}/${f}" "$dst" 2>&1 | tail -2
        [[ -f "$dst" ]] && echo "  完成 $(du -h "$dst" | cut -f1)" || echo "  失败"
    fi
done

# 重新下载失败的财务zip
FIN_DST="/mnt/d/ZephyrAlpha/data/raw/bdpan/financial"
for f in "现金流量表数据.zip" "主营业务构成数据.zip" "资产负债表数据.zip"; do
    if [[ -f "$FIN_DST/$f" ]]; then
        echo "已存在: $f"
    else
        echo "重新下载财务: $f ..."
        $BDPAN download "${FIN_BASE}/${f}" "$FIN_DST/$f" 2>&1 | tail -2
        [[ -f "$FIN_DST/$f" ]] && echo "  完成 $(du -h "$FIN_DST/$f" | cut -f1)" || echo "  失败"
    fi
done
echo "=== 全部下载完成 ==="
