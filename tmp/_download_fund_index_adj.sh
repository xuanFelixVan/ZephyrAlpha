#!/bin/bash
# 批量下载基金分钟数据 + 指数K线 + 复权因子_tushare
BDPAN="/root/.local/bin/bdpan"
DLROOT="/mnt/d/ZephyrAlpha/data/raw/bdpan"

# 1. ETF分钟数据_汇总（10个zip, 约3GB）
ETF_SRC="量化交易数据/基金_分钟数据/ETF分钟数据_汇总"
ETF_DST="${DLROOT}/etf_minute"
mkdir -p "$ETF_DST"
echo "=== 下载ETF分钟数据 ==="
for f in ETF_1min_2005_2022.zip ETF_1min_2023_2025.zip ETF_5min_2005_2024.zip ETF_5min_2025.zip \
         ETF_15min_2005_2024.zip ETF_15min_2025.zip ETF_30min_2005_2024.zip ETF_30min_2025.zip \
         ETF_60min_2005_2024.zip ETF_60min_2025.zip; do
    if [[ -f "$ETF_DST/$f" ]]; then
        echo "已存在: $f"
    else
        echo "下载: $f"
        $BDPAN download "${ETF_SRC}/${f}" "$ETF_DST/$f" 2>&1 | tail -1
        [[ -f "$ETF_DST/$f" ]] && echo "  完成 $(du -h "$ETF_DST/$f" | cut -f1)" || echo "  失败"
    fi
done

# 2. LOF分钟数据_汇总（10个zip, 约1.3GB）
LOF_SRC="量化交易数据/基金_分钟数据/LOF分钟数据_汇总"
LOF_DST="${DLROOT}/lof_minute"
mkdir -p "$LOF_DST"
echo ""
echo "=== 下载LOF分钟数据 ==="
for f in LOF_1min_2005_2024.zip LOF_1min_2025.zip LOF_5min_2005_2024.zip LOF_5min_2025.zip \
         LOF_15min_2005_2024.zip LOF_15min_2025.zip LOF_30min_2005_2024.zip LOF_30min_2025.zip \
         LOF_60min_2005_2024.zip LOF_60min_2025.zip; do
    if [[ -f "$LOF_DST/$f" ]]; then
        echo "已存在: $f"
    else
        echo "下载: $f"
        $BDPAN download "${LOF_SRC}/${f}" "$LOF_DST/$f" 2>&1 | tail -1
        [[ -f "$LOF_DST/$f" ]] && echo "  完成 $(du -h "$LOF_DST/$f" | cut -f1)" || echo "  失败"
    fi
done

# 3. 基金基础信息CSV（3个文件，小）
echo ""
echo "=== 下载基金基础信息CSV ==="
FUND_INFO_SRC="量化交易数据/基金_分钟数据"
FUND_INFO_DST="${DLROOT}/fund_info"
mkdir -p "$FUND_INFO_DST"
for f in "ETF基础信息列表.csv" "ETF基准指数列表.csv" "LOF基金列表.csv"; do
    if [[ -f "$FUND_INFO_DST/$f" ]]; then
        echo "已存在: $f"
    else
        echo "下载: $f"
        $BDPAN download "${FUND_INFO_SRC}/${f}" "$FUND_INFO_DST/$f" 2>&1 | tail -1
        [[ -f "$FUND_INFO_DST/$f" ]] && echo "  完成" || echo "  失败"
    fi
done

# 4. 指数K线（A股数据_zip/指数/，8个文件）
INDEX_SRC="量化交易数据/A股数据_zip/指数"
INDEX_DST="${DLROOT}/index_kline"
mkdir -p "$INDEX_DST"
echo ""
echo "=== 下载指数K线 ==="
for f in "指数_日_kline.zip" "指数_月_kline.zip" "指数_周_kline.zip" "指数列表.csv" \
         "中证指数_日_kline.zip" "中证指数_月_kline.zip" "中证指数_周_kline.zip" "中证指数列表.csv"; do
    if [[ -f "$INDEX_DST/$f" ]]; then
        echo "已存在: $f"
    else
        echo "下载: $f"
        $BDPAN download "${INDEX_SRC}/${f}" "$INDEX_DST/$f" 2>&1 | tail -1
        [[ -f "$INDEX_DST/$f" ]] && echo "  完成 $(du -h "$INDEX_DST/$f" | cut -f1)" || echo "  失败"
    fi
done

# 5. 复权因子_tushare
ADJ_SRC="量化交易数据/复权因子_tushare"
ADJ_DST="${DLROOT}/adj_factor_tushare"
mkdir -p "$ADJ_DST"
echo ""
echo "=== 下载复权因子_tushare ==="
for f in "复权因子.zip"; do
    if [[ -f "$ADJ_DST/$f" ]]; then
        echo "已存在: $f"
    else
        echo "下载: $f"
        $BDPAN download "${ADJ_SRC}/${f}" "$ADJ_DST/$f" 2>&1 | tail -1
        [[ -f "$ADJ_DST/$f" ]] && echo "  完成 $(du -h "$ADJ_DST/$f" | cut -f1)" || echo "  失败"
    fi
done

# 6. 日K线不复权+后复权（A股数据_zip/，6个zip）
DAILY_SRC="量化交易数据/A股数据_zip"
DAILY_DST="${DLROOT}/daily_extra"
mkdir -p "$DAILY_DST"
echo ""
echo "=== 下载日/周/月K线不复权+后复权 ==="
for f in daily.zip daily_hfq.zip weekly.zip weekly_hfq.zip monthly.zip monthly_hfq.zip; do
    if [[ -f "$DAILY_DST/$f" ]]; then
        echo "已存在: $f"
    else
        echo "下载: $f"
        $BDPAN download "${DAILY_SRC}/${f}" "$DAILY_DST/$f" 2>&1 | tail -1
        [[ -f "$DAILY_DST/$f" ]] && echo "  完成 $(du -h "$DAILY_DST/$f" | cut -f1)" || echo "  失败"
    fi
done

echo ""
echo "=== 全部下载完成 ==="
